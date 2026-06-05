"""
Pipeline #25 — Áreas Mínimas Comparáveis (AMC) de Goiás, 1985–2024
==================================================================

PROBLEMA QUE RESOLVE
--------------------
O painel municipal (#16, `painel_unificado.parquet`) cruza dois regimes de dados
que se comportam de formas opostas no tempo:

  - LULC MapBiomas (raster): recorta o polígono ATUAL do município sobre a imagem
    de cada ano → os 246 municípios têm série completa 1985–2024.
  - SIDRA/PPM/PAM/PIB/SICOR (pesquisa): tabulado pelo município COMO ELE EXISTIA
    no ano da coleta → municípios criados depois de 1985 têm NaN antes de existir.

Medição empírica (ver validação abaixo): **62 dos 246 municípios de Goiás (25%)**
só aparecem no SIDRA depois de 1985 (ondas de 1989, 1993, 1997 e 2001). Para os
municípios-PAI, isso produz quedas espúrias de 50–80% no rebanho/produção no ano
em que um filho se emancipa — não é fenômeno econômico/ambiental, é perda de
território. Isso contamina:
  - razões LULC×pesquisa (lotação, crédito/ha), e
  - análises em primeiras diferenças e DiD que atravessam 1989/1993/1997.

SOLUÇÃO: ÁREAS MÍNIMAS COMPARÁVEIS (AMC)
----------------------------------------
Uma AMC agrupa cada município-pai com seus filhos numa unidade de território
CONSTANTE ao longo de toda a janela. Agregando AMBOS os regimes de dados ao nível
de AMC, toda série passa a se referir ao mesmo território em todos os anos.

Metodologia padrão e citável: **Philipp Ehrl (2017), "Minimum comparable areas
for the period 1872–2010", Estudos Econômicos** (doi:10.1590/0101-416147182phe).
A concordância vem pronta no `geobr.read_comparable_areas(start_year=1980,
end_year=2010)` — a coluna `list_code_muni_2010` lista os municípios de cada AMC.

Escolha de janela: **start_year=1980** antecede TODAS as emancipações da nossa
janela (1989+), garantindo que todo desmembramento de 1985–2024 seja colapsado.
**end_year=2010** basta porque Goiás não criou municípios novos após ~2001.
Resultado: 246 municípios → 166 AMCs (53 grupos pai+filhos, 113 unidades 1:1).

ESTRATÉGIA DE DOIS TRILHOS (ver metodologia/areas_minimas_comparaveis.md)
  - AMC = unidade canônica para análises LONGITUDINAIS (primeiras diferenças,
    painel com efeitos fixos, DiD, periodização, "tal área cresceu/encolheu X%").
  - Os 246 municípios atuais (#16) permanecem para análises TRANSVERSAIS e do
    período recente (Censo 2017, mapas de 2024), onde a malha é estável.
Por isso este pipeline NÃO altera `painel_unificado.parquet` — gera um painel
paralelo `painel_amc_goias.parquet`.

REGRAS DE AGREGAÇÃO (o coração do pipeline)
-------------------------------------------
  1. EXTENSIVAS (somáveis): hectares LULC, cabeças, toneladas, mil litros, kg,
     R$ (PIB, VA, SICOR), população, abate (cab/kg), fogo (ha), contagens do
     Censo, volumes Trase. → soma por (code_amc, ano), com min_count=1 (se TODOS
     os municípios da AMC são NaN naquele ano/coluna, o resultado fica NaN, não 0).

     POR QUE A SOMA RESOLVE O PROBLEMA: antes da emancipação o filho é NaN e o pai
     carrega o valor do território inteiro; a soma = valor do pai = total correto.
     Depois, pai e filho têm valores e a soma = total correto. O agregado de AMC
     é portanto CONTÍNUO, sem o salto espúrio.

  2. DERIVADAS (razões/densidades): NUNCA somadas nem promediadas ingenuamente —
     são RECALCULADAS a partir das extensivas já agregadas, com as mesmas fórmulas
     de `derivar_metricas` do #16. Ex.: lotacao = Σcabeças / Σpasto.

  3. RAZÕES DO CENSO (pct_*, lotação): recalculadas como MÉDIA PONDERADA exata,
     reconstruindo o numerador/denominador implícito de cada município antes de
     somar (não há perda de informação).

  4. CONTAGENS DE ENTIDADES TRASE (n_exporters, n_hubs, n_frigorificos): somadas,
     com a RESSALVA de que uma entidade atuante em >1 município é contada mais de
     uma vez (proxy, limite superior). Trase é camada secundária.

ENTRADAS
    data/processed/painel_unificado.parquet   (Pipeline #16)
    geobr.read_comparable_areas(1980, 2010)   (download, cacheado no crosswalk)

SAÍDAS
    data/processed/amc_crosswalk_goias.csv     (cd_mun, nm_mun, code_amc, amc_n_munis)
    data/processed/painel_amc_goias.parquet    (166 AMCs × 40 anos)  [+ .csv cortesia]
    data/processed/amc_goias.gpkg              (geometria dissolvida, p/ mapas; opcional)
    outputs/diagnosticos/amc_impacto_goias.csv (antes×depois: saltos espúrios sumiram?)

COMO RODAR
    python scripts/construir_amc_goias.py            # usa crosswalk cacheado se existir
    python scripts/construir_amc_goias.py --force    # rebaixa a AMC do geobr

Depende de: Pipeline #16 (painel_unificado.parquet).
Quando foi feito: 2026-06-04.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_DIAG      = ROOT / "outputs" / "diagnosticos"
for d in (DIR_PROCESSED, DIR_DIAG):
    d.mkdir(parents=True, exist_ok=True)

ARQ_PAINEL    = DIR_PROCESSED / "painel_unificado.parquet"
ARQ_CROSSWALK = DIR_PROCESSED / "amc_crosswalk_goias.csv"
ARQ_PAINEL_AMC_PARQUET = DIR_PROCESSED / "painel_amc_goias.parquet"
ARQ_PAINEL_AMC_CSV     = DIR_PROCESSED / "painel_amc_goias.csv"
ARQ_GEOM_AMC  = DIR_PROCESSED / "amc_goias.gpkg"
ARQ_IMPACTO   = DIR_DIAG / "amc_impacto_goias.csv"

UF_CODIGO_IBGE = 52            # Goiás (prefixo do código IBGE de 7 dígitos)
AMC_START, AMC_END = 1980, 2010
FATOR_UA_BOVINO = 0.7          # idêntico ao Pipeline #16

# Colunas-chave do painel municipal.
KEYS = ["cd_mun", "nm_mun", "ano"]

# Colunas DERIVADAS recalculadas por fórmula direta sobre as extensivas já
# agregadas (NUNCA somar). Mesmas de derivar_metricas (#16) + taxas de abate.
# Estas reproduzem os singletons exatamente (mesma fórmula do #16), exceto
# taxa_abate_*, que difere ~0,02% porque o #16 ARMAZENA o valor arredondado a
# 4 casas — aqui recalculamos das componentes não-arredondadas (mais preciso).
COLS_DERIVADAS = [
    "lotacao_bov_ha", "pec_bovinos_ua", "lotacao_ua_ha_pasto",
    "credito_por_ha_pastagem", "produtividade_soja_ton_ha",
    "pct_pastagem_lulc", "pct_agricultura_lulc", "pct_natural_lulc",
    "pib_per_capita_real", "densidade_demografica_hab_km2",
    "taxa_abate_bovino", "taxa_abate_frango", "taxa_abate_suino",
]

# Razões agregadas por RECONSTRUÇÃO do denominador implícito. Para uma razão
# r_i = num_i / den_i, temos num_i (coluna extensiva conhecida) e recuperamos
# den_i = num_i / r_i. A razão da AMC = Σnum_i / Σden_i. Reproduz singletons
# EXATAMENTE (1 município → ele mesmo). Por que não somar nem promediar: a média
# de percentuais ignora o peso de cada município.
#   col: (coluna_numerador, é_percentual)
# participacao_agro_pct = VA_agro / VA_total × 100 — o #16 NÃO guarda VA_total,
# então reconstruímos VA_total_i = va_agro_real_i / (participacao_i/100).
RAZOES_RECONSTRUIDAS = {
    "participacao_agro_pct":    ("va_agro_real_rs",            True),
    "censo2017_lotacao_bov_ha": ("censo2017_n_cabecas_bovinos", False),
}

# Razões do Censo onde o PESO conhecido é o próprio denominador (nº de
# estabelecimentos). num_i = (pct_i/100)·peso_i ; razão_AMC = Σnum / Σpeso × 100.
RAZOES_PONDERADAS = {
    "censo2017_pct_familiar":    "censo2017_n_estabelecimentos",
    "censo2017_pct_adubacao":    "censo2017_n_estabelecimentos",
    "censo2017_pct_agrotoxicos": "censo2017_n_estabelecimentos",
}


# ---------------------------------------------------------------------------
# 1. Crosswalk cd_mun → code_amc (Ehrl 2017 via geobr)
# ---------------------------------------------------------------------------

def construir_crosswalk(forcar: bool, munis_painel: set[int]) -> pd.DataFrame:
    """Crosswalk cd_mun → code_amc para Goiás. Cacheia em CSV; baixa do geobr
    apenas quando ausente ou --force."""
    if ARQ_CROSSWALK.exists() and not forcar:
        cw = pd.read_csv(ARQ_CROSSWALK)
        print(f"[crosswalk] cacheado: {ARQ_CROSSWALK.name} "
              f"({cw['cd_mun'].nunique()} munis → {cw['code_amc'].nunique()} AMCs)")
        return cw

    print(f"[crosswalk] baixando AMC do geobr (Ehrl 2017, {AMC_START}–{AMC_END})...")
    import geobr  # import tardio: só necessário no rebaixamento
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        amc = geobr.read_comparable_areas(start_year=AMC_START, end_year=AMC_END)

    # Explodir a lista de municípios (códigos IBGE 2010) de cada AMC.
    linhas = []
    for _, r in amc.iterrows():
        for cd in str(r["list_code_muni_2010"]).split(","):
            cd = cd.strip()
            if cd:
                linhas.append((int(cd), int(r["code_amc"])))
    cw_full = pd.DataFrame(linhas, columns=["cd_mun", "code_amc"]).drop_duplicates()

    # Filtrar Goiás (prefixo 52). Goiás não mudou de malha entre 2010 e 2020,
    # então os códigos 2010 == códigos 2020 usados no painel.
    cw = cw_full[cw_full["cd_mun"] // 100000 == UF_CODIGO_IBGE].copy()

    # Conferir cobertura contra o universo do painel.
    faltando = munis_painel - set(cw["cd_mun"])
    if faltando:
        raise RuntimeError(
            f"[crosswalk] {len(faltando)} munis do painel sem AMC: {sorted(faltando)[:10]}. "
            "Verifique a versão da malha (geobr 2020 vs códigos AMC 2010)."
        )

    cw["amc_n_munis"] = cw.groupby("code_amc")["cd_mun"].transform("size")
    cw.to_csv(ARQ_CROSSWALK, index=False, encoding="utf-8")
    print(f"[crosswalk] {cw['cd_mun'].nunique()} munis → {cw['code_amc'].nunique()} AMCs "
          f"({(cw['amc_n_munis']>1).groupby(cw['code_amc']).first().sum()} grupos pai+filhos). "
          f"Salvo: {ARQ_CROSSWALK.name}")
    return cw


def anexar_nomes_crosswalk(cw: pd.DataFrame, painel: pd.DataFrame) -> pd.DataFrame:
    """Garante coluna nm_mun no crosswalk (vinda do painel) para legibilidade."""
    if "nm_mun" not in cw.columns:
        nomes = painel[["cd_mun", "nm_mun"]].drop_duplicates()
        cw = cw.merge(nomes, on="cd_mun", how="left")
        cw.to_csv(ARQ_CROSSWALK, index=False, encoding="utf-8")
    return cw


# ---------------------------------------------------------------------------
# 2. Classificação de colunas e agregação
# ---------------------------------------------------------------------------

def classificar_colunas(painel: pd.DataFrame) -> list[str]:
    """Retorna as colunas EXTENSIVAS (a somar). Garante que toda coluna numérica
    está classificada (extensiva, derivada ou razão-censo)."""
    numericas = [c for c in painel.columns if c not in KEYS + ["code_amc"]]
    classificadas = set(COLS_DERIVADAS) | set(RAZOES_RECONSTRUIDAS) | set(RAZOES_PONDERADAS)
    extensivas = [c for c in numericas if c not in classificadas]

    # Sanidade: nenhuma coluna pode escapar da classificação.
    nao_classificadas = set(numericas) - set(extensivas) - classificadas
    assert not nao_classificadas, f"colunas não classificadas: {nao_classificadas}"

    # Sanidade: razões/derivadas declaradas devem existir no painel.
    ausentes = classificadas - set(painel.columns)
    if ausentes:
        print(f"[classificação] AVISO: derivadas/razões declaradas ausentes do painel "
              f"(serão ignoradas): {sorted(ausentes)}")
    return extensivas


def agregar_extensivas(painel: pd.DataFrame, extensivas: list[str]) -> pd.DataFrame:
    """Soma colunas extensivas por (code_amc, ano). min_count=1 → all-NaN vira NaN."""
    agg = (
        painel.groupby(["code_amc", "ano"])[extensivas]
        .sum(min_count=1)
        .reset_index()
    )
    return agg


def recalcular_razoes_agregadas(painel: pd.DataFrame) -> pd.DataFrame:
    """Recalcula razões por reconstrução do denominador implícito, por
    (code_amc, ano). Soma numerador e denominador com min_count=1 — se NENHUM
    município da AMC tem o numerador, o resultado fica NaN (não 0)."""
    blocos = []

    def agregar(df, col, fator):
        g = (df.groupby(["code_amc", "ano"])[["_num", "_den"]]
             .sum(min_count=1).reset_index())
        g[col] = g["_num"] / g["_den"].replace(0, np.nan) * fator
        blocos.append(g[["code_amc", "ano", col]])

    # Tipo 1 — numerador extensivo conhecido; den_i = num_i / (razão[/100]).
    for col, (num_col, eh_pct) in RAZOES_RECONSTRUIDAS.items():
        if col not in painel.columns or num_col not in painel.columns:
            continue
        df = painel[["code_amc", "ano", col, num_col]].copy()
        razao = df[col] / 100.0 if eh_pct else df[col]
        df["_num"] = df[num_col]
        df["_den"] = df[num_col] / razao.replace(0, np.nan)
        agregar(df, col, 100.0 if eh_pct else 1.0)

    # Tipo 2 — peso conhecido é o denominador; num_i = (pct/100)·peso.
    for col, peso in RAZOES_PONDERADAS.items():
        if col not in painel.columns or peso not in painel.columns:
            continue
        df = painel[["code_amc", "ano", col, peso]].copy()
        df["_num"] = df[col] / 100.0 * df[peso]
        df["_den"] = df[peso].where(df[col].notna())  # só pesa quem tem a razão
        agregar(df, col, 100.0)

    if not blocos:
        return pd.DataFrame(columns=["code_amc", "ano"])
    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["code_amc", "ano"], how="outer")
    return out


def recalcular_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Recalcula as métricas derivadas a partir das extensivas já agregadas.
    Espelha derivar_metricas do Pipeline #16 + participação + taxas de abate."""
    def ratio(num, den):
        return df[num] / df[den] if num in df and den in df else np.nan

    df["lotacao_bov_ha"]          = ratio("pec_bovinos_cab", "lulc_pastagem_ha")
    if "pec_bovinos_cab" in df:
        df["pec_bovinos_ua"]      = df["pec_bovinos_cab"] * FATOR_UA_BOVINO
        df["lotacao_ua_ha_pasto"] = df["pec_bovinos_ua"] / df["lulc_pastagem_ha"]
    df["credito_por_ha_pastagem"] = ratio("sicor_total_real_rs", "lulc_pastagem_ha")
    df["produtividade_soja_ton_ha"] = ratio("agri_soja_ton", "agri_soja_ha_plantada")

    df["pct_pastagem_lulc"]    = ratio("lulc_pastagem_ha", "lulc_area_total_ha") * 100
    df["pct_agricultura_lulc"] = ratio("lulc_agricultura_ha", "lulc_area_total_ha") * 100
    if {"lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha", "lulc_area_total_ha"} <= set(df.columns):
        natural = (df["lulc_floresta_nativa_ha"] + df["lulc_formacao_savanica_ha"]
                   + df.get("lulc_campo_nativo_ha", 0).fillna(0))
        df["pct_natural_lulc"] = natural / df["lulc_area_total_ha"] * 100

    df["pib_per_capita_real"] = ratio("pib_real_rs", "populacao")
    if {"populacao", "lulc_area_total_ha"} <= set(df.columns):
        df["densidade_demografica_hab_km2"] = df["populacao"] / (df["lulc_area_total_ha"] / 100)
    # participacao_agro_pct é tratada em recalcular_razoes_agregadas (reconstrói
    # VA_total, que o #16 não guarda) — NÃO recalcular como va/pib aqui.

    # Taxas de abate = abate_cab / efetivo (confere com #16: abate/efetivo)
    for esp, rebanho in [("bovino", "pec_bovinos_cab"),
                         ("frango", "pec_galinaceos_cab"),
                         ("suino",  "pec_suinos_cab")]:
        df[f"taxa_abate_{esp}"] = ratio(f"abate_{esp}_cab", rebanho)

    return df.replace([np.inf, -np.inf], np.nan)


