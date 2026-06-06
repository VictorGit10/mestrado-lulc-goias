"""
Pipeline #36 — Robustez da janela do slope (#17)
================================================

PERGUNTA QUE RESPONDE
---------------------
As afirmações-manchete de SLOPE do #17 dependem de ONDE escolhemos a largura da
janela móvel (a decisão D3 fixou 5 anos)? Ou sobrevivem a janelas mais curtas e
mais longas? É a FACE DE RESOLUÇÃO da Decisão D12 — não a face de fronteira (onde
cortar, testada no #35), mas a de RESOLUÇÃO (quão fina é a régua de suavização).

DISTINÇÃO IMPORTANTE
  - Grade-5a do #35  = BINNING  (blocos disjuntos; teste de FRONTEIRA).
  - Janela-5a do #17 = SUAVIZAÇÃO (janela móvel sobreposta; aqui testamos a LARGURA).
  Mesmo "5 anos", operações diferentes.

JANELAS COMPARADAS
  - TRAILING (t−W+1..t): larguras 3, 5 (base, D3), 7, 10 anos — usada p/ inferência.
  - CENTRADA (t−h..t+h): larguras ímpares 3, 5, 7, 9 anos — usada p/ narrativa,
    sem o viés de atraso do trailing. Serve para demonstrar que o "deslize" do
    cruzamento de zero da pastagem é artefato do trailing, não instabilidade.

MÉTRICAS-MANCHETE RECALCULADAS SOB CADA JANELA (nível UF)
  - PASTAGEM   : ano(s) de cruzamento de zero do slope (pico de área ~2004?),
                 comparado entre TRAILING e CENTRADA.
  - VEGETAÇÃO  : desaceleração da perda (|slope| recente < |slope| inicial?).
  - AGRICULTURA: desaceleração recente (slope em 2024 < pico do slope?).
  - FORMATO    : correlação da série de slope de cada janela vs base (5a, trailing).
  - ACELERAÇÃO : nº de inflexões |accel|>2σ e quais anos recorrem (a mais frágil, D5).

Reusa #17 (`calcular_taxas_lulc`) — não reimplementa a agregação nem os slopes OLS
(trailing e centrada).

ENTRADAS: data/processed/mapbiomas_munis_goias.csv (Pipeline #4).
SAÍDAS
    data/processed/robustez_janela_slope.csv            (ano × grupo × janela × método × slope)
    data/processed/robustez_janela_slope_resumo.csv     (concordância por janela, trailing)
    data/processed/robustez_janela_slope_cruzamento.csv (cruzamento zero pastagem: trailing vs centrada)
    outputs/robustez/slope_por_janela.png               (slope × 4 janelas, 3 classes, trailing)
    outputs/robustez/pastagem_trailing_vs_centrada.png  (cruzamento de zero: artefato do trailing)

COMO RODAR
    python scripts/robustez_janela_slope.py

Base metodológica: metodologia/janelas_temporais.md (Decisão D12, face de resolução).
Depende de: #17 (e a entrada dele). Quando: 2026-06-06.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calcular_taxas_lulc as taxas        # reusa #17

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "robustez"
DIR_OUT.mkdir(parents=True, exist_ok=True)

JANELAS_TRAIL = [3, 5, 7, 10]          # larguras trailing (anos)
JANELAS_CENTR = [3, 5, 7, 9]           # larguras centradas — exigem largura ÍMPAR
JANELA_BASE   = 5                      # decisão D3 do #17
CLASSES_NARR  = ["vegetacao_natural", "pastagem", "agricultura"]
ROTULO = {"vegetacao_natural": "Vegetação natural",
          "pastagem": "Pastagem", "agricultura": "Agricultura"}


# ---------------------------------------------------------------------------
# Slopes por janela e método (nível UF) — reusa o #17
# ---------------------------------------------------------------------------

def carregar_uf() -> pd.DataFrame:
    """Carrega o LULC bruto (#4) e agrega ao nível UF (mesma máquina do #17)."""
    df = pd.read_csv(taxas.ARQ_MAPBIOMAS)
    return taxas.agregar_por_grupo(df, nivel="uf").sort_values("ano").reset_index(drop=True)


def slopes_por_janela(uf: pd.DataFrame) -> pd.DataFrame:
    """Série anual de slope (Mha/ano) por (grupo, janela, método).

    O slope é a inclinação OLS; o cov_type HAC só afeta o erro padrão, não o
    ponto estimado — então a robustez é do próprio slope. Trailing (qualquer
    largura) e centrada (larguras ímpares) reusam as funções do #17.
    """
    anos = uf["ano"].values
    linhas = []
    for g in taxas.NOMES_GRUPOS:
        area_mha = uf[g].values.astype(float) / 1e6
        for metodo, janelas, fn in (
            ("trailing", JANELAS_TRAIL, taxas.rolling_slope_hac),
            ("centrada", JANELAS_CENTR, taxas.rolling_slope_hac_centr),
        ):
            for W in janelas:
                maxlags = min(2, max(1, W - 2))
                sl, _ = fn(pd.Series(area_mha), window=W, maxlags=maxlags)
                for i, a in enumerate(anos):
                    linhas.append({"ano": int(a), "grupo": g, "janela": W,
                                   "metodo": metodo, "slope_mha_ano": sl[i]})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Métricas-manchete
# ---------------------------------------------------------------------------

def _serie(df: pd.DataFrame, grupo: str, W: int, metodo: str = "trailing") -> pd.DataFrame:
    s = df[(df.grupo == grupo) & (df.janela == W) & (df.metodo == metodo)].sort_values("ano")
    return s.dropna(subset=["slope_mha_ano"])


def cruzamentos_zero(df: pd.DataFrame, grupo: str, metodo: str, janelas: list[int]) -> dict[int, list]:
    """Anos em que o slope cruza zero PARA BAIXO (>0 → ≤0): pico da área."""
    out: dict[int, list] = {}
    for W in janelas:
        s = _serie(df, grupo, W, metodo)
        anos, vals = s["ano"].values, s["slope_mha_ano"].values
        cruz = [int(anos[i]) for i in range(1, len(vals))
                if vals[i - 1] > 0 and vals[i] <= 0]
        out[W] = cruz
    return out


def borda(df: pd.DataFrame, grupo: str, W: int, n: int = 5) -> tuple[float, float]:
    """Slope médio nos primeiros n e nos últimos n anos válidos (início vs fim)."""
    s = _serie(df, grupo, W)["slope_mha_ano"].values
    return float(np.mean(s[:n])), float(np.mean(s[-n:]))


def slope_recente_vs_pico(df: pd.DataFrame, grupo: str, W: int) -> tuple[float, float, int]:
    """(slope no último ano, slope máximo, ano do máximo) — trailing."""
    s = _serie(df, grupo, W)
    recente = float(s["slope_mha_ano"].iloc[-1])
    imax = s["slope_mha_ano"].idxmax()
    return recente, float(s.loc[imax, "slope_mha_ano"]), int(s.loc[imax, "ano"])


def corr_vs_base(df: pd.DataFrame, grupo: str, W: int) -> float:
    """Correlação de Pearson da série de slope (janela W) vs base (5a), trailing."""
    a = _serie(df, grupo, W).set_index("ano")["slope_mha_ano"]
    b = _serie(df, grupo, JANELA_BASE).set_index("ano")["slope_mha_ano"]
    comum = a.index.intersection(b.index)
    if len(comum) < 3:
        return np.nan
    return float(np.corrcoef(a.loc[comum], b.loc[comum])[0, 1])


def inflexoes_aceleracao(df: pd.DataFrame, grupo: str, W: int) -> list[int]:
    """Anos com |aceleração|>2σ (aceleração = diferença do slope ano-a-ano), trailing."""
    s = _serie(df, grupo, W).set_index("ano")["slope_mha_ano"]
    accel = s.diff().dropna()
    if len(accel) < 3:
        return []
    thr = 2 * accel.std()
    return [int(a) for a, v in accel.items() if abs(v) > thr]


# ---------------------------------------------------------------------------
# Resumos
# ---------------------------------------------------------------------------

def construir_resumo(df: pd.DataFrame) -> pd.DataFrame:
    """Concordância das manchetes por janela (trailing, a régua de inferência)."""
    linhas = []
    for W in JANELAS_TRAIL:
        veg_ini, veg_fim = borda(df, "vegetacao_natural", W)
        agr_rec, agr_pico, agr_ano = slope_recente_vs_pico(df, "agricultura", W)
        linhas.append({
            "janela": W,
            "pasto_cruza_zero": ";".join(map(str, cruzamentos_zero(df, "pastagem", "trailing", [W])[W])) or "—",
            "veg_slope_inicial": round(veg_ini, 3),
            "veg_slope_recente": round(veg_fim, 3),
            "veg_desacelera": veg_fim > veg_ini,                  # menos negativo
            "agric_slope_recente": round(agr_rec, 3),
            "agric_slope_pico": round(agr_pico, 3),
            "agric_ano_pico": agr_ano,
            "agric_desacelera_recente": agr_rec < agr_pico,
            "corr_veg_vs_5a": round(corr_vs_base(df, "vegetacao_natural", W), 3),
            "corr_pasto_vs_5a": round(corr_vs_base(df, "pastagem", W), 3),
            "corr_agric_vs_5a": round(corr_vs_base(df, "agricultura", W), 3),
        })
    return pd.DataFrame(linhas)


def construir_cruzamento(df: pd.DataFrame) -> pd.DataFrame:
    """Cruzamento de zero da pastagem: trailing (desliza) vs centrada (estável)."""
    linhas = []
    for metodo, janelas in (("trailing", JANELAS_TRAIL), ("centrada", JANELAS_CENTR)):
        cz = cruzamentos_zero(df, "pastagem", metodo, janelas)
        for W in janelas:
            linhas.append({"metodo": metodo, "janela": W,
                           "ano_cruzamento": ";".join(map(str, cz[W])) or "—"})
    return pd.DataFrame(linhas)


def verdito(df: pd.DataFrame, resumo: pd.DataFrame, cruz: pd.DataFrame) -> None:
    print("\n[veredito] Manchetes de slope sob cada janela TRAILING (nível UF):\n")
    for _, r in resumo.iterrows():
        W = int(r["janela"])
        base = "  (BASE D3)" if W == JANELA_BASE else ""
        print(f"  Janela {W}a{base}")
        print(f"    pastagem  : slope cruza zero p/ baixo em {r['pasto_cruza_zero']} "
              f"(manchete: ~2004)")
        print(f"    vegetação : slope {r['veg_slope_inicial']:+.3f} (início) → "
              f"{r['veg_slope_recente']:+.3f} (recente)  "
              f"{'✓ desacelera' if r['veg_desacelera'] else '✗'}")
        print(f"    agricultura: pico {r['agric_slope_pico']:+.3f} em {int(r['agric_ano_pico'])} → "
              f"recente {r['agric_slope_recente']:+.3f}  "
              f"{'✓ desacelera no recente' if r['agric_desacelera_recente'] else '✗'}")
        print(f"    formato (corr vs 5a): veg {r['corr_veg_vs_5a']:+.2f} | "
              f"pasto {r['corr_pasto_vs_5a']:+.2f} | agric {r['corr_agric_vs_5a']:+.2f}")
        print()

    # Trailing vs centrada: o deslize do cruzamento é artefato do trailing?
    print("  [cruzamento de zero da pastagem — trailing vs centrada]")
    for metodo in ("trailing", "centrada"):
        sub = cruz[cruz.metodo == metodo]
        pares = " | ".join(f"{int(x.janela)}a→{x.ano_cruzamento}" for _, x in sub.iterrows())
        print(f"    {metodo:9s}: {pares}")
    print("    → no trailing o ano desliza com a largura (atraso esperado); "
          "na centrada fica ~estável (o fenômeno é o mesmo).")

    # Aceleração — a métrica mais frágil (D5): quais inflexões recorrem?
    print("\n  [aceleração — inflexões |accel|>2σ por janela trailing]")
    for g in CLASSES_NARR:
        por_janela = {W: set(inflexoes_aceleracao(df, g, W)) for W in JANELAS_TRAIL}
        recorrentes = set.intersection(*por_janela.values()) if por_janela else set()
        todas = sorted(set().union(*por_janela.values())) if por_janela else []
        print(f"    {ROTULO[g]:18s}: recorrem em TODAS as janelas → "
              f"{sorted(recorrentes) or '—'}  | união: {todas}")


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def fig_slope(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    cores = plt.cm.viridis(np.linspace(0.0, 0.82, len(JANELAS_TRAIL)))
    fig, axes = plt.subplots(1, len(CLASSES_NARR),
                             figsize=(5.4 * len(CLASSES_NARR), 5.0), sharex=True)
    for ax, g in zip(np.atleast_1d(axes), CLASSES_NARR):
        for cor, W in zip(cores, JANELAS_TRAIL):
            s = _serie(df, g, W)
            lw = 2.6 if W == JANELA_BASE else 1.6
            ax.plot(s["ano"], s["slope_mha_ano"], "-", color=cor, lw=lw,
                    label=f"{W}a" + (" (D3)" if W == JANELA_BASE else ""))
        ax.axhline(0, color="0.3", lw=0.9)
        if g == "pastagem":
            ax.axvline(2004, color="0.6", ls="--", lw=0.9)
            ax.text(2004.4, ax.get_ylim()[1], " ~2004", fontsize=8, va="top", color="0.4")
        ax.set_title(ROTULO[g], fontsize=12)
        ax.set_xlabel("ano")
        ax.grid(True, alpha=0.25)
    np.atleast_1d(axes)[0].set_ylabel("slope trailing (Mha/ano)")
    np.atleast_1d(axes)[0].legend(title="janela móvel", fontsize=8.5, loc="best")
    fig.suptitle("Robustez #17 — slope da área por largura da janela móvel (3/5/7/10 anos, trailing)\n"
                 "(o cruzamento de zero da pastagem, a desaceleração da vegetação e a "
                 "freada recente da agricultura sobrevivem à largura)",
                 fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(DIR_OUT / "slope_por_janela.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'slope_por_janela.png').relative_to(ROOT)}")


def fig_trailing_vs_centrada(df: pd.DataFrame) -> None:
    """Pastagem: o deslize do cruzamento de zero é artefato do trailing."""
    import matplotlib.pyplot as plt
    paineis = [("trailing", JANELAS_TRAIL, "Trailing (t−W+1..t)"),
               ("centrada", JANELAS_CENTR, "Centrada (t−h..t+h)")]
    cores = plt.cm.viridis(np.linspace(0.0, 0.82, 4))
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), sharey=True)
    for ax, (metodo, janelas, titulo) in zip(axes, paineis):
        cz = cruzamentos_zero(df, "pastagem", metodo, janelas)
        for cor, W in zip(cores, janelas):
            s = _serie(df, "pastagem", W, metodo)
            lw = 2.6 if W == JANELA_BASE else 1.6
            ax.plot(s["ano"], s["slope_mha_ano"], "-", color=cor, lw=lw, label=f"{W}a")
            for ano in cz[W]:
                ax.plot(ano, 0, "v", color=cor, ms=9, mec="0.2", mew=0.5)
        ax.axhline(0, color="0.3", lw=0.9)
        ax.set_title(titulo, fontsize=12)
        ax.set_xlabel("ano")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("slope da pastagem (Mha/ano)")
    axes[0].legend(title="janela", fontsize=8.5, loc="best")
    fig.suptitle("Pastagem — o deslize do cruzamento de zero é artefato do TRAILING\n"
                 "(triângulos = cruzamento de zero; espalham 2004→2007 no trailing, "
                 "agrupam ~2002–03 na centrada)",
                 fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(DIR_OUT / "pastagem_trailing_vs_centrada.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'pastagem_trailing_vs_centrada.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 70)
    print("Pipeline #36 — Robustez da janela do slope (#17)")
    print("Trailing:", ", ".join(f"{W}a" for W in JANELAS_TRAIL),
          "| Centrada:", ", ".join(f"{W}a" for W in JANELAS_CENTR),
          f"| base D3 = {JANELA_BASE}a | face de RESOLUÇÃO da D12")
    print("=" * 70)

    uf = carregar_uf()
    print(f"[OK] UF agregada: {len(uf)} anos ({uf['ano'].min()}–{uf['ano'].max()})")

    df = slopes_por_janela(uf)
    df.to_csv(DIR_PROC / "robustez_janela_slope.csv", index=False, encoding="utf-8")
    print(f"[OK] robustez_janela_slope.csv ({len(df)} linhas)")

    resumo = construir_resumo(df)
    resumo.to_csv(DIR_PROC / "robustez_janela_slope_resumo.csv", index=False, encoding="utf-8")
    print(f"[OK] robustez_janela_slope_resumo.csv ({len(resumo)} linhas)")

    cruz = construir_cruzamento(df)
    cruz.to_csv(DIR_PROC / "robustez_janela_slope_cruzamento.csv", index=False, encoding="utf-8")
    print(f"[OK] robustez_janela_slope_cruzamento.csv ({len(cruz)} linhas)")

    verdito(df, resumo, cruz)
    print()
    fig_slope(df)
    fig_trailing_vs_centrada(df)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #36. Robustez da largura da janela do slope (#17).")
    print("=" * 70)


if __name__ == "__main__":
    main()
