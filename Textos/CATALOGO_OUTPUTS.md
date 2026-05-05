# Catalogo de Outputs e Produtos da Analise

Documento gerado em: 2026-04-27

Este documento descreve, de forma detalhada, cada grafico, tabela e dado processado produzido pelos pipelines de analise da dissertacao. O objetivo e facilitar a consulta rapida durante a redacao dos capitulos metodologicos e de resultados.

---

## 1. Resumo dos Pipelines

| Pipeline | Script Principal | Foco Analitico | Periodo | Nivel Espacial |
|----------|-----------------|----------------|---------|----------------|
| #1 | `grafico_pastagem_pib_goias.py` | Pastagem x PIB estadual | 1985-2024 | Estado (GO) |
| #2 | `analise_expandida_goias.py` | Cobertura, rebanho, lotacao, PIB agro | 1985-2024 | Estado (GO) |
| #3 | `coleta_sidra.py` | Coleta de dados IBGE/SIDRA | Variavel | Municipal |
| #4 | `pipeline_municipal.py` | Serie municipal MapBiomas | 1985-2024 | Municipal |
| #5 | `analise_pastagem_soja.py` | Transicao Pastagem -> Soja | 1985-2024 | Municipal |
| #6 | `coleta_sicor.py` | Coleta de dados de credito rural | 2013-2025 | Municipal |
| #7 | `coleta_sidra.py` | Coleta de dados IBGE/SIDRA (Censo Agro, PAM, PPM, PIB) | Variavel | Municipal |
| #8 | `analise_credito_uso_terra.py` | Credito rural x Uso da terra | 2013-2023 | Municipal |
| #9 | `gerar_mapas_lulc_40anos.py` | 40 mapas coropleticos municipais (8 classes) | 1985-2024 | Municipal |
| #10 | `gerar_mapas_lulc_gee_40anos.py` | 40 mapas raster GEE MapBiomas (6 classes) | 1985-2024 | Estado (30m) |
| #11 | `gerar_gif_lulc.py` | GIF animado 40 anos LULC | 1985-2024 | Estado |
| #16 | `construir_painel_unificado.py` | Painel unificado wide para regressao | 1985-2024 | Municipal (246) |
| #12 | `transicoes_mapbiomas.py` | Matrizes de transicao pixel-a-pixel via GEE | 1985-2024 | Municipal (246) |
| #13 | `coleta_idhm.py` | IDH-M municipal (IPEA Data API) | 1991/2000/2010 | Municipal (246) |
| #14 | `fogo_mapbiomas.py` | Area queimada por municipio e classe LULC via GEE | 1985-2024 | Municipal (246) |
| #15 | `coleta_sidra.py --so 839` | Milho 1a e 2a safra municipal (SIDRA 839) | 2003-2024 | Municipal (246) |

---

## 2. Graficos (`outputs/`)

---

### 01_pastagem_goias_1985-2024.png

![alt text](image.png)

**Tipo:** Serie temporal univariada  
**Fonte:** MapBiomas Coleca o 10.1 (estatisticas de cobertura por estado)  
**Classe:** 15 - Pastagem  
**Periodo:** 1985 a 2024 (40 anos)  
**Nivel:** Estado de Goias (agregado dos 246 municipios)

**O que mostra:**
Evolucao anual da area ocupada por pastagem em Goias ao longo de quatro decadas. A serie e extraida da planilha de estatisticas estaduais do MapBiomas, somando todas as ocorrencias da classe 15 (Pastagem) independentemente do bioma. A area e apresentada em milhoes de hectares (Mha), com preenchimento suave sob a linha para evidenciar a magnitude absoluta.

**Interpretacao tipica:**
Permite identificar picos de expansao da fronteira pecuaria, estabilizacoes e eventuais recuos. A comparacao com outros periodos economicos ajuda a testar hipoteses sobre ciclos de valorizacao do boi gordo.

**Dados de entrada:**
- `data/raw/mapbiomas_col10_estado.xlsx` (planilha oficial do MapBiomas)

**Dados de saida:**
- `data/processed/pastagem_goias_anual.csv` — serie limpa: [ano, uf, area_pastagem_ha]

---

### 02_pastagem_pib_goias.png

![alt text](outputs/02_pastagem_pib_goias.png)

**Tipo:** Grafico de paineis empilhados (2 subplots, eixo X compartilhado)  
**Fontes:** MapBiomas Coleca o 10.1 + SIDRA/IBGE (tabela 5938, variavel 37) + IPCA (tabela 1737, variavel 63)  
**Periodo:** 2002 a 2024 (periodo de sobreposicao entre as fontes)  
**Nivel:** Estado de Goias

**O que mostra:**
Dois paineis alinhados verticalmente:
1. **Painel superior:** Serie de pastagem em Mha (mesma serie do grafico 01, mas recortada para o periodo de overlap com o PIB).
2. **Painel inferior:** PIB real do estado, deflacionado para reais de dezembro/2024 pelo IPCA acumulado.

A deflacao usa o indice acumulado do IPCA mensal, considerando o valor de dezembro de cada ano como representativo. O ano-base (dez/2024) foi escolhido por ser o ponto mais recente da serie, tornando os valores comparaveis em poder aquisitivo atual.

**Interpretacao tipica:**
Visualiza se o recuo da pastagem acompanha (ou precede) ciclos de expansao do PIB, sugerindo substituicao por atividades de maior valor agregado, ou se ambas evoluem de forma independente.

**Dados de entrada:**
- `data/processed/pastagem_goias_anual.csv`
- SIDRA tabela 5938 (PIB a precos correntes)
- SIDRA tabela 1737 (IPCA mensal)

**Dados de saida:**
- `data/processed/pib_goias_real.csv` — [ano, pib_nominal_rs, indice_dez, fator_deflator, pib_real_rs]

---

