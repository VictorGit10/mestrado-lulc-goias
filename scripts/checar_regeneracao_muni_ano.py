"""checar_regeneracao_muni_ano.py — fluxo reverso pasto→{floresta,savana,campo} por
município-ano, em classe BRUTA (sem colapsar o GRUPO_MAP).

Complementa checar_transicao_pasto_natural_classe.py (que é estadual): aqui mantemos a
dimensão município para permitir correlação com variáveis socioeconômicas do painel
(crédito, fogo, rebanho, soja). Isola:
  - pasto(15)->floresta(3)  = regeneração real (lenhosa, lenta)
  - pasto(15)->savana(4)   = oscilação de borda pasto<->cerrado (ruído de classificador)
  - pasto(15)->campo(12)   = ~0 em GO (controle)
e os reversos 3->15, 4->15, 12->15.

Saída: data/processed/regeneracao_muni_ano.csv
  cd_mun, nm_mun, ano (ano de destino = t), pasto_floresta_ha, pasto_savana_ha,
  pasto_campo_ha, floresta_pasto_ha, savana_pasto_ha, campo_pasto_ha

Só pares CONSECUTIVOS (t-1 -> t), 39 pares (1986..2024). Reusa pc (constantes + muni).
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
CSV_SAIDA = ROOT / "data" / "processed" / "regeneracao_muni_ano.csv"

FLORESTA, SAVANA, CAMPO, PASTO = 3, 4, 12, 15
# 6 transições de interesse, indexadas 0..5
TRANS = [
    (PASTO, FLORESTA),   # 0: regeneração real
    (PASTO, SAVANA),     # 1: oscilação
    (PASTO, CAMPO),      # 2: controle (~0)
    (FLORESTA, PASTO),   # 3: reverso
    (SAVANA, PASTO),     # 4: reverso
    (CAMPO, PASTO),      # 5: reverso
]
N_T = len(TRANS)


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

    n_pares = pc.N_ANOS - 1  # consecutivos: 1985-86 .. 2023-24
    anos_dest = list(range(pc.ANO_MIN + 1, pc.ANO_MAX + 1))  # t = 1986..2024

    gdf_muni = pc.carregar_municipios()
    n_muni = len(gdf_muni)            # 246
    n_slots = n_muni + 1              # +1 (idx 0 = fora de GO)
    print(f"  {n_muni} municípios | {len(tifs)} shards | {n_pares} pares consecutivos")

    # LUT 256x256 -> id de transição (0..5) ou -1.
    pair_lut = np.full((256, 256), -1, dtype=np.int8)
    for k, (o, d) in enumerate(TRANS):
        pair_lut[o, d] = k

    # acumulador: (n_pares, n_slots, N_T) em area_ha
    acc = np.zeros((n_pares, n_slots, N_T), dtype=np.float64)
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
            lats = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
            w_row = np.cos(np.radians(lats)) * pc.AREA_PX_EQUADOR / 10_000.0  # ha/px
            for top in range(0, src.height, tam_janela):
                for left in range(0, src.width, tam_janela):
                    h = min(tam_janela, src.height - top)
                    w = min(tam_janela, src.width - left)
                    mj = muni[top:top + h, left:left + w]
                    if not mj.any():
                        continue
                    arr = src.read(window=Window(left, top, w, h))  # (N_ANOS, h, w)
                    plano = arr.reshape(pc.N_ANOS, -1)
                    pos = np.flatnonzero(mj.reshape(-1))
                    g = plano[:, pos].astype(np.int64)            # (N_ANOS, n_px)
                    muni_px = mj.reshape(-1)[pos].astype(np.int64)
                    wpx = np.broadcast_to(w_row[top:top + h, None],
                                          (h, w)).reshape(-1)[pos]
                    # 39 pares consecutivos
                    for j in range(n_pares):
                        orig = g[j]
                        dest = g[j + 1]
                        t_id = pair_lut[orig, dest]              # (n_px,) -1..5
                        m = t_id >= 0
                        if not m.any():
                            continue
                        chave = muni_px[m] * N_T + t_id[m]
                        acc[j] += np.bincount(chave, weights=wpx[m],
                                              minlength=n_slots * N_T).reshape(n_slots, N_T)
        print(f"[{i:02d}/{len(tifs)}] {tif.name} ({time.time() - t0:.0f}s)")
    print(f"Total cubo: {time.time() - t_ini:.0f}s")

    # Decodifica
    idx_para_cd = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.cd_mun.astype(int)))
    idx_para_nm = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.nm_mun))
    nomes = ["pasto_floresta_ha", "pasto_savana_ha", "pasto_campo_ha",
             "floresta_pasto_ha", "savana_pasto_ha", "campo_pasto_ha"]
    linhas = []
    for j, ano in enumerate(anos_dest):
        mat = acc[j]  # (n_slots, N_T)
        for mi in range(1, n_slots):  # pula idx 0 (fora de GO)
            if not mat[mi].any():
                continue
            linhas.append({
                "cd_mun": idx_para_cd.get(mi, 0),
                "nm_mun": idx_para_nm.get(mi, ""),
                "ano": ano,
                **{nomes[k]: float(mat[mi, k]) for k in range(N_T)},
            })
    df = pd.DataFrame(linhas)
    for c in nomes:
        df[c] = df[c].round(3)
    df = df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    df.to_csv(CSV_SAIDA, index=False)
    print(f"OK: {CSV_SAIDA}  ({len(df):,} linhas muni-ano)")

    # Telemetria estadual rápida
    print("\n=== Totais estaduais (ha/ano, soma dos pares consecutivos) ===")
    for c in nomes:
        print(f"  {c:22s}: {df[c].sum():,.0f} ha (soma 1986-2024)")


if __name__ == "__main__":
    main()