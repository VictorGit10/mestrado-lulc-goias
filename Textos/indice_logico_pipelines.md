# Índice lógico dos pipelines — da tese ao script

> **O que é este documento.** O `pipelines/README.md` lista os pipelines na ordem em que
> **nasceram**; este lista na ordem em que a tese **se sustenta**. É a mesma coleção, lida por
> outro eixo. Entre pelas **4 pernas de evidência** (Parte 4 do
> [`guia_de_leitura.md`](guia_de_leitura.md)) e desça até os scripts.
>
> **Use este documento quando** precisar apresentar o trabalho, preparar a defesa, ou responder
> "por que este pipeline existe?". Use o `pipelines/README.md` quando precisar da ficha técnica
> de um pipeline específico.

---

## Por que os números não estão em ordem lógica (e não vão ficar)

Vale dizer isto de uma vez, para não se re-litigar a cada seis meses.

O número de um pipeline é **identidade, não ordem**. Ele é um handle permanente — aparece em
~1.050 referências cruzadas no `Textos/`, ~200 docstrings de scripts, na memória do projeto e
nas mensagens de commit (`feat(#49,#46)`). Renumerar não criaria ordem; apenas congelaria uma
cronologia diferente no identificador, e apodreceria no dia em que o #51 pertencesse ao meio.

Mas a razão de fundo é outra: **a cronologia é parte da evidência.** O conjunto de pipelines é
um caderno de laboratório, e o valor mais raro deste trabalho é a autocorreção datada — o #40
que derrubou o próprio overclaim no mesmo dia, o #41 que corrigiu o "fogo lidera", o #42 que
voltou para fechar a ponta que o #34 tinha descartado com um aceno, o #50 que testou e
descartou o abate. Reordenar os números apagaria justamente a informação de que essas correções
vieram **depois** — que é o que as torna críveis. O caderno fica em ordem de descoberta; a
apresentação se faz em ordem lógica. São dois documentos, e este é o segundo.

O padrão `#28C` e `#40B` já era a solução certa: **sufixo** para inserir no lugar lógico sem
mexer na identidade.

### A divisão de trabalho entre os cinco documentos

| Documento | Eixo | Responde |
|---|---|---|
| [`pipelines/README.md`](pipelines/README.md) | Cronológico | "O que é o #38 e como rodo?" |
| [`narrativa_pipelines.md`](narrativa_pipelines.md) | Cronológico-narrativo | "Como o trabalho foi construído (tour fase a fase)?" |
| [`guia_de_leitura.md`](guia_de_leitura.md) | Por método | "O que é Toda-Yamamoto e por que usei?" |
| [`ensaio_a_investigacao.md`](ensaio_a_investigacao.md) | Narrativo-ensaístico | "Qual é a *história* do trabalho, e por que ela importa?" |
| **este documento** | **Lógico** | **"O que sustenta a tese, e com que força?"** |

> O **ensaio** é o único feito para ser lido de cabo a rabo, uma vez, como uma história — ele
> funde a cronologia da narrativa, a lógica deste índice e a profundidade do guia num só texto
> corrido. Os outros quatro são obras de consulta.

---

## As três coordenadas

Cada pipeline recebe três etiquetas. Elas não substituem o número — convivem com ele.

**Perna (1–4)** — qual afirmação da tese o pipeline sustenta. Nem todo pipeline tem uma: a
fundação de dados sustenta *todas*, e por isso nenhuma em particular.

**Fase (0–6)** — em que momento da construção nasceu. É a coordenada da
[`narrativa_pipelines.md`](narrativa_pipelines.md).

**Papel** — o que o pipeline *faz*. Esta é a etiqueta que mais falta hoje, porque a lista
numérica plana esconde a pergunta que o leitor mais precisa fazer: *isto é um achado ou um teste
de estresse?*

| Papel | O que significa | Como ler o resultado |
|---|---|---|
| **Coletor** | Traz dado de fora (IBGE, GEE, BACEN, IPEA, Trase, INPE) | Não descobre nada — habilita |
| **Infraestrutura** | Consolida, transforma, padroniza | Não descobre nada — habilita |
| **Cartografia** | Mostra | Descritivo; não testa hipótese |
| **Manchete** | Produz uma afirmação da tese | É o achado. Peça a força da evidência |
| **Robustez** | Testa se uma manchete sobrevive a outra régua | Se passa, a manchete fica; se não, cai |
| **Autocorreção** | Derruba ou refina uma leitura anterior | O resultado mais valioso do conjunto |
| **Validação externa** | Confere contra fonte independente | Credibilidade da base, não achado novo |
| **Extensão** | Novo eixo sobre máquina já existente | Amplia sem mudar conclusão |
| **Superado** | Substituído por peça melhor | Histórico. Não use |

---

# Parte 1 — Entrada pelas 4 pernas

**A afirmação central:**

> Goiás viveu uma **reorganização espacial da produção agropecuária** (1985–2024) —
> intensificação no Sul, fronteira no Norte — coordenada por **forças de mercado comuns** ao
> longo do **gradiente Sul→Norte**, e limitada por um **teto de oferta** de terra convertível — e
> **não** um deslocamento causal de uma região sobre a outra.
>
> ⚠️ **"gradiente Sul→Norte", não "gradiente de aptidão"** — o #56 (19/ago/2026, **D28**) mostrou
> que a aptidão não sobrevive à latitude na mesma regressão. A aptidão é a **régua** com que o
> eixo foi medido (e é boa nesse papel, por ser exógena ao uso da terra); ela **não** é o canal
> identificado. Ver a régua "Confundimento" adiante.

Cada perna abaixo segue a mesma forma: a afirmação, a força, a **manchete** que a faz, a
**robustez** que a defende, a **autocorreção** que a afiou, e o que ela **não** permite dizer.

---

## Perna 1 — O padrão existe

> **Afirma:** toda a fronteira agropecuária marchou ao norte entre 1985 e 2024. A lavoura fica
> **123–135 km** ao sul do pasto/rebanho em *todos* os anos. A vegetação natural ficou ancorada.
>
> ⚠️ **A faixa era escrita "~120–130 km" e a série dá 122,6–135,0** (10 dos 40 anos caíam fora,
> inclusive 2024, cujo valor 135 km o próprio texto citava adiante). Corrigido em 19/ago/2026.

