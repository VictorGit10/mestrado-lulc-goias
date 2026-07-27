"""intensificacao_vs_composicao.py — #22B: o β<0 do #22 é intensificação ou composição?
=========================================================================================

O achado-manchete do [#22](../Textos/pipelines/22_correlacoes_painel.md) é o β<0 de
`Δ Agricultura ~ Δ VA agro`: onde o valor adicionado agropecuário cresce, a área agrícola
não acompanha. Ele é **robusto** (sobrevive a AMC, a multivariado, a VIF e ao termo espacial
do #49) — mas "robusto" não é "interpretado". Duas histórias substantivamente diferentes
produzem exatamente o mesmo sinal negativo:

  (A) INTENSIFICAÇÃO *within*  — dentro de um mesmo município, o valor sobe sem que a área
      cresça. É ganho de produtividade, e é a leitura que o doc vinha adotando.

  (B) COMPOSIÇÃO entre unidades — a expansão de área acontece ONDE a produtividade é baixa
      (fronteira) e o crescimento de valor acontece ONDE a área já está travada (núcleo).
      Nenhum município intensificou; a correlação negativa é o retrato de dois grupos
      diferentes de municípios.

O 2-way FE do #22 **não separa as duas**. O efeito fixo de entidade remove o *nível* de cada
município e o de ano remove o choque comum — mas se os grupos **respondem de forma diferente
ao mesmo choque anual** (fronteira: área ↑; núcleo: valor ↑), o desvio em torno da média do ano
é positivo em área num grupo e positivo em valor no outro, e a covariância pooled sai negativa
**sem que nenhum grupo tenha β<0 por dentro**. Essa composição é *dinâmica* e o FE de entidade
não a toca — só o FE de entidade removeria a composição *estática* (níveis médios).

## O teste

Dois desenhos, um interpretável e um decisivo.

**Subamostras** (Bloco B) — o que o doc do #22 propõe. Roda o mesmo modelo dentro de grupos
homogêneos. Interpretável, mas perde poder e não é prova: grupos ainda são heterogêneos por
dentro.

**FE de grupo × ano** (Bloco C) — o teste decisivo. Troca γ_t por γ_gt: remove a média de
**cada grupo em cada ano**, que é exatamente o canal pelo qual (B) opera. O que sobra é só a
variação de um município contra os do *seu próprio grupo* naquele ano. Se o β sobrevive, ele
é within-grupo e a leitura (A) se sustenta; se colapsa, era composição.

### Regra de decisão — PRÉ-DECLARADA (impressa antes dos resultados)

| Evidência | Veredito |
|---|---|
| β<0 sig. em **todos** os grupos **e** sobrevive ao γ_gt (|Δβ| < 50%, mantém sinal e sig.) | **(A)** intensificação |
| β<0 no pooled mas **ns/nulo** dentro dos grupos **ou** colapsa sob γ_gt | **(B)** composição |
| Sobrevive ao γ_gt mas com magnitude muito menor, ou sig. em parte dos grupos | **misto** — reportar as duas fontes |

A regra é fixada antes de rodar por causa da D14: com muitos cortes possíveis, escolher o
corte depois de ver o resultado é garimpo.

> **Defeito da regra, encontrado ao rodar (registrado, não corrigido em silêncio).** Exigir
> `p<0,05` sob γ_gt confunde **o efeito colapsar** (que é o que evidencia (B)) com **o teste
> perder poder** (γ_gt queima muitos graus de liberdade — 3 grupos × T anos de FE a mais).
> Sob (B), o β deveria ir **a zero**, não apenas perder estrelas com a magnitude intacta.
> O script agora reporta as duas leituras lado a lado, com a pós-hoc **rotulada como tal**:
> a pré-declarada continua valendo como registro, e a de magnitude é a que interpreta.

## O que este script NÃO faz

Não estabelece causalidade — nada aqui muda o que o #22 já dizia sobre isso (é FE + associação,
não identificação). A pergunta é **de onde vem o sinal do β**, não se ele é causal.

Não decide se a intensificação é "boa". Ganho de produtividade e travamento de fronteira
produzem o mesmo β<0 sob a leitura (A); separar isso exigiria produtividade medida.

**Cuidado com o R²-within** (a confusão que o doc do #22 registra): aquela discussão é sobre
*decomposição de variância* — quanto do movimento mora dentro das unidades. Não responde a
esta pergunta e não licencia a resposta.

Saídas:
    outputs/correlacoes/intensificacao_composicao.csv   — todos os modelos, um por linha
    outputs/correlacoes/intensificacao_composicao.md    — veredito legível

Como rodar:
    py -3.14 scripts/intensificacao_vs_composicao.py
    py -3.14 scripts/intensificacao_vs_composicao.py --nivel amc   # robustez (D11)
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from correlacoes_painel import JANELA_ESTENDIDA, JANELA_PLENA, preparar_painel  # noqa: E402
from deslocamento_espacial import MESO_NORTE, MESO_SUL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# O par-manchete. Os dois de pastagem entram como contexto: se o colapso sob γ_gt for
# generalizado, ele é um artefato do desenho e não um diagnóstico sobre o M1.
PAR_ALVO = ("agricultura_delta_mha", "delta_va_agro_real_rs")
PARES_CONTEXTO = [
    ("pastagem_delta_mha", "delta_sicor_total_real_rs"),   # canal crédito→pasto (#49 M2)
    ("pastagem_delta_mha", "delta_va_agro_real_rs"),       # substituição local (#49 M3)
]


def regiao_de_meso(m: str) -> str:
    """Mesma partição do #39 (Sul / Centro / Norte) — reusada, não redefinida."""
    if m in MESO_SUL:
        return "Sul"
    if m in MESO_NORTE:
        return "Norte"
    return "Centro"


