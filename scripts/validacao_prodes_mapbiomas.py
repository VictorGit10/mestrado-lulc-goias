"""validacao_prodes_mapbiomas.py — Pipeline #48
Validação cruzada: PRODES Cerrado (INPE) × perda de vegetação MapBiomas
=======================================================================

PERGUNTA QUE RESPONDE
---------------------
O #39/#46/#47 usam o MapBiomas como fonte da perda de vegetação nativa (o
"convertível", o teto de oferta, o custo de carbono). A D17 deixou pendente a
validação contra uma fonte INDEPENDENTE. Esta é ela: o **PRODES Cerrado do
INPE** — o sistema oficial de monitoramento de desmatamento — concorda com a
conversão veg→antrópico que o MapBiomas mede em Goiás?

ABORDAGEM
---------
- PRODES: `yearly_deforestation` do bioma Cerrado (TerraBrasilis/INPE, WFS),
  filtrado a Goiás (367 mil polígonos), agregado por ano (km² → Mha). É
  desmatamento BRUTO de vegetação primária.
- MapBiomas: fluxo BRUTO veg→antrópico (pastagem+agricultura+área urbana) por
  ano das matrizes de transição (#12/#19). Comparação bruto×bruto (não usar o
  líquido de estoque, que abate rebrota — subestimaria).
- Duas leituras: (a) TOTAL na janela; (b) correlação anual **restrita a
  2013–2024**, o regime em que o PRODES Cerrado é ANUAL. Antes de 2013 o PRODES
  Cerrado mapeia em incrementos PLURIANUAIS (as classes d2002/d2004… somam
  vários anos), então o alinhamento ano-a-ano pré-2013 não é significativo.

ENTRADAS
    data/processed/prodes_go_anual.csv        (cache; se ausente, puxa do WFS)
    data/processed/conversao_bruta_goias.csv  (#12/#19 — transições)

SAÍDAS
    data/processed/prodes_go_anual.csv               (série PRODES, se re-puxada)
    data/processed/validacao_prodes_mapbiomas.csv    (comparação anual)
    outputs/validacao_prodes/prodes_vs_mapbiomas.png

COMO RODAR
    py -3.14 scripts/validacao_prodes_mapbiomas.py
    py -3.14 scripts/validacao_prodes_mapbiomas.py --repuxar   (força WFS)

Depende de: #12/#19 (transições). Fecha a validação PRODES da D17 (#46).
Quando foi feito: 2026-07-16.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_RAW  = ROOT / "data" / "raw" / "prodes"
DIR_OUT  = ROOT / "outputs" / "validacao_prodes"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_RAW.mkdir(parents=True, exist_ok=True)

ARQ_PRODES = DIR_PROC / "prodes_go_anual.csv"
ARQ_TRANS  = DIR_PROC / "conversao_bruta_goias.csv"

WFS = "https://terrabrasilis.dpi.inpe.br/geoserver/ows"
LAYER = "prodes-cerrado-nb:yearly_deforestation"
ANO_ANUAL = 2013  # PRODES Cerrado é anual a partir daqui; antes, incrementos plurianuais


def puxar_prodes() -> pd.DataFrame:
    """Baixa yearly_deforestation (GO) do WFS INPE, paginado, e agrega por ano."""
    import requests
    print("[PRODES] baixando yearly_deforestation (Cerrado, GO) via WFS INPE…")
    step, start, frames = 50000, 0, []
    while True:
        params = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                  "typeNames": LAYER, "outputFormat": "csv",
                  "propertyName": "state,year,area_km,class_name", "sortBy": "fid",
                  "count": str(step), "startIndex": str(start),
                  "CQL_FILTER": "state='GOIÁS'"}
        for _ in range(3):
            try:
                r = requests.get(WFS, params=params, timeout=90); r.raise_for_status(); break
            except Exception as e:
                print(f"  retry start={start} ({type(e).__name__})"); time.sleep(3)
        else:
            raise SystemExit(f"WFS falhou em start={start}")
        d = pd.read_csv(io.StringIO(r.text))
        frames.append(d); print(f"  bloco {start:>6} -> {len(d)} linhas")
        if len(d) < step:
            break
        start += step
    df = pd.concat(frames, ignore_index=True)
    if "fid" in df.columns:
        df = df.drop_duplicates(subset=["fid"])
    df.to_csv(DIR_RAW / "prodes_cerrado_go_yearly.csv", index=False)
    serie = df.groupby("year")["area_km"].sum().sort_index()
    serie.to_csv(ARQ_PRODES, header=["area_km"])
    print(f"  -> {len(df):,} polígonos | {serie.sum():.0f} km² total")
    return serie.rename("area_km").reset_index()


def carregar_prodes(repuxar: bool) -> pd.Series:
    if repuxar or not ARQ_PRODES.exists():
        puxar_prodes()
    p = pd.read_csv(ARQ_PRODES)
    p.columns = ["year", "area_km"]
    return (p.set_index("year")["area_km"] / 1e4).rename("prodes_mha")  # km² → Mha


def mapbiomas_bruto() -> pd.Series:
    """Fluxo bruto veg→antrópico por ano (Mha) das transições #12/#19."""
    t = pd.read_csv(ARQ_TRANS)
    antro = ["pastagem", "agricultura", "area_urbana"]
    g = (t[(t.grupo_orig == "vegetacao_natural") & (t.grupo_dest.isin(antro))]
         .groupby("ano_destino")["area_mha"].sum())
    return g.rename("mapbiomas_mha")


