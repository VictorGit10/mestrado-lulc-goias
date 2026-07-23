"""
centro_massa_deriva_check.py — Diagnóstico: a deriva do Mosaico (#28D) entorta o
centro de massa da agricultura (#32/#44)?
=============================================================================

PERGUNTA QUE RESPONDE
---------------------
A D25 mostrou que, no fim da série MapBiomas, a conversão `pasto→agricultura`
migra para a classe 21 ("Mosaico de Usos"). Se a soja nova está sendo rotulada
como Mosaico em vez de Agricultura, o ESTOQUE de agricultura subconta a expansão
recente — e o centro de massa da agricultura (#32) pode estar enviesado. Este
diagnóstico responde três coisas, TODAS só com a Coleção 10.1 (não precisa da 9):

  (A) TEMPO   — o fluxo pasto→21 explode na mesma janela em que pasto→agric
                colapsa? (co-localização temporal; lê deriva_mosaico_transicoes.csv)
  (B) ESPAÇO  — onde está a massa escondida? Centroide do Mosaico e do seu
                CRESCIMENTO 2019→2024 vs. o centroide da agricultura visível.
                E a "coluna-espelho": quanto a agricultura anda para o norte se
                recontarmos com a régua `agricultura ∪ mosaico` (e com soja SIDRA)?
  (C) SIDRA   — o crescimento do Mosaico por AMC bate espacialmente com o
                crescimento da soja SIDRA por AMC? (correlação transversal)

MÉTODO
------
Reusa a matemática validada do #32 (centro_massa.py): mean center ponderado
(Lefever 1926) sobre os centroides das AMC em EPSG:5880, reprojetado para lat/lon.
Nível AMC (Decisão D11): malha constante 1985–2024, sem artefato de emancipação.

LEITURA DA DIREÇÃO DO VIÉS
--------------------------
Latitude menos negativa = mais ao NORTE. Se o centroide da massa escondida
(Mosaico novo) estiver ao NORTE do centroide da agricultura visível, a agricultura
medida está enviesada para o SUL — exatamente o sentido temido. Se estiver colado,
o centro de massa está limpo apesar da deriva (deriva espacialmente ~uniforme).

ENTRADAS
    data/processed/painel_amc_goias.parquet     (#25)
    data/processed/amc_goias.gpkg               (#25, geometria)
    data/processed/deriva_mosaico_transicoes.csv (#28D, para o bloco A)

SAÍDAS
    data/processed/centro_massa_deriva_check.csv       (latitudes por variável×ano)
    data/processed/centro_massa_deriva_resumo.csv      (deslocamentos + centroides-chave)
    outputs/deriva_mosaico/centro_massa_deriva_check.png

COMO RODAR
    python scripts/centro_massa_deriva_check.py

Depende de: #25 (painel + geometria), #32 (funções de centroide), #28D (transições).
Quando foi feito: 2026-07-23.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Reusa a matemática idêntica do #32.
from centro_massa import carregar_dados, mean_center, metros_para_lonlat  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_FIG = ROOT / "outputs" / "deriva_mosaico"
ARQ_TRANS = DIR_PROC / "deriva_mosaico_transicoes.csv"

ANO_A, ANO_B = 2019, 2024   # janela da deriva (borda terminal da Coleção 10.1)

# Variáveis a acompanhar. chave -> (coluna, rótulo, cor).
# 'agric_mais_mosaico' e 'soja_sidra' são as réguas alternativas de destino.
VARS = {
    "agricultura":        ("lulc_agricultura_ha",              "Agricultura (MapBiomas)", "#c2185b"),
    "mosaico":            ("lulc_mosaico_usos_ha",             "Mosaico de Usos",         "#3d7a5a"),
    "agric_mais_mosaico": ("agric_mais_mosaico_ha",            "Agricultura ∪ Mosaico",   "#7b1fa2"),
    "soja_sidra":         ("agri_soja_ha_plantada",            "Soja plantada (SIDRA)",   "#1565c0"),
    "pastagem":           ("lulc_pastagem_ha",                 "Pastagem",                "#e8920c"),
    "bovinos":            ("pec_bovinos_cab",                  "Rebanho (SIDRA)",         "#7a1f1f"),
}


def lat_de(mx: float, my: float) -> float:
    """Latitude (EPSG:4674) de um ponto-centro em EPSG:5880."""
    return float(metros_para_lonlat(np.array([[mx, my]]))[:, 1][0])


def centro_por_ano(painel: pd.DataFrame, col: str) -> pd.DataFrame:
    """Latitude do mean center ponderado por `col`, ano a ano."""
    linhas = []
    for ano, g in painel.groupby("ano"):
        sub = g[["cx", "cy", col]].dropna()
        sub = sub[sub[col] > 0]
        if len(sub) < 3:
            continue
        x, y, w = sub["cx"].to_numpy(), sub["cy"].to_numpy(), sub[col].to_numpy(float)
        mx, my = mean_center(x, y, w)
        linhas.append({"ano": int(ano), "lat_mean": lat_de(mx, my),
                       "peso_total": float(w.sum()), "n_amc": int(len(sub))})
    return pd.DataFrame(linhas)


def centroide_de_pesos(painel_ano: pd.DataFrame, w: np.ndarray) -> float:
    """Latitude do centroide de um vetor de pesos arbitrário (alinhado ao painel_ano)."""
    m = np.isfinite(w) & (w > 0)
    x = painel_ano["cx"].to_numpy()[m]
    y = painel_ano["cy"].to_numpy()[m]
    mx, my = mean_center(x, y, w[m])
    return lat_de(mx, my)


def main() -> None:
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    painel, _ = carregar_dados()
    painel["agric_mais_mosaico_ha"] = (painel["lulc_agricultura_ha"].fillna(0)
                                       + painel["lulc_mosaico_usos_ha"].fillna(0))

    print("\n" + "=" * 78)
    print("(A) TEMPO — o fluxo pasto→21 explode quando pasto→agric colapsa?")
    print("=" * 78)
    if ARQ_TRANS.exists():
        t = pd.read_csv(ARQ_TRANS)
        cols = ["ano", "pct_saida_para_agricultura", "pct_saida_para_mosaico",
                "razao_mosaico_agricultura"]
        show = t[t.ano.isin([2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023, 2024])][cols]
        show = show.rename(columns={"pct_saida_para_agricultura": "%→agric",
                                    "pct_saida_para_mosaico": "%→mosaico",
                                    "razao_mosaico_agricultura": "razão M/A"})
        with pd.option_context("display.float_format", lambda v: f"{v:6.1f}"):
            print(show.to_string(index=False))
        a15 = t.loc[t.ano == 2015, "pct_saida_para_agricultura"].values[0]
        a24 = t.loc[t.ano == 2024, "pct_saida_para_agricultura"].values[0]
        print(f"\n  → das saídas de pastagem, a fração p/ AGRICULTURA cai de "
              f"{a15:.1f}% (2015) para {a24:.1f}% (2024).")
        print(f"  → a razão Mosaico/Agricultura vai de "
              f"{t.loc[t.ano==2015,'razao_mosaico_agricultura'].values[0]:.2f} a "
              f"{t.loc[t.ano==2024,'razao_mosaico_agricultura'].values[0]:.1f}.")
    else:
        print(f"  [aviso] {ARQ_TRANS} ausente — rode scripts/deriva_mosaico_fim_serie.py")

    print("\n" + "=" * 78)
    print("(B) ESPAÇO — centroides e a coluna-espelho (latitude; +norte = menos negativa)")
    print("=" * 78)

    series = {}
    for chave, (col, rot, _cor) in VARS.items():
        s = centro_por_ano(painel, col)
        series[chave] = s
        la = s.loc[s.ano == ANO_A, "lat_mean"]
        lb = s.loc[s.ano == ANO_B, "lat_mean"]
        l0 = s.loc[s.ano == s.ano.min(), "lat_mean"].values[0]
        if len(la) and len(lb):
            dloc_recent = (lb.values[0] - la.values[0]) * 111
            print(f"  {rot:26s}  {ANO_A}={la.values[0]:+.3f}  {ANO_B}={lb.values[0]:+.3f}"
                  f"  Δ{ANO_A}-{ANO_B}={dloc_recent:+5.1f} km"
                  f"  |  Δtotal={ (lb.values[0]-l0)*111:+5.1f} km")

    # Centroide do CRESCIMENTO do mosaico 2019->2024 (onde a massa nova aterrissou).
    piv = painel.pivot_table(index="code_amc", columns="ano",
                             values=["lulc_mosaico_usos_ha", "agri_soja_ha_plantada"],
                             aggfunc="first")
    geo = painel.groupby("code_amc")[["cx", "cy"]].first()
    base = geo.copy()
    base["dmosaico"] = (piv[("lulc_mosaico_usos_ha", ANO_B)].reindex(base.index)
                        - piv[("lulc_mosaico_usos_ha", ANO_A)].reindex(base.index))
    base["dsoja"] = (piv[("agri_soja_ha_plantada", ANO_B)].reindex(base.index).fillna(0)
                     - piv[("agri_soja_ha_plantada", ANO_A)].reindex(base.index).fillna(0))

    lat_cresc_mosaico = centroide_de_pesos(
        base.rename(columns={}).assign(cx=base["cx"], cy=base["cy"]),
        base["dmosaico"].to_numpy())
    lat_agric_A = series["agricultura"].loc[series["agricultura"].ano == ANO_A, "lat_mean"].values[0]
    lat_agric_B = series["agricultura"].loc[series["agricultura"].ano == ANO_B, "lat_mean"].values[0]
    lat_uni_B = series["agric_mais_mosaico"].loc[series["agric_mais_mosaico"].ano == ANO_B, "lat_mean"].values[0]

    print(f"\n  Centroide da agricultura visível  {ANO_B}: {lat_agric_B:+.3f}")
    print(f"  Centroide do CRESCIMENTO do Mosaico {ANO_A}→{ANO_B}: {lat_cresc_mosaico:+.3f}"
          f"  ({'NORTE' if lat_cresc_mosaico > lat_agric_B else 'sul'} da agric. visível, "
          f"Δ={(lat_cresc_mosaico-lat_agric_B)*111:+.1f} km)")
    print(f"  → Coluna-espelho: recontando `agricultura ∪ mosaico`, o centroide {ANO_B} vai de "
          f"{lat_agric_B:+.3f} para {lat_uni_B:+.3f} ({(lat_uni_B-lat_agric_B)*111:+.1f} km ao norte).")

    print("\n" + "=" * 78)
    print(f"(C) SIDRA — o Mosaico novo aterrissa onde a soja SIDRA cresceu? ({ANO_A}→{ANO_B}, por AMC)")
    print("=" * 78)
    cc = base[["dmosaico", "dsoja"]].dropna()
    r_p = cc["dmosaico"].corr(cc["dsoja"], method="pearson")
    r_s = cc["dmosaico"].corr(cc["dsoja"], method="spearman")
    print(f"  n AMCs = {len(cc)}   Pearson r = {r_p:+.3f}   Spearman ρ = {r_s:+.3f}")
    print(f"  (Δmosaico total = {cc['dmosaico'].sum():,.0f} ha ; "
          f"Δsoja SIDRA total = {cc['dsoja'].sum():,.0f} ha)")

    # ---- salvar ----
    long = pd.concat([s.assign(variavel=k, rotulo=VARS[k][1]) for k, s in series.items()],
                     ignore_index=True)
    long.to_csv(DIR_PROC / "centro_massa_deriva_check.csv", index=False)

    resumo = pd.DataFrame([
        {"metrica": "lat_agric_visivel_2024", "valor": lat_agric_B},
        {"metrica": "lat_crescimento_mosaico_2019_2024", "valor": lat_cresc_mosaico},
        {"metrica": "lat_agric_uniao_mosaico_2024", "valor": lat_uni_B},
        {"metrica": "salto_norte_uniao_km", "valor": (lat_uni_B - lat_agric_B) * 111},
        {"metrica": "vies_massa_escondida_km", "valor": (lat_cresc_mosaico - lat_agric_B) * 111},
        {"metrica": "corr_pearson_dmosaico_dsoja", "valor": r_p},
        {"metrica": "corr_spearman_dmosaico_dsoja", "valor": r_s},
    ])
    resumo.to_csv(DIR_PROC / "centro_massa_deriva_resumo.csv", index=False)

    _figura(series, lat_cresc_mosaico)
    print(f"\n[ok] CSVs em {DIR_PROC} | figura em {DIR_FIG/'centro_massa_deriva_check.png'}")


def _figura(series: dict, lat_cresc_mosaico: float) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    ax.axvspan(ANO_A, ANO_B, color="#f2c9c9", alpha=0.35, zorder=0,
               label=f"janela da deriva ({ANO_A}–{ANO_B})")
    for chave in ["agricultura", "agric_mais_mosaico", "soja_sidra", "pastagem", "bovinos"]:
        s = series[chave]
        col, rot, cor = VARS[chave]
        ls = "--" if chave in ("agric_mais_mosaico", "soja_sidra") else "-"
        ax.plot(s.ano, s.lat_mean, ls=ls, lw=2.1, color=cor, label=rot)
    ax.scatter([ANO_B], [lat_cresc_mosaico], marker="*", s=260, color="#3d7a5a",
               edgecolor="k", zorder=5, label="centroide do Mosaico novo")
    ax.set_ylabel("latitude do centro de massa  (↑ = norte)")
    ax.set_xlabel("ano")
    ax.set_title("Deriva do Mosaico e o centro de massa da agricultura (Goiás, AMC)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc="center left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(DIR_FIG / "centro_massa_deriva_check.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
