# Pipeline #28D — A deriva do destino da conversão no fim da série

**Data:** 2026-07-21 · **Script:** [`scripts/deriva_mosaico_fim_serie.py`](../../scripts/deriva_mosaico_fim_serie.py)
· **Origem:** fecha o §4-E (e, por consequência, o §4-C) de
[28_idade_pastagem_critica.md](28_idade_pastagem_critica.md)

> **Uma frase:** o que o #28 chama de "pastagem que virou agricultura" deixa de
> existir ao longo da série — não porque a conversão parou, mas porque o
> MapBiomas passa a classificar o destino como **Mosaico de Usos**; em 2024 o
> objeto do #28 captura 7,5% do que capturava em 2015, e o que sobra é
> subpopulação selecionada.

---

## 1. De onde veio a pergunta

A leitura crítica do #28 deixou em aberto o §4-E: a mediana da idade da pastagem
na conversão despenca no fim da série e ninguém tinha decomposto o porquê. Com o
censo, os números são:

| ano | eventos P→A | censura | mediana (não-cens.) | horizonte |
|---|---|---|---|---|
| 2019 | 1.117.213 | 54,9% | 22 a | 34 |
| 2020 | 606.821 | 47,1% | 20 a | 35 |
| 2021 | 224.282 | 28,6% | 11 a | 36 |
| 2022 | 285.236 | 18,2% | **4 a** | 37 |
| 2023 | 131.265 | 33,6% | 10 a | 38 |
| 2024 | 157.245 | **4,0%** | 5 a | 39 |

Três coisas caem juntas: o número de eventos, a taxa de censura e a mediana. O
§4-E listava quatro suspeitos — reclassificação do MapBiomas, concentração
espacial, efeito da Coleção 10.1, ou mudança real de comportamento. **Nenhum
deles, na forma como foram formulados.**

---

## 2. O achado — a deriva do destino

O #28 restringe a análise a `pastagem → agricultura`. O Bloco A remove essa
restrição e conta, no censo de pixels (16 shards, todo o cubo), para onde a
pastagem vai a cada ano:

| ano | P→agricultura | P→Mosaico de Usos | razão M/A |
|---|---|---|---|
| 2000 | 1.612.565 | 3.111.159 | 1,9 |
| 2010 | 2.601.149 | 2.661.703 | 1,0 |
| 2015 | 4.040.382 | 2.442.452 | **0,6** |
| 2019 | 2.072.349 | 3.346.353 | 1,6 |
| 2020 | 1.287.587 | 4.635.043 | 3,6 |
| 2022 | 648.197 | 6.774.799 | 10,5 |
| 2024 | 303.432 | 9.875.689 | **32,5** |

`P→agricultura` cai **92%** de 2015 a 2024. No mesmo intervalo `P→Mosaico`
quadruplica. A razão entre os dois destinos vira de 0,6 para 32,5 — em 2024, para
cada pixel de pastagem que o MapBiomas registra virando lavoura, **32 viram
"não consegui distinguir"**.

O #28 estava medindo uma fatia cada vez menor, e cada vez mais atípica, do
fenômeno que pretende descrever.

---

## 3. Por que isto não é "a conversão acabou"

Quatro âncoras, três delas independentes do #28:

**(a) A lavoura cresceu — muito — na janela exata.** Área plantada de soja em
Goiás (SIDRA, dado de campo, externo ao sensoriamento remoto): 3,578 Mha (2020)
→ **4,942 Mha (2024)**, +1,364 Mha, **+38%**.

**(b) A "agricultura" do MapBiomas não se mexeu.** 5,668 → 5,732 Mha no mesmo
período (+0,064 Mha em quatro anos, contra +0,15 a +0,18 Mha/ano em 2015-2017).

**(c) O Mosaico de Usos cresceu quase exatamente o tamanho da expansão de soja.**
2,235 → 3,586 Mha (**+1,351 Mha**) — compare com os +1,364 Mha do SIDRA. A
correspondência é próxima demais para ser coincidência.