### 03_cobertura_goias_1985-2024.png

![alt text](outputs/03_cobertura_goias_1985-2024.png)

**Tipo:** Grafico de area empilhada (stackplot / area chart)  
**Fonte:** MapBiomas Coleca o 10.1  
**Periodo:** 1985 a 2024  
**Nivel:** Estado de Goias

**O que mostra:**
Evolucao das cinco principais classes de cobertura/uso do solo, agregadas em grupos metodologicos:

| Grupo | Classes MapBiomas incluidas | Cor aproximada |
|-------|----------------------------|----------------|
| Pastagem | 15 | Marrom |
| Agricultura | 39 (Soja), 19, 41, 20 (Cana), 36 | Amarelo/Dourado |
| Cerrado/Savana | 4 (Savana), 12 (Campo Nativo) | Verde claro |
| Floresta Nativa | 3 | Verde escuro |
| Area Urbana | 24 | Vermelho tijolo |

A soma dos cinco grupos representa virtualmente toda a area do estado. A sobreposicao vertical mostra a composicao percentual do territorio a cada ano.

**Interpretacao tipica:**
Permite visualizar a transicao do Cerrado nativo para pastagem e, posteriormente, para agricultura. E o grafico mais adequado para ilustrar a "matriz de transicao" conceitual: floresta -> pastagem -> lavoura.

**Dados de saida:**
- `data/processed/cobertura_goias_grupos.csv` — formato wide: [ano, Pastagem, Agricultura, Cerrado/Savana, Floresta_Nativa, Area_Urbana] em Mha

---

### 04_rebanho_bovino_goias.png

![alt text](outputs/04_rebanho_bovino_goias.png)

**Tipo:** Serie temporal univariada com preenchimento  
**Fonte:** IBGE/SIDRA — Pesquisa da Pecuaria Municipal (PPM), tabela 3939, variavel 105 (Efetivo dos rebanhos)  
**Classificacao:** Tipo de rebanho = 2670 (Bovinos)  
**Periodo:** 1985 a 2024  
**Nivel:** Estado de Goias (agregado dos 246 municipios)

**O que mostra:**
Evolucao do efetivo bovino total (cabecas) ao longo de quatro decadas. A serie e defasada em relacao a MapBiomas (publicacao anual do IBGE), mas cobre todo o periodo de interesse. Valores apresentados em milhoes de cabecas.

**Interpretacao tipica:**
Quando combinado com o grafico 01 (pastagem), permite inferir se o aumento do rebanho se deu por expansao de area (mais hectares de pasto) ou por intensificacao (mais cabecas por hectare). Picos de rebanho sem correspondente aumento de pastagem indicam melhoria genetica, confinamento ou lotacao mais densa.

**Dados de saida:**
- `data/processed/rebanho_bovino_goias.csv` — [ano, bovinos]

---

### 05_lotacao_implicita_goias.png

![alt text](outputs/05_lotacao_implícita_goias.png)

**Tipo:** Grafico de tres paineis empilhados (sharex=True)  
**Fontes:** MapBiomas (pastagem) + SIDRA PPM (rebanho bovino)  
**Periodo:** Intersecao dos periodos das duas fontes (tipicamente 1985-2024)  
**Nivel:** Estado de Goias

**O que mostra:**
Tres series alinhadas no tempo:
1. **Painel superior:** Area de pastagem (Mha) — mesma serie do grafico 01.
2. **Painel do meio:** Rebanho bovino (milhoes de cabecas) — mesma serie do grafico 04.
3. **Painel inferior:** **Lotacao implicita** (bovinos por hectare de pastagem), calculada como:

```
lotacao = rebanho_bovino / area_pastagem_ha
```

Inclui uma linha de referencia em 1,0 boi/ha, que representa uma lotacao media de referencia (nao e um otimo tecnico, apenas um marco visual).

**Interpretacao tipica:**
E o indicador-chave de intensificacao da pecuaria. Se a pastagem diminui mas o rebanho se mantem ou cresce, a lotacao sobe, indicando que o mesmo espaço esta sustentando mais animais — seja por melhor manejo, suplementacao, integracao lavoura-pecuaria ou confinamento parcial. Quedas na lotacao podem indicar abandono ou subutilizacao de areas de pastagem.

**Dados de saida:**
- `data/processed/lotacao_implicita_goias.csv` — [ano, area_ha, bovinos, lotacao]

---

### 06_pib_agro_goias.png

![alt text](outputs/06_pib_agro_goias.png)

**Tipo:** Grafico de dois paineis empilhados (sharex=True)  
**Fontes:** SIDRA/IBGE Contas Regionais (tabela 5938) + IPCA (tabela 1737)  
**Variaveis:**
- 513 = Valor Adicionado da Agropecuaria a precos correntes (mil R$)
- 37 = PIB total a precos correntes (mil R$)
**Periodo:** 2002 a 2024 (disponibilidade da tabela 5938)  
**Nivel:** Estado de Goias

**O que mostra:**
1. **Painel superior:** VA Agropecuario real (barras verdes) sobreposto ao PIB total real (linha azul), ambos em bilhoes de R$ de dezembro/2024. O VA Agropecuario e um componente do PIB, nao uma medida externa.
2. **Painel inferior:** Participacao percentual do VA Agropecuario no PIB total de Goias ao longo do tempo.

**Interpretacao tipica:**
Mostra o peso relativo do agronegocio na economia goiana. Uma queda na participacao percentual nao significa necessariamente que o agronegocio encolheu em termos absolutos; pode significar que outros setores (servicos, industria) cresceram mais rapidamente. E util para contextualizar a transicao pastagem->soja: mesmo que a soja aumente de valor, sua participacao no PIB pode se estabilizar se o restante da economia tambem crescer.

