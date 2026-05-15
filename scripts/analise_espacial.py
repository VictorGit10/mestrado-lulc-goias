"""analise_espacial.py -- Pipeline #24: Moran's I, LISA, regressao espacial
============================================================================

Analise espacial estatistica sobre os residuos do Pipeline #22 (painel 2FE) e
sobre as variaveis brutas. Tres saidas principais:

  1. **Moran's I global** dos residuos por (modelo, ano, matriz_W).
     - Detecta autocorrelacao espacial residual nao modelada.
  2. **LISA / Moran local** para anos+modelos com I global significativo.
     - Identifica clusters HH (alto-alto), LL (baixo-baixo), HL (outlier alto-baixo),
       LH (outlier baixo-alto).
     - Mapas coropleticos com 5 categorias.
  3. **Regressao espacial** (spreg) cross-section sobre o modelo mais robusto
     (agricultura ~ Δ VA agro): OLS vs SAR (Spatial Lag) vs SEM (Spatial Error).
     Compara AIC/BIC para decidir se autocorrelacao espacial e estrutural.

Matrizes de pesos:
  - Queen (rainha): contiguidade por fronteira ou vertice. Primaria.
  - KNN-8: 8 vizinhos mais proximos por centroide. Sensibilidade.

Insumos:
  - outputs/correlacoes/painel_residuos.csv (Pipeline #22)
  - data/processed/taxas_lulc_municipal.csv (Pipeline #17, para spreg)
  - data/processed/painel_unificado.parquet (covariaveis para spreg)
  - geobr.read_municipality(code_state='GO', year=2020) (geometrias D6)

Saidas:
  - outputs/espacial/moran_global.csv
  - outputs/espacial/lisa_{modelo}_{ano}.png
  - outputs/espacial/modelos_espaciais.csv

Como rodar:
    python analise_espacial.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import libpysal
from libpysal.weights import Queen, KNN
from esda.moran import Moran, Moran_Local
from spreg import OLS, ML_Lag, ML_Error

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "espacial"
DIR_OUT.mkdir(parents=True, exist_ok=True)

DIR_CORR = ROOT / "outputs" / "correlacoes"

N_PERMUTACOES = 999
SEED = 42

# Modelos a usar para LISA + spreg (subset dos resíduos disponíveis)
MODELOS_FOCO = [
    "pastagem_delta_mha~delta_sicor_total_real_rs",
    "agricultura_delta_mha~delta_va_agro_real_rs",
    "vegetacao_natural_delta_mha~delta_fogo_veg_nat_ha",
]

# Para spreg: pares (Y, X) para rodar OLS vs SAR vs SEM cross-section
# Usar ano com dados completos (2020 — pós-SICOR, pré-2022 sem VA agro)
ANO_SPREG = 2020
PARES_SPREG = [
    ("agricultura_delta_mha", ["delta_va_agro_real_rs", "delta_sicor_total_real_rs"]),
    ("pastagem_delta_mha",    ["delta_sicor_total_real_rs", "delta_va_agro_real_rs"]),
]


def carregar_geometrias() -> "gpd.GeoDataFrame":
    import geobr
    gdf = geobr.read_municipality(code_muni="GO", year=2020)
    # Padronizar cd_mun (7 dig int)
    gdf["cd_mun"] = gdf["code_muni"].astype(int)
    return gdf[["cd_mun", "name_muni", "geometry"]].to_crs(5880)


def montar_pesos(gdf) -> dict:
    """Constroi matrizes Queen e KNN-8, padronizadas por linha."""
    w_queen = Queen.from_dataframe(gdf, use_index=False)
    w_queen.transform = "r"
    w_knn = KNN.from_dataframe(gdf, k=8)
    w_knn.transform = "r"
    return {"queen": w_queen, "knn8": w_knn}


def moran_por_ano(residuos: pd.DataFrame, gdf, pesos: dict) -> pd.DataFrame:
    """Calcula Moran's I para cada (modelo, ano, W). Retorna tabela long."""
    rows = []
    for modelo, sub in residuos.groupby("modelo"):
        for ano, df_ano in sub.groupby("ano"):
            # Merge com geometrias
            df = gdf.merge(df_ano[["cd_mun", "residuo"]], on="cd_mun", how="inner")
            # Drop munis sem residuo
            df = df.dropna(subset=["residuo"])
            if len(df) < 50:
                continue
            for w_name, w in pesos.items():
                # libpysal requer dados na mesma ordem que w
                w_sub = w if len(df) == len(gdf) else None
                if w_sub is None:
                    # Construir matriz reduzida só com munis disponíveis
                    from libpysal.weights import w_subset
                    ids = df.index.tolist()
                    try:
                        w_red = w_subset(w, ids, silence_warnings=True)
                        w_red.transform = "r"
                    except Exception:
                        continue
                    w_use = w_red
                else:
                    w_use = w_sub
                try:
                    m = Moran(df["residuo"].values, w_use, permutations=N_PERMUTACOES, transformation="r")
                    rows.append({
                        "modelo": modelo, "ano": int(ano), "W": w_name,
                        "I": round(float(m.I), 4),
                        "EI": round(float(m.EI), 4),
                        "z": round(float(m.z_sim), 3),
                        "p_sim": round(float(m.p_sim), 4),
                        "n": len(df),
                    })
                except Exception as e:
                    print(f"    Moran {modelo} {ano} {w_name}: {e}")
    return pd.DataFrame(rows)


