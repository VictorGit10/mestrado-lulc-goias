"""exploratorio_col11_decomposicao.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html ou qualificacao/.

POR QUE ESTE SCRIPT EXISTE
--------------------------
A razão agregada pasto→Mosaico / pasto→agricultura em 2024 vai de 32,8 (col10.1) para
3,5 (col11) — um colapso de 9,3×. A leitura tentadora é "artefato de borda": 2024 é
terminal na 10.1 e interior na 11, então o ano teria sido 'curado' ao ganhar futuro.

Mas a Parte B pixel-a-pixel (exploratorio_col11_borda_movel.py) NÃO reproduz isso: a
fração do Mosaico da 10.1 que a 11 reclassifica é plana (~0,46–0,49 em todo ano), e 2024
fica em 1,02× o controle. Sem pico. As duas medidas discordam.

A discordância não é contradição — elas medem conjuntos DIFERENTES. A Parte B mede o
ESTOQUE inteiro de Mosaico. A razão agregada mede um FLUXO fino: só os pixels que eram
pastagem no ano anterior. Este script mede o fluxo diretamente, nas duas coleções, e
decompõe o colapso em numerador × denominador:

    razão(Y) = M(Y) / A(Y),  onde  M = #(pasto_{Y-1} & mosaico_Y)
                                   A = #(pasto_{Y-1} & agri_Y)

    colapso = razão11/razão101 = (M11/M101) ÷ (A11/A101)

Se o colapso mora em M (numerador), a 11 desmontou a transição pasto→Mosaico. Se mora em
A (denominador), a 11 inflou a transição pasto→agricultura. Cada um implica uma história
diferente, e o agregado sozinho não distingue.

⚠️  Cada coleção é lida com a SUA PRÓPRIA pastagem em Y-1 — é assim que a razão agregada
é definida em borda_movel_gee.py, e é o que torna as duas linhas comparáveis. Não é o
mesmo que condicionar no mesmo conjunto de pixels.

COMO RODAR
    set GEE_PROJECT=extreme-height-447417-a9
    python scripts/exploratorio_col11_decomposicao.py

Quando: 2026-08-26.
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

# mesmos IDs de scripts/borda_movel_gee.py
ID_PASTAGEM, ID_MOSAICO = 15, 21
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]

BASE = "projects/mapbiomas-public/assets/brazil/lulc"
ASSETS = {
    "101": f"{BASE}/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1",
    "11": f"{BASE}/collection11/mapbiomas_brazil_collection11_coverage_v3",
}
ANOS = [2010, 2015, 2019, 2020, 2021, 2022, 2023, 2024]

# ⚠️ A ESCALA NÃO É INÓCUA. O docstring do borda_movel_gee.py afirma que a razão "é
# robusta à resolução" porque numerador e denominador são amostrados igual. Medido em
# 2026-08-26, isso é FALSO justamente nos anos terminais, onde a razão é grande:
#   col10.1, 2024:  37,75 (30 m) · 32,92 (100 m) · 15,36 (300 m)
#   col10.1, 2010:   1,29 (30 m) ·  1,25 (100 m) ·  0,97 (300 m)
# O ano interior quase não se move; o terminal cai por 2,5× entre 30 m e 300 m. A razão
# só é comparável entre coleções se as duas forem lidas na MESMA escala — e a escala
# precisa estar etiquetada na saída, senão vira número órfão de régua.
SCALE_PADRAO = 100  # é a escala do CSV registrado em data/processed/borda_movel_matriz_colecoes.csv


def contagens(asset: str, anos: list[int], go, scale: int) -> dict:
    """Um reduceRegion: M(Y) e A(Y) de todos os anos numa imagem multibanda."""
    img = ee.Image(asset)
    bandas = []
    for Y in anos:
        prev = img.select(f"classification_{Y - 1}").eq(ID_PASTAGEM)
        cur = img.select(f"classification_{Y}")
        isagri = cur.remap(IDS_AGRI, [1] * len(IDS_AGRI), 0)
        bandas.append(prev.And(cur.eq(ID_MOSAICO)).rename(f"M_{Y}"))
        bandas.append(prev.And(isagri).rename(f"A_{Y}"))
        bandas.append(prev.rename(f"P_{Y}"))  # base: pastagem em Y-1
    return ee.Image.cat(bandas).reduceRegion(
        ee.Reducer.sum(), go, scale=scale, maxPixels=int(1e13), tileScale=4).getInfo()


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — decomposição do colapso 10.1 × 11")
    ap.add_argument("--scale", type=int, default=SCALE_PADRAO,
                    help="m; a razão NÃO é robusta à escala nos anos terminais (ver topo)")
    ap.add_argument("--anos", type=int, nargs="+", default=ANOS)
    args = ap.parse_args()
    scale, anos_uso = args.scale, sorted(args.anos)

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    go = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM1_NAME", "Goias")).geometry())
    print("EXPLORATÓRIO — decomposição do colapso da razão (10.1 × 11), Goiás, "
          f"scale={scale} m\n")

    d = {}
    for nome, a in ASSETS.items():
        t0 = time.time()
        d[nome] = contagens(a, anos_uso, go, scale)
        print(f"  col{nome} lida em {time.time() - t0:.0f}s")

    linhas = []
    for Y in anos_uso:
        M101, A101, P101 = (d["101"][f"{k}_{Y}"] for k in ("M", "A", "P"))
        M11, A11, P11 = (d["11"][f"{k}_{Y}"] for k in ("M", "A", "P"))
        linhas.append({
            "ano": Y, "scale_m": scale,
            "pasto_ant_101": P101, "pasto_ant_11": P11,
            "M_101": M101, "M_11": M11,
            "A_101": A101, "A_11": A11,
            "razao_101": M101 / A101 if A101 else float("nan"),
            "razao_11": M11 / A11 if A11 else float("nan"),
            "fator_M": M11 / M101 if M101 else float("nan"),
            "fator_A": A11 / A101 if A101 else float("nan"),
            "fator_pasto_base": P11 / P101 if P101 else float("nan"),
        })
    df = pd.DataFrame(linhas)
    df["colapso"] = df.razao_11 / df.razao_101
    # a escala entra no NOME do arquivo: dois runs em réguas diferentes não podem
    # sobrescrever um ao outro e virar um número sem régua.
    csv = DIR_SAIDA / f"col11_decomposicao_razao_scale{scale}m.csv"
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv, index=False)

    with pd.option_context("display.width", 160, "display.max_columns", 16):
        print("\n" + df[["ano", "scale_m", "razao_101", "razao_11", "colapso",
                         "fator_M", "fator_A", "fator_pasto_base"]]
              .round(3).to_string(index=False))
    print(f"\n  -> {csv}")
    print("\n  Leitura: colapso = fator_M / fator_A. fator_M<1 = a 11 desmontou a")
    print("           transição pasto→Mosaico; fator_A>1 = a 11 inflou pasto→agricultura.")
    print("           fator_pasto_base mostra se a própria base de pastagem mudou.")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
