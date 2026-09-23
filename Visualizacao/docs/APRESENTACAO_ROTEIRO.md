# Apresentação da qualificação: roteiro e tempo (set/2026)

> **Padrão dos números (rodada 8):** toda comparação fica numa unidade só, dentro de um
> gráfico ou tabela, com a unidade dita uma vez no cabeçalho (barras a partir do zero,
> halteres antes → depois, linhas). Nada de número grande solto com a legenda continuando a
> frase embaixo. Nenhum código interno (#pipeline, Dnn) na tela; a fonte da medida vai numa
> etiqueta (IBGE / satélite). Vegetação remanescente na voz de exposição ("exposta à
> conversão"), nunca "convertível".

`Visualizacao/apresentacao.html`. São 26 slides principais e 3 de reserva (hub, Toda–Yamamoto, primeira diferença). Teto: **30 min**.
A navegação é por teclado. O mouse é opcional e só serve para arrastar o apoio da balança.

## Tempo por slide

| # | Slide | Passos | Tempo |
|---|---|---|---|
| 1 | Título | — | 0:20 |
| 2 | Abertura · o mapa de 1985 a 2024 | 4 | 1:00 |
| 3 | A hipótese de partida (dominó) | 4 | 0:50 |
| 4 | Três famílias de explicação | — | 0:50 |
| 5 | Pergunta de pesquisa | 1 | 0:20 |
| 6 | **Por que Goiás · objetivos** (antigos 6 e 7 fundidos) | 2 | 1:00 |
| 7 | Dados e método | 4 | 0:50 |
| 8 | Três atos | — | 0:50 |
| 9 | O balanço de quarenta anos (uma classe por passo; pico da pastagem) | 4 | 0:50 |
| 10 | Ato III · o rótulo que muda | — | 0:50 |
| 11 | **A balança** (sorteios visíveis: um Goiás sorteado × a pilha) | 7 | **2:00** |
| 12 | Os centros de massa | 4 | 1:00 |
| 13 | 2019–2024, medida a medida | 4 | 0:45 |
| 14 | Dois Goiáses | 3 | 0:45 |
| 15 | A idade do pasto (+ mistura de gaussianas) | 5 | 1:05 |
| 16 | **O que o empurrão deixaria nos dados** (3 momentos) | 2 | **1:30** |
| 17 | Em nenhuma medida a assinatura aparece (dois painéis, mesmo desenho) | 4 | 0:50 |
| 18 | Se o empurrão não aparece, o que coordena? (cadeia choque → exposição → resposta) | 5 | 1:15 |
| 19 | Não faltou demanda (barras Ato III ÷ Ato II) | 3 | 0:50 |
| 20 | Onde resta menos, converte-se mais devagar | 4 | 1:00 |
| 21 | O que a marcha custou (carbono por ato; IFDM por região) | 2 | 0:45 |
| 22 | Veredito · o placar (uma linha por passo) | 5 | 0:50 |
| 23 | O que isso diz à literatura | — | 0:45 |
| 24 | O que cada resposta não alcança | — | 0:40 |
| 25 | Até a defesa | — | 0:40 |
| 26 | Fecho | 3 | 0:25 |
| | **Total estimado** | | **≈ 23–26 min** |

A faixa depende do ritmo da fala. Os slides 11 e 16 são os únicos acima de 1:30. Se o ensaio
passar de 27 min, corte primeiro a fala do slide 12 (a balança já explicou o "ponto de
equilíbrio") e depois o passo da vegetação natural na balança (dá para parar no passo 6).

## Fala curta dos momentos didáticos

**11 · A balança** (halter → Goiás de lado → bootstrap)
1. "Um halter com pesos diferentes, apoiado no meio, tomba."
2. "Ele para onde os puxões se anulam: a média das posições, ponderada pelo peso. É esta
   fórmula."
3. "Em Goiás, os pesos são os hectares de pasto de cada AMC, pendurados no centroide."
4. "Vejo o estado de lado, com o norte à direita, e ele vira uma régua."
5. "De 1985 a 2024, com o apoio parado, a régua tomba para o norte."
6. "O novo equilíbrio está 77,6 km ao norte."
7. "E se o mapa tivesse saído um pouco diferente? Cada sorteio monta um Goiás alternativo com
   as mesmas 166 AMC: umas entram duas vezes, outras ficam de fora." À esquerda, a balança
   refeita com o Goiás sorteado (o texto diz quantas AMC ficaram de fora e quantas repetiram);
   o tijolo cai na pilha da direita. Cinco devagar, depois os 2.000. "A pilha inteira fica
   longe do zero."
8. "Na vegetação natural, o apoio quase não se mexe, e a faixa de 95% inclui o zero: não dá
   para dizer que o centro dela se moveu."

**15 · A idade do pasto** (+1 passo)
- "Uma população só não dá conta da forma: sobra no pico, falta no ombro. Duas dão."
- "O ajuste descreve a forma. Quem diz que são populações diferentes é o que havia antes no
  pixel, 45% contra 1%."

**16 · O que o empurrão deixaria nos dados** (3 momentos: uma pergunta, uma evidência e uma
frase em cada)
1. *O que esperaríamos?* "Se a soja de Rio Verde empurrasse o pasto, o pasto de Acreúna, logo ao
   norte, teria de crescer. E a lavoura do Sul teria de se mover antes do pasto do Norte."
2. *No espaço:* "Cada ponto é uma AMC num ano. O empurrão pediria a linha verde; os dados dão a
   vermelha, que desce."
3. *No tempo:* "Somar o passado do Sul praticamente não melhora a previsão do Norte. Não
   encontramos a assinatura do empurrão local testado."
O Toda–Yamamoto, o I(2), o Granger reverso e o poder do teste estão na **reserva R2**.

**18 · O motor comum**
- "O mesmo choque cambial chega a todas as AMC. A exposição local decide quanto ele pesa."
- "Mas a exposição acompanha a latitude. Por isso falo de gradiente Sul→Norte, e não de
  aptidão."

**Reserva 3 · primeira diferença (D7)**. Só entra se a banca perguntar por que o painel está
em variação ano a ano. O exemplo real é a AMC de Rio Verde.

## De onde vêm os números

- **Balança**: `assets/data/metodo_centro_massa.json`, o mesmo da página "Por dentro do
  método". O centro e o bootstrap são refeitos no navegador (semente 42). A faixa de 95%
  desenhada é a oficial do #32 (pastagem [54,7; 98,2], vegetação [−0,5; 15,6]). O ΔNorte
  refeito bate com o oficial (77,64 × 77,639; 7,55 × 7,55).
- **Empurrão, idade e motor**: `assets/data/didatica_apresentacao.json`, gerado por
  `Visualizacao/scripts/gerar_dados_didaticos.py`. O script importa as funções do #34 e do
  bracket (D26) e confere contra os CSVs oficiais antes de gravar: θ = −0,15721,
  β local = −0,51496, Granger p = 0,9707, r(aptidão, latitude) = −0,44, perda de 62% (D28).
  A nuvem do slide 16 é o θ publicado pelo teorema de Frisch–Waugh–Lovell: a inclinação da
  reta é o coeficiente.
- **Halter**: único elemento lúdico (3 kg e 1 kg, posições 20 e 100).

Para regenerar: `python Visualizacao/scripts/gerar_dados_didaticos.py`.
