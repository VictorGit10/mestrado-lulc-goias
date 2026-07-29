# Pipeline #47 — O custo de carbono da marcha ao norte

**Script**: `scripts/custo_carbono_marcha.py`
**Quando foi feito**: 2026-07-16. Segunda perna do **eixo ambiental** aberto pelo #46; realiza o "próximo passo" que o #46 e o #44 apontaram (aplicar densidades de C do Cerrado às formações que recuam).
**Depende de**: #44 (vegetação natural aberta em 3 formações — floresta/savânica/campo), #32/#34/#39 (máquina de regionalização Sul/Centro/Norte + faixa de latitude + centróide EPSG:5880), #12/#19 (transições brutas, para o cross-check). Painel AMC (#25).
**Outputs**:
- `data/processed/carbono_por_formacao.csv` — Bloco A: área perdida + Mt C/CO₂e por formação (3 cenários).
- `data/processed/carbono_regional_ato.csv` — Bloco B: emissão por região × ato × formação.
- `data/processed/carbono_por_amc.csv` — perda + emissão por AMC (com lat/região) para mapa.
- `data/processed/carbono_centroide_ato.csv` — centróide da perda de C por ato (a marcha do custo).
- `data/processed/carbono_sensibilidade.csv` — manchete por cenário baixa/central/alta.
- `outputs/custo_carbono/carbono_por_formacao.png`, `carbono_regiao_ato.png`, `carbono_centroide_marcha.png`.

---

## Pergunta de pesquisa