**(d) A pastagem continua saindo.** 13,146 → 11,989 Mha (−1,157 Mha). O pasto
está desaparecendo; só não está sendo contabilizado como *chegando* à
agricultura.

Em resumo: há expansão agrícola real e acelerada em Goiás no Ato III, ela aparece
no dado de campo, e o MapBiomas a registra — mas sob o rótulo "Mosaico de Usos",
não "agricultura".

---

## 4. Artefato do classificador ou mudança real da paisagem?

**O dado não separa as duas, e é desonesto fingir que separa.**

"Mosaico de Usos" (classe 21) é a classe que o MapBiomas usa quando **não
consegue distinguir** lavoura de pastagem no pixel de 30 m — caracterização agora
verificada contra a fonte (ver [censo_vs_amostra.md](../metodologia/censo_vs_amostra.md) §3).
Ela crescer admite duas leituras:

**(a) Deriva do classificador.** Os filtros pós-classificação da Coleção 10 usam
janelas móveis retroativas de 3 e 4 anos, e o ATBD declara explicitamente regras
adicionais "for the last years of the series (2017–2023), when the analysis
window is limited" (ATBD Coleção 10, §3.4.1 e §3.4.3.1). Uma transição no fim da
série não tem anos posteriores que a confirmem, e o comportamento dos filtros ali
é, por construção, diferente.

**(b) Mudança real da paisagem.** Integração lavoura-pecuária (ILP) de fato torna
a paisagem menos separável, e é um fenômeno que Goiás tem — o próprio #40
identifica "Giro de lavoura/ILP" como a tipologia dominante em 45 dos 88
municípios então analisados. Uma paisagem genuinamente mais misturada
*deve* produzir mais mosaico.

A âncora (a) do §3 favorece a deriva como componente dominante — a soja cresceu
38% e a agricultura do MapBiomas ficou parada, o que nenhuma mudança real de
manejo explica sozinha. Mas (b) não é zero, e separar as duas exigiria uma fonte
independente de resolução maior (a coleção de 10 m do MapBiomas, baseada em
Sentinel-2, cobre 2017–2024 e seria o teste natural — **não rodada**).

**Para o #28 a distinção não muda a consequência:** em qualquer dos dois mundos,
a população "conversão pasto→lavoura" medida em 2024 não é comparável à de 2015.

---

## 5. O que isto atinge — e quanto

### 5.1 A manchete do peso (w₁) não sobrevive como tendência

O #28 publica, para o Ato III, `w₁ = 51,5%` e a leitura "o componente jovem
*alcança* o antigo". O Bloco E refaz o GMM ponderado em janelas deslizantes de
5 anos:

| janela | n | μ₁ | **w₁** | μ₂ | w₂ | |
|---|---|---|---|---|---|---|
| 2014-2018 | 3.991.482 | 3,92 | **20,8%** | 20,88 | 79,2% | |
| 2015-2019 | 3.499.917 | 4,03 | **22,3%** | 21,75 | 77,7% | |
| 2016-2020 | 2.824.030 | 4,26 | **25,1%** | 22,71 | 74,9% | |
| 2017-2021 | 2.362.015 | 4,55 | **27,6%** | 23,10 | 72,4% | ←deriva |
| 2018-2022 | 1.850.177 | 4,27 | **31,2%** | 23,32 | 68,8% | ←deriva |
| 2019-2023 | 1.305.208 | 4,20 | **34,5%** | 23,35 | 65,5% | ←deriva |
| 2020-2024 | 952.698 | 4,39 | **51,5%** | 22,95 | 48,5% | ←deriva |

`w₁` **sobe monotonicamente com a exposição da janela à deriva**, de 20,8% (base
pré-deriva) a 51,5% (janela inteiramente dentro dela). Ano a ano o padrão é ainda
mais direto: 2020 dá w₁ = 34,8%; **2024, o ano mais derivado (razão M/A = 32,5),
dá w₁ = 93,4%** — quase só componente jovem, que é exatamente o que se espera se
o que sobrevive ao rótulo "agricultura" for a rotação de ciclo curto.

