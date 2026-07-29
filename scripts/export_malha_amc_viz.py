"""export_malha_amc_viz.py — export de viz (malha cartográfica das AMCs)
=======================================================================

O QUE FAZ
---------
Gera a **base cartográfica** das 166 AMCs de Goiás que o site usa em duas peças:
o painel da Perna 2 (`pastagem-reserva.js`) e o mapa da marcha ao norte
(`marcha-mapa.js`). É geometria + identidade, **sem nenhuma medição**.

POR QUE ESTE SCRIPT EXISTE (2026-07-25)
---------------------------------------
O arquivo que o site servia (`idade_pastagem_amc.geojson`) era **órfão** — nenhum
script do repositório o gerava — e carregava, em `properties.idade_amc`, a idade
média da pastagem na conversão calculada sobre a **amostra** do #28A (43.951 px),
enquanto a seção que o renderizava anunciava o **censo** (44,6 milhões de
eventos). Duas coisas erradas de uma vez: dado velho e dado sem proveniência.

Além disso, a re-checagem sob a união (D26, 23–25/jul/2026) mostrou que o
**gradiente latitudinal de idade é artefato** da mudança de rótulo do Mosaico
(#28C, #40, #33 — três caminhos independentes). Ou seja: um coroplético colorido
por idade não deve existir no site, e o campo `idade_amc` não deve existir no
arquivo. A malha ficou com o que é fato cartográfico — `code_amc`, `mesorregiao`,
`n_munis` — e os valores que o site pinta passam a vir do censo, em tempo de
execução, de `idade_pastagem_regional.json`.

O arquivo mudou de nome (`idade_pastagem_amc` → `malha_amc`) de propósito: uma
malha chamada "idade_pastagem" convida a repintar idade nela.

ENTRADAS
    data/processed/amc_goias.gpkg                    (#25, geometria EPSG:4674)
    data/processed/amc_crosswalk_goias.csv           (#25, cd_mun → code_amc)
    Visualizacao/assets/data/idade_pastagem_municipal.json  (#28 censo, mesorregião)

SAÍDA
    Visualizacao/assets/data/malha_amc.geojson

COMO RODAR
    python scripts/export_malha_amc_viz.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GPKG = ROOT / "data" / "processed" / "amc_goias.gpkg"
CW_AMC = ROOT / "data" / "processed" / "amc_crosswalk_goias.csv"
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"
MUNICIPAL = DIR_VIZ / "idade_pastagem_municipal.json"
SAIDA = DIR_VIZ / "malha_amc.geojson"
SAIDA_MESO = DIR_VIZ / "malha_mesorregiao.geojson"

# 5 casas decimais ≈ 1 m no equador: mais do que suficiente para um mapa de
# 460 px de largura, e corta ~40% do arquivo.
CASAS = 5

# Simplificação (graus). O mapa do site tem ~460 px para ~7° de Goiás, então
# 1 px ≈ 0,015°: com 0,01° o desvio máximo fica abaixo do pixel. Este valor
# reproduz exatamente os 7.289 vértices do arquivo antigo — a malha desenhada
# não muda, só a proveniência. `preserve_topology=True` evita polígono
# degenerado; fendas entre vizinhas ficam sob o traço branco de 0,4 px.
TOLERANCIA = 0.01


def mesorregiao_por_amc(cw: pd.DataFrame) -> pd.DataFrame:
    """Mesorregião de cada AMC = a do município com mais eventos de conversão.

    A AMC agrega municípios que podem cair em mesorregiões diferentes (é uma
    unidade construída por fusão histórica, não por recorte do IBGE). O rótulo
    aqui é só de tooltip; o critério "município de maior peso" é determinístico e
    a discordância é rara.
    """
    muni = pd.DataFrame(json.loads(MUNICIPAL.read_text(encoding="utf-8")))
    m = cw.merge(muni[["cd_mun", "mesorregiao", "n_pixels"]], on="cd_mun", how="left")
    m = m.dropna(subset=["mesorregiao"])
    m = m.sort_values("n_pixels", ascending=False).drop_duplicates("code_amc")
    return m[["code_amc", "mesorregiao"]]


def arredonda(coords, casas: int = CASAS):
    if isinstance(coords[0], (int, float)):
        return [round(float(c), casas) for c in coords]
    return [arredonda(c, casas) for c in coords]


def n_vertices(coords) -> int:
    if isinstance(coords[0], (int, float)):
        return 1
    return sum(n_vertices(c) for c in coords)


def exportar_mesorregioes(gdf: gpd.GeoDataFrame) -> None:
    """Dissolve as AMCs em 5 mesorregiões — o contorno que o site usa como
    *alvo de clique* na peça da Perna 2.

    POR QUE ESTE SEGUNDO ARQUIVO (2026-07-28)
    -----------------------------------------
    A peça mostra duas malhas ao mesmo tempo, de propósito: o **veredito de
    bimodalidade** é por AMC (166 células, quase todas da mesma cor — é a forma
    visual do η² de 0,5%), mas o **histograma** só é ajustável por mesorregião,
    onde o n sustenta o GMM em todos os recortes. Até 28/jul isso ficava numa
    malha para o mapa e noutra para uma fileira de botões, e o leitor não tinha
    como saber que as duas conversavam. Com o contorno dissolvido, o clique
    acontece no mapa: hover acende a mesorregião inteira, clique redesenha o
    histograma. A resolução fina continua desenhada por baixo.

    A dissolução simplifica DEPOIS de unir (união primeiro evita fendas entre
    AMCs vizinhas que a simplificação independente abriria).
    """
    sub = gdf[gdf["mesorregiao"].notna()].copy()
    orfas = len(gdf) - len(sub)
    meso = sub.dissolve(by="mesorregiao", as_index=False)[["mesorregiao", "geometry"]]
    # As AMCs vizinhas não compartilham vértices exatamente coincidentes, então o
    # dissolve deixa fendas capilares e as bordas internas SOBREVIVEM à união
    # (7.784 vértices para 5 polígonos — mais que as 166 AMCs somadas). Fechar e
    # reabrir com ~55 m sela as fendas e derruba para ~1.980 vértices, bem abaixo
    # do pixel do mapa (≈0,015°/px). Feito em graus de propósito: o desvio é
    # isotrópico o bastante nesta latitude e evita duas reprojeções.
    meso["geometry"] = meso.geometry.buffer(0.0005).buffer(-0.0005)
    meso["geometry"] = meso.geometry.simplify(TOLERANCIA, preserve_topology=True)

    geo = json.loads(meso.to_json(drop_id=True, to_wgs84=False))
    geo["name"] = "malha_mesorregiao"
    for f in geo["features"]:
        f["geometry"]["coordinates"] = arredonda(f["geometry"]["coordinates"])

    SAIDA_MESO.write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")
    verts = sum(n_vertices(f["geometry"]["coordinates"]) for f in geo["features"])
    kb = SAIDA_MESO.stat().st_size / 1024
    print(f"[OK] {SAIDA_MESO.relative_to(ROOT)} — {len(geo['features'])} mesorregiões, "
          f"{verts:,} vértices, {kb:.0f} KB"
          + (f" ({orfas} AMC sem mesorregião ficaram de fora do contorno)" if orfas else ""))


def main() -> None:
    gdf = gpd.read_file(GPKG)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    print(f"Malha: {len(gdf)} AMCs, CRS {gdf.crs}")

    cw = pd.read_csv(CW_AMC, dtype={"cd_mun": "int64", "code_amc": "int64"})
    n_munis = cw.groupby("code_amc")["cd_mun"].size().rename("n_munis").reset_index()

    gdf = (gdf.merge(n_munis, on="code_amc", how="left")
              .merge(mesorregiao_por_amc(cw), on="code_amc", how="left"))
    faltando = int(gdf["mesorregiao"].isna().sum())
    if faltando:
        print(f"  [aviso] {faltando} AMC(s) sem mesorregião — ficam null no tooltip")
    gdf["n_munis"] = gdf["n_munis"].fillna(0).astype(int)

    gdf = gdf[["code_amc", "mesorregiao", "n_munis", "geometry"]].copy()
    # O contorno das mesorregiões sai da malha ANTES da simplificação por AMC,
    # para que a união não herde as fendas que a simplificação individual abre.
    exportar_mesorregioes(gdf)

    gdf["geometry"] = gdf.geometry.simplify(TOLERANCIA, preserve_topology=True)
    geo = json.loads(gdf.to_json(drop_id=True, to_wgs84=False))
    geo["name"] = "malha_amc"

    for f in geo["features"]:
        f["geometry"]["coordinates"] = arredonda(f["geometry"]["coordinates"])

    SAIDA.write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")
    kb = SAIDA.stat().st_size / 1024

    verts = sum(n_vertices(f["geometry"]["coordinates"]) for f in geo["features"])
    print(f"[OK] {SAIDA.relative_to(ROOT)} — {len(geo['features'])} feições, "
          f"{verts:,} vértices, {kb:.0f} KB")
    print("     properties:", sorted(geo["features"][0]["properties"]))


if __name__ == "__main__":
    main()
