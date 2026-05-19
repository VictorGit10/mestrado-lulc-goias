"""piecewise_did.py — Diferença-em-Diferenças Goiás vs MT/TO (D9)
================================================================

DiD piecewise para avaliar se marcos regulatórios/econômicos tiveram
impacto diferencial em Goiás comparado a Mato Grosso e Tocantins
(controles do bioma Cerrado).

Especificação:
    Δlulc_{st} = α_s + γ_t + β·treated_s × post_t + ε_{st}

Onde:
    s = estado, t = ano
    treated = GO (1), control = MT ou TO (0)
    post = 1 se ano ≥ marco, 0 caso contrário

Janelas: ±5 anos ao redor de cada marco.

Decisão D9: GO vs MT+TO como controles do Cerrado. Fallback: só TO
se MT for muito diferente em composição.

PRÉ-REQUISITO: rodar `python piecewise_did.py --download` com GEE
autenticado para baixar séries UF de MT e TO.

Saídas:
    data/cache/did/mt_uf_lulc.csv   — série UF MT
    data/cache/did/to_uf_lulc.csv   — série UF TO
    outputs/correlacoes/did_resultados.csv — β_did com SE
    outputs/correlacoes/event_study_resultados.csv — β_k por marco
    outputs/correlacoes/placebo_resultados.csv — β em marcos falsos
    outputs/correlacoes/did_*.png   — gráficos DiD
    outputs/correlacoes/event_study_*.png — gráficos event-study

Decisão (2026-05-14): hierarquia de controles passa a ser
[Tocantins, combined, Mato Grosso]. TO é o controle mais
credível (mesmo bioma Cerrado, sem monocultura soja amazônica).
Placebos usam janela ±3 (não ±5) para não contaminar o pré-período
com o marco real.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_CACHE = ROOT / "data" / "cache" / "did"
DIR_OUT = ROOT / "outputs" / "correlacoes"
DIR_CACHE.mkdir(parents=True, exist_ok=True)
DIR_OUT.mkdir(parents=True, exist_ok=True)

# ─────────────────────────── Config ───────────────────────────

# 6 classes (D1)
GRUPOS_LULC = {
    "vegetacao_natural": [3, 4, 12],
    "pastagem":           [15],
    "agricultura":        [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62],
    "agua":               [31, 33],
    "area_urbana":        [24],
    "outros":             [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],
}
MOSAICO_ID = 21

from config_periodos import MARCOS as MARCOS_FULL

# Marcos para DiD (ano do marco + label)
# Nota: 1995 (consolidacao do Real) em vez de 1994 (ano de criacao)
MARCOS = [
    (1995, "Estabilização (Real)"),
    (2003, "Commodity Boom"),
    (2012, "Código Florestal"),
    (2018, "Reorganização de mercado"),
]

# Janela ±5 anos
JANELA = 5

# Janela ±3 para placebo (evita sobrepor com marco real 5 anos depois)
JANELA_PLACEBO = 3

# Defasagem do placebo em relação ao marco real (anos antes)
DEFASAGEM_PLACEBO = 5

# Classes LULC de interesse para DiD
CLASSES_DID = ["vegetacao_natural", "pastagem", "agricultura"]

# Hierarquia de controles — TO primeiro (mesmo bioma Cerrado, sem soja amazônica)
CONTROLES = ["Tocantins", "combined", "Mato Grosso"]

# ─────────────────────────── Download GEE ───────────────────────────

def download_uf_series(uf_code: str, uf_name: str) -> pd.DataFrame:
    """Baixa série anual de área por classe LULC para um estado via GEE."""
    import ee
    import geobr

    GEE_PROJECT = "extreme-height-447417-a9"
    ASSET = ("projects/mapbiomas-public/assets/brazil/lulc/"
             "collection10_1/mapbiomas_brazil_collection10_1_coverage_v1")
    PIXEL_HA = 0.09

    ee.Initialize(project=GEE_PROJECT)
    print(f"GEE inicializado — baixando {uf_name}...")

    # Remap IDs → 1..6
    from_ids, to_ids = [], []
    for idx, (nome, ids) in enumerate(GRUPOS_LULC.items(), start=1):
        for cid in ids:
            from_ids.append(cid)
            to_ids.append(idx)

    # Geometria do estado
    gdf = geobr.read_municipality(code_muni=uf_code, year=2020).to_crs(4326)
    geom_state = gdf.union_all()
    ee_geom = ee.Geometry(geom_state.__geo_interface__)

    # FeatureCollection com 1 feature (estado inteiro)
    state_feature = ee.Feature(ee_geom, {"nm_estado": uf_name})
    state_fc = ee.FeatureCollection([state_feature])

    img = ee.Image(ASSET)

    rows = []
    for ano in range(1985, 2025):
        print(f"  Ano {ano}...", end=" ")
        band = img.select(f"classification_{ano}")
        remapped = band.remap(from_ids, to_ids, defaultValue=0)
        remapped = remapped.updateMask(remapped.gt(0))

        # frequencyHistogram conta pixels por código de classe
        for scale in [30, 60, 100]:
            try:
                stats = remapped.reduceRegions(
                    collection=state_fc,
                    reducer=ee.Reducer.frequencyHistogram(),
                    scale=scale,
                    crs="EPSG:5880",
                ).getInfo()
                if scale > 30:
                    print(f"(scale={scale})", end=" ")
                break
            except Exception as exc:
                if scale == 100:
                    print(f"ERRO: {exc}")
                    stats = None
                    break

        if stats and stats.get("features"):
            histogram = stats["features"][0]["properties"].get("histogram", {})
            grupos_nomes = list(GRUPOS_LULC.keys())
            row = {"ano": ano, "uf": uf_name}
            for code_str, count in histogram.items():
                classe_idx = int(float(code_str))
                area_ha = count * PIXEL_HA
                if 1 <= classe_idx <= len(grupos_nomes):
                    row[grupos_nomes[classe_idx - 1]] = area_ha
            rows.append(row)
            n_classes = len([k for k in row if k not in ['ano', 'uf']])
            print(f"OK ({n_classes} classes)")
        else:
            print("sem dados")

    df = pd.DataFrame(rows)
    # Converter ha → Mha
    for col in GRUPOS_LULC:
        if col in df.columns:
            df[col] = df[col] / 1e6
    return df


# ─────────────────────────── DiD ───────────────────────────

def montar_painel_did() -> pd.DataFrame:
    """Monta painel GO + MT + TO com deltas."""
    # GO
    go = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")
    go_rename = {"ano": "ano"}
    for g in CLASSES_DID:
        go_rename[f"{g}_mha"] = g
    go = go.rename(columns=go_rename)[["ano"] + CLASSES_DID].copy()
    go["uf"] = "Goiás"

    # MT
    mt_path = DIR_CACHE / "mt_uf_lulc.csv"
    if not mt_path.exists():
        print(f"AVISO: {mt_path} não encontrado. Rode com --download primeiro.")
        sys.exit(1)
    mt = pd.read_csv(mt_path)

    # TO
    to_path = DIR_CACHE / "to_uf_lulc.csv"
    if not to_path.exists():
        print(f"AVISO: {to_path} não encontrado. Rode com --download primeiro.")
        sys.exit(1)
    to_df = pd.read_csv(to_path)

    # Padronizar colunas — MT/TO já usam nomes diretos (Mha), GO renomeado acima
    keep = ["ano", "uf"] + CLASSES_DID
    for name, df in [("MT", mt), ("TO", to_df)]:
        missing = [c for c in CLASSES_DID if c not in df.columns]
        if missing:
            print(f"AVISO: {name} sem colunas {missing}")

    panel = pd.concat([go[keep], mt[keep], to_df[keep]], ignore_index=True)

    # Deltas (D7)
    panel = panel.sort_values(["uf", "ano"]).reset_index(drop=True)
    for col in CLASSES_DID:
        panel[f"delta_{col}"] = panel.groupby("uf")[col].diff()

    return panel


def rodar_did(panel: pd.DataFrame, classe: str, marco: int,
             control: str = "combined") -> dict | None:
    """Ajusta DiD para uma classe LULC e um marco."""
    from statsmodels.formula.api import ols

    inicio = marco - JANELA
    fim = marco + JANELA

    sub = panel[
        (panel["ano"] >= inicio) & (panel["ano"] <= fim)
    ].copy()

    if control == "combined":
        sub = sub[sub["uf"].isin(["Goiás", "Mato Grosso", "Tocantins"])]
    else:
        sub = sub[sub["uf"].isin(["Goiás", control])]

    # Verificar janela
    anos_disponiveis = sorted(sub["ano"].unique())
    if len(anos_disponiveis) < 4:
        return None

    sub = sub.dropna(subset=[f"delta_{classe}"])

    if len(sub) < 10:
        return None

    # Variáveis DiD
    sub["treated"] = (sub["uf"] == "Goiás").astype(int)
    sub["post"] = (sub["ano"] >= marco).astype(int)
    sub["treated_post"] = sub["treated"] * sub["post"]

    y = f"delta_{classe}"

    try:
        # DiD com efeitos fixos via fórmula
        model = ols(
            f"{y} ~ treated_post + C(treated) + C(post)",
            data=sub,
        ).fit(cov_type="HC1")

        beta = model.params.get("treated_post", np.nan)
        se = model.bse.get("treated_post", np.nan)
        p = model.pvalues.get("treated_post", np.nan)

        return {
            "classe_lulc": classe,
            "marco_ano": marco,
            "controle": control,
            "janela": f"{inicio}–{fim}",
            "beta_did": round(beta, 4) if not np.isnan(beta) else np.nan,
            "se": round(se, 4) if not np.isnan(se) else np.nan,
            "p": round(p, 4) if not np.isnan(p) else np.nan,
            "n_obs": len(sub),
            "n_uf": sub["uf"].nunique(),
            "r2": round(model.rsquared, 4),
        }
    except Exception as e:
        return {"classe_lulc": classe, "marco_ano": marco, "controle": control,
                "erro": str(e)[:80]}


# ─────────────────────────── Event-study ───────────────────────────

def rodar_event_study(panel: pd.DataFrame, classe: str, marco: int) -> tuple[pd.DataFrame, dict] | None:
    """Event-study: β_k para k em [-5, +5], k=-1 omitido (baseline).

    Especificação (sempre com controle combined = GO + MT + TO):
        Δlulc_{s,t} = α_s + λ_t + Σ_{k≠-1} β_k · D_k(t,s) · treated_s + ε

    Onde D_k(t,s) = 1 se ano-marco = k e s = GO.

    Identificação requer 3 UFs (combined). Com 2 UFs (TO ou MT isolado), os
    `treated × event_time` dummies ficariam ligados a uma única observação cada,
    produzindo SE espúrios ~0. Por isso o event-study é restrito a combined.
    """
    from statsmodels.formula.api import ols

    inicio = marco - JANELA
    fim = marco + JANELA

    sub = panel[(panel["ano"] >= inicio) & (panel["ano"] <= fim)].copy()
    sub = sub[sub["uf"].isin(["Goiás", "Mato Grosso", "Tocantins"])]
    sub = sub.dropna(subset=[f"delta_{classe}"])

    if len(sub) < 20 or sub["uf"].nunique() < 3:
        return None

    sub["event_time"] = sub["ano"] - marco
    sub["treated"] = (sub["uf"] == "Goiás").astype(int)

    # Dummies treated × event_time, omitindo k=-1
    ks = [k for k in range(-JANELA, JANELA + 1) if k != -1]
    for k in ks:
        col = f"tk_m{abs(k)}" if k < 0 else f"tk_p{k}"
        sub[col] = ((sub["event_time"] == k) & (sub["treated"] == 1)).astype(int)

    rhs = "C(uf) + C(ano) + " + " + ".join([
        f"tk_m{abs(k)}" if k < 0 else f"tk_p{k}" for k in ks
    ])
    spec = "uf+year_fe"

    try:
        model = ols(f"delta_{classe} ~ {rhs}", data=sub).fit(cov_type="HC1")
    except Exception as e:
        return None

    rows = []
    for k in range(-JANELA, JANELA + 1):
        if k == -1:
            rows.append({"k": k, "beta": 0.0, "se": 0.0, "p": np.nan,
                         "ci_low": 0.0, "ci_high": 0.0, "is_baseline": True})
            continue
        col = f"tk_m{abs(k)}" if k < 0 else f"tk_p{k}"
        if col in model.params.index:
            b = float(model.params[col])
            se = float(model.bse[col])
            p = float(model.pvalues[col])
            rows.append({
                "k": k, "beta": round(b, 4), "se": round(se, 4),
                "p": round(p, 4),
                "ci_low": round(b - 1.96 * se, 4),
                "ci_high": round(b + 1.96 * se, 4),
                "is_baseline": False,
            })
        else:
            rows.append({"k": k, "beta": np.nan, "se": np.nan, "p": np.nan,
                         "ci_low": np.nan, "ci_high": np.nan, "is_baseline": False})

    es_df = pd.DataFrame(rows)
    meta = {
        "classe_lulc": classe, "marco_ano": marco, "controle": "combined",
        "spec": spec, "n_obs": len(sub), "n_uf": sub["uf"].nunique(),
        "r2": round(model.rsquared, 4),
    }
    return es_df, meta


def plotar_event_study(es_df: pd.DataFrame, meta: dict, label_marco: str) -> Path:
    """Plot β_k com IC 95%. k<0 deve oscilar perto de zero (parallel trends)."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ks = es_df["k"].values
    betas = es_df["beta"].values
    cilo = es_df["ci_low"].values
    cihi = es_df["ci_high"].values

    # Pre e pos com cores diferentes
    mask_pre = ks < 0
    mask_post = ks >= 0
    mask_base = es_df["is_baseline"].values

    # Faixas IC
    ax.fill_between(ks, cilo, cihi, alpha=0.2, color="gray", step="mid")

    # Pontos
    ax.plot(ks[mask_pre & ~mask_base], betas[mask_pre & ~mask_base],
            "o-", color="#3a7ca5", label="Pré-marco", markersize=5)
    ax.plot(ks[mask_post & ~mask_base], betas[mask_post & ~mask_base],
            "o-", color="#c0392b", label="Pós-marco", markersize=5)
    ax.plot(ks[mask_base], betas[mask_base], "o", color="black",
            markersize=7, label="Baseline (k=-1, β≡0)")

    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(-0.5, color="red", linestyle="--", linewidth=1.2)

    ax.set_xlabel(f"Anos relativos ao marco ({label_marco} = {meta['marco_ano']})")
    ax.set_ylabel(f"β_k — Δ {meta['classe_lulc'].replace('_', ' ').title()} (Mha)")
    ax.set_title(
        f"Event-study: {meta['classe_lulc'].replace('_', ' ').title()} × {label_marco} "
        f"(GO vs {meta['controle']}, {meta['spec']}, N={meta['n_obs']})",
        fontsize=10, loc="left"
    )
    ax.legend(fontsize=8, loc="best")
    ax.set_xticks(range(-JANELA, JANELA + 1))

    fig.tight_layout()
    path = DIR_OUT / f"event_study_{meta['classe_lulc']}_{meta['marco_ano']}_{meta['controle'].replace(' ', '')}.png"
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    return path


