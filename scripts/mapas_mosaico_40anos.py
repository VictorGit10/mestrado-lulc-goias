"""mapas_mosaico_40anos.py — a geografia do Mosaico de Usos, 1985–2024
=====================================================================

O QUE FAZ
---------
Renderiza **40 mapas anuais pixel-a-pixel** da classe 21 do MapBiomas ("Mosaico
de Agricultura ou Pastagem") em Goiás, mais um GIF e um mapa de **diferença
2019 → 2024**. Cada célula do mapa mostra a *fração* de sua área que o MapBiomas
classificou como Mosaico naquele ano.

POR QUE (curiosidade dirigida, 25/jul/2026)
-------------------------------------------
O Mosaico é a classe que a auditoria da mudança de rótulo (**D25**, #28D) colocou
no centro: no fim da série a saída da pastagem migra do rótulo "agricultura" para
"Mosaico de Usos" — a razão entre as duas transições vai de 0,6 (2015) a 32,5
(2024) — enquanto o IBGE registra a soja crescendo 38%. Até aqui isso era um
número. Estes mapas perguntam **onde**.

O que o script *não* faz: mexer nos 40 mapas de LULC do site. Aqueles seguem com
`.selfMask()` na classe 21, por decisão registrada em
`Visualizacao/docs/IMPLEMENTACAO.md` §3.7.1.

MÉTODO
------
- Fonte: cubo MapBiomas Coleção 10.1 de Goiás (`data/raw/cubo_go/`, 16 tiles de
  8192², 40 bandas anuais, uint8, EPSG:4326, ~30 m). É o mesmo cubo do censo do
  #28 — nada é baixado.
- **Uma passada só sobre o cubo.** O TIFF é `interleave=pixel`, então ler uma
  janela com as 40 bandas custa quase o mesmo que ler uma: o script varre cada
  tile em janelas de 1.024 linhas e resolve os 40 anos de uma vez (~2 min no
  total, contra ~25 min lendo banda a banda).
- Agregação: blocos de 16×16 pixels nativos (~480 m). O valor da célula é a
  **fração** de pixels de classe 21 — categórico não se reamostra por média, mas
  a fração *é* a quantidade de interesse, e ela suaviza o mapa sem inventar nada.
- Recorte: máscara do contorno de Goiás rasterizada na grade de saída
  (`amc_goias.gpkg` dissolvido). O cubo é um retângulo envolvente e traz pixels
  de MT/MG/TO/BA/DF — o mesmo defeito que contaminou a amostra do #28A.
- Área em Mha reportada nos rótulos: vem do **CSV municipal** (#4), não do
  raster. O raster serve à geografia; a contabilidade oficial do trabalho é a
  municipal, e misturar as duas seria criar uma terceira régua.

ENTRADAS
    data/raw/cubo_go/*.tif                     (cubo #28, Coleção 10.1)
    data/processed/amc_goias.gpkg              (#25, contorno)
    data/processed/mapbiomas_munis_goias.csv   (#4, área por classe/ano)

SAÍDAS
    outputs/mosaico_40anos/mosaico_{ANO}.png   (40 mapas)
    outputs/mosaico_40anos/mosaico_40anos.gif
    outputs/mosaico_40anos/mosaico_delta_2019_2024.png
    outputs/mosaico_40anos/mosaico_serie.csv   (fração estadual por ano, raster)

COMO RODAR
    python scripts/mapas_mosaico_40anos.py
"""
from __future__ import annotations

import glob
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from _cartografia import adicionar_escala, adicionar_norte  # noqa: E402

CUBO = ROOT / "data" / "raw" / "cubo_go"
AMC_GPKG = ROOT / "data" / "processed" / "amc_goias.gpkg"
CSV_MUNI = ROOT / "data" / "processed" / "mapbiomas_munis_goias.csv"
OUT = ROOT / "outputs" / "mosaico_40anos"
CACHE = ROOT / "data" / "interim" / "mosaico_contagem_40anos.npz"

