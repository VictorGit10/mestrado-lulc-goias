# Plano de construção da visualização reformulada

> Documento de **execução** (28/jul/2026). O *porquê* está em
> [`PROPOSTA_REFORMULACAO.md`](PROPOSTA_REFORMULACAO.md); a *copy* está em
> [`BLUEPRINT_PARTES_0-1-3-4.md`](BLUEPRINT_PARTES_0-1-3-4.md) e
> [`BLUEPRINT_PARTE2.md`](BLUEPRINT_PARTE2.md). Aqui está **o que se constrói, em que
> ordem, com quais arquivos e como se verifica**.
>
> O [`IMPLEMENTACAO.md`](IMPLEMENTACAO.md) descreve o site **atual** (e é de maio, com
> emendas até 27/jul). Ele **não** é substituído por este documento: continua sendo o
> registro do que está no ar até a troca final.

---

## 1. Estratégia — arquivo paralelo, troca no fim

**Decidido em 28/jul/2026.** O site é publicado pelo GitHub Pages a partir do `master`
(`VictorGit10/mestrado-lulc-goias`), então editar o `index.html` no lugar significa
publicar uma reforma pela metade a cada commit. A reforma tem várias etapas.

```
Visualizacao/
├── index.html            ← permanece no ar, intocado, até a troca
├── reforma.html          ← a construção
└── assets/
    ├── css/reforma.css   ← novo: rail lateral, partes, pernas
    └── js/rail.js        ← novo: navegação do scroll único
```

- Os dois arquivos rodam do mesmo servidor local
  (`http://127.0.0.1:8765/index.html` e `…/reforma.html`) — **comparação lado a lado a
  qualquer momento**, sem trocar de branch.
- Todo CSS e JS existente é **compartilhado**, não copiado. `reforma.css` contém apenas o
  que é novo; onde a reforma precisar mudar uma regra existente, ela **sobrescreve** por
  especificidade a partir de um escopo `body.reforma`, para não afetar o `index.html`.
- **A troca final é um commit só**: `reforma.html` → `index.html`, o antigo vira
  `docs/_arquivo/index-pre-reforma.html` (registro, não link publicado).

**Critério de aceite para trocar:** as Partes 0–4 completas, console limpo, verificação
da §7 passando, e o autor tendo lido a peça inteira de cima a baixo pelo menos uma vez.

---

## 2. Ordem de trabalho

**Fase A — a moldura (primeira fatia, decidida em 28/jul).** Entrega cedo a única peça de
UX genuinamente nova (o rail) e valida a navegação **antes** de investir na copy densa da
Parte 2.

| # | entrega | verificável por |
|---|---|---|
| A1 | esqueleto de `reforma.html`: scroll único, Partes 0–4 como seções vazias com IDs definitivos | a página rola de cima a baixo; nenhum `data-modo`, nenhuma aba |
| A2 | **rail lateral** (`rail.js` + `reforma.css`): 5 partes + 4 pernas aninhadas, marca posição, salta ao clique | rolar a página move o marcador; clicar em "O veredito" salta |
| A3 | **Parte 0** (hero) com a copy nova — incluindo a correção de 10× | a primeira frase diz 378 milhões / 15 bilhões |
| A4 | **Parte 1** completa: régua superior + scroll dos 40 anos + saldo (5 cards) + Sankey 7 grupos | os 40 anos rolam; o Sankey desenha o Mosaico |

**Fase B — o núcleo.** Parte 2: abertura (a hipótese tentadora) + as 4 pernas, cada uma no
padrão `pergunta → corpo → resposta → o que não diz`. As duas interativas **já existem** e
são movidas, não construídas. Único item novo: o esquema estático de 2 painéis do #42.

**Fase C — o fecho.** Parte 3 (tese + autocorreções + limites) e Parte 4 (a oficina
consolidada, D1–D26 em tabela colapsável).

**Fase D — polimento e troca.** Mobile, `prefers-reduced-motion`, cross-browser, a
verificação da §7, e o commit de troca.

---

## 3. Mapa de seções — o contrato do scroll único

IDs são **definitivos** desde a Fase A: o rail, os links internos e a copy dependem deles.

| ordem | ID | parte / perna | copy | peça | dados |
|---|---|---|---|---|---|
| 0 | `p0-hero` | Parte 0 · abertura | BP-0134 § Parte 0 | — | — |
| 1 | `p1-mapas` | Parte 1 · 40 anos no mapa | BP-0134 § 1.1–1.2 | `timeline.js` + régua | `painel_goias.json`, `marcos.json`, 40 WebP |
| 2 | `p1-saldo` | Parte 1 · o saldo | BP-0134 § 1.3-A | 5 cards | `transicoes_resumo.json`, `painel_goias.json` |
| 3 | `p1-fluxos` | Parte 1 · os fluxos | BP-0134 § 1.3-B | `sankey.js` + `matriz.js` | `sankey_data.json`, `transicoes_matriz.json` |
| 4 | `p2-hipotese` | Parte 2 · a dobradiça | BP-2 § abertura | — | — |
| 5 | `p2-perna1` | Perna 1 · o padrão existe | BP-2 § Perna 1 | `marcha-mapa.js` 🎞️ | `marcha_centro_massa.json`, `malha_amc.geojson` |
| 6 | `p2-perna2` | Perna 2 · o mecanismo | BP-2 § Perna 2 | `pastagem-reserva.js` 🎞️ | `idade_pastagem_regional.json`, `_gmm.json`, `_municipal.json`, `malha_amc.geojson` |
| 7 | `p2-perna3` | Perna 3 · o clímax | BP-2 § Perna 3 | esquema 2 painéis **(novo)** | — (SVG inline) |
| 8 | `p2-perna4` | Perna 4 · o teto | BP-2 § Perna 4 + §18 | 2 esquemas SVG **(novos, §18.3)** | — (SVG inline) |
| 9 | `p3-tese` | Parte 3 · o veredito | BP-0134 § 3.1 | callout | — |
| 10 | `p3-autocorrecao` | Parte 3 · a assinatura | BP-0134 § 3.2 | painel 10 + 3 | — |
| 11 | `p3-limites` | Parte 3 · o que não afirma | BP-0134 § 3.3 | lista | — |
| 12 | `p4-oficina` | Parte 4 · a oficina | BP-0134 § Parte 4 | M1–M6 + `inventario.js` | `painel_amc_indice.json` |

*(BP-0134 = `BLUEPRINT_PARTES_0-1-3-4.md`; BP-2 = `BLUEPRINT_PARTE2.md`.)*

---

## 4. Inventário de módulos — reusar, adaptar, aposentar

