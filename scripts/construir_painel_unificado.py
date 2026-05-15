"""
Pipeline #16 — Painel Unificado Município × Ano (Goiás, 1985–2024)
==================================================================

Consolida em uma única tabela wide (cd_mun × ano) todas as fontes prontas do
projeto: LULC MapBiomas, pecuária e lavouras SIDRA, PIB municipal, população,
crédito rural SICOR e Censo Agropecuário 2017. Slots vazios reservados para
IDH-M (#13) e Fogo MapBiomas (#14) — preenchimento futuro sem refator.

Saída:
    data/processed/painel_unificado.parquet  (formato primário)
    data/processed/painel_unificado.csv      (cortesia, encoding utf-8)
    outputs/diagnosticos/painel_unificado_cobertura.csv  (% NaN por coluna × ano)

Como rodar:
    python scripts/construir_painel_unificado.py

================================================================================
DECISÕES METODOLÓGICAS E LIMITAÇÕES — LEIA ANTES DE USAR
================================================================================

1. UNIVERSO ESPACIAL: 246 municípios de Goiás, identificados por `cd_mun`
   (int, 7 dígitos IBGE). Verificado: mapbiomas_munis_goias.csv tem 246 munis
   distintos (não 247, como sugere a contagem de linhas do Censo Agro).

2. JANELA TEMPORAL: 1985–2024 completa (40 anos × 246 munis = 9.840 linhas).
   NaN onde a fonte não cobre. Filtro temporal fica nas análises a jusante:
       - Pré-2002:   sem PIB, sem população (estimativas IBGE só desde 2001),
                     sem PAM 839 (safrinha disponível desde 2003).
       - 2002–2012:  sem SICOR (BACEN só desde 2013).
       - 2013–2023:  janela completa (todas as fontes coexistem).
       - 2024:       SICOR e MapBiomas presentes; PIB ainda não publicado.
       - 2025–2026:  apenas SICOR parcial (excluído desta versão).

   AVISO HISTÓRICO: pré-1989, agregados estaduais "Goiás" em fontes externas
   (ex.: rebanho_bovino_goias.csv) frequentemente INCLUEM Tocantins (criado
   em 1988 e instalado em 1989). Este painel cobre APENAS os 246 munis de GO
   atual — o batimento com agregados pré-1989 mostra dif ~19% por essa razão,
   o que está CORRETO conceitualmente. Pós-1989 o batimento é exato.

3. DEFLAÇÃO: Valores monetários (PIB, VA agropecuário, SICOR) convertidos para
   reais de DEZEMBRO/2024 via IPCA acumulado de dezembro de cada ano (tabela
   SIDRA 1737). Padrão idêntico a `analise_credito_uso_terra.py` Pipeline #8.
   Variáveis com sufixo `_real_rs`. Sem deflator, valores nominais não são
   comparáveis entre anos.

4. CENSO AGROPECUÁRIO 2017: replicado como atributo ESTÁTICO em todos os
   anos do município (mesmo valor 1985–2024). Decisão pragmática para
   regressão pooled — Censo é cross-section único; não há série temporal
   municipal anual de estrutura agrária. Limitação: não captura mudanças
   estruturais pré-2017 ou pós-2017.

5. LEITE PPM 74: INCLUÍDO via variável 106 (Quantidade em Mil litros). A
   coleta original não passava a classificação 80 (Tipo de produto) e o
   endpoint devolvia apenas a variável 215 (Valor da produção em moedas
   históricas), por isso ficou excluído na primeira versão. Após corrigir a
   chamada SIDRA com `classifications={"80": "2682"}`, a quantidade física
   passou a vir corretamente. Coluna do painel: `agri_leite_mil_litros`.

6. LAVOURAS — TOP 6 (decisão do usuário, alinhada com economia de Goiás):
       PAM 839 (milho safras, desde 2003):
           - milho1 = categoria_id 114253 (Milho em grão - 1ª safra)
           - milho2 = categoria_id 114254 (Milho em grão - 2ª safra)
       PAM 1612 (lavouras temporárias, desde 1974):
           - soja    = categoria_id 2713
           - cana    = categoria_id 2696 (Cana-de-açúcar)
           - feijao  = categoria_id 2702 (Feijão em grão; soma todas as safras)
           - algodao = categoria_id 2689 (Algodão herbáceo em caroço)
   Cada cultura → 2 colunas: `agri_<cultura>_ha_plantada`, `agri_<cultura>_ton`.
   Demais culturas (arroz, mandioca, sorgo, café, banana, etc.) NÃO entram —
   acessíveis via JOIN ad-hoc com sidra_pam1612_temporarias.csv.
   Validação cruzada MapBiomas vs SIDRA já feita para soja em
   validacao_soja_mapbiomas_sidra.csv.

7. PECUÁRIA: PPM 3939, variável "Efetivo dos rebanhos" (cabeças). Mantidas
   3 categorias agregadas: bovinos (2670), suínos (32794), galináceos (32796).
   Demais (equino, bubalino, ovino, caprino) excluídas — pouca relevância
   para o eixo LULC × pecuária da dissertação.

   UNIDADE ANIMAL (UA): PPM 3939 e 73 não desagregam bovinos por idade no
   nível municipal, e Censo Agro 2017 (tabelas 6910–6913) também não publica
   essa estratificação na API SIDRA. Por isso o painel aplica o fator
   convencional FATOR_UA_BOVINO = 0.7 UA/cabeça (média Embrapa/CONAB para
   rebanho de corte misto brasileiro: ~50% adultos de 1.0 UA, ~30% novilhos
   de 0.7 UA, ~20% bezerros de 0.5 UA → ponderado ≈ 0.71). Coluna derivada:
   `pec_bovinos_ua` e `lotacao_ua_ha_pasto`. Limitação: o fator é
   estado-estacionário, não captura variação inter-anual da composição
   etária. Documentado em Textos/glossario_metricas.md.

8. PIB MUNICIPAL: SIDRA 5938 (Contas Regionais IBGE). Variáveis selecionadas:
       - pib_real_rs:     variavel_id 37  (PIB a preços correntes, deflacionado)
       - va_agro_real_rs: variavel_id 513 (VA da agropecuária, deflacionado)
   IMPORTANTE: SIDRA 5938 reporta valores em "Mil Reais". Este painel
   MULTIPLICA POR 1000 para sair em REAIS — coerência com SICOR (R$).
   `participacao_agro_pct` = VA agro / VA total × 100 (variavel_id 498),
   invariante à deflação por construção.

   DIVERGÊNCIA conhecida com `painel_credito_lulc.csv` (Pipeline #8):
   aquele arquivo reporta `pib_real_rs` ~38% maior que o cálculo aqui,
   apesar de declarar a mesma base IPCA. Causa exata não auditada;
   a fórmula deste pipeline é determinística e bate com SIDRA bruto.
   Se a regressão exigir compatibilidade, usar este painel.

9. SICOR: agregado por (cd_mun, ano, finalidade) somando `valor` e
   `n_operacoes`. Pivotado em Custeio/Investimento. Valores deflacionados.
   Anos 2025-2026 (parciais) EXCLUÍDOS deste painel — incluí-los enviesaria
   somatórios. Quem precisar dos parciais usa sicor_painel_municipal.csv.

10. SLOTS VAZIOS (IDH-M e Fogo): colunas criadas com NaN. Quando os pipelines
    #13 (IDH-M Atlas PNUD) e #14 (Fogo MapBiomas via GEE) forem executados,
    basta `df.update()` por (cd_mun, ano) — sem refator.

11. LULC — agrupamento de classes MapBiomas Col 10.1: ver dicionário
    GRUPOS_LULC abaixo. Decisão: agregar por GRUPO TEMÁTICO, não por
    class_id individual, para reduzir esparsidade. `lulc_agricultura_ha`
    soma TODAS as lavouras MapBiomas (soja + cana + algodão + arroz +
    café + citrus + outras temporárias + outras perenes). `lulc_soja_ha`
    permanece desagregada por ser a cultura central da dissertação.
    `lulc_area_total_ha` = soma de todas as classes presentes (proxy da
    área do município; pode divergir levemente da área oficial geobr por
    arredondamento de pixel).

12. MÉTRICAS DERIVADAS: calculadas APENAS onde os insumos existem (sem
    extrapolação). NaN propaga.

13. NÃO APLICA validação cruzada automática neste script — apenas gera o
    diagnóstico de cobertura. Validação fica em scripts dedicados.
"""
from __future__ import annotations

