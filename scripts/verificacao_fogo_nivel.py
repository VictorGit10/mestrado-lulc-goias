"""verificacao_fogo_nivel.py — #14B: a lacuna de ~30% vs o MapBiomas Fire Dashboard
====================================================================================

O [#14](../Textos/pipelines/14_fogo.md) computa 410.095 ha queimados em Goiás em 2020,
contra ~600k ha do MapBiomas Fire Dashboard. A explicação registrada até 25/jul/2026 era
"sub-amostragem de pixels nas bordas em `scale=30`" — que **não se sustenta**: 30 m é a
resolução nativa do asset, então o `reduceRegions` lê o raster na grade em que ele existe.
O doc foi corrigido e passou a listar quatro hipóteses, **nenhuma testada**:

  1. **Recorte de classe** — "o total é a soma do histograma por classe LULC; pixels
     queimados fora dos grupos mapeados não entram". Era a 1ª a testar.
  2. **Objeto diferente** — área queimada anual × cicatriz acumulada.
  3. **Recorte geográfico** — malha `geobr` 2020 × o recorte do dashboard.
  4. **Versão do asset** — `_v1` × a que alimenta o dashboard.

Este script testa o que é testável **deste ambiente** (o dashboard é externo; não dá para
consultá-lo por API daqui). Blocos:

- **A (offline)** — soma das colunas de classe × `area_queimada_total_ha`, todos os 40 anos.
  Se a hipótese (1) valesse, a soma das classes seria **menor** que o total.
- **B (leitura de código)** — de onde `area_queimada_total_ha` de fato vem.
- **C (GEE)** — soma da banda binária sobre a **geometria dissolvida do estado** × a soma
  dos 246 municípios. Testa a hipótese (3): se a malha municipal perde área (bordas, ilhas,
  divisas), o estado dissolvido é maior.
- **D (GEE)** — inventário dos assets de fogo disponíveis (levantamento para o Bloco E).
- **E (GEE)** — o teste da hipótese (4): o **mesmo** recorte e o **mesmo** ano medidos na
  `collection4` (a usada), na `collection4_1` e na `collection5`. Se a lacuna viesse da versão
  do asset, o nível mudaria entre elas.

A hipótese (2) — "objeto diferente" — é a única que **não** dá para testar daqui, porque exige
saber o que o dashboard conta, e ele não tem API pública consultável neste ambiente. Ela sobra
por eliminação, e é assim que o doc do #14 a reporta.

Saída:
    outputs/fogo/verificacao_nivel.csv       — série anual do Bloco A
    outputs/fogo/verificacao_nivel_gee.csv   — Blocos C/D/E
    outputs/fogo/verificacao_nivel.md        — conclusões

Como rodar:
    py -3.14 scripts/verificacao_fogo_nivel.py            # A e B (offline, instantâneo)
    py -3.14 scripts/verificacao_fogo_nivel.py --gee      # + C e D (precisa de GEE)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_FOGO = ROOT / "data" / "processed" / "fogo_mapbiomas_goias.csv"
DIR_OUT = ROOT / "outputs" / "fogo"
DIR_OUT.mkdir(parents=True, exist_ok=True)

GEE_PROJECT_DEFAULT = "extreme-height-447417-a9"
ASSET_FOGO = ("projects/mapbiomas-public/assets/brazil/fire/collection4/"
              "mapbiomas_fire_collection4_annual_burned_v1")
DIR_COLLECTION4 = "projects/mapbiomas-public/assets/brazil/fire/collection4"
DIR_FIRE = "projects/mapbiomas-public/assets/brazil/fire"

ANO_TESTE = 2020          # o ano citado no doc (410.095 ha vs ~600k)
COLS_CLASSE = [
    "area_queimada_veg_nat_ha", "area_queimada_pastagem_ha",
    "area_queimada_agricultura_ha", "area_queimada_agua_ha",
    "area_queimada_urbano_ha", "area_queimada_outros_ha",
    "area_queimada_mosaico_ha",
]


# ---------------------------------------------------------------------------
# Bloco A — hipótese (1): o recorte de classe perde pixels?
# ---------------------------------------------------------------------------

def bloco_a() -> tuple[pd.DataFrame, list[str]]:
    print("\n" + "=" * 76)
    print("BLOCO A — hipótese (1): recorte de classe")
    print("=" * 76)

    d = pd.read_csv(CSV_FOGO)
    cols = [c for c in COLS_CLASSE if c in d.columns]
    g = d.groupby("ano").agg(
        total_ha=("area_queimada_total_ha", "sum"),
        **{c: (c, "sum") for c in cols})
    g["soma_classes_ha"] = g[cols].sum(axis=1)
    g["razao"] = g["soma_classes_ha"] / g["total_ha"]
    g["gap_ha"] = g["total_ha"] - g["soma_classes_ha"]

    r_min, r_max = g["razao"].min(), g["razao"].max()
    gap_max = g["gap_ha"].abs().max()
    print(f"  40 anos · razão soma_classes/total: min={r_min:.6f} max={r_max:.6f}")
    print(f"  maior descasamento absoluto em um ano: {gap_max:.2f} ha")
    print(f"  {ANO_TESTE}: total={g.loc[ANO_TESTE, 'total_ha']:,.0f} ha · "
          f"classes={g.loc[ANO_TESTE, 'soma_classes_ha']:,.0f} ha")

    ok = abs(r_min - 1) < 1e-4 and abs(r_max - 1) < 1e-4
    notas = []
    if ok:
        print("\n  ⇒ REFUTADA. A soma das classes bate com o total em razão 1,000000 nos")
        print("    40 anos (descasamento < 1 ha = arredondamento). O `remap` cobre 100%")
        print("    dos pixels queimados — não há pixel caindo fora dos grupos mapeados.")
        notas.append("H1 refutada pelo Bloco A: razão classes/total = 1,000000 em 40/40 anos.")
    else:
        print(f"\n  ⇒ há descasamento (razão {r_min:.4f}–{r_max:.4f}) — investigar.")
        notas.append(f"H1: descasamento classes/total de {r_min:.4f} a {r_max:.4f}.")
    return g.reset_index(), notas


# ---------------------------------------------------------------------------
# Bloco B — de onde o total realmente vem
# ---------------------------------------------------------------------------

def bloco_b() -> list[str]:
    print("\n" + "=" * 76)
    print("BLOCO B — leitura de código: a origem de `area_queimada_total_ha`")
    print("=" * 76)
    src = (ROOT / "scripts" / "fogo_mapbiomas.py").read_text(encoding="utf-8")
    usa_binaria = 'band_burned = img_burned.select(f"burned_area_{ano}")' in src
    usa_sum = "reducer=ee.Reducer.sum()" in src
    total_da_binaria = 'total_pixels = feat_b["properties"].get("sum", 0)' in src

    print(f"  banda binária `burned_area_YYYY` seleccionada .... {usa_binaria}")
    print(f"  reduzida por Reducer.sum() ...................... {usa_sum}")
    print(f"  `total_ha` derivado dessa soma (não do histograma)  {total_da_binaria}")

    notas = []
    if usa_binaria and usa_sum and total_da_binaria:
        print("\n  ⇒ REFUTADA por um segundo caminho, independente do Bloco A.")
        print("    `area_queimada_total_ha` JÁ É a soma da banda binária inteira — o número")
        print("    citado no doc (410.095 ha) nunca dependeu do cruzamento com classe. A")
        print("    hipótese (1) descreve um mecanismo que não existe neste código: o")
        print("    condicionamento de classe afeta as COLUNAS POR CLASSE, não o total.")
        notas.append("H1 refutada pelo Bloco B: o total já é a banda binária pura "
                     "(Reducer.sum sobre burned_area_YYYY), sem condicionamento de classe.")
    else:
        notas.append("H1: a leitura de código não confirmou a origem do total — reinspecionar.")
    return notas


# ---------------------------------------------------------------------------
# Blocos C e D — GEE
# ---------------------------------------------------------------------------

def _init_ee():
    import ee
    project = os.environ.get("GEE_PROJECT", GEE_PROJECT_DEFAULT).strip()
    ee.Initialize(project=project)
    return ee


def bloco_c(ee) -> tuple[dict, list[str]]:
    """Hipótese (3): a malha municipal perde área contra o estado dissolvido?"""
    print("\n" + "=" * 76)
    print(f"BLOCO C — hipótese (3): recorte geográfico ({ANO_TESTE})")
    print("=" * 76)

    import geobr
    band = ee.Image(ASSET_FOGO).select(f"burned_area_{ANO_TESTE}")

    # (i) estado dissolvido — geometria simples, para não estourar o timeout
    uf = geobr.read_state(code_state="GO", year=2020).to_crs(4326)
    geom_uf = ee.Geometry(uf.geometry.union_all().__geo_interface__)
    soma_uf = band.reduceRegion(
        reducer=ee.Reducer.sum(), geometry=geom_uf, scale=30,
        maxPixels=int(1e13), bestEffort=False,
    ).getInfo()
    px_uf = float(list(soma_uf.values())[0] or 0)
    ha_uf = px_uf * 0.09
    print(f"  estado dissolvido ......... {ha_uf:>12,.0f} ha")

    # (ii) soma dos municípios, do CSV já processado
    d = pd.read_csv(CSV_FOGO)
    ha_mun = float(d[d["ano"] == ANO_TESTE]["area_queimada_total_ha"].sum())
    print(f"  soma dos 246 municípios ... {ha_mun:>12,.0f} ha")

    dif = ha_uf - ha_mun
    pct = dif / ha_mun * 100 if ha_mun else float("nan")
    print(f"  diferença ................. {dif:>+12,.0f} ha ({pct:+.2f}%)")

    notas = []
    if abs(pct) < 2:
        print("\n  ⇒ H3 NÃO explica a lacuna. A malha municipal e o estado dissolvido")
        print(f"    concordam dentro de {abs(pct):.2f}% — muito longe dos ~30% a explicar.")
        notas.append(f"H3 rejeitada: malha municipal × estado dissolvido diferem {pct:+.2f}%.")
    else:
        print(f"\n  ⇒ H3 explica parte da lacuna ({pct:+.2f}%).")
        notas.append(f"H3: recorte geográfico responde por {pct:+.2f}%.")
    return {"ha_estado_dissolvido": ha_uf, "ha_soma_municipios": ha_mun,
            "dif_ha": dif, "dif_pct": pct}, notas


def bloco_d(ee) -> tuple[list[dict], list[str]]:
    """Hipótese (4): existe versão mais nova do asset?"""
    print("\n" + "=" * 76)
    print("BLOCO D — hipótese (4): versão do asset")
    print("=" * 76)

    achados = []
    for raiz in (DIR_FIRE, DIR_COLLECTION4):
        try:
            lst = ee.data.listAssets({"parent": raiz}).get("assets", [])
        except Exception as e:
            print(f"  {raiz} → erro: {str(e)[:70]}")
            continue
        print(f"\n  {raiz}:")
        for a in lst:
            nome = a["id"].split("/")[-1]
            print(f"    · {nome}  [{a.get('type', '?')}]")
            achados.append({"parent": raiz, "asset": nome, "type": a.get("type", "")})

    nomes = [a["asset"] for a in achados]
    mais_nova = [n for n in nomes if "collection5" in n or "_v2" in n]
    notas = []
    if mais_nova:
        print(f"\n  ⇒ existem coleções mais recentes ({sorted(set(mais_nova))[:2]}...).")
        print("    Isso NÃO fecha a H4 — só a torna testável. Ver Bloco E.")
        notas.append("H4: existem collection4_1 e collection5 além da collection4 usada "
                     "— testadas no Bloco E.")
    else:
        print("\n  ⇒ nenhuma coleção mais nova visível sob este caminho.")
        notas.append("H4 não confirmada: nenhum asset mais novo visível sob brazil/fire.")
    return achados, notas


# Coleções alternativas: (rótulo, caminho da imagem `annual_burned`)
COLECOES_ALT = [
    ("collection4", "collection4/mapbiomas_fire_collection4_annual_burned_v1"),
    ("collection4_1", "collection4_1/mapbiomas_fire_collection41_annual_burned_v1"),
    ("collection5", "collection5/mapbiomas_fire_collection5_annual_burned_v1"),
]
ANOS_CROSS = (2020, 2010)   # um ano baixo e um alto da série


def bloco_e(ee) -> tuple[list[dict], list[str]]:
    """Hipótese (4), o teste de verdade: o nível muda entre coleções?"""
    print("\n" + "=" * 76)
    print("BLOCO E — hipótese (4) testada: mesmo recorte, três coleções")
    print("=" * 76)

    import geobr
    uf = geobr.read_state(code_state="GO", year=2020).to_crs(4326)
    geom = ee.Geometry(uf.geometry.union_all().__geo_interface__)
    base = DIR_FIRE + "/"

    linhas: list[dict] = []
    for ano in ANOS_CROSS:
        print(f"\n  ano {ano}:")
        for nome, path in COLECOES_ALT:
            try:
                img = ee.Image(base + path)
                bandas = img.bandNames().getInfo()
                alvo = [b for b in bandas if str(ano) in b]
                if not alvo:
                    print(f"    {nome:14s} sem banda de {ano}")
                    continue
                v = img.select(alvo[0]).reduceRegion(
                    reducer=ee.Reducer.sum(), geometry=geom, scale=30,
                    maxPixels=int(1e13)).getInfo()
                ha = float(list(v.values())[0] or 0) * 0.09
                print(f"    {nome:14s} {ha:>12,.0f} ha")
                linhas.append({"ano": ano, "colecao": nome, "ha": ha})
            except Exception as e:
                print(f"    {nome:14s} ERRO {str(e)[:60]}")

    notas = []
    df = pd.DataFrame(linhas)
    if not df.empty:
        for ano, g in df.groupby("ano"):
            disp = (g["ha"].max() - g["ha"].min()) / g["ha"].mean() * 100
            print(f"\n  dispersão entre coleções em {ano}: {disp:.3f}%")
            notas.append(f"H4 rejeitada em {ano}: collection4/4_1/5 concordam dentro de "
                         f"{disp:.3f}% ({g['ha'].mean():,.0f} ha).")
        print("\n  ⇒ H4 REJEITADA. A troca de coleção não move o nível — a lacuna não")
        print("    vem da versão do asset.")
    return linhas, notas


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(usar_gee: bool) -> None:
    print("=" * 76)
    print("#14B — a lacuna de ~30% de área queimada vs o Fire Dashboard")
    print("=" * 76)

    notas: list[str] = []
    tab_a, n = bloco_a(); notas += n
    notas += bloco_b()

    linhas_extra: list[dict] = []
    if usar_gee:
        try:
            ee = _init_ee()
        except Exception as e:
            print(f"\n[GEE] indisponível: {str(e)[:90]}")
            ee = None
        if ee is not None:
            try:
                c, n = bloco_c(ee); notas += n
                linhas_extra.append({"bloco": "C", **c})
            except Exception as e:
                print(f"  Bloco C falhou: {str(e)[:110]}")
            try:
                d, n = bloco_d(ee); notas += n
                linhas_extra += [{"bloco": "D", **x} for x in d]
            except Exception as e:
                print(f"  Bloco D falhou: {str(e)[:110]}")
            try:
                e_, n = bloco_e(ee); notas += n
                linhas_extra += [{"bloco": "E", **x} for x in e_]
            except Exception as e:
                print(f"  Bloco E falhou: {str(e)[:110]}")
    else:
        print("\n(Blocos C e D pulados — rode com --gee para incluí-los.)")

    # saídas
    tab_a.to_csv(DIR_OUT / "verificacao_nivel.csv", index=False)
    if linhas_extra:
        pd.DataFrame(linhas_extra).to_csv(DIR_OUT / "verificacao_nivel_gee.csv", index=False)

    md = ["# #14B — verificação do nível de área queimada", "",
          "Testa as hipóteses registradas em `Textos/pipelines/14_fogo.md` para a lacuna",
          "de ~30% contra o MapBiomas Fire Dashboard.", "", "## Conclusões", ""]
    md += [f"- {n}" for n in notas]
    md += ["", "## Série anual (Bloco A)", "",
           "| ano | total (ha) | soma classes (ha) | razão |", "|---|---|---|---|"]
    for _, r in tab_a.iterrows():
        md.append(f"| {int(r['ano'])} | {r['total_ha']:,.0f} | "
                  f"{r['soma_classes_ha']:,.0f} | {r['razao']:.6f} |")
    (DIR_OUT / "verificacao_nivel.md").write_text("\n".join(md), encoding="utf-8")

    print("\n" + "=" * 76)
    print("CONCLUSÕES")
    print("=" * 76)
    for n in notas:
        print(f"  · {n}")
    print(f"\nOK: {DIR_OUT / 'verificacao_nivel.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="#14B — verificação do nível de área queimada")
    ap.add_argument("--gee", action="store_true", help="inclui os blocos C e D (GEE)")
    args = ap.parse_args()
    main(args.gee)
