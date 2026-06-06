# Pipeline #36 — Robustez da janela do slope (#17)

**Script**: `scripts/robustez_janela_slope.py`
**Quando foi feito**: 2026-06-06.
**Depende de**: #17 (`calcular_taxas_lulc`) — reusa a agregação UF e os slopes (`rolling_slope_hac` + `rolling_slope_hac_centr`), não reimplementa.
**Base metodológica**: [Decisão D12 — estratégia de janelas temporais](../metodologia/janelas_temporais.md), na sua **face de resolução** (a largura da régua de suavização), distinta da face de fronteira testada no [#35](35_robustez_janelas.md).
**Outputs**:
- `data/processed/robustez_janela_slope.csv` — slope por ano × grupo × janela × **método** (trailing e centrada), nível UF.
- `data/processed/robustez_janela_slope_resumo.csv` — concordância por janela (trailing).
- `data/processed/robustez_janela_slope_cruzamento.csv` — cruzamento de zero da pastagem, trailing vs centrada.
- `outputs/robustez/slope_por_janela.png` — slope das 3 classes-narrativa sob 4 janelas (trailing).
- `outputs/robustez/pastagem_trailing_vs_centrada.png` — o deslize do cruzamento da pastagem é artefato do trailing.

---

## Pergunta de pesquisa

As afirmações-manchete de **slope** do [#17](17_taxas_lulc.md) dependem da **largura** da janela móvel? A [Decisão D3](17_taxas_lulc.md) fixou **5 anos** (com a justificativa "inferência vs. narrativa"). A pergunta óbvia de banca é: *por que 5? a história muda em 3, 7 ou 10?* Este pipeline recalcula as manchetes de slope sob janela ∈ {3, 5, 7, 10} e reporta o que sobrevive.

## A intuição: duas faces da D12

O [#35](35_robustez_janelas.md) testou a **face de fronteira** da D12 — *onde* cortar o tempo (atos vs. grade-5a vs. décadas, blocos **disjuntos** = *binning*). Este pipeline testa a **face de resolução** — *quão fina* é a janela móvel de suavização (janelas **sobrepostas** = *smoothing*).

> [!NOTE]
> **Mesmo "5 anos", operações diferentes.** A grade-5a do #35 corta a série em 8 blocos que não se sobrepõem. A janela-5a do #17 desliza ano a ano, sobrepondo-se — cada ano recebe o slope dos seus vizinhos. Confundi-las é fácil; o teste de robustez de cada uma é diferente. Aqui o "knob" é a **largura** da janela móvel, o parâmetro mais consequente do #17.

## Janelas comparadas

| Janela | Papel | Trade-off |
|---|---|---|
| **3 anos** | resolução fina | capta inflexões curtas, mas mais ruidosa |
| **5 anos** | **base (Decisão D3)** | a régua testada |
| **7 anos** | resolução média | suaviza mais |
| **10 anos** | resolução grossa | estável, mas borra fenômenos curtos e **atrasa** o slope trailing |

Cada largura é avaliada em **dois métodos** (ambos do #17): **trailing** (t−W+1..t, usado para inferência — larguras 3/5/7/10) e **centrada** (t−h..t+h, usada para narrativa, sem o viés de atraso — larguras ímpares 3/5/7/9). A centrada serve para **isolar** se um achado depende do atraso do trailing.

## Métricas-manchete recalculadas (nível UF)

- **Pastagem** — ano(s) de **cruzamento de zero** do slope (pico da área; manchete do #17: ~2004), comparado entre **trailing e centrada** (para separar o fenômeno do atraso do trailing).
- **Vegetação** — **desaceleração da perda** (`|slope|` recente < `|slope|` inicial?).
- **Agricultura** — **freada recente** (slope em 2024 < pico do slope?).
- **Formato** — correlação de Pearson da série de slope de cada janela vs. a base (5a).
- **Aceleração** — nº de inflexões `|accel|>2σ` e quais anos recorrem em **todas** as janelas (a métrica mais frágil; ver D5 do #17).

---

## Achados — as manchetes de slope são robustas (com uma sensibilidade informativa)

| Janela | Pasto cruza zero | Veg. desacelera | Agric. freia no recente | Formato (corr vs 5a): veg / pasto / agric |
|---|---|---|---|---|
| **3a** | 2004 | sim (−0,32 → −0,06) | sim (pico +0,26 → +0,01) | +0,98 / +0,99 / +0,85 |
| **5a (base)** | 2004 | sim (−0,30 → −0,05) | sim | +1,00 / +1,00 / +1,00 |
| **7a** | 2006 | sim (−0,29 → −0,04) | sim | +0,99 / +0,99 / +0,89 |
| **10a** | 2007 | sim (−0,27 → −0,04) | sim | +0,96 / +0,97 / **+0,44** |

1. **A desaceleração da vegetação é totalmente robusta.** Em todas as janelas o slope sobe de ~−0,3 para ~−0,05 Mha/ano (a perda de vegetação freia); a forma da série é praticamente idêntica (corr ≥ 0,96).
2. **O cruzamento de zero da pastagem é robusto — e o "deslize" é comprovadamente artefato do trailing.** No trailing o pico aparece em **2004** (3a/5a) e desliza para **2006–2007** nas janelas largas. Isso **não é instabilidade**: a janela *trailing* atrasa por construção quando alargada ("olha para trás" por mais anos). A prova está na versão **centrada**, que não tem esse viés: o cruzamento fica **estável em ~2002–03** em todas as larguras (3a→2003, 5a→2002, 7a→2003, 9a→2003). Ou seja, o pico real da pastagem é ~2002–03, e mesmo a "manchete 2004" do 5a-trailing já embute ~1–2 anos do atraso do trailing — algo a ter em mente ao datar o pico na redação (ver `pastagem_trailing_vs_centrada.png`).
3. **A freada recente da agricultura é robusta — mas o *formato* da série é a única sensibilidade real.** O slope recente < pico em **todas** as janelas. Porém a correlação da agricultura cai para **0,44** entre 5a e 10a, e o **ano do pico** salta entre o início dos 1990 (janelas largas) e ~2005 (janela fina). Leitura: a agricultura teve **duas surtidas** (soja sudoeste no início dos 90 e boom em meados dos 2000); qual delas é "o pico" depende da resolução. A freada recente independe disso; a *cronologia interna* da expansão, não.
4. **A aceleração confirma a D5 — é frágil.** A única inflexão `|accel|>2σ` que recorre em **todas** as janelas é a da **pastagem em 2004**. Vegetação e agricultura **não têm nenhuma** inflexão que sobreviva às 4 janelas. Isso valida o aviso da D5 ("aceleração ruidosa por construção") e diz como ler a `aceleracao_uf.png` do [#20](20_figuras_taxas.md): só o pico da pastagem de 2004 é um ponto de inflexão robusto à resolução.

> **Conclusão**: as manchetes de slope do #17 **não são artefato da janela de 5 anos**. A desaceleração da vegetação e a freada recente da agricultura valem em 3/5/7/10 anos; o pico da pastagem é robusto a menos do atraso esperado do trailing. A escolha da D3 (5 anos) é defensável. As duas sensibilidades — a cronologia interna da agricultura e a aceleração em geral — são **informativas**: dizem que a expansão agrícola é multi-pico e que a aceleração é dominada por ruído fora do pico da pastagem de 2004.

---

## Como ler as figuras

### `slope_por_janela.png`
Três painéis (Vegetação, Pastagem, Agricultura). Em cada um, o slope trailing (Mha/ano) sob as 4 janelas (escala viridis; a base 5a em linha grossa). **Vegetação e pastagem**: as 4 linhas ficam quase coladas — robustez visual. **Agricultura**: leque visível entre janelas (a janela larga achata e desloca o pico) — a sensibilidade de formato. A linha tracejada em 2004 (painel da pastagem) marca o cruzamento de zero da manchete.

![Slope por janela](../../outputs/robustez/slope_por_janela.png)

### `pastagem_trailing_vs_centrada.png`
Dois painéis para o slope da pastagem: **Trailing** (esq.) vs **Centrada** (dir.); triângulos marcam o cruzamento de zero. No trailing, os triângulos **se espalham** (2004→2007 conforme a janela alarga) e as curvas se deslocam para a direita — o atraso. Na centrada, as curvas ficam **coladas** e os triângulos **se agrupam em ~2002–03**, independentes da largura. É a demonstração visual de que o deslize do achado #2 é viés do trailing, não instabilidade do fenômeno.

![Pastagem: trailing vs centrada](../../outputs/robustez/pastagem_trailing_vs_centrada.png)

---

## Decisões metodológicas

- **Trailing como régua principal, centrada como controle** — o trailing replica a janela de inferência/testes piecewise do #17 (D3); a centrada (`rolling_slope_hac_centr`, sem viés de atraso) entra só para isolar se um achado depende do atraso do trailing — caso do cruzamento da pastagem (achado #2).
- **Centrada exige largura ímpar** (janela simétrica t−h..t+h ⇒ 2h+1 pontos), por isso suas larguras são {3,5,7,9} como contraparte das {3,5,7,10} do trailing.
- **O slope é o ponto estimado do OLS** — o `cov_type=HAC` do #17 afeta só o erro padrão, não o slope; logo a robustez aqui é da própria inclinação.
- **Reuso integral do #17** — agregação UF (`agregar_por_grupo`) e slopes (`rolling_slope_hac`, `rolling_slope_hac_centr`) vêm do script original; só a largura da janela e o método variam.
- **Concordância pela mesma tabela de decisão da D12** — "aparece em todas → robusto; some/varia na grossa → sensibilidade de resolução, localize o fenômeno".

## Limitações

- Cobre o **nível UF** e as **3 classes-narrativa** (veg/pasto/agric) — não cada classe nem os níveis municipal/meso.
- Testa a **largura** da janela, não outras escolhas de suavização (ex.: kernel, LOESS).
- Não toca o **delta** (`Δlulc` ano-a-ano), que é window-independent e alimenta o [#23](23_did.md) — a robustez aqui é do **slope**, não do DiD.
