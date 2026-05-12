"""calcular_taxas_lulc.py — Métricas anuais de variação LULC para Goiás (1985–2024)
====================================================================================

Computa delta, slope (trailing + centrada), erro padrão Newey-West e aceleração
para as 6 classes agregadas do sistema unificado (mesmo mapeamento de
gerar_mapas_lulc_gee_40anos.py). Mosaico (ID 21) é contabilizado separadamente.

Saídas:
    data/processed/taxas_lulc_goias.csv       — nível UF (40 linhas)
    data/processed/taxas_lulc_municipal.csv    — nível municipal (9.840 linhas)

Decisões metodológicas (vide plano):
    D1: Sistema unificado de 6 classes, Mosaico excluído
    D2: Fonte = mapbiomas_munis_goias.csv (não painel_unificado)
    D3: Slope trailing (t-4..t) e centrada (t-2..t+2)
    D4: Erro padrão com HAC Newey-West (maxlags=2)
    D5: Aceleração = slope_5a_trail[t] - slope_5a_trail[t-1]
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
ARQ_MAPBIOMAS = DIR_PROCESSED / "mapbiomas_munis_goias.csv"

ANO_MIN, ANO_MAX = 1985, 2024
JANELA = 5  # anos para OLS rolling

# D1: Mapeamento de classes — idêntico a gerar_mapas_lulc_gee_40anos.py
GRUPOS_LULC = {
    "vegetacao_natural": [3, 4, 12],
    "pastagem":           [15],
    "agricultura":        [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],
    "agua":               [31, 33],
    "area_urbana":        [24],
    "outros":             [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],
}
MOSAICO_ID = 21  # contabilizado separadamente, não entra nos 6 grupos

# Mapeamento reverso: class_id → nome do grupo
ID_PARA_GRUPO: dict[int, str] = {}
for nome, ids in GRUPOS_LULC.items():
    for cid in ids:
        ID_PARA_GRUPO[cid] = nome

NOMES_GRUPOS = list(GRUPOS_LULC.keys())


# ─────────────────────────── Agregação ───────────────────────────

def agregar_por_grupo(df: pd.DataFrame, nivel: str = "uf") -> pd.DataFrame:
    """Agrega area_ha por (ano[, cd_mun, nm_mun]) e grupo LULC.

    Mosaico (ID 21) e class_id=0 ('Outra') ficam como colunas separadas.
    """
    df = df.copy()
    df["grupo"] = df["class_id"].map(ID_PARA_GRUPO)

    # Mosaico separado
    df["mosaico"] = np.where(df["class_id"] == MOSAICO_ID, df["area_ha"], 0.0)

    # class_id=0 ('Outra') vai para 'outros'
    mask_outros_extra = (df["grupo"].isna()) & (df["class_id"] != MOSAICO_ID) & (df["class_id"] != 0)
    # class_id=0 também para 'outros' se tiver área
    mask_zero = (df["class_id"] == 0)
    df.loc[mask_zero, "grupo"] = "outros"
    df.loc[mask_outros_extra, "grupo"] = "outros"  # não deve acontecer em Goiás

    # Pivot: linhas = (ano[, cd_mun, nm_mun]), colunas = grupo + mosaico
    group_cols = ["ano"]
    if nivel == "municipal":
        group_cols = ["cd_mun", "nm_mun", "ano"]

    # Área por grupo
    area_grupo = df.groupby(group_cols + ["grupo"], as_index=False)["area_ha"].sum()
    pivot_grupo = area_grupo.pivot_table(
        index=group_cols, columns="grupo", values="area_ha", fill_value=0,
    ).reset_index()
    pivot_grupo.columns.name = None

    # Área do mosaico
    mosaico = df.groupby(group_cols, as_index=False)["mosaico"].sum()

    # Área total
    area_total = df.groupby(group_cols, as_index=False)["area_ha"].sum()
    area_total = area_total.rename(columns={"area_ha": "area_total_ha"})

    # Merge
    result = area_total.merge(pivot_grupo, on=group_cols, how="left")
    result = result.merge(mosaico, on=group_cols, how="left")

    # Garantir que todas as colunas de grupo existem
    for g in NOMES_GRUPOS:
        if g not in result.columns:
            result[g] = 0.0

    # Reordenar colunas
    extra_cols = [c for c in result.columns if c not in group_cols + NOMES_GRUPOS + ["mosaico", "area_total_ha"]]
    result = result[group_cols + ["area_total_ha"] + NOMES_GRUPOS + ["mosaico"] + extra_cols]

    return result


# ─────────────────────────── Slopes ───────────────────────────

def rolling_slope_hac(series: pd.Series, window: int = JANELA, maxlags: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """OLS rolling com erro padrão Newey-West (HAC).

    Retorna (slopes, se_nw) com NaN onde a janela é insuficiente.
    """
    n = len(series)
    slopes = np.full(n, np.nan)
    se_nw = np.full(n, np.nan)
    x_base = np.arange(window, dtype=float)
    x_mean = x_base.mean()
    ss_xx = np.sum((x_base - x_mean) ** 2)

    for i in range(window - 1, n):
        y = series.iloc[i - window + 1: i + 1].values.astype(float)
        if np.any(np.isnan(y)):
            continue
        x = x_base
        X = sm.add_constant(x)
        try:
            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
            slopes[i] = model.params[1]
            se_nw[i] = model.bse[1]
        except Exception:
            # fallback: OLS simples
            b = np.sum((x - x_mean) * (y - y.mean())) / ss_xx
            slopes[i] = b
            se_nw[i] = np.nan

    return slopes, se_nw


def computar_taxas(grupo_df: pd.DataFrame) -> pd.DataFrame:
    """Computa delta, slopes, SE e aceleração para cada grupo LULC.

    grupo_df deve ter colunas: ano + NOMES_GRUPOS + area_total_ha + mosaico.
    """
    df = grupo_df.sort_values("ano").reset_index(drop=True)
    anos = df["ano"].values
    n = len(anos)

    result_rows = []

    for idx in range(n):
        row: dict = {"ano": int(anos[idx])}

        for g in NOMES_GRUPOS:
            area_ha = df[g].values.astype(float)
            total_ha = df["area_total_ha"].values.astype(float)

            # Área em Mha e %
            area_mha = area_ha / 1e6
            pct = np.where(total_ha > 0, area_ha / total_ha * 100, np.nan)

            row[f"{g}_mha"] = round(area_mha[idx], 6)
            row[f"{g}_pct"] = round(pct[idx], 4) if not np.isnan(pct[idx]) else np.nan

            # Delta (variação ano-a-ano)
            if idx > 0:
                delta = area_mha[idx] - area_mha[idx - 1]
                row[f"{g}_delta_mha"] = round(delta, 6)
            else:
                row[f"{g}_delta_mha"] = np.nan

        # Slopes e SE (computados uma vez por grupo, depois distribuídos por ano)
        # Serão adicionados depois via rolling

        # Mosaico e total
        row["mosaico_mha"] = round(df["mosaico"].values[idx] / 1e6, 6)
        row["area_total_mha"] = round(df["area_total_ha"].values[idx] / 1e6, 6)

        result_rows.append(row)

    result = pd.DataFrame(result_rows)

    # Computar slopes por grupo
    for g in NOMES_GRUPOS:
        area_mha = df[g].values.astype(float) / 1e6

        # Slope trailing (t-4..t)
        slopes_trail, se_nw = rolling_slope_hac(pd.Series(area_mha), window=JANELA)
        result[f"{g}_slope_5a_trail"] = slopes_trail
        result[f"{g}_slope_se_nw"] = se_nw

        # Slope centrada (t-2..t+2)
        slopes_centr, _ = rolling_slope_hac_centr(pd.Series(area_mha), window=JANELA)
        result[f"{g}_slope_5a_centr"] = slopes_centr

        # Aceleração
        trail = pd.Series(slopes_trail)
        accel = trail.diff()
        result[f"{g}_aceleracao"] = accel.values

    return result


def rolling_slope_hac_centr(series: pd.Series, window: int = JANELA, maxlags: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """OLS rolling centrada em t (janela t-2..t+2).

    Retorna (slopes, se_nw) com NaN nas pontas.
    """
    n = len(series)
    slopes = np.full(n, np.nan)
    se_nw = np.full(n, np.nan)
    half = window // 2  # 2 para janela=5
    x_base = np.arange(window, dtype=float)
    x_mean = x_base.mean()
    ss_xx = np.sum((x_base - x_mean) ** 2)

    for i in range(half, n - half):
        y = series.iloc[i - half: i + half + 1].values.astype(float)
        if np.any(np.isnan(y)):
            continue
        X = sm.add_constant(x_base)
        try:
            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
            slopes[i] = model.params[1]
            se_nw[i] = model.bse[1]
        except Exception:
            b = np.sum((x_base - x_mean) * (y - y.mean())) / ss_xx
            slopes[i] = b

    return slopes, se_nw


# ─────────────────────────── Mesorregiões ───────────────────────────

def agregar_mesorregioes(taxas_muni: pd.DataFrame, mapa_meso: pd.DataFrame) -> pd.DataFrame:
    """Agrega taxas municipais por mesorregião.

    Soma as áreas por mesorregião e ano, depois recalcula pct, delta e slopes
    a partir do agregado (não média dos slopes municipais).
    """
    # Merge com mapeamento
    df = taxas_muni.merge(mapa_meso[["cd_mun", "cod_meso", "nm_meso"]],
                          on="cd_mun", how="left")

    # Soma áreas por mesorregião e ano
    group_cols = ["cod_meso", "nm_meso", "ano"]
    agg_dict = {}
    for g in NOMES_GRUPOS:
        agg_dict[f"{g}_mha"] = "sum"
    agg_dict["mosaico_mha"] = "sum"
    agg_dict["area_total_mha"] = "sum"

    meso_areas = df.groupby(group_cols).agg(agg_dict).reset_index()

    # Recalcular pct
    for g in NOMES_GRUPOS:
        meso_areas[f"{g}_pct"] = (
            meso_areas[f"{g}_mha"] / meso_areas["area_total_mha"] * 100
        ).round(4)

    # Recalcular delta
    meso_areas = meso_areas.sort_values(["cod_meso", "ano"]).reset_index(drop=True)
    for g in NOMES_GRUPOS:
        meso_areas[f"{g}_delta_mha"] = meso_areas.groupby("cod_meso")[f"{g}_mha"].diff()

    # Recalcular slopes
    results = []
    for cod_meso, grp in meso_areas.groupby("cod_meso"):
        grp = grp.sort_values("ano").reset_index(drop=True)
        nm_meso = grp["nm_meso"].iloc[0]

        for idx in range(len(grp)):
            row: dict = {"cod_meso": int(cod_meso), "nm_meso": nm_meso,
                         "ano": int(grp["ano"].iloc[idx])}

            for g in NOMES_GRUPOS:
                row[f"{g}_mha"] = grp[f"{g}_mha"].iloc[idx]
                row[f"{g}_pct"] = grp[f"{g}_pct"].iloc[idx]
                row[f"{g}_delta_mha"] = grp[f"{g}_delta_mha"].iloc[idx]

            # Slopes trailing
            for g in NOMES_GRUPOS:
                series = grp[f"{g}_mha"]
                slopes_trail, se_nw = rolling_slope_hac(series, window=JANELA)
                row[f"{g}_slope_5a_trail"] = slopes_trail[idx] if not np.isnan(slopes_trail[idx]) else np.nan
                row[f"{g}_slope_se_nw"] = se_nw[idx] if not np.isnan(se_nw[idx]) else np.nan

            row["mosaico_mha"] = grp["mosaico_mha"].iloc[idx]
            row["area_total_mha"] = grp["area_total_mha"].iloc[idx]
            results.append(row)

    return pd.DataFrame(results)


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Carregar dados
    print("[1/5] Carregando mapbiomas_munis_goias.csv...")
    df = pd.read_csv(ARQ_MAPBIOMAS)
    print(f"  {len(df):,} linhas, {df['cd_mun'].nunique()} municípios, "
          f"anos {df['ano'].min()}–{df['ano'].max()}")

    # ── Nível UF ──
    print("\n[2/5] Agregando para nível UF...")
    uf = agregar_por_grupo(df, nivel="uf")
    print(f"  UF: {len(uf)} anos, colunas: {list(uf.columns)}")

    # Validar soma
    for _, row in uf.iterrows():
        grupos_sum = sum(row[g] for g in NOMES_GRUPOS) + row["mosaico"]
        diff_pct = abs(grupos_sum - row["area_total_ha"]) / row["area_total_ha"] * 100
        if diff_pct > 0.5:
            print(f"  AVISO: ano {int(row['ano'])} — soma dos grupos + mosaico difere "
                  f"{diff_pct:.2f}% do total")

    print("\n[3/5] Computando taxas (UF)...")
    taxas_uf = computar_taxas(uf)

    # Salvar UF
    out_uf = DIR_PROCESSED / "taxas_lulc_goias.csv"
    taxas_uf.to_csv(out_uf, index=False, float_format="%.6f")
    print(f"  OK: {out_uf.name} ({len(taxas_uf)} linhas, {len(taxas_uf.columns)} colunas)")

    # ── Nível municipal ──
    print("\n[4/5] Computando taxas (municipal)...")
    muni = agregar_por_grupo(df, nivel="municipal")

    # Para municipal: apenas delta e slope_trail (sem centrada e aceleração)
    results_muni = []

    for cd_mun, grp in muni.groupby("cd_mun"):
        grp = grp.sort_values("ano").reset_index(drop=True)
        nm = grp["nm_mun"].iloc[0]
        n = len(grp)

        for idx in range(n):
            row: dict = {"cd_mun": int(cd_mun), "nm_mun": str(nm), "ano": int(grp["ano"].iloc[idx])}

            for g in NOMES_GRUPOS:
                area_mha = grp[g].values.astype(float) / 1e6
                total_ha = grp["area_total_ha"].values.astype(float)

                row[f"{g}_mha"] = round(area_mha[idx], 6)
                row[f"{g}_pct"] = round(
                    (grp[g].iloc[idx] / total_ha[idx] * 100) if total_ha[idx] > 0 else np.nan, 4
                )

                # Delta
                if idx > 0:
                    row[f"{g}_delta_mha"] = round(area_mha[idx] - area_mha[idx - 1], 6)
                else:
                    row[f"{g}_delta_mha"] = np.nan

            # Slopes por grupo (municipal: apenas trailing)
            for g in NOMES_GRUPOS:
                area_mha = grp[g].values.astype(float) / 1e6
                slopes_trail, se_nw = rolling_slope_hac(pd.Series(area_mha), window=JANELA)
                row[f"{g}_slope_5a_trail"] = round(slopes_trail[idx], 6) if not np.isnan(slopes_trail[idx]) else np.nan
                row[f"{g}_slope_se_nw"] = round(se_nw[idx], 6) if not np.isnan(se_nw[idx]) else np.nan

            row["mosaico_mha"] = round(grp["mosaico"].iloc[idx] / 1e6, 6)
            row["area_total_mha"] = round(total_ha[idx] / 1e6, 6)

            results_muni.append(row)

    taxas_muni = pd.DataFrame(results_muni)

    # Salvar municipal
    out_muni = DIR_PROCESSED / "taxas_lulc_municipal.csv"
    taxas_muni.to_csv(out_muni, index=False, float_format="%.6f")
    print(f"  OK: {out_muni.name} ({len(taxas_muni)} linhas, {len(taxas_muni.columns)} colunas)")

    # ── Nível mesorregião ──
    print("\n[5/5] Agregando por mesorregião...")
    mapa_meso = pd.read_csv(DIR_PROCESSED / "mapeamento_mesorregioes.csv")
    taxas_meso = agregar_mesorregioes(taxas_muni, mapa_meso)

    out_meso = DIR_PROCESSED / "taxas_lulc_mesorregioes.csv"
    taxas_meso.to_csv(out_meso, index=False, float_format="%.6f")
    print(f"  OK: {out_meso.name} ({len(taxas_meso)} linhas, {len(taxas_meso.columns)} colunas)")

    # ── Resumo ──
    print("\n" + "=" * 60)
    print("Resumo (UF, ano 2024):")
    for g in NOMES_GRUPOS:
        val = taxas_uf.loc[taxas_uf["ano"] == 2024, f"{g}_pct"].values[0]
        slope = taxas_uf.loc[taxas_uf["ano"] == 2024, f"{g}_slope_5a_trail"].values[0]
        print(f"  {g:20s}: {val:6.2f}%  slope_5a={slope:+.4f} Mha/ano")

    mosaico_val = taxas_uf.loc[taxas_uf["ano"] == 2024, "mosaico_mha"].values[0]
    total_val = taxas_uf.loc[taxas_uf["ano"] == 2024, "area_total_mha"].values[0]
    print(f"  {'mosaico':20s}: {mosaico_val:.4f} Mha")
    print(f"  {'total':20s}: {total_val:.4f} Mha")

    print("\nFeito.")


if __name__ == "__main__":
    main()