> ⚠️ *Nota de leitura:* as janelas de 2010-2014 a 2013-2017 caem em **outra
> solução do GMM** (μ₁ ≈ 8–10 a, que não é um modo jovem) e por isso ficam fora
> da comparação — comparar w₁ entre decomposições qualitativamente distintas
> seria comparar coisas diferentes.

**Veredito:** a afirmação "o componente jovem ganha peso ao longo do tempo" —
que sobreviveu à migração censo×amostra — **não sobrevive a este teste**. Ela
acompanha a deriva. O que resta defensável é o achado de forma, não o de
tendência.

### 5.2 O que SOBREVIVE

Os **modos** são estáveis em toda a tabela: μ₁ ≈ 4–5 a e μ₂ ≈ 21–23 a em todas as
janelas comparáveis, dentro e fora da deriva. **A bimodalidade — o achado central
do #28 — não depende da janela contaminada** (confirmado sob a união em 23/jul:
5/5 mesorregiões e 10/10 células região×ato seguem bimodais; ver #28C).

> ⚠️ **Correção (23/jul/2026):** eu afirmava aqui que "o gradiente Sul→Norte do #28C
> sobrevive por ser transversal (compara regiões dentro do mesmo período)". A
> re-checagem sob a união (`bimodalidade_regional_uniao.py`) mostrou que **isso está
> errado para o gradiente de IDADE**: o "transversal, logo imune" não vale, porque a
> seleção agricultura×Mosaico atua *dentro* de um período. Sob `pasto→(agric∪mosaico)`
> a amplitude Sul→Norte da idade mediana cai de **7a para 2a** — é o mesmo artefato do
> #40. O que é transversal e sobrevive é a **bimodalidade/coexistência**, não o
> gradiente latitudinal de idade.

### 5.3 A mediana pré-2020 já era horizonte, não idade

Um subproduto do Bloco C, e vale registrar porque é independente da deriva: de
1995 a 2019, a mediana da idade não-censurada é **~55% do horizonte
(desvio-padrão 7 pp)** — ou seja, ela acompanha `ano − 1985` quase linearmente.
Isso confirma, em série anual e para o estado inteiro, o que o §7.3 do
`censo_vs_amostra.md` estabeleceu por mesorregião: **a censura mede horizonte, e
enquanto ela morde, a mediana mede horizonte também.** Somando as duas coisas:
antes de 2020 a mediana é horizonte; de 2020 em diante é resíduo selecionado.
Não há janela em que ela seja, sozinha, "a idade do pasto convertido".

### 5.4 Alcance fora do #28

A deriva é uma propriedade do **dado**, não do #28. Qualquer pipeline que leia
transições `pastagem → agricultura` do MapBiomas na janela recente está exposto:
**#12/#19** (matrizes de transição), **#33** (transições regionais), **#39**
(fluxo/hazard), **#47** (custo de carbono, na medida em que usa perda por
formação no Ato III). **Não auditados aqui** — ver §8.

