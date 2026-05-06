# Decisões metodológicas — Censo Agropecuário 2017

Subconjunto temático focado nos eixos da dissertação (LULC × estrutura produtiva). IDs validados via API de metadados do SIDRA e coletados em 2026-04-27.

Pipeline relacionado: [#7](../pipelines/07_censo_agro.md).

## Tabelas SIDRA coletadas

(7 tabelas, todas período 2017):

| Tabela | Eixo | Variáveis | Classificações filtradas |
|---|---|---|---|
| **6878** | Estrutura fundiária | nº estabelecimentos, área (ha) | Tipologia (Total/Fam/Não-Fam), Atividade=Total |
| **6884** | Trabalho | nº estab com pessoal, pessoal ocupado | Tipologia (Total/Fam/Não-Fam), Sexo=Total, Atividade=Total |
| **6870** | Tecnologia (mecanização) | nº estab com tratores, nº tratores | Tipologia=Total, Potência=Total, Atividade=Total |
| **6848** | Tecnologia (adubação) | nº estabelecimentos | Tipologia=Total, Uso de adubação (6 categorias) |
| **6851** | Tecnologia (agrotóxicos) | nº estabelecimentos | Tipologia=Total, Uso de agrotóxicos (3 categorias) |
| **6910** | Pecuária (bovinos) | nº estab com bovinos, nº cabeças, vacas reprodutoras | Tipologia=Total, Grupos cabeças=Total, Atividade=Total |
| **6958** | Lavoura (temporária) | nº estab, área colhida (ha), valor produção (R$ mil) | Tipologia=Total, Produtos (soja/milho/cana), Tipo semente=Total |

## Saída principal

`data/processed/sidra_censo_agro_2017.csv` — 246 municípios × 44 colunas (37 brutas + 7 derivadas).

## Variáveis derivadas no painel

- `ca_area_media_estab_ha` — área média por estabelecimento
- `ca_pct_adubacao` — % estabelecimentos que fizeram adubação
- `ca_pct_agrotoxicos` — % estabelecimentos que utilizaram agrotóxicos
- `ca_pct_estab_com_bovinos` — % estabelecimentos com bovinos
- `ca_pct_estab_com_tratores` — % estabelecimentos com tratores
- `ca_pct_familiar` — % estabelecimentos de agricultura familiar
- `ca_lotacao_censo_bov_ha` — cabeças de bovino por hectare de estabelecimento

## Validação

Estatísticas plausíveis: lotação bovina ~0.9 cab/ha, % familiar ~61%, % adubação ~36%, % agrotóxicos ~25%.

## O que estamos abrindo mão

| Item | Razão |
|---|---|
| **Variáveis sociais detalhadas do produtor** (escolaridade, condição além de "familiar/não-familiar", direção dos trabalhos, sexo/cor/raça/faixa etária) | Importantes para análises sociodemográficas, mas tangenciais ao eixo LULC × econômico desta dissertação. |
| **Censos Agro de 1995–96 e 2006** | A tabela 6778 cobre só 2017. As séries anteriores estão em tabelas SIDRA distintas (1227–1229 para 1996; 933–935 para 2006), com schema de variáveis incompatível. Cruzar três censos exige harmonização manual de classes — só faremos se a análise pedir séries históricas estruturais. |
| **Aberturas finas das classes** (ex.: tamanho do estabelecimento em todas as classes possíveis) | Pegamos as agregações mais amplas; refinar é trivial depois se necessário. |
| **Contagem completa da pesquisa** (~milhares de variáveis) | 99% delas não tocam na hipótese da dissertação. Se um achado pedir variável extra, dá para baixar pontualmente reusando o coletor. |
| **Tabela 6778** (nº estabelecimentos por tipologia + área) | A tabela 6878 já cobre nº estabelecimentos + área com as mesmas classificações, e ainda tem a quebra por sexo e idade do produtor. A 6778 seria redundante. |
