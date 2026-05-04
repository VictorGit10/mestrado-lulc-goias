"""
fogo_mapbiomas.py — Área queimada por município via MapBiomas Fire Collection 4
=================================================================================

Computa área queimada (total e por classe LULC) para os 246 municípios de Goiás,
1985–2024, usando os assets de fogo do MapBiomas Collection 4 via Google Earth Engine.

Assets:
  - burned_area: projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_annual_burned_v1
    Bandas: burned_area_YYYY (binário 0/1, 30m)
  - burned_coverage: projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_annual_burned_coverage_v1
    Bandas: burned_coverage_YYYY (códigos LULC da Coleção 9, 30m)

6 classes agregadas (mesmas do Pipeline #12/transições):
    - Vegetação Natural:  3, 4, 12
    - Pastagem:          15
    - Agricultura:       9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62
    - Água:              31, 33
    - Área Urbana:       24
    - Outros:            5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75
    - EXCLUÍDO: ID 21 (Mosaico) — mantido como "Outros" no contexto de fogo
      (pixels queimados em Mosaico são contabilizados separadamente)

Saída:
  data/processed/fogo_mapbiomas_goias.csv
  Schema: cd_mun, nm_mun, ano, area_queimada_total_ha,
          area_queimada_veg_nat_ha, area_queimada_pastagem_ha,
          area_queimada_agricultura_ha, area_queimada_agua_ha,
          area_queimada_urbano_ha, area_queimada_outros_ha, area_queimada_mosaico_ha

Como rodar:
    1. earthengine authenticate  (terminal Windows real)
    2. set GEE_PROJECT=extreme-height-447417-a9
    3. python "Scripts e Catalogo/fogo_mapbiomas.py"
    4. python "Scripts e Catalogo/fogo_mapbiomas.py" --force     # reprocessa tudo
    4. python "Scripts e Catalogo/fogo_mapbiomas.py" --anos 2020 2021  # só anos específicos
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
ASSET_FOGO = ("projects/mapbiomas-public/assets/brazil/fire/collection4/"
               "mapbiomas_fire_collection4_annual_burned_v1")
ASSET_FOGO_COBERTURA = ("projects/mapbiomas-public/assets/brazil/fire/collection4/"
                         "mapbiomas_fire_collection4_annual_burned_coverage_v1")
PIXEL_HA = 0.09  # 30m × 30m = 900 m² = 0.09 ha
ANOS = list(range(1985, 2025))

CLASSES = {
    1: {"nome": "Vegetação Natural", "ids": [3, 4, 12]},
    2: {"nome": "Pastagem",          "ids": [15]},
    3: {"nome": "Agricultura",       "ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]},
    4: {"nome": "Água",              "ids": [31, 33]},
    5: {"nome": "Área Urbana",       "ids": [24]},
    6: {"nome": "Outros",            "ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75]},
}
# ID 21 (Mosaico) não remapeado — contabilizado separadamente
NOME_CLASSE = {k: v["nome"] for k, v in CLASSES.items()}

ROOT = Path(__file__).resolve().parent.parent
CSV_SAIDA = ROOT / "data" / "processed" / "fogo_mapbiomas_goias.csv"
CACHE_DIR = ROOT / "data" / "cache" / "fogo"
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
    """Mapeia IDs MapBiomas → 1..6 (6 classes). ID 21 fica de fora (será classe 7)."""
    from_ids, to_ids = [], []
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
    # Mosaico → classe 7 (contabilizado separadamente)
    from_ids.append(21)
    to_ids.append(7)
    return from_ids, to_ids


def carregar_municipios_go() -> tuple[ee.FeatureCollection, pd.DataFrame]:
    """Lê 246 municípios via geobr e converte para ee.FeatureCollection."""
    gdf = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    features = []
    for _, row in gdf.iterrows():
        geom = ee.Geometry(row["geometry"].__geo_interface__)
        feat = ee.Feature(geom, {
            "cd_mun": int(row["code_muni"]),
            "nm_mun": str(row["name_muni"]),
        })
        features.append(feat)
    fc = ee.FeatureCollection(features)
    df = gdf[["code_muni", "name_muni"]].rename(columns={
        "code_muni": "cd_mun", "name_muni": "nm_mun"
    })
    df["cd_mun"] = df["cd_mun"].astype("int64")
    return fc, df


def calcular_fogo_anual(
    ano: int,
    img_burned: ee.Image,
    img_coverage: ee.Image,
    municipios_fc: ee.FeatureCollection,
    from_ids: list[int],
    to_ids: list[int],
    scale: int = 30,
) -> pd.DataFrame:
    """Computa área queimada (total e por classe) para um ano sobre todos os municípios.

    Usa dois reduceRegions: (1) soma de pixels queimados, (2) histograma de classes
    nos pixels queimados. Retorna DataFrame com colunas de área em hectares.
    """
    # 1) Área queimada total — banda binária
    band_burned = img_burned.select(f"burned_area_{ano}")
    burned_stats = band_burned.reduceRegions(
        collection=municipios_fc,
        reducer=ee.Reducer.sum(),
        scale=scale,
    )

    # 2) Área queimada por classe — banda de cobertura com códigos LULC
    band_cov = img_coverage.select(f"burned_coverage_{ano}")
    band_remaped = band_cov.remap(from_ids, to_ids, defaultValue=0)
    # Mascarar para apenas pixels queimados
    burned_mask = band_burned.eq(1)
    masked_cov = band_remaped.updateMask(burned_mask)

    cov_stats = masked_cov.reduceRegions(
        collection=municipios_fc,
        reducer=ee.Reducer.frequencyHistogram(),
        scale=scale,
    )

    # Extrair dados
    burned_info = burned_stats.getInfo()
    cov_info = cov_stats.getInfo()

    # Parsear resultados
    rows = []
    for feat_b, feat_c in zip(burned_info["features"], cov_info["features"]):
        cd_mun = feat_b["properties"]["cd_mun"]
        nm_mun = feat_b["properties"]["nm_mun"]

        # Total queimado (soma de pixels × PIXEL_HA)
        total_key = f"burned_area_{ano}_sum"
        total_pixels = feat_b["properties"].get(total_key, 0) or 0
        total_ha = total_pixels * PIXEL_HA

        # Histograma de classes
        hist = feat_c["properties"].get(f"burned_coverage_{ano}", {})
        class_ha = {}
        if isinstance(hist, dict):
            for k, v in hist.items():
                class_ha[int(k)] = v * PIXEL_HA

        row = {
            "cd_mun": cd_mun,
            "nm_mun": nm_mun,
            "ano": ano,
            "area_queimada_total_ha": round(total_ha, 2),
            "area_queimada_veg_nat_ha": round(class_ha.get(1, 0), 2),
            "area_queimada_pastagem_ha": round(class_ha.get(2, 0), 2),
            "area_queimada_agricultura_ha": round(class_ha.get(3, 0), 2),
            "area_queimada_agua_ha": round(class_ha.get(4, 0), 2),
            "area_queimada_urbano_ha": round(class_ha.get(5, 0), 2),
            "area_queimada_outros_ha": round(class_ha.get(6, 0), 2),
            "area_queimada_mosaico_ha": round(class_ha.get(7, 0), 2),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def processar_ano(
    ano: int,
    img_burned: ee.Image,
    img_coverage: ee.Image,
    municipios_fc: ee.FeatureCollection,
    from_ids: list[int],
    to_ids: list[int],
    force: bool = False,
) -> pd.DataFrame:
    """Processa um ano com cache em CSV."""
    cache_path = CACHE_DIR / f"fogo_{ano}.csv"
    if cache_path.exists() and not force:
        df = pd.read_csv(cache_path)
        print(f"  [cache] fogo_{ano}.csv ({len(df)} munis)")
        return df

    print(f"  [...] processando ano {ano} ...")
    t0 = time.time()

    for attempt, scale in enumerate([30, 60, 100]):
        try:
            df = calcular_fogo_anual(ano, img_burned, img_coverage, municipios_fc,
                                      from_ids, to_ids, scale=scale)
            df.to_csv(cache_path, index=False)
            dt = time.time() - t0
            total = df["area_queimada_total_ha"].sum()
            tag = f"scale={scale}" if scale > 30 else ""
            print(f"  [OK] fogo_{ano}.csv ({len(df)} munis, {total:,.0f} ha, {dt:.0f}s {tag})")
            return df
        except Exception as exc:
            if attempt < 2:
                print(f"  [retry] ano {ano} (scale={scale}): {exc} — tentando scale={[60,100][attempt]}")
                time.sleep(5)
            else:
                print(f"  [ERRO] ano {ano} após 3 tentativas: {exc}")
                raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Ignora cache e reprocessa todos os anos")
    parser.add_argument("--anos", nargs="+", type=int, default=None,
                        help="Processar só estes anos (ex: --anos 2020 2021 2022)")
    args = parser.parse_args()

    anos = args.anos if args.anos else ANOS

    print("=" * 70)
    print("Fogo MapBiomas — Área queimada por município de Goiás")
    print(f"  Anos: {anos[0]}–{anos[-1]} ({len(anos)} anos)")
    print(f"  Cache: {'OFF (--force)' if args.force else 'ON'}")
    print(f"  Saída: {CSV_SAIDA}")
    print("=" * 70)

    init_ee()

    # Carregar assets e municípios
    img_burned = ee.Image(ASSET_FOGO)
    img_coverage = ee.Image(ASSET_FOGO_COBERTURA)
    from_ids, to_ids = construir_remap()
    municipios_fc, df_munis = carregar_municipios_go()
    print(f"  Municípios carregados: {len(df_munis)}")

    # Processar cada ano
    dfs = []
    for ano in anos:
        try:
            df_ano = processar_ano(ano, img_burned, img_coverage, municipios_fc,
                                   from_ids, to_ids, force=args.force)
            dfs.append(df_ano)
            time.sleep(2)  # Cortesia para a API GEE
        except Exception as exc:
            print(f"  [ERRO FATAL] ano {ano}: {exc}")
            # Salvar o que já foi processado e continuar
            continue

    if not dfs:
        print("Nenhum ano processado com sucesso. Encerrando.")
        sys.exit(1)

    # Consolidar
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    df.to_csv(CSV_SAIDA, index=False)

    print(f"\n{'='*70}")
    print(f"RESUMO")
    print(f"{'='*70}")
    print(f"  Arquivo: {CSV_SAIDA}")
    print(f"  Linhas: {len(df):,}")
    print(f"  Municípios: {df['cd_mun'].nunique()}")
    print(f"  Anos: {sorted(df['ano'].unique())}")
    print(f"  Área queimada total GO (todos os anos): {df['area_queimada_total_ha'].sum():,.0f} ha")
    print(f"  Média anual: {df.groupby('ano')['area_queimada_total_ha'].sum().mean():,.0f} ha/ano")


if __name__ == "__main__":
    main()