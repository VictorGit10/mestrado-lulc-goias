# Pipeline #45 — A infraestrutura exportadora SEGUE ou LIDERA a expansão LULC?

**Script**: `scripts/analise_trase_lulc.py`
**Quando foi feito**: 2026-07-13. Ativa o **Eixo A** do backlog (as 8 colunas Trase do #27, até aqui sem análise).
**Depende de**: #27 (`painel_trase.csv`, cadeia exportadora Trase.earth), #16 (`painel_unificado.parquet`, LULC/SIDRA/rebanho/abate). Reusa CCF/Granger do #34 e o padrão PanelOLS do #22; aplica D7 (diferenças) e **D16** (cautela com lead-lag de séries integradas).
**Outputs**:
- `data/processed/trase_lulc_leadlag_agregado.csv` — Bloco A: CCF (pico) + Granger (2 direções) + ADF/KPSS por par.
- `data/processed/trase_lulc_painel.csv` — Bloco B: cross-lagged em painel (β padronizado), 3 termos por par.
- `outputs/trase_lulc/leadlag_agregado.png`, `painel_direcoes.png`.

---

## Pergunta de pesquisa

O Pipeline #27 integrou a cadeia **exportadora** da Trase.earth (soja 2004–2022, boi 2011–2023 sem 2018) ao painel — volume/valor escoado, nº de tradings/frigoríficos, nº de hubs logísticos — mas **nunca rodou análise**. A pergunta do Eixo A:

> A presença de infraestrutura exportadora **antecede** a expansão do uso da terra (a infra "puxa" a lavoura/pasto — seria um vetor de fronteira), ou **segue** a expansão (a infra chega onde a produção já se instalou)?

É o complemento do canal de crédito do #22 (SICOR → retração de pastagem): o canal de **infraestrutura agroindustrial exportadora**.

---

## O que faz (dois níveis, com a disciplina do #42/D16)

- **Bloco A — Lead-lag AGREGADO (série estadual GO, anual).** CCF defasada + Granger nas duas direções, em 1as diferenças (D7). **Disciplina D16**: as séries de área/volume são suaves e integradas; o #42 provou que Granger ingênuo em 1ª diferença sobre séries integradas **fabrica precedência espúria**. Por isso o Bloco A é **diagnóstico, não inferência** — reporta ADF/KPSS de cada série e trata T≈12–18 como baixo poder. A inferência fica com o Bloco B.
- **Bloco B — Cross-lagged em PAINEL (municipal, 2-way FE — o cavalo de batalha).** Variáveis **padronizadas (z-score, padrão #38)** para tornar β comparável entre escalas (toneladas × hectares × cabeças). Por par (infra × LULC), três estimativas em painel de efeitos fixos município+ano, SE clusterizado por município:
  - `contemp` — Δlulc ~ Δinfra (co-movimento, direção-neutro);
  - `infra_lidera` — Δlulc ~ Δinfra(t−1) (infra antecede);
  - `lulc_lidera` — Δinfra ~ Δlulc(t−1) (LULC antecede).
  Usa **defasagem distribuída** (sem termo autorregressivo Y(t−1)) para evitar o viés de Nickell de um CLPM com FE — coerente com o SLX do #34.

**Pareamentos**: Trase soja × `lulc_soja_ha` (MapBiomas), `agri_soja_ha_plantada` (SIDRA), `lulc_agricultura_ha`; Trase boi × `lulc_pastagem_ha`, `pec_bovinos_cab`, `abate_bovino_cab`. A soja com fonte **satélite e censo** dá validação cruzada embutida.

---

## Achados — a infra exportadora ACOMPANHA a produção, não a antecede

### 1. Bloco A confirma o alerta da D16 (diagnóstico, não achado)
Todas as séries pareadas são **≥I(2) ou I(1)** (ADF não rejeita raiz unitária no nível). O Granger agregado é **disperso e inconsistente**: picos de CCF espalhados por lags diferentes com troca de sinal, e os poucos p<0,05 (soja hubs→lulc lag 2 p=0,004; agricultura→infra lag 1 p=0,044) **não formam padrão** e são exatamente o tipo de hit lag-1/lag-2 que a D16 diz ser espúrio em séries integradas. Ou seja: o agregado se comporta **como a D16 prevê** e não sustenta leitura causal.

### 2. Bloco B — o sinal vive no CONTEMPORÂNEO
Contagem sobre os 8 pares (painel FE, β padronizado):

| Termo | Pares com p<0,05 | Leitura |
|---|---|---|
| **co-movimento contemporâneo** | **4/8** | infra e produção se movem **no mesmo ano** |
| infra lidera (t−1) | 2/8 | β minúsculos e de sinal inconsistente |
| LULC lidera (t−1) | 1/8 | idem |

Os pares com co-movimento contemporâneo significativo são coerentes:
- **Soja SIDRA** × volume exportado: β=+0,335 (p<0,001) — a área **plantada** (censo, responsiva ano a ano) co-move forte com o escoamento; a soja MapBiomas e a agricultura LULC (mais suaves, satélite) ficam **nulas** — uma nota metodológica útil: a medida de LULC responsiva ao ciclo é a de **área plantada SIDRA**, não o estoque de pixel.
- **Boi** × volume exportado: co-move com o **abate** (β=+0,084, p<0,001, sensato — a exportação sai do abate) e **inversamente** com o rebanho em pé (β=−0,029, p<0,001, sensato — exportar puxa o rebanho para baixo).

Os termos **defasados** em ambas as direções são pequenos, sig-inconsistentes e não desenham nenhum mecanismo de liderança.

> Cautela de tamanho de efeito: dos 4/8 contemporâneos "significativos", só **dois são materiais** — soja-SIDRA (β=+0,335) e boi×abate (+0,084). Os outros dois (boi×pasto β=−0,004; boi×rebanho β=−0,029) são **triviais em magnitude**: o p<0,001 vem do N alto (~2.334 obs) e do SE minúsculo, não de um efeito grande (r²within ≈ 0,007–0,015). A leitura "co-move contemporaneamente" se sustenta na direção, mas o **peso econômico** está na soja-SIDRA e no abate; ler a contagem 4/8 como quatro co-movimentos equivalentes superestimaria os dois pares de área/rebanho.

### 3. Veredito
> Em Goiás, na janela observável, a infraestrutura **exportadora** **co-move contemporaneamente** com a produção agropecuária — **não a antecede**. Ela **acompanha** a fronteira (chega/escoa onde a produção se instala), não a **lidera** como vetor pioneiro. Isso é coerente com o veredito recorrente do projeto — **co-movimento sob forças comuns, sem precedência temporal limpa** (#34, #37, #42) — e adiciona o canal de infraestrutura ao lado do canal de crédito (#22).

---

## Como ler as figuras

### `painel_direcoes.png` — a figura-manchete
Três colunas de coeficientes por par: **co-movimento contemporâneo** (verde), **infra lidera t−1** (roxo), **LULC lidera t−1** (rosa). Os pontos cheios (p<0,05) concentram-se na coluna do **contemporâneo**; as colunas de defasagem ficam quase todas em ~0. Mostra visualmente que o sinal é de coincidência, não de liderança.

![Direções no painel](../../outputs/trase_lulc/painel_direcoes.png)

### `leadlag_agregado.png` — as séries estaduais
Infra exportadora (normalizada) × uso da terra (normalizado) para soja e boi. As curvas sobem juntas — co-movimento visível — sem defasagem clara de uma sobre a outra.

---

## Limitações honestas

- **Trase = fluxo EXPORTADOR apenas** (#27): proxy de exposição à cadeia exportadora, **não** de capacidade agroindustrial total (o abate/esmagamento para mercado interno não entra). O co-movimento com o abate é parcialmente **definicional** (a exportação é um recorte do abate).
- **Janela curta** (soja 19 anos, boi 12 sem 2018) → baixo poder, sobretudo no agregado (Bloco A). O painel recupera poder pelo N municipal, mas o T ainda é curto para defasagens longas.
- **Precedência preditiva, não causalidade** (D16 aplicada). O agregado é diagnóstico.
- **Infra medida por volume/valor/contagem de players**, não por ativos físicos instalados (silos, frigoríficos com SIF). Esse ângulo — que poderia dar liderança onde o fluxo não dá — depende de coletas futuras (CONAB SISDEP, SIGSIF/MAPA), listadas nas coletas pendentes do backlog.

---

## Conexão com a narrativa

Fecha o **Eixo A** do backlog. Reforça, por um terceiro canal (infraestrutura), o veredito de **co-evolução sem precedência** que a narrativa Sul→Norte já sustentava pelos canais de deslocamento (#34) e de drive macro (#37/#42): nenhum dos vetores testados — nem a agricultura do Sul, nem os drivers de mercado, nem a infraestrutura exportadora — **lidera temporalmente** a expansão; todos **co-movem**. A dissertação ganha o argumento de que a cadeia exportadora é **coincidente**, não pioneira — a infraestrutura segue a produção que a fronteira e o gradiente de aptidão organizam.
