# Revisão da apresentação de qualificação

Arquivo analisado: `Visualizacao/apresentacao.html`, com os três JavaScript associados, CSS, JSON didáticos, gerador Python, resultados processados e trechos da qualificação. Revisão de 22/09/2026. A apresentação não foi alterada.

## Avaliação geral

A estrutura faz sentido: observação do padrão, hipótese inicial, medição, investigação dos mecanismos, síntese e limites. A identidade visual é consistente. A balança, o exemplo territorial de Acreúna e a repetição das quatro perguntas são recursos didáticos valiosos.

O principal ajuste é alinhar a força das frases à força da evidência. O texto escrito costuma ser mais cuidadoso que a apresentação. Em alguns slides, uma associação vira mecanismo, ausência de detecção vira ausência do fenômeno e uma comparação entre modelos vira prova de duas populações reais. A simplificação pode continuar acessível sem esses saltos.

## O que foi efetivamente verificado

- Renderização dos 29 slides em Chromium, em 1920 × 1080, com inspeção dos estados finais e de estados intermediários dos momentos didáticos. Não apareceram cortes externos nos blocos de texto verificados. Isso não equivale a garantir a legibilidade numa sala real.
- Navegação normal com setas, índice, Enter, Home, End e tela preta, em viewport 1366 × 768, sem erros de JavaScript nesse percurso.
- Validação de sintaxe dos três arquivos JavaScript com `node --check`.
- Recálculo das funções `empurrao()`, `idade()` e `motor()` do gerador Python, sem executar a gravação: os três objetos reproduziram exatamente os JSON atuais.
- Coeficiente espacial −0,15721; substituição local −0,51496; Granger p ≈ 0,97071; componentes de idade com médias aproximadas de 3,9 e 16,3 anos, pesos 33% e 67%; correlação aptidão–latitude −0,44280; redução de coeficiente de 62,321%.
- Conferência de resultados selecionados nos CSV e no capítulo de resultados, incluindo bootstrap em blocos e carbono.
- Testes de falha controlada: bloqueio do JSON didático e tecla de aspas no hub.

Não foram refeitos todos os pipelines desde as fontes brutas, auditadas todas as referências bibliográficas ou examinadas todas as combinações de animações e dispositivos. As capturas estáticas não validam, sozinhas, o ritmo da exposição.

## Correções de conteúdo prioritárias

### 1. Vegetação: centro sem deslocamento detectável não é centro imóvel

Slides 11–13 e síntese. O próprio resultado é +7,55 km, com IC que inclui zero. “Ficou onde estava” transforma incerteza numa igualdade exata.

Sugestão: **“Na vegetação natural, o deslocamento estimado é pequeno e o intervalo inclui zero.”** No título: **“Pasto, rebanho e agricultura avançam ao norte; a vegetação não apresenta deslocamento detectável.”**

Separar sempre posição do centro e conservação de área. Um centro aproximadamente estável pode coexistir com grande perda de vegetação. A abertura da apresentação mostra essa perda, mas a distinção merece uma frase junto ao resultado do centro.

### 2. Bootstrap: a animação não simula erro do classificador

Slide 11. “E se o mapa tivesse saído um pouco diferente?” sugere incerteza cartográfica. O código reamostra AMC com reposição, preservando seus valores. Isso não modifica rótulos de pixels nem simula uma matriz de confusão.

Sugestão: **“O resultado depende de quais AMC entram na conta? Repetimos a medida em 2.000 reamostragens.”**

Apresentar a reamostragem individual como introdução didática e acrescentar: **“A conclusão também resiste a blocos espaciais.”** O pipeline 55 já oferece essa defesa: os vereditos meridionais persistem nas seis partições. É uma evidência importante que a apresentação quase não aproveita.

Há uma distinção técnica adicional: o histograma é simulado no navegador com `mulberry(42)`, enquanto a faixa desenhada é importada do resultado oficial. A semente numérica igual não garante as mesmas amostras entre geradores. A etiqueta deveria identificar “IC oficial” ou o gráfico deveria usar sorteios e quantis provenientes da mesma fonte.