**Dados de saida:**
- `data/processed/pib_agro_goias.csv` — [ano, va_agro_nominal_rs, pib_nominal_rs, va_agro_real_rs, pib_real_rs, participacao_pct]

---

### 07_evolucao_pastagem_soja_estado.png

![alt text](outputs/07_evolucao_pastagem_soja_estado.png)

**Tipo:** Serie temporal multivariada (multi-line)  
**Fonte:** MapBiomas Coleca o 10.1 (serie municipal agregada ao nivel estadual)  
**Classes:** 15 (Pastagem) e 39 (Soja)  
**Periodo:** 1985 a 2024  
**Nivel:** Estado de Goias

**O que mostra:**
Tres linhas no mesmo espaco:
- **Pastagem (marrom):** Area total de pastagem em Mha.
- **Soja (amarelo):** Area total de soja em Mha.
- **Pastagem + Soja (preta tracejada):** Soma das duas classes, que funciona como um indicador proxy do espaco ocupado pelas duas principais atividades produtivas do estado.

**Interpretacao tipica:**
E o grafico mais direto para demonstrar a hipotese central da dissertacao: a soja avanca enquanto a pastagem recua. A soma das duas linhas revela se a expansao da soja ocorre:
- **Dentro do envelope pastagem+soja:** substituicao direta (a soma se mantem estavel).
- **Alem do envelope:** expansao sobre outras coberturas (a soma sobe).
- **Com recuo da soma:** desmatamento menor ou recuperacao de areas.

**Dados de saida:**
- `data/processed/evolucao_pastagem_soja_estado.csv` — [ano, pastagem_ha, soja_ha, total_ha]

---

### 08_evolucao_pastagem_soja_top10.png

![alt text](outputs/08_evolucao_pastagem_soja_top10.png)

**Tipo:** Small multiples (10 subplots em grade 2x5, sharex=True)  
**Fonte:** MapBiomas Coleca o 10.1 (serie municipal)  
**Periodo:** 1985 a 2024  
**Nivel:** Municipal (top 10 municipios)

**O que mostra:**
Para cada um dos 10 municipios com maior expansao absoluta de soja (delta 2024-1985), um mini-grafico com duas linhas:
- Pastagem (marrom, marcador circulo)
- Soja (amarelo, marcador quadrado)

Os eixos Y sao em mil hectares (1000 ha), permitindo comparacao de magnitude entre municipios.

**Critério de selecao:**
Os 10 municipios sao selecionados pelo maior valor de `delta_soja_ha = soja_2024 - soja_1985`, independentemente do comportamento da pastagem.

**Interpretacao tipica:**
Revela padroes locais que ficam escondidos na agregacao estadual. Alguns municipios mostram substituicao quase perfeita (pastagem cai, soja sobe na mesma proporcao); outros mostram expansao conjunta (ambas sobem). E util para selecionar casos para analise qualitativa ou entrevistas.

**Dados de saida:**
- `data/processed/evolucao_pastagem_soja_top10.csv` — serie longa dos 10 municipios selecionados

---

### 09_scatter_delta_pastagem_soja.png

![alt text](outputs/09_scatter_delta_pastagem_soja.png)

**Tipo:** Diagrama de dispersao (scatter plot) com codificacao visual multivariada  
**Fonte:** Painel municipal (246 municipios)  
**Periodo:** 1985 a 2024 (variacoes acumuladas no periodo)  
**Nivel:** Municipal (um ponto = um municipio)

**O que mostra:**
Cada ponto representa um municipio de Goias posicionado por:
- **Eixo X:** Variacao de pastagem (2024 - 1985), em mil hectares. Valores negativos = reducao de pastagem; positivos = expansao.
- **Eixo Y:** Variacao de soja (2024 - 1985), em mil hectares. Valores negativos = reducao; positivos = expansao.

**Codificacao visual adicional:**
- **Cor (escala YlOrBr):** Intensidade de soja = delta_soja / pastagem_1985. Quanto mais escuro/amarelado, maior a expansao de soja em relacao a base inicial de pastagem. A escala usa transformacao logaritmica (log10) para evitar que outliers (como Cristalina, com intensidade ~3,2) comprimam os demais valores.
- **Tamanho do ponto:** Pastagem em 1985 (maiores pontos = maior base pecuaria inicial).
- **Linha tracejada cinza:** Linha de referencia 1:1 (y = -x), que representa a situacao hipotetica em que todo hectare perdido de pastagem foi convertido em soja.

**Quadrantes conceituais:**
- **Q1 (superior direito):** Expansao simultanea — pastagem e soja ambas cresceram.
- **Q2 (superior esquerdo):** Substituicao — pastagem caiu, soja subiu. Este e o quadrante central da hipotese de transicao.
- **Q3 (inferior esquerdo):** Recuo geral — ambas reduziram.
- **Q4 (inferior direito):** Soja caiu, pastagem cresceu (casos raros, possivelmente pecuarizacao reversa).

**Anotacoes:** Os 5 municipios com maior expansao de soja sao rotulados com nome e intensidade.

**Interpretacao tipica:**
E a visualizacao mais poderosa para testar a hipotese de substituicao em escala municipal. A concentracao de pontos proximo a linha 1:1 no Q2 indica substituicao direta; dispersao para a direita no Q1 indica expansao sobre outras coberturas.

---

### 10_barras_top20_conversao.png

![alt text](outputs/10_barras_top20_conversao.png)

**Tipo:** Grafico de barras horizontais em dois paineis  
**Fonte:** Painel municipal  
**Periodo:** 1985 a 2024  
**Nivel:** Municipal (top 20)

**O que mostra:**
Dois rankings dos mesmos 20 municipios, ordenados por diferentes metricas:

1. **Painel superior — Expansao absoluta de soja:**
   Barras em mil hectares (2024 - 1985). Mostra "quem expandiu mais soja em area bruta".