def plotar_lisa(gdf, residuos_ano: pd.DataFrame, modelo: str, ano: int, w) -> Path | None:
    """Mapa LISA: 5 cores (HH, LL, HL, LH, n.s.)."""
    df = gdf.merge(residuos_ano[["cd_mun", "residuo"]], on="cd_mun", how="inner")
    df = df.dropna(subset=["residuo"])
    if len(df) < 50:
        return None

    from libpysal.weights import w_subset
    ids = df.index.tolist()
    try:
        w_red = w_subset(w, ids, silence_warnings=True)
        w_red.transform = "r"
    except Exception:
        return None

    lm = Moran_Local(df["residuo"].values, w_red, permutations=N_PERMUTACOES, seed=SEED)
    df = df.copy()
    df["q"] = lm.q          # quadrante: 1=HH, 2=LH, 3=LL, 4=HL
    df["p"] = lm.p_sim
    df["sig"] = df["p"] < 0.05
    # Categoria
    cat_map = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}
    df["lisa_cat"] = df["q"].map(cat_map)
    df.loc[~df["sig"], "lisa_cat"] = "n.s."

    cores = {"HH": "#c0392b", "LL": "#1f618d", "HL": "#e67e22",
             "LH": "#5dade2", "n.s.": "#bdc3c7"}

    fig, ax = plt.subplots(figsize=(7, 7))
    for cat, color in cores.items():
        sub = df[df["lisa_cat"] == cat]
        if len(sub) > 0:
            sub.plot(ax=ax, color=color, edgecolor="white", linewidth=0.2,
                     label=f"{cat} (n={len(sub)})")
    ax.set_title(f"LISA — {modelo}\nAno {ano}", fontsize=10, loc="left")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_axis_off()
    fig.tight_layout()

    safe = modelo.replace("~", "_vs_").replace("delta_", "Δ")
    path = DIR_OUT / f"lisa_{safe}_{ano}.png"
    fig.savefig(path, bbox_inches="tight", dpi=180)
    plt.close(fig)
    return path


