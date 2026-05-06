# Validação cruzada (MapBiomas × SIDRA)

Cobertura/uso da terra é medido por dois sistemas independentes:
- **MapBiomas**: pixels classificados via sensoriamento remoto (Landsat, 30m).
- **SIDRA/PAM**: área plantada declarada pelo produtor ao IBGE.

Comparar os dois é essencial para defender a qualidade dos dados na qualificação.

## Soja — validação implementada

Sistemática para a classe Soja, comparando áreas do MapBiomas com áreas plantadas declaradas no SIDRA (PAM, tabela 1612, variável 109).

**Arquivo:** `data/processed/validacao_soja_mapbiomas_sidra.csv`
**Pipeline:** [#5](../pipelines/05_pastagem_soja.md)

### Resultados típicos

- **Correlação Pearson** entre as fontes: ~0,85–0,95 para anos ≥ 2000.
- **Razão mediana** (MapBiomas / SIDRA): próxima de 1,0, com pequena tendência de MapBiomas subestimar levemente em alguns períodos.
- No **Pipeline #16** (4.316 pares 2000–2023): Pearson r = 0,971; razão mediana 1,124.

### Causas conhecidas das diferenças

1. **Segunda safra**: MapBiomas captura a cobertura no momento; pode ler como "soja" área que SIDRA registra como "milho 2ª safra" (ver [Pipeline #15](../pipelines/15_safrinha.md)).
2. **Borda de pixel**: classificação raster tem incerteza nos limites de talhão.
3. **Auto-declaração**: SIDRA depende do produtor; sub-declaração possível em pequenos.

### Implicação

A série de soja do MapBiomas é considerada **consistente com a fonte oficial do IBGE** para análises agregadas. Diferenças ≤ 12% por município são esperadas e têm causa metodológica explicável — não são erro.

## Cana — validação pontual (Pipeline #4)

- 2022: SIDRA 933k ha vs MapBiomas 1.004k ha (razão 1,08).
- Top munis batem (Quirinópolis, Mineiros, Goiatuba, Itumbiara, Acreúna).

## Pastagem — validação batimental (Pipeline #4 e #5)

- **Soma municipal vs UF antiga**: erro máximo de 0,0000% ao longo dos 40 anos. Math é math — confirma que o pivot longo→agregado é idempotente.

## O que ainda falta

Validação cruzada para:
- **Milho** (1612 var 109/216 vs MapBiomas classe 39 ou agrupada): repetir a metodologia da soja para milho.
- **Cana** sistemática (não só 2022).
- **Pastagem vs PPM**: confronto entre área de pastagem MapBiomas e estimativa derivada de rebanho/lotação típica.

Está no [backlog](../backlog.md) como reforço para a qualificação.
