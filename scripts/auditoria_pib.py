"""
Auditoria PIB — Pipeline #8 vs Pipeline #16
============================================

Diagnóstico empírico da discrepância PIB ~38% entre `painel_credito_lulc.csv`
(Pipeline #8) e `painel_unificado.parquet` (Pipeline #16).

A inspeção de código mostrou que ambos pipelines aplicam:
    pib_mil_reais (SIDRA 5938 var 37) -> ×1000 -> deflate(IPCA dez/2024)
em ordem invertida (×1000 antes em #8, depois em #16). Como `deflacionar()` é
multiplicação por escalar, a ordem é matematicamente irrelevante. Este script
calcula a razão empírica para descobrir a causa real.

Saídas:
    outputs/diagnosticos/auditoria_pib_ratio.csv  — uma linha por (cd_mun, ano)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_DIAG = ROOT / "outputs" / "diagnosticos"
DIR_DIAG.mkdir(parents=True, exist_ok=True)


def main() -> None:
    p8 = pd.read_csv(DIR_PROCESSED / "painel_credito_lulc.csv", encoding="utf-8")
    p16 = pd.read_parquet(DIR_PROCESSED / "painel_unificado.parquet")

    print(f"#8  painel_credito_lulc.csv:    {len(p8):,} linhas, anos {p8['ano'].min()}-{p8['ano'].max()}")
    print(f"#16 painel_unificado.parquet:   {len(p16):,} linhas, anos {p16['ano'].min()}-{p16['ano'].max()}")
    print(f"#8  colunas PIB:  {[c for c in p8.columns  if 'pib' in c.lower()]}")
    print(f"#16 colunas PIB:  {[c for c in p16.columns if 'pib' in c.lower()]}")

    col8 = "pib_real_rs"
    col16 = "pib_real_rs"
    a = p8[["cd_mun", "ano", col8]].rename(columns={col8: "pib_8"})
    b = p16[["cd_mun", "ano", col16]].rename(columns={col16: "pib_16"})
    j = a.merge(b, on=["cd_mun", "ano"], how="inner")
    j = j.dropna(subset=["pib_8", "pib_16"])
    j = j[j["pib_16"] > 0]
    j["ratio"] = j["pib_8"] / j["pib_16"]

    print(f"\nLinhas comparáveis: {len(j):,}")
    print(f"\n=== Distribuição da razão pib_8 / pib_16 ===")
    print(j["ratio"].describe())

    print(f"\n=== Mediana por ano ===")
    print(j.groupby("ano")["ratio"].median().to_string())

    print(f"\n=== Variação por município (mediana, depois describe) ===")
    by_mun = j.groupby("cd_mun")["ratio"].median()
    print(by_mun.describe())

    print(f"\n=== 5 maiores razões ===")
    print(j.nlargest(5, "ratio")[["cd_mun", "ano", "pib_8", "pib_16", "ratio"]].to_string(index=False))

    print(f"\n=== 5 menores razões ===")
    print(j.nsmallest(5, "ratio")[["cd_mun", "ano", "pib_8", "pib_16", "ratio"]].to_string(index=False))

    out = DIR_DIAG / "auditoria_pib_ratio.csv"
    j.to_csv(out, index=False)
    print(f"\n[OK] Salvo: {out}")

    median = j["ratio"].median()
    std = j["ratio"].std()
    print(f"\n=== DIAGNOSTICO ===")
    if abs(median - 1.0) < 0.01 and std < 0.01:
        print(f"Razao ~ 1.0 (mediana={median:.4f}, std={std:.4f}) -- SEM divergencia empirica.")
    elif std < 0.01:
        print(f"Razao CONSTANTE = {median:.4f} (std={std:.4f}) -- divergencia por fator escalar.")
    else:
        var_ano = j.groupby("ano")["ratio"].median().std()
        var_mun = by_mun.std()
        print(f"Razao variavel (mediana={median:.4f}, std={std:.4f}).")
        print(f"  Variacao entre anos:       {var_ano:.4f}")
        print(f"  Variacao entre municipios: {var_mun:.4f}")


if __name__ == "__main__":
    main()
