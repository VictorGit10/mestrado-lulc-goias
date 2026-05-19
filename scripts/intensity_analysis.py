"""intensity_analysis.py — Pipeline #31: Intensity Analysis (Aldwaik & Pontius 2012)
================================================================================

Testa se a taxa de mudança LULC é estacionária entre intervalos de tempo.
Diagnóstico para a periodização: se a intensidade de mudança entre 2001-2005
e 2006-2019 é indistinguível, a fronteira é artificial.

Três níveis:
  1. Intervalo: a taxa ANUAL de mudança total varia entre intervalos?
  2. Categoria: ganho e perda de cada categoria variam entre intervalos?
  3. Transição: transições específicas (e.g. pasto→agric) variam?

Pre-requisitos:
    data/processed/conversao_bruta_goias.csv (Pipeline #19)
    data/processed/taxas_lulc_goias.csv (Pipeline #17)
    scripts/config_periodos.py

Referencia:
    ALDWAIK, S. A.; PONTIUS JR., R. G. Intensity analysis to unify
    measurements of change and exclusion difference from thematic maps
    and to quantify map error. International Journal of Remote Sensing,
    v. 33, n. 16, p. 5087-5103, 2012.
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DIR_DATA = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "correlacoes"

from config_periodos import ATOS, ATOS_FLAT

GRUPOS = ["vegetacao_natural", "pastagem", "agricultura", "agua", "area_urbana", "outros"]


def carregar_transicoes() -> pd.DataFrame:
    """Carrega transicoes anuais agregadas por UF."""
    df = pd.read_csv(DIR_DATA / "conversao_bruta_goias.csv")
    return df


def matriz_anual(df: pd.DataFrame, ano_orig: int, ano_dest: int) -> np.ndarray:
    """Constroi matriz de transicao (6x6) em Mha para um par de anos."""
    sub = df[(df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest)]
    m = np.zeros((6, 6))
    for _, row in sub.iterrows():
        i = GRUPOS.index(row["grupo_orig"])
        j = GRUPOS.index(row["grupo_dest"])
        m[i, j] = row["area_mha"]
    return m


def area_inicial(mat: np.ndarray) -> np.ndarray:
    """Vetor de areas iniciais (soma por linha)."""
    return mat.sum(axis=1)


# ─────────────────────── Nivel 1: Intervalo ───────────────────────

def taxa_anual_mudanca(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula a taxa anual de mudanca total para cada par de anos.

    Taxa = (area que mudou) / (area total) / (duracao em anos).
    Como cada par e de 1 ano, duracao = 1.
    """
    rows = []
    anos = sorted(df["ano_origem"].unique())
    for ano_o in anos:
        ano_d = ano_o + 1
        mat = matriz_anual(df, ano_o, ano_d)
        total = mat.sum()
        off_diag = total - np.trace(mat)
        taxa = off_diag / total if total > 0 else 0
        rows.append({
            "ano": ano_o,
            "ano_dest": ano_d,
            "area_total_mha": round(total, 4),
            "area_mudou_mha": round(off_diag, 4),
            "taxa_anual": round(taxa, 6),
        })
    return pd.DataFrame(rows)


def teste_intervalo(df_taxa: pd.DataFrame, periodos: dict) -> dict:
    """Testa se a taxa anual de mudanca difere entre periodos.

    Kruskal-Wallis (nao parametrico) e ANOVA.
    """
    grupos = {}
    for nome, (ini, fim, _) in periodos.items():
        taxa = df_taxa[(df_taxa["ano"] >= ini) & (df_taxa["ano"] < fim)]["taxa_anual"].values
        grupos[nome] = taxa

    # Kruskal-Wallis
    h_stat, h_p = stats.kruskal(*grupos.values())

    # ANOVA
    f_stat, f_p = stats.f_oneway(*grupos.values())

    # Comparacoes par-a-par (Mann-Whitney com correcao Bonferroni)
    nomes = list(grupos.keys())
    pares = []
    n_comp = len(nomes) * (len(nomes) - 1) // 2
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            u, p = stats.mannwhitneyu(grupos[nomes[i]], grupos[nomes[j]], alternative="two-sided")
            p_adj = min(p * n_comp, 1.0)
            pares.append({
                "per1": nomes[i],
                "per2": nomes[j],
                "med1": round(grupos[nomes[i]].mean(), 6),
                "med2": round(grupos[nomes[j]].mean(), 6),
                "ratio": round(grupos[nomes[i]].mean() / grupos[nomes[j]].mean(), 3) if grupos[nomes[j]].mean() > 0 else float("inf"),
                "U": round(u, 1),
                "p_raw": round(p, 6),
                "p_bonferroni": round(p_adj, 6),
            })

    return {
        "kruskal_H": round(h_stat, 3),
        "kruskal_p": round(h_p, 6),
        "anova_F": round(f_stat, 3),
        "anova_p": round(f_p, 6),
        "pares": pares,
        "resumo": {n: {"n": len(v), "media": round(v.mean(), 6), "std": round(v.std(), 6)} for n, v in grupos.items()},
    }


