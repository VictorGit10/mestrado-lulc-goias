# Decisão metodológica: IDHM municipal pós-2010

## Contexto

O Pipeline #13 coleta IDH-M e sub-índices (renda, longevidade, educação) para os 246 municípios de Goiás via IPEA Data API. Os anos disponíveis são **1991, 2000 e 2010** (anos censitários).

## O que não existe

**IDHM municipal pós-2010 é inexistente.** Isso é uma limitação metodológica, não de acesso. O IDHM municipal completo exige variáveis que só o Censo Demográfico produz nessa granularidade:

- Renda domiciliar per capita
- Escolaridade por faixa etária
- Mortalidade infantil estimada

A PNAD Contínua, que sustenta o "Radar IDHM" pós-2010, não desagrega para município — por isso o Radar cobre apenas nível estadual, regiões metropolitanas e RIDEs (anos 2012–2017).

## Notícias sobre "IDHM 2021"

O que aparece em algumas fontes como "IDHM 2021" refere-se ao **Radar IDHM** atualizado com PNAD 2021/2022, sempre estadual/metropolitano. Não há IDHM municipal 2021.

## Próxima atualização municipal

O próximo IDHM municipal só sairá quando IPEA + PNUD + FJP processarem o Censo 2022. Até 2026-05-05, não houve divulgação oficial nem prazo estimado.

## Decisão para a dissertação

1. **Decisão fechada** — não é pendência: "IDHM municipal disponível apenas para anos censitários 1991/2000/2010; PNAD Contínua não permite atualização municipal pós-2010."
2. **Proxy pós-2010** (se necessário para análise temporal): reconstruir componentes com fontes alternativas (educação via Censo Escolar/INEP, longevidade via SIM/DataSUS, renda via PNADc estadual rateada). Isso seria pipeline próprio, não IDHM oficial.
3. **Atualização futura**: quando Censo 2022 → IDHM 2022 for divulgado, integrar retroativamente.

## Fontes

- Atlas do Desenvolvimento Humano no Brasil — IPEA (https://www.ipea.gov.br/portal/categoria-projetos-e-estatisticas/9941-atlas-do-desenvolvimento-humano-no-brasil)
- IDHM — IPEA (https://www.ipea.gov.br/sites/en-GB/idhm)
- Atlas dos Municípios — PNUD Brasil (https://www.undp.org/pt/brazil/atlas-dos-municipios)
- Radar IDHM 2012–2017 (PDF) — Repositório IPEA (https://repositorio.ipea.gov.br/entities/book/5a7c4091-c1df-47d5-8624-110c70f0e43b)
- Atlas Brasil (http://www.atlasbrasil.org.br/) — serve 1991/2000/2010 para municípios