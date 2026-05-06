"""
Pipeline #15-análise — Milho 1ª e 2ª safra em Goiás (2003–2024)
================================================================

Análise descritiva da safrinha (milho 2ª safra) versus 1ª safra nos 246
municípios de Goiás. Foco em intensificação produtiva: a 2ª safra ocupa
a mesma área da 1ª (ou da soja precoce) num segundo ciclo no mesmo ano,
e é o vetor central da diversificação agrícola no centro-oeste pós-2010.

Insumo:
    data/processed/sidra_pam839_milho_safras.csv  (Pipeline #15, SIDRA 839)

Métricas calculadas por município:
    area_milho1_ha (área plantada 1ª safra)
    area_milho2_ha (área plantada 2ª safra)
    area_milho_total_ha = area_milho1 + area_milho2
    prod_milho1_ton, prod_milho2_ton
    razao_milho2_milho1 = area_milho2 / area_milho1 (NaN onde milho1 == 0)
    delta_milho2_ha = milho2_2024 - milho2_2003

Períodos:
    2003–2008 (boom inicial), 2009–2013 (consolidação),
    2014–2018 (intensificação), 2019–2024 (recente).

Saída:
    data/processed/painel_safrinha_municipal.csv
    data/processed/evolucao_safrinha_estado.csv
    outputs/analises/19_evolucao_safras_estado.png
    outputs/analises/20_top10_safrinha_municipal.png
    outputs/analises/21_scatter_safras_municipal.png
    outputs/analises/22_barras_top20_intensificacao.png
    outputs/analises/23_heatmap_safrinha_periodos.png
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
ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUTPUT    = ROOT / "outputs" / "analises"
for d in (DIR_PROCESSED, DIR_OUTPUT):
    d.mkdir(parents=True, exist_ok=True)

ARQ_SAFRINHA = DIR_PROCESSED / "sidra_pam839_milho_safras.csv"

VAR_AREA_PLANTADA = 109
VAR_QTD_PRODUZIDA = 214
CAT_MILHO_1A      = 114253
CAT_MILHO_2A      = 114254

ANO_INI = 2003
ANO_FIM = 2024

PERIODOS = [
    (2003, 2008, "2003-2008"),
    (2009, 2013, "2009-2013"),
    (2014, 2018, "2014-2018"),
    (2019, 2024, "2019-2024"),
]

COR_MILHO1 = "#2E7D32"   # verde escuro (safra principal, ciclo de verão)
COR_MILHO2 = "#F57C00"   # laranja (safrinha, ciclo de outono-inverno)
COR_TOTAL  = "#212121"   # quase preto


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _salvar(fig: plt.Figure, nome: str) -> None:
    fig.savefig(DIR_OUTPUT / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] outputs/analises/{nome}")


def _anotar_top(ax, df, x_col, y_col, label_col, n=5, fontsize=8):
    top = df.nlargest(n, y_col) if y_col in df.columns else df.head(n)
    for _, row in top.iterrows():
        ax.annotate(
            str(row[label_col]),
            xy=(row[x_col], row[y_col]),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=fontsize,
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )


# ---------------------------------------------------------------------------
# 1. Carregamento e pivot
# ---------------------------------------------------------------------------

def carregar_safrinha() -> pd.DataFrame:
    """
    Lê SIDRA 839 e pivota para wide: uma linha por (cd_mun, ano), colunas
    `area_milho1_ha`, `area_milho2_ha`, `prod_milho1_ton`, `prod_milho2_ton`.
    NaNs (municípios sem safra reportada) tratados como 0.
    """
    print(f"[...] Carregando {ARQ_SAFRINHA.name}...")
    df = pd.read_csv(ARQ_SAFRINHA, encoding="utf-8")
    print(f"  {len(df):,} linhas, {df['cd_mun'].nunique()} munis, "
          f"{df['ano'].min()}-{df['ano'].max()}")

    blocos = []
    for cat_id, sufixo in [(CAT_MILHO_1A, "milho1"), (CAT_MILHO_2A, "milho2")]:
        for var_id, prefixo, unidade in [
            (VAR_AREA_PLANTADA, "area",  "ha"),
            (VAR_QTD_PRODUZIDA, "prod",  "ton"),
        ]:
            col = f"{prefixo}_{sufixo}_{unidade}"
            sub = (
                df[(df["categoria_id"] == cat_id) & (df["variavel_id"] == var_id)]
                [["cd_mun", "ano", "valor"]]
                .rename(columns={"valor": col})
            )
            blocos.append(sub)

    out = blocos[0]
    for b in blocos[1:]:
        out = out.merge(b, on=["cd_mun", "ano"], how="outer")

    nomes = df[["cd_mun", "nm_mun"]].drop_duplicates()
    out = out.merge(nomes, on="cd_mun", how="left")

    for c in ["area_milho1_ha", "area_milho2_ha", "prod_milho1_ton", "prod_milho2_ton"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    out["area_milho_total_ha"] = out["area_milho1_ha"] + out["area_milho2_ha"]
    out = (out[["cd_mun", "nm_mun", "ano",
                "area_milho1_ha", "area_milho2_ha", "area_milho_total_ha",
                "prod_milho1_ton", "prod_milho2_ton"]]
           .sort_values(["cd_mun", "ano"]).reset_index(drop=True))

    print(f"  pivot: {len(out):,} linhas (esperado 246*22=5.412)")
    return out


# ---------------------------------------------------------------------------
# 2. Métricas
# ---------------------------------------------------------------------------

def calcular_painel_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Painel cross-section municipal (246 linhas) com métricas de intensificação.
    """
    print("\n[...] Calculando painel municipal de safrinha...")

    ini = df[df["ano"] == ANO_INI].set_index("cd_mun")
    fim = df[df["ano"] == ANO_FIM].set_index("cd_mun")

    painel = pd.DataFrame({
        "cd_mun": ini.index,
        "nm_mun": ini["nm_mun"],
        "milho1_2003_ha": ini["area_milho1_ha"].values,
        "milho1_2024_ha": fim["area_milho1_ha"].values,
        "milho2_2003_ha": ini["area_milho2_ha"].values,
        "milho2_2024_ha": fim["area_milho2_ha"].values,
        "prod_milho2_2024_ton": fim["prod_milho2_ton"].values,
    })
    painel["delta_milho1_ha"] = painel["milho1_2024_ha"] - painel["milho1_2003_ha"]
    painel["delta_milho2_ha"] = painel["milho2_2024_ha"] - painel["milho2_2003_ha"]
    painel["razao_milho2_milho1_2024"] = np.where(
        painel["milho1_2024_ha"] > 0,
        painel["milho2_2024_ha"] / painel["milho1_2024_ha"],
        np.nan,
    )

    painel = painel.sort_values("delta_milho2_ha", ascending=False).reset_index(drop=True)

    n_com_safrinha_2024 = (painel["milho2_2024_ha"] > 0).sum()
    n_com_safrinha_2003 = (painel["milho2_2003_ha"] > 0).sum()
    print(f"  Munis com 2ª safra reportada: 2003={n_com_safrinha_2003}, 2024={n_com_safrinha_2024}")
    print(f"  Top 5 expansão Δmilho2 (2003→2024):")
    for _, r in painel.head(5).iterrows():
        print(f"    {r['nm_mun']:30s}  Δ = {r['delta_milho2_ha']/1e3:+8.1f} kha")

    painel.to_csv(DIR_PROCESSED / "painel_safrinha_municipal.csv", index=False)
    print("[OK] painel_safrinha_municipal.csv")
    return painel