2. **Painel inferior — Intensidade de expansao:**
   Barras em percentual da pastagem inicial de 1985 (`delta_soja / pastagem_1985 * 100`). Mostra "quem teve a maior expansao proporcional em relacao a sua base pecuaria original".

**Por que dois paineis?**
Um municipio grande (ex.: Rio Verde) pode ter expansao absoluta gigantesca, mas representar apenas 30% de sua pastagem inicial. Um municipio pequeno pode ter dobrado sua area sojeira (intensidade 100%+) com numeros absolutos modestos. Os dois rankings raramente coincidem.

**Interpretacao tipica:**
O painel superior e util para destacar os "motores" da expansao sojeira em Goias (onde a area e maior). O painel inferior e util para identificar municipios que passaram por transformacao estrutural profunda (de pecuaria para soja), mesmo que em area bruta nao estejam no topo.

---

### 11_heatmap_muni_periodo.png

![alt text](outputs/11_heatmap_muni_periodo.png)

**Tipo:** Mapa de calor (heatmap) com anotacoes numericas  
**Fonte:** Deltas por periodo (transicao_pastagem_soja_periodos.csv)  
**Periodos:** 1985-1995 | 1995-2005 | 2005-2015 | 2015-2024  
**Nivel:** Municipal (top 40 municipios)

**O que mostra:**
Matriz visual onde:
- **Linhas:** 40 municipios com maior expansao total de soja (1985-2024), ordenados do maior para o menor expansador.
- **Colunas:** Quatro periodos de aproximadamente 10 anos.
- **Cores (escala YlOrBr):** Intensidade da expansao de soja em mil hectares no periodo.
- **Numeros nas celulas:** Valor exato em mil hectares.

**Critério de selecao dos 40:**
Os municipios sao ordenados pela soma total de `delta_soja_ha` em todos os periodos (expansao acumulada 1985-2024).

**Interpretacao tipica:**
Revela a cronologia da expansao. Alguns municipios expandiram soja de forma constante em todos os periodos; outros concentraram o crescimento em janelas especificas (ex.: boom 2005-2015). Permite identificar "ondas" de expansao que se deslocam geograficamente pelo estado. Tambem evidencia municipios onde a expansao estagnou ou reverteu em periodos mais recentes.

**Dados de saida:**
- `data/processed/heatmap_transicao_periodos.csv` — [cd_mun, nm_mun, periodo, delta_soja_ha, delta_pastagem_ha, delta_soja_1000ha]

---

### 12_credito_uf_serie_2013-2024.png

![alt text](outputs/12_credito_uf_serie_2013-2024.png)

**Tipo:** Grafico de barras empilhadas (stacked bar chart)  
**Fonte:** SICOR/BACEN via API Olinda (datasets CusteioRegiaoUFProduto, InvestRegiaoUFProduto, ComercRegiaoUFProduto)  
**Periodo:** 2013 a 2026 (anos 2025-2026 anotados como "parcial")  
**Nivel:** Estado de Goias

**O que mostra:**
Evolucao anual do credito rural total em Goias, desagregado por finalidade:
- **Custeio (verde):** Recursos para financiar despesas de producao (insumos, mao de obra, combustivel).
- **Investimento (azul):** Recursos para bens de capital (maquinas, irrigacao, reforma de pastagens, benfeitorias).
- **Comercializacao (laranja):** Recursos para financiar a comercializacao da producao (custo de estocagem, transporte, exportacao).

Os valores estao deflacionados para reais de dezembro/2024 pelo IPCA acumulado, permitindo comparacao real de magnitude entre anos.

**Interpretacao tipica:**
Permite identificar ciclos de expansao/contracao do credito rural e a composicao entre curto prazo (custeio) e longo prazo (investimento). Picos de investimento coincidem com periodos de modernizacao ou retomada da atividade agropecuaria. A fatia de comercializacao reflete a intensidade da insercao no mercado externo ou a necessidade de estocagem.

---

### 13_scatter_credito_pastagem.png

![alt text](outputs/13_scatter_credito_pastagem.png)

**Tipo:** Diagrama de dispersao (scatter plot) com codificacao visual multivariada  
**Fontes:** SICOR municipal (2013-2023) + MapBiomas (1985-2024) + painel pastagem-soja  
**Periodo:** Creditos acumulados 2013-2023; variacao de pastagem 1985-2024  
**Nivel:** Municipal (um ponto = um municipio)

**O que mostra:**
Cada ponto representa um municipio posicionado por:
- **Eixo X:** Variacao de pastagem (2024 - 1985), em mil hectares. Valores negativos = reducao de pastagem.
- **Eixo Y:** Credito rural total acumulado (2013-2023) por hectare de pastagem media (R$/ha).

**Codificacao visual adicional:**
- **Cor (escala YlOrBr):** Intensidade de soja = delta_soja / pastagem_1985. Quanto mais escuro/amarelado, maior a expansao de soja proporcional a base pecuaria inicial.
- **Tamanho do ponto:** Pastagem media (maiores pontos = maior base pecuaria).

**Interpretacao tipica:**
Testa a hipotese de que municipios que mais reduziram pastagem sao os que receberam mais credito por hectare. Pontos concentrados no quadrante superior-esquerdo (pastagem caiu, credito/ha e alto) sugerem que o credito rural acompanhou ou financiou a transicao. Dispersao aleatoria indica desconexao entre fluxo de credito e mudanca de uso da terra.

---

### 14_composicao_produto_credito.png

![alt text](outputs/14_composicao_produto_credito.png)

**Tipo:** Serie temporal multivariada (multi-line)  
**Fonte:** SICOR/BACEN (datasets *RegiaoUFProduto) agregado por produto  
**Periodo:** 2013 a 2023 (janela completa com dados estaveis)  
**Nivel:** Estado de Goias

