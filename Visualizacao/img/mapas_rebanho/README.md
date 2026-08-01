# Mapas do rebanho bovino por AMC — Goias

Esta pasta reune os mapas coropleticos gerados a partir do painel de
Areas Minimas Comparaveis (AMC) de Goias (D11). Todos usam a malha
`data/processed/amc_goias.gpkg` e o painel `data/processed/painel_amc_goias.parquet`.

## Arquivos

### 1. `ganho_bovino_pasto_1985_2024_abs.png`
**Script:** `Visualizacao/scripts/gerar_mapa_ganho_bovino_pasto.py`

Dois paineis lado a lado com o **ganho absoluto 1985 -> 2024** por AMC:

- A) Rebanho bovino (cabeças)
- B) Pastagem (ha)

**Destaques numericos:**

| Grandeza | Minimo | Maximo |
|---|---:|---:|
| Δ Rebanho | -313.100 cab (Quirinopolis) | +910.495 cab (Nova Crixas) |
| Δ Pastagem | -356.404 ha (Rio Verde) | +484.111 ha (Nova Crixas) |

Entre as 76 AMCs que ganharam pasto, a mediana de intensificacao marginal foi
**2,13 cabeças novas por hectare de pasto novo** (P10=0,02; P90=7,89).

### 2. `ganho_bovino_pasto_veg_1985_2024_abs.png`
**Script:** `Visualizacao/scripts/gerar_mapa_ganho_bovino_pasto_veg.py`

Versao ampliada com **tres paineis** + um **scatter de vies de tamanho**:

- A) Ganho do rebanho bovino (cab)
- B) Ganho da pastagem (ha)
- C) Ganho/perda de vegetacao nativa (ha) — soma de floresta nativa,
   formacao savanica e campo nativo do MapBiomas
- D) Scatter Δ rebanho vs. area da AMC, destacando Nova Crixas

**Totais do estado (1985 -> 2024):**

| Grandeza | Δ total |
|---|---:|
| Area de Goias | 34,17 milhoes ha |
| Rebanho bovino | +7.302.470 cab |
| Pastagem | +1.004.837 ha |
| Vegetacao nativa | **-5.548.015 ha** |
| Agricultura total | +4.405.001 ha |
| Soja | +4.131.376 ha |

**Top 5 perdas de vegetacao nativa:**

| AMC | Δ vegetacao nativa (ha) | Δ pastagem (ha) | Δ agricultura (ha) | Area da AMC (Mha) |
|---|---:|---:|---:|---:|
| Nova Crixas | -408.434 | +484.111 | +43.455 | 1,53 |
| Caiaponia | -331.306 | +161.823 | +140.276 | 1,32 |
| Mineiros | -289.031 | +50.283 | +235.011 | 1,47 |
| Niquelandia | -273.964 | +95.540 | +78.830 | 1,13 |
| Cristalina | -259.033 | +2.512 | +232.235 | 0,62 |

**Top 5 perdas de pastagem (Sul/sudoeste):**

| AMC | Δ pastagem (ha) | Δ vegetacao nativa (ha) | Δ agricultura (ha) | Δ soja (ha) | Δ rebanho (cab) |
|---|---:|---:|---:|---:|---:|
| Rio Verde | -356.404 | -55.649 | +432.675 | +519.134 | -200.715 |
| Jatai | -185.208 | -81.164 | +281.106 | +298.187 | -17.000 |
| Quirinopolis | -182.577 | -11.778 | +132.409 | +49.227 | -313.100 |
| Itumbiara | -134.246 | -4.537 | +92.236 | +93.142 | -177.300 |
| Parauna | -114.798 | -30.967 | +135.315 | +155.705 | -67.141 |

## Cuidados de interpretacao

### 1. Vies de area
O modo "absoluto" reflete o tamanho da AMC. **Nova Crixas e uma das maiores AMCs
de Goias (1,53 Mha)**, o que explica parte do "ganho absurdo" de rebanho no mapa.
Para comparacao cross-sectional livre desse vies, gere a versao percentual
(`MODO='pct'` no script `gerar_mapa_ganho_bovino_pasto.py`).

### 2. Nao e iLUC comprovado
A figura mostra uma **substituicao espacial observada**: pastagem cede lugar a
lavoura no Sul, enquanto rebanho e pastagem crescem no Norte e a vegetacao
nativa recua em ambas as regioes. Isso e **consistente** com a narrativa do iLUC,
mas **nao comprova** iLUC. iLUC exigiria demonstrar deslocamento causal: a
expansao agricola no Sul *forcou* a conversao de vegetacao nativa em pasto no
Norte. A analise estatistica dos 36 canais de iLUC testados nao encontrou essa
assinatura (0/36).

