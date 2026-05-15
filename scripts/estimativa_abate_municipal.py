"""
estimativa_abate_municipal.py -- Estimativa municipal de abate a partir de dados estaduais
==========================================================================================

Os dados de abate (Pesquisa Trimestral do Abate, SIDRA tabelas 1092/1093/1094)
estao disponiveis apenas no nivel estadual (UF). Este script distribui os valores
estaduais proporcionalmente ao efetivo de rebanho municipal (PPM 3939), gerando
estimativas municipais anuais de cabecas abatidas e peso de carcaça.

Metodologia:
  abate_muni = (rebanho_muni / rebanho_UF) * abate_UF

  Premissa: a taxa de abate e uniforme dentro do estado. Essa simplificacao e
  comum na literatura e na pratica de estimativas municipais do IBGE quando dados
  diretos nao estao disponiveis.

Entradas:
  - data/processed/sidra_abate_goias_anual.csv   (abate estadual, do coleta_sidra.py)
  - data/processed/sidra_ppm3939_rebanhos.csv    (efetivo de rebanho municipal)

Saidas:
  - data/processed/abate_municipal_estimado.csv   (estimativa municipal)
  - data/processed/abate_goias_estadual.csv       (abate estadual limpo, formato wide)

Como rodar:
    python estimativa_abate_municipal.py
    python estimativa_abate_municipal.py --force   # reprocessa mesmo se os CSVs ja existem

Notas:
  - O periodo de abate (1997-2025) e mais curto que o de rebanho (1974-2024).
    A estimativa municipal so e calculada para anos onde ambos os dados existem.
  - Para especies sem rebanho municipal (frangos), usa-se o rebanho de galinaceos
    como proxy proporcional.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"

# Mapeamento de especie no abate -> especie no rebanho (PPM 3939)
# IMPORTANTE: os nomes das categorias no PPM 3939 usam acentos (á, í).
ESPECIE_ABATE_REBANHO = {
    "bovino": "Bovino",              # PPM 3939 categoria 2670
    "suino": "Su\xedno - total",     # PPM 3939 categoria 32794 ("Suíno - total")
    "frango": "Galin\xe1ceos - total",  # PPM 3939 categoria 32796 ("Galináceos - total")
}

# Variaveis do abate
ABATE_CABECAS = 284   # Animais abatidos (cabecas)
ABATE_PESO = 285      # Peso total das carcas (kg)


def carregar_abate_estadual() -> pd.DataFrame:
    """Carrega o painel anual de abate estadual (sidra_abate_goias_anual.csv)."""
    path = DIR_PROCESSED / "sidra_abate_goias_anual.csv"
    if not path.exists():
        print(f"[ERRO] {path} nao encontrado. Execute: python coleta_sidra.py --abate")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"  [OK] abate estadual: {len(df)} linhas, {df['ano'].min()}-{df['ano'].max()}")
    return df


def carregar_rebanho_municipal() -> pd.DataFrame:
    """Carrega o efetivo de rebanho municipal (PPM 3939)."""
    path = DIR_PROCESSED / "sidra_ppm3939_rebanhos.csv"
    if not path.exists():
        print(f"[ERRO] {path} nao encontrado. Execute: python coleta_sidra.py")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"  [OK] rebanho municipal: {len(df)} linhas, {df['ano'].min()}-{df['ano'].max()}")
    return df


def montar_abate_estadual_wide(abate: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o painel anual de abate (long) em formato wide:
    [uf_cod, uf_nome, ano, abate_bovino_cab, abate_bovino_kg, ...]

    Salva em data/processed/abate_goias_estadual.csv.
    """
    # Pivot: cada (especie, variavel_id) vira uma coluna
    abate["col_name"] = (
        "abate_" + abate["especie"] + "_"
        + abate["variavel_id"].map({ABATE_CABECAS: "cab", ABATE_PESO: "kg"})
    )
    wide = abate.pivot_table(
        index=["uf_cod", "uf_nome", "ano"],
        columns="col_name",
        values="valor_anual",
    ).reset_index()
    wide.columns.name = None
    wide = wide.sort_values("ano").reset_index(drop=True)

    out_path = DIR_PROCESSED / "abate_goias_estadual.csv"
    wide.to_csv(out_path, index=False)
    print(f"  -> abate_goias_estadual.csv ({len(wide)} linhas, anos {wide['ano'].min()}-{wide['ano'].max()})")
    return wide


