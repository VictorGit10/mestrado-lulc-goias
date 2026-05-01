# Documentação do projeto — Dissertação CIAMB-UFG

**Tema**: Dinâmica de uso e cobertura da terra em Goiás (1985–2024) e sua relação com fatores socioeconômicos.

**Unidade de análise**: 246 municípios de Goiás. **Período**: 1974–2024 (dependendo da fonte).

Este documento descreve, ponto a ponto, **o que existe hoje no diretório**, **como cada peça funciona** e **o que ainda falta** segundo o plano-mestre em `ResumoDoBrainStorm.ini` e o doc de sugestões `SugestaoClaude.md`.

---

## 1. Estrutura de diretórios

```
Mestrado/
├── ResumoDoBrainStorm.ini           # Plano-mestre da dissertação (escrito por você)
├── SugestaoClaude.md                # Lista expandida de fontes + checklist de espacialização
├── DOCUMENTACAO.md                  # Este arquivo
├── PROMPT_MAPAS_40_ANOS.md          # Briefing dos mapas LULC 1985–2024
│
├── Scripts e Catalogo/              # Todos os pipelines Python ficam aqui
│   ├── grafico_pastagem_pib_goias.py    # Pipeline #1 — pastagem UF × PIB UF (UF agregado)
│   ├── analise_expandida_goias.py       # Pipeline #2 — cobertura + rebanho + PIB agro (UF)
│   ├── coleta_sidra.py                  # Pipeline #3 + #7 — SIDRA municipal (8 tabelas) + Censo Agro 2017 (7 tabelas)
│   ├── coleta_sicor.py                  # Pipeline #6 — SICOR/BACEN crédito rural 2013–2026
│   ├── pipeline_municipal.py            # Pipeline #4 — MapBiomas municipal (40 anos × 22 classes × 246 munis)
│   ├── analise_pastagem_soja.py         # Pipeline #5 — Transição pastagem↔soja municipal (1985–2024)
│   ├── analise_credito_uso_terra.py     # Pipeline #8 — crédito SICOR × LULC municipal
│   ├── gerar_mapas_lulc_40anos.py       # Pipeline #9 — 40 mapas coropléticos municipais (CSV → PNG)
│   ├── gerar_mapas_lulc_gee_40anos.py   # Pipeline #10 — 40 mapas raster MapBiomas via GEE (30m, Coleção 10.1)
│   ├── transicoes_mapbiomas.py          # Pipeline #12 — Matrizes de transição pixel-a-pixel via GEE
│   └── visualizar_transicoes.py         # Visualizações das matrizes (heatmaps, Sankey, mapas)
│
├── data/
│   ├── raw/                         # Dados brutos baixados das fontes
│   │   ├── mapbiomas_col10_estado.xlsx   # 78MB — MapBiomas Col 10.1 (estado/bioma/MUNICÍPIO)
│   │   └── sidra/                        # CSVs brutos do SIDRA, paginados (chunks)
│   │       ├── pam1612_temporarias_pNN.csv
│   │       ├── pam1613_permanentes_pNN.csv
│   │       ├── ppm3939_rebanhos_pNN.csv
│   │       ├── ppm74_leite_pNN.csv
│   │       ├── ppm94_ovos_pNN.csv
│   │       ├── tab5938_pib_municipal_pNN.csv
│   │       ├── tab6579_populacao_pNN.csv
│   │       └── tab1737_ipca.csv
│   │   └── sicor/                        # JSONs brutos do SICOR, por endpoint e ano
│   │       ├── CusteioMunicipioProduto_YYYY.json
│   │       ├── InvestMunicipioProduto_YYYY.json
│   │       ├── CusteioRegiaoUFProduto_YYYY.json
│   │       ├── InvestRegiaoUFProduto_YYYY.json
│   │       └── ComercRegiaoUFProduto_YYYY.json
│   │
│   └── processed/                   # Dados limpos, schema padronizado, prontos para análise
│       ├── pastagem_goias_anual.csv             # UF — Pipeline #1
│       ├── pib_goias_real.csv                   # UF — Pipeline #1 (deflacionado)
│       ├── cobertura_goias_grupos.csv           # UF — Pipeline #2
│       ├── rebanho_bovino_goias.csv             # UF — Pipeline #2
│       ├── lotacao_implicita_goias.csv          # UF — Pipeline #2
│       ├── pib_agro_goias.csv                   # UF — Pipeline #2
│       ├── sidra_*.csv                          # MUNICIPAL — Pipeline #3 (8 arquivos) + #7 (7 Censo Agro)
│       ├── sidra_censo_agro_2017.csv            # MUNICIPAL — Pipeline #7 painel wide (246×44)
│       ├── sicor_*.csv                          # MUNICIPAL + UF — Pipeline #6 (5 arquivos)
│       ├── mapbiomas_munis_goias.csv            # MUNICIPAL — Pipeline #4 (8.6 MB)
│       │
│       │   # Saídas do Pipeline #5:
│       ├── painel_pastagem_soja_municipal.csv   # 1 linha por município (deltas, taxa conv., intensidade)
│       ├── transicao_pastagem_soja_periodos.csv # deltas por município × 4 períodos
│       ├── ranking_conversao_municipal.csv      # rankings combinados (Δ absoluto, intensidade)
│       ├── validacao_soja_mapbiomas_sidra.csv   # comparação par-a-par MapBiomas vs SIDRA
│       ├── evolucao_pastagem_soja_estado.csv    # série anual estadual (soma 246 munis)
│       ├── evolucao_pastagem_soja_top10.csv     # séries dos top 10 munis em expansão
│       ├── heatmap_transicao_periodos.csv       # top 40 × 4 períodos para heatmap
│       │
│       │   # Saídas do Pipeline #8:
│       ├── credito_municipal_anual.csv           # MUNICIPAL — crédito/ha pastagem, deflacionado
│       ├── credito_produto_anual.csv             # UF — valor por produto, deflacionado
│       └── painel_credito_lulc.csv               # MUNICIPAL — merge crédito + LULC + PIB 2013–2023
│
└── outputs/                         # Gráficos PNG e anotações
    ├── 01_pastagem_goias_1985-2024.png        # Pipeline #1
    ├── 02_pastagem_pib_goias.png              # Pipeline #1
    ├── 03_cobertura_goias_1985-2024.png       # Pipeline #2
    ├── 04_rebanho_bovino_goias.png            # Pipeline #2
    ├── 05_lotacao_implícita_goias.png         # Pipeline #2
    ├── 06_pib_agro_goias.png                  # Pipeline #2
    ├── 07_evolucao_pastagem_soja_estado.png   # Pipeline #5
    ├── 08_evolucao_pastagem_soja_top10.png    # Pipeline #5
    ├── 09_scatter_delta_pastagem_soja.png     # Pipeline #5
    ├── 10_barras_top20_conversao.png          # Pipeline #5
    ├── 11_heatmap_muni_periodo.png            # Pipeline #5
    ├── 12_credito_uf_serie_2013-2024.png      # Pipeline #8
    ├── 13_scatter_credito_pastagem.png         # Pipeline #8
    ├── 14_composicao_produto_credito.png       # Pipeline #8
    ├── 15_scatter_credito_soja.png             # Pipeline #8
    ├── 16_barras_credito_intensidade.png       # Pipeline #8
    ├── 17_evolucao_credito_pastagem.png        # Pipeline #8
    ├── 18_scatter_credito_censo_agro.png       # Pipeline #8
    ├── Análise.md                              # destinado a anotações da análise (atualmente vazio)
    │
    ├── mapas/                                   # Pipeline #9 — coropléticos municipais (40 PNGs)
    │   └── cobertura_{1985..2024}.png           # 1 cor por município (classe dominante), DPI 200
    │
    └── mapas_gee/                               # Pipeline #10 — raster MapBiomas via GEE (40 PNGs)
        ├── cobertura_{1985..2024}.png           # 30m raster + chrome (título, legenda, escala), DPI 200
        └── _raw/raw_{1985..2024}.png            # raster cru do GEE (2048px), sem chrome
```

