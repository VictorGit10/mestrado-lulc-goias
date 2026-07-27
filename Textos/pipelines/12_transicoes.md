# Pipeline #12 — Matrizes de transição pixel-a-pixel via GEE

**Script**: `scripts/transicoes_mapbiomas.py` + `scripts/visualizar_transicoes.py`
**Depende de**: Earth Engine autenticado.
**Outputs**: `data/cache/transicoes/` (9 CSVs) + `outputs/transicoes/` (visualizações).

## O que faz

Calcula matrizes de transição pixel-a-pixel via Google Earth Engine para pares de anos do MapBiomas Coleção 10.1, agregando as 22 classes em 6 grupos. Para cada município de Goiás, cruza o raster do ano-origem com o ano-destino e gera tabela de fluxo (ex: hectares que eram Floresta em 1995 e viraram Pastagem em 2005).

## Pares de anos calculados

`data/cache/transicoes/` contém 9 CSVs (mais pares do que os 5 períodos publicados em `outputs/transicoes/`):
- 1985→1995, 1985→2000, 1985→2010, 1985→2024
- 1995→2005, 2000→2010
- 2005→2015, 2010→2024, 2015→2024

## Visualizações

`scripts/visualizar_transicoes.py` produz:
- Heatmaps origem×destino
- Diagramas Sankey
- Mapas coropléticos das principais conversões

## Como rodar

```bash
python scripts/transicoes_mapbiomas.py
python scripts/visualizar_transicoes.py
```

## Diferença vs Pipeline #5

- Pipeline #5 (proxy) confronta **estoques** anuais — pastagem em t e soja em t+1, sem pareamento espacial.
- Pipeline #12 (este) faz **pareamento pixel-a-pixel real** — cada pixel sabe sua trajetória.

Para a versão final da dissertação, **#12 substitui #5** como fonte primária da matriz de transição. #5 fica como validação cruzada e baseline metodológico.

---

## ✅ FECHADO em 27/jul/2026 pelo #12B — leia esta seção antes da seguinte

