"""validar_transicoes_cubo.py — a validação que o #12 não conseguia fazer
=========================================================================

Confere a matriz recontada pelo [#12B](transicoes_cubo.py) contra as duas
referências disponíveis, e — o ponto — **decompõe a diferença em duas parcelas
que não podem chegar misturadas a jusante**:

    Δ_medida    instrumento diferente (pixel nativo + cos(lat) × reduceRegions
                em EPSG:5880 a scale=30). Afeta TODA célula, inclusive onde o
                Mosaico é irrelevante.
    Δ_mosaico   o grupo 7 passa a existir. É o conserto.

BLOCO A — Δ_medida isolado
    Colapsa o censo de volta a 6 grupos (descartando o grupo 7 dos dois lados —
    exatamente o que o GEE fazia) e compara par a par com `data/cache/transicoes/`.
    O que sobra aqui é SÓ instrumento. Se este bloco vier grande, não é o Mosaico:
    é erro de grade, de área ou de recorte, e tem que ser explicado antes de
    qualquer repropagação.

BLOCO B — batimento contra o #4 COM a classe 21 dos dois lados
    A `validar_batimental()` do #12 mapeia os `class_id` do #4 pelo mesmo dicionário
    de 6 grupos e faz `dropna(...)`, descartando a classe 21 **dos dois lados** antes
    de comparar. Passaria com δ≈0 mesmo se 100% da conversão recente tivesse migrado
    para o rótulo excluído — é cega por construção. Aqui o Mosaico entra nas duas
    pontas, e a coluna `#12 cobre` mostra, em hectares, o tamanho do buraco que a
    validação antiga não podia enxergar.

BLOCO C — fechamento
    Soma de todas as células por par ≈ área de Goiás, censo × GEE. Mede quanta
    terra cada instrumento simplesmente perde.

SAÍDA
    data/processed/validacao_transicoes_cubo.csv   (Bloco A, por par)
    relatório no stdout

COMO RODAR
    python scripts/validar_transicoes_cubo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402
from transicoes_cubo import NOME_CLASSE, ORDEM_GRUPOS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
CACHE_GEE = ROOT / "data" / "cache" / "transicoes"
CENSO = DIR_PROC / "transicoes_cubo_goias.csv"
CSV_P4 = DIR_PROC / "mapbiomas_munis_goias.csv"
SAIDA = DIR_PROC / "validacao_transicoes_cubo.csv"

ID_MOSAICO = 7  # índice do grupo Mosaico na matriz do #12B
AREA_GOIAS_MHA = 34.009  # IBGE


def carregar_censo() -> pd.DataFrame:
    if not CENSO.exists():
        sys.exit(f"Não encontrei {CENSO}. Rode antes: python scripts/transicoes_cubo.py")
    return pd.read_csv(CENSO)


def carregar_gee() -> pd.DataFrame:
    arquivos = sorted(CACHE_GEE.glob("transicao_????_????.csv"))
    if not arquivos:
        sys.exit(f"Nenhum cache do #12 em {CACHE_GEE}")
    partes = []
    for p in arquivos:
        a0, a1 = (int(x) for x in p.stem.split("_")[1:3])
        df = pd.read_csv(p)
        df["ano_origem"], df["ano_destino"] = a0, a1
        partes.append(df)
    return pd.concat(partes, ignore_index=True)


def bloco_a(censo: pd.DataFrame, gee: pd.DataFrame) -> pd.DataFrame:
    """Δ_medida: censo colapsado a 6 grupos × cache do GEE, por par e por célula."""
    print("=" * 72)
    print("BLOCO A — Δ_medida (censo colapsado a 6 grupos × cache GEE)")
    print("=" * 72)

    # Descarta o grupo 7 dos dois lados: é o que o GEE fazia. O que sobrar é
    # diferença de INSTRUMENTO, não de cobertura de classe.
    c6 = censo[(censo.classe_orig != ID_MOSAICO) & (censo.classe_dest != ID_MOSAICO)]
    c_uf = c6.groupby(["ano_origem", "ano_destino", "classe_orig", "classe_dest"],
                      as_index=False)["area_ha"].sum().rename(columns={"area_ha": "censo6_ha"})
    g_uf = gee.groupby(["ano_origem", "ano_destino", "classe_orig", "classe_dest"],
                       as_index=False)["area_ha"].sum().rename(columns={"area_ha": "gee_ha"})

    m = c_uf.merge(g_uf, on=["ano_origem", "ano_destino", "classe_orig", "classe_dest"],
                   how="outer").fillna({"censo6_ha": 0.0, "gee_ha": 0.0})
    m["delta_ha"] = m["censo6_ha"] - m["gee_ha"]
    with np.errstate(invalid="ignore", divide="ignore"):
        m["delta_pct"] = np.where(m["gee_ha"] > 0, m["delta_ha"] / m["gee_ha"] * 100, np.nan)

    por_par = m.groupby(["ano_origem", "ano_destino"]).agg(
        censo6_mha=("censo6_ha", lambda s: s.sum() / 1e6),
        gee_mha=("gee_ha", lambda s: s.sum() / 1e6),
    ).reset_index()
    por_par["delta_pct_total"] = (por_par.censo6_mha - por_par.gee_mha) / por_par.gee_mha * 100

    print(f"\n  {len(m):,} células comparadas em {len(por_par)} pares")
    print(f"  δ total por par:  mediana {por_par.delta_pct_total.median():+.2f}%  "
          f"| min {por_par.delta_pct_total.min():+.2f}%  "
          f"| max {por_par.delta_pct_total.max():+.2f}%")

    grandes = m[m.gee_ha > 10_000]  # células com massa; ignora ruído de célula minúscula
    print(f"  δ por célula (>10k ha, n={len(grandes):,}): "
          f"mediana {grandes.delta_pct.median():+.2f}%  "
          f"| p05 {grandes.delta_pct.quantile(.05):+.2f}%  "
          f"| p95 {grandes.delta_pct.quantile(.95):+.2f}%")

    print("\n  Pares com maior desvio total:")
    for _, r in por_par.reindex(por_par.delta_pct_total.abs().sort_values(ascending=False).index).head(5).iterrows():
        print(f"    {int(r.ano_origem)}→{int(r.ano_destino)}: censo6 {r.censo6_mha:6.3f} Mha  "
              f"GEE {r.gee_mha:6.3f} Mha  δ {r.delta_pct_total:+6.2f}%")

    print("\n  Células de maior massa (as que a dissertação cita):")
    top = grandes.groupby(["classe_orig", "classe_dest"], as_index=False).agg(
        censo6_ha=("censo6_ha", "sum"), gee_ha=("gee_ha", "sum"))
    top["delta_pct"] = (top.censo6_ha - top.gee_ha) / top.gee_ha * 100
    for _, r in top.nlargest(6, "gee_ha").iterrows():
        o, d = NOME_CLASSE[int(r.classe_orig)], NOME_CLASSE[int(r.classe_dest)]
        print(f"    {o:18s} → {d:18s}: censo6 {r.censo6_ha/1e6:6.3f} Mha  "
              f"GEE {r.gee_ha/1e6:6.3f} Mha  δ {r.delta_pct:+6.2f}%")

    return por_par


def bloco_b(censo: pd.DataFrame, gee: pd.DataFrame) -> None:
    """Batimento contra o #4 com a classe 21 presente nos DOIS lados."""
    print("\n" + "=" * 72)
    print("BLOCO B — batimento contra o #4 COM a classe 21 (o teste que o #12 não faz)")
    print("=" * 72)

    if not CSV_P4.exists():
        print(f"  {CSV_P4.name} não encontrado — bloco pulado.")
        return

    df4 = pd.read_csv(CSV_P4, dtype={"cd_mun": "int64"})
    id_para_idx = {cid: i for i, chave, _ in ORDEM_GRUPOS for cid in pc.GRUPO_MAP[chave]}
    df4["grupo"] = df4["class_id"].map(id_para_idx)
    nao_map = df4[df4.grupo.isna()]["class_id"].unique()
    if len(nao_map):
        print(f"  AVISO: classes do #4 sem grupo: {sorted(nao_map)}")
    df4 = df4.dropna(subset=["grupo"])
    df4["grupo"] = df4["grupo"].astype(int)

    # Pares longos do Nível 1 — os mesmos que a validar_batimental() do #12 usa
    pares = [(1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024)]
    for a0, a1 in pares:
        p4 = df4[df4.ano == a1].groupby("grupo")["area_ha"].sum()
        cs = (censo[(censo.ano_origem == a0) & (censo.ano_destino == a1)]
              .groupby("classe_dest")["area_ha"].sum())
        ge = (gee[(gee.ano_origem == a0) & (gee.ano_destino == a1)]
              .groupby("classe_dest")["area_ha"].sum())
        if cs.empty:
            continue
        print(f"\n  {a0}→{a1}  (estoque no ano-destino, por grupo)")
        print(f"    {'grupo':20s} {'#4 (ha)':>14s} {'#12B censo':>14s} {'δ':>7s}   {'#12 GEE':>14s} {'cobre':>7s}")
        for gidx in sorted(set(p4.index) | set(cs.index)):
            v4, vc = p4.get(gidx, 0.0), cs.get(gidx, 0.0)
            vg = ge.get(gidx, 0.0)
            dc = (vc - v4) / v4 * 100 if v4 > 0 else float("nan")
            cob = vg / v4 * 100 if v4 > 0 else float("nan")
            marca = "  <-- o buraco" if gidx == ID_MOSAICO else ""
            print(f"    {NOME_CLASSE[gidx]:20s} {v4:14,.0f} {vc:14,.0f} {dc:+6.1f}% "
                  f"  {vg:14,.0f} {cob:6.1f}%{marca}")

    print("\n  Leitura: a coluna 'cobre' é quanto do estoque do #4 a matriz do #12")
    print("  contabiliza. Para o Mosaico ela é 0% em todos os pares — e a validação")
    print("  antiga não podia ver isso, porque removia a classe 21 dos dois lados.")


