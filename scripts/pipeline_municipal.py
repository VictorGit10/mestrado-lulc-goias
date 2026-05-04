"""
pipeline_municipal.py — MapBiomas Coleção 10.1 no nível municipal de Goiás
============================================================================

Extrai a aba `COVERAGE_10.1` do xlsx do MapBiomas (já em cache local) e gera
uma tabela longa com a área de cada classe de uso da terra, por município
goiano e por ano (1985–2024).

Resolve dois problemas:
  1. O xlsx vem em formato wide (1 coluna por ano) e mistura biomas (Cerrado +
     Mata Atlântica para munis fronteiriços). Aqui derretemos para longo e
     somamos os biomas, gerando uma única linha por (município, ano, classe).
  2. O xlsx só tem o NOME do município, não o código IBGE de 7 dígitos. Sem
     o código, não dá pra fazer join com SIDRA, BACEN, geobr etc. Aqui fazemos
     merge com a lista de munis Goiás extraída do SIDRA já coletado.

Como rodar:
    python pipeline_municipal.py

Pré-requisitos:
    - data/raw/mapbiomas_col10_estado.xlsx  (baixado por grafico_pastagem_pib_goias.py)
    - data/processed/sidra_pam1612_temporarias.csv  (gerado por coleta_sidra.py)

Saída:
    data/processed/mapbiomas_munis_goias.csv

Schema da saída:
    cd_mun         int   Código IBGE 7 dígitos
    nm_mun         str   Nome (sem sufixo " - GO")
    ano            int   1985–2024
    class_id       int   Código da classe MapBiomas (15 = Pastagem, 39 = Soja, ...)
    class_nome     str   Nome curto da classe (level_3 do MapBiomas, em pt-BR)
    area_ha        float Área em hectares (somada sobre Cerrado + Mata Atlântica)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT           = Path(__file__).resolve().parent.parent
ARQ_MAPBIOMAS = ROOT / "data" / "raw" / "mapbiomas_col10_estado.xlsx"
ARQ_SIDRA_REF = ROOT / "data" / "processed" / "sidra_pam1612_temporarias.csv"
ARQ_SAIDA     = ROOT / "data" / "processed" / "mapbiomas_munis_goias.csv"

ABA_COBERTURA = "COVERAGE_10.1"
ANO_INI, ANO_FIM = 1985, 2024

# Tradução pt-BR das classes MapBiomas mais relevantes para a tese.
# Fonte: brasil.mapbiomas.org/legenda-classificacao/
CLASSES_NOME_PT = {
    1:  "Floresta",
    3:  "Floresta Nativa",
    4:  "Savana/Cerrado",
    5:  "Mangue",
    6:  "Floresta Alagável",
    9:  "Silvicultura",
    10: "Vegetação Herbácea/Arbustiva",
    11: "Campo Alagado",
    12: "Campo Nativo",
    13: "Outras Formações Naturais",
    14: "Agropecuária",
    15: "Pastagem",
    18: "Agricultura",
    19: "Lavoura Temporária",
    20: "Cana-de-açúcar",
    21: "Mosaico de Usos",
    22: "Área Não Vegetada",
    23: "Praia/Duna/Areal",
    24: "Área Urbanizada",
    25: "Outras Áreas Não Vegetadas",
    29: "Afloramento Rochoso",
    30: "Mineração",
    31: "Aquicultura",
    32: "Apicum",
    33: "Rio/Lago/Oceano",
    35: "Dendê",
    36: "Lavoura Perene",
    39: "Soja",
    40: "Arroz",
    41: "Outra Lavoura Temporária",
    46: "Café",
    47: "Citrus",
    48: "Outra Lavoura Perene",
    50: "Restinga Arbórea",
    62: "Algodão",
    63: "Floresta Plantada",
}


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def carregar_mapbiomas_goias() -> pd.DataFrame:
    """Lê COVERAGE_10.1, filtra Goiás, derrete para formato longo."""
    print(f"[...] Lendo {ARQ_MAPBIOMAS.name} aba {ABA_COBERTURA}...")
    df = pd.read_excel(ARQ_MAPBIOMAS, sheet_name=ABA_COBERTURA)
    print(f"  shape: {df.shape}")

    # Filtrar Goiás
    go = df[df["state"].astype(str).str.upper().isin(["GOIÁS", "GOIAS", "GO"])].copy()
    print(f"  linhas Goiás: {len(go)} | munis distintos: {go['municipality'].nunique()}")

    # Identificar colunas de anos (são int, não str)
    cols_anos = [c for c in df.columns if isinstance(c, int) and ANO_INI <= c <= ANO_FIM]
    print(f"  anos: {cols_anos[0]}–{cols_anos[-1]} ({len(cols_anos)} colunas)")

    # Derreter (wide -> long)
    id_vars = ["biome", "municipality", "class_id"]
    long = go[id_vars + cols_anos].melt(
        id_vars=id_vars, var_name="ano", value_name="area_ha",
    )
    long["ano"] = long["ano"].astype(int)
    long["area_ha"] = pd.to_numeric(long["area_ha"], errors="coerce").fillna(0.0)
    long["class_id"] = long["class_id"].astype(int)
    print(f"  formato longo: {len(long):,} linhas")
    return long


def carregar_munis_ibge_de_sidra() -> pd.DataFrame:
    """Extrai a tabela [cd_mun, nm_mun] do SIDRA já coletado (via PAM 1612)."""
    print(f"[...] Carregando códigos IBGE de {ARQ_SIDRA_REF.name}...")
    sidra = (
        pd.read_csv(ARQ_SIDRA_REF, usecols=["cd_mun", "nm_mun"])
        .drop_duplicates()
        .reset_index(drop=True)
    )
    print(f"  munis IBGE: {len(sidra)} (esperado: 246)")
    if len(sidra) != 246:
        print(f"  AVISO: total de munis ({len(sidra)}) difere de 246")
    return sidra


def juntar_mapbiomas_e_ibge(
    mapb: pd.DataFrame, sidra: pd.DataFrame,
) -> pd.DataFrame:
    """Merge por nome do município. Reporta munis sem match."""
    print("[...] Fazendo merge MapBiomas × IBGE por nome do município...")
    df = mapb.merge(
        sidra, left_on="municipality", right_on="nm_mun", how="inner",
    )

    n_munis_mapb = mapb["municipality"].nunique()
    n_munis_join = df["cd_mun"].nunique()
    perdidos = sorted(set(mapb["municipality"]) - set(df["municipality"]))
    print(f"  munis MapBiomas: {n_munis_mapb} | após join: {n_munis_join}")
    if perdidos:
        print(f"  perdidos (esperado: munis-borda de outros estados):")
        for n in perdidos:
            area_total = mapb[mapb["municipality"] == n]["area_ha"].sum()
            print(f"    - {n!r}  (área total na série: {area_total:.2f} ha)")
    return df


def agregar_por_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Soma os biomas (Cerrado + Mata Atlântica) por (cd_mun, ano, class_id)."""
    print("[...] Agregando biomas (Cerrado + Mata Atlântica) por município...")
    out = (
        df.groupby(["cd_mun", "nm_mun", "ano", "class_id"], as_index=False)["area_ha"]
        .sum()
    )
    out["class_nome"] = out["class_id"].map(CLASSES_NOME_PT).fillna("Outra")
    out = out[["cd_mun", "nm_mun", "ano", "class_id", "class_nome", "area_ha"]]
    print(f"  saída: {len(out):,} linhas, "
          f"{out['cd_mun'].nunique()} munis × {out['ano'].nunique()} anos × "
          f"{out['class_id'].nunique()} classes")
    return out