A limitação registrada abaixo (25/jul) **foi resolvida**. A matriz primária passou a ser
recontada localmente, com o Mosaico como grupo próprio, por
[`scripts/transicoes_cubo.py`](../../scripts/transicoes_cubo.py) (#12B).

**O custo estimado estava errado.** O texto abaixo diz que fechar exigia "re-exportar os
caches do GEE". Isso deixou de ser verdade em 21/jul, quando o #28 baixou o cubo completo
(`data/raw/cubo_go/`, 16 shards, 40 bandas, **IDs brutos** do MapBiomas). O descarte da
classe 21 nunca esteve na fonte — ele morava na tradução ID→grupo, que roda aqui. A
recontagem é **local e offline: 13 min**, sem GEE, sem cota, sem autenticação.

### O que a validação mostrou (`scripts/validar_transicoes_cubo.py`)

| bloco | resultado |
|---|---|
| **A — Δ_medida** | **−0,43%**, uniforme (p05/p95 = −0,63%/−0,34% por célula, 48/48 pares entre −0,43% e −0,42%). Trocar `reduceRegions`(EPSG:5880, scale=30) por pixel nativo + `cos(lat)` **não desestabiliza nada** |
| **B — batimento vs #4, com a classe 21 nos dois lados** | o censo bate a **−0,1%** nos 7 grupos. O #12 cobria 87–99% de cada grupo e **0,0% do Mosaico** (2,39 Mha em 1995; 3,59 Mha em 2024) |
| **C — fechamento** | censo perde **0,08%** de Goiás; o #12 perdia **7,26%** na mediana (18,5% no pior par) |

A massa que o #12 descartava é de **6,5% a 10,9% de Goiás, todo ano** — 3,72 Mha em 2024.
Não era resíduo.

### Confirmações independentes

- A razão `P→mosaico / P→agric` sai de **0,66** (2015) a **37,83** (2024) na matriz completa,
  contra 0,66→37,7 do `pastagem_conversao_destinos.parquet` (#28D). São **caminhos de código
  distintos** — o #28D rastreia saídas de pastagem; o #12B monta a matriz inteira.
- No Sul goiano, Ato II→III: `pasto→agric` sozinho dá **−88%** (a manchete antiga, reproduzida
  exatamente) e `pasto→(agric ∪ mosaico)` dá **+51%**. O site já publicava "acelera cerca de
  50%" pelo bracket da D26 — **a régua consertada e o remendo convergem**.

### Achado colateral: `veg→mosaico` **não** é desmatamento

Com o grupo 7 visível, `veg→antrópico` subiria +49,1% na série se o Mosaico entrasse na lista
`antro`. **O PRODES rejeita essa leitura**: na janela 2013–2024, em que MapBiomas e PRODES
concordam 1:1, incluir `veg→mosaico` leva a razão para **1,35**. Logo `veg→mosaico` é
majoritariamente deriva de classificador na borda, não corte raso — e `antro` **permanece**
`[pastagem, agricultura, area_urbana]` em `validacao_prodes_mapbiomas.py` e
`custo_carbono_marcha.py`. O #48 segue válido sem alteração.

### O que **não** foi revogado

A **D26 continua de pé**. A ambiguidade do Mosaico é *semântica* — o MapBiomas não distingue
lavoura de pasto naquele pixel —, não é dado faltante. O grupo 7 dá as duas réguas do bracket
**exatas** em vez de pisos (o `intensity_bracket.py` só conseguia reinjetar `pasto→Mosaico`, e
declarava sua régua superior como ela mesma um piso). O bracket deixa de ser remendo de dado e
vira escolha de leitura — com extremos medidos.

### Regra de exibição: fluxo pinta, estoque não

O Mosaico **aparece** onde o objeto é *fluxo* — Sankeys por Ato, `sankey_regional.json`,
`sankey_data.json`, a figura `fluxos_chave.png` (3 barras) e os 5 coropléticos de transição
dominante (`transicao_*.webp`). Em 2015–2024 ele domina **194 dos 246 municípios**, e é essa a
informação que o mapa existe para dar.

Continua **fora da tinta** onde o objeto é *estoque/cobertura*: os 40 mapas anuais de LULC
seguem com `.selfMask()` na classe 21 (`IMPLEMENTACAO.md` §3.7.1) e a barra empilhada do site
mantém o Mosaico com faixa própria — "conta, mas não pinta". As duas regras não se contradizem:
num mapa de cobertura o Mosaico é ruído visual; num mapa de fluxo ele **é** o achado.
(Decidido pelo autor em 27/jul/2026.)

### Pendência aberta desta passada

O pico de KL da periodização (#29) migrou de 2020 para **2022** sob a matriz de 7 grupos
(2019–2022 num cluster apertado: 0,0108 / 0,0128 / 0,0139 / 0,0162). **`config_periodos.py` não
foi alterado** — a fronteira de 2020 foi estabelecida por triangulação com a quebra do SIDRA
soja, não pelo KL, que o #29c já registrava como contaminado. Decidir se o cluster muda o Ato III
é análise, não repropagação.

---

## 🛑 Limitação estrutural (registro histórico — resolvida acima em 27/jul/2026)

`transicoes_mapbiomas.py` **exclui a classe 21 (Mosaico de Agricultura ou Pastagem)** do mapa de
6 grupos — os IDs não listados vão para `0` e são mascarados. A justificativa está escrita no
cabeçalho do script:

> `EXCLUÍDO: ID 21 (Mosaico de Agricultura ou Pastagem) — no Cerrado goiano, maioria é pastagem, não agricultura.`

**Essa justificativa não sobrevive ao [#28D](28D_deriva_mosaico.md).** Ela foi escrita quando o
Mosaico era um resíduo estável; a auditoria de julho/2026 mostrou que, no fim da série, ele é
justamente **o destino para onde a conversão migra** (a razão `P→mosaico / P→agric` vai de 0,6 em
2015 para **32,5** em 2024, enquanto o SIDRA registra a soja **+38%**). Ou seja: a classe descartada
por ser "resíduo de pastagem" virou o terminal da rota que mais interessa.

### Consequência

A matriz do #12 — a fonte primária de transições da dissertação, que alimenta [#19](19_conversoes_brutas.md)
e [#33](33_transicoes_regionais.md) — **perde a rota `pastagem → Mosaico → agricultura`**. Onde essa
rota carrega o fluxo, a matriz mostra o pixel simplesmente **saindo da contabilidade**, o que se lê
como "a conversão parou". É exatamente o artefato que a **[D25](../metodologia/tratamento_deriva_mosaico.md)**
descreve, e é a razão pela qual **todo número desta matriz que tenha "agricultura" no destino precisa
ser lido sob o bracket da [D26](../metodologia/tratamento_deriva_mosaico.md)** — nunca na régua crua.

### A validação batimental não protege disso

`validar_batimental()` compara os totais por classe-destino do #12 contra o [#4](04_mapbiomas_municipal.md).
O #4 **carrega** a classe 21 (9.840 linhas: 246 munis × 40 anos), mas a função mapeia os `class_id` do #4
pelo **mesmo** dicionário de 6 grupos e faz `dropna(subset=["classe_agg"])` — descartando a classe 21
**dos dois lados** antes de comparar. A validação é, portanto, **cega por construção** ao Mosaico: ela
confere que os dois pipelines concordam *no subconjunto que ambos enxergam*, e passaria com δ≈0 mesmo
que 100% da conversão recente tivesse migrado para o rótulo excluído. **Um batimento verde aqui não é
evidência de que a rota do Mosaico está coberta.**

### O que seria preciso para fechar

Re-exportar os caches de transição do GEE com a classe 21 como **grupo próprio** (7 grupos, não 6),
propagando a `agregar_conversoes.py` → `analise_transicoes.py` → #19/#33 e aos JSONs do Sankey da
visualização. É **re-execução de GEE + repropagação a jusante**, não um ajuste de leitura — por isso
está registrado aqui como limitação declarada e **não** foi feito nesta passada.

> **Como de fato foi feito (27/jul): sem GEE.** O cubo local do #28 já continha os IDs brutos, e a
> recontagem virou um passe de 13 min (`transicoes_cubo.py`). O diagnóstico acima está correto —
> inclusive a crítica à `validar_batimental()`, confirmada em número: o #12 cobre **0,0%** do
> estoque de Mosaico do #4. Só a **estimativa de custo** estava errada. A régua de uso abaixo está
> **revogada**; ver a seção ✅ no topo do doc.

~~Enquanto não for:~~

- ~~**não** citar a matriz do #12 crua para qualquer afirmação sobre `pasto→agricultura` no Ato III;~~
- ~~usar o bracket da D26 (`agric` como piso, `agric ∪ mosaico` como teto) e a **âncora SIDRA**;~~
- ~~tratar `veg→pasto` (que não passa pelo Mosaico) como a transição **imune** do conjunto.~~

Ver a tabela de alcance auditado em
[`metodologia/tratamento_deriva_mosaico.md`](../metodologia/tratamento_deriva_mosaico.md).
