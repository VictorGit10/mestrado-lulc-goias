"""
Pipeline #46 — A fronteira marcha para terra protegida ou desprotegida?
========================================================================

PERGUNTA QUE RESPONDE
---------------------
O Pipeline #39 mediu o "teto de oferta" de Cerrado convertível explicitamente
SEM camada de proteção ("sem CAR/UC/PRODES") e mostrou que ~62% do convertível
remanescente está na FAIXA NORTE — para onde a marcha ao norte (#32) se dirige.
Este pipeline adiciona a camada que faltava:

    Para onde a fronteira marcha — terra que a lei deixa converter (desprotegida)
    ou terra que deveria estar protegida (UC / prioridade de conservação)?

Se o convertível restante no Norte for majoritariamente DESPROTEGIDO, a "marcha ao
norte" é uma fronteira aberta rumo a Cerrado legalmente conversível; se estiver sob
Unidades de Conservação, a proteção formal é um freio (ou uma pressão de conflito).

ABORDAGEM (overlay vetorial, sobre o painel AMC #25 e o estoque do #39)
-----------------------------------------------------------------------
Bloco A — COBERTURA DE PROTEÇÃO por AMC / região / latitude:
    UCs (geobr/CNUC) recortadas em GO, intersectadas com as 166 AMCs em EPSG:5880
    (equal-area). Distingue PROTEÇÃO INTEGRAL (PI) de USO SUSTENTÁVEL (US) — só a PI
    veda a conversão; a US (ex.: APA) admite uso rural. Terras Indígenas (geobr)
    entram como camada complementar (mas em GO somam ~38 mil ha — negligível).

Bloco B — O "GAP DE PROTEÇÃO" da fronteira: cruza a cobertura de UC por AMC com o
    ESTOQUE CONVERTÍVEL REMANESCENTE do #39 (def. refinada, último ano). Mede que
    fração do Cerrado convertível que resta está DESPROTEGIDA, por região/latitude,
    e se o Norte (destino da marcha) é mais ou menos protegido que o Sul.

Bloco C — TEMPO DA PROTEÇÃO: o `creation_year` das UCs permite perguntar se a
    proteção no Norte ANTECEDEU a fronteira ou chegou depois — proteção tardia não
    freia a conversão já ocorrida. Curva de área protegida acumulada por região.

DECISÃO NOVA — D17 (proteção como malha vetorial)
-------------------------------------------------
"Proteção" = malha de UCs (CNUC via geobr), nível VETORIAL, distinguindo PI de US.
LIMITAÇÃO honesta (no espírito da D13): sem intersecção PIXEL do Cerrado convertível
DENTRO de cada UC, assume-se distribuição uniforme do convertível dentro da AMC ao
aplicar a fração protegida — logo o "convertível desprotegido" é um PROXY/teto, não
uma medida pixel-a-pixel. O refino pixel (recortar o estoque convertível do #39 pela
malha de UC no raster, via GEE) fica para a Sprint 2, junto com duas validações
independentes PENDENTES e com fonte registrada:
  - PRODES Cerrado (INPE/terrabrasilis) — checagem da série de perda de vegetação
    (a API pública de taxas não expõe tabular limpo deste ambiente; baixar de
    http://terrabrasilis.dpi.inpe.br/downloads/ → PRODES Cerrado, incrementos anuais).
  - Áreas Prioritárias para Conservação do Cerrado (MMA, Portaria 223/2016) —
    shapefile em https://www.gov.br/mma/ (dados espaciais) — enriqueceria o Bloco B
    com "prioridade de conservação" além de UC.

ENTRADAS
    data/processed/amc_goias.gpkg                    (#25, geometria das AMC)
    data/processed/fronteira_estoque_convertivel.csv (#39, estoque convertível/AMC/ano)
    geobr.read_conservation_units() + read_indigenous_land() + read_state("GO")

SAÍDAS
    data/processed/protecao_uc_amc.csv        (Bloco A: cobertura UC por AMC)
    data/processed/protecao_gap_regional.csv  (Bloco B: gap por região/latitude)
    data/processed/protecao_temporal.csv      (Bloco C: área protegida acumulada)
    outputs/fronteira_protecao/cobertura_uc.png
    outputs/fronteira_protecao/gap_latitude.png
    outputs/fronteira_protecao/protecao_temporal.png

COMO RODAR
    python scripts/fronteira_protecao.py
    python scripts/fronteira_protecao.py --sem-figuras
    python scripts/fronteira_protecao.py --force   (re-baixa/re-intersecta)

Depende de: #25 (AMC), #39 (estoque convertível). Reusa a geografia Sul/Norte do
#33/#34 e o proxy-com-teto do #39 (D13). Quando foi feito: 2026-07-13.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "fronteira_protecao"
DIR_OUT.mkdir(parents=True, exist_ok=True)

CRS_AREA = 5880   # SIRGAS 2000 / Brazil Albers (equal-area)


# ---------------------------------------------------------------------------
# 1. Bloco A — cobertura de proteção por AMC
# ---------------------------------------------------------------------------

def cobertura_uc(force: bool = False) -> pd.DataFrame:
    """Intersecta UCs (PI/US) e TIs com cada AMC; ha protegidos e fração da AMC."""
    saida = DIR_PROC / "protecao_uc_amc.csv"
    if saida.exists() and not force:
        print(f"[cache] {saida.name}")
        return pd.read_csv(saida)

    import geopandas as gpd
    import geobr

    amc = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(CRS_AREA)
    amc["code_amc"] = amc["code_amc"].astype(int)
    amc["area_amc_ha"] = amc.geometry.area / 1e4

    go = geobr.read_state(code_state="GO").to_crs(CRS_AREA)[["geometry"]]
    uc = geobr.read_conservation_units().to_crs(CRS_AREA)
    uc = gpd.overlay(uc[["group", "category", "creation_year", "geometry"]],
                     go, how="intersection")
    ti = geobr.read_indigenous_land().to_crs(CRS_AREA)
    ti = gpd.overlay(ti[["geometry"]], go, how="intersection")
    ti["group"] = "TI"

    def _inter_ha(camada: "gpd.GeoDataFrame", rotulo: str) -> pd.DataFrame:
        inter = gpd.overlay(amc[["code_amc", "geometry"]], camada, how="intersection")
        inter["ha"] = inter.geometry.area / 1e4
        return (inter.groupby("code_amc")["ha"].sum()
                     .rename(f"ha_{rotulo}").reset_index())

    out = amc[["code_amc", "area_amc_ha"]].copy()
    for grp, rot in [("PI", "uc_pi"), ("US", "uc_us")]:
        sub = uc[uc["group"] == grp]
        if len(sub):
            out = out.merge(_inter_ha(sub, rot), on="code_amc", how="left")
        else:
            out[f"ha_{rot}"] = 0.0
    if len(ti):
        out = out.merge(_inter_ha(ti, "ti"), on="code_amc", how="left")
    else:
        out["ha_ti"] = 0.0

    for c in ["ha_uc_pi", "ha_uc_us", "ha_ti"]:
        out[c] = out[c].fillna(0.0)
    out["ha_protegido_total"] = out["ha_uc_pi"] + out["ha_uc_us"] + out["ha_ti"]
    out["frac_pi"]        = out["ha_uc_pi"] / out["area_amc_ha"]
    out["frac_protegido"] = out["ha_protegido_total"] / out["area_amc_ha"]
    out.to_csv(saida, index=False, encoding="utf-8")
    print(f"[OK] {saida.name} ({len(out)} AMCs) | "
          f"protegido GO: {out.ha_protegido_total.sum()/1e6:.2f} Mha "
          f"(PI {out.ha_uc_pi.sum()/1e6:.2f} + US {out.ha_uc_us.sum()/1e6:.2f} + TI {out.ha_ti.sum()/1e6:.2f})")
    return out


# ---------------------------------------------------------------------------
# 2. Bloco B — gap de proteção vs estoque convertível remanescente (#39)
# ---------------------------------------------------------------------------

def gap_protecao(cob: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cruza cobertura de UC com o estoque convertível remanescente (#39, último
    ano). 'Convertível desprotegido' = estoque × (1 − frac_pi) (proxy-teto, D17:
    só a Proteção Integral veda conversão)."""
    est = pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv")
    ult = int(est["ano"].max())
    est = est[est["ano"] == ult][["code_amc", "regiao", "nm_meso", "lat",
                                   "estoque_refinada_ha"]].copy()
    df = est.merge(cob, on="code_amc", how="left")
    df["conv_desprotegido_ha"] = df["estoque_refinada_ha"] * (1 - df["frac_pi"].fillna(0))
    # AMCs sem estoque convertível (ex.: já esgotado) dariam 0/0 → NaN, não inf
    df["pct_conv_desprotegido"] = (df["conv_desprotegido_ha"]
                                   / df["estoque_refinada_ha"].replace(0, np.nan))

    # faixa de latitude (tercis, como leitura Sul→Norte)
    df["faixa_lat"] = pd.qcut(df["lat"], 3, labels=["Sul", "Centro", "Norte"])

    reg = (df.groupby("regiao").agg(
                n_amc=("code_amc", "size"),
                estoque_conv_Mha=("estoque_refinada_ha", lambda s: s.sum() / 1e6),
                conv_desprotegido_Mha=("conv_desprotegido_ha", lambda s: s.sum() / 1e6),
                frac_pi_media=("frac_pi", "mean"),
                frac_protegido_media=("frac_protegido", "mean"))
           .reset_index())
    reg["pct_conv_desprotegido"] = reg["conv_desprotegido_Mha"] / reg["estoque_conv_Mha"]
    reg["pct_do_convertivel_estadual"] = reg["estoque_conv_Mha"] / reg["estoque_conv_Mha"].sum()

    # correlação entre estoque convertível e proteção, entre AMCs
    corr = df[["estoque_refinada_ha", "frac_pi", "frac_protegido", "lat"]].corr()
    df.attrs["ano"] = ult
    df.attrs["corr_estoque_fracpi"] = round(float(corr.loc["estoque_refinada_ha", "frac_pi"]), 3)
    df.attrs["corr_lat_fracpi"]     = round(float(corr.loc["lat", "frac_pi"]), 3)
    return df, reg