# ---------------------------------------------------------------------------
# 3. Validação e relatório de impacto
# ---------------------------------------------------------------------------

def validar_e_relatar(painel_mun: pd.DataFrame, painel_amc: pd.DataFrame,
                      extensivas: list[str], cw: pd.DataFrame) -> None:
    """(a) confere invariância do total estadual; (b) mostra que os saltos
    espúrios de 1989/1993/1997 somem no nível de AMC. Salva relatório."""
    print("\n[validação] Invariância do total estadual (município vs AMC):")
    for col in ["pec_bovinos_cab", "lulc_pastagem_ha", "agri_soja_ha_plantada"]:
        if col not in extensivas:
            continue
        tm = painel_mun.groupby("ano")[col].sum(min_count=1)
        ta = painel_amc.groupby("ano")[col].sum(min_count=1)
        delta = (tm - ta).abs().max()
        print(f"  {col:24s} max|Δ total| = {delta:.6f}  "
              f"{'OK' if delta < 1e-3 else 'DIVERGE — investigar'}")

    # (b) Prova da partição constante: NENHUMA AMC pode estrear no SIDRA depois
    #     de 1985 (se estreasse, conteria só filhos → gap de agrupamento).
    pe = painel_amc.dropna(subset=["pec_bovinos_cab"])
    first_amc = pe.groupby("code_amc")["ano"].min()
    n_tardias = int((first_amc > 1985).sum())
    print(f"\n[validação] AMCs que estreiam após 1985 (deveria ser 0): {n_tardias} "
          f"de {painel_amc['code_amc'].nunique()}  "
          f"{'OK — partição territorialmente constante' if n_tardias == 0 else 'GAP — investigar'}")

    # (c) Isolar o artefato territorial: a pior queda anual de rebanho ENTRE OS
    #     GRUPOS PAI+FILHOS (AMCs multi-município). Comparada com a pior queda
    #     entre os municípios-membro desses grupos. Singletons (variação real)
    #     ficam de fora para não poluir o diagnóstico.
    multi = set(cw.groupby("code_amc")["cd_mun"].nunique().loc[lambda s: s > 1].index)
    munis_multi = set(cw[cw["code_amc"].isin(multi)]["cd_mun"])
    print("\n[validação] Pior queda anual de rebanho NOS GRUPOS PAI+FILHOS "
          "(artefato territorial):")
    print("  ano | municípios-membro | AMCs (agrupadas)")
    linhas_rel = []
    for ano in [1989, 1993, 1997, 2001]:
        pm = painel_mun[painel_mun.ano.isin([ano - 1, ano]) &
                        painel_mun.cd_mun.isin(munis_multi)].pivot(
            index="cd_mun", columns="ano", values="pec_bovinos_cab").dropna()
        var_mun = ((pm[ano] - pm[ano - 1]) / pm[ano - 1] * 100).min() if len(pm) else np.nan
        pa = painel_amc[painel_amc.ano.isin([ano - 1, ano]) &
                        painel_amc.code_amc.isin(multi)].pivot(
            index="code_amc", columns="ano", values="pec_bovinos_cab").dropna()
        var_amc = ((pa[ano] - pa[ano - 1]) / pa[ano - 1] * 100).min() if len(pa) else np.nan
        print(f"  {ano} | {var_mun:+.0f}% | {var_amc:+.0f}%")
        linhas_rel.append({"ano": ano,
                           "pior_queda_municipio_membro_pct": var_mun,
                           "pior_queda_amc_grupo_pct": var_amc})

    rel = pd.DataFrame(linhas_rel)
    rel.to_csv(ARQ_IMPACTO, index=False, encoding="utf-8")
    print(f"\n[validação] Relatório de impacto salvo: {ARQ_IMPACTO.relative_to(ROOT)}")
    print("  Interpretação: entre os grupos pai+filhos, as quedas de 50–80% (perda")
    print("  de território no ano da emancipação) desaparecem ao agregar em AMC.")


