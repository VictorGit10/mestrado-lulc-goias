"""exploratorio_col11_censo_local.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html, qualificacao/ nem cria pipeline novo.

POR QUE ESTE SCRIPT É A BASE DE TUDO
------------------------------------
As leituras anteriores desta rodada saíram do GEE sobre o polígono `FAO/GAUL/2015`. Isso
introduz um viés sistemático de ~5% contra os números do dossiê, que são censo local sobre
a **malha municipal do IBGE** (via geobr, 246 municípios). Medido: estoque de Agricultura
em 2024 dá 6,039 Mha pelo GAUL e 5,732 Mha pela malha do IBGE.

Para o par 10.1 × 11 ser comparável ao dossiê, ele tem que rodar na régua do dossiê: censo
completo, 30 m nativos, máscara municipal autoritativa. É o que este script faz — uma
varredura dos shards de um cubo produzindo DUAS bases exatas de uma vez só:

  (a) área por município × classe × ano   -> estoques (Cap. 4) e correlação municipal (Cap. 7)
  (b) centro de massa pixel-ponderado por classe × ano -> latitude/longitude médias (Cap. 7)

O (b) segue a definição do Pipeline #43: a posição de cada pixel é o próprio pixel, sem
passar por polígono administrativo, então não há MAUP. A diferença é que aqui os pixels
fora da malha do IBGE são EXCLUÍDOS (o #43 usa o contorno do estado no GEE); é a mesma
máscara do #28, que é a autoridade sobre "dentro de Goiás".

REUSO
-----
Importa `processa_cubo_idade` e usa a grade, os IDs e o `carregar_municipios()` dele. A
contagem de bandas é autodetectada, como no `processa_cubo_idade_destinos.py`, então o cubo
da 11 (41 bandas, 1985..2025) entra sem tocar no código do #28.

COMO RODAR
    python scripts/exploratorio_col11_censo_local.py --shards data/raw/cubo_go       --tag col10_1
    python scripts/exploratorio_col11_censo_local.py --shards data/raw/cubo_go_col11 --tag col11

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
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402 — grade, IDs e municípios do #28

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "processed" / "exploratorio_col11"

N_CLASSES = 256

# ⚠️ O pixel NÃO tem 0,09 ha. A grade do MapBiomas é EPSG:4326, então a largura do
# pixel encolhe com cos(latitude): 894 m² no equador, ~858 m² a -16,3°. Usar 0,09 ha
# fixo inflava a área do estado em 4,7% (35,61 Mha em vez de 34,02). É a mesma
# constante e o mesmo método do #28 (`AREA_PX_EQUADOR` + cos(lat) médio observado por
# município), para que este censo seja comparável com `mapbiomas_munis_goias.csv`.
AREA_PX_EQUADOR = pc.PX * pc.PX * 111320.0 * 110574.0  # m² no equador


def processar_shard(caminho: Path, gdf_muni, acc_mc: np.ndarray,
                    acc_lat: np.ndarray, acc_lon: np.ndarray,
                    acc_n: np.ndarray, acc_cos: np.ndarray,
                    muni_stats: np.ndarray, janela: int) -> None:
    """Acumula, para UM shard: contagem por (ano, muni, classe) em `acc_mc`, e
    soma de lat/lon e contagem por (ano, classe) em `acc_lat/lon/n`.

    Só entram pixels com muni_idx > 0 — isto é, dentro da malha do IBGE. É o que
    faz este censo bater com o do dossiê em vez de com o polígono GAUL.
    """
    n_muni = len(gdf_muni)
    with rasterio.open(caminho) as src:
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(src.height, src.width), transform=src.transform,
            fill=0, dtype=np.uint16)
        if not muni.any():
            return
        # latitude do CENTRO de cada linha; longitude do centro de cada coluna
        lats_lin = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
        lons_col = src.transform.c + (np.arange(src.width) + 0.5) * pc.PX

        for top in range(0, src.height, janela):
            for left in range(0, src.width, janela):
                h = min(janela, src.height - top)
                w = min(janela, src.width - left)
                mj = muni[top:top + h, left:left + w] > 0
                if not mj.any():
                    continue
                win = Window(left, top, w, h)
                mid = muni[top:top + h, left:left + w][mj].astype(np.int64)
                lat = np.broadcast_to(lats_lin[top:top + h, None], (h, w))[mj]
                lon = np.broadcast_to(lons_col[None, left:left + w], (h, w))[mj]
                # [n_px, soma cos(lat)] por município -> converte contagem em hectares
                cl = np.cos(np.radians(lat))
                muni_stats[:, 0] += np.bincount(mid, minlength=muni_stats.shape[0])
                muni_stats[:, 1] += np.bincount(mid, weights=cl, minlength=muni_stats.shape[0])
                for it in range(pc.N_ANOS):
                    cls = src.read(it + 1, window=win)[mj].astype(np.int64)
                    acc_mc[it] += np.bincount(mid * N_CLASSES + cls,
                                              minlength=(n_muni + 1) * N_CLASSES)
                    acc_lat[it] += np.bincount(cls, weights=lat, minlength=N_CLASSES)
                    acc_lon[it] += np.bincount(cls, weights=lon, minlength=N_CLASSES)
                    acc_n[it] += np.bincount(cls, minlength=N_CLASSES)
                    acc_cos[it] += np.bincount(cls, weights=cl, minlength=N_CLASSES)


def main() -> None:
    p = argparse.ArgumentParser(description="EXPLORATÓRIO — censo local por muni/classe + centro de massa")
    p.add_argument("--shards", type=Path, required=True)
    p.add_argument("--tag", required=True, help="rótulo da coleção na saída (ex.: col11)")
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--limite", type=int, default=0)
    args = p.parse_args()

    tifs = sorted(args.shards.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {args.shards}")

    with rasterio.open(tifs[0]) as _s:
        n_bandas = _s.count
    if n_bandas != pc.N_ANOS:
        pc.N_ANOS = n_bandas
        pc.ANO_MAX = pc.ANO_MIN + n_bandas - 1
        print(f"  cubo com {n_bandas} bandas -> ANO_MAX={pc.ANO_MAX}")

    if args.limite:
        tifs = tifs[:args.limite]
        print("  (--limite ativo: verificação de partição pulada)")
    else:
        pc.verificar_particao(tifs)

    gdf_muni = pc.carregar_municipios()
    n_muni = len(gdf_muni)
    print(f"{len(tifs)} shard(s) | {n_muni} municípios | {pc.ANO_MIN}..{pc.ANO_MAX}")

    # Checkpoint por shard: a varredura leva ~45 min por cubo e já foi interrompida
    # uma vez. Cada shard grava o acumulador inteiro; reinvocar continua de onde parou.
    ckpt = DIR_SAIDA / f"censo_local_{args.tag}.ckpt.npz"
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    if ckpt.exists():
        z = np.load(ckpt, allow_pickle=True)
        if int(z["n_anos"]) != pc.N_ANOS:
            sys.exit(f"checkpoint {ckpt.name} é de um cubo com {int(z['n_anos'])} bandas; apague-o.")
        acc_mc = z["acc_mc"]; acc_lat = z["acc_lat"]; acc_lon = z["acc_lon"]; acc_n = z["acc_n"]
        muni_stats = z["muni_stats"]; acc_cos = z["acc_cos"]
        feitos = set(z["feitos"].tolist()); z.close()
        print(f"  checkpoint: {len(feitos)}/{len(tifs)} shards já lidos")
    else:
        acc_mc = np.zeros((pc.N_ANOS, (n_muni + 1) * N_CLASSES), dtype=np.int64)
        acc_lat = np.zeros((pc.N_ANOS, N_CLASSES), dtype=np.float64)
        acc_lon = np.zeros((pc.N_ANOS, N_CLASSES), dtype=np.float64)
        acc_n = np.zeros((pc.N_ANOS, N_CLASSES), dtype=np.int64)
        acc_cos = np.zeros((pc.N_ANOS, N_CLASSES), dtype=np.float64)
        muni_stats = np.zeros((n_muni + 1, 2), dtype=np.float64)
        feitos = set()

    for k, t in enumerate(tifs, 1):
        if t.name in feitos:
            continue
        t0 = time.time()
        processar_shard(t, gdf_muni, acc_mc, acc_lat, acc_lon, acc_n, acc_cos,
                        muni_stats, args.janela)
        feitos.add(t.name)
        np.savez(ckpt, acc_mc=acc_mc, acc_lat=acc_lat, acc_lon=acc_lon, acc_n=acc_n,
                 acc_cos=acc_cos, muni_stats=muni_stats,
                 feitos=np.array(sorted(feitos)), n_anos=pc.N_ANOS)
        print(f"  [{k:02d}/{len(tifs)}] {t.name} ({time.time() - t0:.0f}s) [ckpt]", flush=True)

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)

    # (a) área por município × classe × ano
    linhas = []
    cod = gdf_muni.set_index("muni_idx")["cd_mun"].to_dict()
    nom = gdf_muni.set_index("muni_idx")["nm_mun"].to_dict()
    with np.errstate(invalid="ignore", divide="ignore"):
        cos_medio = np.where(muni_stats[:, 0] > 0, muni_stats[:, 1] / muni_stats[:, 0], np.nan)
    area_px_ha = cos_medio * AREA_PX_EQUADOR / 10_000.0
    for it in range(pc.N_ANOS):
        m = acc_mc[it].reshape(n_muni + 1, N_CLASSES)
        idx_m, idx_c = np.nonzero(m)
        for mi, ci in zip(idx_m, idx_c):
            if mi == 0:
                continue  # fora da malha do IBGE
            linhas.append({"ano": pc.ANO_MIN + it, "cd_mun": cod[mi], "nm_mun": nom[mi],
                           "class_id": int(ci), "n_pixels": int(m[mi, ci]),
                           "area_ha": int(m[mi, ci]) * area_px_ha[mi]})
    df_m = pd.DataFrame(linhas)
    f_m = DIR_SAIDA / f"censo_munis_{args.tag}.csv"
    df_m.to_csv(f_m, index=False)
    print(f"\n  -> {f_m}  ({len(df_m):,} linhas)")

    # (b) centro de massa pixel-ponderado por classe × ano
    linhas = []
    for it in range(pc.N_ANOS):
        for ci in np.nonzero(acc_n[it])[0]:
            n = acc_n[it, ci]
            linhas.append({"ano": pc.ANO_MIN + it, "class_id": int(ci), "n_pixels": int(n),
                           "area_ha": float(acc_cos[it, ci]) * AREA_PX_EQUADOR / 10_000.0,
                           "lat": acc_lat[it, ci] / n, "lon": acc_lon[it, ci] / n})
    df_c = pd.DataFrame(linhas)
    f_c = DIR_SAIDA / f"centro_massa_classe_{args.tag}.csv"
    df_c.to_csv(f_c, index=False)
    print(f"  -> {f_c}  ({len(df_c):,} linhas)")
    ckpt.unlink(missing_ok=True)  # só agora: os dois CSVs estão em disco

    # Shards inteiramente fora da malha do IBGE devolvem vazio — é legítimo (o bbox
    # de export é retangular e Goiás não é). Só cai aqui com --limite num canto.
    if df_m.empty:
        print("  [aviso] nenhum pixel dentro da malha do IBGE nos shards lidos "
              "(shard de canto?). Sem sanidade de área.")
    else:
        tot = df_m[df_m.ano == pc.ANO_MAX].area_ha.sum() / 1e6
        print(f"\n  sanidade: área total mapeada em {pc.ANO_MAX} = {tot:.3f} Mha "
              f"(Goiás ~34,0 Mha)")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
