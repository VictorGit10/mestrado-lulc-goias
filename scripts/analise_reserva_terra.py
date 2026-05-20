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
    n_atos = len(ATOS)
    fig, axes = plt.subplots(1, n_atos, figsize=(4 * n_atos, 4.5), sharey=True)
    if n_atos == 1:
        axes = [axes]
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


def classificar_mecanismo(df: pd.DataFrame) -> pd.DataFrame:
    """Classifica cada pixel não-censurado em um dos mecanismos hipotéticos."""
    df = df.copy()
    df["mecanismo"] = "Ambíguo / Outro"
    
    is_nao_cens = ~df["censurado"]
    is_jovem = df["idade_pastagem_anos"] <= 8
    is_antigo = df["idade_pastagem_anos"] >= 20
    
    is_veg_nat = df["origem_anterior"] == "vegetacao_natural"
    is_agric = df["origem_anterior"] == "agricultura"
    
    # 1. Premeditado curto (veg.nat -> pastagem -> agricultura em <= 8 anos)
    df.loc[is_nao_cens & is_jovem & is_veg_nat, "mecanismo"] = "Premeditado curto"
    
    # 2. Rotação (agricultura -> pastagem -> agricultura em <= 8 anos)
    df.loc[is_nao_cens & is_jovem & is_agric, "mecanismo"] = "Rotação"
    
    # 3. Oportunístico clássico (veg.nat -> pastagem -> agricultura em >= 20 anos)
    df.loc[is_nao_cens & is_antigo & is_veg_nat, "mecanismo"] = "Oportunístico clássico"
    
    # 4. Censurado à esquerda
    df.loc[df["censurado"], "mecanismo"] = "Censurado à esquerda"
    
    return df


