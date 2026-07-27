"""transicoes_cubo.py — Pipeline #12B: a matriz de transição recontada no censo
================================================================================

Refaz a matriz de transição do [#12](../Textos/pipelines/12_transicoes.md) a partir
do cubo censitário local (`data/raw/cubo_go/`, o mesmo do #28), com o **Mosaico de
Usos (classe 21) como grupo próprio** — 7 grupos, não 6.

## O defeito que isto fecha

O #12 traduz o ID do MapBiomas para 6 grupos com `remap(..., defaultValue=0)` e
mascara o que sobra (`updateMask`). A classe 21 não está na lista, então o pixel
que sai de pastagem para Mosaico **não vira "pasto→outros": ele some da matriz
inteira**, do numerador e do denominador. Onde essa rota carrega o fluxo — e a
partir de 2021 ela carrega (#28D: a razão `P→mosaico / P→agric` vai de 0,6 em 2015
a 32,5 em 2024, enquanto o IBGE registra a soja +38%) — a matriz mostra a conversão
*parando*. É o artefato da D25, na fonte primária de transições da dissertação.

A `validar_batimental()` do #12 não pega isso: ela descarta a classe 21 dos **dois
lados** antes de comparar contra o #4, então bateria com δ≈0 mesmo se 100% da
conversão recente tivesse migrado para o rótulo excluído. É cega por construção.

## Por que local, e não uma re-exportação do GEE

O doc do #12 registrou o custo do conserto como "re-exportar os caches do GEE".
Deixou de ser verdade em 21/jul/2026, quando o #28 baixou o cubo completo (40
bandas, grade nativa, **IDs brutos** do MapBiomas) para `data/raw/cubo_go/`. O
descarte da classe 21 nunca esteve na fonte — ele mora na nossa tradução ID→grupo,
que roda aqui. Logo a recontagem é local, offline, sem cota nem autenticação.

## O que muda de MEDIDA (declarado, não escondido)

Duas coisas mudam ao mesmo tempo, e é preciso poder separá-las:

    Δ_mosaico   o grupo 7 passa a existir       <- o conserto
    Δ_medida    o instrumento é outro           <- efeito colateral

O #12 conta com `reduceRegions(scale=30, crs="EPSG:5880")`: reprojeta para uma
grade equivalente-área e conta lá. Aqui conta-se o **pixel nativo** (EPSG:4326),
convertido por `cos(lat)` médio observado do município — a mesma régua do #28.
Nenhum dos dois está errado; são instrumentos diferentes. Por isso **toda** célula
muda um pouco, inclusive onde o Mosaico é irrelevante.

`validar_transicoes_cubo.py` isola Δ_medida (colapsando esta saída de volta a 6
grupos e comparando par a par com o cache do GEE), para que Δ_mosaico não chegue
misturado a jusante.

## Sentinelas: três situações, três códigos

Lição do #28A, onde a classe 21 virou censura por `.fillna()`. Aqui um pixel pode
estar fora da matriz por motivos distintos, e cada um tem código próprio e é
**contado e reportado**, nunca absorvido em silêncio:

    0 (IDX_SEM_DADO)      nodata do MapBiomas — ausência de dado, não classe
    8 (IDX_NAO_MAPEADO)   classe existe no raster e falta no GRUPO_MAP — isto é bug
                          de configuração, e o run avisa alto

## Pares calculados

Os mesmos 48 do cache do #12 (39 consecutivos + 9 longos), para que a comparação
seja par a par e o drop-in a jusante seja direto.

SAÍDA
    data/cache/transicoes_cubo/transicao_YYYY_YYYY.csv   (48; schema do #12 + n_pixels)
    data/processed/transicoes_cubo_goias.csv             (consolidado)

O cache do GEE em `data/cache/transicoes/` **não é tocado** — ele é o único
instrumento de comparação que existe, e sobrescrevê-lo destruiria a prova.

COMO RODAR
    python scripts/transicoes_cubo.py --shards data/raw/cubo_go
    python scripts/transicoes_cubo.py --shards data/raw/cubo_go --limite 1   (fumaça)

Pré-requisitos:
    pip install rasterio geopandas geobr pandas
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
import processa_cubo_idade as pc  # noqa: E402 — reuso da máquina do #28

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "transicoes_cubo"
CSV_SAIDA = ROOT / "data" / "processed" / "transicoes_cubo_goias.csv"

# Ordem dos grupos: 1..6 IDÊNTICOS aos do #12 (`transicoes_mapbiomas.CLASSES`), com o
# Mosaico entrando como 7. Deliberado: nenhum código a jusante que já lê 1..6 muda de
# significado — só ganha uma chave nova. (Mesmo princípio do índice de pipelines:
# número é identidade, não se renumera.) Os IDs de classe vêm de `pc.GRUPO_MAP`, para
# não haver duas listas de classes que possam divergir com o tempo.
ORDEM_GRUPOS: list[tuple[int, str, str]] = [
    (1, "vegetacao_natural", "Vegetação Natural"),
    (2, "pastagem",          "Pastagem"),
    (3, "agricultura",       "Agricultura"),
    (4, "agua",              "Água"),
    (5, "area_urbana",       "Área Urbana"),
    (6, "outros",            "Outros"),
    (7, "mosaico",           "Mosaico de Usos"),
]
NOME_CLASSE = {i: nome_exib for i, _, nome_exib in ORDEM_GRUPOS}
CHAVE_GRUPO = {i: chave for i, chave, _ in ORDEM_GRUPOS}

N_G = 9               # base da chave: grupos 1..7 + as duas sentinelas (0 e 8)
IDX_SEM_DADO = 0      # nodata do MapBiomas
IDX_NAO_MAPEADO = 8   # classe no raster e fora do GRUPO_MAP -> bug de configuração

# Os 9 pares longos do #12 (`PERIODOS_DEFAULT`), na mesma ordem.
PARES_LONGOS = [
    (1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024),
    (1985, 2000), (2000, 2010), (2010, 2024),
    (1985, 2010), (1985, 2024),
]


def pares_padrao(ano_max: int) -> list[tuple[int, int]]:
    """39 consecutivos + os 9 longos que couberem na série disponível."""
    longos = [(a, b) for a, b in PARES_LONGOS if b <= ano_max]
    consec = [(a, a + 1) for a in range(pc.ANO_MIN, ano_max)]
    return longos + consec


def construir_lut() -> np.ndarray:
    """ID MapBiomas (0..255) -> índice de grupo 1..7, com sentinelas explícitas.

    O preenchimento padrão é IDX_NAO_MAPEADO, não 0: uma classe ausente do
    GRUPO_MAP tem que aparecer como problema, nunca ser absorvida por "sem dado".
    """
    faltando = {n for _, n, _ in ORDEM_GRUPOS} - set(pc.GRUPO_MAP)
    if faltando:
        raise RuntimeError(f"grupos ausentes de processa_cubo_idade.GRUPO_MAP: {faltando}")
    sobrando = set(pc.GRUPO_MAP) - {n for _, n, _ in ORDEM_GRUPOS}
    if sobrando:
        raise RuntimeError(
            f"GRUPO_MAP tem grupos que ORDEM_GRUPOS não conhece: {sobrando} — "
            "some-os da matriz em silêncio; acrescente-os aqui com índice próprio")

    lut = np.full(256, IDX_NAO_MAPEADO, dtype=np.uint8)
    lut[0] = IDX_SEM_DADO
    for idx, chave, _ in ORDEM_GRUPOS:
        for cid in pc.GRUPO_MAP[chave]:
            lut[cid] = idx
    return lut


def processar_shard(caminho: Path, gdf_muni, pares_idx: list[tuple[int, int]],
                    acc: np.ndarray, muni_stats: np.ndarray, tam_janela: int) -> int:
    """Acumula, para cada par de anos, a contagem (município × grupo_orig × grupo_dest).

    Retorna o nº de pixels-par contados (soma sobre pares), só para telemetria.
    """
    lut = construir_lut()
    n_slots = N_G * N_G

    with rasterio.open(caminho) as src:
        if src.count != pc.N_ANOS:
            raise RuntimeError(f"{caminho.name}: {src.count} bandas, esperado {pc.N_ANOS}")

        # Município por rasterização LOCAL dos polígonos do IBGE, em precisão total.
        # O export é do bbox retangular: é aqui que "fora de Goiás" vira rótulo
        # explícito (muni_idx 0) em vez de acidente de amostragem. Ver #28.
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(src.height, src.width),
            transform=src.transform,
            fill=0,
            dtype=np.uint16,
        )
        if not muni.any():
            return 0  # shard inteiramente fora de Goiás

        # cos(lat) por município, acumulado na varredura (não estimado por centroide):
        # é o que converte contagem de pixel em hectare sem viés norte-sul. Ver #28.
        lats = src.transform.f - (np.arange(src.height) + 0.5) * pc.PX
        cos_lat = np.cos(np.radians(lats))
        for i in range(src.height):
            if not muni[i].any():
                continue
            b = np.bincount(muni[i], minlength=muni_stats.shape[0])
            muni_stats[:, 0] += b
            muni_stats[:, 1] += b * cos_lat[i]

        total = 0
        for top in range(0, src.height, tam_janela):
            for left in range(0, src.width, tam_janela):
                h = min(tam_janela, src.height - top)
                w = min(tam_janela, src.width - left)
                mj = muni[top:top + h, left:left + w]
                if not mj.any():
                    continue

                arr = src.read(window=Window(left, top, w, h))  # (N_ANOS, h, w) uint8
                plano = arr.reshape(pc.N_ANOS, -1)
                pos = np.flatnonzero(mj.reshape(-1))

                # Comprime UMA vez para os pixels dentro de GO e já traduz para grupo.
                # Sem isso, cada um dos 48 pares refaria dois gathers sobre a janela
                # inteira — o custo dominante. Aqui são N_ANOS gathers no total, e
                # cada par vira aritmética sobre vetores já compactos.
                g = np.empty((pc.N_ANOS, pos.size), dtype=np.uint8)
                for j in range(pc.N_ANOS):
                    g[j] = lut[plano[j][pos]]

                base = mj.reshape(-1)[pos].astype(np.int64) * n_slots
                for k, (i0, i1) in enumerate(pares_idx):
                    chave = base + g[i0].astype(np.int64) * N_G + g[i1]
                    acc[k] += np.bincount(chave, minlength=acc.shape[1])
                    total += pos.size
    return total


def decodificar(acc: np.ndarray, pares: list[tuple[int, int]],
                gdf_muni, muni_stats: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (matriz válida, diagnóstico das sentinelas por par)."""
    idx_para_cd = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.cd_mun.astype(int)))
    idx_para_nm = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.nm_mun))

    with np.errstate(invalid="ignore", divide="ignore"):
        cos_medio = np.where(muni_stats[:, 0] > 0, muni_stats[:, 1] / muni_stats[:, 0], np.nan)
    area_px_ha = cos_medio * pc.AREA_PX_EQUADOR / 10_000.0

    partes, diag = [], []
    for k, (a0, a1) in enumerate(pares):
        nz = np.flatnonzero(acc[k])
        if nz.size == 0:
            continue
        n = acc[k][nz].astype("int64")
        g_dest = nz % N_G
        resto = nz // N_G
        g_orig = resto % N_G
        muni_idx = resto // N_G

        validos = ((g_orig >= 1) & (g_orig <= 7) & (g_dest >= 1) & (g_dest <= 7))
        # As sentinelas não entram na matriz publicada, mas são CONTADAS e
        # reportadas — é o que impede que "sumiu" volte a ser indistinguível de
        # "não existe", que foi exatamente o defeito do #12.
        sem_dado = int(n[(~validos) & ((g_orig == IDX_SEM_DADO) | (g_dest == IDX_SEM_DADO))].sum())
        nao_map = int(n[(g_orig == IDX_NAO_MAPEADO) | (g_dest == IDX_NAO_MAPEADO)].sum())
        diag.append({"ano_origem": a0, "ano_destino": a1,
                     "px_validos": int(n[validos].sum()),
                     "px_sem_dado": sem_dado, "px_nao_mapeado": nao_map})

        if not validos.any():
            continue
        mi = muni_idx[validos]
        partes.append(pd.DataFrame({
            "cd_mun": [idx_para_cd.get(int(i), 0) for i in mi],
            "nm_mun": [idx_para_nm.get(int(i), "") for i in mi],
            "classe_orig": g_orig[validos].astype("int16"),
            "classe_dest": g_dest[validos].astype("int16"),
            "n_pixels": n[validos],
            "area_ha": n[validos] * area_px_ha[mi],
            "ano_origem": a0,
            "ano_destino": a1,
        }))

    df = pd.concat(partes, ignore_index=True)
    df["classe_orig_nome"] = df["classe_orig"].map(NOME_CLASSE)
    df["classe_dest_nome"] = df["classe_dest"].map(NOME_CLASSE)
    return df, pd.DataFrame(diag)


