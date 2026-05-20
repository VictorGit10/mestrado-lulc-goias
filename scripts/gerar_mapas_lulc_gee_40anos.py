"""gerar_mapas_lulc_gee_40anos.py — 40 mapas raster MapBiomas Coleção 10.1
para Goiás (1985–2024) via Google Earth Engine.

6 classes agregadas (baseadas nas classes folha do MapBiomas Coleção 10.1):
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
    5. python "Scripts e Catalogo/gerar_mapas_lulc_gee_40anos.py"

Pré-requisitos:
    pip install earthengine-api geopandas geobr matplotlib matplotlib-scalebar pillow requests

Saída:
    outputs/mapas_gee/cobertura_{ANO}.png       (40 PNGs compostos, DPI 200)
    outputs/mapas_gee/_raw/raw_{ANO}.png        (raster cru do GEE, 2048 px)
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
GEE_PROJECT_DEFAULT = ""  # ex: "ee-victoramaral"; ou use env var GEE_PROJECT
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"

DPI = 200
FIGSIZE = (10, 8)
ANO_MIN, ANO_MAX = 1985, 2024
THUMB_DIM = 2048  # largura máx em pixels do thumbnail GEE

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
OUT_DIR = ROOT / "outputs" / "mapas_gee"
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
    """Mapeia IDs originais MapBiomas → 1..6 (6 classes agregadas).
    Retorna (from_ids, to_ids, palette_6_cores).
    """
    from_ids: list[int] = []
    to_ids: list[int] = []
    palette: list[str] = []
    for idx, (nome, info) in enumerate(CLASSES.items(), start=1):
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
        palette.append(info["cor"])
    return from_ids, to_ids, palette


def carregar_geometria_go():
    """Lê polígono de Goiás via geobr e converte para ee.Geometry (EPSG:4326)."""
    gdf = geobr.read_state(code_state="GO", year=2020).to_crs(4326)
    geom_geojson = gdf.iloc[0].geometry.__geo_interface__
    return ee.Geometry(geom_geojson), gdf


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


def compor_mapa(raw_bytes: bytes, ano: int, gdf_go, out_path: Path) -> None:
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.imshow(img)
    ax.set_axis_off()
    ax.set_title(f"Cobertura e Uso da Terra — Goiás {ano}", fontsize=14)

    handles = [Patch(facecolor=info["cor"], edgecolor="black", label=nome)
               for nome, info in CLASSES.items()]
    ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=8,
              title="Classe (6 grupos)", title_fontsize=9,
              borderaxespad=-1.2)

    # Barra de escala: pixels do thumbnail mapeiam para extent real de GO em metros
    bbox_5880 = gdf_go.to_crs(5880).total_bounds  # [minx, miny, maxx, maxy] em metros
    largura_metros = bbox_5880[2] - bbox_5880[0]
    largura_pixels = img.size[0]
    metros_por_pixel = largura_metros / largura_pixels
    adicionar_escala(ax, dx=metros_por_pixel, total_km=150)
    adicionar_norte(ax)

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    # Lazy init: so conecta ao GEE se algum RAW estiver faltando
    gee_inicializado = False
    img_full = None
    geom = None
    gdf_go = None
    from_ids = to_ids = palette = None
    region_coords = None

    # Carrega geometria de GO localmente (sem GEE) para o calculo de escala
    import geobr as _geobr
    gdf_go_local = _geobr.read_state(code_state="GO", year=2020).to_crs(4326)
    print(f"Iniciando 40 anos ({ANO_MIN}–{ANO_MAX}).")

    for i, ano in enumerate(range(ANO_MIN, ANO_MAX + 1), start=1):
        out_path = OUT_DIR / f"cobertura_{ano}.png"
        raw_path = RAW_DIR / f"raw_{ano}.png"

        if out_path.exists():
            print(f"[{i:02d}/40] {out_path.name} — ja existe, pulando")
            continue

        t0 = time.time()

        # Reusar RAW em cache, se existir — evita chamada GEE
        if raw_path.exists():
            raw = raw_path.read_bytes()
            origem = "cache"
        else:
            if not gee_inicializado:
                init_ee()
                img_full = ee.Image(ASSET)
                geom, gdf_go = carregar_geometria_go()
                from_ids, to_ids, palette = construir_remap_palette()
                region_coords = geom.bounds().coordinates().getInfo()
                gee_inicializado = True

            banda = f"classification_{ano}"
            img = (img_full.select(banda)
                           .clip(geom)
                           .remap(from_ids, to_ids, 0)
                           .selfMask())

            params = {
                "region": region_coords,
                "dimensions": THUMB_DIM,
                "format": "png",
                "min": 1,
                "max": 6,
                "palette": palette,
            }
            raw = baixar_thumbnail(img, params)
            raw_path.write_bytes(raw)
            origem = "GEE"

        compor_mapa(raw, ano, gdf_go_local, out_path)
        print(f"[{i:02d}/40] {out_path.name}  ({time.time() - t0:.1f}s, {origem})")

    print(f"OK — 40 mapas em {OUT_DIR}")


if __name__ == "__main__":
    main()