# ─────────────────────────── Placebo ───────────────────────────

def rodar_placebo(panel: pd.DataFrame, classe: str, marco_real: int,
                  control: str) -> dict | None:
    """DiD em marco falso DEFASAGEM_PLACEBO anos antes do real.

    Usa JANELA_PLACEBO = ±3 (menor) para não sobrepor com marco real.
    Se β_placebo for não-significativo, robustece interpretação causal.
    """
    from statsmodels.formula.api import ols

    marco_falso = marco_real - DEFASAGEM_PLACEBO
    inicio = marco_falso - JANELA_PLACEBO
    fim = marco_falso + JANELA_PLACEBO

    sub = panel[(panel["ano"] >= inicio) & (panel["ano"] <= fim)].copy()

    if control == "combined":
        sub = sub[sub["uf"].isin(["Goiás", "Mato Grosso", "Tocantins"])]
    else:
        sub = sub[sub["uf"].isin(["Goiás", control])]

    sub = sub.dropna(subset=[f"delta_{classe}"])

    if len(sub) < 8:
        return None

    sub["treated"] = (sub["uf"] == "Goiás").astype(int)
    sub["post"] = (sub["ano"] >= marco_falso).astype(int)
    sub["treated_post"] = sub["treated"] * sub["post"]

    y = f"delta_{classe}"

    try:
        model = ols(
            f"{y} ~ treated_post + C(treated) + C(post)",
            data=sub,
        ).fit(cov_type="HC1")

        beta = model.params.get("treated_post", np.nan)
        se = model.bse.get("treated_post", np.nan)
        p = model.pvalues.get("treated_post", np.nan)

        return {
            "classe_lulc": classe,
            "marco_real": marco_real,
            "marco_placebo": marco_falso,
            "controle": control,
            "janela": f"{inicio}–{fim}",
            "beta_placebo": round(float(beta), 4) if not pd.isna(beta) else np.nan,
            "se": round(float(se), 4) if not pd.isna(se) else np.nan,
            "p": round(float(p), 4) if not pd.isna(p) else np.nan,
            "n_obs": len(sub),
            "n_uf": sub["uf"].nunique(),
        }
    except Exception as e:
        return {"classe_lulc": classe, "marco_real": marco_real,
                "marco_placebo": marco_falso, "controle": control,
                "erro": str(e)[:80]}


