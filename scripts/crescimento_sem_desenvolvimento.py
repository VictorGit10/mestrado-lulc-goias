"""crescimento_sem_desenvolvimento.py — Pipeline #51
Crescimento econômico × desenvolvimento humano (IFDM 2013–2023) — medindo o que o #50 só viu no espaço
=====================================================================================================

PERGUNTA QUE RESPONDE
---------------------
O #50 (centro de massa econômico) mostrou a ASSINATURA ESPACIAL de "crescimento sem
desenvolvimento": a ÁREA (pasto/soja) marcha ao norte enquanto o VALOR (VA agro, PIB) fica
ancorado ao centro-sul — o vão valor↔fronteira alargou de ~84 p/ ~101 km. Mas o #50 fez isso
SEM um índice de desenvolvimento (o IDH-M municipal do #13 morre em 2010). O fio "crescimento
sem desenvolvimento" foi DESCARTADO por falta de dado.

Este pipeline REABRE o fio com uma MEDIÇÃO direta: o **IFDM (Índice FIRJAN de Desenvolvimento
Municipal), Nova Série Histórica 2013–2023** (#coleta_firjan_ifdm), que alcança o Ato III.
Três perguntas:

  A. NÍVEL/TENDÊNCIA — a fronteira Norte é menos desenvolvida e/ou avança mais devagar em
     desenvolvimento que o núcleo Sul?
  B. GRADIENTE (D14) — o desenvolvimento cai ao norte (fronteira)? O vão diverge ou converge?
  C. DESACOPLAMENTO — o crescimento econômico (VA agro, área, crédito, PIB) se TRADUZ em
     desenvolvimento? Onde a economia cresce mais, o IFDM sobe mais — ou o crescimento é
     "surdo" ao desenvolvimento? (cross-section com controle de latitude D14 + painel 2FE D7/D8)
  D. QUAL DIMENSÃO desacopla mais — emprego&renda, educação ou saúde?

CAUTELAS
--------
- IFDM ≠ IDH-M (construção diferente); é proxy de desenvolvimento, não de bem-estar amplo.
- Série NOVA (revisão metodológica): 2013–2023 é internamente consistente, NÃO emendável com a
  antiga 2005–2016. Janela curta (11 anos).
- VA agro e população existem 2013–2021 (defasagem IBGE). A janela de CRESCIMENTO é 2013→2021;
  os NÍVEIS de IFDM vão até 2023.
- Leitura ASSOCIATIVA (D14): controla-se latitude/longitude antes de atribuir efeito próprio.
  Nada aqui é causal — é a geografia do (des)acoplamento crescimento/desenvolvimento.
- O IFDM SUBIU em toda parte (0,49→0,63); "sem desenvolvimento" é sobre GANHO RELATIVO e NÍVEL,
  não ausência de ganho. Reportamos o que o dado disser, não a hipótese.

ENTRADAS
    data/processed/ifdm_goias_municipal.csv        (#coleta_firjan_ifdm)
    data/processed/painel_unificado.parquet        (#16)
    data/processed/amc_crosswalk_goias.csv + amc_goias.gpkg + mapeamento_mesorregioes.csv

SAÍDAS
    data/processed/desenvolvimento_regional.csv     (Bloco A)
    data/processed/desenvolvimento_gradiente.csv    (Blocos B/C: coeficientes)
    outputs/desenvolvimento/ifdm_regional.png       (IFDM Sul/Centro/Norte no tempo)
    outputs/desenvolvimento/decouplamento.png       (crescimento × Δ desenvolvimento)

COMO RODAR
    py -3.14 scripts/crescimento_sem_desenvolvimento.py
    py -3.14 scripts/crescimento_sem_desenvolvimento.py --sem-figuras

Depende de: #coleta_firjan_ifdm, #16 (painel), #25 (geometria AMC), #33/#39 (região).
Quando foi feito: 2026-07-18. Reabre o fio 6 do backlog ("crescimento sem desenvolvimento").
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
import centro_massa as cm  # noqa: E402  — metros_para_lonlat
from deslocamento_espacial import amc_para_meso, MESO_SUL, MESO_NORTE  # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "desenvolvimento"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ANO_INI, ANO_FIM_ECON, ANO_FIM_IFDM = 2013, 2021, 2023
BOOT_B = 2000
RNG = np.random.default_rng(20260718)

CORES_REGIAO = {"Sul": "#c2185b", "Centro": "#8d6e63", "Norte": "#2e7d32"}

# variáveis econômicas (crescimento) — extensivas, log-ratio 2013→2021
ECON = {
    "va_agro":  ("va_agro_real_rs",     "VA agropecuário"),
    "pib":      ("pib_real_rs",         "PIB total"),
    "area_agri":("lulc_agricultura_ha", "Área agrícola"),
    "sicor":    ("sicor_total_real_rs", "Crédito rural (SICOR)"),
    "rebanho":  ("pec_bovinos_cab",     "Rebanho bovino"),
}
IFDM_DIMS = {"ifdm": "IFDM Geral", "ifdm_emprego": "Emprego&Renda",
             "ifdm_educacao": "Educação", "ifdm_saude": "Saúde"}


def regiao_de_meso(m: str) -> str:
    if m in MESO_SUL:   return "Sul"
    if m in MESO_NORTE: return "Norte"
    return "Centro"


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def carregar() -> pd.DataFrame:
    ifdm = pd.read_csv(DIR_PROC / "ifdm_goias_municipal.csv")
    pan  = pd.read_parquet(DIR_PROC / "painel_unificado.parquet")
    pan  = pan[(pan.ano >= ANO_INI) & (pan.ano <= ANO_FIM_IFDM)]

    econ_cols = [c for c, _ in ECON.values()]
    base = pan[["cd_mun", "ano", "populacao"] + econ_cols].merge(
        ifdm, on=["cd_mun", "ano"], how="left")

    # região + latitude do centroide da AMC (via crosswalk)
    cw = pd.read_csv(DIR_PROC / "amc_crosswalk_goias.csv")[["cd_mun", "code_amc"]]
    reg = amc_para_meso()  # code_amc, nm_meso, cx, cy (EPSG:5880)
    ll = cm.metros_para_lonlat(reg[["cx", "cy"]].to_numpy())
    reg["lat"], reg["lon"] = ll[:, 1], ll[:, 0]
    reg["regiao"] = reg["nm_meso"].map(regiao_de_meso)
    geo = cw.merge(reg[["code_amc", "regiao", "nm_meso", "lat", "lon"]], on="code_amc", how="left")
    base = base.merge(geo, on="cd_mun", how="left")
    return base


def _logratio(df_wide: pd.DataFrame, col: str, a0: int, a1: int) -> pd.Series:
    """Δlog(col) = log(col_a1) - log(col_a0) por município; NA se algum for <=0/ausente."""
    p = df_wide.pivot(index="cd_mun", columns="ano", values=col)
    if a0 not in p or a1 not in p:
        return pd.Series(dtype=float)
    x0, x1 = p[a0], p[a1]
    m = (x0 > 0) & (x1 > 0)
    return np.log(x1.where(m)) - np.log(x0.where(m))


def montar_transversal(base: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por município: IFDM 2013/2023, Δ, crescimento econ 2013→2021, geo, pop."""
    idx = base[["cd_mun", "regiao", "nm_meso", "lat", "lon"]].drop_duplicates("cd_mun").set_index("cd_mun")

    for dim in IFDM_DIMS:
        piv = base.pivot(index="cd_mun", columns="ano", values=dim)
        idx[f"{dim}_ini"] = piv.get(ANO_INI)
        idx[f"{dim}_fim"] = piv.get(ANO_FIM_IFDM)
        idx[f"d_{dim}"]   = piv.get(ANO_FIM_IFDM) - piv.get(ANO_INI)

    for key, (col, _) in ECON.items():
        idx[f"g_{key}"] = _logratio(base, col, ANO_INI, ANO_FIM_ECON)

    pop = base.pivot(index="cd_mun", columns="ano", values="populacao")
    idx["pop_w"] = pop.get(ANO_FIM_ECON)  # peso fixo = pop 2021 (último ano completo)
    return idx.reset_index()


