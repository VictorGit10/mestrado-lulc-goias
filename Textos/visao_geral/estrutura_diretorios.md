# Estrutura de diretórios

```
Mestrado/
├── Textos/                           # Documentação (este diretório)
│   ├── README.md                     # Índice mestre
│   ├── backlog.md                    # O que falta fazer
│   ├── visao_geral/                  # Escopo, estrutura, como retomar
│   ├── pipelines/                    # pipelines documentados (#1–#51, + #28C, #40B)
│   ├── outputs/                      # Catálogo de gráficos, mapas, CSVs
│   ├── metodologia/                  # Decisões transversais
│   ├── referencia/                   # Ambiente, fontes, memórias
│   └── _arquivo/                     # Histórico preservado
│
├── scripts/                          # Pipelines Python (#1–#51) — índice completo em narrativa_pipelines.md (Apêndice A)
│   ├── grafico_pastagem_pib_goias.py      # #1
│   ├── analise_expandida_goias.py         # #2
│   ├── coleta_sidra.py                    # #3 + #7 + #15 (+ Censo 6850)
│   ├── pipeline_municipal.py              # #4
│   ├── analise_pastagem_soja.py           # #5
│   ├── coleta_sicor.py                    # #6
│   ├── analise_credito_uso_terra.py       # #8
│   ├── gerar_mapas_lulc_40anos.py         # #9  (+ _gee_40anos #10, gif #11, *_rio_verde)
│   ├── transicoes_mapbiomas.py            # #12 (+ visualizar_transicoes, agregar_conversoes #19)
│   ├── coleta_idhm.py                     # #13
│   ├── fogo_mapbiomas.py                  # #14 (+ analise_fogo)
│   ├── analise_safrinha.py                # #15
│   ├── construir_painel_unificado.py      # #16 (+ validar_painel_unificado)
│   ├── calcular_taxas_lulc.py             # #17
│   ├── mapeamento_mesorregioes.py         # #18
│   ├── figuras_taxas.py                    # #20
│   ├── correlacoes_uf.py                  # #21
│   ├── correlacoes_painel.py             # #22
│   ├── piecewise_did.py                  # #23
│   ├── analise_espacial.py               # #24 (Moran/LISA/SAR-SEM)
│   ├── construir_amc_goias.py            # #25 (AMC, D11) (+ verificar_amc_goias)
│   ├── deteccao_quebras.py               # #26
│   ├── coleta_trase.py                    # #27 (cadeia exportadora)
│   ├── coleta_idade_pastagem.py          # #28 (+ analise_reserva_terra, bimodalidade_regional #28C)
│   ├── periodizacao_multivariada.py      # #29a (+ _stars #29b, _transicoes #29c, verificacao_*/intensity_analysis #30/#31, config_periodos)
│   ├── centro_massa.py                    # #32 (+ _pixel #43, _desagregado #44)
│   ├── transicoes_regionais.py           # #33 (via analise_transicoes.py)
│   ├── deslocamento_espacial.py          # #34
│   ├── robustez_janelas.py               # #35 (+ robustez_janela_slope #36)
│   ├── coleta_drivers_macro.py           # #37a (+ drive_comum #37b, drive_comum_amc #38)
│   ├── fronteira_fechando.py             # #39 (+ fronteira_protecao #46, refino_protecao_pixel)
│   ├── duas_logicas_pastagem.py          # #40 (+ duas_logicas_calcario_orientacao #40B)
│   ├── fogo_lidera_fronteira.py          # #41
│   ├── granger_reverso_norte_sul.py      # #42
│   ├── analise_trase_lulc.py             # #45 (Eixo A)
│   ├── custo_carbono_marcha.py           # #47 (D18) (+ validacao_prodes_mapbiomas #48)
│   ├── painel_espacial_dinamico.py       # #49 (Eixo C1)
│   ├── centro_massa_economico.py         # #50 (centro de massa crédito/valor)
│   ├── coleta_firjan_ifdm.py             # #51 coleta (IFDM FIRJAN 2013–2023)
│   ├── crescimento_sem_desenvolvimento.py # #51 (crescimento × desenvolvimento; reabre fio 6)
│   ├── coleta_pib_uf_ipea.py             # PIB/VAB UF IPEA (insumo #21)
│   ├── estimativa_abate_municipal.py      # Abate municipal estimado
│   ├── _cartografia.py, auditoria_pib.py, _validar_sicor.py, _verificar_dados.py, _preview_mapa_2024.py, explorar_asset_*.py
│   └── (scripts *_mg.py e config_mg.py = trabalho PARALELO de Minas Gerais — ver CLAUDE.md)
│
├── data/
│   ├── raw/                              # Dados brutos baixados das fontes
│   │   ├── mapbiomas_col10_estado.xlsx       # 78MB — MapBiomas Col 10.1
│   │   ├── sidra/                             # CSVs brutos paginados (11+ tabelas)
│   │   ├── sicor/                             # JSONs brutos do SICOR (2013-2026)
│   │   ├── idhm/                              # IDHM IPEA + Atlas Brasil 2021
│   │   └── pib_uf_ipea/                       # PIB UF IPEA Data (JSONs)
│   │
│   └── processed/                       # Dados limpos, schema padronizado (~159 CSVs + 3 parquets)
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
│       ├── matriz_transicao_ato_I..III.csv      # 3 matrizes 6×6 por ATO — Pipeline #33 (analise_transicoes.py)
│       ├── painel_unificado.parquet            # 9.840×185 — Pipeline #16
│       ├── painel_amc_goias.parquet            # 166 AMCs — Pipeline #25 (longitudinal, D11)
│       ├── pib_uf_ipea_goias.csv               # PIB/VAB agro UF IPEA (1985-2023)
│       ├── sicor_painel_municipal.csv          # Crédito municipal consolidado
│       ├── abate_*.csv                         # Abate bovino/suíno/frango
│       └── ... (65+ CSVs no total)
│
└── outputs/                            # Gráficos, mapas, diagnósticos (25 subpastas, uma por eixo)
    ├── analises/                            # PNGs 01–28 descritivos — Pipelines #1,2,5,8,14,15
    ├── mapas/ mapas_gee/ mapas_gee_rio_verde/   # coropléticos + rasters GEE + GIFs — #9, #10, #11
    ├── transicoes/ transicoes_regionais/   # heatmaps, Sankey, mapas — #12, #33
    ├── taxas/                              # figuras de taxas — #20
    ├── correlacoes/                         # painel 2FE, DiD, quebras — #21-23, #26
    ├── idade_pastagem/                      # bimodalidade da idade do pasto — #28, #28C
    ├── centro_massa/ deslocamento/ robustez/    # marcha ao norte (Camadas 1/3) + robustez — #32,#34,#35,#36,#43,#44
    ├── drive_comum/ drive_comum_amc/       # drivers macro (Camadas 4/5) — #37, #38
    ├── fronteira_fechando/ fronteira_protecao/  # oferta + proteção — #39, #46
    ├── duas_logicas/                        # geografia das duas lógicas — #40, #40B
    ├── fogo_fronteira/ granger_reverso/     # fogo + Granger reverso — #41, #42
    ├── trase_lulc/                          # Eixo A (Trase × LULC) — #45
    ├── custo_carbono/ validacao_prodes/     # eixo ambiental (carbono + PRODES) — #47, #48
    ├── espacial/                            # painel espacial dinâmico (Eixo C1) — #49
    └── diagnosticos/                        # CSVs de validação e auditoria

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