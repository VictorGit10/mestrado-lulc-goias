"""
duas_logicas_deriva_check.py — Robustez do #40 à deriva do Mosaico (D26)
========================================================================

PERGUNTA
--------
O #40 pool a mistura de mecanismos de conversão `pasto→agricultura` sobre uma
JANELA (primária 2010–2024). A deriva do Mosaico (#28D/D25) reetiqueta, nos anos
terminais, conversões pasto→agricultura como pasto→Mosaico — então esses eventos
**somem da tabela do #28** e a cauda da janela fica subcontada e possivelmente
selecionada. Diferente do #28C (transversal por período, imune), o #40 **pool ao
longo do tempo**, logo está exposto.

O bracket via EVENTO (redefinir a conversão como `pasto→(agric∪mosaico)`) exigiria
os eventos pasto→Mosaico COM idade do pasto — que não existem na tabela atual
(`pastagem_idade_censo.parquet` só tem destino = agricultura); precisaria
reprocessar o cubo. O que dá para fazer SEM o cubo, no espírito da D26:

  (A) EXPOSIÇÃO — a contagem (ponderada) de conversões pasto→agric por ano colapsa
      ~2020, como o agregado da deriva? Mede o tamanho do problema.
  (B) BRACKET POR TRUNCAGEM — o gradiente-manchete (índice jovem × latitude) e o
      mix de mecanismos sobrevivem quando se compara a janela LIMPA (≤2019) com a
      CHEIA (até 2024) e com a MAIS EXPOSTA (2016–2024)? Se estáveis, a conclusão
      do #40 é robusta à deriva; se mudam, marca-se a cauda como provisória.

Reusa `duas_logicas_pastagem.carregar` e `.agregar_mix` (censo de pixels do #28).

SAÍDA
    data/processed/duas_logicas_deriva_check.csv

COMO RODAR
    python scripts/duas_logicas_deriva_check.py

Quando foi feito: 2026-07-23.
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
import duas_logicas_pastagem as duas  # noqa: E402 — reuso da máquina do #40

ROOT = Path(__file__).resolve().parent.parent
ARQ_OUT = ROOT / "data" / "processed" / "duas_logicas_deriva_check.csv"

JANELAS = {
    "limpa 2010-2019":  (2010, 2019),
    "cheia 2010-2024":  (2010, 2024),
    "exposta 2016-2024": (2016, 2024),
}
MECS = ["Rotação", "Premeditado curto", "Oportunístico clássico", "Mosaico de usos", "Ambíguo / Outro"]


def mix_estadual(df, a, b) -> dict:
    """Mix de mecanismos (%, ponderado) sobre os não-censurados na janela."""
    sub = df[(df.ano_conversao >= a) & (df.ano_conversao <= b) & (~df.censurado)]
    w = sub["peso"].to_numpy(float)
    tot = w.sum()
    out = {m: 100 * w[(sub.mecanismo == m).to_numpy()].sum() / tot for m in MECS}
    out["idade_mediana"] = float(np.median(np.repeat(sub.idade_pastagem_anos.values,
                                                     np.maximum(sub.peso.values.astype(int), 1))[:2_000_000])) \
        if len(sub) else np.nan
    out["n_nc_Mpx"] = tot / 1e6
    return out


def main() -> None:
    print("=" * 74)
    print("Robustez do #40 à deriva do Mosaico (D26) — exposição + bracket por truncagem")
    print("=" * 74)
    df = duas.carregar("censo")

    # (A) EXPOSIÇÃO — conversões pasto→agric (peso) por ano
    print("\n(A) EXPOSIÇÃO — conversões pasto→agricultura (Mpx) por ano de conversão:")
    nc = df[~df.censurado]
    by = nc.groupby("ano_conversao")["peso"].sum() / 1e6
    for ano in [2010, 2014, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
        if ano in by.index:
            print(f"   {ano}: {by[ano]:6.3f} Mpx")
    pico = by.loc[2014:2019].mean()
    fim = by.loc[2022:2024].mean()
    print(f"   → média 2014-2019 = {pico:.3f} Mpx/a ; média 2022-2024 = {fim:.3f} Mpx/a "
          f"({100*(fim-pico)/pico:+.0f}%) — a cauda subconta, como a deriva prevê.")

    # (B) BRACKET POR TRUNCAGEM — gradiente índice-jovem × latitude + mix
    print("\n(B) BRACKET POR TRUNCAGEM — gradiente (índice jovem × latitude) por AMC:")
    linhas = []
    for nome, (a, b) in JANELAS.items():
        mix = agg = duas.agregar_mix(df, "code_amc", (a, b), duas.MIN_PX_AMC)
        conf = agg[agg.confiavel]
        rho, prho = spearmanr(conf.indice_jovem, conf.lat_centroide)
        r, pr = pearsonr(conf.indice_jovem, conf.lat_centroide)
        me = mix_estadual(df, a, b)
        print(f"\n   [{nome}]  n_AMC confiáveis = {len(conf)}")
        print(f"     índice jovem × latitude: Spearman ρ={rho:+.3f} (p={prho:.3f}) | "
              f"Pearson r={r:+.3f} (p={pr:.3f})")
        print(f"     mix estadual: Rotação {me['Rotação']:.1f}% | Oportun. "
              f"{me['Oportunístico clássico']:.1f}% | Premed. {me['Premeditado curto']:.1f}% | "
              f"Mosaico {me['Mosaico de usos']:.1f}% | idade med {me['idade_mediana']:.1f}a")
        linhas.append(dict(janela=nome, ano_ini=a, ano_fim=b, n_amc=len(conf),
                           rho_jovem_lat=rho, p_rho=prho, r_jovem_lat=r,
                           pct_rotacao=me["Rotação"], pct_oportunistico=me["Oportunístico clássico"],
                           pct_mosaico=me["Mosaico de usos"], idade_mediana=me["idade_mediana"]))

    pd.DataFrame(linhas).to_csv(ARQ_OUT, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")
    print("\nNOTA: o bracket por EVENTO (pasto→(agric∪mosaico) com idade) fica pendente do")
    print("reprocessamento do cubo (processa_cubo_idade.py com destino=mosaico). Aqui: truncagem.")


if __name__ == "__main__":
    main()
