# Pipeline #56 — A corrida de exposições: a aptidão sobrevive ao gradiente? (**D28**)

**Script**: `scripts/drive_horse_race_latitude.py`
**Quando foi feito**: 2026-08-19. Nasceu durante a redação da qualificação, na primeira leitura do texto inteiro *como banca*.
**Depende de**: #38 (o desenho *shift-share* do drive comum), #52 (a aptidão edafoclimática da Embrapa como exposição), #54 (a inferência por permutação do *shifter*), #39 (latitude por AMC), #32 (núcleo de lavoura de 1985), #25 (centroides).
**Outputs**:
- `data/processed/drive_horse_race_latitude.csv` — seis especificações × exposição: β, SE, p agrupado, p de permutação circular, R² *within*.
- `outputs/drive_comum/` — o gráfico de coeficientes que virou a Figura 8 da qualificação.

---

## Pergunta de pesquisa

O drive comum (#38/#52/#54) estima `Δy_it = α_i + γ_t + β·(Δcâmbio_t × exposição_i)`.
Com efeito fixo de ano, o **nível** do choque some, e o que resta identificado é o
**gradiente**: onde o mesmo choque nacional bate mais forte. A exposição escolhida é a
aptidão edafoclimática, defendida por ser física e **exógena** ao uso da terra.

Exógena, porém, não é o mesmo que **isolada**. A aptidão correlaciona-se **−0,44** com a
latitude, e a latitude organiza quase tudo em Goiás: infraestrutura, idade da ocupação,
distância aos mercados, especialização produtiva, preço da terra. Se o câmbio interage com
*qualquer* gradiente Sul→Norte, o coeficiente da aptidão acende sem que a aptidão seja o
mecanismo.

Os placebos já rodados no #54 são todos de **desfecho** — urbano, água. Eles mostram que o
efeito é específico do rebanho; **nenhum pergunta se a exposição escolhida é a certa**. É
a lacuna que este pipeline fecha, e é a régua que a **D14** manda aplicar em todo recorte
transversal — que esta frente ainda não tinha recebido.

## Desenho

Três exposições concorrentes, todas em z-score sobre as 166 AMCs:

1. `exp_apt_edafo` — a aptidão física da Embrapa (a do #52, a defendida);
2. `exp_latitude` — a latitude do centroide da AMC, o **confundidor puro**;
3. `exp_acesso` — distância ao núcleo de lavoura de 1985, um gradiente de acesso.

Seis especificações: cada exposição sozinha (S1–S3), aptidão + latitude (S4), aptidão +
acesso (S5) e as três juntas (S6). Todas com efeito fixo de unidade e de ano, erro-padrão
agrupado por entidade e ano, e o p de **permutação circular do *shifter*** ao lado — a
régua que o #54 estabeleceu como a correta para este desenho.

## Achados

| Spec | Exposição | β | p agrupado | p circular |
|---|---|---|---|---|
| **S1** | aptidão sozinha | **−0,0325** | **0,026** | 0,132 |
| **S2** | latitude sozinha | **+0,0512** | **0,015** | **0,026** |
| S3 | acesso sozinho | +0,0284 | 0,118 | 0,184 |
| **S4** | aptidão \| + latitude | **−0,0123** | **0,302** | **0,474** |
| **S4** | latitude \| + aptidão | **+0,0458** | **0,028** | 0,053 |

**Posta a latitude na mesma regressão, a aptidão perde 62% da magnitude** (−0,033 →
−0,012) **e a significância nas duas réguas** (p agrupado 0,026 → 0,30; p circular 0,13 →
0,47), enquanto a **latitude quase não se move** (+0,051 → +0,046). O VIF de S4 é **1,24**:
a corrida é limpa, e não um empate de colinearidade. E `exp_latitude` **não** é a
`exp_fronteira` do #38 renomeada (r = 0,58).

⚠️ **O `p = 0,026` da latitude é o piso do teste.** Com 38 realizações do *shifter*, 1/38 é
o menor p que a permutação pode devolver: ele significa "nenhuma das 37 rotações superou o
observado" — o melhor desfecho possível, e **não** margem folgada. O 0,053 de S4 é decidido
por **uma única** rotação. A D28 não depende disso: ela se apoia na aptidão **perder**
significância, não na latitude ganhá-la.

## Veredito — **D28**

**O gradiente medido é o do eixo Sul→Norte, e a aptidão é a régua com que ele foi medido,
não o canal identificado.**

O que **sobrevive intacto** é o argumento da Perna 3: a reorganização é coordenada por uma
força comum, e não por um empurrão de uma região sobre a outra. O que **cai** é a
atribuição a solo e clima — o eixo carrega, junto com a aptidão, tudo o que varia nessa
direção.

Consequência de redação: a frase-tese passa de "sobre um **gradiente de aptidão**" para
"ao longo do **gradiente Sul→Norte**". A **pendência** que a decisão abre está no
cronograma: encontrar uma exposição que **não** se ordene com a latitude, sem a qual o
gradiente permanece medido e não nomeado.
