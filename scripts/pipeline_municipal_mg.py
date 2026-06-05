"""pipeline_municipal_mg.py — MapBiomas Coleção 10.1 no nível municipal de Minas Gerais
================================================================================

Filtra o xlsx nacional do MapBiomas para os 853 municípios de MG, derrete
para formato longo e junta com o código IBGE via SIDRA.

Adaptado de pipeline_municipal.py para MG.

Como rodar:
    python pipeline_municipal_mg.py

Pré-requisitos:
    - data/raw/mapbiomas_col10_estado.xlsx  (mesmo arquivo nacional)
    - data/processed/sidra_pam1612_temporarias_mg.csv

Saída:
    data/processed/mapbiomas_munis_mg.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT           = Path(__file__).resolve().parent.parent
ARQ_MAPBIOMAS = ROOT / "data" / "raw" / "mapbiomas_col10_estado.xlsx"
ARQ_SIDRA_REF = ROOT / "data" / "processed" / "sidra_pam1612_temporarias_mg.csv"
ARQ_SAIDA     = ROOT / "data" / "processed" / "mapbiomas_munis_mg.csv"

ABA_COBERTURA = "COVERAGE_10.1"
ANO_INI, ANO_FIM = 1985, 2024

CLASSES_NOME_PT = {
    1:  "Floresta",
    3:  "Floresta Nativa",
    4:  "Savana/Cerrado",
    5:  "Mangue",
    6:  "Floresta Alagável",
    9:  "Silvicultura",
    10: "Formação Natural não Florestal",
    11: "Área Úmida não Florestal",
    12: "Campo Natural",
    15: "Pastagem",
    18: "Agricultura",
    19: "Lavoura Temporária",
    20: "Cana",
    21: "Mosaio de Agricultura e Pastagem",
    23: "Praia e Duna",
    24: "Área Urbanizada",
    25: "Outra Área não Vegetada",
    26: "Corpo d'água não Natural",
    27: "Não Observado",
    29: "Afloramento Rochoso",
    30: "Mineração",
    31: "Aquicultura",
    32: "Apicum",
    33: "Rio, Lago e Oceano",
    34: "Porto",
    35: "Dendê",
    36: "Lavoura Perene",
    39: "Soja",
    40: "Arroz",
    41: "Outras Lavouras Temporárias",
    46: "Café",
    47: "Citrus",
    48: "Outras Lavouras Perenes",
    49: "Restinga Arbustiva",
    50: "Restinga Herbácea",
    62: "Algodão",
    75: "Usina Fotovoltaica",
}

CLASSES_LEVEL1 = {0: "Natural", 1: "Antropizado", 2: "Água"}


def main():
    print("Lendo xlsx MapBiomas (aba COVERAGE_10.1)...")
    df = pd.read_excel(ARQ_MAPBIOMAS, sheet_name=ABA_COBERTURA)
    print(f"  Total nacional: {len(df):,} linhas")

    # Filtrar MG
    df_mg = df[df["state_acronym"] == "MG"].copy()
    print(f"  MG: {len(df_mg):,} linhas, {df_mg['municipality'].nunique()} municípios")

    # Derreter anos
    anos = list(range(ANO_INI, ANO_FIM + 1))
    id_vars = ["country", "biome", "state", "state_acronym", "municipality",
                "class_id", "class_level_0", "class_level_1", "class_level_2", "class_level_3"]
    # Verificar quais colunas existem
    anos_disp = [a for a in anos if a in df_mg.columns]
    id_vars_disp = [c for c in id_vars if c in df_mg.columns]

    longo = df_mg.melt(
        id_vars=id_vars_disp,
        value_vars=anos_disp,
        var_name="ano",
        value_name="area_ha",
    )
    longo["ano"] = longo["ano"].astype(int)

    # Soma por municipio+ano+classe (pode haver mais de 1 bioma por municipio)
    agregado = longo.groupby(
        ["municipality", "ano", "class_id", "class_level_0", "class_level_1", "class_level_2", "class_level_3"],
        as_index=False,
    )["area_ha"].sum()

    # Adicionar nome PT da classe
    agregado["class_nome"] = agregado["class_id"].map(CLASSES_NOME_PT).fillna("Desconhecido")

    # Merge com código IBGE via SIDRA
    print("Merge com código IBGE via SIDRA...")
    sidra = pd.read_csv(ARQ_SIDRA_REF)
    if "cd_mun" not in sidra.columns and "cd_mun" in sidra.columns:
        sidra = sidra.rename(columns={"cd_mun": "cd_mun"})

    # Criar lookup de municipio -> cd_mun
    lookup = sidra[["cd_mun", "nm_mun"]].drop_duplicates()
    lookup["nm_mun_norm"] = lookup["nm_mun"].str.upper().str.strip()

    agregado["municipality_norm"] = agregado["municipality"].str.upper().str.strip()
    # Remover sufixo " - MG" se existir
    agregado["municipality_norm"] = agregado["municipality_norm"].str.replace(r"\s*-\s*MG\s*$", "", regex=True)

    # Merge
    com_codigo = agregado.merge(
        lookup[["cd_mun", "nm_mun_norm"]],
        left_on="municipality_norm",
        right_on="nm_mun_norm",
        how="left",
    )
    sem_codigo = com_codigo[com_codigo["cd_mun"].isna()]
    if len(sem_codigo) > 0:
        print(f"  [AVISO] {sem_codigo['municipality'].nunique()} municípios sem código IBGE")
        # Mostrar alguns exemplos
        for _, row in sem_codigo.head(10).iterrows():
            print(f"    {row['municipality']}")

    # Limpar e reordenar colunas
    com_codigo["cd_mun"] = com_codigo["cd_mun"].astype("Int64")
    saida = com_codigo[["cd_mun", "municipality", "ano", "class_id",
                         "class_level_0", "class_level_1", "class_level_2",
                         "class_level_3", "class_nome", "area_ha"]].copy()
    saida = saida.rename(columns={"municipality": "nm_mun"})
    saida = saida.sort_values(["cd_mun", "ano", "class_id"]).reset_index(drop=True)

    saida.to_csv(ARQ_SAIDA, index=False)
    print(f"\nSaída: {ARQ_SAIDA}")
    print(f"  {len(saida):,} registros, {saida['cd_mun'].nunique()} municípios, "
          f"{saida['ano'].min()}-{saida['ano'].max()}")


if __name__ == "__main__":
    main()