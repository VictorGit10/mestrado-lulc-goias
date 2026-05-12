"""mapeamento_mesorregioes.py — Mapeia cd_mun → mesorregião para Goiás
=====================================================================

Usa geobr para baixar a malha de mesorregiões IBGE 2017 e fazer
spatial join com os municípios de Goiás (2020).

Decisão D6: usar mesorregiões IBGE 2017 (5 unidades para Goiás).
Não usar Regiões Geográficas Imediatas — malha alternativa 2017+
que pulveriza o painel (133 unidades em GO).

Saída:
    data/processed/mapeamento_mesorregioes.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import geobr
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
OUT_CSV = DIR_PROCESSED / "mapeamento_mesorregioes.csv"


def main() -> None:
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

    print("Baixando mesorregiões IBGE 2017 (Goiás)...")
    mesos = geobr.read_meso_region(code_meso="GO", year=2017)
    print(f"  {len(mesos)} mesorregiões: {mesos['name_meso'].tolist()}")

    print("Baixando municípios de Goiás (2020)...")
    munis = geobr.read_municipality(year=2020)
    go_munis = munis[munis["code_state"].astype(str).str.startswith("52")].copy()
    print(f"  {len(go_munis)} municípios")

    # Spatial join via centroid (evita polígonos sobrepostos de fronteira)
    go_munis = go_munis.to_crs(5880)  # projeção métrica para centroides corretos
    go_munis["centroid"] = go_munis.geometry.centroid
    go_munis_pts = go_munis.set_geometry("centroid")
    go_munis_pts = go_munis_pts.to_crs(4674)  # voltar para SIRGAS
    mesos_crs = mesos.to_crs(4674)

    joined = gpd.sjoin(go_munis_pts, mesos_crs[["code_meso", "name_meso", "geometry"]],
                        how="left", predicate="within")

    # Montar tabela de mapeamento
    mapping = joined[["code_muni", "name_muni", "code_meso", "name_meso"]].copy()
    mapping["cd_mun"] = mapping["code_muni"].astype(int)
    mapping["nm_mun"] = mapping["name_muni"]
    mapping["cod_meso"] = mapping["code_meso"].astype(int)
    mapping["nm_meso"] = mapping["name_meso"]
    mapping = mapping[["cd_mun", "nm_mun", "cod_meso", "nm_meso"]].sort_values("cd_mun").reset_index(drop=True)

    # Salvar
    mapping.to_csv(OUT_CSV, index=False)
    print(f"\nOK: {OUT_CSV.name} ({len(mapping)} municípios)")

    # Resumo
    print("\nMesorregiões:")
    for _, row in mapping.groupby("nm_meso").size().reset_index(name="n").iterrows():
        print(f"  {row['nm_meso']}: {row['n']} municípios")


if __name__ == "__main__":
    main()