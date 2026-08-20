"""fronteira_fechando_39b.py -- Pipeline #39B: o nulo do B2b era artefato de domínio
====================================================================================

O QUE ESTE PIPELINE CORRIGE
---------------------------
O #39 (`fronteira_fechando.py`) monta o bloco de testes de oferta da Perna 4. Uma de
suas especificações é

    B2b   hazard ~ depleção_defasada        (2FE, ambos z-score)

e a hipótese pré-declarada no próprio #39 é explícita sobre como lê-la:

    "β<0: hazard CAI com a depleção = remanescente difícil de converter (atrito de oferta)"

O resultado publicado é β = −0,0152 com p = 0,4809: **nulo**. E é esse nulo que a
redação usava como a peça empírica do argumento de oferta — "a taxa não cai quando o
estoque encolhe, logo o fluxo passa a ser ditado pelo tamanho do estoque".

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
Uma grade fatorial, para que o resultado não dependa de uma escolha:

    4 tratamentos do regressor  ×  2 ponderações  ×  2 amostras  =  16 células

**Tratamentos.** `publicado` (nenhum), `piso0` (piso em zero, não descarta nenhuma
linha), `dominio` (restrito a [0,1]) e `winsor` (percentil 1). O `winsor` entra de
propósito como o *contra-exemplo*: é o remédio-padrão para valor extremo, e ele **não**
resolve, porque o defeito não é de cauda e sim de domínio — winsorizado no p1 o
regressor ainda desce a −4,8, oitenta vezes fora da escala que o define.

**Ponderação.** O hazard é uma proporção estimada sobre `estoque_prev`, e a variância de
uma proporção é inversa ao denominador: ponderar pelo estoque é o remédio principiado, e
é independente do tratamento do regressor — ele age sobre o *desfecho*, não sobre a
variável defeituosa.

**Amostras.** Todas as AMC-ano, e o corte `estoque_prev ≥ 1.000 ha`. O corte não é novo:
é o mesmo que o #57 adotou para o hazard, porque abaixo dele a razão degenera (há AMC-ano
com menos de 1 ha de estoque, onde hazard = 1,00 por construção). Rodar as duas amostras
separa dois defeitos que se somavam: o do **regressor** (domínio) e o do **desfecho**
(razão sobre denominador minúsculo).

**Duas réguas de erro-padrão, sempre lado a lado.** O #39 usa cluster duplo
`entidade+ano` sempre que há efeito fixo de ano, porque o choque do ano é comum às AMCs
— e, no caso, porque o próprio trabalho documenta dependência espacial (#41: I de Moran
significativo em 125/140 testes). Reportar aqui apenas o cluster de entidade seria trocar
a régua do pipeline-pai por uma mais frouxa no meio da auditoria, que é exatamente o
defeito que esta série de pipelines existe para caçar. As duas são reportadas em colunas
separadas e **nunca** comparadas entre si como se fossem a mesma medida; a régua do #39 é
a que decide.

**Unidade comparável.** Os β em z **não são comparáveis entre tratamentos**: o desvio-
padrão do regressor vai de 0,21 (no domínio) a 3,54 (sem tratamento), dezessete vezes.
Comparar −0,07 com −0,31 nessas condições é comparar réguas de tamanhos diferentes. Por
isso cada célula reporta também o coeficiente em **unidade natural** — pontos de hazard
por 0,1 de depleção —, que é o que permite dizer que dois tratamentos concordam. A
conversão é conferida no próprio código contra a regressão em unidade bruta.

O RESULTADO (2026-08-20)
------------------------
Amostra com o corte de 1.000 ha, régua do #39 (cluster entidade+ano):

    tratamento          peso         β (z)   β/0,1 dep       p      R²w
    publicado           --          −0,291    −0,00117   0,262    0,030
    publicado           ponderado   −1,097    −0,00440  <0,001    0,182
    piso em 0           --          −0,440    −0,00576  <0,001    0,134
    piso em 0           ponderado   −0,400    −0,00524  <0,001    0,188
    domínio [0,1]       --          −0,452    −0,00596  <0,001    0,172
    domínio [0,1]       ponderado   −0,397    −0,00524  <0,001    0,197
    winsor p1           --          −0,444    −0,00260   0,009    0,066
    winsor p1           ponderado   −0,808    −0,00473  <0,001    0,185

**O sinal é negativo nas 16 células.** Sob a régua do #39, 11 das 16 cruzam 5%. A única
célula que não cruza em **nenhuma** das duas amostras é a publicada — sem tratamento e sem
peso, isto é, a que não corrige nem o regressor nem o desfecho. Corrigido qualquer um dos
dois, o sinal aparece; corrigidos os dois, ele é forte. Onde o regressor é posto dentro do
domínio que o define, os tratamentos convergem para a mesma medida em unidade natural —
entre **0,5 e 0,8 ponto percentual de hazard por 0,1 de depleção** — e o R² *within*
sobe de ~0,03 para 0,13–0,20. O hazard CAI com a depleção, que é exatamente a assinatura
de atrito de oferta que o #39 pré-declarou.

Não muda: B1 (fluxo ~ estoque) segue +2,7 — e continua sendo a identidade
`fluxo ≡ taxa × estoque`, não um achado. O termo quadrático segue nulo nas duas amostras.

Muda, e para menos, o **B2a** (hazard ~ estoque). O #39 publica β=−0,3194 com **p=0,0917**,
que sob a régua dele **não cruza 5%** — o valor impresso no console abaixo é lido do CSV do
#39, e não reestimado, justamente para que a afirmação sobre "o que o #39 já dizia" não
possa divergir do que ele diz. E sob o corte de 1.000 ha o coeficiente praticamente
desaparece (β=−0,057; p=0,74): o B2a era carregado pelas AMCs de estoque minúsculo, as
mesmas que produzem o defeito do B2b pelo outro lado. O bloco de oferta, portanto, **não**
tem um segundo resultado contra a premissa de hazard constante; tem um só, que é o B2b
corrigido — e dizer o contrário seria contar a mesma AMC duas vezes.

O QUE ISSO FAZ COM A PERNA 4
----------------------------
Fortalece, e troca o mecanismo. A leitura antiga era "a taxa é constante, então o fluxo
acompanha o estoque, e o Sul ficou sem estoque" — que além de tudo aceitava a hipótese
nula, coisa que a régua de nulo do próprio trabalho proíbe. A leitura corrigida é mais
forte: à medida que uma unidade se deplete, **caem as duas coisas** — o estoque que resta
e a taxa com que ele é convertido. O que sobra é mais difícil de converter. É a mesma
coisa que o #57 mede por outro caminho (no Sul, a fração florestal do remanescente sobe
de 52,2% para 59,9% — galeria e cerradão, relevo quebrado e APP).

E resolve uma tensão que a redação carregava: o #39 mostra que 83% da freada do Sul está
na parcela *residual*, e o texto precisava insistir que residual "não é demanda". Agora
parte desse residual tem nome e sinal medido: é atrito de oferta.

Há ainda um argumento a favor do sinal que o desenho oferece de graça. Hazard e depleção
compartilham `estoque_prev` — no denominador de um, no numerador (com sinal trocado) do
outro. O acoplamento mecânico entre as duas variáveis, portanto, empurra o coeficiente
para **cima**. Achar β<0 é achar contra a aritmética do desenho, não a favor dela.

LIMITES
-------
1. O coeficiente em unidade natural é uma inclinação **within**: descreve o que acontece
   a uma unidade enquanto ela se deplete, líquido do ano. A comparação transversal bruta
   entre AMCs mais e menos depletadas é aproximadamente plana — composição de unidades e
   de anos, que os efeitos fixos absorvem. Uma coisa não desmente a outra, e ler a
   inclinação como diferença entre regiões seria erro.
2. Restringir a depleção ao domínio [0,1] descarta 46 AMCs que detêm 17,3% do estoque de
   2024 — não é uma exclusão inócua para quem for somar hectares. Para a regressão ela é
   correta (nessas unidades a depleção é indefinida, não extrema), e a variante de piso em
   zero, que não descarta ninguém, dá o mesmo veredito.
3. Nenhum tratamento conserta a razão de as 46 existirem, que é a oscilação de
   classificador na borda pasto↔savana.

ENTRADAS
    data/processed/fronteira_estoque_convertivel.csv   (#39)
    data/processed/fronteira_teste_supply.csv          (#39: os números publicados)

SAÍDAS
    data/processed/fronteira_teste_supply_39b.csv

COMO RODAR
    py -3.14 scripts/fronteira_fechando_39b.py

Depende de: Pipeline #39.
Quando foi feito: 2026-08-19 (grade fatorial e segunda régua de erro-padrão: 2026-08-20).
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
ARQ_PUBLICADO = DIR_PROC / "fronteira_teste_supply.csv"
ARQ_SAIDA = DIR_PROC / "fronteira_teste_supply_39b.csv"

CORTE_ESTOQUE = 1000.0   # ha; o mesmo corte que o #57 adota para o hazard


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
    """Ajusta a especificação e devolve as DUAS réguas de erro-padrão.

    `p_entidade_ano` é a régua do #39 (`_painel_fe`, cluster duplo sempre que há efeito
    fixo de ano) e é a que decide. `p_entidade` fica ao lado porque é mais frouxa e
    porque mostrar as duas é o que impede a régua de ser trocada em silêncio. As duas
    NUNCA são comparadas entre si como se fossem a mesma medida.
    """
    from linearmodels.panel import PanelOLS

    si = s.set_index(["code_amc", "ano"])
    kw = {"weights": si[peso]} if peso else {}
    mod = PanelOLS(si[y], si[xs], entity_effects=True, time_effects=True,
                   check_rank=False, **kw)
    r_ent = mod.fit(cov_type="clustered", cluster_entity=True)
    r_2w = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    return {
        "beta": float(r_ent.params[xs[0]]),
        "p_entidade": float(r_ent.pvalues[xs[0]]),
        "p_entidade_ano": float(r_2w.pvalues[xs[0]]),
        "r2_within": float(r_ent.rsquared_within),
        "n_obs": int(r_ent.nobs),
        "extra": {x: (float(r_ent.params[x]), float(r_ent.pvalues[x]),
                      float(r_2w.pvalues[x])) for x in xs[1:]},
    }


def tratar(chave: str, d: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Devolve (amostra, regressor tratado). O tratamento vem DEPOIS do corte de
    amostra, para que o percentil do winsor seja o da amostra em que ele opera."""
    dep = d["deplecao_prev"]
    if chave == "publicado":
        return d, dep
    if chave == "piso0":
        return d, dep.clip(lower=0)
    if chave == "winsor":
        return d, dep.clip(lower=dep.quantile(0.01))
    if chave == "dominio":
        b = d[(dep >= 0) & (dep <= 1)]
        return b, b["deplecao_prev"]
    raise ValueError(chave)