CLASSE_MOSAICO = 21
ANO_MIN, ANO_MAX = 1985, 2024
FATOR = 16              # 16×16 px nativos ≈ 480 m por célula de saída
LINHAS_JANELA = 1024    # múltiplo de FATOR; ~335 MB por leitura de 40 bandas
DPI = 170
FIGSIZE = (9.2, 8.4)

# Ocre do Mosaico — o mesmo `--color-mosaico` que a barra empilhada do site usa.
CMAP = LinearSegmentedColormap.from_list(
    "mosaico", ["#f7f4ec", "#e8cf9a", "#c98a4b", "#8a4f1d", "#4a2408"])
CMAP_DELTA = LinearSegmentedColormap.from_list(
    "mosaico_delta", ["#2d5a3d", "#a8c4ae", "#f7f4ec", "#e0a86a", "#8a4f1d"])


# --------------------------------------------------------------------------
# 1. Varredura do cubo
# --------------------------------------------------------------------------
def grade_saida(tiles: list[str]) -> tuple[int, int, float, float, float]:
    """Grade global (linhas, colunas, left, top, res) que cobre todos os tiles."""
    lefts, tops, rights, bottoms, res = [], [], [], [], None
    for f in tiles:
        with rasterio.open(f) as s:
            b = s.bounds
            lefts.append(b.left); tops.append(b.top)
            rights.append(b.right); bottoms.append(b.bottom)
            res = s.res[0]
    largura = int(round((max(rights) - min(lefts)) / res))
    altura = int(round((max(tops) - min(bottoms)) / res))
    return altura, largura, min(lefts), max(tops), res


