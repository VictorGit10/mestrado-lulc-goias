"""coleta_drivers_macro.py -- Pipeline #37A: Drivers macro do "drive comum"
=============================================================================

O QUE FAZ
---------
Coleta as series macroeconomicas EXOGENAS que sao candidatas a "drive comum"
da reorganizacao agropecuaria de Goias (1985-2024) -- a peca que o #34 deixou
INFERIDA, nao testada. Todas via IPEA Data (OData4), no mesmo padrao de
coleta_pib_uf_ipea.py (cache JSON + deflacao IPCA -> dez/2024).

POR QUE ESSAS SERIES (decisao do plano #37)
-------------------------------------------
A hipotese de transmissao do boom e: PRECO GLOBAL (super-ciclo China) x CAMBIO
(desvalorizacao real de 1999/2002) = "preco recebido" em R$, que sincroniza a
intensificacao no Sul e a fronteira no Norte. Por isso:

  - Precos internacionais em USD (IMF IFS, exogenos a Goias -> sem causalidade
    reversa, o que torna o lead-lag/Granger interpretavel; ver drive_comum.py).
  - Cambio REAL EFETIVO (REER, indice INPC-exportacoes): ja vem REAL e em indice,
    o que contorna a troca de moedas pre-1994 (Cruzeiro->Real), problema que a
    metodologia (deflacao_ipca.md) marca como nao-trivial para series nominais.
  - Cambio NOMINAL R$/US$ (BM_ERV): usado so para o "preco recebido em R$ real"
    (valido 1994+, quando o nominal e mensuravel; antes disso fica NaN).
  - Credito rural fluxo de Goias (CREATE, ja a precos de 2010): proxy de credito
    LONGA (1969+) que faz a ponte com o SICOR municipal (que so comeca em 2013).

SERIES IPEA (verificadas em 2026-06-06 via /api/odata4/Metadados):
  IFS12_SOJAGP12      mensal  US$         Commodities - soja em grao - cotacao internacional
  IFS12_BEEFB12       mensal  US$         Commodities - carne - cotacao internacional
  IFS12_MAIZE12       mensal  US$         Commodities - milho - cotacao internacional
  GAC12_TCERXTINPC12  mensal  indice      Taxa de cambio - efetiva real - INPC - exportacoes
                                          (media 2010=100; MAIOR = mais desvalorizado/competitivo)
  BM_ERV              anual   R$/US$      Taxa de cambio comercial - venda - media
  CREATE              anual   R$ de 2010  Fluxo de credito rural (nivel Estados; filtra GO=52)

CONSTRUCAO
----------
  preco_recebido_*_idx       = preco_usd x REER, normalizado (media 1985-2024 = 100).
                               Real do lado Brasil; janela completa; serie-manchete.
  preco_recebido_*_brl_real  = preco_usd x cambio_nominal, deflacionado por IPCA ->
                               dez/2024. Intuitivo (R$/t recebido); valido 1994+.
  credito_rural_go_real      = CREATE (R$ 2010) reescalado 2010 -> dez/2024 via IPCA.

LIMITACOES HONESTAS
-------------------
  - Precos USD ficam NOMINAIS (nao deflacionados por CPI dos EUA). Para a analise
    de pontos de virada em primeiras diferencas isso e robusto (a inflacao dos EUA
    e suave no periodo) e o REER ja carrega o ajuste real do lado brasileiro.
  - O "preco recebido em R$ real" pre-1994 e NaN (cambio nominal em moeda antiga
    nao e deflacionavel sem conversao de moeda nao-trivial).
  - Credito e politica (parcialmente endogeno); entra como CONTEXTO/ponte, nao
    como driver exogeno limpo (ver drive_comum.py, que o trata a parte).

SAIDA
  data/processed/drivers_macro_anual.csv   (ano 1985-2024 x drivers)

COMO RODAR
    python scripts/coleta_drivers_macro.py            # busca + processa (cache)
    python scripts/coleta_drivers_macro.py --force    # rebaixa da API
    python scripts/coleta_drivers_macro.py --offline  # so processa cache local

Depende de: IPEA Data API; data/raw/sidra/tab1737_ipca.csv (IPCA nacional, #3).
Quando foi feito: 2026-06-06.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw" / "drivers_macro"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

IPEA_API_BASE = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{code}')"
IPCA_RAW      = ROOT / "data" / "raw" / "sidra" / "tab1737_ipca.csv"  # IPCA nacional (#3)

ANO_MIN, ANO_MAX = 1985, 2024          # janela da dissertacao (LULC MapBiomas)
CODIGO_UF_GO     = "52"

# code IPEA -> (nome_saida, periodicidade, filtrar_GO?)
SERIES = {
    "IFS12_SOJAGP12":     ("preco_soja_usd",        "mensal", False),
    "IFS12_BEEFB12":      ("preco_boi_usd",         "mensal", False),
    "IFS12_MAIZE12":      ("preco_milho_usd",       "mensal", False),
    "GAC12_TCERXTINPC12": ("cambio_real_efetivo",   "mensal", False),
    "BM_ERV":             ("cambio_nominal_brl_usd", "anual", False),
    "CREATE":             ("credito_rural_go_2010",  "anual", True),
}

ANO_REAL_REF = 2010   # base do indice de preco recebido = media 1985-2024 = 100


# ---------------------------------------------------------------------------
# Download IPEA (mesmo padrao de coleta_pib_uf_ipea.py)
# ---------------------------------------------------------------------------

def _baixar_serie(code: str, force: bool = False, offline: bool = False) -> list[dict]:
    cache = DIR_RAW / f"{code}.json"
    if offline:
        if not cache.exists():
            raise FileNotFoundError(
                f"--offline mas cache {cache} nao existe; rode sem --offline antes."
            )
        with cache.open("r", encoding="utf-8") as f:
            return json.load(f)
    if cache.exists() and not force:
        with cache.open("r", encoding="utf-8") as f:
            return json.load(f)
    url = IPEA_API_BASE.format(code=code)
    print(f"  IPEA API: {code}...")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    valores = r.json().get("value", [])
    with cache.open("w", encoding="utf-8") as f:
        json.dump(valores, f)
    print(f"    {len(valores)} pontos, cache em {cache.name}")
    return valores


def _para_anual(valores: list[dict], periodicidade: str, filtrar_go: bool) -> pd.DataFrame:
    """Converte valores IPEA -> DataFrame[ano, valor]. Mensal -> media anual."""
    rows = []
    for v in valores:
        if v.get("VALVALOR") is None:
            continue
        if filtrar_go and str(v.get("TERCODIGO", "")) != CODIGO_UF_GO:
            continue
        ano = int(v["VALDATA"][:4])
        rows.append({"ano": ano, "valor": float(v["VALVALOR"])})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # mensal -> media anual; anual -> 1 valor por ano (mean e idempotente)
    df = df.groupby("ano", as_index=False)["valor"].mean()
    return df.sort_values("ano").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Deflator IPCA (a partir do raw nacional; segue deflacao_ipca.md)
# ---------------------------------------------------------------------------

def _indice_dez_ipca() -> pd.Series:
    """Indice IPCA acumulado em dezembro de cada ano (cumprod de 1+var/100)."""
    df = pd.read_csv(IPCA_RAW, dtype=str)
    df = df[pd.to_numeric(df["V"], errors="coerce").notna()].copy()
    df["ano"] = df["D2C"].str[:4].astype(int)
    df["mes"] = df["D2C"].str[4:].astype(int)
    df["var"] = df["V"].astype(float)
    df = df.sort_values(["ano", "mes"]).reset_index(drop=True)
    df["indice"] = (1 + df["var"] / 100).cumprod()
    return df[df["mes"] == 12].set_index("ano")["indice"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(force: bool = False, offline: bool = False) -> Path:
    out = DIR_PROCESSED / "drivers_macro_anual.csv"

    # 1. Baixar e consolidar series
    base = pd.DataFrame({"ano": range(ANO_MIN, ANO_MAX + 1)})
    for code, (col, per, filtra_go) in SERIES.items():
        valores = _baixar_serie(code, force=force, offline=offline)
        s = _para_anual(valores, per, filtra_go).rename(columns={"valor": col})
        n_jan = ((s["ano"] >= ANO_MIN) & (s["ano"] <= ANO_MAX)).sum() if not s.empty else 0
        print(f"  {code:20s} -> {col:24s} ({n_jan} anos na janela {ANO_MIN}-{ANO_MAX})")
        base = base.merge(s, on="ano", how="left")

    # 2. IPCA: fatores de deflacao -> dez/2024
    idx = _indice_dez_ipca()
    if 2024 not in idx.index:
        raise ValueError("IPCA precisa cobrir dez/2024.")
    fator_ano = (idx.loc[2024] / idx)                 # serie por ano -> dez/2024
    fator_2010 = float(idx.loc[2024] / idx.loc[2010]) # constante 2010 -> dez/2024
    print(f"  fator IPCA dez/2010 -> dez/2024: {fator_2010:.4f}")

    # 3. Credito rural GO: R$ 2010 -> R$ dez/2024
    base["credito_rural_go_real"] = base["credito_rural_go_2010"] * fator_2010

    # 4. Preco recebido em R$ real (valido 1994+, quando o cambio nominal e mensuravel)
    fmap = base["ano"].map(fator_ano)
    pode_brl = base["ano"] >= 1994
    for prod in ("soja", "boi"):
        nominal = base[f"preco_{prod}_usd"] * base["cambio_nominal_brl_usd"]   # R$/unid nominais do ano
        base[f"preco_recebido_{prod}_brl_real"] = np.where(pode_brl, nominal * fmap, np.nan)

    # 5. Preco recebido (INDICE real, janela completa): USD x REER, media 1985-2024 = 100
    for prod in ("soja", "boi"):
        comp = base[f"preco_{prod}_usd"] * base["cambio_real_efetivo"]
        base[f"preco_recebido_{prod}_idx"] = comp / comp.mean() * 100

    base["fonte"] = ("IPEA Data: IFS (precos commodity), GAC12 REER INPC-exp, "
                     "BM_ERV cambio nominal, CREATE credito rural GO; IPCA SIDRA 1737")

    cols = [
        "ano",
        "preco_soja_usd", "preco_boi_usd", "preco_milho_usd",
        "cambio_nominal_brl_usd", "cambio_real_efetivo",
        "preco_recebido_soja_idx", "preco_recebido_boi_idx",
        "preco_recebido_soja_brl_real", "preco_recebido_boi_brl_real",
        "credito_rural_go_2010", "credito_rural_go_real",
        "fonte",
    ]
    base = base[cols].sort_values("ano").reset_index(drop=True)
    base.to_csv(out, index=False, encoding="utf-8")
    print(f"[ok] {out.name}: {len(base)} linhas ({base['ano'].min()}-{base['ano'].max()})")

    # Sanidade: colunas-nucleo sem NaN na janela
    nucleo = ["preco_soja_usd", "preco_boi_usd", "cambio_real_efetivo",
              "preco_recebido_soja_idx", "credito_rural_go_real"]
    faltas = base[nucleo].isna().sum()
    if faltas.any():
        print("[aviso] NaN em colunas-nucleo:\n" + faltas[faltas > 0].to_string())
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Coleta drivers macro (Pipeline #37A)")
    p.add_argument("--force", action="store_true", help="rebaixa da API mesmo com cache")
    p.add_argument("--offline", action="store_true", help="so processa cache local")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        main(force=args.force, offline=args.offline)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
