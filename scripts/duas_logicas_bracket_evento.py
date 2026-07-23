"""
duas_logicas_bracket_evento.py — o bracket por EVENTO do #40 (fecha a D26)
==========================================================================

Com o cubo reprocessado (`pastagem_conversao_destinos.parquet`, destinos
agricultura E mosaico), fecha o que a truncagem só aproximava: recomputa o
gradiente-manchete do #40 (índice jovem × latitude) e o mix de mecanismos sob
DUAS definições de evento —

  • `pasto→agricultura`        (o #28 original; limite INFERIOR)
  • `pasto→(agric∪mosaico)`    (a pergunta grossa; recaptura a conversão que a
                                deriva reetiquetou como Mosaico)

— em três janelas (limpa ≤2019 / cheia / exposta). Se a UNIÃO estabiliza o
gradiente entre as janelas (ao contrário do agric-só, cuja significância só vinha
da cauda), então o gradiente é real e a deriva o distorcia; se a união também é
fraca/instável, o gradiente nunca foi robusto. É o teste definitivo do #40.

Reusa `duas_logicas_pastagem.classificar_mecanismo` e `.agregar_mix` (mesma regra).

SAÍDA
    data/processed/duas_logicas_bracket_evento.csv

COMO RODAR (depois de processa_cubo_idade_destinos.py)
    python scripts/duas_logicas_bracket_evento.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duas_logicas_pastagem as duas  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARQ_DESTINOS = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"
ARQ_CROSSWALK = ROOT / "data" / "processed" / "amc_crosswalk_goias.csv"
ARQ_MESO = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
ARQ_OUT = ROOT / "data" / "processed" / "duas_logicas_bracket_evento.csv"

JANELAS = {"limpa 2010-2019": (2010, 2019), "cheia 2010-2024": (2010, 2024),
           "exposta 2016-2024": (2016, 2024)}


def preparar(destino_set) -> pd.DataFrame:
    """Carrega os eventos do conjunto de destino escolhido, no schema do #40."""
    df = pd.read_parquet(ARQ_DESTINOS)
    df = df[df["destino"].isin(destino_set)].copy()
    df = df.rename(columns={"n_pixels": "peso", "lat_media": "lat", "lon_media": "lon"})
    df["peso"] = df["peso"].astype("float64")
    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    cw = pd.read_csv(ARQ_CROSSWALK, dtype={"cd_mun": "int64"})[["cd_mun", "code_amc"]]
    meso = pd.read_csv(ARQ_MESO, dtype={"cd_mun": "int64"})[["cd_mun", "nm_meso"]]
    df = df.merge(cw, on="cd_mun", how="left").merge(meso, on="cd_mun", how="left")
    return duas.classificar_mecanismo(df)


def gradiente(df, a, b) -> dict:
    agg = duas.agregar_mix(df, "code_amc", (a, b), duas.MIN_PX_AMC)
    conf = agg[agg.confiavel]
    rho, prho = spearmanr(conf.indice_jovem, conf.lat_centroide)
    r, pr = pearsonr(conf.indice_jovem, conf.lat_centroide)
    sub = df[(df.ano_conversao >= a) & (df.ano_conversao <= b) & (~df.censurado)]
    w = sub["peso"].to_numpy(float); tot = w.sum()
    def q(m): return 100 * w[(sub.mecanismo == m).to_numpy()].sum() / tot
    return dict(n_amc=len(conf), n_Mpx=tot / 1e6, rho=rho, p_rho=prho, r=r,
                pct_rotacao=q("Rotação"), pct_oportunistico=q("Oportunístico clássico"),
                pct_mosaico_origem=q("Mosaico de usos"))


def main() -> None:
    if not ARQ_DESTINOS.exists():
        sys.exit(f"Falta {ARQ_DESTINOS}. Rode processa_cubo_idade_destinos.py primeiro.")

    print("=" * 78)
    print("Bracket por EVENTO do #40 — pasto→agric × pasto→(agric∪mosaico) (D26)")
    print("=" * 78)

    conjuntos = {
        "pasto→agricultura (inferior)": {"agricultura"},
        "pasto→(agric∪mosaico) (grossa)": {"agricultura", "mosaico"},
    }

    linhas = []
    for nome_ev, dset in conjuntos.items():
        df = preparar(dset)
        print(f"\n{'─' * 78}\nEVENTO: {nome_ev}\n{'─' * 78}")
        print(f"  {'janela':20s} {'n(Mpx)':>7s} {'n_AMC':>5s} {'ρ jovem×lat':>12s} {'p':>6s} "
              f"{'Rot%':>6s} {'Opor%':>6s}")
        for jn, (a, b) in JANELAS.items():
            g = gradiente(df, a, b)
            marca = "✓" if g["p_rho"] < 0.05 else "·"
            print(f"  {jn:20s} {g['n_Mpx']:7.2f} {g['n_amc']:5d} "
                  f"{g['rho']:+12.3f} {g['p_rho']:6.3f}{marca} "
                  f"{g['pct_rotacao']:6.1f} {g['pct_oportunistico']:6.1f}")
            linhas.append(dict(evento=nome_ev, janela=jn, **g))

    pd.DataFrame(linhas).to_csv(ARQ_OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")
    print("\nLEITURA: se a UNIÃO dá ρ estável e significativo nas 3 janelas (≠ do agric-só,")
    print("que só era sig. na cauda), o gradiente é REAL e a deriva o distorcia. Se a união")
    print("também é fraca na janela limpa, o gradiente nunca foi robusto.")


if __name__ == "__main__":
    main()