# ---------------------------------------------------------------------------
# 3. Bloco C — tempo da proteção (creation_year vs a fronteira)
# ---------------------------------------------------------------------------

def protecao_temporal(force: bool = False) -> pd.DataFrame:
    """Área de UC criada por ano e acumulada, por grupo (PI/US).
    Responde: a proteção antecedeu ou seguiu a marcha da fronteira?"""
    saida = DIR_PROC / "protecao_temporal.csv"
    if saida.exists() and not force:
        print(f"[cache] {saida.name}")
        return pd.read_csv(saida)

    import geopandas as gpd
    import geobr

    go = geobr.read_state(code_state="GO").to_crs(CRS_AREA)[["geometry"]]
    uc = geobr.read_conservation_units().to_crs(CRS_AREA)
    uc = gpd.overlay(uc[["group", "creation_year", "geometry"]], go, how="intersection")
    uc["ha"] = uc.geometry.area / 1e4
    uc["creation_year"] = pd.to_numeric(uc["creation_year"], errors="coerce")
    uc = uc[(uc["creation_year"].notna()) & (uc["creation_year"] > 1900)]
    uc["creation_year"] = uc["creation_year"].astype(int)

    linhas = []
    for grp in ["PI", "US"]:
        s = (uc[uc["group"] == grp].groupby("creation_year")["ha"].sum()
             .reindex(range(1960, 2025), fill_value=0.0))
        linhas.append(pd.DataFrame({"ano": s.index, "grupo": grp,
                                    "ha_criado": s.values,
                                    "ha_acumulado": s.cumsum().values}))
    out = pd.concat(linhas, ignore_index=True)
    out.to_csv(DIR_PROC / "protecao_temporal.csv", index=False, encoding="utf-8")
    print(f"[OK] protecao_temporal.csv ({len(out)} linhas)")
    return out


