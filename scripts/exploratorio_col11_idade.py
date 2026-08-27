"""exploratorio_col11_idade.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html, qualificacao/ nem cria pipeline novo.

O QUE FAZ
---------
Replica o **Capítulo 2 do dossiê** (a queda na idade das conversões, de 22 para 4 anos) na
Coleção 11. É a pergunta de onde a investigação inteira nasceu, e ela ganha um teste novo
agora: a col11 encontra ~3× mais conversão pasto→lavoura nos anos recentes que a 10.1. A
pergunta é se essas conversões a mais são de pasto VELHO (o que restauraria a mediana de
idade e sugeriria que a 10.1 estava perdendo conversão madura) ou de pasto NOVO (o que
manteria o colapso e apontaria para outra coisa).

⚠️ POR QUE UM WRAPPER, E NÃO RODAR O #28 DIRETO
-----------------------------------------------
`processa_cubo_idade.py` grava num caminho FIXO — `data/processed/pastagem_idade_censo.parquet`,
que é artefato da dissertação. Rodá-lo com `--shards data/raw/cubo_go_col11` sobrescreveria
o censo da 10.1 com o da 11 sem aviso. Este wrapper desvia `pc.PARQUET_SAIDA` para a pasta
do exploratório ANTES de chamar o `main()`, e ajusta `pc.N_ANOS/ANO_MAX` para as 41 bandas
(o #28 fixa 40). Mesmo padrão do `processa_cubo_idade_destinos.py`; nenhuma linha do #28 é
tocada.

COMO RODAR
    python scripts/exploratorio_col11_idade.py                       (cubo da 11)
    python scripts/exploratorio_col11_idade.py --limite 2            (validação rápida)

Quando: 2026-08-27.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHARDS_PADRAO = ROOT / "data" / "raw" / "cubo_go_col11"
SAIDA = ROOT / "data" / "processed" / "exploratorio_col11" / "pastagem_idade_censo_col11.parquet"


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — idade das conversões na Coleção 11")
    ap.add_argument("--shards", type=Path, default=SHARDS_PADRAO)
    ap.add_argument("--janela", type=int, default=2048)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--saida", type=Path, default=SAIDA)
    args = ap.parse_args()

    tifs = sorted(args.shards.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {args.shards}")
    with rasterio.open(tifs[0]) as s:
        n_bandas = s.count

    if args.saida.resolve() == pc.PARQUET_SAIDA.resolve():
        sys.exit("RECUSADO: a saída aponta para o parquet da dissertação.")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    pc.PARQUET_SAIDA = args.saida            # desvia ANTES do main() do #28
    if n_bandas != pc.N_ANOS:
        pc.N_ANOS = n_bandas
        pc.ANO_MAX = pc.ANO_MIN + n_bandas - 1

    print("EXPLORATÓRIO — Cap. 2 do dossiê replicado na Coleção 11")
    print(f"  shards: {args.shards}")
    print(f"  {n_bandas} bandas -> {pc.ANO_MIN}..{pc.ANO_MAX}")
    print(f"  saída DESVIADA para: {pc.PARQUET_SAIDA}")
    print(f"  (o parquet da dissertação, {pc.__name__}.PARQUET_SAIDA original, está intacto)\n")

    # Laço próprio em vez de pc.main(): o main() do #28 varre os 16 shards sem
    # checkpoint, e esta rodada já perdeu três trabalhos longos para interrupções de
    # origem desconhecida. Aqui o acumulador inteiro é gravado depois de CADA shard e
    # os já lidos são pulados, então retomar continua de onde parou. As funções
    # chamadas são as do #28, sem alteração — só a orquestração é local.
    if args.limite:
        tifs_uso = tifs[:args.limite]
        print('  (--limite ativo: verificação de partição pulada)')
    else:
        tifs_uso = tifs
        pc.verificar_particao(tifs_uso)

    gdf_muni = pc.carregar_municipios()
    n_muni = len(gdf_muni)
    print(f'  {n_muni} municípios | {len(tifs_uso)} shards')

    ckpt = args.saida.with_suffix('.ckpt.npz')
    if ckpt.exists():
        z = np.load(ckpt, allow_pickle=True)
        if int(z['n_anos']) != pc.N_ANOS:
            sys.exit(f'checkpoint {ckpt.name} é de um cubo com outro número de bandas; apague-o.')
        acc = z['acc']; acc_lat = z['acc_lat']; acc_lon = z['acc_lon']
        muni_stats = z['muni_stats']; feitos = set(z['feitos'].tolist())
        total = int(z['total']); distintos = int(z['distintos']); z.close()
        print(f'  checkpoint: {len(feitos)}/{len(tifs_uso)} shards já lidos')
    else:
        acc = np.zeros((pc.N_ANOS, (n_muni + 1) * pc.N_IDADE * pc.N_CLASSE), dtype=np.int64)
        acc_lat = np.zeros_like(acc, dtype=np.float64)
        acc_lon = np.zeros_like(acc, dtype=np.float64)
        muni_stats = np.zeros((n_muni + 1, 2), dtype=np.float64)
        feitos, total, distintos = set(), 0, 0
    print(f'  acumulador: {(acc.nbytes + acc_lat.nbytes + acc_lon.nbytes) / 1e6:.0f} MB')

    for k, tif in enumerate(tifs_uso, 1):
        if tif.name in feitos:
            continue
        t0 = time.time()
        n, d = pc.processar_shard(tif, gdf_muni, acc, acc_lat, acc_lon, muni_stats, args.janela)
        total += n; distintos += d; feitos.add(tif.name)
        np.savez(ckpt, acc=acc, acc_lat=acc_lat, acc_lon=acc_lon, muni_stats=muni_stats,
                 feitos=np.array(sorted(feitos)), total=total, distintos=distintos,
                 n_anos=pc.N_ANOS)
        print(f'  [{k:02d}/{len(tifs_uso)}] {tif.name} — {n:,} eventos '
              f'({time.time() - t0:.0f}s) [ckpt]', flush=True)

    if total == 0:
        sys.exit('Nenhum evento de conversão encontrado.')

    df = pc.decodificar(acc, acc_lat, acc_lon, gdf_muni, muni_stats)
    df.to_parquet(args.saida, index=False)
    ckpt.unlink(missing_ok=True)  # só agora: o parquet está em disco
    print(f'  {total:,} eventos | {distintos:,} pixels distintos')
    print(f'  {df.area_ha.sum():,.0f} ha convertidos')
    print(f'  -> {args.saida}')
    print("\n  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
