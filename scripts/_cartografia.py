"""_cartografia.py — helpers cartograficos compartilhados para os mapas da dissertacao.

Padroniza:
    - adicionar_norte(ax): rosa-dos-ventos Mariners de 16 pontas
      (4 cardinais bipartidos preto/branco + 4 colaterais bipartidos +
      8 secundarias finas pretas), sem caixa de fundo, com 'N' acima.
      Ancorada via AnchoredOffsetbox; default loc='upper left' (canto NW
      do mapa, que tipicamente fica vazio em GO/Brasil).

    - adicionar_escala(ax, dx): regua minimalista em pixels (linha
      horizontal + 3 ticks + numeros em km + sufixo 'km'), sem caixa
      de fundo, com path_effects de stroke branco para legibilidade
      sobre raster. Default loc='lower left' com leve deslocamento
      para FORA do canto SW (consistente com a legenda).

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

Para legendas, recomenda-se borderaxespad=-1.2 em ax.legend(loc='lower right')
para empurrar a caixa levemente para fora do canto SE (gap consistente com
escala e norte).
"""
from __future__ import annotations

import math

import matplotlib.patheffects as pe
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea
from matplotlib.patches import Circle, Polygon
from matplotlib.text import Text


# ============================================================
# Helpers internos
# ============================================================
def _stroke_white(linewidth: float = 2.5):
    """Path effect: contorno branco para texto/linhas legiveis sobre raster."""
    return [pe.withStroke(linewidth=linewidth, foreground="white")]


def _anchor(ax: Axes, da: DrawingArea, loc: str, borderpad: float) -> None:
    """Ancora um DrawingArea num canto do ax, SEM caixa de fundo.
    borderpad negativo empurra para FORA do ax."""
    box = AnchoredOffsetbox(
        loc=loc,
        child=da,
        frameon=False,
        pad=0.0,
        borderpad=borderpad,
    )
    ax.add_artist(box)


def _losango_bipartido(cx, cy, ang_deg, length, width):
    """Retorna 2 Polygons formando um losango bipartido (branco esq, preto dir).
    A ponta aponta para ang_deg; divisao ao longo do eixo central."""
    ang = math.radians(ang_deg)
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    tip = (cx + length * ux, cy + length * uy)
    base = (cx, cy)
    left = (cx + (width / 2) * px, cy + (width / 2) * py)
    right = (cx - (width / 2) * px, cy - (width / 2) * py)
    return [
        Polygon([base, left, tip], facecolor="white",
                edgecolor="black", linewidth=0.7),
        Polygon([base, tip, right], facecolor="black",
                edgecolor="black", linewidth=0.7),
    ]


def _estimar_ax_pixel_width(ax: Axes) -> float:
    fig = ax.figure
    try:
        renderer = fig.canvas.get_renderer()
        bbox = ax.get_window_extent(renderer)
        return float(bbox.width)
    except Exception:
        ax_pos = ax.get_position()
        return float(fig.get_size_inches()[0] * fig.dpi * ax_pos.width)


# Valores "redondos" em km para auto-escolha de comprimento da escala
_NICE_KM = [2, 4, 8, 20, 40, 80, 100, 200, 400, 800, 1000, 2000]


def _pick_total_km(ax: Axes, dx: float, bar_pixel_target: int) -> tuple[float, float]:
    """Retorna (total_km, bar_pixel_w) para uma escala de ~bar_pixel_target px."""
    xlim = ax.get_xlim()
    x_range_data = abs(xlim[1] - xlim[0])
    ax_pixel_width = _estimar_ax_pixel_width(ax) or 800
    metros_por_pixel_ax = (x_range_data * dx) / ax_pixel_width
    metros_alvo = bar_pixel_target * metros_por_pixel_ax
    km_alvo = metros_alvo / 1000.0
    total_km = float(min(_NICE_KM, key=lambda v: abs(v - km_alvo)))
    bar_pixel_w = (total_km * 1000.0) / metros_por_pixel_ax
    return total_km, bar_pixel_w


