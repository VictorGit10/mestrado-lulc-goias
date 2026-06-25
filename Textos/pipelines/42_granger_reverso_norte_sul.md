# Pipeline #42 — O Granger reverso Norte→Sul: artefato ou inversão da leitura?

**Script**: `scripts/granger_reverso_norte_sul.py`
**Quando foi feito**: 2026-06-08. Fio 5 do backlog (a ponta solta que o #34 deixou).
**Depende de**: #34 (`deslocamento_series_regionais.csv`, séries Sul/Norte/Centro), #37 (`drivers_macro_anual.csv`, câmbio/crédito/preço). Reusa o espírito de Granger/CCF do #34.
**Outputs**:
- `data/processed/granger_reverso_lags.csv` — perfil de lags (fwd/rev/bov), F clássico + Wald HAC.
- `data/processed/granger_reverso_estacionaria.csv` — ADF/KPSS + Toda-Yamamoto.
- `data/processed/granger_reverso_drivecomum.csv` — modelos com controle dos drivers macro.
- `data/processed/granger_reverso_robustez.csv` — detrend, secas, subperíodos, placebos.
- `outputs/granger_reverso/perfil_lags.png`, `drive_comum.png`, `veredito.png`.

---

## Pergunta de pesquisa

O #34 fechou a narrativa Sul→Norte num **nulo causal** (sem precedência temporal, sem spillover direcional) e leu o padrão como **reorganização sob drive comum**. Mas deixou uma ponta solta: o teste **reverso** `ΔPasto_Norte → ΔAgric_Sul` deu **Granger p=0,0007 (lag 1)** — significativo —, descartado só com a justificativa de "N pequeno". Se esse sinal fosse **real**, ele **inverteria a leitura**: seria o Norte antecedendo o Sul, não o contrário.

Este pipeline cutuca a ponta com o rigor que o #34 não teve tempo de aplicar, discriminando três hipóteses:

| Hipótese | Mecanismo | O que prevê |
|---|---|---|
| **H_inverte** | Norte→Sul causal | o pasto do Norte de fato antecede e prevê a lavoura do Sul |
| **H_comum** | timing diferencial sob drive comum (#37) | os dois respondem ao boom; o pasto do Norte responde ~1 ano antes da lavoura do Sul — liderança mecânica, não causal |
| **H_espurio** | artefato estatístico | séries-tendência suaves + N pequeno geram precedência espúria que some sob método correto |

---

## O que faz (4 blocos, cada um isola uma hipótese)

- **Bloco A — Reproduzir e caracterizar.** Perfil de lags 1/2/3, F clássico vs **Wald HAC** (Newey-West), assimetria pasto×rebanho.
- **Bloco B — Estacionariedade + Toda-Yamamoto.** ADF/KPSS em níveis e diferenças; **Toda-Yamamoto** (VAR aumentado, Wald só nos lags próprios) — o Granger correto para séries possivelmente integradas. → testa **H_espurio**.
- **Bloco C — DECISIVO: controlar pelo drive comum (#37).** Regride `ΔAgric_Sul ~ ΔAgric_Sul.L1 + ΔPasto_Norte.L1 + drivers` (câmbio/crédito/preço, Δlog, contemp.+defasados). → discrimina **H_comum vs H_inverte**.
- **Bloco D — Robustez.** Detrend linear, drop secas 1985/2010 (espírito #41), subperíodos, e uma **bateria de placebos direcionais**.

---

## Achados — o reverso é co-tendência espúria, NÃO uma inversão

### 1. O reverso reproduz e parece robusto (a armadilha)
`ΔPasto_Norte → ΔAgric_Sul`: Granger **p=0,0007** (lag 1), e até **fortalece sob HAC** (p=0,0003; β=+0,44). Tomado isolado, parece um achado firme. Mas três coisas já incomodam:
- **Só no lag 1**: o coeficiente individual perde significância no lag 2 (HAC p=0,34) e 3.
- **Só a área de pasto, não o rebanho**: `ΔBovinos_Norte → ΔAgric_Sul` é **nulo** em todos os lags (p=0,72/0,19/0,30). Um mecanismo econômico coerente Norte→Sul deveria aparecer também no rebanho.

### 2. As séries são integradas — a regressão do #34 era *desbalanceada*
ADF/KPSS:

| Série | ADF | KPSS | Diagnóstico |
|---|---|---|---|
| agric_Sul (nível) | p=0,011 (estac.) | p=0,010 (não) | ~**I(0)** (limítrofe, tendência-estac.) |
| pasto_Norte (nível) | p=0,96 (não) | p=0,010 (não) | integrada |
| Δagric_Sul | p=0,001 (estac.) | p=0,050 | **estacionária** |
| **Δpasto_Norte** | **p=0,922 (NÃO-estac.)** | p=0,010 (não) | **ainda integrada ⇒ pasto_Norte é I(2)** |

O ponto-âncora: **a 1ª diferença de pasto_Norte continua não-estacionária**. O #34 rodou o Granger sobre 1as diferenças — ou seja, regrediu uma série **estacionária** (Δagric_Sul) sobre uma **não-estacionária** (Δpasto_Norte). É uma **regressão desbalanceada**, a montagem clássica de **precedência espúria**. E como `agric_Sul ~ I(0)` e `pasto_Norte ~ I(2)` têm **ordens de integração diferentes**, não podem nem ser cointegradas — não há relação de longo prazo estável entre os níveis para detectar.

### 3. O método correto (Toda-Yamamoto) APAGA tudo
Com `dmax=2` (a ordem de integração do pasto_Norte), o Toda-Yamamoto é robusto a integração/cointegração. Resultado:

| Direção | TY lag 1 | TY lag 2 |
|---|---|---|
| **REVERSO** (Pasto_N→Agric_S) | **p=0,45** | p=0,75 |
| Sul→Norte (Agric_S→Pasto_N) | p=0,25 | p=0,25 |

**Nenhuma direção** mostra precedência. O sinal de lead-lag **evapora** sob o teste correto — incluindo o forward (logo, isto **não** autoriza reivindicar Sul→Norte; o correto é **co-movimento sem liderança temporal em nenhuma direção**, exatamente o que o #34 já dizia).

### 4. Os placebos provam a não-especificidade (a evidência mais limpa)
Se houvesse um canal **Norte→Sul agrícola** real, ele não deveria acender onde não há mecanismo. Mas acende em tudo (HAC OLS lag 1):

| Relação | β | p | deveria? |
|---|---|---|---|
| **ALVO** Pasto_N → Agric_S | +0,44 | ~0,000 | — |
| placebo Pasto_**Centro** → Agric_S | +0,53 | ~0,000 | não |
| placebo Pasto_N → Agric_**Centro** | +0,05 | 0,034 | não |
| placebo Pasto_N → **Pasto_S** | +0,46 | **0,0007** | **não** (mesma magnitude do alvo!) |
| placebo Agric_N → Agric_S | −1,14 | 0,033 | não (sinal trocado) |

Qualquer série de área **nortenha/central** suave "Granger-lidera" qualquer série **sulista** suave no lag 1 — inclusive o pasto do Norte "prevendo" o **pasto do Sul** com o mesmo p do achado-manchete. Isso é assinatura de **co-tendência espúria**, não de um mecanismo causal direcionado.

### 5. Por que o Bloco C (drive comum) NÃO salva o H_inverte
O termo `ΔPasto_Norte.L1` **persiste** controlando os drivers (p=0,0002). Isoladamente pareceria robustez — é a **armadilha**. Mas os controles são Δlog **estacionários**; eles não conseguem absorver a **tendência espúria** de uma série I(2). Persistir aqui é o esperado para um artefato de tendência, não evidência de causa. Some-se: **detrend linear** derruba o alvo para o limite (p=0,050). O Bloco C só mostra que o artefato **não** é um confundidor de timing de baixa ordem — é um problema de **integração**, que só o Bloco B (TY) e o Bloco D (placebos) expõem.

### 6. Veredito
> O Granger reverso `ΔPasto_Norte → ΔAgric_Sul` (p=0,0007) é um **artefato de regressão espúria** entre séries integradas de tendência suave — **não** uma inversão causal Norte→Sul. Ele **não derruba** o #34; ao contrário, **reforça** a leitura de **co-evolução sob drive comum sem precedência temporal em nenhuma direção**. A única ponta que poderia inverter a narrativa Sul→Norte está agora explicada e descartada em **base metodológica sólida** — não mais com o aceno de "N pequeno".

Entre H_comum e H_espurio, o peso é em **H_espurio** (a precedência é não-específica e não morre com o controle do drive); mas para a dissertação as duas compartilham a conclusão operativa: **não há inversão causal**.

---

## Como ler as figuras

### `veredito.png` — a figura-manchete
**Painel 1**: o Granger ingênuo (1ª dif, rosa) acende o reverso (p=0,0007), mas o **Toda-Yamamoto** (azul, correto p/ I(2)) **apaga as duas direções** (p=0,45 e 0,25). **Painel 2**: a "precedência reversa" não é específica — placebos que não deveriam acender acendem igual ao alvo (Pasto_N→Pasto_S com o mesmo p=0,0007).

![Veredito](../../outputs/granger_reverso/veredito.png)

### `perfil_lags.png` — fragilidade e assimetria
O reverso (rosa) só é baixo no lag 1; o rebanho (laranja) e o forward (verde) ficam altos. Mostra que o sinal vive num único lag e só na área de pasto.

### `drive_comum.png` — a armadilha do Bloco C
O termo `ΔPasto_Norte.L1` persiste em todos os modelos com drivers — parece robusto, mas (ver §5) é o que se espera de um artefato de tendência, não prova de causa.

---

## Decisão metodológica nova — D16

**Para as séries de área/rebanho das AMC (suaves, fortemente integradas), o Granger ingênuo em 1ª diferença fabrica precedência espúria no lag 1.** Antes de ler qualquer lead-lag agregado como causal, exigir: (i) diagnóstico de integração (ADF/KPSS) das duas séries — uma regressão com ordens de integração distintas é desbalanceada; (ii) **Toda-Yamamoto** (robusto a integração); (iii) **bateria de placebos direcionais** (a precedência some quando o par não tem mecanismo?). É a irmã de séries-temporais da **D14** (parcial controlando latitude em cross-section) e **D15** (alinhamento fogo↔conversão). Aplica-se retroativamente como ressalva ao lead-lag agregado do #34 e do #41 (Granger N≈38).

---

## Limitações honestas

- **N pequeno** (38 1as diferenças). Mas o veredito **não** se apoia num nulo de baixo poder: o resultado espúrio era **significativo**, e o explicamos com diagnóstico de integração + placebos (válidos neste N), não com ausência de poder.
- **As ordens de integração são incertas em n≈40** — agric_Sul é I(0) por ADF mas o KPSS discorda (trend-stationary vs raiz unitária é ambíguo). A âncora robusta é `Δpasto_Norte` ser não-estacionária (ADF p=0,92), o que já basta para tornar a regressão original desbalanceada.
- **O próprio Toda-Yamamoto perde poder** (dmax=2 ⇒ k=3–4 lags sobre n≈37). Por isso o veredito se apoia em TY **+** placebos **+** detrend em conjunto, não em TY isolado.
- **Subperíodos** (D3) têm n≈18–19 — reportados, não decisivos.

---

## Conexão com a narrativa

Fecha o **fio 5** do backlog. A narrativa Sul→Norte (#32/#33/#34) sai deste exame **mais forte e mais honesta**: as três camadas mais o #37 já diziam "reorganização espacial sob drive comum, sem deslocamento causal"; agora o **único contra-resultado** que sobrava (o reverso p=0,0007) está caracterizado como **artefato de co-tendência**, não como inversão. O quadro final permanece: **co-evolução sob forças de mercado comuns sobre um gradiente de aptidão**, sem precedência temporal limpa em nenhuma direção.
