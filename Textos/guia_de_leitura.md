# Guia de leitura da dissertação — entender, de verdade, o que você construiu

> **O que é este documento.** Uma apostila para *você*, autor da dissertação, dominar
> intelectualmente o que foi produzido — não a narrativa (que já existe em
> [`narrativa_pipelines.md`](narrativa_pipelines.md)), mas as **ideias, as técnicas e as
> fórmulas** que a sustentam. A narrativa conta a história pressupondo que você sabe o que é
> "efeito fixo", "Granger", "I(2)". Aqui a gente para em cada uma dessas peças e explica em
> português claro, com **os seus próprios números** como exemplo. Leia em ordem uma vez;
> depois use como dicionário.
>
> **Como estudar.** Não decore fórmula. Para cada método, mire três frases que você
> conseguiria dizer numa banca: (1) *o que ele faz*, (2) *por que eu usei aqui*, (3) *o que ele
> NÃO pode afirmar*. Se você souber dizer essas três, você é dono do método.

---

## Sumário

- **Parte 1 — A tese em uma página** (sem uma fórmula sequer)
- **Parte 2 — A arquitetura**: por que cada passo puxou o seguinte
- **Parte 3 — Curso de métodos** (o coração deste guia)
  - Camada 1 — A gramática comum (aparece em quase tudo)
  - Camada 2 — O kit de inferência (testar associação e causa)
  - Camada 3 — As ferramentas de robustez fina (o que separa uma tese de um gráfico)
- **Parte 4 — Os resultados reais, honestos**: o que você PODE e o que NÃO pode afirmar
- **Parte 5 — Como defender**: as perguntas da banca e as suas respostas
- **Parte 6 — Glossário-relâmpago**: uma linha por termo

---

## Parte 1 — A tese em uma página

Esquece por um momento toda a estatística. Se um colega de outra área te perguntar no corredor
"do que é a sua dissertação?", a resposta honesta é esta:

> Peguei **40 anos de mapas de satélite** de Goiás (1985–2024) — que dizem, ano a ano e pedaço
> a pedaço, o que era pasto, lavoura, mata nativa, cidade — e cruzei com **dados econômicos**
> (PIB, crédito rural, rebanho, preços de commodities, câmbio). A pergunta é: **como e por que
> o uso da terra mudou?**

E o achado central, que organiza tudo, é a **"marcha ao norte"**:

> Ao longo desses 40 anos, **lavoura, pasto e gado inteiros escorregaram para o norte** do
> estado. O **Sul intensificou** (produz mais na mesma terra; o pasto vira lavoura); o **Norte
> abriu fronteira** (a mata nativa vira pasto). Isso foi **coordenado por forças de mercado
> comuns** — o câmbio na dianteira, mais crédito e preços — atuando sobre um **gradiente
> natural de aptidão da terra** (o Sul é mais apto à lavoura mecanizada), e **limitado pela
> quantidade de Cerrado que ainda resta para converter** — que só sobra no norte.

O ponto que dá **credibilidade** ao trabalho — e que muita gente não tem coragem de fazer — é o
que você **rejeitou**. A explicação mais tentadora seria: *"a lavoura do Sul empurra o pasto
para o Norte"* — uma relação de causa e efeito de uma região sobre a outra (o que a literatura
chama de **iLUC**, deslocamento indireto de uso da terra). Você **testou essa hipótese e ela
não se sustentou.** Não é uma região empurrando a outra; são **duas coisas acontecendo em
paralelo, movidas pelo mesmo motor econômico**. Boa parte dos seus resultados mais fortes são
**"nulos"** — coisas que você provou que *não* são verdade. Num mestrado, isso é raro e é uma
virtude: mostra que você perseguiu a resposta certa, não a resposta bonita.

**A frase de uma linha, para decorar:**

> *Goiás viveu uma reorganização espacial da produção agropecuária (intensificação no Sul,
> fronteira no Norte), coordenada por forças de mercado comuns sobre um gradiente de aptidão e
> limitada por um teto de oferta de terra — e não um deslocamento causal de uma região sobre a
> outra.*

Tudo na Parte 4 é essa frase, destrinchada em pernas de evidência. Tudo na Parte 3 é o
ferramental que permitiu afirmá-la com honestidade.

---

## Parte 2 — A arquitetura: por que cada passo puxou o seguinte

O trabalho tem **54 pipelines** (scripts de análise). Parece muito, mas eles não são avulsos:
formam uma **escada**, do agregado ao detalhe e do descritivo ao causal. Entender a escada é
entender por que cada peça existe. São sete degraus (a narrativa completa está em
[`narrativa_pipelines.md`](narrativa_pipelines.md); aqui está o esqueleto).

| Fase | Pergunta-motor | O que ela resolveu | O que ela abriu |
|---|---|---|---|
| **0 — A primeira foto** | Pastagem e economia se movem juntas em Goiás? | As séries estaduais existem e a história é plausível | "UF é grosso demais — desça ao município" |
| **1 — A fundação de dados** | De onde vêm os números, no nível certo? | Coletores validados: LULC, SIDRA, crédito, fogo, Trase | "Agora cruze e coloque no mapa" |
| **2 — Cartografia + transições** | Onde, no pixel, isso acontece? | Matrizes de transição **pixel-a-pixel** (não só estoque) | "As peças estão espalhadas — unifique" |
| **3 — Consolidação** | Como pôr tudo numa tabela comparável? | O **painel unificado** e as **AMC**; o motor de taxas | "Agora dá para testar com rigor" |
| **4 — Inferência** | As associações resistem a controles sérios? | Painel FE, DiD, autocorrelação espacial, quebras | "Os marcos teóricos organizam mal — deixe os dados falarem" |
| **5 — Periodização** | Quais são os 'atos' reais da série? | Três atos data-driven; a **bimodalidade** da idade do pasto | "Existem dois Goiáses — investigue" |
| **6 — A marcha ao norte** | A fronteira se desloca? Como? Por quê? | A tese inteira, testada e autocorrigida | (o encerramento) |

Três hábitos da escada valem mais que qualquer resultado isolado, porque são o que a torna
**confiável** — e o que você deve saber defender:

1. **Os nulos contam como resultado.** Quando um teste dá "nada aqui", isso não é escondido —
   vira achado. O caso-modelo é a Fase 6, onde a hipótese-mãe (uma região empurra a outra) foi
   *refutada*, e essa refutação é o coração da tese.
