# Como retomar o trabalho

Checklist para continuar a dissertação em qualquer sessão do Claude Code.

## 1. Ler a documentação

1. [README.md](../README.md) — índice mestre.
2. [narrativa_pipelines.md](../narrativa_pipelines.md) — a **história** de como o trabalho foi construído (fio condutor de todos os pipelines).
3. [guia_de_leitura.md](../guia_de_leitura.md) — os **métodos** em linguagem simples (o que cada um faz, por que foi usado, o que não pode dizer).
4. [pipelines/README.md](../pipelines/README.md) — ficha técnica de cada pipeline (#1–#51).
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

## 3. Estado atual (jul/2026): 51 pipelines concluídos

**Toda a infraestrutura empírica e a investigação Sul→Norte estão fechadas.** A dissertação está em **modo exploração** — a redação foi adiada **por opção** (será barata porque tudo está documentado em `Textos/`).

| Fase | Pipelines | O que entregou |
|---|---|---|
| 0 — Primeira foto | #1, #2 | Séries estaduais (pastagem × PIB, rebanho, lotação) |
| 1 — Fundação de dados | #3, #4, #6, #7, #13, #14, #15, #27 | Coletores municipais validados (SIDRA, MapBiomas, SICOR, fogo, Trase) |
| 2 — Cartografia + transições | #5, #8, #9–#12, #19 | Mapas + matrizes de transição pixel-a-pixel |
| 3 — Consolidação | #16, #17, #18, #20, #25 | Painel unificado, AMC, motor de taxas |
| 4 — Inferência | #21, #22, #23, #24, #26 | Painel FE, DiD, autocorrelação espacial, quebras |
| 5 — Periodização | #28, #28C, #29–#31 | 3 atos data-driven; bimodalidade da idade do pasto |
| 6 — Marcha ao norte | #32–#42 | A tese Sul→Norte, testada e autocorrigida (5 camadas) |
| 6 — Extensões | #43, #44, #40B, #45, #46, #47, #48, #49, #50, #51 | Robustez (MAUP/desagregação), Eixo A (Trase), eixo ambiental (proteção/carbono/PRODES), Eixo C1 (painel espacial), centro de massa econômico (#50), crescimento × desenvolvimento IFDM (#51) |

Detalhe pipeline a pipeline em [pipelines/README.md](../pipelines/README.md); log cronológico em [backlog.md](../backlog.md).

## 4. O que explorar agora

**A fase é exploração, não redação** — otimizar por *riqueza de história × viabilidade com o dado que já existe*, não por "fechar a dissertação". Os fios 1–6 do [backlog.md](../backlog.md) foram todos fechados (o fio 6 foi **reaberto e feito** como #51), assim como os eixos A / ambiental / **C (C1 + C2)**. Frentes possíveis (todas opcionais):

- ✅ **Eixo C2 — FECHADO (2026-07-18)**: validação das quebras empíricas (1991/1999/2006) na literatura, em [metodologia/validacao_quebras_literatura.md](../metodologia/validacao_quebras_literatura.md). As três viram evidência de apoio (Collor/crédito; câmbio 1999; Moratória da Soja).
- ✅ **Crescimento sem desenvolvimento — FEITO (2026-07-18, [#51](../pipelines/51_crescimento_sem_desenvolvimento.md))**: reabriu o fio 6 com o IFDM (FIRJAN) municipal 2013–2023. Norte quase dobra a área mas ganha IFDM igual e fica −0,08 abaixo; expansão de área desacoplada do desenvolvimento.
- ⏳ **Aptidão edafoclimática direta como exposição no #38** (ataca a perna 4, a mais fraca) — *viabilidade verificada*: shapefile de aptidão do **MacroZAEE-GO** baixável no SIEG; agregar às AMCs por zonal-stats. Ver [backlog.md](../backlog.md) → "Frentes de expansão opcionais".
- ⏳ **Capacidade instalada da cadeia (CONAB SISDEP / SIGSIF / CNPJ)** para a ressalva do #45 (Trase mede fluxo, não capacidade) — *viabilidade verificada*: SISDEP tem série histórica; CNPJ reconstrói contagem anual de frigoríficos/silos. Ver backlog. Provável nulo (defensivo).
- **Micro-mistério 2001–05** — caracterizar o lado institucional (pré-Moratória da Soja 2006).
- **Redação** — quando **você** decidir parar de explorar e escrever; a documentação é a rede de segurança que a torna barata.

## 5. Preferências

- Comunicação em português (pt-BR).
- Scripts em Python (pandas, geopandas, matplotlib, requests, sidrapy).
- QGIS para layout cartográfico final.
- Valores monetários deflacionados via IPCA (dez/2024).
- Malha municipal IBGE 2020, CRS área = EPSG:5880.

## 6. Reprodutibilidade

- `requirements.txt` na raiz do projeto lista todas as dependências Python.
- Todos os scripts são idempotentes (cache CSV). Apagar `data/raw/` força re-download; apagar `data/processed/` força re-processamento.
- Para `geobr`: instalar com `pip install --no-deps geobr` (conflitos de versão com shapely e lxml).
- Para GEE: autenticação via browser (`ee.Authenticate()`) e registro de projeto noncommercial.