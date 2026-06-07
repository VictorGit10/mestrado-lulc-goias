"""drive_comum_amc.py -- Pipeline #38: o "drive comum" no painel AMC (driver x exposicao)
============================================================================================

PERGUNTA QUE RESPONDE
---------------------
O #37 testou o "drive comum" na serie UF/anual e esbarrou no teto de N (~38 anos):
os hits (~7 em ~135 testes) nao sobrevivem a multiplicidade; so o CAMBIO real tem
estrutura, por reaparecer em duas margens. Este pipeline NAO repete o erro de
espremer mais da serie agregada -- ele MUDA A UNIDADE DE ANALISE para o painel AMC
(166 AMCs x ~38 anos ~ 6.000 obs) e, com isso, a ESTRATEGIA DE IDENTIFICACAO.

O driver e nacional (mesmo numero para as 166 AMCs num dado ano), entao NAO se
testa "o driver mexe o LULC?" (isso o #37 ja fez, mal). Testa-se:

    O MESMO choque comum bate MAIS FORTE onde a EXPOSICAO e maior?

ABORDAGEM (interacao driver x exposicao, 2-way FE)
--------------------------------------------------
    Delta y_it = alpha_i + gamma_t + beta * (Delta driver_t x exposicao_i) + e_it

  - alpha_i (efeito fixo de AMC): absorve tudo fixo do lugar (aptidao de solo,
    distancia, estrutura fundiaria) -> absorve o efeito principal de exposicao_i.
  - gamma_t (efeito fixo de ano): absorve TODO choque nacional do ano -> absorve
    o efeito principal de Delta driver_t (cambio, clima, politica nacional).
  - beta (interacao): sobrevive aos dois (driver varia so no tempo, exposicao so
    no espaco -> o produto varia em espaco x tempo). E o "gradiente de aptidao"
    que o #34/#37 AFIRMAM mas a serie UF nao sustenta.

  SE com CLUSTERIZACAO DUPLA (entidade + ano): o driver e um choque comum, entao
  os residuos sao correlacionados DENTRO de cada ano; clusterizar so por AMC
  subestima o erro-padrao. Two-way clustering e o ajuste honesto.

  TRADE-OFF (explicito): o efeito fixo de ANO absorve o efeito MEDIO do driver
  (colinear com o ano). Logo este desenho estima o GRADIENTE ("responde mais onde
  a exposicao manda") com alto poder -- NAO o nivel medio "1pt de cambio -> X Mha".
  O nivel medio e o que o #37 (UF/anual) tentava; os dois sao complementares.

DISCIPLINA DE MULTIPLICIDADE (licao do #37)
-------------------------------------------
  - CONFIRMATORIO TEORICO: conjunto de ~4 interacoes selecionadas POR TEORIA, com
    direcao esperada. NAO e pre-registro temporal (escrito no mesmo dia da analise) --
    o credito vem da hipotese estar declarada antes, nao de precedencia cronologica.
  - EXPLORATORIO: grade completa (driver x exposicao x classe x lag 0/1/2), reportada
    a parte e com correcao FDR (Benjamini-Hochberg). Sem cherry-picking de p<0,05 nem
    de lag. NOTA: o resultado do FDR e sensivel ao tamanho da familia -- incluir o
    lag 2 (onde o #37 achava sinal) derrubou o unico sobrevivente da grade de 96.

CONVENCAO (Decisao D7): drivers em PRIMEIRAS DIFERENCAS (como no #37). Exposicao e
BASELINE (media 1985-1989), TIME-INVARIANT e predeterminada -> nao contaminada pelo
desfecho. Driver e exposicao entram PADRONIZADOS (z-score), entao beta = resposta
(em Mha / mil cab) a um choque conjunto de +1 DP no driver e +1 DP na exposicao.

ENTRADAS
    data/processed/taxas_lulc_amc.csv          (#36/AMC: deltas + shares por AMC-ano)
    data/processed/painel_amc_goias.parquet    (#25: pec_bovinos_cab para o rebanho)
    data/processed/drivers_macro_anual.csv     (#37A: drivers macro nacionais)

SAIDAS
    data/processed/drive_amc_confirmatorio.csv  (4 interacoes pre-registradas, lags 0/1)
    data/processed/drive_amc_exploratorio.csv   (grade completa + FDR)
    outputs/drive_comum_amc/interacoes_confirmatorias.png
    outputs/drive_comum_amc/grade_exploratoria.png

COMO RODAR
    python scripts/drive_comum_amc.py
    python scripts/drive_comum_amc.py --sem-figuras

Depende de: #37A (drivers), #25 (painel AMC), taxas_lulc_amc. Reusa o padrao
PanelOLS 2FE de correlacoes_painel.py (D8). Quando foi feito: 2026-06-06.
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
DIR_OUT  = ROOT / "outputs" / "drive_comum_amc"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# ─────────────────────────── Config ───────────────────────────

BASELINE = (1985, 1989)   # janela para exposicao predeterminada (time-invariant)
# O conjunto confirmatorio (pre-registrado) testa contemporaneo / lidera-1-ano. A grade
# exploratoria inclui lag 2 porque o sinal do #37 (cambio->pastagem) estava no lag 2 --
# sem isso o "nulo de area" do #38 ficava por nao ter testado o lag onde o efeito apareceria.
LAGS_CONF = [0, 1]        # lags do conjunto confirmatorio
LAGS_GRID = [0, 1, 2]     # lags da grade exploratoria (FDR aplicado sobre a grade inteira)
LAGS = sorted(set(LAGS_CONF) | set(LAGS_GRID))  # uniao: lags a construir na carga

# Drivers nacionais (em 1as diferencas, z-score sobre os anos). Rotulos p/ figuras.
DRIVERS = {
    "cambio_real_efetivo":     "Câmbio real (REER)",
    "preco_recebido_soja_idx": "Preço recebido soja",
    "preco_boi_usd":           "Preço boi (US$)",
    "credito_rural_go_real":   "Crédito rural GO",
}

# Exposicoes baseline (z-score sobre as 166 AMCs). Coluna-fonte em taxas_lulc_amc.
EXPOSICOES = {
    "exp_apt_agri":  ("agricultura_pct",      "Aptidão agrícola (Sul)"),
    "exp_pasto":     ("pastagem_pct",         "Especialização em pasto"),
    "exp_fronteira": ("vegetacao_natural_pct", "Fronteira (veg. convertível, Norte)"),
}

# Desfechos (taxa de conversao). rebanho vem do painel parquet (Delta bovinos).
# Padronizados (z-score) na carga -> beta comparavel entre classes; ver carregar().
OUTCOMES = {
    "vegetacao_natural_delta_mha": "Δ Veg. natural",
    "pastagem_delta_mha":          "Δ Pastagem",
    "agricultura_delta_mha":       "Δ Agricultura",
    "d_bovinos_mcab":              "Δ Rebanho",
}

# CONJUNTO CONFIRMATORIO TEORICO (selecionado por teoria, nao pre-registro temporal):
# (driver, exposicao, desfecho, sinal_esperado, hipotese)
CONFIRMATORIO = [
    ("cambio_real_efetivo",     "exp_fronteira", "d_bovinos_mcab",        "+",
     "Depreciação impulsiona o rebanho MAIS na fronteira (headroom) — versão AMC da ponte #37."),
    ("cambio_real_efetivo",     "exp_fronteira", "pastagem_delta_mha",    "+",
     "Depreciação expande pasto MAIS onde há veg. convertível (avanço de fronteira no Norte)."),
    ("preco_recebido_soja_idx", "exp_apt_agri",  "agricultura_delta_mha", "+",
     "Boom de preço converte MAIS para agricultura onde a aptidão agrícola é alta (Sul)."),
    ("preco_recebido_soja_idx", "exp_pasto",     "pastagem_delta_mha",    "-",
     "Boom de preço retrai pasto MAIS onde o pasto é abundante (substituição pasto→soja)."),
]


# ─────────────────────────── Carga ───────────────────────────

def _zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def carregar() -> pd.DataFrame:
    tx = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")

    # 1) Exposicao baseline (media 1985-1989 por AMC), z-score sobre as AMCs
    base = tx[(tx["ano"] >= BASELINE[0]) & (tx["ano"] <= BASELINE[1])]
    expo = base.groupby("code_amc").agg(
        agricultura_pct=("agricultura_pct", "mean"),
        pastagem_pct=("pastagem_pct", "mean"),
        vegetacao_natural_pct=("vegetacao_natural_pct", "mean"),
    ).reset_index()
    for ecol, (src, _rot) in EXPOSICOES.items():
        expo[ecol] = _zscore(expo[src])
    expo = expo[["code_amc", *EXPOSICOES.keys()]]

    # 2) Rebanho: Delta bovinos (mil cab) por AMC, do painel unificado
    pan = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet",
                          columns=["code_amc", "ano", "pec_bovinos_cab"])
    pan = pan.sort_values(["code_amc", "ano"])
    pan["d_bovinos_mcab"] = pan.groupby("code_amc")["pec_bovinos_cab"].diff() / 1e3

    # 3) Painel base: taxas LULC + exposicao + rebanho
    keep = ["code_amc", "ano", *OUTCOMES.keys()]
    keep = [c for c in keep if c in tx.columns]
    df = tx[keep].merge(pan[["code_amc", "ano", "d_bovinos_mcab"]], on=["code_amc", "ano"], how="left")
    df = df.merge(expo, on="code_amc", how="left")

    # 4) Drivers nacionais: 1as diferencas, z-score sobre os anos, defasados; merge por ano
    drv = pd.read_csv(DIR_PROC / "drivers_macro_anual.csv").sort_values("ano").set_index("ano")
    annual = pd.DataFrame(index=drv.index)
    for d in DRIVERS:
        zd = _zscore(drv[d].diff())
        for lag in LAGS:
            annual[f"zd_{d}_l{lag}"] = zd.shift(lag)
    df = df.merge(annual.reset_index(), on="ano", how="left")

    # 5) Termos de interacao: zd_driver_lag x exposicao_z
    for d in DRIVERS:
        for e in EXPOSICOES:
            for lag in LAGS:
                df[f"ix__{d}__{e}__l{lag}"] = df[f"zd_{d}_l{lag}"] * df[e]

    # 6) Padroniza desfechos (z-score). p/t sao invariantes a escala -> isto so
    #    torna o beta legivel e COMPARAVEL entre classes (as taxas em Mha por AMC
    #    sao minusculas; sem isto o beta sai como 0,0000).
    for y in OUTCOMES:
        if y in df.columns:
            df[y] = _zscore(df[y])

    return df.sort_values(["code_amc", "ano"]).reset_index(drop=True)


# ─────────────────────────── Regressao de interacao ───────────────────────────

def rodar_interacao(df: pd.DataFrame, y: str, ix: str) -> dict | None:
    """PanelOLS 2FE com um termo de interacao.

    SE primario = clusterizacao DUPLA (entidade + ano), pois o driver e um choque
    comum (residuos correlacionados dentro do ano). A vcov two-way NAO e garantida
    PSD (propriedade conhecida): quando da variancia negativa (SE = NaN), cai para
    clusterizacao por entidade e marca o fallback no campo 'cluster'.
    """
    from linearmodels.panel import PanelOLS

    sub = df[["code_amc", "ano", y, ix]].dropna()
    if sub["code_amc"].nunique() < 30 or len(sub) < 200:
        return None
    sub = sub.set_index(["code_amc", "ano"])
    try:
        mod = PanelOLS(sub[y], sub[[ix]], entity_effects=True, time_effects=True,
                       check_rank=False)
        res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        cluster = "entidade+ano"
        if not np.isfinite(res.std_errors[ix]):           # two-way nao-PSD -> fallback
            res = mod.fit(cov_type="clustered", cluster_entity=True)
            cluster = "entidade (fallback)"
        ci = res.conf_int().loc[ix]
        return {
            "beta": float(res.params[ix]), "se": float(res.std_errors[ix]),
            "t": float(res.tstats[ix]), "p": float(res.pvalues[ix]),
            "ci_lo": float(ci["lower"]), "ci_hi": float(ci["upper"]),
            "n_obs": int(res.nobs), "n_amc": int(sub.index.get_level_values(0).nunique()),
            "r2_within": float(res.rsquared_within), "cluster": cluster,
        }
    except Exception as e:  # rank/singularidade
        return {"erro": str(e)[:100]}


# ─────────────────────────── 1. Confirmatorio (pre-registrado) ───────────────────────────

def confirmatorio(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for d, e, y, sinal, hip in CONFIRMATORIO:
        for lag in LAGS_CONF:
            ix = f"ix__{d}__{e}__l{lag}"
            r = rodar_interacao(df, y, ix)
            if r is None or "erro" in r:
                continue
            ok = (np.sign(r["beta"]) == (1 if sinal == "+" else -1)) and r["p"] < 0.05
            linhas.append({
                "driver": d, "driver_rotulo": DRIVERS[d],
                "exposicao": e, "exposicao_rotulo": EXPOSICOES[e][1],
                "desfecho": y, "desfecho_rotulo": OUTCOMES[y],
                "lag": lag, "sinal_esperado": sinal,
                **{k: round(v, 5) if isinstance(v, float) else v for k, v in r.items()},
                "confirma": bool(ok), "hipotese": hip,
            })
    return pd.DataFrame(linhas)


# ─────────────────────────── 2. Exploratorio (grade + FDR) ───────────────────────────

def exploratorio(df: pd.DataFrame) -> pd.DataFrame:
    from statsmodels.stats.multitest import multipletests
    linhas = []
    for d in DRIVERS:
        for e in EXPOSICOES:
            for y in OUTCOMES:
                for lag in LAGS_GRID:
                    ix = f"ix__{d}__{e}__l{lag}"
                    r = rodar_interacao(df, y, ix)
                    if r is None or "erro" in r:
                        continue
                    linhas.append({
                        "driver": d, "exposicao": e, "desfecho": y, "lag": lag,
                        **{k: round(v, 5) if isinstance(v, float) else v for k, v in r.items()},
                    })
    out = pd.DataFrame(linhas)
    if not out.empty:
        out["p_fdr"] = np.nan
        out["sig_fdr"] = False
        valid = out["p"].notna()
        if valid.any():
            rej, p_fdr, _, _ = multipletests(out.loc[valid, "p"].to_numpy(),
                                             alpha=0.05, method="fdr_bh")
            out.loc[valid, "p_fdr"] = np.round(p_fdr, 5)
            out.loc[valid, "sig_fdr"] = rej
    return out


# ─────────────────────────── Figuras ───────────────────────────

def fig_confirmatorio(conf: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    conf = conf.dropna(subset=["p"])
    if conf.empty:
        return
    # melhor lag por hipotese (menor p)
    best = conf.loc[conf.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()].reset_index(drop=True)
    best = best.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 0.9 * len(best) + 2))
    for i, r in best.iterrows():
        cor = "#1b7837" if (r["confirma"]) else ("#762a83" if r["p"] < 0.05 else "#999999")
        ax.errorbar(r["beta"], i, xerr=[[r["beta"] - r["ci_lo"]], [r["ci_hi"] - r["beta"]]],
                    fmt="o", color=cor, capsize=4, lw=2, ms=8)
        rot = (f"{r['driver_rotulo']} × {r['exposicao_rotulo']}\n→ {r['desfecho_rotulo']} "
               f"(lag {int(r['lag'])}; esperado {r['sinal_esperado']})")
        ax.annotate(rot, (r["ci_lo"], i), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=8)
        ax.annotate(f"p={r['p']:.3f}", (r["ci_hi"], i), xytext=(8, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8, color=cor)
    ax.axvline(0, color="0.4", lw=1, ls="--")
    ax.set_yticks([])
    ax.set_xlabel("β padronizado (DP do desfecho por +1 DP de driver × +1 DP de exposição)")
    ax.set_title("Interações confirmatórias (pré-registradas): driver × exposição no painel AMC\n"
                 "verde = confirma direção e p<0,05; roxo = p<0,05 sinal inesperado; cinza = NS",
                 fontsize=11, fontweight="bold")
    ax.margins(x=0.35)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "interacoes_confirmatorias.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'interacoes_confirmatorias.png').relative_to(ROOT)}")


def fig_exploratorio(expl: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    expl = expl.dropna(subset=["p"])
    if expl.empty:
        return
    # heatmap de t-stat: linhas = driver×exposicao, colunas = desfecho (melhor lag por celula)
    g = expl.loc[expl.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()]
    g["linha"] = g["driver"].map(lambda d: DRIVERS[d]) + " × " + g["exposicao"].map(lambda e: EXPOSICOES[e][1])
    piv = g.pivot(index="linha", columns="desfecho", values="t")
    pfdr = g.pivot(index="linha", columns="desfecho", values="p_fdr")
    cols = [c for c in OUTCOMES if c in piv.columns]
    piv, pfdr = piv[cols], pfdr[cols]

    fig, ax = plt.subplots(figsize=(1.6 * len(cols) + 4, 0.5 * len(piv) + 2))
    vmax = np.nanmax(np.abs(piv.to_numpy()))
    im = ax.imshow(piv.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)), [OUTCOMES[c] for c in cols], rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(piv)), piv.index, fontsize=8)
    for i in range(len(piv)):
        for j in range(len(cols)):
            t = piv.to_numpy()[i, j]
            mark = "✚" if pfdr.to_numpy()[i, j] < 0.05 else ""
            if not np.isnan(t):
                ax.text(j, i, f"{t:.1f}{mark}", ha="center", va="center", fontsize=7,
                        color="white" if abs(t) > vmax * 0.6 else "black")
    fig.colorbar(im, ax=ax, label="t-stat da interação", shrink=0.7)
    ax.set_title("Grade exploratória: t-stat das interações (✚ = sobrevive FDR-BH)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "grade_exploratoria.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'grade_exploratoria.png').relative_to(ROOT)}")


# ─────────────────────────── Main ───────────────────────────

def main(sem_figuras: bool = False) -> None:
    df = carregar()
    n_amc, n_anos = df["code_amc"].nunique(), df["ano"].nunique()
    print(f"[carga] {len(df):,} obs ({n_amc} AMCs × {n_anos} anos); "
          f"exposições baseline {BASELINE[0]}-{BASELINE[1]} (z-score)\n")

    conf = confirmatorio(df)
    conf.to_csv(DIR_PROC / "drive_amc_confirmatorio.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_amc_confirmatorio.csv ({len(conf)} linhas)")

    expl = exploratorio(df)
    expl.to_csv(DIR_PROC / "drive_amc_exploratorio.csv", index=False, encoding="utf-8")
    print(f"[OK] drive_amc_exploratorio.csv ({len(expl)} linhas)\n")

    # ── Resumo confirmatorio ──
    print("[confirmatório] interações confirmatórias teóricas (melhor lag por hipótese):")
    if not conf.empty:
        best = conf.loc[conf.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()]
        for _, r in best.iterrows():
            flag = "  ✔ CONFIRMA" if r["confirma"] else ("  (p<.05 sinal inesperado)" if r["p"] < 0.05 else "")
            print(f"  {r['driver_rotulo']:20s} × {r['exposicao_rotulo']:34s} → {r['desfecho_rotulo']:20s} "
                  f"lag{int(r['lag'])}: β={r['beta']:+.4f} p={r['p']:.3f} (esp.{r['sinal_esperado']}, N={r['n_obs']:,}){flag}")

    # ── Resumo exploratorio ──
    print("\n[exploratório] interações que sobrevivem ao FDR-BH (α=0,05):")
    if not expl.empty:
        sig = expl[expl["sig_fdr"]].sort_values("p")
        if len(sig):
            for _, r in sig.iterrows():
                print(f"  {DRIVERS[r['driver']]:20s} × {EXPOSICOES[r['exposicao']][1]:34s} → "
                      f"{OUTCOMES[r['desfecho']]:20s} lag{int(r['lag'])}: "
                      f"β={r['beta']:+.4f} t={r['t']:+.2f} p={r['p']:.4f} p_fdr={r['p_fdr']:.4f}")
        else:
            print("  Nenhuma sobrevive ao FDR.")
        n_bruto = int((expl["p"] < 0.05).sum())
        print(f"\n  ({n_bruto} de {len(expl)} interações com p<0,05 brutos; "
              f"{int(expl['sig_fdr'].sum())} sobrevivem ao FDR)")

    if not sem_figuras:
        print()
        fig_confirmatorio(conf)
        fig_exploratorio(expl)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Drive comum no painel AMC: driver × exposição (#38)")
    p.add_argument("--sem-figuras", action="store_true", help="pula a geração de PNGs")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        main(sem_figuras=args.sem_figuras)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
