# Pipeline #28 — Idade da pastagem na conversão para agricultura

**Scripts**: `export_cubo_mapbiomas_go.py` → `baixa_export_drive.py` → `processa_cubo_idade.py` → `analise_reserva_terra.py`
(legado: `coleta_idade_pastagem.py`, a amostra — mantido para reprodutibilidade e comparação)
**Status**: ✅ Censo de pixels concluído (2026-07-21). Sub-pipeline C (aba na `Visualizacao/`) atualizado.
**Outputs**: `data/processed/pastagem_idade_censo.parquet` (**44.639.028 eventos de conversão**), 9 PNGs em `outputs/idade_pastagem/`, 3 JSONs em `Visualizacao/assets/data/`.

---

# O que a família da idade estabelece

*Seção-hub (21/jul/2026). Se você só vai ler uma coisa sobre idade da pastagem,
leia isto. `#28C`, `#33` e `#40` apontam para cá em vez de cada um repetir suas
próprias ressalvas. O histórico de por que os números mudaram está no bloco
seguinte e em [`censo_vs_amostra.md`](../metodologia/censo_vs_amostra.md) — é
registro forense para banca, não leitura necessária para entender o achado.*

## Primeiro: três coisas diferentes se chamam "idade do pasto"

Quase toda contradição aparente nesta família vem de cruzar duas destas. São
quantidades distintas, cada uma legítima para uma pergunta. **Nunca citar uma no
lugar da outra.**

| | responde | onde | censurados |
|---|---|---|---|
| **Forma** | *existem dois mecanismos?* | #28, #28C | **exclui** — a pilha de censura no horizonte quebraria o GMM |
| **Nível** | *quão velho é o pasto convertido aqui?* | #33 (Ato III) | **inclui**, e só onde é identificável |
| **Peso** | *qual mecanismo domina onde?* | #40 (índice jovem) | mistura, não idade |

Os **níveis** não são comparáveis entre #28C e #33 — o #28C descreve a
subpopulação observável. A **ordenação** é robusta nas pontas (Sul e Leste
jovens, Noroeste e Norte velhos) e **instável no Centro Goiano**, que tem 70,9%
de censura e por isso um não-censurado pequeno e selecionado-jovem.

## O achado

Dois mecanismos de conversão pasto → lavoura **coexistem em toda parte** de Goiás:

- **Giro** (μ₁ ≈ **4,4 anos**) — pasto em rotação ativa: ILP, ou pasto como etapa
  antes da lavoura.
- **Reserva** (μ₂ ≈ **22,9 anos**) — pasto antigo sendo capitalizado, a "reserva
  de terra" acionada.

E o balanço entre eles pende em dois eixos: no **espaço** (Sul/Leste → giro;
Noroeste/Norte → reserva) e no **tempo** (giro ganhando peso, w₁ de 31,5% em
2016–24 para 51,5% em 2020–24 — alcança a reserva, não a supera).

