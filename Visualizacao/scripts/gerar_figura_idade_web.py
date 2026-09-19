"""Exporta a figura de idade da pastagem da QUALIFICAÇÃO em resolução de tela.

POR QUE ESTE SCRIPT EXISTE (25/ago/2026)
----------------------------------------
A peça publicava dois PNGs — `sintese_idade_painel_topo.png` e
`sintese_idade_painel_base.png` — que **nenhum script reproduzia**. Eles nasceram
em 2/ago de um recorte manual da figura empilhada de
`gerar_grafico_duas_populacoes.py`, e ficaram órfãos: o gerador seguiu produzindo
o arquivo empilhado, que a página não usa. Um arquivo publicado sem gerador é uma
citação congelada — e foi assim que a legenda do painel B seguiu dizendo
"VEGETAÇÃO NATIVA" três semanas depois de o projeto ter trocado o termo por
"natural" em todo o resto da superfície (D27).

Em vez de manter dois geradores da mesma figura, que precisariam concordar entre
si para sempre, a página passa a consumir **a figura da qualificação**, que é a
mantida: foi regerada em 21/ago, traz os parâmetros do censo anotados dentro do
gráfico (μ₁≈3,9a e μ₂≈16,3a) e rotula as três faixas de origem por dentro, com a
mediana de cada uma, em vez de uma legenda de quatro linhas embaixo.

O que este script faz é só mudar o **suporte**: a mesma função
`fig_idade_pastagem()` de `qualificacao/fig/gerar_figuras.py`, gravada em PNG na
resolução da tela em vez de PDF na mancha de 16 cm. Nenhum número é recalculado
aqui, e nada da qualificação é modificado — a função é chamada com o `salvar` do
módulo de estilo temporariamente redirecionado.

COMO RODAR
    python Visualizacao/scripts/gerar_figura_idade_web.py            # pt (index.html)
    python Visualizacao/scripts/gerar_figura_idade_web.py --lang en  # en (index.en.html)

SAÍDA
    Visualizacao/img/graficos/idade_pastagem_duas_populacoes.png
    Visualizacao/img/graficos/idade_pastagem_duas_populacoes.en.png

INGLÊS (set/2026)
    A função da qualificação desenha em português e não deve ganhar um segundo
    idioma — ela é a figura do texto. A versão inglesa traduz os textos JÁ
    DESENHADOS, logo antes de salvar: cada rótulo passa por TRADUCOES (troca de
    trechos, na ordem) e a vírgula decimal vira ponto. Se a função da
    qualificação ganhar um rótulo novo, ele sai em português e o aviso
    "[sem tradução]" aponta qual.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
DIR_QUAL = ROOT / "qualificacao" / "fig"
OUT = ROOT / "Visualizacao" / "img" / "graficos"
NOME = "idade_pastagem_duas_populacoes"

# 200 dpi dá ~1.700 px de largura: mais que o dobro da coluna de texto do site
# (~700 px em tela grande), que é o que mantém o rótulo das faixas nítido em tela
# de alta densidade e no lightbox, sem inflar o bundle.
DPI_TELA = 200

# A qualificação põe os dois painéis LADO A LADO, que é o certo para a mancha de
# 16 cm. Na página, não: a coluna de texto tem ~700 px e no celular cai a ~330,
# e a essa largura os rótulos de dentro das faixas ficam ilegíveis mesmo no
# lightbox — foi por isso que a figura anterior do site era empilhada. Aqui a
# mesma função é chamada com o arranjo trocado para 2×1: muda a forma, e nenhum
# número.
FIGSIZE_EMPILHADO = (7.6, 8.4)

EN = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en"

# Trechos em pt -> en, aplicados em ordem (os mais longos primeiro). A
# terminologia segue a de index.en.html: young/old pasture, Mosaic of Uses,
# cropland, "rotation".
TRADUCOES = [
    ("idade da pastagem na conversão (anos)", "pasture age at conversion (years)"),
    ("densidade dos eventos", "event density"),
    ("origem anterior do pixel (%)", "prior class of the pixel (%)"),
    ("censo de pixels", "pixel census"),
    ("se fosse 1 população", "if it were 1 population"),
    ("2 populações somadas", "2 populations summed"),
    ("pasto jovem", "young pasture"),
    ("pasto velho", "old pasture"),
    ("da massa", "of the mass"),
    ("mais larga:\nvira ombro, não pico", "wider:\nbecomes a shoulder, not a peak"),
    ("antes era VEGETAÇÃO NATURAL", "previously NATURAL VEGETATION"),
    ("antes era MOSAICO DE USOS", "previously MOSAIC OF USES"),
    ("antes era LAVOURA\n(rotação)", "previously CROPLAND\n(rotation)"),
    ("mediana", "median"),
]


def traduzir(texto: str) -> str:
    novo = texto
    for pt, en in TRADUCOES:
        novo = novo.replace(pt, en)
    novo = re.sub(r"(\d),(\d)", r"\1.\2", novo)   # vírgula decimal -> ponto
    novo = re.sub(r"(\d)a\b", r"\1y", novo)        # "3,9a" (anos) -> "3.9y"
    if novo == texto and re.search(r"[A-Za-zÀ-ú]{3,}", texto):
        print(f"    [sem tradução] {texto!r}")
    return novo


def traduzir_figura(fig) -> None:
    """Passa todo texto desenhado da figura para o inglês."""
    for txt in fig.findobj(plt.Text):
        if txt.get_text():
            txt.set_text(traduzir(txt.get_text()))
    # Os ticks são gerados na hora do desenho pelo formatador de vírgula da
    # qualificação: embrulha o formatador em vez de reescrever o rótulo.
    for ax in fig.axes:
        for eixo in (ax.xaxis, ax.yaxis):
            fmt = eixo.get_major_formatter()
            if isinstance(fmt, FuncFormatter):
                eixo.set_major_formatter(FuncFormatter(
                    lambda x, p, f=fmt: f(x, p).replace(",", ".")))


def main() -> None:
    sys.path.insert(0, str(DIR_QUAL))
    import estilo
    import gerar_figuras

    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / f"{NOME}{'.en' if EN else ''}.png"

    def salvar_na_viz(fig, nome: str, raster: bool = False) -> Path:
        if EN:
            traduzir_figura(fig)
        fig.savefig(destino, dpi=DPI_TELA, facecolor="white",
                    bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)
        return destino

    subplots_original = gerar_figuras.plt.subplots

    def subplots_empilhado(*args, **kwargs):
        """Devolve 2 linhas × 1 coluna onde a qualificação pede 1 × 2.

        A função de figura desempacota ``fig, (ax1, ax2)``, então o que ela
        precisa é de um par de eixos — a disposição deles na tela é indiferente
        para o código que desenha.
        """
        if args[:2] == (1, 2):
            kwargs["figsize"] = FIGSIZE_EMPILHADO
            return subplots_original(2, 1, **kwargs)
        return subplots_original(*args, **kwargs)

    # A função chama `salvar` e `plt` pelos nomes que o módulo dela importou,
    # então é lá que a troca precisa acontecer — mexer no `estilo` não teria
    # efeito.
    original = gerar_figuras.salvar
    gerar_figuras.salvar = salvar_na_viz
    gerar_figuras.plt.subplots = subplots_empilhado
    try:
        estilo.configurar()
        gerar_figuras.fig_idade_pastagem()
    finally:
        gerar_figuras.salvar = original
        gerar_figuras.plt.subplots = subplots_original

    kb = destino.stat().st_size // 1024
    print(f"[OK] {destino.relative_to(ROOT)}  ({kb} KB, {DPI_TELA} dpi)")


if __name__ == "__main__":
    main()
