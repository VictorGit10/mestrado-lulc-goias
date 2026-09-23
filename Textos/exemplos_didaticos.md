# Caderno de exemplos — todo o ferramental, primeiro em miniatura, depois com os dados reais

> **O que é este documento.** O irmão do [`guia_de_leitura.md`](guia_de_leitura.md), que
> explica a **matemática** de cada método. Aqui a ordem é outra: para cada conceito e cada
> ferramenta do trabalho, primeiro um **exemplo didático em miniatura** (números redondos,
> conta de cabeça, zero jargão) e depois **o mesmo mecanismo com os seus dados reais** — o
> número que saiu do pipeline, citado com o `#` dele na frente. Se o guia é o curso, este é
> o caderno de exercícios resolvidos.
>
> **Como usar.** Leia uma vez na ordem; depois volte ao verbete na véspera de qualquer
> conversa em que você precise **explicar** o trabalho (banca, orientador, artigo). Cada
> verbete termina com uma **frase pronta** — a explicação em uma ou duas frases, do tamanho
> de uma resposta de banca. A [Parte G](#parte-g--o-bolso-de-frases) reúne todas elas numa
> tabela só, para revisar de vez em quando.
>
> **Regra de honestidade do caderno.** Os números das miniaturas são **inventados de
> propósito** (redondos, para a mecânica aparecer); os números reais estão **verificados nas
> fichas** de [`pipelines/`](pipelines/) e nos textos de [`metodologia/`](metodologia/) —
> quando um deles já foi corrigido antes (20,5 → 51,6 → 48,1 Mt/ano, R² 0,047 → 0,105),
> este caderno cita o valor vigente em 22/set/2026.

---

## Parte A — A matéria-prima: o dado antes de qualquer método

### A1 · Pixel e cubo de dados

**O exemplo simples.** Um tabuleiro 3×3 em que cada casa é um terreno. Você fotografa o
tabuleiro inteiro todo ano, durante 5 anos. A pilha de 5 fotos é o **cubo**: posição
(linha × coluna) × tempo. Toda pergunta do trabalho — "quanto mudou", "quem virou o quê",
"para onde foi" — é uma conta feita sobre essa pilha de fotos.

**Com os seus dados.** MapBiomas Coleção 10.1: células de **30 × 30 m** (0,09 ha) cobrindo
o Brasil, classificadas **anualmente de 1985 a 2024**. Goiás tem ~340 mil km², ou seja, da
ordem de **380 milhões de células fotografadas 40 vezes** — o "cubo censitário local" do
[#28](pipelines/28_idade_pastagem.md)/[#12B](pipelines/12_transicoes.md) (0,8 GB comprimido,
33×). Só o #28 registra **44.639.028 eventos de conversão** (3,82 Mha = 11,2% do estado,
244 de 246 municípios).

**O que isso não diz.** Um pixel não é um lote, não é um produtor, não é uma decisão. A
menor decisão visível do mundo real cobre muitos pixels — e um pixel sozinho não chega a ser
decisão de ninguém.

**Frase pronta.** *"A unidade básica é o pixel de 30 m fotografado 40 vezes; tudo o que o
trabalho afirma é uma conta feita sobre essa pilha de fotos."*

---

### A2 · Classe, grupo — e o Mosaico

**O exemplo simples.** Numa festa, cada convidado ganha uma etiqueta: "dança", "bar",
"mesa". De longe, o observador às vezes não consegue ver direito e cria a etiqueta "não sei
dizer". Essa etiqueta **não é um comportamento da festa** — é a dúvida do observador virada
categoria. Somá-la a "bar" seria importar a dúvida para dentro da estatística.