**Força: forte.** É a perna mais bem defendida do trabalho — sobreviveu a teste de malha, de
desagregação e de quantificação de incerteza.

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete** | **#32** `centro_massa.py` | Centro de massa por ano e classe (mean center + median center de Weiszfeld + elipse de desvio-padrão), EPSG:5880, sobre as 166 AMCs. Pastagem **+78 km**, rebanho **+67 km**, agricultura **+65 km** |
| **Robustez** | **#43** `centro_massa_pixel.py` | Refaz pixel-a-pixel, **sem malha administrativa**. O MAUP não é problema prático: pasto +79,2 vs +78 km, agric +66,9 vs +65 km |
| **Robustez** | **#35** `robustez_janelas.py` | Três réguas de tempo (atos, grade de 5 anos, décadas). O pasto marcha ao norte em todas |
| **Autocorreção** | **#44** `centro_massa_desagregado.py` | Abre os *lumps*. A "muralha norte" é **a floresta**, não a vegetação inteira — o campo nativo recuou +35 km. Controles limpos: área urbana parada, leite ancorado |
| **Autocorreção** | **D19** (dentro do #32) | Bootstrap de AMCs (B=2000): todo ΔNorte agora vem com IC95%. **A vegetação (+7,6 km) inclui zero** — é "ancorada", não "moveu +8 km" |

**O que esta perna NÃO permite dizer:** que o centro de massa explica *por que* a fronteira
marchou — é uma descrição, não um mecanismo (isso é a Perna 2). E um centro de massa é uma
**média**: foi exatamente essa cegueira que o #44 corrigiu ao abrir a vegetação em três
formações.

**Ler a fundo:** [`32_centro_massa.md`](pipelines/32_centro_massa.md) →
[`43_centro_massa_pixel.md`](pipelines/43_centro_massa_pixel.md) →
[`44_centro_massa_desagregado.md`](pipelines/44_centro_massa_desagregado.md)

---

## Perna 2 — O mecanismo local

> **Afirma:** são **dois mecanismos geograficamente segregados**. No Sul, `pasto→lavoura`
> (intensificação). No Norte, `mata→pasto` (fronteira).

**Força: moderada** (rebaixada de "forte" em 25/jul/2026 — ver a caixa abaixo) — com **três**
ressalvas que a autocorreção impôs. (1) A geografia desloca o **peso** da mistura, não **causa** os
modos (#28C). (2) 🛑 **A segregação é do *tipo* de transição, não da *idade* do pasto** — a
qualificação "sobre pasto jovem no Sul (~9a) / antigo no Norte (~20a)", que esta perna afirmava até
23/jul/2026, **caiu** na auditoria da mudança de rótulo (#40, #28C e #33, por três caminhos
independentes). (3) O canal de **intensificação** do #49 (M1) é **frágil ao bracket D26** — o
intervalo atravessa o zero e a âncora SIDRA dá o sinal oposto; quem sustenta a perna no painel
espacial é a **substituição** (M3), não a intensificação. O que resta de pé são medidas **imunes**:
o `veg→pasto` (que não passa pelo Mosaico), a **bimodalidade** e os centroides do #32/#44.

> 🛑 **Por que "moderada" e não "forte" (25/jul/2026).** O rótulo "forte" foi herdado de uma versão
> da perna que afirmava **três** coisas: coexistência de dois modos, gradiente latitudinal de idade
> e tendência temporal de w₁. As duas últimas caíram (#28D/#40/#28C/#33), e o eixo temporal está
> **suspenso** dos dois lados. Sobra a **coexistência** — que é robusta (5/5 regiões, 10/10 células
> sob a união), mas é **uma** afirmação, não três. A perna continua defensável; o que mudou é
> quanto ela carrega. Ver também a nota de refutação ao final desta seção.

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete** | **#33** `transicoes_regionais.py` | Recorta as conversões brutas por mesorregião × ato. `veg→pasto` é a transição-mãe pervasiva; `pasto→agric` só *lidera* no Sul+Centro no Ato II. O deslocamento aparece no **balanço líquido** (Ato II, janela limpa). ⚠️ **Os dois achados do Ato III caíram** (`transicoes_regionais_bracket.py`, 25/jul): a queda de −88% do `pasto→agric` **inverte para +51%** sob o bracket, e a tabela de idade **inverte a ordenação** (Sul 16a→32a, Norte 27a→23a) |
| **Manchete** | **#28** `coleta_idade_pastagem.py` + `analise_reserva_terra.py` | A idade do pasto na conversão é **bimodal** (~4 e ~23 anos) = dois mecanismos coexistindo. Censo: 44,6 M eventos |
| **Manchete** | **#22** `correlacoes_painel.py` | Painel 2-way FE: a **substituição local** é forte (onde a lavoura entra, o pasto sai *localmente*) e o SICOR é o canal dominante de retração — **na janela com SICOR (2013–2021), ~8 anos**, não nos 40 |
| **Robustez** | **#22B** `intensificacao_vs_composicao.py` | O β<0 de `Δ Agric ~ Δ VA agro` é **intensificação within** ou **composição entre municípios**? **Within** (27/jul): sob **FE de grupo × ano** — que fecha o canal da composição *dinâmica*, o que o FE de entidade não faz — o β se move só **+2,4% a +14,1%** e mantém p<0,001; **24/24 subamostras negativas**. ⚠️ Não revoga a **dependência de medida** do #49/D26 (a soja SIDRA extensifica): são ressalvas independentes |
| **Autocorreção** | **#40** `duas_logicas_pastagem.py` | Espacializa as duas lógicas (Rotação no Sul × Oportunístico no Norte). **Derrubou o próprio overclaim no mesmo dia** → **D14**. Em 21/jul/2026 **derrubou também a autocorreção**: o "some sob o gradiente 2D" era erro de medida; veredito vira *não estabelecido*, e a comparação estrutura×fluxo (agora simétrica) dá o sinal ao **fluxo** |
| **Autocorreção** | **#28C** `bimodalidade_regional.py` | A bimodalidade é *regionalmente causada*? **Não.** A região explica 1,3% (meso) / 7,5% (AMC); o tempo explica 19,6%; **75–79% mora dentro** das células. Sob censo ω²/permutação degeneram (D23) — sustenta-se por estabilidade censo×amostra, não por p |
| **Autocorreção** | **#40B** `duas_logicas_calcario_orientacao.py` | Generaliza a D14: calcário e orientação somem sob o gradiente 2D — e no censo (n=244) o nulo **se confirma**. Ressalva de 21/jul/2026: a generalização vale para eles, **não** para toda covariável (no-till virou limítrofe; adubação dá p=0,003) |
| **Autocorreção** | **#28D** `deriva_mosaico_fim_serie.py` | 🛑 **A mais severa da perna.** O objeto do #28 **não é constante na série**: a saída da pastagem migra do rótulo "agricultura" para "Mosaico de Usos" (razão 0,6 em 2015 → **32,5 em 2024**; `P→agric` cai 92%) enquanto o **SIDRA registra a soja +38%**. Derruba a tendência de w₁; sobrevive a **bimodalidade**, **não** o gradiente de idade (revisto 23–25/jul) → **D25/D26** |
| **Robustez** | **#49** `painel_espacial_dinamico.py` | Os canais do #22 sobrevivem ao termo espacial (Elhorst FE lag/error) — **mas os dois modelos recebem vereditos opostos sob o bracket D26**: **M3 (substituição) é ROBUSTO** (β<0 nas três réguas e nas duas janelas; a mudança de rótulo apenas *subestimava* — o β≈−0,5 é **piso**), enquanto **M1 (intensificação) é FRÁGIL** (o bracket **atravessa o zero** e a âncora SIDRA dá o **sinal oposto**: a soja *extensifica* onde o VA agro cresce). Reportar M1 como **intervalo**, nunca como canal de sinal único |

**O que esta perna NÃO permite dizer:** que "a região causa a bimodalidade" (o #28C mediu: não
causa), que "plantio direto explica a idade do pasto" (o #40 derrubou: era confundidor de
latitude), nem — desde 21/jul/2026 — que **"o pasto jovem vem ganhando peso ao longo do tempo"**
(o #28D derrubou: a tendência de w₁ acompanha a mudança do rótulo de classificação, e o contraste
"tempo ≫ espaço" está **suspenso** porque os dois lados do eixo temporal estão comprometidos —
horizonte antes de 2020, mudança de rótulo depois). E — desde 23–25/jul/2026 — que **"o Sul
converte pasto jovem e o Norte pasto velho"**: o gradiente latitudinal de idade caiu no #40, no
#28C e no #33. Nem — desde 25/jul/2026 — que **"a intensificação é um canal robusto do painel
espacial"**: o M1 do #49 depende da medida de "agricultura" (bracket cruza o zero; SIDRA inverte o
sinal). O canal robusto do #49 é o **M3, substituição local**.

> 🛑 **Uma frase deste índice foi refutada e vale registrar o porquê.** Até 23/jul dizia-se aqui
> que "gradiente regional no *peso* da mistura" sobrevivia **"porque é transversal"**. O
> raciocínio está **errado**: a mudança de rótulo não é apenas temporal — ela decide *quais
> conversões continuam visíveis* como "agricultura", e essa seleção age **dentro** de um mesmo
> período. Comparar regiões no mesmo ano não protege de um viés que muda **quem entra na
> amostra**. O que de fato sobrevive é a **bimodalidade/coexistência** (robusta sob a união:
> 5/5 regiões, 10/10 células) — não a ordenação Sul→Norte das idades.

**Ler a fundo:** [`33_transicoes_regionais.md`](pipelines/33_transicoes_regionais.md) →
[`28_idade_pastagem.md`](pipelines/28_idade_pastagem.md) →
[`40_duas_logicas_pastagem.md`](pipelines/40_duas_logicas_pastagem.md) →
[`28C_bimodalidade_regional.md`](pipelines/28C_bimodalidade_regional.md) →
[`28D_deriva_mosaico.md`](pipelines/28D_deriva_mosaico.md)

---

## Perna 3 — Reorganização coordenada, não deslocamento causal

> **Afirma (o negativo, forte):** a hipótese-mãe — *a lavoura do Sul empurra o pasto para o Norte*
> (iLUC intra-estadual) — foi **testada e refutada no canal testado**. A precedência temporal não
> aparece (Granger nulo, **mas de baixo poder** — N≈38); e o spillover direcional, onde estimável,
> saiu com o **sinal oposto** ao previsto em **todas** as especificações testadas (θ<0 em 12/12
> réguas × janelas × desfechos; auditoria da deriva, 28/jul/2026). A refutação se apoia na
> **ausência universal da assinatura prevista** (θ>0 nunca aparece), não num coeficiente
> isolado: o p=0,02 do θ=−0,16 é da régua exposta e **não sobrevive ao bracket D26**.
> **Afirma (o positivo, corroborante):** o que coordena os dois mecanismos e dá o **compasso
> temporal** da marcha é um impulso **macro comum**, com o câmbio real (REER) como candidato mais
> forte — mas isso é **corroborante, não estabelecido**.

**Força: forte no negativo, corroborante no positivo.** O negativo (um nulo bem defendido) é a
perna que dá credibilidade ao trabalho inteiro — foi o autor quem perseguiu a hipótese que mais o
favoreceria e a derrubou. O positivo é a parte mais fraca: sob a inferência correta (permutação do
shifter, #54) o achado-manchete do drive comum sai de p~0,03 para ≈0,07–0,13 (não significante a
5%); o que o sustenta é a **especificidade** (placebos nulos, sem antecipação, jackknife estável),
não a significância.

> **Por que uma perna só** (antes de jul/2026 eram as pernas 3 e 4 separadas). O negativo abre a
> pergunta "então o que é?"; o positivo a responde — *reorganização coordenada por um drive macro
> comum, não causação local*. Uni-los mantém cada metade honesta sobre o que carrega e evita tratar
> o drive comum como um pilar independente que ele (ainda) não é. Fundidas quando o #54 calibrou a
> significância do drive comum para baixo.

**O negativo — não é deslocamento causal (forte):**

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete (nulo)** | **#34** `deslocamento_espacial.py` | O teste formal, em **tempo contínuo**. (a) Sem precedência: Granger ΔAgric_Sul → ΔPasto_Norte **p=0,97** (nulo de **baixo poder** — N≈38; poder ~48% p/ efeito moderado, ~93% p/ grande, sim. Monte Carlo). (b) Spillover direcional de **sinal trocado**: θ=−0,16 (p=0,02) na régua crua — mas o **bracket D26 (28/jul) mantém o sinal (12/12 negativo) e derruba a significância** (p<0,05 em 1/12; 0,42–0,55 sob união/SIDRA). (c) Substituição local forte: β=−0,52, **robusta nas 3 réguas** (−0,52 crua / −1,14 união / −0,07 SIDRA, p<0,001) |
| **Autocorreção** | **#42** `granger_reverso_norte_sul.py` | **A peça-modelo do conjunto.** O #34 deixou uma ponta: o teste *reverso* deu p=0,0007 — que, se real, inverteria a tese. O #42 provou que é **regressão espúria**: `pasto_Norte` é I(2), `agric_Sul` é I(0), ordens diferentes nem cointegram; **Toda-Yamamoto zera as duas direções**; e os **placebos** mostram que o Norte "lidera" até o pasto do próprio Sul → **D16** |
| **Extensão + Autocorreção** | **#45** `analise_trase_lulc.py` | Terceiro canal a confirmar co-evolução sem líder: a cadeia exportadora **não lidera** (0/3 termos defasados sobrevivem à robustez) **nem co-move materialmente**. Em jul/2026 derrubou o próprio achado-manchete ao descobrir que o regressor era produção disfarçada (β +0,335 → +0,037) |
| **Extensão** | **#53** `centro_massa_capacidade.py` | Fecha a ressalva do #45 pelo lado da **capacidade instalada**: o centroide da capacidade de armazenagem (CONAB) é a camada **mais ao sul de todas** (~150 km ao sul do pasto, ~83 km ao sul até do crédito) — a infraestrutura física **consolida o núcleo, não lidera**. Metade "silos"; a "frigoríficos" segue sem dado |
| **Adjacente** | **#41** `fogo_lidera_fronteira.py` | O fogo é vanguarda **geográfica** (ao norte da conversão em 39/39 anos) mas **não lidera no tempo** — coerente com o veredito de co-evolução |

**O positivo — o drive comum coordena o tempo (corroborante, não estabelecido):**

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete (fraca)** | **#37** `coleta_drivers_macro.py` + `drive_comum.py` | Testa o drive comum na série UF/anual (N≈38). **~7 hits em ~135 testes ≈ acaso; nada sobrevive à correção de multiplicidade.** Só o **câmbio** tem estrutura (reaparece em duas margens). Passa no placebo de exogeneidade. Bônus: a quebra órfã de 1991 ganha nome — colapso de crédito do Plano Collor |
| **Manchete (fraca)** | **#38** `drive_comum_amc.py` | Muda a unidade para o painel AMC (~6.600 obs) e testa **driver × exposição baseline**. A hipótese confirmatória `câmbio × fronteira → rebanho` confirma a **direção**, mas a grade exploratória (144 testes) **não devolve nenhum sobrevivente do FDR** — e o `p=0,031` é o SE **clusterizado**: sob permutação do shifter (#54, **D20**) vira **≈0,07–0,13, n.s. a 5%**. A área LULC é **nulo robusto** |
| **Extensão (identificação)** | **#52** `aptidao_edafo_exposicao.py` + `aptidao_edafo_drive38.py` | Troca o proxy de área do #38 por uma aptidão edafoclimática **exógena** (Embrapa 1:500k, WFS). **52A**: a aptidão física **reproduz** o gradiente Sul→Norte (r_lat=−0,44; Sul 4,69>Centro 4,47>Norte 4,17) — a premissa vira **medida**, não assumida; correlação **moderada** (+0,30) com a exposição do #38 = carrega info própria. **52B**: o achado do #38 reaparece **sem a complementaridade mecânica** (câmbio×aptidão→rebanho **β=−0,033**; o `p=0,026` é clusterizado — sob permutação, **≈0,07–0,13, n.s. a 5%**, D20) e a grade honesta de 192 devolve **2 sobreviventes do FDR** — mas via a **mesma fragilidade de tamanho de família** do Achado #2 do #38. Fortalece a **identificação**, não o poder |
| **Endurecimento (inferência)** | **#54** `defensabilidade_perna4.py` | **Opção B — nomeia o desenho como shift-share e roda a inferência correta.** A **permutação do shifter** (câmbio embaralhado, aptidão fixa) revela que o SE clusterizado do #38/#52 era **otimista**: o p do achado-manchete sai de ~0,03 para **≈0,07 (naive) a 0,13 (rotação circular) = não significante a 5%** (o β *within* reproduz o PanelOLS; só o p muda). Em troca, a **especificidade** segura o padrão: **placebos nulos** (câmbio×aptidão→urbano/água, p>0,24), **lead limpo** para o headline exógeno (p=0,11), **jackknife estável** (sinal 100%, nenhum ano isolado). Menos significante, mais defensável |
| **Extensão** | **#50** `centro_massa_economico.py` | O centroide do **crédito** fica ~75 km **ao sul** da pastagem: o crédito **consolida a massa instalada, não lidera a fronteira** — o que *casa* com o crédito ser endógeno (#37/#38) |
| **Extensão** | **#51** `crescimento_sem_desenvolvimento.py` | Põe um **número** no "crescimento sem desenvolvimento" do #50 (IFDM 2013–2023): a fronteira **Norte quase dobra a área** (+93% vs +14% no Sul) mas ganha desenvolvimento **igual** ao Sul e fica **−0,08 abaixo** (robusto, invariante município↔AMC); a **expansão de área é desacoplada** do desenvolvimento (r≈0, painel r²within≈0), o VA agro tem dividendo modesto (r=0,21). Reabre o fio descartado por falta de dado |

**O que esta perna NÃO permite dizer.** No **negativo**: que o iLUC **não existe** em Goiás —
afirma-se que o **canal intra-estadual testado** não se confirma; e a simetria honesta do #42
(Toda-Yamamoto zera as duas direções) também impede reivindicar que "o Sul lidera" → o veredito é
**sem líder**. No **positivo**: que o câmbio **causa** o gradiente, nem que ele é
**estatisticamente significante** — a redação **não** deve reportar "p=0,026/0,031" como
significância; deve reportar o **p de permutação** (≈0,07–0,13) e chamar o drive comum de
**corroborante**. Dois refinamentos sustentam a honestidade do positivo: o **#52** (identificação —
troca o proxy de área por uma aptidão exógena e tira a objeção de complementaridade mecânica) e o
**#54** (inferência — a permutação do shifter mostra que o SE clusterizado era otimista para um
shift-share de um só shifter nacional; o que segura o padrão é a **especificidade**, não a
significância).