### 3. Ausência de empurrão detectado não identifica um motor alternativo

Slides 17, 18 e 26. “Se ninguém empurra” e “mesmo motor” são mais fortes que “o canal local testado não apareceu”. O slide de limites e a discussão já reconhecem essa diferença.

Sugestão para o slide 18: **“Um estímulo comum é compatível com o padrão?”** Para o fecho: **“Padrão compatível com estímulos comuns ao longo do gradiente Sul–Norte.”**

Os 36 resultados são especificações relacionadas, não 36 replicações independentes. A palavra “relacionadas”, já presente no slide de literatura, deve acompanhar o placar. Preservar a informação de poder: aproximadamente 48% para um efeito moderado impede descartar esse efeito só pelo teste temporal.

### 4. O resultado temporal válido precisa aparecer junto à conclusão principal

Slide 16 e reserva R2. O slide principal enfatiza p = 0,97 do Granger simples. A própria reserva explica que a integração das séries exige cuidado e apresenta Toda–Yamamoto. Convém colocar uma indicação curta no slide principal: **“Resultado também examinado por Toda–Yamamoto; detalhes na reserva.”** Melhor ainda, usar o teste adequado como referência inferencial principal e manter as previsões como ilustração.

Na nuvem espacial, acrescentar à fala que os eixos mostram variações após retirar os efeitos de AMC, ano e lavoura local. “Além do habitual” é acessível, mas não esclarece sozinho tudo o que foi controlado. A reta verde deve ser explicitamente ilustrativa: o sinal esperado não determina aquela inclinação numérica.

### 5. Remanescente: mostrar a taxa que sustenta a conclusão

Slide 20. O gráfico mostra o estoque restante por região. A regressão citada mede como a taxa de conversão muda dentro da unidade enquanto ela se esgota. São evidências diferentes.

O texto “quanto menos resta [...] relação negativa” também esconde qual variável cresce: o coeficiente negativo se refere ao esgotamento. Redação mais precisa: **“À medida que uma AMC se esgota, sua taxa de conversão também diminui.”**

Acrescentar uma visualização da taxa ou dos coeficientes, ou restringir o título atual ao que a figura demonstra: **“O Sul preserva menor parcela do estoque inicial de savana e campo.”**

Os 17% são a parcela mecânica da decomposição atribuída ao estoque. Os demais 83% não ficam causalmente explicados por eliminação. Substituir “o resto é lido por eliminação” por **“A parcela restante reúne mudanças de taxa e outros fatores; o desenho não identifica suas contribuições.”**

“Não é a proteção integral” também deve ser moderado: pouca área protegida e pequeno crescimento não constituem, isoladamente, uma identificação do efeito da proteção. “A expansão da proteção integral não acompanha a magnitude da mudança” é mais próximo da evidência mostrada.

### 6. O Sul reduziu a abertura; não a interrompeu

Slide 19: “parou de tirá-la da vegetação natural” contradiz a queda de 49% exibida. Trocar por **“reduziu a abertura de vegetação e ampliou o uso de pastagens já abertas.”**

Câmbio e preço são indicadores de incentivo econômico, não uma medição direta de demanda por terra. “Incentivos econômicos permaneceram elevados” é mais defensável que “não faltou comprador”. Explicitar a base monetária e a deflação do preço da soja e não chamar de “pico” o que o gráfico mostra apenas como média superior à do ato anterior.

### 7. Idade do pasto: modelo descritivo e mecanismos

Slide 15. Um único tipo de processo não precisa produzir uma gaussiana. Portanto, “se fosse de um tipo só, as idades seguiriam a curva tracejada” é forte demais. Dizer **“Uma única distribuição normal não descreve bem a forma observada; duas componentes ajustam melhor.”**

A interpretação dos mecanismos ganha força com a trajetória anterior dos pixels, não apenas com o ajuste. Mesmo assim, 45% com passagem anterior por lavoura não permite chamar todo pasto jovem de rotação. Usar **“compatível com rotação em parte dos casos”**.

