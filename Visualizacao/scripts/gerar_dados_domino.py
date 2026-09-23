"""Dados do slide "a hipótese de partida" (dominó) da apresentação.

Para cada uma das 166 AMC: ganho de agricultura e ganho de pastagem entre
1985 e 2019, em fração da área da AMC. A janela para em 2019 de propósito:
depois dela a lavoura nova passa a ser rotulada "Mosaico de Usos" (D25/D26),
e o ganho de agricultura do satélite deixa de medir o que mede aqui.

Entrada: assets/data/amcs/*.json (as séries do site).
Saída:   assets/data/domino_amc.json
"""
import glob
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
INI, FIM = 1985, 2019


def ha(v):
    # AMC sem a classe no MapBiomas vem como None (ex.: Divinópolis de Goiás não tem agricultura)
    return v or 0.0


saida = []
for f in sorted(glob.glob(str(RAIZ / "assets/data/amcs/*.json"))):
    d = json.load(open(f, encoding="utf8"))
    s = {r["ano"]: r for r in d["serie"]}
    area = s[INI]["lulc_area_total_ha"]
    saida.append({
        "amc": d["code_amc"],
        "d_agric": round((ha(s[FIM]["lulc_agricultura_ha"]) - ha(s[INI]["lulc_agricultura_ha"])) / area, 4),
        "d_pasto": round((ha(s[FIM]["lulc_pastagem_ha"]) - ha(s[INI]["lulc_pastagem_ha"])) / area, 4),
    })

destino = RAIZ / "assets/data/domino_amc.json"
json.dump({"_nota": f"Ganho de área {INI}–{FIM} em fração da área da AMC. Gerado por scripts/gerar_dados_domino.py.",
           "ini": INI, "fim": FIM, "amc": saida},
          open(destino, "w", encoding="utf8"), ensure_ascii=False)
print(f"{len(saida)} AMC -> {destino}")