**O que mostra:**
Evolucao anual dos 10 produtos mais financiados pelo credito rural em Goias, em valores reais (R$ bilhoes, base dez/2024). Uma linha adicional tracejada em cinza representa a categoria "Outros" (soma dos produtos fora do top 10).

**Criterio de selecao dos 10 produtos:**
Soma total do valor real no periodo 2013-2023. Os produtos que mais concentraram recursos ao longo de toda a serie sao destacados.

**Interpretacao tipica:**
Revela a estrutura produtiva subjacente ao credito rural. Se a soja domina as linhas superiores, confirma a centralidade da lavoura no financiamento. A ascensao ou declinio de produtos ao longo do tempo reflete mudancas na matriz produtiva (ex.: entrada do milho, estabilidade do boi gordo). A categoria "Outros" indica diversificacao ou pulverizacao do credito.

---

### 15_scatter_credito_soja.png

![alt text](outputs/15_scatter_credito_soja.png)

**Tipo:** Diagrama de dispersao (scatter plot) com codificacao visual multivariada  
**Fontes:** SICOR municipal (2013-2023) + painel pastagem-soja (1985-2024)  
**Periodo:** Creditos acumulados 2013-2023; variacao de soja 1985-2024  
**Nivel:** Municipal (um ponto = um municipio)

**O que mostra:**
Cada ponto representa um municipio posicionado por:
- **Eixo X:** Credito rural total acumulado (2013-2023), em R$ bilhoes.
- **Eixo Y:** Variacao de soja (2024 - 1985), em mil hectares.

**Codificacao visual adicional:**
- **Cor (escala YlOrBr):** Intensidade de soja = delta_soja / pastagem_1985.
- **Tamanho do ponto:** Pastagem em 1985.
- **Anotacao:** Coeficiente de correlacao de Pearson entre credito total e delta soja (impresso no canto superior esquerdo).
- **Rotulos:** Top 5 municipios por expansao de soja.

**Interpretacao tipica:**
E a contrapartida direta do grafico 13, testando se o credito esta associado a expansao da soja (e nao apenas ao recuo da pastagem). Correlacao positiva e forte sugere que o credito acompanhou a fronteira agricola. Correlacao fraca ou negativa sugere que a expansao da soja ocorreu independentemente do financiamento formal (via autofinanciamento, capital de giro proprio ou recursos informais).

---

### 16_barras_credito_intensidade.png

![alt text](outputs/16_barras_credito_intensidade.png)

**Tipo:** Grafico de barras horizontais em dois paineis  
**Fonte:** SICOR municipal + MapBiomas  
**Periodo:** Ano mais recente com dados completos (tipicamente 2023)  
**Nivel:** Municipal (top 20)

**O que mostra:**
Dois rankings dos mesmos 20 municipios:

1. **Painel esquerdo — Credito por hectare de pastagem:**
   Barras empilhadas em R$/ha (custeio verde + investimento azul). Mostra "quem recebeu mais credito por unidade de area pecuaria".

2. **Painel direito — Volume total de credito:**
   Barras em R$ milhoes. Mostra "quem recebeu mais credito em valor absoluto".

**Criterio de selecao:**
Os 20 municipios com maior valor de `credito_por_ha_pastagem` no ano mais recente.

**Interpretacao tipica:**
O painel esquerdo identifica municipios onde o credito e intensivo em relacao a base pecuaria — pode indicar intensificacao (melhoramento de pasto, integracao lavoura-pecuaria) ou transicao (credito para reforma visando conversao). O painel direito mostra os grandes volumes, geralmente concentrados nos municipios ja consolidados agricola e pecuariamente. A divergencia entre os paineis destaca municipios pequenos com alta intensidade vs. municipios grandes com alto volume.

---

### 17_evolucao_credito_pastagem.png

![alt text](outputs/17_evolucao_credito_pastagem.png)

**Tipo:** Grafico de dois paineis empilhados (sharex=True)  
**Fontes:** SICOR municipal (2013-2024) + MapBiomas (2013-2024)  
**Periodo:** 2013 a 2024  
**Nivel:** Estado de Goias (painel superior); Municipal agregado (painel inferior)

**O que mostra:**
1. **Painel superior (eixo duplo):**
   - Linha marrom (eixo Y esquerdo): Area de pastagem em milhoes de hectares.
   - Linha azul (eixo Y direito): Credito rural total em R$ bilhoes (deflacionado).
   Permite comparar visualmente a trajetoria das duas series no mesmo periodo.

2. **Painel inferior (barras):**
   Correlacao anual entre `credito_por_ha_pastagem` e `delta_pastagem` (base 2013) para cada ano de 2014 a 2023.
   - Delta pastagem calculado como: `pastagem_ano - pastagem_2013`.
   - Correlacao de Pearson entre credito/ha e delta pastagem, calculada anualmente sobre os 246 municipios.

**Interpretacao tipica:**
O painel superior revela se o credito e a pastagem caminham juntos ou em direcoes opostas. Se o credito sobe enquanto a pastagem cai, pode indicar financiamento da transicao. O painel inferior testa a consistencia estatistica dessa relacao: barras positivas e significativas indicam que, naquele ano, municipios com mais credito por hectare tendiam a ter maior reducao de pastagem.

---

### 18_scatter_credito_censo_agro.png

![alt text](outputs/18_scatter_credito_censo_agro.png)

**Tipo:** Diagrama de dispersao (scatter plot) com codificacao visual multivariada  
**Fontes:** SICOR municipal (2013-2023) + Censo Agropecuario 2017 (IBGE) + painel pastagem-soja  
**Periodo:** Creditos acumulados 2013-2023; Censo Agro 2017 (corte transversal)  
**Nivel:** Municipal (um ponto = um municipio)