# ============================================================
# Norte — Rosa-dos-ventos Mariners 16 pontas
# ============================================================
def adicionar_norte(
    ax: Axes,
    location: str = "upper left",
    size: float = 1.0,
    borderpad: float = 0.7,
) -> None:
    """Rosa-dos-ventos cartografica Mariners de 16 pontas, sem caixa de fundo.

    4 cardinais (N/L/S/O) em losangos bipartidos preto/branco grandes,
    4 colaterais (NE/SE/SO/NO) em losangos bipartidos medios,
    8 secundarias em triangulos pretos finos curtos. 'N' acima da ponta norte.

    Parametros:
        location: canto do ax (default 'upper left' — canto NW tipicamente vazio
                  em mapas de GO).
        size: fator de escala (1.0 = ~72 px; 1.3 = 30% maior; 0.8 = 20% menor).
        borderpad: distancia da borda em font-size units. Pode ser negativo para
                   empurrar para fora.
    """
    base_size = 72
    s = int(base_size * size)
    da = DrawingArea(s, s + 14, 0, 0)
    cx = s / 2
    cy = (s + 14) / 2 - 5
    r_card = s * 0.46
    r_col = s * 0.32
    r_sec = s * 0.22
    w_card = s * 0.18
    w_col = s * 0.12

    # 8 secundarias (22.5/67.5/...) — triangulos pretos finos
    for k in range(8):
        ang_deg = 22.5 + k * 45
        ang = math.radians(ang_deg)
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        tip = (cx + r_sec * ux, cy + r_sec * uy)
        w = s * 0.04
        bl = (cx + (w / 2) * px, cy + (w / 2) * py)
        br = (cx - (w / 2) * px, cy - (w / 2) * py)
        da.add_artist(Polygon([bl, tip, br], facecolor="black",
                              edgecolor="black", linewidth=0.4))

    # 4 colaterais (NE/SE/SO/NO) — losangos bipartidos medios
    for ang_deg in (45, -45, -135, 135):
        for poly in _losango_bipartido(cx, cy, ang_deg, r_col, w_col):
            da.add_artist(poly)

    # 4 cardinais (N/L/S/O) — losangos bipartidos grandes
    for ang_deg in (90, 0, -90, 180):
        for poly in _losango_bipartido(cx, cy, ang_deg, r_card, w_card):
            da.add_artist(poly)

    # Circulo central pequeno
    da.add_artist(Circle((cx, cy), 2.8 * size, facecolor="black",
                         edgecolor="black"))

    # N acima da ponta norte
    n_text = Text(cx, cy + r_card + 4, "N", ha="center", va="bottom",
                  fontsize=int(11 * size), fontweight="bold")
    n_text.set_path_effects(_stroke_white(2.5))
    da.add_artist(n_text)

    _anchor(ax, da, location, borderpad=borderpad)


# ============================================================
# Escala — regua minimalista
# ============================================================
def adicionar_escala(
    ax: Axes,
    dx: float = 1.0,
    total_km: float | None = None,
    location: str = "lower left",
    bar_pixel_target: int = 160,
    borderpad: float = -0.5,
) -> None:
    """Regua de escala minimalista: linha horizontal + 3 ticks (0/meio/total) +
    numeros em km + sufixo 'km'. Sem caixa de fundo, com path_effects de stroke
    branco para legibilidade sobre raster.

    Parametros:
        dx: metros por unidade do eixo x.
            - GeoDataFrame em CRS metrico (EPSG:5880): dx=1
            - imshow de raster com axes em pixels: dx = metros_por_pixel
            - Coordenadas geograficas (graus): dx ~= 111000 m/grau
        total_km: comprimento em km. Se None, escolhe automaticamente um valor
                  "redondo" proximo a bar_pixel_target pixels.
        location: canto do ax (default 'lower left').
        bar_pixel_target: largura aproximada desejada da barra em pixels (default 160).
        borderpad: distancia da borda em font-size units (default -0.5 = pouco
                   abaixo do canto SW, gap consistente com a legenda).
    """
    _picked_km, bar_w = _pick_total_km(ax, dx, bar_pixel_target=bar_pixel_target)
    if total_km is None:
        total_km = _picked_km
        # recalcula bar_w para o total_km final
    else:
        # recalcular largura para total_km customizado
        xlim = ax.get_xlim()
        x_range_data = abs(xlim[1] - xlim[0])
        ax_pixel_width = _estimar_ax_pixel_width(ax) or 800
        metros_por_pixel_ax = (x_range_data * dx) / ax_pixel_width
        bar_w = (total_km * 1000.0) / metros_por_pixel_ax

    h_total = 22
    suffix_w = 30
    da = DrawingArea(bar_w + suffix_w, h_total, 0, 0)

    y_bar = 14
    # Linha principal
    line = Line2D([0, bar_w], [y_bar, y_bar], color="black", linewidth=1.6)
    line.set_path_effects(_stroke_white(2.5))
    da.add_artist(line)

    # 3 Ticks (0, meio, fim)
    for frac in (0.0, 0.5, 1.0):
        x = frac * bar_w
        tick = Line2D([x, x], [y_bar - 4, y_bar + 4], color="black", linewidth=1.4)
        tick.set_path_effects(_stroke_white(2.5))
        da.add_artist(tick)

        km_val = frac * total_km
        label = f"{km_val:.0f}" if total_km >= 1 else f"{km_val:g}"
        t = Text(x, y_bar - 6, label, ha="center", va="top",
                 fontsize=8, fontweight="bold")
        t.set_path_effects(_stroke_white(2.5))
        da.add_artist(t)

    # Sufixo "km" a direita
    km_label = Text(bar_w + 4, y_bar, "km", ha="left", va="center",
                    fontsize=8.5, fontweight="bold")
    km_label.set_path_effects(_stroke_white(2.5))
    da.add_artist(km_label)

    _anchor(ax, da, location, borderpad=borderpad)
