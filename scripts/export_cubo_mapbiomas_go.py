"""export_cubo_mapbiomas_go.py — Pipeline #28 (coleta censitária)

Exporta o cubo completo MapBiomas 10.1 (40 bandas classification_1985..2024)
cobrindo o bbox de Goiás, via task batch do GEE para o Google Drive.

Substitui a amostragem do `coleta_idade_pastagem.py`, que sofria de dois
problemas: (a) amostrava o RETÂNGULO ENVOLVENTE de GO, colocando 43,7% dos
pixels fora do estado; (b) mesmo corrigida, entregava 0,01% do estado, deixando
52% dos municípios com <20 pixels não-censurados.

Decisões de projeto:

  - **bbox inteiro, sem máscara.** O GEE não opina sobre a fronteira do estado.
    O município de cada pixel vem de rasterização LOCAL dos polígonos do IBGE em
    precisão total (ver `processa_cubo_idade.py`). É o que desarma o bug do
    envelope: com censo + máscara local autoritativa, "fora do estado" deixa de
    ser um acidente de amostragem e vira um rótulo explícito por pixel.
  - **Grade nativa, sem reamostragem.** Exporta com `crsTransform` igual ao do
    asset (EPSG:4326, px=0,000269494585235856°), não com `scale=30`. Assim o
    pixel exportado é o pixel MapBiomas; a idade contada é exata.
  - **Sharding espacial com as 40 bandas juntas.** `fileDimensions=8192` faz o
    GEE cortar em ~16 tiles, cada um carregando a série temporal COMPLETA dos
    seus pixels. Cada shard é processável de forma independente — é o que
    permite rodar em janelas, sem carregar o cubo inteiro em memória.

Tamanho medido empiricamente (3 tiles amostrais, 2026-07-21): compressão de
27–41× (o land cover se repete no tempo), ~0,8 GB no total. Cabe no Drive.

Como rodar:
    1. earthengine authenticate
    2. set GEE_PROJECT=extreme-height-447417-a9
    3. python scripts/export_cubo_mapbiomas_go.py --teste     (1 shard, valida o caminho)
    4. python scripts/export_cubo_mapbiomas_go.py             (export completo)
    5. python scripts/export_cubo_mapbiomas_go.py --monitor   (acompanha as tasks)

Pré-requisitos:
    pip install earthengine-api geobr geopandas
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee

# ===== Configuração =====
GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"

ANO_MIN = 1985

# Coleções suportadas. A grade nativa (PX/ORIGEM) é a MESMA para as duas — a 9 e a
# 10.1 partilham a grade continental do MapBiomas (offset inteiro de 3253 col × 9300
# lin, conferido: resíduo < 1e-11 px). Exportar as duas com o MESMO crsTransform faz
# os shards co-registrarem pixel-a-pixel SEM reamostragem — pré-requisito do teste de
# borda-móvel da Coleção 9 (§9 do 28D_deriva_mosaico.md). A 9 termina em 2023 (39
# bandas); a 10.1 em 2024 (40 bandas). Pasta/prefixo distintos p/ não colidir no Drive.
COLECOES = {
    "10.1": dict(
        asset="projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1",
        ano_max=2024, pasta="mestrado_mapbiomas_go", prefixo="cubo_go_mapbiomas101"),
    "9": dict(
        asset="projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
        ano_max=2023, pasta="mestrado_mapbiomas_go_col9", prefixo="cubo_go_col9"),
}

# Grade nativa do asset MapBiomas (conferida via projection().getInfo(); igual na 9 e na 10.1)
PX = 0.00026949458523585647
ORIGEM_X = -74.02073025380652
ORIGEM_Y = 5.405791885246045

# bbox de Goiás (geobr, estado 2020) — margem de 1 px já embutida no snap
GO_BBOX = (-53.2486, -19.4984, -45.9072, -12.3950)

SHARD = 8192  # múltiplo de 256 (exigência do GeoTIFF tiled)


def init_ee() -> None:
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception:
        print("Falha ao inicializar Earth Engine. Rode: earthengine authenticate")
        raise


def bbox_na_grade(bbox: tuple[float, float, float, float]) -> dict:
    """Encaixa o bbox na grade nativa do MapBiomas, expandindo para fora.

    Sem isso o GEE reamostra para uma grade própria e os valores de classe
    passam por vizinho-mais-próximo — inofensivo em aparência, fatal para
    contagem de anos consecutivos (um pixel pode trocar de classe por
    reamostragem e zerar o contador de idade).
    """
    lon_min, lat_min, lon_max, lat_max = bbox
    col0 = math.floor((lon_min - ORIGEM_X) / PX)
    col1 = math.ceil((lon_max - ORIGEM_X) / PX)
    # eixo Y cresce para baixo (py negativo): origem no topo
    row0 = math.floor((ORIGEM_Y - lat_max) / PX)
    row1 = math.ceil((ORIGEM_Y - lat_min) / PX)

    x0 = ORIGEM_X + col0 * PX
    y0 = ORIGEM_Y - row0 * PX
    largura, altura = col1 - col0, row1 - row0
    return {
        "crs_transform": [PX, 0.0, x0, 0.0, -PX, y0],
        "largura": largura,
        "altura": altura,
        "x0": x0,
        "y0": y0,
        "x1": x0 + largura * PX,
        "y1": y0 - altura * PX,
    }


def montar_export(grade: dict, teste: bool, cfg: dict) -> ee.batch.Task:
    bandas = [f"classification_{a}" for a in range(ANO_MIN, cfg["ano_max"] + 1)]
    img = ee.Image(cfg["asset"]).select(bandas).toByte()

    if teste:
        largura = altura = SHARD
        desc = cfg["prefixo"] + "_TESTE"
    else:
        largura, altura = grade["largura"], grade["altura"]
        desc = cfg["prefixo"]

    x1 = grade["x0"] + largura * PX
    y1 = grade["y0"] - altura * PX
    region = ee.Geometry.Rectangle(
        [grade["x0"], y1, x1, grade["y0"]], proj="EPSG:4326", geodesic=False
    )

    return ee.batch.Export.image.toDrive(
        image=img,
        description=desc,
        folder=cfg["pasta"],
        fileNamePrefix=desc,
        region=region,
        crs="EPSG:4326",
        crsTransform=grade["crs_transform"],
        fileDimensions=[SHARD, SHARD],
        fileFormat="GeoTIFF",
        maxPixels=int(1e13),
    )


def monitorar(intervalo: int = 60, prefixo: str = "cubo_go") -> None:
    """Lista as tasks de export do projeto e acompanha até terminarem."""
    while True:
        # A descrição só é confiável via status(); `t.config` não a expõe nesta
        # versão da earthengine-api (1.7.x).
        estados = [t.status() for t in ee.batch.Task.list()]
        tasks = [s for s in estados if s.get("description", "").startswith(prefixo)]
        if not tasks:
            print("Nenhuma task cubo_go encontrada.")
            return
        ativos = 0
        print(f"\n--- {time.strftime('%H:%M:%S')} ---")
        for st in tasks[:20]:
            estado = st.get("state", "?")
            desc = st.get("description", "?")
            extra = ""
            if estado == "FAILED":
                extra = f" — {st.get('error_message', '')[:90]}"
            elif estado == "COMPLETED":
                secs = (st.get("update_timestamp_ms", 0) - st.get("start_timestamp_ms", 0)) / 1000
                extra = f" — {secs / 60:.1f} min"
            print(f"  {desc:28s} {estado}{extra}")
            if estado in ("READY", "RUNNING"):
                ativos += 1
        if ativos == 0:
            print("\nTodas as tasks terminaram.")
            return
        time.sleep(intervalo)


def main() -> None:
    p = argparse.ArgumentParser(description="Pipeline #28 — export censitário do cubo MapBiomas")
    p.add_argument("--colecao", choices=sorted(COLECOES), default="10.1",
                   help="Coleção MapBiomas a exportar (default 10.1; 9 p/ o teste de borda-móvel §9)")
    p.add_argument("--teste", action="store_true",
                   help="Exporta só 1 shard (8192²) para validar o caminho end-to-end")
    p.add_argument("--monitor", action="store_true",
                   help="Só acompanha as tasks já submetidas")
    p.add_argument("--intervalo", type=int, default=60)
    args = p.parse_args()

    cfg = COLECOES[args.colecao]
    bandas = [f"classification_{a}" for a in range(ANO_MIN, cfg["ano_max"] + 1)]

    init_ee()

    if args.monitor:
        monitorar(args.intervalo, prefixo=cfg["prefixo"])
        return

    grade = bbox_na_grade(GO_BBOX)
    nx = math.ceil(grade["largura"] / SHARD)
    ny = math.ceil(grade["altura"] / SHARD)
    px_total = grade["largura"] * grade["altura"]

    print(f"\nColeção {args.colecao} — {ANO_MIN}..{cfg['ano_max']} ({len(bandas)} bandas)")
    print(f"Grade alinhada ao MapBiomas:")
    print(f"  {grade['largura']:,} x {grade['altura']:,} px  ({px_total / 1e6:,.0f} Mpx/banda)")
    print(f"  origem  ({grade['x0']:.6f}, {grade['y0']:.6f})")
    print(f"  {len(bandas)} bandas -> {px_total * len(bandas) / 1e9:.1f} GB brutos")
    print(f"  ~{px_total * len(bandas) / 33 / 1e9:.2f} GB comprimidos (razão medida: 33x)")
    print(f"  sharding {SHARD}² -> {nx} x {ny} = {nx * ny} arquivos")

    if args.teste:
        print("\nMODO TESTE: 1 shard no canto noroeste do bbox")

    task = montar_export(grade, args.teste, cfg)
    task.start()
    st = task.status()
    print(f"\nTask submetida: {st.get('description')}  (id {st.get('id')})")
    print(f"Destino: Google Drive / {cfg['pasta']}/")
    print(f"\nAcompanhe com: python scripts/export_cubo_mapbiomas_go.py --colecao {args.colecao} --monitor")


if __name__ == "__main__":
    main()
