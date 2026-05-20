"""gerar_mapas_lulc_40anos.py — 40 mapas coropléticos anuais (1985–2024)
de cobertura e uso da terra para os 246 municípios de Goiás.

Como rodar:
    python "Scripts e Catalogo/gerar_mapas_lulc_40anos.py"

Pré-requisitos:
    pip install pandas geopandas geobr matplotlib matplotlib-scalebar

Saída:
    outputs/mapas/cobertura_{ANO}.png  (40 arquivos, DPI 200, ~10x8 pol)
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import geopandas as gpd
import geobr
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cartografia import adicionar_norte, adicionar_escala  # noqa: E402

# ===== Configuração =====
SHOW_BORDERS = False
DPI = 200
FIGSIZE = (10, 8)
ANO_MIN, ANO_MAX = 1985, 2024

CLASSES = {
    "Floresta":       {"ids": [3],                           "cor": "#006400"},
    "Cerrado":        {"ids": [4],                           "cor": "#32CD32"},
    "Campo natural":  {"ids": [12],                          "cor": "#90EE90"},
    "Pastagem":       {"ids": [15],                          "cor": "#FFD700"},
    "Soja":           {"ids": [39],                          "cor": "#FF69B4"},
    "Lavouras+Cana":  {"ids": [20, 40, 41, 46, 47, 48, 62], "cor": "#800080"},
    "Área urbana":    {"ids": [24],                          "cor": "#A0A0A0"},
    "Água":           {"ids": [33],                          "cor": "#4169E1"},
}
ORDEM_LEGENDA = list(CLASSES.keys())
COR_POR_CLASSE = {k: v["cor"] for k, v in CLASSES.items()}
ID_PARA_CLASSE = {cid: nome for nome, info in CLASSES.items() for cid in info["ids"]}

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "processed" / "mapbiomas_munis_goias.csv"
OUT_DIR = ROOT / "outputs" / "mapas"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def preprocessar(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype={"cd_mun": "int64"})
    df = df[df["class_id"].isin(ID_PARA_CLASSE)].copy()
    df["classe_agregada"] = df["class_id"].map(ID_PARA_CLASSE)
    df = df.dropna(subset=["classe_agregada"])

    agg = (
        df.groupby(["cd_mun", "ano", "classe_agregada"], as_index=False)["area_ha"]
        .sum()
    )

    # Classe dominante por (cd_mun, ano): maior area_ha
    idx = agg.groupby(["cd_mun", "ano"])["area_ha"].idxmax()
    dominante = agg.loc[idx, ["cd_mun", "ano", "classe_agregada"]].rename(
        columns={"classe_agregada": "classe_dominante"}
    )

    dominante_wide = dominante.pivot(
        index="cd_mun", columns="ano", values="classe_dominante"
    )
    return dominante_wide


def carregar_malha() -> gpd.GeoDataFrame:
    print("[...] Baixando/carregando malha municipal de Goiás (geobr)...")
    gdf = geobr.read_municipality(code_muni="GO", year=2020)
    gdf["code_muni"] = gdf["code_muni"].astype("int64")
    # Reprojetar para EPSG:5880 (Albers Brasil, métrico) para corrigir o achatamento geográfico
    gdf = gdf.to_crs(5880)
    return gdf


def gerar_mapas(dominante_wide: pd.DataFrame, gdf_munis: gpd.GeoDataFrame) -> None:
    handles_legenda = [
        Patch(facecolor=COR_POR_CLASSE[n], edgecolor="black", label=n)
        for n in ORDEM_LEGENDA
    ]
    edgecolor = "black" if SHOW_BORDERS else "none"

    # Limites fixos baseados no total_bounds da malha projetada (EPSG:5880) com 2% de margem
    bounds = gdf_munis.total_bounds
    x_margin = (bounds[2] - bounds[0]) * 0.02
    y_margin = (bounds[3] - bounds[1]) * 0.02
    xmin, xmax = bounds[0] - x_margin, bounds[2] + x_margin
    ymin, ymax = bounds[1] - y_margin, bounds[3] + y_margin

    anos = list(range(ANO_MIN, ANO_MAX + 1))
    for i, ano in enumerate(anos, start=1):
        if ano not in dominante_wide.columns:
            print(f"[AVISO] Ano {ano} não encontrado no CSV — pulando.")
            continue

        serie = dominante_wide[[ano]].rename(columns={ano: "classe_dominante"})
        gdf_ano = gdf_munis.merge(
            serie, left_on="code_muni", right_index=True, how="left"
        )

        cor_munis = gdf_ano["classe_dominante"].map(COR_POR_CLASSE).fillna("#CCCCCC")

        fig, ax = plt.subplots(figsize=FIGSIZE)
        gdf_ano.plot(
            ax=ax,
            color=cor_munis,
            edgecolor=edgecolor,
            linewidth=0.2,
        )

        ax.set_title(
            f"Cobertura e Uso da Terra — Goiás {ano}",
            fontsize=14,
            pad=10,
        )

        ax.legend(
            handles=handles_legenda,
            loc="lower right",
            frameon=True,
            fontsize=8,
            title="Classe dominante",
            title_fontsize=8,
            borderaxespad=-1.2,
        )

        # Fixar limites para enquadramento idêntico
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_axis_off()

        # ScaleBar em CRS métrico (EPSG:5880): dx = 1 metro por unidade do eixo X.
        adicionar_escala(ax, dx=1, total_km=150)
        adicionar_norte(ax)

        fig.savefig(OUT_DIR / f"cobertura_{ano}.png", dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        print(f"[{i:02d}/40] cobertura_{ano}.png salvo")


def main() -> None:
    print("=" * 60)
    print("Gerando 40 mapas coropléticos LULC — Goiás 1985–2024")
    print("=" * 60)

    print(f"[...] Lendo {CSV.name}...")
    dominante_wide = preprocessar(CSV)
    print(f"[OK]  {dominante_wide.shape[0]} municípios × {dominante_wide.shape[1]} anos")

    gdf_munis = carregar_malha()
    print(f"[OK]  Malha: {len(gdf_munis)} municípios, CRS {gdf_munis.crs}")

    gerar_mapas(dominante_wide, gdf_munis)

    print("\n" + "=" * 60)
    print(f"Concluído! PNGs em: {OUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