Um segundo canal de exposição, distinto das transições, é o **estoque**: o
**centro de massa** (#32/#44) pondera pelo estoque de agricultura
(`lulc_agricultura_ha`), que subconta a expansão recente exatamente onde a soja
migra para o Mosaico. Auditado em `centro_massa_deriva_check.py`: a agricultura
visível *congela* 2019→2024 (+0,5 km) enquanto **duas fontes independentes** — o
crescimento do Mosaico misturado à agricultura, e a soja SIDRA (imune ao
classificador) — mostram a agricultura andando **+10,0 km ao norte** na mesma
janela (triangulação exata). O viés é real e tem o sentido temido (agricultura
medida enviesada ao **sul**), mas é pequeno diante do sinal de 40 anos e a
manchete Sul→Norte se sustenta porque sua perna que sobe (rebanho/SIDRA) é imune.
Detalhe no cabeçalho do script e em `centro_massa_deriva_resumo.csv`.

---

## 6. O que isto fecha

### §4-E — decompor o salto 2020→2022 ✅ FECHADO

Resposta: nenhuma das quatro hipóteses. Não é reclassificação por *novas classes
de agricultura* entrando (a agricultura total fica parada), não é concentração
espacial (a queda é estadual e monotônica), não é mudança de comportamento do
produtor (o SIDRA mostra a lavoura acelerando), e não é "efeito da 10.1" no
sentido de um bug pontual de versão. É **deriva do destino da conversão**, com
mecanismo declarado no ATBD e assinatura mensurável.

### §4-C — Kaplan-Meier ✅ FECHADO (como "não é o estimador", com alternativa)

O §4-C propunha tratar a censura formalmente via análise de sobrevivência. Ele
se encerra por **duas razões independentes**, e nenhuma delas é falta de tempo:

1. **Censura informativa** (já estabelecido no §7.3 do `censo_vs_amostra.md`): a
   validade do KM exige censura independente da duração. Aqui a censura **é** o
   horizonte, e o horizonte correlaciona com a idade por construção — regiões
   diferentes converteram em épocas diferentes. Onde o KM mais "corrigiria" é
   onde ele é menos confiável.
2. **O evento de falha não é constante no tempo** (novo, deste pipeline).
   Sobrevivência exige um evento de falha bem definido e estável ao longo do
   acompanhamento. Aqui "falhar" = "virar agricultura", e esse rótulo migra para
   "mosaico" ao longo da série. Um KM ingênuo leria a deriva como **queda de
   hazard** — concluiria que a pastagem "passou a durar mais" justamente quando
   a lavoura crescia 38%. É a armadilha do #42 (D16) em outra roupa: um método
   correto aplicado a uma série cuja definição se move fabrica um resultado
   forte e errado.

**O desenho de coorte (§4-D) não resgata**, porque herda o mesmo problema nos
anos de acompanhamento recentes — e, além disso, o conjunto de risco não é
construível a partir do parquet do #28, que é tabela de *eventos* e não painel de
pixels (pixels que viraram pasto e nunca converteram não estão lá; exigiria
reprocessar o cubo).

**A alternativa construtiva** (não implementada, registrada como caminho): usar
como evento de falha a **saída da pastagem para uso agropecuário — agricultura
∪ mosaico**. A deriva é uma reetiquetagem *dentro* dessa união, então a união é
robusta a ela. Medido:

| ano | (agric+mosaico) / saídas totais | só agricultura / saídas |
|---|---|---|
| 2000 | 74,7% | 25,5% |
| 2015 | 83,4% | **52,0%** |
| 2020 | 77,5% | 16,8% |
| 2024 | 88,6% | **2,6%** |

A união fica em 75–89% em toda a série; a definição atual desaba de 52% para
2,6%. **Custo da troca:** a união responde uma pergunta mais grossa — "a fase de
pastagem terminou?" em vez de "a pastagem virou lavoura?" —, e mistura conversão
produtiva com perda de legibilidade do classificador. É um estimador mais
robusto de uma quantidade menos interessante. A escolha é substantiva, não
técnica, e fica para o autor.

---

## 7. Como reproduzir

```bash
python scripts/deriva_mosaico_fim_serie.py                      # censo completo (~9 min)
python scripts/deriva_mosaico_fim_serie.py --reusar-transicoes  # pula o cubo, refaz o resto
python scripts/deriva_mosaico_fim_serie.py --rapido             # 6 shards, só p/ iterar
```

Saídas em `data/processed/`: `deriva_mosaico_transicoes.csv`,
`deriva_mosaico_areas.csv`, `deriva_mosaico_efeito_28.csv`,
`deriva_mosaico_sidra.csv`, `deriva_mosaico_sensibilidade_gmm.csv`.
Figura em `outputs/deriva_mosaico/deriva_mosaico.png`.

---

## 8. Limitações e o que ficou de fora

- **Artefato × realidade não foi separado** (§4). O teste natural — comparar com
  a coleção de 10 m (Sentinel-2, 2017–2024) — não foi rodado. Um segundo teste,
  que separa *instabilidade terminal do classificador* de *fenômeno de campo real*
  sem depender do MapBiomas confirmar nada, está desenhado em **§9** (Coleção 9).
- **O alcance fora do #28 não foi auditado** (§5.4). Sabe-se que #12/#19/#33/#39/#47
  leem as mesmas transições; não se mediu quanto cada um se move. É a próxima
  tarefa óbvia, e é maior que este pipeline.
- **A contagem do Bloco A é sobre o bbox do cubo**, não recortada a Goiás (o
  recorte municipal vive no `processa_cubo_idade.py`). Isso é adequado para
  *razões* e *tendências*, que é o uso aqui, mas os níveis absolutos incluem
  faixas de MT/MS/MG/BA/TO. As séries de área (§3) e o efeito no #28 (§5) **são**
  recortados a Goiás.
- ~~**Não se testou se a deriva é espacialmente uniforme.**~~ **Testado** (nível
  AMC, `centro_massa_deriva_check.py`): **não é uniforme** — o centroide do
  *crescimento* do Mosaico 2019→2024 está **+46,5 km ao norte** do centroide da
  agricultura visível, ou seja, a massa nova aterrissa na fronteira. Isso confirma
  a preocupação: a deriva tem assinatura espacial (norte). ~~O gradiente do #28C
  segue protegido por ser transversal~~ — **corrigido (23/jul)**: o gradiente
  latitudinal de *idade* do #28C **não** está protegido (a re-checagem sob a união o
  mostrou artefato, §5.2); leituras regionais do Ato III que dependam do nível de
  agricultura ou do gradiente de idade estão expostas.
