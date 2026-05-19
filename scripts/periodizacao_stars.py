"""periodizacao_stars.py — Pipeline #29b: Rodionov STARS (Sequential T-test Analysis of Regime Shifts)
================================================================================================

Implementa o teste de Rodionov (2004) para deteccao de mudancas de regime
com janela deslizante. Complementa o Quandt-Andrews sup-F ao detectar
regimes curtos que o sup-F (que requer trimming) pode perder.

Especificacao:
    Para cada ponto t na serie, testa se a media do regime atual
    difere significativamente da media de referencia:
    - Regime length (l): 5 anos
    - Significancia (alpha): 0.05
    - Huber weight parameter: 1 (reduz impacto de outliers)

Metodo:
    1. Calcular media de referencia dos primeiros l pontos
    2. Para cada ponto seguinte:
       a. Se |x_t - media_ref| > t_crit * diff_std: regime shift detectado
       b. Recalcular media de referencia a partir do ponto de shift
       c. Caso contrario: atualizar media de referencia com x_t

Saidas:
    outputs/correlacoes/stars_go.csv
    outputs/correlacoes/stars_go.png

Prerequisitos:
    data/processed/taxas_lulc_goias.csv  (Pipeline #17)
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy.stats import t as t_dist

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

from config_periodos import MARCOS, ATOS, CORES_ATO

# ─────────────────────────── Config ───────────────────────────

CLASSES = ["vegetacao_natural", "pastagem", "agricultura"]
REGIME_LENGTH = 5    # comprimento minimo do regime (anos)
ALPHA = 0.05         # nivel de significancia
HUBER_W = 1.0        # parametro de peso de Huber
TOL_MARCO = 2        # tolerancia para coincidencia com marcos


# ─────────────────────────── Rodionov STARS ───────────────────────────

def rodionov_stars(y: np.ndarray, l: int = REGIME_LENGTH,
                   alpha: float = ALPHA,
                   huber_w: float = HUBER_W) -> list[dict]:
    """Aplica Rodionov STARS para detectar regime shifts.

    Retorna lista de dicts com ano do shift e media antes/depois.
    """
    n = len(y)
    t_crit = t_dist.ppf(1 - alpha / 2, df=l - 1)

    # Calcular desvio padrao robusto (MAD-based)
    mad = np.median(np.abs(y - np.median(y))) * 1.4826
    diff_std = mad * np.sqrt(2.0 / l)  # diff entre medias de l pontos

    if diff_std == 0:
        return []

    shifts = []
    regime_start = 0
    regime_mean = np.mean(y[:l])

    for t in range(l, n):
        # Teste de shift
        if abs(y[t] - regime_mean) > t_crit * diff_std:
            # Shift detectado
            shift_year = t  # indice
            mean_before = regime_mean
            # Nova media do regime: comecar a partir de t
            end = min(t + l, n)
            regime_mean = np.mean(y[t:end])
            regime_start = t
            shifts.append({
                "shift_idx": shift_year,
                "mean_before": round(float(mean_before), 4),
                "mean_after": round(float(regime_mean), 4),
                "delta": round(float(regime_mean - mean_before), 4),
            })
        else:
            # Atualizar media do regime (media movel)
            regime_mean = regime_mean + (y[t] - regime_mean) / (t - regime_start + 1)

    return shifts


def rodionov_stars_series(series: np.ndarray, anos: np.ndarray,
                            classe: str) -> list[dict]:
    """Aplica STARS a uma serie e enriquece com ano e nome da classe."""
    shifts = rodionov_stars(series)
    for s in shifts:
        s["ano"] = int(anos[s["shift_idx"]])
        s["classe"] = classe
    return shifts


# ─────────────────────────── Cruzamento com marcos ───────────────────────────

def cruzar_com_marcos(shifts: list[dict], tol: int = TOL_MARCO) -> list[dict]:
    """Para cada shift detectado, retorna o marco teorico mais proximo."""
    enriched = []
    for s in shifts:
        ano = s["ano"]
        marco_proximo = None
        dist_min = 999
        for ano_m, dados in MARCOS.items():
            dist = abs(ano - ano_m)
            if dist < dist_min:
                dist_min = dist
                marco_proximo = (ano_m, dados["titulo"], dist)
        enriched.append({
            **s,
            "marco_proximo_ano": marco_proximo[0] if marco_proximo else None,
            "marco_proximo_titulo": marco_proximo[1] if marco_proximo else None,
            "dist_marco": marco_proximo[2] if marco_proximo else None,
            "coincide_marco": marco_proximo[2] <= tol if marco_proximo else False,
        })
    return enriched


# ─────────────────────────── Carregamento ───────────────────────────

def carregar_series() -> tuple[np.ndarray, np.ndarray]:
    """Carrega as 3 series de delta_LULC para GO."""
    go = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")
    go = go.sort_values("ano").reset_index(drop=True)
    Y = np.column_stack([
        go["vegetacao_natural_delta_mha"].values,
        go["pastagem_delta_mha"].values,
        go["agricultura_delta_mha"].values,
    ])
    anos = go["ano"].values
    mask = ~np.isnan(Y).any(axis=1)
    return Y[mask], anos[mask]


# ─────────────────────────── Visualizacao ───────────────────────────

def plotar_stars(Y: np.ndarray, anos: np.ndarray,
                 all_shifts: list[dict]):
    """Gera figura com as 3 series e shifts detectados."""
    import matplotlib.pyplot as plt

    CLASSE_LABEL = {"vegetacao_natural": "Veg. natural", "pastagem": "Pastagem",
                    "agricultura": "Agricultura"}
    CLASSE_COR = {"vegetacao_natural": "#1B8A2F", "pastagem": "#D4A017",
                  "agricultura": "#FF69B4"}
    CLASSE_IDX = {"vegetacao_natural": 0, "pastagem": 1, "agricultura": 2}

    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    for i, (classe, label) in enumerate(CLASSE_LABEL.items()):
        ax = axes[i]
        idx = CLASSE_IDX[classe]
        ax.plot(anos, Y[:, idx], color=CLASSE_COR[classe], linewidth=1.5, label=label)

        # Shifts desta classe
        shifts_classe = [s for s in all_shifts if s["classe"] == classe]
        for s in shifts_classe:
            ax.axvline(s["ano"], color="blue", linestyle="-", linewidth=1.5,
                       alpha=0.7, label="STARS shift" if s == shifts_classe[0] else "")

        # Marcos teoricos
        for ano_m, dados in MARCOS.items():
            if dados["evidencia"] != "C":
                estilo = "-" if dados["evidencia"] == "A" else "--"
                ax.axvline(ano_m, color="gray", linestyle=estilo, alpha=0.4, linewidth=0.8)

        ax.set_ylabel(f"Delta {label} (Mha/ano)")
        ax.legend(loc="upper left", fontsize=8)
        ax.axhline(0, color="black", linewidth=0.3)

    anos_shifts = sorted(set(s["ano"] for s in all_shifts))
    fig.suptitle(f"Rodionov STARS — regime shifts (GO, l={REGIME_LENGTH}, alpha={ALPHA})\n"
                 f"Shifts detectados: {', '.join(str(a) for a in anos_shifts)}", fontsize=11)
    axes[-1].set_xlabel("Ano")

    fig.tight_layout()
    fig.savefig(DIR_OUT / "stars_go.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ─────────────────────────── Main ───────────────────────────

def main():
    print("Carregando series...")
    Y, anos = carregar_series()
    print(f"  {Y.shape[0]} anos, {Y.shape[1]} series (1986-2024)")

    # Rodionov STARS para cada serie
    all_shifts = []
    for i, classe in enumerate(CLASSES):
        print(f"\nSTARS para {classe}...")
        shifts = rodionov_stars_series(Y[:, i], anos, classe)
        print(f"  {len(shifts)} shifts: {[s['ano'] for s in shifts]}")
        all_shifts.extend(shifts)

    # Cruzar com marcos
    all_shifts_enriquecidos = cruzar_com_marcos(all_shifts)

    # Salvar
    df = pd.DataFrame(all_shifts_enriquecidos)
    out_csv = DIR_OUT / "stars_go.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\nResultados salvos em {out_csv}")

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO STARS (Rodionov 2004)")
    print("=" * 60)
    for classe in CLASSES:
        shifts_c = [s for s in all_shifts_enriquecidos if s["classe"] == classe]
        print(f"\n{classe}:")
        for s in shifts_c:
            status = "COINCIDE" if s["coincide_marco"] else "sem marco"
            print(f"  {s['ano']}: delta={s['delta']:+.4f}, "
                  f"marco={s['marco_proximo_titulo']} ({s['dist_marco']}a) [{status}]")

    # Anos unicos de shift (agregando todas as classes)
    anos_shifts = sorted(set(s["ano"] for s in all_shifts_enriquecidos))
    print(f"\nAnos com regime shift (todas as classes): {anos_shifts}")

    # Comparar com multivariado
    mv_csv = DIR_OUT / "quebras_multivariadas_go.csv"
    if mv_csv.exists():
        df_mv = pd.read_csv(mv_csv)
        mv_anos = set(df_mv["ano_quebra"].astype(int))
        stars_anos = set(anos_shifts)
        print(f"\nComparacao com sup-F multivariado:")
        print(f"  Multivariado: {sorted(mv_anos)}")
        print(f"  STARS: {sorted(stars_anos)}")
        print(f"  Convergentes: {sorted(mv_anos & stars_anos)}")

    # Plotar
    print("\nGerando figura...")
    plotar_stars(Y, anos, all_shifts_enriquecidos)
    print("Figura salva em outputs/correlacoes/stars_go.png")


if __name__ == "__main__":
    main()