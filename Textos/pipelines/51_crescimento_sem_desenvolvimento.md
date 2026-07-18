# Pipeline #51 — Crescimento econômico × desenvolvimento humano (IFDM 2013–2023)

**Scripts**: `scripts/coleta_firjan_ifdm.py` (coleta) + `scripts/crescimento_sem_desenvolvimento.py` (análise)
**Status**: ✅ executado (2026-07-18)
**Depende de**: coleta FIRJAN; #16 (`painel_unificado.parquet`); #25 (geometria AMC); #33/#39 (região Sul/Centro/Norte via `deslocamento_espacial.amc_para_meso`).

> **Reabre o fio 6 do backlog** ("crescimento sem desenvolvimento?"), que estava **descartado
> desde 08/jun/2026** por falta de índice de desenvolvimento municipal pós-2010 (o IDH-M do #13
> só existe 1991/2000/2010). A razão do descarte ficou obsoleta: o **IFDM (Índice FIRJAN de
> Desenvolvimento Municipal)** tem uma **Nova Série Histórica municipal 2013–2023** que alcança
> o Ato III. Este pipeline transforma a *assinatura espacial* do #50 (valor ancorado no Sul
> enquanto a área marcha ao Norte) numa **medição direta** de desenvolvimento.

## Pergunta de pesquisa

O #50 mostrou, sem um índice de desenvolvimento, que o **valor** (VA agro, PIB) fica ao centro-sul
enquanto a **área** marcha ao norte — o vão valor↔fronteira alargou de ~84 para ~101 km. Era uma
*proxy espacial* de "crescimento sem desenvolvimento". Com o IFDM (emprego&renda, educação, saúde)
2013–2023, pergunta-se diretamente:

1. **Nível/tendência** — a fronteira Norte é menos desenvolvida e/ou avança mais devagar?
2. **Gradiente (D14)** — o desenvolvimento cai ao norte? O vão diverge ou converge?
3. **Desacoplamento** — o crescimento econômico se **traduz** em desenvolvimento, ou é "surdo" a ele?
4. **Qual dimensão** desacopla mais — emprego&renda, educação ou saúde?

## Dados

- **IFDM** (`coleta_firjan_ifdm.py`): FIRJAN, Nova Série Histórica **municipal 2013–2023**, 4 dimensões
  (Geral + Emprego&Renda + Educação + Saúde). 246 municípios de GO × 11 anos = 2.706 linhas.
  Chave: `COD_MUNIC` (6 díg.) → `cd_mun` (7 díg.) via `cd_mun // 10` (o DV é só anexado — ponte
  exata, sem cálculo de dígito verificador). IFDM Geral médio GO subiu de **0,487 (2013) → 0,633 (2023)**.
