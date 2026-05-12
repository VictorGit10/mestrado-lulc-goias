# Pipeline #16 — Painel unificado (município × ano)

**Script**: `scripts/construir_painel_unificado.py`
**Depende de**: Pipelines #3, #4, #6, #7, #13, #15.
**Outputs**: `data/processed/painel_unificado.parquet` (primário) + `painel_unificado.csv` (cortesia) + `outputs/diagnosticos/painel_unificado_cobertura.csv` (diagnóstico de NaN).

## O que é

Tabela wide única `cd_mun × ano` (9.840 linhas × ~157 colunas) que consolida todas as fontes prontas em formato pronto para regressão pooled, painel ou inferência espacial (Moran, LISA, `spreg`).

**Universo**: 246 municípios de Goiás (atual), 40 anos (1985–2024). Linha = município × ano.

## Saída

- `data/processed/painel_unificado.parquet` (formato primário)
- `data/processed/painel_unificado.csv` (cortesia, utf-8)
- `outputs/diagnosticos/painel_unificado_cobertura.csv` (% NaN por coluna × ano)

## Como rodar

```bash
python scripts/construir_painel_unificado.py
```

## Blocos de variáveis

(prefixo identifica fonte):

| Prefixo | Origem | Cobertura plena |
|---|---|---|
| `lulc_*` (15 cols) | MapBiomas Col 10.1 (Pipeline #4) | 1985–2024 |
| `pec_*` (4 cols: bovinos, suínos, galináceos, ovinos tosquiados) | SIDRA PPM 3939 + 95 (Pipeline #3) | 1974–2024 |
| `agri_*` (~66 cols: todas as temporárias × área+ton + milho 1ª/2ª safras) | SIDRA PAM 1612 + 839 (Pipeline #3 + #15) | 1974+ (safrinha desde 2003) |
| `perm_*` (~76 cols: todas as permanentes × área destinada+ton) | SIDRA PAM 1613 (Pipeline #3) | 1974–2024 |
| `pec_mel_kg`, `pec_la_kg` | SIDRA PPM 74 (Pipeline #3) | 1974–2024 (cobertura municipal variável) |
| `pib_real_rs`, `va_agro_real_rs`, `participacao_agro_pct` | SIDRA 5938 (Pipeline #3) | 2002–2023 (PIB total até 2023; VA agro só 2002–2021) |
| `populacao` | SIDRA 6579 (Pipeline #3) | 2001–2024 (gaps em 2007 e 2010 — anos de Censo, IBGE não publica estimativa) |
| `sicor_*` (6 cols: custeio/investimento/total × valor+n_op) | SICOR (Pipeline #6), deflacionado | 2013–2024 |
| `censo2017_*` (9 cols) | Censo Agro 2017 (Pipeline #7), replicado em todos os anos | Constante (cross-section) |
| `idhm*` (4 cols: idhm, idhm_renda, idhm_educ, idhm_long) | IPEA Data API (Pipeline #13) | 1991, 2000, 2010 (Censo); pós-2010 inexistente em nível municipal |
| `fogo_*` (2 cols) | **PLACEHOLDER** (NaN) | Aguarda Pipeline #14 |
| Métricas derivadas: `lotacao_bov_ha`, `credito_por_ha_pastagem`, `produtividade_soja_ton_ha`, `pct_pastagem_lulc`, `pct_agricultura_lulc`, `pct_natural_lulc`, `pib_per_capita_real`, `densidade_demografica_hab_km2` | Calculadas onde insumos existem | Variável |

## Decisões metodológicas (críticas — leia antes de usar)

1. **Janela temporal completa 1985–2024**, sem filtro temporal embutido. NaN onde a fonte não cobre. Filtragem fica nas análises a jusante. Janela de cobertura plena (todas as fontes coexistem): **2013–2021** (após 2021 cai VA agro; em 2024 cai PIB e bovinos parciais).

2. **Deflação**: PIB, VA agro e SICOR convertidos para R$ de **dezembro/2024** via IPCA dez-a-dez (tabela SIDRA 1737). Padrão idêntico ao Pipeline #8. Ver [metodologia/deflacao_ipca.md](../metodologia/deflacao_ipca.md).

3. **Unidade R$**: SIDRA 5938 reporta em "Mil R$"; este pipeline **multiplica por 1000** para sair em R$ — coerência com SICOR (R$).
   - **Divergência conhecida** com `painel_credito_lulc.csv` (Pipeline #8): aquele arquivo reporta `pib_real_rs` ~38% maior; causa não auditada. O cálculo aqui é determinístico e bate com SIDRA bruto.

4. **Censo 2017 replicado** como atributo estático em todos os anos do município. Decisão pragmática para regressão pooled. Limitação: não captura mudanças estruturais pré- ou pós-2017.

5. **Leite incluído** via PPM 74, variável 106 + classificação 80/categoria 2682 (Leite), unidade "Mil litros". Correção aplicada em 2026-05-11 — a coleta original não passava a classificação 80 e devolvia apenas valor monetário; após corrigir a chamada SIDRA, a quantidade física passou a vir corretamente.

6. **Todas as lavouras temporárias e permanentes** (Pipeline #3 expandido em 2026-05-11): 33 temporárias (PAM 1612) e 38 permanentes (PAM 1613) entram no painel. Culturas com pouca expressão em Goiás terão alta proporção de NaN — isso é esperado e não indica erro. Frutas (laranja, banana, manga etc.) e café mudaram de unidade em 2002 (de "mil frutos" para toneladas), gerando quebra de série histórica que deve ser tratada em análises comparativas longitudinais.

7. **4 categorias de pecuária**: bovinos, suínos, galináceos (PPM 3939) + ovinos tosquiados (PPM 95). Equino, bubalino, ovino, caprino permanecem disponíveis no CSV bruto `sidra_ppm3939_rebanhos.csv` mas não entram no painel unificado. Mel e lã (PPM 74) também disponíveis como colunas isoladas (`pec_mel_kg`, `pec_la_kg`).

8. **SICOR 2025–2026 EXCLUÍDOS** (parciais). Quem precisar usar `sicor_painel_municipal.csv`.

9. **Histórico Goiás × Tocantins**: pré-1989, agregados estaduais externos (ex.: `rebanho_bovino_goias.csv`) frequentemente incluem TO (criado em 1988). O painel cobre só os 246 munis de GO atual — divergência ~19% no batimento pré-1989 é **conceitualmente correta**. Pós-1989 o batimento é exato.

10. **LULC agrupada por tema**: `lulc_agricultura_ha` soma TODAS as lavouras MapBiomas (soja + cana + algodão + arroz + café + citrus + outras temporárias + outras perenes). `lulc_soja_ha` permanece desagregada por ser cultura central da dissertação. `lulc_area_total_ha` = soma de todas as classes (proxy da área do município).

11. **IDH-M parcialmente preenchido, Fogo pendente**: colunas `idhm*` preenchidas para 1991/2000/2010 via IPEA Data API (Pipeline #13, 738 de 9.840 linhas). IDHM municipal pós-2010 não existe (PNAD Contínua só desagrega para estado/RM/RIDE; próxima atualização municipal depende do processamento do Censo 2022 por IPEA/PNUD/FJP). Colunas `fogo_*` ainda NaN — aguardam Pipeline #14.

12. **Métricas derivadas com NaN propagado**: nenhuma extrapolação. Razões com denominador zero → NaN (substituídas via `np.replace([np.inf, -np.inf], np.nan)`).

## Validação realizada

- Shape: 9.840 = 246 × 40, sem duplicatas em (cd_mun, ano).
- Bovinos vs `rebanho_bovino_goias.csv`: dif 0% pós-1989; dif ~19% pré-1989 (Tocantins).
- SICOR/pastagem/soja vs `painel_credito_lulc.csv` (2013–2023): dif mediana 0 (batimento perfeito).
- Soja MapBiomas vs PAM (2000–2023, 4.316 pares): Pearson r = 0,971; razão mediana 1,124 (consistente com `validacao_soja_mapbiomas_sidra.csv`).
- Smoke test regressão (2013–2021, drop NaN nas chaves): 2.185 linhas × 243 munis utilizáveis.
- Validação automatizada em 4 camadas: `scripts/validar_painel_unificado.py` + `notebooks/validacao_painel.ipynb`. Resultado atual: 1.699 OK / 36 ESPERADA_TOCANTINS / 25 CRUZADA_INFORMATIVA / 17 SEM_GABARITO / **0 ANOMALA**. Detalhes em [metodologia/validacao_painel.md](../metodologia/validacao_painel.md).

## O que ESTE pipeline NÃO faz (escopo deliberado)

- Não roda Moran/LISA/regressão — apenas prepara o painel. Análise espacial será script dedicado.
- Não recalcula validações cruzadas — só gera diagnóstico de NaN.
- Não anexa geometria. Para análise espacial via `pysal`, fazer merge com `geobr.read_municipality(code_muni="GO", year=2020)` por `cd_mun` e construir matriz W (queen contiguity é o default).
- Não faz interpolação temporal de séries com gaps (ex.: população em 2007/2010).
- Não inclui IDH-M pós-2010 (inexistente em nível municipal) nem Fogo (slot vazio; pendente Pipeline #14).
