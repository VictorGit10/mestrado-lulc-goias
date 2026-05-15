# Pipelines — índice

23 pipelines documentados. Cada arquivo descreve **processo** (o que faz, como rodar, decisões metodológicas, validações, limitações). Para descrição dos **produtos** (PNGs, CSVs com interpretação para redação), ver [outputs/](../outputs/).

## Tabela resumo

| # | Arquivo | Script | Foco | Período | Nível | Status |
|---|---|---|---|---|---|---|
| 1 | [01_pastagem_pib.md](01_pastagem_pib.md) | `grafico_pastagem_pib_goias.py` | Pastagem × PIB UF | 1985–2024 | Estado (GO) | ✅ |
| 2 | [02_analise_expandida.md](02_analise_expandida.md) | `analise_expandida_goias.py` | Cobertura, rebanho, lotação, PIB agro | 1985–2024 | Estado (GO) | ✅ |
| 3 | [03_coleta_sidra.md](03_coleta_sidra.md) | `coleta_sidra.py` | 8 tabelas SIDRA municipais | Variável | Municipal | ✅ |
| 4 | [04_mapbiomas_municipal.md](04_mapbiomas_municipal.md) | `pipeline_municipal.py` | MapBiomas Col 10.1 municipal | 1985–2024 | Municipal | ✅ |
| 5 | [05_pastagem_soja.md](05_pastagem_soja.md) | `analise_pastagem_soja.py` | Transição pastagem ↔ soja (proxy) | 1985–2024 | Municipal | ✅ |
| 6 | [06_sicor.md](06_sicor.md) | `coleta_sicor.py` | Crédito rural SICOR/BACEN | 2013–2026 | Municipal | ✅ |
| 7 | [07_censo_agro.md](07_censo_agro.md) | `coleta_sidra.py --censo-agro` | Censo Agro 2017 (7 tabelas) | 2017 | Municipal | ✅ |
| 8 | [08_credito_lulc.md](08_credito_lulc.md) | `analise_credito_uso_terra.py` | Crédito × uso da terra | 2013–2023 | Municipal | ✅ |
| 9 | [09_mapas_coropleticos.md](09_mapas_coropleticos.md) | `gerar_mapas_lulc_40anos.py` | 40 mapas coropléticos | 1985–2024 | Municipal | ✅ |
| 10 | [10_mapas_gee.md](10_mapas_gee.md) | `gerar_mapas_lulc_gee_40anos.py` | 40 mapas raster GEE 30m | 1985–2024 | Estado (raster) | ✅ |
| 11 | [11_gif_lulc.md](11_gif_lulc.md) | `gerar_gif_lulc.py` | GIF animado 40 anos | 1985–2024 | Estado | ✅ |
| 12 | [12_transicoes.md](12_transicoes.md) | `transicoes_mapbiomas.py` | Matrizes pixel-a-pixel via GEE | 1985–2024 | Municipal | ✅ |
| 13 | [13_idhm.md](13_idhm.md) | `coleta_idhm.py` | IDH-M (IPEA API) | 1991/2000/2010 | Municipal | ✅ (pós-2010 inexistente) |
| 14 | [14_fogo.md](14_fogo.md) | `fogo_mapbiomas.py` | Área queimada × LULC via GEE | 1985–2024 | Municipal | ✅ |
| 15 | [15_safrinha.md](15_safrinha.md) | `coleta_sidra.py --so 839` | Milho 1ª/2ª safra | 2003–2024 | Municipal | ✅ (sem análise gráfica) |
| 16 | [16_painel_unificado.md](16_painel_unificado.md) | `construir_painel_unificado.py` | Painel wide 9.840 × 66 | 1985–2024 | Municipal | ✅ |
| 17 | [17_taxas_lulc.md](17_taxas_lulc.md) | `calcular_taxas_lulc.py` | Taxas de variação LULC (slope, delta, aceleração) | 1985–2024 | UF, muni, meso | ✅ |
| 18 | [18_mesorregioes.md](18_mesorregioes.md) | `mapeamento_mesorregioes.py` | Mapeamento cd_mun → mesorregião IBGE 2017 | — | Municipal | ✅ |
| 19 | [19_conversoes_brutas.md](19_conversoes_brutas.md) | `agregar_conversoes.py` | Transições brutas ano-a-ano (A→B) | 1985–2024 | UF, muni | ✅ |
| 20 | [20_figuras_taxas.md](20_figuras_taxas.md) | `figuras_taxas.py` | 7 figuras de taxas (slope, delta, aceleração, mapas) | 1985–2024 | UF, muni, meso | ✅ |
| 21 | [21_correlacoes_uf.md](21_correlacoes_uf.md) | `correlacoes_uf.py` | Correlações LULC × socioeconômicas UF (Δ-vs-Δ, HAC) | 1985–2024 | UF | ✅ |
| 22 | [22_correlacoes_painel.md](22_correlacoes_painel.md) | `correlacoes_painel.py` | Painel municipal 2-way FE (entity + time) | 2002–2023 | Municipal | ✅ |
| 23 | [23_did.md](23_did.md) | `piecewise_did.py` | DiD piecewise GO vs MT/TO + event-study + placebo | 1985–2024 | UF | ✅ |
| 24 | [24_analise_espacial.md](24_analise_espacial.md) | `analise_espacial.py` | Moran's I, LISA, regressão espacial (OLS/SAR/SEM) | 2013–2021 | Municipal | ✅ |
| 26 | [26_deteccao_quebras.md](26_deteccao_quebras.md) | `deteccao_quebras.py` | Detecção de quebras estruturais (sup-F + binary segmentation) GO+TO | 1985–2024 | UF | ✅ |

