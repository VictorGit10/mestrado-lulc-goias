# Pipeline #40 — As duas lógicas da pastagem: espacialização + plantio direto

**Script**: `scripts/duas_logicas_pastagem.py`
**Status**: ✅ Concluído (2026-06-07) · **revisado sobre o censo do #28 em 2026-07-21**
**Outputs**: 4 CSVs (`duas_logicas_amc.csv`, `duas_logicas_municipal.csv`, `duas_logicas_cruzamento.csv`, `duas_logicas_robustez.csv`) + 5 PNGs em `outputs/duas_logicas/` (`mapa_logica_dominante_amc`, `pixels_mecanismo`, `gradiente_latitude`, `cruzamento_plantio_direto`, `tipologia_carreira_terra`).
**Depende de**: #28 **censo** (`pastagem_idade_censo.parquet`, com `lat_media`/`lon_media`), #27/Censo 2017 (plantio direto), #25 (AMC + crosswalk).

## Pergunta de pesquisa

O #28 provou que a conversão pasto→agricultura em Goiás é **bimodal** (GMM com ΔBIC
estratosférico): um pico **jovem** (~5a) e um **antigo** (~22a), assinatura de dois
mecanismos coexistentes — **rotação/trampolim premeditado** (pasto é uma fase curta de
um sistema de lavoura) vs. **reserva oportunística** (pasto antigo ativado por
oportunidade exógena). Mas o #28 parou em dois lugares:

1. **Espacialmente** ficou na mesorregião (5 unidades) — não disse *onde*, finamente,
   cada lógica domina.
2. **Estruturalmente** cruzou a idade só com **choques de fluxo** municipais (Δ SICOR,
   Δ VA agro) e achou **nada** (r≈0,03, n.s.), concluindo que "os mecanismos operam
   abaixo da escala municipal".

Este pipeline puxa o fio #2 do backlog: **espacializar** as duas lógicas (AMC e
município) e **cruzá-las com a estrutura do sistema agrícola** — o **plantio direto**
(Censo 2017), proxy de integração lavoura-pecuária (ILP)/rotação. A pergunta-teste era:
a idade-na-conversão é ilegível na escala municipal, ou só faltava cruzar com a variável
certa (estrutura, em vez de fluxo)? **Resposta (após a revisão de 21/jul/2026): a
estrutura NÃO se mostrou superior ao fluxo — é o contrário.** Sob controle 2D simétrico,
o único sinal que sobrevive a multiplicidade é de **fluxo** (Δ SICOR, p=0,001); a
estrutura (no-till) fica limítrofe (p≈0,058) e **não estabelecida**. O que o pipeline
entrega de sólido segue sendo a **geografia** das duas lógicas.

## O que é novo vs. #28

| | #28 | #40 |
|---|---|---|
| Unidade espacial | mesorregião (5) | **AMC (166) + município (246)** |
| Classificação por mecanismo | regra por pixel (existe) | **agregada à unidade** (mistura + índice) |
| Cruzamento | fluxo em painel (muni,ano) → nulo | estrutura/fluxo em recorte transversal + **parcial \| latitude** |
| Síntese | — | **tipologia "carreira da terra"** (regra + k-means) |

## Método

Reusa a regra de decisão do #28 (`classificar_mecanismo`): pixel não-censurado é
**Premeditado curto** (veg.nat, ≤8a), **Rotação** (agricultura, ≤8a),
**Oportunístico clássico** (veg.nat, ≥20a) ou **Ambíguo**.

