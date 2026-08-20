"""aptidao_edafo_exposicao.py -- Protótipo (candidato a #52): aptidão edafoclimática
   como exposição EXÓGENA para o #38, e validação do gradiente Sul→Norte
====================================================================================

PERGUNTA QUE RESPONDE (Etapa A do plano)
----------------------------------------
O #38 testa "o choque comum (câmbio) bate mais forte onde a EXPOSIÇÃO é maior?".
A exposição de hoje é "% de área baseline 1985-89" -- um PROXY de aptidão que é
(a) mecanicamente complementar (`exp_fronteira ≈ −exp_apt_agri`, somam ~constante ->
inflam a "coerência de sinais", Achado #3 do #38) e (b) semi-endógena (share de uso
humano já reflete escolhas). Este protótipo constrói uma exposição de aptidão
EDAFOCLIMÁTICA FÍSICA -- exógena e NÃO-complementar -- e, antes de plugá-la no #38
(Etapa B), responde a pergunta descritiva mais barata e mais robusta:

    A aptidão agronômica MEDIDA reproduz o gradiente Sul→Norte que a narrativa assume?

Isso transforma a premissa hoje ASSUMIDA ("o Sul é apto, o Norte é fronteira") em
evidência medida com um dado independente do LULC -- e NÃO depende do teto de poder
temporal do #38 (o driver varia só ~40×; uma exposição melhor limpa a identificação,
não fabrica poder).

DADO (verificado 2026-07-18)
----------------------------
Embrapa GeoServer WFS (nacional, fetchável -- contorna o cert TLS quebrado do SIEG):
    https://geoinfo.dados.embrapa.br/geoserver/ows
    camada geonode:aptidao_agr_bra  (Aptidão Agrícola das Terras do Brasil, 1:500k)
Campo ordinal `simb_apt` = sistema Ramalho Filho & Beek (1995): o DÍGITO LÍDER é o
grupo de aptidão --
    1 = boa p/ lavouras (melhor) ... 3 = restrita p/ lavouras ...
    4 = apta só p/ pastagem plantada ... 6 = preservação (pior p/ agricultura).
Score de aptidão para lavoura = 7 − grupo  (maior = mais apto). Upgrade posterior:
trocar por MacroZAEE-GO (estadual, mais fino) -- mesma pipeline.

MÉTODO
------
1. WFS GetFeature paginado, recortado no bbox de GO -> cache GeoJSON.
2. `simb_apt` -> grupo (1..6) -> score (7−grupo).
3. Overlay com as 166 AMCs em ESRI:102033 (South America Albers Equal Area
   Conic — equal-area verdadeiro; reusa a máquina do #46);
   aptidão da AMC = média do score PONDERADA POR ÁREA dos polígonos que a cobrem.
   Variante de robustez: pct_apt_lavoura = % da AMC com grupo ≤ 3 (apta p/ lavoura).
4. z-score sobre as 166 AMCs -> exp_apt_edafo (pronta p/ o #38).
5. Validação: correlaciona exp_apt_edafo com latitude, com a exposição atual do #38
   (% agri baseline) e com a fronteira (% veg baseline). Pearson + Spearman (ordinal).

ENTRADAS
    data/processed/amc_goias.gpkg                     (#25, geometria das AMC)
    data/processed/taxas_lulc_amc.csv                 (#36/AMC, shares baseline)
    data/processed/fronteira_estoque_convertivel.csv  (#39, regiao + lat por AMC)
    WFS Embrapa (cacheado em data/raw/aptidao/)

SAÍDAS
    data/processed/aptidao_edafo_amc.csv
    outputs/aptidao_edafo/validacao_gradiente.png

COMO RODAR
    py -3.14 scripts/aptidao_edafo_exposicao.py
    py -3.14 scripts/aptidao_edafo_exposicao.py --sem-figuras
    py -3.14 scripts/aptidao_edafo_exposicao.py --force   (re-baixa o WFS)
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_RAW  = ROOT / "data" / "raw" / "aptidao"
DIR_OUT  = ROOT / "outputs" / "aptidao_edafo"
DIR_RAW.mkdir(parents=True, exist_ok=True)
DIR_OUT.mkdir(parents=True, exist_ok=True)

CRS_AREA = "ESRI:102033"   # South America Albers Equal Area Conic (equal-area verdadeiro, métrico)
WFS_BASE = "https://geoinfo.dados.embrapa.br/geoserver/ows"
WFS_LAYER = "geonode:aptidao_agr_bra"
BBOX_GO  = (-19.6, -53.3, -12.3, -45.9)   # (minlat, minlon, maxlat, maxlon) p/ EPSG::4326
BASELINE = (1985, 1989)


# ─────────────────────────── 1. Fetch WFS (paginado, cacheado) ───────────────────────────

def baixar_aptidao(force: bool = False) -> "gpd.GeoDataFrame":
    import geopandas as gpd
    cache = DIR_RAW / "aptidao_agr_bra_go.gpkg"
    if cache.exists() and not force:
        print(f"[cache] {cache.relative_to(ROOT)}")
        return gpd.read_file(cache)

    import requests
    feats: list = []
    page, start = 2000, 0
    while True:
        params = {
            "service": "WFS", "version": "2.0.0", "request": "GetFeature",
            "typeNames": WFS_LAYER, "outputFormat": "application/json",
            "srsName": "EPSG:4326", "count": page, "startIndex": start,
            "bbox": f"{BBOX_GO[0]},{BBOX_GO[1]},{BBOX_GO[2]},{BBOX_GO[3]},urn:ogc:def:crs:EPSG::4326",
        }
        r = requests.get(WFS_BASE, params=params, timeout=180)
        r.raise_for_status()
        js = r.json()
        got = js.get("features", [])
        feats.extend(got)
        print(f"  [wfs] startIndex={start:>5} -> {len(got)} feições (acum {len(feats)})")
        if len(got) < page:
            break
        start += page
    gdf = gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326")
    gdf.to_file(cache, driver="GPKG")
    print(f"[OK] {cache.relative_to(ROOT)} ({len(gdf)} polígonos)")
    return gdf


# ─────────────────────────── 2. simb_apt -> grupo -> score ───────────────────────────

def _grupo(simb: str) -> float:
    """Dígito líder do símbolo de aptidão (Ramalho Filho & Beek): grupo 1..6.
    1 = boa p/ lavouras ... 6 = preservação. NaN se não houver dígito 1-6."""
    if not isinstance(simb, str):
        return np.nan
    m = re.search(r"[1-6]", simb)
    return float(m.group(0)) if m else np.nan


def preparar_aptidao(gdf: "gpd.GeoDataFrame") -> "gpd.GeoDataFrame":
    gdf = gdf.copy()
    gdf["grupo"] = gdf["simb_apt"].map(_grupo)
    # fallback: dígito líder da legenda quando simb_apt não traz grupo
    faltando = gdf["grupo"].isna()
    if faltando.any() and "legenda_ap" in gdf.columns:
        gdf.loc[faltando, "grupo"] = gdf.loc[faltando, "legenda_ap"].map(_grupo)
    gdf["score"] = 7.0 - gdf["grupo"]        # maior = mais apto p/ lavoura
    gdf["apt_lavoura"] = (gdf["grupo"] <= 3).astype(float)  # grupos 1-3 = aptos p/ lavoura
    gdf = gdf.to_crs(CRS_AREA)
    gdf["geometry"] = gdf.geometry.make_valid()
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
    return gdf[["grupo", "score", "apt_lavoura", "geometry"]]


# ─────────────────────────── 3. Zonal por AMC (área-ponderada, máquina do #46) ───────────

def agregar_por_amc(apt: "gpd.GeoDataFrame") -> pd.DataFrame:
    import geopandas as gpd
    amc = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(CRS_AREA)
    amc["code_amc"] = amc["code_amc"].astype(int)

    inter = gpd.overlay(amc[["code_amc", "geometry"]], apt, how="intersection")
    inter["area"] = inter.geometry.area
    inter = inter[inter["score"].notna() & (inter["area"] > 0)]

    def _wmean(g: pd.DataFrame) -> pd.Series:
        w = g["area"]
        return pd.Series({
            "apt_score_mean": np.average(g["score"], weights=w),
            "pct_apt_lavoura": np.average(g["apt_lavoura"], weights=w),
            "area_coberta_ha": w.sum() / 1e4,
        })

    out = inter.groupby("code_amc").apply(_wmean).reset_index()
    out["exp_apt_edafo"] = (out["apt_score_mean"] - out["apt_score_mean"].mean()) / out["apt_score_mean"].std(ddof=0)
    return out


# ─────────────────────────── 4. Exposições atuais do #38 (baseline) + geografia ──────────

def contexto_amc() -> pd.DataFrame:
    tx = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")
    base = tx[(tx["ano"] >= BASELINE[0]) & (tx["ano"] <= BASELINE[1])]
    expo = base.groupby("code_amc").agg(
        agricultura_pct=("agricultura_pct", "mean"),
        vegetacao_natural_pct=("vegetacao_natural_pct", "mean"),
    ).reset_index()
    z = lambda s: (s - s.mean()) / s.std(ddof=0)
    expo["exp_apt_agri"]  = z(expo["agricultura_pct"])       # exposição atual do #38
    expo["exp_fronteira"] = z(expo["vegetacao_natural_pct"])

    geo = pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv",
                      usecols=["code_amc", "regiao", "lat"]).drop_duplicates("code_amc")
    return expo.merge(geo, on="code_amc", how="left")


# ─────────────────────────── 5. Validação (correlações) ───────────────────────────

def validar(df: pd.DataFrame) -> dict:
    from scipy.stats import pearsonr, spearmanr
    pares = {
        "aptidão × latitude (espera −: apto no Sul)":        ("exp_apt_edafo", "lat"),
        "aptidão × exp. atual do #38 (% agri, espera +)":    ("exp_apt_edafo", "exp_apt_agri"),
        "aptidão × fronteira (% veg baseline, espera −)":    ("exp_apt_edafo", "exp_fronteira"),
    }
    res = {}
    for rot, (a, b) in pares.items():
        s = df[[a, b]].dropna()
        pr, pp = pearsonr(s[a], s[b])
        sr, sp = spearmanr(s[a], s[b])
        res[rot] = dict(pearson=pr, p_pearson=pp, spearman=sr, p_spearman=sp, n=len(s))
    return res


# ─────────────────────────── 6. Figura ───────────────────────────

def figura(df: pd.DataFrame, apt_gdf) -> None:
    import matplotlib.pyplot as plt
    import geopandas as gpd

    amc = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(CRS_AREA)
    amc["code_amc"] = amc["code_amc"].astype(int)
    amc = amc.merge(df[["code_amc", "exp_apt_edafo", "apt_score_mean"]], on="code_amc", how="left")

    fig, (axm, axs) = plt.subplots(1, 2, figsize=(14, 6))

    amc.plot(column="apt_score_mean", cmap="YlGn", legend=True, ax=axm,
             edgecolor="0.7", linewidth=0.2,
             legend_kwds={"label": "Aptidão média (7−grupo; maior = mais apto p/ lavoura)",
                          "shrink": 0.6})
    axm.set_title("Aptidão edafoclimática por AMC (Embrapa 1:500k)", fontsize=11, loc="left")
    axm.axis("off")

    cores = {"Sul": "#1b7837", "Centro": "#f0a202", "Norte": "#c44e00"}
    for reg, g in df.dropna(subset=["regiao"]).groupby("regiao"):
        axs.scatter(g["lat"], g["apt_score_mean"], s=32, alpha=0.8,
                    color=cores.get(reg, "0.5"), label=reg)
    # linha de tendência
    s = df[["lat", "apt_score_mean"]].dropna()
    b, a = np.polyfit(s["lat"], s["apt_score_mean"], 1)
    xs = np.linspace(s["lat"].min(), s["lat"].max(), 50)
    axs.plot(xs, a + b * xs, color="0.3", ls="--", lw=1.5)
    axs.set_xlabel("Latitude do centroide da AMC  (Sul ←  → Norte)")
    axs.set_ylabel("Aptidão média para lavoura")
    axs.set_title("A aptidão medida cai ao Norte?", fontsize=11, loc="left")
    axs.legend(title="Região", fontsize=9)
    axs.grid(True, alpha=0.25)

    fig.suptitle("Validação: a aptidão edafoclimática (dado exógeno) reproduz o gradiente Sul→Norte",
                 fontsize=13, y=1.00)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "validacao_gradiente.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'validacao_gradiente.png').relative_to(ROOT)}")


# ─────────────────────────── Main ───────────────────────────

def main(sem_figuras: bool = False, force: bool = False) -> None:
    print("=" * 76)
    print("Protótipo (cand. #52) — aptidão edafoclimática como exposição exógena + validação")
    print("=" * 76)

    print("\n[1] WFS Embrapa (geonode:aptidao_agr_bra), recorte GO:")
    gdf = baixar_aptidao(force=force)

    print("\n[2] simb_apt -> grupo (Ramalho Filho & Beek) -> score:")
    apt = preparar_aptidao(gdf)
    dist = apt["grupo"].value_counts(dropna=False).sort_index()
    print(f"  polígonos válidos: {len(apt):,} | distribuição por grupo:")
    for g, n in dist.items():
        rot = {1: "boa lavoura", 2: "regular lavoura", 3: "restrita lavoura",
               4: "pastagem plantada", 5: "silvic./past. natural", 6: "preservação"}.get(g, "s/ grupo")
        print(f"    grupo {g if pd.notna(g) else 'NaN'}: {n:>5} ({rot})")

    print("\n[3] Zonal por AMC (área-ponderada, ESRI:102033 Albers equal-area):")
    amc_apt = agregar_por_amc(apt)
    print(f"  {len(amc_apt)} AMCs com aptidão | score médio {amc_apt.apt_score_mean.mean():.2f} "
          f"(min {amc_apt.apt_score_mean.min():.2f}, max {amc_apt.apt_score_mean.max():.2f})")

    print("\n[4] Exposições atuais do #38 (baseline) + geografia:")
    ctx = contexto_amc()
    df = amc_apt.merge(ctx, on="code_amc", how="left")
    df.to_csv(DIR_PROC / "aptidao_edafo_amc.csv", index=False, encoding="utf-8")
    print(f"  [OK] aptidao_edafo_amc.csv ({len(df)} AMCs)")

    print("\n[5] VALIDAÇÃO — a aptidão exógena reproduz o gradiente Sul→Norte?")
    res = validar(df)
    for rot, r in res.items():
        print(f"  {rot}")
        print(f"      Pearson r={r['pearson']:+.3f} (p={r['p_pearson']:.4f}) | "
              f"Spearman ρ={r['spearman']:+.3f} (p={r['p_spearman']:.4f}) | n={r['n']}")
    print("\n  Aptidão média por região (Sul→Norte):")
    reg = df.dropna(subset=["regiao"]).groupby("regiao")["apt_score_mean"].agg(["mean", "size"])
    for r in ["Sul", "Centro", "Norte"]:
        if r in reg.index:
            print(f"    {r:8s}: {reg.loc[r, 'mean']:.2f}  (n={int(reg.loc[r, 'size'])})")

    if not sem_figuras:
        print()
        figura(df, apt)

    print("\n" + "=" * 76)
    print("CONCLUÍDO. Próximo (Etapa B): entrar exp_apt_edafo como exposição no #38.")
    print("=" * 76)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Protótipo aptidão edafoclimática (Etapa A)")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-baixa o WFS")
    args = ap.parse_args()
    try:
        main(sem_figuras=args.sem_figuras, force=args.force)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
