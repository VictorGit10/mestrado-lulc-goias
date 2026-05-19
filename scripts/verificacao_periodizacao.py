"""verificacao_periodizacao.py — Verificação de sanidade dos scripts de periodização
===============================================================================

Testes:
1. Sanidade: gerar séries aleatórias (ruído branco) e verificar se os métodos
   detectam quebras onde não deveria haver (taxa de falso positivo).
2. Sensibilidade de parâmetros: variar min_size (3, 5, 7) e F_threshold (3, 5, 7)
   no sup-F multivariado e verificar se as quebras detectadas mudam.
3. Consistência: comparar resultados do sup-F univariado (Pipeline #26)
   com o sup-F multivariado para ver se são coerentes.

Pré-requisitos:
    data/processed/taxas_lulc_goias.csv (Pipeline #17)
    outputs/correlacoes/quebras_resultados.csv (Pipeline #26)
    outputs/correlacoes/quebras_multivariadas_go.csv (Pipeline #29a)
    outputs/correlacoes/stars_go.csv (Pipeline #29b)
    outputs/correlacoes/transicoes_kl_go.csv (Pipeline #29c)
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"

# ─────────────────────────── 1. Sanidade: ruído branco ───────────────────────────

def teste_falso_positivo(n_sim=1000, n=39, p=3, min_size=5, f_threshold=5.0):
    """Gera n_sim series de ruído branco (p variáveis, n observações cada)
    e conta quantas vezes o sup-F multivariado detecta quebras espúrias."""
    from periodizacao_multivariada import sup_f_multivariado, binary_segmentation_mv

    anos = np.arange(1986, 1986 + n)

    n_sim_with_breaks = 0
    n_breaks_total = 0
    for i in range(n_sim):
        Y = np.random.randn(n, p)  # ruído branco
        breaks = binary_segmentation_mv(Y, anos, max_breaks=3, f_threshold=f_threshold, min_size=min_size)
        if len(breaks) > 0:
            n_sim_with_breaks += 1
            n_breaks_total += len(breaks)

    fpr = n_sim_with_breaks / n_sim
    avg_breaks = n_breaks_total / n_sim
    return {
        "n_sim": n_sim,
        "n_with_breaks": n_sim_with_breaks,
        "false_positive_rate": round(fpr, 4),
        "avg_breaks_per_sim": round(avg_breaks, 4),
        "f_threshold": f_threshold,
        "min_size": min_size,
    }


# ─────────────────────────── 2. Sensibilidade de parâmetros ───────────────────────────

def teste_sensibilidade(y_real, anos_real, param_grid=None):
    """Varia min_size e f_threshold e compara quebras detectadas."""
    from periodizacao_multivariada import binary_segmentation_mv

    if param_grid is None:
        param_grid = [
            (3, 3.0), (3, 5.0), (3, 7.0),
            (5, 3.0), (5, 5.0), (5, 7.0),
            (7, 3.0), (7, 5.0), (7, 7.0),
        ]

    resultados = []
    for min_size, f_thresh in param_grid:
        breaks = binary_segmentation_mv(y_real, anos_real, max_breaks=3,
                                        f_threshold=f_thresh, min_size=min_size)
        anos_breaks = [b["ano_quebra"] for b in breaks]
        f_stats = [round(b["f_stat"], 1) for b in breaks]
        resultados.append({
            "min_size": min_size,
            "f_threshold": f_thresh,
            "n_breaks": len(breaks),
            "anos": anos_breaks,
            "f_stats": f_stats,
        })
    return resultados


# ─────────────────────────── 3. Consistência univariado vs multivariado ───────────────────────────

def teste_consistencia():
    """Compara quebras univariadas (Pipeline #26) com multivariadas (Pipeline #29a)."""
    # Quebras univariadas
    univ_path = DIR_OUT / "quebras_resultados.csv"
    multi_path = DIR_OUT / "quebras_multivariadas_go.csv"

    if not univ_path.exists() or not multi_path.exists():
        print("Arquivos não encontrados. Execute Pipeline #26 e #29a primeiro.")
        return None

    df_univ = pd.read_csv(univ_path)
    df_multi = pd.read_csv(multi_path)

    # Filtrar GO univariado
    go_breaks = df_univ[df_univ["uf"] == "Goiás"]["ano_quebra"].unique()
    multi_breaks = df_multi["ano_quebra"].unique()

    return {
        "univariado_GO": sorted([int(a) for a in go_breaks]),
        "multivariado_GO": sorted([int(a) for a in multi_breaks]),
        "convergentes": sorted(set(int(a) for a in go_breaks) & set(int(a) for a in multi_breaks)),
        "so_univariado": sorted(set(int(a) for a in go_breaks) - set(int(a) for a in multi_breaks)),
        "so_multivariado": sorted(set(int(a) for a in multi_breaks) - set(int(a) for a in go_breaks)),
    }


# ─────────────────────────── 4. Robustez STARS (variação de l e alpha) ───────────────────────────

def teste_sensibilidade_stars(y_real, anos_real):
    """Varia l (regime length) e alpha e compara shifts detectados."""
    from periodizacao_stars import rodionov_stars, CLASSES

    param_grid = [
        (3, 0.05), (3, 0.10), (5, 0.01),
        (5, 0.05), (5, 0.10), (7, 0.05),
    ]
    resultados = []
    for l, alpha in param_grid:
        shifts = []
        for i, classe in enumerate(CLASSES):
            s = rodionov_stars(y_real[:, i], l=l, alpha=alpha)
            for sh in s:
                sh["ano"] = int(anos_real[sh["shift_idx"]])
                sh["classe"] = classe
                sh["l"] = l
                sh["alpha"] = alpha
            shifts.extend(s)
        anos_shifts = sorted(set(s["ano"] for s in shifts))
        resultados.append({
            "l": l, "alpha": alpha,
            "n_shifts": len(shifts),
            "anos": anos_shifts,
        })
    return resultados


# ─────────────────────────── Main ───────────────────────────

def main():
    np.random.seed(42)

    # Carregar dados reais
    from periodizacao_multivariada import carregar_series
    Y, anos = carregar_series()

    print("=" * 70)
    print("VERIFICAÇÃO DE SANIDADE — PERIODIZAÇÃO")
    print("=" * 70)

    # 1. Falso positivo (ruído branco)
    print("\n1. TESTE DE FALSO POSITIVO (ruído branco)")
    print("-" * 50)
    for f_thresh in [3.0, 4.0, 5.0]:
        result = teste_falso_positivo(n_sim=500, n=39, p=3, min_size=5, f_threshold=f_thresh)
        print(f"  F_threshold={f_thresh}: FPR={result['false_positive_rate']:.3f}, "
              f"avg_breaks={result['avg_breaks_per_sim']:.2f}, "
              f"sim_with_breaks={result['n_with_breaks']}/{result['n_sim']}")

    # 2. Sensibilidade de parâmetros (dados reais)
    print("\n2. SENSIBILIDADE DE PARÂMETROS (sup-F multivariado)")
    print("-" * 50)
    resultados_sens = teste_sensibilidade(Y, anos)
    for r in resultados_sens:
        print(f"  min_size={r['min_size']}, F_thresh={r['f_threshold']}: "
              f"{r['n_breaks']} breaks em {r['anos']} (F={r['f_stats']})")

    # 3. Consistência univariado vs multivariado
    print("\n3. CONSISTÊNCIA UNIVARIADO vs MULTIVARIADO")
    print("-" * 50)
    consistencia = teste_consistencia()
    if consistencia:
        print(f"  Univariado (GO): {consistencia['univariado_GO']}")
        print(f"  Multivariado: {consistencia['multivariado_GO']}")
        print(f"  Convergentes: {consistencia['convergentes']}")
        print(f"  Só univariado: {consistencia['so_univariado']}")
        print(f"  Só multivariado: {consistencia['so_multivariado']}")

    # 4. Sensibilidade STARS
    print("\n4. SENSIBILIDADE STARS (variação de l e alpha)")
    print("-" * 50)
    resultados_stars = teste_sensibilidade_stars(Y, anos)
    for r in resultados_stars:
        print(f"  l={r['l']}, alpha={r['alpha']}: {r['n_shifts']} shifts em {r['anos']}")

    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    print("Se FPR < 0.10 para F_threshold=4.0: sup-F multivariado é aceitável.")
    print("Se as quebras são estáveis entre (min_size=3,5,7) e (F_thresh=3,5,7):")
    print("  → as fronteiras são robustas à escolha de parâmetros.")
    print("Se univariado e multivariado convergem nas mesmas fronteiras principais:")
    print("  → os resultados são coerentes entre métodos.")


if __name__ == "__main__":
    main()