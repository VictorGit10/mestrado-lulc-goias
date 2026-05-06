# Pipeline #13 — IDH-M municipal (IPEA Data API)

**Script**: `scripts/coleta_idhm.py`
**Depende de**: nenhum (consome IPEA API).
**Outputs**: `data/processed/idhm_goias_municipal.csv`.

## O que faz

Coleta IDH-M e sub-índices (renda, longevidade, educação) para os 246 municípios de Goiás via IPEA Data API.

## Cobertura

- **Anos disponíveis**: 1991, 2000, 2010 (Censos demográficos)
- **Linhas**: 246 munis × 3 anos = 738 linhas, zero missings
- **IDHM municipal pós-2010: inexistente** — limitação metodológica, não de acesso. O IDHM municipal completo exige variáveis que só o Censo Demográfico produz nessa granularidade (renda domiciliar, escolaridade por faixa etária, mortalidade infantil estimada). A PNAD Contínua, que sustenta o Radar IDHM pós-2010, só desagrega para nível estadual/RM/RIDE (anos 2012–2017). Notícias que citam "IDHM 2021" referem-se ao Radar IDHM estadual, não municipal. Próxima atualização municipal possível somente com processamento do Censo 2022 por IPEA/PNUD/FJP (sem prazo de divulgação até 2026-05-05).

## Séries IPEA usadas

- `ADH_IDHM` — IDH-M total
- `ADH_IDHM_R` — sub-índice Renda
- `ADH_IDHM_L` — sub-índice Longevidade
- `ADH_IDHM_E` — sub-índice Educação

Fonte primária: IPEA Data API. Fallback: arquivos locais (caso a API esteja fora).

## Como rodar

```bash
python scripts/coleta_idhm.py
```

## Saída

`data/processed/idhm_goias_municipal.csv` — colunas: `cd_mun, nm_mun, ano, idhm, idhm_r, idhm_l, idhm_e`.

## Integração

Mesclado ao painel unificado (Pipeline #16) — slot `idhm*` preenchido para 1991/2000/2010.
