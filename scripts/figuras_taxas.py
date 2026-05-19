"""figuras_taxas.py — Figuras de taxas de variação LULC para Goiás
================================================================

Gera figuras estáticas (PNG) para a dissertação a partir dos dados
computados por calcular_taxas_lulc.py.

Figuras:
    1. Slope_5a_centr UF com faixa de confiança ±1.96·SE_NW
       e linhas verticais nos marcos políticos (3 classes)
    2. Slope_5a_trail por mesorregião (5 linhas sobrepostas, 3 classes)
    3. Delta (variação ano-a-ano) UF empilhado, com marcos
    4. Choropleth municipal do slope_5a_trail em períodos-chave

Saída: outputs/taxas/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "taxas"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# Config matplotlib
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "figure.facecolor": "white",
})

# Classes de interesse para as figuras principais
CLASSES_PLOT = ["vegetacao_natural", "pastagem", "agricultura"]
CLASSE_LABEL = {
    "vegetacao_natural": "Vegetação Natural",
    "pastagem": "Pastagem",
    "agricultura": "Agricultura",
}
CLASSE_COR = {
    "vegetacao_natural": "#1B8A2F",
    "pastagem": "#D4A017",
    "agricultura": "#FF69B4",
}

from config_periodos import ATOS as ATOS_DICT, MARCOS as MARCOS_DICT, CORES_ATO

# Marcos políticos (sem 1985 e 2024 que sao extremos da serie)
MARCOS = {ano: m["titulo"] for ano, m in MARCOS_DICT.items() if ano not in (1985, 2024)}

# ATOS (para fundo sombreado, com cores de utils.js)
ATOS = [
    {"inicio": ATOS_DICT[k]["inicio"], "fim": ATOS_DICT[k]["fim"],
     "cor": CORES_ATO[k], "alpha": 0.04,
     "rotulo": k}
    for k in ATOS_DICT
]


def add_atos_bg(ax):
    """Adiciona fundos sombreados dos ATOS ao eixo."""
    for ato in ATOS:
        ax.axvspan(ato["inicio"], ato["fim"], alpha=ato["alpha"],
                    color=ato["cor"], zorder=0)
        mid = (ato["inicio"] + ato["fim"]) / 2
        ax.text(mid, ax.get_ylim()[1] * 0.97, ato["rotulo"],
                ha="center", va="top", fontsize=7, color="gray", alpha=0.6)


def add_marcos(ax, ymin=None, ymax=None):
    """Adiciona linhas verticais dos marcos políticos."""
    for ano, titulo in MARCOS.items():
        ax.axvline(ano, color="gray", linestyle="--", linewidth=0.7, alpha=0.6, zorder=1)
        y_pos = (ymax if ymax else ax.get_ylim()[1]) * 0.95
        ax.text(ano + 0.3, y_pos, titulo, fontsize=6, color="gray",
                rotation=90, va="top", ha="left", alpha=0.7)


# ─────────────────────────── Figura 1: Slope UF ───────────────────────────

def fig_slope_uf(taxas: pd.DataFrame):
    """Slope_5a_centr UF com faixa de confiança e marcos."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("Taxa de variação LULC — Goiás (slope 5 anos, centrada)",
                 fontsize=14, fontweight="bold", y=0.98)

    for i, g in enumerate(CLASSES_PLOT):
        ax = axes[i]
        anos = taxas["ano"].values
        slope = taxas[f"{g}_slope_5a_centr"].values
        se = taxas[f"{g}_slope_se_nw"].values

        # Faixa de confiança (usando SE do trail como aproximação)
        se_plot = taxas[f"{g}_slope_se_nw"].values
        upper = slope + 1.96 * se_plot
        lower = slope - 1.96 * se_plot

        # Plot
        ax.fill_between(anos, lower, upper, alpha=0.15, color=CLASSE_COR[g])
        ax.plot(anos, slope, color=CLASSE_COR[g], linewidth=1.8, label=CLASSE_LABEL[g])
        ax.axhline(0, color="black", linewidth=0.5, zorder=2)

        add_atos_bg(ax)
        add_marcos(ax)

        ax.set_ylabel("Mha/ano", fontsize=9)
        ax.set_title(CLASSE_LABEL[g], fontsize=11, loc="left", pad=4)
        ax.set_xlim(1985, 2024)

        # Marcar cruzamento de zero
        slope_series = pd.Series(slope, index=anos)
        sign_changes = slope_series[slope_series.shift(1, fill_value=1) * slope_series < 0]
        if len(sign_changes) > 0:
            for yr_zero in sign_changes.index:
                ax.annotate(
                    f"→ 0 em {yr_zero}",
                    xy=(yr_zero, 0), xytext=(yr_zero + 2, slope_series.max() * 0.3),
                    fontsize=7, color="red", alpha=0.7,
                    arrowprops=dict(arrowstyle="->", color="red", alpha=0.5, lw=0.8),
                )

    axes[-1].set_xlabel("Ano")
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    path = DIR_OUT / "slope_uf_centrada.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {path.name}")


