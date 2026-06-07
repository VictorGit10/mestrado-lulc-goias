# Pipeline #37 — Caracterizar o "drive comum"

**Scripts**: `scripts/coleta_drivers_macro.py` (#37A, coleta) + `scripts/drive_comum.py` (#37B, análise)
**Quando foi feito**: 2026-06-06. Sequência direta do #34, que fechou a narrativa Sul→Norte num nulo causal e atribuiu o co-movimento a um "drive comum" **inferido, não testado** (ver `34_deslocamento_espacial.md`, Limitações).
**Depende de**: IPEA Data API; #17 (deltas LULC UF); #26 (quebras estruturais); #34 (séries regionais, ponte). Reusa `ccf_defasada`/`granger` (#34) e `pearson_with_hac` (#21).
**Outputs**:
- `data/processed/drivers_macro_anual.csv` — drivers macro exógenos 1985–2024.
- `data/processed/drive_comum_alinhamento.csv` — drivers nas quebras empíricas do LULC.
- `data/processed/drive_comum_leadlag.csv` — CCF + Granger (com placebo de exogeneidade).
- `data/processed/drive_comum_distlag.csv` — distributed-lag HAC + decomposição de canais.
- `data/processed/drive_comum_ponte_regional.csv` — driver → expansão Sul/Norte (#34).
- `outputs/drive_comum/timeline_drivers.png` — overlay drivers × quebras (figura-manchete).
- `outputs/drive_comum/leadlag_ccf.png` — correlação cruzada defasada.
- `outputs/drive_comum/distlag_canais.png` — decomposição canal preço vs câmbio.

---

## Pergunta de pesquisa

O #34 mostrou que a reorganização Sul→Norte **não** é deslocamento causal (iLUC) e propôs que ela é **co-evolução sob um drive comum** — mas o drive ficou *inferido*. Este pipeline o **materializa e testa**:

> As viradas dos drivers macro exógenos (preço de commodity, câmbio, crédito) **antecedem** as inflexões empíricas do LULC de Goiás? Por quais **canais** (preço vs câmbio)? E o **mesmo** driver move a agricultura no Sul **e** a fronteira no Norte?

O alvo são as **6 quebras estruturais de GO** do #26 — veg. natural **1998/2005**; pastagem **1991/2001/2020**; agricultura **2018** — incluindo as **órfãs** (pastagem 1991/2020, sem marco institucional limpo).

---

## A intuição (em linguagem simples)

Imagine duas pessoas em cantos diferentes de uma praça que, de repente, começam a andar na mesma direção. Há duas explicações: (a) uma está **empurrando** a outra; ou (b) as duas ouviram o mesmo **trovão** e correm para o mesmo abrigo. O #34 testou e **descartou o empurrão** (a agricultura do Sul não empurra o pasto do Norte). Sobra o trovão: uma **força externa comum** que move as duas regiões ao mesmo tempo. **Este pipeline procura o trovão.**

Os candidatos são três forças de mercado que um produtor de Goiás **não controla**:
- **Preço internacional** da soja e do boi (em dólar) — o super-ciclo de commodities puxado pela China.
- **Câmbio** — quantos reais vale um dólar. Um real mais fraco (desvalorização) torna exportar muito mais lucrativo em reais.
- **Crédito rural** — quanto dinheiro o sistema financeiro injeta na agropecuária.

**Por que "preço recebido", e não só o preço?** O produtor não decide olhando o preço em dólar nem o câmbio isoladamente — ele olha o **produto dos dois**: o preço em reais que de fato cai no bolso. Soja a US$ 400/t com dólar a R$ 2 é uma coisa; a mesma soja com dólar a R$ 5 é outra completamente diferente. Por isso a série-manchete é o **"preço recebido" = preço internacional × câmbio** (em índice real). Ela junta, num número só, a desvalorização de 1999/2002 **e** o super-ciclo de preços.

**Como se testa se uma força "dirige" o LULC?** Se o crédito (ou o câmbio) realmente puxa a conversão da terra, ele deve **se mexer primeiro** — a causa antecede o efeito. É isso que o teste de **Granger** mede: o passado do driver ajuda a prever a inflexão do LULC, *além* do que o próprio passado do LULC já preveria? É **precedência preditiva**, não prova de causalidade — mas é o que distingue um driver de um mero acompanhante.

**O truque do placebo.** Goiás é grande, mas não move o preço mundial da soja. Então, se rodarmos o teste **ao contrário** (o LULC de Goiás "prevê" o preço internacional?), o resultado **tem** que dar nulo. Se desse significativo, saberíamos que a série está mal construída (uma terceira variável contaminando os dois lados). Esse teste reverso é o nosso **controle de qualidade da exogeneidade** — e ele passou em todos os pares.

---

## Decisão de base de driver: preço recebido = preço global × câmbio

A hipótese de transmissão do boom é que o **preço recebido em R$** — preço internacional (super-ciclo China) ponderado pela **competitividade cambial** (desvalorização real de 1999/2002) — é o que sincroniza a intensificação no Sul e a fronteira no Norte. Escolheu-se a base **"preço recebido"** (sobre preço doméstico CEPEA) por ser a mais defensável:

1. **Exogeneidade limpa** — o preço internacional não é movido por Goiás → sem causalidade reversa, o que torna o Granger/lead-lag interpretável (o teste reverso vira **placebo de exogeneidade**).
2. **Janela completa 1985–2024** sem lacuna → cobre o pré-Real e as órfãs.
3. **É o próprio mecanismo de transmissão** — preço × câmbio captura num só número a desvalorização de 1999/2002 **e** o super-ciclo, e é **decomponível** nos dois canais.

### Fontes (todas IPEA Data OData4 — reprodutível, ativo, janela completa)

| Série IPEA | Conteúdo | Uso |
|---|---|---|
| `IFS12_SOJAGP12` / `IFS12_BEEFB12` / `IFS12_MAIZE12` | Preços internacionais (IMF IFS), US$, mensal | preço global → média anual |
| `GAC12_TCERXTINPC12` | Câmbio efetivo real (REER, INPC-exportações, índice 2010=100), 1980–2024 | **câmbio real** (maior = mais desvalorizado) |
| `BM_ERV` | Câmbio nominal R$/US$ comercial venda média, anual | preço recebido em R$ real (1994+) |
| `CREATE` (TERCODIGO=52) | Fluxo de crédito rural de **Goiás**, R$ de 2010, 1969+ | proxy de crédito **longo** (ponte com SICOR 2013+) |

**Construções**: `preco_recebido_*_idx` = preço_USD × REER (índice real, janela completa, série-manchete); `preco_recebido_*_brl_real` = preço_USD × câmbio nominal deflacionado por IPCA→dez/2024 (R$/t intuitivo, válido 1994+); `credito_rural_go_real` = CREATE reescalado 2010→dez/2024.

**Decisão de janela**: nível **UF/anual** em **primeiras diferenças** (D7) — o drive é exógeno e comum, então a análise é de co-movimento temporal, não de painel espacial. O REER (real, índice) **contorna a troca de moedas pré-1994** (Cruzeiro→Real), problema que a deflação nominal não resolve.

> **Nota (pós-resultados):** a base "preço recebido" cumpriu o papel de exogeneidade e janela completa, mas o sinal de **precedência** (Granger → pasto; ponte → rebanho) é carregado pelo **fator câmbio, não pelo preço** (ver Achado #5). Cuidado com a distinção: isso é **precedência preditiva**, não **amplitude** — na decomposição padronizada o câmbio **não** pesa mais que o preço (Achado #3). E a própria **decisão de janela UF/anual é a fonte do baixo poder**: N ≈ 38 fixa o teto (ver a discussão de N abaixo); a tentativa de recuperar poder mudando a unidade para o **painel AMC** (#38, interação driver × exposição) só produziu um gradiente **sugestivo** no rebanho — não rodar mais lags/drivers no agregado.

---

## Achados

### 1. Alinhamento: as quebras sentam em cima das viradas dos drivers
A figura-manchete (`timeline_drivers.png`) e a tabela de alinhamento materializam o drive — inclusive as **órfãs**:

| Quebra (classe) | Preço recebido (var. triênio ant.) | Câmbio real | Crédito GO | Leitura |
|---|---|---|---|---|
| **2001** (pastagem) | **+24%** | **+64%** | **+45%** | boom: preço/câmbio/crédito disparam *antes* — início da substituição de pasto |
| **2020** (pastagem) | **+47%** | **+51%** | +8% | surto de preço/câmbio pós-2018 precede a nova retração de pasto |
| **1991** (pastagem, *órfã*) | −40% | −19% | **−56%** | **colapso de crédito do Plano Collor** (confisco 1990) trava a pastagem — não é boom, é crise |
| **2005** (veg. natural) | −10% | −24% | −33% | apreciação cambial pós-2002 + queda de crédito → desaceleração da perda de vegetação |
| **1998** (veg. natural, Kandir) | −15% | −15% | +18% | misto |
| **2018** (agricultura) | −2% | −1% | +5% | drivers estáveis — a freada da agricultura **não** tem assinatura macro forte |

A órfã de **1991** ganha materialidade (colapso de crédito Collor); **2001/2020** (pastagem) são precedidas por surtos cambiais+preço.

### 2. Lead-lag formal: câmbio e crédito **antecedem**; preço **não lidera**
> **Caveat de multiplicidade (ler antes dos bullets):** são **3 hits em 36 testes Granger forward** (6 drivers × 3 classes × 2 lags). O acaso entrega ~1,8 a α=0,05, então isto está **no limite do ruído** e **não sobrevive a correção** (Bonferroni/FDR). Os p-valores abaixo são **exploratórios**; o que dá crédito ao câmbio não é o p isolado, é ele **também** reaparecer na ponte regional (Achado #4).
- **Câmbio real → taxa de pastagem**: Granger **p = 0,046** (lag 2); reverso nulo (p = 0,58). A competitividade cambial precede a retração do pasto. *(O lag 3 é o pico da CCF, não o do teste de Granger — não confundir.)*
- **Crédito rural GO → taxa de agricultura**: Granger **p = 0,037** (lag 2); reverso nulo (p = 0,38). Mas crédito é **parcialmente endógeno** — entra como contexto, não como driver exógeno.
- **Crédito rural GO → taxa de veg. natural**: Granger **p = 0,024** (lag 2); reverso nulo (p = 0,11). Mesma ressalva de endogeneidade.
- **Preços de commodity (soja/boi, USD ou recebido) NÃO Granger-lideram** (p = 0,24–0,81). A leitura "transmissão contemporânea" repousa em **uma única** correlação (preço boi → pasto, lag 0, p = 0,014) — fina, **não sobrevender**.
- **Placebo de exogeneidade OK** — em **nenhum** par a taxa de LULC Granger-causa o preço internacional (todos os reversos p > 0,08). A série está bem construída.

### 3. Decomposição de canais: nenhum canal isolado se sustenta — e o câmbio **não** domina em amplitude
No distributed-lag conjunto (HAC, regressores **padronizados** para amplitude comparável), **nenhum canal é individualmente significativo** (R² 0,01–0,06; N≈38). E, ao contrário da leitura inicial, o câmbio **não** tem maior magnitude: com os dois canais na mesma escala, a contribuição do **preço** iguala ou supera a do câmbio — na **pastagem** (classe-manchete) o preço pesa **o dobro** (β_preço = −0,043 vs β_câmbio = −0,022, lag 2; ambos p > 0,15); na agricultura empatam (−0,012 vs −0,015, lag 0). A impressão anterior de "câmbio domina" era **artefato de unidade**: a 1ª diferença do preço em US$ tem desvio-padrão ~3× a do REER, o que inflava o β **bruto** do câmbio sem que ele dominasse de fato. No **univariado**, só sobrevivem `preço boi → pastagem` (lag 0, r = −0,25, p = 0,014) e `preço recebido soja → pastagem` (lag 2, r = −0,27, p = 0,041) — **a pastagem é a classe mais responsiva** (ela é o estado-pivô: avança na fronteira e é convertida no Sul). Note que o câmbio→LULC **univariado é ~0 em todos os lags** (p = 0,46–0,94): a única âncora do câmbio aqui é o Granger (Achado #2) e a ponte regional (#4), **não** a amplitude da decomposição.

### 4. Ponte com o Sul→Norte: o câmbio puxa o rebanho do Norte
- **Δ câmbio real → Δ rebanho Norte**: r = **+0,36**, **p = 0,027** (lag 1) — o **mesmo** driver macro (competitividade cambial) precede o crescimento do rebanho no Norte. É o elo que liga o drive comum à reorganização: a depreciação não "empurra" o Sul sobre o Norte (#34), mas **estimula independentemente** a pecuária de fronteira no Norte.
- Demais elos (preço/crédito → expansão regional) fracos (p > 0,12).

### 5. Síntese honesta — uma assinatura cambial fraca, a confirmar com mais poder
> O "drive comum" ganha **alguma** materialidade empírica, mas o leitor precisa saber o tamanho do alfinete: somando os ~135 testes do pipeline (Granger + Pearson + ponte), ~7 dão p < 0,05 — praticamente o que o acaso entrega a α = 0,05 (≈ 6,8), e **nada sobrevive a correção de multiplicidade** (Bonferroni/FDR). O que dá peso a um achado aqui **não é o p-valor isolado, é replicar em construções independentes**. Por esse critério, **um único fio tem estrutura: o câmbio real (REER)**. Ele aparece em duas margens — Granger → taxa de pastagem (p = 0,046, lag 2) **e** ponte → rebanho do Norte (r ≈ 0,30–0,36, p ≈ 0,03, lags 0–1) — com sinal coerente e exogeneidade limpa. O **crédito** acende (→ agricultura/vegetação, lag 2), mas é **parcialmente endógeno** (política responde ao ciclo): entra como contexto, não como driver. O **preço** de commodity **não lidera** (Granger 0,24–0,99); a leitura "co-move contemporâneo" repousa em uma única correlação e não deve ser sobrevendida. Importante separar **precedência** de **amplitude**: dentro do construto "preço recebido = preço × câmbio", **quem carrega a precedência (Granger → pasto; ponte → rebanho) é o câmbio** — mas em **amplitude** a decomposição padronizada **não** dá vantagem ao câmbio (Achado #3). Leitura mais forte e honesta: a reorganização Sul→Norte do #34 carrega uma **assinatura de competitividade cambial** sobre o gradiente de aptidão — **precedência preditiva fraca, não causalidade**, e a testar num desenho de maior poder (painel AMC, #38).

**Implicação para a redação**: o item 5 da tese (`tese_central_rascunho.md`) sai de "evidência indireta, a completar" para **"drive comum parcialmente testado: assinatura de competitividade cambial (→ pasto e → rebanho do Norte); preço NÃO lidera; crédito é contexto endógeno; exogeneidade confirmada nos placebos"**. Mantém-se a honestidade **dupla**: é **precedência preditiva** (Granger), não causalidade, **e** os hits não sobrevivem a correção de multiplicidade — o que sustenta o câmbio é a **replicação em duas margens**, não o p-valor. O teste de maior poder fica para o painel AMC (interação driver × exposição).

---

## Como ler as figuras

### A. `timeline_drivers.png` — drivers × quebras (manchete)
Painel superior: preço recebido soja (índice real) e câmbio real efetivo, com linhas pontilhadas nos anos de quebra do #26 e atos sombreados. Picos de competitividade em **2002** e **2020** antecedem as quebras de pastagem. Painel inferior: crédito rural GO (R$ real), com a janela SICOR (2013+) destacada — mostra a **ponte** que a série longa CREATE faz com o período pré-SICOR.

![Timeline drivers](../../outputs/drive_comum/timeline_drivers.png)

### B. `leadlag_ccf.png` — quem antecede quem
Correlação cruzada Δdriver × taxa LULC. Barras **verdes** (lag > 0) = o driver lidera. Para a pastagem, preço recebido e crédito têm correlações negativas crescentes em lags +2/+3 (driver lidera a retração); para a agricultura, o câmbio lidera em lags +2/+3.

![Lead-lag CCF](../../outputs/drive_comum/leadlag_ccf.png)

### C. `distlag_canais.png` — preço vs câmbio
Coeficientes **padronizados** do distributed-lag por canal e classe (os dois canais na mesma escala). Ao contrário da versão anterior (β brutos), **o câmbio (roxo) NÃO supera o preço (verde)** — na pastagem o preço tem o dobro da amplitude. Nenhum `*` aparece: nenhum canal isolado é significativo no conjunto (N pequeno). A figura serve para mostrar que a decomposição **não** separa os canais com poder — não para cravar qual domina.

![Distlag canais](../../outputs/drive_comum/distlag_canais.png)

---

## Decisões metodológicas

- **Base "preço recebido" (USD × câmbio), tudo IPEA OData4** — reprodutível e exógeno (ver acima). US$ ficam **nominais** (turning-points em 1as diferenças são robustos à inflação suave dos EUA; o REER carrega o ajuste real do lado Brasil).
- **Câmbio REAL EFETIVO (REER)** como medida primária de câmbio — contorna a troca de moedas pré-1994; janela completa 1980–2024 apesar do flag "inativo" da série.
- **Crédito = fluxo de GO (CREATE), em R$ de 2010** — re-deflacionado a dez/2024 pelo IPCA (deflacao_ipca.md). Faz a ponte com o SICOR municipal (2013+), que sozinho não cobre o boom.
- **D7 (primeiras diferenças)** + **HAC/Newey-West** (reuso #21) + **CCF/Granger** (reuso #34), com **teste reverso como placebo de exogeneidade**.
- **Decomposição de canais com regressores padronizados (z-score)** — sem isso, comparar o β bruto do preço (US$, DP grande) com o do câmbio (REER, DP ~3× menor) é inválido e inverte a leitura de amplitude.

## Limitações

- **N pequeno** (~38 anos) → baixo poder do Granger e do distributed-lag; os achados são **precedência preditiva**, não causalidade (mesma cautela do #34).
- **Multiplicidade não corrigida** → são ~135 testes no pipeline (Granger + Pearson + ponte) e ~7 com p < 0,05, **≈ o esperado por acaso** (~6,8); **nenhum sobrevive a Bonferroni/FDR**. Por isso os p-valores são **exploratórios** — o peso do fio cambial vem de **replicar em duas margens** (LULC pasto + rebanho Norte), não da contagem de hits. O desenho de painel AMC (interação driver × exposição) é a forma de recuperar poder.
- **Crédito é parcialmente endógeno** (política responde ao ciclo) — entra como **contexto/ponte**, não como driver exógeno puro; só os preços/câmbio são tratados como exógenos no placebo.
- **Decomposição de canais fraca no agregado UF** (R² baixo): separar preço de câmbio exigiria desagregação ou instrumentos. Mesmo padronizada, ela **não** sustenta que um canal domine o outro (ambos não-significativos).
- **Preços USD nominais** (sem deflator de CPI dos EUA) e **preço recebido em R$ válido só 1994+**.
- A **órfã 2018** (agricultura) **não** tem assinatura macro forte — consistente com #26 (quebra fraca) e com a leitura de que a freada da agricultura é **pós-2020** e local (#32/#35), não um choque macro de 2018.

## Como rodar

```bash
# 1) Coleta os drivers macro do IPEA (cacheia em data/raw/drivers_macro/)
python scripts/coleta_drivers_macro.py
python scripts/coleta_drivers_macro.py --force     # rebaixa da API mesmo com cache
python scripts/coleta_drivers_macro.py --offline   # só reprocessa o cache local

# 2) Roda a análise (alinhamento + lead-lag + distributed-lag + ponte regional)
python scripts/drive_comum.py
python scripts/drive_comum.py --sem-figuras         # pula a geração dos PNGs
```

A coleta precisa de internet na primeira vez (API IPEA Data); depois roda offline pelo cache. A análise depende de `taxas_lulc_goias.csv` (#17), `quebras_resultados.csv` (#26) e `deslocamento_series_regionais.csv` (#34) já gerados.

---

## Conexão com a narrativa

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| 1 | #32 | **Onde**? | Agricultura ancora no Sul; pasto/rebanho sobem ao Norte. |
| 2 | #33 | **Como**? | Sul: pasto→agric; Norte: veg→pasto. |
| 3 | #34 | **Sul causa Norte?** | Não — sem precedência nem spillover. Drive comum inferido. |
| **4** | **#37** | **Qual é o drive comum?** | **Assinatura de competitividade cambial: o câmbio antecede a retração do pasto (lag 2) e acompanha o rebanho do Norte (lags 0–1). Crédito é contexto endógeno; preço NÃO lidera. Precedência fraca (não sobrevive a multiplicidade) — testada no #38 (gradiente sugestivo no rebanho, não confirmado sob FDR).** |

O #37 **começa a fechar** a peça que o #34 deixou em aberto: a reorganização Sul→Norte carrega uma **assinatura de competitividade cambial** sobre o gradiente de aptidão — não um deslocamento inter-regional. É precedência preditiva **fraca**; o painel AMC (#38) a testa com mais poder e devolve um gradiente **sugestivo no rebanho** que **não** sobrevive à correção de multiplicidade — indício, não achado estabelecido.
