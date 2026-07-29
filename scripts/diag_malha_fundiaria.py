"""Diagnóstico da Malha Fundiária Ambiental LAPIG (GO) — breakdown de área por classe.

Roda a pendência §10 de Textos/metodologia/malha_fundiaria_ambiental.md:
soma de área por `cls_malha` (e por `fonte`) em hectares, com a projeção
equal-area nativa (ESRI:102033 Albers). Dimensiona os buckets do placebo de
especificidade da Perna 4 e gera o perfil fundiário descritivo de GO.

Stack verificado: Py 3.14 + pyarrow 24 + geopandas 1.1.3 + shapely 2.1.2.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Console Windows defaulta para cp1252 (mojibake + crash em U+2212/U+2248).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import geopandas as gpd
import pandas as pd

PARQUET = Path(r"C:\Users\amara\Downloads\brasil_malhafundiaria_ambiental_10m_v3b_GO.parquet")
CRS_NATIVO = "ESRI:102033"  # Albers equal-area — metros; CRS ausente dos metadados


def main() -> None:
    print(f"Lendo: {PARQUET.name} ({PARQUET.stat().st_size / 1e9:.1f} GB)")
    gdf = gpd.read_parquet(
        PARQUET, columns=["cls_malha", "fonte", "cod_malha", "GEOCODIGO", "geometry"]
    )
    # GeoParquet v1.1 defaulta para OGC:CRS84 quando o campo `crs` está ausente —
    # o arquivo LAPIG não traz o CRS (doc §7), mas as coordenadas estão em metros
    # Albers (equal-area). Seta na mão com allow_override para silenciar o aviso e
    # habilitar reprojeção correta depois.
    gdf.set_crs(CRS_NATIVO, inplace=True, allow_override=True)
    print(f"  -> {len(gdf):,} polígonos | CRS forçado: {gdf.crs}")

    # Área em m^2 (Albers equal-area) -> ha. Z (MultiPolygon Z) é ignorado por .area.
    print("Computando área (equal-area, m^2 -> ha)...")
    area_ha = gdf.geometry.area / 10_000.0
    total_ha = float(area_ha.sum())
    print(f"  -> área total: {total_ha:,.0f} ha ({total_ha/1e6:,.2f} Mha)\n")

    df = pd.DataFrame(
        {"cls_malha": gdf["cls_malha"].values, "fonte": gdf["fonte"].values, "area_ha": area_ha.values}
    )

    # --- Por classe fundiária ---
    por_cls = (
        df.groupby("cls_malha")
        .agg(n_polys=("area_ha", "size"), area_ha=("area_ha", "sum"))
        .sort_values("area_ha", ascending=False)
    )
    por_cls["area_Mha"] = por_cls["area_ha"] / 1e6
    por_cls["pct_area"] = 100 * por_cls["area_ha"] / total_ha
    por_cls["pct_polys"] = 100 * por_cls["n_polys"] / len(df)
    print("=== Área por cls_malha ===")
    print(f"{'cls_malha':<32} {'n_polys':>10} {'area_ha':>14} {'Mha':>8} {'%area':>7} {'%polys':>7}")
    for cls, r in por_cls.iterrows():
        print(
            f"{cls:<32} {int(r['n_polys']):>10,} {r['area_ha']:>14,.0f} "
            f"{r['area_Mha']:>8.2f} {r['pct_area']:>6.2f}% {r['pct_polys']:>6.2f}%"
        )
    print(f"{'TOTAL':<32} {len(df):>10,} {total_ha:>14,.0f} {total_ha/1e6:>8.2f} {'100.00%':>7} {'100.00%':>7}")

    # --- Por fonte (desagrega 'Ativo Ambiental' em app/rl) ---
    print("\n=== Área por fonte ===")
    por_fonte = (
        df.groupby("fonte")
        .agg(n_polys=("area_ha", "size"), area_ha=("area_ha", "sum"))
        .sort_values("area_ha", ascending=False)
    )
    por_fonte["pct_area"] = 100 * por_fonte["area_ha"] / total_ha
    print(f"{'fonte':<20} {'n_polys':>10} {'area_ha':>14} {'%area':>7}")
    for f, r in por_fonte.iterrows():
        print(f"{f:<20} {int(r['n_polys']):>10,} {r['area_ha']:>14,.0f} {r['pct_area']:>6.2f}%")

    # --- Buckets do placebo (§4.1 do doc), via `fonte` (códigos ASCII, robustos) ---
    print("\n=== Buckets do placebo (§4.1) — via fonte ===")
    BUCKETS = {
        # (nome, set de códigos `fonte`)
        "Placebo limpo (exógeno)":        {"ma", "mu", "tih", "am"},
        "Placebo frágil (UC/TI não-hom.)":{"ucpi", "ucus", "tinh", "tqd", "tqnd"},
        "Bucket ativo (privado/assent.)": {"sigef_snci", "carss", "carcs", "asses"},
        "Ativo Ambiental (APP/RL)":       {"app", "rl"},
    }
    print(f"{'bucket':<34} {'n_polys':>10} {'area_ha':>14} {'Mha':>8} {'%area':>7}")
    for nome, fonts in BUCKETS.items():
        sub = df[df["fonte"].isin(fonts)]
        a = sub["area_ha"].sum()
        print(f"{nome:<34} {len(sub):>10,} {a:>14,.0f} {a/1e6:>8.2f} {100*a/total_ha:>6.2f}%")

    # --- Subtotais estruturais (cuidado: Ativo Ambiental é OVERLAY, double-counta) ---
    print("\n=== Subtotais estruturais ===")
    privado_bruto = df[df["fonte"].isin(["sigef_snci", "carss", "carcs"])]["area_ha"].sum()
    protegido = df[df["fonte"].isin(["tih", "tinh", "ucpi", "ucus", "tqd", "tqnd"])]["area_ha"].sum()
    app_rl = df[df["fonte"].isin(["app", "rl"])]["area_ha"].sum()
    tenure = total_ha - app_rl  # território sem o overlay APP/RL
    print(f"  Privado bruto (SIGEF + CAR):   {privado_bruto/1e6:6.2f} Mha  ({100*privado_bruto/tenure:5.1f}% da tenure)")
    print(f"  Protegido (TI + UC + quilombo):{protegido/1e6:6.2f} Mha  ({100*protegido/tenure:5.1f}% da tenure)")
    print(f"  APP/RL (overlay, passivo):     {app_rl/1e6:6.2f} Mha  — sobreposto à tenure, NÃO soma ao território")
    print(f"  Território efetivo (tenure):   {tenure/1e6:6.2f} Mha  (= total − APP/RL overlay)")
    print(f"  Total bruto (double-counta):   {total_ha/1e6:6.2f} Mha")
    print(f"  -> Privado LÍQUIDO ≈ privado − APP/RL (maioria dentro do privado)")
    print(f"     = {privado_bruto/1e6:.2f} − ~{app_rl/1e6:.2f} ≈ {(privado_bruto-app_rl)/1e6:.2f} Mha ( aprox.; overlay exato pende)")

    # --- Sanity: território de GO esperado ~ 34 Mha ---
    print(f"\nSanity: território efetivo (tenure) {tenure/1e6:,.2f} Mha vs GO ~ 34 Mha")

    # --- Cobertura municipal (buraco?) ---
    n_mun = gdf["GEOCODIGO"].nunique()
    print(f"Municípios distintos no arquivo: {n_mun} (esperado 246)")

    # --- Persistir em CSV (reproduzível / grepável) ---
    out = Path("outputs/diag_malha_fundiaria_por_classe.csv")
    out.parent.mkdir(exist_ok=True)
    por_cls.reset_index().to_csv(out, index=False, encoding="utf-8")
    out2 = Path("outputs/diag_malha_fundiaria_por_fonte.csv")
    por_fonte.reset_index().to_csv(out2, index=False, encoding="utf-8")
    print(f"\nGravado: {out}  |  {out2}")


if __name__ == "__main__":
    main()