def bloco_c(censo: pd.DataFrame, gee: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("BLOCO C — fechamento (soma de todas as células ≈ área de Goiás)")
    print("=" * 72)

    sc = censo.groupby(["ano_origem", "ano_destino"])["area_ha"].sum() / 1e6
    sg = gee.groupby(["ano_origem", "ano_destino"])["area_ha"].sum() / 1e6
    print(f"\n  censo (7 grupos): min {sc.min():.3f} | mediana {sc.median():.3f} | "
          f"max {sc.max():.3f} Mha")
    print(f"  GEE   (6 grupos): min {sg.min():.3f} | mediana {sg.median():.3f} | "
          f"max {sg.max():.3f} Mha")
    print(f"  referência IBGE:  {AREA_GOIAS_MHA:.3f} Mha")

    falta_c = (AREA_GOIAS_MHA - sc.median()) / AREA_GOIAS_MHA * 100
    falta_g = (AREA_GOIAS_MHA - sg.median()) / AREA_GOIAS_MHA * 100
    print(f"\n  terra que cada instrumento não contabiliza (mediana):")
    print(f"    censo: {falta_c:+.2f}%   |   GEE: {falta_g:+.2f}%")

    # Quanto o Mosaico responde pela diferença, ano a ano no fim da série
    mos = censo[(censo.classe_orig == ID_MOSAICO) | (censo.classe_dest == ID_MOSAICO)]
    mos_ano = mos[mos.ano_destino - mos.ano_origem == 1].groupby("ano_destino")["area_ha"].sum() / 1e6
    print("\n  massa que envolve o Mosaico (pares consecutivos) — a que o #12 descarta:")
    for ano in (1990, 2000, 2010, 2015, 2020, 2024):
        if ano in mos_ano.index:
            print(f"    {ano}: {mos_ano[ano]:6.3f} Mha "
                  f"({mos_ano[ano] / AREA_GOIAS_MHA * 100:4.1f}% de Goiás)")


def main() -> None:
    censo = carregar_censo()
    gee = carregar_gee()
    print(f"censo: {len(censo):,} linhas | GEE: {len(gee):,} linhas\n")

    por_par = bloco_a(censo, gee)
    bloco_b(censo, gee)
    bloco_c(censo, gee)

    por_par.to_csv(SAIDA, index=False, float_format="%.6f")
    print(f"\nOK: {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
