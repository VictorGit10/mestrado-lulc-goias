"""analise_transicoes.py - Pipeline #25
Consome conversao_bruta_*.csv e produz analises por ATO politico:
  - 5 matrizes 6x6 (matriz_transicao_ato_{I..V}.csv)
  - decomposicao_origem.csv (de onde veio cada hectare novo)
  - fluxo_bruto_liquido.csv (distingue rotacao de substituicao)
  - 5 JSONs Sankey por ATO em Visualizacao/assets/data/
  - top_transicoes_mesos.csv (top-3 transicoes por mesorregiao x ATO)

Pre-requisito: scripts/agregar_conversoes.py executado.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_VIZ_DATA = ROOT / "Visualizacao" / "assets" / "data"

ATOS = {
    "I":   (1985, 1993, "Heranca Cerradeira"),
    "II":  (1994, 2002, "Plano Real e Lei Kandir"),
    "III": (2003, 2011, "Boom de Commodities"),
    "IV":  (2012, 2017, "Codigo Florestal"),
    "V":   (2018, 2024, "Cerrado Manifesto"),
}

GRUPOS = ["vegetacao_natural", "pastagem", "agricultura",
          "agua", "area_urbana", "outros"]

GRUPO_LABEL = {
    "vegetacao_natural": "Vegetacao Natural",
    "pastagem":          "Pastagem",
    "agricultura":       "Agricultura",
    "agua":              "Agua",
    "area_urbana":       "Area Urbana",
    "outros":            "Outros",
}

GRUPO_COR = {
    "vegetacao_natural": "#2d5a3d",
    "pastagem":          "#d4b65a",
    "agricultura":       "#d96aa3",
    "agua":              "#4a7ba6",
    "area_urbana":       "#8a8a82",
    "outros":            "#b8a98a",
}

MIN_FLUXO_SANKEY = 0.02  # Mha. Limiar para incluir link no JSON Sankey.


def filtrar_ato(df: pd.DataFrame, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    return df[(df["ano_origem"] >= ano_ini) & (df["ano_destino"] <= ano_fim)].copy()


def matriz_ato(df_ato: pd.DataFrame) -> pd.DataFrame:
    m = df_ato.pivot_table(
        index="grupo_orig", columns="grupo_dest",
        values="area_mha", aggfunc="sum", fill_value=0.0,
    )
    return m.reindex(index=GRUPOS, columns=GRUPOS, fill_value=0.0)


def decomposicao_origem(matriz: pd.DataFrame, ato: str) -> list[dict]:
    linhas = []
    for dest in GRUPOS:
        col = matriz[dest].copy()
        col[dest] = 0.0  # exclui persistencia
        total = float(col.sum())
        if total < 1e-6:
            continue
        for orig in GRUPOS:
            if orig == dest:
                continue
            area = float(col[orig])
            pct = area / total * 100 if total > 0 else 0.0
            linhas.append({
                "ato": ato,
                "grupo_dest": dest,
                "grupo_orig": orig,
                "area_mha": round(area, 4),
                "pct_origem": round(pct, 2),
            })
    return linhas


def fluxo_bruto_liquido(matriz: pd.DataFrame, ato: str) -> list[dict]:
    linhas = []
    for orig in GRUPOS:
        for dest in GRUPOS:
            if orig == dest:
                continue
            bruto_od = float(matriz.loc[orig, dest])
            bruto_do = float(matriz.loc[dest, orig])
            linhas.append({
                "ato": ato,
                "grupo_orig": orig,
                "grupo_dest": dest,
                "bruto_mha": round(bruto_od, 4),
                "liquido_mha": round(bruto_od - bruto_do, 4),
            })
    return linhas


def sankey_json(matriz: pd.DataFrame, ato: str, ano_ini: int, ano_fim: int,
                titulo: str) -> dict:
    """Sankey origem(ano_ini) -> destino(ano_fim). Apenas off-diagonal."""
    nodes = []
    for g in GRUPOS:
        nodes.append({
            "id": f"{GRUPO_LABEL[g]}_{ano_ini}",
            "label": f"{GRUPO_LABEL[g]} ({ano_ini})",
            "color": GRUPO_COR[g],
        })
    for g in GRUPOS:
        nodes.append({
            "id": f"{GRUPO_LABEL[g]}_{ano_fim}",
            "label": f"{GRUPO_LABEL[g]} ({ano_fim})",
            "color": GRUPO_COR[g],
        })

    links = []
    for orig in GRUPOS:
        for dest in GRUPOS:
            if orig == dest:
                continue
            v = float(matriz.loc[orig, dest])
            if v < MIN_FLUXO_SANKEY:
                continue
            links.append({
                "source": f"{GRUPO_LABEL[orig]}_{ano_ini}",
                "target": f"{GRUPO_LABEL[dest]}_{ano_fim}",
                "value": round(v, 4),
                "color": GRUPO_COR[orig],
            })

    return {
        "ato": ato,
        "titulo": titulo,
        "ano_ini": ano_ini,
        "ano_fim": ano_fim,
        "nodes": nodes,
        "links": links,
    }


def top_transicoes_mesos(df_muni: pd.DataFrame, mapa_mesos: pd.DataFrame,
                          top_n: int = 3) -> pd.DataFrame:
    df = df_muni.merge(mapa_mesos[["cd_mun", "nm_meso"]], on="cd_mun", how="left")

    linhas = []
    for ato, (ano_ini, ano_fim, _) in ATOS.items():
        df_ato = df[(df["ano_origem"] >= ano_ini) & (df["ano_destino"] <= ano_fim)]
        # Soma transicoes (off-diagonal) por meso x par
        df_off = df_ato[df_ato["grupo_orig"] != df_ato["grupo_dest"]]
        agg = (df_off.groupby(["nm_meso", "grupo_orig", "grupo_dest"],
                              as_index=False)["area_mha"].sum())
        # Top-N por meso
        for meso, sub in agg.groupby("nm_meso"):
            top = sub.nlargest(top_n, "area_mha")
            for _, row in top.iterrows():
                linhas.append({
                    "ato": ato,
                    "mesorregiao": meso,
                    "grupo_orig": row["grupo_orig"],
                    "grupo_dest": row["grupo_dest"],
                    "area_mha": round(row["area_mha"], 4),
                })
    return pd.DataFrame(linhas)


def main() -> None:
    DIR_PROC.mkdir(parents=True, exist_ok=True)
    DIR_VIZ_DATA.mkdir(parents=True, exist_ok=True)

    print("Lendo conversao_bruta_goias.csv ...")
    df_uf = pd.read_csv(DIR_PROC / "conversao_bruta_goias.csv")
    print(f"  {len(df_uf):,} linhas")

    print("Lendo conversao_bruta_municipal.csv ...")
    df_muni = pd.read_csv(DIR_PROC / "conversao_bruta_municipal.csv")
    print(f"  {len(df_muni):,} linhas")

    print("Lendo mapeamento_mesorregioes.csv ...")
    mapa_mesos = pd.read_csv(DIR_PROC / "mapeamento_mesorregioes.csv")
    print(f"  {len(mapa_mesos):,} munis mapeados")

    # 1. Matrizes por ATO + decomposicao + fluxo
    decomposicao_all = []
    fluxo_all = []

    for ato, (ano_ini, ano_fim, titulo) in ATOS.items():
        df_ato = filtrar_ato(df_uf, ano_ini, ano_fim)
        m = matriz_ato(df_ato)

        out = DIR_PROC / f"matriz_transicao_ato_{ato}.csv"
        m.round(4).to_csv(out)
        print(f"OK: {out.name}")

        decomposicao_all.extend(decomposicao_origem(m, ato))
        fluxo_all.extend(fluxo_bruto_liquido(m, ato))

        # Sankey JSON
        sankey = sankey_json(m, ato, ano_ini, ano_fim, titulo)
        out_json = DIR_VIZ_DATA / f"sankey_ato_{ato}.json"
        out_json.write_text(json.dumps(sankey, ensure_ascii=False, indent=2),
                            encoding="utf-8")
        print(f"OK: {out_json.relative_to(ROOT)}  ({len(sankey['links'])} links)")

    pd.DataFrame(decomposicao_all).to_csv(
        DIR_PROC / "decomposicao_origem.csv", index=False)
    print(f"OK: decomposicao_origem.csv ({len(decomposicao_all)} linhas)")

    pd.DataFrame(fluxo_all).to_csv(
        DIR_PROC / "fluxo_bruto_liquido.csv", index=False)
    print(f"OK: fluxo_bruto_liquido.csv ({len(fluxo_all)} linhas)")

    # 2. Top transicoes por mesorregiao
    print("\nCalculando top transicoes por mesorregiao ...")
    top_mesos = top_transicoes_mesos(df_muni, mapa_mesos, top_n=3)
    top_mesos.to_csv(DIR_PROC / "top_transicoes_mesos.csv", index=False)
    print(f"OK: top_transicoes_mesos.csv ({len(top_mesos)} linhas)")

    # 3. Resumo
    print("\n=== Resumo: decomposicao da expansao por ATO ===")
    df_dec = pd.DataFrame(decomposicao_all)
    for ato in ATOS:
        for dest in ["agricultura", "pastagem"]:
            sub = df_dec[(df_dec["ato"] == ato) & (df_dec["grupo_dest"] == dest)]
            if sub.empty:
                continue
            top = sub.nlargest(1, "pct_origem").iloc[0]
            total = sub["area_mha"].sum()
            print(f"  ATO {ato} expansao de {dest}: {total:.2f} Mha brutas; "
                  f"maior origem = {top['grupo_orig']} ({top['pct_origem']:.1f}%)")


if __name__ == "__main__":
    main()
