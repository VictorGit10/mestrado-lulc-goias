#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta o JSON de todos os centros de massa para a página dedicada centros-de-massa.html.

Reúne:
1. Trajetória Principal (#32): agricultura, pastagem, bovinos, veg_natural
2. Controles & Desagregados (#44): leite, area_urbana, floresta, savanica, campo_nativo
3. Fogo & Queimadas (#41): fogo_total, fogo_pasto, fogo_veg, conv_vp
4. Econômico & Crédito (#50): sicor_total, va_agro, pib
5. Capacidade Instalada / Silos (#53): armazenagem (CONAB)

Uso:
    python scripts/exportar_centros_massa_completo.py
"""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"

ARQ_SAIDA = DIR_VIZ / "centros_massa_completo.json"

CATEGORIAS = {
    "uso_terra": {
        "id": "uso_terra",
        "titulo": "Trajetória Principal (Uso da Terra)",
        "desc": "Os quatro grandes vetores do uso e cobertura da terra em Goiás (Pipeline #32)."
    },
    "controles": {
        "id": "controles",
        "titulo": "Pecuária de Leite & Controles Espaciais",
        "desc": "Atividades e formações vegetais desagregadas que testam a hipótese da marcha (Pipeline #44)."
    },
    "fogo": {
        "id": "fogo",
        "titulo": "Fogo & Queimadas",
        "desc": "Dinâmica espacial dos incêndios e queimadas de manejo em relação à fronteira (Pipeline #41)."
    },
    "economico": {
        "id": "economico",
        "titulo": "Econômico, Crédito & Infraestrutura",
        "desc": "Onde fica o dinheiro, o valor adicionado e a capacidade física de armazenagem (Pipelines #50 e #53)."
    },
    "validacao": {
        "id": "validacao",
        "titulo": "Validação de Fonte (Soja: MapBiomas × SIDRA)",
        "desc": "Teste cruzado: a soja vista pelo raster do MapBiomas vs pela área plantada declarada no SIDRA. A divergência de sinal no Ato III expõe a deriva do mosaico (Pipeline #44; D25)."
    }
}

VAR_CONFIG = {
    # --- Uso da Terra ---
    "agricultura": {
        "cat": "uso_terra",
        "rotulo": "Agricultura (Lavoura)",
        "cor": "#d96aa3",
        "insight": "Marchou +65,2 km ao norte (1985→2024), mantendo gradiente persistente ~120 km ao sul de pasto/rebanho.",
        "fonte": "Pipeline #32 (MapBiomas)",
    },
    "pastagem": {
        "cat": "uso_terra",
        "rotulo": "Pastagem",
        "cor": "#c79a2e",
        "insight": "Lidera a marcha territorial ao norte (+77,6 km), abrindo a fronteira agropecuária.",
        "fonte": "Pipeline #32 (MapBiomas)",
    },
    "bovinos": {
        "cat": "uso_terra",
        "rotulo": "Rebanho bovino",
        "cor": "#8e3b5a",
        "insight": "Marchou +66,9 km ao norte quase a prumo (azimute 19°), acompanhando o pasto.",
        "fonte": "Pipeline #32 (IBGE PPM)",
    },
    "veg_natural": {
        "cat": "uso_terra",
        "rotulo": "Vegetação natural (agregada)",
        "cor": "#2d5a3d",
        "insight": "Ancorada ao norte (+7,6 km, IC contém zero) como muralha natural da fronteira.",
        "fonte": "Pipeline #32 (MapBiomas)",
    },

    # --- Controles & Desagregados ---
    "leite": {
        "cat": "controles",
        "rotulo": "Pecuária de leite",
        "cor": "#4a7c59",
        "insight": "Ancorada na bacia tradicional do Sul: +18,2 km no Ato I (de +29,9 km no líquido 1985–2024); depois estaciona — Ato II +4,9 km e Ato III +2,9 km, ambos com IC contendo zero. Não acompanha o gado de corte.",
        "fonte": "Pipeline #44 (IBGE PPM)",
    },
    "area_urbana": {
        "cat": "controles",
        "rotulo": "Área urbana",
        "cor": "#5b6770",
        "insight": "Moveu-se -8,4 km ao SUL. A população urbanizada ancorou no eixo Goiânia-Anápolis-Rio Verde, ao contrário da agropecuária.",
        "fonte": "Pipeline #44 (MapBiomas)",
    },
    "floresta": {
        "cat": "controles",
        "rotulo": "Formação Florestal (Mata de Galeria)",
        "cor": "#1b4332",
        "insight": "Ancorada ao norte (+8,7 km). É a verdadeira muralha florestal que barra a expansão agrícola.",
        "fonte": "Pipeline #44 (MapBiomas)",
    },
    "savanica": {
        "cat": "controles",
        "rotulo": "Formação Savânica (Cerrado s.s.)",
        "cor": "#52b788",
        "insight": "Deslocamento leve (+12,4 km, IC contém zero). Sofreu a maior perda de área absoluta.",
        "fonte": "Pipeline #44 (MapBiomas)",
    },
    "campo_nativo": {
        "cat": "controles",
        "rotulo": "Formação Campestre (Campos)",
        "cor": "#95d5b2",
        "insight": "Recuou +34,8 km ao norte, revelando que os campos nativos do Sul foram convertidos primeiro.",
        "fonte": "Pipeline #44 (MapBiomas)",
    },

    # --- Fogo & Queimadas ---
    "fogo_total": {
        "cat": "fogo",
        "rotulo": "Fogo Total (Queimadas)",
        "cor": "#e63946",
        "insight": "Fica ao NORTE da conversão em todos os 39 anos (+68,8 km). Co-evolução no espaço.",
        "fonte": "Pipeline #41 (MapBiomas Fogo)",
    },
    "fogo_pasto": {
        "cat": "fogo",
        "rotulo": "Fogo em Pastagem",
        "cor": "#f77f00",
        "insight": "Deslocamento expressivo de +165,6 km ao norte, acompanhando o manejo e renovação de pastos.",
        "fonte": "Pipeline #41 (MapBiomas Fogo)",
    },
    "fogo_veg": {
        "cat": "fogo",
        "rotulo": "Fogo em Veg. Natural",
        "cor": "#d62828",
        "insight": "Subiu +85,8 km ao norte, incidindo fortemente sobre o Cerrado savânico e campestre.",
        "fonte": "Pipeline #41 (MapBiomas Fogo)",
    },
    "conv_vp": {
        "cat": "fogo",
        "rotulo": "Conversão Veg. → Pasto",
        "cor": "#fcbf49",
        "insight": "Vanguarda física do desmatamento: marcha +126,6 km ao norte de 1985 a 2023.",
        "fonte": "Pipeline #41 (MapBiomas)",
    },

    # --- Econômico & Crédito & Capacidade ---
    "sicor_total": {
        "cat": "economico",
        "rotulo": "Crédito Rural (SICOR)",
        "cor": "#2a9d8f",
        "insight": "Fica ~75 km ao SUL da pastagem. O crédito consolida o núcleo produtivo instalado; não lidera a fronteira.",
        "fonte": "Pipeline #50 (Bacen SICOR)",
    },
    "va_agro": {
        "cat": "economico",
        "rotulo": "Valor Adicionado Agro (PIB Agro)",
        "cor": "#264653",
        "insight": "Ancorado no Sul/Sudoeste. O vão entre o valor agro e a área de pasto alargou de 84 para 101 km.",
        "fonte": "Pipeline #50 (IBGE PIB)",
    },
    "pib": {
        "cat": "economico",
        "rotulo": "PIB Total",
        "cor": "#1d3557",
        "insight": "Ancorado na Região Metropolitana de Goiânia e eixo Sudoeste.",
        "fonte": "Pipeline #50 (IBGE PIB)",
    },
    "capacidade": {
        "cat": "economico",
        "rotulo": "Silos CONAB (Armazenagem 2024)",
        "cor": "#6a040f",
        "insight": "A camada MAIS AO SUL de todas (lat -17,24°, ~150 km atrás do gado, -83 km atrás do crédito). A infraestrutura consolida.",
        "fonte": "Pipeline #53 (CONAB Cadastrados)",
    },

    # --- Validação de Fonte: soja MapBiomas × SIDRA ---
    "soja_raster": {
        "cat": "validacao",
        "rotulo": "Soja — MapBiomas (raster)",
        "cor": "#9d4edd",
        "insight": "Recua −7,1 km ao SUL no Ato III (IC 95% −13,2 a −3,4), invertendo a marcha de +50,3 km do Ato II. A soja aberta na fronteira norte é rerrotulada como 'Mosaico de Usos' pelo MapBiomas, escondendo massa no norte — a deriva do mosaico (D25).",
        "fonte": "Pipeline #44 (MapBiomas)",
    },
    "soja_sidra": {
        "cat": "validacao",
        "rotulo": "Soja — SIDRA (área plantada)",
        "cor": "#5a189a",
        "insight": "No mesmo Ato III a soja declarada segue +8,2 km ao NORTE (IC −0,5 a 16,1). As duas fontes divergem em sinal em 2020–24: o SIDRA vê a fronteira que o MapBiomas rerrotula como mosaico. O SIDRA é a âncora imune.",
        "fonte": "Pipeline #44 (IBGE SIDRA)",
    }
}


def _get_val(row, attr, fallback_attr=None):
    if hasattr(row, attr):
        v = getattr(row, attr)
        if pd.notna(v):
            return float(v)
    if fallback_attr and hasattr(row, fallback_attr):
        v = getattr(row, fallback_attr)
        if pd.notna(v):
            return float(v)
    return 0.0


def main():
    print("Iniciando exportação dos centros de massa completos...")

    df_anual = pd.read_csv(DIR_PROCESSED / "centro_massa_anual.csv")
    df_desloc = pd.read_csv(DIR_PROCESSED / "centro_massa_deslocamento.csv")
    df_desag = pd.read_csv(DIR_PROCESSED / "centro_massa_desagregado_anual.csv")
    df_desag_boot = pd.read_csv(DIR_PROCESSED / "centro_massa_desagregado_bootstrap.csv")
    df_fogo = pd.read_csv(DIR_PROCESSED / "fogo_fronteira_centroides.csv")
    df_fogo_desloc = pd.read_csv(DIR_PROCESSED / "fogo_fronteira_deslocamento.csv")
    df_econ = pd.read_csv(DIR_PROCESSED / "centro_massa_economico_anual.csv")
    df_cap = pd.read_csv(DIR_PROCESSED / "centro_massa_capacidade.csv")

    variaveis_out = []

    for var_id, cfg in VAR_CONFIG.items():
        pts = []
        liquido = {}

        if var_id in ["agricultura", "pastagem", "bovinos", "veg_natural"]:
            sub = df_anual[df_anual["variavel"] == var_id].sort_values("ano")
            for r in sub.itertuples():
                pts.append({
                    "a": int(r.ano),
                    "lon": round(_get_val(r, "lon_mean"), 5),
                    "lat": round(_get_val(r, "lat_mean"), 5),
                    "lonM": round(_get_val(r, "lon_med", "lon_mean"), 5),
                    "latM": round(_get_val(r, "lat_med", "lat_mean"), 5)
                })
            sub_d = df_desloc[(df_desloc["variavel"] == var_id) & (df_desloc["ato"] == "LÍQUIDO")]
            if not sub_d.empty:
                r_d = sub_d.iloc[0]
                liquido = {
                    "dN": round(float(r_d.dnorte_km), 1),
                    "dL": round(float(r_d.dleste_km), 1),
                    "dtot": round(float(r_d.dtotal_km), 1),
                    "az": round(float(r_d.azimute_deg), 1),
                    "robusto": True if var_id != "veg_natural" else False
                }

        elif var_id in ["leite", "area_urbana", "floresta", "savanica", "campo_nativo", "soja_raster", "soja_sidra"]:
            sub = df_desag[df_desag["variavel"] == var_id].sort_values("ano")
            for r in sub.itertuples():
                pts.append({
                    "a": int(r.ano),
                    "lon": round(_get_val(r, "lon_mean"), 5),
                    "lat": round(_get_val(r, "lat_mean"), 5),
                    "lonM": round(_get_val(r, "lon_med", "lon_mean"), 5),
                    "latM": round(_get_val(r, "lat_med", "lat_mean"), 5)
                })
            sub_b = df_desag_boot[(df_desag_boot["variavel"] == var_id) & (df_desag_boot["janela"] == "LÍQUIDO")]
            if not sub_b.empty:
                rb = sub_b.iloc[0]
                liquido = {
                    "dN": round(float(rb.dN_km), 1),
                    "lo": round(float(rb.dN_lo), 1),
                    "hi": round(float(rb.dN_hi), 1),
                    "robusto": bool(rb.exclui_zero)
                }
            # Deslocamento por ato (para a categoria validação mostrar a divergência Ato III)
            janelas = {}
            for jn in ["Ato I", "Ato II", "Ato III"]:
                rj = df_desag_boot[(df_desag_boot["variavel"] == var_id) & (df_desag_boot["janela"] == jn)]
                if not rj.empty:
                    janelas[jn] = round(float(rj.iloc[0].dN_km), 1)
            if janelas:
                liquido["janelas"] = janelas

        elif var_id in ["fogo_total", "fogo_pasto", "fogo_veg", "conv_vp"]:
            sub = df_fogo[df_fogo["fluxo"] == var_id].sort_values("ano")
            for r in sub.itertuples():
                pts.append({
                    "a": int(r.ano),
                    "lon": round(_get_val(r, "lon_mean"), 5),
                    "lat": round(_get_val(r, "lat_mean"), 5),
                    "lonM": round(_get_val(r, "lon_med", "lon_mean"), 5),
                    "latM": round(_get_val(r, "lat_med", "lat_mean"), 5)
                })
            sub_d = df_fogo_desloc[(df_fogo_desloc["fluxo"] == var_id) & (df_fogo_desloc["periodo"] == "LÍQUIDO")]
            if not sub_d.empty:
                rd = sub_d.iloc[0]
                liquido = {
                    "dN": round(float(rd.dnorte_km), 1),
                    "dL": round(float(rd.dleste_km), 1),
                    "dtot": round(float(rd.dtotal_km), 1),
                    "az": round(float(rd.azimute_deg), 1),
                    "robusto": True
                }

        elif var_id in ["sicor_total", "va_agro", "pib"]:
            sub = df_econ[df_econ["variavel"] == var_id].sort_values("ano")
            for r in sub.itertuples():
                pts.append({
                    "a": int(r.ano),
                    "lon": round(_get_val(r, "lon_mean"), 5),
                    "lat": round(_get_val(r, "lat_mean"), 5),
                    "lonM": round(_get_val(r, "lon_med", "lon_mean"), 5),
                    "latM": round(_get_val(r, "lat_med", "lat_mean"), 5)
                })
            if len(pts) >= 2:
                dlat_deg = pts[-1]["lat"] - pts[0]["lat"]
                dn_km = dlat_deg * 111.0
                liquido = {
                    "dN": round(float(dn_km), 1),
                    "robusto": True if abs(dn_km) > 15 else False
                }

        elif var_id == "capacidade":
            row = df_cap[df_cap["metodo"] == "ponto"].iloc[0]
            lat_val = round(_get_val(row, "lat_mean"), 5)
            lon_val = round(_get_val(row, "lon_mean"), 5)
            lat_m_val = round(_get_val(row, "lat_med", "lat_mean"), 5)
            lon_m_val = round(_get_val(row, "lon_med", "lon_mean"), 5)
            for ano in range(1985, 2025):
                pts.append({
                    "a": ano,
                    "lon": lon_val,
                    "lat": lat_val,
                    "lonM": lon_m_val,
                    "latM": lat_m_val
                })
            liquido = {
                "dN": 0.0,
                "robusto": True,
                "nota": "Snapshot 2024 (CONAB - 1.134 armazéns)"
            }

        variaveis_out.append({
            "id": var_id,
            "categoria": cfg["cat"],
            "rotulo": cfg["rotulo"],
            "cor": cfg["cor"],
            "insight": cfg["insight"],
            "fonte": cfg["fonte"],
            "pts": pts,
            "liquido": liquido
        })

    payload = {
        "meta": {
            "titulo": "Centros de Massa Completos — Goiás 1985-2024",
            "fonte": "Mestrado UFG / LULC Goiás",
            "total_series": len(variaveis_out)
        },
        "categorias": list(CATEGORIAS.values()),
        "anos": list(range(1985, 2025)),
        "atos": [
            {"id": "I", "titulo": "Pastagem como herança", "ini": 1985, "fim": 2000},
            {"id": "II", "titulo": "Expansão e intensificação", "ini": 2001, "fim": 2019},
            {"id": "III", "titulo": "Conversão acelerada", "ini": 2020, "fim": 2024}
        ],
        "variaveis": variaveis_out
    }

    DIR_VIZ.mkdir(parents=True, exist_ok=True)
    with open(ARQ_SAIDA, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))

    kb = ARQ_SAIDA.stat().st_size / 1024
    print(f"[OK] Exportado {ARQ_SAIDA} ({kb:.1f} KB) com {len(variaveis_out)} séries!")

if __name__ == "__main__":
    main()
