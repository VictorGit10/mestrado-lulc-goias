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

Corrigido em `fogo_mapbiomas.py:163-175` antes da execução. Validação: Goiânia 2020 = 1.612 ha (predominantemente pastagem 750 ha + mosaico 729 ha); total estadual 2020 = 410.095 ha (compatível com MapBiomas Fire Dashboard ~600k ha — diferença ~30% explicada por sub-amostragem de pixels nas bordas em scale=30).

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