import sys
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
DIR_OUTPUT    = ROOT / "outputs"
DIR_DIAG      = DIR_OUTPUT / "diagnosticos"
for d in (DIR_PROCESSED, DIR_OUTPUT, DIR_DIAG):
    d.mkdir(parents=True, exist_ok=True)

ANO_INI = 1985
ANO_FIM = 2024
DATA_BASE_DEFLATOR = (2024, 12)

# Conversão cabeças → Unidade Animal. Fator único aplicado por falta de
# breakdown etário a nível municipal nos dados SIDRA (PPM 3939/73 e Censo
# Agro 2017). Ver decisão metodológica #7 acima.
FATOR_UA_BOVINO = 0.7

# Agrupamento de classes MapBiomas Col 10.1 → coluna do painel.
# class_ids confirmados via inspeção de mapbiomas_munis_goias.csv.
GRUPOS_LULC = {
    "lulc_floresta_nativa_ha":     [3],
    "lulc_formacao_savanica_ha":   [4],   # Savana/Cerrado
    "lulc_silvicultura_ha":        [9],
    "lulc_campo_alagado_ha":       [11],
    "lulc_campo_nativo_ha":        [12],
    "lulc_pastagem_ha":            [15],
    "lulc_mosaico_usos_ha":        [21],
    "lulc_area_urbana_ha":         [24],
    "lulc_outras_nao_vegetadas_ha":[25, 29],  # Outras + Afloramento Rochoso
    "lulc_mineracao_ha":           [30],
    "lulc_aquicultura_ha":         [31],
    "lulc_corpo_dagua_ha":         [33],
    "lulc_soja_ha":                [39],
    "lulc_agricultura_ha":         [20, 39, 40, 41, 46, 47, 48, 62],  # cana+soja+arroz+outras+café+citrus+perenes+algodão
}

