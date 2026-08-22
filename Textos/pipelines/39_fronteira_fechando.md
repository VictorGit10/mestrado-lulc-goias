# Pipeline #39 — A fronteira está fechando? (frontier closure / oferta de Cerrado)

**Script**: `scripts/fronteira_fechando.py`
**Status**: ✅ concluído (2026-06-07)
**Entradas**: `painel_amc_goias.parquet` (#25), `drivers_macro_anual.csv` (#37), geometria/crosswalk AMC.
**Saídas**: 4 CSVs (`data/processed/fronteira_*.csv`) + 4 PNGs (`outputs/fronteira_fechando/`).

## Pergunta de pesquisa

A narrativa Sul→Norte (#32–#38) explicou a desaceleração recente da fronteira agropecuária
sobretudo pela **demanda** (drive comum câmbio/crédito/commodities, #37/#38) sobre um gradiente
de aptidão. Falta testar a alternativa pela **oferta**: a desaceleração recente (agricultura
quase parada no Ato III, #32/#33) seria o **estoque de Cerrado convertível se esgotando** — a
fronteira *fechando*? O sinal de partida vem do #32: tudo marchou ao norte (+65 a +78 km)
**menos a vegetação natural (+8 km, ancorada)**, coerente com uma fronteira que recua ao norte
à medida que o estoque ao sul se exaure. É **reinterpretação**, não mais um cruzamento.

## Decisão metodológica nova — D13: o que é "terra convertível"

Sem CAR/UC/PRODES integrados (coletas pendentes), "convertível" é **proxy com teto declarado**,
reportado em 3 definições lado a lado:

| Definição | Classes (painel #25) | Uso |
|---|---|---|
| **ampla** | floresta nativa + formação savânica + campo nativo | consistente com #32/#25 |
| **refinada** (primária) | **formação savânica + campo nativo** | convertível de fato (exclui floresta) |
| **refinada_rl** | refinada − 20% da área de estabelecimentos (Censo 2017) | sensibilidade Reserva Legal |

> **Premissa da `refinada_rl`, declarada em ago/2026.** O piso de 20% é aplicado uniformemente a
> Goiás. Não é bem o que a lei diz: o Código Florestal (art. 3º, I) inclui na Amazônia Legal as
> regiões **ao norte do paralelo 13º S de Tocantins e Goiás**, onde o cerrado responde por **35%**
> (art. 12, I, b) — regra repetida pela Lei estadual 18.104/2013, art. 25. Medida na malha, essa
> faixa é de **0,27 Mha (0,8% do estado)**, em cinco municípios do extremo norte. Usar 35% ali em
> vez de 20% mudaria o estoque convertível em ~0,04 Mha, contra ~6,6 Mha remanescentes — cerca de
> 0,6%, dentro do ruído, e numa definição que já é de sensibilidade e não a primária. A premissa
> fica registrada, não corrigida.

**Justificativa empírica da refinada** (rodada dentro do pipeline, depleção 1985→2024 por classe):

| Classe | 1985 → 2024 (Mha) | % perdido |
|---|---|---|
| Formação savânica | 9,90 → 6,11 | **38,2%** |
| Campo nativo | 0,77 → 0,45 | **42,5%** |
| Floresta nativa | 6,28 → 4,85 | 22,8% |
| Campo alagado *(não usado)* | 0,70 → 0,48 | 31,8% |

Savana e campo nativo são as classes **ativamente convertidas**; a floresta nativa (mata
ciliar/APP, mais protegida) encolhe bem menos → fica fora da definição preferida.

**Limite honesto**: é um **teto** — inclui RL/APP/UC não-subtraídos. O cenário RL (20%) é cru.
PRODES Cerrado, TerraClass e CAR refinariam, mas não são necessários para o teste de 1ª ordem.

## Abordagem (3 blocos)

- **A. Estoque convertível por região e no tempo** (descritivo) — estoque/depleção por AMC×ano
  nas 3 definições; agregação por mesorregião e **faixa de latitude** (centroide EPSG:5880).
- **B. Teste de oferta** — fluxo de perda anual `= max(0, estoque_{t−1} − estoque_t)`;
  **hazard** `= fluxo / estoque_{t−1}`; **painel 2-way FE** (ano FE absorve o choque comum de
  demanda → o coeficiente do estoque isola o gradiente de oferta cross-AMC, lógica do #38);
  resíduo controlado por demanda (drivers #37). Padrão PanelOLS + cluster duplo (D8).
- **C. Decomposição da desaceleração Ato II→III** — `Δfluxo = h̄·Δestoque + estoquē·Δhazard`
  (decomposição exata de produto pelo ponto médio): efeito-**OFERTA** vs efeito-**DEMANDA** por
  região; cruzamento com os níveis de demanda (#37) por ato.

## Achados

### 1. O estoque convertível recuou ao norte, mas não se esgotou no estado

Cerrado convertível (refinada) restante por mesorregião (Mha | % de 1985):

| Mesorregião | 1985 | 2000 | 2019 | 2024 |
|---|---|---|---|---|
| **Sul** | 2,24 (100%) | 1,47 (66%) | 1,23 (55%) | **1,19 (53%)** |
| Centro | 3,98 (100%) | 3,08 (77%) | 2,63 (66%) | 2,49 (63%) |
| **Norte** | 4,46 (100%) | 3,55 (80%) | 3,04 (68%) | **2,89 (65%)** |

O **Sul** começou com o **menor** estoque absoluto, depletou o **mais** (53%) e **estabilizou
após ~2019** (1,23→1,19) — assinatura de estoque que rareou. A faixa de **latitude mais ao norte
concentra 4,05 de ~6,56 Mha (≈62%)** do convertível remanescente: a fronteira de oferta está, de
fato, ao norte.

### 2. A conversão escala com o estoque disponível, e isso sobrevive à demanda

Painel 2-way FE (z-score; N≈6.400; cluster entidade+ano):

> ⚠ **Correção de 21/ago/2026 — a régua do B3.** Até esta data o `_painel_fe` amarrava o
> agrupamento do erro-padrão ao efeito fixo de ano, e o **B3** — o único sem ano FE — saía
> sozinho na régua de **entidade**, a mais frouxa. As duas escolhas são independentes, e o
> B3 é justamente onde a frouxa mais custa: os regressores de demanda são séries nacionais,
> constantes dentro do ano. Desamarradas, o CSV traz `p_entidade` e `p_entidade_ano` em toda
> linha. O **estoque não se move** (p<0,001 nas duas), e os sinais de demanda do B3 deixam de
> cruzar 5% (câmbio 0,003→0,179; preço da soja <0,001→0,150; crédito 0,828→0,950) — nenhum
> deles sustentava afirmação. Mesmo princípio já enunciado no #38 e no #39B.

| Spec | Regressor | β | p | Leitura |
|---|---|---|---|---|
| B1 fluxo ~ estoque | estoque_{t−1} | **+2,76** | <0,001 | conversão escala com a oferta disponível |
| B1q fluxo ~ estoque + estoque² | estoque²_{t−1} | +0,05 | 0,92 | **n.s.** — sem curvatura: a conversão **não satura** quando o estoque rareia |
| B2a hazard ~ estoque | estoque_{t−1} | −0,32 | 0,092 | (marginal) estoque-rico converte um pouco menos por unidade |
| B2b hazard ~ depleção | depleção_{t−1} | −0,02 | 0,48 | ~~n.s. — sem atrito claro~~ **→ SUPERADA pela D29 (#39B)**: o nulo era artefato de padronizar uma variável fora do domínio [0,1] em ~14% do painel. Tratada, a taxa **cai** com a depleção — β<0 nas 16 células da grade, cruza 5% em 11, entre 0,5 e 0,8 p.p. de taxa anual a menos a cada 10 pontos de depleção |
| B3 fluxo ~ estoque + demanda | estoque_{t−1} | **+2,76** | <0,001 | sobrevive a controlar câmbio/preço/crédito (#37) |

> **Honestidade**: B1/B3 são **parcialmente mecânicos** (fluxo ≡ estoque × hazard), então o β
> grande do estoque é em parte definicional. O teste informativo é o **hazard** (B2), e a
> leitura dele mudou com a **D29**: a taxa de conversão *por unidade de estoque* **cai** com a
> depleção — o remanescente trava, e isso é a assinatura de **atrito de oferta** que o próprio
> #39 pré-declarou. O "hazard plano" publicado aqui era artefato de domínio; ver o #39B.
> A spec quadrática **B1q** segue nula (estoque², p=0,92): a relação entre fluxo e estoque é a
> reta que a identidade prevê, sem curvatura própria — e isso é afirmação sobre o **estoque**,
> não sobre o comportamento da taxa.

### 3. A desaceleração Ato II→III é regional, não estadual — a fronteira **migrou**, não fechou

Decomposição do Δ do fluxo de conversão de vegetação (Mha/ano):

| Região | fluxo II | fluxo III | Δfluxo | efeito-OFERTA (Δestoque) | efeito-residual (Δhazard) |
|---|---|---|---|---|---|
| Goiás (total) | 0,071 | 0,072 | **+0,001** | −0,007 | +0,008 |
| **Sul** | 0,015 | 0,010 | **−0,006** | −0,001 | **−0,005** |
| Centro | 0,027 | 0,030 | +0,003 | −0,003 | +0,006 |
| **Norte** | 0,029 | 0,033 | **+0,004** | −0,003 | **+0,007** |

- **Estado**: o fluxo de conversão de vegetação **não desacelerou** (0,071→0,072) — o efeito-oferta
  (estoque encolhendo, negativo em toda parte) é **compensado** pelo efeito-residual (hazard subindo
  no Centro/Norte). A fronteira **relocou ao norte**.
- **Sul**: único onde o fluxo **caiu**, por estoque baixo **e** hazard caindo (0,012→0,008) — a
  assinatura de **fronteira fechada + giro à intensificação**.

> ⚠️ **Corroboração trocada (25/jul/2026).** Esta linha citava o #33 (`pasto→agric` do Sul
> despencando −88% no Ato III) como evidência convergente. Esse número **não sobreviveu** ao
> bracket da D26 — sob `pasto→(agric∪mosaico)` ele **inverte para +51%**, e a soja SIDRA do Sul
> sobe 244% (ver o CAUTION no [#33](33_transicoes_regionais.md)). **A conclusão do #39 não
> depende dele e não muda**: tudo aqui é medido sobre **vegetação nativa** (estoque convertível,
> `veg→pasto`, hazard), que a mudança de rótulo não toca — o #39 é **imune** na tabela do §9. A
> corroboração independente correta é o próprio `veg→pasto` do #33, que cai **−49% no Sul** e só
> −13% no Norte. O que muda é a *leitura* do "giro à intensificação": ela não pode mais se apoiar
> no colapso aparente do `pasto→agric`, porque a saída de pasto para lavoura-ou-uso-misto no Sul
> **acelerou**. Isso, aliás, **fortalece** a tese de restrição de oferta: a demanda por terra no
> Sul seguiu firme e foi o **Cerrado** que acabou, não o apetite.
- **Norte**: **fronteira ativa** — estoque declinante mas convertido a taxa **crescente**.

> **Ressalva de rótulo.** Chamamos a coluna de **"efeito-residual (Δhazard)"** justamente porque
> **não** é demanda pura medida: o *hazard* (fluxo/estoque) capta tudo o que não é o volume do
> estoque — inclui propensão a converter (demanda), mas também **atrito de proteção**, custo de
> acesso e giro à intensificação. É a parcela **não** explicada pela oferta. A inferência de que a
> desaceleração do Sul é oferta, e não demanda fraca, não repousa neste rótulo, e sim no teste
> hazard-plano (B2) somado à demanda macro **subindo** no Ato III (item 4).

> ⚠️ **Autocorreção (2026-07-28) — a ressalva acima valeu para o texto e não para a figura.**
> `outputs/fronteira_fechando/decomposicao_oferta_demanda.png` continuou exportando a barra com o
> rótulo retratado, **"Efeito-DEMANDA"**, e foi essa figura que a visualização publicou — ao lado
> da manchete "não foi a demanda, foi a oferta", sendo que no Sul aquela barra é **83% da freada**
> (`share_hazard = 0,828`). Ou seja: a peça afirmava uma coisa no texto e a oposta na figura.
> Corrigido na origem em `scripts/fronteira_fechando.py` — a barra agora é cinza e se chama
> *"Efeito-RESIDUAL (Δhazard) — NÃO é demanda medida"*, e o título pergunta "oferta (estoque) vs o
> resto (hazard)". **Quem reusar este PNG precisa re-exportá-lo**; versões geradas antes de
> 28/07/2026 carregam o rótulo errado. O episódio gerou a **D27**
> ([metodologia/auditoria_de_figuras.md](../metodologia/auditoria_de_figuras.md)): o rótulo de uma
> figura é uma afirmação, e ele envelhece quando a auditoria muda a conclusão sem re-rodar o
> script.

### 4. A demanda NÃO esfriou no Ato III — reforça a leitura de oferta no Sul

Níveis médios dos drivers (#37) por ato: câmbio real 134,5→**169,0**; preço recebido soja
104,4→**186,4**; crédito rural GO (R$ 2010) 14,3→**24,1 bi**. A demanda **subiu** no Ato III.
Logo a desaceleração da **conversão de vegetação** no Sul ocorreu **sob demanda forte** →
consistente com **restrição de oferta** (de Cerrado convertível) no Sul, não com demanda fraca.
*(Ajuste de 25/jul/2026: a frase dizia "desaceleração agrícola do Sul (#32/#33)" e apoiava-se
também no `pasto→agric` e no "pasto-reserva jovem" do #28 — as duas âncoras caíram na auditoria da
mudança de rótulo. A leitura de oferta continua, e mais limpa, porque agora repousa só em medidas
imunes: estoque convertível, `veg→pasto` e hazard.)*

## Veredito

**A fronteira está fechando — mas de forma escalonada e incompleta.** No agregado estadual, **não**
(ainda): resta ~60% do Cerrado convertível de 1985 e o fluxo de conversão não desacelerou, apenas
migrou ao norte. **Regionalmente, sim no Sul**: estoque baixo + hazard caindo + giro à intensificação
sob demanda forte. O **Norte** é fronteira ativa que persegue o estoque convertível remanescente.

Para a tese, isto **complementa** (não derruba) o "drive comum + gradiente de aptidão" (#37/#38),
adicionando uma **terceira perna**: a oferta de terra convertível é um **teto regional móvel** — o
Sul bateu no teto e girou para intensificação; o Norte ainda tem teto e avança. A "marcha ao norte"
do #32 é, em parte, a fronteira **perseguindo o estoque que só resta no norte**.

## Limitações

- **Convertível = proxy MapBiomas** (teto; sem CAR/UC/PRODES). Cenário RL (20%) é cru.
- **Fluxo = perda líquida de estoque** clipada em 0 (ignora rebrota; gross `veg→pasto` via
  `analise_transicoes.py` refinaria).
- **B1/B3 parcialmente mecânicos**; a inferência forte vem do hazard (B2) + decomposição. O B2b saiu "fraco/plano" aqui, e a **D29** mostrou que o plano era artefato: tratada a variável, o hazard cai com a depleção.
- **Descritivo/quase-causal**; recorte mesorregional (3 regiões) é grosso; Ato III tem só 4–5 anos.

## Como rodar

```bash
python scripts/fronteira_fechando.py               # CSVs + 4 figuras
python scripts/fronteira_fechando.py --sem-figuras # só a parte numérica
```
