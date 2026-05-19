"""verificacao_intensity.py — Testes de sanidade para Intensity Analysis
========================================================================

1. Consistência de dados: matrizes anuais somam para o total correto?
2. Simetria: perda de A→B ≈ ganho de B vindo de A?
3. Poder estatístico: com n=4 (P2), Mann-Whitney é confiável?
4. Sensibilidade da fronteira: e se P2 fosse 2000-2004 ou 2002-2006?
5. Bootstrap: intervalo de confiança para a diferença P2-P3
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

from intensity_analysis import (
    carregar_transicoes, matriz_anual, taxa_anual_mudanca,
    GRUPOS, ATOS_FLAT
)


def teste_consistencia_dados():
    """1. Verifica se as matrizes anuais somam para areas consistentes."""
    df = carregar_transicoes()
    anos = sorted(df["ano_origem"].unique())

    # Ler taxas_lulc para areas de referencia
    df_taxas = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")

    erros = []
    for ano in anos:
        mat = matriz_anual(df, ano, ano + 1)
        total_mat = mat.sum()

        # Area total do ano de origem (soma das areas)
        row_taxas = df_taxas[df_taxas["ano"] == ano]
        if row_taxas.empty:
            continue

        # Soma das 6 classes no ano de origem
        area_total_taxas = sum(
            row_taxas[f"{g}_mha"].values[0]
            for g in GRUPOS
            if f"{g}_mha" in df_taxas.columns
        )

        # Diferenca relativa (matriz de transicao soma 1 ano de pares)
        diff_pct = abs(total_mat - area_total_taxas) / area_total_taxas * 100 if area_total_taxas > 0 else 0
        erros.append({
            "ano": ano,
            "total_matriz_mha": round(total_mat, 4),
            "total_taxas_mha": round(area_total_taxas, 4),
            "diff_pct": round(diff_pct, 4),
        })

    df_erros = pd.DataFrame(erros)
    max_diff = df_erros["diff_pct"].max()
    mean_diff = df_erros["diff_pct"].mean()

    print("1. CONSISTÊNCIA DE DADOS (matriz vs taxas_lulc)")
    print("-" * 60)
    print(f"  Máximo diff: {max_diff:.4f}%")
    print(f"  Média diff: {mean_diff:.4f}%")

    # Checar anos com diff > 1%
    grandes = df_erros[df_erros["diff_pct"] > 1.0]
    if len(grandes) > 0:
        print(f"  ATENÇÃO: {len(grandes)} anos com diff > 1%:")
        for _, row in grandes.iterrows():
            print(f"    {int(row['ano'])}: matriz={row['total_matriz_mha']:.2f}, "
                  f"taxas={row['total_taxas_mha']:.2f}, diff={row['diff_pct']:.2f}%")
    else:
        print("  Todas as diferenças < 1%. Dados consistentes.")

    # Checar: soma de cada linha da matriz ≈ area da classe no ano
    print("\n  Consistência por classe (linha da matriz ≈ estoque do ano):")
    for ano in [2000, 2005, 2010, 2020]:
        mat = matriz_anual(df, ano, ano + 1)
        row_taxas = df_taxas[df_taxas["ano"] == ano]
        if row_taxas.empty:
            continue
        for k, g in enumerate(GRUPOS[:3]):  # veg, past, agric
            if f"{g}_mha" in df_taxas.columns:
                estoque = row_taxas[f"{g}_mha"].values[0]
                soma_linha = mat[k, :].sum()
                diff = abs(soma_linha - estoque)
                if ano == 2000:  # print header only once
                    print(f"    {'Classe':<20} {'Ano':>4} {'Soma_linha':>10} {'Estoque':>10} {'Diff':>8}" if g == GRUPOS[0] and ano == 2000 else "")
                print(f"    {g:<20} {ano:>4} {soma_linha:>10.3f} {estoque:>10.3f} {diff:>8.3f}")

    return max_diff < 5.0  # tolerancia de 5%


def teste_simetria():
    """2. Perda de A→B ≈ ganho de B vindo de A? (consistência de estoques)."""
    df = carregar_transicoes()

    print("\n2. SIMETRIA: perda(A→B) ≈ estoque_A(t) - estoque_A(t+1) + ganho(B→A)?")
    print("-" * 60)

    # Para 3 pares de anos, verificar que a variação líquida das taxas
    # é consistente com a diferença de estoques
    df_taxas = pd.read_csv(DIR_DATA / "taxas_lulc_goias.csv")

    anos_teste = [1990, 2000, 2010, 2020]
    for ano in anos_teste:
        mat = matriz_anual(df, ano, ano + 1)
        row_t0 = df_taxas[df_taxas["ano"] == ano]
        row_t1 = df_taxas[df_taxas["ano"] == ano + 1]

        if row_t0.empty or row_t1.empty:
            continue

        print(f"\n  Ano {ano}→{ano+1}:")
        for g in ["vegetacao_natural", "pastagem", "agricultura"]:
            if f"{g}_mha" not in df_taxas.columns:
                continue
            estoque_t0 = row_t0[f"{g}_mha"].values[0]
            estoque_t1 = row_t1[f"{g}_mha"].values[0]
            variacao_liquida = estoque_t1 - estoque_t0

            # Da matriz: ganho líquido = coluna - diagonal - (linha - diagonal)
            k = GRUPOS.index(g)
            ganho = mat[:, k].sum() - mat[k, k]  # entrou
            perda = mat[k, :].sum() - mat[k, k]  # saiu
            variacao_matriz = ganho - perda

            diff = abs(variacao_liquida - variacao_matriz)
            print(f"    {g}: delta_taxas={variacao_liquida:+.4f}, "
                  f"delta_matriz={variacao_matriz:+.4f}, "
                  f"diff={diff:.4f}")


def teste_poder_estatistico():
    """3. Com n=4 (P2), Mann-Whitney é confiável?
    Simulação: gerar dados sob H0 e verificar taxa de falso positivo.
    """
    print("\n3. PODER ESTATÍSTICO (Mann-Whitney com n pequeno)")
    print("-" * 60)

    np.random.seed(42)

    # Falso positivo: duas amostras da mesma distribuição
    n_sim = 10000
    n_small = 4  # P2
    n_large = 13  # P3

    fpr_005 = 0
    fpr_010 = 0
    for _ in range(n_sim):
        a = np.random.randn(n_small)
        b = np.random.randn(n_large)
        _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        if p < 0.05:
            fpr_005 += 1
        if p < 0.10:
            fpr_010 += 1

    print(f"  FPR nominal α=0.05: observado={fpr_005/n_sim:.4f} (esperado ≈0.05)")
    print(f"  FPR nominal α=0.10: observado={fpr_010/n_sim:.4f} (esperado ≈0.10)")

    # Poder para detectar diferença do tamanho observado (ratio ~1.25)
    # P2 media=0.014, P3 media=0.011, pooled std ≈0.002
    # Cohen's d ≈ (0.014-0.011)/0.002 = 1.5 (grande)
    # Mas com n=4, o poder é limitado
    poder_005 = 0
    poder_010 = 0
    mu1, mu2 = 0.014, 0.011
    sigma = 0.002
    for _ in range(n_sim):
        a = np.random.normal(mu1, sigma, n_small)
        b = np.random.normal(mu2, sigma, n_large)
        _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        if p < 0.05:
            poder_005 += 1
        if p < 0.10:
            poder_010 += 1

    print(f"\n  Poder para detectar ratio 1.25 (d≈1.5):")
    print(f"    α=0.05: poder={poder_005/n_sim:.4f}")
    print(f"    α=0.10: poder={poder_010/n_sim:.4f}")

    # Com mais anos em P2 (se fosse n=7 em vez de n=4)
    poder_005_n7 = 0
    for _ in range(n_sim):
        a = np.random.normal(mu1, sigma, 7)
        b = np.random.normal(mu2, sigma, n_large)
        _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        if p < 0.05:
            poder_005_n7 += 1

    print(f"  Poder com n=7 (se P2 tivesse 7 anos):")
    print(f"    α=0.05: poder={poder_005_n7/n_sim:.4f}")


def teste_sensibilidade_fronteira():
    """4. Sensibilidade: e se a fronteira fosse 2004, 2006 ou 2007 em vez de 2005?"""
    df = carregar_transicoes()
    df_taxa = taxa_anual_mudanca(df)

    print("\n4. SENSIBILIDADE DA FRONTEIRA (P2/P3)")
    print("-" * 60)

    alternativas = [2003, 2004, 2005, 2006, 2007]
    resultados = []

    for corte in alternativas:
        # P2: 2001 até corte, P3: corte até 2019
        taxas_p2 = df_taxa[(df_taxa["ano"] >= 2001) & (df_taxa["ano"] < corte)]["taxa_anual"].values
        taxas_p3 = df_taxa[(df_taxa["ano"] >= corte) & (df_taxa["ano"] < 2019)]["taxa_anual"].values

        if len(taxas_p2) < 2 or len(taxas_p3) < 2:
            continue

        u, p = stats.mannwhitneyu(taxas_p2, taxas_p3, alternative="two-sided")
        t, p_t = stats.ttest_ind(taxas_p2, taxas_p3)

        resultados.append({
            "corte": corte,
            "n_p2": len(taxas_p2),
            "n_p3": len(taxas_p3),
            "media_p2": taxas_p2.mean(),
            "media_p3": taxas_p3.mean(),
            "ratio": taxas_p2.mean() / taxas_p3.mean() if taxas_p3.mean() > 0 else float("inf"),
            "MW_p": p,
            "t_p": p_t,
        })

    print(f"  {'Corte':>5} {'n_P2':>4} {'n_P3':>4} {'média_P2':>9} {'média_P3':>9} {'ratio':>6} {'MW p':>8} {'t p':>8}")
    for r in resultados:
        sig = "***" if r["MW_p"] < 0.01 else "**" if r["MW_p"] < 0.05 else "*" if r["MW_p"] < 0.10 else ""
        print(f"  {r['corte']:>5} {r['n_p2']:>4} {r['n_p3']:>4} "
              f"{r['media_p2']:>9.6f} {r['media_p3']:>9.6f} {r['ratio']:>6.3f} "
              f"{r['MW_p']:>8.4f} {r['t_p']:>8.4f} {sig}")

    print("\n  Interpretação: se o resultado muda drasticamente com o ponto de corte,")
    print("  a fronteira é sensível à escolha. Se é estável, é robusta.")


def teste_bootstrap_diferenca():
    """5. Bootstrap: intervalo de confiança para a diferença P2-P3."""
    df = carregar_transicoes()
    df_taxa = taxa_anual_mudanca(df)

    print("\n5. BOOTSTRAP: IC para diferença P2-P3")
    print("-" * 60)

    taxas_p2 = df_taxa[(df_taxa["ano"] >= 2001) & (df_taxa["ano"] < 2005)]["taxa_anual"].values
    taxas_p3 = df_taxa[(df_taxa["ano"] >= 2006) & (df_taxa["ano"] < 2019)]["taxa_anual"].values

    np.random.seed(42)
    n_boot = 10000
    diffs = []
    diffs_sem2004 = []

    for _ in range(n_boot):
        b2 = np.random.choice(taxas_p2, size=len(taxas_p2), replace=True)
        b3 = np.random.choice(taxas_p3, size=len(taxas_p3), replace=True)
        diffs.append(b2.mean() - b3.mean())

    # Sem 2004
    taxas_p2_sem2004 = taxas_p2[taxas_p2 != taxas_p2.max()]  # remove o max (2004)
    if len(taxas_p2_sem2004) < 2:
        taxas_p2_sem2004 = taxas_p2  # fallback

    for _ in range(n_boot):
        b2 = np.random.choice(taxas_p2_sem2004, size=len(taxas_p2_sem2004), replace=True)
        b3 = np.random.choice(taxas_p3, size=len(taxas_p3), replace=True)
        diffs_sem2004.append(b2.mean() - b3.mean())

    diffs = np.array(diffs)
    diffs_sem2004 = np.array(diffs_sem2004)

    ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
    ci_low_s, ci_high_s = np.percentile(diffs_sem2004, [2.5, 97.5])

    print(f"  Diferença observada P2-P3: {taxas_p2.mean() - taxas_p3.mean():.6f}")
    print(f"  IC 95% (bootstrap): [{ci_low:.6f}, {ci_high:.6f}]")
    print(f"  Contém zero? {'NÃO' if ci_low > 0 or ci_high < 0 else 'SIM'}")

    print(f"\n  Sem 2004:")
    print(f"  Diferença observada: {taxas_p2_sem2004.mean() - taxas_p3.mean():.6f}")
    print(f"  IC 95% (bootstrap): [{ci_low_s:.6f}, {ci_high_s:.6f}]")
    print(f"  Contém zero? {'NÃO' if ci_low_s > 0 or ci_high_s < 0 else 'SIM'}")

    # Por categoria (veg_nat)
    print(f"\n  IC para diferença P2-P3 (veg_natural perda/anual):")
    perdas_p2, perdas_p3 = [], []
    for ano in range(2001, 2005):
        mat = matriz_anual(df, ano, ano + 1)
        k = GRUPOS.index("vegetacao_natural")
        area_cat = mat[k, :].sum()
        perdeu = area_cat - mat[k, k]
        perdas_p2.append(perdeu / area_cat if area_cat > 0 else 0)
    for ano in range(2006, 2019):
        mat = matriz_anual(df, ano, ano + 1)
        k = GRUPOS.index("vegetacao_natural")
        area_cat = mat[k, :].sum()
        perdeu = area_cat - mat[k, k]
        perdas_p3.append(perdeu / area_cat if area_cat > 0 else 0)

    perdas_p2 = np.array(perdas_p2)
    perdas_p3 = np.array(perdas_p3)
    diffs_veg = []
    for _ in range(n_boot):
        b2 = np.random.choice(perdas_p2, size=len(perdas_p2), replace=True)
        b3 = np.random.choice(perdas_p3, size=len(perdas_p3), replace=True)
        diffs_veg.append(b2.mean() - b3.mean())

    diffs_veg = np.array(diffs_veg)
    ci_low_v, ci_high_v = np.percentile(diffs_veg, [2.5, 97.5])
    print(f"  Diferença: {perdas_p2.mean() - perdas_p3.mean():.6f}")
    print(f"  IC 95%: [{ci_low_v:.6f}, {ci_high_v:.6f}]")
    print(f"  Contém zero? {'NÃO' if ci_low_v > 0 or ci_high_v < 0 else 'SIM'}")


def main():
    print("=" * 70)
    print("VERIFICAÇÃO DE SANIDADE — INTENSITY ANALYSIS")
    print("=" * 70)

    ok = teste_consistencia_dados()
    teste_simetria()
    teste_poder_estatistico()
    teste_sensibilidade_fronteira()
    teste_bootstrap_diferenca()

    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    print("1. Dados: matrizes consistentes com estoques? (ver acima)")
    print("2. Simetria: variações líquidas consistentes? (ver acima)")
    print("3. Poder: Mann-Whitney com n=4 é confiável? (ver acima)")
    print("4. Fronteira: resultado muda se cortar em 2003/2004/2006/2007? (ver acima)")
    print("5. Bootstrap: IC da diferença P2-P3 contém zero? (ver acima)")


if __name__ == "__main__":
    main()