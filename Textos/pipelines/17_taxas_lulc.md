# Pipeline #17 — Métricas anuais de variação LULC (taxas, slopes, aceleração)

**Script**: `scripts/calcular_taxas_lulc.py`
**Depende de**: `data/processed/mapbiomas_munis_goias.csv` (Pipeline #4), `data/processed/mapeamento_mesorregioes.csv` (Pipeline #18)
**Outputs**: `data/processed/taxas_lulc_goias.csv`, `taxas_lulc_municipal.csv`, `taxas_lulc_mesorregioes.csv`

## O que faz

Computa métricas derivadas de variação LULC para cada classe agregada (6 grupos) em três níveis geográficos (UF, municipal, mesorregiões):

| Métrica | Fórmula | Unidade | Disponível |
|---------|---------|---------|------------|
| `{g}_mha` | área / 1e6 | Mha | UF, muni, meso |
| `{g}_pct` | área / total × 100 | % | UF, muni, meso |
| `{g}_delta_mha` | area[t] - area[t-1] | Mha/ano | UF, muni, meso |
| `{g}_slope_5a_trail` | OLS t-4..t + HAC | Mha/ano | UF, muni, meso |
| `{g}_slope_se_nw` | erro padrão Newey-West | Mha/ano | UF, muni, meso |
| `{g}_slope_5a_centr` | OLS t-2..t+2 + HAC | Mha/ano | UF |
| `{g}_aceleracao` | slope[t] - slope[t-1] | Mha/ano² | UF |

Onde `{g}` ∈ {vegetacao_natural, pastagem, agricultura, agua, area_urbana, outros}. Mosaico (ID 21) é coluna separada, não entra nos 6 grupos.

## Decisões metodológicas

### D1 — Sistema unificado de classes

Mapeamento idêntico a `gerar_mapas_lulc_gee_40anos.py`:

| Grupo | IDs MapBiomas |
|-------|---------------|
| Vegetação Natural | 3, 4, 12 |
| Pastagem | 15 |
| Agricultura | 9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62 |
| Água | 31, 33 |
| Área Urbana | 24 |
| Outros | 5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75 |

Mosaico (ID 21) excluído. Campo Alagado (ID 11) em "Outros", não em "Vegetação Natural".

### D2 — Fonte de dados

Consome `mapbiomas_munis_goias.csv` (não `painel_unificado.parquet`), agregando pelos IDs para os 6 grupos. Isso garante coerência com os mapas GEE e as matrizes de transição.

### D3 — Janela do slope

- `slope_5a_trail` (t-4..t): para inferência e testes piecewise. NaN em 1985–1988.
- `slope_5a_centr` (t-2..t+2): para visualização narrativa. NaN em 1985–1986 e 2023–2024.

### D4 — Erro padrão Newey-West

Séries LULC violam i.i.d. Erros padrão calculados com `statsmodels.OLS` + `cov_type="HAC"`, `cov_kwds={"maxlags": 2}`. Não usar OLS i.i.d. para inferência.

### D5 — Aceleração

Derivada de série já suavizada → ruidosa por construção. Plotada apenas com pontos onde `|aceleração| > 2σ`.

## NaNs por construção

- 1985: delta = NaN (não há ano anterior)
- 1985–1988: slope_trail, se_nw, aceleracao = NaN (janela insuficiente)
- 1985–1986, 2023–2024: slope_centr = NaN (janela centrada insuficiente)

## Validação

- Soma dos 6 grupos + Mosaico ≈ área total de Goiás (~34 Mha) em todos os anos
- Slope de pastagem cruza zero em ~2004 (consistente com boom de commodities)
- Slope de vegetação natural desacelera de -0.35 (1989) para -0.04 (2012)

## Como rodar

```bash
python scripts/calcular_taxas_lulc.py
```

Gera os 3 CSVs em `data/processed/`. Requer `statsmodels` e `data/processed/mapeamento_mesorregioes.csv` (Pipeline #18).