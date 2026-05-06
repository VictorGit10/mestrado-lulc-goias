# Pipeline #8 — Crédito rural × Uso da terra

**Script**: `scripts/analise_credito_uso_terra.py`
**Quando foi feito**: 2026-04-27 (corrigido e regerado em 2026-05-05).
**Depende de**: Pipelines #3, #4, #5, #6.
**Outputs**: 7 PNGs (12–18) + 3 CSVs. Ver [graficos_descritivos.md](../outputs/graficos_descritivos.md) e [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## Correção de 2026-05-05 — bug de alinhamento por índice no PIB

A versão original do `painel_credito_lulc.csv` (gerada em 2026-04-27) continha valores de `pib_real_rs` **embaralhados entre municípios** — Goiânia recebeu PIB de cidade pequena (R$ 240 M em vez de ~R$ 70 bi); Cachoeira de Goiás recebeu PIB de cidade grande (R$ 3,3 bi em vez de ~R$ 36 M). A divergência mediana com o painel #16 era ~5%, mas std=12 e razões individuais entre 0,003× e 96×.

**Causa-raiz**: em `gerar_painel_credito_lulc`, o filtro `df_pib[df_pib["ano"] >= 2013]` mantém os índices originais esparsos (ex.: `[11, 12, 13, ...]`); a função `deflacionar()` faz merge interno e retorna Series com índice `[0, 1, ...]`; a atribuição `pib["pib_real_rs"] = deflacionar(...)` alinha por índice no pandas, embaralhando os valores. Os Pipelines #1, #2 e #16 não tinham o bug porque usam dataframes que já saem dos loaders com `reset_index(drop=True)` aplicado e não fazem filtro temporal antes da deflação.

**Fix aplicado**: `.reset_index(drop=True)` no filtro do `pib`. Pipeline regenerado, auditoria empírica em `outputs/diagnosticos/auditoria_pib_ratio.csv` confirma razão pib_8/pib_16 = 1,000 ± 0,000 em 1.352 linhas comparáveis. Diagnóstico via `scripts/auditoria_pib.py`.

## O que faz

Cruza dados de crédito rural (SICOR/BACEN) com mudança de uso da terra (MapBiomas) nos 246 (245 no SICOR) municípios de Goiás. Janela de sobreposição: 2013–2023. Valores deflacionados para R$ de dez/2024 via IPCA — ver [metodologia/deflacao_ipca.md](../metodologia/deflacao_ipca.md).

## Gráficos produzidos

(7 PNGs, 12–18 — descrições completas em [graficos_descritivos.md](../outputs/graficos_descritivos.md)):

| # | Gráfico | Tipo | Descrição |
|---|---|---|---|
| 12 | `12_credito_uf_serie_2013-2024.png` | Barras empilhadas | Crédito por finalidade (Custeio/Invest/Comerc) 2013–2026, R$ bi deflacionados |
| 13 | `13_scatter_credito_pastagem.png` | Scatter colorido | Crédito/ha pastagem vs Δpastagem, cor = intensidade_soja |
| 14 | `14_composicao_produto_credito.png` | Multi-linha | Top 10 produtos + "Outros", 2013–2023 |
| 15 | `15_scatter_credito_soja.png` | Scatter bolha | Crédito total vs Δsoja, bolha = pastagem 1985, inclui Pearson r |
| 16 | `16_barras_credito_intensidade.png` | Barras horiz. 2-painel | Top 20 munis por crédito/ha pastagem (2023), Custeio vs Invest |
| 17 | `17_evolucao_credito_pastagem.png` | 2-painel | (a) Eixo duplo: pastagem Mha + crédito R$ bi; (b) Correlação anual |
| 18 | `18_scatter_credito_censo_agro.png` | Scatter com quadrantes | % familiar vs crédito/ha, cor = intensidade_soja |

## CSVs produzidos

| Arquivo | Conteúdo | Linhas |
|---|---|---|
| `credito_municipal_anual.csv` | (ano, cd_mun) com valor_custeio_real, valor_investimento_real, valor_total_real, credito_por_ha_pastagem | ~3.424 |
| `credito_produto_anual.csv` | (ano, nm_produto) com valor_real, n_contratos | ~1.713 |
| `painel_credito_lulc.csv` | Merge crédito + pastagem/soja + PIB 2013–2023 | ~2.692 |

## Como rodar

```bash
python analise_credito_uso_terra.py
```

(após Pipelines #3, #4, #5, #6).

## Decisões metodológicas

- Valores nominais deflacionados via IPCA (dez/2024) — mesmo deflator dos Pipelines #1 e #2.
- Crédito agregado por (ano, cd_mun, finalidade) — colapsa programa, atividade, modalidade.
- `credito_por_ha_pastagem = valor_total_real / pastagem_ha` — onde pastagem_ha > 0.
- 2025–2026 marcados como "(parcial)" no gráfico UF; excluídos dos scatters.
- Valparaíso de Goiás ausente do SICOR (sem código BACEN) — NaN tratado como 0 no merge.

## Limitações

- SICOR só cobre 2013+ — não há série histórica longa de crédito municipal.
- Crédito/ha mistura precisão de dois sistemas independentes (SICOR financeiro vs MapBiomas raster).
- Correlações são ecológicas (não causais) — painel de regressão espacial fica para etapa futura.