# IDs de categoria SIDRA (confirmados via inspeção)
CAT_PAM839_MILHO1  = 114253
CAT_PAM839_MILHO2  = 114254
CAT_PAM1612 = {
    "abacaxi":      2688,
    "alfafa_fenada": 40471,
    "algodao":      2689,
    "alho":         2690,
    "amendoim":     2691,
    "arroz":        2692,
    "aveia":        2693,
    "batata_doce":  2694,
    "batata_inglesa": 2695,
    "cana":         2696,
    "cana_forragem": 40470,
    "cebola":       2697,
    "centeio":      2698,
    "cevada":       2699,
    "ervilha":      2700,
    "fava":         2701,
    "feijao":       2702,
    "fumo":         2703,
    "girassol":     109179,
    "juta":         2704,
    "linho":        2705,
    "malva":        2706,
    "mamona":       2707,
    "mandioca":     2708,
    "melancia":     2709,
    "melao":        2710,
    "milho_total":  2711,
    "rami":         2712,
    "soja":         2713,
    "sorgo":        2714,
    "tomate":       2715,
    "trigo":        2716,
    "triticale":    109180,
}
CAT_PAM1613 = {
    "abacate":         2717,
    "algodao_arboreo": 2718,
    "acai":            45981,
    "azeitona":        2719,
    "banana":          2720,
    "borracha_coagulado": 2721,
    "borracha_liquido": 40472,
    "cacau":           2722,
    "cafe_total":      2723,
    "cafe_arabica":    31619,
    "cafe_canephora":  31620,
    "caju":            40473,
    "caqui":           2724,
    "castanha_caju":   2725,
    "cha_da_india":    2726,
    "coco_da_baia":    2727,
    "dende":           2728,
    "erva_mate":       2729,
    "figo":            2730,
    "goiaba":          2731,
    "guarana":         2732,
    "laranja":         2733,
    "limao":           2734,
    "maca":            2735,
    "mamao":           2736,
    "manga":           2737,
    "maracuja":        2738,
    "marmelo":         2739,
    "noz":             2740,
    "palmito":         90001,
    "pera":            2741,
    "pessego":         2742,
    "pimenta_do_reino": 2743,
    "sisal_agave":     2744,
    "tangerina":       2745,
    "tungue":          2746,
    "urucum":          2747,
    "uva":             2748,
}
CAT_PPM3939 = {
    "bovinos":    2670,
    "suinos":     32794,
    "galinaceos": 32796,
}
CAT_PPM95 = {"ovinos_tosquiados": 108}
CAT_PPM74_MEL = {"mel": 2687}
CAT_PPM74_LA  = {"la": 2684}

# IDs de variável SIDRA (confirmados)
VAR_PAM_AREA_PLANT = 109   # Área plantada (ha)
VAR_PAM_QTD_PROD   = 214   # Quantidade produzida (ton)
VAR_PPM_REBANHO    = 105   # Efetivo dos rebanhos (cabeças)
VAR_PIB_TOTAL      = 37    # PIB a preços correntes
VAR_PIB_VA_TOTAL   = 498   # VA total
VAR_PIB_VA_AGRO    = 513   # VA agropecuária
VAR_POPULACAO      = 9324  # População residente estimada


# ---------------------------------------------------------------------------
# Helpers de I/O e deflação (replica padrão do Pipeline #8)
# ---------------------------------------------------------------------------

def carregar_ipca() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_1737_ipca.csv", encoding="utf-8")
    return df.dropna(subset=["indice_acum"])


