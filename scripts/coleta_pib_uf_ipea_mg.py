"""coleta_pib_uf_ipea_mg.py — Coleta PIB e VAB agropecuario UF (Minas Gerais) via IPEA Data
================================================================================

Adaptado de coleta_pib_uf_ipea.py para Minas Gerais (UF 31).
Filtra as series PIBE, PIBAGE, PIBPMCE nacionais por TERCODIGO=31.

Saida:
  data/processed/pib_uf_ipea_mg.csv

Como rodar:
    python coleta_pib_uf_ipea_mg.py            # busca + processa
    python coleta_pib_uf_ipea_mg.py --offline  # so processa cache local
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT          = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw" / "pib_uf_ipea"
DIR_PROCESSED = ROOT / "data" / "processed"

CODIGO_UF_MG = "31"
ANO_MIN = 1985

IPEA_API_BASE = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{code}')"

SERIES_IPEA = {
    "PIBE":    ("pib_uf_nominal_2010_mil_rs",   True),
    "PIBAGE":  ("va_agro_uf_nominal_2010_mil_rs", True),
    "PIBPMCE": ("pib_uf_corrente_mil_rs",        False),
}

IPCA_CSV = DIR_PROCESSED / "sidra_1737_ipca_mg.csv"


def baixar_serie(codigo: str, force: bool = False) -> pd.DataFrame:
    cache = DIR_RAW / f"{codigo}.json"
    if cache.exists() and not force:
        print(f"  [cache] {codigo}.json")
        with open(cache, "r", encoding="utf-8") as f:
            rows = json.load(f)
    else:
        import requests
        url = IPEA_API_BASE.format(code=codigo)
        print(f"  [...] baixando {codigo} ...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        rows = r.json()
        if isinstance(rows, dict) and "value" in rows:
            rows = rows["value"]
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        print(f"  [OK] {codigo}.json ({len(rows):,} registros)")

    df = pd.DataFrame(rows)
    df["VALDATA"] = pd.to_datetime(df["VALDATA"], utc=True)
    df["ano"] = df["VALDATA"].dt.year
    df["TERCODIGO"] = df["TERCODIGO"].astype(str)
    return df


def deflacionar_ipca(df_real_2010: pd.DataFrame, ipca: pd.DataFrame) -> pd.DataFrame:
    ipca["ano"] = ipca["ano"].astype(int)
    ipca_mensal = ipca.groupby("ano")["var_mensal_pct"].sum().reset_index()
    ipca_mensal.columns = ["ano", "ipca_anual_pct"]
    base_ano = 2024
    ipca_acum = ipca_mensal.copy()
    ipca_acum["fator"] = 1.0
    anos_disp = ipca_acum[ipca_acum["ano"] <= base_ano].sort_values("ano")
    cumul = 1.0
    fatores = {}
    for _, row in anos_disp.iterrows():
        cumul *= (1 + row["ipca_anual_pct"] / 100)
        fatores[int(row["ano"])] = cumul
    fator_base = fatores.get(base_ano, 1.0)

    df = df_real_2010.merge(ipca_acum[["ano"]], on="ano", how="left")
    df["fator_deflacao"] = df["ano"].map(fatores) / fator_base
    df["valor_deflacionado"] = df["valor_nominal_2010_mil"] * df["fator_deflacao"]
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Rebaixa da API")
    parser.add_argument("--offline", action="store_true", help="So processa cache local")
    args = parser.parse_args()

    print(f"Coleta PIB UF IPEA — Minas Gerais (UF={CODIGO_UF_MG})")

    dfs = {}
    for codigo, (col_nome, deflacionar) in SERIES_IPEA.items():
        df = baixar_serie(codigo, force=args.force)
        mg = df[df["TERCODIGO"] == CODIGO_UF_MG].copy()
        mg = mg[mg["ano"] >= ANO_MIN].sort_values("ano")
        mg = mg.rename(columns={"VALVALOR": col_nome})
        mg[col_nome] = pd.to_numeric(mg[col_nome], errors="coerce")
        dfs[codigo] = mg[["ano", col_nome]].reset_index(drop=True)
        print(f"  {codigo} MG: {len(mg)} anos ({mg['ano'].min()}-{mg['ano'].max()})")

    pib = dfs["PIBE"]
    vab = dfs["PIBAGE"]
    nominal = dfs["PIBPMCE"]

    resultado = pib.merge(vab, on="ano", how="outer").merge(nominal, on="ano", how="outer")
    resultado = resultado.sort_values("ano").reset_index(drop=True)

    # Calcular participacao do VAB agro
    resultado["participacao_uf_pct"] = (
        resultado["va_agro_uf_nominal_2010_mil_rs"] /
        resultado["pib_uf_nominal_2010_mil_rs"] * 100
    )

    # Deflacionar via IPCA
    if IPCA_CSV.exists():
        ipca = pd.read_csv(IPCA_CSV)
        # Deflacionar PIB e VAB agro
        pib_real = resultado[["ano", "pib_uf_nominal_2010_mil_rs"]].rename(
            columns={"pib_uf_nominal_2010_mil_rs": "valor_nominal_2010_mil"})
        pib_defl = deflacionar_ipca(pib_real, ipca)
        resultado["pib_uf_real_rs"] = pib_defl["valor_deflacionado"] * 1000  # mil -> R$

        vab_real = resultado[["ano", "va_agro_uf_nominal_2010_mil_rs"]].rename(
            columns={"va_agro_uf_nominal_2010_mil_rs": "valor_nominal_2010_mil"})
        vab_defl = deflacionar_ipca(vab_real, ipca)
        resultado["va_agro_uf_real_rs"] = vab_defl["valor_deflacionado"] * 1000
    else:
        resultado["pib_uf_real_rs"] = resultado["pib_uf_nominal_2010_mil_rs"] * 1000
        resultado["va_agro_uf_real_rs"] = resultado["va_agro_uf_nominal_2010_mil_rs"] * 1000
        print("[AVISO] IPCA nao encontrado. Usando valores de 2010 sem deflacao.")

    resultado["fonte"] = "IPEA/IBGE Contas Regionais (PIBE+PIBAGE+PIBPMCE)"

    out_cols = ["ano", "pib_uf_real_rs", "va_agro_uf_real_rs", "participacao_uf_pct",
                "pib_uf_nominal_2010_mil_rs", "va_agro_uf_nominal_2010_mil_rs",
                "pib_uf_corrente_mil_rs", "fonte"]
    resultado = resultado[out_cols]
    resultado = resultado.sort_values("ano").reset_index(drop=True)

    out_path = DIR_PROCESSED / "pib_uf_ipea_mg.csv"
    resultado.to_csv(out_path, index=False)
    print(f"\n  -> {out_path.name} ({len(resultado)} anos, {resultado['ano'].min()}-{resultado['ano'].max()})")


if __name__ == "__main__":
    main()