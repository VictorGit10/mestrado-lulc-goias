"""gerar_mapas_lulc_gee_rio_verde.py — 40 mapas raster MapBiomas Coleção 10.1
para o município de Rio Verde - GO (1985–2024) via Google Earth Engine.

Adaptação do Pipeline #10 (gerar_mapas_lulc_gee_40anos.py) para o recorte
municipal de Rio Verde (IBGE 5218805), com contorno municipal em preto e
limites dos municípios vizinhos em cinza claro para contexto geográfico.

6 classes agregadas (mesmas do Pipeline #10):
    - Vegetação Natural:  Formação Florestal(3), Savânica(4), Campestre(12)
    - Pastagem:           Pastagem(15)
    - Agricultura:        Silvicultura(9), Lavoura Temporária(19), Cana(20),
                          Dendê(35), Lavoura Perene(36), Soja(39), Arroz(40),
                          Outras Lavouras Temp(41), Café(46), Citros(47),
                          Outras Lavouras Per(48), Algodão(62)
    - NOTA: ID 21 (Mosaico de Agricultura ou Pastagem) excluído intencionalmente
    - Água:               Aquicultura(31), Rio/Lago/Oceano(33)
    - Área Urbana:        Área Urbanizada(24)
    - Outros:             Manguezal(5), Floresta Inundável(6), Área Úmida(11),
                          Praia/Duna/Areia(23), Outras Áreas Não Veg(25),
                          Não Observado(27), Afloramento Rochoso(29), Mineração(30),
                          Apicum(32), Restingas(49,50), Usina Fotovoltaica(75)

Como rodar:
    1. Tenha conta Google registrada em https://earthengine.google.com/signup
    2. Crie um projeto no Google Cloud Console e habilite Earth Engine API
    3. No terminal:   earthengine authenticate
    4. Defina o ID do projeto:  set GEE_PROJECT=meu-projeto-12345  (Windows)
       ou edite GEE_PROJECT_DEFAULT abaixo
    5. python "Scripts e Catalogo/gerar_mapas_lulc_gee_rio_verde.py"

Pré-requisitos:
    pip install earthengine-api geopandas geobr matplotlib matplotlib-scalebar pillow requests

Saída:
    outputs/mapas_gee_rio_verde/cobertura_{ANO}.png       (40 PNGs compostos, DPI 200)
    outputs/mapas_gee_rio_verde/_raw/raw_{ANO}.png        (raster cru do GEE, 2048 px)
"""
from __future__ import annotations

import io
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import geobr
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cartografia import adicionar_norte, adicionar_escala  # noqa: E402

# ===== Configuração =====
GEE_PROJECT_DEFAULT = ""
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"

COD_RIO_VERDE = 5218805

DPI = 200
FIGSIZE = (10, 8)
ANO_MIN, ANO_MAX = 1985, 2024
THUMB_DIM = 2048

