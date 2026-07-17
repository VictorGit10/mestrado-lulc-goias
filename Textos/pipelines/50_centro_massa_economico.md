# Pipeline #50 — Centro de massa econômico e agroindustrial (extensão do #32)

**Script**: `scripts/centro_massa_economico.py`
**Quando foi feito**: 2026-07-16.
**Depende de**: #32 (`centro_massa.py`, **reuso integral** de `carregar_dados`/`mean_center`/`median_center`/`metros_para_lonlat`) e #25 (`painel_amc_goias.parquet`, `amc_goias.gpkg`). Não usa GEE.
**Outputs**:
- `data/processed/centro_massa_economico_anual.csv` — variável × ano: centro médio/mediano + latitude.
- `data/processed/centro_massa_economico_bootstrap.csv` — variável × janela: ΔNorte + **IC95%** (bootstrap de AMCs, D19).
- `outputs/centro_massa/economico_credito.png` — crédito rural (SICOR) vs a fronteira (com faixa IC95%).
- `outputs/centro_massa/economico_valor.png` — VA agropecuário e PIB vs a área (com faixa IC95%).

---

## Pergunta

O #32/#43/#44 puseram na régua de latitude o mundo **físico** (área LULC) e o **rebanho**. Faltava pôr o mundo do **dinheiro**, do **valor** e do **processamento** — justamente as variáveis onde uma **divergência** da fronteira (não a reconfirmação da marcha) seria o achado. Um centroide só agrega quando a variável *pode* divergir; os centroides já feitos que divergem (leite, área urbana, no #44) são os informativos. Aqui testamos três famílias:

