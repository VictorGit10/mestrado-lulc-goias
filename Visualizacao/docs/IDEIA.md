# A ideia: linha do tempo interativa de Goias 1985-2024

> Documento conceitual. Para implementacao e estado atual, ver `IMPLEMENTACAO.md`.

## 1. Motivacao

A dissertacao analisa a dinamica de uso e cobertura da terra em Goias entre
1985 e 2024 a luz de fatores socioeconomicos. Ao longo dos pipelines #1 a #16
acumulou-se um acervo raro: 40 anos de mapas com framing identico, painel
municipal com 70 variaveis, gráficos analiticos, matrizes de transicao
pixel-a-pixel e dados de fogo, credito e producao agropecuaria.

Esses materiais existem hoje como artefatos isolados — PNGs, CSVs, parquet — e
serao apresentados na dissertacao escrita de forma estática. **A ideia e
construir uma camada interativa que reaproveite esse estoque para contar a
historia em um formato unico**, complementar (nao substituto) ao texto
academico.

A peca atende tres usos:

1. **Apoio a banca**: na defesa, oferece um overview visual do periodo
   estudado em poucos minutos, deixando o texto da dissertacao para o que so
   ele consegue (rigor metodologico, regressoes, discussao).
2. **Divulgacao pos-defesa**: artefato citavel com URL propria, com potencial
   para imprensa especializada (cerrado, agronegocio) e meio academico
   ambiental.
3. **Curriculo / portifolio**: peca de comunicacao cientifica documentada,
   util para concursos, postdocs e candidaturas.

## 2. Tese narrativa

A pergunta de pesquisa da dissertacao trata o LULC como variavel dependente e
fatores socioeconomicos como independentes. A linha do tempo amplifica isso
em uma tese narrativa em **três atos com protagonistas no territorio**:
pastagem como herança, expansão e intensificação, e conversão seletiva. Cada ato tem **um agente concreto** (pastagem, soja, frigorifico,
cerrado nordeste) e **um ou mais marcos institucionais** que mudam as regras
do jogo dentro do ato.

Quatro alternativas narrativas foram consideradas:

| Alternativa | Forca | Por que nao foi escolhida (ou como foi incorporada) |
|---|---|---|
| Conversao do Cerrado (perda de vegetacao) | Apelo publico forte | Reduz o estudo a uma tese conservacionista, perde nuance |
| Politica como motor causal (capitulos = marcos) | Alinhada a pergunta de pesquisa | Capitulos sem protagonista ficam abstratos; marcos sao mantidos como pinos da regua, nao como capitulos |
| Troca da matriz agricola (pasto → soja) | Rigor agronomico | Incorporada nos atos II-III como protagonista narrativo |
| Concentracao espacial (sudoeste puxa GO) | Mostra heterogeneidade | Incorporada na narrativa textual dos atos (sudoeste→oeste→nordeste); sem mini-mapas regionais |
| **Atos no territorio + marcos como pinos** | Une protagonista, ancoragem temporal e tese causal | **Escolhida** |

A escolha implica que cada ato e ancorado em **um protagonista no territorio**
e os marcos institucionais entram como inflexoes datadas dentro de cada
ato — nao mais como o esqueleto dos capitulos.

## 3. Audiencia primaria

Banca examinadora e pares academicos do CIAMB-UFG. Implicacoes de design:

- Tom sobrio: serifa para corpo, paleta restrita, sem animacoes decorativas
- Citacoes bibliograficas visiveis em cada marco
- Metodologia documentada e linkada
- Ingles fora do escopo do MVP (publico imediato e pt-BR)
- Estilo editorial proximo de revistas como *Pesquisa FAPESP* ou *Quarterly
  Journal of Economics*, nao de portais como *NYT The Upshot*

A peca **nao** e uma reportagem. E um anexo digital de uma dissertacao.

## 4. Decisoes de design

### 4.1 Granularidade temporal: scroll hibrido

Avaliou-se tres abordagens:

- **Ano-a-ano completo** (40 frames de peso igual) — informativo, mas cansa
  o leitor; a maioria dos anos nao tem narrativa propria.
- **Por eras** (4 capitulos, 4 mapas) — leve, mas perde a granularidade fina
  e o efeito de "frame se transformando".
- **Hibrido**: scroll ano-a-ano que **pausa** em anos-marco com card
  destacado e **acelera** entre eles. **Escolhido**.

E o padrao usado por pecas como o "Carbon Brief Global Temperatures" e
relatorios visuais do *Reuters Graphics*.

### 4.2 Tipo de mapa: coropletico municipal (PNG → WebP)

Os pipelines geraram tanto rasters MapBiomas a 30 m (`outputs/mapas_gee/`,
133 MB) quanto coropleticos municipais (`outputs/mapas/`, 9.8 MB). Para o MVP
foram escolhidos **os coropleticos**:

- Bundle 70% mais leve apos WebP (2.84 MB total)
- Granularidade municipal e a unidade da analise estatistica
- Cross-fade entre PNGs com framing identico e visualmente impecavel — nao
  ha ganho perceptivel em SVG ou tiles dinamicos para o caso de uso

