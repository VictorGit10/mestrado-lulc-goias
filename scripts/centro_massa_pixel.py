"""centro_massa_pixel.py — Pipeline #43
Centro de massa PIXEL-PONDERADO (MapBiomas) — robustez do Pipeline #32
=======================================================================

PERGUNTA QUE RESPONDE
---------------------
O centro de massa calculado sobre os centroides das 166 AMCs (#32) é um
artefato da malha administrativa (MAUP — AMCs do Norte são maiores/mais
irregulares que as do Sul) ou reflete de fato onde a massa da classe está no
espaço? Aqui a posição de cada pixel é o próprio pixel: sem passar por
nenhum polígono administrativo.

ABORDAGEM
---------
Para cada ano (1985–2024) e cada classe (veg. natural, pastagem,
agricultura), calcula a média de longitude/latitude de TODO pixel do raster
MapBiomas Coleção 10.1 classificado naquele grupo, sobre o contorno de
Goiás (fixo — sem malha intermediária):

    lon̄ = média(longitude_pixel | pixel ∈ classe)
    lat̄ = média(latitude_pixel  | pixel ∈ classe)

Cada pixel pesa igual (30×30 m); não há aproximação de posição por
polígono nem sensibilidade a como a AMC foi desenhada. Feito num único
reduceRegion por ano: imagem de 6 bandas (lon/lat × 3 classes), cada uma
mascarada pela própria classe — o GEE aplica o reducer 'mean' banda a
banda, cada uma só sobre seus pixels não-mascarados (semântica padrão).
Contagem de pixels por classe em reduceRegion separado (reducer 'count'
sobre bandas self-masked) — só para diagnóstico (n_pixels).

Rebanho bovino NÃO tem equivalente aqui: é estatística tabular por
município (PPM/IBGE), sem raster de posição — fica de fora deste pipeline
(ver limitação já documentada no #32).

Classes (mesmos IDs do #28/#40 — MapBiomas Coleção 10.1):
    veg_natural: Floresta(3) + Savânica(4) + Campestre(12)
    pastagem:    Pastagem(15)
    agricultura: Silvicultura(9), Lavoura Temp(19), Cana(20), Dendê(35),
                 Lavoura Per(36), Soja(39), Arroz(40), Outras Temp(41),
                 Café(46), Citros(47), Outras Per(48), Algodão(62)

COMPARAÇÃO
----------
Sobrepõe a trajetória de latitude (pixel vs AMC-centroide do #32) na mesma
figura. Se as duas curvas colam, é validação forte do método do #32 (MAUP
não é problema prático); se divergem, é achado a investigar.

ESCALA: reduceRegion roda por padrão em scale=30 (nativo MapBiomas). Se o
GEE estourar timeout/memória mesmo com tileScale=16, use --escala 60 ou 90
— o erro de posição introduzido é de dezenas de metros, irrelevante frente
aos deslocamentos de dezenas/centenas de km que a análise mede.

ENTRADAS
    asset remoto: projects/mapbiomas-public/.../collection10_1
    data/processed/centro_massa_anual.csv   (Pipeline #32, p/ comparação)

SAÍDAS
    data/processed/centro_massa_pixel_anual.csv
    outputs/centro_massa/comparacao_pixel_amc.png
    data/cache/centro_massa_pixel/{ano}.json   (cache por ano, resumível)

COMO RODAR
    earthengine authenticate            (uma vez, se ainda não feito)
    set GEE_PROJECT=extreme-height-447417-a9
    python scripts/centro_massa_pixel.py                  (completo, 1985–2024)
    python scripts/centro_massa_pixel.py --teste          (só 2024, valida rápido)
    python scripts/centro_massa_pixel.py --force           (ignora cache por ano)
    python scripts/centro_massa_pixel.py --escala 60        (mais rápido, menos preciso)

Depende de: Pipeline #32 (centro_massa.py, p/ a figura de comparação).
Quando foi feito: 2026-07-07.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS, CORES_ATO  # noqa: E402

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_CACHE     = ROOT / "data" / "cache" / "centro_massa_pixel"
DIR_OUT       = ROOT / "outputs" / "centro_massa"
for d in (DIR_PROCESSED, DIR_CACHE, DIR_OUT):
    d.mkdir(parents=True, exist_ok=True)

GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"

ANO_INI, ANO_FIM = 1985, 2024
ESCALA_PADRAO = 30  # metros; nativo MapBiomas

# Mesmos grupos/IDs do Pipeline #28 (coleta_idade_pastagem.py) e #40.
GRUPOS = {
    "veg_natural": {"ids": [3, 4, 12],                                     "rotulo": "Vegetação natural", "cor": "#2e7d32"},
    "pastagem":    {"ids": [15],                                          "rotulo": "Pastagem",          "cor": "#e8920c"},
    "agricultura": {"ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62], "rotulo": "Agricultura",       "cor": "#c2185b"},
}

ARQ_ANUAL = DIR_PROCESSED / "centro_massa_pixel_anual.csv"
ARQ_AMC   = DIR_PROCESSED / "centro_massa_anual.csv"        # Pipeline #32, p/ comparação
FIG_COMPARACAO = DIR_OUT / "comparacao_pixel_amc.png"


# ---------------------------------------------------------------------------
# 1. GEE: init + geometria + extração por ano
# ---------------------------------------------------------------------------

def init_ee():
    import ee
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    try:
        ee.Initialize(project=project)
        print(f"GEE inicializado (projeto: {project})")
    except Exception:
        print("Falha ao inicializar Earth Engine. Rode: earthengine authenticate")
        raise
    return ee


def carregar_geometria_go(ee, tolerancia_m: float = 1000):
    """Polígono de Goiás simplificado (não a bbox — a bbox vazaria pixels de
    UFs vizinhas para dentro da média de longitude/latitude).

    O polígono bruto do geobr tem ~103 mil vértices (segue cada meandro de
    rio como limite estadual) — clipar/rasterizar isso no servidor GEE
    estoura o limite de computação interativa mesmo em scale=90 com
    tileScale=16 (testado). Simplifica com tolerância de 1 km (Douglas-
    Peucker): ~800 vértices, área muda 0,005% — irrelevante frente aos
    deslocamentos de dezenas/centenas de km que a análise mede."""
    import geobr
    gdf = geobr.read_state(code_state="GO", year=2020)
    geom_simples = gdf.to_crs(5880).iloc[0].geometry.simplify(tolerancia_m, preserve_topology=True)
    import geopandas as gpd
    geom_4326 = gpd.GeoSeries([geom_simples], crs=5880).to_crs(4326).iloc[0]
    return ee.Geometry(geom_4326.__geo_interface__, proj="EPSG:4326", geodesic=False)


def _reduzir_com_retry(ee, imagem, reducer, geom, escala: int) -> dict:
    """reduceRegion com tileScale crescente (4→8→16) e timeout crescente, se o
    servidor GEE reclamar de memória ou travar (mesmo padrão de robustez do
    Pipeline #28 — coleta_idade_pastagem.py)."""
    ultimo_erro = None
    for ts, timeout_s in ((4, 120), (8, 240), (16, 480)):
        try:
            resultado = imagem.reduceRegion(reducer=reducer, geometry=geom,
                                            scale=escala, maxPixels=1e10,
                                            tileScale=ts, bestEffort=False)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(resultado.getInfo)
                try:
                    info = future.result(timeout=timeout_s)
                    if ts > 4:
                        print(f"    (sucesso com tileScale={ts})")
                    return info
                except concurrent.futures.TimeoutError:
                    print(f"    tileScale={ts} timeout após {timeout_s}s; tentando maior")
                    future.cancel()
                    continue
        except Exception as exc:
            ultimo_erro = exc
            print(f"    tileScale={ts} erro: {str(exc)[:100]}")
            continue
    raise RuntimeError(f"reduceRegion falhou em todos os tileScale: {ultimo_erro}")


def centroides_pixel_ano(ee, img_full, geom, ano: int, escala: int) -> dict:
    """Um par de reduceRegion (mean p/ posição, count p/ diagnóstico) por ano,
    cobrindo as 3 classes de uma vez (bandas mascaradas independentemente)."""
    classif = img_full.select(f"classification_{ano}")
    lonlat = ee.Image.pixelLonLat()

    bandas_media, bandas_conta = [], []
    for chave, info in GRUPOS.items():
        ids = info["ids"]
        mask = classif.eq(ids[0]) if len(ids) == 1 else classif.remap(ids, [1] * len(ids), 0)
        bandas_media.append(lonlat.select("longitude").updateMask(mask).rename(f"{chave}_lon"))
        bandas_media.append(lonlat.select("latitude").updateMask(mask).rename(f"{chave}_lat"))
        bandas_conta.append(mask.selfMask().rename(f"{chave}_n"))

    img_media = ee.Image.cat(bandas_media)
    img_conta = ee.Image.cat(bandas_conta)

    medias = _reduzir_com_retry(ee, img_media, ee.Reducer.mean(), geom, escala)
    contagens = _reduzir_com_retry(ee, img_conta, ee.Reducer.count(), geom, escala)

    linha = {"ano": ano}
    for chave in GRUPOS:
        linha[f"{chave}_lon"] = medias.get(f"{chave}_lon")
        linha[f"{chave}_lat"] = medias.get(f"{chave}_lat")
        linha[f"{chave}_n"] = contagens.get(f"{chave}_n", 0)
    return linha


# ---------------------------------------------------------------------------
# 2. Figura de comparação: pixel (este pipeline) vs AMC-centroide (#32)
# ---------------------------------------------------------------------------

def fig_comparacao(saida: pd.DataFrame) -> None:
    """Latitude × ano: cheio = centro médio sobre centroides AMC (#32);
    tracejado+marcador = centro médio pixel-a-pixel (#43, este script). Se
    colarem, o MAUP não é problema prático para a narrativa do #32."""
    import matplotlib.pyplot as plt

    if not ARQ_AMC.exists():
        print(f"[aviso] {ARQ_AMC} ausente — rode centro_massa.py (#32) primeiro. Pulando figura.")
        return
    amc = pd.read_csv(ARQ_AMC)

    fig, ax = plt.subplots(figsize=(11, 6))

    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, info["fim"] + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)
        ax.text((info["inicio"] + info["fim"]) / 2, 0.99, f"Ato {ato}",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=9, color="0.4")

    for chave, info in GRUPOS.items():
        cor, rotulo = info["cor"], info["rotulo"]
        g_amc = amc[amc.variavel == chave].sort_values("ano")
        g_pix = saida[saida.variavel == chave].sort_values("ano")
        if not g_amc.empty:
            ax.plot(g_amc["ano"], g_amc["lat_mean"], "-", color=cor, lw=2.0,
                    label=f"{rotulo} — AMC (#32)", zorder=3)
        if not g_pix.empty:
            ax.plot(g_pix["ano"], g_pix["lat_pixel"], "o--", color=cor, lw=1.3,
                    ms=3.5, alpha=0.85, label=f"{rotulo} — pixel (#43)", zorder=4)

    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°, mais alto = mais ao norte)")
    ax.set_title("Centro de massa: AMC-centroide (#32) vs pixel-ponderado MapBiomas (#43)\n"
                 "Goiás 1985–2024 — cheio = 166 polígonos AMC; tracejado = pixel bruto (sem malha)",
                 fontsize=11.5, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=8, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_COMPARACAO, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {FIG_COMPARACAO.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #43 — centro de massa pixel-ponderado (MapBiomas)")
    ap.add_argument("--teste", action="store_true", help=f"só {ANO_FIM}, valida rápido")
    ap.add_argument("--escala", type=int, default=ESCALA_PADRAO, help="metros/pixel no reduceRegion (padrão 30)")
    ap.add_argument("--force", action="store_true", help="ignora cache por ano")
    ap.add_argument("--sem-figura", action="store_true", help="só CSV, sem PNG")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #43 — Centro de massa PIXEL-ponderado (MapBiomas, Goiás)")
    print("=" * 70)

    anos = [ANO_FIM] if args.teste else list(range(ANO_INI, ANO_FIM + 1))
    if args.teste:
        print(f"MODO TESTE: só {ANO_FIM}")

    ee = init_ee()
    geom = carregar_geometria_go(ee)
    img_full = ee.Image(ASSET)

    linhas = []
    for i, ano in enumerate(anos, 1):
        cache_path = DIR_CACHE / f"{ano}.json"
        if cache_path.exists() and not args.force:
            linha = json.loads(cache_path.read_text(encoding="utf-8"))
            print(f"[{i:03d}/{len(anos)}] {ano} — cache")
        else:
            print(f"[{i:03d}/{len(anos)}] {ano} — GEE (escala {args.escala}m)...")
            t0 = time.time()
            linha = centroides_pixel_ano(ee, img_full, geom, ano, args.escala)
            cache_path.write_text(json.dumps(linha), encoding="utf-8")
            print(f"    {time.time() - t0:.1f}s")
        linhas.append(linha)

    bruto = pd.DataFrame(linhas)

    # Long format, mesmo espírito do schema do #32 (variavel, rotulo, ano, lat/lon).
    registros = []
    for chave, info in GRUPOS.items():
        for _, r in bruto.iterrows():
            registros.append({
                "variavel": chave, "rotulo": info["rotulo"], "ano": int(r["ano"]),
                "lon_pixel": r[f"{chave}_lon"], "lat_pixel": r[f"{chave}_lat"],
                "n_pixels": int(r[f"{chave}_n"]) if pd.notna(r[f"{chave}_n"]) else 0,
            })
    saida = pd.DataFrame(registros).sort_values(["variavel", "ano"]).reset_index(drop=True)

    if args.teste:
        print()
        print(saida.to_string(index=False))
        print("\n[teste OK] nada salvo em disco (exceto cache por ano).")
        return

    saida.to_csv(ARQ_ANUAL, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_ANUAL.relative_to(ROOT)}  ({len(saida)} linhas)")

    print("\n[resumo] Deslocamento N–S líquido 1985→2024 (aprox. km; 1° lat ≈ 111 km):")
    for chave, info in GRUPOS.items():
        g = saida[saida.variavel == chave].set_index("ano")
        if ANO_INI in g.index and ANO_FIM in g.index:
            dlat = (g.loc[ANO_FIM, "lat_pixel"] - g.loc[ANO_INI, "lat_pixel"]) * 111.0
            seta = "↑N" if dlat > 0 else "↓S"
            print(f"  {info['rotulo']:18s} ΔN ≈ {dlat:+6.1f} km {seta}  (pixel-ponderado)")

    if not args.sem_figura:
        print()
        fig_comparacao(saida)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #43. Robustez (MAUP) da Camada 1 (#32).")
    print("=" * 70)


if __name__ == "__main__":
    main()
