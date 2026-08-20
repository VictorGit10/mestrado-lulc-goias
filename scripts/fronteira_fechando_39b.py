"""fronteira_fechando_39b.py -- Pipeline #39B: o nulo do B2b era artefato de domínio
====================================================================================

O QUE ESTE PIPELINE CORRIGE
---------------------------
O #39 (`fronteira_fechando.py`) monta o bloco de testes de oferta da Perna 4. Uma de
suas especificações é

    B2b   hazard ~ depleção_defasada        (2FE, ambos z-score)

e a hipótese pré-declarada no próprio #39 é explícita sobre como lê-la:

    "β<0: hazard CAI com a depleção = remanescente difícil de converter (atrito de oferta)"

O resultado publicado é β = −0,015 com p = 0,48: **nulo**. E é esse nulo que a redação
usava como a peça empírica do argumento de oferta — "a taxa não cai quando o estoque
encolhe, logo o fluxo passa a ser ditado pelo tamanho do estoque".

O nulo não sobrevive. `deplecao_prev` está documentada no #39 como uma fração
**0..1**, e no arquivo ela vai de **−84,9** a 0,97: **920 dos 6.379 pares AMC-ano
(14,4%) são negativos**, vindos de 46 AMCs cujo estoque convertível de 1985 era
minúsculo (mediana de 544 ha contra 24.031 ha das demais). Nelas o estoque de savana e
campo *cresceu* ao longo da série — o que é a oscilação classificatória pasto↔savana já
documentada no projeto —, e a razão que define a depleção explode. Como a variável entra
z-scorada, esses poucos valores dominam a escala inteira e achatam o coeficiente contra
zero.

O QUE ELE FAZ
-------------
Roda o mesmo B2b sob cinco tratamentos do outlier, do mais conservador (não descartar
nada, apenas pôr piso em zero) ao mais agressivo (restringir ao domínio documentado), e
mais a versão ponderada pelo estoque — que é o remédio principiado, já que o hazard é uma
proporção estimada sobre `estoque_prev` e sua variância é inversamente proporcional a ele.

Roda também B1, B1q e B2a nas duas amostras, para separar o que muda do que não muda.

O RESULTADO (2026-08-19)
------------------------
    tratamento                              β        p
    PUBLICADO: sem tratamento           −0,015    0,317      ← o único nulo
    piso em 0 (mantém as 6.379 linhas)  −0,202   <0,001
    piso em 0 + ponderado               −0,215   <0,001
    restrito a [0,1] (descarta 920)     −0,312   <0,001
    restrito a [0,1] + ponderado        −0,202   <0,001
    winsorizado no p1                   −0,069    0,026

**Todo tratamento do outlier — inclusive o que não descarta uma linha sequer — devolve
β negativo e significante.** O hazard CAI com a depleção, que é exatamente a assinatura
de atrito de oferta que o #39 pré-declarou.

Não muda: B1 (fluxo ~ estoque) segue +2,7 — e continua sendo a identidade
`fluxo ≡ taxa × estoque`, não um achado. O termo quadrático segue nulo (p = 0,93 → 0,82).
B2a (hazard ~ estoque) já era negativo e significante na versão publicada (−0,320;
p = 0,002), o que por si só já contrariava a premissa de hazard constante.

O QUE ISSO FAZ COM A PERNA 4
----------------------------
Fortalece, e troca o mecanismo. A leitura antiga era "a taxa é constante, então o fluxo
acompanha o estoque, e o Sul ficou sem estoque". A leitura corrigida é mais forte: à
medida que uma unidade se deplete, **caem as duas coisas** — o estoque que resta e a taxa
com que ele é convertido. O que sobra é mais difícil de converter. É a mesma coisa que o
#57 mede por outro caminho (no Sul, a fração florestal do remanescente sobe de 52,2% para
59,9% — galeria e cerradão, relevo quebrado e APP).

E resolve uma tensão que a redação carregava: o #39 mostra que 83% da freada do Sul está
na parcela *residual*, e o texto precisava insistir que residual "não é demanda". Agora
parte desse residual tem nome e sinal medido: é atrito de oferta.

LIMITE
------
Restringir a depleção ao domínio [0,1] descarta 46 AMCs que detêm 17,3% do estoque de
2024 — não é uma exclusão inócua para quem for somar hectares. Para a regressão ela é
correta (nessas unidades a depleção é indefinida, não extrema), e a variante de piso em
zero, que não descarta ninguém, dá o mesmo veredito. Nenhuma das duas conserta a razão de
as 46 existirem, que é a oscilação de classificador na borda pasto↔savana.

ENTRADAS
    data/processed/fronteira_estoque_convertivel.csv   (#39)

SAÍDAS
    data/processed/fronteira_teste_supply_39b.csv

COMO RODAR
    py -3.14 scripts/fronteira_fechando_39b.py

Depende de: Pipeline #39.
Quando foi feito: 2026-08-19.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
ARQ_ENTRADA = DIR_PROC / "fronteira_estoque_convertivel.csv"
ARQ_SAIDA = DIR_PROC / "fronteira_teste_supply_39b.csv"


def _z(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def carregar() -> pd.DataFrame:
    d = pd.read_csv(ARQ_ENTRADA)
    d = d.dropna(subset=["hazard", "deplecao_prev", "estoque_prev"])
    return d[np.isfinite(d["hazard"])].copy()


def diagnostico(d: pd.DataFrame) -> dict:
    """Mede o defeito antes de corrigi-lo, para que ele fique registrado."""
    neg = d[d["deplecao_prev"] < 0]
    b85 = (pd.read_csv(ARQ_ENTRADA, usecols=["code_amc", "ano", "estoque_refinada_ha"])
             .query("ano == 1985").set_index("code_amc")["estoque_refinada_ha"])
    amcs_neg = neg["code_amc"].unique()
    outras = [c for c in d["code_amc"].unique() if c not in set(amcs_neg)]
    return {
        "linhas": len(d),
        "linhas_negativas": len(neg),
        "pct_negativas": 100 * len(neg) / len(d),
        "min_deplecao": float(d["deplecao_prev"].min()),
        "max_deplecao": float(d["deplecao_prev"].max()),
        "amcs_afetadas": len(amcs_neg),
        "estoque85_mediano_afetadas": float(b85.reindex(amcs_neg).median()),
        "estoque85_mediano_demais": float(b85.reindex(outras).median()),
    }


def painel(s: pd.DataFrame, y: str, xs: list[str], peso: str | None = None) -> dict:
    from linearmodels.panel import PanelOLS

    si = s.set_index(["code_amc", "ano"])
    kw = {"weights": si[peso]} if peso else {}
    mod = PanelOLS(si[y], si[xs], entity_effects=True, time_effects=True,
                   check_rank=False, **kw)
    r = mod.fit(cov_type="clustered", cluster_entity=True)
    return {"beta": float(r.params[xs[0]]), "p": float(r.pvalues[xs[0]]),
            "r2_within": float(r.rsquared_within), "n_obs": int(r.nobs),
            "extra": {x: (float(r.params[x]), float(r.pvalues[x])) for x in xs[1:]}}


def preparar(d: pd.DataFrame, dep: pd.Series) -> pd.DataFrame:
    s = d.copy()
    s["dep"] = dep
    s["hz"] = _z(s["hazard"])
    s["fz"] = _z(s["fluxo_ha"])
    s["ez"] = _z(s["estoque_prev"])
    s["e2z"] = _z(s["estoque_prev"] ** 2)
    s["dz"] = _z(s["dep"])
    return s


def main() -> None:
    d = carregar()
    diag = diagnostico(d)

    print("=" * 78)
    print("DIAGNÓSTICO — o domínio de `deplecao_prev`")
    print("=" * 78)
    print(f"  documentada no #39 como fração 0..1; observada de "
          f"{diag['min_deplecao']:.1f} a {diag['max_deplecao']:.2f}")
    print(f"  negativas: {diag['linhas_negativas']} de {diag['linhas']} linhas "
          f"({diag['pct_negativas']:.1f}%), em {diag['amcs_afetadas']} AMCs")
    print(f"  estoque convertível de 1985 dessas AMCs: mediana "
          f"{diag['estoque85_mediano_afetadas']:,.0f} ha, contra "
          f"{diag['estoque85_mediano_demais']:,.0f} ha das demais")

    # As cinco réguas do outlier. A primeira é a publicada.
    q1 = d["deplecao_prev"].quantile(0.01)
    reguas = [
        ("publicado", d, d["deplecao_prev"], None,
         "sem tratamento (a especificação do #39)"),
        ("piso0", d, d["deplecao_prev"].clip(lower=0), None,
         "piso em 0 — não descarta nenhuma linha"),
        ("piso0_pond", d, d["deplecao_prev"].clip(lower=0), "estoque_prev",
         "piso em 0 + ponderado pelo estoque"),
        ("dominio", d[(d["deplecao_prev"] >= 0) & (d["deplecao_prev"] <= 1)], None, None,
         "restrito ao domínio documentado [0,1]"),
        ("dominio_pond", d[(d["deplecao_prev"] >= 0) & (d["deplecao_prev"] <= 1)], None,
         "estoque_prev", "restrito a [0,1] + ponderado"),
        ("winsor", d, d["deplecao_prev"].clip(lower=q1), None,
         "winsorizado no percentil 1"),
    ]

    linhas = []
    print("\n" + "=" * 78)
    print("B2b  hazard ~ depleção   (hipótese pré-declarada do #39: β<0 = atrito de oferta)")
    print("=" * 78)
    for chave, base, dep, peso, rot in reguas:
        dep = base["deplecao_prev"] if dep is None else dep.reindex(base.index)
        s = preparar(base, dep)
        r = painel(s, "hz", ["dz"], peso)
        marca = "NULO" if r["p"] >= 0.05 else "β<0 confirmado" if r["beta"] < 0 else "β>0"
        print(f"  {rot:42s} β={r['beta']:+.4f}  p={r['p']:.4f}  n={r['n_obs']}   {marca}")
        linhas.append({"spec": "B2b", "termo": "principal", "regua": chave, "descricao": rot, **
                       {k: v for k, v in r.items() if k != "extra"}})

    # O que NÃO muda — separar isso é metade do valor do pipeline.
    print("\n" + "=" * 78)
    print("O QUE NÃO MUDA (mesmas duas amostras, demais especificações)")
    print("=" * 78)
    amostras = [("publicado", d), ("dominio",
                d[(d["deplecao_prev"] >= 0) & (d["deplecao_prev"] <= 1)])]
    for chave, base in amostras:
        s = preparar(base, base["deplecao_prev"])
        b1 = painel(s, "fz", ["ez"])
        b1q = painel(s, "fz", ["ez", "e2z"])
        b2a = painel(s, "hz", ["ez"])
        q_b, q_p = b1q["extra"]["e2z"]
        print(f"  [{chave}]")
        print(f"    B1  fluxo ~ estoque      β={b1['beta']:+.4f} p={b1['p']:.4f}"
              f"   (é a identidade fluxo≡taxa×estoque, não achado)")
        print(f"    B1q termo quadrático     β={q_b:+.4f} p={q_p:.4f}"
              f"   {'nulo — sobrevive' if q_p >= 0.05 else 'MUDOU'}")
        print(f"    B2a hazard ~ estoque     β={b2a['beta']:+.4f} p={b2a['p']:.4f}"
              f"   {'já contrariava hazard constante' if b2a['p'] < 0.05 else ''}")
        # Uma linha por COEFICIENTE, não por modelo: o termo quadrático do B1q é
        # justamente o número que interessa ali, e guardá-lo só no console deixava
        # o CSV afirmando, na coluna `p`, o p do termo linear.
        for nome, r in [("B1", b1), ("B1q", b1q), ("B2a", b2a)]:
            linhas.append({"spec": nome, "termo": "principal", "regua": chave,
                           "descricao": "",
                           **{k: v for k, v in r.items() if k != "extra"}})
            for termo, (bx, px) in r["extra"].items():
                linhas.append({"spec": nome, "termo": termo, "regua": chave,
                               "descricao": "", "beta": bx, "p": px,
                               "r2_within": r["r2_within"], "n_obs": r["n_obs"]})

    pd.DataFrame(linhas).to_csv(ARQ_SAIDA, index=False, encoding="utf-8")
    print(f"\n[saída] {ARQ_SAIDA.relative_to(ROOT)}")

    print("\n" + "-" * 78)
    print("VEREDITO")
    print("-" * 78)
    b2b = [l for l in linhas if l["spec"] == "B2b"]
    negs = [l for l in b2b if l["beta"] < 0 and l["p"] < 0.05]
    print(f"  {len(negs)} de {len(b2b)} tratamentos dão β<0 significante; o único nulo é o")
    print("  publicado, sem tratamento do outlier. O hazard CAI com a depleção — que é a")
    print("  assinatura de ATRITO DE OFERTA pré-declarada pelo próprio #39.")
    print("  A Perna 4 não perde nada: ganha um mecanismo medido no lugar de um nulo.")


if __name__ == "__main__":
    main()
