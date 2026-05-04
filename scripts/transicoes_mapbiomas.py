"""transicoes_mapbiomas.py — Matrizes de transição pixel-a-pixel
para os 246 municípios de Goiás via Google Earth Engine.

Computa transições A→B (classe-origem × classe-destino) a partir do
asset de cobertura MapBiomas Coleção 10.1, para pares de anos configuráveis.

6 classes agregadas (mesmas do Pipeline #10):
    - Vegetação Natural:  Formação Florestal(3), Savânica(4), Campestre(12)
    - Pastagem:           Pastagem(15)
    - Agricultura:        Silvicultura(9), Lavoura Temporária(19), Cana(20),
                          Dendê(35), Lavoura Perene(36), Soja(39), Arroz(40),
                          Outras Lavouras Temp(41), Café(46), Citros(47),
                          Outras Lavouras Per(48), Algodão(62)
    - Água:               Aquicultura(31), Rio/Lago/Oceano(33)
    - Área Urbana:        Área Urbanizada(24)
    - Outros:             Manguezal(5), Floresta Inundável(6), Área Úmida(11),
                          Praia/Duna/Areia(23), Outras Áreas Não Veg(25),
                          Não Observado(27), Afloramento Rochoso(29), Mineração(30),
                          Apicum(32), Restingas(49,50), Usina Fotovoltaica(75)
    - EXCLUÍDO: ID 21 (Mosaico de Agricultura ou Pastagem) — no Cerrado
      goiano, maioria é pastagem, não agricultura.

Como rodar:
    1. earthengine authenticate  (terminal Windows real)
    2. set GEE_PROJECT=extreme-height-447417-a9
    3. python "Scripts e Catalogo/transicoes_mapbiomas.py"
    4. (opcional) python "Scripts e Catalogo/transicoes_mapbiomas.py" --consecutivos

Pré-requisitos:
    pip install earthengine-api geopandas geobr pandas

Saída:
    data/processed/transicoes_mapbiomas_goias.csv
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
PIXEL_HA = 0.09  # 30m × 30m = 900 m² = 0.09 ha

CLASSES = {
    1: {"nome": "Vegetação Natural", "ids": [3, 4, 12],                          "cor": "#1B8A2F"},
    2: {"nome": "Pastagem",          "ids": [15],                                 "cor": "#FFD700"},
    3: {"nome": "Agricultura",       "ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62], "cor": "#FF69B4"},
    4: {"nome": "Água",              "ids": [31, 33],                              "cor": "#4169E1"},
    5: {"nome": "Área Urbana",       "ids": [24],                                  "cor": "#A0A0A0"},
    6: {"nome": "Outros",            "ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],  "cor": "#D2B48C"},
}
NOME_CLASSE = {k: v["nome"] for k, v in CLASSES.items()}

# Períodos padrão (Nível 1 + Nível 2)
PERIODOS_DEFAULT = [
    (1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024),
    (1985, 2000), (2000, 2010), (2010, 2024),
    (1985, 2010), (1985, 2024),
]

ROOT = Path(__file__).resolve().parent.parent
CSV_SAIDA = ROOT / "data" / "processed" / "transicoes_mapbiomas_goias.csv"
CACHE_DIR = ROOT / "data" / "cache" / "transicoes"
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
    """Mapeia IDs MapBiomas → 1..6 (6 classes). IDs não listados → 0 (mascarados)."""
    from_ids, to_ids = [], []
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            from_ids.append(cid)
            to_ids.append(idx)
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


def calcular_transicao_par(
    ano_orig: int,
    ano_dest: int,
    img_full: ee.Image,
    municipios_fc: ee.FeatureCollection,
    from_ids: list[int],
    to_ids: list[int],
) -> pd.DataFrame:
    """Computa matriz de transição para um par de anos sobre todos os municípios.

    Retorna DataFrame com colunas: cd_mun, nm_mun, classe_orig, classe_dest, area_ha
    """
    band_orig = img_full.select(f"classification_{ano_orig}")
    band_dest = img_full.select(f"classification_{ano_dest}")

    remap_orig = band_orig.remap(from_ids, to_ids, defaultValue=0)
    remap_dest = band_dest.remap(from_ids, to_ids, defaultValue=0)

    mask = remap_orig.gt(0).And(remap_dest.gt(0))
    transition_code = remap_orig.multiply(10).add(remap_dest).toInt()
    transition_code = transition_code.updateMask(mask)

    # Tentar com scale=30; se falhar, aumentar
    for scale in [30, 60, 100]:
        try:
            stats = transition_code.reduceRegions(
                collection=municipios_fc,
                reducer=ee.Reducer.frequencyHistogram(),
                scale=scale,
                crs="EPSG:5880",
            ).getInfo()
            if scale > 30:
                print(f"    (usou scale={scale} como fallback)")
            break
        except Exception as exc:
            print(f"    reduceRegions falhou (scale={scale}): {exc}")
            if scale == 100:
                raise
            time.sleep(10)

    rows = []
    for feat in stats.get("features", []):
        props = feat.get("properties", {})
        cd_mun = int(props.get("cd_mun", 0))
        nm_mun = str(props.get("nm_mun", ""))
        histogram = props.get("histogram", {})

        for code_str, count in histogram.items():
            code = int(float(code_str))
            orig = code // 10
            dest = code % 10
            rows.append({
                "cd_mun": cd_mun,
                "nm_mun": nm_mun,
                "classe_orig": orig,
                "classe_dest": dest,
                "area_ha": count * PIXEL_HA,
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["classe_orig_nome"] = df["classe_orig"].map(NOME_CLASSE)
        df["classe_dest_nome"] = df["classe_dest"].map(NOME_CLASSE)
    return df


def validar_batimental(df_trans: pd.DataFrame, ano_orig: int, ano_dest: int) -> None:
    """Compara totais por classe-destino com Pipeline #4 para um par específico."""
    csv_p4 = ROOT / "data" / "processed" / "mapbiomas_munis_goias.csv"
    if not csv_p4.exists():
        print(f"  [validação] CSV Pipeline #4 não encontrado, pulando.")
        return

    df4 = pd.read_csv(csv_p4, dtype={"cd_mun": "int64"})
    id_para_agg = {}
    for idx, info in CLASSES.items():
        for cid in info["ids"]:
            id_para_agg[cid] = idx
    df4["classe_agg"] = df4["class_id"].map(id_para_agg)
    df4_valid = df4.dropna(subset=["classe_agg"])

    soma_p4 = (df4_valid[df4_valid["ano"] == ano_dest]
               .groupby("classe_agg")["area_ha"].sum())

    mask = (df_trans["ano_origem"] == ano_orig) & (df_trans["ano_destino"] == ano_dest)
    soma_gee = (df_trans[mask]
                .groupby("classe_dest")["area_ha"].sum())

    print(f"  Validação batimental ({ano_orig}→{ano_dest}):")
    for classe in sorted(set(soma_p4.index) | set(soma_gee.index)):
        v_p4 = soma_p4.get(classe, 0)
        v_gee = soma_gee.get(classe, 0)
        delta = ((v_gee - v_p4) / v_p4 * 100) if v_p4 > 0 else float("inf")
        nome = NOME_CLASSE.get(int(classe), "?")
        print(f"    {nome:20s}: P4={v_p4:>12,.0f} ha  GEE={v_gee:>12,.0f} ha  δ={delta:+.1f}%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Matrizes de transição MapBiomas via GEE")
    parser.add_argument("--consecutivos", action="store_true",
                        help="Adiciona 39 pares ano-a-ano (1985-1986, ..., 2023-2024)")
    parser.add_argument("--periodos", type=str, default=None,
                        help="Pares customizados, ex: '1985,2000 2000,2010'")
    parser.add_argument("--force", action="store_true",
                        help="Recalcula mesmo se CSV já existe")
    args = parser.parse_args()

    if args.periodos:
        periodos = []
        for par in args.periodos.split():
            a, b = par.split(",")
            periodos.append((int(a), int(b)))
    else:
        periodos = list(PERIODOS_DEFAULT)

    if args.consecutivos:
        for a in range(1985, 2024):
            periodos.append((a, a + 1))

    init_ee()

    # Carregar dados de referência
    from_ids, to_ids = construir_remap()
    print(f"Remap: {len(from_ids)} IDs → 6 classes")

    print("Carregando municípios de Goiás...")
    municipios_fc, df_munis = carregar_municipios_go()
    print(f"  {len(df_munis)} municípios")

    img_full = ee.Image(ASSET)

    # Processar cada par de período
    all_dfs = []
    n = len(periodos)
    for i, (ano_orig, ano_dest) in enumerate(periodos, 1):
        label = f"{ano_orig}→{ano_dest}"

        # Cache por par
        cache_path = CACHE_DIR / f"transicao_{ano_orig}_{ano_dest}.csv"
        if cache_path.exists() and not args.force:
            print(f"[{i:02d}/{n}] {label} — cache encontrado, pulando")
            df = pd.read_csv(cache_path)
            df["ano_origem"] = ano_orig
            df["ano_destino"] = ano_dest
            all_dfs.append(df)
            continue

        print(f"[{i:02d}/{n}] {label} — calculando...")
        t0 = time.time()
        df = calcular_transicao_par(ano_orig, ano_dest, img_full, municipios_fc, from_ids, to_ids)
        elapsed = time.time() - t0

        if df.empty:
            print(f"  {label} — sem dados, pulando")
            continue

        df["ano_origem"] = ano_orig
        df["ano_destino"] = ano_dest

        # Salvar cache
        df.to_csv(cache_path, index=False, float_format="%.4f")

        n_transicoes = len(df)
        n_munis = df["cd_mun"].nunique()
        print(f"  {label} — {n_transicoes:,} transições, {n_munis} munis ({elapsed:.0f}s)")

        all_dfs.append(df)

        # Pausa para não sobrecarregar o GEE
        if i < n:
            time.sleep(5)

    if not all_dfs:
        print("Nenhum dado processado.")
        return

    # Consolidar
    resultado = pd.concat(all_dfs, ignore_index=True)

    # Reordenar colunas
    colunas = ["cd_mun", "nm_mun", "ano_origem", "ano_destino",
               "classe_orig", "classe_dest", "classe_orig_nome", "classe_dest_nome",
               "area_ha"]
    resultado = resultado[colunas]
    resultado = resultado.sort_values(["ano_origem", "ano_destino", "cd_mun", "classe_orig", "classe_dest"])
    resultado.to_csv(CSV_SAIDA, index=False, float_format="%.4f")

    print(f"\n{'=' * 60}")
    print(f"SAÍDA: {CSV_SAIDA}")
    print(f"  {len(resultado):,} linhas | {resultado['cd_mun'].nunique()} municípios | "
          f"{resultado.groupby(['ano_origem','ano_destino']).ngroups} pares de período")

    # Validação batimental para os períodos Nível 1
    for ao, ad in PERIODOS_DEFAULT[:4]:
        validar_batimental(resultado, ao, ad)

    # Resumo estadual por par de período
    print(f"\nResumo estadual (top 5 transições por período):")
    for (a_o, a_d) in periodos[:5]:
        subset = resultado[(resultado["ano_origem"] == a_o) & (resultado["ano_destino"] == a_d)]
        top5 = subset.groupby(["classe_orig_nome", "classe_dest_nome"])["area_ha"].sum().nlargest(5)
        print(f"\n  {a_o}→{a_d}:")
        for (co, cd), ha in top5.items():
            print(f"    {co:20s} → {cd:20s}: {ha:>12,.0f} ha")

    print(f"\nConcluído.")


if __name__ == "__main__":
    main()