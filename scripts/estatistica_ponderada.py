"""estatistica_ponderada.py — Pipeline #28

Estatística com pesos de frequência, para o censo de pixels
(`pastagem_idade_censo.parquet`), onde cada linha é uma célula
`(ano, muni, idade, classe) → n_pixels` e não uma observação.

## Contrato de correção

Toda função aqui **reduz exatamente** ao equivalente não-ponderado quando todos
os pesos são 1. Isso não é decoração: é o que permite rodar a mesma análise
sobre a amostra (peso=1) e sobre o censo (peso=n_pixels) e saber que qualquer
diferença nos resultados vem dos DADOS, não da troca de implementação.

`testa_equivalencia()` verifica esse contrato contra numpy/sklearn. Rode-o
sempre que mexer aqui:

    python scripts/estatistica_ponderada.py

## Sobre o quantil ponderado

Adota a convenção 'linear' do numpy generalizada: a i-ésima observação ordenada
recebe probabilidade acumulada p_i = (C_i − w_i) / (W − w_último), onde C é a
soma acumulada dos pesos e W o total. Com pesos iguais isso vira p_i = i/(n−1),
que é exatamente o que `np.quantile(..., method="linear")` usa. Convenções
diferentes de quantil discordam em até 1 ano nestes dados (a idade é inteira),
mas discordar do numpy quebraria a comparabilidade com tudo que já foi
publicado do #28.
"""
from __future__ import annotations

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np


