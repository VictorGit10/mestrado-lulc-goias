# Pipeline #28C — A bimodalidade é regionalmente causada? (decomposição within/between)

**Script**: `scripts/bimodalidade_regional.py`
**Status**: ✅ Concluído (2026-06-08) · ♻️ **re-rodado sobre o censo em 2026-07-21**
**Outputs**: 4 CSVs (`idade_bimodalidade_por_grupo.csv`, `idade_bimodalidade_decomposicao.csv` + variantes `_amc`) + 2 PNGs em `outputs/idade_pastagem/` (`bimodalidade_unidade_ato.png`, `bimodalidade_unidade_ato_amc.png`).
**Depende de**: #28 censo (`pastagem_idade_censo.parquet`) e **reusa o GMM ponderado do #28** (`analise_reserva_terra.ajustar_gmm_unidim`); #25 (`amc_crosswalk_goias.csv`) na malha AMC.

> **Nota de revisão (21/jul/2026).** Quando o #28 virou censo, `carregar()` passou a
> devolver uma **tabela de contingência** (1 linha = 1 célula + coluna `peso`) e a
> defaultar para o censo. Este script não era peso-aware: passou a ler 396.787 células
> como se fossem 396.787 pixels de peso igual. O efeito não era cosmético — **o gradiente
> Sul→Norte desaparecia** (medianas 10·10·11·12·12 sem peso contra 9·9·10·16·16 com peso).
> Todas as estatísticas do módulo (η², ω², BC de Sarle, permutação, GMM, medianas, filtros
> de n) foram reescritas com peso e verificadas por contrato D24
> (`python scripts/bimodalidade_regional.py --testar`). **Os números abaixo são os do censo
> ponderado**; os anteriores, de jun/2026, vinham da amostra com os bugs do envelope e da
> classe 21. Ver `Textos/metodologia/censo_vs_amostra.md`.

## Pergunta de pesquisa

O #28 mostrou que a idade da pastagem na conversão é **bimodal** (picos em ~4 e ~23 anos)
e o #28/#40 mostraram um **gradiente regional** (Sul converte pasto jovem, Norte pasto
antigo). Daí a pergunta de precisão que faltava fechar:

> A bimodalidade é **regionalmente causada**? Ou seja, ela é uma **composição** entre
> regiões internamente unimodais (Sul = só jovem, Norte = só velho), ou uma
> **coexistência** dos dois mecanismos **dentro de cada região**, apenas com peso de
> mistura diferente?

A distinção é decisiva para a redação (ecoa **D14**): "regionalmente causada" exigiria que
cada região fosse internamente unimodal e que a bimodalidade do agregado viesse *só* da
mistura de regiões. Se cada região é, ela mesma, bimodal, então a geografia **modula o
peso** — não **cria** os modos.

**Confundidor explícito: o tempo.** O Ato I converte pasto jovem (mediana 6a) e o Ato II/III
convertem pasto velho (~19a). Logo, parte da "bimodalidade" agregada é **temporal**, não
regional. Por isso a **célula região×ato** é o teste decisivo: dentro de uma única região
*e* um único ato, ainda há dois modos?

## Método

Reusa o `ajustar_gmm_unidim` do #28 (GMM 1c vs 2c, AIC/BIC) — método idêntico ao da manchete
do #28 — e adiciona quatro instrumentos:

- **Decomposição de variância (η²)** da idade não-censurada por **espaço**, **ato** e
  **espaço×ato** — quanto cada eixo "explica" da variância.
- **GMM 1c vs 2c por unidade espacial e por célula espaço×ato** (Ato II e III): cada unidade,
  isoladamente, continua bimodal? Critério de bimodalidade (todos precisam valer): ΔBIC =
  bic₁c − bic₂c > 10, separação entre modos > 5 anos, peso do componente menor > 0,15.
- **Coeficiente de bimodalidade de Sarle (BC)** — corroboração **model-free** do GMM
  (BC > 5/9 ≈ 0,555 sugere bimodalidade).
- **η² da pertinência ao modo "velho"** (responsabilidade posterior de **um GMM global**,
  rótulos consistentes para evitar label-switching) por espaço/ato/célula → isola a parcela
  **between** vs **within** da *separação jovem/velho* especificamente (não só da variância).

### Duas blindagens contra a inflação de nº de grupos (essenciais para a malha AMC)

η² **infla mecanicamente** com mais grupos (166 AMCs "explicam" mais variância que 5
mesorregiões só por terem mais graus de liberdade, mesmo no acaso). Para comparar as malhas
de forma honesta:

