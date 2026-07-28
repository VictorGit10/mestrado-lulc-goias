# Proposta de reformulação da visualização

> Documento de proposta (jul/2026). Não altera o site — desenha a reforma.
> Contexto: a viz foi construída sob o framing antigo (**3 atos + política como
> motor**, ver [`IDEIA.md`](IDEIA.md)); desde então os resultados cristalizaram
> uma espinha intelectual nova — a tese das **4 pernas de evidência**
> ([`../../Textos/indice_logico_pipelines.md`](../../Textos/indice_logico_pipelines.md))
> e a leitura narrativa da investigação
> ([`../../Textos/narrativa_pipelines.md`](../../Textos/narrativa_pipelines.md)).
> O site acumulou seções novas sobre o esqueleto velho sem re-arquitetar. Esta
> proposta re-arquiteta o **conteúdo e a condução**, preservando o que já é bom.

---

## 0. Estado da reforma — 28/jul/2026

> **A análise fechou.** Não há pendência analítica bloqueando a reforma: a auditoria da
> mudança de rótulo do Mosaico (D25/D26) e a auditoria dos pipelines de fundação
> (#12→#12B, #14B, #22B, #23) foram encerradas entre 23 e 27/jul. O que resta é **de
> visualização**.

**Já construído no site atual** *(a reforma reposiciona, não reconstrói)*:

| peça | onde está hoje | estado |
|---|---|---|
| scroll dos 40 anos + régua + sparkline | aba Narrativa | ✅ pronto, vai intocado para a Parte 1 |
| Ato III com a copy corrigida (D25) | `index.html` §atos | ✅ reescrito em 25/jul |
| Sankey + matriz **7×7** (#12B) | §2 | ✅ regenerado em 27/jul |
| Mosaico com faixa própria na barra empilhada | §atos | ✅ 25/jul |
| mapa animado do centro de massa (`marcha-mapa.js`) | "Movimento III" | ✅ pronto, vira **herói da Perna 1** |
| idade do pasto: mapa de bimodalidade + histograma por região | §6 | ✅ re-cablado em 25/jul, vira **herói da Perna 2** |
| oficina M1–M6 + D1–D26 | aba Métodos | ✅ existe, precisa de **consolidação**, não de conteúdo novo |

**O que a reforma ainda precisa criar** *(nenhum item exige análise nova)*:

1. A **arquitetura**: dissolver as abas, reordenar em Partes 0–4, montar as 4 pernas.
2. O **rail lateral fixo** (navegação) — a única peça de UX genuinamente nova.
3. O **esquema estático de 2 painéis** do #42 (a regressão espúria) — a Perna 3 é a única
   sem interativa.
4. Um punhado de **correções de números** que a auditoria deixou na tela — inclusive um
   erro de 10× na primeira frase do hero (ver `BLUEPRINT_PARTES_0-1-3-4.md` § Parte 0).

Plano de execução, ordem de trabalho e verificação: [`PLANO_DE_CONSTRUCAO.md`](PLANO_DE_CONSTRUCAO.md).

---

## 1. Resumo executivo

**A ideia numa frase:** transformar o site de um *catálogo de achados em três
movimentos* numa **história de detetive em três partes que termina nas 4 pernas** —
onde o leitor descobre o **veredito** (as 4 pernas) junto com a investigação, em vez de
recebê-lo pronto. O hero entrega o **fenômeno + a virada** (a marcha e o "a explicação
óbvia está errada"), **não o veredito**: o suspense fica no *por quê*, e é o que se
descobre na Parte 2. (Analogia de detetive: o hero dá o crime, não a solução.)

**O que se mantém (inegociável):**
- O **scroll dos 40 anos de mapa** (`timeline.js` + seção `story`) — abre a peça.
- A **viz interativa das trajetórias** — o centro de massa caminhando ano a ano
  (`marcha-mapa.js`) — **promovida a peça-central da Perna 1**.
- O **sistema de design** (serifa no corpo, paleta restrita, régua superior fixa,
  tom editorial sóbrio).

**O que muda:**
- A **tese vira o destino explícito**, não um "Movimento III" entre outros.
- As **4 pernas de evidência** viram o esqueleto visível da segunda metade.
- O "**Movimento II**" (gaveta de achados no agregado) **se dissolve** — suas peças
  viram evidência de apoio dentro da perna certa.
- Entra a **cronologia da investigação** (a autocorreção como manchete), que é
  exatamente "o texto narrativa que geramos recentemente" e o que torna a peça
  empolgante.
- Vira um **scroll único e contínuo** (acaba a divisão em abas); a metodologia fecha
  como apêndice no fim.

---

## 2. Diagnóstico — por que o site já não conta a história certa

O site nasceu quando o framing era "3 atos no território + marcos institucionais
como motor". Os resultados reorganizaram tudo numa tese contraintuitiva e bem
específica: **reorganização espacial coordenada, NÃO deslocamento causal**. O site
foi ganhando seções (marcha ao norte, eixo ambiental, autocorreção) por cima do
esqueleto antigo. Cinco sintomas:

1. **Três esquemas organizadores competindo.** A peça usa ao mesmo tempo (a) os
   **3 atos** (tempo), (b) os **3 Movimentos** (I saldo, II processos, III marcha)
   e (c), implícita, a tese. Nenhum deles é a espinha atual (as **4 pernas**). O
   leitor não recebe um fio único.

2. **A tese chega tarde e enfraquecida.** O achado mais empolgante e mais difícil
   de conquistar — *o autor testou a própria hipótese predileta e a matou* — é o
   **destino** da história, mas está enterrado como "Movimento III" (um de três).
   As 4 pernas, que são a estrutura real do argumento, nunca aparecem como
   esqueleto.

3. **O "Movimento II" é uma gaveta.** "O que os dados revelam no agregado"
   (pecuária desacoplada, lavoura sobre pasto, crédito, idade do pasto) é um
   apanhado de achados que não constroem em direção a nada. É a maior fonte de
   **ruído**. Cada peça ali é *evidência de apoio de uma perna específica*, não um
   ato autônomo.

4. **Duas cronologias embaralhadas.** Há dois relógios no trabalho: os **40 anos
   do território** (o scroll de mapas) e o **arco da investigação** (como a
   pergunta foi feita, testada, refutada e reconstruída — a `narrativa_pipelines`).
   O site acerta o primeiro e ignora o segundo — mas é o segundo que dá emoção e é
   literalmente o texto novo que você pediu para incorporar.

5. **O modo Métodos pesa demais.** M1–M6 + D1–D16 é uma segunda dissertação.
   Ótimo como apêndice ("a oficina"), mas hoje compete com a narrativa pela
   atenção em vez de servi-la.

---

## 3. A ideia central da reforma — a história de detetive

Re-enquadrar a peça inteira como uma **investigação em três partes**, espelhando o
arco real do trabalho, com as **4 pernas como o veredito**:

```
   PARTE 1                 PARTE 2                      PARTE 3
   O território     →      A investigação        →      O veredito
   (o QUÊ)                 (será? por quê?)             (as 4 pernas fecham)
   ───────────            ─────────────────            ─────────────────
   scroll 40 anos          hipótese tentadora           a tese em uma frase
   + saldo + fluxos        → 4 pernas testadas          + a autocorreção
                           (trajetórias interativas)      como assinatura
```

**O princípio de condução:** o site deve *parecer que descobre a tese junto com o
leitor*, não que a ensina. É isso que "empolgante" significa aqui — e é exatamente
o tom da `narrativa` e do `ensaio`. A dobradiça dramática é: **a hipótese óbvia
(a lavoura do Sul empurra o Norte — iLUC) é boa demais para ser verdade, e o
trabalho prova que ela é falsa.** A partir daí, as 4 pernas são o veredito, e as
autocorreções são o motivo para confiar nele.

---

## 4. Nova estrutura — seção a seção

**Decisão travada:** é **um scroll único e contínuo** (as abas *Narrativa | Métodos*
somem). A história corre de cima a baixo — Partes 0→4 — e **"A oficina"** (era
*Métodos*) fecha como a **Parte 4**, um apêndice no fim do mesmo scroll para quem
quiser descer até a metodologia.

**Navegação (a tarefa que falta):** um scroll único com a Parte 2 (4 pernas densas) e a
Parte 4 (a oficina) é longo demais para depender só da rolagem — o leitor que veio pelo
veredito corre o risco de não chegar à Parte 3 (o selo de credibilidade) nem de saber que
a oficina existe. Entra um **rail lateral fixo** (sumário/ToC com as 4 partes e, sob a
Parte 2, as 4 pernas), visível a partir do início da Parte 1: marca a posição atual,
permite saltar direto ao veredito ou à oficina, e é o que torna o "scroll único"
 navegável em vez de exaustivo. É barato e essencial — sem ele, dissolver as abas é um
 regresso.

### PARTE 0 · Abertura (hero) — a promessa + a virada
**Decisão travada:** o hero **entrega a tese logo** (a marcha + a virada iLUC); o
suspense fica no "por quê", não no "o quê". Trocar "Buscando histórias em 40 anos de
dados" (vago) por um hero que entrega o destino e planta o gancho de detetive.
Rascunho:

> **A marcha ao norte**
> Em 40 anos, toda a fronteira agropecuária de Goiás se moveu para o norte. A
> explicação óbvia — a soja do Sul empurrando o pasto e o boi — está errada. O que
> de fato aconteceu é mais sutil, e melhor documentado. *Comece pelos 40 anos no
> mapa ↓*

### PARTE 1 · Os 40 anos no mapa — o fenômeno (MANTÉM o scroll)
- O **scroll de 40 anos** com os 3 atos, exatamente como está. É o coração visual e
  fica intocado.
- **Enxugar o toggle de camadas** para o que serve *aqui*: **Cobertura + Δ vs 1985**.
  *Fogo* e *Transições* saem deste toggle e reaparecem na perna certa (fogo = Perna
  1/3 adjacente; transições = a ponte de fluxos logo abaixo).
- Fechar a Parte 1 com o **saldo** (os 4 números-choque: veg −5,8 Mha, agric ×4,8,
  soja ×12, pasto +1,0 Mha em U invertido) e os **fluxos** (o Sankey: de onde para
  onde os hectares foram). Esse é o baseline factual.
- **Transição-gancho** para a Parte 2: *"O saldo diz o quê mudou. Não diz onde, nem
  por quê. E o 'onde' guarda uma surpresa."*

### PARTE 2 · A investigação — a marcha e o que a explica (o núcleo reformulado)
Abre com a **hipótese tentadora**, dita sem rodeio:

> *A hipótese óbvia: a lavoura do Sul empurrou o pasto e o boi para o Norte — um
> vazamento de desmatamento dentro do próprio estado (iLUC). É uma boa história. E
> está errada. Veja por quê, em quatro perguntas.*

Então as **4 pernas**, cada uma no padrão **pergunta → evidência → resposta em uma
frase**, contadas como descoberta:

**Perna 1 — O padrão existe? → Sim: tudo marchou ao norte.**
- **Peça-central: a viz interativa das trajetórias** (`marcha-mapa.js`), promovida a
  herói desta perna: pasto **+78 km**, rebanho **+67**, agric **+65**, vegetação
  **ancorada**; a faixa latitude-tempo sincronizada; o toggle da elipse.
- Robustez em uma linha: pixel-a-pixel (#43, o MAUP não é problema); IC95% por
  bootstrap (D19 — a vegetação inclui zero); a "muralha norte" é **a floresta** (#44).

**Perna 2 — Qual o mecanismo? → Dois Goiáses.**

*(Seção consolidada em 28/jul/2026. A versão anterior acumulava três camadas de
tachado sobre a mesma frase; o registro do que caiu vive agora em
[`BLUEPRINT_PARTE2.md`](BLUEPRINT_PARTE2.md) → "Estado dos dados da Perna 2".)*

- **A afirmação, na forma que sobrevive:** o Sul **intensifica** (`pasto→lavoura`), o Norte
  **abre fronteira** (`mata→pasto`). A segregação é do **tipo de transição** — e quem a
  sustenta é o `veg→pasto`, a medida **imune** à ambiguidade do rótulo (Sul −49% × Norte
  −13% entre os Atos II e III).
- 🛑 **A qualificação por idade caiu, e é ela que muda o desenho da peça.** "Sul converte
  pasto jovem (~9a) / Norte, pasto velho (~16–20a)" foi afirmado por este trabalho e
  **refutado** entre 23 e 25/jul, por três caminhos independentes (#40, #28C, #33). A
  cláusula "a geografia desloca o **peso** da mistura" **também sai**: a região explica
  **0,5%** da variação da idade. Força da perna rebaixada de "forte" para **moderada** — não
  porque algo ficou frágil, mas porque ela afirmava três coisas e sobrou **uma**.
- ✅ **A peça interativa já foi re-cablada (25/jul) e o resultado é melhor do que o
  planejado.** O plano original era um "aha" de contraste: escolher o Sul profundo esperando
  um pico só e ver dois. Esse desenho **dependia do gradiente refutado**. O que se
  implementou é mais direto e mais forte: o toggle passou de **ato → região**, e o mapa
  deixou de pintar idade para pintar o **veredito de bimodalidade** por AMC. O "aha" virou
  *a ausência de contraste* — percorra as cinco regiões e **o desenho não muda** (5/5
  mesorregiões, 162/164 AMCs bimodais por dentro). Um mapa quase uniforme é a forma visual
  de um η² de 0,5%.
- **Consequência para a reforma:** esta peça **não precisa ser construída** — precisa ser
  **movida** para dentro da Perna 2 e receber a copy nova.
- **Absorve aqui** (deixam de ser cards soltos): "lavoura sobre pasto, não sobre mata" e
  "crédito → pastagem" como evidência de apoio. ⚠️ **Com duas etiquetas obrigatórias:** o
  SICOR é o *canal associado mais forte*, **não** um "vetor causal"; e a **intensificação**
  do painel espacial (#49, M1) é **frágil ao bracket** — o intervalo cruza o zero e a âncora
  SIDRA dá sinal oposto. Quem sustenta a perna no painel é a **substituição** (M3), robusta.
  O #22B fecha uma ambiguidade **diferente** (o β<0 é intensificação *within*, não
  composição) e **não** revoga a dependência de medida.
- **Autocorreção em destaque:** o #40 derrubou o próprio overclaim no mesmo dia
  (plantio direto era confundidor de latitude → **D14**). É onde o fio "trabalho que
  se autocorrige" começa a aparecer — e a queda do gradiente de idade, semanas depois,
  é onde ele fica sério.

**Perna 3 — É a lavoura do Sul empurrando o Norte? → Não. É coordenação. (o clímax)**
- **A refutação:** o #34 testou a hipótese-mãe e ela falhou. Enquadre como: *"o autor foi
  atrás da hipótese que mais o favorecia — e a derrubou."*
  ⚠️ **Precisão obrigatória na copy:** quem refuta é o **spillover de sinal trocado**
  (θ=−0,16, **p=0,02**), não o nulo de Granger. O nulo é de **baixo poder** (N≈38 anos,
  ~48% para efeito moderado) — apresentá-lo como a prova entrega à banca a objeção mais
  barata que existe ("ausência de evidência não é evidência de ausência"). Um efeito
  **significativo na direção contrária** não tem essa fraqueza. A copy da Parte 2 já foi
  corrigida nesse ponto.
- **A simetria que fecha a perna** (beat novo, 28/jul): se alguma infraestrutura *puxasse*
  a fronteira, seu centro de gravidade estaria à frente dela — e está **atrás**, em todas
  as camadas medidas. Crédito ~75 km ao sul do pasto (#50); armazenagem CONAB ~150 km ao
  sul, a camada mais meridional de todas (#53); cadeia exportadora co-move sem liderar
  (#45). Silo, banco e porto **consolidam**; nenhum lidera.
- **A obra-prima da autocorreção:** o #42 (o Granger reverso que inverteria tudo,
  demonstrado espúrio — série I(2), Toda-Yamamoto zera as duas direções, placebos). É
  a história metodológica mais empolgante do conjunto — **dê palco a ela.**
- **O positivo, honesto:** o que coordena é um **drive comum** (câmbio/crédito/preço)
  sobre um **gradiente de aptidão** — rotulado sem exagero como *"corroborante, não
  estabelecido"* (#37/#38/#52/#54; p de permutação ≈0,07–0,13, não significante a 5%).
- É a seção que mais precisa da **voz narrativa** (puxar direto da `narrativa`/`ensaio`).
- **Compensa a falta de interativa** com um **esquema estático de 2 painéis** para o #42: a
  regressão espúria tem um visual canônico — duas séries lisas que correlacionam por
  construção (o pasto do Norte "antecipa" até o pasto do próprio Sul, que nenhum
  mecanismo econômico explicaria). Um desenho pequeno torna o "espúrio" visível sem
  precisar de palavras técnicas; soma-se às figuras #34/#42, não as substitui.

**Perna 4 — Por que desacelerou? → Bateu no teto de oferta.**
- A fronteira **persegue o Cerrado convertível que só resta no norte**; o Sul fechou a
  fronteira **sob demanda forte** (assinatura de restrição de oferta, não de demanda
  fraca); a terra que resta está **97% desprotegida** (teto **físico, não
  institucional**); custo de carbono ~**973 Mt CO₂e**.
- **Absorve aqui** "pecuária desacoplada" como contexto.
- **Beat novo (28/jul): o preço da marcha tem duas contas.** Além do carbono (#47), entra o
  **#51** — a fronteira norte quase dobra a área cultivada (+93% × +14% no Sul) e termina
  com desenvolvimento municipal **abaixo** do Sul; a expansão de área é praticamente
  desacoplada do desenvolvimento. É o achado mais comunicável do conjunto para fora da
  academia e não tinha endereço em lugar nenhum da peça.
- ⚠️ **Etiqueta obrigatória:** a queda do *hazard* de conversão **não é**, por si, "queda de
  demanda" — ela embute proteção, atrito e intensificação. Quem sustenta a leitura de oferta
  é o teste do plano estoque×hazard, não o rótulo. E o Ato III tem **5 anos**: "sinal
  inicial de", nunca "consolidou".

### PARTE 3 · O veredito + a honestidade (o fecho)
- O **callout da tese** (já existe) — a afirmação central, cristalina.
- **A assinatura do trabalho: uma investigação que se autocorrige.** Um painel curto e
  forte com as autocorreções como **selo de credibilidade** — não enterradas. É o "por que
  confiar nisto", e é genuinamente empolgante (puxar do fecho da `narrativa` e do "ativo
  mais raro" do índice lógico).
  **Revisado em 28/jul:** a lista passa de 7 para **10 itens** e ganha um **segundo bloco**.
  Entram o **#12B** (a matriz primária descartava 6,5–10,9% do estado por ano, e a própria
  validação era cega por construção — é a mais severa, abre a lista), a **queda do gradiente
  de idade** (#28C/#40/#33) e o **#54** (o trabalho rebaixou a significância do próprio drive
  comum). O segundo bloco registra **três verificações que não derrubaram nada** (#14B, #22B,
  #48): contar só as auditorias que acham erro é outra forma de selecionar resultado, e a
  distinção entre os dois blocos *é* o argumento. Copy pronta em
  [`BLUEPRINT_PARTES_0-1-3-4.md`](BLUEPRINT_PARTES_0-1-3-4.md) § 3.2.
- **O que o trabalho NÃO afirma** (os limites honestos), breve. **Dois limites novos:** a
  ambiguidade de medida do fim da série (bracket D26, com âncora SIDRA) e o rebaixamento do
  **#23** — as políticas testadas são federais, então os marcos da régua **contextualizam,
  não identificam**.
- CTA para **"A oficina"**.

### PARTE 4 · A oficina (era a aba Métodos) — enxugar e pôr no fim do scroll
- **Deixa de ser aba** e vira o **fecho do scroll único** — apêndice para quem quiser
  descer até a metodologia depois do veredito.
- Manter, mas **consolidar**. Fundir M1 (periodização/como os atos foram detectados) +
  M2 (as métricas) + M3 (camadas de evidência) em 2–3 peças enxutas.
- Manter a **vitrine do painel** (inventário de dados, M4).
- Mover as **decisões D1–D26** para **uma única tabela colapsável** de referência.
  *(São 26, não 20: D21–D24 entraram com o censo do #28 e D25/D26 com a auditoria do
  Mosaico. Três lugares do site ainda dizem "16 decisões" — corrigir na reforma.)*
- Manter **M6 fragilidades** (honestidade metodológica).
- ⚠️ **Qualificar a periodização:** com a matriz recontada (#12B), o pico de KL migrou de
  2020 para **2022**. A fronteira de 2020 se sustenta pela âncora imune (soja plantada
  SIDRA), mas a oficina **não pode dizer** que os quatro métodos apontam o mesmo ano sem
  dizer qual deles se moveu.

---

## 5. Manter / cortar / mover

| Peça atual | Decisão | Para onde |
|---|---|---|
| Scroll 40 anos (`timeline.js` + `story`) | **Manter** | Parte 1 (intocado) |
| Viz trajetórias do centro de massa (`marcha-mapa.js`) | **Manter + promover** | Peça-central da Perna 1 |
| Sistema de design (CSS, régua, paleta, serifa) | **Manter** | Global |
| Sankey de fluxos + matriz **7×7** (`sankey.js`/`matriz.js`) | **Manter + realocar** | Fecho da Parte 1 — já regenerado com o Mosaico (#12B, 27/jul) |
| Interativa idade do pasto (`pastagem-reserva.js`) | ✅ **já re-cablada** (25/jul) → só **mover** | Perna 2 — mapa pinta bimodalidade, toggle é por região |
| Faixa própria do Mosaico na barra empilhada | **Manter** | Parte 1 — regra "fluxo pinta, estoque não" (§3.7.2 do `IMPLEMENTACAO.md`) |
| Callout da tese | **Manter** | Parte 3 |
| Divisão em abas (Narrativa \| Métodos) | **Cortar** | Vira **scroll único**; oficina no fim |
| Rótulos "3 Movimentos" (I/II/III) | **Cortar** | Substituídos pelas 4 pernas |
| "Movimento II — o que os dados revelam no agregado" | **Dissolver** | Cards viram apoio nas Pernas 2 e 4 |
| Toggle de 4 camadas do mapa | **Reduzir** | Cobertura+Δ na Parte 1; fogo/transições realocam |
| Cards `como-bloco` que não fecham uma perna | **Cortar/fundir** | — |
| Hero "Buscando histórias…" | **Reescrever** | Promessa + virada (entrega a tese) |
| Métodos M1–M6 + D1–D16 | **Enxugar** | Parte 4 (fim do scroll único) |

---

## 6. Princípios de redação (para ser empolgante *e* honesto)

- **Cada perna abre com uma pergunta e fecha com uma resposta em uma frase.** O site já
  faz isso em pontos — torne o padrão universal.
- **Nulos e autocorreções são manchete, não rodapé.** São o que dá credibilidade e são
  a parte mais empolgante da história.
- **Voz de descoberta, não de aula:** "achávamos X; o dado disse Y".
- **Sempre o "o que isto NÃO diz"** — fiel à cultura do trabalho (D14) e ao que separa
  uma tese de um punhado de gráficos.

---

## 7. Decisões (fechadas em jul/2026)

1. **Hero:** ✅ **entrega o fenômeno + a virada** (a marcha + "a explicação óbvia está
   errada"), **não o veredito** (as 4 pernas ficam para a Parte 2). O suspense fica no
   "por quê", não no "o quê".
2. **Estrutura:** ✅ **scroll único e contínuo** — as abas somem; a oficina vira a
   Parte 4, no fim do mesmo scroll.
3. **Sankey:** ✅ **mantido como está** (é bonito e carrega os fluxos) — no fecho da
   Parte 1.
4. **Idade do pasto:** ✅ **re-cablear, não simplificar** — mapa e histograma passam a
   conversar (selecionar região redesenha o histograma, que segue bimodal), para que a
   interação *seja* o argumento #28C. Detalhe na Perna 2 acima.
5. **Navegação:** ✅ **rail lateral fixo** (ToC: 4 partes + as 4 pernas sob a Parte 2),
   visível a partir da Parte 1, marcando posição e permitindo saltar ao veredito/oficina.
   Scroll único longo demais para depender só da rolagem — sem ele, dissolver as abas é
   um regresso.
6. **Perna 3 sem interativa:** ✅ **um esquema estático de 2 painéis** para o #42 (regressão
   espúria: duas séries lisas que correlacionam por construção) — compensa o fato de a
   perna-clímax ser a mais textual e a única sem peça interativa. Não substitui as figuras
   #34/#42; soma-se a elas.

### Decisões acrescentadas em 28/jul/2026

7. **O Mosaico é personagem da Parte 1, não nota de rodapé.** ✅ A regra é
   **"fluxo pinta, estoque não"** (`IMPLEMENTACAO.md` §3.7.2, decidida pelo autor em
   27/jul): onde o objeto é *para onde a área foi*, o Mosaico aparece com cor própria;
   onde é *o que a área é*, não é pintado mas é contado. O Ato III é onde o leitor
   **aprende a ler a classe**, e tudo o que vem depois depende disso ter funcionado.
8. **A copy nomeia qual teste refuta a hipótese-mãe.** ✅ O spillover de sinal trocado
   (θ=−0,16, p=0,02), **não** o nulo de Granger (baixo poder, N≈38). Vale como regra geral
   da peça: onde houver um nulo e um efeito de sinal contrário, a manchete é o efeito.
9. **As autocorreções ganham um segundo bloco: as verificações que confirmaram.** ✅
   (#14B, #22B, #48.) Listar só as auditorias que derrubaram algo é selecionar resultado —
   e o contraste entre os dois blocos é mais persuasivo que qualquer um deles sozinho.
10. **O #51 entra na Perna 4** como a segunda conta do "preço da marcha", ao lado do
    carbono. ⏳ *Reversível:* se alongar demais a perna, vira coda da Parte 3 — mas não é
    cortado.

### Próximo passo
~~Detalhar o blueprint da Parte 2 em nível de copy~~ ✅ **feito** (25/jul, revisado em
28/jul). Os três documentos de prancheta estão reconciliados com o estado analítico.
**O próximo passo é a construção** — plano de execução em
[`PLANO_DE_CONSTRUCAO.md`](PLANO_DE_CONSTRUCAO.md).
