"""
painel_espacial_dinamico_deriva.py — Robustez do #49 à deriva do Mosaico (D26)
==============================================================================

PERGUNTA
--------
Os canais inferenciais do #49 (painel espacial dinâmico) usam `agricultura_delta`,
que a deriva do Mosaico (#28D/D25) distorce nos anos terminais. Este companheiro
re-estima os dois modelos expostos no formato **SIDRA-âncora + bracket** (Decisão
D26, `metodologia/tratamento_deriva_mosaico.md`): NÃO "corrige" com a união — mede
o INTERVALO entre as réguas e ancora na SIDRA (imune).

- M1 (intensificação, Δagric ~ ΔVA): varia o REGRESSANDO em 3 réguas
    agric (limite inferior) · agric∪mosaico (superior) · soja SIDRA (âncora imune)
  + janela plena (2003–2021) × truncada (2003–2019, sem a cauda da deriva).
- M3 (substituição local, Δpasto ~ Δagric): varia o REGRESSOR nas mesmas 3 réguas
  (y = pastagem, largamente real) + janela 1988–2024 × 1988–2019.
- M2 (Δpasto ~ ΔSICOR + ΔVA): regressores imunes → não re-rodado aqui (só nota).

LEITURA (D26): conclusão robusta ⇔ sinal/significância do β sobrevivem nas 3 réguas
E na janela truncada. Se o β de `agric` (inferior) diverge da união/SIDRA, a deriva
estava atenuando/distorcendo o coeficiente — reporta-se o INTERVALO, não um ponto.
A união é TETO (superconta ILP+mosaico antigo); a âncora é a SIDRA.

Reusa a máquina de estimação do #49 (`painel_espacial_dinamico.py`): mesmo 2-way
within, mesmo Elhorst FE lag/error, mesma escolha por LM. Não altera o #49.

SAÍDA
    data/processed/painel_espacial_dinamico_deriva.csv

COMO RODAR
    python scripts/painel_espacial_dinamico_deriva.py

Quando foi feito: 2026-07-23.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import painel_espacial_dinamico as pe  # noqa: E402 — reuso integral da máquina do #49

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"

# Réguas de destino agrícola (D26). chave -> (coluna, rótulo, papel).
RULERS = {
    "agric":   ("agricultura_delta_mha", "Agricultura (MapBiomas)", "inferior"),
    "uniao":   ("agric_uniao_delta",     "Agricultura ∪ Mosaico",   "superior (teto)"),
    "sidra":   ("soja_sidra_delta_mha",  "Soja plantada (SIDRA)",   "ÂNCORA imune"),
}


def carregar_dados_deriva() -> pd.DataFrame:
    """Igual ao #49, + mosaico_delta, agric∪mosaico e soja SIDRA (Δ, Mha) por AMC."""
    tx = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")
    tx["code_amc"] = tx["code_amc"].astype(int)
    tx = tx.sort_values(["code_amc", "ano"])
    # delta do mosaico e régua da união (delta da soma = soma dos deltas)
    tx["mosaico_delta_mha"] = tx.groupby("code_amc")["mosaico_mha"].diff()
    tx["agric_uniao_delta"] = tx["agricultura_delta_mha"] + tx["mosaico_delta_mha"]

    soc = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")
    soc["code_amc"] = soc["code_amc"].astype(int)
    soc = soc.sort_values(["code_amc", "ano"])
    soc["delta_va_agro_real_rs"] = soc.groupby("code_amc")["va_agro_real_rs"].diff() / 1e9
    soc["soja_sidra_mha"] = soc["agri_soja_ha_plantada"] / 1e6
    soc["soja_sidra_delta_mha"] = soc.groupby("code_amc")["soja_sidra_mha"].diff()

    keep = ["code_amc", "ano", "delta_va_agro_real_rs", "soja_sidra_delta_mha"]
    return tx.merge(soc[keep], on=["code_amc", "ano"], how="left")


def _amcs_comuns(df, cols, anos) -> set[int]:
    """AMCs com TODOS os `cols` não-NaN em TODOS os anos da janela (amostra comum
    → β's das réguas ficam sobre exatamente o mesmo painel, sem confundir amostra)."""
    d = df[df["ano"].isin(anos)][["code_amc", "ano"] + cols].dropna(subset=cols)
    cont = d.groupby("code_amc")["ano"].nunique()
    return set(cont[cont == len(anos)].index)


