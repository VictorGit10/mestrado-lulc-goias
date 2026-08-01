"""gerar_mapa_ganho_bovino_pasto_veg.py — mapa coropletico triplo do GANHO (1985->2024)
por AMC de Goias:
    A) Rebanho bovino (cabeças)
    B) Pastagem (ha)
    C) Vegetaçao nativa (floresta + savanica + campo nativo, ha)

E um inseto com scatter Δrebanho x area da AMC para destacar o vies de tamanho
(Nova Crixas é uma AMC muito grande; o ganho absoluto reflete area).

Colormap divergente RdBu_r centrado em 0, estilo gerar_mapas_delta_lulc.py.

Saida:
    Visualizacao/img/mapas_rebanho/ganho_bovino_pasto_veg_{INI}_{FIM}.png

Caveat: 'abs' reflete tamanho da AMC. Para comparacao cross-sectional livre do vies
use a versao percentual (gerar_mapa_ganho_bovino_pasto.py com MODO='pct').
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
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _cartografia import adicionar_norte, adicionar_escala  # noqa: E402

# ===== Configuraçao =====
DPI = 200
FIGSIZE = (18, 8)
ANO_INI, ANO_FIM = 1985, 2024

PAINEL = ROOT / "data" / "processed" / "painel_amc_goias.parquet"
AMC_GPKG = ROOT / "data" / "processed" / "amc_goias.gpkg"
OUT_DIR = ROOT / "Visualizacao" / "img" / "mapas_rebanho"

COL_NATIVA = ["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha", "lulc_campo_nativo_ha"]


def carregar_malha() -> gpd.GeoDataFrame:
    print("[...] Carregando malha AMC de Goias (amc_goias.gpkg)...")
    gdf = gpd.read_file(AMC_GPKG)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    gdf = gdf.to_crs(5880)
    gdf["area_ha"] = gdf.geometry.area / 1e4
    return gdf


def delta_amc(df: pd.DataFrame, col: str) -> pd.DataFrame:
    ini = df[df["ano"] == ANO_INI][["code_amc", col]].rename(columns={col: "v_ini"})
    fim = df[df["ano"] == ANO_FIM][["code_amc", col]].rename(columns={col: "v_fim"})
    d = ini.merge(fim, on="code_amc", how="outer")
    d["delta"] = d["v_fim"] - d["v_ini"]
    return d[["code_amc", "delta"]]


def painel_mapa(ax, gdf_amcs, gdf_valor, vmax, unidade, titulo, bounds):
    g = gdf_amcs.merge(gdf_valor, on="code_amc", how="left")
    g["delta"] = g["delta"].fillna(0)

    cmap = plt.get_cmap("RdBu_r")
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cores = cmap(norm(g["delta"].values))

    g.plot(ax=ax, color=cores, edgecolor="none", linewidth=0.2)
    ax.set_title(titulo, fontsize=12, pad=8)
    ax.set_axis_off()

    xmargin = (bounds[2] - bounds[0]) * 0.02
    ymargin = (bounds[3] - bounds[1]) * 0.02
    ax.set_xlim(bounds[0] - xmargin, bounds[2] + xmargin)
    ax.set_ylim(bounds[1] - ymargin, bounds[3] + ymargin)

    adicionar_escala(ax, dx=1, total_km=150)
    adicionar_norte(ax)

    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.02, shrink=0.72)
    cbar.set_label(unidade, fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    return g


def main() -> None:
    print("=" * 72)
    print(f"Ganho rebanho x pastagem x vegetaçao nativa por AMC — Goias {ANO_INI}->{ANO_FIM}")
    print("=" * 72)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[...] Lendo {PAINEL.name}...")
    df = pd.read_parquet(PAINEL)
    print(f"[OK]  {len(df)} linhas, {df['code_amc'].nunique()} AMCs")

    gdf_amcs = carregar_malha()
    print(f"[OK]  Malha: {len(gdf_amcs)} AMCs, CRS {gdf_amcs.crs}, area total = {gdf_amcs['area_ha'].sum()/1e6:.2f} milhoes ha")

    d_reb = delta_amc(df, "pec_bovinos_cab")
    d_pas = delta_amc(df, "lulc_pastagem_ha")
    df["veg_nativa_ha"] = df[COL_NATIVA].sum(axis=1, skipna=True)
    d_veg = delta_amc(df, "veg_nativa_ha")

    vmax_reb = np.ceil(np.nanmax(np.abs(d_reb["delta"])) / 50_000) * 50_000
    vmax_pas = np.ceil(np.nanmax(np.abs(d_pas["delta"])) / 50_000) * 50_000
    vmax_veg = np.ceil(np.nanmax(np.abs(d_veg["delta"])) / 50_000) * 50_000

    print(f"[OK]  Rebanho: [{d_reb['delta'].min():.0f}, {d_reb['delta'].max():.0f}] cabeças, vmax={vmax_reb:.0f}")
    print(f"[OK]  Pastagem: [{d_pas['delta'].min():.0f}, {d_pas['delta'].max():.0f}] ha, vmax={vmax_pas:.0f}")
    print(f"[OK]  Veg. nativa: [{d_veg['delta'].min():.0f}, {d_veg['delta'].max():.0f}] ha, vmax={vmax_veg:.0f}")

    bounds = gdf_amcs.total_bounds

    fig = plt.figure(figsize=FIGSIZE)
    gs = fig.add_gridspec(2, 3, height_ratios=[3.5, 1], hspace=0.28, wspace=0.22)

    ax_reb = fig.add_subplot(gs[0, 0])
    ax_pas = fig.add_subplot(gs[0, 1])
    ax_veg = fig.add_subplot(gs[0, 2])
    ax_inset = fig.add_subplot(gs[1, :])

    painel_mapa(ax_reb, gdf_amcs, d_reb, vmax_reb, "Δ cabeças",
                "A) Ganho do rebanho bovino", bounds)
    painel_mapa(ax_pas, gdf_amcs, d_pas, vmax_pas, "Δ ha",
                "B) Ganho da pastagem", bounds)
    painel_mapa(ax_veg, gdf_amcs, d_veg, vmax_veg, "Δ ha",
                "C) Ganho/perda de vegetaçao nativa", bounds)

    # Inseto: scatter area x delta rebanho, com destaque para Nova Crixas
    m = gdf_amcs[["code_amc", "area_ha"]].merge(d_reb, on="code_amc", how="left")
    ax_inset.scatter(m["area_ha"], m["delta"], alpha=0.55, s=35, edgecolor="none", color="#444444", label="AMCs")
    outlier = m.nlargest(1, "delta").iloc[0]
    ax_inset.scatter(outlier["area_ha"], outlier["delta"], color="#d62728", s=120, zorder=5)
    ax_inset.annotate(
        f"Nova Crixas\n({outlier['delta']:,.0f} cab, {outlier['area_ha']/1e6:.2f} Mha)",
        xy=(outlier["area_ha"], outlier["delta"]),
        xytext=(outlier["area_ha"] * 0.35, outlier["delta"] * 0.85),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )
    ax_inset.set_xlabel("Area da AMC (ha)", fontsize=10)
    ax_inset.set_ylabel("Δ rebanho 1985->2024 (cab)", fontsize=10)
    ax_inset.set_title("D) Vies de tamanho: ganho absoluto de rebanho vs. area da AMC", fontsize=11, loc="left")
    ax_inset.axhline(0, color="black", linewidth=0.6, linestyle="--")
    ax_inset.ticklabel_format(style="plain", axis="both")
    ax_inset.grid(True, alpha=0.3)

    fig.suptitle(
        f"Ganho do rebanho, da pastagem e da vegetaçao nativa por AMC — Goias {ANO_INI}->{ANO_FIM}",
        fontsize=14, y=0.98,
    )

    out = OUT_DIR / f"ganho_bovino_pasto_veg_{ANO_INI}_{ANO_FIM}_abs.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[OK]  Mapa salvo: {out}")
    print(f"      Tamanho: {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