- **Painel** (#16): VA agro, PIB, SICOR, área agrícola, rebanho, população. **Janela de crescimento
  = 2013→2021** (VA agro e população têm defasagem IBGE e param em 2021); **níveis de IFDM até 2023**.
- **Região + latitude**: `amc_para_meso()` (centroide da AMC, EPSG:5880 → lat) + `regiao_de_meso`
  (Sul = Sul Goiano; Norte = Norte + Noroeste Goiano; Centro = resto). n: Sul 82, Centro 115, Norte 49.

## Achados

### A. A fronteira Norte quase dobrou a lavoura — e o desenvolvimento não acompanhou

| Região | n | IFDM 2013→2023 (Δ) | Área agríc. (agreg.) | VA agro (agreg.) | Rebanho (agreg.) |
|---|--:|---|--:|--:|--:|
| **Sul** | 82 | 0,533 → 0,674 (**+0,141**) | +0,13 (3,46→3,94 Mha) | +0,47 | +0,01 |
| Centro | 114 | 0,474 → 0,621 (**+0,147**) | +0,22 | +0,46 | +0,15 |
| **Norte** | 50 | 0,441 → 0,591 (**+0,150**) | **+0,66** (0,24→0,46 Mha) | +0,51 | **+0,20** |

*(Crescimento = **log da soma regional** 2013→2021, robusto ao viés de base pequena — a média de
log-ratios municipais inflava o Norte. Números por município disponíveis no CSV.)*

A marca do Norte é a **expansão de fronteira**: a área agrícola **quase dobrou** (0,24 → 0,46 Mha, +93%),
contra +14% no Sul, além do maior avanço no rebanho. **Já o VA agropecuário cresceu de forma parecida em
todas as regiões** (~+0,5 no agregado) — ou seja, o que distingue o Norte é a **abertura de terra**, não o
valor gerado. **E o ganho de desenvolvimento foi estatisticamente idêntico ao do Sul**: ΔIFDM Norte−Sul =
**+0,009, IC95% [−0,008, +0,027] (inclui zero)**. O boom de fronteira **não fechou** o vão: o nível
permanece **IFDM 2023 Norte−Sul = −0,083, IC95% [−0,108, −0,058]** (robusto, ≠0). A fronteira gera
hectares — e desenvolvimento humano na mesma proporção **não** vem junto.

### B. Gradiente latitudinal: forte no NÍVEL, nulo no GANHO (D14)

| Alvo | Spec | n | r² | β_lat (z) | p | β_lon | p |
|---|---|--:|--:|--:|--:|--:|--:|
| IFDM 2023 (nível) | ~lat | 246 | 0,246 | **−0,038** | <0,001 | — | — |
| IFDM 2023 (nível) | ~lat+lon | 246 | 0,252 | **−0,036** | <0,001 | −0,006 | 0,213 |
| Δ IFDM 2013→2023 | ~lat | 245 | 0,022 | +0,008 | 0,018 | — | — |
| Δ IFDM 2013→2023 | ~lat+lon | 245 | 0,025 | +0,007 | **0,066** | +0,003 | 0,415 |

O **nível** de desenvolvimento cai claramente ao norte (β robusto, r²=0,25, sobrevive ao controle de
longitude). O **ganho**, porém, é praticamente **plano** na latitude — o marginal "Norte ganha um pouco
mais" **enfraquece** sob o controle 2D (D14: p passa de 0,018 → 0,066). Conclusão: o gradiente é de
**nível persistente**, não de convergência nem de divergência — o vão está **estável**.

### C. Desacoplamento: a EXPANSÃO DE ÁREA não compra desenvolvimento; o VALOR compra um pouco

**Transversal (246 municípios, ΔIFDM Geral × crescimento — ambos na janela casada 2013→2021):**

| Crescimento | r bruto | p | β parcial \| lat,lon | p |
|---|--:|--:|--:|--:|
| VA agropecuário | +0,208 | 0,001 | +0,009 | 0,003 |
| PIB total | +0,169 | 0,008 | +0,007 | 0,049 |
| **Área agrícola** | **−0,020** | 0,754 | −0,008 | 0,008 |
| Crédito rural (SICOR) | +0,081 | 0,207 | +0,003 | 0,220 |
| Rebanho bovino | +0,160 | 0,012 | +0,005 | 0,064 |

**Painel 2FE (município+ano) em 1as diferenças (D7/D8), 2013–2021:**

| Modelo | Regressor | β | p | n | r²within |
|---|---|--:|--:|--:|--:|
| ΔIFDM ~ Δlog VA | Δlog VA agro | +0,0039 | 0,539 | 1.950 | 0,0005 |
| ΔIFDM ~ Δlog área | Δlog área | +0,0118 | 0,011 | 1.950 | ≈0 |
| ΔIFDM ~ VA+área | Δlog VA agro | +0,0035 | 0,582 | 1.950 | ≈0 |
| ΔIFDM ~ VA+área | Δlog área | +0,0117 | 0,012 | 1.950 | ≈0 |

O **motor da fronteira — a expansão de área — é o mais desacoplado**: correlação transversal **nula**
(r=−0,02) e, controlando latitude, até **negativa** (β=−0,008, p=0,008); no painel intra-município um β
minúsculo (dobrar a área → ~+0,008 de IFDM) com **r²within ≈ 0**. Já o **VA agropecuário** (o *valor*, não
a *terra*) tem um dividendo **modesto mas real** (r=+0,21, robusto ao controle de latitude, p=0,003) — no
painel intra-município, porém, some (β não-significativo). Leitura: onde a fronteira **abre terra**, o
desenvolvimento **não** acompanha; onde há **valor agropecuário**, há um ganho pequeno de desenvolvimento —
e como o Norte cresce em *área* (não distintamente em *valor*, Bloco A), fica com o lado desacoplado.

### D. Educação é a desacoplada; emprego&renda e saúde acompanham

r transversal Δsubíndice × Δlog VA agro (janela casada): **Emprego&Renda +0,213** (mecânico — renda entra no
índice), **Saúde +0,206** (parcial|lat robusto, p<0,001), **Educação −0,099** (ns, até negativo; parcial|lat
p=0,052). O ganho de **educação** — dimensão provida pelo Estado, não pelo boom agrícola local — é o que
**menos** tem a ver com o crescimento econômico.

### E. Robustez à unidade — o achado é invariante entre município e AMC

Como a janela 2013–2023 tem os **246 municípios estáveis** (nenhum nasceu/se dividiu — a motivação do AMC/D11
não se aplica), a análise é municipal. Ainda assim, replicou-se o núcleo no **AMC (166, IFDM pop-ponderado)**
e o resultado é o mesmo: nível 2023 Norte−Sul **−0,077** (municipal −0,083); ganho Norte−Sul **+0,015**
(municipal +0,009, ambos ≈0); gradiente latitudinal **r=−0,49** (p<0,0001); desacoplamento Δárea×ΔIFDM
**r=−0,09** (ns). **Nenhuma conclusão depende da unidade de análise.**

## Veredito

**"Crescimento sem desenvolvimento" deixa de ser proxy espacial (#50) e vira medição.** A fronteira Norte
**quase dobrou** a área agrícola (+93% vs +14% no Sul), mas: (i) permanece ~0,08 de IFDM **abaixo** do Sul
(gradiente de nível forte e robusto, invariante a município/AMC); (ii) seu ganho de desenvolvimento foi
**idêntico** ao do Sul — o boom **não** fechou o vão; (iii) o **motor da fronteira — a expansão de área —
é desacoplado** do desenvolvimento (r≈0, até negativo controlando latitude; painel r²within≈0), enquanto o
**valor** agropecuário tem só um dividendo **modesto** (r=0,21). Como o Norte cresce em *terra* e não
distintamente em *valor*, ele fica com o lado desacoplado. É a leitura "exporta hectares, não
desenvolvimento" do #50 — agora com um número.

## Limitações

- **IFDM ≠ IDH-M** e ≠ bem-estar amplo; é proxy de desenvolvimento (emprego&renda / educação / saúde).
- **O IFDM subiu em toda parte** (+~0,14): a leitura é "o crescimento não **fecha o vão** nem compra
  desenvolvimento **extra**", **não** "não houve desenvolvimento". Frasear sempre em ganho **relativo**/nível.
- **Série nova** (revisão metodológica): 2013–2023 consistente por dentro, **não** emendável com a antiga
  2005–2016. Janela curta (11 anos; crescimento só até 2021 por defasagem do VA agro/pop). O desacoplamento
  (Bloco C) usa a **janela casada** 2013→2021 para ΔIFDM e crescimento; o nível/vão (A/B) usa 2013→2023.
- **Associativo (D14)**, não causal — controla-se latitude/longitude, mas não confundidores que variam
  dentro do município no tempo. Emprego&renda é parcialmente **mecânico** (renda entra no índice).
- **Geografia municipal direta**: região por `mapeamento_mesorregioes.csv` e latitude pelo **centroide do
  município** (geobr, cacheado). Diferença ante a via AMC do 1º rascunho: 1/246 município de região, ~1 km
  de latitude — imaterial, e o Bloco E confirma invariância município↔AMC.

## Saídas

| Arquivo | Conteúdo |
|---|---|
| `data/processed/ifdm_goias_municipal.csv` | IFDM 4 dimensões, 246 munis × 2013–2023 |
| `data/processed/municipios_centroides_go.csv` | cache dos centroides municipais (lat/lon, geobr) |
| `data/processed/desenvolvimento_regional.csv` | Bloco A: IFDM + crescimento por região |
| `data/processed/desenvolvimento_gradiente.csv` | Blocos B/C/E: coeficientes (gradiente, desacoplamento, painel, robustez AMC) |
| `outputs/desenvolvimento/ifdm_regional.png` | IFDM Sul/Centro/Norte 2013–2023 (4 dimensões) |
| `outputs/desenvolvimento/decouplamento.png` | expansão de área (fronteira) × Δ IFDM, cor por região |

## Como rodar

```bash
py -3.14 scripts/coleta_firjan_ifdm.py              # baixa + processa o IFDM
py -3.14 scripts/crescimento_sem_desenvolvimento.py  # análise + figuras
py -3.14 scripts/crescimento_sem_desenvolvimento.py --sem-figuras
```

## Conexão com a narrativa

Estende o **Movimento VII** do ensaio ("o que limita, o que custa" → agora "o que **não** se traduz em
desenvolvimento"). O #50 dava a assinatura espacial ("crescimento em área sem desenvolvimento em valor na
ponta da fronteira") **sem** um índice de desenvolvimento; o #51 fecha o argumento com o IFDM: a fronteira
Norte é a que mais cresce e a que menos desenvolve — e o crescimento e o desenvolvimento **andam
desacoplados** no município. É a peça de **Ciências Ambientais/socioeconômica** que faltava para dizer que a
marcha ao norte gera valor agropecuário sem converter isso em bem-estar humano proporcional.
