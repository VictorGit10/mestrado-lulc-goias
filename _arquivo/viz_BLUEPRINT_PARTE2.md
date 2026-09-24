# Blueprint da Parte 2 — copy das 4 pernas

> Prancheta de texto (jul/2026, **revisada em 28/jul/2026**). Arquitetura em
> [`PROPOSTA_REFORMULACAO.md`](PROPOSTA_REFORMULACAO.md); plano de execução em
> [`PLANO_DE_CONSTRUCAO.md`](PLANO_DE_CONSTRUCAO.md). Aqui está a **copy pronta** da
> Parte 2 (o núcleo da investigação), em nível de aprovação: para cada perna há título,
> pergunta de abertura, corpo na voz de descoberta, a **resposta em uma frase** e o
> **"o que isto NÃO diz"**. Tom: sóbrio, editorial (banca + pares), com momentum
> narrativo — não é reportagem. Os números vêm da `narrativa_pipelines.md` e do
> `indice_logico_pipelines.md`.
>
> **Padrão de cada perna:** `PERGUNTA → corpo (descoberta) → RESPOSTA em uma frase → o que não diz`.
> Legenda das notas: 🎞️ = peça interativa que ancora · 🔗 = pipelines/blocos que alimentam.
>
> ### ⚠️ Estado de conferência (28/jul/2026)
> A copy foi **reconciliada com o estado analítico pós-auditorias**. O que mudou nesta
> revisão, e por quê:
>
> | perna | mudança | causa |
> |---|---|---|
> | **2** | corpo, resposta e "não diz" **reescritos** | o gradiente latitudinal de **idade** caiu (#40/#28C/#33, 23–25/jul); a cláusula "a geografia desloca o peso" saiu; a amostra de 78 mil virou **censo de 44,6 M** |
> | **3** | o corpo passa a dizer **qual** dos três ângulos refuta | o nulo de Granger é de **baixo poder** (N≈38). ♻️ **Revisto em 28/jul**: a auditoria da deriva mostrou que a *significância* do spillover também não é robusta (p<0,05 em 1/12 células). A copy passou a apoiar-se na **ausência universal da assinatura prevista** (θ>0 nunca aparece), que é mais forte e não depende de um p-valor |
> | **3** | novo parágrafo: crédito/armazenagem/exportação ficam **atrás** da fronteira | #50/#53/#45 não tinham endereço na peça e fecham a perna por simetria |
> | **4** | "a demanda subiu" ganha lastro medido + ressalva do Δhazard; entra o **#51** | aresta residual da auditoria (hazard embute proteção/atrito); o #51 não tinha endereço |
> | **4** | o −88% do Sul **sai**, entra o `veg→pasto` | a régua crua inverteu sob o bracket D26 (+51%) e o #12B confirmou por recontagem |
>
> **Números conferidos nesta revisão** contra os dados que o site já serve
> (`idade_pastagem_gmm.json`, `sankey_data.json`, `transicoes_resumo.json`) e contra o
> `indice_logico_pipelines.md`. Os que **não** foram reconferidos estão marcados no §"Notas
> de implementação".

---

## Abertura da Parte 2 — a hipótese tentadora (a dobradiça)

> *Transição vinda do fecho da Parte 1 (saldo + Sankey), que respondeu "o quê mudou" e
> "de onde para onde". Esta abertura vira a chave para "onde no estado" e "por quê".*

**A pergunta que o mapa não respondeu.**
Quarenta anos de conversão têm um saldo — vegetação perdida, agricultura multiplicada,
pasto em U invertido. Mas um saldo é mudo sobre a geografia: ele diz *quanto*, não
*onde*. E o "onde" guarda a história de verdade.

Há uma explicação óbvia à espera. Ela diz assim: a lavoura, empurrada pela soja, tomou
o pasto no Sul; o pasto, expulso, recuou para o Norte, levando o boi junto. Seria um
vazamento de desmatamento dentro do próprio estado — um **iLUC intra-estadual**, a
lavoura de um lado empurrando a fronteira do outro. É uma boa história. É a que mais
favorecia a tese inicial deste trabalho.

**E está errada.** O que a investigação encontrou é mais sutil — e melhor documentado.
Ela se responde em quatro perguntas.

---

## Perna 1 — O padrão existe?

🎞️ **Peça-central: a viz interativa das trajetórias** (`marcha-mapa.js`) — o centro de
massa de cada uso da terra caminhando ano a ano, 1985→2024, com a faixa latitude-tempo
sincronizada e o toggle da elipse. É o herói visual desta perna.
🔗 #32 (manchete) · #43 (robustez pixel/MAUP) · #44 (desagregação) · D19 (IC95%).

**PERGUNTA**
> A fronteira agropecuária de Goiás se moveu? E, se moveu, para onde?

**CORPO**
Para responder sem depender de impressão visual, medimos o **centro de massa** de cada
uso da terra — o ponto de equilíbrio geográfico, ponderado pela área de cada classe — e
o acompanhamos ano a ano, sobre as 166 Áreas Mínimas Comparáveis (território constante,
imune às emancipações municipais).

A expectativa era modesta: talvez a agricultura parada e o pasto subindo. O que
apareceu foi mais forte e mais uniforme. **Tudo marchou ao norte.** A pastagem avançou
+78 km; o rebanho, +67; a agricultura, +65. Só a vegetação natural ficou onde estava —
o deslocamento é pequeno e a barra de erro inclui zero, então a leitura honesta é
"**ancorada**", não "andou um pouco". E há um padrão que se repete em *todos* os 40
anos: a lavoura fica sempre ~120–130 km ao sul do pasto e do boi. A fronteira não é uma
linha só — são camadas que sobem juntas, mantendo a distância entre si.

*(Robustez, em uma linha: refizemos o cálculo pixel a pixel, sem nenhuma malha
administrativa — a marcha reaparece a 1–2 km do valor original, então não é artefato de
recorte (MAUP). E, ao abrir a vegetação, a "muralha" que resiste ao norte é a
**floresta**; o campo nativo, esse, também recuou.)*

**A RESSALVA DO CENTRO DE MASSA — beat acrescentado em 28/jul/2026**

*O centroide da agricultura pondera pelo estoque `lulc_agricultura_ha`, e a partir de 2021
a conversão recente migra para "Mosaico de Usos" (#28D/D25). A linha da agricultura
**achata** depois de 2019 — e a peça interativa **mostra** isso. Deixar sem anotação
convidaria a leitura "a agricultura parou em 2020", que este trabalho abandonou.*

**O desenho escolhido: a figura "cinco medidas, uma discorda"** (2019→2024, SVG inline).
É a mesma forma retórica do esquema do #42 na Perna 3 — uma figura pequena que faz o
argumento sem jargão:

| medida | Δ norte 2019→24 | estado |
|---|---|---|
| Pastagem | **+12,9 km** | não exposta |
| Rebanho bovino (SIDRA) | **+11,9 km** | **imune** (campo, não classificador) |
| Soja plantada (SIDRA) | **+10,1 km** | **imune** |
| Agricultura ∪ Mosaico | +4,4 km | teto da janela curta |
| **Agricultura (satélite)** | **+0,5 km** | ← a única cujo rótulo mudou |

A pastagem e o rebanho concordarem (+12,9 × +11,9) **fecha empiricamente** a dúvida sobre
a perna que sobe: se o `pasto→Mosaico` distorcesse o centroide do pasto, ele divergiria do
rebanho, que é imune. Não diverge.

**O fecho, e é ele que transforma a ressalva em ativo:** o centro da massa reetiquetada
fica **+46,5 km ao norte** da agricultura visível, e seu crescimento por AMC correlaciona
**r=0,84** com o da soja SIDRA (1,525 ≈ 1,539 Mha). **O erro de medida aponta contra a
tese** — a régua crua faz a marcha parecer mais fraca do que foi.

**Três decisões de implementação:**
1. **Manchete mantém +65 km** (mesma régua de pasto/rebanho, comparável entre si), com a
   âncora imune declarada na glosa: soja SIDRA **+48 km**, mesma direção, IC exclui zero.
   Não é bracket do mesmo objeto — a soja é o componente dominante da lavoura, não a
   lavoura toda —, e a copy diz isso.
2. **A peça interativa anota:** o trecho da agricultura a partir de 2019 vira
   **pontilhado**, com nota na legenda (`marcha-mapa.js`, `ANO_ROTULO_DERIVA`). Sem isso, a
   figura contradiria o texto — a falha de propagação parcial que já mordeu este projeto
   duas vezes.
3. 🚫 **Nunca reportar a união como bracket de 40 anos.** Ela dá **−60 km** (sul), porque o
   Mosaico de 1985 (3,63 Mha, 10,7% do estado, ao norte) é **outro objeto** que o de 2024 —
   o número mede o Mosaico antigo se dissolvendo, não a lavoura recuando. Um `<details>`
   explica isso na tela, porque está nos CSVs e a banca vai encontrar.

**RESPOSTA (uma frase)**
> Toda a fronteira agropecuária marchou ~65–78 km ao norte em 40 anos — pasto à frente,
> lavoura ~120 km atrás, vegetação natural ancorada.

**O QUE ISTO NÃO DIZ**
Um centro de massa descreve *que* a fronteira andou — não *por que*. E é uma média:
esconde o que acontece dentro. As duas perguntas seguintes atacam exatamente isso. Também
**não** se afirma que a agricultura desacelerou depois de 2020 (é leitura do rótulo; as duas
medidas imunes apontam ao norte), nem se usa a régua corrigida como se valesse para os 40
anos.

---

## Perna 2 — Qual é o mecanismo?

> ♻️ **Reescrita estrutural em 28/jul/2026 — a segunda desta perna, e por outro motivo.**
> A reescrita anterior corrigiu o *conteúdo* (caíram o gradiente latitudinal de idade e a
> cláusula "a geografia desloca o peso da mistura"). Esta corrige a **arquitetura do
> argumento**, a partir da revisão do autor. Quatro defeitos, todos reais:
>
> | defeito apontado | o que se fez |
> |---|---|
> | a perna **abria** afirmando uma diferença Sul×Norte e **fechava** dizendo que não há diferença | os dois registros passam a ser explícitos e sequenciais: a geografia separa **qual transição** (abertura), **não** separa **as duas populações de pastagem** (fecho). O que era anticlímax virou a espinha |
> | a figura não correspondia ao texto — falava em "dois picos" e em linhas tracejadas difíceis de enxergar | figura **substituída** (ver abaixo). A antiga era organizada por Ato, e a própria legenda pedia para não ler variação entre atos: o eixo que estruturava a figura era o que o texto desautorizava |
> | "bimodalidade" não é visível no histograma | **o site parou de afirmar que é.** A copy passa a dizer "um pico jovem e um ombro", e tanto a figura quanto a peça interativa desenham **o ajuste de uma população só** para o leitor ver onde ele falha. É a forma honesta do argumento: a segunda população é larga (σ≈7,5a contra 1,6a), e população larga vira platô, não espiga |
> | os cards pareciam colcha de retalhos | os 3 cards de coorte e os 2 do GMM **saíram como cards** e viraram, respectivamente, o **painel B da figura** (corroboração sem modelo) e as **curvas desenhadas sobre o histograma**. Os 2 cards que sobraram têm função narrativa: são os dois candidatos a explicar a idade, com o veredito de cada um |
>
> Uma quinta mudança veio da mesma revisão e é de **conteúdo**: a copy dizia que o
> cruzamento com plantio direto "desmancha" sob controle de latitude. **Isso é mais forte
> do que o #40 sustenta** — o veredito de lá é *não estabelecido* (p≈0,058; 0 de 8 pares
> sobrevivem a FDR-BH), e o nulo limpo anterior **foi retirado** por ser artefato de erro
> de medida. A tela agora diz "não estabelecido" e explica a diferença.

> ### ⚠️ Segunda rodada da mesma revisão — três correções de fundo
>
> **(a) "O desenho não muda" estava ERRADO na régua que a peça desenhava.** O autor olhou
> os histogramas e disse que Norte e Noroeste pareciam mais bimodais que Sul e Centro.
> Medido (`forma_regional_bimodalidade.py`), o olho estava certo: sob `pasto→agricultura`
> o vale do Noroeste tem profundidade **0,415** e o do Norte **0,271**, enquanto Sul e
> Leste **não têm vale nenhum**; pela distância de variação total as cinco regiões se
> partem em dois blocos (dentro dos blocos TV 0,05–0,09; entre eles **0,18–0,23**). O
> #28C nunca tinha medido isso — ele mede *coexistência*, não *forma*, e as duas podem
> divergir. Sob a régua da união a diferença colapsa (TV Sul×Norte **0,223 → 0,023**;
> vale do Noroeste **0,415 → 0,058**): é o mesmo artefato de rotulagem.
>
> **Consequência estrutural:** a peça desenhava a régua exposta enquanto o texto ao lado
> afirmava a conclusão da união — a mesma classe de defeito de quando o mapa pintava a
> amostra sob manchete de censo. A peça passou a oferecer **as duas réguas**, com a imune
> por padrão, e a troca virou o beat mais didático da perna. Novo bloco de copy: *"A régua
> que muda a resposta — e por que a resposta certa é uma só"*.
>
> **(b) O fio do crédito foi RODADO** (`duas_logicas_bracket_fluxo.py`). Δ SICOR × idade
> mediana, parcial | lat+lon: **sobrevive à união e se fortalece** (+0,22 → **+0,30**,
> p<0,0001, passa o FDR em 2 janelas em vez de 1). Não é artefato de rotulagem — e a
> assimetria com o gradiente latitudinal (que morreu) é ela própria informativa. **Mas**
> na janela limpa (≤2019) o coeficiente é ~zero nas duas réguas: a associação só existe
> com os anos recentes dentro, e isso *não* pode ser creditado ao Mosaico (a união é imune
> por construção). O card da tela deixou de dizer "não foi testado" e passa a dizer o que
> é: real, invertida em sinal, recente, sem mecanismo.
>
> **(c) Terminologia corrigida — duas frases que não se sustentavam.**
> - **"giro de lavoura"** era termo inventado. Vira **"pasto de ciclo curto"**, com o nome
>   técnico ao lado (*rotação lavoura-pastagem*) e a ressalva de que é **compatível** com
>   ILP sem prová-la: o satélite vê o capim, não vê o boi.
> - **"plantio direto = proxy de ILP"** é frouxo demais. Plantio direto é **conservação de
>   solo**; o Censo Agropecuário **não tem** variável de ILP, e foi por isso que o no-till
>   entrou — por ser o mais próximo, não por ser o certo. O que ele indexa é lavoura de
>   grãos tecnificada. A tela agora declara isso antes de apresentar o teste.

🎞️ **Peça-central: a interativa da idade do pasto** (`reserva-perna2.js`) — **o clique saiu
dos botões e foi para o mapa**. Antes: mapa por AMC de um lado, fileira de 6 pastilhas por
mesorregião do outro, duas malhas sem relação visível na tela. Agora o contorno dissolvido
das 5 mesorregiões (`malha_mesorregiao.geojson`) fica **sobre** as 166 AMCs e recebe o
clique; as AMCs continuam desenhadas por baixo porque são elas que sustentam o "162 de
164". Selecionar uma região vela as outras e redesenha o histograma — que continua com as
duas populações. **Segundo controle: a régua** (`pasto→lavoura ou uso misto` × `só
pasto→lavoura`), que redesenha os DOIS painéis ao mesmo tempo, porque o veredito por AMC
e a forma do histograma mudam juntos. A interação *é* o argumento.

> A legenda do histograma saiu de dentro do SVG e virou HTML abaixo do gráfico, no mesmo
> componente da legenda do mapa. Dentro do SVG ela competia com as curvas por espaço e
> encolhia junto com o `viewBox` — no celular ficava com ~6 px.

> ⚠️ `reserva-perna2.js` e `reserva-perna2.css` são **fork deliberado** de
> `pastagem-reserva.js` / `reserva.css`. O `index.html` no ar tem outra marcação (pastilhas,
> 3 cards de coorte) e continua servido pelo módulo antigo, intocado, conforme a estratégia
> de arquivo paralelo. **Na troca final, o módulo antigo é apagado junto com o `index.html`
> antigo.** (`reserva.css` segue carregado pelos dois: a base é comum, o fork só acrescenta.)

🔗 #33 (mecanismo por mesorregião) · #28/#28C (o censo da idade, coexistência) · #22/#22B
(substituição local; intensificação *within*) · #49 (M3 robusto, M1 frágil) · #40/#40B (a
autocorreção da latitude, D14) · #28D (a mudança de rótulo, D25/D26).

