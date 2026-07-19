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

## 1. Resumo executivo

**A ideia numa frase:** transformar o site de um *catálogo de achados em três
movimentos* numa **história de detetive em três partes que termina nas 4 pernas** —
onde o leitor descobre a tese junto com a investigação, em vez de recebê-la pronta.

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
somem). A história corre de cima a baixo — Partes 0→3 — e **"A oficina"** (era
*Métodos*) fecha como a **Parte 4**, um apêndice no fim do mesmo scroll para quem
quiser descer até a metodologia.

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
- Sul **intensifica** (`pasto→lavoura`, pasto jovem ~9 anos); Norte **abre fronteira**
  (`mata→pasto`, pasto velho ~20 anos).
- **A interativa da idade do pasto: re-cablear, não simplificar.** Hoje são duas peças
  lado a lado (mapa por AMC + histograma bimodal, com toggle de ato). A recomendação é
  **fazê-las conversar** para que a interação *seja* o argumento — em dois tempos:
  - *Tempo 1 — "existem dois modos":* o histograma bimodal da idade na conversão, com
    os dois picos do GMM marcados (~5 anos e ~22/35 anos). O toggle de ato **fica** —
    porque o motor honesto da mistura é o **tempo** (o Ato I converte pasto jovem; o
    II/III, velho).
  - *Tempo 2 — "a geografia desloca o peso, não cria os modos" (o achado #28C):* ao
    **selecionar uma região** no mapa (Sul jovem → Norte velho), o histograma **se
    redesenha para aquela região e continua com dois corcovas**. O "aha" é escolher o
    Sul profundo esperando um pico só de pasto jovem — e ainda ver os dois. Essa
    persistência *é* a prova de que a bimodalidade mora **dentro** de cada região
    (34/36 AMCs bimodais), que é justamente a autocorreção da D14. Fica mais rico e mais
    honesto, sem ficar conceitualmente mais complexo.
- **Absorve aqui** (deixam de ser cards soltos): "lavoura sobre pasto, não sobre mata"
  e "crédito → pastagem" como evidência de apoio.
- **Autocorreção em destaque:** o #40 derrubou o próprio overclaim no mesmo dia
  (plantio direto era confundidor de latitude → **D14**). É onde o fio "trabalho que
  se autocorrige" começa a aparecer.

**Perna 3 — É a lavoura do Sul empurrando o Norte? → Não. É coordenação. (o clímax)**
- **A refutação:** o #34 testou a hipótese-mãe e ela falhou (sem precedência temporal;
  spillover **de sinal trocado**). Enquadre como: *"o autor foi atrás da hipótese que
  mais o favorecia — e a derrubou."*
- **A obra-prima da autocorreção:** o #42 (o Granger reverso que inverteria tudo,
  demonstrado espúrio — série I(2), Toda-Yamamoto zera as duas direções, placebos). É
  a história metodológica mais empolgante do conjunto — **dê palco a ela.**
- **O positivo, honesto:** o que coordena é um **drive comum** (câmbio/crédito/preço)
  sobre um **gradiente de aptidão** — rotulado sem exagero como *"corroborante, não
  estabelecido"* (#37/#38/#52/#54; p de permutação ≈0,07–0,13, não significante a 5%).
- É a seção que mais precisa da **voz narrativa** (puxar direto da `narrativa`/`ensaio`).

**Perna 4 — Por que desacelerou? → Bateu no teto de oferta.**
- A fronteira **persegue o Cerrado convertível que só resta no norte**; o Sul fechou a
  fronteira **sob demanda forte** (assinatura de restrição de oferta, não de demanda
  fraca); a terra que resta está **97% desprotegida** (teto **físico, não
  institucional**); custo de carbono ~**973 Mt CO₂e**.
- **Absorve aqui** "pecuária desacoplada" como contexto.

### PARTE 3 · O veredito + a honestidade (o fecho)
- O **callout da tese** (já existe) — a afirmação central, cristalina.
- **A assinatura do trabalho: uma investigação que se autocorrige.** Um painel curto e
  forte com as **7 autocorreções** (#28C, #40, #40B, #41, #42, #44, #45 + D19) como
  **selo de credibilidade** — não enterradas. É o "por que confiar nisto", e é
  genuinamente empolgante (puxar do fecho da `narrativa` e do "ativo mais raro" do
  índice lógico).
- **O que o trabalho NÃO afirma** (os limites honestos), breve.
- CTA para **"A oficina"**.

### PARTE 4 · A oficina (era a aba Métodos) — enxugar e pôr no fim do scroll
- **Deixa de ser aba** e vira o **fecho do scroll único** — apêndice para quem quiser
  descer até a metodologia depois do veredito.
- Manter, mas **consolidar**. Fundir M1 (periodização/como os atos foram detectados) +
  M2 (as métricas) + M3 (camadas de evidência) em 2–3 peças enxutas.
- Manter a **vitrine do painel** (inventário de dados, M4).
- Mover as **decisões D1–D20** para **uma única tabela colapsável** de referência.
- Manter **M6 fragilidades** (honestidade metodológica).

---

## 5. Manter / cortar / mover

| Peça atual | Decisão | Para onde |
|---|---|---|
| Scroll 40 anos (`timeline.js` + `story`) | **Manter** | Parte 1 (intocado) |
| Viz trajetórias do centro de massa (`marcha-mapa.js`) | **Manter + promover** | Peça-central da Perna 1 |
| Sistema de design (CSS, régua, paleta, serifa) | **Manter** | Global |
| Sankey de fluxos (`sankey.js`/`matriz.js`) | **Manter + realocar** | Fecho da Parte 1 |
| Interativa idade do pasto (`pastagem-reserva.js`) | **Re-cablear** (mapa↔histograma) | Perna 2 |
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

1. **Hero:** ✅ **entrega a tese logo** (a marcha + a virada iLUC). O suspense fica no
   "por quê", não no "o quê".
2. **Estrutura:** ✅ **scroll único e contínuo** — as abas somem; a oficina vira a
   Parte 4, no fim do mesmo scroll.
3. **Sankey:** ✅ **mantido como está** (é bonito e carrega os fluxos) — no fecho da
   Parte 1.
4. **Idade do pasto:** ✅ **re-cablear, não simplificar** — mapa e histograma passam a
   conversar (selecionar região redesenha o histograma, que segue bimodal), para que a
   interação *seja* o argumento #28C. Detalhe na Perna 2 acima.

### Próximo passo sugerido
Detalhar o **blueprint da Parte 2 em nível de copy** (título, pergunta de abertura,
1–2 parágrafos e a "resposta em uma frase" de cada perna), aprovar esse texto, e só
então tocar no HTML.