def salvar_geometria(cw: pd.DataFrame) -> None:
    """Salva a geometria dissolvida das AMC de Goiás (para mapas). Opcional —
    requer geopandas/geobr; falha silenciosamente se indisponível."""
    try:
        import geobr
        import geopandas as gpd  # noqa: F401
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            amc = geobr.read_comparable_areas(start_year=AMC_START, end_year=AMC_END)
        amc_go = amc[amc["code_amc"].astype(int).isin(cw["code_amc"].unique())].copy()
        amc_go = amc_go[["code_amc", "geometry"]]
        amc_go.to_file(ARQ_GEOM_AMC, driver="GPKG")
        print(f"[geom] {len(amc_go)} polígonos AMC salvos: {ARQ_GEOM_AMC.relative_to(ROOT)}")
    except Exception as e:  # noqa: BLE001
        print(f"[geom] geometria não salva (opcional): {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true",
                    help="rebaixa a AMC do geobr (ignora o crosswalk cacheado)")
    ap.add_argument("--sem-geometria", action="store_true",
                    help="não gera o GPKG de geometria das AMC")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #25 — Áreas Mínimas Comparáveis (AMC), Goiás 1985–2024")
    print(f"Ehrl 2017 via geobr | janela AMC {AMC_START}–{AMC_END}")
    print("=" * 70)

    if not ARQ_PAINEL.exists():
        raise FileNotFoundError(
            f"{ARQ_PAINEL} não encontrado. Rode construir_painel_unificado.py (#16)."
        )
    painel = pd.read_parquet(ARQ_PAINEL)
    munis = set(painel["cd_mun"].unique())
    print(f"[painel #16] {painel.shape[0]:,} linhas | {len(munis)} munis × "
          f"{painel['ano'].nunique()} anos | {painel.shape[1]} colunas")

    # 1. Crosswalk
    cw = construir_crosswalk(args.force, munis)
    cw = anexar_nomes_crosswalk(cw, painel)

    # 2. Anexar code_amc e agregar
    painel_cw = painel.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
    assert painel_cw["code_amc"].notna().all(), "há município sem AMC após o merge"

    extensivas = classificar_colunas(painel_cw)
    n_razoes = len(RAZOES_RECONSTRUIDAS) + len(RAZOES_PONDERADAS)
    print(f"[agregação] {len(extensivas)} colunas extensivas (soma), "
          f"{len(COLS_DERIVADAS)} derivadas (recalc por fórmula), "
          f"{n_razoes} razões (reconstrução do denominador)")

    amc = agregar_extensivas(painel_cw, extensivas)
    razoes = recalcular_razoes_agregadas(painel_cw)
    if not razoes.empty:
        amc = amc.merge(razoes, on=["code_amc", "ano"], how="left")
    amc = recalcular_derivadas(amc)

    # Metadados de AMC: nome representativo (maior área LULC) e nº de munis.
    rep = (painel_cw.sort_values("lulc_area_total_ha", ascending=False)
           .drop_duplicates("code_amc")[["code_amc", "nm_mun"]]
           .rename(columns={"nm_mun": "amc_nome_rep"}))
    n_munis = cw.groupby("code_amc")["cd_mun"].nunique().rename("amc_n_munis").reset_index()
    amc = amc.merge(rep, on="code_amc", how="left").merge(n_munis, on="code_amc", how="left")

    # Ordenar colunas: chaves/metadados primeiro
    frente = ["code_amc", "amc_nome_rep", "amc_n_munis", "ano"]
    amc = amc[frente + [c for c in amc.columns if c not in frente]]
    amc = amc.sort_values(["code_amc", "ano"]).reset_index(drop=True)

    # Sanidade dimensional
    n_amc, n_anos = amc["code_amc"].nunique(), amc["ano"].nunique()
    assert len(amc) == n_amc * n_anos, "linhas != AMCs × anos"
    assert amc.duplicated(["code_amc", "ano"]).sum() == 0, "duplicatas (code_amc, ano)"
    print(f"[agregação] painel AMC: {amc.shape[0]:,} linhas "
          f"({n_amc} AMCs × {n_anos} anos) × {amc.shape[1]} colunas")

    # 3. Validação + impacto
    validar_e_relatar(painel_cw, amc, extensivas, cw)

    # 4. Salvar
    amc.to_parquet(ARQ_PAINEL_AMC_PARQUET, index=False)
    amc.to_csv(ARQ_PAINEL_AMC_CSV, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_PAINEL_AMC_PARQUET.relative_to(ROOT)}")
    print(f"[OK] {ARQ_PAINEL_AMC_CSV.relative_to(ROOT)}")

    if not args.sem_geometria:
        salvar_geometria(cw)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — use painel_amc_goias.parquet para análises LONGITUDINAIS.")
    print("painel_unificado.parquet (246 munis) segue válido para TRANSVERSAIS.")
    print("=" * 70)


if __name__ == "__main__":
    main()
