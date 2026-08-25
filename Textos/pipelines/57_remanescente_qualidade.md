# Pipeline #57 — O remanescente do Sul é pior, ou só menor?

**Script**: `scripts/remanescente_qualidade.py`
**Quando foi feito**: 2026-08-19. Nasceu durante a redação da qualificação, na primeira leitura do texto inteiro *como banca*.
**Depende de**: #39 (estoque convertível e *hazard* por AMC-ano), #52 (aptidão edafoclimática por AMC), #25 (classes de vegetação no painel AMC).
**Outputs**:
- `data/processed/remanescente_qualidade_aptidao.csv` — aptidão média do estoque, ponderada pelo próprio estoque, por região × ano.
- `data/processed/remanescente_qualidade_composicao.csv` — composição do remanescente em floresta / savânica / campo, por região × ano.
- `outputs/fronteira_fechando/` — figuras.

---

## Pergunta de pesquisa

A Perna 4 sustenta que a freada da conversão no Sul é de **oferta de terra**: restou pouco
Cerrado a suprimir. O argumento se monta por eliminação — a demanda estava no pico, a
proteção integral não estava no caminho, e a demanda de terra do Sul continuou existindo,
atendida por pasto já aberto.

Sobra uma alternativa que a eliminação **não** cobre, e que não é a de Reserva Legal e APP
já declarada. É a de **composição**:

> E se o que restou no Sul não for apenas **menos** Cerrado, e sim Cerrado **pior**?

As duas leituras produzem a mesma série de estoque decrescente e a mesma queda de fluxo,
mas dizem coisas diferentes. "Acabou a terra" é esgotamento de **quantidade**; "o que
sobrou não presta" é seleção de **qualidade** — a conversão comeu primeiro o que era fácil
e barato e parou ao encontrar encosta, solo raso e mata de galeria. A segunda enfraquece a
extrapolação para o Norte, porque lá o remanescente ainda inclui a parte fácil.

## Abordagem

Duas medidas de "pior", ambas com dado já em disco.

**(A) Qualidade *entre* AMCs** — aptidão média do estoque, ponderada pelo próprio estoque:
se a conversão comeu primeiro as AMCs aptas, essa média **cai** ao longo da série, e cai
mais onde a depleção foi maior. Se ficar plana, o canal entre-AMCs está eliminado.

**(B) Composição *dentro* da unidade** — a fração do remanescente que é **formação
florestal**, a fisionomia que a fronteira historicamente não converte (mata de galeria,
cerradão, tipicamente em APP).

## Achados

**(A) Entre AMCs, o canal não aparece — e no Sul ele aparece ao contrário.**

| Região | aptidão ponderada 1985 | 2024 |
|---|---|---|
| Goiás | 4,094 | 4,007 |
| **Sul** | **4,603** | **4,613** |
| Centro | 3,977 | 3,934 |
| Norte | 3,943 | 3,821 |

No estado a queda é de menos de 0,09 ponto em quarenta anos, e **no Sul — a região da
freada — a aptidão ponderada do estoque não cai: sobe de leve**. Se o mecanismo fosse
"comeram-se as AMCs boas", o Sul seria o caso-modelo, e não é.

**(B) Dentro da unidade, o quadro é outro.** A fração florestal do remanescente sobe em
todas as regiões, e **sobe mais no Sul**:

| Região | % floresta 1985 | 2024 |
|---|---|---|
| Goiás | 37,0 | 42,5 |
| **Sul** | **52,2** | **59,9** |
| Centro | 33,1 | 38,7 |
| Norte | 29,6 | 34,3 |

**O remanescente do Sul é hoje, em três quintos, a fisionomia que a fronteira não
converte.**

## Ressalva de medida

O β do *hazard* contra a fração florestal foi **corrigido no mesmo dia em que foi obtido**.
A primeira estimativa (+0,011) estava inflada: *hazard* é uma razão, **690 pares têm
estoque abaixo de 100 ha**, e os extremos são AMCs do Sul com menos de 1 ha, onde
*hazard* = 1,00 por construção. Numa grade de cortes, **o sinal sobrevive nas três regiões
e em todos os cortes; a magnitude não**. O número citável é o do corte defensável:
**+0,004 (estoque ≥ 1.000 ha; p < 0,01)**.

## Veredito

**Misto, e é isso que o torna útil.** O canal *entre* AMCs — "a conversão comeu as unidades
aptas" — está **eliminado**: a aptidão ponderada do estoque não cai onde a freada
aconteceu. O canal *dentro* da unidade **existe e é mensurável**: o que sobrou no Sul é
majoritariamente floresta, e floresta é o que a fronteira historicamente não converte.

Para a Perna 4, isso **reforça** o teto sem trocar o mecanismo: o Sul tem menos Cerrado
convertível *e* o pouco que tem é da fisionomia mais difícil. Casa com o **#39B/D29** —
onde a região se esgota, caem as duas coisas, o estoque e a taxa —, e dá nome a parte do
resíduo que o #39 deixava sem explicação.
