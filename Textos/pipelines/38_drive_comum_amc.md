# Pipeline #38 — O "drive comum" no painel AMC (driver × exposição)

**Script**: `scripts/drive_comum_amc.py`
**Quando foi feito**: 2026-06-06. Sequência direta do #37, que testou o drive comum na série UF/anual e esbarrou no **teto de N (~38 anos)**: os hits não sobreviviam a multiplicidade e só o câmbio tinha estrutura. Este pipeline **muda a unidade de análise** para recuperar poder.
**Depende de**: #37A (`drivers_macro_anual.csv`); #25 (`painel_amc_goias.parquet`, rebanho); `taxas_lulc_amc.csv` (deltas + shares por AMC). Reusa o padrão **PanelOLS 2FE** de `correlacoes_painel.py` (D8) e a convenção de 1as diferenças (D7).
**Outputs**:
- `data/processed/drive_amc_confirmatorio.csv` — 4 interações **confirmatórias teóricas** (lags 0/1).
- `data/processed/drive_amc_exploratorio.csv` — grade completa (144 modelos, lags 0/1/2) + **FDR-BH**.
- `outputs/drive_comum_amc/interacoes_confirmatorias.png` — forest plot das confirmatórias.
- `outputs/drive_comum_amc/grade_exploratoria.png` — heatmap de t-stat da grade (✚ = sobrevive FDR).

---

## Pergunta de pesquisa

O #37 mostrou que a série UF/anual não tem poder para testar o drive comum (N≈38, ~7 hits em ~135 testes ≈ acaso). O driver é **nacional** — num dado ano é o mesmo número para as 166 AMCs —, então não adianta perguntar "o driver mexe o LULC?" no agregado. A pergunta com poder é outra:

> O **mesmo** choque comum (câmbio, preço, crédito) bate **mais forte onde a exposição é maior**? Ou seja: existe o **gradiente de aptidão** que o #34/#37 *afirmam* mas a série agregada não consegue testar?

---

## A intuição (em linguagem simples)

O câmbio sobe igual para Goiás inteiro num ano. Então você não vê o efeito do câmbio comparando "Goiás contra Goiás" — você precisa comparar **lugares diferentes no mesmo ano**: quando o câmbio dispara, a AMC de **fronteira** (muita vegetação convertível, Norte) reage **mais** que a AMC já consolidada na agricultura (Sul)? Se sim, isso é a assinatura do drive comum **operando sobre o gradiente** — e é exatamente o que a série de um ponto só (o estado inteiro) é cega para enxergar.

O truque econométrico: o **efeito fixo de ano** "limpa" tudo que é comum àquele ano (inclusive o nível do câmbio); o **efeito fixo de AMC** limpa tudo que é fixo do lugar. O que sobra — e o que medimos — é a **interação**: o choque comum × a exposição do lugar. Como o choque varia só no tempo e a exposição só no espaço, o produto varia nos dois e é identificado limpo.

---

## Decisão de desenho

**Especificação (2-way FE):**

> Δy_it = α_i + γ_t + β·(Δdriver_t × exposição_i) + ε_it

- **α_i** (efeito fixo de AMC) absorve o efeito principal da exposição (que é fixa no tempo).
- **γ_t** (efeito fixo de ano) absorve **todo choque nacional** — inclusive o nível do driver.
- **β** (interação) é o **gradiente**: quanto mais forte o desfecho responde por unidade extra de exposição.

**Padronização**: driver em **1as diferenças** (D7) e **z-score sobre os anos**; exposição **baseline 1985–1989** (predeterminada → não contaminada pelo desfecho) e **z-score sobre as 166 AMCs**; desfechos também em **z-score** (β comparável entre classes). Assim **β = DP do desfecho por um choque conjunto de +1 DP no driver e +1 DP na exposição**.

**SE com clusterização dupla (entidade + ano)**: o driver é um **choque comum**, então os resíduos são correlacionados dentro do ano; clusterizar só por AMC subestima o erro. A vcov two-way não é garantidamente PSD — em **3 das 144 células** da grade ela deu variância negativa e o código **caiu para cluster por entidade** (marcado em `cluster`).

