"""processa_cubo_idade.py — Pipeline #28 (processamento censitário)

Lê os shards exportados por `export_cubo_mapbiomas_go.py` e calcula, para CADA
pixel de Goiás que sofreu transição pastagem → agricultura, a idade da pastagem
no momento da conversão e a classe imediatamente anterior à fase de pastagem.

Substitui a amostragem de 2.000 px/ano do `coleta_idade_pastagem.py`.

## Por que a saída é uma tabela de contingência, e não uma linha por pixel

O censo tem ordens de magnitude mais eventos de conversão que a amostra (43.951).
Mas as quatro variáveis do #28 são todas discretas e de baixa cardinalidade:

    ano_conversao   1986..2024        (39)
    idade           0..39 anos        (41)
    classe_antes    ~30 classes + censurado
    cd_mun          246 municípios (+ 1 rótulo "fora de GO")

Logo o censo COMPLETO cabe, **sem perda nenhuma**, em `(ano, muni, idade,
classe) → n_pixels`. Toda análise do #28 — histogramas, medianas, percentis,
GMM, mapas municipais, Kaplan-Meier — é recuperável exatamente desses pesos.
Guardar linha-por-pixel só desperdiçaria disco.

Quem precisar de linhas individuais (ex.: `sklearn.GaussianMixture`, que não
aceita sample_weight) expande o subconjunto de interesse com
`df.loc[df.index.repeat(df.n_pixels)]` — barato para um recorte, inviável para
o todo.

## O município vem daqui, não do GEE

O export é do bbox retangular, sem máscara. É aqui que os polígonos do IBGE em
precisão total (103.454 vértices, sem simplificação) são rasterizados sobre a
grade nativa do MapBiomas. Pixels fora de GO recebem `cd_mun = 0` e ficam
gravados como rótulo explícito — não como acidente de amostragem.

Essa inversão é o que desarma o bug do envelope do #28A: lá, o GEE amostrava um
retângulo e 43,7% dos pixels caíam fora do estado sem que ninguém percebesse.

## Área do pixel varia com a latitude — declarado, não corrigido por padrão

O raster está em EPSG:4326, onde a área de solo de um pixel é proporcional a
cos(latitude). Goiás cobre 7° de latitude, então:

    cos(12,395°) = 0,97669   (norte)
    cos(19,498°) = 0,94268   (sul)

Um pixel do norte cobre **3,5% mais chão** que um do sul. Contar pixels como
equivalentes subpondera o norte — e o eixo norte-sul é exatamente o da tese da
"marcha ao norte", então isso não pode ficar implícito.

A saída traz **as duas** colunas:

    n_pixels   contagem bruta  → comparável com a amostra do #28A (que também
                                 contava pixels), use para validar o censo
    area_ha    área de solo    → use para qualquer afirmação sobre QUANTO de
                                 Goiás fez X

`area_ha` sai de cos(lat) médio observado por município (acumulado na
rasterização, não estimado por centroide), então o erro residual vem só da
correlação entre latitude e conversão DENTRO de um município — desprezível.

O padrão das análises segue `n_pixels` porque a comparação com a amostra
corrigida exige mesma métrica. Trocar para `area_ha` muda resultados em <3,5%.

## Centroide (lat_media / lon_media)

A tabela de contingência perde a coordenada de cada pixel, mas o #40 precisa
dela: o argumento da D14 é que as covariáveis de manejo não sobrevivem ao
controle do gradiente 2D (lat+lon), e esse controle usa a posição MÉDIA dos
pixels convertidos da unidade — não o centroide geométrico do município ou da
AMC. São coisas diferentes: a conversão se concentra em partes do município.

Por isso `acc_lat`/`acc_lon` acumulam a SOMA de lat/lon na mesma chave de `acc`.
No decode, `soma / n` devolve a média exata dos pixels daquela célula, e
qualquer agregação posterior (por AMC, por janela, só não-censurados) é a média
ponderada por `n_pixels` — exata, não aproximada.

## Memória

Processa em janelas (padrão 2048²): ~500 MB de working set independentemente do
tamanho do shard, mais ~390 MB de acumuladores (contagem + soma lat/lon).
Roda em laptop; máquina de servidor só paraleliza os shards.

Como rodar:
    python scripts/processa_cubo_idade.py --shards data/raw/cubo_go
    python scripts/processa_cubo_idade.py --shards data/raw/cubo_go --limite 1   (validação)

Pré-requisitos:
    pip install rasterio geopandas geobr pyarrow
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import geobr
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parent.parent
PARQUET_SAIDA = ROOT / "data" / "processed" / "pastagem_idade_censo.parquet"

ANO_MIN = 1985
ANO_MAX = 2024
N_ANOS = ANO_MAX - ANO_MIN + 1  # 40 bandas

ID_PASTAGEM = 15
IDS_AGRICULTURA = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

GRUPO_MAP = {
    "vegetacao_natural": [3, 4, 12],
    "pastagem":          [15],
    "agricultura":       [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],
    # Classe 21 (Mosaico de Usos) FALTAVA no GRUPO_MAP do #28A. Como o código
    # original fazia `.map(ID_PARA_GRUPO).fillna("censurado_esquerda")`, todo
    # pixel cuja classe pré-pastagem era 21 virava "censurado" — isto é, "idade
    # desconhecida" — quando a idade era perfeitamente conhecida. Na amostra
    # corrigida isso são 4.898 px: censura publicada 74,9% vs real 63,7%, e
    # não-censurados 11.035 vs 15.933 (+44%). Como TODAS as análises-manchete do
    # #28 (GMM, bimodalidade, medianas por Ato, regra de decisão) rodam sobre o
    # subconjunto não-censurado, elas usaram 2/3 dos dados que tinham direito.
    # E os excluídos não eram aleatórios: eram justamente os de origem mista
    # agricultura/pastagem, a categoria mais próxima do mecanismo "rotação".
    "mosaico":           [21],
    "agua":              [31, 33],
    "area_urbana":       [24],
    "outros":            [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],
}
ID_PARA_GRUPO = {cid: nome for nome, ids in GRUPO_MAP.items() for cid in ids}

N_IDADE = 41          # idade 0..40
N_CLASSE = 40         # índice compacto de classe_antes (folga sobre as 32 usadas)

# Censura e "classe não reconhecida" são coisas DIFERENTES e precisam de códigos
# diferentes. No #28A ambas eram 0, então uma classe fora do GRUPO_MAP virava
# censura silenciosamente (foi assim que a classe 21 sumiu). Aqui:
#   IDX_CENSURADO    -> a fase de pastagem alcança 1985; idade é limite inferior.
#                       Determinado por índice (inicio <= 0), NUNCA por lookup.
#   IDX_NAO_MAPEADO  -> classe existe no raster mas não está no GRUPO_MAP.
#                       É um bug de configuração; o run avisa alto e não a
#                       confunde com censura.
# São TRÊS situações distintas, e cada uma precisa de código próprio:
IDX_CENSURADO = 0             # fase de pastagem alcança 1985; idade é limite inferior
IDX_SEM_DADO = N_CLASSE - 2   # classe anterior = 0 (nodata do MapBiomas).
                              # A IDADE é conhecida; só a origem é indeterminada.
                              # Não é censura e não é bug — é ausência de dado.
IDX_NAO_MAPEADO = N_CLASSE - 1  # classe existe no raster e falta no GRUPO_MAP.
                              # Isso SIM é bug de configuração; o run avisa alto.

# Grade nativa do MapBiomas 10.1 — idêntica à do export
PX = 0.00026949458523585647
ORIGEM_X = -74.02073025380652
ORIGEM_Y = 5.405791885246045

# Área de um pixel a 30 m no equador (m²); multiplicar por cos(lat)
AREA_PX_EQUADOR = PX * PX * 111320.0 * 110574.0


def verificar_particao(tifs: list[Path]) -> int:
    """Confere que os shards particionam a grade: sem sobreposição, sem reamostragem.

    O GEE fatia o export via `fileDimensions`. Se dois tiles se sobrepuserem, os
    pixels da costura entram DUAS vezes no censo e o resultado não denuncia nada
    — as contagens só ficam silenciosamente altas. Idem se algum shard vier fora
    da grade nativa: aí houve reamostragem e a contagem de anos consecutivos
    perde sentido. Ambos são erros que só aparecem se forem procurados.
    """
    caixas = []
    for t in tifs:
        with rasterio.open(t) as s:
            tr = s.transform
            fx, fy = (tr.c - ORIGEM_X) / PX, (ORIGEM_Y - tr.f) / PX
            col0, row0 = round(fx), round(fy)
            if abs(fx - col0) > 1e-6 or abs(fy - row0) > 1e-6:
                raise RuntimeError(
                    f"{t.name}: origem fora da grade nativa (desvio "
                    f"{abs(fx - col0):.2e}, {abs(fy - row0):.2e} px) — houve reamostragem")
            if abs(tr.a - PX) > 1e-15 or abs(tr.e + PX) > 1e-15:
                raise RuntimeError(f"{t.name}: escala difere da nativa")
            caixas.append((t.name, col0, row0, s.width, s.height))

    for i in range(len(caixas)):
        for j in range(i + 1, len(caixas)):
            n1, c1, r1, w1, h1 = caixas[i]
            n2, c2, r2, w2, h2 = caixas[j]
            ox = max(0, min(c1 + w1, c2 + w2) - max(c1, c2))
            oy = max(0, min(r1 + h1, r2 + h2) - max(r1, r2))
            if ox and oy:
                raise RuntimeError(f"SOBREPOSIÇÃO entre {n1} e {n2}: {ox}x{oy} px "
                                   f"— pixels seriam contados em duplicidade")

    total = sum(w * h for _, _, _, w, h in caixas)
    cols = {(c, w) for _, c, _, w, _ in caixas}
    rows = {(r, h) for _, _, r, h, _ in caixas}
    extensao = (max(c + w for _, c, _, w, _ in caixas) - min(c for _, c, _, _, _ in caixas)) * \
               (max(r + h for _, _, r, _, h in caixas) - min(r for _, _, r, _, _ in caixas))
    print(f"  partição: {len(caixas)} shards, {total / 1e6:,.0f} Mpx, sem sobreposição")
    if total != extensao:
        print(f"  AVISO: {(extensao - total) / 1e6:,.1f} Mpx de buraco na cobertura "
              f"(retângulo envolvente = {extensao / 1e6:,.0f} Mpx)")
    return total


def construir_lookup_classe() -> tuple[np.ndarray, dict[int, int]]:
    """Mapeia ID MapBiomas (0..255) → índice compacto 1..N.

    O preenchimento padrão é IDX_NAO_MAPEADO, não 0: uma classe ausente do
    GRUPO_MAP tem que aparecer como problema, nunca ser absorvida pela censura.
    """
    ids = sorted(ID_PARA_GRUPO.keys())
    id_para_idx = {cid: i + 1 for i, cid in enumerate(ids)}
    # Classes reais ocupam idx 1..len(ids); os 3 sentinelas vivem em 0, N_CLASSE-2
    # e N_CLASSE-1. Para a maior classe (idx len(ids)) não colidir com IDX_SEM_DADO
    # (= N_CLASSE-2), precisa len(ids) <= N_CLASSE-3, i.e. len(ids)+3 > N_CLASSE dispara.
    # O limite era +2 (off-by-one: deixaria len(ids)=N_CLASSE-2 colidir com a sentinela).
    if len(ids) + 3 > N_CLASSE:
        raise RuntimeError(f"N_CLASSE={N_CLASSE} pequeno para {len(ids)} classes + 3 sentinelas")
    lut = np.full(256, IDX_NAO_MAPEADO, dtype=np.uint8)
    lut[0] = IDX_SEM_DADO  # 0 é o nodata do MapBiomas, não uma classe ausente
    for cid, idx in id_para_idx.items():
        lut[cid] = idx
    return lut, {v: k for k, v in id_para_idx.items()}


def carregar_municipios():
    """246 municípios de GO em EPSG:4326, SEM simplificação."""
    gdf = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    gdf = gdf.rename(columns={"code_muni": "cd_mun", "name_muni": "nm_mun"})
    gdf["cd_mun"] = gdf["cd_mun"].astype("int64")
    gdf = gdf.reset_index(drop=True)
    gdf["muni_idx"] = np.arange(1, len(gdf) + 1, dtype=np.uint16)  # 0 = fora de GO
    return gdf[["cd_mun", "nm_mun", "muni_idx", "geometry"]]


def processar_shard(caminho: Path, gdf_muni, acc: np.ndarray,
                    acc_lat: np.ndarray, acc_lon: np.ndarray,
                    muni_stats: np.ndarray, tam_janela: int) -> tuple[int, int]:
    """Acumula contagens de um shard em `acc` (e soma de lat/lon em `acc_lat/lon`).

    Retorna (nº de eventos de conversão, nº de pixels distintos que converteram).
    Os dois diferem porque um pixel pode converter mais de uma vez
    (pasto→lavoura→pasto→lavoura); ver nota sobre independência no `main()`.

    `acc_lat`/`acc_lon` usam a MESMA chave de `acc`, então `acc_lat/acc` é a
    latitude média exata dos pixels daquela célula — ver "Centroide" no
    docstring do módulo.
    """
    lut, _ = construir_lookup_classe()
    is_agri_lut = np.zeros(256, dtype=bool)
    is_agri_lut[IDS_AGRICULTURA] = True

    total = 0
    distintos = 0
    with rasterio.open(caminho) as src:
        if src.count != N_ANOS:
            raise RuntimeError(f"{caminho.name}: {src.count} bandas, esperado {N_ANOS}")

        # Rasteriza os municípios na grade EXATA deste shard (precisão total)
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(src.height, src.width),
            transform=src.transform,
            fill=0,
            dtype=np.uint16,
        )
        if not muni.any():
            return 0, 0  # shard inteiramente fora de Goiás — nada a fazer

        # cos(lat) por município: converte contagem em hectares depois, sem
        # aproximar por centroide (ver "Área do pixel" no docstring do módulo).
        lats = src.transform.f - (np.arange(src.height) + 0.5) * PX
        lons = src.transform.c + (np.arange(src.width) + 0.5) * PX
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

                arr = src.read(window=Window(left, top, w, h))  # (40, h, w) uint8
                arr = np.ascontiguousarray(arr)
                is_past = arr == ID_PASTAGEM

                # Idade acumulada: contador que zera quando o pixel não é pasto
                age = np.zeros_like(arr, dtype=np.int8)
                age[0] = is_past[0]
                for j in range(1, N_ANOS):
                    age[j] = (age[j - 1] + 1) * is_past[j]

                plano = arr.reshape(-1)
                mj_plano = mj.reshape(-1)
                conv_ever = np.zeros((h, w), dtype=bool)

                for it in range(1, N_ANOS):  # it = índice do ano de conversão
                    conv = is_past[it - 1] & is_agri_lut[arr[it]]
                    conv &= mj > 0  # só pixels com município (dentro de GO)
                    if not conv.any():
                        continue
                    conv_ever |= conv

                    pos = np.flatnonzero(conv.reshape(-1))
                    idade = age[it - 1].reshape(-1)[pos].astype(np.int32)

                    # Invariante: conv exige pasto em it-1, logo idade >= 1.
                    # Se cair para 0, o contador de idade dessincronizou da
                    # máscara e todo o censo estaria deslocado em um ano.
                    if idade.min() < 1:
                        raise RuntimeError(
                            f"{caminho.name} ano {ANO_MIN + it}: idade {idade.min()} < 1 "
                            "— contador dessincronizado da máscara de conversão")

                    # Índice do PRIMEIRO ano da fase pastagem; <=0 => censurado
                    inicio = it - idade
                    cens = inicio <= 0

                    classe_idx = np.full(pos.shape, IDX_CENSURADO, dtype=np.int64)
                    if (~cens).any():
                        flat = (inicio[~cens] - 1).astype(np.int64) * (h * w) + pos[~cens]
                        classe_idx[~cens] = lut[plano[flat]]

                    chave = ((mj_plano[pos].astype(np.int64) * N_IDADE
                              + np.clip(idade, 0, N_IDADE - 1)) * N_CLASSE + classe_idx)
                    acc[it] += np.bincount(chave, minlength=acc.shape[1])

                    # Soma de lat/lon dos pixels convertidos, na mesma chave.
                    # `pos` é o índice achatado dentro da janela (h×w), então a
                    # linha/coluna GLOBAL do shard é (top + pos//w, left + pos%w).
                    rr, cc = np.divmod(pos, w)
                    acc_lat[it] += np.bincount(chave, weights=lats[top + rr],
                                               minlength=acc.shape[1])
                    acc_lon[it] += np.bincount(chave, weights=lons[left + cc],
                                               minlength=acc.shape[1])
                    total += pos.size

                distintos += int(conv_ever.sum())
    return total, distintos


def decodificar(acc: np.ndarray, acc_lat: np.ndarray, acc_lon: np.ndarray,
                gdf_muni, muni_stats: np.ndarray) -> pd.DataFrame:
    _, idx_para_id = construir_lookup_classe()
    idx_para_cd = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.cd_mun.astype(int)))
    idx_para_nm = dict(zip(gdf_muni.muni_idx.astype(int), gdf_muni.nm_mun))

    linhas = []
    for it in range(1, N_ANOS):
        nz = np.flatnonzero(acc[it])
        if nz.size == 0:
            continue
        classe_idx = nz % N_CLASSE
        resto = nz // N_CLASSE
        idade = resto % N_IDADE
        muni_idx = resto // N_IDADE
        n = acc[it][nz].astype("int64")
        linhas.append(pd.DataFrame({
            "ano_conversao": ANO_MIN + it,
            "muni_idx": muni_idx,
            "idade_pastagem_anos": idade.astype("int16"),
            "classe_idx": classe_idx,
            "n_pixels": n,
            # Centroide EXATO dos pixels da célula (soma/contagem), não do
            # município nem do centroide da AMC. É o que o #40 usa para o
            # controle do gradiente 2D — ver "Centroide" no docstring.
            "lat_media": acc_lat[it][nz] / n,
            "lon_media": acc_lon[it][nz] / n,
        }))

    df = pd.concat(linhas, ignore_index=True)
    df["cd_mun"] = df["muni_idx"].map(idx_para_cd).fillna(0).astype("int64")
    df["nm_mun"] = df["muni_idx"].map(idx_para_nm).fillna("")
    # Cada sentinela é resolvida explicitamente. Nada de `.fillna(...)`: foi
    # exatamente esse padrão que fez a classe 21 virar censura no #28A.
    df["classe_antes_id"] = df["classe_idx"].map(idx_para_id).astype("float").fillna(-1).astype("int32")
    df["origem_anterior"] = df["classe_antes_id"].map(ID_PARA_GRUPO)
    df.loc[df["classe_idx"] == IDX_CENSURADO, ["classe_antes_id", "origem_anterior"]] = \
        [0, "censurado_esquerda"]
    df.loc[df["classe_idx"] == IDX_SEM_DADO, ["classe_antes_id", "origem_anterior"]] = \
        [0, "sem_dado_anterior"]
    df.loc[df["classe_idx"] == IDX_NAO_MAPEADO, ["classe_antes_id", "origem_anterior"]] = \
        [-1, "nao_mapeado"]
    if df["origem_anterior"].isna().any():
        ruins = sorted(df.loc[df["origem_anterior"].isna(), "classe_antes_id"].unique())
        raise RuntimeError(f"classes sem grupo e sem sentinela: {ruins}")

    # area_ha: contagem x área real do pixel, via cos(lat) MÉDIO OBSERVADO do
    # município (não do centroide). Ver "Área do pixel" no docstring do módulo.
    with np.errstate(invalid="ignore", divide="ignore"):
        cos_medio = np.where(muni_stats[:, 0] > 0, muni_stats[:, 1] / muni_stats[:, 0], np.nan)
    area_px_ha = cos_medio * AREA_PX_EQUADOR / 10_000.0
    df["area_ha"] = df["n_pixels"] * area_px_ha[df["muni_idx"].to_numpy()]

    return df[["ano_conversao", "cd_mun", "nm_mun", "idade_pastagem_anos",
               "classe_antes_id", "origem_anterior", "n_pixels", "area_ha",
               "lat_media", "lon_media"]]


def main() -> None:
    p = argparse.ArgumentParser(description="Pipeline #28 — processa o cubo censitário")
    p.add_argument("--shards", type=Path, required=True, help="Diretório com os .tif exportados")
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--limite", type=int, default=0, help="Processa só os N primeiros shards")
    args = p.parse_args()

    tifs = sorted(args.shards.glob("*.tif"))
    if not tifs:
        sys.exit(f"Nenhum .tif em {args.shards}")
    if args.limite:
        tifs = tifs[:args.limite]
    print(f"{len(tifs)} shard(s) | janela {args.janela}²")

    if args.limite:
        print("  (--limite ativo: verificação de partição pulada)")
    else:
        verificar_particao(tifs)

    print("Carregando municípios (geobr, precisão total)...")
    gdf_muni = carregar_municipios()
    print(f"  {len(gdf_muni)} municípios")

    acc = np.zeros((N_ANOS, (len(gdf_muni) + 1) * N_IDADE * N_CLASSE), dtype=np.int64)
    acc_lat = np.zeros_like(acc, dtype=np.float64)
    acc_lon = np.zeros_like(acc, dtype=np.float64)
    muni_stats = np.zeros((len(gdf_muni) + 1, 2), dtype=np.float64)  # [n_px, soma cos(lat)]
    print(f"  acumulador: {(acc.nbytes + acc_lat.nbytes + acc_lon.nbytes) / 1e6:.0f} MB "
          f"(contagem + soma lat/lon)")

    total = distintos = 0
    for i, tif in enumerate(tifs, 1):
        t0 = time.time()
        n, d = processar_shard(tif, gdf_muni, acc, acc_lat, acc_lon, muni_stats, args.janela)
        total += n
        distintos += d
        print(f"[{i:02d}/{len(tifs)}] {tif.name} — {n:,} eventos ({time.time() - t0:.0f}s)")

    if total == 0:
        print("Nenhum evento de conversão encontrado.")
        return

    df = decodificar(acc, acc_lat, acc_lon, gdf_muni, muni_stats)
    PARQUET_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_SAIDA, index=False)

    print(f"\n{'=' * 60}")
    print(f"SAÍDA: {PARQUET_SAIDA}")
    print(f"  {len(df):,} células | {df.n_pixels.sum():,} eventos de conversão")
    print(f"  {df.area_ha.sum():,.0f} ha convertidos")
    print(f"  {df.cd_mun.nunique()} municípios | {df.ano_conversao.nunique()} anos")
    cens = df.loc[df.origem_anterior == "censurado_esquerda", "n_pixels"].sum()
    print(f"  censurados: {cens:,} ({cens / df.n_pixels.sum() * 100:.1f}%)")

    sd = df.loc[df.origem_anterior == "sem_dado_anterior", "n_pixels"].sum()
    if sd:
        print(f"  sem dado anterior (classe 0): {sd:,} ({sd / df.n_pixels.sum() * 100:.4f}%) "
              f"— idade conhecida, origem indeterminada; não é censura")

    nm = df.loc[df.origem_anterior == "nao_mapeado", "n_pixels"].sum()
    if nm:
        print(f"  *** {nm:,} px ({nm / df.n_pixels.sum() * 100:.4f}%) com classe pré-pastagem "
              f"FORA do GRUPO_MAP — isto é bug de configuração: identifique a "
              f"classe, adicione ao GRUPO_MAP e reprocesse")
    print(f"  vs amostra do #28A: 43.951 px em GO "
          f"({df.n_pixels.sum() / 43951:.0f}x mais)")

    # Independência: um pixel pode converter mais de uma vez (pasto→lavoura→
    # pasto→lavoura). Cada conversão é um evento legítimo para "idade na
    # conversão", mas os eventos NÃO são observações independentes de unidades
    # distintas. Quem for calcular erro-padrão sobre esses dados precisa saber
    # a razão — se for muito acima de 1, o n efetivo é bem menor que o n bruto.
    if distintos:
        print(f"  eventos por pixel distinto: {total / distintos:.3f} "
              f"({distintos:,} pixels converteram ao menos uma vez)")
        if total / distintos > 1.10:
            print("    ATENÇÃO: reconversão frequente — eventos não são "
                  "independentes; não tratar n como tamanho amostral efetivo")

    # Sanidade: idade nunca pode exceder a distância até 1985
    fora = df[df.idade_pastagem_anos > (df.ano_conversao - ANO_MIN)]
    if len(fora):
        print(f"  ERRO: {len(fora)} células com idade > (ano - {ANO_MIN})")

    # Sanidade do centroide: Goiás cabe em lat [-19,6; -12,3] e lon [-53,3; -45,9].
    # Se uma célula cair fora, a aritmética de janela (top+rr / left+cc) está
    # errada e o controle 2D do #40 herdaria o erro em silêncio.
    geo_fora = df[(df.lat_media < -19.7) | (df.lat_media > -12.2)
                  | (df.lon_media < -53.4) | (df.lon_media > -45.8)]
    if len(geo_fora):
        print(f"  ERRO: {len(geo_fora)} células com centroide fora de Goiás "
              f"(lat {geo_fora.lat_media.min():.2f}..{geo_fora.lat_media.max():.2f}, "
              f"lon {geo_fora.lon_media.min():.2f}..{geo_fora.lon_media.max():.2f})")
    else:
        print(f"  centroide: lat {df.lat_media.min():.2f}..{df.lat_media.max():.2f} | "
              f"lon {df.lon_media.min():.2f}..{df.lon_media.max():.2f} — dentro de GO")


if __name__ == "__main__":
    main()
