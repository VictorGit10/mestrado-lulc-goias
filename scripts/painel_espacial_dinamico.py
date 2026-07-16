"""painel_espacial_dinamico.py — Pipeline #49 (Eixo C1): painel espacial dinâmico
================================================================================

MOTIVAÇÃO
---------
O Pipeline #24 mostrou que a autocorrelação espacial dos resíduos é ESTRUTURAL
(115/140 combinações modelo×ano×W com Moran's I significativo), mas o painel
principal (#22) é um 2-way FE SEM termo espacial — e o #24 só modelou o espaço
numa seção transversal (2020). Esta é a lacuna que a banca pode cutucar: "acharam
dependência espacial estrutural e não a modelaram nos modelos centrais".

Este pipeline fecha a lacuna: re-estima os canais-manchete do #22 num PAINEL
espacial dinâmico (Elhorst FE spatial lag / spatial error), sobre as 166 AMCs, e
pergunta se os coeficientes substantivos SOBREVIVEM ao termo espacial. Não é
história nova — é ESCUDO de robustez, na disciplina de D14/D16/#38.

DECISÃO DE MÉTODO
-----------------
- `spreg.Panel_FE_Lag`/`Panel_FE_Error` fazem FE de UMA via (só entidade, via
  demean_panel = kron(J_t, I_n)). O #22/#38 usam 2-way FE. Para casar, faço
  TIME-DEMEAN manual (subtrair a média anual entre AMCs) ANTES de passar ao spreg;
  em painel balanceado, (I−P_entidade)(I−P_tempo) = within de duas vias (P_ent·P_tempo
  = P_grande). Assim γ_t (choque macro comum, como no #38) é absorvido e o que resta
  é o gradiente + o spillover espacial ρ.
- Painel LONGO em formato time-major: y[0:N]=T0, y[N:2N]=T1… (exigência do spreg).
  W construído das AMCs na MESMA ordem (code_amc) da entidade dentro de cada bloco.
- Baseline não-espacial = OLS within (2-way demean) com SE cluster por AMC — o
  análogo direto do #22, para comparar o β antes/depois do espaço.
- LM tests (lag vs error, + robustos) escolhem a forma espacial.

MODELOS (canais substantivos do #22/#34)
- M1 Intensificação:  Δagricultura ~ Δ VA agro          janela 2003–2021
- M2 Crédito→pasto:   Δpastagem ~ Δ SICOR + Δ VA agro    janela 2014–2021
- M3 Substituição:    Δpastagem ~ Δagricultura           janela 1986–2024 (painel longo)

Rodar:  py -3.14 scripts/painel_espacial_dinamico.py
Saídas: data/processed/painel_espacial_dinamico.csv
        outputs/espacial/painel_espacial_beta.png
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats

import libpysal
from libpysal.weights import Queen, KNN
from spreg import (Panel_FE_Lag, Panel_FE_Error,
                   panel_LMlag, panel_LMerror, panel_rLMlag, panel_rLMerror)

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "espacial"
DIR_OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def carregar_dados() -> pd.DataFrame:
    """Junta taxas LULC (Δ área) + deltas socioeconômicos por AMC×ano."""
    tx = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")
    tx["code_amc"] = tx["code_amc"].astype(int)

    soc = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")
    soc["code_amc"] = soc["code_amc"].astype(int)
    soc = soc.sort_values(["code_amc", "ano"])
    for c in ["sicor_total_real_rs", "va_agro_real_rs"]:
        soc[f"delta_{c}"] = soc.groupby("code_amc")[c].diff() / 1e9  # bilhões R$
    keep = ["code_amc", "ano", "delta_sicor_total_real_rs", "delta_va_agro_real_rs"]
    df = tx.merge(soc[keep], on=["code_amc", "ano"], how="left")
    return df


def carregar_geom():
    import geopandas as gpd
    gdf = gpd.read_file(DIR_PROC / "amc_goias.gpkg")
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    return gdf[["code_amc", "geometry"]].to_crs(5880)


def montar_W(gdf, codes: list[int], tipo: str):
    """W das AMCs em 'codes', ordenadas por code_amc (mesma ordem do painel)."""
    sub = gdf[gdf["code_amc"].isin(codes)].sort_values("code_amc").reset_index(drop=True)
    if tipo == "queen":
        w = Queen.from_dataframe(sub, use_index=False)
    else:
        w = KNN.from_dataframe(sub, k=8)
    w.transform = "r"
    return w, sub["code_amc"].tolist()


# ---------------------------------------------------------------------------
# Painel balanceado + demeaning
# ---------------------------------------------------------------------------

def painel_balanceado(df, y_col, x_cols, anos):
    """Retorna (y, X, codes, T) em formato time-major (y[0:N]=T0…), balanceado."""
    cols = [y_col] + x_cols
    d = df[df["ano"].isin(anos)][["code_amc", "ano"] + cols].dropna(subset=cols)
    # manter só AMCs presentes em TODOS os anos da janela
    cont = d.groupby("code_amc")["ano"].nunique()
    full = cont[cont == len(anos)].index
    d = d[d["code_amc"].isin(full)].copy()
    d = d.sort_values(["ano", "code_amc"])  # time-major: ano externo, AMC interno
    codes = sorted(d["code_amc"].unique())
    N, T = len(codes), len(anos)
    assert len(d) == N * T, f"painel não-balanceado: {len(d)} != {N}*{T}"
    y = d[y_col].to_numpy().reshape(-1, 1)
    X = d[x_cols].to_numpy()
    return y, X, codes, T


def time_demean(arr, N, T):
    """Remove a média de cada período (entre AMCs). Array time-major (N*T,·)."""
    a = arr.reshape(T, N, -1)
    a = a - a.mean(axis=1, keepdims=True)
    return a.reshape(N * T, -1)


def within_2way(arr, N, T):
    """Within de 2 vias (tempo e entidade)."""
    a = arr.reshape(T, N, -1)
    a = a - a.mean(axis=1, keepdims=True)   # tempo
    a = a - a.mean(axis=0, keepdims=True)   # entidade
    return a.reshape(N * T, -1)


def ols_within_cluster(y, X, N, T):
    """OLS within 2-way + SE cluster por AMC. Baseline não-espacial (~#22)."""
    yd = within_2way(y, N, T)
    Xd = within_2way(X, N, T)
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    # cluster por entidade (mesma AMC ao longo de T): índices time-major
    XtX_inv = np.linalg.inv(Xd.T @ Xd)
    meat = np.zeros((Xd.shape[1], Xd.shape[1]))
    for i in range(N):
        idx = [t * N + i for t in range(T)]
        Xi, ui = Xd[idx], resid[idx]
        meat += Xi.T @ (ui @ ui.T) @ Xi
    G = N
    dof = G / (G - 1) * (N * T - 1) / (N * T - Xd.shape[1])
    vcov = dof * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(vcov)).reshape(-1, 1)
    z = beta / se
    p = 2 * (1 - stats.norm.cdf(np.abs(z)))
    return beta.ravel(), se.ravel(), p.ravel()


