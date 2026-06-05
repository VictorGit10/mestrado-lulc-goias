"""config_mg.py — Definicoes canonicas de ATOS e MARCOS para Minas Gerais
====================================================================

Fonte unica de verdade para periodizacao e marcos institucionais de MG.
Espelha config_periodos.py mas com eras e marcos especificos de MG.

TODO: Apos rodar periodizacao em dados de MG, atualizar ATOS e MARCOS
com as fronteiras data-driven reais. Os valores abaixo sao placeholders
usando os mesmos limites de Goias.

Periodizacao data-driven para MG sera definida apos:
    - Pipeline #29a (sup-F multivariado) em painel_mg
    - Pipeline #29b (STARS) em painel_mg
    - Pipeline #29c (KL/TV transicoes) em transicoes_mg

Estrutura:
    - ATOS: periodos LULC empiricos com fronteiras data-driven
    - MARCOS: eventos institucionais com tipologia evidencial (A/B/C)
    - ANOS_MARCO: conjunto de anos com pino institucional
    - CORES_ATO: paleta de cores por ato
"""

from __future__ import annotations

# ─────────────────────────── ATOS ───────────────────────────
# TODO: Ajustar fronteiras apos periodizacao de MG.
# Placeholders usando os mesmos limites de Goias.

ATOS = {
    "I":   {"inicio": 1985, "fim": 2000, "titulo": "Pastagem como herança"},
    "II":  {"inicio": 2001, "fim": 2019, "titulo": "Expansão e intensificação"},
    "III": {"inicio": 2020, "fim": 2024, "titulo": "Conversão seletiva"},
}

ATOS_FLAT = {k: (v["inicio"], v["fim"], v["titulo"]) for k, v in ATOS.items()}

# ─────────────────────────── MARCOS ───────────────────────────
# TODO: Definir marcos institucionais especificos de MG.
# Placeholders com marcos nacionais (mesmos de Goias, a ajustar).

MARCOS = {
    1985: {
        "titulo": "Início da série / Redemocratização",
        "evidencia": "C",
        "escopo_empirico": "nao_aplicavel",
    },
    1994: {
        "titulo": "Plano Real",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Ajustar com dados especificos de MG.",
    },
    1996: {
        "titulo": "Lei Kandir",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Verificar se efeito e especifico a MG.",
    },
    2002: {
        "titulo": "Crédito e demanda chinesa",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Ajustar com dinamica de MG.",
    },
    2003: {
        "titulo": "Boom de commodities",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Ajustar com dinamica de MG.",
    },
    2012: {
        "titulo": "Código Florestal",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Ajustar com dinamica de MG.",
    },
    2018: {
        "titulo": "Reorganização de mercado",
        "evidencia": "B",
        "escopo_empirico": "nacional",
        "nota": "PLACEHOLDER: Ajustar com dinamica de MG.",
    },
    2024: {
        "titulo": "Estado atual",
        "evidencia": "C",
        "escopo_empirico": "nao_aplicavel",
    },
}

MARCOS_FLAT = {ano: m["titulo"] for ano, m in MARCOS.items()}
ANOS_MARCO = set(MARCOS.keys())

# ─────────────────────────── CORES ───────────────────────────
# Paleta para MG. TODO: considerar ajustar se o bioma dominante mudar.

CORES_ATO = {
    "I": "#8b3a1d",
    "II": "#a85234",
    "III": "#2d5a3d",
}

# ─────────────────────────── CONSTANTES MG ───────────────────────────

UF_SIGLA = "MG"
UF_CODIGO_IBGE = "31"
UF_NOME = "Minas Gerais"
N_MUNICIPIOS = 853
PAINEL_PATH = "data/processed/painel_unificado_mg.parquet"
TRANSICOES_PATH = "data/processed/transicoes_mapbiomas_mg.csv"
FOGO_PATH = None  # Sem dados de fogo para MG

# ─────────────────────────── EXPORTS ───────────────────────────

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    print("ATOS (placeholder, mesmos limites de GO):")
    for k, v in ATOS.items():
        print(f"  {k}: {v['inicio']}-{v['fim']}  {v['titulo']}")
    print()
    print("MARCOS (placeholder, marcos nacionais):")
    for ano, m in MARCOS.items():
        print(f"  {ano}: [{m['evidencia']}] {m['titulo']}  ({m['escopo_empirico']})")
    print()
    print(f"UF: {UF_SIGLA} ({UF_CODIGO_IBGE}) — {UF_NOME} — {N_MUNICIPIOS} municípios")
    print(f"Painel: {PAINEL_PATH}")
    print(f"Transições: {TRANSICOES_PATH}")
    print(f"Fogo: {FOGO_PATH} (sem dados de fogo)")