## Como os pipelines se cruzam

- **#1 e #2** foram feitos antes do plano-mestre amadurecer; produzem só análises **descritivas no nível UF**, úteis como "primeira foto" da tese e como baseline de validação batimental.
- **#3, #4, #6, #7** são o **fundamento real da dissertação**: dados municipais brutos prontos para correlações, mapas e regressão espacial.
- **#5 consome #3 e #4** para produzir a primeira camada analítica municipal — métricas de transição pastagem↔soja por município e período, com validação cruzada entre as duas fontes (MapBiomas vs SIDRA).
- **#8 consome #3, #4, #5, #6** para cruzar crédito × LULC.
- **#9 e #10** consomem #4 para mapas; #10 também usa GEE direto.
- **#11** consome PNGs do #10.
- **#12** é independente (puro GEE) e **substitui o #5 como fonte de matriz de transição** real (pixel-a-pixel).
- **#13, #14, #15** alimentam slots do painel unificado (#16).
- **#16** consolida #3, #4, #6, #7, #13, #15 num painel pronto para análise espacial estatística.
- **#17** consome #4 (dados brutos MapBiomas municipal) e #18 (mesorregiões). Produz métricas de variação LULC para #20 e para as correlações da Etapa 2.
- **#18** é independente (geobr). Alimenta #17 e #20 com o mapeamento cd_mun → mesorregião.
- **#19** consome #12 com flag `--consecutivos` (39 pares ano-a-ano). Produz conversão bruta A→B para análise de fluxo.
- **#20** consome #17 (taxas) e #18 (geometrias) para figuras.
- **#21** consome #17 (taxas UF) e #16 (painel socioeconômico) para correlações UF em primeiras diferenças (D7).
- **#22** consome #17 (taxas municipais) e #16 (painel socioeconômico) para painel 2-way FE (D8). Resíduos alimentam análise espacial (Moran's I).
- **#23** consome #17 (taxas GO) + séries MT/TO baixadas via GEE. DiD piecewise (D9).

## Convenções

- **Cache CSV** em todos os coletores — re-execuções são instantâneas; `--force` rebaixa.
- **Schema padronizado** quando possível: chave municipal `cd_mun` (IBGE 7 dígitos) + `nm_mun` + `ano`.
- **Idempotência**: rodar o mesmo pipeline duas vezes produz output idêntico.
- **Deflação para R$ dez/2024** via IPCA — ver [metodologia/deflacao_ipca.md](../metodologia/deflacao_ipca.md).
