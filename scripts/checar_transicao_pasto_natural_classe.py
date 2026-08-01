"""checar_transicao_pasto_natural_classe.py — diagnóstico de classe BRUTA.

Testa a hipótese: o fluxo reverso pastagem -> "vegetação natural" observado nas
matrizes agregadas (#12B) é majoritariamente OSCILAÇÃO DE CLASSIFICADOR na
fronteira pastagem(15) <-> campo natural(12), e não regeneração real para
floresta(3)/savana(4).

Motivo: o GRUPO_MAP colapsa 3 (Florestal) + 4 (Savânica) + 12 (Campestre) num
único grupo "vegetacao_natural" ANTES de contar a transição. Depois de colapsar,
pasto->12 e pasto->3 viram o mesmo número, e a "diagonal" natural->natural esconde
o churn intra-grupo (floresta<->savana<->campo). Este script NÃO colapsa: conta
transições em nível de classe bruta do MapBiomas.

Saída: data/processed/checar_transicao_pasto_natural_classe.csv — matriz
{3,4,12,15} x {3,4,12,15} (area_ha) para cada par de anos pedido, mais o
veredito (pasto->12 vs pasto->3, etc.).

Reusa as constantes e o carregador de municípios de processa_cubo_idade (pc).
"""
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHARDS = ROOT / "data" / "raw" / "cubo_go"
CSV_SAIDA = ROOT / "data" / "processed" / "checar_transicao_pasto_natural_classe.csv"

# Classes de interesse (IDs brutos MapBiomas 10.1).
FLORESTA, SAVANA, CAMPO, PASTO = 3, 4, 12, 15
CLASSES_INT = [FLORESTA, SAVANA, CAMPO, PASTO]
NOMES = {3: "Floresta(3)", 4: "Savana(4)", 12: "CampoNatural(12)", 15: "Pastagem(15)"}

# Pares a medir. Longos = conversão decenal (regeneração real deveria aparecer
# aqui); consecutivos = oscilação ano-a-ano (ruído de classificador aparece aqui).
PARES = [
    # decadais / por Ato
    (1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024),
    # série inteira
    (1985, 2024),
    # consecutivos (oscilação) — um por Ato + fim de série
    (1995, 1996), (2005, 2006), (2015, 2016), (2023, 2024),
]


