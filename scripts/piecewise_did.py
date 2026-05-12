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
    outputs/correlacoes/did_*.png   — gráficos
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

# Marcos para DiD (ano do marco + label)
MARCOS = [
    (1995, "Estabilização (Real)"),
    (2003, "Commodity Boom"),
    (2012, "Código Florestal"),
    (2018, "PAC Cerrado"),
]

# Janela ±5 anos
JANELA = 5

# Classes LULC de interesse para DiD
CLASSES_DID = ["vegetacao_natural", "pastagem", "agricultura"]

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

    for classe in CLASSES_DID:
        for marco, label in MARCOS:
            for control in ["combined", "Mato Grosso", "Tocantins"]:
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

            # Figura (só combined)
            try:
                path = plotar_did(panel, classe, marco, label)
                print(f"    Figura: {path.name}")
            except Exception as e:
                print(f"    Figura: erro {e}")

    # Salvar
    res_df = pd.DataFrame(results)
    out_csv = DIR_OUT / "did_resultados.csv"
    res_df.to_csv(out_csv, index=False)
    print(f"\nOK: {out_csv.name} ({len(res_df)} modelos)")

    # Resumo
    print("\n=== DiD significativos (p < 0.05) ===")
    if len(res_df) > 0 and "p" in res_df.columns:
        sig = res_df[(res_df["p"] < 0.05) & res_df["p"].notna()]
        if len(sig) > 0:
            for _, row in sig.iterrows():
                print(f"  {row['classe_lulc']:20s} × marco {row['marco_ano']} "
                      f"[{row['controle']}] β={row['beta_did']:+.4f} p={row['p']:.4f}")
        else:
            print("  Nenhum DiD significativo.")
    else:
        print("  Nenhum modelo ajustado.")

    print(f"\nFeito — resultados em {DIR_OUT}")


if __name__ == "__main__":
    main()