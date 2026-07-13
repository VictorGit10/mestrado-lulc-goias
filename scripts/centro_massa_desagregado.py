"""centro_massa_desagregado.py — Pipeline #44
Centro de massa: abrir os lumps + variáveis de controle (extensão do #32)
=========================================================================

PERGUNTA QUE RESPONDE
---------------------
O #32 mediu o deslocamento Sul→Norte de 4 agregados (agricultura, pastagem,
rebanho, veg. natural). Dois desses agregados carregam a narrativa e são
justamente LUMPS heterogêneos. Este pipeline abre os lumps e adiciona
controles, reusando a MESMA máquina do #32 (mean/median center sobre os
centroides das 166 AMCs, EPSG:5880) — não reimplementa nada.

Três sondagens (cada uma com hipótese):

1. SOJA ISOLADA + validação cruzada de fonte.
   "Agricultura" mistura soja + milho + cana + algodão + perenes. A soja é a
   commodity de exportação — o mecanismo do #37 é uma história de câmbio/preço.
   (a) A soja marcha ao norte MAIS que o lump (ancorado ao sul por cana/perenes)?
   (b) O centroide da soja pelo RASTER (MapBiomas, lulc_soja_ha) bate com o da
       SIDRA (área plantada, agri_soja_ha_plantada)? Se colam, é validação
       cruzada raster×estatística — análoga ao #43 (raster×malha), e empresta
       credibilidade ao centroide tabular do rebanho (a única variável que o
       #43 não valida por não ter raster).

2. VEGETAÇÃO NATURAL aberta em 3 formações.
   O "+8 km, quase parada" do #32 é a "muralha norte". Mas o lump mistura mata
   de galeria (floresta nativa — segue rio, imóvel), savana sensu stricto (o
   substrato real da conversão) e campo nativo. Qual formação recua/está presa?

3. LEITE como CONTROLE (placebo sobre o próprio fenômeno).
   O leite é pecuária atada à bacia leiteira consolidada do SUL Goiano. Se o
   boi (corte+leite) sobe e o leite fica ancorado ao sul, é um contraste
   DENTRO da pecuária que separa fronteira de núcleo. Área urbana entra como
   segundo controle (deve ficar parada / puxar p/ Goiânia-Entorno DF).

ABORDAGEM
---------
Reusa cm.carregar_dados / cm.mean_center / cm.median_center /
cm.metros_para_lonlat do Pipeline #32 (centro_massa.py). Idêntico método,
CRS e malha — só muda o conjunto de variáveis.

CAUTELAS (herdadas da minha própria recomendação):
- Só variáveis EXTENSIVAS (ha, cabeças, mil litros) — centro de massa de uma
  razão/taxa não é interpretável.
- Análise DESCRITIVA (deslocamento). NÃO fazemos lead-lag entre latitudes de
  centroides aqui: séries suaves integradas fabricam precedência espúria (D16,
  #42). Precedência exigiria Toda-Yamamoto + placebos.

ENTRADAS
    data/processed/painel_amc_goias.parquet   (#25)
    data/processed/amc_goias.gpkg             (#25)

SAÍDAS
    data/processed/centro_massa_desagregado_anual.csv
    outputs/centro_massa/desagregado_soja.png       (soja raster×SIDRA vs lump)
    outputs/centro_massa/desagregado_vegetacao.png  (3 formações vs lump)
    outputs/centro_massa/desagregado_controle.png   (leite/urbano vs fronteira)

COMO RODAR
    python scripts/centro_massa_desagregado.py
    python scripts/centro_massa_desagregado.py --sem-figuras

Depende de: #32 (centro_massa.py, reuso de máquina) e #25 (painel + geometria).
Quando foi feito: 2026-07-13.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centro_massa as cm  # noqa: E402  — reuso integral da máquina do #32
from config_periodos import ATOS  # noqa: E402

ROOT    = Path(__file__).resolve().parent.parent
DIR_OUT = ROOT / "outputs" / "centro_massa"
DIR_OUT.mkdir(parents=True, exist_ok=True)
ARQ_ANUAL = ROOT / "data" / "processed" / "centro_massa_desagregado_anual.csv"

ANO_INI, ANO_FIM = 1985, 2024

# key -> (coluna no painel, rótulo, cor, grupo-de-figura)
VARS = {
    # --- referências/âncoras (do #32, p/ contexto de latitude) ---
    "agricultura": ("lulc_agricultura_ha", "Agricultura (lump)",      "#c2185b", "soja"),
    "pastagem":    ("lulc_pastagem_ha",    "Pastagem",                "#e8920c", "controle"),
    "bovinos":     ("pec_bovinos_cab",     "Rebanho bovino (total)",  "#7a1f1f", "controle"),
    "veg_natural": ("veg_natural_ha",      "Veg. natural (lump)",     "#2e7d32", "veg"),
    # --- 1. soja isolada + fonte cruzada ---
    "soja_raster": ("lulc_soja_ha",          "Soja — MapBiomas (raster)", "#6a1b9a", "soja"),
    "soja_sidra":  ("agri_soja_ha_plantada", "Soja — SIDRA (área plant.)", "#ab47bc", "soja"),
    # --- 2. vegetação aberta ---
    "floresta":    ("lulc_floresta_nativa_ha",   "Floresta nativa (galeria)", "#1b5e20", "veg"),
    "savanica":    ("lulc_formacao_savanica_ha", "Formação savânica (Cerrado)", "#66bb6a", "veg"),
    "campo_nativo":("lulc_campo_nativo_ha",       "Campo nativo",             "#c5e1a5", "veg"),
    # --- 3. controles ---
    "leite":       ("agri_leite_mil_litros", "Leite (produção)",       "#0277bd", "controle"),
    "area_urbana": ("lulc_area_urbana_ha",   "Área urbana",            "#546e7a", "controle"),
}


def calcular(painel: pd.DataFrame) -> pd.DataFrame:
    """Centro médio + mediano por (variável, ano). Idêntico ao #32, outro conjunto."""
    linhas = []
    for chave, (col, rotulo, _cor, _grp) in VARS.items():
        if col not in painel.columns:
            print(f"[aviso] coluna ausente: {col} ({chave}) — pulando")
            continue
        for ano, g in painel.groupby("ano"):
            sub = g[["cx", "cy", col]].dropna()
            sub = sub[sub[col] > 0]
            if len(sub) < 3:
                continue
            x, y, w = sub["cx"].to_numpy(), sub["cy"].to_numpy(), sub[col].to_numpy(float)
            mx, my = cm.mean_center(x, y, w)
            dx, dy = cm.median_center(x, y, w)
            linhas.append({"variavel": chave, "rotulo": rotulo, "ano": int(ano),
                           "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
                           "n_amc": int(len(sub))})
    df = pd.DataFrame(linhas)
    ll_mean = cm.metros_para_lonlat(df[["x_mean", "y_mean"]].to_numpy())
    ll_med = cm.metros_para_lonlat(df[["x_med", "y_med"]].to_numpy())
    df["lat_mean"], df["lat_med"] = ll_mean[:, 1], ll_med[:, 1]
    df["lon_mean"] = ll_mean[:, 0]
    return df.sort_values(["variavel", "ano"]).reset_index(drop=True)