# ---------------------------------------------------------------------------
# 1. Grupos: região (#39) e share agrícola baseline
# ---------------------------------------------------------------------------

def anexar_grupos(df: pd.DataFrame, nivel: str, janela: tuple[int, int]) -> pd.DataFrame:
    """Anexa `regiao` e `tercil_agric` ao painel.

    O share agrícola baseline é lido no ano **anterior** ao início da janela, para que a
    variável que define o grupo não seja função do período estimado (senão o grupo já
    carrega o desfecho).
    """
    df = df.copy()

    # --- região ---
    if nivel == "amc":
        # a malha AMC não tem meso direto; herda pelo município representante
        cw = pd.read_csv(DIR_DATA / "amc_crosswalk_goias.csv")
        meso = pd.read_csv(DIR_DATA / "mapeamento_mesorregioes.csv")
        cw = cw.merge(meso[["cd_mun", "nm_meso"]], on="cd_mun", how="left")
        # meso majoritária dentro da AMC
        dom = (cw.groupby(["code_amc", "nm_meso"]).size().reset_index(name="n")
                 .sort_values("n", ascending=False)
                 .drop_duplicates("code_amc")[["code_amc", "nm_meso"]])
        dom = dom.rename(columns={"code_amc": "cd_mun"})
        df = df.merge(dom, on="cd_mun", how="left")
    else:
        meso = pd.read_csv(DIR_DATA / "mapeamento_mesorregioes.csv")
        df = df.merge(meso[["cd_mun", "nm_meso"]], on="cd_mun", how="left")

    df["regiao"] = df["nm_meso"].map(regiao_de_meso)

    # --- share agrícola baseline (ano anterior à janela) ---
    ano_base = janela[0] - 1
    base = (df[df["ano"] == ano_base][["cd_mun", "agricultura_pct"]]
            .rename(columns={"agricultura_pct": "agric_pct_base"}))
    df = df.merge(base, on="cd_mun", how="left")

    # tercis do share baseline — "núcleo" = tercil superior, "fronteira" = inferior
    val = df.drop_duplicates("cd_mun")[["cd_mun", "agric_pct_base"]].dropna()
    if len(val) >= 30:
        val["tercil_agric"] = pd.qcut(
            val["agric_pct_base"], 3,
            labels=["T1 (baixo share)", "T2", "T3 (núcleo agrícola)"])
        df = df.merge(val[["cd_mun", "tercil_agric"]], on="cd_mun", how="left")
    else:
        df["tercil_agric"] = np.nan

    return df


# ---------------------------------------------------------------------------
# 2. Estimadores
# ---------------------------------------------------------------------------

