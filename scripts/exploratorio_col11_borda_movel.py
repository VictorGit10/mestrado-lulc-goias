"""exploratorio_col11_borda_movel.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. Isto NÃO é pipeline da dissertação. A dissertação usa a Coleção 10.1 para
trás; a Coleção 11 (ago/2026) é análise exploratória à parte, por decisão do autor em
2026-08-26. Nada aqui altera #28D, D26, dossie-mosaico.html ou qualificacao/. Todas as
saídas moram em data/processed/exploratorio_col11/ e outputs/exploratorio_col11/, que
são gitignored — nenhum número daqui pode ser lido por engano como resultado do trabalho.

O QUE FAZ
---------
Roda a **Parte B** do teste da borda móvel (§9.2 do 28D) com o par 10.1 × 11, em vez do
par 9 × 10.1 do `borda_movel_colecao9.py`. A pergunta é a mesma: dos pixels que a coleção
ANTIGA chama de Mosaico(21) no ano Y, que fração a coleção NOVA reclassifica? Se a fração
dispara justamente no ano terminal da antiga, o colapso anda com a borda e é artefato.

Para este par o ano decisivo é **2024**: terminal na 10.1 (d=0) e interior na 11 (d=1,
porque a 11 vai até 2025). Os controles interiores (2010, 2015, 2019) medem o offset de
versão — a 11 põe menos Mosaico em todo lugar —, e é esse offset que a razão
R(2024)/R(controle) remove.

REUSO, NÃO CÓPIA
----------------
Importa `borda_movel_colecao9` e chama as funções dele. A máquina de casar tiles, varrer
janelas e acumular o cross-tab 4×4 é literalmente a mesma que rodou no par 9 × 10.1 —
mesmo código, mesmos IDs, mesma LUT. Só os caminhos de entrada e saída mudam. É o mesmo
padrão que o `processa_cubo_idade_destinos.py` usa com o `processa_cubo_idade`.

O parâmetro `--shards9` do módulo importado recebe a coleção ANTIGA e o `--shards10` a
NOVA; aqui isso é 10.1 e 11. Para que ninguém leia "c9" e entenda "Coleção 9", as colunas
da saída são renomeadas de c9/c10 para c101/c11 antes de gravar.

COMO RODAR
    python scripts/exploratorio_col11_borda_movel.py --max-shards 1   (cronometra 1 tile)
    python scripts/exploratorio_col11_borda_movel.py                  (os 16, com checkpoint)

Quando: 2026-08-26.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import borda_movel_colecao9 as bm  # noqa: E402 — reusa a máquina do #28E

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "processed" / "exploratorio_col11"
CSV_RECLASS = DIR_SAIDA / "col11_reclassificacao.csv"
CKPT = DIR_SAIDA / "col11_reclassificacao.ckptB.npz"

SHARDS_ANTIGA = ROOT / "data" / "raw" / "cubo_go"          # Coleção 10.1 (até 2024)
SHARDS_NOVA = ROOT / "data" / "raw" / "cubo_go_col11"      # Coleção 11   (até 2025)

# 2024 é o ano decisivo (terminal na 10.1); 2010/2015/2019 são controles interiores.
ANOS_PADRAO = [2010, 2015, 2019, 2020, 2021, 2022, 2023, 2024]

RENOMEIA = {
    "mosaico_c9": "mosaico_c101",
    "mos9_para_agri10": "mos101_para_agri11",
    "mos9_para_mos10": "mos101_para_mos11",
    "mos9_para_past10": "mos101_para_past11",
    "R_cura_mos9_agri10": "R_mos101_para_agri11",
    "R_reversa_agri9_mos10": "R_reversa_agri101_para_mos11",
    "frac_rerroteado_era_pasto_ant": "frac_rerroteado_era_pasto_ant",
    "lat_rerroteado": "lat_rerroteado",
    "lat_mosaico_c9": "lat_mosaico_c101",
    "dlat_rer_menos_mos9": "dlat_rer_menos_mos101",
}


def main() -> None:
    p = argparse.ArgumentParser(description="EXPLORATÓRIO — borda móvel 10.1 × 11 (Parte B)")
    p.add_argument("--shards-antiga", type=Path, default=SHARDS_ANTIGA)
    p.add_argument("--shards-nova", type=Path, default=SHARDS_NOVA)
    p.add_argument("--anos", type=int, nargs="+", default=ANOS_PADRAO)
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--max-shards", type=int, default=0,
                   help="máx. tiles por invocação (0=todos); checkpoint por tile")
    args = p.parse_args()

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("EXPLORATÓRIO (fora da dissertação) — borda móvel Coleção 10.1 × Coleção 11")
    print("  antiga = 10.1 (termina em 2024)   nova = 11 (termina em 2025)")
    print("  pergunta: dos Mosaico(21) da 10.1 no ano Y, o que a 11 chama?")
    print("  decisivo: 2024 é terminal na 10.1 e interior na 11")
    print("=" * 78)

    t0 = time.time()
    cont, slat, past, anos, completo, ndone, ntot = bm.parte_B(
        args.shards_antiga, args.shards_nova, sorted(args.anos),
        args.janela, CKPT, args.max_shards)

    if not completo:
        print(f"\nPARCIAL: {ndone}/{ntot} tiles ({time.time() - t0:.0f}s). Reinvoque p/ continuar.")
        return

    B = bm.finalizar_B(cont, slat, past, anos).rename(columns=RENOMEIA)
    # A 11 manda o Mosaico majoritariamente para PASTAGEM, não para agricultura (ao
    # contrário do par 9 × 10.1). As duas taxas precisam aparecer lado a lado.
    B["R_mos101_para_past11"] = B["mos101_para_past11"] / B["mosaico_c101"]
    B["R_mos101_sobrevive"] = B["mos101_para_mos11"] / B["mosaico_c101"]
    B.to_csv(CSV_RECLASS, index=False)
    CKPT.unlink(missing_ok=True)

    with pd.option_context("display.width", 150, "display.max_columns", 16):
        mostra = ["ano", "mosaico_c101", "R_mos101_sobrevive", "R_mos101_para_past11",
                  "R_mos101_para_agri11", "R_reversa_agri101_para_mos11",
                  "lat_rerroteado", "dlat_rer_menos_mos101"]
        print("\n" + B[mostra].round(4).to_string(index=False))

    print(f"\n  -> {CSV_RECLASS}  ({time.time() - t0:.0f}s)")
    print("  Leitura: R_* são frações do Mosaico da 10.1 naquele ano. Se as taxas de")
    print("           reclassificação disparam em 2024 (terminal na 10.1) contra os anos")
    print("           de controle, o colapso anda com a borda = artefato terminal.")
    print("  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
