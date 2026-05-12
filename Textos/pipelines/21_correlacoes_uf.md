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
| `outputs/correlacoes/uf_deltas.csv` | Tabela com 36 pares: pearson_r, pearson_p, spearman_rho, spearman_p, n_obs |
| `outputs/correlacoes/uf_scatter_*.png` | 6 scatter plots com reta de regressão HAC |

## Resultados principais

Apenas 1 par significativo a 5% (36 testados):

| Par | Métrica | Lag | r | p | Interpretação |
|-----|---------|-----|---|---|---------------|
| Δ Agricultura × Δ Soja (ton) | delta vs delta | 0 | −0,303 | 0,022 | Anos de expansão agrícola não coincidem com saltos de produção sojeira (composição de culturas ou efeito área vs produtividade) |

**Limitação**: N = 11 para pares com SICOR (janela 2013–2023), insuficiente para detectar efeitos moderados.

## Como rodar

```bash
python scripts/correlacoes_uf.py
```

Sem argumentos. Usa `taxas_lulc_goias.csv` e `painel_unificado.parquet`.