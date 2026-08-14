r"""Estilo compartilhado das figuras do texto de qualificação.

Por que este módulo existe
--------------------------
As figuras de ``outputs/`` são feitas para tela: ``figsize`` de 9x5 a 12x12
polegadas, título embutido, fontes de 10 a 14 pt. Reduzidas à mancha da ABNT
(16 cm = 6,3 pol), um rótulo de 10 pt vira ~5 pt — ilegível em papel.

Aqui as figuras nascem já na geometria da página: largura exatamente igual à
``\textwidth``, de modo que ``\includegraphics[width=\textwidth]`` aplique
escala 1,0 e o corpo de 9 pt da figura saia como 9 pt no PDF, junto de um
texto de 12 pt em Times.

Convenções
----------
* **Sem título embutido.** Na ABNT o título é a ``\caption`` acima da figura;
  título dentro da imagem duplicaria. O que a figura precisa dizer de si vai
  em anotação no eixo, não em ``suptitle``.
* **Saída em PDF** (vetor) para os gráficos de eixo — nítidos em qualquer
  ampliação e leves. Rasters (mapas do GEE) saem em PNG a 300 dpi.
* **Prévia em PNG** ao lado do PDF, só para conferência visual rápida; o
  LaTeX usa o PDF.

Uso::

    from estilo import configurar, salvar, CORES, LARGURA_TEXTO
    configurar()
    fig, ax = plt.subplots(figsize=(LARGURA_TEXTO, 3.4))
    ...
    salvar(fig, "04_decomposicao_fronteira")
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Geometria da página
# --------------------------------------------------------------------------
# A4 (21 cm) com margens ABNT 3-3-2-2 => mancha de 16 cm.
LARGURA_TEXTO = 16.0 / 2.54  # 6,30 pol — usar com width=\textwidth
LARGURA_MEIA = LARGURA_TEXTO / 2

DIR_FIG = Path(__file__).resolve().parent
DIR_RAIZ = DIR_FIG.parent.parent
DIR_PROC = DIR_RAIZ / "data" / "processed"
DIR_OUT = DIR_RAIZ / "outputs"

# Prévias em PNG para conferência (fora do repositório do usuário).
DIR_PREVIA = Path(
    r"C:\Users\amara\AppData\Local\Temp\claude"
    r"\C--Users-amara-OneDrive-Documentos-Antigravity-Mestrado"
    r"\67904e65-85bc-4c93-a9a3-0b420baf29ca\scratchpad\previa_figuras"
)

# --------------------------------------------------------------------------
# Paleta — a mesma da visualização, para que quem vier do site reconheça
# --------------------------------------------------------------------------
CORES = {
    # camadas de uso da terra (centro_massa.py, l. 114-117)
    "agricultura": "#c2185b",        # magenta
    "pastagem": "#e8920c",           # laranja
    "bovinos": "#7a1f1f",            # vinho
    "veg_natural": "#2e7d32",        # verde
    "mosaico": "#7b1fa2",            # roxo
    # réguas de medida (CORES_RULER)
    "agric_uniao": "#7b1fa2",
    "soja_sidra": "#1565c0",
    # recortes regionais (CORES_REGIAO)
    "Sul": "#c2185b",
    "Centro": "#8d6e63",
    "Norte": "#2e7d32",
    # apoio
    "neutro": "#555555",
    "grade": "#cccccc",
    "banda": "#000000",
}

# Paleta das SETE CLASSES do raster. Deliberadamente igual à dos mapas do
# Pipeline #10 (convenção MapBiomas), e não à paleta de camadas acima: o
# Sankey e o painel de mapas ficam no mesmo capítulo, e duas cores diferentes
# para "Mosaico de Usos" a duas páginas de distância seria armadilha de
# leitura. Os valores são os RGB exatos que saem do raster.
CORES_CLASSES = {
    "Vegetação Natural": "#1b8a2f",
    "Pastagem": "#ffd700",
    "Agricultura": "#ff69b4",
    "Mosaico de Usos": "#c98a4b",
    "Água": "#4169e1",
    "Área Urbana": "#a0a0a0",
    "Outros": "#d2b48c",
}

# RGB de origem no raster -> nome da classe (o raster tem 8 cores exatas)
RGB_CLASSES = {
    (27, 138, 47): "Vegetação Natural",
    (255, 215, 0): "Pastagem",
    (255, 105, 180): "Agricultura",
    (201, 138, 75): "Mosaico de Usos",
    (65, 105, 225): "Água",
    (160, 160, 160): "Área Urbana",
    (210, 180, 140): "Outros",
}


def configurar() -> None:
    """Aplica o estilo de página aos ``rcParams``."""
    plt.rcdefaults()
    plt.rcParams.update(
        {
            # Times, para casar com o newtx do corpo do texto
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            # corpo de 9 pt: legível a 100% ao lado de um texto de 12 pt
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.titlesize": 9,
            # traço fino: a figura é pequena, linha grossa vira borrão
            "axes.linewidth": 0.6,
            "grid.linewidth": 0.4,
            "lines.linewidth": 1.2,
            "patch.linewidth": 0.5,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            # moldura discreta: só os eixos que carregam informação
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": CORES["grade"],
            "grid.alpha": 0.6,
            "legend.frameon": False,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            # texto vetorial de verdade no PDF (não contornos)
            "pdf.fonttype": 42,
            "pdf.compression": 9,
            # vírgula decimal, como manda o português
            "axes.formatter.use_locale": False,
        }
    )


def virgula(x, _pos=None) -> str:
    """Formatador de eixo com vírgula decimal."""
    s = f"{x:g}"
    return s.replace(".", ",")


# --------------------------------------------------------------------------
# Cartografia — reusa o padrão do projeto (scripts/_cartografia.py)
# --------------------------------------------------------------------------
# A rosa-dos-ventos Mariners de 16 pontas e a régua de escala já existem e são
# usadas pelos mapas de `outputs/`. Reusá-las mantém a cartografia da
# dissertação toda igual. O que muda aqui é só o dimensionamento: aquele
# módulo foi calibrado para figuras de tela de 10-12 polegadas, e estes
# painéis têm 2 a 3. `size` vem pequeno, e o "N" é recomposto depois porque o
# módulo o escala junto com a rosa (a 0,45 ele sairia com 5 pt, ilegível).

def _cartografia():
    import sys

    dir_scripts = str(DIR_RAIZ / "scripts")
    if dir_scripts not in sys.path:
        sys.path.insert(0, dir_scripts)
    import _cartografia as c

    return c


def pronta_para_cartografia(fig, **kwargs) -> None:
    """Fecha o layout e desenha, para que a régua de escala meça o eixo final.

    Ver a advertência de ordem em :func:`escala`.
    """
    fig.tight_layout(**kwargs)
    fig.canvas.draw()


def norte(ax, size: float = 0.46, loc: str = "upper left",
          borderpad: float = 0.2, n_fontsize: float = 7.5) -> None:
    """Rosa-dos-ventos do projeto, dimensionada para a página."""
    from matplotlib.text import Text

    antes = list(ax.artists)
    _cartografia().adicionar_norte(ax, location=loc, size=size,
                                   borderpad=borderpad)

    def _textos(artista):
        for filho in getattr(artista, "get_children", lambda: [])():
            if isinstance(filho, Text):
                yield filho
            else:
                yield from _textos(filho)

    for artista in ax.artists:
        if artista in antes:
            continue
        for t in _textos(artista):
            t.set_fontsize(n_fontsize)


def escala(ax, dx: float = 1.0, total_km: float | None = None,
           loc: str = "lower left", alvo_px: int = 150,
           borderpad: float = 0.2) -> None:
    """Régua de escala do projeto.

    ``dx`` = metros por unidade do eixo x. Em CRS métrico (EPSG:5880) é 1;
    num raster desenhado por ``imshow`` em pixels, é o metro-por-pixel.

    ATENÇÃO À ORDEM: a régua é dimensionada a partir da largura do eixo **em
    pixels**, medida no momento da chamada, e depois fixada em pontos. Chamar
    isto antes de ``tight_layout()`` produz uma barra fora de escala — aqui o
    erro medido foi de −17,5%, porque o ``tight_layout`` alarga o eixo de
    726 px para 880 px. Chame sempre depois do layout final e de um
    ``fig.canvas.draw()``. A função ``pronta_para_cartografia()`` faz as duas
    coisas.
    """
    _cartografia().adicionar_escala(ax, dx=dx, total_km=total_km,
                                    location=loc, bar_pixel_target=alvo_px,
                                    borderpad=borderpad)


def salvar(fig, nome: str, raster: bool = False) -> Path:
    """Grava a figura em ``fig/`` e uma prévia PNG no scratchpad.

    ``raster=True`` grava PNG em vez de PDF — para figuras que já são imagem
    (mosaicos de mapas do GEE), onde o PDF só embrulharia o mesmo raster.
    """
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    DIR_PREVIA.mkdir(parents=True, exist_ok=True)

    ext = "png" if raster else "pdf"
    destino = DIR_FIG / f"{nome}.{ext}"
    fig.savefig(destino)

    previa = DIR_PREVIA / f"{nome}.png"
    fig.savefig(previa, dpi=150)

    plt.close(fig)
    print(f"  {destino.relative_to(DIR_RAIZ)}  (prévia: {previa.name})")
    return destino
