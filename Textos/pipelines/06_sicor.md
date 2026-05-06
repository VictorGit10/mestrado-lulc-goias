# Pipeline #6 — Coleta SICOR/BACEN

**Script**: `scripts/coleta_sicor.py`
**Quando foi feito**: 2026-04-27 (registrado junto ao #8).
**Depende de**: nenhum.
**Outputs**: 5 CSVs em `data/processed/sicor_*.csv`. Ver [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## O que faz

Coleta crédito rural municipal e estadual via API OData do SICOR/BACEN para Goiás, 2013–2026. Salva em valores nominais (deflação fica para análise — ver [metodologia/deflacao_ipca.md](../metodologia/deflacao_ipca.md)).

## Decisões de escopo

Decisões metodológicas e idiossincrasias da API documentadas em [metodologia/decisoes_sicor.md](../metodologia/decisoes_sicor.md).

## Validações realizadas

- Soma municipal = soma UF em todos os anos (razão 1.0000).
- 245/246 munis cobertos (Valparaíso de Goiás sem código BACEN).

## Como rodar

```bash
python coleta_sicor.py
```

## Saída

| Arquivo | Conteúdo |
|---|---|
| `sicor_custeio_municipal.csv` | Operações de crédito de custeio por município e ano |
| `sicor_invest_municipal.csv` | Operações de crédito de investimento por município e ano |
| `sicor_painel_municipal.csv` | Painel consolidado de crédito rural (custeio + investimento) |
| `sicor_uf_anual.csv` | Agregação estadual anual das operações de crédito |
| `sicor_de_para_municipio.csv` | De-para código município SICOR → IBGE |

Detalhes de schema/granularidade em [metodologia/decisoes_sicor.md](../metodologia/decisoes_sicor.md).
