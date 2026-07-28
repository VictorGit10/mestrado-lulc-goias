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
| 8 | `p2-perna4` | Perna 4 · o teto | BP-2 § Perna 4 | figuras #39/#47 | imagens de `outputs/` |
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

### 11.1 A revisão do autor — em curso, parada na Perna 1

> **Onde a leitura está (28/jul/2026):** o autor leu do hero até
> **"Perna 1 de 4 · O padrão existe?"** e parou ali. O trecho lido foi aprovado
> ("está muito bom"), com duas questões levantadas na própria Perna 1 — **ambas já
> resolvidas** (§12 e §13). **As Pernas 2, 3 e 4 e as Partes 3 e 4 ainda não foram lidas.**

Isso importa registrar porque **a leitura é o critério de aceite da §1** — nenhum teste a
substitui, e ela é a única coisa que hoje separa a peça da troca. Vale notar o que a
revisão parcial já produziu: as duas questões da Perna 1 não eram ajustes de copy, eram
**um problema conceitual** (a deriva do Mosaico no centroide) e **um risco de leitura
errada** (confundir co-expansão com deslocamento). A primeira virou figura nova e uma
correção em `marcha-mapa.js` que também alcançou o site publicado; a segunda virou parágrafo
distinguindo as duas afirmações; e a conversa sobre a segunda **descobriu uma auditoria que
faltava** (§14). Ou seja: uma perna de leitura rendeu três commits. É razoável esperar que
as três pernas restantes rendam mais — a Fase D não deveria ser tratada como formalidade.

### 11.2 O que falta

1. **Terminar a leitura** — da Perna 2 até o fim da Parte 4. ⏳ *bloqueia a troca*
2. **Polimento:** o título embutido nos PNGs do mapa coberto pelo seletor de camadas (§8);
   revisar a Parte 1 em 360 px; conferir `prefers-reduced-motion` nas duas interativas.
3. **A troca:** `reforma.html` → `index.html`, o antigo para
   `docs/_arquivo/index-pre-reforma.html`, num commit só. Depois disso, `router.js`,
   `secoes.js` e `tabs.css` ficam órfãos e podem sair.
4. **Reconciliar o `IMPLEMENTACAO.md`**, que descreve o site em abas — ele vira registro
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
   a âncora imune declarada: soja SIDRA **+49 km**.
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
