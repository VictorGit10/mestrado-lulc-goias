# Pipeline #40B — Calcário + orientação técnica no arcabouço das duas lógicas

**Script**: `scripts/duas_logicas_calcario_orientacao.py`
**Quando foi feito**: 2026-07-16. Extensão do #40 que consome as covariáveis novas do Censo 2017 (tabela 6850, coletadas em jul/2026 — calcário e orientação técnica).
**Depende de**: #40 (reusa integralmente `carregar`/`agregar_mix`/`_partial_corr`/`_partial_corr_multi`), #28 (idade da pastagem), coletas triviais 6850.
**Outputs**:
- `data/processed/duas_logicas_calcario_orientacao.csv` — tabela D14 (bruto → parcial|lat → parcial|lat+lon). Gerado sobre o **censo** do #28; `--fonte amostra` escreve com sufixo `_amostra`.
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
| **Orientação técnica** | **−0,49** |
| **Calcário** | **−0,40** |
| Plantio direto (ref. #40) | −0,38 |
| Adubação (ref.) | −0,24 |

Calcário e orientação são marcadores nítidos do Sul comercial mecanizado — mais nítidos que o no-till.

### 2. Mas nenhum par sobrevive ao controle do gradiente 2D (D14 generalizada)

> **Revisado em 21/jul/2026 sobre o censo do #28.** n vai de 88 a **244 municípios** — o
> corte de ≥20 px deixa de morder. **O nulo se confirma e fica muito melhor sustentado**:
> aqui, ao contrário do no-till no #40, medir melhor **não** ressuscitou o sinal.

Cross-check com os desfechos da lógica (**n=244 munis**), bruto → parcial|lat → parcial|lat+lon:

| Covariável × desfecho | bruto | \|lat | \|lat+lon |
|---|---|---|---|
| Calcário × idade mediana | −0,16 | −0,08 (p=0,24) | −0,05 (p=0,45) |
| Calcário × índice jovem | +0,16 | +0,05 (p=0,41) | +0,03 (p=0,70) |
| Calcário × % rotação | +0,22 | −0,01 (p=0,83) | −0,01 (p=0,93) |
| Orientação × idade mediana | −0,09 | +0,02 (p=0,76) | +0,02 (p=0,73) |
| Orientação × % rotação | +0,27 | −0,01 (p=0,89) | −0,01 (p=0,90) |

**Nenhum** dos 8 pares das covariáveis novas sobrevive, com |r| ≤ 0,05 sob o controle 2D
— nulos francos, não limítrofes. A intensificação (calcário) e a instituição (orientação)
**co-localizam na aptidão latitudinal; não isolam efeito próprio** sobre a idade da
pastagem.

> ⚠️ **Mas a generalização precisa de uma ressalva agora.** O no-till, citado antes como
> "exatamente igual", **não** é mais um nulo franco: no censo fica em p≈0,057–0,058
> (limítrofe, ver #40 §2), e a covariável de referência **adubação** dá 3 pares a
> p=0,003–0,013. Nenhum desses sobrevive a **FDR-BH** (0 de 16 pares do #40B), então o
> veredito agregado se mantém — mas **não escrever que "nenhuma covariável estrutural
> sobrevive ao gradiente" como afirmação geral**. Isso vale para calcário e orientação,
> que é o que este pipeline testa; não para todas.

### 3. Textura institucional nova — a ORIGEM da orientação é ela mesma Sul→Norte
Composição da assistência técnica entre os estabelecimentos que a recebem, vs latitude:

- **Cooperativas**: r(lat) = **−0,40** — orientação cooperativa/comercial concentra-se no **Sul**.
- **Governo** (extensão pública): r(lat) = **+0,53** — assistência pública domina no **Norte**.

Os "dois Goiáses" têm **dois modelos de extensão**: comercial-cooperativo no núcleo agrícola do Sul, público na fronteira do Norte. É textura descritiva (não causal), coerente com todo o eixo Sul→Norte.

---

## Veredito

Confirma e **generaliza a D14**: em cross-section estadual, calcário e orientação técnica são mais dois marcadores do gradiente de aptidão — descem ao Sul com a lógica jovem, mas o efeito próprio evapora ao controlar lat+lon. O achado robusto do #40 permanece **a geografia da bimodalidade**, não um driver estrutural. Contribuição desta passada: (a) mostra que a lição não era peculiaridade do no-till — com a ressalva, acrescentada em 21/jul/2026, de que o próprio no-till deixou de ser um nulo franco no censo (p≈0,058) e que quem hoje sustenta o nulo com folga são calcário e orientação, não o no-till; (b) revela o **gradiente institucional da extensão** (cooperativa-Sul × pública-Norte), um espelho institucional do "dois Goiáses". As covariáveis novas (Q2 da auditoria de uso do painel) ganham, assim, seu primeiro uso analítico.

**Honestidade**: cross-section 2017 estático (sem uso longitudinal); n=244 munis (censo do #28; era 88 na amostra); a composição da orientação é descritiva. Não abre perna causal — reforça a existente.
