"""exploratorio_col11_concordancia.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html, qualificacao/ nem cria pipeline novo.

O QUE FAZ (três perguntas de contexto, numa varredura só)
--------------------------------------------------------
Antes de discutir o que a Coleção 11 muda no Mosaico, é preciso saber o TAMANHO da revisão
como um todo. Sem isso não há como dizer se o Mosaico foi tratado de forma especial ou se
apenas acompanhou uma troca geral de rótulos. Este script responde:

  N10  Concordância global — que fração dos pixels de Goiás recebe o MESMO rótulo nas duas
       coleções, por ano? É a linha de base contra a qual tudo o mais se compara.
  N11  Matriz de confusão compacta — para onde vai cada categoria. Em cinco categorias
       (pastagem, agricultura, mosaico, vegetação natural, outros), não nas 20+ classes
       cruas, porque é a partição que o dossiê usa e a que tem leitura.
  N12  Latitude média de CADA célula da matriz — onde, no eixo Sul→Norte, cada tipo de
       discordância acontece. É o que liga a revisão ao centro de massa.

MÉTODO E ESCALA. Roda no GEE em **escala nativa (30 m)**, porque a matriz de confusão é uma
contagem de coincidência pixel-a-pixel e degrada com reamostragem por moda — diferente dos
fluxos, que se mostraram estáveis. Duas chamadas por ano: um `frequencyHistogram` sobre a
chave combinada (25 células de uma vez) e um `mean` agrupado para a latitude. A geometria é
`FAO/GAUL/2015` — ⚠️ NÃO é a malha do IBGE usada no censo local, então as ÁREAS absolutas
daqui não são comparáveis com as do dossiê; as FRAÇÕES e as latitudes são.

COMO RODAR
    python scripts/exploratorio_col11_concordancia.py
    python scripts/exploratorio_col11_concordancia.py --anos 2024 --escala 30

Quando: 2026-08-27.
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

ID_PASTAGEM, ID_MOSAICO = 15, 21
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]
IDS_VEG = [3, 4, 5, 11, 12, 32, 49, 50]

CATS = ["outros", "pastagem", "agricultura", "mosaico", "veg_natural"]
N_CAT = len(CATS)

BASE = "projects/mapbiomas-public/assets/brazil/lulc"
ASSET_101 = f"{BASE}/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
ASSET_11 = f"{BASE}/collection11/mapbiomas_brazil_collection11_coverage_v3"
ANOS_PADRAO = [2010, 2019, 2024]


def categorizar(img: ee.Image) -> ee.Image:
    """Classe crua -> categoria compacta 0..4, na ordem de CATS."""
    ids = [ID_PASTAGEM] + IDS_AGRI + [ID_MOSAICO] + IDS_VEG
    vals = ([1] + [2] * len(IDS_AGRI) + [3] + [4] * len(IDS_VEG))
    return img.remap(ids, vals, 0)


def medir_ano(Y: int, go, escala: int) -> tuple[dict, dict]:
    c101 = categorizar(ee.Image(ASSET_101).select(f"classification_{Y}"))
    c11 = categorizar(ee.Image(ASSET_11).select(f"classification_{Y}"))
    chave = c101.multiply(N_CAT).add(c11).rename("chave")

    h = chave.reduceRegion(ee.Reducer.frequencyHistogram(), go, scale=escala,
                           maxPixels=int(1e13), tileScale=8).getInfo()
    cont = {int(float(k)): int(round(v)) for k, v in (next(iter(h.values())) or {}).items()}

    lat = ee.Image.pixelLonLat().select("latitude").rename("lat").addBands(chave)
    g = lat.reduceRegion(
        ee.Reducer.mean().group(groupField=1, groupName="chave"),
        go, scale=escala, maxPixels=int(1e13), tileScale=8).getInfo()
    lats = {int(d["chave"]): d["mean"] for d in g.get("groups", [])}
    return cont, lats


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — concordância 10.1 × 11")
    ap.add_argument("--anos", type=int, nargs="+", default=ANOS_PADRAO)
    ap.add_argument("--escala", type=int, default=30, help="m; 30 = nativo")
    args = ap.parse_args()

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    go = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM1_NAME", "Goias")).geometry())

    print("EXPLORATÓRIO — concordância e matriz de confusão, Coleção 10.1 × Coleção 11")
    print(f"  Goiás (GAUL) | escala={args.escala} m | categorias: {', '.join(CATS)}\n")

    linhas = []
    for Y in sorted(args.anos):
        t0 = time.time()
        cont, lats = medir_ano(Y, go, args.escala)
        tot = sum(cont.values())
        diag = sum(v for k, v in cont.items() if k // N_CAT == k % N_CAT)
        print(f"  {Y}: concordância global = {100*diag/tot:.2f}%  "
              f"({tot:,} px, {time.time()-t0:.0f}s)", flush=True)
        for k, v in sorted(cont.items()):
            linhas.append({"ano": Y, "escala_m": args.escala,
                           "de_col10_1": CATS[k // N_CAT], "para_col11": CATS[k % N_CAT],
                           "n_pixels": v, "frac_do_total": v / tot,
                           "lat_media": lats.get(k)})
    df = pd.DataFrame(linhas)
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    csv = DIR_SAIDA / f"col11_concordancia_escala{args.escala}m.csv"
    df.to_csv(csv, index=False)

    for Y in sorted(args.anos):
        d = df[df.ano == Y]
        print(f"\n=== {Y} — matriz de confusão (% do total de pixels) ===")
        piv = d.pivot(index="de_col10_1", columns="para_col11",
                      values="frac_do_total").reindex(index=CATS, columns=CATS) * 100
        print(piv.round(2).to_string())
        print(f"\n=== {Y} — latitude média de cada célula (maior = mais ao norte) ===")
        pl = d.pivot(index="de_col10_1", columns="para_col11",
                     values="lat_media").reindex(index=CATS, columns=CATS)
        print(pl.round(3).to_string())

    print(f"\n  -> {csv}")
    print("  ⚠️  Áreas absolutas usam GAUL, não a malha do IBGE: frações e latitudes")
    print("      são comparáveis com o dossiê; hectares NÃO são.")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