def figura(comp: pd.DataFrame, corr13: float):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axvspan(2012.5, 2024.5, color="#2e7d32", alpha=0.06)
    ax.text(2018.5, 0.98, "PRODES anual (comparável)", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=9, color="#2e7d32")
    ax.text(2007, 0.98, "PRODES plurianual\n(alinhamento não comparável)",
            transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8.5, color="0.5")
    ax.plot(comp.index, comp["mapbiomas_mha"], "o-", color="#8b3a1d", lw=2, label="MapBiomas (bruto veg→antrópico)")
    ax.plot(comp.index, comp["prodes_mha"], "s-", color="#2e7d32", lw=2, label="PRODES Cerrado (INPE)")
    ax.set_xlabel("Ano"); ax.set_ylabel("Desmatamento / conversão (Mha/ano)")
    ax.set_title("Validação cruzada — PRODES (INPE) × MapBiomas, Goiás\n"
                 f"regime anual 2013–2024: correlação r = {corr13:.2f}", loc="left", fontsize=12)
    ax.legend(frameon=True); ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "prodes_vs_mapbiomas.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'prodes_vs_mapbiomas.png').relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description="Pipeline #48 — validação PRODES × MapBiomas")
    ap.add_argument("--repuxar", action="store_true", help="força novo download do WFS INPE")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #48 — Validação cruzada PRODES (INPE) × MapBiomas (GO)")
    print("=" * 70)

    prodes = carregar_prodes(args.repuxar)
    mb = mapbiomas_bruto()
    anos = range(2002, 2025)
    comp = pd.DataFrame({"mapbiomas_mha": mb.reindex(anos),
                         "prodes_mha": prodes.reindex(anos)}).round(3)
    comp.index.name = "ano"
    comp.to_csv(DIR_PROC / "validacao_prodes_mapbiomas.csv")

    # Janela anual comparável (2013+)
    a13 = range(ANO_ANUAL, 2025)
    m13, p13 = mb.reindex(a13), prodes.reindex(a13)
    corr13 = float(m13.corr(p13))

    print("\n[totais]")
    print(f"  2002–2024  MapBiomas bruto veg→antrópico: {mb.reindex(anos).sum():.2f} Mha")
    print(f"  2002–2024  PRODES Cerrado (INPE):         {prodes.reindex(anos).dropna().sum():.2f} Mha")
    print(f"  (pré-2013 do PRODES é plurianual → totais brutos não são 1:1)")
    print(f"\n[regime anual comparável, {ANO_ANUAL}–2024]")
    print(f"  MapBiomas: {m13.sum():.2f} Mha | PRODES: {p13.sum():.2f} Mha "
          f"| razão {p13.sum()/m13.sum():.2f}")
    print(f"  correlação anual (Pearson): r = {corr13:.2f}  (n = {m13.notna().sum()} anos)")
    veredito = ("CONCORDAM" if (corr13 > 0.8 and 0.7 < p13.sum()/m13.sum() < 1.4)
                else "DIVERGEM — investigar")
    print(f"\n  VEREDITO: no regime anual, PRODES e MapBiomas **{veredito}** — "
          f"valida o MapBiomas como fonte de perda de vegetação do #39/#46/#47.")

    if not args.sem_figuras:
        print()
        figura(comp, corr13)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #48 (validação PRODES × MapBiomas).")
    print("=" * 70)


if __name__ == "__main__":
    main()
