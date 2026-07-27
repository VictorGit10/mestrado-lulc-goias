# Pipeline #14 — Fogo MapBiomas (GEE Collection 4)

**Coleta**: `scripts/fogo_mapbiomas.py` (GEE)
**Análise**: `scripts/analise_fogo.py`
**Quando foi feito**: executado em 2026-05-05.
**Depende de**: Earth Engine autenticado, `GEE_PROJECT=extreme-height-447417-a9`.
**Outputs**:
- `data/processed/fogo_mapbiomas_goias.csv` (246 munis × 40 anos = 9.840 linhas, 7 colunas de área queimada)
- `data/cache/fogo/fogo_{ANO}.csv` (cache por ano, idempotente)
- `data/processed/painel_fogo_municipal.csv` (cross-section municipal, queima acumulada)
- 5 PNGs em `outputs/analises/` (24–28)
- Colunas `fogo_*` integradas ao painel unificado (#16)

## Correção aplicada em 2026-05-05

Versão original do `fogo_mapbiomas.py` extraía propriedades erradas dos resultados de `reduceRegions`:
- `Reducer.sum()` em banda única retorna a propriedade `"sum"` — o script buscava `"burned_area_{ano}_sum"` → 0 ha em todos os municípios.
- `Reducer.frequencyHistogram()` retorna a propriedade `"histogram"` — o script buscava `"burned_coverage_{ano}"` → vazio.

Corrigido em `fogo_mapbiomas.py:163-175` antes da execução. Validação: Goiânia 2020 = 1.612 ha (predominantemente pastagem 750 ha + mosaico 729 ha); total estadual 2020 = **410.095 ha** — valor **verificado em 27/jul/2026** contra dois recortes geográficos e três coleções do MapBiomas Fogo (ver abaixo). A antiga ressalva de "~30% abaixo do Fire Dashboard" **não descreve um viés deste pipeline** e foi requalificada.

## ✅ A lacuna de ~30% vs. o dashboard — TESTADA (#14B, 27/jul/2026)

> **Resultado: o número deste pipeline está certo.** Três das quatro hipóteses foram **rejeitadas
> empiricamente**; a quarta sobra por eliminação e não é sobre o nosso cálculo. Script:
> [`verificacao_fogo_nivel.py`](../../scripts/verificacao_fogo_nivel.py).

O registro **original** atribuía a diferença a "sub-amostragem de pixels nas bordas em `scale=30`".
Essa explicação caiu em 25/jul: 30 m é a **resolução nativa** do asset, então o `reduceRegions`
não sub-amostra nada — lê o raster na grade em que ele existe. Em seu lugar ficaram quatro
hipóteses, então **nenhuma testada**. Agora estão:

| # | Hipótese | Veredito | Evidência |
|---|---|---|---|
| 1 | **Recorte de classe** — o total seria a soma do histograma por classe, perdendo pixels fora dos grupos | 🔴 **REFUTADA** (dois caminhos) | (a) a soma das 7 colunas de classe bate com o total em razão **1,000000 nos 40 anos**; (b) `area_queimada_total_ha` **já é** a banda binária pura (`Reducer.sum()` sobre `burned_area_YYYY`) — nunca dependeu do cruzamento com classe |
| 2 | **Objeto diferente** — área anual × cicatriz acumulada, sobreposição no mesmo ano | 🟡 **sobra por eliminação** | não testável daqui (exige saber o que o dashboard conta; sem API pública neste ambiente) |
| 3 | **Recorte geográfico** — malha `geobr` × recorte do dashboard | 🔴 **REJEITADA** | estado dissolvido = 410.066 ha × soma dos 246 municípios = 410.095 ha → **−0,01%** |
| 4 | **Versão do asset** | 🔴 **REJEITADA** | mesmo recorte, mesmo ano, nas três coleções: 2020 → **410.066 / 409.890 / 409.921 ha** (`collection4` / `4_1` / `5`), dispersão **0,04%**; 2010 → 1,8034 / 1,8031 / 1,8031 Mha |

**A hipótese (1) merece uma nota**, porque ela foi escrita neste doc em 25/jul como "a primeira a
testar" e descrevia **um mecanismo que não existe no código**. O total sempre veio da banda
binária; o condicionamento de classe afeta as *colunas por classe*, não o total. Foi um erro de
leitura do próprio pipeline — registrado aqui em vez de apagado, porque o padrão importa: uma
hipótese plausível e bem escrita pode não ter referente no código, e o jeito barato de descobrir
isso é ler a função antes de planejar o teste.

### O que isso muda

O valor de **410.095 ha para 2020 é reprodutível e estável** — sobrevive à troca de recorte
geográfico e à troca de coleção do MapBiomas (três versões independentes, concordância de 0,04%).
Logo **a lacuna, se existe, não está do lado deste cálculo**.

Sobre o "~600k ha do Fire Dashboard": esse número entrou no doc **sem proveniência registrada**
(data da consulta, recorte, métrica). Como (1), (3) e (4) caíram, o que resta é que ele seja
**outro objeto** — outra métrica (cicatriz acumulada, frequência), outro recorte (Cerrado goiano
× Goiás) ou outra leitura. **Não é uma discrepância a explicar do nosso lado; é uma referência a
requalificar.**

**Como citar agora.** O número **pode** ser citado como estimativa de área queimada anual em Goiás
pelo MapBiomas Fogo — com a fonte e a coleção declaradas —, o que a versão anterior deste doc
proibia. O que **não** se deve fazer é repetir a comparação "~30% abaixo do dashboard" como se
fosse um viés conhecido do pipeline: isso nunca foi estabelecido e agora tem três explicações
descartadas.

**Consequência para as análises (inalterada).** Mesmo que houvesse um viés de nível, ele entraria
como constante multiplicativa e seria absorvido pelos efeitos fixos de ano em primeira diferença
(D7/D8) — que é como o fogo é usado no [#41](41_fogo_fronteira.md) (centroide) e no painel.
**Nenhuma conclusão da dissertação depende do nível absoluto de hectares queimados.**

## 🛑 Bug latente corrigido em 25/jul/2026: escala do retry × área do pixel

`processar_ano()` tem um fallback que reduz a resolução quando o GEE falha (`scale` 30 → 60 → 100),
mas a área era convertida por uma constante fixa `PIXEL_HA = 0,09` (a área de um pixel de **30 m**).
Se algum ano tivesse caído no fallback, sua área teria sido **subestimada em 4×** (a 60 m) ou
**~11×** (a 100 m) — silenciosamente, porque o CSV de cache **não registrava a escala usada**.

- **Nenhum número atual está afetado**: `data/cache/fogo/_run.log` não tem nenhum `[retry]`, ou
  seja, os 40 anos rodaram a 30 m. O bug era latente, não realizado.
- **Correção**: a área do pixel agora é derivada da escala efetiva (`(scale²)/10.000`), e o CSV
  ganhou a coluna de proveniência **`scale_m`**. Caches gerados antes desta data não têm a coluna;
  todos são 30 m.
- **Mesmo padrão corrigido em** `transicoes_mapbiomas.py` ([#12](12_transicoes.md)) e
  `piecewise_did.py` ([#23](23_did.md)), que tinham o fallback idêntico com `PIXEL_HA` fixo. No #12
  a validação batimental contra o #4 pegaria um erro de 4×; no #23 **não havia rede** nenhuma.
- **Ressalva que permanece**: mesmo com a área corrigida, um ano rodado a 60/100 m **não é
  comparável em nível** a um rodado a 30 m (a agregação muda o que conta como queimado na borda).
  Se a coluna `scale_m` algum dia sair diferente de 30, o ano deve ser reprocessado, não corrigido
  por fator.

## O que faz

Calcula área queimada anual por município de Goiás cruzada com classe LULC do MapBiomas, usando os assets:

- `.../fire/collection4/mapbiomas_fire_collection4_annual_burned_v1` (40 bandas binárias `burned_area_1985`…`burned_area_2024`)
- `.../fire/collection4/mapbiomas_fire_collection4_annual_burned_coverage_v1` (40 bandas `burned_coverage_1985`…`burned_coverage_2024`)

Para cada município/ano, retorna histograma de hectares queimados por classe de cobertura (Floresta, Cerrado, Campo, Pastagem, Soja, Lavouras, Mosaico).

## Por que importa

Fogo no Cerrado precede ~70% das conversões (LULC). Sem essa camada, o eixo "vetor de ocupação" fica incompleto — fogo é o mecanismo físico pelo qual a pastagem aparece.

ID 21 (Mosaico) é contabilizado separadamente como classe 7 no histograma — captura áreas que MapBiomas não decidiu se é agricultura ou pastagem.

## Gráficos produzidos (5 PNGs, 24–28)

| # | Arquivo | Tipo | Descrição |
|---|---|---|---|
| 24 | `24_fogo_estado_serie.png` | Stacked area | Área queimada anual estadual decomposta por classe (veg natural, pastagem, agricultura, mosaico, outros) — 1985-2024 |
| 25 | `25_fogo_classe_proporcao.png` | Stacked 100% | Composição percentual da queima por classe ao longo do tempo |
| 26 | `26_fogo_top10_municipal.png` | Small multiples 2×5 | Top 10 munis em queima acumulada — série anual |
| 27 | `27_scatter_fogo_transicoes.png` | Scatter | Cruzamento queima acumulada × área convertida (#12), com Pearson |
| 28 | `28_mapa_fogo_acumulado.png` | Coroplético | Queima acumulada 1985-2024 por município (escala log YlOrRd) |

## Como rodar

```bash
# Pré-requisito: GEE autenticado e GEE_PROJECT exportado.
$env:GEE_PROJECT = "extreme-height-447417-a9"
python scripts/fogo_mapbiomas.py     # ~45 min: 40 anos × ~67s/ano
python scripts/analise_fogo.py       # gera painel + 5 gráficos
python scripts/construir_painel_unificado.py  # regenera painel #16 com colunas fogo_*
```