CLASSES = {
    "Vegetação Natural": {"ids": [3, 4, 12],                                          "cor": "#1B8A2F"},
    "Pastagem":          {"ids": [15],                                                 "cor": "#FFD700"},
    "Agricultura":       {"ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],      "cor": "#FF69B4"},
    "Água":              {"ids": [31, 33],                                              "cor": "#4169E1"},
    "Área Urbana":       {"ids": [24],                                                  "cor": "#A0A0A0"},
    "Outros":            {"ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],       "cor": "#D2B48C"},
}
ORDEM_LEGENDA = list(CLASSES.keys())

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "mapas_gee_rio_verde"
RAW_DIR = OUT_DIR / "_raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    if not project:
        sys.exit(
            "Erro: defina o ID do projeto Google Cloud.\n"
            "  - via variável de ambiente: set GEE_PROJECT=seu-projeto\n"
            "  - ou edite GEE_PROJECT_DEFAULT no topo deste script."
        )
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception as exc:
        print("Falha ao inicializar Earth Engine.")
        print("Se for primeiro uso, rode no terminal:  earthengine authenticate")
        raise


def construir_remap_palette() -> tuple[list[int], list[int], list[str]]:
    from_ids: list[int] = []
    to_ids: list[int] = []
    palette: list[str] = []
    for idx, (nome, info) in enumerate(CLASSES.items(), start=1):
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
        palette.append(info["cor"])
    return from_ids, to_ids, palette


def carregar_geometria_rio_verde():
    gdf = geobr.read_municipality(code_muni=COD_RIO_VERDE, year=2020).to_crs(4326)
    geom_geojson = gdf.iloc[0].geometry.__geo_interface__
    return ee.Geometry(geom_geojson), gdf


def carregar_vizinhos(gdf_rv):
    gdf_all = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    rv_geom = gdf_rv.iloc[0].geometry
    vizinhos = gdf_all[
        gdf_all.intersects(rv_geom) & (gdf_all["code_muni"].astype(int) != COD_RIO_VERDE)
    ].copy()
    return vizinhos


def baixar_thumbnail(image: ee.Image, params: dict, max_retries: int = 5) -> bytes:
    for tentativa in range(max_retries):
        try:
            url = image.getThumbURL(params)
        except Exception as exc:
            print(f"  getThumbURL falhou (tentativa {tentativa+1}/{max_retries}): {exc}")
            time.sleep(10 * (tentativa + 1))
            continue
        for download_tentativa in range(max_retries):
            r = requests.get(url, timeout=180)
            if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
                return r.content
            time.sleep(5 * (download_tentativa + 1))
        print(f"  download falhou após {max_retries} tentativas (tentativa URL {tentativa+1})")
    raise RuntimeError(f"Falha ao baixar thumbnail após {max_retries} tentativas")


def compor_mapa(raw_bytes: bytes, ano: int, gdf_rv, gdf_vizinhos,
               region_coords, out_path: Path) -> None:
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")

    lons = [c[0] for c in region_coords[0]]
    lats = [c[1] for c in region_coords[0]]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.imshow(img, extent=[min_lon, max_lon, min_lat, max_lat])

    if gdf_vizinhos is not None and len(gdf_vizinhos) > 0:
        gdf_vizinhos.plot(ax=ax, facecolor="none", edgecolor="#CCCCCC", linewidth=0.3)

    gdf_rv.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1.5)

    ax.set_axis_off()
    ax.set_title(f"Cobertura e Uso da Terra — Rio Verde - GO {ano}", fontsize=14)

    handles = [Patch(facecolor=info["cor"], edgecolor="black", label=nome)
               for nome, info in CLASSES.items()]
    ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=8,
              title="Classe (6 grupos)", title_fontsize=9,
              borderaxespad=-1.2)

    bbox_5880 = gdf_rv.to_crs(5880).total_bounds
    largura_metros = bbox_5880[2] - bbox_5880[0]
    largura_graus = max_lon - min_lon
    dx = largura_metros / largura_graus
    adicionar_escala(ax, dx=dx)
    adicionar_norte(ax)

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    # Carregar geometrias localmente (geobr — sem GEE)
    gdf_rv = geobr.read_municipality(code_muni=COD_RIO_VERDE, year=2020).to_crs(4326)
    gdf_vizinhos_full = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    rv_geom_local = gdf_rv.iloc[0].geometry
    gdf_vizinhos = gdf_vizinhos_full[
        gdf_vizinhos_full.intersects(rv_geom_local)
        & (gdf_vizinhos_full["code_muni"].astype(int) != COD_RIO_VERDE)
    ].copy()

    # Bounds em EPSG:4326 — mesmos do region_coords antigo, mas sem GEE
    minx, miny, maxx, maxy = gdf_rv.total_bounds
    region_coords_local = [[
        [minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny],
    ]]

    n_viz = len(gdf_vizinhos)
    print(f"Rio Verde carregado ({n_viz} vizinhos). Iniciando 40 anos ({ANO_MIN}–{ANO_MAX}).")

    # Lazy init GEE — so se algum RAW estiver faltando
    gee_inicializado = False
    img_full = None
    geom_ee = None
    from_ids = to_ids = palette = None
    region_coords_ee = None

    for i, ano in enumerate(range(ANO_MIN, ANO_MAX + 1), start=1):
        out_path = OUT_DIR / f"cobertura_{ano}.png"
        raw_path = RAW_DIR / f"raw_{ano}.png"

        if out_path.exists():
            print(f"[{i:02d}/40] {out_path.name} — ja existe, pulando")
            continue

        t0 = time.time()

        if raw_path.exists():
            raw = raw_path.read_bytes()
            origem = "cache"
        else:
            if not gee_inicializado:
                init_ee()
                img_full = ee.Image(ASSET)
                geom_ee, _ = carregar_geometria_rio_verde()
                from_ids, to_ids, palette = construir_remap_palette()
                region_coords_ee = geom_ee.bounds().coordinates().getInfo()
                gee_inicializado = True

            banda = f"classification_{ano}"
            img = (img_full.select(banda)
                           .clip(geom_ee)
                           .remap(from_ids, to_ids, 0)
                           .selfMask())

            params = {
                "region": region_coords_ee,
                "dimensions": THUMB_DIM,
                "format": "png",
                "min": 1,
                "max": 6,
                "palette": palette,
            }
            raw = baixar_thumbnail(img, params)
            raw_path.write_bytes(raw)
            origem = "GEE"

        compor_mapa(raw, ano, gdf_rv, gdf_vizinhos, region_coords_local, out_path)
        print(f"[{i:02d}/40] {out_path.name}  ({time.time() - t0:.1f}s, {origem})")

    print(f"OK — 40 mapas em {OUT_DIR}")


if __name__ == "__main__":
    main()