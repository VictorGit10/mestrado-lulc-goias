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
> intensificação no Sul, fronteira no Norte — coordenada por **forças de mercado comuns** sobre
> um **gradiente de aptidão**, e limitada por um **teto de oferta** de terra convertível — e
> **não** um deslocamento causal de uma região sobre a outra.

Cada perna abaixo segue a mesma forma: a afirmação, a força, a **manchete** que a faz, a
**robustez** que a defende, a **autocorreção** que a afiou, e o que ela **não** permite dizer.

---

## Perna 1 — O padrão existe

> **Afirma:** toda a fronteira agropecuária marchou ao norte entre 1985 e 2024. A lavoura fica
> ~120–130 km ao sul do pasto/rebanho em *todos* os anos. A vegetação natural ficou ancorada.

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
> (intensificação, sobre pasto jovem, mediana ~9 anos). No Norte, `mata→pasto` (fronteira, sobre
> pasto antigo, ~20 anos).

**Força: forte** — com uma ressalva que a autocorreção impôs: a geografia desloca o **peso** da
mistura, não **causa** os modos.

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete** | **#33** `transicoes_regionais.py` | Recorta as conversões brutas por mesorregião × ato. `veg→pasto` é a transição-mãe pervasiva; `pasto→agric` só *lidera* no Sul+Centro no Ato II. O deslocamento aparece no **balanço líquido** |
| **Manchete** | **#28** `coleta_idade_pastagem.py` + `analise_reserva_terra.py` | A idade do pasto na conversão é **bimodal** (~5 anos e ~22/35 anos) = dois mecanismos coexistindo. ~78 mil pixels |
| **Manchete** | **#22** `correlacoes_painel.py` | Painel 2-way FE: a **substituição local** é forte (onde a lavoura entra, o pasto sai *localmente*) e o SICOR é o canal dominante de retração — **na janela com SICOR (2013–2021), ~8 anos**, não nos 40 |
| **Autocorreção** | **#40** `duas_logicas_pastagem.py` | Espacializa as duas lógicas (Rotação no Sul × Oportunístico no Norte). **Derrubou o próprio overclaim no mesmo dia**: o cruzamento com plantio direto some sob o gradiente 2D → **D14** |
| **Autocorreção** | **#28C** `bimodalidade_regional.py` | A bimodalidade é *regionalmente causada*? **Não.** A região explica 2,5% (meso) / 7,3% (AMC, líquido de acaso); o tempo explica 20%; **73–77% mora dentro** das células |
| **Autocorreção** | **#40B** `duas_logicas_calcario_orientacao.py` | Generaliza a D14: calcário e orientação técnica também somem sob o gradiente 2D. A lição vale para manejo, insumo e instituição |
| **Robustez** | **#49** `painel_espacial_dinamico.py` | Os canais do #22 sobrevivem ao termo espacial (Elhorst FE lag/error) |

**O que esta perna NÃO permite dizer:** que "a região causa a bimodalidade" (o #28C mediu: não
causa) nem que "plantio direto explica a idade do pasto" (o #40 derrubou: era confundidor de
latitude). A frase certa é **"gradiente regional no *peso* da mistura"**.

**Ler a fundo:** [`33_transicoes_regionais.md`](pipelines/33_transicoes_regionais.md) →
[`28_idade_pastagem.md`](pipelines/28_idade_pastagem.md) →
[`40_duas_logicas_pastagem.md`](pipelines/40_duas_logicas_pastagem.md) →
[`28C_bimodalidade_regional.md`](pipelines/28C_bimodalidade_regional.md)

---

## Perna 3 — Reorganização coordenada, não deslocamento causal

> **Afirma (o negativo, forte):** a hipótese-mãe — *a lavoura do Sul empurra o pasto para o Norte*
> (iLUC intra-estadual) — foi **testada e refutada no canal testado**. A precedência temporal não
> aparece (Granger nulo, **mas de baixo poder** — N≈38); e o spillover direcional, onde estimável,
> saiu **significativo no sentido oposto** ao previsto (θ=−0,16, p=0,02). É o spillover de sinal
> trocado — não o nulo do Granger — que carrega a refutação.
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
| **Manchete (nulo)** | **#34** `deslocamento_espacial.py` | O teste formal, em **tempo contínuo**. (a) Sem precedência: Granger ΔAgric_Sul → ΔPasto_Norte **p=0,97** (nulo de **baixo poder** — N≈38; poder ~48% p/ efeito moderado, ~93% p/ grande, sim. Monte Carlo). (b) Spillover direcional **significativo e de sinal trocado**: θ=−0,16, **p=0,02**, oposto ao previsto — **é ele que refuta, não o nulo do Granger**. (c) Substituição local forte: β=−0,52 |
| **Autocorreção** | **#42** `granger_reverso_norte_sul.py` | **A peça-modelo do conjunto.** O #34 deixou uma ponta: o teste *reverso* deu p=0,0007 — que, se real, inverteria a tese. O #42 provou que é **regressão espúria**: `pasto_Norte` é I(2), `agric_Sul` é I(0), ordens diferentes nem cointegram; **Toda-Yamamoto zera as duas direções**; e os **placebos** mostram que o Norte "lidera" até o pasto do próprio Sul → **D16** |
| **Extensão + Autocorreção** | **#45** `analise_trase_lulc.py` | Terceiro canal a confirmar co-evolução sem líder: a cadeia exportadora **não lidera** (0/3 termos defasados sobrevivem à robustez) **nem co-move materialmente**. Em jul/2026 derrubou o próprio achado-manchete ao descobrir que o regressor era produção disfarçada (β +0,335 → +0,037) |
| **Extensão** | **#53** `centro_massa_capacidade.py` | Fecha a ressalva do #45 pelo lado da **capacidade instalada**: o centroide da capacidade de armazenagem (CONAB) é a camada **mais ao sul de todas** (~150 km ao sul do pasto, ~83 km ao sul até do crédito) — a infraestrutura física **consolida o núcleo, não lidera**. Metade "silos"; a "frigoríficos" segue sem dado |
| **Adjacente** | **#41** `fogo_lidera_fronteira.py` | O fogo é vanguarda **geográfica** (ao norte da conversão em 39/39 anos) mas **não lidera no tempo** — coerente com o veredito de co-evolução |

