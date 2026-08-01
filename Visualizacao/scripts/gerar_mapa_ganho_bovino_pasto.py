"""gerar_mapa_ganho_bovino_pasto.py — mapa coropletico duplo do GANHO do rebanho
bovino (cabeças) e da pastagem (ha) por AMC de Goias, 1985 -> 2024.

Dois painéis lado a lado (small multiples — duas grandezas, eixos proprios,
nunca eixo duplo), colormap divergente RdBu_r centrado em 0 (vermelho = retração,
azul = expansão) e TwoSlopeNorm, seguindo o estilo de gerar_mapas_delta_lulc.py.

D11: AMC = unidade canonica para analises longitudinais.

Periodo e modo sao parametrizaveis (constantes abaixo):
    MODO='abs'  -> Δ = X[ANO_FIM] - X[ANO_INI]        (cabeças / ha, bruto)
    MODO='pct'  -> Δ% = (X[ANO_FIM]/X[ANO_INI] - 1)*100 (relativo, livre de area-bias)

Saida:
    Visualizacao/img/mapas_rebanho/ganho_bovino_pasto_{INI}_{FIM}_{modo}.png

Caveat (area-bias): o modo 'abs' reflete tambem o tamanho da AMC. Para comparacao
cross-sectional livre desse vies use MODO='pct'. O sinal de intensificacao
marginal (Δcab/Δpasto_ha) fica em stdout, nao no mapa.
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

# ===== Configuracao =====
DPI = 200
FIGSIZE = (16, 8)
ANO_INI, ANO_FIM = 1985, 2024
MODO = "abs"  # 'abs' | 'pct'
QUALITY_WEBP = 85

PAINEL = ROOT / "data" / "processed" / "painel_amc_goias.parquet"
AMC_GPKG = ROOT / "data" / "processed" / "amc_goias.gpkg"
OUT_DIR = ROOT / "Visualizacao" / "img" / "mapas_rebanho"


def carregar_malha() -> gpd.GeoDataFrame:
    print("[...] Carregando malha AMC de Goias (amc_goias.gpkg)...")
    gdf = gpd.read_file(AMC_GPKG)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    gdf = gdf.to_crs(5880)  # Albers Brasil -> barra de escala em metros
    return gdf


def delta_amc(df: pd.DataFrame, col: str, modo: str) -> pd.DataFrame:
    """Retorna DataFrame {code_amc, delta} com Δ (abs ou pct) entre ANO_FIM e ANO_INI."""
    ini = df[df["ano"] == ANO_INI][["code_amc", col]].rename(columns={col: "v_ini"})
    fim = df[df["ano"] == ANO_FIM][["code_amc", col]].rename(columns={col: "v_fim"})
    d = ini.merge(fim, on="code_amc", how="outer")
    if modo == "pct":
        # Livre de area-bias. Base 0 -> NaN (evita divisao por zero / % infinito).
        d["delta"] = np.where(
            d["v_ini"].fillna(0) > 0,
            (d["v_fim"] / d["v_ini"] - 1.0) * 100.0,
            np.nan,
        )
    else:
        d["delta"] = d["v_fim"] - d["v_ini"]
    return d[["code_amc", "delta"]]


def painel(ax, gdf_amcs, gdf_valor, vmax, unidade, titulo):
    """Plota um painel coropletico divergente centrado em 0."""
    g = gdf_amcs.merge(gdf_valor, on="code_amc", how="left")
    g["delta"] = g["delta"].fillna(0)  # AMCs sem dado -> neutro (0)

    cmap = plt.get_cmap("RdBu_r")
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cores = cmap(norm(g["delta"].values))

    g.plot(ax=ax, color=cores, edgecolor="none", linewidth=0.2)
    ax.set_title(titulo, fontsize=13, pad=8)
    ax.set_axis_off()

    # Mesmo enquadramento em ambos os paineis
    bounds = gdf_amcs.total_bounds
    xmargin = (bounds[2] - bounds[0]) * 0.02
    ymargin = (bounds[3] - bounds[1]) * 0.02
    ax.set_xlim(bounds[0] - xmargin, bounds[2] + xmargin)
    ax.set_ylim(bounds[1] - ymargin, bounds[3] + ymargin)

    adicionar_escala(ax, dx=1, total_km=150)
    adicionar_norte(ax)

    # Colorbar continua
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.02, shrink=0.78)
    cbar.set_label(unidade, fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    return g


def main() -> None:
    print("=" * 64)
    print(f"Ganho rebanho bovino x pastagem por AMC — Goias {ANO_INI}->{ANO_FIM} ({MODO})")
    print("=" * 64)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[...] Lendo {PAINEL.name}...")
    df = pd.read_parquet(PAINEL)
    print(f"[OK]  {len(df)} linhas, {df['code_amc'].nunique()} AMCs")

    gdf_amcs = carregar_malha()
    print(f"[OK]  Malha: {len(gdf_amcs)} AMCs, CRS {gdf_amcs.crs}")

    d_reb = delta_amc(df, "pec_bovinos_cab", MODO)
    d_pas = delta_amc(df, "lulc_pastagem_ha", MODO)

    # vmax simetrico por painel (centrado em 0)
    vmax_reb = np.nanmax(np.abs(d_reb["delta"]))
    vmax_pas = np.nanmax(np.abs(d_pas["delta"]))
    if MODO == "abs":
        vmax_reb = np.ceil(vmax_reb / 50_000) * 50_000
        vmax_pas = np.ceil(vmax_pas / 50_000) * 50_000
    else:
        vmax_reb = np.ceil(vmax_reb / 100) * 100
        vmax_pas = np.ceil(vmax_pas / 100) * 100

    unid = "Δ cabeças" if MODO == "abs" else "Δ %"
    print(f"[OK]  Rebanho: [{d_reb['delta'].min():.0f}, {d_reb['delta'].max():.0f}] {unid}, vmax={vmax_reb:.0f}")
    print(f"[OK]  Pastagem: [{d_pas['delta'].min():.0f}, {d_pas['delta'].max():.0f}] {unid}, vmax={vmax_pas:.0f}")

    # --- Sinal de intensificacao marginal (Δcab / Δpasto_ha), so modo abs ---
    if MODO == "abs":
        m = d_reb.merge(d_pas, on="code_amc", suffixes=("_reb", "_pas"))
        m = m[(m["delta_pas"] > 0) & m["delta_reb"].notna()]
        m["cab_por_ha_novo"] = m["delta_reb"] / m["delta_pas"]
        print("\n[intensificacao marginal] Δcab / Δpasto_ha (AMCs c/ ganho de pasto):")
        print(f"  mediana = {m['cab_por_ha_novo'].median():.3f} cab/ha, "
              f"P10={m['cab_por_ha_novo'].quantile(.10):.3f}, "
              f"P90={m['cab_por_ha_novo'].quantile(.90):.3f}, n={len(m)}")
        print("  (alto = intensificacao: muito boi novo por ha de pasto novo; "
              "baixo = extensificacao: boi novo segue pasto novo 1:1)")

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE)
    sufixo_unid = "cabeças" if MODO == "abs" else "%"
    painel(axes[0], gdf_amcs, d_reb, vmax_reb, f"Δ rebanho ({sufixo_unid})",
           f"A) Ganho do rebanho bovino — {sufixo_unid}")
    painel(axes[1], gdf_amcs, d_pas, vmax_pas, f"Δ pastagem ({sufixo_unid})",
           f"B) Ganho da pastagem — {sufixo_unid}")

    fig.suptitle(
        f"Ganho do rebanho bovino e da pastagem por AMC — Goiás {ANO_INI}→{ANO_FIM}",
        fontsize=15, y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    out = OUT_DIR / f"ganho_bovino_pasto_{ANO_INI}_{ANO_FIM}_{MODO}.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[OK]  Mapa salvo: {out}")
    print(f"      Tamanho: {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()