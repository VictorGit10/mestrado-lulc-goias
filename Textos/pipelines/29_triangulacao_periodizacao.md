# Pipeline #29 — Triangulação para periodização data-driven

**Scripts**: `periodizacao_multivariada.py` (#29a), `periodizacao_stars.py` (#29b), `periodizacao_transicoes.py` (#29c)
**Verificação**: `verificacao_periodizacao.py` (#30), `intensity_analysis.py` (#31)
**Status**: ✅ executado (2026-05-19)
**Depende de**: #17 (`taxas_lulc_goias.csv`), #19 (`conversao_bruta_goias.csv`), #26 (quebras univariadas)

## Motivação

A dissertação dividia 1985–2024 em atos ancorados por marcos institucionais, mas as fronteiras entre atos careciam de metodologia explícita. Se a banca questionar "por que 2005 e não 2006?", não havia resposta formal. Além disso, marcos como Código Florestal (2012) e Cerrado Manifesto (2018) eram tratados como equivalentes a Lei Kandir (1996), apesar de terem suportes empíricos radicalmente diferentes.

Esta pipeline inverte a lógica:

1. **Atos são definidos por dados**, não por eventos institucionais.
2. **Fronteiras são estabelecidas por triangulação** de métodos estatísticos independentes.
3. **Marcos são classificados** por força evidencial (A/B/C), não por importância discursiva.

A fraqueza de um marco não afeta o ato — as fronteiras vêm de dados, não de eventos.

## Regra de decisão (definida ANTES de rodar)

- **Método primário**: sup-F multivariado (Quandt-Andrews para 3 séries GO conjuntas)
- **Métodos de sensibilidade**: Rodionov STARS, KL/TV de matrizes de transição
- **Fronteira confirmada** = primário + ≥1 sensibilidade convergam
- Se os 3 métodos divergem → sensibilidade ao método documentada como achado

## Especificação dos testes

### Teste 1: Quebras estruturais multivariadas (`periodizacao_multivariada.py`)

Quandt-Andrews sup-F multivariado para a matriz (N=39, p=3) com Δveg_nat, Δpast, Δagric anuais de GO. Binary segmentation com min_size=5, max_breaks=3, F_threshold=4.0.

**Resultados:**

| Quebra | Ano | F estatístico | Segmento anterior | Segmento posterior |
|--------|----:|:------------:|-------------------|--------------------|
| 1 | 1991 | 10.3 | 1985-1990 | 1991-2000 |
| 2 | 2001 | 62.2 | 1991-2000 | 2001-2020* |
| 3 | 2020 | 21.5 | 2001-2019 | 2020-2024 |

*O binary segmentation detecta 2001 e 2020 na primeira passagem; a subamostra 2001-2020 pode conter quebras adicionais que o sup-F não detecta com F_threshold=4.0.*

### Teste 2: Transições KL/TV (`periodizacao_transicoes.py`)

Divergência KL (row-weighted por distribuição estacionária) entre matrizes de transição 6×6 ano-a-ano. Bootstrap com 1000 permutações para significância. TV(π) = variação total da distribuição estacionária.

**Resultados:**
- KL é monotonicamente crescente — todo ano ≥1996 é significativamente diferente de 1985
- TV(π) tem pico local em 2003 (0.168) e plateau em 2018-2020
- KL não discrimina anos de fronteira específicos (ver limitações)

### Teste 3: Rodionov STARS (`periodizacao_stars.py`)

Sequential t-test Analysis of Regime Shifts (l=5, α=0.05, Huber weight=1) nas 3 séries GO.

**Resultados (l=5, α=0.05):**

| Série | Shifts detectados |
|-------|-------------------|
| vegetação_natural | 2006 |
| pastagem | 2004 |
| agricultura | 2004, 2014 |

Com α=0.01, nenhum shift é detectado. Com α=0.10, detecta 2004, 2006, 1996, 1998, 2014, 2018.

## Triangulação — resultado consolidado

| Fronteira | sup-F multivariado | STARS | KL/TV | Status |
|-----------|:------------------:|:-----:|:-----:|--------|
| ~1991 | ✓ (F=10.3) | ✗ | ✗ | Não confirmada (1 método, instável) |
| **~2001** | **✓ (F=62.2)** | **✗** | **✓ (pico 2003)** | **Confirmada (primário + sensibilidade)** |
| ~2005/2006 | ✗ | ✓ (2004/2006) | ✓ (pico 2003) | Sensibilidade (sem primário) |
| ~2014 | ✗ | ✓ (agric) | ✗ | Não confirmada (1 método, 1 série) |
| **~2020** | **✓ (F=21.5)** | **✗** | **✓ (pico 2018-2020)** | **Confirmada (primário + sensibilidade)** |

**Fronteiras confirmadas**: ~2001, ~2020 → definem P1/P2 e P3/P4.
**Fronteira de sensibilidade**: ~2005/2006 → define P2/P3 (sem primário, mas com composição diferente).

## Verificação de sanidade (Pipeline #30)

### 1. Falso positivo (ruído branco)

Geração de 500 simulações com séries aleatórias (n=39, p=3) e contagem de quebras detectadas pelo sup-F multivariado + binary segmentation.

| F_threshold | FPR | Avg breaks/sim |
|:-----------:|:---:|:---------------:|
| 3.0 | 0.286 | 0.36 |
| **4.0** | **0.110** | **0.12** |
| 5.0 | 0.028 | 0.03 |

Com F_threshold=4.0, FPR=11% — marginalmente acima de 10%. As quebras reais (F=62.2 e F=21.5) estão muito acima do limiar e são genuínas. A quebra de 1991 (F=10.3) está no limiar e deve ser interpretada com cautela.

### 2. Sensibilidade de parâmetros

Variação de min_size (3, 5, 7) e F_threshold (3, 5, 7) — 9 combinações:

| min_size | F_thresh | Quebras | Anos | F estatísticos |
|:--------:|:--------:|:-------:|:----:|:--------------:|
| 3 | 3 | 3 | 1989, 2001, 2020 | 13.9, 62.2, 21.5 |
| 3 | 5 | 3 | 1989, 2001, 2020 | 13.9, 62.2, 21.5 |
| 3 | 7 | 3 | 1989, 2001, 2020 | 13.9, 62.2, 21.5 |
| **5** | **3** | **3** | **1991, 2001, 2020** | **10.3, 62.2, 21.5** |
| 5 | 5 | 3 | 1991, 2001, 2020 | 10.3, 62.2, 21.5 |
| 5 | 7 | 3 | 1991, 2001, 2020 | 10.3, 62.2, 21.5 |
| 7 | 3 | 3 | 1993, 2001, 2018 | 8.7, 62.2, 19.4 |
| 7 | 5 | 3 | 1993, 2001, 2018 | 8.7, 62.2, 19.4 |
| 7 | 7 | 3 | 1993, 2001, 2018 | 8.7, 62.2, 19.4 |

**2001** aparece em TODAS as 9 combinações (F=62.2 sempre) → extremamente robusta.
**2020** aparece em 6/9 (desloca para 2018 com min_size=7).
**1991** é instável: desloca de 1989→1991→1993 conforme min_size aumenta, com F baixo (8.7–13.9).

### 3. Consistência univariado vs multivariado

| Método | Quebras em GO |
|--------|:-------------:|
| Univariado (Pipeline #26) | 1991, 1998, 2001, 2005, 2018, 2020 |
| Multivariado (Pipeline #29a) | 1991, 2001, 2020 |
| Convergentes | 1991, 2001, 2020 |
| Só univariado | 1998, 2005, 2018 |
| Só multivariado | nenhum |

As 3 quebras multivariadas são subconjunto das univariadas — coerente. As quebras "só univariado" (1998, 2005, 2018) são detectadas em séries individuais mas não no teste conjunto, o que é esperado e consistente.

### 4. Sensibilidade STARS

| l | α | Shifts | Anos |
|:-:|:-:|:------:|:----:|
| 3 | 0.05 | 0 | — |
| 3 | 0.10 | 1 | 2004 |
| 5 | 0.01 | 0 | — |
| **5** | **0.05** | **4** | **2004, 2006, 2014** |
| 5 | 0.10 | 6 | 1996, 1998, 2004, 2014, 2018 |
| 7 | 0.05 | 6 | 1996, 1998, 2004, 2014, 2021 |

STARS com parâmetros primários (l=5, α=0.05) detecta 2004/2006 → consistente com fronteira ~2005/2006. Com α=0.01 (mais rigoroso), nada detecta.

## Intensity Analysis (Pipeline #31)

### Diagnóstico P2 vs P3

**Pergunta**: a fronteira 2005/2006 é justificável pela taxa de mudança, ou P2 e P3 são indistinguíveis?

| Comparação | Ratio | Mann-Whitney p | Significativo? |
|-----------|:-----:|:--------------:|:--------------:|
| P2 vs P3 (taxa total) | 1.25 | 0.060 | Marginal (n=4) |
| P2 sem 2004 vs P3 | 1.13 | 0.189 | Não |
| P2 vs P3 (veg_nat perda) | 1.69 | 0.0008 | Sim (***) |
| P2 vs P3 (pastagem) | 1.06 | 0.871 | Não |
| P2 vs P3 (agricultura) | 0.98 | 0.956 | Não |

**Efeito de 2004**: taxa 0.0179 (pico da série inteira). Removendo 2004, P2 vs P3 perde significância (p=0.189).

**Bootstrap (10.000 reamostragens)**:
- IC 95% para diferença P2-P3 (taxa total): [0.0007, 0.0055] → **não contém zero**
- IC 95% sem 2004: [0.0004, 0.0025] → **não contém zero**
- IC 95% para diferença P2-P3 (veg_nat perda): [0.0042, 0.0077] → **claramente não contém zero**

**Teste de 3 vs 4 períodos**:
- Kruskal-Wallis 3 períodos (P1 | P2+P3 | P4): H=20.26, p=0.00004
- Kruskal-Wallis 4 períodos (P1 | P2 | P3 | P4): H=22.57, p=0.00005
- Comparações par-a-par (Bonferroni): I vs III ***, II vs III NS, I vs IV **, III vs IV **

**Sensibilidade da fronteira** (variação do ponto de corte):

| Corte | n_P2 | n_P3 | média_P2 | média_P3 | ratio | MW p | t p |
|:-----:|:----:|:----:|:--------:|:--------:|:-----:|:----:|:---:|
| 2003 | 2 | 16 | 0.0124 | 0.0116 | 1.07 | 0.47 | 0.67 |
| 2004 | 3 | 15 | 0.0142 | 0.0112 | 1.27 | 0.10 | 0.04 |
| **2005** | **4** | **14** | **0.0139** | **0.0111** | **1.26** | **0.046** | **0.03** |
| 2006 | 5 | 13 | 0.0132 | 0.0111 | 1.19 | 0.12 | 0.10 |
| 2007 | 6 | 12 | 0.0127 | 0.0112 | 1.13 | 0.25 | 0.22 |

O resultado muda de significativo para não-significativo dependendo de onde se corta (2004 significativo com t-test mas não Mann-Whitney; 2005 significativo com ambos; 2006 já não significativo).

### Poder estatístico com n=4

Simulação com 10.000 réplicas:
- FPR nominal α=0.05: observado 0.044 (correto)
- **Poder para detectar ratio 1.25 (d≈1.5) com n=4**: 0.63
- Poder com n=7: 0.83

Com apenas 4 anos em P2, o poder estatístico é limitado (63%). O resultado borderline (p=0.06) é esperado mesmo se a diferença é real.

### Transições-chave (intensidade anual por período)

| Transição | P1 (85-00) | P2 (01-19) | P3 (20-24) |
|-----------|:----------:|:----------:|:----------:|
| pasto→agric (/a) | 0.0005 | 0.0010 | 0.0003 |
| pasto→veg (/a) | 0.0002 | 0.0005 | 0.0011 |
| veg→pasto (/a) | 0.0011 | 0.0013 | 0.0016 |
| veg→agric (/a) | 0.0000 | 0.0001 | 0.0000 |

Em P2 (2001-2019), a conversão pasto→agric é 2x mais intensa que em P1, e a regeneração pasto→veg_nat começa a ganhar importância relativa. P3 (2020-2024) se distingue pela regeneração (pasto→veg 0.11%/a, maior que qualquer período anterior) e pela retração da agricultura.

### Intensidade por categoria

| Categoria | Período | Perda (/a) | Ganho (/a) | Perda/uniform | Ganho/uniform |
|-----------|:--------:|:----------:|:----------:|:-------------:|:------------:|
| veg_nat | P1 (85-00) | 0.0012 | 0.0001 | 1.15 | 0.12 |
| veg_nat | P2 (01-05) | 0.0037 | 0.0005 | **1.05** | 0.16 |
| veg_nat | P2 (06-19) | 0.0007 | 0.0002 | 0.78 | 0.19 |
| veg_nat | P3 (20-24) | 0.0019 | 0.0005 | **1.20** | **0.32** |
| pastagem | P1 (85-00) | 0.0008 | 0.0006 | 0.74 | 0.59 |
| pastagem | P2 (01-05) | 0.0035 | 0.0016 | 0.99 | 0.46 |
| pastagem | P2 (06-19) | 0.0010 | 0.0004 | **1.17** | 0.42 |
| pastagem | P3 (20-24) | 0.0017 | 0.0007 | 1.08 | 0.46 |

Nota: P2 (01-05) e P2 (06-19) referem-se às sub-fases dentro do período 2001-2019. A sub-fase 2001-05 exibe perda acelerada de vegetação natural (0.37%/a vs 0.07%/a, ratio 5.3x) e conversão pasto→agric 4x mais intensa que 2006-19, mas a taxa total de mudança não difere significativamente (p=0.060).

## Periodização final

Com base na triangulação, verificações e Intensity Analysis:

| Período | Anos | Título | Fronteira | Evidência |
|---------|------|--------|-----------|-----------|
| P1 | 1985-2000 | Pastagem como herança | — | Herança POLOCENTRO/PRODECER |
| P2 | 2001-2019 | Expansão e intensificação | ~2001 | sup-F F=62.2 + KL/TV pico 2003 ✓ |
| P3 | 2020-2024 | Conversão seletiva | ~2020 | sup-F F=21.5 + KL/TV pico 2018-2020 ✓ |

### Sub-fase 2001-2005 dentro de P2

A sub-fase 2001-2005 exibe perda acelerada de vegetação natural (0.37%/a vs 0.07%/a em 2006-19, p=0.0008) e conversão pasto→agric 4x mais intensa. No entanto, esta fronteira **não é detectada pelo método primário** (sup-F multivariado vê 2001-2020 como platô contínuo) e é **sensível ao ponto de corte** (significativa em 2005, marginal em 2004, NS em 2006). A taxa total de mudança não difere significativamente entre as sub-fases (Mann-Whitney p=0.060, poder=0.63 com n=4). Por estas razões, optou-se por 3 períodos em vez de 4, documentando a sub-fase como nota metodológica.

STARS detecta shifts em 2004 (pastagem, agricultura) e 2006 (vegetação natural) com l=5, α=0.05. KL/TV mostra pico local em 2003. Intensity Analysis por categoria confirma que a diferença é composicional (perda de veg_nat), não de taxa total.

### Fronteiras não confirmadas

- **1991**: Instável no sup-F (desloca 1989-1993 com min_size), não detectada por STARS ou KL/TV. Provavelmente efeito de borda ou ruído. Não incluída como fronteira de período.
- **2014**: Só detectada por STARS na série de agricultura com α=0.05. Não confirmada por outros métodos. Não incluída.

## Tipologia dos marcos (independente dos atos)

| Marco | Quebra em GO? | GO-específico? | DiD robusto? | Categoria |
|-------|:-------------:|:--------------:|:-------------:|:---------:|
| 1985 | N/A | N/A | N/A | C |
| 1994 Plano Real | Nenhuma em 1994 (lag→1998) | Não | Parcial (janela 1995) | B |
| 1996 Lei Kandir | veg_nat 1998 (±2a) | **Sim** | **Sim** | **A** |
| 2002 Crédito e demanda chinesa | past 2001 (±1a) | Não (cerrado-amplo) | Não | B |
| 2003 Boom de commodities | veg_nat 2005 (±2a) | Não (cerrado-amplo) | Não | B |
| 2012 Código Florestal | **Nenhuma** | **Não** | **Não** | B |
| 2018 Reorganização de mercado | agric 2018, past 2020 | Não (cerrado-amplo) | Não | B |
| 2024 | N/A | N/A | N/A | C |

- **A (Causal)**: quebra estrutural GO-específica + DiD robusto. Apenas Lei Kandir (1996).
- **B (Narrativo)**: evento institucionalmente significativo; evidência cerrado-amplo ou sem quebra. Cinco marcos.
- **C (Fronteira)**: limites da série, sem pretensão causal. Dois marcos (1985, 2024).

## Limitações

1. **N=39 observações**: poder estatístico limitado, especialmente para o período P2 (4 anos). Quebras de pequena magnitude podem não ser detectadas.
2. **sup-F não detecta 2005/2006**: o método primário vê 2001-2020 como regime contínuo. A fronteira P2/P3 repousa em métodos de sensibilidade.
3. **KL monotonicamente crescente**: não discrimina anos de fronteira específicos. É informativa sobre direção (mais diferente de 1985 ao longo do tempo), não sobre localização.
4. **STARS sensível a α**: com α=0.01, nada detecta; com α=0.10, detecta ruído. Os shifts em 2004/2006 requerem α=0.05.
5. **2004 é outlier**: a taxa de mudança 2003→2004 (0.0179) é o pico da série inteira. P2 sem 2004 perde significância vs P3 (p=0.189).
6. **p-valores não corrigidos**: os testes sup-F usam F bruto, sem correção para múltiplos testes (Andrews 1993, Hansen 1997). A significância absoluta deve ser lida com cautela.
7. **Binary segmentation é greedy**: não garante ótimo global como Bai-Perron clássico. Robusto para até 3 quebras em N=40.
8. **Sem teste formal de coincidência GO×TO**: as coincidências entre séries são contadas por proximidade temporal, sem teste de causa comum.

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `outputs/correlacoes/quebras_multivariadas_go.csv` | 3 quebras multivariadas (ano, F, segmentos) |
| `outputs/correlacoes/stars_go.csv` | Shifts STARS por série |
| `outputs/correlacoes/transicoes_kl_go.csv` | KL divergência ano-a-ano vs 1985 |
| `outputs/correlacoes/intensity_taxas_anuais.csv` | Taxa anual de mudança por par de anos |
| `outputs/correlacoes/intensity_categorias.csv` | Intensidade por categoria e período |
| `outputs/correlacoes/intensity_transicoes.csv` | Intensidade por transição e período |
| `outputs/correlacoes/figuras_quebras_multivariadas.png` | 3 séries com quebras detectadas |
| `outputs/correlacoes/figuras_stars_go.png` | 3 séries com shifts STARS |
| `outputs/correlacoes/figuras_transicoes_kl.png` | KL e TV ao longo do tempo |

## Como rodar

```bash
# Triangulação (3 métodos)
python scripts/periodizacao_multivariada.py   # #29a
python scripts/periodizacao_stars.py           # #29b
python scripts/periodizacao_transicoes.py      # #29c

# Verificação de sanidade
python scripts/verificacao_periodizacao.py     # #30

# Intensity Analysis
python scripts/intensity_analysis.py           # #31

# Verificação da Intensity Analysis
python scripts/verificacao_intensity.py         # #31-sanidade
```

Pré-requisitos: `taxas_lulc_goias.csv` (#17), `conversao_bruta_goias.csv` (#19), `to_uf_lulc.csv` (#23). Não usa GEE.

## Decisões de implementação

- **3 períodos, não 4**: a fronteira 2005/2006 não é confirmada pelo método primário (sup-F multivariado vê 2001-2020 como platô contínuo). A diferença composicional é real (perda de veg_nat p=0.0008), mas a taxa total não difere (p=0.060) e a fronteira é sensível ao ponto de corte. Optou-se por 3 períodos, documentando a sub-fase 2001-05 como nota metodológica.
- **Código Florestal (2012)**: cai dentro de P2 (2001-2019) sem efeito mensurável — ausência de quebra é o achado.
- **Tipologia A/B/C dos marcos**: independente dos atos. Fraqueza de marco não afeta ato.
- **Config centralizada**: todos os scripts importam de `config_periodos.py`. Não há cópias independentes de ATOS ou MARCOS.