# ─────────────────────── Nivel 2: Categoria ───────────────────────

def intensidade_categoria(df: pd.DataFrame, periodos: dict) -> pd.DataFrame:
    """Para cada categoria e periodo, calcula:
    - Taxa anual de ganho (gain intensity)
    - Taxa anual de perda (loss intensity)
    - Uniform intensity (esperada sob estacionariedade)
    """
    rows = []
    for nome, (ini, fim, _) in periodos.items():
        n_anos = fim - ini
        # Acumular matrizes anuais
        mat_total = np.zeros((6, 6))
        for ano in range(ini, fim):
            mat_total += matriz_anual(df, ano, ano + 1)

        area_inicio = area_inicial(mat_total)  # soma por linha = area no inicio acumulada
        area_total = mat_total.sum()

        for k, cat in enumerate(GRUPOS):
            # Perda: area que saiu da categoria / area da categoria / n_anos
            area_cat_inicio = mat_total[k, :].sum()
            area_persistiu = mat_total[k, k]
            area_perdeu = area_cat_inicio - area_persistiu
            taxa_perda = (area_perdeu / area_cat_inicio / n_anos) if area_cat_inicio > 0 else 0

            # Ganho: area que entrou na categoria / area total / n_anos
            area_cat_fim = mat_total[:, k].sum()
            area_ganhou = area_cat_fim - area_persistiu
            taxa_ganho = (area_ganhou / area_total / n_anos) if area_total > 0 else 0

            # Uniform: mudanca total / area total / n_anos (esperada se aleatoria)
            off_diag = area_total - np.trace(mat_total)
            taxa_uniform = (off_diag / area_total / n_anos) if area_total > 0 else 0

            rows.append({
                "periodo": nome,
                "anos": f"{ini}-{fim}",
                "n_anos": n_anos,
                "categoria": cat,
                "perdeu_mha": round(area_perdeu, 4),
                "ganhou_mha": round(area_ganhou, 4),
                "taxa_perda_anual": round(taxa_perda, 6),
                "taxa_ganho_anual": round(taxa_ganho, 6),
                "taxa_uniform_anual": round(taxa_uniform, 6),
                "ganho_vs_uniform": round(taxa_ganho / taxa_uniform, 3) if taxa_uniform > 0 else float("inf"),
                "perda_vs_uniform": round(taxa_perda / taxa_uniform, 3) if taxa_uniform > 0 else float("inf"),
            })

    return pd.DataFrame(rows)


# ─────────────────────── Diagnostico P2 vs P3 ───────────────────────