A "marcha ao norte" (#32) é uma **reorganização** da produção — mas, numa dissertação de Ciências Ambientais, ela precisa de um **preço ambiental** quantificado. A ponte veio do #44: a "muralha norte" da vegetação (o +8 km, "quase parada" no #32) era miragem de média — a **floresta** nativa ficou presa (mata de galeria, +9 km) enquanto **savânica e campo** recuaram forte ao norte. Como as três formações têm densidades de carbono **muito diferentes** (floresta densa ≫ savana ≫ campo), a pergunta é dupla:

> (1) Quanto **carbono comprometido** saiu do recuo de cada formação, 1985→2024? (2) Esse custo **marcha ao norte** junto com a fronteira, ou fica ancorado ao sul?

---

## O que faz (método de diferença de estoque, formação-resolvido)

Emissão comprometida = Σ_f Δestoque_f (ha perdidos) × densidade_C_f (Mg C/ha), por AMC × ano, com f ∈ {floresta, savânica, campo}, seguindo o **método de diferença de estoque (IPCC Tier 1)**. CO₂e = C × 44/12.

- **Estoque por formação** vem do painel AMC (#25/#44). **Espacialização** reusa `amc_para_meso` (#34) → região (Sul/Centro/Norte) + faixa de latitude (4 quantis) + latitude do centróide.
- **Bloco A** — balanço estadual por formação: quem perde área × quem domina o carbono.
- **Bloco B** — espacial: emissão por região × ato + **centróide da perda de C por ato** (análogo ao #32; só perdas ponderam; média + mediano robusto por Weiszfeld).
- **Bloco C** — cross-check com as **matrizes de transição** (#12/#19): fluxo bruto veg→antrópico × densidade média ponderada = cota-teto **bruta** vs o **líquido** (diferença de estoque). Bruto ≥ líquido porque o líquido desconta rebrota.

### D18 (decisão nova) — densidades de carbono do Cerrado
Mg C/ha, **biomassa aérea + radicular (AGB+BGB)**, três cenários de sensibilidade. Fontes: Bustamante et al. (2012, *Climatic Change* 115:559), Grace et al. (2006, *J. Biogeography* 33:387), Ribeiro & Walter (2008, fisionomias), IPCC (2006 GL, Tier 1 tropical). O Cerrado tem enorme biomassa **radicular** (razão raiz:parte-aérea alta), por isso savana/campo não são desprezíveis.

| formação | baixa | central | alta |
|---|---|---|---|
| Floresta nativa (galeria/cerradão) | 75 | 95 | 120 |
| Formação savânica (Cerrado s.s.) | 25 | 33 | 40 |
| Campo nativo | 8 | 13 | 18 |

Solo (SOC 0–30 cm ≈ 40 Mg C/ha, fração liberada ~0,25) entra como **camada separada e opcional** (`--com-solo`) — a mudança de SOC na conversão para pasto/lavoura é lenta e contestada, então **fica fora da manchete**.

---

## Achados — o carbono não é proporcional à área, e o custo marcha ao norte

### 1. A floresta domina o carbono mesmo perdendo menos da metade da área da savânica
Perda líquida de vegetação nativa 1985→2024 = **5,55 Mha**. Balanço por formação (cenário central):

| formação | área perdida (Mha) | emissão (Mt CO₂e) | faixa (baixa–alta) |
|---|---|---|---|
| **Floresta nativa** | 1,43 | **499** | 394–631 |
| **Formação savânica** | 3,79 | 458 | 347–555 |
| **Campo nativo** | 0,33 | 16 | 10–22 |
| **TOTAL** | **5,55** | **973** | 751–1208 |

A savânica perde **2,6× mais área** que a floresta, mas a floresta **emite mais carbono** (499 > 458 Mt) por ser ~3× mais densa por hectare. **Manchete**: o custo de carbono da conversão **não é proporcional à área** — a mata de galeria/cerradão, que o #44 mostrou "presa" e imóvel, quando cai custa desproporcionalmente caro. Campo nativo é quase gratuito em carbono (16 Mt, 1,6% do total). Total comprometido ≈ **973 Mt CO₂e** (biomassa, central; ~25 Mt/ano médio), robusto no ordenamento em toda a faixa 751–1208.

### 2. O custo foi pago cedo e no Sul; o que resta migra ao norte
Ritmo de emissão (Mt CO₂e/ano) por região × ato:

| ato | Sul | Centro | Norte |
|---|---|---|---|
| I (1985–2000) | **20,5** | 15,2 | 15,9 |
| II (2001–2019) | 1,6 | 2,9 | 3,0 |
| III (2020–2024) | 1,4 | **4,6** | 3,1 |

**80% do carbono comprometido saiu no Ato I** (1985–2000) — a expansão inicial do pasto sobre o Cerrado, concentrada no **Sul** (20,5 Mt/ano). Depois de 2001 o ritmo despenca ~6× e **inverte a geografia**: no Ato III o **Sul é o menor** (1,4) e Centro/Norte lideram (4,6 / 3,1). O **centróide da perda de carbono marcha +98 km ao norte** de Ato I (lat −16,06) a Ato III (−15,17). Isto **amarra diretamente com o #39**: o Sul esgotou o Cerrado convertível (fronteira fechada) e o custo residual de carbono migrou para onde ainda há o que converter — o Norte/Centro. A soma cumulativa por região fica quase equilibrada (Sul 36% / Centro 32% / Norte 32%) *porque o Sul carrega a herança do Ato I*.

> **Nota de reconciliação (29/jul/2026).** A decomposição por ato (`carbono_regional_ato.csv`)
> soma **946,7 Mt = 97,3% do total-manchete de 973 Mt** (`carbono_por_formacao.csv`), porque cada
> ato é medido por **diferença de estoque entre seus endpoints** (I=1985→2000, II=2001→2019,
> III=2020→2024) e as transições dos **dois anos-fronteira entre atos (2000→01 e 2019→20)** não
> caem em ato nenhum — verificado: `perda(2000,01) + perda(2019,20) = 26,4 Mt`, exatamente o gap.
> Portanto **não divida uma tabela pela outra**: o Ato I vale **79,5% do total de estoque** (774
> de 973) *ou* **81,7% da decomposição por ato** (774 de 947) — o "~80%" é robusto às duas réguas.
> O total-manchete (973) e o cross-check bruto×líquido (§3) usam a diferença de estoque de período
> inteiro, que é a régua correta para a métrica-manchete.

### 3. Cross-check bruto × líquido — consistente
Fluxo bruto veg→antrópico das transições (#12/#19) = 6,24 Mha × densidade ponderada 48 Mg C/ha ≈ **1.095 Mt CO₂e** (cota-teto); o líquido por diferença de estoque = **974 Mt CO₂e**; razão líq/bruto = **0,89**. O líquido é 89% do bruto — a rebrota/regeneração compensa ~11% da conversão bruta, coerente com uma fronteira que ainda avança (pouca regeneração líquida).

---

## Veredito

O eixo ambiental ganha sua **métrica-manchete**: a marcha ao norte comprometeu da ordem de **~970 Mt CO₂e** (biomassa; ~1 Gt), e a distribuição desse custo entre as formações **desmonta a leitura ingênua "savana é pouco carbono"** — a floresta densa, minoritária em área, responde por mais da metade da conta. Junto com o #46 (97% do convertível remanescente está desprotegido), fecha-se a leitura de conservação: **a fronteira marcha sobre Cerrado desprotegido e o pouco que ela ainda converte, ela converte ao norte — mas o grosso do dano de carbono já foi pago, cedo, no Sul.** Isso reposiciona a política: a agenda de mitigação em GO é menos "impedir a próxima conversão" (o estoque e o ritmo caíram) e mais **restauração/recuperação** do passivo já emitido e proteção dos ~6,35 Mha convertíveis desprotegidos do #46.

---

## Honestidade metodológica

- **Diferença de estoque = emissão LÍQUIDA comprometida** (desconta rebrota); o bruto das transições entra ao lado como cota superior. Não é fluxo medido de CO₂ (sem torre de fluxo) — é estoque removido × fator, o padrão de inventário nacional.
- **Densidade é Tier 1** (literatura, não medida em campo em GO) → a sensibilidade baixa/central/alta é obrigatória; a manchete é robusta porque **o ordenamento** (floresta ≳ savânica ≫ campo; marcha ao norte) **não muda** de cenário.
- **"Comprometida"**: o carbono deixa de estar estocado; a liberação real se dá ao longo de anos (decomposição/queima) — não modelo a dinâmica temporal.
- **Centróide é média** (D do #32) → reporto o mediano robusto ao lado, e só sobre AMCs que **perderam** formação.
- **Solo fora da manchete** (D18) — mudança de SOC na conversão é contestada; disponível em `--com-solo` para quem quiser a cota com solo.
- **Validações pendentes** (para a Sprint 2, junto com as do #46): fatores de emissão específicos do Cerrado goiano (se houver inventário estadual); recorte pixel via GEE para checar a atribuição de formação na borda; comparação com o SEEG/MCTI (inventário nacional) para a ordem de grandeza estadual.
