"""
Pipeline #14-análise — Fogo MapBiomas em Goiás (1985–2024)
============================================================

Análise descritiva e cruzamentos do fogo (área queimada) nos 246 municípios
de Goiás. Usa `data/processed/fogo_mapbiomas_goias.csv` (Pipeline #14, GEE
Collection 4) cruzado com o painel de transições (#12) quando disponível.

Saída:
    data/processed/painel_fogo_municipal.csv  (cross-section 1985-2024)
    outputs/analises/24_fogo_estado_serie.png
    outputs/analises/25_fogo_classe_proporcao.png
    outputs/analises/26_fogo_top10_municipal.png
    outputs/analises/27_scatter_fogo_transicoes.png    (se #12 disponível)
    outputs/analises/28_mapa_fogo_acumulado.png         (coroplético)
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUTPUT    = ROOT / "outputs" / "analises"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)

ARQ_FOGO = DIR_PROCESSED / "fogo_mapbiomas_goias.csv"

ANO_INI = 1985
ANO_FIM = 2024

# Cores por classe de queima (compatível com paletas dos #9, #10)
COR_CLASSE = {
    "veg_nat":     "#1B8A2F",   # Vegetação Natural
    "pastagem":    "#FFD700",
    "agricultura": "#FF69B4",
    "mosaico":     "#D2B48C",
    "outros":      "#A0A0A0",
    "agua":        "#4169E1",
    "urbano":      "#888888",
}

CLASSES_ORDEM = [
    ("veg_nat",     "Vegetação Natural", "area_queimada_veg_nat_ha"),
    ("pastagem",    "Pastagem",          "area_queimada_pastagem_ha"),
    ("agricultura", "Agricultura",       "area_queimada_agricultura_ha"),
    ("mosaico",     "Mosaico",           "area_queimada_mosaico_ha"),
    ("outros",      "Outros",            "area_queimada_outros_ha"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _salvar(fig: plt.Figure, nome: str) -> None:
    fig.savefig(DIR_OUTPUT / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] outputs/analises/{nome}")


# ---------------------------------------------------------------------------
# 1. Carregamento
# ---------------------------------------------------------------------------

def carregar_fogo() -> pd.DataFrame:
    print(f"[...] Carregando {ARQ_FOGO.name}...")
    df = pd.read_csv(ARQ_FOGO, encoding="utf-8")
    print(f"  {len(df):,} linhas, {df['cd_mun'].nunique()} munis, "
          f"{df['ano'].min()}-{df['ano'].max()}")
    return df


def calcular_painel_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """Acumulado 1985-2024 por município (1 linha por muni)."""
    print("\n[...] Calculando painel municipal acumulado...")
    cols_class = [c for _, _, c in CLASSES_ORDEM] + ["area_queimada_total_ha"]
    painel = (df.groupby(["cd_mun", "nm_mun"], as_index=False)[cols_class].sum())
    painel = painel.sort_values("area_queimada_total_ha", ascending=False).reset_index(drop=True)
    painel.to_csv(DIR_PROCESSED / "painel_fogo_municipal.csv", index=False)
    print(f"  Top 5 munis (queima acumulada 1985-2024):")
    for _, r in painel.head(5).iterrows():
        print(f"    {r['nm_mun']:30s}  total = {r['area_queimada_total_ha']/1e3:8.1f} kha")
    print("[OK] painel_fogo_municipal.csv")
    return painel


# ---------------------------------------------------------------------------
# 2. Gráficos
# ---------------------------------------------------------------------------

def grafico_24_serie_estado(df: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 24: série estadual...")
    estado = df.groupby("ano").agg({
        "area_queimada_total_ha":      "sum",
        "area_queimada_veg_nat_ha":    "sum",
        "area_queimada_pastagem_ha":   "sum",
        "area_queimada_agricultura_ha":"sum",
        "area_queimada_mosaico_ha":    "sum",
        "area_queimada_outros_ha":     "sum",
    }).reset_index()

    fig, ax = plt.subplots(figsize=(13, 6.5))
    bottom = np.zeros(len(estado))
    for key, label, col in CLASSES_ORDEM:
        vals = estado[col].values / 1e3
        ax.fill_between(estado["ano"], bottom, bottom + vals,
                        color=COR_CLASSE[key], label=label, alpha=0.85,
                        edgecolor="white", linewidth=0.3)
        bottom = bottom + vals

    ax.plot(estado["ano"], estado["area_queimada_total_ha"] / 1e3,
            color="black", lw=1.0, ls="--", label="Total")

    ax.set_xlabel("Ano")
    ax.set_ylabel("Área queimada (mil ha)")
    ax.set_title("Área queimada anual em Goiás por classe de cobertura — MapBiomas Fire C4 (1985–2024)")
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.2, axis="y")
    ax.set_xlim(ANO_INI, ANO_FIM)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.tight_layout()
    _salvar(fig, "24_fogo_estado_serie.png")


def grafico_25_proporcao_classe(df: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 25: proporção por classe...")
    estado = df.groupby("ano").agg({
        col: "sum" for _, _, col in CLASSES_ORDEM
    }).reset_index()
    total = estado[[c for _, _, c in CLASSES_ORDEM]].sum(axis=1)
    pct = estado.copy()
    for _, _, col in CLASSES_ORDEM:
        pct[col] = np.where(total > 0, estado[col] / total * 100, 0)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    bottom = np.zeros(len(pct))
    for key, label, col in CLASSES_ORDEM:
        vals = pct[col].values
        ax.fill_between(pct["ano"], bottom, bottom + vals,
                        color=COR_CLASSE[key], label=label, alpha=0.9,
                        edgecolor="white", linewidth=0.3)
        bottom = bottom + vals

    ax.set_xlabel("Ano")
    ax.set_ylabel("Composição da queima (%)")
    ax.set_title("Composição percentual da área queimada por classe — Goiás (1985–2024)")
    ax.legend(loc="upper right", fontsize=9, ncol=2)
    ax.set_xlim(ANO_INI, ANO_FIM)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.2, axis="y")
    fig.tight_layout()
    _salvar(fig, "25_fogo_classe_proporcao.png")


def grafico_26_top10_municipal(df: pd.DataFrame, painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 26: small multiples top 10...")
    top10 = painel.head(10)

    fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharex=True)
    for i, (cd, ax) in enumerate(zip(top10["cd_mun"].values, axes.flat)):
        sub = df[df["cd_mun"] == cd].sort_values("ano")
        nm = sub["nm_mun"].iloc[0]
        ax.fill_between(sub["ano"], 0, sub["area_queimada_total_ha"] / 1e3,
                        color="#B71C1C", alpha=0.4)
        ax.plot(sub["ano"], sub["area_queimada_total_ha"] / 1e3,
                color="#B71C1C", lw=1.2)
        ax.set_title(nm, fontsize=10)
        ax.grid(True, alpha=0.2)
        if i % 5 == 0:
            ax.set_ylabel("kha queimados")

    fig.suptitle("Top 10 municípios — área queimada anual 1985–2024 (mil ha)",
                 fontsize=12, y=1.00)
    fig.tight_layout()
    _salvar(fig, "26_fogo_top10_municipal.png")


def grafico_27_scatter_transicoes(painel_fogo: pd.DataFrame) -> None:
    """Cruzamento espacial fogo × conversão Vegetação Natural→outros (1985-2024)."""
    print("\n[...] Gerando gráfico 27: scatter fogo × transições...")

    arq_trans = DIR_PROCESSED / "transicoes_mapbiomas_goias.csv"
    if not arq_trans.exists():
        print(f"  [skip] {arq_trans.name} não encontrado.")
        return

    trans = pd.read_csv(arq_trans, encoding="utf-8")

    par = trans[(trans["ano_origem"] == 1985) & (trans["ano_destino"] == 2024)]
    if len(par) == 0:
        print("  [skip] par 1985→2024 ausente em transições.")
        return

    nome_veg = "Vegetação Natural"
    conv = par[(par["classe_orig_nome"] == nome_veg) &
               (par["classe_dest_nome"] != nome_veg)]
    if len(conv) == 0:
        # Fallback: usar comparação por id de classe (1 = Veg Natural no #12)
        conv = par[(par["classe_orig"] == 1) & (par["classe_dest"] != 1)]
    agg = conv.groupby("cd_mun", as_index=False)["area_ha"].sum().rename(
        columns={"area_ha": "area_convertida_ha"})

    merged = painel_fogo.merge(agg, on="cd_mun", how="inner")
    if len(merged) < 30:
        print(f"  [skip] poucos pontos ({len(merged)}).")
        return

    x = merged["area_convertida_ha"] / 1e3
    y = merged["area_queimada_total_ha"] / 1e3
    pearson = np.corrcoef(x, y)[0, 1]

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.scatter(x, y, s=40, alpha=0.6, color="#B71C1C",
               edgecolors="black", linewidths=0.4)

    top = merged.nlargest(5, "area_queimada_total_ha")
    for _, row in top.iterrows():
        ax.annotate(
            row["nm_mun"],
            xy=(row["area_convertida_ha"]/1e3, row["area_queimada_total_ha"]/1e3),
            xytext=(6, 6), textcoords="offset points", fontsize=9,
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        )

    ax.set_xlabel("Vegetação natural convertida 1985→2024 (mil ha)")
    ax.set_ylabel("Área queimada acumulada 1985–2024 (mil ha)")
    ax.set_title(f"Fogo vs. conversão de Vegetação Natural — 246 municípios | Pearson r = {pearson:.3f}",
                 fontsize=12)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    _salvar(fig, "27_scatter_fogo_transicoes.png")


def grafico_28_mapa_acumulado(painel: pd.DataFrame) -> None:
    print("\n[...] Gerando gráfico 28: coroplético acumulado...")
    try:
        import geobr
    except ImportError:
        print("  [skip] geobr não instalado.")
        return
    try:
        gdf = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4674)
    except Exception as exc:
        print(f"  [skip] falha geobr: {exc}")
        return

    gdf["cd_mun"] = gdf["code_muni"].astype("int64")
    m = gdf.merge(painel[["cd_mun", "area_queimada_total_ha"]],
                  on="cd_mun", how="left")
    m["area_queimada_total_ha"] = m["area_queimada_total_ha"].fillna(0)

    fig, ax = plt.subplots(figsize=(11, 10))
    vals = m["area_queimada_total_ha"].clip(lower=1)  # log: evitar 0
    norm = mcolors.LogNorm(vmin=vals.min(), vmax=vals.max())
    m.plot(column="area_queimada_total_ha", ax=ax, cmap="YlOrRd",
           norm=norm, edgecolor="white", linewidth=0.2, legend=True,
           legend_kwds={"label": "Área queimada acumulada 1985–2024 (ha, escala log)",
                        "orientation": "horizontal", "shrink": 0.6, "pad": 0.05})
    ax.set_axis_off()
    ax.set_title("Área queimada acumulada por município — Goiás 1985–2024",
                 fontsize=13)
    fig.tight_layout()
    _salvar(fig, "28_mapa_fogo_acumulado.png")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Análise do Fogo (#14) — Área queimada em Goiás 1985–2024")
    print("=" * 70)

    df = carregar_fogo()
    painel = calcular_painel_municipal(df)

    grafico_24_serie_estado(df)
    grafico_25_proporcao_classe(df)
    grafico_26_top10_municipal(df, painel)
    grafico_27_scatter_transicoes(painel)
    grafico_28_mapa_acumulado(painel)

    print("\n" + "=" * 70)
    print("Análise do fogo concluída!")
    print("=" * 70)


if __name__ == "__main__":
    main()
