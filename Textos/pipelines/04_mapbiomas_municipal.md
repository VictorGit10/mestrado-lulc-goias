# Pipeline #4 — MapBiomas municipal Goiás

**Script**: `scripts/pipeline_municipal.py`
**Quando foi feito**: 2026-04-26.
**Depende de**: Pipeline #3 (usa nomes/códigos IBGE de `sidra_pam1612_temporarias.csv` para o merge por nome).
**Outputs**: `data/processed/mapbiomas_munis_goias.csv` (8.6 MB).

## O que faz

Lê a aba `COVERAGE_10.1` do xlsx do MapBiomas (já em cache desde o Pipeline #1) e extrai uma tabela longa por município de Goiás. Resolve dois problemas:

1. O xlsx vem em formato wide (1 coluna por ano) e divide cada município nos biomas que o cortam (Cerrado e Mata Atlântica para munis fronteiriços do sudeste de GO). O pipeline derrete para longo e soma os biomas.
2. O xlsx só tem o NOME do município. Sem o código IBGE, não dá pra fazer join com SIDRA. Solução: merge por nome contra a tabela `cd_mun ↔ nm_mun` extraída do `sidra_pam1612_temporarias.csv` (Pipeline #3). Como toda a coleta IBGE usa a mesma grafia oficial, o match é exato — sem fuzzy.

## Como rodar

```bash
python pipeline_municipal.py
```

## Saída

`data/processed/mapbiomas_munis_goias.csv` (8.6 MB).

## Schema

```
cd_mun       int    Código IBGE 7 dígitos
nm_mun       str    Nome do município
ano          int    1985–2024
class_id     int    Código da classe MapBiomas
class_nome   str    Nome em pt-BR (15=Pastagem, 39=Soja, 20=Cana-de-açúcar, etc.)
area_ha      float  Área em hectares (somada sobre Cerrado + Mata Atlântica)
```

Total: **137.080 linhas** = 246 munis × 40 anos × 22 classes.

## Validações realizadas

1. **Batimental**: a soma municipal de pastagem (classe 15) bate com a série UF antiga (`pastagem_goias_anual.csv`) com **erro máximo de 0,0000%** ao longo dos 40 anos. Math é math.
2. **Soja MapBiomas vs SIDRA (2022)**: total Goiás 4,17 Mha vs 4,12 Mha (razão 1,01). Os 10 maiores produtores de soja batem em ordem entre as duas fontes (Rio Verde, Jataí, Cristalina, Montividiu, Paraúna, Catalão, Mineiros, Ipameri, Chapadão do Céu, Silvânia). A diferença ≤ 12% por município é esperada e tem causa metodológica:
   - SIDRA = área plantada declarada pelo produtor.
   - MapBiomas = pixels classificados como soja por sensoriamento remoto, podendo capturar área plantada em segunda safra ou cultura de inverno que SIDRA conta como milho.
3. **Cana 2022**: SIDRA 933k ha vs MapBiomas 1.004k ha (razão 1,08). Top munis batem (Quirinópolis, Mineiros, Goiatuba, Itumbiara, Acreúna).
4. **Cobertura Goiás 2024** (proporção): Pastagem 35,2% > Cerrado 18,0% > Floresta 14,2% > Soja 13,2% > Mosaico 10,5% > Cana 2,4%. Bate com o conhecimento geral.

**Munis-borda descartados (4)**: Brasília (DF), Paraná (TO), São Desidério (BA), Talismã (TO) — somam ~28 ha total na série inteira (pixels de fronteira mal-classificados). Irrelevante.

## Limitações

**O que o Pipeline #4 ainda NÃO faz**: não anexa geometria (geobr/GPKG). Para mapas, vai precisar instalar `geopandas` + `geobr` em uma fase próxima e fazer `merge` por `cd_mun`. Como o código IBGE já está pronto, o merge será trivial.
