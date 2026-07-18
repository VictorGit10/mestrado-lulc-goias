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

### A. A fronteira Norte cresceu MUITO mais — e o desenvolvimento não acompanhou

| Região | n | IFDM 2013→2023 (Δ) | Δlog VA agro | Δlog área agríc. | Δlog rebanho |
|---|--:|---|--:|--:|--:|
| **Sul** | 82 | 0,533 → 0,674 (**+0,141**) | +0,37 | +0,24 | −0,01 |
| Centro | 115 | 0,474 → 0,621 (**+0,147**) | +0,32 | +0,38 | +0,10 |
| **Norte** | 49 | 0,441 → 0,590 (**+0,150**) | **+0,46** | **+1,02** | **+0,23** |

O Norte teve **de longe** a maior expansão econômica — a área agrícola cresceu ~**3× mais** que no Sul
(Δlog +1,02 vs +0,24), além do maior avanço em VA agro e rebanho. **Mas o ganho de desenvolvimento foi
estatisticamente idêntico ao do Sul**: ΔIFDM Norte−Sul = **+0,008, IC95% [−0,010, +0,026] (inclui zero)**.
Ou seja, o boom econômico da fronteira **não fechou** o vão de desenvolvimento. E o nível permanece
abaixo: **IFDM 2023 Norte−Sul = −0,084, IC95% [−0,109, −0,057]** (robusto, ≠0). A fronteira gera
hectares e valor agropecuário sem converter isso em desenvolvimento humano proporcional.

### B. Gradiente latitudinal: forte no NÍVEL, nulo no GANHO (D14)

| Alvo | Spec | n | r² | β_lat (z) | p | β_lon | p |
|---|---|--:|--:|--:|--:|--:|--:|
| IFDM 2023 (nível) | ~lat | 246 | 0,244 | **−0,038** | <0,001 | — | — |
| IFDM 2023 (nível) | ~lat+lon | 246 | 0,248 | **−0,036** | <0,001 | −0,006 | 0,242 |
| Δ IFDM 2013→2023 | ~lat | 245 | 0,018 | +0,007 | 0,031 | — | — |
| Δ IFDM 2013→2023 | ~lat+lon | 245 | 0,022 | +0,006 | **0,111** | +0,004 | 0,316 |

O **nível** de desenvolvimento cai claramente ao norte (β robusto, r²=0,24, sobrevive ao controle de
longitude). O **ganho** 2013–2023, porém, é praticamente **plano** na latitude — o marginal "Norte
ganha um pouco mais" **não sobrevive** ao controle 2D (D14: p passa de 0,031 → 0,111). Conclusão: o
gradiente é de **nível persistente**, não de convergência nem de divergência — o vão está **estável**.

### C. Desacoplamento: o crescimento é largamente "surdo" ao desenvolvimento

**Transversal (246 municípios, ΔIFDM Geral × crescimento 2013→2021):**

| Crescimento | r bruto | p | β parcial \| lat,lon | p |
|---|--:|--:|--:|--:|
| VA agropecuário | +0,132 | 0,039 | +0,006 | 0,049 |
| PIB total | +0,132 | 0,040 | +0,006 | 0,053 |
| **Área agrícola** | **−0,038** | 0,553 | −0,007 | 0,082 |
| Crédito rural (SICOR) | +0,048 | 0,452 | +0,002 | 0,499 |
| Rebanho bovino | +0,066 | 0,307 | +0,001 | 0,678 |

**Painel 2FE (município+ano) em 1as diferenças (D7/D8), 2013–2021:**

| Modelo | Regressor | β | p | n | r²within |
|---|---|--:|--:|--:|--:|
| ΔIFDM ~ Δlog VA | Δlog VA agro | +0,0039 | 0,539 | 1.950 | 0,0005 |
| ΔIFDM ~ Δlog área | Δlog área | +0,0118 | 0,011 | 1.950 | ≈0 |
| ΔIFDM ~ VA+área | Δlog VA agro | +0,0035 | 0,582 | 1.950 | ≈0 |
| ΔIFDM ~ VA+área | Δlog área | +0,0117 | 0,012 | 1.950 | ≈0 |

O motor de crescimento da fronteira — a **expansão de área** — é o mais **desacoplado**: correlação
transversal **nula** (r=−0,04) e, no painel intra-município, um β minúsculo (economicamente irrelevante:
dobrar a área → +0,008 de IFDM) com **r²within ≈ 0** (não explica nada da variação de desenvolvimento).
O VA agro tem uma associação **fraca** e frágil (r=0,13; no painel β não-significativo). Onde a economia
cresce, o desenvolvimento **não sobe junto** de forma material.

### D. Educação é a mais desacoplada; emprego&renda a que mais acompanha

r transversal Δsubíndice × Δlog VA agro: **Emprego&Renda +0,142** (mecânico — renda entra no índice, mas
não sobrevive ao controle de latitude), **Saúde +0,133** (parcial|lat robusto, p=0,003), **Educação −0,084**
(ns, até negativo). O ganho de **educação** — dimensão provida pelo Estado, não pelo boom agrícola local —
é o que menos tem a ver com o crescimento econômico da fronteira.

## Veredito

**"Crescimento sem desenvolvimento" deixa de ser proxy espacial (#50) e vira medição.** A fronteira Norte
cresceu economicamente muito mais que o núcleo Sul (≈3× a expansão de área), mas: (i) permanece ~0,08 de
IFDM **abaixo** do Sul (gradiente de nível forte e robusto); (ii) seu ganho de desenvolvimento foi
**idêntico** ao do Sul — o boom **não** fechou o vão; (iii) no município, o crescimento econômico é
**largamente desacoplado** do ganho de desenvolvimento (a área, motor da fronteira, tem r≈0 e r²within≈0).
É a leitura de "exporta hectares e valor, não desenvolvimento" do #50 — agora com um número.

## Limitações

- **IFDM ≠ IDH-M** e ≠ bem-estar amplo; é proxy de desenvolvimento (emprego&renda / educação / saúde).
- **O IFDM subiu em toda parte** (+~0,14): a leitura é "o crescimento não **fecha o vão** nem compra
  desenvolvimento **extra**", **não** "não houve desenvolvimento". Frasear sempre em ganho **relativo**/nível.
- **Série nova** (revisão metodológica): 2013–2023 consistente por dentro, **não** emendável com a antiga
  2005–2016. Janela curta (11 anos; crescimento só até 2021 por defasagem do VA agro/pop).
- **Associativo (D14)**, não causal — controla-se latitude/longitude, mas não confundidores que variam
  dentro do município no tempo. Emprego&renda é parcialmente **mecânico** (renda entra no índice).
- **Latitude via centroide da AMC** (não do município) — herda o caveat de resolução do #50/#43.

## Saídas

| Arquivo | Conteúdo |
|---|---|
| `data/processed/ifdm_goias_municipal.csv` | IFDM 4 dimensões, 246 munis × 2013–2023 |
| `data/processed/desenvolvimento_regional.csv` | Bloco A: IFDM + crescimento por região |
| `data/processed/desenvolvimento_gradiente.csv` | Blocos B/C: coeficientes (gradiente, desacoplamento, painel) |
| `outputs/desenvolvimento/ifdm_regional.png` | IFDM Sul/Centro/Norte 2013–2023 (4 dimensões) |
| `outputs/desenvolvimento/decouplamento.png` | crescimento (VA agro) × Δ IFDM, cor por região |

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
