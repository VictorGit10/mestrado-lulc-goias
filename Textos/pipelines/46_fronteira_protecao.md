# Pipeline #46 — A fronteira marcha para terra protegida ou desprotegida?

**Script**: `scripts/fronteira_protecao.py`
**Quando foi feito**: 2026-07-13. Adiciona ao #39 a camada de proteção que ele deixou de fora ("sem CAR/UC/PRODES").
**Depende de**: #25 (`amc_goias.gpkg`, geometria das AMC), #39 (`fronteira_estoque_convertivel.csv`, estoque convertível/AMC/ano). Coleta UCs/TIs via `geobr` (CNUC). Reusa a geografia Sul/Norte do #33/#34 e o proxy-com-teto do #39 (D13).
**Outputs**:
- `data/processed/protecao_uc_amc.csv` — Bloco A: cobertura de UC (PI/US/TI) por AMC.
- `data/processed/protecao_gap_regional.csv` — Bloco B: gap de proteção por região.
- `data/processed/protecao_temporal.csv` — Bloco C: área protegida acumulada por ano.
- `outputs/fronteira_protecao/cobertura_uc.png`, `gap_latitude.png`, `protecao_temporal.png`.

---

## Pergunta de pesquisa

O #39 mediu o "teto de oferta" de Cerrado convertível **sem** camada de proteção e mostrou que ~62% do convertível remanescente está na **faixa norte** — o destino da marcha ao norte (#32). Faltava a pergunta ambiental que dá o *stake* de conservação:

> Para onde a fronteira marcha — terra que a lei deixa converter (**desprotegida**), ou terra que deveria estar protegida (**UC / prioridade de conservação**)?

Se o convertível restante no Norte for majoritariamente **desprotegido**, a marcha ao norte é uma fronteira aberta rumo a Cerrado legalmente conversível; se estivesse sob Proteção Integral, a proteção formal seria um freio.

---

## O que faz (overlay vetorial sobre o painel AMC e o estoque do #39)

- **Bloco A — Cobertura de proteção por AMC.** UCs do CNUC (via `geobr`) recortadas em GO e intersectadas com as 166 AMCs em **EPSG:5880** (equal-area). Distingue **Proteção Integral (PI)** de **Uso Sustentável (US)** — só a PI veda a conversão; a US (ex.: APA) admite uso rural. Terras Indígenas entram como camada complementar.
- **Bloco B — O "gap de proteção" da fronteira.** Cruza a cobertura de UC com o **estoque convertível remanescente** do #39 (def. refinada, último ano = 2024). "Convertível desprotegido" = estoque × (1 − fração de PI) — quanto do convertível que resta está fora de Proteção Integral, por região e faixa de latitude.
- **Bloco C — Tempo da proteção.** O `creation_year` das UCs permite perguntar se a proteção **antecedeu** a fronteira ou chegou depois: curva de área protegida acumulada. Proteção tardia não freia a conversão já ocorrida.

---

## Achados — a fronteira marcha para Cerrado quase inteiramente desprotegido

### 1. A proteção em Goiás é pequena e dominada por Uso Sustentável
Total protegido em GO: **2,14 Mha ≈ 6,3%** do território — mas só **0,50 Mha (PI)** vedam conversão; **1,60 Mha** são Uso Sustentável (APAs) e **0,04 Mha** são TIs (negligível). Sanity check independente: os grandes blocos de PI conhecidos (Chapada dos Veadeiros ~240k ha + Emas ~132k ha + demais) somam ~0,5 Mha — bate com o calculado. A **Proteção Integral média por AMC é de 0,9%**.

### 2. 97% do Cerrado convertível remanescente está desprotegido
Do estoque convertível de 2024 (**6,56 Mha**, def. refinada), **6,35 Mha (97%)** estão **fora de Proteção Integral**. Por região:

| Região | Convertível (Mha) | % do convertível estadual | % desprotegido | PI média |
|---|---|---|---|---|
| **Norte** | 2,89 | 44% | **95%** | 2,7% |
| **Centro** | 2,49 | 38% | 99% | 0,6% |
| **Sul** | 1,19 | 18% | 98% | 0,3% |

O Norte — destino da marcha e detentor de 44% do convertível remanescente — é o **mais protegido** dos três (PI 2,7% vs 0,3% no Sul; corr(latitude, %PI) = +0,21), mas ainda assim **95% desprotegido**. A proteção formal não é, em nível nenhum, um freio material à fronteira.

> Nota sobre partições: o "~62% na faixa norte" citado do #39 (§pergunta) e este "Norte = 44%" **não se contradizem** — são recortes diferentes do mesmo estoque (2,89 Mha no Norte batem entre os dois). "Faixa norte" do #39 é o **quartil superior de latitude** (`qcut(lat, 4)`, ≈4,05 Mha), mais amplo; "Norte" aqui é a **mesorregião** (30 AMCs, 2,89 Mha). Este pipeline reporta por mesorregião.