🖼️ **Figura-âncora: `sintese_idade_duas_populacoes.png`** (gerada por
`Visualizacao/scripts/gerar_grafico_duas_populacoes.py`), dois painéis **empilhados** —
empilhados porque a coluna do site tem 760 px e lado a lado ficaria ilegível:
- **A — "Uma população só não produz esta curva."** Histograma bruto + o melhor ajuste de
  **uma** gaussiana (tracejado) + as duas componentes. O tracejado erra o pico e erra a
  cauda: é assim que a bimodalidade fica visível quando não há dois picos.
- **B — "A mesma divisão sem ajustar modelo nenhum."** Composição por **origem anterior** ao
  longo da idade. Entre o pasto convertido aos 3 anos, **50%** veio de lavoura; entre o
  convertido aos 33, **1%**. O Mosaico tem faixa própria (D25/D26), não é somado à rotação.
- 🚫 `sintese_idade_pastagem_atos.png` **sai da Perna 2**. Continua no repositório como
  export do #28, mas não volta para esta seção.

**PERGUNTA**
> Se a fronteira inteira marchou, que conversão — e em que parte do estado — a moveu?

**CORPO — em cinco movimentos**

**1. A geografia responde, e responde bem — mas só metade.** A marcha é o saldo de duas
conversões diferentes, e elas não estão no mesmo lugar. No Sul manda **pasto → lavoura**:
intensificação. No Norte, **mata → pasto**: fronteira. Dois Goiáses. A medida que sustenta
a divisão é a que **não** depende da classe ambígua do satélite — o `veg→pasto`, que
despenca **−49% no Sul** entre os Atos II e III e cede só **−13% no Norte**. Isso responde
*onde*, não *como*: saber que o Sul converte pasto em lavoura não diz se aquele pasto era
etapa planejada de um sistema agrícola ou fazenda parada há vinte anos.

