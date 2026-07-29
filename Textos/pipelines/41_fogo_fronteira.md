# Pipeline #41 — O fogo lidera a marcha ao norte? (fogo como assinatura da fronteira)

**Script**: `scripts/fogo_lidera_fronteira.py`
**Status**: ✅ concluído (2026-06-07)
**Entradas**: `fogo_mapbiomas_goias.csv` (#14), `conversao_bruta_municipal.csv` (#19), crosswalk/geometria AMC (#25), `centro_massa_anual.csv` (#32, overlay).
**Saídas**: 7 CSVs (`data/processed/fogo_fronteira_*.csv`) + 6 PNGs (`outputs/fogo_fronteira/`).

## Pergunta de pesquisa

O Pipeline #14 (fogo) ficou **fora** da narrativa Sul→Norte (#32–#40). Este pipeline o traz
para dentro testando o **item 4 do backlog**: o **centroide do fogo lidera o centroide da
conversão veg→pasto** na marcha ao norte? O fogo é a **assinatura antecipatória** da fronteira?
A intuição vem da própria doc do #14 ("fogo no Cerrado precede ~70% das conversões"): se for
verdade, a geografia do fogo deve estar **à frente** (mais ao norte) e/ou **antes** (no tempo)
da geografia da conversão.

## A armadilha (e como o pipeline a navega)

Fogo em vegetação natural e a conversão veg→pasto são quase o **mesmo evento** — queimar o
Cerrado é, muitas vezes, o ato de abri-lo para pasto. Um "fogo lidera por ~1 ano" no centroide
seria então em parte **definicional**, não uma descoberta (no espírito das correções dos
#34/#37/#40). Duas coisas blindam a leitura:

1. **O fogo em veg natural é ~5–15× MAIOR que a conversão veg→pasto do mesmo ano** (ex.: 2010
   fogo_veg = 1,27 Mha vs conv = 0,083 Mha). A maior parte do fogo no Cerrado **não vira pasto**,
   e tem forte componente **climático** (1985/2010 = anos de seca). Logo o fogo é um sinal
   **mais amplo**, não o decalque da conversão.
2. **O teste local (Bloco 4) usa efeito fixo de ANO**, que absorve o choque climático comum, e
   **separa** o fogo-que-abre-fronteira (fogo em veg → conversão) do fogo-de-manejo (conversão →
   fogo em pasto), em direções opostas e com **tipos de fogo distintos**.

## Decisão metodológica nova — D15: alinhamento temporal fogo × conversão

A conversão é rotulada por `ano_origem = t` (veg em t, pasto em t+1); o evento de abertura
(fogo) ocorre na estação seca de t. Logo **fogo(ano=t) ↔ conv(origem=t)** é o alinhamento
**contemporâneo** (k=0, mecânico/esperado). "Fogo lidera" = fogo(t) prevê conv(origem=t+1, t+2),
i.e. **k≥1 sobreviver é o sinal genuíno**. Centroides e painel sobre as **166 AMCs** (#25,
EPSG:5880), reusando a maquinaria do #32 (D11: AMC neutraliza o artefato de emancipação).

## Os blocos

| Bloco | O que faz | Reusa |
|---|---|---|
| 1. Centroides | mean+median ponderados de fogo_veg, fogo_total, fogo_pasto, conv_vp por ano | `mean_center`/`median_center` (#32) |
| 2. Deslocamento + offset | ΔN/ΔL (km) por ato + offset espacial anual lat(fogo_veg)−lat(conv) | tabela de deslocamento (#32) |
| 3. Lead-lag agregado | CCF + Granger nas 1as diferenças das latitudes (fogo→conv, + reverso) | `ccf_defasada`/`granger` (#34) |
| 4. Painel local | conv(t) ~ fogo_veg(t−2..t+2) em 2-way FE + contra-prova de manejo | `PanelOLS` (#22/#38) |
| 5. Robustez | re-roda o perfil sob 5 specs (cluster duplo, log1p, sem seca, 2001+) | padrão #35/#36/#38 |
| 6. Teste focal 2001–05 | o pulso de perda de veg do #29 foi de fogo? (tempo × espaço × composição) | fecha micro-mistério #29 |

## Achados

### Veredito de uma linha

**Sim como vanguarda ESPACIAL; NÃO no tempo; não como "corrida" ao norte.** O fogo é o sinal
mais ao norte (robusto), mas **não lidera a conversão no tempo** de forma estabelecida: no
agregado o Granger é nulo e, no local, a co-elevação fogo↔conversão dentro da AMC é **robusta**
enquanto a **assimetria de liderança (passado>futuro) é FRÁGIL** — significativa só na
especificação base, some sob `log1p` e **inverte** ao excluir os anos de seca. Na marcha
(deslocamento) a conversão ainda **avança mais** que o fogo.

### 1. Espacial — o fogo é a vanguarda ao norte (robusto)

O centroide do fogo em veg natural está **ao norte da conversão veg→pasto em 100% dos anos**
(39/39), por **+73 km em média**. O gap era maior no início (~115–160 km nos anos 1980) e
**encolheu** para ~20–75 km (a conversão *alcançando* a latitude do fogo). Mais: o fogo-veg
está ao norte **do próprio estoque de Cerrado** (#32) e cada vez mais (1985: +35 km; 2023:
+114 km) — então **não** é só "fogo segue onde o Cerrado está"; concentra-se na porção
**norte/ativa**.

> **Ressalva honesta**: parte dessa concentração nortenha do fogo é **tipo de vegetação** — a
> savana/campo do Norte é mais inflamável que os fragmentos florestais e a mata ciliar do Sul
> (depleção 1985→2024: savana −38%, campo −43% vs floresta −23%, #39). A comparação **limpa** é
> fogo vs **conversão** (ambos fluxos de distúrbio do Cerrado), e aí o +73 km é robusto.

### 2. Temporal agregado — nulo (esperado)

CCF e Granger nas 1as diferenças das latitudes dos centroides **não** acham precedência: pico de
CCF em lag −4 (r≈−0,30, ruído), Granger fogo→conv p=0,67/0,81. A marcha ao norte é uma
**tendência lenta**; os saltos N–S ano-a-ano não lideram-defasam. **Coerente com o #34**
(co-movimento sob drive comum, sem precedência temporal no agregado).

### 3. Local (AMC, 2-way FE) — co-elevação robusta, liderança temporal FRÁGIL

Perfil de `conv(t) ~ fogo_veg(t−2..t+2)`, com **ano FE absorvendo o clima comum** e AMC FE a
propensão local (β em z-score, p clusterizado por AMC) — **especificação base**:

| defasagem | β | p | leitura |
|---|---|---|---|
| fogo t−2 (lidera) | +0,081 | 0,011 * | |
| **fogo t−1 (lidera)** | **+0,123** | **0,002** * | pico (base) |
| fogo t (contemp.) | +0,103 | 0,016 * | co-elevação |
| fogo t+1 (placebo/futuro) | +0,081 | 0,046 * | |
| fogo t+2 (placebo/futuro) | +0,086 | 0,133 | |

Na base, soma **passado +0,204 > futuro +0,167** (pico em t−1) sugeriria que o fogo lidera ~1
ano. **Mas a verificação de robustez derruba a liderança** (ver Bloco 5 abaixo): o fogo *futuro*
também prevê a conversão (t+1 significativo), e a assimetria passado>futuro **não sobrevive**. O
que é **robusto** é a **co-elevação** fogo↔conversão dentro da AMC (o termo contemporâneo t0 é
significativo em 4/5 especificações) — uma **janela de ~5 anos** em que fogo e conversão sobem
**juntos** (o "episódio de fronteira"), **sem** liderança temporal estabelecida.

### 3b. Robustez da liderança local (o que rebaixa o item 3)

O perfil base foi re-rodado sob 5 especificações, comparando Σβ do **passado** (lidera) vs
**futuro** (placebo) e a significância do lead em t−1:

| spec | Σpassado | Σfuturo | t−1 p | leitura |
|---|---|---|---|---|
| base (z, cluster entidade) | +0,204 | +0,167 | 0,002 | lead sig |
| cluster duplo (entidade+ano) | +0,204 | +0,167 | 0,006 | lead sig (mesma amostra) |
| **log1p** (doma cauda/zero-infl.) | +0,041 | +0,029 | **0,091** | t−1 **n.s.** |
| **sem seca** (exclui 1985, 2010) | +0,179 | +0,262 | 0,013 | **futuro > passado (INVERTE)** |
| só 2001–2023 | +0,149 | −0,118 | 0,127 | t−1 **n.s.** |

**Direção** passado>futuro em 4/5, **mas o lead t−1 significativo só em 2/5 (a mesma amostra)**;
ele **colapsa sob `log1p`** (era puxado pela cauda pesada do fluxo de conversão) e **inverte ao
remover os dois anos extremos de fogo climático** (1985/2010). O contemporâneo (t0) é significativo
em 4/5 → **a co-elevação é robusta; a liderança temporal não é estabelecida**. Esta é a correção
da primeira leitura (que anunciou "fogo lidera ~1 ano" como achado).

### 4. Contra-prova de manejo — direção oposta, fogo distinto

`fogo_pasto(t) ~ conv(0, t−1, t−2)`: contemporâneo e t−1 nulos/negativos, **t−2 β=+0,51
(p=0,065, marginal)** — sugere que ~2 anos **após** a conversão a pastagem nova passa a ser
**queimada para manejo** (fogo em *pasto*, não em veg). Direção oposta à do Bloco 3 e com tipo
de fogo distinto: separa o fogo-de-abertura (veg → conversão) do fogo-de-manutenção (conversão →
pasto), reforçando que o sinal do Bloco 3 não é artefato.

## Deslocamento líquido 1985→2023 (Bloco 2)

| fluxo | ΔN (km) | ΔL (km) | azimute |
|---|---|---|---|
| Conversão veg→pasto | +126,6 | +128,7 | 45,5° (NE) |
| Fogo em pastagem | +165,6 | +124,1 | 36,9° |
| Fogo em veg natural | +85,8 | +55,0 | 32,7° |
| Fogo total | +68,8 | +47,5 | 34,6° |

A conversão **marchou mais** ao norte (+127 km) que o fogo-veg (+86 km) — porque partiu mais ao
sul e está alcançando o fogo. Por isso "o fogo **lidera a marcha**" no sentido literal de
*corrida ao norte* **não** se sustenta: o fogo é a **posição** avançada, não a maior **velocidade**.

## Teste focal (Bloco 6) — a sub-fase 2001–05 do #29 foi um pulso de FOGO?

O #29 deixou uma sub-fase **2001–05** com perda de veg natural ~3–5× mais intensa que 2006–19
(p=0,0008) que não virou período — um "micro-mistério". Como o #41 instrumenta fogo × perda de
veg, dá para perguntar: **esse pulso de desmatamento foi de fogo-de-abertura?**

| janela | fogo em veg (Mha/a) | declínio do estoque de veg (Mha/a) | veg→agric (% da perda) |
|---|---|---|---|
| 1985–2000 | 0,75 | +0,264 | 3,2% |
| **2001–2005** | **0,52** | **+0,133** | **6,1%** |
| 2006–2019 | 0,48 | +0,042 | 4,3% |
| razão 01-05 / 06-19 | **1,09×** | **3,2×** | — |

**Resposta: NÃO.** O discriminante é o **tempo**: na virada 2005→2006 a perda de veg caiu ~40–70%
(declínio do estoque 3,2× menor) mas o **fogo em veg quase não mudou (1,09×)** — *a desaceleração
do desmatamento não foi uma desaceleração de fogo*. O acoplamento **espacial** fogo×perda é alto
em **todas** as janelas (Spearman ~0,85–0,87, inclusive 2001–05), mas isso é a **co-localização
estrutural** "ambos no Cerrado de fronteira" do Bloco 1/3, **não** prova de que o fogo dirigiu a
aceleração. E a **composição** entrega o mecanismo: a fatia de conversão **direta** veg→agric
**dobra** em 2001–05 (3,2%→6,1%) = onset da **soja mecanizada** (clareira sem fogo). **Leitura**:
o pulso 2001–05 foi **demanda/mecanização** (boom da soja, câmbio/crédito do #37), **não** fogo —
fechando o micro-mistério do #29 de forma coerente com o veredito do #41 (fogo co-localiza, não
dirige) e do #37 (drive de demanda).

## Conexão com a tese

Traz o #14 (fogo) para dentro da narrativa Sul→Norte como **quinta perna descritiva**: o fogo é
a **vanguarda espacial** da fronteira (sempre ao norte da conversão, ao norte do estoque de
Cerrado), e dentro de cada AMC **co-evolui** com a conversão num episódio de fronteira de ~5
anos — **sem** liderança temporal estabelecida (a assimetria passado>futuro é frágil, e o Granger
agregado é nulo). Espelha o veredito geral do projeto (#34/#37/#38): **reorganização/co-evolução
sob distúrbio comum**, com o fogo na **dianteira geográfica** (não temporal), não uma cadeia
causal de mão única.

## Honestidade / limites

- Fogo-veg ≈ ignição da abertura → **k=0 é parcialmente definicional** (tratado isolando k≥1).
- A concentração nortenha do fogo é **em parte flamabilidade por tipo de vegetação** (savana
  nortenha), não só atividade de fronteira — por isso a âncora espacial é fogo vs conversão.
- **A liderança temporal local NÃO é robusta** (Bloco 3b): o placebo (fogo futuro) não é nulo, a
  assimetria some sob `log1p` e inverte sem os anos de seca. **Reportar como co-elevação, não
  como "fogo lidera/causa conversão".** (Correção de overclaim, no espírito da D14.)
- Granger agregado tem N pequeno (38 anos) → baixo poder; lido junto ao painel, não isolado.
- Conversão = **perda líquida** veg→pasto (#19), ignora rebrota; fogo = área queimada anual
  (#14; o nível está **validado** no #14B — dispersão ±0,04% entre 3 coleções e 2 recortes. A
  antiga leitura "~30% abaixo do Fire Dashboard por sub-amostragem `scale=30`" foi **refutada**:
  30 m é a resolução **nativa** do asset, não sub-amostra).

## Saídas

**CSVs** (`data/processed/`): `fogo_fronteira_centroides.csv` (156 linhas), `..._deslocamento.csv`
(16), `..._offset.csv` (39 anos), `..._leadlag.csv` (6), `..._painel.csv` (8),
`..._robustez.csv` (5 specs), `..._pulso2001.csv` (4 janelas).
**PNGs** (`outputs/fogo_fronteira/`): `latitude_trajetorias.png` (manchete N–S),
`offset_espacial.png` (fogo ao norte da conversão, 39/39), `mapa_trajetorias.png` (trajetórias
dos centroides), `leadlag.png` (CCF agregado + perfil distributed-lag local),
`robustez_leadlag.png` (fragilidade da liderança: passado vs futuro por especificação),
`pulso_2001_05.png` (teste focal: perda sobe, fogo não; veg→agric dobra).

## Como rodar

```bash
python scripts/fogo_lidera_fronteira.py            # CSVs + 6 PNGs
python scripts/fogo_lidera_fronteira.py --sem-figuras
```
