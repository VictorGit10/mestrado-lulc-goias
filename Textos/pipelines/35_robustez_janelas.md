# Pipeline #35 — Robustez de janelas temporais (#32 e #33)

**Script**: `scripts/robustez_janelas.py`
**Quando foi feito**: 2026-06-06.
**Depende de**: #32 (`centro_massa`) e #33 (`transicoes_regionais`) — reusa as duas máquinas, não reimplementa.
**Base metodológica**: [Decisão D12 — estratégia de janelas temporais](../metodologia/janelas_temporais.md) (o *método geral*; este pipeline é a primeira aplicação).
**Outputs**:
- `data/processed/robustez_velocidade_ns.csv` — velocidade N–S por esquema × janela × variável (#32).
- `data/processed/robustez_fluxos_regionais.csv` — fluxos regionais por esquema × janela (#33).
- `outputs/robustez/velocidade_ns.png` — #32 sob cada esquema.
- `outputs/robustez/fluxos_regionais.png` — #33 sob cada esquema.

---

## Pergunta de pesquisa

Os achados-manchete das Camadas 1 (#32) e 2 (#33) dependem de **onde** cortamos o tempo — das fronteiras data-driven dos atos? Ou sobrevivem a réguas **exógenas e de duração igual**? É o teste de **robustez multi-resolução** (à prova de banca), motivado pela discussão metodológica de 2026-06-06.

## A intuição: a mesma história em três réguas

Se a narrativa Sul→Norte só aparece quando se usa exatamente os atos (1985–2000 / 2001–2019 / 2020–2024), ela é frágil — pode ser artefato da escolha de fronteira. Se aparece **também** numa grade regular de 5 anos e em décadas (réguas que ignoram os atos), ela é robusta. Este pipeline recalcula as métricas-manchete sob cada régua e compara.

> [!NOTE]
> **Por que grade regular e não "blocos de 5 anos dentro dos atos"?** Os atos não são múltiplos de 5 (têm 16/19/5 anos), então sub-dividi-los em blocos de 5 deixa restos desiguais — e, pior, **re-importa as fronteiras dos atos**, anulando o teste. Uma grade regular de 5 anos sobre a série inteira (8 blocos: 1985–89 … 2020–24) é **exógena** às fronteiras — é isso que a torna um teste válido. O último bloco (2020–24) coincide com o Ato III, então o período recente fica diretamente comparável.

## Esquemas comparados

| Esquema | Janelas | Papel |
|---|---|---|
| **Contínua** (anual) + **Janela única** (1985–2024) | 40 pontos / 1 bloco | espinha dorsal + resumo |
| **Atos** (data-driven, #29) | 3 (16/19/5 anos) | **linha de base** testada |
| **Grade 5 anos** | 8 blocos de 5 anos | régua regular exógena |
| **Décadas** | 4 blocos de 10 anos | régua regular grossa |

## Métricas-manchete recalculadas

- **#32 — velocidade para o norte (km/ano)** do centro de massa de cada variável, por janela = inclinação OLS do *northing* (EPSG:5880) vs ano. Checagem: pasto/rebanho sobem (>0) e a **agricultura desacelera** na janela recente?
- **#33 — taxa anual (Mha/ano)** de `pasto→agric` (Sul) e `veg→pasto` (Norte), por janela. Checagem: o **gradiente** (Sul faz pasto→agric; Norte faz veg→pasto) vale em toda janela?

---

## Achados — os resultados são robustos

| Esquema | Pasto sobe? | Agricultura desacelera no recente? | Sul>Norte em pasto→agric | Norte>Sul em veg→pasto |
|---|---|---|---|---|
| **Atos** | sim (+2,2 km/a) | sim (+0,1 vs méd +1,4) | **100%** das janelas | **100%** |
| **Grade 5 anos** | sim (+2,0 km/a) | sim (+0,1 vs méd +1,6) | **100%** | 88% |
| **Décadas** | sim (+2,0 km/a) | mais fraco (+0,9 vs +1,5) | **100%** | 75% |

1. **A marcha do pasto ao norte é robusta** — velocidade média ~+2 km/ano em todos os esquemas.
2. **A desaceleração recente da agricultura é robusta — mas dependente de resolução.** Nítida nos Atos e na Grade-5 (a janela recente isola 2020–24); **diluída nas Décadas**, porque a década 2015–2024 mistura o boom pré-2020 com o congelamento pós-2020. Isso **justifica** manter janelas finas / a fronteira de 2020 dos atos: o congelamento é um fenômeno pós-2020 que réguas grossas borram.
3. **O gradiente `Sul: pasto→agric` é cravado**: o Sul converte mais pasto em agricultura que o Norte em **100% das janelas, em todos os esquemas**.
4. **O gradiente `Norte: veg→pasto` é robusto, com leve oscilação no fino** (100%/88%/75%) — coerente com o achado honesto do #33 (gradiente **relativo, não exclusivo**: o Sul também foi fronteira de `veg→pasto` no início).
5. **O deslocamento líquido 1985→2024 é idêntico em todo esquema** (agricultura +65, pasto +78, rebanho +67, veg +8 km) — depende só dos extremos, é a robustez trivial.

> **Conclusão**: a narrativa Sul→Norte (#32/#33) **não é artefato das fronteiras dos atos**. Sobrevive a réguas regulares e exógenas. A única sensibilidade — a nitidez do congelamento recente da agricultura — é informativa: ela confirma que o fenômeno é **pós-2020** e endossa o uso de janelas que isolam esse período.

---

## Como ler as figuras

### `velocidade_ns.png` (#32)
Três painéis (Atos, Grade 5 anos, Décadas). Em cada um, a velocidade para o norte (km/ano) de cada variável por janela. Pasto (laranja) e rebanho (vinho) ficam **acima de zero**; agricultura (magenta) **cai rumo à janela recente**; vegetação (verde) perto de zero. O padrão se repete nas três réguas.

![Velocidade N–S por esquema](../../outputs/robustez/velocidade_ns.png)

### `fluxos_regionais.png` (#33)
Três painéis. `Sul: pasto→agric` (rosa) e `Norte: veg→pasto` (verde) por janela, em Mha/ano. As duas assinaturas regionais declinam ao longo do tempo (colapso recente do pasto→agric no Sul) e o gradiente persiste — em todas as réguas.

![Fluxos regionais por esquema](../../outputs/robustez/fluxos_regionais.png)

---

## Decisões metodológicas

- **Grade regular exógena** (não aninhada nos atos) — ver `[!NOTE]` acima.
- **Velocidade = inclinação OLS do northing vs ano na janela** (não diferença de extremos) — usa todos os anos da janela, robusto a ruído de ponta.
- **Fluxos anualizados** (Mha/ano) — atos/janelas têm durações diferentes; total absoluto enganaria.
- **Reuso integral de #32 e #33** — as séries e recortes vêm das máquinas originais, garantindo consistência.

## Limitações

- A robustez cobre as **métricas-manchete** (velocidade N–S; gradiente de fluxos), não cada número dos pipelines originais.
- A grade de 5 anos é mais ruidosa que os atos/décadas (mais janelas, menos anos cada) — visível como oscilação na figura do #32, mas sem mudar a direção dos achados.
- Não altera a conclusão causal do #34 (não-confirmação de deslocamento): robustez de **descrição**, não de causalidade.
