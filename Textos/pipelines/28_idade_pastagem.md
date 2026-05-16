# Pipeline #28 — Idade da pastagem na conversão para agricultura

**Scripts**: `scripts/coleta_idade_pastagem.py` + `scripts/analise_reserva_terra.py`
**Status**: ✅ Sub-pipelines A e B concluídos (2026-05-15). Sub-pipeline C (aba na `Visualizacao/`) pendente.
**Outputs**: `data/processed/pastagem_idade_conversao.csv` (78.000 pixels), 6 PNGs em `outputs/idade_pastagem/`, 2 JSONs em `Visualizacao/assets/data/`.

## Pergunta de pesquisa

Pastagem funciona como **reserva de terra** no Cerrado goiano? A hipótese é que existem dois mecanismos coexistentes na conversão pastagem → agricultura:

- **Premeditado** — caminho `veg.nat → pastagem → agricultura` planejado desde o início; pastagem é etapa intermediária deliberada de **curta duração** (entrada barata, ocupação fundiária).
- **Oportunístico** — pastagem é o uso "default" do pecuarista; conversão para agricultura emerge de **oportunidade exógena** (oferta de arrendamento, expansão de armazém, choque de preço). Pastagem tende a ser **antiga** no momento da conversão.

A distribuição da **idade da pastagem no momento da conversão** é a assinatura empírica que distingue os mecanismos.

## Sub-pipeline A — Coleta (`coleta_idade_pastagem.py`)

Não há asset MapBiomas Pastagem (idade) integrado ao projeto. A **idade é calculada localmente em Python** a partir das 40 bandas `classification_YYYY` (1985–2024) do asset LULC Coleção 10.1 já em uso, aplicando a mesma lógica do MapBiomas platform-analysis (`codes/analysis_1_age.js`): contador que incrementa quando pixel é classe 15 (Pastagem) e reseta quando não é.

Asset: `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`.

Para cada ano de conversão t ∈ [1986, 2024]:
1. Identifica máscara de pixels que eram pastagem (ID=15) em t−1 e viraram agricultura (IDs 9,19,20,35,36,39,40,41,46,47,48,62) em t.
2. Stack com bandas `classification_1985..classification_{t-1}` + `pixelLonLat`. Aplica a máscara.
3. **Amostra via `stratifiedSample`** (não `sample` — máscara é esparsa, `sample` retorna pouquíssimos hits) com classe artificial = 1 onde a máscara está ativa, `numPoints=2000`, `seed=42`.
4. Em Python: percorre as bandas vetorialmente para calcular idade da pastagem em t−1 e classe imediatamente anterior à fase pastagem.
5. Overlay local com geopandas para anexar `cd_mun`/`nm_mun` e `mesorregiao` (via `mapeamento_mesorregioes.csv`).

Robustez: `tileScale` escala 8 → 16 → 32 com timeouts 240s/480s/720s via `concurrent.futures` em caso de travamento no GEE. Caches por ano em `data/cache/idade_pastagem/idade_<YYYY>.csv` permitem retomar coleta interrompida.

**Saída** (`data/processed/pastagem_idade_conversao.csv`):

| Coluna | Conteúdo |
|---|---|
| `ano_conversao` | Ano da transição pastagem → agricultura |
| `cd_mun`, `nm_mun` | Município IBGE 2020 |
| `mesorregiao` | Nome da mesorregião IBGE 2017 |
| `idade_pastagem_anos` | Anos consecutivos como pastagem imediatamente antes da conversão |
| `classe_antes_id` | Classe MapBiomas no ano anterior ao início da fase pastagem |
| `origem_anterior` | Categórico: `vegetacao_natural` / `agricultura` / `outros` / `censurado_esquerda` |
| `lon`, `lat` | Coordenadas do pixel amostrado |

## Sub-pipeline B — Análise (`analise_reserva_terra.py`)

Consome `pastagem_idade_conversao.csv` e produz:

