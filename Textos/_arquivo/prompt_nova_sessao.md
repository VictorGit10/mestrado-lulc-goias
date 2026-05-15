# Prompt para continuar a dissertação em nova sessão do Claude Code

---

Estou trabalhando na dissertação de mestrado sobre dinâmica de uso e cobertura da terra em Goiás (1985–2024) e sua relação com fatores socioeconômicos. O diretório de trabalho é `C:\Users\amara\OneDrive\Documentos\Antigravity\Mestrado`.

## O que já está pronto

26 pipelines foram concluídos. Os dados processados estão em `data/processed/` (~65 CSVs + 1 parquet) e as visualizações em `outputs/` (139+ imagens). O painel unificado (`painel_unificado.parquet`, 9.840×66) consolida LULC + pecuária + lavouras + PIB + população + SICOR + Censo 2017 + IDH-M + fogo + taxas de variação + mesorregiões.

**Pipelines concluídos**:
- #1–#8: coleta SIDRA/SICOR + análises descritivas (18 PNGs)
- #9–#11: cartografia (40 coropletas + 40 rasters GEE + 2 GIFs)
- #12: matrizes de transição pixel-a-pixel via GEE (6 classes, 39 pares)
- #13: IDH-M via IPEA Data API (1991/2000/2010, 246 munis)
- #14: fogo MapBiomas Collection 4 via GEE (CSV + 5 PNGs)
- #15: milho 1ª e 2ª safra (SIDRA 839, 2003–2024)
- #16: painel unificado (9.840×66, parquet + CSV)
- #17: taxas de variação LULC (delta, slope 5a, SE Newey-West, aceleração)
- #18: mapeamento de mesorregiões IBGE 2017
- #19: transições brutas ano-a-ano (39 pares via GEE + agregação)
- #20: figuras de taxas (7 PNGs)
- #21: correlações UF Δ-vs-Δ (36 pares, 6 scatter plots)
- #22: painel municipal 2-way FE (16 modelos, 6 significativos)
- #23: DiD piecewise GO vs MT/TO (36 modelos, 9 significativos)
- #26: detecção de quebras estruturais (sup-F + binary segmentation)

**Em andamento**: Pipeline #25 (análise de transições 6×6 por ATO, decomposição, Sankey).

**Visualização interativa**: Site scrollytelling com Narrativa + Atlas + Sankey (`Visualizacao/`).

## Arquivos essenciais para ler

1. **`Textos/README.md`** — Índice mestre da documentação.
2. **`Textos/visao_geral/escopo_dissertacao.md`** — Escopo, eixos e hipóteses.
3. **`Textos/visao_geral/estrutura_diretorios.md`** — Estrutura completa e atualizada do projeto.
4. **`Textos/backlog.md`** — Status dos pipelines e próximos passos.
5. **`Textos/metodologia/glossario_metricas.md`** — Definições de todas as métricas calculadas.
6. **`Textos/pipelines/README.md`** — Índice dos 23+ pipelines documentados.
7. **`Textos/referencia/ambiente_python.md`** — Setup do ambiente Python e dependências.
8. **`requirements.txt`** — Dependências Python (raiz do projeto).

## Backlog (prioridade sugerida)

1. **Escrita da dissertação** — infraestrutura empírica completa, falta prosa acadêmica
2. **Pipeline #24 — Análise espacial estatística** (Moran's I, LISA, spreg)
3. **Robustez DiD** — event-study plot, placebo pré-marco
4. **Correção para testes múltiplos** nas quebras estruturais
5. **IDH-M 2021** — download manual do Atlas Brasil, integrar ao painel
6. **Infraestrutura agroindustrial** (SIGSIF, CONAB, DNIT) — coleta do zero

## O que eu quero fazer agora

[TAREFA ESPECÍFICA AQUI — ex.: "Implementar análise espacial com Moran's I e LISA" ou "Escrever seção de metodologia"]

## Preferências

- Comunicação em português (pt-BR)
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy)
- QGIS para layout cartográfico final
- Valores monetários deflacionados via IPCA (dez/2024)
- Malha municipal IBGE 2020, CRS área = EPSG:5880
- geobr instalado com `pip install --no-deps geobr`