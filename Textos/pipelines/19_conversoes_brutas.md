# Pipeline #19 — Agregação de transições consecutivas

**Script**: `scripts/agregar_conversoes.py`
**Depende de**: `data/cache/transicoes/transicao_YYYY_YYYY.csv` (39 pares consecutivos + 9 pares longos, gerados por Pipeline #12 com flag `--consecutivos`)
**Status**: ✅ executado
**Outputs**: `data/processed/conversao_bruta_goias.csv`, `conversao_bruta_municipal.csv`

## O que faz

Lê os 39 CSVs de cache de transições pixel-a-pixel consecutivas (1985→1986, 1986→1987, ..., 2023→2024) e agrega em dois níveis:

1. **UF**: fluxo entre 6 classes LULC por par de anos consecutivos (156 linhas)
2. **Municipal**: fluxo por município (35.250 linhas)

O mapeamento de classes segue D1 (mesmo de Pipeline #17 e #10).

## Pré-requisito

Antes de rodar, executar:

```bash
set GEE_PROJECT=extreme-height-447417-a9
python scripts/transicoes_mapbiomas.py --consecutivos
```

Isso gera 39 arquivos de cache em `data/cache/transicoes/`. Tempo estimado: ~40 min com GEE autenticado.

## Como rodar (após GEE)

```bash
python scripts/agregar_conversoes.py
```

## Validação

- Soma da diagonal + off-diagonal por ano ≈ área total de Goiás (~34 Mha)
- Fluxo líquido (diagonal - total_origem) ≈ delta do Pipeline #17
- GEE reporta ~6.000-6.250 transições (6×6 classes × 246 munis) por par de anos

## Colunas

**UF** (`conversao_bruta_goias.csv`):
- `ano_origem`, `ano_destino`, `grupo_orig`, `grupo_dest`, `area_ha`, `area_mha`

**Municipal** (`conversao_bruta_municipal.csv`):
- `cd_mun`, `nm_mun`, `ano_origem`, `ano_destino`, `grupo_orig`, `grupo_dest`, `area_ha`, `area_mha`

## Validação batimental

O script GEE compara áreas agregadas contra o Pipeline #4 (MapBiomas municipal). Divergências de 1-13% são esperadas (GEE usa pixels de 30m; Pipeline #4 usa estatísticas tabulares). Pastagem tende a divergir mais (-3 a -13%) por causa da classe Mosaico (excluída do GEE, incluída nas estatísticas).