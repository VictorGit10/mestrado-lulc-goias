"""
bimodalidade_regional_uniao.py — re-checagem do #28C sob a união (D26)
=====================================================================

O bracket-por-evento do #40 mostrou que o gradiente young-Sul/old-Norte sobre
`pasto→agricultura` some sob `pasto→(agric∪mosaico)`. O #28C usa a MESMA fonte
(só destino=agricultura) e faz afirmações do mesmo tipo. Esta é a re-checagem que
o próprio #40 pediu: recomputa as três afirmações do #28C sob os dois conjuntos de
evento, usando o cubo com destino=Mosaico (`pastagem_conversao_destinos.parquet`):

  (1) GRADIENTE — idade mediana ponderada por mesorregião (Sul→Norte).
  (2) DECOMPOSIÇÃO — η² da idade e da separação jovem/velho por região/ato.
  (3) BIMODALIDADE — quantas regiões e células região×ato seguem bimodais.

Reusa as funções ponderadas do #28C (`bimodalidade_regional`) tal como estão —
mesmas métricas, só troca o conjunto de eventos.

SAÍDA
    data/processed/bimodalidade_uniao_check.csv

COMO RODAR (depois de processa_cubo_idade_destinos.py)
    python scripts/bimodalidade_regional_uniao.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bimodalidade_regional as bm  # noqa: E402 — reuso das estatísticas ponderadas do #28C
from config_periodos import ATOS    # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARQ_DESTINOS = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"
ARQ_MESO = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
ARQ_OUT = ROOT / "data" / "processed" / "bimodalidade_uniao_check.csv"

CONJUNTOS = {"agric (pasto→agricultura)": {"agricultura"},
             "união (pasto→agric∪mosaico)": {"agricultura", "mosaico"}}


def ato_de(ano: int):
    for k, v in ATOS.items():
        if v["inicio"] <= ano <= v["fim"]:
            return k
    return None


def preparar(dset) -> pd.DataFrame:
    df = pd.read_parquet(ARQ_DESTINOS)
    df = df[df["destino"].isin(dset)].copy()
    df = df.rename(columns={"n_pixels": "peso"})
    df["peso"] = df["peso"].astype("float64")
    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    meso = pd.read_csv(ARQ_MESO, dtype={"cd_mun": "int64"})[["cd_mun", "nm_meso"]]
    df = df.merge(meso, on="cd_mun", how="left").rename(columns={"nm_meso": "mesorregiao"})
    df["ato"] = df["ano_conversao"].map(ato_de)
    dnc = df[(~df["censurado"]) & df["mesorregiao"].notna() & (df["mesorregiao"] != "")
             & df["ato"].notna()].copy()
    return dnc


def analisar(dnc: pd.DataFrame, nome: str) -> list[dict]:
    print(f"\n{'═' * 78}\n{nome}  ({dnc['peso'].sum() / 1e6:.1f} Mpx não-censurados)\n{'═' * 78}")

    # (1) GRADIENTE — idade mediana por mesorregião, ordenada
    med = {u: bm.mediana_p(g["idade_pastagem_anos"].to_numpy(float), g["peso"].to_numpy(float))
           for u, g in dnc.groupby("mesorregiao", observed=True)}
    ordem = sorted(med, key=lambda u: med[u])
    print("(1) idade mediana por mesorregião (jovem→velho):")
    for u in ordem:
        print(f"      {u:<18} {med[u]:.0f}a")
    amp = med[ordem[-1]] - med[ordem[0]]
    print(f"    → amplitude Sul→Norte = {amp:.0f}a")

    # (2) DECOMPOSIÇÃO η²
    eta_esp = bm.eta_squared(dnc, "idade_pastagem_anos", "mesorregiao")
    eta_ato = bm.eta_squared(dnc, "idade_pastagem_anos", "ato")
    eta_esp_ato = bm.eta_squared(dnc, "idade_pastagem_anos", ["mesorregiao", "ato"])
    z = bm.posterior_modo_velho(dnc["idade_pastagem_anos"].to_numpy(float),
                                dnc["peso"].to_numpy(float))
    dnc = dnc.assign(p_velho=z)
    etaz_esp = bm.eta_squared(dnc, "p_velho", "mesorregiao")
    print("(2) decomposição de variância:")
    print(f"      η²(mesorregião) da IDADE          = {eta_esp:.1%}")
    print(f"      η²(ato) da IDADE                  = {eta_ato:.1%}")
    print(f"      η²(mesorregião) da separação J/V  = {etaz_esp:.1%}")
    print(f"      within-célula (1−η² região×ato)   = {1 - eta_esp_ato:.1%}")

    # (3) BIMODALIDADE por mesorregião e por célula região×ato
    n_bim = n_tot = 0
    n_bim_cell = n_tot_cell = 0
    for u in ordem:
        g = dnc[dnc["mesorregiao"] == u]
        if g["peso"].sum() < 100:
            continue
        n_tot += 1
        r = bm.avaliar_grupo("U", u, g["idade_pastagem_anos"].to_numpy(float),
                             g["peso"].to_numpy(float))
        n_bim += int(r["bimodal"])
        for ato in ("II", "III"):
            gc = g[g["ato"] == ato]
            if gc["peso"].sum() < 100:
                continue
            n_tot_cell += 1
            rc = bm.avaliar_grupo("C", f"{u}·{ato}", gc["idade_pastagem_anos"].to_numpy(float),
                                  gc["peso"].to_numpy(float))
            n_bim_cell += int(rc["bimodal"])
    print(f"(3) bimodalidade: {n_bim}/{n_tot} mesorregiões | "
          f"{n_bim_cell}/{n_tot_cell} células região×ato")

    return [dict(conjunto=nome, amplitude_sul_norte=amp, eta_espacial_idade=eta_esp,
                 eta_espacial_pvelho=etaz_esp, within_cell=1 - eta_esp_ato,
                 regioes_bimodais=f"{n_bim}/{n_tot}", celulas_bimodais=f"{n_bim_cell}/{n_tot_cell}",
                 **{f"med_{u}": med[u] for u in ordem})]


def main() -> None:
    if not ARQ_DESTINOS.exists():
        sys.exit(f"Falta {ARQ_DESTINOS}. Rode processa_cubo_idade_destinos.py primeiro.")
    print("=" * 78)
    print("Re-checagem do #28C sob a união (D26) — o gradiente e a bimodalidade sobrevivem?")
    print("=" * 78)
    linhas = []
    for nome, dset in CONJUNTOS.items():
        linhas += analisar(preparar(dset), nome)
    pd.DataFrame(linhas).to_csv(ARQ_OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
