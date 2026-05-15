"""
coleta_pib_uf_ipea.py -- Coleta PIB e VAB agropecuario UF (Goias) via IPEA Data
==============================================================================

Baixa series anuais estaduais do IPEA Data API para Goias (UF 52), cobrindo
1985-2023 sem lacunas. O objetivo e ter uma serie UF nativa (Contas Regionais
IBGE, encadeada pelo IPEA) ao lado da serie agregada municipal SIDRA 5938
que so existe a partir de 2002.

Series IPEA usadas:
  - PIBE     -- PIB Estadual a precos de mercado (precos de 2010), R$ mil
  - PIBAGE   -- VAB Estadual agropecuaria (precos de 2010), R$ mil
  - PIBPMCE  -- PIB Estadual a precos correntes (nominal), R$ mil

As series PIBE/PIBAGE ja vem deflacionadas para precos de 2010 pelo IPEA
(deflator implicito do PIB nacional 1939-1985, indice de volume 1986-1995,
serie encadeada Contas Regionais 2010 a partir de 1996). Este script faz
apenas a conversao final: R$ de 2010 -> R$ de dezembro/2024 via IPCA
(mesmo procedimento de Textos/metodologia/deflacao_ipca.md).

PIBPMCE (nominal) e mantido apenas para referencia -- nao e deflacionado
porque pre-1994 atravessa varias mudancas de moeda (Cruzado, Cruzado Novo,
Cruzeiro Real, Real), conversao nao-trivial.

Endpoint: http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='<code>')

Saida:
  data/processed/pib_uf_ipea_goias.csv

Schema:
  ano, pib_uf_real_rs, va_agro_uf_real_rs, participacao_uf_pct,
  pib_uf_nominal_2010_mil_rs, va_agro_uf_nominal_2010_mil_rs,
  pib_uf_corrente_mil_rs, fonte

  pib_uf_real_rs                  -- PIB UF em R$ de dez/2024
  va_agro_uf_real_rs              -- VAB agro UF em R$ de dez/2024
  participacao_uf_pct             -- VAB agro / PIB em %
  pib_uf_nominal_2010_mil_rs      -- bruto IPEA, antes do redeflator (R$ mil de 2010)
  va_agro_uf_nominal_2010_mil_rs  -- bruto IPEA (R$ mil de 2010)
  pib_uf_corrente_mil_rs          -- nominal historico IPEA (R$ mil correntes da epoca)
  fonte                           -- 'IPEA/IBGE Contas Regionais (PIBE+PIBAGE+PIBPMCE)'

Como rodar:
    python coleta_pib_uf_ipea.py            # busca + processa
    python coleta_pib_uf_ipea.py --force    # rebaixa da API mesmo com cache
    python coleta_pib_uf_ipea.py --offline  # so processa cache local
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw" / "pib_uf_ipea"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

CODIGO_UF_GO = "52"
ANO_MIN = 1985  # ponto a partir do qual a serie IPEA e contigua

IPEA_API_BASE = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{code}')"

# code IPEA -> (nome saida bruta R$ 2010 mil, deflacionar?)
SERIES_IPEA = {
    "PIBE":    ("pib_uf_nominal_2010_mil_rs",   True),   # PIB UF real (2010)
    "PIBAGE":  ("va_agro_uf_nominal_2010_mil_rs", True), # VAB agro UF real (2010)
    "PIBPMCE": ("pib_uf_corrente_mil_rs",        False), # PIB UF nominal (corrente)
}

IPCA_CSV = DIR_PROCESSED / "sidra_1737_ipca.csv"


# ---------------------------------------------------------------------------
# Download IPEA
# ---------------------------------------------------------------------------

def _baixar_serie(sercodigo: str, force: bool = False) -> list[dict]:
    """Baixa uma serie do IPEA Data, com cache em data/raw/pib_uf_ipea/."""
    cache = DIR_RAW / f"{sercodigo}.json"
    if cache.exists() and not force:
        with cache.open("r", encoding="utf-8") as f:
            return json.load(f)

    url = IPEA_API_BASE.format(code=sercodigo)
    print(f"  IPEA API: {sercodigo}...")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    valores = r.json().get("value", [])
    with cache.open("w", encoding="utf-8") as f:
        json.dump(valores, f)
    print(f"    {len(valores)} pontos baixados, cache em {cache.name}")
    return valores


def _filtrar_goias(valores: list[dict]) -> pd.DataFrame:
    """Filtra TERCODIGO=52 (Goias) e converte para DataFrame[ano, valor]."""
    rows = []
    for v in valores:
        if str(v.get("TERCODIGO", "")) != CODIGO_UF_GO:
            continue
        ano = int(v["VALDATA"][:4])
        if ano < ANO_MIN:
            continue
        rows.append({"ano": ano, "valor": v["VALVALOR"]})
    df = pd.DataFrame(rows).sort_values("ano").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Deflator IPCA (2010 -> dez/2024)
# ---------------------------------------------------------------------------

def _fator_deflator_2010_para_2024() -> float:
    """Calcula fator IPCA: R$ dez/2010 -> R$ dez/2024.

    fator = indice_acum[dez/2024] / indice_acum[dez/2010]
    """
    ipca = pd.read_csv(IPCA_CSV)
    dez = ipca[ipca["mes"] == 12].set_index("ano")["indice_acum"]
    if 2010 not in dez.index or 2024 not in dez.index:
        raise ValueError(
            f"IPCA acumulado precisa cobrir dez/2010 e dez/2024. "
            f"Disponivel: {dez.index.min()}-{dez.index.max()}."
        )
    return float(dez.loc[2024] / dez.loc[2010])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(force: bool = False, offline: bool = False) -> Path:
    out = DIR_PROCESSED / "pib_uf_ipea_goias.csv"
    if out.exists() and not force and not offline:
        print(f"[ok] {out.name} ja existe (use --force para reprocessar).")
        return out

    # Baixar series
    dfs = {}
    for code, (col_bruta, _) in SERIES_IPEA.items():
        if offline:
            cache = DIR_RAW / f"{code}.json"
            if not cache.exists():
                raise FileNotFoundError(
                    f"--offline mas cache {cache} nao existe; "
                    f"rode sem --offline pelo menos uma vez."
                )
            with cache.open("r", encoding="utf-8") as f:
                valores = json.load(f)
        else:
            valores = _baixar_serie(code, force=force)
        df = _filtrar_goias(valores).rename(columns={"valor": col_bruta})
        dfs[code] = df
        print(f"  {code}: {len(df)} anos GO ({df['ano'].min()}-{df['ano'].max()})")

    # Merge sobre ano
    df = dfs["PIBE"]
    for code in ("PIBAGE", "PIBPMCE"):
        df = df.merge(dfs[code], on="ano", how="outer")
    df = df.sort_values("ano").reset_index(drop=True)

    # Deflacionar 2010 -> dez/2024
    fator = _fator_deflator_2010_para_2024()
    print(f"  fator IPCA dez/2010 -> dez/2024: {fator:.4f}")

    # PIBE e PIBAGE vem em R$ mil (precos 2010). Converter: mil R$ * 1000 * fator = R$
    df["pib_uf_real_rs"]     = df["pib_uf_nominal_2010_mil_rs"]    * 1000 * fator
    df["va_agro_uf_real_rs"] = df["va_agro_uf_nominal_2010_mil_rs"] * 1000 * fator

    # Participacao agro (em precos 2010 -- equivalente a participacao real)
    df["participacao_uf_pct"] = (
        df["va_agro_uf_nominal_2010_mil_rs"] / df["pib_uf_nominal_2010_mil_rs"] * 100
    )

    df["fonte"] = "IPEA/IBGE Contas Regionais (PIBE+PIBAGE+PIBPMCE)"

    # Reordenar
    cols = [
        "ano",
        "pib_uf_real_rs", "va_agro_uf_real_rs", "participacao_uf_pct",
        "pib_uf_nominal_2010_mil_rs", "va_agro_uf_nominal_2010_mil_rs",
        "pib_uf_corrente_mil_rs",
        "fonte",
    ]
    df = df[cols]

    df.to_csv(out, index=False)
    print(f"[ok] {out.name}: {len(df)} linhas ({df['ano'].min()}-{df['ano'].max()})")
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1] if __doc__ else "")
    p.add_argument("--force", action="store_true", help="rebaixa mesmo com cache")
    p.add_argument("--offline", action="store_true", help="so processa cache local")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        main(force=args.force, offline=args.offline)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
