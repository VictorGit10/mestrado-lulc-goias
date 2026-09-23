# Caderno de preparação para a qualificação

`caderno.pdf` — 111 páginas. Companhia do texto de qualificação (`../main.pdf`),
escrito para a **arguição**, e não para a leitura corrida: destrincha a
matemática que o documento resume, ordena os números que ele espalha e ensaia
as perguntas que ele convida.

Não entra na entrega à banca. É material de estudo do autor.

## Estrutura

```
caderno.tex      — arquivo mestre (só os \input, na ordem)
preambulo.tex    — classe, pacotes, paleta, títulos, as quatro caixas
p0_abertura.tex  — capa, como usar, sumário
p1_argumento.tex — Parte I:   a tese em três tamanhos; os nulos; o mapa do documento
p2_alicerces.tex — Parte II:  o dado, as unidades, o painel, as convenções geodésicas
p3a_matematica.tex   — Parte III (1ª metade): centro de massa, bootstrap, quebras,
                       matrizes de transição, mistura de gaussianas
p3b_econometria.tex  — Parte III (2ª metade): painel 2FE, erros-padrão, integração,
                       Granger/Toda-Yamamoto, espacial, shift-share, teto de oferta,
                       multiplicidade, carbono
p4_resultados.tex— Parte IV:  os três atos e as quatro frentes, com os números
p5_alcance.tex   — Parte V:   graus de estabelecimento, as sete autocorreções,
                              frases proibidas e as substitutas
p6_banca.tex     — Parte VI:  50 perguntas com resposta + as três que podem doer
p7_apresentacao.tex  — Parte VII: roteiro de 20 minutos e cartão de bolso
```

## Compilar

```powershell
pdflatex caderno.tex   # duas passadas: a segunda é o sumário
pdflatex caderno.tex
```

Não usa bibtex nem figuras: é autocontido e compila em uma passada além do
sumário. Os mesmos binários do MiKTeX que `../compilar.ps1` usa.

## Convenções internas

Quatro caixas, definidas no preâmbulo, com um trabalho cada:

| Caixa | Comando | O que carrega |
|---|---|---|
| O que o método NÃO diz | `\begin{naodiz}` | a fronteira do instrumento |
| Como dizer isto na banca | `\begin{nabanca}` | a formulação pronta, no registro em que deve ser dita |
| Números-âncora | `\begin{ancora}` | os valores que valem memorizar |
| Armadilha | `\begin{armadilha}` | o excesso de afirmação que a pergunta convida a cometer |

Todas aceitam título próprio entre colchetes. Todas são `breakable`, e o
`\Needspace` do preâmbulo impede a viúva de título — o cabeçalho colorido no pé
de uma página e o corpo na seguinte, que num caderno de consulta é o defeito
que mais custa, porque se procura pelo rótulo.

`\onde{§4.2}` marca a seção do documento de qualificação em que aquilo está
escrito, para poder ir à fonte durante a defesa.

## Duas notas de manutenção

**Todo número daqui veio do `../cap/*.tex`, e não de recálculo.** O caderno é
uma releitura do documento, não uma fonte nova. Se um número mudar lá, ele está
errado aqui — e o cartão de bolso da Parte VII é onde a checagem é mais barata,
porque concentra os que precisam sair sem consulta.

**As tabelas longas são `longtable`, e não `tabular`.** Um `tabular` que não
cabe na página é empurrado inteiro para a seguinte, deixando atrás de si uma
página em branco sob o título do capítulo. Aconteceu com a tabela das frases
proibidas; as outras três (o mapa do documento, os graus de estabelecimento e o
roteiro de apresentação) foram convertidas por precaução, porque estão perto do
limite. Se alguma ganhar linhas, conferir se ainda quebra bem.
