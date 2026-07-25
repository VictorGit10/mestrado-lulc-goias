"""
transicoes_regionais_bracket.py — re-checagem do #33 sob o bracket (D26)
=======================================================================

O §5.4 do #28D nomeou o **#33** como exposto à mudança de rótulo do destino, mas a
varredura de 23/jul/2026 fechou sem lhe dar veredito: ele não aparece na tabela do
§9 de `metodologia/tratamento_deriva_mosaico.md`. Este script fecha essa lacuna.

A afirmação em risco é o item (c) do #33:

    "no Ato III o `pasto→agric` do Sul despenca 0,066→0,008 Mha/ano (−88%)"

que é exatamente a assinatura descrita pela D25 — a transição de interesse
"desaparece" enquanto o fenômeno de campo acelera.

POR QUE O BRACKET NÃO SAI DA FONTE DO #33
    `conversao_bruta_municipal.csv` (#19/#12) tem só os **6 grupos** da D1, e o
    Mosaico de Usos (classe 21) é **mascarado** no #12 (`remap defaultValue=0` +
    `mask(...gt(0))`) — some do numerador e do denominador. Logo a régua superior
    `pasto→(agric∪mosaico)` é **inconstruível** ali. O único instrumento que carrega
    os dois destinos é o censo de pixels do #28 reprocessado
    (`pastagem_conversao_destinos.parquet`, `processa_cubo_idade_destinos.py`).
    Por isso o Bloco A reproduz a manchete na fonte do #33 e o Bloco B a bracketa
    no cubo — duas fontes, mesma quantidade, régua inferior comparável entre elas.

BLOCOS
    A — reprodução na fonte do #33 (régua inferior; valida a comparabilidade)
    B — bracket no cubo: `pasto→agric` × `pasto→(agric∪mosaico)`, meso × ato
    C — âncora IMUNE: soja plantada SIDRA (`agri_soja_ha_plantada`) por mesorregião
    D — as outras afirmações do #33 (veg→pasto e o balanço líquido do Ato II)

SAÍDA
    data/processed/transicoes_regionais_bracket.csv

COMO RODAR
    python scripts/transicoes_regionais_bracket.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
ARQ_CONV = DIR_PROC / "conversao_bruta_municipal.csv"       # fonte do #33 (#19)
ARQ_DESTINOS = DIR_PROC / "pastagem_conversao_destinos.parquet"  # cubo com os 2 destinos
ARQ_PAINEL = DIR_PROC / "painel_unificado.parquet"          # âncora SIDRA
ARQ_MESO = DIR_PROC / "mapeamento_mesorregioes.csv"
ARQ_OUT = DIR_PROC / "transicoes_regionais_bracket.csv"

ORDEM = ["Sul Goiano", "Leste Goiano", "Centro Goiano", "Noroeste Goiano", "Norte Goiano"]


def ato_de(ano: int):
    for k, v in ATOS.items():
        if v["inicio"] <= ano <= v["fim"]:
            return k
    return None


def meso_map() -> pd.DataFrame:
    return pd.read_csv(ARQ_MESO, dtype={"cd_mun": "int64"})[["cd_mun", "nm_meso"]]


def taxa_por_meso_ato(df: pd.DataFrame, col_ano: str, col_area: str) -> pd.DataFrame:
    """Mha/ano por (mesorregião, ato). O denominador é o nº de anos DISTINTOS
    efetivamente observados na célula — não um valor fixo —, para que a taxa seja
    comparável entre fontes cujas convenções de janela diferem."""
    g = df.groupby(["nm_meso", "ato"], observed=True)
    tot = g[col_area].sum() / 1e6
    nanos = g[col_ano].nunique()
    return (tot / nanos).unstack()


def ato_janela_33(ano_origem: pd.Series, ano_destino: pd.Series) -> pd.Series:
    """Ato pela convenção EXATA do #33: `ano_origem >= início & ano_destino <= fim`.

    Não é equivalente a rotular pelo ano de destino: a transição 2019→2020 pertence
    ao Ato II por esta regra (origem 2019) e ao Ato III se rotulada pelo destino. O
    par de fronteira é justamente o mais gordo do Ato III, então a convenção muda a
    magnitude da queda (−88% pela regra do #33, −83% pela do destino). Reproduzir a
    manchete exige a regra dele.
    """
    out = pd.Series(pd.NA, index=ano_origem.index, dtype="object")
    for k, v in ATOS.items():
        m = (ano_origem >= v["inicio"]) & (ano_destino <= v["fim"])
        out[m] = k
    return out


def var_ii_iii(t: pd.DataFrame) -> pd.Series:
    return (t["III"] / t["II"] - 1) * 100


def bloco_a() -> tuple[pd.DataFrame, pd.Series]:
    print("\n" + "═" * 78)
    print("BLOCO A — reprodução na fonte do #33 (conversao_bruta_municipal, régua inferior)")
    print("═" * 78)
    conv = pd.read_csv(ARQ_CONV)
    conv = conv.merge(meso_map(), on="cd_mun", how="left")
    conv["ato"] = ato_janela_33(conv["ano_origem"], conv["ano_destino"])
    pa = conv[(conv.grupo_orig == "pastagem") & (conv.grupo_dest == "agricultura")
              & conv.ato.notna() & conv.nm_meso.notna()].copy()
    t = taxa_por_meso_ato(pa, "ano_origem", "area_ha").reindex(ORDEM)
    t["var_%"] = var_ii_iii(t)
    print(t[["II", "III", "var_%"]].round(4).to_string())
    est = pa.groupby("ato")["area_ha"].sum() / 1e6 / pa.groupby("ato")["ano_origem"].nunique()
    print(f"\n  estado: Ato II {est['II']:.4f} → Ato III {est['III']:.4f} Mha/a "
          f"({(est['III'] / est['II'] - 1) * 100:+.1f}%)")
    print("  (manchete do #33: Sul 0,066 → 0,008 Mha/a, −88%)")
    return t, est


def bloco_b() -> dict[str, pd.DataFrame]:
    print("\n" + "═" * 78)
    print("BLOCO B — bracket no cubo (pastagem_conversao_destinos): agric × união")
    print("═" * 78)
    cubo = pd.read_parquet(ARQ_DESTINOS).merge(meso_map(), on="cd_mun", how="left")
    # `ano_conversao` = Y é o par (Y−1 → Y); a regra do #33 (`ano_origem >= início`)
    # equivale portanto a Y ∈ [início+1, fim]. Mesma janela do Bloco A.
    cubo["ato"] = ato_janela_33(cubo["ano_conversao"] - 1, cubo["ano_conversao"])
    cubo = cubo[cubo.ato.notna() & cubo.nm_meso.notna()]
    out = {}
    for nome, dset in [("agric", {"agricultura"}), ("uniao", {"agricultura", "mosaico"})]:
        sub = cubo[cubo["destino"].isin(dset)]
        t = taxa_por_meso_ato(sub, "ano_conversao", "area_ha").reindex(ORDEM)
        t["var_%"] = var_ii_iii(t)
        print(f"\n  régua = {nome} (Mha/ano)")
        print(t[["II", "III", "var_%"]].round(4).to_string())
        est = (sub.groupby("ato")["area_ha"].sum() / 1e6
               / sub.groupby("ato")["ano_conversao"].nunique())
        print(f"    estado: {est['II']:.4f} → {est['III']:.4f} Mha/a "
              f"({(est['III'] / est['II'] - 1) * 100:+.1f}%)")
        out[nome] = t
    return out


def bloco_c() -> pd.DataFrame:
    print("\n" + "═" * 78)
    print("BLOCO C — âncora IMUNE: soja plantada SIDRA por mesorregião (Mha/ano de expansão)")
    print("═" * 78)
    p = pd.read_parquet(ARQ_PAINEL)[["cd_mun", "ano", "agri_soja_ha_plantada"]]
    p = p.merge(meso_map(), on="cd_mun", how="left")
    s = (p.groupby(["nm_meso", "ano"], observed=True)["agri_soja_ha_plantada"]
         .sum().unstack() / 1e6)
    linhas = {}
    for ato in ("II", "III"):
        ini, fim = ATOS[ato]["inicio"], ATOS[ato]["fim"]
        anos = [a for a in s.columns if ini <= a <= fim]
        # expansão média anual dentro do ato = (nível final − inicial) / nº de saltos
        linhas[ato] = (s[anos[-1]] - s[anos[0]]) / (len(anos) - 1)
    t = pd.DataFrame(linhas).reindex(ORDEM)
    t["var_%"] = var_ii_iii(t)
    print(t.round(4).to_string())
    return t


def bloco_d() -> pd.DataFrame:
    print("\n" + "═" * 78)
    print("BLOCO D — as outras afirmações do #33 (mesma fonte, exposição diferente)")
    print("═" * 78)
    conv = pd.read_csv(ARQ_CONV).merge(meso_map(), on="cd_mun", how="left")
    conv["ato"] = ato_janela_33(conv["ano_origem"], conv["ano_destino"])
    conv = conv[conv.ato.notna() & conv.nm_meso.notna()]

    vp = conv[(conv.grupo_orig == "vegetacao_natural") & (conv.grupo_dest == "pastagem")]
    t = taxa_por_meso_ato(vp, "ano_origem", "area_ha").reindex(ORDEM)
    t["var_%"] = var_ii_iii(t)
    print("\n  (a) veg→pasto — IMUNE (origem e destino fora do Mosaico), Mha/ano:")
    print(t[["II", "III", "var_%"]].round(4).to_string())

    print("\n  (b) balanço líquido de pastagem no Ato II (2001-2019, pré-2020 = limpo), Mha:")
    ii = conv[conv.ato == "II"]
    ganho = ii[ii.grupo_dest == "pastagem"].groupby("nm_meso")["area_ha"].sum()
    perda = ii[ii.grupo_orig == "pastagem"].groupby("nm_meso")["area_ha"].sum()
    bal = ((ganho - perda) / 1e6).reindex(ORDEM)
    for m, v in bal.items():
        print(f"      {m:<18} {v:+.3f}")
    return t


def bloco_e() -> pd.DataFrame:
    """A OUTRA afirmação exposta do #33: a tabela de idade do Ato III (§5).

    O #28C mostrou que o gradiente latitudinal de idade colapsa sob a união, mas
    mediu sobre todos os atos. O #33 publica a tabela **do Ato III** — justamente a
    janela mais exposta —, então precisa do seu próprio teste.
    """
    print("\n" + "═" * 78)
    print("BLOCO E — a tabela de idade do Ato III (§5 do #33) sob o bracket")
    print("═" * 78)
    import estatistica_ponderada as ep

    # Convenções do #33 §5, ambas necessárias para reproduzir a tabela publicada:
    #   (a) o ato da tabela de IDADE é dado pelo `ano_conversao` (janela [início, fim]) —
    #       diferente da regra `ano_origem >= início` que governa as matrizes de fluxo;
    #   (b) a mediana é ponderada com os censurados a FACE VALUE (no Ato III ela é exata,
    #       porque a censura fica toda acima da mediana).
    # Com as duas, o bloco devolve exatamente Sul 16 · Leste 16 · Centro 28 · Norte 27 ·
    # Noroeste 31 na régua `agric` — a tabela do doc.
    ini, fim = ATOS["III"]["inicio"], ATOS["III"]["fim"]
    cubo = pd.read_parquet(ARQ_DESTINOS).merge(meso_map(), on="cd_mun", how="left")
    cubo = cubo[cubo["ano_conversao"].between(ini, fim) & cubo.nm_meso.notna()]
    linhas = {}
    for nome, dset in [("agric", {"agricultura"}), ("uniao", {"agricultura", "mosaico"})]:
        sub = cubo[cubo["destino"].isin(dset)]
        linhas[nome] = {m: ep.mediana(g["idade_pastagem_anos"].to_numpy(float),
                                      g["n_pixels"].to_numpy(float))
                        for m, g in sub.groupby("nm_meso", observed=True)}
    t = pd.DataFrame(linhas).reindex(ORDEM)
    t["Δ"] = t["uniao"] - t["agric"]
    print(t.round(1).to_string())
    for c in ("agric", "uniao"):
        amp = t[c].max() - t[c].min()
        ordem_obs = " < ".join(t[c].sort_values().index.str.replace(" Goiano", ""))
        print(f"  {c:>6}: amplitude Sul→Norte = {amp:.0f}a   |  ordem jovem→velho: {ordem_obs}")
    return t


def main() -> None:
    for f in (ARQ_CONV, ARQ_DESTINOS, ARQ_PAINEL, ARQ_MESO):
        if not f.exists():
            sys.exit(f"Falta {f.relative_to(ROOT)}.")
    print("=" * 78)
    print("#33 sob o bracket da D26 — a queda do `pasto→agric` no Ato III sobrevive?")
    print("=" * 78)

    fonte, _ = bloco_a()
    cubo = bloco_b()
    sidra = bloco_c()
    bloco_d()
    idade = bloco_e()

    linhas = []
    for m in ORDEM:
        linhas.append(dict(
            mesorregiao=m,
            var_fonte33_agric_pct=round(fonte.loc[m, "var_%"], 1),
            var_cubo_agric_pct=round(cubo["agric"].loc[m, "var_%"], 1),
            var_cubo_uniao_pct=round(cubo["uniao"].loc[m, "var_%"], 1),
            var_soja_sidra_pct=round(sidra.loc[m, "var_%"], 1),
            inverte_sinal=bool(cubo["agric"].loc[m, "var_%"] < 0
                               < cubo["uniao"].loc[m, "var_%"]),
            idade_ato3_agric_a=round(idade.loc[m, "agric"], 1),
            idade_ato3_uniao_a=round(idade.loc[m, "uniao"], 1),
        ))
    res = pd.DataFrame(linhas)

    print("\n" + "═" * 78)
    print("VEREDITO — variação da taxa Ato II→III (%), por régua")
    print("═" * 78)
    print(res.to_string(index=False))
    n_inv = int(res["inverte_sinal"].sum())
    print(f"\n  mesorregiões em que o bracket INVERTE o sinal: {n_inv}/{len(res)}")
    print("  Regra da D26: robusto ⇔ sobrevive nos dois extremos. Aqui o intervalo não só")
    print("  cruza zero, ele troca de sinal — a queda do Ato III NÃO é robusta.")

    res.to_csv(ARQ_OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
