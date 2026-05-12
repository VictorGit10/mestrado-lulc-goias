# Pipeline #20 — Figuras de taxas de variação LULC

**Script**: `scripts/figuras_taxas.py`
**Depende de**: Pipeline #17 (`taxas_lulc_goias.csv`, `taxas_lulc_municipal.csv`, `taxas_lulc_mesorregioes.csv`)
**Outputs**: `outputs/taxas/` (7 PNGs)

## O que faz

Gera figuras estáticas para a dissertação a partir dos dados de taxas (Pipeline #17).

## Figuras

| # | Arquivo | Descrição | Nível |
|---|---------|-----------|-------|
| 1 | `slope_uf_centrada.png` | Slope 5a centrada com faixa ±1.96 SE e marcos políticos | UF |
| 2 | `slope_mesorregioes.png` | Slope 5a trailing: UF + 5 mesorregiões sobrepostas | UF + meso |
| 3 | `delta_uf.png` | Barras de variação ano-a-ano com média 3a | UF |
| 4 | `mapa_slope_vegetacao_natural.png` | Choropleth slope municipal (5 períodos) | Municipal |
| 5 | `mapa_slope_pastagem.png` | Choropleth slope municipal (5 períodos) | Municipal |
| 6 | `mapa_slope_agricultura.png` | Choropleth slope municipal (5 períodos) | Municipal |
| 7 | `aceleracao_uf.png` | Aceleração (2a derivada) com pontos de inflexão >2σ | UF |

## Períodos dos mapas municipais

Cada mapa mostra 5 painéis com o `slope_5a_trail` no ano central de cada ATOS:

| Rótulo | Ano central |
|--------|-------------|
| I. Herança | 1989 |
| II. Soja sudoeste | 1998 |
| III. Boom | 2007 |
| IV. Cód. Florestal | 2014 |
| V. Reorganização | 2021 |

## Marcos políticos (linhas verticais)

1994 (Plano Real), 1996 (Lei Kandir), 2003 (Boom commodities), 2012 (Código Florestal), 2018 (Cerrado Manifesto).

## ATOS (fundos sombreados)

I (1985–93), II (94–02), III (03–11), IV (12–17), V (18–24) — mesmos do `utils.js`.

## Como rodar

```bash
python scripts/figuras_taxas.py
```

Requer `geobr` para os mapas municipais.