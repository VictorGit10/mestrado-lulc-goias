"""gerar_mapas_fogo_40anos.py — 40 mapas coropleticos anuais (1985-2024)
de area queimada por municipio de Goias.

Usa painel unificado para area queimada total por municipio x ano,
aplica escala log (np.log1p) e breaks Jenks globais para comparabilidade.

Saida:
    Visualizacao/img/mapas_fogo/fogo_{ANO}.webp  (40 arquivos)
    Tambem salva PNGs intermediarios em Visualizacao/img/mapas_fogo/
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
from matplotlib.colors import Normalize
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
OUT_DIR = ROOT / "Visualizacao" / "img" / "mapas_fogo"


def _fmt_ha(v: float) -> str:
    """Formata valor em ha de forma humana: 100, 2k, 35k, 1.2M."""
    if v < 1000:
        return f"{v:.0f} ha"
    if v < 10000:
        return f"{v / 1000:.1f}k ha".replace(".0k", "k")
    if v < 1_000_000:
        return f"{v / 1000:.0f}k ha"
    return f"{v / 1_000_000:.1f}M ha"


def carregar_malha() -> gpd.GeoDataFrame:
    print("[...] Baixando/carregando malha municipal de Goias (geobr)...")
    gdf = geobr.read_municipality(code_muni="GO", year=2020)
    gdf["code_muni"] = gdf["code_muni"].astype("int64")
    # Reprojetar para EPSG:5880 (Albers Brasil, metrico) — necessario para a
    # barra de escala em metros via adicionar_escala(ax, dx=1).
    gdf = gdf.to_crs(5880)
    return gdf


def gerar_mapas(df: pd.DataFrame, gdf_munis: gpd.GeoDataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Agregar fogo total por municipio x ano
    fogo = df.groupby(["cd_mun", "ano"], as_index=False)["fogo_total_ha"].sum(min_count=1)

    # Calcular breaks Jenks globais sobre log1p de TODOS os valores
    try:
        import jenkspy
        valores_pos = fogo["fogo_total_ha"][fogo["fogo_total_ha"] > 0]
        log_vals = np.log1p(valores_pos)
        breaks_log = jenkspy.jenks_breaks(log_vals.tolist(), n_classes=6)
        print(f"[OK]  Breaks Jenks (log1p): {[f'{b:.2f}' for b in breaks_log]}")
    except ImportError:
        # Fallback: quantiles
        log_vals = np.log1p(fogo["fogo_total_ha"][fogo["fogo_total_ha"] > 0])
        breaks_log = [0] + np.quantile(log_vals, [0.2, 0.4, 0.6, 0.8, 0.95, 1.0]).tolist()
        print(f"[OK]  Breaks Quantile (log1p): {[f'{b:.2f}' for b in breaks_log]}")

    cmap = plt.get_cmap("YlOrRd")
    anos = list(range(ANO_MIN, ANO_MAX + 1))

    # Legenda: 4 niveis amostrados do gradiente continuo + cinza p/ sem fogo.
    # Labels = valor em ha aproximado no centro de cada faixa (inversa do log1p).
    log_max = breaks_log[-1]
    fracs = [0.15, 0.40, 0.65, 0.85]
    ha_at_frac = [float(np.expm1(f * log_max)) for f in fracs]
    handles = [
        Patch(facecolor=cmap(fracs[0]), label=f"~{_fmt_ha(ha_at_frac[0])}"),
        Patch(facecolor=cmap(fracs[1]), label=f"~{_fmt_ha(ha_at_frac[1])}"),
        Patch(facecolor=cmap(fracs[2]), label=f"~{_fmt_ha(ha_at_frac[2])}"),
        Patch(facecolor=cmap(fracs[3]), label=f"~{_fmt_ha(ha_at_frac[3])}"),
        Patch(facecolor="#ececec", label="Sem fogo"),
    ]

    total_in = total_out = 0
    convertidos = 0

    for i, ano in enumerate(anos, start=1):
        fogo_ano = fogo[fogo["ano"] == ano][["cd_mun", "fogo_total_ha"]].copy()
        fogo_ano["log_fogo"] = np.where(
            fogo_ano["fogo_total_ha"] > 0,
            np.log1p(fogo_ano["fogo_total_ha"]),
            0,
        )
        fogo_ano["tem_fogo"] = fogo_ano["fogo_total_ha"] > 0

        gdf_ano = gdf_munis.merge(fogo_ano, left_on="code_muni", right_on="cd_mun", how="left")
        gdf_ano["tem_fogo"] = gdf_ano["tem_fogo"].fillna(False)
        gdf_ano["log_fogo"] = gdf_ano["log_fogo"].fillna(0)

        norm = Normalize(vmin=breaks_log[0], vmax=breaks_log[-1])
        cor_vals = norm(gdf_ano["log_fogo"].values)
        cores = np.where(
            gdf_ano["tem_fogo"].values[:, None],
            cmap(cor_vals),
            [0.925, 0.925, 0.925, 1.0],  # cinza para sem fogo
        )

        fig, ax = plt.subplots(figsize=FIGSIZE)
        gdf_ano.plot(ax=ax, color=cores, edgecolor="none", linewidth=0.2)
        ax.set_title(f"Area Queimada — Goias {ano}", fontsize=14, pad=10)
        ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=8,
                  title="Area queimada (ha)", title_fontsize=8,
                  borderaxespad=-1.2)
        ax.set_axis_off()
        adicionar_escala(ax, dx=1)  # gdf_munis usa CRS metrico apos to_crs(5880)
        adicionar_norte(ax)

        png_path = OUT_DIR / f"fogo_{ano}.png"
        webp_path = OUT_DIR / f"fogo_{ano}.webp"
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
        print(f"  [{i:02d}/40] fogo_{ano}: {size_png/1024:.0f} KB -> {size_webp/1024:.0f} KB ({ratio:.0f}% menor)")

        # Remover PNG intermediario
        png_path.unlink()

    if convertidos:
        ratio = (1 - total_out / total_in) * 100
        print(f"\n{convertidos} arquivos | {total_in/1024/1024:.2f} MB -> "
              f"{total_out/1024/1024:.2f} MB ({ratio:.1f}% menor)")


def main() -> None:
    print("=" * 60)
    print("Gerando 40 mapas coropleticos de fogo — Goias 1985-2024")
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