# ─────────────────────────── Figura 2: Slope por mesorregião ───────────────────────────

def fig_slope_mesorregioes(taxas_uf: pd.DataFrame, taxas_meso: pd.DataFrame):
    """Slope_5a_trail: UF + 5 mesorregiões sobrepostas."""
    meso_nomes = sorted(taxas_meso["nm_meso"].unique())
    meso_cores = plt.cm.Set2(np.linspace(0, 1, len(meso_nomes)))

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
    fig.suptitle("Taxa de variação por mesorregião — Goiás (slope 5a trailing)",
                 fontsize=13, fontweight="bold")

    for i, g in enumerate(CLASSES_PLOT):
        ax = axes[i]

        # UF (linha grossa)
        ax.plot(taxas_uf["ano"], taxas_uf[f"{g}_slope_5a_trail"],
                color="black", linewidth=2, label="Goiás (UF)", zorder=3)
        ax.axhline(0, color="gray", linewidth=0.5)

        # Mesorregiões
        for j, nm_meso in enumerate(meso_nomes):
            sub = taxas_meso[taxas_meso["nm_meso"] == nm_meso].sort_values("ano")
            ax.plot(sub["ano"], sub[f"{g}_slope_5a_trail"],
                    color=meso_cores[j], linewidth=1, alpha=0.7, label=nm_meso)

        add_marcos(ax)
        ax.set_title(CLASSE_LABEL[g], fontsize=11, loc="left")
        ax.set_ylabel("Mha/ano")
        ax.set_xlabel("Ano")
        ax.set_xlim(1989, 2024)

    axes[-1].legend(fontsize=6, loc="lower left", framealpha=0.8)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    path = DIR_OUT / "slope_mesorregioes.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {path.name}")


# ─────────────────────────── Figura 3: Delta UF ───────────────────────────

