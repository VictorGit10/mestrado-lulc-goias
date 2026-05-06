# Espacialização — CRS, malha e fluxo de mapas

Decisões transversais sobre projeção, malha municipal e divisão de papéis Python ↔ QGIS.

## Malha base

- **Recomendado**: `geobr.read_municipality(code_muni="GO", year=2020)` — 246 polígonos, IBGE oficial.
- **Chave de junção** com qualquer CSV: `cd_mun` (IBGE 7 dígitos).
- **Por que IBGE 2020 (e não 2022/2024)**: Goiás tem 246 munis hoje, mas em 1985 tinha ~199. Usar 2020 é convenção estável; séries anteriores ficam agregadas via pai-filho de desmembramento se preciso.
- **Bacia vs município**: para análise ambiental, OttoBacias nível 4–5 fragmenta menos. Mas socioeconômica é obrigatoriamente municipal (é onde IBGE/BACEN publicam). Se necessário, gerar duas malhas e juntar via área proporcional.

## CRS — cuidado com o uso

| Uso | CRS | Por quê |
|---|---|---|
| **Cálculo de área** | **EPSG:5880** (SIRGAS Albers Brasil) | Cônica de áreas iguais — única opção honesta para hectares |
| **Mapas finais** | EPSG:4674 (SIRGAS 2000 lat/long) | Default do `geobr`, não distorce visualmente em escala estadual |
| **Análise hidrográfica/regional** | UTM 22S ou 23S | Goiás cobre os dois fusos — cuidado |
| **Web embed (Folium/Leaflet)** | EPSG:3857 (Web Mercator) | Só para isso. Distorce área em ~30% em latitude -16° |

**Não use Web Mercator (EPSG:3857) para análise** — distorce área significativamente nessa latitude.

## Divisão de papéis Python ↔ QGIS

| Etapa | Ferramenta | Por quê |
|---|---|---|
| Exploração rápida (ver se faz sentido) | `geopandas.plot()` + `matplotlib` | Reprodutível, fica no script, zero clique |
| Coropletas municipais "rápidas" para o relatório | **Pipeline #9** (`gerar_mapas_lulc_40anos.py`) | 40 PNGs em ~2 min, derivável do CSV |
| Mapas de uso da terra "tipo MapBiomas" (raster 30m) | **Pipeline #10** (`gerar_mapas_lulc_gee_40anos.py`) | Resolução nativa, qualidade publicável |
| Mapas de capa / figura final da dissertação | **QGIS** | Controle fino de tipografia, layout impresso, legenda composta — pode importar PNGs do #10 ou GPKGs derivados |
| Inspeção interativa (debug de anomalias) | `folium` ou QGIS | Hover, zoom, comparação visual |

## Tipos de mapa — opções

- **Snapshots vs animação**: anos-chave (1985, 1995, 2005, 2015, 2024) num painel de 5 mapas para PDF; GIF para apresentação oral/digital ([Pipeline #11](../pipelines/11_gif_lulc.md)).
- **Coropleto absoluto vs relativo**: pastagem em ha mostra "onde tem"; em % da área municipal mostra "onde domina". Histórias diferentes — vale gerar ambos.
- **Bivariados** (3×3 cor, Joshua Stevens): cruzando pastagem × crédito, ou desmatamento × frigoríficos. Visualmente densos mas didáticos.
- **Hotspot (LISA / Getis-Ord)**: clusters HH/LL de variação de pastagem — fronteiras ativas vs estabilizadas. Pendente.
- **Mapa de fluxo**: setas A→B sobre matriz de transição (origem-destino dentro de Goiás). Usar saídas do [Pipeline #12](../pipelines/12_transicoes.md).

## Estética e legibilidade

- **Classes**: Jenks natural breaks para distribuições enviesadas (pastagem); quantis (5 classes) para comparação entre mapas.
- **Paleta**: divergente (RdYlBu) para variações; sequencial (YlOrBr) para estoques. ColorBrewer cobre daltonismo.
- **Camadas-base**: contorno limpo basta; relevo SRTM polui em escala estadual.
- **Small multiples**: 4–5 painéis com legenda compartilhada — padrão-ouro para tese.

## Infraestrutura técnica

- **Formato vetor**: GeoPackage (`.gpkg`) sempre. Shapefile trunca nomes em 10 chars e perde Unicode.
- **PostGIS**: útil se passar de 5GB de raster ou para SQL espacial. Para dissertação solo, geopandas+gpkg basta.
- **GEE**: account próprio para transições customizadas e fogo×LULC. Assets públicos pré-computados são mais rápidos quando suficientes.

## Pendente

**Refator `mapas.py`** — módulo com helpers reutilizáveis (carregar malha, plotar coropleta com legenda padronizada, exportar GPKG para QGIS). Vale fazer antes de duplicar código entre próximos coropléticos temáticos. Ver [backlog](../backlog.md).
