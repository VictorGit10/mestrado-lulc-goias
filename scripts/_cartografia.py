"""_cartografia.py — helpers cartograficos compartilhados para os mapas da dissertacao.

Padroniza:
    - adicionar_norte(ax): icone SIG (triangulo solido + N) em caixa branca,
      ancorado num canto do ax via AnchoredOffsetbox.
    - adicionar_escala(ax, dx): barra de escala SEGMENTADA estilo cartografico
      (4 retangulos preto/branco alternados + ticks numericos em km + sufixo 'km'),
      desenhada em pixels via AnchoredOffsetbox. Funciona identicamente em
      mapas vetoriais (gpd.plot) e raster (ax.imshow), independente de inversao
      de eixo.

Uso:
    from _cartografia import adicionar_norte, adicionar_escala

    fig, ax = plt.subplots(...)
    gdf.plot(ax=ax, ...)         # vetor em CRS metrico (EPSG:5880)
    adicionar_escala(ax, dx=1)
    adicionar_norte(ax)

    # Para raster via imshow (axes em pixels, dx = metros/pixel):
    ax.imshow(img)
    adicionar_escala(ax, dx=metros_por_pixel)
    adicionar_norte(ax)
"""
from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea
from matplotlib.patches import Polygon, Rectangle
from matplotlib.text import Text


# ============================================================
# Norte
# ============================================================
def adicionar_norte(
    ax: Axes,
    location: str = "upper right",
    size: float = 1.3,
    pad: float = 0.4,
    borderpad: float = 0.6,
) -> None:
    """Seta de norte estilo SIG: triangulo preto solido apontando para cima,
    com a letra 'N' abaixo, dentro de uma caixa branca discreta.

    Parametros:
        location: canto do ax ('upper right' (default), 'upper left',
                  'lower right', 'lower left').
        size: fator de escala (1.0 = tamanho default; 1.5 = 50% maior).
    """
    box_w = int(28 * size)
    box_h = int(40 * size)
    da = DrawingArea(box_w, box_h, 0, 0)

    cx = box_w / 2
    tri = Polygon(
        [
            [cx, box_h * 0.92],
            [cx - box_w * 0.34, box_h * 0.42],
            [cx + box_w * 0.34, box_h * 0.42],
        ],
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
    )
    da.add_artist(tri)

    n_label = Text(
        cx,
        box_h * 0.02,
        "N",
        ha="center",
        va="bottom",
        fontsize=int(12 * size),
        fontweight="bold",
    )
    da.add_artist(n_label)

    box = AnchoredOffsetbox(
        loc=location,
        child=da,
        frameon=True,
        pad=pad,
        borderpad=borderpad,
    )
    box.patch.set_facecolor("white")
    box.patch.set_edgecolor("0.35")
    box.patch.set_linewidth(0.6)
    box.patch.set_alpha(0.92)
    ax.add_artist(box)


# ============================================================
# Escala (barra segmentada)
# ============================================================
# Valores "redondos" escolhidos para dividir limpo em 4 segmentos
# (todos sao multiplos de 4: 4/4=1, 8/4=2, 20/4=5, 40/4=10, 100/4=25,
#  200/4=50, 400/4=100, 1000/4=250, 2000/4=500)
_NICE_KM = [2, 4, 8, 20, 40, 80, 100, 200, 400, 800, 1000, 2000]


def _nice_total_km(extent_m: float, fraction: float = 0.22) -> float:
    """Escolhe um comprimento 'redondo' proximo a fraction*extent (em km)."""
    target = (extent_m / 1000.0) * fraction
    return float(min(_NICE_KM, key=lambda v: abs(v - target)))


def _estimar_ax_pixel_width(ax: Axes) -> float:
    """Estima largura do ax em pixels usando o renderer atual."""
    fig = ax.figure
    try:
        renderer = fig.canvas.get_renderer()
        bbox = ax.get_window_extent(renderer)
        return float(bbox.width)
    except Exception:
        # Fallback: figure_width_inches * dpi * ax_position.width
        ax_pos = ax.get_position()
        return float(fig.get_size_inches()[0] * fig.dpi * ax_pos.width)


