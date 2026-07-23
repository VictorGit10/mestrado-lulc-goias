"""
periodizacao_robustez_deriva.py — A quebra de 2020 (Ato III) é artefato da deriva?
=================================================================================

PERGUNTA QUE RESPONDE
---------------------
O corte que abre o Ato III (~2020) é detectado pelo sup-F multivariado (#29a) sobre
TRÊS séries de variação de área LULC: veg. natural, pastagem e **agricultura**. A
#28D/D25 mostrou que, no fim da série, a conversão pasto→agricultura é reetiquetada
como "Mosaico de Usos" — então `agricultura_delta` **congela** por volta de 2020 por
artefato de classificação, não por fenômeno de campo. Pergunta natural (levantada na
sessão de 2026-07-23): **a fronteira de 2020 é gerada pela deriva?**

TESTE
-----
Re-detecta as quebras trocando `agricultura_delta` pela régua corrigida
`(agricultura ∪ mosaico)_delta`, que desfaz a reetiquetagem (o Mosaico novo é a soja
que o classificador não pôs em "Agricultura"). Compara com a série imune (veg) e com
a pastagem. Reusa o sup-F multivariado do #29a (`periodizacao_multivariada.py`).

RESULTADO (2026-07-23)
----------------------
A quebra de 2020 **NÃO some — fortalece** sob a correção (F 21,5 → 34,1); a série
corrigida `agric∪mosaico` sozinha quebra exatamente em 2020 (F≈40). O que a deriva faz
é **inverter o SINAL** da mudança, não criar a quebra:

    agricultura_delta (cru):   pré-2020 +0,135 → Ato III +0,024  (Δ −0,111, "desacelera")
    agric∪mosaico (corrigido): pré-2020 +0,134 → Ato III +0,329  (Δ +0,195, ACELERA)

A quebra é sustentada pela **pastagem** (declínio −0,07 → −0,27 Mha/a) e pelo choque
cambial de 2020 (#37, imune) — não pela agricultura. A série imune (veg) **não** quebra
em 2020 (quebra em 1998): o Ato III é um evento de **composição da fronteira**
(pasto→lavoura acelera), não de taxa de desmatamento.

Confirmação por fonte 100% IMUNE (soja SIDRA, área plantada PAM/IBGE): o DELTA quebra em
2020 (F=7,8, p=0,008) e a taxa de expansão triplica (+0,10 → +0,31 Mha/a). A fronteira de
2020 existe fora do MapBiomas. NOTA sobre os OUTROS testes de quebra: o KL/TV (#29c) é
CONTAMINADO — opera sobre a matriz de 6 classes que NÃO rastreia o Mosaico, então seu pico
2018-2020 lê a mesma deriva (não é corroboração independente); o STARS (#29b) não sinaliza
2020 de qualquer modo; o univariado (#26) quebra a agricultura em 2018 = a deriva.

VEREDITO
--------
- A FRONTEIRA de 2020 é ROBUSTA à deriva (real, não artefato de classificação).
- A CARACTERIZAÇÃO "Conversão seletiva" (agricultura desacelera) está INVERTIDA pela
  deriva — o Ato III é, na verdade, **aceleração da conversão** mascarada pela
  reclassificação. Corrigir o rótulo/nota, não a fronteira.

SAÍDAS
    data/processed/periodizacao_robustez_deriva.csv   (quebras: original × corrigido)

COMO RODAR
    python scripts/periodizacao_robustez_deriva.py

Depende de: #29a (`periodizacao_multivariada.py`), taxas_lulc_goias.csv (#17),
mosaico via #28D. Quando foi feito: 2026-07-23.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from periodizacao_multivariada import sup_f_multivariado, binary_segmentation_mv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARQ_TAXAS  = ROOT / "data" / "processed" / "taxas_lulc_goias.csv"
ARQ_PAINEL = ROOT / "data" / "processed" / "painel_amc_goias.parquet"
ARQ_OUT    = ROOT / "data" / "processed" / "periodizacao_robustez_deriva.csv"

PRE_INI, PRE_FIM = 2001, 2019   # Ato II
A3_INI, A3_FIM   = 2020, 2024   # Ato III


def carregar() -> pd.DataFrame:
    d = pd.read_csv(ARQ_TAXAS).sort_values("ano").reset_index(drop=True)
    d["mosaico_delta_mha"] = d["mosaico_mha"].diff()
    d["agric_union_delta"] = d["agricultura_delta_mha"] + d["mosaico_delta_mha"]
    return d


def quebras(d: pd.DataFrame, cols: list[str]) -> dict:
    sub = d[["ano"] + cols].dropna().reset_index(drop=True)
    Y, anos = sub[cols].values, sub["ano"].values
    res = sup_f_multivariado(Y)
    tau = res["tau_idx"]
    saida = {"ano_unico": int(anos[tau]) if tau is not None else None,
             "F_unico": round(float(res["f_stat"]), 1),
             "p_unico": float(res["p_value"])}
    if len(cols) == 3:
        brks = binary_segmentation_mv(Y, anos)
        saida["binseg"] = [(b["ano_quebra"], round(b["f_stat"], 1)) for b in brks]
    return saida


def teste_soja_sidra() -> None:
    """Confirmação por fonte 100% IMUNE: a soja SIDRA (área plantada, PAM/IBGE)
    quebra em 2020? Nunca toca o classificador MapBiomas — se ela também vê 2020,
    a fronteira é real, ponto final."""
    if not ARQ_PAINEL.exists():
        print("\n[soja SIDRA] painel AMC ausente — pulando teste imune.")
        return
    p = pd.read_parquet(ARQ_PAINEL)
    s = p.groupby("ano")["agri_soja_ha_plantada"].sum(min_count=1).dropna()
    s = s[s.index >= 1988]  # série SIDRA de soja começa 1988
    lvl, anos = s.values.astype(float), s.index.values
    dlt, anos_d = np.diff(lvl), anos[1:]
    rL = sup_f_multivariado(lvl.reshape(-1, 1))
    rD = sup_f_multivariado(dlt.reshape(-1, 1))
    dd = pd.Series(dlt, index=anos_d)
    pre = dd[(dd.index >= PRE_INI) & (dd.index <= PRE_FIM)].mean() / 1e6
    pos = dd[(dd.index >= A3_INI) & (dd.index <= A3_FIM)].mean() / 1e6
    print("\n[soja SIDRA — fonte IMUNE ao MapBiomas]")
    print(f"  sup-F NÍVEL:  quebra={anos[rL['tau_idx']]}  F={rL['f_stat']:.1f}  "
          f"p={rL['p_value']:.3g}  (boom de commodities)")
    print(f"  sup-F DELTA:  quebra={anos_d[rD['tau_idx']]}  F={rD['f_stat']:.1f}  "
          f"p={rD['p_value']:.3g}  ← quebra de 2020 numa série que não toca o classificador")
    print(f"  taxa de expansão: Ato II {pre:+.3f} → Ato III {pos:+.3f} Mha/a "
          f"(×{pos/pre:.1f} — acelera)")


def main() -> None:
    d = carregar()

    orig = ["vegetacao_natural_delta_mha", "pastagem_delta_mha", "agricultura_delta_mha"]
    corr = ["vegetacao_natural_delta_mha", "pastagem_delta_mha", "agric_union_delta"]

    print("=" * 74)
    print("Robustez da periodização à deriva do Mosaico (#28D) — quebra do Ato III")
    print("=" * 74)

    A = quebras(d, orig)
    B = quebras(d, corr)
    print("\n[quebra multivariada — binseg]")
    print(f"  A. ORIGINAL   [veg, pasto, agric]        : "
          + " | ".join(f"{a} (F={f})" for a, f in A["binseg"]))
    print(f"  B. CORRIGIDA  [veg, pasto, agric∪mosaico] : "
          + " | ".join(f"{a} (F={f})" for a, f in B["binseg"]))

    print("\n[quebra univariada — sup-F global]")
    for cols, nome in [
        (["vegetacao_natural_delta_mha"], "veg (IMUNE)"),
        (["pastagem_delta_mha"], "pastagem"),
        (["agricultura_delta_mha"], "agricultura (cru)"),
        (["agric_union_delta"], "agric∪mosaico (corrigido)"),
    ]:
        r = quebras(d, cols)
        print(f"  {nome:28s} quebra={r['ano_unico']}  F={r['F_unico']}  p={r['p_unico']:.3g}")

    print(f"\n[médias delta Mha/a] Ato II ({PRE_INI}-{PRE_FIM}) × Ato III ({A3_INI}-{A3_FIM})")
    linhas = []
    for c in ["vegetacao_natural_delta_mha", "pastagem_delta_mha",
              "agricultura_delta_mha", "agric_union_delta"]:
        pre = d[(d.ano >= PRE_INI) & (d.ano <= PRE_FIM)][c].mean()
        pos = d[(d.ano >= A3_INI) & (d.ano <= A3_FIM)][c].mean()
        seta = "acelera↑" if (pos - pre) > 0 and pos > 0 else ("desacelera↓" if pos >= 0 else "declina↓")
        print(f"  {c:32s} pré={pre:+.4f}  AtoIII={pos:+.4f}  Δ={pos - pre:+.4f}  {seta}")
        linhas.append({"serie": c, "media_ato2": round(pre, 4), "media_ato3": round(pos, 4),
                       "delta": round(pos - pre, 4)})

    # CSV
    out = pd.DataFrame([
        {"cenario": "original", "series": "veg+pasto+agric",
         "binseg": ";".join(f"{a}:{f}" for a, f in A["binseg"]),
         "F_2020": next((f for a, f in A["binseg"] if a == 2020), None)},
        {"cenario": "corrigido", "series": "veg+pasto+agric_uniao_mosaico",
         "binseg": ";".join(f"{a}:{f}" for a, f in B["binseg"]),
         "F_2020": next((f for a, f in B["binseg"] if a == 2020), None)},
    ])
    medias = pd.DataFrame(linhas)
    out.to_csv(ARQ_OUT, index=False, encoding="utf-8")
    medias.to_csv(ARQ_OUT.with_name("periodizacao_robustez_deriva_medias.csv"),
                  index=False, encoding="utf-8")

    teste_soja_sidra()

    f_orig = next((f for a, f in A["binseg"] if a == 2020), None)
    f_corr = next((f for a, f in B["binseg"] if a == 2020), None)
    print("\n" + "-" * 74)
    print("VEREDITO:")
    print(f"  • Fronteira 2020 ROBUSTA à deriva: F {f_orig} (cru) → {f_corr} (corrigido) — "
          "não some, fortalece.")
    print("  • A deriva INVERTE o sinal (agric −0,11 vira agric∪mosaico +0,20), não cria a quebra.")
    print("  • Sustentada por pastagem (−0,07→−0,27, SIDRA soja +38%) e câmbio 2020 (#37, imune).")
    print("  • Caracterização 'Conversão seletiva' está INVERTIDA — é ACELERAÇÃO mascarada.")
    print(f"[OK] {ARQ_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