**Disciplina de multiplicidade (lição do #37)**:
- **Confirmatório teórico** — 4 interações selecionadas **por teoria** (com direção esperada), testadas nos lags 0/1. *Nota de honestidade:* foram escritas no mesmo dia da análise — é **seleção dirigida por teoria**, não pré-registro temporal; o crédito vem da hipótese estar declarada antes, não de precedência cronológica.
- **Exploratório** — grade completa (4 drivers × 3 exposições × 4 desfechos × **3 lags [0/1/2]** = 144), com **FDR-BH**. O lag 2 foi incluído porque o sinal do #37 (câmbio→pasto) estava no lag 2 — sem ele o "nulo de área" ficava por não ter testado o lag certo. Sem cherry-picking de lag.

**Exposições** (baseline, z-score): `exp_apt_agri` (% agricultura — aptidão/Sul), `exp_pasto` (% pastagem), `exp_fronteira` (% vegetação natural convertível — Norte). **Desfechos**: Δ veg. natural, Δ pastagem, Δ agricultura (área, Mha) e **Δ rebanho** (bovinos, do painel #25).

---

## Achados

**N efetivo**: 6.640 obs (166 AMCs × 40 anos) — contra os ~38 do #37. Mas atenção ao que esse N compra: o **driver** ainda varia só 40 vezes (uma por ano); quem dá poder à interação é a **exposição cross-section** (166 AMCs). O 6.640 é o N da *interação*, não 6.640 observações independentes do driver — e a clusterização por ano tem só ~40 clusters (no limite). Mais poder que o #37, sim; "poder resolvido", não.

### 1. A única confirmatória que vinga é câmbio × fronteira → **rebanho** — e isoladamente
| Hipótese confirmatória teórica (melhor lag) | β | p | Veredito |
|---|---|---|---|
| Câmbio × Fronteira → **Δ Rebanho** (lag 1) | **+0,028** | **0,031** | **✔ confirma direção** (CI 0,003–0,054) |
| Câmbio × Fronteira → Δ Pastagem (lag 0) | −0,011 | 0,76 | nulo |
| Preço soja × Aptidão agríc. → Δ Agricultura (lag 0) | −0,032 | 0,50 | nulo |
| Preço soja × Pasto → Δ Pastagem (lag 1) | +0,006 | 0,84 | nulo |

A **versão AMC da ponte do #37** (câmbio → rebanho do Norte) reaparece no sinal esperado: a depreciação faz o rebanho crescer **mais** nas AMCs de fronteira. Mas calibre o tamanho: é **1 de 8** testes confirmatórios (4 hipóteses × 2 lags) com p<0,05 — pouco acima do que o acaso entrega para um conjunto direcional. As outras três hipóteses (todas de **área** LULC) são nulas. É **indício coerente**, não confirmação robusta.

### 2. Sob a grade completa (lag 2 incluído), **nada** sobrevive ao FDR
Na grade de **144**, **8 têm p<0,05 brutos e 0 sobrevivem ao FDR-BH**. O que mudou em relação à primeira versão (grade de 96, sem lag 2): o antes-"sobrevivente" —
- **Câmbio × Aptidão agrícola → Δ Rebanho** (lag 0): β=−0,031, t=−3,52, p=0,0004 — passou de **p_fdr=0,042 ✚** para **p_fdr=0,063 ✗**.

Ele estava **na fronteira da correção**: com 96 testes o limiar de BH no posto 1 é 0,05/96 ≈ 0,00052; com 144 cai para 0,05/144 ≈ 0,00035 — e o p=0,00044 ficou exatamente **no meio**. Lição honesta: aquele "1 sobrevive ao FDR" era **frágil ao tamanho exato da família** — ampliar a grade (legitimamente, para testar o lag 2) o derruba. **A grade exploratória, corrigida, não entrega nenhum gradiente.**

### 3. A coluna do rebanho é coerente em sinal — mas **não** é replicação independente
Olhando **só o desfecho rebanho** (melhor lag por célula), o padrão de sinais parece consistente:

| Driver → Δ Rebanho | × Fronteira | × Aptidão agríc. | × Pasto |
|---|---|---|---|
| **Câmbio** | +0,028 (p .031) | −0,031 (p .0004) | −0,023 (p .067) |
| **Preço soja** | +0,030 (p .008) | −0,003 (ns) | −0,030 (p .004) |
| **Crédito GO** | +0,024 (p .070) | +0,000 (ns) | −0,028 (p .034) |

**Fronteira sempre +, pasto/aptidão sempre − (ou nulo).** Mas **não** chame isso de "replicar em construções independentes" — as células **não** são independentes, por duas razões mecânicas: (a) as três exposições são *shares* que somam ~constante, então `exp_fronteira ≈ −exp_apt_agri` — dado o + na fronteira, o − na aptidão é quase **forçado**; (b) `preço recebido = preço × câmbio` **contém** o câmbio, então as linhas "câmbio" e "preço soja" compartilham um fator. Um teste de sinais que pressupõe 9 sorteios independentes está **superestimando** a evidência. O que há é **um** gradiente (fronteira vs núcleo) visto de ângulos mecanicamente ligados — não uma malha coerente de três drivers.

### 4. Null honesto e agora **robusto**: a **área** LULC não tem gradiente macro
Nenhuma interação com desfecho de **área** (veg./pasto/agric. em Mha) sobrevive ao FDR; quase nenhuma passa nem do p<0,05 bruto — **inclusive no lag 2** (menor p de área = 0,052). Como o lag 2 era justamente onde o #37 achava sinal, testá-lo e não achar nada **fecha** o nulo de área em vez de deixá-lo em aberto. Os R²-within são minúsculos (0,0001–0,008) em toda a grade. Leitura: se há transmissão macro diferenciada por exposição, ela aparece no **rebanho** (estoque de ajuste rápido — lotação/intensificação), **não na conversão de área**. *Ressalva:* parte do contraste pode ser de **medição** — a PPM (rebanho) é série anual volátil; o MapBiomas (área) é suave, com menos variância ano-a-ano para a interação "pegar".

### 5. Síntese — gradiente **sugestivo** no rebanho, não estabelecido
> O que o #34/#37 **afirmavam** ("drive comum sobre o gradiente de aptidão") ganhou aqui um **teste com mais poder e correção de multiplicidade** — e a resposta honesta é mais sóbria do que a primeira versão deste pipeline sugeria. O **único** elemento com algum standing é a hipótese **confirmatória teórica** câmbio × fronteira → rebanho (β=+0,028, p=0,031, lag 1): sob depreciação, o rebanho cresce **mais na fronteira** (Norte) e **menos no núcleo agrícola** (Sul), coerente com #32/#33. **Mas**: (i) é 1 de 8 testes confirmatórios; (ii) a grade exploratória completa (144, com lag 2) **não devolve nenhum** sobrevivente do FDR — o "1 que sobrevivia" era artefato do tamanho da família; (iii) a "coerência de sinais" na coluna do rebanho é mecânica (exposições complementares + drivers que compartilham o câmbio), não replicação independente; (iv) R²-within ~0,001. Veredito: **indício de um gradiente câmbio × aptidão materializado na pecuária de fronteira — sugestivo e coerente com a narrativa, NÃO um achado estabelecido.** A área LULC, por sua vez, **não** responde diferencialmente (nulo robusto até o lag 2).

**Implicação para a redação**: o item 5 da tese sai de "assinatura cambial fraca no agregado (#37)" para **"indício de gradiente de aptidão no painel AMC: sob depreciação, o rebanho (não a área) tende a crescer mais na fronteira e menos no núcleo agrícola — direção coerente e confirmatória (p=0,031), mas que NÃO sobrevive à correção sobre a grade completa; a área LULC não responde"**. Não vender como "testado e confirmado": é **identificação de gradiente** (interação 2FE) de magnitude **modesta** (R² pequeno) e **significância frágil** (cai sob FDR da grade inteira).

---

## Como ler as figuras

### A. `interacoes_confirmatorias.png` — forest plot (manchete)
Cada linha é uma hipótese confirmatória teórica (melhor lag), com β e IC 95%. **Verde** = confirma direção e p<0,05; **roxo** = p<0,05 com sinal inesperado; **cinza** = não-significativo. Só `Câmbio × Fronteira → Δ Rebanho` está verde; as três de área estão cinza, cruzando o zero.

![Confirmatórias](../../outputs/drive_comum_amc/interacoes_confirmatorias.png)

### B. `grade_exploratoria.png` — heatmap de t-stat
Linhas = driver × exposição; colunas = desfecho; cor = t-stat da interação (azul − / vermelho +); **✚** marcaria sobrevivência ao FDR-BH — **ausente**: na grade completa (144, lags 0/1/2) nenhuma célula sobrevive. A coluna **Δ Rebanho** ainda concentra a cor (o gradiente é visível em sinal/t-stat), mas isso **não** passa pela correção de multiplicidade; as colunas de área são pálidas (sem gradiente).

![Grade exploratória](../../outputs/drive_comum_amc/grade_exploratoria.png)

---

## Decisões metodológicas

- **Interação driver × exposição com 2-way FE** (reuso de `correlacoes_painel.py`, D8): o γ_t absorve o choque comum, identificando o **gradiente** — não o nível médio (que fica para o #37, agregado). Os dois desenhos são **complementares**.
- **Exposição baseline 1985–1989, predeterminada** → exógena ao desfecho (não é o LULC corrente prevendo a si mesmo).
- **Tudo padronizado (z-score)** → β comparável entre classes e legível (sem isso, β de área sai 0,0000).
- **Clusterização dupla (entidade + ano)** como primária; fallback para entidade quando a vcov two-way é não-PSD (3/144 células da grade).
- **FDR-BH na grade exploratória** + **conjunto confirmatório teórico** — aplica a lição do #37 sobre multiplicidade. *Caveat:* o resultado do FDR é sensível ao tamanho da família (ver Achado #2) — ampliar a grade legitimamente (lag 2) derrubou o único sobrevivente.

## Limitações

- **R²-within minúsculos** (0,0001–0,008): o gradiente é **modesto** — a maior parte da variação AMC-ano é idiossincrática/local. O achado é, na melhor leitura, sobre **sinal/direção** do gradiente, não sobre variância explicada nem sobre magnitude econômica relevante.
- **Significância frágil à multiplicidade**: o único sobrevivente do FDR na grade de 96 **não sobrevive** na grade de 144 (lag 2 incluído) — estava na fronteira da correção. O standing empírico restante é a **hipótese confirmatória teórica** (1 de 8 testes, p=0,031), que não é correção-robusta.
- **A "coerência de sinais" (#3) não é replicação independente** — as três exposições são complementares (fronteira ≈ −aptidão) e `preço recebido` contém o câmbio. É **um** gradiente visto de ângulos ligados, não vários achados convergentes.
- **Identifica gradiente, não nível**: o γ_t absorve o efeito médio do driver. "1 DP de câmbio → X" no agregado **não** sai daqui (sai, fraco, do #37).
- **Crédito é parcialmente endógeno** (mesma ressalva do #37); entra como contexto.
- **Exposição em % de área baseline** é um proxy de aptidão, não aptidão edafoclimática direta. Um próximo passo seria usar aptidão agronômica (ex.: zoneamento) como exposição instrumental. **Viabilidade verificada (2026-07-18)**: o **MacroZAEE-GO** tem um **Mapa de Aptidão Agrícola das Terras** em shapefile, baixável no SIEG (`www2.sieg.go.gov.br/post/ver/185411/macrozaee`) — agregável às AMCs por zonal-stats. Detalhe e trade-offs em [backlog.md](../backlog.md) → "Frentes de expansão opcionais".

## Como rodar

```bash
python scripts/drive_comum_amc.py
python scripts/drive_comum_amc.py --sem-figuras
```

Depende de `drivers_macro_anual.csv` (#37A), `painel_amc_goias.parquet` (#25) e `taxas_lulc_amc.csv` já gerados.

---

## Conexão com a narrativa

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| 1 | #32 | **Onde?** | Agricultura ancora no Sul; pasto/rebanho sobem ao Norte. |
| 2 | #33 | **Como?** | Sul: pasto→agric; Norte: veg→pasto. |
| 3 | #34 | **Sul causa Norte?** | Não — drive comum inferido. |
| 4 | #37 | **Qual é o drive comum?** | Assinatura de competitividade cambial (UF/anual), **fraca** — N≈38 trava o poder. |
| **5** | **#38** | **O drive opera sobre o gradiente de aptidão?** | **Indício, não confirmação: a hipótese teórica câmbio × fronteira → REBANHO confirma a direção (p=0,031), mas a grade completa (lag 2) NÃO devolve nenhum sobrevivente do FDR. A área LULC não responde (nulo robusto). Gradiente sugestivo, magnitude modesta.** |

O #38 **avança** o arco aberto no #34 sem fechá-lo: a reorganização Sul→Norte é **consistente com** competitividade macro × gradiente de aptidão materializada na pecuária de fronteira — um **indício** testado no painel AMC (mais poder que o #37), porém de significância frágil à multiplicidade. É um passo da inferência para a evidência, não a prova. Um desenho de maior poder/identificação (aptidão edafoclimática como exposição instrumental; instrumentos para o câmbio) seria o próximo passo para sair de "sugestivo" para "estabelecido".
