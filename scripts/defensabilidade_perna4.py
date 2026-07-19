"""defensabilidade_perna4.py -- Pipeline #54: endurecimento shift-share do DRIVE COMUM
====================================================================================

NOTA DE ESTRUTURA (jul/2026): o resultado deste pipeline motivou a fusão da antiga
"perna 4" (o drive comum) com a antiga perna 3 -> o drive comum virou o POSITIVO da
Perna 3 ("reorganização coordenada, não deslocamento") e o teto de oferta virou a
Perna 4. O nome do arquivo é mantido como handle. Onde se lê "perna 4" abaixo, leia
"o drive comum / o positivo da Perna 3". Ver Textos/indice_logico_pipelines.md.

PERGUNTA QUE RESPONDE
---------------------
O drive comum (choque comum câmbio × gradiente de aptidão -> rebanho de fronteira) é a
metade mais fraca da narrativa. O #38/#52 mostraram que o teto é ESTRUTURAL: o driver (câmbio) é uma
série NACIONAL -- varia só no tempo, ~38 realizações -- então o poder é capado e nenhuma
quantidade de AMCs a mais o levanta (o cluster por ano já reconhece isso). NÃO dá para
"estabelecer" a perna 4 espremendo mais do mesmo dado.

O que DÁ para fazer -- e é o objetivo deste pipeline -- é a opção (B): maximizar a
DEFENSABILIDADE sem dado novo, nomeando o desenho pelo que ele é (um shift-share/Bartik:
"shift" = câmbio nacional, "share" = aptidão local) e rodando a inferência correta para
esse desenho, mais a bateria de especificidade que uma banca julga:

    (1) INFERÊNCIA POR PERMUTAÇÃO (Borusyak-Hull-Jaravel): reembaralhar o SHIFTER
        (o câmbio) entre os anos, mantendo as SHARES (aptidão) fixas, e ver onde o β
        real cai na distribuição nula. NÃO depende da assintótica frágil de ~38 clusters
        -- é a resposta honesta justamente quando o N efetivo é pequeno.
          (a) naive  : permutação livre dos anos (quebra a autocorrelação do câmbio).
          (b) circular: rotação da série (preserva a autocorrelação do shifter macro) --
              exaustiva sobre as T-1 rotações; é a mais defensável para série serial.
    (2) PLACEBOS DE DESFECHO: câmbio × aptidão -> área urbana e -> água devem ser NULOS
        (o efeito é específico do rebanho, não deriva genérica). Urbano é o placebo limpo
        do #44 ("área urbana parada").
    (3) PLACEBO-NO-TEMPO (lead / antecipação): câmbio_{t+1} × aptidão -> rebanho_t deve
        ser NULO -- um choque FUTURO não pode "explicar" a variação presente. Contraste
        com o lag 1 (o achado). Se lead nulo e lag positivo, é especificidade temporal.
    (4) JACKKNIFE ANO-A-ANO (leave-one-year-out): reestima o β dropando cada ano; revela
        se a identificação repousa nas grandes desvalorizações (1999/2002/2015) -- a
        versão HONESTA do "event-study nas desvalorizações" (com ~3 eventos, um event-study
        dinâmico seria subdimensionado; o jackknife anotado pelo tamanho do choque entrega
        a mesma leitura sem superdimensionar).

HEADLINES ENDURECIDOS (os dois ângulos do MESMO achado, lag 1)
--------------------------------------------------------------
    H1 (proxy de área, #38) : câmbio × exp_fronteira   -> Δ rebanho  (esperado +; β≈+0,028)
    H2 (aptidão exógena,#52): câmbio × exp_apt_edafo    -> Δ rebanho  (esperado −; β≈−0,033)
H2 é o headline mais defensável (share físico exógeno, não-complementar). A bateria roda
nos dois.

DESENHO (reuso INTEGRAL do #38/#52 -- não altera nada publicado)
----------------------------------------------------------------
    Δy_it = α_i + γ_t + β·(Δcâmbio_t × exposição_i) + ε_it
Importa `drive_comum_amc` (#38) para montar exposições/interações/z-scores e reusa seu
`rodar_interacao` (PanelOLS 2FE, cluster duplo) para os placebos/lead/jackknife. A
permutação usa um within-transform 2-way próprio (rápido) VALIDADO contra o PanelOLS.

ENTRADAS
    scripts/drive_comum_amc.py            (#38, importado)
    data/processed/aptidao_edafo_amc.csv  (#52: exp_apt_edafo por AMC)
    data/processed/taxas_lulc_amc.csv     (placebos: area_urbana/agua delta)
    + as entradas do #38 (drivers, painel AMC, taxas)

SAÍDAS
    data/processed/perna4_permutacao.csv
    data/processed/perna4_placebos.csv
    data/processed/perna4_jackknife.csv
    outputs/defensabilidade_perna4/bateria.png

COMO RODAR
    py -3.14 scripts/defensabilidade_perna4.py
    py -3.14 scripts/defensabilidade_perna4.py --sem-figuras
    py -3.14 scripts/defensabilidade_perna4.py --nperm 2000
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
DIR_OUT  = ROOT / "outputs" / "defensabilidade_perna4"
DIR_OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "scripts"))
import drive_comum_amc as d38   # reuso integral do #38

DRIVER   = "cambio_real_efetivo"
EXPO_EDA = "exp_apt_edafo"
REBANHO  = "d_bovinos_mcab"
LAG_HEAD = 1                    # o achado vive no lag 1

# (rótulo, exposição, sinal esperado, descrição) -- os dois ângulos do mesmo achado
HEADLINES = [
    ("H1 proxy de área (#38)",  "exp_fronteira", "+",
     "câmbio × fronteira (% veg baseline) → rebanho: depreciação cresce o rebanho MAIS na fronteira."),
    ("H2 aptidão exógena (#52)", EXPO_EDA,       "-",
     "câmbio × aptidão física exógena → rebanho: depreciação cresce o rebanho MAIS onde a aptidão é BAIXA."),
]

# placebos de desfecho (esperado NULO). z-score na carga.
PLACEBO_OUT = {
    "urbano_z": ("area_urbana_delta_mha", "Δ Área urbana (placebo)"),
    "agua_z":   ("agua_delta_mha",        "Δ Água (placebo)"),
}


# ─────────────────────────── Carga estendida ───────────────────────────

def _z(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def carregar_estendido() -> pd.DataFrame:
    """df do #38 (3 exposições + interações + outcomes z) + exp_apt_edafo (#52),
    + placebos de desfecho (urbano/água z) + interações de LEAD do câmbio."""
    df = d38.carregar()

    # exposição exógena do #52 + suas interações (todos os lags do #38)
    apt = pd.read_csv(DIR_PROC / "aptidao_edafo_amc.csv")[["code_amc", EXPO_EDA]]
    apt["code_amc"] = apt["code_amc"].astype(df["code_amc"].dtype)
    df = df.merge(apt, on="code_amc", how="left")
    for lag in d38.LAGS:
        df[f"ix__{DRIVER}__{EXPO_EDA}__l{lag}"] = df[f"zd_{DRIVER}_l{lag}"] * df[EXPO_EDA]

    # placebos de desfecho (z-score, como os outcomes do #38)
    tx = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv",
                     usecols=["code_amc", "ano", "area_urbana_delta_mha", "agua_delta_mha"])
    df = df.merge(tx, on=["code_amc", "ano"], how="left")
    df["urbano_z"] = _z(df["area_urbana_delta_mha"])
    df["agua_z"]   = _z(df["agua_delta_mha"])

    # LEAD do câmbio (choque futuro): s0 por ano deslocado -1/-2 -> interações
    s0 = (df.dropna(subset=[f"zd_{DRIVER}_l0"])
            .groupby("ano")[f"zd_{DRIVER}_l0"].first().sort_index())
    for k in (1, 2):
        lead = s0.shift(-k)                       # valor de t+k atribuído ao ano t
        df[f"zd_{DRIVER}_lead{k}"] = df["ano"].map(lead)
        for e in ("exp_fronteira", EXPO_EDA):
            df[f"ixlead{k}__{e}"] = df[f"zd_{DRIVER}_lead{k}"] * df[e]

    return df


# ─────────────────────────── Within 2-way rápido (p/ permutação) ───────────────────────────

def _demean2way(v, ent, tim, ne, nt, iters: int = 14):
    """Remove iterativamente médias de entidade e de ano (converge ao within 2-way)."""
    v  = v.astype(float).copy()
    ce = np.bincount(ent, minlength=ne).astype(float)
    ct = np.bincount(tim, minlength=nt).astype(float)
    for _ in range(iters):
        me = np.bincount(ent, weights=v, minlength=ne) / ce
        v -= me[ent]
        mt = np.bincount(tim, weights=v, minlength=nt) / ct
        v -= mt[tim]
    return v


def _beta_within(ydd, X, ent, tim, ne, nt):
    Xdd = _demean2way(X, ent, tim, ne, nt)
    den = float(Xdd @ Xdd)
    return float(Xdd @ ydd) / den if den > 0 else np.nan


def permutacao_shifter(df: pd.DataFrame, e: str, nperm: int, seed: int = 20260718) -> dict:
    """Inferência por permutação do SHIFTER (câmbio) mantendo as SHARES (exposição) fixas.
    Retorna β real (within), p naive (nperm shuffles) e p circular (T-1 rotações exaustivas)."""
    zcol = f"zd_{DRIVER}_l{LAG_HEAD}"
    sub = df[["code_amc", "ano", REBANHO, e, zcol]].dropna().copy()

    ent = pd.factorize(sub["code_amc"])[0]
    tim = pd.factorize(sub["ano"])[0]
    ne, nt = int(ent.max() + 1), int(tim.max() + 1)

    ydd = _demean2way(sub[REBANHO].to_numpy(), ent, tim, ne, nt)
    ev  = sub[e].to_numpy()

    # shifter por ano, ORDENADO por ano; índice de ano de cada obs na ordem ordenada
    anos_ord = np.sort(sub["ano"].unique())
    y2i = {a: i for i, a in enumerate(anos_ord)}
    obs_yi = sub["ano"].map(y2i).to_numpy()
    s_ord = sub.groupby("ano")[zcol].first().reindex(anos_ord).to_numpy()
    T = len(anos_ord)

    beta_real = _beta_within(ydd, s_ord[obs_yi] * ev, ent, tim, ne, nt)

    # (a) naive: permuta livre da série anual
    rng = np.random.default_rng(seed)
    betas_naive = np.empty(nperm)
    for b in range(nperm):
        sp = s_ord[rng.permutation(T)]
        betas_naive[b] = _beta_within(ydd, sp[obs_yi] * ev, ent, tim, ne, nt)

    # (b) circular: todas as T-1 rotações não-triviais (exaustivo, preserva autocorrelação)
    betas_circ = np.empty(T - 1)
    for k in range(1, T):
        sp = np.roll(s_ord, k)
        betas_circ[k - 1] = _beta_within(ydd, sp[obs_yi] * ev, ent, tim, ne, nt)

    ar = abs(beta_real)
    p_naive = (1 + int(np.sum(np.abs(betas_naive) >= ar))) / (1 + nperm)
    p_circ  = (1 + int(np.sum(np.abs(betas_circ)  >= ar))) / (1 + len(betas_circ))
    return dict(beta_real=beta_real, T=T, n_obs=len(sub),
                p_naive=p_naive, p_circ=p_circ,
                betas_naive=betas_naive, betas_circ=betas_circ)


# ─────────────────────────── Bateria ───────────────────────────

def rodar(df: pd.DataFrame, nperm: int) -> dict:
    res = {"baseline": [], "perm": {}, "placebo": [], "lead": [], "jack": {}}

    for rot, e, sinal, desc in HEADLINES:
        ixcol = f"ix__{DRIVER}__{e}__l{LAG_HEAD}"

        # (0) baseline: PanelOLS 2FE, cluster duplo (o número "oficial" do #38/#52)
        base = d38.rodar_interacao(df, REBANHO, ixcol)
        res["baseline"].append({"headline": rot, "exposicao": e, "sinal": sinal, **base})

        # (1) permutação do shifter
        p = permutacao_shifter(df, e, nperm)
        res["perm"][rot] = p
        # sanity: β within ≈ β PanelOLS
        p["beta_panelols"] = base["beta"]
        p["match"] = abs(p["beta_real"] - base["beta"]) < 5e-4

        # (2) placebos de desfecho
        for pcol, prot in PLACEBO_OUT.items():
            r = d38.rodar_interacao(df, pcol, ixcol)
            res["placebo"].append({"headline": rot, "exposicao": e,
                                   "placebo": prot[1], **(r or {})})

        # (3) placebo-no-tempo (lead 1 e 2)
        for k in (1, 2):
            r = d38.rodar_interacao(df, REBANHO, f"ixlead{k}__{e}")
            res["lead"].append({"headline": rot, "exposicao": e, "lead": k, **(r or {})})

        # (4) jackknife ano-a-ano
        zcol = f"zd_{DRIVER}_l{LAG_HEAD}"
        shock = (df.dropna(subset=[zcol]).groupby("ano")[zcol].first())  # tamanho do choque/ano
        jrows = []
        anos = sorted(df.dropna(subset=[ixcol, REBANHO])["ano"].unique())
        for yr in anos:
            r = d38.rodar_interacao(df[df["ano"] != yr], REBANHO, ixcol)
            if r and "beta" in r:
                jrows.append({"ano_removido": int(yr), "beta": r["beta"], "p": r["p"],
                              "shock_abs": float(abs(shock.get(yr, np.nan)))})
        res["jack"][rot] = pd.DataFrame(jrows)

    return res


# ─────────────────────────── Relatório ───────────────────────────

def relatar(res: dict) -> None:
    print("\n" + "=" * 82)
    print("PERNA 4 — BATERIA DE DEFENSABILIDADE (shift-share; sem dado novo)")
    print("=" * 82)

    print("\n[0] BASELINE (PanelOLS 2FE, cluster entidade+ano) — o número do #38/#52:")
    for r in res["baseline"]:
        print(f"  {r['headline']:26s}: β={r['beta']:+.4f}  p={r['p']:.3f}  "
              f"[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}]  N={r['n_obs']:,}  ({r['cluster']})")

    print("\n[1] INFERÊNCIA POR PERMUTAÇÃO DO SHIFTER (câmbio embaralhado, aptidão fixa):")
    for rot, p in res["perm"].items():
        chk = "✓" if p["match"] else f"⚠ Δ={abs(p['beta_real']-p['beta_panelols']):.1e}"
        print(f"  {rot:26s}: β_within={p['beta_real']:+.4f} (bate PanelOLS {chk}) | "
              f"T={p['T']} anos (=N efetivo do shifter)")
        print(f"     p_naive   = {p['p_naive']:.4f}   (permutação livre — quebra a autocorrelação)")
        print(f"     p_circular= {p['p_circ']:.4f}   (rotação — preserva a autocorrelação; DEFENSÁVEL)")

    print("\n[2] PLACEBOS DE DESFECHO (esperado NULO — especificidade do rebanho):")
    for r in res["placebo"]:
        flag = "  ← NULO ✓" if r.get("p", 0) >= 0.05 else "  ← ⚠ não-nulo"
        print(f"  {r['headline']:26s} → {r['placebo']:22s}: "
              f"β={r.get('beta', float('nan')):+.4f}  p={r.get('p', float('nan')):.3f}{flag}")

    print("\n[3] PLACEBO-NO-TEMPO / LEAD (choque FUTURO; esperado NULO — sem antecipação):")
    for r in res["lead"]:
        flag = "  ← NULO ✓" if r.get("p", 0) >= 0.05 else "  ← ⚠ não-nulo"
        print(f"  {r['headline']:26s} câmbio_(t+{r['lead']}) → rebanho_t: "
              f"β={r.get('beta', float('nan')):+.4f}  p={r.get('p', float('nan')):.3f}{flag}")

    print("\n[4] JACKKNIFE ANO-A-ANO (a identificação repousa nas grandes desvalorizações?):")
    for rot, jk in res["jack"].items():
        if jk.empty:
            continue
        b_full = next(r["beta"] for r in res["baseline"] if r["headline"] == rot)
        sign_ok = (np.sign(jk["beta"]) == np.sign(b_full)).mean() * 100
        p_ok = (jk["p"] < 0.05).mean() * 100
        infl = jk.loc[(jk["beta"] - b_full).abs().idxmax()]
        big = jk.nlargest(3, "shock_abs")["ano_removido"].tolist()
        print(f"  {rot:26s}: β varia [{jk['beta'].min():+.4f}, {jk['beta'].max():+.4f}] "
              f"(cheio {b_full:+.4f}); sinal estável {sign_ok:.0f}%; p<0,05 em {p_ok:.0f}% dos drops")
        print(f"     ano mais influente: {int(infl['ano_removido'])} "
              f"(β→{infl['beta']:+.4f}); maiores choques cambiais: {big}")


# ─────────────────────────── Figura ───────────────────────────

def figura(res: dict) -> None:
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 3, figsize=(16, 5))

    # Painel A: distribuição nula de permutação (H2, a exógena) + β real
    rotH2 = HEADLINES[1][0]
    p = res["perm"][rotH2]
    axA = axs[0]
    axA.hist(p["betas_naive"], bins=40, color="#c9d5c0", edgecolor="white",
             label=f"nulo (permutação naive)\np={p['p_naive']:.3f}")
    for b in p["betas_circ"]:
        axA.axvline(b, color="#8ca77b", lw=0.6, alpha=0.5)
    axA.axvline(p["betas_circ"][0], color="#8ca77b", lw=0.6, alpha=0.5,
                label=f"nulo (rotação circular)\np={p['p_circ']:.3f}")
    axA.axvline(p["beta_real"], color="#762a83", lw=2.5,
                label=f"β real = {p['beta_real']:+.3f}")
    axA.axvline(0, color="0.5", lw=1, ls="--")
    axA.set_title("A) Inferência por permutação — H2 (aptidão exógena)\n"
                  "câmbio embaralhado, aptidão fixa", fontsize=10, loc="left", fontweight="bold")
    axA.set_xlabel("β da interação sob o nulo")
    axA.set_ylabel("frequência")
    axA.legend(fontsize=8, loc="upper left")

    # Painel B: especificidade (baseline vs placebos vs lead) — forest, H2
    axB = axs[1]
    rows = []
    base = next(r for r in res["baseline"] if r["headline"] == rotH2)
    rows.append(("câmbio × aptidão → REBANHO (lag 1)", base["beta"], base["ci_lo"], base["ci_hi"], "#1b7837"))
    for r in res["placebo"]:
        if r["headline"] == rotH2:
            rows.append((r["placebo"], r.get("beta", np.nan), r.get("ci_lo", np.nan),
                         r.get("ci_hi", np.nan), "#999999"))
    for r in res["lead"]:
        if r["headline"] == rotH2:
            rows.append((f"câmbio (t+{r['lead']}) → rebanho_t [lead]", r.get("beta", np.nan),
                         r.get("ci_lo", np.nan), r.get("ci_hi", np.nan), "#999999"))
    rows = rows[::-1]
    for i, (rot, b, lo, hi, cor) in enumerate(rows):
        if np.isfinite(b):
            axB.errorbar(b, i, xerr=[[b - lo], [hi - b]], fmt="o", color=cor,
                         capsize=4, lw=2, ms=7)
        axB.annotate(rot, (0, i), xytext=(0, 12), textcoords="offset points",
                     ha="center", va="bottom", fontsize=7.5)
    axB.axvline(0, color="0.4", lw=1, ls="--")
    axB.set_yticks([])
    axB.set_ylim(-0.6, len(rows) - 0.4)
    axB.set_title("B) Especificidade — só o rebanho responde\n"
                  "placebos (urbano/água) e lead ≈ 0", fontsize=10, loc="left", fontweight="bold")
    axB.set_xlabel("β padronizado (IC95%)")

    # Painel C: jackknife ano-a-ano (H2), colorido pelo tamanho do choque
    axC = axs[2]
    jk = res["jack"][rotH2].sort_values("ano_removido")
    b_full = base["beta"]
    sc = axC.scatter(jk["ano_removido"], jk["beta"], c=jk["shock_abs"],
                     cmap="magma_r", s=45, edgecolor="0.3", lw=0.4, zorder=3)
    axC.axhline(b_full, color="#762a83", lw=1.5, ls="-", label=f"β amostra cheia ({b_full:+.3f})")
    axC.axhline(0, color="0.5", lw=1, ls="--")
    axC.set_title("C) Jackknife ano-a-ano — nenhum ano isolado carrega\n"
                  "cor = tamanho do choque cambial do ano removido", fontsize=10, loc="left",
                  fontweight="bold")
    axC.set_xlabel("ano removido")
    axC.set_ylabel("β (dropando o ano)")
    axC.legend(fontsize=8, loc="best")
    fig.colorbar(sc, ax=axC, label="|Δ câmbio| do ano", shrink=0.8)

    fig.suptitle("Pipeline #54 — endurecimento shift-share da PERNA 4 (câmbio × aptidão → rebanho de fronteira)",
                 fontsize=13, y=1.02, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "bateria.png", dpi=155, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[fig] {(DIR_OUT / 'bateria.png').relative_to(ROOT)}")


# ─────────────────────────── Persistência ───────────────────────────

def salvar(res: dict) -> None:
    # permutação
    perm_rows = []
    for rot, p in res["perm"].items():
        perm_rows.append({"headline": rot, "beta_real": p["beta_real"],
                          "beta_panelols": p["beta_panelols"], "match": p["match"],
                          "T_anos": p["T"], "n_obs": p["n_obs"],
                          "p_naive": p["p_naive"], "p_circular": p["p_circ"]})
    pd.DataFrame(perm_rows).to_csv(DIR_PROC / "perna4_permutacao.csv", index=False, encoding="utf-8")

    # placebos + lead num só arquivo
    pl = pd.DataFrame(res["placebo"]); pl["tipo"] = "placebo_desfecho"
    ld = pd.DataFrame(res["lead"]);    ld["tipo"] = "placebo_lead"
    pd.concat([pl, ld], ignore_index=True).to_csv(
        DIR_PROC / "perna4_placebos.csv", index=False, encoding="utf-8")

    # jackknife
    jk_all = []
    for rot, jk in res["jack"].items():
        jk = jk.copy(); jk.insert(0, "headline", rot)
        jk_all.append(jk)
    pd.concat(jk_all, ignore_index=True).to_csv(
        DIR_PROC / "perna4_jackknife.csv", index=False, encoding="utf-8")
    print("[OK] perna4_permutacao.csv | perna4_placebos.csv | perna4_jackknife.csv")


# ─────────────────────────── Main ───────────────────────────

def main(sem_figuras: bool = False, nperm: int = 5000) -> None:
    print("=" * 82)
    print("Pipeline #54 — defensabilidade da PERNA 4 (opção B: shift-share, sem dado novo)")
    print("=" * 82)
    df = carregar_estendido()
    print(f"[carga] {len(df):,} obs | {df['code_amc'].nunique()} AMCs × {df['ano'].nunique()} anos | "
          f"exp_apt_edafo em {df[EXPO_EDA].notna().sum():,} linhas | nperm={nperm}")

    res = rodar(df, nperm=nperm)
    relatar(res)
    salvar(res)
    if not sem_figuras:
        figura(res)

    print("\n" + "=" * 82)
    print("CONCLUÍDO — perna 4 endurecida (inferência de permutação + placebos + lead + jackknife).")
    print("=" * 82)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Defensabilidade shift-share da perna 4 (#54)")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--nperm", type=int, default=5000, help="permutações naive (default 5000)")
    args = ap.parse_args()
    try:
        main(sem_figuras=args.sem_figuras, nperm=args.nperm)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
