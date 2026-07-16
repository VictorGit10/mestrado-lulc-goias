# Pipeline #49 (Eixo C1) — Painel espacial dinâmico: os canais do #22 sobrevivem ao espaço?

**Script**: `scripts/painel_espacial_dinamico.py`
**Quando foi feito**: 2026-07-16.
**Depende de**: #17 (`taxas_lulc_amc.csv`, Δ área por classe), #25 (`amc_goias.gpkg` + `painel_amc_goias.parquet`), #22 (modelos-manchete), #24 (diagnóstico de autocorrelação espacial). Estimador: `spreg.Panel_FE_Lag` / `Panel_FE_Error` (Elhorst 2003).
**Outputs**:
- `data/processed/painel_espacial_dinamico.csv` — β OLS-within × FE-lag × FE-error, ρ, λ, LM tests, veredito por modelo×W.
- `outputs/espacial/painel_espacial_beta.png` — β (95% IC) antes × depois do termo espacial, por modelo.

---

## Pergunta de pesquisa

O #24 mostrou que a **autocorrelação espacial dos resíduos é estrutural** (115/140 combinações modelo×ano×W com Moran's I significativo), mas:
- o **painel principal (#22)** é um 2-way FE **sem termo espacial**;
- o #24 só modelou o espaço numa **seção transversal** (2020), não no painel.

É a lacuna que uma banca quantitativa pode cutucar: *"vocês documentaram dependência espacial estrutural e não a modelaram nos modelos centrais."* Este pipeline fecha a lacuna:

> Os coeficientes-manchete do #22/#34 **sobrevivem** quando o painel passa a modelar explicitamente a dependência espacial (spatial lag / spatial error)?

Não é história nova — é **escudo de robustez**, na mesma disciplina de D14/D16/#38 (reportar a versão mais conservadora antes de cravar um efeito).

---

## O que faz

Re-estima três canais substantivos num **painel espacial dinâmico** sobre as 166 AMCs, comparando o β **antes** (OLS within, o análogo do #22) e **depois** de adicionar o termo espacial:

| Modelo | Especificação | Janela | Origem |
|---|---|---|---|
| **M1** | Δagricultura ~ Δ VA agro | 2003–2021 (19a) | intensificação (#22) |
| **M2** | Δpastagem ~ Δ SICOR + Δ VA agro | 2014–2021 (8a) | crédito→retração de pasto (#22) |
| **M3** | Δpastagem ~ Δagricultura | 1986–2024 (39a, painel longo) | substituição local (#34, β≈−0,52) |

Para cada modelo: **OLS within 2-way** (baseline, SE cluster por AMC) → **FE spatial lag** (ρ, spillover no desfecho) → **FE spatial error** (λ, correlação espacial no distúrbio) → **LM tests** (lag vs error, incl. robustos) para escolher a forma. M3 roda com **Queen** e **KNN-8** (robustez à matriz W).

### Decisões de método
- **2-way FE com estimador de 1 via.** `spreg.Panel_FE_*` faz FE só de **entidade** (`demean_panel` = kron(J_t, I_n)). Para casar com o 2-way FE do #22/#38, faço **time-demean manual** (subtrair a média anual entre AMCs) **antes** de passar ao spreg; em painel balanceado, (I−P_entidade)(I−P_tempo) = within de duas vias. Assim o **choque macro comum γ_t** (o motivo de o #38 usar γ_t) é absorvido, e o que resta é o gradiente + o spillover espacial.
- **Formato time-major** exigido pelo spreg: y[0:N]=T0, y[N:2N]=T1…; W das AMCs na **mesma ordem** (`code_amc`) da entidade dentro de cada bloco temporal.
- **Painel balanceado** (166 AMCs × T), garantido por construção (`taxas_lulc_amc` tem 0 células nulas; janelas socioeconômicas restringem T).

---

## Achados — todos os canais do #22/#34 sobrevivem ao espaço

**Resultado central: a dependência espacial existe e é forte em toda parte, mas os coeficientes substantivos quase não se movem.**

| Modelo | W | β OLS-within (#22) | β FE-lag | β FE-error | ρ | λ | forma preferida | β sobrevive? |
|---|---|---|---|---|---|---|---|---|
| **M1** intensificação | Queen | −0,0047*** | −0,0043*** | −0,0046*** | +0,35 | +0,37 | error | **sim** |
| **M2** crédito→pasto | Queen | −0,0040*** | −0,0035*** | −0,0034*** | +0,40 | +0,40 | lag | **sim** |
| **M3** substituição | Queen | −0,546*** | −0,477*** | −0,536*** | +0,39 | +0,41 | error | **sim** |
| **M3** substituição | KNN-8 | −0,546*** | −0,481*** | −0,549*** | +0,53 | +0,56 | error | **sim** |

*(\*\*\* p<0,001; todos os LM tests — lag, error e robustos — dão p<0,001, confirmando o #24.)*

**Leitura:**
1. **O espaço é real** — ρ e λ entre +0,35 e +0,56, todos altamente significativos, em todos os modelos e nas duas matrizes W. Confirma o #24: a estrutura espacial não é ruído, é parte do processo.
2. **Mas não vieses os canais do #22.** Em M1 e M3 o robusto-LM prefere **spatial error** (dependência espacial no distúrbio) — caso em que o OLS é **não-viesado**, só ineficiente; por isso β_OLS ≈ β_error (movem <2%). Ou seja: as estimativas do #22 já eram **não-enviesadas** pela dependência espacial. Em M2 prefere **spatial lag** (spillover no próprio desfecho, onde o OLS *seria* enviesado) — e mesmo aí o β do SICOR só atenua 12% (−0,0040→−0,0035) e **segue p<0,001**.
3. **A substituição local (#34) é a mais robusta** — β≈−0,5 sobrevive nas duas W (Queen e KNN-8), com atenuação máxima de ~12% no pior caso (lag). O AIC corrobora a escolha de forma em todos (M1/M3 error, M2 lag).

**Veredito**: os três achados centrais do painel — **intensificação** (agricultura×VA agro), **crédito como canal de retração da pastagem** (SICOR) e **substituição local pasto↔agricultura** — **não dependem de ter ignorado o espaço**. O #22 fica blindado; a dependência espacial estrutural do #24 é, para esses canais, **nuisance a corrigir na inferência**, não um confundidor que inverta o sinal.

---

## Como ler a figura (`painel_espacial_beta.png`)
Um painel por modelo: o β da variável de interesse com IC 95% em três estimadores lado a lado — OLS-within (#22), FE spatial lag, FE spatial error. Em todos, os três pontos ficam do **mesmo lado de zero** e com ICs sobrepostos; os títulos trazem ρ e λ. A mensagem visual é "o ponto não pula quando o espaço entra".

---

## Limitações honestas
- **Uma AMC-ilha** (code 143, sem vizinho Queen) gera *warning*, não erro; efeito negligenciável em N=166.
- **Precedência preditiva, não causal** — como no #22, é FE + defasagem, não identificação causal dura; o termo espacial trata dependência, não endogeneidade da variável econômica.
- **FE de 2 vias por demeaning sequencial** (correto em painel balanceado) — não é o estimador de FE-tempo nativo do spreg (que não existe para o modelo espacial); a equivalência vale porque o painel é balanceado.
- **Janela curta em M2** (8 anos, limite do SICOR ∩ VA agro) — menor poder que M1/M3; ainda assim o SICOR sobrevive.
- **Não é SDM completo** — testa lag OU error, não o Spatial Durbin (lag de X). O SLX direcional já foi testado no #34 (spillover ao sul → pasto local, β=−0,16, oposto ao previsto).

---

## Conexão com a narrativa
Fecha o **Eixo C1** do backlog. Dá ao #22/#34 a robustez espacial que o #24 sinalizava como faltante: os canais econômicos do painel não são artefato de autocorrelação espacial não modelada. Complementa a bateria de robustez do projeto (janelas D12, latitude D14, Toda-Yamamoto D16, FDR do #38) com a dimensão **espacial** — agora as quatro réguas (temporal, latitudinal, de integração e espacial) concordam que os achados centrais são estáveis.
