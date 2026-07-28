# A linha lógica dos pipelines — como esta dissertação foi construída

> **O que é este documento.** Uma leitura *narrativa* e *didática* de todos os scripts de
> análise do trabalho principal (LULC em Goiás, 1985–2024). Não é um catálogo — para a ficha
> técnica de cada pipeline existe [`pipelines/`](pipelines/README.md). Aqui o objetivo é
> reconstruir o **fio condutor**: por que cada análise nasceu, o que ela descobriu, e como
> esse achado tornou necessário o passo seguinte. Lido de cima a baixo, é a história de como
> uma pergunta descritiva simples ("a pastagem encolheu em Goiás?") foi se desdobrando, ao
> longo de mais de 60 scripts, numa tese verificável sobre a **reorganização espacial da
> produção agropecuária goiana**.

> **Escopo.** Tudo aqui se refere ao trabalho principal — Goiás. Os trabalhos paralelos
> (rebanho bovino BR/MG, Montes Claros, viagem de campo; `paralelo/` e os scripts `*_mg.py`)
> ficam deliberadamente de fora; há uma nota sobre eles no apêndice.

---

## Como ler

A construção do trabalho tem uma forma reconhecível: ela vai **do agregado ao detalhe e do
descritivo ao inferencial**, e só no fim retorna ao agregado — agora para *interpretar*, não
para *descrever*. Organizamos isso em sete fases:

| Fase | Título | Pergunta-motor | Pipelines |
|---|---|---|---|
| 0 | A primeira foto | "A pastagem e a economia de Goiás se movem juntas?" | #1, #2 |
| 1 | A fundação de dados | "De onde vêm os números, no nível certo?" | #3, #4, #6, #7, #13, #14, #15, #27 |
| 2 | Primeiras leituras + cartografia | "Onde, no mapa e nos pixels, isso acontece?" | #5, #8, #9–#12, #19 |
| 3 | Consolidação | "Como pôr tudo numa tabela única e comparável?" | #16, #17, #18, #20, #25 |
| 4 | Inferência estatística | "As associações resistem a controles sérios?" | #21, #22, #23, #24, #26 |
| 5 | Periodização data-driven | "Quais são os 'atos' reais da série, sem chutar datas?" | #28, #29, #30, #31 |
| 6 | A marcha ao norte + extensões | "A fronteira se desloca? Como? Por quê? E qual o custo ambiental?" | #32–#49, #28C, #40B |

Cada fase abaixo abre com o *momento* em que ela surgiu, narra os pipelines que a compõem
(incluindo os scripts auxiliares de coleta, validação e cartografia), e fecha com a transição
para a fase seguinte.

---

## Convenções transversais (a gramática comum dos pipelines)

Antes da história, vale fixar as regras que valem para **todos** os scripts — elas são o que
faz peças escritas em momentos diferentes conversarem entre si.

- **Cache e idempotência.** Todo coletor guarda o bruto em `data/raw/` (ou `data/cache/`) e o
  limpo em `data/processed/`. Rodar duas vezes produz o mesmo resultado; `--force` ignora o
  cache e rebaixa. Isso torna a reprodução barata e o pipeline auditável.
- **Chave municipal canônica.** `cd_mun` (código IBGE de 7 dígitos) + `nm_mun` + `ano`. É o
  que permite o *join* entre MapBiomas, SIDRA, BACEN e geobr.
- **Deflação.** Todo valor monetário (PIB, VAB, crédito) é convertido para **reais de
  dezembro/2024** via IPCA (SIDRA 1737). Sem isso, anos não são comparáveis.
- **CRS de área e distância.** Cálculos espaciais de área usam **EPSG:5880** (SIRGAS 2000 /
  Albers Brasil, *equal-area*); rótulos de latitude reprojetam para EPSG:4674.