# ---------------------------------------------------------------------------
# 4. Figuras
# ---------------------------------------------------------------------------

def fig_cobertura(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    d = df.sort_values("lat")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(d["lat"], d["frac_pi"] * 100, s=30, color="#1b7837", label="Proteção Integral (veda conversão)")
    ax.scatter(d["lat"], d["frac_protegido"] * 100, s=18, color="0.6", alpha=0.7, label="Proteção total (PI+US+TI)")
    ax.set_xlabel("Latitude do centroide da AMC (Sul → Norte →)")
    ax.set_ylabel("% do território da AMC protegido")
    ax.set_title("Cobertura de proteção por AMC ao longo do gradiente Sul→Norte", fontsize=12, loc="left")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.25)
    fig.tight_layout(); fig.savefig(DIR_OUT / "cobertura_uc.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'cobertura_uc.png').relative_to(ROOT)}")


def fig_gap(df: pd.DataFrame, reg: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5))
    # esquerda: estoque convertível por faixa de latitude, empilhando protegido/desprotegido
    faixa = (df.groupby("faixa_lat", observed=True).agg(
                conv=("estoque_refinada_ha", lambda s: s.sum() / 1e6),
                desp=("conv_desprotegido_ha", lambda s: s.sum() / 1e6)).reset_index())
    faixa["prot"] = faixa["conv"] - faixa["desp"]
    x = np.arange(len(faixa))
    ax1.bar(x, faixa["desp"], color="#c44e00", label="convertível DESPROTEGIDO")
    ax1.bar(x, faixa["prot"], bottom=faixa["desp"], color="#1b7837", label="convertível sob Proteção Integral")
    ax1.set_xticks(x); ax1.set_xticklabels(faixa["faixa_lat"])
    ax1.set_ylabel("Cerrado convertível remanescente (Mha)")
    ax1.set_title("Onde resta o convertível — e quanto é desprotegido", fontsize=11, loc="left")
    ax1.legend(fontsize=8.5)
    for i, r in faixa.iterrows():
        if r["conv"] > 0:
            ax1.text(i, r["conv"] + 0.02, f"{100*r['desp']/r['conv']:.0f}% desprot.", ha="center", fontsize=8.5)
    # direita: % desprotegido por região
    r = reg.sort_values("pct_conv_desprotegido")
    ax2.barh(r["regiao"], r["pct_conv_desprotegido"] * 100, color="#c44e00")
    for i, row in enumerate(r.itertuples()):
        ax2.text(row.pct_conv_desprotegido * 100 - 2, i,
                 f"{row.pct_conv_desprotegido*100:.0f}%", va="center", ha="right",
                 color="white", fontsize=9, fontweight="bold")
    ax2.set_xlabel("% do convertível remanescente que está desprotegido")
    ax2.set_title("Gap de proteção por região", fontsize=11, loc="left")
    ax2.set_xlim(0, 100)
    fig.suptitle("A fronteira marcha para terra convertível majoritariamente DESPROTEGIDA",
                 fontsize=12.5, y=1.01)
    fig.tight_layout(); fig.savefig(DIR_OUT / "gap_latitude.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'gap_latitude.png').relative_to(ROOT)}")


