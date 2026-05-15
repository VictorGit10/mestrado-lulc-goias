# Validação cruzada (MapBiomas × SIDRA)

Cobertura/uso da terra é medido por dois sistemas independentes:
- **MapBiomas**: pixels classificados via sensoriamento remoto (Landsat, 30m).
- **SIDRA/PAM**: área plantada declarada pelo produtor ao IBGE.

Comparar os dois é essencial para defender a qualidade dos dados na qualificação.

## Soja — validação implementada

Sistemática para a classe Soja, comparando áreas do MapBiomas com áreas plantadas declaradas no SIDRA (PAM, tabela 1612, variável 109).

**Arquivo:** `data/processed/validacao_soja_mapbiomas_sidra.csv`
**Pipeline:** [#5](../pipelines/05_pastagem_soja.md)

### Resultados típicos

- **Correlação Pearson** entre as fontes: ~0,85–0,95 para anos ≥ 2000.
- **Razão mediana** (MapBiomas / SIDRA): próxima de 1,0, com pequena tendência de MapBiomas subestimar levemente em alguns períodos.
- No **Pipeline #16** (4.316 pares 2000–2023): Pearson r = 0,971; razão mediana 1,124.

### Causas conhecidas das diferenças

1. **Segunda safra**: MapBiomas captura a cobertura no momento; pode ler como "soja" área que SIDRA registra como "milho 2ª safra" (ver [Pipeline #15](../pipelines/15_safrinha.md)).
2. **Borda de pixel**: classificação raster tem incerteza nos limites de talhão.
3. **Auto-declaração**: SIDRA depende do produtor; sub-declaração possível em pequenos.

### Implicação

A série de soja do MapBiomas é considerada **consistente com a fonte oficial do IBGE** para análises agregadas. Diferenças ≤ 12% por município são esperadas e têm causa metodológica explicável — não são erro.

## Cana — validação pontual (Pipeline #4)

- 2022: SIDRA 933k ha vs MapBiomas 1.004k ha (razão 1,08).
- Top munis batem (Quirinópolis, Mineiros, Goiatuba, Itumbiara, Acreúna).

## Pastagem — validação batimental (Pipeline #4 e #5)

- **Soma municipal vs UF antiga**: erro máximo de 0,0000% ao longo dos 40 anos. Math é math — confirma que o pivot longo→agregado é idempotente.

## PIB e VAB agro UF — IPEA Data nativo × SIDRA municipal-agregado

Para o nível UF existem duas fontes:

- **IPEA Data** (Contas Regionais encadeadas IBGE, séries `PIBE` e `PIBAGE`): valores estaduais nativos a preços de 2010, 1985-2023 contínuo. Reescalados para R$ dez/2024 via IPCA dez/2010→dez/2024 (`scripts/coleta_pib_uf_ipea.py`). Saída: `data/processed/pib_uf_ipea_goias.csv` (`pib_uf_real_rs`, `va_agro_uf_real_rs`).
- **SIDRA 5938** agregado para UF: soma dos 246 municípios disponível só a partir de 2002, deflacionado por IPCA dez/2024 (Pipeline #1 e #16). Colunas `pib_real_rs` e `va_agro_real_rs` no `painel_unificado.parquet`.

### Comparação na janela comum (2002-2023)

| Indicador | Média | Mín | Máx |
|---|---|---|---|
| Razão PIB (IPEA / SIDRA) | 1,002 | 0,867 (2023) | 1,212 (2002) |
| Razão VAB agro (IPEA / SIDRA) | 1,015 | 0,894 (2021) | 1,212 (2002) |

A razão é exatamente 1,000 em 2010 (ano-base do deflator implícito do PIB usado pelo IPEA).

### Origem da divergência

São **deflatores diferentes** aplicados a séries derivadas da mesma fonte primária:

- A série IPEA carrega o **deflator implícito do PIB** (encadeado pelo IBGE entre os SCN antigos e o SCN 2010) até 2010, depois IPCA daí em diante.
- A série SIDRA usa **IPCA** o tempo todo, base dez/2024 (ver `deflacao_ipca.md`).

Como o IPCA cresce mais que o deflator do PIB no Brasil pós-Real, valores em "preços PIB 2010" trazidos para 2024 via IPCA divergem **sistematicamente** dos valores que sempre viveram em "preços IPCA".

### Implicação para os pipelines

- **Pipeline #21** (correlações UF Δ-vs-Δ) passa a usar a série IPEA UF (1985-2023, N≈37 após primeiras diferenças vs N≈21 antes). Como a análise opera em **deltas**, a diferença de nível absoluto entre os dois deflatores não atrapalha — as taxas de variação são comparáveis.
- **Pipeline #22** (painel municipal 2-way FE) **não é tocado**: continua usando `pib_real_rs` e `va_agro_real_rs` municipais (SIDRA, 2002+).
- Site (`painel_goias.json`): expõe as duas séries lado a lado (`pib_uf_real_rs` e `pib_real_rs`, idem para VA agro), permitindo ao leitor ver a divergência diretamente.

### Quebra metodológica embutida em 2002

A série `PIBAGE` do IPEA tem **dois regimes documentados no metadado oficial**: 1985-2001 (Antigo Sistema de Contas Regionais, conceito a preços básicos) e 2002+ (Sistema de Contas Regionais Referência 2002). A participação agro pula de ~5-7% (1991-2001) para ~13% (2002+) no plot da série. Parte é mudança real do peso do agro pós-Plano Real, parte é mudança de definição de "agropecuária" no SCN. O usuário do dado deve tratar esse degrau como **artefato metodológico parcial**, não somente como sinal econômico.

## O que ainda falta

Validação cruzada para:
- **Milho** (1612 var 109/216 vs MapBiomas classe 39 ou agrupada): repetir a metodologia da soja para milho.
- **Cana** sistemática (não só 2022).
- **Pastagem vs PPM**: confronto entre área de pastagem MapBiomas e estimativa derivada de rebanho/lotação típica.

Está no [backlog](../backlog.md) como reforço para a qualificação.
