"""remanescente_qualidade.py -- Pipeline #57: o remanescente do Sul é PIOR, ou só MENOR?
====================================================================================

PERGUNTA QUE RESPONDE
---------------------
A Perna 4 sustenta que a freada da conversão no Sul é de OFERTA DE TERRA: restou pouco
Cerrado a suprimir. O argumento se monta por eliminação -- a demanda estava no pico, a
proteção integral não estava no caminho, e a demanda de terra do Sul continuou existindo,
atendida por pasto já aberto.

Sobra uma alternativa que a eliminação não cobre, e que não é a de Reserva Legal/APP já
declarada. É a de COMPOSIÇÃO:

    e se o que restou no Sul não for apenas MENOS Cerrado, e sim Cerrado PIOR?

As duas leituras produzem a mesma série de estoque decrescente e a mesma queda de fluxo,
mas dizem coisas diferentes. "Acabou a terra" é esgotamento de quantidade; "o que sobrou
não presta" é seleção de qualidade -- a conversão comeu primeiro o que era fácil e barato
e parou quando encontrou encosta, solo raso e mata de galeria. A segunda leitura enfraquece
a extrapolação para o Norte, porque lá o remanescente ainda inclui a parte fácil.

ABORDAGEM
---------
Duas medidas de "pior", ambas com dado que já está em disco.

(A) QUALIDADE ENTRE AMCs -- aptidão média do estoque, ponderada pelo próprio estoque:
        apt_ponderada(região, ano) = Σ_i estoque_i(ano)·apt_i / Σ_i estoque_i(ano)
    Se a conversão comeu primeiro as AMCs aptas, essa média CAI ao longo da série, e cai
    mais onde a depleção foi maior (o Sul). Se ficar plana, o canal entre-AMCs está
    eliminado.

(B) QUALIDADE DENTRO da AMC -- composição fitofisionômica do que restou em pé:
        % floresta  vs  % savânica  vs  % campo  na vegetação natural remanescente
    A formação florestal em Goiás é sobretudo mata de galeria e cerradão: acompanha
    drenagem, ocupa relevo mais quebrado e é o que a Área de Preservação Permanente
    protege por definição. Se o remanescente do Sul migrou para floresta, o que sobrou é
    física e juridicamente mais difícil de converter, independentemente do tamanho.

(C) Como controle das duas, o hazard por aptidão: a propensão a converter é de fato maior
    onde a aptidão é alta? Se não for, o mecanismo de seleção por qualidade não opera e as
    medidas (A) e (B) não têm por que se mover.

LIMITE DECLARADO
----------------
A aptidão da Embrapa entra como MÉDIA POR AMC (1:500.000, 8.284 polígonos no estado).
A medida (A) enxerga, portanto, apenas a seleção ENTRE unidades; se a conversão escolheu
os melhores talhões DENTRO de cada AMC -- que é o mais provável --, ela é invisível aqui.
Um resultado nulo em (A) elimina o canal entre-AMCs e nada diz sobre o canal dentro. É por
isso que (B) entra: a composição por fitofisionomia é medida no pixel e não depende da
malha. Nenhuma das duas separa "difícil" de "proibido" -- para isso seria preciso o
cadastro ambiental integrado pixel a pixel, que o trabalho não tem.

A medida (B) tem um limite próprio, e ele restringe o que dela se pode afirmar. A
fração florestal do remanescente sobe no ESTADO INTEIRO (37,0% -> 42,5%), e o excesso
do Sul (+7,7 pontos) sobre a média estadual (+5,5) é de pouco mais de dois pontos. Uma
subida comum a todas as regiões é o que se esperaria tanto de seleção quanto de DERIVA
DE CLASSIFICADOR na borda savana <-> formação florestal -- resíduo que o projeto
documenta como não medido (a oscilação medida é a de pasto <-> savana). A TENDÊNCIA,
portanto, não separa as duas leituras. O que se afirma com segurança é o NÍVEL: em 2024
três quintos do remanescente do Sul são formação florestal, contra um terço no Norte --
e o Sul já entra na série em 52,2%, de modo que a diferença entre regiões é de
fisiografia antes de ser de história, e não depende da tendência para valer.

ENTRADAS
    data/processed/fronteira_estoque_convertivel.csv  (#39: estoque e hazard por AMC-ano)
    data/processed/aptidao_edafo_amc.csv              (#52: aptidão por AMC)
    data/processed/painel_amc_goias.parquet           (#25: classes de vegetação por AMC-ano)

SAÍDAS
    data/processed/remanescente_qualidade_aptidao.csv
    data/processed/remanescente_qualidade_composicao.csv
    outputs/fronteira_fechando/remanescente_qualidade.png

COMO RODAR
    py -3.14 scripts/remanescente_qualidade.py
    py -3.14 scripts/remanescente_qualidade.py --sem-figuras

Depende de: Pipelines #25, #39, #52.
Quando foi feito: 2026-08-19.
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
DIR_OUT  = ROOT / "outputs" / "fronteira_fechando"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_APT  = DIR_PROC / "remanescente_qualidade_aptidao.csv"
ARQ_COMP = DIR_PROC / "remanescente_qualidade_composicao.csv"

REGIOES = ["Sul", "Centro", "Norte"]
CORES   = {"Sul": "#c2185b", "Centro": "#e8920c", "Norte": "#2e7d32"}
ANOS_MARCO = [1985, 2000, 2019, 2024]

# Cortes mínimos de estoque para o teste (C). O primeiro é "sem corte" e reproduz
# a versão ingênua; os demais medem quanto dela era denominador degenerado.
# Ver a docstring de hazard_vs_aptidao e a decisão D29.
CORTES_ESTOQUE = [0, 100, 1000, 5000]


# ---------------------------------------------------------------------------
# (A) aptidão do estoque, ponderada pelo estoque
# ---------------------------------------------------------------------------

def aptidao_ponderada() -> pd.DataFrame:
    est = pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv",
                      usecols=["code_amc", "ano", "regiao", "estoque_refinada_ha", "hazard"])
    apt = pd.read_csv(DIR_PROC / "aptidao_edafo_amc.csv",
                      usecols=["code_amc", "apt_score_mean", "pct_apt_lavoura"])
    df = est.merge(apt, on="code_amc", how="inner")

    # Duas AMCs do Sul têm estoque ausente em parte dos anos (80 pares AMC-ano de
    # 6.640). Sem máscara, um único NaN de peso propaga para a média inteira do
    # grupo e apaga a região. Elas saem da média ponderada, e o n efetivo por
    # célula é reportado para que a exclusão fique visível.
    def agg(g: pd.DataFrame) -> pd.Series:
        ok = (g["estoque_refinada_ha"].notna() & g["apt_score_mean"].notna()
              & np.isfinite(g["estoque_refinada_ha"]))
        gg = g[ok]
        w = gg["estoque_refinada_ha"].to_numpy()
        tot = w.sum()
        if tot <= 0:
            return pd.Series({"apt_pond": np.nan, "pct_apt_pond": np.nan,
                              "estoque_mha": 0.0, "n_amc": 0, "n_amc_sem_dado": int((~ok).sum())})
        return pd.Series({
            "apt_pond": float(np.average(gg["apt_score_mean"], weights=w)),
            "pct_apt_pond": float(np.average(gg["pct_apt_lavoura"], weights=w)),
            "estoque_mha": tot / 1e6,
            "n_amc": int(ok.sum()), "n_amc_sem_dado": int((~ok).sum()),
        })

    reg = df.groupby(["regiao", "ano"], group_keys=True).apply(agg, include_groups=False).reset_index()
    est_uf = df.groupby("ano", group_keys=True).apply(agg, include_groups=False).reset_index()
    est_uf.insert(0, "regiao", "Goiás")
    return pd.concat([est_uf, reg], ignore_index=True)


# ---------------------------------------------------------------------------
# (B) composição fitofisionômica do remanescente
# ---------------------------------------------------------------------------

def composicao_remanescente() -> pd.DataFrame:
    pan = pd.read_parquet(
        DIR_PROC / "painel_amc_goias.parquet",
        columns=["code_amc", "ano", "lulc_floresta_nativa_ha",
                 "lulc_formacao_savanica_ha", "lulc_campo_nativo_ha"])
    reg = (pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv",
                       usecols=["code_amc", "regiao"]).drop_duplicates("code_amc"))
    pan = pan.merge(reg, on="code_amc", how="left")

    g = (pan.groupby(["regiao", "ano"])[["lulc_floresta_nativa_ha",
                                         "lulc_formacao_savanica_ha",
                                         "lulc_campo_nativo_ha"]].sum().reset_index())
    uf = (pan.groupby("ano")[["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                              "lulc_campo_nativo_ha"]].sum().reset_index())
    uf.insert(0, "regiao", "Goiás")
    g = pd.concat([uf, g], ignore_index=True)

    g["total_ha"] = g[["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                       "lulc_campo_nativo_ha"]].sum(axis=1)
    for c, nome in [("lulc_floresta_nativa_ha", "pct_floresta"),
                    ("lulc_formacao_savanica_ha", "pct_savanica"),
                    ("lulc_campo_nativo_ha", "pct_campo")]:
        g[nome] = 100 * g[c] / g["total_ha"]
    return g


# ---------------------------------------------------------------------------
# (C) o hazard depende da aptidão?
# ---------------------------------------------------------------------------

def hazard_vs_aptidao() -> pd.DataFrame:
    """Propensão a converter × aptidão, entre AMCs.

    O hazard é uma razão `fluxo/estoque_prev`, e o denominador tem cauda perigosa:
    690 dos 6.379 pares AMC-ano têm estoque abaixo de 100 ha, e os extremos são
    unidades com MENOS DE UM HECTARE, onde o hazard vai a 1,00 por construção.
    Como essas unidades se concentram no Sul depletado — que é justamente a região
    de aptidão alta —, deixá-las dentro infla o coeficiente na direção da hipótese.
    Por isso o teste roda numa grade de cortes mínimos de estoque, e o que se
    reporta é o que concorda entre eles (mesma disciplina da decisão D29).
    """
    from linearmodels.panel import PanelOLS

    est = pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv",
                      usecols=["code_amc", "ano", "regiao", "hazard", "estoque_prev"])
    apt = pd.read_csv(DIR_PROC / "aptidao_edafo_amc.csv",
                      usecols=["code_amc", "exp_apt_edafo"])
    df = est.merge(apt, on="code_amc", how="inner").dropna(
        subset=["hazard", "exp_apt_edafo", "estoque_prev"])
    df = df[np.isfinite(df["hazard"])]

    def ajusta(s: pd.DataFrame) -> dict | None:
        if s["code_amc"].nunique() < 15:
            return None
        si = s.set_index(["code_amc", "ano"])
        mod = PanelOLS(si["hazard"], si[["exp_apt_edafo"]], time_effects=True,
                       check_rank=False)
        r = mod.fit(cov_type="clustered", cluster_entity=True)
        return {"beta": float(r.params["exp_apt_edafo"]),
                "se": float(r.std_errors["exp_apt_edafo"]),
                "p": float(r.pvalues["exp_apt_edafo"]), "n_obs": int(r.nobs)}

    linhas = []
    for lim in CORTES_ESTOQUE:
        base = df[df["estoque_prev"] >= lim]
        for escopo in ["Goiás", *REGIOES]:
            s = base if escopo == "Goiás" else base[base["regiao"] == escopo]
            r = ajusta(s)
            if r:
                linhas.append({"escopo": escopo, "corte_estoque_ha": lim, **r})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------

def figura(apt: pd.DataFrame, comp: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))
    for r in REGIOES:
        s = apt[apt["regiao"] == r].sort_values("ano")
        base = s[s["ano"] == 1985]["apt_pond"].iloc[0]
        ax1.plot(s["ano"], s["apt_pond"] - base, color=CORES[r], lw=1.9, label=r)
    ax1.axhline(0, color="0.4", lw=1.0, ls="--")
    ax1.set_title("(a) Aptidão do estoque ainda exposto\n(variação em relação a 1985, escala ordinal)",
                  fontsize=9.5)
    ax1.set_ylabel("Δ aptidão média ponderada pelo estoque")
    ax1.legend(frameon=False, fontsize=8)
    ax1.grid(alpha=0.25)

    for r in REGIOES:
        s = comp[comp["regiao"] == r].sort_values("ano")
        ax2.plot(s["ano"], s["pct_floresta"], color=CORES[r], lw=1.9, label=r)
    ax2.set_title("(b) Fração florestal do remanescente\n(galeria e cerradão: relevo quebrado e APP)",
                  fontsize=9.5)
    ax2.set_ylabel("% da vegetação natural em formação florestal")
    ax2.legend(frameon=False, fontsize=8)
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(DIR_OUT / "remanescente_qualidade.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'remanescente_qualidade.png').relative_to(ROOT)}")


def main(sem_figuras: bool = False) -> None:
    apt = aptidao_ponderada()
    comp = composicao_remanescente()
    apt.to_csv(ARQ_APT, index=False, encoding="utf-8")
    comp.to_csv(ARQ_COMP, index=False, encoding="utf-8")

    print("=" * 78)
    print("(A) APTIDÃO MÉDIA DO ESTOQUE AINDA EXPOSTO — ponderada pelo estoque")
    print("=" * 78)
    piv = apt.pivot_table(index="ano", columns="regiao", values="apt_pond")
    print(piv.loc[ANOS_MARCO].round(3).to_string())
    print("\nΔ 1985→2024 (escala ordinal 1..6, maior = mais apto):")
    for r in ["Goiás", *REGIOES]:
        s = apt[apt["regiao"] == r].set_index("ano")["apt_pond"]
        d = s.loc[2024] - s.loc[1985]
        print(f"   {r:8s}  {s.loc[1985]:.3f} → {s.loc[2024]:.3f}   Δ = {d:+.3f}")

    print("\n" + "=" * 78)
    print("(B) COMPOSIÇÃO DO REMANESCENTE — % em formação florestal")
    print("=" * 78)
    pivc = comp.pivot_table(index="ano", columns="regiao", values="pct_floresta")
    print(pivc.loc[ANOS_MARCO].round(2).to_string())
    print("\nΔ 1985→2024 (pontos percentuais):")
    for r in ["Goiás", *REGIOES]:
        s = comp[comp["regiao"] == r].set_index("ano")["pct_floresta"]
        print(f"   {r:8s}  {s.loc[1985]:5.2f}% → {s.loc[2024]:5.2f}%   Δ = {s.loc[2024]-s.loc[1985]:+.2f} p.p.")

    print("\n" + "=" * 78)
    print("(C) O HAZARD DEPENDE DA APTIDÃO? (entre AMCs, efeito fixo de ano)")
    print("=" * 78)
    print("    grade de cortes mínimos de estoque — o hazard é razão, e o denominador")
    print("    degenera nas unidades quase sem estoque (decisão D29)")
    hz = hazard_vs_aptidao()
    piv = hz.pivot_table(index="escopo", columns="corte_estoque_ha", values="beta")
    pvp = hz.pivot_table(index="escopo", columns="corte_estoque_ha", values="p")
    for escopo in ["Goiás", *REGIOES]:
        if escopo not in piv.index:
            continue
        cel = "  ".join(
            f"{lim:>5}ha {piv.loc[escopo, lim]:+.5f}{'*' if pvp.loc[escopo, lim] < 0.05 else ' '}"
            for lim in CORTES_ESTOQUE if lim in piv.columns)
        print(f"   {escopo:8s} {cel}")
    print("    (* = p<0,05). O SINAL sobrevive a toda a grade; a MAGNITUDE do corte 0")
    print("    é inflada pelo denominador — citar a de um corte defensável.")

    print("\n" + "-" * 78)
    print("LEITURA")
    print("-" * 78)
    sul = apt[apt["regiao"] == "Sul"].set_index("ano")["apt_pond"]
    nor = apt[apt["regiao"] == "Norte"].set_index("ano")["apt_pond"]
    d_sul, d_nor = sul.loc[2024] - sul.loc[1985], nor.loc[2024] - nor.loc[1985]
    print(f"   Aptidão do estoque: Sul {d_sul:+.3f} vs Norte {d_nor:+.3f} em 40 anos.")
    fs = comp[comp["regiao"] == "Sul"].set_index("ano")["pct_floresta"]
    fn = comp[comp["regiao"] == "Norte"].set_index("ano")["pct_floresta"]
    print(f"   Fração florestal:   Sul {fs.loc[2024]-fs.loc[1985]:+.2f} p.p. vs "
          f"Norte {fn.loc[2024]-fn.loc[1985]:+.2f} p.p.")

    print(f"\n[saída] {ARQ_APT.relative_to(ROOT)}")
    print(f"[saída] {ARQ_COMP.relative_to(ROOT)}")

    if not sem_figuras:
        figura(apt, comp)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sem-figuras", action="store_true")
    main(**vars(ap.parse_args()))