def diagnostico_p2_p3(df: pd.DataFrame, periodos: dict) -> dict:
    """Diagnostico focal: P2 (2001-2005) vs P3 (2006-2019).

    Se as taxas de mudanca sao estatisticamente indistinguiveis,
    a fronteira entre P2 e P3 e artificial.
    """
    ini_p2, fim_p2, _ = periodos["II"]
    ini_p3, fim_p3, _ = periodos["III"]

    # Taxas anuais para P2 e P3
    taxas_p2, taxas_p3 = [], []
    for ano in range(ini_p2, fim_p2):
        mat = matriz_anual(df, ano, ano + 1)
        total = mat.sum()
        off_diag = total - np.trace(mat)
        taxas_p2.append(off_diag / total if total > 0 else 0)

    for ano in range(ini_p3, fim_p3):
        mat = matriz_anual(df, ano, ano + 1)
        total = mat.sum()
        off_diag = total - np.trace(mat)
        taxas_p3.append(off_diag / total if total > 0 else 0)

    taxas_p2 = np.array(taxas_p2)
    taxas_p3 = np.array(taxas_p3)

    # Testes
    u_stat, u_p = stats.mannwhitneyu(taxas_p2, taxas_p3, alternative="two-sided")
    t_stat, t_p = stats.ttest_ind(taxas_p2, taxas_p3)

    # Efeito de 2004 (outlier?)
    mat_2004 = matriz_anual(df, 2003, 2004)  # transicao 2003→2004
    total_2004 = mat_2004.sum()
    off_diag_2004 = total_2004 - np.trace(mat_2004)
    taxa_2004 = off_diag_2004 / total_2004

    # Taxas por categoria para P2 e P3
    cats_interesse = ["vegetacao_natural", "pastagem", "agricultura"]
    cat_rows = []
    for cat in cats_interesse:
        k = GRUPOS.index(cat)
        taxas_cat_p2, taxas_cat_p3 = [], []
        for ano in range(ini_p2, fim_p2):
            mat = matriz_anual(df, ano, ano + 1)
            area_cat = mat[k, :].sum()
            perdeu = area_cat - mat[k, k]
            taxas_cat_p2.append(perdeu / area_cat if area_cat > 0 else 0)
        for ano in range(ini_p3, fim_p3):
            mat = matriz_anual(df, ano, ano + 1)
            area_cat = mat[k, :].sum()
            perdeu = area_cat - mat[k, k]
            taxas_cat_p3.append(perdeu / area_cat if area_cat > 0 else 0)

        u, p = stats.mannwhitneyu(taxas_cat_p2, taxas_cat_p3, alternative="two-sided")
        cat_rows.append({
            "categoria": cat,
            "taxa_media_p2": round(np.mean(taxas_cat_p2), 6),
            "taxa_media_p3": round(np.mean(taxas_cat_p3), 6),
            "ratio_p2_p3": round(np.mean(taxas_cat_p2) / np.mean(taxas_cat_p3), 3) if np.mean(taxas_cat_p3) > 0 else float("inf"),
            "U": round(u, 1),
            "p": round(p, 6),
        })

    # Sem 2004 (sera que o outlier domina P2?)
    taxas_p2_sem2004 = taxas_p2[taxas_p2 != taxa_2004] if len(taxas_p2) > 1 else taxas_p2
    u_sem, p_sem = stats.mannwhitneyu(taxas_p2_sem2004, taxas_p3, alternative="two-sided")

    # Com 3 periodos alternativos (P2+P3 fundidos)
    taxas_p2p3 = np.concatenate([taxas_p2, taxas_p3])
    taxas_p1 = []
    ini_p1, fim_p1, _ = periodos["I"]
    for ano in range(ini_p1, fim_p1):
        mat = matriz_anual(df, ano, ano + 1)
        total = mat.sum()
        off_diag = total - np.trace(mat)
        taxas_p1.append(off_diag / total if total > 0 else 0)
    taxas_p1 = np.array(taxas_p1)

    taxas_p4 = []
    ini_p4, fim_p4, _ = periodos["IV"]
    for ano in range(ini_p4, fim_p4):
        mat = matriz_anual(df, ano, ano + 1)
        total = mat.sum()
        off_diag = total - np.trace(mat)
        taxas_p4.append(off_diag / total if total > 0 else 0)
    taxas_p4 = np.array(taxas_p4)

    # KW: 3 periodos (P1, P2+P3, P4) vs 4 periodos (P1, P2, P3, P4)
    h_3, p_3 = stats.kruskal(taxas_p1, taxas_p2p3, taxas_p4)
    h_4, p_4 = stats.kruskal(taxas_p1, taxas_p2, taxas_p3, taxas_p4)

    return {
        "p2_vs_p3": {
            "media_p2": round(taxas_p2.mean(), 6),
            "std_p2": round(taxas_p2.std(), 6),
            "media_p3": round(taxas_p3.mean(), 6),
            "std_p3": round(taxas_p3.std(), 6),
            "ratio_p2_p3": round(taxas_p2.mean() / taxas_p3.mean(), 3),
            "mann_whitney_U": round(u_stat, 1),
            "mann_whitney_p": round(u_p, 6),
            "t_stat": round(t_stat, 3),
            "t_p": round(t_p, 6),
        },
        "outlier_2004": {
            "taxa_2004": round(taxa_2004, 6),
            "media_p2_sem_2004": round(taxas_p2_sem2004.mean(), 6),
            "p2_sem2004_vs_p3_p": round(p_sem, 6),
        },
        "categorias": cat_rows,
        "3_periodos_vs_4_periodos": {
            "descricao": "P1 | P2+P3 fundidos | P4 vs P1 | P2 | P3 | P4",
            "h_3per": round(h_3, 3), "p_3per": round(p_3, 6),
            "h_4per": round(h_4, 3), "p_4per": round(p_4, 6),
        },
    }


# ─────────────────────── Nivel 3: Transicao especifica ───────────────────────

