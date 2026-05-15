"""gerar_mapas_delta_lulc.py — 40 mapas coropleticos anuais (1985-2024)
de delta % pastagem vs. 1985 por municipio de Goias.

Usa painel unificado para pct_pastagem_lulc por municipio x ano,
calcula delta = pct_pastagem[ano] - pct_pastagem[1985] e plota
mapa diverging (RdBu_r) centrado em 0.

Saida:
    Visualizacao/img/mapas_delta/delta_{ANO}.webp  (40 arquivos)
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import geopandas as gpd
import geobr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _cartografia import adicionar_norte, adicionar_escala  # noqa: E402

# ===== Configuracao =====
DPI = 200
FIGSIZE = (10, 8)
ANO_MIN, ANO_MAX = 1985, 2024
QUALITY_WEBP = 85

PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
OUT_DIR = ROOT / "Visualizacao" / "img" / "mapas_delta"


def carregar_malha() -> gpd.GeoDataFrame:
    print("[...] Baixando/carregando malha municipal de Goias (geobr)...")
    gdf = geobr.read_municipality(code_muni="GO", year=2020)
    gdf["code_muni"] = gdf["code_muni"].astype("int64")
    # Reprojetar para EPSG:5880 (Albers Brasil) para a barra de escala em metros.
    gdf = gdf.to_crs(5880)
    return gdf


def gerar_mapas(df: pd.DataFrame, gdf_munis: gpd.GeoDataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Calcular pct_pastagem se nao existir
    if "pct_pastagem_lulc" in df.columns:
        pct_col = "pct_pastagem_lulc"
    else:
        df["pct_pastagem"] = df["lulc_pastagem_ha"] / df["lulc_area_total_ha"] * 100
        pct_col = "pct_pastagem"

    # Baseline: pct_pastagem em 1985
    baseline = df[df["ano"] == 1985][["cd_mun", pct_col]].rename(
        columns={pct_col: "pct_baseline"}
    )

    # Calcular delta para cada municipio x ano
    delta = df[["cd_mun", "ano", pct_col]].merge(baseline, on="cd_mun", how="left")
    delta["delta_pct"] = delta[pct_col] - delta["pct_baseline"]

    # Limites globais para o colormap (centrado em 0)
    max_abs = delta["delta_pct"].abs().max()
    vmax = np.ceil(max_abs / 5) * 5  # Arredondar para multiplo de 5
    print(f"[OK]  Delta range: [{delta['delta_pct'].min():.1f}, {delta['delta_pct'].max():.1f}] pp, vmax={vmax:.0f}")

    cmap = plt.get_cmap("RdBu_r")
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

    anos = list(range(ANO_MIN, ANO_MAX + 1))

    # Cor central do TwoSlopeNorm em RdBu_r e branco-acinzentado proximo a 0.5.
    handles = [
        Patch(facecolor=cmap(0.0),  label=f"-{vmax:.0f} pp (retracao forte)"),
        Patch(facecolor=cmap(0.25), label=f"-{vmax/2:.0f} pp (retracao)"),
        Patch(facecolor=cmap(0.5),  label="~0 pp (sem mudanca)"),
        Patch(facecolor=cmap(0.75), label=f"+{vmax/2:.0f} pp (expansao)"),
        Patch(facecolor=cmap(1.0),  label=f"+{vmax:.0f} pp (expansao forte)"),
    ]

    total_in = total_out = 0
    convertidos = 0

    for i, ano in enumerate(anos, start=1):
        delta_ano = delta[delta["ano"] == ano][["cd_mun", "delta_pct"]].copy()
        gdf_ano = gdf_munis.merge(delta_ano, left_on="code_muni", right_on="cd_mun", how="left")
        gdf_ano["delta_pct"] = gdf_ano["delta_pct"].fillna(0)

        # 1985 deve ser neutro (delta = 0)
        cores = cmap(norm(gdf_ano["delta_pct"].values))

        fig, ax = plt.subplots(figsize=FIGSIZE)
        gdf_ano.plot(ax=ax, color=cores, edgecolor="none", linewidth=0.2)
        subtitulo = "referencia" if ano == 1985 else "vs. 1985"
        ax.set_title(f"Delta % Pastagem — Goias {ano} ({subtitulo})", fontsize=14, pad=10)
        ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=8,
                  title="Δ pp pastagem vs. 1985", title_fontsize=8)
        ax.set_axis_off()
        adicionar_escala(ax, dx=1)
        adicionar_norte(ax)

        png_path = OUT_DIR / f"delta_{ano}.png"
        webp_path = OUT_DIR / f"delta_{ano}.webp"
        fig.savefig(png_path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)

        # Converter para WebP
        with Image.open(png_path) as img:
            img.save(webp_path, format="WEBP", quality=QUALITY_WEBP, method=6)

        size_png = png_path.stat().st_size
        size_webp = webp_path.stat().st_size
        total_in += size_png
        total_out += size_webp
        convertidos += 1
        ratio = (1 - size_webp / size_png) * 100
        print(f"  [{i:02d}/40] delta_{ano}: {size_png/1024:.0f} KB -> {size_webp/1024:.0f} KB ({ratio:.0f}% menor)")

        # Remover PNG intermediario
        png_path.unlink()

    if convertidos:
        ratio = (1 - total_out / total_in) * 100
        print(f"\n{convertidos} arquivos | {total_in/1024/1024:.2f} MB -> "
              f"{total_out/1024/1024:.2f} MB ({ratio:.1f}% menor)")


def main() -> None:
    print("=" * 60)
    print("Gerando 40 mapas coropleticos delta pastagem — Goias 1985-2024")
    print("=" * 60)

    print(f"[...] Lendo {PAINEL.name}...")
    df = pd.read_parquet(PAINEL)
    print(f"[OK]  {len(df)} linhas, {df['cd_mun'].nunique()} municipios")

    gdf_munis = carregar_malha()
    print(f"[OK]  Malha: {len(gdf_munis)} municipios, CRS {gdf_munis.crs}")

    gerar_mapas(df, gdf_munis)

    print("\n" + "=" * 60)
    print(f"Concluido! WebPs em: {OUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()