**O que mostra:**
Cada ponto representa um municipio posicionado por:
- **Eixo X:** Percentual de estabelecimentos agropecuarios classificados como "agricultura familiar" no Censo Agropecuario 2017.
- **Eixo Y:** Credito rural total acumulado (2013-2023) por hectare de pastagem media (R$/ha).

**Codificacao visual adicional:**
- **Cor (escala YlOrBr):** Intensidade de soja = delta_soja / pastagem_1985.
- **Tamanho do ponto:** Pastagem media 2013-2023.
- **Linhas tracejadas cinzas:** Medianas de cada eixo, dividindo o grafico em quatro quadrantes.

**Quadrantes conceituais:**
- **Superior-esquerdo:** Alto credito, alta agricultura familiar — municipios onde o PRONAF ou credito fundiario pode estar atuando fortemente.
- **Superior-direito:** Alto credito, alta agricultura patronal — municipios consolidados com grande producao capitalizada.
- **Inferior-esquerdo:** Baixo credito, alta agricultura familiar — possivel vulnerabilidade de acesso ao credito formal.
- **Inferior-direito:** Baixo credito, alta agricultura patronal — possivel autofinanciamento ou capital proprio.

**Interpretacao tipica:**
Testa a distribuicao do credito rural entre diferentes estruturas produtivas. Se pontos de alta intensidade de soja (amarelos) se concentram no quadrante superior-direito, sugere que a transicao pastagem-soja esta associada a producao patronal e capitalizada, nao a pequena propriedade familiar.

---

### 19–58. Mapas LULC Goias 1985–2024 (GEE, 6 classes)

**Tipo:** Mapas raster compostos (PNG, 200 DPI, 10×8 pol)
**Fonte:** MapBiomas Colecao 10.1 via Google Earth Engine
**Periodo:** 1985 a 2024 (40 arquivos)
**Nivel:** Estado de Goias (resolucao 30m)

**Classes agregadas (6 grupos):**