def deflacionar(df_nominal: pd.DataFrame, col_val: str, df_ipca: pd.DataFrame) -> pd.Series:
    """Deflaciona col_val para R$ de DATA_BASE_DEFLATOR usando dez de cada ano."""
    ano_base, mes_base = DATA_BASE_DEFLATOR
    idx_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base),
        "indice_acum",
    ].iloc[0]
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "idx_dez"}
    )
    merged = df_nominal.merge(df_dez, on="ano", how="left")
    return merged[col_val] * (idx_base / merged["idx_dez"])


# ---------------------------------------------------------------------------
# Loaders por fonte — todos retornam DataFrame indexado em (cd_mun, ano)
# ---------------------------------------------------------------------------

def construir_grade() -> pd.DataFrame:
    """Produto cartesiano dos 246 munis × 1985–2024."""
    mapb = pd.read_csv(DIR_PROCESSED / "mapbiomas_munis_goias.csv", encoding="utf-8")
    munis = mapb[["cd_mun", "nm_mun"]].drop_duplicates().sort_values("cd_mun")
    anos = pd.DataFrame({"ano": range(ANO_INI, ANO_FIM + 1)})
    grade = munis.merge(anos, how="cross")
    print(f"[grade] {len(grade):,} linhas ({munis.shape[0]} munis × {anos.shape[0]} anos)")
    return grade


def load_lulc() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "mapbiomas_munis_goias.csv", encoding="utf-8")
    blocos = []
    for col, class_ids in GRUPOS_LULC.items():
        sub = (
            df[df["class_id"].isin(class_ids)]
            .groupby(["cd_mun", "ano"], as_index=False)["area_ha"].sum()
            .rename(columns={"area_ha": col})
        )
        blocos.append(sub)
    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["cd_mun", "ano"], how="outer")
    # Área total = soma de todas as classes presentes no original (não dos grupos,
    # para evitar contagem dupla com lulc_agricultura que inclui soja).
    area_total = (
        df.groupby(["cd_mun", "ano"], as_index=False)["area_ha"].sum()
        .rename(columns={"area_ha": "lulc_area_total_ha"})
    )
    out = out.merge(area_total, on=["cd_mun", "ano"], how="outer")
    print(f"[lulc] {len(out):,} linhas, {out.shape[1]-2} colunas LULC")
    return out


def load_pecuaria() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_ppm3939_rebanhos.csv", encoding="utf-8")
    df = df[df["variavel_id"] == VAR_PPM_REBANHO]
    blocos = []
    for nome, cat_id in CAT_PPM3939.items():
        sub = (
            df[df["categoria_id"] == cat_id][["cd_mun", "ano", "valor"]]
            .rename(columns={"valor": f"pec_{nome}_cab"})
        )
        blocos.append(sub)
    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["cd_mun", "ano"], how="outer")
    print(f"[pecuaria] {len(out):,} linhas, {out.shape[1]-2} colunas")
    return out


def load_leite() -> pd.DataFrame:
    """PPM 74 — Quantidade produzida de leite (mil litros).

    Filtra variável 106 (Produção de origem animal) com unidade "Mil litros".
    A categoria já é fixa (Leite, código 2682) na coleta — basta selecionar a
    variável certa. Anos sem dado para o município ficam NaN.
    """
    df = pd.read_csv(DIR_PROCESSED / "sidra_ppm74_leite.csv", encoding="utf-8")
    qtd = df[(df["variavel_id"] == 106) & (df["unidade"] == "Mil litros")]
    out = qtd[["cd_mun", "ano", "valor"]].rename(
        columns={"valor": "agri_leite_mil_litros"}
    )
    print(f"[leite] {len(out):,} linhas com quantidade não-nula")
    return out


def load_agricultura() -> pd.DataFrame:
    # PAM 1612 — todas as lavouras temporárias
    df1612 = pd.read_csv(DIR_PROCESSED / "sidra_pam1612_temporarias.csv", encoding="utf-8")
    blocos = []
    for nome, cat_id in CAT_PAM1612.items():
        for var_id, sufixo in [
            (VAR_PAM_AREA_PLANT, "ha_plantada"),
            (VAR_PAM_QTD_PROD,   "ton"),
        ]:
            col = f"agri_{nome}_{sufixo}"
            sub = (
                df1612[
                    (df1612["categoria_id"] == cat_id) &
                    (df1612["variavel_id"]  == var_id)
                ][["cd_mun", "ano", "valor"]]
                .rename(columns={"valor": col})
            )
            blocos.append(sub)

    # PAM 839 — milho 1ª e 2ª safra
    df839 = pd.read_csv(DIR_PROCESSED / "sidra_pam839_milho_safras.csv", encoding="utf-8")
    for nome, cat_id in [("milho1", CAT_PAM839_MILHO1), ("milho2", CAT_PAM839_MILHO2)]:
        for var_id, sufixo in [
            (VAR_PAM_AREA_PLANT, "ha_plantada"),
            (VAR_PAM_QTD_PROD,   "ton"),
        ]:
            col = f"agri_{nome}_{sufixo}"
            sub = (
                df839[
                    (df839["categoria_id"] == cat_id) &
                    (df839["variavel_id"]  == var_id)
                ][["cd_mun", "ano", "valor"]]
                .rename(columns={"valor": col})
            )
            blocos.append(sub)

    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["cd_mun", "ano"], how="outer")
    print(f"[agricultura] {len(out):,} linhas, {out.shape[1]-2} colunas")
    return out


