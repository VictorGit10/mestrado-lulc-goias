"""drive_comum.py -- Pipeline #37B: o "drive comum" testado contra o LULC
==========================================================================

PERGUNTA QUE RESPONDE
---------------------
O #34 fechou a narrativa Sul->Norte num NULO causal (sem deslocamento direto) e
atribuiu tudo a um "drive comum" INFERIDO, nao testado. Aqui ele e MATERIALIZADO
e TESTADO: as viradas dos drivers macro exogenos (preco recebido = preco global x
cambio; credito) ANTECEDEM as inflexoes do LULC de Goias? Da substancia as quebras
orfas do #26 (pastagem 1991/2020) e ao trio Real-94 / Kandir-98 / cambio-99.

ABORDAGEM (3 camadas, nivel UF/anual -- o drive e exogeno e comum)
------------------------------------------------------------------
1. ALINHAMENTO (descritivo): para cada quebra empirica do LULC em GO (#26),
   o nivel e o momento (variacao no trienio anterior) de cada driver -- materializa
   as quebras orfas.
2. LEAD-LAG FORMAL: CCF + Granger (reusa deslocamento_espacial.py) entre
   Delta(driver) e a TAXA de conversao LULC (delta_mha). Inclui o teste REVERSO
   como PLACEBO DE EXOGENEIDADE: a TAXA LULC nao deve Granger-causar o preco
   internacional (que Goias nao move). Se causar, a serie esta mal construida.
3. DISTRIBUTED-LAG (HAC/Newey-West, reusa correlacoes_uf.py): TAXA LULC ~
   Delta(driver) em lags 0/1/2, e DECOMPOSICAO canal-preco vs canal-cambio
   (Delta preco_usd + Delta cambio_real no mesmo modelo).
4. (PONTE) o MESMO driver preve a expansao da agricultura no Sul E do pasto no
   Norte? -- liga o drive comum a reorganizacao Sul->Norte (item 5 da tese).

CONVENCAO (Decisao D7): tudo em PRIMEIRAS DIFERENCAS. A serie LULC ja e uma taxa
(delta_mha = Delta estoque); os drivers entram como Delta(nivel). Simetrico.

LIMITACAO HONESTA: N pequeno (~38 anos). Granger e precedencia PREDITIVA, nao
causalidade dura -- mesma cautela do #34. Credito e parcialmente endogeno (entra
como contexto). Precos USD nominais (ver coleta_drivers_macro.py).

ENTRADAS
    data/processed/drivers_macro_anual.csv        (#37A)
    data/processed/taxas_lulc_goias.csv           (#17)
    outputs/correlacoes/quebras_resultados.csv    (#26)
    data/processed/deslocamento_series_regionais.csv (#34, ponte)

SAIDAS
    data/processed/drive_comum_alinhamento.csv
    data/processed/drive_comum_leadlag.csv
    data/processed/drive_comum_distlag.csv
    data/processed/drive_comum_ponte_regional.csv
    outputs/drive_comum/timeline_drivers.png
    outputs/drive_comum/leadlag_ccf.png
    outputs/drive_comum/distlag_canais.png

COMO RODAR
    python scripts/drive_comum.py
    python scripts/drive_comum.py --sem-figuras

Depende de: #37A, #17, #26, #34. Quando foi feito: 2026-06-06.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "drive_comum"
DIR_OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS, MARCOS, CORES_ATO          # noqa: E402
from deslocamento_espacial import ccf_defasada, granger       # noqa: E402  (reuso #34)
from correlacoes_uf import pearson_with_hac                    # noqa: E402  (reuso #21)

# ─────────────────────────── Config ───────────────────────────

# Drivers exogenos (preco/cambio) + contexto (credito). Rotulos p/ figuras.
DRIVERS = {
    "preco_recebido_soja_idx": "Preço recebido soja (índice real)",
    "preco_recebido_boi_idx":  "Preço recebido boi (índice real)",
    "preco_soja_usd":          "Preço soja (US$, global)",
    "preco_boi_usd":           "Preço boi (US$, global)",
    "cambio_real_efetivo":     "Câmbio real efetivo (REER)",
    "credito_rural_go_real":   "Crédito rural GO (R$ real)",
}
# Drivers exogenos puros (entram no placebo de exogeneidade e na decomposicao)
EXOGENOS = ["preco_recebido_soja_idx", "preco_soja_usd", "preco_boi_usd", "cambio_real_efetivo"]

LULC = {
    "vegetacao_natural": "Vegetação natural",
    "pastagem":          "Pastagem",
    "agricultura":       "Agricultura",
}
MAX_LAG = 3
LAGS_DL = [0, 1, 2]


# ─────────────────────────── Carga ───────────────────────────

def carregar() -> pd.DataFrame:
    drv = pd.read_csv(DIR_PROC / "drivers_macro_anual.csv")
    tx  = pd.read_csv(DIR_PROC / "taxas_lulc_goias.csv")
    lulc_cols = {f"{c}_delta_mha": f"{c}_taxa" for c in LULC}
    tx = tx[["ano", *lulc_cols.keys()]].rename(columns=lulc_cols)
    df = drv.merge(tx, on="ano", how="inner").sort_values("ano").reset_index(drop=True)
    # Delta dos drivers (1a diferenca dos niveis) -- D7
    for d in DRIVERS:
        df[f"d_{d}"] = df[d].diff()
    return df


def quebras_go() -> pd.DataFrame:
    q = pd.read_csv(ROOT / "outputs" / "correlacoes" / "quebras_resultados.csv")
    return q[q["uf"] == "Goiás"].copy()


# ─────────────────────────── 1. Alinhamento ───────────────────────────

def alinhamento(df: pd.DataFrame, q: pd.DataFrame) -> pd.DataFrame:
    """Para cada quebra GO, nivel e momento (var. no trienio anterior) dos drivers."""
    idx = df.set_index("ano")
    linhas = []
    for _, r in q.iterrows():
        tau = int(r["ano_quebra"])
        for d, rot in DRIVERS.items():
            nivel = idx[d].get(tau, np.nan)
            ant   = idx[d].get(tau - 3, np.nan)
            var3  = (nivel - ant) if pd.notna(nivel) and pd.notna(ant) else np.nan
            var3_pct = (var3 / ant * 100) if pd.notna(var3) and ant not in (0, np.nan) else np.nan
            linhas.append({
                "classe_lulc": r["classe_lulc"], "ano_quebra": tau,
                "marco_proximo": r["marco_proximo_label"], "dist_marco": r["dist_anos"],
                "driver": d, "driver_rotulo": rot,
                "nivel_no_ano": round(float(nivel), 2) if pd.notna(nivel) else np.nan,
                "var_trienio_ant": round(float(var3), 2) if pd.notna(var3) else np.nan,
                "var_trienio_ant_pct": round(float(var3_pct), 1) if pd.notna(var3_pct) else np.nan,
            })
    return pd.DataFrame(linhas)


# ─────────────────────────── 2. Lead-lag formal ───────────────────────────

def leadlag(df: pd.DataFrame) -> pd.DataFrame:
    """CCF (pico) + Granger entre Delta(driver) e a taxa LULC, com reverso (placebo)."""
    linhas = []
    for d in DRIVERS:
        xcol = f"d_{d}"
        for c in LULC:
            ycol = f"{c}_taxa"
            sub = df[[xcol, ycol]].dropna()
            if len(sub) < 8:
                continue
            x, y = sub[xcol].to_numpy(), sub[ycol].to_numpy()
            # forward: driver -> LULC
            ccf = ccf_defasada(x, y, MAX_LAG)
            pico = ccf.loc[ccf["r"].abs().idxmax()]
            gf = granger(sub[xcol], sub[ycol], maxlag=2)
            # reverse: LULC -> driver (placebo de exogeneidade)
            gr = granger(sub[ycol], sub[xcol], maxlag=2)
            for g in gf:
                linhas.append({
                    "driver": d, "lulc": c, "sentido": "driver→LULC",
                    "ccf_lag_pico": int(pico["lag"]), "ccf_r_pico": pico["r"],
                    "granger_lag": g["lag"], "granger_p": g["p_valor"],
                    "exogeno": d in EXOGENOS,
                })
            for g in gr:
                linhas.append({
                    "driver": d, "lulc": c, "sentido": "LULC→driver (placebo)",
                    "ccf_lag_pico": int(pico["lag"]), "ccf_r_pico": pico["r"],
                    "granger_lag": g["lag"], "granger_p": g["p_valor"],
                    "exogeno": d in EXOGENOS,
                })
    return pd.DataFrame(linhas)


# ─────────────────────────── 3. Distributed-lag (HAC) ───────────────────────────

def _zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std()


def _ols_hac(y: pd.Series, X: pd.DataFrame, maxlags: int = 2) -> dict:
    """OLS multivariado com erros HAC (Newey-West). Retorna betas/p/R2."""
    valid = y.notna() & X.notna().all(axis=1)
    yv, Xv = y[valid], X[valid]
    if len(yv) < len(X.columns) + 4:
        return {}
    Xc = sm.add_constant(Xv)
    m = sm.OLS(yv.to_numpy(), Xc.to_numpy()).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    out = {"n": int(len(yv)), "r2": round(float(m.rsquared), 3)}
    names = ["const", *Xv.columns]
    for i, nm in enumerate(names):
        out[f"beta_{nm}"] = round(float(m.params[i]), 5)
        out[f"p_{nm}"]    = round(float(m.pvalues[i]), 4)
    return out


def distlag(df: pd.DataFrame) -> pd.DataFrame:
    """(a) lag-a-lag univariado HAC; (b) decomposicao canal preco vs cambio."""
    linhas = []
    # (a) univariado por lag (reusa pearson_with_hac)
    for d in DRIVERS:
        for c in LULC:
            for lag in LAGS_DL:
                x = df[f"d_{d}"].shift(lag)
                y = df[f"{c}_taxa"]
                res = pearson_with_hac(x, y)
                linhas.append({
                    "tipo": "univariado", "driver": d, "lulc": c, "lag": lag,
                    "r": res["r"], "p": res["p"], "n": res["n"],
                })
    uni = pd.DataFrame(linhas)

    # (b) decomposicao: TAXA LULC ~ d_preco_usd(lag*) + d_cambio_real(lag*).
    # Regressores PADRONIZADOS (z-score) -> betas COMPARAVEIS entre canais. Sem isto a
    # comparacao de amplitude e invalida: d(preco USD) tem DP ~3x maior que d(REER), o
    # que inflava o beta BRUTO do cambio sem que ele "dominasse" de fato (corrige a
    # leitura antiga "cambio domina em amplitude", que era artefato de unidade).
    zp = _zscore(df["d_preco_soja_usd"])
    zc = _zscore(df["d_cambio_real_efetivo"])
    dec = []
    for c in LULC:
        for lag in LAGS_DL:
            X = pd.DataFrame({
                "preco_usd": zp.shift(lag),
                "cambio_real": zc.shift(lag),
            })
            r = _ols_hac(df[f"{c}_taxa"], X)
            if r:
                dec.append({
                    "tipo": "decomposicao", "lulc": c, "lag": lag, "n": r["n"], "r2": r["r2"],
                    "beta_preco_usd": r["beta_preco_usd"], "p_preco_usd": r["p_preco_usd"],
                    "beta_cambio_real": r["beta_cambio_real"], "p_cambio_real": r["p_cambio_real"],
                })
    return uni, pd.DataFrame(dec)


# ─────────────────────────── 4. Ponte Sul→Norte ───────────────────────────

def ponte_regional(df: pd.DataFrame) -> pd.DataFrame:
    """O MESMO driver (preco recebido soja) preve Δagric_Sul E Δpasto/rebanho_Norte?"""
    arq = DIR_PROC / "deslocamento_series_regionais.csv"
    if not arq.exists():
        return pd.DataFrame()
    reg = pd.read_csv(arq)
    reg = reg.merge(df[["ano", "d_preco_recebido_soja_idx", "d_cambio_real_efetivo",
                        "d_credito_rural_go_real"]], on="ano", how="inner")
    alvos = {
        "agric_mha_Sul":     "Δ Agricultura Sul",
        "pasto_mha_Norte":   "Δ Pastagem Norte",
        "bovinos_mcab_Norte": "Δ Rebanho Norte",
    }
    drivers = ["d_preco_recebido_soja_idx", "d_cambio_real_efetivo", "d_credito_rural_go_real"]
    linhas = []
    for alvo, rot in alvos.items():
        reg[f"d_{alvo}"] = reg[alvo].diff()
        for drv in drivers:
            for lag in LAGS_DL:
                res = pearson_with_hac(reg[drv].shift(lag), reg[f"d_{alvo}"])
                linhas.append({
                    "alvo": alvo, "alvo_rotulo": rot, "driver": drv.replace("d_", "Δ"),
                    "lag": lag, "r": res["r"], "p": res["p"], "n": res["n"],
                })
    return pd.DataFrame(linhas)


# ─────────────────────────── Figuras ───────────────────────────

def fig_timeline(df: pd.DataFrame, q: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    anos_q = sorted(q["ano_quebra"].unique())
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    ax = axes[0]
    ax.plot(df["ano"], df["preco_recebido_soja_idx"], color="#1b7837", lw=2.2, label="Preço recebido soja (índice real)")
    ax.plot(df["ano"], df["cambio_real_efetivo"], color="#762a83", lw=1.6, ls="--", label="Câmbio real efetivo (REER)")
    ax.set_ylabel("Índice (real)")
    ax.set_title("Drivers exógenos vs quebras empíricas do LULC em Goiás (#26)", fontsize=12, fontweight="bold")

    ax2 = axes[1]
    ax2.plot(df["ano"], df["credito_rural_go_real"] / 1e9, color="#b35806", lw=2, label="Crédito rural GO (R$ bi, real)")
    ax2.axvspan(2013, df["ano"].max(), color="0.85", alpha=0.4, zorder=0, label="janela SICOR (2013+)")
    ax2.set_ylabel("R$ bilhões (dez/2024)")
    ax2.set_xlabel("Ano")

    for a in axes:
        # atos sombreados
        for k, v in ATOS.items():
            a.axvspan(v["inicio"], v["fim"], color=CORES_ATO[k], alpha=0.05, zorder=0)
        for ya in anos_q:
            a.axvline(ya, color="0.4", lw=0.8, ls=":", zorder=1)
        a.legend(fontsize=8, loc="upper left")
        a.grid(alpha=0.25)
    # rotular quebras no topo
    ymax = axes[0].get_ylim()[1]
    for ya in anos_q:
        axes[0].annotate(str(ya), (ya, ymax), fontsize=7, color="0.3", rotation=90, va="top", ha="right")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "timeline_drivers.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'timeline_drivers.png').relative_to(ROOT)}")


def fig_leadlag(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    pares = [("preco_recebido_soja_idx", "agricultura"),
             ("preco_recebido_soja_idx", "pastagem"),
             ("cambio_real_efetivo", "agricultura"),
             ("credito_rural_go_real", "pastagem")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for ax, (d, c) in zip(axes.flat, pares):
        sub = df[[f"d_{d}", f"{c}_taxa"]].dropna()
        ccf = ccf_defasada(sub[f"d_{d}"].to_numpy(), sub[f"{c}_taxa"].to_numpy(), MAX_LAG)
        cores = ["#1b7837" if l > 0 else ("#999999" if l == 0 else "#c0c0c0") for l in ccf["lag"]]
        ax.bar(ccf["lag"], ccf["r"], color=cores)
        ax.axhline(0, color="0.5", lw=0.6)
        ax.set_title(f"Δ {DRIVERS[d]}\n→ taxa {LULC[c]}", fontsize=9)
        ax.set_xlabel("lag (anos; >0 = driver lidera)")
        ax.set_ylabel("corr")
        ax.grid(alpha=0.25)
    fig.suptitle("Lead-lag (CCF): drivers macro × taxa de conversão LULC", fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "leadlag_ccf.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'leadlag_ccf.png').relative_to(ROOT)}")


def fig_distlag(dec: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    if dec.empty:
        return
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=False)
    for ax, c in zip(axes, LULC):
        sub = dec[dec["lulc"] == c]
        ax.plot(sub["lag"], sub["beta_preco_usd"], "o-", color="#1b7837", label="canal preço (US$)")
        ax.plot(sub["lag"], sub["beta_cambio_real"], "s--", color="#762a83", label="canal câmbio (REER)")
        for _, r in sub.iterrows():
            if r["p_preco_usd"] < 0.05:
                ax.annotate("*", (r["lag"], r["beta_preco_usd"]), color="#1b7837", fontsize=14)
            if r["p_cambio_real"] < 0.05:
                ax.annotate("*", (r["lag"], r["beta_cambio_real"]), color="#762a83", fontsize=14)
        ax.axhline(0, color="0.5", lw=0.6)
        ax.set_title(LULC[c], fontsize=10)
        ax.set_xlabel("lag (anos)")
        ax.set_xticks(LAGS_DL)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("β padronizado (taxa LULC por +1 DP do canal)")
    axes[-1].legend(fontsize=8)
    fig.suptitle("Decomposição canal preço vs câmbio (distributed-lag, HAC; β padronizado; * p<0,05)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "distlag_canais.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'distlag_canais.png').relative_to(ROOT)}")


# ─────────────────────────── Main ───────────────────────────

def main(sem_figuras: bool = False) -> None:
    df = carregar()
    q  = quebras_go()
    print(f"[carga] {len(df)} anos ({df['ano'].min()}-{df['ano'].max()}); "
          f"{len(q)} quebras GO ({sorted(q['ano_quebra'].unique())})\n")

    al = alinhamento(df, q)
    al.to_csv(DIR_PROC / "drive_comum_alinhamento.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_comum_alinhamento.csv ({len(al)} linhas)")

    ll = leadlag(df)
    ll.to_csv(DIR_PROC / "drive_comum_leadlag.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_comum_leadlag.csv ({len(ll)} linhas)")

    uni, dec = distlag(df)
    out_dl = pd.concat([uni, dec], ignore_index=True)
    out_dl.to_csv(DIR_PROC / "drive_comum_distlag.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_comum_distlag.csv ({len(out_dl)} linhas)")

    pr = ponte_regional(df)
    pr.to_csv(DIR_PROC / "drive_comum_ponte_regional.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_comum_ponte_regional.csv ({len(pr)} linhas)\n")

    # ── Resumo no console ──
    print("[lead-lag] Granger driver→LULC (lag de menor p) e placebo reverso:")
    for (d, c), sub in ll.groupby(["driver", "lulc"]):
        fwd = sub[sub["sentido"] == "driver→LULC"]
        rev = sub[sub["sentido"].str.contains("placebo")]
        pf = fwd["granger_p"].min() if len(fwd) else np.nan
        pr_ = rev["granger_p"].min() if len(rev) else np.nan
        pico = fwd["ccf_r_pico"].iloc[0] if len(fwd) else np.nan
        lagp = fwd["ccf_lag_pico"].iloc[0] if len(fwd) else np.nan
        flag = "  <<" if (pd.notna(pf) and pf < 0.05) else ""
        print(f"  {d:26s}→{c:18s} CCF pico lag={lagp:+d} r={pico:+.2f} | "
              f"Granger fwd p={pf:.3f} rev p={pr_:.3f}{flag}")

    print("\n[decomposição] canal preço vs câmbio (lag de maior |β| sig.):")
    if not dec.empty:
        for c in LULC:
            sub = dec[dec["lulc"] == c]
            best = sub.iloc[sub[["beta_preco_usd", "beta_cambio_real"]].abs().max(axis=1).argmax()]
            print(f"  {c:18s} lag{int(best['lag'])}: preço β={best['beta_preco_usd']:+.4f} "
                  f"(p={best['p_preco_usd']}) | câmbio β={best['beta_cambio_real']:+.4f} "
                  f"(p={best['p_cambio_real']}) | R²={best['r2']}")

    if not pr.empty:
        print("\n[ponte] Δpreço recebido soja → expansão regional (melhor lag por alvo):")
        sub = pr[pr["driver"] == "Δpreco_recebido_soja_idx"]
        for alvo, s in sub.groupby("alvo_rotulo"):
            b = s.loc[s["r"].abs().idxmax()]
            print(f"  {alvo:22s} lag{int(b['lag'])}: r={b['r']:+.2f} p={b['p']} (n={b['n']})")

    if not sem_figuras:
        print()
        fig_timeline(df, q)
        fig_leadlag(df)
        fig_distlag(dec)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Drive comum: drivers macro × LULC (#37B)")
    p.add_argument("--sem-figuras", action="store_true", help="pula a geração de PNGs")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        main(sem_figuras=args.sem_figuras)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
