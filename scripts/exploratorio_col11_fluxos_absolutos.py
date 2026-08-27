"""exploratorio_col11_fluxos_absolutos.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html ou qualificacao/.

POR QUE ESTE SCRIPT SUBSTITUI OS ANTERIORES COMO LEITURA PRINCIPAL
------------------------------------------------------------------
Os scripts anteriores mediram RAZÃO (M/A dentro de uma coleção) e FATOR (mesmo canal
entre duas coleções). As duas medidas são derivadas, e a razão é frágil: ela tem um
denominador que encolhe 13× entre 2015 e 2024, então explode por motivo aritmético e
fica sensível à escala de leitura.

Aqui a medida é a mais crua possível: **quantos hectares de pastagem viraram Agricultura,
e quantos viraram Mosaico, em cada ano, em cada coleção.** Sem divisão. Cada número é
interpretável sozinho, e a comparação entre coleções é direta.

A leitura de borda × calendário fica trivial nessa forma. A hipótese de borda diz que uma
coleção fica "cautelosa" perto do SEU fim de série: menos Agricultura, mais Mosaico. Então:

  • BORDA      → o tombo da Agricultura acontece no fim de CADA coleção, em anos de
                 calendário DIFERENTES (2020 na col6, 2022 na col8, 2023 na col9...).
  • CALENDÁRIO → o tombo acontece no MESMO ano em todas, inclusive nas que já passaram
                 muito daquele ponto, e falta nas que param antes dele.

A col6 é o caso decisivo: ela termina em 2020, antes da quebra. Se o tombo é de borda,
a col6 tem que despencar no seu 2020.

ESCALA E VALIDAÇÃO
------------------
scale=100 m, em que cada pixel somado é exatamente 1 ha. Conferido contra o censo local
exato do #28 (`pastagem_conversao_destinos.parquet`, 30 m): os fluxos absolutos batem
dentro de poucos por cento. É a razão M/A que degrada com a escala, não os fluxos.

COMO RODAR
    python scripts/exploratorio_col11_fluxos_absolutos.py
    python scripts/exploratorio_col11_fluxos_absolutos.py --validar   (+ censo local)

Quando: 2026-08-26.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "processed" / "exploratorio_col11"
CENSO = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"

ID_PASTAGEM, ID_MOSAICO = 15, 21
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]
BASE = "projects/mapbiomas-public/assets/brazil/lulc"

COLECOES = {
    "6":    (f"{BASE}/collection6/mapbiomas_collection60_integration_v1", 2020),
    "8":    (f"{BASE}/collection8/mapbiomas_collection80_integration_v1", 2022),
    "9":    (f"{BASE}/collection9/mapbiomas_collection90_integration_v1", 2023),
    "10.1": (f"{BASE}/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1", 2024),
    "11":   (f"{BASE}/collection11/mapbiomas_brazil_collection11_coverage_v3", 2025),
}
ANOS = list(range(2010, 2026))


# 16 anos x 3 bandas num reduceRegion só estoura o teto de tempo do GEE
# ("Computation timed out"). Fatiar em blocos de BLOCO anos resolve; as somas são
# independentes por ano, então fatiar não muda resultado nenhum.
BLOCO = 5


def medir(asset: str, anos: list[int], go, scale: int) -> dict:
    img = ee.Image(asset)
    saida: dict = {}
    for i in range(0, len(anos), BLOCO):
        bandas = []
        for Y in anos[i:i + BLOCO]:
            prev = img.select(f"classification_{Y - 1}").eq(ID_PASTAGEM)
            cur = img.select(f"classification_{Y}")
            isagri = cur.remap(IDS_AGRI, [1] * len(IDS_AGRI), 0)
            bandas.append(prev.rename(f"P_{Y}"))
            bandas.append(prev.And(isagri).rename(f"A_{Y}"))
            bandas.append(prev.And(cur.eq(ID_MOSAICO)).rename(f"M_{Y}"))
        saida.update(ee.Image.cat(bandas).reduceRegion(
            ee.Reducer.sum(), go, scale=scale, maxPixels=int(1e13),
            tileScale=4).getInfo())
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — fluxos absolutos por coleção")
    ap.add_argument("--scale", type=int, default=100, help="100 m => 1 px = 1 ha")
    ap.add_argument("--validar", action="store_true", help="compara col10.1 com o censo local")
    args = ap.parse_args()
    scale = args.scale

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    go = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM1_NAME", "Goias")).geometry())

    print("EXPLORATÓRIO — fluxo pasto→lavoura e pasto→Mosaico, em hectares, por coleção")
    print(f"  Goiás | scale={scale} m (1 px = 1 ha)\n")

    linhas = []
    for nome, (asset, term) in COLECOES.items():
        anos = [a for a in ANOS if a <= term]
        t0 = time.time()
        d = medir(asset, anos, go, scale)
        print(f"  col{nome:5s} (→{term}) {len(anos):2d} anos em {time.time() - t0:3.0f}s")
        for Y in anos:
            linhas.append({"colecao": nome, "ano_terminal": term, "ano": Y,
                           "scale_m": scale, "d_da_borda": term - Y,
                           "pasto_base_ha": d[f"P_{Y}"],
                           "para_agricultura_ha": d[f"A_{Y}"],
                           "para_mosaico_ha": d[f"M_{Y}"]})
    df = pd.DataFrame(linhas)
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    csv = DIR_SAIDA / f"col11_fluxos_absolutos_scale{scale}m.csv"
    df.to_csv(csv, index=False)

    for campo, titulo in [("para_agricultura_ha", "PASTO → AGRICULTURA (mil ha/ano)"),
                          ("para_mosaico_ha", "PASTO → MOSAICO (mil ha/ano)")]:
        piv = (df.pivot(index="colecao", columns="ano", values=campo)
                 .reindex(list(COLECOES)) / 1000)
        print(f"\n{titulo}")
        print(piv.round(1).to_string())

    if args.validar and CENSO.exists():
        c = pd.read_parquet(CENSO)
        p = c.groupby(["ano_conversao", "destino"])["n_pixels"].sum().unstack(fill_value=0)
        p = (p * 0.09)  # px de 30 m -> ha
        g = df[df.colecao == "10.1"].set_index("ano")
        print("\nVALIDAÇÃO col10.1 — censo local exato (30 m) × este GEE (100 m), mil ha")
        print(f"{'ano':>5} {'agri censo':>11} {'agri GEE':>10} {'erro':>7} "
              f"{'mos censo':>11} {'mos GEE':>10} {'erro':>7}")
        for Y in [2010, 2015, 2019, 2021, 2023, 2024]:
            if Y not in p.index or Y not in g.index:
                continue
            ac, ag = p.loc[Y, "agricultura"], g.loc[Y, "para_agricultura_ha"]
            mc, mg = p.loc[Y, "mosaico"], g.loc[Y, "para_mosaico_ha"]
            print(f"{Y:>5} {ac/1000:11.1f} {ag/1000:10.1f} {100*(ag-ac)/ac:6.1f}% "
                  f"{mc/1000:11.1f} {mg/1000:10.1f} {100*(mg-mc)/mc:6.1f}%")

    print(f"\n  -> {csv}")
    print("\n  Leitura (linha = coleção, coluna = ano). O tombo da Agricultura cai no")
    print("  MESMO ano em todas as coleções, ou no fim de cada uma? A col6 termina em")
    print("  2020: se o tombo é de borda, ela tem que despencar lá.")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
