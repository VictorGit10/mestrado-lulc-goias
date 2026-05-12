# Pipeline #22 — Correlações painel municipal (2-way FE)

**Script**: `scripts/correlacoes_painel.py`
**Status**: ✅ executado
**Depende de**: #17 (`taxas_lulc_municipal.csv`), #16 (`painel_unificado.parquet`)

## O que faz

Regressão em painel com efeitos fixos de entidade (município) e tempo (ano) para associar mudanças LULC a mudanças socioeconômicas no nível municipal.

**Decisão D8**: `PanelOLS` com `entity_effects + time_effects`, SE clusterizado por município.

**Especificação**: Δlulc_it = α_i + γ_t + β·Δx_it + ε_it

## Janelas

| Janela | Obs típico | Variáveis disponíveis |
|--------|-----------|----------------------|
| 2013–2021 (plena) | ~1.956–2.214 | LULC + pecuária + PIB + SICOR |
| 2002–2023 (estendida) | ~2.444–5.412 | LULC + pecuária + PIB (sem SICOR) |

## Pares testados

| Y (Δ LULC) | X (Δ socioeconômico) | Rótulo |
|------------|---------------------|--------|
| Δ Pastagem | Δ SICOR crédito rural | Crédito rural × pastagem |
| Δ Pastagem | Δ Bovinos | Rebanho × pastagem |
| Δ Pastagem | Δ VA agropecuária | VA agro × pastagem |
| Δ Veg. natural | Δ Fogo veg. nativa | Fogo × vegetação natural |
| Δ Veg. natural | Δ PIB real | PIB × vegetação natural |
| Δ Agricultura | Δ Produção soja | Soja × agricultura |
| Δ Agricultura | Δ SICOR crédito rural | Crédito rural × agricultura |
| Δ Agricultura | Δ VA agropecuária | VA agro × agricultura |

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `outputs/correlacoes/painel_2fe.csv` | Tabela com 16 modelos: β, SE, p, R² within, n_obs |
| `outputs/correlacoes/painel_residuos.csv` | Resíduos para futura análise espacial (Moran's I) |

## Resultados principais

6 de 16 modelos significativos a 5%:

| Y | X | Janela | β | p | R² within | Interpretação |
|---|---|--------|---|---|-----------|---------------|
| Δ Pastagem | Δ SICOR | 2013–2021 | −0,0034 | 0,0000 | 0,049 | Crédito rural associado a retração de pastagem (possível transição para agricultura) |
| Δ Pastagem | Δ SICOR | 2002–2023 | −0,0029 | 0,0000 | 0,030 | Robusto na janela estendida |
| Δ Pastagem | Δ Bovinos | 2002–2023 | ≈0 | 0,0042 | 0,021 | Significativo mas efeito praticamente nulo |
| Δ Pastagem | Δ VA agro | 2013–2021 | −0,0015 | 0,0334 | 0,022 | Crescimento do VA agro → retração de pastagem |
| Δ Agricultura | Δ VA agro | 2013–2021 | −0,0035 | 0,0000 | 0,105 | VA cresce sem expansão de área → intensificação |
| Δ Agricultura | Δ VA agro | 2002–2023 | −0,0040 | 0,0000 | 0,047 | Robusto na janela estendida |

**Conclusão**: o sinal negativo Δ Agricultura × Δ VA agro é o achado mais robusto — sugere que o crescimento do valor adicionado agropecuário em Goiás se dá por intensificação (produtividade), não por expansão de área. Os R² within baixos (0–10%) são esperados para modelos bivariados com alta heterogeneidade municipal.

## Como rodar

```bash
pip install linearmodels
python scripts/correlacoes_painel.py
```

Sem argumentos. Requer `linearmodels` instalado.