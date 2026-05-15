"""correlacoes_uf.py — Correlações LULC × socioeconômicas em nível UF
========================================================================

Correlaciona taxas de variação LULC (Pipeline #17) com variáveis
socioeconômicas (painel_unificado.parquet) no nível estadual.

Decisão D7: correlações em PRIMEIRAS DIFERENÇAS, nunca em níveis.
Inferência com erros padrão Newey-West (HAC).

Pares testados:
    - Slope/delta pastagem vs PIB agro, SICOR, bovinos
    - Slope/delta vegetação natural vs fogo, PIB
    - Slope/delta agricultura vs soja_ton, SICOR
    - Lags 0, 1, 2 anos

Saídas:
    outputs/correlacoes/uf_deltas.csv  — tabela de correlações
    outputs/correlacoes/uf_scatter_*.png — gráficos de dispersão
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "font.size": 10,
    "figure.facecolor": "white",
})

# ─────────────────────────── Config ───────────────────────────

# Pares LULC × socioeconômico para testar
PARES = [
    # (nome_lulc, nome_socio, label_lulc, label_socio)
    ("pastagem", "sicor_total_real_rs", "Slope pastagem (Mha/ano)", "Δ Crédito rural (R$ bi)"),
    ("pastagem", "pec_bovinos_cab", "Slope pastagem (Mha/ano)", "Δ Bovinos (mil cab)"),
    ("vegetacao_natural", "fogo_veg_nat_ha", "Slope veg. nativa (Mha/ano)", "Δ Fogo veg. nat. (kha)"),
    ("vegetacao_natural", "pib_real_rs", "Slope veg. nativa (Mha/ano)", "Δ PIB (R$ bi)"),
    ("agricultura", "agri_soja_ton", "Slope agricultura (Mha/ano)", "Δ Produção soja (kton)"),
    ("agricultura", "sicor_total_real_rs", "Slope agricultura (Mha/ano)", "Δ Crédito rural (R$ bi)"),
]

LAGS = [0, 1, 2]

# ─────────────────────────── Funções ───────────────────────────

def agregar_uf_socio() -> pd.DataFrame:
    """Agrega painel_unificado para nível UF por ano.

    PIB e VA agro UF vêm de fonte separada (IPEA Data, Contas Regionais
    encadeadas — `pib_uf_ipea_goias.csv`), 1985-2023 contíguo, em vez do
    agregado municipal SIDRA 5938 (que só existe 2002+). Os outros campos
    continuam vindo do painel municipal agregado.
    """
    df = pd.read_parquet(DIR_DATA / "painel_unificado.parquet")
    socio_cols = [
        "pec_bovinos_cab", "agri_soja_ton", "agri_milho_total_ton",
        "sicor_total_real_rs",
        "fogo_total_ha", "fogo_veg_nat_ha", "populacao",
        "agri_leite_mil_litros",
    ]
    grp = df.groupby("ano", as_index=False)[socio_cols].sum(min_count=1)

    # PIB e VA agro UF nativos do IPEA (série longa 1985-2023)
    pib_uf = pd.read_csv(DIR_DATA / "pib_uf_ipea_goias.csv")
    pib_uf = pib_uf[["ano", "pib_uf_real_rs", "va_agro_uf_real_rs"]].rename(
        columns={"pib_uf_real_rs": "pib_real_rs",
                 "va_agro_uf_real_rs": "va_agro_real_rs"}
    )
    grp = grp.merge(pib_uf, on="ano", how="left")
    return grp


def compute_deltas(df: pd.DataFrame, col: str) -> pd.Series:
    """Primeiras diferenças de uma série."""
    return df[col].diff()


def pearson_with_hac(x: pd.Series, y: pd.Series, maxlags: int = 2) -> dict:
    """Correlação de Pearson com p-valor via HAC (Newey-West)."""
    valid = x.notna() & y.notna()
    xv, yv = x[valid].values, y[valid].values
    n = len(xv)
    if n < 5:
        return {"r": np.nan, "p": np.nan, "n": n, "method": "insufficient"}
    r = np.corrcoef(xv, yv)[0, 1]
    # Regressão y ~ x com HAC para p-valor
    X = sm.add_constant(xv)
    try:
        model = sm.OLS(yv, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
        p = model.pvalues[1]
    except Exception:
        # Fallback: t-test simples
        from scipy import stats
        t_stat = r * np.sqrt((n - 2) / (1 - r**2 + 1e-10))
        p = 2 * stats.t.sf(abs(t_stat), df=n - 2)
    return {"r": round(r, 4), "p": round(p, 4), "n": n, "method": "Pearson+HAC"}


def spearman_safe(x: pd.Series, y: pd.Series) -> dict:
    """Correlação de Spearman."""
    valid = x.notna() & y.notna()
    xv, yv = x[valid].values, y[valid].values
    n = len(xv)
    if n < 5:
        return {"rho": np.nan, "p": np.nan, "n": n}
    from scipy import stats
    rho, p = stats.spearmanr(xv, yv)
    return {"rho": round(rho, 4), "p": round(p, 4), "n": n}


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    # Carregar taxas LULC
    print("Carregando taxas LULC (UF)...")
    taxas = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")

    # Carregar dados socioeconômicos UF
    print("Carregando painel unificado (agregado UF)...")
    socio = agregar_uf_socio()

    # Merge
    df = taxas.merge(socio, on="ano", how="left").sort_values("ano").reset_index(drop=True)

    # Calcular deltas (D7)
    print("Computando primeiras diferenças...")
    socio_cols = [c for c in socio.columns if c != "ano"]
    for col in socio_cols:
        df[f"delta_{col}"] = compute_deltas(df, col)

    # LULC deltas já existem ({g}_delta_mha), slopes já existem
    # Para correlação: usar slope_5a_trail como "velocidade" LULC
    # e delta_socio como "velocidade" socioeconômica

    # ── Tabela de correlações ──
    print("\nComputando correlações...")
    results = []

    for g_lulc, socio_col, label_l, label_s in PARES:
        slope_col = f"{g_lulc}_slope_5a_trail"
        delta_socio_col = f"delta_{socio_col}"
        delta_lulc_col = f"{g_lulc}_delta_mha"

        if slope_col not in df.columns or delta_socio_col not in df.columns:
            print(f"  Pulando {g_lulc} × {socio_col}: coluna ausente")
            continue

        for lag in LAGS:
            # Slope LULC vs Δsocio (lagged)
            x = df[slope_col]
            y = df[delta_socio_col].shift(-lag) if lag > 0 else df[delta_socio_col]

            res_pearson = pearson_with_hac(x, y)
            res_spearman = spearman_safe(x, y)

            results.append({
                "lulc_classe": g_lulc,
                "socio_var": socio_col,
                "lag": lag,
                "metrica_lulc": "slope_5a_trail",
                "metrica_socio": "delta",
                "pearson_r": res_pearson["r"],
                "pearson_p": res_pearson["p"],
                "spearman_rho": res_spearman["rho"],
                "spearman_p": res_spearman["p"],
                "n_obs": res_pearson["n"],
            })

        # Também: Δ LULC vs Δ socio (ambas velocidades)
        for lag in LAGS:
            x = df[delta_lulc_col]
            y = df[delta_socio_col].shift(-lag) if lag > 0 else df[delta_socio_col]

            res_pearson = pearson_with_hac(x, y)
            res_spearman = spearman_safe(x, y)

            results.append({
                "lulc_classe": g_lulc,
                "socio_var": socio_col,
                "lag": lag,
                "metrica_lulc": "delta",
                "metrica_socio": "delta",
                "pearson_r": res_pearson["r"],
                "pearson_p": res_pearson["p"],
                "spearman_rho": res_spearman["rho"],
                "spearman_p": res_spearman["p"],
                "n_obs": res_pearson["n"],
            })

    results_df = pd.DataFrame(results)

    # Salvar tabela
    out_csv = DIR_OUT / "uf_deltas.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"OK: {out_csv.name} ({len(results_df)} pares)")

    # ── Resumo ──
    print("\n=== Correlações significativas (p < 0.05) ===")
    sig = results_df[(results_df["pearson_p"] < 0.05) & results_df["pearson_r"].notna()]
    if len(sig) > 0:
        for _, row in sig.iterrows():
            print(f"  {row['lulc_classe']:20s} × {row['socio_var']:25s} "
                  f"lag={row['lag']} "
                  f"r={row['pearson_r']:+.3f} p={row['pearson_p']:.3f} "
                  f"({row['metrica_lulc']} vs {row['metrica_socio']})")
    else:
        print("  Nenhuma correlação significativa encontrada.")

    # ── Figuras ──
    print("\nGerando scatter plots...")
    for g_lulc, socio_col, label_l, label_s in PARES:
        slope_col = f"{g_lulc}_slope_5a_trail"
        delta_socio_col = f"delta_{socio_col}"

        if slope_col not in df.columns or delta_socio_col not in df.columns:
            continue

        valid = df[slope_col].notna() & df[delta_socio_col].notna()
        n_valid = valid.sum()
        if n_valid < 5:
            continue

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(df.loc[valid, slope_col],
                   df.loc[valid, delta_socio_col],
                   alpha=0.6, s=40, edgecolors="white", linewidths=0.5)

        # Anotar anos
        for _, row in df[valid].iterrows():
            ax.annotate(str(int(row["ano"])),
                       (row[slope_col], row[delta_socio_col]),
                       fontsize=6, alpha=0.5, ha="center", va="bottom")

        # Linha de regressão
        x_vals = df.loc[valid, slope_col].values
        y_vals = df.loc[valid, delta_socio_col].values
        X_reg = sm.add_constant(x_vals)
        try:
            model = sm.OLS(y_vals, X_reg).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
            x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
            y_line = model.predict(sm.add_constant(x_line))
            ax.plot(x_line, y_line, "r--", alpha=0.6, linewidth=1)
            r_val = np.corrcoef(x_vals, y_vals)[0, 1]
            p_val = model.pvalues[1]
            ax.text(0.05, 0.95, f"r = {r_val:.3f} (p = {p_val:.3f})",
                    transform=ax.transAxes, fontsize=9, va="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        except Exception:
            pass

        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.set_xlabel(label_l)
        ax.set_ylabel(label_s)
        ax.set_title(f"{g_lulc.replace('_', ' ').title()} × {socio_col.replace('_', ' ')}",
                     fontsize=11, loc="left")

        fig.tight_layout()
        path = DIR_OUT / f"uf_scatter_{g_lulc}_{socio_col}.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(f"OK: {path.name}")

    print(f"\nFeito — resultados em {DIR_OUT}")


if __name__ == "__main__":
    main()