O **teto de poder temporal** está agora **quantificado**: N efetivo = **38 anos**, um único driver
nacional. Nenhuma exposição melhor ou mais AMCs o levantam (o #52 mostrou; o #54 mediu). Sair de
"corroborante" para "estabelecido" pediria a **opção (A)** — um shifter com variação
espaço-temporal (frete/ferrovia, choque climático) ou um IV para o câmbio, que é **fio novo**.

**Ler a fundo:** o negativo — [`34_deslocamento_espacial.md`](pipelines/34_deslocamento_espacial.md) →
[`42_granger_reverso_norte_sul.md`](pipelines/42_granger_reverso_norte_sul.md); o positivo —
[`37_drive_comum.md`](pipelines/37_drive_comum.md) →
[`38_drive_comum_amc.md`](pipelines/38_drive_comum_amc.md) →
[`52_aptidao_edafoclimatica.md`](pipelines/52_aptidao_edafoclimatica.md) →
[`54_defensabilidade_perna4.md`](pipelines/54_defensabilidade_perna4.md)

---

## Perna 4 — O teto de oferta

> **Afirma:** o Sul bateu no estoque de Cerrado convertível; o Norte ainda tem. A desaceleração
> do Sul ocorreu **sob demanda forte** — assinatura de restrição de **oferta**, não de demanda
> fraca. E a terra que resta está **97% desprotegida**: o teto é **físico, não institucional**.

**Força: forte no diagnóstico**, com proxy declarado (D13/D17).

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete** | **#39** `fronteira_fechando.py` | Veredito **escalonado**: no estado a fronteira **não** fechou (resta ~60%; só **migrou ao norte**); **no Sul fechou** (estoque a 53% de 1985, hazard caindo). A decomposição `Δfluxo = h̄·Δestoque + estoquē·Δhazard` separa "acabou a terra" de "acabou a vontade" → **D13** |
| **Extensão** | **#46** `fronteira_protecao.py` | Adiciona a camada que o #39 deixou de fora. **97% do convertível remanescente (6,35 de 6,56 Mha) está desprotegido**; a Proteção Integral cobre <3% e congelou após 2000 → **D17** |
| **Validação externa** | **#48** `validacao_prodes_mapbiomas.py` | Valida a base de perda de vegetação contra o **PRODES/INPE**: no regime anual 2013–24 as fontes concordam (**r=0,91**). Fecha a pendência PRODES da D17 |
| **Extensão** | **#47** `custo_carbono_marcha.py` | O **custo** da marcha: ~**973 Mt CO₂e** (849 só com biomassa; faixa de **escopo**, não de incerteza). Densidades do **4º Inventário Nacional**, com valor de floresta específico de Goiás (**D30**, 20/ago/2026 — substitui a D18). A **savânica domina a emissão** (573 × 340 Mt): ela perdeu 2,6× mais área, e isso mais que compensa valer menos por hectare. O centróide da perda marcha +91 km ao norte — amarra com o #39 |

**O que esta perna NÃO permite dizer:** que se conhece o estoque **cadastral**. "Terra
convertível" e "proteção" são **proxies com teto** declarados (D13/D17) — MapBiomas + malha
vetorial de UCs, sem CAR pixel a pixel.

**Ler a fundo:** [`39_fronteira_fechando.md`](pipelines/39_fronteira_fechando.md) →
[`46_fronteira_protecao.md`](pipelines/46_fronteira_protecao.md) →
[`47_custo_carbono_marcha.md`](pipelines/47_custo_carbono_marcha.md)

---

# Parte 2 — A família do centro de massa (caso demonstrativo)

Esta família é a prova de que **o papel importa mais que o número**. Na linha numérica os quatro
pipelines estão espalhados (32… 43, 44… 50) e parecem avulsos. Lidos por papel, são uma coisa
só: **uma manchete e as três peças que a defendem e a estendem.**

```
#32  centro_massa.py            MANCHETE     A figura-manchete da tese
 │                                           pasto +78 km · rebanho +67 · agric +65 · veg ancorada
 │
 ├─ #43  centro_massa_pixel.py       ROBUSTEZ     "É artefato da malha (MAUP)?"
 │                                                Não → pixel-a-pixel bate a ~1-2 km
 │
 ├─ #44  centro_massa_desagregado.py AUTOCORREÇÃO "O que a média esconde?"
 │                                                A "muralha norte" é a floresta, não a vegetação
 │                                                Soja não lidera · urbano parado · leite ancorado
 │
 ├─ #50  centro_massa_economico.py   EXTENSÃO     "E o dinheiro, marcha junto?"
 │                                                Crédito ~75 km ao SUL · valor ancorado
 │                                                Abate TESTADO E DESCARTADO (circular)
 │
 ├─ #53  centro_massa_capacidade.py  EXTENSÃO     "E a capacidade física (silos)?"
 │                                                A camada MAIS ao sul de todas: ~150 km ao
 │                                                sul do pasto, ~83 km ao sul até do crédito
 │                                                Fecha a metade "silos" da ressalva do #45
 │
 └─ D19  bootstrap_incerteza()       AUTOCORREÇÃO "Qual a incerteza de cada ΔNorte?"
                                                  IC95% por bootstrap → veg inclui zero
```

**Por que esta leitura só aparece aqui.** Renumerar para deixá-los adjacentes (32/33/34/35)
daria a mesma adjacência — **ao custo de apagar que #43, #44 e #50 nasceram depois**, como
trabalho defensivo e de extensão. Que o #43 tenha vindo 11 números depois do #32 *é a
informação*: significa que a manchete foi publicada, a objeção do MAUP foi levantada, e o autor
foi atrás dela. A etiqueta de papel dá a adjacência de graça e preserva a data.

**Os "centroides extras", explicitamente.** Além das 4 classes-manchete do #32 (pastagem,
agricultura, rebanho, vegetação natural), a família produziu:

| Centroide | Pipeline | O achado |
|---|---|---|
| Soja isolada (raster e SIDRA) | #44 | **Não lidera** o lump agrícola — está colada a ele (±5 km) porque o *domina*. A manchete do #32 é a geografia da soja. Valida raster×SIDRA (r=0,89) |
| Floresta / campo nativo / savânica | #44 | A "muralha" é só a **floresta** (+9 km). Campo nativo **+35 km** (IC largo), savânica +12 km (inclui zero) |
| Área urbana | #44 | **Parada** (ao sul) — placebo limpo: a marcha ao norte não é deriva genérica |
| Leite × corte | #44 | Leite ancorado ao sul (+30 km) vs boi (+67 km): o vão **dobra**. É o **corte** que marcha |
| Crédito custeio × investimento | #50 | Ambos ~75 km ao sul do pasto. O **investimento é ~27 km ao norte do custeio** (capex inclina à fronteira) |
| VA agropecuário / PIB | #50 | **Ancorados** enquanto a área marcha → o vão valor↔pasto **alarga** (−84 → −101 km). É "crescimento sem desenvolvimento na ponta" **sem precisar de IDH-M** |
| Abate bovino | #50 | **Descartado.** É modelado do rebanho (`abate=(rebanho_muni/rebanho_UF)×abate_UF`) → centroide idêntico por construção. Comparação circular |
| Capacidade de armazenagem | #53 | A **mais austral** de todas (−17,24°): ~150 km ao sul do pasto, **~83 km ao sul até do crédito**, colada à lavoura (−16 km). Fecha a metade "silos" da ressalva do #45 — a capacidade física consolida, não lidera |
| Fogo em vegetação | #41 | Vanguarda **geográfica**: ao norte da conversão em 39/39 anos (+73 km) |
| Perda de carbono | #47 | Marcha +91 km ao norte |