def resumo(df: pd.DataFrame) -> pd.DataFrame:
    """ΔN líquido (km) 1985→2024 + latitude nos extremos, por variável."""
    out = []
    for chave, (col, rotulo, _c, _g) in VARS.items():
        g = df[df.variavel == chave].set_index("ano")
        if g.empty:
            continue
        a0 = g.index.min()  # soja SIDRA começa 1988
        a1 = g.index.max()
        dn = (g.loc[a1, "y_mean"] - g.loc[a0, "y_mean"]) / 1000
        # ΔN mediano (robusto ao cluster)
        dn_med = (g.loc[a1, "y_med"] - g.loc[a0, "y_med"]) / 1000
        out.append({"variavel": chave, "rotulo": rotulo, "grupo": _g,
                    "ano_ini": int(a0), "ano_fim": int(a1),
                    "lat_ini": g.loc[a0, "lat_mean"], "lat_fim": g.loc[a1, "lat_mean"],
                    "dN_km_mean": dn, "dN_km_med": dn_med})
    return pd.DataFrame(out)


def dn_por_ato(df: pd.DataFrame, chave: str) -> str:
    """ΔN (km) por ato para uma variável — string curta p/ console."""
    g = df[df.variavel == chave].set_index("ano")
    partes = []
    for ato, info in ATOS.items():
        ini, fim = info["inicio"], info["fim"]
        if ini in g.index and fim in g.index:
            dn = (g.loc[fim, "y_mean"] - g.loc[ini, "y_mean"]) / 1000
            partes.append(f"{ato}:{dn:+.0f}")
    return "  ".join(partes)


# ---------------------------------------------------------------------------
# Figuras (estilo do #32: bandas de ato, cor por variável, latitude × ano)
# ---------------------------------------------------------------------------

def _fundo_atos(ax):
    from config_periodos import CORES_ATO
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, info["fim"] + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)
        ax.text((info["inicio"] + info["fim"]) / 2, 0.99, f"Ato {ato}",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=8.5, color="0.45")