1. **Crédito rural (SICOR, 2013–2024).** O eixo econômico (#37/#38: drive liderado por câmbio; #22: crédito→pasto) sempre foi medido no **tempo**, nunca no **espaço**. **O dinheiro público segue a fronteira ao norte, ou consolida a massa produtiva ao sul?** Custeio (capital de giro) e investimento (capex/abertura) podem divergir.
2. **Valor (VA agropecuário 2002–2021; PIB total 2002–2023).** Divergência **valor × área**: se o centroide do valor fica **ao sul** enquanto a área (pasto) marcha ao norte, "a fronteira exporta hectares ao norte, mas o valor se acumula no núcleo". É um ângulo espacial sobre o fio "crescimento sem desenvolvimento" (descartado por falta de IDH-M pós-2010) que **não precisa de IDH**.
3. **Abate bovino** — **testado e descartado** (ver abaixo).

## Abordagem

Método **idêntico** ao #32/#44: centro médio ponderado (Lefever) + mediano (Weiszfeld) sobre os centroides das 166 AMCs em EPSG:5880, só muda o conjunto de variáveis. As **âncoras de área** (pasto, agricultura, soja, rebanho) são recomputadas no mesmo passo, para que as latitudes sejam comparáveis maçã-com-maçã. Todas as variáveis são **extensivas** (R$, cabeças) — centro de massa de razão/taxa não é interpretável. **Descritivo**: sem lead-lag entre latitudes de centroides (D16/#42).

> [!WARNING]
> **Janelas curtas.** Crédito começa em **2013**; valor em **2002**. A leitura de "marcha" de 40 anos **não se aplica** a elas — o que interessa é a **posição relativa** (o vão de latitude vs a fronteira) nos anos em comum, não o ΔN líquido. O resumo reporta a janela própria de cada uma.

---

## Achado 1 — Crédito: consolida a massa produtiva, **não** persegue a fronteira

O centroide do crédito rural senta-se numa **faixa central**, entre o pasto (ao norte) e a agricultura (ao sul), e fica sistematicamente **~75 km ao SUL da pastagem** — a borda da fronteira. Ele **não** acompanha a ponta do avanço; acompanha a **massa produtiva estabelecida** (latitude do rebanho), bem ao norte do núcleo de lavoura, mas longe da fronteira de pasto.

| Crédito (SICOR) | vão vs Pastagem (médio) | 2013 → 2024 |
|---|---:|---:|
| **Total** | **−74,9 km** (ao sul) | −77 → −69 |
| Custeio (giro) | −83,1 km | −91 → −75 |
| **Investimento (capex)** | **−56,4 km** | −53 → −50 |

Dois refinos:
- **Investimento é ~27 km ao NORTE do custeio.** O crédito de **investimento** (abertura/estruturação — cercas, correção de solo, aquisição) inclina-se para a fronteira; o de **custeio** (capital de giro da safra) ancora-se no núcleo consolidado. Faz sentido econômico: capex abre terra nova (norte), giro roda produção madura (sul).
- **O vão encolhe devagar** (total −77 → −69 km de 2013 a 2024): o crédito sobe um pouco ao norte com a expansão geral, mas continua muito ao sul da borda do pasto.
- O centro **médio** do crédito é puxado ~10 km mais ao sul que o **mediano** (o cluster de custeio da lavoura do Sudoeste pesa) — mas ambos ficam largamente ao sul do pasto; a leitura não muda.

**Leitura**: coerente com #37/#38 (crédito é **contexto endógeno**, não o *driver* que lidera; o câmbio lidera) e com #22 (crédito→pasto no local). Espacialmente, o crédito **não é o que empurra a fronteira ao norte** — ele rega a massa já instalada.

## Achado 2 — Valor: fica **quase ancorado** enquanto a área marcha (o vão **alarga**)

O centroide do **VA agropecuário** mal se move (ΔN **+10,8 km** em 2002–2021, IC95% **[+2,5, +19,4]** — *marginalmente* ≠ 0) e o do **PIB total** é **estatisticamente parado** (**+2,0 km**, IC95% **[−12,2, +17,7]** — inclui zero), enquanto no mesmo período a fronteira de pasto segue subindo. O resultado é um **vão que alarga**:

| Valor | vs Agricultura (área) | vs Pastagem (área) |
|---|---:|---:|
| **VA agropecuário** | **+39,8 km** (ao norte) | **−88,6 km** (ao sul) — vão 2002:−84 → 2021:**−101** |
| PIB total | +51,5 km | −77,1 km — vão 2002:−65 → 2023:−96 |

- O valor senta-se **entre** o núcleo de lavoura (ao sul) e a fronteira de pasto (ao norte), mas **muito mais perto do núcleo**: fica **~90 km ao sul** de onde a pastagem está centrada, e o pasto **se afasta** ~17 km ao longo de 2002–2021 (vão −84 → −101 km).
- Ou seja: **a fronteira exporta hectares ao norte, mas o valor não a segue** — permanece ancorado ao centro-sul intensificado. É a assinatura espacial de "crescimento (área) sem desenvolvimento (valor) na ponta da fronteira", medida sem depender de IDH-M.
- **PIB total** é ainda mais parado e um pouco mais ao norte que o VA agro (puxado pelo eixo urbano Goiânia–Anápolis, serviços/indústria) — contexto, não o corte agrícola.

**Nuance honesta**: o VA agro fica **ao norte** da área de lavoura (+40 km) porque mistura valor de lavoura (sul) com valor de pecuária (mais espalhado ao norte); não é o "núcleo da soja" puro. Por isso o achado é **comparativo** — *valor ancorado × área que marcha, com o vão alargando* — e não "o valor está no extremo sul".

## Abate bovino — testado e **descartado** (dado não permite)

A hipótese era rica: o rebanho marchou +67 km ao norte (#32); e o **processamento** (abate/frigorífico)? Se o abate ficasse ao sul, perto dos frigoríficos, haveria descolamento **criar (norte) × abater (sul)**.

**Mas o dado não sustenta a pergunta.** `abate_bovino_cab`/`_kg` no painel são **estimativa top-down**:
$$\text{abate}_{\text{muni}} = \frac{\text{rebanho}_{\text{muni}}}{\text{rebanho}_{\text{UF}}} \times \text{abate}_{\text{UF}}$$
(`estimativa_abate_municipal.py`), porque a Pesquisa Trimestral do Abate (SIDRA 1092–1094) só existe no **nível estadual**. Verificação: dentro de cada ano, `abate/rebanho` tem **desvio-padrão 0,0000** e **corr(abate, rebanho) = 1,0000** → o centroide do abate é **idêntico ao do rebanho por construção** (vão 0,0 km). A comparação seria **circular**. A geografia real de abate exigiria o **registro SIF/MAPA** de estabelecimentos ou a **geolocalização de frigoríficos do Trase** (#45, `trase_boi_n_frigorificos`) — coleta à parte, fora deste pipeline. Por isso o abate **não** entra nos resultados. (Fica como possível extensão futura, se a banca cobrar a geografia agroindustrial.)

---

## Incerteza (bootstrap de AMCs, D19)

Mesma máquina de bootstrap do #32 (reamostra as 166 AMCs com reposição, B=2000; IC95% do ΔNorte; faixa sombreada nas figuras). O que ela diz destes achados:

| Variável | ΔNorte | IC95% (km) | janela | veredito |
| :--- | :---: | :---: | :---: | :--- |
| Crédito total (SICOR) | +26,4 | [+11,6, +38,7] | 2013–24 | marcha (mas fica ~75 km ao sul do pasto) |
| Crédito — custeio | +33,9 | [+17,5, +48,4] | 2013–24 | marcha |
| Crédito — investimento | +21,0 | [+1,5, +39,6] | 2013–24 | marcha (IC apertado) |
| **VA agropecuário** | +10,8 | **[+2,5, +19,4]** | 2002–21 | **move pouco (marginalmente ≠0)** |
| **PIB total** | +2,0 | **[−12,2, +17,7]** | 2002–23 | **parado (inclui zero)** |

Ou seja: o crédito **de fato sobe** um pouco ao norte (não é imóvel), mas o achado não é a marcha e sim a **posição** — ele permanece ~75 km ao sul da fronteira. E o valor **quase não se move** (VA agro mal exclui zero; PIB não exclui), enquanto a área marcha +65 a +78 km — é o alargamento do vão que sustenta a leitura, robusto porque as faixas de VA agro/PIB e do pasto **não se sobrepõem**.

## Como ler as figuras

- **`economico_credito.png`** — as três linhas verdes (crédito) ficam numa **faixa central**, ~75 km **abaixo** (ao sul) da tracejada laranja (pasto) e **acima** da magenta (lavoura). Investimento (verde-escuro) é a mais ao norte das três; custeio (verde-claro) a mais ao sul. A **faixa sombreada** é o IC95% do centroide do crédito (larga porque a janela é curta e poucas AMCs concentram o crédito) — mas mesmo o topo dela fica ao sul do pasto.
- **`economico_valor.png`** — VA agropecuário (azul cheio) e PIB (cinza) ficam **planos** no meio, com suas **faixas IC95%** que **não tocam** a tracejada do pasto/rebanho no topo: o valor **não acompanha** a subida da fronteira; o vão valor↔pasto **alarga**.

## Limitações

- **Descritivo** (posição/deslocamento), não causal — mesma postura do #32/#44. Nenhum lead-lag entre centroides (D16).
- **Janelas curtas** (crédito 12 anos; valor ~20 anos): lê-se posição relativa, não marcha de 40 anos.
- **Tabulares sem MAUP**: crédito é estatística de contratação (SICOR/BCB), não raster — herda o caveat "sem validação pixel" do #43; a ponte de credibilidade é a validação soja raster×SIDRA do #44.
- **SICOR = crédito contratado** (não desembolso homogêneo); reflete onde o crédito é *tomado*, adequado à pergunta de concentração.
- **VA agro** mistura valor de lavoura e de pecuária — daí a nuance do Achado 2.
- **Incerteza reportada (D19)**: todo ΔNorte vem com IC95% por bootstrap; o vão latitude↔fronteira é lido como robusto só quando as **faixas não se sobrepõem** (é o caso de valor↔pasto e crédito↔pasto).

## Conexão com a narrativa

**Não muda nenhuma conclusão das 5 camadas — adiciona um eixo espacial-econômico** à Camada 1:

1. **O crédito consolida a massa instalada, não lidera a fronteira** (~75 km ao sul do pasto; investimento mais ao norte que custeio) — casa com #37/#38 (crédito endógeno; câmbio lidera) e #22.
2. **O valor fica quase ancorado enquanto a área marcha** (VA agro só +11 km, marginalmente ≠0; PIB parado; vão valor↔pasto alarga de −84 para −101 km) — um ângulo espacial sobre "crescimento sem desenvolvimento" **sem precisar de IDH-M**, e coerente com a leitura de **fronteira de baixa intensidade ao norte × núcleo intensificado ao sul**.
3. **Abate**: negativo metodológico honesto — a geografia agroindustrial não é acessível com o dado atual (abate municipal é modelado do rebanho).
