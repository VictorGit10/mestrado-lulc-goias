# Pipeline #34 — Deslocamento Sul→Norte: lead-lag + spillover espacial

**Script**: `scripts/deslocamento_espacial.py`
**Quando foi feito**: 2026-06-06. Camada 3 (econômica/formal) da narrativa de deslocamento Sul→Norte.
**Depende de**: #25 (painel AMC + geometria), #17 (deltas LULC), #18 (mesorregiões). Reusa convenções de #22 (painel FE) e #24 (pesos espaciais).
**Outputs**:
- `data/processed/deslocamento_series_regionais.csv` — séries anuais Sul/Norte + shares estaduais.
- `data/processed/deslocamento_leadlag.csv` — CCF (pico) + Granger por relação.
- `data/processed/deslocamento_slx.csv` — coeficientes do SLX em painel FE.
- `outputs/deslocamento/shares_regionais.png` — concentração regional no tempo.
- `outputs/deslocamento/leadlag_ccf.png` — correlação cruzada defasada.
- `outputs/deslocamento/slx_coeficientes.png` — coeficiente de vizinhança (IC95%).

---

## Pergunta de pesquisa

As Camadas 1 (#32, centro de massa) e 2 (#33, mecanismo) mostraram uma **coincidência espacial**: a agricultura avança/ancora no Sul; o pasto e o rebanho sobem para o Norte. A Camada 3 faz o **teste formal de deslocamento** (iLUC intra-estadual) — separa "padrão" de "mecanismo causal":

> (A) **Temporal** — a expansão da agricultura no Sul *antecede* o avanço de pasto/rebanho no Norte?
> (B) **Espacial** — a agricultura dos *vizinhos ao sul* prevê o crescimento de pasto/rebanho *local*?

## Decisão de janela: tempo contínuo

Roda sobre o **painel anual** (AMC, #25) com **defasagens** — não bina por ato. Os atos só entrariam como interação de robustez. **Por quê**: a periodização (#29) foi definida em parte a partir de transições; usá-la para analisar deslocamento reintroduziria circularidade. Métodos de painel/séries usam o tempo contínuo naturalmente. É o **princípio 4 da [Decisão D12 — janelas temporais](../metodologia/janelas_temporais.md)** (anti-circularidade).

---

## A intuição: padrão não é mecanismo

Que a agricultura esteja no Sul e o rebanho no Norte (um **padrão** espacial) não prova que *um empurra o outro* (um **mecanismo causal**). Dois processos independentes — agricultura no Sul e pecuária no Norte — movidos pela **mesma força** (boom de commodities, crédito) produziriam o mesmo padrão, sem qualquer deslocamento direto. A Camada 3 tenta distinguir as duas leituras com dois testes que, se o deslocamento fosse real, dariam positivo:

- **Precedência temporal** (lead-lag): se o Sul *empurra*, ΔAgric_Sul deveria *anteceder* ΔPasto_Norte.
- **Spillover espacial direcional**: se o Sul *empurra*, a agricultura dos meus vizinhos **ao sul** deveria prever **crescimento** do meu pasto (pasto empurrado para cima, para dentro de mim) — coeficiente θ>0.

---

## O que faz

1. **Recorte regional** (Parte A): cada AMC recebe sua mesorregião modal; agregam-se totais anuais de agricultura (Sul) e pasto/rebanho (Norte+Noroeste). Séries em primeiras diferenças.
2. **Lead-lag** (Parte A): correlação cruzada `corr(ΔAgric_Sul_{t}, ΔY_Norte_{t+k})` para k=−5..+5 (k>0 ⇒ Sul antecede) + **Granger** (com teste **reverso** como placebo direcional).
3. **Spillover espacial** (Parte B): matrizes de vizinhança **direcionais** (k=8 vizinhos mais próximos, filtrados por estarem **ao sul** / ao norte / todos), linha-padronizadas. **SLX** em painel 2-way FE (entidade + ano, SE clusterizado por AMC):
   $$\Delta\text{pasto}_{it} = \beta\,\Delta\text{agric}_{it} + \theta\,(W_{\text{sul}}\Delta\text{agric})_{it} + \alpha_i + \gamma_t + \varepsilon_{it}$$
   θ é o coeficiente-chave: agricultura dos vizinhos ao sul prevê pasto local? Placebo = vizinhos ao norte.

---

## Achados — e por que são um resultado de "não-confirmação"

### 1. O padrão descritivo existe (e é forte)
A concentração regional move-se exatamente como a narrativa prevê: a **agricultura no Sul cai de ~92% para ~71%** do estado (ela se espalha para fora, mas segue dominante no Sul), e **pasto/rebanho no Norte+Noroeste sobem de ~21% para ~37%/34%**. Figura A.

### 2. Não há precedência temporal Sul→Norte
- **Granger ΔAgric_Sul → ΔPasto_Norte: p = 0,97** (lag 1) — **nulo**. A agricultura do Sul **não** antecede o pasto do Norte.
- A CCF é positiva em todas as defasagens (co-movimento), mas **mais forte quando o Norte lidera** (lags negativos, r até 0,60) do que quando o Sul lidera (lags positivos, r 0,23–0,37).
- O **teste reverso** (ΔPasto_Norte → ΔAgric_Sul) é que dá significativo (**p = 0,0007**). Se há precedência, ela corre **Norte→Sul**, não Sul→Norte.

### 3. Não há spillover espacial de deslocamento
No SLX (figura C):
- **Substituição local forte e robusta**: `Δagric → Δpasto` local **β = −0,52 (p<0,001)** — onde a lavoura entra, o pasto local sai (intensificação; confere com #22).
- **Mas o termo de deslocamento é nulo/invertido**: a agricultura dos vizinhos **ao sul** prevê pasto local com **β = −0,16 (p = 0,02)** — **negativo**, não o θ>0 que o deslocamento exigia. Vizinhos **ao norte** (placebo) e **todos** os vizinhos: não significativos.
- **Rebanho**: nenhum spillover dos vizinhos ao sul (p = 0,26).

A leitura do sinal negativo: a agricultura **co-expande no espaço** (clusters de lavoura crescem juntos) e o pasto recua junto com ela — o oposto de pasto sendo *empurrado* para os vizinhos do norte.

### 4. Síntese honesta — reorganização, não deslocamento causal
> O padrão Sul→Norte é **real como reorganização espacial**, mas os testes formais **não sustentam um mecanismo de deslocamento causal** (a lavoura do Sul empurrando o rebanho ao Norte). O quadro é mais consistente com **co-evolução sob um drive comum** (boom de commodities/crédito) sobre um **gradiente estrutural de aptidão** (lavoura favorecida no Sul; terra de fronteira barata no Norte). Os mecanismos são **locais e paralelos**: no Sul, agricultura substitui pasto (intensificação); no Norte, pasto avança sobre o Cerrado (fronteira). Rodam em paralelo, movidos pelas mesmas forças, e o resultado *parece* deslocamento.

**Implicação para a redação**: descrever como **"reorganização espacial / divisão regional do trabalho agropecuário"**, **não** como iLUC/deslocamento causal comprovado. É a leitura defensável — e mais forte por ser honesta (mesma postura do #23/#26, que rebaixaram efeitos que não replicaram).

---

## Como ler as figuras

### A. `shares_regionais.png` — a montagem do padrão
Participação no total estadual: agricultura no Sul (cai), pasto/rebanho no Norte (sobem). Mostra a reorganização — o "antes de qualquer teste causal".

![Shares regionais](../../outputs/deslocamento/shares_regionais.png)

### B. `leadlag_ccf.png` — quem antecede quem?
Correlação cruzada ΔAgric_Sul × ΔY_Norte. Barras **verdes** (k>0) = Sul antecede; **cinzas** (k<0) = Norte antecede. As cinzas são mais altas → se há precedência, é Norte→Sul, contrariando o deslocamento.

![Lead-lag CCF](../../outputs/deslocamento/leadlag_ccf.png)

### C. `slx_coeficientes.png` — o teste espacial
Coeficiente θ do termo de vizinhança (W·Δagric), IC95%. O deslocamento previa θ>0 (faixa verde). O único significativo (Δpasto ~ vizinhos ao sul) é **negativo**; os demais, nulos.

![SLX coeficientes](../../outputs/deslocamento/slx_coeficientes.png)

---

## Decisões metodológicas

- **Tempo contínuo** (não atos) — evita circularidade com #29 (ver acima).
- **Recorte Sul = Sul Goiano; Norte = Norte + Noroeste Goiano** (coerente com #33). 58 AMCs no Sul, 30 no Norte+Noroeste.
- **Pesos direcionais**: k=8 vizinhos mais próximos filtrados por latitude do centroide (EPSG:5880). Linha-padronizados.
- **SLX (não Durbin/SAR)**: o termo espacial é `W·X` (exógeno), estimável por PanelOLS com FE — sem a maquinaria ML do spreg, mais robusto e interpretável para um primeiro teste de deslocamento.

---

## Limitações

- **N pequeno no lead-lag** (39 primeiras diferenças, agregado regional) → **baixo poder do Granger, agora quantificado**. Simulação Monte Carlo do próprio teste (`grangercausalitytests`, ssr F, T=38, em `scripts/_poder_granger_deslocamento.py`): tamanho do teste 5% no nulo, mas o poder é só **~48% para um efeito moderado** (correlação parcial ≈0,3) e **~93% para um grande** (≈0,5). **Consequência**: o nulo forward (p=0,97) é fraco *por si só* — não *refuta*, apenas *não corrobora* — e o reverso significativo deve ser lido como sugestivo, não firme. ~~O que sustenta a leitura de **não-deslocamento causal** é o **spillover direcional de sinal trocado** (θ=−0,16, **p=0,02**), somado ao Toda-Yamamoto (#42).~~ → **Revisto em 28/jul/2026** pela auditoria da mudança de rótulo (seção abaixo): a *significância* do spillover **também não é robusta** (p<0,05 em 1 de 12 células). O que sustenta a leitura de não-deslocamento é a conjunção de **três coisas que sobrevivem ao bracket** — o nulo temporal (0/24 células significativas em três réguas), a **ausência universal da assinatura prevista** (θ>0 nunca aparece; θ<0 em 12/12) e a **substituição local** (robusta nas três réguas) — somada ao Toda-Yamamoto do #42. Nenhum p-valor isolado carrega a refutação.
- **Teste espacial é local e contemporâneo** (vizinhos imediatos, mesmo ano). **Não descarta** deslocamento de longo alcance ou de defasagem muito longa — apenas mostra que a assinatura local/direcional esperada **não aparece**.
- **O drive comum é inferido, não testado.** Atribuir o co-movimento ao boom/crédito é a leitura mais parcimoniosa; provar exigiria instrumentos de preço/crédito (fora do escopo).
- **Agregação regional e de AMC** suaviza heterogeneidade interna; um deslocamento muito localizado poderia escapar das duas escalas (mas as duas concordam no nulo).

---

## Conexão com a narrativa (fecho das 3 camadas)

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| 1 | #32 | **Onde** está a massa e para onde foi? | Agricultura ancora no Sul; pasto/rebanho sobem ao Norte (padrão real). |
| 2 | #33 | **Como** (composição)? | Sul: pasto→agric (pasto jovem); Norte: veg→pasto (fronteira). Sul perde pasto líquido, Norte ganha. |
| 3 | #34 | **Por quê** — o Sul *causa* o Norte? | **Não** há precedência (Granger nulo) nem spillover direcional (θ≤0). Co-evolução sob drive comum + gradiente de aptidão, não deslocamento causal. |

**A narrativa final**: uma **reorganização espacial da produção agropecuária** em Goiás — intensificação no Sul, fronteira no Norte — coordenada por forças de mercado comuns, e não um empurrão causal direto de uma região sobre a outra. As três camadas, juntas, contam isso com honestidade.

---

## Robustez à mudança de rótulo do Mosaico (#28D/D25) — auditoria de 28/jul/2026

**Por que só agora.** A varredura de 23–25/jul percorreu #33, #40, #28C, #49, #39, #47,
#48, #22/#24, #32/#44 — e **não alcançou o #34**. Ele não aparece na tabela do §9 de
[`tratamento_deriva_mosaico.md`](../metodologia/tratamento_deriva_mosaico.md) nem no §5.4 do
[#28D](28D_deriva_mosaico.md), e este documento não mencionava Mosaico/D25/D26 uma única
vez. A lacuna foi encontrada em 28/jul ao construir a Perna 1 da visualização, a partir de
uma pergunta do autor. **É a manchete da Perna 3**, então valia fechar.

**A exposição era concreta**: o Bloco A monta `agric_mha_Sul` a partir de
`lulc_agricultura_ha`; o Bloco B usa `agricultura_delta_mha`. As duas são a classe que o
rótulo esvazia nos anos terminais.

**O teste** (`scripts/deslocamento_bracket.py`, D26): os dois blocos reestimados em
**três réguas** — `agric` (piso) · `agric ∪ mosaico` (teto) · **soja plantada SIDRA**
(âncora imune, medida em campo) — × **duas janelas** — plena e **truncada em 2019**, que
remove inteiramente a cauda contaminada (a mudança de rótulo é ancorada no calendário,
2021+). O companheiro **reproduz o original antes de bracketá-lo**: na régua crua/janela
plena devolve Granger p=0,971 e θ=−0,1572 (p=0,0204), que são os números publicados acima.

### Bloco A — sem precedência temporal: ✅ ROBUSTO

**24 células** (3 réguas × 2 janelas × 2 desfechos × 2 lags). **Nenhuma** atinge p<0,05; o
menor p é **0,078**. O nulo não é criatura da mudança de rótulo, e a deriva não podia estar
escondendo uma precedência — na janela truncada, sem a cauda, o quadro é o mesmo.

*Achado colateral que reforça o #42:* o **pico da CCF é instável entre réguas** — lag −1
(r=+0,60) na crua, lag 0 (r=−0,45) na união, lag +4 (r=−0,15) na SIDRA. Precedência
aparente que muda de sinal e de defasagem conforme a régua é exatamente a assinatura de
co-tendência espúria que o [#42](42_granger_reverso_norte_sul.md) demonstrou por outro
caminho (**D16**).

### Bloco B — substituição local: ✅ ROBUSTO (e reforçado)

`Δagric → Δpasto` local: **β<0 em 12/12 células**, com p<0,001 nas três réguas na janela
plena — **−0,515** (crua), **−1,144** (união), **−0,072** (SIDRA). O canal **cresce** sob a
união, o que faz sentido: com o Mosaico dentro, a medida de conversão fica mais completa e
a substituição local aparece maior. É o efeito mais firme do #34 e sobrevive intacto.

### Bloco B — spillover direcional: ⚠️ **SINAL ROBUSTO, SIGNIFICÂNCIA NÃO**

Esta é a única mudança de veredito da auditoria, e ela pede correção na redação.

| régua | janela | θ (Wsul·Δx → Δpasto) | p |
|---|---|---|---|
| Agricultura (MapBiomas) | plena | **−0,157** | **0,020** |
| Agricultura (MapBiomas) | truncada 1985–2019 | −0,122 | 0,083 |
| Agricultura ∪ Mosaico | plena | −0,050 | 0,545 |
| Agricultura ∪ Mosaico | truncada | −0,075 | 0,422 |
| Soja plantada (SIDRA) ◆ | plena | −0,012 | 0,526 |
| Soja plantada (SIDRA) ◆ | truncada | −0,025 | 0,094 |

**O que sobrevive:** o **sinal**. θ é negativo em **12/12** células (as 6 acima mais as 6 do
desfecho rebanho). A hipótese de deslocamento prevê **θ>0**, e não há uma única
especificação em que isso apareça — muito menos significativa.

**O que não sobrevive:** a **significância**. O p<0,05 aparece em **1 de 12** células, e é
exatamente a régua exposta na janela plena — a mais contaminada.

**A leitura honesta, e por que não dá para salvar o p=0,02.** A defesa natural seria
atenuação: a união acrescenta ruído de classificação ao regressor e empurra coeficientes
para zero. Mas o **termo local vai na direção contrária** — ele *dobra* sob a união
(−0,515 → −1,144, p<0,001). Uma régua que fortalece um canal e apaga o outro não está se
comportando como ruído puro. Isso **inclina** a leitura para o lado desconfortável: parte da
significância do spillover dependia do rótulo. O bracket não separa as duas explicações com
certeza — e, pela regra da D26, o que não sobrevive às três réguas se reporta como
**intervalo, não como ponto**.

*Mancha de especificidade, registrada:* na régua SIDRA/janela plena o **placebo norte** dá
significativo (θ=−0,054, p=0,032) enquanto o alvo sul não (p=0,526). A especificação
espacial sob a soja não separa direções de forma limpa — é uma razão a mais para não
apoiar a refutação nesse canal.

### Veredito e o que muda na redação

**A refutação da hipótese-mãe permanece de pé — e sobre duas pernas robustas, não três.**
Nenhuma especificação, em nenhuma régua, produz a assinatura que o deslocamento causal
exige. O que muda é **em que apoiá-la**:

| leg | antes | depois da auditoria |
|---|---|---|
| sem precedência temporal | nulo de baixo poder, "não refuta sozinho" | **robusto nas 3 réguas e nas 2 janelas** (0/24 células significativas) |
| spillover de sinal trocado | ⚠️ "**é ele que refuta**" (θ=−0,16, p=0,02) | **sinal robusto (12/12 negativo); significância não** — não citar o p=0,02 como se fosse robusto |
| substituição local | forte | **robusta nas 3 réguas**, e maior sob a união |

🚫 **Não escrever mais**: "o spillover é significativo e de sinal trocado (p=0,02), e é ele
que carrega a refutação". ✅ **Escrever**: "a assinatura que a hipótese exige (θ>0) **não
aparece em nenhuma régua**; o coeficiente é negativo em todas as 12 especificações
testadas, e o único estimador significativo está na régua que a mudança de rótulo
contamina".

**Padrão que se repete, e vale nomear.** É o mesmo movimento do [#54](54_defensabilidade_perna4.md)
na Perna 4: sob a inferência correta o achado perde significância e ganha defensabilidade,
porque passa a se apoiar na **especificidade** (a assinatura prevista nunca aparece) em vez
de num p-valor único. Duas vezes o trabalho trocou um número bonito por um argumento mais
difícil de derrubar.

**Saídas**: `data/processed/deslocamento_bracket_leadlag.csv`,
`data/processed/deslocamento_bracket_slx.csv`.
