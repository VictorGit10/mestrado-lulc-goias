# Pipeline #28 — Leitura crítica e próximos passos

Documento complementar a [28_idade_pastagem.md](28_idade_pastagem.md). Explica o método de forma didática, aponta fragilidades, e propõe o que falta para responder plenamente à pergunta de pesquisa.

---

## 1. O que foi feito, passo a passo

### Etapa 1 — Coleta no Google Earth Engine

Para cada ano `t` entre 1986 e 2024 (39 anos):

**a) Identificação da máscara de conversão**

- Acesso o raster MapBiomas Coleção 10.1 (já usado no projeto).
- Olho a banda `classification_{t-1}` e marco com 1 os pixels que eram pastagem (classe ID 15).
- Olho a banda `classification_{t}` e marco com 1 os pixels que viraram agricultura (IDs 9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62 — soja, milho, algodão, etc.).
- A **máscara final** é a interseção: pixels que eram pasto E viraram agricultura naquele ano. Isso é o universo de pixels "convertidos no ano t".

**b) Amostragem**

- Em vez de baixar TODOS os pixels da máscara (poderiam ser milhões), peço ao GEE para amostrar 2.000 pixels aleatórios DENTRO da máscara, com seed fixa.
- Cada pixel amostrado vem com: as coordenadas (lat/lon) E todos os valores da classificação MapBiomas em todos os anos anteriores (40 bandas: `classification_1985`, ..., `classification_{t-1}`).

**c) Cálculo local em Python**

- Para cada pixel amostrado, percorro sua história ano a ano (de 1985 até `t-1`):
  - Conto quantos anos consecutivos imediatamente antes de `t` ele foi pastagem (= **idade**).
  - Identifico que classe ele era no ano imediatamente anterior ao início da fase pastagem (= **origem anterior**).
- Localizo o município de cada pixel via overlay com o shapefile do IBGE.

**Resultado final**: 78.000 linhas (2.000 pixels × 39 anos), cada uma com `ano_conversao`, `idade_pastagem_anos`, `classe_antes_id`, `origem_anterior`, `cd_mun`, `mesorregiao`, `lon`, `lat`.

### Etapa 2 — Análise descritiva

Histogramas agregando esses 78k pixels por ATO político, por mesorregião e por origem anterior. Medianas, percentis (P10, P90), e scatter com Δ SICOR/Δ VA agro municipais.

---

## 2. O que é "N" e o que é "censurado"

**N** = número de pixels amostrados em cada grupo. Por exemplo, `n=16.000 mediana=4a` no ATO I significa: dos 78.000 pixels totais, 16.000 sofreram conversão entre 1985 e 1993 (8 anos × 2.000/ano), e desses, a mediana de idade era 4 anos.

**Censurado à esquerda** é um termo de análise de sobrevivência que significa que **a observação começa antes do início da série de dados**. Em concreto:

- Se um pixel já era pastagem em **1985** (primeiro ano da série MapBiomas), eu **não sei** quantos anos ele já era pasto. Pode ter virado pasto em 1984, 1970, 1955... não tenho como saber.
- Se esse pixel virou agricultura em 1986, eu só sei dizer "tinha pelo menos 1 ano de pasto". Pode ter tido 50 anos. A idade verdadeira está escondida.
- Esses pixels recebem `origem_anterior = censurado_esquerda` e `idade_pastagem_anos` representa a idade **mínima possível**, não a real.

A censura é massiva: 66% dos 78k pixels são censurados, e quase todos eles estão nos anos iniciais (em 1986, 100% são censurados; em 2024, só 12%). Por isso o resumo executivo só olha os 26.427 **não-censurados**.

---

## 3. Avaliação honesta: a análise NÃO respondeu plenamente à pergunta

**A pergunta era**: "A idade da pastagem traz pistas para entender se a conversão é premeditada ou oportunística?"

**O que foi feito**:

- ✅ Calcular a idade da pastagem em cada conversão (dado bruto)
- ✅ Descrever como essa idade varia por época, região e origem anterior
- ⚠️ **NÃO** classificar cada pixel como "provavelmente premeditado" ou "provavelmente oportunístico"
- ⚠️ **NÃO** quantificar a fração de cada mecanismo por município/mesorregião/ATO
- ⚠️ **NÃO** testar formalmente a bimodalidade observada no histograma do período 2018-24

A interpretação dos dois mecanismos ficou no nível "olhe o histograma e tire suas conclusões". É um primeiro passo, mas falta o passo de virar isso em variável quantificável.

---

## 4. Análises que faltaram (e fazem sentido fazer)

### A) Classificação de cada pixel por mecanismo

Estabelecer regras de decisão:

