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

from estatistica_ponderada import quantil, mediana, media, desvio, gmm_ponderado

ROOT = Path(__file__).resolve().parent.parent
CSV_IN = ROOT / "data" / "processed" / "pastagem_idade_conversao.csv"
CENSO_IN = ROOT / "data" / "processed" / "pastagem_idade_censo.parquet"
MESO_IN = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
PAINEL = ROOT / "data" / "processed" / "painel_unificado.csv"
DIR_OUT = ROOT / "outputs" / "idade_pastagem"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"
DIR_VIZ.mkdir(parents=True, exist_ok=True)

from config_periodos import ATOS_FLAT as ATOS, MARCOS_FLAT as MARCOS

COR_ATO = {
    "I": "#8a8a82", "II": "#4a7ba6", "III": "#2d5a3d",
}


def carregar(fonte: str = "censo") -> pd.DataFrame:
    """Devolve sempre um DataFrame com coluna `peso`, venha de onde vier.

    `fonte="censo"`  → censo de pixels; peso = n_pixels da célula.
    `fonte="amostra"` → amostra do #28A; peso = 1 em toda linha.

    Uniformizar em `peso` é o que permite UM único caminho de código para as
    duas fontes. Como a estatística ponderada reduz exatamente ao caso não
    ponderado quando peso=1 (ver `estatistica_ponderada.testa_equivalencia`),
    rodar com `--fonte amostra` reproduz os números publicados do #28 — o que
    torna qualquer diferença atribuível aos DADOS, nunca à implementação.
    """
    if fonte == "censo":
        if not CENSO_IN.exists():
            sys.exit(f"Censo não encontrado: {CENSO_IN}\n"
                     f"Rode: python scripts/processa_cubo_idade.py --shards data/raw/cubo_go")
        df = pd.read_parquet(CENSO_IN).rename(columns={"n_pixels": "peso"})
        # O censo guarda cd_mun; a mesorregião vem do mesmo crosswalk que o #28A usa
        meso = pd.read_csv(MESO_IN, dtype={"cd_mun": "int64"})
        df = df.merge(meso[["cd_mun", "nm_meso"]], on="cd_mun", how="left")
        df["mesorregiao"] = df["nm_meso"].fillna("")
        df = df.drop(columns=["nm_meso"])
        df["peso"] = df["peso"].astype("float64")
    elif fonte == "amostra":
        if not CSV_IN.exists():
            sys.exit(f"Arquivo não encontrado: {CSV_IN}\nRode primeiro: python scripts/coleta_idade_pastagem.py")
        df = pd.read_csv(CSV_IN, dtype={"cd_mun": "int64"})
        # A amostragem do #28A usa o ENVELOPE retangular de GO (bbox), que engloba
        # faixas de estados vizinhos; esses pixels não recebem município no overlay
        # (cd_mun == 0) e ~99,9% caem fora do polígono de Goiás.
        df = df[df["cd_mun"] != 0].copy()
        # Classe 21 (Mosaico de Usos) faltava no GRUPO_MAP da coleta e caía no
        # `.fillna("censurado_esquerda")` — idade conhecida rotulada como
        # desconhecida. Corrigido aqui para a amostra ficar comparável ao censo.
        df.loc[df["classe_antes_id"] == 21, "origem_anterior"] = "mosaico"
        df["peso"] = 1.0
    else:
        sys.exit(f"fonte desconhecida: {fonte!r} (use 'censo' ou 'amostra')")

    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    df["ato"] = pd.cut(
        df["ano_conversao"],
        bins=[1984] + [v[1] for v in ATOS.values()],
        labels=list(ATOS.keys()),
    )
    return df


