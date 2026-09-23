# O que estudar para dominar a apresentação

Preparação orientada à banca informada: economista, sociólogo/cientista ambiental e estatístico. Data: 23/09/2026.

Não é possível inferir seu domínio pessoal a partir dos arquivos. A prioridade abaixo considera a dificuldade dos métodos, a importância para o argumento e as perguntas que o próprio desenho convida. Use os exercícios para descobrir quais são suas lacunas reais.

## Onde eu concentraria o esforço

| Prioridade | Tema | Por que merece atenção | Slides |
|---|---|---|---|
| Máxima | Estímulo comum, interação, efeitos fixos e permutação | É o ponto em que se pode confundir associação com causa, e aptidão com mecanismo | 18, 22–24 |
| Máxima | Granger, integração, Toda–Yamamoto e poder | Um resultado nulo ocupa parte central da tese e depende de inferência adequada | 16–17, R2 |
| Máxima | Estoque, fluxo, taxa e esgotamento | A identidade contábil pode ser confundida com uma descoberta causal | 19–20 |
| Máxima | Centro de massa, censo e bootstrap espacial | A balança será memorável e pode levar o estatístico à definição da incerteza | 11–13 |
| Alta | Medida, AMC, Mosaico, transições e recortes | Sem domínio das definições, os números parecem contraditórios | 7–10, 14 |
| Alta | Quem são os agentes e o que “marcha” significa | Essencial para conversar com o sociólogo sem extrapolar indicadores territoriais | 3–6, 23–24 |
| Alta | Mistura de gaussianas e censura de idade | Duas componentes não equivalem automaticamente a duas práticas produtivas | 15 |
| Alta | Matriz espacial, composição e substituição | Define exatamente qual canal de deslocamento foi testado | 16–17 |
| Complementar | Periodização, carbono e IFDM | Têm muitas escolhas e unidades que precisam ser explicadas com precisão | 8, 21, 23 |

Se o tempo de estudo for curto, distribua o esforço entre as quatro prioridades máximas e os fundamentos de medida. Não gaste a maior parte do tempo decorando os 36 resultados da grade.

## 1. Estímulo comum: o tema economicamente mais difícil

Você precisa explicar a diferença entre três afirmações: o câmbio mudou; unidades diferentes responderam de maneira diferente; essa diferença foi causada pelo câmbio através da aptidão. O desenho observa e modela as duas primeiras de maneiras distintas, mas não estabelece a terceira.

A equação de estudo é:

`Δy_it = α_i + λ_t + γ(s_t−1 × E_i) + ε_it`

Aqui, `Δy` é a variação do rebanho; `s` é a transformação do estímulo cambial usada no modelo, defasada; `E` é a exposição fixa padronizada; `α` e `λ` representam efeitos de unidade e ano. Confira as transformações exatas no script: não basta chamar tudo de “câmbio”.

O termo comum do estímulo se confunde com os efeitos de ano. O termo fixo da exposição se confunde com os efeitos de unidade. A interação sobrevive porque varia entre unidades e anos. Isso explica por que o coeficiente representa um contraste de respostas, não o efeito total do câmbio.

**Exercício de quadro:** desenhe duas AMC com exposições diferentes e dois anos com estímulos diferentes. Calcule o produto exposição × estímulo nas quatro células. Mostre que a interação contém uma diferença que não se reduz a uma constante de AMC nem a uma constante de ano.

**Você domina quando consegue:** explicar, sem usar a palavra “endogeneidade” como resposta pronta, por que um choque omitido pode afetar mais justamente os lugares de maior exposição; explicar a queda de 62% como sensibilidade e não como prova de que latitude causa a marcha; distinguir p agrupado, permutação livre e circular.

**Atenção especial:** 38 anos não são milhares de choques independentes porque existem 166 AMC. Tampouco são necessariamente 38 realizações temporalmente independentes. Rotações circulares são uma referência inferencial condicionada a hipóteses, não uma fonte automática de exogeneidade.

**Leia:** [econometria do caderno](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/guia/p3b_econometria.tex), nos capítulos sobre efeitos fixos e interação; [corrida entre exposições](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/56_drive_horse_race_latitude.md); [metodologia](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/cap/03_metodologia.tex).