def _fit(sub: pd.DataFrame, y: str, x: str, *, grupo_ano: bool) -> dict | None:
    """PanelOLS com entity FE + (ano FE | grupo×ano FE), SE clusterizado por entidade."""
    from linearmodels.panel import PanelOLS

    sub = sub.dropna(subset=[y, x]).copy()
    if grupo_ano:
        sub = sub.dropna(subset=["grupo_ano"])
    if len(sub) < 100 or sub["cd_mun"].nunique() < 10:
        return None

    idx = sub.set_index(["cd_mun", "ano"])
    try:
        if grupo_ano:
            # γ_gt substitui γ_t: como grupo×ano aninha ano, o efeito de ano é absorvido.
            mod = PanelOLS(idx[y], idx[[x]], entity_effects=True,
                           other_effects=idx["grupo_ano"], check_rank=False)
        else:
            mod = PanelOLS(idx[y], idx[[x]], entity_effects=True,
                           time_effects=True, check_rank=False)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        return {
            "beta": float(res.params[x]),
            "se": float(res.std_errors[x]),
            "p": float(res.pvalues[x]),
            "n_obs": int(res.nobs),
            "n_ent": int(idx.index.get_level_values(0).nunique()),
            "r2_within": float(res.rsquared_within) if res.rsquared_within is not None else np.nan,
        }
    except Exception as e:  # pragma: no cover — diagnóstico
        return {"erro": str(e)[:90]}


def _linha(**kw) -> dict:
    return kw


def rodar_par(df: pd.DataFrame, y: str, x: str, janela: tuple[int, int],
              nivel: str, rotulo_par: str) -> list[dict]:
    """Blocos A–D para um par (y, x)."""
    out: list[dict] = []
    jstr = f"{janela[0]}–{janela[1]}"
    sub = df[(df["ano"] >= janela[0]) & (df["ano"] <= janela[1])].copy()

    # ── Bloco A — pooled (reprodução do #22) ──
    r = _fit(sub, y, x, grupo_ano=False)
    if r and "erro" not in r:
        out.append(_linha(bloco="A_pooled", par=rotulo_par, janela=jstr, nivel=nivel,
                          grupo="(todos)", **r))
        print(f"  [A] pooled            β={r['beta']:+.5f} SE={r['se']:.5f} "
              f"p={r['p']:.4f} N={r['n_obs']:,} ({r['n_ent']} ent)")
    beta_pooled = r["beta"] if r and "erro" not in r else np.nan

    # ── Bloco B — subamostras ──
    for col, nome in [("regiao", "regiao"), ("tercil_agric", "tercil")]:
        if col not in sub.columns or sub[col].isna().all():
            continue
        print(f"  [B] subamostras por {nome}:")
        for g, gsub in sub.groupby(col, observed=True):
            r = _fit(gsub, y, x, grupo_ano=False)
            if not r or "erro" in r:
                print(f"       {str(g):22s} — insuficiente")
                continue
            sig = "*" if r["p"] < 0.05 else " "
            out.append(_linha(bloco=f"B_sub_{nome}", par=rotulo_par, janela=jstr,
                              nivel=nivel, grupo=str(g), **r))
            print(f"       {str(g):22s} β={r['beta']:+.5f} SE={r['se']:.5f} "
                  f"p={r['p']:.4f}{sig} N={r['n_obs']:,}")

    # ── Bloco C — FE de grupo × ano (decisivo) ──
    for col, nome in [("regiao", "regiao"), ("tercil_agric", "tercil")]:
        if col not in sub.columns or sub[col].isna().all():
            continue
        s2 = sub.copy()
        s2["grupo_ano"] = s2[col].astype(str) + "_" + s2["ano"].astype(str)
        r = _fit(s2, y, x, grupo_ano=True)
        if not r or "erro" in r:
            print(f"  [C] γ_gt ({nome}) — falhou: {r.get('erro') if r else 'insuficiente'}")
            continue
        var = (r["beta"] - beta_pooled) / abs(beta_pooled) * 100 if beta_pooled else np.nan
        sig = "*" if r["p"] < 0.05 else " "
        out.append(_linha(bloco=f"C_gxano_{nome}", par=rotulo_par, janela=jstr, nivel=nivel,
                          grupo=f"γ_gt {nome}", var_pct_vs_pooled=round(var, 1), **r))
        print(f"  [C] γ_gt por {nome:8s}  β={r['beta']:+.5f} SE={r['se']:.5f} "
              f"p={r['p']:.4f}{sig} N={r['n_obs']:,}  ({var:+.1f}% vs pooled)")

    # ── Bloco D — interação com o share baseline (contínuo) ──
    if "agric_pct_base" in sub.columns and sub["agric_pct_base"].notna().any():
        from linearmodels.panel import PanelOLS
        s3 = sub.dropna(subset=[y, x, "agric_pct_base"]).copy()
        if len(s3) >= 100:
            # centrado para que o efeito principal seja lido na média, não em share=0
            s3["_base_c"] = s3["agric_pct_base"] - s3["agric_pct_base"].mean()
            s3["_inter"] = s3[x] * s3["_base_c"]
            idx = s3.set_index(["cd_mun", "ano"])
            try:
                res = PanelOLS(idx[y], idx[[x, "_inter"]], entity_effects=True,
                               time_effects=True, check_rank=False
                               ).fit(cov_type="clustered", cluster_entity=True)
                out.append(_linha(
                    bloco="D_interacao", par=rotulo_par, janela=jstr, nivel=nivel,
                    grupo="Δx × share_base(centrado)",
                    beta=float(res.params[x]), se=float(res.std_errors[x]),
                    p=float(res.pvalues[x]),
                    beta_inter=float(res.params["_inter"]),
                    se_inter=float(res.std_errors["_inter"]),
                    p_inter=float(res.pvalues["_inter"]),
                    n_obs=int(res.nobs),
                    n_ent=int(idx.index.get_level_values(0).nunique())))
                print(f"  [D] interação         β_principal={res.params[x]:+.5f} "
                      f"(p={res.pvalues[x]:.4f}) · β_inter={res.params['_inter']:+.5f} "
                      f"(p={res.pvalues['_inter']:.4f})")
            except Exception as e:
                print(f"  [D] interação — falhou: {str(e)[:70]}")

    return out