| Output | Conteúdo |
|---|---|
| `distribuicao_global.png` | Histograma de idade na conversão, separando censurados à esquerda |
| `distribuicao_por_ato.png` | 5 painéis por ATO político (I–V), 1985–2024 |
| `distribuicao_por_mesorregiao.png` | 5 painéis por mesorregião IBGE 2017 |
| `coortes_vegnat_pastagem_agric.png` | Compara `veg.nat → pastagem → agric` vs `agric → pastagem → agric` (rotação) vs `outros` |
| `idade_temporal_marcos.png` | Mediana e média anual com linhas verticais em 1995/2012/2018 |
| `idade_x_socioeconomicos.png` | Idade mediana municipal × Δ SICOR e Δ VA agro |
| `data/processed/idade_pastagem_estatisticas.csv` | n / mediana / média / p10 / p90 por escopo (global, ATO, mesorregião, origem) |
| `Visualizacao/assets/data/idade_pastagem_municipal.json` | Idade mediana/média/n por município, consumido pela Sub-pipeline C |
| `Visualizacao/assets/data/idade_pastagem_histograma.json` | Histograma por ATO com bins/counts/mediana, consumido pela Sub-pipeline C |

## Achados consolidados (2026-05-15)

### 1. Mudança de regime ao longo dos ATOs

| ATO | Período | Idade mediana (não-censurado) |
|---|---|---|
| I — Heranca Cerradeira | 1985-93 | **4 anos** |
| II — Plano Real / Lei Kandir | 1994-02 | **11 anos** |
| III — Boom de Commodities | 2003-11 | **19 anos** |
| IV — Código Florestal | 2012-17 | **27 anos** (pico) |
| V — Cerrado Manifesto | 2018-24 | **22 anos** |

A subida 1986-2019 tem componente mecânico (série inicia em 1985), mas a estabilização ~28a em 2014-2018 e a queda pós-2020 (com mediana caindo para 6-7a em 2022 e 2024) são reais e indicam mudança no padrão de conversão.

### 2. Achado-chave — distribuição BIMODAL no ATO V

Os histogramas dos ATOs I-IV são **unimodais** (uma mecânica dominante por vez). O **ATO V (Cerrado Manifesto 2018-24) tem distribuição claramente bimodal**: dois picos, um em ~5 anos e outro em ~35 anos.

Esta é a **assinatura empírica direta** da coexistência dos dois mecanismos da hipótese:
- **Pico jovem (≈5a)** — mecanismo premeditado. Fronteira interna em consolidação convertendo pastagens novas. Coerente com pressão das tradings pós-Cerrado Manifesto para "agriculturizar sem novo desmatamento".
- **Pico antigo (≈35a)** — mecanismo oportunístico. Produtores tradicionais ativando reservas históricas em resposta a choques exógenos.

### 3. Gradiente espacial (mesorregiões)

| Mesorregião | n | Idade mediana |
|---|---|---|
| **Sul Goiano** | 28.776 (37%) | **9 anos** |
| Leste Goiano | 4.525 | 12 anos |
| Centro Goiano | 4.691 | 15 anos |
| Noroeste Goiano | 4.069 | **20 anos** |
| Norte Goiano | 1.890 | **20 anos** |

O Sul Goiano domina a conversão (37% dos pixels) com distribuição puxada para pastagens jovens — frente ativa via caminho premeditado curto. Norte/Noroeste com mediana 20a indica pastagens antigas convertidas tardiamente.

### 4. Coortes por origem anterior à pastagem

| Origem | n | % do total | Mediana | Leitura |
|---|---|---|---|---|
| `censurado_esquerda` | 51.573 | 66,1% | 14a (mínimo) | Pixels já-pastagem em 1985 |
| `vegetacao_natural` | 16.009 | **20,5%** | **13 anos** (cauda longa) | Coorte central da hipótese reserva |
| `agricultura` | 9.419 | 12,1% | 5 anos | **Rotação curta** — não é reserva |
| `outros` | 984 | 1,3% | 13 anos | — |

A coorte `agricultura → pastagem → agricultura` (rotação) é distinta da coorte de reserva — distribuição concentrada em 2-8 anos. A coorte `veg.nat → pastagem → agricultura` é onde os dois mecanismos operam: distribuição larga com pico jovem (premeditado) e cauda longa (oportunístico).

### 5. Sem correlação com socioeconômicos municipais

- Δ SICOR vs idade mediana municipal: r = +0,026 (n=1.751, n.s.)
- Δ VA agropecuária vs idade mediana municipal: r = −0,031 (n=3.001, n.s.)

