#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta o JSON da marcha ao norte para a visualização interativa (#32).

Lê os CSVs já computados pelo Pipeline #32 (`centro_massa.py`) e emite um único
`Visualizacao/assets/data/marcha_centro_massa.json` consumido por
`assets/js/marcha-mapa.js` — o mapa animado + a faixa latitude-tempo.

NÃO recomputa nada: só reempacota `data/processed/centro_massa_*.csv`. Assim o
export é leve (sem GEE, sem parquet) e reproduzível a partir dos CSVs versionados.

As elipses (SDE por ato) são amostradas na fronteira em coordenadas métricas
(EPSG:5880, onde `theta` e os semi-eixos foram calculados) e reprojetadas para
lon/lat (EPSG:4674) via geopandas — assim o d3 as desenha com a MESMA projeção
geográfica do mapa, sem misturar referenciais de ângulo.

Uso:
    python scripts/exportar_marcha_viz.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"

ARQ_ANUAL = DIR_PROCESSED / "centro_massa_anual.csv"
ARQ_ELIPSES = DIR_PROCESSED / "centro_massa_elipses.csv"
ARQ_DESLOC = DIR_PROCESSED / "centro_massa_deslocamento.csv"
ARQ_BOOT = DIR_PROCESSED / "centro_massa_bootstrap.csv"

ARQ_SAIDA = DIR_VIZ / "marcha_centro_massa.json"

CRS_METRICO = 5880
CRS_GEO = 4674

# chave-canônica -> (rótulo, cor). Espelha VARIAVEIS de centro_massa.py, mas com
# cores alinhadas à paleta do site (styles.css) onde há equivalente; rebanho
# ganha um vinho próprio (sem var no site).
VARIAVEIS = {
    "agricultura": ("Agricultura",       "#d96aa3"),  # rosa (= --color-agric)
    "pastagem":    ("Pastagem",           "#c79a2e"),  # âmbar escurecido p/ contraste do ponto
    "bovinos":     ("Rebanho bovino",     "#8e3b5a"),  # vinho
    "veg_natural": ("Vegetação natural",  "#2d5a3d"),  # verde (= --color-veg)
}

# Ordem de desenho / z-index (veg ao fundo, agricultura na frente).
ORDEM = ["veg_natural", "pastagem", "bovinos", "agricultura"]


def _elipse_boundary_lonlat(cx: float, cy: float, sig_maior_km: float,
                            sig_menor_km: float, theta_deg: float,
                            n: int = 72) -> list[list[float]]:
    """Amostra a fronteira 1σ da elipse em métricos e reprojeta p/ [lon,lat]."""
    import geopandas as gpd

    a = sig_maior_km * 1000.0   # semi-eixo maior em metros
    b = sig_menor_km * 1000.0
    th = np.radians(theta_deg)
    t = np.linspace(0, 2 * np.pi, n, endpoint=True)
    # elipse canônica -> rotação por theta (mesmo referencial do cálculo em #32)
    ex, ey = a * np.cos(t), b * np.sin(t)
    xr = cx + ex * np.cos(th) - ey * np.sin(th)
    yr = cy + ex * np.sin(th) + ey * np.cos(th)
    pts = gpd.GeoSeries(gpd.points_from_xy(xr, yr), crs=CRS_METRICO).to_crs(CRS_GEO)
    return [[round(float(x), 5), round(float(y), 5)] for x, y in zip(pts.x, pts.y)]


def main() -> None:
    anual = pd.read_csv(ARQ_ANUAL)
    desloc = pd.read_csv(ARQ_DESLOC)
    elipses = pd.read_csv(ARQ_ELIPSES)
    boot = pd.read_csv(ARQ_BOOT) if ARQ_BOOT.exists() else None

    anos = sorted(int(a) for a in anual["ano"].unique())

    liq_d = desloc[desloc["ato"] == "LÍQUIDO"].set_index("variavel")
    liq_b = (boot[boot["janela"] == "LÍQUIDO"].set_index("variavel")
             if boot is not None else None)

    variaveis = []
    for chave in ORDEM:
        rotulo, cor = VARIAVEIS[chave]
        sub = anual[anual["variavel"] == chave].sort_values("ano")
        pts = [{
            "a": int(r.ano),
            "lon": round(float(r.lon_mean), 5),
            "lat": round(float(r.lat_mean), 5),
            "lonM": round(float(r.lon_med), 5),
            "latM": round(float(r.lat_med), 5),
        } for r in sub.itertuples()]

        d = liq_d.loc[chave]
        liquido = {
            "dN": round(float(d.dnorte_km), 1),
            "dL": round(float(d.dleste_km), 1),
            "dtot": round(float(d.dtotal_km), 1),
            "az": round(float(d.azimute_deg), 1),
        }
        if liq_b is not None and chave in liq_b.index:
            b = liq_b.loc[chave]
            liquido.update({
                "lo": round(float(b.dN_lo), 1),
                "hi": round(float(b.dN_hi), 1),
                "robusto": bool(b.exclui_zero),
            })

        variaveis.append({
            "id": chave, "rotulo": rotulo, "cor": cor,
            "pts": pts, "liquido": liquido,
        })

    # elipses por ato (fronteira em lon/lat, prontas p/ d3.geoPath)
    els = []
    for r in elipses.itertuples():
        ring = _elipse_boundary_lonlat(
            r.cx, r.cy, r.sigma_maior_km, r.sigma_menor_km, r.theta_deg)
        els.append({
            "id": r.variavel, "ato": r.ato,
            "centro": [round(float(r.lon), 5), round(float(r.lat), 5)],
            "ring": ring,
        })

    atos = (elipses[["ato", "ato_titulo", "ano_ini", "ano_fim"]]
            .drop_duplicates().sort_values("ano_ini"))
    atos_out = [{
        "id": a.ato, "titulo": a.ato_titulo,
        "ini": int(a.ano_ini), "fim": int(a.ano_fim),
    } for a in atos.itertuples()]

    payload = {
        "meta": {
            "fonte": "Pipeline #32 (centro_massa.py) — painel AMC Goiás",
            "crs": "lon/lat EPSG:4674 (reprojetado de EPSG:5880 equal-area)",
            "nota": "ponto = centro médio ponderado; *M = centro mediano (Weiszfeld, robusto)",
        },
        "anos": anos,
        "atos": atos_out,
        "variaveis": variaveis,
        "elipses": els,
    }

    DIR_VIZ.mkdir(parents=True, exist_ok=True)
    ARQ_SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    kb = ARQ_SAIDA.stat().st_size / 1024
    print(f"[OK] {ARQ_SAIDA.relative_to(ROOT)}  ({kb:.1f} KB)")
    print(f"     {len(anos)} anos · {len(variaveis)} variáveis · "
          f"{len(els)} elipses · {len(atos_out)} atos")


if __name__ == "__main__":
    main()
