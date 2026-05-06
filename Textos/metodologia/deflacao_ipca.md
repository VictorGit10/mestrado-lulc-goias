# Metodologia de deflação (IPCA)

Todos os valores monetários do projeto (PIB, VA agro, crédito rural SICOR) são deflacionados para **reais de dezembro/2024** usando o IPCA acumulado.

## Procedimento

1. Coleta do IPCA mensal (variável 63, tabela 1737 do SIDRA).
2. Construção do número-índice cumulativo: `indice_t = produto(1 + var_mensal_i / 100)` para `i = 1..t`.
3. Para cada ano X, usa-se o índice acumulado em **dezembro de X** como representativo.
4. Fator de deflação = `indice_dez_2024 / indice_dez_X`.

```python
# Esboço do cálculo
ipca = pd.read_csv("data/processed/sidra_1737_ipca.csv")
ipca["indice"] = (1 + ipca["valor"] / 100).cumprod()
indice_dez = ipca[ipca["mes"] == 12].set_index("ano")["indice"]
fator = indice_dez.loc[2024] / indice_dez
# Multiplicar valor nominal pelo fator do ano correspondente
valor_real = valor_nominal * fator.loc[ano]
```

## Por que IPCA dezembro

- **IPCA** (não IGP-DI nem deflator implícito do PIB): índice de preços ao consumidor amplo, série mais longa e estável do IBGE.
- **Dezembro de cada ano**: simplifica o cálculo (1 valor por ano em vez de média móvel) e é convenção comum em séries anuais.
- **Base dez/2024**: ponto mais recente da série quando a deflação foi implementada. Todos os valores devem ser interpretados como "reais de dezembro de 2024".

## Onde é aplicado

- [Pipeline #1](../pipelines/01_pastagem_pib.md) — PIB de Goiás
- [Pipeline #2](../pipelines/02_analise_expandida.md) — VA agropecuário e PIB total
- [Pipeline #8](../pipelines/08_credito_lulc.md) — todo o crédito SICOR
- [Pipeline #16](../pipelines/16_painel_unificado.md) — `pib_real_rs`, `va_agro_real_rs`, `sicor_*` em reais (não mil R$)

## Limitações

- IPCA é índice nacional. Variações regionais não são capturadas.
- Para análises focadas em insumos agrícolas, IGP-M poderia ser mais adequado (mas a série é mais ruidosa).
- Conversão histórica de **moedas anteriores ao Real** (Cruzeiro, Cruzado, Cruzado Novo, Cruzeiro Real) é não-trivial. Por isso a variável 215 da PAM (valor da produção, mil R$ correntes) e leite PPM 74 são **excluídos** dos pipelines.