**2. A medida que revela a intenção.** Pasto de três anos que vira lavoura foi plantado já
pensando nisso; pasto de vinte e cinco anos é terra parada que uma oportunidade tornou
lucrativa. A **idade da pastagem no instante da conversão** é a coisa mais próxima da
intenção do produtor que um satélite consegue ver. Censo, não amostra: **44,6 milhões** de
conversões (3,8 Mha, 11,2% do estado), das quais **16,0 milhões** com idade conhecida — as
outras já eram pastagem em 1985 e têm a idade truncada.

**3. Duas populações, não dois picos.** A curva bruta é decrescente: um pico jovem e um
ombro longo. O que estabelece a segunda população não é enxergar um segundo pico — é uma
população só não dar conta da forma. Jovem: μ≈3,9a, **σ≈1,6a**, 33% da massa. Velha:
μ≈16,3a, **σ≈7,5a** (5× mais larga, por isso vira platô), 67%. E a mesma divisão aparece
**sem modelo nenhum**, pela origem: pasto que veio de lavoura tem mediana **5a**; pasto que
veio de vegetação nativa, **13a** com cauda longa. Nomes: **pasto de ciclo curto**
(*rotação lavoura-pastagem*; compatível com ILP, não prova de ILP — o satélite não vê o
gado) e **reserva ativada**.

**4. A hipótese natural cai — e o que fica é mais forte.** Se o Sul intensifica e o Norte
abre, o esperado seria uma população em cada metade do estado. Esta investigação chegou a
afirmá-lo. Não sobrevive: **5 de 5** mesorregiões e **todas as 166** AMCs são bimodais *por
dentro*, e a mesorregião explica **0,5%** da variação da idade. Quanto menos a região
explica, mais universal fica o par de mecanismos.

**4b. A régua que muda a resposta.** Beat novo, e o mais didático da perna. Trocando para a
régua estrita, o desenho **passa a mudar**: Norte e Noroeste ganham vale nítido (0,271 e
**0,415**), Sul e Leste não têm nenhum, e as cinco regiões se separam em dois blocos pela
distância entre formas. É real — e é o artefato: o rótulo perdido some mais ao norte, e o
que sobra lá é amostra enviesada para a ponta velha. Fechado o buraco, TV Sul×Norte cai de
**0,22 para 0,02** e o vale do Noroeste de **42% para 6%**. ⚠️ Ressalva na tela: mesmo na
união o Noroeste guarda um vale raso — a frase certa é "praticamente o mesmo desenho",
nunca "idêntico".

**4c. Segundo eixo: e se forem apenas épocas diferentes?** A objeção "isso é só composição"
tem duas versões, e até 28/jul a perna só respondia uma. Se Goiás converteu pasto novo nos
anos 1990 e velho nos 2020, somar as décadas fabrica duas populações que nunca coexistiram —
dois regimes em sequência, não dois mecanismos em paralelo. Isolando cada período: **10 de 10**
células período×região na régua imune (9/10 na estrita; falha Noroeste × Ato II por peso).
O **Ato I é unimodal em toda parte — e não poderia ser outra coisa**: conversão em 1995 se dá
sobre pasto de no máximo 10 anos, e para *enxergar* pasto de 22 anos é preciso chegar a 2007.
A população velha ali é **invisível, não ausente**; por isso a contagem começa no Ato II. É o
beat que mais ensina a ler janela de observação, e ele fecha a simetria: o movimento seguinte
passa a ser *"Se não é a região **nem a época**…"*.
⚠️ Contrapartida obrigatória no "não diz": nem Ato I unimodal = "a reserva surgiu depois",
nem vale mais fundo no Ato III = "os grupos estão se separando". Nos dois casos lê-se a
janela.

