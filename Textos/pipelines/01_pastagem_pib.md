# Pipeline #1 — Pastagem × PIB Goiás

**Script**: `scripts/grafico_pastagem_pib_goias.py`
**Quando foi feito**: Primeiro script, no início do projeto.
**Depende de**: nenhum (é o pipeline-base).
**Outputs**: ver [graficos_descritivos.md](../outputs/graficos_descritivos.md) (PNGs 01–02) e [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## O que faz

1. Baixa o xlsx do MapBiomas Coleção 10.1 (78MB, do Google Drive) → cacheado em `data/raw/`.
2. Filtra Goiás, classe 15 (Pastagem), agrega ano-a-ano (soma de biomas).
3. Baixa o **PIB total de Goiás** via SIDRA tabela 5938, variável 37, **nível UF** (territorial_level=3).
4. Baixa o **IPCA mensal** via SIDRA tabela 1737, calcula índice acumulado, deflaciona o PIB para reais de **dez/2024**.
5. Gera dois PNGs: pastagem 1985–2024 sozinha, e painel pastagem+PIB lado a lado.

## Como rodar

```bash
python grafico_pastagem_pib_goias.py
```

## Saída

- `outputs/01_pastagem_goias_1985-2024.png`
- `outputs/02_pastagem_pib_goias.png`
- `data/processed/pastagem_goias_anual.csv`
- `data/processed/pib_goias_real.csv`

## Limitações

- Só nível UF (Goiás como agregado único).
- PIB começa em 2002 — anos anteriores ficam vazios no gráfico de overlap.
- Deflator usa IPCA dezembro — não IGP-DI nem deflator implícito do PIB.
