"""bimodalidade_regional.py — Pipeline #28C (decomposição within/between)
========================================================================

PERGUNTA QUE RESPONDE
---------------------
A bimodalidade da idade da pastagem na conversão (#28: picos em ~5 e ~22 anos)
é "regionalmente causada"? Ou seja, ela é uma COMPOSIÇÃO entre regiões unimodais
(Sul jovem × Norte velho), ou uma COEXISTÊNCIA dos dois mecanismos DENTRO de
cada região, apenas com peso de mistura diferente?

A distinção é decisiva para a redação (Decisão D14): "regionalmente causada"
exige que cada região seja internamente unimodal e que a bimodalidade do
agregado venha só da mistura de regiões. Se cada região é, ela mesma, bimodal,
a geografia MODULA o peso — não CAUSA a bimodalidade.

CONFUNDIDOR EXPLÍCITO: o tempo. O Ato I converte pasto jovem (mediana 6a) e o
Ato II/III convertem pasto velho (~19a); logo, parte da "bimodalidade" agregada
é TEMPORAL, não regional. Por isso a célula região×ato é o teste decisivo:
dentro de uma única região E um único ato, ainda há dois modos?

TESTES
------
  1. Decomposição de variância (η²) da idade não-censurada por:
     região | ato | região×ato  → quanto cada eixo "explica" da variância.
  2. GMM 1c vs 2c por mesorregião (reusa ajustar_gmm_unidim do #28):
     cada região continua bimodal (ΔBIC>10 + modos separados)?
  3. GMM 1c vs 2c por célula região×ato (Ato II e III): isola a coexistência
     pura do confundidor temporal.
  4. Coeficiente de bimodalidade de Sarle (model-free) por região e célula,
     como corroboração independente do GMM.
  5. η² da pertinência ao modo "velho" (responsabilidade posterior do GMM
     GLOBAL, rótulos consistentes) por região, ato e célula → a parcela
     BETWEEN vs WITHIN da separação jovem/velho.

VEREDITO
--------
Se (a) as células região×ato permanecem bimodais e (b) o WITHIN domina o η² da
pertinência ao modo velho, então a bimodalidade NÃO é regionalmente causada:
é coexistência dos dois mecanismos modulada por um gradiente Sul→Norte no peso
da mistura. (Coerente com a leitura honesta da D14.)

PESO — POR QUE TODA ESTATÍSTICA AQUI É PONDERADA (21/jul/2026)
--------------------------------------------------------------
Desde que o #28 virou censo, `carregar()` devolve uma **tabela de contingência**:
cada linha é a célula `(ano, muni, idade, classe)` e a coluna `peso` diz quantos
pixels ela representa. Uma linha NÃO é uma observação.

Este script rodava sem peso. Como `carregar()` passou a defaultar para o censo,
ele leria 405.771 células como se fossem 405.771 pixels de peso igual — o que
sobrepondera brutalmente as combinações raras. O efeito medido no gradiente
mediano Sul→Norte por mesorregião:

    sem peso (errado):  Sul 10 · Centro 10 · Leste 11 · Noroeste 12 · Norte 12
    com peso (certo):   Sul  9 · Centro  9 · Leste 10 · Noroeste 16 · Norte 16

Isto é, o gradiente Sul→Norte — que é o achado — DESAPARECE sem o peso. Por isso
toda função estatística deste módulo recebe `w` explicitamente; nenhuma usa
`np.median`, `.mean()` ou `len()` sobre as linhas. Ver D24 em
`Textos/metodologia/censo_vs_amostra.md`.

ENTRADAS
    data/processed/pastagem_idade_censo.parquet   (#28 censo, padrão)
    data/processed/pastagem_idade_conversao.csv   (#28A amostra, via --fonte amostra)

SAÍDAS  (sufixo `_amc` na malha AMC)
    data/processed/idade_bimodalidade_por_grupo[_amc].csv     (GMM+BC por unidade e célula)
    data/processed/idade_bimodalidade_decomposicao[_amc].csv  (η²/ω² variância + modo velho + permutação)
    outputs/idade_pastagem/bimodalidade_unidade_ato[_amc].png (grid unidade×{todos,II,III})

COMO RODAR
    python scripts/bimodalidade_regional.py                 # malha mesorregião (5)
    python scripts/bimodalidade_regional.py --malha amc     # malha AMC (164)
    python scripts/bimodalidade_regional.py --fonte amostra # reproduz os números de jun/2026
    python scripts/bimodalidade_regional.py --sem-figuras

Depende de: #28 (censo ou amostra) e reusa o GMM ponderado do #28
(analise_reserva_terra.ajustar_gmm_unidim); na malha AMC, o crosswalk do #25
(amc_crosswalk_goias.csv). Quando foi feito: 2026-06-07/08;
migrado para censo/peso em 2026-07-21.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS                                    # noqa: E402
from analise_reserva_terra import carregar, ajustar_gmm_unidim      # noqa: E402
from estatistica_ponderada import (                                 # noqa: E402
    mediana as mediana_p, gmm_ponderado,
)

ROOT    = Path(__file__).resolve().parent.parent
DIR_OUT = ROOT / "outputs" / "idade_pastagem"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_PROC = ROOT / "data" / "processed"

# Critérios para chamar uma distribuição de "bimodal" (todos precisam valer):
BIC_MIN      = 10.0   # ΔBIC = bic_1c - bic_2c > 10  → evidência forte p/ 2 comp.
SEP_MIN      = 5.0    # separação mínima entre modos (anos): evita 2-gaussianas que
                      #   só modelam assimetria de uma unimodal
PESO_MIN     = 0.15   # peso mínimo do componente menor (modo não-trivial)
N_CONFIAVEL  = 50     # abaixo disso, o ajuste é frágil (flag, não descarte)


# ---------------------------------------------------------------------------
# Estatísticas auxiliares
# ---------------------------------------------------------------------------

def _decompor(df: pd.DataFrame, value_col: str, group_cols,
              w_col: str = "peso") -> tuple[float, float, float, float]:
    """Devolve (SS_entre, SS_total, W, k) com pesos de FREQUÊNCIA.

    Com peso de frequência, W = Σw é o número de observações (pixels), não o
    número de linhas — é o que faz a soma de quadrados ser a do dado real e não
    a da tabela que o armazena. Com w≡1 tudo reduz ao caso clássico.
    """
    v = df[value_col].to_numpy(float)
    w = df[w_col].to_numpy(float)
    W = float(w.sum())
    if W <= 0:
        return float("nan"), float("nan"), 0.0, 0
    grand = float(np.sum(v * w) / W)
    ss_total = float(np.sum(w * (v - grand) ** 2))

    cols = [group_cols] if isinstance(group_cols, str) else list(group_cols)
    d = pd.DataFrame({"__w": w, "__vw": v * w})
    for i, c in enumerate(cols):
        d[f"__g{i}"] = df[c].to_numpy()
    gb = d.groupby([f"__g{i}" for i in range(len(cols))], observed=True)[["__w", "__vw"]].sum()
    gb = gb[gb["__w"] > 0]
    media_g = gb["__vw"].to_numpy() / gb["__w"].to_numpy()
    ss_between = float(np.sum(gb["__w"].to_numpy() * (media_g - grand) ** 2))
    return ss_between, ss_total, W, int(len(gb))


def eta_squared(df: pd.DataFrame, value_col: str, group_cols,
                w_col: str = "peso") -> float:
    """η² = SS_entre / SS_total, ponderado (fração da variância de `value_col`
    explicada por pertencer ao grupo)."""
    ss_b, ss_t, _W, _k = _decompor(df, value_col, group_cols, w_col)
    if not (ss_t > 0):
        return float("nan")
    return float(ss_b / ss_t)


def omega_squared(df: pd.DataFrame, value_col: str, group_cols,
                  w_col: str = "peso") -> float:
    """ω² (omega-quadrado): effect-size de variância explicada CORRIGIDO para o
    número de grupos. Ao contrário do η², não infla mecanicamente quando há mais
    grupos (pode até ficar negativo se o agrupamento não explica nada além do
    acaso). É a métrica honesta para comparar 5 mesorregiões vs ~150 AMCs.

    ATENÇÃO (D23) — sob o CENSO a correção perde a mordida. O termo corretivo é
    (k−1)·MS_within, e MS_within não encolhe com W enquanto SS_entre cresce
    proporcionalmente a W. Com W na casa dos milhões e k≤164, ω² ≈ η² até a
    terceira casa. Isso NÃO significa que o agrupamento passou a explicar mais:
    significa que a correção para nº de grupos era um ajuste de amostra pequena
    e virou irrelevante. A comparação meso×AMC continua válida pelo η² líquido
    de acaso (`perm_eta`), não por ω².
    """
    ss_b, ss_t, W, k = _decompor(df, value_col, group_cols, w_col)
    if not (ss_t > 0):
        return float("nan")
    gl_within = W - k
    if gl_within <= 0:
        return float("nan")
    ms_within = (ss_t - ss_b) / gl_within
    return float((ss_b - (k - 1) * ms_within) / (ss_t + ms_within))


def perm_eta(df: pd.DataFrame, value_col: str, group_col: str,
             B: int = 200, seed: int = 42, w_col: str = "peso") -> dict:
    """Linha-base de permutação para η²: sob H0 (rótulo espacial ⊥ valor), qual
    η² se obtém por acaso com aquele número/tamanho de grupos? É o piso mecânico
    contra o qual o η² observado deve ser comparado.

    PERMUTA EVENTOS, NÃO LINHAS — e a diferença importa
    ----------------------------------------------------
    A versão original embaralhava os rótulos das LINHAS. Sobre a amostra
    (1 linha = 1 pixel) isso era permutação de eventos e estava certo. Sobre o
    censo, 1 linha = 1 célula com `peso` pixels, e embaralhar linhas seria uma
    permutação de BLOCOS: manteria juntos todos os pixels que compartilham
    (ano, muni, idade, classe) e randomizaria os tamanhos de grupo. Isso testa
    outra hipótese nula — mais frouxa — e infla o piso do acaso.

    Aqui a permutação é feita no nível do evento, mantendo os tamanhos de grupo
    W_g fixos, via sorteio hipergeométrico multivariado sobre o pool de valores
    distintos. Como a idade é inteira (≤41 valores) e `p_velho` é função
    determinística da idade (logo também ≤41 valores), o pool é minúsculo e o
    sorteio exato é barato — não é aproximação.

    D23 — SOB CENSO ESTE TESTE É VESTIGIAL
    ---------------------------------------
    O valor esperado de η² sob H0 é ≈ (k−1)/(W−1). Com W = 16 milhões e k = 5,
    isso é ~2,5e−7: o piso do acaso colapsa para zero, "líquido de acaso" vira
    igual ao observado e p_perm vira 0,005 (o mínimo com B=200) para qualquer
    sinal não-nulo. Isso NÃO é evidência forte — é n grande, exatamente como o
    ΔBIC da D23. O piso analítico vai no retorno (`eta2_acaso_analitico`) para
    deixar a degeneração visível em vez de implícita.
    """
    rng = np.random.default_rng(seed)
    obs = eta_squared(df, value_col, group_col, w_col)
    ss_b, ss_total, W, k = _decompor(df, value_col, group_col, w_col)
    if not (ss_total > 0) or k < 2:
        return {"eta2_obs": float(obs), "eta2_acaso_medio": float("nan"),
                "eta2_acaso_p95": float("nan"), "eta2_acaso_analitico": float("nan"),
                "eta2_liquido": float("nan"), "p_perm": float("nan"), "B": 0}

    v = df[value_col].to_numpy(float)
    w = df[w_col].to_numpy(float)
    grand = float(np.sum(v * w) / W)

    # Pool de eventos por valor distinto (a permutação vive aqui, não nas linhas)
    vals, inv = np.unique(v, return_inverse=True)
    pool = np.rint(np.bincount(inv, weights=w, minlength=vals.size)).astype(np.int64)

    # Tamanhos de grupo, em eventos
    Wg = df.groupby(group_col, observed=True)[w_col].sum()
    Wg = np.rint(Wg[Wg > 0].to_numpy()).astype(np.int64)
    # Reconcilia arredondamento (só morde se algum peso for fracionário)
    delta = int(pool.sum() - Wg.sum())
    if delta:
        Wg[int(np.argmax(Wg))] += delta

    nulos = np.empty(B)
    for b in range(B):
        restante = pool.copy()
        ssb = 0.0
        for g in range(Wg.size - 1):
            if Wg[g] <= 0:
                continue
            sorteio = rng.multivariate_hypergeometric(restante, int(Wg[g]))
            restante -= sorteio
            m = float(np.sum(sorteio * vals) / Wg[g])
            ssb += Wg[g] * (m - grand) ** 2
        sobra = int(restante.sum())
        if sobra > 0:
            m = float(np.sum(restante * vals) / sobra)
            ssb += sobra * (m - grand) ** 2
        nulos[b] = ssb / ss_total

    pval = float((np.sum(nulos >= obs) + 1) / (B + 1))
    return {"eta2_obs": float(obs), "eta2_acaso_medio": float(nulos.mean()),
            "eta2_acaso_p95": float(np.quantile(nulos, 0.95)),
            "eta2_acaso_analitico": float((k - 1) / (W - 1)) if W > 1 else float("nan"),
            "eta2_liquido": float(obs - nulos.mean()), "p_perm": pval, "B": B}


def bimodality_coef(x: np.ndarray, w: np.ndarray | None = None) -> float:
    """Coeficiente de bimodalidade de Sarle (model-free), ponderado.
    BC > 5/9≈0.555 sugere bimodalidade (ou caudas mais leves que a normal);
    ≤0.555 sugere unimodal.

    Reimplementa as correções de viés de `scipy.stats.skew(bias=False)` e
    `kurtosis(fisher=True, bias=False)` com n → W = Σw, porque o scipy não aceita
    peso de frequência. Com w≡1 devolve exatamente o que o scipy devolvia (o teste
    de contrato em `_testa_contrato_peso` verifica isso).
    """
    x = np.asarray(x, dtype=float).ravel()
    w = np.ones_like(x) if w is None else np.asarray(w, dtype=float).ravel()
    manter = w > 0
    x, w = x[manter], w[manter]
    W = float(w.sum())
    if W < 4 or x.size < 2:
        return float("nan")

    m = float(np.sum(w * x) / W)
    d = x - m
    m2 = float(np.sum(w * d ** 2) / W)
    if m2 <= 0:
        return float("nan")
    m3 = float(np.sum(w * d ** 3) / W)
    m4 = float(np.sum(w * d ** 4) / W)

    g1 = m3 / m2 ** 1.5                     # assimetria enviesada
    g2 = m4 / m2 ** 2 - 3.0                 # curtose-excesso enviesada
    G1 = np.sqrt(W * (W - 1)) / (W - 2) * g1
    G2 = ((W + 1) * g2 + 6) * (W - 1) / ((W - 2) * (W - 3))

    denom = G2 + 3.0 * (W - 1) ** 2 / ((W - 2) * (W - 3))
    if denom <= 0:
        return float("nan")
    return float((G1 ** 2 + 1.0) / denom)


def avaliar_grupo(escopo: str, chave: str, x: np.ndarray,
                  w: np.ndarray | None = None) -> dict:
    """Ajusta GMM 1c/2c (método do #28) + BC de Sarle e classifica bimodalidade.

    `n` é o número de EVENTOS (Σw), não de linhas: sob o censo uma linha é uma
    célula da tabela de contingência. `n_celulas` vai junto para o leitor
    distinguir "muitos pixels" de "muitas combinações distintas".
    """
    x = np.asarray(x, dtype=float).ravel()
    w = np.ones_like(x) if w is None else np.asarray(w, dtype=float).ravel()
    n = float(w.sum())
    g = ajustar_gmm_unidim(x, w)
    delta_bic = g["bic_1c"] - g["bic_2c"]
    sep       = abs(g["mu2"] - g["mu1"])
    peso_menor = min(g["w1"], g["w2"])
    bc = bimodality_coef(x, w)
    bimodal = (delta_bic > BIC_MIN) and (sep > SEP_MIN) and (peso_menor > PESO_MIN)
    return {
        "escopo": escopo, "chave": chave, "n": int(round(n)),
        "n_celulas": int(x.size),
        "mediana": float(mediana_p(x, w)),
        "mu_jovem": round(g["mu1"], 1), "w_jovem": round(g["w1"], 3),
        "mu_velho": round(g["mu2"], 1), "w_velho": round(g["w2"], 3),
        "separacao_anos": round(sep, 1),
        "delta_bic": round(delta_bic, 1),
        "bc_sarle": round(bc, 3) if bc == bc else None,
        "bimodal": bool(bimodal),
        "confiavel": bool(n >= N_CONFIAVEL),
    }


# ---------------------------------------------------------------------------
# Posterior do modo "velho" (GMM global, rótulos consistentes)
# ---------------------------------------------------------------------------

def posterior_modo_velho(x: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """Responsabilidade posterior P(componente velho | idade) de UM GMM global
    de 2 componentes. Rótulo 'velho' = componente de maior média (consistente
    para todos os pixels — evita label-switching entre subamostras).

    Ajusta com `gmm_ponderado` (EM com peso de frequência) em vez de
    `sklearn.GaussianMixture`, que não aceita `sample_weight`: sob o censo, o
    ajuste sem peso trataria cada célula da tabela como um pixel. O posterior em
    si é função determinística da idade, então é calculado analiticamente a
    partir de (μ, σ, π) — não precisa de `predict_proba`.
    """
    x = np.asarray(x, dtype=float).ravel()
    w = np.ones_like(x) if w is None else np.asarray(w, dtype=float).ravel()
    r = gmm_ponderado(x, w, n_comp=2)
    if not r.get("ok"):
        return np.full(x.shape, np.nan)
    mu, sig, pi = r["mu"], r["sigma"], r["peso"]
    iv = int(np.argmax(mu))

    # log π_k + log N(x; μ_k, σ_k), normalizado de forma estável
    logp = np.stack([
        np.log(max(pi[k], 1e-300))
        - 0.5 * np.log(2 * np.pi * max(sig[k], 1e-9) ** 2)
        - 0.5 * ((x - mu[k]) / max(sig[k], 1e-9)) ** 2
        for k in range(2)
    ])
    mx = logp.max(axis=0)
    return np.exp(logp[iv] - (mx + np.log(np.exp(logp - mx).sum(axis=0))))


# ---------------------------------------------------------------------------
# Figura: grid região × {todos, Ato II, Ato III}
# ---------------------------------------------------------------------------

def fig_grid(df_nc: pd.DataFrame, unidades: list, col_esp: str = "mesorregiao",
             lab_fn=str, outname: str = "bimodalidade_unidade_ato.png") -> None:
    import matplotlib.pyplot as plt
    from scipy.stats import norm

    cols = [("Todos os anos", None),
            ("Ato II (2001–2019)", "II"),
            ("Ato III (2020–2024)", "III")]
    bins = np.arange(0, 41, 2)
    xs = np.linspace(0, 40, 400)

    fig, axes = plt.subplots(len(unidades), len(cols),
                             figsize=(4.3 * len(cols), 2.7 * len(unidades)),
                             sharex=True, sharey=True)
    axes = np.atleast_2d(axes)
    for i, reg in enumerate(unidades):
        for j, (titulo, ato) in enumerate(cols):
            ax = axes[i, j]
            sub = df_nc[df_nc[col_esp] == reg]
            if ato is not None:
                sub = sub[sub["ato"] == ato]
            x = sub["idade_pastagem_anos"].to_numpy(float)
            ww = sub["peso"].to_numpy(float)
            n_ev = float(ww.sum())
            if n_ev < 5 or x.size < 2:
                ax.text(0.5, 0.5, "n<5", ha="center", va="center",
                        transform=ax.transAxes, color="0.6")
                ax.set_axis_off()
                continue
            # `weights` é o que faz o histograma ser dos PIXELS e não das células
            ax.hist(x, bins=bins, weights=ww, density=True, color="#dcdcd6",
                    edgecolor="white", alpha=0.9)
            g = ajustar_gmm_unidim(x, ww)
            y1 = g["w1"] * norm.pdf(xs, g["mu1"], max(g["sig1"], 0.3))
            y2 = g["w2"] * norm.pdf(xs, g["mu2"], max(g["sig2"], 0.3))
            ax.plot(xs, y1 + y2, color="#8a3068", lw=2.0)
            ax.plot(xs, y1, "--", color="#d95f02", lw=1.2)
            ax.plot(xs, y2, "--", color="#1b9e77", lw=1.2)
            dbic = g["bic_1c"] - g["bic_2c"]
            bc = bimodality_coef(x, ww)
            sep = abs(g["mu2"] - g["mu1"])
            bimodal = (dbic > BIC_MIN) and (sep > SEP_MIN) and (min(g["w1"], g["w2"]) > PESO_MIN)
            marca = "● bimodal" if bimodal else "○ unimodal"
            ax.text(0.97, 0.95, f"n={n_ev:,.0f}\nΔBIC={dbic:.0f}\nBC={bc:.2f}\n{marca}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
                    color="#333")
            if i == 0:
                ax.set_title(titulo, fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{lab_fn(reg)}\n(mediana {mediana_p(x, ww):.0f}a)", fontsize=8.5)
    for ax in axes[-1, :]:
        ax.set_xlabel("Idade na conversão (anos)", fontsize=8.5)
    fig.suptitle("Bimodalidade da idade do pasto DENTRO de cada unidade espacial e ato\n"
                 "— mistura GMM, -- componentes; ● = bimodal (ΔBIC>10, modos>5a, peso>0,15)",
                 fontsize=12, y=0.997)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = DIR_OUT / outname
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Contrato D24 — as versões ponderadas reduzem ao caso não-ponderado
# ---------------------------------------------------------------------------

def _testa_contrato_peso() -> bool:
    """Confere que peso≡1 reproduz a implementação antiga, e que peso inteiro
    equivale a repetir a observação.

    É o mesmo contrato da D24 (`estatistica_ponderada.testa_equivalencia`),
    aplicado às estatísticas que vivem AQUI (η², ω², BC de Sarle, permutação) e
    que não passam por aquele módulo. Sem isto, não há como distinguir "o número
    mudou porque virou censo" de "o número mudou porque reimplementei errado".

        python scripts/bimodalidade_regional.py --testar
    """
    from scipy.stats import skew, kurtosis
    rng = np.random.default_rng(0)
    ok = True

    print("1. η²/ω² com peso=1 vs fórmula clássica não-ponderada")
    x = rng.integers(0, 40, 400).astype(float)
    g = rng.integers(0, 5, 400)
    d = pd.DataFrame({"v": x, "g": g, "peso": 1.0})
    grand = x.mean()
    ss_t = np.sum((x - grand) ** 2)
    ss_b = sum(len(x[g == u]) * (x[g == u].mean() - grand) ** 2 for u in np.unique(g))
    if not np.isclose(eta_squared(d, "v", "g"), ss_b / ss_t, atol=1e-12):
        print("   FALHA η²"); ok = False
    k = len(np.unique(g))
    ms_w = (ss_t - ss_b) / (len(x) - k)
    if not np.isclose(omega_squared(d, "v", "g"),
                      (ss_b - (k - 1) * ms_w) / (ss_t + ms_w), atol=1e-12):
        print("   FALHA ω²"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("2. peso inteiro equivale a repetir a linha (η², ω², BC)")
    xs = rng.integers(0, 40, 120).astype(float)
    gs = rng.integers(0, 4, 120)
    ws = rng.integers(1, 12, 120).astype(float)
    dp = pd.DataFrame({"v": xs, "g": gs, "peso": ws})
    de = pd.DataFrame({"v": np.repeat(xs, ws.astype(int)),
                       "g": np.repeat(gs, ws.astype(int)), "peso": 1.0})
    for nome, fn in [("η²", eta_squared), ("ω²", omega_squared)]:
        a, b = fn(dp, "v", "g"), fn(de, "v", "g")
        if not np.isclose(a, b, atol=1e-9):
            print(f"   FALHA {nome} ponderado: {a} vs {b}"); ok = False
    a, b = bimodality_coef(xs, ws), bimodality_coef(de["v"].to_numpy())
    if not np.isclose(a, b, atol=1e-9):
        print(f"   FALHA BC ponderado: {a} vs {b}"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("3. BC de Sarle com peso=1 vs scipy (a implementação que substituí)")
    for tam in (10, 50, 500):
        z = rng.normal(0, 1, tam)
        n = len(z)
        gg = skew(z, bias=False)
        kk = kurtosis(z, fisher=True, bias=False)
        ref = (gg ** 2 + 1.0) / (kk + 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
        if not np.isclose(bimodality_coef(z), ref, atol=1e-9):
            print(f"   FALHA BC n={tam}: {bimodality_coef(z)} vs {ref}"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("4. permutação: sob H0 o η² médio bate com o analítico (k−1)/(W−1)")
    xr = rng.integers(0, 40, 300).astype(float)
    wr = rng.integers(1, 30, 300).astype(float)
    gr = rng.integers(0, 4, 300)                      # rótulo independente do valor
    dr = pd.DataFrame({"v": xr, "g": gr, "peso": wr})
    pm = perm_eta(dr, "v", "g", B=300, w_col="peso")
    razao = pm["eta2_acaso_medio"] / pm["eta2_acaso_analitico"]
    print(f"   acaso empírico={pm['eta2_acaso_medio']:.3e} | "
          f"analítico={pm['eta2_acaso_analitico']:.3e} | razão={razao:.2f}")
    if not (0.7 < razao < 1.4):
        print("   FALHA: permutação não reproduz o piso analítico"); ok = False
    print("   ok" if ok else "   FALHOU")

    print("\nTODOS OS TESTES PASSARAM" if ok else "\n*** HÁ FALHAS ***")
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #28C — within/between da bimodalidade")
    ap.add_argument("--malha", choices=["meso", "amc"], default="meso",
                    help="recorte espacial: mesorregião (5) ou AMC (~150)")
    ap.add_argument("--n-gmm-min", type=int, default=100,
                    help="n mínimo de PIXELS (eventos, não linhas) p/ ajustar GMM por unidade")
    ap.add_argument("--fonte", choices=["censo", "amostra"], default="censo",
                    help="censo de pixels (padrão) ou amostra do #28A (reproduz jun/2026)")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--testar", action="store_true",
                    help="roda só o contrato D24 das estatísticas ponderadas e sai")
    args = ap.parse_args()

    if args.testar:
        sys.exit(0 if _testa_contrato_peso() else 1)

    # A amostra escreve em arquivos próprios: rodar `--fonte amostra` para
    # conferência não pode sobrescrever o resultado censitário.
    suf = ("" if args.malha == "meso" else "_amc") + \
          ("" if args.fonte == "censo" else "_amostra")
    col_esp = "mesorregiao" if args.malha == "meso" else "code_amc"
    lab_esp = "mesorregião" if args.malha == "meso" else "AMC"
    lab_fn  = (lambda v: str(v)) if args.malha == "meso" else (lambda v: f"AMC {int(v)}")

    print("=" * 76)
    print(f"Pipeline #28C — A bimodalidade é regionalmente causada? (malha = {args.malha.upper()})")
    print("=" * 76)

    df = carregar(args.fonte)
    df_nc = df[~df["censurado"]].copy()
    df_nc = df_nc[df_nc["mesorregiao"].notna() & (df_nc["mesorregiao"] != "")]
    df_nc = df_nc[df_nc["ato"].notna()]

    if args.malha == "amc":
        cw = pd.read_csv(ROOT / "data" / "processed" / "amc_crosswalk_goias.csv",
                         dtype={"cd_mun": "int64", "code_amc": "int64"})
        df_nc = df_nc.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
        df_nc = df_nc[df_nc["code_amc"].notna()]
        df_nc["code_amc"] = df_nc["code_amc"].astype(int)

    # Linhas e eventos SEMPRE lado a lado: foi confundir os dois que quebrou
    # este pipeline quando `carregar()` passou a defaultar para o censo.
    n_ev = float(df_nc["peso"].sum())
    print(f"[dados] fonte={args.fonte} | {n_ev:,.0f} pixels não-censurados "
          f"em {len(df_nc):,} células | "
          f"{df_nc[col_esp].nunique()} {lab_esp}(s) com conversão | "
          f"{df_nc['ano_conversao'].nunique()} anos")
    if args.fonte == "censo" and n_ev == len(df_nc):
        sys.exit("[erro] censo com peso≡1 — a coluna `peso` não sobreviveu à carga")

    # Unidades ordenadas pela mediana PONDERADA (jovem → velho).
    med_esp = {u: mediana_p(g["idade_pastagem_anos"].to_numpy(float),
                            g["peso"].to_numpy(float))
               for u, g in df_nc.groupby(col_esp, observed=True)}
    ord_esp = sorted(med_esp, key=lambda u: med_esp[u])

    # ---- Teste 1: decomposição de variância da IDADE (η², ω², acaso) -------
    eta_esp     = eta_squared(df_nc, "idade_pastagem_anos", col_esp)
    om_esp      = omega_squared(df_nc, "idade_pastagem_anos", col_esp)
    eta_ato     = eta_squared(df_nc, "idade_pastagem_anos", "ato")
    eta_esp_ato = eta_squared(df_nc, "idade_pastagem_anos", [col_esp, "ato"])
    om_esp_ato  = omega_squared(df_nc, "idade_pastagem_anos", [col_esp, "ato"])
    print("\n[1] Decomposição de variância da IDADE:")
    print(f"    {lab_esp:<12} η²={eta_esp:6.1%}  ω²={om_esp:6.1%}  (ω² corrige nº de grupos)")
    print(f"    ato (tempo)  η²={eta_ato:6.1%}")
    print(f"    {lab_esp}×ato η²={eta_esp_ato:6.1%}  ω²={om_esp_ato:6.1%}")
    print(f"    within-célula (1−ω²): {1 - om_esp_ato:6.1%}")

    # ---- Teste 5: separação jovem/velho (posterior do GMM global) ----------
    z = posterior_modo_velho(df_nc["idade_pastagem_anos"].to_numpy(float),
                             df_nc["peso"].to_numpy(float))
    df_nc["p_velho"] = z
    etaz_esp     = eta_squared(df_nc, "p_velho", col_esp)
    omz_esp      = omega_squared(df_nc, "p_velho", col_esp)
    etaz_ato     = eta_squared(df_nc, "p_velho", "ato")
    etaz_esp_ato = eta_squared(df_nc, "p_velho", [col_esp, "ato"])
    omz_esp_ato  = omega_squared(df_nc, "p_velho", [col_esp, "ato"])
    print("\n[5] Decomposição da SEPARAÇÃO jovem/velho (pertinência ao modo velho):")
    print(f"    {lab_esp:<12} η²={etaz_esp:6.1%}  ω²={omz_esp:6.1%}")
    print(f"    ato (tempo)  η²={etaz_ato:6.1%}")
    print(f"    {lab_esp}×ato η²={etaz_esp_ato:6.1%}  ω²={omz_esp_ato:6.1%}")
    print(f"    DENTRO das células (1−ω²): {1 - omz_esp_ato:6.1%}")

    # ---- Linha-base de permutação (piso do acaso p/ esse nº de grupos) -----
    print(f"\n[perm] η² esperado sob ACASO ({df_nc[col_esp].nunique()} grupos, "
          f"EVENTOS permutados com tamanhos de grupo fixos, B=200):")
    pm_idade = perm_eta(df_nc, "idade_pastagem_anos", col_esp, B=200)
    pm_velho = perm_eta(df_nc, "p_velho", col_esp, B=200)
    for nome, pm in [("idade", pm_idade), ("p_velho", pm_velho)]:
        print(f"    {nome:<8} obs={pm['eta2_obs']:.1%}  acaso≈{pm['eta2_acaso_medio']:.2e} "
              f"(p95={pm['eta2_acaso_p95']:.2e}; analítico (k−1)/(W−1)="
              f"{pm['eta2_acaso_analitico']:.2e})  líquido={pm['eta2_liquido']:.1%}  "
              f"p={pm['p_perm']:.3f}")
    if pm_velho["eta2_acaso_analitico"] < 1e-4:
        print("    [D23] o piso do acaso colapsou (W enorme): 'líquido' ≈ 'observado' e o")
        print("          p-valor é mecânico. Ler o η² pelo TAMANHO, não pela significância.")

    # ---- Testes 2-4: GMM + BC por unidade e por célula unidade×ato ---------
    def _vp(d: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        return (d["idade_pastagem_anos"].to_numpy(float), d["peso"].to_numpy(float))

    linhas = [avaliar_grupo("GLOBAL", "nao_censurado", *_vp(df_nc))]
    # Por unidade espacial (só as com n suficiente p/ GMM confiável). O filtro
    # conta EVENTOS (Σpeso), não linhas: sob o censo uma unidade pode ter poucas
    # células e milhões de pixels.
    peso_por_unidade = df_nc.groupby(col_esp, observed=True)["peso"].sum()
    unidades_gmm = [u for u in ord_esp if peso_por_unidade.get(u, 0) >= args.n_gmm_min]
    for u in unidades_gmm:
        linhas.append(avaliar_grupo("UNIDADE", lab_fn(u), *_vp(df_nc[df_nc[col_esp] == u])))
    # Por célula unidade×ato (Ato II e III), idem.
    for u in unidades_gmm:
        for ato in ("II", "III"):
            sub = df_nc[(df_nc[col_esp] == u) & (df_nc["ato"] == ato)]
            if sub["peso"].sum() >= args.n_gmm_min:
                linhas.append(avaliar_grupo("UNIDADE_ATO", f"{lab_fn(u)} · Ato {ato}", *_vp(sub)))
    res = pd.DataFrame(linhas)

    n_unid = (res.escopo == "UNIDADE").sum()
    n_unid_bim = int(res[res.escopo == "UNIDADE"]["bimodal"].sum())
    n_cell = (res.escopo == "UNIDADE_ATO").sum()
    n_cell_bim = int(res[res.escopo == "UNIDADE_ATO"]["bimodal"].sum())

    print(f"\n[2-4] GMM por unidade (n≥{args.n_gmm_min}): "
          f"{n_unid_bim}/{n_unid} {lab_esp}(s) bimodais | "
          f"células {lab_esp}×ato bimodais: {n_cell_bim}/{n_cell}")
    # Mostra as 12 maiores unidades.
    head = res[res.escopo == "UNIDADE"].nlargest(12, "n")
    print("      unidade           n     mediana  jovem  velho   ΔBIC    BC    bimodal?")
    for _, r in head.iterrows():
        print(f"      {r['chave']:<16} {r['n']:>6}   {r['mediana']:>4.0f}a   "
              f"{r['mu_jovem']:>4.1f}  {r['mu_velho']:>5.1f}  {r['delta_bic']:>6.0f}  "
              f"{r['bc_sarle']:.2f}   {'SIM' if r['bimodal'] else 'não'}")

    # ---- Salvar -----------------------------------------------------------
    arq_grupo  = DIR_PROC / f"idade_bimodalidade_por_grupo{suf}.csv"
    arq_decomp = DIR_PROC / f"idade_bimodalidade_decomposicao{suf}.csv"
    res.to_csv(arq_grupo, index=False, encoding="utf-8")
    decomp = pd.DataFrame([
        {"malha": args.malha, "alvo": "idade",   "eixo": "espacial",     "eta2": eta_esp,     "omega2": om_esp},
        {"malha": args.malha, "alvo": "idade",   "eixo": "ato",          "eta2": eta_ato,     "omega2": None},
        {"malha": args.malha, "alvo": "idade",   "eixo": "espacial_ato", "eta2": eta_esp_ato, "omega2": om_esp_ato},
        {"malha": args.malha, "alvo": "idade",   "eixo": "within_cell",  "eta2": 1 - eta_esp_ato, "omega2": 1 - om_esp_ato},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "espacial",     "eta2": etaz_esp,     "omega2": omz_esp},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "ato",          "eta2": etaz_ato,     "omega2": None},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "espacial_ato", "eta2": etaz_esp_ato, "omega2": omz_esp_ato},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "within_cell",  "eta2": 1 - etaz_esp_ato, "omega2": 1 - omz_esp_ato},
        {"malha": args.malha, "alvo": "idade",   "eixo": "perm_obs",     "eta2": pm_idade["eta2_obs"],    "omega2": pm_idade["eta2_liquido"]},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "perm_obs",     "eta2": pm_velho["eta2_obs"],    "omega2": pm_velho["eta2_liquido"]},
        {"malha": args.malha, "alvo": "idade",   "eixo": "perm_acaso",   "eta2": pm_idade["eta2_acaso_medio"], "omega2": pm_idade["eta2_acaso_analitico"]},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "perm_acaso",   "eta2": pm_velho["eta2_acaso_medio"], "omega2": pm_velho["eta2_acaso_analitico"]},
    ])
    # Proveniência no próprio arquivo: sem isto, um CSV do censo e um da amostra
    # são indistinguíveis depois de salvos — foi assim que os CSVs de jun/2026
    # sobreviveram à migração parecendo atuais.
    decomp.insert(0, "fonte", args.fonte)
    decomp.insert(1, "n_eventos", int(round(n_ev)))
    decomp.insert(2, "n_celulas", len(df_nc))
    res.insert(0, "fonte", args.fonte)
    decomp.to_csv(arq_decomp, index=False, encoding="utf-8")
    print(f"\n[OK] {arq_grupo.relative_to(ROOT)}  ({len(res)} linhas)")
    print(f"[OK] {arq_decomp.relative_to(ROOT)}  ({len(decomp)} linhas)")

    if not args.sem_figuras:
        # Para AMC, ilustra com as maiores unidades (grid de 150 seria ilegível).
        unidades_fig = (ord_esp if args.malha == "meso"
                        else res[res.escopo == "UNIDADE"].nlargest(6, "n")
                              ["chave"].str.replace("AMC ", "").astype(int).tolist())
        fig_grid(df_nc, unidades_fig, col_esp=col_esp, lab_fn=lab_fn,
                 outname=f"bimodalidade_unidade_ato{suf}.png")

    # ---- Veredito ---------------------------------------------------------
    within_velho_omega = 1 - omz_esp_ato
    liq_velho = pm_velho["eta2_liquido"]
    print("\n" + "=" * 76)
    print(f"VEREDITO (malha = {args.malha.upper()})")
    print("=" * 76)
    print(f"  η²({lab_esp}) da separação jovem/velho: {etaz_esp:.1%} bruto | "
          f"ω²={omz_esp:.1%} | líquido de acaso={liq_velho:.1%}")
    print(f"  {lab_esp}(s) internamente bimodais (n≥{args.n_gmm_min}): {n_unid_bim}/{n_unid}")
    print(f"  Coexistência DENTRO das células {lab_esp}×ato (1−ω²): {within_velho_omega:.0%}")
    if within_velho_omega >= 0.5 and liq_velho < 0.25:
        print(f"  → Mesmo na malha {args.malha.upper()}, a geografia NÃO causa a bimodalidade:")
        print("    captura pouco da separação além do acaso; cada unidade é bimodal por dentro.")
        print("    Confirma: gradiente no PESO da mistura, não causação regional (D14).")
    else:
        print(f"  → Na malha {args.malha.upper()} o recorte espacial captura parcela relevante —")
        print("    a mesorregião era grossa demais. Reportar a parcela between/within.")


if __name__ == "__main__":
    main()
