"""_sensibilidade_w_deslocamento.py — o SLX do #34 é sensível à escolha de W?
============================================================================

POR QUÊ
-------
O Bloco B do #34 (e o bracket da D26, `deslocamento_bracket.py`) usa UMA só
matriz de vizinhança: k=8 vizinhos mais próximos, filtrados ao sul/norte,
linha-padronizada. Nunca se testou outro k. Este script reroda o SLX do bracket
(3 réguas × 2 janelas × modelos) com k = 4, 8 e 12, sem alterar o #34 nem os
CSVs do bracket.

Leitura: o veredito do #34 é "θ>0 nunca aparece; θ<0 na maioria". Sobrevive à
escolha de W se isso se mantém em k=4 e k=12.

SAÍDA
    data/processed/deslocamento_sensibilidade_w.csv

COMO RODAR
    py -3.14 scripts/_sensibilidade_w_deslocamento.py

Quando foi feito: 2026-09-23.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "scripts"))

from deslocamento_espacial import amc_para_meso, construir_pesos_direcionais  # noqa: E402
from deslocamento_bracket import rodar_slx_bracket, taxas_reguas  # noqa: E402

KS = [4, 8, 12]


def main() -> None:
    reg = amc_para_meso()
    taxas = taxas_reguas()
    todos = []
    for k in KS:
        pesos = construir_pesos_direcionais(reg, k=k)
        n_sem_sul = int((pesos["sul"].sum(axis=1) == 0).sum())
        print(f"[k={k}] AMCs sem nenhum vizinho ao sul: {n_sem_sul}")
        slx = rodar_slx_bracket(reg, pesos, taxas)
        slx.insert(0, "k", k)
        todos.append(slx)
    res = pd.concat(todos, ignore_index=True)
    res.to_csv(DIR_PROC / "deslocamento_sensibilidade_w.csv", index=False, encoding="utf-8")

    viz = res[res.termo == "vizinhanca"]
    print("\nθ do termo de vizinhança por k (* = p<0,05)")
    for (janela, regua, modelo), sub in viz.groupby(["janela", "regua_rotulo", "modelo"], sort=False):
        cel = "  ".join(f"k={r.k:<2d} θ={r.beta:+.4f} p={r.p:.3f}{'*' if r.p < 0.05 else ' '}"
                        for _, r in sub.sort_values("k").iterrows())
        print(f"  {janela:20s} {regua:22s} {modelo:38s} {cel}")

    print("\nResumo por k:")
    for k, sub in viz.groupby("k"):
        print(f"  k={k:<2d} células={len(sub):2d}  θ<0: {(sub.beta < 0).sum():2d}  "
              f"θ>0: {(sub.beta > 0).sum():2d}  θ>0 e p<0,05: {((sub.beta > 0) & (sub.p < 0.05)).sum()}  "
              f"θ<0 e p<0,05: {((sub.beta < 0) & (sub.p < 0.05)).sum()}")


if __name__ == "__main__":
    main()