def ajustar_gmm_unidim(x: np.ndarray) -> dict:
    """Ajusta GMM de 1 e 2 componentes e retorna AIC, BIC e parâmetros estimados."""
    from scipy.stats import norm
    
    x = x.reshape(-1, 1)
    n = len(x)
    
    if n < 5:
        # Poucos dados para ajustar
        return {
            "mu_1c": 0.0, "sig_1c": 1.0, "aic_1c": 0.0, "bic_1c": 0.0,
            "mu1": 0.0, "sig1": 1.0, "w1": 0.0,
            "mu2": 0.0, "sig2": 1.0, "w2": 0.0,
            "aic_2c": 0.0, "bic_2c": 0.0
        }
    
    # Modelo de 1 componente (Gaussiana simples)
    mu_1c = float(np.mean(x))
    sig_1c = float(np.std(x))
    sig_1c = max(sig_1c, 0.1)  # evitar divisão por zero
    
    ll_1c = float(np.sum(norm.logpdf(x, loc=mu_1c, scale=sig_1c)))
    aic_1c = 2 * 2 - 2 * ll_1c  # 2 parâmetros: media, std
    bic_1c = 2 * np.log(n) - 2 * ll_1c
    
    # Modelo de 2 componentes (Mistura)
    try:
        from sklearn.mixture import GaussianMixture
        gmm = GaussianMixture(n_components=2, random_state=42, max_iter=250)
        gmm.fit(x)
        w1, w2 = gmm.weights_
        mu1, mu2 = gmm.means_.flatten()
        sig1, sig2 = np.sqrt(gmm.covariances_.flatten())
        aic_2c = gmm.aic(x)
        bic_2c = gmm.bic(x)
    except ImportError:
        # Fallback usando scipy.optimize para ajuste de máxima verossimilhança
        from scipy.optimize import minimize
        
        x_flat = x.flatten()
        # Chutes iniciais inteligentes baseados nos dois modos conhecidos
        init_mu1 = np.mean(x_flat[x_flat <= 10]) if np.any(x_flat <= 10) else 4.0
        init_mu2 = np.mean(x_flat[x_flat > 10]) if np.any(x_flat > 10) else 30.0
        init_sig1 = np.std(x_flat[x_flat <= 10]) if np.any(x_flat <= 10) and np.std(x_flat[x_flat <= 10]) > 0.5 else 3.0
        init_sig2 = np.std(x_flat[x_flat > 10]) if np.any(x_flat > 10) and np.std(x_flat[x_flat > 10]) > 0.5 else 3.0
        
        # Parâmetros irrestritos iniciais: [logit(w), mu1, log(sig1), mu2, log(sig2)]
        theta0 = [0.0, float(init_mu1), np.log(float(init_sig1)), float(init_mu2), np.log(float(init_sig2))]
        
        def nll(theta):
            w = 1.0 / (1.0 + np.exp(-theta[0]))
            m1 = theta[1]
            s1 = np.exp(theta[2])
            m2 = theta[3]
            s2 = np.exp(theta[4])
            
            pdf1 = norm.pdf(x_flat, loc=m1, scale=s1)
            pdf2 = norm.pdf(x_flat, loc=m2, scale=s2)
            
            val = w * pdf1 + (1.0 - w) * pdf2
            val = np.maximum(val, 1e-15)  # evitar log(0)
            return -np.sum(np.log(val))
            
        res = minimize(nll, theta0, method="L-BFGS-B")
        
        w1 = 1.0 / (1.0 + np.exp(-res.x[0]))
        w2 = 1.0 - w1
        mu1 = res.x[1]
        sig1 = np.exp(res.x[2])
        mu2 = res.x[3]
        sig2 = np.exp(res.x[4])
        
        ll_2c = -res.fun
        aic_2c = 2 * 5 - 2 * ll_2c  # 5 parâmetros: w, mu1, sig1, mu2, sig2
        bic_2c = 5 * np.log(n) - 2 * ll_2c

    # Garantir que mu1 <= mu2 para manter o componente 1 como o "Jovem"
    if mu1 > mu2:
        mu1, mu2 = mu2, mu1
        sig1, sig2 = sig2, sig1
        w1, w2 = w2, w1

    return {
        "mu_1c": float(mu_1c), "sig_1c": float(sig_1c), "aic_1c": float(aic_1c), "bic_1c": float(bic_1c),
        "mu1": float(mu1), "sig1": float(sig1), "w1": float(w1),
        "mu2": float(mu2), "sig2": float(sig2), "w2": float(w2),
        "aic_2c": float(aic_2c), "bic_2c": float(bic_2c)
    }


def analise_sensibilidade_gmm_janelas(df: pd.DataFrame) -> list:
    """Realiza análise de sensibilidade por janelas deslizantes e ajusta GMM em cada uma."""
    janelas = [
        {"nome": "2016–2024", "anos": (2016, 2024)},
        {"nome": "2017–2024", "anos": (2017, 2024)},
        {"nome": "2018–2024", "anos": (2018, 2024)},
        {"nome": "2020–2024", "anos": (2020, 2024)},
    ]
    
    resultados = []
    df_mecanismos = classificar_mecanismo(df)
    
    for j in janelas:
        ai, af = j["anos"]
        sub_total = df_mecanismos[(df_mecanismos["ano_conversao"] >= ai) & (df_mecanismos["ano_conversao"] <= af)]
        sub_nao_cens = sub_total[~sub_total["censurado"]]
        
        n_tot = len(sub_total)
        n_nc = len(sub_nao_cens)
        
        # Ajusta GMM nas idades não-censuradas
        gmm_res = ajustar_gmm_unidim(sub_nao_cens["idade_pastagem_anos"].values)
        
        # Proporções dos mecanismos entre os não-censurados
        mec_counts = sub_nao_cens["mecanismo"].value_counts(normalize=True)
        prop_premeditado = float(mec_counts.get("Premeditado curto", 0.0))
        prop_rotacao = float(mec_counts.get("Rotação", 0.0))
        prop_oportunistico = float(mec_counts.get("Oportunístico clássico", 0.0))
        prop_ambiguo = float(mec_counts.get("Ambíguo / Outro", 0.0))
        
        res = {
            "janela": j["nome"],
            "ano_inicio": ai,
            "ano_fim": af,
            "n_total": n_tot,
            "n_nao_censurado": n_nc,
            **gmm_res,
            "prop_premeditado_curto": prop_premeditado,
            "prop_rotacao": prop_rotacao,
            "prop_oportunistico_classico": prop_oportunistico,
            "prop_ambiguo_outro": prop_ambiguo
        }
        resultados.append(res)
        
    return resultados