| Idade | Origem anterior | Classificação |
|---|---|---|
| ≤ 8 anos | veg.natural | **Premeditado curto** (caminho deliberado rápido) |
| ≤ 8 anos | agricultura | **Rotação** (não é reserva de terra) |
| ≥ 20 anos | veg.natural | **Oportunístico clássico** (pasto histórico ativado) |
| Intermediário | — | **Ambíguo / transição** |

Depois agregar essas frações por município e ano. Aí sim teríamos variáveis quantificáveis para correlacionar com SICOR, preço da soja, Trase, expansão de armazéns.

### B) Modelo de mistura formal para testar bimodalidade

Ajustar uma mistura de 2 gaussianas no período 2018-24 e fazer teste de razão de verossimilhança vs 1 gaussiana. Se duas gaussianas vencem, dá rigor estatístico ao que o histograma sugere visualmente. Os pesos da mistura quantificam a fração de cada mecanismo.

### C) Sobrevivência (Kaplan-Meier) — análise mais natural para esses dados

A pergunta "quanto tempo uma pastagem dura antes de virar agricultura?" é literalmente uma análise de sobrevivência. Vantagens:

- Trata a censura formalmente (Kaplan-Meier sabe lidar com observações censuradas).
- Permite comparar coortes (Sul vs Norte, Ato II vs III) via teste log-rank.
- Produz curvas interpretáveis: "metade das pastagens de 2010 já viraram agricultura até 2020".

### D) Coortes longitudinais ao invés de snapshot anual

Em vez de "todos os pixels convertidos em ano X", olhar "todos os pixels que viraram pasto em ano Y, e ver quando viraram agricultura". Isso é mais coerente com a hipótese — a coorte que entrou em pasto em 1995 tem trajetória diferente da que entrou em 2010.

### E) Decompor o salto 2020→2022

A queda de mediana 31a → 7a precisa investigação:

- É reclassificação MapBiomas (novas classes de agricultura entrando)?
- É concentração espacial (algum município novo entrou pesado)?
- É efeito da última versão da coleção 10.1?
- Comparar com dados de soja Trase / SICOR para ver se faz sentido temporalmente.

---

## 5. Amostra vs dados completos

**Sim, o resultado pode ser diferente** com dados completos. Mas a diferença será principalmente de **precisão**, não de direção.

- 78k pixels equivalem a ~7.000 hectares amostrados de talvez ~2 milhões de hectares totais convertidos no período. É 0,35% da área.
- As **medianas e formas das distribuições** são estatisticamente bem estimadas com 2.000 pixels/ano (intervalos de confiança apertados).
- O que muda com dados completos:
  - **Precisão municipal**: alguns munis pequenos têm só 5-10 pixels amostrados, então a mediana municipal é ruidosa. Com tudo, ficaria precisa.
  - **Cauda da distribuição**: eventos raros (pastagens muito antigas em regiões secundárias) ficam subamostrados.
  - **Mapas**: para mapear cada pixel, precisa de tudo (não dá pra mapear amostra estratificada — é descontínua espacialmente).

**Quanto custaria em dados?** Se baixássemos todos os ~2M ha de pixels P→A com 40 bandas cada, seria ~5 GB. Inviável local, mas o GEE pode exportar isso para Cloud Storage / Drive sem trafegar pela máquina.

**Recomendação**: manter a amostra para análises agregadas, mas **gerar um raster de idade-na-conversão** para mapas (próximo item).

---

## 6. Visualização espacial — possível e útil

Três tipos de mapa fazem sentido:

### Mapa 1 — Idade mediana na conversão por município (coroplético)

- **O que mostra**: cada município pintado pela mediana da idade-na-conversão dos pixels convertidos nele.
- **Como produzir**: já temos os dados (`pastagem_idade_conversao.csv`), basta agregar e plotar.
- **Leitura esperada**: Sul Goiano azul (jovem); Norte/Noroeste vermelho (antigo); gradiente fronteira → consolidado.
- **Tempo**: 30 min de script Python.

### Mapa 2 — Raster de idade-na-conversão (todos os pixels)

- **O que mostra**: cada pixel de 30m colorido pela idade que tinha no momento em que virou agricultura (e cinza para pixels que nunca foram convertidos).
- **Como produzir**: exportar do GEE para um único TIFF cobrindo Goiás. O cálculo é exatamente o mesmo, mas sem amostragem.
- **Leitura esperada**: clusters claros vs escuros revelam padrão espacial fino que o município médio esconde.
- **Tempo**: ~30 min de tempo GEE + script de export.

### Mapa 3 — Frações de mecanismo por município

- **O que mostra**: dois mapas lado a lado — % premeditado vs % oportunístico no município.
- **Como produzir**: depende da Análise A acima (classificar pixels por regra).
- **Leitura esperada**: testar se Sul é dominantemente premeditado e Norte oportunístico.

