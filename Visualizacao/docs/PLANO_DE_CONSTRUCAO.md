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

## 5. Correções de números pendentes no site atual

A auditoria deixou erros na tela. Eles **entram na reforma já corrigidos**; e, como o
`index.html` continua no ar durante toda a construção, cada um também precisa ser
decidido: corrigir agora no site antigo ou esperar a troca.

| # | onde | erro | correto |
|---|---|---|---|
| 1 | `index.html:143` (hero) | "38 milhões de pontos… 1,5 bilhão de registros" — **10× menor** | **378 milhões** de pixels/ano · **15,1 bilhões** em 40 anos (34.024.262 ha ÷ 0,09 ha) |
| 2 | `index.html:415`, `:1514`, `:1580` | "as 16 decisões metodológicas" | **26** (D1–D26) — o próprio bloco M5 já lista as 26 |
| 3 | `index.html:487`, `:492`, `:497`, `:511` | cards do Sankey com os valores da matriz de 6 grupos (4,11 / 2,73 / 1,29) | **4,10 / 2,72 / 1,29** pela recontagem do #12B — e o texto "três fluxos" precisa virar quatro, com o Mosaico |
| 4 | `index.html:415` | "avança em três movimentos" | a reforma dissolve os Movimentos; some com a arquitetura nova |

*(1 e 2 são erros factuais simples e independentes da reforma; 3 e 4 se resolvem
naturalmente na Parte 1 reformulada.)*

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