def estimar_abate_municipal(
    abate: pd.DataFrame,
    rebanho: pd.DataFrame,
) -> pd.DataFrame:
    """
    Estima abate municipal proporcionalmente ao rebanho.

    Para cada (ano, especie):
      abate_muni = (rebanho_muni / sum_rebanho_UF) * abate_UF

    Retorna DataFrame com colunas:
      [cd_mun, nm_mun, ano, especie, abate_cab_est, abate_kg_est,
       rebanho_muni, rebanho_uf, participacao_rebanho]
    """
    # Filtrar rebanho apenas para as especies de interesse
    especies_rebanho = list(ESPECIE_ABATE_REBANHO.values())
    reb_filtrado = rebanho[rebanho["categoria"].isin(especies_rebanho)].copy()

    # Padronizar nome da especie no rebanho para o nome no abate
    reb_para_abate = {v: k for k, v in ESPECIE_ABATE_REBANHO.items()}
    reb_filtrado["especie"] = reb_filtrado["categoria"].map(reb_para_abate)

    # Total do rebanho por (ano, especie) em Goias
    reb_total_uf = (
        reb_filtrado
        .groupby(["ano", "especie"])["valor"]
        .sum()
        .reset_index()
        .rename(columns={"valor": "rebanho_uf"})
    )

    # Mesclar abate estadual com total do rebanho
    # Abate: variavel_id 284 = cabecas, 285 = peso kg
    abate_cab = abate[abate["variavel_id"] == ABATE_CABECAS][
        ["ano", "especie", "valor_anual"]
    ].rename(columns={"valor_anual": "abate_uf_cab"})

    abate_kg = abate[abate["variavel_id"] == ABATE_PESO][
        ["ano", "especie", "valor_anual"]
    ].rename(columns={"valor_anual": "abate_uf_kg"})

    # Join rebanho municipal + total UF + abate UF
    reb_muni = reb_filtrado[["cd_mun", "nm_mun", "ano", "especie", "valor"]].rename(
        columns={"valor": "rebanho_muni"}
    )

    merged = reb_muni.merge(reb_total_uf, on=["ano", "especie"], how="left")
    merged = merged.merge(abate_cab, on=["ano", "especie"], how="left")
    merged = merged.merge(abate_kg, on=["ano", "especie"], how="left")

    # Calcular participacao e estimar abate municipal
    merged["participacao_rebanho"] = merged["rebanho_muni"] / merged["rebanho_uf"]
    merged["abate_cab_est"] = (merged["participacao_rebanho"] * merged["abate_uf_cab"]).round(0)
    merged["abate_kg_est"] = (merged["participacao_rebanho"] * merged["abate_uf_kg"]).round(0)

    # Taxa de abate = cabecas abatidas / rebanho total
    merged["taxa_abate"] = (merged["abate_uf_cab"] / merged["rebanho_uf"]).round(4)

    merged = merged.sort_values(["especie", "cd_mun", "ano"]).reset_index(drop=True)

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo se os CSVs ja existem")
    args = parser.parse_args()

    print("=" * 70)
    print("Estimativa municipal de abate -- Goias")
    print(f"  dados  -> {DIR_PROCESSED}")
    print("=" * 70)

    # 1. Carregar dados
    print("\n[1] Carregando abate estadual...")
    abate = carregar_abate_estadual()

    print("\n[2] Carregando rebanho municipal...")
    rebanho = carregar_rebanho_municipal()

    # 2. Gerar painel estadual wide
    print("\n[3] Montando painel estadual wide...")
    abate_wide = montar_abate_estadual_wide(abate)

    # 3. Estimativa municipal
    print("\n[4] Calculando estimativa municipal de abate...")
    muni = estimar_abate_municipal(abate, rebanho)

    # Resumo por especie
    print()
    for esp in sorted(muni["especie"].unique()):
        sub = muni[muni["especie"] == esp]
        anos_disp = f"{sub['ano'].min()}-{sub['ano'].max()}" if len(sub) else "-"
        n_munis = sub["cd_mun"].nunique()
        print(f"  {esp:8s}: {len(sub):5d} linhas, {n_munis} municipios, anos {anos_disp}")

    # Salvar
    out_path = DIR_PROCESSED / "abate_municipal_estimado.csv"
    muni.to_csv(out_path, index=False)
    print(f"\n  -> abate_municipal_estimado.csv ({len(muni)} linhas, "
          f"{muni['cd_mun'].nunique()} municipios, anos {muni['ano'].min()}-{muni['ano'].max()})")

    # Verificacao rapida: comparar soma municipal com estadual
    print("\n[5] Verificacao: soma municipal vs. estadual (bovino, 2024)")
    check_ano = 2024
    check_esp = "bovino"
    abate_uf = abate[
        (abate["especie"] == check_esp)
        & (abate["ano"] == check_ano)
        & (abate["variavel_id"] == ABATE_CABECAS)
    ]["valor_anual"].sum()
    muni_sum = muni[
        (muni["especie"] == check_esp)
        & (muni["ano"] == check_ano)
    ]["abate_cab_est"].sum()
    print(f"  Abate UF (cabecas):  {abate_uf:>12,.0f}")
    print(f"  Soma municipal:     {muni_sum:>12,.0f}")
    if abate_uf > 0:
        print(f"  Razao:               {muni_sum / abate_uf:.4f} (esperado ~1.0)")

    print("\n" + "=" * 70)
    print("Concluido.")


if __name__ == "__main__":
    main()