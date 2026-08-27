"""exploratorio_col11_fator_multicolecao.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html ou qualificacao/.

O BURACO QUE ESTE SCRIPT TAPA
-----------------------------
A decomposição 10.1 × 11 achou que o colapso da razão mora no DENOMINADOR: a 11 encontra
3,4× mais conversão pasto→agricultura em 2024 do que a 10.1, contra só ~1,3× em 2010/2019.
Eu li isso como "assinatura de borda no canal da agricultura". **Essa leitura foi
precipitada**, e o próprio dossiê já tinha nomeado o motivo (Cap. 8, "O que este teste não
separa"): um fator que cresce em 2021–2024 é compatível com DUAS causas que o par de
coleções sozinho não distingue —

  (a) BORDA — a 10.1 sub-detecta agricultura perto do SEU fim de série; ou
  (b) CALENDÁRIO — a 11 detecta melhor a expansão real da soja, que de fato acelera a
      partir de 2021 (IBGE), e isso apareceria mesmo sem erro de borda nenhum.

O teste que separa é o mesmo que o dossiê usou para a razão (Cap. 8, Figura 5): olhar
VÁRIAS coleções, cada uma com a sua própria borda, e perguntar se o fator segue a borda de
cada uma ou um ano fixo do calendário. Aqui isso é aplicado ao CANAL DA AGRICULTURA, que é
onde a decomposição localizou o efeito — o dossiê tinha aplicado à razão.

    fator_A(X → 11, Y) = A_11(Y) / A_X(Y),   A_X(Y) = #(pasto_{Y-1} & agri_Y) na coleção X

  • BORDA    → fator_A é máximo quando Y é terminal em X, em ANOS DIFERENTES para cada X.
  • CALENDÁRIO → fator_A sobe nos MESMOS anos (2021+) em toda coleção, inclusive na 6,
                 que termina em 2020 e portanto nunca chega lá.

A col6 é o caso decisivo: ela termina em 2020, antes da quebra do calendário. Se o efeito
é de borda, `fator_A(6→11, 2020)` tem que ser grande. Se é de calendário, tem que ser
modesto — porque 2020 ainda é pré-quebra.

ESCALA
------
Roda a 100 m. Medido em 2026-08-26, os FATORES são estáveis à escala (30 m × 100 m batem na
3ª casa) mesmo que a RAZÃO não seja — porque o fator compara like-with-like entre coleções e
o viés de pirâmide cancela. A escala vai no CSV e no nome do arquivo assim mesmo.

COMO RODAR
    python scripts/exploratorio_col11_fator_multicolecao.py

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

ID_PASTAGEM, ID_MOSAICO = 15, 21
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]
BASE = "projects/mapbiomas-public/assets/brazil/lulc"

# coleção -> (asset, ano_terminal). As quatro primeiras são as do borda_movel_gee.py.
COLECOES = {
    "6":    (f"{BASE}/collection6/mapbiomas_collection60_integration_v1", 2020),
    "8":    (f"{BASE}/collection8/mapbiomas_collection80_integration_v1", 2022),
    "9":    (f"{BASE}/collection9/mapbiomas_collection90_integration_v1", 2023),
    "10.1": (f"{BASE}/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1", 2024),
    "11":   (f"{BASE}/collection11/mapbiomas_brazil_collection11_coverage_v3", 2025),
}
ANOS = [2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
REFERENCIA = "11"


def contagens(asset: str, anos: list[int], go, scale: int) -> dict:
    img = ee.Image(asset)
    bandas = []
    for Y in anos:
        prev = img.select(f"classification_{Y - 1}").eq(ID_PASTAGEM)
        cur = img.select(f"classification_{Y}")
        isagri = cur.remap(IDS_AGRI, [1] * len(IDS_AGRI), 0)
        bandas.append(prev.And(cur.eq(ID_MOSAICO)).rename(f"M_{Y}"))
        bandas.append(prev.And(isagri).rename(f"A_{Y}"))
    return ee.Image.cat(bandas).reduceRegion(
        ee.Reducer.sum(), go, scale=scale, maxPixels=int(1e13), tileScale=4).getInfo()


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — fator_A por coleção × ano")
    ap.add_argument("--scale", type=int, default=100)
    args = ap.parse_args()
    scale = args.scale

    ee.Initialize(project=os.environ.get("GEE_PROJECT", "extreme-height-447417-a9"))
    go = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM1_NAME", "Goias")).geometry())

    print("EXPLORATÓRIO — o fator segue a BORDA de cada coleção ou o CALENDÁRIO?")
    print(f"  referência = Coleção {REFERENCIA} | Goiás | scale={scale} m\n")

    dados = {}
    for nome, (asset, term) in COLECOES.items():
        anos = [a for a in ANOS if a <= term]
        t0 = time.time()
        dados[nome] = contagens(asset, anos, go, scale)
        print(f"  col{nome:5s} (→{term}) lida em {time.time() - t0:3.0f}s")

    ref = dados[REFERENCIA]
    linhas = []
    for nome, (_, term) in COLECOES.items():
        if nome == REFERENCIA:
            continue
        for Y in [a for a in ANOS if a <= term]:
            A_x, M_x = dados[nome][f"A_{Y}"], dados[nome][f"M_{Y}"]
            linhas.append({
                "colecao": nome, "ano_terminal": term, "ano": Y, "scale_m": scale,
                "d_da_borda": term - Y,
                "fator_A": ref[f"A_{Y}"] / A_x if A_x else float("nan"),
                "fator_M": ref[f"M_{Y}"] / M_x if M_x else float("nan"),
            })
    df = pd.DataFrame(linhas)
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    csv = DIR_SAIDA / f"col11_fator_multicolecao_scale{scale}m.csv"
    df.to_csv(csv, index=False)

    for campo in ("fator_A", "fator_M"):
        piv = df.pivot(index="colecao", columns="ano", values=campo)
        piv = piv.reindex([c for c in COLECOES if c != REFERENCIA])
        print(f"\n{campo}  (= canal da coleção {REFERENCIA} ÷ canal da coleção da linha)")
        print(piv.round(2).to_string())

    print("\n  Leitura de fator_A, descendo cada COLUNA (ano fixo do calendário):")
    print("   • valores parecidos entre coleções = o fator é do CALENDÁRIO")
    print("   • valor grande só onde o ano é terminal na coleção = BORDA")
    print("  Caso decisivo: col6 termina em 2020. Se é borda, fator_A(6, 2020) tem que")
    print("  ser grande; se é calendário, tem que ser modesto (2020 é pré-quebra).")
    print(f"\n  -> {csv}")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