def intensidade_transicao(df: pd.DataFrame, periodos: dict) -> pd.DataFrame:
    """Para cada transicao (i→j) e periodo, calcula intensidade vs uniform."""
    rows = []
    for nome, (ini, fim, _) in periodos.items():
        n_anos = fim - ini
        mat_total = np.zeros((6, 6))
        for ano in range(ini, fim):
            mat_total += matriz_anual(df, ano, ano + 1)

        area_total = mat_total.sum()
        off_diag_total = area_total - np.trace(mat_total)
        taxa_uniform = off_diag_total / area_total / n_anos if area_total > 0 else 0

        for i, orig in enumerate(GRUPOS):
            area_orig = mat_total[i, :].sum()
            for j, dest in enumerate(GRUPOS):
                if i == j:
                    continue
                area_trans = mat_total[i, j]
                # Intensidade da transicao: area / area_orig / n_anos
                intensidade = area_trans / area_orig / n_anos if area_orig > 0 else 0
                rows.append({
                    "periodo": nome,
                    "anos": f"{ini}-{fim}",
                    "origem": orig,
                    "destino": dest,
                    "area_mha": round(area_trans, 4),
                    "intensidade_anual": round(intensidade, 6),
                    "intensidade_vs_uniform": round(intensidade / taxa_uniform, 3) if taxa_uniform > 0 else float("inf"),
                })
    return pd.DataFrame(rows)


# ─────────────────────── Main ───────────────────────

