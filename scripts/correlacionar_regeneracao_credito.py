"""correlacionar_regeneracao_credito.py — regeneração (pasto->floresta) × variáveis
socioeconômicas (crédito, fogo, rebanho, soja), muni-ano.

Variável-dependente (3 versões):
  regen_f  = pasto->floresta(3)   [regeneração real, lenhosa]
  regen_s  = pasto->savana(4)     [oscilação de borda, ruído de classificador]
  d_floresta = Δ lulc_floresta_nativa_ha   [proxy de estoque, denso, líquido]

Variáveis-explicativas (painel_unificado):
  credit  = sicor_total_real_rs
  fire    = fogo_veg_nat_ha
  cattle  = pec_bovinos_cab
  soy     = lulc_soja_ha

Método:
  A. Primeiras diferenças dentro do município (D7 — tira o efeito de tamanho/FE):
     Δy_it vs Δx_it, Pearson sobre o painel.
  B. Por ATO (I=1986-2000, II=2001-2019, III=2020-2024): regen somada, x médio,
     normalizado por pastagem; Pearson entre muni×ato + Δ dentro do muni entre atos.
  C. Lag: Δx_{t-1} vs Δy_t  (crédito precede regeneração?).

Saída: outputs/correlacoes/regeneracao_credito.csv + resumo no stdout.
"""
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REGEN = ROOT / "data" / "processed" / "regeneracao_muni_ano.csv"
PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
OUT = ROOT / "outputs" / "correlacoes" / "regeneracao_credito.csv"

ATOS = {"I": (1986, 2000), "II": (2001, 2019), "III": (2020, 2024)}
X_VARS = {"credit": "sicor_total_real_rs", "fire": "fogo_veg_nat_ha",
          "cattle": "pec_bovinos_cab", "soy": "lulc_soja_ha"}
Y_VARS = {"regen_f": "pasto_floresta_ha", "regen_s": "pasto_savana_ha",
          "d_floresta": None}  # None = derivado do painel


def pearson(a, b):
    m = ~(np.isnan(a) | np.isnan(b) | np.isinf(a) | np.isinf(b))
    if m.sum() < 30:
        return (np.nan, int(m.sum()))
    aa, bb = a[m], b[m]
    if aa.std() == 0 or bb.std() == 0:
        return (np.nan, int(m.sum()))
    return (float(np.corrcoef(aa, bb)[0, 1]), int(m.sum()))