def fig_sensibilidade_gmm(df: pd.DataFrame, resultados: list) -> None:
    """Gera figura de 4 painéis dos GMMs ajustados sobre os histogramas de cada janela."""
    from scipy.stats import norm
    
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.5), sharex=True, sharey=True)
    axes = axes.flatten()
    
    bins = np.arange(0, 41, 2)
    x_plot = np.linspace(0, 40, 500)
    
    for ax, res in zip(axes, resultados):
        ai, af = res["ano_inicio"], res["ano_fim"]
        
        # Filtra dados reais da janela
        sub = df[(df["ano_conversao"] >= ai) & (df["ano_conversao"] <= af) & (~df["censurado"])]["idade_pastagem_anos"]
        
        # Histograma de densidade empírica
        ax.hist(sub, bins=bins, density=True, color="#dcdcd6", edgecolor="white", alpha=0.85,
                label=f"Frequência real (n={len(sub):,})")
        
        # Parâmetros estimadores do GMM
        w1, mu1, sig1 = res["w1"], res["mu1"], res["sig1"]
        w2, mu2, sig2 = res["w2"], res["mu2"], res["sig2"]
        
        # Plot das densidades de probabilidade do GMM
        y1 = w1 * norm.pdf(x_plot, loc=mu1, scale=sig1)
        y2 = w2 * norm.pdf(x_plot, loc=mu2, scale=sig2)
        y_mistura = y1 + y2
        
        ax.plot(x_plot, y_mistura, color="#8a3068", linewidth=2.5, label="Mistura GMM (2 comp.)")
        ax.plot(x_plot, y1, color="#d95f02", linestyle="--", linewidth=1.5, label=f"Comp. Jovem (w={w1:.2f})")
        ax.plot(x_plot, y2, color="#1b9e77", linestyle="--", linewidth=1.5, label=f"Comp. Antigo (w={w2:.2f})")
        
        diff_bic = res["bic_1c"] - res["bic_2c"]
        status_bic = "2 Comp. Superior (ΔBIC > 10)" if diff_bic > 10 else "Sem forte preferência"
        
        ax.set_title(f"Janela {res['janela']} ({ai}–{af})\n"
                     f"Comp. Jovem: μ={mu1:.1f}a (w={w1 * 100:.0f}%)\n"
                     f"Comp. Antigo: μ={mu2:.1f}a (w={w2 * 100:.0f}%)\n"
                     f"ΔBIC = {diff_bic:.1f} ({status_bic})", fontsize=10)
        ax.set_xlabel("Idade da pastagem na conversão (anos)", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.4)
        
        if ax in (axes[0], axes[2]):
            ax.set_ylabel("Densidade de probabilidade", fontsize=9)
        ax.legend(fontsize=8, loc="upper right")
        
    fig.suptitle("Modelagem por Mistura Gaussiana (GMM) da Idade da Pastagem na Conversão\n"
                 "Análise de Sensibilidade por Janelas Deslizantes (Dados Não-Censurados)", fontsize=13, y=0.98)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "gmm_janelas_deslizantes.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    print(f"Lendo {CSV_IN.name}...")
    df = carregar()
    print(f"  {len(df):,} pixels | {df['ano_conversao'].nunique()} anos | "
          f"{df['cd_mun'].nunique()} munis")
    print(f"  Censurado à esquerda: {df['censurado'].mean() * 100:.1f}%")

    print("\nGerando figuras base...")
    fig_distribuicao_global(df)
    fig_por_ato(df)
    fig_por_mesorregiao(df)
    fig_coortes_vegnat(df)
    fig_temporal_marcos(df)
    merged = fig_cruzamento_painel(df)
    
    print("\nExecutando modelagem GMM e análise de sensibilidade por janelas deslizantes...")
    resultados_gmm = analise_sensibilidade_gmm_janelas(df)
    
    print("Gerando figura do GMM de janelas deslizantes...")
    fig_sensibilidade_gmm(df, resultados_gmm)
    
    print(f"  {len(list(DIR_OUT.glob('*.png')))} PNGs em {DIR_OUT.relative_to(ROOT)}")

    print("\nGerando estatísticas descritivas básicas...")
    stats = resumo_estatisticas(df)
    csv_stats = ROOT / "data" / "processed" / "idade_pastagem_estatisticas.csv"
    stats.to_csv(csv_stats, index=False, float_format="%.2f")
    print(f"  {csv_stats.relative_to(ROOT)}")
    
    print("Exportando CSV de sensibilidade GMM...")
    df_sens = pd.DataFrame(resultados_gmm)
    csv_sens = ROOT / "data" / "processed" / "idade_pastagem_gmm_sensibilidade.csv"
    df_sens.to_csv(csv_sens, index=False, float_format="%.4f")
    print(f"  {csv_sens.relative_to(ROOT)}")

    print("\nExportando JSONs para visualização web...")
    exportar_jsons_viz(df)
    
    # Exporta o JSON do GMM estruturado para a aba do visualizador
    (DIR_VIZ / "idade_pastagem_gmm.json").write_text(
        json.dumps(resultados_gmm, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  idade_pastagem_municipal.json | idade_pastagem_histograma.json | idade_pastagem_gmm.json")

    print("\n" + "=" * 60)
    print("Resumo executivo:")
    nao_cens = df[~df["censurado"]]
    print(f"  Idade mediana global (não-censurado): {nao_cens['idade_pastagem_anos'].median():.1f} anos")
    print(f"  IQR: {nao_cens['idade_pastagem_anos'].quantile(0.25):.0f}-"
          f"{nao_cens['idade_pastagem_anos'].quantile(0.75):.0f} anos")
    print(f"  Coortes veg.nat → pastagem → agric: "
          f"{(df['origem_anterior'] == 'vegetacao_natural').sum():,} pixels "
          f"({(df['origem_anterior'] == 'vegetacao_natural').mean() * 100:.1f}%)")
    
    print("\nResultados do Ajuste GMM (Ato III / Janela 2020-2024):")
    res_ato3 = resultados_gmm[-1]
    print(f"  Componente Jovem: μ = {res_ato3['mu1']:.1f} anos | Peso (w) = {res_ato3['w1'] * 100:.1f}%")
    print(f"  Componente Antigo: μ = {res_ato3['mu2']:.1f} anos | Peso (w) = {res_ato3['w2'] * 100:.1f}%")
    print(f"  Força da Bimodalidade: ΔBIC = {res_ato3['bic_1c'] - res_ato3['bic_2c']:.1f} "
          f"(evidência muito forte a favor de 2 comp. se ΔBIC > 10)")
    
    print("Distribuição dos Mecanismos de Conversão no Ato III (Não-Censurado):")
    print(f"  - Premeditado curto (veg.nat <= 8a): {res_ato3['prop_premeditado_curto'] * 100:.1f}%")
    print(f"  - Rotação agrícola (agric <= 8a):     {res_ato3['prop_rotacao'] * 100:.1f}%")
    print(f"  - Oportunístico clássico (veg.nat >= 20a): {res_ato3['prop_oportunistico_classico'] * 100:.1f}%")
    print(f"  - Ambíguo / Outros (faixas intermediárias):  {res_ato3['prop_ambiguo_outro'] * 100:.1f}%")


if __name__ == "__main__":
    main()
