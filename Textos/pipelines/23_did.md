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
| 2018 | PAC Cerrado | 2013–2023 |

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
| Pastagem | 2018 | Combined | −0,26 | 0,001 | Após PAC Cerrado, pastagem retraiu em GO vs controles |
| Pastagem | 2018 | MT | −0,44 | <0,001 | Efeito forte vs MT |
| Agricultura | 1995 | TO | −0,07 | 0,046 | Agricultura desacelerou em GO vs TO |
| Agricultura | 2012 | MT | −0,19 | 0,005 | Agricultura expandiu menos em GO vs MT após Código Florestal |
| Agricultura | 2018 | MT | +0,17 | 0,011 | Agricultura expandiu mais em GO vs MT após PAC Cerrado |

**Nota**: O efeito vs MT deve ser interpretado com cautela — MT tem composição LULC muito diferente (Floresta Amazônica, soja em larga escala). TO é controle mais plausível. DiD com TO isolado tem resultados mais modestos.

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `data/cache/did/mt_uf_lulc.csv` | Série anual UF MT (40 anos × 6 classes, Mha) |
| `data/cache/did/to_uf_lulc.csv` | Série anual UF TO (40 anos × 6 classes, Mha) |
| `outputs/correlacoes/did_resultados.csv` | 36 modelos: β_did, SE, p, n_obs |
| `outputs/correlacoes/did_*.png` | 12 gráficos (3 classes × 4 marcos) |

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