def vp(d: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extrai (valores, pesos) de um recorte — o par que a estatística consome."""
    return (d["idade_pastagem_anos"].to_numpy(dtype=float),
            d["peso"].to_numpy(dtype=float))


def estatisticas(d: pd.DataFrame) -> dict:
    if d.empty or d["peso"].sum() <= 0:
        return {"n": 0}
    v, w = vp(d)
    return {
        "n": int(round(w.sum())),
        "mediana": mediana(v, w),
        "media": media(v, w),
        "p10": float(quantil(v, w, 0.10)),
        "p90": float(quantil(v, w, 0.90)),
    }


def fig_distribuicao_global(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    vnc, wnc = vp(df[~df["censurado"]])
    vc, wc = vp(df[df["censurado"]])
    bins = np.arange(0, max(40, int(df["idade_pastagem_anos"].max()) + 2))
    ax.hist([vnc, vc], bins=bins, stacked=True, weights=[wnc, wc],
            color=["#d4b65a", "#cccccc"],
            label=[f"Origem identificada (n={wnc.sum():,.0f})",
                   f"Censurado à esquerda (n={wc.sum():,.0f})"])
    med = mediana(vnc, wnc)
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
        sub = df[df["ato"] == ato_id]
        if sub.empty:
            ax.set_title(f"ATO {ato_id}\n{ai}-{af}\n(sem dados)")
            continue
        v, w = vp(sub)
        ax.hist(v, bins=bins, weights=w, color=COR_ATO[ato_id], edgecolor="white")
        med = mediana(v, w)
        ax.axvline(med, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"ATO {ato_id} — {nome}\n{ai}–{af}\nn={w.sum():,.0f}  mediana={med:.0f}a")
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
        sub = df[df["mesorregiao"] == meso]
        if sub.empty:
            ax.set_visible(False)
            continue
        v, w = vp(sub)
        ax.hist(v, bins=bins, weights=w, color="#2d5a3d", edgecolor="white")
        med = mediana(v, w)
        ax.axvline(med, color="#a3387f", linestyle="--")
        ax.set_title(f"{meso}\nn={w.sum():,.0f}  mediana={med:.0f}a")
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
        # Mosaico de Usos: no #28A esta coorte não existia — a classe 21 faltava
        # no GRUPO_MAP e caía em "censurado". É ~12% das conversões.
        ("mosaico",           "#c98a3a", "Mosaico de usos → pastagem → agricultura"),
        ("outros",            "#b8a98a", "Outros → pastagem → agricultura"),
    ]
    for origem, cor, label in grupos:
        sub = df[df["origem_anterior"] == origem]
        if sub.empty:
            continue
        v, w = vp(sub)
        ax.hist(v, bins=bins, weights=w, alpha=0.55, color=cor,
                label=f"{label}\n(n={w.sum():,.0f}, mediana={mediana(v, w):.0f}a)")
    ax.set_xlabel("Duração da fase pastagem (anos)")
    ax.set_ylabel("Pixels")
    ax.set_title("Coortes da conversão para agricultura — por origem anterior à pastagem")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "coortes_vegnat_pastagem_agric.png", dpi=150)
    plt.close(fig)


def agrega_ponderado(df: pd.DataFrame, por, extras: dict | None = None) -> pd.DataFrame:
    """groupby ponderado: mediana, média e n (soma dos pesos) por chave.

    `pandas.groupby().median()` ignoraria a coluna `peso` e trataria cada célula
    do censo como uma observação — o que daria a uma célula de 3 pixels o mesmo
    peso de uma de 300 mil.
    """
    if isinstance(por, str):
        por = [por]
    linhas = []
    for chave, g in df.groupby(por, observed=True, dropna=False):
        v, w = vp(g)
        if w.sum() <= 0:
            continue
        chave = chave if isinstance(chave, tuple) else (chave,)
        linha = dict(zip(por, chave))
        linha["median"] = mediana(v, w)
        linha["mean"] = media(v, w)
        linha["count"] = w.sum()
        for nome, q in (extras or {}).items():
            linha[nome] = float(quantil(v, w, q))
        linhas.append(linha)
    return pd.DataFrame(linhas)


def fig_temporal_marcos(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    agg = agrega_ponderado(df, "ano_conversao").sort_values("ano_conversao")
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

    idade_mun = (agrega_ponderado(df, ["cd_mun", "ano_conversao"])
                   [["cd_mun", "ano_conversao", "median"]]
                   .rename(columns={"ano_conversao": "ano", "median": "idade_mediana"}))
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
    linhas.append({"escopo": "GLOBAL", "chave": "todos", **estatisticas(df)})
    linhas.append({"escopo": "GLOBAL", "chave": "nao_censurado",
                   **estatisticas(df[~df["censurado"]])})
    for ato_id, (ai, af, nome) in ATOS.items():
        linhas.append({"escopo": "ATO", "chave": f"{ato_id}_{nome}",
                       **estatisticas(df[df["ato"] == ato_id])})
        # Por Ato o corte não-censurado é o que sustenta as leituras do #28 —
        # no #28A a tabela publicada misturava N total com mediana não-censurada.
        linhas.append({"escopo": "ATO_NAO_CENS", "chave": f"{ato_id}_{nome}",
                       **estatisticas(df[(df["ato"] == ato_id) & ~df["censurado"]])})
    for meso in sorted(df["mesorregiao"].dropna().unique()):
        if not meso:
            continue
        linhas.append({"escopo": "MESORREGIAO", "chave": meso,
                       **estatisticas(df[df["mesorregiao"] == meso])})
    for origem in sorted(df["origem_anterior"].dropna().unique()):
        linhas.append({"escopo": "ORIGEM", "chave": origem,
                       **estatisticas(df[df["origem_anterior"] == origem])})
    return pd.DataFrame(linhas)


def exportar_jsons_viz(df: pd.DataFrame) -> None:
    """JSONs consumidos pela aba nova do Visualizacao/."""
    municipal = agrega_ponderado(df, ["cd_mun", "nm_mun", "mesorregiao"])
    municipal = municipal.rename(columns={"median": "idade_mediana",
                                          "mean": "idade_media",
                                          "count": "n_pixels"})
    municipal["n_pixels"] = municipal["n_pixels"].round().astype("int64")
    (DIR_VIZ / "idade_pastagem_municipal.json").write_text(
        municipal.to_json(orient="records", force_ascii=False, indent=2),
        encoding="utf-8",
    )

    histograma = []
    for ato_id, (ai, af, nome) in ATOS.items():
        sub = df[df["ato"] == ato_id]
        if sub.empty:
            continue
        v, w = vp(sub)
        counts, edges = np.histogram(v, bins=np.arange(0, 41, 2), weights=w)
        histograma.append({
            "ato": ato_id, "nome": nome, "periodo": [ai, af],
            "bins": edges.tolist(),
            "counts": [int(round(c)) for c in counts],
            "mediana": mediana(v, w),
            "n": int(round(w.sum())),
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

    # 4. Mosaico de usos -> pastagem -> agricultura. Categoria própria, e não
    #    diluída em "Ambíguo", porque são ~12% das conversões e o #28A as
    #    escondia dentro de "censurado" (classe 21 ausente do GRUPO_MAP).
    #    Se contam como rotação é decisão SUBSTANTIVA (origem mista
    #    agricultura/pastagem é rotação-like), deixada explícita em vez de
    #    embutida numa regra.
    df.loc[is_nao_cens & (df["origem_anterior"] == "mosaico"), "mecanismo"] = \
        "Mosaico (origem mista)"

    # 5. Censurado à esquerda
    df.loc[df["censurado"], "mecanismo"] = "Censurado à esquerda"

    return df


def ajustar_gmm_unidim(x: np.ndarray, w: np.ndarray | None = None) -> dict:
    """Ajusta GMM de 1 e 2 componentes; devolve AIC, BIC e parâmetros.

    Usa `estatistica_ponderada.gmm_ponderado` (EM com pesos de frequência)
    porque `sklearn.mixture.GaussianMixture` não aceita `sample_weight`, e
    expandir o censo em 44,6 milhões de linhas só para caber na API seria
    desperdício — a idade é inteira, logo cada recorte tem ≤40 valores
    distintos. A implementação foi verificada contra o sklearn com peso=1
    (ver `testa_equivalencia`), então a troca não muda resultado, só permite peso.

    ATENÇÃO ao ler o ΔBIC sobre o censo: com n na casa dos milhões, qualquer
    desvio ínfimo da unimodalidade produz ΔBIC astronômico. Isso reflete o
    tamanho de n, NÃO força de evidência. O censo torna μ e w mais precisos;
    não torna a bimodalidade "mais provada".
    """
    x = np.asarray(x, dtype=float).ravel()
    w = np.ones_like(x) if w is None else np.asarray(w, dtype=float).ravel()
    n = float(w.sum())

    if n < 5 or x.size < 2:
        # Poucos dados para ajustar
        return {
            "mu_1c": 0.0, "sig_1c": 1.0, "aic_1c": 0.0, "bic_1c": 0.0,
            "mu1": 0.0, "sig1": 1.0, "w1": 0.0,
            "mu2": 0.0, "sig2": 1.0, "w2": 0.0,
            "aic_2c": 0.0, "bic_2c": 0.0
        }
    
    # 1 componente
    r1 = gmm_ponderado(x, w, n_comp=1)
    mu_1c = float(r1["mu"][0])
    sig_1c = max(float(r1["sigma"][0]), 0.1)
    aic_1c, bic_1c = float(r1["aic"]), float(r1["bic"])

    # 2 componentes (gmm_ponderado já devolve ordenado por mu crescente)
    r2 = gmm_ponderado(x, w, n_comp=2)
    mu1, mu2 = (float(v) for v in r2["mu"])
    sig1, sig2 = (float(v) for v in r2["sigma"])
    w1, w2 = (float(v) for v in r2["peso"])
    aic_2c, bic_2c = float(r2["aic"]), float(r2["bic"])

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
        
        n_tot = int(round(sub_total["peso"].sum()))
        n_nc = int(round(sub_nao_cens["peso"].sum()))

        # Ajusta GMM nas idades não-censuradas
        v_nc, w_nc = vp(sub_nao_cens)
        gmm_res = ajustar_gmm_unidim(v_nc, w_nc)

        # Proporções dos mecanismos entre os não-censurados — por PESO, não por
        # linha: no censo cada linha é uma célula agregada, não uma observação.
        soma = sub_nao_cens.groupby("mecanismo", observed=True)["peso"].sum()
        total = soma.sum()
        mec_counts = (soma / total) if total > 0 else soma
        prop_premeditado = float(mec_counts.get("Premeditado curto", 0.0))
        prop_rotacao = float(mec_counts.get("Rotação", 0.0))
        prop_oportunistico = float(mec_counts.get("Oportunístico clássico", 0.0))
        prop_mosaico = float(mec_counts.get("Mosaico (origem mista)", 0.0))
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
            "prop_mosaico": prop_mosaico,
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
        sub = df[(df["ano_conversao"] >= ai) & (df["ano_conversao"] <= af) & (~df["censurado"])]
        v, w = vp(sub)

        # Histograma de densidade empírica
        ax.hist(v, bins=bins, weights=w, density=True, color="#dcdcd6",
                edgecolor="white", alpha=0.85,
                label=f"Frequência real (n={w.sum():,.0f})")
        
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
    import argparse
    p = argparse.ArgumentParser(description="Pipeline #28 — análise da idade da pastagem")
    p.add_argument("--fonte", choices=["censo", "amostra"], default="censo",
                   help="censo = todos os pixels (padrão); amostra = 2.000 px/ano do #28A")
    args = p.parse_args()

    df = carregar(args.fonte)
    n = df["peso"].sum()
    print(f"Fonte: {args.fonte}")
    print(f"  {n:,.0f} eventos em {len(df):,} linhas | {df['ano_conversao'].nunique()} anos | "
          f"{df['cd_mun'].nunique()} munis")
    cens_pct = df.loc[df["censurado"], "peso"].sum() / n * 100
    print(f"  Censurado à esquerda: {cens_pct:.1f}%")

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
    vnc, wnc = vp(df[~df["censurado"]])
    print(f"  Idade mediana global (não-censurado): {mediana(vnc, wnc):.1f} anos")
    print(f"  IQR: {quantil(vnc, wnc, 0.25):.0f}-{quantil(vnc, wnc, 0.75):.0f} anos")
    for origem in ("vegetacao_natural", "mosaico", "agricultura"):
        pe = df.loc[df["origem_anterior"] == origem, "peso"].sum()
        if pe:
            print(f"  Coorte {origem} → pastagem → agric: {pe:,.0f} px ({pe / n * 100:.1f}%)")
    
    print("\nResultados do Ajuste GMM (Ato III / Janela 2020-2024):")
    res_ato3 = resultados_gmm[-1]
    print(f"  Componente Jovem: μ = {res_ato3['mu1']:.1f} anos | Peso (w) = {res_ato3['w1'] * 100:.1f}%")
    print(f"  Componente Antigo: μ = {res_ato3['mu2']:.1f} anos | Peso (w) = {res_ato3['w2'] * 100:.1f}%")
    dbic = res_ato3['bic_1c'] - res_ato3['bic_2c']
    print(f"  ΔBIC = {dbic:,.0f} (n = {res_ato3['n_nao_censurado']:,})")
    if args.fonte == "censo":
        print("    NÃO ler como força de evidência: com censo, n é a população e")
        print("    qualquer desvio ínfimo da unimodalidade infla o ΔBIC. O ganho")
        print("    do censo está na PRECISÃO de μ e w, não no ΔBIC.")

    print("Distribuição dos Mecanismos de Conversão no Ato III (Não-Censurado):")
    print(f"  - Premeditado curto (veg.nat <= 8a): {res_ato3['prop_premeditado_curto'] * 100:.1f}%")
    print(f"  - Rotação agrícola (agric <= 8a):     {res_ato3['prop_rotacao'] * 100:.1f}%")
    print(f"  - Oportunístico clássico (veg.nat >= 20a): {res_ato3['prop_oportunistico_classico'] * 100:.1f}%")
    print(f"  - Mosaico de usos (origem mista):     {res_ato3['prop_mosaico'] * 100:.1f}%")
    print(f"  - Ambíguo / Outros (faixas intermediárias):  {res_ato3['prop_ambiguo_outro'] * 100:.1f}%")


if __name__ == "__main__":
    main()
