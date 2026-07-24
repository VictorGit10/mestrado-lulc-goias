"""borda_movel_gee.py — matriz da borda móvel [coleção × ano] via GEE (sem download)
================================================================================

Estende o teste da Coleção 9 (§9 do 28D) para VÁRIAS coleções, server-side. A
razão pasto→Mosaico / pasto→agricultura por ano-calendário é calculada dentro de
Goiás para as coleções 6 (→2020), 8 (→2022), 9 (→2023) e 10.1 (→2024). Como é
uma RAZÃO (numerador e denominador amostrados igual), é robusta à resolução — daí
`scale` grosso, que torna a matriz inteira viável em ~poucos reduceRegion.

A LEITURA (o coração do teste): olhe uma COLUNA (ano-calendário fixo) descendo as
coleções, cada uma pondo esse ano a uma distância diferente da SUA borda terminal:

  • ARTEFATO ancorado na borda → a razão de um ano fixo CAI conforme ele fica mais
    interior nas coleções mais novas (ex.: 2020 alto na Col6/terminal, baixo na
    Col10.1/d=4).
  • REAL / estável no calendário → a razão de um ano fixo é ~CONSTANTE entre
    coleções (a menos do offset de versão ~1,2× medido no teste da Col9).

Cross-valida também as razões LOCAIS da Col9/10.1 (pipeline do #28D): se batem, o
método server-side e o censo local concordam.

SAÍDA  data/processed/borda_movel_matriz_colecoes.csv  (linhas=coleção, cols=ano)

COMO RODAR
    set GEE_PROJECT=extreme-height-447417-a9
    python scripts/borda_movel_gee.py                 # scale=300 (rápido)
    python scripts/borda_movel_gee.py --scale 30      # nativo (lento, referência)

Quando: 2026-07-23. Companheiro do #28D / teste da borda móvel.
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
CSV = ROOT / "data" / "processed" / "borda_movel_matriz_colecoes.csv"

ID_PASTAGEM = 15
ID_MOSAICO = 21
IDS_AGRICULTURA = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

# coleção -> (asset, ano_terminal)
COLECOES = {
    "6":    ("projects/mapbiomas-public/assets/brazil/lulc/collection6/mapbiomas_collection60_integration_v1", 2020),
    "8":    ("projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1", 2022),
    "9":    ("projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1", 2023),
    "10.1": ("projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1", 2024),
}
ANOS = [2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023, 2024]


def razoes_colecao(asset: str, anos: list[int], go, scale: int) -> dict:
    """Um reduceRegion por coleção: empilha agri_Y/mos_Y de todos os anos numa
    imagem multibanda e soma dentro de GO de uma vez só."""
    img = ee.Image(asset)
    bandas = []
    for Y in anos:
        prev = img.select(f"classification_{Y - 1}").eq(ID_PASTAGEM)
        cur = img.select(f"classification_{Y}")
        isagri = cur.remap(IDS_AGRICULTURA, [1] * len(IDS_AGRICULTURA), 0)
        bandas.append(prev.And(isagri).rename(f"agri_{Y}"))
        bandas.append(prev.And(cur.eq(ID_MOSAICO)).rename(f"mos_{Y}"))
    stk = ee.Image.cat(bandas)
    r = stk.reduceRegion(ee.Reducer.sum(), go, scale=scale, maxPixels=int(1e13), tileScale=4)
    return r.getInfo()


def main() -> None:
    p = argparse.ArgumentParser(description="Matriz da borda móvel [coleção × ano] via GEE")
    p.add_argument("--scale", type=int, default=300, help="m; grosso é ok p/ RAZÃO (default 300)")
    args = p.parse_args()

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    go = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM1_NAME", "Goias")).geometry())
    print(f"Goiás (GAUL) | scale={args.scale} m | razão pasto→Mosaico / pasto→agricultura\n")

    linhas = {}
    for nome, (asset, term) in COLECOES.items():
        anos = [a for a in ANOS if a <= term]
        t0 = time.time()
        d = razoes_colecao(asset, anos, go, args.scale)
        linha = {}
        for Y in anos:
            a, m = d.get(f"agri_{Y}", 0), d.get(f"mos_{Y}", 0)
            linha[Y] = (m / a) if a else float("nan")
        linhas[f"col{nome} (→{term})"] = linha
        print(f"col{nome:4s} (→{term}) — {time.time()-t0:.0f}s | " +
              " ".join(f"{Y}:{linha[Y]:.1f}" for Y in anos))

    df = pd.DataFrame(linhas).T.reindex(columns=ANOS)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV)
    print(f"\nMATRIZ razão [coleção × ano] (leia cada COLUNA descendo: cai=artefato / estável=real):")
    print(df.round(1).to_string())
    print(f"\n  -> {CSV}")

    # Diagonais terminais (razão de cada coleção no SEU último ano) vs o mesmo ano na 10.1
    print("\n  Ano terminal de cada coleção (d=0) vs esse ano na 10.1 (interior):")
    for nome, (asset, term) in COLECOES.items():
        if nome == "10.1":
            continue
        rt = linhas[f"col{nome} (→{term})"].get(term, float("nan"))
        r10 = linhas["col10.1 (→2024)"].get(term, float("nan"))
        print(f"    {term}: col{nome}(d=0)={rt:.1f}  ×  col10.1(d={2024-term})={r10:.1f}  "
              f"-> {'BORDA(artefato)' if rt > 2*r10 else 'estável(calendário)'}")


if __name__ == "__main__":
    main()
