# Blueprint da Parte 2 — copy das 4 pernas

> Prancheta de texto (jul/2026). Arquitetura em
> [`PROPOSTA_REFORMULACAO.md`](PROPOSTA_REFORMULACAO.md). Aqui está a **copy pronta** da
> Parte 2 (o núcleo da investigação), em nível de aprovação: para cada perna há título,
> pergunta de abertura, corpo na voz de descoberta, a **resposta em uma frase** e o
> **"o que isto NÃO diz"**. Tom: sóbrio, editorial (banca + pares), com momentum
> narrativo — não é reportagem. Os números vêm da `narrativa_pipelines.md` e do
> `indice_logico_pipelines.md`; conferir antes de congelar.
>
> **Padrão de cada perna:** `PERGUNTA → corpo (descoberta) → RESPOSTA em uma frase → o que não diz`.
> Legenda das notas: 🎞️ = peça interativa que ancora · 🔗 = pipelines/blocos que alimentam.

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

**RESPOSTA (uma frase)**
> Toda a fronteira agropecuária marchou ~65–78 km ao norte em 40 anos — pasto à frente,
> lavoura ~120 km atrás, vegetação natural ancorada.

**O QUE ISTO NÃO DIZ**
Um centro de massa descreve *que* a fronteira andou — não *por que*. E é uma média:
esconde o que acontece dentro. As duas perguntas seguintes atacam exatamente isso.

---

## Perna 2 — Qual é o mecanismo?

🎞️ **Peça-central: a interativa da idade do pasto, re-cablada** (`pastagem-reserva.js`)
— mapa e histograma passam a conversar (ver PROPOSTA §4, Perna 2): selecionar uma região
redesenha o histograma, que **continua bimodal**. A interação *é* o argumento.
🔗 #33 (mecanismo por mesorregião) · #28/#28C (idade do pasto, bimodalidade) · #22
(substituição local) · #40/#40B (a autocorreção da latitude, D14).

**PERGUNTA**
> Se a fronteira inteira marchou, que conversão — e em que parte do estado — a moveu?

**CORPO**
A marcha é o saldo de duas conversões diferentes, e elas não estão no mesmo lugar. No
Sul, a transição que manda é **pasto → lavoura**: intensificação, terra que troca de
função. No Norte, é **mata → pasto**: fronteira, terra nova sendo aberta. Dois
Goiáses.

A assinatura mais fina disso está na **idade da pastagem no momento em que ela é
convertida**. Amostramos ~78 mil pontos que viraram lavoura e perguntamos, para cada um,
há quantos anos aquele pasto existia. A distribuição tem **dois picos**: um de pasto
jovem (~5 anos) e um de pasto velho (~22/35 anos). Dois picos são dois mecanismos: o
pasto jovem convertido é reserva de terra rotacionada (plantar pasto já pensando em
lavoura); o velho é fronteira antiga sendo finalmente aberta. E eles se distribuem no
mapa — o Sul converte pasto jovem (mediana ~9 anos), o Norte, pasto de ~20.

Aqui o trabalho se corrigiu, e vale contar. A primeira leitura anunciou que a lógica
jovem era *estrutural* — explicada pelo plantio direto. No mesmo dia, o controle derrubou
o exagero: ao segurar a latitude, o cruzamento com plantio direto desmancha. O que sobra
é mais honesto e mais interessante — **a geografia desloca o peso da mistura, não cria os
modos**. Os dois mecanismos coexistem em toda parte: mesmo dentro de uma única região, e
de um único período, o histograma segue com dois picos (34 de 36 AMCs testadas). A região
explica pouco da separação jovem/velho (2,5% a 7,3%); o *tempo* explica mais (20%). É esse
o "aha" da peça interativa: escolha o Sul profundo esperando um pico só, e ainda verá dois.

**RESPOSTA (uma frase)**
> São dois mecanismos — intensificar no Sul sobre pasto jovem, abrir fronteira no Norte
> sobre pasto velho — que **coexistem em toda parte**; a geografia só desloca o peso da
> mistura.

**O QUE ISTO NÃO DIZ**
Que "a região causa a bimodalidade" — foi medido, e não causa. Nem que o plantio direto
explica a idade do pasto — era confundidor de latitude. A frase certa é sempre
"gradiente regional no *peso* da mistura".

---

## Perna 3 — É a lavoura do Sul empurrando o Norte? *(o clímax)*

🎞️ Ancora nas figuras do #34 (lead-lag / spillover direcional) e no painel de
autocorreção do #42. É a única perna sem peça interativa — compensa com um **esquema
estático de 2 painéis** (ver abaixo) além das figuras, e com a **voz narrativa**.
🔗 #34 (o teste formal, nulo) · #42 (o Granger reverso, espúrio — a peça-modelo) ·
#37/#38/#52/#54 (o drive comum, corroborante) · #41 (fogo, vanguarda geográfica não
temporal).

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
ângulos. Nenhum a sustenta. **Primeiro:** não há precedência temporal — a expansão da
lavoura no Sul não antecede o avanço do pasto no Norte (o teste dá praticamente zero).
**Segundo:** onde o empurrão espacial poderia aparecer, ele aparece com o **sinal
trocado** — os vizinhos ao sul *co-expandem* com o Norte, não o empurram. **Terceiro:** o
único efeito forte é *local* — onde a lavoura entra, o pasto sai ali mesmo (é
intensificação, não expulsão à distância). O veredito: não é deslocamento causal de uma
região sobre a outra. É **reorganização espacial** — dois mecanismos locais paralelos sob
um mesmo impulso.

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

