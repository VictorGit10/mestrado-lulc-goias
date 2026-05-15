# Backlog

Itens pendentes alinhados com o plano-mestre e [fontes_dados_adicionais.md](referencia/fontes_dados_adicionais.md).

## Já feito

- [x] Pipeline #1 — Pastagem × PIB UF (2 PNGs)
- [x] Pipeline #2 — Análise expandida UF (4 PNGs)
- [x] Pipeline #3 — Coleta SIDRA municipal (11 tabelas: PAM 1612 expandida 33 produtos, PAM 1613 expandida 38 produtos, PPM 95, PPM 74 mel/lã)
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
- [x] Pipeline #16 — Painel unificado (9.840×~200, parquet + CSV) com todas as lavouras, permanentes, mel, lã e ovinos tosquiados
- [x] Pipeline #17 — Taxas de variação LULC (delta, slope 5a, SE Newey-West, aceleração) — UF, municípios, mesorregiões
- [x] Pipeline #18 — Mapeamento de mesorregiões IBGE 2017 (246 munis → 5 mesos)
- [x] Pipeline #19 — Transições brutas ano-a-ano (39 pares via GEE + agregação UF/municipal)
- [x] Pipeline #20 — Figuras de taxas (7 PNGs: slope, mesorregiões, delta, mapas, aceleração)
- [x] Pipeline #21 — Correlações UF Δ-vs-Δ (36 pares, 6 scatter plots)
- [x] Pipeline #22 — Painel municipal 2-way FE (16 modelos, 6 significativos)
- [x] Pipeline #23 — DiD GO vs MT/TO (36 modelos, 9 significativos)
- [x] Fix `agregar_conversoes.py` (2026-05-12) — caches GEE têm IDs agrupados 1–6, não MapBiomas brutos. CSV agora exporta 6×6 = 36 transições por ano-par (era 2×2), 39 pares validados em ±15% de 34 Mha.
- [x] Pipeline #26 — Detecção de quebras estruturais (binary segmentation + Quandt-Andrews) GO+TO (2026-05-13). 15 quebras em 6 séries. **Código Florestal 2012 sem quebra empírica em GO ou TO; Cerrado Manifesto 2018 é cerrado-amplo, não GO-específico; inflexão de veg. natural em GO é 1998 (Lei Kandir), não 1994 (Real).**
- [x] Renomeação "PAC Cerrado" → "Cerrado Manifesto" + rebaixamento dos achados DiD 2012/2018 (2026-05-13) — PAC Cerrado era label de rascunho sem programa real correspondente. Efeitos DiD 2012/2018 não replicam vs TO; texto e dados de choque do `index.html`/`marcos.json` atualizados; figuras DiD regeneradas.
- [x] **PIB e VAB agro UF nativos IPEA (1985-2023)** (2026-05-14) — novo `scripts/coleta_pib_uf_ipea.py` baixa séries `PIBE` e `PIBAGE` do IPEA Data, reescala 2010→dez/2024 via IPCA, gera `data/processed/pib_uf_ipea_goias.csv`. Pipeline #21 (`correlacoes_uf.py`) passa a usar essa série em vez do agregado municipal SIDRA — **N por par com PIB/VA agro sobe de ~21 para ~37**, novo par significativo (Δveg.natural × ΔPIB lag=1: r=+0,32, p=0,046). Site (`painel_goias.json` + acordeão socioeconômico) mostra as duas séries lado a lado. Comparação e quebra metodológica documentadas em `validacao_cruzada.md`.
- [x] **Robustez DiD: event-study + placebo + hierarquia TO** (2026-05-14) — `piecewise_did.py` ganhou `rodar_event_study()` e `rodar_placebo()`. Resultados em `event_study_resultados.csv` (132 linhas) + 12 figuras + `placebo_resultados.csv` (36 placebos). **Achado consolidado**: apenas Veg.natural × 1995 vs TO sobrevive ao conjunto parallel-trends + placebo + DiD sig. Demais efeitos pós-2012/2018 vs MT/combined têm placebos significativos (dinâmica pré-existente, não causal). Veja `23_did.md`.
- [x] **Robustez painel multivariada** (2026-05-14) — `correlacoes_painel.py` ganhou `rodar_painel_multivariado()`. 9 modelos multivariados em `painel_multivariada.csv`. **Achado**: SICOR é canal dominante de retração de pastagem (β=−0,003, p<0,001 com VA agro+Bovinos+Fogo no modelo); VA agro perde sig. Intensificação Δ Agricultura × Δ VA agro sobrevive em todas variantes (com/sem SICOR, ambas janelas). R²w salta de 0,047→0,122 em agricultura. VIFs ≤ 1,55.
- [x] **Pipeline #24 — análise espacial estatística** (2026-05-14) — novo `scripts/analise_espacial.py` com Moran's I global, LISA e regressão espacial (OLS/SAR/SEM via `spreg`). **115 de 140 resíduos (modelo × ano × W) têm I sig** — autocorrelação espacial é estrutural. Pico em 2018 (I=+0,53 para pastagem × bovinos). spreg cross-section 2020 mostra SEM com pequena vantagem sobre OLS (λ=+0,06–0,08). 8 mapas LISA gerados. `requirements.txt` ganha pysal stack.

## Em andamento (sequência atual A→B→C, 2026-05-12)

- [x] **Frente A** — Fix conversao_bruta_*.csv (concluído)
- [ ] **Frente B** — Pipeline #25: `scripts/analise_transicoes.py` (matrizes 6×6 por ATO, decomposição de origem, fluxo bruto vs líquido, 5 JSONs Sankey, top por mesorregião)
- [ ] **Frente C** — Refinar primeira aba do `Visualizacao/index.html`:
  - C1: cards diversificados de produção (mini-grid 4 culturas por ATO, explora painel ampliado)
  - C2: toggle de camadas no sticky-map (Cobertura | Δ | Fogo | Transições)
  - C3: pull-quotes nos marcos 1994/1996/2003/2012/2018
  - C4: mini-sankey ao fim de cada ato (consome JSONs da Frente B)
  - C5: highlight barra empilhada ↔ pixels do mapa

## Próximos (prioridade sugerida)

| # | Item | Fonte | O que adiciona |
|---|---|---|---|
| 1 | **Frente C** (visualização) | `Visualizacao/` | C1 cards de produção, C3 pull-quotes, C4 mini-sankey containers HTML, C5 highlight barra↔mapa. Componentes para apresentação. |
| 2 | **Investigar quebras data-driven sem marco** | quebras_resultados.csv | 1991 (pastagem GO+TO), 1999 (agric TO), 2006 (veg_nat TO). Hipóteses: Plano Collor 1990, câmbio flutuante 1999, Moratória Soja Amazônia 2006. Validar via literatura |
| 3 | **Painel espacial dinâmico** | `analise_espacial.py` | Estender Pipeline #24 com `spreg.Panel_FE_Lag` cobrindo todas as janelas (não só 2020). Pipeline #24 já mostrou que I varia ao longo do tempo |
| 4 | **IDH-M 2021** | Atlas Brasil PNUD | Download manual, integrar ao painel |
| 5 | **Infraestrutura agroindustrial** | SIGSIF, CONAB, DNIT | Frigoríficos, silos, malha viária — coleta do zero |
| 6 | **Reprodutibilidade pyproject.toml** | requirements.txt já existe | pyproject.toml para empacotamento moderno + lock file |

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