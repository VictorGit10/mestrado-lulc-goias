"""analise_reserva_terra.py — Pipeline #28 (análise)
Consome data/processed/pastagem_idade_conversao.csv (Sub-pipeline A) e produz
análises descritivas da hipótese "pastagem como reserva de terra":

  1. Distribuição global da idade da pastagem na conversão para agricultura
  2. Distribuição por ATO político (Heranca Cerradeira → Cerrado Manifesto)
  3. Distribuição por mesorregião IBGE
  4. Coortes veg.nat → pastagem → agricultura (origem confirmada)
  5. Cruzamento com Δ SICOR e Δ VA agro (painel_unificado.csv)
  6. Idade mediana temporal com sobreposição de marcos (1995/2012/2018)
  7. Estatísticas resumo por ATO × mesorregião → CSV

Saídas em outputs/idade_pastagem/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_IN = ROOT / "data" / "processed" / "pastagem_idade_conversao.csv"
PAINEL = ROOT / "data" / "processed" / "painel_unificado.csv"
DIR_OUT = ROOT / "outputs" / "idade_pastagem"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"
DIR_VIZ.mkdir(parents=True, exist_ok=True)

from config_periodos import ATOS_FLAT as ATOS, MARCOS_FLAT as MARCOS

COR_ATO = {
    "I": "#8a8a82", "II": "#4a7ba6", "III": "#2d5a3d",
    "IV": "#d4b65a", "V": "#d96aa3",
}


def carregar() -> pd.DataFrame:
    if not CSV_IN.exists():
        sys.exit(f"Arquivo não encontrado: {CSV_IN}\nRode primeiro: python scripts/coleta_idade_pastagem.py")
    df = pd.read_csv(CSV_IN, dtype={"cd_mun": "int64"})
    # Censura à esquerda: idade pode estar truncada quando ano_inicio < 1985
    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    df["ato"] = pd.cut(
        df["ano_conversao"],
        bins=[1984] + [v[1] for v in ATOS.values()],
        labels=list(ATOS.keys()),
    )
    return df


def estatisticas(s: pd.Series) -> dict:
    if s.empty:
        return {"n": 0}
    return {
        "n": int(s.size),
        "mediana": float(s.median()),
        "media": float(s.mean()),
        "p10": float(s.quantile(0.10)),
        "p90": float(s.quantile(0.90)),
    }


def fig_distribuicao_global(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    nao_cens = df[~df["censurado"]]["idade_pastagem_anos"]
    cens = df[df["censurado"]]["idade_pastagem_anos"]
    bins = np.arange(0, max(40, int(df["idade_pastagem_anos"].max()) + 2))
    ax.hist([nao_cens, cens], bins=bins, stacked=True,
            color=["#d4b65a", "#cccccc"],
            label=[f"Origem identificada (n={nao_cens.size:,})",
                   f"Censurado à esquerda (n={cens.size:,})"])
    med = nao_cens.median()
    ax.axvline(med, color="#a3387f", linestyle="--",
               label=f"Mediana não-censurado = {med:.0f} anos")
    ax.set_xlabel("Idade da pastagem no momento da conversão (anos)")
    ax.set_ylabel("Número de pixels amostrados")
    ax.set_title("Idade da pastagem ao virar agricultura — Goiás 1986–2024")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "distribuicao_global.png", dpi=150)
    plt.close(fig)


def fig_por_ato(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 5, figsize=(20, 4.5), sharey=True)
    bins = np.arange(0, 41, 2)
    for ax, (ato_id, (ai, af, nome)) in zip(axes, ATOS.items()):
        sub = df[df["ato"] == ato_id]["idade_pastagem_anos"]
        if sub.empty:
            ax.set_title(f"ATO {ato_id}\n{ai}-{af}\n(sem dados)")
            continue
        ax.hist(sub, bins=bins, color=COR_ATO[ato_id], edgecolor="white")
        med = sub.median()
        ax.axvline(med, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"ATO {ato_id} — {nome}\n{ai}–{af}\nn={sub.size:,}  mediana={med:.0f}a")
        ax.set_xlabel("Idade (anos)")
    axes[0].set_ylabel("Pixels")
    fig.suptitle("Idade da pastagem na conversão para agricultura — por ATO político",
                 y=1.02, fontsize=13)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "distribuicao_por_ato.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_por_mesorregiao(df: pd.DataFrame) -> None:
    mesos = sorted(df["mesorregiao"].dropna().unique())
    mesos = [m for m in mesos if m]
    if not mesos:
        return
    ncols = min(5, len(mesos))
    nrows = (len(mesos) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 4 * nrows), sharey=True)
    if nrows * ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes.reshape(1, -1)

    bins = np.arange(0, 41, 2)
    for ax, meso in zip(axes.flat, mesos):
        sub = df[df["mesorregiao"] == meso]["idade_pastagem_anos"]
        if sub.empty:
            ax.set_visible(False)
            continue
        ax.hist(sub, bins=bins, color="#2d5a3d", edgecolor="white")
        med = sub.median()
        ax.axvline(med, color="#a3387f", linestyle="--")
        ax.set_title(f"{meso}\nn={sub.size:,}  mediana={med:.0f}a")
        ax.set_xlabel("Idade (anos)")
    for ax in axes.flat[len(mesos):]:
        ax.set_visible(False)
    axes.flat[0].set_ylabel("Pixels")
    fig.suptitle("Idade da pastagem na conversão para agricultura — por mesorregião IBGE",
                 y=1.01, fontsize=13)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "distribuicao_por_mesorregiao.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_coortes_vegnat(df: pd.DataFrame) -> None:
    """Compara duração da fase pastagem para coortes com origem identificada."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bins = np.arange(0, 41, 2)
    grupos = [
        ("vegetacao_natural", "#2d5a3d", "Veg.nat → pastagem → agricultura"),
        ("agricultura",       "#d96aa3", "Agric → pastagem → agricultura (rotação)"),
        ("outros",            "#b8a98a", "Outros → pastagem → agricultura"),
    ]
    for origem, cor, label in grupos:
        sub = df[df["origem_anterior"] == origem]["idade_pastagem_anos"]
        if sub.empty:
            continue
        ax.hist(sub, bins=bins, alpha=0.55, color=cor,
                label=f"{label}\n(n={sub.size:,}, mediana={sub.median():.0f}a)")
    ax.set_xlabel("Duração da fase pastagem (anos)")
    ax.set_ylabel("Pixels")
    ax.set_title("Coortes da conversão para agricultura — por origem anterior à pastagem")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "coortes_vegnat_pastagem_agric.png", dpi=150)
    plt.close(fig)