- **Bloco A — Agregação.** Mistura de mecanismos por AMC e município sobre os pixels
  **não-censurados** na **janela primária 2010–2024** (regime moderno, censura baixa,
  Censo 2017 no meio). Índice contínuo `indice_jovem = %≤8a − %≥20a ∈ [−1,1]`
  (+ = lógica jovem). Filtro de confiabilidade: **≥20 px/município, ≥15 px/AMC**
  (mitiga o ruído de munis pequenos apontado na crítica do #28). Com o censo o corte
  deixa de morder: → **244 munis e 164 AMCs** (era 88 e 82 na amostra)
  confiáveis.
- **Bloco B — Espacializar.** Coroplético AMC (malha EPSG:5880 do #32–#39): índice
  contínuo + mecanismo dominante categórico; scatter de pixels por mecanismo (textura
  fina, contorna o filtro de N); gradiente latitudinal (índice e no-till × latitude do
  centroide).
- **Bloco C — Cruzar com plantio direto.** `pct_pd_area = área plantio direto / área dos
  estabelecimentos` (Censo 2017). Pearson + **Spearman** (robusto) da mistura municipal
  contra no-till e outras variáveis **estruturais** do Censo; robustez em **3 janelas**.
  **Verificação crítica (Bloco C2)**: parcial controlando **latitude** (o cruzamento é
  informação própria ou só o gradiente Sul→Norte?) + comparação **justa** com fluxo
  (SICOR/VA agro) no **mesmo recorte transversal** municipal.
- **Bloco D — Tipologia.** Regra (mecanismo líder → "carreira da terra") + **k-means
  (k=4)** sobre features padronizadas como robustez à regra.

## Achados

> ⚠️ **Duas correções sucessivas — leia nesta ordem.**
>
> **(a) 2026-06-07** — a primeira leitura anunciou "a lógica é estrutural (no-till), não
> de fluxo". A verificação não sustentou: quase tudo é o gradiente Sul→Norte
> compartilhado, e o achado robusto é a **segregação espacial** das duas lógicas.
>
> **(b) 2026-07-21** — ao migrar para o **censo** do #28 e igualar os controles dos dois
> braços da comparação, três coisas mudaram: (i) o gradiente sobrevive mas **cai à
> metade** (r −0,49 → −0,236); (ii) "não há efeito próprio do no-till" **foi retirado** —
> era artefato de erro de medida, e o veredito correto é *não estabelecido*; (iii) a
> comparação estrutura × fluxo, agora simétrica, **confirma** que o fluxo tem o único
> sinal robusto. As seções abaixo já refletem (b).

### 1. O achado ROBUSTO — a geografia da bimodalidade (segregação espacial)

A contribuição sólida do #40 é **espacializar** a bimodalidade do #28: cada AMC/município
recebe sua mistura de mecanismos. **Rotação (jovem ≤8a) domina Sul/Centro; Oportunístico
(antigo ≥20a) concentra-se no Norte** (mapa AMC). É o gradiente de mesorregião do #28
(Sul 9a → Norte 16a, não-censurado) em resolução fina, alinhado ao eixo Sul→Norte de
#32/#39. ⚠️ Esta página mede **peso da mistura**, não idade — ver
["O que a família da idade estabelece"](28_idade_pastagem.md#o-que-a-família-da-idade-estabelece):

- índice jovem↔antigo × latitude: **r = −0,236** (p=0,002, n=164 AMCs)
- idade mediana × latitude: r = +0,176 (p=0,024)
- as duas lógicas são a face *mecanismo-de-conversão* do gradiente de **aptidão + capital**:
  o Sul capitalizado **gira** pasto jovem na rotação (pasto = fase); o Norte de fronteira
  **ativa** pasto antigo (pasto = reserva de terra).

> **Revisado em 21/jul/2026 — o gradiente sobrevive, mas com metade da força.**
> A amostra dava r = −0,49; o censo dá **−0,236**. A direção, a significância e a
> leitura substantiva se mantêm; a **magnitude não**.
>
> | recorte | n AMCs | índice jovem × lat |
> |---|---|---|
> | Amostra | 88 | −0,500 (p<0,001) |
> | **Censo, nas MESMAS 88 AMCs** | 88 | **−0,310 (p=0,003)** |
> | Censo, todas | 164 | −0,236 (p=0,002) |
> | Censo, só as 76 acrescidas | 76 | −0,154 (p=0,185) |
>
> Note que aqui a composição **não** explica a queda: nas mesmas 88 AMCs o r já cai de
> −0,50 a −0,31. Ou seja, é medição — e no sentido **contrário** ao do §2, onde medir
> melhor *fortaleceu* a parcial. A explicação mais provável é a **ponderação entre anos**:
> a amostra usava 2.000 px/ano, sobre-representando anos recentes (menos conversão, pasto
> mais jovem) de forma desigual entre AMCs — o mesmo defeito de composição documentado
> em `metodologia/censo_vs_amostra.md` §3. **Não isolei esse mecanismo**; fica como
> hipótese, não como conclusão.
>
> Consequência para a redação: o gradiente continua sendo o achado robusto do #40, mas
> **não citar r = −0,49**, e não descrever a segregação como "limpa" — ela é real,
> significativa e moderada.

> [!WARNING]
> **Robustez à mudança de rótulo do Mosaico (D26, 23/jul/2026) — a significância do gradiente é
> FRÁGIL e depende da cauda contaminada.** O #40 *pool* os eventos `pasto→agricultura`
> sobre a janela; a [mudança de rótulo do Mosaico](28D_deriva_mosaico.md) reetiqueta esses eventos
> como `pasto→Mosaico` nos anos terminais, e eles **somem** da tabela do #28 — o #40 pool
> ao longo do tempo, logo herda a contaminação (e o #28C, que se *supunha* imune por ser
> transversal, **também herda** — refutado abaixo). Medido (`duas_logicas_deriva_check.py`):
> as conversões `pasto→agric`
> caem **−79%** de 2014–19 (0,75 Mpx/a) para 2022–24 (0,16 Mpx/a). E o gradiente-manchete
> **fortalece quanto mais da cauda entra**:
>
> | janela | índice jovem × lat (Spearman ρ) | p |
> |---|---|---|
> | **limpa 2010–2019** | **−0,124** | **0,113 (ns)** |
> | cheia 2010–2024 (a manchete) | −0,228 | 0,003 |
> | exposta 2016–2024 | −0,308 | <0,001 |
>
> Na janela **limpa (≤2019) o gradiente é fraco e NÃO significativo**; a significância do
> −0,236 vem justamente do trecho que a mudança de rótulo censura mais. Isto **resolve o enigma** da
> revisão de 21/jul (a "ponderação entre anos" que fortalecia r): não era só amostragem —
> os anos recentes carregam um gradiente aparente mais forte porque a mudança de rótulo **seleciona**
> quais conversões ficam visíveis (as perdidas para o Mosaico crescem ao Norte, #32/#44).
> **Bracket por EVENTO — FECHADO (cubo reprocessado, 23/jul/2026,
> `processa_cubo_idade_destinos.py` → `pastagem_conversao_destinos.parquet`;
> teste em `duas_logicas_bracket_evento.py`).** Redefinindo a conversão como
> `pasto→(agric∪mosaico)` — a pergunta grossa, robusta à reetiquetagem por construção — o
> gradiente **desaparece e fica estável em ~zero nas três janelas**, ao contrário do
> `pasto→agric`, cuja significância só vinha da cauda:
>
> | evento | limpa 2010–19 | cheia 2010–24 | exposta 2016–24 |
> |---|---|---|---|
> | `pasto→agricultura` | −0,124 (ns) | −0,228** | −0,308*** |
> | **`pasto→(agric∪mosaico)`** | **+0,036 (ns)** | **+0,090 (ns)** | **+0,082 (ns)** |
>
> A união quase **triplica** os eventos (6,8 → 17,8 Mpx na janela limpa) — as conversões
> `pasto→Mosaico` são a maioria dos términos de pastagem e **não carregam** o gradiente. Ou
> seja: o −0,23 é **específico do subconjunto rotulado como "agricultura"** — que é
> exatamente o que a mudança de rótulo e a confiança do classificador selecionam —, **não** uma
> propriedade robusta da conversão de pastagem. **Veredito revisado: a segregação
> young-Sul/old-Norte NÃO está estabelecida como fenômeno geral** (o intervalo do bracket,
> −0,12 a +0,04, cruza o zero sem significância em nenhum extremo). Sobrevive só na leitura
> estrita "pasto→agricultura pura". O que segue robusto e **independente** é a marcha dos
> **centroides** (#32/#44) — outra medida (onde estão as classes, não a idade do pasto).
> **#28C re-checado sob a união (23/jul/2026):** o gradiente Sul→Norte de idade mediana do
> #28C é o **mesmo artefato** — cai de 7a para 2a sob `pasto→(agric∪mosaico)` e o Norte perde a
> assinatura de pasto velho. Mas o **núcleo do #28C sobrevive** (a bimodalidade/coexistência
> dentro de cada região: 5/5 regiões e 10/10 células ainda bimodais; η²(região) cai de 3,7%
> para 0,5%, reforçando "não-regional"). Ou seja: o **gradiente latitudinal na idade do pasto**
> é artefato do rótulo "agricultura" (tanto no #40 quanto no #28C); o que é real é a
> **coexistência bimodal** modulada pelo **tempo** (Ato III), não pela latitude. Ver
> `bimodalidade_regional_uniao.py` e o WARNING do #28C.

### 2. O cruzamento com plantio direto — co-localização, NÃO efeito próprio

> **Revisado em 21/jul/2026 sobre o censo do #28.** Os números abaixo vêm do censo
> de pixels (n=**209** municípios com dado de no-till, contra 101 na amostra). A
> leitura anterior — "nenhum par sobrevive, **não há efeito próprio** do no-till" —
> **não se sustenta**: era artefato de **erro de medida**, não achado. Ver a
> decomposição adiante.

Na bivariada, no-till parece explicar a idade (no-till % área × idade mediana **r=−0,21**;
× índice jovem +0,23; × % rotação +0,31). **Mas o no-till também desce ao Sul** — exatamente
como a lógica jovem. Controlando o gradiente, o cruzamento encolhe:

| no-till (% área) × | r bruto | r parcial \| lat | **r parcial \| lat+lon** | leitura |
|---|---|---|---|---|
| **idade mediana** | −0,21 | −0,14 (p=0,049) | **−0,13 (p=0,058)** | limítrofe |
| índice jovem↔antigo | +0,23 | +0,14 (p=0,048) | +0,13 (p=0,057) | limítrofe |
| % rotação | +0,31 | +0,13 (p=0,063) | +0,13 (p=0,057) | limítrofe |
| % oportunístico | −0,14 | −0,09 (p=0,180) | −0,09 (p=0,214) | some |

Três dos quatro pares ficam em **p≈0,057–0,058**: encolhem muito sob o controle 2D, mas
não desaparecem. Nenhum cruza 0,05, e **nenhum sobrevive a FDR-BH** (0 de 8 pares do
pipeline; ver §3). O veredito é **"não estabelecido"** — por falta de evidência
conclusiva, **não** por ausência de sinal.

#### Por que o número mudou: precisão × composição

Isto precisa ficar registrado, senão "o r caiu com mais dados" parece contradição.
Rodando o censo **restrito aos mesmos 101 municípios** da amostra, a composição fica
fixa e só a precisão muda:

| recorte | n | r parcial \| lat+lon |
|---|---|---|
| Amostra, seus 101 municípios | 101 | −0,083 (p=0,413) |
| **Censo, nos MESMOS 101** (só precisão) | 101 | **−0,217 (p=0,031)** |
| Censo, todos os 209 (precisão + composição) | 209 | −0,132 (p=0,058) |
| Censo, só os 108 acrescidos | 108 | −0,163 (p=0,095) |

**O nulo limpo da amostra era artefato de medição.** Com a mesma composição e medida
melhor, ele vira significativo (p=0,413 → **0,031**). A amostra estimava a idade mediana
municipal com ~26 pixels não-censurados por município; erro de medida na variável
dependente atenua a correlação em direção a zero, e era isso que se estava lendo como
"não há efeito".

A composição puxa **no sentido oposto**: os 108 municípios que a amostra não conseguia
medir têm mediana de no-till de **2%** (contra 8% nos 101) — pouca variação no regressor
para explorar — e concentram só 10,5% da conversão. O agregado de 209 (p=0,058) é o
líquido dos dois efeitos.

> ⚠️ O corte 101/108 é **pós-hoc e correlacionado com volume de conversão**. Serve para
> diagnosticar de onde veio a mudança, **não** como estimativa preferida. A manchete é o
> n=209. Na bruta a composição domina (−0,341 na amostra → −0,386 nos mesmos 101 →
> −0,209 nos 209); na parcial, a precisão domina.

### 3. "Estrutura bate fluxo" NÃO se sustenta (comparação justa)

O enquadramento original contrastava o cruzamento (transversal) com o **nulo do #28**
(Δ SICOR/Δ VA agro × idade ≈ 0). **A comparação era injusta**: o nulo do #28 era em
**painel (município, ano)** — que lava o gradiente cross-section —, não transversal. Posto
o **fluxo no mesmo recorte transversal** municipal (× idade mediana, mesma janela):

> **Corrigido em 21/jul/2026 — a comparação ainda era assimétrica.** Até aqui o bloco
> de estrutura levava controle **2D (lat+lon)** e o de fluxo só **1D (lat)**. Como a
> conclusão desta seção sai justamente do confronto entre os dois, controles desiguais
> favoreciam o fluxo por construção. O fluxo agora passa pelo mesmo controle 2D.

| Fluxo (mesmo recorte, n=243) | r bruto | r parcial \| lat | **r parcial \| lat+lon** |
|---|---|---|---|
| **SICOR (Δ médio)** | +0,27 | +0,26 (p<0,001) | **+0,22 (p=0,001)** ✅ |
| SICOR (nível médio) | +0,08 | +0,13 (p=0,043) | +0,09 (p=0,163) |
| VA agro (nível médio) | −0,01 | +0,05 (p=0,435) | +0,03 (p=0,590) |
| VA agro (Δ médio) | +0,00 | +0,04 (p=0,516) | +0,05 (p=0,450) |

**A assimetria não era artefato do controle.** O Δ SICOR mal se move ao ganhar a segunda
dimensão (+0,26 → +0,22) e continua a p=0,001.

**Comparação plenamente simétrica** — restringindo os dois blocos aos **mesmos 209
municípios** (que têm no-till *e* SICOR), mesma janela, mesmo controle 2D:

| | r bruto | r parcial \| lat+lon | p |
|---|---|---|---|
| Estrutura (no-till) | −0,209 | −0,132 | 0,058 |
| **Fluxo (Δ SICOR)** | +0,266 | **+0,230** | **0,0009** |

**FDR-BH sobre os 8 pares do #40** (4 estrutura + 4 fluxo, q=0,05): **exatamente 1
sobrevive**, e é o mesmo nas duas fontes — Δ SICOR × idade mediana (censo p=0,0006;
amostra p=0,0047). Nenhum par de estrutura passa.

Logo a dicotomia "estrutura > fluxo" **cai**, e agora com base numa comparação justa: o
único sinal do pipeline que resiste a controle 2D, troca de fonte e multiplicidade é de
**fluxo**, não de estrutura.

> ⚠️ **Atenção ao sinal.** O Δ SICOR × idade é **positivo** (+0,22): municípios onde o
> crédito cresceu mais convertem pastagens **mais velhas**, não mais jovens. É o oposto
> do que se esperaria de "crédito puxa rotação de pasto jovem", e o mecanismo **não foi
> investigado**. Escrever com cuidado — a frase é fácil de ler ao contrário.

#### Bracket da D26 sobre estrutura e fluxo — FECHADO (28/jul/2026)

**O fio que estava aberto.** A D26 tinha sido aplicada ao gradiente latitudinal (§1) e o
derrubou. Os cruzamentos desta seção e da §3 medem a idade sobre **o mesmo subconjunto
selecionado pela mudança de rótulo** e nunca tinham passado pela mesma régua — ou seja, o
único par "robusto" do pipeline estava apoiado numa régua que já havia falhado noutro
teste do próprio #40. Rodado em `scripts/duas_logicas_bracket_fluxo.py` (mesmo
`agregar_mix`, mesmos controles, mesmo FDR-BH), Δ SICOR × idade mediana, parcial | lat+lon:

| janela | `pasto→agric` | **`pasto→(agric∪mosaico)`** |
|---|---|---|
| limpa 2010–2019 | +0,040 (p=0,53) ns | **+0,061 (p=0,34) ns** |
| cheia 2010–2024 | +0,221 (p=0,0006) ✅FDR | **+0,299 (p<0,0001) ✅FDR** |
| exposta 2016–2024 | +0,161 (p=0,013) ✗FDR | **+0,246 (p=0,0001) ✅FDR** |

**Duas leituras, e as duas importam.**

1. **A associação NÃO é artefato de rotulagem** — ao contrário do gradiente latitudinal,
   ela **sobrevive e se fortalece** sob a união (+0,22 → +0,30), e passa a sobreviver ao
   FDR em duas janelas em vez de uma. Isto é evidência genuína, e é o oposto do que
   aconteceu com o gradiente. Vale registrar a assimetria: a D26 não condena tudo que
   toca — ela **separa** o que era artefato do que não era.
2. **Mas ela só existe com os anos recentes dentro.** Na janela limpa (≤2019) o
   coeficiente é ~zero e não significativo **nas duas réguas**. Como a união é imune à
   reetiquetagem por construção, a dependência de janela **não** pode ser creditada ao
   Mosaico: ou é um efeito genuinamente recente (crédito de 2020–24 ativando reserva
   antiga), ou é outro confundidor de período não identificado. **Não foi investigado.**

**Estrutura sob a mesma régua** (no-till × idade mediana, parcial | lat+lon): −0,132
(p=0,058) no `agric` contra **−0,125 (p=0,073)** na união, janela cheia; na exposta,
−0,080 (p=0,25) contra −0,135 (p=0,052). O veredito **"não estabelecido" é robusto ao
bracket** — não muda de lado em nenhuma combinação, e nenhum par de estrutura sobrevive
ao FDR em nenhuma das seis células.

> ⚠️ **O que "plantio direto" mede, e o que ele não mede.** O texto acima e o §2 chamam o
> no-till de "proxy de ILP/rotação". Isso é **frouxo demais** e foi corrigido na redação do
> site: plantio direto é **conservação de solo** (semear sem revolver, mantendo palhada),
> não integração lavoura-pecuária. O Censo Agropecuário **não tem** variável de ILP — foi
> por isso que o no-till entrou, por ser o mais próximo disponível, não por ser o certo. O
> que ele indexa bem é *lavoura de grãos tecnificada e capitalizada*. Qualquer frase que
> derive "há rotação com pecuária" de "há plantio direto" é inferência, não medida.

### 4. Tipologia "carreira da terra" (244 municípios, 2010–24)

Com o censo **todos** os 244 municípios entram (antes 88 passavam no corte de ≥20 px);
a categoria `mosaico` também entra no denominador, o que empurra muitos casos para
"Misto" — o líder passa a precisar de 30% de uma base maior.

| Tipo | n munis | idade med | no-till med | Leitura |
|---|---|---|---|---|
| **Misto / transição** | 160 | 15a | 3,5% | sem mecanismo líder claro |
| **Reserva ativada (oportunístico)** | 42 | 21a | 3,5% | pasto antigo convertido tardiamente |
| **Giro de lavoura (ILP/rotação)** | 38 | 9a | 9,8% | pasto é fase do sistema de lavoura |
| **Trampolim de fronteira** | 4 | 6a | 1,9% | premeditado curto raramente *domina* |

> ⚠️ A **maioria agora é "Misto"** (160 de 244), contra 26 de 88 na amostra. Isso é em
> boa parte **artefato da regra**, não do território: a regra de dominância (`líder ≥30%`
> e `líder > ambíguo`) foi mantida deliberadamente inalterada na migração, para que o
> diff fosse atribuível aos dados. Com o mosaico no denominador, o mesmo limiar ficou
> mais difícil de cruzar. **A tipologia precisa de recalibração antes de ser usada como
> resultado** — hoje ela é comparável com a versão antiga, mas não bem calibrada. Os
> dois polos (Giro 9a, no-till 9,8% × Reserva 21a, no-till 3,5%) seguem nítidos e
> ordenados como antes.

O **"Trampolim de fronteira"** (premeditado curto, veg.nat→pasto→agric em ≤8a) quase
nunca vence o *argmax* — coerente com o #28 §4, que o mediu em ~4–5% estável. As duas
lógicas que **estruturam a geografia** são **Rotação (jovem)** × **Oportunístico
(antigo)**; o premeditado é uma terceira via fina.

**k-means (k=4) recupera os mesmos polos** (com a ressalva de circularidade logo abaixo):

| cluster | %rotação | %oportun. | idade med | **no-till** | n munis | Leitura |
|---|---|---|---|---|---|---|
| 3 | 0,63 | 0,08 | **6,4a** | **39,5%** | 16 | **ILP intensivo** (polo claro de giro) |
| 0 | 0,54 | 0,15 | 8,0a | 5,8% | 23 | rotação de sequeiro (jovem, pouco no-till) |
| 1 | 0,28 | 0,24 | 11,4a | 17,0% | 25 | misto/transição |
| 2 | 0,24 | **0,43** | **18,4a** | 5,6% | 21 | **reserva ativada** (polo antigo) |

Os dois polos emergem do k-means: cluster 3 (rotação + jovem + no-till 40%) vs. cluster 2
(oportunístico + antigo + no-till 6%). **Ressalva de circularidade**: o no-till **entra
como feature** do k-means, então o "no-till 40%" do cluster 3 é em parte por construção;
e como tudo gradeia ao Sul, os clusters **re-expressam o gradiente** mais do que validam
um efeito do no-till. O cluster 0 ainda é instrutivo — rotação jovem **sem** no-till alto
(rotação de sequeiro): nem toda lógica jovem é ILP capitalizada.

## Conexão com a narrativa

- **Fecha o fio #2** do backlog ("as duas lógicas da pastagem") — entregando a **geografia
  da bimodalidade**, não um driver estrutural.
- **Refina o #28 espacialmente**: leva o gradiente de idade da mesorregião (Sul 9a → Norte
  16a, não-cens.) à resolução AMC/municipal e o nomeia (giro de lavoura × reserva ativada). **Corrige**
  a tentação de dizer que a idade "vira legível pela estrutura" — a verificação mostra que
  estrutura (no-till) e fluxo (VA agro/SICOR) co-variam igualmente no gradiente; a idade
  segue sem um preditor transversal próprio (consistente com o #28 §7: o mecanismo opera
  abaixo da escala municipal/transversal).
- **Encaixa no #39/#32/#38**: as duas lógicas são o gradiente **Sul→Norte de aptidão**
  visto pela lente da idade-na-conversão — o Sul gira pasto jovem (a face *mecanismo* da
  intensificação que o #39 viu o Sul adotar ao bater no teto de oferta), o Norte ativa
  pasto antigo. É **descrição coerente do gradiente**, não uma quarta peça causal nova.

## Limitações honestas

1. **Gradiente espacial domina** — o cruzamento é transversal e quase tudo é o gradiente
   Sudoeste→Nordeste de aptidão. Controlando só latitude, no-till × idade ainda fica no fio
   (parcial −0,22, p=0,048); controlando o **gradiente 2D (lat+lon)**, **nenhum par
   sobrevive** (idade −0,15, NS). **Não** se estabelece efeito próprio do no-till.
2. **"Estrutura bate fluxo" refutado** — em recorte transversal comparável, fluxo (VA agro,
   Δ SICOR) correlaciona com a idade tanto quanto/mais que o no-till. O contraste com o nulo
   do #28 era injusto (lá era painel (muni,ano)).
3. **Correlação ecológica** — agregados municipais, não fazenda; Censo 2017 é *snapshot*.
   Mecanismo (rotação vs reserva) é **inferido** por idade+origem; sem CAR/intenção do
   produtor (herança do #28).
4. **Circularidade no k-means** — no-till é feature; clusters re-expressam o gradiente.
5. **Amostra/cobertura** — amostra estratificada do #28 (ruído de classificação pode gerar
   idades curtas artificiais); só 88/246 munis passam o filtro de N; mapa de tipologia pinta
   AMC pelo tipo de maior peso (sem geometria municipal no projeto).

## Decisão metodológica (D14)

**Em cruzamentos transversais de LULC em Goiás, sempre reportar a correlação PARCIAL
controlando o gradiente espacial (latitude e longitude — o eixo de aptidão
Sudoeste→Nordeste) antes de atribuir efeito próprio a qualquer covariável — e comparar
régua com régua (transversal × transversal, painel × painel), com o **mesmo conjunto de
controles dos dois lados**.** Justificativa empírica (aprendida aqui): no-till, VA agro e
SICOR co-variam com a idade da pastagem em boa parte porque todos gradeiam ao Sudoeste; a
bivariada no-till × idade (r=−0,21) cai a −0,13 ao controlar lat+lon. Regra reusável: **o
gradiente de aptidão é um confundidor de primeira ordem em todo cross-section estadual**
(ecoa #38, onde γ_t absorvia o choque comum e a identificação vinha da interação).

### Revisão de 21/jul/2026 — o que mudou e o que não mudou

**A REGRA continua válida e sai reforçada.** O que mudou é o *achado* a que ela foi
aplicada aqui. Três correções, nesta ordem de importância:

1. **"Não há efeito próprio do no-till" foi retirado.** Era artefato de erro de medida:
   com a composição fixa (mesmos 101 municípios) e a idade mediana medida pelo censo em
   vez de ~26 pixels, a parcial 2D vai de −0,083 (p=0,413) a **−0,217 (p=0,031)**. O
   veredito correto é **"não estabelecido"** (p≈0,058 em n=209; 0 de 8 sobrevivem a
   FDR-BH), não "não há efeito". A distinção importa: um nulo limpo encerra a pergunta,
   um indeterminado não.
2. **A comparação estrutura × fluxo era assimétrica** (estrutura com controle 2D, fluxo
   com 1D) e agora é simétrica. A conclusão sobrevive: sob controles e municípios
   idênticos, o Δ SICOR fica a p=0,0009 e a estrutura a p=0,058.
3. **Corolário novo da própria D14**: controle desigual entre os lados de uma comparação
   é a mesma falácia que a D14 combate, uma camada acima. Não basta controlar o
   gradiente — é preciso controlá-lo **igualmente** nos dois braços, senão o veredito
   mede o desenho, não o dado.

**Lição transversal**: antes de ler um nulo como evidência de ausência, verificar o erro
de medida da variável dependente. Um nulo obtido sobre desfecho ruidoso é indistinguível
de falta de poder — e aqui era exatamente isso. Vale para todo pipeline que agrega pixels
a município ou AMC antes de correlacionar.

## Como rodar

```bash
python scripts/duas_logicas_pastagem.py                    # padrão: --fonte censo
python scripts/duas_logicas_pastagem.py --fonte amostra    # amostra legada do #28A
# censo: lê pastagem_idade_censo.parquet (#28) + painel_unificado.parquet (#27/Censo)
# + amc_crosswalk_goias.csv + amc_goias.gpkg; escreve 4 CSVs + 5 PNGs.
# --fonte amostra escreve com sufixo _amostra e NÃO sobrescreve os CSVs canônicos;
# aplica em memória as correções de 21/jul (filtro cd_mun!=0 + relabel da classe 21),
# porque o CSV em disco é anterior a elas.
```