def adicionar_escala(
    ax: Axes,
    dx: float = 1.0,
    total_km: float | None = None,
    n_segs: int = 4,
    location: str = "lower left",
    bar_pixel_target: int = 180,
    borderpad: float = 0.7,
) -> None:
    """Barra de escala cartografica segmentada estilo SIG (preto/branco
    alternado), com ticks numericos em km abaixo e sufixo 'km' a direita.

    Implementacao: cria um DrawingArea em coordenadas de pixel e ancora num
    canto do ax via AnchoredOffsetbox. Funciona para qualquer tipo de plot
    (gpd.plot vetorial, ax.imshow raster) e para qualquer orientacao de eixo.

    Parametros:
        dx: metros por unidade do eixo x.
            - GeoDataFrame em CRS metrico (EPSG:5880): dx=1
            - imshow de raster com axes em pixels: dx = metros_por_pixel
            - Coordenadas geograficas (graus): dx ~= 111000 m/grau
        total_km: comprimento total em km. Se None, escolhe automaticamente
                  um valor "redondo" (1/2/5/10/20/25/50/100/200/250/500/1000 km)
                  proximo a bar_pixel_target pixels.
        n_segs: numero de segmentos alternados (default 4).
        location: canto do ax onde ancorar (default 'lower left').
        bar_pixel_target: largura aproximada desejada da barra em pixels
                          (default 180).
    """
    # Estimar quantos metros equivalem a bar_pixel_target pixels do ax
    xlim = ax.get_xlim()
    x_range_data = abs(xlim[1] - xlim[0])
    ax_pixel_width = _estimar_ax_pixel_width(ax)
    if ax_pixel_width <= 1:
        ax_pixel_width = 800  # fallback razoavel

    # metros por pixel do ax
    metros_por_pixel_ax = (x_range_data * dx) / ax_pixel_width
    metros_alvo = bar_pixel_target * metros_por_pixel_ax

    if total_km is None:
        # Escolher valor "redondo" (km) proximo ao alvo em pixels.
        total_km = _nice_total_km(metros_alvo, fraction=1.0)

    # Largura final da barra em pixels (depois de arredondar para km redondo)
    bar_pixel_w = (total_km * 1000.0) / metros_por_pixel_ax
    bar_pixel_h = 9  # altura da barra em px

    # Dimensoes do DrawingArea: largura precisa incluir a barra + sufixo "km"
    # e a altura precisa incluir a barra + ticks + labels
    suffix_w = 28  # espaco para " km"
    da_w = bar_pixel_w + suffix_w
    label_h = 14   # espaco para os tick labels abaixo
    da_h = bar_pixel_h + label_h + 2

    da = DrawingArea(da_w, da_h, 0, 0)

    # No DrawingArea, y cresce para CIMA (origin no canto inferior-esquerdo).
    # Posicionamos a barra perto do topo do DrawingArea, e os labels abaixo dela.
    bar_y = label_h + 1  # deixar espaco para labels abaixo

    # Segmentos alternados
    seg_w = bar_pixel_w / n_segs
    for i in range(n_segs):
        cor = "black" if i % 2 == 0 else "white"
        rect = Rectangle(
            (i * seg_w, bar_y),
            seg_w,
            bar_pixel_h,
            facecolor=cor,
            edgecolor="black",
            linewidth=0.6,
        )
        da.add_artist(rect)

    # Tick labels (km values) abaixo da barra
    step_km = total_km / n_segs
    for i in range(n_segs + 1):
        x = i * seg_w
        km_val = i * step_km
        label = f"{km_val:.0f}" if step_km >= 1 else f"{km_val:g}"
        t = Text(
            x, bar_y - 2,
            label,
            ha="center",
            va="top",
            fontsize=7.5,
        )
        da.add_artist(t)

    # Sufixo "km" a direita da barra (alinhado verticalmente com o centro)
    suffix = Text(
        bar_pixel_w + 4,
        bar_y + bar_pixel_h / 2,
        "km",
        ha="left",
        va="center",
        fontsize=8,
        fontweight="bold",
    )
    da.add_artist(suffix)

    # Ancorar no canto do ax via AnchoredOffsetbox
    box = AnchoredOffsetbox(
        loc=location,
        child=da,
        frameon=True,
        pad=0.45,
        borderpad=borderpad,
    )
    box.patch.set_facecolor("white")
    box.patch.set_edgecolor("0.35")
    box.patch.set_linewidth(0.6)
    box.patch.set_alpha(0.92)
    ax.add_artist(box)
