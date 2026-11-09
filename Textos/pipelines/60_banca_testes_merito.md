# Pipeline #60 — Testes de mérito pedidos pela banca de qualificação

**Script:** `scripts/banca_testes_merito.py` · **Rodado em:** 05–07/out/2026 ·
**Saídas:** `data/processed/banca60_*.csv`, `outputs/banca60/log_B*.txt`

## Por quê

A banca de qualificação (Adriana Ferreira Silva e Luis Rodrigo F. Baumann) e a revisão cruzada
Claude × Codex (`Textos/banca_qualificacao/comparacao_revisoes.md`) levantaram pontos que não se
resolvem reescrevendo: a ordem de integração das séries regionais, a implementação do
Toda-Yamamoto, o poder do teste temporal, a calibração do sup-F, a justificativa da primeira
diferença no painel, a escolha de efeitos fixos e a leitura da mistura de gaussianas. Este pipeline
roda esses testes **sem alterar** os pipelines de origem (#29, #34, #42, #28C, #49), que continuam
descrevendo o que está no texto da qualificação.

## Histórico de correções (registro do resultado superado)

A primeira versão (05/out) foi conferida pelo Codex (`Textos/banca_qualificacao/conferencia_testes_codex.md`),
que reproduziu os números de forma independente e achou quatro erros de código. Todos procediam:

| Bloco | Erro | O que se publicaria sem a conferência |
|---|---|---|
| B1 | Lee-Strazicich começava a regressão uma observação tarde (k + 1 em vez de k), podendo zerar uma dummy de impulso | LS-A da agricultura do Sul τ = −2,23; correto: −3,39 |
| B2 | Dummies de quebra deslocadas um ano | datas de quebra erradas nas especificações com dummies (não mudou a conclusão) |
| B6 | `f_pooled` testava unidade **e** ano juntos | "efeitos de unidade significativos nas três"; no rebanho o F correto é 1,07, p = 0,27 |
| B7 | Normal truncada parou em ótimo local | log-lik −2,9689; melhor: −2,9627 |

Ao corrigir o B7 apareceu um quinto erro, achado depois da conferência: um piso numérico de −700
fazia o numerador e o denominador da verossimilhança caírem juntos quando a massa ia para fora da
janela, e a razão virava 0, um ajuste "perfeito" falso que o otimizador explorava (a normal
assimétrica chegou a log-verossimilhança 0). O piso foi removido; valores não finitos são
penalizados.

A segunda conferência do Codex (`Textos/banca_qualificacao/conferencia_testes_codex_2.md`)
confirmou as correções e reproduziu os números novos, e apontou mais dois pontos de código: (i) no
LS modelo C, 29 regressões candidatas tinham deficiência de posto (ex.: TB1 = 4 com k = 3 torna ΔDT1
igual à constante) e eram aceitas pela pseudoinversa; agora são descartadas; (ii) a rotina de ajuste
do B7 ainda podia aceitar um ajuste penalizado ou não convergido; agora os exclui. Com a correção do
posto, B1 e B2 foram rodados de novo e **nenhum número mudou**: as candidatas deficientes nunca eram o
mínimo, nem nos dados nem nos passeios simulados.

## Resultados (versão corrigida)

### B1 — Raiz unitária com quebra (séries regionais, T = 40)

Valores críticos de amostra finita por simulação do mesmo procedimento (500 passeios aleatórios).

| Série | ADF c | ADF ct | Zivot-Andrews c / ct | Lee-Strazicich A / C |
|---|---|---|---|---|
| agric_Sul, nível | p = 0,006 | p = 0,477 | não rejeita / não | τ −3,39 (cv5 −4,87) não / não |
| pasto_Norte, nível | p = 0,870 | p = 0,992 | não / não | não / não |
| Δagric_Sul | p = 0,001 | p < 0,001 | **rejeita** (1991) / **rejeita** (1999) | não / não |
| Δpasto_Norte | p = 0,738 | **p = 0,032** | não (τ −4,74, cv5 −5,15; quebra 2009) / não | τ −4,53 (cv5 −4,78) não / não |

**Leitura.** A ordem da pastagem do Norte **não está resolvida**: o ADF com tendência rejeita a raiz
da Δpastagem, os testes com quebra não, e ficam perto do limiar (ZA em 2009, LS-A). I(2) não está
demonstrado, e I(1) com quebra também não. Com T = 39 esses testes têm pouco poder (o LS não rejeita
nem a Δagricultura do Sul, que os outros dão como estacionária). Ressalvas: o ZA é a variante do
statsmodels (defasagem escolhida uma vez, antes da busca da quebra); para o LS-C, o valor crítico por
passeio sem quebra é aproximação.

### B2 — Toda-Yamamoto refeito

Wald χ² com covariância OLS (forma original), χ² com HAC de largura fixa 3 e p por bootstrap sob a
nula (1.999 réplicas). AIC = BIC = HQ escolhem p = 2 no VAR em nível.

- **Sul→Norte:** nenhuma das 8 combinações (p ∈ {1, 2} × d_max ∈ {1, 2} × com/sem dummies nas
  quebras do LS) rejeita a 5%.
- **Reverso Norte→Sul:** idem; p bootstrap de 0,28 a 0,83.
- **n efetivo:** T-Y usa 40 − (p + d_max) observações (37 e 36 com d_max = 2). A coluna n da tabela
  de precedência do Apêndice A traz o n do Granger em Δ (38/37).

**Leitura.** O sinal clássico do reverso **não é robusto**: some com d_max 1 ou 2, com e sem
dummies, no χ² e no bootstrap. Isso sustenta "não detectamos precedência nessas especificações",
não "a relação é espúria" nem "não há líder". O bootstrap é uma variante (gera do VAR aumentado
restrito, sem o ajuste de alavancagem de Hacker e Hatemi-J) e mantém fixas as datas de quebra
estimadas. Faltam diagnósticos das inovações reamostradas e a avaliação do tamanho dessa variante.

### B3 — Poder do procedimento usado

DGP I(1) calibrado (Δagric_Sul AR(1) ρ = 0,39; Δpasto_Norte AR(1) com φ = 0,95 estimado e com
φ = 0,5), 50 observações de aquecimento, 2.000 réplicas. Em nível o DGP tem ordem básica 2. r é o
coeficiente padronizado do efeito (não exatamente a correlação parcial). "Aj." = poder ajustado ao
tamanho (quantil 5% da nula simulada).

| r | Granger em Δ | T-Y p1 d2 | T-Y p2 d2 (o especificado nos dados) | T-Y p2 d2 HAC |
|---|---|---|---|---|
| 0 (tamanho) | 6% | 7% | 9% | **18%** |
| 0,3 | 45% (aj. 43%) | 39% (aj. 33%) | 35% (aj. **26%**) | 47% |
| 0,5 | 90% (aj. 89%) | 82% (aj. 77%) | 75% (aj. **66–68%**) | 82% |

(φ = 0,95; com φ = 0,5 os números ficam a 1–3 pontos.)

**Leitura.** Os 93%/48% do texto valem para o Granger em Δ, não para o procedimento que sustenta a
conclusão. **Neste DGP I(1), o T-Y com p = 2 e d_max = 2, após ajuste ao tamanho, detecta r = 0,3
em cerca de 26% e r = 0,5 em 66–68% das simulações.** O poder do bootstrap empírico usado no B2
permanece sem avaliação. A frase "descarta um empurrão forte" **não se sustenta**; o nulo Sul→Norte
vale como ausência de evidência preditiva com poder limitado. O HAC desta implementação teve tamanho
de ≈ 18% nestes DGPs (os poderes HAC da tabela são nominais; ajustados ao tamanho, com φ ≈ 0,95, caem
para 22% e 57%). Limites: o DGP não inclui I(2), tendência ou quebras.

### B4 — sup-F calibrado

2.000 réplicas, aquecimento de 200. Nulas: (a) **global** — VAR(1) da série inteira sem quebra
(raio espectral 0,97; pode absorver quebras reais na persistência); (b) **sensibilidade** — VAR(1)
dos resíduos por segmento (0,65; usa as próprias fronteiras e tende a favorecer rejeição);
(c) **condicional** — VAR(1) no próprio segmento da quebra.

| Fronteira | F | (a) global | (b) por segmento | (c) condicional |
|---|---|---|---|---|
| 2001 | 62,2 | **0,020** | 0,0005 | — |
| 2020 | 21,5 | 0,120 | 0,0085 | VAR irrestrito do segmento explosivo (1,06): sem p |
| 1991 (não adotada) | 10,3 | 0,202 | 0,083 | 0,0495 |

Falso positivo da segmentação binária com F ≥ 4: **97%** (nula a) e **74%** (nula b) das séries sem
quebra recebem ao menos uma; o #29 registrava 11% sob ruído branco.

**Leitura.** **2001 rejeita** nas duas calibrações. **2020 não rejeita na referência global**,
rejeita na sensibilidade segmentada e fica sem resultado condicional válido: o VAR irrestrito ajustado
ao segmento é explosivo, e não se produziu p sob a calibração estacionária proposta (isso não confirma
nem descarta a quebra, nem mostra que outra especificação condicional seja impossível). 2020 fica como
**fronteira candidata, sensível ao modelo de erros**. A quebra da soja na PAM em 2020 corrobora por
outra fonte de medição, mas o p dela (F = 7,83, p = 0,008) também é de data fixa depois de maximizar
sobre as datas, e não funciona como confirmação calibrada. O p condicional de 1991 (0,0495) é
limítrofe e não incorpora a seleção sequencial. O limiar **F ≥ 4 não controla erro** sob autocorrelação e não deve ser
apresentado como filtro. Limites: simula-se o comprimento do segmento, não toda a seleção
sequencial; a estatística soma SSR das três classes (não é um Wald ponderado pela covariância).

### B5 — CIPS no painel de 166 AMCs

Valores críticos simulados (300 réplicas, passeios independentes; o Codex conferiu com fator comum,
cargas heterogêneas e autocorrelação moderada: cv5 de −2,55 a −2,58 em nível e −2,04 a −2,09 em Δ).

- **Em Δ:** as cinco variáveis (pastagem, agricultura, Mosaico, vegetação natural, bovinos) rejeitam
  a raiz com folga, com 0 e 1 defasagem (CIPS de −3,1 a −6,7 contra cv5 ≈ −2,1).
- **Em nível:** misto e sensível à defasagem (pastagem não rejeita com p = 0 e rejeita com p = 1;
  agricultura não rejeita; vegetação natural rejeita).

**Leitura.** O CIPS rejeita a raiz unitária nas primeiras diferenças das cinco variáveis, sem
estabelecer a ordem de integração de cada AMC (não exclui unidades I(2) num painel heterogêneo). Isso
responde à pergunta do Baumann (B9.2) no plano do painel. A primeira diferença é adequada para estudar mudanças anuais nesses modelos; o CIPS **não** mostra que
toda variável exija diferença, nem trata cointegração ou quebras. A nula é raiz em todas as unidades;
rejeitar não diz quais são estacionárias.

### B6 — Efeitos fixos no modelo em Δ

Três especificações representativas (não as 140 do painel), erros agrupados por AMC. F aninhado
(homocedástico) dos efeitos de unidade mantendo os de ano.

| Especificação | β (unidade + ano) | β (só ano) | F unidade dado ano | Mundlak p |
|---|---|---|---|---|
| Δpastagem ~ Δagricultura | −0,540 (0,079) | −0,538 | 15,3 (p < 0,001) | 0,987 |
| Δveg. natural ~ Δpastagem | −0,438 (0,049) | −0,454 | 41,3 (p < 0,001) | 0,698 |
| Δbovinos ~ Δpastagem | +0,285 (0,073) | +0,631 | **1,07 (p = 0,27)** | **< 0,001** |

**Leitura.** Nas duas primeiras, os efeitos de unidade (tendências próprias de cada AMC em nível) são
significativos pelo F, o coeficiente fica estável entre o modelo com unidade + ano e o modelo só com
ano, e o Mundlak não rejeita a restrição de efeitos aleatórios. Na do rebanho, o F não rejeita, mas o
Mundlak rejeita a restrição de RE naquela equação e o coeficiente cai pela metade com os efeitos de
unidade. O que os testes mostram é **estabilidade do coeficiente** nas duas primeiras e **sensibilidade**
na do rebanho; não demonstram a consistência do estimador FE, nem que FE seja a única especificação
admissível no rebanho, nem comparam diretamente FE com RE (a tabela compara FE com o modelo só-ano).
O F é convencional e homocedástico. Não rejeitar o Mundlak não prova exogeneidade; agrupar por AMC não
trata dependência entre AMCs; e efeito de unidade em Δ absorve diferenças persistentes no
**crescimento**, não a "heterogeneidade fixa em nível" que o texto descreve.

### B7 — Mistura × distribuição única, com truncamento

A idade observável numa conversão do ano Y vai até Y − 1986; o #28C ajustou a mistura sem esse
limite. Todas as soluções: 15/15 partidas convergiram, nenhuma célula não finita.

| Modelo (com truncamento) | log-lik por evento | distância de variação total |
|---|---|---|
| **Mistura de 2 normais** | **−2,9284** | **0,078** |
| Lognormal | −2,9583 | 0,130 |
| Gama / Weibull | −2,9614 | 0,124 |
| Normal assimétrica | −2,9626 | 0,115 |
| Normal | −2,9626 (μ no limite de 500: densidade quase linear na janela; coincide com o ótimo achado pelo Codex) | 0,114 |

Sem truncamento, a mistura reproduz aproximadamente o texto (μ1 = 3,6, σ1 = 1,4; μ2 = 13,7,
σ2 = 9,2). BIC em subamostras (30 réplicas): a mistura vence em **73%** com n = 500 (lognormal 27%)
e em **30 de 30** com n = 2.000 e com n = 10.000. A distância de variação do modelo sem truncamento
omite a massa prevista fora das células observadas antes de renormalizar, e por isso subestima a
discrepância desse modelo.

Peso da componente jovem (μ1 = 3,6, σ1 = 1,3), em três medidas diferentes:

| Medida | Valor |
|---|---|
| Peso latente (antes do corte da janela) | 5,6% |
| Peso médio dentro da janela de cada ano = fração dos eventos atribuída a ela | 21,0% |
| Parcela empírica de idades ≤ 6 anos | 35,8% |

**Leitura.** **Um pico jovem e concentrado é estável nos ajustes paramétricos examinados**: a
mistura supera todas as distribuições únicas testadas, com e sem truncamento, e vence o BIC em todas as
reamostragens com n ≥ 2.000. Isso não demonstra robustez a coortes, à seleção dos eventos ou à
dependência entre pixels. O que **não** se
sustenta: (i) a divisão 33%/67% como propriedade das pastagens, porque o peso depende da medida (5,6%,
21% ou 35,8%); (ii) a afirmação de **duas populações econômicas**, que a mistura não identifica.
Ressalvas: truncamento não substitui um modelo de coortes e conversão (a idade dos eventos depende de
quantas pastagens nasceram em cada coorte e da chance de conversão); as distribuições únicas
truncadas encostam em limites, com parâmetros sem interpretação fora da janela; as subamostras são
sorteios independentes, não tratam a dependência entre pixels.

### B8 — Direção da matriz W do SLX

`deslocamento_espacial.py` põe em W_sul só os vizinhos ao sul de i, e a regressão é
Δpasto_i ~ Δagric_i + (W_sul·Δagric)_i. **O código está certo**; a frase de
`qualificacao/cap/07_apendice.tex:193` está invertida. Isso confirma a direção do regressor
espacial, não um mecanismo causal.

## O que muda no texto

1. **D16:** "o sinal do reverso não é robusto a d_max, a dummies de quebra nem ao bootstrap", em vez
   de "artefato espúrio"; tirar "sem líder".
2. **Ordem de integração:** declarar a pastagem do Norte como indeterminada entre I(1) e I(2).
3. **Poder:** substituir 93%/48% por ≈ 2/3 (forte) e ≈ 1/4 (moderado) para o T-Y especificado;
   retirar "descarta um empurrão forte".
4. **Periodização:** 2001 com p calibrado; 2020 como candidata sustentada pela convergência com a
   PAM; tirar a taxa de 11% e o papel do F ≥ 4 como controle de erro.
5. **D7 e efeitos fixos:** citar o CIPS; registrar o F aninhado e o Mundlak; corrigir a descrição do
   que o efeito de unidade absorve em Δ.
6. **Mistura:** apresentar como descrição da forma (pico jovem robusto), separar as três medidas de
   peso e retirar "duas populações".
7. Corrigir a frase do SLX (`07_apendice.tex:193`) e a coluna n do Apêndice A.

## Limites gerais

- Simulações com DGPs simples; nenhuma inclui I(2), quebras e dependência espacial ao mesmo tempo.
- O B6 cobre três especificações representativas, não a bateria completa do painel.
- Segunda conferência do Codex, sobre as correções: ver
  `Textos/banca_qualificacao/conferencia_testes_codex_2.md`.
