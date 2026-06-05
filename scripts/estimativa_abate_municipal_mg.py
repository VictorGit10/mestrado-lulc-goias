"""
estimativa_abate_municipal_mg.py -- Estimativa municipal de abate para Minas Gerais
==========================================================================================

Adaptado de estimativa_abate_municipal.py (Goiás).
Distribui os valores estaduais de abate proporcionalmente ao efetivo de rebanho
municipal (PPM 3939).

Metodologia:
  abate_muni = (rebanho_muni / rebanho_UF) * abate_UF

Entradas:
  - data/processed/sidra_abate_mg_anual_mg.csv   (abate estadual, do coleta_sidra_mg.py)
  - data/processed/sidra_ppm3939_rebanhos_mg.csv  (efetivo de rebanho municipal)

Saidas:
  - data/processed/abate_municipal_estimado_mg.csv
  - data/processed/abate_mg_estadual.csv

Como rodar:
    python estimativa_abate_municipal_mg.py
    python estimativa_abate_municipal_mg.py --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"

ESPECIE_ABATE_REBANHO = {
    "bovino": "Bovino",
    "suino": "Su\xedno - total",
    "frango": "Galin\xe1ceos - total",
}

ABATE_CABECAS = 284
ABATE_PESO = 285


def carregar_abate_estadual() -> pd.DataFrame:
    path = DIR_PROCESSED / "sidra_abate_mg_anual_mg.csv"
    if not path.exists():
        print(f"[ERRO] {path} nao encontrado. Execute: python coleta_sidra_mg.py --abate")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"  [OK] abate estadual: {len(df)} linhas, {df['ano'].min()}-{df['ano'].max()}")
    return df


def carregar_rebanho_municipal() -> pd.DataFrame:
    path = DIR_PROCESSED / "sidra_ppm3939_rebanhos_mg.csv"
    if not path.exists():
        print(f"[ERRO] {path} nao encontrado. Execute: python coleta_sidra_mg.py")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"  [OK] rebanho municipal: {len(df)} linhas, {df['ano'].min()}-{df['ano'].max()}")
    return df


def montar_abate_estadual_wide(abate: pd.DataFrame) -> pd.DataFrame:
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

    out_path = DIR_PROCESSED / "abate_mg_estadual.csv"
    wide.to_csv(out_path, index=False)
    print(f"  -> abate_mg_estadual.csv ({len(wide)} linhas, anos {wide['ano'].min()}-{wide['ano'].max()})")
    return wide


def estimar_abate_municipal(
    abate: pd.DataFrame,
    rebanho: pd.DataFrame,
) -> pd.DataFrame:
    especies_rebanho = list(ESPECIE_ABATE_REBANHO.values())
    reb_filtrado = rebanho[rebanho["categoria"].isin(especies_rebanho)].copy()

    reb_para_abate = {v: k for k, v in ESPECIE_ABATE_REBANHO.items()}
    reb_filtrado["especie"] = reb_filtrado["categoria"].map(reb_para_abate)

    reb_total_uf = (
        reb_filtrado
        .groupby(["ano", "especie"])["valor"]
        .sum()
        .reset_index()
        .rename(columns={"valor": "rebanho_uf"})
    )

    abate_cab = abate[abate["variavel_id"] == ABATE_CABECAS][
        ["ano", "especie", "valor_anual"]
    ].rename(columns={"valor_anual": "abate_uf_cab"})

    abate_kg = abate[abate["variavel_id"] == ABATE_PESO][
        ["ano", "especie", "valor_anual"]
    ].rename(columns={"valor_anual": "abate_uf_kg"})

    reb_muni = reb_filtrado[["cd_mun", "nm_mun", "ano", "especie", "valor"]].rename(
        columns={"valor": "rebanho_muni"}
    )

    merged = reb_muni.merge(reb_total_uf, on=["ano", "especie"], how="left")
    merged = merged.merge(abate_cab, on=["ano", "especie"], how="left")
    merged = merged.merge(abate_kg, on=["ano", "especie"], how="left")

    merged["participacao_rebanho"] = merged["rebanho_muni"] / merged["rebanho_uf"]
    merged["abate_cab_est"] = (merged["participacao_rebanho"] * merged["abate_uf_cab"]).round(0)
    merged["abate_kg_est"] = (merged["participacao_rebanho"] * merged["abate_uf_kg"]).round(0)
    merged["taxa_abate"] = (merged["abate_uf_cab"] / merged["rebanho_uf"]).round(4)

    merged = merged.sort_values(["especie", "cd_mun", "ano"]).reset_index(drop=True)

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo se os CSVs ja existem")
    args = parser.parse_args()

    print("=" * 70)
    print("Estimativa municipal de abate -- Minas Gerais")
    print(f"  dados  -> {DIR_PROCESSED}")
    print("=" * 70)

    print("\n[1] Carregando abate estadual...")
    abate = carregar_abate_estadual()

    print("\n[2] Carregando rebanho municipal...")
    rebanho = carregar_rebanho_municipal()

    print("\n[3] Montando painel estadual wide...")
    montar_abate_estadual_wide(abate)

    print("\n[4] Calculando estimativa municipal de abate...")
    muni = estimar_abate_municipal(abate, rebanho)

    print()
    for esp in sorted(muni["especie"].unique()):
        sub = muni[muni["especie"] == esp]
        anos_disp = f"{sub['ano'].min()}-{sub['ano'].max()}" if len(sub) else "-"
        n_munis = sub["cd_mun"].nunique()
        print(f"  {esp:8s}: {len(sub):5d} linhas, {n_munis} municipios, anos {anos_disp}")

    out_path = DIR_PROCESSED / "abate_municipal_estimado_mg.csv"
    muni.to_csv(out_path, index=False)
    print(f"\n  -> abate_municipal_estimado_mg.csv ({len(muni)} linhas, "
          f"{muni['cd_mun'].nunique()} municipios, anos {muni['ano'].min()}-{muni['ano'].max()})")

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