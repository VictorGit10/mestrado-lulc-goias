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
| 6 | A marcha ao norte (Sul→Norte) | "A fronteira se desloca? Como? Por quê?" | #32–#41, #28C, #42 |

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
- **As decisões (D1–D16).** Ao longo do texto aparecem referências a decisões metodológicas
  numeradas. Resumidas:

  | # | Decisão | Onde |
  |---|---|---|
  | D1 | 6 classes unificadas, Mosaico excluído | #10, #12, #17 |
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
  | D14 | Em cross-section estadual, reportar a **parcial controlando latitude** antes de atribuir efeito próprio | #40, #28C |
  | D15 | Alinhamento `fogo(t) ↔ conv(origem=t)` como contemporâneo | #41 |
  | D16 | Lead-lag de séries AMC integradas exige Toda-Yamamoto + placebos (Granger ingênuo fabrica precedência espúria) | #42 |
  | D17 | "Proteção" = malha vetorial de UCs (Proteção Integral × Uso Sustentável), proxy-teto no espírito da D13; refino pixel e PRODES/MMA pendentes | #46 |

- **Os atos (a régua narrativa).** A periodização data-driven (Fase 5) cristalizou três
  **atos** em `config_periodos.py`: **I — Pastagem como herança (1985–2000)**, **II — Expansão
  e intensificação (2001–2019)**, **III — Conversão seletiva (2020–2024)**. Os **marcos**
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

