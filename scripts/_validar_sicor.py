"""
Validação do coletor SICOR:
  1. Total Custeio + Invest por ano vs total UF correspondente (consistência interna)
  2. Quais munis ficaram de fora? Comparar contra a lista canônica de 246
  3. Qual a linha de Investimento sem cd_mun? Investigar
  4. Sanidade dos valores anuais (ordem de grandeza esperada)
"""
import sys
from pathlib import Path
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DIR = Path(__file__).parent / "data" / "processed"

print("=" * 70)
print("Validação SICOR")
print("=" * 70)

cust = pd.read_csv(DIR / "sicor_custeio_municipal.csv", encoding="utf-8")
inv  = pd.read_csv(DIR / "sicor_invest_municipal.csv", encoding="utf-8")
uf   = pd.read_csv(DIR / "sicor_uf_anual.csv", encoding="utf-8")
de_para = pd.read_csv(DIR / "sicor_de_para_municipio.csv", encoding="utf-8")

# 1. Consistência interna: soma municipal × soma UF, por ano e finalidade
print("\n[1] Consistência: total municipal vs total UF (R$ bi nominais)")
print("  Custeio:")
print("  ano   municipal     UF        razão")
for ano in sorted(cust["ano"].unique()):
    m = cust[cust["ano"] == ano]["valor"].sum() / 1e9
    u = uf[(uf["ano"] == ano) & (uf["finalidade"] == "Custeio")]["valor"].sum() / 1e9
    razao = m / u if u else 0
    print(f"  {ano}  {m:>9.2f}   {u:>9.2f}   {razao:.4f}")

print("  Investimento:")
for ano in sorted(inv["ano"].unique()):
    m = inv[inv["ano"] == ano]["valor"].sum() / 1e9
    u = uf[(uf["ano"] == ano) & (uf["finalidade"] == "Investimento")]["valor"].sum() / 1e9
    razao = m / u if u else 0
    print(f"  {ano}  {m:>9.2f}   {u:>9.2f}   {razao:.4f}")

print("  Comercializacao (só UF — não tem granularidade municipal):")
for ano in sorted(uf[uf["finalidade"] == "Comercializacao"]["ano"].unique()):
    u = uf[(uf["ano"] == ano) & (uf["finalidade"] == "Comercializacao")]["valor"].sum() / 1e9
    print(f"  {ano}              {u:>9.2f}")

# 2. Munis ausentes vs lista canônica
print("\n[2] Cobertura de municípios:")
ref = pd.read_csv(DIR / "sidra_pam1612_temporarias.csv", encoding="utf-8")
canon = set(ref["cd_mun"].unique())
print(f"  Lista canônica (PAM 1612): {len(canon)} munis")

cust_munis = set(cust["cd_mun"].dropna().astype(int).unique())
ausentes_cust = sorted(canon - cust_munis)
print(f"  Munis em Custeio: {len(cust_munis)}")
if ausentes_cust:
    print(f"  Ausentes em Custeio (têm SIDRA mas não SICOR): {ausentes_cust}")
    nomes = ref[ref["cd_mun"].isin(ausentes_cust)][["cd_mun", "nm_mun"]].drop_duplicates()
    print(nomes.to_string(index=False))

# Munis em Invest (via de-para)
inv_munis = set(de_para["cd_mun"].dropna().astype(int).unique())
ausentes_inv = sorted(canon - inv_munis)
print(f"  Munis em Investimento (via de-para): {len(inv_munis)}")
if ausentes_inv:
    print(f"  Ausentes em Investimento: {ausentes_inv}")

# 3. Linha de Investimento sem cd_mun — qual cd_municipio_bacen?
print("\n[3] Investimento sem match no de-para:")
inv_com_cdmun = inv.merge(de_para[["cd_municipio_bacen", "cd_mun"]],
                           on="cd_municipio_bacen", how="left")
sem = inv_com_cdmun[inv_com_cdmun["cd_mun"].isna()]
print(f"  {len(sem)} linhas sem match")
if len(sem):
    print(sem[["ano", "cd_municipio_bacen", "nm_mun", "valor"]].head(10).to_string(index=False))

# 4. Volume anual (em R$ bi) — sanidade
print("\n[4] Volume nominal anual (R$ bi) — ordem de grandeza:")
soma = (uf.groupby(["ano", "finalidade"])["valor"].sum() / 1e9).round(2).unstack()
print(soma.to_string())

# 5. Top 5 munis por valor 2024
print("\n[5] Top 10 munis Goiás por valor total 2024 (Custeio + Invest, R$ mi):")
total_2024 = (
    pd.concat([
        cust[cust["ano"] == 2024][["cd_mun", "nm_mun", "valor"]],
        inv.merge(de_para[["cd_municipio_bacen", "cd_mun"]],
                  on="cd_municipio_bacen", how="left")
        [lambda d: d["ano"] == 2024][["cd_mun", "nm_mun", "valor"]],
    ])
    .groupby(["cd_mun", "nm_mun"])["valor"].sum() / 1e6
).sort_values(ascending=False).head(10)
print(total_2024.to_string())
