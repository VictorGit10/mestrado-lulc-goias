# Três ideias difíceis, passo a passo

Abra `index.html` no navegador. Ele tem três abas, uma por conceito. Cada aba tem três passos curtos; use **Próximo passo →**. Os três HTMLs individuais também abrem diretamente e não precisam de internet:

- `motor-comum.html`
- `granger-toda-yamamoto.html`
- `estoque-taxa.html`

Se preferir um percurso, comece por **Estoque × taxa**: a conta de 100 ha e 10% estabelece a diferença entre estoque, taxa e fluxo. Depois veja **Motor comum**, que segue o mesmo sinal cambial através de três AMCs. Por fim, **Granger**, que compara previsões com duas quantidades de informação e mostra as defasagens adicionais de Toda–Yamamoto.

Cada conceito começa pela intuição e termina nos dados da pesquisa. Contas inventadas são marcadas como ilustração. Os dados reais vêm dos arquivos locais do projeto. Os detalhes da estimação e os limites estão em uma seção expansível depois dos três passos. A versão anterior, mais carregada de informações, foi preservada em `versao-detalhada.html` apenas como referência.

Após uma conversa de estudo, foram acrescentadas quatro respostas didáticas no próprio HTML. Em **Motor comum**: por que a latitude enfraquece a interpretação da aptidão; por que o resultado do rebanho não determina qual transição de uso da terra ocorreu; e o que a defasagem de um ano testa e deixa em aberto. Em **Estoque × taxa**: a conta, em quatro passos, das parcelas de 17% e 83% da queda do fluxo anual no Sul. Essas respostas ficam fechadas até o leitor abrir a pergunta, preservando o percurso simples das três etapas.

## Fontes e cuidados

- Motor: índice cambial anual real, aptidão de 166 AMCs e coeficientes do painel. O gráfico final mostra apenas a parcela estimada da interação. Ela não é a mudança observada do rebanho nem demonstra causa. A diferença entre p agrupado (0,026) e p de permutação circular (0,132), assim como a sensibilidade à latitude, é mantida no texto.
- Granger: ajustes de duas equações em níveis feitos com séries regionais do projeto. Os ajustes são dentro da amostra. Para p=1 e dmax=2, são estimadas três defasagens de cada série, mas só o primeiro coeficiente da origem é testado. Os quatro resultados Toda–Yamamoto foram reproduzidos com OLS, HAC e `f_test`, como no pipeline original; p = 0,2521 e 0,2461 em Sul→Norte, 0,4549 e 0,7483 em Norte→Sul.
- Estoque: o exemplo 100 ha × 10% = 10 ha é inventado e identificado assim. Nos dados reais, estoque é savana + campo. O fluxo soma perdas positivas de estoque por AMC; não é a perda líquida regional. As parcelas de 17%/83% no Sul são uma decomposição simétrica do produto estoque × taxa, não uma identificação causal da demanda.

## Atualizar os arquivos

Edite `modelo.html`, `estilo.css` ou `laboratorio.js` e rode a partir da raiz do projeto:

```powershell
python Visualizacao/laboratorio_metodos/gerar.py
node --check Visualizacao/laboratorio_metodos/laboratorio.js
python Visualizacao/laboratorio_metodos/verificar.py
```

O gerador lê os dados existentes e escreve apenas nesta pasta. A geração usa numpy, pandas e statsmodels. A verificação usa Playwright e Chromium. Os HTMLs finais não carregam bibliotecas externas. As capturas das nove etapas e o resultado da verificação estão em `qa/`.