def main():
    print("=" * 70)
    print("INTENSITY ANALYSIS (Aldwaik & Pontius 2012)")
    print("Diagnóstico para periodização: P2 (2001-2005) vs P3 (2006-2019)")
    print("=" * 70)

    df = carregar_transicoes()
    print(f"  Transições carregadas: {len(df):,} linhas")

    periodos = ATOS_FLAT

    # ── Nivel 1: Taxa anual de mudanca ──
    print("\n1. TAXA ANUAL DE MUDANÇA POR PAR DE ANOS")
    print("-" * 50)
    df_taxa = taxa_anual_mudanca(df)
    for _, row in df_taxa.iterrows():
        print(f"  {int(row['ano'])}-{int(row['ano_dest'])}: {row['taxa_anual']:.4f}  "
              f"({row['area_mudou_mha']:.2f} Mha mudou de {row['area_total_mha']:.2f} Mha)")

    # Destaques
    max_row = df_taxa.loc[df_taxa["taxa_anual"].idxmax()]
    min_row = df_taxa.loc[df_taxa["taxa_anual"].idxmin()]
    print(f"\n  Pico: {int(max_row['ano'])}-{int(max_row['ano_dest'])} taxa={max_row['taxa_anual']:.4f}")
    print(f"  Vale: {int(min_row['ano'])}-{int(min_row['ano_dest'])} taxa={min_row['taxa_anual']:.4f}")

    # ── Teste de intervalo ──
    print("\n2. TESTE DE INTERVALO (estacionariedade entre periodos)")
    print("-" * 50)
    resultado_intervalo = teste_intervalo(df_taxa, periodos)
    print(f"  Kruskal-Wallis: H={resultado_intervalo['kruskal_H']:.3f}, p={resultado_intervalo['kruskal_p']:.6f}")
    print(f"  ANOVA: F={resultado_intervalo['anova_F']:.3f}, p={resultado_intervalo['anova_p']:.6f}")
    print("\n  Resumo por periodo:")
    for nome, info in resultado_intervalo["resumo"].items():
        print(f"    {nome} (n={info['n']}): media={info['media']:.6f}, std={info['std']:.6f}")
    print("\n  Comparacoes par-a-par (Mann-Whitney, Bonferroni):")
    for par in resultado_intervalo["pares"]:
        sig = "***" if par["p_bonferroni"] < 0.001 else "**" if par["p_bonferroni"] < 0.01 else "*" if par["p_bonferroni"] < 0.05 else ""
        print(f"    {par['per1']} vs {par['per2']}: ratio={par['ratio']:.3f}, p={par['p_bonferroni']:.6f} {sig}")

    # ── Nivel 2: Intensidade por categoria ──
    print("\n3. INTENSIDADE POR CATEGORIA")
    print("-" * 50)
    df_cat = intensidade_categoria(df, periodos)
    for cat in ["vegetacao_natural", "pastagem", "agricultura"]:
        print(f"\n  {cat}:")
        sub = df_cat[df_cat["categoria"] == cat]
        for _, row in sub.iterrows():
            print(f"    {row['periodo']} ({row['anos']}): "
                  f"perda={row['taxa_perda_anual']:.4f}/a, "
                  f"ganho={row['taxa_ganho_anual']:.4f}/a, "
                  f"uniform={row['taxa_uniform_anual']:.4f}/a, "
                  f"perda/uniform={row['perda_vs_uniform']:.2f}, "
                  f"ganho/uniform={row['ganho_vs_uniform']:.2f}")

    # ── Diagnostico focal P2 vs P3 ──
    print("\n4. DIAGNOSTICO FOCAL: P2 (2001-2005) vs P3 (2006-2019)")
    print("-" * 50)
    diag = diagnostico_p2_p3(df, periodos)

    r = diag["p2_vs_p3"]
    print(f"  Taxa media P2: {r['media_p2']:.6f} (std={r['std_p2']:.6f})")
    print(f"  Taxa media P3: {r['media_p3']:.6f} (std={r['std_p3']:.6f})")
    print(f"  Ratio P2/P3: {r['ratio_p2_p3']:.3f}")
    print(f"  Mann-Whitney: U={r['mann_whitney_U']:.1f}, p={r['mann_whitney_p']:.6f}")
    print(f"  t-test: t={r['t_stat']:.3f}, p={r['t_p']:.6f}")

    o = diag["outlier_2004"]
    print(f"\n  Efeito de 2004 (outlier?):")
    print(f"    Taxa 2004: {o['taxa_2004']:.6f}")
    print(f"    Media P2 sem 2004: {o['media_p2_sem_2004']:.6f}")
    print(f"    P2(sem 2004) vs P3: p={o['p2_sem2004_vs_p3_p']:.6f}")

    print(f"\n  Por categoria:")
    for c in diag["categorias"]:
        sig = "***" if c["p"] < 0.001 else "**" if c["p"] < 0.01 else "*" if c["p"] < 0.05 else ""
        print(f"    {c['categoria']}: P2={c['taxa_media_p2']:.4f}, P3={c['taxa_media_p3']:.4f}, "
              f"ratio={c['ratio_p2_p3']:.2f}, p={c['p']:.4f} {sig}")

    c3 = diag["3_periodos_vs_4_periodos"]
    print(f"\n  3 periodos (P1 | P2+P3 | P4): H={c3['h_3per']:.3f}, p={c3['p_3per']:.6f}")
    print(f"  4 periodos (P1 | P2 | P3 | P4): H={c3['h_4per']:.3f}, p={c3['p_4per']:.6f}")

    # ── Nivel 3: Transicoes-chave ──
    print("\n5. TRANSICOES-CHAVE (intensidade anual por periodo)")
    print("-" * 50)
    df_trans = intensidade_transicao(df, periodos)
    transicoes_chave = [
        ("pastagem", "agricultura"),
        ("pastagem", "vegetacao_natural"),
        ("vegetacao_natural", "pastagem"),
        ("vegetacao_natural", "agricultura"),
    ]
    for orig, dest in transicoes_chave:
        sub = df_trans[(df_trans["origem"] == orig) & (df_trans["destino"] == dest)]
        print(f"\n  {orig} → {dest}:")
        for _, row in sub.iterrows():
            print(f"    {row['periodo']} ({row['anos']}): "
                  f"intensidade={row['intensidade_anual']:.4f}/a, "
                  f"vs_uniform={row['intensidade_vs_uniform']:.2f}x, "
                  f"area={row['area_mha']:.2f} Mha")

    # ── Salvar resultados ──
    DIR_OUT.mkdir(parents=True, exist_ok=True)
    df_taxa.to_csv(DIR_OUT / "intensity_taxas_anuais.csv", index=False)
    df_cat.to_csv(DIR_OUT / "intensity_categorias.csv", index=False)
    df_trans.to_csv(DIR_OUT / "intensity_transicoes.csv", index=False)
    print(f"\nResultados salvos em {DIR_OUT}")

    # ── Conclusao ──
    print("\n" + "=" * 70)
    print("CONCLUSÃO DO DIAGNÓSTICO")
    print("=" * 70)
    p_p2p3 = r['mann_whitney_p']
    if p_p2p3 < 0.05:
        print(f"  P2 e P3 são ESTATISTICAMENTE DIFERENTES (p={p_p2p3:.4f})")
        print(f"  → A fronteira 2005/2006 é justificada: taxas de mudança diferem.")
    else:
        print(f"  P2 e P3 NÃO são estatisticamente diferentes (p={p_p2p3:.4f})")
        print(f"  → A fronteira 2005/2006 é questionável: intensidade de mudança similar.")

    p_sem = o['p2_sem2004_vs_p3_p']
    if p_sem < 0.05:
        print(f"  Mesmo sem 2004, P2≠P3 (p={p_sem:.4f})")
    else:
        print(f"  Sem 2004, P2≈P3 (p={p_sem:.4f}) — outlier 2004 pode estar dominando.")


if __name__ == "__main__":
    main()