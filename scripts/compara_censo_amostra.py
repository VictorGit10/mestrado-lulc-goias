"""compara_censo_amostra.py — Pipeline #28 (validação)

Confronta o censo de pixels (`pastagem_idade_censo.parquet`) com a amostra
corrigida do #28A (`pastagem_idade_conversao.csv`, filtrada a `cd_mun != 0`).

## O que esta comparação responde — e o que ela NÃO responde

A pergunta útil é: **a amostra corrigida era representativa de Goiás?** Se sim,
os resultados publicados do #28 sobrevivem ao censo com números um pouco mais
precisos. Se não, o filtro `cd_mun != 0` foi paliativo e o censo muda leituras.

Mas amostra e censo diferem por DUAS causas independentes, e o agregado as
confunde:

  (a) **erro amostral** — 2.000 px/ano é uma amostra pequena do universo;
  (b) **ponderação entre anos** — a amostra do #28A tinha 2.000 px/ano no
      ENVELOPE, e a fatia que caía em GO variava de 32,8% a 79,1%, *caindo ao
      longo do tempo* (MATOPIBA cresceu mais rápido que GO). Depois do filtro,
      cada ano contribui com 2.000 × fatia_GO(ano), não com peso igual nem com
      peso proporcional à área convertida.

Por isso a comparação é feita em dois níveis:

  1. **Por ano** — isola (a). Se as distribuições anuais batem, a amostragem
     dentro de cada ano era sadia.
  2. **Agregada** — expõe (b). Se o passo 1 bate mas este não, a diferença é
     inteiramente artefato de ponderação, não de amostragem.

Um viés que esta comparação NÃO detecta: qualquer coisa que afete censo e
amostra igualmente (ex.: erro de classificação do próprio MapBiomas). O censo
elimina erro amostral, não erro de medida.

## A amostra é corrigida aqui antes de comparar

O CSV do #28A carrega o bug da classe 21 (Mosaico de Usos ausente do GRUPO_MAP
→ rotulada `censurado_esquerda` via `.fillna()`). Comparar sem consertar isso
mediria o bug, não a representatividade. O relabel é aplicado em memória; o CSV
não é tocado.

Como rodar:
    python scripts/compara_censo_amostra.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

# Reusa o módulo verificado do #28 (contrato D24): com peso=1 reduz exatamente a
# numpy/sklearn. Antes a comparação reimplementava a mediana em convenção step
# (searchsorted sobre cumsum), que diverge em até 1 ano da convenção linear que
# o resto do #28 usa — inofensivo só porque os dois lados da comparação usavam a
# mesma convenção, mas quebraria se alguém copiasse a métrica para outro lugar.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from estatistica_ponderada import mediana as mediana_ponderada, quantil as quantil_ponderado

ROOT = Path(__file__).resolve().parent.parent
CENSO = ROOT / "data" / "processed" / "pastagem_idade_censo.parquet"
AMOSTRA = ROOT / "data" / "processed" / "pastagem_idade_conversao.csv"

ATOS = [("I", 1985, 2000), ("II", 2001, 2019), ("III", 2020, 2024)]


def carregar_amostra() -> pd.DataFrame:
    df = pd.read_csv(AMOSTRA, dtype={"cd_mun": "int64"})
    df = df[df["cd_mun"] != 0].copy()
    # Conserta o bug da classe 21 antes de comparar (ver docstring)
    m21 = df["classe_antes_id"] == 21
    df.loc[m21, "origem_anterior"] = "mosaico"
    print(f"  amostra: {len(df):,} px em GO | relabel classe 21: {int(m21.sum()):,}")
    df["peso"] = 1.0
    return df


def carregar_censo() -> pd.DataFrame:
    df = pd.read_parquet(CENSO)
    df = df.rename(columns={"n_pixels": "peso"})
    print(f"  censo:   {df.peso.sum():,.0f} eventos | {len(df):,} células")
    return df


def resumo(df: pd.DataFrame, col_peso: str = "peso") -> dict:
    nc = df[df.origem_anterior != "censurado_esquerda"]
    p = df[col_peso].to_numpy(float)
    return {
        "n": df[col_peso].sum(),
        "cens_%": df.loc[df.origem_anterior == "censurado_esquerda", col_peso].sum() / p.sum() * 100,
        "med_nc": mediana_ponderada(nc.idade_pastagem_anos.to_numpy(),
                                    nc[col_peso].to_numpy(float)) if len(nc) else np.nan,
        "p90_nc": quantil_ponderado(nc.idade_pastagem_anos.to_numpy(),
                                    nc[col_peso].to_numpy(float), 0.90) if len(nc) else np.nan,
    }


def main() -> None:
    if not CENSO.exists():
        sys.exit(f"Censo não encontrado: {CENSO}\nRode primeiro: processa_cubo_idade.py")
    print("Carregando...")
    amo, cen = carregar_amostra(), carregar_censo()

    # ---- 1. Por ano: isola erro amostral ----
    print(f"\n{'=' * 74}\n1. POR ANO (isola erro amostral)\n{'=' * 74}")
    print(f"{'ano':>5} {'n_amo':>7} {'n_censo':>10} | {'cens% amo':>9} {'cens% cen':>9} | "
          f"{'med amo':>7} {'med cen':>7} {'dif':>5}")
    difs_med, difs_cens = [], []
    for ano in sorted(cen.ano_conversao.unique()):
        a, c = amo[amo.ano_conversao == ano], cen[cen.ano_conversao == ano]
        if not len(a) or not len(c):
            continue
        ra, rc = resumo(a), resumo(c)
        d = ra["med_nc"] - rc["med_nc"]
        difs_med.append(d)
        difs_cens.append(ra["cens_%"] - rc["cens_%"])
        print(f"{ano:>5} {ra['n']:>7,.0f} {rc['n']:>10,.0f} | {ra['cens_%']:>8.1f}% "
              f"{rc['cens_%']:>8.1f}% | {ra['med_nc']:>7.0f} {rc['med_nc']:>7.0f} {d:>5.0f}")

    dm = np.array(difs_med, float)
    dc = np.array(difs_cens, float)
    print(f"\n  diferença de mediana (amostra − censo): média {np.nanmean(dm):+.2f}a | "
          f"mediana {np.nanmedian(dm):+.1f}a | máx |{np.nanmax(np.abs(dm)):.0f}|a")
    print(f"  diferença de censura:                   média {np.nanmean(dc):+.2f} pp | "
          f"máx |{np.nanmax(np.abs(dc)):.1f}| pp")
    if np.nanmean(np.abs(dm)) < 1.5:
        print("  -> amostragem DENTRO de cada ano parece sadia")
    else:
        print("  -> amostragem enviesada mesmo dentro do ano; investigar")

    # ---- 2. Agregada: expõe a ponderação entre anos ----
    print(f"\n{'=' * 74}\n2. AGREGADA POR ATO (expõe ponderação entre anos)\n{'=' * 74}")
    print(f"{'ato':>5} | {'n amo':>8} {'n censo':>11} | {'cens% amo':>9} {'cens% cen':>9} | "
          f"{'med amo':>7} {'med cen':>7}")
    for nome, y0, y1 in ATOS:
        a = amo[amo.ano_conversao.between(y0, y1)]
        c = cen[cen.ano_conversao.between(y0, y1)]
        if not len(a) or not len(c):
            continue
        ra, rc = resumo(a), resumo(c)
        print(f"{nome:>5} | {ra['n']:>8,.0f} {rc['n']:>11,.0f} | {ra['cens_%']:>8.1f}% "
              f"{rc['cens_%']:>8.1f}% | {ra['med_nc']:>7.0f} {rc['med_nc']:>7.0f}")

    # ---- 3. Origem anterior ----
    print(f"\n{'=' * 74}\n3. ORIGEM ANTERIOR (% do total)\n{'=' * 74}")
    pa = amo.groupby("origem_anterior")["peso"].sum()
    pc = cen.groupby("origem_anterior")["peso"].sum()
    comp = pd.DataFrame({"amostra_%": pa / pa.sum() * 100, "censo_%": pc / pc.sum() * 100})
    comp["dif_pp"] = comp["amostra_%"] - comp["censo_%"]
    print(comp.round(2).sort_values("censo_%", ascending=False).to_string())

    # ---- 4. Granularidade municipal ----
    print(f"\n{'=' * 74}\n4. GRANULARIDADE MUNICIPAL (não-censurados)\n{'=' * 74}")
    anc = amo[amo.origem_anterior != "censurado_esquerda"]
    cnc = cen[cen.origem_anterior != "censurado_esquerda"]
    ca = anc.groupby("cd_mun").size()
    cc = cnc.groupby("cd_mun")["peso"].sum()
    print(f"  amostra: {len(ca)} munis | mediana {ca.median():,.0f} px | "
          f"<20 px: {(ca < 20).sum()} ({(ca < 20).mean() * 100:.0f}%)")
    print(f"  censo:   {len(cc)} munis | mediana {cc.median():,.0f} px | "
          f"<20 px: {(cc < 20).sum()} ({(cc < 20).mean() * 100:.0f}%)")


if __name__ == "__main__":
    main()
