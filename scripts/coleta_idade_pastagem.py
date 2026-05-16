"""coleta_idade_pastagem.py — Pipeline #28
Amostragem de pixels que sofreram transição pastagem → agricultura em Goiás
(1986–2024), com idade da pastagem no momento da conversão e classe
imediatamente anterior à fase pastagem.

Estratégia: o GEE faz apenas máscara + sample com 40 bandas classification_YYYY.
O cálculo de idade e classe-antes é feito LOCALMENTE em Python (pandas), o que
evita encadear 35+ operações em ee.Image e estourar o limite computacional do
servidor.

Hipótese: pastagem como "reserva de terra" — distribuição da idade na conversão
distingue mecanismo premeditado (curta) do oportunístico (longa).

Como rodar:
    1. earthengine authenticate
    2. set GEE_PROJECT=extreme-height-447417-a9
    3. python scripts/coleta_idade_pastagem.py            (coleta completa)
    4. python scripts/coleta_idade_pastagem.py --teste    (validação 1 ano)

Pré-requisitos:
    pip install earthengine-api geopandas geobr pandas shapely
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import geobr
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# ===== Configuração =====
GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"

ID_PASTAGEM = 15
IDS_AGRICULTURA = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

GRUPO_MAP = {
    "vegetacao_natural": [3, 4, 12],
    "pastagem":          [15],
    "agricultura":       [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],
    "agua":              [31, 33],
    "area_urbana":       [24],
    "outros":            [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],
}
ID_PARA_GRUPO = {cid: nome for nome, ids in GRUPO_MAP.items() for cid in ids}

N_PIXELS_POR_ANO_DEFAULT = 2000
SEED = 42
ANO_MIN = 1985
ANO_MAX = 2024

ROOT = Path(__file__).resolve().parent.parent
CSV_SAIDA = ROOT / "data" / "processed" / "pastagem_idade_conversao.csv"
CACHE_DIR = ROOT / "data" / "cache" / "idade_pastagem"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception:
        print("Falha ao inicializar Earth Engine. Rode: earthengine authenticate")
        raise


def carregar_municipios_gdf() -> gpd.GeoDataFrame:
    """246 munis de GO em EPSG:4326 — usado para overlay local pós-amostragem."""
    gdf = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    gdf = gdf.rename(columns={"code_muni": "cd_mun", "name_muni": "nm_mun"})
    gdf["cd_mun"] = gdf["cd_mun"].astype("int64")
    return gdf[["cd_mun", "nm_mun", "geometry"]]


def carregar_mesorregioes() -> dict[int, str]:
    csv = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
    if not csv.exists():
        return {}
    df = pd.read_csv(csv, dtype={"cd_mun": "int64"})
    col = next(
        (c for c in df.columns if c.lower() in ("mesorregiao", "nm_meso", "meso")),
        None,
    )
    if col is None:
        return {}
    return dict(zip(df["cd_mun"].astype(int), df[col].astype(str)))


def amostrar_ano_via_gee(
    ano_conv: int,
    img_full: ee.Image,
    region: ee.Geometry,
    n_pixels: int,
) -> pd.DataFrame:
    """GEE só faz máscara P→A e sample. Retorna DataFrame com todas as bandas
    classification_1985..ano_conv-1 + lon/lat para cada pixel amostrado.

    Tenta tileScale crescente (8 → 16 → 32) se o GEE retornar memory error.
    Para anos com muitas transições (~2000+, pós-Lei Kandir), a stack de bandas
    fica grande e o GEE precisa mais tiles para processar.
    """
    if ano_conv <= ANO_MIN:
        return pd.DataFrame()

    band_orig = img_full.select(f"classification_{ano_conv - 1}")
    band_dest = img_full.select(f"classification_{ano_conv}")
    foi_pastagem = band_orig.eq(ID_PASTAGEM)
    virou_agric = band_dest.remap(
        IDS_AGRICULTURA, [1] * len(IDS_AGRICULTURA), defaultValue=0
    ).gt(0)
    mask_conv = foi_pastagem.And(virou_agric)

    bandas = [f"classification_{a}" for a in range(ANO_MIN, ano_conv)]
    stack = (
        img_full.select(bandas)
        .addBands(ee.Image.pixelLonLat())
        .addBands(mask_conv.rename("classe_mask").toInt8())
        .updateMask(mask_conv)
    )

    info = None
    ultima_excecao = None
    # Timeouts crescentes em segundos; tileScale crescente
    tentativas = [(8, 240), (16, 480), (32, 720)]
    for ts, timeout_s in tentativas:
        try:
            fc = stack.stratifiedSample(
                numPoints=n_pixels,
                classBand="classe_mask",
                region=region,
                scale=30,
                seed=SEED,
                geometries=False,
                tileScale=ts,
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(fc.getInfo)
                try:
                    info = future.result(timeout=timeout_s)
                    if ts > 8:
                        print(f"    (sucesso com tileScale={ts})")
                    break
                except concurrent.futures.TimeoutError:
                    print(f"    tileScale={ts} timeout após {timeout_s}s; tentando maior")
                    future.cancel()
                    continue
        except Exception as exc:
            msg = str(exc)
            ultima_excecao = exc
            print(f"    tileScale={ts} erro: {msg[:80]}")
            continue
    if info is None:
        raise RuntimeError(f"Todos os tileScale falharam para {ano_conv}: {ultima_excecao}")
    feats = info.get("features", [])
    if not feats:
        return pd.DataFrame()

    rows = [f.get("properties", {}) for f in feats]
    df = pd.DataFrame(rows)
    df["ano_conversao"] = ano_conv
    return df


def calcular_idade_e_origem(df: pd.DataFrame, ano_conv: int) -> pd.DataFrame:
    """Aplica lógica de idade da pastagem e classe-antes em Python.

    Para cada pixel:
      - Idade em ano_conv-1: número de anos consecutivos imediatamente
        anteriores (incluindo ano_conv-1) em que classification == 15.
      - Classe-antes: classification no ano IMEDIATAMENTE ANTERIOR ao início
        da fase pastagem. Se idade abrange até 1985, marca censurado.
    """
    if df.empty:
        return df

    anos = list(range(ANO_MIN, ano_conv))
    cols = [f"classification_{a}" for a in anos]
    presentes = [c for c in cols if c in df.columns]
    if not presentes:
        return pd.DataFrame()

    arr = df[presentes].to_numpy(dtype="int32")  # shape (N, n_anos)
    is_past = (arr == ID_PASTAGEM).astype("int8")
    n_pix, n_anos = is_past.shape

    # Idade: percorre da esquerda (1985) para direita (ano_conv-1) mantendo
    # contador que reseta a 0 quando não é pastagem.
    idade_serie = np.zeros((n_pix, n_anos), dtype="int16")
    for j in range(n_anos):
        if j == 0:
            idade_serie[:, j] = is_past[:, j]
        else:
            idade_serie[:, j] = (idade_serie[:, j - 1] + 1) * is_past[:, j]
    idade_final = idade_serie[:, -1]  # idade em ano_conv-1

    # Classe-antes: idx_inicio = (n_anos - 1) - (idade - 1) = n_anos - idade
    # Ano correspondente = ANO_MIN + idx_inicio
    # Classe antes = classification[idx_inicio - 1]; se idx_inicio == 0 → censura
    idx_inicio = n_anos - idade_final  # posição do PRIMEIRO ano da fase pastagem
    censurado = idx_inicio <= 0
    classe_antes = np.zeros(n_pix, dtype="int32")
    valid = ~censurado
    if valid.any():
        idx_antes = (idx_inicio[valid] - 1).astype("int64")
        rows_valid = np.where(valid)[0]
        classe_antes[rows_valid] = arr[rows_valid, idx_antes]

    out = pd.DataFrame({
        "ano_conversao": ano_conv,
        "idade_pastagem_anos": idade_final.astype("int16"),
        "classe_antes_id": classe_antes.astype("int32"),
        "lon": df["longitude"].astype("float64").to_numpy(),
        "lat": df["latitude"].astype("float64").to_numpy(),
    })
    out["origem_anterior"] = out["classe_antes_id"].map(ID_PARA_GRUPO).fillna(
        "censurado_esquerda"
    )
    out.loc[censurado, "origem_anterior"] = "censurado_esquerda"
    out.loc[censurado, "classe_antes_id"] = 0
    return out


def overlay_municipios(df: pd.DataFrame, gdf_muni: gpd.GeoDataFrame) -> pd.DataFrame:
    """Atribui cd_mun/nm_mun a cada pixel via sjoin geopandas (rápido, local)."""
    if df.empty:
        return df
    gdf_pix = gpd.GeoDataFrame(
        df.copy(),
        geometry=[Point(x, y) for x, y in zip(df["lon"], df["lat"])],
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(gdf_pix, gdf_muni, how="left", predicate="within")
    joined["cd_mun"] = joined["cd_mun"].fillna(0).astype("int64")
    joined["nm_mun"] = joined["nm_mun"].fillna("")
    return joined.drop(columns=["geometry", "index_right"], errors="ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline #28 — idade da pastagem na conversão")
    parser.add_argument("--teste", action="store_true",
                        help="Roda só 2020 com 200 pixels (validação rápida)")
    parser.add_argument("--n-pixels", type=int, default=N_PIXELS_POR_ANO_DEFAULT)
    parser.add_argument("--ano-min", type=int, default=1986)
    parser.add_argument("--ano-max", type=int, default=ANO_MAX)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.teste:
        anos = [2020]
        n_pixels = 200
        print("MODO TESTE: 2020, 200 pixels")
    else:
        anos = list(range(args.ano_min, args.ano_max + 1))
        n_pixels = args.n_pixels

    init_ee()
    print("Carregando municípios de Goiás (geobr)...")
    gdf_muni = carregar_municipios_gdf()
    print(f"  {len(gdf_muni)} municípios")

    meso_por_mun = carregar_mesorregioes()
    print(f"  Mesorregiões: {len(meso_por_mun)} munis mapeados")

    # Geometria GO única para o sample (mais eficiente que FeatureCollection)
    go_geom = ee.Geometry.Polygon(
        list(gdf_muni.union_all().envelope.exterior.coords),
        proj="EPSG:4326",
        geodesic=False,
    )
    img_full = ee.Image(ASSET)

    todos = []
    for i, ano in enumerate(anos, 1):
        cache_path = CACHE_DIR / f"idade_{ano}.csv"
        if cache_path.exists() and not args.force:
            df = pd.read_csv(cache_path, dtype={"cd_mun": "int64"})
            print(f"[{i:02d}/{len(anos)}] {ano} — cache ({len(df):,} pixels)")
            todos.append(df)
            continue

        print(f"[{i:02d}/{len(anos)}] {ano} — amostrando GEE...")
        t0 = time.time()
        try:
            df_bands = amostrar_ano_via_gee(ano, img_full, go_geom, n_pixels)
        except Exception as exc:
            print(f"  ERRO GEE: {exc}")
            continue
        print(f"  {len(df_bands):,} pixels recebidos do GEE ({time.time() - t0:.0f}s)")

        if df_bands.empty:
            continue

        t1 = time.time()
        df_calc = calcular_idade_e_origem(df_bands, ano)
        df_final = overlay_municipios(df_calc, gdf_muni)
        df_final["mesorregiao"] = df_final["cd_mun"].map(meso_por_mun).fillna("")

        colunas = ["ano_conversao", "cd_mun", "nm_mun", "mesorregiao",
                   "idade_pastagem_anos", "classe_antes_id", "origem_anterior",
                   "lon", "lat"]
        df_final = df_final[colunas]
        df_final.to_csv(cache_path, index=False, float_format="%.6f")
        med = df_final["idade_pastagem_anos"].median()
        cens = (df_final["origem_anterior"] == "censurado_esquerda").mean() * 100
        print(f"  {ano} — idade mediana {med:.0f}a | censurado {cens:.0f}% "
              f"(processamento local {time.time() - t1:.1f}s)")
        todos.append(df_final)

        if i < len(anos):
            time.sleep(2)

    if not todos:
        print("Nenhum dado coletado.")
        return

    resultado = pd.concat(todos, ignore_index=True)
    colunas = ["ano_conversao", "cd_mun", "nm_mun", "mesorregiao",
               "idade_pastagem_anos", "classe_antes_id", "origem_anterior",
               "lon", "lat"]
    resultado = resultado[colunas].sort_values(
        ["ano_conversao", "cd_mun", "idade_pastagem_anos"]
    )

    CSV_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(CSV_SAIDA, index=False, float_format="%.6f")

    print(f"\n{'=' * 60}")
    print(f"SAÍDA: {CSV_SAIDA}")
    print(f"  {len(resultado):,} pixels | {resultado['cd_mun'].nunique()} munis | "
          f"{resultado['ano_conversao'].nunique()} anos")
    print(f"  Idade mediana global: {resultado['idade_pastagem_anos'].median():.0f} anos")
    print(f"  Origem anterior (%):")
    print(resultado["origem_anterior"].value_counts(normalize=True).mul(100).round(1).to_string())


if __name__ == "__main__":
    main()
