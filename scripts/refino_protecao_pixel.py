"""refino_protecao_pixel.py — Refino pixel-a-pixel do #46 (fecha o caveat D17)
=============================================================================

O Pipeline #46 mediu o "convertível desprotegido" com um PROXY: aplicou a fração
de Proteção Integral (PI) de cada AMC ao estoque convertível assumindo distribuição
UNIFORME intra-AMC (D17). Este script fecha esse caveat medindo NO RASTER, via GEE,
quanto do Cerrado convertível de 2024 (savana ID 4 + campo ID 12, def. refinada do
#39) cai DENTRO dos polígonos de Proteção Integral — pixel a pixel.

Estratégia de computação (contorna o limite interativo do GEE):
    reduceRegions sobre as 166 AMCs estoura ("Computation timed out"); polígonos
    regionais dissolvidos (muitos vértices) também. Solução que funciona: geometria
    SIMPLES do estado (união) + banda de código de região rasterizada (reduceToImage)
    + Reducer.sum().group(groupField) — UMA passada agregada por região.

Pré-requisitos: earthengine-api autenticado (ee.Initialize com GEE_PROJECT),
    geobr, geopandas. Rodar com py -3.14 (ver reference/ambiente_python).

Entradas:
    projects/mapbiomas-public/.../collection10_1 coverage (band classification_2024)
    data/processed/amc_goias.gpkg                     (#25)
    data/processed/fronteira_estoque_convertivel.csv  (#39, região + proxy)
    data/processed/protecao_uc_amc.csv                (#46, frac_pi p/ o proxy)
    geobr.read_conservation_units() (PI) + read_state("GO")

Saída:
    data/processed/protecao_gap_pixel_regiao.csv  (conv/desprot pixel × proxy, por região)

Resultado (2026-07-16): estado 94,3% desprotegido no pixel (vs 97% proxy); Norte 93,4%,
    Centro 98,1%, Sul 88,8% (proxy superestimava o Sul — as UCs de PI do Sudoeste, ex.
    Parque Nacional das Emas = savana/campo, assentam sobre convertível). Manchete do #46
    inalterada e agora pixel-validada.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import geobr
import geopandas as gpd
import pandas as pd

GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET = ("projects/mapbiomas-public/assets/brazil/lulc/collection10_1/"
         "mapbiomas_brazil_collection10_1_coverage_v1")
ANO = 2024
CONVERTIVEL_IDS = [4, 12]  # savana + campo nativo (def. refinada #39)

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    ee.Initialize(project=project)
    print(f"GEE inicializado (projeto: {project})")


def main() -> None:
    init_ee()

    cob = ee.Image(ASSET).select(f"classification_{ANO}")
    convert = cob.eq(CONVERTIVEL_IDS[0])
    for cid in CONVERTIVEL_IDS[1:]:
        convert = convert.Or(cob.eq(cid))

    go = geobr.read_state(code_state="GO").to_crs(4326)
    go_geom = ee.Geometry(go.geometry.union_all().__geo_interface__)

    # Proteção Integral -> máscara raster
    uc = geobr.read_conservation_units()
    pi = uc[uc["group"] == "PI"].to_crs(4326)
    pi = pi[pi.geometry.notna()]
    pi_go = gpd.overlay(pi[["geometry"]], go[["geometry"]], how="intersection")
    pi_fc = ee.FeatureCollection(
        [ee.Feature(ee.Geometry(g.__geo_interface__)) for g in pi_go.geometry])
    pi_mask = ee.Image.constant(1).clip(pi_fc).mask().gt(0)

    # AMC + região (#39) -> banda de código de região
    amc = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(4326)
    amc["code_amc"] = amc["code_amc"].astype(int)
    est = pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv")
    ult = int(est["ano"].max())
    reg_map = est[est["ano"] == ult][["code_amc", "regiao", "estoque_refinada_ha"]]
    prox = pd.read_csv(DIR_PROC / "protecao_uc_amc.csv")[["code_amc", "frac_pi"]]
    amc = amc.merge(reg_map, on="code_amc", how="left").merge(prox, on="code_amc", how="left")
    amc["conv_desprot_proxy_ha"] = amc["estoque_refinada_ha"] * (1 - amc["frac_pi"].fillna(0))

    regioes = sorted(amc["regiao"].dropna().unique())
    cod = {r: i + 1 for i, r in enumerate(regioes)}
    amc["reg_code"] = amc["regiao"].map(cod).fillna(0).astype(int)
    print("regiões:", cod)

    feats = [ee.Feature(ee.Geometry(r.geometry.__geo_interface__), {"reg_code": int(r.reg_code)})
             for r in amc.itertuples()]
    reg_img = ee.FeatureCollection(feats).reduceToImage(["reg_code"], ee.Reducer.first()).rename("reg_code")

    area_ha = ee.Image.pixelArea().divide(1e4)

    def grouped(masked_area: ee.Image) -> dict:
        r = (masked_area.rename("v").addBands(reg_img)
             .reduceRegion(reducer=ee.Reducer.sum().group(groupField=1, groupName="reg_code"),
                           geometry=go_geom, scale=30, maxPixels=int(1e13),
                           bestEffort=True, tileScale=4).getInfo())
        return {int(g["reg_code"]): g["sum"] for g in r["groups"]}

    print("passada 1/2: convertível por região...")
    g_conv = grouped(area_ha.updateMask(convert))
    print("passada 2/2: convertível ∩ PI por região...")
    g_conv_pi = grouped(area_ha.updateMask(convert.And(pi_mask)))

    inv = {v: k for k, v in cod.items()}
    linhas = []
    for code, regiao in inv.items():
        conv = g_conv.get(code, 0) or 0
        conv_pi = g_conv_pi.get(code, 0) or 0
        proxy = amc[amc["regiao"] == regiao]["conv_desprot_proxy_ha"].sum()
        linhas.append({
            "regiao": regiao,
            "conv_px_Mha": conv / 1e6,
            "conv_pi_px_Mha": conv_pi / 1e6,
            "desprot_px_Mha": (conv - conv_pi) / 1e6,
            "pct_desprot_pixel": 100 * (conv - conv_pi) / conv if conv else None,
            "pct_desprot_proxy": 100 * proxy / conv if conv else None,
        })
    out = pd.DataFrame(linhas).sort_values("conv_px_Mha", ascending=False)

    tot_conv = out["conv_px_Mha"].sum()
    tot_desp = out["desprot_px_Mha"].sum()
    estado = pd.DataFrame([{
        "regiao": "ESTADO", "conv_px_Mha": tot_conv,
        "conv_pi_px_Mha": out["conv_pi_px_Mha"].sum(), "desprot_px_Mha": tot_desp,
        "pct_desprot_pixel": 100 * tot_desp / tot_conv, "pct_desprot_proxy": None,
    }])
    out = pd.concat([estado, out], ignore_index=True)

    saida = DIR_PROC / "protecao_gap_pixel_regiao.csv"
    out.to_csv(saida, index=False, encoding="utf-8")

    print("\n=== REFINO PIXEL vs PROXY (convertível 2024 savana+campo, % desprotegido) ===")
    for _, r in out.iterrows():
        pp = f"{r['pct_desprot_proxy']:.1f}%" if pd.notna(r["pct_desprot_proxy"]) else "  —"
        print(f"  {r['regiao']:10s} conv {r['conv_px_Mha']:5.3f} Mha | "
              f"PIXEL {r['pct_desprot_pixel']:4.1f}% | PROXY {pp}")
    print(f"\n[OK] {saida.name}")


if __name__ == "__main__":
    main()