def fig_temporal_marcos(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    agg = (df.groupby("ano_conversao")["idade_pastagem_anos"]
             .agg(["median", "mean", "count"]).reset_index())
    ax.plot(agg["ano_conversao"], agg["median"], marker="o",
            color="#a3387f", label="Mediana")
    ax.plot(agg["ano_conversao"], agg["mean"], marker="x",
            color="#4a7ba6", label="Média", alpha=0.7)
    for ano, label in MARCOS.items():
        if ano >= agg["ano_conversao"].min() and ano <= agg["ano_conversao"].max():
            ax.axvline(ano, color="black", linestyle=":", alpha=0.5)
            ax.text(ano, ax.get_ylim()[1] * 0.95, label,
                    rotation=90, va="top", ha="right", fontsize=8)
    ax.set_xlabel("Ano da conversão pastagem → agricultura")
    ax.set_ylabel("Idade da pastagem (anos)")
    ax.set_title("Idade mediana e média da pastagem na conversão — série temporal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "idade_temporal_marcos.png", dpi=150)
    plt.close(fig)


def fig_cruzamento_painel(df: pd.DataFrame) -> pd.DataFrame:
    """Idade mediana por (cd_mun, ano) × Δ SICOR, Δ VA agro."""
    if not PAINEL.exists():
        print(f"  [aviso] painel_unificado.csv não encontrado, pulando cruzamento")
        return pd.DataFrame()

    painel = pd.read_csv(PAINEL, dtype={"cd_mun": "int64"})
    painel = painel.sort_values(["cd_mun", "ano"])
    for col in ("sicor_total_real_rs", "va_agro_real_rs"):
        if col in painel.columns:
            painel[f"d_{col}"] = painel.groupby("cd_mun")[col].diff()

    idade_mun = (df.groupby(["cd_mun", "ano_conversao"])["idade_pastagem_anos"]
                   .median().reset_index()
                   .rename(columns={"ano_conversao": "ano",
                                    "idade_pastagem_anos": "idade_mediana"}))
    merged = idade_mun.merge(painel, on=["cd_mun", "ano"], how="left")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    pares = [
        ("d_sicor_total_real_rs", "Δ SICOR total (R$ 2024)", axes[0]),
        ("d_va_agro_real_rs",     "Δ VA agropecuária (R$ 2024)", axes[1]),
    ]
    for col, label, ax in pares:
        if col not in merged.columns:
            ax.set_visible(False)
            continue
        m = merged.dropna(subset=[col, "idade_mediana"])
        if m.empty:
            ax.set_visible(False)
            continue
        ax.scatter(m[col], m["idade_mediana"], alpha=0.25, s=8, color="#2d5a3d")
        r = m[col].corr(m["idade_mediana"])
        ax.set_xlabel(label)
        ax.set_ylabel("Idade mediana da pastagem convertida (anos)")
        ax.set_title(f"r = {r:+.3f}  (n={m.shape[0]:,})")
    fig.suptitle("Idade mediana × Δ socioeconômicos por (município, ano)", y=1.02)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "idade_x_socioeconomicos.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return merged


def resumo_estatisticas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    linhas.append({"escopo": "GLOBAL", "chave": "todos", **estatisticas(df["idade_pastagem_anos"])})
    linhas.append({"escopo": "GLOBAL", "chave": "nao_censurado",
                   **estatisticas(df[~df["censurado"]]["idade_pastagem_anos"])})
    for ato_id, (ai, af, nome) in ATOS.items():
        sub = df[df["ato"] == ato_id]["idade_pastagem_anos"]
        linhas.append({"escopo": "ATO", "chave": f"{ato_id}_{nome}", **estatisticas(sub)})
    for meso in sorted(df["mesorregiao"].dropna().unique()):
        if not meso:
            continue
        sub = df[df["mesorregiao"] == meso]["idade_pastagem_anos"]
        linhas.append({"escopo": "MESORREGIAO", "chave": meso, **estatisticas(sub)})
    for origem in df["origem_anterior"].dropna().unique():
        sub = df[df["origem_anterior"] == origem]["idade_pastagem_anos"]
        linhas.append({"escopo": "ORIGEM", "chave": origem, **estatisticas(sub)})
    return pd.DataFrame(linhas)


def exportar_jsons_viz(df: pd.DataFrame) -> None:
    """JSONs consumidos pela aba nova do Visualizacao/."""
    municipal = (df.groupby(["cd_mun", "nm_mun", "mesorregiao"])
                   ["idade_pastagem_anos"]
                   .agg(["median", "mean", "count"]).reset_index())
    municipal.columns = ["cd_mun", "nm_mun", "mesorregiao",
                         "idade_mediana", "idade_media", "n_pixels"]
    (DIR_VIZ / "idade_pastagem_municipal.json").write_text(
        municipal.to_json(orient="records", force_ascii=False, indent=2),
        encoding="utf-8",
    )

    histograma = []
    for ato_id, (ai, af, nome) in ATOS.items():
        sub = df[df["ato"] == ato_id]["idade_pastagem_anos"]
        if sub.empty:
            continue
        counts, edges = np.histogram(sub, bins=np.arange(0, 41, 2))
        histograma.append({
            "ato": ato_id, "nome": nome, "periodo": [ai, af],
            "bins": edges.tolist(),
            "counts": counts.tolist(),
            "mediana": float(sub.median()),
            "n": int(sub.size),
        })
    (DIR_VIZ / "idade_pastagem_histograma.json").write_text(
        json.dumps(histograma, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    print(f"Lendo {CSV_IN.name}...")
    df = carregar()
    print(f"  {len(df):,} pixels | {df['ano_conversao'].nunique()} anos | "
          f"{df['cd_mun'].nunique()} munis")
    print(f"  Censurado à esquerda: {df['censurado'].mean() * 100:.1f}%")

    print("\nGerando figuras...")
    fig_distribuicao_global(df)
    fig_por_ato(df)
    fig_por_mesorregiao(df)
    fig_coortes_vegnat(df)
    fig_temporal_marcos(df)
    merged = fig_cruzamento_painel(df)
    print(f"  {len(list(DIR_OUT.glob('*.png')))} PNGs em {DIR_OUT.relative_to(ROOT)}")

    print("\nGerando estatísticas...")
    stats = resumo_estatisticas(df)
    csv_stats = ROOT / "data" / "processed" / "idade_pastagem_estatisticas.csv"
    stats.to_csv(csv_stats, index=False, float_format="%.2f")
    print(f"  {csv_stats.relative_to(ROOT)}")

    print("\nExportando JSONs para visualização web...")
    exportar_jsons_viz(df)
    print(f"  idade_pastagem_municipal.json | idade_pastagem_histograma.json")

    print("\n" + "=" * 60)
    print("Resumo executivo:")
    nao_cens = df[~df["censurado"]]
    print(f"  Idade mediana global (não-censurado): {nao_cens['idade_pastagem_anos'].median():.1f} anos")
    print(f"  IQR: {nao_cens['idade_pastagem_anos'].quantile(0.25):.0f}-"
          f"{nao_cens['idade_pastagem_anos'].quantile(0.75):.0f} anos")
    print(f"  Coortes veg.nat → pastagem → agric: "
          f"{(df['origem_anterior'] == 'vegetacao_natural').sum():,} pixels "
          f"({(df['origem_anterior'] == 'vegetacao_natural').mean() * 100:.1f}%)")


if __name__ == "__main__":
    main()
