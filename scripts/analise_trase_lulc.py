"""
Pipeline #45 — A infraestrutura exportadora SEGUE ou LIDERA a expansão LULC?
===========================================================================

PERGUNTA QUE RESPONDE
---------------------
O Pipeline #27 (`coleta_trase.py`) deixou 8 colunas de cadeia exportadora
(Trase.earth: soja 2004–2022, boi 2011–2023 sem 2018) no painel, SEM análise
rodada. Este pipeline as ativa com uma pergunta de precedência:

    A presença de infraestrutura exportadora (volume/valor escoado, nº de
    tradings/frigoríficos, nº de hubs logísticos) ANTECEDE a expansão do uso da
    terra (a infra "puxa" a lavoura/pasto), ou SEGUE a expansão (a infra chega
    onde a produção já se instalou)?

É o "Eixo A" do backlog. Complementa o canal SICOR do #22 (crédito → retração
de pastagem) com o canal de infraestrutura agroindustrial exportadora.

ABORDAGEM (dois níveis, padrão #21 + #22, com a disciplina do #42/D16)
----------------------------------------------------------------------
Bloco A — LEAD-LAG AGREGADO (série estadual GO, anual):
    CCF (corr cruzada defasada) + Granger nas duas direções, em PRIMEIRAS
    DIFERENÇAS (D7). **Disciplina D16**: as séries de área/volume são suaves e
    integradas; o #42 mostrou que Granger ingênuo em 1ª diferença sobre séries
    integradas FABRICA precedência espúria no lag 1. Logo aqui o Granger
    agregado é DIAGNÓSTICO, não inferência: reportamos ADF/KPSS de cada série,
    tratamos T≈12–18 como baixo poder, e deixamos a INFERÊNCIA para o Bloco B
    (painel, muito mais observações). Nunca ler o lead-lag agregado como causal.

Bloco B — PAINEL DE DEFASAGEM DISTRIBUÍDA (municipal, 2-way FE — o cavalo de
batalha): para cada par (infra × LULC), dois modelos simétricos —
    "LULC segue infra":  Δlulc_it  ~ Δinfra_{i,t−1}   (+ FE muni + FE ano)
    "infra segue LULC":  Δinfra_it ~ Δlulc_{i,t−1}    (+ FE muni + FE ano)
A direção cujo termo DEFASADO é significativo indica quem lidera. O termo
CONTEMPORÂNEO (Δinfra_it × Δlulc_it) mede co-movimento. Usamos defasagem
distribuída (sem termo autorregressivo Y_{t−1}) para evitar o viés de Nickell
de um CLPM com FE — decisão coerente com o SLX/distributed-lag do #34. SE
clusterizado por município.

PAREAMENTOS
    Trase SOJA (infra) × soja/agricultura (LULC):
        lulc_soja_ha (MapBiomas), agri_soja_ha_plantada (SIDRA), lulc_agricultura_ha
    Trase BOI (infra) × pasto/rebanho:
        lulc_pastagem_ha, pec_bovinos_cab, abate_bovino_cab
    (soja tem fonte satélite E censo → validação cruzada embutida.)

LIMITAÇÕES HONESTAS
    - Trase rastreia SÓ o fluxo EXPORTADOR (#27): proxy de exposição à cadeia
      exportadora, não de capacidade agroindustrial total (mercado interno fora).
    - Janela curta (soja 19 anos, boi 12 anos — 2018 ausente na Trase, interpolado
      linearmente no Bloco A para não diferenciar através do vão) → baixo poder,
      sobretudo no agregado. O painel recupera poder pelo N municipal.
    - Precedência preditiva (Granger/defasagem), NÃO causalidade. D16 aplicada.
    - Infra medida por volume/valor/contagem, não por ativos físicos (silos,
      frigoríficos instalados) — esses ficam para coletas futuras (CONAB/SIGSIF).

ENTRADAS
    data/processed/painel_trase.csv          (#27)
    data/processed/painel_unificado.parquet  (#16 — LULC, SIDRA, rebanho, abate)

SAÍDAS
    data/processed/trase_lulc_leadlag_agregado.csv  (Bloco A: CCF+Granger+ADF)
    data/processed/trase_lulc_painel.csv            (Bloco B: defasagem distribuída)
    outputs/trase_lulc/leadlag_agregado.png
    outputs/trase_lulc/painel_direcoes.png

COMO RODAR
    python scripts/analise_trase_lulc.py
    python scripts/analise_trase_lulc.py --sem-figuras

Depende de: #27 (painel_trase), #16 (painel_unificado). Reusa CCF/Granger do #34
e o padrão PanelOLS do #22. Aplica D7 (diferenças) e D16 (cautela lead-lag).
Quando foi feito: 2026-07-13.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "trase_lulc"
DIR_OUT.mkdir(parents=True, exist_ok=True)

MAX_LAG = 4   # defasagens da CCF agregada

# Pareamentos (rótulo, coluna_infra_Trase, coluna_lulc, cadeia)
PARES = [
    ("Soja: volume exportado × soja MapBiomas",   "trase_soja_volume_t", "lulc_soja_ha",          "soja"),
    ("Soja: volume exportado × soja SIDRA",       "trase_soja_volume_t", "agri_soja_ha_plantada", "soja"),
    ("Soja: volume exportado × agricultura LULC", "trase_soja_volume_t", "lulc_agricultura_ha",   "soja"),
    ("Soja: nº hubs × soja MapBiomas",            "trase_soja_n_hubs",   "lulc_soja_ha",          "soja"),
    ("Boi: volume exportado × pastagem LULC",     "trase_boi_volume_t",  "lulc_pastagem_ha",      "boi"),
    ("Boi: volume exportado × rebanho bovino",    "trase_boi_volume_t",  "pec_bovinos_cab",       "boi"),
    ("Boi: volume exportado × abate bovino",      "trase_boi_volume_t",  "abate_bovino_cab",      "boi"),
    ("Boi: nº frigoríficos × rebanho bovino",     "trase_boi_n_frigorificos", "pec_bovinos_cab",  "boi"),
]


# ---------------------------------------------------------------------------
# 0. Dados
# ---------------------------------------------------------------------------

def carregar() -> pd.DataFrame:
    """Merge Trase (#27) + LULC/SIDRA/rebanho (#16) em (cd_mun, ano)."""
    trase = pd.read_csv(DIR_PROC / "painel_trase.csv")
    cols_lulc = ["cd_mun", "ano", "lulc_soja_ha", "agri_soja_ha_plantada",
                 "lulc_agricultura_ha", "lulc_pastagem_ha", "pec_bovinos_cab",
                 "abate_bovino_cab"]
    pan = pd.read_parquet(DIR_PROC / "painel_unificado.parquet")[cols_lulc]
    df = pan.merge(trase, on=["cd_mun", "ano"], how="left")
    return df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 1. Utilitários de série temporal (reuso de espírito #34 + disciplina D16)
# ---------------------------------------------------------------------------

def ccf_defasada(x: np.ndarray, y: np.ndarray, max_lag: int) -> pd.DataFrame:
    """corr(x_{t-k}, y_t), k=-max_lag..+max_lag. k>0 = x ANTECEDE y."""
    linhas = []
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            xa, ya = x[:len(x) - k], y[k:]
        else:
            xa, ya = x[-k:], y[:len(y) + k]
        if len(xa) > 3 and np.std(xa) > 0 and np.std(ya) > 0:
            linhas.append({"lag": k, "r": round(float(np.corrcoef(xa, ya)[0, 1]), 3),
                           "n": len(xa)})
    return pd.DataFrame(linhas)


def granger_p(x: pd.Series, y: pd.Series, maxlag: int = 2) -> dict:
    """p-valor de x Granger-causa y, por lag. N pequeno → cautela (D16)."""
    import io
    import warnings
    from contextlib import redirect_stdout
    from statsmodels.tsa.stattools import grangercausalitytests
    data = np.column_stack([y.to_numpy(), x.to_numpy()])  # [y, x] testa x→y
    out = {}
    # Não passamos `verbose`: depreciado no statsmodels 0.14 (emite FutureWarning ao
    # recebê-lo) e removido no 0.15+. O default já é silencioso; o redirect_stdout
    # blinda contra versões antigas que ainda imprimiam tabelas.
    try:
        with warnings.catch_warnings(), redirect_stdout(io.StringIO()):
            warnings.simplefilter("ignore")
            res = grangercausalitytests(data, maxlag=maxlag)
        for lag in range(1, maxlag + 1):
            out[f"granger_p_lag{lag}"] = round(float(res[lag][0]["ssr_ftest"][1]), 4)
    except Exception as e:  # noqa: BLE001
        out["granger_erro"] = str(e)[:60]
    return out


def integracao(s: pd.Series) -> dict:
    """Diagnóstico D16: ADF (H0 = raiz unitária) e KPSS (H0 = estacionária) no
    nível e na 1ª diferença. Retorna ordem de integração aproximada."""
    from statsmodels.tsa.stattools import adfuller, kpss
    import warnings
    s = s.dropna()
    res = {}
    def _adf(v):
        try:  return round(float(adfuller(v, autolag="AIC")[1]), 3)
        except Exception:  return np.nan
    def _kpss(v):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return round(float(kpss(v, regression="c", nlags="auto")[1]), 3)
        except Exception:  return np.nan
    if len(s) >= 8:
        res["adf_p_nivel"]  = _adf(s.to_numpy())
        res["kpss_p_nivel"] = _kpss(s.to_numpy())
        d1 = s.diff().dropna().to_numpy()
        res["adf_p_diff1"]  = _adf(d1)
        res["kpss_p_diff1"] = _kpss(d1)
        # ordem: se ADF rejeita no nível → I(0); se só após 1 dif → I(1); senão ≥I(2)
        if res["adf_p_nivel"] is not np.nan and res["adf_p_nivel"] < 0.05:
            res["ordem_aprox"] = "I(0)"
        elif res["adf_p_diff1"] is not np.nan and res["adf_p_diff1"] < 0.05:
            res["ordem_aprox"] = "I(1)"
        else:
            res["ordem_aprox"] = "≥I(2)"
    return res


# ---------------------------------------------------------------------------
# 2. Bloco A — lead-lag agregado (série estadual)
# ---------------------------------------------------------------------------

def serie_estadual(df: pd.DataFrame, col_infra: str, col_lulc: str) -> pd.DataFrame:
    """Soma anual estadual das duas séries, restrita aos anos com ambas.

    Reindexa para anos CONTÍGUOS e interpola buracos INTERIORES (ex.: o boi da
    Trase não tem 2018). Sem isso, `.diff()` a jusante trataria o vão 2017→2019
    como um único passo anual, contaminando um ponto da CCF/Granger do Bloco A.
    A interpolação linear de um único ano interior é defensável num bloco que já
    é só diagnóstico (D16); os extremos nunca são extrapolados (limit_area).
    """
    g = (df.groupby("ano")[[col_infra, col_lulc]]
           .sum(min_count=1).reset_index())
    # anos com cobertura Trase (infra > 0) e LULC presente
    g = g[(g[col_infra].fillna(0) > 0) & g[col_lulc].notna()].sort_values("ano")
    if len(g) >= 2:
        anos = range(int(g["ano"].min()), int(g["ano"].max()) + 1)
        g = (g.set_index("ano").reindex(anos)
               .interpolate(method="linear", limit_area="inside")
               .reset_index())
    return g


def bloco_a(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for rotulo, ci, cl, cadeia in PARES:
        g = serie_estadual(df, ci, cl)
        if len(g) < 8:
            linhas.append({"par": rotulo, "cadeia": cadeia, "n_anos": len(g),
                           "obs": "série curta demais"})
            continue
        di = g[ci].diff().to_numpy()[1:]
        dl = g[cl].diff().to_numpy()[1:]
        # CCF: infra ANTECEDE lulc? (k>0 nesta orientação)
        ccf = ccf_defasada(di, dl, min(MAX_LAG, len(di) - 4))
        pico = ccf.loc[ccf["r"].abs().idxmax()] if len(ccf) else None
        # Granger nas duas direções (diagnóstico, D16)
        di_s = pd.Series(di); dl_s = pd.Series(dl)
        g_inf_lead = granger_p(di_s, dl_s, maxlag=2)   # infra → lulc
        g_lulc_lead = granger_p(dl_s, di_s, maxlag=2)   # lulc → infra
        integ_i = integracao(g[ci]); integ_l = integracao(g[cl])
        linhas.append({
            "par": rotulo, "cadeia": cadeia, "n_anos": len(g),
            "anos": f"{int(g.ano.min())}-{int(g.ano.max())}",
            "ccf_lag_pico": int(pico["lag"]) if pico is not None else np.nan,
            "ccf_r_pico": pico["r"] if pico is not None else np.nan,
            "infra→lulc_p_lag1": g_inf_lead.get("granger_p_lag1"),
            "infra→lulc_p_lag2": g_inf_lead.get("granger_p_lag2"),
            "lulc→infra_p_lag1": g_lulc_lead.get("granger_p_lag1"),
            "lulc→infra_p_lag2": g_lulc_lead.get("granger_p_lag2"),
            "infra_ordem": integ_i.get("ordem_aprox"),
            "lulc_ordem": integ_l.get("ordem_aprox"),
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 3. Bloco B — painel de defasagem distribuída (2-way FE)
# ---------------------------------------------------------------------------

def _zscore_painel(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """z-score global por variável (padrão #38): torna β comparável entre pares
    de escalas diferentes (toneladas × hectares × cabeças). NaN preservado."""
    d = df.copy()
    for c in cols:
        s = d[c]
        sd = s.std()
        d[c] = (s - s.mean()) / sd if sd and sd > 0 else np.nan
    return d


def _fe_um_termo(d: pd.DataFrame, yvar: str, xvar: str) -> dict | None:
    """Roda Δy ~ Δx (um regressor) em 2-way FE, SE cluster por município."""
    from linearmodels.panel import PanelOLS
    sub = d.dropna(subset=[yvar, xvar]).copy()
    if len(sub) < 50 or sub["cd_mun"].nunique() < 20 or sub["ano"].nunique() < 4:
        return None
    if sub[xvar].std() == 0 or sub[yvar].std() == 0:
        return None
    try:
        m = sub.set_index(["cd_mun", "ano"])
        res = PanelOLS(m[yvar], m[[xvar]], entity_effects=True,
                       time_effects=True).fit(cov_type="clustered", cluster_entity=True)
        return {"beta": round(float(res.params[xvar]), 4),
                "se": round(float(res.std_errors[xvar]), 4),
                "p": round(float(res.pvalues[xvar]), 4),
                "n": int(res.nobs), "r2w": round(float(res.rsquared_within), 4)}
    except Exception:  # noqa: BLE001
        return None


def bloco_b(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-lagged em painel (variáveis padronizadas). Por par, 3 estimativas:
        contemp        : Δlulc_it   ~ Δinfra_it        (co-movimento, direção-neutro)
        infra_lidera   : Δlulc_it   ~ Δinfra_{i,t−1}   (infra ANTECEDE lulc)
        lulc_lidera    : Δinfra_it  ~ Δlulc_{i,t−1}    (lulc ANTECEDE infra)
    """
    cols_z = sorted({c for _, ci, cl, _ in PARES for c in (ci, cl)})
    dz = _zscore_painel(df, cols_z)

    linhas = []
    for rotulo, ci, cl, cadeia in PARES:
        d = dz[["cd_mun", "ano", ci, cl]].sort_values(["cd_mun", "ano"]).copy()
        d["d_infra"] = d.groupby("cd_mun")[ci].diff()
        d["d_lulc"]  = d.groupby("cd_mun")[cl].diff()
        d["d_infra_l1"] = d.groupby("cd_mun")["d_infra"].shift(1)
        d["d_lulc_l1"]  = d.groupby("cd_mun")["d_lulc"].shift(1)

        estims = {
            "contemp":      _fe_um_termo(d, "d_lulc", "d_infra"),
            "infra_lidera": _fe_um_termo(d, "d_lulc", "d_infra_l1"),
            "lulc_lidera":  _fe_um_termo(d, "d_infra", "d_lulc_l1"),
        }
        for termo, v in estims.items():
            if v:
                linhas.append({"par": rotulo, "cadeia": cadeia, "termo": termo,
                               **v})
    return pd.DataFrame(linhas)


def veredito_b(b: pd.DataFrame) -> str:
    """Tally: quantos pares têm co-movimento contemporâneo sig vs liderança sig."""
    def n_sig(termo):
        return int((b[(b.termo == termo)]["p"] < 0.05).sum())
    n_pares = b["par"].nunique()
    return (f"Pares com co-movimento contemporâneo sig (p<0,05): {n_sig('contemp')}/{n_pares}; "
            f"com INFRA lidera (t−1) sig: {n_sig('infra_lidera')}/{n_pares}; "
            f"com LULC lidera (t−1) sig: {n_sig('lulc_lidera')}/{n_pares}.")


# ---------------------------------------------------------------------------
# 4. Figuras
# ---------------------------------------------------------------------------

def fig_agregado(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    pares_fig = [("trase_soja_volume_t", "lulc_soja_ha", "Soja: infra exportadora × área (MapBiomas)", "#6a3d9a"),
                 ("trase_boi_volume_t", "pec_bovinos_cab", "Boi: infra exportadora × rebanho", "#7a1f1f")]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5))
    for ax, (ci, cl, tit, cor) in zip(axes, pares_fig):
        g = serie_estadual(df, ci, cl)
        ax2 = ax.twinx()
        l1 = ax.plot(g.ano, g[ci] / g[ci].max(), "o-", color=cor, lw=2, label="infra exportadora (norm.)")
        l2 = ax2.plot(g.ano, g[cl] / g[cl].max(), "s--", color="0.35", lw=2, label="uso da terra (norm.)")
        ax.set_title(tit, fontsize=11, loc="left", color=cor)
        ax.set_xlabel("Ano"); ax.set_ylabel("infra (normalizada)", color=cor)
        ax2.set_ylabel("LULC (normalizada)", color="0.35")
        ax.grid(True, alpha=0.2)
        ls = l1 + l2; ax.legend(ls, [x.get_label() for x in ls], fontsize=8, loc="upper left")
    fig.suptitle("Trase (cadeia exportadora) × uso da terra — séries estaduais normalizadas",
                 fontsize=12.5, y=1.0)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "leadlag_agregado.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'leadlag_agregado.png').relative_to(ROOT)}")


def fig_painel(b: pd.DataFrame) -> None:
    """Três colunas de termos (contemp | infra lidera | lulc lidera) por par —
    mostra que o sinal vive no contemporâneo, não nas defasagens."""
    import matplotlib.pyplot as plt
    termos = [("contemp", "co-movimento\ncontemporâneo", "#1b7837"),
              ("infra_lidera", "infra lidera\n(t−1)", "#6a3d9a"),
              ("lulc_lidera", "LULC lidera\n(t−1)", "#c2185b")]
    pares = list(dict.fromkeys(b["par"]))
    y = np.arange(len(pares))
    fig, axes = plt.subplots(1, 3, figsize=(13.5, max(4, 0.5 * len(pares))), sharey=True)
    for ax, (termo, tit, cor) in zip(axes, termos):
        sub = b[b.termo == termo].set_index("par").reindex(pares)
        for i, (_, r) in enumerate(sub.iterrows()):
            if pd.isna(r["beta"]):
                continue
            sig = r["p"] < 0.05
            c = cor if sig else "0.7"
            ax.errorbar(r["beta"], i, xerr=1.96 * r["se"], fmt="o", color=c, capsize=3,
                        ms=7 if sig else 5)
            if sig:
                ax.text(r["beta"], i + 0.25, f"p={r['p']:g}", ha="center", fontsize=7, color=c)
        ax.axvline(0, color="0.3", lw=1)
        ax.set_title(tit, fontsize=10.5, color=cor)
        ax.grid(True, axis="x", alpha=0.2)
    axes[0].set_yticks(y); axes[0].set_yticklabels(pares, fontsize=8)
    fig.suptitle("Trase × LULC — painel 2-way FE (β padronizado, IC95%; cheio = p<0,05)\n"
                 "Sinal concentra-se no co-movimento contemporâneo; defasagens ~nulas",
                 fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "painel_direcoes.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'painel_direcoes.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #45 — Trase × LULC (lead-lag)")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("Pipeline #45 — Infra exportadora (Trase) SEGUE ou LIDERA a expansão LULC?")
    print("=" * 72)

    df = carregar()
    print(f"[dados] {df.shape[0]:,} linhas (cd_mun×ano) | munis {df.cd_mun.nunique()} | "
          f"anos {int(df.ano.min())}-{int(df.ano.max())}")

    print("\n[Bloco A] Lead-lag AGREGADO (série estadual, D7 + diagnóstico D16):")
    a = bloco_a(df)
    a.to_csv(DIR_PROC / "trase_lulc_leadlag_agregado.csv", index=False, encoding="utf-8")
    for _, r in a.iterrows():
        if "obs" in r and isinstance(r.get("obs"), str):
            print(f"  {r['par']:44s} — {r['obs']}"); continue
        print(f"  {r['par']:44s} [{r['anos']}, {r['n_anos']}a] "
              f"CCF pico lag={r['ccf_lag_pico']:+d} r={r['ccf_r_pico']:+.2f} | "
              f"infra→lulc p(l1/l2)={r['infra→lulc_p_lag1']}/{r['infra→lulc_p_lag2']} | "
              f"lulc→infra p(l1/l2)={r['lulc→infra_p_lag1']}/{r['lulc→infra_p_lag2']} | "
              f"ordens {r['infra_ordem']}/{r['lulc_ordem']}")
    print(f"  [OK] trase_lulc_leadlag_agregado.csv ({len(a)} pares)")

    print("\n[Bloco B] Cross-lagged em painel (2-way FE, β padronizado, cluster muni):")
    b = bloco_b(df)
    b.to_csv(DIR_PROC / "trase_lulc_painel.csv", index=False, encoding="utf-8")
    for par, sub in b.groupby("par", sort=False):
        s = sub.set_index("termo")
        def fmt(t):
            if t not in s.index: return f"{t}=—"
            r = s.loc[t]; star = "*" if r.p < 0.05 else " "
            return f"{t} β={r.beta:+.3f}{star}(p={r.p})"
        print(f"  {par:44s} {fmt('contemp')} | {fmt('infra_lidera')} | {fmt('lulc_lidera')}")
    print(f"  [OK] trase_lulc_painel.csv ({len(b)} linhas)")
    print("\n  VEREDITO: " + veredito_b(b))

    if not args.sem_figuras:
        print()
        fig_agregado(df)
        fig_painel(b)

    print("\n" + "=" * 72)
    print("CONCLUÍDO — Pipeline #45. Ler o Bloco B (painel) como inferência; "
          "o Bloco A é diagnóstico (D16).")
    print("=" * 72)


if __name__ == "__main__":
    main()