---

## 2. Pipeline #1 — `grafico_pastagem_pib_goias.py`

**Quando foi feito**: Primeiro script, no início do projeto.

**O que faz**:
1. Baixa o xlsx do MapBiomas Coleção 10.1 (78MB, do Google Drive) → cacheado em `data/raw/`.
2. Filtra Goiás, classe 15 (Pastagem), agrega ano-a-ano (soma de biomas).
3. Baixa o **PIB total de Goiás** via SIDRA tabela 5938, variável 37, **nível UF** (territorial_level=3).
4. Baixa o **IPCA mensal** via SIDRA tabela 1737, calcula índice acumulado, deflaciona o PIB para reais de **dez/2024**.
5. Gera dois PNGs: pastagem 1985–2024 sozinha, e painel pastagem+PIB lado a lado.

**Como rodar**: `python grafico_pastagem_pib_goias.py`

**Saída**: `outputs/01_pastagem_goias_1985-2024.png`, `outputs/02_pastagem_pib_goias.png`, e CSVs `data/processed/pastagem_goias_anual.csv`, `pib_goias_real.csv`.

**Limitações** (importante para a dissertação):
- Só nível UF (Goiás como agregado único).
- PIB começa em 2002 — anos anteriores ficam vazios no gráfico de overlap.
- Deflator usa IPCA dezembro — não IGP-DI nem deflator implícito do PIB.

---

## 3. Pipeline #2 — `analise_expandida_goias.py`

**Quando foi feito**: Segundo script, expansão do #1.

**O que faz**:
1. Reusa o xlsx do MapBiomas (cache).
2. Agrupa as classes do MapBiomas em 5 grupos: Pastagem (15), Agricultura (39, 19, 41, 20, 36), Cerrado/Savana (4, 12), Floresta Nativa (3), Área Urbana (24).
3. Baixa **rebanho bovino** via PPM 3939, variável 105, classification 79 (Tipo de rebanho) → categoria 2670 (Bovino), **nível UF**.
4. Baixa **VA agropecuário** (5938 var 513) e **PIB total** (5938 var 37), **nível UF**, deflaciona via IPCA.
5. Calcula **lotação implícita** = bovinos / área de pastagem.
6. Gera 4 PNGs: cobertura empilhada, rebanho, painel lotação (3 gráficos), PIB agro vs total.

