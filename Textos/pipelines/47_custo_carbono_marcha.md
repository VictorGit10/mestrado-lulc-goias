# Pipeline #47 — O custo de carbono da marcha ao norte

**Script**: `scripts/custo_carbono_marcha.py`
**Quando foi feito**: 2026-07-16. Segunda perna do **eixo ambiental** aberto pelo #46; realiza o "próximo passo" que o #46 e o #44 apontaram (aplicar densidades de C do Cerrado às formações que recuam).
**Depende de**: #44 (vegetação natural aberta em 3 formações — floresta/savânica/campo), #32/#34/#39 (máquina de regionalização Sul/Centro/Norte + faixa de latitude + centróide EPSG:5880), #12/#19 (transições brutas, para o cross-check). Painel AMC (#25).
**Outputs**:
- `data/processed/carbono_por_formacao_mcti.csv` — Bloco A: área perdida + Mt C/CO₂e por formação (3 cenários).
- `data/processed/carbono_regional_ato_mcti.csv` — Bloco B: emissão por região × ato × formação.
- `data/processed/carbono_por_amc_mcti.csv` — perda + emissão por AMC (com lat/região) para mapa.
- `data/processed/carbono_centroide_ato_mcti.csv` — centróide da perda de C por ato (a marcha do custo).
- `data/processed/carbono_sensibilidade_mcti.csv` — manchete por cenário baixa/central/alta.
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