def main() -> None:
    p = argparse.ArgumentParser(description="Pipeline #12B — matriz de transição no censo (7 grupos)")
    p.add_argument("--shards", type=Path, default=ROOT / "data" / "raw" / "cubo_go")
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--limite", type=int, default=0, help="Processa só os N primeiros shards")
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
        print("  (--limite ativo: verificação de partição pulada; números NÃO são o censo)")
    else:
        pc.verificar_particao(tifs)

    pares = pares_padrao(pc.ANO_MAX)
    pares_idx = [(a - pc.ANO_MIN, b - pc.ANO_MIN) for a, b in pares]
    print(f"{len(tifs)} shard(s) | janela {args.janela}² | {len(pares)} pares "
          f"({len(PARES_LONGOS)} longos + {len(pares) - len(PARES_LONGOS)} consecutivos)")

    gdf_muni = pc.carregar_municipios()
    print(f"  {len(gdf_muni)} municípios | 7 grupos (Mosaico = 7)")

    acc = np.zeros((len(pares), (len(gdf_muni) + 1) * N_G * N_G), dtype=np.int64)
    muni_stats = np.zeros((len(gdf_muni) + 1, 2), dtype=np.float64)
    print(f"  acumulador: {acc.nbytes / 1e6:.1f} MB")

    t_ini = time.time()
    for i, tif in enumerate(tifs, 1):
        t0 = time.time()
        n = processar_shard(tif, gdf_muni, pares_idx, acc, muni_stats, args.janela)
        print(f"[{i:02d}/{len(tifs)}] {tif.name} — {n / 1e6:,.0f} Mpx-par ({time.time() - t0:.0f}s)")

    if not acc.any():
        print("Nenhum pixel contado (shards fora de GO?).")
        return

    df, diag = decodificar(acc, pares, gdf_muni, muni_stats)

    # Uma corrida com --limite NÃO é o censo, e não pode ocupar o caminho canônico:
    # a jusante ninguém tem como distinguir um CSV parcial de um completo, e o erro
    # seria silencioso (a matriz simplesmente teria menos Goiás). Sufixo no caminho.
    if args.limite:
        cache_dir = CACHE_DIR.parent / f"{CACHE_DIR.name}_PARCIAL"
        csv_saida = CSV_SAIDA.with_name(f"{CSV_SAIDA.stem}_PARCIAL.csv")
    else:
        cache_dir, csv_saida = CACHE_DIR, CSV_SAIDA
    cache_dir.mkdir(parents=True, exist_ok=True)
    cols = ["cd_mun", "nm_mun", "classe_orig", "classe_dest", "n_pixels", "area_ha",
            "classe_orig_nome", "classe_dest_nome", "ano_origem", "ano_destino"]
    df = df[cols].sort_values(["ano_origem", "ano_destino", "cd_mun",
                               "classe_orig", "classe_dest"])
    for (a0, a1), sub in df.groupby(["ano_origem", "ano_destino"]):
        sub.to_csv(cache_dir / f"transicao_{a0}_{a1}.csv", index=False,
                   float_format="%.4f")
    csv_saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_saida, index=False, float_format="%.4f")

    print(f"\n{'=' * 64}")
    print(f"SAÍDA: {cache_dir.relative_to(ROOT)}/ ({df.groupby(['ano_origem','ano_destino']).ngroups} CSVs)")
    print(f"       {csv_saida.relative_to(ROOT)} ({len(df):,} linhas)")
    if args.limite:
        print("       ⚠️  PARCIAL (--limite): não é o censo, não use a jusante")
    print(f"       {time.time() - t_ini:.0f}s no total")

    # Sentinelas: nodata é esperado (mais nos anos iniciais); não-mapeado é BUG.
    tot_val = int(diag["px_validos"].sum())
    tot_sd = int(diag["px_sem_dado"].sum())
    tot_nm = int(diag["px_nao_mapeado"].sum())
    print(f"\n  pixels-par válidos: {tot_val:,}")
    print(f"  sem dado (nodata):  {tot_sd:,} ({tot_sd / (tot_val + tot_sd + tot_nm) * 100:.4f}%)")
    if tot_nm:
        print(f"  *** {tot_nm:,} pixels-par com classe FORA do GRUPO_MAP — bug de "
              f"configuração: identifique a classe e acrescente-a antes de usar isto")
    else:
        print("  não-mapeado: 0 — toda classe do raster tem grupo")

    # Assinatura da mudança de rótulo (#28D): a razão P->mosaico / P->agric deve sair
    # de ~0,6 em 2015 e explodir na cauda. Se NÃO explodir, alguma coisa aqui está
    # errada — este é o teste de fumaça que o #12 nunca pôde fazer.
    consec = df[df["ano_destino"] - df["ano_origem"] == 1]
    pas = consec[consec["classe_orig"] == 2]
    piv = (pas[pas["classe_dest"].isin([3, 7])]
           .groupby(["ano_destino", "classe_dest"])["area_ha"].sum().unstack(fill_value=0.0))
    print("\n  pastagem -> agricultura vs Mosaico (razão M/A; ver #28D):")
    for ano in (2010, 2015, 2018, 2020, 2021, 2022, 2023, 2024):
        if ano in piv.index and 3 in piv.columns and 7 in piv.columns:
            a, m = piv.loc[ano, 3], piv.loc[ano, 7]
            r = m / a if a > 0 else float("nan")
            print(f"    {ano}: agric {a:>10,.0f} ha | mosaico {m:>10,.0f} ha | razão {r:6.2f}")

    print("\n  Próximo passo: python scripts/validar_transicoes_cubo.py")


if __name__ == "__main__":
    main()
