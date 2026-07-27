# Pipeline #23 — Diferença-em-Diferenças (GO vs MT/TO)

**Script**: `scripts/piecewise_did.py`
**Status**: ✅ executado
**Depende de**: #17 (`taxas_lulc_goias.csv`), GEE (séries MT/TO baixadas)

## O que faz

Diferença-em-Diferenças piecewise para avaliar se marcos regulatórios/econômicos tiveram impacto diferencial em Goiás comparado a Mato Grosso e Tocantins (controles do bioma Cerrado).

**Decisão D9**: GO como tratamento, MT+TO como controles do Cerrado. Também testado com cada estado isoladamente.

**Especificação**: Δlulc_{st} = α_s + γ_t + β·treated_s × post_t + ε_{st}

## Marcos testados

| Ano | Marco | Janela DiD |
|-----|-------|------------|
| 1995 | Estabilização (Plano Real) | 1990–2000 |
| 2003 | Commodity Boom | 1998–2008 |
| 2012 | Código Florestal | 2007–2017 |
| 2018 | Cerrado Manifesto + consolidação frigorífica | 2013–2023 |

## Classes LULC

vegetacao_natural, pastagem, agricultura

## Controles

- **Combined**: MT + TO
- **MT only**: Mato Grosso
- **TO only**: Tocantins

## Resultados principais (9/36 significativos a 5%)

| Classe | Marco | Controle | β_did | p | Interpretação |
|--------|-------|---------|-------|---|---------------|
| Veg. natural | 1995 | TO | +0,08 | 0,005 | Plano Real favoreceu vegetação em GO vs TO |
| Pastagem | 1995 | MT | −0,23 | 0,022 | Pastagem expandiu menos em GO vs MT após estabilização |
| Pastagem | 2012 | Combined | +0,16 | 0,010 | Após Código Florestal, pastagem expandiu mais em GO vs MT+TO |
| Pastagem | 2012 | MT | +0,30 | <0,001 | Efeito forte vs MT |
| Pastagem | 2018 | Combined | −0,26 | 0,001 | Após Cerrado Manifesto, pastagem retraiu em GO vs MT+TO (efeito puxado pelo MT) |
| Pastagem | 2018 | MT | −0,44 | <0,001 | Efeito forte vs MT — **não se replica vs TO** (β=−0,07, p=0,21) |
| Agricultura | 1995 | TO | −0,07 | 0,046 | Agricultura desacelerou em GO vs TO |
| Agricultura | 2012 | MT | −0,19 | 0,005 | Agricultura expandiu menos em GO vs MT após Código Florestal — **não vs TO** (β=+0,01, p=0,86) |
| Agricultura | 2018 | MT | +0,17 | 0,011 | Agricultura expandiu mais em GO vs MT após Cerrado Manifesto — **sinal inverte vs TO** (β=−0,06, p=0,07) |

**Nota crítica**: Os efeitos de pastagem e agricultura em 2012 e 2018 são **dirigidos pelo contraste com MT**. Com TO isolado (controle mais comparável: ~92% Cerrado vs ~40% no MT), nenhum dos efeitos 2012/2018 sobrevive, e a direção de "Agricultura × 2018" inverte de sinal. O único achado robusto cross-especificação é **Veg. natural × 1995 vs TO** (β=+0,08, p=0,005). A leitura honesta é: o β contra MT capta tanto "GO divergindo do Cerrado" quanto "MT divergindo do Cerrado" (Moratória da Soja Amazônia 2006, conversão pastagem→soja na borda da floresta). **Hierarquizar TO-isolado como especificação principal** e reportar MT/combined como sensibilidade.

## Robustez (2026-05-14)

Três extensões para defender o DiD junto à banca:

### Event-study por marco

Estima `β_k` para `k ∈ [-5, +5]`, com `k=-1` omitido (baseline). Spec:

```
Δlulc_{s,t} = α_s + λ_t + Σ_{k≠-1} β_k · D(t-marco=k) · treated_s + ε
```

**Limitação técnica**: identificação só é possível com **controle combined (3 UFs, year FE)**. Com TO ou MT isolado (2 UFs), cada dummy `tk_k` fira em uma única observação, produzindo SE espúrios ~0. Por isso o event-study é restrito a combined; TO-isolado/MT-isolado seguem como DiD pontual.

**Resultado**: das 12 (classe × marco) combinações em combined, **apenas 3 lags pré-marco têm β significativo a 5%** — todos no par `agricultura × 1995` (k=-5, -4, -2). Os outros 33 lags pré-marco (k<-1) ficam dentro do IC do zero → **parallel trends sustentada para 11 de 12 pares**.

### Placebo (marco falso 5 anos antes)

Re-roda DiD com `marco_falso = marco_real - 5`, janela ±3 anos (não sobrepõe com marco real). De 36 modelos placebo, **9 saem significativos** (idealmente zero):

