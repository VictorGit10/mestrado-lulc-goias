"""Gera 3 PNGs para os blocos novos da seção Síntese de index.html.

Saída em Visualizacao/img/graficos/:
  - sintese_culturas_comparadas.png   (small multiples 7 culturas)
  - sintese_pecuaria_intensificacao.png (3 séries normalizadas)
  - sintese_socioeconomico.png        (PIB, SICOR, população, eixos independentes)

Lê data/processed/painel_unificado.parquet e agrega para a UF.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
OUT = ROOT / "Visualizacao" / "img" / "graficos"

COR_VEG = "#2d5a3d"
COR_PASTO = "#d4b65a"
COR_SOJA = "#8b3a1d"
COR_AGRIC = "#d96aa3"
COR_ACCENT = "#8b3a1d"
COR_AGUA = "#4a7ba6"
COR_MUTED = "#6b6b6b"
COR_FOGO = "#e31a1c"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#d8d6cf",
    "axes.labelcolor": "#1a1a1a",
    "axes.titlesize": 10,
    "xtick.color": "#6b6b6b",
    "ytick.color": "#6b6b6b",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 140,
    "savefig.bbox": "tight",
})


def carregar_uf() -> pd.DataFrame:
    df = pd.read_parquet(PAINEL)
    cols = [
        "ano",
        "lulc_pastagem_ha",
        "pec_bovinos_cab",
        "pec_bovinos_ua",
        "agri_soja_ton",
        "agri_milho_total_ton",
        "agri_cana_ton",
        "agri_algodao_ton",
        "agri_sorgo_ton",
        "agri_arroz_ton",
        "agri_feijao_ton",
        "pib_real_rs",
        "sicor_total_real_rs",
        "populacao",
    ]
    grp = df.groupby("ano", as_index=False)[cols[1:]].sum(min_count=1)
    grp["lotacao_ua_ha_pasto"] = grp["pec_bovinos_ua"] / grp["lulc_pastagem_ha"]
    return grp.sort_values("ano").reset_index(drop=True)


def grafico_culturas(grp: pd.DataFrame) -> None:
    culturas = [
        ("Soja",    "agri_soja_ton",          COR_SOJA),
        ("Milho",   "agri_milho_total_ton",   "#a87b3e"),
        ("Cana",    "agri_cana_ton",          "#7da651"),
        ("Algodão", "agri_algodao_ton",       "#d96aa3"),
        ("Sorgo",   "agri_sorgo_ton",         "#c97052"),
        ("Arroz",   "agri_arroz_ton",         "#c9a96e"),
        ("Feijão",  "agri_feijao_ton",        "#5c8a6f"),
    ]
    # eixo Y compartilhado para comparar ordens de grandeza
    y_max_mt = max(grp[col].max() for _, col, _ in culturas) / 1e6
    fig, axes = plt.subplots(1, 7, figsize=(13.5, 2.6), sharey=True)
    for ax, (nome, col, cor) in zip(axes, culturas):
        serie_mt = grp[col] / 1e6
        ax.fill_between(grp["ano"], 0, serie_mt, color=cor, alpha=0.85)
        ax.plot(grp["ano"], serie_mt, color=cor, linewidth=1)
        ax.set_title(nome, color="#1a1a1a", pad=4)
        ax.set_xlim(grp["ano"].min(), grp["ano"].max())
        ax.set_ylim(0, y_max_mt * 1.05)
        ax.set_xticks([1985, 2024])
        ax.tick_params(axis="x", which="major", pad=1)
    axes[0].set_ylabel("milhões de t", color="#6b6b6b")
    fig.suptitle(
        "Produção agrícola anual em Goiás — 1985–2024 (eixo Y compartilhado)",
        fontsize=10, color="#1a1a1a", y=1.02
    )
    fig.savefig(OUT / "sintese_culturas_comparadas.png")
    plt.close(fig)


def grafico_pecuaria(grp: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 3.2))

    def norm(s: pd.Series) -> pd.Series:
        mx = s.max(skipna=True)
        return s / mx if mx and mx > 0 else s

    pasto_n = norm(grp["lulc_pastagem_ha"])
    rebanho_n = norm(grp["pec_bovinos_cab"])
    lotacao_n = norm(grp["lotacao_ua_ha_pasto"])

    ax.plot(grp["ano"], pasto_n,   color=COR_PASTO,  linewidth=2.2, label="Área de pasto (Mha)")
    ax.plot(grp["ano"], rebanho_n, color=COR_ACCENT, linewidth=2.2, label="Rebanho bovino (M cab)")
    ax.plot(grp["ano"], lotacao_n, color=COR_VEG,    linewidth=2.2, label="Lotação (UA/ha)")

    # Sombrear a era de intensificação (2012-)
    ax.axvspan(2012, grp["ano"].max(), color="#5c8a6f", alpha=0.07, zorder=0)
    ax.text(2018, 0.04, "intensificação", color=COR_VEG, fontsize=8, fontstyle="italic")

    ax.set_xlim(grp["ano"].min(), grp["ano"].max())
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("normalizado (0–1 do próprio máximo)", color="#6b6b6b", fontsize=8)
    ax.set_title("Desacoplamento da pecuária goiana — pasto, rebanho e lotação", pad=10)
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    fig.savefig(OUT / "sintese_pecuaria_intensificacao.png")
    plt.close(fig)


def grafico_socio(grp: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(10, 3.2))

    # PIB real em bi
    pib_bi = grp["pib_real_rs"] / 1e9
    ax1.plot(grp["ano"], pib_bi, color=COR_AGUA, linewidth=2.2, label="PIB real (R$ bi)")
    ax1.set_ylabel("PIB / SICOR (R$ bi)", color=COR_AGUA, fontsize=8)
    ax1.tick_params(axis="y", labelcolor=COR_AGUA)

    # SICOR no mesmo eixo (mesma unidade)
    sicor_bi = grp["sicor_total_real_rs"] / 1e9
    ax1.plot(grp["ano"], sicor_bi, color=COR_AGRIC, linewidth=2.2, linestyle="--", label="SICOR (R$ bi)")

    # População em eixo secundário
    ax2 = ax1.twinx()
    pop_mi = grp["populacao"] / 1e6
    ax2.plot(grp["ano"], pop_mi, color=COR_MUTED, linewidth=1.8, label="População (Mi)")
    ax2.set_ylabel("População (Mi)", color=COR_MUTED, fontsize=8)
    ax2.tick_params(axis="y", labelcolor=COR_MUTED)
    ax2.spines["top"].set_visible(False)

    ax1.set_xlim(grp["ano"].min(), grp["ano"].max())
    ax1.set_title("Indicadores socioeconômicos (cobertura temporal parcial)", pad=10)

    # Cobertura: gaps explícitos via texto
    ax1.axvline(2002, color=COR_AGUA, alpha=0.15, linestyle=":")
    ax1.axvline(2013, color=COR_AGRIC, alpha=0.2, linestyle=":")
    ax1.text(2003, ax1.get_ylim()[1] * 0.92, "PIB →", color=COR_AGUA, fontsize=7)
    ax1.text(2014, ax1.get_ylim()[1] * 0.82, "SICOR →", color=COR_AGRIC, fontsize=7)

    # Legenda combinada
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8)

    fig.savefig(OUT / "sintese_socioeconomico.png")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    grp = carregar_uf()
    grafico_culturas(grp)
    print("OK sintese_culturas_comparadas.png")
    grafico_pecuaria(grp)
    print("OK sintese_pecuaria_intensificacao.png")
    grafico_socio(grp)
    print("OK sintese_socioeconomico.png")


if __name__ == "__main__":
    main()
