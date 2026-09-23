# Guia unificado da qualificação

Preparado em 23/09/2026. Junta dois materiais feitos em paralelo e de forma independente: o roteiro, as perguntas e o plano de estudo desta pasta (`ROTEIRO_ORAL_DETALHADO`, `PERGUNTAS_BANCA`, `PLANO_DE_DOMINIO`) e um segundo roteiro feito numa conversa à parte. Os três arquivos originais continuam na pasta, e este não os substitui. Quando os dois divergiam, ficou a formulação que o texto da qualificação e o código sustentam, e três dúvidas que os dois deixavam em aberto foram respondidas nos scripts (Parte 1, já resolvida).

**Banca:** uma economista, um sociólogo/cientista ambiental e um estatístico.
**Tempo:** 30 minutos. A meta de ensaio é terminar entre 26 e 28 minutos.
**Como usar:** ensaie com a fala completa (Parte 2) e, depois, reduza cada slide a quatro lembretes: **pergunta, evidência, interpretação e limite**. Não decore o texto palavra por palavra. O teste de domínio é conseguir reconstruir uma conta simples e dizer o que mudaria a conclusão, mesmo quando a pergunta vier formulada de outro jeito.

---

## Parte 1: o que foi conferido e corrigido antes da apresentação

> **Estado em 23/09/2026: tudo resolvido e commitado** (`745ae4a`, `fc47e9b`, `b40c784`, `768c046`). O texto recompila limpo e o `verificar.py` dá 0 erros e 0 avisos. Restam só as duas verificações opcionais marcadas com ☐ em 1.3. O que segue serve para **saber responder**, não para corrigir.

### 1.1 Três dúvidas respondidas nos scripts

