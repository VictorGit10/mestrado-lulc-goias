# Pipeline #7 — Censo Agropecuário 2017 (SIDRA)

**Script**: `scripts/coleta_sidra.py --censo-agro`
**Quando foi feito**: 2026-04-27.
**Depende de**: nenhum (compartilha mecanismo de cache/paginação com o Pipeline #3).
**Outputs**: 7 CSVs individuais em `data/processed/sidra_censo_*.csv` (formato longo) + `data/processed/sidra_censo_agro_2017.csv` (painel consolidado 246×44).

## O que faz

Coleta 7 tabelas SIDRA do Censo Agropecuário 2017 para os 246 municípios de Goiás e monta um painel wide-format (1 linha/município) com 44 colunas. Usa o mesmo mecanismo de cache e paginação do Pipeline #3 (`sidrapy` + CSV local).

## Tabelas coletadas

(ver [metodologia/decisoes_censo_agro.md](../metodologia/decisoes_censo_agro.md) para detalhes de variáveis e classificações):

- 6878: Estrutura fundiária (estabelecimentos + área, por tipologia familiar)
- 6884: Pessoal ocupado (por tipologia familiar)
- 6870: Tratores (estabelecimentos com tratores + nº tratores)
- 6848: Adubação (estabelecimentos por tipo de adubação)
- 6851: Agrotóxicos (estabelecimentos por uso de agrotóxicos)
- 6910: Bovinos (estabelecimentos com bovinos + efetivo + vacas reprodutoras)
- 6958: Lavouras temporárias (soja, milho, cana — nº estab, área colhida, valor produção)

## Como rodar

```bash
python coleta_sidra.py --censo-agro
# ou para rebaixar:
python coleta_sidra.py --censo-agro --force
```

## Saídas

- 7 CSVs individuais em `data/processed/sidra_censo_*.csv` (formato longo)
- `data/processed/sidra_censo_agro_2017.csv` — painel consolidado (246×44)

## Validação

Estatísticas plausíveis — lotação bovina ~0.9 cab/ha, % familiar ~61%, % adubação ~36%, % agrotóxicos ~25%.

## Variáveis derivadas no painel

- `ca_area_media_estab_ha` — área média por estabelecimento
- `ca_pct_adubacao` — % estabelecimentos que fizeram adubação
- `ca_pct_agrotoxicos` — % estabelecimentos que utilizaram agrotóxicos
- `ca_pct_estab_com_bovinos` — % estabelecimentos com bovinos
- `ca_pct_estab_com_tratores` — % estabelecimentos com tratores
- `ca_pct_familiar` — % estabelecimentos de agricultura familiar
- `ca_lotacao_censo_bov_ha` — cabeças de bovino por hectare de estabelecimento
