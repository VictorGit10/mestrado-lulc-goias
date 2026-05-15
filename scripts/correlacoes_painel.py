"""correlacoes_painel.py — Painel municipal 2-way FE (D8)
========================================================

Regressão em painel com efeitos fixos de entidade (município)
e tempo (ano), SE clusterizado por município.

Especificação: Δlulc_it = α_i + γ_t + β·Δx_it + ε_it

Decisão D7: todas as variáveis em primeiras diferenças.
Decisão D8: PanelOLS com entity_effects + time_effects.

Janela plena: 2013–2021 (LULC + pecuária + PIB + SICOR completos).
Janela estendida: 2002–2023 (LULC + pecuária + PIB, sem SICOR).

Saídas:
    outputs/correlacoes/painel_2fe.csv          — tabela de β com SE (univariada)
    outputs/correlacoes/painel_multivariada.csv — β simultâneos por classe LULC
    outputs/correlacoes/painel_residuos.csv     — resíduos para Moran's I
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# ─────────────────────────── Config ───────────────────────────

# (y_lulc, x_socio, label_y, label_x)
PARES = [
    ("pastagem_delta_mha", "delta_sicor_total_real_rs", "Δ Pastagem (Mha)", "Δ Crédito rural (R$ bi)"),
    ("pastagem_delta_mha", "delta_pec_bovinos_cab", "Δ Pastagem (Mha)", "Δ Bovinos (mil cab)"),
    ("pastagem_delta_mha", "delta_va_agro_real_rs", "Δ Pastagem (Mha)", "Δ VA agropecuária (R$ bi)"),
    ("vegetacao_natural_delta_mha", "delta_fogo_veg_nat_ha", "Δ Veg. nativa (Mha)", "Δ Fogo veg. nat. (kha)"),
    ("vegetacao_natural_delta_mha", "delta_pib_real_rs", "Δ Veg. nativa (Mha)", "Δ PIB (R$ bi)"),
    ("agricultura_delta_mha", "delta_agri_soja_ton", "Δ Agricultura (Mha)", "Δ Produção soja (kton)"),
    ("agricultura_delta_mha", "delta_sicor_total_real_rs", "Δ Agricultura (Mha)", "Δ Crédito rural (R$ bi)"),
    ("agricultura_delta_mha", "delta_va_agro_real_rs", "Δ Agricultura (Mha)", "Δ VA agropecuária (R$ bi)"),
]

JANELA_PLENA = (2013, 2021)
JANELA_ESTENDIDA = (2002, 2023)

# Modelos multivariados — covariáveis simultâneas por classe LULC
MODELOS_MULTIVARIADA = [
    ("pastagem_delta_mha", [
        "delta_sicor_total_real_rs", "delta_pec_bovinos_cab",
        "delta_va_agro_real_rs", "delta_fogo_total_ha",
    ]),
    ("vegetacao_natural_delta_mha", [
        "delta_fogo_veg_nat_ha", "delta_sicor_total_real_rs",
        "delta_va_agro_real_rs",
    ]),
    ("agricultura_delta_mha", [
        "delta_agri_soja_ton", "delta_sicor_total_real_rs",
        "delta_va_agro_real_rs", "delta_pec_bovinos_cab",
    ]),
]


# ─────────────────────────── Funções ───────────────────────────

def preparar_painel() -> pd.DataFrame:
    """Monta painel municipal com deltas LULC e socioeconômicos."""
    # Taxas LULC municipal
    taxas = pd.read_csv(DIR_DATA / "taxas_lulc_municipal.csv")

    # Painel unificado (socioeconômicos)
    socio = pd.read_parquet(DIR_DATA / "painel_unificado.parquet")

    # Manter apenas colunas socioeconômicas relevantes
    socio_cols = [
        "pec_bovinos_cab", "agri_soja_ton", "agri_milho_total_ton",
        "pib_real_rs", "va_agro_real_rs", "sicor_total_real_rs",
        "fogo_total_ha", "fogo_veg_nat_ha", "populacao",
    ]
    keep_cols = ["cd_mun", "nm_mun", "ano"] + [c for c in socio_cols if c in socio.columns]
    socio = socio[keep_cols]

    # Merge
    df = taxas.merge(socio, on=["cd_mun", "nm_mun", "ano"], how="left")

    # Ordenar para painel
    df = df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)

    # Primeiras diferenças das variáveis socioeconômicas (D7)
    for col in socio_cols:
        if col in df.columns:
            df[f"delta_{col}"] = df.groupby("cd_mun")[col].diff()

    # LULC deltas já existem como {g}_delta_mha

    # Converter unidades para facilitar leitura
    # SICOR: R$ → R$ bilhões
    if "delta_sicor_total_real_rs" in df.columns:
        df["delta_sicor_total_real_rs"] = df["delta_sicor_total_real_rs"] / 1e9
    # PIB: R$ → R$ bilhões
    if "delta_pib_real_rs" in df.columns:
        df["delta_pib_real_rs"] = df["delta_pib_real_rs"] / 1e9
    # VA agro: R$ → R$ bilhões
    if "delta_va_agro_real_rs" in df.columns:
        df["delta_va_agro_real_rs"] = df["delta_va_agro_real_rs"] / 1e9
    # Bovinos: cab → mil cab
    if "delta_pec_bovinos_cab" in df.columns:
        df["delta_pec_bovinos_cab"] = df["delta_pec_bovinos_cab"] / 1e3
    # Soja: ton → kton
    if "delta_agri_soja_ton" in df.columns:
        df["delta_agri_soja_ton"] = df["delta_agri_soja_ton"] / 1e3
    # Fogo: ha → kha
    if "delta_fogo_veg_nat_ha" in df.columns:
        df["delta_fogo_veg_nat_ha"] = df["delta_fogo_veg_nat_ha"] / 1e3

    return df


def rodar_painel(df: pd.DataFrame, y_col: str, x_col: str,
                 janela: tuple[int, int]) -> dict | None:
    """Ajusta PanelOLS com 2-way FE para um par de variáveis."""
    from linearmodels.panel import PanelOLS

    # Filtrar janela
    sub = df[(df["ano"] >= janela[0]) & (df["ano"] <= janela[1])].copy()

    # Apenas obs com y e x válidos
    sub = sub.dropna(subset=[y_col, x_col])

    if len(sub) < 100:
        return None

    # Montar painel multi-index
    sub = sub.set_index(["cd_mun", "ano"])

    try:
        mod = PanelOLS(
            sub[y_col],
            sub[[x_col]],
            entity_effects=True,
            time_effects=True,
            check_rank=False,
        )
        res = mod.fit(cov_type="clustered", cluster_entity=True)

        return {
            "y_var": y_col,
            "x_var": x_col,
            "janela": f"{janela[0]}–{janela[1]}",
            "beta": round(res.params[x_col], 4),
            "se": round(res.std_errors[x_col], 4),
            "t": round(res.tstats[x_col], 2),
            "p": round(res.pvalues[x_col], 4),
            "n_obs": int(res.nobs),
            "n_entities": int(sub.index.get_level_values(0).nunique()),
            "r2_within": round(res.rsquared_within, 4) if res.rsquared_within is not None else np.nan,
            "r2_overall": round(res.rsquared_overall, 4) if res.rsquared_overall is not None else np.nan,
        }
    except Exception as e:
        return {"y_var": y_col, "x_var": x_col, "janela": f"{janela[0]}–{janela[1]}",
                "erro": str(e)[:80]}


def rodar_painel_multivariado(df: pd.DataFrame, y_col: str, x_cols: list[str],
                               janela: tuple[int, int]) -> dict | None:
    """PanelOLS 2-way FE com múltiplas covariáveis simultâneas.

    Especificação: Δy_it = α_i + γ_t + Σ_k β_k · Δx_k_it + ε
    SE clusterizado por município.
    """
    from linearmodels.panel import PanelOLS

    sub = df[(df["ano"] >= janela[0]) & (df["ano"] <= janela[1])].copy()
    sub = sub.dropna(subset=[y_col] + x_cols)

    if len(sub) < 100:
        return None

    sub = sub.set_index(["cd_mun", "ano"])

    try:
        mod = PanelOLS(
            sub[y_col],
            sub[x_cols],
            entity_effects=True,
            time_effects=True,
            check_rank=False,
        )
        res = mod.fit(cov_type="clustered", cluster_entity=True)

        out = {
            "y_var": y_col,
            "janela": f"{janela[0]}–{janela[1]}",
            "x_vars": ",".join(x_cols),
            "n_x": len(x_cols),
            "n_obs": int(res.nobs),
            "n_entities": int(sub.index.get_level_values(0).nunique()),
            "r2_within": round(res.rsquared_within, 4) if res.rsquared_within is not None else np.nan,
            "r2_overall": round(res.rsquared_overall, 4) if res.rsquared_overall is not None else np.nan,
        }
        for x in x_cols:
            out[f"beta_{x}"] = round(float(res.params[x]), 4)
            out[f"se_{x}"] = round(float(res.std_errors[x]), 4)
            out[f"p_{x}"] = round(float(res.pvalues[x]), 4)
        # VIF — usar dataframe na escala original (pré-set_index)
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            X = sub[x_cols].values
            vifs = [variance_inflation_factor(X, i) for i in range(len(x_cols))]
            for x, v in zip(x_cols, vifs):
                out[f"vif_{x}"] = round(float(v), 2)
        except Exception:
            pass
        return out
    except Exception as e:
        return {"y_var": y_col, "janela": f"{janela[0]}–{janela[1]}",
                "x_vars": ",".join(x_cols), "erro": str(e)[:120]}


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    print("Preparando painel municipal...")
    df = preparar_painel()
    n_munis = df["cd_mun"].nunique()
    n_anos = df["ano"].nunique()
    print(f"  {len(df):,} obs × {len(df.columns)} cols ({n_munis} munis, {n_anos} anos)")

    results = []

    for y_col, x_col, label_y, label_x in PARES:
        if y_col not in df.columns or x_col not in df.columns:
            print(f"  Pulando {y_col} × {x_col}: coluna ausente")
            continue

        for janela in [JANELA_PLENA, JANELA_ESTENDIDA]:
            print(f"  Panel: {y_col} ~ {x_col} [{janela[0]}–{janela[1]}]...", end=" ")
            res = rodar_painel(df, y_col, x_col, janela)
            if res is None:
                print("insuficiente")
                continue
            if "erro" in res:
                print(f"ERRO: {res['erro']}")
                results.append(res)
                continue

            sig = "*" if res["p"] < 0.05 else ""
            print(f"β={res['beta']:+.4f} SE={res['se']:.4f} p={res['p']:.4f} "
                  f"R²w={res['r2_within']:.3f} N={res['n_obs']}{sig}")
            results.append(res)

    # Salvar
    out_csv = DIR_OUT / "painel_2fe.csv"
    res_df = pd.DataFrame(results)
    res_df.to_csv(out_csv, index=False)
    print(f"\nOK: {out_csv.name} ({len(res_df)} modelos)")

    # Resíduos do melhor modelo (para Moran's I futuro)
    print("\nExportando resíduos para Moran's I...")
    residuos_rows = []
    for y_col, x_col, label_y, label_x in PARES:
        if y_col not in df.columns or x_col not in df.columns:
            continue
        res = rodar_painel(df, y_col, x_col, JANELA_PLENA)
        if res is None or "erro" in res:
            continue

        from linearmodels.panel import PanelOLS
        sub = df[(df["ano"] >= JANELA_PLENA[0]) & (df["ano"] <= JANELA_PLENA[1])].copy()
        sub = sub.dropna(subset=[y_col, x_col])
        sub_idx = sub.set_index(["cd_mun", "ano"])

        mod = PanelOLS(sub_idx[y_col], sub_idx[[x_col]],
                       entity_effects=True, time_effects=True, check_rank=False)
        fit = mod.fit(cov_type="clustered", cluster_entity=True)

        resids = fit.resids.reset_index()
        resids.columns = ["cd_mun", "ano", "residuo"]
        resids["modelo"] = f"{y_col}~{x_col}"
        residuos_rows.append(resids)

    if residuos_rows:
        residuos_df = pd.concat(residuos_rows, ignore_index=True)
        out_resid = DIR_OUT / "painel_residuos.csv"
        residuos_df.to_csv(out_resid, index=False)
        print(f"OK: {out_resid.name} ({len(residuos_df):,} resíduos)")

    # ── Painel multivariada ──
    # NOTA: incluir SICOR restringe a amostra a 2014+ (SICOR começa 2013, Δ a partir 2014),
    # mesmo na janela "estendida" 2002-2023. Por isso rodamos também uma variante
    # **sem SICOR** para aproveitar a janela completa.
    print("\nRodando especificação multivariada...")
    mv_results = []
    for y_col, x_cols in MODELOS_MULTIVARIADA:
        if y_col not in df.columns:
            print(f"  Pulando {y_col}: ausente")
            continue
        x_cols_ok = [c for c in x_cols if c in df.columns]
        if len(x_cols_ok) < 2:
            print(f"  {y_col}: < 2 covariáveis disponíveis, pulando")
            continue

        # Variante sem SICOR, para janela estendida 2002-2023 com mais N
        x_cols_no_sicor = [c for c in x_cols_ok if "sicor" not in c]

        for janela in [JANELA_PLENA, JANELA_ESTENDIDA]:
            print(f"  Multivariada: {y_col} ~ {'+'.join(c.replace('delta_','Δ') for c in x_cols_ok)} [{janela[0]}–{janela[1]}]...")
            mv = rodar_painel_multivariado(df, y_col, x_cols_ok, janela)
            if mv is None:
                print(f"    insuficiente"); continue
            if "erro" in mv:
                print(f"    ERRO: {mv['erro']}"); mv_results.append(mv); continue
            r2w = mv.get("r2_within", np.nan)
            print(f"    R²w={r2w:.3f} N={mv['n_obs']}")
            for x in x_cols_ok:
                b = mv.get(f"beta_{x}", np.nan)
                p = mv.get(f"p_{x}", np.nan)
                vif = mv.get(f"vif_{x}", np.nan)
                sig = "*" if (p is not None and not pd.isna(p) and p < 0.05) else ""
                print(f"      {x:35s} β={b:+.5f} p={p:.4f} VIF={vif:.2f}{sig}")
            mv_results.append(mv)

        # Variante sem SICOR, só na janela estendida (para ganhar N)
        if x_cols_no_sicor != x_cols_ok and len(x_cols_no_sicor) >= 2:
            print(f"  Multivariada (sem SICOR): {y_col} ~ {'+'.join(c.replace('delta_','Δ') for c in x_cols_no_sicor)} [{JANELA_ESTENDIDA[0]}–{JANELA_ESTENDIDA[1]}]...")
            mv_ns = rodar_painel_multivariado(df, y_col, x_cols_no_sicor, JANELA_ESTENDIDA)
            if mv_ns is not None and "erro" not in mv_ns:
                mv_ns["variant"] = "sem_sicor"
                r2w = mv_ns.get("r2_within", np.nan)
                print(f"    R²w={r2w:.3f} N={mv_ns['n_obs']}")
                for x in x_cols_no_sicor:
                    b = mv_ns.get(f"beta_{x}", np.nan)
                    p = mv_ns.get(f"p_{x}", np.nan)
                    vif = mv_ns.get(f"vif_{x}", np.nan)
                    sig = "*" if (p is not None and not pd.isna(p) and p < 0.05) else ""
                    print(f"      {x:35s} β={b:+.5f} p={p:.4f} VIF={vif:.2f}{sig}")
                mv_results.append(mv_ns)

    mv_df = pd.DataFrame(mv_results)
    out_mv = DIR_OUT / "painel_multivariada.csv"
    mv_df.to_csv(out_mv, index=False)
    print(f"OK: {out_mv.name} ({len(mv_df)} modelos multivariados)")

    # Comparação R² within univariado vs multivariado
    print("\n=== R² within: univariado (máx por Y) vs multivariado ===")
    for y_col, _ in MODELOS_MULTIVARIADA:
        uni = res_df[res_df["y_var"] == y_col].dropna(subset=["r2_within"]) if "r2_within" in res_df.columns else pd.DataFrame()
        for janela in [JANELA_PLENA, JANELA_ESTENDIDA]:
            jstr = f"{janela[0]}–{janela[1]}"
            r2_uni_max = uni[uni["janela"] == jstr]["r2_within"].max() if len(uni) else np.nan
            mv_row = mv_df[(mv_df["y_var"] == y_col) & (mv_df["janela"] == jstr)]
            r2_mv = mv_row["r2_within"].iloc[0] if len(mv_row) and "r2_within" in mv_row.columns else np.nan
            print(f"  {y_col:30s} [{jstr}] uni_max={r2_uni_max:.3f} mv={r2_mv:.3f}")

    # Resumo univariada
    print("\n=== Modelos univariados significativos (p < 0.05) ===")
    if len(res_df) > 0 and "p" in res_df.columns:
        sig = res_df[(res_df["p"] < 0.05) & res_df["p"].notna()]
        if len(sig) > 0:
            for _, row in sig.iterrows():
                print(f"  {row['y_var']:30s} ~ {row['x_var']:30s} "
                      f"[{row['janela']}] β={row['beta']:+.4f} p={row['p']:.4f}")
        else:
            print("  Nenhum modelo significativo.")
    else:
        print("  Nenhum modelo ajustado.")

    print(f"\nFeito — resultados em {DIR_OUT}")


if __name__ == "__main__":
    main()