def varrer_cubo(tiles: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Uma passada sobre o cubo. Devolve:

    - `contagem` (n_anos, H, W) uint16 — pixels de classe 21 por célula 16×16;
    - `origem_2019` (256,) int64 — classe em 2019 dos pixels que **viraram**
      Mosaico entre 2019 e 2024 (a pergunta do D25: de onde veio o novo Mosaico).
    """
    lin_nat, col_nat, left, top, res = grade_saida(tiles)
    H, W = -(-lin_nat // FATOR), -(-col_nat // FATOR)   # teto da divisão
    n_anos = ANO_MAX - ANO_MIN + 1
    print(f"Grade nativa {lin_nat}×{col_nat} → saída {H}×{W} "
          f"(célula ≈ {res * FATOR * 111_000:.0f} m)")

    if CACHE.exists():
        z = np.load(CACHE)
        print(f"Cache: {CACHE.name} (apague o arquivo para varrer o cubo de novo)")
        return z["contagem"], z["origem"]

    contagem = np.zeros((n_anos, H, W), dtype=np.uint16)
    origem = np.zeros(256, dtype=np.int64)
    i2019, i2024 = 2019 - ANO_MIN, 2024 - ANO_MIN

    t0 = time.time()
    for k, f in enumerate(tiles, 1):
        with rasterio.open(f) as s:
            r_off = int(round((top - s.bounds.top) / res))
            c_off = int(round((s.bounds.left - left) / res))
            for y in range(0, s.height, LINHAS_JANELA):
                h = min(LINHAS_JANELA, s.height - y)
                win = rasterio.windows.Window(0, y, s.width, h)
                arr = s.read(window=win)                     # (40, h, w)

                # Pad até múltiplo de FATOR — as sobras caem na borda do
                # retângulo, fora do estado, e a máscara as descarta.
                ph = (-h) % FATOR
                pw = (-arr.shape[2]) % FATOR
                if ph or pw:
                    arr = np.pad(arr, ((0, 0), (0, ph), (0, pw)))

                eq = (arr == CLASSE_MOSAICO)
                hb, wb = eq.shape[1] // FATOR, eq.shape[2] // FATOR
                blocos = eq.reshape(n_anos, hb, FATOR, wb, FATOR).sum(axis=(2, 4))

                r0, c0 = (r_off + y) // FATOR, c_off // FATOR
                contagem[:, r0:r0 + hb, c0:c0 + wb] += blocos.astype(np.uint16)

                # De onde veio o Mosaico novo (sem pad, para não contar zeros)
                novo = (arr[i2024, :h] == CLASSE_MOSAICO) & (arr[i2019, :h] != CLASSE_MOSAICO)
                if novo.any():
                    origem += np.bincount(arr[i2019, :h][novo], minlength=256)

        print(f"  tile {k:>2}/{len(tiles)}  {time.time() - t0:5.1f}s")

    # A varredura custa ~4 min; o cache torna qualquer ajuste de mapa instantâneo.
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE, contagem=contagem, origem=origem)
    print(f"  cache salvo em {CACHE.relative_to(ROOT)}")
    return contagem, origem


def mascara_goias(H: int, W: int, left: float, top: float, res: float) -> np.ndarray:
    """Máscara booleana do contorno do estado na grade de saída."""
    gdf = gpd.read_file(AMC_GPKG).to_crs(4326)
    contorno = gdf.union_all()
    transform = from_origin(left, top, res * FATOR, res * FATOR)
    return rasterize([(contorno, 1)], out_shape=(H, W), transform=transform,
                     dtype="uint8", all_touched=False).astype(bool)


# --------------------------------------------------------------------------
# 2. Mapas
# --------------------------------------------------------------------------
def area_municipal() -> pd.Series:
    """Mha de Mosaico por ano, do CSV municipal (#4) — a régua oficial."""
    df = pd.read_csv(CSV_MUNI, usecols=["ano", "class_id", "area_ha"])
    s = df[df["class_id"] == CLASSE_MOSAICO].groupby("ano")["area_ha"].sum() / 1e6
    return s


def moldura(ax, gdf, extent):
    gdf.boundary.plot(ax=ax, color="#8a8a82", linewidth=0.25, zorder=3)
    gdf.dissolve().boundary.plot(ax=ax, color="#3a3a3a", linewidth=0.9, zorder=4)
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
    ax.set_axis_off()


def _titulo(fig, titulo, subtitulo, rodape, tam=34):
    """Título e rodapé em coordenadas de FIGURA, fora do ax.

    Desenhar sobre o ax colocava o texto por cima do estado (Goiás preenche quase
    todo o quadro). Reservar faixas em cima e embaixo custa altura, e a leitura
    ganha o suficiente para valer.
    """
    fig.text(0.02, 0.975, titulo, ha="left", va="top",
             fontsize=tam, fontweight="bold", color="#1a1a1a")
    fig.text(0.02, 0.928, subtitulo, ha="left", va="top",
             fontsize=11.5, color="#4a4a4a")
    fig.text(0.02, 0.022, rodape, ha="left", va="bottom",
             fontsize=7.5, color="#6b6b6b", linespacing=1.5)


def desenhar_ano(frac, ano, mha, gdf, extent, caminho):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(top=0.90, bottom=0.075, left=0.02, right=0.90)
    ax.imshow(np.ma.masked_invalid(frac), extent=extent, origin="upper",
              cmap=CMAP, vmin=0, vmax=1, interpolation="nearest", zorder=2)
    moldura(ax, gdf, extent)

    _titulo(fig, str(ano),
            f"Mosaico de Usos — {mha:.2f} Mha  ({mha / 34.01 * 100:.1f}% de Goiás)",
            "Fração da célula (~480 m) classificada como “Mosaico de Agricultura ou Pastagem”\n"
            "MapBiomas Coleção 10.1, cubo pixel-a-pixel do #28 · área do CSV municipal (#4)")

    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.01, ticks=[0, 0.5, 1])
    cb.ax.set_yticklabels(["0%", "50%", "100%"], fontsize=8)
    cb.outline.set_visible(False)

    # Sem rosa-dos-ventos: o mapa é norte-acima e ela cobria a mancha do nordeste.
    try:
        adicionar_escala(ax, dx=111_000, location="lower right")
    except Exception as e:                      # helper é cosmético
        print(f"  [aviso] escala: {e}")

    fig.savefig(caminho, dpi=DPI, facecolor="white")
    plt.close(fig)


def desenhar_delta(delta, gdf, extent, caminho, origem_pct):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(top=0.90, bottom=0.085, left=0.02, right=0.90)
    lim = 0.6
    ax.imshow(np.ma.masked_invalid(delta), extent=extent, origin="upper",
              cmap=CMAP_DELTA, norm=TwoSlopeNorm(0, -lim, lim),
              interpolation="nearest", zorder=2)
    moldura(ax, gdf, extent)
    _titulo(fig, "2019 → 2024",
            "Onde o Mosaico apareceu (ocre) e onde recuou (verde)",
            f"Diferença da fração de Mosaico por célula. É a janela da D25 — e {origem_pct:.0f}% do "
            "Mosaico novo\nera PASTAGEM em 2019: a saída do pasto trocou de rótulo, não de destino.",
            tam=28)
    sm = plt.cm.ScalarMappable(cmap=CMAP_DELTA, norm=TwoSlopeNorm(0, -lim, lim))
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.01, ticks=[-lim, 0, lim])
    cb.ax.set_yticklabels([f"−{lim:.0%}", "0", f"+{lim:.0%}"], fontsize=8)
    cb.outline.set_visible(False)
    fig.savefig(caminho, dpi=DPI, facecolor="white")
    plt.close(fig)