def load_permanentes() -> pd.DataFrame:
    # PAM 1613 — todas as lavouras permanentes
    df1613 = pd.read_csv(DIR_PROCESSED / "sidra_pam1613_permanentes.csv", encoding="utf-8")
    blocos = []
    for nome, cat_id in CAT_PAM1613.items():
        for var_id, sufixo in [
            (2313, "ha_destinada"),
            (214,  "ton"),
        ]:
            col = f"perm_{nome}_{sufixo}"
            sub = (
                df1613[
                    (df1613["categoria_id"] == cat_id) &
                    (df1613["variavel_id"]  == var_id)
                ][["cd_mun", "ano", "valor"]]
                .rename(columns={"valor": col})
            )
            blocos.append(sub)
    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["cd_mun", "ano"], how="outer")
    print(f"[permanentes] {len(out):,} linhas, {out.shape[1]-2} colunas")
    return out


def load_ovinos_tosquiados() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_ppm95_ovinos_tosquiados.csv", encoding="utf-8")
    out = (
        df[df["variavel_id"] == 108][["cd_mun", "ano", "valor"]]
        .rename(columns={"valor": "pec_ovinos_tosquiados_cab"})
    )
    print(f"[ovinos tosquiados] {len(out):,} linhas")
    return out


def load_mel() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_ppm74_mel.csv", encoding="utf-8")
    qtd = df[(df["variavel_id"] == 106) & (df["unidade"] == "Quilogramas")]
    out = qtd[["cd_mun", "ano", "valor"]].rename(columns={"valor": "pec_mel_kg"})
    print(f"[mel] {len(out):,} linhas com quantidade não-nula")
    return out


def load_la() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_ppm74_la.csv", encoding="utf-8")
    qtd = df[(df["variavel_id"] == 106) & (df["unidade"] == "Quilogramas")]
    out = qtd[["cd_mun", "ano", "valor"]].rename(columns={"valor": "pec_la_kg"})
    print(f"[la] {len(out):,} linhas com quantidade não-nula")
    return out


