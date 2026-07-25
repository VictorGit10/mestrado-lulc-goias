"""processa_cubo_idade_destinos.py — reprocessa o cubo capturando destino=Mosaico
================================================================================

Estende o #28 (`processa_cubo_idade.py`) para registrar, além de
`pastagem → agricultura`, também `pastagem → Mosaico de Usos (21)`, COM a idade
do pasto e a origem — numa única passagem. Fecha:

  • o **bracket por EVENTO do #40** (redefinir a conversão como
    `pasto→(agric∪mosaico)`), que a tabela do #28 (só destino=agricultura) não
    permitia; e
  • a **demonstração pendente do #28D/D25**: o MESMO pixel que sairia da pastagem
    para agricultura passa a sair para Mosaico nos anos terminais — mostrado agora
    com idade, ano e localização, não só na contagem agregada.

Reusa integralmente a máquina do #28 (grade, LUT de classes, rasterização dos
municípios, decodificação, `area_ha`, centroide) via `import processa_cubo_idade`.
A ÚNICA diferença é a máscara de conversão: em vez de só `is_past[it-1] &
is_agri`, também `is_past[it-1] & (classe==21)`, acumulada em paralelo.

SAÍDA
    data/processed/pastagem_conversao_destinos.parquet
      colunas do #28 + `destino` ∈ {agricultura, mosaico}.
    Filtrar destino=agricultura reproduz o #28; a união é `agric∪mosaico`.

COMO RODAR
    python scripts/processa_cubo_idade_destinos.py --shards data/raw/cubo_go
    python scripts/processa_cubo_idade_destinos.py --shards data/raw/cubo_go --limite 1  (validação)

Quando foi feito: 2026-07-23.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402 — reuso integral da máquina do #28

ROOT = Path(__file__).resolve().parent.parent
PARQUET_SAIDA = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"
ID_MOSAICO = 21
DESTINOS = ("agricultura", "mosaico")


def _acumular(conv, it, age, plano, mj_plano, h, w, top, left, lats, lons,
              lut, acc, acc_lat, acc_lon) -> int:
    """Acumula os eventos de uma máscara `conv` (h×w bool) no ano `it`. Lógica de
    idade/origem/chave IDÊNTICA ao #28 — só a máscara de destino muda."""
    if not conv.any():
        return 0
    pos = np.flatnonzero(conv.reshape(-1))
    idade = age[it - 1].reshape(-1)[pos].astype(np.int32)
    if idade.min() < 1:
        raise RuntimeError(f"ano {pc.ANO_MIN + it}: idade {idade.min()} < 1 — dessincronizado")
    inicio = it - idade
    cens = inicio <= 0
    classe_idx = np.full(pos.shape, pc.IDX_CENSURADO, dtype=np.int64)
    if (~cens).any():
        flat = (inicio[~cens] - 1).astype(np.int64) * (h * w) + pos[~cens]
        classe_idx[~cens] = lut[plano[flat]]
    chave = ((mj_plano[pos].astype(np.int64) * pc.N_IDADE
              + np.clip(idade, 0, pc.N_IDADE - 1)) * pc.N_CLASSE + classe_idx)
    acc[it] += np.bincount(chave, minlength=acc.shape[1])
    rr, cc = np.divmod(pos, w)
    acc_lat[it] += np.bincount(chave, weights=lats[top + rr], minlength=acc.shape[1])
    acc_lon[it] += np.bincount(chave, weights=lons[left + cc], minlength=acc.shape[1])
    return int(pos.size)


def processar_shard(caminho: Path, gdf_muni, accs: dict, muni_stats, tam_janela):
    """accs = {destino: (acc, acc_lat, acc_lon)}. Acumula os DOIS destinos numa
    passagem. muni_stats (cos-lat) é acumulado uma vez (compartilhado)."""
    lut, _ = pc.construir_lookup_classe()
    is_agri = np.zeros(256, dtype=bool)
    is_agri[pc.IDS_AGRICULTURA] = True
    tot = {d: 0 for d in DESTINOS}

    with rasterio.open(caminho) as src:
        if src.count != pc.N_ANOS:
            raise RuntimeError(f"{caminho.name}: {src.count} bandas, esperado {pc.N_ANOS}")
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(src.height, src.width), transform=src.transform,
            fill=0, dtype=np.uint16)
        if not muni.any():
            return tot

        lats = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
        lons = src.transform.c + (np.arange(src.width) + 0.5) * pc.PX
        cos_lat = np.cos(np.radians(lats))
        for i in range(src.height):
            if not muni[i].any():
                continue
            b = np.bincount(muni[i], minlength=muni_stats.shape[0])
            muni_stats[:, 0] += b
            muni_stats[:, 1] += b * cos_lat[i]

        for top in range(0, src.height, tam_janela):
            for left in range(0, src.width, tam_janela):
                h = min(tam_janela, src.height - top)
                w = min(tam_janela, src.width - left)
                mj = muni[top:top + h, left:left + w]
                if not mj.any():
                    continue
                arr = np.ascontiguousarray(src.read(window=Window(left, top, w, h)))
                is_past = arr == pc.ID_PASTAGEM
                age = np.zeros_like(arr, dtype=np.int8)
                age[0] = is_past[0]
                for j in range(1, pc.N_ANOS):
                    age[j] = (age[j - 1] + 1) * is_past[j]
                plano = arr.reshape(-1)
                mj_plano = mj.reshape(-1)

                for it in range(1, pc.N_ANOS):
                    base = is_past[it - 1] & (mj > 0)
                    if not base.any():
                        continue
                    masks = {"agricultura": base & is_agri[arr[it]],
                             "mosaico": base & (arr[it] == ID_MOSAICO)}
                    for d in DESTINOS:
                        acc, acc_lat, acc_lon = accs[d]
                        tot[d] += _acumular(masks[d], it, age, plano, mj_plano, h, w,
                                            top, left, lats, lons, lut, acc, acc_lat, acc_lon)
    return tot