# ---------------------------------------------------------------------------
# Bloco A — nível e tendência por região
# ---------------------------------------------------------------------------
def _wmean(v: pd.Series, w: pd.Series) -> float:
    m = v.notna() & w.notna()
    return float(np.average(v[m], weights=w[m])) if m.any() else np.nan


def bloco_A(tx: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for reg in ["Sul", "Centro", "Norte"]:
        g = tx[tx.regiao == reg]
        row = {"regiao": reg, "n_mun": len(g)}
        for dim in IFDM_DIMS:
            row[f"{dim}_2013"]  = g[f"{dim}_ini"].mean()
            row[f"{dim}_2023"]  = g[f"{dim}_fim"].mean()
            row[f"{dim}_d"]     = g[f"d_{dim}"].mean()
            row[f"{dim}_2013w"] = _wmean(g[f"{dim}_ini"], g["pop_w"])
            row[f"{dim}_2023w"] = _wmean(g[f"{dim}_fim"], g["pop_w"])
        for key in ECON:
            row[f"g_{key}"] = g[f"g_{key}"].mean()
        linhas.append(row)
    return pd.DataFrame(linhas)


def _boot_gap(tx: pd.DataFrame, col: str) -> tuple[float, float, float]:
    """ΔNorte−Sul da coluna `col` + IC95% por bootstrap de municípios."""
    s = tx[tx.regiao == "Sul"][col].dropna().to_numpy()
    n = tx[tx.regiao == "Norte"][col].dropna().to_numpy()
    obs = n.mean() - s.mean()
    bs = np.array([RNG.choice(n, n.size).mean() - RNG.choice(s, s.size).mean()
                   for _ in range(BOOT_B)])
    return obs, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------------------
# Blocos B/C — gradiente e desacoplamento (OLS transversal + painel 2FE)
# ---------------------------------------------------------------------------
def ols(y: pd.Series, X: pd.DataFrame) -> dict:
    import statsmodels.api as sm
    d = pd.concat([y, X], axis=1).dropna()
    if len(d) < 10:
        return {}
    yy, XX = d.iloc[:, 0], sm.add_constant(d.iloc[:, 1:])
    m = sm.OLS(yy, XX).fit(cov_type="HC1")
    return {"n": int(m.nobs), "r2": float(m.rsquared),
            "coef": m.params.to_dict(), "p": m.pvalues.to_dict()}


def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def bloco_B(tx: pd.DataFrame) -> pd.DataFrame:
    """Gradiente latitudinal do IFDM (nível 2023 e Δ2013-23). D14: + controle de longitude."""
    out = []
    for alvo, rot in [("ifdm_fim", "IFDM 2023 (nível)"), ("d_ifdm", "Δ IFDM 2013→2023")]:
        for spec, cols in [("~lat", ["lat"]), ("~lat+lon", ["lat", "lon"])]:
            r = ols(tx[alvo], tx[cols].apply(zscore))
            if r:
                out.append({"alvo": rot, "spec": spec, "n": r["n"], "r2": r["r2"],
                            "beta_lat": r["coef"].get("lat"), "p_lat": r["p"].get("lat"),
                            "beta_lon": r["coef"].get("lon"), "p_lon": r["p"].get("lon")})
    return pd.DataFrame(out)


def bloco_C1(tx: pd.DataFrame) -> pd.DataFrame:
    """Desacoplamento transversal: Δdimensão ~ crescimento econômico (bruto e parcial|lat,lon)."""
    from scipy.stats import pearsonr
    out = []
    for dim in IFDM_DIMS:
        y = tx[f"d_{dim}"]
        for key, (_, rot) in ECON.items():
            x = tx[f"g_{key}"]
            d = pd.concat([y, x], axis=1).dropna()
            if len(d) < 10:
                continue
            r_bruto, p_bruto = pearsonr(d.iloc[:, 0], d.iloc[:, 1])
            # parcial controlando lat+lon (D14)
            reg = ols(y, tx[[f"g_{key}", "lat", "lon"]].rename(columns={f"g_{key}": "growth"})
                      .assign(growth=zscore(tx[f"g_{key}"]), lat=zscore(tx["lat"]), lon=zscore(tx["lon"])))
            out.append({"dim": IFDM_DIMS[dim], "growth": rot, "n": len(d),
                        "r_bruto": r_bruto, "p_bruto": p_bruto,
                        "beta_parcial": reg.get("coef", {}).get("growth"),
                        "p_parcial": reg.get("p", {}).get("growth")})
    return pd.DataFrame(out)


def bloco_C2(base: pd.DataFrame) -> pd.DataFrame:
    """Painel 2FE (D8) em 1as diferenças (D7): ΔIFDM ~ Δlog(VA agro)+Δlog(área) intra-município."""
    from linearmodels.panel import PanelOLS
    dfp = base[(base.ano >= ANO_INI) & (base.ano <= ANO_FIM_ECON)].copy()
    dfp = dfp.sort_values(["cd_mun", "ano"])
    dfp["l_va"]   = np.log(dfp["va_agro_real_rs"].where(dfp["va_agro_real_rs"] > 0))
    dfp["l_area"] = np.log(dfp["lulc_agricultura_ha"].where(dfp["lulc_agricultura_ha"] > 0))
    for c in ["ifdm", "l_va", "l_area"]:
        dfp[f"d_{c}"] = dfp.groupby("cd_mun")[c].diff()
    d = dfp.dropna(subset=["d_ifdm", "d_l_va", "d_l_area"]).set_index(["cd_mun", "ano"])
    out = []
    for rhs in (["d_l_va"], ["d_l_area"], ["d_l_va", "d_l_area"]):
        m = PanelOLS(d["d_ifdm"], d[rhs], entity_effects=True, time_effects=True)
        res = m.fit(cov_type="clustered", cluster_entity=True)
        for v in rhs:
            out.append({"modelo": "+".join(rhs), "regressor": v,
                        "beta": float(res.params[v]), "p": float(res.pvalues[v]),
                        "n": int(res.nobs), "r2_within": float(res.rsquared_within)})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def figuras(base: pd.DataFrame, tx: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    # Fig 1 — IFDM por região no tempo (média simples municipal) + subíndices
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, (dim, rot) in zip(axes.ravel(), IFDM_DIMS.items()):
        for reg in ["Sul", "Centro", "Norte"]:
            cds = tx[tx.regiao == reg]["cd_mun"]
            g = (base[base.cd_mun.isin(cds)].groupby("ano")[dim].mean())
            ax.plot(g.index, g.values, lw=2.1, color=CORES_REGIAO[reg], label=reg)
        ax.set_title(rot, fontsize=10, loc="left")
        ax.grid(True, alpha=0.25)
        ax.set_ylabel("IFDM (média municipal)")
    axes[0, 0].legend(loc="lower right", fontsize=8.5, title="Região")
    fig.suptitle("Desenvolvimento (IFDM) por região, Goiás 2013–2023 — a fronteira Norte fica atrás?",
                 fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "ifdm_regional.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'ifdm_regional.png').relative_to(ROOT)}")

    # Fig 2 — desacoplamento: crescimento VA agro (x) × Δ IFDM (y), cor por região
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for reg in ["Sul", "Centro", "Norte"]:
        g = tx[tx.regiao == reg]
        ax.scatter(g["g_va_agro"], g["d_ifdm"], s=26, alpha=0.7,
                   color=CORES_REGIAO[reg], label=reg, edgecolor="none")
    d = tx[["g_va_agro", "d_ifdm"]].dropna()
    if len(d) > 2:
        b = np.polyfit(d["g_va_agro"], d["d_ifdm"], 1)
        xs = np.linspace(d["g_va_agro"].min(), d["g_va_agro"].max(), 50)
        ax.plot(xs, np.polyval(b, xs), "k--", lw=1.3, alpha=0.7,
                label=f"ajuste (incl.={b[0]:+.3f})")
    ax.axhline(0, color="0.6", lw=0.8)
    ax.set_xlabel("Crescimento econômico 2013→2021: Δlog(VA agropecuário)")
    ax.set_ylabel("Δ IFDM 2013→2023 (ganho de desenvolvimento)")
    ax.set_title("Crescimento econômico se traduz em desenvolvimento?\n"
                 "se a nuvem é plana, o crescimento é 'surdo' ao desenvolvimento", fontsize=11, loc="left")
    ax.legend(loc="best", fontsize=8.5)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "decouplamento.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'decouplamento.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #51 — crescimento × desenvolvimento (IFDM)")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 78)
    print("Pipeline #51 — Crescimento econômico × desenvolvimento humano (IFDM 2013–2023)")
    print("=" * 78)

    base = carregar()
    tx = montar_transversal(base)
    print(f"[carga] {tx['cd_mun'].nunique()} municípios | região: "
          f"{tx['regiao'].value_counts().to_dict()}")

    # --- A. nível e tendência regional ---
    A = bloco_A(tx)
    A.to_csv(DIR_PROC / "desenvolvimento_regional.csv", index=False, encoding="utf-8")
    print("\n[A] IFDM por região (média municipal simples) e crescimento econômico 2013→2021")
    print("-" * 78)
    for _, r in A.iterrows():
        print(f"  {r['regiao']:7s} (n={int(r['n_mun']):3d}) | IFDM {r['ifdm_2013']:.3f}→{r['ifdm_2023']:.3f} "
              f"(Δ{r['ifdm_d']:+.3f}) | Δlog VA agro {r['g_va_agro']:+.2f} | "
              f"Δlog área {r['g_area_agri']:+.2f} | Δlog rebanho {r['g_rebanho']:+.2f}")
    obs, lo, hi = _boot_gap(tx, "ifdm_fim")
    obs_d, lo_d, hi_d = _boot_gap(tx, "d_ifdm")
    print(f"  → NÍVEL IFDM 2023 Norte−Sul: {obs:+.3f} [IC95% {lo:+.3f}, {hi:+.3f}] "
          f"{'(≠0)' if lo*hi>0 else '(inclui 0)'}")
    print(f"  → GANHO ΔIFDM Norte−Sul:     {obs_d:+.3f} [IC95% {lo_d:+.3f}, {hi_d:+.3f}] "
          f"{'(diverge/converge ≠0)' if lo_d*hi_d>0 else '(inclui 0)'}")

    # --- B. gradiente latitudinal ---
    B = bloco_B(tx)
    print("\n[B] Gradiente latitudinal do IFDM (β z-score; D14 = controlar lat+lon)")
    print("-" * 78)
    for _, r in B.iterrows():
        extra = f" | β_lon {r['beta_lon']:+.3f} (p={r['p_lon']:.3f})" if pd.notna(r['beta_lon']) else ""
        print(f"  {r['alvo']:22s} {r['spec']:9s} n={int(r['n'])} r²={r['r2']:.3f} | "
              f"β_lat {r['beta_lat']:+.3f} (p={r['p_lat']:.3f}){extra}")

    # --- C1. desacoplamento transversal ---
    C1 = bloco_C1(tx)
    print("\n[C1] Desacoplamento (transversal): Δdesenvolvimento ~ crescimento econômico")
    print("     r_bruto e β_parcial|lat,lon (D14). Perto de 0 = crescimento 'surdo' ao desenvolvimento.")
    print("-" * 78)
    for dim_rot in ["IFDM Geral"]:
        sub = C1[C1.dim == dim_rot]
        for _, r in sub.iterrows():
            print(f"  {r['dim']:12s} × {r['growth']:22s} r={r['r_bruto']:+.3f} (p={r['p_bruto']:.3f}) | "
                  f"parcial|lat {r['beta_parcial']:+.3f} (p={r['p_parcial']:.3f})")

    # --- C2. painel 2FE ---
    C2 = bloco_C2(base)
    print("\n[C2] Painel 2FE (município+ano) em 1as diferenças (D7/D8): ΔIFDM ~ Δlog econ intra-município")
    print("-" * 78)
    for _, r in C2.iterrows():
        print(f"  modelo [{r['modelo']:16s}] {r['regressor']:8s} β={r['beta']:+.4f} "
              f"(p={r['p']:.3f}) | n={int(r['n'])} r²within={r['r2_within']:.4f}")

    # --- D. qual dimensão desacopla ---
    print("\n[D] Qual dimensão desacopla? (r transversal Δsubíndice × Δlog VA agro)")
    print("-" * 78)
    d_va = C1[C1.growth == "VA agropecuário"]
    for _, r in d_va.iterrows():
        print(f"  {r['dim']:14s} r={r['r_bruto']:+.3f} (p={r['p_bruto']:.3f}) | "
              f"parcial|lat {r['beta_parcial']:+.3f} (p={r['p_parcial']:.3f})")

    # salvar coeficientes
    grad = pd.concat([
        B.assign(bloco="B_gradiente"),
        C1.assign(bloco="C1_desacoplamento"),
        C2.assign(bloco="C2_painel2fe"),
    ], ignore_index=True)
    grad.to_csv(DIR_PROC / "desenvolvimento_gradiente.csv", index=False, encoding="utf-8")
    print(f"\n[OK] desenvolvimento_regional.csv + desenvolvimento_gradiente.csv")

    if not args.sem_figuras:
        figuras(base, tx)

    print("\n" + "=" * 78)
    print("CONCLUÍDO — Pipeline #51.")
    print("=" * 78)


if __name__ == "__main__":
    main()
