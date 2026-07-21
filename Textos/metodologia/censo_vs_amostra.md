# Censo × amostra — auditoria e reconstrução do Pipeline #28

**Decisões D21–D24** (2026-07-21): registro do episódio em que o [#28](../pipelines/28_idade_pastagem.md)
deixou de ser amostra de pixels e virou censo, e das quatro regras reutilizáveis
que saíram dele.

> **Para que serve este documento**: (a) responder à pergunta de banca "por que
> seus números mudaram?"; (b) impedir que alguém — inclusive você daqui a seis
> meses — reverta para a amostra por achá-la mais simples; (c) registrar três
> armadilhas que valem para **qualquer** pipeline, não só o #28.

---

## 1. Como o episódio começou

Uma IA externa auditou o #28 e apontou um defeito na coleta. Estava certa, e a
verificação confirmou: `coleta_idade_pastagem.py` usava `gdf_muni.union_all().envelope`
como região de amostragem — o **retângulo envolvente** de Goiás, não o polígono.
Como o estado tem formato irregular, a bbox engolia faixas de MT, MS, MG, BA e TO.

Verificação por *point-in-polygon* contra o polígono estadual:

| | |
|---|---|
| Linhas com `cd_mun == 0` | 34.049 de 78.000 (43,7%) |
| Dessas, **realmente fora** de Goiás | 34.046 (**99,991%**) |
| Falhas de sjoin (dentro, mas sem município) | **3** |
| Amostra de 5.000 com `cd_mun != 0` dentro de GO | **100,00%** |

A correção aplicada por ela — filtrar `cd_mun != 0` — é **estatisticamente
válida**: condicionado a cair em Goiás, a seleção continua uniforme; custa
tamanho de amostra, não validade. Todos os números revisados reproduziram.

Mas a aplicação teve três defeitos, e é deles que vem a primeira lição.

### 1.1 Misatribuição

A nota de correção creditava ao envelope toda a mudança da tabela por Ato. Mas os
números antigos (6 / 19 / 17) reproduziam exatamente como **todos os pixels,
inclusive censurados**, enquanto o cabeçalho da coluna dizia "não-censurado" —
erro de rótulo pré-existente e independente. Decompondo o Ato II:

```
19 (antigo, todos os pixels)  →  13 (não-censurado)  →  12 (não-censurado + só GO)
        └── correção de censura: 6 anos ──┘   └── envelope: 1 ano ──┘
```

O envelope era o fator **menor**. Corrigir um bug e atribuir-lhe uma mudança que
veio de outro é pior do que não corrigir: cria uma explicação falsa que ninguém
vai reexaminar.

### 1.2 Propagação parcial

A legenda da figura no site foi reescrita; a **figura** não foi regerada (era um
PNG de 20/mai sem script que a gerasse). Legenda e imagem passaram a discordar em
silêncio. Três blocos de `index.html` e cinco documentos ficaram com números
velhos.

### 1.3 Causa-raiz de pé

A coleta continuava amostrando o envelope. Consequências não mencionadas: 44% do
orçamento do GEE desperdiçado, 52% dos municípios com <20 px não-censurados, e a
fatia de GO por ano variando de 32,8% a 79,1% **caindo ao longo do tempo** — o
que quebra qualquer estatística agregada por período.

---

## 2. O segundo bug — o que ninguém tinha achado

Durante a validação do censo contra a amostra, um teste de round-trip acusou
divergência: células com `classe_antes_id = 21` na referência apareciam como
`classe_antes_id = 0` no censo.

**MapBiomas classe 21 = "Mosaico de Usos" não estava no `GRUPO_MAP`.** E o código
fazia:

```python
out["origem_anterior"] = out["classe_antes_id"].map(ID_PARA_GRUPO).fillna("censurado_esquerda")
```

Qualquer classe ausente do dicionário caía no `.fillna(...)` e era rotulada
**censurada** — "idade desconhecida" — sendo que a idade era perfeitamente
conhecida. Era a única classe faltante, e respondia por:

| | Publicado | Real |
|---|---|---|
| Taxa de censura (amostra estadual) | 74,9% | **63,7%** |
| Não-censurados | 11.035 | **15.933 (+44%)** |

**Por que isso é pior do que o envelope:** *todas* as análises-manchete do #28
rodam sobre o subconjunto não-censurado — GMM, bimodalidade, medianas por Ato,
regra de decisão. Elas usavam dois terços dos dados a que tinham direito. E os
excluídos não eram aleatórios: eram especificamente os de origem mista
agricultura/pastagem, ou seja, a categoria substantivamente mais próxima do
mecanismo "rotação" — um dos dois que o #28 afirma distinguir. O bug removia
evidência **preferencialmente de um lado da conclusão**.

A causa-raiz é de projeto: o código usava `0` tanto para "censurado" quanto para
"lookup falhou". São coisas diferentes e precisam de códigos diferentes.

---

## 3. O que o censo mudou

44.639.028 eventos de conversão (1.016× a amostra), 3.817.080 ha = 11,2% de
Goiás, 244 de 246 municípios.

A comparação foi desenhada em **dois níveis de propósito**, porque amostra e
censo diferem por duas causas independentes que o agregado confunde:

**Nível 1 — por ano (isola erro amostral).** Diferença de mediana: média
−0,09 a, máx |2| a. Censura: média −0,17 pp. **A amostragem dentro de cada ano
era sadia.**

**Nível 2 — agregado (expõe a ponderação).** Ato III: mediana 6 na amostra
contra 8 no censo; censura 24,7% contra 32,2%. E as medianas **ano a ano** do
Ato III são idênticas (2020: 20 e 20; 2021: 11 e 11; 2022: 4 e 4; 2024: 5 e 5).
Logo a discrepância é **100% composição**:

| ano | peso na amostra | peso real | mediana do ano |
|---|---|---|---|
| 2020 | 22,2% | **43,2%** | 20 a |
| 2024 | 24,5% | **11,2%** | 5 a |

`2.000 px/ano` tratava um ano de 607 mil conversões igual a um de 157 mil.

### O que sobrevive e o que cai

| | Amostra | Censo | |
|---|---|---|---|
| μ₁, μ₂ (Ato III) | 4,6 / 22,7 a | 4,4 / 22,9 a | ✅ estáveis |
| Gradiente Sul→Norte | 7 → 14 a | 9 → 16 a | ✅ ordenação idêntica |
| Direção da tendência | w₁ sobe | w₁ sobe | ✅ |
| **w₁ (Ato III)** | 62,3% | **51,5%** | ❌ |
| **Rotação (2020-24)** | 54,7% | **43,0%** | ❌ |
| Munis com <20 px | 44% | **0%** | capacidade nova |

A frase "a rotação está se tornando dominante" **não sobrevive**: o componente
jovem *alcança* o antigo (51,5% × 48,5%), não o supera.

### A coincidência que vale registrar

Se `mosaico` fosse somado à rotação, o censo daria 51,2% → 62,8% — quase o
publicado (48,7% → 64,8%). Ou seja: **a manchete antiga sobrevivia por acaso.**
O bug excluía o mosaico do denominador, o que compensava numericamente incluí-lo
no numerador. Duas correções em direções opostas quase se cancelavam.

Isto é um alerta geral: *números que continuam batendo depois de um bug ser
corrigido não são prova de que o bug era inofensivo.*

**Decisão substantiva:** mosaico fica como categoria própria. O MapBiomas usa
essa classe quando **não consegue separar** lavoura de pasto — é incerteza de
classificação, não uso observado; somá-la à rotação importaria a incerteza do
classificador para dentro da conclusão. ⚠️ *Esta caracterização da classe 21 foi
afirmada de conhecimento e não conferida contra a documentação da Coleção 10.1 —
verificar antes de a frase ir para o texto final.*

---

## 4. As quatro decisões

### D21 — Toda amostragem espacial declara a fração fora do recorte

`region` derivada de `.envelope`, `.bounds` ou bbox é **armadilha silenciosa**: o
overlay posterior conserta o *rótulo* de cada ponto, mas não a *alocação* da
amostra. Antes de usar qualquer amostra espacial, calcule e reporte a fração que
caiu fora do recorte pretendido. Se for material, a amostra não é do que você
pensa que é.

### D22 — Sentinela de erro nunca compartilha código com categoria real

`.fillna(<categoria substantiva>)` depois de um `.map()` transforma **falha de
configuração em dado**. Regras:

- categorias substantivas, sentinela de "não mapeado" e sentinela de "sem dado"
  recebem **códigos distintos**;
- o preenchimento padrão de um lookup é o sentinela de erro, nunca zero nem uma
  categoria válida;
- condições estruturais (aqui: censura) são decididas por **índice/cálculo**,
  jamais por sucesso ou fracasso de um lookup;
- classe não reconhecida faz o pipeline **avisar alto**, não seguir quieto.

### D23 — Com censo, ΔBIC e p-valor deixam de medir evidência

Quando *n* é a população, qualquer desvio ínfimo do modelo nulo produz estatística
astronômica (aqui: ΔBIC de 844.789 no Ato III). Isso reflete o tamanho de *n*,
**não** força de evidência. Com censo:

- a robustez vem de **estabilidade entre recortes** (janelas, malhas, períodos),
  não de teste de hipótese;
- o ganho real é **precisão dos parâmetros** (μ, w), e é isso que se reporta;
- nunca escrever "com o censo o ΔBIC subiu, logo a evidência é mais forte".

### D24 — Estatística ponderada verificada por contrato

Quando dados agregados (célula + peso) substituem dados linha-a-linha, toda
estatística ponderada **deve reduzir exatamente ao caso não-ponderado com
peso = 1**, e isso é verificado por teste, não presumido. É esse contrato que
permite rodar a mesma análise sobre amostra e censo sabendo que qualquer
diferença vem dos **dados**, não da troca de implementação.

Implementado em [`scripts/estatistica_ponderada.py`](../../scripts/estatistica_ponderada.py)
(`python scripts/estatistica_ponderada.py` roda a suíte). Inclui GMM ponderado por
EM, porque `sklearn.mixture.GaussianMixture` não aceita `sample_weight`.

---

## 5. Receita — quando trocar amostra por censo

Não é sempre. O censo aqui foi **parcialmente exagero**: a comparação ano a ano
mostrou que a amostra era sadia dentro de cada ano, e o defeito de ponderação
entre anos se corrigiria reponderando a amostra pela área convertida — vinte
linhas, não um pipeline novo.

**Vá para censo quando** o gargalo for **granularidade**, não viés: aqui, 44% dos
municípios tinham <20 px não-censurados, o que tornava a mediana municipal e o
mapa de AMCs ruído apresentado como padrão. Isso o censo resolve e a reponderação
não.

**Fique na amostra quando** o problema for só de peso entre estratos — reponderar
é mais barato, mais portátil e não cria dependência de 1,5 GB.

**Antes de decidir, meça.** A intuição erra:

| Estimativa a priori | Medido |
|---|---|
| "cubo de 40 bandas = 28,7 GB, inviável local" | comprime **18,8×** → 1,5 GB |
| "precisa de máquina com muita RAM" | ~500 MB em janelas; roda em laptop de 7,7 GB |
| "processar leva horas" | **3,5 min** |

### Checklist de validação (o que efetivamente pegou defeito)

1. **Equivalência com a implementação anterior** — a lógica nova reproduz a antiga
   nos mesmos dados? (Aqui: idade e classe-antes idênticas em 39/39 anos.)
   Sem isso, é impossível distinguir "número mudou porque os dados mudaram" de
   "número mudou porque reimplementei errado".
2. **Round-trip da agregação** — decodificar o acumulado devolve exatamente o que
   entrou? *Foi este teste que revelou o bug da classe 21.*
3. **Partição sem sobreposição** — tiles se sobrepondo contam pixels em
   duplicidade sem deixar rastro no resultado. Verificado antes de processar; e
   o detector foi confirmado disparando num caso real de 8192×8192 px.
4. **Invariantes de domínio** — aqui, idade ≥ 1 sempre (a conversão exige pasto
   no ano anterior). Se cair para 0, o contador dessincronizou.
5. **Zeros são "não ocorreu" ou "não foi processado"?** Dois municípios ficaram
   com zero eventos; conferido por rasterização que ambos estavam cobertos
   (480 mil e 955 mil px) — é ausência real de conversão, no Vão do Paranã.
6. **Números do documento conferidos contra o dado, por script** — não por
   leitura. (20 de 20 conferem.)

---

## 6. Armadilhas que o censo *cria*

Trocar amostra por censo não é só ganho:

- **D23 acima** — a estatística de teste vira ornamento e, pior, ornamento que
  cresce, parecendo evidência mais forte.
- **Independência some da vista.** Um pixel pode converter mais de uma vez
  (pasto→lavoura→pasto→lavoura): 1,064 eventos por pixel distinto. Inofensivo
  para descrição, relevante para qualquer erro-padrão.
- **Área do pixel varia com a latitude.** Em EPSG:4326 a área de solo é ∝ cos(lat);
  Goiás cobre 7°, então pixels do norte cobrem 3,5% mais chão. Contagem e área
  deixam de ser a mesma coisa — e o eixo norte-sul é justamente o da tese da
  marcha. O parquet traz `n_pixels` **e** `area_ha`.
- **Reprodutibilidade fica mais cara.** A amostra rodava em 80 min só com a API.
  O censo exige auth com escopo Drive, 1,5 GB de download e um export que precisa
  ser refeito se o MapBiomas atualizar a coleção.
- **O que o censo NÃO resolve:** censura à esquerda (64,1% — é limite da série,
  que começa em 1985), erro de classificação do MapBiomas (que passa a ser a
  **maior** incerteza restante, já que o erro amostral saiu de cena), e
  identificação causal.

---

## 7. Efeito colateral em outro pipeline

O `export_idade_histograma_regional.py` (#28C) tinha escolhido operar em
**mesorregiões** em vez de AMCs porque só 36 de 158 AMCs tinham n≥100 pixels
não-censurados. Com o censo, **164 de 164 passam**. A restrição que motivou a
escolha desapareceu; a decisão de qual malha o site expõe virou editorial, não
técnica. Ambos os blocos continuam exportados.

---

## 8. Rastro de arquivos

| Arquivo | Papel |
|---|---|
| `scripts/export_cubo_mapbiomas_go.py` | Export batch do cubo, alinhado à grade nativa |
| `scripts/baixa_export_drive.py` | Download (reusa o refresh token do GEE, que já tem escopo Drive) |
| `scripts/processa_cubo_idade.py` | Censo em janelas → tabela de contingência |
| `scripts/estatistica_ponderada.py` | Estatística com peso + suíte do contrato (D24) |
| `scripts/analise_reserva_terra.py` | Análise, `--fonte censo\|amostra` |
| `scripts/compara_censo_amostra.py` | Confronto em dois níveis (§3) |
| `scripts/fig_sintese_idade_atos.py` | Figura do site (antes era PNG órfão sem script) |
| `scripts/coleta_idade_pastagem.py` | Amostra legada — mantida para reprodutibilidade |

Ver também: [28_idade_pastagem.md](../pipelines/28_idade_pastagem.md),
[28_idade_pastagem_critica.md](../pipelines/28_idade_pastagem_critica.md),
[28C_bimodalidade_regional.md](../pipelines/28C_bimodalidade_regional.md).
