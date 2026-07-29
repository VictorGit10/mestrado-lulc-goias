# A varredura "número na tela × CSV" — a peça inteira, um a um (28/jul/2026)

> A varredura irmã da **D27** ([`auditoria_de_figuras.md`](auditoria_de_figuras.md)). A D27
> pergunta *o rótulo da figura ainda diz o que o pipeline conclui?*; esta pergunta
> **o número exibido é o número que está no CSV?** O `PLANO_DE_CONSTRUCAO.md` §19.4 a
> registrou como "outro método, que merece dia próprio" — foi ela que, feita *ad hoc* na
> Perna 4, achou os três erros da §18.6. Este é o dia próprio, feito sobre a peça inteira.

## 1. Método

1. **Extração mecânica**, não leitura: um parser de HTML percorre `reforma.html` e devolve
   toda frase que contém dígito, agrupada pelo `id` da seção que a contém (Partes 0–4 e as
   quatro pernas), marcando as classes de honestidade (`.nao-diz`, `.nota-honestidade`,
   `.autocorrecoes`, `.verificacoes-ok`, `.decisoes-corpo`, `.regua-decidiu`).
   **Resultado: 442 blocos com número, em 27 seções.** Ler a peça procurando números não
   funciona — foi assim que os três erros da §18.6 sobreviveram a três revisões.
2. **Cada número é rastreado até a fonte primária** — `data/processed/*.csv|parquet`,
   `Visualizacao/assets/data/*.json`, ou o pipeline em `Textos/pipelines/` quando o valor é
   estatística de modelo. Prosa não conta como fonte para prosa.
3. **As figuras SVG inline são decodificadas geometricamente** — as coordenadas do `path` e a
   largura dos `rect` são convertidas de volta a valores pela escala dos eixos e comparadas ao
   CSV. Uma figura autorada à mão pode desenhar um número diferente do que ela rotula, e nenhum
   teste do projeto olhava para isso.

## 2. O veredito, em uma linha

**Nenhuma conclusão da peça cai.** Das ~160 afirmações numéricas rastreadas, **quatro estão
erradas ou imprecisas**, nenhuma delas sustentando uma tese; **três** são questões de
apresentação ou arredondamento. O restante bate com a fonte — em boa parte ao decimal.

## 3. O que está garantido (e não precisa ser reaberto)

| bloco | o que foi conferido | resultado |
|---|---|---|
| **Parte 1 · os 5 cards do saldo** | veg 17,65→11,88 Mha (51,9%→34,9%); agric ×4,8 (1,17→5,58); soja ×12 área e ×13 produção; pasto +1,0 Mha com pico 14,80 em 2003; lotação 1,01→1,36; rebanho +46%; Mosaico 3,63→3,59 (10,7%→6,1%→10,5%) | **exatos** contra `painel_goias.json` + `transicoes_resumo.json` |
| **Parte 1 · Sankey** | 4,10 / 2,72 / 1,29 / 1,00 Mha; o par que se cancela (1,72 ↔ 1,62); razão PRODES 1,00→1,35 | **exatos** contra `sankey_data.json` |
| **Parte 1 · Ato III** | −88% (narrado como artefato); soja SIDRA +38%; união acelera ~50% (0,2697→0,4055 Mha/ano); pasto perde 0,076→0,273 Mha/ano; 34,9% | **exatos** |
| **Perna 1 · centro de massa** | +78 / +67 / +65 / +8 km e o IC que inclui zero; as **cinco medidas** 2019→2024 (+12,9 / +11,9 / +10,1 / +4,4 / +0,5); vãos 135 / 111 / 122 km; união −60 km; massa escondida +46,5 km e r=0,84; #43 pixel +79,2 / +66,9; campo nativo +35 km | **exatos** contra `centro_massa_*.csv` |
| **Perna 2 · censo de idade** | 44.639.028 px = 3.817.080 ha = 11,22%; 16,0 M não-censurados; σ 1,60 / 7,53; **162/164** (estrita) e **166/166** (imune); mesorregião 3,7%→0,5%; vale Noroeste 42%→6%; TV Sul×Norte 0,22→0,02; amplitude 7a→2a; 9/10→10/10 células; Ato II 32,5 M; crédito +0,22→+0,30 | **exatos** contra o parquet do censo, `forma_regional_*.csv`, `bimodalidade_uniao_check.csv` e o próprio JSON que o mapa desenha |
| **Perna 3 · a refutação** | θ<0 em **12/12** e p<0,05 em **1/12** (e é a régua exposta, θ=−0,157 p=0,0204); **0/24** temporais, menor p **0,0782**; poder 48%/93% (T=38); β −0,515→−1,144; simetria 69 km (77 em 2013) / 135 / 152 / 16 / 83 km | **exatos** contra `deslocamento_bracket_*.csv` e `centro_massa_capacidade_vaos.csv` |
| **Perna 4 · o teto** | decomposição inteira (Sul −0,0056 = −0,0010 + −0,0047, share 17,2%/82,8%; Centro e Norte idem); 0,0706→0,0721; −37% no Sul; p=0,4809 e p=0,9196; estoque 6,56 Mha, 61,5% de 1985, Norte 44,0%; Sul 53,0 / Centro 62,5 / Norte 64,7; −1,98 contra −3,48/−3,44 pontos; proteção 6,35/6,56=96,8% e 94,3% pixel, PI <3%, 89,1% da PI antes de 2000; carbono 973 (751–1208), floresta 499 × savânica 458, 80% (774 Mt) no Ato I a 20,5 Mt/ano, Ato III Sul 1,4 × Centro 4,6, centroide +98 km; câmbio 134,5→169,0, preço 104,4→186,4, crédito 14,3→24,1 bi; +51% × +244%; IFDM 0,49→0,63 e −0,083 [−0,108; −0,058]; +93% × +14% | **exatos** |
| **Parte 3 · autocorreções** | fechamento 7,26%→0,08%; 6,5–10,9% do estado; r=0,912 contra PRODES no regime anual (2013+); 24/24 subamostras; 3 das 4 hipóteses do fogo caíram; #45 caiu 9×; #54 p 0,03→0,07–0,13 | **exatos** |
| **Parte 4 · oficina** | F=62,152 e F=21,470; MW p=0,060 e poder 0,63; 6/9; ΔBIC 844.789; 43,7%; 63,7%/74,9%; razão 0,6→32,5; 115/140 Moran e I=+0,53; R² 0,122/0,047/0,072; 11/12; 9/36 placebos; N=11 | **exatos** |