**Com os seus dados.** As dezenas de classes do MapBiomas são dobradas em **6 grupos de
trabalho** (florestal, savânica, campestre, pastagem, agricultura, outros) e, desde o
[#12B](pipelines/12_transicoes.md), o **"Mosaico de Usos" (classe 21) como 7º grupo** — a
classe em que o classificador admite não conseguir separar lavoura de pasto. O #12 original
nem a mapeava: **6,5–10,9% de Goiás sumia do numerador e do denominador todo ano** sem
ninguém notar (o bug da classe 21, [`censo_vs_amostra.md`](metodologia/censo_vs_amostra.md)).
A decisão substantiva do #28: mosaico fica **categoria própria** — é incerteza de
classificação, não uso observado.

**O que isso não diz.** A etiqueta não é o chão. Classes oscilam entre anos (ver E6), e o
Mosaico **cresceu de significado** ao fim da série (ver E1) — ler qualquer classe sem
conferir o contrato do grupo é onde nasce erro.

**Frase pronta.** *"'Mosaico de Usos' não é um uso — é o classificador dizendo que não sabe.
Tratá-lo como categoria própria mantém a dúvida dele fora das minhas conclusões."*

---

### A3 · Estoque × fluxo (a matriz de transição)

**O exemplo simples.** Uma caixa d'água: o **nível** de hoje é o estoque; a **torneira e o
ralo** por ano são o fluxo. Dois municípios com o mesmo nível podem estar em situações
opostas — um enchendo, outro esvaziando. Só o filme dos fluxos distingue os dois.

**Com os seus dados.** O [#5](pipelines/05_pastagem_soja.md) inferia fluxo pela diferença
de estoques (proxy) — **superado** pelo [#12](pipelines/12_transicoes.md): a matriz de
transição **pixel-a-pixel** (quem virou o quê, ano a ano), depois recontada honestamente
como 7 grupos no [#12B](pipelines/12_transicoes.md) e consolidada em 39 pares de classes
pelo [#19](pipelines/19_conversoes_brutas.md). É ela que mostra o `veg→pasto` como a
**transição-mãe** pervasiva e o `pasto→agric` liderando só no Sul+Centro no Ato II
([#33](pipelines/33_transicoes_regionais.md)).

**O que isso não diz.** A matriz diz **quem virou o quê e quando** — nunca por quê. E
fluxo bruto ≠ mudança líquida: entradas e saídas oscilantes se cancelam (é a lição do E6).

**Frase pronta.** *"Estoque é fotografia, fluxo é o filme — e só o filme diz quem virou o
quê."*

---

### A4 · Censura — o horizonte de observação

**O exemplo simples.** Você quer saber a idade média de casamento, mas seus registros
começam em 2000. Todo casamento anterior a isso não tem idade observável: é **censurado à
esquerda**. Se numa cidade as pessoas casam mais cedo, sobram **menos** casamentos
observáveis lá — a censura é maior justamente onde o fenômeno é mais antigo. Comparar a
média das duas cidades sem comparar as censuras é comparar coisas que o dado não sabe.

**Com os seus dados.** A série começa em 1985; a idade do pasto é "anos desde a última
conversão **observada**". No censo do [#28](pipelines/28_idade_pastagem.md), **63,7%** dos
eventos são censurados (o bug da classe 21 inflava isso a 74,9%), e a censura é maior no Sul
(**70,9%**) que no Norte (**41,9%**) — *porque o Sul converteu antes de 1985*; por mesorregião
vai de 37% (Leste) a 71% (Sul/Centro). Mediana calculada **com** censurados é limite
inferior e distorce: o Centro aparece como 3ª mais velha (19 a) com censurado dentro, e
empatado em mais jovem (9 a) sem ([ficha 28](pipelines/28_idade_pastagem.md)).

**O que isso não diz.** Censurado ≠ inexistente. Censuras diferentes entre grupos fazem
qualquer comparação de média/mediana entre eles mentir — a diferença pode ser do horizonte,
não do fenômeno.

**Frase pronta.** *"Antes de comparar idades entre regiões, compare as censuras — no Sul,
70% das idades são incognoscíveis porque o pasto é mais velho que a própria série."*

---

### A5 · Censo × amostra — e o contrato do peso

**O exemplo simples.** Medir a altura da turma entrevistando 3 de 30 alunos é **amostra**
(tem sorteio, tem erro amostral); medir os 30 é **censo** (não tem sorteio, não tem erro
amostral — mas continua podendo ter **ponderação** errada). Se você entrevista 3 alunos
por turma e depois junta tudo, uma turma de 60 e uma de 10 pesam igual — o erro não estava
no sorteio, estava no peso.

**Com os seus dados.** O #28 era amostra de 2.000 pixels/ano; virou **censo**
(44,6 M eventos, 1.016×). A comparação em dois níveis
([`censo_vs_amostra.md`](metodologia/censo_vs_amostra.md)) separou as duas causas: **por
ano, a amostra era sadia** (mediana difere −0,09 ano em média); **no agregado, o problema
era o peso** — 2020 valia 22,2% na amostra contra **43,2%** reais; 2024 valia 24,5% contra
**11,2%**. O "2.000/ano" tratava um ano de 607 mil conversões igual a um de 157 mil. Por
isso a frase *"a rotação está se tornando dominante" caiu*: no censo, o componente jovem do
Ato III (w₁ = **51,5%**) *alcança* o antigo, não o supera. D21–D24 registram as regras
(fração fora do recorte, sentinela ≠ categoria, censo mata ΔBIC, contrato peso=1).

**O que isso não diz.** Censo não é "mais verdade" para inferência: com n gigante, testes
paramétricos degeneram (ver D10) — o que sustenta a bimodalidade é a **estabilidade
censo×amostra**, não um p. E a correção da amostra (filtrar o envelope) era válida porque
condicionada a cair em Goiás a seleção seguia uniforme — o defeito era o envelope engolir
**43,7%** de linhas fora do estado.

**Frase pronta.** *"O censo acabou com o erro amostral, não com a pergunta estatística — e
a mudança que ele causou nos números foi de ponderação, não de sorteio."*

---

### A6 · AMC — Áreas Mínimas Comparáveis

**O exemplo simples.** Comparar a nota da Escola X em 2000 e em 2024, quando ela fundiu com
a vizinha em 2010: o "X" de hoje não é o mesmo território. AMC é **seguir a turma**, não o
prédio — reconstruir a unidade de modo que o território seja o mesmo nos dois extremos da
série.

**Com os seus dados.** [#25](pipelines/25_amc_goias.md): **166 AMCs** de território
constante 1985–2024 (método Ehrl 2017,
[`areas_minimas_comparaveis.md`](metodologia/areas_minimas_comparaveis.md)). É o palco do
painel longitudinal (~6.600 obs AMC×ano no [#38](pipelines/38_drive_comum_amc.md)) — o
[#16](pipelines/16_painel_unificado.md) municipal tem 9.840 linhas × 185 colunas e sofre
com municípios que nascem, fundem e se desmembram.

**O que isso não diz.** A AMC conserta o **território**, não a **coleta** — o Censo Agro
muda questionário entre rodadas, e AMC não desfaz isso. Também não torna unidades
comparáveis em **tamanho**, apenas em contorno.

**Frase pronta.** *"O município muda de nome ao longo de 40 anos; a AMC é o território que
não mente sobre si mesmo — por isso todo painel longitudinal da Fase 6 mora nela."*

---

## Parte B — Medidas descritivas: mostrar antes de explicar

### B1 · Centro de massa

**O exemplo simples.** Régua de prato: 1 kg no ponto 0 e 1 kg no ponto 100 → equilíbrio em
50. Agora metade do peso do meio se muda: 0,5 kg fica em 100 e 0,5 kg vai para 150 →
equilíbrio em (1·0 + 0,5·100 + 0,5·150)/2 = **62,5**. O ponto de equilíbrio andou 12,5 para
o lado onde a massa **cresceu** — sem que nenhum peso tenha "andado" no espaço. Centro de
massa é média ponderada de coordenadas: ele se move quando a **fatia** de cada lugar no
total muda.

**Com os seus dados.** [#32](pipelines/32_centro_massa.md) (EPSG:5880, sobre as 166 AMCs):
pastagem **+78 km**, rebanho **+67 km**, agricultura **+65 km** ao norte em 40 anos;
vegetação natural **+7,6 km com IC95% que inclui zero** — "ancorada" (D19, bootstrap
B=2000). A lavoura fica **123–135 km ao sul** do pasto/rebanho **em todos os anos**. A
leitura certa do número: *"o centro de gravidade da pastagem está 78 km mais ao norte em
2024 do que em 1985"* — nunca *"o pasto subiu"*. O mecanismo é composição: o pasto tem duas
pontas (Sul e Norte), o boi só cresce no Norte, e a lavoura cresce **mais no Sul** e ainda
assim sobe, porque a fatia do Sul no total cai de ~92% para ~71% do estado
([#34](pipelines/34_deslocamento_espacial.md)).

**O que isso não diz.** Nada de mecanismo — é descrição, e é uma **média**: o
[#44](pipelines/44_centro_massa_desagregado.md) abriu a vegetação e a "muralha parada" era
só a **floresta** (+9 km); o campo nativo **recuou 35 km**. Média esconde pedaços.

**Frase pronta.** *"O centro de massa não se move porque alguém andou; move porque a fatia
de cada lugar no total mudou — por isso eu digo 'o centro de gravidade está 78 km mais ao
norte', e nunca 'o pasto subiu'."*

---

### B2 · Idade do pasto e bimodalidade (mistura de gaussianas)

**O exemplo simples.** Medir a idade dos carros de um estacionamento e achar **dois
montões**: ~3 anos (frota de locadora, renovação rápida) e ~15 anos (táxi que roda até
morrer). Uma "média de 9 anos" não descreve ninguém. Mistura de gaussianas é achar as duas
sinetas escondidas no histograma — cada modo é uma história.

**Com os seus dados.** [#28](pipelines/28_idade_pastagem.md): a idade do pasto **na
conversão** é bimodal — na curva inteira do censo, uma população jovem (μ ≈ **4** anos,
σ ≈ 1,6, 33% da massa) e uma velha (μ ≈ **16**, σ ≈ 7,5, 67%) — dois mecanismos
coexistindo (rotação de pasto jovem × conversão de pasto velho). O qualificador viaja
junto com o número: nas janelas deslizantes, μ₂ lê-se 21–23. A
coexistência é o que sobrevive a tudo: **5/5 mesorregiões, 10/10 células** sob a união
(Mosaico incluído). O peso do modo jovem no Ato III (w₁ = **51,5%**) alcança, não supera.

**O que isso não diz.** A bimodalidade **não** é causada pela região — o
[#28C](pipelines/28C_bimodalidade_regional.md) mediu a decomposição da separação
jovem/velho: espaço explica **1,3%** (mesorregião) a **7,5%** (AMC), tempo **19,6%**, e
**75–79% mora dentro das células**; na régua da união, a mesorregião despenca para
**0,5%** da variação da idade — o número que a qualificação cita. A **tendência
temporal** de w₁ caiu no [#28D](pipelines/28D_deriva_mosaico.md) (acompanha a mudança de
rótulo). E a **ordenação de idade entre regiões** depende da régua: sob o bracket do #33, a
tabela inverte (Sul 16→32 a, Norte 27→23 a). Quem lê o histograma tem que dizer qual régua o
descreve.

**Frase pronta.** *"Dois montões no histograma são duas histórias no mesmo pasto — rotação
de pasto jovem e conversão de pasto velho — e onde a mistura mora não é a região: três
quartos ficam dentro das próprias células."*

---

### B3 · Hazard e a decomposição do fluxo

**O exemplo simples.** Uma fazenda com 100 ha de mata; o fazendeiro derruba, todo ano,
**10% do que ainda está de pé** (não 10 ha fixos). O hazard é essa divisão: o que caiu ÷ o
que ainda estava de pé.

| ano | de pé no início | derrubado (fluxo) | de pé no fim | hazard |
|---|---|---|---|---|
| 1 | 100 | 10 | 90 | 10% |
| 2 | 90 | 9 | 81 | 10% |
| ⋮ | *(mesmo ritmo, todo ano)* | | ⋮ | 10% |
| 15 | ≈23 | ≈2 | ≈21 | 10% |
| 16 | ≈21 | ≈1 | ≈20 | **5%** |

A coluna do fluxo cai **todo ano** (10, 9, …, 2) sem o hazard se mexer uma vez: queda de
fluxo pode não ser mudança de comportamento nenhuma — só sobrou menos mata. No ano 16 o
hazard cai para 5%: agora cada hectare de pé cai na metade da velocidade (sobrou o difícil),
e é só aí que o comportamento mudou. Quem olha só o fluxo não distingue os dois motivos;
quando ele cai, a conta aritmética separa as duas causas:

```
Δfluxo = h̄·Δestoque  +  ē·Δhazard
          ↑                   ↑
  caiu porque sobrou    caiu porque cada hectare
  menos mata            de pé passou a cair mais devagar
```

**Com os seus dados.** [#39](pipelines/39_fronteira_fechando.md): **no Sul a fronteira
fechou** (estoque de convertível a 53% do de 1985, hazard caindo); **no estado, não** —
resta ~60% do convertível, a fronteira só migrou ao norte. A decomposição aplicada à freada
do Sul: apenas **17%** é "ter menos Cerrado"; **83%** ficam na parcela residual — e essa
parcela **não é demanda** (reúne propensão a converter, atrito de acesso, proteção, troca de
fonte de terra). O mecanismo dentro dela é medido no
[#39B](pipelines/39B_fronteira_dominio_deplecao.md) (ver E2): onde a depleção entra no
domínio certo, caem **as duas coisas** — estoque **e** taxa (16/16 células com β<0).

**O que isso não diz.** A decomposição é **identidade aritmética**, não causal — separa as
contas, não diz por que cada parcela se move. E Δhazard ≠ demanda (a leitura errada que a
ficha do #39 já registrou).

**Frase pronta.** *"A conta separa 'acabou a terra' de 'acabou a vontade' — e no Sul a
resposta é 17/83: a parcela do estoque é pequena, e o argumento de oferta nunca se apoiou
nela, apoiou-se na taxa cair com demanda no pico."*

---

### B4 · Réguas de tempo e periodização por triangulação

**O exemplo simples.** A "temperatura média do dia" depende de onde você corta: meça da
meia-noite à meia-noite e o dia "esfria". Para não escolher o corte que lhe convém, use
**três relógios independentes** e defina a regra **antes** de olhar o resultado
(pré-registro).

**Com os seus dados.** Dois ferramentos. (1) As **4 réguas** reutilizáveis (D12,
[`janelas_temporais.md`](metodologia/janelas_temporais.md)): série completa, atos, grade de
5 anos, décadas — o [#35](pipelines/35_robustez_janelas.md) testa cada manchete nelas. (2)
A **periodização** do [#29](pipelines/29_triangulacao_periodizacao.md): sup-F multivariado
(primário) + STARS + KL/TV (sensibilidades), regra definida antes de rodar → fronteiras
**2001** (F=62,2) e **2020** (F=21,5) confirmadas; 1991 (F=10,3) instável, não confirmada.
Os atos: **I 1985–2000 "Pastagem como herança", II 2001–2019 "Expansão e intensificação",
III 2020–2024 "Conversão acelerada sob rótulo ambíguo"**. A fronteira de 2020 **fortalece**
sob a correção do Mosaico (F 21,5→34,1) e existe fora do MapBiomas (soja SIDRA: F=7,8,
p=0,008; taxa triplica de +0,10 para +0,31 Mha/a). A sub-fase 2001–05 fica como nota: difere
em **composição** (perda de vegetação 5×, p=0,0008), não em taxa total (p=0,060, poder
0,63). Os marcos institucionais viram **tipologia A/B/C**: hoje **nenhum** é "A" — todos são
B (referência narrativa) ou C (limite da série); o Código Florestal não produz quebra em
lugar nenhum.

**O que isso não diz.** As fronteiras são **do comportamento LULC**, não de lei — e "ato"
não é período histórico-causal. A fronteira de 2001 é **a pastagem quebrando em 2001**, não
a Lei Kandir (1996).

**Frase pronta.** *"Os cortes foram escolhidos pelos dados, com regra definida antes de
rodar: a série quebra em 2001 e 2020, e nenhum marco institucional — nem o Código Florestal
— produz quebra alguma."*

---

## Parte C — A gramática estatística

### C1 · Correlação (r) — e o confundidor

**O exemplo simples.** Vendas de sorvete e afogamentos sobem juntos todo verão; ninguém se
afoga por comer sorvete — o **verão** move os dois. `r` mede co-movimento, ponto. E há um
caso especial: `r` perto de 1 entre duas variáveis pode significar que **são a mesma
variável duas vezes**.

**Com os seus dados.** Os dois lados do mesmo número alto: **r = 0,89** entre o raster
MapBiomas e a soja SIDRA ([#44](pipelines/44_centro_massa_desagregado.md)) é uma
**validação** — é exatamente o que se quer quando duas fontes independentes medem o mesmo
fenômeno. Mas **r = 0,986** entre o regressor `trase_soja_volume_t` e a área plantada era
um **alarme**: o "volume exportado" era a **produção disfarçada** — o β-manchete do
[#45](pipelines/45_trase_lulc.md) caiu de **+0,335 para +0,037** quando trocado pelo volume
exportado de verdade. Regra do trabalho: **cheque a correlação entre regressor e regressando
antes de ler o β**.

**O que isso não diz.** Causa, direção, mecanismo — nada disso está em `r`. E o mesmo valor
de `r` pede leituras opostas conforme as duas variáveis sejam fontes rivais (validação) ou
quase-a-mesma-coisa (vazamento).

**Frase pronta.** *"r=0,89 entre raster e SIDRA é uma validação; r=0,986 entre regressor e
regressando é um alarme — o mesmo número alto quer coisas opostas dependendo do que as duas
variáveis são."*

---

### C2 · Primeira diferença — dentro (within) × entre (between)

**O exemplo simples.** Altura × vocabulário de uma criança ao longo dos anos: correlação
≈1, e é **pura mentira estatística** — ambas crescem com a idade (tendência comum). A cura
é olhar a **variação anual**: "quanto cresceu este ano" × "quantas palavras novas neste
ano". O que sobrevive é o co-movimento verdadeiro.

**Com os seus dados.** D7: **correlação sempre em primeira diferença, nunca em nível** — é
o contrato do [#21](pipelines/21_correlacoes_uf.md) e a base do painel. A auditoria de
circularidade pós-Trase (jul/2026) mediu o tamanho do risco: correlação de nível ~0,9
desaba para ~0 em Δ within — o vazamento de tendência estava armado em todo par de séries
que crescem juntas. O [#22B](pipelines/22_correlacoes_painel.md) é a mesma ideia no painel:
o FE de **grupo×ano** fecha o canal da composição *dinâmica* que o FE de entidade não
fecha, e o β se move só +2,4% a +14,1% (24/24 subamostras negativas) — a resposta era
**within** (dentro do município), não composição entre municípios.

**O que isso não diz.** A primeira diferença remove a tendência comum — mas joga fora
também a informação de **longo prazo**: dois séries podem co-mover no curto prazo e divergir
no longo (para isso existe cointegração, verbete 3.2 do guia).

**Frase pronta.** *"Em nível, tudo em Goiás correlaciona com tudo, porque tudo cresce junto;
em primeira diferença, sobra só quem se move junto de verdade."*

---

### C3 · Regressão e o β

**O exemplo simples.** "Cada R$ 1 de crédito está associado a R$ 0,30 de venda a mais,
*tudo o mais constante*." O β é a inclinação — e o "tudo o mais constante" é uma hipótese,
não um fato. Se dois regressores andam de braços dados (multicolinearidade, VIF>10), a
inclinação de cada um fica instável.

**Com os seus dados.** [#22](pipelines/22_correlacoes_painel.md) (2-way FE, VIF ≤ 1,55):
onde a lavoura entra, o pasto sai **localmente** — substituição local; SICOR é o canal
dominante de retração na janela em que existe (2013–2021, ~8 anos). No
[#34](pipelines/34_deslocamento_espacial.md), o β da substituição é **−0,52** na régua crua
(robusta: −1,14 união / −0,07 SIDRA, p<0,001). E o #49 (Elhorst espacial) separa os canais:
**M3 (substituição) robusto** — β<0 nas 3 réguas e 2 janelas, o β≈−0,5 é **piso**; **M1
(intensificação) frágil** — o bracket atravessa o zero.

**O que isso não diz.** β não é efeito causal sem desenho que o sustente; e **β em
z-score não se compara entre tratamentos** cujos desvios-padrão diferem (#39B: sd varia
17×) — cada β fala na unidade em que foi medido.

**Frase pronta.** *"O β diz 'associado a'; a distância até 'causa' é o desenho — por isso
cada β-manchete do trabalho carrega uma régua de robustez atrás dele."*

---

### C4 · R²

**O exemplo simples.** Com 2 pontos, qualquer reta dá R²=1 — perfeito e inútil. R²
pergunta "quanto da variação a reta explica", e ele **não sabe** a diferença entre explicar
e coincidir.

**Com os seus dados.** O R² mais informativo do trabalho é um **zero**: no
[#51](pipelines/51_crescimento_sem_desenvolvimento.md), a expansão de área e o IFDM têm
r²within ≈ 0 — a fronteira Norte quase dobra a área (**+93%** vs +14% no Sul) e ganha
desenvolvimento **igual** ao Sul (fica −0,08 abaixo); o VA agro tem dividendo modesto
(r=0,21). "Crescimento sem desenvolvimento" é um R² de **zero** transformado em achado.
E o #39B mostra o contrário: com o domínio do regressor tratado, o R²within do hazard sobe
de ~0 para **0,05–0,20** — o mecanismo passa a existir na regressão.

**O que isso não diz.** R² alto não valida modelo nem causa; e R² baixo pode ser **a
resposta**, quando a pergunta era "tem ligação?" — aí zero é descoberta, não fracasso.

**Frase pronta.** *"Um R² de zero pode ser um resultado: quando a pergunta era 'crescer em
área traz desenvolvimento?', a resposta zero é a descoberta."*

---

### C5 · Painel 2-way FE

**O exemplo simples.** Quer saber se a merenda melhora as notas. Comparar a escola com a
vizinha confunde (a vizinha é outra desde sempre). Melhor: comparar **a escola consigo
mesma** nos anos sem merenda (efeito fixo da escola), e ainda tirar o que aconteceu em
**todas** as escolas naquele ano — greve, pandemia (efeito fixo do ano). O que sobra é a
associação dentro da unidade.

**Com os seus dados.** [#22](pipelines/22_correlacoes_painel.md): `PanelOLS` com
entity+time effects (D8), SE clusterizado por município — o cavalo de batalha da Fase 4. O
[#49](pipelines/49_painel_espacial_dinamico.md) mostra a escada: os canais do #22
sobrevivem ao termo espacial (Elhorst FE lag/error). E o
[#22B](pipelines/22_correlacoes_painel.md) acrescenta o refinamento: FE de **grupo×ano**
(em vez de só entidade) para fechar o canal da composição dinâmica — ver C2.

**O que isso não diz.** FE controla o que é **fixo** na entidade e o que é **comum** no
ano; não controla o que **varia dentro** da entidade (política local, preços locais) — e
não transforma associação em causa.

**Frase pronta.** *"Cada município comparado consigo mesmo, cada ano retirado de todos os
municípios — o que sobra é a associação dentro da unidade, não entre elas."*

---

### C6 · Erro-padrão HAC (Newey-West)

**O exemplo simples.** O erro-padrão ingênuo trata os anos como bolas de bingo sorteadas
independentes. Mas o pasto de 2020 não esquece 2019: um ano puxa o outro. O HAC estima a
incerteza admitindo essa **memória** entre observações consecutivas.

**Com os seus dados.** Todos os slopes do [#17](pipelines/17_taxas_lulc.md) (o motor de
taxas mais reutilizado do projeto) saem com HAC (maxlags=2); as correlações do #21 idem; a
convenção do trabalho: **não usar OLS i.i.d. para inferência em série temporal**
([glossário](metodologia/glossario_metricas.md)).

**O que isso não diz.** HAC conserta a estimação da incerteza, **não o N** — com N≈38 anos
o poder segue baixo (ver D1), e nenhum erro-padrão inventa informação.

**Frase pronta.** *"Ano não é observação independente — o HAC é o erro-padrão que admite
que o ano puxa o ano."*

---

### C7 · Autocorrelação espacial (Moran's I, SAR/SEM)

**O exemplo simples.** Numa sala, quem senta perto ri junto: vizinhos se parecem. O
Moran's I mede o quanto os vizinhos de um mapa se parecem entre si. Se você ignora essa
semelhança, seu erro-padrão fica estreito demais — e você "descobre" coisas que eram só
geografia.

**Com os seus dados.** [#24](pipelines/24_analise_espacial.md): **115 de 140 resíduos**
com Moran's I significativo — o espaço é estrutural, não ruído. O
[#49](pipelines/49_painel_espacial_dinamico.md) estima ρ/λ (SAR/SEM, Elhorst) e os canais
do #22 sobrevivem. E o [#55](pipelines/55_robustez_bootstrap_bloco.md) tira a consequência
honestidade: reamostrar AMCs **uma a uma** (i.i.d.) era **incoerente com o diagnóstico do
próprio trabalho** — em blocos espaciais (k-means, 166→12 blocos), o IC95% alarga
(pastagem: 45 → 80 km de largura) e **nenhum veredito muda** (6/6).

**O que isso não diz.** Moran alto não é "o vizinho causa" — pode ser variável omitida
correlacionada no espaço (λ), e ρ≠0 (SAR) não é efeito causal do vizinho sem desenho.

**Frase pronta.** *"Os vizinhos se parecem a ponto de o erro-padrão ter que prestar contas
disso — senão a significância sai emprestada da geografia."*

---

## Parte D — Inferência: testar sem se enganar

### D1 · p-valor — e o placar no lugar do adjetivo

**O exemplo simples.** Uma moeda honesta dar 10 coroas seguidas: p ≈ 0,001 — "se a moeda
fosse honesta, isso seria raríssimo". `p` é a raridade do resultado **sob a hipótese de
nada aqui**. Mas cuidado com os dois lados: p pequeno não é verdade grande; e p grande
com amostra pequena não é "provou que não" — é "não sei".

**Com os seus dados.** A regra do trabalho (set/2026): reportar o **placar do teste**, não
o adjetivo — "0 de 36 sobrevivem ao FDR", "β<0 em 16 de 16 células", nunca "evidência
forte". E o exemplo do p grande que não prova nada: o Granger do
[#34](pipelines/34_deslocamento_espacial.md) dá **p=0,97** com N≈38 — nulo de **baixo
poder** (simulação de Monte Carlo: poder ~48% para efeito moderado, ~93% para grande), não
refutação.

**O que isso não diz.** p não é a probabilidade da hipótese ser verdade; 5% não é fronteira
entre verdade e mentira; e com N pequeno o nulo é "**não sei**", nunca "não".

**Frase pronta.** *"Eu reporto o placar do teste, não um adjetivo — e um p grande com N
pequeno é 'não sei', nunca 'não'."*

---

### D2 · Granger — precedência preditiva

**O exemplo simples.** O cachorro sempre sai correndo **antes** de o dono chegar: o
latido ajuda a prever o dono — mas o cachorro não traz o dono para casa. X
"Granger-causa" Y se o **passado de X** melhora a previsão de Y além do passado de Y.
E o teste reverso é o detector de mentira: para um driver verdadeiramente exógeno (preço
internacional), o reverso **deve** dar nulo.

**Com os seus dados.** [#34](pipelines/34_deslocamento_espacial.md): ΔAgric_Sul **não**
precede ΔPasto_Norte (p=0,97). O teste reverso deu p=0,0007 — o Norte "liderando" o Sul —
que seria a tese invertida… e era **artefato de série integrada** (ver D3). Já o câmbio
passa no placebo de exogeneidade do [#37](pipelines/37_drive_comum.md): reverso nulo, como
um driver exógeno deve ser.

**O que isso não diz.** Precedência preditiva ≠ causalidade (o próprio nome "Granger-causa"
é promessa de previsão, não de causa). Em séries que vagueiam, tudo "precede" tudo — é o
D3.

**Frase pronta.** *"Granger diz se o passado de um ajuda a prever o outro — não quem empurra
quem; e o teste reverso é o detector de mentira do método."*

---

### D3 · Estacionariedade, regressão espúria e Toda-Yamamoto (D16)

**O exemplo simples.** Dois bêbados andando de braços dados parecem caminhar juntos:
correlação alta, significância falsa — porque cada um **vagueia** (não volta a uma média).
Antes de testar se o passo de um segue o do outro, confira **como cada um anda**: vagueia
em volta de um ponto (I(0))? Se afasta sem volta (I(1))? Vagueia com aceleração acumulada
(I(2))?

**Com os seus dados.** [#42](pipelines/42_granger_reverso_norte_sul.md): `pasto_Norte` é
**I(2)**, `agric_Sul` é **I(0)** — ordens de integração diferentes **nem cointegram**; o
p=0,0007 do Granger reverso era regressão espúria. O **Toda-Yamamoto** (VAR em nível com
defasagens extras) zera **as duas direções** — e os placebos dão o golpe: o Norte
"lideraria" até o pasto **do próprio Sul**. D16: o veredito é **sem líder** — e a simetria
honestamente impede também reivindicar o oposto ("o Sul lidera").

**O que isso não diz.** Toda-Yamamoto não é o "Granger melhorado que acha o efeito" — é o
teste que **só fala depois de conferir se cada série vagueia**; e um nulo dele não prova
independência.

**Frase pronta.** *"Séries que vagueiam correlacionam por acidente; Toda-Yamamoto é o teste
que confere como cada série anda antes de deixar o Granger falar — e ele zerou as duas
direções."*

---

### D4 · DiD — diferença-em-diferenças

**O exemplo simples.** Uma farmácia abre na rua A e não na B. Compare o antes/depois em
cada rua e **subtraia**: o que sobra é o efeito da farmácia — *desde que as ruas andassem
juntas antes* (parallel trends). O DiD não é "antes e depois"; é antes-e-depois **menos um
contrafactual**.

**Com os seus dados.** [#23](pipelines/23_did.md): GO vs MT/TO em 4 marcos (1995, 2003,
2012, 2018), com event-study (k=−5..+5, k=−1 omitido) e placebo (marco falso 5 anos antes,
janela ±3). Só **`Vegetação × 1995 vs TO`** sobrevive a parallel-trends + placebo. E a
qualificação de 25/jul/2026: os marcos são **federais** — não existe grupo não-tratado;
sem grupo de controle de verdade, o DiD identifica só **exposição diferencial** (o resultado
foi rebaixado a *sensibilidade de co-movimento*). Nota de leitura: o marco que importa na
série do trabalho é o **Commodity Boom (2003)** — a Lei Kandir não está entre os marcos
testados.

**O que isso não diz.** Parallel trends não é testável **depois** do tratamento (só se
conhece o pré); e com tratamento federal, o "controle" também foi tratado — a diferença
medida é de intensidade, não de existência.

**Frase pronta.** *"DiD precisa de um grupo que o tratamento não tocou; com marcos
federais, esse grupo não existe — por isso o #23 reporta co-movimento de exposição, não
efeito causal."*

---

### D5 · Quebra estrutural (sup-F, Quandt-Andrews)

**O exemplo simples.** Uma torneira que muda de vazão num dia: até lá seguia uma média,
depois segue outra. O sup-F procura **o dia** em que trocar a média mais reduz o erro — e o
F mede o quanto a troca ajuda. (E um detector é honesto se, alimentado com puro ruído,
quase não dispara.)

**Com os seus dados.** [#26](pipelines/26_deteccao_quebras.md)/[#29](pipelines/29_triangulacao_periodizacao.md):
sup-F multivariado sobre Δveg, Δpasto, Δagric (binary segmentation, min_size=5, threshold
4,0) → **2001 (F=62,2)** e **2020 (F=21,5)**; 1991 (F=10,3) é instável (desloca 1989–93). A
taxa de falso positivo do detector, medida em ruído branco, é **11%** — limitação declarada.
O Código Florestal (2012) **não produz quebra alguma**. E a fronteira de 2020 sobrevive à
correção da mudança de rótulo **mais forte** (F 21,5→34,1 na série agric∪mosaico).

**O que isso não diz.** Quebra na série ≠ causa institucional: 2001 e 2020 são
**comportamento do uso da terra**; a "explicação" é outra pergunta (é a Perna 3). E a
fronteira depende da janela mínima — quebras a menos de 5 anos da borda não são
detectáveis por construção.

**Frase pronta.** *"A série quebra em 2001 e 2020 porque os deltas mudam — nenhuma quebra
nasceu de um marco institucional; o detector tem 11% de falso positivo em ruído, e isso
está declarado."*

---

### D6 · Multiplicidade e FDR (Benjamini-Hochberg)

**O exemplo simples.** Teste 36 hipóteses a 5%: espere ~2 "significativos" de **puro azar**
(36 × 0,05 ≈ 1,8). O BH ordena os p e só deixa passar os que sobrevivem ao volume testado —
garimpar hits numa grade sem correção é pescar com rede demais.

**Com os seus dados.** [#21](pipelines/21_correlacoes_uf.md): **0 de 36** correlações UF
sobrevivem ao FDR-BH. [#37](pipelines/37_drive_comum.md): **~7 hits em ~135 testes** ≈ a
taxa de acoro (nada sobrevive). [#38](pipelines/38_drive_comum_amc.md): grade exploratória
de 144 testes devolve **nenhum** sobrevivente. [#52](pipelines/52_aptidao_edafoclimatica.md):
2 de 192 sobrevivem — pela mesma fragilidade de família pequena. É por isso que só a
**hipótese confirmatória** (câmbio × fronteira → rebanho, fora da grade) pode ser lida
como achado.

**O que isso não diz.** FDR não diz que os hits são falsos — diz que **não se pode garimar
 numa grade**; e sobreviver ao FDR não é "verdade", é "não morreu na peneira".

**Frase pronta.** *"Com 135 testes, 7 acertos é o que o azar entrega de graça — a pergunta
não é 'quantos deram certo', é 'quantos sobreviveram à correção'."*

---

### D7 · Bootstrap e intervalo de confiança (D19)

**O exemplo simples.** Mediu a altura média de 30 pessoas. Repita a pesquisa 2.000 vezes
"re-sortando" os 30 dos dados originais, e a nuvem de 2.000 médias mostra a incerteza. O
IC95% é onde 95% das médias caem.

**Com os seus dados.** D19 (dentro do [#32](pipelines/32_centro_massa.md)): bootstrap de
AMCs, B=2000 — **todo ΔNorte vem com IC95%**. Foi o que trocou "vegetação +7,6 km" por
"vegetação **+7,6 km com IC que inclui zero**" = **ancorada**. E o
[#55](pipelines/55_robustez_bootstrap_bloco.md) corrige o próprio bootstrap: as AMCs não
são independentes (Moran em 115/140, ρ/λ 0,35–0,56) — em **blocos espaciais** o IC alarga
(pastagem: 45→80 km) e o veredito não muda em **nenhum** tamanho de bloco (6/6). Achado
lateral: **nenhuma componente leste sobrevive** à varredura em blocos — a da pastagem cai
primeiro (blocos de 3 AMCs), a da agricultura em blocos de 8, a do rebanho em 14; a marcha
que o trabalho descreve é a do **eixo norte–sul**, que atravessa as 6 réguas intacto.

**O que isso não diz.** O IC não é "a verdade está dentro com 95% de chance"; e o bootstrap
**herda a suposição de reamostragem** — i.i.d. mente quando as unidades estão
espacialmente correlacionadas.

**Frase pronta.** *"Sem barra de erro, um Δ é um ponto; com ela vira frase completa — a
vegetação ficou onde estava, e é o intervalo que diz isso, não o número só."*

**Nota estendida — o bootstrap por dentro** (explicação de 22/set; conferida no código,
função `bootstrap_incerteza` de [`scripts/centro_massa.py`](../scripts/centro_massa.py)).

"Duas mil vezes" não são 2000 testes — são **2000 medições do mesmo número**, cada uma num
"Goiás alternativo", para ver o quanto o número treme quando a composição de unidades muda.
O bootstrap não testa hipótese nenhuma: **desenha uma nuvem**, e a nuvem é a barra de erro.

*A sacola de papéis.* A unidade sorteada é a **AMC** — nunca pixel, nunca ano (a série
inteira entra em toda réplica; 1985 e 2024 sempre presentes). Os nomes das 166 AMCs vão
para uma sacola; sorteia-se um papel, **anota-se e devolve-se à sacola** antes do próximo
sorteio — é isso que "com reposição" quer dizer. Só a devolução cria variação: sem ela, todo
sorteio puxaria as 166 exatas e a réplica seria idêntica ao original. Com ela, em cada
réplica ~37% das AMCs ficam de fora (a conta de 1/e) e outras entram duas ou três vezes.
Cada réplica é um "Goiás com buracos e duplicatas"; a pergunta que a nuvem responde é: *o
ΔNorte sobrevive a esses buracos?*

*A miniatura, com conta de cabeça.* Três AMCs numa estrada reta sul→norte:

| AMC | Posição | Pasto 1985 | Pasto 2024 |
|---|---|---|---|
| A | km 0 | 10 ha | 2 ha |
| B | km 100 | 10 ha | 10 ha |
| C | km 200 | 10 ha | 18 ha |

Centro 1985 = (0·10 + 100·10 + 200·10)/30 = **km 100**; centro 2024 = (0·2 + 100·10 +
200·18)/30 ≈ **km 153** → ΔNorte ≈ **+53 km** (um número só). Sorteando três papéis com
reposição, quatro réplicas:

| Réplica | Sorteio | Centro 1985 | Centro 2024 | ΔNorte |
|---|---|---|---|---|
| R1 | A, B, C (todas) | km 100 | km 153 | **+53** |
| R2 | B, B, C (A de fora) | km 133 | km 147 | **+14** |
| R3 | A, C, C (B de fora, C dobrada) | km 133 | km 189 | **+56** |
| R4 | A, A, B (C de fora) | km 33 | km 71 | **+38** |

Duas lições na tabela. O Δ **treme** (+14 a +56) conforme o azar inclui ou exclui quem
mudou — essa tremedeira é a incerteza. E o **sinal não treme**: nenhuma réplica zera a
marcha. Se a nuvem cruzasse o zero, a resposta honesta seria "não sei se moveu" — que é o
caso da vegetação, abaixo.

*O código, réplica a réplica.* Cada AMC carrega seu centroide (cx, cy) e o peso de cada ano
(hectares da variável nela; o rebanho vem dos dados tabulares). O sorteio das 2000 sacolas
é um vetor de contagens (`multinomial`): quem saiu 2× entra com peso dobrado — o peso
efetivo é **contagem × área**. Recalcula-se o centro ponderado em **todos os 40 anos** da
réplica; ΔNorte = centro no último ano − centro no primeiro. No fim, ordenam-se as 2000
réplicas e cortam-se os percentis **2,5% e 97,5%** — as posições 50ª e 1950ª da fila. A
`seed=42` é a semente do azar: rodar de novo sorteia as mesmas sacolas e o IC sai igual —
reprodutibilidade que a banca pode conferir.

*Por que 2000, e não 20 nem 100 mil.* O IC são as **pontas** da nuvem. Com 20 réplicas, a
"ponta" é praticamente o máximo da amostra — pura sorte, muda a cada rodada; lá para cima
de ~2000, as pontas param de tremer e o intervalo para de se mover. É convenção de
estabilidade, não mágica — e as réplicas **não aumentam a informação**: tudo já está nos
166; a nuvem só revela.

*Como a nuvem se lê, no [#32](pipelines/32_centro_massa.md).*

| Variável | ΔNorte | IC95% das 2000 réplicas | Leitura |
|---|---|---|---|
| Pastagem | +77,6 km | **[+54,7, +98,2]** | nenhuma réplica zera — robusto |
| Rebanho | +66,9 km | [+47,2, +84,5] | robusto |
| Agricultura | +65,2 km | [+43,5, +94,6] | robusto |
| Vegetação | +7,6 km | **[−0,5, +15,6]** | cruza o zero — **"ancorada"** |

A vegetação é o caso que justifica o método: o ponto diz +7,6, a nuvem cruza o zero —
reportar "moveu 7,6 km" seria reportar azar. É a D19 em ação: ΔNorte cujo IC inclui zero
**não vira número**, vira frase.

*O fino do [#55](pipelines/55_robustez_bootstrap_bloco.md), por extenso.* A sacola acima
supõe papéis **bem misturados** — cada AMC contando uma história independente das vizinhas.
Mas o diagnóstico espacial do próprio trabalho (#24: I de Moran significativo em 115 a 125
dos 140 testes, conforme a régua; ρ/λ entre +0,35 e +0,56) diz que vizinhos **se parecem**:
sortear AMC a AMC "inventa" variação independente que não existe, e o IC sai estreito
demais — otimista. A correção: amarrar vizinhos em **blocos** (k-médias sobre os
centroides; a grade varre k = 166, 83, 55, 33, 20, 12) e sortear blocos inteiros. O IC da
pastagem alarga de 45 para 80 km de largura — e o veredito ΔNorte **não muda em 6/6
tamanhos de bloco** (pastagem, rebanho e agricultura excluem zero nas 6; a vegetação o
inclui nas 6). O que a régua honesta derruba são as componentes **lestes**: **nenhuma
sobrevive à varredura** — a da pastagem é a primeira (cai já em blocos de 3 AMCs, IC
[−1,7; +44,7], e vinha no fio da navalha desde o i.i.d.: [+1,2; +39,5]); a da agricultura
(+49,5 km de ΔLeste na régua crua) cai em blocos de 8 ([−7,3; +105,8]); a do rebanho, em
blocos de 14 ([−7,8; +54,9]). A marcha que a qualificação descreve é a do **eixo
norte–sul** — que atravessa as 6 réguas intacto.

*Frase pronta da nota.* *"Não são 2000 testes — é o mesmo número medido em 2000 Goiases
alternativos; onde a nuvem inteira fica de um lado do zero, o deslocamento é robusto; onde
ela cruza o zero, como na vegetação, a palavra certa é 'ancorada', não '+7,6 km'."*

---

### D8 · Permutação e placebo

**O exemplo simples.** Suspeitar que o baralho veio marcado: embaralhe-o 1.000 vezes e
conte em quantas o resultado "impossível" aparece por acaso. Placebo é o remédio falso:
se o paciente "melhora" igual, o efeito não era do remédio.

**Com os seus dados.** O caso-modelo é o
[#54](pipelines/54_defensabilidade_perna4.md): **permutação do shifter** (embaralhar o
câmbio, manter a aptidão) revelou que o erro-padrão clusterizado era **otimista** — o p do
achado-manchete sai de ~0,03 para **≈0,07–0,13** (não significante a 5%). O que sustenta o
padrão é a **especificidade**: placebos de desfecho nulos (câmbio×aptidão→urbano/água,
p>0,24), lead limpo (p=0,11), jackknife estável. Outros placares do trabalho: **θ<0 em
12/12** réguas × janelas × desfechos do [#34](pipelines/34_deslocamento_espacial.md) (o
sinal oposto ao previsto aparece em todas), e a **simulação de Monte Carlo do poder** do
Granger. Detalhe fino da permutação: com 38 realizações do shifter, **1/38 é o piso** — p=
0,026 significa "nenhuma rotação superou o observado" (o melhor desfecho possível do teste),
**não** margem folgada.

**O que isso não diz.** Permutação não converte associação em causa; e placebo nulo não
prova o mecanismo — prova que o padrão é **específico** do par testado.

**Frase pronta.** *"Embaralhei o câmbio 38 vezes e o padrão nunca voltou tão forte — isso
não é significância a 5%, é especificidade; e eu reporto as duas coisas, com os números."*

---

### D9 · Jackknife

**O exemplo simples.** Refaça a conta **tirando um dado de cada vez**. Se o resultado muda
muito quando um único elemento sai, ele estava nas mãos de um só — e não do fenômeno.

**Com os seus dados.** [#54](pipelines/54_defensabilidade_perna4.md): jackknife por ano —
o sinal se mantém em **100%** das re-estimativas; nenhum ano isolado carrega o achado. E o
[#39B](pipelines/39B_fronteira_dominio_deplecao.md): grade de 16 células de tratamento —
β<0 em **16/16**, p<0,05 em **11/16** — e a única célula que não cruza em nenhuma amostra
era justamente a **publicada** (que não tratava nem o regressor nem o desfecho).

**O que isso não diz.** O jackknife cobre "um por vez" — não é o teste de dois outliers
juntos; robustez a múltiplos pede outro desenho.

**Frase pronta.** *"Tirei cada ano da conta, uma vez de cada, e o sinal nunca virou —
nenhum ano carrega o resultado sozinho."*

---

### D10 · ΔBIC — e a degeneração sob censo (D23)

**O exemplo simples.** Toda variável extra **melhora o ajuste** (o R² só sobe); o BIC é a
**multa por complexidade**: o modelo ganha só se o ganho de ajuste pagar a multa. Mas com
um n gigante, a multa vira esmola — e qualquer diferença minúscula "passa".

**Com os seus dados.** D23: com o censo de **44,6 M eventos**, o ΔBIC **degenera** — n
enorme transforma qualquer diferença em "decisiva". Por isso a bimodalidade do
[#28C](pipelines/28C_bimodalidade_regional.md) se sustenta por **estabilidade
censo×amostra** (mesma ordenação, mesmos w), não por p. O teste certo no censo é o que
pergunta "o padrão se move quando a fonte muda", não "é diferente de zero".

**O que isso não diz.** BIC não mede verdade — mede o equilíbrio ajuste × parcimônia; com
n enorme ele deixa de medir "quão diferente" e passa a medir "quão certo você está de que
difere" — perguntas diferentes.

**Frase pronta.** *"Com 44 milhões de eventos, o BIC não pergunta 'são diferentes?' —
pergunta 'quanto?', e por isso a resposta certa é estabilidade entre fontes, não
significância."*

---

### D11 · Shift-share (Bartik)

**O exemplo simples.** Prever o comércio da cidade com o boom do e-commerce: **fartura
nacional** do boom × **peso da cidade antes dele**. Nenhum dado da cidade *depois* entra na
previsão — ela já vem pronta de fora, e é isso que dá credibilidade. A credibilidade,
porém, tem um limite: se há **um só** shifter nacional, a "sorte" dele e a das cidades não
se separa direito — e a inferência tem que ser mais conservadora.

**Com os seus dados.** [#38](pipelines/38_drive_comum_amc.md): driver nacional (câmbio
REER) × exposição **baseline** da AMC (fronteira) → rebanho (~6.600 obs). Com um único
shifter nacional, o SE clusterizado é **otimista** — a inferência correta é a permutação do
shifter (ver D8). O [#52](pipelines/52_aptidao_edafoclimatica.md) troca a share por uma
**aptidão edafoclimática exógena** (Embrapa 1:500k, WFS): reproduz o gradiente
(r_lat=−0,44; Sul 4,69 > Centro 4,47 > Norte 4,17), carrega informação própria (+0,30 com a
exposição do #38) e tira a objeção de complementaridade mecânica — o achado reaparece com a
share trocada (β=−0,033). O limite do desenho está quantificado: **N efetivo = 38 anos de
um único driver nacional** — nenhuma AMC a mais levanta esse teto.

**O que isso não diz.** Shift-share não é causal por natureza — a validade vem dos
shifters serem quase-aleatórios para as unidades; com **um** shifter nacional, este é o
desenho mais fraco da família, e é por isso que o resultado é reportado como padrão
específico, não como efeito identificado.

**Frase pronta.** *"Câmbio nacional × fronteira de 1985: o desenho soma à AMC a variação
que não cabe a nenhuma delas — e, com um só shifter, o juiz honesto é a permutação, não o
erro-padrão clusterizado."*

---

## Parte E — As réguas de honestidade (o que separa tese de gráfico)

### E1 · Bracket + âncora externa (D26)

**O exemplo simples.** Medir a mesa com uma régua esticada e com a régua frouxa, reportar
**as duas medidas**, e conferir com uma trena de outra marca (a âncora). Se as duas réguas
discordam **até sobre o sinal**, o achado não era do objeto — era da régua.

**Com os seus dados.** [#28D](pipelines/28D_deriva_mosaico.md): a saída da pastagem migrou
do rótulo "agricultura" para "Mosaico" (razão 0,6 em 2015 → **32,5** em 2024; `P→agric`
cai 92%) enquanto o SIDRA registra soja **+38%** — a medida crua subconta o fenômeno real.
D26: reportar sempre o intervalo **[agricultura, agricultura ∪ mosaico]**, sendo a união o
**teto**, não a correção, e a âncora o levantamento do IBGE (que nunca passa pelo
classificador). O que o bracket já decidiu: M3/substituição **robusto** (#49: β<0 nas 3
réguas e 2 janelas — o β≈−0,5 é piso), M1/intensificação **frágil** (o intervalo atravessa
o zero e a âncora dá sinal oposto); a queda de −88% do `pasto→agric` no Ato III **inverte
para +51%** sob a união [#33](pipelines/33_transicoes_regionais.md) — e a tabela de idade
inverte a ordenação (Sul 16→32 a, Norte 27→23 a).

**O que isso não diz.** O bracket não diz qual régua está **certa** — ele separa onde o
achado é estável de onde depende da régua; e a âncora cobre o que a âncora cobre (soja
SIDRA não valida pastagem).

**Frase pronta.** *"Quando o classificador troca de régua no meio da série, eu reporto as
duas réguas e uma âncora que nunca passa pelo classificador — o que sobrevive às duas é
achado; o que depende da régua, eu digo qual é a régua."*

---

### E2 · Domínio da variável (D29)

**O exemplo simples.** Um termômetro que marca −50 °C dentro de um forno: o valor saiu da
**escala que define a variável**. Toda conta em que ele entra mistura coisa com não-coisa —
e o "nulo" que aparecia era o não-coisa fazendo papel de zero.

**Com os seus dados.** [#39B](pipelines/39B_fronteira_dominio_deplecao.md): a
`deplecao_prev` estava documentada como fração **0..1** e no arquivo ia a **−84,9** — em
**920 dos 6.379 pares (14%)**, de 46 AMCs com estoque mínimo de 1985 (mediana 544 ha contra
24.031 ha), cujo estoque *cresceu* (a oscilação pasto↔savana vista pelo estoque).
Z-scorada, a coluna virava "definida" por esses valores — e o B2b publicava um nulo
(β=−0,015; p=0,48) que sustentava a Perna 4 **em falso, na direção errada**. Tratado o
domínio: **β<0 em 16/16 células** de tratamento, p<0,05 em 11/16, convergência em unidade
natural ≈ **0,5–0,8 ponto percentual de taxa anual a cada 0,1 de depleção**, R²within de ~0
para 0,05–0,20. E o reexame derrubou o vizinho: o B2a publicava p=0,002, mas na régua
correta era **p=0,0917** — e some sob corte de 1.000 ha (p=0,74), carregado que era pelas
AMCs de estoque minúsculo.

**O que isso não diz.** Tratar o domínio não é "arrumar número" — é não deixar que a
**unidade** da variável decida o resultado; e os β em z **não se comparam** entre
tratamentos (o sd do regressor varia 17×).

**Frase pronta.** *"O nulo do B2b era um valor fora da escala fazendo papel de zero —
conferido o domínio, o sinal inverteu: na depleção caem as duas coisas, estoque e taxa,
em 16 de 16 células."*

---

### E3 · Horse race — o confundidor da latitude (D28)

**O exemplo simples.** "Vendas de chapéu correlacionam com insolação" — até você pôr a
**latitude** na mesma conta e ver que a correlação era do **eixo** (chapéu vende no sul,
sol brilha no norte), não da variável. Horse race: as duas candidatas **na mesma
regressão**, e quem sobrar carrega o resultado.

**Com os seus dados.** [#56](pipelines/56_drive_horse_race_latitude.md): latitude e
aptidão na mesma regressão (r=−0,44 entre elas — moderadas, não colineares). A aptidão
**perde 62% da magnitude** (β −0,033 → −0,012) e a significância nas **duas** réguas
(p_agrup 0,026→0,30; p_circ 0,13→0,47); a latitude quase não se move (β +0,051→+0,046;
p_circ 0,053; sozinha, p_circ 0,026 — o **piso** 1/38 da permutação, ver D8). **D28**: o
gradiente medido é o do **eixo Sul→Norte**; a aptidão é a **régua** com que o eixo foi
medido (boa nesse papel, por ser exógena ao uso da terra), **não** o canal identificado. O
argumento da Perna 3 sobrevive inteiro; o que cai é a atribuição a solo/clima.

**O que isso não diz.** O horse race não diz que a latitude **é** o canal — diz que a
aptidão **não sobrevive** ao controle; e o p piso de uma permutação com 38 realizações não
é margem folgada — é o melhor desfecho que o teste pode dar.

**Frase pronta.** *"Aptidão era a régua, não a resposta: com a latitude na mesma conta, ela
perde 62% da magnitude e a significância nas duas réguas — o gradiente é do eixo
Sul→Norte, e eu digo exatamente isso."*

---

### E4 · MAUP — o problema da unidade de área

**O exemplo simples.** Medir densidade de árvores com quadrados de 10 m ou de 1 km dá
respostas diferentes: a **malha de medição** muda a medida. A pergunta da robustez é: o
achado é da terra ou da malha?

**Com os seus dados.** [#43](pipelines/43_centro_massa_pixel.md): a manchete do
[#32](pipelines/32_centro_massa.md) refeita **pixel-a-pixel, sem nenhuma malha
administrativa** — pastagem +79,2 km (vs +78 da malha AMC), agricultura +66,9 (vs +65).
Diferença de 1–2 km: o MAUP **não é problema prático** para esta manchete. (E o #32 já usa
AMC, não municípios, justamente porque municípios mudam de contorno.)

**O que isso não diz.** MAUP não se "resolve" em abstrato — se mostra **estável ou não no
caso concreto**; a resposta de um estudo não vale para o outro.

**Frase pronta.** *"Refiz a manchete sem nenhuma malha administrativa, pixel a pixel, e ela
se moveu 1–2 km — o achado é da terra, não da malha."*

---

### E5 · Instrumento × placebo (o que seria um IV)

**O exemplo simples.** Querer medir o efeito do estudo sobre a renda esbarra na mão
dupla: renda compra estudo. Um **instrumento** é uma loteria que distribui estudo ao
acaso — quem ganha não escolheu, e a comparação vale. Se a "loteria" na verdade premia quem
**já ia** estudar, ela é placebo, não instrumento.

**Com os seus dados.** A malha fundiária LAPIG (snapshot 04/2026,
[`malha_fundiaria_ambiental.md`](metodologia/malha_fundiaria_ambiental.md)) foi avaliada
para a Perna 4 e **rejeitada como instrumento**: é **estática** (não varia no tempo),
**endógena** (a proteção responde à própria conversão) e **pós-desfecho**; vale como
placebo. O que restou da peça institucional está no
[#46](pipelines/46_fronteira_protecao.md): **97% do convertível remanescente (6,35 de 6,56
Mha) está desprotegido**, a Proteção Integral cobre <3% e congelou após 2000 — a terra que
resta está desprotegida: **o teto é físico, não institucional**. (GO tem pouca área
protegida: 4 TIs, 114 UCs.)

**O que isso não diz.** "Achei um placebo" não é consolo — é o **resultado negativo** de
procurar instrumento e não achar; e as proxies de estoque/proteção têm **teto declarado**
(D13/D17): MapBiomas + malha vetorial, sem CAR pixel a pixel — "convertível" não é
cadastro.

**Frase pronta.** *"Procurei na malha fundiária um instrumento e achei um placebo: ela
responde ao próprio desfecho — por isso a uso só como placebo, e o teto que resta é físico:
97% do convertível não tem proteção."*

---

### E6 · Oscilação do classificador × regeneração

**O exemplo simples.** Um juiz que relê as mesmas fotos e troca "campo" por "pasto", e no
ano seguinte volta: o **fluxo aparente** não é o gado chegando nem a natureza voltando — é
o juiz balançando. Oscilação é **bidirecional e balanceada**; regeneração é lenta e
**unidirecional**.

**Com os seus dados.** [`oscilacao_pasto_savana.md`](metodologia/oscilacao_pasto_savana.md):
o fluxo reverso `pasto→natural` é majoritariamente **pasto→Savana** (75–98% do total), e a
razão `savana→pasto : pasto→savana` colapsa de **8,4×** (1985–95) para **1,22×** (anual,
2023–24: 50.770 ha de um lado, 61.792 do outro) — oscilação de classificador, não
recuperação. A componente real é **minoritária e lenta**: só no par longo 1985→2024 o
`pasto→Floresta` chega a 184.049 ha (**38% do reverso**); nas janelas decenais/anuais é
2–8%. O [#57](pipelines/57_remanescente_qualidade.md) usa essa lição para se policiar: a
fração florestal do remanescente sobe **no estado inteiro** (37,0→42,5%) e o excesso do Sul
é de ~2 pontos — a **tendência** não separa seleção de deriva; o que se afirma é o **nível**
(Sul 52,2→59,9% vs Norte 29,6→34,3% de fração florestal).

**O que isso não diz.** **Nunca** narrar pasto→natural como recuperação; e o churn
savana↔floresta **não foi medido** (resíduo declarado que pode biasedar o #47).

**Frase pronta.** *"Pasto que vira savana e volta no ano seguinte não é natureza voltando —
é o classificador balançando; só a floresta que acumula em 40 anos é regeneração, e ela é
minoritária."*

---

## Parte F — As lentes teóricas (conceitos para ler o resultado)

### F1 · Frente de expansão × frente pioneira (Martins)

**O exemplo simples.** Duas frentes diferentes com o mesmo nome na manchete: na **de
expansão**, o capital chega onde a produção **já existia** e a reorganiza; na **pioneira**,
chega **antes** do mercado, sobre terra tratada como "vazia" — vazia de trabalho, nunca de
gente.

**Com os seus dados.** Se a banca perguntar: o **Norte goiano é frente PIONEIRA**
(martins1996, conferido no full text — 0 erros de atribuição; extrato em
`qualificacao/ref/pdf/_martins.txt`); o Sul que intensifica é o retrato da frente de
**expansão**. Os números da pioneira: +93% de área no Norte vs +14% no Sul (#51), fogo à
frente da conversão em **39/39 anos** (+73 km, [#41](pipelines/41_fogo_fronteira.md)),
estoque convertível ainda ~60% ([#39](pipelines/39_fronteira_fechando.md)).

**O que isso não diz.** Martins p. 32: a tipologia é **vocabulário, não teste** — posição
do próprio autor. Ela orienta a leitura; não substitui a estatística, e não vira hipótese
testável sem operacionalização.

**Frase pronta.** *"Se a banca perguntar: o Norte goiano é frente pioneira — o Sul
reorganiza o que já produzia; e a tipologia de Martins é vocabulário, não teste, como ele
mesmo diz na página 32."*

---

### F2 · von Thünen e a transição florestal (Angelsen)

**O exemplo simples.** O anel de Thünen: perto da cidade, a terra vale mais e leva o uso
**intensivo** (horta); longe, o uso **extensivo** (gado). Quando o preço da terra sobe, o
anel intensivo **se expande para fora** — não "empurra" o gado mecanicamente: o gado vai
sendo absorvido ou reassentado mais longe, coordenado pelo preço.

**Com os seus dados.** A geometria do anel, congelada: a lavoura fica **123–135 km ao sul**
do pasto/rebanho em **todos os anos** ([#32](pipelines/32_centro_massa.md)) — a produção
intensiva mais perto do mercado, a extensiva além. A "marcha ao norte" é o anel se
expandindo sobre a fronteira; o **teto de oferta** decide o que ele encontra pela frente
(Perna 4). É a âncora teórica do
[`referencial_marcha.md`](referencia/referencial_marcha.md) (Angelsen 2007: von Thünen +
transição florestal).

**O que isso não diz.** O anel **prevê a geometria**, não o empurrão — a expansão do anel
não é mecanismo causal de deslocamento regional (foi exatamente isso que a Perna 3 testou
e não encontrou); e "transição florestal" não está afirmada em Goiás — o que se mede é o
que resta (E6).

**Frase pronta.** *"O modelo do anel prevê a geometria — lavoura mais perto do mercado que
o gado — e não o empurrão; e a geometria é exatamente o que os 123–135 km congelados
mostram."*

---

### F3 · Câmbio (REER) → preço recebido → soja (Richards)

**O exemplo simples.** O produtor vende em dólar e paga em real. O **preço que recebe**
soma os dois: preço internacional × câmbio. Desvalorizar o câmbio transforma o mesmo dólar
da saca em mais reais — e o REER (câmbio da cesta de parceiros, ajustado por inflação,
média 2010=100) faz isso **sem** quebrar na troca de moedas pré-1994 (Cruzeiro→Real).

**Com os seus dados.** [#37](pipelines/37_drive_comum.md): o preço recebido
(USD × câmbio, normalizado) é a série-manchete do drive comum; na grade UF, **~7 hits em
~135 testes ≈ acaso**, mas o câmbio é o único driver com **estrutura** — reaparece em duas
margens e passa no placebo de exogeneidade (o reverso dá nulo, como exógeno deve). Bônus da
série: a quebra órfã de 1991 ganhou nome — colapso de crédito do Plano Collor. No painel
AMC ([#38](pipelines/38_drive_comum_amc.md)), câmbio × fronteira → rebanho confirma a
**direção** prevista (com o p de permutação 0,07–0,13 — ver D8). Richards (2012) é a âncora
histórica do mecanismo câmbio→soja.

**O que isso não diz.** O câmbio não é o canal **identificado** — é o candidato com
estrutura que sobrevive ao placebo; o teto de poder está quantificado (**N=38 anos, um
único driver nacional**), e daí para "estabelecido" seria preciso um shifter com variação
espaço-temporal (frete/ferrovia) ou um IV — fio novo, não afirmado.

**Frase pronta.** *"O preço que o produtor recebe soma mundo e câmbio — o REER contorna a
troca de moedas — e o câmbio é o único driver da série com estrutura que sobrevive ao
placebo reverso."*

---

### F4 · iLUC — deslocamento indireto de uso da terra

**O exemplo simples.** A hipótese-mãe: converter pasto em soja no Sul "empurraria" o pasto —
e a mata — para o Norte. Testável: se A empurra B, o passado de A deve ajudar a prever B
(Granger) e o transbordamento espacial deve aparecer com **um sinal específico**. A
hipótese mais favorável ao próprio autor — e por isso a mais importante de testar.

**Com os seus dados.** A Perna 3 negativa: Granger nulo (p=0,97, N≈38 — baixo poder, ver
D1); spillover direcional com **sinal trocado** — θ=−0,16 na régua crua, e **θ<0 em 12/12**
réguas × janelas × desfechos sob o bracket (o p=0,02 da régua crua é o único p<0,05 em
12 — e vira 0,42–0,55 sob a união/SIDRA); Toda-Yamamoto zera as duas direções; e os
placebos do #42 mostram o Norte "liderando" até o pasto do próprio Sul. A refutação se
apóia na **ausência universal da assinatura prevista** (θ>0 nunca aparece em nenhuma
especificação), não num coeficiente isolado.

**O que isso não diz.** **Nunca** dizer "iLUC refutado": o que não apareceu é a assinatura
do **canal intra-estadual testado**; iLUC via mercado de commodities (fora do estado) não
foi testado e não se afirma nada sobre ele. E a simetria honesta do #42 impede o oposto —
o veredito é **sem líder**, não "o Sul lidera".

**Frase pronta.** *"Testei a hipótese que mais me favorecia e a assinatura que ela exige
não aparece em nenhuma das 12 especificações — o canal intra-estadual não se confirma;
sobre iLUC por mercado de commodities, o trabalho não fala."*

---

### F5 · Gradiente Sul→Norte — os "dois Goiáses"

**O exemplo simples.** Um corredor de 600 km com o mesmo mercado chegando com intensidade
diferente em cada trecho: a **posição no eixo** é a exposição — não uma causa que viaja
pelo corredor.

**Com os seus dados.** O gradiente é o fio que costura o trabalho (e o espelho
MATOPIBA = "dois Goiáses" dentro de um só estado,
[`referencial_marcha.md`](referencia/referencial_marcha.md)). Medidas que o sustentam:
lavoura 123–135 km ao sul do pasto (Perna 1); aptidão decrescente Sul 4,69 > Centro 4,47 >
Norte 4,17 ([#52A](pipelines/52_aptidao_edafoclimatica.md) — a premissa virou **medida**,
não assunção); e a fronteira ativa **degrada** o próprio estoque no Norte (aptidão ponderada
do estoque: Norte **−0,12** em 40 anos, Sul estável 4,60→4,61 —
[#57](pipelines/57_remanescente_qualidade.md)). Mas atenção à régua "Confundimento": o
gradiente medido é o do **eixo Sul→Norte** — a aptidão é a régua, não o canal (D28, E3).

**O que isso não diz.** O gradiente **não é o canal** — é o eixo onde um drive comum
encontra exposições diferentes; e "dois Goiáses" é leitura descritiva, não fronteira
política nem tipologia fundiária.

**Frase pronta.** *"O gradiente é onde o mesmo motor encontra terras diferentes: a aptidão
é a régua do eixo, e a latitude é o que sobra na conta quando as duas brigam na mesma
regressão."*

---

### F6 · Carbono — estoque removido × emissão líquida

**O exemplo simples.** Derrubar a mata emite carbono; mas se no lugar entra pasto, parte
dele **volta a morar ali**. A **emissão líquida** desconta o estoque do uso entrante. E
hectares não são intercambiáveis: um hectare de floresta vale, em carbono, 1,6 de savana —
perder pouco da densa pode custar mais que perder muito da rala.

**Com os seus dados.** [#47](pipelines/47_custo_carbono_marcha.md) (densidades do 4º
Inventário Nacional + nota metodológica SEEG, valor de floresta **de Goiás**, sem carbono do
solo, fator 44/12 — D30): a conversão removeu da cobertura natural da ordem de **973 Mt
CO₂e** de estoque; descontado o estoque do uso que entrou, a **emissão líquida é de 833
Mt** (desconto de 14,4%). A **savânica** paga a conta: **573 contra 340 Mt** da florestal —
não por valer mais por hectare, mas por ter perdido **2,6× mais área** (razão 1,69→1,58 com
o desconto). No tempo: o Ato I pagou três quartos (**722 Mt, a 48,1 Mt/ano**; Sul à frente:
275 Mt, 18,3 Mt/ano), o Ato II cai ~5× (9,7 Mt/ano) e o Ato III remove **11,8 Mt/ano** — o
Sul é o que menos remove (1,9). O centróide da perda marcha **+91 km ao norte**; no
acumulado, as três regiões pagam quase igual (Sul 34, Norte 34, Centro 32) — o que
distingue o Sul é ter removido **cedo**. (A soma por atos dá 944 Mt, não 973: as viradas
de período não pertencem a ato algum — diferença de 3%, declarada.)

**O que isso não diz.** "Removido" ≠ "emitido" — a régua do estoque é a exata para os
números por ato; nada aqui é "desmatamento **evitado**" (não há contrafactual). A
convenção do Mosaico é declarada (tratá-lo como pastagem daria 815 Mt — diferença de
convenção, não de fonte); e o carbono do **solo** não entra.

**Frase pronta.** *"973 Mt de estoque removido, 833 de emissão líquida — e a savânica paga
a conta (573 vs 340) porque perdeu 2,6 vezes mais área, não porque valha mais por
hectare."*

---

### F7 · Teto de oferta de terra

**O exemplo simples.** Uma fila de pão: se a cozinha para de assar, a fila para de crescer
**mesmo com mais gente chegando**. Parar de crescer com demanda alta é assinatura de
**oferta**, não de apetite.

**Com os seus dados.** A Perna 4: **no Sul, a fronteira fechou** (estoque a 53% do de 1985,
hazard caindo) **sob demanda no pico** — e a demanda foi atendida trocando de fonte: no Ato
III do Sul, o fluxo pasto→lavoura sobe **+51%** e o acréscimo anual de soja plantada acelera
**244%**, enquanto a abertura de Cerrado novo **cai pela metade** (a distinção importa: 38%
é o crescimento do estoque plantado no estado entre as pontas da janela; 244% é a
aceleração do acréscimo anual no Sul de um ato para o outro). **No estado, a fronteira não
fechou** — resta ~60% do convertível, ela migrou ao norte. E a terra que resta está **97%
desprotegida** (6,35 de 6,56 Mha; Proteção Integral <3%, congelada após 2000 —
[#46](pipelines/46_fronteira_protecao.md)): **o teto é físico, não institucional**. O
mecanismo dentro dele é o #39B (E2): onde a depleção entra no domínio certo, caem as duas
coisas — estoque **e** taxa; e o [#57](pipelines/57_remanescente_qualidade.md) elimina a
alternativa "terra pior": a aptidão do estoque do Sul é a mesma em 1985 e 2024
(4,60→4,61); quem degrada é o Norte (−0,12).

**O que isso não diz.** "Convertível" e "protegido" são **proxies com teto declarado**
(D13/D17 — sem CAR pixel a pixel); e a decomposição não diz **por que** a taxa cai — a
parcela residual reúne propensão, atrito, proteção e troca de fonte. O argumento se monta
por eliminação: a taxa caiu com demanda no pico, o que a derrubou não é falta de
comprador, não é a lei — e a demanda foi atendida de outra fonte.

**Frase pronta.** *"A taxa do Sul caiu com a demanda no pico, e a demanda foi atendida de
outra fonte — pasto já aberto; restrição de oferta é leitura por eliminação, e o teto é
físico: 97% do que resta não tem proteção."*

---

## Parte G — O bolso de frases

A tabela de revisão: um conceito, uma linha. (Repete as frases prontas de cada verbete —
para a véspera da apresentação, não para decorar: o objetivo de cada uma é que você
**lembre do mecanismo**, e a frase é só o gancho.)

| # | Conceito | A frase |
|---|---|---|
| A1 | Pixel/cubo | O pixel de 30 m fotografado 40 vezes; tudo é conta sobre essa pilha de fotos |
| A2 | Mosaico | "Mosaico de Usos" é o classificador dizendo que não sabe — mantém a dúvida dele fora das conclusões |
| A3 | Estoque × fluxo | Estoque é fotografia, fluxo é o filme — só o filme diz quem virou o quê |
| A4 | Censura | Compare as censuras antes das idades — no Sul, 70% das idades são incognoscíveis |
| A5 | Censo × amostra | O censo acabou com o erro amostral, não com a pergunta — a mudança foi de ponderação |
| A6 | AMC | A AMC é o território que não muda de contorno em 40 anos |
| B1 | Centro de massa | "O centro de gravidade está 78 km mais ao norte" — nunca "o pasto subiu" |
| B2 | Bimodalidade | Dois montões = duas histórias (rotação × conversão); ¾ mora dentro das células |
| B3 | Hazard | A conta separa "acabou a terra" de "acabou a vontade" — no Sul, 17/83 |
| B4 | Periodização | As fronteiras vêm dos dados (2001, 2020); nenhuma lei produz quebra |
| C1 | Correlação | r=0,89 valida fontes; r=0,986 entre regressor e regressando é alarme |
| C2 | 1ª diferença | Em nível tudo correlaciona; em diferença sobra quem se move junto de verdade |
| C3 | β | O β diz "associado a"; a distância até "causa" é o desenho |
| C4 | R² | R² de zero pode ser o achado — a pergunta era "tem ligação?" |
| C5 | 2-way FE | Cada município consigo mesmo, cada ano retirado de todos |
| C6 | HAC | Ano não é observação independente — o HAC admite que o ano puxa o ano |
| C7 | Moran | Vizinhos se parecem — sem corrigir, a significância sai emprestada da geografia |
| D1 | p-valor | Reporto o placar (0 de 36; 16 de 16), não adjetivo; p grande com N pequeno é "não sei" |
| D2 | Granger | Precedência preditiva, não causa — e o teste reverso é o detector de mentira |
| D3 | Toda-Yamamoto | Séries que vagueiam correlacionam por acidente; T-Y confere antes de falar |
| D4 | DiD | Sem grupo não-tratado (marcos federais), DiD vira co-movimento, não efeito |
| D5 | sup-F | Quebra em 2001 e 2020 pelos dados; Código Florestal não quebra em lugar nenhum |
| D6 | FDR | 7 acertos em 135 testes é o que o azar entrega — o que conta é sobreviver à correção |
| D7 | Bootstrap | Não são 2000 testes — o mesmo número em 2000 Goiases alternativos; onde a nuvem cruza o zero, "ancorada" |
| D8 | Permutação | Embaralhei o câmbio 38× e o padrão nunca voltou — especificidade, com os números |
| D9 | Jackknife | Tirei cada ano uma vez e o sinal nunca virou |
| D10 | ΔBIC | Com 44 M eventos o BIC pergunta "quanto?", e a resposta é estabilidade, não p |
| D11 | Shift-share | Câmbio nacional × fronteira de 1985 — e o juiz honesto é a permutação do shifter |
| E1 | Bracket | Reporto as duas réguas e a âncora — o que depende da régua, eu digo qual |
| E2 | Domínio | O nulo era um valor fora da escala fazendo papel de zero — tratado, o sinal inverteu |
| E3 | Horse race | Aptidão era a régua, não a resposta — perdeu 62% com a latitude na conta |
| E4 | MAUP | Refeito sem malha, pixel a pixel, moveu 1–2 km — achado da terra, não da malha |
| E5 | IV × placebo | Na malha fundiária procurei instrumento e achei placebo — o teto é físico |
| E6 | Oscilação | Pasto→savana que volta é classificador balançando; só a floresta acumulada é regeneração |
| F1 | Martins | Norte goiano = frente pioneira; tipologia é vocabulário, não teste (p. 32) |
| F2 | von Thünen | O anel prevê a geometria (123–135 km), não o empurrão |
| F3 | REER | Preço recebido soma mundo e câmbio; o câmbio é o único com estrutura + placebo reverso |
| F4 | iLUC | A assinatura exigida não aparece em 12/12 — canal intra-estadual não confirmado |
| F5 | Gradiente | O mesmo motor encontra terras diferentes; aptidão é a régua, latitude é o que sobra |
| F6 | Carbono | 973/833 Mt — e a savânica paga por área (2,6×), não por densidade |
| F7 | Teto de oferta | Taxa caiu com demanda no pico, atendida por pasto já aberto — oferta, por eliminação |

---

> **Última nota, de estudo.** O guia de leitura propõe três frases por método — *o que
> faz, por que aqui, o que NÃO afirma*. Este caderno acrescenta a quarta, que é a que a
> banca realmente testa: **contar a engrenagem com um exemplo na ponta da língua**. Se um
> dia uma dessas miniaturas for citada num texto da dissertação, ela deve ser reescrita —
> miniatura é para falar, não para publicar.