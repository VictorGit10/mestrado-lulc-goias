"""
explorar_asset_fogo.py — Explorar assets de fogo MapBiomas Collection 4
========================================================================

Verifica bandas, valores de pixel e estrutura dos assets de fogo no GEE
antes de implementar o pipeline de coleta principal.

Assets a explorar:
  - mapbiomas_fire_collection4_annual_burned_v1 (área queimada binária)
  - mapbiomas_fire_collection4_annual_burned_coverage_v1 (queimada por classe LULC)

Como rodar:
    1. earthengine authenticate  (terminal Windows real)
    2. set GEE_PROJECT=extreme-height-447417-a9
    3. python "Scripts e Catalogo/explorar_asset_fogo.py"
"""
from __future__ import annotations

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee

GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"

# Possíveis paths do asset (confirmar via exploração)
ASSETS_CANDIDATOS = [
    "projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_annual_burned_v1",
    "projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_annual_burned_coverage_v1",
    # Alternativas caso o path acima não funcione
    "projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_burned_v1",
    "projects/mapbiomas-public/assets/brazil/fire/collection4/mapbiomas_fire_collection4_coverage_v1",
]

# Região de teste: Goiânia (código 5201108) — criada depois de init_ee()
GOIANIA_GEOM = None  # Inicializado em main() após ee.Initialize


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    if not project:
        sys.exit("Erro: defina GEE_PROJECT.")
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception as exc:
        print("Falha ao inicializar Earth Engine. Rode: earthengine authenticate")
        raise


def explorar_asset(asset_path: str) -> None:
    """Tenta carregar um asset e imprimir metadados."""
    print(f"\n{'='*70}")
    print(f"Explorando: {asset_path}")
    print(f"{'='*70}")

    try:
        img = ee.Image(asset_path)
        # Nome do asset
        print(f"Tipo: {img.name()}")

        # Bandas
        bandas = img.bandNames().getInfo()
        print(f"Número de bandas: {len(bandas)}")
        print(f"Primeiras 10 bandas: {bandas[:10]}")
        print(f"Últimas 5 bandas: {bandas[-5:]}")

        # Se houver bandas de ano, testar uma
        for banda_teste in [f"burned_area_2020", f"burned_coverage_2020",
                            f"burned_2020", f"fire_2020"]:
            if banda_teste in bandas:
                print(f"\nTestando banda '{banda_teste}':")
                img_banda = img.select(banda_teste)

                # Estatísticas na região de Goiânia
                stats = img_banda.reduceRegion(
                    reducer=ee.Reducer.minMax().combine(ee.Reducer.mean, "", True),
                    geometry=GOIANIA_GEOM,
                    scale=30,
                    maxPixels=1e6,
                ).getInfo()
                print(f"  Stats (buffer 5km Goiânia): {stats}")

                # Histograma (valores únicos)
                hist = img_banda.reduceRegion(
                    reducer=ee.Reducer.frequencyHistogram(),
                    geometry=GOIANIA_GEOM,
                    scale=30,
                    maxPixels=1e6,
                ).getInfo()
                print(f"  Histogram (buffer 5km Goiânia): {hist}")
                break
        else:
            # Se não encontrou banda padrão, testar a primeira banda
            if bandas:
                primeira = bandas[0]
                print(f"\nTestando primeira banda '{primeira}':")
                img_banda = img.select(primeira)
                stats = img_banda.reduceRegion(
                    reducer=ee.Reducer.minMax().combine(ee.Reducer.mean, "", True),
                    geometry=GOIANIA_GEOM,
                    scale=30,
                    maxPixels=1e6,
                ).getInfo()
                print(f"  Stats: {stats}")
                hist = img_banda.reduceRegion(
                    reducer=ee.Reducer.frequencyHistogram(),
                    geometry=GOIANIA_GEOM,
                    scale=30,
                    maxPixels=1e6,
                ).getInfo()
                print(f"  Histogram: {hist}")

    except Exception as exc:
        print(f"  ERRO: {exc}")


def main() -> None:
    global GOIANIA_GEOM
    init_ee()
    GOIANIA_GEOM = ee.Geometry.Point([-49.25, -16.69]).buffer(5000)

    # Tentar cada asset candidato
    for asset in ASSETS_CANDIDATOS:
        explorar_asset(asset)

    # Se nenhum candidato funcionar, tentar listar assets do projeto
    print(f"\n{'='*70}")
    print("Tentando listar assets em projects/mapbiomas-public/assets/brazil/fire/collection4/")
    print(f"{'='*70}")
    try:
        assets = ee.data.listAssets("projects/mapbiomas-public/assets/brazil/fire/collection4/")
        for a in assets.get("assets", [])[:10]:
            print(f"  {a.get('name', '?')} — tipo: {a.get('type', '?')}")
    except Exception as exc:
        print(f"  ERRO: {exc}")

    # Tentar listar assets raiz do fire
    print(f"\n{'='*70}")
    print("Tentando listar assets em projects/mapbiomas-public/assets/brazil/fire/")
    print(f"{'='*70}")
    try:
        assets = ee.data.listAssets("projects/mapbiomas-public/assets/brazil/fire/")
        for a in assets.get("assets", [])[:10]:
            print(f"  {a.get('name', '?')} — tipo: {a.get('type', '?')}")
    except Exception as exc:
        print(f"  ERRO: {exc}")


if __name__ == "__main__":
    main()