- **ω² (omega-quadrado)** — effect-size de variância explicada **corrigido para k grupos**
  (pode ficar negativo se o agrupamento não explica nada além do acaso).
- **Linha-base de permutação** (B=200): sob H₀ (rótulo espacial ⊥ idade), qual η² sai por
  acaso com aquele número/tamanho de grupos? O sinal real é `η²_obs − η²_acaso`.

> **Duas ressalvas que o censo criou nessas blindagens** (D23) — ambas apontam para o mesmo
> lugar: elas eram correções de amostra pequena e perderam a função.
>
> - **ω² ≈ η² até a 3ª casa.** O termo corretivo é (k−1)·MS_within, e MS_within não encolhe
>   com W enquanto SS_entre cresce com W. Com W = 16 milhões e k ≤ 164, a correção some.
>   Isso não significa que o agrupamento explica mais; significa que a coluna ω² parou de
>   informar. A comparação meso×AMC honesta passa a ser pelo **tamanho** do η².
> - **O piso do acaso colapsou.** E[η²|H₀] ≈ (k−1)/(W−1) = 2,5·10⁻⁷ (meso) e 1,0·10⁻⁵ (AMC).
>   Logo "líquido de acaso" ≡ "observado" e p_perm = 0,005 (o mínimo com B=200) para
>   qualquer sinal não-nulo. **Não citar esse p-valor como força de evidência.**
>
> A permutação foi reimplementada no nível do **evento** (sorteio hipergeométrico
> multivariado com tamanhos de grupo fixos), não da linha: sob o censo, embaralhar linhas
> seria permutar *blocos* de pixels e testaria uma hipótese nula mais frouxa. O teste de
> contrato confere que o piso empírico bate com o analítico.

