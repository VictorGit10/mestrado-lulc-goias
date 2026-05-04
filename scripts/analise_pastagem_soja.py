"""
Pipeline #5 — Transição Pastagem → Soja em Goiás (1985–2024, nível municipal)
==============================================================================

Analisa como a área de pastagem e soja evoluiu nos 246 municípios de Goiás
ao longo de 40 anos. Produz métricas de conversão, rankings municipais e
gráficos prontos para a dissertação.

Métricas calculadas por município:
  - delta_pastagem_ha: variação de pastagem (2024 − 1985)
  - delta_soja_ha: variação de soja (2024 − 1985)
  - taxa_conversao: razão Δsoja / |Δpast| (quando pastagem reduziu)
  - intensidade_soja: Δsoja / pastagem_inicial (expansão relativa)
  - participacao_soja_2024: fração da soja no conjunto pastagem+soja

Períodos de análise:
  1985–1995 (expansão inicial)
  1995–2005 (consolidação)
  2005–2015 (intensificação)
  2015–2024 (recente)

Como rodar:
    python analise_pastagem_soja.py

Pré-requisitos:
    - data/processed/mapbiomas_munis_goias.csv  (Pipeline #4)
    - data/processed/sidra_pam1612_temporarias.csv  (Pipeline #3)

Saída:
    CSVs em data/processed/
    PNGs em outputs/ (07 a 11)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Garantir que print() funcione com Unicode no Windows (cp1252 → utf-8)
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

CLS_PASTAGEM = 15
CLS_SOJA     = 39
ANO_INICIO   = 1985
ANO_FIM      = 2024

COR_PASTAGEM = "#7a4f00"
COR_SOJA     = "#f5c242"
COR_CERRADO  = "#78a050"
COR_REFERENCIA = "#888888"

# Períodos para análise temporal
PERIODOS = [
    (1985, 1995, "1985-1995"),
    (1995, 2005, "1995-2005"),
    (2005, 2015, "2005-2015"),
    (2015, 2024, "2015-2024"),
]

ARQ_MAPBIOMAS = DIR_PROCESSED / "mapbiomas_munis_goias.csv"
ARQ_SIDRA     = DIR_PROCESSED / "sidra_pam1612_temporarias.csv"


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def _salvar(fig: plt.Figure, nome: str) -> None:
    """Salva figura em outputs/ com dpi=150 e fecha."""
    fig.savefig(DIR_OUTPUT / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] outputs/{nome}")


# ---------------------------------------------------------------------------
# 1. Carregamento de dados
# ---------------------------------------------------------------------------

def carregar_mapbiomas() -> pd.DataFrame:
    """
    Lê mapbiomas_munis_goias.csv e pivota para formato wide:
    uma linha por (cd_mun, ano), colunas pastagem_ha e soja_ha.

    Municípios sem registro de soja (2 casos) recebem area_ha = 0.
    """
    print(f"[...] Carregando {ARQ_MAPBIOMAS.name}...")
    df = pd.read_csv(ARQ_MAPBIOMAS, encoding="utf-8")
    print(f"  {len(df):,} linhas, {df['cd_mun'].nunique()} municípios")

    # Filtrar apenas pastagem e soja
    mask = df["class_id"].isin([CLS_PASTAGEM, CLS_SOJA])
    df_filt = df[mask][["cd_mun", "nm_mun", "ano", "class_id", "area_ha"]].copy()

    # Pivotar: uma coluna por classe
    pivot = df_filt.pivot_table(
        index=["cd_mun", "ano"],
        columns="class_id",
        values="area_ha",
        fill_value=0,
    ).reset_index()

    # Renomear colunas de class_id para nomes legíveis
    col_map = {}
    if CLS_PASTAGEM in pivot.columns:
        col_map[CLS_PASTAGEM] = "pastagem_ha"
    if CLS_SOJA in pivot.columns:
        col_map[CLS_SOJA] = "soja_ha"
    pivot = pivot.rename(columns=col_map)

    # Garantir que ambas as colunas existem (mesmo que soja seja 0 para todos)
    if "pastagem_ha" not in pivot.columns:
        pivot["pastagem_ha"] = 0.0
    if "soja_ha" not in pivot.columns:
        pivot["soja_ha"] = 0.0

    # Criar malha completa: todos os munis × todos os anos
    munis = df[["cd_mun"]].drop_duplicates()
    anos = pd.DataFrame({"ano": range(ANO_INICIO, ANO_FIM + 1)})
    mesh = munis.merge(anos, how="cross")

    # Merge com a malha completa para garantir que munis sem soja apareçam
    pivot = mesh.merge(pivot, on=["cd_mun", "ano"], how="left")
    pivot[["pastagem_ha", "soja_ha"]] = pivot[["pastagem_ha", "soja_ha"]].fillna(0.0)

    # Recuperar nomes dos municípios
    nomes = df[["cd_mun", "nm_mun"]].drop_duplicates()
    pivot = pivot.merge(nomes, on="cd_mun", how="left")

    # Ordenar
    pivot = pivot[["cd_mun", "nm_mun", "ano", "pastagem_ha", "soja_ha"]].sort_values(
        ["cd_mun", "ano"]
    ).reset_index(drop=True)

    n_munis = pivot["cd_mun"].nunique()
    n_anos = pivot["ano"].nunique()
    print(f"  Pivot: {len(pivot):,} linhas ({n_munis} munis × {n_anos} anos)")

    # Diagnóstico: quantos munis têm soja = 0 em todos os anos
    soja_zero = pivot.groupby("cd_mun")["soja_ha"].max()
    n_sem_soja = (soja_zero == 0).sum()
    if n_sem_soja > 0:
        munis_sem = pivot[pivot["cd_mun"].isin(soja_zero[soja_zero == 0].index)]["nm_mun"].unique()
        print(f"  {n_sem_soja} município(s) sem soja em todo o período: {', '.join(munis_sem)}")

    return pivot


def carregar_sidra_soja() -> pd.DataFrame:
    """
    Lê sidra_pam1612_temporarias.csv e extrai a área plantada de soja
    (categoria_id=2713, variavel_id=109) para validação cruzada.
    """
    print(f"[...] Carregando soja SIDRA de {ARQ_SIDRA.name}...")
    df = pd.read_csv(ARQ_SIDRA, encoding="utf-8")

    # Filtrar soja, área plantada
    soja = df[
        (df["categoria_id"] == 2713) & (df["variavel_id"] == 109)
    ][["cd_mun", "nm_mun", "ano", "valor"]].copy()
    soja = soja.rename(columns={"valor": "soja_sidra_ha"})

    # Remover NaN (anos sem dados)
    soja = soja.dropna(subset=["soja_sidra_ha"])

    n_munis = soja["cd_mun"].nunique()
    ano_min = soja["ano"].min()
    ano_max = soja["ano"].max()
    print(f"  {len(soja):,} registros, {n_munis} munis, anos {ano_min}–{ano_max}")
    return soja


# ---------------------------------------------------------------------------
# 2. Validação cruzada: MapBiomas vs SIDRA
# ---------------------------------------------------------------------------

def validar_soja_mapbiomas_vs_sidra(df_mapb: pd.DataFrame, df_sidra: pd.DataFrame) -> None:
    """
    Compara as áreas de soja do MapBiomas com as do SIDRA (PAM 1612).
    Apenas a partir de 2000, quando a cobertura SIDRA é razoável.
    Imprime diagnóstico e salva CSV de comparação.
    """
    print("\n[validação] Soja: MapBiomas vs SIDRA (PAM 1612, área plantada)")

    # Agregar soja MapBiomas por município e ano
    soja_mapb = df_mapb[["cd_mun", "nm_mun", "ano", "soja_ha"]].copy()

    # Merge
    comp = soja_mapb.merge(df_sidra[["cd_mun", "ano", "soja_sidra_ha"]],
                           on=["cd_mun", "ano"], how="inner")

    # Filtrar a partir de 2000
    comp = comp[comp["ano"] >= 2000]

    # Estatísticas por ano
    stats = []
    for ano, grp in comp.groupby("ano"):
        n = len(grp)
        if n < 50:
            continue
        corr = grp["soja_ha"].corr(grp["soja_sidra_ha"])
        ratio = (grp["soja_ha"] / grp["soja_sidra_ha"].replace(0, np.nan)).median()
        stats.append({
            "ano": ano,
            "n_munis": n,
            "corr_pearson": round(corr, 4),
            "razao_mediana": round(ratio, 4),
            "soja_mapb_Mha": round(grp["soja_ha"].sum() / 1e6, 3),
            "soja_sidra_Mha": round(grp["soja_sidra_ha"].sum() / 1e6, 3),
        })
    df_stats = pd.DataFrame(stats)
    print(df_stats.to_string(index=False))
    print(f"  Correlação média: {df_stats['corr_pearson'].mean():.3f}")

    # Salvar comparação detalhada
    comp.to_csv(DIR_PROCESSED / "validacao_soja_mapbiomas_sidra.csv", index=False)
    print("[OK] validacao_soja_mapbiomas_sidra.csv")


# ---------------------------------------------------------------------------
# 3. Cálculo de métricas
# ---------------------------------------------------------------------------

def calcular_painel_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o painel de métricas por município:
    deltas, taxa de conversão, intensidade de soja, participação.
    Uma linha por município (246 linhas).
    """
    print("\n[...] Calculando painel municipal de métricas...")

    ini = df[df["ano"] == ANO_INICIO].set_index("cd_mun")
    fim = df[df["ano"] == ANO_FIM].set_index("cd_mun")

    painel = pd.DataFrame({
        "cd_mun": ini.index,
        "nm_mun": ini["nm_mun"],
        "pastagem_1985_ha": ini["pastagem_ha"].values,
        "pastagem_2024_ha": fim["pastagem_ha"].values,
        "soja_1985_ha": ini["soja_ha"].values,
        "soja_2024_ha": fim["soja_ha"].values,
    })

    painel["delta_pastagem_ha"] = painel["pastagem_2024_ha"] - painel["pastagem_1985_ha"]
    painel["delta_soja_ha"] = painel["soja_2024_ha"] - painel["soja_1985_ha"]

    # Taxa de conversão: Δsoja / |Δpast| — só quando pastagem reduziu
    mask_reducao = painel["delta_pastagem_ha"] < 0
    painel["houve_reducao_pastagem"] = mask_reducao
    painel["taxa_conversao"] = np.nan
    painel.loc[mask_reducao, "taxa_conversao"] = (
        painel.loc[mask_reducao, "delta_soja_ha"]
        / painel.loc[mask_reducao, "delta_pastagem_ha"].abs()
    )

    # Intensidade de soja: Δsoja / pastagem_inicial — sempre válido (exceto past_0=0)
    painel["intensidade_soja"] = np.where(
        painel["pastagem_1985_ha"] > 0,
        painel["delta_soja_ha"] / painel["pastagem_1985_ha"],
        np.nan,
    )

    # Participação da soja no conjunto pastagem+soja em 2024
    denom = painel["soja_2024_ha"] + painel["pastagem_2024_ha"]
    painel["participacao_soja_2024"] = np.where(
        denom > 0,
        painel["soja_2024_ha"] / denom,
        np.nan,
    )

    # Ordenar por expansão absoluta de soja (descendente)
    painel = painel.sort_values("delta_soja_ha", ascending=False).reset_index(drop=True)

    # Diagnósticos
    n_red = mask_reducao.sum()
    n_exp = (~mask_reducao).sum()
    print(f"  {n_red} munis com redução de pastagem, {n_exp} com aumento")
    print(f"  Top 5 expansão de soja:")
    for _, row in painel.head(5).iterrows():
        print(f"    {row['nm_mun']:30s}  Δsoja = {row['delta_soja_ha']/1e3:+8.1f} kha")

    painel.to_csv(DIR_PROCESSED / "painel_pastagem_soja_municipal.csv", index=False)
    print("[OK] painel_pastagem_soja_municipal.csv")
    return painel


