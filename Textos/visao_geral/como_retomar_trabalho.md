# Como retomar o trabalho

Checklist para continuar a dissertação em qualquer sessão do Claude Code.

## 1. Ler a documentação

1. [README.md](../README.md) — índice mestre.
2. [narrativa_pipelines.md](../narrativa_pipelines.md) — a **história** de como o trabalho foi construído (fio condutor de todos os pipelines).
3. [guia_de_leitura.md](../guia_de_leitura.md) — os **métodos** em linguagem simples (o que cada um faz, por que foi usado, o que não pode dizer).
4. [pipelines/README.md](../pipelines/README.md) — ficha técnica de cada pipeline (#1–#54; os quatro de agosto/2026 estão no [índice lógico](../indice_logico_pipelines.md)).
5. [backlog.md](../backlog.md) — fios em aberto (modo **exploração**).
6. [escopo_dissertacao.md](escopo_dissertacao.md) — escopo/hipóteses **iniciais** (a tese que de fato emergiu está na narrativa e no guia).
7. [estrutura_diretorios.md](estrutura_diretorios.md) — estrutura do projeto.

## 2. Inspecionar dados

```bash
ls data/processed/    # ~159 CSVs + 3 parquets (painel_unificado, painel_amc_goias, +MG paralelo)
ls outputs/            # PNGs, mapas, diagnósticos (25 subpastas por eixo de análise)
ls data/cache/         # Cache de requisições (sidra, sicor, gee)
```

Duas tabelas-mãe: `painel_unificado.parquet` (9.840×185, o **transversal** — 246 munis × 40 anos) e `painel_amc_goias.parquet` (166 AMCs, o **longitudinal** — território constante, D11). O primeiro consolida LULC + pecuária + lavouras + PIB + população + SICOR + Censo 2017 + IDH-M + fogo + Trase.

## 3. Estado atual (ago/2026): 58 pipelines, e o texto de qualificação escrito

**Toda a infraestrutura empírica e a investigação Sul→Norte estão fechadas, e o trabalho saiu do modo exploração.** O modo exploração foi encerrado em **11/ago/2026**, e desde então a frente é a **redação**: o documento de qualificação está em [`qualificacao/`](../../qualificacao/README.md) — texto ABNT com abnTeX2, capítulos 00–09, 8 figuras, 115 páginas, apêndice B com as 31 decisões e apêndice C com as rotinas. **Depósito previsto para dez/2026, defesa para jan/2027**; o cronograma detalhado é o capítulo 6 do próprio texto.

> **Se você está retomando agora**, o ponto de partida é [`qualificacao/README.md`](../../qualificacao/README.md), que é o estado vivo da redação (o que já foi conferido, por qual régua, e o que ficou pendente). Este documento aqui cobre a infraestrutura empírica que sustenta o texto.

Quatro pipelines nasceram durante a redação e ainda não têm ficha em `pipelines/`: **#55** (bootstrap de blocos, robustece a Perna 1), **#56** (corrida de exposições — origem da **D28**, que rebaixou a aptidão de canal a régua), **#57** (qualidade do remanescente) e **#39B** (domínio do esgotamento — origem da **D29**). Estão documentados em [indice_logico_pipelines.md](../indice_logico_pipelines.md).

| Fase | Pipelines | O que entregou |
|---|---|---|
| 0 — Primeira foto | #1, #2 | Séries estaduais (pastagem × PIB, rebanho, lotação) |
| 1 — Fundação de dados | #3, #4, #6, #7, #13, #14, #15, #27 | Coletores municipais validados (SIDRA, MapBiomas, SICOR, fogo, Trase) |
| 2 — Cartografia + transições | #5, #8, #9–#12, #19 | Mapas + matrizes de transição pixel-a-pixel |
| 3 — Consolidação | #16, #17, #18, #20, #25 | Painel unificado, AMC, motor de taxas |
| 4 — Inferência | #21, #22, #23, #24, #26 | Painel FE, DiD, autocorrelação espacial, quebras |
| 5 — Periodização | #28, #28C, #29–#31 | 3 atos data-driven; bimodalidade da idade do pasto |
| 6 — Marcha ao norte | #32–#42 | A tese Sul→Norte, testada e autocorrigida (5 camadas) |
| 6 — Extensões | #43, #44, #40B, #45, #46, #47, #48, #49, #50, #51, #52, #53, #54 | Robustez (MAUP/desagregação), Eixo A (Trase), eixo ambiental (proteção/carbono/PRODES), Eixo C1 (painel espacial), centro de massa econômico (#50), crescimento × desenvolvimento IFDM (#51), aptidão exógena no #38 (#52), capacidade de armazenagem (#53), endurecimento shift-share do drive comum (#54) |

Detalhe pipeline a pipeline em [pipelines/README.md](../pipelines/README.md); log cronológico em [backlog.md](../backlog.md).

## 4. O que resta

**A fase é redação, não exploração.** As frentes que restam estão no cronograma do capítulo 6 da qualificação, e nenhuma delas reverte o que a tese afirma: a **revisão de literatura** (a mais extensa e a menos comprimível, orientada pela lista de leitura da §2.10), o fechamento das **arestas empíricas residuais** inventariadas no apêndice de decisões, e a **redação final**. Três arestas já têm desenho definido — o cadastro ambiental pixel a pixel, a comparação com a coleção anterior do MapBiomas, e a busca de uma exposição que não se ordene com a latitude (decorrente da D28).

A lista abaixo é o **registro do que a exploração fechou** até 11/ago/2026, e não uma fila de trabalho. Os fios 1–6 do [backlog.md](../backlog.md) foram todos fechados (o fio 6 foi **reaberto e feito** como #51), assim como os eixos A / ambiental / **C (C1 + C2)**:

- ✅ **Eixo C2 — FECHADO (2026-07-18)**: validação das quebras empíricas (1991/1999/2006) na literatura, em [metodologia/validacao_quebras_literatura.md](../metodologia/validacao_quebras_literatura.md). As três viram evidência de apoio (Collor/crédito; câmbio 1999; Moratória da Soja).
- ✅ **Crescimento sem desenvolvimento — FEITO (2026-07-18, [#51](../pipelines/51_crescimento_sem_desenvolvimento.md))**: reabriu o fio 6 com o IFDM (FIRJAN) municipal 2013–2023. Norte quase dobra a área mas ganha IFDM igual e fica −0,08 abaixo; expansão de área desacoplada do desenvolvimento.
- ✅ **Aptidão edafoclimática como exposição no #38 — FEITO (2026-07-18, [#52](..\pipelines\52_aptidao_edafoclimatica.md))**: troca o proxy de área do #38 por uma aptidão física **exógena** (Embrapa 1:500k, via WFS). A aptidão medida **reproduz** o gradiente Sul→Norte (r_lat=−0,44); o achado do rebanho reaparece **sem a complementaridade** (câmbio×aptidão→rebanho β=−0,033, p=0,026 clusterizado) e beira o FDR. Ganho de **identificação**. **Ler junto com o #54** (a inferência correta calibra o p para baixo). **Pendência de refino**: MacroZAEE-GO estadual (1:250k, mais defensável na banca) **não é fetchável** deste ambiente (cert TLS do SIEG) → download manual no IMB/SIEG + remapear legenda; ver [backlog.md](../backlog.md) → "Frentes de expansão opcionais".
- ✅ **Endurecimento shift-share do drive comum (opção B) — FEITO (2026-07-18, [#54](../pipelines/54_defensabilidade_perna4.md))**: nomeia o desenho do #38/#52 como shift-share e roda a **inferência correta**. **Mudança de estrutura**: com a significância calibrada para baixo, o drive comum deixou de ser perna própria e virou o **positivo da Perna 3** ("reorganização coordenada, não deslocamento"); o teto de oferta passou a ser a Perna 4. A **permutação do shifter** (câmbio embaralhado, aptidão fixa) revela que o p clusterizado (~0,03) era **otimista** — sai para **≈0,07 (naive) a 0,13 (rotação circular): não significante a 5%**. Mas o padrão **passa na especificidade**: placebos de desfecho nulos (câmbio×aptidão→urbano/água), lead limpo (sem antecipação) e jackknife estável (sinal 100%, nenhum ano isolado carrega). **Veredito: "corroborante, não estabelecido" — mais defensável, menos significante.** Sair para "estabelecido" só pela **opção (A)** (shifter espaço-temporal: frete/ferrovia/clima, ou IV do câmbio = fio novo); ver backlog → "Endurecimento da perna 4".
- ✅ **Capacidade instalada da cadeia — FEITO na forma viável (2026-07-18, [#53](../pipelines/53_centro_massa_capacidade.md))**: o cadastro de armazéns da CONAB (fetchável, ao contrário do MacroZAEE) virou um **centroide de capacidade** — a camada **mais ao sul de todas** (~150 km ao sul do pasto, ~83 km ao sul até do crédito), fechando a metade "silos" da ressalva do #45 (capacidade consolida o núcleo, não lidera). A metade "frigoríficos" (SIGSIF) e o teste de liderança temporal (CNPJ município×ano) seguem descartados por acesso/esforço; ganho realizado = defensivo, como previsto. Ver backlog → "Frentes de expansão opcionais".
- **Micro-mistério 2001–05** — caracterizar o lado institucional (pré-Moratória da Soja 2006). Segue aberto, e não é pendência de completude.

## 5. Preferências

- Comunicação em português (pt-BR).
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy).
- QGIS para layout cartográfico final.
- Valores monetários deflacionados via IPCA (dez/2024).
- Malha municipal IBGE 2020, CRS métrico = EPSG:5880 (policônica de compromisso, não equal-area).

## 6. Reprodutibilidade

- `requirements.txt` na raiz do projeto lista todas as dependências Python.
- Todos os scripts são idempotentes (cache CSV). Apagar `data/raw/` força re-download; apagar `data/processed/` força re-processamento.
- Para `geobr`: instalar com `pip install --no-deps geobr` (conflitos de versão com shapely e lxml).
- Para GEE: autenticação via browser (`ee.Authenticate()`) e registro de projeto noncommercial.