**Como rodar**: `python analise_expandida_goias.py` (depois de já ter rodado o Pipeline #1, pois ele lê `pastagem_goias_anual.csv`).

**Saída**: 4 PNGs em `outputs/` (`03_*.png` a `06_*.png`) e 4 CSVs em `data/processed/`.

**Limitações**:
- Mesmo problema do #1: tudo nível UF.
- Lotação implícita = "boi por hectare de pastagem MapBiomas" — mistura precisão de dois sistemas independentes (raster vs. censo PPM). É uma boa aproximação mas não substitui Censo Agro.

---

## 4. Pipeline #3 — `coleta_sidra.py`

**Quando foi feito**: 2026-04-26.

**O que faz**: Baixa **8 tabelas SIDRA no nível municipal** (246 munis de Goiás) usando paginação automática para respeitar o limite de 50.000 valores/chamada da API SIDRA.

**Tabelas cobertas**:

| Tabela | Variáveis | Categorias | Anos | Linhas |
|---|---|---|---|---:|
| **PAM 1612** — Lavouras temporárias | 109 área plantada, 216 área colhida, 214 quantidade produzida | 8 culturas (algodão, arroz, cana, feijão, mamona, milho, soja, sorgo) | 1974–2024 | 301k |
| **PAM 1613** — Lavouras permanentes | 2313 área destinada, 216 área colhida, 214 quantidade | 8 culturas (banana, café, coco, goiaba, laranja, limão, manga, tangerina) | 1974–2024 | 297k |
| **PPM 3939** — Efetivo rebanhos | 105 efetivo (cabeças) | 7 espécies (bovino, suíno, bubalino, equino, ovino, caprino, galináceos) | 1974–2024 | 88k |
| **PPM 74** — Produção de leite | quantidade (mil L), valor (mil R$) | – | 1974–2024 | 25k |
| **PPM 94** — Produção de ovos | quantidade (mil dúzias), valor | – | 1974–2024 | 13k |
| **5938** — PIB municipal | 37 PIB, 498 VA total, 543 impostos, 513 VA agro, 517 VA indústria, 6575 VA serviços, 525 VA adm. pública | – | 2002–2023 | 38k |
| **6579** — População residente | 9324 estimativas anuais | – | 2001–2024 | 5k |
| **1737** — IPCA mensal Brasil | 63 variação mensal | – | 1979–2026 | 556 |

**Schema padronizado** (todos os 8 CSVs em `data/processed/sidra_*.csv`):

```
cd_mun         int     Código IBGE 7 dígitos do município
nm_mun         str     Nome do município (sem o sufixo " - GO")
ano            int     Ano de referência
variavel_id    int     Código IBGE da variável (ex: 109 = área plantada)
variavel       str     Nome da variável
unidade        str     Unidade de medida (Hectares, Toneladas, Cabeças, etc.)
categoria_id   int     Código da classificação (ex: 2713 = Soja). Vazio quando não aplicável.
categoria      str     Nome da classificação (ex: "Soja (em grão)")
valor          float   Valor numérico. NaN para "..", "-" ou ausente no SIDRA.
```

**Decisões metodológicas tomadas**:

1. **Variável 215 (valor da produção PAM) omitida**. Razão: a unidade de moeda muda no tempo — Cruzeiros (1974–85), Cruzados (1986–88), Cruzados Novos (1989), Cruzeiros Reais (1993), Reais (1994+). Não dá pra deflacionar via IPCA puro. Se precisar do valor real, dá pra reconstruir a partir de Quantidade × Preço médio anual (PAM tabela auxiliar) em uma fase posterior.

2. **Variável 112 (rendimento médio) omitida**. Razão: redundante — é exatamente Quantidade Produzida (214) ÷ Área Colhida (216). Posso calcular no momento da análise sem perda.

3. **PAM 1613 tem 243 municípios, não 246**. Razão: 3 munis de Goiás nunca tiveram registro de lavoura permanente em nenhum ano da série. Goiás é dominado por temporárias.

4. **PIB municipal vai só até 2023**, não 2024. Razão: o IBGE publica Contas Regionais com defasagem de 2 anos.

5. **Códigos validados contra metadados da API** em 2026-04-26. Os primeiros chutes estavam errados: Soja é 2713 (não 2737); Bovino é 2670 (correto); mas Suíno é 32794 (não 2675 — esse é Bubalino). Sempre conferir via `https://servicodados.ibge.gov.br/api/v3/agregados/<tab>/metadados`.

**Como rodar**:

```bash
python coleta_sidra.py                  # baixa só o que faltar (usa cache CSV)
python coleta_sidra.py --force          # ignora cache e rebaixa tudo
python coleta_sidra.py --so 1612 5938   # roda só tabelas que casem com essas substrings
```

**Tempo de execução**: ~10 min na primeira execução (38 chunks × ~25s cada). Re-execuções são instantâneas (cache CSV).

**Arquitetura interna**:

```
_get_sidra_cached(nome, **kwargs)             # 1 chamada SIDRA + cache CSV
        ↓
_quebrar_periodo(ano_ini, ano_fim, ...)       # calcula janelas para caber em 50k valores
        ↓
_get_sidra_paginated(...)                     # várias chamadas, concatena, deduplica header
        ↓
coletar_<tabela>()                            # 1 função por tabela, padroniza schema
        ↓
_padronizar_municipal(df_raw, classif_col)    # bruto → schema canônico
        ↓
data/processed/sidra_<nome>.csv
```

---

## 5. Pipeline #4 — `pipeline_municipal.py`

**Quando foi feito**: 2026-04-26.

**O que faz**: Lê a aba `COVERAGE_10.1` do xlsx do MapBiomas (já em cache desde o Pipeline #1) e extrai uma tabela longa por município de Goiás. Resolve dois problemas:

1. O xlsx vem em formato wide (1 coluna por ano) e divide cada município nos biomas que o cortam (Cerrado e Mata Atlântica para munis fronteiriços do sudeste de GO). O pipeline derrete para longo e soma os biomas.
2. O xlsx só tem o NOME do município. Sem o código IBGE, não dá pra fazer join com SIDRA. Solução: merge por nome contra a tabela `cd_mun ↔ nm_mun` extraída do `sidra_pam1612_temporarias.csv` (Pipeline #3). Como toda a coleta IBGE usa a mesma grafia oficial, o match é exato — sem fuzzy.

**Como rodar**: `python pipeline_municipal.py`

**Saída**: `data/processed/mapbiomas_munis_goias.csv` (8.6 MB).

**Schema**:

```
cd_mun       int    Código IBGE 7 dígitos
nm_mun       str    Nome do município
ano          int    1985–2024
class_id     int    Código da classe MapBiomas
class_nome   str    Nome em pt-BR (15=Pastagem, 39=Soja, 20=Cana-de-açúcar, etc.)
area_ha      float  Área em hectares (somada sobre Cerrado + Mata Atlântica)
```

Total: **137.080 linhas** = 246 munis × 40 anos × 22 classes.

**Validações realizadas**:

1. **Batimental**: a soma municipal de pastagem (classe 15) bate com a série UF antiga (`pastagem_goias_anual.csv`) com **erro máximo de 0,0000%** ao longo dos 40 anos. Math é math.
2. **Soja MapBiomas vs SIDRA (2022)**: total Goiás 4,17 Mha vs 4,12 Mha (razão 1,01). Os 10 maiores produtores de soja batem em ordem entre as duas fontes (Rio Verde, Jataí, Cristalina, Montividiu, Paraúna, Catalão, Mineiros, Ipameri, Chapadão do Céu, Silvânia). A diferença ≤ 12% por município é esperada e tem causa metodológica:
   - SIDRA = área plantada declarada pelo produtor.
   - MapBiomas = pixels classificados como soja por sensoriamento remoto, podendo capturar área plantada em segunda safra ou cultura de inverno que SIDRA conta como milho.
3. **Cana 2022**: SIDRA 933k ha vs MapBiomas 1.004k ha (razão 1,08). Top munis batem (Quirinópolis, Mineiros, Goiatuba, Itumbiara, Acreúna).
4. **Cobertura Goiás 2024** (proporção): Pastagem 35,2% > Cerrado 18,0% > Floresta 14,2% > Soja 13,2% > Mosaico 10,5% > Cana 2,4%. Bate com o conhecimento geral.

**Munis-borda descartados (4)**: Brasília (DF), Paraná (TO), São Desidério (BA), Talismã (TO) — somam ~28 ha total na série inteira (pixels de fronteira mal-classificados). Irrelevante.

**O que o Pipeline #4 ainda NÃO faz**: não anexa geometria (geobr/GPKG). Para mapas, vai precisar instalar `geopandas` + `geobr` em uma fase próxima e fazer `merge` por `cd_mun`. Como o código IBGE já está pronto, o merge será trivial.

---

## 6. Pipeline #5 — `analise_pastagem_soja.py`

**Quando foi feito**: 2026-04-26 (sessão anterior).

**O que faz**: Quantifica a transição pastagem ↔ soja nos 246 municípios de Goiás entre 1985 e 2024. **Não é** matriz de transição pixel-a-pixel (isso depende do MapBiomas via GEE, ainda pendente) — é uma análise **por proxy** que cruza os estoques anuais de área (Pipeline #4) com a série da PAM (Pipeline #3) para validar e produzir métricas de conversão municipais.

**Métricas calculadas por município** (em `painel_pastagem_soja_municipal.csv`, 1 linha por município):

- `delta_pastagem_ha` = pastagem(2024) − pastagem(1985)
- `delta_soja_ha` = soja(2024) − soja(1985)
- `taxa_conversao` = Δsoja / |Δpastagem|, **só quando** Δpastagem < 0 — interpreta-se como "fração da pastagem perdida que virou soja"
- `intensidade_soja` = Δsoja / pastagem(1985) — expansão relativa ao estoque inicial
- `participacao_soja_2024` = soja / (soja + pastagem) em 2024

**Períodos analíticos** (em `transicao_pastagem_soja_periodos.csv`):
1985–1995 (expansão inicial), 1995–2005 (consolidação), 2005–2015 (intensificação), 2015–2024 (recente). Mesmas métricas, recalculadas em cada janela.

**Validações realizadas**:

1. **Batimental UF** (soma municipal × série UF antiga): max |Δ| < 0,01% — confirma idempotência do pivot.
2. **MapBiomas vs SIDRA (área de soja, par-a-par por município/ano)**: salvo em `validacao_soja_mapbiomas_sidra.csv`. Correlação Pearson ≥ ~0,99 nos anos com cobertura SIDRA razoável (a partir de 2000); razão mediana MapBiomas/SIDRA ≈ 1,0–1,1 (MapBiomas captura área de segunda safra que SIDRA registra como milho).

**Como rodar**: `python analise_pastagem_soja.py` (após Pipelines #3 e #4).

**Saída**: 7 CSVs em `data/processed/` + 5 PNGs em `outputs/` (07–11) — ver árvore na seção 1.

**Limitações** (importantes para o texto da dissertação):

- **Não é matriz de transição real**. Apenas confronta estoques (pastagem em t e soja em t+1). Pode haver migração indireta (pastagem → cerrado em regeneração → soja) que não vira "conversão direta" pelo cálculo.
- **`taxa_conversao` é interpretativa, não causal**. Um município pode ter perdido pastagem para vegetação e simultaneamente ganhado soja a partir de cerrado — numerador e denominador não são pareados pixel-a-pixel.
- **A matriz de transição verdadeira** (asset MapBiomas de transição via GEE, com classe-origem × classe-destino por par de anos) está no backlog — ver seção 8.

---

## 6b. Pipeline #8 — `analise_credito_uso_terra.py`

**Quando foi feito**: 2026-04-27.

**O que faz**: Cruza dados de crédito rural (SICOR/BACEN) com mudança de uso da terra (MapBiomas) nos 246 (245 no SICOR) municípios de Goiás. Janela de sobreposição: 2013–2023. Valores deflacionados para R$ de dez/2024 via IPCA.

**Gráficos produzidos** (7 PNGs, 12–18):

| # | Gráfico | Tipo | Descrição |
|---|---|---|---|
| 12 | `12_credito_uf_serie_2013-2024.png` | Barras empilhadas | Crédito por finalidade (Custeio/Invest/Comerc) 2013–2026, R$ bi deflacionados |
| 13 | `13_scatter_credito_pastagem.png` | Scatter colorido | Crédito/ha pastagem vs Δpastagem, cor = intensidade_soja |
| 14 | `14_composicao_produto_credito.png` | Multi-linha | Top 10 produtos + "Outros", 2013–2023 |
| 15 | `15_scatter_credito_soja.png` | Scatter bolha | Crédito total vs Δsoja, bolha = pastagem 1985, inclui Pearson r |
| 16 | `16_barras_credito_intensidade.png` | Barras horiz. 2-painel | Top 20 munis por crédito/ha pastagem (2023), Custeio vs Invest |
| 17 | `17_evolucao_credito_pastagem.png` | 2-painel | (a) Eixo duplo: pastagem Mha + crédito R$ bi; (b) Correlação anual |
| 18 | `18_scatter_credito_censo_agro.png` | Scatter com quadrantes | % familiar vs crédito/ha, cor = intensidade_soja |

**CSVs produzidos** (3):

| Arquivo | Conteúdo | Linhas |
|---|---|---|
| `credito_municipal_anual.csv` | (ano, cd_mun) com valor_custeio_real, valor_investimento_real, valor_total_real, credito_por_ha_pastagem | ~3.424 |
| `credito_produto_anual.csv` | (ano, nm_produto) com valor_real, n_contratos | ~1.713 |
| `painel_credito_lulc.csv` | Merge crédito + pastagem/soja + PIB 2013–2023 | ~2.692 |

**Como rodar**: `python analise_credito_uso_terra.py` (após Pipelines #3, #4, #5, #6).

**Decisões metodológicas**:

- Valores nominais deflacionados via IPCA (dez/2024) — mesmo deflator dos Pipelines #1 e #2.
- Crédito agregado por (ano, cd_mun, finalidade) — colapsa programa, atividade, modalidade.
- `credito_por_ha_pastagem = valor_total_real / pastagem_ha` — onde pastagem_ha > 0.
- 2025–2026 marcados como "(parcial)" no gráfico UF; excluídos dos scatters.
- Valparaíso de Goiás ausente do SICOR (sem código BACEN) — NaN tratado como 0 no merge.

**Limitações**:

- SICOR só cobre 2013+ — não há série histórica longa de crédito municipal.
- Crédito/ha mistura precisão de dois sistemas independentes (SICOR financeiro vs MapBiomas raster).
- Correlações são ecológicas (não causais) — painel de regressão espacial fica para etapa futura.

---

## 6c. Pipeline #9 — `gerar_mapas_lulc_40anos.py`

**Quando foi feito**: 2026-04-27.

**O que faz**: Lê `mapbiomas_munis_goias.csv` (Pipeline #4), agrega as 22 classes MapBiomas em **8 grupos temáticos**, calcula a **classe dominante por município/ano** (maior área em ha) e renderiza 40 PNGs coropléticos — um por ano de 1985 a 2024.

**8 classes agregadas** (mapeamento explícito no topo do script):

| Classe | IDs MapBiomas | Cor |
|---|---|---|
| Floresta | 3 | `#006400` verde escuro |
| Cerrado | 4 | `#32CD32` verde médio |
| Campo natural | 12 | `#90EE90` verde claro |
| Pastagem | 15 | `#FFD700` amarelo |
| Soja | 39 | `#FF69B4` rosa |
| Lavouras+Cana | 20, 40, 41, 46, 47, 48, 62 | `#800080` roxo |
| Área urbana | 24 | `#A0A0A0` cinza |
| Água | 33 | `#4169E1` azul |

Demais IDs do CSV (`0, 9, 11, 21, 25, 29, 30, 31`) são **descartados** antes do cálculo da classe dominante — foco da dissertação é pastagem×soja×água×urbano.

**Layout cada PNG**:
- Coroplético municipal (246 polígonos), 1 cor por município
- Bordas municipais OFF por padrão (variável `SHOW_BORDERS = False` no topo)
- Título "Cobertura e Uso da Terra — Goiás {ANO}"
- Legenda com 8 entradas (canto inferior direito)
- Barra de escala em km (canto inferior esquerdo)
- DPI 200, ~10×8 polegadas

**Como rodar**: `python "Scripts e Catalogo/gerar_mapas_lulc_40anos.py"` (após Pipeline #4).

**Pré-requisitos**: `pip install pandas geopandas geobr matplotlib matplotlib-scalebar` (ver seção 11 sobre gotchas Py 3.14).

**Saída**: 40 PNGs em `outputs/mapas/cobertura_{ANO}.png` (~250 KB cada, ~10 MB total).

**Limitações** (importante registrar para o texto da dissertação):

- **Resolução visual = 246 polígonos**. Cada município vira UMA cor. Município com 51% pastagem e 49% soja "vira" amarelo total — perde-se toda a heterogeneidade interna.
- **Não é raster**. A representação mata o detalhe que aparece na plataforma MapBiomas (manchas finas de cana, núcleos urbanos, hidrografia, mosaicos).
- **Útil para**: visão geral rápida, slide de apresentação, narrativa "qual classe domina cada município". **Não substitui** o Pipeline #10 (raster 30m via GEE) para figuras finais da dissertação.

---

## 6d. Pipeline #10 — `gerar_mapas_lulc_gee_40anos.py`

**Quando foi feito**: 2026-04-28.

**O que faz**: Conecta ao Google Earth Engine, baixa o raster oficial do MapBiomas Coleção 10.1 (asset `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`), recorta pelo polígono de Goiás (via `geobr.read_state`) e gera 40 PNGs em **resolução nativa 30m** (downsampled para 2048px de largura no thumbnail).

Mesmo conjunto de **8 classes agregadas** do Pipeline #9 — paleta consistente entre coroplético e raster, facilita comparação visual entre as duas representações.

**Pipeline interno por ano**:
1. `ee.Image(ASSET).select(f'classification_{ano}')` — banda do ano
2. `.clip(geom_GO)` — recorte
3. `.remap(from_ids, to_ids, 0)` + `.selfMask()` — agrega 22→8 classes, mascara o que não interessa
4. `getThumbURL({'dimensions': 2048, 'palette': [...8 cores], 'min': 1, 'max': 8})` — gera URL do PNG
5. `requests.get()` baixa raw em `outputs/mapas_gee/_raw/raw_{ANO}.png`
6. matplotlib compõe título + legenda + scalebar sobre o raw → `outputs/mapas_gee/cobertura_{ANO}.png`

**Como rodar**:

```bash
# Pré-requisito 1 — autenticar (uma vez):
earthengine authenticate    # abre browser, fluxo OAuth do Google

# Pré-requisito 2 — definir projeto Google Cloud (uma vez):
set GEE_PROJECT=extreme-height-447417-a9     # Windows cmd
$env:GEE_PROJECT="extreme-height-447417-a9"  # PowerShell
export GEE_PROJECT=extreme-height-447417-a9   # bash

# Rodar:
python "Scripts e Catalogo/gerar_mapas_lulc_gee_40anos.py"
```

**Pré-requisitos**: `pip install earthengine-api geopandas geobr matplotlib matplotlib-scalebar pillow requests`.

**Saída**: 40 PNGs em `outputs/mapas_gee/` (~3-4 MB cada, ~137 MB total) + 40 raws em `outputs/mapas_gee/_raw/`.

**Tempo de execução**: ~35 min (dominado por `getThumbURL` — ~50s/ano).

**Decisões metodológicas**:

- **Coleção 10.1** (não 10.0 nem 9). Rationale: Coleção 10 lançada em 2024, 10.1 é a revisão consolidada (correções de Cerrado/Caatinga). Cobertura 1985–2024.
- **Tier noncommercial GEE**. Projeto Cloud `extreme-height-447417-a9` precisa ser registrado em https://code.earthengine.google.com/register como "Noncommercial or Academic" — uso acadêmico é gratuito; sem registro, o tier comercial cobra (consumo deste pipeline é trivial mas registrar é obrigatório por política).
- **Geometria de Goiás vem do `geobr`**, não do `FAO/GAUL` no GEE. Razão: contornos IBGE oficiais > generalizados internacionais, e mantém consistência com Pipeline #9.
- **Aproximação da escala**: o thumbnail é gerado em EPSG:4326 (graus); `metros_por_pixel` calculado pela bbox em EPSG:5880 dá uma boa aproximação para Goiás (latitudes -19° a -12°). Erro <2% nos extremos.
- **selfMask** (vs `updateMask(neq(0))`): mascara pixels com valor 0 do remap → áreas residuais (silvicultura, mosaico, mineração, etc.) ficam transparentes ao invés de pretas.

**Validação visual**:
- 1985: domínio de cerrado (verde médio) e floresta (verde escuro), pastagem já estabelecida no centro-sul, lavouras residuais no sudoeste — confere com história agrária de GO.
- 2024: pastagem dominante em todo o estado, mancha de soja explodida no sudoeste/oeste, cerrado preservado concentrado no nordeste (entorno Chapada dos Veadeiros) e norte de GO — confere com MapBiomas oficial.
- Buraco branco no leste = Distrito Federal (corretamente fora do polígono GO).

**Quando usar #9 vs #10**:

| Caso | Pipeline | Por quê |
|---|---|---|
| Slide de apresentação rápido | #9 | Carrega rápido, narrativa "uma cor = um município" é simples |
| Figura final da dissertação | **#10** | Resolução 30m, vê textura interna, qualidade tipo plataforma MapBiomas |
| Animação GIF/MP4 da série | #10 (preferido) | A textura raster torna a transição visualmente impactante |
| Análise quantitativa de áreas | nem um nem outro | Use diretamente `mapbiomas_munis_goias.csv` (Pipeline #4) |

---

## 7. Cruzando os pipelines

**Por que existem cinco pipelines com sobreposição?**
- #1 e #2 foram feitos antes do plano-mestre amadurecer; produzem só análises **descritivas no nível UF**, úteis como "primeira foto" da tese e como baseline de validação batimental.
- #3 e #4 são o **fundamento real da dissertação**: dados municipais brutos prontos para correlações, mapas e regressão espacial.
- #5 consome #3 e #4 para produzir a **primeira camada analítica municipal** — métricas de transição pastagem↔soja por município e período, com validação cruzada entre as duas fontes (MapBiomas vs SIDRA).

**O que vai mudar daqui pra frente**: as próximas análises (mapas coropléticos, matrizes de transição via GEE, regressão espacial, cruzamento com crédito rural e infraestrutura) vão consumir os CSVs do Pipeline #3, #4, #5, #6 e #7 — não os UFs do #1/#2. Os scripts antigos ficam como referência histórica e validação batimental: se a soma municipal não bate com o agregado UF, é sinal de erro.

---

## 7a. Pipeline #7 — `coleta_sidra.py --censo-agro`

**Quando foi feito**: 2026-04-27.

**O que faz**: Coleta 7 tabelas SIDRA do Censo Agropecuário 2017 para os 246 municípios de Goiás e monta um painel wide-format (1 linha/município) com 44 colunas. Usa o mesmo mecanismo de cache e paginação do Pipeline #3 (`sidrapy` + CSV local).

**Tabelas coletadas** (ver seção 9.2 para detalhes de variáveis e classificações):
- 6878: Estrutura fundiária (estabelecimentos + área, por tipologia familiar)
- 6884: Pessoal ocupado (por tipologia familiar)
- 6870: Tratores (estabelecimentos com tratores + nº tratores)
- 6848: Adubação (estabelecimentos por tipo de adubação)
- 6851: Agrotóxicos (estabelecimentos por uso de agrotóxicos)
- 6910: Bovinos (estabelecimentos com bovinos + efetivo + vacas reprodutoras)
- 6958: Lavouras temporárias (soja, milho, cana — nº estab, área colhida, valor produção)

**Como rodar**: `python coleta_sidra.py --censo-agro` (ou `--censo-agro --force` para rebaixar).

**Saídas**:
- 7 CSVs individuais em `data/processed/sidra_censo_*.csv` (formato longo)
- `data/processed/sidra_censo_agro_2017.csv` — painel consolidado (246×44)

**Validação**: estatísticas plausíveis — lotação bovina ~0.9 cab/ha, % familiar ~61%, % adubação ~36%, % agrotóxicos ~25%.

---

## 8. Backlog — alinhado com `SugestaoClaude.md`

### Já feito
- [x] `coleta_sidra.py` — 8 tabelas SIDRA municipais (Pipeline #3)
- [x] `pipeline_municipal.py` — MapBiomas municipal de Goiás (Pipeline #4)
- [x] `analise_pastagem_soja.py` — análise pastagem↔soja municipal por proxy (Pipeline #5). **Atende parcialmente** o item "matrizes de transição" do plano-mestre — a matriz pixel-a-pixel via GEE continua pendente.
- [x] `coleta_sicor.py` — crédito rural SICOR/BACEN 2013–2026 (Pipeline #6). **Validado**: soma municipal = soma UF em todos os anos (razão 1.0000); 245/246 munis cobertos (Valparaíso de Goiás sem código BACEN).
- [x] `coleta_sidra.py --censo-agro` — Censo Agropecuário 2017, 7 tabelas SIDRA + painel wide 246×44 (Pipeline #7). Variáveis: estrutura fundiária, pessoal ocupado, tratores, adubação, agrotóxicos, bovinos, lavouras temporárias (soja/milho/cana). Inclui 7 variáveis derivadas (% familiar, % adubação, % agrotóxicos, % estab com bovinos, % estab com tratores, lotação Censo, área média estab).

- [x] `analise_credito_uso_terra.py` — cruzamento crédito rural × LULC (Pipeline #8). Produz painel municipal crédito/ha + 7 gráficos (12–18) cruzando SICOR com MapBiomas, PIB e Censo Agro. Janela 2013–2023.
- [x] `gerar_mapas_lulc_40anos.py` — 40 mapas coropléticos municipais (Pipeline #9). 8 classes agregadas, 1 cor por município (classe dominante), 246 polígonos × 40 anos.
- [x] `gerar_mapas_lulc_gee_40anos.py` — 40 mapas raster MapBiomas Coleção 10.1 via GEE (Pipeline #10). 30m de resolução nativa, mesmas 8 classes, qualidade tipo plataforma oficial. **Habilita** os próximos itens do backlog que dependem de GEE (matrizes de transição, fogo).

### Em andamento (próximos a entrar)

### Eixos principais ainda não atacados

| Item | Fonte | O que adiciona |
|---|---|---|
| ~~Matrizes de transição A→B~~ | ~~MapBiomas via GEE~~ | ~~CONCLUÍDO Pipeline #12~~ |
| Frigoríficos federais | SIGSIF/MAPA | Pontos para análise de proximidade |
| Frigoríficos estaduais | Agrodefesa-GO | Complementa SIGSIF para abatedouros menores |
| Silos e armazéns | CONAB SISDEP | Capacidade estática por município |
| Malha viária | DNIT/SNV | Acessibilidade rodoviária |
| ~~IDH-M~~ | ~~PNUD Atlas~~ | ~~CONCLUÍDO Pipeline #13 (aguarda download manual)~~ |
| População rural/urbana | SIDRA 200 (Censos) | Esvaziamento rural decenal |
| ~~Fogo MapBiomas~~ | ~~GEE Collection 4~~ | ~~CONCLUÍDO Pipeline #14 (script pronto, rodar com GEE)~~ |
| PRODES Cerrado | INPE/TerraBrasilis | Desmatamento anual ("primeira supressão") |
| TerraClass Cerrado | INPE/Embrapa | Pastagem íntegra vs degradada (categórico) |
| ~~LSPA tabela 1618~~ | ~~SIDRA~~ | ~~CONCLUÍDO Pipeline #15 (tabela 839 — ver nota abaixo)~~ |
| CAR/SICAR | sicar.gov.br | Limites prediais + reserva legal |
| Precipitação | Xavier/UFES ou GEE ERA5 | Controle climático para regressões |

**Nota Pipeline #15**: tabela 1618 (LSPA) NÃO tem dados municipais (só UF). A tabela municipal
correta para safrinha é **SIDRA 839** (milho 1ª e 2ª safra, 2003–2024, 246 municípios).

**Nota Pipeline #13**: `coleta_idhm.py` requer download manual do CSV em `data/raw/idhm/`
(ver instruções no script). Fonte: http://www.atlasbrasil.org.br/consulta/planilha

**Nota Pipeline #14**: assets confirmados via GEE:
  - `.../fire/collection4/mapbiomas_fire_collection4_annual_burned_v1` (40 bandas binárias)
  - `.../fire/collection4/mapbiomas_fire_collection4_annual_burned_coverage_v1` (40 bandas códigos LULC)
  Bandas: `burned_area_1985`…`burned_area_2024`, `burned_coverage_1985`…`burned_coverage_2024`
  ID 21 (Mosaico) contabilizado separadamente como classe 7 no histograma.

### Decisões de espacialização ainda pendentes (do `SugestaoClaude.md`)

- Malha de referência: **IBGE 2020** (recomendado, default)
- CRS para cálculo de área: **EPSG:5880 SIRGAS Albers** (Brasil)
- Pacote de malha municipal: `geobr` (precisa instalar — não está no ambiente)
- Mapas finais: pipeline gera GPKG/CSV, QGIS faz layout cartográfico (ver seção 10 abaixo)

---

## 9. Decisões aceitas para próximas coletas (SICOR / Censo Agro)

Antes de codar os próximos coletores, registramos abaixo as restrições de escopo aceitas. **Tudo o que está aqui é uma escolha consciente, não uma omissão acidental** — caso a análise futura mostre que algum item é necessário, basta voltar e estender o coletor.

### 9.1 BACEN SICOR — crédito rural

**Sondagem da API realizada em 2026-04-27** (registrada para evitar retrabalho):

- API: `https://olinda.bcb.gov.br/olinda/servico/SICOR/versao/v2/odata/`. Datasets úteis: `CusteioMunicipioProduto`, `InvestMunicipioProduto` (granularidade município, mas Investimento traz só `cdMunicipio` BACEN — não `codIbge`), `CusteioRegiaoUFProduto`, `InvestRegiaoUFProduto`, `ComercRegiaoUFProduto` (agregado UF).
- **Idiossincrasias do Olinda**: `$filter eq` funciona **somente com `%20`** entre tokens (não `+`); `$skip`, `$count`, `$orderby`, `$apply` retornam erro ou são ignorados; `$top` aceita até pelo menos 100.000.
- **Códigos confirmados**: `cdEstado` BACEN para Goiás = `'10'`; `nomeUF` nos datasets agregados = sigla `'GO'` (não 'GOIÁS').
- **Range disponível em TODOS os datasets**: `AnoEmissao` de **2013 a 2026** (operações registradas inclusive com vencimento futuro). Não há série pré-2013 nesta API — nem no nível município, nem no agregado UF.

**Escopo decidido**:

- **Painel municipal**: período **2013 a 2026** (cobertura efetiva do SICOR; 2026 será parcial — sinalizado na análise).
- **Painel UF agregado**: mesmo período **2013 a 2026** (a ideia inicial de cobrir 2003+ foi **abandonada** ao constatar que o OData só inicia em 2013).
- **Recorte de operações**: **todas as finalidades** (Custeio + Investimento + Comercialização). Industrialização não tem entidade própria no OData — fica fora.
- **Granularidade salva**:
  - Municipal: (ano, cd_mun_IBGE, finalidade, programa, subprograma, fonte_recurso, atividade, modalidade, produto) → valor contratado (R$), área (ha) quando aplicável.
  - UF: (ano, sigla_uf, finalidade, programa, …) → valor + nº de contratos (`QtdCusteio`/`QtdInvest`/`QtdComerc`).

**Estamos abrindo mão de**:

- **Crédito rural antes de 2013 (qualquer granularidade)**. **Razão**: a API OData do SICOR só consolida operações pós-2013, e os Anuários do Crédito Rural (BACEN/MCR) anteriores publicam agregados Brasil/região em PDFs sem padrão. Cobrir esse buraco exigiria scraping específico — custo alto e payoff baixo, dado que o ciclo recente de soja em Goiás se acelerou justamente após 2013.
- **Microdados operação-a-operação** (`bcb.gov.br/.../micrrural`). **Razão**: o agregado por município/finalidade/programa basta para correlação com LULC. Microdados servem para análise de tomador (perfil de produtor), fora do escopo desta dissertação.
- **Industrialização** (4ª finalidade do MCR). **Razão**: o OData do SICOR não expõe entidade dedicada para isso, e o volume é marginal no estado.
- **Subsídio implícito** (custo de equalização Tesouro-BACEN). **Razão**: publicado só em nível Brasil, não dá para municipalizar.
- **Deflação na coleta**. **Razão**: salvamos valores nominais — a deflação para reais de dez/2024 é aplicada no momento da análise, usando o IPCA já coletado em `sidra_1737_ipca.csv`. Mantém o coletor desacoplado da escolha de deflator.
- **Resolução temporal mensal**. **Razão**: o SICOR traz `MesEmissao`, mas para correlação com LULC anual o mês é granular demais. Salvamos mês no painel mas trabalhamos com soma anual no painel agregado.

**Estratégia de paginação (consequência das limitações do Olinda)**:
Como `$skip`/`$count` não funcionam, a coleta é segmentada por (`AnoEmissao`, `cdEstado`/`nomeUF`) — uma chamada por ano. Volumes Goiás por ano: ~15–20k registros em Custeio, ~10–17k em Investimento — bem dentro do `$top=50000`.

### 9.2 Censo Agro 2017 — implementado em 2026-04-27

**Escopo decidido e implementado**: subconjunto temático focado nos eixos da dissertação (LULC × estrutura produtiva). IDs validados via API de metadados e coletados com `coleta_sidra.py --censo-agro`.

**Tabelas SIDRA coletadas** (7 tabelas, todas período 2017):

| Tabela | Eixo | Variáveis | Classificações filtradas |
|---|---|---|---|
| 6878 | Estrutura fundiária | nº estabelecimentos, área (ha) | Tipologia (Total/Fam/Não-Fam), Atividade=Total |
| 6884 | Trabalho | nº estab com pessoal, pessoal ocupado | Tipologia (Total/Fam/Não-Fam), Sexo=Total, Atividade=Total |
| 6870 | Tecnologia (mecanização) | nº estab com tratores, nº tratores | Tipologia=Total, Potência=Total, Atividade=Total |
| 6848 | Tecnologia (adubação) | nº estabelecimentos | Tipologia=Total, Uso de adubação (6 categorias) |
| 6851 | Tecnologia (agrotóxicos) | nº estabelecimentos | Tipologia=Total, Uso de agrotóxicos (3 categorias) |
| 6910 | Pecuária (bovinos) | nº estab com bovinos, nº cabeças, vacas reprodutoras | Tipologia=Total, Grupos cabeças=Total, Atividade=Total |
| 6958 | Lavoura (temporária) | nº estab, área colhida (ha), valor produção (R$ mil) | Tipologia=Total, Produtos (soja/milho/cana), Tipo semente=Total |

**Saída principal**: `sidra_censo_agro_2017.csv` — 246 municípios × 44 colunas (37 brutas + 7 derivadas).

**Variáveis derivadas no painel**:
- `ca_area_media_estab_ha` — área média por estabelecimento
- `ca_pct_adubacao` — % estabelecimentos que fizeram adubação
- `ca_pct_agrotoxicos` — % estabelecimentos que utilizaram agrotóxicos
- `ca_pct_estab_com_bovinos` — % estabelecimentos com bovinos
- `ca_pct_estab_com_tratores` — % estabelecimentos com tratores
- `ca_pct_familiar` — % estabelecimentos de agricultura familiar
- `ca_lotacao_censo_bov_ha` — cabeças de bovino por hectare de estabelecimento

**Estamos abrindo mão de**:

- **Variáveis sociais detalhadas do produtor** (escolaridade, condição além de "familiar/não-familiar", direção dos trabalhos, sexo/cor/raça/faixa etária). **Razão**: importantes para análises sociodemográficas, mas tangenciais ao eixo LULC × econômico desta dissertação.
- **Censos Agro de 1995–96 e 2006**. **Razão**: a 6778 cobre só 2017. As séries anteriores estão em tabelas SIDRA distintas (1227–1229 para 1996; 933–935 para 2006), com schema de variáveis incompatível. Cruzar três censos exige harmonização manual de classes — só faremos se a análise pedir séries históricas estruturais.
- **Aberturas finas das classes** (ex.: tamanho do estabelecimento em todas as classes possíveis). **Razão**: pegamos as agregações mais amplas; refinar é trivial depois se necessário.
- **Contagem completa da pesquisa** (~milhares de variáveis). **Razão**: 99% delas não tocam na hipótese da dissertação. Se um achado pedir variável extra, dá para baixar pontualmente reusando o coletor.
- **Tabela 6778** (nº estabelecimentos por tipologia + área). **Razão**: a tabela 6878 já cobre nº estabelecimentos + área com as mesmas classificações, e ainda tem a quebra por sexo e idade do produtor. A 6778 seria redundante.

---

## 10. Mapas — fluxo recomendado

Divisão de papéis entre Python e QGIS, alinhada à preferência registrada nas memórias:

| Etapa | Ferramenta | Por quê |
|---|---|---|
| Exploração rápida (ver se faz sentido) | `geopandas.plot()` + `matplotlib` | reprodutível, fica no script, zero clique |
| Coropletas municipais "rápidas" para o relatório | **Pipeline #9** (`gerar_mapas_lulc_40anos.py`) | 40 PNGs coropléticos em ~2 min, tudo derivável do CSV |
| Mapas de uso da terra "tipo MapBiomas" (raster 30m) | **Pipeline #10** (`gerar_mapas_lulc_gee_40anos.py`) | Resolução nativa MapBiomas, qualidade publicável |
| Mapas de capa / figura final da dissertação | **QGIS** | controle fino de tipografia, layout impresso, legenda composta — pode importar os PNGs do #10 ou os GPKGs derivados |
| Inspeção interativa (debug de anomalias) | `folium` ou QGIS | hover, zoom, comparação visual |

**Malha base** (para mapas coropléticos não-LULC, ex.: crédito/ha, Δsoja, %familiar): `geobr.read_municipality(code_muni="GO", year=2020)` — junta com qualquer CSV pelo `cd_mun` (chave IBGE 7 dígitos). **CRS para áreas**: EPSG:5880 (SIRGAS Albers Brasil). **CRS para mapas**: EPSG:4674 (SIRGAS 2000 lat/long) é o default do `geobr`.

**Pipelines #9 e #10 já estão prontos** para os mapas LULC de cobertura/uso anuais. Para mapas temáticos novos (ex.: coropleta de crédito/ha pastagem 2023), o padrão a copiar é o pré-processamento do #9 (ler CSV → merge com malha geobr → plot matplotlib).

**Pendente**: módulo `mapas.py` com helpers reutilizáveis (carregar malha, plotar coropleta com legenda padronizada, exportar GPKG para QGIS) — refatoração que evita duplicar código entre próximos coropléticos temáticos.

---

## 11. Ambiente Python — pegadinhas conhecidas

**Versão**: Python 3.14. Sem `requirements.txt` no projeto — instalação ad-hoc via pip.

**Gotchas geoespaciais (Win+Py 3.14)**:

- `geobr` declara `shapely<=2.1.0` e `lxml<6.0.0` em metadados, mas Python 3.14 não tem wheel pré-compilada para essas versões antigas. Versões mais novas (`shapely 2.1.2`, `lxml 6.1.0`) funcionam — os limites do `geobr` são conservadores.
- Sequência de instalação que funciona:
  ```bash
  pip install --only-binary=:all: shapely
  pip install --only-binary=:all: geopandas pyogrio pyproj
  pip install --only-binary=:all: lxml html5lib
  pip install --no-deps geobr
  pip install matplotlib-scalebar
  ```
- `matplotlib_scalebar.ScaleBar` em CRS geográfico (EPSG:4326/4674, em graus) emite warning "unequal aspect ratio". Não afeta a imagem; suprimir com `ax.set_aspect("equal")` se incomodar.
- Aproximação `dx=111000` (metros por grau de latitude) na ScaleBar é aceitável para Goiás (latitudes -19° a -12°, erro <2%).
- `geobr.read_municipality()` baixa shapefile na primeira execução (~MB) e cacheia local.

**Earth Engine (Pipeline #10)**:

- Instalar com `pip install --only-binary=:all: earthengine-api` (puxa cryptography, google-auth, etc.).
- Autenticação: `earthengine authenticate` num **terminal Windows real** (não funciona dentro do Bash do Claude Code — exige interação browser + paste).
- Cada projeto Cloud precisa ser registrado em https://code.earthengine.google.com/register como Noncommercial/Academic para uso gratuito. Sem registro, o tier comercial cobra.
- Variável de ambiente `GEE_PROJECT` (ou `GEE_PROJECT_DEFAULT` no topo do script) define qual projeto usar.

---

## 12. Memórias persistidas (Claude Code)

Para que conversas futuras saibam onde estamos sem precisar rastrear este chat, há arquivos em `~/.claude/projects/.../memory/`:

- `user_role.md` — perfil acadêmico (mestrando CIAMB, stack Python/GEE, prefere pt-BR)
- `project_dissertacao.md` — estado atual: o que já foi coletado, schema, decisões metodológicas, backlog
- `reference_ambiente_python.md` — gotchas Py 3.14 + geobr/shapely/lxml + sequência de install que funciona

Arquivo índice: `MEMORY.md`. Esses arquivos são lidos automaticamente em qualquer sessão futura no mesmo diretório.

---

## 13. Como retomar o trabalho

Em qualquer sessão futura:

1. Ler este arquivo (`DOCUMENTACAO.md`) — visão geral.
2. Ler `ResumoDoBrainStorm.ini` — escopo e fontes do plano-mestre.
3. Ler `SugestaoClaude.md` — checklist de fontes e decisões cartográficas.
4. Inspecionar `data/processed/` para ver o que já está pronto.
5. Decidir o próximo bloco do backlog (seção 8 acima) e executar.

**Reproducibilidade**: todos os scripts são idempotentes (cache CSV) e auto-explicativos via docstrings. Apagar `data/raw/` força re-download; apagar `data/processed/` força re-processamento.