- ~~**A correspondência mosaico ≈ expansão de soja (§3c) é agregada.**~~
  **Verificado** ao nível AMC (`centro_massa_deriva_check.py`): o crescimento do
  Mosaico e o da soja SIDRA por AMC (2019→2024) têm **Pearson r = +0,84** e
  magnitudes quase idênticas (Δmosaico 1,525 Mha ≈ Δsoja 1,539 Mha) — o mosaico
  novo *está onde* a soja nova está.
- ~~**Falta a versão pixel a pixel do rastreio `pasto→21`.**~~ **FEITO** (23/jul/2026,
  `processa_cubo_idade_destinos.py`): o cubo foi reprocessado capturando os DOIS destinos
  (`pasto→agricultura` e `pasto→Mosaico`) com **idade do pasto** e localização. A razão
  `pasto→Mosaico / pasto→agricultura`, agora ao nível do pixel e recortada a GO, **explode
  na cauda**: 0,66 (2015) → 1,93 (2019) → 4,89 (2020) → **37,7 (2024)**, enquanto
  `pasto→agric` colapsa (2,1M → 0,16M px) e `pasto→Mosaico` cresce (1,4M → 5,9M). São os
  **mesmos pixels de pastagem que terminaram** — só mudou o rótulo do destino. Isto
  estabelece a **co-localização** temporal e espacial (o que o balanço agregado só
  insinuava), mas **não** separa artefato × ILP real — isso continua exigindo a comparação
  entre coleções (§9). Saída: `pastagem_conversao_destinos.parquet`.

---

## 9. Teste proposto para separar artefato × realidade (Coleção 9)

O §4 mostra que a assinatura da deriva é *consistente* com um artefato de fim de
série (filtros temporais com janela truncada nas bordas — ATBD Coleção 10,
§3.4.1 e §3.4.3.1), mas o dado da própria Coleção 10.1 **não separa** "o
classificador rerroteou soja recém-convertida para o Mosaico" de "expansão real
de sistemas integrados (ILP), que é legitimamente Mosaico". As duas hipóteses
produzem a mesma série dentro de uma coleção só. Esta seção documenta o teste que
as separa. **Não foi executado** — exige baixar e reprocessar outra coleção — mas
é barato, usa dado público, e é o único caminho que *prova* a natureza do sinal.

