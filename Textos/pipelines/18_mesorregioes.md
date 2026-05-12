# Pipeline #18 — Mapeamento de mesorregiões

**Script**: `scripts/mapeamento_mesorregioes.py`
**Depende de**: `geobr`
**Outputs**: `data/processed/mapeamento_mesorregioes.csv`

## O que faz

Baixa a malha de mesorregiões IBGE 2017 para Goiás via `geobr.read_meso_region()` e faz spatial join com os 246 municípios (malha 2020), atribuindo cada `cd_mun` a uma mesorregião.

## Decisão D6 — Mesorregiões IBGE 2017

Usa `geobr.read_meso_region(code_meso="GO", year=2017)` → 5 mesorregiões:

| cod_meso | nm_meso | Municípios |
|----------|---------|------------|
| 5201 | Noroeste Goiano | 23 |
| 5202 | Norte Goiano | 27 |
| 5203 | Centro Goiano | 82 |
| 5204 | Leste Goiano | 32 |
| 5205 | Sul Goiano | 82 |

Não usa Regiões Geográficas Imediatas (133 unidades em GO) — pulverizaria o painel.

## Spatial join

Usa centroides (projetados em EPSG:5880) para evitar problemas de polígonos sobrepostos em fronteiras. Resultado: 100% dos municípios mapeados.

## Como rodar

```bash
python scripts/mapeamento_mesorregioes.py
```

Requer `geobr` e `geopandas`.