# Pipeline #24 — Análise espacial estatística (Moran's I, LISA, spreg)

**Script**: `scripts/analise_espacial.py`
**Status**: ✅ executado (2026-05-14)
**Depende de**: #17 (`taxas_lulc_municipal.csv`), #22 (`painel_residuos.csv`), #16 (`painel_unificado.parquet`), `geobr` (geometrias)

## O que faz

Três análises em sequência para diagnosticar e modelar a estrutura espacial:

1. **Moran's I global** dos resíduos do painel #22 por (modelo, ano, matriz W) — detecta se o painel 2FE deixou autocorrelação espacial não modelada.
2. **LISA / Moran local** para identificar clusters HH (alto-alto), LL (baixo-baixo), HL e LH em anos com I global significativo.
3. **Regressão espacial** (`spreg`) cross-section em 2020 sobre as covariáveis brutas (não resíduos): OLS vs SAR (Spatial Lag) vs SEM (Spatial Error) — compara AIC para escolher a especificação.

## Matrizes de pesos

- **Queen (rainha)**: contiguidade por fronteira ou vértice. Primária. 246 munis, média 5,4 vizinhos por município.
- **KNN-8**: 8 vizinhos mais próximos por centróide. Sensibilidade. Média de 8 vizinhos (por construção).
- Ambas padronizadas por linha (`w.transform = 'r'`).

## Resultados — Moran's I global

**115 de 140** pares (modelo × ano × W) têm I significativo (p<0,05 via 999 permutações). Autocorrelação espacial é uma característica forte e persistente dos resíduos do Pipeline #22.

Top 5 (W = Queen):

| Modelo | Ano | I | z | p |
|---|---|---|---|---|
| pastagem ~ Δ pec_bovinos | 2018 | +0,53 | +13,4 | 0,001 |
| pastagem ~ Δ VA agro | 2018 | +0,53 | +13,5 | 0,001 |
| pastagem ~ Δ SICOR | 2018 | +0,50 | +12,8 | 0,001 |
| agricultura ~ Δ SICOR | 2018 | +0,44 | +11,5 | 0,001 |
| pastagem ~ Δ pec_bovinos | 2013 | +0,44 | +10,9 | 0,001 |

**Pico em 2018** sugere que a fase pós-Cerrado Manifesto + consolidação frigorífica gerou padrão espacial mais clusterizado nos resíduos — modelo univariado 2FE é mais incompleto nessa fase.

## Resultados — LISA

8 mapas gerados (3 modelos foco × 3-4 anos representativos: 2013, 2016, 2019). Cores:

- **Vermelho (HH)**: município com resíduo alto rodeado por vizinhos altos. Hot-spot — modelo subestima sistematicamente.
- **Azul escuro (LL)**: resíduo baixo rodeado por baixos. Cold-spot.
- **Laranja (HL) e Azul claro (LH)**: outliers espaciais.
- **Cinza**: não significativo (p ≥ 0,05).

Padrão típico: hot-spots de Δ agricultura concentrados no **Sudoeste e Sul** (Mineiros, Quirinópolis, Itumbiara), cold-spots no **Nordeste** (regiões com pouca conversão para grãos).

## Resultados — spreg cross-section (2020)

| Y | W | Modelo | R² | AIC | ρ/λ |
|---|---|---|---|---|---|
| Δ agricultura | queen | OLS | 0,333 | −2.923,6 | — |
| Δ agricultura | queen | SAR (Lag) | 0,333 | −2.921,8 | +0,030 |
| Δ agricultura | queen | SEM (Error) | 0,333 | **−2.924,3** | +0,080 |
| Δ pastagem | queen | OLS | 0,345 | −2.573,9 | — |
| Δ pastagem | queen | SAR (Lag) | 0,345 | −2.572,0 | +0,010 |
| Δ pastagem | queen | SEM (Error) | 0,345 | **−2.574,3** | +0,064 |

**SEM (Spatial Error)** vence ambos os pares por margem pequena (1-2 pontos de AIC). O parâmetro λ é positivo mas pequeno (+0,06–0,08), sugerindo autocorrelação no termo de erro mais que no nível da variável dependente.

## Interpretação para a dissertação

1. **Autocorrelação espacial é estrutural** nos resíduos do painel #22 (115/140 anos × modelos significativos). Não é resíduo aleatório.
2. **Mas em cross-section de um único ano (2020)**, a estrutura espacial é fraca (AIC de SEM vs OLS quase igual). Isso indica que **a autocorrelação varia ao longo do tempo** — alguns anos têm forte clustering, outros não.
3. **Recomendação para texto**: reportar como **limitação reconhecida** do Pipeline #22, com Pipeline #24 mostrando a magnitude. Uma extensão futura seria painel espacial (`spreg.Panel_FE_Lag`) — fica para sprint posterior.

## Saídas

| Arquivo | Conteúdo |
|---|---|
| `outputs/espacial/moran_global.csv` | I, E[I], z, p por (modelo, ano, W). 140 linhas. |
| `outputs/espacial/lisa_*.png` | 8 mapas LISA (3 modelos × 3 anos representativos) |
| `outputs/espacial/modelos_espaciais.csv` | OLS vs SAR vs SEM para 2 pares × 2 matrizes W. 12 modelos. |

## Como rodar

```bash
pip install libpysal esda splot spreg  # ver requirements.txt
python scripts/analise_espacial.py
```

Tempo: ~2 min (geobr download + Moran com 999 permutações × 140 pares).

## Limitações

- **Cross-section em 2020 apenas** para spreg: análise espacial em painel completo (todas as 9 janelas) seria mais robusta — fica para extensão.
- **Matriz Queen pode ser muito restritiva** para municípios goianos com vizinhos administrativos pequenos. KNN-8 confirma magnitudes similares — robustez ok.
- **Testes múltiplos não corrigidos** nos p-valores LISA — usar como exploratório, não como teste formal por município.
- **Modelos LISA em resíduos** assumem que os resíduos do painel 2FE são exógenos; se o modelo original tem omissão de variável correlacionada espacialmente, LISA captura combinação de efeito espacial + omissão.
