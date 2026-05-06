# Pipeline #5 — Análise pastagem ↔ soja municipal (proxy)

**Script**: `scripts/analise_pastagem_soja.py`
**Quando foi feito**: 2026-04-26 (sessão anterior).
**Depende de**: Pipelines #3 e #4.
**Outputs**: 7 CSVs em `data/processed/` + 5 PNGs (07–11). Ver [graficos_descritivos.md](../outputs/graficos_descritivos.md) e [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## O que faz

Quantifica a transição pastagem ↔ soja nos 246 municípios de Goiás entre 1985 e 2024. **Não é** matriz de transição pixel-a-pixel (isso depende do MapBiomas via GEE — ver Pipeline #12) — é uma análise **por proxy** que cruza os estoques anuais de área (Pipeline #4) com a série da PAM (Pipeline #3) para validar e produzir métricas de conversão municipais.

## Métricas calculadas por município

(em `painel_pastagem_soja_municipal.csv`, 1 linha por município):

- `delta_pastagem_ha` = pastagem(2024) − pastagem(1985)
- `delta_soja_ha` = soja(2024) − soja(1985)
- `taxa_conversao` = Δsoja / |Δpastagem|, **só quando** Δpastagem < 0 — interpreta-se como "fração da pastagem perdida que virou soja"
- `intensidade_soja` = Δsoja / pastagem(1985) — expansão relativa ao estoque inicial
- `participacao_soja_2024` = soja / (soja + pastagem) em 2024

**Períodos analíticos** (em `transicao_pastagem_soja_periodos.csv`):
1985–1995 (expansão inicial), 1995–2005 (consolidação), 2005–2015 (intensificação), 2015–2024 (recente). Mesmas métricas, recalculadas em cada janela.

## Validações realizadas

1. **Batimental UF** (soma municipal × série UF antiga): max |Δ| < 0,01% — confirma idempotência do pivot.
2. **MapBiomas vs SIDRA (área de soja, par-a-par por município/ano)**: salvo em `validacao_soja_mapbiomas_sidra.csv`. Correlação Pearson ≥ ~0,99 nos anos com cobertura SIDRA razoável (a partir de 2000); razão mediana MapBiomas/SIDRA ≈ 1,0–1,1 (MapBiomas captura área de segunda safra que SIDRA registra como milho).

## Como rodar

```bash
python analise_pastagem_soja.py
```

(após Pipelines #3 e #4).

## Limitações

- **Não é matriz de transição real**. Apenas confronta estoques (pastagem em t e soja em t+1). Pode haver migração indireta (pastagem → cerrado em regeneração → soja) que não vira "conversão direta" pelo cálculo.
- **`taxa_conversao` é interpretativa, não causal**. Um município pode ter perdido pastagem para vegetação e simultaneamente ganhado soja a partir de cerrado — numerador e denominador não são pareados pixel-a-pixel.
- **A matriz de transição verdadeira** (asset MapBiomas de transição via GEE, com classe-origem × classe-destino por par de anos) está implementada no Pipeline #12.
