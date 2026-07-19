# Pipeline #54 — Endurecimento shift-share do drive comum (o positivo da Perna 3)

> **Nota de estrutura (jul/2026).** Este pipeline nasceu para endurecer o que a narrativa então
> chamava de **"perna 4"** (o drive comum). O próprio resultado do #54 motivou a **fusão** dessa
> perna com a antiga perna 3: o drive comum passou a ser o **positivo da Perna 3**
> (*"reorganização coordenada, não deslocamento causal"*) e o teto de oferta virou a **Perna 4**.
> Onde este doc diz "perna 4"/"drive comum", leia **o positivo da Perna 3**. O nome do arquivo
> (`54_defensabilidade_perna4.md`) é mantido como handle. Ver
> [`../indice_logico_pipelines.md`](../indice_logico_pipelines.md).

**Script**: `scripts/defensabilidade_perna4.py`.
**Quando foi feito**: 2026-07-18. Realiza a **opção (B)** decidida com o usuário: *maximizar a
defensabilidade do drive comum sem dado novo* — nomear o desenho pelo que ele é (um **shift-share/
Bartik**: "shift" = câmbio nacional, "share" = aptidão local) e rodar a **inferência correta**
para esse desenho, mais a bateria de especificidade que uma banca julga.
**Depende de**: #38 (`drive_comum_amc.py`, importado — monta exposições/interações/z-scores e
fornece `rodar_interacao`), #52 (`aptidao_edafo_amc.csv`, exposição exógena), #17/AMC
(`taxas_lulc_amc.csv`, placebos urbano/água).
**Outputs**:
- `data/processed/perna4_permutacao.csv` — β real + p de permutação (naive e circular) por headline.
- `data/processed/perna4_placebos.csv` — placebos de desfecho (urbano/água) + placebo-no-tempo (lead).
- `data/processed/perna4_jackknife.csv` — β dropando cada ano (leave-one-year-out).
- `outputs/defensabilidade_perna4/bateria.png` — 3 painéis (permutação, especificidade, jackknife).

---

## Por que este pipeline existe

O drive comum (choque comum câmbio × gradiente de aptidão → rebanho de fronteira) é a metade mais
fraca da narrativa. O #38/#52 já haviam diagnosticado que o teto é **estrutural**: o driver (câmbio) é uma
série **nacional** — varia só no tempo, ~38 realizações — então o poder é capado e **nenhuma
quantidade de AMCs a mais o levanta** (o cluster por ano já reconhece isso). Não dá para
"estabelecer" o drive comum espremendo mais do mesmo dado (o #52 confirmou: uma exposição melhor limpa
a *identificação*, não fabrica *poder*).

O que **dá** para fazer é o que este pipeline faz: parar de confiar no erro-padrão *clusterizado*
(que, para um shift-share de um único shifter, é **otimista** — resultado conhecido de
Adão-Kolesár-Morales 2019 e Borusyak-Hull-Jaravel 2022) e rodar a inferência **desenhada para esse
caso**, mais os placebos que separam "achado real" de "artefato".

## Os dois headlines endurecidos (o mesmo achado, dois ângulos; lag 1)

