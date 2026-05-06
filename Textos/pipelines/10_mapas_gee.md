# Pipeline #10 — 40 mapas raster MapBiomas via GEE

**Script**: `scripts/gerar_mapas_lulc_gee_40anos.py`
**Quando foi feito**: 2026-04-28.
**Depende de**: Earth Engine autenticado.
**Outputs**: 40 PNGs em `outputs/mapas_gee/cobertura_{1985..2024}.png` + 40 raws em `outputs/mapas_gee/_raw/`. Ver [mapas_lulc.md](../outputs/mapas_lulc.md).

## O que faz

Conecta ao Google Earth Engine, baixa o raster oficial do MapBiomas Coleção 10.1 (asset `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`), recorta pelo polígono de Goiás (via `geobr.read_state`) e gera 40 PNGs em **resolução nativa 30m** (downsampled para 2048px de largura no thumbnail).

Mesmo conjunto de **8 classes agregadas** do Pipeline #9 — paleta consistente entre coroplético e raster, facilita comparação visual entre as duas representações.

## Pipeline interno por ano

1. `ee.Image(ASSET).select(f'classification_{ano}')` — banda do ano
2. `.clip(geom_GO)` — recorte
3. `.remap(from_ids, to_ids, 0)` + `.selfMask()` — agrega 22→8 classes, mascara o que não interessa
4. `getThumbURL({'dimensions': 2048, 'palette': [...8 cores], 'min': 1, 'max': 8})` — gera URL do PNG
5. `requests.get()` baixa raw em `outputs/mapas_gee/_raw/raw_{ANO}.png`
6. matplotlib compõe título + legenda + scalebar sobre o raw → `outputs/mapas_gee/cobertura_{ANO}.png`

## Como rodar

```bash
# Pré-requisito 1 — autenticar (uma vez):
earthengine authenticate    # abre browser, fluxo OAuth do Google

# Pré-requisito 2 — definir projeto Google Cloud (uma vez):
set GEE_PROJECT=extreme-height-447417-a9     # Windows cmd
$env:GEE_PROJECT="extreme-height-447417-a9"  # PowerShell
export GEE_PROJECT=extreme-height-447417-a9   # bash

# Rodar:
python "scripts/gerar_mapas_lulc_gee_40anos.py"
```

**Pré-requisitos**: `pip install earthengine-api geopandas geobr matplotlib matplotlib-scalebar pillow requests`. Ver [referencia/ambiente_python.md](../referencia/ambiente_python.md) para gotchas.

## Saída

40 PNGs em `outputs/mapas_gee/` (~3-4 MB cada, ~137 MB total) + 40 raws em `outputs/mapas_gee/_raw/`.

**Tempo de execução**: ~35 min (dominado por `getThumbURL` — ~50s/ano).

## Decisões metodológicas

- **Coleção 10.1** (não 10.0 nem 9). Rationale: Coleção 10 lançada em 2024, 10.1 é a revisão consolidada (correções de Cerrado/Caatinga). Cobertura 1985–2024.
- **Tier noncommercial GEE**. Projeto Cloud `extreme-height-447417-a9` precisa ser registrado em https://code.earthengine.google.com/register como "Noncommercial or Academic" — uso acadêmico é gratuito; sem registro, o tier comercial cobra (consumo deste pipeline é trivial mas registrar é obrigatório por política).
- **Geometria de Goiás vem do `geobr`**, não do `FAO/GAUL` no GEE. Razão: contornos IBGE oficiais > generalizados internacionais, e mantém consistência com Pipeline #9.
- **Aproximação da escala**: o thumbnail é gerado em EPSG:4326 (graus); `metros_por_pixel` calculado pela bbox em EPSG:5880 dá uma boa aproximação para Goiás (latitudes -19° a -12°). Erro <2% nos extremos.
- **selfMask** (vs `updateMask(neq(0))`): mascara pixels com valor 0 do remap → áreas residuais (silvicultura, mosaico, mineração, etc.) ficam transparentes ao invés de pretas.

## Validação visual

- 1985: domínio de cerrado (verde médio) e floresta (verde escuro), pastagem já estabelecida no centro-sul, lavouras residuais no sudoeste — confere com história agrária de GO.
- 2024: pastagem dominante em todo o estado, mancha de soja explodida no sudoeste/oeste, cerrado preservado concentrado no nordeste (entorno Chapada dos Veadeiros) e norte de GO — confere com MapBiomas oficial.
- Buraco branco no leste = Distrito Federal (corretamente fora do polígono GO).

## Quando usar #9 vs #10

| Caso | Pipeline | Por quê |
|---|---|---|
| Slide de apresentação rápido | #9 | Carrega rápido, narrativa "uma cor = um município" é simples |
| Figura final da dissertação | **#10** | Resolução 30m, vê textura interna, qualidade tipo plataforma MapBiomas |
| Animação GIF/MP4 da série | #10 (preferido) | A textura raster torna a transição visualmente impactante |
| Análise quantitativa de áreas | nem um nem outro | Use diretamente `mapbiomas_munis_goias.csv` (Pipeline #4) |