| Dúvida | Resposta (código) | Como dizer na banca |
|---|---|---|
| O que são os empurrões "forte" e "moderado" na simulação de poder | Monte Carlo do próprio `grangercausalitytests` (F com soma dos quadrados dos resíduos, T = 38) em `scripts/_poder_granger_deslocamento.py`. **Moderado = correlação parcial ≈ 0,3 → poder ~48%. Forte ≈ 0,5 → ~93%.** Tamanho de 5% sob o nulo. | Os 93% e os 48% valem só para o **Granger simples**, e não para o Toda-Yamamoto nem para as inclinações espaciais. |
| Se o "preço recebido pela soja" está deflacionado | `preco_recebido_soja_idx` (`scripts/coleta_drivers_macro.py`) = **cotação internacional em US$ (FMI, nominal) × câmbio real efetivo**, normalizado (média 1985–2024 = 100). | Não é preço pesquisado junto ao produtor, e o câmbio está dentro dele: o "+26% câmbio" e o "+79% soja" do slide 19 **não são sinais independentes**. |
| Se o teste espacial depende da matriz W | Rodado com k = 4, 8 e 12 (`scripts/_sensibilidade_w_deslocamento.py`; ficha do #34; apêndice, `tab:slx-w`). Nenhum θ positivo é significativo nas três; o pasto fica negativo nas 6 células; o β local praticamente não se move. Negativos: 12/12 (k = 8), 10/12 (k = 4), 8/12 (k = 12); os positivos são todos do rebanho, com p ≥ 0,70. | "Nenhum θ positivo distinguível de zero, com 4, 8 ou 12 vizinhos." "Todas negativas" só com "com oito vizinhos". Contiguidade e raio não foram testados. |

### 1.2 Defeitos que a banca poderia apontar (todos corrigidos)

1. ✅ **"Preço recebido pelo produtor".** O texto atribuía ao Ipeadata "preços recebidos pelo produtor". Agora a §3.2 (`03_metodologia.tex:144–151`) define o *preço recebido* como construção (cotação × câmbio real) e avisa que ele não é independente do câmbio. Slide 19: "Soja, índice (cotação em dólar × câmbio real)", com a fonte declarando que a linha contém o câmbio.
2. ✅ **Erro de medida no desfecho.** Dizia que "atenua qualquer associação". Agora (`03_metodologia.tex:1354`): reduz a precisão e o poder e, quando não é puramente aleatório, pode atenuar. *Para a fala:* com erro clássico no desfecho, o coeficiente não é viesado; a atenuação vem de erro no regressor ou de erro não clássico, como a má classificação.
3. ✅ **Albers × contagem de pixels.** A Albers agora é "empregada apenas nesta sobreposição vetorial" (`03_metodologia.tex:752`); as áreas do raster vêm da contagem de pixels.
4. ✅ **Slide 17.** "O teste **no tempo** detecta um empurrão forte em ~93%."
5. ✅ **Slide 22.** "16 de 16 · 11 de 16". *Na fala:* "negativa nas 16, significante em 11".
6. ✅ **Ficha do #39.** O crédito rural agora está em "R$ de dez/2024", como no texto.

### 1.3 Verificações opcionais

- ✅ **Sensibilidade da W a k = 4 e k = 12.** Feita (ver 1.1); fecha a pergunta 30 da Parte 3.
- ☐ **Acurácia da Coleção 10.1 por classe** (pastagem, agricultura, mosaico) no Cerrado. Não precisa rodar nada, só ler o documento de acurácia do MapBiomas. Pergunta 37.
- ☐ **Teste de raiz unitária com quebra (Zivot-Andrews)** na pastagem do Norte. A classificação I(2) veio de ADF e KPSS, sem modelar quebra. Se não rodar, use a resposta da pergunta 25.

---

## Parte 2: a fala, slide a slide

A fala está entre aspas angulares (>). As instruções entre colchetes são ações e não devem ser lidas. O tempo está entre colchetes no título de cada slide. Os slides marcados com ✂ são os primeiros a encurtar.

**Marcos de ensaio:** balança por volta dos 9–10 minutos; teste do empurrão por volta dos 16–17; estoque e taxa por volta dos 21–22; síntese até cerca de 24.

### 1 · Título [0:30]

[Olhe para a banca antes de olhar para o mapa.]

> Bom dia. Agradeço à banca pela leitura e ao professor Laerte pela orientação. O trabalho se chama *A marcha ao norte* e trata da dinâmica de uso e cobertura da terra em Goiás entre 1985 e 2024 e dos seus fatores socioeconômicos. Vou apresentar o problema, os dados, as quatro perguntas em que a investigação se dividiu e, no fim, o que cada resposta não alcança.

### 2 · O mapa de 1985 a 2024 [1:15]

[Mostre 1985 e dê dois segundos para reconhecer Goiás. Um toque por ato.]

> Isto é Goiás a cada ano, pixel a pixel, na Coleção 10.1 do MapBiomas, a 30 metros. Verde é vegetação natural, amarelo é pastagem, rosa é agricultura. *[Ato I]* O estado já entra ocupado. Em 1985, quase um terço de Goiás é pasto, herança de frentes de ocupação anteriores ao início da série. Não estou vendo o começo da ocupação, e sim quatro décadas de transformação de um território já usado. *[Ato II]* A partir de 2001, o sudoeste (Rio Verde, Jataí, Mineiros) passa à lavoura, e passa sobre o pasto. *[Ato III]* E o Cerrado que resta, no norte e no nordeste, continua cedendo. *[pergunta]* O mapa sugere uma reorganização. Mas olhar a sequência não diz se ela é mensurável, nem se uma região está provocando a transformação da outra.

### 3 · A hipótese de partida [1:00]

[Uma revelação por etapa. Pausa antes do limite.]

> O trabalho partiu de uma hipótese clássica, a da pastagem como estágio intermediário: vegetação vira pasto, pasto vira lavoura. Em Goiás, ela ganha forma geográfica. No Sul, a lavoura toma o lugar do pasto. O pasto deslocado sobe para o Norte e leva o boi junto. E lá abre o Cerrado que ainda resta.
>
> São três partes: uma substituição no Sul, uma ligação entre as regiões e uma abertura no Norte. As duas pontas podem existir sem que a ligação exista. Adianto o desfecho: as duas pontas aparecem nos dados, e o elo entre elas, o empurrão, não apareceu nos testes. Boa parte desta apresentação é sobre como esse elo foi procurado.

### 4 · Três famílias de explicação [1:15]

> O mesmo mapa comporta três explicações, que não se excluem. A primeira é o deslocamento indireto de uso da terra, o iLUC: uma região empurra a outra. Aqui testo um canal de curta distância, dentro do estado. Se for isso, a conversão tem origem localizável e uma política regional pode alcançá-la.
>
> A segunda é a de forças de mercado comuns. As duas regiões respondem ao mesmo incentivo, com intensidade diferente ao longo do gradiente Sul–Norte. Se for isso, não há origem a conter.
>
> A terceira é o encolhimento do próprio Cerrado exposto à conversão, que faz o ritmo depender do que resta, e não só do mercado.
>
> As três descrevem o mesmo mapa e recomendam ações diferentes. Por isso o trabalho precisava de um desenho capaz de rejeitar as que não se sustentam, e não só de descrever.

### 5 · Pergunta de pesquisa [0:30]

> A pergunta geral é como e por que o uso da terra mudou em Goiás entre 1985 e 2024. Na forma mais precisa: o que coordena a reorganização espacial da produção agropecuária no estado?

### 6 · Justificativa e objetivos [1:15]

[Não leia os objetivos. Use-os como sumário.]

> Goiás tem uma vantagem de comparação. Dentro dele coexistem os dois regimes que a literatura do Cerrado compara entre regiões distantes: um Sul consolidado, onde a expansão acontece sobre área já aberta, e um Norte em fronteira, onde ela avança sobre vegetação natural. Aqui os dois são medidos com o mesmo classificador, a mesma malha e a mesma fonte. Isso não elimina que o erro de classificação varie entre regiões, mas tira do caminho as diferenças de régua.
>
> O que está em jogo é mensurável: 6,56 milhões de hectares de savana e campo ainda expostos à conversão, 44% deles no Norte. Esse número mede o Cerrado que ainda pode ser perdido, e não terra livre para converter.
>
> Os objetivos específicos são as quatro perguntas que organizam o resto da apresentação: o deslocamento existe? Quais conversões o compõem? O Sul empurrou o Norte? E por que a conversão desacelerou onde desacelerou?

### 7 · Dados e método [1:30]

> Três princípios atravessam o trabalho. O primeiro é contar tudo: todos os pixels de Goiás nos 40 anos, na grade original do produto. Censo não quer dizer ausência de erro, porque a classificação continua sendo uma estimativa. Quer dizer que não há sorteio de pixels. Uma amostragem anterior tinha defeitos que mudavam resultados, e foi substituída.
>
> O segundo é fixar o território. Goiás tinha 184 municípios com estatística em 1985 e tem 246 hoje. O satélite recorta o município atual em todos os anos, e o IBGE tabula o município como ele existia naquele ano. No ano da emancipação, um município-pai chega a registrar queda de 50% a 80% no rebanho. Isso é perda de território, não dinâmica pecuária. Por isso toda análise longitudinal usa as 166 Áreas Mínimas Comparáveis de Ehrl, de 2017, unidades cujo contorno não muda no período.
>
> O terceiro é conferir por fora. Cada medida do satélite tem uma contraparte que não passa pelo classificador: a soja plantada e o rebanho do IBGE, o crédito rural, o câmbio. Nos gráficos, a etiqueta IBGE marca essas medidas. Essa triangulação não transforma nenhuma fonte em verdade, mas mostra quando as duas divergem, e é o que salva a leitura do fim da série daqui a pouco.

### 8 · Três atos [1:30] ✂

> Para dividir os 40 anos, as fronteiras não foram escolhidas antes. Elas saem de testes de quebra estrutural aplicados às variações anuais de vegetação, pasto e lavoura, com a regra de decisão fixada antes de rodar os testes. Saíram duas fronteiras, em 2001 e em 2020. Uma terceira candidata, em 1991, tinha suporte bem mais fraco e não foi adotada.
>
> *[Ato I]* O Ato I, de 1985 a 2000, é o mais destrutivo em volume. A pastagem avança 3,71 milhões de hectares e a vegetação natural cede 4,10. A lavoura também cresce, de 1,2 para 3,0 milhões de hectares, mas sem mudar de endereço.
>
> *[Ato II]* Sobre o Ato II, é preciso cuidado com o que muda em 2001. Não é a lavoura que acelera: ela mantém praticamente o mesmo ritmo. Quem inverte o sinal é a pastagem, que passa a perder área. Muda a fonte da terra: a lavoura passa a crescer sobre o pasto.
>
> *[Ato III]* No Ato III, de 2020 a 2024, o pasto recua quase quatro vezes mais rápido, e parte da lavoura nova passa a ser rotulada como "Mosaico de Usos". A quebra de 2020 aparece também na soja plantada do IBGE, que não passa pelo satélite. É essa âncora que a sustenta. E o Ato III tem cinco anos, então o que ele mostra é sinal inicial.

### 9 · O balanço de 40 anos [0:45] ✂

[Diga a unidade antes do número.]

> Somados os 40 anos, em milhões de hectares: a vegetação natural vai de 17,7 para 11,9 e a agricultura de 1,2 para 5,6. A pastagem sobe até cerca de 14,8 em 2003 e depois recua, e comparar só as pontas esconderia essa virada. Cruzando o mapa de 1985 com o de 2024, 58% da área que entrou em agricultura veio de pastagem. É a parte da hipótese de partida que os dados confirmam: o pasto é o elo intermediário da maior parte da expansão agrícola.

### 10 · O satélite diz que parou, o campo diz que acelerou [1:30]

[Diga o denominador: ritmo anual no Ato III comparado ao do Ato II, no Sul.]

> Antes das quatro perguntas, é preciso resolver um problema de medida. No Sul, lida só pela classe "Agricultura", a conversão de pasto em lavoura cai 88% no Ato III em relação ao Ato II. Parece que parou. Mas os hectares novos de soja que o IBGE registra por ano no Sul crescem 244%. Não são a mesma medida, mas a contradição pede explicação.
>
> Ela se resolve quando se somam as classes Agricultura e Mosaico: a conversão de pasto para uma das duas cresce 51%. O que parou foi o rótulo, e não a conversão.
>
> A consequência vale para o resto da apresentação. Toda medida de lavoura pelo satélite no fim da série aparece em duas versões: só Agricultura, que subconta, e Agricultura mais Mosaico, que superconta, porque o Mosaico também contém uso misto real. A soma não é a correção. Procuro as conclusões que valem nas duas versões, e onde há fonte de campo, é ela que decide.

### 11 · A balança: como se mede o centro [1:45]

[Fale mais devagar. Um avanço por ideia.]

> A primeira pergunta usa um instrumento que convém mostrar antes do resultado. *[halter]* Um halter com três quilos de um lado e um do outro, apoiado no meio, tomba para o lado mais pesado. Ele só se equilibra na média das posições ponderada pelo peso.
>
> *[Goiás de lado]* Em Goiás, cada uma das 166 AMC vira um peso, os hectares de pasto dela, pendurado no seu centroide. Para o rebanho, o peso é o número de cabeças. Visto de lado, com o norte à direita, o estado vira uma régua, e o apoio vai para o equilíbrio de 1985.
>
> *[1985→2024]* Trocando os pesos pelos de 2024, com o apoio parado, a régua tomba para o norte. O novo equilíbrio fica 77,6 quilômetros ao norte. Isso não quer dizer que algum hectare ou algum boi viajou 77 quilômetros. Quer dizer que mudou o peso relativo das partes do estado.
>
> *[sorteios]* E se o resultado dependesse de poucas AMC? Cada sorteio monta um Goiás alternativo, com as 166 AMC sorteadas com reposição, e são 2.000 sorteios. Como tenho todos os pixels, esse intervalo não mede erro de amostragem. Ele mede quanto o deslocamento depende de quais unidades carregam o peso. Como AMC vizinhas não são independentes, refiz também sorteando blocos de AMC vizinhas. A faixa alarga e o veredito não muda.
>
> *[vegetação]* Na vegetação natural, a faixa de 95% inclui o zero. Não detecto deslocamento do centro dela, o que é diferente de dizer que a vegetação ficou onde estava. Ela perdeu área, e o centro pode ficar no lugar enquanto a área cai.

### 12 · O centro de gravidade subiu, menos o da vegetação [1:30]

> O resultado: o centro de gravidade da pastagem está 78 quilômetros mais ao norte, o do rebanho medido pelo IBGE 67, o da agricultura 65, e a vegetação natural não tem deslocamento detectável. A lavoura fica sempre entre 123 e 135 quilômetros ao sul do pasto e do boi. As camadas sobem juntas, sem trocar de ordem.
>
> Um centro de massa sobe quando o Norte ganha peso na soma, mesmo que as duas regiões cresçam. E as três camadas sobem por razões diferentes. O pasto sai do Sul e entra no Norte. O rebanho fica parado no Sul e mais que dobra no Norte. A lavoura cresce nas três regiões, e cresce mais no Sul em hectares, mas a fatia do Sul cai de 92% para 71%. Então a afirmação é de redistribuição, e não de que as mesmas atividades se mudaram, e ainda menos de que uma região empurrou a outra.

### 13 · De 2019 a 2024, só a "Agricultura" parou [1:00] ✂

> No último quinquênio o problema do rótulo aparece de novo. As medidas que não passam pela classe "Agricultura" continuam andando para o norte: pastagem 12,9 quilômetros, rebanho 11,9, soja plantada 10,1. A Agricultura mais Mosaico anda 4,4. Só a Agricultura isolada fica parada, em meio quilômetro, e é a única cujo rótulo mudou no período. O erro de rótulo faz a marcha parecer menor, e não maior.
>
> *[resposta 1]* A resposta à primeira pergunta é sim. O tamanho exato do deslocamento agrícola recente continua dependendo da régua.

### 14 · A marcha é o saldo de duas conversões [1:00]

> Que conversão move esse centro? No Sul, a transição que manda é pasto→lavoura, terra que troca de função. No Norte, é vegetação→pasto, terra nova sendo aberta. A medida que separa os dois regimes não passa pela classe ambígua: do Ato II para o Ato III, a abertura de vegetação para pasto cai 49% no Sul e só 13% no Norte. Isso responde onde. Para saber como, uso outra medida: há quanto tempo o pixel era pasto quando virou lavoura.

### 15 · Dois tipos de pasto [1:45]

[Primeiro o histograma, depois a curva, só então a origem do pixel.]

> A idade aqui é o número de anos seguidos em que o pixel foi pasto antes de virar lavoura. Entram 16 milhões de conversões com idade conhecida. As que já eram pasto em 1985 têm idade desconhecida, só um mínimo, e ficam de fora.
>
> A distribuição tem um pico nos primeiros anos e uma cauda longa. Uma única curva, a tracejada, não alcança o pico nem a cauda. Duas componentes descrevem melhor a forma, uma perto de 4 anos e outra perto de 16. Mas o ajuste sozinho não prova dois mecanismos. O que pesa é a história do pixel: entre os pastos de até 3 anos, 45% já tinham sido lavoura antes, o que é compatível com rotação. Entre os de 30 anos ou mais, só 1% tinha sido lavoura: é pasto antigo que só agora virou lavoura.
>
> O ponto que importa é que os dois tipos convivem em toda parte, nas cinco mesorregiões e nas 166 AMC. A região explica 0,5% da variação da idade. Numa versão anterior, o Sul parecia converter pasto jovem e o Norte pasto velho, mas esse gradiente vinha do rótulo do Mosaico, que tirava da conta justamente as conversões recentes do norte. Corrigido isso, sobra a convivência.
>
> *[resposta 2]* O que decide entre girar o capim em três anos ou deixá-lo trinta está abaixo da escala municipal, no imóvel rural.

### 16 · O que o empurrão deixaria nos dados [1:45]

[Mapa de Acreúna, depois a nuvem, depois o tempo.]

> Agora a pergunta central. Coincidência no espaço não é mecanismo, porque dois processos movidos pela mesma força desenham o mesmo mapa que um empurrão desenharia. É preciso procurar uma marca que só o empurrão deixa, e são duas.
>
> *[esperado]* No espaço: se a lavoura cresce nos vizinhos ao sul, o pasto aqui deveria crescer, descontada a lavoura local. Na AMC de Acreúna, por exemplo, tomo os oito vizinhos mais próximos e fico com os que estão ao sul. Os do norte ficam de fora e servem de controle. No tempo: a lavoura do Sul deveria vir primeiro e o pasto do Norte depois.
>
> *[espaço]* Cada ponto é uma AMC num ano, descontados os efeitos fixos de AMC e de ano. A inclinação que o empurrão exigiria é positiva. A observada é negativa, menos 0,157. Não leio isso como um mecanismo inverso, e sim como a ausência do sinal que a hipótese exigia.
>
> *[tempo]* No tempo, somar o passado da lavoura do Sul praticamente não melhora a previsão do pasto do Norte (p = 0,97). Isso não é 97% de chance de não haver empurrão. É só que o passado do Sul não acrescenta previsão.
>
> Não encontramos a assinatura do empurrão no canal testado.

### 17 · O placar [1:15]

> Esse resultado não depende de uma escolha. Os dois testes foram repetidos com três medidas de lavoura (Agricultura, Agricultura mais Mosaico e soja do IBGE) e em duas janelas, até 2019 e até 2024. No espaço, com oito vizinhos, as 12 inclinações são negativas, 0 de 12 na zona do empurrão. Refeito com quatro e com doze vizinhos, algumas do rebanho passam para o lado positivo, mas nenhuma se distingue de zero. No tempo, 0 de 24 testes significantes. São especificações relacionadas da mesma pergunta, e não 36 experimentos independentes.
>
> Um nulo precisa vir com o poder. Por simulação, o teste no tempo detecta um empurrão forte em cerca de 93% das vezes, mas um moderado só em cerca de 48%. Um empurrão moderado não fica descartado por ele.
>
> O que aparece no lugar é substituição local: onde a lavoura cresce, o pasto recua ali mesmo, entre meio e 1,1 hectare de pasto por hectare de lavoura, com p < 0,001 em 5 de 6 combinações.

### 18 · Se o empurrão não aparece, o que coordena? [1:45]

[Separe na voz: previsão, resultado, limite.]

> Descartar uma explicação não instala a seguinte. A leitura alternativa precisa de um teste próprio. A cadeia suposta tem três elos. O choque é comum: com o real desvalorizado, soja e carne exportadas rendem mais reais no estado inteiro ao mesmo tempo. A exposição é diferente: a aptidão agrícola da Embrapa é maior no Sul e menor no Norte. E daí sai uma resposta prevista: no Sul, a terra apta vai para a lavoura e o rebanho cresce menos; no Norte, o rebanho cresce mais.
>
> O modelo cruza a variação do câmbio com essa exposição. Como o efeito de ano absorve o que é comum a todos, ele estima a diferença de resposta entre lugares, e não o efeito do câmbio sobre Goiás. A direção é a prevista, mas o p fica entre 0,07 e 0,13. Uso uma permutação do câmbio porque, com um único choque nacional, o erro-padrão usual é otimista.
>
> E há mais uma restrição. A aptidão acompanha a latitude. Com a latitude no mesmo modelo, a aptidão perde 62% do efeito. O dado sustenta um gradiente Sul→Norte, sem dizer se ele é de solo, de acesso ou de tempo de ocupação, e sem separar o câmbio dos outros incentivos que andam com ele.
>
> *[resposta 3]* A resposta à terceira pergunta é não, no canal testado. O estímulo comum fica como hipótese compatível com os dados, sem identificação causal.

### 19 · Não faltou demanda [1:00]

> Última pergunta: por que o Sul desacelerou? A explicação intuitiva seria mercado fraco, e os indicadores não mostram isso. No Ato III, o câmbio real está 26% mais desvalorizado que no Ato II, e a cotação internacional da soja convertida por esse câmbio está 79% mais alta. Os dois indicadores dividem o câmbio, então não são sinais independentes, mas nenhum deles cai.
>
> O mais direto é o próprio Sul. Ele não parou de converter terra: a conversão de pasto em lavoura ou uso misto sobe 51%, enquanto a abertura de vegetação cai 49%. No estado, a abertura de vegetação quase não muda (0,071 para 0,072 milhão de hectares por ano). Ela mudou de endereço.

### 20 · Onde resta menos, converte-se mais devagar [1:45]

[Aponte o gráfico. Diga que a regressão da taxa é uma análise à parte.]

> O gráfico mostra, para cada região, a savana e o campo que restam como percentual do que havia em 1985. O Sul desce mais rápido, é o único que cruza os 60% e estabiliza a partir de 2019, em cerca de 53%.
>
> Converter menos hectares pode ser só consequência de restar menos. Por isso olho a taxa, a fração do que resta que é convertida a cada ano. Dentro de cada unidade, quanto menos resta, mais devagar se converte o que resta. A relação é negativa nas 16 combinações testadas e significante em 11. É uma regularidade compatível com maior dificuldade de conversão, sem identificar a causa dela.
>
> Os limites: pela conta, só 17% da freada do Sul se deve a restar menos vegetação. Os outros 83% não têm causa isolada. A proteção integral não explica: 94% a 97% do que resta está fora dela, e ela cresceu 0,12 milhão de hectares desde 1985, contra 4,11 milhões suprimidos. Reserva Legal, APP e fiscalização ficam em aberto, porque sem o cadastro pixel a pixel não se separam de esgotamento.
>
> *[resposta 4]* E o que sobra no Sul é, em três quintos, floresta (mata de galeria e cerradão), que a fronteira não consome. A conversão segue para o Norte, onde ainda há savana.

### 21 · O que a marcha custou [1:15] ✂

> Em carbono, a conversão removeu da vegetação natural cerca de 973 milhões de toneladas de CO₂ equivalente, com as densidades do Quarto Inventário Nacional. Isso é estoque removido, e não emissão. Descontado o que pasto e lavoura estocam no lugar, a emissão líquida fica em cerca de 833, sem o carbono do solo. Três quartos saíram no Ato I. Depois a fronteira passou a consumir quase só savana. O carbono é uma dimensão do custo ambiental, e não o custo inteiro.
>
> No desenvolvimento, o Norte quase dobrou a área cultivada entre 2013 e 2021, e a diferença de IFDM em relação ao Sul quase não mudou (0,092 em 2013, 0,083 em 2023). Dentro de cada município, dobrar a área vale 0,008 ponto de IFDM, diante dos cerca de 0,15 que o índice subiu na década. É uma associação, não uma causa, e o IFDM não esgota o que se entende por desenvolvimento.

### 22 · Veredito [1:00]

[Uma frase por linha.]

> Juntando as quatro respostas. Primeiro, o deslocamento existe: pasto, rebanho e lavoura estão 65 a 78 quilômetros mais ao norte, e a vegetação não tem deslocamento detectável. Segundo, ele é feito de conversões diferentes: pasto→lavoura no Sul, vegetação→pasto no Norte, com os dois tipos de pasto em todo lugar. Terceiro, o empurrão não apareceu em nenhuma das 36 especificações, e a substituição local apareceu em 5 de 6. Quarto, a taxa de conversão cai onde resta menos, negativa nas 16 combinações e significante em 11, o que é compatível com atrito de oferta. O que os testes não separam: câmbio, crédito e preço andam juntos, e aptidão e latitude também.

### 23 · O que isso diz à literatura [1:00] ✂

> A ordem dos usos prevista pela renda da terra, na síntese de Angelsen (2007), se mantém nos 40 anos, mas o dado não diz se ela é governada pela qualidade da terra ou pelo acesso. O Sul estabiliza sem regenerar: é o terceiro estágio de Angelsen e, pela definição de Rudel, ainda não é transição florestal, com o cuidado adicional de que no Cerrado savana e campo são vegetação nativa. O canal de vizinhança não aparece, e isso não refuta o iLUC de longo alcance de Arima e colegas (2011), cujo desenho liga municípios distantes. E o câmbio de Richards (2012) entra como candidato, sem que eu transporte para Goiás um efeito estimado em outra escala.

### 24 · Alcance e limites [1:00]

> O que cada resposta não alcança. Primeiro, um centro de massa não acompanha produtores nem capitais: a marcha é da distribuição, e não de agentes. Segundo, não sei o que escolhe entre as duas populações de pasto. Terceiro, o nulo não alcança deslocamentos de longa distância, entre estados ou com defasagem longa, e não identifica qual força move a marcha. Quarto, não sei quanto do que resta é Reserva Legal e APP, e o Ato III tem cinco anos. E, atravessando tudo, a medida depende de um classificador, que mudou de comportamento no fim da série.

### 25 · Até a defesa [0:40]

> Até a defesa, o cronograma prevê depósito em dezembro e defesa em janeiro. A prioridade é a revisão de literatura, começando por quem já testou deslocamento em escala subnacional. Nas análises, a frente principal é procurar uma medida de exposição econômica que não cresça junto com a latitude. Se ela não existir, isso fica declarado como limite. A qualificação é o momento de discutir se a delimitação das conclusões e essas prioridades estão adequadas.

### 26 · Fecho [0:20]

[Volte ao mapa. Pausa antes da última frase.]

> Comecei com uma imagem de efeito dominó. É o mesmo mapa, com outra leitura: no Norte, fronteira; no Sul, intensificação; e, como hipótese, um estímulo comum ao longo do gradiente Sul→Norte até o teto de oferta. Obrigado. Fico à disposição da banca.

### Reservas: só entram se houver pergunta

**R1 · Painel de evidências.**

> Esse ponto tem uma análise específica. Vou abrir a figura correspondente para mostrar a medida e o recorte.

[Abra só a página necessária, explique um resultado e volte. Se não abrir, responda com o que domina e ofereça localizar o detalhe depois.]

**R2 · Por que o Granger simples não basta.**

> Granger pergunta se o passado de uma série acrescenta previsão à outra, dado o passado dela mesma. É precedência preditiva, e não causalidade.
>
> Os testes classificaram a pastagem do Norte como integrada de ordem dois: nem a primeira diferença dela é estacionária. Pôr uma série assim contra uma estacionária fabrica precedência. De fato, o Granger simples acendia no sentido inverso, Norte→Sul, com p = 0,0007, e acendia igual em placebos sem mecanismo, como o pasto do Norte "prevendo" o pasto do Sul.
>
> O Toda-Yamamoto ajusta o modelo em nível com duas defasagens extras (d máximo = 2) e testa só as primeiras p. Com p = 1, estimo três defasagens e testo a primeira. Ele não acende em nenhum sentido (0,25 Sul→Norte e 0,45 Norte→Sul). O veredito é sem líder, e não "o outro lado venceu".

**R3 · De "quanto havia?" para "quanto mudou?".**

> Em nível, área e produção correlacionam cerca de 0,9 só porque as duas cresceram. Na primeira diferença, a pergunta passa a ser: quando a lavoura desta AMC subiu, o pasto dela recuou? Com a equação já em diferença, o efeito fixo de AMC tira o ritmo próprio de cada unidade, e o de ano tira o que é comum ao ano. O coeficiente mede o desvio em relação ao que a tendência local e o ano já previam. Isso melhora a comparação, mas não remove um fator omitido que mude de forma diferente entre lugares e anos, e por isso a leitura é associativa.

---

## Parte 3: banco de perguntas

**Como responder:** primeiro a resposta direta, depois uma evidência, depois o limite. A primeira resposta cabe em 30 a 60 segundos, e só se aprofunda se houver réplica. As respostas são sugestões de ensaio e só valem se corresponderem ao que você fez e entende.

As três perguntas mais prováveis, uma por perfil:
- **Sociólogo/cientista ambiental:** "Quem está marchando: produtores, capital ou só a distribuição medida?" (pergunta 13).
- **Estatístico:** "Se você tem um censo dos pixels, o que o intervalo do bootstrap representa?" (pergunta 21).
- **Economista:** "Que variação do seu desenho distingue o mecanismo que você propõe das explicações concorrentes?" (pergunta 1).

### Economista

**1. Você identifica um mecanismo causal ou só descreve correlações? Que variação distingue as explicações?**
O trabalho estabelece um padrão descritivo e testa implicações que só algumas explicações produzem. O empurrão exige θ > 0 com os vizinhos ao sul e precedência Sul→Norte. Essas assinaturas podem falhar, e falharam. O estímulo comum usa a variação conjunta do câmbio no tempo e da exposição entre AMC, que é a única variação que sobra depois dos efeitos fixos. Não há identificação causal forte: a substituição local é uma associação consistente, e o estímulo comum é compatível com os dados, não demonstrado.
*Se insistir:* dê um confundidor concreto, como uma estrada nova que muda ao mesmo tempo lavoura, pasto e acesso numa AMC. Os efeitos fixos de AMC e de ano não removem um choque específico de lugar e ano.

**2. Por que câmbio, e não preço, crédito, tecnologia ou infraestrutura?**
O câmbio é um candidato com teoria (Richards, 2012) e série longa. Mas preço, crédito e expectativa de renda se movem com ele e caem no mesmo efeito de ano. O desenho não reparte a contribuição de cada um. Não responda "o câmbio é nacional, logo é exógeno": um choque nacional pode andar junto com outros choques nacionais de efeito heterogêneo.

**3. Com efeito fixo de ano, como você estima efeito do câmbio?**
Não estimo. O termo comum do câmbio é absorvido pelo efeito de ano, e a exposição fixa pelo efeito da AMC. O que sobra é a interação: unidades com exposições diferentes respondem diferente no mesmo ano? A equação é `Δy_it = α_i + λ_t + γ(s_{t−1} × E_i) + ε_it`, com y = variação do rebanho em cabeças, s = câmbio real efetivo (Ipeadata GAC12, alta = real desvalorizado) e E = aptidão padronizada. γ é um contraste de respostas, não o efeito médio do câmbio.

**4. O R² within é 0,001. O efeito não é irrelevante?**
É pequeno, e não o apresento como grande. O que se lê é o sinal do gradiente e a especificidade, isto é, os placebos que saem vazios. Diga junto: **os desfechos de área são nulos** (pastagem com p entre 0,83 e 0,92; agricultura entre 0,60 e 0,77). O único gradiente com sinal aparece em cabeças de gado, e não em terra. A célula vem de uma grade de 192 testes e sobrevive ao controle de falsas descobertas numa família de 96 testes, mas não numa de 144.

**5. Isso é mesmo shift-share, ou Bartik?**
Por analogia: um choque comum cruzado com uma exposição local. Não é uma soma de muitos choques setoriais, e por isso as garantias de identificação de Borusyak e colegas não se aplicam automaticamente. O que importei desse debate foi a inferência: com um único choque, o erro agrupado é otimista (Adão, Kolesár e Morales, 2019), e por isso uso a permutação.

**6. Aptidão contra latitude não é só multicolinearidade?**
A correlação é moderada (−0,44, fator de inflação da variância de 1,24), então as duas se separam em princípio. Com as duas no modelo, a aptidão perde 62% da magnitude e a significância, e a latitude quase não se move. Isso não prova que a latitude seja causa, porque ela não é mecanismo econômico, e sim um resumo de tudo que varia de sul para norte. A leitura é que o desenho não atribui o gradiente a uma característica específica. *Se insistir:* distinga queda de magnitude, aumento do erro-padrão e mudança do p. São três coisas diferentes.

**7. Preço alto não prova demanda alta. E o seu "preço recebido" é o quê?**
Seja direto: o índice é a cotação internacional da soja em dólar multiplicada pelo câmbio real efetivo, normalizado. Não é preço pago ao produtor levantado em pesquisa, e contém o câmbio, então as duas barras não são independentes (Parte 1). "Não faltou demanda" é uma síntese dos indicadores de incentivo, e não uma curva de demanda estimada. A evidência mais direta é o próprio Sul: a conversão sobre pasto cresce 51% enquanto a abertura de vegetação cai 49%. Isso enfraquece a explicação por retração geral, sem descartar custos, margem ou crédito.

**8. Os 17% não enfraquecem a tese do teto de oferta?**
Limitam a explicação mecânica, e por isso estão no slide. O argumento se apoia na queda da taxa de conversão com o esgotamento e em descartar a demanda fraca e a proteção integral. Não atribuo os 83% à dificuldade da terra e não separo restrição física, legal e econômica. Não diga "as demais causas foram eliminadas": descartar algumas alternativas não descarta todas.

**9. As áreas das classes somam um território fixo. A substituição não é uma identidade?**
Em parte, sim. Com área fixa, ganho de uma classe exige perda de outra, e um coeficiente negativo entre lavoura e pasto não prova decisão econômica de substituir. O que a matriz de transição acrescenta é a origem e o destino de cada pixel: 58% da entrada em agricultura veio de pasto. Sobre o −1,14: mais de um hectare de pasto perdido por hectare de lavoura inclui outras classes e erro de medida, e não quer dizer "substituição mais que completa". É também a régua da união, que é o teto.

**10. Por que o pasto teria de ir para o vizinho? E se for para outro estado?**
Não precisa ir para o vizinho. O teste é de um canal específico: proximidade, dentro de Goiás, no mesmo ano. Redes de propriedade, compra de terra e cadeias comerciais podem ligar áreas distantes ou cruzar a divisa. O nulo vale para a assinatura procurada, e não para todo iLUC. Arima e colegas (2011) usam uma ligação distal, de centenas de quilômetros.

**11. Que política pública o resultado permite recomendar?**
Recomenda cautela ao atribuir a abertura do Norte a um efeito dominó do Sul. O que se pode dizer é geográfico e temporal: um instrumento teria de estar à frente da fronteira, no Norte, e antes de o fluxo chegar, porque a proteção integral existente está ao sul dela. Qual instrumento funciona, o desenho não diz, porque os marcos são federais e não deixam grupo sem tratamento.

**12. Por que não diferenças em diferenças nos marcos históricos?**
Foi feito e rebaixado. Plano Real, boom de commodities, Código Florestal e o rearranjo de 2018 atingem Goiás e os controles ao mesmo tempo, então não há grupo sem tratamento. Estudo de evento e placebo favoráveis não resolvem isso. Separar os efeitos exigiria variação dentro do estado, entre municípios mais e menos expostos, que o desenho não tem.

**12b. E a intensificação poupa terra ou desloca pressão?**
O estudo não responde isso causalmente. A lotação sobe de 1,45 para 1,94 cabeça por hectare, mas converter uma classe em outra não é medir produtividade, e falta o contrafactual de quanto se desmataria sem intensificação.

### Sociólogo / cientista ambiental

**13. Quem está marchando: produtores, empresas, capital ou só um indicador?**
Observo a redistribuição de áreas, rebanho e fluxos de conversão, e não a trajetória dos mesmos produtores ou capitais. "Marcha" é o nome do padrão geográfico medido, e não a prova de que agentes migraram. Um centro pode avançar sem ninguém se mudar: o rebanho do Sul fica parado e o do Norte dobra. Identificar quem produz a reorganização pede dado de estabelecimento, de propriedade e de rede empresarial, ou trabalho de campo. *Se insistir:* é uma delimitação substantiva, e não um detalhe de vocabulário.

**14. É um trabalho de ciências ambientais. Onde estão as relações sociais?**
Fazem parte do problema, mas o desenho não as observa. Não infiro relação de trabalho, conflito ou forma de apropriação a partir das cores do mapa. A contribuição ambiental está em ligar a reorganização produtiva à perda de vegetação, ao carbono e aos indicadores sociais, declarando esse limite.

**15. Como você usa Martins sem estudar os agentes?**
Como vocabulário para nomear o contraste, frente de expansão contra frente pioneira, e não como teste. As categorias de Martins são sociológicas (trabalho, propriedade, mediação capitalista), e o que eu meço é cobertura do solo e agregados municipais. A correspondência é analógica, e nada nos dados poderia testar a tese dele.

**16. Norte e Sul não escondem diferenças internas?**
Sim. Por isso a análise fina roda nas 166 AMC e até no pixel. A idade do pasto é o exemplo: a região explica 0,5% da variação. Tenha os recortes na ponta da língua. As três regiões são o Sul Goiano; o Centro Goiano com o Leste; e o Norte com o Noroeste. As cinco mesorregiões são outro recorte, e AMC não é município atual.

**17. "Terra exposta" não naturaliza a conversão como destino do Cerrado?**
Não é esse o sentido. O número mede o Cerrado que ainda pode ser perdido, e não uma reserva aproveitável nem terra desocupada. É um teto, porque inclui Reserva Legal e APP que não podem ser convertidas.

**18. Por que transição florestal num bioma de savana?**
Com adaptação e limites explícitos. No Cerrado, floresta não é sinônimo de vegetação natural, e mais cobertura arbórea não é recuperação ecológica. Uso a literatura para separar desaceleração da perda de recuperação, sem transferir a sequência formulada para paisagens florestais.

**19. O fluxo pasto→vegetação não é regeneração?**
Pode haver regeneração real em pixels específicos, e isso não fica excluído. Mas o fluxo reverso vai de 75% a 98% para savana e é quase simétrico ao de ida, com a razão entre ida e volta caindo de 8,4 para 1,22. Esse padrão é compatível com oscilação do classificador na borda entre pasto e cerrado. O componente real é minoritário e está na formação florestal. Não diga "provei que nada regenerou" nem "regeneração só anda numa direção".

**20. O IFDM basta para dizer que não houve desenvolvimento?**
Não, e não digo isso. O índice mede emprego e renda, educação e saúde, e não capta distribuição, conflito ou qualidade ambiental. O resultado é que a expansão agrícola não veio com convergência do IFDM regional. É uma associação, e médias regionais escondem distribuição.

**20b. O carbono resume o custo ambiental?**
Não. É a dimensão que dava para quantificar. Ficam de fora biodiversidade, água, conectividade, o carbono do solo e os impactos sociais.

**20c. Você não confunde falta física de terra com restrição legal?**
Essa separação está em aberto, e o texto diz isso. Sem o cadastro ambiental integrado pixel a pixel, "acabou a terra convertível" e "o que restou é legalmente inconversível" produzem a mesma série no Sul. Sobre o CAR: ele é autodeclarado e tem sobreposições. Usá-lo é o próximo passo, e não um dado que eu tenha agora.

**20d. Como o Estado e a história da ocupação entram?**
Entram no referencial e no contexto. Coincidir uma quebra estatística com um marco histórico não prova que o marco a causou. Por isso os marcos têm tipologia e não sustentam conclusão.

**20e. Que pesquisa de campo ajudaria mais?**
Comparar unidades com trajetórias de cobertura parecidas e acesso, estrutura fundiária e restrição ambiental diferentes, com entrevistas sobre decisões de conversão. É uma agenda complementar, que você não precisa prometer para esta dissertação.

### Estatístico

**21. Se você tem um censo de pixels, o que o intervalo do bootstrap representa?**
Para o produto e o período observados, o deslocamento é uma descrição calculada sobre todas as unidades, sem erro de amostragem de pixels. O bootstrap das AMC mede a **sensibilidade à composição das unidades**: quanto o resultado depende de quais AMC carregam o peso. Ler o intervalo como inferência exige tratar a configuração observada como uma realização de um processo espacial, o que é uma hipótese. O intervalo **não inclui o erro de classificação** e não simula confusão entre pasto, savana e agricultura. *Réplica provável: "qual é o seu estimando?".* Distinga o deslocamento do produto observado de uma leitura mais ampla que exigiria um modelo de superpopulação.

**22. O que significa o intervalo da vegetação incluir zero?**
Que, pelo procedimento usado, não distingo o deslocamento estimado (+7,6 km) de zero. Não afirmo que ele parou exatamente, e o centro estável não quer dizer vegetação conservada. Aberta por formação, a floresta anda +8,7 km (IC entre +2,5 e +15,1) e a savana, que domina o agregado, não anda.

**23. Por que o bootstrap individual seria válido com dependência espacial?**
Não seria sozinho, e por isso há o bootstrap de blocos. Os blocos saem de k-médias sobre os centroides, compactos mas sem contiguidade garantida, com 1 a 14 AMC por bloco. A faixa da pastagem vai de 45 para 80 km de largura, e pastagem, rebanho e agricultura excluem o zero nas seis partições. A componente leste não sobrevive: a da pastagem inclui o zero já em blocos de 3 AMC. Isso é robustez dentro da grade testada, e não prova de cobertura correta sob qualquer dependência.

**24. Todas as inclinações negativas excluem um efeito positivo?**
Não só pelo sinal. Onze das doze não são significativas, e o conjunto não é um teste de equivalência. As 12 não têm cálculo de poder próprio. O que elas estabelecem é que a assinatura positiva não aparece. *Réplica: "que magnitude você consegue descartar?".* Não invente. Mostre o limite superior do intervalo da especificação pertinente (Figura 8 e Tabela SLX do apêndice) ou diga que isso pede um teste de equivalência com efeito mínimo relevante definido.

**25. Como você concluiu que a série é I(2)? Testou raiz unitária com quebra?**
ADF (a hipótese nula é raiz unitária) e KPSS (a hipótese nula é estacionariedade) em nível, na primeira e na segunda diferença. Só na segunda os dois concordam em estacionariedade. Com 40 observações e duas quebras estimadas, a ordem de integração é um diagnóstico de trabalho, e não uma propriedade do processo. **Não foi feito teste com quebra (Zivot-Andrews ou Perron).** Se perguntarem, reconheça. O veredito sem líder também se apoia nos placebos, em que o pasto do Norte "prevê" o pasto do Sul, e não só na ordem de integração.

**26. Por que Toda-Yamamoto, e o que exatamente é testado?**
É um VAR em nível com p + d_max defasagens, com o teste de Wald só nas p primeiras, o que dá validade sob integração nas condições do método. Com p = 1 e d_max = 2, estimo três defasagens e restrinjo a primeira. Continua sendo precedência preditiva. Com n em torno de 37 e 3 a 4 defasagens, o próprio TY tem pouco poder, e por isso o veredito combina TY, placebos e retirada da tendência.

**27. O poder de 93% e 48% vale para qual teste e qual efeito?**
Monte Carlo do Granger simples (F com soma dos quadrados dos resíduos, T = 38), com efeito forte = correlação parcial ≈ 0,5 (93%) e moderado ≈ 0,3 (48%), tamanho de 5% sob o nulo, em `scripts/_poder_granger_deslocamento.py`. Não vale para o Toda-Yamamoto nem para as 12 inclinações espaciais, e não é a probabilidade de a conclusão estar certa. Antes da banca, confira no script o número de repetições.

**28. p = 0,97 é 97% de chance de não haver empurrão?**
Não. O p mede a compatibilidade da estatística com o modelo sob o nulo, e não a probabilidade da hipótese (declaração da ASA sobre p-valores). Aqui significa apenas que não rejeito a ausência de contribuição preditiva.

**29. Por que permutação circular? E o 0,026 da latitude?**
Ela rotaciona a série do câmbio mantendo a ordem interna, o que preserva a autocorrelação. A livre embaralha e tende a ser otimista. Com 38 posições, o menor p possível é 1/38 ≈ 0,026. Então o 0,026 da latitude sozinha significa "nenhuma rotação superou o observado", o melhor resultado possível do teste, e não uma margem folgada. E 38 anos não são 38 choques independentes. A permutação dá uma referência sob hipóteses, e não uma randomização.

**30. Como a matriz W define vizinhança? É robusto a outra W?**
São os oito vizinhos mais próximos por distância entre centroides, dos quais ficam os que estão ao sul, com a linha padronizada para somar um. Três AMC de borda ficam sem vizinho ao sul e entram com termo zero. Não são oito vizinhos obrigatoriamente ao sul, nem fronteira compartilhada. **Refiz com k = 4 e k = 12.** O que não depende de k: nenhum θ positivo significativo, o pasto negativo nas 6 células e o β local praticamente igual nas três matrizes. O que depende: a contagem de negativos (12 de 12 com k = 8, 10 com k = 4, 8 com k = 12, e os positivos são todos do rebanho, com p ≥ 0,70) e o único p = 0,02, que some com 4 e com 12. Com k = 12 o placebo ao norte da soja acende mais, o que reforça a ressalva de especificidade. Contiguidade e raio não foram testados; não afirme robustez a eles.

**31. Muitas especificações: como você trata multiplicidade e seleção?**
Grades exploratórias têm família declarada e correção de Benjamini-Hochberg: o teste de vazamento do #21 tem 0 de 36 depois da correção, e a grade do motor comum tem 192 testes. As 16 do esgotamento são leituras da mesma hipótese, declarada antes. A concordância entre elas indica estabilidade, e não 16 confirmações independentes, e 11 p-valores abaixo de 5% não formam um teste global.

**32. Duas gaussianas provam duas populações? E o ΔBIC?**
Não. Uma distribuição assimétrica pode ser aproximada por duas normais sem que haja dois grupos naturais. Com censo, o ΔBIC é astronômico, porque mede o tamanho do n e não a evidência, e por isso não é critério (D23). O que sustenta a leitura são medidas sem ajuste: a mediana por origem (5 anos se veio de lavoura, 13 se veio de vegetação) e o contraste de 45% contra 1% de lavoura anterior.

**33. E a censura da idade?**
A distribuição conhecida está condicionada ao que é observável. Dos 44,6 milhões de eventos, 16,0 milhões têm idade conhecida, e cerca de 64% são pasto que já existia em 1985, com idade mínima e não exata. O Ato I é unimodal por construção: em 1995, nenhum pasto pode ter mais de 10 anos de idade observada. Nada se afirma sobre tendência. E 16 milhões de pixels não são 16 milhões de observações independentes, nem um pixel é um produtor.

**34. Esgotamento negativo é erro? Por que excluir unidades?**
A fração 1 − estoque atual / estoque de 1985 pode ser negativa sem erro nenhum: basta o estoque crescer. O problema era tratá-la como fração entre 0 e 1 e padronizá-la, com denominadores perto de zero e oscilação de classificador. Ela chegava a −84,9 em 14% dos pares, e o coeficiente era achatado. Comparo quatro tratamentos: excluir as 46 unidades, que têm 17,3% do estoque de 2024, muda a população, e o piso em zero cria massa artificial em zero. A leitura descansa na concordância entre eles, e o coeficiente é comparado em unidade natural, porque o desvio-padrão varia 17 vezes entre tratamentos.

**35. Taxa e esgotamento usam o mesmo estoque. Não é associação construída?**
Há acoplamento, e o texto diz para que lado ele empurra. O estoque anterior está no denominador da taxa e, com sinal trocado, no esgotamento, e isso empurra o coeficiente **para cima**, de modo que achar sinal negativo é achar contra a montagem. Não resolve tudo sobre a estrutura do erro. É uma regularidade, e não uma identificação causal. E fluxo = taxa × estoque é identidade, então o β = 2,76 do fluxo sobre o estoque não prova nada.

**36. Os testes de quebra escolheram as datas sem intervenção? E a quebra de 2020 não é o Mosaico?**
As séries orientaram as datas, com escolhas explícitas e fixadas antes: segmento mínimo de 5 anos, até 3 quebras, F ≥ 4 e a exigência de o primário concordar com ao menos um método de sensibilidade. O STARS é uma implementação simplificada e só corrobora. Houve teste com séries de ruído, e o Kruskal-Wallis (H = 20,3) descreve, mas não valida, porque as fronteiras saíram dos mesmos dados. Sobre 2020: **a soja plantada do IBGE quebra em 2020 sozinha**, sem passar pelo satélite. Admita a ressalva: separado o Mosaico, o pico da divergência entre matrizes migra para 2022.

### Sobre o dado (qualquer um dos três)

**37. Qual a acurácia do MapBiomas para pastagem e agricultura?**
Leia o número antes (Parte 1). A resposta estrutural: a acurácia do classificador é o limite que nenhum recorte alcança, e a estratégia foi ancorar cada medida numa fonte que não passa por ele.

**38. O Mosaico não é integração lavoura-pecuária real?**
Parte pode ser, e por isso a soma é teto e não correção. Indícios de que é reetiquetagem: o centro da massa que mudou de rótulo fica 46 km ao norte da agricultura visível, e o crescimento dela por região acompanha a soja do IBGE (correlação de 0,84; 1,52 contra 1,53 milhão de hectares). Converter o intervalo em ponto exigiria comparar com outra coleção, o que não foi feito.

**39. O rebanho da PPM é confiável?**
É uma estimativa por informante. O dado de vacinação da defesa agropecuária seria uma alternativa. O padrão do rebanho coincide com o do pasto do satélite, que é outra fonte.

### Transversais e fechamento

**40. Qual é a contribuição, se as causas ficam abertas?**
Três coisas. O teste formal do canal intraestadual por vizinhança, que as fontes consultadas não trazem. O centro de massa aplicado a fluxos de transição. E o procedimento piso/teto ancorado em campo para um rótulo que mudou, que vale para qualquer uso da série. A contribuição não depende de uma explicação total.

**41. É original? Ninguém fez antes?**
A originalidade está na combinação de recorte, fontes comparáveis, verificações e teste delimitado. A revisão atual não autoriza dizer que não existe precedente, e a busca sobre deslocamento subnacional é a frente prioritária até a defesa.

**42. O que pode mudar até a defesa?**
A delimitação dos mecanismos, com a literatura e a busca de uma exposição que não acompanhe a latitude. O compromisso é registrar as mudanças, como já está feito com os resultados superados.

**43. Você usou IA. Como demonstra autoria e domínio?**
O uso está declarado: implementação, figuras e auditoria de consistência. Pergunta, decisões e interpretação são suas, e as 31 decisões registradas mostram as escolhas feitas. A demonstração é explicar uma escolha, reconstruir uma conta e localizar um número na fonte ali mesmo. Só afirme verificações manuais e leituras que você de fato fez.

**44. Mostre como eu reconstruo um resultado.**
Pegue o deslocamento da pastagem. Pesos anuais por AMC e centroides em EPSG:5880, média ponderada em 1985 e em 2024, diferença das coordenadas, conferência com o CSV da rotina #32. Numa regressão, mostre amostra, transformação, especificação e inferência.

**45. Qual a limitação mais importante?**
Há duas, de natureza diferente. Para as causas, separar mecanismos espacialmente correlacionados sem variação que os identifique. Para a medida, o erro de classificação. Melhorar o classificador aperfeiçoa a medida, mas não cria identificação causal.

### Quando não souber, ou quando o erro for demonstrado

> "Consigo explicar a escolha geral, mas não tenho agora o parâmetro exato dessa implementação. Vou conferir no script antes de afirmar. O resultado que apresentei foi obtido na configuração documentada, e a sensibilidade que você propõe merece ser examinada."

> "Concordo com essa distinção. A formulação que usei foi mais forte do que o resultado permite. Vou ajustá-la para [formulação precisa]. Isso altera [a interpretação, a magnitude ou o alcance], e preciso verificar se afeta os demais resultados."

Não prometa que o erro é só de redação antes de verificar. Anote o ponto, confirme que entendeu a objeção e responda ao que foi perguntado.

---

## Parte 4: plano de domínio

### 4.1 Onde concentrar o esforço

| Prioridade | Tema | Por que merece atenção | Slides |
|---|---|---|---|
| Máxima | Estímulo comum: interação, efeitos fixos, permutação, corrida entre exposições | É onde se confunde associação com causa, e aptidão com mecanismo | 18, 22–24 |
| Máxima | Granger, integração, Toda-Yamamoto e poder | Um nulo ocupa parte central da tese e depende de inferência adequada | 16–17, R2 |
| Máxima | Estoque, fluxo, taxa e esgotamento | Uma identidade contábil pode passar por descoberta | 19–20 |
| Máxima | Centro de massa, censo e bootstrap | A balança vai ser lembrada e leva o estatístico à definição da incerteza | 11–13 |
| Alta | Medida: AMC, Mosaico, transições, recortes | Sem as definições, os números parecem contraditórios | 7–10, 14 |
| Alta | Agentes e o que "marcha" significa | Essencial com o sociólogo | 3–6, 23–24 |
| Alta | Mistura de gaussianas e censura | Duas componentes não são dois mecanismos | 15 |
| Alta | Matriz W, painel espacial e composição | Define exatamente qual canal foi testado | 16–17 |
| Complementar | Periodização, carbono, IFDM | Muitas escolhas e unidades | 8, 21 |
| Complementar | Metodologia do MapBiomas (pastagem, agricultura, Mosaico, acurácia) | Qualquer um pode perguntar "por que o rótulo mudou?" | 7, 10 |

Com pouco tempo, fique nas quatro máximas e nos fundamentos de medida. Não gaste tempo decorando os 36 resultados da grade.

### 4.2 Os temas, com exercício e critério de domínio

**1. Estímulo comum.** Distinga três afirmações: (a) o câmbio mudou; (b) unidades diferentes responderam diferente; (c) essa diferença foi causada pelo câmbio através da aptidão. O desenho trata (a) e (b), e não estabelece (c).
- *Exercício de quadro:* duas AMC com exposições E = −1 e E = +1, dois anos com câmbio s = 0 e s = 1. Calcule s × E nas quatro células e mostre que a interação contém uma diferença que não se reduz a uma constante de AMC nem de ano.
- *Domina quando:* explica sem dizer "endogeneidade" por que um choque omitido pode bater mais justamente onde a exposição é maior; lê os 62% como sensibilidade, e não como "a latitude causa"; distingue p agrupado, permutação livre e circular; sabe o piso de 1/38; e sabe dizer de que é feito o índice de preço (cotação em dólar × câmbio real).
- *Leia:* `Textos/pipelines/56_drive_horse_race_latitude.md`, `03_metodologia.tex` (shift-share) e as introduções de Adão et al. (2019) e Borusyak et al. (2022).

**2. Testes temporais.** Comece pela pergunta simples: "o passado do Sul acrescenta previsão ao Norte depois de considerar o passado do próprio Norte?".
- *Exercício:* escreva o modelo restrito (só o passado do Norte) e o irrestrito (mais o passado do Sul), e circule os coeficientes testados. Depois, com p = 1 e d_max = 2, desenhe o VAR com três defasagens e marque que o teste incide só na primeira. Por fim, conte a história do p = 0,0007 em dois minutos, sem slide.
- *Domina quando:* sabe distinguir tendência determinística, raiz unitária e quebra estrutural; sabe as hipóteses nulas do ADF e do KPSS; explica por que p = 0,97 não é 97%; sabe que o poder simulado é do Granger simples (correlação parcial de 0,3 e 0,5); e sabe que Zivot-Andrews não foi feito.
- *Leia:* `Textos/pipelines/42_granger_reverso_norte_sul.md`, a seção "Limitações" de `34_deslocamento_espacial.md` e a reserva R2.

**3. Estoque, fluxo e taxa.** Decore as definições:
`taxa_t = fluxo_t / estoque_{t−1}` · `fluxo_t = taxa_t × estoque_{t−1}` · `esgotamento_t = 1 − estoque_t / estoque_1985`.
- *Exercício obrigatório:* com 100 ha, convertem-se 10, e a taxa é de 10%. Com 50 ha restantes, convertem-se 5: o fluxo caiu pela metade e a taxa continua em 10%. Essa queda não prova dificuldade. Se forem 2 ha dos mesmos 50, a taxa cai para 4%, e é a queda da taxa que é a questão empírica. Depois, mostre que esgotamento = −1 significa estoque duas vezes o de 1985. Por fim, desenhe no quadro a decomposição 17/83.
- *Domina quando:* explica os 17% e os 83%; sabe o que muda ao excluir as 46 unidades ou pôr piso em zero; distingue relação dentro da AMC de comparação entre regiões; explica para que lado o acoplamento empurra o coeficiente; e não diz "os efeitos fixos tiram as tendências" sem mostrar a equação, porque a equação do teto está em nível.
- *Leia:* `Textos/pipelines/54_defensabilidade_perna4.md`, `39B_fronteira_dominio_deplecao.md` e §4.5 dos resultados.

**4. Centro de massa e bootstrap.**
- *Exercício:* ponha o Sul na posição 0 e o Norte em 100 km. Com pesos 80 e 20, o centro fica em 20 km. Com pesos 100 e 50, fica em 33,3 km. As duas regiões cresceram e mesmo assim houve marcha, então a métrica não prova expulsão nem migração. Depois responda em voz alta a pergunta 21, sobre o censo e o bootstrap.
- *Domina quando:* sabe o que é sorteado, o que fica fixo, e que a mesma reamostragem liga 1985 e 2024; distingue robustez ao pixel (79,2 contra 77,6 km), à malha, à classe e à dependência; e explica o intervalo que inclui zero sem concluir igualdade.
- *Leia:* `Textos/pipelines/55_robustez_bootstrap_bloco.md` e a página "Por dentro do método" do site.

**5. Medida e recortes.** Faça uma ficha para cada número central, com fonte, variável, unidade, território, período, denominador e transformação. Distinga:
- Agricultura, união Agricultura + Mosaico e soja do IBGE;
- estoque, saldo entre pontas, fluxo de transição e soma de eventos anuais;
- 40 mapas e 39 transições (e 38 diferenças no painel estimado);
- as viradas 2000–2001 e 2019–2020, que não pertencem a ato nenhum;
- município, AMC, 3 regiões e 5 mesorregiões;
- crescimento percentual, crescimento do acréscimo anual e pontos percentuais.

*Exercício:* explique o +244% sem dizer que a soja quadruplicou; explique por que 58% no cruzamento das pontas não quer dizer que cada pixel fez uma só transição; e explique por que Agricultura + Mosaico é uma régua de sensibilidade, e não um intervalo de confiança.
- *Leia:* `Textos/metodologia/areas_minimas_comparaveis.md`, `tratamento_deriva_mosaico.md` e `janelas_temporais.md`.

**6. Agentes, território e custo ambiental.**
- *Exercício de dois minutos:* responda "quem está marchando?" só com o que o desenho observa. Depois diga que dado levaria de redistribuição territorial a deslocamento de agentes.
- *Domina quando:* discute Martins sem transformar categorias em cores do mapa; explica por que desenvolvimento não se reduz ao IFDM, por que carbono não resume o custo ambiental, por que savana e campo são vegetação nativa, e por que "terra restante" não é "terra vazia".
- *Leia:* capítulos 2 e 5. Para cada autor central, anote uma proposição, a evidência usada pelo autor e a diferença entre o desenho dele e o seu: Angelsen, Rudel, Arima, Richards, Carneiro Filho & Costa, Martins e Cohn.

**7. Idade, mistura e censura.** Uma mistura pode ter um pico só. Explique primeiro o histograma sem curva, depois o ajuste, depois a origem do pixel. Se a interpretação depender só das curvas, está incompleta. Um pixel que já era pasto em 1985 e vira lavoura em 1990 tem pelo menos 5 anos de pasto, e não 5. Não chame todo pasto jovem de rotação: são 45%, e não 100%.
- *Leia:* `28C_bimodalidade_regional.md` e `28_idade_pastagem_critica.md`, respeitando os trechos marcados como superados.

**8. Matriz W, painel e substituição.** Desenhe seis pontos e monte uma linha de W com filtro ao sul. Distinga o coeficiente da lavoura local (β, substituição) do coeficiente dos vizinhos (θ, empurrão). Saiba se cada modelo põe covariáveis dos vizinhos (SLX), desfecho dos vizinhos (SAR) ou estrutura do erro (SEM). Corrigir o erro-padrão e mudar a especificação espacial são operações diferentes.
- *Leia:* `34_deslocamento_espacial.md` e `scripts/deslocamento_espacial.py:266`.

**9. Fichas curtas.**
- *Periodização:* sup-F de Quandt-Andrews multivariado (F = 62,2 em 2001 e 21,5 em 2020); STARS como sensibilidade; Kullback-Leibler indica direção e variação total indica localização; 1991 recusado; o Código Florestal de 2012 não quebra série nenhuma.
- *Carbono:* área × densidade × 44/12; 973 Mt removidos contra 833 Mt líquidos; quatro compartimentos, sem o solo; densidades de 64,72, 41,32, 24,94 e 36,21 tC/ha; a regra é que, quando a conclusão depende de uma razão entre parâmetros, é a razão que entra na sensibilidade (2,64 contra 1,57).
- *IFDM:* série revista 2013–2023, não emendável com a anterior; 0,008 ponto por dobrar a área, como associação.

### 4.3 Formulações arriscadas e as que você consegue defender

| Evite | Diga |
|---|---|
| "A vegetação ficou onde estava" | "Não detectamos deslocamento distinto de zero pelo procedimento adotado." |
| "A lavoura subiu 65 km" | "O centro de gravidade da lavoura está 65 km mais ao norte", porque ela cresceu mais no Sul em hectares. |
| "Como é censo, o teste perde o sentido" | "A incerteza precisa de uma população ou processo de referência; ter todos os pixels não elimina o erro de medida nem a dependência." |
| "Erro no desfecho sempre atenua o coeficiente" | "Erro clássico no desfecho custa precisão e poder; atenuação é de erro no regressor ou de erro não clássico." (Corrigir também no texto: Parte 1.) |
| "As 36 especificações rejeitam / refutam o empurrão" | "A assinatura procurada não apareceu nessas especificações relacionadas, com limites de precisão e de poder." Nunca "iLUC refutado". |
| "38 anos são 38 choques independentes" | "São cerca de 38 observações do estímulo, com possível dependência serial." |
| "A permutação resolve a inferência" | "A permutação dá uma referência sob hipóteses que precisam ser defendidas." |
| "Duas gaussianas provam duas populações" | "Duas componentes descrevem melhor a forma; o mecanismo vem da origem do pixel." |
| "As 16 sensibilidades não têm problema de multiplicidade" | "A concordância indica estabilidade, e não 16 confirmações independentes." |
| "O mesmo classificador elimina a diferença de medida entre regiões" | "O mesmo produto melhora a comparabilidade, mas o erro pode variar por classe, região e período." |
| "Proteção constante não explica mudança" | "A proteção integral não se moveu nem está no caminho; fiscalização, Reserva Legal e APP podem ter mudado, e não foram medidas." |
| "Gradiente de aptidão" | "Gradiente Sul→Norte, medido pela aptidão." |
| "Pasto voltando a ser Cerrado / regeneração" | "Oscilação do classificador na borda pasto–savana; regeneração real é minoritária e está na floresta." |
| "Preço recebido pelo produtor" | "Cotação internacional da soja convertida pelo câmbio real (índice)." |
| Rótulos de grau ("corroborante", "estabelecido", "evidência forte") | O placar do teste: "0 de 36", "16 de 16, 11 significantes", "p entre 0,07 e 0,13". |

### 4.4 Sete sessões de preparação

Cada sessão leva de 60 a 90 minutos. A ordem importa mais do que os dias.

1. **Argumento e medidas.** Explique as quatro perguntas sem slide, monte as fichas dos números e faça o exercício da AMC e dos denominadores. Aplique as correções da Parte 1.
2. **Centro e incerteza.** Faça a conta das duas regiões, a pergunta 21 em voz alta e a balança ensaiada.
3. **Painel e espacial.** Escreva a equação local e a de vizinhança, desenhe a W, e trabalhe primeira diferença, efeitos fixos e composição de áreas.
4. **Temporal.** Modelo restrito e irrestrito, ADF e KPSS, Toda-Yamamoto e os parâmetros do poder. Conte o p = 0,0007 sem slide.
5. **Interação econômica.** O exercício 2 × 2, confundimento, permutação, a construção do índice de preço, e as perguntas 1 a 12b.
6. **Oferta e dimensão ambiental e social.** O exercício de estoque e taxa, censura, carbono e IFDM, e responder "quem marcha?" e "que desenvolvimento?".
7. **Simulação completa.** Apresente com todas as revelações e marque o tempo. Depois responda a seis perguntas sem consulta, duas de cada perfil, e reestude só onde faltou.

### 4.5 Critério de prontidão

Para cada tema, atribua a si mesmo uma nota:
- **0:** reconheço o nome, mas não explico;
- **1:** repito a definição;
- **2:** explico com um exemplo e identifico as variáveis;
- **3:** reconstruo uma conta, digo uma limitação e respondo a uma mudança de cenário.

Busque nível 3 nas quatro prioridades máximas e nos fundamentos de medida.

A última checagem é prática: pegue um número, ache o arquivo que o produziu, diga a unidade, explique por que o método foi escolhido, dê uma alternativa e diga o que mudaria a conclusão.
