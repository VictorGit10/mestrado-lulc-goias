# Como retomar o trabalho

Checklist para continuar a dissertação em qualquer sessão do Claude Code.

## 1. Ler a documentação

1. [README.md](../README.md) — índice mestre.
2. [escopo_dissertacao.md](escopo_dissertacao.md) — eixos e hipóteses.
3. [backlog.md](../backlog.md) — o que falta fazer.

## 2. Inspecionar dados

```bash
ls data/processed/    # CSVs e parquets prontos
ls outputs/            # PNGs e GIFs gerados
ls data/cache/         # Cache de requisições (sidra, sicor, gee)
```

O painel unificado (`painel_unificado.parquet`, 9.840×66) consolida LULC + pecuária + lavouras + PIB + população + SICOR + Censo 2017 + IDH-M.

## 3. Decidir o próximo bloco

Ver [backlog.md](../backlog.md). Prioridades sugeridas:

1. **Análise espacial estatística** (Moran's I, LISA, spreg) — núcleo analítico faltante; painel unificado destrava.
2. **Pipeline #14 (fogo)** — script pronto, rodar com GEE.
3. **IDH-M 2021** — download manual do Atlas Brasil, integrar ao painel.
4. **Análise descritiva da safrinha** (#15) — dados coletados, sem gráficos.
5. **Infraestrutura agroindustrial** (SIGSIF, CONAB, DNIT) — coleta do zero.
6. **Reprodutibilidade** — requirements.txt/pyproject.toml.

## 4. Preferências

- Comunicação em português (pt-BR).
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy).
- QGIS para layout cartográfico final.
- Valores monetários deflacionados via IPCA (dez/2024).
- Malha municipal IBGE 2020, CRS área = EPSG:5880.

## 5. Reprodutibilidade

Todos os scripts são idempotentes (cache CSV). Apagar `data/raw/` força re-download; apagar `data/processed/` força re-processamento.