def rodar_bracket(df, gdf, modelo_id, reguas, y_por_regua, x_fixo, janelas,
                  amostra_comum=True) -> list[dict]:
    """Roda pe.rodar_modelo para cada (régua × janela). `y_por_regua`: a régua varia
    o REGRESSANDO (senão o regressor). `amostra_comum`: força as mesmas AMCs nas
    réguas da mesma janela (intersecção das completas)."""
    linhas = []
    for jnome, anos in janelas.items():
        # colunas necessárias por TODAS as réguas escolhidas + lado fixo
        cols_reguas = [RULERS[k][0] for k in reguas]
        fixas = ([x_fixo["y"]] if not y_por_regua else []) + (x_fixo["x"] or [])
        comuns = _amcs_comuns(df, cols_reguas + fixas, anos) if amostra_comum else None
        for chave in reguas:
            col, rot, papel = RULERS[chave]
            y = col if y_por_regua else x_fixo["y"]
            x = [col] if not y_por_regua else x_fixo["x"]
            dfx = df[df["code_amc"].isin(comuns)] if comuns is not None else df
            m = dict(id=modelo_id, nome=rot, y=y, x=x, anos=anos, Ws=["queen"])
            try:
                r = pe.rodar_modelo(dfx, gdf, m)[0]
            except Exception as e:
                print(f"  [{modelo_id} {chave} {jnome}] falhou: {e!r}")
                continue
            linhas.append(dict(
                modelo=modelo_id, regua=chave, rotulo=rot, papel=papel, janela=jnome,
                N=r["N"], T=r["T"], var=r["var"],
                beta_ols=r["beta_ols"], p_ols=r["p_ols"],
                beta_esp=(r["beta_lag"] if r["forma_preferida"] == "lag" else r["beta_err"]),
                p_esp=(r["p_lag"] if r["forma_preferida"] == "lag" else r["p_err"]),
                forma=r["forma_preferida"], rho=r["rho"], lam=r["lam"],
                sobrevive=r["sobrevive"]))
    return linhas


def imprimir(linhas, titulo, unidade):
    print(f"\n{'='*78}\n{titulo}\n{'='*78}")
    print(f"  {'régua':26s} {'janela':12s} {'N':>4s} {'β_OLS':>9s} {'p':>6s} "
          f"{'β_espac':>9s} {'p':>6s}  forma  sobrev")
    for r in linhas:
        marca = "✓" if r["sobrevive"] else "·"
        print(f"  {r['rotulo']:26s} {r['janela']:12s} {r['N']:>4d} "
              f"{r['beta_ols']:+9.4f} {r['p_ols']:6.3f} "
              f"{r['beta_esp']:+9.4f} {r['p_esp']:6.3f}  {r['forma']:5s}  {marca}")
    print(f"  (β em Δpasto por unidade de Δ{unidade}; espac = forma espacial preferida por LM)")


def main() -> None:
    print("=" * 78)
    print("Robustez do #49 à deriva do Mosaico — SIDRA-âncora + bracket (D26)")
    print("=" * 78)
    df = carregar_dados_deriva()
    gdf = pe.carregar_geom()

    tres = ["agric", "uniao", "sidra"]

    # M1: Δ(destino agrícola) ~ ΔVA agro — varia o REGRESSANDO; amostra comum (91 AMCs)
    m1 = rodar_bracket(
        df, gdf, "M1", reguas=tres, y_por_regua=True,
        x_fixo=dict(y=None, x=["delta_va_agro_real_rs"]),
        janelas={"2003-2021": list(range(2003, 2022)),
                 "2003-2019": list(range(2003, 2020))})

    # M3 bracket moderno: Δpasto ~ Δ(destino) — 3 réguas, amostra comum, janela viável p/ SIDRA
    m3 = rodar_bracket(
        df, gdf, "M3", reguas=tres, y_por_regua=False,
        x_fixo=dict(y="pastagem_delta_mha", x=None),
        janelas={"2003-2024": list(range(2003, 2025)),
                 "2003-2019": list(range(2003, 2020))})

    # M3 continuidade (janela nativa do #49, 166 AMCs): só agric × união (SIDRA inviável p/ 1988+)
    m3_longo = rodar_bracket(
        df, gdf, "M3", reguas=["agric", "uniao"], y_por_regua=False,
        x_fixo=dict(y="pastagem_delta_mha", x=None),
        janelas={"1988-2024": list(range(1988, 2025)),
                 "1988-2019": list(range(1988, 2020))})

    imprimir(m1, "M1 — Intensificação: Δ(destino) ~ ΔVA agro (regressando varia; amostra comum)", "VA agro")
    imprimir(m3, "M3 — Substituição: Δpasto ~ Δ(destino) — bracket moderno 3 réguas (amostra comum)", "destino")
    imprimir(m3_longo, "M3 — continuidade janela nativa #49 (166 AMCs; agric × união)", "destino")

    res = pd.DataFrame(m1 + m3 + m3_longo)
    saida = DIR_PROC / "painel_espacial_dinamico_deriva.csv"
    res.to_csv(saida, index=False, encoding="utf-8")
    print(f"\n[OK] {saida.relative_to(ROOT)} ({len(res)} linhas)")
    print("\nM2 (Δpasto ~ ΔSICOR + ΔVA): regressores imunes (BCB/IBGE) — não re-rodado.")


if __name__ == "__main__":
    main()