Idade da pastagem na conversão **não é guiada por choques agregados municipais**. Sugere que os mecanismos atuam **abaixo da escala municipal** — provavelmente por propriedade individual e história fundiária, variáveis não capturadas pelos dados disponíveis.

## Censura à esquerda

Pixels já classificados como pastagem em 1985 não têm idade verdadeira conhecida (a série inicia em 1985). O Sub-pipeline A marca esses pixels com `origem_anterior = censurado_esquerda` (66,1% da amostra global, decrescendo de 100% em 1986 para 12% em 2024) e o Sub-pipeline B os separa em todas as figuras. Análises sensíveis a idade absoluta restringem-se aos 26.427 pixels não-censurados.

## Hipóteses testáveis (descritivas) — resultado

| Hipótese | Status |
|---|---|
| Distribuição bimodal global | **Confirmada apenas no ATO V** — coexistência dos mecanismos surge no Cerrado Manifesto |
| Idade mediana decrescente ao longo dos ATOs | **Refutada na linha geral**: cresce I→IV; cai parcialmente em V |
| Idade menor no Sul de GO vs Norte/Nordeste | **Confirmada**: Sul 9a, Norte/Noroeste 20a |
| Coorte veg.nat→pastagem→agric com mediana <15a | **Confirmada** (mediana 13a, cauda longa) |
| Correlação Δ SICOR vs idade mediana | **Sem correlação** — mecanismos operam abaixo da escala municipal |

## Decisão metodológica chave (D10)

**Não existe asset MapBiomas Pastagem separado** integrado ao pipeline. Idade é calculada localmente em Python a partir das bandas `classification_YYYY` extraídas via `stratifiedSample`. Esta decisão simplifica enormemente o pipeline e evita o encadeamento pesado de 35+ operações em `ee.Image` que estourava o limite computacional do servidor GEE (testado e rejeitado na primeira versão do script).

## Limitações

- **Identificação causal não é reivindicada** — análise é descritiva por idade. Discriminação dos mecanismos é interpretativa.
- **Sem dados de propriedade (CAR/SICAR)** — não é possível testar diretamente a hipótese sobre arrendamento.
- **Censura à esquerda 66,1%** — afeta intensamente os anos iniciais (1986–~2000); leitura interpretativa restringe-se ao subconjunto não-censurado (n=26.427).
- **Salto 2020→2022 (mediana 31a→7a)** — pode incluir componente de reclassificação de classes de agricultura entre coleções MapBiomas. Vale investigação caso a leitura se torne central na dissertação.
- **stratifiedSample com classe única** retorna até `numPoints` pixels, mas pode amostrar mais de uma classe quando há ruído na máscara — em prática isso não tem efeito porque `classe_mask` só assume 1 onde há transição P→A.

## Como rodar

```bash
# Validação rápida (200 pixels em 2020, ~2 min)
python scripts/coleta_idade_pastagem.py --teste

# Coleta completa (1986-2024, 78k pixels, ~80 min)
python scripts/coleta_idade_pastagem.py

# Retomada (reusa caches em data/cache/idade_pastagem/)
python scripts/coleta_idade_pastagem.py        # idempotente; pula anos com cache

# Análise (figuras + estatísticas + JSONs)
python scripts/analise_reserva_terra.py
```

## Sub-pipeline C (pendente) — Aba na visualização web

Os JSONs `idade_pastagem_municipal.json` (~41 KB, idade mediana/média/n por município) e `idade_pastagem_histograma.json` (~3 KB, histograma por ATO) já estão gerados em `Visualizacao/assets/data/`.

Componentes propostos para a aba nova em `Visualizacao/index.html`:

1. **Mapa coroplético municipal** — idade mediana da pastagem no momento da conversão, com classes em quantis (jovem/médio/antigo) e toggle por ATO.
2. **Histograma interativo** — distribuição por ATO com slider temporal, destacando o achado bimodal do ATO V.
3. **Pull-quote narrativo** explicando os dois mecanismos da hipótese com leitura empírica.
4. **Cards de coortes** — comparação visual veg.nat→pastagem→agric vs rotação agric→pastagem→agric.

Implementação alinhada com o padrão de `timeline.js`, `inventario.js` e `atlas.js`. Ver pendência registrada em `Textos/backlog.md` (Frente C estendida).