def main() -> None:
    regen = pd.read_csv(REGEN)
    painel = pd.read_parquet(PAINEL)
    cols = ["cd_mun", "nm_mun", "ano", "sicor_total_real_rs", "fogo_veg_nat_ha",
            "pec_bovinos_cab", "lulc_soja_ha", "lulc_pastagem_ha",
            "lulc_floresta_nativa_ha"]
    painel = painel[cols].copy()

    # Reindexa regen para grade completa muni×ano (fill 0): o CSV só tem linhas
    # onde houve transição; sem isso, groupby.diff() pularia anos e daria diffs
    # de janelas arbitrárias. Sem transição = 0 ha de regeneração.
    ha_cols = ["pasto_floresta_ha", "pasto_savana_ha", "pasto_campo_ha",
               "floresta_pasto_ha", "savana_pasto_ha", "campo_pasto_ha"]
    munis = sorted(regen["cd_mun"].unique())
    anos = range(int(regen["ano"].min()), int(regen["ano"].max()) + 1)
    full = pd.MultiIndex.from_product([munis, anos], names=["cd_mun", "ano"]).to_frame(index=False)
    regen = full.merge(regen, on=["cd_mun", "ano"], how="left")
    regen[ha_cols] = regen[ha_cols].fillna(0.0)

    # proxy de estoque: Δfloresta dentro do muni
    painel = painel.sort_values(["cd_mun", "ano"])
    painel["d_floresta"] = painel.groupby("cd_mun")["lulc_floresta_nativa_ha"].diff()

    df = regen.merge(painel, on=["cd_mun", "ano"], how="left", suffixes=("", "_p"))
    if "nm_mun" not in df.columns:
        df["nm_mun"] = df.get("nm_mun_p", "")
    df = df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)

    # --- primeira diferença dentro do muni (D7) ---
    for c in list(X_VARS.values()) + ["pasto_floresta_ha", "pasto_savana_ha",
                                      "d_floresta", "lulc_pastagem_ha"]:
        df[f"d_{c}"] = df.groupby("cd_mun")[c].diff()

    linhas = []

    def reg(nome, y_col, x_col, janela, metodo):
        r, n = pearson(df[y_col].to_numpy(), df[x_col].to_numpy())
        linhas.append({"metodo": metodo, "janela": janela, "y": nome, "x": x_col,
                       "r": r, "n": n})

    print("═" * 78)
    print("A. PRIMEIRAS DIFERENÇAS dentro do muni (Δy_t vs Δx_t) — anual")
    print("═" * 78)
    print(f"{'y':12s} {'x':28s} {'r':>8s} {'n':>7s}")
    for yn, yc in [("regen_f", "d_pasto_floresta_ha"),
                   ("regen_s", "d_pasto_savana_ha"),
                   ("d_floresta", "d_d_floresta")]:
        for xn, xc in X_VARS.items():
            reg(yn, yc, f"d_{xc}", "anual", "D7_anual")
            print(f"{yn:12s} Δd_{xn:24s} {linhas[-1]['r']:8.3f} {linhas[-1]['n']:7d}")

    print("\n" + "═" * 78)
    print("C. LAG: Δx_{t-1} vs Δy_t  (crédito/fogo/rebanho/soja precede regeneração?)")
    print("═" * 78)
    for yn, yc in [("regen_f", "d_pasto_floresta_ha"),
                   ("regen_s", "d_pasto_savana_ha")]:
        for xn, xc in X_VARS.items():
            df[f"lag_{xc}"] = df.groupby("cd_mun")[f"d_{xc}"].shift(1)
            reg(yn + "_lag", yc, f"lag_{xc}", "anual", "D7_lag1")
            print(f"{yn:12s} Δd_{xn}(t-1){'':<14s} {linhas[-1]['r']:8.3f} {linhas[-1]['n']:7d}")

    # --- por ATO: regen somada, x médio, normalizado por pastagem média ---
    print("\n" + "═" * 78)
    print("B. POR ATO (regen somada no ato, x médio no ato, /pastagem média) — cross-seção")
    print("═" * 78)
    df["ato"] = pd.cut(df["ano"], bins=[1985, 2000, 2019, 2024],
                      labels=["I", "II", "III"], include_lowest=True)
    agg = df.groupby(["cd_mun", "ato"], observed=True).agg(
        regen_f=("pasto_floresta_ha", "sum"),
        regen_s=("pasto_savana_ha", "sum"),
        credit=("sicor_total_real_rs", "mean"),
        fire=("fogo_veg_nat_ha", "mean"),
        cattle=("pec_bovinos_cab", "mean"),
        soy=("lulc_soja_ha", "mean"),
        pasto=("lulc_pastagem_ha", "mean"),
    ).reset_index()
    for c in ["regen_f", "regen_s", "credit", "fire", "cattle", "soy"]:
        agg[f"{c}_p"] = agg[c] / agg["pasto"]  # normalizado por pastagem
    print(f"{'y':12s} {'x':22s} {'r':>8s} {'n':>7s}   (cross-seção muni×ato)")
    for yn in ["regen_f_p", "regen_s_p"]:
        for xn in ["credit_p", "fire_p", "cattle_p", "soy_p"]:
            r, n = pearson(agg[yn].to_numpy(), agg[xn].to_numpy())
            linhas.append({"metodo": "ato_cross", "janela": "ato", "y": yn,
                           "x": xn, "r": r, "n": n})
            print(f"{yn:12s} {xn:22s} {r:8.3f} {n:7d}")

    # Δ dentro do muni entre atos (I->II, II->III)
    print("\nΔ dentro do muni entre atos (remove tamanho):")
    agg_w = agg.pivot(index="cd_mun", columns="ato",
                      values=["regen_f", "regen_s", "credit", "fire", "cattle", "soy"])
    print(f"{'y':12s} {'x':22s} {'r':>8s} {'n':>7s}")
    for yn in ["regen_f", "regen_s"]:
        for xn in ["credit", "fire", "cattle", "soy"]:
            dy = (agg_w[(yn, "II")] - agg_w[(yn, "I")]).to_numpy()
            dy2 = (agg_w[(yn, "III")] - agg_w[(yn, "II")]).to_numpy()
            dy = np.concatenate([dy, dy2])
            dx = np.concatenate([
                (agg_w[(xn, "II")] - agg_w[(xn, "I")]).to_numpy(),
                (agg_w[(xn, "III")] - agg_w[(xn, "II")]).to_numpy()])
            r, n = pearson(dy, dx)
            linhas.append({"metodo": "ato_dentro", "janela": "ato", "y": yn,
                           "x": xn, "r": r, "n": n})
            print(f"{yn:12s} Δ{xn:22s} {r:8.3f} {n:7d}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(linhas).to_csv(OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()