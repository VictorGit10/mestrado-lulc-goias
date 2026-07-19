"""_poder_granger_deslocamento.py — poder do Granger agregado do #34 (banca)
==========================================================================

POR QUÊ
-------
O #34 conclui "não há precedência temporal Sul→Norte" a partir de um Granger
AGREGADO com N≈38 (primeiras diferenças de 1985–2024). Um nulo (p=0,97) num teste
de baixo poder não *refuta* — apenas *não corrobora*. Este script QUANTIFICA esse
poder por simulação Monte Carlo, usando o MESMO teste do pipeline
(`statsmodels.tsa.stattools.grangercausalitytests`, ssr F-test), para que a banca
veja exatamente quanto o nulo forward do #34 vale por si só.

VEREDITO (o que sustenta a perna negativa NÃO é este Granger)
------------------------------------------------------------
Com T=38 o teste só detecta com folga efeitos GRANDES. Logo a refutação do
deslocamento causal se apoia no **spillover direcional de sinal trocado** do #34
(θ=−0,16, p=0,02, oposto ao previsto) + no **Toda-Yamamoto** do #42 — não neste
Granger de baixo poder.

DGP (x Granger-causa y de verdade; medimos a taxa de detecção):
    x_t = rho_x·x_{t-1} + u_t          (regressor persistente, como área diferenciada)
    y_t = phi_y·y_{t-1} + r·x_{t-1} + sqrt(1-r²)·e_t
`r` ≈ correlação parcial populacional de x_{t-1} sobre y (dado y_{t-1}).

COMO RODAR
    py -3.14 scripts/_poder_granger_deslocamento.py
"""
from __future__ import annotations

import sys
import warnings

import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
warnings.simplefilter("ignore")

T      = 39      # primeiras diferenças de 1985–2024 (o #34 usa ~38–36 obs efetivas)
NREP   = 2000
RHO_X  = 0.4     # persistência do regressor diferenciado
PHI_Y  = 0.2     # persistência própria de y
SEED   = 20260719


def sim_power(true_r: float, lag: int = 1) -> float:
    rng = np.random.default_rng(SEED + int(true_r * 100))
    rej = ok = 0
    for _ in range(NREP):
        x = np.zeros(T)
        for t in range(1, T):
            x[t] = RHO_X * x[t - 1] + rng.normal()
        x = (x - x.mean()) / x.std()
        e = rng.normal(size=T)
        y = np.zeros(T)
        for t in range(1, T):
            y[t] = PHI_Y * y[t - 1] + true_r * x[t - 1] + np.sqrt(max(1 - true_r**2, 0.01)) * e[t]
        data = np.column_stack([y, x])          # ordem [y, x] testa x → y
        try:
            res = grangercausalitytests(data, maxlag=[lag], verbose=False)
            rej += int(res[lag][0]["ssr_ftest"][1] < 0.05)
            ok += 1
        except Exception:  # noqa: BLE001
            pass
    return rej / ok if ok else float("nan")


def main() -> None:
    print("=" * 52)
    print(f"Poder do Granger (ssr F, lag 1, α=0,05) — T={T}, {NREP} reps")
    print(f"rho_x={RHO_X}, phi_y={PHI_Y}")
    print("=" * 52)
    print(f"{'corr. parcial verdadeira':>26} | {'poder':>7}")
    print("-" * 40)
    for r in [0.0, 0.2, 0.3, 0.4, 0.5, 0.6]:
        tag = "  ← tamanho do teste (deve ~0,05)" if r == 0.0 else ""
        print(f"{r:>26.2f} | {sim_power(r):>6.1%}{tag}")
    print("\nLeitura: com N≈38 o nulo forward do #34 (p=0,97) é fraco por si só;")
    print("a refutação se apoia no spillover θ=−0,16 (p=0,02) + Toda-Yamamoto (#42).")


if __name__ == "__main__":
    main()