### 3. Reorganizacao sob drives comuns
O padrao espacial reflete vantagem comparativa regional (Sul = grãos, Norte =
pecuaria extensiva) interagindo com drives macroeconomicos comuns (câmbio,
preco de commodity, credito). Nao e evidencia de que bois "se mudaram" do Sul
para o Norte. Ver pipeline #32/#33/#34/#37/#38 e a memoria
`project_centro_massa.md`.

### 4. Frases proibidas
Nao usar estas frases com base apenas nestes mapas:

- "iLUC comprovado"
- "soja no Sul deslocou gado para a fronteira Norte"
- "expansao do rebanho desmatou o Norte"

Frase segura:

> "A distribuicao espacial do ganho de rebanho e pastagem e consistente com uma
> especializacao regional — lavoura no Sul e pecuaria extensiva no Norte —, mas
> nao permite distinguir entre iLUC e resposta independente a drives
> macroeconomicos comuns."

## Como regenerar

```bash
python Visualizacao/scripts/gerar_mapa_ganho_bovino_pasto.py
python Visualizacao/scripts/gerar_mapa_ganho_bovino_pasto_veg.py
```

Para a versao percentual (livre de vies de area), edite a constante `MODO`
no primeiro script:

```python
MODO = "pct"  # 'abs' | 'pct'
```

### 3. `intensificacao_extensao_amc.png`
**Script:** `Visualizacao/scripts/gerar_mapa_produtividade_amc.py`

Versao espacial da decomposicao **intensificacao vs. extensao**, com quatro
paineis:

- **A)** Delta da produtividade da soja (t/ha) por AMC: 1988 -> 2024.
- **B)** Delta da lotacao bovina (cab/ha de pasto) por AMC: 1985 -> 2024.
- **C)** Delta da area plantada de soja (ha) por AMC: 1988 -> 2024.
- **D)** Scatter: delta produtividade da soja x delta area de soja, com cores
   indicando a delta da lotacao bovina.

**Resumo espacial:**

| Grandeza | Media | Minimo | Maximo |
|---|---:|---:|---:|
| Delta produtividade soja (t/ha) | +1,43 | +0,05 | +2,80 |
| Delta lotacao bovina (cab/ha) | +0,63 | -4,81 | +5,31 |
| Delta area de soja (ha) | +45.113 | -790 | +436.200 |

**Correlacoes (AMCs com dados de soja e bovino):**

- delta produtividade soja x delta area soja: **r = 0,10** (quase nulo)
- delta produtividade soja x delta lotacao bovina: **r = 0,30** (fraco)
- delta area soja x delta lotacao bovina: **r = 0,15** (quase nulo)

**Destaques:**

- **Maior extensao de soja:** Rio Verde (+436.200 ha de soja, produtividade +2,1 t/ha).
- **Maior ganho de produtividade da soja:** Sao Simao (+2,8 t/ha, area praticamente estavel).
- **Maior intensificacao bovina:** Santa Helena de Goias (lotação +5,3 cab/ha) e Panama (+5,2 cab/ha).
- **Maior perda de lotacao bovina:** Cavalcante (-4,8 cab/ha), Campos Belos (-4,6 cab/ha), Minacu (-4,2 cab/ha) — areas do entorno do Parque Nacional da Chapada dos Veadeiros e do Norte de Goias.

**Interpretacao:**

- A soja cresceu principalmente por **extensao** (mais hectares) — veja o painel C
  dominado por azuis/verdes, e o scatter mostra que ganhos de area podem ocorrer
  com ganhos de produtividade pequenos (Rio Verde) ou grandes (Cristalina).
- A pecuaria intensificou em muitos lugares, mas nao uniformemente: o Norte/Centro-Oeste
  ganhou lotacao, enquanto areas de entorno de unidades de conservacao e do Planalto
  perderam.
- A correlacao quase nula entre delta produtividade da soja e delta area de soja
  reforca que **a produtividade nao foi o motor do aumento da producao**: o volume
  veio de expansao territorial.

**Cuidado:** o delta da produtividade da soja usa a **area plantada SIDRA/PAM** como
 denominador. Comparar com LULC MapBiomas (`lulc_soja_ha`) daria uma produtividade
 aparente diferente (ver memoria `project_deriva_mosaico.md`).

## Como regenerar (todos os mapas)

```bash
cd Visualizacao
python scripts/gerar_mapa_ganho_bovino_pasto.py
python scripts/gerar_mapa_ganho_bovino_pasto_veg.py
python scripts/gerar_mapa_produtividade_amc.py
```

## Fontes

- Malha AMC: `data/processed/amc_goias.gpkg` (EPSG:5880)
- Painel longitudinal: `data/processed/painel_amc_goias.parquet`
- LULC e rebanho: MapBiomas (coleçao 10) e SIDRA/IBGE, reconciliados no
  pipeline D11 (AMC).