**5. Então o que decide a idade? Nada que estes dados alcancem.** Duas famílias de
explicação, cada uma com previsão falsificável. **Estrutura** — o plantio direto, proxy de
o indicador mais próximo de sistema tecnificado que o Censo Agropecuário oferece — **não**
é variável de ILP, que o Censo não tem, e é conservação de solo, não integração com
pecuária. Com a ressalva declarada: se a população jovem é pasto de ciclo curto,
municípios com mais plantio direto deveriam converter pasto mais novo. Na bivariada,
confirma; segurando o gradiente espacial, encolhe cerca de um terço, fica **na fronteira** da
significância e **não sobrevive a FDR-BH**: **não estabelecido**. **Fluxo** — o crédito
rural: é a única associação que resiste ao controle, à multiplicidade **e à troca de
régua** — na união ela se fortalece (+0,22 → **+0,30**), então **não é** artefato de
rotulagem. Mas o sinal é **invertido** (mais crédito → pasto **mais velho**), ela **só
existe com os anos recentes dentro** (≤2019 dá ~zero nas duas réguas) e o mecanismo não foi
investigado. A dupla ausência é o
resultado: a escolha entre girar o capim em três anos ou deixá-lo trinta acontece **abaixo
da escala destes dados** — no talhão, na fazenda. Aponta para dados fundiários por imóvel.

**RESPOSTA (uma frase)**
> O mecanismo são **duas populações de pastagem convertidas em paralelo** — pasto de ciclo
> curto, em três a cinco anos, e reserva antiga ativada quinze, vinte, trinta anos depois. A geografia
> separa *qual transição* domina cada metade do estado, mas **não** separa essas duas
> populações: elas convivem em praticamente toda célula do território, e o que decide entre
> uma e outra está abaixo do alcance destes dados.

**O QUE ISTO NÃO DIZ**
Que a curva tem *dois picos visíveis* — não tem: tem um pico e um ombro. Que a região
*causa* a divisão (foi medido: 0,5%). Que "o Sul converte pasto jovem e o Norte, pasto
velho" — esteve nesta investigação e caiu por três caminhos independentes. Sobre o plantio
direto, **nem que explica nem que está descartado**: a evidência não decide, e chamar isso
de refutação repetiria um erro já cometido aqui. E nada sobre **tendência**: o eixo do tempo
está comprometido dos dois lados (idade truncada antes, mudança de rótulo depois).

**DOIS BLOCOS RECOLHIDOS** (`<details>`, para não pesar a leitura corrida)
- *"Como se soube que o gradiente regional era falso"* — a autocorreção: a idade só é medida
  sob o rótulo `agricultura`, esses eventos somem mais ao norte, e sob
  `pasto → (agric ∪ mosaico)` a amplitude cai de **7a para 2a**, a ordem embaralha e o η² vai
  de 3,7% a **0,5%**. O que **não** mudou: a coexistência (5/5 regiões; 9/10 → **10/10**
  células). Fecha explicando por que a peça pinta veredito e não idade.
- *"Por que 'não estabelecido' e não 'refutado'"* — o nulo limpo do plantio direto foi
  **retirado**: medido sobre desfecho ruidoso, era indistinguível de falta de poder; com a
  idade medida pelo censo nos mesmos municípios, a associação cruza o limiar usual. Termina
  na **D14** e no corolário de que os dois lados de uma comparação precisam do *mesmo*
  controle.

**SEM DATAS NA TELA.** A perna conta *como* a investigação se corrigiu, não *quando* —
"por algumas semanas este trabalho disse X" vale como narrativa; "em 23/jul/2026" não
acrescenta nada ao leitor e envelhece a peça. As datas ficam nesta prancheta e nos
pipelines.

---

## Perna 3 — É a lavoura do Sul empurrando o Norte? *(o clímax)*

> ⚠️ **Esta seção foi reescrita em 28/jul/2026 pela revisão do autor.** A copy abaixo é a
> versão **antiga** e está mantida só como registro do que mudou. A versão em vigor vive no
> `reforma.html` e está descrita em [`PLANO_DE_CONSTRUCAO.md` §16](PLANO_DE_CONSTRUCAO.md).
> O que a revisão mudou, em uma linha cada: **(a)** a perna ganhou os cinco `h4` que as
> Pernas 1 e 2 já tinham, no lugar de quatro parágrafos corridos; **(b)** a pergunta passou
> a ser *"O pasto que o Sul perdeu é o pasto que o Norte ganhou?"*, que engancha direto na
> Perna 2, e a abertura passa a **montar** a hipótese antes de testá-la; **(c)** o beat novo
> *"o que precisaria aparecer"* explicita as duas assinaturas **antes** dos resultados;
> **(d)** duas figuras novas — a das **12 especificações** (o argumento-manchete, que antes
> não tinha figura nenhuma) e a do **teste de simetria** (que antes era um parágrafo);
> **(e)** o `veredito.png` do #42 foi **removido** (jargão, e redundante com o esquema SVG),
> virando um `<details>` de método; **(f)** o veredito deixou de dizer **"refutada"** — ver
> abaixo.

🎞️ Ancora nas figuras do #34 (lead-lag / spillover direcional) e no painel de
autocorreção do #42. É a única perna sem peça interativa — compensa com um **esquema
estático de 2 painéis** (ver abaixo) além das figuras, e com a **voz narrativa**.
🔗 #34 (o teste formal: o nulo **e** o spillover de sinal trocado) · #42 (o Granger reverso,
espúrio — a peça-modelo) · #37/#38/#52/#54 (o drive comum, corroborante) · #41 (fogo,
vanguarda geográfica não temporal) · #45/#53/#50 (as camadas que **consolidam** e não
lideram: exportação, armazenagem, crédito).

**Esquema estático do #42 (mini-figura, 2 painéis)** — *(não é copy, é direção visual; o
desenho final vive no HTML, mas o conceito congela aqui porque é o que torna "espúrio"
visível sem jargão).*
- *Painel A — o "resultado que invertia a tese":* duas linhas suaves e paralelas subindo
  juntas (Norte pasto, Sul pasto), com uma seta "antecede?" apontando do Norte para o Sul.
  Legenda curta: *"Rodado ao contrário, o teste dava significativo — o Norte 'anteciparia'
  o Sul."*