| Classe | IDs MapBiomas | Cor |
|--------|--------------|-----|
| Vegetacao Natural | 3, 4, 12 | Verde escuro (#1B8A2F) |
| Pastagem | 15 | Amarelo (#FFD700) |
| Agricultura | 9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62 | Rosa (#FF69B4) |
| Agua | 31, 33 | Azul royal (#4169E1) |
| Area Urbana | 24 | Cinza (#A0A0A0) |
| Outros | 5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75 | Bege (#D2B48C) |

**NOTA:** ID 21 (Mosaico de Agricultura ou Pastagem) foi excluido intencionalmente. No Cerrado goiano, a maioria desse pixel e pastagem extensiva, nao agricultura; inclui-lo em Agricultura enviesa o mapa.

**Dados de entrada:**
- Asset GEE: `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`

**Dados de saida:**
- `outputs/mapas_gee/cobertura_{ANO}.png` — 40 PNGs compostos (legenda, titulo, escala)
- `outputs/mapas_gee/_raw/raw_{ANO}.png` — 40 PNGs brutos GEE (2048 px, sem legenda)

---

### 59. cobertura_1985_2024.gif

**Tipo:** GIF animado (~2 fps, 500ms/frame)
**Fonte:** PNGs compostos do pipeline #10
**Periodo:** 1985 a 2024
**Nivel:** Estado de Goias

**O que mostra:**
Sequencia rapida dos 40 mapas LULC, permitindo visualizar a evolucao temporal da cobertura do solo. A expansao da pastagem e agricultura sobre a vegetacao natural fica evidente em movimento.

**Dados de saida:**
- `outputs/mapas_gee/cobertura_1985_2024.gif` (~13 MB)

---

## 3. Dados Processados (`data/processed/`)

Alem dos CSVs ja mencionados como saida de cada grafico, existem tabelas de suporte essenciais para replicacao e validacao:

### Series estaduais

| Arquivo | Conteudo | Origem | Utilizacao |
|---------|----------|--------|------------|
| `pastagem_goias_anual.csv` | Serie anual de pastagem (ha) | MapBiomas Col. 10.1 | Graficos 01, 02, 05, 07 |
| `pib_goias_real.csv` | PIB nominal e deflacionado (R$) | SIDRA 5938 + IPCA 1737 | Grafico 02 |
| `cobertura_goias_grupos.csv` | Cinco grupos de cobertura (Mha) | MapBiomas | Grafico 03 |
| `rebanho_bovino_goias.csv` | Efetivo bovino (cabecas) | SIDRA PPM 3939 | Graficos 04, 05 |
| `lotacao_implicita_goias.csv` | Pastagem, rebanho e lotacao | Calculado | Grafico 05 |
| `pib_agro_goias.csv` | VA agro, PIB total e participacao % | SIDRA 5938 + IPCA | Grafico 06 |

### Series e paineis municipais

| Arquivo | Conteudo | Origem | Utilizacao |
|---------|----------|--------|------------|
| `mapbiomas_munis_goias.csv` | Serie municipal longa (cada linha = municipio-ano-classe) | MapBiomas Col. 10.1 | Base de quase toda analise municipal |
| `painel_pastagem_soja_municipal.csv` | Painel com metricas de transicao (246 linhas) | Calculado a partir de mapbiomas_munis_goias.csv | Graficos 09, 10, 11; analise estatistica |
| `ranking_conversao_municipal.csv` | Rankings por delta, intensidade e taxa de conversao | Calculado | Graficos 08, 10, 11 |
| `transicao_pastagem_soja_periodos.csv` | Deltas por municipio e por periodo (4 periodos) | Calculado | Grafico 11; analise temporal |
| `evolucao_pastagem_soja_estado.csv` | Agregacao estadual de pastagem e soja | Calculado | Grafico 07 |
| `evolucao_pastagem_soja_top10.csv` | Serie dos 10 maiores expansores de soja | Calculado | Grafico 08 |
| `heatmap_transicao_periodos.csv` | Dados tabulares do heatmap | Calculado | Grafico 11 |

### Validacao cruzada

| Arquivo | Conteudo | Origem | Utilizacao |
|---------|----------|--------|------------|
| `validacao_soja_mapbiomas_sidra.csv` | Comparacao municipio-ano entre MapBiomas e SIDRA PAM | MapBiomas vs SIDRA 1612 | Diagnostico de qualidade dos dados de soja; apenas anos >= 2000 |

### Dados SIDRA tratados (coletados por `coleta_sidra.py`)

| Arquivo | Conteudo | Tabela SIDRA |
|---------|----------|--------------|
| `sidra_1737_ipca.csv` | IPCA mensal (variacao %) | 1737 |
| `sidra_5938_pib_municipal.csv` | PIB municipal a precos correntes | 5938 |
| `sidra_6579_populacao.csv` | Estimativas populacionais | 6579 |
| `sidra_pam1612_temporarias.csv` | Producao Agricola Municipal — lavouras temporarias (soja, milho, algodao etc.) | 1612 |
| `sidra_pam1613_permanentes.csv` | Producao Agricola Municipal — lavouras permanentes (cafe, frutas etc.) | 1613 |
| `sidra_ppm3939_rebanhos.csv` | Efetivo dos rebanhos por municipio | 3939 |
| `sidra_ppm74_leite.csv` | Producao de leite | 74 |
| `sidra_ppm94_ovos.csv` | Producao de ovos | 94 |
| `sidra_censo_agro_2017.csv` | Dados do Censo Agropecuario 2017 (consolidado) | Multiplas (6848, 6851, 6870, 6878, 6884, 6910, 6958) |

### Dados IDH-M (coletados por `coleta_idhm.py`)

| Arquivo | Conteudo | Origem | Utilizacao |
|---------|----------|--------|------------|
| `idhm_goias_municipal.csv` | IDH-M e sub-indices por municipio e ano (cd_mun, nm_mun, ano, idhm, idhm_r, idhm_l, idhm_e) | IPEA Data API (ADH_IDHM, ADH_IDHM_E, ADH_IDHM_L, ADH_IDHM_R) | Correlacao IDH x LULC; regressao espacial |

**Cobertura**: 246 municipios x 3 anos (1991, 2000, 2010) = 738 linhas. Zero missings.
**2021 pendente**: dados de PNAD Continua requerem download manual do Atlas Brasil.

### Dados SICOR tratados (coletados por `coleta_sicor.py`)

| Arquivo | Conteudo |
|---------|----------|
| `sicor_custeio_municipal.csv` | Operacoes de credito de custeio por municipio e ano |
| `sicor_invest_municipal.csv` | Operacoes de credito de investimento por municipio e ano |
| `sicor_painel_municipal.csv` | Painel consolidado de credito rural (custeio + investimento) |
| `sicor_uf_anual.csv` | Agregacao estadual anual das operacoes de credito |
| `sicor_de_para_municipio.csv` | Tabela de de-para codigo municipio SICOR -> IBGE |

### Painel de credito rural x uso da terra (gerados por `analise_credito_uso_terra.py`)

| Arquivo | Conteudo | Origem | Utilizacao |
|---------|----------|--------|------------|
| `credito_municipal_anual.csv` | Credito rural municipal anual (custeio, investimento, total, real e nominal) com pastagem e credito/ha | SICOR + MapBiomas + IPCA | Graficos 12, 13, 15, 16, 17, 18 |
| `credito_produto_anual.csv` | Credito rural estadual agregado por produto e ano (valor real) | SICOR + IPCA | Grafico 14 |
| `painel_credito_lulc.csv` | Painel integrado: credito + pastagem/soja + PIB municipal (2013-2023) | SICOR + MapBiomas + SIDRA 5938 + IPCA | Graficos 13, 15, 17, 18; analise econometrica |

---

## 4. Dados Brutos (`data/raw/`)

| Arquivo / Pasta | Descricao | Fonte |
|-----------------|-----------|-------|
| `mapbiomas_col10_estado.xlsx` | Estatisticas de cobertura do solo por estado, bioma e municipio (Colecao 10.1) | MapBiomas — download via Google Drive |
| `sidra/` | Arquivos JSON/CSV brutos retornados pelas requisicoes a API SIDRA | IBGE/SIDRA |
| `sicor/` | Arquivos CSV brutos baixados do portal de dados abertos do Banco Central | SICOR/BCB |

---

## 5. Metodologia de Deflacao

Todos os valores monetarios (PIB, VA agro, credito rural) sao deflacionados para reais de dezembro/2024 usando o IPCA acumulado.

**Procedimento:**
1. Coleta do IPCA mensal (variavel 63, tabela 1737).
2. Construcao do numero-indice cumulativo: `indice_t = produto(1 + var_mensal_i / 100)` para i = 1..t.
3. Para cada ano X, usa-se o indice acumulado em dezembro de X como representativo.
4. Fator de deflacao = `indice_dez_2024 / indice_dez_X`.

**Nota:** O ano-base (dez/2024) foi escolhido por ser o ponto mais recente da serie. Todos os valores monetarios neste projeto devem ser interpretados como "reais de dezembro de 2024".

---

## 6. Metodologia de Validacao Cruzada (MapBiomas vs SIDRA)

Para a classe Soja, foi realizada uma validacao sistematica comparando as areas do MapBiomas com as areas plantadas declaradas no SIDRA (PAM, tabela 1612, variavel 109).

**Resultados tipicos:**
- Correlacao media (Pearson) entre as fontes: ~0,85-0,95 para anos >= 2000.
- Razao mediana (MapBiomas / SIDRA): proxima de 1,0 para a maioria dos anos, com pequena tendencia de o MapBiomas subestimar levemente a soja em relacao ao SIDRA em determinados periodos.

**Implicacao:** A serie de soja do MapBiomas e considerada consistente com a fonte oficial do IBGE para analises agregadas.

---

## 6b. Painel Unificado (Pipeline #16)

### painel_unificado.parquet / painel_unificado.csv

**Caminho:** `data/processed/painel_unificado.{parquet,csv}`
**Linhas x Colunas:** 9.840 x 66 (246 municipios x 40 anos x ~50 indicadores + chaves)
**Granularidade:** wide; uma linha por (cd_mun, ano)
**Periodo:** 1985-2024 completo (NaN onde a fonte nao cobre)

**Para que serve:**
Tabela unica pronta para regressao pooled, modelo de painel ou inferencia espacial (Moran's I, LISA, `spreg`). Consolida em formato wide todas as fontes prontas do projeto, com prefixos identificando a origem (`lulc_`, `pec_`, `agri_`, `pib_`, `sicor_`, `censo2017_`).

**Cobertura por janela temporal** (% completo das colunas-chave):

| Janela | Linhas | LULC | Pecuaria | PIB | SICOR | Censo |
|---|---|---|---|---|---|---|
| 1985-2024 (completa) | 9.840 | 100% | 95% | 55% | 30% | 100% |
| 2002-2023 (PIB+LULC) | 5.412 | 100% | 100% | 100% | 50% | 100% |
| 2013-2021 (regressao plena) | ~2.185 | 100% | 100% | 100% | 100% | 100% |

**Decisoes metodologicas chave** (ver DOCUMENTACAO.md secao 7b para detalhes):
- Censo Agro 2017 replicado como atributo estatico em todos os anos.
- Top-6 lavouras: soja, milho 1a, milho 2a, cana, feijao, algodao.
- 3 categorias de pecuaria: bovinos, suinos, galinaceos. Demais excluidas.
- Leite (PPM 74) EXCLUIDO — so ha "Valor da producao" em moedas historicas.
- SICOR 2025-2026 EXCLUIDOS (parciais).
- Pre-1989: agregados externos GO incluem Tocantins; este painel cobre so os 246 munis de GO atual (divergencia ~19% no batimento, conceitualmente correta).
- IDH-M: preenchido para 1991/2000/2010 (738 de 9.840 linhas, via IPEA API). 2021 pendente (Atlas Brasil).
- Fogo: slot vazio (colunas NaN) aguardando Pipeline #14.

**Variaveis monetarias:** PIB, VA agropecuaria e SICOR deflacionados para R$ de dezembro/2024 via IPCA (SIDRA 1737, mes 12 de cada ano). Coluna em REAIS (nao Mil R$).

**Validacao:**
- Bovinos: dif 0% pos-1989 contra `rebanho_bovino_goias.csv`.
- SICOR/pastagem/soja: dif mediana 0 contra `painel_credito_lulc.csv` (2013-2023).
- Soja MapBiomas vs PAM: Pearson r = 0,971 (4.316 pares 2000-2023).

**Diagnostico de cobertura:** `outputs/diagnosticos/painel_unificado_cobertura.csv` traz % de NaN por (coluna x ano).

---

## 7. Glossario de Metricas

| Metrica | Formula | Interpretacao |
|---------|---------|---------------|
| **Delta pastagem** | `pastagem_2024 - pastagem_1985` | Variacao absoluta de area de pastagem em hectares. Negativo = reducao. |
| **Delta soja** | `soja_2024 - soja_1985` | Variacao absoluta de area de soja em hectares. Positivo = expansao. |
| **Taxa de conversao** | `delta_soja / abs(delta_pastagem)` (apenas quando delta_pastagem < 0) | Proporcao da reducao de pastagem que foi "explicada" pela expansao de soja. Taxa = 1,0 significa substituicao perfeita. Taxa > 1,0 significa que a soja expandiu alem da pastagem perdida (sobre outras coberturas). |
| **Intensidade de soja** | `delta_soja / pastagem_1985` | Quanto a soja cresceu em relacao a base inicial de pastagem. Intensidade = 1,0 significa que a soja "ocupou" 100% da pastagem inicial. |
| **Participacao soja 2024** | `soja_2024 / (soja_2024 + pastagem_2024)` | Fracao do conjunto pastagem+soja ocupada pela soja no ano mais recente. |
| **Lotacao implicita** | `bovinos / area_pastagem_ha` | Numero de cabecas de gado por hectare de pastagem. Indicador de intensificacao da pecuaria. |
| **Credito por hectare de pastagem** | `valor_total_real / pastagem_ha` | Quanto de credito rural (R$) foi desembolsado por hectare de pastagem existente no municipio. Indicador de intensificacao financiera da pecuaria ou de pressao de transicao. |
| **Produtividade soja (ton/ha)** | `agri_soja_ton / agri_soja_ha_plantada` | Rendimento medio da soja por hectare plantado (Pipeline #16). Permite comparar intensificacao tecnica entre municipios. |
| **PIB per capita real** | `pib_real_rs / populacao` | PIB municipal deflacionado por habitante (Pipeline #16). Em R$ de dez/2024. |
| **Densidade demografica** | `populacao / (lulc_area_total_ha / 100)` | Hab/km2 calculado contra a area total LULC do municipio (Pipeline #16). |
| **% pastagem (LULC)** | `lulc_pastagem_ha / lulc_area_total_ha * 100` | Fracao do municipio coberta por pastagem (MapBiomas). |
| **% agricultura (LULC)** | `lulc_agricultura_ha / lulc_area_total_ha * 100` | Fracao coberta por todas as lavouras MapBiomas somadas. |
| **% natural (LULC)** | `(lulc_floresta_nativa_ha + lulc_formacao_savanica_ha + lulc_campo_nativo_ha) / lulc_area_total_ha * 100` | Fracao com vegetacao nativa remanescente. |

---

*Fim do documento.*
