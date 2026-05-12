"""agregar_conversoes.py — Agrega transições pixel-a-pixel consecutivas
===========================================================================

Lê os 39 CSVs de cache (transicao_YYYY_YYYY.csv) gerados por
transicoes_mapbiomas.py --consecutivos e agrega para nível UF e municipal.

O mapeamento de classes segue o mesmo sistema de 6 grupos usado em
gerar_mapas_lulc_gee_40anos.py e calcular_taxas_lulc.py (D1).

Pré-requisito:
    python scripts/transicoes_mapbiomas.py --consecutivos

Saídas:
    data/processed/conversao_bruta_goias.csv       — nível UF
    data/processed/conversao_bruta_municipal.csv   — nível municipal
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "transicoes"
DIR_PROCESSED = ROOT / "data" / "processed"

# Mapeamento id → grupo (mesmo de calcular_taxas_lulc.py e GEE)
GRUPOS_LULC = {
    "vegetacao_natural": [3, 4, 12],
    "pastagem":           [15],
    "agricultura":        [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],
    "agua":               [31, 33],
    "area_urbana":        [24],
    "outros":             [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],
}

ID_PARA_GRUPO: dict[int, str] = {}
for nome, ids in GRUPOS_LULC.items():
    for cid in ids:
        ID_PARA_GRUPO[cid] = nome

NOMES_GRUPOS = list(GRUPOS_LULC.keys())


def main() -> None:
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Verificar caches consecutivos
    consecutivos = sorted(CACHE_DIR.glob("transicao_????_????.csv"))
    # Filtrar apenas pares consecutivos (diferença de 1 ano)
    pares_consec = []
    for p in consecutivos:
        parts = p.stem.split("_")
        a1, a2 = int(parts[1]), int(parts[2])
        if a2 - a1 == 1:
            pares_consec.append((a1, a2, p))

    pares_consec.sort(key=lambda x: x[0])
    print(f"Encontrados {len(pares_consec)} pares consecutivos (esperado: 39)")

    if len(pares_consec) < 39:
        print("AVISO: Faltam pares consecutivos. Execute:")
        print("  python scripts/transicoes_mapbiomas.py --consecutivos")
        print(f"\nProcessando {len(pares_consec)} pares disponíveis...")

    all_dfs = []
    for ano_orig, ano_dest, path in pares_consec:
        df = pd.read_csv(path)
        df["ano_origem"] = ano_orig
        df["ano_destino"] = ano_dest
        # Mapear classes para grupos
        df["grupo_orig"] = df["classe_orig"].map(ID_PARA_GRUPO)
        df["grupo_dest"] = df["classe_dest"].map(ID_PARA_GRUPO)
        # Filtrar apenas mapeamentos válidos (exclui IDs não mapeados)
        df = df.dropna(subset=["grupo_orig", "grupo_dest"])
        all_dfs.append(df)

    if not all_dfs:
        print("Nenhum dado para processar. Execute --consecutivos primeiro.")
        return

    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"Total de linhas: {len(df_all):,}")

    # ── Nível UF ──
    uf = df_all.groupby(["ano_origem", "ano_destino", "grupo_orig", "grupo_dest"],
                         as_index=False)["area_ha"].sum()
    uf["area_mha"] = uf["area_ha"] / 1e6
    uf = uf.round({"area_ha": 2, "area_mha": 6})

    out_uf = DIR_PROCESSED / "conversao_bruta_goias.csv"
    uf.to_csv(out_uf, index=False)
    print(f"OK: {out_uf.name} ({len(uf)} linhas)")

    # ── Nível municipal ──
    muni = df_all.groupby(["cd_mun", "nm_mun", "ano_origem", "ano_destino",
                           "grupo_orig", "grupo_dest"],
                          as_index=False)["area_ha"].sum()
    muni["area_mha"] = muni["area_ha"] / 1e6
    muni = muni.round({"area_ha": 2, "area_mha": 6})

    out_muni = DIR_PROCESSED / "conversao_bruta_municipal.csv"
    muni.to_csv(out_muni, index=False)
    print(f"OK: {out_muni.name} ({len(muni)} linhas)")

    # ── Resumo ──
    print("\n=== Resumo UF (top 5 fluxos por area, 2023->2024) ===")
    recente = uf[uf["ano_destino"] == 2024].nlargest(5, "area_ha")
    for _, row in recente.iterrows():
        print(f"  {row['grupo_orig']:.15s} -> {row['grupo_dest']:.15s}: "
              f"{row['area_mha']:.4f} Mha")


if __name__ == "__main__":
    main()