**`coleta_trase.py` (#27)** integra os dados de cadeia produtiva exportadora da Trase.earth
(soja 2004–2022, boi 2011–2023) agregados por município-ano, mapeando os nomes Trase
(caixa-alta, sem acento) para `cd_mun`. A docstring é honesta sobre o limite: a Trase rastreia
**só o fluxo exportador**, então é proxy de exposição à cadeia agroindustrial, não de
capacidade total de abate/esmagamento.

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
9.840 linhas × ~200 colunas) todas as fontes prontas: LULC, pecuária, lavouras, PIB,
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
p<0,001). Os resíduos deste painel não são jogados fora — viram insumo do #24.

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
**`coleta_idade_pastagem.py` (#28A)** amostra ~78.000 pixels que sofreram a transição
pasto→agricultura e, para cada um, calcula **há quantos anos aquela pastagem existia no momento
da conversão** — com a idade computada **localmente em Python** a partir das 40 bandas anuais
(Decisão D10, que evita estourar o limite do GEE encadeando 35+ operações). A hipótese é a
"pastagem como reserva de terra": uma pastagem jovem convertida sugere mecanismo *premeditado*
(plantar pasto já pensando em virar lavoura); uma pastagem velha sugere mecanismo
*oportunístico*. **`analise_reserva_terra.py` (#28B)** descreve a distribuição e encontra o
achado-chave: no período recente a idade é **bimodal** — picos em ~5 anos e ~22/35 anos — a
assinatura empírica direta da *coexistência* dos dois mecanismos. E um gradiente regional já
aparece: o Sul converte pasto jovem (mediana ~9 anos), o Norte/Noroeste converte pasto antigo
(~20 anos). (*Quanto* desse gradiente é causa regional vs mera composição só seria medido
depois, no #28C — Fase 6: a resposta é que a geografia modula o peso, não causa a bimodalidade.)

**O que essa fase deixou pronto.** Uma régua temporal honesta (os atos), uma régua de marcos
com graus de evidência, e uma pista forte de que existem **dois Goiáses** — um Sul que
intensifica sobre pasto jovem e um Norte que abre fronteira sobre pasto/vegetação antiga. Essa
pista, somada ao gradiente regional, é o que disparou a investigação que organizaria tudo.

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
líquido (−0,57 Mha) e ganha agricultura, enquanto Norte/Noroeste ganham pasto. No Ato III o
`pasto→agric` do Sul **despenca −88%** (e a agricultura desacelera, fechando com o #32),
enquanto o `veg→pasto` do Norte persiste. A idade do pasto (#28) costura tudo: Sul 9 anos
(reserva jovem) → Norte 20 anos (fronteira).

### Camada 3 — É deslocamento causal? `deslocamento_espacial.py` (#34)

O teste formal — e o resultado mais importante da fase. Em **tempo contínuo** (sem binar por
ato, para evitar circularidade com o #29), faz duas perguntas: **(A) temporal** — a expansão da
agricultura no Sul *antecede* o avanço de pasto/rebanho no Norte? (lead-lag por CCF + Granger,
com teste reverso); **(B) espacial** — a agricultura dos *vizinhos ao sul* prevê o crescimento
de pasto local? (SLX em painel 2-way FE com peso direcional; placebo = vizinhos ao norte). O
veredito é de **não-confirmação**: (1) **sem precedência temporal** (Granger ΔAgric_Sul →
ΔPasto_Norte p=0,97); (2) **sem spillover direcional** (θ=−0,16, *oposto* do previsto — vizinhos
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
hipótese **câmbio × fronteira → rebanho** confirma a direção (p=0,031), mas a grade completa
(com lag 2) não devolve nenhum sobrevivente do FDR. O gradiente câmbio × aptidão na pecuária de
fronteira é, portanto, **indício sugestivo, não achado estabelecido** — a Camada 5 avança, não
fecha.

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
tipologia de "carreira da terra". O **achado robusto** é a **geografia das duas lógicas** — a
Rotação (pasto jovem) domina o Sul/Centro, o Oportunístico (pasto antigo) domina o Norte: as
duas lógicas são as **duas faces do gradiente de aptidão Sul→Norte** (índice jovem × latitude
r=−0,49). Mas este pipeline é também um caso-modelo de **autocorreção**: a primeira leitura
anunciou que "a lógica é estrutural (plantio direto), não de fluxo", e a *verificação no mesmo
dia derrubou o overclaim*. Controlando latitude (correlação parcial), o cruzamento no-till ×
idade colapsa (r −0,37 → −0,22); controlando o gradiente 2D (lat+lon), nada sobrevive. A
contribuição sólida é a *geografia da bimodalidade*, não um driver estrutural — o plantio
direto **co-localiza** com a lógica jovem, não a causa. Daí a **Decisão D14**: em cross-section
estadual, sempre reportar a parcial controlando latitude antes de atribuir efeito próprio.

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
banca faz. Sabemos que a idade do pasto na conversão é **bimodal** (#28) e que há um
**gradiente regional** (Sul jovem, Norte velho; #28/#40). Mas isso permite concluir que a
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
mesorregiões** e **10/10 células região×ato** (e, na malha fina, **34/36 AMCs** com n≥100),
com BC de Sarle sempre acima do limiar. E a geografia explica **muito pouco** da separação
jovem/velho: η²(mesorregião) = **2,5%**, contra **20%** do tempo (ato), com **77%** morando
*dentro* das células. A pergunta natural — "e se a mesorregião for grossa demais?" — foi
respondida rodando na malha **AMC** (158 unidades), com duas blindagens contra a inflação
mecânica do η² por excesso de grupos: o **ω²** (effect-size corrigido) e uma **linha-base de
permutação**. O recorte fino capta *mais*, mas pouco: a parcela espacial sobe para **7,3%**
(líquido de acaso; a permutação confirma que é real — acaso só 1,4%, p=0,005), ainda **abaixo
do tempo** e com **73%** within. A leitura corrigida, agora à prova de banca: a bimodalidade
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
2. **As decisões são explícitas e centralizadas.** As dezesseis decisões (D1–D16) e os atos
   (`config_periodos.py`) garantem que peças escritas em meses diferentes usem a mesma régua —
   e que a régua possa ser defendida, não apenas usada.
3. **Tudo é validado contra verdades independentes.** Os auxiliares de validação
   (`verificar_amc_goias`, `validar_painel_unificado`, `_validar_sicor`, `auditoria_pib`,
   `verificacao_*`) são tão parte do método quanto as análises que validam.

As limitações honestas, que a redação deve carregar: não se afirma que o iLUC *não existe* —
afirma-se que o canal intra-estadual testado não se confirma; o drive comum está *inferido*, não
provado; a desaceleração do Ato III tem só 4–5 anos; e o recorte mesorregional (5 unidades) é
grosso — embora, onde foi possível testar (a bimodalidade da idade do pasto), o #28C tenha
replicado o achado na malha **AMC** (158 unidades, com ω² e permutação contra inflação) e a
conclusão tenha sobrevivido; o mecanismo de transições do #33 segue, esse sim, em resolução
mesorregional. São essas qualificações que transformam um conjunto de gráficos numa tese.

**Duas extensões pós-fechamento (jul/2026).** Fechada a narrativa Sul→Norte, dois pipelines a
prolongam por fora. O **#45** ativa o **Eixo A** — as colunas Trase (cadeia exportadora) que
dormiam no painel desde o #27 — e pergunta se a infraestrutura de escoamento *lidera* a fronteira:
a resposta é **não** — ela **co-move contemporaneamente** com a produção (4/8 pares no painel FE),
sem precedência defasada robusta, um terceiro canal (depois de #34 e #37/#42) a confirmar
"co-evolução sem líder temporal". O **#46** dá ao #39 a perna que faltava — a **proteção**: a
marcha ao norte se dirige a Cerrado convertível que está **97% desprotegido** (a Proteção Integral
cobre <3% em qualquer região e congelou após 2000), de modo que o teto de oferta do #39 é
**físico, não institucional**. Este último abre, pela primeira vez, o **eixo ambiental** da
dissertação — a conservação e, adiante, o custo de carbono/biodiversidade da reorganização.

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
| `coleta_trase.py` | 27 | 1 | Cadeia exportadora Trase (soja/boi) |
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
| `transicoes_mapbiomas.py` | 12 | 2 | Matrizes de transição pixel-a-pixel via GEE |
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
| `fogo_lidera_fronteira.py` | 41 | 6 | Fogo como vanguarda da fronteira (D15) |
| `bimodalidade_regional.py` | 28C | 6 | Bimodalidade é regional? Decomposição within/between (meso+AMC, D14) |
| `granger_reverso_norte_sul.py` | 42 | 6 | O Granger reverso do #34 inverte a leitura? Estacionariedade + Toda-Yamamoto + placebos (D16) |
| `centro_massa_pixel.py` | 43 | 6 | O centroide-AMC do #32 é artefato de malha (MAUP)? Centro de massa pixel-a-pixel |
| `centro_massa_desagregado.py` | 44 | 6 | Abre os *lumps* do #32 (soja; veg. em 3 formações) + controles (leite, área urbana) |
| `analise_trase_lulc.py` | 45 | 6 | Infra exportadora (Trase) segue ou lidera a expansão LULC? Cross-lagged em painel (D16) |
| `fronteira_protecao.py` | 46 | 6 | A fronteira marcha para terra protegida ou desprotegida? Overlay UC×AMC sobre o #39 (D17) |

## Apêndice B — Nota sobre os trabalhos paralelos (fora deste documento)

Este documento cobre apenas o **trabalho principal** (Goiás). O repositório também abriga
trabalhos paralelos que foram **deliberadamente excluídos** desta narrativa: o site de rebanho
bovino BR/MG e Montes Claros, a visualização de Minas Gerais, a experiência da viagem de campo,
e o pipeline de dados de MG (os nove scripts `scripts/*_mg.py` e `config_mg.py`, que ficam em
`scripts/` por acoplamento técnico mas são paralelos — o sufixo `_mg` os distingue). Esses itens
têm sua própria lógica e não pertencem ao fio condutor descrito acima.
