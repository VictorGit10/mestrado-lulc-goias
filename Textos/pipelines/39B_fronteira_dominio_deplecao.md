# Pipeline #39B — O nulo do B2b era artefato de domínio (**D29**)

**Script**: `scripts/fronteira_fechando_39b.py`
**Quando foi feito**: 2026-08-19, **ao auditar a própria auditoria** — a conferência do que a leitura crítica do texto havia mudado no mesmo dia. Régua de erro-padrão corrigida em 20/ago.
**Depende de**: #39 (`fronteira_fechando.py`) — consome `fronteira_estoque_convertivel.csv` e `fronteira_teste_supply.csv`, que traz os números publicados.
**Outputs**:
- `data/processed/fronteira_teste_supply_39b.csv` — a grade fatorial inteira: β em z, β em unidade natural, p sob duas réguas de agrupamento, R² *within*, n.

---

## O que este pipeline corrige

O #39 monta o bloco de testes de oferta da Perna 4. Uma das especificações é

```
B2b   hazard ~ depleção_defasada        (2FE, ambos em z-score)
```

e a hipótese **pré-declarada no próprio #39** é explícita: *β < 0 significa que o hazard
cai com a depleção, isto é, o remanescente é difícil de converter — atrito de oferta*.

O resultado publicado é **β = −0,0152 com p = 0,4809: nulo**. E era esse nulo que a redação
usava como a peça empírica do argumento de oferta.

**O nulo não sobrevive.** `deplecao_prev` está documentada no #39 como uma fração **0..1**,
e no arquivo ela vai de **−84,9** a 0,97: **920 dos 6.379 pares AMC-ano (14,4%) são
negativos**, vindos de **46 AMCs** cujo estoque convertível de 1985 era minúsculo (mediana
de **544 ha** contra 24.031 ha das demais). Nelas o estoque de savana e campo *cresceu* ao
longo da série — a oscilação classificatória pasto↔savana já documentada no projeto —, e a
razão que define a depleção explode. Como a variável entra **z-scorada**, esses poucos
valores dominam a escala inteira e achatam o coeficiente contra zero.

## O que ele faz

Uma **grade fatorial**, para que o resultado não dependa de uma escolha:

- **4 tratamentos** da variável: publicado (sem tratamento), piso em 0 (não descarta linha
  alguma), domínio documentado [0,1], e *winsor* p1 (que **não** põe no domínio);
- **com e sem ponderação** pelo tamanho do estoque;
- **2 amostras**: todas as AMCs, e o corte de estoque ≥ 1.000 ha.

São **16 células**, todas sob a **régua de erro-padrão do próprio #39** (agrupamento por
entidade **e** por ano). A régua não se troca no meio de uma conferência — foi exatamente
esse o defeito que a revisão de 20/ago encontrou nesta ficha e corrigiu.

## Achados

**β é negativo nas 16 células**, e cruza 5% em **11** delas. A única célula que não cruza
em nenhuma das duas amostras é a **publicada**, que não trata nem o regressor (domínio) nem
o desfecho (denominador minúsculo).

Onde o regressor entra no domínio, os tratamentos **convergem em unidade natural**:

> ≈ **0,5 a 0,8 ponto percentual de taxa anual a menos a cada 0,1 de depleção**,
> com R² *within* saindo de ~0 para 0,05–0,20.

⚠️ **Os β em z não são comparáveis entre tratamentos.** O desvio-padrão do regressor varia
**17×** entre o tratamento de domínio (0,21) e o sem tratamento (3,54) — a faixa
"−0,07 a −0,31" que circulou até 20/ago comparava réguas de tamanhos diferentes. A
concordância se afere em **unidade natural**, e é isso que a tabela reporta.

**O que não muda**: o **B1** segue sendo identidade (`fluxo ≡ taxa × estoque`; β = +2,76
com R² *within* = 0,43 é a definição se reapresentando) e o termo **quadrático** segue nulo
(p = 0,92) — não há saturação abrupta.

**O que muda para menos**: o **B2a** (*hazard* ~ estoque) **não** cruzava 5% na versão
publicada — β = −0,3194 com **p = 0,0917**, e não 0,002; este último vinha da régua frouxa
(agrupamento só por entidade) e foi atribuído por engano ao pipeline de origem. Sob o corte
de 1.000 ha o efeito some (β = −0,057; p = 0,74), porque era carregado pelas AMCs de
estoque minúsculo. **O bloco de oferta tem um resultado contra *hazard* constante, não
dois.**

## Veredito — **D29**

**Variável fora do domínio declarado não entra padronizada.** A decisão fixa três regras:

1. toda variável com domínio declarado é **conferida contra ele** antes de entrar
   padronizada — um z-score não é robusto a nada, e um valor 80× fora de escala redefine a
   unidade de medida da coluna inteira;
2. o resultado reportado é o que **concorda entre tratamentos**, não o de um deles — e a
   concordância se afere em unidade natural;
3. **a conferência herda a régua de inferência do teste conferido**, sob pena de produzir
   uma robustez que é da régua, e não do dado.

**A Perna 4 sai fortalecida.** Onde havia uma premissa apoiada num nulo fraco, há agora
mecanismo medido: quando uma região se esgota, **caem as duas coisas** — o estoque e a
taxa —, porque o que sobra é mais difícil de converter. Casa com o [#57](57_remanescente_qualidade.md)
(no Sul, a fração florestal do remanescente sobe de 52,2% para 59,9%) e resolve a tensão do
"resíduo não é demanda": parte do resíduo do #39 passa a ter nome.

Resolve também uma **contradição interna** do texto de qualificação, em que o capítulo 5 já
dizia "taxa de conversão cadente" enquanto o capítulo 4 dizia "a taxa não cai" — decidida a
favor do capítulo 5.