def rodar_spreg(df_ano: pd.DataFrame, y_col: str, x_cols: list[str], w,
                 nome_W: str) -> list[dict]:
    """OLS vs SAR (lag) vs SEM (error) para uma seção transversal."""
    sub = df_ano.dropna(subset=[y_col] + x_cols).reset_index(drop=True)
    if len(sub) < 100:
        return []

    # Reordenar W para bater com sub
    from libpysal.weights import w_subset
    ids = sub.index.tolist()
    try:
        w_red = w_subset(w, ids, silence_warnings=True)
        w_red.transform = "r"
    except Exception:
        return []

    y = sub[[y_col]].values
    X = sub[x_cols].values
    names = ["const"] + x_cols

    out = []
    try:
        ols = OLS(y, X, w=w_red, spat_diag=True, moran=True, name_x=x_cols,
                  name_y=y_col, name_w=nome_W, name_ds=f"painel_{nome_W}")
        out.append({
            "modelo": "OLS", "y": y_col, "x": "+".join(x_cols), "W": nome_W, "n": ols.n,
            "r2": round(float(ols.r2), 4),
            "aic": round(float(getattr(ols, "aic", np.nan)), 2),
            "schwarz": round(float(getattr(ols, "schwarz", np.nan)), 2),
            "moran_resid_I": round(float(getattr(ols, "moran_res", [np.nan, np.nan, np.nan])[0] if hasattr(ols, "moran_res") and ols.moran_res is not None else np.nan), 4),
            "lm_lag_p": round(float(ols.lm_lag[1]) if getattr(ols, "lm_lag", None) is not None else np.nan, 4),
            "lm_error_p": round(float(ols.lm_error[1]) if getattr(ols, "lm_error", None) is not None else np.nan, 4),
            "rho_or_lambda": np.nan,
        })
    except Exception as e:
        out.append({"modelo": "OLS", "erro": str(e)[:120]})

    try:
        sar = ML_Lag(y, X, w=w_red, name_x=x_cols, name_y=y_col, name_w=nome_W)
        out.append({
            "modelo": "SAR (Lag)", "y": y_col, "x": "+".join(x_cols), "W": nome_W, "n": sar.n,
            "r2": round(float(sar.pr2), 4),
            "aic": round(float(sar.aic), 2),
            "schwarz": round(float(sar.schwarz), 2),
            "moran_resid_I": np.nan,
            "lm_lag_p": np.nan, "lm_error_p": np.nan,
            "rho_or_lambda": round(float(sar.rho), 4),
        })
    except Exception as e:
        out.append({"modelo": "SAR (Lag)", "erro": str(e)[:120]})

    try:
        sem = ML_Error(y, X, w=w_red, name_x=x_cols, name_y=y_col, name_w=nome_W)
        out.append({
            "modelo": "SEM (Error)", "y": y_col, "x": "+".join(x_cols), "W": nome_W, "n": sem.n,
            "r2": round(float(sem.pr2), 4),
            "aic": round(float(sem.aic), 2),
            "schwarz": round(float(sem.schwarz), 2),
            "moran_resid_I": np.nan,
            "lm_lag_p": np.nan, "lm_error_p": np.nan,
            "rho_or_lambda": round(float(sem.lam), 4),
        })
    except Exception as e:
        out.append({"modelo": "SEM (Error)", "erro": str(e)[:120]})

    return out


