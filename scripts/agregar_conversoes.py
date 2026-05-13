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

# Mapeamento id → grupo: os caches GEE (transicao_YYYY_YYYY.csv) já vêm com
# IDs agrupados 1..6 (não com IDs MapBiomas brutos). Ver transicoes_mapbiomas.py.
ID_PARA_GRUPO: dict[int, str] = {
    1: "vegetacao_natural",
    2: "pastagem",
    3: "agricultura",
    4: "agua",
    5: "area_urbana",
    6: "outros",
}

NOMES_GRUPOS = list(ID_PARA_GRUPO.values())

# IBGE: 34.009 Mha. MapBiomas tipicamente reporta 30-32 Mha em GO por causa de
# pixels nao classificados (mais frequentes nos anos iniciais). Tolerancia ampla.
AREA_GOIAS_MHA = 34.009
TOLERANCIA_PCT = 15.0


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

    # Validacao: soma das transicoes por ano-par ~ area de Goias
    print("\n=== Validacao soma de areas por ano-par (esperado ~ 34 Mha) ===")
    soma_por_par = uf.groupby(["ano_origem", "ano_destino"])["area_mha"].sum()
    desvios = []
    for (a1, a2), total in soma_por_par.items():
        desvio_pct = (total - AREA_GOIAS_MHA) / AREA_GOIAS_MHA * 100
        if abs(desvio_pct) > TOLERANCIA_PCT:
            desvios.append((a1, a2, total, desvio_pct))
    print(f"  pares dentro de +/-{TOLERANCIA_PCT:.0f}%: "
          f"{len(soma_por_par) - len(desvios)}/{len(soma_por_par)}")
    print(f"  min: {soma_por_par.min():.3f} Mha  max: {soma_por_par.max():.3f} Mha  "
          f"media: {soma_por_par.mean():.3f} Mha")
    if desvios:
        print(f"  ATENCAO: {len(desvios)} pares com desvio > 1%:")
        for a1, a2, t, d in desvios[:5]:
            print(f"    {a1}->{a2}: {t:.3f} Mha ({d:+.2f}%)")


if __name__ == "__main__":
    main()