"""exploratorio_col11_sentinel_juiz.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html, qualificacao/ nem cria pipeline novo.

O TESTE (o mais forte desta rodada)
-----------------------------------
A Coleção 11 discorda da 10.1 sobre o Mosaico: ela manda ~45% dele para Pastagem e ~4%
para Agricultura. Isso é uma MUDANÇA — mas mudança não é melhora. Quem decide se a 11
acertou tem que ser uma testemunha que não seja nem a 10.1 nem a 11.

O Sentinel-2 é essa testemunha: sensor diferente (MSI, não Landsat), resolução 3× mais
fina, produto separado (`lulc_10m/collection3`). Ele já serviu de Teste 4 no dossiê, para
perguntar o que há dentro da célula-Mosaico da 10.1. Aqui ele é promovido a **juiz entre
as duas coleções Landsat**, com predições falseáveis registradas ANTES de rodar:

  população                              se a col11 ACERTOU        se a col11 ERROU
  ─────────────────────────────────────  ────────────────────────  ──────────────────
  Mosaico(10.1) → Pastagem(11)           parece PASTO ao 10 m      parece lavoura/misto
  Mosaico(10.1) → Agricultura(11)        parece LAVOURA ao 10 m    parece pasto
  Mosaico nos dois (sobrevive)           fica no meio, misto       —
  Mosaico(11) que a 10.1 NÃO via         deveria ser misto         —

As duas primeiras linhas são o coração: elas fazem predições OPOSTAS, o que torna o teste
capaz de reprovar a col11 em vez de só descrevê-la. Se as duas populações vierem parecidas,
a col11 mexeu no rótulo sem ganhar informação.

CALIBRAÇÃO (sem ela os números não significam nada). Mede-se `f_agri` também dentro de
Pastagem-nos-dois (o PISO) e Agricultura-nos-dois (o TETO). A posição de cada população no
vão piso→teto é o que se reporta, não o `f_agri` cru — é a mesma régua do Teste 4 do dossiê,
que pôs o Mosaico a 12% do caminho entre pasto e lavoura.

⚠️ O QUE ESTE TESTE NÃO DECIDE. A coleção 10 m continua sendo MapBiomas, com a mesma
legenda geral e uma classe 21 própria. Ele testa independência de SENSOR e RESOLUÇÃO, não
de metodologia nem de legenda. Se o Mosaico for uma escolha de legenda, a Sentinel herda.

MÉTODO. O estado inteiro a 10 m estoura o limite interativo do GEE, então varre-se os 6
recortes de ~1° do `mosaico_10m_sentinel.py` (Sul→Norte, núcleo agrícola→fronteira) e
agrega-se ponderando por contagem. O padrão POR recorte é bônus: o dossiê achou gradiente
de latitude na fração-lavoura, e aqui dá para ver se a col11 o acompanha.

COMO RODAR
    python scripts/exploratorio_col11_sentinel_juiz.py --teste     (1 recorte, valida)
    python scripts/exploratorio_col11_sentinel_juiz.py             (os 6 recortes)

Quando: 2026-08-27.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ee
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "processed" / "exploratorio_col11"

ID_PASTAGEM, ID_MOSAICO = 15, 21
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

BASE = "projects/mapbiomas-public/assets/brazil/lulc"
ASSET_101 = f"{BASE}/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
ASSET_11 = f"{BASE}/collection11/mapbiomas_brazil_collection11_coverage_v3"
ASSET_10M = ("projects/mapbiomas-public/assets/brazil/lulc_10m/collection3/"
             "mapbiomas_10m_collection3_integration_v1")

# mesmos recortes do mosaico_10m_sentinel.py (Teste 4 do dossiê), Sul -> Norte
REGIOES = {
    "SO_RioVerde":    (-51.5, -18.5, -50.5, -17.5),
    "Sul_Itumbiara":  (-49.5, -18.5, -48.5, -17.5),
    "SE_Catalao":     (-48.3, -18.3, -47.3, -17.3),
    "Centro_Goiania": (-49.8, -16.8, -48.8, -15.8),
    "NE_Posse":       (-47.2, -14.6, -46.2, -13.6),
    "N_Porangatu":    (-49.6, -13.8, -48.6, -12.8),
}
ANO = 2024  # último ano comum às três fontes (10.1 vai a 2024; a 10 m, a 2024)


def populacoes(a101: ee.Image, a11: ee.Image) -> dict:
    """As máscaras de 30 m que definem cada população. Chaves = nome na saída."""
    agri101 = a101.remap(IDS_AGRI, [1] * len(IDS_AGRI), 0)
    agri11 = a11.remap(IDS_AGRI, [1] * len(IDS_AGRI), 0)
    mos101, mos11 = a101.eq(ID_MOSAICO), a11.eq(ID_MOSAICO)
    pas101, pas11 = a101.eq(ID_PASTAGEM), a11.eq(ID_PASTAGEM)
    return {
        "mos101_para_pasto11": mos101.And(pas11),
        "mos101_para_agri11": mos101.And(agri11),
        "mos101_sobrevive": mos101.And(mos11),
        "mos11_novo": mos11.And(mos101.Not()),
        "PISO_pasto_nos_dois": pas101.And(pas11),
        "TETO_agri_nos_dois": agri101.And(agri11),
    }


def composicao(mascara30: ee.Image, s10: ee.Image, region, escala: int) -> dict:
    """Tabula a classe 10 m de todos os pixels sob a máscara de 30 m. A fração de
    cada classe é a composição de área daquela população no olhar da Sentinel."""
    h = (s10.updateMask(mascara30.selfMask())
            .reduceRegion(ee.Reducer.frequencyHistogram(), region,
                          scale=escala, maxPixels=int(1e13), tileScale=8).getInfo())
    raw = next(iter(h.values()), None) or {}
    hist = {int(float(k)): int(round(v)) for k, v in raw.items()}
    tot = sum(hist.values())
    if tot == 0:
        return {"n_10m": 0, "f_agri": float("nan"), "f_pasto": float("nan"),
                "f_mos": float("nan"), "f_outro": float("nan")}
    fa = sum(hist.get(i, 0) for i in IDS_AGRI) / tot
    fp = hist.get(ID_PASTAGEM, 0) / tot
    fm = hist.get(ID_MOSAICO, 0) / tot
    return {"n_10m": tot, "f_agri": fa, "f_pasto": fp, "f_mos": fm,
            "f_outro": max(0.0, 1.0 - fa - fp - fm)}


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — Sentinel-2 como juiz entre 10.1 e 11")
    ap.add_argument("--escala", type=int, default=10, help="m; 10 = nativo da Sentinel")
    ap.add_argument("--ano", type=int, default=ANO)
    ap.add_argument("--teste", action="store_true", help="só o recorte de Rio Verde")
    args = ap.parse_args()

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    Y = args.ano
    a101 = ee.Image(ASSET_101).select(f"classification_{Y}")
    a11 = ee.Image(ASSET_11).select(f"classification_{Y}")
    s10 = ee.Image(ASSET_10M).select(f"classification_{Y}")
    pops = populacoes(a101, a11)

    regs = {"SO_RioVerde": REGIOES["SO_RioVerde"]} if args.teste else REGIOES
    print("EXPLORATÓRIO — Sentinel-2 (10 m) julga a revisão da Coleção 11")
    print(f"  ano={Y} | escala={args.escala} m | {len(regs)} recorte(s)\n")

    linhas = []
    for nome_reg, bbox in regs.items():
        region = ee.Geometry.Rectangle(list(bbox), proj="EPSG:4326", geodesic=False)
        for nome_pop, m in pops.items():
            t0 = time.time()
            try:
                r = composicao(m, s10, region, args.escala)
            except Exception as e:
                print(f"  [ERRO] {nome_reg}/{nome_pop}: {type(e).__name__} {str(e)[:110]}")
                continue
            r.update({"regiao": nome_reg, "populacao": nome_pop, "ano": Y,
                      "escala_m": args.escala, "lat_centro": (bbox[1] + bbox[3]) / 2})
            linhas.append(r)
            print(f"  {nome_reg:16s} {nome_pop:22s} n={r['n_10m']:>10,} "
                  f"f_agri={r['f_agri']:.3f} f_pasto={r['f_pasto']:.3f} "
                  f"f_mos={r['f_mos']:.3f}  ({time.time()-t0:.0f}s)", flush=True)

    df = pd.DataFrame(linhas)
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    csv = DIR_SAIDA / f"col11_sentinel_juiz_{Y}_escala{args.escala}m.csv"
    df.to_csv(csv, index=False)

    # agregado ponderado por contagem de pixels 10 m
    print("\nAGREGADO (ponderado por n de pixels 10 m, todos os recortes)")
    ag = (df.assign(**{c: df[c] * df.n_10m for c in ("f_agri", "f_pasto", "f_mos", "f_outro")})
            .groupby("populacao")[["n_10m", "f_agri", "f_pasto", "f_mos", "f_outro"]].sum())
    for c in ("f_agri", "f_pasto", "f_mos", "f_outro"):
        ag[c] = ag[c] / ag.n_10m
    ordem = ["PISO_pasto_nos_dois", "mos101_para_pasto11", "mos101_sobrevive",
             "mos11_novo", "mos101_para_agri11", "TETO_agri_nos_dois"]
    ag = ag.reindex([o for o in ordem if o in ag.index])
    print(ag.round(4).to_string())

    if {"PISO_pasto_nos_dois", "TETO_agri_nos_dois"} <= set(ag.index):
        piso, teto = ag.loc["PISO_pasto_nos_dois", "f_agri"], ag.loc["TETO_agri_nos_dois", "f_agri"]
        print(f"\nPosição no vão pasto→lavoura (piso={piso:.3f}, teto={teto:.3f}):")
        for pop in ag.index:
            if pop.startswith(("PISO", "TETO")):
                continue
            pos = (ag.loc[pop, "f_agri"] - piso) / (teto - piso)
            print(f"  {pop:22s} {100*pos:5.1f}% do caminho entre pasto e lavoura")
        print("\n  Predição registrada: se a col11 acertou, 'mos101_para_pasto11' fica")
        print("  perto do piso e 'mos101_para_agri11' perto do teto. Se as duas vierem")
        print("  parecidas, a col11 trocou rótulo sem ganhar informação.")

    print(f"\n  -> {csv}")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
