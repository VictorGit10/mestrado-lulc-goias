"""fig_sintese_idade_atos.py — Pipeline #28

Gera `Visualizacao/img/graficos/sintese_idade_pastagem_atos.png`, a figura-síntese
da Perna 2 no site.

Até 21/jul/2026 esta figura não tinha script: era um PNG solto de 20/mai que
ninguém sabia regerar. Quando os números do #28 mudaram (censo, correção da
classe 21), a legenda no site foi reescrita mas a imagem continuou a mesma —
legenda e figura passaram a discordar em silêncio. Daí este arquivo existir.

## Decisões de visualização

**Painéis empilhados, não curvas sobrepostas.** A distribuição tem dois modos e
cauda longa; sobrepostas, as curvas se ocultam justamente na região que importa.
Empilhadas com eixo x compartilhado, a comparação entre Atos acontece por
POSIÇÃO — codificação mais forte que cor — e a identidade de cada painel vem do
seu título, nunca da cor sozinha.

**Paleta validada.** `#ad7532 / #2a6f9e / #3f8a4a` passa nos seis checks
(banda de luminosidade, piso de croma, separação para daltonismo, piso de visão
normal, contraste). A paleta anterior do projeto (`#8a8a82 / #4a7ba6 / #2d5a3d`)
FALHAVA: cinza contra azul dava ΔE 11,5 para visão normal, abaixo do piso 15 —
difícil de separar mesmo enxergando todas as cores.

**Só idades conhecidas.** Os censurados (64,1%) ficam fora: misturá-los faria o
eixo x significar duas coisas diferentes na mesma curva (idade real e limite
inferior). A fração censurada de cada Ato vai anotada no painel.

Como rodar:
    python scripts/fig_sintese_idade_atos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analise_reserva_terra import carregar, vp  # noqa: E402
from estatistica_ponderada import mediana, gmm_ponderado  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "Visualizacao" / "img" / "graficos" / "sintese_idade_pastagem_atos.png"

# Paleta validada — ver docstring. NÃO trocar sem rodar o validador.
COR = {"I": "#ad7532", "II": "#2a6f9e", "III": "#3f8a4a"}
ATOS = [("I", 1985, 2000, "Herança"),
        ("II", 2001, 2019, "Expansão"),
        ("III", 2020, 2024, "Seletivo")]

TINTA = "#26251f"
TINTA_FRACA = "#6b6a61"
SURF = "#fcfcfb"


def y_peso(r: dict, mu: float) -> float:
    """Peso (%) da componente cujo mu é o dado."""
    i = int(np.argmin(np.abs(np.asarray(r["mu"]) - mu)))
    return float(r["peso"][i]) * 100


def main() -> None:
    df = carregar("censo")
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 8.4), sharex=True,
                             gridspec_kw={"hspace": 0.32})
    fig.patch.set_facecolor(SURF)
    bins = np.arange(0.5, 40.5, 1.0)

    for ax, (ato, a0, a1, nome) in zip(axes, ATOS):
        ax.set_facecolor(SURF)
        sub = df[df["ato"] == ato]
        nc = sub[~sub["censurado"]]
        v, w = vp(nc)
        n_cens = sub.loc[sub["censurado"], "peso"].sum()
        pct_cens = n_cens / sub["peso"].sum() * 100

        cont, _, _ = ax.hist(v, bins=bins, weights=w, density=True, color=COR[ato],
                             edgecolor=SURF, linewidth=0.4, alpha=0.9)

        # Os dois modos, explícitos: sem isso o leitor tem que adivinhar onde eles estão
        r = gmm_ponderado(v, w, n_comp=2)
        curvas = []
        xs = np.linspace(0.5, 40, 400)
        if r.get("ok"):
            for mu, sg, pw in zip(r["mu"], r["sigma"], r["peso"]):
                y = pw * np.exp(-0.5 * ((xs - mu) / sg) ** 2) / (sg * np.sqrt(2 * np.pi))
                ax.plot(xs, y, color=TINTA, linewidth=1.4, linestyle="--", alpha=0.75)
                curvas.append((mu, y))

        # Folga no topo ANTES de anotar: sem isso os rótulos dos componentes
        # invadem o título do painel (acontecia nos Atos I e III).
        ymax = max(cont.max(), max((y.max() for _, y in curvas), default=0))
        ax.set_ylim(0, ymax * 1.42)

        for mu, y in curvas:
            ax.annotate(f"{mu:.0f}a · {y_peso(r, mu):.0f}%",
                        xy=(mu, min(y.max(), ymax * 1.02)), xytext=(0, 6),
                        textcoords="offset points", ha="center",
                        fontsize=8.5, color=TINTA)

        # Mediana acima da faixa dos rótulos de componente: no Ato I o pico jovem
        # é o próprio ymax e os dois textos colidiam.
        med = mediana(v, w)
        ax.axvline(med, color="#a3387f", linewidth=1.6, ymax=0.70)
        ax.annotate(f"mediana {med:.0f}a", xy=(med, ymax * 1.33),
                    xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color="#a3387f")

        ax.set_title(f"Ato {ato} — {nome}   ({a0}–{a1})",
                     loc="left", fontsize=11.5, color=TINTA, pad=7)
        ax.text(0.995, 0.93, f"{w.sum() / 1e6:.1f} mi de pixels com idade conhecida\n"
                             f"{pct_cens:.0f}% censurados à esquerda (fora do gráfico)",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=8, color=TINTA_FRACA, linespacing=1.4)

        ax.grid(axis="y", color="#e6e5df", linewidth=0.7)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color("#c9c8c0")
        ax.tick_params(colors=TINTA_FRACA, labelsize=8.5, length=3)
        ax.set_yticks([])

    axes[-1].set_xlabel("Idade da pastagem no momento da conversão para agricultura (anos)",
                        fontsize=10, color=TINTA, labelpad=8)
    axes[-1].set_xlim(0, 40)

    fig.suptitle("Duas populações de pastagem, não uma",
                 x=0.055, y=0.985, ha="left", fontsize=14.5, color=TINTA)
    fig.text(0.055, 0.945,
             "Idade da pastagem na conversão para lavoura — censo de 44,6 milhões de pixels, Goiás 1986–2024",
             ha="left", fontsize=9.5, color=TINTA_FRACA)
    fig.text(0.055, 0.018,
             "Linhas tracejadas: componentes da mistura gaussiana ajustada às idades conhecidas.  "
             "Fonte: MapBiomas Coleção 10.1.",
             ha="left", fontsize=8, color=TINTA_FRACA)

    fig.subplots_adjust(top=0.895, bottom=0.105, left=0.055, right=0.975)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA, dpi=150, facecolor=SURF)
    plt.close(fig)
    print(f"OK: {SAIDA.relative_to(ROOT)}  ({SAIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