2. **A investigação se autocorrige.** Mais de uma vez, uma primeira leitura empolgada foi
   derrubada pela verificação do próprio autor no mesmo dia (o caso do "plantio direto", #40; o
   "fogo lidera", #41). Isso gerou regras (as "Decisões" D1–D20) para não repetir o erro.
3. **Tudo é validado contra uma verdade independente.** Cada coletor tem um script que confere
   o total contra a fonte oficial. A soma dos municípios tem que bater com o estado. Se a lógica
   estivesse errada, os testes quebrariam alto.

Guarde a imagem: **a Fase 6 é onde a tese vive; as Fases 0–5 são a fundação que a torna
verificável.** E o **gradiente Sul→Norte** — o "dois Goiáses" — é o fio que costura tudo.

---

## Parte 3 — Curso de métodos

Este é o núcleo. Cada verbete segue a mesma forma:

- **A ideia** — em uma ou duas frases, sem jargão.
- **Analogia** — quando ajuda a fixar.
- **Por que aqui** — o que, no *seu* trabalho, usa isso.
- **A matemática, com calma** — a fórmula, com cada símbolo nomeado. Nada de hand-waving.
- **Com números** — quando o método tem uma mecânica, uma mini-tabela ou uma conta pequena que
  mostra a engrenagem girando (às vezes com dados inventados só para ilustrar; às vezes com os
  seus). É o "veja funcionar" antes de olhar o resultado real.
- **Seu resultado** — o número real que saiu do seu pipeline.
- **A armadilha** — o que o método **não** pode dizer (é isso que a banca cobra).

As três camadas são por frequência de uso: a **Camada 1** aparece em quase todo script; a
**Camada 2** é o kit de inferência; a **Camada 3** são as ferramentas finas de robustez, que
costumam aparecer uma vez, no ponto exato em que a tese precisava se blindar.

---

### Camada 1 — A gramática comum

#### 1.1 Primeiras diferenças (Decisão D7)

- **A ideia:** em vez de correlacionar os *níveis* de duas séries (quanto de pasto × quanto de
  PIB), você correlaciona as *variações ano-a-ano* (quanto o pasto **mudou** × quanto o PIB
  **mudou**).
- **Analogia:** duas pessoas que crescem com o tempo vão parecer "correlacionadas" só porque
  ambas crescem — como altura de duas crianças diferentes ao longo dos anos. Olhar a variação
  (cresceu quanto neste ano?) remove esse crescimento comum e revela se elas se movem *juntas de
  verdade*.
- **Por que aqui:** quase toda série do seu trabalho tem tendência (tudo cresce com a economia
  e a população). Correlacionar níveis produziria correlações altas e **falsas** — todo mundo
  sobe junto. Por isso a regra é: **correlação sempre em primeira diferença, nunca em nível.**
- **A matemática, com calma:** a primeira diferença é `Δx_t = x_t − x_{t−1}` (leia "delta x no
  ano t" = valor deste ano menos o do ano passado). Só isso. Você perde o primeiro ano (não há
  anterior), por isso vê `NaN` em 1985.
- **Veja o truque funcionar (com números):** imagine duas séries que só têm em comum o fato de
  crescerem — pasto e, digamos, número de celulares no estado:

  | Ano | Pasto (nível) | Celulares (nível) | Δ Pasto | Δ Celulares |
  |---|---|---|---|---|
  | 2010 | 100 | 200 | — | — |
  | 2011 | 102 | 260 | +2 | +60 |
  | 2012 | 101 | 330 | −1 | +70 |
  | 2013 | 103 | 380 | +2 | +50 |

  Nos **níveis**, as duas sobem juntas → correlação altíssima e **falsa** (celular não move
  pasto). Nas **variações** (as duas últimas colunas), o pasto ora sobe ora desce enquanto o
  celular só sobe → a correlação despenca para perto de zero, revelando que **não** havia
  relação real. Foi exatamente essa "limpeza" que a diferenciação fez em todo o seu trabalho.
- **Seu resultado:** essa decisão (D7) está por trás de *todas* as correlações UF (#21) e do
  painel (#22). É o que impede o trabalho de anunciar correlações espúrias de tendência.
- **A armadilha:** diferenciar remove tendência, mas **não** remove tudo — como você
  descobriu no #42, uma série pode precisar de *duas* diferenças (ver 3.1, integração I(2)).
  Diferenciar de menos ainda deixa passar correlação espúria.

#### 1.2 Deflação pelo IPCA

- **A ideia:** R$ 1 milhão em 1995 não é a mesma coisa que R$ 1 milhão em 2024. A deflação
  converte todo valor monetário para reais de uma mesma data (você usou **dez/2024**), para que
  anos diferentes sejam comparáveis.
- **A matemática, com calma:** `valor_real = valor_nominal × (IPCA_dez2024 / IPCA_do_ano)`.
  O IPCA (índice de preços) é a "régua" que encolhe conforme o dinheiro perde valor.
- **Com números:** suponha um crédito de `R$ 100 milhões` em 2010, quando o IPCA era `4.000`, e o
  IPCA de dez/2024 é `7.200`. O valor real é `100 × (7.200 / 4.000) = R$ 180 milhões` em reais de
  2024. Ou seja: aqueles R$ 100 mi de 2010 **valiam** R$ 180 mi de hoje. Se você comparasse os
  R$ 100 mi de 2010 com, digamos, R$ 150 mi nominais de 2024 sem deflacionar, "veria" um aumento
  — quando na verdade **caiu** em poder de compra (180 → 150).
- **Por que aqui:** PIB, crédito (SICOR), Valor Adicionado — tudo é deflacionado. Sem isso, um
  "aumento do crédito" poderia ser só inflação, como no exemplo acima.
- **A armadilha:** o deflator escolhido importa. O glossário registra que a série de PIB do
  IPEA e a agregada do SIDRA divergem justamente por usarem **deflatores diferentes** — não é
  erro, é definição.

#### 1.3 Efeitos fixos de painel — o *2-way FE* (Decisão D8)

Este é o **cavalo de batalha** da sua inferência. É o verbete mais longo do guia de propósito:
se você dominar só um método, que seja este.

**Primeiro: o que é um "painel"?** É uma tabela com **duas dimensões ao mesmo tempo** — espaço
(municípios) e tempo (anos). Cada linha é um *município num ano*:

| Município | Ano | Pastagem | Crédito |
|---|---|---|---|
| Rio Verde | 2013 | 500 | 20 |
| Rio Verde | 2014 | 490 | 27 |
| Rio Verde | 2015 | 475 | 33 |
| Formoso   | 2013 | 900 | 15 |
| Formoso   | 2014 | 895 | 16 |
| Formoso   | 2015 | 880 | 20 |

Esse formato é muito mais rico do que um retrato de um único ano (corte transversal) ou do que
a série do estado inteiro (série agregada): ele deixa você olhar **cada município se movendo ao
longo do tempo**. É essa riqueza que o efeito fixo explora.

- **O problema que ele resolve (o confundidor):** suponha que você rode a regressão ingênua
  `pastagem = a + b·crédito` juntando todos os municípios e todos os anos, e ache que
  *municípios com mais crédito têm menos pasto*. Isso prova alguma coisa? **Não.** Talvez esses
  municípios tenham solo melhor, sejam mais perto de frigorífico, tenham tradição agrícola
  antiga — características que empurram **tanto** o crédito **quanto** o uso da terra. É o
  clássico problema do **confundidor** (ver 2.1): um terceiro fator move as duas variáveis e
  simula uma relação que talvez não exista.
- **A ideia central (comparar cada um consigo mesmo):** o efeito fixo responde a uma pergunta
  mais esperta. Em vez de "municípios com mais crédito têm menos pasto?" (comparar Rio Verde
  *com* Formoso), ele pergunta: **"quando Rio Verde recebeu mais crédito do que o normal *dele*,
  o pasto *dele* mudou?"** — e depois repete isso para cada município e junta tudo. Não se
  compara município com município; compara-se **cada município com ele mesmo ao longo do tempo**.
- **Analogia (alunos), agora com números:** imagine notas por horas de estudo:

  | Aluno | Horas | Nota |
  |---|---|---|
  | João  | 2 | 5 |
  | João  | 4 | 7 |
  | João  | 6 | 8 |
  | Maria | 2 | 8 |
  | Maria | 4 | 9 |
  | Maria | 6 | 10 |

  Maria sempre tira mais que João — talvez seja mais preparada, tenha tido melhor escola, sei lá.
  Isso **nunca muda** entre as linhas dela. Se você comparar João com Maria, esse "algo fixo da
  Maria" polui tudo. Então não comparamos os dois: perguntamos *"quando João estudou mais que o
  normal dele, a nota subiu?"* e *"quando Maria estudou mais que o normal dela, a nota subiu?"*.
  O efeito fixo de aluno **absorve** o talento/preparo fixo; o que sobra é o efeito real de
  estudar mais. Trocando "aluno" por "município" e "estudar" por "receber crédito", é
  exatamente o seu caso.
- **Por que a palavra "fixo"? (a confusão mais comum):** "fixo" **não** quer dizer que a
  variável é constante. Quer dizer que o modelo **segura tudo aquilo que não muda no tempo**
  dentro de cada município: tipo de solo, altitude, distância ao porto, relevo, clima médio,
  tradição agrícola. Mesmo que você **não tenha nenhuma dessas colunas na sua base**, elas ficam
  todas absorvidas. Cada município ganha o seu próprio intercepto — `α_Rio Verde`,
  `α_Formoso`, ... — e esses números nunca são interpretados; eles só "prendem" as diferenças
  permanentes para que não contaminem o `β`. Por serem um por município e constantes no tempo,
  chamam-se **efeitos fixos**.
- **E o efeito fixo de ano?** Pense no contrário: em 2008 veio a crise mundial; em certos anos
  houve boom da soja, disparada do câmbio, pandemia. Esses choques atingem **quase todos os
  municípios no mesmo ano**. Então criamos *outro* conjunto de interceptos, um por ano
  (`γ_2008`, `γ_2014`, ...), que retiram do modelo tudo o que foi **comum a todos** naquele ano.
  Como há **dois** conjuntos de efeitos fixos — município (`α_i`) e ano (`γ_t`) — o método se
  chama **Two-Way Fixed Effects (2-way FE)**.
- **Por que aqui:** você quer saber se, quando o crédito de *um* município sobe, a pastagem
  *dele* recua — sem que a resposta seja contaminada por "esse município sempre teve muito
  pasto" (o `α_i` absorve solo, porto, cultura) nem por "em 2008/2014 o mundo todo mudou" (o
  `γ_t` absorve preço internacional, câmbio, crise).
- **A matemática, com calma:** o modelo é

  ```
  Δlulc_it = α_i + γ_t + β·Δx_it + ε_it
  ```

  Leia símbolo a símbolo: `Δlulc_it` = a **variação** do uso da terra no município *i*, ano *t*;
  `α_i` = o intercepto próprio do município (efeito fixo de município); `γ_t` = o intercepto
  próprio do ano (efeito fixo de ano); `β` = o número que você quer; `Δx_it` = a variação da
  variável explicativa (crédito, VA agro...); `ε_it` = o erro. Os erros são **clusterizados por
  município** (ver 1.4). **Uma observação importante e específica do seu trabalho:** aqui tudo
  entra em **primeira diferença** (o `Δ`) — confirmado no código (`correlacoes_painel.py` aplica
  `.diff()` a todas as variáveis). Isso é uma escolha metodológica (D7): você modela
  *mudanças* no uso da terra, não *níveis*. Não é o 2-way FE "de livro-texto", que costuma ser
  escrito em níveis (`Y_it = α_i + γ_t + β·X_it + ε_it`) — mas é uma especificação válida. Num
  modelo em diferenças, o `α_i` absorve uma **tendência própria** de cada município (um
  crescimento constante), e o `γ_t` absorve o **choque comum às variações** daquele ano. A interpretação do
  `β` (abaixo) é a mesma.
- **A mecânica, com números (o "demeaning"):** como o software joga fora o que é fixo? Com uma
  transformação chamada *within* (ou "centrar na média"). Para cada município, ele calcula a
  **média temporal** de cada variável e a subtrai de cada observação. Exemplo — o crédito
  (já diferenciado) de um município nos seus anos é `20, 30, 40`; a média é `30`; depois de
  subtrair a média vira `−10, 0, +10`. Faz o mesmo com a pastagem. Agora repare: qualquer coisa
  **constante** naquele município (o solo, digamos, com o mesmo valor em todos os anos) vira
  **zero** ao subtrair a própria média — e **some** da equação. É *por isso* que dizemos que o
  efeito fixo "absorve" tudo o que é invariante no tempo: matematicamente, essas colunas
  constantes zeram.
- **O que é comparado, exatamente:** volte à tabela lá do começo. O modelo **não** compara Rio
  Verde com Formoso. Ele compara **Rio Verde 2013 vs. Rio Verde 2015** (dentro), depois
  **Formoso 2013 vs. Formoso 2015** (dentro), e **combina** essas comparações internas. Guardar
  essa frase — "é uma média de comparações de cada um consigo mesmo" — é entender o método.
- **Seu resultado, e a interpretação certa × errada:** no painel multivariado (#22), o **crédito
  SICOR é o canal dominante de retração da pastagem** (na janela com SICOR, **2013–2021** — ~8 anos, não os 40): `β ≈ −0,003, p < 0,001` (bate com
  `painel_multivariada.csv`). O que esse número **NÃO** quer dizer: *"municípios com mais
  crédito têm menos pasto"* (essa seria a leitura transversal, ingênua, contaminada por
  confundidor). O que ele **quer** dizer: *dentro de um mesmo município, nos anos em que o
  crédito subiu acima do padrão daquele município — e descontados os choques comuns do ano — a
  pastagem, em média, recuou.* O `p < 0,001` diz que essa associação dificilmente é acaso. E
  `Δagricultura × ΔVA agro` sobrevive a todas as variantes: a **assinatura da intensificação**.
- **A armadilha:** o efeito fixo controla o que é *fixo* (não muda no tempo) e o que é *comum*
  (igual a todos no ano) — mas **não** controla um confundidor que **varia dentro do município
  ao longo do tempo** e ficou de fora do modelo. Exemplo concreto: se em 2015 chega uma
  agroindústria a um município, ela ao mesmo tempo puxa o crédito e muda o uso da terra; como
  ela varia no tempo e é específica daquele lugar, o 2-way FE **não** a segura. Por isso o `β`
  aqui é uma **associação forte e bem-controlada**, mas ainda **não** é prova de causa — é o
  degrau anterior à Fase 6, que ataca justamente esse resíduo.

#### 1.4 Erro-padrão robusto: HAC / Newey-West (Decisão D4)

- **A ideia:** o `β` de uma regressão vem com uma "margem de erro" (o erro-padrão), e é dela
  que sai o p-valor. Em séries temporais, o cálculo ingênuo dessa margem **mente**: ela sai
  pequena demais, e você "acha" significância que não existe. O HAC corrige isso.
- **Por que o ingênuo mente:** a regressão comum (OLS) assume que os erros de cada ano são
  **independentes**. Mas em série temporal, um ano parecido com o anterior (autocorrelação) —
  se choveu pouco este ano, provavelmente choveu pouco no ano passado também. Erros
  correlacionados = você tem *menos informação independente* do que parece = a margem verdadeira
  é maior.
- **A intuição em uma frase:** se cada ano "carrega" informação do ano anterior, então 38 anos
  de dados valem, para efeito de precisão, como se fossem *bem menos* de 38 observações
  independentes. Menos informação real → margem de erro maior. O HAC recalcula a margem para
  refletir isso.
- **A matemática, com calma:** HAC = *Heteroskedasticity and Autocorrelation Consistent*.
  Newey-West é a receita mais usada: ela infla o erro-padrão levando em conta as
  **autocovariâncias** até um certo número de defasagens (`maxlags=2` no seu caso). Importante:
  **o β não muda** — só a margem de erro (e portanto o p-valor) fica honesta. Ilustrando o
  efeito: um `β` com erro-padrão ingênuo de `0,0010` pode ter erro HAC de `0,0018`; a estatística
  `t = β/SE` cai quase pela metade e um p-valor que "parecia" 0,01 pode virar 0,06 — ou seja, o
  que parecia significativo deixa de ser. É essa correção que evita você anunciar um efeito que
  não existe.
- **Seu resultado:** aparece nas correlações UF (#21) e nas taxas LULC (#17: o `SE Newey-West`
  do slope). É o que permite pôr uma faixa de confiança honesta (±1,96·SE) em torno das
  tendências.
- **A armadilha:** com N pequeno (suas séries UF têm ~38 anos), mesmo o HAC tem **pouco
  poder** — é difícil achar significância de verdade. Isso corta para os dois lados: protege
  contra falso positivo, mas também esconde efeitos reais fracos.

#### 1.5 AMC — Áreas Mínimas Comparáveis (Decisão D11)

- **A ideia:** municípios **nascem** ao longo do tempo (emancipação). Quando um distrito vira
  município, o "pai" perde território — e nos dados isso parece uma **queda brusca** que não
  aconteceu de verdade. A AMC agrupa cada pai com seus filhos numa unidade de **território
  constante** ao longo de toda a série.
- **Por que aqui:** **25% dos 246 municípios de Goiás nasceram depois de 1985.** Cidade de
  Goiás, por exemplo, "caiu 56%" em 1989 — mas foi perda de território, não de pecuária. Sem a
  AMC, toda análise longitudinal (que compara anos) estaria cheia dessas quedas falsas.
- **A matemática, com calma:** não há fórmula sofisticada — há uma **regra de ouro**. Variáveis
  **extensivas** (que se somam: hectares, cabeças de gado, R$) são **agregadas por soma** (o que
  neutraliza a emancipação — o território total do pai+filhos é constante). Variáveis
  **derivadas** (razões, densidades) são **recalculadas** a partir das extensivas já somadas —
  **nunca** somadas ou promediadas diretamente. Os 246 municípios viram **166 AMCs**
  (concordância de Ehrl, 2017).
- **Com números (a regra em ação):** um município-pai tinha 1.000 cabeças de gado em 400 km²
  (densidade 2,5/km²); em 1989 ele se divide e o filho leva 200 cabeças e 100 km². Olhando só o
  pai, o rebanho "cai" de 1.000 para 800 — uma **queda falsa**, foi só perda de território. A AMC
  junta pai+filho de novo: rebanho `800 + 200 = 1.000` (constante ✓), área `300 + 100 = 400 km²`
  (constante ✓). E a densidade? **Não** se faz a média das densidades dos dois — recalcula-se a
  partir das somas: `1.000 / 400 = 2,5/km²`. Fazer a média das razões daria um número errado; por
  isso a regra manda **sempre recalcular as derivadas depois de somar as extensivas**.
- **Seu resultado:** `painel_amc_goias.parquet` é a **unidade canônica de toda a Fase 6**. Sem
  ele, a "marcha ao norte" seria poluída por saltos de emancipação.
- **A armadilha:** você mantém **dois trilhos**: AMC (166) para o **longitudinal** (comparar no
  tempo); município atual (246) para o **transversal** e mapas recentes. Usar o trilho errado é
  erro metodológico.

#### 1.6 Centro de massa migratório — a figura-manchete (#32)

- **A ideia:** para cada ano, você resume "onde, em média, está o pasto de Goiás" num **único
  ponto no mapa** — o centro de gravidade da pastagem, ponderado pela área. Repita para todos os
  anos e você tem uma **trajetória**: para onde o pasto (ou a lavoura, ou o gado) foi migrando.
- **Analogia:** é o "ponto de equilíbrio" de uma gangorra. Se você põe mais peso (mais pasto) no
  norte, o ponto de equilíbrio se desloca para o norte.
- **A matemática, com calma:** o **centro médio** (*mean center*) é só a média das coordenadas
  ponderada pelo peso: `lat_centro = Σ(lat_i × peso_i) / Σ peso_i` (e igual para a longitude),
  onde `peso_i` é a área da classe naquela AMC.
- **Com números (3 AMCs fictícias):** uma ao sul com muito pasto, duas ao norte com pouco:

  | AMC | Latitude | Pasto (peso) |
  |---|---|---|
  | Sul   | −18,0 | 800 |
  | Meio  | −15,0 | 300 |
  | Norte | −13,0 | 100 |

  `lat_centro = (−18,0×800 + −15,0×300 + −13,0×100) / (800+300+100) = −20.200 / 1.200 ≈ −16,8`.
  O centro fica **puxado para o sul** (−16,8, perto do −18,0), porque é lá que está a maior
  massa de pasto. Se, dez anos depois, o Norte ganhar pasto e o Sul perder, esse número **sobe**
  (fica menos negativo) — e é esse deslocamento, ano a ano, que vira a "marcha ao norte".
  Você acrescentou duas peças a esse cálculo básico:
  - o **centro mediano** (algoritmo de **Weiszfeld**): em vez da média, o ponto que **minimiza
    a soma das distâncias** a todos os outros — é **robusto** a um cluster gigante (o polo de
    soja do Sudoeste) que puxaria a média;
  - a **elipse de desvio-padrão**: desenha a *dispersão* e a *orientação* (o azimute) do
    espalhamento — mostra não só onde está o centro, mas em que direção a mancha se alonga.

  Tudo calculado em **EPSG:5880** (uma projeção de área-igual, para que "km" signifique km de
  verdade).
- **Seu resultado (a manchete):** de 1985 a 2024, o centro de massa subiu ao norte —
  **pastagem +78 km, rebanho +67 km, agricultura +65 km** — enquanto a **vegetação natural ficou
  ancorada**. A lavoura fica sempre ~120–130 km **ao sul** do pasto/rebanho (o gradiente
  latitudinal persistente). E **só no Ato III (2020–24) a agricultura praticamente estaciona**
  (avança só +0,2 km, dentro do ruído do bootstrap — é desaceleração recente, não reversão)
  enquanto pasto e rebanho seguem subindo — o sinal mais limpo de deslocamento, e é recente.
- **A barra de erro (Decisão D19):** um centro de massa é uma estatística **pontual** — sem
  margem de erro não dá para saber se um deslocamento pequeno é real ou ruído. Por isso o #32
  ganhou um **bootstrap de AMCs**: reamostra as 166 AMCs **com reposição** (B = 2000), recomputa
  o centro a cada vez, e reporta o IC95% do ΔNorte. É a **faixa sombreada** na figura de
  latitude.

  | Variável | ΔNorte | IC95% | Veredito |
  |---|---|---|---|
  | Pastagem | +77,6 km | [+54,7, +98,2] | robusto |
  | Rebanho bovino | +66,9 km | [+47,2, +84,5] | robusto |
  | Agricultura | +65,2 km | [+43,5, +94,6] | robusto |
  | Vegetação natural | +7,6 km | **[−0,5, +15,6]** | **inclui zero** |

  As três manchetes estão **longe de zero** — são sólidas. Mas o "+7,6 km" da vegetação **não é
  distinguível de "não se moveu"**. Daí a regra **D19**: *um ΔNorte cujo IC inclui zero nunca é
  reportado como km* — diga **"ancorada"**. Repare que isso **reforça** a sua leitura (a
  vegetação não acompanhou a marcha); só proíbe vender os 7,6 km como se fossem deslocamento
  medido. Pelo mesmo critério, a agricultura no Ato III (+0,2 km) está seguramente dentro do
  ruído — o que é exatamente o que "praticamente estaciona" quer dizer.
- **A armadilha:** um centro de massa é uma **média** — ele pode esconder o que acontece nas
  pontas. Foi o que o #44 revelou ao abrir a vegetação em três formações: a "muralha norte" é
  **só a floresta** (+8,7 km, IC [+2,5, +15,1] — essa sim, presa), enquanto o **campo nativo
  recuou ao norte** (+34,8 km, mas com IC larguíssimo — [+0,2, +79,9]: a *direção* é robusta, a
  *magnitude* não) e a **savânica inclui zero** (+12,4 km, IC [−0,3, +23,3]). Média nenhuma
  dispensa abrir os componentes — e componente nenhum dispensa a barra de erro.

#### 1.7 Correlação de Pearson (r) e o p-valor

- **A ideia:** `r` é um número entre −1 e +1 que mede o quanto duas variáveis andam juntas em
  linha reta. `+1` = sobem juntas perfeitamente; `−1` = uma sobe, a outra desce; `0` = sem
  relação linear. O **p-valor** responde: "qual a chance de ver um `r` deste tamanho por puro
  acaso, se na verdade não houvesse relação?" — p pequeno (< 0,05) = provavelmente não é acaso.
- **A matemática, com calma:** `r` é a covariância das duas variáveis dividida pelo produto dos
  desvios-padrão (é a covariância "normalizada" para caber entre −1 e 1). No seu trabalho ele
  quase sempre vem **em primeira diferença** (1.1) e **com p-valor HAC** (1.4).
- **Como ler o número:** `r = 0,9` é forte; `r = 0,3` é fraco; `r = −0,8` é uma relação inversa
  forte (quando um sobe, o outro desce). Cuidado com um detalhe: `r` mede só relação **linear** —
  duas variáveis podem ter uma relação clara em forma de "U" e ainda assim dar `r ≈ 0`. E o
  p-valor é uma pergunta separada da força: com muitos anos, um `r` até modesto pode ter
  p pequeno; com poucos anos (suas séries UF têm ~38), até um `r` aparentemente grande pode não
  passar (ver 1.4).
- **A armadilha (a mais importante de todo o guia):** **correlação não é causa.** Um `r` alto
  entre A e B pode significar que A causa B, que B causa A, ou que um terceiro fator C causa os
  dois (o **confundidor**). Toda a Fase 6 é uma longa batalha contra confundidores — e o
  principal deles, você batizou de gradiente de **latitude/aptidão** (Decisão D14: em recorte
  transversal do estado, *sempre* reportar a correlação parcial controlando latitude antes de
  atribuir efeito próprio a qualquer variável).
- **A contra-armadilha (aprendida em 21/jul/2026, e vale para banca):** depois de controlar o
  confundidor, é tentador ler o resultado nulo como "então não há efeito". **Não é a mesma
  coisa.** "Não achei" e "não tinha como achar" produzem a mesma tabela. O #40 tinha um nulo
  aparentemente limpo (p=0,41) que **evaporou** quando a variável dependente passou a ser
  medida direito: nos *mesmos* municípios, só trocando amostra por censo, virou p=0,03. O
  motivo é mecânico e vale sempre: **ruído na variável dependente empurra a correlação para
  zero** (atenuação). Se o seu desfecho é uma mediana calculada com ~26 pixels por município,
  o nulo pode ser só o ruído falando. Antes de escrever "não há efeito", pergunte **com que
  precisão o desfecho foi medido** — e prefira escrever "**não estabelecido**", que é o que
  os dados de fato autorizam.

---

### Camada 2 — O kit de inferência

#### 2.1 Correlação × causalidade, e o confundidor

Já apareceu em 1.7, mas merece um verbete próprio porque é a **espinha filosófica** do
trabalho. Sempre que você vê duas coisas andando juntas, há quatro explicações possíveis:

1. A → B (A causa B);
2. B → A (B causa A);
3. C → A e C → B (um confundidor comum move os dois);
4. acaso (some com amostra grande / correção de múltiplos testes).

A tese da "marcha ao norte" é, no fundo, a afirmação de que o padrão Sul→Norte é o **caso 3**
(um motor comum: câmbio/crédito/aptidão) e **não** o caso 1 (o Sul causando o Norte). Todo o
arsenal a seguir existe para **distinguir esses casos**.

#### 2.2 Granger (precedência preditiva) + o placebo reverso

- **A ideia:** "x Granger-causa y" se o **passado de x ajuda a prever y** melhor do que o
  passado de y sozinho. É uma pergunta sobre **quem vem antes no tempo**, não sobre causa
  verdadeira.
- **Analogia:** o galo canta antes do sol nascer — o canto "Granger-causa" o nascer do sol
  (ajuda a prevê-lo). Mas o galo obviamente não *causa* o amanhecer. Por isso o nome tem
  aspas: é **precedência preditiva**, não causalidade. O próprio Granger avisava disso.
- **A matemática, com calma:** você roda duas regressões: uma "restrita" (`y_t` explicado só
  pelo próprio passado `y_{t−1}, y_{t−2}, ...`) e uma "completa" (acrescentando o passado de x).
  Um **teste F** pergunta: a versão completa reduz o erro o suficiente para valer a pena? Se sim
  (p pequeno), x "Granger-causa" y. **Com números:** se o modelo só-com-o-passado-de-y erra (soma
  de quadrados dos resíduos) `100`, e ao acrescentar o passado de x o erro cai para `98`, a
  melhora é ínfima → F pequeno, p alto → x **não** ajuda a prever y. Se caísse para `70`, a
  melhora seria grande → F grande, p pequeno → x "Granger-causa" y. É sempre uma pergunta sobre
  *quanto o passado de x reduz o erro de previsão de y*.
- **O truque do placebo reverso:** para um driver **exógeno** — algo que Goiás não move, como o
  preço internacional da soja — o teste **reverso** (o LULC de Goiás Granger-causa o preço
  mundial?) *deveria dar nulo*. Se der significativo, a série está contaminada e você não pode
  confiar na direção principal. Foi um teste de exogeneidade elegante no #37 (e o preço, de
  fato, não é "causado" por Goiás — passou no placebo).
- **Seu resultado:** no #34, `ΔAgric_Sul → ΔPasto_Norte` deu `p = 0,97` (**nulo**: o Sul não
  antecede o Norte). Esse nulo é uma das pernas centrais da tese.