def main() -> None:
    tifs = sorted(SHARDS.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {SHARDS}")

    with rasterio.open(tifs[0]) as s0:
        n_bandas = s0.count
    if n_bandas != pc.N_ANOS:
        pc.N_ANOS = n_bandas
        pc.ANO_MAX = pc.ANO_MIN + n_bandas - 1
        print(f"  cubo com {n_bandas} bandas -> ANO_MAX={pc.ANO_MAX}")

    # Bandas efetivamente necessárias (1-indexadas p/ rasterio). Ler só essas:
    anos_usados = sorted({a for par in PARES for a in par})
    banda_para_ano = {a - pc.ANO_MIN + 1: a for a in anos_usados}
    indexes = sorted(banda_para_ano)  # 1-indexados
    print(f"  lendo só {len(indexes)} bandas/ano: {[banda_para_ano[b] for b in indexes]}")

    # índice local (0-based) de cada ano dentro do array lido:
    idx_local = {a: i for i, b in enumerate(indexes) for a in [banda_para_ano[b]]}
    pares_idx = [(idx_local[a0], idx_local[a1]) for a0, a1 in PARES]

    gdf_muni = pc.carregar_municipios()
    print(f"  {len(gdf_muni)} municípios | {len(tifs)} shards")

    # Acumulador: matriz 256x256 (area_ha) por par. Sem colapsar classes.
    acc = np.zeros((len(PARES), 256 * 256), dtype=np.float64)
    tam_janela = 2048

    t_ini = time.time()
    for i, tif in enumerate(tifs, 1):
        t0 = time.time()
        with rasterio.open(tif) as src:
            muni = rasterize(
                ((g, k) for g, k in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
                out_shape=(src.height, src.width),
                transform=src.transform, fill=0, dtype=np.uint16,
            )
            if not muni.any():
                print(f"[{i:02d}/{len(tifs)}] {tif.name} — fora de GO")
                continue
            # peso de área por linha: cos(lat) * AREA_PX_EQUADOR / 10000 ha
            lats = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
            w_row = np.cos(np.radians(lats)) * pc.AREA_PX_EQUADOR / 10_000.0  # ha/px
            for top in range(0, src.height, tam_janela):
                for left in range(0, src.width, tam_janela):
                    h = min(tam_janela, src.height - top)
                    w = min(tam_janela, src.width - left)
                    mj = muni[top:top + h, left:left + w]
                    if not mj.any():
                        continue
                    arr = src.read(indexes=indexes, window=Window(left, top, w, h))
                    plano = arr.reshape(len(indexes), -1)
                    pos = np.flatnonzero(mj.reshape(-1))
                    g = plano[:, pos].astype(np.int64)  # (n_bandas_lidas, n_px)
                    wpx = np.broadcast_to(w_row[top:top + h, None],
                                           (h, w)).reshape(-1)[pos]
                    for k, (i0, i1) in enumerate(pares_idx):
                        chave = g[i0] * 256 + g[i1]
                        acc[k] += np.bincount(chave, weights=wpx,
                                              minlength=256 * 256)
        print(f"[{i:02d}/{len(tifs)}] {tif.name} ({time.time() - t0:.0f}s)")
    print(f"Total: {time.time() - t_ini:.0f}s")

    # Decodifica só o sub-bloco de interesse.
    linhas = []
    for k, (a0, a1) in enumerate(PARES):
        mat = acc[k].reshape(256, 256)  # [orig, dest] em area_ha
        for o in CLASSES_INT:
            for d in CLASSES_INT:
                linhas.append({
                    "ano_origem": a0, "ano_destino": a1,
                    "classe_orig": o, "classe_dest": d,
                    "nome_orig": NOMES[o], "nome_dest": NOMES[d],
                    "area_ha": float(mat[o, d]),
                })
    df = pd.DataFrame(linhas)
    df["area_ha"] = df["area_ha"].round(2)
    df.to_csv(CSV_SAIDA, index=False)
    print(f"OK: {CSV_SAIDA}")

    # Veredito direto no stdout.
    print("\n=== VEREDITO (area_ha) ===")
    for a0, a1 in PARES:
        sub = df[(df.ano_origem == a0) & (df.ano_destino == a1)]
        p_f = sub[(sub.classe_orig == PASTO) & (sub.classe_dest == FLORESTA)].area_ha.iloc[0]
        p_s = sub[(sub.classe_orig == PASTO) & (sub.classe_dest == SAVANA)].area_ha.iloc[0]
        p_c = sub[(sub.classe_orig == PASTO) & (sub.classe_dest == CAMPO)].area_ha.iloc[0]
        rev_f = sub[(sub.classe_orig == FLORESTA) & (sub.classe_dest == PASTO)].area_ha.iloc[0]
        rev_s = sub[(sub.classe_orig == SAVANA) & (sub.classe_dest == PASTO)].area_ha.iloc[0]
        rev_c = sub[(sub.classe_orig == CAMPO) & (sub.classe_dest == PASTO)].area_ha.iloc[0]
        total_rev = p_f + p_s + p_c
        print(f"\n{a0}->{a1}  (pasto->natural = {total_rev:,.0f} ha)")
        print(f"  pasto->Floresta(3): {p_f:10,.0f} ha   ({p_f/total_rev*100:4.1f}% do reverso)" if total_rev else "")
        print(f"  pasto->Savana(4):   {p_s:10,.0f} ha   ({p_s/total_rev*100:4.1f}% do reverso)" if total_rev else "")
        print(f"  pasto->Campo(12):   {p_c:10,.0f} ha   ({p_c/total_rev*100:4.1f}% do reverso)" if total_rev else "")
        print(f"  --- reverso natural->pasto: Floresta {rev_f:,.0f} | Savana {rev_s:,.0f} | Campo {rev_c:,.0f} ha")


if __name__ == "__main__":
    main()