> ⚠ **ESTA SEÇÃO ESTÁ NA RÉGUA D18, SUPERADA.** Os números de composição abaixo (floresta 499
> × savânica 458) foram **invertidos** pela D30, que trocou as densidades compiladas da
> literatura pelas do 4º Inventário Nacional: a savânica passa a ser quem paga (573 × 340). O
> total quase não se move (973 Mt nas duas réguas). A D31 acrescentou a distinção entre
> **estoque removido** (973 Mt) e **emissão líquida** (833 Mt), que esta seção não faz.
> A régua vigente está em [§ Régua nova](#régua-nova-os-estoques-do-4º-inventário-nacional-20ago2026).
> A seção fica registrada, e não corrigida: é o que se publicaria antes da conferência de
> procedência que a substituiu.

### 1. A floresta domina o carbono mesmo perdendo menos da metade da área da savânica *(superado — ver aviso acima)*
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

> **Nota de reconciliação (29/jul/2026).** A decomposição por ato (`carbono_regional_ato_mcti.csv`)
> soma **946,7 Mt = 97,3% do total-manchete de 973 Mt** (`carbono_por_formacao_mcti.csv`), porque cada
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

---

## Régua nova: os estoques do 4º Inventário Nacional (20/ago/2026)

Fecha a validação que este próprio documento listava como pendente ("comparação com o
SEEG/MCTI para a ordem de grandeza estadual") e resolve, de quebra, a única afirmação
numérica do trabalho sem localizador de página.

**O problema.** A conta inteira é área medida × densidade de literatura. Das quatro
fontes da D18, **duas nunca foram lidas** — Bustamante (2012) e Grace (2006) são pagas,
e o `LEIAME` registrava só metadados do Crossref. Seis números sem localizador
sustentavam 973 Mt.

**A fonte.** 4º Inventário Nacional (MCTI, 2020), Relatório de Referência do setor
LULUCF: estoques por fitofisionomia do mapa do IBGE, **Tabela 24, p. 121–127** (Cerrado)
e **Tabela 76, p. 246** (fisionomias florestais). A Nota Metodológica do SEEG agrega
essas fitofisionomias nas **classes do MapBiomas** por média ponderada de área
(Tabela 2, p. 20–32) e publica o estoque de Floresta do Cerrado **por estado**
(Tabela 3, p. 33). Tudo gratuito. PDFs em `qualificacao/ref/pdf/`.

| classe MapBiomas | coluna do painel | D18 (central) | 4º Inventário |
|---|---|---|---|
| 3 — Formação Florestal | `lulc_floresta_nativa_ha` | 95,00 | **64,72** (valor de **GO**) |
| 4 — Formação Savânica | `lulc_formacao_savanica_ha` | 33,00 | **41,32** |
| 12 — Formação Campestre | `lulc_campo_nativo_ha` | 13,00 | **24,94** |
| 11 — Campo Alagado | `lulc_campo_alagado_ha` | *(fora da conta)* | **36,21** |

Escopo do Inventário: aéreo + subterrâneo + madeira morta + serapilheira, sem solo —
dois compartimentos a mais que a D18. Sem cenário baixa/alta: o Inventário publica valor
pontual para o Cerrado e trata a incerteza qualitativamente (Tabela 85, p. 269); não se
fabrica faixa aqui.

**Não há passo de tradução.** Os valores saem publicados nas mesmas classes que
`construir_painel_unificado.py:165-169` usa. O caminho alternativo — derivar tudo dos
defaults do IPCC — exigiria decidir se Goiás é *tropical dry* ou *moist deciduous forest*
e se Cerrado *sensu stricto* é *tropical shrubland* (a zona **semiárida**), duas
correspondências contestáveis que virariam o alvo no lugar da densidade.

### O que muda, e o que não muda

| afirmação | D18 | 4º Inventário | |
|---|---|---|---|
| Total comprometido | 973,1 Mt | **973,3 Mt** | ✅ intacto |
| Ato I concentra a emissão | 774 Mt (80%) | 722 Mt (76%) | ✅ |
| Ritmo despenca depois de 2001 | 51,6 → 7,6 Mt/ano | 48,1 → 9,7 | ✅ (cinco vezes, não sete) |
| Fronteira troca a formação densa pela extensa | 62,1% → 2,4% florestal | 45,4% → 1,3% | ✅ mais limpo |
| Centróide do custo marcha ao norte | +98 km | **+91 km** | ✅ |
| **Floresta domina a emissão** | 499 × 458 | 340 × **573** | ❌ **inverte** |

O total bater a uma casa decimal é coincidência de erros que se cancelam — a floresta
estava alta e a savânica baixa —, mas é **corroboração externa da magnitude** por uma
fonte oficial independente.

### A razão crítica — e por que a sensibilidade publicada não a testava

"A floresta perde 2,6× menos área e ainda assim emite mais" **não é uma afirmação sobre
seis densidades; é sobre uma razão**. Ela vale se, e só se,

    dens(floresta) / dens(savânica)  >  área_savânica / área_floresta = 2,64

A D18 dá 2,88 — **9% de folga**. Bastaria a savânica valer 36,0 em vez de 33 para empatar.
E os **três cenários da D18 mantêm a razão entre 2,88 e 3,00**, porque movem as duas
densidades juntas: a faixa de 751 a 1.208 Mt testa o **nível** e é estruturalmente
incapaz de testar a **composição**. O `--regua` agora imprime a razão crítica em toda
execução, justamente para que essa dependência não volte a ficar implícita.

Sob a régua oficial a razão é 1,57 e a manchete cai. Isso corrige a frase da seção
"Honestidade metodológica" acima, que dizia que o ordenamento "não muda de cenário": não
mudava porque o cenário não podia mudá-lo.

### Como rodar

```powershell
py -3.14 scripts/custo_carbono_marcha.py                # d18 (publicada)
py -3.14 scripts/custo_carbono_marcha.py --regua mcti   # 4o Inventario, CSVs com sufixo _mcti
```

A régua publicada **não é sobrescrita**: o texto da qualificação cita os CSVs sem sufixo,
e trocar a régua do texto é decisão editorial, não efeito colateral de rodar o pipeline.

### Aresta que a fonte nova abre

O Inventário publica também o estoque do uso que **entra** (Cerrado: pastagem 7,57 e
agricultura anual 5,00 tC/ha, Tabela 5 do SEEG, p. 36). A conta atual assume estoque zero
depois da conversão, e portanto **superestima em 11–16%** (813–868 Mt em vez de 973).
Passar a descontar o destino é mudança de **método**, não de parâmetro, e por isso ficou
fora deste passe — registrada em `ESTOQUE_DESTINO_CERRADO` no script.