## 2. Testes temporais: o tema inferencial mais delicado

Sua explicação deve começar com uma pergunta simples: “O passado do Sul acrescenta informação à previsão do Norte depois de considerar o próprio passado do Norte?” Só depois entram Granger e Toda–Yamamoto.

Estude estacionariedade, raiz unitária, diferença e ordem de integração. Uma tendência determinística, uma raiz unitária e uma quebra estrutural não são sinônimos. Conheça as hipóteses nulas de ADF e KPSS e a especificação usada em cada teste.

**Exercício de quadro:** represente o modelo restrito com o passado do Norte e o irrestrito acrescentando o passado do Sul. Circule os coeficientes cuja nulidade é testada. Depois, para p = 1 e d máximo = 2, desenhe o VAR com três atrasos e marque que o teste incide apenas no primeiro atraso relevante, não indistintamente em todos.

**Você domina quando consegue:** explicar por que p = 0,97 não é 97% de chance de ausência do fenômeno; por que corrigir o erro-padrão não resolve sozinho uma especificação inadequada para integração; por que um resultado temporal não é uma observação de produtores migrando; e por que não se pode transportar o poder do Granger simulado automaticamente ao Toda–Yamamoto.

**Antes da banca, localize:** parâmetros dos efeitos forte e moderado na simulação; número de repetições; escolha de defasagens; tamanho efetivo das séries após diferenças e atrasos; diagnóstico dos resíduos. Saber dizer “93% e 48%” sem explicar como foram obtidos é insuficiente.

**Leia:** [Granger reverso e diagnósticos](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/42_granger_reverso_norte_sul.md), o capítulo correspondente no caderno e a reserva R2. A [documentação oficial do statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html) ajuda a conferir a hipótese e a ordem das colunas da implementação. Não substitui estudar as condições do teste.

## 3. Estoque e taxa: o tema com maior risco de circularidade

Memorize as definições, não apenas o resultado:

`taxa_t = fluxo_t / estoque_t−1`

`fluxo_t = taxa_t × estoque_t−1`

`esgotamento_t = 1 − estoque_t / estoque_1985`

**Exercício obrigatório:** há 100 hectares de vegetação e dez são convertidos num ano. A taxa é 10%. Depois, com 50 hectares restantes, cinco são convertidos. O fluxo caiu pela metade, mas a taxa continua em 10%. Essa queda de fluxo não demonstra maior dificuldade de converter. Se apenas dois hectares forem convertidos a partir dos mesmos 50, a taxa cai a 4%. É a mudança da taxa que acrescenta outra questão empírica.

Em seguida, explique por que esgotamento de −1 significa estoque atual duas vezes maior que o inicial. O valor é possível pela fórmula, mas não se comporta como uma fração de esgotamento entre zero e um. Não atribua automaticamente todo aumento a erro de classificação.

**Você domina quando consegue:** explicar o que significam 17% e 83%; identificar o que muda ao excluir 46 unidades ou aplicar piso em zero; distinguir uma relação dentro da AMC de uma comparação entre regiões; e explicar por que coeficiente negativo não identifica a causa da restrição.

**Outro cuidado:** efeitos fixos em uma equação em níveis não eliminam automaticamente qualquer tendência específica de cada unidade. A afirmação depende da especificação. Não use a expressão genérica “os efeitos fixos retiram as tendências” sem mostrar a equação.

**Leia:** [defensabilidade da quarta frente](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/54_defensabilidade_perna4.md), [domínio e esgotamento](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/39B_fronteira_dominio_deplecao.md) e a seção correspondente dos [resultados](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/cap/04_resultados.tex).

## 4. Centro e bootstrap: a explicação simples precisa suportar uma pergunta difícil

Você deve calcular uma média ponderada à mão e dizer o que cada peso significa. Para agricultura e pastagem, hectares; para rebanho, cabeças. São centros de distribuições diferentes.

