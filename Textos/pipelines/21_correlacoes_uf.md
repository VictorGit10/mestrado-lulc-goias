# Pipeline #21 — Correlações UF (primeiras diferenças)

**Script**: `scripts/correlacoes_uf.py`
**Status**: ✅ executado
**Depende de**: #17 (`taxas_lulc_goias.csv`), #16 (`painel_unificado.parquet`)

## O que faz

Correlaciona métricas de variação LULC (slope_5a_trail e delta_mha) com variáveis socioeconômicas em primeiras diferenças, no nível estadual (UF).

**Decisão D7**: todas as correlações em primeiras diferenças, nunca em níveis.

## Pares testados

| LULC | Socioeconômica | Rótulo Y | Rótulo X |
|------|---------------|----------|----------|
| Pastagem | SICOR crédito rural | Slope pastagem (Mha/ano) | Δ Crédito rural (R$ bi) |
| Pastagem | Bovinos | Slope pastagem (Mha/ano) | Δ Bovinos (mil cab) |
| Veg. natural | Fogo veg. nativa | Slope veg. nativa (Mha/ano) | Δ Fogo veg. nat. (kha) |
| Veg. natural | PIB real | Slope veg. nativa (Mha/ano) | Δ PIB (R$ bi) |
| Agricultura | Soja (ton) | Slope agricultura (Mha/ano) | Δ Produção soja (kton) |
| Agricultura | SICOR crédito rural | Slope agricultura (Mha/ano) | Δ Crédito rural (R$ bi) |

Para cada par: slope LULC × Δ socioeconômico e Δ LULC × Δ socioeconômico, com lags 0, 1, 2.

## Inferência

- **Pearson + HAC** (Newey-West, maxlags=2) via `statsmodels.OLS`
- **Spearman** como robustez não-paramétrica

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `outputs/correlacoes/uf_deltas.csv` | Tabela com 36 pares: pearson_r, pearson_p, **pearson_p_fdr** (Benjamini-Hochberg), spearman_rho, spearman_p, n_obs |
| `outputs/correlacoes/uf_scatter_*.png` | 6 scatter plots com reta de regressão HAC |

## Resultados principais

Dos **36 pares** testados, **2** cruzam p<0,05 sem correção — mas isso é **exatamente o esperado por acaso**: com 36 testes a α=0,05, ~1,8 falso-positivo é o previsto sob H0.

| Par | Métrica | Lag | r | p | q (FDR-BH) |
|-----|---------|-----|---|---|-----------|
| Δ Agricultura × Δ Soja (ton) | delta vs delta | 0 | −0,303 | 0,022 | 0,585 |
| Δ Veg. natural × Δ PIB real | delta vs delta | 1 | +0,317 | 0,047 | 0,585 |

**Nenhum par sobrevive à correção de multiplicidade (Benjamini-Hochberg): q ≈ 0,59 em ambos, muito acima de 0,05.**

**Leitura correta — este pipeline é evidência _negativa_.** No nível UF e em primeiras diferenças, **nenhuma** associação LULC×socioeconômica robusta emerge. O r=−0,303 **não** deve ser lido substantivamente: a hipótese "composição de culturas / efeito área vs produtividade" seria super-leitura de ruído — 1 a 2 hits em 36 é o piso do acaso, não um achado. A **ausência** de sinal ao nível estadual é, ela própria, o resultado, e é o que motiva descer ao **painel municipal (#22)**, onde há N (246 munis × anos) para detectar efeitos moderados que o agregado UF (N=11–39, série curta) não alcança.

**Limitação**: N = 11 para pares com SICOR (janela 2013–2023) e N = 11–39 nos demais — série curta em que o regime assintótico do Pearson+HAC é frágil e um único outlier move o r. Poder baixo para efeitos moderados; a leitura defensável é a ausência de associação forte, não a estimativa pontual de nenhum r individual.

## Como rodar

```bash
python scripts/correlacoes_uf.py
```

Sem argumentos. Usa `taxas_lulc_goias.csv` e `painel_unificado.parquet`.