# ---------------------------------------------------------------------------
# 3. Gráficos
# ---------------------------------------------------------------------------

def grafico_19_evolucao_estado(df: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 19: evolução estadual...")
    estado = df.groupby("ano").agg(
        milho1_ha=("area_milho1_ha", "sum"),
        milho2_ha=("area_milho2_ha", "sum"),
        total_ha=("area_milho_total_ha", "sum"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(estado["ano"], estado["milho1_ha"] / 1e6,
            color=COR_MILHO1, lw=2, marker="o", ms=3, label="Milho 1ª safra")
    ax.plot(estado["ano"], estado["milho2_ha"] / 1e6,
            color=COR_MILHO2, lw=2, marker="s", ms=3, label="Milho 2ª safra (safrinha)")
    ax.plot(estado["ano"], estado["total_ha"] / 1e6,
            color=COR_TOTAL, lw=1.5, ls="--", label="Total milho")

    ax.set_xlabel("Ano")
    ax.set_ylabel("Área plantada (milhões de hectares)")
    ax.set_title("Milho 1ª e 2ª safra em Goiás — SIDRA 839 (2003–2024)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2, axis="y")
    ax.set_xlim(ANO_INI, ANO_FIM)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    fig.tight_layout()
    _salvar(fig, "19_evolucao_safras_estado.png")

    estado.to_csv(DIR_PROCESSED / "evolucao_safrinha_estado.csv", index=False)
    print("[OK] evolucao_safrinha_estado.csv")


def grafico_20_top10_municipal(df: pd.DataFrame, painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 20: small multiples top 10...")
    top10 = painel.head(10)

    fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharex=True)
    for i, (cd, ax) in enumerate(zip(top10["cd_mun"].values, axes.flat)):
        sub = df[df["cd_mun"] == cd].sort_values("ano")
        nm = sub["nm_mun"].iloc[0]
        ax.plot(sub["ano"], sub["area_milho1_ha"] / 1e3,
                color=COR_MILHO1, lw=1.5, label="1ª safra")
        ax.plot(sub["ano"], sub["area_milho2_ha"] / 1e3,
                color=COR_MILHO2, lw=1.5, label="2ª safra")
        ax.fill_between(sub["ano"], 0, sub["area_milho2_ha"] / 1e3,
                        color=COR_MILHO2, alpha=0.15)
        ax.set_title(nm, fontsize=10)
        ax.grid(True, alpha=0.2)
        if i == 0:
            ax.legend(loc="upper left", fontsize=8)
        if i % 5 == 0:
            ax.set_ylabel("kha")

    fig.suptitle("Top 10 municípios — expansão da safrinha 2003→2024 (área plantada, mil ha)",
                 fontsize=12, y=1.00)
    fig.tight_layout()
    _salvar(fig, "20_top10_safrinha_municipal.png")


def grafico_21_scatter_safras(painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 21: scatter Δmilho1 × Δmilho2...")

    df = painel.copy()
    df = df[(df["delta_milho1_ha"].abs() < 1e6) & (df["delta_milho2_ha"].abs() < 1e6)]

    sizes = (df["prod_milho2_2024_ton"] / 1000).clip(lower=5, upper=400)
    cor = df["razao_milho2_milho1_2024"].clip(lower=0.1, upper=200)

    fig, ax = plt.subplots(figsize=(11, 8))
    sc = ax.scatter(
        df["delta_milho1_ha"] / 1e3,
        df["delta_milho2_ha"] / 1e3,
        s=sizes, c=cor, cmap="YlOrBr", alpha=0.7,
        edgecolors="gray", linewidths=0.4,
        norm=plt.matplotlib.colors.LogNorm(),
    )

    lim = max(abs(df["delta_milho1_ha"]).max(),
              abs(df["delta_milho2_ha"]).max()) / 1e3 * 1.05
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.plot([-lim, lim], [-lim, lim], color="gray", ls="--", lw=0.7, label="Linha 1:1")

    ax.set_xlabel("Δ milho 1ª safra 2003→2024 (mil ha)")
    ax.set_ylabel("Δ milho 2ª safra (safrinha) 2003→2024 (mil ha)")
    ax.set_title("Expansão da safrinha vs. 1ª safra — 246 municípios de Goiás")
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Razão milho2/milho1 em 2024 (log)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2)

    _anotar_top(ax,
                df.assign(x_kha=df["delta_milho1_ha"]/1e3,
                          y_kha=df["delta_milho2_ha"]/1e3),
                "x_kha", "y_kha", "nm_mun", n=5)

    fig.tight_layout()
    _salvar(fig, "21_scatter_safras_municipal.png")


def grafico_22_barras_top20(painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 22: barras top 20...")
    top_abs = painel.head(20).copy()
    top_int = (painel.dropna(subset=["razao_milho2_milho1_2024"])
                     .nlargest(20, "razao_milho2_milho1_2024").copy())

    fig, axes = plt.subplots(1, 2, figsize=(14, 8))

    ax = axes[0]
    ax.barh(top_abs["nm_mun"][::-1], top_abs["delta_milho2_ha"][::-1] / 1e3,
            color=COR_MILHO2, edgecolor="black", linewidth=0.3)
    ax.set_xlabel("Δ milho 2ª safra 2003→2024 (mil ha)")
    ax.set_title("Expansão absoluta da safrinha")
    ax.grid(True, alpha=0.2, axis="x")

    ax = axes[1]
    ax.barh(top_int["nm_mun"][::-1], top_int["razao_milho2_milho1_2024"][::-1],
            color=COR_MILHO2, edgecolor="black", linewidth=0.3)
    ax.set_xlabel("Razão milho2/milho1 em 2024")
    ax.set_title("Intensificação relativa (safrinha por unidade de safra principal)")
    ax.grid(True, alpha=0.2, axis="x")

    fig.suptitle("Top 20 municípios — safrinha em Goiás", fontsize=12, y=1.00)
    fig.tight_layout()
    _salvar(fig, "22_barras_top20_intensificacao.png")


def grafico_23_heatmap_periodos(df: pd.DataFrame, painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 23: heatmap períodos...")
    top40_cds = painel.head(40)["cd_mun"].values
    sub = df[df["cd_mun"].isin(top40_cds)].copy()

    sub["periodo"] = pd.NA
    for t0, t1, label in PERIODOS:
        mask = (sub["ano"] >= t0) & (sub["ano"] <= t1)
        sub.loc[mask, "periodo"] = label

    media = (sub.groupby(["cd_mun", "nm_mun", "periodo"])["area_milho2_ha"]
                .mean().reset_index())
    pivot = media.pivot_table(index="nm_mun", columns="periodo",
                              values="area_milho2_ha", aggfunc="first")

    ordem = (painel.head(40).set_index("nm_mun").index)
    pivot = pivot.reindex(ordem)
    pivot = pivot[[p for _, _, p in PERIODOS]]

    fig, ax = plt.subplots(figsize=(10, 12))
    arr = pivot.values / 1e3
    im = ax.imshow(arr, cmap="YlOrBr", aspect="auto")

    ax.set_xticks(range(arr.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=0)
    ax.set_yticks(range(arr.shape[0]))
    ax.set_yticklabels(pivot.index, fontsize=9)

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            if not np.isnan(v):
                color = "white" if v > arr.max() * 0.55 else "black"
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        color=color, fontsize=7)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Área média da 2ª safra no período (mil ha)")
    ax.set_title("Top 40 municípios — área da safrinha por período (média anual, mil ha)",
                 fontsize=11)
    fig.tight_layout()
    _salvar(fig, "23_heatmap_safrinha_periodos.png")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Análise da Safrinha (#15) — Milho 1ª e 2ª safra em Goiás 2003-2024")
    print("=" * 70)

    df = carregar_safrinha()
    painel = calcular_painel_municipal(df)

    grafico_19_evolucao_estado(df)
    grafico_20_top10_municipal(df, painel)
    grafico_21_scatter_safras(painel)
    grafico_22_barras_top20(painel)
    grafico_23_heatmap_periodos(df, painel)

    print("\n" + "=" * 70)
    print("Análise da safrinha concluída!")
    print("=" * 70)
    print("\nCSVs gerados em data/processed/:")
    print("  - painel_safrinha_municipal.csv")
    print("  - evolucao_safrinha_estado.csv")
    print("\nPNGs gerados em outputs/analises/:")
    for n in ("19_evolucao_safras_estado.png",
              "20_top10_safrinha_municipal.png",
              "21_scatter_safras_municipal.png",
              "22_barras_top20_intensificacao.png",
              "23_heatmap_safrinha_periodos.png"):
        print(f"  - {n}")


if __name__ == "__main__":
    main()