**Exercício:** coloque o Sul na posição zero e o Norte na posição 100 km. Com pesos 80 e 20, o centro fica em 20 km. Depois, aumente ambos para 100 e 50: o centro passa a 33,3 km. As duas regiões cresceram, e ainda assim houve marcha ao norte. Isso demonstra por que a métrica não prova expulsão no Sul nem migração dos mesmos agentes.

**Bootstrap:** explique o que é sorteado, o que fica fixo e por que a mesma reamostragem de unidades deve preservar a ligação entre os anos comparados. Se forem reamostrados anos ou unidades independentemente de modo inadequado, a pergunta muda. Explique a diferença entre AMC individuais e blocos espaciais.

**A pergunta difícil:** se o mapa é observado integralmente, qual incerteza esse intervalo pretende representar? Você precisa distinguir sensibilidade à composição das unidades, uma interpretação de superpopulação sob hipóteses e erro de classificação do produto. O bootstrap de AMC não simula diretamente confusões entre pasto, savana e agricultura.

**Você domina quando consegue:** explicar o intervalo que inclui zero sem concluir igualdade; mostrar que centro estável não significa área conservada; distinguir robustez ao pixel, à malha, à classe e à dependência espacial; e não tratar a estabilidade na grade de blocos como prova universal de validade.

**Leia:** [matemática do caderno](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/guia/p3a_matematica.tex) e [bootstrap espacial](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/55_robustez_bootstrap_bloco.md).

## 5. Medida e recortes: os fundamentos que evitam contradições

Prepare uma ficha para cada número central: fonte, variável, unidade, território, período, denominador e transformação. A maior parte das confusões da banca pode surgir quando duas medidas parecidas têm definições diferentes.

Exemplos que você precisa distinguir:

- Agricultura do MapBiomas, união Agricultura + Mosaico e área plantada de soja do IBGE.
- Estoque num ano, diferença líquida entre pontas, fluxo de transição e soma de eventos anuais.
- Os 40 mapas anuais de 1985–2024 e os 39 intervalos entre anos consecutivos.
- Taxas medidas entre o primeiro e o último ano de cada ato e as transições de virada não atribuídas aos atos na convenção do trabalho.
- Município atual, AMC e agregação em três regiões ou cinco mesorregiões.
- Aumento percentual de área, aumento percentual do acréscimo anual de área e variação em pontos percentuais.

**Exercício:** explique +244% sem dizer que a área total de soja quadruplicou. É a comparação do acréscimo anual de área entre atos, no recorte indicado. Explique também por que 58% no cruzamento de dois mapas não significa que cada pixel fez uma única transição direta no intervalo inteiro.

**Atenção:** Agricultura + Mosaico é uma régua operacional de sensibilidade. Ela não é um intervalo de confiança, e chamar as classes de piso e teto não prova que toda a área agrícola verdadeira esteja matematicamente contida nesse intervalo sob qualquer erro de classificação.

**Leia:** [AMC](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/metodologia/areas_minimas_comparaveis.md), [Mosaico](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/metodologia/tratamento_deriva_mosaico.md), [janelas temporais](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/metodologia/janelas_temporais.md) e [convenções de classes](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/README.md).

## 6. Território, agentes e contribuição ambiental

Não é um tema secundário diante de uma banca interdisciplinar. Você precisa explicar o que os dados deixam invisível: trajetórias de produtores, concentração de propriedade, relações de trabalho, conflitos e redes de comercialização.

**Exercício de dois minutos:** responda “quem está marchando?” usando apenas observações que o desenho permite. Em seguida, proponha qual dado seria necessário para passar de redistribuição territorial a deslocamento de agentes.

**Você domina quando consegue:** discutir as categorias sociais do referencial sem torná-las sinônimos de cores do mapa; explicar por que desenvolvimento não se reduz ao IFDM; por que carbono não resume o custo ambiental; por que savana e campo são vegetação nativa; e por que “terra restante” não significa “terra vazia ou disponível”.

**Leia:** [referencial](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/cap/02_referencial.tex) e [discussão](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/cap/05_discussao.tex). Para cada autor central, anote uma proposição, a evidência usada pelo autor e a diferença entre o desenho dele e o seu. Não faça uma lista de nomes para decorar.