Explicitar “eventos de conversão pixel–ano com idade conhecida”. A documentação registra 64,1% de eventos censurados à esquerda, excluídos dessa distribuição. A estatística descreve o subconjunto de idade observável, não todas as conversões históricas. Levar a dimensão da censura para uma reserva metodológica.

### 8. Comparabilidade não elimina erro de medida

Slide 6: “a diferença entre Sul e Norte não vem da medida” não decorre de usar o mesmo classificador. Erros podem variar regionalmente. Sugestão: **“As regiões são comparadas com fontes e critérios comuns; a triangulação avalia a robustez das diferenças.”**

Slide 7: “censo” descreve cobertura de todos os pixels do produto, não ausência de erro de classificação. “Cobertura completa do território” evita confusão. “Fontes independentes do classificador” também é mais preciso que chamar crédito e câmbio de “campo”.

### 9. Carbono e desenvolvimento: denominar o que foi estimado

Slide 21. O CSV distingue 973,27 Mt CO₂ de estoque removido de 832,95 Mt de emissão líquida com desconto do destino. Preservar essa distinção com **“Perda de estoque de carbono da vegetação, expressa em CO₂”**. “CO₂ removido” pode soar como retirada de CO₂ da atmosfera.

O gráfico de área agrícola cobre 2013–2021 e o texto do IFDM compara 2013–2023. Explicar o horizonte adicional ou harmonizar os recortes. Mostrar o próprio IFDM, pois a figura atual mostra área e deixa a evidência de desenvolvimento apenas no parágrafo.

“Não trouxe desenvolvimento adicional”, mesmo seguido de “associação, não causa”, ainda soa causal. Sugestão: **“A expansão da área não veio acompanhada de maior convergência do IFDM entre Norte e Sul.”**

## Estética e didática

Manter fundo claro, paleta, títulos serifados, mapas e consistência das cores dos usos. As barras dos slides 10, 13 e 19 apresentam as comparações com clareza. A balança deve continuar como momento central.

Prioridades de simplificação:

| Slide | Ajuste recomendado |
|---|---|
| 6 | Separar justificativa e objetivos, ou retirar os parágrafos explicativos e manter as quatro perguntas. Há muitas unidades de leitura simultâneas. |
| 9 | Restaurar o contraste das quatro séries no último passo. A classe `f-pico` deixa as séries que não são pastagem com opacidade 0,28 até o final. |
| 11 | Dar tempo para a transição entre mapa, régua e reamostragem. Explicar primeiro o centro, depois a robustez. |
| 15 | Encurtar o texto lateral e revelar a origem anterior dos pixels como evidência separada do ajuste das curvas. |
| 16 | Preservar a estrutura pergunta–expectativa–evidência, um dos melhores recursos da apresentação. Destacar que a nuvem inclui todas as AMC, embora o mapa use Acreúna como exemplo. |
| 17 | Explicar verbalmente o eixo dos p-valores e o significado da área sombreada; para público não econométrico, um placar sozinho é pouco intuitivo. |
| 18 | Reduzir o texto nos três elos. Separar visualmente hipótese teórica e evidência estimada. |
| 20 | Alinhar gráfico, título e variável testada. Dar mais destaque à limitação dos 17%. |
| 21 | Separar carbono e IFDM ou escolher um para a exposição principal. São duas perguntas distintas dentro de uma seção sobre desaceleração. |
| 22 | Uma frase por pergunta; os detalhes dos testes já foram apresentados e podem ficar na reserva. |
| 23 | Resumir a contribuição à literatura em poucas relações; a tabela atual exige leitura extensa durante a fala. |
| 26 | Encerrar com uma frase proporcional à evidência, evitando transformar a hipótese do motor comum em conclusão causal. |

Textos de corpo de 27 px tornam-se cerca de 19 px numa tela de 1366 px; fontes de 18 px tornam-se cerca de 13 px. Rodapés e detalhes dos gráficos não devem carregar informações essenciais à compreensão. Testar no projetor da sala e do fundo da plateia.

