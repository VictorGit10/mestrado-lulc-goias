"""mosaico_10m_sentinel.py — a 10 m (Sentinel-2) olha DENTRO da célula-Mosaico de 30 m
================================================================================

Opção A do teste que a borda-móvel (§9.6 do 28D) deixou em aberto: separar
*artefato-de-rótulo compartilhado* de *ILP real* na deriva do Mosaico. A
borda-móvel matou o "artefato de fim-de-série" (a rampa é ancorada no calendário
2021+, não na borda), mas NÃO separa "o classificador rerroteou soja recém-
convertida para Mosaico" de "a paisagem virou mistura de verdade" — as duas dão a
mesma série *dentro de uma coleção Landsat 30 m*.

A coleção 10 m (Sentinel-2, `lulc_10m/collection3`, 2017–2024) é independente em
DOIS eixos que a borda-móvel não tocou:
  • SENSOR diferente (Sentinel-2 MSI, não Landsat) → imune à hipótese "mudança de
    insumo ~2021 (Landsat 7→9) herdada por todas as coleções".
  • RESOLUÇÃO 3× mais fina → dá pra olhar DENTRO de uma célula-Mosaico de 30 m.

O QUE ELA *NÃO* DECIDE (honestidade obrigatória): continua sendo MapBiomas, mesma
legenda (até nível 3), classe 21 própria, filtros parecidos. Testa independência
de sensor+resolução, NÃO de metodologia/legenda. Se o Mosaico for uma *escolha de
legenda*, a Sentinel pode herdar. É diagnóstico, não um swap que devolve 100/0.

--------------------------------------------------------------------------------
O TESTE (uma frase): pegar as células que a Landsat 10.1 (30 m) rotula Mosaico
(classe 21) e perguntar à Sentinel (10 m) qual é a COMPOSIÇÃO por fração de área
lá dentro, no mesmo ano.

Como: tabula-se a classe 10 m de todos os pixels sob as células-Mosaico de 30 m
(reduceRegion.frequencyHistogram, num recorte limitado — ver `composicao`). A
fração de cada classe = a composição de área. Os desfechos:

  • f_agri ALTO (célula-Mosaico é lavoura limpa a 10 m)  → hedge de RESOLUÇÃO →
    artefato dominante e recuperável.
  • mistura f_agri~f_pasto equilibrada                   → ILP real (paisagem mista).
  • f_mos ALTO (Sentinel também diz Mosaico)             → os dois produtos hedgeiam
    → não é problema de 30 m → pende p/ legenda compartilhada; inconclusivo no eixo.

Dois controles que tornam isto decisivo:
  (1) CALENDÁRIO — a mesma composição num ano interior pré-deriva (2018) vs anos-
      deriva (2021–24). Se a célula-Mosaico RECENTE tem mais f_agri que a ANTIGA,
      o Mosaico novo é "mais lavoura" = assinatura do artefato. Se iguais, o
      Mosaico sempre significou isto (pende p/ ILP/legenda).
  (2) CALIBRAÇÃO — f_agri dentro das células que a Landsat diz Agricultura (teto)
      e Pastagem (piso). Onde f_agri|Mosaico cai entre piso e teto localiza o
      Mosaico no espectro pasto↔lavoura.

O estado inteiro numa chamada estoura o limite interativo do GEE (e `sample` sobre
a geometria estadual é igualmente lento). Solução: varrer 6 recortes de ~1° que
cobrem GO Sul→Norte (REGIOES) e agregar count-weighted — cada chamada volta em ~2 s.
O padrão POR região é bônus (a deriva "aterrissa na fronteira norte", §8 do 28D).

--------------------------------------------------------------------------------
COMO RODAR
    set GEE_PROJECT=extreme-height-447417-a9
    python scripts/mosaico_10m_sentinel.py --teste        # só Rio Verde + legenda 10 m (valida)
    python scripts/mosaico_10m_sentinel.py                # varre as 6 regiões (2018 × 2024)
    python scripts/mosaico_10m_sentinel.py --anos 2018 2020 2022 2024   # mais anos na varredura
    python scripts/mosaico_10m_sentinel.py --bbox -51.5 -18.5 -50.5 -17.5   # 1 recorte, série cheia
    python scripts/mosaico_10m_sentinel.py --escala 10    # exato (lê 10 m nativo; mais lento)

SAÍDAS  data/processed/mosaico_10m_sentinel.csv        (regiao × populacao × ano × fração)
        data/processed/mosaico_10m_sentinel_hist.csv   (classe 10 m × região × ano)

Quando: 2026-07-24. Companheiro do #28D / a "ponta pendente" da coleção 10 m.
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
CSV = ROOT / "data" / "processed" / "mosaico_10m_sentinel.csv"
CSV_HIST = ROOT / "data" / "processed" / "mosaico_10m_sentinel_hist.csv"

ID_PASTAGEM = 15
ID_MOSAICO = 21
IDS_AGRICULTURA = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

# 30 m Landsat (referência de grade e da máscara-Mosaico) e 10 m Sentinel (a testemunha).
ASSET_30M = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
ASSET_10M = "projects/mapbiomas-public/assets/brazil/lulc_10m/collection3/mapbiomas_10m_collection3_integration_v1"

ANOS_PADRAO = [2018, 2020, 2021, 2022, 2023, 2024]  # 2018 = controle interior pré-deriva
ANO_CONTROLE = 2018
ANO_BASE_DERIVA = 2017  # 1º ano da 10 m; "era pasto no início da Sentinel e virou Mosaico em Y"
ANOS_CALIBRACAO = [2018, 2024]  # teto/piso (Agri/Pasto 30 m) nestes anos

# bbox de agricultura densa no SO de Goiás (região de Rio Verde) p/ o --teste
TESTE_BBOX = (-51.5, -18.5, -50.5, -17.5)

# 6 recortes de ~1° dentro de GO, Sul→Norte e núcleo agrícola→fronteira. O estado
# inteiro numa chamada estoura o GEE (visto); varrer bboxes limitados e agregar
# count-weighted é o caminho viável — e o padrão POR região é informativo (a deriva
# "aterrissa na fronteira norte", §8 do 28D).
REGIOES = {
    "SO_RioVerde":    (-51.5, -18.5, -50.5, -17.5),
    "Sul_Itumbiara":  (-49.5, -18.5, -48.5, -17.5),
    "SE_Catalao":     (-48.3, -18.3, -47.3, -17.3),
    "Centro_Goiania": (-49.8, -16.8, -48.8, -15.8),
    "NE_Posse":       (-47.2, -14.6, -46.2, -13.6),
    "N_Porangatu":    (-49.6, -13.8, -48.6, -12.8),
}
SWEEP_ANOS = [2018, 2024]  # controle interior × terminal, na varredura de regiões


def composicao(mascara30: ee.Image, s10: ee.Image, region, escala: int,
               seed: int = 0) -> tuple[dict, dict]:
    """Tabula a classe 10 m de TODOS os pixels sob as células-Mosaico de 30 m
    (`mascara30`) num RECORTE limitado, via reduceRegion.frequencyHistogram. A
    fração de cada classe = a composição de área da população, no olhar da Sentinel.

    Recorte limitado (bbox ~1°), não o estado inteiro: o reduceResolution/leitura
    10 m sobre GO inteiro estoura o limite interativo do GEE (visto na prática — e
    `sample` sobre a geometria estadual é igualmente lento, varre a região toda).
    Num bbox de ~1° a chamada é exata e volta em segundos. Estado = varrer bboxes e
    somar (count-weighted). Devolve (linha_de_frações, histograma_de_classes)."""
    h = (s10.updateMask(mascara30)
            .reduceRegion(ee.Reducer.frequencyHistogram(), region,
                          scale=escala, maxPixels=int(1e13), tileScale=8).getInfo())
    raw = next(iter(h.values()), None) or {}
    hist = {int(float(k)): int(round(v)) for k, v in raw.items()}
    total = sum(hist.values())
    if total == 0:
        return {"n_cells": 0, "f_agri": 0.0, "f_pasto": 0.0, "f_mos": 0.0, "f_outro": 0.0}, hist
    fa = sum(hist.get(i, 0) for i in IDS_AGRICULTURA) / total
    fp = hist.get(ID_PASTAGEM, 0) / total
    fm = hist.get(ID_MOSAICO, 0) / total
    return ({"n_cells": total, "f_agri": fa, "f_pasto": fp, "f_mos": fm,
             "f_outro": max(0.0, 1.0 - fa - fp - fm)}, hist)


def diag_legenda_10m(Y: int, region, scale: int) -> None:
    """Frequência das classes 10 m no recorte — p/ conferir que os IDs de
    agricultura da legenda 30 m batem com a 10 m (senão viram 'outro' silencioso)."""
    s = ee.Image(ASSET_10M).select(f"classification_{Y}")
    h = s.reduceRegion(ee.Reducer.frequencyHistogram(), region,
                       scale=scale, maxPixels=int(1e13), tileScale=8).getInfo()
    hist = h.get(f"classification_{Y}", {}) or {}
    tot = sum(hist.values()) or 1
    conhecido = set(map(str, IDS_AGRICULTURA)) | {str(ID_PASTAGEM), str(ID_MOSAICO)}
    print(f"\n  Legenda 10 m presente em {Y} (recorte-teste) — 'outro' = fora de agri/pasto/mosaico:")
    for cid, cnt in sorted(hist.items(), key=lambda kv: -kv[1]):
        tag = ("AGRI" if cid in map(str, IDS_AGRICULTURA)
               else "PASTO" if cid == str(ID_PASTAGEM)
               else "MOSAICO" if cid == str(ID_MOSAICO) else "outro")
        print(f"    classe {cid:>3}: {cnt/tot*100:6.2f}%   [{tag}]")
    fora = [cid for cid in hist if cid not in conhecido and hist[cid] / tot > 0.01]
    if fora:
        print(f"  ⚠️  classes >1% tratadas como 'outro': {sorted(fora, key=int)} — "
              f"conferir se alguma é agricultura na legenda 10 m antes de confiar em f_agri.")


def anos_disponiveis_10m() -> list[int]:
    nomes = ee.Image(ASSET_10M).bandNames().getInfo()
    anos = sorted(int(n.split("_")[1]) for n in nomes if n.startswith("classification_"))
    return anos


def varre_regiao(label: str, region, anos_mos: list[int], col30, escala: int,
                 com_extra: bool) -> tuple[list[dict], list[dict]]:
    """Composição da população-Mosaico (todos os anos de `anos_mos`) num recorte, e,
    se `com_extra`, também deriva + calibração no ano terminal. Devolve (linhas, hist)."""
    linhas, hist_rows = [], []
    for Y in anos_mos:
        land = col30.select(f"classification_{Y}")
        s10 = ee.Image(ASSET_10M).select(f"classification_{Y}")
        t0 = time.time()
        lin, hist = composicao(land.eq(ID_MOSAICO), s10, region, escala)
        linhas.append({"regiao": label, "populacao": "mosaico", "ano": Y, **lin})
        for cid, cnt in sorted(hist.items()):
            hist_rows.append({"regiao": label, "ano": Y, "classe_10m": cid, "count": cnt})
        print(f"    [{label:16s}] {Y} mosaico — {time.time()-t0:.0f}s | "
              f"n={lin['n_cells']:>9,} f_agri={lin['f_agri']:.3f} "
              f"f_pasto={lin['f_pasto']:.3f} f_mos={lin['f_mos']:.3f} f_outro={lin['f_outro']:.3f}",
              flush=True)

    if com_extra:
        Yt = anos_mos[-1]
        land = col30.select(f"classification_{Yt}")
        s10 = ee.Image(ASSET_10M).select(f"classification_{Yt}")
        deriva = land.eq(ID_MOSAICO).And(
            col30.select(f"classification_{ANO_BASE_DERIVA}").eq(ID_PASTAGEM))
        dd, _ = composicao(deriva, s10, region, escala)
        linhas.append({"regiao": label, "populacao": "deriva_pasto→mos", "ano": Yt, **dd})
        agri30 = land.remap(IDS_AGRICULTURA, [1] * len(IDS_AGRICULTURA), 0).eq(1)
        da, _ = composicao(agri30, s10, region, escala)
        linhas.append({"regiao": label, "populacao": "ref_agri30", "ano": Yt, **da})
        dp, _ = composicao(land.eq(ID_PASTAGEM), s10, region, escala)
        linhas.append({"regiao": label, "populacao": "ref_pasto30", "ano": Yt, **dp})
    return linhas, hist_rows


def wmean(g: pd.DataFrame, col: str) -> float:
    """Média de `col` ponderada por n_cells (= agregação count-weighted exata das frações)."""
    n = g["n_cells"].sum()
    return float((g[col] * g["n_cells"]).sum() / n) if n else 0.0


def main() -> None:
    p = argparse.ArgumentParser(description="Composição 10 m dentro da célula-Mosaico de 30 m (Opção A do #28D)")
    p.add_argument("--anos", type=int, nargs="+", default=None,
                   help=f"anos da população-Mosaico (default: varredura={SWEEP_ANOS}, teste/bbox={ANOS_PADRAO})")
    p.add_argument("--escala", type=int, default=30,
                   help="m do reduceRegion; 30 = ~1 px 10 m por célula (rápido); 10 = exato (lento)")
    p.add_argument("--bbox", type=float, nargs=4, metavar=("LON0", "LAT0", "LON1", "LAT1"),
                   help="recorte único; sem isto (nem --teste) varre as 6 regiões de GO")
    p.add_argument("--teste", action="store_true",
                   help="só Rio Verde + diagnóstico de legenda 10 m; valida o caminho")
    args = p.parse_args()

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    disp = anos_disponiveis_10m()
    print(f"Sentinel 10 m (Coleção 3 beta) — anos disponíveis: {disp[0]}..{disp[-1]} ({len(disp)} bandas)")
    col30 = ee.Image(ASSET_30M)

    # modo
    if args.bbox:
        regioes = {"bbox": tuple(args.bbox)}
        anos = [a for a in (args.anos or ANOS_PADRAO) if a in disp]
        sweep = False
    elif args.teste:
        regioes = {"SO_RioVerde": TESTE_BBOX}
        anos = [a for a in (args.anos or ANOS_PADRAO) if a in disp]
        diag_legenda_10m(anos[-1], ee.Geometry.Rectangle(list(TESTE_BBOX)), 30)
        sweep = False
    else:
        regioes = REGIOES
        anos = [a for a in (args.anos or SWEEP_ANOS) if a in disp]
        sweep = True
    if not anos:
        sys.exit("Nenhum ano pedido existe na coleção 10 m.")

    print(f"escala={args.escala} m | anos-mosaico {anos} | {len(regioes)} recorte(s) | "
          f"base-deriva {ANO_BASE_DERIVA}\n")

    todas, hist_all = [], []
    for label, bb in regioes.items():
        region = ee.Geometry.Rectangle(list(bb), proj="EPSG:4326", geodesic=False)
        linhas, hrows = varre_regiao(label, region, anos, col30, args.escala, com_extra=True)
        todas.extend(linhas)
        hist_all.extend(hrows)
        pd.DataFrame(todas).to_csv(CSV, index=False)  # incremental (resiliente a interrupção)

    df = pd.DataFrame(todas)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False)
    pd.DataFrame(hist_all).to_csv(CSV_HIST, index=False)

    # ---- leitura: agregado count-weighted sobre as regiões ----
    ag = (df.groupby(["populacao", "ano"])
            .apply(lambda g: pd.Series({
                "n_cells": int(g["n_cells"].sum()),
                "f_agri": wmean(g, "f_agri"), "f_pasto": wmean(g, "f_pasto"),
                "f_mos": wmean(g, "f_mos"), "f_outro": wmean(g, "f_outro")}),
                   include_groups=False)
            .reset_index())
    mos = ag[ag.populacao == "mosaico"].set_index("ano")
    print("\n== COMPOSIÇÃO 10 m DENTRO DAS CÉLULAS-MOSAICO DE 30 m (agregado GO) ==")
    print(mos[["n_cells", "f_agri", "f_pasto", "f_mos", "f_outro"]].round(3).to_string())

    if sweep:  # padrão geográfico: f_agri|Mosaico no ano terminal por região (Sul→Norte)
        Yt = anos[-1]
        geo = (df[(df.populacao == "mosaico") & (df.ano == Yt)]
               .set_index("regiao")[["n_cells", "f_agri", "f_pasto", "f_mos", "f_outro"]])
        geo = geo.reindex([r for r in REGIOES if r in geo.index])
        print(f"\n  Padrão geográfico em {Yt} (ordem Sul→Norte) — f_agri dentro do Mosaico:")
        print(geo.round(3).to_string())

    der = ag[ag.populacao == "deriva_pasto→mos"].set_index("ano")
    if not der.empty:
        print(f"\n  População-deriva (era pasto em {ANO_BASE_DERIVA}, virou Mosaico no terminal) — a mais afiada:")
        print(der[["n_cells", "f_agri", "f_pasto", "f_mos", "f_outro"]].round(3).to_string())

    if ANO_CONTROLE in mos.index and anos[-1] != ANO_CONTROLE:
        d_cal = mos.loc[anos[-1], "f_agri"] - mos.loc[ANO_CONTROLE, "f_agri"]
        print(f"\n  Δcalendário f_agri|Mosaico ({anos[-1]} − {ANO_CONTROLE}) = {d_cal:+.3f}")
        print("    > 0 e grande → Mosaico recente é 'mais lavoura' = assinatura de ARTEFATO")
        print("    ~ 0          → Mosaico sempre significou o mesmo = pende p/ ILP/legenda")

    Yc = anos[-1]
    calf = ag[ag.populacao.isin(["ref_agri30", "ref_pasto30"]) & (ag.ano == Yc)]
    if len(calf) == 2:
        teto = calf[calf.populacao == "ref_agri30"]["f_agri"].iloc[0]
        piso = calf[calf.populacao == "ref_pasto30"]["f_agri"].iloc[0]
        fmos = mos.loc[Yc, "f_agri"]
        pos = (fmos - piso) / (teto - piso) if teto > piso else float("nan")
        print(f"\n  Calibração em {Yc}: f_agri|Pasto(piso)={piso:.3f}  "
              f"f_agri|Mosaico={fmos:.3f}  f_agri|Agri(teto)={teto:.3f}")
        print(f"    → Mosaico está a {pos*100:.0f}% do caminho pasto→lavoura no olhar da 10 m")

    print("\n  Lembrete: a 10 m é MapBiomas — testa sensor+resolução, NÃO legenda/metodologia.")
    print("  f_mos alto = os dois produtos hedgeiam (resolução NÃO é o gargalo → pende p/ legenda).")
    print(f"  Distribuição de classes 10 m por região/ano em {CSV_HIST.name} (o que é o 'outro').")
    print(f"\n  -> {CSV}\n  -> {CSV_HIST}")


if __name__ == "__main__":
    main()
