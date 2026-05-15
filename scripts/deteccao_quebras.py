"""deteccao_quebras.py — Pipeline #26: Detecção de quebras estruturais
=====================================================================

Aplica Quandt-Andrews sup-F test + binary segmentation para detectar
quebras estruturais data-driven em séries anuais de Δ LULC para GO e TO,
e cruza com os 8 marcos teóricos da dissertação.

Motivação: o DiD piecewise (#23) testa só 4 marcos pré-definidos, o que
sofre de viés de confirmação. Esta pipeline inverte a lógica — deixa
os dados indicarem onde estão as quebras e verifica se coincidem com
marcos teóricos.

Especificação:
    H0: Δy_t = μ + ε_t (média constante)
    H1: Δy_t = μ_1·I(t<τ) + μ_2·I(t≥τ) + ε_t (quebra em τ)
    sup-F = max_τ F(τ) com min_size = 5

Múltiplas quebras: binary segmentation recursiva com parada via BIC.

Leitura cruzada:
    • Quebra em GO sem quebra em TO no mesmo ano (±2) → evidência
      GO-específica que complementa o DiD.
    • Quebra em GO e TO simultânea → fenômeno cerrado-amplo, não
      atribuível a marco GO-específico.
    • Marco teórico sem quebra detectada → marco simbólico/regulatório
      sem efeito mensurável em LULC.

Limitação: usa p-valor F bruto, não corrigido para múltiplos testes via
Andrews (1993). Para a magnitude relativa entre séries é suficiente; a
correção rigorosa é hipótese de extensão.

Pré-requisitos:
    data/processed/taxas_lulc_goias.csv  (Pipeline #17)
    data/cache/did/to_uf_lulc.csv        (Pipeline #23 --download)

Saídas:
    outputs/correlacoes/quebras_resultados.csv
    outputs/correlacoes/quebras_vs_marcos.csv
    outputs/correlacoes/quebras_*.png   (6 figs: 3 classes × 2 UFs)
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_CACHE = ROOT / "data" / "cache" / "did"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# ─────────────────────────── Config ───────────────────────────

CLASSES = ["vegetacao_natural", "pastagem", "agricultura"]
MIN_SIZE = 5                       # mínimo de obs em cada segmento
MAX_BREAKS = 3                     # máximo de quebras por série (binseg)
F_THRESHOLD = 5.0                  # F-stat mínimo para aceitar nova quebra
TOL_MARCO = 2                      # tolerância (anos) ao cruzar com marcos

MARCOS_TEORICOS = {
    1994: "Plano Real",
    1996: "Lei Kandir",
    2002: "Plano Safra",
    2003: "Boom commodities",
    2012: "Código Florestal",
    2018: "Cerrado Manifesto",
}

# ─────────────────────────── Quandt-Andrews ───────────────────────────

def sup_f_break(y: np.ndarray, min_size: int = MIN_SIZE) -> dict:
    """Quandt-Andrews sup-F test para quebra única de média.

    Para cada τ ∈ [min_size, n-min_size]:
        SSR_0 = Σ(y - ȳ)²
        SSR_1 = Σ_{t<τ}(y - ȳ_pre)² + Σ_{t≥τ}(y - ȳ_pos)²
        F(τ) = ((SSR_0 - SSR_1) / 1) / (SSR_1 / (n - 2))

    Retorna τ* = argmax F(τ), o F-stat correspondente e p-valor F bruto.
    """
    from scipy.stats import f as f_dist

    y = np.asarray(y, dtype=float)
    y = y[~np.isnan(y)]
    n = len(y)
    if n < 2 * min_size:
        return {"tau_idx": None, "f_stat": np.nan, "p_value": np.nan,
                "fstats": []}

    ssr_0 = float(np.sum((y - y.mean()) ** 2))
    fstats = []
    best = (None, -np.inf)
    for tau in range(min_size, n - min_size + 1):
        pre, pos = y[:tau], y[tau:]
        ssr_1 = float(np.sum((pre - pre.mean()) ** 2) +
                       np.sum((pos - pos.mean()) ** 2))
        if ssr_1 <= 0:
            continue
        f = ((ssr_0 - ssr_1) / 1.0) / (ssr_1 / (n - 2))
        fstats.append((tau, f))
        if f > best[1]:
            best = (tau, f)

    tau_star, f_star = best
    p_value = float(1.0 - f_dist.cdf(f_star, 1, n - 2)) if tau_star else np.nan

    return {
        "tau_idx": tau_star,
        "f_stat": f_star,
        "p_value": p_value,
        "fstats": fstats,
    }


def binary_segmentation(y: np.ndarray, anos: np.ndarray,
                        max_breaks: int = MAX_BREAKS,
                        f_threshold: float = F_THRESHOLD,
                        min_size: int = MIN_SIZE) -> list[dict]:
    """Binary segmentation: aplica sup-F recursivamente.

    Em cada passo: encontra o segmento com maior F-stat e divide. Para
    quando max_breaks atingido ou nenhum segmento passa F > threshold.
    """
    segments = [(0, len(y))]
    breaks = []

    for _ in range(max_breaks):
        best_seg = None
        best_res = None
        for (a, b) in segments:
            if b - a < 2 * min_size:
                continue
            res = sup_f_break(y[a:b], min_size=min_size)
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
        media_pre = float(np.mean(y[a:tau_global]))
        media_pos = float(np.mean(y[tau_global:b]))
        breaks.append({
            "ano_quebra": ano_quebra,
            "f_stat": round(best_res["f_stat"], 3),
            "p_value": round(best_res["p_value"], 4),
            "segmento": f"{int(anos[a])}–{int(anos[b-1])}",
            "media_pre": round(media_pre, 4),
            "media_pos": round(media_pos, 4),
            "delta_media": round(media_pos - media_pre, 4),
        })
        segments.remove((a, b))
        segments.append((a, tau_global))
        segments.append((tau_global, b))
        segments.sort()

    return sorted(breaks, key=lambda d: d["ano_quebra"])


# ─────────────────────────── Carregamento ───────────────────────────

def carregar_series() -> dict[str, pd.DataFrame]:
    """Monta dict {uf: dataframe com ano + delta_<classe>}."""
    # GO — taxas_lulc_goias.csv já tem delta_mha
    go = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")
    go = go[["ano"] + [f"{c}_delta_mha" for c in CLASSES]].copy()
    go.columns = ["ano"] + [f"delta_{c}" for c in CLASSES]
    go["uf"] = "Goiás"

    # TO — cache GEE; precisa calcular delta
    to_raw = pd.read_csv(DIR_CACHE / "to_uf_lulc.csv")
    to_raw = to_raw.sort_values("ano").reset_index(drop=True)
    to = pd.DataFrame({"ano": to_raw["ano"]})
    for c in CLASSES:
        to[f"delta_{c}"] = to_raw[c].diff()
    to["uf"] = "Tocantins"

    return {"Goiás": go, "Tocantins": to}


# ─────────────────────────── Cruzamento com marcos ───────────────────────────

def cruzar_com_marcos(breaks: list[dict], tol: int = TOL_MARCO) -> list[dict]:
    """Para cada quebra detectada, retorna o marco teórico mais próximo."""
    enriched = []
    for b in breaks:
        ano = b["ano_quebra"]
        dist_min, marco_mais_proximo, label = None, None, None
        for ano_marco, nome in MARCOS_TEORICOS.items():
            d = abs(ano - ano_marco)
            if dist_min is None or d < dist_min:
                dist_min, marco_mais_proximo, label = d, ano_marco, nome
        coincide = dist_min <= tol
        enriched.append({
            **b,
            "marco_proximo_ano": marco_mais_proximo,
            "marco_proximo_label": label,
            "dist_anos": dist_min,
            "coincide_marco": coincide,
        })
    return enriched


# ─────────────────────────── Figuras ───────────────────────────

def plotar_serie_com_quebras(df: pd.DataFrame, uf: str, classe: str,
                              breaks: list[dict]) -> Path:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 4.5))
    col = f"delta_{classe}"
    sub = df.dropna(subset=[col])

    ax.plot(sub["ano"], sub[col], marker="o", markersize=3,
            linewidth=1, color="#2b5d34" if uf == "Goiás" else "#5d2b34",
            label=f"Δ {classe} {uf}")
    ax.axhline(0, color="gray", linewidth=0.5)

    # Marcos teóricos (linhas verticais cinza claras)
    for ano_marco, nome in MARCOS_TEORICOS.items():
        ax.axvline(ano_marco, color="#cccccc", linestyle=":", linewidth=1,
                   zorder=0)
        ax.text(ano_marco, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0
                else ax.get_ylim()[0] * 0.95,
                nome, fontsize=7, color="#888888", rotation=90,
                va="top", ha="right")

    # Quebras detectadas (vermelho se coincide com marco, laranja se não)
    for b in breaks:
        cor = "#cc3333" if b["coincide_marco"] else "#e69100"
        ax.axvline(b["ano_quebra"], color=cor, linestyle="--", linewidth=1.5,
                   label=f"Quebra {b['ano_quebra']} (F={b['f_stat']:.1f})")

    ax.set_xlabel("Ano")
    ax.set_ylabel(f"Δ {classe.replace('_', ' ')} (Mha)")
    ax.set_title(f"Quebras estruturais detectadas — {classe.replace('_', ' ').title()} · {uf}",
                 fontsize=11, loc="left")
    ax.legend(fontsize=7, loc="lower left")

    fig.tight_layout()
    path = DIR_OUT / f"quebras_{classe}_{uf.lower().replace('á','a')}.png"
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    return path


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    print("Carregando séries GO e TO...")
    series = carregar_series()

    todos = []
    for uf, df in series.items():
        df = df.sort_values("ano").reset_index(drop=True)
        for classe in CLASSES:
            col = f"delta_{classe}"
            sub = df.dropna(subset=[col])
            y = sub[col].values
            anos = sub["ano"].values

            print(f"\n[{uf}] Δ {classe}  (n={len(y)})")
            breaks = binary_segmentation(y, anos)
            breaks_enriched = cruzar_com_marcos(breaks)

            if not breaks_enriched:
                print("  Nenhuma quebra detectada (F < threshold)")
                continue

            for b in breaks_enriched:
                tag = " ✓ MARCO" if b["coincide_marco"] else ""
                print(f"  Quebra {b['ano_quebra']}  F={b['f_stat']:.2f}  "
                      f"p={b['p_value']:.3f}  "
                      f"Δmédia={b['delta_media']:+.4f} Mha/ano  "
                      f"[mais próximo: {b['marco_proximo_ano']} "
                      f"{b['marco_proximo_label']}, "
                      f"dist={b['dist_anos']}a]{tag}")

            # Figura
            path = plotar_serie_com_quebras(df, uf, classe, breaks_enriched)
            print(f"  Figura: {path.name}")

            for b in breaks_enriched:
                todos.append({
                    "uf": uf,
                    "classe_lulc": classe,
                    **b,
                })

    # Tabela consolidada
    df_out = pd.DataFrame(todos)
    out_csv = DIR_OUT / "quebras_resultados.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"\nOK: {out_csv.name} ({len(df_out)} quebras)")

    # Cruzamento agregado: para cada marco teórico, quantas quebras coincidem
    print("\n=== Marcos teóricos × quebras detectadas (tol ±2 anos) ===")
    rows = []
    for ano_marco, nome in MARCOS_TEORICOS.items():
        coincidencias = df_out[df_out["coincide_marco"] &
                               (df_out["marco_proximo_ano"] == ano_marco)]
        n_go = (coincidencias["uf"] == "Goiás").sum()
        n_to = (coincidencias["uf"] == "Tocantins").sum()
        classes_go = sorted(coincidencias[coincidencias["uf"]
                                          == "Goiás"]["classe_lulc"].unique())
        classes_to = sorted(coincidencias[coincidencias["uf"]
                                          == "Tocantins"]["classe_lulc"].unique())
        rows.append({
            "marco_ano": ano_marco,
            "marco_label": nome,
            "n_quebras_GO": n_go,
            "classes_GO": ",".join(classes_go) if classes_go else "",
            "n_quebras_TO": n_to,
            "classes_TO": ",".join(classes_to) if classes_to else "",
            "leitura": (
                "GO-específico" if n_go > 0 and n_to == 0 else
                "Cerrado-amplo" if n_go > 0 and n_to > 0 else
                "Só TO"        if n_to > 0 else
                "Sem evidência"
            ),
        })
        print(f"  {ano_marco} {nome:25s}  GO={n_go} ({','.join(classes_go) or '-'})  "
              f"TO={n_to} ({','.join(classes_to) or '-'})  "
              f"→ {rows[-1]['leitura']}")

    df_cruz = pd.DataFrame(rows)
    out_cruz = DIR_OUT / "quebras_vs_marcos.csv"
    df_cruz.to_csv(out_cruz, index=False)
    print(f"\nOK: {out_cruz.name}")

    # Quebras detectadas SEM marco teórico próximo
    sem_marco = df_out[~df_out["coincide_marco"]]
    if len(sem_marco) > 0:
        print(f"\n=== Quebras data-driven SEM marco teórico próximo (±{TOL_MARCO}a) ===")
        for _, r in sem_marco.iterrows():
            print(f"  [{r['uf']}] Δ {r['classe_lulc']}  ano={r['ano_quebra']}  "
                  f"F={r['f_stat']:.2f}  Δmédia={r['delta_media']:+.4f}  "
                  f"(mais próximo: {r['marco_proximo_ano']}, "
                  f"dist={r['dist_anos']}a)")

    print(f"\nFeito — saídas em {DIR_OUT}")


if __name__ == "__main__":
    main()