### 3.1 As figuras SVG desenham o que rotulam

Verificação nova, que nenhum teste do projeto fazia. Decodificando a geometria:

| figura | escala recuperada | resultado |
|---|---|---|
| **cinco-medidas** (Perna 1) | 24 px/km | as 5 barras batem ao pixel (310/286/242/106/12 px) |
| **decomp** (Perna 4) | 30.000 px por Mha/ano | as 6 barras batem ao pixel |
| **estoquefig** (Perna 4) | 3,746 px por ponto percentual | a curva **reproduz o CSV a 0,1 pp** em todos os pontos conferidos (Sul 1999=66,7 · 2005=59,8 · 2024=53,0) |

Isto é uma garantia forte e vale dizer em voz alta: **as figuras autorais da peça não mentem
sobre os próprios dados.** O único defeito encontrado numa figura foi na *legenda em prosa* de
uma delas (§4.2) — e foi a figura, desenhada certo, que denunciou a legenda.

> **Estado (28/jul/2026): os quatro defeitos e as três imprecisões estão CORRIGIDOS** em
> `reforma.html` (e no `index.html` publicado, no caso do §4.1). Cada número introduzido foi
> reconferido contra a fonte, o HTML foi checado quanto a balanceamento de tags e a varredura de
> frases banidas voltou limpa. Um quinto caso, da mesma família do §4.3, foi encontrado ao
> aplicar as correções e também corrigido (ver §4.5).

## 4. Os quatro defeitos

### 4.1 `H = 22,6` é a estatística do teste errado — e está no site publicado

**Onde:** `reforma.html` linhas 182 e 2239; **`index.html` (no ar), 3 ocorrências.**

A tela diz: *"Kruskal-Wallis **H = 22,6**, p < 0,001 — os 3 Atos diferem significativamente em
taxa de mudança. É um teste único comparando os três períodos ao mesmo tempo."*

O `29_triangulacao_periodizacao.md`, seção **"Teste de 3 vs 4 períodos"**, dá:

- 3 períodos (P1 | P2+P3 | P4 — **a partição dos 3 Atos**): **H = 20,26**, p = 0,00004
- 4 períodos (P1 | P2 | P3 | P4 — a alternativa com a fronteira ~2005): H = 22,57, p = 0,00005

O número exibido é o do **teste de 4 períodos**, atribuído em texto ao de 3. O parágrafo
seguinte da própria peça diz que a candidata a 4º período foi rejeitada — ou seja, a peça
publica a estatística da partição que ela rejeita como se fosse a da que adota.

**Não muda a conclusão** (ambos p<0,001; a partição em 3 Atos continua validada). Muda o
número, na tabela de método que uma banca confere primeiro. **Correção: `H = 20,3`.**

### 4.2 "cruza os 60% ainda nos anos 1990" — a figura logo acima diz 2005

**Onde:** `reforma.html`, legenda da `estoquefig` (Perna 4). Também no
`PLANO_DE_CONSTRUCAO.md` §18.3, de onde a frase veio.

