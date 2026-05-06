# Prompt para continuar a dissertação em nova sessão do Claude Code

---

Estou trabalhando na dissertação de mestrado sobre dinâmica de uso e cobertura da terra em Goiás (1985–2024) e sua relação com fatores socioeconômicos. O diretório de trabalho é `C:\Users\amara\OneDrive\Documentos\Antigravity\Mestrado`.

## O que já está pronto

16 pipelines foram concluídos. Os dados processados estão em `data/processed/` (40+ CSVs + 1 parquet) e as visualizações em `outputs/` (139 imagens). O painel unificado (`painel_unificado.parquet`, 9.840×66) consolida LULC + pecuária + lavouras + PIB + população + SICOR + Censo 2017 + IDH-M.

**Pipelines concluídos**:
- #1–#8: coleta SIDRA/SICOR + análises descritivas (18 PNGs)
- #9–#11: cartografia (40 coropletas + 40 rasters GEE + 2 GIFs)
- #12: matrizes de transição pixel-a-pixel via GEE (6 classes, 9 pares)
- #13: IDH-M via IPEA Data API (1991/2000/2010, 246 munis, integrado ao painel)
- #15: milho 1ª e 2ª safra (SIDRA 839, 2003–2024)
- #16: painel unificado wide (9.840×66, parquet + CSV)

**Pipelines com script pronto, não executados**:
- #14: fogo MapBiomas (GEE Collection 4) — requer autenticação GEE

## Arquivos essenciais para ler

1. **`Textos/DOCUMENTACAO.md`** — Documentação completa do projeto (estrutura, pipelines, decisões metodológicas, backlog). Comece por aqui.
2. **`Textos/CATALOGO_OUTPUTS.md`** — Catálogo detalhado de cada gráfico e CSV produzido.
3. **`Textos/ResumoDoBrainStorm.ini`** — Plano-mestre da dissertação (4 eixos de pesquisa).
4. **`Textos/SugestaoClaude.md`** — Lista de fontes de dados adicionais e decisões de espacialização.

## Backlog (prioridade sugerida)

1. **Análise espacial estatística** (Moran's I, LISA, spreg) — núcleo analítico faltante; painel unificado destrava
2. **Pipeline #14 (fogo)** — script pronto, rodar com GEE
3. **IDH-M 2021** — download manual do Atlas Brasil, integrar ao painel
4. **Análise descritiva da safrinha** (#15) — dados coletados, sem gráficos
5. **Infraestrutura agroindustrial** (SIGSIF, CONAB, DNIT) — coleta do zero
6. **Reprodutibilidade** — requirements.txt/pyproject.toml

## O que eu quero fazer agora

[TAREFA ESPECÍFICA AQUI — ex.: "Implementar análise espacial com Moran's I e LISA" ou "Rodar Pipeline #14 de fogo no GEE"]

## Preferências

- Comunicação em português (pt-BR)
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy)
- QGIS para layout cartográfico final
- Valores monetários deflacionados via IPCA (dez/2024)
- Malha municipal IBGE 2020, CRS área = EPSG:5880