Definir Mha na primeira ocorrência, identificar o recorte Sul/Centro/Norte no primeiro mapa analítico e manter a definição de AMC disponível. A idade do pasto é duração consecutiva observada, não necessariamente idade desde a primeira abertura.

O roteiro está desatualizado em relação aos passos: o slide 7 tem três revelações, e vários slides assinalados sem passos têm revelações no HTML. Um ensaio deve contabilizar todas. A sequência é plausível para 30 minutos, mas a estimativa de 23–26 minutos não foi validada por um ensaio oral nesta revisão.

## Código e confiabilidade

### Pontos positivos

- HTML/CSS/JS sem framework ou dependências externas necessárias ao núcleo da apresentação.
- Separação entre navegação, hooks visuais e conteúdo didático.
- Estado recuperável por hash, índice, atalhos numéricos e slides de reserva.
- Gerador Python reutiliza funções analíticas e confere resultados relevantes antes de gravar.
- Escala fixa 16:9 mantém a composição proporcional entre telas.

### Ajustes prioritários

1. **Carregamento de dados:** os helpers fazem `fetch(...).then(r => r.json())` sem testar `r.ok`. A inicialização usa `Promise.all(...).finally(...)` sem `catch`, deixando rejeições não tratadas. Bloquear o JSON didático reproduziu `Failed to fetch`. Validar respostas, identificar o recurso que falhou e oferecer recuperação explícita. Não continuar silenciosamente com gráficos incompletos.
2. **Mapa atrasado:** `desenha(a)` atualiza ano e contadores mesmo quando a imagem de `a` ainda não está carregada, deixando o mapa anterior no canvas. Só sincronizar os três após a imagem correta estar disponível, ou mostrar estado de carregamento. Esse risco decorre diretamente do fluxo do código; não ocorreu no percurso normal em cache local.
3. **Tecla de aspas no hub:** interpolar qualquer caractere em `.hub[data-tecla="..."]` permite seletor inválido. Reproduzido pressionando `"` no slide 27. Filtrar as letras permitidas ou comparar `dataset.tecla` sem montar seletor CSS.
4. **Prontidão do teclado:** proteger navegação enquanto `atual < 0` e a inicialização não terminou. Há caminhos que acessam `slides[atual]` antes de um slide ativo existir. É um risco de leitura do código, não uma falha reproduzida no percurso normal.
5. **Fonte única dos números:** parte dos dados vem de JSON e parte está digitada no HTML/SVG, como os coeficientes do placar e a curva do remanescente. Uma atualização dos pipelines pode deixar o deck parcialmente antigo. Gerar esses trechos a partir dos resultados ou conferir automaticamente seus valores.
6. **Exportação de segurança:** `?estatico` desativa animações, mas não pagina todos os slides nem escolhe seus estados explicativos. Falta uma exportação para PDF que selecione quadros relevantes, especialmente para balança e empurrão. Simplesmente imprimir a página não é uma estratégia confiável.
7. **Tipografia:** Source Serif Pro e Crimson Pro são preferências de fonte, sem carregamento local explícito no CSS. Se a intenção for usar uma delas, empacotar a fonte para obter a mesma composição em outra máquina.
8. **Acessibilidade e manutenção:** melhorar foco nos overlays, estados de slides ocultos e preferência por movimento reduzido. Os comentários descrevem um sumário lateral que o CSS atual esconde; sincronizar documentação e implementação.

## Ordem sugerida de trabalho

1. Corrigir as afirmações categóricas e alinhar o slide 20 à variável efetivamente estimada.
2. Simplificar os slides 6, 18, 22 e 23 e melhorar a relação entre evidência e conclusão no 21.
3. Endurecer carregamento, sincronização de mapas e teclado.
4. Preparar PDF com estados selecionados e reservas sobre bootstrap espacial, censura da idade e Toda–Yamamoto.
5. Ensaiar a apresentação completa, com as revelações, antes de decidir novos cortes.
