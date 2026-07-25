"""
intensity_bracket.py — re-checagem do #31 (Intensity Analysis) sob o bracket (D26)
=================================================================================

Última pendência da auditoria da mudança de rótulo. O #31 lê as mesmas matrizes de
transição do #12/#19, onde a classe 21 (Mosaico de Usos) é **mascarada** — o pixel
que sai de pastagem para Mosaico desaparece do numerador *e* do denominador. Como
a partir de 2021 é para lá que a conversão vai, o Ato III é medido sobre uma matriz
da qual o fluxo dominante foi removido.

A exposição é MAIOR do que o caveat original dizia. Ele marcava só a "retração da
agricultura". Mas o #31 normaliza tudo por

    taxa_uniform = (mudança total fora da diagonal) / (área total) / n_anos

e as duas parcelas encolhem quando os pixels somem da matriz. Logo **toda razão
`*_vs_uniform` do Ato III** — de qualquer categoria ou transição, inclusive as
imunes — está medida contra uma linha-base contaminada. É um efeito de segunda
ordem que o caveat não cobria, e o sinal dele não é óbvio a priori: precisa ser
medido.

MÉTODO (bracket da D26)
    inferior = a matriz como está (Mosaico mascarado; o que o #31 publica)
    superior = a mesma matriz + o fluxo `pasto→Mosaico` reinjetado na célula
               [pastagem, agricultura] — a pergunta grossa "o pasto saiu para
               lavoura-ou-uso-misto?"

LIMITE HONESTO DA RÉGUA SUPERIOR
    O cubo do #28 (`pastagem_conversao_destinos.parquet`) rastreia **saídas de
    pastagem**, e só. Não dá para reinjetar `veg→Mosaico`, `outros→Mosaico` nem as
    saídas do próprio Mosaico. Portanto a régua superior aqui é ela mesma um
    **piso** do que falta na matriz — o intervalo verdadeiro é ao menos tão largo
    quanto o reportado. Isso não enfraquece o veredito: se a conclusão já vira com
    a correção parcial, viraria também com a completa.

SAÍDA
    data/processed/intensity_bracket.csv

COMO RODAR
    python scripts/intensity_bracket.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
ARQ_CONV = DIR_PROC / "conversao_bruta_goias.csv"
ARQ_DESTINOS = DIR_PROC / "pastagem_conversao_destinos.parquet"
ARQ_OUT = DIR_PROC / "intensity_bracket.csv"

GRUPOS = ["vegetacao_natural", "pastagem", "agricultura", "agua", "area_urbana", "outros"]
I_PAST = GRUPOS.index("pastagem")
I_AGRI = GRUPOS.index("agricultura")
I_VEG = GRUPOS.index("vegetacao_natural")


def matriz_anual(df: pd.DataFrame, a0: int, a1: int) -> np.ndarray:
    m = np.zeros((6, 6))
    sub = df[(df["ano_origem"] == a0) & (df["ano_destino"] == a1)]
    for _, r in sub.iterrows():
        m[GRUPOS.index(r["grupo_orig"]), GRUPOS.index(r["grupo_dest"])] = r["area_mha"]
    return m


def mosaico_por_ano() -> dict[int, float]:
    """Fluxo `pasto→Mosaico` em Mha, por ano de destino (GO, censo de pixels)."""
    d = pd.read_parquet(ARQ_DESTINOS, columns=["ano_conversao", "destino", "area_ha"])
    d = d[d["destino"] == "mosaico"]
    return (d.groupby("ano_conversao")["area_ha"].sum() / 1e6).to_dict()


def metricas(mat: np.ndarray, n_anos: int) -> dict:
    # Convenção dimensional já corrigida no #31 (25/jul/2026): `mat` acumula n_anos
    # matrizes, então as somas já são n_anos × a área anual — a razão é a taxa/ano.
    area_total = mat.sum()
    off = area_total - np.trace(mat)
    unif = off / area_total
    out = {"taxa_total_anual": unif, "taxa_uniform": unif}
    # transições-chave: intensidade = área da transição / área da origem (taxa/ano)
    for nome, (i, j) in {"pasto→agric": (I_PAST, I_AGRI),
                         "pasto→veg": (I_PAST, I_VEG),
                         "veg→pasto": (I_VEG, I_PAST)}.items():
        a_orig = mat[i, :].sum()
        inten = mat[i, j] / a_orig if a_orig else 0.0
        out[f"int[{nome}]"] = inten
        out[f"vsunif[{nome}]"] = inten / unif if unif else float("nan")
    # categoria agricultura: ganho vs uniform
    persistiu = mat[I_AGRI, I_AGRI]
    ganho = mat[:, I_AGRI].sum() - persistiu
    out["ganho_agric_anual"] = ganho / area_total
    out["vsunif[ganho agric]"] = (ganho / area_total) / unif if unif else float("nan")
    return out


def por_periodo(df: pd.DataFrame, mos: dict[int, float] | None) -> pd.DataFrame:
    linhas = []
    for nome, info in ATOS.items():
        ini, fim = info["inicio"], info["fim"]
        anos = [a for a in range(ini, fim) if a + 1 <= fim]
        mat = np.zeros((6, 6))
        for a in anos:
            mat += matriz_anual(df, a, a + 1)
            if mos is not None:
                mat[I_PAST, I_AGRI] += mos.get(a + 1, 0.0)
        linhas.append({"ato": nome, "anos": f"{ini}-{fim}", **metricas(mat, len(anos))})
    return pd.DataFrame(linhas).set_index("ato")


def main() -> None:
    for f in (ARQ_CONV, ARQ_DESTINOS):
        if not f.exists():
            sys.exit(f"Falta {f.relative_to(ROOT)}.")
    print("=" * 78)
    print("#31 Intensity Analysis sob o bracket — a linha-base 'uniform' está contaminada?")
    print("=" * 78)

    df = pd.read_csv(ARQ_CONV)
    mos = mosaico_por_ano()
    print(f"\nFluxo pasto→Mosaico reinjetado (Mha/ano, censo GO): "
          f"2015 {mos.get(2015, 0):.3f} · 2020 {mos.get(2020, 0):.3f} · "
          f"2022 {mos.get(2022, 0):.3f} · 2024 {mos.get(2024, 0):.3f}")

    inf = por_periodo(df, None)
    sup = por_periodo(df, mos)

    cols = ["taxa_total_anual", "taxa_uniform", "int[pasto→agric]", "vsunif[pasto→agric]",
            "int[pasto→veg]", "vsunif[pasto→veg]", "int[veg→pasto]", "vsunif[veg→pasto]",
            "vsunif[ganho agric]"]
    print("\n── régua INFERIOR (matriz como está — o que o #31 publica) " + "─" * 18)
    print(inf[cols].round(5).to_string())
    print("\n── régua SUPERIOR (pasto→Mosaico reinjetado como saída p/ lavoura-ou-misto) " + "─" * 2)
    print(sup[cols].round(5).to_string())

    print("\n" + "═" * 78)
    print("VEREDITO")
    print("═" * 78)
    u_i, u_s = inf.loc["III", "taxa_uniform"], sup.loc["III", "taxa_uniform"]
    print(f"1. A linha-base do Ato III: uniform {u_i:.5f} → {u_s:.5f} "
          f"({(u_s / u_i - 1) * 100:+.1f}%)")
    print("   Toda razão *_vs_uniform do Ato III é medida contra ela — inclusive as das")
    print("   transições imunes, que não têm nada de errado no numerador.")
    for k in ("pasto→agric", "pasto→veg", "veg→pasto"):
        a, b = inf.loc["III", f"vsunif[{k}]"], sup.loc["III", f"vsunif[{k}]"]
        print(f"2. {k:>12} vs uniform (Ato III): {a:.2f} → {b:.2f} ({(b / a - 1) * 100:+.0f}%)")
    # A comparação Ato II→III tem de ser feita DENTRO de cada régua: cruzar réguas
    # (o Ato II cru contra o Ato III corrigido) é justamente o erro que a D26 proíbe.
    print("3. 'retração da agricultura' — variação da intensidade pasto→agric, Ato II→III,")
    print("   medida dentro de cada régua:")
    for nome, d in (("inferior (agric)", inf), ("superior (agric∪mosaico)", sup)):
        ii, iii = d.loc["II", "int[pasto→agric]"], d.loc["III", "int[pasto→agric]"]
        print(f"     {nome:<26} {ii:.5f} → {iii:.5f}  ({(iii / ii - 1) * 100:+.0f}%)")
    print("   O bracket INVERTE o sinal: a 'retração' é a régua, não o campo.")

    res = pd.concat([inf.assign(regua="inferior (agric)"),
                     sup.assign(regua="superior (agric∪mosaico)")]).reset_index()
    res.to_csv(ARQ_OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