def preparar(base: pd.DataFrame, dep: pd.Series) -> tuple[pd.DataFrame, float]:
    """Padroniza e devolve também o fator que converte β(z) em unidade natural:
    Δhazard por 1 unidade de depleção = β(z) · sd(hazard) / sd(depleção)."""
    s = base.copy()
    s["dz"] = _z(dep.reindex(base.index))
    s["hz"] = _z(s["hazard"])
    fator = float(s["hazard"].std(ddof=0)) / float(dep.reindex(base.index).std(ddof=0))
    return s, fator


def conferir_unidade(d: pd.DataFrame) -> None:
    """A conversão de β(z) para unidade natural é algébrica; esta função a confere
    contra a regressão em unidade bruta, para que o número não dependa da álgebra
    estar certa no comentário."""
    from linearmodels.panel import PanelOLS

    base, dep = tratar("piso0", d[d["estoque_prev"] >= CORTE_ESTOQUE])
    s, fator = preparar(base, dep)
    beta_convertido = painel(s, "hz", ["dz"])["beta"] * fator

    b = base.copy()
    b["dep_bruta"] = dep.reindex(base.index)
    si = b.set_index(["code_amc", "ano"])
    r = PanelOLS(si["hazard"], si[["dep_bruta"]], entity_effects=True, time_effects=True,
                 check_rank=False).fit(cov_type="clustered", cluster_entity=True)
    beta_bruto = float(r.params["dep_bruta"])

    if not np.isclose(beta_convertido, beta_bruto, rtol=1e-6):
        raise AssertionError(
            f"conversão de unidade não bate: {beta_convertido:.8f} × {beta_bruto:.8f}")
    print(f"  [conferido] β em unidade natural bate com a regressão bruta "
          f"({beta_bruto:+.5f} por unidade de depleção)")


