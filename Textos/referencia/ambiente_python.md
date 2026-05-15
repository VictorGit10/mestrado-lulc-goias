# Ambiente Python — pegadinhas conhecidas

**Versão**: Python 3.14. `requirements.txt` na raiz do projeto cobre todas as dependências (core, plotting, geoespacial, GEE, estatística/econometria, APIs IBGE/IPEA, e pysal stack para Pipeline #24). Instalação: `pip install -r requirements.txt`.

## Gotchas geoespaciais (Win+Py 3.14)

- `geobr` declara `shapely<=2.1.0` e `lxml<6.0.0` em metadados, mas Python 3.14 não tem wheel pré-compilada para essas versões antigas. Versões mais novas (`shapely 2.1.2`, `lxml 6.1.0`) funcionam — os limites do `geobr` são conservadores.

### Sequência de instalação que funciona

```bash
pip install --only-binary=:all: shapely
pip install --only-binary=:all: geopandas pyogrio pyproj
pip install --only-binary=:all: lxml html5lib
pip install --no-deps geobr
pip install matplotlib-scalebar
```

### Warnings benignos

- `matplotlib_scalebar.ScaleBar` em CRS geográfico (EPSG:4326/4674) emite warning "unequal aspect ratio". Não afeta a imagem; suprimir com `ax.set_aspect("equal")` se incomodar.
- Aproximação `dx=111000` (metros por grau de latitude) na ScaleBar é aceitável para Goiás (latitudes -19° a -12°, erro <2%).
- `geobr.read_municipality()` baixa shapefile na primeira execução (~MB) e cacheia local.

## Earth Engine (Pipeline #10)

- Instalar com `pip install --only-binary=:all: earthengine-api`.
- Autenticação: `earthengine authenticate` num **terminal Windows real** (não funciona dentro do Bash do Claude Code — exige interação browser + paste).
- Cada projeto Cloud precisa ser registrado em https://code.earthengine.google.com/register como Noncommercial/Academic para uso gratuito.
- Variável de ambiente `GEE_PROJECT` define qual projeto usar.