---

# Parte 3 — A fundação (as pernas que não são pernas)

Estes pipelines não aparecem em nenhuma perna porque sustentam **todas**. Eles não descobrem —
**habilitam**. Um leitor que quer entender a tese pode pular; um leitor que quer *confiar* nela,
não.

### Coletores (Fase 1) — de onde vêm os números

| # | Script | Fonte |
|---|---|---|
| #3 | `coleta_sidra.py` | IBGE/SIDRA — 8 tabelas municipais (lavouras, rebanho, leite, PIB/VA, população, IPCA) |
| #4 | `pipeline_municipal.py` | MapBiomas Col. 10.1 municipal — **a espinha dorsal** |
| #6 | `coleta_sicor.py` | Crédito rural SICOR/BACEN (2013–2026) |
| #7 | `coleta_sidra.py --censo-agro` | Censo Agropecuário 2017 (plantio direto, calcário, orientação) |
| #13 | `coleta_idhm.py` | IDH-M via IPEA (1991/2000/2010 — **não existe pós-2010**) |
| #14 | `fogo_mapbiomas.py` | Área queimada × LULC via GEE |
| #14B | `verificacao_fogo_nivel.py` | Verifica o **nível** do #14: 3 das 4 hipóteses da lacuna vs o Fire Dashboard **rejeitadas**; o valor de 2020 é estável entre 2 recortes e 3 coleções |
| #15 | `analise_safrinha.py` | Milho 1ª/2ª safra |
| #27 | `coleta_trase.py` | Cadeia produtiva Trase — soja e boi (dormente até o #45). ⚠️ "só exportação" vale para o boi, **não para a soja** (44,6% é esmagamento doméstico) |

### Infraestrutura (Fases 2–3) — as tabelas-mãe

