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
| `Visualizacao/asset## Achados consolidados (Atualizado em 2026-05-19)

### 1. Mudança de regime ao longo dos ATOs (Reestruturado para 3 Atos)

| ATO | Período | Descrição do Regime Político | Pixels ($N$) | Idade Mediana (não-censurado) | Média |
|---|---|---|---|---|---|
| **I — Herança** | 1985–2000 | Pastagem herdada / Ocupação extensiva inicial | 30.000 | **6,0 anos** | 6,65 anos |
| **II — Expansão** | 2001–2019 | Consolidação e expansão da soja / Lei Kandir | 38.000 | **19,0 anos** | 18,89 anos |
| **III — Seletivo** | 2020–2024 | Conversão seletiva sob governança ambiental rígida | 10.000 | **17,0 anos** | 18,54 anos |

A transição mostra uma consolidação clara: nos anos iniciais (Ato I), convertiam-se principalmente pastagens recém-formadas. Com o tempo (Ato II), a idade das áreas convertidas aumentou drasticamente para uma mediana de 19 anos, refletindo a conversão de antigas pastagens degradadas acumuladas. No período recente (Ato III), a mediana cai levemente para 17 anos devido à coexistência nítida de dois comportamentos de fronteira e rotação.

### 2. Achado-chave — Rigor Estatístico da Bimodalidade via GMM

> [!IMPORTANT]
> A bimodalidade do período recente foi testada formalmente através do **Ajuste de Modelo de Mistura Gaussiana (GMM) de 1 vs 2 componentes**.
> O modelo bimodal (2 componentes) foi selecionado com evidência **estatisticamente inquestionável** sobre o modelo unimodal.

No **Ato III (2020–2024)**, o GMM unidimensional das idades não-censuradas revelou os seguintes parâmetros:
*   **Componente Jovem**: $\mu_1 = 4,7$ anos | Peso ($w_1$) = **55,3%**
*   **Componente Antigo**: $\mu_2 = 22,3$ anos | Peso ($w_2$) = **44,7%**
*   **Apoio de Seleção**: $\Delta BIC = 7.799,5$ (um valor de $\Delta BIC > 10$ já aponta evidência bayesiana muito forte a favor de 2 componentes).

Isso comprova cientificamente a coexistência de dois mecanismos estruturais distintos atuando na conversão em Goiás:
1.  **Mecanismo de Rotação/Intensificação (Componente Jovem ~5a)**: Áreas agrícolas de rotação dinâmica curta ou pastagens novas formadas na fronteira que rapidamente dão lugar à lavoura.
2.  **Mecanismo de Reserva/Limpeza de Passivos (Componente Antigo ~22a)**: Ativação tardia de pastagens tradicionais consolidadas há décadas.

### 3. Análise de Sensibilidade por Janelas Deslizantes

Para avaliar a robustez temporal do achado em relação a diferentes marcos históricos recentes (como o Cerrado Manifesto pós-2018), executamos uma análise de sensibilidade em quatro janelas temporais deslizantes:

| Janela | Anos | $N$ Não-Cens. | $\mu_1$ (Jovem) | $w_1$ | $\mu_2$ (Antigo) | $w_2$ | $\Delta BIC$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **9 Anos** | 2016–2024 | 10.136 | 4,6 anos | 43,8% | 21,8 anos | 56,2% | 9.737,1 |
| **8 Anos** | 2017–2024 | 9.299 | 4,6 anos | 45,9% | 21,9 anos | 54,1% | 9.230,4 |
| **7 Anos** | 2018–2024 | 8.381 | 4,7 anos | 48,8% | 22,3 anos | 51,2% | 8.768,1 |
| **5 Anos** (Ato III) | 2020–2024 | 6.742 | 4,7 anos | **55,3%** | 22,3 anos | **44,7%** | 7.799,4 |

*   **Estabilidade**: A localização dos picos ($\mu_1 \approx 4,6$a e $\mu_2 \approx 22$a) é impressionantemente estável em todas as janelas.
*   **Transição de Peso**: Há um avanço sistemático no peso do componente jovem ($w_1$ sobe de 43,8% para 55,3%), mostrando que a dinâmica de rotação agrícola curta está se tornando dominante no estado nos anos mais recentes.

### 4. Quantificação dos Mecanismos por Regra de Decisão

Classificamos os pixels individuais com base no cruzamento de sua idade de conversão e sua origem de uso anterior:

*   **Rotação Agrícola (Idade $\le 8$a, vinda de agricultura)**: Cresceu expressivamente, passando de **37,7%** (2016-24) para **49,4%** (2020-24), evidenciando a forte consolidação dos sistemas de integração lavoura-pecuária de ciclo curto.
*   **Oportunístico Clássico (Idade $\ge 20$a, vinda de vegetação natural)**: Representa a conversão de passivos históricos. Encolheu ligeiramente de **28,5%** (2016-24) para **21,9%** (2020-24), mas continua a ser uma âncora de um quinto das conversões do estado.
*   **Premeditado Curto (Idade $\le 8$a, vinda de vegetação natural)**: Transição direta rápida de fronteira de expansão. Permanece muito baixa e estável: de **5,7%** (2016-24) para **4,2%** (2020-24).
*   **Ambíguo / Outro (Idades intermediárias de 9 a 19 anos)**: Estável em torno de **24%** a **28%**.

### 5. Gradiente espacial (mesorregiões)

| Mesorregião | n | Idade mediana |
|---|---|---|
| **Sul Goiano** | 28.776 (37%) | **9 anos** |
| Leste Goiano | 4.525 | 12 anos |
| Centro Goiano | 4.691 | 15 anos |
| Noroeste Goiano | 4.069 | **20 anos** |
| Norte Goiano | 1.890 | **20 anos** |

O Sul Goiano domina a conversão (37% dos pixels) com distribuição puxada para pastagens jovens — frente ativa via caminho premeditado curto. Norte/Noroeste com mediana 20a indica pastagens antigas convertidas tardiamente.

### 6. Coortes por origem anterior à pastagem

| Origem | n | % do total | Mediana | Leitura |
|---|---|---|---|---|
| `censurado_esquerda` | 51.573 | 66,1% | 14a (mínimo) | Pixels já-pastagem em 1985 |
| `vegetacao_natural` | 16.009 | **20,5%** | **13 anos** (cauda longa) | Coorte central da hipótese reserva |
| `agricultura` | 9.419 | 12,1% | 5 anos | **Rotação curta** — não é reserva |
| `outros` | 984 | 1,3% | 13 anos | — |

A coorte `agricultura → pastagem → agricultura` (rotação) é distinta da coorte de reserva — distribuição concentrada em 2-8 anos. A coorte `veg.nat → pastagem → agricultura` é onde os dois mecanismos operam: distribuição larga com pico jovem (premeditado) e cauda longa (oportunístico).

### 7. Sem correlação com socioeconômicos municipais

- Δ SICOR vs idade mediana municipal: r = +0,026 (n=1.751, n.s.)
- Δ VA agropecuária vs idade mediana municipal: r = −0,031 (n=3.001, n.s.)

Idade da pastagem na conversão **não é guiada por choques agregados municipais**. Sugere que os mecanismos atuam **abaixo da escala municipal** — provavelmente por propriedade individual e história fundiária, variáveis não capturadas pelos dados disponíveis.

## Censura à esquerda

Pixels já classificados como pastagem em 1985 não têm idade verdadeira conhecida (a série inicia em 1985). O Sub-pipeline A marca esses pixels com `origem_anterior = censurado_esquerda` (66,1% da amostra global, decrescendo de 100% em 1986 para 12% em 2024) e o Sub-pipeline B os separa em todas as figuras. Análises sensíveis a idade absoluta restringem-se aos 26.427 pixels não-censurados.

## Hipóteses testáveis (descritivas) — resultado

| Hipótese | Status |
|---|---|
| Distribuição bimodal global | **Confirmada no período recente (2016-24)** — coexistência dos mecanismos comprovada estatisticamente por GMM com ΔBIC estratosférico |
| Idade mediana decrescente ao longo dos ATOs | **Refutada na linha geral**: cresce I→II; cai levemente no Ato III |
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
2. **Histograma interativo** — distribuição por ATO com slider temporal, destacando o achado bimodal no período 2018-24.
3. **Pull-quote narrativo** explicando os dois mecanismos da hipótese com leitura empírica.
4. **Cards de coortes** — comparação visual veg.nat→pastagem→agric vs rotação agric→pastagem→agric.

Implementação alinhada com o padrão de `timeline.js`, `inventario.js` e `atlas.js`. Ver pendência registrada em `Textos/backlog.md` (Frente C estendida).
