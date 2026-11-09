"""
Pipeline #60 — Testes de mérito pedidos pela banca de qualificação
==================================================================

POR QUÊ
-------
A banca (Adriana, Baumann) e a revisão cruzada Claude × Codex (05/out/2026,
`Textos/banca_qualificacao/comparacao_revisoes.md`) levantaram pontos que não
se resolvem escrevendo melhor: exigem rodar testes. Este pipeline roda todos, sem
alterar os pipelines originais (#29, #34, #42, #28C, #49), que continuam sendo a
referência do que está no texto da qualificação.

BLOCOS
------
  B1  Raiz unitária com quebra nas séries regionais (agric_Sul, pasto_Norte):
      ADF com constante e com tendência; Zivot-Andrews (1 quebra) com valores
      críticos de amostra finita por simulação; Lee-Strazicich LM com 2 quebras
      (modelos A e C), valores críticos por simulação.        [banca B9.3]
  B2  Toda-Yamamoto refeito: Wald χ² com covariância OLS (forma original de
      Toda-Yamamoto 1995), Wald χ² HAC com largura fixa independente de d_max,
      d_max ∈ {1, 2}, p ∈ {1, 2}, e p-valor por bootstrap sob a nula
      (Hacker & Hatemi-J 2006). Inclui variante com dummies de quebra.
      Registra o n efetivo de cada regressão.                 [Codex 2 e 6]
  B3  Poder do procedimento efetivamente usado (Granger em Δ e Toda-Yamamoto em
      nível, d_max 1 e 2) num DGP I(1) calibrado nas séries.   [Codex 1]
  B4  sup-F calibrado: distribuição nula do máximo sob VAR(1) estimado
      (autocorrelação e correlação cruzada), p ajustado para cada fronteira e
      taxa de falso positivo da segmentação binária com F ≥ 4. [Codex 3]
  B5  CIPS (Pesaran 2007) no painel de 166 AMCs, em nível e em Δ, com valores
      críticos simulados para N e T do painel.                 [banca B9.1/B9.2]
  B6  Diagnóstico dos efeitos fixos no modelo em Δ: poolabilidade dos efeitos
      de unidade (= tendências próprias em nível) e teste de Mundlak.
                                                               [banca B9.5]
  B7  Mistura de gaussianas × distribuição única assimétrica, com o
      truncamento da idade pela janela (idade máx. = ano − 1986). [Codex 7]
  B8  Matriz W do SLX: confere a direção (vizinhos ao sul).   [Codex 5]

ENTRADAS
    data/processed/deslocamento_series_regionais.csv, drivers_macro_anual.csv (#34/#37)
    data/processed/taxas_lulc_goias.csv (#17)
    data/processed/painel_amc_goias.parquet (#25)
    data/processed/pastagem_idade_censo.parquet (#28C)

SAÍDAS
    data/processed/banca60_*.csv  (um por bloco)
    outputs/banca60/log_<bloco>.txt

COMO RODAR
    python scripts/banca_testes_merito.py            # todos os blocos
    python scripts/banca_testes_merito.py B1 B2      # só alguns

Quando foi feito: 2026-10-05, depois da banca de qualificação.
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "banca60"
DIR_OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261005
warnings.simplefilter("ignore")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def ols(y: np.ndarray, X: np.ndarray):
    """OLS por lstsq. Devolve beta, resíduos, (X'X)^-1."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    xtx_inv = np.linalg.pinv(X.T @ X)
    return beta, resid, xtx_inv


def tstat(y: np.ndarray, X: np.ndarray, j: int) -> float:
    beta, resid, xtx_inv = ols(y, X)
    n, k = X.shape
    s2 = resid @ resid / (n - k)
    return float(beta[j] / np.sqrt(s2 * xtx_inv[j, j]))


def lagmat(x: np.ndarray, k: int) -> np.ndarray:
    """Matriz (n × k) com x_{t-1}..x_{t-k}, primeiras k linhas NaN."""
    n = len(x)
    out = np.full((n, k), np.nan)
    for i in range(1, k + 1):
        out[i:, i - 1] = x[:-i]
    return out


def carregar_regionais() -> pd.DataFrame:
    s = pd.read_csv(DIR_PROC / "deslocamento_series_regionais.csv")
    return s.sort_values("ano").reset_index(drop=True)


class Log:
    def __init__(self, nome: str):
        self.path = DIR_OUT / f"log_{nome}.txt"
        self.buf: list[str] = []

    def __call__(self, *a):
        msg = " ".join(str(x) for x in a)
        print(msg)
        self.buf.append(msg)

    def salvar(self):
        self.path.write_text("\n".join(self.buf) + "\n", encoding="utf-8", newline="\n")


# ===========================================================================
# B1 — Raiz unitária com quebra
# ===========================================================================

def ls_stat(y: np.ndarray, model: str, kmax: int = 3, trim: float = 0.1,
            gap: int | None = None) -> dict:
    """Lee-Strazicich (2003) LM com duas quebras, mínimo sobre os pares.

    model 'A' (crash: quebra de nível) ou 'C' (nível e inclinação).
    Para cada par (TB1, TB2): k escolhido por geral-para-específico (|t| > 1,645
    na última defasagem, a partir de kmax). Estatística = min τ sobre os pares.
    """
    T = len(y)
    t = np.arange(1, T + 1, dtype=float)
    lo, hi = max(int(np.ceil(trim * T)), 2), int(np.floor((1 - trim) * T))
    if gap is None:
        gap = 2 if model == "A" else 3
    best = {"tau": np.inf}
    dy = np.diff(y)
    for tb1 in range(lo, hi):
        for tb2 in range(tb1 + gap, hi):
            cols = [np.ones(T), t]
            for tb in (tb1, tb2):
                cols.append((t > tb).astype(float))          # D_jt
                if model == "C":
                    cols.append(np.where(t > tb, t - tb, 0.0))  # DT_jt
            Z = np.column_stack(cols)
            dZ = np.diff(Z, axis=0)
            # passo 1: δ̃ de Δy sobre ΔZ (sem a constante, que some na diferença)
            dZ_ = dZ[:, 1:]
            d_til, *_ = np.linalg.lstsq(dZ_, dy, rcond=None)
            d_full = np.concatenate([[0.0], d_til])
            psi = y[0] - Z[0] @ d_full
            S = y - psi - Z @ d_full                              # S̃_t
            dS = np.diff(S)
            # passo 2: Δy_t = ΔZ_t δ + φ S̃_{t-1} + Σ γ ΔS̃_{t-i} + e
            tau_k = None
            for k in range(kmax, -1, -1):
                start = k            # índice em dy (dy[i] = y[i+1]-y[i]); dS[rows-i] exige rows ≥ k
                                     # (corrigido 06/out após conferência do Codex: era k + 1)
                rows = np.arange(start, T - 1)
                Xp = [dZ_[rows], S[rows][:, None]]               # S̃_{t-1}: S[i] para dy[i]
                for i in range(1, k + 1):
                    Xp.append(dS[rows - i][:, None])
                X = np.column_stack(Xp)
                yy = dy[rows]
                if len(yy) <= X.shape[1] + 2:
                    continue
                if np.linalg.matrix_rank(X) < X.shape[1]:
                    # ex.: modelo C com TB1 = 4 e k = 3, ΔDT1 = 1 em todas as linhas = constante.
                    # Corrigido 07/out (2ª conferência do Codex): candidata descartada.
                    continue
                beta, resid, xtx_inv = ols(yy, X)
                s2 = resid @ resid / (len(yy) - X.shape[1])
                se = np.sqrt(np.maximum(s2 * np.diag(xtx_inv), 1e-300))
                tvals = beta / se
                j_phi = dZ_.shape[1]
                if k == 0 or abs(tvals[-1]) > 1.645:
                    tau_k = (float(tvals[j_phi]), k)
                    break
            if tau_k and tau_k[0] < best["tau"]:
                best = {"tau": tau_k[0], "k": tau_k[1], "tb1": tb1, "tb2": tb2}
    return best


def za_stat(y: np.ndarray, regression: str) -> dict:
    from statsmodels.tsa.stattools import zivot_andrews
    r = zivot_andrews(y, trim=0.15, maxlag=3, regression=regression, autolag="AIC")
    return {"stat": float(r[0]), "p_asint": float(r[1]), "bp_idx": int(r[4]),
            "cv5_asint": float(r[2]["5%"])}


def bloco_B1(nsim: int = 500) -> pd.DataFrame:
    log = Log("B1")
    from statsmodels.tsa.stattools import adfuller
    s = carregar_regionais()
    anos = s["ano"].to_numpy()
    series = {
        "agric_Sul (nível)": s["agric_mha_Sul"].to_numpy(),
        "pasto_Norte (nível)": s["pasto_mha_Norte"].to_numpy(),
        "Δagric_Sul": np.diff(s["agric_mha_Sul"].to_numpy()),
        "Δpasto_Norte": np.diff(s["pasto_mha_Norte"].to_numpy()),
    }
    rng = np.random.default_rng(SEED)
    linhas = []
    log("=" * 72)
    log("B1 — Raiz unitária com e sem quebra (séries regionais, 1985–2024)")
    log("=" * 72)

    # Valores críticos de amostra finita por simulação (passeio aleatório puro).
    def cv_sim(fun, T, nsim):
        vals = []
        for _ in range(nsim):
            e = rng.normal(size=T)
            vals.append(fun(np.cumsum(e)))
        vals = np.array([v for v in vals if np.isfinite(v)])
        return np.quantile(vals, [0.01, 0.05, 0.10]), vals

    cache_cv: dict = {}
    for nome, y in series.items():
        T = len(y)
        ano0 = anos[0] if "nível" in nome else anos[1]
        row = {"serie": nome, "T": T}
        for reg in ("c", "ct"):
            r = adfuller(y, maxlag=3, regression=reg, autolag="AIC")
            row[f"adf_{reg}_stat"] = round(r[0], 3)
            row[f"adf_{reg}_p"] = round(r[1], 4)
        for reg in ("c", "ct"):
            za = za_stat(y, reg)
            key = ("za", reg, T)
            if key not in cache_cv:
                t0 = time.time()
                cache_cv[key], _ = cv_sim(lambda x: za_stat(x, reg)["stat"], T, nsim)
                log(f"   [cv ZA {reg} T={T}: {nsim} sim em {time.time()-t0:.0f}s]")
            cv = cache_cv[key]
            row[f"za_{reg}_stat"] = round(za["stat"], 3)
            row[f"za_{reg}_quebra"] = int(ano0 + za["bp_idx"])
            row[f"za_{reg}_cv5_sim"] = round(cv[1], 3)
            row[f"za_{reg}_cv10_sim"] = round(cv[2], 3)
            row[f"za_{reg}_rejeita5"] = bool(za["stat"] < cv[1])
        for model in ("A", "C"):
            ls = ls_stat(y, model)
            key = ("ls", model, T)
            if key not in cache_cv:
                t0 = time.time()
                cache_cv[key], _ = cv_sim(lambda x: ls_stat(x, model)["tau"], T, nsim)
                log(f"   [cv LS {model} T={T}: {nsim} sim em {time.time()-t0:.0f}s]")
            cv = cache_cv[key]
            row[f"ls_{model}_stat"] = round(ls["tau"], 3)
            row[f"ls_{model}_quebras"] = f"{int(ano0 + ls['tb1'])}/{int(ano0 + ls['tb2'])}"
            row[f"ls_{model}_k"] = ls["k"]
            row[f"ls_{model}_cv5_sim"] = round(cv[1], 3)
            row[f"ls_{model}_cv10_sim"] = round(cv[2], 3)
            row[f"ls_{model}_rejeita5"] = bool(ls["tau"] < cv[1])
        linhas.append(row)
        log(f"\n  {nome}  (T={T})")
        log(f"    ADF c : τ={row['adf_c_stat']:+.2f} p={row['adf_c_p']:.3f} | "
            f"ADF ct: τ={row['adf_ct_stat']:+.2f} p={row['adf_ct_p']:.3f}")
        for reg in ("c", "ct"):
            log(f"    ZA {reg:2s}: τ={row[f'za_{reg}_stat']:+.2f} quebra={row[f'za_{reg}_quebra']} "
                f"cv5(sim)={row[f'za_{reg}_cv5_sim']:+.2f} → "
                f"{'REJEITA raiz' if row[f'za_{reg}_rejeita5'] else 'não rejeita'}")
        for model in ("A", "C"):
            log(f"    LS {model} : τ={row[f'ls_{model}_stat']:+.2f} quebras={row[f'ls_{model}_quebras']} "
                f"k={row[f'ls_{model}_k']} cv5(sim)={row[f'ls_{model}_cv5_sim']:+.2f} → "
                f"{'REJEITA raiz' if row[f'ls_{model}_rejeita5'] else 'não rejeita'}")
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B1_raiz_quebra.csv", index=False)
    log("\nNota: cv(sim) = quantis do mesmo procedimento (com a mesma busca de quebra e de")
    log(f"defasagem) aplicado a {nsim} passeios aleatórios de mesmo T. Para LS-C a")
    log("distribuição depende da posição real das quebras; o cv por passeio sem quebra é")
    log("aproximação, declarada como tal.")
    log.salvar()
    return out


# ===========================================================================
# B2 — Toda-Yamamoto refeito
# ===========================================================================

NW_BW = int(np.floor(4 * (40 / 100) ** (2 / 9)))   # = 3, regra usual de Newey-West


def ty_design(y: np.ndarray, x: np.ndarray, k: int, exog: np.ndarray | None = None):
    """Equação de y no VAR em nível com k = p + dmax defasagens de y e x."""
    Ly, Lx = lagmat(y, k), lagmat(x, k)
    cols = [np.ones(len(y))]
    names = ["c"]
    for i in range(k):
        cols += [Ly[:, i], Lx[:, i]]
        names += [f"y_l{i+1}", f"x_l{i+1}"]
    if exog is not None:
        for j in range(exog.shape[1]):
            cols.append(exog[:, j]); names.append(f"ex{j}")
    X = np.column_stack(cols)
    ok = ~np.isnan(X).any(axis=1)
    return y[ok], X[ok], names, ok


def wald(beta, V, idx):
    R = np.zeros((len(idx), len(beta)))
    for r, j in enumerate(idx):
        R[r, j] = 1.0
    Rb = R @ beta
    W = float(Rb @ np.linalg.pinv(R @ V @ R.T) @ Rb)
    return W, float(stats.chi2.sf(W, len(idx)))


def hac_cov(X, resid, bw):
    n = X.shape[0]
    u = X * resid[:, None]
    S = u.T @ u
    for l in range(1, bw + 1):
        w = 1 - l / (bw + 1)
        G = u[l:].T @ u[:-l]
        S += w * (G + G.T)
    B = np.linalg.pinv(X.T @ X)
    return B @ S @ B


def ty_test(y, x, p, dmax, exog=None, bw=NW_BW):
    yy, X, names, ok = ty_design(y, x, p + dmax, exog)
    beta, resid, xtx_inv = ols(yy, X)
    n, kx = X.shape
    s2 = resid @ resid / (n - kx)
    idx = [names.index(f"x_l{i+1}") for i in range(p)]
    W_ols, p_ols = wald(beta, s2 * xtx_inv, idx)
    W_hac, p_hac = wald(beta, hac_cov(X, resid, bw) * n / (n - kx), idx)
    return {"n": n, "W_ols": W_ols, "p_ols": p_ols, "W_hac": W_hac, "p_hac": p_hac}


def ty_bootstrap(y, x, p, dmax, nboot, rng, exog=None):
    """Bootstrap de resíduos sob a nula — VARIANTE inspirada em Hacker & Hatemi-J (2006):
    gera do VAR AUMENTADO (k = p + dmax) restrito, não do VAR de ordem básica, e sem o
    ajuste de alavancagem. Equação de x irrestrita; equação de y sem as p primeiras
    defasagens de x (as dmax extras ficam livres). Gera séries recursivamente a partir das k primeiras
    observações reais, reamostrando pares de resíduos centrados."""
    k = p + dmax
    W_obs = ty_test(y, x, p, dmax, exog)["W_ols"]
    yy, Xy, names, ok = ty_design(y, x, k, exog)
    drop = [names.index(f"x_l{i+1}") for i in range(p)]
    keep = [j for j in range(Xy.shape[1]) if j not in drop]
    by_r, ry, _ = ols(yy, Xy[:, keep])
    by = np.zeros(Xy.shape[1]); by[keep] = by_r
    xx, Xx, _, _ = ty_design(x, y, k, exog)        # equação de x: regressores trocados
    bx, rx, _ = ols(xx, Xx)
    # Xx tem [c, x_l1, y_l1, ...] (ty_design(x, y): 'y'=x, 'x'=y)
    R = np.column_stack([ry - ry.mean(), rx - rx.mean()])
    T = len(y)
    first = np.where(ok)[0][0]
    cnt = 0
    for _ in range(nboot):
        ys, xs = y.copy(), x.copy()
        draw = R[rng.integers(0, len(R), size=T)]
        for t in range(first, T):
            row_y = [1.0]; row_x = [1.0]
            for i in range(1, k + 1):
                row_y += [ys[t - i], xs[t - i]]
                row_x += [xs[t - i], ys[t - i]]
            if exog is not None:
                row_y += list(exog[t]); row_x += list(exog[t])
            ys[t] = np.dot(by, row_y) + draw[t, 0]
            xs[t] = np.dot(bx, row_x) + draw[t, 1]
        cnt += ty_test(ys, xs, p, dmax, exog)["W_ols"] >= W_obs
    return (cnt + 1) / (nboot + 1)


def bloco_B2(nboot: int = 1999) -> pd.DataFrame:
    log = Log("B2")
    from statsmodels.tsa.api import VAR
    s = carregar_regionais()
    anos = s["ano"].to_numpy()
    ag, pa = s["agric_mha_Sul"].to_numpy(), s["pasto_mha_Norte"].to_numpy()
    rng = np.random.default_rng(SEED + 2)
    log("=" * 72)
    log("B2 — Toda-Yamamoto refeito (níveis, 1985–2024)")
    log("=" * 72)
    sel = VAR(np.column_stack([ag, pa])).select_order(maxlags=4, trend="c")
    log(f"  Seleção de defasagens do VAR em nível (maxlags=4): "
        f"AIC={sel.aic} BIC={sel.bic} HQIC={sel.hqic}")
    log(f"  Largura HAC fixa (Newey-West, 4(T/100)^(2/9)) = {NW_BW}, independente de d_max")

    # Dummies de degrau nas quebras de Lee-Strazicich (se o B1 já rodou).
    exog_sets = {"sem dummies": None}
    f_b1 = DIR_PROC / "banca60_B1_raiz_quebra.csv"
    if f_b1.exists():
        b1 = pd.read_csv(f_b1)
        anos_q = set()
        for nome in ("agric_Sul (nível)", "pasto_Norte (nível)"):
            r = b1[b1.serie == nome].iloc[0]
            anos_q.update(int(a) for a in str(r["ls_A_quebras"]).split("/"))
        # o ano publicado no B1 é o PRIMEIRO ano do novo regime (t > TB ⇔ índice ≥ TB)
        D = np.column_stack([(anos >= a).astype(float) for a in sorted(anos_q)])
        exog_sets[f"dummies de nível em {sorted(anos_q)}"] = D

    linhas = []
    for exnome, ex in exog_sets.items():
        log(f"\n  [{exnome}]")
        for rot, yv, xv in [("Sul→Norte (agric_Sul → pasto_Norte)", pa, ag),
                            ("REVERSO (pasto_Norte → agric_Sul)", ag, pa)]:
            for p in (1, 2):
                for dmax in (1, 2):
                    r = ty_test(yv, xv, p, dmax, ex)
                    t0 = time.time()
                    pb = ty_bootstrap(yv, xv, p, dmax, nboot, rng, ex)
                    linhas.append({"exog": exnome, "relacao": rot, "p": p, "dmax": dmax,
                                   "n_efetivo": r["n"],
                                   "W_ols": round(r["W_ols"], 3), "p_chi2_ols": round(r["p_ols"], 4),
                                   "W_hac": round(r["W_hac"], 3), "p_chi2_hac_bw3": round(r["p_hac"], 4),
                                   "p_bootstrap": round(pb, 4)})
                    log(f"    {rot:38s} p={p} dmax={dmax} n={r['n']:2d} | "
                        f"χ² OLS p={r['p_ols']:.3f} | χ² HAC(bw={NW_BW}) p={r['p_hac']:.3f} | "
                        f"bootstrap p={pb:.3f}  [{time.time()-t0:.0f}s]")
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B2_toda_yamamoto.csv", index=False)

    # Conferência da coluna n da Tabela de precedência (apêndice A).
    log("\n  Conferência do n: Granger em Δ com lag L usa 39 − L observações;")
    log("  T-Y em nível com k = p + dmax usa 40 − k. Com dmax=2: p=1 → n=37; p=2 → n=36.")
    log("  A tabela do apêndice traz 38/37 nas linhas de T-Y: é o n do Granger em Δ.")
    log.salvar()
    return out


# ===========================================================================
# B3 — Poder do procedimento usado
# ===========================================================================

def ar1_coef(z: np.ndarray) -> tuple[float, float]:
    z0 = z - z.mean()
    b = float(z0[1:] @ z0[:-1] / (z0[:-1] @ z0[:-1]))
    return b, float(np.std(z0[1:] - b * z0[:-1], ddof=1))


def granger_diff_p(dy, dx, lag=1) -> float:
    yy, X, names, ok = ty_design(dy, dx, lag)
    beta, resid, xtx_inv = ols(yy, X)
    n, k = X.shape
    s2 = resid @ resid / (n - k)
    idx = [names.index(f"x_l{i+1}") for i in range(lag)]
    W, _ = wald(beta, s2 * xtx_inv, idx)
    return float(stats.f.sf(W / lag, lag, n - k))      # mesma forma do ssr F-test


def bloco_B3(nrep: int = 2000) -> pd.DataFrame:
    log = Log("B3")
    s = carregar_regionais()
    dag = np.diff(s["agric_mha_Sul"].to_numpy())
    dpa = np.diff(s["pasto_mha_Norte"].to_numpy())
    rho_x, _ = ar1_coef(dag)
    phi_y, _ = ar1_coef(dpa)
    T = 40
    log("=" * 72)
    log("B3 — Poder: Granger em Δ (o que o texto simulou) × Toda-Yamamoto em nível")
    log("=" * 72)
    log(f"  DGP calibrado: Δx AR(1) ρ={rho_x:.2f} (Δagric_Sul); Δy AR(1) φ={phi_y:.2f} (Δpasto_Norte)")
    log("  Δy_t = φΔy_{t-1} + r·z_{t-1} + √(1−r²)·e_t, z = Δx padronizado; níveis = soma acumulada,")
    log("  com 50 observações de aquecimento descartadas. r é o coeficiente padronizado do efeito")
    log("  (não exatamente a correlação parcial, pois z pode correlacionar-se com o passado de y).")
    log("  Em nível o DGP tem ordem básica 2 (o mesmo p que AIC/BIC escolhem nos dados, B2), por isso")
    log("  o T-Y é testado com p = 2 além de p = 1. 'aj.' = poder ajustado ao tamanho: rejeição")
    log("  com o quantil 5% da distribuição nula simulada (r = 0) em vez de 0,05.")
    rng = np.random.default_rng(SEED + 3)
    BURN = 50
    testes = ["granger_dif", "ty_p1_d1", "ty_p1_d2", "ty_p2_d1", "ty_p2_d2", "ty_p2_d2_hac"]
    linhas = []
    for phi_nome, phi in ((f"φ estimado ({phi_y:.2f}, Δy quase integrada)", phi_y),
                          ("φ = 0,5 (Δy claramente estacionária)", 0.5)):
        log(f"\n  [{phi_nome}]")
        q_nula = None
        for r in (0.0, 0.2, 0.3, 0.4, 0.5):
            pv = {k: [] for k in testes}
            for _ in range(nrep):
                n_tot = T + BURN
                z = np.zeros(n_tot)
                u = rng.normal(size=n_tot)
                for t in range(1, n_tot):
                    z[t] = rho_x * z[t - 1] + u[t]
                z = (z - z.mean()) / z.std()
                e = rng.normal(size=n_tot)
                dy = np.zeros(n_tot)
                for t in range(1, n_tot):
                    dy[t] = phi * dy[t - 1] + r * z[t - 1] + np.sqrt(1 - r * r) * e[t]
                z, dy = z[BURN:], dy[BURN:]
                lx, ly = np.cumsum(z), np.cumsum(dy)
                pv["granger_dif"].append(granger_diff_p(dy[1:], z[1:]))
                pv["ty_p1_d1"].append(ty_test(ly, lx, 1, 1)["p_ols"])
                pv["ty_p1_d2"].append(ty_test(ly, lx, 1, 2)["p_ols"])
                pv["ty_p2_d1"].append(ty_test(ly, lx, 2, 1)["p_ols"])
                b = ty_test(ly, lx, 2, 2)
                pv["ty_p2_d2"].append(b["p_ols"]); pv["ty_p2_d2_hac"].append(b["p_hac"])
            pv = {k: np.array(v) for k, v in pv.items()}
            if r == 0.0:
                q_nula = {k: float(np.quantile(v, 0.05)) for k, v in pv.items()}
            row = {"phi": round(phi, 2), "r": r}
            for k in testes:
                row[k] = round(float((pv[k] < 0.05).mean()), 3)
                row[k + "_aj"] = round(float((pv[k] < q_nula[k]).mean()), 3)
            linhas.append(row)
            log(f"  r={r:.1f} | Granger Δ {row['granger_dif']:.0%} (aj. {row['granger_dif_aj']:.0%}) | "
                f"T-Y p1d2 {row['ty_p1_d2']:.0%} (aj. {row['ty_p1_d2_aj']:.0%}) | "
                f"T-Y p2d1 {row['ty_p2_d1']:.0%} (aj. {row['ty_p2_d1_aj']:.0%}) | "
                f"T-Y p2d2 {row['ty_p2_d2']:.0%} (aj. {row['ty_p2_d2_aj']:.0%}) | "
                f"p2d2 HAC {row['ty_p2_d2_hac']:.0%}"
                + ("   ← tamanho" if r == 0 else ""))
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B3_poder.csv", index=False)
    log.salvar()
    return out


# ===========================================================================
# B4 — sup-F calibrado
# ===========================================================================

def bloco_B4(nsim: int = 2000) -> pd.DataFrame:
    log = Log("B4")
    from periodizacao_multivariada import (sup_f_multivariado, binary_segmentation_mv,
                                           carregar_series, MIN_SIZE, F_THRESHOLD)
    Y, anos = carregar_series()
    n, p = Y.shape
    breaks = binary_segmentation_mv(Y, anos)
    log("=" * 72)
    log("B4 — sup-F multivariado: p calibrado sob VAR(1) e falso positivo")
    log("=" * 72)
    log(f"  Observado (#29): " + "; ".join(f"{b['ano_quebra']} F={b['f_stat']} p_F={b['p_value']}"
                                            f" seg {b['segmento']}" for b in breaks))

    # Nula: VAR(1) sobre os resíduos de média por segmento (quebras adotadas 2001 e 2020)
    # e, como alternativa conservadora, sobre a série só demeaned (sem quebras).
    def var1(E):
        X, Yt = E[:-1], E[1:]
        A = np.linalg.lstsq(X, Yt, rcond=None)[0].T
        U = Yt - X @ A.T
        return A, np.cov(U.T)

    seg_id = np.zeros(n, dtype=int)
    for a in (2001, 2020):
        seg_id += (anos >= a)
    E_seg = Y.copy()
    for g in np.unique(seg_id):
        E_seg[seg_id == g] -= Y[seg_id == g].mean(axis=0)
    # (a) nula global: VAR(1) da série inteira, sem quebra — referência direta para a nula de
    #     nenhuma quebra (pode absorver quebras reais na persistência estimada).
    # (b) sensibilidade: VAR(1) dos resíduos por segmento (usa as fronteiras adotadas e tende a
    #     subestimar a persistência sob a nula).
    nulas = {"(a) VAR(1) da série inteira, sem quebra (nula global)": var1(Y - Y.mean(axis=0)),
             "(b) VAR(1) dos resíduos por segmento (sensibilidade)": var1(E_seg)}
    BURN = 200
    rng = np.random.default_rng(SEED + 4)
    linhas = []
    for nome, (A, S) in nulas.items():
        eig = np.max(np.abs(np.linalg.eigvals(A)))
        log(f"\n  Nula: {nome} — raio espectral de A = {eig:.2f}")
        Lc = np.linalg.cholesky(S + 1e-12 * np.eye(p))

        def gera(m, A=A, Lc=Lc):
            e = rng.normal(size=(m + BURN, p)) @ Lc.T
            z = np.zeros((m + BURN, p))
            for t in range(1, m + BURN):
                z[t] = A @ z[t - 1] + e[t]
            return z[BURN:]

        # Distribuição do sup-F para os comprimentos de segmento de cada quebra observada
        for b in breaks:
            a0, a1 = (int(v) for v in b["segmento"].split("-"))
            m = int(((anos >= a0) & (anos <= a1)).sum())
            sims = np.array([sup_f_multivariado(gera(m), MIN_SIZE)["f_stat"] for _ in range(nsim)])
            p_cal = (np.sum(sims >= b["f_stat"]) + 1) / (nsim + 1)
            linhas.append({"nula": nome, "quebra": b["ano_quebra"], "segmento": b["segmento"],
                           "m": m, "F_obs": b["f_stat"], "p_F_convencional": b["p_value"],
                           "F_crit95_sim": round(float(np.quantile(sims, 0.95)), 2),
                           "p_calibrado": round(p_cal, 4)})
            log(f"    {b['ano_quebra']} (seg {b['segmento']}, m={m}): F={b['f_stat']:.1f} | "
                f"F crítico 95% simulado={np.quantile(sims, .95):.1f} | p calibrado={p_cal:.4f} "
                f"(p F convencional={b['p_value']})")
        # Falso positivo da segmentação completa com F ≥ 4
        nb = []
        for _ in range(nsim // 4):
            nb.append(len(binary_segmentation_mv(gera(n), anos)))
        nb = np.array(nb)
        linhas.append({"nula": nome, "quebra": "FPR binseg", "segmento": f"F≥{F_THRESHOLD}",
                       "m": n, "F_obs": np.nan, "p_F_convencional": np.nan,
                       "F_crit95_sim": np.nan, "p_calibrado": round(float((nb > 0).mean()), 3)})
        log(f"    Segmentação binária (F ≥ {F_THRESHOLD}) sem quebra verdadeira: "
            f"≥1 quebra em {(nb > 0).mean():.0%} das séries; média {nb.mean():.2f} quebras "
            f"[ruído branco no #29: 11%]")
    # (c) nula CONDICIONAL para as quebras de segunda ordem: o VAR(1) é estimado só dentro do
    #     segmento em que a quebra foi procurada (que já admite a quebra anterior, ex.: 2001,
    #     e exclui a testada, ex.: 2020). É a nula "2001 sim, 2020 não" sugerida pelo Codex.
    log("\n  Nula: (c) condicional — VAR(1) estimado no próprio segmento da quebra")
    for b in breaks:
        a0, a1 = (int(v) for v in b["segmento"].split("-"))
        msk = (anos >= a0) & (anos <= a1)
        if msk.sum() == n:
            continue                                # a primeira quebra não tem nula condicional
        A_c, S_c = var1(Y[msk] - Y[msk].mean(axis=0))
        Lc_c = np.linalg.cholesky(S_c + 1e-12 * np.eye(p))
        m = int(msk.sum())
        eig_c = np.max(np.abs(np.linalg.eigvals(A_c)))
        if eig_c >= 1.0:
            # VAR estimado no segmento é explosivo: não serve de nula estacionária. Registra e
            # não reporta p (o p = 1,00 que sairia é artefato da explosão, não evidência).
            linhas.append({"nula": "(c) condicional ao segmento", "quebra": b["ano_quebra"],
                           "segmento": b["segmento"], "m": m, "F_obs": b["f_stat"],
                           "p_F_convencional": b["p_value"], "F_crit95_sim": np.nan,
                           "p_calibrado": np.nan})
            log(f"    {b['ano_quebra']} (seg {b['segmento']}, m={m}): VAR(1) do segmento é explosivo "
                f"(raio espectral {eig_c:.2f}) ⇒ nula condicional não estimável com {m} anos")
            continue

        def gera_c(m, A=A_c, Lc=Lc_c):
            e = rng.normal(size=(m + BURN, p)) @ Lc.T
            z = np.zeros((m + BURN, p))
            for t in range(1, m + BURN):
                z[t] = A @ z[t - 1] + e[t]
            return z[BURN:]
        sims = np.array([sup_f_multivariado(gera_c(m), MIN_SIZE)["f_stat"] for _ in range(nsim)])
        p_cal = (np.sum(sims >= b["f_stat"]) + 1) / (nsim + 1)
        eig = np.max(np.abs(np.linalg.eigvals(A_c)))
        linhas.append({"nula": "(c) condicional ao segmento", "quebra": b["ano_quebra"],
                       "segmento": b["segmento"], "m": m, "F_obs": b["f_stat"],
                       "p_F_convencional": b["p_value"],
                       "F_crit95_sim": round(float(np.quantile(sims, 0.95)), 2),
                       "p_calibrado": round(p_cal, 4)})
        log(f"    {b['ano_quebra']} (seg {b['segmento']}, m={m}, raio espectral {eig:.2f}): "
            f"F={b['f_stat']:.1f} | F crítico 95%={np.quantile(sims, .95):.1f} | p calibrado={p_cal:.4f}")
    log("\n  Limite: simula-se o comprimento do segmento, não toda a seleção sequencial da")
    log("  segmentação binária; a estatística é a soma de SSR das três classes (não um Wald")
    log(f"  ponderado pela covariância). Aquecimento de {BURN} observações.")
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B4_supF_calibrado.csv", index=False)
    log.salvar()
    return out


# ===========================================================================
# B5 — CIPS no painel de AMCs
# ===========================================================================

def cips(Ymat: np.ndarray, trend: bool, plag: int = 1) -> tuple[float, int]:
    """CIPS de Pesaran (2007): média dos t de CADF. Ymat (T × N).
    Δy_it = a + [b·t] + ρ y_i,t-1 + c ȳ_{t-1} + Σ_{j=0}^{p} d_j Δȳ_{t-j} + Σ_{j=1}^{p} g_j Δy_i,t-j + e"""
    T, N = Ymat.shape
    ybar = Ymat.mean(axis=1)
    dyb = np.diff(ybar)
    ts = []
    for i in range(N):
        y = Ymat[:, i]
        dy = np.diff(y)
        rows = np.arange(plag, T - 1)          # índice em dy
        cols = [np.ones(len(rows))]
        if trend:
            cols.append(rows.astype(float))
        cols += [y[rows], ybar[rows]]
        j_rho = 2 if trend else 1
        for j in range(0, plag + 1):
            cols.append(dyb[rows - j])
        for j in range(1, plag + 1):
            cols.append(dy[rows - j])
        X = np.column_stack(cols)
        ts.append(tstat(dy[rows], X, j_rho))
    ts = np.array(ts)
    ts = ts[np.isfinite(ts)]
    return float(ts.mean()), len(ts)


def bloco_B5(nsim: int = 300) -> pd.DataFrame:
    log = Log("B5")
    a = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet").sort_values(["code_amc", "ano"])
    a["vegnat_ha"] = a[["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                        "lulc_campo_nativo_ha", "lulc_campo_alagado_ha"]].sum(axis=1)
    vars_ = {"pastagem": "lulc_pastagem_ha", "agricultura": "lulc_agricultura_ha",
             "mosaico": "lulc_mosaico_usos_ha", "vegetacao_natural": "vegnat_ha",
             "bovinos": "pec_bovinos_cab"}
    rng = np.random.default_rng(SEED + 5)
    log("=" * 72)
    log("B5 — CIPS (Pesaran 2007) no painel de AMCs, 1985–2024")
    log("=" * 72)
    cv_cache: dict = {}

    def cv(T, N, trend, plag):
        key = (T, N, trend, plag)
        if key not in cv_cache:
            t0 = time.time()
            sims = [cips(np.cumsum(rng.normal(size=(T, N)), axis=0), trend, plag)[0]
                    for _ in range(nsim)]
            cv_cache[key] = np.quantile(sims, [0.01, 0.05, 0.10])
            log(f"   [cv CIPS T={T} N={N} trend={trend} p={plag}: {nsim} sim em {time.time()-t0:.0f}s]")
        return cv_cache[key]

    linhas = []
    for nome, col in vars_.items():
        W = a.pivot(index="ano", columns="code_amc", values=col).sort_index()
        W = W.dropna(axis=1)
        W = W.loc[:, W.std() > 0] / 1e3                     # mil ha / mil cab
        for forma, M, trend in (("nível", W.to_numpy(), True),
                                ("Δ", np.diff(W.to_numpy(), axis=0), False)):
            for plag in (0, 1):
                stat, N = cips(M, trend, plag)
                c = cv(M.shape[0], N, trend, plag)
                linhas.append({"variavel": nome, "forma": forma, "tendencia": trend, "p_lags": plag,
                               "T": M.shape[0], "N": N, "CIPS": round(stat, 3),
                               "cv1": round(c[0], 3), "cv5": round(c[1], 3), "cv10": round(c[2], 3),
                               "rejeita_raiz_5pct": bool(stat < c[1])})
                log(f"  {nome:18s} {forma:5s} p={plag} N={N} | CIPS={stat:+.3f} cv5={c[1]:+.3f} → "
                    f"{'rejeita raiz (estacionária em parte das unidades)' if stat < c[1] else 'não rejeita raiz'}")
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B5_cips.csv", index=False)
    log("\nH0 do CIPS: raiz unitária em todas as unidades. Rejeitar não implica que todas")
    log("sejam estacionárias, só que uma fração não desprezível é.")
    log.salvar()
    return out


# ===========================================================================
# B6 — Efeitos fixos no modelo em Δ: poolabilidade e Mundlak
# ===========================================================================

def bloco_B6() -> pd.DataFrame:
    log = Log("B6")
    from linearmodels.panel import PanelOLS, RandomEffects
    a = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet").sort_values(["code_amc", "ano"])
    a["vegnat_ha"] = a[["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                        "lulc_campo_nativo_ha", "lulc_campo_alagado_ha"]].sum(axis=1)
    base = {"pasto": "lulc_pastagem_ha", "agric": "lulc_agricultura_ha",
            "vegnat": "vegnat_ha", "bov": "pec_bovinos_cab"}
    for k, c in base.items():
        a[f"d_{k}"] = a.groupby("code_amc")[c].diff() / (1e3 if k != "bov" else 1e3)
    specs = [("Δpastagem ~ Δagricultura (substituição)", "d_pasto", "d_agric"),
             ("Δveg. natural ~ Δpastagem (abertura)", "d_vegnat", "d_pasto"),
             ("Δbovinos ~ Δpastagem (lotação)", "d_bov", "d_pasto")]
    log("=" * 72)
    log("B6 — Modelo em Δ com efeitos de unidade e de ano: são necessários? FE × RE?")
    log("=" * 72)
    log("  Especificações representativas (não as 140 do painel); unidades em mil ha / mil cab.")
    linhas = []
    for rot, yv, xv in specs:
        d = a.dropna(subset=[yv, xv]).set_index(["code_amc", "ano"])
        fe = PanelOLS(d[yv], d[[xv]], entity_effects=True, time_effects=True).fit(
            cov_type="clustered", cluster_entity=True)
        te = PanelOLS(d[yv], d[[xv]], entity_effects=False, time_effects=True).fit(
            cov_type="clustered", cluster_entity=True)
        # F ANINHADO dos efeitos de unidade mantendo os de ano (corrigido 06/out: `f_pooled`
        # testava unidade E ano juntos contra o modelo sem efeito algum). Homocedástico.
        fp = fe.f_pooled                                   # conjunto, só para registro
        q = int(d.index.get_level_values(0).nunique()) - 1
        F_u = ((float(te.resid_ss) - float(fe.resid_ss)) / q) / (float(fe.resid_ss) / float(fe.df_resid))
        p_u = float(stats.f.sf(F_u, q, float(fe.df_resid)))
        # Mundlak: RE com média da explicativa por unidade + dummies de ano
        d2 = d.copy()
        d2["xbar"] = d2.groupby(level=0)[xv].transform("mean")
        anos_d = pd.get_dummies(d2.index.get_level_values(1), prefix="a", drop_first=True,
                                dtype=float)
        anos_d.index = d2.index
        X = pd.concat([d2[[xv, "xbar"]], anos_d], axis=1)
        X.insert(0, "const", 1.0)
        re = RandomEffects(d2[yv], X).fit(cov_type="clustered", cluster_entity=True)
        t_m, p_m = float(re.tstats["xbar"]), float(re.pvalues["xbar"])
        row = {"especificacao": rot, "n": int(fe.nobs), "beta_FE": round(float(fe.params[xv]), 4),
               "se_FE": round(float(fe.std_errors[xv]), 4),
               "beta_so_ano": round(float(te.params[xv]), 4),
               "F_unidade_dado_ano": round(F_u, 3), "p_F_unidade_dado_ano": round(p_u, 4),
               "F_conjunto_unidade_e_ano": round(float(fp.stat), 3),
               "mundlak_t_xbar": round(t_m, 3), "mundlak_p": round(p_m, 4)}
        linhas.append(row)
        log(f"\n  {rot}  (n={row['n']})")
        log(f"    β com efeito de unidade e ano = {row['beta_FE']:+.4f} (EP {row['se_FE']:.4f}) | "
            f"só ano = {row['beta_so_ano']:+.4f}")
        log(f"    F dos efeitos de unidade, mantidos os de ano (= tendências próprias em nível) = "
            f"{F_u:.2f}, p = {p_u:.4f}   [F conjunto unidade+ano = {float(fp.stat):.2f}]")
        log(f"    Mundlak (média de Δx por unidade no RE): t = {t_m:+.2f}, p = {p_m:.4f} → "
            f"{'restrição de RE rejeitada nesta equação' if p_m < 0.05 else 'restrição de RE não rejeitada (não prova exogeneidade)'}")
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B6_efeitos_fixos.csv", index=False)
    log.salvar()
    return out


# ===========================================================================
# B7 — Mistura × distribuição única, com truncamento da janela
# ===========================================================================

def _disc_probs(cdf, a_max_by_year, ages):
    """P(a | ano) = [F(a+½) − F(a−½)] / [F(A+½) − F(½)], a = 1..A (A = ano − 1986)."""
    lo = cdf(ages - 0.5); hi = cdf(ages + 0.5)
    pa = np.clip(hi - lo, 1e-300, None)
    return pa


def bloco_B7(nsub_rep: int = 100) -> pd.DataFrame:
    log = Log("B7")
    p = pd.read_parquet(DIR_PROC / "pastagem_idade_censo.parquet")
    nc = p[p.origem_anterior != "censurado_esquerda"]
    tab = nc.groupby(["ano_conversao", "idade_pastagem_anos"]).n_pixels.sum().reset_index()
    tab.columns = ["ano", "idade", "w"]
    tab["A"] = tab["ano"] - 1986
    assert (tab["idade"] <= tab["A"]).all(), "idade acima do limite da janela"
    W = tab["w"].to_numpy(float); a = tab["idade"].to_numpy(float); A = tab["A"].to_numpy(float)
    Ntot = W.sum()
    log("=" * 72)
    log("B7 — Idade da pastagem na conversão: mistura de 2 gaussianas × distribuições únicas")
    log("=" * 72)
    log(f"  Eventos com idade conhecida: {Ntot/1e6:.2f} milhões (pixels). Idade máx. observável = ano − 1986.")

    def comps(dist, th):
        """Lista de (log peso, distribuição congelada) do modelo."""
        E = np.exp
        if dist == "normal":
            return [(0.0, stats.norm(th[0], E(th[1])))]
        if dist == "gamma":
            return [(0.0, stats.gamma(E(th[0]), scale=E(th[1])))]
        if dist == "lognormal":
            return [(0.0, stats.lognorm(E(th[1]), scale=E(th[0])))]
        if dist == "weibull":
            return [(0.0, stats.weibull_min(E(th[0]), scale=E(th[1])))]
        if dist == "skewnormal":
            return [(0.0, stats.skewnorm(th[2], th[0], E(th[1])))]
        if dist == "mix2normal":
            lw1 = -np.logaddexp(0.0, -th[4]); lw2 = -np.logaddexp(0.0, th[4])
            return [(lw1, stats.norm(th[0], E(th[1]))), (lw2, stats.norm(th[2], E(th[3])))]
        raise ValueError(dist)

    NPAR = {"normal": 2, "gamma": 2, "lognormal": 2, "weibull": 2, "skewnormal": 3, "mix2normal": 5}

    def mk(dist):
        return NPAR[dist], None

    def log_interval(fz, lo, hi):
        """log P(lo < X ≤ hi), estável nas duas caudas."""
        with np.errstate(all="ignore"):
            lc_hi, lc_lo = fz.logcdf(hi), fz.logcdf(lo)
            ls_lo, ls_hi = fz.logsf(lo), fz.logsf(hi)
            via_cdf = lc_hi + np.log1p(-np.exp(lc_lo - lc_hi))
            via_sf = ls_lo + np.log1p(-np.exp(ls_hi - ls_lo))
            out = np.where(lc_hi < np.log(0.5), via_cdf, via_sf)
        # Sem piso (corrigido 06/out): o piso de −700 deixava numerador e denominador iguais
        # quando a massa ia toda para fora da janela, e a razão virava log 1 = 0 — um ajuste
        # "perfeito" falso que o otimizador explorava. Não finito agora é penalizado no nll.
        return out

    def n_piso(dist, th, a_, A_, truncated):
        lc = log_cond(dist, th, a_, A_, truncated)
        return int(np.sum(~np.isfinite(lc)))

    def log_prob(dist, th, lo, hi):
        parts = [lw + log_interval(fz, lo, hi) for lw, fz in comps(dist, th)]
        return parts[0] if len(parts) == 1 else np.logaddexp(*parts)

    starts = {"normal": [12, np.log(8)], "gamma": [np.log(2), np.log(6)],
              "lognormal": [np.log(10), np.log(0.8)], "weibull": [np.log(1.5), np.log(14)],
              "skewnormal": [3, np.log(12), 4],
              "mix2normal": [4, np.log(1.6), 16, np.log(7.5), np.log(0.33 / 0.67)]}

    def log_cond(dist, th, a_, A_, truncated):
        ln = log_prob(dist, th, a_ - 0.5, a_ + 0.5)
        ld = (log_prob(dist, th, 0.5, A_ + 0.5) if truncated
              else log_prob(dist, th, np.array([0.5]), np.array([np.inf])))
        return ln - ld

    def nll(th, dist, a_, A_, w_, truncated=True):
        lc = log_cond(dist, th, a_, A_, truncated)
        if not np.all(np.isfinite(lc)):
            return 1e6                       # parâmetro numericamente inválido: penalidade
        return -float(np.sum(w_ * lc) / np.sum(w_))   # por evento

    # Limites largos; o log registra se algum ajuste encostou neles.
    L = np.log
    bounds = {"normal": [(-50, 500), (L(.3), L(500))],
              "gamma": [(L(.05), L(50)), (L(.1), L(5000))],
              "lognormal": [(L(.5), L(5000)), (L(.05), L(10))],
              "weibull": [(L(.1), L(10)), (L(.5), L(5000))],
              "skewnormal": [(-50, 500), (L(.3), L(500)), (-50, 50)],
              "mix2normal": [(0, 15), (L(.3), L(20)), (3, 200), (L(.5), L(200)), (-8, 8)]}

    rng_ini = np.random.default_rng(SEED + 70)

    def fit(dist, a_, A_, w_, truncated=True, x_ini=None, n_rand=12):
        """Várias partidas (fixas + aleatórias uniformes nos limites); escolhe o menor nll
        entre as que convergiram (corrigido 06/out: a normal truncada parava em ótimo local)."""
        lo_b = np.array([b[0] for b in bounds[dist]]); hi_b = np.array([b[1] for b in bounds[dist]])
        inis = ([np.asarray(x_ini, float)] if x_ini is not None else
                [np.array(starts[dist], float) + j for j in (0.0, 0.3, -0.3)])
        inis += [lo_b + rng_ini.random(len(lo_b)) * (hi_b - lo_b) for _ in range(n_rand)]
        res = []
        for x0 in inis:
            x0 = np.clip(x0, lo_b, hi_b)
            r = optimize.minimize(nll, x0, args=(dist, a_, A_, w_, truncated),
                                  method="L-BFGS-B", bounds=bounds[dist],
                                  options={"maxiter": 5000})
            if np.isfinite(r.fun) and r.fun < 1e5:     # exclui a penalidade de inválidos
                res.append(r)
        if not res:
            raise RuntimeError(f"{dist}: nenhuma partida produziu ajuste numericamente válido")
        conv = [r for r in res if r.success]
        best = min(conv or res, key=lambda r: r.fun)
        best.sem_convergencia = not conv
        best.no_limite = bool(np.any(np.isclose(best.x, lo_b) | np.isclose(best.x, hi_b)))
        best.n_partidas = len(inis)
        best.n_conv = sum(bool(r.success) for r in res)
        return best

    # Histograma empírico marginal (agregado sobre os anos)
    emp = tab.groupby("idade").w.sum()
    emp = emp / emp.sum()
    ev_ano = tab.groupby("ano").w.transform("sum").to_numpy()

    def marginal(dist, th, truncated=True):
        pc = np.exp(log_cond(dist, th, a, A, truncated))
        exp = pd.Series(ev_ano * pc).groupby(tab["idade"].to_numpy()).sum()
        return exp / exp.sum()

    log(f"  Parcela empírica com idade ≤ 6 anos entre os eventos de idade conhecida: "
        f"{emp[emp.index <= 6].sum():.1%}")

    linhas = []
    sol_trunc = {}
    for truncated in (False, True):
        tag = "COM truncamento" if truncated else "SEM truncamento (como no #28C)"
        log(f"\n  [{tag}] ajuste no censo (ponderado por pixels)")
        for dist in ("normal", "gamma", "lognormal", "weibull", "skewnormal", "mix2normal"):
            r = fit(dist, a, A, W, truncated, n_rand=40)
            if truncated:
                sol_trunc[dist] = r.x
            k = mk(dist)[0]
            m = marginal(dist, r.x, truncated)
            tv = 0.5 * float(np.abs(m.reindex(emp.index).fillna(0) - emp).sum())
            ll_ev = -r.fun
            row = {"truncamento": truncated, "modelo": dist, "k": k,
                   "loglik_por_evento": round(ll_ev, 5), "dist_variacao_total": round(tv, 4),
                   "parametros": np.round(r.x, 3).tolist()}
            if dist == "mix2normal":
                w = 1 / (1 + np.exp(-r.x[4]))
                row["parametros"] = (f"μ1={r.x[0]:.2f} σ1={np.exp(r.x[1]):.2f} w1={w:.2f} | "
                                     f"μ2={r.x[2]:.2f} σ2={np.exp(r.x[3]):.2f}")
            linhas.append(row)
            row["parametro_no_limite"] = r.no_limite
            row["convergiu"] = not r.sem_convergencia
            row["celulas_no_piso"] = n_piso(dist, r.x, a, A, truncated)
            log(f"    {dist:11s} k={k} | log-lik/evento={ll_ev:.6f} | distância de variação total="
                f"{tv:.3f} | {row['parametros']}" + ("  [parâmetro no limite]" if r.no_limite else "")
                + f"  [{r.n_conv}/{r.n_partidas} partidas convergiram; piso: {row['celulas_no_piso']}]")
            if dist == "mix2normal" and truncated:
                (lw1, c1), (lw2, c2) = comps(dist, r.x)
                lden = log_prob(dist, r.x, 0.5, A + 0.5)
                w_cond = np.exp(lw1 + log_interval(c1, 0.5, A + 0.5) - lden)
                lnum = log_prob(dist, r.x, a - 0.5, a + 0.5)
                post1 = np.exp(lw1 + log_interval(c1, a - 0.5, a + 0.5) - lnum)
                pesos = {"w1_latente": 1 / (1 + np.exp(-r.x[4])),
                         "w1_condicional_media_eventos": float(np.sum(W * w_cond) / Ntot),
                         "w1_posterior_media_eventos": float(np.sum(W * post1) / Ntot),
                         "parcela_empirica_idade_le6": float(emp[emp.index <= 6].sum())}
                row.update({kk: round(v, 4) for kk, v in pesos.items()})
                log("      Três medidas do peso da componente jovem:")
                log(f"        peso latente (antes do corte da janela)        = {pesos['w1_latente']:.1%}")
                log(f"        peso médio dentro da janela de cada ano        = {pesos['w1_condicional_media_eventos']:.1%}")
                log(f"        fração dos eventos atribuída a ela (posterior) = {pesos['w1_posterior_media_eventos']:.1%}")
                log(f"        parcela empírica de idades ≤ 6 anos            = {pesos['parcela_empirica_idade_le6']:.1%}")

    # BIC em subamostras de tamanho realista (o argumento do texto: ΔBIC no censo mede n)
    log("\n  BIC em subamostras (com truncamento): quem ganha com n moderado?")
    log("  (sorteios independentes de eventos da distribuição agregada: sensibilidade ao tamanho")
    log("  de n, não correção para a dependência espacial ou temporal entre pixels)")
    rng = np.random.default_rng(SEED + 7)
    prob = W / W.sum()
    venc = []
    for nsub in (500, 2000, 10000):
        cont = {}
        for _ in range(nsub_rep):
            idx = rng.choice(len(W), size=nsub, p=prob)
            cnt = np.bincount(idx, minlength=len(W)).astype(float)
            m = cnt > 0
            bics = {}
            for dist in ("normal", "gamma", "lognormal", "weibull", "skewnormal", "mix2normal"):
                r = fit(dist, a[m], A[m], cnt[m], True, x_ini=sol_trunc[dist], n_rand=2)
                bics[dist] = 2 * r.fun * nsub + mk(dist)[0] * np.log(nsub)
            win = min(bics, key=bics.get)
            cont[win] = cont.get(win, 0) + 1
        venc.append({"n_sub": nsub, **{k: v / nsub_rep for k, v in cont.items()}})
        log(f"    n={nsub:6d}: vencedor por BIC → " +
            ", ".join(f"{k} {v/nsub_rep:.0%}" for k, v in sorted(cont.items(), key=lambda kv: -kv[1])))
    out = pd.DataFrame(linhas)
    out.to_csv(DIR_PROC / "banca60_B7_mistura.csv", index=False)
    pd.DataFrame(venc).to_csv(DIR_PROC / "banca60_B7_bic_subamostras.csv", index=False)
    log.salvar()
    return out


# ===========================================================================
# B8 — Direção da matriz W do SLX
# ===========================================================================

def bloco_B8() -> pd.DataFrame:
    log = Log("B8")
    import re
    src = (ROOT / "scripts" / "deslocamento_espacial.py").read_text(encoding="utf-8")
    linha = [l.strip() for l in src.splitlines() if 'direcao == "sul"' in l]
    log("=" * 72)
    log("B8 — Direção de W no SLX (#49, deslocamento_espacial.py)")
    log("=" * 72)
    log(f"  Código: {linha[0] if linha else '(não encontrado)'}")
    log("  ⇒ para a unidade i, entram em W_sul só os vizinhos j com y_j < y_i (ao SUL de i).")
    log("  Regressão: Δpasto_i ~ Δagric_i + (W_sul·Δagric)_i ⇒ a pastagem de i responde à")
    log("  lavoura dos vizinhos ao sul. O código implementa o mecanismo correto; a frase de")
    log("  07_apendice.tex:193 ('empurre a pastagem das unidades ao sul dela') está invertida.")
    log.salvar()
    return pd.DataFrame([{"codigo": linha[0] if linha else "", "direcao_codigo": "vizinhos ao sul de i",
                          "frase_apendice": "invertida"}])


BLOCOS = {"B1": bloco_B1, "B2": bloco_B2, "B3": bloco_B3, "B4": bloco_B4,
          "B5": bloco_B5, "B6": bloco_B6, "B7": bloco_B7, "B8": bloco_B8}

if __name__ == "__main__":
    pedidos = sys.argv[1:] or list(BLOCOS)
    for b in pedidos:
        t0 = time.time()
        BLOCOS[b]()
        print(f"[{b} concluído em {time.time()-t0:.0f}s]\n")