Rodado em **duas malhas**: mesorregião (`--malha meso`, 5 unidades, D6) e AMC
(`--malha amc`, 164 com conversão, via crosswalk do #25). **16.004.530** eventos
não-censurados em 396.787 células (censo de 21/jul/2026; antes eram 11.035 pixels
amostrados, valor que também estava inflado pelo bug da classe 21 — ver
`28_idade_pastagem.md`).

## Achados

### 1. Cada unidade espacial é bimodal POR DENTRO

Não há nenhuma região/AMC unimodal que a mistura "junte":

| Malha | Unidades internamente bimodais (n≥100) | Células espaço×ato bimodais | BC de Sarle > 0,555 |
|---|---|---|---|
| **Mesorregião (5)** | **5/5** | **9/10** | 5/5 (0,57–0,64) |
| **AMC (164)** | **162/164** | 287/323 | 140/164 (0,41–0,88) |

As 5 mesorregiões têm ΔBIC de 351 mil a 3,3 milhões — números que, sob censo, medem
**n e não evidência** (D23); o que importa é que os dois modos (~4a e ~15–20a) aparecem em
todos os painéis, e que as medianas ordenam o gradiente Sul→Norte: **Sul 9 · Centro 9 ·
Leste 10 · Noroeste 16 · Norte 16**.

As **3 exceções** (2 AMCs + 1 célula meso×ato) falham todas pelo **mesmo critério e do mesmo
lado**: peso do componente jovem abaixo de 0,15 — AMC 16065 (w₁=0,121, mediana 17a),
AMC 16192 (w₁=0,109, mediana 22a) e Noroeste × Ato II (w₁=0,121, mediana 19a). São as
**pontas velhas do gradiente**, exatamente o que "gradiente contínuo no peso" prevê. Nenhuma
falha por ausência de dois modos.

### 2. A geografia explica MUITO POUCO da separação jovem/velho

Decomposição da pertinência ao modo "velho":

| Eixo | Mesorregião (5) | AMC (164) |
|---|---|---|
| **Espacial** η² | 1,3% | 7,5% |
| **Espacial** ω² (corrigido) | 1,3% | 7,5% |
| **Espacial** líquido de acaso (perm.) | 1,3% (acaso 2,5·10⁻⁷) | **7,5%** (acaso 1,0·10⁻⁵) |
| **Ato (tempo)** η² | **19,6%** | **19,6%** |
| **DENTRO das células** espaço×ato (1−ω²) | **79%** | **75%** |

(Para a variância da *idade* bruta: espacial η² = 3,7% (meso) / 12,7% (AMC); within-célula
78% / 71%.)

Sob o censo, ω² e "líquido de acaso" deixaram de acrescentar informação ao η² (ver ressalva
D23 no Método) — ficam na tabela por continuidade, não por conteúdo.

### 3. O recorte fino capta MAIS — mas pouco, e ainda minoria

Indo da mesorregião para a AMC, a parcela espacial da separação jovem/velho sobe de
**1,3% → 7,5%**, ~5,8×. A mesorregião era grossa: geografia fina captura sinal genuíno que
ela escondia. (Esse ganho não pode mais ser creditado à permutação, que degenerou — ele se
sustenta pelo **tamanho** do η² e pela estabilidade entre fontes, abaixo.)

**Mas a conclusão não muda**: mesmo no recorte fino, (a) o espaço explica ~7,5% da separação
jovem/velho, **menos que o tempo (19,6%)**; (b) **75%** mora *dentro* das células; e (c)
**162/164** AMCs seguem bimodais por dentro.

### 4. Estabilidade censo × amostra (o que substitui o p-valor)

Com o piso do acaso colapsado, a robustez vem de o resultado não depender do recorte. Rodando
a mesma implementação ponderada sobre a amostra corrigida (`--fonte amostra`, w≡1, n=15.933):

| Métrica (malha meso) | Censo (16,0 M) | Amostra corrigida (15.933) |
|---|---|---|
| Espacial η² (p_velho) | 1,3% | 2,1% |
| Ato (tempo) η² | 19,6% | 20,2% |
| Within células (1−ω²) | 79% | 78% |
| Unidades bimodais | 5/5 | 5/5 |
| Células bimodais | 9/10 | 9/10 |

Três ordens de magnitude de diferença em n movem o η² espacial em menos de um ponto
percentual e não mudam nenhuma classificação. **É isto — e não o ΔBIC nem o p — que sustenta
o veredito.**

### Veredito

> A bimodalidade **NÃO é regionalmente causada**, nem na mesorregião nem na AMC. Os dois
> mecanismos **coexistem em praticamente toda unidade**; a geografia **modula o peso** da
> mistura ao longo de um gradiente Sul→Norte — um pouco mais nitidamente em resolução fina —
> mas **não cria os modos**. O que mais desloca o peso é o **tempo** (o pulso jovem recente
> do Ato III, coerente com o *onset* da soja direta do #41), não a latitude.

> [!WARNING]
> **Re-checagem sob a união (D26, 23/jul/2026, `bimodalidade_regional_uniao.py`) — a metade
> ROBUSTA sobrevive; o "gradiente Sul→Norte" era artefato.** O #28C usa só `pasto→agricultura`;
> o bracket-por-evento do #40 mostrou que esse subconjunto é selecionado pela mudança de rótulo. Com o
> cubo reprocessado (`pastagem_conversao_destinos.parquet`), recomputei as três afirmações sob
> `pasto→agricultura` × `pasto→(agric∪mosaico)`:
>
> | afirmação | agric (16,0 Mpx) | união (59,5 Mpx) | veredito |
> |---|---|---|---|
> | **bimodalidade** (regiões · células) | 5/5 · 9/10 | **5/5 · 10/10** | **ROBUSTA** (sobrevive/fortalece) |
> | **within-célula domina** | 77,8% | **76,1%** | **ROBUSTA** |
> | **η²(mesorregião) da idade** | 3,7% | **0,5%** | "não-regional" ainda mais forte |
> | **gradiente idade mediana Sul→Norte** | 9·9·10·16·16 (ampl. **7a**) | 9·9·10·10·11, ordem embaralhada (ampl. **2a**) | **ARTEFATO** — colapsa |
>
> **Leitura corrigida:** o **núcleo do #28C sobrevive e sai reforçado** — os dois mecanismos
> coexistem dentro de cada região e a geografia explica quase nada (η² cai de 3,7% para 0,5%),
> então "a bimodalidade NÃO é regionalmente causada" fica **mais** verdadeiro sob a união. Mas
> a cláusula **"a geografia modula o peso ao longo de um gradiente Sul→Norte" é artefato**: sob
> a união a amplitude Sul→Norte cai de 7a para 2a e o Norte perde a assinatura de pasto velho
> (Noroeste 16→11, Norte 16→10). Isso é o **mesmo artefato do #40** — o gradiente young-Sul/
> old-Norte existe só no subconjunto rotulado "agricultura". **O que desloca o peso é o TEMPO,
> não a latitude** — e a re-checagem torna isso ainda mais claro (η²(ato) sobe de 18,6% para
> 23,2% na união, η²(região) some). A frase para a banca: bimodalidade robusta + coexistência
> within-região; **retirar a afirmação de gradiente latitudinal na idade**.

> ### ➕ A FORMA também difere entre regiões — e também é artefato (28/jul/2026)
>
> **Como apareceu.** Na revisão da Perna 2 do site, o autor olhou os histogramas por
> mesorregião e notou que Norte e Noroeste *parecem* mais bimodais que Sul e Centro. O #28C
> nunca tinha medido isso: ele mede **coexistência** (os dois componentes existem ali?) e
> responde 5/5. Coexistência e **forma** são coisas diferentes — uma mistura pode ter os
> dois componentes e mesmo assim não produzir vale nenhum, se o componente velho for largo
> o bastante para virar ombro. Medido em `scripts/forma_regional_bimodalidade.py`:
>
> | mesorregião | vale no histograma bruto — `agric` | sob a **união** |
> |---|---|---|
> | Sul · Centro · Leste | **não há** (Centro: 0,08, marginal) | não há |
> | Noroeste | **0,415** | **0,058** |
> | Norte | **0,271** | não há |
>
> O olho estava certo: sob a régua exposta a diferença de forma é grande e sistemática. O
> peso do componente jovem varia de 0,239 (Norte) a 0,390 (Centro), e a **distância de
> variação total** entre os histogramas separa as cinco regiões em dois blocos —
> dentro de {Sul, Centro, Leste} TV = 0,053–0,092; dentro de {Norte, Noroeste} TV = 0,076;
> **entre os blocos, 0,177–0,234**.
>
> **E é o mesmo artefato.** Sob `pasto→(agric∪mosaico)` a diferença colapsa: w₁ passa a
> 0,380–0,435 (quase plano), o vale só sobrevive no Noroeste e raso (0,058), e a TV
> Sul × Norte cai de **0,223 para 0,023** — um décimo. A mudança de rótulo perde mais
> conversão ao norte, e o que sobra lá é uma amostra enviesada para a ponta velha; é ela
> que cava o vale.
>
> **Consequência para a redação.** "As cinco regiões têm o mesmo desenho" é verdadeiro
> **sob a régua imune** e falso sob a exposta — então a afirmação precisa vir com a régua
> declarada, e qualquer figura que a acompanhe tem de ser desenhada na régua certa. Foi
> exatamente esse o defeito encontrado no site: a peça desenhava `agric` enquanto o texto
> ao lado afirmava a conclusão da união. Corrigido — a peça passou a oferecer as duas, com
> a imune por padrão (`export_idade_bracket_viz.py`).
>
> **Ressalva honesta:** mesmo na união o Noroeste guarda um vale raso e é a região mais
> distante das demais (TV 0,072–0,115). "Praticamente o mesmo desenho" é a frase certa;
> "idêntico" não é.

> ### ➕ A bimodalidade por ATO — e por que o Ato I não conta (28/jul/2026)
>
> **A pergunta.** Levantada na revisão da Perna 2: "a bimodalidade não se sustentava só no
> Ato III?" É a pergunta certa a fazer, porque se ela só aparecesse ao juntar os três
> períodos, seria **composição temporal** e não coexistência. Recomputado por célula
> região×ato nas duas réguas:
>
> | recorte | `agric` | **união** |
> |---|---|---|
> | **Ato I** (1985–2000) | **0/5** unimodal em toda parte | **0/5** unimodal em toda parte |
> | **Ato II** (2001–2019) | 4/5 (falha Noroeste, w₁=0,121) | **5/5** |
> | **Ato III** (2020–2024) | 5/5 | **5/5** |
> | Ato II + III (o recorte do §1) | 9/10 | **10/10** |
>
> **A resposta é não — e o Ato I é justamente a prova.** O Ato I é unimodal em toda parte
> porque **não pode ser outra coisa**: uma conversão em 1995 se dá sobre um pasto que tem,
> no máximo, 10 anos, e a série só começa em 1985. Para *observar* um pasto de 22 anos
> sendo convertido é preciso chegar a 2007. Ou seja, a população velha é **inobservável**
> no Ato I, não ausente — o GMM ali ajusta dois componentes a 3,3a e 7,6a, separação 4,2a,
> abaixo do limiar de 5a. Ler isso como "a segunda população não existia nos anos 1990"
> seria confundir horizonte de observação com fenômeno, exatamente o erro que a censura à
> esquerda existe para evitar.
>
> **O que sustenta o achado:** Ato II sozinho (32,5 M eventos na união — o maior bloco) é
> bimodal por si, e Ato III sozinho também, em todas as regiões. A coexistência **não** é
> subproduto de empilhar períodos. É por isso que o §1 conta células de Ato II e III e
> exclui as de Ato I por construção: incluí-las mediria o desenho da série, não o
> território.
>
> ⚠️ **Não derivar tendência disto.** Que o vale seja mais fundo no Ato III (dip 0,21–0,48
> na união, contra 0,00–0,06 no Ato II) é, em boa parte, o mesmo efeito de horizonte
> operando ao contrário — quanto mais tarde a janela, mais idade cabe nela. O eixo temporal
> segue suspenso (D25/D26).
>
> Reproduzível com `scripts/forma_regional_bimodalidade.py` (as células por ato saem do
> mesmo `carregar`/`carregar_uniao` usados ali).

## Conexão com a narrativa

- **Fecha a pergunta de precisão deixada por #28/#40.** O #40 entregou a *geografia* das duas
  lógicas (Rotação no Sul × Oportunístico no Norte); o #28C mede **quanto** dessa geografia é
  composição (between) vs coexistência (within) — e responde: coexistência domina (~75–79%).
- **Reforça e quantifica a D14.** O #40 mostrou que a latitude é confundidor de 1ª ordem em
  cross-section; o #28C mostra que, mesmo *sendo* o eixo organizador do peso, a geografia
  explica só ~1–8% da separação jovem/velho. A frase correta passa a ser **"gradiente
  regional no peso da mistura"**, nunca "bimodalidade causada pela região".
- **Responde a uma limitação do Encerramento** ("o recorte mesorregional (5 unidades) é
  grosso"): replicado na malha AMC, com ω² + permutação contra a inflação — a conclusão é
  robusta às duas malhas.

## Limitações honestas

1. **Observacional.** η²(espacial) baixo prova que a geografia não **gera** os modos; não
   prova que "região não importa para nada" — ela move o peso, e esse gradiente é real
   (medianas 9→16a, ordenação idêntica em censo e amostra). ⚠️ A versão anterior desta
   limitação creditava o gradiente a "p=0,005 na AMC"; sob censo esse p é mecânico (D23) e
   **não deve ser citado** — o que sustenta o gradiente é tamanho de efeito + estabilidade
   entre fontes.
2. **"Espacial" é um proxy de um pacote** (aptidão de solo, chuva, preço da terra,
   infraestrutura, distância a esmagadoras) — a decomposição diz *quanto* o espaço capta, não
   *qual* fator dentro dele.
3. **Censura à esquerda** herdada do #28 (idades truncadas quando o pasto já existia em 1985);
   por isso só os **não-censurados** entram (16.004.530 eventos). A bimodalidade é do regime
   recente. O censo **não reduz** a censura — ela é limite da série MapBiomas, não da amostra.
   ⚠️ Esta página mede **forma**, não nível: as medianas aqui descrevem a subpopulação
   observável e **não** são comparáveis com as do #33. Ver
   ["O que a família da idade estabelece"](28_idade_pastagem.md#o-que-a-família-da-idade-estabelece).
4. ~~**GMM e BC concordam, mas n pequeno** em algumas células AMC×ato~~ — **superado pelo
   censo**: as 164 AMCs passaram todas o filtro n≥100 (antes eram 36 de 158). O filtro
   permanece no código como salvaguarda, mas não morde mais. Atenção: o filtro conta
   **eventos (Σpeso)**, não linhas da tabela de contingência.
5. **BC de Sarle discorda do GMM em 24 AMCs** (140/164 acima de 0,555, contra 162/164
   bimodais pelo GMM). O BC é sensível a assimetria e a corroboração *model-free* é, nessas
   unidades, mais fraca que o ajuste paramétrico. Não altera o veredito — que se apoia na
   decomposição, não na contagem de bimodais — mas a frase "GMM e BC concordam" não vale
   mais para a malha fina e foi removida.

## Como rodar

```bash
python scripts/bimodalidade_regional.py                  # malha mesorregião (5), censo
python scripts/bimodalidade_regional.py --malha amc      # malha AMC (164), censo
python scripts/bimodalidade_regional.py --fonte amostra  # amostra corrigida (contraste)
python scripts/bimodalidade_regional.py --testar         # contrato D24 das estatísticas com peso
# lê pastagem_idade_censo.parquet (#28); na malha AMC também amc_crosswalk_goias.csv (#25).
# escreve idade_bimodalidade_{por_grupo,decomposicao}[_amc][_amostra].csv + 1 PNG por malha.
# Os CSVs trazem coluna `fonte` — censo e amostra não se sobrescrevem nem se confundem.
```