---

## 7. Fragilidades honestas da análise atual

1. **Não há identificação causal** — só descrição. Não dá pra dizer "X causa Y", só "X e Y andam juntos".
2. **Censura subutilizada** — 66% dos pixels foram excluídos das análises principais. Kaplan-Meier reaproveitaria essa informação.
3. **Amostragem estratificada por idade** distorce contagens — não dá pra ler proporção direta do histograma. Cada "pico" do histograma é proporcional ao número amostrado naquele bin, não à prevalência real.

   > Nota técnica: na implementação atual, `stratifiedSample` é chamado com classe única (a máscara P→A é 1 onde houve conversão e mascarada onde não), então **não há estratificação efetiva por bin de idade** — todos os pixels têm a mesma probabilidade de seleção. Mas a documentação anterior sugeria estratificação por idade. **Esta é uma inconsistência que deve ser corrigida**.

4. **MapBiomas tem incerteza de classificação** — pixels podem oscilar entre pastagem/outros por ruído, criando "idades curtas" artificiais. Os 7a de 2022 podem ser parcialmente isso.
5. **Conceito de "premeditado vs oportunístico" não é diretamente observável** — só inferimos. Sem dado de propriedade (CAR) e intenção do produtor, é leitura interpretativa.
6. **Sul Goiano domina a amostra** (37%) — risco de extrapolar achados regionais como se fossem estaduais.
7. **Cruzamento com SICOR/VA agro foi limitado** — só Δ contemporâneo, sem lags. Lags 1-3 anos seriam mais sensatos (decisão de converter leva tempo).

---

## 8. Decisões metodológicas — explicação detalhada

### D10 — Idade calculada localmente, não via asset GEE separado

Existe o asset `mapbiomas_brazil_collection10_pasture_age_v2` (Coleção 10 base), mas:

- O projeto usa Coleção 10.1 (versão mais recente), e o asset de pasture_age v2 é da Coleção 10 (versão anterior).
- Calcular localmente a partir das bandas `classification_YYYY` da 10.1 é mais coerente com o resto do pipeline e mais flexível (permite mudar o critério de "classe alvo" facilmente).
- A lógica é exatamente a mesma que o MapBiomas usa internamente (`codes/analysis_1_age.js` do platform-analysis): contador que incrementa quando pixel é classe 15 e reseta quando não é.

### Amostragem estratificada vs uniforme

Primeira tentativa usou `sample(numPixels=200)`, mas o GEE distribui esses 200 pixels uniformemente em toda Goiás, e a maioria cai FORA da máscara (pixels que não sofreram conversão). Resultado: 3 pixels úteis de 200 tentados.

Solução: `stratifiedSample(classBand='classe_mask', numPoints=2000)` — força o GEE a amostrar apenas DENTRO da máscara. Isso resolveu o problema de raridade.

### Cálculo em Python, não em GEE

Primeira versão calculava idade em GEE encadeando 35+ operações `image.add(1).multiply(is_past)`. Resultado: GEE travava ou retornava timeout no ano 2000 (esperou 20+ minutos sem resposta).

Solução: GEE faz apenas máscara + sample com 40 bandas; cálculo de idade é vetorial em NumPy em ~0,1s/ano. Reduz cálculo no servidor e custo de transferência.

### Timeouts e tileScale crescente

Mesmo com a estratégia simplificada, o ano 2000 travou na primeira tentativa por motivo transitório (rede/throttling do GEE). Implementei retry com `tileScale` escalando 8→16→32 e timeouts de 240s/480s/720s via `concurrent.futures`. Na retomada, 2000 respondeu em 1 segundo — o problema era pontual.

---

## 9. Recomendação de caminho

Se concorda que a análise está parada na "fase descritiva", o caminho mais produtivo agora seria, em ordem:

1. **Classificação de pixels por regra simples** (premeditado / oportunístico / rotação / ambíguo) — converte os dados em variáveis quantificáveis. ~1h de código.
2. **Mapa coroplético municipal da idade mediana** — dá visualização espacial imediata. ~30 min.
3. **Kaplan-Meier por coorte** (Sul vs Norte, Ato II vs III) — análise estatisticamente mais correta para a pergunta. ~2h.
4. **Investigar o salto 2020→2022** — diagnóstico para ver se é real ou artefato. ~1h.

Depois disso, com variáveis quantificáveis em mãos:

5. **Painel municipal** % premeditado × Δ SICOR / Δ Trase / Δ VA agro com lags. Aqui sim seria possível dizer "crédito acelera o caminho premeditado" ou similar.
6. **Sub-pipeline #28-C** (aba na visualização web). Os JSONs já estão prontos, mas ganham muito com os mapas e a classificação por mecanismo.