| Rótulo | Interação | Esperado | β (baseline) | p clusterizado |
|---|---|---|---|---|
| **H1** proxy de área (#38) | câmbio × fronteira (% veg baseline) → Δ rebanho | + | +0,0285 | 0,031 |
| **H2** aptidão exógena (#52) | câmbio × aptidão física exógena → Δ rebanho | − | −0,0325 | 0,026 |

H2 é o headline mais defensável (share físico **exógeno**, não-complementar). A bateria roda nos dois.
O `β` *within* que a permutação usa **reproduz o PanelOLS ao 4º decimal** (checagem no console) — a
maquinaria rápida é o mesmo estimador, só sem o erro-padrão.

## Método — a bateria (4 blocos)

1. **Inferência por permutação do shifter** (BHJ). Reembaralha a série anual do **câmbio** entre os
   anos, **mantém as shares (aptidão) fixas**, recomputa a interação e o β, B vezes → distribuição
   nula. p = fração de |β_nulo| ≥ |β_real|. Não depende da assintótica frágil de ~38 clusters.
   - **naive**: permutação livre dos anos (quebra a autocorrelação do câmbio → tende a *otimista*).
   - **circular**: rotação da série sobre as T−1 posições (exaustivo; **preserva a autocorrelação**
     do shifter macro) → é a versão **defensável** para uma série serialmente correlacionada.
2. **Placebos de desfecho**: câmbio × aptidão → **área urbana** e → **água**. Devem ser **nulos** —
   o efeito é específico do rebanho, não deriva genérica. (Urbano é o placebo limpo do #44.)
3. **Placebo-no-tempo (lead)**: câmbio_(t+1) e câmbio_(t+2) × aptidão → rebanho_t. Um choque
   **futuro** não pode explicar a variação presente → deve ser **nulo**. Contraste com o lag 1.
4. **Jackknife ano-a-ano** (leave-one-year-out): reestima o β dropando cada ano. Revela se a
   identificação repousa em uma grande desvalorização isolada (1999/2000/2015/2021). É a versão
   **honesta** do "event-study nas desvalorizações": com ~3 eventos grandes, um event-study dinâmico
   seria subdimensionado; o jackknife anotado pelo tamanho do choque entrega a mesma leitura.

---

## Achados

### O resultado central: o p clusterizado era OTIMISTA

A inferência desenhada para o shift-share **desloca o p para bem acima de 0,05**:

| Headline | β | p clusterizado (#38/#52) | p permutação **naive** | p permutação **circular** |
|---|---|---|---|---|
| H1 (proxy) | +0,0285 | 0,031 | 0,062 | **0,158** |
| H2 (exógena) | −0,0325 | 0,026 | 0,069 | **0,132** |

Lido em linguagem simples: quando se respeita que há só **~38 choques** vindos de **um** driver
nacional — e que esses choques são **serialmente correlacionados** (o câmbio de um ano parece o do
seguinte) —, a chance de ver um gradiente **deste tamanho por acaso** é de ~7% (permutação livre) a
~13% (rotação, que preserva a autocorrelação). **Não é significante a 5%.** O erro-padrão
clusterizado dava p≈0,03 porque **subestima** a incerteza quando o shifter é uma série agregada —
exatamente a advertência de AKM/BHJ, aqui **medida**, não citada.

> **O que o método NÃO diz.** A permutação **não** prova que o efeito é zero — β=−0,033 é o mesmo,
> o sinal é o esperado, e a distribuição nula está centrada em zero com o β real na cauda (~87º
> percentil). Ela diz que, com o número de choques que existe, **não dá para distinguir esse
> gradiente do acaso ao nível convencional**. É "não estabelecido", não "refutado".

### O que SOBREVIVE: direção, especificidade e robustez

O mesmo dado que não sustenta a significância sustenta que o **padrão é real e específico**, não ruído:

- **Placebos de desfecho — nulos** (o efeito é do rebanho, não deriva genérica):
  câmbio × aptidão → área urbana **p=0,34** (H2) / 0,52 (H1); → água **p=0,33** (H2) / 0,24 (H1).
- **Placebo-no-tempo — o headline exógeno passa limpo**: câmbio_(t+1) → rebanho **p=0,105** e
  câmbio_(t+2) **p=0,772** para H2. (Ressalva honesta: para **H1** o lead fica **borderline**,
  p≈0,06–0,07 — o câmbio serialmente correlacionado faz o "futuro" tocar o presente; é **mais uma**
  razão para o headline ser o **H2 exógeno**, cujo lead é limpo.)
- **Jackknife — nenhum ano isolado carrega**: dropando cada ano, o β de H2 fica na faixa estreita
  [−0,040; −0,027] (cheio −0,033), **sinal estável em 100%** dos drops, e as grandes desvalorizações
  (2000/2021/1990) **não** são os anos mais influentes. Não é artefato de um evento.

Os três blocos contam **a mesma história**: a autocorrelação do câmbio é o que inflava o p
clusterizado (o lead borderline de H1 e a rotação circular apontam para o mesmo mecanismo); tirado
esse verniz, a **significância evapora**, mas o **padrão** (sinal, especificidade ao rebanho,
robustez a dropar qualquer ano) **fica de pé**.

---

## Veredito

O #54 **não blinda** o drive comum — ele o **calibra honestamente**, e o efeito líquido é **mais
defensabilidade com menos significância aparente**:

- A significância do achado-manchete foi **revista para baixo**: de "p≈0,03, sugestivo" (leitura
  clusterizada do #38/#52) para **"não significante a 5% sob a inferência correta (p≈0,07–0,13)"**.
  O drive comum é um **padrão corroborante e honestamente delimitado**, não uma alegação causal isolada
  com standing estatístico.
- Em troca, ganha a **camada que a banca cobra**: o desenho vira um shift-share **nomeado**, com
  **inferência desenhada para o caso** (permutação), e uma **bateria de especificidade** que mostra
  que o padrão é do rebanho (placebos nulos), não antecipatório (lead limpo em H2) e não refém de um
  evento (jackknife). Isso converte o drive comum de *"uma regressão com p=0,03"* em *"um shift-share com
  inferência correta e placebos"* — que é o que se julga.

O **teto de poder temporal** permanece intacto e agora **quantificado**: N efetivo = **38 anos**, um
único shifter. Sair de "sugestivo" para "estabelecido" exige a **opção (A)** — um shifter com
variação espaço-temporal (frete/ferrovia, choque climático) ou um IV para o câmbio —, que é **fio
novo com dado novo**, não refinamento deste.

## Adenda (2026-07-19) — o teto é irresolvível? E isso compromete o quê?

Duas perguntas surgiram ao revisitar o veredito: *mesmo o choque climático (opção A) não traria a
resposta sobre o câmbio?* e *isso é uma fragilidade impossível de resolver?* A resposta é **sim às
duas** — e registrar o porquê evita reabrir este fio.

### 1. A opção (A) responde uma pergunta vizinha, não esta

Um shifter com variação espaço-temporal (clima/SPI município×ano, frete, ferrovia) testaria, com
poder real (milhares de realizações), a pergunta **"o gradiente de aptidão medeia choques
exógenos?"** — o *mecanismo*. Mas o câmbio não estaria no desenho: a pergunta **"foi o câmbio que
operou sobre esse gradiente?"** continuaria exatamente onde está. Por isso o backlog diz "abre
frente, não fecha o drive comum": a opção (A) pode estabelecer o **canal**, nunca a **peça cambial
específica**.

### 2. A fragilidade cambial é estrutural — todas as rotas de fuga falham

O limite não é de método, é de informação: a natureza rodou o experimento ~38 vezes. Enumerando:

| Rota de fuga | Por que não levanta o teto |
|---|---|
| Mais AMCs | O cluster por ano já reconhece que as 166 compartilham o mesmo choque; N efetivo segue ~38 |
| Mais drivers anuais | Zero realizações temporais novas — e reabre a multiplicidade do #37 |
| Frequência maior (câmbio mensal) | O desfecho trava: PPM e MapBiomas são **anuais** |
| IV para o câmbio (DXY, juros externos) | Resolve *exogeneidade*, não *poder* — o instrumento também só varia ~38× (e IV custa poder) |
| Esperar mais anos | T cresce 1/ano; sair de p≈0,10 para <0,05 levaria décadas |

**Conclusão dura**: a alegação "o câmbio, especificamente, causou o gradiente" **não vai cruzar a
significância convencional com dado existente**. Isso não é defeito do trabalho — é o limite de
AKM/BHJ para *qualquer* regressão de desfecho local em série macro nacional. A maioria da literatura
nem o reconhece; aqui ele foi **medido**.

### 3. O que isso NÃO compromete — três caminhos de standing sem significância

- **Triangulação de mecanismo** (se a opção A um dia for feita): se outro choque, com poder, mostrar
  o gradiente operando, a leitura da Perna 3 — "reorganização coordenada por forças comuns sobre o
  gradiente" — ganha standing como afirmação geral, mesmo com a peça cambial permanecendo em
  "corroborante". É a mesma lógica da periodização: nenhuma régua fecha sozinha; a convergência fecha.
- **Fardo dividido com a literatura**: o elo câmbio→expansão agropecuária no Brasil tem literatura
  própria em nível nacional (ex.: Richards e coautores, anos 2010 — conferir as referências exatas na
  redação). A dissertação não precisa reestabelecer que o câmbio importa; a contribuição própria é a
  **incidência diferencial no gradiente goiano** — o *nível* vem de fora, o *gradiente* é corroborado
  aqui.
- **Leitura correta da bateria deste pipeline**: direção esperada + placebos nulos + lead limpo +
  jackknife estável é o que distingue "subpotenciado mas provavelmente real" de "ruído". A evidência
  move a crença mesmo sem cruzar 5% — desde que o texto não a chame de estabelecida (e não chama).

### Veredito de escopo

**O trabalho não fica incompleto sem a opção (A).** Ela é expansão opcional — outra pergunta, outro
dado —, não pendência de completude. O único requisito de completude que este fio impõe é
**textual**: nenhuma frase-manchete pode vender o câmbio como causa estabelecida da fronteira, nem
citar p=0,026/0,031 como significância — o número reportável é o p de permutação (D20).

## Limitações

- A **rotação circular** tem só T−1 ≈ 37 permutações distintas → o p_circular tem granularidade
  ~0,027 (é exato, mas coarse); reporta-se junto com o naive (5.000) para bracketar.
- A permutação testa o **shifter** (câmbio) como as-good-as-random dado o desenho; **não** resolve
  uma eventual **tendência diferencial** das AMCs aptas (isso seria o event-study/pré-tendência da
  opção A). O lead limpo de H2 é evidência *contra* antecipação, não prova de ausência de trend.
- Herda os limites do #38/#52: identifica **gradiente** (não nível); exposição **time-invariant**;
  crédito parcialmente endógeno; 3 fallbacks de vcov não-PSD no baseline (comportamento conhecido).
- O **within 2-way rápido** (usado na permutação) é validado contra o PanelOLS no β; o erro-padrão
  clusterizado continua vindo do PanelOLS (a permutação **substitui** o p, não o SE).

## Como rodar

```bash
py -3.14 scripts/defensabilidade_perna4.py                 # bateria completa (nperm=5000) + figura
py -3.14 scripts/defensabilidade_perna4.py --sem-figuras
py -3.14 scripts/defensabilidade_perna4.py --nperm 2000    # permutação naive mais rápida
```

---

## Conexão com a narrativa

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| 5 | #38 | O drive comum opera sobre o gradiente (proxy de área)? | Sugestivo (p clusterizado 0,031); nada no FDR de 144. |
| 5 | #52 | E com aptidão **exógena**? | Confirma direção sem a complementaridade (p clusterizado 0,026); beira o FDR. |
| **5** | **#54** | **E sob a inferência CORRETA para o shift-share?** | **O p clusterizado era otimista: permutação dá p≈0,07–0,13 (não significante a 5%). Mas o padrão é específico (placebos nulos), não antecipatório (lead limpo em H2) e não refém de um ano (jackknife). Mais defensável, menos significante — "corroborante, não estabelecido".** |

O #54 fecha a opção (B): o drive comum sai **mais honesto e mais defensável**, com o número de incerteza
**certo** e a especificidade **demonstrada** — sem inflar. O caminho para "estabelecido" é a opção
(A), fora do escopo deste pipeline.
