# Pipeline #15 — Milho 1ª e 2ª safra (SIDRA 839)

**Coleta**: `scripts/coleta_sidra.py --so 839`
**Análise**: `scripts/analise_safrinha.py` (concluída em 2026-05-05)
**Depende de**: nenhum (compartilha mecanismo do Pipeline #3).
**Outputs**:
- `data/processed/sidra_pam839_milho_safras.csv` (43.297 linhas)
- `data/processed/painel_safrinha_municipal.csv` (246 munis × métricas cross-section)
- `data/processed/evolucao_safrinha_estado.csv` (22 anos × área 1ª/2ª/total)
- 5 PNGs em `outputs/analises/` (19–23)

## O que faz

Coleta dados municipais de área e produção de milho 1ª safra (verão) e 2ª safra (safrinha/inverno) via SIDRA tabela 839, 2003–2024, 246 municípios.

## Por que tabela 839 e não 1618 (LSPA)

Tabela **1618 (LSPA)** NÃO tem dados municipais — só nível UF. A tabela municipal correta para safrinha é **SIDRA 839**, que separa explicitamente milho 1ª e 2ª safra desde 2003.

## Por que importa

A intensificação agrícola via 2ª safra é o que o MapBiomas mistura num único pixel "Soja" ou "Lavoura" — porque o sensoriamento captura a cobertura no momento, não a sequência de cultivos. Separar safrinha permite distinguir:

- Município "novo" (1 safra/ano, expansão de área)
- Município "intensificado" (2 safras/ano na mesma área)

Diferencial analítico que poucos estudos LULC exploram.

## Como rodar

```bash
python scripts/coleta_sidra.py --so 839
```

## Status atual

- ✅ Dados coletados.
- ✅ Análise descritiva e gráficos (concluído 2026-05-05).

## Achados principais (2003 → 2024)

- **Munis com 2ª safra reportada**: 28 em 2003 → 166 em 2024 (×6).
- **Top 5 por expansão absoluta da safrinha (Δárea 2003→2024)**:
  - Rio Verde +302 mil ha
  - Jataí +180,8 mil ha
  - Mineiros +100 mil ha
  - Montividiu +88 mil ha
  - Cristalina +86,1 mil ha
- Estes 5 municípios concentram a maior parte da intensificação safrinheira; o sudoeste goiano (Rio Verde / Jataí / Mineiros) emerge como núcleo da segunda safra.

## Gráficos produzidos (5 PNGs, 19–23)

| # | Arquivo | Tipo | Descrição |
|---|---|---|---|
| 19 | `19_evolucao_safras_estado.png` | Série temporal | Área plantada anual: 1ª safra, 2ª safra (safrinha) e total — 2003–2024, soma estadual |
| 20 | `20_top10_safrinha_municipal.png` | Small multiples 2×5 | Top 10 munis por Δmilho2 — duas linhas por painel (1ª e 2ª safra) |
| 21 | `21_scatter_safras_municipal.png` | Scatter colorido | Δmilho1 (X) vs Δmilho2 (Y); cor = razão milho2/milho1 (log); tamanho = produção 2024 |
| 22 | `22_barras_top20_intensificacao.png` | Barras horiz. 2-painel | (a) top 20 expansão absoluta safrinha; (b) top 20 razão milho2/milho1 |
| 23 | `23_heatmap_safrinha_periodos.png` | Heatmap | Top 40 munis × 4 períodos (2003-08, 09-13, 14-18, 19-24): área média anual da 2ª safra |

## Como rodar

```bash
python scripts/coleta_sidra.py --so 839     # coleta (uma vez)
python scripts/analise_safrinha.py           # gera painel + 5 gráficos
```

## Integração

Mesclado ao painel unificado (Pipeline #16) — colunas `agri_milho1_*` e `agri_milho2_*` (área + toneladas).