def main() -> None:
    import pandas as pd
    p = argparse.ArgumentParser(description="Reprocessa o cubo com destino=Mosaico (companheiro do #28)")
    p.add_argument("--shards", type=Path, required=True)
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--saida", type=Path, default=PARQUET_SAIDA,
                   help="Parquet de saída (default: pastagem_conversao_destinos.parquet, a 10.1)")
    args = p.parse_args()

    tifs = sorted(args.shards.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {args.shards}")

    # Detecta o nº de bandas do cubo e ajusta a máquina do #28 (que fixa 40=10.1).
    # A Coleção 9 tem 39 bandas (1985..2023); a 10.1, 40 (1985..2024). Só a contagem
    # de bandas muda entre elas — grade, IDs de classe e origem 1985 são idênticos —,
    # então sobrescrever pc.N_ANOS/ANO_MAX reusa TODA a máquina sem tocar no código do #28.
    with rasterio.open(tifs[0]) as _s:
        n_bandas = _s.count
    if n_bandas != pc.N_ANOS:
        pc.N_ANOS = n_bandas
        pc.ANO_MAX = pc.ANO_MIN + n_bandas - 1
        print(f"  cubo com {n_bandas} bandas -> ANO_MAX={pc.ANO_MAX} "
              f"(ajustado; padrão do #28 é 40/2024)")

    if args.limite:
        tifs = tifs[:args.limite]
        print("  (--limite ativo: verificação de partição pulada)")
    else:
        pc.verificar_particao(tifs)
    print(f"{len(tifs)} shard(s) | janela {args.janela}² | destinos: {DESTINOS} | "
          f"{pc.ANO_MIN}..{pc.ANO_MAX}")

    gdf_muni = pc.carregar_municipios()
    print(f"  {len(gdf_muni)} municípios")

    def novo_acc():
        a = np.zeros((pc.N_ANOS, (len(gdf_muni) + 1) * pc.N_IDADE * pc.N_CLASSE), dtype=np.int64)
        return a, np.zeros_like(a, dtype=np.float64), np.zeros_like(a, dtype=np.float64)

    accs = {d: novo_acc() for d in DESTINOS}
    muni_stats = np.zeros((len(gdf_muni) + 1, 2), dtype=np.float64)
    mb = sum(sum(x.nbytes for x in accs[d]) for d in DESTINOS) / 1e6
    print(f"  acumuladores: {mb:.0f} MB (2 destinos × contagem+lat+lon)")

    tot = {d: 0 for d in DESTINOS}
    for i, tif in enumerate(tifs, 1):
        t0 = time.time()
        n = processar_shard(tif, gdf_muni, accs, muni_stats, args.janela)
        for d in DESTINOS:
            tot[d] += n[d]
        print(f"[{i:02d}/{len(tifs)}] {tif.name} — agric {n['agricultura']:,} | "
              f"mosaico {n['mosaico']:,} ({time.time() - t0:.0f}s)")

    partes = []
    for d in DESTINOS:
        acc, acc_lat, acc_lon = accs[d]
        if acc.any():
            df = pc.decodificar(acc, acc_lat, acc_lon, gdf_muni, muni_stats)
            df["destino"] = d
            partes.append(df)
    if not partes:
        print("Nenhum evento de conversão (shards fora de GO?). Nada gravado.")
        return
    out = pd.concat(partes, ignore_index=True)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.saida, index=False)

    print(f"\n{'=' * 60}\nSAÍDA: {args.saida}")
    for d in DESTINOS:
        s = out[out.destino == d]
        print(f"  destino={d:12s}: {len(s):,} células | {s.n_pixels.sum():,} eventos "
              f"| {s.area_ha.sum():,.0f} ha")
    # Razão M/A por ano (a assinatura da mudança de rótulo) — sanidade rápida
    piv = out.groupby(["ano_conversao", "destino"])["n_pixels"].sum().unstack(fill_value=0)
    piv["razao_M/A"] = piv["mosaico"] / piv["agricultura"].replace(0, np.nan)
    print("\n  razão pasto→Mosaico / pasto→agricultura (deve explodir na cauda):")
    for ano in [2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
        if ano in piv.index:
            print(f"    {ano}: agric {piv.loc[ano,'agricultura']/1e6:5.3f}M | "
                  f"mosaico {piv.loc[ano,'mosaico']/1e6:5.3f}M | razão {piv.loc[ano,'razao_M/A']:.2f}")


if __name__ == "__main__":
    main()