- **As seis classes (D1).** Os 30+ códigos do MapBiomas são agregados em **6 grupos** —
  vegetação natural, pastagem, agricultura, água, área urbana, outros — com o **Mosaico
  (ID 21) excluído** (no Cerrado goiano é majoritariamente pasto, e misturá-lo contaminaria a
  leitura). Esse mapeamento é idêntico nos mapas (#10), nas transições (#12) e nas taxas (#17).
- **Duas malhas, dois trilhos (D11).** Para análises **transversais** e do período recente,
  os **246 municípios** atuais. Para análises **longitudinais** (1ª diferença, painel FE, DiD,
  tendências), as **166 Áreas Mínimas Comparáveis (AMC)** de território constante — porque 25%
  dos municípios goianos nasceram depois de 1985 e produziriam quedas espúrias.
- **As decisões (D1–D20).** Ao longo do texto aparecem referências a decisões metodológicas
  numeradas. Resumidas:

  | # | Decisão | Onde |
  |---|---|---|
  | D1 | 6 classes unificadas, Mosaico excluído | #10, #17 (**e #12 até 27/jul/2026** — o #12B o traz de volta como 7º grupo nos *fluxos*; nos *estoques* segue excluído) |
  | D2 | Fonte das taxas = `mapbiomas_munis_goias.csv` (não o painel) | #17 |
  | D3 | Slope por janela móvel de 5 anos, *trailing* e *centrada* | #17 |
  | D4 | Erro-padrão HAC Newey-West (maxlags=2) | #17 |
  | D5 | Aceleração = slope[t] − slope[t−1] (a métrica mais frágil) | #17 |
  | D6 | Mesorregiões IBGE 2017 (5 unidades), não Regiões Imediatas | #18 |
  | D7 | Correlações sempre em **primeiras diferenças**, nunca em níveis | #21, #22 |
  | D8 | Painel 2-way FE (efeitos de município + ano), SE clusterizado | #22 |
  | D9 | DiD GO vs MT/TO; hierarquia de controles [TO > combinado > MT] | #23 |
  | D10 | Idade da pastagem calculada **localmente** em Python, não via asset GEE | #28 |
  | D11 | Áreas Mínimas Comparáveis (Ehrl 2017) para análise longitudinal | #25 |
  | D12 | Janelas temporais explícitas: face de **fronteira** (#35) + de **resolução** (#36) | #35, #36 |
  | D13 | "Terra convertível" = proxy MapBiomas com teto, em 3 definições | #39 |
  | D14 | Em cross-section estadual, reportar a **parcial controlando latitude** antes de atribuir efeito próprio — com **os mesmos controles nos dois lados** de qualquer comparação, e checando o **erro de medida do desfecho** antes de ler um nulo como ausência (revisto 21/jul/2026) | #40, #40B, #28C |
  | D15 | Alinhamento `fogo(t) ↔ conv(origem=t)` como contemporâneo | #41 |
  | D16 | Lead-lag de séries AMC integradas exige Toda-Yamamoto + placebos (Granger ingênuo fabrica precedência espúria) | #42 |
  | D17 | "Proteção" = malha vetorial de UCs (Proteção Integral × Uso Sustentável), proxy-teto no espírito da D13; PRODES validada (#48) e refino pixel fechados, MMA dispensada | #46 |
  | D18 | Custo de carbono por diferença de estoque (IPCC Tier 1) × densidades de C do Cerrado por formação (biomassa AGB+BGB, 3 cenários); solo (SOC) fora da manchete | #47 |
  | D19 | Todo ΔNorte de centroide vem com **IC95% por bootstrap de AMCs** (B=2000); um IC que inclui zero **nunca** é reportado como km (diga "ancorada") | #32, #44, #50 |
  | D20 | Para um desenho **shift-share** (choque nacional × exposição local) com **um único shifter**, o SE clusterizado é **otimista** (AKM 2019); a inferência correta é **permutação do shifter** (naive + circular), reportada junto com a bateria de placebos/lead/jackknife | #54 |
  | D21 | Toda **amostragem espacial** declara a fração que caiu fora do recorte pretendido; `region` derivada de `.envelope`/`.bounds` é armadilha silenciosa (o overlay posterior conserta o rótulo, não a alocação) | #28 |
  | D22 | **Sentinela de erro nunca compartilha código com categoria real**: `.fillna(<categoria>)` após `.map()` vira falha de configuração em dado. Condição estrutural (ex.: censura) é decidida por índice, jamais por sucesso de lookup | #28 |
  | D23 | Com **censo** (n = população), ΔBIC e p-valor deixam de medir evidência — a robustez vem de **estabilidade entre recortes**, e o ganho a reportar é a **precisão** dos parâmetros | #28, #28C |
  | D24 | Estatística **ponderada** deve reduzir *exatamente* ao caso não-ponderado com peso=1, verificado por teste — é o que garante que a diferença amostra × censo venha dos dados, não da implementação | #28 |
  | D25 | Antes de comparar uma medida de transição LULC entre períodos distantes, verifique que a **classe de destino manteve o mesmo significado**; diagnóstico barato = contar o destino **completo** das saídas e olhar *frações*, não níveis | #28D |
  | D26 | `agric ∪ mosaico` **não é correção**, é o **limite superior** de um bracket cujo inferior é `agric` só; reportar o **intervalo**, nunca um ponto — robusto ⇔ sobrevive nos dois extremos. A âncora dos anos terminais é a **SIDRA** (imune), não o bracket | #28D, #29, #32, #33, #40, #49 |

- **Os atos (a régua narrativa).** A periodização data-driven (Fase 5) cristalizou três
  **atos** em `config_periodos.py`: **I — Pastagem como herança (1985–2000)**, **II — Expansão
  e intensificação (2001–2019)**, **III — Conversão acelerada, mascarada (2020–2024)** —
  este último renomeado em 25/jul/2026, quando a auditoria mostrou que a "seletividade" era
  a mudança de rótulo do Mosaico, não o campo (ver o epílogo). Os **marcos**
  institucionais (Real, Kandir, Código Florestal etc.) recebem uma **tipologia evidencial**:
  **A** = evidência causal (só a Lei Kandir), **B** = referência narrativa (sem afirmação
  causal), **C** = limites da série (1985, 2024).

---

## Fase 0 — A primeira foto (nível estadual, descritivo)

**O momento.** No começo, antes do plano-mestre amadurecer, a pergunta era a mais simples
possível e mirava o nível mais agregado: *em Goiás, a área de pastagem e a economia se movem
juntas ao longo de 40 anos?* Não havia ainda ambição causal nem dado municipal — só a vontade
de ver a forma geral da série e montar a tubulação mínima (baixar, limpar, deflacionar,
plotar).

**`grafico_pastagem_pib_goias.py` (#1)** é literalmente o primeiro tijolo. Em quatro passos
ele baixa a planilha de estatísticas do MapBiomas Coleção 10.1 (estados/biomas), filtra Goiás
e a classe Pastagem; baixa o PIB estadual via SIDRA; baixa o IPCA e **deflaciona o PIB para
dez/2024**; e plota a pastagem sozinha e depois pastagem + PIB lado a lado. Mais importante do
que o gráfico: aqui já nascem duas convenções que o projeto inteiro herdaria — o **deflator
ancorado em dez/2024** e o **cache em `data/processed/`**.

**`analise_expandida_goias.py` (#2)** amplia a foto para um painel estadual de quatro vistas:
a cobertura do solo em cinco classes empilhadas; o rebanho bovino (SIDRA PPM 3939); a **taxa
de lotação implícita** (cabeças por hectare de pasto); e a participação do PIB agropecuário no
PIB total. É a "primeira foto" propriamente dita — e já insinua a hipótese que organizaria
tudo depois: a pastagem como protagonista que cresce, satura e começa a ceder, enquanto a
lotação sobe (sinal de intensificação).

O auxiliar **`_verificar_dados.py`** pertence a este momento: é um conferidor rápido que
imprime, para pastagem e rebanho estaduais, o valor em 1985, o pico (e o ano) e o valor em
2024. Serve de sanity check de bolso — o tipo de checagem informal que precede qualquer
análise séria.

**O que essa fase deixou claro.** As séries estaduais *existem*, são plausíveis e contam uma
história sugestiva. Mas o nível UF é grosso demais: ele esconde *onde* as coisas acontecem e
não permite controlar nada. Para responder "por quê" e "onde", era preciso descer ao
**município** — e para isso, construir uma base de dados de verdade.

---

## Fase 1 — A fundação: dados municipais brutos

**O momento.** Decidido que a unidade de análise seriam os 246 municípios de Goiás, a fase
seguinte é pura **engenharia de dados**: montar coletores robustos, com cache, schema
padronizado e validação, para cada fonte do plano-mestre. Nada de análise ainda — só a
matéria-prima, no nível certo e pronta para *join*.

**`coleta_sidra.py` (#3, e também #7 e a coleta do #15)** é o coletor unificado do IBGE. Um só
script baixa todas as tabelas SIDRA relevantes — lavouras temporárias (PAM 1612) e permanentes
(1613), milho 1ª/2ª safra (839), rebanhos (PPM 3939), leite (74), ovos (94), PIB e Valor
Adicionado (5938), população (6579), IPCA (1737) e o bloco estadual de abate (1092/1093/1094).
Com a flag `--censo-agro` ele coleta o **Censo Agropecuário 2017** (que vira o **Pipeline #7**:
plantio direto, veículos, calcário, orientação técnica); com `--so 839`, a safrinha. O script
padroniza tudo num schema comum (`cd_mun, nm_mun, ano, variavel, categoria, valor`), o que é a
condição de possibilidade de todos os *joins* posteriores.

**`pipeline_municipal.py` (#4)** faz o MapBiomas falar a mesma língua. A aba `COVERAGE_10.1` do
xlsx vem *wide* (uma coluna por ano), mistura biomas (Cerrado + Mata Atlântica nos municípios
de fronteira) e — crucial — **só traz o nome do município, não o código IBGE**. O pipeline
derrete para *longo*, soma os biomas e faz o *merge* com a lista canônica de municípios do
SIDRA para recuperar o `cd_mun`. O produto, `mapbiomas_munis_goias.csv`, é a espinha dorsal de
quase tudo que vem depois (taxas, mapas, transições).

**`coleta_sicor.py` (#6)** baixa o crédito rural do SICOR/BACEN via OData, 2013–2026, em cinco
entidades (custeio e investimento municipais; custeio, investimento e comercialização
estaduais). A docstring registra as idiossincrasias do Olinda/BACEN descobertas na marra (o
`$filter` exige `%20`, `$skip`/`$orderby` não funcionam, o código de Goiás no BACEN é '10' e
não 52). O auxiliar **`_validar_sicor.py`** fecha o ciclo: confere o total municipal contra o
total UF, identifica municípios faltantes contra a lista de 246 e checa a ordem de grandeza —
é a desconfiança metódica aplicada ao coletor.

**`coleta_idhm.py` (#13)** traz o IDH-M e sub-índices via API do IPEA Data, cobrindo os anos
de Censo Demográfico (1991/2000/2010), com instruções de *fallback* manual para 2021 (que a
API municipal não tem). É a única peça de "desenvolvimento humano" da base — guardada para o
fio "crescimento sem desenvolvimento?" que ainda está em aberto.

**`fogo_mapbiomas.py` (#14, coleta)** computa área queimada — total e por classe LULC — para os
246 municípios, 1985–2024, via Google Earth Engine sobre os assets do MapBiomas Fire
Collection 4. Antes dele veio o auxiliar **`explorar_asset_fogo.py`**, uma sondagem dos assets
(bandas, valores de pixel, estrutura) — o passo prudente de *entender o dado remoto* antes de
escrever o coletor de produção. A contraparte analítica, **`analise_fogo.py`** (#14-análise),
produz a série estadual, a proporção por classe, o top-10 municipal e o mapa de fogo
acumulado.

**`analise_safrinha.py` (#15)** é a leitura descritiva do milho 2ª safra — o vetor central da
intensificação pós-2010 (um segundo ciclo na mesma área, tipicamente após a soja precoce).
Calcula a razão milho2/milho1 por município e período, antecipando o tema "intensificar em vez
de expandir" que voltaria com força na Fase 6.

**`coleta_trase.py` (#27)** integra os dados de cadeia produtiva da Trase.earth (soja 2004–2022,
boi 2011–2023) agregados por município-ano, mapeando os nomes Trase (caixa-alta, sem acento) para
`cd_mun` — um de-para que acerta 100% (zero linhas órfãs em 646 mil). A docstring original declarava
um limite que, dois meses depois, se revelou **falso para a soja**: a premissa "a Trase rastreia só
o fluxo exportador" vale para o boi, mas **44,6% do volume de soja é `PROCESSED DOMESTICALLY`**
(esmagamento no Brasil, destino BRAZIL, FOB = 0). Somar tudo devolvia **produção**, não
infraestrutura — `trase_soja_volume_t` tem `r = 0,986` com a área plantada. O schema hoje separa
`_volume_export_t` de `_volume_domestico_t`, e essa descoberta **corrigiu o #45** (Fase 6). É o
lembrete de que uma premissa herdada da docstring é uma hipótese, não um fato.

Dois auxiliares de coleta completam a fundação. **`coleta_pib_uf_ipea.py`** baixa as séries
estaduais nativas do IPEA (PIB e VAB agropecuário, encadeadas pelas Contas Regionais), que
cobrem **1985–2023 sem lacunas** — uma série muito melhor que o agregado municipal do SIDRA,
que só começa em 2002 (essa troca, depois, fez o N das correlações UF saltar de ~21 para ~37).
E **`estimativa_abate_municipal.py`** distribui o abate estadual (que só existe em nível UF)
proporcionalmente ao rebanho municipal — uma estimativa explícita e simples (`abate_muni =
rebanho_muni/rebanho_UF × abate_UF`), com a premissa de taxa de abate uniforme declarada.

**O que essa fase deixou pronto.** Um conjunto de CSVs municipais limpos, padronizados e
validados — LULC, lavouras, pecuária, crédito, fogo, IDH-M, cadeia exportadora, abate. A
matéria-prima estava no nível certo. A pergunta natural passou a ser: *o que esses dados
mostram quando cruzados e postos no mapa?*

---

## Fase 2 — Primeiras leituras municipais, cartografia e transições

**O momento.** Com a base municipal pronta, vêm as **primeiras análises substantivas** e a
**cartografia exploratória**. É aqui também que o projeto faz uma descoberta metodológica que
o reorienta: a diferença entre *inferir* transições a partir de estoques e *medi-las*
pixel-a-pixel.

**`analise_pastagem_soja.py` (#5)** é a primeira camada analítica municipal. Cruza
`mapbiomas_munis_goias.csv` (#4) e a soja do SIDRA (#3) para medir, por município e por
período, quanto de pastagem virou soja — com métricas como `taxa_conversao` (Δsoja / |Δpasto|)
e validação cruzada entre as duas fontes. É importante notar o que ele é: um **proxy** de
transição baseado em variação de estoques (a pastagem caiu *e* a soja subiu no mesmo
município), não a medição direta de qual pixel virou o quê. Essa limitação é exatamente o que
motivaria o #12.

**`analise_credito_uso_terra.py` (#8)** dá o primeiro passo na direção da pergunta econômica:
cruza o crédito SICOR (#6) com a mudança de uso (#4), construindo crédito por hectare de pasto
e correlações descritivas na janela de sobreposição 2013–2023. Daqui saiu um problema
diagnóstico que rendeu o auxiliar **`auditoria_pib.py`**: havia uma discrepância de ~38% no
PIB entre o painel do #8 e o painel unificado (#16); o script isola empiricamente a causa
(razão por município-ano) em vez de aceitar a explicação plausível-porém-errada. É a cultura
de auditoria do projeto em miniatura.

A cartografia entra em três peças. **`gerar_mapas_lulc_40anos.py` (#9)** produz 40 mapas
coropléticos municipais (área por classe), apoiado no auxiliar **`_cartografia.py`** — um
módulo compartilhado que padroniza a rosa-dos-ventos e a escala de todos os mapas da
dissertação. **`gerar_mapas_lulc_gee_40anos.py` (#10)** vai além do coroplético e renderiza 40
mapas **raster de 30 m** direto do GEE, com as 6 classes; seu auxiliar
**`_preview_mapa_2024.py`** gera variantes do mapa de 2024 para escolha estética (reusando o
raster já baixado, sem rechamar o GEE). **`gerar_gif_lulc.py` (#11)** costura os 40 PNGs num
GIF animado — a forma mais imediata de *ver* os 40 anos de conversão. Como estudo de caso, os
auxiliares **`gerar_mapas_lulc_gee_rio_verde.py`** e **`gerar_gif_lulc_rio_verde.py`** repetem
o procedimento para o município de Rio Verde (o coração do agronegócio goiano), com contorno
municipal e vizinhos — um zoom que torna concreto o que o estadual mostra no atacado.

**`transicoes_mapbiomas.py` (#12)** é a virada metodológica da fase. Em vez de inferir
transições de estoques (como o #5), ele computa a **matriz de transição A→B pixel-a-pixel**
via GEE, cruzando a classe-origem e a classe-destino de cada pixel entre pares de anos. Antes
dele, o auxiliar **`explorar_asset_transicao.py`** sondou o asset de transição do MapBiomas e
testou a abordagem em um município contra o #4. O #12 **substitui o #5 como fonte de verdade**
sobre fluxos: agora se sabe não só que a pastagem caiu e a soja subiu, mas que tantos hectares
de *pasto* viraram *agricultura* e tantos de *vegetação* viraram *pasto*. O auxiliar
**`visualizar_transicoes.py`** explora essas matrizes (heatmaps 6×6, Sankey 1985→2024, mapas
de transição dominante e de estabilidade) e compara explicitamente o proxy (#5) com o
pixel-a-pixel (#12).

**Nota de 27/jul/2026 — esta matriz foi refeita.** A tradução ID→grupo do #12 manda o que não
está na lista para `0` e mascara; a classe 21 (Mosaico de Usos) não estava na lista. O pixel que
saía de pastagem para Mosaico não virava "pasto→outros" — **sumia da matriz inteira**, do
numerador e do denominador. Enquanto o Mosaico foi pequeno isso era resíduo; a partir de 2021
ele passou a carregar o fluxo (#28D), e a matriz mostrava a conversão *parando* justamente onde
ela acelerava. O **`transicoes_cubo.py` (#12B)** reconta tudo com **7 grupos** a partir do cubo
censitário local do #28 — sem GEE, 13 min —, e a `validar_transicoes_cubo.py` separa o que mudou
por causa do conserto do que mudou por causa do instrumento. É esta a matriz primária desde
então; os heatmaps viraram 7×7.

**`agregar_conversoes.py` (#19)** fecha a fase preparando o fluxo para análise. Rodando o #12
com a flag `--consecutivos` (39 pares ano-a-ano), ele agrega as matrizes para os níveis UF e
municipal, validando o total contra a área de Goiás (±15%). Aqui foi corrigido um bug
revelador (maio/2026): os caches do GEE já vêm com IDs agrupados 1–6, não com os IDs brutos do
MapBiomas — o que fazia o CSV exportar 2×2 em vez de 6×6. O conserto entregou as 36 transições
por ano-par, base de toda a análise de fluxo posterior (#29c, #31, #33).

**O que essa fase deixou claro.** Já dava para *ver* a conversão no mapa e *medir* o fluxo
pixel-a-pixel. Mas as peças estavam espalhadas em dezenas de CSVs com recortes e janelas
diferentes. Para fazer estatística séria — correlação, painel, regressão espacial — era
preciso **uma tabela única**, alinhada por `cd_mun × ano`, com tudo dentro.

---

## Fase 3 — Consolidação: o painel unificado e as taxas de variação

**O momento.** Esta é a fase de **integração**. O objetivo é transformar a coleção de CSVs num
único objeto analítico — e, em paralelo, transformar os estoques de área em **taxas de
variação** (que é o que a teoria e a inferência realmente pedem).

**`construir_painel_unificado.py` (#16)** consolida em uma tabela *wide* (`cd_mun × ano`,
9.840 linhas × 185 colunas) todas as fontes prontas: LULC, pecuária, lavouras, PIB,
população, SICOR, Censo 2017, IDH-M, fogo, Trase. A docstring é um pequeno tratado de honestidade
metodológica: declara o universo (246 munis), a janela (1985–2024, com NaN onde a fonte não
cobre), a deflação, o tratamento do Censo 2017 como atributo **estático**, e — o ponto
decisivo — alerta que **25% dos municípios surgiram depois de 1985**, o que torna o painel
adequado para análises transversais mas **perigoso para longitudinais**. Esse alerta é a
semente do #25. O auxiliar **`validar_painel_unificado.py`** submete o painel a quatro camadas
de validação (integridade interna; agregação município→UF contra gabaritos internos; contra a
fonte original; e validação cruzada entre fontes, ex. MapBiomas × PAM para soja), com *exit
code* pronto para CI.

**`mapeamento_mesorregioes.py` (#18)** é uma peça pequena e estrutural: via geobr, mapeia cada
`cd_mun` para sua **mesorregião IBGE 2017** (5 unidades em Goiás). A decisão D6 — mesorregiões
e não Regiões Geográficas Imediatas (que pulverizariam o estado em 133 unidades) — é o que
torna possível, mais tarde, a leitura regional Sul→Norte.

**`calcular_taxas_lulc.py` (#17)** é talvez a peça analítica mais reutilizada do projeto.
Transforma os estoques de área (do #4) em **métricas de variação**: delta ano-a-ano, *slope*
de janela móvel de 5 anos (em duas versões, *trailing* e *centrada* — D3), erro-padrão HAC
Newey-West (D4) e aceleração (D5). Produz tudo em três níveis — UF, município, mesorregião. As
decisões D1–D5 vivem aqui, e quase toda a Fase 4 e a Fase 6 consomem este script. **`figuras_taxas.py`
(#20)** é sua vitrine: gera as figuras de slope com faixa de confiança e marcos, as
mesorregiões sobrepostas, o delta empilhado e os coropléticos de períodos-chave.

**`construir_amc_goias.py` (#25)** resolve o problema que o #16 havia diagnosticado. É a
implementação da **Decisão D11**: agrupa cada município-pai com seus filhos emancipados em
**Áreas Mínimas Comparáveis** de território constante (concordância de Ehrl 2017, pronta no
`geobr.read_comparable_areas`), colapsando os 246 municípios em **166 AMCs**. A regra de ouro
do pipeline é a distinção entre variáveis **extensivas** (somáveis — hectares, cabeças, R$:
agregadas por soma, o que neutraliza o salto da emancipação) e **derivadas** (razões e
densidades: *recalculadas* a partir das extensivas já agregadas, nunca somadas). O produto,
`painel_amc_goias.parquet` (mais a geometria `amc_goias.gpkg`), torna-se a **unidade canônica
de toda análise longitudinal** — e, sem que ninguém previsse na época, o palco da Fase 6
inteira. O auxiliar **`verificar_amc_goias.py`** é uma verificação independente impressionante:
exige que as 113 AMCs de um único município reproduzam *exatamente* a linha municipal original
(inclusive o padrão de NaN), re-agrega manualmente uma amostra célula a célula, confere as
razões recalculadas e testa contiguidade espacial. Se a lógica do #25 tivesse qualquer erro,
esses testes quebrariam alto.

**O que essa fase deixou pronto.** Duas tabelas-mãe (`painel_unificado` para o transversal,
`painel_amc_goias` para o longitudinal) e um motor de taxas. A infraestrutura empírica estava
completa. Agora — finalmente — dava para perguntar *com rigor estatístico*: as associações que
a primeira foto sugeria sobrevivem a controles?

---

## Fase 4 — Inferência estatística

**O momento.** Com painel e taxas, o projeto passa do "ver" para o "testar". A fase percorre
uma escada de exigência crescente: correlação em diferenças (UF) → painel com efeitos fixos
(município) → quase-experimento (DiD com controles) → estrutura espacial dos resíduos →
quebras estruturais data-driven. Cada degrau responde a uma fragilidade do anterior.

**`correlacoes_uf.py` (#21)** começa modesto e correto: correlaciona as taxas LULC (#17) com
variáveis socioeconômicas no nível estadual, **sempre em primeiras diferenças (D7)** e com
erros HAC, testando lags 0/1/2. É aqui que a troca da série de PIB municipal pela série nativa
do IPEA (`coleta_pib_uf_ipea.py`) paga dividendos — o N por par sobe de ~21 para ~37 e surge
um par novo significativo (Δvegetação natural × ΔPIB defasado). Mas correlação em UF tem N
pequeno e nenhum controle de heterogeneidade: é só o primeiro degrau.

**`correlacoes_painel.py` (#22)** sobe o degrau decisivo: **painel municipal 2-way FE (D8)** —
`Δlulc_it = α_i + γ_t + β·Δx_it + ε_it` — com efeitos fixos de município (absorve tudo o que é
fixo do lugar) e de ano (absorve choques comuns), SE clusterizado. O achado robusto é a
**intensificação**: Δagricultura × ΔVA agro sobrevive a todas as variantes; e, no modelo
multivariado, o **SICOR aparece como canal dominante de retração da pastagem** (β≈−0,003,
p<0,001, na janela com SICOR 2013–2021 — ~8 anos, não os 40). Os resíduos deste painel não são jogados fora — viram insumo do #24.

**`piecewise_did.py` (#23)** monta o quase-experimento (D9): Goiás como tratado, Mato Grosso e
Tocantins (mesmo bioma Cerrado) como controles, em janelas de ±5 anos ao redor de cada marco.
Ganhou depois *event-study* e *placebo*, e uma decisão importante: **Tocantins é o controle
mais credível** (Cerrado, sem a soja amazônica de MT). O resultado disciplinador: dos vários
efeitos testados, **só Vegetação natural × 1995 vs TO sobrevive** ao conjunto parallel-trends +
placebo + DiD significativo. Os efeitos pós-2012/2018 têm placebos significativos — ou seja,
refletem dinâmica pré-existente, não o marco. Foi esse rigor que levou ao rebaixamento do
"PAC Cerrado" (rótulo de rascunho sem programa real) e à cautela com o Código Florestal.

**`analise_espacial.py` (#24)** pergunta se a inferência do #22 está completa: os resíduos têm
**autocorrelação espacial**? Calcula Moran's I global por (modelo, ano, matriz W), mapeia
clusters LISA, e roda regressão espacial (OLS vs SAR vs SEM via `spreg`). A resposta é
inequívoca — **115 de 140 resíduos têm I significativo**: a estrutura espacial é *estrutural*,
não ruído. Isso justifica, lá na frente, levar a sério a dimensão espacial (vizinhança,
spillover) no #34.

**`deteccao_quebras.py` (#26)** inverte a lógica do DiD. Em vez de testar marcos pré-definidos
(viés de confirmação), deixa os **dados apontarem onde estão as quebras** (Quandt-Andrews
sup-F + binary segmentation) em GO e TO, e só *depois* confere se coincidem com marcos
teóricos. Achados que reorganizaram a narrativa: o **Código Florestal 2012 não tem quebra
empírica** em GO nem TO; a inflexão da vegetação natural em GO é **1998 (Lei Kandir)**, não
1994 (Real); várias quebras (1991, 2020) ficaram "órfãs" — sem marco atribuído — o que viraria
combustível para a Fase 6 (o #37 mostraria que 1991 é o colapso de crédito do Plano Collor).

**O que essa fase deixou claro.** As associações sobrevivem a controles sérios — mas com
qualificações importantes: a intensificação é o sinal forte; muitos "efeitos de marco" não
resistem a placebo; e há quebras empíricas que *não* batem com as datas que a literatura
esperava. Isso gerou um desconforto produtivo: **se os marcos teóricos não organizam bem a
série, qual é a periodização real?** Era preciso deixar os dados definirem os "atos".

---

## Fase 5 — Periodização data-driven (os "atos")

**O momento.** A Fase 4 mostrou que pendurar a narrativa em datas de leis era frágil. A Fase 5
constrói uma periodização **a partir dos próprios dados**, por triangulação de métodos
independentes — e, em paralelo, investiga a *assinatura* mais fina do mecanismo de conversão
(a idade da pastagem).

O **Pipeline #29** é uma triangulação de três métodos sobre as séries de GO:
**`periodizacao_multivariada.py` (#29a)** aplica o sup-F multivariado (Bai-Lumsdaine-Stock) ao
**vetor conjunto** (Δveg, Δpasto, Δagric) — detecta mudanças de *regime*, não de série
isolada; **`periodizacao_stars.py` (#29b)** usa o teste sequencial de Rodionov (STARS), que
pega regimes curtos que o sup-F pode perder; **`periodizacao_transicoes.py` (#29c)** compara as
*matrizes de transição* antes/depois de cada ano-candidato via divergência KL e autovalores,
com significância por bootstrap de permutação. A convergência dos três cristaliza **três
períodos**: I (1985–2000), II (2001–2019), III (2020–2024).

Esses números não foram aceitos sem auditoria. **`verificacao_periodizacao.py` (#30)** testa a
**taxa de falso positivo** (rodando os métodos sobre ruído branco), a sensibilidade a
parâmetros (min_size × F_threshold) e a consistência univariado vs multivariado: 2001 é robusta
em todas as combinações; 1991 é instável; STARS só detecta com α=0,05. E **`intensity_analysis.py`
(#31)**, implementando o método de Aldwaik & Pontius (2012), testa se P2 e P3 diferem em *taxa*
de mudança, em três níveis (intervalo, categoria, transição); **`verificacao_intensity.py`**
acrescenta consistência de dados, poder estatístico (n=4 é pouco) e bootstrap de IC. O
resultado é deliberadamente cauteloso: a fronteira **2005/2006** — visível por STARS e KL —
**não** virou período, porque o método primário não a detecta e a diferença de taxa total entre
as sub-fases não é significativa (p=0,060). Ela ficou registrada como **nota metodológica**: a
sub-fase 2001–05 perde vegetação natural ~5× mais intensamente (p=0,0008) — um micro-mistério
que só seria parcialmente fechado no #41.

Toda essa decisão é congelada em **`config_periodos.py`** — a fonte única de verdade que define
os `ATOS` e os `MARCOS` (com a tipologia evidencial A/B/C). A partir daqui, #20, #23, #28, #31
e toda a Fase 6 importam os atos daqui, em vez de cada script chutar suas próprias datas.

Em paralelo, o **Pipeline #28** investiga a assinatura fina do mecanismo.
O **#28** varre **todos** os pixels que sofreram a transição pasto→agricultura em Goiás —
**44,6 milhões de eventos**, 11,2% do estado — e para cada um calcula **há quantos anos aquela
pastagem existia no momento da conversão**, com a idade computada **localmente em Python** a
partir das 40 bandas anuais (Decisão D10, que evita estourar o limite do GEE encadeando 35+
operações). Até jul/2026 isso era uma amostra de 2.000 px/ano; virou censo depois que a
amostra se mostrou enviesada na composição entre anos. A hipótese é a
"pastagem como reserva de terra": uma pastagem jovem convertida sugere mecanismo *premeditado*
(plantar pasto já pensando em virar lavoura); uma pastagem velha sugere mecanismo
*oportunístico*. **`analise_reserva_terra.py` (#28B)** descreve a distribuição e encontra o
achado-chave: no período recente a idade é **bimodal** — picos em ~4 e ~23 anos — a
assinatura empírica direta da *coexistência* dos dois mecanismos. E um gradiente regional parecia
aparecer: o Sul convertendo pasto jovem (mediana ~9 anos), o Norte/Noroeste pasto antigo (~20
anos). (*Quanto* desse gradiente é causa regional vs mera composição seria medido depois, no #28C
— Fase 6: a geografia modula o peso, não causa a bimodalidade. ⚠️ **E o gradiente em si não
sobreviveu**: a auditoria da mudança de rótulo, em julho de 2026, mostrou que ele existe apenas
dentro do subconjunto rotulado "agricultura" — ver o epílogo. O que resta desta passagem é a
**bimodalidade**, que é robusta.)

**O que essa fase deixou pronto.** Uma régua temporal honesta (os atos), uma régua de marcos
com graus de evidência, e uma pista forte de que existem **dois Goiáses** — um Sul que
intensifica e um Norte que abre fronteira. Essa pista é o que disparou a investigação que
organizaria tudo. (A pista se confirmou; a *qualificação* pela idade do pasto — "Sul jovem,
Norte velho" — é que não sobreviveu à auditoria de julho de 2026. O contraste real está no
**tipo de transição**: `pasto→agric` ao sul × `veg→pasto` ao norte, medido por um fluxo imune.)

---

## Fase 6 — A marcha ao norte: a investigação Sul→Norte

**O momento.** Todas as fases anteriores convergem aqui. A hipótese-mãe, formulada em
junho/2026, era forte: *a pressão da agricultura no Sul empurra pasto e rebanho para o
Norte/Noroeste — um deslocamento de fronteira, um iLUC intra-estadual.* A Fase 6 testa essa
hipótese em camadas, e o que acontece é exemplar do método do projeto: a hipótese é
**refinada, depois parcialmente refutada, depois reconstruída** numa forma mais defensável.
Tudo roda sobre o painel AMC (#25), que neutraliza a emancipação.

### Camada 1 — O padrão existe? `centro_massa.py` (#32)

A peça-chave (*keystone*). Para cada variável (pastagem, agricultura, rebanho, vegetação) e
cada ano, calcula o **centro de massa ponderado** (mean center) usando os centroides das 166
AMCs como posições e o valor da variável como peso; acompanha o **centro mediano** (Weiszfeld,
robusto ao puxão do cluster agrícola do Sudoeste) e a **elipse de desvio-padrão** por ato. O
resultado **refina e em parte contraria** a hipótese-mãe: não é "agricultura estática × pasto
subindo" — **toda a fronteira agropecuária marchou ao norte** (pastagem +78 km, rebanho +67
km, agricultura +65 km; só a vegetação natural ficou quase parada, +8 km). Mas três coisas
*sustentam* a narrativa: (a) há um **gradiente latitudinal persistente** — a agricultura fica
~120–130 km ao sul de pasto/rebanho *em todos os anos*; (b) a **pastagem lidera** o avanço; e
(c) **só no Ato III (2020–24) a agricultura desacelera** enquanto pasto e rebanho seguem
subindo — o sinal de deslocamento mais limpo, e é recente.

### Camada 2 — Qual o mecanismo? `transicoes_regionais.py` (#33)

Se o centroide se moveu, *qual transição, em qual região*, o moveu? Este pipeline re-corta as
conversões brutas (#19) por **mesorregião × ato**, reusando a maquinaria de
**`analise_transicoes.py`** — o módulo (rascunhado originalmente como "#25", número depois
reatribuído ao AMC) que monta as matrizes 6×6 por ato, a decomposição de origem e os Sankey, e
que alimenta também a Visualização. O mecanismo se confirma como **gradiente relativo**: a
transição-mãe de Goiás é `veg→pasto` (pervasiva); `pasto→agric` só *lidera* no Sul+Centro no
Ato II (o boom). O deslocamento aparece no **balanço líquido**: no Ato II o Sul *perde* pasto
líquido (−0,57 Mha) e ganha agricultura, enquanto Norte/Noroeste ganham pasto — essa é a parte
sólida, e a janela do Ato II (2001–2019) fecha antes de qualquer problema de rótulo.

> ⚠️ **As duas leituras do Ato III desta camada caíram na auditoria de julho de 2026** (ver o
> epílogo, e `pipelines/33_transicoes_regionais.md`). A primeira era que "no Ato III o
> `pasto→agric` do Sul **despenca −88%**, e a agricultura desacelera": sob o bracket da D26 esse
> número **inverte para +51%**, e a soja plantada da SIDRA — imune ao classificador — sobe 244%
> no Sul. A segunda era a idade do pasto no Ato III (Sul **16 anos**, Norte **27**, Noroeste
> **31**), que sob a régua superior **inverte a ordenação** (Sul 32a, Norte 23a). O que sobrevive
> desta camada é o `veg→pasto` do Norte persistindo — medida **imune**, porque nem origem nem
> destino passam pelo Mosaico — e é ela, não o `pasto→agric`, que sustenta o contraste "o Sul
> trava, o Norte avança" usado adiante pelo #39.

Nos Atos I e II a censura à esquerda consome a mediana da idade (o Sul tem 70,9% de censura porque
converteu cedo, não porque tem pasto velho), então **não** há série temporal de idade a narrar.
Revisado em 21/jul/2026; ver §7.3 de `metodologia/censo_vs_amostra.md`.

### Camada 3 — É deslocamento causal? `deslocamento_espacial.py` (#34)

O teste formal — e o resultado mais importante da fase. Em **tempo contínuo** (sem binar por
ato, para evitar circularidade com o #29), faz duas perguntas: **(A) temporal** — a expansão da
agricultura no Sul *antecede* o avanço de pasto/rebanho no Norte? (lead-lag por CCF + Granger,
com teste reverso); **(B) espacial** — a agricultura dos *vizinhos ao sul* prevê o crescimento
de pasto local? (SLX em painel 2-way FE com peso direcional; placebo = vizinhos ao norte). O
veredito é de **não-confirmação**: (1) **sem precedência temporal** (Granger ΔAgric_Sul →
ΔPasto_Norte p=0,97 — nulo **robusto ao bracket D26**, 0/24 células significativas); (2) **sem spillover direcional** (θ=−0,16, *oposto* do previsto e negativo em 12/12 réguas × janelas, **embora a significância não sobreviva ao bracket** — vizinhos
ao sul co-expandem, não empurram); (3) mas **substituição local forte** (Δagric→Δpasto β=−0,52
— onde a lavoura entra, o pasto sai *localmente*: intensificação, confirmando o #22). A leitura
defensável: **não é iLUC causal, é reorganização espacial** — dois mecanismos locais paralelos
(intensificar no Sul, abrir fronteira no Norte) sob um mesmo impulso macro, sobre um gradiente
de aptidão. Daí a regra de redação: nunca dizer "deslocamento" sem qualificar; usar
"reorganização espacial" ou "marcha ao norte da fronteira". O nulo aqui é **força, não
fraqueza** — refuta uma hipótese tentadora e errada. (Um detalhe ficou pendente: o *teste
reverso* desse lead-lag deu um resultado isolado e significativo — ΔPasto_Norte → ΔAgric_Sul,
p=0,0007 — que, se real, *inverteria* a leitura. O #34 o descartou só com "N pequeno"; foi essa
ponta solta que o **#42** mais tarde puxou e fechou.)

### Robustez — `robustez_janelas.py` (#35) e `robustez_janela_slope.py` (#36)

Antes de seguir, à prova de banca: os achados dependem de *onde cortamos o tempo*? O **#35**
(face de **fronteira** da D12) recalcula as métricas-manchete do #32/#33 sob três réguas —
atos, grade regular de 5 anos (exógena), décadas. Robusto: o pasto marcha ao norte em todos os
esquemas; o gradiente Sul(pasto→agric)/Norte(veg→pasto) vale em quase todas as janelas. A única
sensibilidade — a desaceleração recente da agricultura é nítida só nas réguas que isolam
2020–24 — *confirma* que o fenômeno é pós-2020. O **#36** (face de **resolução** da D12)
recalcula os slopes do #17 sob quatro larguras de janela móvel (3/5/7/10 anos): a desaceleração
da vegetação e a freada da agricultura sobrevivem a tudo; o "pico da pastagem em 2004" do
*trailing* revela-se artefato de atraso — a versão **centrada** fixa o pico em ~2002–03; e a
aceleração (D5) confirma-se a métrica mais frágil (só o pico de pastagem de 2004 sobrevive às
quatro janelas).

### O drive comum — `coleta_drivers_macro.py` + `drive_comum.py` (#37) e `drive_comum_amc.py` (#38)

O #34 atribuiu o co-movimento a um "drive comum" que ficou **inferido, não testado**. O #37 o
materializa. **`coleta_drivers_macro.py` (#37A)** coleta os drivers macro **exógenos** via IPEA:
preços internacionais de soja/boi/milho (IMF IFS), **câmbio real efetivo** (REER, que contorna
a troca de moedas pré-1994), câmbio nominal e o crédito rural longo de GO (CREATE, que faz a
ponte com o SICOR 2013+); e constrói o **"preço recebido"** = preço internacional × câmbio.
**`drive_comum.py` (#37B)** testa, na série UF/anual e em primeiras diferenças, se as viradas
dos drivers *antecedem* as inflexões do LULC, com um placebo de exogeneidade engenhoso (a taxa
LULC **não** deve Granger-causar o preço internacional — e não causa). Achados: **câmbio e
crédito antecedem** o LULC (câmbio→pastagem e →rebanho do Norte; crédito→agricultura e
→vegetação), enquanto o **preço co-move contemporaneamente mas não lidera**; a órfã 1991 do #26
ganha nome — **colapso de crédito do Plano Collor (−56%)**. O limite é honesto: N≈38, e os
~7 *hits* em ~135 testes não sobrevivem à correção de multiplicidade — só o câmbio tem
estrutura, por reaparecer em duas margens.

**`drive_comum_amc.py` (#38)** não repete o erro de espremer a série agregada: **muda a unidade
de análise** para o painel AMC (~6.600 obs) e, com isso, a *estratégia de identificação*. Como
o driver é nacional (mesmo número para todas as AMCs num ano), não se testa "o driver mexe o
LULC?" mas **"o choque comum bate mais forte onde a exposição é maior?"** — via interação
**driver × exposição baseline** em 2-way FE (o efeito fixo de ano absorve o choque comum; a
interação isola o gradiente). Com clusterização dupla, um conjunto confirmatório teórico e uma
grade exploratória sob FDR (a lição de multiplicidade do #37), o achado é **sóbrio**: a
hipótese **câmbio × fronteira → rebanho** confirma a direção, mas a grade completa
(com lag 2) não devolve nenhum sobrevivente do FDR — e o `p=0,031` que este pipeline reportava é
o **erro-padrão clusterizado**, otimista para um shifter nacional único: sob **permutação do
shifter** (#54, D20) ele sobe para **≈0,07–0,13, não significante a 5%**. O gradiente câmbio ×
aptidão na pecuária de fronteira é, portanto, **corroborante, não achado estabelecido** — a
Camada 5 avança, não fecha.

### A oferta de terra — `fronteira_fechando.py` (#39)

Até aqui, tudo foi *demanda* (preço, câmbio, crédito). O #39 testa a perna de **oferta**: a
desaceleração recente seria o **estoque de Cerrado convertível se esgotando**? O sinal de
partida vem do #32 — *tudo* marchou ao norte menos a vegetação natural (ancorada), coerente com
uma fronteira que recua à medida que o estoque ao sul se exaure. Com a Decisão D13 (convertível
= proxy MapBiomas com teto, em três definições) e três blocos — estoque/depleção por região;
hazard (`perda/estoque_{t−1}`) em painel FE; decomposição exata Δfluxo = h̄·Δestoque +
estoquē·Δhazard — o veredito é **escalonado e surpreendente**: no agregado estadual a fronteira
**não** fechou (resta ~60% do convertível; o fluxo de conversão não desacelerou, só **migrou ao
norte**), mas **regionalmente fechou no Sul** (estoque baixo, 53% de 1985, e hazard caindo =
giro à intensificação, coerente com o `pasto→agric` do Sul despencando, #33). Crucial: a
demanda **subiu** no Ato III (câmbio, preço, crédito todos em alta) — logo a desaceleração
agrícola do Sul ocorreu **sob demanda forte**, o que é a assinatura de uma restrição de
**oferta**. A "marcha ao norte" do #32 é, em parte, a fronteira **perseguindo o estoque que só
resta no norte**.

### As duas lógicas da pastagem — `duas_logicas_pastagem.py` (#40)

Puxa o fio do #28 ao nível espacial. Espacializa a mistura de mecanismos (Rotação jovem ×
Oportunístico antigo) por AMC e município, cruza com plantio direto (Censo 2017) e propõe uma
tipologia de "carreira da terra". O achado que **parecia** robusto era a **geografia das duas
lógicas** — a Rotação (pasto jovem) dominando o Sul/Centro e o Oportunístico (pasto antigo) o
Norte, as duas como **faces do gradiente de aptidão Sul→Norte** (índice jovem × latitude
r=−0,236 no censo; a amostra dava −0,49).

> 🛑 **Esse achado caiu — e é a autocorreção mais dura da perna.** O bracket-por-evento (julho de
> 2026) mostrou que o r=−0,236 vive **inteiramente dentro do rótulo "agricultura"**: redefinindo
> a conversão como `pasto→(agric∪mosaico)`, o ρ vai a **≈0 e não-significante nas três janelas**
> testadas. A união triplica o número de eventos — as conversões que passaram a ser rotuladas
> Mosaico são a *maioria* dos términos de pastagem, e elas não carregam gradiente nenhum. O
> mesmo veredito veio, independentemente, do #28C e do #33. **A segregação geográfica das duas
> lógicas não está estabelecida**; o que está é a **coexistência** dos dois mecanismos dentro de
> cada região. Ver o epílogo e `pipelines/40_duas_logicas_pastagem.md`.

Mas este pipeline é também um caso-modelo de **autocorreção** por outro motivo: a primeira leitura
anunciou que "a lógica é estrutural (plantio direto), não de fluxo", e a *verificação no mesmo
dia derrubou o overclaim*. Controlando latitude (correlação parcial), o cruzamento no-till ×
idade colapsa. A contribuição sólida é a *geografia da bimodalidade*, não um driver
estrutural — o plantio direto **co-localiza** com a lógica jovem. Daí a **Decisão D14**: em
cross-section estadual, sempre reportar a parcial controlando latitude antes de atribuir
efeito próprio.

Em 21/jul/2026, ao migrar o #40 para o **censo** do #28, essa passagem ganhou uma segunda
camada — e ela é mais interessante que a primeira. O "nada sobrevive" **não era achado, era
artefato de medição**: a idade mediana municipal vinha de ~26 pixels, e erro de medida no
desfecho atenua a correlação em direção a zero. Com a mesma composição e o censo, a parcial
2D vai de p=0,413 a **p=0,031**. O veredito honesto passa de "não há efeito próprio" para
**"não estabelecido"** (p≈0,058 em n=209; nada sobrevive a FDR-BH). Além disso, a comparação
estrutura × fluxo estava **assimétrica** — estrutura levava controle 2D e fluxo só 1D. Posta
em pé de igualdade, ela *confirma* a leitura antiga: o único sinal que resiste a controle 2D,
troca de fonte e multiplicidade é o **Δ SICOR** (fluxo, p=0,001), não a estrutura. A lição que
fica é de método: **antes de ler um nulo como ausência, medir o ruído do desfecho** — um nulo
sobre desfecho ruidoso é indistinguível de falta de poder.

### O fogo — `fogo_lidera_fronteira.py` (#41)

A quinta perna descritiva traz o fogo (#14), até então fora da narrativa, para dentro dela: o
**centroide do fogo lidera a marcha ao norte**? O pipeline navega explicitamente uma armadilha
— queimar o Cerrado *é*, muitas vezes, o ato de abri-lo para pasto, então um "fogo lidera por
~1 ano" seria em parte *definicional* (blindagem: o efeito fixo de ano absorve o clima comum, e
o fogo em vegetação é 5–15× maior que a conversão do mesmo ano, sendo portanto um sinal mais
amplo). O veredito é **escalonado**: (1) **espacialmente** o fogo é uma **vanguarda robusta** —
está ao norte da conversão em **39/39 anos** (+73 km), e ao norte do próprio estoque de
Cerrado; (2) **temporalmente no agregado é nulo** (Granger p=0,67/0,81); (3) **localmente** (AMC,
2-way FE) o robusto é a **co-elevação** fogo↔conversão, enquanto a **liderança t−1 é frágil**
(some sob log1p, inverte sem os anos de seca 1985/2010) — outra **correção pós-robustez** no
espírito da D14. Como contraprova, a conversão em t−2 prevê o fogo *em pasto* (manejo, direção
oposta). Resumo: fogo na **dianteira geográfica, não temporal** — co-evolução sob distúrbio
comum, coerente com #34/#37. Como bônus, o Bloco 6 fecha o micro-mistério 2001–05 do #29: o
pulso de perda de vegetação **não foi de fogo** (fogo plano), e sim demanda/mecanização (a
fatia veg→agric dobra) — o *onset* da soja direta.

### Refinamento — a bimodalidade é regionalmente causada? `bimodalidade_regional.py` (#28C)

O #28 e o #40 deixaram uma pergunta de precisão em aberto, e ela é o tipo de pergunta que a
banca faz. Sabíamos que a idade do pasto na conversão é **bimodal** (#28) e que parecia haver um
**gradiente regional** (Sul jovem, Norte velho; #28/#40 — a metade que a auditoria de julho de
2026 viria a derrubar, enquanto *reforçava* a resposta abaixo). Mas isso permite concluir que a
bimodalidade é *regionalmente causada*? Em outras palavras: ela é uma **composição** entre
regiões internamente unimodais (Sul = só o modo jovem, Norte = só o velho), ou uma
**coexistência** dos dois mecanismos *dentro* de cada região, apenas com peso de mistura
diferente? A distinção decide a redação — afirmar "causada pela região" seria justamente o
salto que a **D14** existe para impedir.

Este pipeline responde com uma decomposição **within/between**, reusando *o mesmo GMM* do #28
(método idêntico ao da manchete) e isolando explicitamente o confundidor **temporal** — afinal
o Ato I converte pasto jovem e o Ato II/III pasto velho, então parte da bimodalidade agregada
é *tempo*, não região. O teste decisivo é a **célula região×ato**: dentro de uma única região
*e* um único ato, ainda há dois modos? São quatro instrumentos: decomposição de variância
(η²); GMM 1c-vs-2c por unidade e por célula; o coeficiente de bimodalidade de Sarle
(corroboração *model-free*); e o η² da pertinência ao modo "velho" (posterior de um GMM global,
rótulos consistentes) — este último isola a parcela between/within da *separação jovem/velho*
em si, não só da variância.

O veredito é **inequívoco e nas duas malhas**. Cada unidade é bimodal *por dentro* — **5/5
mesorregiões** e **9/10 células região×ato** (e, na malha fina, **162/164 AMCs** — com o
censo, todas passam o filtro n≥100 que antes cortava 122), com BC de Sarle acima do limiar
em 5/5 (meso) e 140/164 (AMC). E a geografia explica **muito pouco** da separação
jovem/velho: η²(mesorregião) = **1,3%**, contra **19,6%** do tempo (ato), com **79%** morando
*dentro* das células. A pergunta natural — "e se a mesorregião for grossa demais?" — foi
respondida rodando na malha **AMC** (164 unidades). O recorte fino capta *mais*, mas pouco:
a parcela espacial sobe para **7,5%**, ainda **abaixo do tempo** e com **75%** within. (Sob
o censo, ω² e a permutação **degeneram** — o piso do acaso colapsa, `E[η²|H₀] ≈ (k−1)/(W−1)`,
e `p=0,005` sai para qualquer sinal não-nulo —, de modo que a robustez vem da **estabilidade
censo × amostra**, não da permutação; ver #28C e `metodologia/censo_vs_amostra.md` §7.2.) A leitura corrigida, agora à prova de banca: a bimodalidade
**não é regionalmente causada** — é coexistência dos dois mecanismos em toda parte, e a
geografia **desloca o peso** da mistura ao longo do gradiente Sul→Norte (um pouco mais
nitidamente em alta resolução), **sem criar os modos**. O que mais move o peso é o **tempo** —
o pulso jovem recente do Ato III, coerente com o *onset* da soja direta do #41. Como o #40 e o
#41, é uma **correção pós-robustez** no espírito da D14: a frase certa é "gradiente regional no
*peso* da mistura", nunca "bimodalidade causada pela região".

### A ponta solta do #34 — o Granger reverso inverte a história? `granger_reverso_norte_sul.py` (#42)

A Camada 3 (#34) fechou a narrativa Sul→Norte num nulo causal, mas deixou **uma** pedra no
sapato. Ao testar a precedência temporal, o #34 rodou também o *teste reverso* — e ele deu
significativo: **ΔPasto_Norte → ΔAgric_Sul, Granger p=0,0007**. Lido ao pé da letra, isso seria
uma bomba: significaria que é o **Norte que antecede o Sul**, e a história inteira ("a lavoura
do Sul organiza o avanço ao Norte") estaria de cabeça para baixo. O #34 o descartou com uma
única frase — "N pequeno" — e seguiu em frente. Mas "descartar por N pequeno" é insatisfatório:
um N pequeno *dificulta* achar significância, então um p=0,0007 *apesar* do N pequeno pede
explicação, não um aceno. O #42 é essa explicação. Ele discrimina três hipóteses — **inverte**
(Norte→Sul é real), **comum** (os dois respondem ao boom, e o pasto do Norte só responde um ano
antes — timing, não causa) e **espúrio** (artefato estatístico) — com quatro blocos, e o
veredito é inequívoco: **é espúrio; não inverte nada; ao contrário, reforça o #34.**

A demonstração tem três pregos. **Primeiro, a regressão do #34 era desbalanceada.** Os testes
ADF/KPSS revelam que a série `pasto_Norte` é **I(2)** — ou seja, *nem a sua primeira diferença é
estacionária* (ADF p=0,92). O Granger do #34 rodou sobre primeiras diferenças, o que para uma
série I(2) ainda deixa um regressor **não-estacionário**; cruzá-lo com a `Δagric_Sul` (que é
estacionária, ~I(0)) é a montagem de manual da **regressão espúria**. E como as duas séries têm
*ordens de integração diferentes* (I(0) vs I(2)), elas nem podem ser cointegradas — não existe
relação de longo prazo entre os níveis para o Granger detectar. **Segundo, o método correto
apaga tudo.** O **Toda-Yamamoto** (VAR aumentado, robusto a integração) — o jeito certo de fazer
Granger quando as séries são integradas — zera **as duas direções** (reverso p=0,45, forward
p=0,25). Não há precedência em sentido nenhum; só co-movimento — exatamente o que o #34 já
afirmava. (Note-se a simetria honesta: isso também impede reivindicar uma precedência *Sul→Norte*
— o veredito é "sem líder", não "o Sul lidera".) **Terceiro, e mais limpo: os placebos.** Se a
"precedência reversa" fosse um mecanismo econômico Norte→Sul de verdade, ela não deveria
aparecer onde não há mecanismo. Mas aparece em tudo: o pasto do Norte "Granger-lidera" até o
**pasto do Sul** (mesmo p=0,0007 do achado-manchete!), e o pasto do *Centro* lidera a lavoura do
Sul. Qualquer série de área nortenha suave "prevê" qualquer sulista suave no lag 1 — a assinatura
inconfundível de **co-tendência espúria**, não de um canal direcionado.

Houve uma armadilha no caminho, e vale registrá-la porque ensina. O **Bloco C** controlava o
reverso pelos drivers do drive comum (#37): se o pasto do Norte só "antecede" porque ambos
seguem o câmbio/crédito (hipótese *comum*), controlar esses drivers deveria matar o termo. Mas
ele **persiste** (p=0,0002) — o que, isolado, pareceria *robustez* a favor do Norte→Sul real. A
leitura correta é o oposto: os controles são taxas de crescimento **estacionárias**, e elas não
têm como absorver a **tendência espúria** de uma série I(2); persistir ali é o *esperado* de um
artefato de integração, não prova de causa. Some-se a fragilidade do achado — vive **só no lag
1** (some no lag 2), o *detrend* linear já o derruba ao limite (p=0,050), e ele aparece **só na
área de pasto, não no rebanho** (incoerente como mecanismo econômico) — e o caso está fechado.

O fruto metodológico é a **Decisão D16**: para as séries de área e rebanho das AMC — que são
suaves e fortemente integradas — o Granger ingênuo em primeira diferença **fabrica** precedência
espúria no lag 1. Antes de ler qualquer lead-lag agregado como causal, é preciso exigir o
diagnóstico de integração (ADF/KPSS), o **Toda-Yamamoto** e a **bateria de placebos
direcionais**. É a irmã de séries-temporais da D14 (parcial controlando latitude) e da D15
(alinhamento fogo↔conversão), e funciona como **ressalva retroativa** ao lead-lag agregado do
próprio #34 e do #41 (ambos com Granger de N≈38). No saldo, a narrativa Sul→Norte sai deste
exame **mais forte e mais honesta**: a única ponta que poderia tê-la invertido está agora
caracterizada e descartada em base sólida — co-evolução sob drive comum, **sem precedência
temporal limpa em direção nenhuma**.

---

## Encerramento — a tese que emergiu

Lida como um todo, a sequência de pipelines não é uma coleção de análises avulsas: é uma
**investigação que se autocorrige**. A primeira foto (Fase 0) sugeriu uma história; a fundação
de dados e a cartografia (Fases 1–2) a tornaram mensurável; a consolidação (Fase 3) a tornou
testável; a inferência (Fase 4) separou o sinal robusto (intensificação) das ilusões de marco;
a periodização (Fase 5) deu uma régua honesta e revelou os "dois Goiáses"; e a Fase 6 testou —
e em parte refutou — a hipótese-mãe, reconstruindo-a numa forma mais defensável.

A afirmação central que o conjunto sustenta é esta:

> Goiás passou por uma **reorganização espacial da produção agropecuária** entre 1985 e 2024 —
> intensificação no Sul, fronteira no Norte — coordenada por forças de mercado comuns (câmbio,
> crédito, preço) sobre um **gradiente estrutural de aptidão**, e limitada por um **teto de
> oferta** (Cerrado convertível) que só resta no norte. Esse padrão é empiricamente verificável
> (centro de massa, mecanismo por mesorregião, robustez multi-resolução), e **não** é explicável
> como deslocamento causal direto de uma região sobre a outra (iLUC intra-estadual) — hipótese
> que foi testada e refutada.

Três traços de método merecem registro, porque são o que dá credibilidade à tese:

1. **Os nulos são tratados como resultados.** O #34 (sem deslocamento causal), o #38 (gradiente
   apenas sugestivo), as correções do #40/#41 e o #42 (o contra-resultado que invertia a leitura,
   desmontado como espúrio) não são fracassos escondidos — são a espinha dorsal da honestidade do
   trabalho. A regra D14 nasceu de uma autocorreção; a D16, de levar a sério uma ponta solta em
   vez de varrê-la para baixo do "N pequeno".
2. **As decisões são explícitas e centralizadas.** As vinte decisões (D1–D20) e os atos
   (`config_periodos.py`) garantem que peças escritas em meses diferentes usem a mesma régua —
   e que a régua possa ser defendida, não apenas usada.
3. **Tudo é validado contra verdades independentes.** Os auxiliares de validação
   (`verificar_amc_goias`, `validar_painel_unificado`, `_validar_sicor`, `auditoria_pib`,
   `verificacao_*`) são tão parte do método quanto as análises que validam.

As limitações honestas, que a redação deve carregar: não se afirma que o iLUC *não existe* —
afirma-se que o canal intra-estadual testado não se confirma; o drive comum está *inferido*, não
provado; a desaceleração do Ato III tem só 4–5 anos; e o recorte mesorregional (5 unidades) é
grosso — embora, onde foi possível testar (a bimodalidade da idade do pasto), o #28C tenha
replicado o achado na malha **AMC** (164 unidades; sob o censo ω² e permutação degeneram,
e a robustez vem da estabilidade censo×amostra) e a conclusão tenha sobrevivido; o
mecanismo de transições do #33 segue, esse sim, em resolução
mesorregional. São essas qualificações que transformam um conjunto de gráficos numa tese.

**Extensões (jul/2026): robustez da Camada 1 e três eixos novos.** Fechada a narrativa Sul→Norte
(Fases 0–6), o trabalho a prolongou em duas direções — reforçando a Camada 1 e abrindo eixos por fora.

*Robustez e desagregação da Camada 1.* O **#43** refez o centro de massa **pixel-a-pixel** (direto do
raster, sem malha administrativa) e reencontrou a marcha ao norte a ~1–2 km do centroide-AMC do #32 —
**o MAUP não é problema prático** para a figura-manchete. O **#44** abriu os *lumps* do #32: a soja é o
lump agrícola (não lidera; valida raster×SIDRA, r=0,89) e a "muralha norte" da vegetação é **a floresta**
(campo nativo e savânico recuaram ao norte), com controles limpos (área urbana parada, leite ancorado ao
sul). O **#40B** generaliza a **D14**: calcário e orientação técnica (Censo 6850) descem ao Sul como o
plantio direto, mas somem sob o gradiente 2D — a lição vale para manejo, insumo e instituição.

*Eixo A — a cadeia exportadora (#45).* Ativa as colunas Trase (dormentes desde o #27) e pergunta se a
infra de escoamento *lidera* a fronteira: **não**. E o pipeline virou, ele próprio, um caso de
autocorreção. Na primeira versão (jul/2026) o veredito era "co-move contemporaneamente, sem liderar",
apoiado num achado forte: `β = +0,335` entre volume de soja e área plantada. Ao documentar o #27, a
**premissa sobre a variável** foi medida em vez de herdada — e `trase_soja_volume_t` não era volume
exportado, era **produção** (44,6% dele é esmagamento doméstico; `r = 0,986` com a área plantada). O
"achado" era a Trase batendo consigo mesma. Refeito com o volume **exportado** de fato, o β cai **9×
para +0,037** (r²within 0,268 → 0,025), e um **Bloco C** de robustez (winsor/log1p, espírito do #41)
derruba **os 3** termos defasados significativos — inclusive dois de "LULC lidera" com sinal negativo
que, sem o teste, teriam virado alegação de liderança reversa. O veredito sai **mais forte**: a cadeia
exportadora **não lidera nem co-move materialmente** — o único co-movimento de peso é
`exportação ↔ abate` (β=+0,084), elo mecânico da própria cadeia. Terceiro canal (depois de #34 e
#37/#42) a confirmar "co-evolução sem líder temporal", agora sem o falso positivo.

*Eixo ambiental — conservação e carbono (#46, #47, #48).* O **#46** dá ao #39 a perna que faltava — a
**proteção**: a marcha ao norte se dirige a Cerrado convertível que está **97% desprotegido** (a Proteção
Integral cobre <3% e congelou após 2000), de modo que o teto de oferta do #39 é **físico, não
institucional** (**D17**). O **#47** precifica o **custo de carbono da marcha** por diferença de estoque
(IPCC Tier 1, **D18**): ~**973 Mt CO₂e** comprometidos (faixa dos cenários de densidade: 751–1208), com a **floresta dominando a emissão** apesar de
perder menos área que o savânico, e o centróide da perda marchando +98 km ao norte (amarra com o #39: o Sul
fechou a fronteira). O **#48** **valida** a base de perda de vegetação contra o **PRODES/INPE** — no regime
anual 2013–24 as duas fontes concordam (r=0,91) —, fechando a pendência PRODES da D17 (o refino pixel via GEE
também foi concluído; as Áreas Prioritárias MMA foram dispensadas).

*Eixo C1 — a robustez espacial (#49).* Por fim, o **#49** blinda o painel-manchete (#22) contra a
autocorrelação espacial estrutural que o #24 detectou: num **painel espacial dinâmico** (Elhorst FE
lag/error), os três canais (intensificação, crédito→pasto, substituição local) **sobrevivem** ao termo
espacial — ρ/λ fortes e significativos confirmam o #24, mas os β quase não mudam. É a quarta régua de
robustez, ao lado de tempo (D12), latitude (D14) e integração (D16).

*Extensão socioeconômica — crescimento sem desenvolvimento (#51).* O **#51** reabre o fio que estava
descartado por falta de dado (o IDH-M municipal morre em 2010) e o mede com o **IFDM (FIRJAN) municipal
2013–2023**, que alcança o Ato III. Transforma a assinatura *espacial* do #50 (valor ao sul, área ao
norte) em **medição direta**: a fronteira Norte **quase dobrou a área agrícola** (+93% vs +14% no Sul),
mas o **ganho de desenvolvimento foi idêntico** ao do Sul e o Norte **permanece −0,08 abaixo** — o vão
**não fecha**. O motor da fronteira (expansão de área) é **desacoplado** do desenvolvimento (r≈0), e só o
*valor* agropecuário rende um dividendo modesto (r=0,21). É **descritivo/associativo** (D14) e **invariante
a município↔AMC**. Como a janela 2013–2023 tem os 246 municípios estáveis, a análise é municipal (a
motivação do AMC/D11 não se aplica); a robustez-AMC embutida no pipeline confirma a invariância.

*Extensão de identificação — a aptidão exógena no drive comum (#52).* A metade mais fraca da tese — o
**drive comum** (#37/#38), hoje o *positivo* da perna 3 (ver nota abaixo) — tinha um flanco declarado:
a exposição do #38 era um **proxy de área** mecanicamente complementar (`fronteira ≈ −aptidão`) e
semi-endógeno. O **#52** troca-o por uma **aptidão
edafoclimática física exógena** — a camada nacional da **Embrapa** (`geonode:aptidao_agr_bra`, 1:500k),
puxada por **WFS** e agregada às 166 AMCs pelo overlay do #46. Duas etapas: **52A** valida antes de
testar — a aptidão física **reproduz** o gradiente Sul→Norte (r_lat=−0,44; Sul 4,69 > Centro 4,47 >
Norte 4,17), então a premissa "Sul apto / Norte fronteira" **deixa de ser assumida e vira medida**; a
correlação **moderada** (+0,30) com a exposição do #38 mostra que a aptidão carrega informação própria,
não é clone. **52B** entra a aptidão no teste do #38 e o achado-manchete reaparece **sem a
complementaridade mecânica** (câmbio × aptidão → rebanho, β=−0,033, p=0,026 clusterizado). O ganho é
de **identificação**, não de poder — o teto temporal do #38 (o driver varia só ~40×) segue intacto.
Pendência: refino com o MacroZAEE-GO estadual, **não fetchável** deste ambiente (cert TLS do SIEG).

*Extensão de inferência — o drive comum sob a régua certa (#54).* Restava a pergunta "dá para dar mais
força ao drive comum?". A resposta honesta veio do **#54**, que nomeia o desenho do #38/#52 pelo que ele é
— um **shift-share** (choque nacional do câmbio × fatia local de aptidão) — e roda a **inferência
desenhada para esse caso**. O golpe central é a **permutação do shifter** (embaralhar o câmbio entre
os anos, mantendo a aptidão fixa): ela revela que o erro-padrão **clusterizado** do #38/#52 era
**otimista** para um único choque nacional (resultado de Adão-Kolesár-Morales), e que o p honesto sai
de ~0,03 para **≈0,07 (naive) a 0,13 (rotação circular): não significante a 5%**. O `β` não muda — a
permutação troca o *p*, não o estimador. Em contrapartida, o padrão **passa na especificidade**:
placebos de desfecho nulos (câmbio × aptidão → área urbana / água), **sem antecipação** (um câmbio
futuro não prevê o rebanho de hoje) e **jackknife estável** (nenhuma desvalorização isolada carrega o
resultado). O veredito do drive comum fica então mais preciso: **"corroborante, não estabelecido" — mais
defensável (inferência correta + especificidade demonstrada), menos significante**. Cruzar para
"estabelecido" pediria a **opção A** — um choque que varie no espaço e no tempo (frete, ferrovia,
clima) ou um IV para o câmbio —, que é fio novo, não refinamento. E note o alcance dessa opção: ela
responderia sobre o **mecanismo** (o gradiente medeia choques exógenos?), não sobre o câmbio em si —
a alegação cambial específica é **estruturalmente irrespondível** com dado existente (um choque
nacional anual só tem ~38 realizações, e nenhuma rota de fuga levanta esse teto), e o trabalho **não
fica incompleto** sem essa expansão; o requisito de completude é textual, não empírico (ver a adenda
de 2026-07-19 no [#54](pipelines/54_defensabilidade_perna4.md)).

> **Nota de estrutura (jul/2026).** À luz do #54, o *drive comum* deixou de ser uma perna própria (era
> a "perna 4") e passou a ser o **positivo da Perna 3** — *"reorganização coordenada, não deslocamento
> causal"*. O negativo (não é deslocamento, forte) e o positivo (é coordenação por macro comum,
> corroborante) são as duas metades de uma afirmação só; o teto de oferta, antes perna 5, é agora a
> **Perna 4**. Ver [`indice_logico_pipelines.md`](indice_logico_pipelines.md).

*Extensão de infraestrutura — a capacidade instalada não lidera (#53).* O #45 fechou o Eixo A com a
cadeia exportadora **acompanhando, não liderando** a fronteira, mas deixou uma ressalva honesta: o Trase
mede **fluxo**, não **capacidade instalada** — silos/frigoríficos poderiam estar na dianteira onde o
fluxo não está. O **#53** responde pela metade "silos", reusando integral a máquina do #32: o centroide
da **capacidade estática de armazenagem** (CONAB, `ArmazensCadastrados.txt` — **fetchável** por download
direto, ao contrário do MacroZAEE; 1.135 armazéns, 18,5 Mt) é a camada **mais ao sul de todas** — ~150 km
ao sul do pasto/rebanho, **~83 km ao sul até do crédito** (que o #50 já achara consolidador) e colada ao
núcleo de lavoura do sudoeste (−16 km da agricultura). Como o cadastro traz **coordenadas de ponto**, o
centroide é calculado por ponto e por AMC e os dois **coincidem** (Δ 0,3 km); IC95% por bootstrap de
armazéns. Leitura: *nem a capacidade instalada está na dianteira; ela consolida o núcleo, mais fundo até
que o crédito* — terceiro objeto (após crédito #50 e fluxo #45) a sustentar "co-evolução sem líder"
(Perna 3), agora pela infraestrutura física. É **descritivo/snapshot** (a série histórica da CONAB é por
UF, não municipal) e cobre só **grãos** — a metade "frigoríficos/abate" segue sem dado acessível (SIGSIF
descartado, abate circular no #50).

---

## O epílogo que quase virou prólogo — a mudança de rótulo (#28D, D25/D26)

Este é o último capítulo cronológico do trabalho (21–25 de julho de 2026) e o mais desconfortável
de todos. Ele não acrescenta um achado: ele **audita todos os anteriores** — e derruba alguns.

A porta de entrada foi uma pergunta menor. Na reconstrução do #28 como censo, a idade mediana do
pasto convertido desabava no fim da série (20 anos em 2020 → 4 em 2022), junto com o número de
eventos e com a censura. Quatro hipóteses foram testadas e nenhuma explicava. O
**[#28D](pipelines/28D_deriva_mosaico.md)** foi então contar o destino **completo** das saídas de
pastagem, e encontrou algo que nenhuma delas previa: a conversão **não parou — ela trocou de
nome**. Para cada pixel que sai de pasto para "agricultura" em 2024, **32 saem para "Mosaico de
Usos"**, a classe que o MapBiomas usa quando não consegue separar lavoura de pasto; em 2015 essa
razão era 0,6, e o fluxo `pasto→agricultura` caiu **92%** ao longo da série.

O que torna isso um problema de método, e não um detalhe de dado, é a **âncora independente**: a
SIDRA registra a área de soja de Goiás **crescendo 38%** exatamente nessa janela, e a classe
Mosaico cresce +1,35 Mha — quase o tamanho da soja nova. A medida dizia "a conversão acabou"
enquanto o campo dizia "a conversão acelerou". Daí a **D25**, que é a lição generalizável: *antes
de comparar uma transição LULC entre períodos distantes, verifique que a classe de destino manteve
o mesmo significado* — e o sintoma é fácil de ler ao contrário, porque a transição de interesse
"desaparece" justamente quando o fenômeno de campo acelera.

Duas rodadas de teste tentaram fechar a natureza do sinal. A **borda-móvel** (§9.6) reprocessou
quatro coleções do MapBiomas (6, 8, 9 e 10.1) e **refutou** a explicação mais confortável — não é
instabilidade de fim de série que um reprocessamento conserta: a rampa está ancorada no
**calendário de 2021 em diante**, aparece em toda coleção que alcança 2021, e 97,5% dos pixels
rotulados Mosaico continuam Mosaico quando ganham um ano de futuro. A **coleção de 10 m**
(Sentinel-2, §9.7) removeu outra: um sensor independente e três vezes mais fino **não** resolve o
Mosaico em lavoura — dentro das células-Mosaico só 11,5% da área é lavoura, e o maior naco continua
sendo Mosaico. Restou uma ambiguidade que o trabalho **não** fecha e declara: legenda compartilhada
× integração lavoura-pecuária real.

A resposta operacional é a **D26**, e a sua forma importa: `agricultura ∪ mosaico` **não é uma
correção** — é o **limite superior** de um intervalo cujo limite inferior é `agricultura` sozinha.
Reporta-se o **bracket**, nunca um ponto, e uma conclusão só é robusta se sobrevive nos **dois**
extremos; a melhor evidência dos anos terminais não é o bracket, é a **SIDRA**, que não passa pelo
classificador. A união responde honestamente a uma pergunta *mais grossa* — "quanta terra saiu de
pasto puro para lavoura-ou-uso-misto?" — e o erro a evitar é passar uma pergunta pela outra.

Aplicada a todos os consumidores, essa régua produziu o balanço mais honesto do trabalho:

- **Sobrevive e sai reforçado:** a marcha dos centroides (#32/#44 — expostos, mas robustos, com o
  viés de +10 km medido e triangulado); a fronteira de 2020 da periodização (#29 — a soja da SIDRA
  quebra em 2020 **sozinha**, sem tocar no MapBiomas); a substituição local do #49 (que a mudança
  de rótulo estava **subestimando**); a bimodalidade e a coexistência dos dois mecanismos (#28C —
  5/5 regiões, 10/10 células); e todo o eixo de vegetação nativa (#39, #48 — imunes por construção).
- **Cai:** a tendência temporal de w₁ ("o pasto jovem ganha peso"); o **gradiente latitudinal de
  idade** do pasto, derrubado por três caminhos independentes (#40, #28C e #33); e a queda de
  **−88%** do `pasto→agric` do Sul no Ato III (#33), que sob o bracket **inverte para +51%**.
- **Fica frágil:** o canal de intensificação M1 do #49, cujo bracket cruza zero e cuja âncora SIDRA
  dá sinal oposto — dependência de medida, não só de rótulo.

O último consumidor auditado, o **Intensity Analysis (#31)**, rendeu a lição mais transferível de
toda a varredura, porque expôs um canal que a regra até então não cobria. A regra era: *exposto é
quem tem "agricultura" no **numerador** no fim da série*. Mas o Intensity normaliza tudo por uma
linha-base — a mudança total da matriz —, e essa linha-base **também perde** o fluxo reetiquetado.
No Ato III ela desaba pela metade, de modo que **toda razão "observado sobre esperado" daquele ato
estava inflada cerca de três vezes, inclusive as de transições cujo numerador é impecável**. Foi
assim que caiu a frase "o Ato III se distingue pela regeneração": em valor absoluto a regeneração é
mesmo a maior da série, mas por margem modesta — o que a fazia parecer excepcional era o
denominador ter encolhido. A moral generaliza para além do Mosaico: **antes de declarar uma métrica
imune, olhe as duas pontas da razão**. Um viés no denominador contamina indicadores que, olhados
pelo numerador, pareciam a salvo.

*(No caminho apareceu também um defeito que nada tem a ver com rótulo: as intensidades do #31 eram
divididas duas vezes pela duração do período, o que as tornava incomparáveis entre atos de 15, 18 e
4 anos. Corrigido. Ele empurrava na direção oposta à do rótulo — escondia parte da queda —, e é um
lembrete de que auditar por um motivo costuma revelar outro.)*

Houve ainda uma consequência de nomenclatura, e ela foi executada em 25/jul/2026: o Ato III
chamava-se **"Conversão seletiva"**, um rótulo **factualmente invertido** pela auditoria — ele
nomeava uma desaceleração que não existiu. Passou a ser **"Conversão acelerada (mascarada)"**.
A fronteira de 2020 sempre foi real; o nome é que não era. O parêntese é parte do nome de
propósito: o traço que define o período é que a medida crua diz o oposto do que ocorreu.

O epílogo deixa uma moral que vale para além deste caso, e é a razão de ele estar na narrativa e
não só numa nota de rodapé: **o método estava correto, e a série é que se moveu debaixo dele.** É
a mesma família da D16 (Granger espúrio por integração) e da D23 (ΔBIC sob censo) — três casos de
uma técnica impecável rodando sobre uma definição que mudou. Nenhuma sofisticação estatística a
jusante conserta isso; só olhar o dado de frente conserta.

Detalhe completo em [`metodologia/tratamento_deriva_mosaico.md`](metodologia/tratamento_deriva_mosaico.md)
(protocolo por tipo de análise e a tabela de veredito por pipeline).

---

## Apêndice A — Índice de todos os scripts (trabalho principal)

Mapeamento completo de cada script não-MG à sua fase e função. (Os scripts `*_mg.py` e a pasta
`paralelo/` pertencem aos trabalhos paralelos — ver Apêndice B.)

| Script | # | Fase | Função |
|---|---|---|---|
| `grafico_pastagem_pib_goias.py` | 1 | 0 | Pastagem × PIB estadual; deflação; primeira tubulação |
| `analise_expandida_goias.py` | 2 | 0 | Painel estadual (cobertura, rebanho, lotação, PIB agro) |
| `_verificar_dados.py` | — | 0 | Sanity check das séries estaduais |
| `coleta_sidra.py` | 3/7/15 | 1 | Coletor unificado SIDRA/IBGE (+ `--censo-agro`, `--so 839`) |
| `pipeline_municipal.py` | 4 | 1 | MapBiomas Col. 10.1 municipal (wide→longo, +cd_mun) |
| `coleta_sicor.py` | 6 | 1 | Crédito rural SICOR/BACEN |
| `_validar_sicor.py` | — | 1 | Validação do coletor SICOR |
| `coleta_idhm.py` | 13 | 1 | IDH-M via IPEA Data (1991/2000/2010) |
| `fogo_mapbiomas.py` | 14 | 1 | Área queimada × LULC via GEE (coleta) |
| `explorar_asset_fogo.py` | — | 1 | Sondagem dos assets de fogo (pré-#14) |
| `analise_fogo.py` | 14 | 1 | Fogo: análise descritiva e cruzamentos |
| `analise_safrinha.py` | 15 | 1 | Milho 1ª/2ª safra (intensificação) |
| `coleta_trase.py` | 27 | 1 | Cadeia produtiva Trase (soja/boi); separa export × esmagamento doméstico |
| `coleta_pib_uf_ipea.py` | — | 1 | PIB/VAB agro UF nativo IPEA (insumo do #21) |
| `estimativa_abate_municipal.py` | — | 1 | Abate municipal estimado (rateio pelo rebanho) |
| `analise_pastagem_soja.py` | 5 | 2 | Transição pasto↔soja (proxy de estoque) |
| `analise_credito_uso_terra.py` | 8 | 2 | Crédito × uso da terra |
| `auditoria_pib.py` | — | 2 | Auditoria da discrepância de PIB (#8 vs #16) |
| `gerar_mapas_lulc_40anos.py` | 9 | 2 | 40 mapas coropléticos municipais |
| `_cartografia.py` | — | 2 | Helpers cartográficos (rosa-dos-ventos, escala) |
| `gerar_mapas_lulc_gee_40anos.py` | 10 | 2 | 40 mapas raster GEE 30 m |
| `_preview_mapa_2024.py` | — | 2 | Variantes do mapa de 2024 para escolha |
| `gerar_gif_lulc.py` | 11 | 2 | GIF animado 40 anos |
| `gerar_mapas_lulc_gee_rio_verde.py` | — | 2 | Estudo de caso Rio Verde (raster) |
| `gerar_gif_lulc_rio_verde.py` | — | 2 | Estudo de caso Rio Verde (GIF) |
| `transicoes_mapbiomas.py` | 12 | 2 | Matrizes de transição pixel-a-pixel via GEE (6 grupos; **superado pelo #12B**) |
| `transicoes_cubo.py` | 12B | 6 | A matriz primária recontada no cubo censitário, com o Mosaico como 7º grupo |
| `validar_transicoes_cubo.py` | 12B | 6 | Separa Δ_medida (instrumento) de Δ_mosaico (o conserto) em 3 blocos |
| `explorar_asset_transicao.py` | — | 2 | Sondagem do asset de transição (pré-#12) |
| `visualizar_transicoes.py` | — | 2 | Heatmaps/Sankey/coropléticos das transições |
| `agregar_conversoes.py` | 19 | 2 | Conversões brutas ano-a-ano (UF + municipal) |
| `construir_painel_unificado.py` | 16 | 3 | Painel wide `cd_mun × ano` |
| `validar_painel_unificado.py` | — | 3 | Validação em 4 camadas do painel |
| `mapeamento_mesorregioes.py` | 18 | 3 | cd_mun → mesorregião IBGE 2017 (D6) |
| `calcular_taxas_lulc.py` | 17 | 3 | Taxas LULC (delta, slope, SE HAC, aceleração) |
| `figuras_taxas.py` | 20 | 3 | Figuras de taxas |
| `construir_amc_goias.py` | 25 | 3 | Áreas Mínimas Comparáveis (D11) |
| `verificar_amc_goias.py` | — | 3 | Verificação independente do AMC |
| `correlacoes_uf.py` | 21 | 4 | Correlações UF Δ-vs-Δ (HAC) |
| `correlacoes_painel.py` | 22 | 4 | Painel municipal 2-way FE (D8) |
| `piecewise_did.py` | 23 | 4 | DiD GO vs MT/TO + event-study + placebo (D9) |
| `analise_espacial.py` | 24 | 4 | Moran's I, LISA, regressão espacial |
| `deteccao_quebras.py` | 26 | 4 | Quebras estruturais data-driven (sup-F) |
| `coleta_idade_pastagem.py` | 28 | 5 | Idade do pasto na conversão (amostragem GEE, D10) |
| `analise_reserva_terra.py` | 28 | 5 | Idade do pasto: análise (bimodalidade) |
| `periodizacao_multivariada.py` | 29a | 5 | sup-F multivariado |
| `periodizacao_stars.py` | 29b | 5 | Rodionov STARS |
| `periodizacao_transicoes.py` | 29c | 5 | KL/autovalores das matrizes de transição |
| `verificacao_periodizacao.py` | 30 | 5 | Sanidade da periodização (FPR, sensibilidade) |
| `intensity_analysis.py` | 31 | 5 | Intensity Analysis (Aldwaik & Pontius 2012) |
| `verificacao_intensity.py` | 31 | 5 | Sanidade do Intensity (poder, bootstrap) |
| `config_periodos.py` | — | 5 | Fonte única de ATOS e MARCOS (A/B/C) |
| `centro_massa.py` | 32 | 6 | Centro de massa migratório (Camada 1) |
| `transicoes_regionais.py` | 33 | 6 | Mecanismo por mesorregião × ato (Camada 2) |
| `analise_transicoes.py` | — | 6 | Maquinaria de transições por ato (base do #33) |
| `deslocamento_espacial.py` | 34 | 6 | Lead-lag + spillover (Camada 3, teste formal) |
| `robustez_janelas.py` | 35 | 6 | Robustez de fronteira (#32/#33) |
| `robustez_janela_slope.py` | 36 | 6 | Robustez de resolução do slope (#17) |
| `coleta_drivers_macro.py` | 37A | 6 | Drivers macro exógenos (preço, câmbio, crédito) |
| `drive_comum.py` | 37B | 6 | Drive comum na série UF (lead-lag, exogeneidade) |
| `drive_comum_amc.py` | 38 | 6 | Drive comum no painel AMC (driver × exposição) |
| `fronteira_fechando.py` | 39 | 6 | Oferta de Cerrado convertível (D13) |
| `duas_logicas_pastagem.py` | 40 | 6 | Geografia das duas lógicas do pasto (D14) |
| `duas_logicas_calcario_orientacao.py` | 40B | 6 | Calcário + orientação técnica (Censo 6850) no arcabouço das duas lógicas — generaliza a D14 |
| `fogo_lidera_fronteira.py` | 41 | 6 | Fogo como vanguarda da fronteira (D15) |
| `bimodalidade_regional.py` | 28C | 6 | Bimodalidade é regional? Decomposição within/between (meso+AMC, D14) |
| `granger_reverso_norte_sul.py` | 42 | 6 | O Granger reverso do #34 inverte a leitura? Estacionariedade + Toda-Yamamoto + placebos (D16) |
| `centro_massa_pixel.py` | 43 | 6 | O centroide-AMC do #32 é artefato de malha (MAUP)? Centro de massa pixel-a-pixel |
| `centro_massa_desagregado.py` | 44 | 6 | Abre os *lumps* do #32 (soja; veg. em 3 formações) + controles (leite, área urbana) |
| `analise_trase_lulc.py` | 45 | 6 | Cadeia exportadora (Trase) segue ou lidera a expansão LULC? Cross-lagged em painel (D16) + robustez das defasagens |
| `fronteira_protecao.py` | 46 | 6 | A fronteira marcha para terra protegida ou desprotegida? Overlay UC×AMC sobre o #39 (D17) |
| `refino_protecao_pixel.py` | 46 | 6 | Refino pixel do #46 via GEE (convertível 2024 × Proteção Integral no raster) |
| `custo_carbono_marcha.py` | 47 | 6 | Custo de carbono da marcha (diferença de estoque IPCC Tier 1 × densidades por formação, D18) |
| `validacao_prodes_mapbiomas.py` | 48 | 6 | Validação cruzada PRODES (INPE) × MapBiomas (fecha a pendência PRODES da D17) |
| `painel_espacial_dinamico.py` | 49 | 6 | Painel espacial dinâmico (Elhorst FE lag/error): os canais do #22 sobrevivem ao espaço? |
| `centro_massa_economico.py` | 50 | 6 | Centro de massa de crédito/valor (extensão do #32): crédito ~75 km ao sul da fronteira; valor ancorado; abate descartado |
| `coleta_firjan_ifdm.py` + `crescimento_sem_desenvolvimento.py` | 51 | 6 | Crescimento × desenvolvimento (IFDM 2013–2023): Norte quase dobra a área mas ganha IFDM igual e fica −0,08 abaixo; expansão de área desacoplada do desenvolvimento; invariante município↔AMC |
| `aptidao_edafo_exposicao.py` + `aptidao_edafo_drive38.py` | 52 | 6 | Aptidão edafoclimática exógena (Embrapa 1:500k, WFS) como exposição no #38: a aptidão física reproduz o gradiente Sul→Norte (52A) e o achado do rebanho reaparece sem a complementaridade mecânica (52B); fortalece a identificação do drive comum (positivo da perna 3), não o poder |
| `centro_massa_capacidade.py` | 53 | 6 | Centro de massa da capacidade instalada de armazenagem (CONAB): a capacidade é a camada mais ao sul de todas (~150 km ao sul do pasto, ~83 km ao sul até do crédito) → fecha a metade "silos" da ressalva do #45; ponto+AMC coincidem, IC por bootstrap de armazéns |
| `defensabilidade_perna4.py` | 54 | 6 | Endurecimento shift-share do drive comum (opção B): permutação do shifter (câmbio) mostra que o p clusterizado do #38/#52 era otimista — sai de ~0,03 para ≈0,07–0,13 (não significante a 5%); placebos/lead/jackknife seguram a especificidade. "Corroborante, não estabelecido"; funde o drive comum ao positivo da perna 3 |
| `deriva_mosaico_fim_serie.py` | 28D | 6 | **A mudança de rótulo** (D25): conta o destino completo das saídas de pastagem e acha a conversão migrando de "agricultura" para "Mosaico de Usos" (razão 0,6→32,5) enquanto a SIDRA dá soja +38% |
| `processa_cubo_idade_destinos.py` | 28D | 6 | Reprocessa o cubo do #28 capturando os **dois** destinos (agric e Mosaico) com idade — habilita todos os brackets-por-evento |
| `borda_movel_gee.py` + `borda_movel_colecao9.py` + `razao_destino_ano.py` + `fig_borda_movel.py` | 28D §9.6 | 6 | Borda-móvel em 4 coleções (6/8/9/10.1): **refuta** o artefato de fim de série — a rampa é ancorada no calendário 2021+, e 97,5% dos pixels Mosaico não "curam" com um ano a mais de futuro |
| `mosaico_10m_sentinel.py` | 28D §9.7 | 6 | A coleção 10 m (Sentinel-2) olha dentro da célula-Mosaico: só 11,5% é lavoura → **remove** a hipótese "hedge de resolução sobre soja recuperável"; não separa legenda × ILP real |
| `centro_massa_deriva_check.py` | 28D/32 | 6 | Quantifica o viés no centroide (+10 km, triangulado por mosaico e por SIDRA) e mostra que a mudança de rótulo **não é espacialmente uniforme** (aterrissa na fronteira norte) |
| `periodizacao_robustez_deriva.py` | 28D/29 | 6 | A fronteira de 2020 é real: sob a régua corrigida o sup-F **fortalece** (21,5→34,1) e a soja SIDRA quebra em 2020 sozinha |
| `painel_espacial_dinamico_deriva.py` | 28D/49 | 6 | Bracket inferencial: M3 (substituição) robusto — a mudança de rótulo o **subestimava**; M1 (intensificação) frágil — o bracket cruza zero |
| `duas_logicas_deriva_check.py` + `duas_logicas_bracket_evento.py` | 28D/40 | 6 | Bracket-por-evento: o gradiente índice-jovem × latitude **some** sob `pasto→(agric∪mosaico)` |
| `bimodalidade_regional_uniao.py` | 28D/28C | 6 | Re-checagem do #28C sob a união: bimodalidade/coexistência **robustas**, gradiente de idade **artefato** |
| `transicoes_regionais_bracket.py` | 28D/33 | 6 | Fecha a auditoria: a queda de −88% do `pasto→agric` do Sul no Ato III **inverte para +51%** sob o bracket (SIDRA +244%), e a tabela de idade do Ato III inverte a ordenação; o `veg→pasto` e o balanço do Ato II são imunes |

## Apêndice B — Nota sobre os trabalhos paralelos (fora deste documento)

Este documento cobre apenas o **trabalho principal** (Goiás). O repositório também abriga
trabalhos paralelos que foram **deliberadamente excluídos** desta narrativa: o site de rebanho
bovino BR/MG e Montes Claros, a visualização de Minas Gerais, a experiência da viagem de campo,
e o pipeline de dados de MG (os nove scripts `scripts/*_mg.py` e `config_mg.py`, que ficam em
`scripts/` por acoplamento técnico mas são paralelos — o sufixo `_mg` os distingue). Esses itens
têm sua própria lógica e não pertencem ao fio condutor descrito acima.
