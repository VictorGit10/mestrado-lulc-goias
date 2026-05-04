"""Verificação rápida dos CSVs processados de Goiás."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import pandas as pd

print('=== PASTAGEM ===')
df_p = pd.read_csv(ROOT / 'data/processed/pastagem_goias_anual.csv')
idx_pico = df_p['area_pastagem_ha'].idxmax()
print(f"1985: {df_p[df_p.ano==1985]['area_pastagem_ha'].values[0]/1e6:.2f} Mha")
print(f"Pico: {df_p['area_pastagem_ha'].max()/1e6:.2f} Mha em {int(df_p.loc[idx_pico, 'ano'])}")
print(f"2024: {df_p[df_p.ano==2024]['area_pastagem_ha'].values[0]/1e6:.2f} Mha")

print()
print('=== REBANHO ===')
df_r = pd.read_csv(ROOT / 'data/processed/rebanho_bovino_goias.csv')
idx_pico_r = df_r['bovinos'].idxmax()
print(f"1985: {df_r[df_r.ano==1985]['bovinos'].values[0]/1e6:.2f} Mi cab")
print(f"Pico: {df_r['bovinos'].max()/1e6:.2f} Mi em {int(df_r.loc[idx_pico_r, 'ano'])}")
print(f"2024: {df_r[df_r.ano==2024]['bovinos'].values[0]/1e6:.2f} Mi cab")

print()
print('=== LOTACAO ===')
df_l = pd.read_csv(ROOT / 'data/processed/lotacao_implicita_goias.csv')
idx_pico_l = df_l['lotacao'].idxmax()
print(f"1985: {df_l[df_l.ano==1985]['lotacao'].values[0]:.2f} bois/ha")
print(f"Pico: {df_l['lotacao'].max():.2f} em {int(df_l.loc[idx_pico_l, 'ano'])}")
print(f"2024: {df_l[df_l.ano==2024]['lotacao'].values[0]:.2f} bois/ha")

print()
print('=== PIB AGRO (participacao %) ===')
df_a = pd.read_csv(ROOT / 'data/processed/pib_agro_goias.csv')
print(df_a[['ano','va_agro_real_rs','pib_real_rs','participacao_pct']].to_string(index=False))
print(f"\nMin participacao: {df_a['participacao_pct'].min():.1f}% em {int(df_a.loc[df_a['participacao_pct'].idxmin(), 'ano'])}")
print(f"Max participacao: {df_a['participacao_pct'].max():.1f}% em {int(df_a.loc[df_a['participacao_pct'].idxmax(), 'ano'])}")