def validacao_batimental(df_muni: pd.DataFrame) -> None:
    """Confere se o agregado municipal bate com a série UF que já temos."""
    print("\n[validação] Pastagem (classe 15) total Goiás vs série UF antiga:")
    pasto_muni = df_muni[df_muni["class_id"] == 15].groupby("ano")["area_ha"].sum()

    arq_uf = ROOT / "data" / "processed" / "pastagem_goias_anual.csv"
    if arq_uf.exists():
        pasto_uf = pd.read_csv(arq_uf).set_index("ano")["area_pastagem_ha"]
        comp = pd.DataFrame({"municipal_soma": pasto_muni, "uf_antigo": pasto_uf}).dropna()
        comp["delta_pct"] = (comp["municipal_soma"] - comp["uf_antigo"]) / comp["uf_antigo"] * 100
        print(comp.head(3).to_string())
        print("...")
        print(comp.tail(3).to_string())
        delta_max = comp["delta_pct"].abs().max()
        print(f"\n  max |delta|: {delta_max:.4f}%  -> "
              f"{'OK (idêntico)' if delta_max < 0.01 else 'DIVERGE — investigar'}")
    else:
        print(f"  (sem série UF antiga em {arq_uf.name} para comparar)")


def main() -> None:
    print("=" * 70)
    print("Pipeline municipal — MapBiomas Coleção 10.1, Goiás (1985–2024)")
    print("=" * 70)

    if not ARQ_MAPBIOMAS.exists():
        raise FileNotFoundError(
            f"{ARQ_MAPBIOMAS} não encontrado. "
            "Rode primeiro grafico_pastagem_pib_goias.py para baixar."
        )
    if not ARQ_SIDRA_REF.exists():
        raise FileNotFoundError(
            f"{ARQ_SIDRA_REF} não encontrado. "
            "Rode primeiro coleta_sidra.py para gerar a tabela de códigos IBGE."
        )

    mapb = carregar_mapbiomas_goias()
    sidra = carregar_munis_ibge_de_sidra()
    juntos = juntar_mapbiomas_e_ibge(mapb, sidra)
    final = agregar_por_municipio(juntos)

    final.to_csv(ARQ_SAIDA, index=False)
    print(f"\n[OK] Salvo: {ARQ_SAIDA}")
    print(f"     {ARQ_SAIDA.stat().st_size / 1e6:.1f} MB")

    validacao_batimental(final)

    print("\n" + "=" * 70)
    print("Próximos cruzamentos disponíveis:")
    print("=" * 70)
    print("  mapb = pd.read_csv('data/processed/mapbiomas_munis_goias.csv')")
    print("  sidra = pd.read_csv('data/processed/sidra_pam1612_temporarias.csv')")
    print("  pasto = mapb[mapb.class_id == 15]")
    print("  soja  = sidra[(sidra.categoria_id == 2713) & (sidra.variavel_id == 109)]")
    print("  juntos = pasto.merge(soja, on=['cd_mun','ano'], suffixes=('_mapb','_sidra'))")


if __name__ == "__main__":
    main()
