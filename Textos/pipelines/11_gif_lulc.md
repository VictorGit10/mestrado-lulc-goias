# Pipeline #11 — GIF animado LULC

**Script**: `scripts/gerar_gif_lulc.py` (estado) + `scripts/gerar_gif_lulc_rio_verde.py` (Rio Verde)
**Depende de**: Pipeline #10 (consome os PNGs em `outputs/mapas_gee/`).
**Outputs**: `outputs/mapas_gee/cobertura_1985_2024.gif` (~13 MB).

## O que faz

Compila os 40 PNGs do Pipeline #10 (1985–2024) em GIF animado a ~2 fps (500ms/frame). Permite visualizar a evolução temporal da cobertura do solo em movimento — a expansão da pastagem e agricultura sobre a vegetação natural fica evidente.

## Como rodar

```bash
python scripts/gerar_gif_lulc.py
# variante para Rio Verde:
python scripts/gerar_gif_lulc_rio_verde.py
```

(após Pipeline #10).

## Saída

- `outputs/mapas_gee/cobertura_1985_2024.gif` (~13 MB)
- variantes Rio Verde em `outputs/mapas_gee_rio_verde/`

## Limitações

GIF é grande para colar em PDF — útil para apresentação oral/web, não para impressão. Para versão impressa, preferir small multiples de 4–5 anos-chave (1985, 1995, 2005, 2015, 2024).
