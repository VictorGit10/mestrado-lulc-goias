# Blueprint das Partes 0, 1, 3 e 4 — a moldura da história

> Prancheta de texto (jul/2026, **revisada em 28/jul/2026**). Complementa
> [`BLUEPRINT_PARTE2.md`](BLUEPRINT_PARTE2.md) (o núcleo das 4 pernas); plano de execução em
> [`PLANO_DE_CONSTRUCAO.md`](PLANO_DE_CONSTRUCAO.md). Aqui está a copy da **moldura**: a
> abertura (0), o scroll dos 40 anos (1), o veredito (3) e a oficina (4). Mesmo tom: sóbrio,
> editorial, voz de descoberta.
>
> Legenda: 🎞️ = peça interativa · 🔗 = pipelines/blocos que alimentam · *(itálico)* =
> nota editorial, não é copy.
>
> ### ⚠️ O que mudou nesta revisão (28/jul/2026)
>
> | onde | mudança | causa |
> |---|---|---|
> | **Parte 0** | a contagem de pixels do lede estava **10× menor** | são **378 milhões** de pixels/ano e **~15,1 bilhões** em 40 anos, não 38 M e 1,5 bi. Erro herdado do site publicado (`index.html:143`) — ver o box abaixo |
> | **Parte 1 · Ato III** | copy **substituída** | a versão anterior dizia "a vegetação ensaia um piso" e "as lavouras se estabilizam": as duas eram leituras do **artefato de rótulo** (D25). O site já foi reescrito em 25/jul; a prancheta ficou atrás |
> | **Parte 1 · saldo** | entra o **Mosaico de Usos** como 5º número | ele sai de 10,7% (1985) para 6,1% (2019) e volta a **10,5%** (2024) — a classe que absorve a conversão do fim da série |
> | **Parte 1 · Sankey** | de **3 fluxos** para **7 grupos** e os números mudam | o #12B (27/jul) recontou a matriz primária incluindo a classe 21. "Três fluxos enquadram tudo" **deixou de ser verdade** |
> | **Parte 3** | a lista de autocorreções ganha o **#12B** e uma segunda categoria | as verificações que **confirmaram** o número (#14B, #22B) são registro tão honesto quanto as que derrubaram |
> | **Parte 4** | D1–D20 → **D1–D26**; entra o rebaixamento do **#23** | as decisões chegaram a 26; o #23 virou veredito de desenho, não pendência |

---

## PARTE 0 · Abertura (hero) — entrega o fenômeno + a virada

