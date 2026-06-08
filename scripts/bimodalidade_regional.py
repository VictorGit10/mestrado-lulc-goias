"""bimodalidade_regional.py — Pipeline #28C (decomposição within/between)
========================================================================

PERGUNTA QUE RESPONDE
---------------------
A bimodalidade da idade da pastagem na conversão (#28: picos em ~5 e ~22 anos)
é "regionalmente causada"? Ou seja, ela é uma COMPOSIÇÃO entre regiões unimodais
(Sul jovem × Norte velho), ou uma COEXISTÊNCIA dos dois mecanismos DENTRO de
cada região, apenas com peso de mistura diferente?

A distinção é decisiva para a redação (Decisão D14): "regionalmente causada"
exige que cada região seja internamente unimodal e que a bimodalidade do
agregado venha só da mistura de regiões. Se cada região é, ela mesma, bimodal,
a geografia MODULA o peso — não CAUSA a bimodalidade.

CONFUNDIDOR EXPLÍCITO: o tempo. O Ato I converte pasto jovem (mediana 6a) e o
Ato II/III convertem pasto velho (~19a); logo, parte da "bimodalidade" agregada
é TEMPORAL, não regional. Por isso a célula região×ato é o teste decisivo:
dentro de uma única região E um único ato, ainda há dois modos?

TESTES
------
  1. Decomposição de variância (η²) da idade não-censurada por:
     região | ato | região×ato  → quanto cada eixo "explica" da variância.
  2. GMM 1c vs 2c por mesorregião (reusa ajustar_gmm_unidim do #28):
     cada região continua bimodal (ΔBIC>10 + modos separados)?
  3. GMM 1c vs 2c por célula região×ato (Ato II e III): isola a coexistência
     pura do confundidor temporal.
  4. Coeficiente de bimodalidade de Sarle (model-free) por região e célula,
     como corroboração independente do GMM.
  5. η² da pertinência ao modo "velho" (responsabilidade posterior do GMM
     GLOBAL, rótulos consistentes) por região, ato e célula → a parcela
     BETWEEN vs WITHIN da separação jovem/velho.

VEREDITO
--------
Se (a) as células região×ato permanecem bimodais e (b) o WITHIN domina o η² da
pertinência ao modo velho, então a bimodalidade NÃO é regionalmente causada:
é coexistência dos dois mecanismos modulada por um gradiente Sul→Norte no peso
da mistura. (Coerente com a leitura honesta da D14.)

ENTRADAS
    data/processed/pastagem_idade_conversao.csv   (#28A)

SAÍDAS  (sufixo `_amc` na malha AMC)
    data/processed/idade_bimodalidade_por_grupo[_amc].csv     (GMM+BC por unidade e célula)
    data/processed/idade_bimodalidade_decomposicao[_amc].csv  (η²/ω² variância + modo velho + permutação)
    outputs/idade_pastagem/bimodalidade_unidade_ato[_amc].png (grid unidade×{todos,II,III})

COMO RODAR
    python scripts/bimodalidade_regional.py                 # malha mesorregião (5)
    python scripts/bimodalidade_regional.py --malha amc     # malha AMC (158)
    python scripts/bimodalidade_regional.py --sem-figuras

Depende de: #28A (pastagem_idade_conversao.csv) e reusa o GMM do #28
(analise_reserva_terra.ajustar_gmm_unidim); na malha AMC, o crosswalk do #25
(amc_crosswalk_goias.csv). Quando foi feito: 2026-06-07/08.
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
from config_periodos import ATOS                                    # noqa: E402
from analise_reserva_terra import carregar, ajustar_gmm_unidim      # noqa: E402

ROOT    = Path(__file__).resolve().parent.parent
DIR_OUT = ROOT / "outputs" / "idade_pastagem"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_PROC = ROOT / "data" / "processed"

# Critérios para chamar uma distribuição de "bimodal" (todos precisam valer):
BIC_MIN      = 10.0   # ΔBIC = bic_1c - bic_2c > 10  → evidência forte p/ 2 comp.
SEP_MIN      = 5.0    # separação mínima entre modos (anos): evita 2-gaussianas que
                      #   só modelam assimetria de uma unimodal
PESO_MIN     = 0.15   # peso mínimo do componente menor (modo não-trivial)
N_CONFIAVEL  = 50     # abaixo disso, o ajuste é frágil (flag, não descarte)


# ---------------------------------------------------------------------------
# Estatísticas auxiliares
# ---------------------------------------------------------------------------

def eta_squared(df: pd.DataFrame, value_col: str, group_cols) -> float:
    """η² = SS_entre / SS_total para o agrupamento dado (fração da variância
    de `value_col` explicada por pertencer ao grupo)."""
    y = df[value_col].to_numpy(float)
    grand = y.mean()
    ss_total = np.sum((y - grand) ** 2)
    if ss_total <= 0:
        return float("nan")
    ss_between = 0.0
    for _, g in df.groupby(group_cols, observed=True):
        yi = g[value_col].to_numpy(float)
        ss_between += len(yi) * (yi.mean() - grand) ** 2
    return float(ss_between / ss_total)


def omega_squared(df: pd.DataFrame, value_col: str, group_cols) -> float:
    """ω² (omega-quadrado): effect-size de variância explicada CORRIGIDO para o
    número de grupos. Ao contrário do η², não infla mecanicamente quando há mais
    grupos (pode até ficar negativo se o agrupamento não explica nada além do
    acaso). É a métrica honesta para comparar 5 mesorregiões vs ~150 AMCs."""
    y = df[value_col].to_numpy(float)
    grand = y.mean()
    n = len(y)
    ss_total = float(np.sum((y - grand) ** 2))
    if ss_total <= 0:
        return float("nan")
    ss_between = 0.0
    k = 0
    for _, g in df.groupby(group_cols, observed=True):
        yi = g[value_col].to_numpy(float)
        ss_between += len(yi) * (yi.mean() - grand) ** 2
        k += 1
    ss_within = ss_total - ss_between
    df_w = n - k
    if df_w <= 0:
        return float("nan")
    ms_within = ss_within / df_w
    return float((ss_between - (k - 1) * ms_within) / (ss_total + ms_within))


def perm_eta(df: pd.DataFrame, value_col: str, group_col: str,
             B: int = 200, seed: int = 42) -> dict:
    """Linha-base de permutação para η²: embaralha os rótulos espaciais (preserva
    tamanhos de grupo e a distribuição do valor) e recalcula η². Dá o η² ESPERADO
    SOB O ACASO para aquele número/tamanho de grupos — o piso mecânico contra o
    qual o η² observado deve ser comparado."""
    rng = np.random.default_rng(seed)
    obs = eta_squared(df, value_col, group_col)
    y = df[value_col].to_numpy(float)
    labels = df[group_col].to_numpy()
    grand = y.mean()
    ss_total = float(np.sum((y - grand) ** 2))
    tmp = pd.DataFrame({"y": y, "g": labels})
    nulos = np.empty(B)
    for b in range(B):
        tmp["g"] = rng.permutation(labels)
        ssb = 0.0
        for _, gg in tmp.groupby("g", observed=True):
            yi = gg["y"].to_numpy()
            ssb += len(yi) * (yi.mean() - grand) ** 2
        nulos[b] = ssb / ss_total
    pval = float((np.sum(nulos >= obs) + 1) / (B + 1))
    return {"eta2_obs": float(obs), "eta2_acaso_medio": float(nulos.mean()),
            "eta2_acaso_p95": float(np.quantile(nulos, 0.95)),
            "eta2_liquido": float(obs - nulos.mean()), "p_perm": pval}


def bimodality_coef(x: np.ndarray) -> float:
    """Coeficiente de bimodalidade de Sarle (model-free). BC > 5/9≈0.555 sugere
    bimodalidade (ou caudas mais leves que a normal); ≤0.555 sugere unimodal.
    Usa skewness e excess-kurtosis com correção de viés (amostral)."""
    from scipy.stats import skew, kurtosis
    n = len(x)
    if n < 4:
        return float("nan")
    g = skew(x, bias=False)
    k = kurtosis(x, fisher=True, bias=False)          # excess kurtosis
    denom = k + 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    if denom <= 0:
        return float("nan")
    return float((g ** 2 + 1.0) / denom)


def avaliar_grupo(escopo: str, chave: str, x: np.ndarray) -> dict:
    """Ajusta GMM 1c/2c (método do #28) + BC de Sarle e classifica bimodalidade."""
    n = len(x)
    g = ajustar_gmm_unidim(x.astype(float))
    delta_bic = g["bic_1c"] - g["bic_2c"]
    sep       = abs(g["mu2"] - g["mu1"])
    peso_menor = min(g["w1"], g["w2"])
    bc = bimodality_coef(x)
    bimodal = (delta_bic > BIC_MIN) and (sep > SEP_MIN) and (peso_menor > PESO_MIN)
    return {
        "escopo": escopo, "chave": chave, "n": int(n),
        "mediana": float(np.median(x)),
        "mu_jovem": round(g["mu1"], 1), "w_jovem": round(g["w1"], 3),
        "mu_velho": round(g["mu2"], 1), "w_velho": round(g["w2"], 3),
        "separacao_anos": round(sep, 1),
        "delta_bic": round(delta_bic, 1),
        "bc_sarle": round(bc, 3) if bc == bc else None,
        "bimodal": bool(bimodal),
        "confiavel": bool(n >= N_CONFIAVEL),
    }


# ---------------------------------------------------------------------------
# Posterior do modo "velho" (GMM global, rótulos consistentes)
# ---------------------------------------------------------------------------

def posterior_modo_velho(x: np.ndarray) -> np.ndarray:
    """Responsabilidade posterior P(componente velho | idade) de UM GMM global
    de 2 componentes. Rótulo 'velho' = componente de maior média (consistente
    para todos os pixels — evita label-switching entre subamostras)."""
    from sklearn.mixture import GaussianMixture
    gmm = GaussianMixture(n_components=2, random_state=42, max_iter=250)
    gmm.fit(x.reshape(-1, 1))
    idx_velho = int(np.argmax(gmm.means_.flatten()))
    return gmm.predict_proba(x.reshape(-1, 1))[:, idx_velho]


# ---------------------------------------------------------------------------
# Figura: grid região × {todos, Ato II, Ato III}
# ---------------------------------------------------------------------------

def fig_grid(df_nc: pd.DataFrame, unidades: list, col_esp: str = "mesorregiao",
             lab_fn=str, outname: str = "bimodalidade_unidade_ato.png") -> None:
    import matplotlib.pyplot as plt
    from scipy.stats import norm

    cols = [("Todos os anos", None),
            ("Ato II (2001–2019)", "II"),
            ("Ato III (2020–2024)", "III")]
    bins = np.arange(0, 41, 2)
    xs = np.linspace(0, 40, 400)

    fig, axes = plt.subplots(len(unidades), len(cols),
                             figsize=(4.3 * len(cols), 2.7 * len(unidades)),
                             sharex=True, sharey=True)
    axes = np.atleast_2d(axes)
    for i, reg in enumerate(unidades):
        for j, (titulo, ato) in enumerate(cols):
            ax = axes[i, j]
            sub = df_nc[df_nc[col_esp] == reg]
            if ato is not None:
                sub = sub[sub["ato"] == ato]
            x = sub["idade_pastagem_anos"].to_numpy(float)
            if len(x) < 5:
                ax.text(0.5, 0.5, "n<5", ha="center", va="center",
                        transform=ax.transAxes, color="0.6")
                ax.set_axis_off()
                continue
            ax.hist(x, bins=bins, density=True, color="#dcdcd6",
                    edgecolor="white", alpha=0.9)
            g = ajustar_gmm_unidim(x)
            y1 = g["w1"] * norm.pdf(xs, g["mu1"], max(g["sig1"], 0.3))
            y2 = g["w2"] * norm.pdf(xs, g["mu2"], max(g["sig2"], 0.3))
            ax.plot(xs, y1 + y2, color="#8a3068", lw=2.0)
            ax.plot(xs, y1, "--", color="#d95f02", lw=1.2)
            ax.plot(xs, y2, "--", color="#1b9e77", lw=1.2)
            dbic = g["bic_1c"] - g["bic_2c"]
            bc = bimodality_coef(x)
            sep = abs(g["mu2"] - g["mu1"])
            bimodal = (dbic > BIC_MIN) and (sep > SEP_MIN) and (min(g["w1"], g["w2"]) > PESO_MIN)
            marca = "● bimodal" if bimodal else "○ unimodal"
            ax.text(0.97, 0.95, f"n={len(x):,}\nΔBIC={dbic:.0f}\nBC={bc:.2f}\n{marca}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
                    color="#333")
            if i == 0:
                ax.set_title(titulo, fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{lab_fn(reg)}\n(mediana {np.median(x):.0f}a)", fontsize=8.5)
    for ax in axes[-1, :]:
        ax.set_xlabel("Idade na conversão (anos)", fontsize=8.5)
    fig.suptitle("Bimodalidade da idade do pasto DENTRO de cada unidade espacial e ato\n"
                 "— mistura GMM, -- componentes; ● = bimodal (ΔBIC>10, modos>5a, peso>0,15)",
                 fontsize=12, y=0.997)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = DIR_OUT / outname
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #28C — within/between da bimodalidade")
    ap.add_argument("--malha", choices=["meso", "amc"], default="meso",
                    help="recorte espacial: mesorregião (5) ou AMC (~150)")
    ap.add_argument("--n-gmm-min", type=int, default=100,
                    help="n mínimo de pixels p/ ajustar GMM por unidade espacial")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    suf = "" if args.malha == "meso" else "_amc"
    col_esp = "mesorregiao" if args.malha == "meso" else "code_amc"
    lab_esp = "mesorregião" if args.malha == "meso" else "AMC"
    lab_fn  = (lambda v: str(v)) if args.malha == "meso" else (lambda v: f"AMC {int(v)}")

    print("=" * 76)
    print(f"Pipeline #28C — A bimodalidade é regionalmente causada? (malha = {args.malha.upper()})")
    print("=" * 76)

    df = carregar()
    df_nc = df[~df["censurado"]].copy()
    df_nc = df_nc[df_nc["mesorregiao"].notna() & (df_nc["mesorregiao"] != "")]
    df_nc = df_nc[df_nc["ato"].notna()]

    if args.malha == "amc":
        cw = pd.read_csv(ROOT / "data" / "processed" / "amc_crosswalk_goias.csv",
                         dtype={"cd_mun": "int64", "code_amc": "int64"})
        df_nc = df_nc.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
        df_nc = df_nc[df_nc["code_amc"].notna()]
        df_nc["code_amc"] = df_nc["code_amc"].astype(int)

    print(f"[dados] {len(df_nc):,} pixels não-censurados | "
          f"{df_nc[col_esp].nunique()} {lab_esp}(s) com conversão | "
          f"{df_nc['ano_conversao'].nunique()} anos")

    # Unidades ordenadas pela mediana (jovem → velho).
    ord_esp = (df_nc.groupby(col_esp)["idade_pastagem_anos"].median()
                     .sort_values().index.tolist())

    # ---- Teste 1: decomposição de variância da IDADE (η², ω², acaso) -------
    eta_esp     = eta_squared(df_nc, "idade_pastagem_anos", col_esp)
    om_esp      = omega_squared(df_nc, "idade_pastagem_anos", col_esp)
    eta_ato     = eta_squared(df_nc, "idade_pastagem_anos", "ato")
    eta_esp_ato = eta_squared(df_nc, "idade_pastagem_anos", [col_esp, "ato"])
    om_esp_ato  = omega_squared(df_nc, "idade_pastagem_anos", [col_esp, "ato"])
    print("\n[1] Decomposição de variância da IDADE:")
    print(f"    {lab_esp:<12} η²={eta_esp:6.1%}  ω²={om_esp:6.1%}  (ω² corrige nº de grupos)")
    print(f"    ato (tempo)  η²={eta_ato:6.1%}")
    print(f"    {lab_esp}×ato η²={eta_esp_ato:6.1%}  ω²={om_esp_ato:6.1%}")
    print(f"    within-célula (1−ω²): {1 - om_esp_ato:6.1%}")

    # ---- Teste 5: separação jovem/velho (posterior do GMM global) ----------
    z = posterior_modo_velho(df_nc["idade_pastagem_anos"].to_numpy(float))
    df_nc["p_velho"] = z
    etaz_esp     = eta_squared(df_nc, "p_velho", col_esp)
    omz_esp      = omega_squared(df_nc, "p_velho", col_esp)
    etaz_ato     = eta_squared(df_nc, "p_velho", "ato")
    etaz_esp_ato = eta_squared(df_nc, "p_velho", [col_esp, "ato"])
    omz_esp_ato  = omega_squared(df_nc, "p_velho", [col_esp, "ato"])
    print("\n[5] Decomposição da SEPARAÇÃO jovem/velho (pertinência ao modo velho):")
    print(f"    {lab_esp:<12} η²={etaz_esp:6.1%}  ω²={omz_esp:6.1%}")
    print(f"    ato (tempo)  η²={etaz_ato:6.1%}")
    print(f"    {lab_esp}×ato η²={etaz_esp_ato:6.1%}  ω²={omz_esp_ato:6.1%}")
    print(f"    DENTRO das células (1−ω²): {1 - omz_esp_ato:6.1%}")

    # ---- Linha-base de permutação (piso do acaso p/ esse nº de grupos) -----
    print(f"\n[perm] η² esperado sob ACASO ({df_nc[col_esp].nunique()} grupos, "
          f"rótulos embaralhados, B=200):")
    pm_idade = perm_eta(df_nc, "idade_pastagem_anos", col_esp, B=200)
    pm_velho = perm_eta(df_nc, "p_velho", col_esp, B=200)
    for nome, pm in [("idade", pm_idade), ("p_velho", pm_velho)]:
        print(f"    {nome:<8} obs={pm['eta2_obs']:.1%}  acaso≈{pm['eta2_acaso_medio']:.1%} "
              f"(p95={pm['eta2_acaso_p95']:.1%})  líquido={pm['eta2_liquido']:.1%}  "
              f"p={pm['p_perm']:.3f}")

    # ---- Testes 2-4: GMM + BC por unidade e por célula unidade×ato ---------
    linhas = [avaliar_grupo("GLOBAL", "nao_censurado",
                            df_nc["idade_pastagem_anos"].to_numpy())]
    # Por unidade espacial (só as com n suficiente p/ GMM confiável).
    unidades_gmm = [u for u in ord_esp
                    if (df_nc[col_esp] == u).sum() >= args.n_gmm_min]
    for u in unidades_gmm:
        x = df_nc[df_nc[col_esp] == u]["idade_pastagem_anos"].to_numpy()
        linhas.append(avaliar_grupo("UNIDADE", lab_fn(u), x))
    # Por célula unidade×ato (Ato II e III), idem.
    for u in unidades_gmm:
        for ato in ("II", "III"):
            x = df_nc[(df_nc[col_esp] == u) &
                      (df_nc["ato"] == ato)]["idade_pastagem_anos"].to_numpy()
            if len(x) >= args.n_gmm_min:
                linhas.append(avaliar_grupo("UNIDADE_ATO", f"{lab_fn(u)} · Ato {ato}", x))
    res = pd.DataFrame(linhas)

    n_unid = (res.escopo == "UNIDADE").sum()
    n_unid_bim = int(res[res.escopo == "UNIDADE"]["bimodal"].sum())
    n_cell = (res.escopo == "UNIDADE_ATO").sum()
    n_cell_bim = int(res[res.escopo == "UNIDADE_ATO"]["bimodal"].sum())

    print(f"\n[2-4] GMM por unidade (n≥{args.n_gmm_min}): "
          f"{n_unid_bim}/{n_unid} {lab_esp}(s) bimodais | "
          f"células {lab_esp}×ato bimodais: {n_cell_bim}/{n_cell}")
    # Mostra as 12 maiores unidades.
    head = res[res.escopo == "UNIDADE"].nlargest(12, "n")
    print("      unidade           n     mediana  jovem  velho   ΔBIC    BC    bimodal?")
    for _, r in head.iterrows():
        print(f"      {r['chave']:<16} {r['n']:>6}   {r['mediana']:>4.0f}a   "
              f"{r['mu_jovem']:>4.1f}  {r['mu_velho']:>5.1f}  {r['delta_bic']:>6.0f}  "
              f"{r['bc_sarle']:.2f}   {'SIM' if r['bimodal'] else 'não'}")

    # ---- Salvar -----------------------------------------------------------
    arq_grupo  = DIR_PROC / f"idade_bimodalidade_por_grupo{suf}.csv"
    arq_decomp = DIR_PROC / f"idade_bimodalidade_decomposicao{suf}.csv"
    res.to_csv(arq_grupo, index=False, encoding="utf-8")
    decomp = pd.DataFrame([
        {"malha": args.malha, "alvo": "idade",   "eixo": "espacial",     "eta2": eta_esp,     "omega2": om_esp},
        {"malha": args.malha, "alvo": "idade",   "eixo": "ato",          "eta2": eta_ato,     "omega2": None},
        {"malha": args.malha, "alvo": "idade",   "eixo": "espacial_ato", "eta2": eta_esp_ato, "omega2": om_esp_ato},
        {"malha": args.malha, "alvo": "idade",   "eixo": "within_cell",  "eta2": 1 - eta_esp_ato, "omega2": 1 - om_esp_ato},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "espacial",     "eta2": etaz_esp,     "omega2": omz_esp},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "ato",          "eta2": etaz_ato,     "omega2": None},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "espacial_ato", "eta2": etaz_esp_ato, "omega2": omz_esp_ato},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "within_cell",  "eta2": 1 - etaz_esp_ato, "omega2": 1 - omz_esp_ato},
        {"malha": args.malha, "alvo": "idade",   "eixo": "perm_obs",     "eta2": pm_idade["eta2_obs"],    "omega2": pm_idade["eta2_liquido"]},
        {"malha": args.malha, "alvo": "p_velho", "eixo": "perm_obs",     "eta2": pm_velho["eta2_obs"],    "omega2": pm_velho["eta2_liquido"]},
    ])
    decomp.to_csv(arq_decomp, index=False, encoding="utf-8")
    print(f"\n[OK] {arq_grupo.relative_to(ROOT)}  ({len(res)} linhas)")
    print(f"[OK] {arq_decomp.relative_to(ROOT)}  ({len(decomp)} linhas)")

    if not args.sem_figuras:
        # Para AMC, ilustra com as maiores unidades (grid de 150 seria ilegível).
        unidades_fig = (ord_esp if args.malha == "meso"
                        else res[res.escopo == "UNIDADE"].nlargest(6, "n")
                              ["chave"].str.replace("AMC ", "").astype(int).tolist())
        fig_grid(df_nc, unidades_fig, col_esp=col_esp, lab_fn=lab_fn,
                 outname=f"bimodalidade_unidade_ato{suf}.png")

    # ---- Veredito ---------------------------------------------------------
    within_velho_omega = 1 - omz_esp_ato
    liq_velho = pm_velho["eta2_liquido"]
    print("\n" + "=" * 76)
    print(f"VEREDITO (malha = {args.malha.upper()})")
    print("=" * 76)
    print(f"  η²({lab_esp}) da separação jovem/velho: {etaz_esp:.1%} bruto | "
          f"ω²={omz_esp:.1%} | líquido de acaso={liq_velho:.1%}")
    print(f"  {lab_esp}(s) internamente bimodais (n≥{args.n_gmm_min}): {n_unid_bim}/{n_unid}")
    print(f"  Coexistência DENTRO das células {lab_esp}×ato (1−ω²): {within_velho_omega:.0%}")
    if within_velho_omega >= 0.5 and liq_velho < 0.25:
        print(f"  → Mesmo na malha {args.malha.upper()}, a geografia NÃO causa a bimodalidade:")
        print("    captura pouco da separação além do acaso; cada unidade é bimodal por dentro.")
        print("    Confirma: gradiente no PESO da mistura, não causação regional (D14).")
    else:
        print(f"  → Na malha {args.malha.upper()} o recorte espacial captura parcela relevante —")
        print("    a mesorregião era grossa demais. Reportar a parcela between/within.")


if __name__ == "__main__":
    main()