**O positivo — o drive comum coordena o tempo (corroborante, não estabelecido):**

| Papel | Pipeline | O que entrega |
|---|---|---|
| **Manchete (fraca)** | **#37** `coleta_drivers_macro.py` + `drive_comum.py` | Testa o drive comum na série UF/anual (N≈38). **~7 hits em ~135 testes ≈ acaso; nada sobrevive à correção de multiplicidade.** Só o **câmbio** tem estrutura (reaparece em duas margens). Passa no placebo de exogeneidade. Bônus: a quebra órfã de 1991 ganha nome — colapso de crédito do Plano Collor |
| **Manchete (fraca)** | **#38** `drive_comum_amc.py` | Muda a unidade para o painel AMC (~6.600 obs) e testa **driver × exposição baseline**. A hipótese confirmatória `câmbio × fronteira → rebanho` confirma a direção (**p=0,031**), mas a grade exploratória (144 testes) **não devolve nenhum sobrevivente do FDR**. A área LULC é **nulo robusto** |
| **Extensão (identificação)** | **#52** `aptidao_edafo_exposicao.py` + `aptidao_edafo_drive38.py` | Troca o proxy de área do #38 por uma aptidão edafoclimática **exógena** (Embrapa 1:500k, WFS). **52A**: a aptidão física **reproduz** o gradiente Sul→Norte (r_lat=−0,44; Sul 4,69>Centro 4,47>Norte 4,17) — a premissa vira **medida**, não assumida; correlação **moderada** (+0,30) com a exposição do #38 = carrega info própria. **52B**: o achado do #38 reaparece **sem a complementaridade mecânica** (câmbio×aptidão→rebanho **β=−0,033, p=0,026**) e a grade honesta de 192 devolve **2 sobreviventes do FDR** — mas via a **mesma fragilidade de tamanho de família** do Achado #2 do #38. Fortalece a **identificação**, não o poder |
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
| **Extensão** | **#47** `custo_carbono_marcha.py` | O **custo** da marcha: ~**973 Mt CO₂e** (faixa de cenários de densidade: **751–1208**). A **floresta domina a emissão** apesar de perder 2,6× menos área que o savânico. O centróide da perda marcha +98 km ao norte — amarra com o #39 |

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
| Perda de carbono | #47 | Marcha +98 km ao norte |

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
| #15 | `analise_safrinha.py` | Milho 1ª/2ª safra |
| #27 | `coleta_trase.py` | Cadeia produtiva Trase — soja e boi (dormente até o #45). ⚠️ "só exportação" vale para o boi, **não para a soja** (44,6% é esmagamento doméstico) |

### Infraestrutura (Fases 2–3) — as tabelas-mãe

| # | Script | O que entrega |
|---|---|---|
| #12 | `transicoes_mapbiomas.py` | **A virada metodológica**: matriz de transição **pixel-a-pixel**, não inferida de estoques. Substitui o #5 |
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
| #23 | `piecewise_did.py` | Manchete (nulo) | **Só `Vegetação × 1995 vs TO` sobrevive** a parallel-trends + placebo. O Código Florestal não |
| #24 | `analise_espacial.py` | Diagnóstico | **115 de 140 resíduos** têm Moran's I significativo → o espaço é estrutural |
| #26 | `deteccao_quebras.py` | Manchete | Quebras data-driven: **2001 (F=62,2)** e **2020 (F=21,5)**. O Código Florestal **não produz quebra** |

### Robustez transversal — as quatro réguas

O trabalho testa cada manchete em quatro eixos independentes. Vale saber nomeá-los:

| Régua | Pergunta | Pipelines | Decisão |
|---|---|---|---|
| **Tempo** | Depende de onde cortamos? | #35 (fronteira), #36 (resolução) | D12 |
| **Latitude** | É efeito próprio ou gradiente? | #40, #28C, #40B | D14 |
| **Integração** | O Granger é espúrio? | #42 | D16 |
| **Espaço** | Sobrevive à autocorrelação? | #49, #43 (MAUP) | — |
| **Incerteza** | Qual o IC? | D19 (#32/#44/#50) | D19 |

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
| 12 | `transicoes_mapbiomas.py` | Infraestrutura | — | 2 | Transições |
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
autocorreção): 12 manchetes · 8 coletores · **7 autocorreções** · 7 infraestrutura · 7 extensões ·
7 robustez · 4 cartografia · 2 foto inicial · 1 validação externa · 1 primeira leitura ·
1 diagnóstico · 1 superado.

> As **7 autocorreções** (#28C, #40, #40B, #41, #42, #44, #45 + a D19) são o ativo mais raro do
> conjunto. Nenhum outro número desta tabela é tão difícil de conquistar.

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

**Para reproduzir.** Fundação → tabelas-mãe → análise: #3/#4/#6 → #12/#19 → #16 → #25 → #17 →
o pipeline que interessa. Todo coletor tem cache; `--force` rebaixa.

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