def fig_delta_uf(taxas: pd.DataFrame):
    """Barras de delta (variação ano-a-ano) UF para as 3 classes principais."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
    fig.suptitle("Variação ano-a-ano (delta) — Goiás",
                 fontsize=14, fontweight="bold", y=0.98)

    for i, g in enumerate(CLASSES_PLOT):
        ax = axes[i]
        anos = taxas["ano"].values[1:]  # sem 1985 (NaN)
        delta = taxas[f"{g}_delta_mha"].values[1:]

        colors = [CLASSE_COR[g] if d >= 0 else "#cc3333" for d in delta]
        ax.bar(anos, delta, color=colors, alpha=0.7, width=0.8)
        ax.axhline(0, color="black", linewidth=0.5)

        # Média móvel do delta (3 anos)
        delta_ma3 = pd.Series(delta).rolling(3, center=True).mean().values
        ax.plot(anos, delta_ma3, color="black", linewidth=1.2, alpha=0.6, label="Média 3a")

        add_atos_bg(ax)
        add_marcos(ax)

        ax.set_ylabel("Mha/ano")
        ax.set_title(CLASSE_LABEL[g], fontsize=11, loc="left", pad=4)

    axes[-1].set_xlabel("Ano")
    axes[-1].set_xlim(1986, 2024)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    path = DIR_OUT / "delta_uf.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {path.name}")


# ─────────────────────────── Figura 4: Mapas municipais ───────────────────────────

def fig_mapas_slope_municipal(taxas_muni: pd.DataFrame):
    """Choropleth do slope_5a_trail para períodos-chave e 3 classes.

    Períodos: slope médio por ATOS (centrado no ano médio do ATOS).
    """
    try:
        import geobr
    except ImportError:
        print("AVISO: geobr não instalado, pulando mapas municipais.")
        return

    # Baixar geometrias
    print("  Baixando geometrias municipais...")
    munis_gdf = geobr.read_municipality(year=2020)
    go_munis = munis_gdf[munis_gdf["code_state"].astype(str).str.startswith("52")].copy()
    go_munis["cd_mun"] = go_munis["code_muni"].astype(int)
    go_munis = go_munis[["cd_mun", "geometry"]].to_crs(5880)

    # Períodos-chave: usar o slope_5a_trail do ano central de cada ATOS
    periodos = {
        "I. Herança\n(1989)": 1989,
        "II. Soja sudoeste\n(1998)": 1998,
        "III. Boom\n(2007)": 2007,
        "IV. Cód. Florestal\n(2014)": 2014,
        "V. Reorganização\n(2021)": 2021,
    }

    for g in CLASSES_PLOT:
        fig, axes = plt.subplots(1, len(periodos), figsize=(20, 4))
        fig.suptitle(f"Slope municipal — {CLASSE_LABEL[g]} (Mha/ano)",
                     fontsize=13, fontweight="bold")

        # Determinar range comum
        col_slope = f"{g}_slope_5a_trail"
        vals = taxas_muni[taxas_muni[col_slope].notna()][col_slope]
        vmin, vmax = vals.quantile(0.05), vals.quantile(0.95)
        # Simétrico em torno de zero
        abs_max = max(abs(vmin), abs(vmax))
        vmin, vmax = -abs_max, abs_max

        for j, (titulo, ano) in enumerate(periodos.items()):
            ax = axes[j]
            sub = taxas_muni[taxas_muni["ano"] == ano][["cd_mun", col_slope]].copy()
            merged = go_munis.merge(sub, on="cd_mun", how="left")

            merged.plot(column=col_slope, ax=ax, legend=(j == len(periodos) - 1),
                       cmap="RdBu", vmin=vmin, vmax=vmax,
                       missing_kwds={"color": "lightgray", "label": "Sem dados"},
                       linewidth=0.1, edgecolor="white")

            ax.set_title(titulo, fontsize=8)
            ax.set_axis_off()

        fig.tight_layout(rect=[0, 0, 1, 0.92])
        path = DIR_OUT / f"mapa_slope_{g}.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(f"OK: {path.name}")


# ─────────────────────────── Figura 5: Aceleração ───────────────────────────

def fig_aceleracao_uf(taxas: pd.DataFrame):
    """Aceleração (mudança do slope) UF — pontos de inflexão candidatos."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("Aceleração da mudança LULC — Goiás (2a derivada do slope)",
                 fontsize=14, fontweight="bold", y=0.98)

    for i, g in enumerate(CLASSES_PLOT):
        ax = axes[i]
        anos = taxas["ano"].values
        accel = taxas[f"{g}_aceleracao"].values

        # Plotar série completa
        ax.bar(anos, accel, color=CLASSE_COR[g], alpha=0.5, width=0.8, label="Aceleração")
        ax.axhline(0, color="black", linewidth=0.5)

        # Destacar pontos de inflexão (|acel| > 2·σ)
        accel_series = pd.Series(accel).dropna()
        if len(accel_series) > 2:
            sigma = accel_series.std()
            anos_validos = taxas["ano"].values[~np.isnan(accel)]
            high_accel = np.abs(accel_series) > 2 * sigma
            if high_accel.any():
                ax.scatter(anos_validos[high_accel.values], accel_series[high_accel.values],
                          color="red", s=30, zorder=5, label=f"|acel| > 2σ ({sigma:.4f})")

        add_atos_bg(ax)
        add_marcos(ax)

        ax.set_ylabel("Mha/ano²")
        ax.set_title(CLASSE_LABEL[g], fontsize=11, loc="left", pad=4)
        ax.legend(fontsize=7, loc="upper right")

    axes[-1].set_xlabel("Ano")
    axes[-1].set_xlim(1989, 2024)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    path = DIR_OUT / "aceleracao_uf.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {path.name}")


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    print("Carregando dados...")
    taxas_uf = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")
    taxas_muni = pd.read_csv(DIR_DATA / "taxas_lulc_municipal.csv")

    if (DIR_DATA / "taxas_lulc_mesorregioes.csv").exists():
        taxas_meso = pd.read_csv(DIR_DATA / "taxas_lulc_mesorregioes.csv")
    else:
        taxas_meso = None

    print("\n[1/5] Figura: Slope UF (centrada) com confiança...")
    fig_slope_uf(taxas_uf)

    print("\n[2/5] Figura: Slope por mesorregião...")
    if taxas_meso is not None:
        fig_slope_mesorregioes(taxas_uf, taxas_meso)
    else:
        print("  Pulando (sem dados de mesorregião)")

    print("\n[3/5] Figura: Delta UF...")
    fig_delta_uf(taxas_uf)

    print("\n[4/5] Figura: Mapas municipais de slope...")
    fig_mapas_slope_municipal(taxas_muni)

    print("\n[5/5] Figura: Aceleração UF...")
    fig_aceleracao_uf(taxas_uf)

    print(f"\nFeito — figuras em {DIR_OUT}")


if __name__ == "__main__":
    main()