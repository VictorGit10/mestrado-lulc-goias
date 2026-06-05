"""Agrega painel municipal em series anuais UF (Minas Gerais) para a timeline.

Adaptado de Visualizacao/scripts/preparar_dados_timeline.py para MG.
Le data/processed/painel_unificado_mg.parquet (853 munis x 40 anos x N cols),
soma areas LULC, totaliza socioeconomicos e exporta JSONs enxutos para o
front-end em Minas/assets/data/. Tambem produz:
  - transicoes_resumo_mg.json  (2 snapshots: inicio e fim da serie)
  - painel_mg.json             (serie UF anual)
  - painel_municipal_indice_mg.json (lookup leve: 853 municipios)
  - municipios/{cd_mun}.json x 853 (serie municipal compacta)
  - transicoes_matriz_mg.json  (5 matrizes 6x6 por periodo)
  - sankey_data_mg.json        (nodos + links para d3-sankey 1985->2024)
  - marcos_mg.json             (marcos institucionais de MG)

NOTA: Sem dados de fogo (fogo_*.json nao e gerado).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from config_mg import ATOS, MARCOS, CORES_ATO

ROOT = Path(__file__).resolve().parents[3]
PAINEL = ROOT / "data" / "processed" / "painel_unificado_mg.parquet"
TRANSICOES_CSV = ROOT / "data" / "processed" / "transicoes_mapbiomas_mg.csv"
PIB_UF_IPEA_CSV = ROOT / "data" / "processed" / "pib_uf_ipea_mg.csv"
OUT_DIR = ROOT / "Minas" / "assets" / "data"
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
    "lulc_cafe_ha",
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
    "pib_uf_real_rs",
    "va_agro_uf_real_rs",
    "populacao",
    # sicor_total_real_rs: adicionado se disponível (ausente antes da coleta SICOR)
    # NOTA: sem fogo_total_ha (sem dados de fogo para MG)
]

# Colunas opcionais — presentes apenas quando os pipelines correspondentes já rodaram
_OPTIONAL = ["sicor_total_real_rs"]
SOMAR = [c for c in SOMAR if c not in _OPTIONAL]

# Periodos das transicoes (5 periodos para o Atlas)
PERIODOS_TRANSICAO = [
    (1985, 1995),
    (1995, 2005),
    (2005, 2015),
    (2015, 2024),
    (1985, 2024),
]

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

# Colunas para a serie municipal compacta (sem fogo)
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
    "populacao",
    "lotacao_bov_ha_pasto",
    "lotacao_ua_ha_pasto",
]

MUNI_COLS_PCT = [
    "pct_pastagem_lulc",
    "pct_agricultura_lulc",
    "pct_natural_lulc",
]


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

    if PIB_UF_IPEA_CSV.exists():
        pib_uf = pd.read_csv(PIB_UF_IPEA_CSV)[
            ["ano", "pib_uf_real_rs", "va_agro_uf_real_rs"]
        ]
        grp = grp.merge(pib_uf, on="ano", how="left")
    else:
        grp["pib_uf_real_rs"] = pd.NA
        grp["va_agro_uf_real_rs"] = pd.NA
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
        "pib_uf_real_rs",
        "va_agro_uf_real_rs",
        "populacao",
        "lotacao_bov_ha_pasto",
        "lotacao_ua_ha_pasto",
    ]
    out = []
    for _, row in grp.iterrows():
        rec = {"ano": int(row["ano"])}
        for c in cols_pct:
            rec[c] = None if pd.isna(row[c]) else round(float(row[c]), 6)
        for c in cols_abs:
            v = row.get(c)
            rec[c] = None if v is None or pd.isna(v) else float(v)
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
    }
    items = []
    for nome, col in classes.items():
        vi = float(inicio[col]) if not pd.isna(inicio[col]) else 0
        vf = float(fim[col]) if not pd.isna(fim[col]) else 0
        delta = vf - vi
        area_total = float(fim["lulc_area_total_ha"])
        pct_i = vi / area_total if area_total else 0
        pct_f = vf / area_total if area_total else 0
        items.append({
            "classe": nome,
            "ha_inicio": round(vi),
            "ha_fim": round(vf),
            "delta_ha": round(delta),
            "pct_inicio": round(pct_i, 4),
            "pct_fim": round(pct_f, 4),
            "delta_pp": round((pct_f - pct_i) * 100, 2),
        })
    return {
        "unidade": "Minas Gerais (UF)",
        "ano_inicio": int(inicio["ano"]),
        "ano_fim": int(fim["ano"]),
        "classes": items,
    }


def gerar_marcos() -> dict:
    return {
        "marcos": [
            {
                "ano": ano,
                "titulo": m["titulo"],
                "categoria": m["evidencia"],
                **({"subtitulo": m.get("subtitulo", "")} if "subtitulo" in m else {}),
                "descricao": m.get("nota", m["titulo"]),
            }
            for ano, m in sorted(MARCOS.items())
        ]
    }


def gerar_serie_municipal(df: pd.DataFrame) -> None:
    MUNI_DIR.mkdir(parents=True, exist_ok=True)
    for cd_mun, grp in df.groupby("cd_mun"):
        nm = grp["nm_mun"].iloc[0] if "nm_mun" in grp.columns else str(cd_mun)
        serie = []
        for _, row in grp.sort_values("ano").iterrows():
            rec = {"ano": int(row["ano"])}
            for c in MUNI_COLS_SERIE:
                v = row.get(c)
                rec[c] = None if v is None or pd.isna(v) else float(v)
            for c in MUNI_COLS_PCT:
                v = row.get(c)
                rec[c] = None if v is None or pd.isna(v) else round(float(v), 6)
            serie.append(rec)
        out = {"cd_mun": int(cd_mun), "nm_mun": nm, "serie": serie}
        (MUNI_DIR / f"{cd_mun}.json").write_text(
            json.dumps(out, ensure_ascii=False), encoding="utf-8"
        )


def gerar_indice_municipal(df: pd.DataFrame) -> dict:
    items = []
    for cd_mun, grp in df.groupby("cd_mun"):
        nm = grp["nm_mun"].iloc[0] if "nm_mun" in grp.columns else str(cd_mun)
        items.append({"cd_mun": int(cd_mun), "nm_mun": nm})
    return {"municipios": sorted(items, key=lambda x: x["nm_mun"])}


def gerar_sankey_uf(df: pd.DataFrame) -> dict:
    if not TRANSICOES_CSV.exists():
        print(f"[AVISO] {TRANSICOES_CSV} nao encontrado. Sankey nao sera gerado.")
        return {}

    trans = pd.read_csv(TRANSICOES_CSV)
    ini = df["ano"].min()
    fim = df["ano"].max()
    filtro = trans[trans["ano_de"].eq(ini) & trans["ano_para"].eq(fim)]
    nodes = []
    links = []
    node_set = set()
    for _, row in filtro.iterrows():
        src = CLASSES_SANKEY.get(int(row["classe_de"]), "Outros")
        tgt = CLASSES_SANKEY.get(int(row["classe_para"]), "Outros")
        src_id = f"{src}_{ini}"
        tgt_id = f"{tgt}_{fim}"
        if src_id not in node_set:
            nodes.append({"id": src_id, "label": src, "color": CORES_SANKEY.get(src, "#999")})
            node_set.add(src_id)
        if tgt_id not in node_set:
            nodes.append({"id": tgt_id, "label": tgt, "color": CORES_SANKEY.get(tgt, "#999")})
            node_set.add(tgt_id)
        links.append({
            "source": src_id,
            "target": tgt_id,
            "value": round(float(row["area_ha"]) / 1e6, 3),
            "color": CORES_SANKEY.get(src, "#999"),
        })
    return {"nodes": nodes, "links": links, "ano_ini": int(ini), "ano_fim": int(fim)}


def gerar_sankey_atos(df: pd.DataFrame) -> dict[str, dict]:
    if not TRANSICOES_CSV.exists():
        return {}

    trans = pd.read_csv(TRANSICOES_CSV)
    resultados = {}
    for ato_id, ato_info in ATOS.items():
        ini = ato_info["inicio"]
        fim = ato_info["fim"]
        filtro = trans[trans["ano_de"].eq(ini) & trans["ano_para"].eq(fim)]
        if filtro.empty:
            continue
        nodes = []
        links = []
        node_set = set()
        for _, row in filtro.iterrows():
            src = CLASSES_SANKEY.get(int(row["classe_de"]), "Outros")
            tgt = CLASSES_SANKEY.get(int(row["classe_para"]), "Outros")
            src_id = f"{src}_{ini}"
            tgt_id = f"{tgt}_{fim}"
            if src_id not in node_set:
                nodes.append({"id": src_id, "label": src, "color": CORES_SANKEY.get(src, "#999")})
                node_set.add(src_id)
            if tgt_id not in node_set:
                nodes.append({"id": tgt_id, "label": tgt, "color": CORES_SANKEY.get(tgt, "#999")})
                node_set.add(tgt_id)
            links.append({
                "source": src_id,
                "target": tgt_id,
                "value": round(float(row["area_ha"]) / 1e6, 3),
                "color": CORES_SANKEY.get(src, "#999"),
            })
        resultados[ato_id] = {"nodes": nodes, "links": links, "ano_ini": int(ini), "ano_fim": int(fim)}
    return resultados


def gerar_matrizes_transicao() -> dict:
    if not TRANSICOES_CSV.exists():
        return {"periodos": []}

    trans = pd.read_csv(TRANSICOES_CSV)
    periodos = []
    for ini, fim in PERIODOS_TRANSICAO:
        filtro = trans[trans["ano_de"].eq(ini) & trans["ano_para"].eq(fim)]
        if filtro.empty:
            continue
        matriz = {}
        for _, row in filtro.iterrows():
            src = CLASSES_SANKEY.get(int(row["classe_de"]), "Outros")
            tgt = CLASSES_SANKEY.get(int(row["classe_para"]), "Outros")
            matriz[(src, tgt)] = round(float(row["area_ha"]) / 1e6, 3)
        periodos.append({
            "inicio": ini,
            "fim": fim,
            "matriz": {f"{k[0]}|{k[1]}": v for (k, v), v in matriz.items()},
        })
    return {"periodos": periodos}


def main():
    if not PAINEL.exists():
        print(f"[ERRO] {PAINEL} nao encontrado. Execute o pipeline de dados MG primeiro.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MUNI_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(PAINEL)
    print(f"  Carregado: {len(df):,} linhas, {df['cd_mun'].nunique()} municipios")

    # Filtrar listas de colunas para incluir apenas as que existem no painel
    cols_disponiveis = set(df.columns)
    global SOMAR, MUNI_COLS_SERIE
    SOMAR = [c for c in SOMAR if c in cols_disponiveis]
    MUNI_COLS_SERIE = [c for c in MUNI_COLS_SERIE if c in cols_disponiveis]
    # Adicionar colunas opcionais se disponíveis
    if "sicor_total_real_rs" in cols_disponiveis:
        SOMAR.append("sicor_total_real_rs")

    # Agregar UF
    grp = agregar_uf(df)
    serie = montar_serie(grp)

    # Painel UF
    painel_out = {"unidade": "Minas Gerais (UF)", "serie": serie}
    (OUT_DIR / "painel_mg.json").write_text(
        json.dumps(painel_out, ensure_ascii=False, indent=None), encoding="utf-8"
    )
    print(f"  painel_mg.json: {len(serie)} anos")

    # Transicoes resumo
    resumo = transicoes_resumo(grp)
    (OUT_DIR / "transicoes_resumo_mg.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  transicoes_resumo_mg.json: {len(resumo['classes'])} classes")

    # Marcos
    marcos_out = gerar_marcos()
    (OUT_DIR / "marcos_mg.json").write_text(
        json.dumps(marcos_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  marcos_mg.json: {len(marcos_out['marcos'])} marcos")

    # Indice municipal
    indice = gerar_indice_municipal(df)
    (OUT_DIR / "painel_municipal_indice_mg.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=None), encoding="utf-8"
    )
    print(f"  painel_municipal_indice_mg.json: {len(indice['municipios'])} municipios")

    # Series municipais
    gerar_serie_municipal(df)
    print(f"  municipios/: {len(list(MUNI_DIR.glob('*.json')))} arquivos")

    # Sankey UF
    sankey = gerar_sankey_uf(df)
    if sankey:
        (OUT_DIR / "sankey_data_mg.json").write_text(
            json.dumps(sankey, ensure_ascii=False, indent=None), encoding="utf-8"
        )
        print(f"  sankey_data_mg.json: {len(sankey['nodes'])} nodes, {len(sankey['links'])} links")

    # Sankey por ato
    sankey_atos = gerar_sankey_atos(df)
    for ato_id, data in sankey_atos.items():
        (OUT_DIR / f"sankey_ato_{ato_id}_mg.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=None), encoding="utf-8"
        )
        print(f"  sankey_ato_{ato_id}_mg.json: {len(data['nodes'])} nodes")

    # Matrizes de transicao
    matrizes = gerar_matrizes_transicao()
    (OUT_DIR / "transicoes_matriz_mg.json").write_text(
        json.dumps(matrizes, ensure_ascii=False, indent=None), encoding="utf-8"
    )
    print(f"  transicoes_matriz_mg.json: {len(matrizes['periodos'])} periodos")

    print("\n  Concluido! JSONs em Minas/assets/data/")


if __name__ == "__main__":
    main()