Pela régua **refinada** (a declarada na própria legenda: savânica + campo nativo, D13), o Sul
está em **66,7% em 1999** e cruza os 60% em **2005**. Só a régua `refinada_rl` (com o desconto
de 20% de Reserva Legal, que é cenário de sensibilidade, não a usada) cruza nos anos 1990.

O detalhe que torna isto instrutivo: **o SVG está certo.** A curva do Sul passa a linha de 60%
entre `x=314,2` (2004, 60,2%) e `x=325,8` (2005, 59,8%) — exatamente onde o CSV manda. A
figura desenha 2005 e a legenda embaixo dela diz "anos 1990". É a §18.8 ao contrário: aqui
quem envelheceu foi a prosa, não o rótulo.

**Não muda o argumento** — o Sul continua descendo mais rápido e mais cedo, e continua sendo o
único dos três que cruza os 60%. **Correção: "cruza os 60% em meados dos anos 2000"**, ou
"é o único dos três a cruzar os 60%".

### 4.3 "os placebos não acendem" — o #34 registra que um acende

**Onde:** `reforma.html` linha 1572, dentro do **"o que isto não diz"** da Perna 3 — o bloco
mais crítico da peça em matéria de honestidade.

A tela: *"O que carrega a conclusão é a conjunção: a assinatura prevista nunca aparece, **os
placebos não acendem**, e a explicação rival aparece em toda régua."*

O `34_deslocamento_espacial.md` registra, textualmente:

> *Mancha de especificidade, registrada:* na régua SIDRA/janela plena o **placebo norte** dá
> significativo (θ=−0,054, p=0,032) enquanto o alvo sul não (p=0,526). A especificação
> espacial sob a soja não separa direções de forma limpa — é uma razão a mais para não apoiar
> a refutação nesse canal.

Confirmado no CSV: dos 6 placebos direcionais (`Wx_norte`), **1 tem p<0,05**.

Esta é **exatamente a classe de defeito da §16.4** (o overclaim do iLUC): a prancheta escreveu
a ressalva, a tela afirmou o contrário, e as duas nunca foram lidas lado a lado. É a mais
séria das quatro justamente por estar no `.nao-diz`.

**Correção sugerida:** *"os placebos direcionais dão nulo em cinco das seis células — a
exceção está registrada no #34, e é uma das razões de a refutação não se apoiar nesse canal"*.
Dizer isso **fortalece** a peça: é o mesmo trade da §14 e da §16.5.

### 4.4 "Sul, Centro e Leste seguem com pico e ombro" — o Centro tem um vale raso

**Onde:** `reforma.html` linha 892 (Perna 2, o beat da troca de régua).

Sob a régua `agric`, o teste de vale empírico (`forma_regional_bimodalidade.csv`) dá:

| região | `tem_vale_emp` | `dip_emp` |
|---|---|--:|
| Noroeste | sim | **0,415** |
| Norte | sim | **0,271** |
| **Centro** | **sim** | **0,084** |
| Sul | não | 0,000 |
| Leste | não | 0,000 |

A frase é precisa sobre o Sul (*"simplesmente não existe"* ✓) e sobre Noroeste/Norte/Leste. Só
o Centro está do lado errado da divisão — com um vale de um quinto do Norte, mas não nulo.

**A conclusão de blocos está certa** e é o que sustenta o beat: pela distância entre formas, o
Centro fica com o trio do sul (TV 0,058 com o Sul e 0,092 com o Leste, contra 0,177–0,185 com
a dupla do norte). **Correção: "enquanto Sul e Leste seguem com pico e ombro, e o Centro fica
no meio do caminho, com um vale raso."** Vale corrigir porque o leitor **pode clicar no Centro
na peça e ver** — foi assim que este achado nasceu.

### 4.5 O quinto, encontrado ao corrigir o terceiro

Ao conferir o §4.3 notei o irmão dele duas telas antes: o `.nao-diz` do câmbio dizia *"os
placebos dão nulo, **não há antecipação**, o resultado não depende de um ano isolado"*. Os
placebos de desfecho são de fato nulos (p = 0,24 a 0,52 nas quatro células) e o jackknife é
limpo — mas o `54_defensabilidade_perna4.md` registra que o **placebo-no-tempo é borderline
para H1** (p≈0,06–0,07), limpo apenas para **H2**, a especificação exógena — que é o *headline*
**justamente por isso**.

Reescrito para dizer **qual** especificação passa limpa, em vez de generalizar. Mesmo padrão do
§4.3: o pipeline escreveu a ressalva, a tela generalizou, ninguém leu as duas lado a lado.

## 5. Três notas de precisão (não são defeitos)

