# Glossário de métricas

Definições, fórmulas e interpretação das métricas calculadas em pipelines de análise.

| Métrica | Fórmula | Interpretação |
|---|---|---|
| **Delta pastagem** | `pastagem_2024 - pastagem_1985` | Variação absoluta de área de pastagem em hectares. Negativo = redução. |
| **Delta soja** | `soja_2024 - soja_1985` | Variação absoluta de área de soja em hectares. Positivo = expansão. |
| **Taxa de conversão** | `delta_soja / abs(delta_pastagem)` (apenas quando `delta_pastagem < 0`) | Proporção da redução de pastagem que foi "explicada" pela expansão de soja. Taxa = 1,0 significa substituição perfeita. Taxa > 1,0 significa que a soja expandiu além da pastagem perdida (sobre outras coberturas). **Cuidado**: é interpretativa, não causal — numerador e denominador não são pareados pixel-a-pixel. |
| **Intensidade de soja** | `delta_soja / pastagem_1985` | Quanto a soja cresceu em relação à base inicial de pastagem. Intensidade = 1,0 significa que a soja "ocupou" 100% da pastagem inicial. |
| **Participação soja 2024** | `soja_2024 / (soja_2024 + pastagem_2024)` | Fração do conjunto pastagem+soja ocupada pela soja no ano mais recente. |
| **Lotação implícita (cab/ha)** | `pec_bovinos_cab / lulc_pastagem_ha` | Cabeças de gado por hectare de pastagem. Indicador bruto de intensificação. |
| **UA bovino** | `pec_bovinos_cab × 0,7` | Conversão de efetivo total para Unidade Animal usando fator único 0,7. Justificativa: SIDRA (PPM 3939, PPM 73, Censo Agro 2017) não publica desagregação etária a nível municipal. O fator 0,7 é a média ponderada convencional Embrapa/CONAB para rebanho de corte misto brasileiro (~50% adultos×1,0 + ~30% novilhos×0,7 + ~20% bezerros×0,5 ≈ 0,71). **Limitação**: estado-estacionário; não captura variação inter-anual da composição etária. |
| **Lotação UA (UA/ha)** | `pec_bovinos_ua / lulc_pastagem_ha` | Lotação em Unidade Animal por hectare de pastagem. Métrica padronizada para comparação com literatura zootécnica. |
| **Produção de leite (mil litros)** | `agri_leite_mil_litros` | Quantidade física produzida via PPM 74, variável 106 + classificação 80/categoria 2682 (Leite). Disponível 1974–2024. |
| **Crédito por hectare de pastagem** | `valor_total_real / pastagem_ha` | Quanto de crédito rural (R$) foi desembolsado por hectare de pastagem existente no município. Indicador de intensificação financeira da pecuária ou de pressão de transição. |
| **Produtividade soja (ton/ha)** | `agri_soja_ton / agri_soja_ha_plantada` | Rendimento médio da soja por hectare plantado (Pipeline #16). Permite comparar intensificação técnica entre municípios. |
| **PIB per capita real** | `pib_real_rs / populacao` | PIB municipal deflacionado por habitante (Pipeline #16). Em R$ de dez/2024. |
| **Densidade demográfica** | `populacao / (lulc_area_total_ha / 100)` | Hab/km² calculado contra a área total LULC do município (Pipeline #16). |
| **% pastagem (LULC)** | `lulc_pastagem_ha / lulc_area_total_ha * 100` | Fração do município coberta por pastagem (MapBiomas). |
| **% agricultura (LULC)** | `lulc_agricultura_ha / lulc_area_total_ha * 100` | Fração coberta por todas as lavouras MapBiomas somadas. |
| **% natural (LULC)** | `(lulc_floresta_nativa_ha + lulc_formacao_savanica_ha + lulc_campo_nativo_ha) / lulc_area_total_ha * 100` | Fração com vegetação nativa remanescente. |

## Convenções

- Valores monetários sempre em **R$ de dezembro/2024** (ver [deflacao_ipca.md](deflacao_ipca.md)).
- Áreas em **hectares** quando indicado `_ha`; em **mil hectares** ou **milhões de hectares** (Mha) em gráficos para legibilidade.
- Razões com denominador zero → NaN (não infinito; substituídas via `np.replace([np.inf, -np.inf], np.nan)`).