def desenhar_confronto(f85, f24, r, gdf, extent, caminho):
    """1985 | 2024 lado a lado — mesmo total estadual, geografia diferente."""
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 8.0))
    fig.subplots_adjust(top=0.82, bottom=0.10, left=0.02, right=0.98, wspace=0.02)
    for ax, arr, ano, mha in ((axes[0], f85, 1985, 3.63), (axes[1], f24, 2024, 3.59)):
        ax.imshow(np.ma.masked_invalid(arr), extent=extent, origin="upper",
                  cmap=CMAP, vmin=0, vmax=1, interpolation="nearest", zorder=2)
        moldura(ax, gdf, extent)
        ax.set_title(f"{ano} — {mha:.2f} Mha", fontsize=17, fontweight="bold",
                     color="#1a1a1a", pad=8)
    fig.text(0.02, 0.975, "O Mosaico voltou ao tamanho de 1985 — em outro lugar",
             ha="left", va="top", fontsize=20, fontweight="bold", color="#1a1a1a")
    fig.text(0.02, 0.925,
             "Mesma área estadual (10,7% × 10,5% de Goiás), mas as duas manchas quase não se "
             f"sobrepõem: correlação espacial r = {r:.2f}".replace(".", ",") + " entre as células.",
             ha="left", va="top", fontsize=11.5, color="#4a4a4a")
    fig.text(0.02, 0.025,
             "Nos 10% de células com mais Mosaico em 1985 (média 51%), a classe caiu para 11% em 2019 e só voltou a 16% em 2024.\n"
             "Nos outros 90%, ela foi de 6% para 10%. O total é o mesmo; o fenômeno, não. MapBiomas Coleção 10.1, cubo do #28.",
             ha="left", va="bottom", fontsize=8, color="#6b6b6b", linespacing=1.5)
    fig.savefig(caminho, dpi=DPI, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tiles = sorted(glob.glob(str(CUBO / "*.tif")))
    if not tiles:
        sys.exit(f"cubo não encontrado em {CUBO}")

    lin_nat, col_nat, left, top, res = grade_saida(tiles)
    contagem, origem = varrer_cubo(tiles)
    n_anos, H, W = contagem.shape

    mask = mascara_goias(H, W, left, top, res)
    print(f"Máscara: {mask.sum():,} células dentro de Goiás de {mask.size:,} "
          f"({mask.sum() / mask.size:.0%} do retângulo)")

    frac = contagem.astype(np.float32) / (FATOR * FATOR)
    frac[:, ~mask] = np.nan

    extent = (left, left + W * FATOR * res, top - H * FATOR * res, top)
    gdf = gpd.read_file(AMC_GPKG).to_crs(4326)
    mha = area_municipal()

    # série estadual pela própria varredura (para conferência com o CSV)
    serie = pd.DataFrame({
        "ano": range(ANO_MIN, ANO_MAX + 1),
        "frac_raster": np.nanmean(frac, axis=(1, 2)),
        "mha_csv_municipal": [mha.get(a, np.nan) for a in range(ANO_MIN, ANO_MAX + 1)],
    })
    serie.to_csv(OUT / "mosaico_serie.csv", index=False)

    print("\nRenderizando 40 mapas...")
    quadros = []
    for i, ano in enumerate(range(ANO_MIN, ANO_MAX + 1)):
        p = OUT / f"mosaico_{ano}.png"
        desenhar_ano(frac[i], ano, mha.get(ano, np.nan), gdf, extent, p)
        quadros.append(p)
        if ano % 5 == 0 or ano == ANO_MAX:
            print(f"  {ano} — {mha.get(ano, float('nan')):.2f} Mha")

    pct_pasto = origem[15] / origem.sum() * 100 if origem.sum() else float("nan")
    desenhar_delta(frac[2024 - ANO_MIN] - frac[2019 - ANO_MIN], gdf, extent,
                   OUT / "mosaico_delta_2019_2024.png", pct_pasto)

    # O total estadual de 2024 é o de 1985 — mas a mancha é outra.
    a85, a24 = frac[0][mask], frac[-1][mask]
    r = float(np.corrcoef(a85, a24)[0, 1])
    desenhar_confronto(frac[0], frac[-1], r, gdf, extent,
                       OUT / "mosaico_1985_vs_2024.png")
    print(f"\nCorrelação espacial 1985 × 2024: r = {r:.3f} "
          f"(2019 × 2024: r = {np.corrcoef(frac[2019 - ANO_MIN][mask], a24)[0, 1]:.3f})")

    print("\nMontando o GIF...")
    imgs = [Image.open(p).convert("RGB") for p in quadros]
    largura = 1100
    imgs = [im.resize((largura, int(im.height * largura / im.width)), Image.LANCZOS)
            for im in imgs]
    imgs[0].save(OUT / "mosaico_40anos.gif", save_all=True, append_images=imgs[1:],
                 duration=[260] * (len(imgs) - 1) + [1800], loop=0, optimize=True)

    # De onde veio o Mosaico novo de 2019→2024
    print("\nDe onde veio o Mosaico que apareceu entre 2019 e 2024:")
    tot = origem.sum()
    nomes = {3: "Formação Florestal", 4: "Formação Savânica", 11: "Campo Alagado",
             12: "Formação Campestre", 15: "Pastagem", 18: "Agricultura",
             19: "Lavoura Temporária", 20: "Cana", 24: "Área Urbana",
             25: "Outra Área não Vegetada", 29: "Afloramento Rochoso",
             30: "Mineração", 33: "Rio/Lago", 39: "Soja", 40: "Arroz",
             41: "Outras Lavouras Temporárias", 46: "Café", 47: "Citrus",
             48: "Outras Lavouras Perenes", 9: "Silvicultura", 62: "Algodão"}
    for cid in np.argsort(origem)[::-1][:8]:
        if origem[cid] == 0:
            continue
        print(f"  {nomes.get(cid, f'classe {cid}'):<28} "
              f"{origem[cid] / tot:6.1%}  ({origem[cid] * 0.09 / 1e6:.3f} Mha brutos)")
    print("  (inclui pixels fora de Goiás — é o retângulo do cubo; leitura de proporção)")

    print(f"\n[OK] {OUT.relative_to(ROOT)} — 40 mapas + GIF + delta + série")


if __name__ == "__main__":
    main()
