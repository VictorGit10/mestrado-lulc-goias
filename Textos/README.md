# Documentação — Dissertação CIAMB-UFG

Dinâmica de uso e cobertura da terra em Goiás (1985–2024) e fatores socioeconômicos.
Este é o **ponto de entrada único** do repositório: onde está cada coisa, e por onde procurar
um assunto.

## Por onde começar

- **Retomando o trabalho?** → [`qualificacao/README.md`](../qualificacao/README.md), o estado vivo
  da redação (o que foi conferido, por qual régua, o que ficou pendente).
- A história do trabalho, do começo ao fim → [ensaio_a_investigacao.md](ensaio_a_investigacao.md)
- O que sustenta a tese, e com que força → [indice_logico_pipelines.md](indice_logico_pipelines.md)
- Como o trabalho foi construído, fase a fase → [narrativa_pipelines.md](narrativa_pipelines.md)
- Dominar os métodos → [guia_de_leitura.md](guia_de_leitura.md)
- A ficha de um pipeline → [pipelines/README.md](pipelines/README.md)
- Um gráfico ou CSV específico → [outputs/README.md](outputs/README.md)
- Um assunto (ex.: centro de massa) → tabela [Por tema](#por-tema), abaixo
- Log cronológico da exploração → [backlog.md](backlog.md)

## Onde está cada coisa

| Pasta | O que é |
|---|---|
| `qualificacao/` | **O texto** (abnTeX2): `cap/`, `fig/` (+ gerador), `ref/`, `guia/` (caderno de estudo para a banca) |
| `Visualizacao/` | **O site** (GitHub Pages): `index.html` + páginas de apoio, `apresentacao.html`, `conceitos.html`, `laboratorio_metodos/` |
| `Textos/` | Esta documentação: `pipelines/` (uma ficha por pipeline), `metodologia/` (decisões transversais), `outputs/` (catálogo de figuras e CSVs), `referencia/` (ambiente, fontes, escopo inicial, guias práticos) |
| `scripts/` | Os pipelines em Python (plano, sem subpastas; `*_mg.py` = trabalho paralelo) |
| `data/` | `raw/` (baixado das fontes), `processed/` (CSVs e as duas tabelas-mãe), `cache/` — fora do git |
| `outputs/` | Figuras e diagnósticos, uma subpasta por eixo — fora do git |
| `_arquivo/` | Material superado, guardado e não atualizado (planos antigos da viz, páginas aposentadas, rascunhos iniciais) |
| `paralelo/` | Trabalhos paralelos (rebanho BR/MG, Minas, viagem de campo) — ver `CLAUDE.md` |

As duas tabelas-mãe: `data/processed/painel_unificado.parquet` (246 municípios × 40 anos, o
trilho **transversal**) e `data/processed/painel_amc_goias.parquet` (166 AMCs de território
constante, o trilho **longitudinal**, D11).

## Por tema

Cada tema usa **o mesmo prefixo de nome** em `scripts/`, `data/processed/` e `outputs/`. Para ver
tudo de um assunto, busque o prefixo (ex.: `centro_massa`) nas três pastas. A tabela diz onde o
tema aparece em cada camada; a ficha de cada pipeline fica em `pipelines/`.

| Tema | Pipelines | Prefixos (scripts · data · outputs) | Site | Qualificação |
|---|---|---|---|---|
| **Os três atos** (periodização, quebras, transições) | #12B, #17, #19, #26, #29 (+#30, #31) | `periodizacao_*`, `deteccao_quebras`, `config_periodos`, `transicoes_cubo` · `matriz_transicao_ato_*`, `taxas_lulc_*`, `conversao_bruta_*`, `periodizacao_*` · `taxas/`, `transicoes/`, `correlacoes/` | Parte 1; `#p4-periodizacao` | §4.1 |
| **Marcha ao norte / centro de massa** (Perna 1) | #32, #35, #36, #43, #44, #50, #53, #55, #58, #59 | `centro_massa*`, `robustez_*`, `exportar_marcha_viz`, `exportar_metodo_centro_massa_viz` · `centro_massa_*`, `robustez_*`, `data/cache/centro_massa_pixel/` · `centro_massa/`, `robustez/` | `#p2-perna1`, `centros-de-massa.html`, `metodo-centro-de-massa.html`, `img/marcha_norte/` | §4.2; `fig/cap4_centro_massa` |
| **Duas lógicas / idade da pastagem** (Perna 2) | #22, #22B, #28, #28C, #33, #40, #40B, #49 | `coleta_idade_pastagem`, `processa_cubo_idade*`, `bimodalidade_*`, `forma_regional_*`, `duas_logicas_*`, `transicoes_regionais*`, `correlacoes_painel`, `painel_espacial_dinamico*` · `idade_*`, `pastagem_idade_*`, `duas_logicas_*`, `transicoes_regionais_*` · `idade_pastagem/`, `duas_logicas/`, `transicoes_regionais/`, `espacial/` | `#p2-perna2` | §4.3; `fig/cap4_idade_pastagem`, `cap4_sankey` |
| **Deslocamento e *drive* comum** (Perna 3) | #34, #37, #38, #41, #42, #45, #52, #54, #56 | `deslocamento_*`, `drive_*`, `coleta_drivers_macro`, `granger_reverso_*`, `aptidao_edafo_*`, `defensabilidade_perna4`, `fogo_lidera_fronteira`, `analise_trase_lulc` · `deslocamento_*`, `drive_*`, `granger_reverso_*`, `perna4_*` (são do #54), `fogo_fronteira_*`, `trase_lulc_*` · `deslocamento/`, `drive_comum*/`, `granger_reverso/`, `aptidao_edafo/`, `defensabilidade_perna4/`, `fogo_fronteira/`, `trase_lulc/` | `#p2-perna3` | §4.4; `fig/cap4_teste_espacial`, `cap4_horse_race` |
| **Teto de oferta e remanescente** (Perna 4) | #39, #39B, #46, #47, #48, #51, #57 | `fronteira_*`, `refino_protecao_pixel`, `custo_carbono_marcha`, `validacao_prodes_mapbiomas`, `crescimento_sem_desenvolvimento`, `remanescente_qualidade` · `fronteira_*`, `protecao_*`, `carbono_*`, `desenvolvimento_*`, `remanescente_*` · `fronteira_fechando/`, `fronteira_protecao/`, `custo_carbono/`, `validacao_prodes/`, `desenvolvimento/` | `#p2-perna4` | §4.5; `fig/cap4_fronteira_oferta` |
| **Mosaico de Usos** (a deriva do rótulo, D25/D26) | #28D | `deriva_mosaico_*`, `*_deriva*`, `*_bracket*`, `razao_destino_ano`, `mapas_mosaico_40anos`, `borda_movel_*`, `mosaico_10m_sentinel` · `deriva_mosaico_*`, `*_deriva*`, `*_bracket*`, `borda_movel_*` · `deriva_mosaico/`, `mosaico_40anos/` | `dossie-mosaico.html` | §4.1 (Ato III); Apêndice B |
| **Fundação de dados** (coletores e painéis) | #3, #4, #6, #7, #13, #14, #15, #16, #18, #25, #27 | `coleta_*`, `pipeline_municipal`, `construir_*`, `mapeamento_mesorregioes`, `fogo_mapbiomas` · `sidra_*`, `sicor_*`, `painel_*`, `amc_*` · `analises/`, `mapas/`, `mapas_gee/` | Parte 1 (mapas) | Cap. 3 |
| Coleção 11 do MapBiomas (exploratório, **fora da dissertação**) | — | `exploratorio_col11_*` · `data/processed/exploratorio_col11/` · `outputs/exploratorio_col11/` | `dossie-colecao11.html` | — |

Textos de apoio por tema: centro de massa → [metodologia/pagina_metodo_centro_massa.md](metodologia/pagina_metodo_centro_massa.md)
e [referencia/referencial_marcha.md](referencia/referencial_marcha.md); três atos →
[referencia/explicacao_atos.md](referencia/explicacao_atos.md) e
[metodologia/janelas_temporais.md](metodologia/janelas_temporais.md); Mosaico →
[metodologia/tratamento_deriva_mosaico.md](metodologia/tratamento_deriva_mosaico.md); fundação →
[metodologia/areas_minimas_comparaveis.md](metodologia/areas_minimas_comparaveis.md).

## Convenções e reprodutibilidade

- Valores monetários deflacionados pelo IPCA (dez/2024). Malha municipal IBGE 2020; CRS métrico
  EPSG:5880 (policônica, não equal-area).
- Dependências em `requirements.txt`; detalhes de instalação (geobr, GEE) em
  [referencia/ambiente_python.md](referencia/ambiente_python.md).
- Scripts idempotentes: apagar `data/processed/` força re-processamento; `data/raw/` reconstrói o
  processado offline.
- Publicar o site e fazer commits → [referencia/guia-github-pages-e-commits.md](referencia/guia-github-pages-e-commits.md);
  compilar o LaTeX no Windows → [referencia/guia-abntex2-windows.html](referencia/guia-abntex2-windows.html).
