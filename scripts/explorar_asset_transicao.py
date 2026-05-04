"""explorar_asset_transicao.py — Inspeção do asset de transição MapBiomas
e teste da Abordagem B (computar transições a partir do asset de cobertura).

Este script é temporário (Fase 1 do Pipeline #12). Ele:
1. Inicializa GEE
2. Carrega o asset de transição e imprime bandNames, metadados, codificação
3. Amostra pixels em Goiás para entender a codificação
4. Testa a Abordagem B para 1985→2000 em 1 município e compara com Pipeline #4

Como rodar:
    set GEE_PROJECT=extreme-height-447417-a9
    python "Scripts e Catalogo/explorar_asset_transicao.py"
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import geobr

# ===== Configuração =====
GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET_COBERTURA = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
ASSET_TRANSICAO = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_transition_v1"
PIXEL_HA = 0.09  # 30m × 30m = 900 m² = 0.09 ha

CLASSES = {
    1: {"nome": "Vegetação Natural", "ids": [3, 4, 12],                          "cor": "#1B8A2F"},
    2: {"nome": "Pastagem",          "ids": [15],                                 "cor": "#FFD700"},
    3: {"nome": "Agricultura",       "ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62], "cor": "#FF69B4"},
    4: {"nome": "Água",              "ids": [31, 33],                              "cor": "#4169E1"},
    5: {"nome": "Área Urbana",       "ids": [24],                                  "cor": "#A0A0A0"},
    6: {"nome": "Outros",            "ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],  "cor": "#D2B48C"},
}
ID_PARA_CLASSE = {cid: idx for idx, info in CLASSES.items() for cid in info["ids"]}


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    if not project:
        sys.exit("Erro: defina GEE_PROJECT.")
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception as exc:
        print("Falha ao inicializar Earth Engine.")
        print("Rode no terminal:  earthengine authenticate")
        raise


def construir_remap() -> tuple[list[int], list[int]]:
    """Mapeia IDs MapBiomas → 1..6 (6 classes agregadas). IDs não listados → 0."""
    from_ids: list[int] = []
    to_ids: list[int] = []
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
    return from_ids, to_ids


def carregar_geometria_go():
    gdf = geobr.read_state(code_state="GO", year=2020).to_crs(4326)
    geom_geojson = gdf.iloc[0].geometry.__geo_interface__
    return ee.Geometry(geom_geojson), gdf


def carregar_municipios_go():
    gdf = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    print(f"  Colunas do geobr: {list(gdf.columns)}")
    print(f"  Primeiros codigos: {gdf['code_muni'].head(3).tolist()}")
    features = []
    for _, row in gdf.iterrows():
        geom = ee.Geometry(row["geometry"].__geo_interface__)
        feat = ee.Feature(geom, {
            "cd_mun": int(row["code_muni"]),
            "nm_mun": str(row.get("name_muni", row.get("name_municipality", ""))),
        })
        features.append(feat)
    return ee.FeatureCollection(features), gdf


# ──────────────────────────────────────────────────────────────
# Parte 1: Inspecionar asset de transição
# ──────────────────────────────────────────────────────────────
def inspecionar_asset_transicao(geom_go):
    print("\n" + "=" * 60)
    print("PARTE 1: Inspeção do asset de transição")
    print("=" * 60)

    try:
        img = ee.Image(ASSET_TRANSICAO)
        info = img.getInfo()
        band_names = [b["id"] for b in info["bands"]]
        print(f"\nNúmero de bandas: {len(band_names)}")
        print(f"Primeiras 20 bandas: {band_names[:20]}")
        if len(band_names) > 20:
            print(f"Últimas 10 bandas: {band_names[-10:]}")

        # Metadados das propriedades
        props = info.get("properties", {})
        if props:
            print(f"\nPropriedades: {props}")

        # Tipo de dados e valores
        for b in info["bands"][:3]:
            print(f"\n  Banda '{b['id']}': dtype={b.get('data_type', '?')}, "
                  f"crs={b.get('crs', '?')}, dimensions={b.get('dimensions', '?')}")

        # Amostrar pixels em Goiás
        sample_bands = band_names[:3]
        print(f"\nAmostrando 5 pixels em Goiás das bandas: {sample_bands}")
        sample = img.select(sample_bands).sample(
            region=geom_go, scale=30, numPixels=5, seed=42
        ).getInfo()

        for i, feat in enumerate(sample.get("features", [])[:5]):
            vals = feat.get("properties", {})
            print(f"  Pixel {i+1}: {vals}")

    except Exception as exc:
        print(f"Erro ao inspecionar asset de transição: {exc}")
        print("  → Asset pode não existir com este path. Continuando com Abordagem B.")


# ──────────────────────────────────────────────────────────────
# Parte 2: Testar Abordagem B (computar a partir da cobertura)
# ──────────────────────────────────────────────────────────────
def testar_abordagem_b(geom_go, municipios_fc, gdf_munis):
    print("\n" + "=" * 60)
    print("PARTE 2: Teste da Abordagem B — 1985→2000 em Goiânia")
    print("=" * 60)

    from_ids, to_ids = construir_remap()

    # Encontrar Goiânia no FeatureCollection
    goiania_code = 520870
    goiania_fc = municipios_fc.filter(ee.Filter.eq("cd_mun", goiania_code))
    goiania_count = goiania_fc.size().getInfo()
    print(f"\nGoiânia (código {goiania_code}) encontrada: {goiania_count} feature(s)")

    if goiania_count == 0:
        # Tentar com o primeiro município
        print("Goiânia não encontrada. Usando primeiro município.")
        goiania_fc = municipios_fc.limit(1)
        feat = goiania_fc.first().getInfo()
        print(f"  Usando: cd_mun={feat['properties'].get('cd_mun')}, "
              f"nm_mun={feat['properties'].get('nm_mun')}")

    # Carregar bandas de cobertura
    img_full = ee.Image(ASSET_COBERTURA)
    band_orig = img_full.select("classification_1985")
    band_dest = img_full.select("classification_2000")

    # Remap para 6 classes
    remap_orig = band_orig.remap(from_ids, to_ids, defaultValue=0)
    remap_dest = band_dest.remap(from_ids, to_ids, defaultValue=0)

    # Máscara: ambos os anos têm classe válida
    mask = remap_orig.gt(0).And(remap_dest.gt(0))

    # Código de transição: origem * 10 + destino
    transition_code = remap_orig.multiply(10).add(remap_dest).toInt()
    transition_code = transition_code.updateMask(mask).clip(geom_go)

    # reduceRegions no município
    print("\nCalculando reduceRegions para 1985→2000...")
    t0 = time.time()
    stats = transition_code.reduceRegions(
        collection=goiania_fc,
        reducer=ee.Reducer.frequencyHistogram(),
        scale=30,
        crs="EPSG:5880",
    ).getInfo()
    elapsed = time.time() - t0
    print(f"Tempo: {elapsed:.1f}s")

    # Parse do histograma
    for feat in stats.get("features", []):
        props = feat.get("properties", {})
        cd_mun = props.get("cd_mun")
        nm_mun = props.get("nm_mun")
        histogram = props.get("histogram", {})
        print(f"\nMunicípio: {nm_mun} (cd_mun={cd_mun})")
        print(f"Histograma bruto: {histogram}")

        # Decodificar
        total_ha = 0
        print("\nDecodificação:")
        for code_str, count in sorted(histogram.items()):
            code = int(float(code_str))
            orig = code // 10
            dest = code % 10
            area_ha = count * PIXEL_HA
            total_ha += area_ha
            nome_orig = CLASSES.get(orig, {}).get("nome", f"?{orig}")
            nome_dest = CLASSES.get(dest, {}).get("nome", f"?{dest}")
            print(f"  {code:2d} → {nome_orig:20s} → {nome_dest:20s}: "
                  f"{count:>10,} pixels = {area_ha:>12,.1f} ha")
        print(f"\n  Total (classes válidas): {total_ha:,.1f} ha")

    # ── Teste com TODOS os municípios ──
    print("\n" + "-" * 40)
    print("Teste com TODOS os 246 municípios (1985→2000)...")
    t0 = time.time()
    stats_all = transition_code.reduceRegions(
        collection=municipios_fc,
        reducer=ee.Reducer.frequencyHistogram(),
        scale=30,
        crs="EPSG:5880",
    ).getInfo()
    elapsed = time.time() - t0
    n_munis = len(stats_all.get("features", []))
    print(f"Tempo: {elapsed:.1f}s | Municípios retornados: {n_munis}")

    # Resumo por classe de destino (soma estadual)
    dest_totals: dict[int, float] = {}
    for feat in stats_all.get("features", []):
        histogram = feat.get("properties", {}).get("histogram", {})
        for code_str, count in histogram.items():
            code = int(float(code_str))
            dest = code % 10
            dest_totals[dest] = dest_totals.get(dest, 0) + count * PIXEL_HA

    print("\nSoma estadual por classe de destino (1985→2000):")
    for dest in sorted(dest_totals):
        print(f"  {CLASSES.get(dest, {}).get('nome', f'?{dest}'):20s}: "
              f"{dest_totals[dest]:>12,.1f} ha")


# ──────────────────────────────────────────────────────────────
# Parte 3: Comparação batimental com Pipeline #4
# ──────────────────────────────────────────────────────────────
def comparar_com_pipeline4(stats_all):
    print("\n" + "=" * 60)
    print("PARTE 3: Comparação batimental com Pipeline #4")
    print("=" * 60)

    csv_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "mapbiomas_munis_goias.csv"
    if not csv_path.exists():
        print(f"CSV do Pipeline #4 não encontrado: {csv_path}")
        return

    import pandas as pd
    df4 = pd.read_csv(csv_path, dtype={"cd_mun": "int64"})

    # Agregar classes do Pipeline #4 para as 6 classes agregadas
    id_para_agregada = {}
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            id_para_agregada[cid] = idx

    df4["classe_agg"] = df4["class_id"].map(id_para_agregada)
    df4_valid = df4.dropna(subset=["classe_agg"])

    # Soma por (cd_mun, classe_agg) para ano 2000
    soma_2000 = (df4_valid[df4_valid["ano"] == 2000]
                 .groupby(["cd_mun", "classe_agg"])["area_ha"]
                 .sum().reset_index())

    # Soma por (cd_mun, classe_destino) do GEE
    gee_data = []
    for feat in stats_all.get("features", []):
        props = feat.get("properties", {})
        cd_mun = int(props.get("cd_mun", 0))
        histogram = props.get("histogram", {})
        for code_str, count in histogram.items():
            code = int(float(code_str))
            dest = code % 10
            gee_data.append({
                "cd_mun": cd_mun,
                "classe_agg": dest,
                "area_ha_gee": count * PIXEL_HA,
            })

    import pandas as pd
    df_gee = pd.DataFrame(gee_data)
    if df_gee.empty:
        print("Nenhum dado GEE para comparar.")
        return

    gee_agg = df_gee.groupby(["cd_mun", "classe_agg"])["area_ha_gee"].sum().reset_index()

    # Merge
    comp = soma_2000.merge(gee_agg, on=["cd_mun", "classe_agg"], how="outer")
    comp = comp.fillna(0)
    comp["delta_pct"] = ((comp["area_ha_gee"] - comp["area_ha"]) / comp["area_ha"].replace(0, 1) * 100)

    print(f"\nMunicipios comparados: {comp['cd_mun'].nunique()}")
    print(f"Delta % médio: {comp['delta_pct'].mean():.1f}%")
    print(f"Delta % máximo (abs): {comp['delta_pct'].abs().max():.1f}%")
    print(f"Delta % mediano: {comp['delta_pct'].median():.1f}%")

    # Top 5 maiores diferenças
    top5 = comp.nlargest(5, "delta_pct")
    print("\nTop 5 maiores diferenças positivas (GEE > Pipeline #4):")
    for _, row in top5.iterrows():
        print(f"  cd_mun={int(row['cd_mun'])} classe={int(row['classe_agg'])} "
              f"→ P4={row['area_ha']:.0f} ha, GEE={row['area_ha_gee']:.0f} ha, "
              f"delta={row['delta_pct']:.1f}%")

    # Soma estadual
    estado = comp.groupby("classe_agg")[["area_ha", "area_ha_gee"]].sum()
    estado["delta_pct"] = ((estado["area_ha_gee"] - estado["area_ha"]) /
                           estado["area_ha"].replace(0, 1) * 100)
    print("\nComparação estadual por classe (ano 2000):")
    for classe, row in estado.iterrows():
        nome = CLASSES.get(int(classe), {}).get("nome", f"?{classe}")
        print(f"  {nome:20s}: P4={row['area_ha']:>12,.0f} ha, "
              f"GEE={row['area_ha_gee']:>12,.0f} ha, delta={row['delta_pct']:.1f}%")


def main():
    init_ee()
    geom_go, gdf_go = carregar_geometria_go()

    # Parte 1: Inspeção do asset de transição
    inspecionar_asset_transicao(geom_go)

    # Parte 2: Teste da Abordagem B
    print("\nCarregando municípios de Goiás...")
    municipios_fc, gdf_munis = carregar_municipios_go()
    print(f"  {gdf_munis.shape[0]} municípios carregados")

    testar_abordagem_b(geom_go, municipios_fc, gdf_munis)

    # Parte 3: Comparação com Pipeline #4 (usa o resultado de TODOS os municípios)
    print("\nRecalculando para TODOS os municípios para comparação batimental...")
    from_ids, to_ids = construir_remap()
    img_full = ee.Image(ASSET_COBERTURA)
    band_orig = img_full.select("classification_1985")
    band_dest = img_full.select("classification_2000")
    remap_orig = band_orig.remap(from_ids, to_ids, defaultValue=0)
    remap_dest = band_dest.remap(from_ids, to_ids, defaultValue=0)
    mask = remap_orig.gt(0).And(remap_dest.gt(0))
    transition_code = remap_orig.multiply(10).add(remap_dest).toInt()
    transition_code = transition_code.updateMask(mask).clip(geom_go)

    t0 = time.time()
    stats_all = transition_code.reduceRegions(
        collection=municipios_fc,
        reducer=ee.Reducer.frequencyHistogram(),
        scale=30,
        crs="EPSG:5880",
    ).getInfo()
    print(f"Tempo reduceRegions (246 munis): {time.time() - t0:.1f}s")

    comparar_com_pipeline4(stats_all)

    print("\n" + "=" * 60)
    print("EXPLORAÇÃO CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()