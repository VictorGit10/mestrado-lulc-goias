# Estrutura de diretórios

```
Mestrado/
├── Textos/                           # Documentação (este diretório)
│   ├── README.md                     # Índice mestre
│   ├── backlog.md                    # O que falta fazer
│   ├── visao_geral/                  # Escopo, estrutura, como retomar
│   ├── pipelines/                    # 16 pipelines documentados
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
│   ├── fogo_mapbiomas.py                  # Pipeline #14 (não executado)
│   └── construir_painel_unificado.py      # Pipeline #16
│
├── data/
│   ├── raw/                              # Dados brutos baixados das fontes
│   │   ├── mapbiomas_col10_estado.xlsx       # 78MB — MapBiomas Col 10.1
│   │   ├── sidra/                             # CSVs brutos paginados
│   │   └── sicor/                             # JSONs brutos do SICOR
│   │
│   └── processed/                       # Dados limpos, schema padronizado
│       ├── pastagem_goias_anual.csv          # UF — Pipeline #1
│       ├── pib_goias_real.csv                # UF — Pipeline #1 (deflacionado)
│       ├── cobertura_goias_grupos.csv        # UF — Pipeline #2
│       ├── rebanho_bovino_goias.csv          # UF — Pipeline #2
│       ├── lotacao_implicita_goias.csv       # UF — Pipeline #2
│       ├── pib_agro_goias.csv                # UF — Pipeline #2
│       ├── sidra_*.csv                        # Municipal — Pipeline #3 (8) + #7 (7) + #15
│       ├── sidra_censo_agro_2017.csv          # Municipal — Pipeline #7 (246×44)
│       ├── sicor_*.csv                        # Municipal + UF — Pipeline #6 (5)
│       ├── mapbiomas_munis_goias.csv          # Municipal — Pipeline #4 (8.6 MB)
│       ├── painel_pastagem_soja_municipal.csv  # Municipal — Pipeline #5
│       ├── validacao_soja_mapbiomas_sidra.csv  # Municipal — Pipeline #5
│       ├── credito_municipal_anual.csv         # Municipal — Pipeline #8
│       ├── credito_produto_anual.csv           # UF — Pipeline #8
│       ├── painel_credito_lulc.csv             # Municipal — Pipeline #8
│       ├── idhm_goias_municipal.csv            # Municipal — Pipeline #13
│       ├── sidra_839_milho_safras.csv          # Municipal — Pipeline #15
│       └── painel_unificado.parquet            # Municipal — Pipeline #16 (9.840×66)
│
└── outputs/                            # Gráficos, mapas, diagnósticos
    ├── 01_*.png … 18_*.png                # 18 PNGs descritivos — Pipelines #1,2,5,8
    ├── mapas/                              # 40 coropléticos municipais — Pipeline #9
    │   └── cobertura_{1985..2024}.png
    ├── mapas_gee/                          # 40 rasters GEE + GIF — Pipelines #10,11
    │   ├── cobertura_{1985..2024}.png
    │   ├── _raw/raw_{1985..2024}.png
    │   └── cobertura_1985_2024.gif
    ├── transicoes/                         # Heatmaps e Sankey — Pipeline #12
    └── diagnosticos/                       # CSVs de diagnóstico
```

Ver também: [escopo_dissertacao.md](escopo_dissertacao.md), [como_retomar_trabalho.md](como_retomar_trabalho.md).