Os rasters MapBiomas ficam reservados para spotlights em momentos cirurgicos
da v2 (fora do MVP).

### 4.3 Layout: mapa sticky + steps + spark-line + regua

```
┌─────────────────────────────────────────────────────────┐
│  [REGUA: 1985 ──●─────●──────●─────────●────── 2024]   │ sticky top
├──────────────────────────┬──────────────────────────────┤
│                          │                              │
│  MAPA do ano             │  Texto do ano + dados-chave  │
│  (sticky, cross-fade)    │  (em anos-marco: card        │
│                          │   politico destacado)        │
│                          │                              │
├──────────────────────────┴──────────────────────────────┤
│  [SPARK-LINE: %Veg / %Pasto / %Soja  ●ano atual ────]  │ sticky bottom
└─────────────────────────────────────────────────────────┘
```

Tres elementos persistentes (regua, mapa, spark-line) dao ao leitor
**ancoragem espacial e temporal continua** — sem isso, scroll vira tunel.

### 4.4 Series do spark-line

Tres series escolhidas:

- **% Vegetacao nativa** (floresta + savanica + campo + alagado): variavel-
  alvo da analise ambiental
- **% Pastagem**: uso dominante e em transformacao
- **% Soja (LULC MapBiomas)**: vetor da expansao agricola

Outras series foram consideradas e rejeitadas:

- **Bovinos / soja em toneladas**: relevantes mas com escala incompativel
  (saltos de 2 ordens de grandeza)
- **PIB / credito**: criticos para a tese, mas com cobertura temporal parcial
  (PIB municipal so 2002-2023, SICOR so 2013+) — confundiriam o leitor com
  series interrompidas

### 4.5 Marcos politicos selecionados

Oito ancoragens, com pinos visiveis na regua:

| Ano | Marco | Por que |
|---|---|---|
| 1985 | Inicio da serie / redemocratizacao | Baseline; ponto de comparacao |
| 1994 | Plano Real | Estabilizacao macro destrava planejamento de longo prazo |
| 1996 | Lei Kandir (LC 87/1996) | Isencao ICMS sobre exportacao gatilha primeira onda de soja |
| 2002 | Plano Safra | Sistematizacao do credito rural federal |
| 2003 | Boom commodity / China shock | Inicio do super-ciclo de precos viabiliza substituicao em massa de pasto por soja-milho |
| 2012 | Novo Codigo Florestal (Lei 12.651/2012) | Reset regulatorio sobre o Cerrado |
| 2018 | Cerrado Manifesto + reorganizacao frigorifica | Pressao de cadeia produtiva e consolidacao JBS/Marfrig/Minerva mudam a geografia da pecuaria |
| 2024 | Fim da serie | Estado atual; sintese |

A lista cresceu de 6 para 8 com a refatoracao para 3 atos: 2003 e 2018
foram adicionados para que os cortes dos atos III e V tenham ancora
institucional, nao apenas narrativa. **Crise 2008, COVID 2020 e PRONAF
seguem fora dos pinos** — entram no texto narrativo sem virar marco
visual, mantendo o spark-line legivel.

A redacao final dos cards e a bibliografia de **2003 e 2018 dependem de
revisao do orientador** — e decisao metodologica da dissertacao, nao
apenas de design.

## 5. Anti-escopo (MVP)

Coisas deliberadamente fora do MVP:

- Mobile pixel-perfect (versao linear basta)
- Raster MapBiomas em todos os frames (so coropleticos)
- Comparador A/B side-by-side
- Multilingua (pt-BR somente)
- Modo escuro
- Build pipeline (Webpack/Vite)
- Frameworks (React/Vue/Svelte)
- Animacoes de morfismo entre rasters

## 6. Riscos e mitigacoes

| Risco | Mitigacao |
|---|---|
| Banca achar "decoracao" | Tom academico sobrio + citacoes + metodologia visivel + posicionar como anexo digital |
| Marcos politicos sem consenso | Validar lista com orientador antes da redacao final |
| Bundle pesado | WebP + lazy-load (alvo < 5 MB; atual 3 MB) |
| Mobile quebra sticky | "Modo simples" linear sem sticky abaixo de 900px |
| Tempo estourar a semana | Cortar era 2014-2024 do MVP; manter 1985-2013 |
| Custo de oportunidade vs dissertacao escrita | MVP em 1 semana, decisao "expandir ou parar" no fim |

## 7. Roadmap (potencial v2, fora do MVP)

Caso o MVP funcione e o orientador aprove:

- Ano-a-ano com raster MapBiomas a 30 m em todos os frames
- Comparador A/B (split-screen) entre dois anos
- Versao tile-based (Mapbox GL / MapLibre) com zoom/pan
- Mobile responsivo completo
- Versao em ingles para alcance internacional
- Animacao de transicao pixel-a-pixel (morph entre rasters)
- Integracao com filtro por mesoregiao (Sudoeste, Sul, Leste, Norte)