> ## 🛑 O eixo TEMPORAL está suspenso (21/jul/2026) — leia antes de citar
>
> O [#28D](28D_deriva_mosaico.md) mostrou que o objeto medido pelo #28 **não é
> constante ao longo da série**: a saída da pastagem migra do rótulo
> "agricultura" para "Mosaico de Usos" (razão 0,6 em 2015 → **32,5 em 2024**),
> `P→agricultura` cai **92%**, e o SIDRA registra a soja **crescendo 38%** na
> mesma janela.
>
> **O que isso derruba:** a tendência `w₁ 31,5% → 51,5%` sobe monotonicamente com
> a exposição da janela à deriva (20,8% em 2014-18, base pré-deriva → 51,5% na
> janela inteiramente derivada). **Não citar como achado temporal.**
>
> **O que fica sob suspeita e precisa de re-auditoria:** a frase "a mudança é
> temporal, não geográfica" (19,6% × 1,3%) tem os **dois** lados comprometidos —
> a subida Ato I→II é horizonte (a mediana pré-2020 é ~55% de `ano−1985`, dp
> 7 pp) e a queda no Ato III é deriva. O contraste tempo × espaço precisa ser
> refeito em janelas limpas antes de voltar ao texto.
>
> **O que sobrevive intacto:** a **bimodalidade** com modos estáveis (μ₁≈4-5a,
> μ₂≈21-23a em *todas* as janelas, derivadas ou não; confirmada sob a união em
> 23/jul). **⚠️ Correção (23/jul):** eu escrevia aqui que o **gradiente Sul→Norte**
> do [#28C](28C_bimodalidade_regional.md) "é transversal — a deriva é temporal". A
> re-checagem sob `pasto→(agric∪mosaico)` mostrou que o gradiente latitudinal de
> *idade* **é artefato** (amplitude 7a→2a): a seleção agricultura×Mosaico atua
> *dentro* de um período. O transversal que sobrevive é a **coexistência bimodal**,
> não o gradiente de idade. Ver o WARNING do #28C.

> **O ponto que merece o centro da dissertação: a mudança é temporal, não
> geográfica.** O tempo explica **19,6%** da separação jovem/velho contra
> **1,3%** do espaço (mesorregião), e **cada** unidade é bimodal por dentro —
> 5/5 mesorregiões e 162/164 AMCs. Ou seja, a leitura intuitiva de "dois
> Goiáses, cada um com sua lógica" **é falsa**: todo lugar faz as duas coisas, e
> o que está mudando é o balanço, virando para o giro em todo o estado ao mesmo
> tempo, com inclinação latitudinal. O que a fronteira do Norte tem de diferente
> não é uma lógica própria — é mais pasto velho a capitalizar e mais Cerrado
> restante (#39).

## O que sobreviveu a cinco rodadas de correção

Envelope amostral, classe 21, migração para censo, bug de peso do #28C e censura
do #33 — cinco episódios com métodos e dados diferentes. Não moveram:

| | |
|---|---|
| Bimodalidade existe | μ₁ ≈ 4,4a e μ₂ ≈ 22,9a, estáveis em 4 janelas |
| Não é composição regional | 5/5 mesos e 162/164 AMCs bimodais **por dentro** |
| ~~Tempo ≫ espaço~~ | 🛑 **suspenso** — 19,6% × 1,3%, mas os dois lados do eixo temporal estão comprometidos (horizonte antes de 2020, deriva depois). Re-auditar. [#28D](28D_deriva_mosaico.md) |
| ~~Modo jovem ganha peso~~ | 🛑 **derrubado** — w₁ 31,5% → 51,5% acompanha a deriva do destino, não o tempo. [#28D](28D_deriva_mosaico.md) §5.1 |
| Gradiente nas pontas | Sul/Leste jovens × Noroeste/Norte velhos, em todo estimador |

## O que foi aposentado — não citar

1. ~~"A rotação está se tornando dominante"~~ → **alcança o empate** (51,5% ×
   48,5%). Morreu na migração para censo.
2. ~~Idade mediana por mesorregião agregando 1986–2024~~ (era "Sul 9a → Norte
   20a", no #33) → **não identificada**: a censura mede horizonte, não idade, e é
   maior no Sul (70,9%) que no Norte (41,9%) porque o Sul converteu cedo.
   Identificado só no **Ato III**: Sul 16a · Leste 16a · Norte 27a · Centro 28a ·
   Noroeste 31a.
3. ~~"Sem efeito próprio do no-till"~~ (#40) → **não estabelecido**. Era
   atenuação por erro de medida: nos mesmos municípios, p vai de 0,413 a 0,031
   com a idade medida pelo censo.

## Limites estruturais — permanentes, não pendências

- **Censura à esquerda de 64,1%.** É o início da série MapBiomas (1985), não
  defeito de método. Não há o que corrigir.
- **Não existe série temporal de idade na conversão.** Atos I e II não são
  identificáveis (horizonte curto demais); só o corte transversal recente é
  mensurável. Portanto **não afirmar** que a idade do pasto convertido subiu ou
  caiu ao longo do tempo.
- **Erro de classificação do MapBiomas** passou a ser a maior incerteza restante,
  já que o erro amostral saiu de cena com o censo.

---

> ## Reconstrução de 2026-07-21 — de amostra para censo
>
> O #28 deixou de ser amostra (2.000 px/ano) e passou a ser **censo**: todos os
> pixels de Goiás que sofreram transição pastagem → agricultura, 1986–2024.
> São **44.639.028 eventos** (1.016× a amostra), cobrindo **3.817.080 ha =
> 11,2% do estado**, em **244 dos 246 municípios**.
>
> A mudança foi motivada por **três defeitos** encontrados na amostra, dois
> deles graves e um deles nunca detectado antes:
>
> **1. Envelope amostral.** A coleta amostrava o *retângulo envolvente* de
> Goiás, não o polígono: **34.049 dos 78.000 pixels (43,7%) caíam fora do
> estado** (verificado por point-in-polygon: 99,991% realmente fora, só 3 eram
> falha de sjoin). Corrigido em 20/jul filtrando `cd_mun != 0`.
>
> **2. Classe 21 (Mosaico de Usos) ausente do `GRUPO_MAP`.** Combinada com um
> `.fillna("censurado_esquerda")`, isso rotulava como **censurado** — "idade
> desconhecida" — pixels cuja idade era perfeitamente conhecida. Eram 4.898 px
> (11,1%) da amostra estadual e são **11,83% do censo**. Consequência: a
> censura publicada (74,9%) estava superestimada — o valor real é **63,7%** na
> amostra e **64,1%** no censo — e como *todas* as análises-manchete do #28
> rodam sobre o subconjunto não-censurado, elas usaram dois terços dos dados a
> que tinham direito. Pior: os excluídos não eram aleatórios, eram
> especificamente os de origem mista agricultura/pastagem.
>
> **3. Ponderação entre anos.** A amostra alocava 2.000 px/ano
> independentemente de quanta conversão houve naquele ano. Comparando com o
> censo, as medianas **ano a ano** são praticamente idênticas (diferença média
> −0,09 a, máx |2| a) — ou seja, a amostragem *dentro* de cada ano era sadia —
> mas os **agregados por Ato** divergem, porque a composição está errada: a
> amostra deu a 2024 peso 24,5% quando o real é 11,2%, e a 2020 peso 22,2%
> quando o real é 43,2%. Como 2020 tem mediana 20 a e 2024 tem 5 a, o Ato III
> foi puxado para baixo (mediana 6 na amostra contra **8** no censo).
>
> **O que sobrevive ao censo:** a bimodalidade e a posição dos dois modos
> (μ₁ ≈ 4,4 a e μ₂ ≈ 22,9 a, notavelmente estáveis em todas as janelas), o
> gradiente Sul(jovem) → Norte(velho), e a *direção* da tendência (componente
> jovem ganhando peso ao longo do tempo).
>
> **O que muda:** os pesos dos dois componentes, a decomposição de mecanismos
> (ver §4) e a taxa de censura. Ver a tabela comparativa no fim desta página.
>
> **Leitura obrigatória sobre o ΔBIC:** com censo, n é a população e qualquer
> desvio ínfimo da unimodalidade produz ΔBIC astronômico (ordem de 10⁶). Isso
> reflete o tamanho de n, **não** força de evidência. O censo torna μ e w mais
> *precisos*; não torna a bimodalidade "mais provada". Não citar ΔBIC do censo
> como grau de confiança.

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
| `origem_anterior` | Categórico: `vegetacao_natural` / `mosaico` / `agricultura` / `agua` / `area_urbana` / `outros` / `sem_dado_anterior` / `censurado_esquerda` |
| `lon`, `lat` | Coordenadas do pixel amostrado |

### Saída do censo (`data/processed/pastagem_idade_censo.parquet`)

Tabela de contingência, **não** uma linha por pixel:

| Coluna | Conteúdo |
|---|---|
| `ano_conversao`, `cd_mun`, `nm_mun` | Chaves |
| `idade_pastagem_anos` | 1..39 |
| `classe_antes_id`, `origem_anterior` | Origem anterior à fase pastagem |
| `n_pixels` | **Peso**: quantos pixels caem nesta célula |
| `area_ha` | Área de solo, corrigida por cos(lat) |

As quatro variáveis do #28 são discretas e de baixa cardinalidade (39 anos × 246 munis × 41 idades × ~32 classes), então o censo completo cabe **sem perda nenhuma** em 405.771 células. Toda estatística — mediana, percentil, GMM, Kaplan-Meier — é recuperável exatamente desses pesos. Guardar 44,6 milhões de linhas individuais só desperdiçaria disco.

## Sub-pipeline B — Análise (`analise_reserva_terra.py`)

Consome `pastagem_idade_conversao.csv` e produz:

| Output | Conteúdo |
|---|---|
| `distribuicao_global.png` | Histograma de idade na conversão, separando censurados à esquerda. **Lê como unimodal** (pico jovem + cauda longa dominam) — usar para a censura, **não** como prova da bimodalidade; para os dois modos ver `bimodalidade_unidade_ato.png` (#28C) |
| `distribuicao_por_ato.png` | 5 painéis por ATO político (I–V), 1985–2024 |
| `distribuicao_por_mesorregiao.png` | 5 painéis por mesorregião IBGE 2017 |
| `coortes_vegnat_pastagem_agric.png` | Compara `veg.nat → pastagem → agric` vs `agric → pastagem → agric` (rotação) vs `outros` |
| `idade_temporal_marcos.png` | Mediana e média anual com linhas verticais em 1995/2012/2018 |
| `idade_x_socioeconomicos.png` | Idade mediana municipal × Δ SICOR e Δ VA agro |
| `data/processed/idade_pastagem_estatisticas.csv` | n / mediana / média / p10 / p90 por escopo (global, ATO, mesorregião, origem) |
| `Visualizacao/assets/data/idade_pastagem_municipal.json` | Idade mediana/média/n por município, consumido pela Sub-pipeline C |
| `Visualizacao/assets/data/idade_pastagem_histograma.json` | Histograma de idade por Ato, consumido pela Sub-pipeline C |
| `Visualizacao/assets/data/idade_pastagem_gmm.json` | Parâmetros do GMM por janela deslizante |

## Achados consolidados (censo, 2026-07-21)

### 1. Mudança de regime ao longo dos ATOs

| ATO | Período | Descrição do Regime Político | Pixels não-cens. ($N$) | Idade Mediana | Média | P10–P90 |
|---|---|---|---|---|---|---|
| **I — Herança** | 1985–2000 | Pastagem herdada / Ocupação extensiva inicial | 3.459.385 | **4,0 anos** | 5,18 anos | 2–10 |
| **II — Expansão** | 2001–2019 | Consolidação e expansão da soja / Lei Kandir | 11.592.447 | **14,0 anos** | 14,17 anos | 3–26 |
| **III — Seletivo** | 2020–2024 | Conversão seletiva sob governança ambiental rígida | 952.698 | **8,0 anos** | 13,38 anos | 3–31 |

Nos anos iniciais (Ato I), convertiam-se pastagens recém-formadas (mediana 4 anos). No Ato II a idade sobe para 14 anos — conversão do estoque de pastagens antigas acumuladas. No Ato III a mediana recua para 8 anos, mas a média (13,4) e o P90 (31 anos) mostram que **não é um recuo geral**: é a coexistência de uma massa jovem com uma cauda muito longa. É a assinatura dos dois mecanismos, não a substituição de um pelo outro.

> A amostra dava 6 anos no Ato III. A diferença para os 8 do censo é
> integralmente de **composição**, não de amostragem: as medianas ano a ano são
> idênticas entre amostra e censo (2020: 20 e 20; 2021: 11 e 11; 2022: 4 e 4;
> 2024: 5 e 5), mas a amostra sobrepesava 2024 e subpesava 2020.

### 2. Achado-chave — Rigor Estatístico da Bimodalidade via GMM

> [!IMPORTANT]
> A bimodalidade é **descritiva e robusta**: os dois modos aparecem em todas as
> janelas testadas e suas posições mal se movem. Mas o ΔBIC do censo **não é
> medida de confiança** — ver a ressalva no cabeçalho. Com n = 952.698 no Ato
> III, o ΔBIC de 844.789 diz sobretudo que n é enorme.

**Figura da bimodalidade:** a prova *visual* dos dois modos está em `outputs/idade_pastagem/bimodalidade_unidade_ato.png` (Pipeline #28C) — 15 painéis (5 mesorregiões × 3 recortes) com as duas componentes GMM tracejadas e o marcador ● *bimodal*. O histograma global `distribuicao_global.png` **não** revela os dois modos sozinho: o pico jovem e a cauda longa o fazem parecer unimodal. Ao apresentar a Perna 2, use a figura do #28C, não o histograma global.

No **Ato III (2020–2024)**, o GMM unidimensional das idades não-censuradas ($n$ = 952.698):
*   **Componente Jovem**: $\mu_1 = 4,4$ anos | Peso ($w_1$) = **51,5%**
*   **Componente Antigo**: $\mu_2 = 22,9$ anos | Peso ($w_2$) = **48,5%**

Os dois componentes estão **em equilíbrio** no período recente — não há um dominante. A amostra (corrigida) sugeria 62,3% / 37,7%, já uma dominância do jovem, que o censo não confirma.

Isso comprova cientificamente a coexistência de dois mecanismos estruturais distintos atuando na conversão em Goiás:
1.  **Mecanismo de Rotação/Intensificação (Componente Jovem ~5a)**: Áreas agrícolas de rotação dinâmica curta ou pastagens novas formadas na fronteira que rapidamente dão lugar à lavoura.
2.  **Mecanismo de Reserva/Limpeza de Passivos (Componente Antigo ~22a)**: Ativação tardia de pastagens tradicionais consolidadas há décadas.

### 3. Análise de Sensibilidade por Janelas Deslizantes

Para avaliar a robustez temporal do achado em relação a diferentes marcos históricos recentes (como o Cerrado Manifesto pós-2018), executamos uma análise de sensibilidade em quatro janelas temporais deslizantes:

| Janela | Anos | $N$ Não-Cens. | $\mu_1$ (Jovem) | $w_1$ | $\mu_2$ (Antigo) | $w_2$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **9 Anos** | 2016–2024 | 3.455.514 | 4,2 anos | 31,5% | 22,5 anos | 68,5% |
| **8 Anos** | 2017–2024 | 2.833.330 | 4,3 anos | 33,7% | 22,8 anos | 66,3% |
| **7 Anos** | 2018–2024 | 2.088.268 | 4,5 anos | 37,1% | 23,5 anos | 62,9% |
| **5 Anos** (Ato III) | 2020–2024 | 952.698 | 4,4 anos | **51,5%** | 22,9 anos | **48,5%** |

*   **Estabilidade**: A posição dos picos ($\mu_1 \approx 4,2$–$4,5$a e $\mu_2 \approx 22,5$–$23,5$a) é notavelmente estável em todas as janelas. **Este é o achado robusto** e sobrevive intacto à troca de amostra por censo.
*   **Transição de Peso**: $w_1$ sobe de 31,5% para 51,5% — o componente jovem **ganha peso sistematicamente**, e a direção é inequívoca. Mas ele apenas *alcança* o antigo no período recente; não passa a dominar. A amostra (corrigida) sugeria 47,1% → 62,3%, o que teria justificado falar em dominância. O censo não sustenta essa leitura.
*   ΔBIC omitido de propósito: ver a ressalva no cabeçalho.

### 4. Quantificação dos Mecanismos por Regra de Decisão

Classificamos os pixels não-censurados cruzando idade de conversão com origem anterior:

*   **Rotação Agrícola (Idade $\le 8$a, vinda de agricultura)**: sobe de **21,3%** (2016-24) para **43,0%** (2020-24) — **dobra**, e é a mudança mais forte da decomposição.
*   **Mosaico de Usos (origem mista agricultura/pastagem)**: recua de **30,0%** para **19,8%**. Categoria que **não existia** nas versões anteriores desta página: a classe 21 estava ausente do `GRUPO_MAP` e esses pixels eram contados como censurados.
*   **Oportunístico Clássico (Idade $\ge 20$a, vinda de vegetação natural)**: de **23,9%** para **16,6%**. Encolhe, mas segue ancorando um sexto das conversões.
*   **Premeditado Curto (Idade $\le 8$a, vinda de vegetação natural)**: baixo e em queda, de **4,6%** para **2,5%**.
*   **Ambíguo / Outro**: de **20,2%** para **18,1%**.

> **Decisão substantiva (21/jul/2026):** "Mosaico de Usos" recebe categoria
> própria em vez de ser somado à rotação. O MapBiomas usa essa classe quando
> **não consegue separar** lavoura de pasto — é incerteza de classificação, não
> um uso observado. Somá-la à rotação daria 51,2% → **62,8%**, praticamente o
> que as versões anteriores publicavam (48,7% → 64,8%), mas importaria a
> incerteza do classificador para dentro da conclusão. Quem preferir a leitura
> agregada tem os números aqui; o padrão do pipeline é mantê-las separadas.

### 5. Gradiente espacial (mesorregiões)

| Mesorregião | n eventos | % do total | % censura | Idade mediana (não-cens.) |
|---|---|---|---|---|
| **Sul Goiano** | 28.750.470 | 64,4% | 70,9% | **9 anos** |
| Leste Goiano | 4.864.734 | 10,9% | 36,8% | 10 anos |
| Centro Goiano | 4.946.759 | 11,1% | 70,9% | 9 anos |
| Noroeste Goiano | 3.933.298 | 8,8% | 52,0% | **16 anos** |
| Norte Goiano | 2.143.767 | 4,8% | 41,9% | **16 anos** |

A mediana é **só dos não-censurados**, como todo o resto do #28 e o JSON do site; a % de censura vai em coluna própria porque varia de 37% (Leste) a 71% (Sul/Centro) e é substantiva. Mediana calculada *com* censurados é limite inferior e distorce a leitura: Centro Goiano (71% de censura) aparece como 3ª mais velha (19a) com censurado dentro, mas é empatada em mais jovem (9a) sem — a diferença é censura, não idade de pasto.

O Sul Goiano concentra 64,4% dos eventos de conversão — 64,1% em área (diferença de só 0,27 pp: o Sul se espalha em latitude e o efeito cos(lat) quase se cancela) — com pastagens mais jovens (mediana 9a); Norte/Noroeste com mediana 16a indicam pastagens antigas convertidas tardiamente. **O gradiente Sul→Norte sobrevive ao censo** — era 7→14 na amostra (não-cens.) e é 9→16 no censo (não-cens.). A ordenação das pontas se mantém (Sul/Leste jovens, Norte/Noroeste velhos); o meio (Centro) é sensível à convenção de censura.

### 6. Coortes por origem anterior à pastagem

| Origem | n | % do total | Mediana | Leitura |
|---|---|---|---|---|
| `censurado_esquerda` | 28.634.498 | 64,1% | 17a (mínimo) | Pixels já-pastagem em 1985 |
| `vegetacao_natural` | 6.379.954 | **14,3%** | **13 anos** (cauda longa) | Coorte central da hipótese reserva |
| `mosaico` | 5.280.675 | **11,8%** | 12 anos | Origem mista — antes contada como censura |
| `agricultura` | 3.910.537 | 8,8% | 5 anos | **Rotação curta** — não é reserva |
| `outros` | 427.099 | 1,0% | 12 anos | — |
| `agua` | 5.487 | 0,012% | 5 anos | Raro; antes do pasto era água |
| `area_urbana` | 141 | 0,0003% | 3 anos | Raro; antes do pasto era área urbana |
| `sem_dado_anterior` | 637 | 0,001% | 4 anos | Classe 0 do MapBiomas; idade conhecida, origem não |

A coorte `agricultura → pastagem → agricultura` (rotação) é distinta da coorte de reserva — concentrada em 2–8 anos. A coorte `veg.nat → pastagem → agricultura` é onde os dois mecanismos operam: distribuição larga com pico jovem (premeditado) e cauda longa (oportunístico).

### 7. Sem correlação com socioeconômicos municipais

- Δ SICOR vs idade mediana municipal: r = +0,026 (n=1.751, n.s.)
- Δ VA agropecuária vs idade mediana municipal: r = −0,031 (n=3.001, n.s.)

Idade da pastagem na conversão **não é guiada por choques agregados municipais**. Sugere que os mecanismos atuam **abaixo da escala municipal** — provavelmente por propriedade individual e história fundiária, variáveis não capturadas pelos dados disponíveis.

> **Seguimento (Pipeline #40, 2026-06-07)**: a espacialização (AMC + município) e o cruzamento com **plantio direto** (estrutura, não fluxo) **confirmam** esta leitura. No recorte transversal, idade, no-till, VA agro e SICOR **co-variam apenas pelo gradiente Sul→Norte de aptidão** — controlando latitude, nenhum isola um mecanismo (no-till × idade cai de −0,37 para −0,22). A contribuição do #40 é a **geografia** das duas lógicas (Rotação jovem no Sul × Oportunístico antigo no Norte), não um preditor transversal. Ver `pipelines/40_duas_logicas_pastagem.md`.

## Censura à esquerda

Pixels já classificados como pastagem em 1985 não têm idade verdadeira conhecida (a série inicia em 1985). Esses pixels recebem `origem_anterior = censurado_esquerda` — **64,1% do censo**, decrescendo de 100% em 1986 para ~4% em 2024 — e são separados em todas as figuras. Análises sensíveis a idade absoluta restringem-se aos **16.004.530** eventos não-censurados.

> **Censura é decidida pelo índice, nunca por lookup.** Um pixel é censurado
> quando sua fase de pastagem alcança 1985, e ponto. Até 21/jul/2026 o código
> confundia isso com "classe não encontrada no `GRUPO_MAP`", inflando a censura
> em ~11 pontos. Classe 0 (nodata do MapBiomas) agora tem rótulo próprio,
> `sem_dado_anterior`: a idade é conhecida, só a origem é indeterminada.

## Hipóteses testáveis (descritivas) — resultado

| Hipótese | Status |
|---|---|
| Distribuição bimodal global | **Confirmada e robusta** — dois modos em todas as janelas, posições estáveis (μ₁≈4,4a, μ₂≈22,9a). Robustez vem da *estabilidade entre janelas*, não do ΔBIC |
| Idade mediana decrescente ao longo dos ATOs | **Refutada**: cresce I→II (4→14a); recua no III (8a) sem voltar ao nível do I |
| Idade menor no Sul de GO vs Norte/Nordeste | **Confirmada**: Sul 12a, Norte/Noroeste 21a |
| Coorte veg.nat→pastagem→agric com mediana <15a | **Confirmada** (mediana 13a, cauda longa) |
| Componente jovem torna-se dominante | **Não sustentada pelo censo**: $w_1$ sobe de 31,5% para 51,5% — alcança o antigo, não o supera. A amostra sugeria dominância (62,3%) |
| Correlação Δ SICOR vs idade mediana | **Sem correlação** — mecanismos operam abaixo da escala municipal |

## Decisão metodológica chave (D10)

**Não existe asset MapBiomas Pastagem separado** integrado ao pipeline. A idade é calculada localmente a partir das bandas `classification_YYYY`. No censo, o cubo de 40 bandas é exportado do GEE (`ee.batch.Export`, alinhado à grade nativa via `crsTransform` — nunca `scale=30`, que reamostraria e destruiria a contagem de anos consecutivos) e processado em janelas com rasterio. Isso evita o encadeamento de 35+ operações em `ee.Image` que estourava o limite do servidor.

**A lógica de idade do censo foi verificada por equivalência** contra a função original do amostrador: idade e classe-antes idênticas em 39/39 anos de conversão. Qualquer diferença nos resultados vem dos dados, não da reimplementação.

## Limitações

- **Identificação causal não é reivindicada** — análise é descritiva por idade. Discriminação dos mecanismos é interpretativa.
- **Sem dados de propriedade (CAR/SICAR)** — não é possível testar diretamente a hipótese sobre arrendamento.
- **Censura à esquerda 64,1%** — afeta intensamente os anos iniciais (1986–~2000); leitura interpretativa restringe-se aos 16.004.530 eventos não-censurados. O censo **não resolve** a censura: ela é limite da série MapBiomas, não do tamanho da amostra.
- **Eventos não são observações independentes** — um pixel pode converter mais de uma vez (pasto→lavoura→pasto→lavoura). São 1,064 eventos por pixel distinto (41.965.688 pixels converteram ao menos uma vez). Inofensivo para descrição; quem calcular erro-padrão precisa saber.
- **ΔBIC e p-valor perdem sentido com censo** — n é a população; qualquer desvio ínfimo infla a estatística. Ver ressalva no cabeçalho.
- **Área do pixel varia com a latitude** — em EPSG:4326 a área de solo é ∝ cos(lat), e Goiás cobre 7°: pixels do norte cobrem 3,5% mais chão. O parquet traz `n_pixels` **e** `area_ha`; as análises acima usam contagem (comparável com a amostra). Afirmações sobre *quanto* de Goiás fez algo devem usar `area_ha`.
- **Salto 2020→2022** — pode incluir reclassificação de classes de agricultura entre coleções MapBiomas. Vale investigação caso a leitura se torne central.
- **Erro de classificação do MapBiomas não é eliminado pelo censo** — o censo remove erro amostral, não erro de medida. Um pixel que oscila espúriamente entre pasto e não-pasto ainda gera idade curta artificial.

## Como rodar

### Censo (padrão)

```bash
# 1. Valida o caminho com 1 shard (~18 min de GEE)
python scripts/export_cubo_mapbiomas_go.py --teste

# 2. Export completo: 16 shards, ~1,5 GB no Drive (~17 min)
python scripts/export_cubo_mapbiomas_go.py
python scripts/export_cubo_mapbiomas_go.py --monitor

# 3. Baixa (usa o refresh token do GEE, que já tem escopo Drive)
python scripts/baixa_export_drive.py --prefixo cubo_go_mapbiomas101

# 4. Processa o censo (~3,5 min; ~500 MB de RAM, roda em laptop)
python scripts/processa_cubo_idade.py --shards data/raw/cubo_go

# 5. Análise (figuras + estatísticas + JSONs)
python scripts/analise_reserva_terra.py --fonte censo
```

### Amostra (legado — para comparação)

```bash
python scripts/coleta_idade_pastagem.py            # 1986-2024, 78k px, ~80 min
python scripts/analise_reserva_terra.py --fonte amostra
python scripts/compara_censo_amostra.py            # confronta as duas fontes
```

### Testes

```bash
# Contrato da estatística ponderada: com peso=1 tem que bater com numpy/sklearn
python scripts/estatistica_ponderada.py
```

## Comparação amostra × censo

| Métrica | Amostra (corrigida) | Censo | Sobrevive? |
|---|---|---|---|
| Eventos | 43.951 | **44.639.028** | — |
| Municípios com evento | 234 | **244** de 246 | — |
| Municípios com <20 px não-cens. | 104 (44%) | **0** | — |
| Censura | 63,7% | 64,1% | ✅ |
| Mediana global (não-cens.) | 8a | 10a | ~ |
| Ato I / II / III (mediana) | 4 / 12 / 6 | 4 / 14 / **8** | ~ |
| μ₁ (Ato III) | 4,6a | 4,4a | ✅ |
| μ₂ (Ato III) | 22,7a | 22,9a | ✅ |
| **w₁ (Ato III)** | 62,3% | **51,5%** | ❌ |
| Gradiente Sul→Norte | 7→14a | 9→16a | ✅ (ordenação idêntica) |
| Rotação (2020-24) | 54,7% | **43,0%** | ❌ |

A verificação **ano a ano** mostra que a amostragem dentro de cada ano era sadia (diferença de mediana: média −0,09a, máx |2|a). O que falha são os **agregados**, por erro de composição entre anos. Ver `scripts/compara_censo_amostra.py`.

## Sub-pipeline C — Aba na visualização web ✅

Implementado em `Visualizacao/index.html` (§6), com `assets/js/pastagem-reserva.js`:
coroplético d3 das 166 AMCs, histograma por Ato com toggle, e cards de coortes.
Consome `idade_pastagem_municipal.json`, `idade_pastagem_histograma.json`,
`idade_pastagem_gmm.json` e `idade_pastagem_amc.geojson` — todos regerados a
partir do censo em 21/jul/2026.

Ganho concreto do censo aqui: a mediana municipal deixou de ser ruído. Na
amostra, 44% dos municípios tinham menos de 20 pixels não-censurados (mediana
de 26 px por município); no censo são **0%**, com mediana de 22.250 px. O mapa
municipal passou a ser interpretável célula a célula.
