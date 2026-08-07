# Revisão da Parte 1 — "Os 40 anos no mapa"

**Data:** 2026-08-07 · **Escopo:** `Visualizacao/index.html` linhas 119–495, `assets/data/marcos.json`,
`assets/js/timeline.js`, as 4 abas de mapa e as figuras que elas servem.

**Por quê agora.** A reforma de jul–ago/2026 concentrou-se da Parte 2 em diante. A Parte 1 —
o hero, o "Como ler", os 3 cards de ato, os 40 cards anuais, o saldo e o Sankey — foi carregada
da versão anterior quase intacta. Leitores externos passaram a maior parte do tempo justamente
ali e devolveram quatro críticas. Esta revisão parte delas e varre o resto.

Evidência-âncora: **`marcos.json` tem data de 21/mai/2026**, anterior a toda a reforma, ao fix da
classe 21, ao censo de pixels e à D26. Seu próprio cabeçalho registra que a redação nunca foi
validada:

> `"_nota": "... A redação final dos cards e a bibliografia devem ser validadas com o orientador antes da publicação."`

Isso não foi feito. Os 8 cards de referência institucional são o material mais antigo e menos
auditado da página — e são os que o leitor lê com mais atenção, porque interrompem a monotonia
do scroll.

---

## A. Coisas erradas

### A1 — Contradição direta dentro da própria página (a mais grave)

O card do pino **1996 (Lei Kandir)** afirma:

> "O teste de diferença-em-diferenças confirma que GO diverge dos estados-controle após 1996."

O bloco "Como ler os 40 anos", **80 linhas acima**, afirma o contrário:

> "Os pinos **contextualizam, não identificam**: as políticas testadas são federais, então não
> existe grupo não-tratado com que compará-las."

E a decisão D em `index.html:3790` fecha a questão:

> "os marcos testados (Plano Real, Commodity Boom, Código Florestal, Cerrado Manifesto) são
> *federais* — incidem sobre Goiás *e* sobre os controles, então não existe grupo não-tratado.
> O resultado mede **exposição diferencial a um choque comum**, não o efeito da lei. Nenhuma
> conclusão desta página se apoia nele."

O card ainda carrega `"evidencia": "A"` e `"escopo_empirico": "go_especifico"` — a classificação
mais forte do esquema, para o único achado que a página explicitamente desautoriza.

**Ajuste:** reescrever a última frase do card 1996 para "GO diverge dos estados de controle após
1996 — mas como a Kandir é federal e incide também sobre eles, isso mede exposição diferencial a
um choque comum, não o efeito da lei." Rebaixar `evidencia` para `B` e `escopo_empirico` para
`cerrado_amplo`.

### A2 — O card de 2018 sustenta exatamente a leitura que o Ato III desmonta

> "a agricultura para de crescer e a vegetação se recupera lentamente"

Medido no painel atual (`painel_goias.json`):

| ano | Δ veg (pp) | Δ agric (pp) |
|---|---|---|
| 2018 | −0,017 | +0,180 |
| 2019 | −0,097 | +0,203 |
| 2020 | −0,111 | +0,170 |
| 2021 | −0,162 | +0,031 |
| 2022 | −0,191 | +0,091 |
| 2023 | −0,276 | 0,000 |
| 2024 | −0,298 | +0,050 |

A vegetação **não se recupera em nenhum ano** — perde todos, e a perda **acelera
monotonicamente** (×17 entre 2018 e 2024). A frase é falsa.