- *Painel B — a prova de que é espúrio:* as mesmas duas linhas, agora com uma terceira
  igualmente lisa e sem relação (ex.: consumo de cerveja per capita, marcado como "qualquer
  série nortenha suave"), também "antecipando" o Sul. Legenda: *"Qualquer série lisa
  'prevê' qualquer outra — até o pasto do Sul por ele mesmo. Com o método certo para séries
  integradas (Toda-Yamamoto), a precedência some nas duas direções."*
- A mini-figura carrega a ideia que o corpo da perna já explica em texto: dá ao leitor um
  *aha* visual no ponto mais denso da peça. Repete o tom dos outros "o que isto NÃO diz".

**PERGUNTA**
> Então foi a lavoura do Sul que empurrou o pasto e o boi para o Norte?

**CORPO**
Esta é a hipótese que mais favorecia o trabalho — a história limpa do iLUC
intra-estadual. Por isso ela foi testada com o maior rigor, em tempo contínuo, de três
ângulos. Nenhum a sustenta — mas eles não pesam igual, e a diferença importa.
**Primeiro:** não aparece precedência temporal — a lavoura do Sul não antecede o pasto do
Norte (p=0,97). É um nulo, e um nulo com 38 anos de série tem pouco poder: ele não *prova*
ausência, apenas deixa de encontrar. **Segundo:** onde o empurrão espacial deveria aparecer, o
sinal vem **trocado**. A hipótese exige um coeficiente positivo; ele é **negativo nas doze
especificações testadas**, sem exceção (3 réguas × 2 janelas × 2 desfechos, auditoria de
28/jul). Não é um número que refuta — é a ausência de um: a assinatura que a hipótese pede
não aparece em régua nenhuma. **Terceiro:** o único efeito forte é *local* — onde a lavoura entra, o pasto
sai ali mesmo (β=−0,52): é intensificação, não expulsão à distância. O veredito: não é
deslocamento causal de uma região sobre a outra. É **reorganização espacial** — dois
mecanismos locais paralelos sob um mesmo impulso.

E então veio a parte que mais orgulha o trabalho. O teste anterior tinha deixado uma
ponta solta: rodado ao contrário, ele dava um resultado significativo — *o Norte
anteciparia o Sul* — que, se fosse real, viraria a tese de cabeça para baixo. Seria fácil
varrer para baixo do tapete com um "N é pequeno". Em vez disso, fomos atrás. E provamos
que era **regressão espúria**: a série do pasto do Norte é tão "lisa" (integrada de ordem
2) que qualquer série nortenha suave "prevê" qualquer série sulista suave — o Norte
"antecede" até o pasto do próprio Sul, o que nenhum mecanismo econômico explicaria. Com o
método correto para séries integradas, a precedência **some nas duas direções**. Não há
líder temporal; há co-movimento.

Se ninguém empurra ninguém, o que coordena os dois mecanismos e dá o compasso da marcha?
Um **impulso macro comum** — câmbio, crédito e preço agindo sobre um gradiente de aptidão
que já estava no chão. O candidato mais forte é o câmbio real. Mas aqui a honestidade
pesa: sob a inferência correta para esse tipo de desenho, o achado é **corroborante, não
estabelecido** — o que o sustenta é a especificidade (os placebos dão nulo, não há
antecipação, o resultado não depende de um ano isolado), não a significância estatística.

Há ainda um teste de simetria que raramente se faz e que fecha bem esta perna: se alguma
infraestrutura *puxasse* a fronteira, seu centro de gravidade estaria à frente dela. Está
atrás — em todas as camadas medidas. O centroide do **crédito** fica ~75 km ao sul da
pastagem; o da **capacidade de armazenagem** (CONAB) é a camada mais meridional de todas,
~150 km ao sul do pasto e ~83 km ao sul até do próprio crédito; e a cadeia **exportadora**
co-move sem liderar. Silo, banco e porto **consolidam o núcleo** — eles chegam onde a
produção já está. Nenhum deles é a ponta da marcha.

**RESPOSTA (uma frase)** — 🚫 **versão antiga, retirada em 28/jul/2026**
> ~~A lavoura do Sul **não** empurra o Norte — a hipótese de deslocamento causal foi testada
> e refutada; os dois mecanismos são coordenados por um impulso macro comum sobre um
> gradiente de aptidão.~~

**O problema com ela**, levantado pelo autor na revisão: "**refutada**" afirma mais do que
o desenho sustenta, e afirma **contra o próprio pipeline**. O #34 registra, nas suas
limitações, que o teste espacial é *local e contemporâneo* e "**não descarta** deslocamento
de longo alcance ou de defasagem muito longa"; e a simulação de poder dá **~48%** para um
efeito temporal moderado. Pior: a Parte 3 da mesma página já dizia, na lista de
fragilidades, "iLUC: **não confirmado, não refutado em absoluto**" — a peça se contradizia
a duas telas de distância. E "refutada" é a palavra **mais fácil de derrubar numa banca**:
a primeira pergunta é "com que poder?".

**RESPOSTA (uma frase)** — ✅ **em vigor**
> **Não.** A assinatura que um empurrão do Sul sobre o Norte exigiria não aparece em nenhum
> dos doze recortes espaciais nem dos vinte e quatro temporais — e o que aparece no lugar é
> substituição *local*, forte em todos eles. Os dois mecanismos não se comandam: são
> coordenados por um impulso macro comum sobre um gradiente de aptidão.

A troca não enfraquece a perna, **muda o tipo de argumento**: sai um veredito apoiado em
p-valor, entra um apoiado em **especificidade** — previsão arriscada, procurada em 36
recortes com placebos e três réguas independentes, nunca encontrada, enquanto a explicação
rival aparece em todos. É o mesmo movimento do [#54](../../Textos/pipelines/54_defensabilidade_perna4.md)
na Perna 4 e o que a auditoria do [#34](../../Textos/pipelines/34_deslocamento_espacial.md)
já mandava escrever.

**O QUE ISTO NÃO DIZ** *(ampliado — era um parágrafo, virou cinco)*
Que o iLUC não existe — apenas que o **canal intra-estadual, local e contemporâneo** que
foi procurado não aparece; canal de longo alcance, de defasagem longa, ou que **atravesse a
divisa de Goiás** (soja daqui deslocando pecuária para o Pará/Maranhão) não foi testado e
segue aberto. Que a hipótese foi refutada em absoluto — o nulo temporal tem ~48% de poder
para efeito moderado. Que "o Sul lidera" — o Toda-Yamamoto zera a precedência nas **duas**
direções (p=0,45 e 0,25), e isso corta para os dois lados. Que o câmbio é causa provada — é
corroborante, e não se cita o p agrupado (0,026/0,031) como significância; o correto é
≈0,07–0,13. E nada sobre infraestrutura além da **posição**: os centroides são descritivos.

---

## Perna 4 — Por que a marcha desacelerou?

🎞️ Ancora no mapa/figuras do #39 (estoque convertível por região) e do #47 (centroide da
perda de carbono). Pode reusar a camada de fronteira/estoque.
🔗 #39 (o teto de oferta, decomposição) · #46 (97% desprotegido, D17) · #48 (validação
PRODES, r=0,91) · #47 (custo de carbono) · **#51** (crescimento sem desenvolvimento —
beat novo, ver nota abaixo) · #33 (o `veg→pasto` imune que substituiu o −88%).

