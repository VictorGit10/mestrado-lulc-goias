# Como retomar o trabalho

Checklist para continuar a dissertação em qualquer sessão do Claude Code.

## 1. Ler a documentação

1. [README.md](../README.md) — índice mestre.
2. [escopo_dissertacao.md](escopo_dissertacao.md) — eixos e hipóteses.
3. [backlog.md](../backlog.md) — o que falta fazer.
4. [estrutura_diretorios.md](estrutura_diretorios.md) — estrutura atualizada do projeto.

## 2. Inspecionar dados

```bash
ls data/processed/    # CSVs e parquets prontos (~65 arquivos)
ls outputs/            # PNGs, mapas, diagnósticos
ls data/cache/         # Cache de requisições (sidra, sicor, gee)
```

O painel unificado (`painel_unificado.parquet`, 9.840×66) consolida LULC + pecuária + lavouras + PIB + população + SICOR + Censo 2017 + IDH-M + fogo + taxas de variação + mesorregiões.

## 3. Pipelines concluídos (26)

| # | Pipeline | Status |
|---|---|---|
| 1–8 | Coleta SIDRA/SICOR + análises descritivas | ✅ |
| 9–11 | Cartografia (40 coropletas + 40 rasters GEE + 2 GIFs) | ✅ |
| 12 | Matrizes de transição pixel-a-pixel via GEE (6 classes) | ✅ |
| 13 | IDH-M via IPEA Data API (1991/2000/2010) | ✅ |
| 14 | Fogo MapBiomas Collection 4 via GEE | ✅ |
| 15 | Milho 1ª e 2ª safra (SIDRA 839) | ✅ |
| 16 | Painel unificado (9.840×66, parquet + CSV) | ✅ |
| 17 | Taxas de variação LULC (delta, slope, SE, aceleração) | ✅ |
| 18 | Mapeamento de mesorregiões IBGE 2017 | ✅ |
| 19 | Conversões brutas ano-a-ano (39 pares) | ✅ |
| 20 | Figuras de taxas (7 PNGs) | ✅ |
| 21 | Correlações UF Δ-vs-Δ (36 pares) | ✅ |
| 22 | Painel municipal 2-way FE (16 modelos) | ✅ |
| 23 | DiD piecewise GO vs MT/TO (36 modelos) | ✅ |
| 26 | Detecção de quebras estruturais (sup-F + binary segmentation) | ✅ |

**Em andamento**: Pipeline #25 (análise de transições 6×6 por ATO, decomposição, Sankey).

## 4. Decidir o próximo bloco

Ver [backlog.md](../backlog.md). Prioridades sugeridas:

1. **Escrita da dissertação** — infraestrutura empírica completa, falta prosa acadêmica.
2. **Pipeline #24 — Análise espacial estatística** (Moran's I, LISA, spreg) — núcleo analítico faltante; painel unificado destrava.
3. **Robustez DiD** — Event-study plot (β por ano relativo), placebo pré-marco.
4. **Correção para testes múltiplos** nas quebras estruturais (Bonferroni/BH-FDR).
5. **IDH-M 2021** — download manual do Atlas Brasil, integrar ao painel.
6. **Infraestrutura agroindustrial** (SIGSIF, CONAB, DNIT) — coleta do zero.

## 5. Preferências

- Comunicação em português (pt-BR).
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy).
- QGIS para layout cartográfico final.
- Valores monetários deflacionados via IPCA (dez/2024).
- Malha municipal IBGE 2020, CRS área = EPSG:5880.

## 6. Reprodutibilidade

- `requirements.txt` na raiz do projeto lista todas as dependências Python.
- Todos os scripts são idempotentes (cache CSV). Apagar `data/raw/` força re-download; apagar `data/processed/` força re-processamento.
- Para `geobr`: instalar com `pip install --no-deps geobr` (conflitos de versão com shapely e lxml).
- Para GEE: autenticação via browser (`ee.Authenticate()`) e registro de projeto noncommercial.