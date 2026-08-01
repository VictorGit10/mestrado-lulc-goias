"""
Gera figura decomposto: extensão vs. intensificação em Goiás.

Painéis:
  A) Soja — scatter conectado: área plantada (SIDRA) × produção (SIDRA)
  B) Bovinocultura — scatter conectado: pastagem (MapBiomas LULC) × rebanho (SIDRA)
  C) Soja — decomposição indexada (área, produção, produtividade)
  D) Bovinocultura — decomposição indexada (pastagem, rebanho, lotação)

Uso:
  cd Visualizacao
  python scripts/gerar_figura_produtividade.py

Saida:
  img/graficos/produtividade_extensao_intensificacao.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "Visualizacao" / "img" / "graficos" / "produtividade_extensao_intensificacao.png"
OUT.parent.mkdir(parents=True, exist_ok=True)


def load_state_series() -> pd.DataFrame:
    df = pd.read_parquet(REPO_ROOT / "data" / "processed" / "painel_amc_goias.parquet")
    est = (
        df.groupby("ano")
        .agg(
            {
                "agri_soja_ha_plantada": "sum",
                "agri_soja_ton": "sum",
                "lulc_soja_ha": "sum",
                "lulc_pastagem_ha": "sum",
                "pec_bovinos_cab": "sum",
            }
        )
        .reset_index()
    )
    # Lotação = razão de agregados (não média de AMCs)
    est["lotacao_bov_ha"] = est["pec_bovinos_cab"] / est["lulc_pastagem_ha"]
    est["produtividade_soja_ton_ha"] = est["agri_soja_ton"] / est["agri_soja_ha_plantada"]
    return est


def index_to(df: pd.DataFrame, col: str, ano_base: int) -> pd.Series:
    base = df.loc[df["ano"] == ano_base, col].iloc[0]
    return (df[col] / base) * 100.0


def make_figure(df: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), constrained_layout=True)
    fig.patch.set_facecolor("white")

    # ------------------------------------------------------------------
    # Paleta de anos comum
    # ------------------------------------------------------------------
    cmap = plt.cm.viridis_r  # anos recentes em amarelo, antigos em roxo

    # ------------------------------------------------------------------
    # Painel A: scatter conectado soja
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    soy = df.dropna(subset=["agri_soja_ha_plantada", "agri_soja_ton"]).copy()
    x = soy["agri_soja_ha_plantada"] / 1e6
    y = soy["agri_soja_ton"] / 1e6
    anos = soy["ano"].values

    # linha conectada com cor gradiente
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    from matplotlib.collections import LineCollection

    norm = plt.Normalize(anos.min(), anos.max())
    lc = LineCollection(segments, cmap=cmap, norm=norm, alpha=0.7, linewidth=2)
    lc.set_array(anos)
    ax.add_collection(lc)

    # pontos principais
    sc = ax.scatter(x, y, c=anos, cmap=cmap, norm=norm, s=40, zorder=5, edgecolor="k", linewidth=0.3)

    # rótulo início/fim
    ax.annotate(
        f"{anos[0]:.0f}",
        (x.iloc[0], y.iloc[0]),
        textcoords="offset points",
        xytext=(-12, -8),
        fontsize=9,
        fontweight="bold",
        color="#440154",
    )
    ax.annotate(
        f"{anos[-1]:.0f}",
        (x.iloc[-1], y.iloc[-1]),
        textcoords="offset points",
        xytext=(8, 4),
        fontsize=9,
        fontweight="bold",
        color="#FDE725",
    )

    # linha de referência: produtividade constante = produtividade do último ano
    prod_final = (soy["agri_soja_ton"].iloc[-1] / soy["agri_soja_ha_plantada"].iloc[-1])
    x_line = np.linspace(0, x.max() * 1.05, 100)
    ax.plot(x_line, x_line * prod_final, "--", color="gray", lw=1.5, label=f"produtividade {anos[-1]:.0f} = {prod_final:.1f} t/ha")

    ax.set_xlabel("Área plantada (milhões de ha)", fontsize=10)
    ax.set_ylabel("Produção (milhões de ton)", fontsize=10)
    ax.set_title("A) Soja: quase tudo foi extensão", fontsize=12, fontweight="bold", loc="left")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(0, x.max() * 1.08)
    ax.set_ylim(0, y.max() * 1.08)

    # ------------------------------------------------------------------
    # Painel B: scatter conectado bovino
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    bov = df.dropna(subset=["lulc_pastagem_ha", "pec_bovinos_cab"]).copy()
    xb = bov["lulc_pastagem_ha"] / 1e6
    yb = bov["pec_bovinos_cab"] / 1e6
    anos_b = bov["ano"].values

    points_b = np.array([xb, yb]).T.reshape(-1, 1, 2)
    segments_b = np.concatenate([points_b[:-1], points_b[1:]], axis=1)
    lc_b = LineCollection(segments_b, cmap=cmap, norm=norm, alpha=0.7, linewidth=2)
    lc_b.set_array(anos_b)
    ax.add_collection(lc_b)

    ax.scatter(xb, yb, c=anos_b, cmap=cmap, norm=norm, s=40, zorder=5, edgecolor="k", linewidth=0.3)

    ax.annotate(
        f"{anos_b[0]:.0f}",
        (xb.iloc[0], yb.iloc[0]),
        textcoords="offset points",
        xytext=(-12, -8),
        fontsize=9,
        fontweight="bold",
        color="#440154",
    )
    ax.annotate(
        f"{anos_b[-1]:.0f}",
        (xb.iloc[-1], yb.iloc[-1]),
        textcoords="offset points",
        xytext=(8, 4),
        fontsize=9,
        fontweight="bold",
        color="#FDE725",
    )

    # linha de referência: lotação constante = lotação do último ano
    lot_final = (bov["pec_bovinos_cab"].iloc[-1] / bov["lulc_pastagem_ha"].iloc[-1])
    xb_line = np.linspace(0, xb.max() * 1.05, 100)
    ax.plot(xb_line, xb_line * lot_final, "--", color="gray", lw=1.5, label=f"lotação {anos_b[-1]:.0f} = {lot_final:.2f} cab/ha")

    ax.set_xlabel("Pastagem (milhões de ha)", fontsize=10)
    ax.set_ylabel("Rebanho (milhões de cabeças)", fontsize=10)
    ax.set_title("B) Bovinocultura: intensificou dentro da pastagem", fontsize=12, fontweight="bold", loc="left")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(10.0, xb.max() * 1.02)
    ax.set_ylim(14.0, yb.max() * 1.05)

    # colorbar compartilhada entre A e B
    cbar_ax = fig.add_axes([0.92, 0.55, 0.015, 0.35])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, cax=cbar_ax, label="Ano")

    # ------------------------------------------------------------------
    # Painel C: decomposição indexada soja
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    soy_idx = df[df["ano"].between(1988, 2024)].copy()
    base_soy = 1988
    ax.plot(soy_idx["ano"], index_to(soy_idx, "agri_soja_ha_plantada", base_soy), color="#2E7D32", lw=2.5, label="Área plantada")
    ax.plot(soy_idx["ano"], index_to(soy_idx, "agri_soja_ton", base_soy), color="#F9A825", lw=2.5, label="Produção")
    ax.plot(soy_idx["ano"], index_to(soy_idx, "produtividade_soja_ton_ha", base_soy), color="#00897B", lw=2.5, label="Produtividade")
    ax.axhline(100, color="gray", lw=1, ls="--", alpha=0.5)
    ax.set_xlabel("Ano", fontsize=10)
    ax.set_ylabel("Índice (1988 = 100)", fontsize=10)
    ax.set_title("C) Soja: área e produção caminham juntas", fontsize=12, fontweight="bold", loc="left")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylim(50, max(1200, index_to(soy_idx, "agri_soja_ton", base_soy).max() * 1.1))

    # anotação final
    fim = soy_idx.iloc[-1]
    ax.annotate(
        f"produtividade\n{index_to(soy_idx, 'produtividade_soja_ton_ha', base_soy).iloc[-1]/100:.1f}×",
        xy=(fim["ano"], index_to(soy_idx, "produtividade_soja_ton_ha", base_soy).iloc[-1]),
        xytext=(fim["ano"] - 8, index_to(soy_idx, "produtividade_soja_ton_ha", base_soy).iloc[-1] + 120),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="#00897B", lw=1),
    )

    # ------------------------------------------------------------------
    # Painel D: decomposição indexada bovino
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    bov_idx = df[df["ano"].between(1985, 2024)].copy()
    base_bov = 1985
    ax.plot(bov_idx["ano"], index_to(bov_idx, "lulc_pastagem_ha", base_bov), color="#8D6E63", lw=2.5, label="Pastagem")
    ax.plot(bov_idx["ano"], index_to(bov_idx, "pec_bovinos_cab", base_bov), color="#C62828", lw=2.5, label="Rebanho")
    ax.plot(bov_idx["ano"], index_to(bov_idx, "lotacao_bov_ha", base_bov), color="#EF6C00", lw=2.5, label="Lotação (cab/ha)")
    ax.axhline(100, color="gray", lw=1, ls="--", alpha=0.5)
    ax.set_xlabel("Ano", fontsize=10)
    ax.set_ylabel("Índice (1985 = 100)", fontsize=10)
    ax.set_title("D) Bovinocultura: rebanho cresce mais que a pastagem", fontsize=12, fontweight="bold", loc="left")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylim(80, 160)

    # ------------------------------------------------------------------
    # Título geral e nota
    # ------------------------------------------------------------------
    fig.suptitle(
        "Extensão vs. intensificação em Goiás (1985–2024)",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    nota = (
        "Soja: área plantada SIDRA/PAM × produção SIDRA/PAM — 1988→2024: "
        f"área {index_to(soy_idx, 'agri_soja_ha_plantada', 1988).iloc[-1]/100:.1f}×, "
        f"produção {index_to(soy_idx, 'agri_soja_ton', 1988).iloc[-1]/100:.1f}×, "
        f"produtividade {index_to(soy_idx, 'produtividade_soja_ton_ha', 1988).iloc[-1]/100:.1f}×\n"
        "Bovinocultura: pastagem MapBiomas × rebanho SIDRA — 1985→2024: "
        f"pasto {index_to(bov_idx, 'lulc_pastagem_ha', 1985).iloc[-1]/100:.1f}×, "
        f"rebanho {index_to(bov_idx, 'pec_bovinos_cab', 1985).iloc[-1]/100:.1f}×, "
        f"lotação {index_to(bov_idx, 'lotacao_bov_ha', 1985).iloc[-1]/100:.1f}×"
    )
    fig.text(0.5, -0.04, nota, ha="center", fontsize=9, style="italic", color="#333333")

    return fig


def main():
    df = load_state_series()
    fig = make_figure(df)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Figura salva: {OUT}")

    # Tabela de destaque
    print("\nResumo dos números:")
    soy = df[df["ano"].between(1988, 2024)].copy()
    bov = df[df["ano"].between(1985, 2024)].copy()
    print(f"  Soja 1988: {soy.iloc[0]['agri_soja_ha_plantada']/1e6:.2f} Mha, {soy.iloc[0]['agri_soja_ton']/1e6:.2f} Mt, {soy.iloc[0]['produtividade_soja_ton_ha']:.2f} t/ha")
    print(f"  Soja 2024: {soy.iloc[-1]['agri_soja_ha_plantada']/1e6:.2f} Mha, {soy.iloc[-1]['agri_soja_ton']/1e6:.2f} Mt, {soy.iloc[-1]['produtividade_soja_ton_ha']:.2f} t/ha")
    print(f"  Bovino 1985: {bov.iloc[0]['lulc_pastagem_ha']/1e6:.2f} Mha, {bov.iloc[0]['pec_bovinos_cab']/1e6:.2f} M cab, {bov.iloc[0]['lotacao_bov_ha']:.2f} cab/ha")
    print(f"  Bovino 2024: {bov.iloc[-1]['lulc_pastagem_ha']/1e6:.2f} Mha, {bov.iloc[-1]['pec_bovinos_cab']/1e6:.2f} M cab, {bov.iloc[-1]['lotacao_bov_ha']:.2f} cab/ha")


if __name__ == "__main__":
    main()
