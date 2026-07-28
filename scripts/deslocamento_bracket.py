"""
deslocamento_bracket.py — Robustez do #34 à mudança de rótulo do Mosaico (D26)
==============================================================================

PERGUNTA
--------
O #34 é a **manchete da Perna 3**: é ele que testa e refuta a hipótese-mãe (a
lavoura do Sul empurrando pasto/rebanho para o Norte — iLUC intra-estadual). Ele
constrói o regressor a partir de `lulc_agricultura_ha` (Bloco A) e de
`agricultura_delta_mha` (Bloco B) — a classe que a mudança de rótulo do Mosaico
(#28D/D25) esvazia nos anos terminais.

Ao contrário de #33/#40/#49/#28C, o **#34 nunca passou pela varredura** de
23–25/jul/2026: não aparece na tabela do §9 de
`metodologia/tratamento_deriva_mosaico.md`, nem no §5.4 do #28D, e o próprio
`34_deslocamento_espacial.md` não menciona Mosaico/D25/D26. Lacuna encontrada em
28/jul/2026 ao construir a Perna 1 da visualização. Este companheiro a fecha.

DESENHO (Decisão D26 — `metodologia/tratamento_deriva_mosaico.md`)
------------------------------------------------------------------
NÃO se "corrige" com a união. Mede-se o INTERVALO entre réguas e ancora-se numa
fonte imune:

  · `agric`            — a régua do #34 (piso; é a que o rótulo esvazia)
  · `agric ∪ mosaico`  — teto (reabsorve a massa reetiquetada; superconta ILP e
                         o mosaico antigo)
  · `soja SIDRA`       — ÂNCORA IMUNE: área plantada medida em campo pelo IBGE,
                         não passa por classificador (`agri_soja_ha_plantada`)

E acrescenta-se a régua que o #34 já tinha e não sabia que era uma prova:
  · **janela truncada 1985–2019** — a mudança de rótulo começa em 2021. Se os
    vereditos sobrevivem sem a cauda contaminada, a deriva não pode tê-los
    produzido. Para o Bloco A, este é o teste decisivo: são só 4 de ~38
    primeiras diferenças que a deriva toca.

O desenho do #34 já embute uma segunda imunidade que vale explicitar: o
**desfecho** `ΔBovinos_Norte` é PPM/IBGE, também imune ao classificador. Logo
existem células regressor-imune × desfecho-imune.

LEITURA
-------
Robusto ⇔ o veredito (nulo no temporal; θ≤0 no espacial) sobrevive nas três
réguas E na janela truncada. Se `agric` divergir da união/SIDRA, reporta-se o
INTERVALO — nunca um ponto.

ENTRADAS
    data/processed/painel_amc_goias.parquet    (#25)
    data/processed/taxas_lulc_amc.csv          (#25/#17)
    data/processed/amc_crosswalk_goias.csv     (#25)
    data/processed/mapeamento_mesorregioes.csv (#18)
    data/processed/amc_goias.gpkg              (#25)

SAÍDAS
    data/processed/deslocamento_bracket_leadlag.csv
    data/processed/deslocamento_bracket_slx.csv

COMO RODAR
    python scripts/deslocamento_bracket.py

Reusa a maquinaria do #34 (`deslocamento_espacial.py`) por import: mesmo recorte
regional, mesma CCF, mesmo Granger, mesmos pesos direcionais, mesma especificação
de painel. **Não altera o #34.**

Quando foi feito: 2026-07-28.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "scripts"))

from deslocamento_espacial import (  # noqa: E402
    MESO_NORTE,
    MESO_SUL,
    MAX_LAG,
    amc_para_meso,
    ccf_defasada,
    construir_pesos_direcionais,
    granger,
    spatial_lag,
)

ANO_DERIVA = 2020   # a mudança de rótulo é ancorada no calendário: 2021+ (#28D)

# régua -> (rótulo, é imune?)
REGUAS = {
    "agric":       ("Agricultura (MapBiomas)", False),
    "agric_uniao": ("Agricultura ∪ Mosaico",   False),
    "soja_sidra":  ("Soja plantada (SIDRA)",   True),
}


# ---------------------------------------------------------------------------
# 1. Séries regionais sob as três réguas
# ---------------------------------------------------------------------------

def series_regionais_reguas(reg: pd.DataFrame) -> pd.DataFrame:
    """Como `series_regionais` do #34, mas com o regressor em três réguas.

    Os desfechos (pasto/rebanho no Norte) ficam idênticos ao #34 — variar o
    regressor é exatamente o que a D26 pede aqui, porque é ele que carrega a
    classe exposta.
    """
    cols = ["code_amc", "ano", "lulc_agricultura_ha", "lulc_mosaico_usos_ha",
            "agri_soja_ha_plantada", "lulc_pastagem_ha", "pec_bovinos_cab"]
    painel = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")[cols]
    painel = painel.merge(reg[["code_amc", "nm_meso"]], on="code_amc", how="left")

    def regiao(m):
        if m in MESO_SUL:
            return "Sul"
        if m in MESO_NORTE:
            return "Norte"
        return "Centro"

    painel["regiao"] = painel["nm_meso"].map(regiao)

    painel["agric"] = painel["lulc_agricultura_ha"]
    painel["agric_uniao"] = (painel["lulc_agricultura_ha"].fillna(0)
                             + painel["lulc_mosaico_usos_ha"].fillna(0))
    painel["soja_sidra"] = painel["agri_soja_ha_plantada"]

    agg = (painel.groupby(["regiao", "ano"])
           .agg(agric=("agric", lambda s: s.sum(min_count=1) / 1e6),
                agric_uniao=("agric_uniao", lambda s: s.sum(min_count=1) / 1e6),
                soja_sidra=("soja_sidra", lambda s: s.sum(min_count=1) / 1e6),
                pasto_mha=("lulc_pastagem_ha", lambda s: s.sum(min_count=1) / 1e6),
                bovinos_mcab=("pec_bovinos_cab", lambda s: s.sum(min_count=1) / 1e6))
           .reset_index())

    wide = agg.pivot(index="ano", columns="regiao")
    wide.columns = [f"{v}_{r}" for v, r in wide.columns]
    return wide.reset_index()


def rodar_leadlag_bracket(wide: pd.DataFrame) -> pd.DataFrame:
    """Bloco A do #34 sob as três réguas × duas janelas.

    Mantém tudo do original: primeira diferença, CCF até MAX_LAG, Granger com
    maxlag=2 pelo ssr_ftest.
    """
    linhas = []
    desfechos = [("pasto_mha_Norte", "ΔPasto_Norte", False),
                 ("bovinos_mcab_Norte", "ΔBovinos_Norte", True)]

    for janela, corte in [("plena", None), ("truncada 1985–2019", 2019)]:
        df = wide.sort_values("ano").copy()
        if corte is not None:
            df = df[df["ano"] <= corte]

        for regua, (rot_regua, imune_x) in REGUAS.items():
            xcol_nivel = f"{regua}_Sul"
            if xcol_nivel not in df.columns:
                continue
            sub = df[["ano", xcol_nivel] + [c for c, _, _ in desfechos]].copy()
            sub["dx"] = sub[xcol_nivel].diff()
            for ycol, rot_y, imune_y in desfechos:
                sub[f"dy_{ycol}"] = sub[ycol].diff()

            for ycol, rot_y, imune_y in desfechos:
                dd = sub.dropna(subset=["dx", f"dy_{ycol}"])
                if len(dd) < 12:
                    continue
                ccf = ccf_defasada(dd["dx"].to_numpy(),
                                   dd[f"dy_{ycol}"].to_numpy(), MAX_LAG)
                melhor = ccf.loc[ccf["r"].abs().idxmax()]
                for g in granger(dd["dx"], dd[f"dy_{ycol}"], maxlag=2):
                    linhas.append({
                        "janela": janela,
                        "regua": regua,
                        "regua_rotulo": rot_regua,
                        "regressor_imune": imune_x,
                        "desfecho": rot_y,
                        "desfecho_imune": imune_y,
                        "n_dif": len(dd),
                        "ccf_lag_pico": int(melhor["lag"]),
                        "ccf_r_pico": melhor["r"],
                        "granger_lag": g["lag"],
                        "granger_p": g["p_valor"],
                    })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 2. Bloco B — SLX sob as três réguas
# ---------------------------------------------------------------------------

def taxas_reguas() -> pd.DataFrame:
    """Deltas por AMC×ano nas três réguas do regressor.

    `taxas_lulc_amc.csv` já traz `agricultura_delta_mha` e o NÍVEL `mosaico_mha`;
    a soja SIDRA vem do painel. As três entram como Δ em Mha, na mesma unidade
    do #34.
    """
    t = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")[
        ["code_amc", "ano", "agricultura_delta_mha", "pastagem_delta_mha",
         "agricultura_mha", "mosaico_mha"]].sort_values(["code_amc", "ano"])

    t["uniao_mha"] = t["agricultura_mha"] + t["mosaico_mha"].fillna(0)
    t["agric"] = t["agricultura_delta_mha"]
    t["agric_uniao"] = t.groupby("code_amc")["uniao_mha"].diff()

    pan = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")[
        ["code_amc", "ano", "agri_soja_ha_plantada", "pec_bovinos_cab"]
    ].sort_values(["code_amc", "ano"])
    pan["soja_sidra"] = pan.groupby("code_amc")["agri_soja_ha_plantada"].diff() / 1e6
    pan["bovinos_delta_mcab"] = pan.groupby("code_amc")["pec_bovinos_cab"].diff() / 1e6

    return t.merge(pan[["code_amc", "ano", "soja_sidra", "bovinos_delta_mcab"]],
                   on=["code_amc", "ano"], how="left")


def rodar_slx_bracket(reg: pd.DataFrame, pesos: dict, taxas: pd.DataFrame) -> pd.DataFrame:
    """Bloco B do #34 sob as três réguas × duas janelas.

    O termo de vizinhança W·Δagric e o termo local usam a MESMA régua — trocar só
    um dos dois mediria outra coisa.
    """
    from linearmodels.panel import PanelOLS

    codes = pesos["codes"]
    linhas = []

    for janela, corte in [("plena", None), ("truncada 1985–2019", 2019)]:
        base = taxas if corte is None else taxas[taxas["ano"] <= corte]

        for regua, (rot_regua, imune) in REGUAS.items():
            df = base.copy()
            df["x_local"] = df[regua]
            wl_cols = []
            for nome in ("sul", "norte"):
                wl = spatial_lag(df[["code_amc", "ano", "x_local"]].dropna(),
                                 pesos[nome], codes, "x_local", f"Wx_{nome}")
                df = df.merge(wl, on=["code_amc", "ano"], how="left")
                wl_cols.append(f"Wx_{nome}")

            df = df.dropna(subset=["pastagem_delta_mha", "x_local",
                                   "bovinos_delta_mcab", "Wx_sul", "Wx_norte"])
            if len(df) < 200:
                continue
            d = df.set_index(["code_amc", "ano"])

            specs = [
                ("pastagem_delta_mha", ["x_local", "Wx_sul"],   "Δpasto ~ Δx + Wsul·Δx",   False),
                ("pastagem_delta_mha", ["x_local", "Wx_norte"], "Δpasto ~ Δx + Wnorte·Δx (placebo)", False),
                ("bovinos_delta_mcab", ["x_local", "Wx_sul"],   "Δbovinos ~ Δx + Wsul·Δx", True),
            ]
            for y, xs, rotulo, desf_imune in specs:
                res = PanelOLS(d[y], d[xs], entity_effects=True,
                               time_effects=True).fit(cov_type="clustered",
                                                      cluster_entity=True)
                for x in xs:
                    linhas.append({
                        "janela": janela,
                        "regua": regua,
                        "regua_rotulo": rot_regua,
                        "regressor_imune": imune,
                        "modelo": rotulo,
                        "desfecho_imune": desf_imune,
                        "termo": "vizinhanca" if x.startswith("Wx_") else "local",
                        "termo_bruto": x,
                        "beta": round(float(res.params[x]), 5),
                        "se": round(float(res.std_errors[x]), 5),
                        "p": round(float(res.pvalues[x]), 4),
                        "n": int(res.nobs),
                    })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 78)
    print("#34 sob o bracket da D26 — a mudança de rótulo do Mosaico derruba a refutação?")
    print("=" * 78)

    reg = amc_para_meso()
    wide = series_regionais_reguas(reg)

    print("\n[Bloco A] lead-lag: ΔAgric_Sul antecede o Norte? (3 réguas × 2 janelas)")
    ll = rodar_leadlag_bracket(wide)
    ll.to_csv(DIR_PROC / "deslocamento_bracket_leadlag.csv", index=False, encoding="utf-8")

    for janela in ll["janela"].unique():
        print(f"\n  --- janela {janela} ---")
        for (regua, desf), sub in ll[ll.janela == janela].groupby(["regua_rotulo", "desfecho"],
                                                                 sort=False):
            ps = ", ".join(f"lag{int(r.granger_lag)} p={r.granger_p:.3f}"
                           for _, r in sub.iterrows())
            r0 = sub.iloc[0]
            marca = " ◆" if r0.regressor_imune else "  "
            print(f"   {regua:24s}{marca} → {desf:16s} "
                  f"CCF pico lag={r0.ccf_lag_pico:+d} r={r0.ccf_r_pico:+.2f} | {ps}")

    print("\n[Bloco B] SLX espacial: θ do termo de vizinhança ao sul (3 réguas × 2 janelas)")
    pesos = construir_pesos_direcionais(reg, k=8)
    taxas = taxas_reguas()
    slx = rodar_slx_bracket(reg, pesos, taxas)
    slx.to_csv(DIR_PROC / "deslocamento_bracket_slx.csv", index=False, encoding="utf-8")

    viz = slx[slx.termo == "vizinhanca"]
    for janela in viz["janela"].unique():
        print(f"\n  --- janela {janela} ---")
        for _, r in viz[viz.janela == janela].iterrows():
            marca = "◆" if r.regressor_imune else " "
            sig = "*" if r.p < 0.05 else " "
            print(f"   {r.regua_rotulo:24s}{marca} {r.modelo:38s} "
                  f"θ={r.beta:+.4f} (p={r.p:.4f}){sig}  n={r.n}")

    print("\n" + "=" * 78)
    print("Vereditos em Textos/pipelines/34_deslocamento_espacial.md")
    print("=" * 78)


if __name__ == "__main__":
    main()
