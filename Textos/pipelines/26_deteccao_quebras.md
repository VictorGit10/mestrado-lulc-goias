# Pipeline #26 — Detecção de quebras estruturais (Bai-Perron / Binary Segmentation)

**Script**: `scripts/deteccao_quebras.py`
**Status**: ✅ executado (2026-05-13)
**Depende de**: #17 (`taxas_lulc_goias.csv`), #23 (cache `to_uf_lulc.csv`)

> **Nota de contexto (2026-05-20):** Este pipeline foi um passo intermediário para a triangulação data-driven (#29). As quebras detectadas alimentaram o sup-F multivariado e a verificação de sanidade (#30). A classificação dos marcos em GO-específico / cerrado-amplo / sem evidência pertencia ao paradigma anterior (marcos como unidades analíticas). Na periodização final, os marcos são referências narrativas dentro dos atos — a tipologia A/B/C (#29) reclassificou os marcos por nível de evidência, e o enquadramento atual os trata como contexto institucional, não como variáveis causais testáveis independentemente.

## Motivação

O DiD piecewise (#23) testa apenas 4 marcos pré-definidos, sofrendo de viés
de confirmação: se o pesquisador só procura efeito onde *espera* encontrar,
deixa de detectar quebras inesperadas e gera atribuição circular (DiD em
2018 "confirma" Cerrado Manifesto porque o pesquisador escolheu 2018 = CM).

Esta pipeline inverte a lógica:

1. Detecta quebras estruturais data-driven em Δ veg_nat, Δ past, Δ agric
   para GO e TO.
2. Cruza os anos de quebra com os 8 marcos teóricos da dissertação.
3. Classifica cada marco como:
   - **GO-específico** (quebra em GO sem quebra em TO no mesmo ano ±2)
     → evidência genuína de algo único a GO.
   - **Cerrado-amplo** (quebra em GO e TO simultânea)
     → fenômeno bioma-amplo, não atribuível a marco GO-específico.
   - **Só TO** ou **Sem evidência** → marco simbólico/regulatório sem
     impacto mensurável em LULC.

## Especificação

Quandt-Andrews sup-F test para quebra única de média:

    H0: Δy_t = μ + ε_t
    H1: Δy_t = μ_1·I(t<τ) + μ_2·I(t≥τ) + ε_t
    sup-F = max_τ F(τ),  τ ∈ [min_size, n-min_size]

Múltiplas quebras via **binary segmentation** com parada por threshold
F > 5,0 e máximo 3 quebras por série. `min_size = 5` (5 anos por segmento).

Tolerância para coincidência marco × quebra: ±2 anos.

## Resultados — quebras detectadas (15 quebras em 6 séries)

| UF | Classe | Quebra | F | p | Δ média (Mha/ano) | Marco próximo | Dist | Coincide? |
|---|---|---:|---:|---:|---:|---|---:|:-:|
| GO | veg_nat | **1998** | 86,6 | <0,001 | +0,22 | 1996 Lei Kandir | 2a | ✓ |
| GO | veg_nat | **2005** | 80,4 | <0,001 | +0,10 | 2003 Boom commodities | 2a | ✓ |
| GO | pastagem | 1991 | 15,6 | 0,002 | −0,21 | 1994 Real | 3a | ✗ |
| GO | pastagem | **2001** | 85,7 | <0,001 | −0,36 | 2002 Plano Safra | 1a | ✓ |
| GO | pastagem | **2020** | 44,9 | <0,001 | −0,20 | 2018 C. Manifesto | 2a | ✓ |
| GO | agric | **2018** | 12,3 | 0,001 | −0,10 | 2018 C. Manifesto | 0a | ✓ |
| TO | veg_nat | **1993** | 6,2 | 0,023 | +0,04 | 1994 Real | 1a | ✓ |
| TO | veg_nat | **2000** | 7,1 | 0,022 | −0,03 | 2002 Plano Safra | 2a | ✓ |
| TO | veg_nat | 2006 | 10,6 | 0,003 | +0,05 | 2003 Boom | 3a | ✗ |
| TO | pastagem | 1991 | 18,5 | 0,001 | −0,13 | 1994 Real | 3a | ✗ |
| TO | pastagem | **2005** | 70,7 | <0,001 | −0,20 | 2003 Boom | 2a | ✓ |
| TO | pastagem | **2016** | 36,1 | <0,001 | −0,11 | 2018 C. Manifesto | 2a | ✓ |
| TO | agric | 1999 | 59,4 | <0,001 | +0,01 | 1996 Kandir | 3a | ✗ |
| TO | agric | **2004** | 22,0 | <0,001 | +0,05 | 2003 Boom | 1a | ✓ |
| TO | agric | **2020** | 10,3 | 0,005 | −0,06 | 2018 C. Manifesto | 2a | ✓ |

## Marcos teóricos × evidência empírica

| Marco | n quebras GO | n quebras TO | Leitura |
|---|:-:|:-:|---|
| 1994 Plano Real | 0 | 1 (veg_nat) | **Só TO** — Real não gera quebra em GO |
| 1996 Lei Kandir | 1 (veg_nat) | 0 | **GO-específico** — desonera ICMS exportação puxa GO |
| 2002 Plano Safra | 1 (pastagem) | 1 (veg_nat) | **Cerrado-amplo** |
| 2003 Boom commodities | 1 (veg_nat) | 2 (agric, past) | **Cerrado-amplo** |
| **2012 Código Florestal** | **0** | **0** | **Sem evidência empírica** ⚠ |
| 2018 Cerrado Manifesto | 2 (agric, past) | 2 (agric, past) | **Cerrado-amplo** ⚠ |

## Quebras data-driven SEM marco teórico próximo

- **1991** (GO pastagem F=15,6; TO pastagem F=18,5): inflexão pré-Real,
  possivelmente fim do ciclo POLOCENTRO/PRODECER ou efeito Plano Collor.
- **1999** (TO agricultura F=59,4): coincide com flexibilização cambial
  (regime de câmbio flutuante, jan/1999). Hipótese a investigar.
- **2006** (TO veg_nat F=10,6): coincide com a Moratória da Soja Amazônia.
  TO tem ~8% Amazônia. Hipótese plausível, ausente em GO (100% Cerrado).

## Implicações para a dissertação

1. **Marco 2012 (Código Florestal) é regulatório, não causal mensurável.**
   Nem GO nem TO apresentam quebra estrutural ±2 anos. O efeito +0,30 do
   DiD vs MT capturou divergência MT, não quebra em GO. Atualizar marcos.json
   e textos para reconhecer o caráter simbólico-regulatório.

2. **Marco 2018 é real mas cerrado-amplo.**
   Quebra em GO e TO simultânea desautoriza atribuição exclusiva ao Cerrado
   Manifesto. Driver provável: combinação de recuperação macro pós-2016,
   ciclo de preços e pressão de cadeia produtiva afetando todo o Cerrado.

3. **A inflexão de veg. natural em GO é em 1998, não 1994.**
   A literatura tende a creditar Plano Real (1994). Os dados de GO mostram
   inflexão 4 anos depois, alinhada à Lei Kandir (1996). Suporta narrativa
   "tributação > monetária" para LULC.

4. **Achado novo data-driven**: 2006 em TO sugere efeito da Moratória da
   Soja Amazônia chegando a TO via os ~8% de bioma Amazônia. Vale comentar
   na seção de limitações do controle.

## Limitações

- **p-valor F bruto**, não corrigido para múltiplos testes via Andrews
  (1993) ou Hansen (1997). Magnitude relativa entre séries é confiável; a
  significância absoluta deve ser lida com cautela.
- **N=39 (deltas anuais)** → poder estatístico moderado. Quebras de
  pequena magnitude podem não atingir F > 5,0.
- **Binary segmentation é greedy** — não garante optimum global como
  Bai-Perron clássico. Robusto para até 3 quebras em N=40 (validado em
  literatura de changepoint detection).
- **Sem teste de validade simultâneo entre séries** — coincidências GO×TO
  são contadas por proximidade temporal, sem teste formal de causa comum.

## Saídas

| Arquivo | Conteúdo |
|---|---|
| `outputs/correlacoes/quebras_resultados.csv` | 15 quebras com F, p, segmento, Δmédia, marco próximo |
| `outputs/correlacoes/quebras_vs_marcos.csv` | 6 marcos × leitura (GO-específico / Cerrado-amplo / Só TO / Sem evidência) |
| `outputs/correlacoes/quebras_*.png` | 6 figuras (3 classes × 2 UFs) com série, marcos teóricos cinza, quebras detectadas vermelho/laranja |

## Como rodar

```bash
python scripts/deteccao_quebras.py
```

Pré-requisitos: `taxas_lulc_goias.csv` (pipeline #17), `to_uf_lulc.csv`
(pipeline #23 com `--download`). Não usa GEE.

## Decisões de implementação

- **Sem `ruptures`**: pacote não compila no Py 3.14 (sem wheels). Implementação
  manual com numpy + scipy.stats é equivalente para detecção de quebras de
  média em série anual de N=40 e evita dependência problemática.
- **min_size = 5**: garante 5 anos por segmento, evitando quebras
  artefatuais em regiões esparsas da série.
- **F_THRESHOLD = 5.0**: corresponde a p ≈ 0,03 para n=40, df=(1, 37).
  Suficientemente rigoroso para evitar over-detection mas permite captar
  quebras de magnitude moderada.
- **TOL_MARCO = 2 anos**: tolerância razoável dado que efeitos regulatórios
  podem ter defasagem de implementação (Cadastro Ambiental Rural só
  começou efetivamente em 2014, dois anos após o Código Florestal).
