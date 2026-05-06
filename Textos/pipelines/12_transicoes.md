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
