"""razao_destino_ano.py — razão pasto→agricultura vs pasto→Mosaico por ano (leve)
================================================================================

Versão MEMÓRIA-FRUGAL do #28D/`processa_cubo_idade_destinos.py`, para o teste da
borda-móvel (§9 do 28D). Aquele script acumula o cruzamento completo
(município × idade × classe_anterior × lat × lon × destino) — ~750 MB de
acumuladores + arrays transientes grandes — e estoura num laptop de 7,7 GB.

O teste da borda-móvel (Parte A) só precisa de UMA coisa: quantos pixels de
pastagem viraram **agricultura** e quantos viraram **Mosaico de Usos (21)** a
cada ano, dentro de Goiás. Sem idade, sem classe, sem centroide. Este script
conta só isso, com pico de memória ~200 MB (uma janela de bandas por vez, sem
array de idade nem somas de lat/lon).

Detecta o nº de bandas do cubo (Coleção 9 = 39 bandas/2023; 10.1 = 40/2024),
recorta a Goiás pelos polígonos IBGE (mesma máscara do #28) e grava um parquet no
MESMO schema do #28D (`ano_conversao, destino, n_pixels`) para
`borda_movel_colecao9.py` consumir sem alteração.

COMO RODAR
    python scripts/razao_destino_ano.py --shards data/raw/cubo_go_col9 \
        --saida data/processed/pastagem_conversao_destinos_col9.parquet

Quando: 2026-07-23. Companheiro do #28D / teste da Coleção 9.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402 — grade, IDs, municípios do #28

ROOT = Path(__file__).resolve().parent.parent
ID_MOSAICO = 21


def processar_shard(caminho: Path, gdf_muni, agric: np.ndarray, mosa: np.ndarray,
                    janela: int) -> int:
    lut_agri = np.zeros(256, dtype=bool)
    lut_agri[pc.IDS_AGRICULTURA] = True
    n_eventos = 0
    with rasterio.open(caminho) as src:
        nb = src.count
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(src.height, src.width), transform=src.transform,
            fill=0, dtype=np.uint16)
        if not muni.any():
            return 0
        for top in range(0, src.height, janela):
            for left in range(0, src.width, janela):
                h = min(janela, src.height - top)
                w = min(janela, src.width - left)
                go = muni[top:top + h, left:left + w] > 0
                if not go.any():
                    continue
                arr = src.read(window=Window(left, top, w, h))  # (nb,h,w) uint8
                for t in range(1, nb):
                    base = (arr[t - 1] == pc.ID_PASTAGEM) & go
                    if not base.any():
                        continue
                    at = arr[t]
                    na = int((base & lut_agri[at]).sum())
                    nm = int((base & (at == ID_MOSAICO)).sum())
                    agric[t] += na
                    mosa[t] += nm
                    n_eventos += na + nm
                del arr
    return n_eventos


def main() -> None:
    p = argparse.ArgumentParser(description="Razão pasto→agric vs pasto→Mosaico por ano (leve)")
    p.add_argument("--shards", type=Path, required=True)
    p.add_argument("--saida", type=Path, required=True)
    p.add_argument("--janela", type=int, default=1536)
    p.add_argument("--max-shards", type=int, default=0,
                   help="processa no máximo N shards não-feitos por invocação (0=todos)")
    args = p.parse_args()

    tifs = sorted(args.shards.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {args.shards}")
    with rasterio.open(tifs[0]) as s:
        nb = s.count
    ano_max = pc.ANO_MIN + nb - 1
    print(f"{len(tifs)} shard(s) | {nb} bandas -> {pc.ANO_MIN}..{ano_max} | janela {args.janela}²")

    # Checkpoint incremental: este ambiente mata tarefas de CPU longa (3 kills seguidos
    # ~1-2 shards; o monitor OCIOSO sobreviveu 19,9 min → parece orçamento de CPU, não
    # memória). Salva (agric, mosa, feitos) por shard num .npz irmão do parquet; ao
    # reiniciar, pula os shards já contados. Reinvocar até `TODOS OS SHARDS FEITOS`.
    ckpt = args.saida.with_suffix(".ckpt.npz")
    if ckpt.exists():
        z = np.load(ckpt, allow_pickle=True)
        agric = z["agric"].astype(np.int64)
        mosa = z["mosa"].astype(np.int64)
        feitos = set(z["feitos"].tolist())
        print(f"  checkpoint: {len(feitos)}/{len(tifs)} shards já contados")
    else:
        agric = np.zeros(nb, dtype=np.int64)
        mosa = np.zeros(nb, dtype=np.int64)
        feitos = set()

    gdf_muni = pc.carregar_municipios()
    print(f"  {len(gdf_muni)} municípios (recorte GO)")

    pendentes = [t for t in tifs if t.name not in feitos]
    if args.max_shards:
        pendentes = pendentes[:args.max_shards]
    for i, tif in enumerate(pendentes, 1):
        t0 = time.time()
        n = processar_shard(tif, gdf_muni, agric, mosa, args.janela)
        feitos.add(tif.name)
        np.savez(ckpt, agric=agric, mosa=mosa, feitos=np.array(sorted(feitos)))
        print(f"[{len(feitos):02d}/{len(tifs)}] {tif.name} — {n:,} eventos "
              f"({time.time() - t0:.0f}s) [checkpoint salvo]", flush=True)

    if len(feitos) < len(tifs):
        print(f"\nPARCIAL: {len(feitos)}/{len(tifs)} shards. Reinvoque para continuar.")
        return
    print(f"\nTODOS OS SHARDS FEITOS ({len(feitos)}/{len(tifs)}) — gravando parquet")

    linhas = []
    for t in range(1, nb):
        ano = pc.ANO_MIN + t
        if agric[t]:
            linhas.append({"ano_conversao": ano, "destino": "agricultura", "n_pixels": int(agric[t])})
        if mosa[t]:
            linhas.append({"ano_conversao": ano, "destino": "mosaico", "n_pixels": int(mosa[t])})
    out = pd.DataFrame(linhas)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.saida, index=False)
    ckpt.unlink(missing_ok=True)
    print(f"\nSAÍDA: {args.saida}")

    piv = out.pivot(index="ano_conversao", columns="destino", values="n_pixels").fillna(0)
    piv["razao_M_A"] = piv["mosaico"] / piv["agricultura"].replace(0, np.nan)
    print("\n  razão pasto→Mosaico / pasto→agricultura por ano (GO):")
    for ano in piv.index:
        if ano in (2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023, 2024) or ano == ano_max:
            print(f"    {ano}: agric {piv.loc[ano,'agricultura']/1e6:6.3f}M | "
                  f"mosaico {piv.loc[ano,'mosaico']/1e6:6.3f}M | razão {piv.loc[ano,'razao_M_A']:.2f}")


if __name__ == "__main__":
    main()
