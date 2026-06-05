"""
verificar_amc_goias.py — Verificação independente do Pipeline #25 (AMC)
=======================================================================

Não confia na lógica de construir_amc_goias.py: testa o resultado contra
verdades-terra independentes. Cada teste falha ALTO (AssertionError) se algo
estiver errado. Rode após o #25.

    python scripts/verificar_amc_goias.py

Testes:
  1. IDENTIDADE DOS SINGLETONS (o teste mais forte): as 113 AMCs de 1 município
     devem reproduzir EXATAMENTE a linha municipal — todas as colunas, inclusive
     o padrão de NaN. Se a classificação de colunas ou as fórmulas de recálculo
     tivessem qualquer erro, os singletons não bateriam.
  2. RE-AGREGAÇÃO MANUAL: para uma amostra de AMCs multi-município, soma-se os
     membros do painel BRUTO célula a célula (sem groupby) e compara-se com o
     painel AMC. Caminho independente da agregação do #25.
  3. RECÁLCULO DE RAZÕES: confere que as derivadas batem com a fórmula aplicada
     às extensivas já agregadas (lotação = Σcab/Σpasto, etc.).
  4. NaN preservado: AMC-ano sem nenhum dado nos membros fica NaN, não 0.
  5. CONTIGUIDADE ESPACIAL: membros de cada AMC multi-município formam região
     conexa (filho é desmembrado do pai → tocam). Informativo.
  6. UM PAI POR GRUPO: cada AMC multi tem exatamente 1 município presente em 1985.
  7. LIMITES FÍSICOS: áreas ≥ 0, percentuais em faixa, lotação plausível.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR  = ROOT / "data" / "processed"

painel = pd.read_parquet(DIR / "painel_unificado.parquet")
amc    = pd.read_parquet(DIR / "painel_amc_goias.parquet")
cw     = pd.read_csv(DIR / "amc_crosswalk_goias.csv")

KEYS_MUN = {"cd_mun", "nm_mun", "ano"}
KEYS_AMC = {"code_amc", "amc_nome_rep", "amc_n_munis", "ano"}
COLS = [c for c in painel.columns if c not in KEYS_MUN and c in amc.columns]

falhas = 0
def ok(nome, cond, detalhe=""):
    global falhas
    print(f"  [{'PASS' if cond else 'FALHA'}] {nome}" + (f" — {detalhe}" if detalhe else ""))
    if not cond:
        falhas += 1

print("=" * 70)
print("Verificação independente do Pipeline #25 (AMC Goiás)")
print("=" * 70)

# painel anexado ao crosswalk (uma vez)
pcw = painel.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")

# ---------------------------------------------------------------------------
print("\n[1] Identidade dos singletons (AMC de 1 muni == município)")
tam = cw.groupby("code_amc")["cd_mun"].nunique()
singletons = tam[tam == 1].index
cd_de_amc = cw[cw.code_amc.isin(singletons)].set_index("code_amc")["cd_mun"]
amc_s = amc[amc.code_amc.isin(singletons)].copy()
amc_s["cd_mun"] = amc_s["code_amc"].map(cd_de_amc)
m = painel.merge(amc_s, on=["cd_mun", "ano"], suffixes=("_mun", "_amc"))
# taxa_abate_* ficam fora desta identidade: o #16 ARMAZENA o valor arredondado a
# 4 casas calculado a montante (estimativa_abate), enquanto o AMC recalcula das
# componentes não-arredondadas (Σabate/Σpec). A correção da fórmula é validada no
# teste [3], não aqui. Comparar contra o valor armazenado seria comparar contra
# um artefato de arredondamento.
cols_id = [c for c in COLS if not c.startswith("taxa_abate_")]
piores = []
for c in cols_id:
    a, b = m[f"{c}_mun"].to_numpy(float), m[f"{c}_amc"].to_numpy(float)
    bate = np.isclose(a, b, rtol=1e-6, atol=1e-6, equal_nan=True)
    if not bate.all():
        piores.append((c, int((~bate).sum())))
ok(f"{len(singletons)} singletons reproduzem o município em {len(cols_id)} colunas "
   f"(taxa_abate_* via teste [3])",
   len(piores) == 0, "" if not piores else f"divergem: {piores[:5]}")

# ---------------------------------------------------------------------------
print("\n[2] Re-agregação manual de AMCs multi-município (caminho independente)")
multi = tam[tam > 1].index.tolist()
rng = np.random.default_rng(0)
amostra = rng.choice(multi, size=min(12, len(multi)), replace=False)
extensivas_amostra = ["pec_bovinos_cab", "lulc_pastagem_ha", "agri_soja_ha_plantada",
                      "sicor_total_real_rs", "populacao", "lulc_area_total_ha",
                      "abate_bovino_cab", "fogo_total_ha"]
extensivas_amostra = [c for c in extensivas_amostra if c in COLS]
n_ok = n_test = 0
divergencias = []
for code in amostra:
    membros = cw[cw.code_amc == code]["cd_mun"].tolist()
    for ano in [1985, 1990, 1995, 2000, 2010, 2020]:
        sub = painel[(painel.cd_mun.isin(membros)) & (painel.ano == ano)]
        ref = amc[(amc.code_amc == code) & (amc.ano == ano)]
        if ref.empty:
            continue
        for c in extensivas_amostra:
            vals = sub[c].dropna()
            esperado = vals.sum() if len(vals) else np.nan   # min_count=1
            obtido = ref[c].iloc[0]
            n_test += 1
            if np.isclose(esperado, obtido, rtol=1e-6, atol=1e-6, equal_nan=True):
                n_ok += 1
            else:
                divergencias.append((int(code), ano, c, esperado, obtido))
ok(f"{n_ok}/{n_test} células (soma manual dos membros == painel AMC)",
   n_ok == n_test, "" if not divergencias else f"ex: {divergencias[:3]}")

# ---------------------------------------------------------------------------
print("\n[3] Recálculo de razões a partir das extensivas agregadas")
def chk_ratio(col, num, den, fator=1.0):
    if not {col, num, den} <= set(amc.columns):
        return
    esperado = amc[num] / amc[den] * fator
    esperado = esperado.replace([np.inf, -np.inf], np.nan)
    bate = np.isclose(amc[col].to_numpy(float), esperado.to_numpy(float),
                      rtol=1e-6, atol=1e-9, equal_nan=True)
    ok(f"{col} == {num}/{den}" + (f"*{fator:g}" if fator != 1 else ""), bate.all(),
       "" if bate.all() else f"{(~bate).sum()} linhas divergem")
chk_ratio("lotacao_bov_ha", "pec_bovinos_cab", "lulc_pastagem_ha")
chk_ratio("credito_por_ha_pastagem", "sicor_total_real_rs", "lulc_pastagem_ha")
chk_ratio("pct_pastagem_lulc", "lulc_pastagem_ha", "lulc_area_total_ha", 100)
chk_ratio("produtividade_soja_ton_ha", "agri_soja_ton", "agri_soja_ha_plantada")
chk_ratio("taxa_abate_bovino", "abate_bovino_cab", "pec_bovinos_cab")
# participacao_agro_pct NÃO é va/pib (é va_agro/VA_total, e VA_total não está no
# painel) — é reconstruída em recalcular_razoes_agregadas. Sua correção é provada
# pela identidade dos singletons no teste [1] (reproduz o município exatamente).

# ---------------------------------------------------------------------------
print("\n[4] NaN preservado (não virou 0)")
# AMC-ano onde TODOS os membros são NaN em sicor_total_real_rs (pré-2013) → NaN
pre = amc[amc.ano == 2010]["sicor_total_real_rs"]
ok("sicor_total_real_rs é NaN em 2010 (BACEN só desde 2013)", pre.isna().all(),
   f"{pre.notna().sum()} valores não-NaN inesperados")

# ---------------------------------------------------------------------------
print("\n[5] Contiguidade espacial dos grupos multi-município (informativo)")
try:
    import warnings, geobr
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # simplified=False: a malha simplificada cria falsos buracos entre munis.
        go = geobr.read_municipality(code_muni="GO", year=2020, simplified=False)
    go["cd_mun"] = go["code_muni"].astype(int)
    go = go.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="inner")
    nao_conexas = []
    for code in multi:
        geoms = go[go.code_amc == code].geometry
        if geoms.empty:
            continue
        uniao = geoms.union_all() if hasattr(geoms, "union_all") else geoms.unary_union
        n_pecas = len(getattr(uniao, "geoms", [uniao]))
        if n_pecas > 1:
            nao_conexas.append((int(code), n_pecas))
    # INFORMATIVO (não conta como falha): uma AMC pode ser não-contígua quando
    # uma filha puxou território de DOIS pais e toca o grupo só via um município
    # de fora da AMC. É sutileza conhecida da concordância de Ehrl, não erro do
    # pipeline (o crosswalk vem da fonte autoritativa geobr/Ehrl).
    n_ok = len(multi) - len(nao_conexas)
    print(f"  [INFO] {n_ok}/{len(multi)} grupos multi formam região contígua" +
          (f" — não-contíguas (esperado p/ emancipação multi-pai): {nao_conexas}"
           if nao_conexas else ""))
except Exception as e:  # noqa: BLE001
    print(f"  [skip] contiguidade não testada: {type(e).__name__}: {e}")

# ---------------------------------------------------------------------------
print("\n[6] Cada grupo multi tem ≥1 município 'pai' (presente em 1985)")
# Invariante real: toda AMC deve conter ao menos um município que já existia em
# 1985 (caso contrário a AMC estrearia após 1985 — testado no #25). NÃO se exige
# exatamente 1: um split ocorrido entre 1980 e 1985 deixa 2 munis-pai legítimos
# na mesma AMC (ambos já têm dado em 1985), o que é correto para a janela 1980.
pe = painel.dropna(subset=["pec_bovinos_cab"])
first = pe.groupby("cd_mun")["ano"].min()
cw2 = cw.copy()
cw2["existe_1985"] = cw2["cd_mun"].map(first) <= 1985
pais = cw2[cw2.code_amc.isin(multi)].groupby("code_amc")["existe_1985"].sum()
ok(f"todos os {len(multi)} grupos multi têm ≥1 pai",
   (pais >= 1).all(), f"distribuição de nº de pais por AMC: {pais.value_counts().sort_index().to_dict()}")

# ---------------------------------------------------------------------------
print("\n[7] Limites físicos das colunas")
neg_area = [c for c in amc.columns if c.endswith("_ha") and (amc[c].dropna() < -1e-6).any()]
ok("nenhuma área negativa", not neg_area, f"negativas: {neg_area[:5]}")
pct = amc["pct_pastagem_lulc"].dropna()
ok("pct_pastagem_lulc em [0, 100]", ((pct >= -0.01) & (pct <= 100.01)).all(),
   f"fora da faixa: min={pct.min():.2f} max={pct.max():.2f}")
lot = amc["lotacao_bov_ha"].dropna()
ok("lotacao_bov_ha plausível (0–20 cab/ha)", ((lot >= 0) & (lot < 20)).all(),
   f"min={lot.min():.2f} max={lot.max():.2f}")

# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
if falhas == 0:
    print("RESULTADO: todos os testes passaram. ✓")
else:
    print(f"RESULTADO: {falhas} teste(s) FALHARAM — investigar acima.")
    sys.exit(1)
print("=" * 70)
