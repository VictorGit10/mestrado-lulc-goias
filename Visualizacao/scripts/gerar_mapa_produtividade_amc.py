"""
Mapa espacial de intensificação vs. extensão por AMC.

Painéis:
  A) Δ produtividade da soja (2024 − 1988), t/ha
  B) Δ lotação bovina (2024 − 1985), cab/ha
  C) Δ área plantada de soja por AMC (2024 − 1988), mil ha
  D) Scatter: Δ produtividade × Δ área soja (colorido por Δ lotação)

Uso:
  cd Visualizacao
  python scripts/gerar_mapa_produtividade_amc.py

Saída:
  img/mapas_rebanho/intensificacao_extensao_amc.png
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import MaxNLocator

import sys

# helpers cartográficos
_HERE = Path.cwd() if "__file__" not in globals() else Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parents[1] / "scripts"))
from _cartografia import adicionar_norte, adicionar_escala

REPO_ROOT = _HERE.parents[1]
OUT = REPO_ROOT / "Visualizacao" / "img" / "mapas_rebanho" / "intensificacao_extensao_amc.png"
OUT.parent.mkdir(parents=True, exist_ok=True)


def load() -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    df = pd.read_parquet(REPO_ROOT / "data" / "processed" / "painel_amc_goias.parquet")
    gdf = gpd.read_file(REPO_ROOT / "data" / "processed" / "amc_goias.gpkg")
    gdf = gdf.to_crs(epsg=5880)
    gdf["area_ha"] = gdf.geometry.area / 1e4
    return df, gdf


def compute_deltas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["produtividade_soja_ton_ha"] = df["agri_soja_ton"] / df["agri_soja_ha_plantada"]
    df["lotacao_bov_ha"] = df["pec_bovinos_cab"] / df["lulc_pastagem_ha"]

    # soja: 1988 e 2024
    s88 = df[df["ano"] == 1988][["code_amc", "produtividade_soja_ton_ha", "agri_soja_ha_plantada", "amc_nome_rep"]].rename(
        columns={"produtividade_soja_ton_ha": "prod88", "agri_soja_ha_plantada": "area88"}
    )
    s24 = df[df["ano"] == 2024][["code_amc", "produtividade_soja_ton_ha", "agri_soja_ha_plantada"]].rename(
        columns={"produtividade_soja_ton_ha": "prod24", "agri_soja_ha_plantada": "area24"}
    )
    soja = s88.merge(s24, on="code_amc", how="inner")
    soja["delta_prod"] = soja["prod24"] - soja["prod88"]
    soja["delta_area_ha"] = soja["area24"] - soja["area88"]

    # bovino: 1985 e 2024
    b85 = df[df["ano"] == 1985][["code_amc", "lotacao_bov_ha", "lulc_pastagem_ha"]].rename(
        columns={"lotacao_bov_ha": "lot85", "lulc_pastagem_ha": "pasto85"}
    )
    b24 = df[df["ano"] == 2024][["code_amc", "lotacao_bov_ha", "lulc_pastagem_ha"]].rename(
        columns={"lotacao_bov_ha": "lot24", "lulc_pastagem_ha": "pasto24"}
    )
    bov = b85.merge(b24, on="code_amc", how="inner")
    bov["delta_lot"] = bov["lot24"] - bov["lot85"]
    bov["delta_pasto_ha"] = bov["pasto24"] - bov["pasto85"]

    # merge
    d = soja.merge(bov, on="code_amc", how="outer")
    return d


def panel_map(gdf: gpd.GeoDataFrame, col: str, ax, title: str, cmap: str, center: float | None, vmin=None, vmax=None, label=""):
    merged = gdf.copy()
    # limita outliers visuais no 1% superior/inferior para RdBu
    vals = merged[col].dropna()
    if vmin is None:
        vmin = np.percentile(vals, 1)
    if vmax is None:
        vmax = np.percentile(vals, 99)

    # TwoSlopeNorm exige vmin < center < vmax
    if center is not None:
        if vmin >= center:
            vmin = center - 0.05 * abs(vmax - center) - 1e-6
        if vmax <= center:
            vmax = center + 0.05 * abs(center - vmin) + 1e-6
        norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
        sm = merged.plot(column=col, ax=ax, cmap=cmap, norm=norm, edgecolor="k", linewidth=0.2, missing_kwds={"color": "#eeeeee", "label": "sem dado"})
    else:
        sm = merged.plot(column=col, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, edgecolor="k", linewidth=0.2, missing_kwds={"color": "#eeeeee", "label": "sem dado"})

    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    ax.axis("off")
    adicionar_norte(ax, location="upper left", size=0.9)
    adicionar_escala(ax, dx=1, total_km=200, location="lower left")

    # colorbar
    cbar = plt.colorbar(sm.collections[0], ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(label, fontsize=9)
    return merged


def main():
    df, gdf = load()
    deltas = compute_deltas(df)
    gdf = gdf.merge(deltas, on="code_amc", how="left")

    fig, axes = plt.subplots(2, 2, figsize=(15, 13), constrained_layout=True)
    fig.patch.set_facecolor("white")

    # A) delta produtividade soja
    panel_map(
        gdf, "delta_prod", axes[0, 0],
        title="A) Soja: Δ produtividade 1988→2024 (t/ha)",
        cmap="RdBu_r", center=0,
        label="Δ t/ha"
    )

    # B) delta lotacao bovina
    panel_map(
        gdf, "delta_lot", axes[0, 1],
        title="B) Bovinocultura: Δ lotação 1985→2024 (cab/ha)",
        cmap="RdBu_r", center=0,
        label="Δ cab/ha"
    )

    # C) delta area soja (sequencial)
    panel_map(
        gdf, "delta_area_ha", axes[1, 0],
        title="C) Soja: Δ área plantada 1988→2024 (ha)",
        cmap="YlGnBu", center=None,
        label="Δ ha"
    )

    # D) scatter
    ax = axes[1, 1]
    d = gdf.dropna(subset=["delta_prod", "delta_area_ha", "delta_lot"]).copy()
    scatter = ax.scatter(
        d["delta_area_ha"] / 1e3,
        d["delta_prod"],
        c=d["delta_lot"],
        cmap="RdBu_r",
        norm=TwoSlopeNorm(vmin=d["delta_lot"].quantile(0.02), vcenter=0, vmax=d["delta_lot"].quantile(0.98)),
        s=60,
        edgecolor="k",
        linewidth=0.3,
        alpha=0.9,
    )
    ax.axhline(0, color="gray", lw=1, ls="--", alpha=0.5)
    ax.axvline(0, color="gray", lw=1, ls="--", alpha=0.5)
    ax.set_xlabel("Δ área de soja (mil ha)", fontsize=10)
    ax.set_ylabel("Δ produtividade de soja (t/ha)", fontsize=10)
    ax.set_title("D) Δ produtividade × Δ área de soja\n(cores = Δ lotação bovina)", fontsize=11, fontweight="bold", loc="left")

    # anotar alguns outliers
    top_area = d.nlargest(3, "delta_area_ha")
    top_prod = d.nlargest(3, "delta_prod")
    top_neg = d.nsmallest(3, "delta_prod")
    for _, row in pd.concat([top_area, top_prod, top_neg]).drop_duplicates("code_amc").iterrows():
        nome = row["amc_nome_rep"] if pd.notna(row.get("amc_nome_rep")) else str(int(row["code_amc"]))
        ax.annotate(
            nome,
            (row["delta_area_ha"] / 1e3, row["delta_prod"]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
        )

    cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Δ lotação bovina (cab/ha)", fontsize=9)

    fig.suptitle(
        "Intensificação vs. extensão por AMC em Goiás",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Mapa salvo: {OUT}")

    # resumo
    print("\nResumo espacial:")
    print(f"  AMCs com soja em 1988 e 2024: {gdf['delta_prod'].notna().sum()}")
    print(f"  AMCs com bovino em 1985 e 2024: {gdf['delta_lot'].notna().sum()}")
    print("  Soja delta produtividade (t/ha):")
    print(gdf["delta_prod"].describe())
    print("  Bovino delta lotacao (cab/ha):")
    print(gdf["delta_lot"].describe())


if __name__ == "__main__":
    main()