*Decisão travada: o hero entrega o **fenômeno + a virada** (a marcha e o "a explicação
óbvia está errada"), **não o veredito** (as 4 pernas ficam para a Parte 2). O suspense fica
no "por quê".*

**Sobrelinha (eyebrow)**
> Dissertação CIAMB-UFG · Goiás · 1985–2024

**Título**
> A marcha ao norte

**Lede**
> Em quarenta anos, toda a fronteira agropecuária de Goiás se moveu para o norte —
> pasto, boi e lavoura, cerca de 70 km cada. A explicação óbvia — a soja do Sul
> empurrando o pasto para longe — é boa demais para ser verdade, e este trabalho mostra
> por quê. Cada pixel desta tela é um quadrado de 30 metros no chão: são **378 milhões**
> deles cobrindo Goiás, recontados **todo ano** por quatro décadas — **15 bilhões** de
> observações — para rastrear a cicatriz que os mercados e as leis deixaram no
> território. A história se conta em **três atos** no mapa — e se resolve em **quatro
> perguntas**.

**Chamada (CTA)**
> Comece pelo mapa de 1985 ↓

*Alternativa de título, se "A marcha ao norte" parecer entregar demais cedo:
"O território que se reorganizou" (mais neutro). Recomendo o primeiro — é a imagem que
o leitor levará embora.*

> 🔴 **Erro numérico encontrado em 28/jul/2026 — corrigir também no site publicado.**
> O hero atual (`index.html:143`) diz *"38 milhões de pontos… 1,5 bilhão de registros"*.
> Os dois estão **10× abaixo** do real. A conta: Goiás tem **34.024.262 ha**
> (`painel_goias.json`, `lulc_area_total_ha`); um pixel de 30 m cobre 0,09 ha; logo
> **34.024.262 / 0,09 = 378,0 milhões de pixels por ano**, e ×40 anos = **15,1 bilhões**.
> "38 milhões" corresponderia a um pixel de ~95 m, que não é a grade do MapBiomas.
> A frase não tem fonte em `Textos/` — nasceu na própria copy do hero. **Ela subestima o
> trabalho**, o que é um erro simpático, mas continua sendo um erro na primeira frase que
> o leitor lê. Entra na lista de correções do `PLANO_DE_CONSTRUCAO.md`.

---

## PARTE 1 · Os 40 anos no mapa — o fenômeno

🎞️ **Peça-central: o scroll dos 40 anos** (`timeline.js` + seção `story`), intocado.
🔗 #10 (mapas raster GEE) · #12/#19 (transições, Sankey) · saldo do painel UF.

### 1.1 — Contrato de leitura ("como ler")

*Versão enxuta do bloco atual "Como ler esta linha do tempo". Mantém os três painéis
(atos / referências / navegar), mas com uma frase nova no topo que posiciona o mapa como
o fenômeno — ainda não a tese.*

**Título**
> Como ler os 40 anos

**Lede**
> O que vem a seguir é o **fenômeno bruto**: quatro décadas de uso da terra, ano a ano,
> no mesmo enquadramento. Ainda não é a tese — é o que aconteceu no chão, antes de
> perguntarmos *onde* e *por quê*. A série se organiza em **três atos**, definidos por
> triangulação estatística (não escolhidos a dedo), marcados pelas faixas coloridas da
> régua acima; os **pinos pretos** são referências institucionais que contextualizam as
> inflexões — não são o esqueleto da história.

*(Os três sub-blocos — "Os três atos", "Referências institucionais", "Como navegar" —
seguem como estão hoje. O acordeão "Como os atos foram definidos?" pode encolher: a
versão longa vive na Parte 4, a oficina.)*

### 1.2 — Os três atos (passos do scroll)

*Copy de cada era. Mantém-se descritiva — é o mapa falando, não a tese. Refinada a
partir da atual, sem antecipar a investigação.*

**Ato I · Pastagem como herança · 1985–2000**
> *Tese do ato:* O ponto de partida não é uma paisagem natural — é uma fronteira que já
> se moveu.
> *No mapa:* O dourado que domina o centro-sul é pastagem — herança do POLOCENTRO e do
> PRODECER, que abriram cerca de um terço do estado para a pecuária extensiva na década
> anterior. O verde escuro do norte e do nordeste (Paranã, Vão do Paranã) é o Cerrado
> que sobreviveu. A agricultura ainda é incipiente: manchas de rosa no sudoeste. Sob a
> hiperinflação, nenhum cálculo agrícola de longo prazo fecha.

**Ato II · Expansão e intensificação · 2001–2019**
> *Tese do ato:* A soja abre caminho no sudoeste, e o motor não é uma política agrícola —
> é a moeda estável.
> *No mapa:* O Plano Real (1994) faz o que nenhum programa setorial conseguiu — permite
> calcular o futuro; a Lei Kandir (1996) zera o ICMS sobre a exportação de grãos. O
> sudoeste (Rio Verde, Jataí, Mineiros) se veste de rosa: a lavoura avança sobre o pasto.
> A pecuária segue gigante em área, mas a dinâmica econômica do agronegócio já pertence à
> soja.

**Ato III · Conversão acelerada, mascarada · 2020–2024**

> ♻️ **Copy substituída (28/jul/2026).** A versão anterior desta prancheta dizia *"a
> vegetação ensaia um piso"*, *"as lavouras se estabilizam"* e *"a queda livre encontra,
> enfim, um piso"* — **as três eram leituras do artefato de rótulo** que o #28D identificou
> (D25). O site já havia sido reescrito em 25/jul; o texto abaixo é o que está na tela e
> usa **só medidas verificadas**. O parêntese "(mascarada)" é parte do nome de propósito: o
> traço que define o período é que a medida crua diz o oposto do que ocorreu.

> *Tese do ato:* A lavoura avança sobre o pasto mais rápido do que nunca — e o mapa,
> sozinho, diz o contrário.
> *No mapa:* Este é o ato em que a medida engana. Olhando só a classe "agricultura" do
> satélite, a conversão parece ter parado: no Sul goiano ela cai 88%. Mas a área de soja
> plantada que o IBGE recolhe em campo — que não passa por classificador nenhum — **cresce
> 38%** na mesma janela. O que mudou foi o rótulo: a partir de 2021 a conversão de pasto em
> lavoura passa a ser classificada como "Mosaico de Usos", a categoria que o MapBiomas usa
> quando não consegue separar as duas coisas. Contada pela régua corrigida, a saída de pasto
> para lavoura-ou-uso-misto **acelera cerca de 50%**. O que o pasto perde, a lavoura ganha:
> o recuo da pastagem **triplica de velocidade** (de 0,07 para 0,27 Mha por ano). A vegetação
> nativa, essa sim, não muda de ritmo — segue cedendo o mesmo tanto de sempre, agora
> concentrada ao norte, onde ainda resta Cerrado. Com 34,9% do estado em vegetação natural em
> 2024, Goiás **não encontrou um piso: mudou o endereço da fronteira.**

*(Nota de arquitetura: este ato é a **primeira aparição do Mosaico** na peça, e é onde o
leitor aprende a ler a classe. Tudo o que vem depois — o Sankey de 7 grupos, o bracket da
Perna 2, o −88% que a Perna 4 recusa a usar — depende de este parágrafo ter funcionado.
Se algum corte for necessário na Parte 1, **não é aqui**.)*

### 1.3 — O fecho: o saldo e os fluxos

*Fecho da Parte 1. Dá o baseline factual e entrega o bastão à investigação. O Sankey é
mantido (é bonito e carrega os fluxos).*

**Bloco A — O que 40 anos deixaram (saldo)**

*Grid de números-choque. **Passa de quatro para cinco**: o Mosaico entra porque a Parte 1
acabou de ensinar o leitor a lê-lo, e porque é o único da lista cuja trajetória é um **U**.*
> **−5,8 Mha** · Vegetação natural perdida — 17,65 → 11,88 Mha (51,9% → 34,9% do estado).
> **×4,8** · Agricultura — 1,17 → 5,58 Mha (a soja sozinha: ×12 em área, ×13 em produção).
> **+1,0 Mha** · Pastagem — saldo enganoso: sobe até ~14,8 Mha em 2003 e recua (U invertido).
> **×1,34** · Lotação bovina — 1,01 → 1,36 UA/ha: o rebanho cresce 46% e a área de pasto, só 9%.
> **≈0** · Mosaico de Usos — 3,63 → 3,59 Mha, saldo de 40 anos praticamente **nulo**. Mas o
> caminho não é: cai de **10,7%** do estado (1985) a **6,1%** (2019) e volta a **10,5%** (2024).
> A classe que absorve a conversão do fim da série é a mesma que estava lá no começo.

> *Em uma frase:* a vegetação perdeu 5,8 Mha, a agricultura quase quintuplicou e duas
> classes — pastagem e Mosaico — *parecem* estáveis no saldo enquanto sobem e descem no
> caminho. Saldo líquido é justamente o que esconde o caminho dos hectares.

**Bloco B — Para onde os hectares foram (Sankey)** 🎞️

> ♻️ **Reescrito em 28/jul/2026 — o #12B mudou o objeto.** Até 27/jul a matriz primária de
> transições **excluía a classe 21** (Mosaico), e a própria função de validação a descartava
> dos **dois lados** antes de comparar — era cega por construção. O #12B recontou o cubo
> localmente com **7 grupos**: o fechamento passou de 7,26% de Goiás perdidos para **0,08%**,
> e a massa que estava sendo descartada era de **6,5 a 10,9% do estado, todo ano**. Os três
> números da versão anterior (4,11 / 2,73 / 1,29) mudaram pouco — mas a frase *"três fluxos
> enquadram tudo"* **deixou de ser verdade**: o terceiro maior fluxo do estado é
> `Mosaico → Pastagem`.

> O saldo diz *quanto* cada classe ganhou ou perdeu; esconde *de onde para onde*. O
> diagrama cruza o uso de cada pixel em 1985 com o do mesmo pixel em 2024, nos **sete
> grupos** de cobertura. Quatro fluxos enquadram a paisagem:
> **4,10 Mha** vegetação → pastagem — o maior de todos, o desmatamento histórico,
> concentrado nos anos 1980–90; **2,72 Mha** pastagem → agricultura, a conversão moderna,
> que expande a lavoura sem desmatar direto; **1,29 Mha** vegetação → agricultura direta,
> menor, mas ganhando peso no nordeste depois de 2010; e **1,00 Mha** vegetação → Mosaico
> de Usos.
>
> Esse quarto fluxo pede uma ressalva, e ela é um achado. Seria natural somá-lo ao
> desmatamento — é vegetação que deixou de ser vegetação. **Mas não é isso que os dados
> independentes dizem:** ao incluir `vegetação → Mosaico` na conta de conversão
> antrópica, a razão entre o nosso número e o do PRODES/INPE salta de **1,00 para 1,35** —
> ou seja, passamos a contar um terço a mais de desmatamento do que o sistema oficial vê.
> A classe "Mosaico" contém transição de ida e de volta, e tratá-la como perda definitiva
> **superestima**. Por isso ela fica fora de "conversão antrópica" nesta peça.
>
> E há um par de fluxos que quase se cancela e diz muito sobre a medida: **1,72 Mha**
> Mosaico → pastagem e **1,62 Mha** pastagem → Mosaico. Duas correntes quase iguais em
> sentidos opostos, entre as duas classes que o classificador mais confunde. Boa parte
> disso não é terra mudando de uso — é o rótulo mudando de ideia.
>
> *Em uma frase:* dois fluxos mandam — vegetação→pasto (o desmatamento antigo) e
> pasto→lavoura (a conversão recente) —, a pastagem é o elo intermediário de quase tudo, e
> a classe ambígua do satélite movimenta tanta área quanto os fluxos que a peça consegue
> nomear.

*(Nota de arquitetura — a regra que vale para a peça inteira, decidida em 27/jul/2026:
**fluxo pinta, estoque não**. Onde o objeto é para **onde a área foi** — este Sankey, a
matriz 7×7, os mini-Sankeys por ato, os coropléticos de transição —, o Mosaico aparece com
cor própria (ocre `#c98a4b`). Onde o objeto é **o que a área é** — os 40 rasters anuais —,
ele não é pintado, mas é contado: tem faixa própria na barra empilhada e a legenda declara
que o raster não o mostra. Não são regras em conflito: num mapa de cobertura o Mosaico é um
borrão sobre metade do estado que não diz se ali é lavoura ou pasto; num mapa de fluxo ele
**é** o achado — em 2015–2024 é o destino dominante em **194 dos 246 municípios**.)*

*Bridge para a Parte 2:* o texto encerra aqui e a Parte 2 abre com "A pergunta que o
mapa não respondeu" (ver `BLUEPRINT_PARTE2.md`) — o saldo e os fluxos deram o *quanto* e
o *de onde para onde*; falta o **onde no estado** e o **por quê**. Não repetir a ponte
nos dois lados: ela vive na abertura da Parte 2.

---

## PARTE 3 · O veredito

*Fecho da investigação. Três beats: a tese em uma frase; a assinatura de honestidade; os
limites. É onde a peça cobra o investimento do leitor.*
🔗 `narrativa_pipelines.md` (Encerramento) · `indice_logico_pipelines.md` (Parte 1 e as
7 autocorreções) · `ensaio_a_investigacao.md`.

### 3.1 — A tese, em uma frase (callout central)

*Componente destacado — o clímax textual. Reusa o estilo do `tese-callout` atual.*

> **Goiás viveu uma reorganização espacial da produção agropecuária entre 1985 e 2024** —
> intensificação no Sul, fronteira no Norte —, coordenada por **forças de mercado comuns**
> (câmbio, crédito, preço) sobre um **gradiente estrutural de aptidão**, e limitada por um
> **teto de oferta** de Cerrado convertível que só resta no norte.
>
> Não foi um **deslocamento causal** de uma região sobre a outra — a hipótese óbvia do
> vazamento intra-estadual (iLUC) foi **testada e refutada**. É uma descrição
> empiricamente verificável, não uma metáfora.

### 3.2 — A assinatura do trabalho: uma investigação que se autocorrige

*Painel curto, em destaque — o "por que confiar nisto". NÃO é rodapé.*

**Título**
> Por que confiar nisto: o trabalho foi atrás dos próprios erros

**Corpo**
> A parte mais rara desta investigação não são os achados — são as vezes em que ela se
> corrigiu, sozinha e datada, antes que qualquer banca o fizesse. Cada linha abaixo é um
> "eu achava X; o dado disse Y", com a data em que Y venceu.

*(Lista compacta, uma linha cada. **Ordenar da mais severa para a menor** — a primeira e a
quarta são as que a banca vai querer discutir.)*
> · **A matriz de transição do trabalho estava certa?** Não — ela excluía a classe "Mosaico" e descartava, todo ano, entre 6,5% e 10,9% do estado. Pior: a rotina que a validava removia a mesma classe dos **dois lados** antes de comparar — passaria intacta mesmo se toda a conversão recente tivesse escapado por ali. Recontada, o fechamento sai de 7,26% para **0,08%**. *(#12 → #12B)*
> · **O Sul converte pasto jovem e o Norte, pasto velho?** Não — o gradiente de idade é artefato do rótulo; a região explica **0,5%**. Caiu por três caminhos independentes. *(#28C, #40, #33 → D25/D26)*
> · **A lógica do pasto jovem era do plantio direto?** Não — era confundidor de latitude. *(#40 → D14)*
> · **O Norte antecede o Sul (o dado que invertia a tese)?** Não — regressão espúria; some com o método certo. *(#42 → D16)*
> · **O fogo lidera a fronteira no tempo?** Não — só na geografia; co-evolui, não antecede. *(#41)*
> · **A "muralha norte" é a vegetação inteira?** Não — é só a floresta; o campo nativo recuou. *(#44)*
> · **Calcário e assistência técnica explicam a geografia?** Não — somem sob o gradiente 2D, como o plantio direto. *(#40B)*
> · **A infra de exportação lidera a fronteira?** Não — e o regressor "volume" era produção disfarçada; o achado caiu 9×. *(#45)*
> · **O drive comum é estatisticamente significante?** Não como se reportava — sob a inferência correta para o desenho, p vai de ~0,03 para **≈0,07–0,13**. O trabalho rebaixou o próprio achado. *(#54 → D20)*
> · **Faltava barra de erro na marcha?** Sim — agora todo ΔNorte vem com IC95%, e a vegetação inclui zero. *(D19)*

*(Segundo bloco, menor e com tratamento visual distinto — é uma categoria diferente e a
distinção **é** o argumento.)*
> **E três verificações que não derrubaram nada — e ficam registradas do mesmo jeito.**
> Nem toda auditoria acha um erro; contar só as que acham é outra forma de selecionar
> resultado.
> · **A área queimada estava 30% abaixo do painel oficial. Era erro nosso?** Não — três das quatro hipóteses foram testadas e caíram; o número voltou a ser citável. *(#14B)*
> · **O efeito de intensificação era só composição entre municípios?** Não — sob efeito fixo de grupo × ano o coeficiente não se move, e 24 de 24 subamostras mantêm o sinal. *(#22B)*
> · **A base de perda de vegetação bate com o sistema oficial?** Bate — r=0,91 contra o PRODES/INPE no regime anual. *(#48)*

> *Em uma frase:* uma tese que perseguiu a hipótese que mais a favorecia e a derrubou é
> mais forte do que uma que só coleciona confirmações.

### 3.3 — O que o trabalho NÃO afirma (os limites honestos)

*Bloco discreto, fechando o veredito com a mesma disciplina das pernas.*

> · Não se afirma que o **iLUC não existe** — apenas que o canal intra-estadual testado
>   não se confirma.
> · O **drive comum** é *corroborante, não estabelecido*: o câmbio é o candidato mais
>   forte, não uma causa provada — e o p correto para o desenho é ≈0,07–0,13, não 0,03.
> · No fim da série, **a medida fica ambígua**: o satélite deixa de separar lavoura de
>   pasto numa parte da conversão e chama o resultado de "Mosaico". Onde isso pesa, este
>   trabalho reporta um **intervalo** — o mínimo (só "agricultura") e o máximo
>   (agricultura ∪ mosaico) — e confere com a soja que o IBGE mede em campo. Nunca um
>   número só fingindo precisão que a medida não tem.
> · O **Ato III** tem só 5 anos — o que se lê nele é **sinal inicial**, não regime
>   consolidado.
> · "**Convertível**" e "**protegida**" são proxies com teto declarado (MapBiomas + malha
>   de UCs), não o cadastro pixel a pixel.
> · Os **marcos institucionais** da régua do topo **contextualizam, não identificam**: as
>   quatro políticas testadas são federais, então não existe grupo não-tratado com que
>   compará-las. Nenhum teste conserta isso — o limite é de desenho, não de estimação. Os
>   pinos marcam quando algo mudou no país, não a prova de que aquilo causou o que se vê no
>   mapa.
> · O recorte por mesorregião é grosso — mas, onde deu para testar na malha fina (AMC), a
>   conclusão sobreviveu.

**Chamada final**
> Como cada número foi apurado — a detecção dos atos, as réguas de robustez, as vinte
> decisões metodológicas, os limites — está na **oficina**, abaixo. ↓

---

## PARTE 4 · A oficina (era a aba Métodos) — moldura

*Deixa de ser aba: vira o fecho do scroll único, apêndice para quem quiser descer à
metodologia. O corpo reusa os blocos M1–M6 atuais, consolidados. Aqui só a copy de
moldura e a nova organização; as exposições de método já existem no site.*

**Abertura da oficina**
> Tudo o que você leu tem uma bancada por trás. Esta seção é para quem quer conferir — não
> é preciso ler para entender a tese, mas é o que permite *confiar* nela.

**Organização proposta (consolida M1–M6):**

1. **Como os três atos foram detectados** — a periodização data-driven (triangulação de
   quatro métodos; a candidata a 4º período rejeitada). *Consolida o M1 atual + o acordeão
   longo que sai da Parte 1.*
   > ⚠️ **Ponta aberta, registrada em 27/jul/2026.** Com a matriz recontada pelo #12B, o
   > pico do indicador de divergência (KL) **migrou de 2020 para 2022** — o cluster fica em
   > 2019–2022. A fronteira de 2020 **não cai por isso**: ela vem da triangulação, e a
   > âncora que a sustenta (a quebra da soja plantada do SIDRA em 2020) é **imune** à
   > mudança de rótulo, porque não passa por classificador. Mas a copy da oficina **não pode
   > dizer que os quatro métodos apontam o mesmo ano** sem qualificar qual deles se moveu.
   > `config_periodos.py` segue intocado, por decisão.
2. **As réguas de robustez** — as quatro provas independentes a que cada manchete foi
   submetida: tempo, latitude, integração, espaço (mais a incerteza por bootstrap).
   *Funde M2 (as métricas) + M3 (camadas de evidência) numa peça só, orientada a "como
   sabemos que sobrevive".*
3. **A vitrine do painel** — o inventário de dados (fontes, cobertura, o que entra e o que
   falta). *Mantém o M4 (`inventario.js`).*
4. **As vinte e seis decisões (D1–D26)** — a régua comum de todos os pipelines, em **tabela
   colapsável** de referência. *Recolhe o M5 num único `details`.*
   > ⚠️ **Correção pendente no site:** três lugares ainda dizem "**16 decisões**"
   > (`index.html` linhas ~415, ~1514 e ~1580, incluindo o item do sumário lateral),
   > enquanto o próprio bloco M5 já lista **D1–D26**. As duas mais recentes — **D25**
   > (a mudança de rótulo do Mosaico) e **D26** (o bracket) — são justamente as que a
   > reforma mais usa.
5. **Os limites** — as fragilidades declaradas. *Mantém o M6 — é honestidade, fica
   visível.*
6. **De onde vêm os números que a peça não mostra** *(bloco novo, opcional)* — o
   rebaixamento do **#23** merece uma linha aqui além da Parte 3: as quatro políticas
   testadas por diferença-em-diferenças são **federais**, logo sem grupo de controle; o
   pipeline foi rebaixado de "evidência causal" para "sensibilidade de co-movimento". É um
   caso limpo de *problema de desenho, não de estimação* — e explica por que a peça inteira
   trata os marcos como contexto e não como motor.

**Fecho da peça (rodapé)**
> *Dissertação CIAMB-UFG · Goiás 1985–2024 · dados MapBiomas Coleção 10.1, IBGE/SIDRA,
> BACEN/SICOR, IPEA, Trase, INPE. Anexo digital de uma dissertação — não a substitui.*

---

## Ordem de leitura final (o scroll inteiro, de cima a baixo)

```
0 · Hero — a marcha + a virada
1 · Os 40 anos no mapa  ── scroll 40 anos → saldo → Sankey
        ↓ "o mapa não respondeu onde nem por quê"
2 · A investigação  ── hipótese tentadora → Perna 1 (trajetórias) → Perna 2 (idade do
        pasto) → Perna 3 (o clímax) → Perna 4 (teto)
        ↓
3 · O veredito  ── a tese em uma frase → a autocorreção como assinatura → os limites
        ↓
4 · A oficina  ── periodização · robustez · painel · decisões · limites
```

### Navegação — o rail lateral (a tarefa que falta na moldura)

Um scroll único com a Parte 2 (4 pernas densas) e a Parte 4 (a oficina) é longo demais
para depender só da rolagem. Entra um **rail lateral fixo**, visível a partir do início da
Parte 1 (não no hero, para não competir com a abertura):

- **Conteúdo:** as 4 partes (0–4), com as **4 pernas** aninhadas sob a Parte 2.
- **Comportamento:** marca a seção/perna atual conforme o scroll; clique salta direto ao
  veredito (Parte 3) ou à oficina (Parte 4) sem rolar tudo.
- **Por que é inegociável:** sem ele, o leitor que veio pela tese pode nunca chegar ao selo
  de credibilidade (Parte 3) nem descobrir que a oficina existe — dissolver as abas sem
  rail é um regresso de UX. É peça de moldura, não de conteúdo; entra no mesmo passo do
  "scroll único".
