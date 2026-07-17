# Escopo da dissertação

**Tema**: Dinâmica de uso e cobertura da terra em Goiás (1985–2024) e sua relação com fatores socioeconômicos.

**Unidade de análise**: 246 municípios de Goiás. **Período**: 1974–2024 (dependendo da fonte).

**Programa**: Mestrado Profissional em Ciências Ambientais — CIAMB/UFG.

> **Nota (jul/2026).** Este documento registra o **escopo e as hipóteses iniciais**. A investigação evoluiu: as hipóteses de "deslocamento" (iLUC intra-estadual) foram **testadas e refinadas/refutadas** (#34/#42), e a análise longitudinal passou a usar **166 Áreas Mínimas Comparáveis** (D11) ao lado dos 246 municípios. A **tese que de fato emergiu** — a "marcha ao norte" (reorganização espacial Sul→Norte sob drive comum + gradiente de aptidão + teto de oferta) — está em [narrativa_pipelines.md](../narrativa_pipelines.md) e [guia_de_leitura.md](../guia_de_leitura.md).

## Eixos de investigação

### 1. Dinâmica de Conversão (Uso e Cobertura)
Mapeamento temporal da expansão da pastagem, sua consolidação e posterior substituição por agricultura (soja, cana) ou regeneração de vegetação nativa.

### 2. Transição e Vetores
Quantificação da pastagem como estágio intermediário de ocupação do solo — matrizes de transição pixel-a-pixel (desmatamento → pastagem → lavoura). Correlação com crédito rural, infraestrutura agroindustrial e PIB agropecuário.

### 3. Variáveis Econômicas e de Infraestrutura
Correlação das mudanças espaciais com:
- PIB agropecuário municipal (SIDRA 5938)
- Crédito rural municipalizado (SICOR/BACEN)
- Produção pecuária (lotação animal, leite, carne)
- Infraestrutura agroindustrial (frigoríficos, silos, malha viária)

## Hipóteses centrais

> *Hipóteses **de partida**. Resultado após a Fase 6: a cadeia pasto→lavoura confirma-se no Sul (intensificação), mas o **deslocamento causal de uma região sobre a outra foi refutado** (#34/#42) — ver narrativa/guia.*

- A pastagem funciona como estágio intermediário: floresta/cerrado → pastagem → lavoura.
- Crédito rural e infraestrutura agroindustrial aceleram a conversão pastagem→soja.
- Municípios com maior lotação bovina e maior acesso a crédito convertem pastagem mais rápido.

## Recorte temporal

- **MapBiomas**: 1985–2024 (série anual, 40 anos).
- **SIDRA**: 1974–2024 (séries longas PPM/PAM; PIB desde 2002).
- **SICOR**: 2013–2026 (limite da API).
- **Censo Agro**: 2017 (cross-section).

## Stack tecnológico

| Camada | Ferramenta | Papel |
|---|---|---|
| Processamento LULC | Google Earth Engine (Python API) | Tabulação cruzada, matrizes de transição, fogo×LULC |
| Pipelines de dados | Python (pandas, geopandas, requests, sidrapy) | Coleta, limpeza, merge |
| Cartografia | matplotlib + QGIS | Exploração rápida (Python) / layout final (QGIS) |
| Análise espacial | pysal/spreg | Moran's I, LISA, regressão espacial |

Ver também: [estrutura_diretorios.md](estrutura_diretorios.md), [como_retomar_trabalho.md](como_retomar_trabalho.md).