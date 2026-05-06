# Backlog

Itens pendentes alinhados com o plano-mestre e [fontes_dados_adicionais.md](referencia/fontes_dados_adicionais.md).

## Já feito

- [x] Pipeline #1 — Pastagem × PIB UF (2 PNGs)
- [x] Pipeline #2 — Análise expandida UF (4 PNGs)
- [x] Pipeline #3 — Coleta SIDRA municipal (8 tabelas)
- [x] Pipeline #4 — MapBiomas municipal Goiás (8.6 MB CSV)
- [x] Pipeline #5 — Análise pastagem ↔ soja municipal (7 CSVs + 5 PNGs)
- [x] Pipeline #6 — Coleta SICOR/BACEN crédito rural 2013–2026 (5 CSVs)
- [x] Pipeline #7 — Censo Agropecuário 2017 (7 tabelas + painel 246×44)
- [x] Pipeline #8 — Crédito rural × LULC (3 CSVs + 7 PNGs)
- [x] Pipeline #9 — 40 mapas coropléticos municipais
- [x] Pipeline #10 — 40 mapas raster MapBiomas via GEE
- [x] Pipeline #11 — GIF animado LULC
- [x] Pipeline #12 — Matrizes de transição pixel-a-pixel via GEE
- [x] Pipeline #13 — IDH-M via IPEA Data API (1991/2000/2010)
- [x] Pipeline #14 — Fogo MapBiomas Collection 4 via GEE (CSV + 5 PNGs)
- [x] Pipeline #15 — Milho 1ª e 2ª safra (SIDRA 839, com análise descritiva)
- [x] Pipeline #16 — Painel unificado (9.840×66, parquet + CSV) com slot fogo populado

## Próximos (prioridade sugerida)

| # | Item | Fonte | O que adiciona |
|---|---|---|---|
| 1 | **Análise espacial estatística** | painel_unificado.parquet | Moran's I, LISA, regressão espacial (spreg) — núcleo analítico faltante |
| 2 | **IDH-M 2021** | Atlas Brasil PNUD | Download manual, integrar ao painel |
| 3 | **Infraestrutura agroindustrial** | SIGSIF, CONAB, DNIT | Frigoríficos, silos, malha viária — coleta do zero |
| 4 | **Reprodutibilidade** | — | requirements.txt / pyproject.toml |

## Eixos ainda não atacados

| Item | Fonte | O que adiciona |
|---|---|---|
| Frigoríficos federais | SIGSIF/MAPA | Pontos para análise de proximidade |
| Frigoríficos estaduais | Agrodefesa-GO | Complementa SIGSIF |
| Silos e armazéns | CONAB SISDEP | Capacidade estática por município |
| Malha viária | DNIT/SNV | Acessibilidade rodoviária |
| População rural/urbana | SIDRA 200 | Esvaziamento rural decenal |
| PRODES Cerrado | INPE/TerraBrasilis | Desmatamento anual |
| TerraClass Cerrado | INPE/Embrapa | Pastagem íntegra vs degradada |
| CAR/SICAR | sicar.gov.br | Limites prediais + reserva legal |
| Precipitação | Xavier/ERA5 | Controle climático para regressões |

## Decisões de espacialização pendentes

- Malha de referência: **IBGE 2020** (recomendado, default).
- CRS para cálculo de área: **EPSG:5880 SIRGAS Albers** (Brasil).
- Pacote de malha: `geobr`.
- Mapas finais: pipeline gera GPKG/CSV, QGIS faz layout cartográfico.