def calcular_deltas_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula deltas de pastagem e soja para cada período definido em PERIODOS.
    Retorna DataFrame com colunas: cd_mun, nm_mun, periodo_label,
    pastagem_inicial_ha, soja_inicial_ha, delta_pastagem_ha, delta_soja_ha,
    taxa_conversao.
    """
    print("\n[...] Calculando deltas por período...")

    registros = []
    for t0, t1, label in PERIODOS:
        df_ini = df[df["ano"] == t0].set_index("cd_mun")
        df_fim = df[df["ano"] == t1].set_index("cd_mun")

        # Usar apenas municípios presentes em ambos os anos
        comuns = df_ini.index.intersection(df_fim.index)

        for cd in comuns:
            past_ini = df_ini.loc[cd, "pastagem_ha"]
            past_fim = df_fim.loc[cd, "pastagem_ha"]
            soja_ini = df_ini.loc[cd, "soja_ha"]
            soja_fim = df_fim.loc[cd, "soja_ha"]
            d_past = past_fim - past_ini
            d_soja = soja_fim - soja_ini
            tc = d_soja / abs(d_past) if d_past < 0 else np.nan
            nm = df_ini.loc[cd, "nm_mun"]

            registros.append({
                "cd_mun": cd,
                "nm_mun": nm,
                "periodo": label,
                "ano_inicio": t0,
                "ano_fim": t1,
                "pastagem_inicial_ha": past_ini,
                "soja_inicial_ha": soja_ini,
                "delta_pastagem_ha": d_past,
                "delta_soja_ha": d_soja,
                "taxa_conversao": tc,
            })

    deltas = pd.DataFrame(registros)
    print(f"  {len(deltas):,} registros ({deltas['cd_mun'].nunique()} munis × {len(PERIODOS)} períodos)")

    deltas.to_csv(DIR_PROCESSED / "transicao_pastagem_soja_periodos.csv", index=False)
    print("[OK] transicao_pastagem_soja_periodos.csv")
    return deltas


def ranking_transicao(painel: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """
    Produz o ranking dos N municípios com maior expansão de soja.
    Inclui posições por diferentes métricas.
    """
    print(f"\n[...] Gerando ranking dos top {n} municípios...")

    rk = painel.copy()

    # Rankings
    rk["rank_delta_soja"] = rk["delta_soja_ha"].rank(ascending=False).astype(int)
    rk["rank_intensidade"] = rk["intensidade_soja"].rank(ascending=False, na_option="bottom").astype(int)
    rk["rank_taxa_conversao"] = rk["taxa_conversao"].rank(ascending=False, na_option="bottom").astype(int)

    # Ordenar por expansão absoluta de soja
    rk = rk.sort_values("delta_soja_ha", ascending=False).reset_index(drop=True)

    rk.to_csv(DIR_PROCESSED / "ranking_conversao_municipal.csv", index=False)
    print("[OK] ranking_conversao_municipal.csv")
    return rk


# ---------------------------------------------------------------------------
# 4. Gráficos
# ---------------------------------------------------------------------------

def grafico_evolucao_estado(df: pd.DataFrame) -> None:
    """Gráfico 07: evolução estadual de pastagem e soja (soma dos 246 munis)."""
    print("\n[...] Gerando gráfico 07: evolução estadual...")

    estado = df.groupby("ano").agg(
        pastagem_ha=("pastagem_ha", "sum"),
        soja_ha=("soja_ha", "sum"),
    ).reset_index()

    estado["total_ha"] = estado["pastagem_ha"] + estado["soja_ha"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(estado["ano"], estado["pastagem_ha"] / 1e6,
            color=COR_PASTAGEM, lw=2, marker="o", ms=3, label="Pastagem")
    ax.plot(estado["ano"], estado["soja_ha"] / 1e6,
            color=COR_SOJA, lw=2, marker="s", ms=3, label="Soja")
    ax.plot(estado["ano"], estado["total_ha"] / 1e6,
            color="black", lw=1.5, ls="--", label="Pastagem + Soja")

    ax.set_xlabel("Ano")
    ax.set_ylabel(u"Área (milhões de hectares)")
    ax.set_title(u"Pastagem e Soja em Goiás — MapBiomas Col. 10.1 (1985–2024)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2, axis="y")
    ax.set_xlim(ANO_INICIO, ANO_FIM)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    fig.tight_layout()
    _salvar(fig, "07_evolucao_pastagem_soja_estado.png")

    estado.to_csv(DIR_PROCESSED / "evolucao_pastagem_soja_estado.csv", index=False)
    print("[OK] evolucao_pastagem_soja_estado.csv")


def grafico_evolucao_top10(df: pd.DataFrame, ranking: pd.DataFrame) -> None:
    """Gráfico 08: small multiples dos 10 municípios com maior expansão de soja."""
    print("\n[...] Gerando gráfico 08: small multiples top 10...")

    top10_cds = ranking.head(10)["cd_mun"].values

    fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharex=True)
    axes_flat = axes.flat

    for i, (cd, ax) in enumerate(zip(top10_cds, axes_flat)):
        sub = df[df["cd_mun"] == cd].sort_values("ano")
        nm = sub["nm_mun"].iloc[0]

        ax.plot(sub["ano"], sub["pastagem_ha"] / 1e3,
                color=COR_PASTAGEM, lw=1.8, label="Pastagem", marker="o", ms=2)
        ax.plot(sub["ano"], sub["soja_ha"] / 1e3,
                color=COR_SOJA, lw=1.8, label="Soja", marker="s", ms=2)

        ax.set_title(nm, fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("1000 ha", fontsize=8)
        if i == 0:
            ax.legend(fontsize=7, loc="upper left")

    fig.suptitle(u"Expansão da Soja e Recuo da Pastagem — Top 10 Municípios",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _salvar(fig, "08_evolucao_pastagem_soja_top10.png")

    # Salvar CSV das séries dos top 10
    df_top10 = df[df["cd_mun"].isin(top10_cds)].copy()
    df_top10.to_csv(DIR_PROCESSED / "evolucao_pastagem_soja_top10.csv", index=False)
    print("[OK] evolucao_pastagem_soja_top10.csv")


def grafico_scatter_delta(painel: pd.DataFrame) -> None:
    """Gráfico 09: scatter Δpastagem × Δsoja para todos os 246 municípios."""
    print("\n[...] Gerando gráfico 09: scatter delta...")

    fig, ax = plt.subplots(figsize=(11, 9))

    # Escala logarítmica para intensidade (evita compressão dos valores baixos
    # e evita que Cristalina, com intensidade ~3,2, sature a barra de cores)
    intensidade = painel["intensidade_soja"].fillna(0)
    log_intensidade = np.log10(intensidade + 1)  # +1 para não dar -inf em zero

    scatter = ax.scatter(
        painel["delta_pastagem_ha"] / 1e3,
        painel["delta_soja_ha"] / 1e3,
        c=log_intensidade,
        cmap="YlOrBr",
        s=np.clip(painel["pastagem_1985_ha"] / 5e3, 8, 200),
        alpha=0.7,
        edgecolors="gray",
        linewidths=0.3,
    )
    # Barra de cores com ticks em escala original (não log)
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(u"Intensidade de soja (Δsoja / pastagem 1985)")
    # Ticks manuais na escala original para legibilidade
    tick_vals = [0, 0.2, 0.5, 1.0, 2.0, 3.5]
    cbar.set_ticks([np.log10(v + 1) for v in tick_vals])
    cbar.set_ticklabels([f"{v:.1f}" for v in tick_vals])

    # Limites dos eixos com folga para incluir anotações
    lim_x = max(abs(painel["delta_pastagem_ha"].min()), abs(painel["delta_pastagem_ha"].max())) / 1e3 * 1.10
    lim_y = painel["delta_soja_ha"].max() / 1e3 * 1.12  # folga extra no topo para rótulos
    ax.set_xlim(-lim_x, lim_x)
    ax.set_ylim(-20, lim_y)

    # Linha de referência: y = -x (todo pasto perdido virou soja)
    ax.plot([-lim_x, lim_x], [lim_x, -lim_x], "--", color=COR_REFERENCIA, lw=1,
            label=u"Linha 1:1 (Δpast = -Δsoja)")

    # Anotar os 5 maiores — offset variável para evitar sobreposição
    top5 = painel.head(5)
    offsets = [(25, 15), (25, -15), (-60, 15), (25, 15), (25, -15)]
    for (_, row), off in zip(top5.iterrows(), offsets):
        ax.annotate(
            f"{row['nm_mun']} ({row['intensidade_soja']:.1f})",
            xy=(row["delta_pastagem_ha"] / 1e3, row["delta_soja_ha"] / 1e3),
            xytext=off, textcoords="offset points",
            fontsize=7, color="black",
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )

    # Cruzamento nos eixos
    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)

    # Quadrantes com rótulos cautelosos
    ax.text(0.97, 0.97,
            u"Q2: Soja avança com recuo de pastagem\n(pastagem ↓, soja ↑)",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            color=COR_SOJA,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))
    ax.text(0.03, 0.97,
            u"Q1: Expansão simultânea\n(pastagem ↑, soja ↑)",
            transform=ax.transAxes, ha="left", va="top", fontsize=8,
            color="#5a7a3a",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax.set_xlabel(u"Variação de pastagem (1000 ha, 2024 − 1985)")
    ax.set_ylabel(u"Variação de soja (1000 ha, 2024 − 1985)")
    ax.set_title(u"Transição Pastagem e Soja nos Municípios de Goiás (1985–2024)")
    ax.legend(fontsize=9, loc="lower left")
    ax.grid(True, alpha=0.2)

    fig.tight_layout()
    _salvar(fig, "09_scatter_delta_pastagem_soja.png")


def grafico_barras_conversao(ranking: pd.DataFrame, n: int = 20) -> None:
    """Gráfico 10: barras horizontais dos top 20 municípios por expansão de soja."""
    print("\n[...] Gerando gráfico 10: barras top 20...")

    top = ranking.head(n).copy()
    top = top.sort_values("delta_soja_ha", ascending=True)  # ascending para barras horiz

    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # Painel superior: expansão absoluta de soja
    ax1 = axes[0]
    ax1.barh(top["nm_mun"], top["delta_soja_ha"] / 1e3,
             color=COR_SOJA, alpha=0.85, edgecolor="gray", linewidth=0.3)
    ax1.set_xlabel(u"Expansão de soja (1000 ha, 2024 − 1985)")
    ax1.set_title(f"Top {n} municípios — Expansão absoluta de soja")
    ax1.grid(True, alpha=0.2, axis="x")

    # Painel inferior: intensidade (Δsoja / pastagem_inicial)
    top2 = ranking.dropna(subset=["intensidade_soja"]).head(n).copy()
    top2 = top2.sort_values("intensidade_soja", ascending=True)

    ax2 = axes[1]
    ax2.barh(top2["nm_mun"], top2["intensidade_soja"] * 100,
             color=COR_SOJA, alpha=0.85, edgecolor="gray", linewidth=0.3)
    ax2.set_xlabel(u"Expansão relativa de soja (% da pastagem em 1985)")
    ax2.set_title(f"Top {n} municípios — Intensidade de expansão (Δsoja / pastagem₁₉₈₅)")
    ax2.grid(True, alpha=0.2, axis="x")

    fig.tight_layout(h_pad=3)
    _salvar(fig, "10_barras_top20_conversao.png")


def grafico_heatmap_periodo(deltas: pd.DataFrame, ranking: pd.DataFrame) -> None:
    """Gráfico 11: heatmap dos top 40 municípios × 4 períodos (expansão de soja)."""
    print("\n[...] Gerando gráfico 11: heatmap...")

    top40_cds = ranking.head(40)["cd_mun"].values

    # Preparar dados: delta_soja em 1000 ha por município × período
    heat = deltas[deltas["cd_mun"].isin(top40_cds)].pivot_table(
        index="nm_mun",
        columns="periodo",
        values="delta_soja_ha",
    ) / 1e3  # converter para 1000 ha

    # Ordenar linhas pelo total
    heat = heat.loc[heat.sum(axis=1).sort_values(ascending=False).index]

    # Ordem das colunas
    col_order = [label for _, _, label in PERIODOS]
    heat = heat.reindex(columns=col_order)

    fig, ax = plt.subplots(figsize=(10, 14))
    im = ax.imshow(heat.values, cmap="YlOrBr", aspect="auto")

    # Rótulos
    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(heat.columns, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=7)

    # Anotar células com valores
    for i in range(len(heat.index)):
        for j in range(len(heat.columns)):
            val = heat.values[i, j]
            if not np.isnan(val):
                # Texto escuro em células claras, claro em células escuras
                color = "white" if val > heat.values[~np.isnan(heat.values)].mean() else "black"
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        fontsize=6, color=color)

    fig.colorbar(im, ax=ax, label=u"Expansão de soja (1000 ha)", shrink=0.6)
    ax.set_title(u"Expansão da Soja por Município e Período — Top 40", fontsize=13, pad=15)
    fig.tight_layout()
    _salvar(fig, "11_heatmap_muni_periodo.png")

    # Salvar dados do heatmap
    heat_output = deltas[deltas["cd_mun"].isin(top40_cds)][
        ["cd_mun", "nm_mun", "periodo", "delta_soja_ha", "delta_pastagem_ha"]
    ].copy()
    heat_output["delta_soja_1000ha"] = heat_output["delta_soja_ha"] / 1e3
    heat_output.to_csv(DIR_PROCESSED / "heatmap_transicao_periodos.csv", index=False)
    print("[OK] heatmap_transicao_periodos.csv")


# ---------------------------------------------------------------------------
# 5. Validação batimental (soma municipal vs série UF)
# ---------------------------------------------------------------------------

def validacao_batimental_estado(df: pd.DataFrame) -> None:
    """Confere se a soma municipal de pastagem e soja bate com a série UF antiga."""
    print("\n[validação] Soma municipal vs série UF (pastagem):")

    arq_uf = DIR_PROCESSED / "pastagem_goias_anual.csv"
    if not arq_uf.exists():
        print(f"  (série UF não encontrada em {arq_uf.name} — pulando)")
        return

    pasto_uf = pd.read_csv(arq_uf).set_index("ano")["area_pastagem_ha"]
    pasto_muni = df.groupby("ano")["pastagem_ha"].sum()

    comp = pd.DataFrame({"municipal": pasto_muni, "uf": pasto_uf}).dropna()
    comp["delta_pct"] = (comp["municipal"] - comp["uf"]) / comp["uf"] * 100

    print(f"  Anos comparados: {len(comp)}")
    print(f"  Max |delta|: {comp['delta_pct'].abs().max():.4f}%")
    print(f"  Resultado: {'OK (idêntico)' if comp['delta_pct'].abs().max() < 0.01 else 'DIVERGE — investigar'}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Pipeline #5 -- Transicao Pastagem -> Soja (municipal, Goias 1985-2024)")
    print("=" * 70)

    # 1. Carregar dados
    df_mapb = carregar_mapbiomas()
    df_sidra = carregar_sidra_soja()

    # 2. Validação cruzada
    validar_soja_mapbiomas_vs_sidra(df_mapb, df_sidra)
    validacao_batimental_estado(df_mapb)

    # 3. Calcular métricas
    painel = calcular_painel_municipal(df_mapb)
    deltas = calcular_deltas_periodo(df_mapb)
    ranking = ranking_transicao(painel)

    # 4. Gráficos
    grafico_evolucao_estado(df_mapb)
    grafico_evolucao_top10(df_mapb, ranking)
    grafico_scatter_delta(painel)
    grafico_barras_conversao(ranking)
    grafico_heatmap_periodo(deltas, ranking)

    # Resumo final
    print("\n" + "=" * 70)
    print("Pipeline #5 concluído!")
    print("=" * 70)
    print("\nCSVs gerados em data/processed/:")
    print("  - painel_pastagem_soja_municipal.csv")
    print("  - transicao_pastagem_soja_periodos.csv")
    print("  - ranking_conversao_municipal.csv")
    print("  - validacao_soja_mapbiomas_sidra.csv")
    print("  - evolucao_pastagem_soja_estado.csv")
    print("  - evolucao_pastagem_soja_top10.csv")
    print("  - heatmap_transicao_periodos.csv")
    print("\nPNGs gerados em outputs/:")
    print("  - 07_evolucao_pastagem_soja_estado.png")
    print("  - 08_evolucao_pastagem_soja_top10.png")
    print("  - 09_scatter_delta_pastagem_soja.png")
    print("  - 10_barras_top20_conversao.png")
    print("  - 11_heatmap_muni_periodo.png")
    print("\nPróximo passo: instalar geopandas + geobr para mapas coropléticos.")


if __name__ == "__main__":
    main()