### 9.1 A hipótese, tornada falseável

A classe 21 ("Mosaico de Usos") é a classe da **ambiguidade** agricultura/pasto;
por isso tanto o artefato quanto o ILP real aumentam `pasto→21`. O que os separa
é **onde no tempo** o colapso de `pasto→agricultura` mora:

- **Fenômeno real** (soja/ILP explodindo de fato) está ancorado no **calendário**.
  Aparece nos mesmos anos-calendário (2023–24) em *qualquer* coleção.
- **Artefato terminal** está ancorado na **borda de cada coleção**. Cada coleção
  aplica a regra de janela truncada aos seus próprios últimos anos. Logo o colapso
  deve **acompanhar a borda**: se a Coleção 9 termina ~1 ano antes da 10.1, o
  colapso nela deve sentar ~1 ano antes.

As duas hipóteses fazem predições **opostas** sobre um mesmo teste: o colapso é
fixo no calendário (real) ou móvel com a borda (artefato)?

### 9.2 Por que *não* comparar níveis entre coleções

A tentação é comparar "quanto Mosaico há em 2021–22 na 9 vs na 10.1" e ver se
encolhe. **Não vale**: o MapBiomas lança coleção nova todo ano com melhorias
(treino, algoritmo, legenda), então a 9 é um produto **pior em tudo**, e um
encolhimento de nível confunde "ganhou anos futuros" (o que se quer medir) com
"o algoritmo ficou melhor" (confound). Um controle de ano-interior estável (ex.:
2010, terminal em nenhuma das duas) tira o *offset médio* de qualidade, mas não
salva se a degradação da 9 for ela própria concentrada nos anos recentes.

A saída é **não usar a 9 como linha de base de qualidade**, e sim como uma coleção
cuja **borda terminal cai em outro ano-calendário**. Aí a qualidade geral da 9
passa a ser irrelevante: o teste pergunta *onde dentro de cada coleção* o colapso
senta, não *quanto* Mosaico cada uma tem.

### 9.3 O desenho robusto (borda móvel, pixel-a-pixel)

Para os pixels de Goiás:

1. **Localizar a borda de cada coleção.** Confirmar o último ano de cada uma
   (a 10.1 vai a 2024; a 9 termina antes — verificar 2022 ou 2023).
2. **Rastrear o mesmo pixel entre coleções.** Tomar anos que são *terminais* na 9
   e *interiores* na 10.1. Comparar a classe de cada pixel: os que saem de
   `Mosaico` (na 9) para `Agricultura` (na 10.1) são os **rerroteados**.
3. **Testar a borda móvel.** Verificar se o colapso de `pasto→agricultura` (e o
   pico de `pasto→21`) na 9 senta na **borda da 9**, não no mesmo ano-calendário
   da 10.1. Se cada coleção tem o colapso na sua própria borda, é o classificador,
   ponto final. Se ambas têm o colapso fixo no mesmo ano-calendário, é fenômeno
   real.

### 9.4 O que o teste entrega — e o que não entrega

- **Discrimina a presença do artefato mesmo com ILP real coexistindo.** Se houver
  os dois superpostos, o teste detecta o componente-artefato como um *excesso* de
  colapso na emenda terminal, acima da tendência de calendário. É uma decomposição,
  não um sim/não.
- **Alimenta o centro de massa.** Os pixels rerroteados têm coordenadas → dá para
  calcular o **centroide da agricultura escondida** e cravar a direção do viés no
  #32/#44 (ver a análise-companheira `centro_massa_deriva_check.py`, que já resolve
  a *direção* só com a 10.1). **Nota (23/jul/2026):** o rastreio pixel-a-pixel de
  `pasto→21` **com idade** já foi feito **sem** a Coleção 9, reprocessando o cubo da
  própria 10.1 (`processa_cubo_idade_destinos.py`, ver §8) — isso estabelece a
  *co-localização*. A Coleção 9 permanece necessária **só** para o passo que a
  10.1 não resolve: **discriminar artefato × ILP real** (a borda móvel de §9.3).
