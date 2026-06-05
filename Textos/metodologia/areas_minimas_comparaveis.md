# Áreas Mínimas Comparáveis (AMC) — decisão metodológica

**Decisão D11** (2026-06-04): toda análise **longitudinal** que cruze dados de
pesquisa (SIDRA/PPM/PAM/PIB/SICOR) com LULC ou que compare territórios ao longo
de 1985–2024 usa **Áreas Mínimas Comparáveis** como unidade espacial. Os 246
municípios atuais ficam reservados para análises **transversais** e do período
recente. Implementação: [Pipeline #25](../pipelines/25_amc_goias.md).

## O problema

Goiás tinha ~199 municípios em 1985 e tem 246 hoje. Há dois regimes de dados que
se comportam de formas opostas no tempo:

| | LULC MapBiomas (raster) | SIDRA/PPM/PAM/PIB/SICOR (pesquisa) |
|---|---|---|
| Como é gerado | Polígono **atual** recortado sobre a imagem de cada ano | Tabulado pelo município **como existia no ano** |
| "Município X em 1985" | Território **de hoje**, em 1985 | Território **de 1985** (do pai, maior) |
| Município criado em 1997 | Série completa desde 1985 | NaN antes de 1997 |

Quando se junta os dois por `cd_mun`, para um município-pai compara-se o LULC do
território **atual** contra a produção/rebanho de um território **historicamente
maior** (que incluía os filhos). Para os filhos, compara-se LULC contra NaN.

### Evidência empírica (no painel #16)

- **62 dos 246 municípios (25%)** só aparecem no SIDRA depois de 1985 — ondas de
  emancipação em **1989 (27), 1993 (21), 1997 (10), 2001 (4)**.
- O **total estadual** de rebanho é contínuo atravessando esses anos (o gado do
  filho estava dentro do pai), mas **municípios-pai individuais despencam 50–80%**
  no ano da emancipação:
  - 1989: Cidade de Goiás −56% (340→150 mil), Formoso −73%, Planaltina −53%
  - 1993: Mambaí −81%, Goianira −64%, Corumbá de Goiás −50%
  - 1997: Pirenópolis −37%, Mara Rosa −39%, Barro Alto −37%

Reportar "Cidade de Goiás perdeu 56% do rebanho em 1989" como dinâmica pecuária
seria atribuir a um fenômeno econômico/ambiental o que é **perda de território**.

### Por que fere especificamente esta dissertação

1. **Contamina os cruzamentos centrais**: `lotacao_bov_ha` e `credito_por_ha_pastagem`
   dividem dado de pesquisa (numerador, território histórico) por LULC (denominador,
   território atual) → viés para cima nos anos iniciais dos municípios-pai.
2. **Bate nas análises longitudinais**: correlações em primeiras diferenças
   ([#21](../pipelines/21_correlacoes_uf.md), [#22](../pipelines/22_correlacoes_painel.md))
   e o DiD ([#23](../pipelines/23_did.md), quebra em 1995, janela 1990–2000)
   atravessam justamente as ondas de 1993 e 1997. As quedas de −50% a −80% são
   outliers que dominam qualquer Δ ou estimador de tendência nessa janela.

## A solução: AMC (Ehrl 2017)

Uma **Área Mínima Comparável** agrupa cada município-pai com seus filhos numa
unidade de **território constante** ao longo de toda a janela. Agregando **ambos
os regimes** (raster + pesquisa) ao nível de AMC, toda série passa a se referir ao
mesmo território em todos os anos.

- **Referência citável**: Ehrl, P. (2017). *Minimum comparable areas for the period
  1872–2010: an aggregation of Brazilian municipalities*. Estudos Econômicos, 47(1),
  215–229. doi:10.1590/0101-416147182phe. (Equivalente conceitual às AMCs do IPEA.)
- **Fonte de dados**: `geobr.read_comparable_areas(start_year=1980, end_year=2010)`
  entrega a concordância pronta (coluna `list_code_muni_2010`).
- **Escolha de janela**: `start_year=1980` antecede todas as emancipações da nossa
  janela (1989+), garantindo que todo desmembramento de 1985–2024 seja colapsado.
  `end_year=2010` basta porque GO não criou municípios após ~2001.
- **Resultado**: 246 municípios → **166 AMCs** (53 grupos pai+filhos, 113 unidades 1:1).

### Por que a soma resolve

Antes da emancipação o filho é NaN e o pai carrega o valor do território inteiro →
soma da AMC = valor do pai = total correto. Depois, ambos têm valores e a soma
continua correta. O agregado é **contínuo**, sem salto espúrio. Validação no #25:
o total estadual é idêntico (Δ=0) e **0 das 166 AMCs** estreiam após 1985 (partição
territorialmente constante).

## Estratégia de dois trilhos

| Unidade | Quando usar | Arquivo |
|---|---|---|
| **AMC** (166) | Longitudinal: 1ª diferença, painel FE, DiD, periodização, tendências, "cresceu/encolheu X%" | `painel_amc_goias.parquet` |
| **Município atual** (246) | Transversal e período recente: Censo 2017, mapas de 2024, foto de um ano | `painel_unificado.parquet` |

## O preço (limitação honesta)

A AMC funde cada pai com seus filhos → ~62 municípios atuais deixam de ser
analisáveis isoladamente nas séries longas. É inevitável quando o dado vem de
pesquisa: a informação histórica do filho não existe separada — estava no pai.
Para mapas e recortes de um único ano recente, usa-se a malha de 246.

## Resultado do re-teste (as conclusões mudam?)

As análises longitudinais municipais foram re-rodadas sobre as AMC (modo
`--nivel amc` em #22 e #24). **As conclusões são robustas**:

- **Painel 2FE (#22)**: todos os achados significativos mantêm sinal e
  significância; os β ficam ~15–30% **mais fortes** e o R² within **maior**
  (médio 0,021 → 0,028) — coerente com a remoção do ruído territorial que
  atenuava as estimativas. Nenhum achado-chave se inverte. As únicas mudanças
  são duas trocas de sinal em coeficientes ≈0 não-significativos (ruído) e um
  coeficiente borderline que cruza para significante. Tabela em
  [pipelines/22_correlacoes_painel.md](../pipelines/22_correlacoes_painel.md).
- **Análise espacial (#24)**: mesma conclusão — autocorrelação espacial positiva
  forte nos resíduos (Moran I médio ≈ +0,20; 125/140 testes significativos vs
  115/140 no municipal) e os modelos espaciais (SEM/SAR) superam o OLS nos dois
  níveis. A dependência espacial não é artefato da malha.
- **O que NÃO precisou re-rodar**: análises de nível UF (#21 correlações UF,
  #23 DiD, #26 quebras, #29 periodização) — o agregado estadual é idêntico sob
  AMC (Δ=0 provado no #25), então seus resultados não mudam.

Conclusão prática: a AMC torna os resultados longitudinais **defensáveis** frente
à crítica de comparabilidade, e o re-teste **confirma** que os achados não eram
artefatos da malha municipal.

## Relação com decisões anteriores

Substitui a nota vaga de [espacializacao.md](espacializacao.md) ("séries anteriores
agregadas via pai-filho de desmembramento se preciso") — que era uma intenção
nunca implementada — por um método publicado, citável e reprodutível.
