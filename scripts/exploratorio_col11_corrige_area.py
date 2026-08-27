"""exploratorio_col11_corrige_area.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. Exploratório da Coleção 11; não toca em nada da dissertação.

O DEFEITO QUE ESTE SCRIPT CONSERTA
----------------------------------
A primeira versão do `exploratorio_col11_censo_local.py` converteu contagem de pixels em
hectares com **0,09 ha por pixel fixo**. Está errado: a grade do MapBiomas é EPSG:4326, e
a largura do pixel encolhe com cos(latitude). Pelo #28, um pixel tem
`PX² × 111320 × 110574` = 894 m² no equador, o que a −16,3° dá ~858 m² = 0,0858 ha.

O sintoma foi a área total de Goiás sair 35,614 Mha em vez de 34,024 Mha — 4,67% a mais,
constante em todo ano, que é exatamente 0,09/0,0858. O `n_pixels` e as latitudes estavam
corretos; só a coluna `area_ha` saiu inflada.

O script já foi corrigido para acumular cos(lat) nativamente. Este corretor existe para
não desperdiçar a varredura de 45 minutos do cubo da 11, que já está feita.

COMO CORRIGE, E COM QUE EXATIDÃO
--------------------------------
`censo_munis_*.csv` — recalcula `cos(lat)` MÉDIO OBSERVADO por município varrendo apenas a
rasterização dos municípios sobre os shards (sem ler nenhuma banda: é rápido). É o mesmo
método do #28, então o resultado é **idêntico** ao que o script corrigido produziria.

`centro_massa_classe_*.csv` — usa `cos(lat_média_da_classe)` em vez de `média(cos(lat))`.
A diferença é o termo de Jensen, que sobre a faixa de latitude de Goiás (~7°) vale ~0,03%
da área. Declarado aqui porque é aproximação, não identidade.

COMO RODAR
    python scripts/exploratorio_col11_corrige_area.py --tag col11 --shards data/raw/cubo_go_col11

Quando: 2026-08-27.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "processed" / "exploratorio_col11"
AREA_PX_EQUADOR = pc.PX * pc.PX * 111320.0 * 110574.0  # m² no equador


def cos_medio_por_municipio(shards: Path, gdf_muni) -> np.ndarray:
    """cos(lat) médio observado de cada município, varrendo só a máscara municipal."""
    n = len(gdf_muni) + 1
    stats = np.zeros((n, 2), dtype=np.float64)  # [n_px, soma cos(lat)]
    for t in sorted(shards.glob("*.tif")):
        with rasterio.open(t) as src:
            muni = rasterize(
                ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
                out_shape=(src.height, src.width), transform=src.transform,
                fill=0, dtype=np.uint16)
            if not muni.any():
                continue
            lats = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
            cl = np.cos(np.radians(lats))
            for i in range(src.height):
                linha = muni[i]
                if not linha.any():
                    continue
                b = np.bincount(linha, minlength=n)
                stats[:, 0] += b
                stats[:, 1] += b * cl[i]
        print(f"  {t.name} lido", flush=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(stats[:, 0] > 0, stats[:, 1] / stats[:, 0], np.nan)


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — corrige area_ha do censo local")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--shards", type=Path, required=True)
    args = ap.parse_args()

    gdf = pc.carregar_municipios()
    print(f"cos(lat) médio por município, varrendo a máscara de {args.shards}:")
    cosm = cos_medio_por_municipio(args.shards, gdf)
    area_px_ha = cosm * AREA_PX_EQUADOR / 10_000.0
    cd_para_idx = gdf.set_index("cd_mun")["muni_idx"].to_dict()
    print(f"\n  cos(lat) de {np.nanmin(cosm):.5f} (sul) a {np.nanmax(cosm):.5f} (norte)")
    print(f"  área do pixel: {np.nanmin(area_px_ha):.5f} a {np.nanmax(area_px_ha):.5f} ha "
          f"(o valor errado era 0,09000)")

    f = DIR_SAIDA / f"censo_munis_{args.tag}.csv"
    if f.exists():
        d = pd.read_csv(f, encoding="utf-8")
        antes = d[d.ano == d.ano.max()].area_ha.sum() / 1e6
        idx = d.cd_mun.map(cd_para_idx).to_numpy()
        d["area_ha"] = d.n_pixels.to_numpy() * area_px_ha[idx]
        d.to_csv(f, index=False)
        depois = d[d.ano == d.ano.max()].area_ha.sum() / 1e6
        print(f"\n  {f.name}: {antes:.4f} -> {depois:.4f} Mha  (Goiás = 34,0243 Mha)")

    g = DIR_SAIDA / f"centro_massa_classe_{args.tag}.csv"
    if g.exists():
        d = pd.read_csv(g, encoding="utf-8")
        antes = d[d.ano == d.ano.max()].area_ha.sum() / 1e6
        # aproximação declarada: cos(lat_média) no lugar de média(cos(lat)); ~0,03%
        d["area_ha"] = d.n_pixels * np.cos(np.radians(d.lat)) * AREA_PX_EQUADOR / 10_000.0
        d.to_csv(g, index=False)
        depois = d[d.ano == d.ano.max()].area_ha.sum() / 1e6
        print(f"  {g.name}: {antes:.4f} -> {depois:.4f} Mha  "
              f"(aprox. de Jensen ~0,03%)")

    print("\n  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