> 📌 **Beat novo nesta revisão (28/jul/2026): o #51 entra na Perna 4.** Ele não existia no
> blueprint de 25/jul e não tinha endereço em lugar nenhum da peça. Entra aqui porque a
> Perna 4 é a única que já fala em **preço da marcha** (o carbono do #47): "o que custou"
> ganha duas contas em vez de uma. Se o teste de leitura mostrar que alonga demais a perna,
> a alternativa é movê-lo para a Parte 3 como coda — **não** cortá-lo, porque é o achado mais
> comunicável do conjunto para fora da academia.

> ♻️ **Seção revisada em 28/jul/2026 — o que está abaixo em "PERGUNTA / CORPO / RESPOSTA"
> é REGISTRO HISTÓRICO.** A revisão do autor encontrou aqui os mesmos sintomas da Perna 3
> (pouca estrutura, figuras que não casam com o texto, veredito mais forte que a evidência),
> mais um defeito novo e pior: **a figura publicada contradizia a manchete**. A copy em vigor
> é a de `reforma.html`; ver `PLANO_DE_CONSTRUCAO.md` §18. Três pontos mudam de conteúdo:
>
> 1. **"A marcha desacelerou" é falso no estado.** O fluxo de conversão de Goiás vai de
>    0,071 a 0,072 Mha/ano do Ato II ao III — não desacelerou, **mudou de endereço**. Quem
>    freou foi o Sul (−37%). A perna passa a abrir corrigindo a própria pergunta.
> 2. **A decomposição não mede a oferta.** Só **17%** do freio do Sul é o estoque menor; 83%
>    é a taxa caindo, e a taxa é um **resíduo**. A leitura de oferta vem de eliminação
>    (demanda no pico + proteção desprezível) e do teste da taxa plana (p=0,48). Declarado na
>    perna e agora com dono em `p4-limites`.
> 3. **O beat que faltava** e fecha o argumento: no Sul do Ato III a conversão de pasto em
>    lavoura-ou-uso-misto **sobe 51%** e a soja plantada **sobe 244%** — a procura por terra
>    subiu; o que secou foi a **fonte**.
>
> Correções de número: `+93%/+14%` é **2013→2021** (era "2013–2023"; a janela de crescimento
> para no lag do IBGE), e o desprotegido vira **94–97%** (97% pelo proxy vetorial, 94,3% no
> refino pixel do #46). E a frase *"não converte em bem-estar"*, abaixo, é **proibida** pelo
> #51 — já corrigida na peça, mantida aqui só como registro do que foi escrito.

**PERGUNTA** *(registro histórico)*
> No Ato III (2020–24) a lavoura do Sul desacelera. Acabou a demanda?

**CORPO** *(registro histórico)*
A resposta intuitiva — "esfriou o mercado" — está errada, e é o que torna esta perna
interessante. No Ato III os sinais de demanda **subiram**: câmbio, preço e crédito, todos
em alta, e a soja plantada que o IBGE mede em campo cresce 38%. A abertura de terra nova no
Sul freou **enquanto a demanda apertava**. Isso não é assinatura de demanda fraca; é
assinatura de uma restrição de **oferta** — a terra acabando.

E acabou de forma desigual. No agregado do estado, a fronteira *não* fechou: ainda resta
cerca de **60%** do Cerrado convertível, e o fluxo de conversão não caiu — só **migrou ao
norte**. Mas, olhando por região, no Sul ela fechou: o estoque convertível está em **~53%**
do que era em 1985, e a abertura de vegetação nativa cai **−49%** lá contra **−13%** no
Norte. A "marcha ao norte" é, em boa parte, a fronteira **perseguindo a terra que só resta
no norte**. E a terra que resta está **97% desprotegida** — o teto é **físico, não
institucional**: não é a lei que segura a conversão, é o fim do estoque acessível.

O que essa marcha custou tem duas contas, e nenhuma delas é econômica no sentido usual. A
primeira é de carbono: precificada por diferença de estoque, a conversão emite da ordem de
**~973 Mt de CO₂e** (751–1208 conforme o cenário de densidade), com a **floresta dominando
a emissão** embora perca 2,6× menos área que o savânico. A segunda é humana e mais
desconfortável: entre 2013 e 2023 a fronteira norte quase **dobrou a área** cultivada
(+93%, contra +14% no Sul) e terminou o período com desenvolvimento municipal **abaixo** do
Sul — a expansão de área é praticamente **desacoplada** do desenvolvimento. Abrir terra
nova, medido assim, não converte em bem-estar onde ela é aberta.

**RESPOSTA (uma frase)** — ⛔ *substituída*
> A desaceleração do Sul não é falta de demanda — é o estoque de Cerrado convertível se
> esgotando (um teto de oferta **físico**), e a marcha ao norte é a fronteira perseguindo
> a terra que só resta lá.

**RESPOSTA (uma frase)** — ✅ **em vigor**
> **Não acabou a demanda — ela estava no pico.** O que o Sul perdeu foi a *fonte*: seu
> Cerrado convertível é o menor e o mais gasto do estado (53% do que havia em 1985,
> praticamente parado desde 2019), e a procura por terra que continuou lá passou a ser
> atendida por pasto já aberto. A marcha ao norte é, em parte, a fronteira seguindo o estoque
> que só resta no norte — e o teto que ela encontra é **físico, não institucional**.

**O QUE ISTO NÃO DIZ** *(registro histórico — ampliado na peça, ver §18)*
Que se conhece o estoque **cadastral** de terra: "convertível" e "protegida" são proxies
com teto declarado (MapBiomas + malha de unidades de conservação), não o CAR pixel a pixel.
Que a queda do *hazard* de conversão seja, por si, "queda de demanda" — o hazard embute
também proteção, atrito e intensificação; quem sustenta a leitura de oferta é o teste do
plano estoque×hazard, não o rótulo. E o Ato III tem **cinco anos**: é um sinal inicial, não
um regime consolidado.

---

## Ponte para a Parte 3 (o veredito)

> *Fecho da investigação, entrada do veredito.*

Quatro perguntas, quatro respostas — e a hipótese óbvia derrubada pelo caminho. O que
sobra não é a história simples do "Sul empurra o Norte", mas uma mais precisa: **uma
reorganização espacial coordenada, sob forças de mercado comuns e um teto de oferta**. A
Parte 3 fecha com essa tese em uma frase — e com a coisa mais rara do trabalho, o que dá
razão para confiar nela: **uma investigação que foi atrás dos próprios erros antes que a
banca fosse.**

---

## ✅ Estado dos dados da Perna 2 — RESOLVIDO (25/jul/2026)

> **Fechado em 25/jul/2026.** Os três problemas abaixo estão corrigidos no site; o
> diagnóstico fica como registro do que era e de por que mudou. O que foi feito:
>
> | item | o que foi feito |
> |---|---|
> | geojson órfão com dados da amostra | virou **`malha_amc.geojson`** — só identidade e geometria, gerado por `scripts/export_malha_amc_viz.py`. O nome mudou de propósito: uma malha chamada "idade_pastagem" convida a repintar idade nela |
> | coroplético de idade por AMC | **substituído**: o mapa agora codifica o **veredito de bimodalidade** por AMC (162 bimodais · 2 unimodais · 2 sem ajuste), lido do censo em tempo de execução. Um mapa quase uniforme é a forma visual do η² de 0,5% |
> | cards com números da amostra | lidos de `idade_pastagem_gmm.json` (janela 2016–24): μ₁ 4,2a / 31,5% e μ₂ 22,5a / 68,5%. O texto declara o que estava lá antes |
> | 3 JSONs do censo não cabeados | `idade_pastagem_regional.json` alimenta mapa + histograma (toggle passou de **Ato → região**, que era o desenho da Opção A); `_gmm.json` alimenta os cards; `_municipal.json` alimenta a nota de cobertura (244 municípios, mínimo 182 eventos) **e** a mesorregião de cada AMC no export da malha |
> | `idade_pastagem_histograma.json` (por Ato) | **deliberadamente não consumido** — o eixo temporal está suspenso. Fica como export do #28; não é ponta solta, é decisão registrada |
> | Mosaico escondido em "Outros" | ganhou **faixa própria listrada** na barra empilhada (10,5% do estado em 2024, contra 1,0% de tudo o mais somado) e entrada na legenda, que declara que o raster GEE não o pinta |
> | copy do gradiente | retirada do §6, do §8 (o "−88%"), do §11 e dos dois cards de autocorreção do §12 — ver o aviso na seção anterior |
>
> Verificado com Playwright: 166 AMCs desenhadas, toggle de 6 regiões redesenhando,
> console limpo, e varredura confirmando que as sete frases retiradas não estão mais no DOM.

**Diagnóstico original (21/jul/2026), preservado como registro.** Eram três problemas
independentes, em ordem de gravidade.

### 1. A copy desta página estava na era da amostra ✅ *(corrigido em 28/jul/2026)*

O corpo da Perna 2 dizia **"Amostramos ~78 mil pontos"** e **"o Norte, pasto de ~20
[anos]"**. Ambos caducaram: o #28 virou **censo** em 21/jul/2026 — **44,6 milhões de
eventos**, 3,8 Mha, 11,2% de Goiás. Ver
[28_idade_pastagem.md](../../Textos/pipelines/28_idade_pastagem.md). **A correção da copy
só aconteceu em 28/jul** — três dias depois de o *site* já ter sido corrigido: a prancheta
ficou atrás da tela que ela deveria especificar. Vale como lição de processo, e é por isso
que o `PLANO_DE_CONSTRUCAO.md` põe a ordem "blueprint → HTML" por escrito.

*(As duas medianas regionais — Sul 9a / Norte 16a — que apareciam aqui como a correção
"certa" **também caíram** dias depois, no bracket da D26. Não use nenhum dos dois pares.)*

### 2. O site publicado mostra dados da amostra sob manchete de censo

Diagnóstico de 21/jul/2026, ainda **não corrigido**:

| item | estado |
|---|---|
| `assets/data/idade_pastagem_amc.geojson` | ❌ **é a amostra** — 43.951 px (= 78.000 − 34.049 fora de GO) contra 44.639.028 do censo. É o que o coroplético do §6 renderiza (`pastagem-reserva.js:227`). Arquivo **órfão**: nenhum script do repo o gera |
| Cards "μ ≈ 4,6 a (44%)" / "μ ≈ 21,8 a (56%)" (`index.html:812`, `:822`) | ❌ números da amostra; o censo dá μ₁ 4,24a **w₁ 31,5%** / μ₂ 22,49a w₂ 68,5% para a mesma janela — e a prosa 3 linhas abaixo já diz "31%", então a seção se contradiz |
| `idade_pastagem_municipal.json`, `_gmm.json` | ⚠️ regerados do censo mas **não consumidos** por nada na viz |
| `idade_pastagem_regional.json` (541 KB, malha meso "Opção A") | ⚠️ export da própria reforma, **não cabeado** |
| `28_idade_pastagem.md:418` | ❌ afirma que os 4 arquivos "foram regerados a partir do censo" — falso para o geojson |

O `marcha-mapa.js` também carrega o geojson, mas só pela geometria — lá é
inofensivo.

### 3. O eixo temporal da Perna 2 está suspenso

O [#28D](../../Textos/pipelines/28D_deriva_mosaico.md) (21/jul/2026) mostrou que
o objeto medido pelo #28 **não é constante ao longo da série**: a saída da
pastagem migra do rótulo "agricultura" para "Mosaico de Usos" (razão 0,6 em 2015
→ **32,5 em 2024**) enquanto o SIDRA registra a soja **crescendo 38%**.

**Consequência para a copy:** qualquer frase do tipo "o pasto jovem vem ganhando
peso" / "a rotação avança" **não pode entrar**. A tendência de w₁ acompanha a
deriva. O contraste "tempo explica 20%, região explica 2,5–7,3%" — que a nota de
números a conferir abaixo ainda lista — **está suspenso**: os dois lados do eixo
temporal estão comprometidos (horizonte antes de 2020, deriva depois).

**O que continua firme e sustenta a Perna 2 como está desenhada:** a
**bimodalidade** (μ₁≈4-5a, μ₂≈21-23a, estáveis em toda janela testada) e o
**gradiente Sul→Norte** do #28C, que é transversal. A tese da perna — "dois
mecanismos coexistem em toda parte; a geografia desloca o peso da mistura" — **é
justamente a parte que sobrevive**, porque é uma afirmação sobre forma e
espaço, não sobre tendência temporal. A peça interativa segue de pé; o que sai é
a narrativa de *avanço no tempo*.

> ### ⚠️ O parágrafo acima está ERRADO na segunda metade — corrigido em 23–25/jul/2026
>
> O argumento "**o gradiente é transversal, logo imune à deriva**" foi explicitamente
> **refutado**. Ele confunde *quando a deriva ocorre* com *o que ela seleciona*: a
> mudança de rótulo atua **dentro** de um período, escolhendo quais eventos ficam
> visíveis sob a classe "agricultura". Um corte transversal feito sobre esse
> subconjunto herda a seleção inteira.
>
> Três testes independentes derrubaram o gradiente latitudinal de **idade**:
>
> | teste | régua crua | sob `pasto→(agric∪mosaico)` |
> |---|---|---|
> | amplitude Sul→Norte da mediana (#28C) | 7 anos | **2 anos**, ordem embaralhada |
> | η² da mesorregião sobre a idade (#28C) | 3,7% | **0,5%** |
> | índice-jovem × latitude (#40, bracket por evento) | ρ significativo | **ρ ≈ 0, ns nas 3 janelas** |
> | idade mediana no Ato III (#33) | Sul 16a · Norte 27a | **Sul 32a · Norte 23a — inverte** |
>
> **A tese da perna, corrigida:** "dois mecanismos coexistem em toda parte" —
> ponto. A cláusula "e a geografia desloca o peso da mistura" **sai**. A parte que
> sobrevive sobrevive **reforçada**: quanto menos a região explica (0,5%), mais
> forte fica o "em toda parte" (5/5 mesorregiões, 162/164 AMCs bimodais por dentro).
> Ver o WARNING no topo de [`28C_bimodalidade_regional.md`](../../Textos/pipelines/28C_bimodalidade_regional.md).

---

## Notas de implementação (não é copy)

- **Cada "RESPOSTA em uma frase"** deve ter tratamento visual consistente (o mesmo
  componente da tese-callout, em versão menor) — é o batimento que se repete 4×.
- **"O QUE ISTO NÃO DIZ"** entra como bloco discreto (aside/nota), presente nas 4 pernas
  — é a marca de honestidade e o que amarra com a D14.
- **Números da copy — estado de conferência (28/jul/2026).** ✅ = conferido nesta revisão
  contra o dado que o site serve ou contra o `indice_logico_pipelines.md`; ⏳ = herdado, a
  reconferir na hora de cabear.

  | número | perna | fonte | estado |
  |---|---|---|---|
  | marcha +78 / +67 / +65 km · veg. ancorada (IC inclui zero) | 1 | #32 + D19 | ✅ |
  | soja SIDRA (âncora imune) **+48 km** em 1988–2024, IC exclui zero | 1 | #44 | ✅ |
  | 2019→24: pasto **+12,9** · rebanho **+11,9** · soja **+10,1** · ∪mosaico **+4,4** · agric **+0,5** km | 1 | `centro_massa_deriva_check.csv` | ✅ |
  | massa reetiquetada **+46,5 km** ao norte da agric. visível; r=0,84 com Δsoja | 1 | `centro_massa_deriva_resumo.csv` | ✅ |
  | ∪mosaico em 40 anos = **−60 km** (não usar como bracket longo) | 1 | `..._deriva_desloc.csv` | ✅ |
  | lavoura ~120–130 km ao sul do pasto, em todos os anos | 1 | #32 | ⏳ |
  | 166 AMCs (malha); **164** com conversão (base do #28C) | 1 · 2 | #25 · #28C | ✅ |
  | pixel-a-pixel a 1–2 km do valor original (MAUP) | 1 | #43 | ✅ |
  | censo: 44,6 M eventos · 3,8 Mha · 11,2% de GO · **16,0 M com idade conhecida** | 2 | #28 | ✅ |
  | série inteira: μ₁ **3,9a / σ 1,6 / w 33%** · μ₂ **16,3a / σ 7,5 / w 67%** · uma-só μ 12,2 | 2 | `idade_pastagem_regional.json` | ✅ |
  | BC de Sarle **0,609** (GO) · **0,568–0,639** nas 5 mesos, todas acima de 0,555 | 2 | idem (via #28C) | ✅ |
  | coortes por origem: lavoura **5a** (3.910.537) · veg. nativa **13a** (6.379.954) | 2 | #28 §6 | ✅ |
  | composição por origem: aos 3a **50%** veio de lavoura, aos 33a **1%** | 2 | censo, painel B da figura | ✅ |
  | bimodalidade **5/5** mesos · **162/164** AMCs (régua estrita) · **166/166** (união) | 2 | #28C · `_bracket_viz` | ✅ |
  | coexistência **dentro de cada ato**: **10/10** células período×região (união), 9/10 (estrita) | 2 | #28C | ✅ |
  | Ato I unimodal em 0/5 — horizonte, não ausência (μ 3,4 e 7,6; separação 4,2a < limiar 5a) | 2 | #28C | ✅ |
  | vale no histograma bruto — Noroeste **0,415→0,058**, Norte **0,271→sem vale** | 2 | `forma_regional_bimodalidade.py` | ✅ |
  | distância entre formas (TV) Sul×Norte **0,223 → 0,023** sob a união | 2 | idem | ✅ |
  | Δ SICOR × idade, parcial lat+lon: **+0,22 (agric) → +0,30 (união)**, p<0,0001 | 2 | `duas_logicas_bracket_fluxo.py` | ✅ |
  | o mesmo par na janela limpa ≤2019: **+0,04 / +0,06, n.s. nas duas réguas** | 2 | idem | ✅ |
  | η²(mesorregião) da idade: 3,7% cru → **0,5%** sob a união | 2 | #28C | ✅ |
  | amplitude Sul→Norte da mediana: 7a → **2a**, ordem embaralhada | 2 | #28C | ✅ |
  | `veg→pasto` Ato II→III: Sul **−49%** · Norte **−13%** | 2 · 4 | #33 | ✅ |
  | Granger ΔAgric_Sul→ΔPasto_Norte **p=0,97** (baixo poder, N≈38) | 3 | #34 | ✅ |
  | spillover: **θ<0 em 12/12** réguas×janelas; **p=0,02 só na régua exposta** (não citar como robusto) | 3 | #34 + bracket D26 | ✅ |
  | substituição local **β=−0,52** | 3 | #34 | ✅ |
  | drive comum: p de permutação **≈0,07–0,13** (n.s. a 5%) | 3 | #54 (D20) | ✅ |
  | crédito ~**75 km** ao sul do pasto | 3 | #50 | ✅ |
  | armazenagem ~**150 km** ao sul do pasto, ~83 km ao sul do crédito | 3 | #53 | ✅ |
  | estoque convertível: estado ~**60%** · Sul ~**53%** de 1985 | 4 | #39 | ⏳ |
  | **97%** do convertível remanescente desprotegido (6,35 de 6,56 Mha) | 4 | #46 (D17) | ✅ |
  | **~973 Mt CO₂e** (faixa 751–1208) | 4 | #47 | ✅ |
  | soja plantada SIDRA **+38%** no Ato III | 4 · Parte 1 | #28D/D25 | ✅ |
  | fronteira Norte **+93%** de área × **+14%** no Sul; IFDM **−0,08** | 4 | #51 | ✅ |

  🚫 **Números banidos** (estiveram na copy e caíram — não reintroduzir por descuido):
  "~78 mil pontos amostrados"; "Sul ~9a / Norte ~16a (ou ~20a)"; "a geografia desloca o peso
  da mistura"; "34 de 36 AMCs"; "tempo explica 20%, região 2,5–7,3%"; "o `pasto→agric` do Sul
  cai −88%"; "o pasto jovem vem ganhando peso"; **"giro de lavoura"** (termo inventado, virou "pasto
  de ciclo curto"); **"plantio direto é a melhor aproximação para ILP"** (é conservação de
  solo; o Censo não tem variável de ILP); **"percorra as cinco regiões e o desenho não
  muda"** sem declarar a régua (é falso na régua estrita); e, na Parte 1, "a vegetação
  encontra um piso".
- **A Perna 3 é a única sem interativa nova** — compensar com o esquema estático de 2
  painéis (ver acima) e as figuras #34/#42. É a perna que mais se beneficia de puxar frases
  direto do `ensaio_a_investigacao.md`.
- ✅ **Viabilidade da Perna 2 — resolvida, e a peça já existe (25/jul/2026).** A dúvida era se
  o redesenho do histograma por região ficaria instantâneo. Ficou: o censo vem como tabela de
  contingência `(ano, muni, idade, classe) → n_pixels`, então o histograma por recorte é uma
  **soma de pesos**, não uma reamostragem — pré-computado em `idade_pastagem_regional.json`
  (541 KB). A preocupação original ("alguma AMC pode ficar rasa") caducou: no censo, **0%** dos
  municípios têm menos de 20 pixels não-censurados, contra 44% na amostra. **Consequência para
  a reforma:** esta peça **não precisa ser construída** — precisa ser **movida** para dentro da
  Perna 2 e receber a copy nova acima.
- ✅ **A dívida das duas malhas — quitada em 28/jul/2026.** O problema era que o mapa estava
  numa resolução (166 AMCs) e o toggle noutra (6 pastilhas por mesorregião), sem nada na tela
  ligando as duas. Resolvido pela raiz em vez de por uma nota de rodapé: o contorno das
  mesorregiões passou a ser **desenhado sobre o mapa e a receber o clique**, então as duas
  malhas ficam visivelmente sobrepostas e a relação é óbvia sem texto. A justificativa
  continua declarada em uma linha abaixo da peça — mas agora explica *por que cada malha faz
  o que faz* (a fina é o teste duro; a grossa é onde o n sustenta o ajuste), não apenas que
  são diferentes.
- 📐 **Exports novos que a peça passou a exigir** (rodar os dois antes de conferir a Perna 2):
  - `scripts/export_malha_amc_viz.py` → agora gera também `malha_mesorregiao.geojson` (5
    feições). O dissolve sela as fendas entre AMCs vizinhas com um buffer de ~55 m; sem isso
    as bordas internas sobrevivem à união e o arquivo sai com 7.784 vértices em vez de 1.977.
  - `scripts/export_idade_histograma_regional.py` → o bloco `gmm` ganhou `sig_jovem`,
    `sig_velho`, `mu_1c`, `sig_1c` e `bc_sarle`. Os três primeiros são o que permite desenhar
    as curvas (inclusive a de **uma população só**, que é o argumento); o `bc_sarle` é a
    corroboração *model-free* que a nota do histograma cita. Chaves **acrescentadas**, nenhuma
    removida — o `index.html` no ar lê o mesmo arquivo e não quebrou (verificado).