**Robustez da manchete**: como a PI é tão pequena em toda parte, o "97% desprotegido" sobrevive ao caveat do proxy uniforme (Bloco B assume convertível distribuído uniformemente na AMC) — mesmo se o convertível estivesse **3× mais concentrado** dentro das UCs de PI, ainda seria **90% desprotegido**.

### 3. A proteção não respondeu à fronteira — ela a antecede e congelou
**89% da Proteção Integral de GO já existia em 2000** (0,45 de 0,50 Mha); ela cresceu só +0,05 Mha em 24 anos, enquanto a marcha ao norte se intensificava (Ato III, 2020–24). A PI **não** se expandiu para acompanhar a fronteira que avança para o Norte — ela ficou pequena e estática. A proteção formal não é resposta ao avanço recente.

### 4. Veredito
> A "marcha ao norte" da fronteira agropecuária (#32) se dirige a Cerrado que está **97% desprotegido** contra conversão. Goiás protege formalmente ~6% do território, mas quase tudo é **Uso Sustentável** (que admite uso rural); a **Proteção Integral** — a única que veda conversão — cobre <3% em qualquer região, congelou após 2000 e não acompanhou a fronteira. O teto de oferta do #39 é, portanto, um teto **quase exclusivamente físico/econômico** (estoque convertível esgotando no Sul, ainda aberto no Norte), **não** um teto **institucional**: a lei não está barrando a conversão do Cerrado convertível que resta. Isto adiciona à narrativa a dimensão de **conservação**: a reorganização Sul→Norte avança sobre um estoque de biodiversidade formalmente desguarnecido.

---

## Como ler as figuras

### `gap_latitude.png` — a figura-manchete
Esquerda: o Cerrado convertível remanescente por faixa de latitude, empilhando a parte sob Proteção Integral (verde, fininha) e desprotegida (laranja) — a barra é quase toda laranja em todas as faixas. Direita: % desprotegido por região (todas entre 95% e 99%).

![Gap de proteção](../../outputs/fronteira_protecao/gap_latitude.png)

### `cobertura_uc.png` — proteção ao longo do gradiente
% do território protegido por AMC contra a latitude do centroide. A Proteção Integral (verde) fica rente ao chão em quase todas as AMCs; a proteção total (cinza) sobe pontualmente onde há APAs grandes.

### `protecao_temporal.png` — quando a proteção foi criada
Área protegida acumulada (PI e US) por ano, com os atos marcados. Mostra a PI praticamente estável desde ~2000, muito antes e sem relação com a aceleração da fronteira no Ato III.

---

## Decisão metodológica nova — D17 (proteção como malha vetorial)

**"Proteção" é operacionalizada como a malha de UCs (CNUC via `geobr`), em nível VETORIAL, distinguindo Proteção Integral (veda conversão) de Uso Sustentável (admite uso rural).** Limitação, no espírito da D13: sem intersecção **pixel** do Cerrado convertível *dentro* de cada UC, aplica-se a fração protegida da AMC ao estoque convertível assumindo distribuição **uniforme** intra-AMC — logo o "convertível desprotegido" é um **proxy/teto**, não uma medida pixel-a-pixel (mostra-se robusto porque a PI é minúscula em toda parte). O refino pixel (recortar o estoque do #39 pela malha de UC no raster, via GEE) fica para a Sprint 2.

---

## Limitações honestas e validações PENDENTES

- **Overlay vetorial, não pixel** (D17). O headline sobrevive ao caveat (ver §2), mas a atribuição fina "este hectare convertível está dentro/fora de UC" exige o raster.
- **UC ≠ proteção efetiva.** A camada é o limite legal; não mede fiscalização, desmatamento ilegal dentro de UC, nem a Reserva Legal/APP prediais (que o #39 aproxima na def. `refinada_rl`).
- **PRODES Cerrado (INPE) — validação PENDENTE.** A checagem independente da série de perda de vegetação do MapBiomas contra o PRODES não entrou: a API pública de taxas do terrabrasilis não expõe tabular limpo deste ambiente. Fonte para coleta manual: `http://terrabrasilis.dpi.inpe.br/downloads/` → PRODES Cerrado, incrementos anuais 2000+.
- **Áreas Prioritárias para Conservação do Cerrado (MMA, Portaria 223/2016) — PENDENTE.** Enriqueceria o Bloco B com "prioridade de conservação" além do binário UC. Fonte: dados espaciais do MMA (`gov.br/mma`).

---

## Conexão com a narrativa

Dá ao #39 a **terceira leitura** que faltava. O #39 mostrou que o teto de oferta de Cerrado convertível é um **teto regional móvel** (fechou no Sul, aberto no Norte); o #46 mostra que esse teto é **físico, não institucional** — a fração do convertível remanescente barrada por Proteção Integral é desprezível (3% no total, ≤3% em qualquer região). A marcha ao norte encontra pela frente estoque de Cerrado que a lei deixa converter. É a ponte natural para o eixo ambiental sugerido no backlog (o **custo de carbono/biodiversidade da marcha**): as formações que recuam ao norte no #44 (campo nativo, savânica) são exatamente as menos protegidas e mais biodiversas do Cerrado.