## 7. Idade, mistura e censura

Estude a diferença entre dois picos visuais e uma mistura de duas componentes. Uma mistura pode ter apenas um pico. Uma distribuição assimétrica pode ser aproximada por duas normais sem que os grupos sejam mecanismos naturais separados.

**Exercício:** explique primeiro o histograma sem curva nenhuma. Depois apresente o ajuste e, só então, a trajetória anterior do pixel. Se a interpretação dos mecanismos depender exclusivamente das duas curvas, sua explicação ainda está incompleta.

**Censura:** um pixel que já era pastagem em 1985 e vira lavoura em 1990 tem pelo menos cinco anos observados de pasto, mas pode ser muito mais antigo. Não pode entrar como se cinco fosse sua idade verdadeira. A distribuição de idade conhecida é selecionada pelo horizonte de observação.

**Você domina quando consegue:** explicar os aproximadamente 16 milhões como eventos com idade conhecida; mencionar a proporção excluída por censura; distinguir idade de permanência contínua e tempo desde a primeira abertura; e não chamar todos os pastos jovens de rotação porque 45% tiveram lavoura antes.

**Leia:** [bimodalidade e heterogeneidade](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/28C_bimodalidade_regional.md) e [crítica da idade](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/28_idade_pastagem_critica.md), respeitando as notas que identificam trechos superados.

## 8. Vizinhança, painel e substituição

Desenhe seis pontos num papel e construa uma linha de matriz de pesos. Depois explique como isso se generaliza para oito vizinhos mais próximos, filtrados por direção ao sul. A soma dos pesos da linha não vazia é um. A variável espacial é uma média da mudança nos vizinhos selecionados.

**Você domina quando consegue:** distinguir o coeficiente da lavoura local do coeficiente da lavoura dos vizinhos; dizer o que significa uma unidade sem vizinhos retidos; explicar o papel do controle ao norte; e diferenciar proximidade física, fronteira compartilhada e conexão econômica.

Conheça também a distinção conceitual entre SLX, SAR e SEM. Não precisa recitar todas as derivações, mas deve saber se o modelo relaciona o desfecho às covariáveis dos vizinhos, ao desfecho dos vizinhos ou à estrutura espacial dos erros. Corrigir erro-padrão e mudar a especificação espacial são operações diferentes.

**Leia:** [teste de deslocamento](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/Textos/pipelines/34_deslocamento_espacial.md) e a implementação de [pesos direcionais](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/scripts/deslocamento_espacial.py:266).

## 9. Resultados complementares que precisam de uma ficha curta

**Periodização:** método primário, sensibilidades, parâmetros, datas adotadas e limite do último segmento. Uma quebra não identifica sua causa histórica. A busca em múltiplos anos-candidatos precisa de avaliação apropriada.

**Carbono:** área por formação × densidade de carbono, seguida da conversão de C para CO₂ por 44/12. Diferencie os aproximadamente 973 Mt de estoque removido dos aproximadamente 833 Mt da conta líquida com desconto do destino. Conheça os compartimentos incluídos e excluídos. A fórmula não calcula todas as emissões de gases de efeito estufa da agropecuária.

**IFDM:** dimensões do índice, escala de zero a um, agregação regional, janela da área agrícola e janela do indicador. Se mencionar a associação de 0,008 ponto ao dobrar a área, saiba reconstruir a transformação do modelo que permite essa interpretação. Não diga que isso é um efeito causal.

## Formulações do material antigo que eu não decoraria literalmente

Há boas explicações no caderno anterior, mas algumas frases merecem cautela adicional na fala:

| Formulação arriscada | Formulação que você deve conseguir defender |
|---|---|
| “A vegetação ficou onde estava” | “Não detectamos deslocamento distinto de zero pelo procedimento adotado.” |
| “Como é censo, o teste perde o sentido” | “A incerteza precisa de uma população ou processo de referência; cobertura completa não elimina erro de medida ou dependência.” |
| “Erro no desfecho sempre atenua o coeficiente” | “O efeito depende da estrutura do erro. Erro aditivo clássico no desfecho não implica, sozinho, atenuação do coeficiente em regressão linear.” |
| “As 36 especificações rejeitam o empurrão” | “A assinatura procurada não apareceu nessas especificações relacionadas, com limites de precisão e poder.” |
| “38 anos são 38 choques independentes” | “Há cerca de 38 observações temporais do estímulo, com possível dependência serial.” |
| “A permutação resolve a inferência” | “A permutação oferece uma referência sob hipóteses que precisam ser defendidas.” |
| “Duas gaussianas provam duas populações” | “Duas componentes descrevem melhor a distribuição dentro dos modelos comparados; os mecanismos exigem evidência adicional.” |
| “As dezesseis sensibilidades não têm problema de multiplicidade” | “A concordância informa estabilidade, mas não produz dezesseis confirmações independentes nem um teste global automático.” |
| “O mesmo classificador elimina diferença de medida entre regiões” | “O mesmo produto melhora a comparabilidade, mas o erro pode variar por classe, região e período.” |
| “Uma proteção constante não pode explicar uma mudança” | “A área protegida pode ser estável enquanto fiscalização, cumprimento e incentivos mudam.” |

Essas correções não exigem abandonar o trabalho. Exigem saber exatamente qual inferência cada procedimento sustenta. A orientação geral de não converter p-valores em probabilidades de hipóteses está em consonância com a [declaração da ASA](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf).

## Plano de estudo em sete sessões

Cada sessão pode ocupar aproximadamente 60–90 minutos. Adapte à disponibilidade; a ordem importa mais que os dias. Reserve tempo adicional se os exercícios revelarem lacunas.

1. **Argumento e medidas:** explique as quatro perguntas sem slides; construa as fichas dos números; resolva o exemplo de AMC e os denominadores das comparações.
2. **Centro e incerteza:** faça a conta de duas regiões; explique o bootstrap, blocos e população de referência; ensaie a balança em voz alta.
3. **Painel e espacial:** escreva a equação local e a de vizinhança; desenhe W; explique primeira diferença, efeitos fixos e composição de áreas.
4. **Temporal:** desenhe restrito e irrestrito; explique ADF/KPSS e Toda–Yamamoto; localize os parâmetros das simulações de poder.
5. **Interação econômica:** faça o exemplo de duas exposições e dois anos; explique confundimento e permutação; responda às perguntas 1–12 do banco.
6. **Oferta e dimensão ambiental/social:** resolva o exercício de estoque e taxa; explique censura, carbono e IFDM; responda “quem marcha?” e “que desenvolvimento?”.
7. **Simulação completa:** apresente com os slides e todas as revelações; registre o tempo; depois responda a seis perguntas sem consultar, duas de cada perfil. Reestude apenas os pontos em que faltou explicação ou precisão.

## Critério para saber se está preparado

Para cada tema, atribua a si mesmo:

- **0:** reconheço o nome, mas não explico.
- **1:** consigo repetir uma definição.
- **2:** explico com um exemplo e identifico as variáveis.
- **3:** reconstruo uma conta, explico uma limitação e respondo a uma mudança de cenário.

Busque nível 3 nas quatro prioridades máximas e nos fundamentos de medida. A fluência verbal sem capacidade de reconstrução pode esconder uma lacuna.

Faça uma última checagem prática: encontre o arquivo que produziu um número, diga sua unidade, explique por que o método foi escolhido, apresente uma alternativa e diga o que mudaria sua conclusão. Se conseguir fazer isso sem recorrer a frases prontas, terá uma base sólida para a banca.

## Documentos que acompanham este plano

- [Fala completa, slide a slide](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/guia/ROTEIRO_ORAL_DETALHADO_2026-09-23.md).
- [46 perguntas prováveis e respostas](C:/Users/amara/OneDrive/Documentos/Antigravity/Mestrado/qualificacao/guia/PERGUNTAS_BANCA_2026-09-23.md).

O roteiro foi feito para uma apresentação de até 30 minutos. A possibilidade de ultrapassar um pouco deve funcionar como margem para pausas, não como planejamento de uma exposição maior.