Pior: "a agricultura para de crescer" é precisamente o artefato de rótulo que o card do Ato III,
duas telas adiante, existe para desmontar ("Olhando só a classe agricultura do satélite, a
conversão parece ter parado"). O card de 2018 endossa a ilusão; o card do Ato III a derruba. O
leitor encontra os dois.

**Ajuste:** trocar por "a agricultura *aparenta* parar de crescer na classe do satélite a partir
de 2021 — o Ato III mostra que é mudança de rótulo — enquanto a perda de vegetação natural, que
havia caído a 0,02 pp em 2018, volta a acelerar até 0,30 pp/a em 2024."

### A3 — "a maior desde 1993" é falso

Card de **2003**: "a perda de vegetação natural atinge 0,49 pp/a em 2003 — a maior desde 1993."

Perdas anuais medidas entre 1994 e 2003: 1994 −0,757 · 1995 −0,673 · 1996 −0,540 · 1997 −0,776 ·
1998 −0,537 · 1999 −0,413 · 2000 −0,439 · 2001 −0,430 · 2002 −0,445 · **2003 −0,490**.

Cinco anos posteriores a 1993 tiveram perda maior. O correto é **"a maior desde 1998"**.

### A4 — Reserva Legal: enunciado geral falso + o ponto que falta é 2008

Card de **2012**: "No Cerrado, a RL permanece em 20%."

Falso como regra geral. Lei 12.651/2012, art. 12: dentro da **Amazônia Legal** a RL no cerrado é
**35%**; os 20% valem fora dela. A frase do card não faz essa distinção, e a diferença **importa
para o desenho do trabalho**: o Tocantins, controle do #23, é 100% Amazônia Legal. Tratado e
controle passam a ter restrição legal estruturalmente diferente depois de 2012, e isso não está
declarado em lugar nenhum.

> ⚠️ **Esta seção continha um erro meu, corrigido mais abaixo.** Na primeira passada eu escrevi
> aqui — e na página — que "Goiás não integra a Amazônia Legal", o que é falso: o próprio art. 3º,
> I do Código Florestal inclui as regiões **ao norte do paralelo 13º S de Tocantins *e de Goiás***.
> Ver [Autocorreção](#autocorreção-eu-errei-o-a4-na-primeira-passada-07ago2026-mesma-sessão).
> O resto do raciocínio desta seção (o corte de 2008) se mantém, com uma ressalva causal também
> registrada lá.

O ponto maior, que é o que o revisor está entregando de graça: **o conteúdo operante da lei de
2012 é a data de 22/07/2008.**

- art. 3º, IV — "área rural consolidada" = ocupação antrópica preexistente a **22/07/2008**;
- art. 67 — imóveis até 4 módulos fiscais: a RL é a vegetação nativa **existente em 22/07/2008**;
- art. 68 — quem suprimiu respeitando a lei vigente à época está **dispensado de recompor**;
- art. 29 — o **CAR** é o registro; art. 59 — a inscrição no CAR é a porta de entrada do PRA e,
  com ele, da regularização.

Ou seja: o Código Florestal de 2012 não impôs uma restrição nova sobre o passivo acumulado —
**converteu-o em situação consolidada**, e o CAR é o instrumento que operacionaliza isso.

Hoje o card diz "A ausência de desaceleração é o achado — a regulação não reverteu a tendência".
Está certo como fato e vazio como explicação. O corte de 2008 dá o mecanismo que falta.

> ⚠️ **Segunda correção.** Na primeira passada eu emendei essa frase com "é por isso que não há
> quebra em 2012", transformando o nulo em nulo *explicado*. Isso é uma ponte causal sem teste —
> o mesmo defeito do A1. Ver a [Autocorreção](#autocorreção-eu-errei-o-a4-na-primeira-passada-07ago2026-mesma-sessão).

**Ajuste:** reescrever o card de 2012 em torno do corte de 2008 + CAR, apresentando a ligação com
o nulo como leitura plausível e não como resultado, e qualificar os percentuais (20% em quase
todo Goiás; 35% na faixa ao norte do paralelo 13º S). Registrar o descasamento GO × TO como
ressalva do #23 na Oficina.

### A5 — A glosa dos −5,8 Mha compara coisas incomparáveis

> "17,65 → 11,88 Mha (51,9% → 34,9% do território). **A 15 pontos do limite legal de Reserva
> Legal no Cerrado (20%).**"

Três problemas empilhados:

1. **RL é obrigação por imóvel, não agregado estadual.** Um estado com 34,9% de vegetação pode
   ter a maioria dos imóveis abaixo de 20%. A comparação não tem sentido dimensional.
2. **O numerador não é o que a RL protege.** Os 34,9% incluem unidades de conservação, terras
   indígenas, APPs e vegetação em área urbana — nada disso é Reserva Legal.
3. **Depois de A4, a referência dos 20% nem é a vinculante** para o passivo existente: para quem
   já havia desmatado até 22/07/2008, a referência legal é o que havia naquela data.

A frase soa como um alarme quantificado ("faltam 15 pontos") e não mede nada.

**Ajuste:** trocar por algo que a série realmente sustenta — p.ex. "Em 1985 metade do estado
ainda era vegetação natural; em 2024, pouco mais de um terço." Se quiser manter a âncora legal,
ela pertence a uma nota que explique por que o agregado estadual **não** é comparável ao piso de
RL. O mesmo vale para a frase do card de 2024 ("vegetação natural próxima ao limite legal de 20%
em diversas regiões"), que tem o mesmo defeito em versão mais vaga.

### A6 — Atribuição causal não medida no card do Ato I

> "POLOCENTRO e PRODECER abriram cerca de um terço do estado para pecuária extensiva."

- "Um terço do estado" é simplesmente a **área de pastagem em 1985** (32,3%) — atribuída a dois
  programas sem que nada no trabalho tenha medido essa atribuição. Nos documentos internos os
  dois aparecem só como contexto ("herança POLOCENTRO/PRODECER", `29_triangulacao_periodizacao.md`).
- O **PRODECER era programa de grãos**, não de pecuária, e chegou a Goiás na fase II
  (a partir de 1987) — depois do primeiro mapa da série.

**Ajuste:** "Em 1985, quase um terço de Goiás já era pastagem — legado de duas décadas de
ocupação dirigida do Cerrado (POLOCENTRO, a partir de 1975) que a série não alcança." Tirar o
PRODECER da frase ou movê-lo para onde ele de fato entra (grãos, fim dos anos 1980).

### A7 — Números velhos nos cards

`marcos.json` é de maio; o painel foi recomputado depois (fix da classe 21, censo de pixels).
Alguns valores não batem mais:

| card | afirma | medido hoje |
|---|---|---|
| 1994 | 0,88 pp/a (1990-93) | **0,86** |
| 1994 | 0,63 pp/a (1995-98) | **0,62** |
| 2012 | agric 0,20 → **0,45** pp/a, "**2,3×** mais rápido" | 0,19 → **0,55**, ou seja **2,8×** (a janela 2012-15 citada dá 0,55; 0,45 corresponde a 2011-15) |
| 1996 | 0,54 → 0,41 pp/a "após 1998" | nenhuma janela do painel atual reproduz esse par |

Os de 1994 são arredondamento; os de 2012 e 1996 precisam ser recalculados ou removidos.

### A8 — Escopos trocados sem aviso no card do Ato III

Três orações seguidas, três recortes diferentes, nenhum declarado:

- "no Sul goiano ela **cai 88%**" → Sul, MapBiomas `pasto→agric` (−88,4%);
- "a área de soja plantada que o IBGE recolhe em campo **cresce 38%**" → **estado inteiro**, SIDRA;
- "acelera cerca de **50%**" → de volta ao **Sul**, régua da união (+51,0%).

O leitor lê como se fosse tudo o mesmo recorte. Basta rotular cada um.

---

## B. Bugs vivos

**B1 — "Lotação: —" nos 40 anos.** `timeline.js:243` lê `dado.lotacao_bov_ha`; o painel entrega
`lotacao_bov_ha_pasto` (40/40 anos preenchidos). `valorOuTraco` recebe `undefined`, devolve travessão.
A linha aparece vazia em todos os anos desde a remoção da UA (29/jul). Correção de uma palavra.

**B2 — Sankey sem acento.** `sankey.js:199` faz `.replace("Agua", "Agua")` — no-op: o rótulo
sai **"Agua"**. O mesmo em `mini-sankey.js` (o mapa de nomes não tem entrada para "Agua"). E os
tooltips (`sankey.js:161`, `mini-sankey.js:167`) usam o `label` cru do JSON: toda passagem de
mouse mostra **"Vegetacao Natural (1985) → Pastagem (2024)"**. O `aria-label` do SVG também
("transicoes").

**B3 — A lista de pinos está incompleta.** "Referências institucionais" lista 6 pinos; a régua
renderiza os **8** de `marcos.json` (faltam 1985 e 2024). O leitor conta e não fecha.

**B4 — Rótulo inicial da régua diverge.** O HTML nasce com "1985 · Linha de base da série";
`marcos.json` diz "Início da série / Redemocratização", que é o que aparece assim que o leitor rola.

---

## C. As abas de mapa — o problema é maior do que "sobrar mapa"

As 4 abas (Cobertura · Δ vs 1985 · Fogo · Transições) trocam **só a imagem**. Tudo em volta fica
parado:

**C1 — A legenda não troca.** Em Fogo, Δ e Transições o leitor vê a legenda de LULC
(Veg. natural / Pastagem / Agricultura / Mosaico / Água / Urbano / Outros) embaixo de um mapa que
não usa nenhuma dessas classes. Cada PNG traz a sua própria legenda embutida — então há **duas
legendas simultâneas na tela, discordando**.

**C2 — A barra de composição não troca.** Continua mostrando a composição LULC do ano, ao lado de
um mapa de área queimada.

**C3 — A fonte do caption mente em 3 das 4 abas.** "Fonte: MapBiomas Coleção 10.1 · pixel-a-pixel
(30 m)" fica fixo. Mas:

| aba | unidade real | fonte real |
|---|---|---|
| Cobertura | pixel 30 m | MapBiomas 10.1 |
| Δ vs 1985 | **AMC** (coroplético) | painel AMC |
| Fogo | **AMC** (coroplético) | painel AMC, `fogo_total_ha` |
| Transições | **município** (coroplético) | MapBiomas 10.1 agregado |

Três unidades espaciais diferentes sob um caption que declara uma só.

**C4 — "Δ vs 1985" não diz de quê.** É Δ pp de **pastagem**, e só. O botão não fala isso, o
caption não fala, e o PNG contradiz a si mesmo: título "Delta % Pastagem", legenda "Δ pp pastagem".

> **É aqui que provavelmente mora a crítica "diferenças em pp entre mapa e painel".** A escala do
> mapa vai a **±45 pp por AMC**, enquanto o caption logo abaixo mostra o agregado estadual
> ("vs. 1985 — veg −17,0 pp · pasto +3,0 pp"). O mesmo símbolo, dois referentes.
> Some-se a isso o segundo candidato: os cards laterais mostram delta **ano a ano** em pp, sem
> dizer que é ano a ano, enquanto o caption mostra **acumulado desde 1985**, também em pp.
> Nenhum dos dois declara sua base.

**C5 — Fogo: o mapa não discrimina nada.** `gerar_mapas_fogo_40anos.py` plota **área queimada
absoluta** por AMC, em `log1p` com breaks Jenks **globais**. Consequências:
- sem normalizar por área, o mapa desenha o tamanho da AMC tanto quanto o fogo;
- a escala global é fixada pelos anos 1985–88 (2,1 / 1,4 / 1,8 / 2,4 Mha), que são o topo da série;
- o `log1p` comprime o resto: em 2010 o estado inteiro sai vermelho, com quatro tons quase
  indistinguíveis.

A sugestão do revisor — **anomalia (Z) contra o período do próprio ato** — corrige exatamente
isso: passa a mostrar *onde queimou fora do normal para aquele ato*, que é a única pergunta que
um mapa de fogo responde bem numa série de 40 anos com variabilidade climática dominante
(2013: 0,21 Mha · 2010: 1,80 Mha — fator 8,5 entre anos vizinhos na série).

**C6 — Transições: congela e afirma o que a página nega.** Só existem 4 imagens de período; ao
rolar ano a ano dentro de 2005–2015 o mapa fica parado 10 anos sem aviso. Pior: o painel
2015→2024 mostra **quase todo o estado em "Mosaico de Usos"** como transição dominante — sem
legenda de página, sem caption, sem ressalva. É o artefato de rótulo que a página inteira (e o
dossiê `dossie-mosaico.html`) existe para desmontar, apresentado como fato cartográfico.

**C7 — Acentuação faltando nos PNGs antigos.** Fogo e Δ (gerados em jun/2026) saem com
"Area Queimada — Goias", "Delta % Pastagem — Goias", "retracao", "expansao", "sem mudanca".
Cobertura e Transições (regerados depois) já estão acentuados.

### Recomendação sobre as abas

**Cortar "Fogo" e "Δ vs 1985" da Parte 1.**

- **Fogo** já tem duas casas melhores: o atlas de 8 camadas (linkado em `index.html:598`) e o
  teste da "quinta camada" na Perna 1 (`index.html:778`), onde o resultado é que a hipótese
  "o fogo abre o caminho" **não se sustenta**. Na Parte 1 ele não pertence à narrativa — a Parte 1
  é o fenômeno bruto do uso da terra — e o mapa que temos não mostra nada.
- **Δ vs 1985 (pastagem)** duplica o que a barra de composição + o caption já dão em número, com
  menos precisão e mais ambiguidade.

**Manter "Transições"**, mas com legenda própria, caption de período visível, aviso de que o mapa
é por município e não por pixel, e a ressalva do Mosaico no painel 2015→2024. Ou movê-lo para
depois do Sankey, onde o assunto já é fluxo.

Se preferir manter o Fogo, o mínimo é: regerar como **Z por ato** (sugestão do revisor),
normalizar por área da AMC, trocar legenda e caption junto com a aba, e escrever uma linha
dizendo o que se deve olhar.

---

## D. O "estilo IA"

O revisor citou uma frase; o padrão é mensurável. Na Parte 1 (~10.500 caracteres de texto
visível):

- **39 travessões** — um a cada ~270 caracteres, cerca de um por frase e meia;
- **8 antíteses "não é X — é Y"**;
- **13 dois-pontos retóricos** (`palavra: minúscula`).

É a assinatura estilística que os leitores estão detectando. Não é o conteúdo — é a densidade da
mesma figura de linguagem.

**Frases a reescrever (a citada + as irmãs):**

| onde | frase | problema |
|---|---|---|
| Ato I | "Sem estabilidade macroeconômica, qualquer cálculo agrícola de longo prazo segue bloqueado." | citada pelo revisor; aforismo sem sujeito, não diz nada sobre Goiás |
| Ato II | "O Plano Real faz o que nenhuma política agrícola isolada conseguiria: permite calcular o futuro." | superlativo não testado + "calcular o futuro" |
| marco 1994 | "reabilita o cálculo econômico de longo prazo" | terceira repetição da mesma ideia em três telas |
| Ato I | "O ponto de partida não é uma paisagem natural — é uma fronteira que já se moveu." | antítese; e a informação (1985 já é paisagem alterada) cabe direta |
| saldo | "Goiás não encontrou um piso: mudou o endereço da fronteira." | "mudou o endereço" |
| saldo | "Saldo líquido é justamente o que esconde o caminho dos hectares." | aforismo de fecho |
| Mosaico | "Tratá-lo à parte não é contabilidade: ..." | mesma antítese, quarta ocorrência |

**Léxico a revisar:** "**pino**" para marcador de linha do tempo é decalque do inglês (*pin*) —
em pt-BR seria "marco" ou "marcador", e "marco" já é o nome do dado (`marcos.json`).
"**Veredito**" e "**Oficina**" como títulos de parte foram citados pelo revisor pelo mesmo motivo.
E a legenda da matriz 7×7 usa "**off-diagonal**" cru (`matriz.js:105`).

**Redundância estrutural:** o contexto do **Ato II** é inteiramente sobre **1994 e 1996** — que
são Ato I. O leitor já passou pelos dois cards de pino ao rolar. Chega no topo do Ato II e lê a
terceira versão dos mesmos eventos. O contexto do Ato II deveria falar de 2001–2019.

---

## E. MapBiomas na abertura

Pedido explícito do revisor, e está certo. O hero diz "378 milhões de pixels... 15 bilhões de
observações" — números que só existem porque **são do MapBiomas** — e não nomeia a fonte. A
primeira menção só aparece no caption do mapa, depois que o leitor já rolou.

(Os números conferem: 378 M × 900 m² = 34,02 Mha = `lulc_area_total_ha`; × 40 anos = 15,1 bi.)

**Ajuste:** nomear MapBiomas Coleção 10.1 na própria frase do hero, junto com o IBGE, que é a
âncora independente do argumento inteiro.

---

## F. Um problema que ninguém apontou: o mapa e a barra não fecham

Na aba Cobertura, o raster tem o Mosaico **transparente** (`selfMask()` no GEE) e a legenda
embutida no PNG diz "Classe (6 grupos)". A legenda em HTML embaixo lista **7**, incluindo o
Mosaico com a nota "(só na barra)". Resultado: em 2024, **10,5% do estado é branco no mapa** e
aparece como faixa na barra. Quem tentar conferir a barra contra o mapa não fecha — e essa é a
outra leitura possível de "diferenças em pp entre mapa e painel".

A nota "(só na barra)" existe e é honesta, mas é pequena e chega depois do estranhamento.
Vale um passo a mais: dizer no caption que **as manchas brancas no mapa são o Mosaico**, ou
pintá-lo em hachura de baixa saturação para que a área apareça sem competir com as classes
nomeadas.

---

---

## Estado: tudo aplicado em 07/ago/2026

O autor aprovou os pontos e todos foram executados na mesma sessão.

| item | o que foi feito |
|---|---|
| A1 | Card 1996 reescrito (DiD vira "exposição diferencial a um choque comum"); `evidencia` A→B, `escopo_empirico` `go_especifico`→`cerrado_amplo` |
| A2 | Card 2018 reescrito: a vegetação não "se recupera", perde e acelera; a estabilidade da agricultura é declarada como mudança de rótulo |
| A3 | "a maior desde 1993" → **"a maior desde 1998"** |
| A4 | Card 2012 reescrito em torno de 22/07/2008 + CAR (arts. 3º IV, 67, 68, 29, 59); os 20% qualificados por Amazônia Legal; referências ampliadas com a LC 124/2007 |
| A5 | Glosa dos −5,8 Mha trocada por leitura direta da série; a âncora legal virou um `<details>` novo, **"Por que 34,9% não se compara com os 20% de Reserva Legal"**, com os três motivos (escala, numerador, data) |
| A6 | Card Ato I: PRODECER removido da atribuição; "um terço" declarado como a pastagem de 1985, não como obra dos programas |
| A7 | 1994 (0,86 / 0,62), 1996 (0,66 → 0,44), 2012 (0,19 → 0,55, 2,8×) recalculados contra o painel atual |
| A8 | Ato III passa a rotular cada escopo: 88% **no Sul**, 38% **no estado inteiro**, 51% **no Sul** |
| B1 | `timeline.js` → `lotacao_bov_ha_pasto`. Verificado em tela: 2010 mostra 1,51 cab/ha |
| B2 | `acentuar()` em `sankey.js` e `mini-sankey.js`: rótulos e **tooltips** acentuados; `aria-label` corrigido |
| B3 | Lista de referências passa de 6 para os 8 marcos da régua |
| B4 | Rótulo inicial da régua alinhado ao `marcos.json` |
| C | **Fogo e Δ removidos.** Restam Cobertura e Transições. Legenda, barra de composição, rótulo do ano e fonte agora trocam junto com a camada; a fonte de Transições declara "por município, não por pixel" e traz a ressalva do Mosaico com link para o dossiê |
| D | Travessões na Parte 1: **39 → 5** (de 1 a cada 270 caracteres para 1 a cada 2.528). Frases-aforismo reescritas. "pino" → "marcador" em toda a página; "off-diagonal" → "fora da diagonal" |
| E | Hero ganhou parágrafo próprio nomeando **MapBiomas Coleção 10.1** e **IBGE** |
| F | Legenda e caption passam a dizer que as **falhas brancas do mapa são o Mosaico** |

### Achados extras, corrigidos no caminho

- **Contagem do atlas errada duas vezes:** o texto dizia "oito camadas" e listava **nove** itens; o atlas tem **19 séries** em 5 famílias. Corrigido nas duas ocorrências (Perna 1 e cartão dos bastidores).
- **Tags de categoria sem acento:** os slugs do JSON iam crus para a tela ("regulacao ambiental", "credito publico"). Mapa de rótulos em `timeline.js`.
- **`[hidden]` não escondia a legenda:** `display: flex` no autor vence `display: none` da folha do navegador. Sem `.map-legend[hidden] { display: none }` as duas legendas apareciam juntas. Pego pelo teste, não pela leitura.
- **Toggle de camadas cobria o título dos PNGs:** flutuava sobre a imagem e escondia ora o começo do título, ora o período no fim. Virou faixa própria acima do mapa.

### Verificação

- `Visualizacao/scripts/verificar_reforma.py`: todas as verificações passam.
- Checagem dirigida da Parte 1 (25 asserções: abas, troca de legenda/barra/fonte/rótulo, lotação, base dos "pp", acentos do Sankey, contagem de marcos, console): todas passam.
- Números dos cards e dos marcos reconferidos contra `painel_goias.json` e `sankey_data.json`.

---

## Autocorreção: eu errei o A4 na primeira passada (07/ago/2026, mesma sessão)

Provocado pela pergunta do autor ("você tem certeza absoluta?"), fui verificar o texto legal
em vez de reafirmar. **A minha correção estava errada no mesmo eixo em que o original estava.**

Eu escrevi na página: *"em Goiás a Reserva Legal é de 20% porque o estado fica fora da Amazônia
Legal"*. Isso é falso. O **próprio Código Florestal**, no art. 3º, I, define Amazônia Legal como

> "os Estados do Acre, Pará, Amazonas, Roraima, Rondônia, Amapá e Mato Grosso e as regiões
> situadas **ao norte do paralelo 13º S, dos Estados de Tocantins e Goiás**, e ao oeste do
> meridiano de 44º W, do Estado do Maranhão"

Goiás está lá, nominalmente. E a **Lei estadual de Goiás 18.104/2013, art. 25**, repete a regra
sem margem para dúvida: "I — 35%, no imóvel situado em área de cerrado na Amazônia Legal acima do
paralelo 13º; II — 20%, no imóvel situado nas demais regiões do Estado."

### O tamanho do erro, medido

Recortei a malha de Goiás no paralelo 13º S:

| medida | valor |
|---|---|
| extremo norte de GO | 12,396º S (existe território ao norte da linha) |
| área ao norte de 13º S | **0,27 Mha = 0,8% do estado** |
| municípios atingidos | 5: São Miguel do Araguaia (26% dele), Porangatu (13%), Campos Belos (47%), Montividiu do Norte (14%), Novo Planalto (<1%) |
| AMCs atingidas | 4 de 166 |
| centro de massa mais setentrional em 2024 | fogo em veg. natural, **14,47º S** — ainda 1,5 grau ao sul da linha |

Ou seja: o enunciado estava errado, o alcance é pequeno, e **a faixa fica além de onde a
fronteira chegou**. Nenhuma conclusão do trabalho depende disso. Mas numa banca a frase errada
custa caro, e era exatamente o tipo de detalhe que o revisor estava sinalizando.

### Um segundo erro meu, mais grave que o primeiro

Eu também escrevi no card de 2012: *"A lei não criou restrição nova sobre o passivo acumulado:
consolidou-o. **É por isso que** 2012 não deixa quebra em nenhuma das seis séries testadas."*

Esse "é por isso que" é **exatamente o pecado do A1** — a contradição que eu tinha acabado de
corrigir no card da Kandir. Transformei um nulo em nulo *explicado* sem nenhum teste. Explicações
concorrentes que não foram descartadas:

- o **CAR só entra em operação em 2014** (SICAR), com prazos de adesão prorrogados por anos; o
  PRA demorou ainda mais a ser regulamentado nos estados. Nada operacional acontece em 2012;
- um teste de quebra estrutural sobre série anual de LULC pode simplesmente **não ter potência**
  para detectar mudança regulatória, qualquer que seja o conteúdo dela.

O card agora afirma o que é fato sobre o texto da lei (consolidou o passivo pré-2008) e **recusa
explicitamente** a ponte causal com o nulo.

### Corrigido em

- `marcos.json`, card 2012 (percentuais + recusa da ponte causal);
- `index.html`, nota do `<details>` "Por que 34,9% não se compara com os 20%";
- `index.html`, ressalva da decisão do controle GO×TO na Oficina.

---

## O que NÃO foi analisado (resposta honesta)

Não. Nem tudo que poderia ter sido feito foi feito. O que ficou de fora, em ordem de interesse:

1. **A descontinuidade do paralelo 13º S como estratégia de identificação.** É uma fronteira
   legal, nítida e geográfica, que muda a Reserva Legal de 20% para 35% **dentro do mesmo
   estado**, mesmo bioma, mesmo governo estadual, mesma logística. É material clássico de
   regressão descontínua, e nunca foi tentado neste trabalho. **Mas o poder estatístico
   provavelmente inviabiliza**: são 0,8% do território e 4 AMCs de um lado da linha. Só faria
   sentido empilhando GO+TO ao longo do paralelo, e mesmo aí a linha corta o Tocantins numa
   região onde tudo ao norte também é Amazônia Legal. Vale registrar como ideia examinada e
   descartada por potência, não como ideia não pensada.
2. **Se o diferencial 20%/35% chega a vincular.** Argumentei que a consolidação de 2008 esvazia
   o piso de 20% para o passivo existente. O mesmo argumento vale para os 35% — e eu não o
   carreguei até lá. Sem dados de CAR por imóvel, não dá para dizer quanto da diferença é letra
   morta sobre o estoque já convertido.
3. **Os dados de CAR nunca foram usados.** A malha fundiária LAPIG já tinha sido avaliada para a
   Perna 4 e recusada (estática, endógena, pós-desfecho — `malha_fundiaria_ambiental.md`). As
   mesmas objeções valem aqui, então "usar o CAR para testar o corte de 2008" não é uma porta
   aberta.
4. **Tocantins não é uniformemente 35%.** O noroeste do estado (Bico do Papagaio) é área de
   floresta, onde a RL é 80%. A página agora diz isso; a simplificação "GO 20% × TO 35%" que usei
   no resumo era grosseira.
5. **A varredura de "20%" e "Reserva Legal" nos `Textos/`** não foi feita. A revisão cobriu a
   Parte 1 de `index.html` e o `marcos.json`. Se a mesma frase errada estiver na documentação da
   dissertação, ela continua lá.

---

## Varredura das afirmações institucionais em fonte primária (07/ago/2026)

Feita depois do episódio acima, pela mesma razão: se uma afirmação jurídica verificável em cinco
minutos passou errada, as outras mereciam a mesma passada. Todo card de marco e toda referência
foram conferidos em fonte primária ou no registro do periódico.

### Confere

| afirmação | fonte |
|---|---|
| POLOCENTRO criado em 1975 | Decreto 75.320, de 29/01/1975. E o programa foi articulado com os governos de **MG, MT e Goiás** — Goiás está no escopo original |
| Plano Real, "a nova moeda em julho de 1994" | MP 542, de 30/06/1994; o real passa a ter curso legal em **1º/07/1994** |
| Lei Kandir, LC 87 de **13/09/1996** | confere; desonera primários **e semielaborados** de exportação |
| China entra na OMC em dez/2001 | 11/12/2001, 143º membro |
| Manifesto do Cerrado, 2017 | lançado em **11/09/2017**, Dia do Cerrado, por ~60 organizações da sociedade civil |
| Código Florestal: arts. 3º I, 3º IV, 12, 29, 59, 67, 68 | conferidos no texto da lei |
| Lei estadual GO 18.104/2013, art. 25 | conferido: 35% acima do paralelo 13º, 20% no resto |
| SOARES-FILHO et al. 2014 | *Science* 344(6182):363-364 ✓. O abstract fala em "**grants amnesty to illegal deforesters**" — a referência sustenta bem o enquadramento de 2008 |
| SOTERRONI et al. 2019 | *Science Advances* 5(7):eaav7336, 17/07/2019 ✓ |
| RAJÃO et al. 2020 | *Science* 369(6501):246-248 ✓ |
| MARTINELLI et al. 2010 | *Curr. Opin. Environ. Sustain.* 2:431-438 ✓ |
| REZENDE, IPEA TD 1180 | Rio de Janeiro, abril/2006 ✓ |
| BACHA in MERCADANTE (org.) | *O Brasil pós-Real: a política econômica em debate*. UNICAMP/IE, 1997, **p. 11-70** — subtítulo e páginas acrescentados |

### Não conferia — dois erros

**1. Card de 2018: "adesões de traders e financiadores". Falso.** Os mais de 60 signatários do
Manifesto do Cerrado são **varejistas e indústrias de alimentos** (Walmart, Unilever, Nestlé,
McDonald's, Carrefour). As tradings que compram direto do produtor — ADM, Cargill, Bunge, Amaggi —
**não assinaram**. A correção não enfraquece a narrativa: reforça. O compromisso nunca alcançou o
elo que negocia com quem desmata, o que é coerente com o nulo que a série mostra. Card reescrito
nomeando quem aderiu e dizendo quem não aderiu.

**2. Card de 2002: "O Plano Safra sistematiza o crédito rural federal a partir de 2002/03".**
Errado em duas frentes. O instrumento se chama **Plano Agrícola e Pecuário** (a primeira edição no
repositório do MAPA é a de 2002/2003); "Plano Safra" é nome popular e, em sentido estrito, designa
o da agricultura familiar. E o crédito rural federal não foi sistematizado ali: o Sistema Nacional
de Crédito Rural é de 1965. O PAP **anuncia anualmente volume e condições**, que é bem menos do que
"sistematiza". Reescrito.

### Ajuste de escopo: o Tocantins saiu da Parte 1

Decisão do autor, e correta: o contraste GO×TO **não sustenta nenhuma conclusão da tese** — o #23
já está rebaixado a "sensibilidade de co-movimento" — então exibi-lo na Parte 1 dava a impressão
de uma análise que não existe.

- Na Parte 1, a nota sobre Reserva Legal agora fala **só de Goiás** e fecha com
  *"Nenhuma análise desta página trata essa faixa em separado."* A única menção restante ao
  Tocantins é a citação literal do art. 3º, I, que nomeia os dois estados.
- Na Oficina, onde o #23 mora, a ressalva foi encurtada e passou a declarar o que **não** foi
  feito: *"Não medimos se isso tem efeito prático: a consolidação do passivo anterior a 22/07/2008
  pode esvaziar os dois pisos, e verificar isso exigiria dados de CAR por imóvel, que este
  trabalho não usa."*

> **Regra que fica desta rodada.** Corrigir um erro não autoriza a acrescentar uma análise. As duas
> vezes em que errei aqui foi ampliando: primeiro inventando um mecanismo causal para o nulo de
> 2012, depois transformando um detalhe legal em suposto achado de desenho sobre GO×TO. O reparo
> certo de uma afirmação errada costuma ser uma afirmação **menor**, não uma maior.

---

## Justaposição × teste, tornada explícita nos cards (07/ago/2026)

Restava um resíduo: os cards afirmam coisas verificadas, mas a *ligação* entre o marco e os
números segue sendo justaposição. "Depois da Kandir a perda cai de 0,66 para 0,44 pp/a" convida à
leitura causal, e o aviso só existia no cabeçalho da seção, longe de onde o leitor está quando lê.

Resolvido com **duas intervenções pequenas**, evitando o parágrafo de ressalva repetido oito vezes:

**1. Um selo curto e idêntico**, renderizado em `timeline.js` (um lugar, não oito):

> Contexto: os números abaixo acompanham o marco, não o testam.

Fica entre a descrição e os cards de métrica, separado por um filete, em corpo 0,7 rem e cor
esmaecida. Sendo **literalmente igual** em todos, lê-se como rótulo e não como prosa: presente
para quem lê com atenção, invisível para quem rola. Não aparece nos marcos de `categoria:
contexto` (1985 e 2024), que são as pontas da série e não têm o que testar — 6 cards ao todo.

Duas versões foram descartadas: *"a série ao lado não testa este marco"* (o "ao lado" depende do
layout, e no celular o mapa vai para cima) e *"nada nesta página testa este marco"* (forte demais:
o #23 chegou a testar alguns, e foi rebaixado, não ausente).

**2. Neutralização dos conectivos causais** que sobravam na redação:

| card | antes | depois |
|---|---|---|
| 1996 | "**Depois dela**, a perda cai de 0,66 para 0,44 pp/a" | "**Entre 1994-98 e 1999-2003**, a perda cai de 0,66 para 0,44 pp/a" |
| 2003 | "**Com** câmbio favorável e **crédito sistematizado**, a perda atinge 0,49 pp" | "...e o câmbio acompanha. **Em 2003** a perda atinge 0,49 pp" |

O card de 2003 ainda carregava "crédito sistematizado", sobra da mesma expressão que já havia sido
corrigida no card de 2002. Saiu junto.

Os cards de 1994 e 2002 não precisaram de ajuste: o de 1994 já se autocorrige na frase seguinte
("a inflexão mais nítida só aparece em 1998, mais perto da Kandir do que do Real") e o de 2002 usa
"enquanto", que é simultaneidade e não sequência.

### Fica em aberto

- **Regerar os PNGs de Cobertura com acentuação e legenda de 7 grupos.** Hoje o PNG diz "Classe (6 grupos)" e o Mosaico aparece como falha branca. A legenda em HTML explica, mas a fonte da verdade continua sendo uma imagem que não menciona a classe.
- **Fogo como anomalia (Z por ato)**, se um dia voltar à página. A sugestão do revisor está certa; o mapa atual (área absoluta, log, Jenks global) não discrimina. Hoje o fogo vive no atlas e no teste da 5ª camada da Perna 1, que é onde ele responde a alguma pergunta.
- **`img/mapas_fogo/` e `img/mapas_delta/`** (80 arquivos) seguem no repositório, sem referência no site. Remover é decisão à parte.