def main() -> None:
    print("Carregando geometrias GO via geobr...")
    gdf = carregar_geometrias()
    print(f"  {len(gdf)} municipios (CRS={gdf.crs})")

    print("Construindo matrizes de pesos W...")
    pesos = montar_pesos(gdf)
    for name, w in pesos.items():
        print(f"  {name}: {w.n} unidades, {w.s0:.0f} links totais, mean_neighbors={w.mean_neighbors:.2f}")

    print("\nCarregando residuos do painel #22...")
    residuos = pd.read_csv(DIR_CORR / "painel_residuos.csv")
    print(f"  {len(residuos):,} residuos × {residuos['modelo'].nunique()} modelos × {residuos['ano'].nunique()} anos")

    print("\nMoran's I global por (modelo, ano, W)...")
    moran_df = moran_por_ano(residuos, gdf, pesos)
    moran_df = moran_df.sort_values(["modelo", "W", "ano"])
    out_moran = DIR_OUT / "moran_global.csv"
    moran_df.to_csv(out_moran, index=False)
    print(f"OK: {out_moran.name} ({len(moran_df)} linhas)")

    # Resumo: pares com Moran significativo
    sig = moran_df[moran_df["p_sim"] < 0.05]
    print(f"\n=== Moran I significativo (p<0.05): {len(sig)} de {len(moran_df)} ===")
    if len(sig):
        # Top 10
        top = sig.sort_values("I", ascending=False).head(10)
        for _, row in top.iterrows():
            print(f"  {row['modelo'][:55]:55s} ano={row['ano']} W={row['W']:5s} "
                  f"I={row['I']:+.4f} z={row['z']:+.2f} p={row['p_sim']:.3f}")

    # LISA para subset de focos (3 modelos × 3 anos representativos)
    print("\nGerando mapas LISA para modelos foco × anos significativos...")
    anos_lisa = sorted(moran_df["ano"].unique())[::3][:4]  # ~3-4 anos representativos
    n_lisa = 0
    for modelo in MODELOS_FOCO:
        for ano in anos_lisa:
            sub_resid = residuos[(residuos["modelo"] == modelo) & (residuos["ano"] == ano)]
            if len(sub_resid) < 50:
                continue
            try:
                path = plotar_lisa(gdf, sub_resid, modelo, ano, pesos["queen"])
                if path:
                    print(f"  OK: {path.name}")
                    n_lisa += 1
            except Exception as e:
                print(f"  ERRO LISA {modelo} {ano}: {e}")
    print(f"  Total: {n_lisa} mapas LISA")

    # Regressao espacial cross-section
    print(f"\nRegressao espacial (cross-section em {ANO_SPREG})...")
    taxas = pd.read_csv(DIR_DATA / "taxas_lulc_municipal.csv")
    socio = pd.read_parquet(DIR_DATA / "painel_unificado.parquet")
    socio_keep = ["cd_mun", "ano", "sicor_total_real_rs", "va_agro_real_rs"]
    socio = socio[socio_keep]
    socio = socio.sort_values(["cd_mun", "ano"])
    for c in ["sicor_total_real_rs", "va_agro_real_rs"]:
        socio[f"delta_{c}"] = socio.groupby("cd_mun")[c].diff() / 1e9

    df = taxas.merge(
        socio[["cd_mun", "ano", "delta_sicor_total_real_rs", "delta_va_agro_real_rs"]],
        on=["cd_mun", "ano"], how="left"
    )

    df_ano = df[df["ano"] == ANO_SPREG].copy()
    # Merge geometria
    df_ano = gdf.merge(df_ano, on="cd_mun", how="inner")
    print(f"  {len(df_ano)} munis em {ANO_SPREG}")

    spreg_results = []
    for y_col, x_cols in PARES_SPREG:
        for w_name, w in pesos.items():
            res = rodar_spreg(df_ano, y_col, x_cols, w, w_name)
            spreg_results.extend(res)

    spreg_df = pd.DataFrame(spreg_results)
    out_spreg = DIR_OUT / "modelos_espaciais.csv"
    spreg_df.to_csv(out_spreg, index=False)
    print(f"OK: {out_spreg.name} ({len(spreg_df)} modelos espaciais)")

    # Resumo OLS vs SAR vs SEM
    print("\n=== OLS vs SAR vs SEM (AIC menor = melhor) ===")
    if len(spreg_df) and "aic" in spreg_df.columns:
        for (y, w_name), grp in spreg_df.dropna(subset=["aic"]).groupby(["y", "W"]):
            print(f"\n  {y} [W={w_name}]:")
            for _, row in grp.iterrows():
                rho = row.get("rho_or_lambda", np.nan)
                rho_s = f"ρ/λ={rho:+.3f}" if not pd.isna(rho) else ""
                print(f"    {row['modelo']:14s} R²={row['r2']:.3f} AIC={row['aic']:.1f} BIC={row['schwarz']:.1f} {rho_s}")

    print(f"\nFeito — resultados em {DIR_OUT}")


if __name__ == "__main__":
    main()