- **A armadilha (que virou a Decisão D16):** Granger ingênuo em séries **integradas** (que têm
  tendência forte — ver 3.1) **fabrica** precedência que não existe. Foi o drama do #42: o teste
  reverso deu `p = 0,0007` (parecia que o Norte antecede o Sul!), mas era **artefato**. A
  correção exige as ferramentas da Camada 3 (estacionariedade, Toda-Yamamoto, placebos). Nunca
  leia um Granger agregado como causal sem esses cuidados.

#### 2.3 CCF / lead-lag — o primo descritivo do Granger

- **A ideia:** desliza uma série sobre a outra e mede a correlação em cada defasagem, para ver
  em que "encaixe temporal" elas casam melhor — quem lidera e por quantos anos.
- **A matemática, com calma:** `corr(Δx_{t−k}, y_t)` para vários `k`. Se a correlação é mais
  forte em `k > 0`, então x **antecede** y (x lidera); se em `k < 0`, y lidera. É puramente
  **descritivo** — não tem teste formal, é o mapa que orienta onde rodar o Granger.
- **Seu resultado:** usado no #34 e no #37 para localizar as defasagens antes dos testes
  formais.
- **A armadilha:** como é só correlação defasada, herda todos os riscos de correlação espúria
  de tendência (1.1). Serve para *achar candidatos*, não para *concluir*.

#### 2.4 DiD — Diferença-em-Diferenças + event-study + placebo (Decisão D9)

