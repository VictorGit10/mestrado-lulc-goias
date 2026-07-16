# Pipeline #40B — Calcário + orientação técnica no arcabouço das duas lógicas

**Script**: `scripts/duas_logicas_calcario_orientacao.py`
**Quando foi feito**: 2026-07-16. Extensão do #40 que consome as covariáveis novas do Censo 2017 (tabela 6850, coletadas em jul/2026 — calcário e orientação técnica).
**Depende de**: #40 (reusa integralmente `carregar`/`agregar_mix`/`_partial_corr`/`_partial_corr_multi`), #28 (idade da pastagem), coletas triviais 6850.
**Outputs**:
- `data/processed/duas_logicas_calcario_orientacao.csv` — tabela D14 (bruto → parcial|lat → parcial|lat+lon).
- `outputs/duas_logicas/calcario_orientacao.png`.

---

## Pergunta de pesquisa

O #40 estabeleceu que a segregação Rotação(jovem, Sul) × Oportunístico(antigo, Norte) é real, mas que **nenhuma covariável transversal isola mecanismo próprio** — tudo co-varia na aptidão latitudinal (D14). As duas variáveis novas do Censo 2017 permitem **testar a generalidade** dessa lição com dois proxies de natureza diferente do no-till:

- **Calcário** (% estab. que corrigem o pH) = proxy **direto de intensificação** — corrigir o solo ácido do Cerrado é o ato que o torna cultivável.
- **Orientação técnica** (% estab. com assistência) = proxy de **capacitação/instituição**, com a composição por origem (cooperativas × governo).

Se ambas se comportarem como o no-till (descem ao Sul mas somem sob o gradiente 2D), a D14 se generaliza de "estrutura de manejo" para "intensificação" e "instituição".

---

## Achados

### 1. As duas descem ao Sul com a lógica jovem — até mais forte que o no-till
Correlação da covariável com a latitude do centróide (− = desce ao Sul):

| Covariável | r(latitude) |
|---|---|
| **Orientação técnica** | **−0,54** |
| **Calcário** | **−0,43** |
| Plantio direto (ref. #40) | −0,37 |
| Adubação (ref.) | −0,21 |

Calcário e orientação são marcadores nítidos do Sul comercial mecanizado — mais nítidos que o no-till.

### 2. Mas nenhum par sobrevive ao controle do gradiente 2D (D14 generalizada)
Cross-check com os desfechos da lógica (n=88 munis), bruto → parcial|lat → parcial|lat+lon:

| Covariável × desfecho | bruto | \|lat | \|lat+lon |
|---|---|---|---|
| Calcário × idade mediana | −0,30 | −0,09 (ns) | −0,04 (ns) |
| Calcário × índice jovem | +0,19 | −0,03 (ns) | −0,09 (ns) |
| Orientação × idade mediana | −0,22 | +0,10 (ns) | +0,09 (ns) |
| Orientação × % rotação | +0,23 | −0,14 (ns) | −0,14 (ns) |

**Nenhum** dos 8 pares das covariáveis novas sobrevive — exatamente como o no-till no #40 (reproduzido aqui como referência: −0,37 → −0,22|lat → −0,15|lat+lon, ns). A intensificação (calcário) e a instituição (orientação) **co-localizam na aptidão latitudinal; não isolam efeito próprio** sobre a idade da pastagem. **A D14 vale para as três famílias de proxy** (manejo, insumo, extensão).

### 3. Textura institucional nova — a ORIGEM da orientação é ela mesma Sul→Norte
Composição da assistência técnica entre os estabelecimentos que a recebem, vs latitude:

- **Cooperativas**: r(lat) = **−0,40** — orientação cooperativa/comercial concentra-se no **Sul**.
- **Governo** (extensão pública): r(lat) = **+0,53** — assistência pública domina no **Norte**.

Os "dois Goiáses" têm **dois modelos de extensão**: comercial-cooperativo no núcleo agrícola do Sul, público na fronteira do Norte. É textura descritiva (não causal), coerente com todo o eixo Sul→Norte.

---

## Veredito

Confirma e **generaliza a D14**: em cross-section estadual, calcário e orientação técnica são mais dois marcadores do gradiente de aptidão — descem ao Sul com a lógica jovem, mas o efeito próprio evapora ao controlar lat+lon. O achado robusto do #40 permanece **a geografia da bimodalidade**, não um driver estrutural. Contribuição desta passada: (a) fecha que a lição do no-till não era peculiaridade do no-till; (b) revela o **gradiente institucional da extensão** (cooperativa-Sul × pública-Norte), um espelho institucional do "dois Goiáses". As covariáveis novas (Q2 da auditoria de uso do painel) ganham, assim, seu primeiro uso analítico.

**Honestidade**: cross-section 2017 estático (sem uso longitudinal); n=88 munis confiáveis; a composição da orientação é descritiva. Não abre perna causal — reforça a existente.