def load_economico(df_ipca: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_5938_pib_municipal.csv", encoding="utf-8")
    pivot = df.pivot_table(
        index=["cd_mun", "ano"],
        columns="variavel_id",
        values="valor",
        aggfunc="first",
    ).reset_index()
    # Manter só as 3 variáveis de interesse e renomear
    keep = pivot[["cd_mun", "ano", VAR_PIB_TOTAL, VAR_PIB_VA_TOTAL, VAR_PIB_VA_AGRO]].rename(
        columns={
            VAR_PIB_TOTAL:    "pib_nominal_rs",
            VAR_PIB_VA_TOTAL: "va_total_nominal_rs",
            VAR_PIB_VA_AGRO:  "va_agro_nominal_rs",
        }
    )
    # SIDRA 5938 está em Mil R$. Multiplicar por 1000 para sair em R$ (alinha com SICOR).
    keep["pib_real_rs"]     = deflacionar(keep, "pib_nominal_rs",     df_ipca) * 1000.0
    keep["va_agro_real_rs"] = deflacionar(keep, "va_agro_nominal_rs", df_ipca) * 1000.0
    keep["participacao_agro_pct"] = (
        keep["va_agro_nominal_rs"] / keep["va_total_nominal_rs"] * 100
    )
    out = keep[["cd_mun", "ano", "pib_real_rs", "va_agro_real_rs", "participacao_agro_pct"]]
    print(f"[pib] {len(out):,} linhas")
    return out


def load_populacao() -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sidra_6579_populacao.csv", encoding="utf-8")
    out = (
        df[df["variavel_id"] == VAR_POPULACAO][["cd_mun", "ano", "valor"]]
        .rename(columns={"valor": "populacao"})
    )
    print(f"[populacao] {len(out):,} linhas")
    return out


def load_sicor(df_ipca: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(DIR_PROCESSED / "sicor_painel_municipal.csv", encoding="utf-8")
    df = df[(df["ano"] >= ANO_INI) & (df["ano"] <= ANO_FIM)]  # exclui 2025–2026 parciais
    agg = (
        df.groupby(["cd_mun", "ano", "finalidade"], as_index=False)
        .agg(valor=("valor", "sum"), n_op=("n_operacoes", "sum"))
    )
    pivot = agg.pivot_table(
        index=["cd_mun", "ano"],
        columns="finalidade",
        values=["valor", "n_op"],
        fill_value=0,
    ).reset_index()
    pivot.columns = [
        "cd_mun" if c == ("cd_mun", "") else
        "ano"    if c == ("ano", "")    else
        f"sicor_{c[1].lower()}_{c[0]}"
        for c in pivot.columns
    ]
    # Renomear e calcular total
    rename = {
        "sicor_custeio_valor":       "sicor_custeio_nominal_rs",
        "sicor_investimento_valor":  "sicor_investimento_nominal_rs",
        "sicor_custeio_n_op":        "sicor_custeio_n_operacoes",
        "sicor_investimento_n_op":   "sicor_investimento_n_operacoes",
    }
    pivot = pivot.rename(columns=rename)
    for c in rename.values():
        if c not in pivot.columns:
            pivot[c] = 0
    pivot["sicor_custeio_real_rs"]      = deflacionar(pivot, "sicor_custeio_nominal_rs",      df_ipca)
    pivot["sicor_investimento_real_rs"] = deflacionar(pivot, "sicor_investimento_nominal_rs", df_ipca)
    pivot["sicor_total_real_rs"]        = pivot["sicor_custeio_real_rs"] + pivot["sicor_investimento_real_rs"]
    pivot["sicor_n_operacoes_total"]    = (
        pivot["sicor_custeio_n_operacoes"] + pivot["sicor_investimento_n_operacoes"]
    )
    out = pivot[[
        "cd_mun", "ano",
        "sicor_custeio_real_rs", "sicor_investimento_real_rs", "sicor_total_real_rs",
        "sicor_custeio_n_operacoes", "sicor_investimento_n_operacoes", "sicor_n_operacoes_total",
    ]]
    print(f"[sicor] {len(out):,} linhas (1985–2024 com NaN onde não há dado)")
    return out


def load_fogo() -> pd.DataFrame | None:
    """Fogo MapBiomas Collection 4 — área queimada total e por classe.

    Retorna None se o CSV ainda não foi gerado (pipeline #14 não rodou).
    """
    path = DIR_PROCESSED / "fogo_mapbiomas_goias.csv"
    if not path.exists():
        print("[fogo] CSV ausente — slot permanecerá NaN (rode fogo_mapbiomas.py)")
        return None
    df = pd.read_csv(path, encoding="utf-8")
    out = (df[["cd_mun", "ano",
               "area_queimada_total_ha",
               "area_queimada_veg_nat_ha",
               "area_queimada_pastagem_ha",
               "area_queimada_agricultura_ha",
               "area_queimada_mosaico_ha",
               "area_queimada_outros_ha"]]
           .rename(columns={
                "area_queimada_total_ha":       "fogo_total_ha",
                "area_queimada_veg_nat_ha":     "fogo_veg_nat_ha",
                "area_queimada_pastagem_ha":    "fogo_pastagem_ha",
                "area_queimada_agricultura_ha": "fogo_agricultura_ha",
                "area_queimada_mosaico_ha":     "fogo_mosaico_ha",
                "area_queimada_outros_ha":      "fogo_outros_ha",
           }))
    print(f"[fogo] {len(out):,} linhas, anos {out['ano'].min()}-{out['ano'].max()}")
    return out


def load_censo_2017() -> pd.DataFrame:
    """Censo Agropecuário 2017 — replicado como atributo estático por munic."""
    df = pd.read_csv(DIR_PROCESSED / "sidra_censo_agro_2017.csv", encoding="utf-8")
    cols_keep = {
        "cd_mun":                              "cd_mun",
        "ca_n_estabelecimentos_total":         "censo2017_n_estabelecimentos",
        "ca_area_estabelecimentos_ha_total":   "censo2017_area_estabelecimentos_ha",
        "ca_pct_familiar":                     "censo2017_pct_familiar",
        "ca_n_estab_com_tratores":             "censo2017_n_estab_tratores",
        "ca_n_cabecas_bovinos":                "censo2017_n_cabecas_bovinos",
        "ca_lotacao_censo_bov_ha":             "censo2017_lotacao_bov_ha",
        "ca_valor_producao_mil_reais_soja":    "censo2017_valor_producao_soja_mil_rs",
        "ca_pct_adubacao":                     "censo2017_pct_adubacao",
        "ca_pct_agrotoxicos":                  "censo2017_pct_agrotoxicos",
    }
    out = df[list(cols_keep.keys())].rename(columns=cols_keep)
    print(f"[censo2017] {len(out):,} munis (estático, replicado em todos os anos)")
    return out


# ---------------------------------------------------------------------------
# Abate estadual + estimativa municipal
# ---------------------------------------------------------------------------

def load_abate() -> pd.DataFrame:
    """Carrega estimativa municipal de abate (cabeças e kg de carcaça).

    Fonte: sidra_abate_goias_anual.csv (estadual) + PPM 3939 (rebanho municipal)
           → estimativa proporcional em estimativa_abate_municipal.py.

    Retorna DataFrame com colunas:
      [cd_mun, ano, abate_bovino_cab, abate_bovino_kg,
       abate_suino_cab, abate_suino_kg, abate_frango_cab, abate_frango_kg,
       taxa_abate_bovino, taxa_abate_suino, taxa_abate_frango]

    Dados disponíveis: 1997–2024 (interseção ABATE 1997–2025 com PPM 3939 1974–2024).
    Anos fora desse intervalo ficam com NaN.
    """
    path = DIR_PROCESSED / "abate_municipal_estimado.csv"
    if not path.exists():
        print("[abate] AVISO: abate_municipal_estimado.csv nao encontrado — "
              "execute estimativa_abate_municipal.py")
        return pd.DataFrame(columns=["cd_mun", "ano"])

    df = pd.read_csv(path)

    # Pivot: especie × variavel → colunas wide
    # Colunas: cd_mun, nm_mun, ano, especie, abate_cab_est, abate_kg_est, taxa_abate, ...
    wide_rows = []
    for (cd_mun, ano), grp in df.groupby(["cd_mun", "ano"]):
        row = {"cd_mun": cd_mun, "ano": ano}
        for _, r in grp.iterrows():
            esp = r["especie"]
            row[f"abate_{esp}_cab"] = r.get("abate_cab_est", np.nan)
            row[f"abate_{esp}_kg"] = r.get("abate_kg_est", np.nan)
            row[f"taxa_abate_{esp}"] = r.get("taxa_abate", np.nan)
        wide_rows.append(row)

    out = pd.DataFrame(wide_rows)
    out = out.sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    n_munis = out["cd_mun"].nunique()
    anos = sorted(out["ano"].dropna().unique())
    print(f"[abate] {len(out):,} linhas, {n_munis} munis, anos {anos[0]}–{anos[-1]}")
    return out


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def derivar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula ratios e densidades onde insumos existem (NaN propaga)."""
    df["lotacao_bov_ha"] = df["pec_bovinos_cab"] / df["lulc_pastagem_ha"]
    df["pec_bovinos_ua"] = df["pec_bovinos_cab"] * FATOR_UA_BOVINO
    df["lotacao_ua_ha_pasto"] = df["pec_bovinos_ua"] / df["lulc_pastagem_ha"]
    df["credito_por_ha_pastagem"] = df["sicor_total_real_rs"] / df["lulc_pastagem_ha"]
    df["produtividade_soja_ton_ha"] = (
        df["agri_soja_ton"] / df["agri_soja_ha_plantada"]
    )
    # Áreas relativas
    df["pct_pastagem_lulc"]    = df["lulc_pastagem_ha"]    / df["lulc_area_total_ha"] * 100
    df["pct_agricultura_lulc"] = df["lulc_agricultura_ha"] / df["lulc_area_total_ha"] * 100
    df["pct_natural_lulc"] = (
        (df["lulc_floresta_nativa_ha"] + df["lulc_formacao_savanica_ha"]
         + df.get("lulc_campo_nativo_ha", 0).fillna(0))
        / df["lulc_area_total_ha"] * 100
    )
    df["pib_per_capita_real"] = df["pib_real_rs"] / df["populacao"]
    # Densidade demográfica (hab/km² ≈ hab/(ha/100))
    df["densidade_demografica_hab_km2"] = df["populacao"] / (df["lulc_area_total_ha"] / 100)
    # Substituir infinitos (divisão por zero) por NaN para análise downstream
    df = df.replace([np.inf, -np.inf], np.nan)
    return df


def adicionar_slots_vazios(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas placeholder para IDH-M (#13). Fogo (#14) já é populado
    via load_fogo() quando o CSV existe — sem placeholder."""
    for col in [
        "idhm", "idhm_renda", "idhm_educ", "idhm_long",
    ]:
        if col not in df.columns:
            df[col] = np.nan
    return df


def diagnostico_cobertura(df: pd.DataFrame) -> pd.DataFrame:
    """% de NaN por (coluna × ano). Salva em outputs/diagnosticos/."""
    cols_data = [c for c in df.columns if c not in ("cd_mun", "nm_mun", "ano")]
    rows = []
    for ano, sub in df.groupby("ano"):
        n = len(sub)
        for c in cols_data:
            n_nan = sub[c].isna().sum()
            rows.append({"ano": ano, "coluna": c, "n_total": n,
                         "n_nan": int(n_nan), "pct_nan": 100.0 * n_nan / n})
    diag = pd.DataFrame(rows)
    out_path = DIR_DIAG / "painel_unificado_cobertura.csv"
    diag.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[diag] {out_path.relative_to(ROOT)} — {len(diag):,} linhas")

    # Resumo de cobertura média por coluna
    resumo = diag.groupby("coluna", as_index=False).agg(
        pct_nan_medio=("pct_nan", "mean"),
        anos_com_dado=("pct_nan", lambda s: (s < 100).sum()),
    ).sort_values("pct_nan_medio", ascending=False)
    print("\n[diag] Top 15 colunas com mais NaN (média entre anos):")
    print(resumo.head(15).to_string(index=False))
    return diag


def main() -> None:
    print("=" * 70)
    print("Pipeline #16 — Construindo painel unificado município × ano")
    print(f"Janela: {ANO_INI}–{ANO_FIM} | Base deflator: dez/{DATA_BASE_DEFLATOR[0]}")
    print("=" * 70)

    # 1. Grade base
    grade   = construir_grade()
    df_ipca = carregar_ipca()

    # 2. Carregar todas as fontes
    lulc    = load_lulc()
    pec     = load_pecuaria()
    agri    = load_agricultura()
    perm    = load_permanentes()
    leite   = load_leite()
    mel     = load_mel()
    la      = load_la()
    ovinos  = load_ovinos_tosquiados()
    pib     = load_economico(df_ipca)
    pop     = load_populacao()
    sicor   = load_sicor(df_ipca)
    fogo    = load_fogo()
    censo   = load_censo_2017()
    abate   = load_abate()

    # 3. Joins sequenciais sobre a grade
    print("\n[join] Construindo wide table...")
    painel = grade.copy()
    fontes = [("lulc", lulc), ("pec", pec), ("agri", agri), ("perm", perm),
              ("leite", leite), ("mel", mel), ("la", la), ("ovinos", ovinos),
              ("pib", pib), ("pop", pop), ("sicor", sicor), ("abate", abate)]
    if fogo is not None:
        fontes.append(("fogo", fogo))
    for nome, df in fontes:
        painel = painel.merge(df, on=["cd_mun", "ano"], how="left")
        print(f"  + {nome}: shape = {painel.shape}")
    # Censo entra só em cd_mun (replicado em todos os anos)
    painel = painel.merge(censo, on="cd_mun", how="left")
    print(f"  + censo: shape = {painel.shape}")

    # 4. Métricas derivadas e slots vazios
    painel = derivar_metricas(painel)
    painel = adicionar_slots_vazios(painel)

    # 5. Sanity checks
    assert painel.duplicated(["cd_mun", "ano"]).sum() == 0, "duplicatas (cd_mun, ano)"
    n_munis = painel["cd_mun"].nunique()
    n_anos  = painel["ano"].nunique()
    print(f"\n[sanity] {n_munis} munis × {n_anos} anos = {n_munis * n_anos} linhas esperadas")
    print(f"[sanity] painel.shape = {painel.shape}")
    assert len(painel) == n_munis * n_anos, "linhas != munis × anos"

    # 6. Remover colunas 100% NaN (exceto chaves)
    cols_dado = [c for c in painel.columns if c not in ("cd_mun", "nm_mun", "ano")]
    cols_vazias = [c for c in cols_dado if painel[c].isna().all()]
    if cols_vazias:
        painel = painel.drop(columns=cols_vazias)
        print(f"\n[cleanup] {len(cols_vazias)} colunas 100% NaN removidas: {', '.join(cols_vazias[:5])}{'...' if len(cols_vazias) > 5 else ''}")

    # 7. Salvar
    painel = painel.sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    out_parquet = DIR_PROCESSED / "painel_unificado.parquet"
    out_csv     = DIR_PROCESSED / "painel_unificado.csv"
    painel.to_parquet(out_parquet, index=False)
    painel.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n[OK] {out_parquet.relative_to(ROOT)}")
    print(f"[OK] {out_csv.relative_to(ROOT)}")

    # 8. Diagnóstico de cobertura
    diagnostico_cobertura(painel)

    print("\n" + "=" * 70)
    print("CONCLUÍDO")
    print("=" * 70)
    print(f"Painel: {painel.shape[0]:,} linhas × {painel.shape[1]} colunas")
    print(f"Cobertura plena (todas as fontes): ano in [2013, 2023]")
    print(f"Slots vazios reservados: idhm* (1991/2000/2010 disponíveis pós-merge IDH-M)")


if __name__ == "__main__":
    main()