**RESPOSTA (uma frase)**
> A lavoura do Sul **não** empurra o Norte — a hipótese de deslocamento causal foi testada
> e refutada; os dois mecanismos são coordenados por um impulso macro comum sobre um
> gradiente de aptidão.

**O QUE ISTO NÃO DIZ**
Que o iLUC não existe — apenas que o **canal intra-estadual testado** não se confirma. E,
por simetria honesta, também não se afirma que "o Sul lidera": o veredito é *sem líder*. O
drive comum é corroborante — não se deve ler o câmbio como causa provada.

---

## Perna 4 — Por que a marcha desacelerou?

🎞️ Ancora no mapa/figuras do #39 (estoque convertível por região) e do #47 (centroide da
perda de carbono). Pode reusar a camada de fronteira/estoque.
🔗 #39 (o teto de oferta, decomposição) · #46 (97% desprotegido, D17) · #48 (validação
PRODES) · #47 (custo de carbono).

**PERGUNTA**
> No Ato III (2020–24) a lavoura do Sul desacelera. Acabou a demanda?

**CORPO**
A resposta intuitiva — "esfriou o mercado" — está errada, e é o que torna esta perna
interessante. No Ato III a demanda **subiu**: câmbio, preço e crédito, todos em alta. A
lavoura do Sul freou **sob demanda forte**. Isso não é assinatura de demanda fraca; é
assinatura de uma restrição de **oferta** — a terra acabando.

E acabou de forma desigual. No agregado do estado, a fronteira *não* fechou: ainda resta
cerca de 60% do Cerrado convertível, e o fluxo de conversão não caiu — só **migrou ao
norte**. Mas, olhando por região, no Sul ela fechou: o estoque convertível está em ~53%
do que era em 1985, e o ritmo de abertura despenca (o giro para a intensificação que a
Perna 2 já tinha mostrado). A "marcha ao norte" é, em boa parte, a fronteira
**perseguindo a terra que só resta no norte**. E a terra que resta está **97%
desprotegida** — o teto é físico, não institucional; não é a lei que segura a conversão,
é o fim do estoque acessível. O custo dessa marcha, precificado por diferença de estoque
de carbono, é da ordem de ~970 Mt de CO₂e, com a floresta dominando a emissão.

**RESPOSTA (uma frase)**
> A desaceleração do Sul não é falta de demanda — é o estoque de Cerrado convertível se
> esgotando (um teto de oferta **físico**), e a marcha ao norte é a fronteira perseguindo
> a terra que só resta lá.

**O QUE ISTO NÃO DIZ**
Que se conhece o estoque **cadastral** de terra. "Convertível" e "protegida" são proxies
com teto declarado (MapBiomas + malha de unidades de conservação), não o CAR pixel a
pixel.

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

## Notas de implementação (não é copy)

- **Cada "RESPOSTA em uma frase"** deve ter tratamento visual consistente (o mesmo
  componente da tese-callout, em versão menor) — é o batimento que se repete 4×.
- **"O QUE ISTO NÃO DIZ"** entra como bloco discreto (aside/nota), presente nas 4 pernas
  — é a marca de honestidade e o que amarra com a D14.
- **Números a conferir antes de congelar** (fonte entre parênteses): marcha +78/+67/+65 km
  (#32); gradiente ~120–130 km (#32); idade ~5 e ~22/35 anos, Sul ~9 / Norte ~20 (#28);
  η² região 2,5%/7,3%, tempo 20%, 34/36 AMCs (#28C); estoque estadual ~60%, Sul ~53%
  (#39); 97% desprotegido (#46); ~973 Mt CO₂e (#47).
- **A Perna 3 é a única sem interativa nova** — compensar com o esquema estático de 2
  painéis (ver acima) e as figuras #34/#42. É a perna que mais se beneficia de puxar frases
  direto do `ensaio_a_investigacao.md`.
- **Viabilidade da Perna 2 (checar antes de tratar como herói):** o redesenho do
  histograma ao selecionar uma região só fica instantâneo se as distribuições de idade
  **por AMC** estiverem **pré-computadas** (são ~78 mil pontos). Pré-calcular os histogramas
  binned por AMC (e por região agregada) ao build, e ao selecionar só ler o bin-array
  correspondente — não reamostrar 78k pontos ao vivo. Confirmar que os 78k pontos cobrem as
  36 AMCs com N razoável por AMC; se alguma AMC ficar rasa, fallback para o agregado da
  mesorregião. **Decidir isto antes de comprometer a peça como hero da Perna 2** — se a
  pré-computação não for viável, o "aha" do redesenho borra e a peça perde a aposta.