TRATAMENTOS = [
    ("publicado", "sem tratamento (a do #39)"),
    ("piso0", "piso em 0 (não descarta linha)"),
    ("dominio", "domínio documentado [0,1]"),
    ("winsor", "winsor p1 (não põe no domínio)"),
]
AMOSTRAS = [
    ("todas", 0.0, "todas as AMC-ano"),
    ("corte1k", CORTE_ESTOQUE, f"estoque_prev ≥ {CORTE_ESTOQUE:,.0f} ha (o corte do #57)"),
]


def main() -> None:
    d = carregar()
    diag = diagnostico(d)

    print("=" * 88)
    print("DIAGNÓSTICO — o domínio de `deplecao_prev`")
    print("=" * 88)
    print(f"  documentada no #39 como fração 0..1; observada de "
          f"{diag['min_deplecao']:.1f} a {diag['max_deplecao']:.2f}")
    print(f"  negativas: {diag['linhas_negativas']} de {diag['linhas']} linhas "
          f"({diag['pct_negativas']:.1f}%), em {diag['amcs_afetadas']} AMCs")
    print(f"  estoque convertível de 1985 dessas AMCs: mediana "
          f"{diag['estoque85_mediano_afetadas']:,.0f} ha, contra "
          f"{diag['estoque85_mediano_demais']:,.0f} ha das demais")
    conferir_unidade(d)

    linhas: list[dict] = []
    print("\n" + "=" * 88)
    print("B2b  hazard ~ depleção   (hipótese pré-declarada do #39: β<0 = atrito de oferta)")
    print("=" * 88)
    print("  p(ent+ano) é a régua do #39 e é a que decide; p(ent) fica ao lado porque é")
    print("  mais frouxa — as duas não são a mesma medida e não se comparam entre si.\n")
    for chave_am, corte, rot_am in AMOSTRAS:
        base_am = d[d["estoque_prev"] >= corte]
        print(f"  [{rot_am}]   n_AMC={base_am['code_amc'].nunique()}")
        print(f"    {'tratamento':31s} {'peso':10s} {'β(z)':>8s} {'β/0,1dep':>10s} "
              f"{'p(ent)':>8s} {'p(ent+ano)':>11s} {'R²w':>7s} {'n':>6s}")
        for chave_tr, rot_tr in TRATAMENTOS:
            base, dep = tratar(chave_tr, base_am)
            s, fator = preparar(base, dep)
            for peso in (None, "estoque_prev"):
                r = painel(s, "hz", ["dz"], peso)
                nat = r["beta"] * fator * 0.1
                cruza = "" if r["p_entidade_ano"] < 0.05 else "   ← não cruza 5%"
                print(f"    {rot_tr:31s} {('ponderado' if peso else '--'):10s} "
                      f"{r['beta']:+8.4f} {nat:+10.5f} {r['p_entidade']:8.4f} "
                      f"{r['p_entidade_ano']:11.4f} {r['r2_within']:7.4f} "
                      f"{r['n_obs']:6d}{cruza}")
                linhas.append({"spec": "B2b", "termo": "principal", "amostra": chave_am,
                               "tratamento": chave_tr, "peso": "estoque" if peso else "",
                               "descricao": rot_tr, "beta_z": r["beta"],
                               "beta_por_01_deplecao": nat,
                               "p_entidade": r["p_entidade"],
                               "p_entidade_ano": r["p_entidade_ano"],
                               "r2_within": r["r2_within"], "n_obs": r["n_obs"]})
        print()

    # O que NÃO muda — separar isso é metade do valor do pipeline.
    print("=" * 88)
    print("O QUE NÃO MUDA (demais especificações do bloco de oferta)")
    print("=" * 88)
    pub = pd.read_csv(ARQ_PUBLICADO)
    b2a_pub = pub[pub["spec"].str.startswith("B2a")].iloc[0]
    print(f"  Publicado pelo #39, lido do CSV dele (régua entidade+ano):")
    print(f"    B2a hazard ~ estoque     β={b2a_pub['beta']:+.4f} p={b2a_pub['p']:.4f}"
          f"   {'cruza 5%' if b2a_pub['p'] < 0.05 else 'NÃO cruza 5% — negativo, mas não significante'}")
    print()
    for chave_am, corte, rot_am in AMOSTRAS:
        base = d[d["estoque_prev"] >= corte].copy()
        s, _ = preparar(base, base["deplecao_prev"])
        s["fz"] = _z(s["fluxo_ha"])
        s["ez"] = _z(s["estoque_prev"])
        s["e2z"] = _z(s["estoque_prev"] ** 2)
        b1 = painel(s, "fz", ["ez"])
        b1q = painel(s, "fz", ["ez", "e2z"])
        b2a = painel(s, "hz", ["ez"])
        q_b, _, q_p2 = b1q["extra"]["e2z"]
        print(f"  [{rot_am}]")
        print(f"    B1  fluxo ~ estoque      β={b1['beta']:+.4f} p={b1['p_entidade_ano']:.4f}"
              f"   (é a identidade fluxo≡taxa×estoque, não achado)")
        print(f"    B1q termo quadrático     β={q_b:+.4f} p={q_p2:.4f}"
              f"   {'nulo — sobrevive' if q_p2 >= 0.05 else 'MUDOU'}")
        print(f"    B2a hazard ~ estoque     β={b2a['beta']:+.4f} p={b2a['p_entidade_ano']:.4f}")
        # Uma linha por COEFICIENTE, não por modelo: o termo quadrático do B1q é
        # justamente o número que interessa ali, e guardá-lo só no console deixava
        # o CSV afirmando, na coluna `p`, o p do termo linear.
        for nome, r in [("B1", b1), ("B1q", b1q), ("B2a", b2a)]:
            linhas.append({"spec": nome, "termo": "principal", "amostra": chave_am,
                           "tratamento": "", "peso": "", "descricao": "",
                           "beta_z": r["beta"], "beta_por_01_deplecao": np.nan,
                           "p_entidade": r["p_entidade"],
                           "p_entidade_ano": r["p_entidade_ano"],
                           "r2_within": r["r2_within"], "n_obs": r["n_obs"]})
            for termo, (bx, px1, px2) in r["extra"].items():
                linhas.append({"spec": nome, "termo": termo, "amostra": chave_am,
                               "tratamento": "", "peso": "", "descricao": "",
                               "beta_z": bx, "beta_por_01_deplecao": np.nan,
                               "p_entidade": px1, "p_entidade_ano": px2,
                               "r2_within": r["r2_within"], "n_obs": r["n_obs"]})
        print()

    pd.DataFrame(linhas).to_csv(ARQ_SAIDA, index=False, encoding="utf-8")
    print(f"[saída] {ARQ_SAIDA.relative_to(ROOT)}")

    print("\n" + "-" * 88)
    print("VEREDITO")
    print("-" * 88)
    b2b = [l for l in linhas if l["spec"] == "B2b"]
    neg = [l for l in b2b if l["beta_z"] < 0]
    sig = [l for l in b2b if l["beta_z"] < 0 and l["p_entidade_ano"] < 0.05]
    # A célula que interessa isolar é a que falha nas DUAS amostras: falhar em uma só
    # significa que o outro defeito, sozinho, já bastava para esconder o sinal.
    por_celula: dict[tuple[str, str], list[bool]] = {}
    for l in b2b:
        por_celula.setdefault((l["tratamento"], l["peso"]), []).append(
            l["p_entidade_ano"] < 0.05)
    nunca = sorted(k for k, v in por_celula.items() if not any(v))
    print(f"  β<0 em {len(neg)} das {len(b2b)} células; cruza 5% sob a régua do #39 em "
          f"{len(sig)} delas.")
    rot = ", ".join(f"{tr}{'/ponderado' if pe else ' sem peso'}" for tr, pe in nunca)
    print(f"  Não cruza em NENHUMA das duas amostras: {rot} — a célula que não corrige")
    print("  nem o regressor (domínio) nem o desfecho (denominador). Corrigido um dos")
    print("  dois, o sinal aparece; corrigidos os dois, ele é forte. Onde o regressor é")
    print("  posto no domínio, os tratamentos convergem em unidade natural.")
    print("  O hazard CAI com a depleção — que é a assinatura de ATRITO DE OFERTA")
    print("  pré-declarada pelo próprio #39. A Perna 4 ganha um mecanismo medido no")
    print("  lugar de um nulo que, além de artefato, era lido como aceitação da nula.")


if __name__ == "__main__":
    main()
