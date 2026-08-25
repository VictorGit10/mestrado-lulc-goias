"""Gera a figura-âncora da Perna 2 do site: "duas populações de pastagem".

⚠️ APOSENTADO EM 25/ago/2026 — A PÁGINA NÃO USA MAIS A SAÍDA DESTE SCRIPT.
--------------------------------------------------------------------------
A peça publicava dois PNGs recortados à mão desta figura em 2/ago
(`sintese_idade_painel_topo.png` e `_base.png`), que **nenhum script
reproduzia**. Órfãos, envelheceram: a legenda do painel B seguiu dizendo
"VEGETAÇÃO NATIVA" três semanas depois de o projeto ter trocado o termo por
"natural" no resto da superfície (D27 — o rótulo de uma figura é afirmação, e
um PNG não é grepável nem entra no diff).

Em vez de manter dois geradores da mesma figura, que precisariam concordar
entre si para sempre, a página passou a consumir **a figura da qualificação**,
que é a mantida — ver `gerar_figura_idade_web.py`, ao lado. Este arquivo fica
como registro do desenho anterior e da razão dele (a nota abaixo, sobre por que
a figura por Ato foi abandonada, continua valendo e não está escrita em outro
lugar). **Não republicar a saída dele sem antes decidir qual das duas figuras é
a da página** — foi a coexistência silenciosa que produziu o defeito.

Saída em Visualizacao/img/graficos/:
  - sintese_idade_duas_populacoes.png   (não referenciado pelo index.html)

POR QUE ESTA FIGURA SUBSTITUI `sintese_idade_pastagem_atos.png` (2026-07-28)
---------------------------------------------------------------------------
A figura anterior organizava a distribuição da idade **por Ato** — e a legenda
logo abaixo pedia ao leitor que NÃO lesse variação entre atos como tendência
(antes de 2020 a mediana mede horizonte de observação; depois, a mudança de
rótulo do Mosaico — D25/D26). Ou seja: o eixo que estruturava a figura era
exatamente o eixo que o texto desautorizava. Pior, ela exibia três pares de
modos diferentes (3a/8a, 4a/17a, 4a/23a) na mesma tela em que o corpo do texto
falava de "~4 e ~22 anos" — o leitor não tinha como reconciliar.

Esta figura ataca o que o texto de fato afirma, em dois painéis:

  A. **Uma população só não explica a curva.** O histograma bruto de Goiás é
     decrescente — não tem dois picos visíveis, e o site não deve fingir que
     tem. O que se vê é um pico jovem estreito e um *ombro* longo. O painel
     desenha o melhor ajuste de UMA gaussiana por cima: ele erra o pico e erra
     o ombro. É a forma honesta de mostrar bimodalidade quando a segunda
     população é larga (σ≈7,5a contra σ≈1,6a da jovem) — ela não produz
     segundo pico, produz platô.

  B. **A mesma conclusão sem modelo nenhum.** Separando os eventos pela ORIGEM
     anterior à pastagem, as duas populações aparecem sem GMM, sem BIC e sem
     ajuste: pasto que veio de lavoura morre jovem (mediana 5a); pasto que veio
     de vegetação natural dura (mediana 13a, cauda longa). Este painel é a
     corroboração independente do painel A — é o argumento que não depende de
     nenhuma escolha de método.

ENTRADAS
    data/processed/pastagem_idade_censo.parquet   (#28 censo, via carregar)

COMO RODAR
    python Visualizacao/scripts/gerar_grafico_duas_populacoes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from analise_reserva_terra import carregar, ajustar_gmm_unidim  # noqa: E402

OUT = ROOT / "Visualizacao" / "img" / "graficos"

COR_JOVEM = "#e8920c"     # laranja — pasto jovem (rotação)
COR_VELHO = "#2e7d32"     # verde — pasto velho (reserva)
COR_BARRA = "#d9d6cd"
COR_UMA = "#8b3a1d"       # terracota — o ajuste de UMA população
COR_FG = "#1a1a1a"
COR_MUTED = "#6b6b6b"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#d8d6cf",
    "axes.labelcolor": COR_FG,
    "xtick.color": COR_MUTED,
    "ytick.color": COR_MUTED,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 150,
    
})

TETO = 40           # anos — corta a cauda irrelevante (>40a é ruído de borda)
BINS = np.arange(0, TETO + 1, 1)


def normal(x, mu, sig):
    return np.exp(-0.5 * ((x - mu) / sig) ** 2) / (sig * np.sqrt(2 * np.pi))


def hist_densidade(idade, peso, bins=BINS):
    """Histograma normalizado para densidade (integra 1 no domínio dos bins)."""
    c, _ = np.histogram(idade, bins=bins, weights=peso)
    larg = np.diff(bins)
    return c / (c.sum() * larg)


def painel_a(ax, df):
    """Uma população só não produz esta curva."""
    nc = df[~df["censurado"]]
    idade = nc["idade_pastagem_anos"].to_numpy(float)
    peso = nc["peso"].to_numpy(float)
    n = peso.sum()

    dens = hist_densidade(idade, peso)
    centros = BINS[:-1] + 0.5
    ax.bar(centros, dens, width=0.9, color=COR_BARRA, zorder=1)

    g = ajustar_gmm_unidim(idade, peso)
    x = np.linspace(0, TETO, 600)

    # O ajuste de UMA população — a hipótese que a figura precisa derrubar.
    ax.plot(x, normal(x, g["mu_1c"], g["sig_1c"]), color=COR_UMA, lw=2.2,
            ls=(0, (5, 2)), zorder=4,
            label=f"se fosse UMA população (μ={g['mu_1c']:.0f}a)")

    c1 = g["w1"] * normal(x, g["mu1"], g["sig1"])
    c2 = g["w2"] * normal(x, g["mu2"], g["sig2"])
    ax.fill_between(x, 0, c1, color=COR_JOVEM, alpha=0.30, zorder=2)
    ax.fill_between(x, 0, c2, color=COR_VELHO, alpha=0.30, zorder=2)
    ax.plot(x, c1, color=COR_JOVEM, lw=1.6, zorder=3)
    ax.plot(x, c2, color=COR_VELHO, lw=1.6, zorder=3)
    ax.plot(x, c1 + c2, color=COR_FG, lw=1.4, zorder=5,
            label="duas populações somadas")

    ax.annotate(
        f"pasto jovem\nμ={g['mu1']:.1f}a · σ={g['sig1']:.1f}a\n{g['w1']:.0%} da massa",
        xy=(g["mu1"], c1.max()), xytext=(9.0, dens.max() * 0.88),
        color=COR_FG, fontsize=8.5, ha="left", va="top",
        arrowprops=dict(arrowstyle="-", color=COR_JOVEM, lw=1.2,
                        connectionstyle="arc3,rad=-0.2"))
    ax.annotate(
        f"pasto velho\nμ={g['mu2']:.1f}a · σ={g['sig2']:.1f}a — {g['sig2'] / g['sig1']:.0f}× mais larga,\n"
        f"por isso vira OMBRO, não pico\n{g['w2']:.0%} da massa",
        xy=(g["mu2"], c2.max()), xytext=(20.5, dens.max() * 0.55),
        color=COR_FG, fontsize=8.5, ha="left", va="top",
        arrowprops=dict(arrowstyle="-", color=COR_VELHO, lw=1.2,
                        connectionstyle="arc3,rad=0.2"))

    # Onde a curva de uma população só erra — o argumento em duas setas.
    for alvo, texto, desloc, rad in [(3.7, "erra o pico", (1.2, 0.066), -0.3),
                                     (28.0, "e erra a cauda", (31.5, 0.022), 0.25)]:
        ax.annotate(texto, xy=(alvo, normal(alvo, g["mu_1c"], g["sig_1c"])),
                    xytext=desloc, fontsize=8.5, color=COR_UMA, ha="center",
                    arrowprops=dict(arrowstyle="->", color=COR_UMA, lw=1.2,
                                    connectionstyle=f"arc3,rad={rad}"))

    ax.set_title("A. Uma população só não produz esta curva", loc="left",
                 fontsize=10.5, color=COR_FG, pad=8)
    ax.set_xlabel("Idade da pastagem no momento da conversão (anos)")
    ax.set_ylabel("Densidade dos eventos")
    ax.set_xlim(0, TETO)
    ax.set_ylim(0, dens.max() * 1.12)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.text(0.985, 0.70, f"{n:,.0f} eventos de idade conhecida".replace(",", "."),
            transform=ax.transAxes, ha="right", fontsize=8, color=COR_MUTED)
    return g


# Origens da fase pastagem. O Mosaico ganha faixa própria em vez de ser somado a
# uma das duas (D25/D26): é a classe que o MapBiomas usa quando NÃO consegue
# separar lavoura de pasto, ou seja incerteza de classificação — escondê-la
# dentro de "antes era lavoura" importaria essa incerteza para dentro do achado.
COORTES = [
    ("agricultura", "antes era LAVOURA — rotação lavoura-pastagem", COR_JOVEM),
    ("mosaico", "antes era MOSAICO DE USOS (o classificador não separou)", "#c8b9a0"),
    ("outros", "outras origens", "#e6e3dc"),
    ("vegetacao_natural", "antes era VEGETAÇÃO NATURAL — reserva antiga", COR_VELHO),
]


def painel_b(ax, df):
    """As mesmas duas populações, identificadas pela origem — sem ajustar nada.

    Composição por idade (participação de cada origem dentro de cada faixa
    etária), não densidade: as coortes têm tamanhos muito diferentes e, em
    densidade, o pico jovem da rotação achata todo o resto do gráfico. A
    pergunta aqui também é outra — não "como cada coorte se distribui", mas
    "de onde vem o pasto que está sendo convertido nesta idade".
    """
    nc = df[~df["censurado"]]
    centros = BINS[:-1] + 0.5
    faixas, rotulos, cores = [], [], []
    for origem, rotulo, cor in COORTES:
        sub = nc[nc["origem_anterior"] == origem]
        c, _ = np.histogram(sub["idade_pastagem_anos"].to_numpy(float), bins=BINS,
                            weights=sub["peso"].to_numpy(float))
        med = np.interp(0.5, np.cumsum(c) / c.sum(), centros)
        faixas.append(c)
        cores.append(cor)
        n_fmt = f"{c.sum():,.0f}".replace(",", ".")
        rotulos.append(f"{rotulo} — {n_fmt} eventos · mediana {med:.0f}a"
                       if origem in ("agricultura", "vegetacao_natural") else rotulo)

    total = np.sum(faixas, axis=0)
    partes = [f / np.where(total > 0, total, 1) for f in faixas]
    # Corta as pontas: abaixo de 2a e acima de 35a o n por faixa cai a ponto de a
    # composição virar ruído (o repique verde em 37–39a é uma dessas pontas).
    m = (centros >= 1.5) & (centros <= 35)
    ax.stackplot(centros[m], *[p[m] for p in partes], colors=cores, labels=rotulos,
                 edgecolor="white", linewidth=0.3)

    # Os dois extremos da faixa "antes era lavoura" — é a leitura inteira do painel.
    laranja = partes[0]
    for xi, ha in [(3.0, "left"), (33.0, "right")]:
        i = int(np.argmin(np.abs(centros - xi)))
        ax.annotate(f"{laranja[i]:.0%}", xy=(centros[i], laranja[i] + 0.035),
                    ha=ha, va="bottom", fontsize=10, color="#7a4a00", weight="bold")

    ax.set_title("B. A mesma divisão sem ajustar modelo nenhum — basta a origem do pasto",
                 loc="left", fontsize=10.5, color=COR_FG, pad=8)
    ax.set_xlabel("Idade da pastagem no momento da conversão (anos)")
    ax.set_ylabel("Composição dos eventos daquela idade")
    ax.set_xlim(1.5, 35)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], frameon=False, fontsize=8.5,
              loc="lower center", bbox_to_anchor=(0.5, -0.52), ncol=1)


def main() -> None:
    df = carregar("censo")
    # Empilhado, não lado a lado: a coluna de texto do site tem 760 px, e dois
    # painéis nessa largura deixariam os rótulos ilegíveis. Cada painel ocupa a
    # largura inteira.
    fig, axes = plt.subplots(2, 1, figsize=(8.6, 9.6))
    fig.subplots_adjust(top=0.885, bottom=0.195, left=0.10, right=0.985, hspace=0.55)
    g = painel_a(axes[0], df)
    painel_b(axes[1], df)

    fig.text(0.005, 0.985, "Duas populações de pastagem, não uma",
             ha="left", va="top", fontsize=15, color=COR_FG)
    fig.text(0.005, 0.955,
             "Idade da pastagem na conversão para lavoura — censo de 44,6 milhões de "
             "pixels, Goiás 1986–2024\n(só os 16,0 milhões cuja idade é conhecida)",
             ha="left", va="top", fontsize=9.5, color=COR_MUTED)
    fig.text(0.005, 0.012,
             "Pixels que já eram pastagem em 1985 têm a idade truncada e ficam de fora. "
             "Fonte: MapBiomas Coleção 10.1, contagem pixel-a-pixel.",
             ha="left", va="top", fontsize=8, color=COR_MUTED)

    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / "sintese_idade_duas_populacoes.png"
    fig.savefig(destino)
    plt.close(fig)
    print(f"[OK] {destino.relative_to(ROOT)}")
    print(f"     jovem μ={g['mu1']:.2f} σ={g['sig1']:.2f} w={g['w1']:.3f} | "
          f"velho μ={g['mu2']:.2f} σ={g['sig2']:.2f} w={g['w2']:.3f} | "
          f"uma só μ={g['mu_1c']:.2f} σ={g['sig_1c']:.2f}")


if __name__ == "__main__":
    main()
