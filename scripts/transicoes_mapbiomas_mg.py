"""transicoes_mapbiomas_mg.py — Matrizes de transição pixel-a-pixel
para os 853 municípios de Minas Gerais via Google Earth Engine.

Adaptado de transicoes_mapbiomas.py para MG.
Mesmas 6 classes agregadas, mesma lógica, geometria de MG.

Saída:
    data/processed/transicoes_mapbiomas_mg.csv

Pré-requisitos:
    pip install earthengine-api geopandas geobr pandas

Como rodar:
    python transicoes_mapbiomas_mg.py [--consecutivos] [--force]
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
import geobr
import pandas as pd

# ===== Configuração =====
GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
PIXEL_HA = 0.09

CLASSES = {
    1: {"nome": "Vegetação Natural", "ids": [3, 4, 12],                          "cor": "#1B8A2F"},
    2: {"nome": "Pastagem",          "ids": [15],                                 "cor": "#FFD700"},
    3: {"nome": "Agricultura",       "ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62], "cor": "#FF69B4"},
    4: {"nome": "Água",              "ids": [31, 33],                              "cor": "#4169E1"},
    5: {"nome": "Área Urbana",       "ids": [24],                                  "cor": "#A0A0A0"},
    6: {"nome": "Outros",            "ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],  "cor": "#D2B48C"},
}
NOME_CLASSE = {k: v["nome"] for k, v in CLASSES.items()}

PERIODOS_DEFAULT = [
    (1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024),
    (1985, 2000), (2000, 2010), (2010, 2024),
    (1985, 2010), (1985, 2024),
]

ROOT = Path(__file__).resolve().parent.parent
CSV_SAIDA = ROOT / "data" / "processed" / "transicoes_mapbiomas_mg.csv"
CACHE_DIR = ROOT / "data" / "cache" / "transicoes_mg"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    if not project:
        sys.exit("Erro: defina GEE_PROJECT.")
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception as exc:
        print("Falha ao inicializar Earth Engine. Rode: earthengine authenticate")
        raise


def construir_remap() -> tuple[list[int], list[int]]:
    from_ids, to_ids = [], []
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
    return from_ids, to_ids


def carregar_municipios_mg() -> tuple[list[ee.Feature], pd.DataFrame]:
    """Lê 853 municípios de MG via geobr, simplifica geometrias e retorna lista
    de ee.Feature para processamento em lotes (evita payload >10MB no GEE).

    Retorna (lista de ee.Feature, DataFrame de referência).
    """
    print("Carregando municípios de Minas Gerais (853)...")
    gdf = geobr.read_municipality(code_muni="MG", year=2020).to_crs(4326)
    print(f"  {len(gdf)} municípios carregados")

    # Simplificar geometrias para reduzir tamanho do payload (tolerância ~1km)
    gdf_simplified = gdf.copy()
    gdf_simplified["geometry"] = gdf_simplified["geometry"].simplify(0.008)

    features = []
    for _, row in gdf_simplified.iterrows():
        geom = ee.Geometry(row["geometry"].__geo_interface__)
        feat = ee.Feature(geom, {
            "cd_mun": int(row["code_muni"]),
            "nm_mun": str(row["name_muni"]),
        })
        features.append(feat)

    df = gdf[["code_muni", "name_muni"]].rename(columns={
        "code_muni": "cd_mun", "name_muni": "nm_mun"
    })
    df["cd_mun"] = df["cd_mun"].astype("int64")
    return features, df


def calcular_transicao_par(
    ano_orig: int,
    ano_dest: int,
    img_full: ee.Image,
    features_list: list[ee.Feature],
    df_munis: pd.DataFrame,
    from_ids: list[int],
    to_ids: list[int],
    batch_size: int = 50,
) -> pd.DataFrame:
    band_orig = img_full.select(f"classification_{ano_orig}")
    band_dest = img_full.select(f"classification_{ano_dest}")

    remap_orig = band_orig.remap(from_ids, to_ids, defaultValue=0)
    remap_dest = band_dest.remap(from_ids, to_ids, defaultValue=0)

    mask = remap_orig.gt(0).And(remap_dest.gt(0))
    transition_code = remap_orig.multiply(10).add(remap_dest).toInt()
    transition_code = transition_code.updateMask(mask)

    n_total = len(features_list)
    all_rows = []
    n_batches = (n_total + batch_size - 1) // batch_size

    for b in range(n_batches):
        start = b * batch_size
        end = min(start + batch_size, n_total)
        batch_fc = ee.FeatureCollection(features_list[start:end])
        print(f"    lote {b+1}/{n_batches} (munis {start}-{end-1})...", end=" ", flush=True)

        for scale in [30, 60, 100]:
            try:
                stats = transition_code.reduceRegions(
                    collection=batch_fc,
                    reducer=ee.Reducer.frequencyHistogram(),
                    scale=scale,
                    crs="EPSG:5880",
                ).getInfo()
                if scale > 30:
                    print(f"(scale={scale})", end=" ", flush=True)
                break
            except Exception as exc:
                print(f"falhou scale={scale}", end=" ", flush=True)
                if scale == 100:
                    raise
                time.sleep(10)
        print("OK", flush=True)

        for feat in stats["features"]:
            props = feat["properties"]
            cd_mun = props.get("cd_mun", 0)
            nm_mun = props.get("nm_mun", "")
            hist = props.get("histogram", {})
            if isinstance(hist, dict):
                for code_str, count in hist.items():
                    code = int(code_str)
                    orig = code // 10
                    dest = code % 10
                    if orig > 0 and dest > 0:
                        all_rows.append({
                            "cd_mun": cd_mun,
                            "nm_mun": nm_mun,
                            "ano_de": ano_orig,
                            "ano_para": ano_dest,
                            "classe_de": orig,
                            "classe_para": dest,
                            "area_ha": count * PIXEL_HA,
                        })

    return pd.DataFrame(all_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consecutivos", action="store_true",
                        help="Inclui todos os pares consecutivos 1985-1986, 1986-1987, ...")
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo com cache")
    args = parser.parse_args()

    init_ee()

    periodos = list(PERIODOS_DEFAULT)
    if args.consecutivos:
        for y in range(1985, 2024):
            periodos.append((y, y + 1))

    from_ids, to_ids = construir_remap()
    features_list, df_munis = carregar_municipios_mg()

    print(f"Carregando asset MapBiomas Coleção 10.1...")
    img = ee.Image(ASSET)

    all_rows = []
    for ano_orig, ano_dest in periodos:
        cache_file = CACHE_DIR / f"transicao_{ano_orig}-{ano_dest}.csv"
        if cache_file.exists() and not args.force:
            print(f"  [cache] {ano_orig}-{ano_dest}")
            df_par = pd.read_csv(cache_file)
        else:
            print(f"  Processando {ano_orig} -> {ano_dest}...")
            df_par = calcular_transicao_par(ano_orig, ano_dest, img, features_list, df_munis, from_ids, to_ids)
            df_par.to_csv(cache_file, index=False)
            print(f"    {len(df_par):,} registros salvos")
        all_rows.append(df_par)

    resultado = pd.concat(all_rows, ignore_index=True)

    # Adicionar nomes de classe
    resultado["classe_de_nome"] = resultado["classe_de"].map(NOME_CLASSE)
    resultado["classe_para_nome"] = resultado["classe_para"].map(NOME_CLASSE)

    resultado.to_csv(CSV_SAIDA, index=False)
    print(f"\nSaída: {CSV_SAIDA}")
    print(f"  {len(resultado):,} registros, {resultado['cd_mun'].nunique()} municípios")


if __name__ == "__main__":
    main()