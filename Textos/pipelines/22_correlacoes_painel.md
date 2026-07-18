# Pipeline #22 — Correlações painel municipal (2-way FE)

**Script**: `scripts/correlacoes_painel.py`
**Status**: ✅ executado
**Depende de**: #17 (`taxas_lulc_municipal.csv`), #16 (`painel_unificado.parquet`)

## O que faz

Regressão em painel com efeitos fixos de entidade (município) e tempo (ano) para associar mudanças LULC a mudanças socioeconômicas no nível municipal.

**Decisão D8**: `PanelOLS` com `entity_effects + time_effects`, SE clusterizado por município.

**Especificação**: Δlulc_it = α_i + γ_t + β·Δx_it + ε_it

## Janelas

| Janela | Obs típico | Variáveis disponíveis |
|--------|-----------|----------------------|
| 2013–2021 (plena) | ~1.956–2.214 | LULC + pecuária + PIB + SICOR |
| 2002–2023 (estendida) | ~2.444–5.412 | LULC + pecuária + PIB (sem SICOR) |

## Pares testados

| Y (Δ LULC) | X (Δ socioeconômico) | Rótulo |
|------------|---------------------|--------|
| Δ Pastagem | Δ SICOR crédito rural | Crédito rural × pastagem |
| Δ Pastagem | Δ Bovinos | Rebanho × pastagem |
| Δ Pastagem | Δ VA agropecuária | VA agro × pastagem |
| Δ Veg. natural | Δ Fogo veg. nativa | Fogo × vegetação natural |
| Δ Veg. natural | Δ PIB real | PIB × vegetação natural |
| Δ Agricultura | Δ Produção soja | Soja × agricultura |
| Δ Agricultura | Δ SICOR crédito rural | Crédito rural × agricultura |
| Δ Agricultura | Δ VA agropecuária | VA agro × agricultura |

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `outputs/correlacoes/painel_2fe.csv` | Tabela com 16 modelos: β, SE, p, R² within, n_obs |
| `outputs/correlacoes/painel_residuos.csv` | Resíduos para futura análise espacial (Moran's I) |

## Resultados principais

6 de 16 modelos significativos a 5%:

| Y | X | Janela | β | p | R² within | Interpretação |
|---|---|--------|---|---|-----------|---------------|
| Δ Pastagem | Δ SICOR | 2013–2021 | −0,0034 | 0,0000 | 0,049 | Crédito rural associado a retração de pastagem (possível transição para agricultura) |
| Δ Pastagem | Δ SICOR | 2002–2023 | −0,0029 | 0,0000 | 0,030 | Robusto na janela estendida |
| Δ Pastagem | Δ Bovinos | 2002–2023 | ≈0 | 0,0042 | 0,021 | Significativo mas efeito praticamente nulo |
| Δ Pastagem | Δ VA agro | 2013–2021 | −0,0015 | 0,0334 | 0,022 | Crescimento do VA agro → retração de pastagem |
| Δ Agricultura | Δ VA agro | 2013–2021 | −0,0035 | 0,0000 | 0,105 | VA cresce sem expansão de área → intensificação |
| Δ Agricultura | Δ VA agro | 2002–2023 | −0,0040 | 0,0000 | 0,047 | Robusto na janela estendida |

**Conclusão**: o sinal negativo Δ Agricultura × Δ VA agro é o achado mais robusto — sugere que o crescimento do valor adicionado agropecuário em Goiás se dá por intensificação (produtividade), não por expansão de área. Os R² within baixos (0–10%) são esperados para modelos bivariados com alta heterogeneidade municipal.

## Robustez — especificação multivariada (2026-05-14)

Para responder à crítica de R² within baixo no univariado, rodamos três modelos multivariados com covariáveis simultâneas (mesma especificação 2FE, cluster por município):

| Y (ΔLULC) | Covariáveis simultâneas | R²w uni (máx) | R²w mv | N |
|---|---|---|---|---|
| Δ Pastagem | Δ SICOR, Δ Bovinos, Δ VA agro, Δ Fogo | 0,049 | 0,072 | 1.956 |
| Δ Veg. natural | Δ Fogo veg.nat., Δ SICOR, Δ VA agro | 0,002 | 0,005 | 1.956 |
| Δ Agricultura | Δ Soja ton, Δ SICOR, Δ VA agro, Δ Bovinos | 0,105 | 0,122 | 1.550 |

Variante sem SICOR (janela estendida 2002–2023, mais N):

| Y | Covariáveis sem SICOR | R²w mv | N |
|---|---|---|---|
| Δ Pastagem | Δ Bovinos, Δ VA agro, Δ Fogo | 0,014 | 4.674 |
| Δ Agricultura | Δ Soja, Δ VA agro, Δ Bovinos | 0,061 | 3.339 |

### β multivariados significativos (p<0,05)

- **Δ Pastagem ~ Δ SICOR**: β=−0,0030, p<0,001 (com VA agro+Bovinos+Fogo no modelo) — **SICOR é o canal dominante de retração de pastagem**; VA agro perde significância (p=0,15) quando se controla por SICOR.
- **Δ Agricultura ~ Δ VA agro**: β=−0,0035, p<0,001 (com SICOR, com Soja, com Bovinos); β=−0,0029, p=0,012 sem SICOR (N=3.339) — **achado de intensificação sobrevive a todos os controles**.

### VIFs

Todos ≤ 1,55. Sem multicolinearidade preocupante.

### Implicação

- O R² within do multivariado é 1,5× a 2,4× o do univariado em pastagem e agricultura. Substancial, mas ainda modesto — confirma que **dinâmica intra-municipal** captura a maior parte da variação de Δlulc, com socioeconômicos explicando ~10–15% adicional.
- A **decomposição do canal** muda interpretação: para pastagem, SICOR (não VA agro) é o **canal associado mais forte** — o preditor mais robusto da retração; VA agro perde significância quando se controla por SICOR. Para agricultura, VA agro mantém a posição central — **a intensificação é o resultado consistente da dissertação**. *(Leitura **associativa**, não causal: um painel 2FE com cluster identifica associação condicional, não efeito causal — o crédito pode **responder** ao plano de conversão tanto quanto antecedê-lo. "Canal mais forte" = preditor mais robusto, não "vetor causal".)*

## Robustez — Áreas Mínimas Comparáveis (D11, 2026-06-04)

25% dos 246 municípios surgiram após 1985 (emancipações 1989/1993/1997/2001), o
que injeta saltos territoriais espúrios na variação intra-município — exatamente
a variação que o 2FE usa. Re-rodamos o painel inteiro sobre as **166 AMC**
(Pipeline #25, território constante): `--nivel amc`.

**As conclusões são robustas.** Todos os achados significativos mantêm sinal e
significância; os β ficam sistematicamente um pouco **mais fortes** e o R² within
**maior** — coerente com a remoção do ruído territorial que atenuava as
estimativas municipais.

| Y ~ X | Janela | β municipal | β AMC | R²w mun → AMC |
|---|---|---|---|---|
| Δ Pastagem ~ Δ SICOR | 2013–2021 | −0,0034* | −0,0045* | 0,049 → 0,070 |
| Δ Pastagem ~ Δ SICOR | 2002–2023 | −0,0029* | −0,0040* | 0,030 → 0,045 |
| Δ Pastagem ~ Δ VA agro | 2013–2021 | −0,0015* | −0,0018* | 0,022 → 0,031 |
| Δ Agricultura ~ Δ VA agro | 2013–2021 | −0,0035* | −0,0040* | 0,105 → 0,137 |
| Δ Agricultura ~ Δ VA agro | 2002–2023 | −0,0040* | −0,0047* | 0,047 → 0,068 |

\* p < 0,05. R²w médio dos 16 modelos: 0,021 (municipal) → 0,028 (AMC).

- **Trocas de sinal: 2** — ambas em `Δ Agricultura ~ Δ SICOR`, β≈0 e **não-significativo** nos dois níveis (ruído, sem achado).
- **Trocas de significância: 1** — `Δ Agricultura ~ Δ Soja [2013–2021]` passa de p=0,112 (n.s.) para p=0,044 (sig.), na direção esperada com dados mais limpos.

**Implicação para a redação**: a AMC é a unidade defensável para os resultados
longitudinais (responde à crítica de comparabilidade), e o re-teste **confirma**
que os achados-chave — crédito→retração de pastagem e VA agro→intensificação da
agricultura — não eram artefatos da malha municipal.

Saídas AMC: `painel_2fe_amc.csv`, `painel_residuos_amc.csv`,
`painel_multivariada_amc.csv`, e a comparação lado a lado em
`outputs/correlacoes/comparacao_municipal_vs_amc.csv`.

## Como rodar

```bash
pip install linearmodels
python scripts/correlacoes_painel.py                # municipal (246) — default
python scripts/correlacoes_painel.py --nivel amc    # AMC (166) — longitudinal (D11)
```

Requer `linearmodels`. O modo `amc` depende de `painel_amc_goias.parquet` (#25) e
`taxas_lulc_amc.csv` (#17).