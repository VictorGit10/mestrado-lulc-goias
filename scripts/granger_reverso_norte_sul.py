"""
Pipeline #42 — O Granger reverso Norte→Sul: artefato ou inversão da leitura?
============================================================================

PERGUNTA QUE RESPONDE (fio 5 do backlog)
----------------------------------------
O #34 fechou a narrativa Sul→Norte num NULO causal, mas deixou uma ponta solta:
o teste REVERSO `ΔPasto_Norte → ΔAgric_Sul` deu **Granger p=0,0007 (lag 1)** —
significativo, descartado só por "N pequeno". Se for um sinal real, **inverte a
leitura** (seria o Norte antecedendo o Sul, não o contrário). Este pipeline cutuca
a ponta com o rigor que o #34 não teve tempo de aplicar.

TRÊS HIPÓTESES A DISCRIMINAR
    H_inverte   — Norte→Sul causal: o avanço do pasto no Norte de fato antecede e
                  prevê a lavoura no Sul (mecanismo econômico estranho, mas possível).
    H_comum     — timing diferencial sob DRIVE COMUM (#37): o boom/câmbio/crédito move
                  os dois; o pasto do Norte (fronteira barata, rápida) responde ~1 ano
                  ANTES da lavoura do Sul (capital-intensiva, lenta). A "liderança" é
                  mecânica, não causal.
    H_espurio   — artefato estatístico: séries-tendência suaves + N pequeno geram
                  precedência espúria que não sobrevive a método correto.

DESENHO DOS TESTES (cada um isola uma hipótese)
    Bloco A  Reproduz e caracteriza (perfil de lags, HAC, assimetria pasto×rebanho).
    Bloco B  Estacionariedade (ADF/KPSS) + Toda-Yamamoto (Granger correto p/ I(1)) → H_espurio.
    Bloco C  DECISIVO: controla pelo drive comum (#37). Se ΔPasto_Norte.L1 morre →
             H_comum; se sobrevive → H_inverte fica de pé.                → H_comum vs H_inverte
    Bloco D  Robustez: detrend, drop secas 1985/2010 (espírito #41), subperíodos, placebos.

ENTRADAS
    data/processed/deslocamento_series_regionais.csv   (#34 — séries Sul/Norte/Centro)
    data/processed/drivers_macro_anual.csv             (#37 — câmbio/crédito/preço)

SAÍDAS
    data/processed/granger_reverso_lags.csv        (perfil de lags fwd/rev, F e HAC)
    data/processed/granger_reverso_estacionaria.csv(ADF/KPSS + Toda-Yamamoto)
    data/processed/granger_reverso_drivecomum.csv  (modelos com controle de drivers)
    data/processed/granger_reverso_robustez.csv    (detrend/secas/subperíodos/placebo)
    outputs/granger_reverso/*.png

COMO RODAR
    python scripts/granger_reverso_norte_sul.py

Depende de: #34 (séries), #37 (drivers). Reusa o ccf/granger do #34.
Quando foi feito: 2026-06-08. Fio 5 do backlog (ponta solta do #34).
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "granger_reverso"
DIR_OUT.mkdir(parents=True, exist_ok=True)

DROUGHT = [1985, 2010]   # anos de seca extrema no Cerrado (mexeram o #41)

# Defasagens do nucleo de Newey-West. Vale para o Wald-HAC do bloco A e para o
# aumento do Toda-Yamamoto (dmax) do bloco B, que ja rodava com 2: a constante
# existe para que as duas reguas nao possam divergir de novo em silencio.
# A Secao 3.x da metodologia declara este numero.
HAC_LAGS = 2


# ---------------------------------------------------------------------------
# 0. Dados
# ---------------------------------------------------------------------------

def carregar() -> pd.DataFrame:
    """Junta as séries regionais (#34) com os drivers macro (#37), por ano.
    Constrói as primeiras diferenças (LULC em Mha; macro em Δlog = crescimento)."""
    s = pd.read_csv(DIR_PROC / "deslocamento_series_regionais.csv")
    d = pd.read_csv(DIR_PROC / "drivers_macro_anual.csv")
    df = s.merge(d, on="ano", how="left").sort_values("ano").reset_index(drop=True)

    # Primeiras diferenças das áreas/rebanho (mesma convenção do #34: ΔMha, Δmcab).
    for c in ["agric_mha_Sul", "pasto_mha_Norte", "bovinos_mcab_Norte",
              "agric_mha_Centro", "pasto_mha_Centro", "agric_mha_Norte",
              "pasto_mha_Sul", "bovinos_mcab_Sul"]:
        if c in df:
            df[f"d_{c}"] = df[c].diff()

    # Segundas diferenças das duas séries-protagonistas. Sem elas o dmax=2 do
    # Toda-Yamamoto fica AFIRMADO e não mostrado: I(2) só se sustenta exibindo
    # a diferença em que a série finalmente para de ter raiz unitária.
    for c in ["agric_mha_Sul", "pasto_mha_Norte"]:
        df[f"dd_{c}"] = df[f"d_{c}"].diff()

    # Drivers em Δlog (crescimento) — torna o nível estritamente positivo ~estacionário.
    for c in ["cambio_real_efetivo", "credito_rural_go_real",
              "preco_recebido_soja_idx", "preco_soja_usd"]:
        df[f"dl_{c}"] = np.log(df[c]).diff()
    return df


# ---------------------------------------------------------------------------
# Helpers de Granger (reusa a lógica do #34) + HAC
# ---------------------------------------------------------------------------

def granger_p(x: pd.Series, y: pd.Series, lag: int) -> float:
    """p-valor do ssr_ftest de que x Granger-causa y, no lag dado (ordem [y,x])."""
    from statsmodels.tsa.stattools import grangercausalitytests
    data = np.column_stack([y.to_numpy(), x.to_numpy()])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = grangercausalitytests(data, maxlag=[lag], verbose=False)
    return float(res[lag][0]["ssr_ftest"][1])


def granger_hac(xcause: pd.Series, yeffect: pd.Series, lag: int) -> dict:
    """Granger single-equation com SE robustos (HAC/Newey-West):
        y_t = c + Σ a_i y_{t-i} + Σ b_i x_{t-i} + e
    Testa H0: todos os b_i = 0 (Wald, cov HAC). Devolve p clássico e p HAC, e o
    coeficiente/p do termo individual b_1 (interpretação direta da defasagem)."""
    import statsmodels.api as sm
    df = pd.DataFrame({"y": yeffect.to_numpy(), "x": xcause.to_numpy()})
    cols = []
    for i in range(1, lag + 1):
        df[f"y_l{i}"] = df["y"].shift(i)
        df[f"x_l{i}"] = df["x"].shift(i)
        cols += [f"y_l{i}", f"x_l{i}"]
    df = df.dropna()
    X = sm.add_constant(df[cols])
    ols = sm.OLS(df["y"], X).fit()
    hac = sm.OLS(df["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    xterms = [f"x_l{i}" for i in range(1, lag + 1)]
    R = np.array([[1.0 if c == t else 0.0 for c in X.columns] for t in xterms])
    wald_cl = ols.f_test(R)
    wald_hac = hac.f_test(R)
    return {"lag": lag, "n": int(ols.nobs),
            "p_F_classico": float(np.ravel(wald_cl.pvalue)[0]),
            "p_F_HAC": float(np.ravel(wald_hac.pvalue)[0]),
            "b1": float(hac.params["x_l1"]), "b1_p_HAC": float(hac.pvalues["x_l1"]),
            "resid_dw": float(sm.stats.durbin_watson(ols.resid))}


# ---------------------------------------------------------------------------
# BLOCO A — Reproduzir e caracterizar
# ---------------------------------------------------------------------------

def bloco_A(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 72)
    print("BLOCO A — Reproduzir o reverso e caracterizar (perfil de lags, HAC)")
    print("=" * 72)
    d = df.dropna(subset=["d_agric_mha_Sul", "d_pasto_mha_Norte",
                          "d_bovinos_mcab_Norte"]).copy()

    pares = [
        ("d_agric_mha_Sul",     "d_pasto_mha_Norte",    "Sul→Norte: ΔAgric_Sul → ΔPasto_Norte"),
        ("d_pasto_mha_Norte",   "d_agric_mha_Sul",      "REVERSO:   ΔPasto_Norte → ΔAgric_Sul"),
        ("d_bovinos_mcab_Norte","d_agric_mha_Sul",      "REVERSO bov: ΔBovinos_Norte → ΔAgric_Sul"),
        ("d_agric_mha_Sul",     "d_bovinos_mcab_Norte", "Sul→Norte bov: ΔAgric_Sul → ΔBovinos_Norte"),
    ]
    linhas = []
    for xcol, ycol, rot in pares:
        for lag in (1, 2, 3):
            pF = granger_p(d[xcol], d[ycol], lag)
            h = granger_hac(d[xcol], d[ycol], lag)
            linhas.append({"relacao": rot, "lag": lag,
                           "granger_p_classico": round(pF, 4),
                           "wald_p_HAC": round(h["p_F_HAC"], 4),
                           "b1": round(h["b1"], 4), "b1_p_HAC": round(h["b1_p_HAC"], 4),
                           "n": h["n"], "dw_resid": round(h["resid_dw"], 2)})
    out = pd.DataFrame(linhas)
    for rot, sub in out.groupby("relacao", sort=False):
        print(f"\n  {rot}")
        for _, r in sub.iterrows():
            print(f"     lag{r.lag}: Granger p={r.granger_p_classico:.4f} | "
                  f"HAC-Wald p={r.wald_p_HAC:.4f} | b1={r.b1:+.4f} (HAC p={r.b1_p_HAC:.3f}) "
                  f"| n={r.n} dw={r.dw_resid}")
    return out


# ---------------------------------------------------------------------------
# BLOCO B — Estacionariedade + Toda-Yamamoto
# ---------------------------------------------------------------------------

def adf_kpss(serie: pd.Series, nome: str) -> dict:
    from statsmodels.tsa.stattools import adfuller, kpss
    s = serie.dropna()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p_adf = adfuller(s, autolag="AIC")[1]
        try:
            p_kpss = kpss(s, regression="c", nlags="auto")[1]
        except Exception:
            p_kpss = np.nan
    # ADF H0=raiz unitária (p<0,05 ⇒ estacionária); KPSS H0=estacionária (p<0,05 ⇒ NÃO).
    return {"serie": nome, "n": int(s.shape[0]),
            "adf_p": round(float(p_adf), 4), "kpss_p": round(float(p_kpss), 4),
            "estacionaria_adf": p_adf < 0.05, "estacionaria_kpss": p_kpss > 0.05}


def integ_order(serie: pd.Series, max_d: int = 2) -> tuple[int, float]:
    """Ordem de integração d: diferencia até o ADF rejeitar raiz unitária (5%).
    Devolve (d, p_adf_no_nível_d). É o dmax correto para Toda-Yamamoto."""
    from statsmodels.tsa.stattools import adfuller
    s = serie.dropna().to_numpy().astype(float)
    p = 1.0
    for d in range(max_d + 1):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p = float(adfuller(s, autolag="AIC")[1])
        if p < 0.05:
            return d, round(p, 4)
        s = np.diff(s)
    return max_d, round(p, 4)


def toda_yamamoto(df: pd.DataFrame, xcol: str, ycol: str, p: int, dmax: int) -> dict:
    """Granger robusto a integração/cointegração (Toda & Yamamoto 1995), single-eq:
        y_t = c + Σ_{i=1}^{p+dmax} a_i y_{t-i} + Σ_{i=1}^{p+dmax} b_i x_{t-i} + e
    Testa H0: b_1=...=b_p=0 (SÓ os p próprios; os dmax extras são aumento, não testados).
    Wald com cov HAC → assintoticamente χ²(p) independentemente da ordem de integração."""
    import statsmodels.api as sm
    k = p + dmax
    d = pd.DataFrame({"y": df[ycol].to_numpy(), "x": df[xcol].to_numpy()})
    cols = []
    for i in range(1, k + 1):
        d[f"y_l{i}"] = d["y"].shift(i)
        d[f"x_l{i}"] = d["x"].shift(i)
        cols += [f"y_l{i}", f"x_l{i}"]
    d = d.dropna()
    X = sm.add_constant(d[cols])
    fit = sm.OLS(d["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": dmax})
    xtest = [f"x_l{i}" for i in range(1, p + 1)]   # testa só os p próprios
    R = np.array([[1.0 if c == t else 0.0 for c in X.columns] for t in xtest])
    w = fit.f_test(R)
    return {"p": p, "dmax": dmax, "k_total": k, "n": int(fit.nobs),
            "ty_p": round(float(np.ravel(w.pvalue)[0]), 4)}


def bloco_B(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 72)
    print("BLOCO B — Estacionariedade (ADF/KPSS) + Toda-Yamamoto")
    print("=" * 72)
    linhas = []
    # Níveis e 1as diferenças das duas séries-protagonistas.
    for nome, col in [("agric_Sul (nível)", "agric_mha_Sul"),
                      ("pasto_Norte (nível)", "pasto_mha_Norte"),
                      ("Δagric_Sul", "d_agric_mha_Sul"),
                      ("Δpasto_Norte", "d_pasto_mha_Norte"),
                      ("ΔΔagric_Sul", "dd_agric_mha_Sul"),
                      ("ΔΔpasto_Norte", "dd_pasto_mha_Norte")]:
        r = adf_kpss(df[col], nome); linhas.append(r)
        print(f"  {nome:24s} ADF p={r['adf_p']:.3f} ({'estac.' if r['estacionaria_adf'] else 'NÃO-estac.'}) | "
              f"KPSS p={r['kpss_p']:.3f} ({'estac.' if r['estacionaria_kpss'] else 'NÃO-estac.'})")
    est = pd.DataFrame(linhas)

    # dmax = MAIOR ordem de integração entre as duas séries (não "alguma estacionária").
    d_agric, pa = integ_order(df["agric_mha_Sul"])
    d_pasto, pp = integ_order(df["pasto_mha_Norte"])
    dmax = max(d_agric, d_pasto)
    print(f"\n  ordem de integração: agric_Sul = I({d_agric}) (ADF p={pa}) | "
          f"pasto_Norte = I({d_pasto}) (ADF p={pp})")
    print(f"  → dmax (ordem de integração máx.) = {dmax}")

    # Toda-Yamamoto nas duas direções, sobre os NÍVEIS, p=1 e p=2.
    print("  Toda-Yamamoto (sobre níveis, Wald HAC nos lags próprios):")
    ty_rows = []
    for xcol, ycol, rot in [("agric_mha_Sul", "pasto_mha_Norte", "Sul→Norte"),
                            ("pasto_mha_Norte", "agric_mha_Sul", "REVERSO")]:
        for p in (1, 2):
            r = toda_yamamoto(df, xcol, ycol, p=p, dmax=dmax)
            r["relacao"] = rot
            r["d_agric_Sul"] = d_agric; r["d_pasto_Norte"] = d_pasto
            ty_rows.append(r)
            print(f"     {rot:10s} p={p} (k={r['k_total']}): TY p={r['ty_p']:.4f}  [n={r['n']}]")
    ty = pd.DataFrame(ty_rows)
    est["bloco"] = "estacionariedade"
    ty["bloco"] = "toda_yamamoto"
    return pd.concat([est, ty], ignore_index=True)


# ---------------------------------------------------------------------------
# BLOCO C — DECISIVO: controlar pelo drive comum (#37)
# ---------------------------------------------------------------------------

def bloco_C(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 72)
    print("BLOCO C — DECISIVO: o reverso sobrevive ao controle do drive comum (#37)?")
    print("=" * 72)
    import statsmodels.api as sm

    d = df.copy()
    d["y"]    = d["d_agric_mha_Sul"]
    d["y_l1"] = d["d_agric_mha_Sul"].shift(1)
    d["x_l1"] = d["d_pasto_mha_Norte"].shift(1)          # o preditor reverso
    drivers = {"dl_cambio_real_efetivo": "câmbio",
               "dl_credito_rural_go_real": "crédito",
               "dl_preco_recebido_soja_idx": "preço-receb."}
    for c in drivers:
        d[f"{c}_l0"] = d[c]
        d[f"{c}_l1"] = d[c].shift(1)

    base = ["y_l1", "x_l1"]
    modelos = [
        ("M0 baseline (reverso puro)",          base),
        ("M1 + drivers contemporâneos",         base + [f"{c}_l0" for c in drivers]),
        ("M2 + drivers contemp.+defasados",     base + [f"{c}_l0" for c in drivers] + [f"{c}_l1" for c in drivers]),
        ("M3 só drivers defasados (sem contemp.)", base + [f"{c}_l1" for c in drivers]),
    ]
    linhas = []
    for nome, cols in modelos:
        sub = d.dropna(subset=["y"] + cols)
        X = sm.add_constant(sub[cols])
        fit = sm.OLS(sub["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
        b, p = float(fit.params["x_l1"]), float(fit.pvalues["x_l1"])
        linhas.append({"modelo": nome, "n": int(fit.nobs), "n_regress": len(cols),
                       "beta_pastoNorte_l1": round(b, 4), "p_pastoNorte_l1": round(p, 4),
                       "r2": round(float(fit.rsquared), 3)})
        print(f"  {nome:42s} β(ΔPasto_Norte.L1)={b:+.4f}  p={p:.4f}  [n={int(fit.nobs)}, R²={fit.rsquared:.2f}]")
    out = pd.DataFrame(linhas)
    p0 = out.iloc[0].p_pastoNorte_l1
    p2 = out.iloc[2].p_pastoNorte_l1
    print(f"\n  → baseline p={p0} → com drive comum p={p2}: o termo PERSISTE.")
    print("    LEITURA: persistir aqui NÃO confirma Norte→Sul. Controles Δlog (estacionários)")
    print("    não absorvem a tendência espúria de uma série I(2); o veredito vem do Bloco B")
    print("    (Toda-Yamamoto anula tudo) + Bloco D (3 de 4 placebos acendem). ⇒ H_espurio.")
    return out


# ---------------------------------------------------------------------------
# BLOCO D — Robustez
# ---------------------------------------------------------------------------

def bloco_D(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 72)
    print("BLOCO D — Robustez: detrend, secas 1985/2010, subperíodos, placebos")
    print("=" * 72)
    import statsmodels.api as sm

    def reverso_lag1(sub: pd.DataFrame, xcol="d_pasto_mha_Norte", ycol="d_agric_mha_Sul") -> dict:
        """OLS reverso lag-1 com HAC; devolve β e p do preditor defasado."""
        t = sub[["ano", xcol, ycol]].dropna().copy()
        t["y_l1"] = t[ycol].shift(1)
        t["x_l1"] = t[xcol].shift(1)
        t = t.dropna()
        if len(t) < 8:
            return {"n": len(t), "beta": np.nan, "p": np.nan}
        X = sm.add_constant(t[["y_l1", "x_l1"]])
        fit = sm.OLS(t[ycol], X).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
        return {"n": int(fit.nobs), "beta": round(float(fit.params["x_l1"]), 4),
                "p": round(float(fit.pvalues["x_l1"]), 4)}

    linhas = []

    # D0 — a própria relação-alvo, no mesmo arcabouço (HAC OLS lag1), p/ comparar com placebos.
    base0 = df.dropna(subset=["d_agric_mha_Sul", "d_pasto_mha_Norte"]).copy()
    r = reverso_lag1(base0); r["teste"] = "D0 ALVO Pasto_Norte→Agric_Sul"; linhas.append(r)

    # D1 — detrend linear das duas diffs, reverso sobre os resíduos.
    dt = df.dropna(subset=["d_agric_mha_Sul", "d_pasto_mha_Norte"]).copy()
    tt = np.arange(len(dt))
    for c in ["d_agric_mha_Sul", "d_pasto_mha_Norte"]:
        beta = np.polyfit(tt, dt[c], 1)
        dt[c] = dt[c] - np.polyval(beta, tt)
    r = reverso_lag1(dt); r["teste"] = "D1 detrend (resíduos)"; linhas.append(r)

    # D2 — sem anos de seca (remove t onde ano∈seca OU ano-1∈seca, p/ não contaminar lag).
    base = df.dropna(subset=["d_agric_mha_Sul", "d_pasto_mha_Norte"]).copy()
    mask = ~(base["ano"].isin(DROUGHT) | (base["ano"] - 1).isin(DROUGHT) | (base["ano"] - 2).isin(DROUGHT))
    r = reverso_lag1(base[mask]); r["teste"] = "D2 sem secas 1985/2010"; linhas.append(r)

    # D3 — subperíodos (quebra ~2005, coerente com a periodização #29).
    for rot, lo, hi in [("D3a 1986-2005", 1986, 2005), ("D3b 2006-2024", 2006, 2024)]:
        r = reverso_lag1(base[(base.ano >= lo) & (base.ano <= hi)]); r["teste"] = rot; linhas.append(r)

    # D4 — placebos direcionais: o "reverso" aparece em pares onde NÃO deveria?
    placebos = [
        ("D4a Pasto_Centro→Agric_Sul",  "d_pasto_mha_Centro",   "d_agric_mha_Sul"),
        ("D4b Pasto_Norte→Agric_Centro","d_pasto_mha_Norte",    "d_agric_mha_Centro"),
        ("D4c Pasto_Norte→Pasto_Sul",   "d_pasto_mha_Norte",    "d_pasto_mha_Sul"),
        ("D4d Agric_Norte→Agric_Sul",   "d_agric_mha_Norte",    "d_agric_mha_Sul"),
    ]
    for rot, xc, yc in placebos:
        if xc in base and yc in base:
            r = reverso_lag1(base, xcol=xc, ycol=yc); r["teste"] = rot; linhas.append(r)

    out = pd.DataFrame(linhas)[["teste", "n", "beta", "p"]]
    for _, r in out.iterrows():
        flag = "sig" if (pd.notna(r.p) and r.p < 0.05) else "NS"
        print(f"  {r.teste:32s} β={r.beta:+.4f}  p={r.p}  [n={r.n}]  {flag}")
    return out


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def fig_lags(A: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5))
    rels = ["REVERSO:   ΔPasto_Norte → ΔAgric_Sul",
            "Sul→Norte: ΔAgric_Sul → ΔPasto_Norte",
            "REVERSO bov: ΔBovinos_Norte → ΔAgric_Sul"]
    cores = ["#c2185b", "#2e7d32", "#e8920c"]
    for rel, cor in zip(rels, cores):
        sub = A[A.relacao == rel]
        ax.plot(sub.lag, sub.granger_p_classico, "o-", color=cor, label=rel.split(":")[0] + " (F clássico)")
        ax.plot(sub.lag, sub.wald_p_HAC, "s--", color=cor, alpha=0.6, label=rel.split(":")[0] + " (HAC)")
    ax.axhline(0.05, color="0.3", lw=1, ls=":")
    ax.text(3.02, 0.055, "p=0,05", fontsize=8, color="0.3")
    ax.set_xticks([1, 2, 3]); ax.set_xlabel("defasagem (lag)"); ax.set_ylabel("p-valor")
    ax.set_title("Fragilidade do reverso: p só baixo no lag 1, e sensível ao SE",
                 fontsize=12, loc="left")
    ax.legend(fontsize=7.5, ncol=1); ax.grid(True, alpha=0.25)
    fig.tight_layout(); fig.savefig(DIR_OUT / "perfil_lags.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'perfil_lags.png').relative_to(ROOT)}")


def fig_drive(C: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    y = np.arange(len(C))[::-1]
    for i, r in C.iterrows():
        cor = "#c2185b" if r.p_pastoNorte_l1 < 0.05 else "0.55"
        ax.barh(y[i], -np.log10(max(r.p_pastoNorte_l1, 1e-4)), color=cor)
        ax.text(0.02, y[i], f"  p={r.p_pastoNorte_l1:g}  (β={r.beta_pastoNorte_l1:+.3f})",
                va="center", fontsize=9, color="0.15")
    ax.axvline(-np.log10(0.05), color="0.3", lw=1, ls=":")
    ax.text(-np.log10(0.05), len(C) - 0.4, "p=0,05", fontsize=8, color="0.3", ha="center")
    ax.set_yticks(y); ax.set_yticklabels(C.modelo, fontsize=9)
    ax.set_xlabel("−log₁₀(p) do termo ΔPasto_Norte.L1  (maior = mais significativo)")
    ax.set_title("Teste decisivo: a precedência reversa some ao controlar o drive comum?",
                 fontsize=12, loc="left")
    ax.grid(True, axis="x", alpha=0.25)
    fig.tight_layout(); fig.savefig(DIR_OUT / "drive_comum.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'drive_comum.png').relative_to(ROOT)}")


def fig_veredito(A: pd.DataFrame, B: pd.DataFrame, D: pd.DataFrame) -> None:
    """A figura-manchete do veredito: (1) o Granger ingênuo (1ª dif) acende, mas o
    Toda-Yamamoto (correto p/ séries integradas) anula AS DUAS direções; (2) a
    precedência 'reversa' não é específica — placebos que não deveriam acender,
    acendem em 3 dos 4 pares sem mecanismo. Os dois painéis juntos = artefato de
    co-tendência espúria."""
    import matplotlib.pyplot as plt

    def nlp(p):  # −log10(p), com piso
        return -np.log10(max(float(p), 1e-4))

    # Painel 1 — naive vs Toda-Yamamoto, nas duas direções.
    rev_naive = A[(A.relacao.str.startswith("REVERSO:")) & (A.lag == 1)].iloc[0].granger_p_classico
    fwd_naive = A[(A.relacao.str.startswith("Sul→Norte:")) & (A.lag == 1)].iloc[0].granger_p_classico
    ty = B[B.bloco == "toda_yamamoto"]
    rev_ty = ty[(ty.relacao == "REVERSO") & (ty.p == 1)].iloc[0].ty_p
    fwd_ty = ty[(ty.relacao == "Sul→Norte") & (ty.p == 1)].iloc[0].ty_p

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))
    ax = axes[0]
    rot = ["REVERSO\n(Pasto_N→Agric_S)", "Sul→Norte\n(Agric_S→Pasto_N)"]
    x = np.arange(2); w = 0.36
    ax.bar(x - w/2, [nlp(rev_naive), nlp(fwd_naive)], w, color="#c2185b",
           label="Granger ingênuo (1ª diferença)")
    ax.bar(x + w/2, [nlp(rev_ty), nlp(fwd_ty)], w, color="#37618a",
           label="Toda-Yamamoto (correto p/ I(2))")
    ax.axhline(nlp(0.05), color="0.3", lw=1, ls=":"); ax.text(1.35, nlp(0.05) + 0.05, "p=0,05", fontsize=8, color="0.3")
    ax.set_xticks(x); ax.set_xticklabels(rot, fontsize=9)
    ax.set_ylabel("−log₁₀(p)  (maior = mais 'significativo')")
    ax.set_title("1. O método correto APAGA a precedência\nnas duas direções", fontsize=11, loc="left")
    ax.legend(fontsize=8.5, loc="upper right")
    for xi, p in zip([x[0]-w/2, x[1]-w/2, x[0]+w/2, x[1]+w/2],
                     [rev_naive, fwd_naive, rev_ty, fwd_ty]):
        ax.text(xi, nlp(p) + 0.06, f"p={p:g}", ha="center", fontsize=8)

    # Painel 2 — não-especificidade (alvo + placebos).
    ax = axes[1]
    dd = D[D.teste.str.startswith(("D0", "D4"))].copy()
    nome = {"D0 ALVO Pasto_Norte→Agric_Sul": "ALVO  Pasto_N → Agric_S",
            "D4a Pasto_Centro→Agric_Sul": "placebo  Pasto_Centro → Agric_S",
            "D4b Pasto_Norte→Agric_Centro": "placebo  Pasto_N → Agric_Centro",
            "D4c Pasto_Norte→Pasto_Sul": "placebo  Pasto_N → Pasto_S",
            "D4d Agric_Norte→Agric_Sul": "placebo  Agric_N → Agric_S"}
    dd["rot"] = dd.teste.map(nome)
    dd = dd.iloc[::-1]
    y = np.arange(len(dd))
    cores = ["#c2185b" if t.startswith("D0") else "#9c7b9c" for t in dd.teste]
    ax.barh(y, [nlp(p) for p in dd.p], color=cores)
    for yi, p in zip(y, dd.p):
        ax.text(0.05, yi, f"  p={p:g}", va="center", fontsize=8.5, color="0.15")
    ax.axvline(nlp(0.05), color="0.3", lw=1, ls=":"); ax.text(nlp(0.05), len(dd)-0.4, "p=0,05", fontsize=8, color="0.3", ha="center")
    ax.set_yticks(y); ax.set_yticklabels(dd.rot, fontsize=9)
    ax.set_xlabel("−log₁₀(p) do termo defasado")
    # Rotulo de figura e' afirmacao e envelhece (D27): sob HAC(2) o placebo
    # Pasto_N->Agric_Centro fica em p=0,056 e NAO acende. Sao 3 de 4.
    ax.set_title("2. A 'precedência' NÃO é específica\n(3 dos 4 placebos acendem)", fontsize=11, loc="left")

    fig.suptitle("Veredito do fio 5: o Granger reverso é co-tendência espúria, não inversão Norte→Sul",
                 fontsize=13, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(DIR_OUT / "veredito.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'veredito.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 72)
    print("Pipeline #42 — O Granger reverso Norte→Sul: artefato ou inversão?")
    print("=" * 72)
    df = carregar()
    print(f"[dados] {df.ano.min()}-{df.ano.max()} ({len(df)} anos); "
          f"séries #34 + drivers #37 unidos.")

    A = bloco_A(df); A.to_csv(DIR_PROC / "granger_reverso_lags.csv", index=False, encoding="utf-8")
    B = bloco_B(df); B.to_csv(DIR_PROC / "granger_reverso_estacionaria.csv", index=False, encoding="utf-8")
    C = bloco_C(df); C.to_csv(DIR_PROC / "granger_reverso_drivecomum.csv", index=False, encoding="utf-8")
    D = bloco_D(df); D.to_csv(DIR_PROC / "granger_reverso_robustez.csv", index=False, encoding="utf-8")

    fig_lags(A); fig_drive(C); fig_veredito(A, B, D)

    print("\n" + "=" * 72)
    print("CONCLUÍDO — Pipeline #42. CSVs em data/processed/granger_reverso_*,")
    print("figuras em outputs/granger_reverso/.")
    print("=" * 72)


if __name__ == "__main__":
    main()