1. **Soja SIDRA "+49 km"** (card da Perna 1). O CSV dá **48,28 km** e o `44_centro_massa_desagregado.md`
   publica **+48,3 km**. É arredondamento para cima além do valor. Trocar por **+48 km**.
   *(Vale notar a coincidência que pode ter causado o deslize: o `32_centro_massa.md` tem
   "+49,5" na mesma linha da agricultura — mas é a coluna `dleste_km`, não o deslocamento ao
   norte.)*
2. **Lotação "×1,35"** (card da Parte 1). A razão verdadeira é **1,337 (×1,34)**; ×1,35 sai de
   dividir os extremos já arredondados (1,36/1,01).
3. **AIC "−2.924 vs −2.924"** (F8, `p4-limites`). Os números estão **certos** (OLS −2923,64 ·
   SEM −2924,34), mas exibi-los arredondados para sustentar *"SEM vence OLS"* faz a frase
   parecer erro de digitação. Melhor: *"diferença de 0,7 ponto de AIC — empate prático"*.

E uma **inconsistência de convenção**, registrada porque alguém vai fazer a conta: o hero usa
**0,09 ha/pixel** (nominal de 30 m: 378 M px/ano, 15 bi em 40 anos) e o censo do #28 usa
**0,0855 ha/pixel** (área real na projeção: 44,6 M px = 3,82 Mha). Dividir 3,8 Mha por 0,09 dá
42,4 M, não 44,6 M. Nenhum dos dois números está errado; o projeto simplesmente não tem uma
constante única. *(Idem: `≈0,07–0,13` do #54 é o arredondamento do próprio pipeline — as quatro
células de permutação vão de 0,062 a 0,158.)*

## 6. O que esta varredura **não** cobre

Registrado para não virar falsa garantia:

- **Os 40 rasters WebP do mapa** — cores e classes dentro do binário. (A ausência do Mosaico
  está declarada na legenda, no *swatch* hachurado e na linha de fonte — ver §7.)
- **O que o Sankey e as duas peças interativas desenham em tela**: verifiquei o JSON que as
  alimenta, não o traço renderizado.
- Prosa sem número, glossário, mobile, cross-browser.

## 7. O outro item da D27 — a legenda de classes do mapa da Parte 1: **fechado**

O `PLANO_DE_CONSTRUCAO.md` §19.4 põe esta legenda como bloqueio de troca, por nunca ter sido
auditada e por a classe do bug conhecido (21, "Mosaico de Usos") ser justamente uma categoria
de legenda. Auditada agora, ela **declara a ausência em três lugares independentes**:

1. o *swatch* do Mosaico é **hachurado** (`repeating-linear-gradient`), único visualmente
   distinto dos sólidos — sinaliza "classe mista" sem prometer cor no mapa;
2. `title` do *swatch*: *"Classe 21 do MapBiomas… Aparece na barra, mas não é pintada no mapa"*;
3. **linha de fonte, em texto visível**: *"o Mosaico de usos entra na barra, mas fica
   transparente no mapa"*.

O item (3) é o que fecha — os outros dois dependem de *hover*. Sem ressalva pendente.

**O primeiro item da D27 (`deslocamento_latitude.png`, §19.3) continua aberto**: o PNG segue na
linha 554, plotando a série da agricultura em linha cheia e período inteiro, dois centímetros
abaixo do interativo que a corta em 2019 (`ANO_ROTULO_DERIVA`). Continua sendo decisão de autor
entre as três saídas da §19.3.

## 8. A regra que sai daqui

**Número exibido é afirmação, e afirmação envelhece do mesmo jeito que rótulo de figura.** Os
quatro defeitos têm a mesma origem: o valor estava certo quando foi escrito *ou* foi copiado da
linha vizinha da tabela certa, e ninguém releu tela e CSV lado a lado depois. Nenhum teste do
projeto pega isso — a varredura de frases banidas procura texto que *voltou*, não número que
*nunca bateu*.

Três padrões a vigiar, todos observados aqui:

1. **A linha vizinha da tabela certa.** §4.1 (H de 4 períodos em vez de 3) e a nota 1 da §5
   (coluna leste em vez de norte). O erro não vem de inventar número — vem de acertar a tabela
   e errar a linha.
2. **A prosa que envelheceu junto à figura que não envelheceu.** §4.2. A D27 previa o inverso;
   as duas direções acontecem, e **decodificar a geometria do SVG resolve as duas**.
3. **O `.nao-diz` que afirma mais do que o pipeline.** §4.3, terceira reincidência depois da
   §16.4 e da §17. Vale a regra explícita: *toda frase de "o que isto não diz" que afirme um
   nulo ("os placebos não acendem", "nada sobrevive", "não aparece em nenhum") precisa da
   contagem exata ao lado.* Nulo sem denominador é o overclaim mais fácil de cometer no bloco
   que existe justamente para evitá-lo.
