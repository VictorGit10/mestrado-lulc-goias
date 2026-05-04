# Prompt para continuar a dissertação em nova sessão do Claude Code

---

Estou trabalhando na dissertação de mestrado sobre dinâmica de uso e cobertura da terra em Goiás (1985–2024) e sua relação com fatores socioeconômicos. O diretório de trabalho é `C:\Users\amara\OneDrive\Documentos\Antigravity\Mestrado`.

## O que já está pronto

8 pipelines foram concluídos. Os dados processados estão em `data/processed/` (37 CSVs) e os gráficos em `outputs/` (18 PNGs). A documentação completa está em `DOCUMENTACAO.md`.

## Arquivos essenciais para ler

1. **`DOCUMENTACAO.md`** — Documentação completa do projeto (estrutura, pipelines, decisões metodológicas, backlog). Comece por aqui.
2. **`Scripts e Catalogo/CATALOGO_OUTPUTS.md`** — Catálogo detalhado de cada gráfico e CSV produzido.
3. **`ResumoDoBrainStorm.ini`** — Plano-mestre da dissertação (escrito por mim).
4. **`Histórico/SugestaoClaude.md`** — Lista de fontes de dados adicionais e decisões de espacialização.

## Arquivos NÃO precisam ser lidos na íntegra

- Os 37 CSVs em `data/processed/` — estão documentados no CATALOGO_OUTPUTS.md
- Os scripts em `Scripts e Catalogo/` — estão documentados no DOCUMENTACAO.md
- Os JSONs em `data/raw/sicor/` — dados brutos em cache
- Os CSVs em `data/raw/sidra/` — dados brutos em cache
- `data/raw/mapbiomas_col10_estado.xlsx` — 78MB, não abrir

## Backlog (prioridade sugerida)

1. Matrizes de transição A→B via GEE (coração da dissertação)
2. IDH-M (PNUD Atlas)
3. Fogo MapBiomas (GEE)
4. Infraestrutura (frigoríficos, silos, malha viária)
5. Precipitação (Xavier/ERA5)

## O que eu quero fazer agora

[TAREFA ESPECÍFICA AQUI — ex.: "Implementar a coleta de dados de IDH-M do PNUD Atlas" ou "Criar o pipeline de matrizes de transição no GEE"]

## Preferências

- Comunicação em português (pt-BR)
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy)
- QGIS para layout cartográfico final
- Valores monetários deflacionados via IPCA (dez/2024)
- Malha municipal IBGE 2020, CRS área = EPSG:5880