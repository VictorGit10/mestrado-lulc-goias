"""
Pipeline #8 — Crédito Rural × Uso da Terra em Goiás (2013–2023)
================================================================

Cruza dados de crédito rural (SICOR/BACEN) com mudança de uso da terra
(MapBiomas) nos 246 municípios de Goiás. Produz painel municipal com
métricas de crédito por hectare de pastagem e gráficos prontos para
a dissertação.

Janela de sobreposição: 2013–2023 (SICOR + MapBiomas + PIB municipais).
O gráfico UF estende a 2014–2026 com anotação "(parcial)".

Como rodar:
    python analise_credito_uso_terra.py

Pré-requisitos (CSVs já gerados pelos pipelines anteriores):
    - data/processed/sicor_painel_municipal.csv   (Pipeline #6)
    - data/processed/sicor_uf_anual.csv            (Pipeline #6)
    - data/processed/mapbiomas_munis_goias.csv     (Pipeline #4)
    - data/processed/sidra_1737_ipca.csv           (Pipeline #1)
    - data/processed/sidra_5938_pib_municipal.csv   (Pipeline #3)
    - data/processed/sidra_censo_agro_2017.csv      (Pipeline #7)
    - data/processed/painel_pastagem_soja_municipal.csv  (Pipeline #5)

Saída:
    CSVs em data/processed/
    PNGs em outputs/ (12 a 18)
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT           = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUTPUT    = ROOT / "outputs"
for d in (DIR_PROCESSED, DIR_OUTPUT):
    d.mkdir(parents=True, exist_ok=True)

ANO_SICOR_INI  = 2013
ANO_SICOR_FIM  = 2026   # parcial
ANO_OVERLAP_INI = 2013
ANO_OVERLAP_FIM = 2023   # PIB termina 2023
ANO_RECENTE    = 2023
DATA_BASE_DEFLATOR = (2024, 12)

CLS_PASTAGEM = 15
CLS_SOJA     = 39

COR_CUSTEIO      = "#2e7d32"
COR_INVESTIMENTO = "#1565c0"
COR_COMERC       = "#e65100"
COR_PASTAGEM     = "#7a4f00"
COR_SOJA         = "#f5c242"
COR_REFERENCIA   = "#888888"

# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def _salvar(fig: plt.Figure, nome: str) -> None:
    fig.savefig(DIR_OUTPUT / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] outputs/{nome}")


def _anotar_top(ax, df, x_col, y_col, label_col, n=5,
                offsets=None, fontsize=7) -> None:
    """Anota os n maiores pontos num scatter."""
    top = df.nlargest(n, y_col)
    if offsets is None:
        offsets = [(25, 15), (25, -15)] * ((n // 2) + 1)
    for (_, row), off in zip(top.iterrows(), offsets[:n]):
        ax.annotate(
            row[label_col],
            xy=(row[x_col], row[y_col]),
            xytext=off, textcoords="offset points",
            fontsize=fontsize, color="black",
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )


# ---------------------------------------------------------------------------
# 1. Carregamento de dados
# ---------------------------------------------------------------------------

def carregar_ipca() -> pd.DataFrame:
    print("[...] Carregando IPCA...")
    df = pd.read_csv(DIR_PROCESSED / "sidra_1737_ipca.csv", encoding="utf-8")
    df = df.dropna(subset=["indice_acum"])
    print(f"  {len(df)} registros, {df['ano'].min()}-{df['ano'].max()}")
    return df


def deflacionar(df_nominal: pd.DataFrame, col_val: str, df_ipca: pd.DataFrame) -> pd.Series:
    """Deflaciona col_val para R$ de DATA_BASE_DEFLATOR usando dez de cada ano."""
    ano_base, mes_base = DATA_BASE_DEFLATOR
    idx_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base), "indice_acum"
    ].iloc[0]
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "idx_dez"}
    )
    merged = df_nominal.merge(df_dez, on="ano", how="left")
    return merged[col_val] * (idx_base / merged["idx_dez"])


def carregar_sicor_municipal() -> pd.DataFrame:
    print("[...] Carregando SICOR municipal...")
    df = pd.read_csv(DIR_PROCESSED / "sicor_painel_municipal.csv", encoding="utf-8")
    df["cd_mun"] = df["cd_mun"].astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["area_ha"] = pd.to_numeric(df["area_ha"], errors="coerce").fillna(0)
    df["n_operacoes"] = pd.to_numeric(df["n_operacoes"], errors="coerce").fillna(0).astype(int)
    print(f"  {len(df):,} linhas, {df['cd_mun'].nunique()} munis, "
          f"{df['ano'].min()}-{df['ano'].max()}")
    print(f"  Finalidades: {df['finalidade'].unique().tolist()}")
    print(f"  Valor total nominal: R$ {df['valor'].sum()/1e9:.1f} bi")
    return df


def carregar_sicor_uf() -> pd.DataFrame:
    print("[...] Carregando SICOR UF...")
    df = pd.read_csv(DIR_PROCESSED / "sicor_uf_anual.csv", encoding="utf-8")
    # Agregar mensal → anual
    df_agg = df.groupby(["ano", "finalidade", "nm_produto"], as_index=False).agg(
        valor=("valor", "sum"),
        n_contratos=("n_contratos", "sum"),
        area_ha=("area_ha", "sum"),
    )
    # Limpar aspas residuais em nm_produto
    df_agg["nm_produto"] = df_agg["nm_produto"].str.strip('"')
    print(f"  {len(df_agg):,} linhas (ano × finalidade × produto)")
    print(f"  Finalidades: {df_agg['finalidade'].unique().tolist()}")
    return df_agg


def carregar_mapbiomas_municipal() -> pd.DataFrame:
    print("[...] Carregando MapBiomas municipal (pastagem + soja)...")
    df = pd.read_csv(DIR_PROCESSED / "mapbiomas_munis_goias.csv", encoding="utf-8")
    df = df[df["class_id"].isin([CLS_PASTAGEM, CLS_SOJA])].copy()
    pivot = df.pivot_table(
        index=["cd_mun", "ano"],
        columns="class_id",
        values="area_ha",
        fill_value=0,
    ).reset_index()
    col_map = {CLS_PASTAGEM: "pastagem_ha", CLS_SOJA: "soja_ha"}
    pivot = pivot.rename(columns=col_map)
    for col in ("pastagem_ha", "soja_ha"):
        if col not in pivot.columns:
            pivot[col] = 0.0
    # Recuperar nm_mun
    nomes = df[["cd_mun", "nm_mun"]].drop_duplicates()
    pivot = pivot.merge(nomes, on="cd_mun", how="left")
    pivot = pivot[["cd_mun", "nm_mun", "ano", "pastagem_ha", "soja_ha"]].sort_values(
        ["cd_mun", "ano"]
    ).reset_index(drop=True)
    print(f"  {len(pivot):,} linhas, {pivot['cd_mun'].nunique()} munis")
    return pivot


def carregar_pib_municipal() -> pd.DataFrame:
    print("[...] Carregando PIB municipal...")
    df = pd.read_csv(DIR_PROCESSED / "sidra_5938_pib_municipal.csv", encoding="utf-8")
    # Filtrar PIB total (37) e VA agro (513)
    df_filtrado = df[df["variavel_id"].isin([37, 513])].copy()
    pivot = df_filtrado.pivot_table(
        index=["cd_mun", "ano"],
        columns="variavel_id",
        values="valor",
    ).reset_index()
    pivot = pivot.rename(columns={37: "pib_mil_reais", 513: "va_agro_mil_reais"})
    pivot["pib_rs"] = pivot["pib_mil_reais"] * 1000
    pivot["va_agro_rs"] = pivot["va_agro_mil_reais"] * 1000
    # Recuperar nm_mun
    nomes = df_filtrado[["cd_mun", "nm_mun"]].drop_duplicates()
    pivot = pivot.merge(nomes, on="cd_mun", how="left")
    cols_out = [c for c in ["cd_mun", "nm_mun", "ano", "pib_rs", "va_agro_rs"] if c in pivot.columns]
    pivot = pivot[cols_out].sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    print(f"  {len(pivot):,} linhas, anos {pivot['ano'].min()}-{pivot['ano'].max()}")
    return pivot


def carregar_censo_agro() -> pd.DataFrame:
    print("[...] Carregando Censo Agro 2017...")
    df = pd.read_csv(DIR_PROCESSED / "sidra_censo_agro_2017.csv", encoding="utf-8")
    df["cd_mun"] = df["cd_mun"].astype(int)
    print(f"  {len(df)} munis × {len(df.columns)} colunas")
    return df


def carregar_painel_past_soja() -> pd.DataFrame:
    print("[...] Carregando painel pastagem↔soja...")
    df = pd.read_csv(DIR_PROCESSED / "painel_pastagem_soja_municipal.csv", encoding="utf-8")
    print(f"  {len(df)} munis")
    return df


# ---------------------------------------------------------------------------
# 2. Tabelas derivadas
# ---------------------------------------------------------------------------

def gerar_credito_municipal_anual(
    df_sicor: pd.DataFrame, df_ipca: pd.DataFrame, df_mapb: pd.DataFrame
) -> pd.DataFrame:
    """Agrega SICOR municipal por (ano, cd_mun), deflaciona e calcula crédito/ha."""
    print("\n[...] Gerando painel de crédito municipal anual...")

    # Agregar por ano × município × finalidade
    agg = df_sicor.groupby(["ano", "cd_mun", "finalidade"], as_index=False).agg(
        valor=("valor", "sum"),
        n_operacoes=("n_operacoes", "sum"),
    )
    # Pivotar finalidade em colunas
    pivot = agg.pivot_table(
        index=["ano", "cd_mun"],
        columns="finalidade",
        values=["valor", "n_operacoes"],
        fill_value=0,
    ).reset_index()
    # Achatar multi-index
    pivot.columns = [
        "ano" if c[0] == "" else f"{c[0]}_{c[1]}" if c[1] else c[0]
        for c in pivot.columns
    ]
    # Renomear para nomes simples
    rename_map = {}
    for c in pivot.columns:
        if "Custeio" in c:
            rename_map[c] = c.replace("valor_Custeio", "valor_custeio").replace(
                "n_operacoes_Custeio", "n_op_custeio"
            )
        elif "Investimento" in c:
            rename_map[c] = c.replace("valor_Investimento", "valor_investimento").replace(
                "n_operacoes_Investimento", "n_op_investimento"
            )
    pivot = pivot.rename(columns=rename_map)

    # Se colunas de finalidade não existirem (só 1 finalidade), criar com 0
    for col in ["valor_custeio", "valor_investimento", "n_op_custeio", "n_op_investimento"]:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["valor_total"] = pivot["valor_custeio"] + pivot["valor_investimento"]
    pivot["n_op_total"] = pivot["n_op_custeio"] + pivot["n_op_investimento"]

    # Deflacionar
    pivot["valor_custeio_real"] = deflacionar(pivot, "valor_custeio", df_ipca)
    pivot["valor_investimento_real"] = deflacionar(pivot, "valor_investimento", df_ipca)
    pivot["valor_total_real"] = pivot["valor_custeio_real"] + pivot["valor_investimento_real"]

    # Juntar pastagem do MapBiomas
    pastagem = df_mapb[["cd_mun", "ano", "pastagem_ha"]].copy()
    pivot = pivot.merge(pastagem, on=["cd_mun", "ano"], how="left")
    pivot["pastagem_ha"] = pivot["pastagem_ha"].fillna(0)

    # Crédito por hectare de pastagem
    pivot["credito_por_ha_pastagem"] = np.where(
        pivot["pastagem_ha"] > 0,
        pivot["valor_total_real"] / pivot["pastagem_ha"],
        np.nan,
    )

    # Juntar nm_mun
    nomes = df_sicor[["cd_mun", "nm_mun"]].drop_duplicates()
    pivot = pivot.merge(nomes, on="cd_mun", how="left")

    # Ordenar colunas
    cols_out = [
        "ano", "cd_mun", "nm_mun",
        "valor_custeio", "valor_investimento", "valor_total",
        "valor_custeio_real", "valor_investimento_real", "valor_total_real",
        "n_op_custeio", "n_op_investimento", "n_op_total",
        "pastagem_ha", "credito_por_ha_pastagem",
    ]
    pivot = pivot[[c for c in cols_out if c in pivot.columns]].sort_values(
        ["cd_mun", "ano"]
    ).reset_index(drop=True)

    pivot.to_csv(DIR_PROCESSED / "credito_municipal_anual.csv", index=False)
    print(f"[OK] credito_municipal_anual.csv — {len(pivot):,} linhas")

    # Diagnóstico: munis faltantes
    munis_sicor = set(pivot["cd_mun"].unique())
    munis_mapb = set(df_mapb["cd_mun"].unique())
    faltantes = munis_mapb - munis_sicor
    if faltantes:
        nm_falt = df_mapb[df_mapb["cd_mun"].isin(faltantes)]["nm_mun"].unique()
        print(f"  Munis no MapBiomas mas NÃO no SICOR: {list(nm_falt)}")

    return pivot


def gerar_credito_produto_anual(
    df_sicor_uf: pd.DataFrame, df_ipca: pd.DataFrame
) -> pd.DataFrame:
    """Agrega SICOR UF por (ano, produto), deflaciona."""
    print("\n[...] Gerando painel de crédito por produto...")

    agg = df_sicor_uf.groupby(["ano", "nm_produto"], as_index=False).agg(
        valor_nominal=("valor", "sum"),
        n_contratos=("n_contratos", "sum"),
    )
    agg["valor_real"] = deflacionar(agg, "valor_nominal", df_ipca)

    agg.to_csv(DIR_PROCESSED / "credito_produto_anual.csv", index=False)
    print(f"[OK] credito_produto_anual.csv — {len(agg):,} linhas")
    return agg


def gerar_painel_credito_lulc(
    df_credito_muni: pd.DataFrame,
    df_mapb: pd.DataFrame,
    df_pib: pd.DataFrame,
) -> pd.DataFrame:
    """Merge crédito + pastagem/soja + PIB para 2013-2023."""
    print("\n[...] Gerando painel crédito × LULC (2013-2023)...")

    # Filtrar janela de sobreposição
    credito = df_credito_muni[
        (df_credito_muni["ano"] >= ANO_OVERLAP_INI) & (df_credito_muni["ano"] <= ANO_OVERLAP_FIM)
    ][["ano", "cd_mun", "valor_custeio_real", "valor_investimento_real",
       "valor_total_real", "pastagem_ha", "credito_por_ha_pastagem"]].copy()

    lulc = df_mapb[
        (df_mapb["ano"] >= ANO_OVERLAP_INI) & (df_mapb["ano"] <= ANO_OVERLAP_FIM)
    ][["cd_mun", "ano", "pastagem_ha", "soja_ha"]].copy()
    lulc = lulc.rename(columns={"pastagem_ha": "pastagem_ha_mapb", "soja_ha": "soja_ha"})

    pib = df_pib[
        (df_pib["ano"] >= ANO_OVERLAP_INI) & (df_pib["ano"] <= ANO_OVERLAP_FIM)
    ][["cd_mun", "ano", "pib_rs", "va_agro_rs"]].copy().reset_index(drop=True)

    # Deflacionar PIB. O reset_index acima é crítico: deflacionar() faz merge
    # interno e retorna Series com índice 0..N-1; sem reset, o filtro de ano
    # mantém índices esparsos (ex.: [11, 12, ...]) e a atribuição embaralha
    # valores entre municípios via alinhamento por índice do pandas.
    ipca = carregar_ipca()
    pib["pib_real_rs"] = deflacionar(pib, "pib_rs", ipca)
    pib["va_agro_real_rs"] = deflacionar(pib, "va_agro_rs", ipca)

    # Merge
    painel = credito.merge(lulc, on=["cd_mun", "ano"], how="inner")
    painel = painel.merge(pib[["cd_mun", "ano", "pib_real_rs", "va_agro_real_rs"]],
                          on=["cd_mun", "ano"], how="left")
    painel["participacao_agro_pct"] = np.where(
        painel["pib_real_rs"] > 0,
        painel["va_agro_real_rs"] / painel["pib_real_rs"] * 100,
        np.nan,
    )

    # Recuperar nm_mun
    nomes = df_credito_muni[["cd_mun", "nm_mun"]].drop_duplicates()
    painel = painel.merge(nomes, on="cd_mun", how="left")

    cols_out = [
        "ano", "cd_mun", "nm_mun",
        "valor_custeio_real", "valor_investimento_real", "valor_total_real",
        "pastagem_ha_mapb", "soja_ha",
        "pib_real_rs", "va_agro_real_rs", "participacao_agro_pct",
        "credito_por_ha_pastagem",
    ]
    painel = painel[[c for c in cols_out if c in painel.columns]].sort_values(
        ["cd_mun", "ano"]
    ).reset_index(drop=True)

    painel.to_csv(DIR_PROCESSED / "painel_credito_lulc.csv", index=False)
    print(f"[OK] painel_credito_lulc.csv — {len(painel):,} linhas")
    return painel


# ---------------------------------------------------------------------------
# 3. Gráficos
# ---------------------------------------------------------------------------

def grafico_credito_uf_serie(df_sicor_uf: pd.DataFrame, df_ipca: pd.DataFrame) -> None:
    """Gráfico 12: série temporal do crédito rural em Goiás por finalidade."""
    print("\n[...] Gerando gráfico 12: crédito UF série...")

    # Agregar por ano e finalidade
    agg = df_sicor_uf.groupby(["ano", "finalidade"], as_index=False).agg(
        valor=("valor", "sum"),
    )
    # Deflacionar
    agg["valor_real"] = deflacionar(agg, "valor", df_ipca)

    # Pivotar
    pivot = agg.pivot_table(index="ano", columns="finalidade", values="valor_real",
                            fill_value=0).reset_index()
    pivot = pivot.sort_values("ano")

    anos = pivot["ano"].values
    custeio = pivot.get("Custeio", pd.Series(0, index=pivot.index)).values
    invest = pivot.get("Investimento", pd.Series(0, index=pivot.index)).values
    comerc = pivot.get("Comercializacao", pd.Series(0, index=pivot.index)).values

    fig, ax = plt.subplots(figsize=(13, 6))

    bar_width = 0.7
    ax.bar(anos, custeio / 1e9, bar_width, label="Custeio", color=COR_CUSTEIO, alpha=0.85)
    ax.bar(anos, invest / 1e9, bar_width, bottom=custeio / 1e9,
           label="Investimento", color=COR_INVESTIMENTO, alpha=0.85)
    ax.bar(anos, comerc / 1e9, bar_width,
           bottom=(custeio + invest) / 1e9,
           label="Comercialização", color=COR_COMERC, alpha=0.85)

    # Anotação "(parcial)" em 2025 e 2026
    for ano_parc in [2025, 2026]:
        if ano_parc in anos:
            ax.annotate("(parcial)", xy=(ano_parc, 0), xytext=(ano_parc, -0.3),
                        fontsize=8, ha="center", color="gray")

    ax.set_xlabel("Ano")
    ax.set_ylabel(u"R$ bilhões (base dez/2024)")
    ax.set_title(u"Crédito Rural em Goiás por Finalidade (2013–2026, valores deflacionados)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2, axis="y")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
    fig.tight_layout()
    _salvar(fig, "12_credito_uf_serie_2013-2024.png")


def grafico_credito_pastagem_scatter(
    df_painel: pd.DataFrame, df_past_soja: pd.DataFrame
) -> None:
    """Gráfico 13: scatter crédito/ha pastagem vs Δpastagem."""
    print("\n[...] Gerando gráfico 13: scatter crédito/pastagem...")

    # Agregar crédito por município no período 2013-2023
    credito_muni = df_painel.groupby("cd_mun", as_index=False).agg(
        credito_total_real=("valor_total_real", "sum"),
        pastagem_media=("pastagem_ha_mapb", "mean"),
    )
    credito_muni["credito_por_ha"] = np.where(
        credito_muni["pastagem_media"] > 0,
        credito_muni["credito_total_real"] / credito_muni["pastagem_media"],
        np.nan,
    )

    # Merge com painel pastagem↔soja
    merged = credito_muni.merge(
        df_past_soja[["cd_mun", "nm_mun", "delta_pastagem_ha", "intensidade_soja",
                       "pastagem_1985_ha"]],
        on="cd_mun", how="inner",
    )
    merged = merged.dropna(subset=["credito_por_ha", "delta_pastagem_ha"])

    fig, ax = plt.subplots(figsize=(11, 9))

    intensidade = merged["intensidade_soja"].fillna(0)
    log_intensidade = np.log10(intensidade + 1)

    scatter = ax.scatter(
        merged["delta_pastagem_ha"] / 1e3,
        merged["credito_por_ha"],
        c=log_intensidade,
        cmap="YlOrBr",
        s=np.clip(merged["pastagem_media"] / 2e3, 8, 200),
        alpha=0.7, edgecolors="gray", linewidths=0.3,
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(u"Intensidade de soja (Δsoja / pastagem 1985)")
    tick_vals = [0, 0.2, 0.5, 1.0, 2.0, 3.5]
    cbar.set_ticks([np.log10(v + 1) for v in tick_vals])
    cbar.set_ticklabels([f"{v:.1f}" for v in tick_vals])

    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)

    _anotar_top(ax, merged, "delta_pastagem_ha", "credito_por_ha", "nm_mun", n=8,
                offsets=[(25, 12), (25, -12), (-70, 12), (25, 12), (25, -12),
                          (25, 12), (25, -12), (-70, -12)])

    ax.set_xlabel(u"Variação de pastagem (1000 ha, 2024 − 1985)")
    ax.set_ylabel(u"Crédito total por ha de pastagem (R$/ha, 2013–2023)")
    ax.set_title(u"Crédito por Hectare de Pastagem vs Variação de Pastagem")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    _salvar(fig, "13_scatter_credito_pastagem.png")


def grafico_composicao_produto(df_credito_prod: pd.DataFrame) -> None:
    """Gráfico 14: evolução dos 10 principais produtos do crédito rural."""
    print("\n[...] Gerando gráfico 14: composição por produto...")

    # Top 10 produtos por valor total 2013-2023
    total_por_produto = df_credito_prod.groupby("nm_produto")["valor_real"].sum()
    top10 = total_por_produto.nlargest(10).index.tolist()

    df_top10 = df_credito_prod[
        (df_credito_prod["nm_produto"].isin(top10)) &
        (df_credito_prod["ano"] >= ANO_OVERLAP_INI) &
        (df_credito_prod["ano"] <= ANO_OVERLAP_FIM)
    ].copy()

    # "Outros"
    df_outros = df_credito_prod[
        (~df_credito_prod["nm_produto"].isin(top10)) &
        (df_credito_prod["ano"] >= ANO_OVERLAP_INI) &
        (df_credito_prod["ano"] <= ANO_OVERLAP_FIM)
    ].groupby("ano", as_index=False).agg(valor_real=("valor_real", "sum"))
    df_outros["nm_produto"] = "Outros"

    pivot_top = df_top10.pivot_table(
        index="ano", columns="nm_produto", values="valor_real", fill_value=0
    ).reset_index()
    pivot_top = pivot_top.merge(df_outros[["ano", "valor_real"]].rename(
        columns={"valor_real": "Outros"}
    ), on="ano", how="left").fillna(0)

    fig, ax = plt.subplots(figsize=(13, 7))
    cores = plt.cm.tab10(np.linspace(0, 1, len(top10) + 1))
    for i, prod in enumerate(top10):
        if prod in pivot_top.columns:
            ax.plot(pivot_top["ano"], pivot_top[prod] / 1e9,
                    marker="o", ms=4, lw=1.8, label=prod, color=cores[i])
    if "Outros" in pivot_top.columns:
        ax.plot(pivot_top["ano"], pivot_top["Outros"] / 1e9,
                ls="--", lw=1.5, label="Outros", color="gray")

    ax.set_xlabel("Ano")
    ax.set_ylabel(u"R$ bilhões (base dez/2024)")
    ax.set_title(u"Composição do Crédito Rural por Produto — Top 10 (Goiás 2013–2023)")
    ax.legend(fontsize=8, ncol=2, loc="upper left")
    ax.grid(True, alpha=0.2, axis="y")
    fig.tight_layout()
    _salvar(fig, "14_composicao_produto_credito.png")


def grafico_credito_soja_scatter(
    df_painel: pd.DataFrame, df_past_soja: pd.DataFrame
) -> None:
    """Gráfico 15: scatter crédito total vs Δsoja."""
    print("\n[...] Gerando gráfico 15: scatter crédito vs soja...")

    # Agregar crédito por município (2013-2023)
    credito_muni = df_painel.groupby("cd_mun", as_index=False).agg(
        credito_total_real=("valor_total_real", "sum"),
    )

    merged = credito_muni.merge(
        df_past_soja[["cd_mun", "nm_mun", "delta_soja_ha", "intensidade_soja",
                       "pastagem_1985_ha"]],
        on="cd_mun", how="inner",
    )
    merged = merged.dropna(subset=["credito_total_real", "delta_soja_ha"])

    # Correlação
    corr = merged["credito_total_real"].corr(merged["delta_soja_ha"])

    fig, ax = plt.subplots(figsize=(11, 9))

    intensidade = merged["intensidade_soja"].fillna(0)
    log_intensidade = np.log10(intensidade + 1)

    scatter = ax.scatter(
        merged["credito_total_real"] / 1e9,
        merged["delta_soja_ha"] / 1e3,
        c=log_intensidade,
        cmap="YlOrBr",
        s=np.clip(merged["pastagem_1985_ha"] / 5e3, 8, 200),
        alpha=0.7, edgecolors="gray", linewidths=0.3,
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(u"Intensidade de soja (Δsoja / pastagem 1985)")
    tick_vals = [0, 0.2, 0.5, 1.0, 2.0, 3.5]
    cbar.set_ticks([np.log10(v + 1) for v in tick_vals])
    cbar.set_ticklabels([f"{v:.1f}" for v in tick_vals])

    # Anotar top 5 por delta_soja
    top5 = merged.nlargest(5, "delta_soja_ha")
    for _, row in top5.iterrows():
        ax.annotate(
            row["nm_mun"],
            xy=(row["credito_total_real"] / 1e9, row["delta_soja_ha"] / 1e3),
            xytext=(15, 10), textcoords="offset points",
            fontsize=7, color="black",
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )

    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)

    ax.text(0.02, 0.97, f"Pearson r = {corr:.3f}",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax.set_xlabel(u"Crédito rural total (R$ bilhões, 2013–2023)")
    ax.set_ylabel(u"Variação de soja (1000 ha, 2024 − 1985)")
    ax.set_title(u"Crédito Rural Total vs Expansão da Soja (2013–2023)")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    _salvar(fig, "15_scatter_credito_soja.png")


def grafico_credito_intensidade_bar(
    df_credito_muni: pd.DataFrame, df_mapb: pd.DataFrame
) -> None:
    """Gráfico 16: top 20 municípios por crédito/ha de pastagem."""
    print("\n[...] Gerando gráfico 16: barras crédito/ha...")

    # Usar ano mais recente com dados completos
    anos_disp = sorted(df_credito_muni["ano"].unique())
    ano_recente = ANO_RECENTE if ANO_RECENTE in anos_disp else anos_disp[-1]

    df_recente = df_credito_muni[df_credito_muni["ano"] == ano_recente].copy()
    df_recente = df_recente.dropna(subset=["credito_por_ha_pastagem"])
    df_recente = df_recente[df_recente["credito_por_ha_pastagem"] > 0]

    top20 = df_recente.nlargest(20, "credito_por_ha_pastagem").sort_values(
        "credito_por_ha_pastagem", ascending=True
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

    # Painel esquerdo: crédito/ha (Custeio + Investimento empilhados)
    ax1.barh(top20["nm_mun"], top20["valor_custeio_real"] / 1e6,
             color=COR_CUSTEIO, alpha=0.85, label="Custeio")
    ax1.barh(top20["nm_mun"], top20["valor_investimento_real"] / 1e6,
             left=top20["valor_custeio_real"] / 1e6,
             color=COR_INVESTIMENTO, alpha=0.85, label="Investimento")
    ax1.set_xlabel(u"Crédito por ha de pastagem (R$/ha)")
    ax1.set_title(f"Top 20 — Crédito/ha de Pastagem ({ano_recente})")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.2, axis="x")

    # Painel direito: valor total em R$ milhões
    top20_abs = top20.sort_values("valor_total_real", ascending=True)
    ax2.barh(top20_abs["nm_mun"], top20_abs["valor_total_real"] / 1e6,
             color="#555555", alpha=0.85, label="Total")
    ax2.set_xlabel(u"Crédito total (R$ milhões)")
    ax2.set_title(f"Top 20 — Volume Total ({ano_recente})")
    ax2.grid(True, alpha=0.2, axis="x")

    fig.suptitle(u"Crédito Rural por Hectare de Pastagem — Top 20 Municípios",
                 fontsize=13, y=1.01)
    fig.tight_layout()
    _salvar(fig, "16_barras_credito_intensidade.png")


def grafico_evolucao_temporal(
    df_credito_muni: pd.DataFrame, df_mapb: pd.DataFrame, df_ipca: pd.DataFrame
) -> None:
    """Gráfico 17: evolução crédito × pastagem (2 painéis)."""
    print("\n[...] Gerando gráfico 17: evolução temporal crédito × pastagem...")

    # Painel (a): série temporal UF — eixo duplo
    credito_estado = df_credito_muni.groupby("ano", as_index=False).agg(
        valor_total_real=("valor_total_real", "sum"),
    )

    pastagem_estado = df_mapb.groupby("ano", as_index=False).agg(
        pastagem_ha=("pastagem_ha", "sum"),
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # (a) Eixo duplo
    ax1b = ax1.twinx()
    l1, = ax1.plot(pastagem_estado["ano"], pastagem_estado["pastagem_ha"] / 1e6,
                    color=COR_PASTAGEM, lw=2, marker="o", ms=3, label="Pastagem")
    l2, = ax1b.plot(credito_estado["ano"], credito_estado["valor_total_real"] / 1e9,
                     color=COR_INVESTIMENTO, lw=2, marker="s", ms=3, label="Crédito rural")

    ax1.set_xlabel("Ano")
    ax1.set_ylabel(u"Pastagem (milhões ha)", color=COR_PASTAGEM)
    ax1b.set_ylabel(u"Crédito rural (R$ bilhões)", color=COR_INVESTIMENTO)
    ax1.set_title(u"Evolução da Pastagem e do Crédito Rural em Goiás (2013–2024)")
    ax1.legend([l1, l2], ["Pastagem", "Crédito rural"], fontsize=9, loc="upper left")
    ax1.grid(True, alpha=0.2)
    ax1.set_xlim(ANO_OVERLAP_INI, 2024)

    # (b) Correlação anual crédito/ha vs Δpastagem
    anos_corr = list(range(ANO_OVERLAP_INI + 1, ANO_OVERLAP_FIM + 1))
    corr_por_ano = []
    for ano in anos_corr:
        cred_ano = df_credito_muni[
            (df_credito_muni["ano"] == ano) &
            (df_credito_muni["credito_por_ha_pastagem"].notna()) &
            (df_credito_muni["credito_por_ha_pastagem"] > 0)
        ][["cd_mun", "credito_por_ha_pastagem"]]

        # Delta pastagem do ano base (2013) até o ano corrente
        past_ini = df_mapb[df_mapb["ano"] == ANO_OVERLAP_INI][["cd_mun", "pastagem_ha"]].rename(
            columns={"pastagem_ha": "past_ini"}
        )
        past_fim = df_mapb[df_mapb["ano"] == ano][["cd_mun", "pastagem_ha"]].rename(
            columns={"pastagem_ha": "past_fim"}
        )
        delta = past_ini.merge(past_fim, on="cd_mun", how="inner")
        delta["delta_pastagem_ha"] = delta["past_fim"] - delta["past_ini"]

        merged_corr = cred_ano.merge(delta[["cd_mun", "delta_pastagem_ha"]], on="cd_mun", how="inner")
        if len(merged_corr) > 10:
            r = merged_corr["credito_por_ha_pastagem"].corr(merged_corr["delta_pastagem_ha"])
            corr_por_ano.append({"ano": ano, "corr": r})

    df_corr = pd.DataFrame(corr_por_ano)

    ax2.bar(df_corr["ano"], df_corr["corr"], color="#4575b4", alpha=0.7)
    ax2.axhline(0, color="black", lw=0.5)
    ax2.set_xlabel("Ano")
    ax2.set_ylabel(u"Correlação (Pearson r)")
    ax2.set_title(u"Correlação Anual: Crédito/ha vs ΔPastagem (base 2013)")
    ax2.grid(True, alpha=0.2, axis="y")

    fig.tight_layout(h_pad=3)
    _salvar(fig, "17_evolucao_credito_pastagem.png")


def grafico_credito_censo_agro(
    df_credito_muni: pd.DataFrame, df_censo: pd.DataFrame,
    df_past_soja: pd.DataFrame,
) -> None:
    """Gráfico 18: scatter crédito/ha vs % agricultura familiar."""
    print("\n[...] Gerando gráfico 18: scatter crédito × Censo Agro...")

    # Agregar crédito por município (2013-2023)
    credito_muni = df_credito_muni.groupby("cd_mun", as_index=False).agg(
        credito_total_real=("valor_total_real", "sum"),
    )

    # Crédito/ha: usar pastagem média 2013-2023 do painel
    pastagem_media = df_credito_muni.groupby("cd_mun", as_index=False).agg(
        pastagem_media=("pastagem_ha", "mean"),
    )
    credito_muni = credito_muni.merge(pastagem_media, on="cd_mun", how="left")
    credito_muni["credito_por_ha"] = np.where(
        credito_muni["pastagem_media"] > 0,
        credito_muni["credito_total_real"] / credito_muni["pastagem_media"],
        np.nan,
    )

    # Merge com Censo Agro e painel past-soja
    merged = credito_muni.merge(
        df_censo[["cd_mun", "ca_pct_familiar"]],
        on="cd_mun", how="inner",
    ).merge(
        df_past_soja[["cd_mun", "nm_mun", "intensidade_soja"]],
        on="cd_mun", how="inner",
    )
    merged = merged.dropna(subset=["credito_por_ha", "ca_pct_familiar"])

    # Medianas para linhas de referência
    med_credito = merged["credito_por_ha"].median()
    med_familiar = merged["ca_pct_familiar"].median()

    fig, ax = plt.subplots(figsize=(11, 9))

    intensidade = merged["intensidade_soja"].fillna(0)
    log_intensidade = np.log10(intensidade + 1)

    scatter = ax.scatter(
        merged["ca_pct_familiar"],
        merged["credito_por_ha"],
        c=log_intensidade,
        cmap="YlOrBr",
        s=np.clip(merged["pastagem_media"] / 2e3, 8, 150),
        alpha=0.7, edgecolors="gray", linewidths=0.3,
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(u"Intensidade de soja (Δsoja / pastagem 1985)")
    tick_vals = [0, 0.2, 0.5, 1.0, 2.0, 3.5]
    cbar.set_ticks([np.log10(v + 1) for v in tick_vals])
    cbar.set_ticklabels([f"{v:.1f}" for v in tick_vals])

    # Linhas de mediana
    ax.axhline(med_credito, color="gray", ls="--", lw=1, alpha=0.6)
    ax.axvline(med_familiar, color="gray", ls="--", lw=1, alpha=0.6)

    # Quadrantes
    ax.text(0.03, 0.97, u"Alto crédito,\nagricultura familiar",
            transform=ax.transAxes, fontsize=8, va="top", color="#333",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    ax.text(0.97, 0.97, u"Alto crédito,\nagricultura patronal",
            transform=ax.transAxes, fontsize=8, va="top", ha="right", color="#333",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    ax.text(0.03, 0.03, u"Baixo crédito,\nagricultura familiar",
            transform=ax.transAxes, fontsize=8, va="bottom", color="#333",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    ax.text(0.97, 0.03, u"Baixo crédito,\nagricultura patronal",
            transform=ax.transAxes, fontsize=8, va="bottom", ha="right", color="#333",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # Anotar top 5
    top5 = merged.nlargest(5, "credito_por_ha")
    for _, row in top5.iterrows():
        ax.annotate(
            row["nm_mun"],
            xy=(row["ca_pct_familiar"], row["credito_por_ha"]),
            xytext=(15, 10), textcoords="offset points",
            fontsize=7, color="black",
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )

    ax.set_xlabel(u"% estabelecimentos familiares (Censo Agro 2017)")
    ax.set_ylabel(u"Crédito por ha de pastagem (R$/ha, 2013–2023)")
    ax.set_title(u"Crédito Rural vs Agricultura Familiar nos Municípios de Goiás")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    _salvar(fig, "18_scatter_credito_censo_agro.png")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Pipeline #8 -- Crédito Rural x Uso da Terra (Goiás 2013-2023)")
    print("=" * 70)

    # 1. Carregar dados
    df_ipca       = carregar_ipca()
    df_sicor_muni = carregar_sicor_municipal()
    df_sicor_uf   = carregar_sicor_uf()
    df_mapb       = carregar_mapbiomas_municipal()
    df_pib        = carregar_pib_municipal()
    df_censo      = carregar_censo_agro()
    df_past_soja  = carregar_painel_past_soja()

    # 2. Gerar tabelas derivadas
    df_credito_muni = gerar_credito_municipal_anual(df_sicor_muni, df_ipca, df_mapb)
    df_credito_prod = gerar_credito_produto_anual(df_sicor_uf, df_ipca)
    df_painel_lulc  = gerar_painel_credito_lulc(df_credito_muni, df_mapb, df_pib)

    # 3. Gráficos
    grafico_credito_uf_serie(df_sicor_uf, df_ipca)
    grafico_credito_pastagem_scatter(df_painel_lulc, df_past_soja)
    grafico_composicao_produto(df_credito_prod)
    grafico_credito_soja_scatter(df_painel_lulc, df_past_soja)
    grafico_credito_intensidade_bar(df_credito_muni, df_mapb)
    grafico_evolucao_temporal(df_credito_muni, df_mapb, df_ipca)
    grafico_credito_censo_agro(df_credito_muni, df_censo, df_past_soja)

    # 4. Resumo
    print("\n" + "=" * 70)
    print("Pipeline #8 concluído!")
    print("=" * 70)
    print("\nCSVs gerados em data/processed/:")
    print("  - credito_municipal_anual.csv")
    print("  - credito_produto_anual.csv")
    print("  - painel_credito_lulc.csv")
    print("\nPNGs gerados em outputs/:")
    print("  - 12_credito_uf_serie_2013-2024.png")
    print("  - 13_scatter_credito_pastagem.png")
    print("  - 14_composicao_produto_credito.png")
    print("  - 15_scatter_credito_soja.png")
    print("  - 16_barras_credito_intensidade.png")
    print("  - 17_evolucao_credito_pastagem.png")
    print("  - 18_scatter_credito_censo_agro.png")


if __name__ == "__main__":
    main()