def zp(beta, se):
    z = beta / se
    return z, 2 * (1 - stats.norm.cdf(abs(z)))


# ---------------------------------------------------------------------------
# Estimação por modelo
# ---------------------------------------------------------------------------

MODELOS = [
    dict(id="M1", nome="Intensificação: Δagricultura ~ Δ VA agro",
         y="agricultura_delta_mha", x=["delta_va_agro_real_rs"],
         anos=list(range(2003, 2022)), Ws=["queen"]),
    dict(id="M2", nome="Crédito→pasto: Δpastagem ~ Δ SICOR + Δ VA agro",
         y="pastagem_delta_mha", x=["delta_sicor_total_real_rs", "delta_va_agro_real_rs"],
         anos=list(range(2014, 2022)), Ws=["queen"]),
    dict(id="M3", nome="Substituição local: Δpastagem ~ Δagricultura",
         y="pastagem_delta_mha", x=["agricultura_delta_mha"],
         anos=list(range(1986, 2025)), Ws=["queen", "knn8"]),
]


def rodar_modelo(df, gdf, m) -> list[dict]:
    out = []
    for wtipo in m["Ws"]:
        y, X, codes, T = painel_balanceado(df, m["y"], m["x"], m["anos"])
        N = len(codes)
        w, wcodes = montar_W(gdf, codes, wtipo)
        assert wcodes == codes, "ordem do W não bate com o painel"

        # baseline OLS within 2-way (cluster por AMC)
        b_ols, se_ols, p_ols = ols_within_cluster(y, X, N, T)

        # 2-way FE: time-demean e deixar o spreg fazer o entity-demean
        ytd = time_demean(y, N, T)
        Xtd = time_demean(X, N, T)

        # LM tests (escolha lag vs error)
        lm = {}
        for nome, fn in [("LM_lag", panel_LMlag), ("LM_err", panel_LMerror),
                         ("rLM_lag", panel_rLMlag), ("rLM_err", panel_rLMerror)]:
            try:
                r = fn(ytd, Xtd, w)
                lm[nome] = float(r[1])  # p-valor
            except Exception as e:
                lm[nome] = np.nan

        # spatial lag
        lag = Panel_FE_Lag(ytd, Xtd, w, name_y=m["y"], name_x=m["x"])
        b_lag = np.asarray(lag.betas).ravel()
        se_lag = np.asarray(lag.std_err).ravel()
        rho = float(lag.rho)
        # rho é o último; se_lag alinha (k+1)
        z_rho, p_rho = zp(rho, se_lag[-1])
        z_bl, p_bl = zp(b_lag[0], se_lag[0])  # 1º x = variável de interesse

        # spatial error
        err = Panel_FE_Error(ytd, Xtd, w, name_y=m["y"], name_x=m["x"])
        b_err = np.asarray(err.betas).ravel()
        se_err = np.asarray(err.std_err).ravel()
        lam = float(err.lam)
        z_be, p_be = zp(b_err[0], se_err[0])

        row = dict(modelo=m["id"], desc=m["nome"], W=wtipo, N=N, T=T, n_obs=N * T,
                   var=m["x"][0],
                   beta_ols=b_ols[0], se_ols=se_ols[0], p_ols=p_ols[0],
                   beta_lag=b_lag[0], se_lag=se_lag[0], p_lag=p_bl,
                   rho=rho, p_rho=float(p_rho), aic_lag=float(getattr(lag, "aic", np.nan)),
                   beta_err=b_err[0], se_err=se_err[0], p_err=p_be,
                   lam=lam, aic_err=float(getattr(err, "aic", np.nan)),
                   **lm)
        # veredito: β sobrevive (mesmo sinal + p<0.05) no modelo espacial preferido?
        prefere_lag = (lm.get("rLM_lag", 1) < lm.get("rLM_err", 1))
        b_pref = row["beta_lag"] if prefere_lag else row["beta_err"]
        p_pref = row["p_lag"] if prefere_lag else row["p_err"]
        row["forma_preferida"] = "lag" if prefere_lag else "error"
        row["sobrevive"] = bool(np.sign(b_pref) == np.sign(b_ols[0]) and p_pref < 0.05)
        out.append(row)
    return out