def _ordena(v: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    v = np.asarray(v, dtype=float).ravel()
    w = np.asarray(w, dtype=float).ravel()
    if v.shape != w.shape:
        raise ValueError(f"valores {v.shape} e pesos {w.shape} incompatíveis")
    if np.any(w < 0):
        raise ValueError("peso negativo")
    o = np.argsort(v, kind="stable")
    return v[o], w[o]


def quantil(valores, pesos, q: float | np.ndarray):
    """Quantil ponderado, convenção 'linear' do numpy (ver docstring do módulo).

    Peso de FREQUÊNCIA: cada observação ocupa `w` vagas na ordenação, como a
    repetição faria. Um valor com peso 3 cobre o intervalo de probabilidade das
    3 posições que ocuparia se estivesse repetido — por isso cada observação
    gera DOIS pontos de quebra (início e fim da sua faixa), e a interpolação
    linear só acontece na transição entre valores distintos.

    Interpolar direto entre valores distintos (um ponto por valor) estaria
    errado: ignoraria quanta massa cada um carrega.
    """
    v, w = _ordena(valores, pesos)
    manter = w > 0
    v, w = v[manter], w[manter]
    if v.size == 0:
        return np.nan
    C = np.cumsum(w)
    N = C[-1]
    if v.size == 1 or N <= 1:
        return float(v[0]) if np.isscalar(q) else np.full(np.shape(q), float(v[0]))
    p_ini = (C - w) / (N - 1.0)          # primeira vaga desta observação
    p_fim = (C - 1.0) / (N - 1.0)        # última vaga desta observação
    pts_p = np.empty(2 * v.size)
    pts_v = np.empty(2 * v.size)
    pts_p[0::2], pts_p[1::2] = p_ini, p_fim
    pts_v[0::2], pts_v[1::2] = v, v
    return np.interp(q, pts_p, pts_v)


def mediana(valores, pesos) -> float:
    return float(quantil(valores, pesos, 0.5))


def media(valores, pesos) -> float:
    v, w = _ordena(valores, pesos)
    return float(np.sum(v * w) / np.sum(w)) if np.sum(w) else np.nan


def desvio(valores, pesos, ddof: int = 0) -> float:
    """Desvio-padrão ponderado. ddof=0 = populacional (o que `np.std` faz)."""
    v, w = _ordena(valores, pesos)
    tot = np.sum(w)
    if tot <= ddof:
        return np.nan
    m = np.sum(v * w) / tot
    return float(np.sqrt(np.sum(w * (v - m) ** 2) / (tot - ddof)))


def _log_normal(x: np.ndarray, mu: float, sig: float) -> np.ndarray:
    sig = max(sig, 1e-9)
    return -0.5 * np.log(2 * np.pi * sig * sig) - 0.5 * ((x - mu) / sig) ** 2


def gmm_ponderado(valores, pesos, n_comp: int = 2, max_iter: int = 500,
                  tol: float = 1e-8, seed: int = 42) -> dict:
    """Mistura de gaussianas 1-D por EM com pesos de frequência.

    Existe porque `sklearn.mixture.GaussianMixture` não aceita `sample_weight`,
    e expandir o censo para 44,6 milhões de linhas só para caber na API seria
    desperdício — a idade é inteira, então o censo inteiro tem no máximo 40
    valores distintos por recorte.

    Retorna mu/sigma/peso ordenados por mu crescente, log-verossimilhança, BIC e
    AIC. Convenção de nº de parâmetros: 2 para 1 componente (mu, sigma) e
    3k−1 para k componentes — a mesma que o #28 já usava, para o ΔBIC seguir
    comparável com o que foi publicado.
    """
    v, w = _ordena(valores, pesos)
    manter = w > 0
    v, w = v[manter], w[manter]
    n = float(np.sum(w))
    if v.size < n_comp or n <= 0:
        return {"ok": False}

    rng = np.random.default_rng(seed)
    if n_comp == 1:
        mu = np.array([media(v, w)])
        sig = np.array([max(desvio(v, w), 1e-6)])
        pi = np.array([1.0])
    else:
        qs = np.linspace(0.15, 0.85, n_comp)
        mu = np.asarray(quantil(v, w, qs), dtype=float)
        mu = mu + rng.normal(0, 1e-6, n_comp)  # desempata modos idênticos
        sig = np.full(n_comp, max(desvio(v, w), 1e-6))
        pi = np.full(n_comp, 1.0 / n_comp)

    ll_ant = -np.inf
    ll = -np.inf
    for _ in range(max_iter):
        # E: log-responsabilidades estabilizadas
        logp = np.stack([np.log(max(pi[k], 1e-300)) + _log_normal(v, mu[k], sig[k])
                         for k in range(n_comp)])
        mx = logp.max(axis=0)
        soma = mx + np.log(np.exp(logp - mx).sum(axis=0))
        resp = np.exp(logp - soma)
        ll = float(np.sum(w * soma))

        # M: pesos de frequência entram multiplicando as responsabilidades
        rw = resp * w
        Nk = rw.sum(axis=1)
        if np.any(Nk <= 0):
            break
        mu = (rw * v).sum(axis=1) / Nk
        sig = np.sqrt(np.maximum((rw * (v - mu[:, None]) ** 2).sum(axis=1) / Nk, 1e-12))
        pi = Nk / n

        if np.isfinite(ll_ant) and abs(ll - ll_ant) < tol * max(1.0, abs(ll_ant)):
            break
        ll_ant = ll

    o = np.argsort(mu)
    k_par = 2 if n_comp == 1 else 3 * n_comp - 1
    return {
        "ok": True,
        "mu": mu[o], "sigma": sig[o], "peso": pi[o],
        "loglik": ll, "n": n, "k": k_par,
        "bic": k_par * np.log(n) - 2 * ll,
        "aic": 2 * k_par - 2 * ll,
    }


def expandir(df, col_peso: str = "n_pixels"):
    """Replica cada linha `n_pixels` vezes. Só para recortes pequenos.

    Existe para casos em que uma biblioteca de terceiros não aceita peso. Cuidado:
    no censo inteiro isso são 44,6 milhões de linhas.
    """
    import pandas as pd  # noqa: F401  (import local: uso raro)
    return df.loc[df.index.repeat(df[col_peso].astype(int))].drop(columns=[col_peso])


# ---------------------------------------------------------------- validação
def testa_equivalencia() -> bool:
    """Confere o contrato: com peso=1, tudo bate com numpy/sklearn."""
    rng = np.random.default_rng(0)
    ok = True

    print("1. quantil/mediana/media/desvio com peso=1 vs numpy")
    for tam in (1, 2, 5, 40, 999, 1000):
        x = rng.integers(0, 40, tam).astype(float)
        w = np.ones(tam)
        for q in (0.0, 0.10, 0.25, 0.5, 0.75, 0.90, 1.0):
            a, b = quantil(x, w, q), np.quantile(x, q, method="linear")
            if not np.isclose(a, b, atol=1e-9):
                print(f"   FALHA quantil n={tam} q={q}: {a} vs {b}"); ok = False
        if not np.isclose(media(x, w), x.mean(), atol=1e-9):
            print(f"   FALHA media n={tam}"); ok = False
        if not np.isclose(desvio(x, w), x.std(), atol=1e-9):
            print(f"   FALHA desvio n={tam}"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("2. peso inteiro equivale a repetir a observação")
    x = rng.integers(0, 40, 60).astype(float)
    w = rng.integers(1, 9, 60).astype(float)
    xe = np.repeat(x, w.astype(int))
    for q in (0.10, 0.25, 0.5, 0.75, 0.90):
        a, b = quantil(x, w, q), np.quantile(xe, q, method="linear")
        if not np.isclose(a, b, atol=1e-9):
            print(f"   FALHA quantil ponderado q={q}: {a} vs {b}"); ok = False
    if not np.isclose(media(x, w), xe.mean(), atol=1e-9):
        print("   FALHA media ponderada"); ok = False
    if not np.isclose(desvio(x, w), xe.std(), atol=1e-9):
        print("   FALHA desvio ponderado"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("3. GMM ponderado vs sklearn (peso=1 e peso inteiro)")
    try:
        from sklearn.mixture import GaussianMixture
    except ImportError:
        print("   sklearn ausente — pulado")
        return ok
    # mistura sintética com dois modos bem separados
    a1 = rng.normal(5, 2, 4000)
    a2 = rng.normal(22, 7, 3000)
    x = np.concatenate([a1, a2])
    r = gmm_ponderado(x, np.ones(x.size), 2)
    g = GaussianMixture(2, random_state=42, max_iter=500, tol=1e-8).fit(x.reshape(-1, 1))
    o = np.argsort(g.means_.ravel())
    dmu = np.abs(r["mu"] - g.means_.ravel()[o]).max()
    dpi = np.abs(r["peso"] - g.weights_[o]).max()
    dll = abs(r["loglik"] - g.score(x.reshape(-1, 1)) * x.size)
    print(f"   peso=1: dif mu {dmu:.2e} | dif peso {dpi:.2e} | dif loglik {dll:.2e}")
    if dmu > 1e-3 or dpi > 1e-3 or dll > 1e-2:
        print("   FALHA: divergiu do sklearn"); ok = False

    # peso inteiro deve bater com a versão expandida
    xs = rng.integers(0, 40, 300).astype(float)
    ws = rng.integers(1, 20, 300).astype(float)
    xexp = np.repeat(xs, ws.astype(int))
    rp = gmm_ponderado(xs, ws, 2)
    re = gmm_ponderado(xexp, np.ones(xexp.size), 2)
    dmu2 = np.abs(rp["mu"] - re["mu"]).max()
    dbic = abs(rp["bic"] - re["bic"])
    print(f"   peso inteiro vs expandido: dif mu {dmu2:.2e} | dif BIC {dbic:.2e}")
    if dmu2 > 1e-6 or dbic > 1e-6:
        print("   FALHA: peso != repetição"); ok = False

    print("\nTODOS OS TESTES PASSARAM" if ok else "\n*** HÁ FALHAS ***")
    return ok


if __name__ == "__main__":
    sys.exit(0 if testa_equivalencia() else 1)
