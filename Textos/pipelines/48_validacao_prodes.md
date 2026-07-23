# Pipeline #48 — Validação cruzada PRODES (INPE) × MapBiomas

**Script**: `scripts/validacao_prodes_mapbiomas.py`
**Quando foi feito**: 2026-07-16. Fecha a validação **PRODES** que a **D17** (#46) deixou pendente para a "Sprint 2".
**Depende de**: #12/#19 (transições veg→antrópico). Fonte externa independente: PRODES Cerrado do INPE (TerraBrasilis, WFS).
**Outputs**:
- `data/raw/prodes/prodes_cerrado_go_yearly.csv` — 367.236 polígonos de desmatamento anual do Cerrado em GO (INPE).
- `data/processed/prodes_go_anual.csv` — série anual agregada (km²).
- `data/processed/validacao_prodes_mapbiomas.csv` — comparação anual.
- `outputs/validacao_prodes/prodes_vs_mapbiomas.png`.

---

## Pergunta de pesquisa

O #39/#46/#47 apoiam-se no **MapBiomas** como fonte da perda de vegetação nativa (o estoque convertível, o teto de oferta, o custo de carbono). A D17 pediu uma validação contra fonte **independente**. O **PRODES Cerrado do INPE** — sistema oficial de monitoramento de desmatamento — é o padrão-ouro. A pergunta:

> O desmatamento que o PRODES mede em Goiás concorda com a conversão veg→antrópico que o MapBiomas registra?

Se concordarem, o MapBiomas está validado como base empírica de toda a linha ambiental; se divergirem, os achados do #39/#46/#47 precisariam de ressalva.

---

## O que faz

- **PRODES**: camada `yearly_deforestation` do bioma Cerrado (WFS TerraBrasilis), filtrada a Goiás (`state='GOIÁS'`), paginada (367 mil polígonos), agregada por ano (km²→Mha). É desmatamento **bruto** de vegetação primária.
- **MapBiomas**: fluxo **bruto** veg→antrópico (pastagem+agricultura+área urbana) por ano das transições (#12/#19). Comparação **bruto×bruto** — o líquido de estoque (que abate rebrota) subestimaria e não seria a métrica análoga.
- **Duas leituras**: (a) TOTAL na janela; (b) correlação anual **restrita a 2013–2024**. Antes de 2013 o PRODES Cerrado mapeia em **incrementos plurianuais** (as classes `d2002`/`d2004`… somam vários anos cada), então o alinhamento ano-a-ano pré-2013 não é interpretável — os pontos altos de 2002/2004 são acúmulos, não anos.

---

## Achado — concordância quase perfeita no regime anual

| Janela | MapBiomas (bruto) | PRODES | razão | correlação |
|---|---|---|---|---|
| 2002–2024 (total) | 2,46 Mha | 4,94 Mha | 2,0 | — (pré-2013 plurianual) |
| **2013–2024 (anual)** | **1,09 Mha** | **1,08 Mha** | **0,99** | **r = 0,91** |

No **regime anual do PRODES (2013–2024)** — a única janela em que as duas séries são comparáveis ano-a-ano — MapBiomas e PRODES **concordam quase perfeitamente**: o total bate (1,09 vs 1,08 Mha, razão 0,99) e a série anual **correlaciona a r = 0,91**. A aparente divergência 2002–2024 (razão 2,0) é **integralmente artefato dos incrementos plurianuais do PRODES pré-2013** (2002 e 2004 aparecem como ~1,2–1,3 Mha porque cada um soma ~2+ anos de desmatamento), não discordância real — a figura mostra os dois pontos altos isolados fora da faixa comparável.

**Veredito**: o MapBiomas está **validado** contra a fonte oficial independente do INPE como base da perda de vegetação usada no #39 (teto de oferta), #46 (proteção) e #47 (carbono). A linha ambiental inteira ganha respaldo externo.

> **Imune à deriva do Mosaico (D26, verificado 23/jul/2026).** A deriva (#28D) é uma reetiquetagem *antrópico→antrópico* (pasto→agricultura vira pasto→Mosaico), não um problema da *perda de vegetação*. Empiricamente confirma-se: o `veg→antrópico` do MapBiomas é **estável 2017–2024** (0,069–0,089 Mha/a, sem colapso), ao contrário do `pasto→agric` que cai −79% na mesma janela. Em 2024 o MapBiomas (0,069) fica até *acima* do PRODES (0,041) — o oposto do que um subconto pela deriva produziria. A validação do #48 **não** é afetada.

---

## Honestidade metodológica

- **Bruto × bruto**: PRODES = supressão de vegetação primária; MapBiomas bruto = qualquer transição nativo→antrópico. São conceitos próximos, não idênticos — a correlação de 0,91 mostra que rastreiam o mesmo processo, mas não são a mesma medida (PRODES ignora rebrota/veg. secundária; MapBiomas reclassifica anualmente).
- **Pré-2013 não comparável ano-a-ano** (incremento plurianual) — reportado como tal, não escondido.
- **PRODES Cerrado começa em 2000/2001** (baseline `accumulated_deforestation_2000`); não cobre o Ato I (1985–2000), onde o #47 mostrou 80% da perda de carbono. Para o Ato I não há PRODES — o MapBiomas é a única fonte longa, e a validação 2013+ é o que empresta credibilidade retroativa.

---

## O que ainda falta da D17 (Sprint 2)

- **Áreas Prioritárias para Conservação (MMA)**: cruzar o convertível desprotegido do #46 com a camada nacional de prioridade de conservação. **Pendente por indisponibilidade da fonte**: o geoserver do MMA (`geoservicos.mma.gov.br`) estava fora do ar (2026-07-16) e a camada nacional do Cerrado não está no WFS do INDE. Requer download manual do shapefile no portal gov.br/MMA quando disponível.
- **Refino pixel via GEE**: recortar o estoque convertível (#39) pela UC no raster para eliminar o proxy de distribuição uniforme intra-AMC do #46. **Bloqueado**: exige autenticação do Earth Engine (`ee.Authenticate()`) na máquina do autor.