def figura(res: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    sub = res[res["W"] == "queen"].copy()
    fig, axes = plt.subplots(1, len(sub), figsize=(4.4 * len(sub), 4.2), squeeze=False)
    for ax, (_, r) in zip(axes[0], sub.iterrows()):
        labels = ["OLS within\n(#22)", "FE spatial\nlag", "FE spatial\nerror"]
        betas = [r["beta_ols"], r["beta_lag"], r["beta_err"]]
        ses = [r["se_ols"], r["se_lag"], r["se_err"]]
        x = np.arange(3)
        cols = ["#4a4a4a", "#1b7837", "#762a83"]
        ax.errorbar(x, betas, yerr=1.96 * np.array(ses), fmt="o", capsize=5,
                    color="none", ecolor="0.5")
        for xi, b, c in zip(x, betas, cols):
            ax.scatter(xi, b, s=70, color=c, zorder=3)
        ax.axhline(0, color="0.7", lw=1, ls="--")
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(f"{r['modelo']}: β de {r['var']}\nρ={r['rho']:+.2f} λ={r['lam']:+.2f}",
                     fontsize=9, loc="left")
        ax.set_ylabel("coeficiente (95% IC)")
        ax.grid(True, axis="y", alpha=0.25)
    fig.suptitle("Os canais do #22 sobrevivem ao painel espacial? (β antes × depois do termo espacial)",
                 fontsize=11.5, y=1.02)
    fig.tight_layout()
    p = DIR_OUT / "painel_espacial_beta.png"
    fig.savefig(p, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {p.relative_to(ROOT)}")


def main() -> None:
    print("=" * 74)
    print("Pipeline #49 (C1) — painel espacial dinâmico (Elhorst FE lag/error)")
    print("=" * 74)
    df = carregar_dados()
    gdf = carregar_geom()

    linhas = []
    for m in MODELOS:
        print(f"\n[{m['id']}] {m['nome']}  | anos {m['anos'][0]}–{m['anos'][-1]}")
        rows = rodar_modelo(df, gdf, m)
        for r in rows:
            linhas.append(r)
            print(f"  W={r['W']:5s} N={r['N']} T={r['T']} "
                  f"| β_OLS={r['beta_ols']:+.4f} (p={r['p_ols']:.3f}) "
                  f"→ β_lag={r['beta_lag']:+.4f} (p={r['p_lag']:.3f}), ρ={r['rho']:+.3f} "
                  f"| β_err={r['beta_err']:+.4f} (p={r['p_err']:.3f}), λ={r['lam']:+.3f}")
            print(f"        LM_lag p={r['LM_lag']:.3f} LM_err p={r['LM_err']:.3f} "
                  f"rLM_lag p={r['rLM_lag']:.3f} rLM_err p={r['rLM_err']:.3f} "
                  f"→ prefere {r['forma_preferida']}; β SOBREVIVE: {r['sobrevive']}")

    res = pd.DataFrame(linhas)
    saida = DIR_PROC / "painel_espacial_dinamico.csv"
    res.to_csv(saida, index=False, encoding="utf-8")
    print(f"\n[OK] {saida.relative_to(ROOT)} ({len(res)} linhas)")
    try:
        figura(res)
    except Exception as e:
        print(f"[fig] falhou: {e}")
    print("\nCONCLUÍDO — Pipeline #49 (C1).")


if __name__ == "__main__":
    main()