# ---------------------------------------------------------------------------
# 3. Veredito
# ---------------------------------------------------------------------------

def veredito(res: pd.DataFrame, par: str, janela: str) -> tuple[str, list[str]]:
    """Aplica a regra pré-declarada. Devolve (veredito, linhas de justificativa)."""
    sel = res[(res["par"] == par) & (res["janela"] == janela)]
    if sel.empty:
        return "sem dados", []

    pooled = sel[sel["bloco"] == "A_pooled"]
    if pooled.empty:
        return "sem pooled", []
    b0 = float(pooled["beta"].iloc[0])
    p0 = float(pooled["p"].iloc[0])

    just: list[str] = [
        f"pooled: β={b0:+.5f} (p={p0:.4f})",
    ]

    subs = sel[sel["bloco"].str.startswith("B_sub_")]
    n_sub = len(subs)
    n_mesmo_sinal_sig = int(((np.sign(subs["beta"]) == np.sign(b0)) & (subs["p"] < 0.05)).sum())
    n_mesmo_sinal = int((np.sign(subs["beta"]) == np.sign(b0)).sum())
    just.append(f"subamostras: {n_mesmo_sinal_sig}/{n_sub} com mesmo sinal E p<0,05; "
                f"{n_mesmo_sinal}/{n_sub} só com mesmo sinal")

    gx = sel[sel["bloco"].str.startswith("C_gxano_")]
    sobrevive = []       # regra pré-declarada (sinal + p<0,05 + |Δβ|<50%)
    magnitude_ok = []    # leitura pós-hoc: só a magnitude do β
    for _, r in gx.iterrows():
        muda = abs(r["beta"] - b0) / abs(b0) * 100 if b0 else np.nan
        ok = (np.sign(r["beta"]) == np.sign(b0)) and (r["p"] < 0.05) and (muda < 50)
        sobrevive.append(ok)
        magnitude_ok.append((np.sign(r["beta"]) == np.sign(b0)) and (muda < 50))
        just.append(f"γ_gt [{r['grupo']}]: β={r['beta']:+.5f} (p={r['p']:.4f}), "
                    f"{muda:+.1f}% vs pooled → {'sobrevive' if ok else 'NÃO sobrevive'}")

    todos_sub_ok = n_sub > 0 and n_mesmo_sinal_sig == n_sub
    todos_gx_ok = len(sobrevive) > 0 and all(sobrevive)
    algum_gx_ok = any(sobrevive)

    if todos_sub_ok and todos_gx_ok:
        v = "(A) INTENSIFICAÇÃO within"
    elif not algum_gx_ok or n_mesmo_sinal_sig == 0:
        v = "(B) COMPOSIÇÃO entre grupos"
    else:
        v = "MISTO — as duas fontes contribuem"

    # ── Leitura pós-hoc (declaradamente NÃO pré-registrada) ──
    # A regra acima exige p<0,05 sob γ_gt, e com isso confunde duas coisas diferentes:
    # o efeito COLAPSAR (evidência de composição) e o teste PERDER PODER (γ_gt queima
    # muitos graus de liberdade). Sob a hipótese (B), o β deveria ir a zero — não apenas
    # perder estrelas com a magnitude intacta. Este diagnóstico olha só a magnitude.
    if len(magnitude_ok) > 0:
        if all(magnitude_ok):
            just.append("[pós-hoc, magnitude] β NÃO colapsa sob γ_gt em nenhum corte "
                        "→ a composição não é a fonte do sinal")
        elif any(magnitude_ok):
            just.append("[pós-hoc, magnitude] β colapsa em parte dos cortes "
                        "→ composição contribui em parte")
        else:
            just.append("[pós-hoc, magnitude] β colapsa sob γ_gt → composição é a fonte")
    return v, just


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------

