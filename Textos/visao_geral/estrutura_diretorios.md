# Estrutura de diretórios

```
Mestrado/
├── Textos/                           # Documentação (este diretório)
│   ├── README.md                     # Índice mestre
│   ├── backlog.md                    # O que falta fazer
│   ├── visao_geral/                  # Escopo, estrutura, como retomar
│   ├── pipelines/                    # 23+ pipelines documentados
│   ├── outputs/                      # Catálogo de gráficos, mapas, CSVs
│   ├── metodologia/                  # Decisões transversais
│   ├── referencia/                   # Ambiente, fontes, memórias
│   └── _arquivo/                     # Histórico preservado
│
├── scripts/                          # Todos os pipelines Python
│   ├── grafico_pastagem_pib_goias.py      # Pipeline #1
│   ├── analise_expandida_goias.py         # Pipeline #2
│   ├── coleta_sidra.py                    # Pipeline #3 + #7 + #15
│   ├── pipeline_municipal.py              # Pipeline #4
│   ├── analise_pastagem_soja.py           # Pipeline #5
│   ├── coleta_sicor.py                    # Pipeline #6
│   ├── analise_credito_uso_terra.py       # Pipeline #8
│   ├── gerar_mapas_lulc_40anos.py         # Pipeline #9
│   ├── gerar_mapas_lulc_gee_40anos.py     # Pipeline #10
│   ├── gerar_gif_lulc.py                  # Pipeline #11 (estado)
│   ├── gerar_gif_lulc_rio_verde.py        # Pipeline #11 (Rio Verde)
│   ├── transicoes_mapbiomas.py            # Pipeline #12
│   ├── visualizar_transicoes.py           # Pipeline #12 (visualizações)
│   ├── coleta_idhm.py                     # Pipeline #13
│   ├── fogo_mapbiomas.py                  # Pipeline #14
│   ├── analise_safrinha.py                # Pipeline #15 (análise descritiva)
│   ├── construir_painel_unificado.py      # Pipeline #16
│   ├── calcular_taxas_lulc.py             # Pipeline #17
│   ├── mapeamento_mesorregioes.py         # Pipeline #18
│   ├── agregar_conversoes.py             # Pipeline #19
│   ├── figuras_taxas.py                  # Pipeline #20
│   ├── correlacoes_uf.py                 # Pipeline #21
│   ├── correlacoes_painel.py             # Pipeline #22
│   ├── piecewise_did.py                  # Pipeline #23
│   ├── analise_transicoes.py             # Pipeline #25 (em andamento)
│   ├── deteccao_quebras.py               # Pipeline #26
│   ├── coleta_pib_uf_ipea.py            # PIB/VAB UF IPEA Data
│   ├── estimativa_abate_municipal.py      # Abate municipal estimado
│   ├── auditoria_pib.py                  # Diagnóstico PIB
│   └── _cartografia.py, _validar_sicor.py, _verificar_dados.py, validar_painel_unificado.py
│
├── data/
│   ├── raw/                              # Dados brutos baixados das fontes
│   │   ├── mapbiomas_col10_estado.xlsx       # 78MB — MapBiomas Col 10.1
│   │   ├── sidra/                             # CSVs brutos paginados (11+ tabelas)
│   │   ├── sicor/                             # JSONs brutos do SICOR (2013-2026)
│   │   ├── idhm/                              # IDHM IPEA + Atlas Brasil 2021
│   │   └── pib_uf_ipea/                       # PIB UF IPEA Data (JSONs)
│   │
│   └── processed/                       # Dados limpos, schema padronizado (~65 CSVs + 1 parquet)
│       ├── pastagem_goias_anual.csv          # UF — Pipeline #1
│       ├── pib_goias_real.csv                # UF — Pipeline #1 (deflacionado)
│       ├── cobertura_goias_grupos.csv        # UF — Pipeline #2
│       ├── rebanho_bovino_goias.csv          # UF — Pipeline #2
│       ├── lotacao_implicita_goias.csv       # UF — Pipeline #2
│       ├── pib_agro_goias.csv                # UF — Pipeline #2
│       ├── sidra_*.csv                        # Municipal — Pipeline #3, #7, #15
│       ├── sidra_censo_agro_2017.csv          # 246×44 — Pipeline #7
│       ├── sicor_*.csv                        # Municipal + UF — Pipeline #6
│       ├── mapbiomas_munis_goias.csv          # 137K linhas — Pipeline #4
│       ├── painel_pastagem_soja_municipal.csv  # Municipal — Pipeline #5
│       ├── validacao_soja_mapbiomas_sidra.csv  # Validação cruzada — Pipeline #5
│       ├── credito_municipal_anual.csv         # Municipal — Pipeline #8
│       ├── credito_produto_anual.csv           # UF — Pipeline #8
│       ├── painel_credito_lulc.csv             # Municipal — Pipeline #8
│       ├── idhm_goias_municipal.csv            # Municipal — Pipeline #13
│       ├── sidra_pam839_milho_safras.csv       # Municipal — Pipeline #15
│       ├── fogo_mapbiomas_goias.csv            # UF — Pipeline #14
│       ├── painel_fogo_municipal.csv           # Municipal — Pipeline #14
│       ├── taxas_lulc_*.csv                    # UF, municípios, mesorregiões — Pipeline #17
│       ├── mapeamento_mesorregioes.csv         # cd_mun → mesorregião — Pipeline #18
│       ├── conversao_bruta_*.csv               # UF + municipal — Pipeline #19
│       ├── decomposicao_origem.csv, fluxo_bruto_liquido.csv  # Pipeline #19
│       ├── matriz_transicao_ato_I..V.csv      # 5 matrizes 6×6 por ATO — Pipeline #25
│       ├── painel_unificado.parquet            # 9.840×66 — Pipeline #16
│       ├── pib_uf_ipea_goias.csv               # PIB/VAB agro UF IPEA (1985-2023)
│       ├── sicor_painel_municipal.csv          # Crédito municipal consolidado
│       ├── abate_*.csv                         # Abate bovino/suíno/frango
│       └── ... (65+ CSVs no total)
│
└── outputs/                            # Gráficos, mapas, diagnósticos
    ├── analises/                            # 22 PNGs descritivos — Pipelines #1,2,5,8,14,15,20
    ├── mapas/                              # 40 coropléticos municipais — Pipeline #9
    │   └── cobertura_{1985..2024}.png
    ├── mapas_gee/                          # 40 rasters GEE + 40 raw — Pipeline #10
    │   ├── cobertura_{1985..2024}.png
    │   ├── _raw/raw_{1985..2024}.png
    │   └── cobertura_1985_2024.gif
    ├── mapas_gee_rio_verde/                 # 40+ rasters Rio Verde — Pipeline #10
    ├── transicoes/                         # Heatmaps, mapas, Sankey — Pipelines #12, #25
    │   ├── matriz_transicao_*.png
    │   ├── mapa_estabilidade_*.png
    │   ├── mapa_pastagem_agricultura_*.png
    │   ├── mapa_transicao_dominante_*.png
    │   ├── evolucao_transicoes.png
    │   └── sankey_1985_2024.html
    ├── taxas/                              # Figuras de taxas — Pipeline #20
    ├── correlacoes/                         # Painel 2FE, DiD, quebras — Pipelines #21-23, #26
    │   ├── painel_2fe.csv, painel_residuos.csv
    │   ├── did_resultados.csv
    │   ├── quebras_resultados.csv, quebras_vs_marcos.csv
    │   └── uf_deltas.csv, uf_deltas_pre_ipea.csv
    └── diagnosticos/                       # CSVs de validação e auditoria

├── Visualizacao/                         # Site scrollytelling (vanilla JS + D3.js)
│   ├── index.html                           # Aplicação single-page
│   ├── assets/
│   │   ├── css/                             # styles.css, tabs.css, atlas.css
│   │   ├── js/                              # timeline.js, atlas.js, utils.js, router.js, sankey.js, mini-sankey.js
│   │   │   └── vendor/                      # d3.v7, d3-sankey, scrollama
│   │   └── data/                            # JSONs de dados + 246 municípios
│   ├── img/                                 # Mapas WebP, gráficos PNG
│   └── scripts/                             # Scripts Python de geração de dados

├── notebooks/                            # Jupyter notebooks
│   └── validacao_painel.ipynb               # Validação visual do painel unificado

├── requirements.txt                      # Dependências Python
└── .gitignore                            # Ignora data/, outputs/, __pycache__/
```

Ver também: [escopo_dissertacao.md](escopo_dissertacao.md), [como_retomar_trabalho.md](como_retomar_trabalho.md).