- **A ideia:** um "quase-experimento". Você quer o efeito de um marco (uma lei) sobre Goiás.
  Como não há um "Goiás sem a lei" para comparar, você usa **outros estados parecidos** (Mato
  Grosso, Tocantins — mesmo bioma Cerrado) como **grupo de controle**, e compara a **mudança**
  em Goiás com a **mudança** neles.
- **Analogia:** dois pacientes parecidos; um toma o remédio, o outro não. Se o que tomou
  melhorou *mais* que o que não tomou, o "a mais" é o efeito do remédio. DiD é isso com estados.
- **A matemática, com calma:** o efeito é o coeficiente `β` da **interação** `tratado × depois`:

  ```
  β_DiD = (GO_depois − GO_antes) − (Controle_depois − Controle_antes)
  ```

  Subtrair a mudança do controle **remove** o que teria acontecido de qualquer jeito (a
  tendência comum).
- **Com números (a tabela 2×2):** suponha a vegetação natural (Mha) antes e depois de um marco:

  | | Antes | Depois | Variação |
  |---|---|---|---|
  | **Goiás (tratado)** | 10,0 | 8,0 | **−2,0** |
  | **Tocantins (controle)** | 12,0 | 11,5 | **−0,5** |

  Goiás perdeu 2,0. Mas Tocantins, **sem** o marco, também perdeu 0,5 — essa é a tendência que
  teria acontecido de qualquer jeito. O efeito atribuível ao marco é a *diferença das
  diferenças*: `β_DiD = (−2,0) − (−0,5) = −1,5`. Ou seja, o marco explica **−1,5** dos −2,0; o
  resto (−0,5) seria queda "natural". Sem o controle, você creditaria os −2,0 inteiros ao marco
  — e superestimaria o efeito.
  Duas extensões:
  - **event-study:** em vez de um "antes/depois" único, estima um `β_k` para cada ano *k*
    relativo ao marco (k = −5..+5, com k = −1 como referência). Se os `β_k` **antes** do marco
    são ≈ 0, isso apoia a hipótese de **tendências paralelas** (o pressuposto-chave do DiD: sem
    a lei, GO e controle andariam juntos).
  - **placebo:** finge que o marco aconteceu 5 anos antes (onde não houve nada). Se esse marco
    falso der efeito significativo, é sinal de que o seu "efeito" real é só dinâmica pré-
    existente, não a lei.