- **Não é pré-requisito para a dissertação.** O caminho defensável (SIDRA carrega
  o período terminal; manchete em `agric` e `agric∪mosaico`; taxas de transição
  truncadas em ~2019) **independe** da resposta da 9. O teste da 9 serve para
  *provar afirmativamente* a natureza do sinal — útil para um dossiê ao MapBiomas
  ou como contribuição de método —, não para blindar as conclusões.

### 9.5 Custo e viabilidade

Coleções antigas do MapBiomas são **públicas** (Google Earth Engine / downloads
por bioma-UF). O reprocessamento é o mesmo do cubo censitário do #28, restrito ao
recorte de Goiás e a ~3 anos de sobreposição terminal — ordem de minutos, não de
infra. O gargalo é operacional (baixar a 9), não computacional.

---

## 10. Decisão

**D25 — Antes de comparar uma medida de transição LULC entre períodos distantes,
verifique que a classe de destino manteve o mesmo significado.**

Uma série de transições `A→B` pressupõe que "B" quer dizer a mesma coisa no
começo e no fim. Classificadores evoluem, filtros temporais se comportam
diferente nas bordas da série, e classes "mistas" (mosaico, não-observado,
outros) absorvem silenciosamente o que o modelo deixou de resolver. O sintoma é
sempre o mesmo e é fácil de ler ao contrário: **a transição de interesse
"desaparece" enquanto o fenômeno de campo acelera.**

Diagnóstico barato, aplicável a qualquer par de classes: conte o destino
**completo** das saídas da classe de origem, ano a ano, e olhe as *frações*, não
os níveis. Se a fração que vai para o destino de interesse não é estável, a série
não é comparável — e nenhuma sofisticação estatística a jusante conserta isso.

Irmã da **D16** (Granger espúrio por integração) e da **D23** (ΔBIC sob censo):
as três são casos de um método correto rodando sobre uma série cuja *definição* se
move.

**D26 — como *tratar* a deriva numa análise (o complemento operacional de D25).**
`agricultura ∪ mosaico` **não é uma correção**, e sim o **limite superior** de um
intervalo cujo limite inferior é `agricultura` sozinha (a união superconta ILP + mosaico
antigo; assume 100% do Mosaico = agricultura mal-rotulada, o que é falso). Regra: **reportar
o intervalo `[agric, agric∪mosaico]`, nunca um ponto; conclusão robusta ⇔ sobrevive nos dois
extremos.** A união responde honestamente a uma **pergunta mais grossa** — "saiu de pasto
puro para lavoura-ou-uso-misto?" — não à fina ("virou lavoura pura?"). A **melhor evidência**
dos anos terminais é a **SIDRA** (imune), não o bracket; uma correção de *ponto* exigiria a
demonstração da §9 (pixel `pasto→21` / Coleção 9). Método completo e protocolo por tipo de
análise em [`metodologia/tratamento_deriva_mosaico.md`](../metodologia/tratamento_deriva_mosaico.md).

---

## Ver também

- [28_idade_pastagem.md](28_idade_pastagem.md) — o pipeline principal
- [28_idade_pastagem_critica.md](28_idade_pastagem_critica.md) — §4-C e §4-E, fechados aqui
- [28C_bimodalidade_regional.md](28C_bimodalidade_regional.md) — o gradiente regional, que sobrevive
- [censo_vs_amostra.md](../metodologia/censo_vs_amostra.md) — §3 (classe 21), §7.3 (censura = horizonte)
- [42_granger_reverso_norte_sul.md](42_granger_reverso_norte_sul.md) — D16, a armadilha irmã