| arquivo | destino na reforma |
|---|---|
| `timeline.js` | **reusar** — o scroll dos 40 anos vai intocado |
| `marcha-mapa.js` + `marchamap.css` | **reusar** — vira herói da Perna 1 |
| `pastagem-reserva.js` + `reserva.css` | **reusar** — vira herói da Perna 2 |
| `sankey.js`, `mini-sankey.js`, `matriz.js` | **reusar** — já com 7 grupos (#12B) |
| `inventario.js` | **reusar** — a vitrine do painel, na oficina |
| `zoom.js`, `utils.js`, `marcha.js` | **reusar** |
| `router.js` | **aposentar** — fazia o roteamento entre abas; a reforma não tem abas. O hash passa a apontar direto para as âncoras das seções |
| `secoes.js` | **substituir por `rail.js`** — a lógica de "seção ativa por scroll" é reaproveitável quase inteira (ver `avaliar()`); o que muda é o alvo: rail **lateral** em vez da faixa horizontal da régua |
| `tabs.css` | **aposentar** junto com as abas |
| `styles.css` | **reusar** como base; a reforma adiciona `reforma.css` por cima |

**Regra de ouro para o CSS:** nada de editar `styles.css` durante as Fases A–C. Enquanto
o `index.html` estiver no ar, ele e o `reforma.html` compartilham essa folha — mudá-la
altera o site publicado sem querer. As diferenças vivem em `reforma.css`, sob `body.reforma`.

---

## 5. Correções de números no site atual — ✅ aplicadas em 28/jul/2026

A auditoria tinha deixado erros na tela. Como o `index.html` continua no ar durante toda a
construção, **foram corrigidos nele agora** (decisão do autor), além de já entrarem
corrigidos na reforma.

| # | onde | erro | correto | estado |
|---|---|---|---|---|
| 1 | hero | "38 milhões de pontos… 1,5 bilhão de registros" — **10× menor** | **378 milhões** de pixels/ano · **15 bilhões** em 40 anos (34.024.262 ha ÷ 0,09 ha) | ✅ |
| 2 | lede da síntese, teaser da oficina, sumário de Métodos | "as 16 decisões metodológicas" | **26** (D1–D26) — o próprio bloco M5 já listava as 26 | ✅ |
| 3 | cards do Sankey (§2) e §4 | valores da matriz de 6 grupos (4,11 / 2,73) | **4,10 / 2,72** pela recontagem do #12B; entrou um **4º card** (`veg→Mosaico`, 1,00 Mha) com a ressalva do PRODES, e a nota do par que quase se cancela (1,72 ↔ 1,62 Mha) | ✅ |
| 4 | lede da síntese | "avança em três movimentos" | a reforma dissolve os Movimentos; some com a arquitetura nova — **não** se corrige no site antigo | — |

**Um resíduo encontrado ao corrigir o item 3, declarado na tela em vez de silenciado:** o
`<details>` de método compara a matriz líquida (#12) com a soma dos 39 pares anuais (#19,
≈3,83 Mha). O #12B recontou a **primeira** com sete grupos; os **pares anuais do #19 não**
passaram pela recontagem. A comparação virou indicativa, não exata, e o texto agora diz isso.
*(Recontá-los é trabalho de pipeline, fora do escopo da reforma.)*

**Uma exceção à regra do §4 (não editar `styles.css`)**, feita conscientemente: a nota do
Mosaico precisava de um estilo (`.sankey-nota-mosaico`). Como a correção do item 3 é do
**site publicado**, não da reforma, editar `styles.css` era o lugar certo — e a classe nova
não é usada por `reforma.html`, então não há efeito cruzado.

---

## 6. O que **não** entra nesta reforma

Registrado para não reabrir a discussão a cada fase:

- **Repintar a classe 21 nos 40 rasters GEE.** Exigiria reexportar as 40 imagens do Earth
  Engine. A barra empilhada e a legenda já declaram a ausência (§3.7.1 do `IMPLEMENTACAO.md`).
- **Mapa municipal de idade do pasto.** Em resolução fina ele só repintaria o gradiente
  refutado.
- **`idade_pastagem_histograma.json` (por Ato).** Segue exportado e **não consumido** — é o
  eixo temporal suspenso. Decisão registrada, não ponta solta.
- **Rediscutir a periodização.** O pico de KL migrou para 2022 com o #12B, mas a fronteira
  de 2020 vem da triangulação com a âncora imune (soja SIDRA). A oficina **qualifica**; a
  reforma não repropõe atos.
- **`index-Victor-Lapig.html`.** Variante experimental; fora do escopo.

---

## 7. Verificação (roda antes da troca)

1. **Navegação:** rolar do topo ao fim; o rail marca a parte certa em todas as 13 seções;
   clicar em cada item do rail salta para o alvo correto.
2. **Peças interativas:** o scroll dos 40 anos faz cross-fade ano a ano; o mapa da marcha
   anima e o slider responde; o toggle de região da Perna 2 redesenha o histograma; o
   Sankey desenha **7 grupos** com a faixa do Mosaico em ocre.
3. **Console limpo** — zero erros, zero 404 de asset.
4. **Números banidos ausentes do DOM.** Varredura das frases listadas em
   `BLUEPRINT_PARTE2.md` § "Números banidos": `78 mil`, `−88%`, `desloca o peso`,
   `34 de 36`, `16 decisões`, `1,5 bilhão`, `encontra um piso`.
5. **Mobile** (360 px) e **`prefers-reduced-motion`**: o rail colapsa; nenhuma animação
   essencial ao argumento se perde.
6. **Sem regressão no antigo:** `index.html` continua abrindo e funcionando até o commit
   de troca.

---

## 8. Diário de execução

| data | fase | o que foi feito |
|---|---|---|
| 28/jul/2026 | — | blueprints reconciliados com o estado analítico pós-auditorias; este plano criado; estratégia (arquivo paralelo) e primeira fatia (moldura) decididas |
| 28/jul/2026 | **A1–A4 ✅** | `reforma.html` + `assets/css/reforma.css` + `assets/js/rail.js`. Scroll único com Partes 0–4, rail lateral funcional, Parte 0 e Parte 1 completas com a copy nova. Verificado com Playwright (script em scratchpad): 40 steps, rail marca e salta, régua recolhe fora da Parte 1, Sankey de 7 grupos com o Mosaico, console limpo, zero 404, mobile sem overflow, nenhuma frase banida no DOM |
| 28/jul/2026 | **correções no site no ar ✅** | hero 10×, "16 decisões" (3 lugares), cards do Sankey + 4º card do Mosaico. Ver §5 |
| 28/jul/2026 | **B ✅** | As 4 pernas com a copy do blueprint; as duas interativas movidas; esquema da regressão espúria criado. Corrigido o bug de rolagem horizontal no celular — que era do site publicado. Ver §9 |
| 28/jul/2026 | **C ✅** | Parte 3 (tese + 10 autocorreções + 3 verificações + 7 limites) e Parte 4 (oficina consolidada, D1–D26 colapsadas). Ver §10 |
| 28/jul/2026 | **revisão do autor → Perna 1** | leitura parada em "Perna 1 de 4 · O padrão existe?". Duas questões levantadas ali, ambas resolvidas: a ressalva do centro de massa (§12) e a distinção entre "a lavoura nova está no norte" e "o Sul empurrou o Norte" (§13) |
| 28/jul/2026 | **auditoria do #34 ✅** | o bracket D26 aplicado ao pipeline que sustenta a Perna 3; dois blocos robustos, um rebaixado; copy da Perna 3 reescrita. Ver §14 |
| 28/jul/2026 | **revisão do autor → Perna 2 ✅** | leitura aprovada até o fim da "Perna 2 de 4 · Qual é o mecanismo?". A perna foi **reescrita inteira** (estrutura, figura, peça, cards, conclusão) e depois **corrigida de novo** sobre duas questões da própria revisão. Ver §15 |
| 28/jul/2026 | **revisão do autor → Perna 3 ✅** | quatro questões: falta de cuidado vs. Pernas 1–2, abertura desconectada, texto longo e opaco, duas figuras confusas — e a dúvida sobre o overclaim do iLUC, que estava certa. Perna reescrita inteira: 5 `h4`, 2 figuras novas, 1 figura removida, 2 `<details>`, veredito corrigido em **4 lugares** da peça. Ver §16 |
| 28/jul/2026 | **varredura número × CSV ✅** | a §19.4 pedia "dia próprio" — feito sobre a peça inteira. 442 blocos com número extraídos mecanicamente, ~160 rastreados até a fonte. **Nenhuma conclusão cai**; 4 defeitos + 3 imprecisões, todos corrigidos; a legenda do mapa da Parte 1 (D27, item 2) auditada e aprovada. Ver §20 e `Textos/metodologia/auditoria_numeros_tela.md` |
| 28/jul/2026 | **revisão do autor → Perna 4 ✅** | mesmos sintomas da Perna 3 e um defeito pior: **a figura publicada contradizia a manchete** (o PNG do #39 rotulava o resíduo como "efeito-DEMANDA", rótulo que o próprio pipeline retratou). Perna reescrita inteira: 6 `h4`, 2 `<details>`, 4 cards, os **dois PNGs de pipeline removidos** e substituídos por SVG inline; 3 correções de número; 2 fragilidades novas; rótulo consertado na origem (`fronteira_fechando.py`). Ver §18 |

### Dois defeitos encontrados pela verificação da Fase A (e corrigidos)

1. **O salto do rail errava o alvo por ~400 px em distâncias longas.** As peças da
   Parte 1 renderizam de forma preguiçosa (Sankey, mini-Sankeys); num salto de ~30 mil px
   elas entram na viewport *durante* a animação, crescem e empurram o alvo para baixo. O
   `scrollTo` tinha sido calculado com a altura antiga. Corrigido em `rail.js` com uma
   correção pós-assentamento (`aoAssentar`), que reposiciona até duas vezes se o desvio
   passar de 6 px. **Vale para qualquer âncora nesta peça** — não é específico do rail.
2. **Seções curtas acendiam a vizinha no rail.** A régua "seção ativa = a última cujo topo
   passou da linha de leitura" falha quando a seção é mais curta que a distância entre a
   âncora e a linha: clicar na Perna 3 acendia a Perna 4. A linha de leitura passou a ser
   **fixa em pixels, logo abaixo do offset da âncora** (150 px), e a regra virou "a seção
   que **contém** a linha", com o aninhamento resolvido pela ordem do array (a perna vem
   depois da Parte 2, então ganha dela). Com as pernas ainda vazias o efeito é gritante;
   com o conteúdo da Fase B seria sutil e passaria despercebido.

### Item de polimento herdado (não é regressão da reforma)

O título embutido no PNG do mapa (*"Cobertura e Uso da Terra — Goiás 1986"*) fica
parcialmente coberto pelo seletor de camadas. Acontece igual no `index.html` publicado —
é do asset + do overlay, não da reforma. Resolver na Fase D.

---

## 9. Fase B — as 4 pernas (28/jul/2026) ✅

As quatro pernas montadas com a copy do `BLUEPRINT_PARTE2.md`, no padrão
`pergunta → corpo → resposta → o que isto não diz`. As duas peças heroínas foram
**movidas, não reconstruídas**; o único visual novo da reforma inteira é o esquema da
regressão espúria.

| perna | peça | origem |
|---|---|---|
| 1 · O padrão existe? | mapa animado do centro de massa + faixa latitude-tempo | `marcha-mapa.js`, movido |
| 2 · Qual é o mecanismo? | mapa de bimodalidade por AMC + histograma por região | `pastagem-reserva.js`, movido |
| 3 · O Sul empurrou o Norte? | **esquema de 2 painéis da regressão espúria** | SVG inline, **novo** |
| 4 · Por que desacelerou? | figuras de decomposição oferta/demanda e estoque por região | `outputs/`, reusadas |

**Contrato de DOM a preservar** (os dois módulos observam um ancestral *visível*, porque o
bloco que eles montam começa `hidden` e um elemento de área zero nunca intersecta):
`pastagem-reserva.js` procura `#sec-idade-pastagem` — por isso o interativo da Perna 2 fica
dentro de um wrapper com esse id; `marcha-mapa.js` procura `#mov-marcha` e, não achando,
cai no `parentElement`, que na reforma é o próprio bloco da Perna 1 (visível). Mexer nessa
aninhagem quebra as duas peças **em silêncio** — elas simplesmente não montam.

### O bug de rolagem horizontal no celular — era do site publicado, não da reforma

A verificação acusou rolagem lateral em 390 px. Não era regressão: o `index.html` no ar
tinha o mesmo defeito. **Duas causas independentes, ambas o mesmo padrão** — decoração
`position: absolute` invisível que continua entrando na área rolável do documento:

1. `.bar-tooltip` (o resumo da barra empilhada) media ~690 px com `white-space: nowrap`,
   com `opacity: 0`. Corrigido com quebra de linha e teto de largura — o que também
   conserta o caso em que ele fica **visível** no celular, onde transbordava igual.
2. `.termo::after` (o balão do glossário) tem 290 px centrados no termo; num card estreito
   ele escapa pela direita.

O conserto de raiz é `overflow-x: clip` — e ele precisa estar **em `html` e em `body`**:
sozinho, cada um deixa o `scrollWidth` da raiz em 396 contra 390 de viewport. Tem que ser
`clip`, **nunca `hidden`**: `hidden` criaria um container de rolagem e quebraria todo o
`position: sticky` da peça (o mapa dos 40 anos, a régua). Há agora um teste que verifica
justamente isso — que o clip não matou o sticky.

### Uma lição sobre o próprio teste

A varredura de "frases banidas" acusou *"o pasto jovem vem ganhando peso"* na Perna 2. Era
**falso positivo**: a frase aparece dentro do bloco "o que isto **não** diz", que existe
precisamente para nomeá-la e negá-la. O teste passou a excluir `.nao-diz` da varredura —
confundir a afirmação com a sua negação seria punir exatamente a parte mais honesta da
peça. (Antes disso, o mesmo teste tinha acusado "78 mil" dentro de "**3**78 milhões.")

---

## 10. Fase C — o veredito e a oficina (28/jul/2026) ✅

**Parte 3 · O veredito.** Três batidas, na ordem do blueprint: o callout da tese; o painel
de autocorreções; os limites. O painel é o item que mais mudou em relação ao site antigo —
ele passou de 7 itens enterrados no §12 para **10 em destaque**, ordenados da mais severa
para a menor, com o #12B abrindo a lista. Cada linha traz um selo de veredito
(**NÃO** em terracota, **SIM** em verde para o único caso), e a coluna de "NÃO" descendo a
página *é* o argumento — dá para ler de relance.

Abaixo dele, um segundo bloco com tratamento visual distinto: as **três verificações que
não derrubaram nada** (#14B, #22B, #48). A separação entre os dois blocos é deliberada e é
o que torna o painel persuasivo em vez de performático — contar só as auditorias que acham
erro é outra forma de selecionar resultado.

**Parte 4 · A oficina.** Consolidada de sete blocos para quatro, como o blueprint pedia:

| era | virou |
|---|---|
| M1 periodização + o acordeão longo da Parte 1 | **1 · Como os três atos foram detectados** — com a ressalva do pico de KL que migrou para 2022 e a âncora SIDRA que segura a fronteira de 2020 |
| M2 métricas do tempo + M3 camadas de evidência | **2 · As réguas de robustez** — uma peça só, orientada a "como sabemos que sobrevive": as seis réguas e o que cada uma decidiu, mais as três camadas de força |
| M4 vitrine do painel | **3 · O painel: o que medimos** — intocado (`inventario.js`) |
| M5 decisões | **4 · As vinte e seis decisões** — os 26 cards agora vivem dentro de um `<details>` fechado. São referência, não leitura corrida |
| M6 limitações · M7 glossário | mantidos como estão |

O DiD ganhou uma nota própria na tabela de camadas: as quatro políticas testadas são
**federais**, sem grupo não-tratado, então a camada foi rebaixada de evidência causal para
*sensibilidade de co-movimento* (#23). É o que justifica os pinos da régua aparecerem como
contexto e nunca como motor.

### O que a importação dos blocos antigos trouxe de errado

Os blocos M5/M6/M7 foram trazidos quase verbatim — e vieram com **oito referências
cruzadas mortas**: "Narrativa § 9", "§ 6", "§ 11", que existiam quando a peça tinha doze
seções numeradas e duas abas. Reescritas para o vocabulário novo (Perna 1–4, Parte 3).
**Lição de processo:** reaproveitar HTML de uma arquitetura para outra carrega as
referências da arquitetura antiga, e elas não quebram nada visivelmente — só apontam para o
nada. A verificação passou a checar isso (`ancoras: dup / quebrados`).

### A varredura de frases banidas precisou de uma regra, não de mais exceções

Depois do `.nao-diz` da Fase B, a Fase C trouxe mais casos: o card da **D26** cita o
"−88%" para dizer que ele caiu, e a tabela de réguas cita o gradiente de idade pelo mesmo
motivo. A regra que fechou o assunto: **a lista guarda contra *reafirmar* um achado que
caiu; texto que *narra* a queda é o oposto disso.** Ficam fora da varredura, por classe
explícita: `.nao-diz`, `.nota-honestidade`, `.autocorrecoes`, `.verificacoes-ok`,
`.decisoes-corpo` e `.regua-decidiu`. Sem essa regra, o teste passaria a premiar quem varre
o próprio erro para debaixo do tapete — exatamente o contrário do que a peça defende.

---

## 11. Estado atual e o que falta — Fase D

**A construção está completa: Fases A, B e C ✅.** As Partes 0 a 4 existem em
`Visualizacao/reforma.html`, a verificação da §7 passa, o console está limpo e o
`index.html` publicado continua no ar, intocado e agora com os três números corrigidos (§5).
Nada aqui está pela metade — o que falta é **aceite**, não construção.

### 11.1 A revisão do autor — em curso, a Parte 2 inteira lida

> **Onde a leitura está (28/jul/2026):** o autor leu do hero até o fim da
> **"Perna 4 de 4 · o teto"** — a Parte 2 inteira. Questões levantadas: duas na Perna 1
> (§12 e §13), quatro na Perna 2 (§15), quatro na Perna 3 (§16) e quatro na Perna 4
> (§18) — **todas resolvidas**. **As Partes 3 e 4 ainda não foram lidas.**

Isso importa registrar porque **a leitura é o critério de aceite da §1** — nenhum teste a
substitui, e ela é a única coisa que hoje separa a peça da troca. Vale notar o que a
revisão parcial já produziu: as duas questões da Perna 1 não eram ajustes de copy, eram
**um problema conceitual** (a deriva do Mosaico no centroide) e **um risco de leitura
errada** (confundir co-expansão com deslocamento). A primeira virou figura nova e uma
correção em `marcha-mapa.js` que também alcançou o site publicado; a segunda virou parágrafo
distinguindo as duas afirmações; e a conversa sobre a segunda **descobriu uma auditoria que
faltava** (§14).

A leitura da Perna 2 confirmou o padrão e subiu a aposta: rendeu **uma reescrita estrutural,
uma figura nova, uma peça reprojetada, dois achados analíticos inéditos e uma correção de
overclaim** (§15). Duas das quatro questões do autor eram defeitos de fundo que nenhum teste
automatizado pegaria — uma delas, a diferença de forma entre regiões, foi vista **a olho** num
gráfico. **A Fase D não é formalidade: é o instrumento de auditoria mais produtivo do projeto
até agora.** Duas pernas de leitura já renderam sete commits e três correções de conteúdo.

A leitura da **Perna 3** manteve o padrão e encontrou o defeito mais sério até agora — um
**overclaim que contradizia a própria página** duas telas adiante (§16).

### 11.2 O que falta

1. **Terminar a leitura** — as Partes 3 e 4 (o veredito e a oficina). ⏳ *bloqueia a troca*
2. **Fechar o item restante da D27** (§19): o `deslocamento_latitude.png` da Perna 1 contradiz a
   ressalva que o interativo logo acima carrega. ⏳ *bloqueia a troca*
   ~~e a legenda de classes do mapa da Parte 1 nunca foi auditada~~ → **auditada e aprovada em
   28/jul (§20.4)**: ela declara a ausência do Mosaico em três lugares, um deles texto visível.
3. **Polimento:** o título embutido nos PNGs do mapa coberto pelo seletor de camadas (§8);
   revisar a Parte 1 em 360 px; conferir `prefers-reduced-motion` nas duas interativas.
4. **A troca:** `reforma.html` → `index.html`, o antigo para
   `docs/_arquivo/index-pre-reforma.html`, num commit só. Depois disso, `router.js`,
   `secoes.js` e `tabs.css` ficam órfãos e podem sair.
5. **Reconciliar o `IMPLEMENTACAO.md`**, que descreve o site em abas — ele vira registro
   histórico no momento da troca.

---

## 12. A ressalva do centro de massa na Perna 1 (28/jul/2026)

Levantada pelo autor na revisão da Perna 1, e é a última ponta conceitual da reforma: o
centroide da agricultura pondera pelo **estoque** `lulc_agricultura_ha`, que subconta a
conversão migrada para "Mosaico" (#28D/D25). A peça interativa **mostra** a linha achatando
depois de 2019 — deixar sem anotação convidaria a leitura "a agricultura parou em 2020",
que o trabalho abandonou.

**O que se descobriu ao medir, e que decidiu o desenho:** na janela 2019→2024, quatro
medidas dizem ~+10 a +13 km ao norte (pastagem +12,9; rebanho SIDRA +11,9; soja SIDRA
+10,1; ∪mosaico +4,4) e **só a exposta diz zero** (+0,5). Duas das quatro são **imunes** ao
classificador. Além disso, a pastagem e o rebanho concordarem fecha empiricamente a dúvida
sobre a perna que sobe — se o `pasto→Mosaico` a distorcesse, ela divergiria da medida imune.

**Implementado:**
1. Figura **"cinco medidas, uma discorda"** (SVG inline), mesma forma retórica do esquema
   do #42 na Perna 3.
2. Card da agricultura mantém **+65 km** (comparável a pasto/rebanho pela mesma régua) com
   a âncora imune declarada: soja SIDRA **+48 km**.
3. `marcha-mapa.js`: trecho da agricultura a partir de 2019 vira **pontilhado**, com nota
   na legenda (`ANO_ROTULO_DERIVA`). Vale para o `index.html` também — lá o texto já
   trazia a ressalva, mas a figura não.
4. `<details>` explicando por que a união **não** é régua de 40 anos.

**A armadilha que ficou documentada na tela.** Sob `agric ∪ mosaico` os 40 anos dão
**−60 km — para o sul**. O número é real e está no CSV, mas o Mosaico de 1985 (3,63 Mha,
10,7% do estado, ao norte) é **outro objeto** que o de 2024: a conta mede o Mosaico antigo
se dissolvendo, não a lavoura recuando. A união é teto de janela curta. Alguém vai fazer
essa conta, então a peça a faz primeiro.

**E o ativo:** a massa reetiquetada aterrissa **+46,5 km ao norte** da agricultura visível,
com r=0,84 contra o crescimento da soja SIDRA por AMC. **O erro de medida aponta contra a
tese** — a régua crua faz a marcha parecer mais fraca do que foi. Como o #44 formula: não é
a soja que recuou ao sul, é o rótulo "Soja" que perdeu a soja nova.

---

## 13. "A lavoura nova está no norte" ≠ "o Sul empurrou o Norte" (28/jul/2026)

Segunda questão levantada na mesma revisão da Perna 1, e é de **arquitetura do argumento**,
não de número: a Parte 2 abre dizendo que a explicação óbvia — a lavoura empurrando o pasto
para o norte, um iLUC intra-estadual — **está errada**. A ressalva do centro de massa (§12)
acabara de mostrar que a agricultura *também* marchou para o norte. Parece contradição.

**Não é, e a distinção é o coração da Perna 3.** "A lavoura nova está no norte" é uma
afirmação sobre *onde a expansão aconteceu*. "O Sul empurrou o Norte" é uma afirmação sobre
*causa entre lugares* — exige que a expansão no Sul **preceda e desloque** a do Norte. As
duas culturas subindo o mapa **ao mesmo tempo** é co-expansão sob um drive comum, e
co-expansão é justamente o que o spillover negativo do #34 descreve. A ressalva **reforça**
a refutação em vez de arranhá-la.

A copy, porém, convidava a confusão: ela dizia que a explicação óbvia está errada sem dizer
*qual parte* dela está errada. Corrigido com um parágrafo que separa as duas afirmações
antes de derrubar a segunda. **Lição de escrita:** quando uma seção anterior mostra um fato
que *parece* apoiar a hipótese que a seção seguinte derruba, o texto tem que nomear a
semelhança e desfazê-la — o leitor não vai fazer isso por conta própria.

---

## 15. A revisão da Perna 2 — o que ela encontrou (28/jul/2026)

A leitura da Perna 2 levantou quatro questões. Nenhuma era de estilo; três eram defeitos e
uma era uma pergunta que virou análise nova.

**1. A perna abria afirmando uma diferença regional e fechava negando-a.** Não era
contradição — são registros diferentes (a geografia separa *qual transição*, não *as duas
populações de pastagem*) —, mas a distinção chegava como surpresa no fim. Virou a espinha:
cinco movimentos, com a distinção declarada no segundo parágrafo.

**2. A figura não correspondia ao texto.** A antiga era organizada por Ato, e a própria
legenda pedia para não ler variação entre atos — o eixo que a estruturava era o que o texto
desautorizava. Substituída por `sintese_idade_duas_populacoes.png`: um painel mostra o
ajuste de **uma** população falhando sobre o dado bruto, outro mostra a mesma divisão sem
modelo nenhum (composição por origem).

**3. "Bimodalidade" não era visível — e o site afirmava que era.** Verdade: no agregado a
curva tem **um pico e um ombro**, não dois picos. A copy parou de fingir o contrário e passou
a explicar por quê (σ≈7,5a contra 1,6a: população larga vira platô). O `28_idade_pastagem.md`
já registrava isso desde antes ("use a figura do #28C, não o histograma global") — a
prancheta sabia, a tela não.

**4. A peça pedia clique por AMC quando a análise é por mesorregião.** O contorno dissolvido
das 5 mesorregiões passou a ficar **sobre** as 166 AMCs e a receber o clique.

### 15.1 O que a revisão descobriu depois — dois achados novos

**(a) "O desenho não muda" era FALSO na régua que a peça desenhava.** O autor notou a olho
que Norte e Noroeste pareciam mais bimodais. Medido (`forma_regional_bimodalidade.py`):
sob `pasto→agricultura` o vale do Noroeste tem profundidade **0,415**, o do Norte **0,271**,
e Sul e Leste **não têm vale**; a distância entre formas separa as regiões em dois blocos
(TV entre blocos 0,18–0,23 contra 0,05–0,09 dentro). Sob a união tudo colapsa (TV Sul×Norte
**0,223 → 0,023**). A peça desenhava a régua exposta enquanto o texto afirmava a conclusão
da união — **a mesma classe de defeito de quando o mapa pintava a amostra sob manchete de
censo**. Corrigido: a peça oferece as duas réguas, imune por padrão, e a troca virou o beat
mais didático da perna.

**(b) O fio do crédito foi fechado** (`duas_logicas_bracket_fluxo.py`). Δ SICOR × idade
**sobrevive à união e se fortalece** (+0,22 → +0,30) — não é artefato de rotulagem, ao
contrário do gradiente latitudinal. Mas só existe com os anos recentes dentro (≤2019 dá
~zero nas duas réguas), tem sinal invertido e não tem mecanismo.

**(c) Duas correções de linguagem que eram de conteúdo:** "giro de lavoura" era termo
inventado (virou "pasto de ciclo curto", com a ressalva de que é compatível com ILP sem
prová-la) e "plantio direto = proxy de ILP" é frouxo demais — é conservação de solo, e o
Censo Agropecuário **não tem** variável de ILP.

### 15.2 A quinta questão — o eixo do tempo, que virou beat novo

A pergunta final da revisão foi *"a bimodalidade não tem a ver com os atos? não tinha algo
de se sustentar só no Ato III?"*. Medida, a resposta **fortalece** a perna — e o autor pediu
que entrasse na tela. Entrou como o movimento **"Segundo eixo: e se forem apenas épocas
diferentes?"**.

O ganho não foi só o resultado: foi **descobrir que a perna tinha uma simetria escondida**.
A objeção "isso é só composição" tem duas versões — regiões somadas e épocas somadas — e a
perna só respondia uma. Agora as duas viram um par declarado ("Primeiro eixo" / "Segundo
eixo"), a objeção é levantada logo depois da figura, e o movimento seguinte passa a ser
*"Se não é a região **nem a época**, o que decide a idade do pasto?"*.

**O conteúdo** (registrado em
[`28C_bimodalidade_regional.md`](../../Textos/pipelines/28C_bimodalidade_regional.md)):
dentro de cada ato isoladamente a coexistência se sustenta em **10/10** células região×ato
sob a régua imune (9/10 na estrita — falha Noroeste × Ato II por peso). O **Ato I é unimodal
em toda parte por razão estrutural**: até 2000 o horizonte não permite existir pasto com mais
de 15 anos, então a população velha é *inobservável* ali, não ausente — e é por isso que a
contagem começa no Ato II. A tela declara isso, e o "não diz" ganhou a contrapartida: nem o
Ato I unimodal significa que a reserva surgiu depois, nem o vale mais fundo no Ato III
significa que os grupos estejam se separando. Nos dois casos lê-se a janela, não o
território.

**Dívida técnica que veio junto:** a peça ganhou a primeira `<table>` do projeto, e não havia
estilo de tabela em lugar nenhum. `.tabela-compacta` ficou em `reserva-perna2.css` — escopo
da reforma, sem alcançar o `index.html` no ar. Na troca, promover para `styles.css`.

## 14. A auditoria do #34 — encontrada por uma pergunta da revisão (28/jul/2026)

A conversa da §13 expôs uma lacuna real: o **#34** (lead-lag + SLX, a espinha da Perna 3)
pondera por `lulc_agricultura_ha` e `agricultura_delta_mha`, exatamente as variáveis que a
deriva do Mosaico contamina — e a **varredura de alcance da D26, de 23–25/jul, não o
alcançou**. A manchete "θ=−0,16, p=0,02, é ele que refuta" estava sendo publicada sem passar
pelo bracket.

Auditado por `scripts/deslocamento_bracket.py`, que **importa** a maquinaria do #34 (não a
altera) e roda 3 réguas × 2 janelas × 2 desfechos. O companheiro **reproduz o original**
antes de bracketá-lo (Granger p=0,971; θ=−0,1572, p=0,0204), o que valida o arranjo.

| bloco | veredito | evidência |
|---|---|---|
| **Temporal** (Granger/CCF) | **robusto** | 0/24 células com p<0,05; menor p = 0,078. O pico da CCF troca de sinal e de defasagem conforme a régua (lag −1 / 0 / +4) — precedência que depende da régua é assinatura de co-tendência espúria, o #42 por outro caminho |
| **Substituição local** (β) | **robusta, e reforçada** | β<0 em 12/12, p<0,001; **cresce** sob a união (−0,52 → −1,14) |
| **Spillover direcional** (θ) | **sinal robusto, significância NÃO** | θ<0 em **12/12** — o θ>0 que a hipótese exige nunca aparece —, mas p<0,05 em **1/12**, e essa uma é a régua exposta na janela plena (união p=0,545; SIDRA p=0,526) |

A defesa óbvia ("a união só acrescenta ruído e atenua tudo") foi testada e **não se
sustenta**: a mesma régua *dobra* o termo local. Régua que fortalece um canal e apaga o
outro não age como ruído puro.

**Consequência para a Perna 3.** A refutação **permanece** — nenhuma especificação, em régua
nenhuma, produz a assinatura do deslocamento causal. Mas passa a se apoiar em **dois blocos
robustos + a ausência universal de θ>0**, não num p=0,02. A copy ficou **mais forte**: em vez
de "há um efeito significativo na direção contrária", diz "o coeficiente é negativo nas doze
especificações testadas" — não há p-valor para a banca contestar. É o mesmo trade do #54 na
Perna 4: menos significância, mais defensabilidade.

**Frase banida a partir daqui:** *"o spillover é significativo e é ele que refuta"*.
Propagado nos sete endereços (índice lógico, narrativa, ensaio, guia de leitura, tabela de
vereditos da D26, `BLUEPRINT_PARTE2.md` e `reforma.html`); o pipeline `#34` traz a seção de
auditoria e a Limitação antiga riscada.

---

## 16. A revisão da Perna 3 — o overclaim que a própria página desmentia (28/jul/2026)

A leitura da Perna 3 levantou quatro questões. Três eram de forma e uma era de fundo — e a
de fundo é a correção de conteúdo mais séria da reforma até aqui.

### 16.1 "Não parece ter tido o mesmo carinho que as Pernas 1 e 2" — e não tinha

Não era impressão. Medido contra as duas pernas já aprovadas, a Perna 3 tinha **quatro
parágrafos corridos**, nenhum `h4`, nenhum card, nenhum `<details>` — enquanto a Perna 1 tem
2 subtítulos + 4 cards + 2 `details` e a Perna 2 tem 4 subtítulos + 2 cards + 3 `details`.
A perna anunciada como **o clímax** era a menos estruturada da peça. Reescrita no mesmo
padrão: **cinco `h4`** (o que precisaria aparecer → a assinatura que não aparece → a ponta
solta → quem dá o compasso → o teste de simetria), **três cards**, **dois `details`**.

### 16.2 A abertura estava desconectada — e o gancho já existia, sem uso

A pergunta era *"Então foi a lavoura do Sul que empurrou o pasto e o boi para o Norte?"*. O
"Então" prometia uma ligação que o texto não fazia: a Perna 2 termina em duas populações de
pastagem e resolução de talhão, e a Perna 3 abria num assunto novo.

O gancho estava documentado desde o §13 — *"a lavoura nova está no norte" ≠ "o Sul empurrou
o Norte"*, com a nota de que "a distinção é o coração da Perna 3" — e nunca tinha sido
usado **dentro** da perna. Agora a pergunta é **"O pasto que o Sul perdeu é o pasto que o
Norte ganhou?"** e a abertura *monta* a hipótese a partir dos dois achados anteriores (tudo
subiu ao norte; cada metade faz uma conversão diferente) antes de derrubá-la — inclusive
nomeando o defeito lógico: **coincidência no espaço não é mecanismo**; dois processos
independentes sob a mesma força desenham o mesmo mapa.

### 16.3 As duas figuras: as duas eram sobre a mesma nota de rodapé

O diagnóstico foi desconfortável. A perna tinha duas figuras — o esquema SVG do #42 e o
`veredito.png` — e **as duas eram sobre o Granger reverso ser espúrio**, que é uma ponta
solta metodológica, não a manchete. O argumento principal (*a assinatura do empurrão não
aparece em 12 especificações*) **não tinha figura nenhuma**. Estava exatamente invertido.

Além disso o `veredito.png` é figura de pipeline, não de leitor: eixo em −log₁₀(p), rótulos
`Pasto_N → Agric_S`, "Granger ingênuo", "Toda-Yamamoto", "I(2)".

**Resolvido assim:**

| figura | destino |
|---|---|
| `veredito.png` (#42) | **removida** — vira `<details>` "como se prova que uma precedência é espúria", em três passos e sem jargão |
| esquema SVG do #42 (2 painéis) | **mantido**, agora sob o seu próprio `h4` — é a peça-modelo e continua sendo o único visual novo herdado da Fase B |
| **as 12 especificações** (novo, SVG inline) | a manchete finalmente ganha figura: 12 pontos, todos negativos, e a **faixa positiva que a hipótese exige pintada e vazia** |
| **o teste de simetria** (novo, SVG inline) | era um parágrafo; vira barras — crédito 69 km, lavoura 135 km, armazenagem 152 km **ao sul** da fronteira, e a faixa "se puxassem, estariam aqui" vazia |

A figura das 12 especificações carrega um segundo argumento de graça, que o texto sozinho
não entregava: as maiores magnitudes estão na **régua exposta** e encolhem para perto de
zero nas duas limpas — ou seja, o pouco que havia de sinal dependia do rótulo. É a auditoria
do §14 renderizada.

### 16.4 O overclaim do iLUC — a questão que estava certa

O autor perguntou se "conseguimos provar isso mesmo". **Não, e a página já sabia disso.**

A Perna 3 dizia *"a hipótese de deslocamento causal foi testada e **refutada**"*. Duas telas
adiante, a Parte 3 listava, entre as fragilidades: *"iLUC intra-estadual: **não confirmado,
não refutado em absoluto**"*. A peça se contradizia — e a versão forte é a que aparecia
primeiro, em negrito, no veredito.

O pipeline nunca sustentou "refutada". O [#34](../../Textos/pipelines/34_deslocamento_espacial.md)
registra nas limitações que o teste espacial é **local e contemporâneo** e "não descarta
deslocamento de longo alcance ou de defasagem muito longa"; a simulação de poder dá **~48%**
para um efeito temporal moderado (e ~93% para um grande). O que existe é forte, mas é outra
coisa: **a assinatura prevista nunca aparece, e a rival aparece sempre**.

**Corrigido em quatro lugares da peça** — porque corrigir só a Perna 3 deixaria a
contradição de pé no sentido inverso:

| onde | era | ficou |
|---|---|---|
| hero (`p0-hero`) | "é boa demais para ser verdade" | "não resiste ao teste" |
| dobradiça (`p2-hipotese`) | "**E está errada.**" | "**E ela não sobrevive ao teste.** Procurada em trinta e seis recortes, a marca que essa história exigiria não apareceu em nenhum" |
| veredito da Perna 3 | "testada e refutada" | "a assinatura … não aparece em nenhum dos doze recortes espaciais nem dos vinte e quatro temporais" |
| tese da Parte 3 (`p3-tese`) | "testada e **refutada**" | "testada em trinta e seis recortes, e **a assinatura que ela exige não apareceu em nenhum**" + link para os limites |

E o "o que isto não diz" saiu de um parágrafo para **cinco**, com o primeiro dedicado
exatamente à leitura errada mais provável: *que o iLUC não existe*. Inclui o que
deliberadamente **não** foi testado — canal de longo alcance, defasagem longa, e sobretudo
qualquer canal que **atravesse a divisa de Goiás**, que é uma pergunta legítima e aberta.

Somou-se um `<details>` novo — *"o que este teste descarta · e o que ele não alcança"* —
que separa as duas colunas explicitamente. Numa conclusão negativa é a seção que a banca vai
abrir primeiro; melhor que ela já esteja escrita.

### 16.5 A lição, que vale para o resto da leitura

**Um veredito em negrito não pode ser mais forte que a linha correspondente na lista de
fragilidades.** As duas foram escritas em momentos diferentes, por bons motivos cada uma, e
ninguém as leu lado a lado — foi preciso um leitor atravessando a peça inteira para notar.
Vale varrer isso nas Pernas 1, 2 e 4 antes da troca: para cada afirmação forte, existe uma
entrada em `p4-limites` que a contradiz?

E a troca não enfraqueceu a perna. **Mudou o tipo de argumento**: sai um veredito apoiado em
p-valor, entra um apoiado em **especificidade** — previsão arriscada, procurada em 36
recortes com placebos direcionais e três réguas independentes (uma delas medida em campo,
fora do satélite), nunca encontrada, enquanto a explicação rival aparece em todos. É o
terceiro lugar em que este projeto troca um número bonito por um argumento mais difícil de
derrubar, depois do [#54](../../Textos/pipelines/54_defensabilidade_perna4.md) na Perna 4 e
da própria auditoria do #34 (§14).

**Arquivos tocados:** `reforma.html` (Perna 3 inteira + 3 correções pontuais),
`assets/css/reforma.css` (blocos `.assinatura` e `.simetria`), `docs/BLUEPRINT_PARTE2.md`
(seção da Perna 3 marcada como registro histórico + veredito novo).

---

## 17. A varredura "afirmação forte × lista de limites" (28/jul/2026)

Pedida pelo autor logo depois da §16, e pelo motivo certo: se o overclaim do iLUC nasceu de
duas seções escritas em momentos diferentes e nunca lidas lado a lado, o mesmo poderia estar
acontecendo nas outras pernas. Estava. **Cinco defeitos**, dois deles contradições diretas.

### 17.1 O que foi cruzado

Toda afirmação forte das Pernas 1, 2 e 4 (`bloco-pergunta`, `bloco-resposta`,
`destaque-inline`, os `dado-choque`) contra as **duas** listas de limites da peça — a curta
da Parte 3 (`p3-limites`, 7 itens) e a longa da Parte 4 (`p4-limites`, 11 itens) — e contra
as limitações registradas nos pipelines de origem.

### 17.2 Os cinco defeitos, corrigidos

| # | defeito | onde | correção |
|---|---|---|---|
| 1 | **Perna 4 contradizia a Perna 1** — a pergunta dizia *"a lavoura do Sul desacelera"*, exatamente a leitura que o "não diz" da Perna 1 retira como artefato de rótulo (e que o corpo da própria Perna 4 desmente três linhas abaixo, com a soja SIDRA +38%) | `p2-perna4` | pergunta vira *"o Sul quase para de abrir terra nova"*, e a perna abre **nomeando** a distinção: o que freou é o `veg→pasto`, medida imune |
| 2 | **A fragilidade F3 citava a Perna 1** para "a freada da agricultura no Sul" — claim que a Perna 1 explicitamente não faz | `p4-limites` | glosa reescrita sobre a abertura de terra nova, com aviso de objeto e link para a Perna 1 |
| 3 | **"não converte em bem-estar"** — frase que o #51 proíbe por escrito ("IFDM ≠ bem-estar amplo"; "o IFDM subiu em toda parte: frasear sempre em ganho relativo/nível"). A peça sugeria que a fronteira não se desenvolveu; o que os dados dizem é que ela **ganhou no mesmo ritmo do Sul e não fechou o vão** | `p2-perna4` (corpo + card) | reescrito em ganho relativo, com o IC do nível (−0,083 [−0,108; −0,058]) no card e um parágrafo novo no "não diz" |
| 4 | **F2 defendia o drive comum na base errada** — "câmbio e crédito *antecedem* as inflexões", quando o #37 registra ~7 acertos em ~135 testes, nada sobrevivendo à multiplicidade, e a **D16** (pós-#42) proíbe ler precedência de Granger em série agregada como causa | `p4-limites` | reescrita: o que sustenta o câmbio é replicação em construções independentes + especificidade, com o p honesto ≈0,07–0,13 |
| 5 | **164 × 166** — F4 citava "164 unidades com conversão" (número **pré-D26**, régua estrita) enquanto a Perna 2 diz "todas as 166" (régua imune, a do mapa). Os dois estão certos, em réguas diferentes, e a peça não dizia isso | `p4-limites` + `p2-perna2` | as duas passam a declarar a régua: **162/164** na estrita, **166/166** na imune |

O defeito 5 é o mais instrutivo: **nenhum dos dois lados estava errado**. A D26 passou por
um e não pelo outro, e o resultado é uma peça que se contradiz numericamente sem que ninguém
tenha escrito nada falso. É o custo de propagação parcial, e já mordeu este projeto três
vezes.

### 17.3 Gaps que ficam (decisão do autor, não corrigidos)

1. **Seis fragilidades órfãs.** F5 (DiD 2012/2018), F6 (Mato Grosso é controle imperfeito),
   F7 (R² *within*), F8 (Moran's I), F9 (aceleração autocorrelacionada) e F10 (N=11 nas
   correlações UF com SICOR) são limites de análises que **não sustentam nenhuma afirmação**
   nas Partes 1–3 da peça reformulada. "Mato Grosso" aparece na página **uma única vez: no
   próprio limite** — o leitor encontra a ressalva sem nunca ter visto a análise.
   Duas saídas: agrupá-las sob um rótulo do tipo *"limites das análises da oficina"*, ou
   retirá-las da lista publicada e deixá-las no pipeline. **Não fiz nem uma nem outra** —
   tirar limite da tela é decisão de autor, não de edição.
2. **F10 tem risco ativo de confusão.** "Correlações UF com SICOR servem para narrativa, não
   para inferência" (N=11, nível **estado**) pode ser lido como se derrubasse o achado de
   crédito da Perna 2, que é **municipal** e sobrevive a controle espacial, FDR e troca de
   régua. São análises diferentes. Uma oração resolve, se a fragilidade ficar.
3. **O carbono ganhou caveat na perna, não na lista.** Densidades Tier 1 de literatura (não
   medidas em GO), biomassa aérea+radicular **sem carbono de solo** — agora está no "não diz"
   da Perna 4, mas não há entrada correspondente em `p4-limites`.

### 17.4 A regra que sai daqui

**Toda afirmação forte precisa de dono na lista de limites, e todo limite precisa de uma
afirmação viva a que se refira.** As duas direções falham: a §16 achou um limite mais fraco
que o veredito (iLUC), e a §17 achou limites apontando para pernas que mudaram (F2, F3),
números de antes de uma decisão metodológica (F4/D26) e seis limites sem claim nenhum.
Vale refazer esta varredura **imediatamente antes da troca** `reforma.html → index.html`,
porque a Parte 3 e a Parte 4 ainda não foram lidas pelo autor.

---

## 18. A revisão da Perna 4 — a figura que dizia o contrário do texto (28/jul/2026)

Quatro questões do autor, e o mesmo padrão da §16: **nenhuma era de estilo**. A queixa foi
"não tem o mesmo carinho, as imagens não casam com a análise, e a conclusão parece forte
demais para não ser verificada". As três estavam certas, e a segunda escondia o defeito mais
grave encontrado na reforma até aqui.

### 18.1 "Não tem o mesmo carinho" — medido, era 29% de uma perna

A mesma medição da §16.1, agora com três pernas aprovadas como referência:

| perna | `h4` | `<details>` | figuras | cards | tamanho |
|---|--:|--:|--:|--:|--:|
| 1 · o padrão existe | 1 | 2 | 4 + 1 SVG | 4 | 15,4k |
| 2 · o mecanismo | 5 | 3 | 3 | 2 | 27,4k |
| 3 · o clímax | 5 | 2 | 3 + 4 SVG | 3 | 27,3k |
| **4 · o teto (antes)** | **0** | **0** | **2** | 3 | **7,8k** |
| **4 · o teto (agora)** | 6 | 2 | 2 SVG | 4 | 27,6k |

A perna que carrega **quatro pipelines** (#39, #46, #47, #51) — mais que qualquer outra —
era a menor da peça, com sete parágrafos corridos, nenhum subtítulo e nenhum `<details>`.

### 18.2 A figura contradizia a manchete — e o pipeline já sabia

O `decomposicao_oferta_demanda.png` decompõe a mudança do fluxo de conversão em
`Δfluxo = h̄·Δestoque + estoque̅·Δhazard` e rotulava as duas barras **"Efeito-OFERTA"** e
**"Efeito-DEMANDA"**. No Sul, a barra da "demanda" é a grande (−0,0047 de −0,0056) e a da
"oferta" é a pequena (−0,0010). Ou seja: **a figura publicada sob a manchete "não foi a
demanda, foi a oferta" mostrava a demanda explicando 83% da freada.**

O rótulo estava errado, e o próprio #39 **já o havia retratado** — a "Ressalva de rótulo"
do §3 diz, literalmente, que a coluna se chama *efeito-residual* "justamente porque **não**
é demanda pura medida". A prancheta corrigiu; a figura, não. **Consertado na origem**
(`scripts/fronteira_fechando.py`: rótulo, cor e título), para não reincidir na próxima
rodada — mesma classe de dívida da §15.3 ("a prancheta sabia, a tela não").

### 18.3 As duas figuras eram de pipeline, não de leitor

Diagnóstico idêntico ao do `veredito.png` na §16.3, e a mesma solução. O
`estoque_por_regiao.png` plotava Mha absolutos, com "def. refinada" no eixo — e como o Sul
**sempre** foi a menor das três regiões, a curva dele fica embaixo o tempo todo e a
afirmação do texto ("no Sul o estoque está em ~53% do que era") é **invisível** no gráfico
que a acompanha.

| figura | destino |
|---|---|
| `decomposicao_oferta_demanda.png` | **removida** — vira SVG inline com o resíduo em **cinza** (cinza é a cor do que não foi identificado, que é o que a barra contém) e a nota "83% do freio está na taxa, não no estoque" **dentro** da figura |
| `estoque_por_regiao.png` | **removida** — vira SVG inline **normalizado a 1985 = 100%**, onde as trajetórias se separam: o Sul é o único que cruza os 60% (em 2005) e achata em 53% depois de 2019, contra Centro e Norte ainda descendo juntos |

### 18.4 A verificação da conclusão — ela era forte demais, e agora é mais forte

A dúvida do autor ("parece forte, precisa conferir se é isso mesmo") estava certa. A
resposta dizia *"é o estoque de Cerrado convertível se esgotando"*, e a decomposição atribui
ao estoque **17%** do freio do Sul. Se o argumento dependesse daquela barra, cairia.

Ele não depende — mas a peça nunca tinha dito de que ele depende. Agora diz, e em voz alta:
a leitura de oferta se sustenta por **eliminação** (a demanda estava no pico; a Proteção
Integral é desprezível) e pelo **teste da taxa plana** (a taxa de conversão não cai com a
depleção nas 166 unidades, p=0,48 — logo o fluxo acompanha o estoque). O 17%/83% está no
corpo, na legenda da figura, no "não diz" **e** virou fragilidade própria em `p4-limites`.

**E a verificação achou o beat que faltava.** O teste que fecha a questão não é o do estado,
é o do próprio Sul: no Ato III sulista, `pasto→(agric∪mosaico)` sobe **+51%** e a soja
plantada sobe **+244%**, enquanto o `veg→pasto` cai **−49%**. O Sul não perdeu apetite por
terra — **trocou a fonte**, do Cerrado para o pasto já aberto. Estava no #33/#39 desde a
auditoria da D26 e nunca tinha chegado à tela. É o argumento mais limpo da perna e não
custou dado novo.

### 18.5 A pergunta da perna tinha uma premissa falsa

"Por que a **marcha** desacelerou?" — ela não desacelerou. O fluxo de conversão de Goiás vai
de **0,071 a 0,072 Mha/ano** do Ato II para o III. Caiu 37% no Sul e **subiu** no Centro e no
Norte: mudou de endereço, não de velocidade. O #39 diz isso no veredito ("a fronteira
**migrou**, não fechou") e o corpo antigo até repetia — três parágrafos **depois** de a
pergunta ter afirmado o contrário. A perna agora abre corrigindo a própria pergunta, e ganha
com isso o beat de abertura que lhe faltava (§16.2: o mesmo remédio).

### 18.6 Três correções de número

| # | onde | era | ficou |
|---|---|---|---|
| 1 | corpo + card do IFDM | "entre 2013 e **2023** a área cultivada +93%" | **2013→2021** — a janela de crescimento do #51 para no lag do IBGE para VA agro e área; só o *nível* de IFDM alcança 2023 |
| 2 | corpo + card da proteção | "**97%** desprotegido" | **94–97%** — 97% pelo proxy vetorial (D17), **94,3%** no refino pixel a pixel que o #46 fez no GEE. Publicar só o número do proxy quando existe a régua melhor é o inverso da disciplina do bracket D26 |
| 3 | carbono | só o total (~973 Mt) e a composição por formação | \+ a **cronologia**, que é o que interessa a esta perna: **80% (774 Mt) saiu no Ato I**, no Sul, e o centroide da emissão marcha **+98 km ao norte**. "O grosso do dano já estava pago antes de a marcha ser notada" |

### 18.7 Duas fragilidades novas (a regra da §17.4 aplicada à perna nova)

A perna reescrita faz afirmações que a lista de limites não cobria. Entraram em `p4-limites`:
**"o teto de oferta é lido por eliminação, não medido"** (o 17%/83% com dono) e **"o custo de
carbono é de literatura, não medido em campo"** (Tier 1, sem carbono de solo — o gap que a
§17.3 tinha registrado e deixado em aberto; ampliar o claim de carbono obrigou a fechá-lo).

### 18.8 A lição

**Uma figura de pipeline publicada sem revisão pode contradizer a manchete que ela ilustra,
e ninguém percebe — porque quem escreveu o texto sabia o que a barra significava.** O leitor
não sabe: ele lê o rótulo. Os dois PNGs desta perna foram gerados para a prancheta, onde
"Efeito-DEMANDA" era uma abreviação entendida entre quem rodou o script; na tela, virou uma
afirmação falsa em negrito ao lado do seu próprio desmentido. Vale varrer **toda figura de
`outputs/` que a peça reusa** com essa pergunta: *o rótulo dos eixos ainda diz o que o
pipeline concluiu, ou diz o que ele concluía antes da última auditoria?*

**Arquivos tocados:** `reforma.html` (Perna 4 inteira + 2 fragilidades novas),
`assets/css/reforma.css` (blocos `.decomp` e `.estoquefig`),
`scripts/fronteira_fechando.py` (rótulo do #39 na origem),
`docs/BLUEPRINT_PARTE2.md` (Perna 4 marcada como registro histórico + resposta nova).

---

## 19. A varredura de rótulos de figura — virou D27, e achou um segundo caso (28/jul/2026)

A lição da §18.8 foi promovida a decisão. A regra e o método completo vivem em
**`Textos/metodologia/auditoria_de_figuras.md` (D27)**; aqui fica só o que a varredura
encontrou **nesta peça**.

### 19.1 A regra, em uma linha

> Toda figura **importada de um script** responde, antes de publicar: *o rótulo — título, eixo,
> legenda, nome de série — ainda diz o que o pipeline conclui hoje, ou o que ele concluía antes
> da última auditoria?*

Com uma regra companheira que o caso novo obrigou a escrever: **se a peça acrescentou uma
ressalva a uma série, toda representação daquela série carrega a ressalva** — inclusive a que
veio pronta do pipeline.

### 19.2 O inventário desta peça — 12 figuras, e a oficina não tinha nenhuma

`grep "<figure\|<canvas\|role=\"img\""` no `reforma.html` dá 12 peças visuais, em três classes de
risco (A = raster de script, rótulo dentro do binário; B = JS + JSON exportado; C = SVG inline
autorado):

| Classe | Quantas | Onde |
|---|--:|---|
| **A** — raster importado | **2** | `deslocamento_latitude.png` (Perna 1) e `sintese_idade_duas_populacoes.png` (Perna 2) |
| **B** — JS + JSON | **4** | mapa da Parte 1; `marchamap-mapa` e `marchamap-strip` (Perna 1); `reserva-painel` ×2 (Perna 2) |
| **C** — SVG inline | **8** | cinco-medidas (P1); assinatura, esquema-espúria ×2, simetria (P3); decomp, estoquefig (P4) |

Duas surpresas do levantamento:

1. **As Partes 3 e 4 não têm figura nenhuma.** A suspeita registrada na §18.8 era que
   "sobrariam as da Perna 1 e as da oficina" — a oficina não tem o que sobrar. O que sobra é a
   Perna 1.
2. **O site publicado tem 25 figuras estáticas, todas classe A** — incluindo o próprio
   `decomposicao_oferta_demanda.png`. Ou seja: **o site no ar exibe agora a figura do caso 1**,
   com o rótulo que o #39 já retratou. Isso não pede auditoria; pede a troca, que aposenta 23
   das 25 por construção. Auditar o `index.html` figura a figura seria trabalho jogado fora.

### 19.3 O caso novo — a mesma série, ressalvada em cima e não ressalvada embaixo

Na Perna 1, a revisão do autor (§12) concluiu que a série da **agricultura** precisa de ressalva
a partir de **2019**, por causa da deriva do Mosaico (D25/D26). O interativo passou a marcar
isso: `ANO_ROTULO_DERIVA = 2019` em `marcha-mapa.js`, com nota em texto abaixo.

O PNG `deslocamento_latitude.png` fica **na linha 553, imediatamente abaixo** — e plota a *mesma
série* em linha cheia, período inteiro, legenda "Agricultura", sem ressalva alguma.

Nenhum rótulo está errado: os títulos do `fig_latitude` (`centro_massa.py`) são descritivos. O
que falha é a regra companheira — a peça ressalvou a série num lugar e não no outro, e o leitor
vê as duas versões com dois centímetros de distância.

**Três saídas, a decidir pelo autor:**

| | O que fazer | Custo | Efeito colateral |
|---|---|---|---|
| a | propagar o corte de 2019 para o `fig_latitude` e re-rodar o #32 | médio (roda pipeline) | conserta a figura para sempre, inclusive fora do site |
| b | trocar pelo `robustez_deriva_regua.png`, que o #32 **já produz** para exatamente esta pergunta | baixo | muda o assunto da figura de "para onde andou" para "a régua muda a resposta?" |
| c | remover o PNG — o interativo acima já cobre a informação | mínimo | foi o desfecho do `veredito.png` na Perna 3 |

### 19.4 O que a D27 põe como gate da troca (e o que ela explicitamente não põe)

**Bloqueia a troca** (entrou na §11.2): fechar o caso do §19.3; e auditar a **legenda de classes
do mapa da Parte 1** — a única figura de classe B nunca revisada, e a classe do bug conhecido
(classe 21 "Mosaico de Usos") é justamente uma categoria de legenda.

**Não bloqueia:** auditar o `index.html` (a troca o aposenta); auditar as 434 figuras de
`outputs/` — vale o princípio de escopo da D27, **audita-se por exposição, não por inventário**;
e a varredura irmã **número na tela × CSV**, que é outro método (abrir o CSV e conferir um a um)
e merece dia próprio — foi ela que, feita *ad hoc* na Perna 4, achou os três erros da §18.6.

---

## 20. A varredura "número na tela × CSV" — a peça inteira (28/jul/2026) ✅

A §19.4 registrou esta varredura como "outro método, que merece dia próprio" — foi ela que,
feita *ad hoc* na Perna 4, achou os três erros da §18.6. Feita agora sobre a peça inteira. O
método e o inventário completo vivem em **`Textos/metodologia/auditoria_numeros_tela.md`**;
aqui fica o que ela mudou nesta peça.

**Método, em uma linha:** extração **mecânica** (parser de HTML → toda frase com dígito,
agrupada por `id` de seção → **442 blocos em 27 seções**), depois cada número rastreado até
`data/processed/` ou `assets/data/`. Ler a peça procurando número não funciona — foi assim que
os três erros da §18.6 sobreviveram a três revisões.

**Veredito: nenhuma conclusão cai.** ~160 afirmações rastreadas, a maioria batendo ao decimal —
incluindo a decomposição inteira da Perna 4, as cinco medidas da Perna 1, o censo de 44,6 M
pixels da Perna 2 e as 12 e 24 células da Perna 3.

### 20.1 Garantia nova: as figuras SVG desenham o que rotulam

Decodifiquei a geometria dos SVG autorais (converter `path`/`rect` de volta a valores pela
escala do eixo). **As três batem ao pixel**: `cinco-medidas` (24 px/km), `decomp` (30.000 px por
Mha/ano) e `estoquefig` (3,746 px por ponto percentual, reproduzindo o CSV a 0,1 pp). Nenhum
teste do projeto olhava para isso, e uma figura autorada à mão pode desenhar número diferente
do que rotula.

### 20.2 Os quatro defeitos — corrigidos

| # | defeito | correção |
|---|---|---|
| 1 | **`H = 22,6` era a estatística do teste errado** — é o Kruskal-Wallis de **4 períodos**; o dos 3 Atos é **H = 20,26**. A peça publicava a estatística da partição que ela **rejeita duas frases adiante**. Estava em `reforma.html` ×2 **e no `index.html` no ar ×3** | `H = 20,3` nos cinco lugares; a oficina agora **declara** o 22,6 como sendo o da partição rejeitada, para o número não voltar |
| 2 | **"cruza os 60% ainda nos anos 1990"** (legenda da `estoquefig`) — pela régua refinada o Sul está em **66,7% em 1999** e cruza em **2005**. **O SVG estava certo** (decodifica para 2005): envelheceu a *prosa*, não o rótulo — a D27 ao contrário | "é o único dos três que chega a cruzar os 60%, em meados dos anos 2000" (+ §18.3 do plano) |
| 3 | **"os placebos não acendem"**, no `.nao-diz` da Perna 3 — o #34 registra por escrito a *"mancha de especificidade"*: 1 dos 6 placebos direcionais dá p=0,032. **Terceira reincidência** do padrão da §16.4 | "nulo em **cinco das seis** células", com a sexta nomeada e explicada. **Fortalece** a peça, no trade da §14/§16.5 |
| 4 | **"Sul, Centro e Leste seguem com pico e ombro"** (Perna 2) — o Centro tem vale raso (dip 0,084 contra 0,415 do Noroeste e 0,271 do Norte) | as cinco profundidades agora aparecem (42/27/8/0/0) e o Centro fica "no meio do caminho". A conclusão de **blocos** já estava certa |

Um quinto, da mesma família, encontrado ao conferir o item 3: o `.nao-diz` do câmbio dizia
*"não há antecipação"*, e o #54 registra o lead **borderline para H1** (p≈0,06–0,07), limpo só
para o H2 exógeno — que é o headline justamente por isso. Reescrito para dizer qual
especificação passa limpo.

### 20.3 Três imprecisões (não eram defeitos)

Soja SIDRA era **+48,3** e saía como "+49" (propagado também para o `BLUEPRINT_PARTE2.md` e o
§12 deste plano — corrigidos); lotação é **×1,337** e saía como "×1,35" (vinha de dividir os
extremos já arredondados); e o **"AIC −2.924 vs −2.924"** estava *certo* mas parecia erro de
digitação — virou "0,7 ponto de AIC separa os dois", que é o que o número quer dizer.

*Registrada, sem ação:* o hero usa **0,09 ha/px** (nominal de 30 m) e o censo do #28 usa
**0,0855 ha/px** (área real na projeção). Dividir 3,8 Mha por 0,09 dá 42,4 M, não 44,6 M.
Nenhum dos dois está errado — o projeto não tem uma constante única, e vale saber disso antes
que alguém faça a conta.

### 20.4 A legenda de classes do mapa da Parte 1 — auditada, **aprovada**

O outro bloqueio da D27 (§19.4). Ela declara a ausência do Mosaico em **três lugares
independentes**: o *swatch* é **hachurado** (único visualmente distinto dos sólidos); o `title`
diz "aparece na barra, mas não é pintada no mapa"; e a **linha de fonte, em texto visível**,
repete. O terceiro é o que fecha — os outros dois dependem de *hover*. **Sai da lista de
bloqueios.**

### 20.5 A regra que sai daqui

**Número exibido é afirmação, e envelhece igual a rótulo de figura.** Nenhum teste do projeto
pega isso: a varredura de frases banidas procura texto que *voltou*, não número que *nunca
bateu*. Dois padrões a vigiar, ambos observados aqui:

1. **A linha vizinha da tabela certa** — 2 dos 4 defeitos. O erro não vem de inventar número;
   vem de acertar a tabela e errar a linha.
2. **O `.nao-diz` que afirma um nulo sem denominador.** Regra explícita: *toda frase de "o que
   isto não diz" que afirme um nulo ("os placebos não acendem", "não aparece em nenhum")
   precisa da contagem exata ao lado.* É o overclaim mais fácil de cometer no bloco que existe
   justamente para evitá-lo — e já aconteceu três vezes.
