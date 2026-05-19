"""periodizacao_transicoes.py — Pipeline #29c: Transições via KL divergence + autovalores
==========================================================================================

Compara matrizes de transição LULC antes/depois de cada ano-candidato para
identificar fronteira de atos. Usa divergência KL ponderada pela distribuição
estacionária, comparação de autovalores (λ₁ e |λ₂|) e bootstrap de permutação.

Especificação:
    Para cada ano-candidato τ ∈ [1988, 2022]:
      1. Construir P_before (média das matrizes de transição dos pares
         com ano_origem < τ) e P_after (ano_origem ≥ τ).
      2. KL(P_before || P_after) = Σ_i γ_i Σ_j P_before_ij log(P_before_ij / P_after_ij)
         onde γ é a distribuição estacionária de P_before.
      3. Autovalores: λ₁ (1.0 para matriz estocástica), |λ₂| (taxa de convergência).
      4. Significância bootstrap: permutar rótulos de ano 1000 vezes e recalcular KL.

Pré-requisitos:
    data/processed/conversao_bruta_goias.csv  (Pipeline #19 / agregar_conversoes.py)

Saídas:
    outputs/correlacoes/transicoes_kl_go.csv
    outputs/correlacoes/transicoes_kl_go.png
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import eig

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

from config_periodos import MARCOS, ATOS, CORES_ATO

# ─────────────────────────── Config ───────────────────────────

GRUPOS = ["vegetacao_natural", "pastagem", "agricultura", "agua", "area_urbana", "outros"]
N = len(GRUPOS)
EPSILON = 0.001          # pseudocount para evitar log(0)
N_BOOT = 1000            # número de permutações bootstrap
ANO_MIN = 1985
ANO_MAX = 2024
TAU_LO = 1988            # primeiro ano-candidato
TAU_HI = 2022            # último ano-candidato
MIN_PARES = 2            # mínimo de pares de transição por segmento


# ─────────────────────────── Funções ───────────────────────────

def carregar_transicoes() -> dict[tuple[int, int], pd.DataFrame]:
    """Carrega conversao_bruta_goias.csv e retorna dict (ano_orig, ano_dest) -> DataFrame."""
    df = pd.read_csv(DIR_DATA / "conversao_bruta_goias.csv")
    transicoes: dict[tuple[int, int], pd.DataFrame] = {}
    for (a1, a2), grp in df.groupby(["ano_origem", "ano_destino"]):
        transicoes[(int(a1), int(a2))] = grp.reset_index(drop=True)
    return transicoes


def construir_matriz(df: pd.DataFrame) -> np.ndarray:
    """Constrói matriz 6x6 de áreas de transição a partir de um DataFrame agrupado."""
    P = np.zeros((N, N))
    for _, row in df.iterrows():
        i = GRUPOS.index(row["grupo_orig"])
        j = GRUPOS.index(row["grupo_dest"])
        P[i, j] = row["area_mha"]
    return P


def normalizar_linhas(P: np.ndarray, eps: float = EPSILON) -> np.ndarray:
    """Adiciona pseudocounts ε e normaliza linhas para soma 1 (row-stochastic)."""
    P_eps = P + eps
    row_sums = P_eps.sum(axis=1, keepdims=True)
    return P_eps / row_sums


def distribuicao_estacionaria(P: np.ndarray) -> np.ndarray:
    """Calcula distribuição estacionária π tal que π = πP (autovetor esquerdo de λ=1).

    Para matriz estocástica, λ₁=1 sempre. Retornamos autovetor normalizado.
    """
    vals, vecs = eig(P.T)  # autovetores direitos de P^T = autovetores esquerdos de P
    # Encontrar índice do autovalor mais próximo de 1
    idx = np.argmin(np.abs(vals - 1.0))
    pi = np.real(vecs[:, idx])
    # Normalizar para soma 1 (lidar com sinal)
    if pi.sum() < 0:
        pi = -pi
    pi = pi / pi.sum()
    # Garantir não-negatividade
    pi = np.maximum(pi, 1e-15)
    pi = pi / pi.sum()
    return pi


def segundo_autovalor(P: np.ndarray) -> float:
    """Retorna |λ₂|, o segundo maior autovalor em módulo (taxa de convergência)."""
    vals = np.linalg.eigvals(P)
    vals_mod = np.sort(np.abs(vals))[::-1]  # ordenar decrescente
    # vals_mod[0] ≈ 1 (autovalor dominante)
    if len(vals_mod) > 1:
        return float(vals_mod[1])
    return 0.0


def kl_divergence(P: np.ndarray, Q: np.ndarray, gamma: np.ndarray | None = None) -> float:
    """KL(P||Q) ponderada pela distribuição estacionária γ de P.

    KL(P||Q) = Σ_i γ_i Σ_j P_ij log(P_ij / Q_ij)
    """
    if gamma is None:
        gamma = distribuicao_estacionaria(P)
    # Evitar log(0): pseudocounts já foram adicionados
    kl = 0.0
    for i in range(N):
        row_kl = 0.0
        for j in range(N):
            if P[i, j] > 0 and Q[i, j] > 0:
                row_kl += P[i, j] * np.log(P[i, j] / Q[i, j])
        kl += gamma[i] * row_kl
    return float(kl)


def computar_matriz_media(
    pares: list[tuple[int, int]],
    transicoes: dict[tuple[int, int], pd.DataFrame],
) -> np.ndarray | None:
    """Calcula a matriz de transição média para um conjunto de pares de anos.

    Média aritmética das matrizes de transição normalizadas (row-stochastic).
    Retorna None se não houver pares suficientes.
    """
    if len(pares) < MIN_PARES:
        return None
    matrizes = []
    for par in pares:
        if par not in transicoes:
            continue
        M = construir_matriz(transicoes[par])
        M = normalizar_linhas(M)
        matrizes.append(M)
    if len(matrizes) < MIN_PARES:
        return None
    return np.mean(matrizes, axis=0)


# ─────────────────────────── Pipeline principal ───────────────────────────

def main() -> None:
    print("=" * 70)
    print("Pipeline #29c: Transições via KL divergence + autovalores")
    print("=" * 70)

    # ── 1. Carregar dados ──
    transicoes = carregar_transicoes()
    pares_disponiveis = sorted(transicoes.keys())
    print(f"\nCarregados {len(pares_disponiveis)} pares de transição "
          f"({pares_disponiveis[0][0]}-{pares_disponiveis[-1][1]})")

    # ── 2. Classificar pares por ano de origem ──
    anos_origem = sorted(set(a1 for a1, _ in pares_disponiveis))
    print(f"Anos de origem disponíveis: {anos_origem[0]}-{anos_origem[-1]} "
          f"({len(anos_origem)} anos)")

    # ── 3. Calcular KL, autovalores e bootstrap para cada ano-candidato ──
    resultados: list[dict] = []
    anos_candidatos = list(range(TAU_LO, TAU_HI + 1))

    print(f"\nCalculando KL divergence para {len(anos_candidatos)} anos-candidato...")
    for tau in anos_candidatos:
        pares_before = [(a1, a2) for a1, a2 in pares_disponiveis if a1 < tau]
        pares_after = [(a1, a2) for a1, a2 in pares_disponiveis if a1 >= tau]

        P_before = computar_matriz_media(pares_before, transicoes)
        P_after = computar_matriz_media(pares_after, transicoes)

        if P_before is None or P_after is None:
            print(f"  τ={tau}: insuficiente (before={len(pares_before)}, "
                  f"after={len(pares_after)}) — ignorado")
            continue

        # Distribuição estacionária e autovalores de P_before
        gamma_before = distribuicao_estacionaria(P_before)
        lambda2_before = segundo_autovalor(P_before)

        # Distribuição estacionária e autovalores de P_after
        gamma_after = distribuicao_estacionaria(P_after)
        lambda2_after = segundo_autovalor(P_after)

        # KL divergence (before || after), ponderado por γ_before
        kl_ba = kl_divergence(P_before, P_after, gamma_before)
        # KL divergence (after || before), ponderado por γ_after
        kl_ab = kl_divergence(P_after, P_before, gamma_after)
        # Simétrico: média geométrica
        kl_sym = np.sqrt(kl_ba * kl_ab) if kl_ba > 0 and kl_ab > 0 else 0.0

        # Variação no |λ₂|
        delta_lambda2 = abs(lambda2_after - lambda2_before)

        # Variação na distribuição estacionária (distância TV)
        tv_pi = 0.5 * np.sum(np.abs(gamma_after - gamma_before))

        resultados.append({
            "tau": tau,
            "n_before": len(pares_before),
            "n_after": len(pares_after),
            "kl_before_after": kl_ba,
            "kl_after_before": kl_ab,
            "kl_simetrico": kl_sym,
            "lambda2_before": lambda2_before,
            "lambda2_after": lambda2_after,
            "delta_lambda2": delta_lambda2,
            "tv_pi": tv_pi,
            "pi_before_veg": gamma_before[0],
            "pi_before_past": gamma_before[1],
            "pi_before_agri": gamma_before[2],
            "pi_after_veg": gamma_after[0],
            "pi_after_past": gamma_after[1],
            "pi_after_agri": gamma_after[2],
        })

    if not resultados:
        print("ERRO: Nenhum resultado calculado. Verifique os dados.")
        return

    df_result = pd.DataFrame(resultados)
    print(f"\nCalculados {len(df_result)} anos-candidato")

    # ── 4. Bootstrap de significância ──
    print(f"\nBootstrap de permutação ({N_BOOT} réplicas)...")

    # Preparar todas as matrizes de transição normalizadas
    todas_matrizes: list[np.ndarray] = []
    todos_anos: list[int] = []
    for a1 in anos_origem:
        par = (a1, a1 + 1)
        if par in transicoes:
            M = construir_matriz(transicoes[par])
            M = normalizar_linhas(M)
            todas_matrizes.append(M)
            todos_anos.append(a1)

    n_matrizes = len(todas_matrizes)
    todas_matrizes_arr = np.array(todas_matrizes)  # shape (n_matrizes, N, N)

    rng = np.random.default_rng(42)

    # Para cada τ, calcular KL sob permutação dos rótulos de ano
    bootstrap_kl: dict[int, list[float]] = {tau: [] for tau in df_result["tau"]}

    for b in range(N_BOOT):
        # Permutar rótulos de ano, mantendo matrizes intactas
        idx_perm = rng.permutation(n_matrizes)

        for _, row in df_result.iterrows():
            tau = int(row["tau"])
            n_before = int(row["n_before"])

            # Matrizes before e after sob permutação
            perm_before = todas_matrizes_arr[idx_perm[:n_before]]
            perm_after = todas_matrizes_arr[idx_perm[n_before:n_before + int(row["n_after"])]]

            if len(perm_before) < MIN_PARES or len(perm_after) < MIN_PARES:
                continue

            P_b = np.mean(perm_before, axis=0)
            P_a = np.mean(perm_after, axis=0)

            # KL simétrico sob permutação
            gamma_b = distribuicao_estacionaria(P_b)
            gamma_a = distribuicao_estacionaria(P_a)

            kl_ba_perm = kl_divergence(P_b, P_a, gamma_b)
            kl_ab_perm = kl_divergence(P_a, P_b, gamma_a)
            kl_sym_perm = np.sqrt(kl_ba_perm * kl_ab_perm) if kl_ba_perm > 0 and kl_ab_perm > 0 else 0.0

            bootstrap_kl[tau].append(kl_sym_perm)

    # Calcular p-valores
    pvalues = []
    for _, row in df_result.iterrows():
        tau = int(row["tau"])
        kl_obs = row["kl_simetrico"]
        null_dist = np.array(bootstrap_kl[tau])
        if len(null_dist) > 0:
            p_val = float(np.mean(null_dist >= kl_obs))
        else:
            p_val = 1.0
        pvalues.append(p_val)

    df_result["p_valor"] = pvalues
    df_result["significativo_05"] = df_result["p_valor"] < 0.05
    df_result["significativo_01"] = df_result["p_valor"] < 0.01

    # ── 5. Referência cruzada com MARCOS ──
    df_result["marco"] = df_result["tau"].apply(
        lambda t: MARCOS.get(t, {}).get("titulo", "")
    )
    df_result["evidencia"] = df_result["tau"].apply(
        lambda t: MARCOS.get(t, {}).get("evidencia", "")
    )

    # ── 6. Salvar CSV ──
    out_csv = DIR_OUT / "transicoes_kl_go.csv"
    df_result.to_csv(out_csv, index=False, float_format="%.6f")
    print(f"\nCSV salvo: {out_csv}")

    # ── 7. Resumo ──
    print("\n" + "=" * 70)
    print("RESULTADOS — Anos com maior divergência estrutural")
    print("=" * 70)

    # Top 5 por KL simétrico
    top5 = df_result.nlargest(5, "kl_simetrico")
    print("\nTop 5 anos por KL simétrico:")
    for _, row in top5.iterrows():
        marco = row["marco"] or "—"
        ev = row["evidencia"] or "—"
        print(f"  τ={int(row['tau'])}: KL={row['kl_simetrico']:.4f} "
              f"p={row['p_valor']:.3f} "
              f"|λ₂|: {row['lambda2_before']:.4f}→{row['lambda2_after']:.4f} "
              f"TV(π)={row['tv_pi']:.4f}  "
              f"[{ev}] {marco}")

    # Top 5 por variação de |λ₂|
    top5_lam = df_result.nlargest(5, "delta_lambda2")
    print("\nTop 5 anos por variação em |λ₂|:")
    for _, row in top5_lam.iterrows():
        marco = row["marco"] or "—"
        ev = row["evidencia"] or "—"
        print(f"  τ={int(row['tau'])}: Δ|λ₂|={row['delta_lambda2']:.4f} "
              f"|λ₂|={row['lambda2_before']:.4f}→{row['lambda2_after']:.4f} "
              f"[{ev}] {marco}")

    # Top 5 por variação na distribuição estacionária
    top5_tv = df_result.nlargest(5, "tv_pi")
    print("\nTop 5 anos por distância TV(π):")
    for _, row in top5_tv.iterrows():
        marco = row["marco"] or "—"
        ev = row["evidencia"] or "—"
        print(f"  τ={int(row['tau'])}: TV(π)={row['tv_pi']:.4f} "
              f"π_veg: {row['pi_before_veg']:.3f}→{row['pi_after_veg']:.3f} "
              f"π_past: {row['pi_before_past']:.3f}→{row['pi_after_past']:.3f} "
              f"[{ev}] {marco}")

    # ── 8. Plot ──
    plotar_resultados(df_result)

    print("\nConcluído.")


# ─────────────────────────── Visualização ───────────────────────────

def plotar_resultados(df: pd.DataFrame) -> None:
    """Gera painel com 4 métricas: KL, |λ₂|, TV(π) e p-valores."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    tau = df["tau"].values

    # Cores dos atos para fundo
    ato_ranges = []
    for nome, info in ATOS.items():
        ato_ranges.append((info["inicio"], info["fim"], nome))

    ato_colors_map = CORES_ATO

    def add_ato_bands(ax):
        for ini, fim, nome in ato_ranges:
            cor = ato_colors_map.get(nome, "#cccccc")
            ax.axvspan(ini, fim + 0.5, alpha=0.08, color=cor)

    def add_marcos(ax, y_max_frac=0.95):
        """Adiciona linhas verticais nos marcos institucionais."""
        for ano, info in MARCOS.items():
            ev = info["evidencia"]
            ls = "-" if ev == "A" else ("--" if ev == "B" else ":")
            lw = 1.5 if ev == "A" else (1.0 if ev == "B" else 0.7)
            ax.axvline(ano, color="#333333", linestyle=ls, linewidth=lw, alpha=0.6)
            # Label no topo
            titulo_curto = info["titulo"][:12]
            ax.text(ano, ax.get_ylim()[1] * y_max_frac, titulo_curto,
                    rotation=90, fontsize=6, va="top", ha="right",
                    color="#555555", alpha=0.8)

    # ── Painel A: KL simétrico ──
    ax = axes[0, 0]
    add_ato_bands(ax)
    ax.plot(tau, df["kl_simetrico"], "o-", color="#1f77b4", markersize=4, linewidth=1.2)
    # Destacar significativos
    sig = df[df["significativo_05"]]
    if len(sig) > 0:
        ax.scatter(sig["tau"], sig["kl_simetrico"], s=50, facecolors="none",
                   edgecolors="#d62728", linewidths=1.5, zorder=5, label="p < 0.05")
    add_marcos(ax)
    ax.set_ylabel("Divergência KL simétrico")
    ax.set_title("A) KL(P_before || P_after) — Mudança estrutural")
    ax.legend(fontsize=8)

    # ── Painel B: |λ₂| antes e depois ──
    ax = axes[0, 1]
    add_ato_bands(ax)
    ax.plot(tau, df["lambda2_before"], "s-", color="#2ca02c", markersize=4,
            linewidth=1.0, label="|λ₂| before")
    ax.plot(tau, df["lambda2_after"], "^-", color="#ff7f0e", markersize=4,
            linewidth=1.0, label="|λ₂| after")
    add_marcos(ax)
    ax.set_ylabel("|λ₂|")
    ax.set_title("B) Taxa de convergência |λ₂| — Before vs After")
    ax.legend(fontsize=8)

    # ── Painel C: Distância TV(π) ──
    ax = axes[1, 0]
    add_ato_bands(ax)
    ax.plot(tau, df["tv_pi"], "D-", color="#9467bd", markersize=4, linewidth=1.2)
    add_marcos(ax)
    ax.set_ylabel("TV(π_before, π_after)")
    ax.set_xlabel("Ano-candidato τ")
    ax.set_title("C) Distância total variation — Distribuição estacionária")

    # ── Painel D: P-valores (escala -log10) ──
    ax = axes[1, 1]
    add_ato_bands(ax)
    log_p = -np.log10(df["p_valor"].clip(lower=1e-10))
    ax.bar(tau, log_p, color="#8c564b", alpha=0.7, width=0.8)
    ax.axhline(-np.log10(0.05), color="#d62728", linestyle="--", linewidth=1, label="p = 0.05")
    ax.axhline(-np.log10(0.01), color="#d62728", linestyle=":", linewidth=1, label="p = 0.01")
    add_marcos(ax, y_max_frac=0.9)
    ax.set_ylabel("-log₁₀(p)")
    ax.set_xlabel("Ano-candidato τ")
    ax.set_title("D) Significância bootstrap (1000 permutações)")
    ax.legend(fontsize=8)

    # Ajustes finais
    fig.suptitle("Pipeline #29c — Transições LULC: KL divergence + autovalores + bootstrap\n"
                 "Goiás 1985-2024 | 6 classes | Pseudocounts ε=0.001",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])

    out_png = DIR_OUT / "transicoes_kl_go.png"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"PNG salvo: {out_png}")


if __name__ == "__main__":
    main()