def main(nivel: str = "municipal") -> None:
    rotulo = "AMC (166)" if nivel == "amc" else "municipal (246)"
    print("=" * 78)
    print(f"#22B — intensificação (A) × composição (B)   [{rotulo}]")
    print("=" * 78)
    print("""
REGRA DE DECISÃO (pré-declarada, antes de ver os resultados):
  (A) intensificação  ⇔ β<0 sig. em TODOS os grupos E sobrevive ao FE grupo×ano
                        (mesmo sinal, p<0,05, variação < 50%)
  (B) composição      ⇔ β<0 no pooled mas ns dentro dos grupos OU colapsa sob γ_gt
  misto               ⇔ sobrevive em parte
""")

    resultados: list[dict] = []
    pares = [PAR_ALVO] + PARES_CONTEXTO

    for janela in [JANELA_PLENA, JANELA_ESTENDIDA]:
        df = preparar_painel(nivel)
        df = anexar_grupos(df, nivel, janela)
        print(f"\n{'─' * 78}\nJANELA {janela[0]}–{janela[1]}")
        n_reg = df.dropna(subset=["regiao"]).groupby("regiao")["cd_mun"].nunique().to_dict()
        print(f"grupos: região {n_reg} · tercis do share agrícola em {janela[0]-1}")

        for i, (y, x) in enumerate(pares):
            if y not in df.columns or x not in df.columns:
                continue
            rot = f"{y} ~ {x}"
            marca = "★ ALVO" if i == 0 else "  contexto"
            print(f"\n{marca}  {rot}")
            resultados += rodar_par(df, y, x, janela, nivel, rot)

    if not resultados:
        print("\nNenhum modelo estimado.")
        return

    res = pd.DataFrame(resultados)
    suf = "_amc" if nivel == "amc" else ""
    out_csv = DIR_OUT / f"intensificacao_composicao{suf}.csv"
    res.to_csv(out_csv, index=False)
    print(f"\nOK: {out_csv.name} ({len(res)} modelos)")

    # ── Veredito ──
    print("\n" + "=" * 78)
    print("VEREDITO (regra pré-declarada)")
    print("=" * 78)
    linhas_md = ["# #22B — intensificação × composição", "",
                 f"Nível: **{rotulo}**", ""]
    for par in [f"{PAR_ALVO[0]} ~ {PAR_ALVO[1]}"] + [f"{y} ~ {x}" for y, x in PARES_CONTEXTO]:
        for janela in [JANELA_PLENA, JANELA_ESTENDIDA]:
            jstr = f"{janela[0]}–{janela[1]}"
            v, just = veredito(res, par, jstr)
            if v in ("sem dados", "sem pooled"):
                continue
            alvo = "★ " if par.startswith(PAR_ALVO[0]) and PAR_ALVO[1] in par else "  "
            print(f"\n{alvo}{par}  [{jstr}]  →  {v}")
            for j in just:
                print(f"      · {j}")
            linhas_md += [f"## {par} — {jstr}", "", f"**Veredito: {v}**", ""]
            linhas_md += [f"- {j}" for j in just] + [""]

    out_md = DIR_OUT / f"intensificacao_composicao{suf}.md"
    out_md.write_text("\n".join(linhas_md), encoding="utf-8")
    print(f"\nOK: {out_md.name}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="#22B — o β<0 do #22 é within ou composição?")
    ap.add_argument("--nivel", choices=["municipal", "amc"], default="municipal")
    args = ap.parse_args()
    main(args.nivel)