- **Seu resultado (disciplinador):** de todos os marcos testados (#23), **só `Vegetação natural
  × 1995` contra Tocantins sobrevive** ao conjunto tendências-paralelas + placebo + DiD
  significativo. Os efeitos do Código Florestal (2012) e outros pós-2012 **têm placebo
  significativo** — ou seja, refletem dinâmica anterior, não o marco. Foi isso que rebaixou
  vários "efeitos de lei" a coincidências.
- **A armadilha:** DiD só é válido se as tendências eram paralelas **antes** do marco. Sem esse
  pressuposto, o `β` mede a diferença de trajetórias, não o efeito da lei. Por isso o
  event-study e o placebo não são luxo — são o que separa causa de coincidência.

#### 2.5 Autocorrelação espacial: Moran's I, LISA, SAR/SEM

- **A ideia:** "coisas próximas se parecem." Moran's I mede se municípios **vizinhos** têm
  valores parecidos (formam manchas) ou se o mapa é aleatório.
- **Analogia:** se as casas ricas ficam todas num bairro e as pobres em outro, há
  autocorrelação espacial positiva. Se ricos e pobres estão espalhados ao acaso, I ≈ 0.
- **A matemática, com calma:** primeiro define-se uma **matriz de vizinhança** `W` (quem é
  vizinho de quem, padronizada por linha). Então:

  ```
  I = (n/S₀) · Σᵢⱼ wᵢⱼ(yᵢ−ȳ)(yⱼ−ȳ) / Σᵢ(yᵢ−ȳ)²
  ```

  Em português: I é positivo quando um município acima da média tende a ter **vizinhos** também
  acima da média. Os valores vão, na prática, de cerca de **−1 a +1**: `I ≈ +1` = mapa em
  manchas nítidas (os altos colados nos altos); `I ≈ 0` = mapa aleatório (o valor de um município
  nada diz sobre o vizinho); `I < 0` = padrão de xadrez (alto cercado de baixo — raro em uso da
  terra). A significância vem de **permutações** (embaralhar os valores no mapa 999
  vezes e ver se o I real é extremo — se o mapa embaralhado quase nunca alcança o I que você
  observou, o padrão é real, não sorte). O **LISA** é a versão *local*: em vez de um número para
  o mapa todo, classifica **cada** município em Alto-Alto, Baixo-Baixo, ou outlier (Alto-Baixo /
  Baixo-Alto). E **SAR/SEM** são regressões que *incorporam* essa dependência: SAR
  (`Y = ρWY + Xβ + ε`) modela spillover direto entre vizinhos (`ρ`); SEM (`u = λWu + ε`) modela
  autocorrelação no *erro* (uma variável omitida espacialmente organizada, `λ`).
- **Seu resultado:** **115 de 140 resíduos** do painel (#24) têm Moran's I significativo. Tradução:
  o que o painel FE **não** explicou ainda tem estrutura geográfica forte — não é ruído
  aleatório. Isso **justificou** levar a sério a dimensão espacial (vizinhança, direção) na
  Fase 6 (o teste de spillover do #34).
- **A armadilha:** o LISA faz um teste por município (centenas de testes) sem correção formal —
  é **exploratório**, use para gerar hipóteses, não para cravar significância município a
  município.

#### 2.6 Quebras estruturais: sup-F / Quandt-Andrews + binary segmentation

- **A ideia:** em vez de *supor* que 2001 foi um ponto de virada, deixe **os dados apontarem**
  onde a série muda de patamar/regime.
- **A matemática, com calma:** para cada ano-candidato `τ`, você parte a série em dois e mede o
  quanto o ajuste melhora ao permitir médias diferentes antes e depois — isso é uma estatística
  `F(τ)`. O **sup-F** (Quandt-Andrews) pega o **máximo** dessa estatística ao longo de todos os
  candidatos: `max_τ F(τ)`. O "sup" (supremo) é porque o ponto de quebra é desconhecido — você
  testa todos e fica com o mais forte. Para achar **várias** quebras, aplica-se recursivamente
  (**binary segmentation**): achou uma, parte nos dois lados e procura de novo.
- **A intuição:** imagine testar `τ = 1998`, `1999`, ..., `2005` como possíveis viradas. Em cada
  ano você calcula "quão melhor o modelo fica se eu permitir uma média antes e outra depois desse
  ano". Se em 2001 a série realmente pula de patamar, o `F(2001)` dispara acima de todos os
  vizinhos; nos anos onde nada acontece, o `F` fica baixinho. O sup-F é simplesmente **o pico
  dessa curva** — e o `F = 62,2` em 2001 é um pico altíssimo (muito acima do `F = 21,5` de 2020,
  que ainda assim é uma quebra clara).
- **Seu resultado:** a periodização (#26/#29) achou quebras robustas em **~2001 (F = 62,2)** e
  **~2020 (F = 21,5)** — que viraram as fronteiras dos três atos. E um achado por *ausência*: o
  **Código Florestal (2012) não produz quebra empírica** nenhuma. Ausência de quebra também é
  informação.
- **A armadilha:** o p-valor do sup-F é bruto, **sem correção para múltiplos testes** (você
  testou muitos candidatos). Por isso a periodização passou por **verificação de falso positivo**
  (#30: rodar o método sobre ruído branco e medir quantas quebras "aparecem" por acaso).

#### 2.7 VIF — diagnóstico de multicolinearidade

- **A ideia:** num modelo com várias variáveis explicativas, se duas delas dizem quase a mesma
  coisa (são muito correlacionadas), o modelo "não sabe" a quem creditar o efeito, e os
  coeficientes ficam instáveis. O VIF mede esse problema.
- **A matemática, com calma:** `VIF_k = 1/(1 − R²_k)`, onde `R²_k` vem de regredir a variável
  *k* contra **todas as outras** explicativas. Se as outras explicam bem o *k* (R²_k alto), o
  VIF explode. Regra de bolso: VIF > 5 preocupa, > 10 é grave.
- **Com números:** se as outras variáveis explicam 20% da variável *k* (`R²_k = 0,2`), então
  `VIF = 1/(1−0,2) = 1,25` — tranquilo. Se explicam 80% (`R²_k = 0,8`), `VIF = 1/(1−0,8) = 5` — no
  limite. Se explicam 90%, `VIF = 10` — grave: as duas variáveis dizem quase a mesma coisa e o
  modelo não consegue separar os efeitos. Seus VIFs ≤ 1,55 correspondem a `R²_k ≲ 0,35`: bem
  folgado.
- **Seu resultado:** no painel multivariado (#22), **todos os VIFs ≤ 1,55** — ou seja, as
  variáveis não se pisam; os coeficientes (como o do SICOR) são confiáveis nesse quesito.
- **A armadilha:** VIF baixo diz que não há redundância *entre as incluídas* — não diz nada
  sobre variáveis **omitidas** (o confundidor de fora do modelo).

#### 2.8 O problema dos testes múltiplos: FDR e Bonferroni

- **A ideia:** se você roda 100 testes com corte de 5%, espera-se ~5 "significativos" **por puro
  acaso**, mesmo que nada seja real. Quando você faz muitos testes, precisa de uma correção,
  senão coleciona falsos positivos.
- **Analogia:** jogar dado muitas vezes e depois se surpreender por ter tirado 6 "várias" vezes.
  Com muitas jogadas, é esperado.
- **A matemática, com calma:** duas correções:
  - **Bonferroni** (conservadora): use o corte `α / número_de_testes`. Com 135 testes, exigir
    p < 0,05/135 ≈ 0,00037. Simples e severa.
  - **FDR** (Benjamini-Hochberg, mais gentil): controla a **proporção esperada de falsos
    positivos entre as descobertas**, não a chance de *qualquer* falso positivo. Mais poder,
    menos severa.
- **Seu resultado (uma lição que você aprendeu na marra):** no #37, houve **~7 hits em ~135
  testes** — exatamente o que o acaso produziria; **nada sobreviveu à correção**. Só o câmbio
  tinha estrutura de verdade (reaparecia em duas margens independentes). E no #38, a hipótese
  confirmatória `câmbio × fronteira → rebanho` deu `p = 0,031`, mas a **grade exploratória
  completa não devolveu nenhum sobrevivente do FDR** — por isso a leitura correta é "indício
  **sugestivo**, não achado estabelecido". Essa honestidade é ouro numa banca.
- **A armadilha:** o número de testes na "família" muda o resultado. O antigo "sobrevivente" do
  #38 (`câmbio × aptidão`, `p_fdr = 0,042`) **morreu** (`0,063`) quando a grade foi ampliada —
  prova de que era frágil ao tamanho da família. Sempre declare quantos testes entraram na conta.

---

### Camada 3 — As ferramentas de robustez fina

Estas aparecem no ponto exato em que a tese precisou se blindar contra uma objeção específica.
São as mais "técnicas", mas cada uma resolve um problema concreto do seu trabalho.

#### 3.1 Estacionariedade e ordens de integração — I(0), I(1), I(2); ADF e KPSS

- **A ideia:** uma série é **estacionária** — I(0) — quando sua média e sua variância são
  estáveis no tempo (ela "orbita" um valor fixo). Se ela tem tendência e você precisa
  **diferenciar uma vez** para estabilizá-la, ela é **I(1)**; se precisa diferenciar **duas
  vezes**, é **I(2)**. A "ordem de integração" é *quantas diferenças* a série pede.
- **Como reconhecer cada uma (com números):**
  - **I(0)** — oscila em torno de um valor fixo: `5, 4, 6, 5, 4, 6, 5` (já é estável, não pede
    diferença).
  - **I(1)** — tem tendência, mas a *variação* é estável: `100, 102, 105, 107, 110` → as
    diferenças `+2, +3, +2, +3` já estão estáveis. Uma diferença resolveu.
  - **I(2)** — a própria variação *acelera*: `100, 102, 106, 113, 124` → diferenças
    `+2, +4, +7, +11` (ainda crescendo!) → só as diferenças **das** diferenças (`+2, +3, +4`) se
    estabilizam. Precisou diferenciar duas vezes. É o caso do `pasto_Norte`: uma série cuja
    subida vinha **acelerando** — por isso uma diferença só não bastava.
- **Por que isso importa demais:** correlacionar/regressar séries não-estacionárias produz
  **relações espúrias** (ver 3.2). E — crucial — o Granger comum pressupõe estacionariedade.
- **A matemática, com calma:** dois testes que se **complementam**:
  - **ADF** (Dickey-Fuller aumentado): hipótese nula = "a série **é** não-estacionária (tem raiz
    unitária)". p **alto** = não consegue rejeitar = provavelmente não-estacionária.
  - **KPSS**: hipótese nula = "a série **é** estacionária". Os dois juntos triangulam (um confirma
    o outro pela via oposta).
- **Seu resultado (o coração do #42):** a série `pasto_Norte` é **I(2)** — nem a primeira
  diferença dela é estacionária (`ADF p = 0,92`). Ou seja, o Granger do #34, que rodou em
  *primeira* diferença, ainda tinha um regressor não-estacionário — a montagem clássica de uma
  regressão espúria.
- **A armadilha:** N pequeno enfraquece esses testes também; por isso você triangulou ADF+KPSS
  em vez de confiar num só.

#### 3.2 Regressão espúria e cointegração

- **A ideia:** **regressão espúria** é quando duas séries que só têm em comum o fato de
  *crescerem* aparecem fortemente "correlacionadas" — sem nenhuma relação real. **Cointegração**
  é o oposto: duas séries com tendência cujos desvios *andam juntos* de verdade (existe uma
  relação de longo prazo entre elas).
- **Analogia:** duas rolhas boiando num rio descem juntas porque a correnteza leva as duas
  (espúrio — nenhuma puxa a outra). Mas se estivessem **amarradas por um barbante**, quando uma
  se afasta a outra a segue (cointegração — há um laço real).
- **A matemática, com calma:** o resultado clássico (Granger-Newbold, 1974): regredir uma série
  I(1) sobre outra I(1) independente dá R² alto e t-estatística "significativa" com altíssima
  frequência — puro artefato. Para haver **cointegração**, as séries precisam ter a **mesma
  ordem de integração** e uma combinação linear delas ser estacionária.
- **Seu resultado:** no #42, `pasto_Norte` é I(2) e `agric_Sul` é I(0). Como têm **ordens
  diferentes**, elas **nem podem** ser cointegradas — não existe relação de longo prazo entre os
  níveis para o Granger "detectar". Logo, o `p = 0,0007` do teste reverso só podia ser espúrio.
- **A armadilha:** a persistência do termo mesmo controlando os drivers macro (#37) *pareceu*
  robustez, mas era o contrário — controles estacionários **não conseguem** absorver uma
  tendência espúria I(2). Robustez aparente pode ser sintoma do artefato.

#### 3.3 Toda-Yamamoto — o Granger que sobrevive à integração

- **A ideia:** a maneira **correta** de testar precedência quando as séries são integradas (I(1),
  I(2)) e você não tem certeza de cointegração. Contorna todo o problema da regressão espúria.
- **A matemática, com calma:** ajusta-se um VAR (modelo de vetores autorregressivos) **nos
  níveis** com `p + dmax` defasagens, onde `p` é o número ótimo de lags e `dmax` é a ordem máxima
  de integração das séries (no seu caso `dmax = 2`). O teste de Wald de precedência é aplicado
  **só nas primeiras `p`** defasagens — as `dmax` extras existem só para "absorver" a integração
  e tornar o teste válido. É engenhoso: você adiciona lags de propósito para poder ignorá-los.
  Concretamente, no #42: `p = 1` (um lag ótimo) e `dmax = 2` (a série mais integrada é I(2)) →
  ajusta-se o VAR com `1 + 2 = 3` defasagens, mas o teste de precedência olha **só o 1º lag**;
  os lags 2 e 3 estão ali apenas para neutralizar a integração.
- **Seu resultado:** aplicado ao #42, o Toda-Yamamoto **zera as duas direções** (reverso
  `p = 0,45`, forward `p = 0,25`). Não há precedência em sentido nenhum — só co-movimento.
  Repare na **simetria honesta**: isso também impede você de reivindicar que "o Sul lidera" — o
  veredito é *sem líder*, não *o Sul lidera*.
- **A armadilha:** Toda-Yamamoto resolve a *integração*, mas ainda tem baixo poder com N
  pequeno; por isso você não parou nele — somou os **placebos** (3.4).

#### 3.4 Placebos direcionais (a prova mais limpa do #42)

- **A ideia:** se uma "precedência" fosse um mecanismo econômico real e específico (Norte → Sul),
  ela **não deveria aparecer** onde não há mecanismo. Se aparece em todo lugar, é artefato.
- **A matemática, com calma:** você repete o mesmo teste de precedência trocando o "alvo" por
  destinos que **não fariam sentido** economicamente. Se o "sinal" persiste, ele não é
  direcionado — é co-tendência genérica.
- **Seu resultado:** o pasto do Norte "Granger-lidera" até o **pasto do próprio Sul** (mesmo
  `p = 0,0007` da manchete!), e o pasto do Centro lidera a lavoura do Sul. Qualquer série de área
  nortenha suave "prevê" qualquer sulista suave no lag 1. Essa é a **assinatura inconfundível de
  co-tendência espúria**, não de um canal Norte→Sul.
- **A armadilha:** placebo é poderoso justamente porque é **falsificável** — você monta um teste
  que *deveria* dar nulo. Se der positivo, derruba sua interpretação. Use com honestidade.

#### 3.5 Mistura de gaussianas (GMM), bimodalidade e o coeficiente de Sarle

- **A ideia:** uma distribuição é **bimodal** quando tem **dois picos** — dois "tipos" de coisa
  misturados. No seu caso: a idade da pastagem no momento da conversão tem um pico em ~5 anos
  (pasto jovem) e outro em ~22-35 anos (pasto velho) = **dois mecanismos coexistindo**.
- **A matemática, com calma:** o **GMM** (*Gaussian Mixture Model*) modela os dados como uma
  soma de "sinos" (gaussianas). Você ajusta um modelo de **1 componente** (um pico) e outro de
  **2 componentes** (dois picos) e pergunta qual descreve melhor os dados — comparando o **BIC**
  (um critério que premia ajuste e penaliza complexidade; menor é melhor). Se o de 2 componentes
  vence com folga (ΔBIC grande), há bimodalidade. Regra de bolso para o ΔBIC: uma diferença acima
  de ~10 a favor do modelo de 2 componentes já é considerada **evidência forte** de que há mesmo
  dois picos, e não um só "esticado". Como corroboração *sem modelo*, o **coeficiente de
  bimodalidade de Sarle (BC)**, calculado a partir da assimetria e da curtose: `BC > 0,555`
  sugere bimodalidade (0,555 é o valor de uma distribuição uniforme). Seus `BC` entre 0,60 e 0,70
  ficam claramente acima desse limiar em todas as mesorregiões.
- **Seu resultado:** a idade do pasto é robustamente bimodal — e (no #28C) **cada mesorregião é
  bimodal por dentro**, com `BC` entre 0,60 e 0,70 em todas. Isso sustenta a leitura de
  "coexistência dos dois mecanismos em toda parte".
- **A armadilha:** achar dois picos não diz *o que os causa*. Foi por isso que o #28C precisou da
  decomposição de variância (3.6) para responder "a bimodalidade é causada pela **região**?".

#### 3.6 Decomposição within/between, η² (eta²), ω² (omega²) e permutação

- **A ideia:** você tem uma variação total (na idade do pasto, digamos) e quer saber **quanto
  dela é explicada por um agrupamento** (a região) versus **quanto sobra dentro dos grupos**.
  "Between" = entre grupos; "within" = dentro dos grupos.
- **A matemática, com calma:** `η² = (variação entre grupos) / (variação total)` — a fração da
  variância que o agrupamento explica.
- **Com números:** idade média do pasto em três regiões: Sul `8 anos`, Centro `15`, Norte `22`.
  Se **dentro** de cada região quase todo pasto tem a idade da média (pouca variação interna), a
  região "explica" quase tudo → `η²` perto de 1. Se, ao contrário, dentro de cada região há de
  tudo (pasto de 3 e de 30 anos convivendo) e as médias regionais são parecidas, a região explica
  quase nada → `η²` perto de 0. Foi este segundo caso que você achou: `η² ≈ 0,013` significa que a
  região responde por só **~1,3%** da separação entre os dois tipos de pasto; **~79%** mora
  *dentro* das células região×ato. Traduzindo: os dois tipos de pasto (jovem e velho)
  **coexistem em toda parte** — não são "um por região".
- **Por que não parar no η²:** ele **infla** quando você tem muitos grupos
  (mais grupos "explicam" mais só por contagem). Duas blindagens:
  - **ω²** (omega²): um η² **corrigido** para o número de grupos — o effect-size honesto.
  - **permutação**: embaralha os rótulos de grupo muitas vezes e mede o η² que aparece **por
    acaso**; o "ganho real" é o η² observado menos o η² do acaso.
- **Seu resultado (à prova de banca):** a **região (mesorregião) explica só ~1,3%** da separação
  jovem/velho da idade do pasto; o **tempo (ato) explica ~19,6%**; e **~79% mora dentro das
  células região×ato**. Na malha fina (AMC), a parcela espacial sobe para **~7,5%** — ainda
  **minoria**. Conclusão que você pode cravar: a geografia **desloca o peso** da mistura ao longo
  do gradiente Sul→Norte, mas **não cria os modos**. A frase certa é "gradiente regional no
  *peso*", nunca "bimodalidade causada pela região".
- **Cuidado com o pós-censo (D23):** sob o censo (16 M de eventos), ω² ≈ η² até a 3ª casa e o
  piso da permutação colapsa — `E[η²|H₀] ≈ (k−1)/(W−1)` — de modo que `p = 0,005` sai para
  **qualquer** sinal não-nulo. **Não citar esse p-valor como força de evidência.** O que sustenta
  o veredito hoje é a **estabilidade censo × amostra** (três ordens de grandeza em *n* movem o η²
  em <1 pp e não mudam classificação), não a permutação. Ver `Textos/metodologia/censo_vs_amostra.md`
  §7.2 e `pipelines/28C_bimodalidade_regional.md`.
- **A armadilha:** é a inflação do η² por número de grupos — a mesorregião (5 grupos) e a AMC
  (164 grupos) poderiam mascarar. ω² e a permutação eram as blindagens previstas para isso; sob
  o censo, porém, elas **degeneram** (D23, ver acima) e a defesa passa a ser a estabilidade
  censo × amostra — três ordens de grandeza em *n* movem o η² em <1 pp e não mudam
  classificação —, não a permutação.

#### 3.7 Intensity Analysis (Aldwaik & Pontius, 2012)

- **A ideia:** um método hierárquico para perguntar se a mudança de uso da terra num período foi
  **rápida ou lenta**, e se foi **uniforme ou concentrada** em certas categorias/transições — em
  vez de só olhar o total.
- **A matemática, com calma:** compara a intensidade **observada** de cada transição com a
  intensidade **uniforme** que se esperaria se a mudança fosse espalhada igualmente. Faz isso em
  três níveis: **intervalo** (o período todo mudou rápido?), **categoria** (esta classe ganhou/
  perdeu mais que o uniforme?) e **transição** (esta troca específica A→B foi "mirada"?).
- **Seu resultado:** usado no #31 para testar se os sub-períodos diferem em taxa. O achado
  cauteloso: a sub-fase 2001–05 **não** difere significativamente do resto de P2 em *taxa total*
  (`p = 0,060`), mas difere na *composição* — perde vegetação natural ~5× mais intensamente
  (`p = 0,0008`). Foi por isso que 2005/2006 ficou como **nota metodológica**, não como um quarto
  período.
- **A armadilha:** com só 4-5 anos por sub-período, o **poder estatístico é baixo** (o próprio
  `p = 0,060` é limítrofe) — por isso a decisão prudente de não criar o período.

#### 3.8 Divergência de Kullback-Leibler (KL) — comparar matrizes de transição

- **A ideia:** uma medida de **quão diferente** uma distribuição é de outra. No seu caso: as
  matrizes de transição (quem virou o quê) **antes** e **depois** de um ano-candidato são muito
  diferentes? Um pico de KL num ano sugere uma virada de regime *na estrutura das conversões*.
- **A matemática, com calma:** a KL "soma", sobre todas as transições possíveis, o quanto a
  probabilidade mudou (ponderada logaritmicamente). Não é uma distância simétrica, mas serve
  como termômetro de "mudou muito aqui". A significância veio por **bootstrap de permutação**.
- **Seu resultado:** no #29c, o pico de KL/TV em torno de 2003 (e 2018–2020) corroborou as
  quebras do sup-F — foi uma das três pernas da triangulação da periodização.
- **A armadilha:** KL detecta que a *estrutura* mudou, não *por quê*. É corroboração, não
  explicação.

#### 3.9 STARS / Rodionov — quebras sequenciais

- **A ideia:** um detector de mudança de regime que funciona **em tempo real, sequencialmente**
  — bom para pegar regimes **curtos** que o sup-F (que procura a melhor partição global) pode
  perder.
- **A matemática, com calma:** ele monitora a média corrente e sinaliza um "shift" quando um novo
  valor está tão longe da média do regime atual que a hipótese de "mesmo regime" fica
  improvável, dado um nível `α`.
- **Seu resultado:** no #29b/#30, o STARS detectou shifts em 2004/2006 (e 2014 com `α = 0,05`) —
  parte da corroboração, mas sensível ao parâmetro (o que reforçou a decisão de tratar 2005/06
  como sub-fase, não período).
- **A armadilha:** é sensível ao `α` e ao comprimento de corte — por isso entrou como método
  *corroborativo*, nunca sozinho.

#### 3.10 Spillover espacial direcional — o SLX

- **A ideia:** testar diretamente a hipótese do deslocamento: *a agricultura dos vizinhos ao sul
  prevê o crescimento do pasto aqui?* Ou seja, incluir na regressão não só as variáveis do
  próprio município, mas as dos **vizinhos numa direção específica**.
- **A matemática, com calma:** SLX = *Spatially Lagged X*. Você adiciona ao modelo um termo
  `θ · (média da variável X nos vizinhos ao sul)`. O coeficiente `θ` é o **spillover
  direcional**. O **placebo** é rodar com vizinhos ao **norte** (onde a teoria não prevê efeito).
- **Seu resultado:** no #34, `θ = −0,16` — **oposto** ao previsto. Vizinhos ao sul **co-expandem**
  a lavoura, não "empurram" o pasto para cá. Mais uma perna do nulo de deslocamento causal.
- **A armadilha:** a definição de "vizinho" e de "ao sul" (a matriz W direcional) é uma escolha
  — daí a importância do placebo (norte) para mostrar que o resultado não é artefato da matriz.

#### 3.11 Hazard e a decomposição do fluxo de conversão (#39)

- **A ideia:** para saber se a fronteira está "fechando", separe **quanto ainda existe para
  converter** (o estoque) de **com que intensidade o que existe está sendo convertido** (o
  *hazard*, ou taxa de risco).
- **A matemática, com calma:** `hazard_t = perda_t / estoque_{t−1}` (a fração do que existia que
  foi convertida). Exemplo: se no início do ano havia `1.000` ha de Cerrado e `50` foram
  convertidos, o hazard é `50/1.000 = 5%`. A variação do fluxo de conversão se decompõe
  **exatamente** em:

  ```
  Δfluxo = h̄ · Δestoque  +  estoquē · Δhazard
  ```

  O primeiro termo é "mudou o fluxo porque encolheu o estoque disponível"; o segundo é "mudou o
  fluxo porque a intensidade de conversão mudou".
- **Por que a distinção importa (com números):** imagine que a conversão anual caiu de `50` para
  `20` ha. Dois mundos diferentes podem gerar isso:
  - **Acabou a terra (oferta):** o estoque despencou de 1.000 para 400 ha, mas a intensidade
    (hazard) até se manteve/subiu. Há quem queira converter — só não sobra o que converter.
  - **Acabou a vontade (demanda):** o estoque continua alto (1.000 ha), mas o hazard caiu de 5%
    para 2%. Tem terra de sobra — ninguém está convertendo.

  A decomposição separa exatamente esses dois termos e diz qual predomina. No Sul, você achou o
  **primeiro** padrão (estoque caiu a 53% do de 1985 *e* a demanda — câmbio/preço/crédito —
  subindo): a assinatura de **restrição de oferta**, não de demanda fraca.
- **Seu resultado:** no Sul, o estoque caiu para 53% do de 1985 **e** o hazard caiu — enquanto a
  demanda (câmbio, preço, crédito) **subiu**. Desacelerar sob demanda forte = a assinatura de
  restrição de **oferta**. No estado como um todo, a fronteira **não** fechou (resta ~60%), só
  **migrou ao norte**. Foi a terceira perna da tese (oferta), ao lado de demanda e gradiente.
- **A armadilha:** "estoque convertível" é um **proxy** com teto (Decisão D13) — MapBiomas sem
  CAR/UC/PRODES. É uma aproximação declarada, não a verdade cadastral.

#### 3.12 MAUP — o problema da unidade de área modificável

- **A ideia:** resultados espaciais podem **depender do recorte** (o tamanho e o formato das
  unidades). Se as AMCs do Norte são maiores e mais irregulares que as do Sul, será que a
  "marcha ao norte" é real ou artefato do desenho das unidades?
- **A matemática, com calma:** não há fórmula — há um **teste de robustez**: refazer o cálculo
  sem nenhuma unidade intermediária. No #43 você recalculou o centro de massa **pixel-a-pixel**,
  direto do raster de 30 m, sem passar pelas AMCs.
- **Seu resultado:** concordância quase perfeita — `ΔN` pixel × AMC: pastagem **+79,2 vs +78 km**,
  agricultura **+66,9 vs +65 km**, vegetação **+6,7 vs +7,6 km**. Diferenças de 1–2 km,
  irrelevantes. **O MAUP não é problema prático para a figura-manchete.** Poder dizer isso na
  banca vale muito. (Na vegetação a concordância é ainda menos informativa do que parece: pela
  **D19** os dois números estão dentro do ruído de qualquer jeito — as duas malhas concordam em
  que ela **não se moveu**.)
- **A armadilha:** o teste vale para *esta* métrica (o centroide). MAUP pode afetar outras
  análises — não é um "selo" que se estende a tudo.

#### 3.13 REER — o câmbio real efetivo

- **A ideia:** o driver macro que mais aparece na sua tese. "Câmbio" todo mundo conhece; o
  **REER** refina em duas direções: **efetivo** = ponderado por uma cesta de parceiros
  comerciais (não só o dólar); **real** = ajustado pela inflação relativa (não o câmbio nominal,
  que mistura inflação).
- **A matemática, com calma:** é um índice (base 2010 = 100). **Maior = mais desvalorizado/
  competitivo** — mais reais por dólar em termos reais, o que torna a exportação mais lucrativa.
  Por ser um índice *real*, ele **contorna a troca de moedas pré-1994** (Cruzeiro → Real) que
  inviabilizaria o câmbio nominal histórico — por isso cobre 1980–2024 sem buraco.
- **Seu resultado:** é a única variável macro que sobrevive com estrutura no #37 (reaparece em
  duas margens independentes) e a que ancora a hipótese confirmatória do #38 (`câmbio × fronteira
  → rebanho`, `p = 0,031` — mas veja o #54: sob a permutação correta isso vira ≈0,07–0,13, **não** significante; é **corroborante, não estabelecido**). O "preço recebido" que você construiu é literalmente
  `preço_internacional × câmbio` — e quem carrega o sinal é o **fator câmbio**.
- **A armadilha:** câmbio é exógeno a Goiás (bom para causalidade), mas o "crédito" que o
  acompanha é **endógeno** (a política responde ao ciclo) — por isso o crédito entra como
  *contexto*, não como driver exógeno puro.

#### 3.14 Inferência por reamostragem: bootstrap e permutação

- **A ideia:** quando você não confia nas fórmulas teóricas de p-valor (amostra pequena,
  distribuição estranha), você **simula** a incerteza reembaralhando os próprios dados.
- **A matemática, com calma:** **bootstrap** = reamostrar *com reposição* muitas vezes e ver
  como a estatística varia (dá intervalos de confiança empíricos). **Permutação** = embaralhar
  os rótulos (grupo, tempo, posição) para construir a distribuição do "acaso" e ver se o valor
  observado é extremo.
- **Seu resultado:** aparece em vários pontos — bootstrap do IC na Intensity Analysis (#31),
  permutação contra a inflação do η² (#28C), permutações do Moran's I (#24), bootstrap de
  permutação nas matrizes de transição (#29c). É a "cola" que dá p-valores honestos onde a teoria
  clássica não serve. O caso mais consequente é o **bootstrap de AMCs** do #32 (reusado por #44 e
  #50): é ele que põe IC95% em todo ΔNorte de centroide e sustenta a **D19** — ver 1.6.
- **A armadilha:** reamostragem não cria informação — com N muito pequeno, o intervalo sai largo
  (honestamente largo). É uma virtude, não um defeito.

#### 3.15 Shift-share (Bartik) e a permutação do *shifter* (#54)

- **O que é um shift-share.** Muita análise de "choque comum × exposição local" tem a mesma forma:
  um **empurrão** que é igual para todo mundo num dado ano (o *shift* — aqui, o câmbio nacional) é
  multiplicado por uma **fatia** que varia entre lugares (a *share* — aqui, a aptidão de cada AMC).
  O regressor do #38/#52 (`câmbio_t × aptidão_i`) **é exatamente isso** — um shift-share, ou desenho
  de *Bartik*. Reconhecer o nome importa porque existe uma literatura (Adão-Kolesár-Morales 2019;
  Borusyak-Hull-Jaravel 2022) que diz **como fazer o teste estatístico certo** para essa forma.
- **A pegadinha central (por que o p clusterizado mente aqui).** O erro-padrão que o #38/#52
  reportou é **clusterizado por ano** (ver 1.3) — ele reconhece que as AMCs de um mesmo ano
  compartilham o choque. Parece honesto, mas ainda é **otimista** num caso específico: quando o
  *shift* é **uma única série nacional**. O motivo intuitivo: por mais que você tenha 6.600 linhas
  (166 AMCs × 38 anos), a informação que **identifica** o efeito vem de quantas vezes o **empurrão**
  de fato mudou — e isso é **38 anos**, não 6.600. Você está aprendendo com **~38 choques**, e o
  erro-padrão clusterizado não desconta isso o bastante. É o "teto temporal" que o #38/#52 já
  citavam, agora **com nome e com correção**.
- **A correção: permutar o *shifter*.** Em vez de confiar na fórmula, você **testa por
  reamostragem** (é a ideia da 3.14, aplicada ao shift-share). Sob a hipótese nula "o câmbio não bate
  diferente ao longo da aptidão", **qual ano recebeu qual choque cambial é troca-livre**. Então você
  **embaralha a série do câmbio entre os anos**, mantém a aptidão de cada AMC fixa, recalcula o `β`, e
  repete milhares de vezes → uma distribuição do `β` "por acaso". O p = quantas vezes o acaso deu um
  `β` tão grande quanto o real. Duas versões: **naive** (embaralha livre) e **circular** (só *gira* a
  série, o que **preserva a autocorrelação** do câmbio — o câmbio de um ano parece o do seguinte; é a
  versão mais honesta para série macro). No #54, o `β` **não muda** (é o mesmo estimador), mas o p sai
  de **~0,03 para ≈0,07–0,13**: o achado do rebanho **deixa de ser significante a 5%**.
- **O que o método NÃO diz.** A permutação **não** diz que o efeito é zero — o `β` continua lá, com o
  sinal certo, na cauda da distribuição nula (~87º percentil). Ela diz que, **com só ~38 choques**,
  não dá para separar esse gradiente do acaso ao nível convencional. Vira **"corroborante, não
  estabelecido"** — e o que segura o padrão como real (não ruído) é a **especificidade** que o #54
  também testou: placebos de desfecho nulos (o efeito é do *rebanho*, não aparece na área urbana nem
  na água), sem antecipação (um câmbio *futuro* não "prevê" o rebanho de hoje) e robusto a dropar
  qualquer ano (nenhuma desvalorização isolada carrega o resultado). Levantar o teto de vez pediria
  outro tipo de dado — um choque que varie **no espaço e no tempo** (frete, ferrovia, clima) ou um IV
  para o câmbio (a "opção A", um fio novo). **Mas atenção ao alcance**: mesmo a opção A responderia
  sobre o **mecanismo** ("o gradiente de aptidão medeia choques exógenos?"), não sobre o câmbio em
  si — a pergunta "foi *o câmbio*?" é **estruturalmente irrespondível** com dado existente (o desfecho
  é anual, o choque é nacional, e nada multiplica as ~38 realizações; um IV resolveria exogeneidade,
  não poder). Isso não é um buraco na tese: é um limite **nomeado, medido e corretamente rebaixado**
  para "corroborante" — ver a adenda do [#54](pipelines/54_defensabilidade_perna4.md).

---

## Parte 4 — Os resultados reais, honestos

Agora que você tem o ferramental, dá para ler a tese como ela é: **uma afirmação central,
sustentada por pernas de evidência de forças diferentes.** Seja honesto sobre a força de cada
perna — é isso que uma banca respeita.

**A afirmação central:**

> Goiás viveu uma **reorganização espacial da produção agropecuária** (1985–2024) —
> intensificação no Sul, fronteira no Norte — coordenada por **forças de mercado comuns** sobre
> um **gradiente de aptidão**, e limitada por um **teto de oferta** de terra convertível — e
> **não** um deslocamento causal de uma região sobre a outra.

Ela se apoia em quatro pernas:

| Perna | O que afirma | Pipelines | Força da evidência |
|---|---|---|---|
| **1. O padrão existe** | Tudo marchou ao norte; a lavoura fica ao sul do pasto; a vegetação ficou **ancorada** | #32, #43 (MAUP), #44 (desagregado), D19 (IC) | **Forte** — robusto a malha, a desagregação e ao bootstrap |
| **2. O mecanismo local** | Sul: pasto→lavoura (intensifica); Norte: mata→pasto (fronteira) | #33, #28, #22, #40, #28C, #40B, #49 | **Forte no *tipo* de transição** — mas por medidas **imunes**: o `veg→pasto` do #33 (que não passa pelo Mosaico) e os centroides #32/#44. **⚠️ Cai o gradiente latitudinal de IDADE do pasto (#40/#28C/#33 — três testes independentes)**, **cai a queda de −88% do `pasto→agric` do Sul no Ato III (#33: inverte para +51%)** e **cai a "retração da agricultura" do Intensity (#31: −84% inverte para +67%)**. Auditoria D26, `metodologia/tratamento_deriva_mosaico.md` §9 — sobrevive a bimodalidade/coexistência, não o "young-Sul/old-Norte" |
| **3. Reorganização coordenada, não deslocamento** | *Negativo:* sem precedência temporal, sem spillover direcional. *Positivo:* coordenada por um **drive macro comum** (câmbio o candidato), não por causação local | *Negativo:* #34, #42, #45, #53, #41 · *Positivo:* #37, #38, #52 (aptidão exógena), #54 (inferência), #50 (crédito não lidera) | **Forte no negativo** (nulo bem defendido); **corroborante no positivo** — o #54 mostrou que o p clusterizado (~0,03) era otimista, a permutação do shifter dá **p≈0,07–0,13 (não sig. a 5%)**; o que sustenta o drive comum é a **especificidade** (placebos/lead/jackknife), não a significância |
| **4. O teto de oferta** | Sul bateu no estoque; Norte ainda tem Cerrado; 97% desprotegido | #39, #46, #48 (valida PRODES), #47 (custo) | **Forte no diagnóstico**, com proxy declarado (D13/D17) |

> Esta tabela é o esqueleto do [índice lógico](indice_logico_pipelines.md), que desce de cada
> perna até os scripts e etiqueta cada pipeline por **papel** (manchete, robustez, autocorreção…).

**O que você PODE afirmar** (com o texto adequado):

- Que houve uma **reorganização espacial** mensurável e robusta (Perna 1).
- Que os **dois mecanismos** (intensificação/fronteira) são reais e geograficamente segregados
  (Perna 2), com a ressalva de que a geografia **modula o peso**, não causa a bimodalidade.
- Que a hipótese de **deslocamento causal (iLUC intra-estadual) foi testada e refutada** (Perna
  3, o negativo) — e que isso é força, não fraqueza.
- Que o **câmbio** é o driver macro com estrutura mais consistente (Perna 3, o positivo),
  materializado no **rebanho de fronteira** — como **indício corroborante, não estabelecido** (p de
  permutação ≈0,07–0,13; o que o sustenta é a especificidade, não a significância).
- Que a desaceleração do Sul é compatível com **restrição de oferta** (terra acabando), não
  demanda fraca (Perna 4), e que a terra que resta está **97% desprotegida** — logo o teto é
  **físico/econômico, não institucional**.

**O que você NÃO pode afirmar** (e deve dizer que não afirma):

- Que "a lavoura do Sul empurrou o pasto para o Norte" (deslocamento causal). Refutado.
- Que o câmbio **causa** o gradiente, nem que ele é **estatisticamente significante** — sob a
  inferência correta (permutação do shifter, #54) o p é ≈0,07–0,13, não significante a 5%; é
  corroborante, não provado.
- Que o iLUC **não existe** em Goiás — você afirma que *o canal intra-estadual testado* não se
  confirma, não que o fenômeno inexista.
- Que "plantio direto explica a idade do pasto" — foi o overclaim que você mesmo derrubou (#40):
  era confundidor de latitude.

**Um corolário socioeconômico (fora das quatro pernas): crescimento sem desenvolvimento (#51).**
O #50 mostrou, *sem* índice de desenvolvimento, que o valor fica ao sul enquanto a área marcha ao
norte. O **#51** põe um número nisso com o **IFDM (FIRJAN) municipal 2013–2023** — o índice que o
IDH-M (só 1991/2000/2010) não dava. A fronteira Norte **quase dobrou a área agrícola** (+93% vs +14%
no Sul) mas **ganhou desenvolvimento igual** ao Sul e **permanece −0,08 abaixo** (o vão não fecha);
o **motor da fronteira — a expansão de área — é desacoplado** do desenvolvimento (r≈0, até negativo
controlando latitude; painel r²within≈0), enquanto o **valor** agropecuário rende só um dividendo
modesto (r=0,21). **Força: descritiva/associativa** (D14; não causal), mas robusta: **invariante a
município↔AMC**. Duas lições de método reutilizáveis vieram daí: (i) para crescimento regional, use o
**agregado** (log da soma), não a **média de log-ratios** — esta infla regiões de base pequena (foi o
que corrigiu "3× mais" para "quase dobrou"); (ii) num teste de desacoplamento, **case a janela** dos
dois lados (aqui 2013→2021). Como frasear: "o crescimento **não fecha o vão** nem compra
desenvolvimento **extra**" — **não** "não houve desenvolvimento" (o IFDM subiu em toda parte, +0,14).

---

## Parte 5 — Como defender (as perguntas da banca e as suas respostas)

Estas são as perguntas que um avaliador rigoroso faria. Ter a resposta pronta é ser dono do
trabalho.

**"Os números da idade da pastagem mudaram entre versões do seu trabalho. Por quê — e por que eu deveria confiar nos de agora?"**
Porque eu **auditei o meu próprio pipeline e achei dois defeitos**, e o segundo eu achei sozinho.
O primeiro: a coleta amostrava o **retângulo envolvente** de Goiás em vez do polígono, então 43,7%
dos pixels caíam fora do estado (verifiquei por *point-in-polygon*: 99,991% realmente fora). O
segundo, e mais grave: a classe **21 do MapBiomas ("Mosaico de Usos") não estava no dicionário de
grupos**, e o código fazia `.fillna("censurado_esquerda")` — ou seja, pixel com classe não
reconhecida era rotulado como **"idade desconhecida"** sendo que a idade era perfeitamente conhecida.
Isso inflava a censura em 11 pontos (74,9% publicado × 63,7% real) e, como *todas* as análises
principais rodam sobre o subconjunto não-censurado, elas usavam **dois terços** dos dados a que
tinham direito — e os excluídos não eram aleatórios, eram justamente os de origem mista
agricultura/pastagem, o lado "rotação" da conclusão. Depois disso troquei a amostra por **censo**:
todos os 44,6 milhões de eventos de conversão de Goiás. **O que sobreviveu**: a bimodalidade e a
posição dos dois modos (μ₁≈4,4a, μ₂≈22,9a, estáveis em todas as janelas). *(Na época eu também
listei aqui o gradiente Sul→Norte da idade, porque a ordenação das mesorregiões era idêntica na
amostra e no censo — mas ele caiu na auditoria de 23–25/jul; ver a pergunta seguinte.)*
**O que caiu**: a frase "a rotação está se tornando
dominante" — o componente jovem subia de 31,5% para 51,5%, ou seja **alcançava** o antigo, sem o
superar. Eu mudei a afirmação em vez de manter a versão mais bonita. Detalhe que registro por
honestidade: somando a categoria mosaico à rotação, o número volta a ~63%, quase o que eu publicava
antes — as duas correções quase se cancelavam, e **isso é um alerta, não um alívio**: número que
continua batendo depois de um bug corrigido não prova que o bug era inofensivo. Todo o episódio está
em [metodologia/censo_vs_amostra.md](metodologia/censo_vs_amostra.md), com as decisões **D21–D24**.
⚠️ **E há um terceiro capítulo, de 21/jul/2026: mesmo o "31,5% → 51,5%" caiu depois** — ver a
pergunta seguinte.

**"Você diz que o pasto jovem vem ganhando peso. Como sabe que isso não é o sensor mudando de opinião?"**
Não sabia, e quando fui verificar **era o sensor**. Esta é a autocorreção mais dura do trabalho
([#28D](pipelines/28D_deriva_mosaico.md), **D25**). Eu media "pastagem que virou agricultura" e
supunha que essa categoria significava a mesma coisa em 1990 e em 2024. Não significa. Contando o
destino **completo** das saídas de pastagem no censo de pixels, a conversão migra de rótulo: para
cada pixel que sai de pasto para "agricultura" em 2024, **32 saem para "Mosaico de Usos"** — a classe
que o MapBiomas usa quando não consegue separar lavoura de pasto. Em 2015 essa razão era **0,6**.
`P→agricultura` cai **92%** na série. E não é que a conversão parou: o **SIDRA** (dado de campo,
independente do satélite) registra a área de soja em Goiás **crescendo 38%** no mesmo intervalo, e a
classe Mosaico cresce **+1,35 Mha** — praticamente o tamanho da soja nova. A causa provável está
declarada na própria fonte: os filtros temporais da Coleção 10 usam janelas retroativas de 3–4 anos e
o ATBD prevê regras especiais "for the last years of the series, when the analysis window is limited".
**Consequência**: a tendência de w₁ sobe monotonicamente com a exposição da janela à mudança de rótulo
(20,8% numa janela limpa → 51,5% na janela inteiramente contaminada; o ano de 2024, sozinho, dá 93,4%).
Então eu **retirei** a afirmação temporal. **O que continua de pé** é o que não depende dela: a
**bimodalidade com modos estáveis** (μ₁≈4-5a, μ₂≈21-23a em *toda* janela testada, contaminada ou não)
e a **coexistência dos dois mecanismos dentro de cada região**. A lição generalizável (**D25**):
antes de comparar uma transição LULC entre períodos distantes, verifique que a **classe de destino
manteve o mesmo significado**; o sintoma é fácil de ler ao contrário — *a transição de interesse
"desaparece" enquanto o fenômeno de campo acelera*.

⚠️ **Correção de 23–25/jul/2026 — eu errei uma vez mais aqui, e a resposta acima já é a corrigida.**
Minha primeira defesa foi: *"o gradiente Sul→Norte da idade sobrevive porque é **transversal** —
compara regiões dentro do mesmo período, e a mudança de rótulo é temporal e estadual."* **Esse
raciocínio é falso**, e é um erro que vale conhecer, porque soa convincente. A mudança de rótulo não
é só temporal: ela **seleciona quais conversões continuam visíveis** como "agricultura", e essa
seleção opera *dentro* de um mesmo período. Comparar regiões no mesmo ano não protege de nada se o
que mudou foi **quem entra na amostra**. A verificação sob a régua superior derrubou o gradiente por
**três caminhos independentes**: o #40 (ρ do índice-jovem × latitude vai a ≈0, ns), o #28C (a
amplitude Sul→Norte cai de 7a para 2a) e o #33 (no Ato III o Sul vai de 16a — a mais jovem — para
**32a**, e o Norte de 27a para 23a: a ordenação **inverte**). **O que se afirma hoje**: a
bimodalidade e a coexistência são robustas; **o "pasto jovem no Sul, velho no Norte" não é
afirmável** — ele existe só dentro do subconjunto rotulado "agricultura". O gradiente Sul→Norte que
segue de pé é outro, e é medido por outras coisas: o **tipo de transição** (#33, `veg→pasto` ao
norte × `pasto→agric` ao sul — o `veg→pasto` é imune) e a **marcha dos centroides** (#32/#44).

**"Com censo você tem a população inteira. Seus testes não ficam todos significantes por construção?"**
Ficam, e é por isso que eu **não os uso** (**D23**). O ΔBIC da bimodalidade no Ato III é 844.789 —
um número que diz apenas que *n* é enorme, não que a evidência é forte. Com censo, seleção de modelo
por BIC é degenerada: qualquer desvio ínfimo da unimodalidade favorece mais componentes. Então eu
reporto duas coisas em vez do teste: (a) a **estabilidade dos modos entre recortes** — μ₁ entre 4,2 e
4,5 anos e μ₂ entre 22,5 e 23,5 nas quatro janelas testadas —, que é robustez de verdade; e (b) a
**precisão** dos parâmetros, que é o ganho real do censo. E digo o que o censo **não** resolve: a
censura de 64% é limite da série MapBiomas (começa em 1985), não do tamanho da amostra; e o erro de
classificação do próprio MapBiomas agora é a **maior** incerteza restante, justamente porque o erro
amostral saiu de cena.

**"Você diz 'marcha ao norte' — não é só efeito do desenho das suas unidades (AMC)?"**
Não. O #43 refez o centro de massa **pixel-a-pixel**, sem nenhuma malha, e a concordância é de
1–2 km (`+79 vs +78 km` no pasto). O MAUP foi testado e descartado para essa métrica.

**"Um centro de massa é um ponto. Qual a incerteza dele? Como sei que +78 km não é ruído?"**
Tem barra de erro, e ela é explícita (**D19**). Um **bootstrap de AMCs** (reamostragem com
reposição, B=2000) dá o IC95% de cada ΔNorte: pastagem [+54,7, +98,2], rebanho [+47,2, +84,5],
agricultura [+43,5, +94,6] — todos **longe de zero**. E eu aplico a régua contra mim mesmo: o IC
da **vegetação natural inclui zero** ([−0,5, +15,6]), então eu **não** reporto "+7,6 km" — digo
**"ancorada"**. A regra que adotei é: *ΔNorte com IC contendo zero nunca vira quilômetro no
texto*. É por isso que a vegetação aparece como "ficou parada" e não como um número.

**"O método do centro de massa é seu ou é padrão?"**
É padrão, e não inventei nada. *Mean center* ponderado é o que o **US Census Bureau** publica como
*mean center of population*, e o trio que uso (centro médio + centro mediano de Weiszfeld + elipse
de desvio-padrão) é o toolset *Measuring Geographic Distributions* do **ArcGIS**. Tudo em projeção
de área-igual (EPSG:5880). A implementação foi reproduzida do zero a partir do dado cru e bate ao
decimal.

**"Correlação não é causa. Como você sabe que o câmbio importa?"**
Eu **não** afirmo causa estabelecida — afirmo indício **corroborante**, e sou eu quem aperta o
parafuso contra mim mesmo. O câmbio é **exógeno** a Goiás (passou no placebo de exogeneidade, #37) e
é a única variável macro que reaparece em margens independentes. A hipótese confirmatória (câmbio ×
fronteira → rebanho) deu `p = 0,031`, e eu ataquei esse número por **dois flancos**. Primeiro a
**identificação** (#52): a exposição do #38 era um proxy de área mecanicamente complementar
(`fronteira ≈ −aptidão`); troquei-a por uma **aptidão edafoclimática física exógena** (Embrapa, via
WFS) e o achado do rebanho **reaparece sem a complementaridade** (β=−0,033) — a premissa "Sul apto /
Norte fronteira" deixa de ser assumida e vira **medida** (r_lat=−0,44). Segundo, e mais importante, a
**inferência** (#54): meu desenho é um **shift-share** (choque nacional × fatia local), e para esse
desenho o erro-padrão clusterizado é **otimista** quando há **um único choque nacional** (Adão-Kolesár-
Morales 2019). Então rodei a inferência certa — **permutação do câmbio entre os anos** — e ela mostra
que o p honesto é **≈0,07 a 0,13, não 0,03**: com só ~38 choques, **não é significante a 5%**. Ou
seja: eu **não** reporto o `p=0,03` como significância; reporto o de permutação e chamo a perna de
**"corroborante, não estabelecida"**. O que me faz crer que o padrão é **real e não ruído** não é o
p, é a **especificidade** (#54): o efeito aparece **só no rebanho** (placebos de área urbana e água
dão nulo), **não é antecipatório** (um câmbio *futuro* não prevê o rebanho de hoje) e **não depende de
nenhum ano isolado** (jackknife estável, nem 1999/2015 carregam sozinhos). Para cruzar de
"corroborante" a "estabelecido" eu precisaria de outro dado — um choque que varie no espaço e no tempo
(frete, ferrovia, clima) ou um IV para o câmbio —, e digo isso na dissertação em vez de superafirmar.

**"O Trase mede só fluxo exportador. E a capacidade instalada (silos, frigoríficos) — não pode ela
estar liderando a fronteira?"**
Testei pela metade viável e o veredito reforça o resto (#53). O cadastro de armazéns da **CONAB**
(fetchável por download direto) dá a **capacidade estática por município** com coordenadas; pus o
seu **centro de massa** na mesma régua de latitude do #32/#50, e ele é a camada **mais ao sul de
todas** — ~150 km ao sul do pasto e **~83 km ao sul até do crédito**, colado ao núcleo de lavoura
do sudoeste. Ou seja, a infraestrutura física **consolida o núcleo, não lidera** — como o crédito
(#50) e o fluxo exportador (#45). Duas honestidades: (a) é **capacidade de grãos** — a metade
"frigoríficos/abate" continua sem dado acessível (SIGSIF descartado; o abate municipal é modelado
do rebanho, circular, ver #50); (b) é **posição atual**, não teste de liderança temporal — a série
histórica da CONAB é estadual (por UF), não municipal, então não dá para rodar precedência (só o
CNPJ daria município × ano, e é engenharia pesada já descartada). É defensivo, como eu previa: fecha
a ressalva pela posição, sem inventar um teste que o dado não sustenta.

**"Por que a periodização é 1985-2000 / 2001-2019 / 2020-2024, e não outra?"**
Não escolhi as datas — os dados escolheram. Três métodos independentes (sup-F multivariado, STARS,
divergência KL das matrizes de transição) **convergem** em ~2001 e ~2020. E rodei verificação de
falso positivo (sobre ruído branco) para garantir que não são artefato. A fronteira 2005/06,
visível em alguns métodos, **não** virou período porque o método primário não a detecta e a
diferença de taxa total não é significativa (`p = 0,060`) — ficou como nota metodológica honesta.

**"O Código Florestal (2012) não aparece? Isso não enfraquece o trabalho?"**
Ao contrário — a **ausência de quebra** é um achado. O DiD com placebo mostrou que os "efeitos"
pós-2012 refletem dinâmica pré-existente (placebo significativo), não a lei. Preferi reportar o
nulo honesto a inventar um efeito.

**"O Granger reverso (Norte→Sul, p=0,0007) não inverte a sua história?"**
Foi a pergunta que eu mesmo persegui (#42). É **artefato de regressão espúria**, não inversão: a
série do pasto do Norte é I(2), a do Sul é I(0) — ordens diferentes, não podem nem ser
cointegradas. O método correto (Toda-Yamamoto) **zera as duas direções**, e o "sinal" reverso
aparece até em placebos sem sentido econômico (o pasto do Norte "lidera" o pasto do Sul com o
mesmo p). Co-movimento sem líder — que é exatamente o que o #34 já dizia.

**"Cinco unidades (mesorregiões) não é um recorte grosso?"**
É uma limitação real, e eu a declaro. Onde foi possível testar (a bimodalidade da idade do pasto),
repliquei na malha **AMC** (164 unidades; sob o censo ω² e permutação degeneram, e a
robustez vem da estabilidade censo×amostra) e a conclusão sobreviveu. O mecanismo de
transições do #33, esse sim, fica em resolução mesorregional.

**As limitações que você deve carregar com honestidade (declará-las é força):**

1. O drive comum está **corroborado, não estabelecido** — não significante sob a inferência correta (permutação, #54: p≈0,07–0,13); é o positivo da Perna 3.
2. A desaceleração do Ato III tem só **4-5 anos** de dados — é recente e ainda pode mudar.
3. "Terra convertível" e "proteção" são **proxies com teto** (D13/D17), sem CAR/PRODES pixel.
4. O iLUC intra-estadual foi refutado **no canal testado** — não é uma prova de que não exista
   qualquer forma de deslocamento.

---

## Parte 6 — Glossário-relâmpago

Uma linha por termo, para consulta rápida. O número remete ao verbete completo na Parte 3.

- **Primeira diferença (1.1):** variação ano-a-ano (`Δx = x_t − x_{t−1}`); remove tendência
  comum antes de correlacionar.
- **Deflação (1.2):** trazer R$ de anos diferentes para uma mesma data (dez/2024) via IPCA.
- **Efeito fixo / 2-way FE (1.3):** joga fora o que é fixo do lugar e comum do ano; sobra a
  variação interna. Cavalo de batalha da inferência.
- **HAC / Newey-West (1.4):** corrige o erro-padrão para autocorrelação; sem ele o p-valor mente
  em série temporal.
- **AMC (1.5):** unidades de território constante que neutralizam a criação de municípios.
- **Centro de massa / Weiszfeld / elipse (1.6):** o "ponto de gravidade" do pasto por ano; a
  figura-manchete da marcha ao norte.
- **D19 — IC do centroide (1.6):** todo ΔNorte vem com IC95% por bootstrap de AMCs; se o IC
  inclui zero (o caso da vegetação), diga "ancorada", nunca o número em km.
- **Pearson r + p-valor (1.7):** força da relação linear (−1 a 1) e chance de ser acaso.
- **Confundidor (2.1):** terceiro fator que move duas variáveis e simula correlação causal.
- **Granger (2.2):** o passado de x prevê y? Precedência preditiva, **não** causa.
- **CCF / lead-lag (2.3):** correlação defasada; mapeia quem lidera, descritivamente.
- **DiD / event-study / placebo (2.4):** efeito de um marco comparando GO a estados-controle;
  exige tendências paralelas.
- **Moran's I / LISA / SAR / SEM (2.5):** autocorrelação espacial (vizinhos se parecem) e
  regressões que a modelam.
- **sup-F / Quandt-Andrews (2.6):** acha quebras estruturais deixando os dados apontarem a data.
- **VIF (2.7):** diagnóstico de variáveis redundantes num modelo (>5 preocupa).
- **FDR / Bonferroni (2.8):** correção para muitos testes; "7 hits em 135" ≈ acaso.
- **I(0)/I(1)/I(2), ADF, KPSS (3.1):** quantas diferenças a série pede para estabilizar.
- **Regressão espúria / cointegração (3.2):** correlação falsa por tendência comum × laço real
  de longo prazo.
- **Toda-Yamamoto (3.3):** o Granger correto quando as séries são integradas.
- **Placebos direcionais (3.4):** o mesmo teste em alvos sem mecanismo; se "dá positivo", é
  artefato.
- **GMM / bimodalidade / Sarle BC (3.5):** dois picos = dois mecanismos; `BC > 0,555` sugere
  bimodal.
- **within/between, η², ω², permutação (3.6):** quanto um agrupamento explica; ω² e permutação
  corrigem a inflação por número de grupos.
- **Intensity Analysis (3.7):** a mudança de LULC foi rápida/mirada ou uniforme?
- **Divergência KL (3.8):** o quanto duas matrizes de transição diferem.
- **STARS / Rodionov (3.9):** detector sequencial de mudança de regime.
- **SLX / spillover direcional (3.10):** os vizinhos ao sul preveem o pasto aqui? (`θ`).
- **Hazard e decomposição do fluxo (3.11):** separa "acabou a terra" (oferta) de "mudou a
  intensidade" (demanda).
- **MAUP (3.12):** o resultado depende do recorte? Testado e descartado no centro de massa.
- **REER (3.13):** câmbio real efetivo; maior = mais competitivo; o driver-âncora da tese.
- **Bootstrap / permutação (3.14):** simular a incerteza reembaralhando os dados.
- **Shift-share / Bartik + permutação do shifter (3.15):** desenho "choque nacional × fatia local"
  (câmbio × aptidão); o erro-padrão clusterizado é **otimista** com um só choque nacional, então o
  p honesto vem de **embaralhar o câmbio entre os anos** (#54: sai de ~0,03 para ≈0,07–0,13).

---

> **Última palavra.** Você não precisa dominar a *derivação* de cada fórmula acima — precisa
> saber, para cada uma: *o que ela faz, por que você a usou, e o que ela não pode dizer.* Se você
> conseguir contar a história da Parte 1 e, quando alguém apontar para um método, responder com
> as três frases do verbete correspondente, o trabalho **é seu**. Ele sempre foi — o que faltava
> era a chave do vocabulário. Agora você tem.