def fig_temporal(tmp: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    from config_periodos import ATOS
    fig, ax = plt.subplots(figsize=(10, 5.5))
    cores = {"PI": "#1b7837", "US": "#9bbf85"}
    for grp in ["US", "PI"]:
        s = tmp[tmp.grupo == grp]
        ax.fill_between(s["ano"], 0, s["ha_acumulado"] / 1e6, color=cores[grp], alpha=0.6,
                        label=("Proteção Integral" if grp == "PI" else "Uso Sustentável"))
    for k, v in ATOS.items():
        ax.axvline(v["inicio"], color="0.4", ls=":", lw=1)
        ax.text(v["inicio"] + 0.4, ax.get_ylim()[1] * 0.92, f"Ato {k}", fontsize=8, color="0.3")
    ax.set_xlim(1970, 2024); ax.set_xlabel("Ano"); ax.set_ylabel("Área protegida acumulada em GO (Mha)")
    ax.set_title("Quando a proteção foi criada — vs a marcha da fronteira (atos)", fontsize=12, loc="left")
    ax.legend(fontsize=9, loc="upper left"); ax.grid(True, alpha=0.25)
    fig.tight_layout(); fig.savefig(DIR_OUT / "protecao_temporal.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'protecao_temporal.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #46 — fronteira vs proteção")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-baixa/re-intersecta UCs")
    args = ap.parse_args()
    sys.path.insert(0, str(ROOT / "scripts"))

    print("=" * 72)
    print("Pipeline #46 — A fronteira marcha para terra protegida ou desprotegida?")
    print("=" * 72)

    print("\n[Bloco A] Cobertura de proteção por AMC (UC PI/US + TI):")
    cob = cobertura_uc(force=args.force)
    print(f"  proteção integral média por AMC: {cob.frac_pi.mean()*100:.1f}% | "
          f"proteção total média: {cob.frac_protegido.mean()*100:.1f}%")

    print("\n[Bloco B] Gap de proteção vs estoque convertível remanescente (#39):")
    df, reg = gap_protecao(cob)
    reg.to_csv(DIR_PROC / "protecao_gap_regional.csv", index=False, encoding="utf-8")
    ano = df.attrs["ano"]
    tot_conv = df["estoque_refinada_ha"].sum() / 1e6
    tot_desp = df["conv_desprotegido_ha"].sum() / 1e6
    print(f"  ano de referência do estoque: {ano}")
    print(f"  Cerrado convertível remanescente: {tot_conv:.2f} Mha | "
          f"desprotegido (fora de Proteção Integral): {tot_desp:.2f} Mha "
          f"({100*tot_desp/tot_conv:.0f}%)")
    print(f"  corr(estoque convertível, % Proteção Integral) entre AMCs = {df.attrs['corr_estoque_fracpi']} | "
          f"corr(latitude, % PI) = {df.attrs['corr_lat_fracpi']}")
    print("  por região:")
    for _, r in reg.sort_values("estoque_conv_Mha", ascending=False).iterrows():
        print(f"    {r['regiao']:16s} conv {r['estoque_conv_Mha']:.2f} Mha "
              f"({r['pct_do_convertivel_estadual']*100:4.0f}% do estado) | "
              f"desprotegido {r['pct_conv_desprotegido']*100:3.0f}% | "
              f"PI média {r['frac_pi_media']*100:.1f}%")
    print(f"  [OK] protecao_gap_regional.csv")

    print("\n[Bloco C] Tempo da proteção (creation_year das UCs):")
    tmp = protecao_temporal(force=args.force)
    pi2000 = tmp[(tmp.grupo == "PI") & (tmp.ano == 2000)]["ha_acumulado"].iloc[0]
    pi2024 = tmp[(tmp.grupo == "PI") & (tmp.ano == 2024)]["ha_acumulado"].iloc[0]
    print(f"  Proteção Integral acumulada: {pi2000/1e6:.2f} Mha até 2000 → {pi2024/1e6:.2f} Mha em 2024 "
          f"({100*pi2000/pi2024 if pi2024 else 0:.0f}% já existia em 2000)")

    if not args.sem_figuras:
        print()
        fig_cobertura(df); fig_gap(df, reg); fig_temporal(tmp)

    print("\n" + "=" * 72)
    print("CONCLUÍDO — Pipeline #46. PRODES/MMA = validações pendentes (ver docstring).")
    print("=" * 72)


if __name__ == "__main__":
    main()
