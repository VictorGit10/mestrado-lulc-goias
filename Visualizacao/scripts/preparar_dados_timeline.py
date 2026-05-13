"""Agrega painel municipal em series anuais UF (Goias) para a timeline.

Le data/processed/painel_unificado.parquet (246 munis x 40 anos x 70 cols),
soma areas LULC, totaliza socioeconomicos e exporta JSONs enxutos para o
front-end consumir. Tambem produz:
  - transicoes_resumo.json  (2 snapshots: inicio e fim da serie)
  - fogo_goias.json         (serie UF de fogo por classe)
  - painel_municipal_indice.json (lookup leve: 246 municipios)
  - municipios/{cd_mun}.json x 246 (serie municipal compacta)
  - transicoes_matriz.json  (5 matrizes 6x6 por periodo)
  - sankey_data.json        (nodos + links para d3-sankey 1985->2024)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
TRANSICOES_CSV = ROOT / "data" / "processed" / "transicoes_mapbiomas_goias.csv"
OUT_DIR = ROOT / "Visualizacao" / "assets" / "data"
MUNI_DIR = OUT_DIR / "municipios"

LULC_NATIVO = [
    "lulc_floresta_nativa_ha",
    "lulc_formacao_savanica_ha",
    "lulc_campo_alagado_ha",
    "lulc_campo_nativo_ha",
]
LULC_CLASSES = LULC_NATIVO + [
    "lulc_pastagem_ha",
    "lulc_soja_ha",
    "lulc_agricultura_ha",
    "lulc_mosaico_usos_ha",
    "lulc_silvicultura_ha",
    "lulc_area_urbana_ha",
    "lulc_mineracao_ha",
    "lulc_corpo_dagua_ha",
]
SOMAR = LULC_CLASSES + [
    "lulc_area_total_ha",
    "pec_bovinos_cab",
    "pec_bovinos_ua",
    "pec_suinos_cab",
    "pec_galinaceos_cab",
    "pec_ovinos_tosquiados_cab",
    "agri_soja_ha_plantada",
    "agri_soja_ton",
    "agri_milho1_ha_plantada",
    "agri_milho2_ha_plantada",
    "agri_milho_total_ha_plantada",
    "agri_milho_total_ton",
    "agri_cana_ha_plantada",
    "agri_cana_ton",
    "agri_algodao_ha_plantada",
    "agri_algodao_ton",
    "agri_mandioca_ha_plantada",
    "agri_mandioca_ton",
    "agri_arroz_ha_plantada",
    "agri_arroz_ton",
    "agri_sorgo_ha_plantada",
    "agri_sorgo_ton",
    "agri_feijao_ha_plantada",
    "agri_feijao_ton",
    "agri_leite_mil_litros",
    "perm_cafe_total_ha_destinada",
    "perm_cafe_total_ton",
    "perm_banana_ha_destinada",
    "perm_banana_ton",
    "perm_laranja_ha_destinada",
    "perm_laranja_ton",
    "perm_manga_ha_destinada",
    "perm_manga_ton",
    "perm_mamao_ha_destinada",
    "perm_mamao_ton",
    "perm_maracuja_ha_destinada",
    "perm_maracuja_ton",
    "perm_uva_ha_destinada",
    "perm_uva_ton",
    "pib_real_rs",
    "va_agro_real_rs",
    "populacao",
    "sicor_total_real_rs",
    "fogo_total_ha",
]

FOGO_SOMAR = [
    "fogo_total_ha",
    "fogo_veg_nat_ha",
    "fogo_pastagem_ha",
    "fogo_agricultura_ha",
    "fogo_mosaico_ha",
    "fogo_outros_ha",
]

# Colunas para a serie municipal compacta
MUNI_COLS_SERIE = [
    "lulc_area_total_ha",
    "lulc_vegetacao_nativa_ha",
    "lulc_pastagem_ha",
    "lulc_soja_ha",
    "lulc_agricultura_ha",
    "lulc_mosaico_usos_ha",
    "lulc_corpo_dagua_ha",
    "lulc_area_urbana_ha",
    "pec_bovinos_cab",
    "pec_bovinos_ua",
    "pec_suinos_cab",
    "pec_galinaceos_cab",
    "pec_ovinos_tosquiados_cab",
    "agri_soja_ton",
    "agri_milho_total_ton",
    "agri_cana_ton",
    "agri_algodao_ton",
    "agri_mandioca_ton",
    "agri_arroz_ton",
    "agri_sorgo_ton",
    "agri_feijao_ton",
    "agri_leite_mil_litros",
    "perm_cafe_total_ton",
    "perm_banana_ton",
    "perm_laranja_ton",
    "perm_manga_ton",
    "perm_mamao_ton",
    "perm_maracuja_ton",
    "perm_uva_ton",
    "pib_real_rs",
    "populacao",
    "sicor_total_real_rs",
    "fogo_total_ha",
    "lotacao_bov_ha_pasto",
    "lotacao_ua_ha_pasto",
]

MUNI_COLS_PCT = [
    "pct_pastagem_lulc",
    "pct_agricultura_lulc",
    "pct_natural_lulc",
]

# Periodos das transicoes (5 periodos para o Atlas)
PERIODOS_TRANSICAO = [
    (1985, 1995),
    (1995, 2005),
    (2005, 2015),
    (2015, 2024),
    (1985, 2024),
]

# Classes LULC para o Sankey (6 classes agregadas, alinhadas com o mapa GEE)
CLASSES_SANKEY = {
    1: "Vegetacao Natural",
    2: "Pastagem",
    3: "Agricultura",
    4: "Agua",
    5: "Area Urbana",
    6: "Outros",
}

CORES_SANKEY = {
    "Vegetacao Natural": "#2d5a3d",
    "Pastagem": "#d4b65a",
    "Agricultura": "#d96aa3",
    "Agua": "#4a7ba6",
    "Area Urbana": "#8a8a82",
    "Outros": "#c4ad8a",
}


# -------------------- funcoes existentes (inalteradas) --------------------

def agregar_uf(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("ano", as_index=False)[SOMAR].sum(min_count=1)
    grp["lulc_vegetacao_nativa_ha"] = grp[LULC_NATIVO].sum(axis=1)
    grp["pct_vegetacao_nativa"] = grp["lulc_vegetacao_nativa_ha"] / grp["lulc_area_total_ha"]
    grp["pct_pastagem"] = grp["lulc_pastagem_ha"] / grp["lulc_area_total_ha"]
    grp["pct_soja"] = grp["lulc_soja_ha"] / grp["lulc_area_total_ha"]
    grp["pct_agricultura"] = grp["lulc_agricultura_ha"] / grp["lulc_area_total_ha"]
    grp["pct_mosaico"] = grp["lulc_mosaico_usos_ha"] / grp["lulc_area_total_ha"]
    grp["pct_agua"] = grp["lulc_corpo_dagua_ha"] / grp["lulc_area_total_ha"]
    grp["pct_area_urbana"] = grp["lulc_area_urbana_ha"] / grp["lulc_area_total_ha"]
    grp["lotacao_bov_ha_pasto"] = grp["pec_bovinos_cab"] / grp["lulc_pastagem_ha"]
    grp["lotacao_ua_ha_pasto"] = grp["pec_bovinos_ua"] / grp["lulc_pastagem_ha"]
    return grp


def montar_serie(grp: pd.DataFrame) -> list[dict]:
    cols_pct = [
        "pct_vegetacao_nativa", "pct_pastagem", "pct_soja",
        "pct_agricultura", "pct_mosaico", "pct_agua", "pct_area_urbana",
    ]
    cols_abs = [
        "lulc_area_total_ha",
        "lulc_vegetacao_nativa_ha",
        "lulc_pastagem_ha",
        "lulc_soja_ha",
        "lulc_agricultura_ha",
        "lulc_corpo_dagua_ha",
        "lulc_area_urbana_ha",
        "pec_bovinos_cab",
        "pec_bovinos_ua",
        "pec_suinos_cab",
        "pec_galinaceos_cab",
        "pec_ovinos_tosquiados_cab",
        "agri_soja_ton",
        "agri_milho_total_ton",
        "agri_milho1_ha_plantada",
        "agri_milho2_ha_plantada",
        "agri_cana_ton",
        "agri_algodao_ton",
        "agri_mandioca_ton",
        "agri_arroz_ton",
        "agri_sorgo_ton",
        "agri_feijao_ton",
        "agri_leite_mil_litros",
        "perm_cafe_total_ton",
        "perm_banana_ton",
        "perm_laranja_ton",
        "perm_manga_ton",
        "perm_mamao_ton",
        "perm_maracuja_ton",
        "perm_uva_ton",
        "pib_real_rs",
        "va_agro_real_rs",
        "populacao",
        "sicor_total_real_rs",
        "fogo_total_ha",
        "lotacao_bov_ha_pasto",
        "lotacao_ua_ha_pasto",
    ]
    out = []
    for _, row in grp.iterrows():
        rec = {"ano": int(row["ano"])}
        for c in cols_pct:
            rec[c] = None if pd.isna(row[c]) else round(float(row[c]), 6)
        for c in cols_abs:
            rec[c] = None if pd.isna(row[c]) else float(row[c])
        out.append(rec)
    return out


def transicoes_resumo(grp: pd.DataFrame) -> dict:
    inicio = grp[grp["ano"] == grp["ano"].min()].iloc[0]
    fim = grp[grp["ano"] == grp["ano"].max()].iloc[0]
    classes = {
        "Vegetacao nativa": "lulc_vegetacao_nativa_ha",
        "Pastagem": "lulc_pastagem_ha",
        "Soja": "lulc_soja_ha",
        "Outras lavouras": "lulc_agricultura_ha",
        "Mosaico de usos": "lulc_mosaico_usos_ha",
        "Silvicultura": "lulc_silvicultura_ha",
        "Area urbana": "lulc_area_urbana_ha",
    }
    return {
        "ano_inicio": int(inicio["ano"]),
        "ano_fim": int(fim["ano"]),
        "classes": [
            {
                "nome": nome,
                "ha_inicio": float(inicio[col]),
                "ha_fim": float(fim[col]),
                "delta_ha": float(fim[col] - inicio[col]),
                "delta_pct": (
                    None
                    if inicio[col] == 0
                    else round(float((fim[col] - inicio[col]) / inicio[col]) * 100, 2)
                ),
            }
            for nome, col in classes.items()
        ],
    }


# -------------------- novas funcoes --------------------

def gerar_fogo_goias(df: pd.DataFrame) -> dict:
    """Serie UF agregada de fogo por classe, 40 anos."""
    fogo_cols = FOGO_SOMAR
    grp = df.groupby("ano", as_index=False)[fogo_cols].sum(min_count=1)
    serie = []
    for _, row in grp.iterrows():
        rec = {"ano": int(row["ano"])}
        for c in fogo_cols:
            key = c.replace("fogo_", "").replace("_ha", "")
            rec[key] = None if pd.isna(row[c]) else round(float(row[c]), 2)
        serie.append(rec)
    return {
        "unidade": "Goias (UF)",
        "n_anos": len(serie),
        "classes": ["veg_nat", "pastagem", "agricultura", "mosaico", "outros", "total"],
        "serie": serie,
    }


def gerar_painel_municipal_indice(df: pd.DataFrame) -> list[dict]:
    """Lookup leve: cd_mun, nm_mun para cada municipio."""
    indice = df[["cd_mun", "nm_mun"]].drop_duplicates("cd_mun").sort_values("cd_mun")
    return [
        {"cd_mun": int(row["cd_mun"]), "nm_mun": str(row["nm_mun"])}
        for _, row in indice.iterrows()
    ]


def gerar_series_municipais(df: pd.DataFrame) -> None:
    """Escreve 246 JSONs individuais em municipios/."""
    MUNI_DIR.mkdir(parents=True, exist_ok=True)

    # Derivar pct vegetacao nativa
    df = df.copy()
    df["lulc_vegetacao_nativa_ha"] = df[LULC_NATIVO].sum(axis=1)
    df["pct_vegetacao_nativa"] = df["lulc_vegetacao_nativa_ha"] / df["lulc_area_total_ha"]

    all_cols = MUNI_COLS_SERIE + MUNI_COLS_PCT + ["lulc_vegetacao_nativa_ha", "pct_vegetacao_nativa"]

    for cd_mun, grp in df.groupby("cd_mun"):
        grp = grp.sort_values("ano")
        serie = []
        for _, row in grp.iterrows():
            rec = {"ano": int(row["ano"])}
            for c in all_cols:
                v = row.get(c)
                if c.startswith("pct_"):
                    rec[c] = None if pd.isna(v) else round(float(v), 4)
                else:
                    rec[c] = None if pd.isna(v) else float(v)
            serie.append(rec)
        nm = grp["nm_mun"].iloc[0]
        obj = {"cd_mun": int(cd_mun), "nm_mun": str(nm), "serie": serie}
        path = MUNI_DIR / f"{int(cd_mun)}.json"
        path.write_text(
            json.dumps(obj, ensure_ascii=False),
            encoding="utf-8",
        )
    print(f"OK municipios/ -> {len(df['cd_mun'].unique())} arquivos")


def gerar_transicoes_matriz() -> dict:
    """5 matrizes 6x6 agregadas (periodos do Atlas)."""
    df = pd.read_csv(TRANSICOES_CSV)
    # Mapear ids para nomes canonicos
    id_to_nome = {1: "Vegetacao Natural", 2: "Pastagem", 3: "Agricultura",
                  4: "Agua", 5: "Area Urbana", 6: "Outros"}
    nomes_canonicos = list(id_to_nome.values())

    periodos = []
    for ano_orig, ano_dest in PERIODOS_TRANSICAO:
        subset = df[(df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest)]
        if subset.empty:
            print(f"  AVISO: periodo {ano_orig}-{ano_dest} sem dados")
            continue
        # Agregar area_ha por (classe_orig, classe_dest)
        pivot = subset.groupby(["classe_orig", "classe_dest"], as_index=False)["area_ha"].sum()
        # Montar matriz 6x6
        matriz = [[0.0] * 6 for _ in range(6)]
        for _, row in pivot.iterrows():
            i = int(row["classe_orig"]) - 1
            j = int(row["classe_dest"]) - 1
            if 0 <= i < 6 and 0 <= j < 6:
                matriz[i][j] = round(float(row["area_ha"]), 2)
        periodos.append({
            "rotulo": f"{ano_orig} → {ano_dest}",
            "ano_origem": ano_orig,
            "ano_destino": ano_dest,
            "classes": nomes_canonicos,
            "matriz": matriz,
        })
    return {"periodos": periodos}


def gerar_sankey_data() -> dict:
    """Nodos + links para d3-sankey (1985 -> 2024)."""
    df = pd.read_csv(TRANSICOES_CSV)

    # Filtrar apenas 1985->2024
    subset = df[(df["ano_origem"] == 1985) & (df["ano_destino"] == 2024)]
    pivot = subset.groupby(["classe_orig", "classe_dest"], as_index=False)["area_ha"].sum()

    # Nodos: 6 classes x 2 anos = 12
    id_to_nome = {1: "Vegetacao Natural", 2: "Pastagem", 3: "Agricultura",
                  4: "Agua", 5: "Area Urbana", 6: "Outros"}
    nomes = list(id_to_nome.values())

    nodes = []
    node_id_map = {}
    for ano_label in ["1985", "2024"]:
        for cid in range(1, 7):
            nome = id_to_nome[cid]
            node_key = f"{nome}_{ano_label}"
            node_id = len(nodes)
            node_id_map[(cid, ano_label)] = node_id
            nodes.append({
                "id": node_key,
                "label": f"{nome} ({ano_label})",
                "color": CORES_SANKEY[nome],
            })

    # Links
    links = []
    for _, row in pivot.iterrows():
        src = int(row["classe_orig"])
        tgt = int(row["classe_dest"])
        area = float(row["area_ha"])
        # Converter para Mha para legibilidade
        area_mha = round(area / 1e6, 4)
        if area_mha < 0.01:
            continue  # Pular fluxos muito pequenos
        src_nome = id_to_nome[src]
        tgt_nome = id_to_nome[tgt]
        links.append({
            "source": f"{src_nome}_1985",
            "target": f"{tgt_nome}_2024",
            "value": area_mha,
            "color": CORES_SANKEY[src_nome],
        })

    return {"nodes": nodes, "links": links}


# -------------------- main --------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PAINEL)
    grp = agregar_uf(df).sort_values("ano").reset_index(drop=True)

    # 1. painel_goias.json (existente, inalterado)
    serie = montar_serie(grp)
    (OUT_DIR / "painel_goias.json").write_text(
        json.dumps({"unidade": "Goias (UF)", "n_anos": len(serie), "serie": serie}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK painel_goias.json -> {len(serie)} anos ({serie[0]['ano']}-{serie[-1]['ano']})")

    # 2. transicoes_resumo.json (existente, inalterado)
    resumo = transicoes_resumo(grp)
    (OUT_DIR / "transicoes_resumo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK transicoes_resumo.json -> {len(resumo['classes'])} classes")

    # 3. fogo_goias.json (novo)
    fogo = gerar_fogo_goias(df)
    (OUT_DIR / "fogo_goias.json").write_text(
        json.dumps(fogo, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK fogo_goias.json -> {fogo['n_anos']} anos, {len(fogo['classes'])} classes")

    # 4. painel_municipal_indice.json (novo)
    indice = gerar_painel_municipal_indice(df)
    (OUT_DIR / "painel_municipal_indice.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK painel_municipal_indice.json -> {len(indice)} municipios")

    # 5. municipios/{cd_mun}.json x 246 (novo)
    gerar_series_municipais(df)

    # 6. transicoes_matriz.json (novo)
    transicoes = gerar_transicoes_matriz()
    (OUT_DIR / "transicoes_matriz.json").write_text(
        json.dumps(transicoes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    n_periodos = len(transicoes["periodos"])
    print(f"OK transicoes_matriz.json -> {n_periodos} periodos")

    # 7. sankey_data.json (novo)
    sankey = gerar_sankey_data()
    (OUT_DIR / "sankey_data.json").write_text(
        json.dumps(sankey, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    n_links = len(sankey["links"])
    n_nodes = len(sankey["nodes"])
    print(f"OK sankey_data.json -> {n_nodes} nodos, {n_links} links")


if __name__ == "__main__":
    main()