# ─────────────────────────── Figuras ───────────────────────────

def plotar_did(panel: pd.DataFrame, classe: str, marco: int,
               label_marco: str) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))

    for uf in panel["uf"].unique():
        sub = panel[panel["uf"] == uf].dropna(subset=[f"delta_{classe}"])
        ax.plot(sub["ano"], sub[f"delta_{classe}"], marker="o",
                markersize=3, alpha=0.7, label=uf)

    ax.axvline(marco, color="red", linestyle="--", linewidth=1.5,
               label=f"Marco: {label_marco}")

    inicio = marco - JANELA
    fim = marco + JANELA
    ax.axvspan(inicio, marco - 1, alpha=0.05, color="blue")
    ax.axvspan(marco, fim, alpha=0.05, color="red")

    ax.set_xlabel("Ano")
    ax.set_ylabel(f"Δ {classe.replace('_', ' ').title()} (Mha)")
    ax.set_title(f"DiD: {classe.replace('_', ' ').title()} — {label_marco} ({marco})",
                 fontsize=11, loc="left")
    ax.legend(fontsize=8)
    ax.axhline(0, color="gray", linewidth=0.5)

    fig.tight_layout()
    path = DIR_OUT / f"did_{classe}_{marco}.png"
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    return path


# ─────────────────────────── Main ───────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="DiD Goiás vs MT/TO")
    parser.add_argument("--download", action="store_true",
                        help="Baixar séries MT e TO via GEE")
    args = parser.parse_args()

    if args.download:
        # Baixar MT
        mt_path = DIR_CACHE / "mt_uf_lulc.csv"
        if not mt_path.exists():
            mt = download_uf_series("MT", "Mato Grosso")
            mt.to_csv(mt_path, index=False)
            print(f"OK: {mt_path}")
        else:
            print(f"Já existe: {mt_path}")

        # Baixar TO
        to_path = DIR_CACHE / "to_uf_lulc.csv"
        if not to_path.exists():
            to_df = download_uf_series("TO", "Tocantins")
            to_df.to_csv(to_path, index=False)
            print(f"OK: {to_path}")
        else:
            print(f"Já existe: {to_path}")
        return

    # ── Análise DiD ──
    print("Montando painel GO + MT + TO...")
    panel = montar_painel_did()
    print(f"  {len(panel)} obs ({panel['uf'].unique().tolist()})")

    results = []
    es_rows = []
    placebo_results = []

    for classe in CLASSES_DID:
        for marco, label in MARCOS:
            # DiD principal — TO primeiro (hierarquia D9 revisada)
            for control in CONTROLES:
                print(f"  DiD: {classe} × marco={marco} ctrl={control}...", end=" ")
                res = rodar_did(panel, classe, marco, control)
                if res is None:
                    print("insuficiente")
                    continue
                if "erro" in res:
                    print(f"ERRO: {res['erro']}")
                    results.append(res)
                    continue
                sig = "*" if res["p"] < 0.05 else ""
                beta = res.get("beta_did", np.nan)
                p = res.get("p", np.nan)
                print(f"β={beta:+.4f} p={p:.4f}{sig}")
                results.append(res)

            # Event-study — apenas controle combined (3 UFs, com year FE)
            # TO/MT isolado teria SE espúrios por saturação. Reportado na doc.
            es = rodar_event_study(panel, classe, marco)
            if es is not None:
                es_df, meta = es
                for _, r in es_df.iterrows():
                    es_rows.append({**meta, **r.to_dict()})
                try:
                    path = plotar_event_study(es_df, meta, label)
                    print(f"    Event-study figura: {path.name}")
                except Exception as e:
                    print(f"    Event-study figura erro: {e}")

            # Placebo — todos os controles, marco falso 5 anos antes
            for control in CONTROLES:
                pres = rodar_placebo(panel, classe, marco, control)
                if pres is None or "erro" in pres:
                    continue
                placebo_results.append(pres)

            # Figura DiD principal (combined)
            try:
                path = plotar_did(panel, classe, marco, label)
                print(f"    Figura DiD: {path.name}")
            except Exception as e:
                print(f"    Figura DiD: erro {e}")

    # Salvar DiD principal
    res_df = pd.DataFrame(results)
    if len(res_df) and "controle" in res_df.columns:
        # Reordenar: TO, combined, MT
        order = {"Tocantins": 0, "combined": 1, "Mato Grosso": 2}
        res_df["_order"] = res_df["controle"].map(order)
        res_df = res_df.sort_values(["classe_lulc", "marco_ano", "_order"]).drop(columns="_order")
    out_csv = DIR_OUT / "did_resultados.csv"
    res_df.to_csv(out_csv, index=False)
    print(f"\nOK: {out_csv.name} ({len(res_df)} modelos)")

    # Salvar event-study
    es_full = pd.DataFrame(es_rows)
    out_es = DIR_OUT / "event_study_resultados.csv"
    es_full.to_csv(out_es, index=False)
    print(f"OK: {out_es.name} ({len(es_full)} linhas — {es_full[['classe_lulc','marco_ano','controle']].drop_duplicates().shape[0] if len(es_full) else 0} pares × 11 lags)")

    # Salvar placebo
    pl_df = pd.DataFrame(placebo_results)
    if len(pl_df) and "controle" in pl_df.columns:
        order = {"Tocantins": 0, "combined": 1, "Mato Grosso": 2}
        pl_df["_order"] = pl_df["controle"].map(order)
        pl_df = pl_df.sort_values(["classe_lulc", "marco_real", "_order"]).drop(columns="_order")
    out_pl = DIR_OUT / "placebo_resultados.csv"
    pl_df.to_csv(out_pl, index=False)
    print(f"OK: {out_pl.name} ({len(pl_df)} modelos placebo)")

    # ── Resumos ──
    print("\n=== DiD significativos (p < 0.05), ordem TO → combined → MT ===")
    if len(res_df) > 0 and "p" in res_df.columns:
        sig = res_df[(res_df["p"] < 0.05) & res_df["p"].notna()]
        if len(sig) > 0:
            for _, row in sig.iterrows():
                print(f"  {row['classe_lulc']:20s} × marco {row['marco_ano']} "
                      f"[{row['controle']:12s}] β={row['beta_did']:+.4f} p={row['p']:.4f}")
        else:
            print("  Nenhum DiD significativo.")

    print("\n=== Placebos significativos (p < 0.05) — IDEALMENTE ZERO ===")
    if len(pl_df) > 0 and "p" in pl_df.columns:
        sig_pl = pl_df[(pl_df["p"] < 0.05) & pl_df["p"].notna()]
        if len(sig_pl) > 0:
            print("  [ATENÇÃO] Placebos significativos sugerem que efeito do marco real")
            print("  pode estar capturando dinâmica pré-existente:")
            for _, row in sig_pl.iterrows():
                print(f"    {row['classe_lulc']:20s} marco_real={row['marco_real']} "
                      f"[{row['controle']:12s}] β_placebo={row['beta_placebo']:+.4f} p={row['p']:.4f}")
        else:
            print("  Nenhum placebo significativo — robustece interpretação causal dos marcos reais.")

    print("\n=== Parallel trends (β_k para k<0 com p<0.05) ===")
    if len(es_full) and "p" in es_full.columns:
        pre_sig = es_full[(es_full["k"] < -1) & (es_full["p"] < 0.05) & es_full["p"].notna()]
        if len(pre_sig) > 0:
            print("  [ATENÇÃO] β pré-marco significativos — parallel trends VIOLADA em:")
            for _, row in pre_sig.iterrows():
                print(f"    {row['classe_lulc']:20s} marco={row['marco_ano']} "
                      f"[{row['controle']:12s}] k={int(row['k']):+d} "
                      f"β={row['beta']:+.4f} p={row['p']:.4f}")
        else:
            print("  Nenhum β pré-marco significativo — parallel trends OK em todos os pares.")

    print(f"\nFeito — resultados em {DIR_OUT}")


if __name__ == "__main__":
    main()