def fig_grupo(df: pd.DataFrame, grupo: str, titulo: str, arquivo: str,
              chaves: list[str]) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 6))
    _fundo_atos(ax)
    for chave in chaves:
        col, rotulo, cor, _g = VARS[chave]
        g = df[df.variavel == chave].sort_values("ano")
        if g.empty:
            continue
        estilo = "--" if chave in ("agricultura", "veg_natural") else "-"
        lw = 1.4 if chave in ("agricultura", "veg_natural") else 2.1
        ax.plot(g["ano"], g["lat_mean"], estilo, color=cor, lw=lw,
                label=rotulo, zorder=3)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°, ↑ = mais ao norte)")
    ax.set_title(titulo, fontsize=12, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=8.5, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / arquivo, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / arquivo).relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #44 — centro de massa desagregado + controles")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #44 — Centro de massa: abrir lumps + controles (extensão #32)")
    print("=" * 70)

    painel, _ = cm.carregar_dados()  # reuso: cx/cy + veg_natural_ha idênticos ao #32
    df = calcular(painel)
    df.to_csv(ARQ_ANUAL, index=False, encoding="utf-8")
    print(f"[OK] {ARQ_ANUAL.relative_to(ROOT)} ({len(df)} linhas)\n")

    res = resumo(df)
    print("[resumo] Deslocamento N–S líquido (km; + = norte), latitude nos extremos:")
    print("-" * 70)
    for _, r in res.sort_values("dN_km_mean").iterrows():
        seta = "↑N" if r["dN_km_mean"] > 0 else "↓S"
        print(f"  {r['rotulo']:28s} ΔN {r['dN_km_mean']:+6.1f} km {seta} "
              f"(med {r['dN_km_med']:+6.1f}) | lat {r['lat_ini']:.2f}→{r['lat_fim']:.2f} "
              f"| {r['ano_ini']}–{r['ano_fim']}")

    print("\n[ΔN por ato] (km; I=1985–2000, II=2001–2019, III=2020–2024)")
    for chave in ("agricultura", "soja_raster", "pastagem", "bovinos", "leite",
                  "veg_natural", "savanica", "floresta", "campo_nativo"):
        print(f"  {VARS[chave][1]:28s} {dn_por_ato(df, chave)}")

    # --- Validação cruzada soja: raster × SIDRA ---
    print("\n[soja: raster × SIDRA] concordância de fonte (anos em comum):")
    r = df[df.variavel == "soja_raster"].set_index("ano")["lat_mean"]
    s = df[df.variavel == "soja_sidra"].set_index("ano")["lat_mean"]
    comum = r.index.intersection(s.index)
    corr = np.corrcoef(r.loc[comum], s.loc[comum])[0, 1]
    difmed = float((r.loc[comum] - s.loc[comum]).abs().mean()) * 111  # ° → km
    print(f"  corr(latitude anual) = {corr:.3f} | |Δlat| médio = {difmed:.1f} km "
          f"| n anos = {len(comum)}")

    # --- Gradiente soja vs lump ---
    ag = df[df.variavel == "agricultura"].set_index("ano")["lat_mean"]
    print("\n[soja vs lump agrícola] latitude (° ; soja acima = soja mais ao norte):")
    for ano in (1990, 2000, 2010, 2024):
        if ano in r.index and ano in ag.index:
            print(f"  {ano}: soja(raster) {r.loc[ano]:.2f}  agricultura(lump) {ag.loc[ano]:.2f}  "
                  f"Δ {(r.loc[ano]-ag.loc[ano])*111:+.0f} km")

    # --- Leite vs boi (contraste dentro da pecuária) ---
    le = df[df.variavel == "leite"].set_index("ano")["lat_mean"]
    bo = df[df.variavel == "bovinos"].set_index("ano")["lat_mean"]
    print("\n[leite vs rebanho] latitude (° ; boi acima = corte mais ao norte que leite):")
    for ano in (1985, 2000, 2024):
        if ano in le.index and ano in bo.index:
            print(f"  {ano}: leite {le.loc[ano]:.2f}  rebanho {bo.loc[ano]:.2f}  "
                  f"Δ {(bo.loc[ano]-le.loc[ano])*111:+.0f} km")

    if not args.sem_figuras:
        print()
        fig_grupo(df, "soja",
                  "Soja isolada vs 'agricultura' (lump) — centro de massa, Goiás 1985–2024\n"
                  "roxo = soja (raster e SIDRA); tracejado magenta = agregado agrícola",
                  "desagregado_soja.png",
                  ["agricultura", "soja_raster", "soja_sidra", "pastagem"])
        fig_grupo(df, "veg",
                  "Vegetação natural aberta em formações — centro de massa, Goiás 1985–2024\n"
                  "tracejado verde = lump; savânica = substrato da fronteira; floresta = mata de galeria",
                  "desagregado_vegetacao.png",
                  ["veg_natural", "floresta", "savanica", "campo_nativo", "pastagem"])
        fig_grupo(df, "controle",
                  "Controles: leite e área urbana vs a fronteira — centro de massa, Goiás 1985–2024\n"
                  "se leite/urbano NÃO sobem com pasto/boi, a marcha ao norte é específica da fronteira",
                  "desagregado_controle.png",
                  ["bovinos", "pastagem", "leite", "area_urbana", "agricultura"])

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #44 (extensão desagregada do #32).")
    print("=" * 70)


if __name__ == "__main__":
    main()