| Par com placebo significativo | β_placebo | p |
|---|---|---|
| agricultura × 2012 [TO] | −0,11 | 0,027 |
| agricultura × 2012 [MT] | +0,29 | <0,001 |
| agricultura × 2018 [MT] | −0,21 | 0,015 |
| pastagem × 2012 [combined] | +0,20 | 0,042 |
| pastagem × 2012 [MT] | +0,35 | 0,017 |
| pastagem × 2018 [MT] | +0,21 | 0,031 |
| veg.natural × 2003 [TO] | +0,07 | 0,017 |
| veg.natural × 2012 [combined] | −0,41 | 0,046 |
| veg.natural × 2012 [MT] | −0,81 | <0,001 |

**Leitura**: os efeitos pós-2012 vs MT e combined estão **fortemente contaminados** por dinâmica pré-existente — o "efeito" do marco pode estar capturando tendências do Moratória da Soja (2006) ou expansão pastagem-soja em MT, não causalidade do marco real. **Reforça hierarquia TO-isolado**: o único marco com placebo limpo em todos os controles é **1995 (Plano Real)**.

### Achado consolidado pós-robustez

Apenas um par sobrevive ao conjunto de testes (parallel trends ok + placebo n.s. + DiD sig em TO): **Veg. natural × 1995 vs TO, β=+0,08, p=0,005**. É o único par com padrão estatístico limpo. Demais β positivos/negativos pós-2012 viram **co-movimentos do Cerrado** com possível contribuição do marco, não atribuíveis.

> 🛑 **Rebaixamento do enquadramento (25/jul/2026): este pipeline é uma *sensibilidade de
> co-movimento*, não uma estimativa causal — nem no par sobrevivente.**
>
> A versão anterior desta linha dizia que Veg×1995 vs TO era "a única evidência DiD interpretável
> como causal". **Não é**, e a razão é anterior a qualquer teste de robustez: **os quatro marcos são
> federais/nacionais**. Plano Real, Lei Kandir, Código Florestal e Cerrado Manifesto **não tratam
> Goiás e não tratam Tocantins** — incidem sobre os dois ao mesmo tempo. Num DiD, `treated × post`
> só identifica efeito causal do marco se o grupo de controle **não** tiver recebido o tratamento;
> aqui recebeu. O que o β mede, então, é **exposição diferencial** a um choque comum (GO e TO têm
> estruturas produtivas diferentes e reagem de modo diferente ao mesmo Plano Real), o que é
> equivalente a uma **tendência diferencial pós-marco** — não ao efeito do marco.
>
> Some-se a isso: (i) **poder baixíssimo** — a especificação identificada exige o controle
> *combined* (3 UFs); com TO ou MT isolados cada dummy `tk_k` fira numa única observação (ver
> Limitação técnica acima); (ii) **9 de 36 placebos significativos**, quando o esperado seria ~2;
> (iii) **tensão de datação** com o [#26](26_deteccao_quebras.md)/[#29](29_triangulacao_periodizacao.md),
> que localizam a quebra da vegetação em **1998** e a atribuem à **Lei Kandir (1996)** — não em
> 1994/95. Se a inflexão real é 1998, a janela 1990–2000 do "marco 1995" está capturando o começo
> de um movimento que outro marco explica melhor.
>
> **Como usar o #23 na redação.** Como **descrição comparativa**: "no pós-Plano Real, a vegetação
> natural de Goiás se manteve acima da trajetória de Tocantins" — um fato de co-movimento, útil
> como pano de fundo. **Nunca** como "o Plano Real causou X em Goiás", e **nunca** como uma das
> pernas de evidência. A identificação causal dos marcos exigiria variação **subnacional** no
> tratamento (ex.: municípios diferencialmente expostos à Kandir por pauta exportadora), que este
> desenho não tem.

### Saídas adicionais

| Arquivo | Conteúdo |
|---|---|
| `outputs/correlacoes/event_study_resultados.csv` | β_k para 12 pares × 11 lags = 132 linhas |
| `outputs/correlacoes/event_study_*.png` | 12 figuras de event-study (control=combined) |
| `outputs/correlacoes/placebo_resultados.csv` | 36 modelos placebo |

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `data/cache/did/mt_uf_lulc.csv` | Série anual UF MT (40 anos × 6 classes, Mha) |
| `data/cache/did/to_uf_lulc.csv` | Série anual UF TO (40 anos × 6 classes, Mha) |
| `outputs/correlacoes/did_resultados.csv` | 36 modelos: β_did, SE, p, n_obs (ordenados TO→combined→MT) |
| `outputs/correlacoes/event_study_resultados.csv` | β_k event-study (combined, com year FE) |
| `outputs/correlacoes/placebo_resultados.csv` | 36 modelos placebo (marco_real − 5) |
| `outputs/correlacoes/did_*.png` | 12 gráficos DiD (3 classes × 4 marcos) |
| `outputs/correlacoes/event_study_*.png` | 12 gráficos event-study |

## Como rodar

### Download (já executado, cache salvo)

```bash
python scripts/piecewise_did.py --download
```

### Análise DiD

```bash
python scripts/piecewise_did.py
```

## Limitações

- N = 3 UFs (GO, MT, TO) → baixo poder para efeitos fixos de UF.
- MT tem composição LULC muito diferente (Floresta Amazônica, soja em larga escala).
- Séries UF agregadas (não municipal) → sem variação intra-estado para clusterizar.
- Inferência via OLS com HC1 — não é painel convencional dado o N pequeno.