"""periodizacao_multivariada.py — Pipeline #29: Quebras estruturais multivariadas
==============================================================================

Estende o Pipeline #26 (deteccao_quebras.py) para testar as 3 series de GO
(Δveg_nat, Δpast, Δagric) conjuntamente, detectando mudancas na distribuicao
conjunta em vez de em cada serie separadamente.

Metodo: sup-F multivariado (Bai-Lumsdaine-Stock 1998) com binary segmentation.

Especificacao:
    H0: Y_t = μ + ε_t  (vetor de media p-dimensional constante)
    H1: Y_t = μ_1·I(t<τ) + μ_2·I(t≥τ) + ε_t  (quebra em τ)

    sup-F(τ) = max_τ  F(τ)

    F(τ) = [(SSR_0 - SSR_1) / p] / [SSR_1 / (n*p - 2p)]

    onde SSR_0 = soma dos SSR das p series sob H0 (media unica)
    e    SSR_1 = soma dos SSR das p series sob H1 (duas medias)

Triangulacao com Pipeline #26:
    - Pipeline #26 detecta quebras univariadas (poder para series individuais)
    - Este pipeline detecta quebras no VETOR conjunto (poder para mudancas de regime)
    - Se ambos convergem para o mesmo ano: fronteira confirmada
    - Se divergem: sensibilidade ao metodo (documentar como achado)

Prerequisitos:
    data/processed/taxas_lulc_goias.csv  (Pipeline #17)
    data/cache/did/to_uf_lulc.csv         (Pipeline #23 --download)

Saidas:
    outputs/correlacoes/quebras_multivariadas_go.csv
    outputs/correlacoes/quebras_multivariadas_go.png
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_CACHE = ROOT / "data" / "cache" / "did"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

from config_periodos import MARCOS, ATOS, CORES_ATO

# ─────────────────────────── Config ───────────────────────────

CLASSES = ["vegetacao_natural", "pastagem", "agricultura"]
MIN_SIZE = 5        # minimo de obs em cada segmento
MAX_BREAKS = 3      # maximo de quebras (binseg)
F_THRESHOLD = 4.0   # F-stat minimo para aceitar nova quebra (mais liberal que univariado pois p=3)
TOL_MARCO = 2       # tolerancia (anos) ao cruzar com marcos

# ─────────────────────────── sup-F multivariado ───────────────────────────

def sup_f_multivariado(Y: np.ndarray, min_size: int = MIN_SIZE) -> dict:
    """sup-F test multivariado para quebra de vetor de media.

    Y: array (n, p) com p series temporais
    Retorna tau*, F*, p-valor e lista de F(τ) para todos os candidatos.
    """
    n, p = Y.shape
    if n < 2 * min_size:
        return {"tau_idx": None, "f_stat": np.nan, "p_value": np.nan,
                "fstats": []}

    # SSR restrito: media unica para cada serie
    ssr_0 = 0.0
    for j in range(p):
        ssr_0 += float(np.sum((Y[:, j] - Y[:, j].mean()) ** 2))

    fstats = []
    best = (None, -np.inf)
    for tau in range(min_size, n - min_size + 1):
        pre, pos = Y[:tau], Y[tau:]
        ssr_1 = 0.0
        for j in range(p):
            ssr_1 += float(np.sum((pre[:, j] - pre[:, j].mean()) ** 2) +
                          np.sum((pos[:, j] - pos[:, j].mean()) ** 2))
        if ssr_1 <= 0:
            continue
        # F = [(SSR_0 - SSR_1) / p] / [SSR_1 / (n*p - 2p)]
        df_num = p
        df_den = n * p - 2 * p
        if df_den <= 0:
            continue
        f = ((ssr_0 - ssr_1) / df_num) / (ssr_1 / df_den)
        fstats.append((tau, f))
        if f > best[1]:
            best = (tau, f)

    tau_star, f_star = best
    p_value = float(1.0 - f_dist.cdf(f_star, p, n * p - 2 * p)) if tau_star else np.nan

    return {
        "tau_idx": tau_star,
        "f_stat": f_star,
        "p_value": p_value,
        "fstats": fstats,
    }


def binary_segmentation_mv(Y: np.ndarray, anos: np.ndarray,
                           max_breaks: int = MAX_BREAKS,
                           f_threshold: float = F_THRESHOLD,
                           min_size: int = MIN_SIZE) -> list[dict]:
    """Binary segmentation multivariado: aplica sup-F recursivamente."""
    segments = [(0, len(Y))]
    breaks = []

    for _ in range(max_breaks):
        best_seg = None
        best_res = None
        for (a, b) in segments:
            if b - a < 2 * min_size:
                continue
            res = sup_f_multivariado(Y[a:b], min_size=min_size)
            if res["tau_idx"] is None:
                continue
            if best_res is None or res["f_stat"] > best_res["f_stat"]:
                best_seg = (a, b)
                best_res = res

        if best_res is None or best_res["f_stat"] < f_threshold:
            break

        a, b = best_seg
        tau_global = a + best_res["tau_idx"]
        ano_quebra = int(anos[tau_global])
        # Medias pre/post para cada serie
        media_pre = Y[a:tau_global].mean(axis=0)
        media_pos = Y[tau_global:b].mean(axis=0)
        delta = media_pos - media_pre
        breaks.append({
            "ano_quebra": ano_quebra,
            "f_stat": round(best_res["f_stat"], 3),
            "p_value": round(best_res["p_value"], 4),
            "segmento": f"{int(anos[a])}-{int(anos[b-1])}",
            "delta_veg_nat": round(float(delta[0]), 4),
            "delta_past": round(float(delta[1]), 4),
            "delta_agric": round(float(delta[2]), 4),
        })
        segments.remove((a, b))
        segments.append((a, tau_global))
        segments.append((tau_global, b))
        segments.sort()

    return sorted(breaks, key=lambda d: d["ano_quebra"])


# ─────────────────────────── Carregamento ───────────────────────────

def carregar_series() -> tuple[np.ndarray, np.ndarray]:
    """Carrega as 3 series de delta_LULC para GO como array (n, 3)."""
    go = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")
    go = go.sort_values("ano").reset_index(drop=True)
    Y = np.column_stack([
        go["vegetacao_natural_delta_mha"].values,
        go["pastagem_delta_mha"].values,
        go["agricultura_delta_mha"].values,
    ])
    anos = go["ano"].values
    # Remover NaNs (primeira linha de diff)
    mask = ~np.isnan(Y).any(axis=1)
    return Y[mask], anos[mask]


# ─────────────────────────── Cruzamento com marcos ───────────────────────────

def cruzar_com_marcos(breaks: list[dict], tol: int = TOL_MARCO) -> list[dict]:
    """Para cada quebra detectada, retorna o marco teorico mais proximo."""
    enriched = []
    for b in breaks:
        ano = b["ano_quebra"]
        marco_proximo = None
        dist_min = 999
        for ano_m, dados in MARCOS.items():
            dist = abs(ano - ano_m)
            if dist < dist_min:
                dist_min = dist
                marco_proximo = (ano_m, dados["titulo"], dist)
        enriched.append({
            **b,
            "marco_proximo_ano": marco_proximo[0] if marco_proximo else None,
            "marco_proximo_titulo": marco_proximo[1] if marco_proximo else None,
            "dist_marco": marco_proximo[2] if marco_proximo else None,
            "coincide_marco": marco_proximo[2] <= tol if marco_proximo else False,
        })
    return enriched


# ─────────────────────────── Visualizacao ───────────────────────────

def plotar_quebras_multivariadas(Y: np.ndarray, anos: np.ndarray,
                                 breaks: list[dict],
                                 breaks_univ: pd.DataFrame | None = None):
    """Gera figura com as 3 series e quebras detectadas."""
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

        # Quebras multivariadas
        for b in breaks:
            ax.axvline(b["ano_quebra"], color="red", linestyle="-", linewidth=1.5,
                       alpha=0.7)

        # Marcos teoricos
        for ano_m, dados in MARCOS.items():
            if dados["evidencia"] != "C":  # nao plotar fronteira
                estilo = "-" if dados["evidencia"] == "A" else "--"
                ax.axvline(ano_m, color="gray", linestyle=estilo, alpha=0.4, linewidth=0.8)

        ax.set_ylabel(f"Δ {label} (Mha/ano)")
        ax.legend(loc="upper left", fontsize=8)
        ax.axhline(0, color="black", linewidth=0.3)

    # Legenda de quebras
    anos_q = ", ".join(str(b["ano_quebra"]) for b in breaks)
    fig.suptitle(f"Quebras estruturais multivariadas (GO) — sup-F multivariado\n"
                 f"Quebras detectadas: {anos_q}", fontsize=11)

    axes[-1].set_xlabel("Ano")

    fig.tight_layout()
    fig.savefig(DIR_OUT / "quebras_multivariadas_go.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ─────────────────────────── Main ───────────────────────────

def main():
    print("Carregando series...")
    Y, anos = carregar_series()
    print(f"  {Y.shape[0]} anos, {Y.shape[1]} series (1986-2024)")

    # Quebras multivariadas
    print("\nDetecção de quebras multivariadas (binary segmentation)...")
    breaks = binary_segmentation_mv(Y, anos)
    print(f"  {len(breaks)} quebras detectadas:")
    for b in breaks:
        print(f"    {b['ano_quebra']}: F={b['f_stat']:.1f}, p={b['p_value']:.4f}, "
              f"delta=[{b['delta_veg_nat']:+.4f}, {b['delta_past']:+.4f}, {b['delta_agric']:+.4f}]")

    # Cruzar com marcos
    breaks_enriquecidos = cruzar_com_marcos(breaks)
    print("\nCruzamento com marcos teoricos:")
    for b in breaks_enriquecidos:
        status = "COINCIDE" if b["coincide_marco"] else "sem marco proximo"
        print(f"    {b['ano_quebra']}: {b['marco_proximo_titulo']} "
              f"(dist={b['dist_marco']}a) [{status}]")

    # Salvar resultados
    df = pd.DataFrame(breaks_enriquecidos)
    out_csv = DIR_OUT / "quebras_multivariadas_go.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\nResultados salvos em {out_csv}")

    # Comparar com Pipeline #26 (univariado)
    univ_csv = DIR_OUT / "quebras_resultados.csv"
    breaks_univ = None
    if univ_csv.exists():
        df_univ = pd.read_csv(univ_csv)
        breaks_univ = df_univ[df_univ["uf"] == "Goiás"]
        print(f"\nComparação com Pipeline #26 (univariado, GO):")
        go_breaks = df_univ[df_univ["uf"] == "Goiás"]["ano_quebra"].unique()
        mv_breaks = set(b["ano_quebra"] for b in breaks)
        print(f"  Univariado: {sorted(go_breaks)}")
        print(f"  Multivariado: {sorted(mv_breaks)}")
        print(f"  Convergentes: {sorted(set(go_breaks) & mv_breaks)}")
        print(f"  Apenas univariado: {sorted(set(go_breaks) - mv_breaks)}")
        print(f"  Apenas multivariado: {sorted(mv_breaks - set(go_breaks))}")

    # Plotar
    print("\nGerando figura...")
    plotar_quebras_multivariadas(Y, anos, breaks, breaks_univ)
    print("Figura salva em outputs/correlacoes/quebras_multivariadas_go.png")

    # Resumo para triangulacao
    print("\n" + "=" * 60)
    print("RESUMO PARA TRIANGULACAO")
    print("=" * 60)
    print(f"Metodo: sup-F multivariado (p=3 series)")
    print(f"Quebras detectadas: {len(breaks)}")
    for b in breaks_enriquecidos:
        print(f"  {b['ano_quebra']}: F={b['f_stat']:.1f}, "
              f"marco={b['marco_proximo_titulo']} ({b['dist_marco']}a), "
              f"coincide={b['coincide_marco']}")
    print("\nProximos passos:")
    print("  1. Rodar periodizacao_transicoes.py (KL + bootstrap)")
    print("  2. Rodar periodizacao_stars.py (Rodionov STARS)")
    print("  3. Comparar fronteira confirmada = primario + >=1 sensibilidade")


if __name__ == "__main__":
    main()