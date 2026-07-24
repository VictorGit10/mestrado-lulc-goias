"""fig_borda_movel.py — figura do teste da borda móvel (§9.6 do #28D)
================================================================================
Uma linha por coleção MapBiomas (6/8/9/10.1), razão pasto→Mosaico / pasto→agricultura
em Goiás por ano-calendário (eixo y log). A MENSAGEM é visual: as curvas se SOBREPÕEM
em cada ano-calendário (rampa ancorada em 2021+), em vez de cada uma disparar na SUA
borda terminal (estrela). Se fosse artefato de borda, cada estrela seria o pico da sua
curva; não é.

Paleta: rampa sequencial azul (coleção antiga=clara → nova=escura) — as coleções são
ORDENADAS, então sequencial single-hue é a codificação certa e é CVD-safe por
construção. Lê `data/processed/borda_movel_matriz_colecoes.csv` (GEE 90 m).

    python scripts/fig_borda_movel.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "processed" / "borda_movel_matriz_colecoes.csv"
OUT = ROOT / "outputs" / "deriva_mosaico" / "borda_movel.png"

# rampa sequencial azul: col6 (antiga) clara -> col10.1 (nova) escura
CORES = {"col6": "#9ecae1", "col8": "#4292c6", "col9": "#2171b5", "col10.1": "#08306b"}
TERMINAL = {"col6": 2020, "col8": 2022, "col9": 2023, "col10.1": 2024}
TINTA, TINTA2 = "#1a1a1a", "#5a5a5a"


def main() -> None:
    df = pd.read_csv(CSV, index_col=0)
    df.columns = [int(c) for c in df.columns]
    fig, ax = plt.subplots(figsize=(9.0, 5.6), dpi=150)

    import matplotlib.lines as mlines
    xmin = 2010
    handles = []
    for rótulo, linha in df.iterrows():
        nome = rótulo.split(" ")[0]  # "col9 (→2023)" -> "col9"
        cor = CORES[nome]
        s = linha[[a for a in df.columns if a >= xmin]].dropna()
        ax.plot(s.index, s.values, "-", color=cor, lw=2.2, zorder=3,
                marker="o", ms=5, mfc=cor, mec="white", mew=0.8)
        # estrela no ano terminal (d=0) da coleção + o ano por baixo
        yt = df.loc[rótulo, TERMINAL[nome]]
        ax.plot(TERMINAL[nome], yt, marker="*", ms=18, color=cor, mec="white",
                mew=1.1, zorder=5)
        dy = 1.32 if nome in ("col9", "col10.1") else 0.80  # afasta rótulos que se juntam no topo
        ax.annotate(str(TERMINAL[nome]), (TERMINAL[nome], yt * dy),
                    ha="center", va="bottom" if dy > 1 else "top",
                    fontsize=8.5, color=cor, fontweight="bold")
        handles.append(mlines.Line2D([], [], color=cor, lw=2.4, marker="*", ms=12,
                                     mec="white", mew=0.8, label=f"MapBiomas {rótulo}"))

    # faixa da rampa 2021+
    ax.axvspan(2020.5, 2024.5, color="#f2a900", alpha=0.08, zorder=0)
    ax.annotate("rampa 2021+\n(surge em TODA coleção\nque alcança 2021)", (2020.2, 30),
                fontsize=9, color="#8a6d00", ha="right", va="center")
    ax.annotate("col6 termina em 2020,\nsem rampa (curva plana)", (2015.6, 3.0),
                fontsize=9, color=TINTA2, ha="center", va="bottom")
    leg = ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.015, 0.99),
                    frameon=False, fontsize=9, handlelength=1.6, labelspacing=0.35)
    for t in leg.get_texts():
        t.set_color(TINTA)

    ax.set_yscale("log")
    ax.set_ylim(0.4, 45)
    ax.set_yticks([0.5, 1, 2, 5, 10, 20, 40])
    ax.yaxis.set_major_formatter(FixedFormatter(["0,5", "1", "2", "5", "10", "20", "40"]))
    ax.set_xlim(xmin - 0.3, 2026.2)
    ax.xaxis.set_major_locator(FixedLocator(list(range(2010, 2025, 2))))
    ax.axhline(1.0, color="#cccccc", lw=1, ls=(0, (4, 3)), zorder=1)

    ax.set_ylabel("razão  pasto→Mosaico / pasto→agricultura   (Goiás, escala log)",
                  fontsize=10.5, color=TINTA)
    ax.set_xlabel("ano-calendário da conversão", fontsize=10.5, color=TINTA)
    ax.set_title("A rampa do Mosaico é ancorada no CALENDÁRIO (2021+), não na borda de cada coleção",
                 fontsize=12.5, color=TINTA, fontweight="bold", pad=14)
    ax.text(0.0, 1.015, "★ = último ano de cada coleção (d=0). As estrelas NÃO são o pico da sua curva "
            "→ o classificador não infla a borda; as curvas se sobrepõem por ano.",
            transform=ax.transAxes, fontsize=8.8, color=TINTA2)

    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#bbbbbb")
    ax.tick_params(colors=TINTA2, labelsize=9.5)
    ax.grid(axis="y", color="#eeeeee", lw=0.8, zorder=0)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    print(f"figura -> {OUT}")


if __name__ == "__main__":
    main()