| # | Script | O que entrega |
|---|---|---|
| #12 | `transicoes_mapbiomas.py` | **A virada metodológica**: matriz de transição **pixel-a-pixel**, não inferida de estoques. Substitui o #5. ⚠️ 6 grupos — **mascara a classe 21**, superado pelo #12B |
| #12B | `transicoes_cubo.py` | **A mesma matriz, honesta**: recontada no cubo censitário local com o **Mosaico como 7º grupo**. O #12 descartava 6,5–10,9% de Goiás todo ano — a rota `pasto→Mosaico` sumia do numerador *e* do denominador. É esta a matriz primária desde 27/jul/2026 |
| #19 | `agregar_conversoes.py` | Conversões brutas ano-a-ano (39 pares) — insumo de #29c, #31, #33 |
| #16 | `construir_painel_unificado.py` | Painel `cd_mun × ano` (9.840 × 185). **Trilho transversal** |
| #25 | `construir_amc_goias.py` | 166 AMCs de território constante (D11). **Trilho longitudinal** — o palco da Fase 6 inteira |
| #17 | `calcular_taxas_lulc.py` | O motor de taxas (delta, slope, HAC, aceleração). A peça mais reutilizada do projeto |
| #18 | `mapeamento_mesorregioes.py` | `cd_mun` → mesorregião IBGE 2017 (D6) — o que torna possível a leitura Sul→Norte |
| #29 | `periodizacao_*.py` | **A régua temporal.** Triangulação de 3 métodos → os três atos, congelados em `config_periodos.py` |

### Inferência (Fase 4) — a escada de exigência

| # | Script | Papel | O achado |
|---|---|---|---|
| #21 | `correlacoes_uf.py` | Manchete fraca | Correlações UF em 1ª diferença + HAC (D7). N pequeno, sem controles |
| #22 | `correlacoes_painel.py` | Manchete | **O cavalo de batalha** — 2-way FE (D8). Intensificação robusta; SICOR dominante (na janela 2013–2021) |
| #22B | `intensificacao_vs_composicao.py` | Robustez | Fecha a ambiguidade **intensificação × composição** do #22 com FE de grupo×ano: o sinal é **within** |
| #23 | `piecewise_did.py` | Manchete (nulo) | **Só `Vegetação × 1995 vs TO` sobrevive** a parallel-trends + placebo. O Código Florestal não. ⚠️ **Rebaixado a *sensibilidade de co-movimento* em 25/jul/2026**: os 4 marcos são **federais**, então não há grupo não-tratado — nem o par sobrevivente identifica efeito causal, só exposição diferencial |
| #24 | `analise_espacial.py` | Diagnóstico | **115 de 140 resíduos** têm Moran's I significativo → o espaço é estrutural |
| #26 | `deteccao_quebras.py` | Manchete | Quebras data-driven: **2001 (F=62,2)** e **2020 (F=21,5)**. O Código Florestal **não produz quebra** |

### Robustez transversal — as réguas

O trabalho testa cada manchete em eixos independentes. Vale saber nomeá-los:

| Régua | Pergunta | Pipelines | Decisão |
|---|---|---|---|
| **Tempo** | Depende de onde cortamos? | #35 (fronteira), #36 (resolução) | D12 |
| **Latitude** | É efeito próprio ou gradiente? | #40, #28C, #40B | D14 |
| **Integração** | O Granger é espúrio? | #42 | D16 |
| **Espaço** | Sobrevive à autocorrelação? | #49, #43 (MAUP) | — |
| **Incerteza** | Qual o IC? | D19 (#32/#44/#50) | D19 |
| **Incerteza sob vizinhança** | O IC i.i.d. é estreito demais? | **#55** | D19 |
| **Confundimento** | O gradiente é da variável ou do eixo? | **#56** | **D28** |
| **Domínio** | A variável respeita o intervalo que a define? | **#39B** | **D29** |

#### As três réguas acrescentadas em 19/ago/2026

Nasceram da leitura crítica do texto de qualificação, e as três atacam o mesmo
tipo de defeito: uma régua que o trabalho aplicava a um resultado e não aplicava
a outro.

| Onde | Script | O que achou |
|---|---|---|
| **#55** | `robustez_bootstrap_bloco.py` | O IC da D19 reamostra as 166 AMCs **uma a uma**, enquanto o #41 documenta I de Moran significativo em 125/140 testes e ρ/λ de 0,35–0,56: o bootstrap i.i.d. é **incoerente com o diagnóstico do próprio trabalho**. Refeito com **blocos espaciais** (k-means, grade de 166 a 12 blocos), o IC alarga como esperado (pastagem: 45 → 80 km de largura) e **o veredito não muda em nenhum tamanho de bloco** — 3 robustos + vegetação ancorada, 6/6. **A Perna 1 fica mais forte, não mais fraca.** Achado lateral: a **componente leste**, que o texto nunca reportava, é robusta sob i.i.d. (agricultura +49,5 km, azimute 37°) e é a **primeira a cair** sob blocos ≥8 AMCs |
| **#56** | `drive_horse_race_latitude.py` | **O achado que dói.** Os placebos do #54 são todos de *desfecho* — nenhum pergunta se a *share* é a certa. Posta a **latitude** na mesma regressão (r=−0,44 com a aptidão: moderada, não colinear), a aptidão **perde 62% da magnitude** (β −0,033→−0,012) e a significância nas **duas** réguas (p_agrup 0,026→0,30; p_circ 0,13→0,47) enquanto a latitude quase não se move (β +0,051→+0,046; p_circ 0,053). Sozinha, a latitude é **a única exposição que cruza 5% sob permutação circular** (p=0,026). ⚠️ Esse **0,026 é o PISO do teste**: com 38 realizações do shifter, 1/38 é o menor p que a permutação pode devolver — significa "nenhuma rotação superou o observado", o melhor desfecho possível, **não** margem folgada (o 0,053 do S4 é decidido por *uma* rotação). A D28 não depende disso: ela se apoia na aptidão **perder** significância, não na latitude ganhá-la. ⇒ **D28**: o gradiente medido é o do **eixo Sul→Norte**, e a aptidão é a régua, não o canal. O argumento da Perna 3 (reorganização coordenada, não empurrão) **sobrevive intacto**; o que cai é a atribuição a solo/clima |
| **#39B** | `fronteira_fechando_39b.py` | **Achado ao auditar a própria auditoria.** O B2b do #39 (`hazard ~ depleção`) publicava **nulo** (β=−0,015; p=0,48), e a redação o usava como a peça empírica da Perna 4. O nulo é artefato: `deplecao_prev` é documentada como fração **0..1** e no arquivo vai a **−84,9**, em **920 dos 6.379 pares (14%)**, de 46 AMCs com estoque de 1985 minúsculo (mediana 544 ha × 24.031 ha) cujo estoque de savana/campo *cresceu* — a oscilação pasto↔savana vista pelo estoque. Z-scorada, a coluna passa a ser definida por esses valores. **Tratado, o sinal inverte e é robusto**: grade fatorial de **16 células** (4 tratamentos × com/sem ponderação pelo estoque × 2 amostras), β<0 nas 16 e p<0,05 em 11 **sob a régua do próprio #39** (cluster entidade+ano — a régua não se troca no meio da conferência). A única célula que não cruza em nenhuma das duas amostras é a **publicada**, que não trata nem o regressor (domínio) nem o desfecho (denominador minúsculo). Onde o regressor entra no domínio, os tratamentos **convergem em unidade natural**: ≈ **0,5 a 0,8 ponto percentual de taxa anual a cada 0,1 de depleção**, R²w de ~0 para 0,05–0,20. ⚠️ Os β **em z não são comparáveis entre tratamentos** (o sd do regressor varia 17×: 0,21 no domínio × 3,54 sem tratamento) — a faixa "−0,07 a −0,31" que circulou até 20/ago comparava réguas de tamanhos diferentes. ⇒ **D29**. **A Perna 4 sai FORTALECIDA**: sai de uma premissa apoiada em nulo fraco para mecanismo medido (na depleção caem *as duas coisas*, estoque e taxa). Casa com o #57 e resolve a tensão do "residual não é demanda" — parte do residual agora tem nome. Não muda: B1 segue identidade, quadrático segue nulo. **Muda para menos**: o B2a (hazard ~ estoque) **não** cruzava 5% na versão publicada (β=−0,3194; **p=0,0917**, e não 0,002 — este vinha da régua frouxa) e some sob o corte de 1.000 ha (β=−0,057; p=0,74), porque era carregado pelas AMCs de estoque minúsculo. O bloco de oferta tem **um** resultado contra hazard constante, não dois |
| **#57** | `remanescente_qualidade.py` | Fecha a alternativa "o Sul tem terra **pior**, não só **menos**" que a decomposição do #39 não cobria. **Entre AMCs**: eliminada — a aptidão ponderada do estoque do Sul é a mesma em 1985 e 2024 (4,60→4,61); quem degrada é o **Norte** (−0,12), comportamento de fronteira ativa descendo o gradiente. **Dentro da AMC**: viva — a fração florestal do remanescente do Sul sobe de **52,2% para 59,9%** (galeria/cerradão = relevo quebrado + APP), contra 29,6→34,3% no Norte. O mecanismo de seleção existe (hazard×aptidão β>0, p<0,001 nas 3 regiões). ⚠️ **Viva como ESTADO, não como processo** (ajuste de 20/ago): a fração florestal sobe no **estado inteiro** (37,0→42,5%) e o excesso do Sul sobre a média estadual é de ~2 pontos — a **tendência** não separa seleção de **deriva de classificador savana↔floresta**, resíduo não medido de [`oscilacao_pasto_savana.md`](metodologia/oscilacao_pasto_savana.md). O que se afirma é o **nível** (3/5 hoje × 1/3 no Norte), que já era 52,2% em 1985: fisiografia antes de história, e não depende da tendência. ⇒ veredito **misto**, e é por isso que "estoque convertível" exclui floresta |

### Cartografia e legado

| # | Script | Nota |
|---|---|---|
| #9, #10, #11 | mapas coropléticos, raster GEE 30 m, GIF | A vitrine visual dos 40 anos |
| #20 | `figuras_taxas.py` | A vitrine do #17 |
| #8 | `analise_credito_uso_terra.py` | Primeira leitura crédito × LULC; gerou a `auditoria_pib.py` |
| #1, #2 | primeira foto UF | Baseline histórico; úteis como validação batimental |
| **#5** | `analise_pastagem_soja.py` | ⚠️ **SUPERADO pelo #12.** Proxy de transição por estoque. Não use como fonte de fluxo |

---

# Parte 4 — Tabela de coordenadas

Todos os pipelines, com as três etiquetas. **O número é a identidade** (nunca muda); as demais
colunas são a ordem lógica.

| # | Script | Papel | Perna | Fase | Família |
|---|---|---|---|---|---|
| 1 | `grafico_pastagem_pib_goias.py` | Foto inicial | — | 0 | — |
| 2 | `analise_expandida_goias.py` | Foto inicial | — | 0 | — |
| 3 | `coleta_sidra.py` | Coletor | — | 1 | Fundação |
| 4 | `pipeline_municipal.py` | Coletor | — | 1 | Fundação |
| 5 | `analise_pastagem_soja.py` | **Superado** (por #12) | — | 2 | Transições |
| 6 | `coleta_sicor.py` | Coletor | — | 1 | Fundação |
| 7 | `coleta_sidra.py --censo-agro` | Coletor | — | 1 | Fundação |
| 8 | `analise_credito_uso_terra.py` | Primeira leitura | — | 2 | — |
| 9 | `gerar_mapas_lulc_40anos.py` | Cartografia | — | 2 | Cartografia |
| 10 | `gerar_mapas_lulc_gee_40anos.py` | Cartografia | — | 2 | Cartografia |
| 11 | `gerar_gif_lulc.py` | Cartografia | — | 2 | Cartografia |
| 12 | `transicoes_mapbiomas.py` | Infraestrutura (**superado**) | — | 2 | Transições |
| 12B | `transicoes_cubo.py` + `validar_transicoes_cubo.py` | Infraestrutura | #28 (cubo) | 6 | Transições |
| 13 | `coleta_idhm.py` | Coletor | — | 1 | Fundação |
| 14 | `fogo_mapbiomas.py` + `analise_fogo.py` | Coletor | — | 1 | Fogo |
| 15 | `analise_safrinha.py` | Coletor | — | 1 | Fundação |
| 16 | `construir_painel_unificado.py` | Infraestrutura | — | 3 | Painel |
| 17 | `calcular_taxas_lulc.py` | Infraestrutura | — | 3 | Taxas |
| 18 | `mapeamento_mesorregioes.py` | Infraestrutura | — | 3 | — |
| 19 | `agregar_conversoes.py` | Infraestrutura | — | 2 | Transições |
| 20 | `figuras_taxas.py` | Cartografia | — | 3 | Taxas |
| 21 | `correlacoes_uf.py` | Manchete (fraca) | — | 4 | Inferência |
| 22 | `correlacoes_painel.py` | **Manchete** | **2** | 4 | Inferência |
| 23 | `piecewise_did.py` | Manchete (nulo) | — | 4 | Inferência |
| 24 | `analise_espacial.py` | Diagnóstico | — | 4 | Inferência |
| 25 | `construir_amc_goias.py` | Infraestrutura | — | 3 | Painel |
| 26 | `deteccao_quebras.py` | Manchete | — | 4 | Periodização |
| 27 | `coleta_trase.py` | Coletor | — | 1 | Fundação |
| 28 | `coleta_idade_pastagem.py` + `analise_reserva_terra.py` | **Manchete** | **2** | 5 | Idade do pasto |
| 28C | `bimodalidade_regional.py` | **Autocorreção** | **2** | 6 | Idade do pasto |
| 28D | `deriva_mosaico_fim_serie.py` | **Autocorreção** | **2** | 6 | Idade do pasto |
| 29 | `periodizacao_multivariada/stars/transicoes.py` | Infraestrutura (régua) | — | 5 | Periodização |
| 30 | `verificacao_periodizacao.py` | Robustez | — | 5 | Periodização |
| 31 | `intensity_analysis.py` + `verificacao_intensity.py` | Robustez | — | 5 | Periodização |
| 32 | `centro_massa.py` | **Manchete** | **1** | 6 | **Centro de massa** |
| 33 | `transicoes_regionais.py` | **Manchete** | **2** | 6 | Transições |
| 34 | `deslocamento_espacial.py` | **Manchete (nulo)** | **3** | 6 | Deslocamento |
| 35 | `robustez_janelas.py` | Robustez | 1, 2 | 6 | Robustez |
| 36 | `robustez_janela_slope.py` | Robustez | — (defende #17) | 6 | Robustez |
| 37 | `coleta_drivers_macro.py` + `drive_comum.py` | Manchete (fraca) | **3** | 6 | Drive comum |
| 38 | `drive_comum_amc.py` | Manchete (fraca) | **3** | 6 | Drive comum |
| 39 | `fronteira_fechando.py` | **Manchete** | **4** | 6 | Oferta |
| 40 | `duas_logicas_pastagem.py` | Manchete + **Autocorreção** | **2** | 6 | Idade do pasto |
| 40B | `duas_logicas_calcario_orientacao.py` | **Autocorreção** | **2** | 6 | Idade do pasto |
| 41 | `fogo_lidera_fronteira.py` | **Autocorreção** | 1, 3 | 6 | Fogo |
| 42 | `granger_reverso_norte_sul.py` | **Autocorreção** | **3** | 6 | Deslocamento |
| 43 | `centro_massa_pixel.py` | Robustez (MAUP) | **1** | 6 | **Centro de massa** |
| 44 | `centro_massa_desagregado.py` | **Autocorreção** | **1** | 6 | **Centro de massa** |
| 45 | `analise_trase_lulc.py` | Extensão (Eixo A) + **Autocorreção** | **3** | 6 | Deslocamento |
| 46 | `fronteira_protecao.py` | Extensão | **4** | 6 | Oferta |
| 47 | `custo_carbono_marcha.py` | Extensão (Eixo ambiental) | 4 (consequência) | 6 | Ambiental |
| 48 | `validacao_prodes_mapbiomas.py` | **Validação externa** | **4** | 6 | Ambiental |
| 49 | `painel_espacial_dinamico.py` | Robustez (Eixo C1) | 2, 3 | 6 | Inferência |
| 50 | `centro_massa_economico.py` | Extensão | 3 | 6 | **Centro de massa** |
| 51 | `crescimento_sem_desenvolvimento.py` | Extensão | 3 | 6 | **Centro de massa** |
| 52 | `aptidao_edafo_exposicao.py` + `aptidao_edafo_drive38.py` | Extensão (identificação) | 3 | 6 | Drive comum |
| 53 | `centro_massa_capacidade.py` | Extensão | 3 | 6 | **Centro de massa** |
| 54 | `defensabilidade_perna4.py` | Robustez (inferência) | 3 | 6 | Drive comum |

**Contagem por papel** (56 linhas; o #40 e o #45 contam duas vezes — são manchete/extensão *e*
autocorreção): 12 manchetes · 8 coletores · **8 autocorreções** · 7 infraestrutura · 7 extensões ·
7 robustez · 4 cartografia · 2 foto inicial · 1 validação externa · 1 primeira leitura ·
1 diagnóstico · 1 superado.

> As **8 autocorreções** (#28C, #28D, #40, #40B, #41, #42, #44, #45 + a D19) são o ativo mais raro
> do conjunto. Nenhum outro número desta tabela é tão difícil de conquistar. A mais recente,
> **#28D**, é também a mais dura: derruba uma manchete temporal do #28 mostrando que o *dado de
> origem* mudou de significado no meio da série.

---

# Parte 5 — Ordens de leitura sugeridas

Não existe "a" ordem. Existe a ordem **para quê**.

**Para a banca (o caminho crítico, ~1h).** As 4 pernas da Parte 1, nesta ordem, lendo só as
manchetes e as autocorreções: #32 → #33 → **#34** → #42 → #37/#38 → #39. O #34 e o #42 são o
coração: é onde a tese é testada contra si mesma.

**Para entender os métodos.** [`guia_de_leitura.md`](guia_de_leitura.md) de cima a baixo, uma
vez. Depois use como dicionário.

**Para entender como o trabalho nasceu.**
[`narrativa_pipelines.md`](narrativa_pipelines.md) — Fases 0 a 6, em ordem.

**Para reproduzir.** Fundação → tabelas-mãe → análise: #3/#4/#6 → **#28 (cubo) → #12B** → #19 → #16 → #25 → #17 →
o pipeline que interessa. (O #12 original ainda roda, mas só como referência de comparação: a
matriz primária vem do #12B desde 27/jul/2026, e ele lê o cubo do #28, não o GEE.) Todo coletor tem cache; `--force` rebaixa.

**Para auditar a honestidade do trabalho.** Só as autocorreções, em ordem cronológica: #40 →
#41 → #28C → #42 → #44 → #40B → D19 → **#45**. Lidas em sequência, contam uma história própria — a
de alguém que foi atrás dos próprios erros antes que a banca fosse. E note a **escada de
profundidade**: o #40 corrigiu uma *interpretação* (confundidor de latitude), o #42 corrigiu um
*método* (Granger em série integrada), a D19 corrigiu uma *omissão* (faltava barra de erro), e o
#45 corrigiu a camada mais funda de todas — **o que a variável continha**. Uma correlação de 0,986
entre regressor e regressando estava lá o tempo todo; ninguém tinha olhado.

---

## Pendências que a construção deste índice revelou

Itens factuais que estavam desatualizados em outros documentos. **Todos corrigidos em
2026-07-17**, exceto o último:

- ✅ `Textos/README.md` dizia "#1–#49" — corrigido para #50.
- ✅ `guia_de_leitura.md` dizia "49 pipelines" e reportava a vegetação como "+8 km / quase
  parada" — agora diz **"ancorada"**, traz a tabela de IC95% da **D19** no verbete 1.6, e ganhou
  duas perguntas de banca sobre incerteza e sobre o método ser padrão.
- ✅ `narrativa_pipelines.md` resumia as decisões como **D1–D18** e não listava o #50 no
  Apêndice A — a **D19** entrou na tabela de decisões e o `centro_massa_economico.py` no índice
  de scripts.
- ✅ **O #27 (coleta Trase) não tinha doc própria** — agora tem:
  [`27_coleta_trase.md`](pipelines/27_coleta_trase.md). Era a única lacuna de documentação do
  conjunto.

- ✅ **O #45 pareava um regressor que não era o que dizia ser** — `trase_soja_volume_t`, chamado de
  "volume exportado", é na verdade **produção** (r=0,986 com a área plantada; 44,6% dele é
  esmagamento doméstico). **Corrigido na raiz**: o #27 agora separa `_volume_export_t` de
  `_volume_domestico_t`, o #45 usa o exportado, ganhou um par de contraste e um **Bloco C** de
  robustez. O β-manchete caiu de **+0,335 para +0,037** e o veredito ficou **mais forte**: a
  cadeia exportadora não lidera **nem co-move materialmente**. Ver
  [`45_trase_lulc.md`](pipelines/45_trase_lulc.md).

---

> **Última palavra.** Se alguém — inclusive você, daqui a seis meses — sentir de novo que "os
> números estão fora de ordem", a resposta está no topo deste documento: eles não são uma
> ordem, são uma identidade, e a ordem lógica é esta aqui. O caderno de laboratório fica como
> está. A apresentação é este documento.
