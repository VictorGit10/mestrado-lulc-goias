# Pipeline #25 — Áreas Mínimas Comparáveis (AMC) de Goiás

**Script**: `scripts/construir_amc_goias.py`
**Quando foi feito**: 2026-06-04.
**Depende de**: Pipeline #16 (`painel_unificado.parquet`) e `geobr.read_comparable_areas`.
**Outputs**:
- `data/processed/amc_crosswalk_goias.csv` — crosswalk `cd_mun → code_amc`.
- `data/processed/painel_amc_goias.parquet` (+ `.csv`) — painel **166 AMCs × 40 anos**.
- `data/processed/amc_goias.gpkg` — geometria dissolvida das AMC (para mapas).
- `outputs/diagnosticos/amc_impacto_goias.csv` — relatório antes×depois.

## Por que existe

O painel municipal (#16) cruza dois regimes de dados incompatíveis no tempo:

- **LULC MapBiomas (raster)**: recorta o polígono **atual** do município sobre a imagem de cada ano → os 246 municípios têm série completa 1985–2024.
- **SIDRA/PPM/PAM/PIB/SICOR (pesquisa)**: tabulado pelo município **como existia no ano** → municípios criados depois de 1985 não têm dado antes de existir.

**Medição empírica**: 62 dos 246 municípios (25%) só aparecem no SIDRA depois de 1985 — ondas de 1989 (27), 1993 (21), 1997 (10) e 2001 (4). Isso produz, nos **municípios-pai**, quedas espúrias de 50–80% no rebanho/produção no ano da emancipação de um filho. Não é fenômeno econômico/ambiental — é perda de território. Contamina razões LULC×pesquisa (lotação, crédito/ha) e análises em primeiras diferenças/DiD que cruzam 1989/1993/1997.

A fundamentação completa está em [metodologia/areas_minimas_comparaveis.md](../metodologia/areas_minimas_comparaveis.md).

## O que faz

1. **Crosswalk** (Ehrl 2017 via `geobr.read_comparable_areas(1980, 2010)`): explode `list_code_muni_2010`, filtra Goiás (prefixo IBGE 52) e mapeia cada `cd_mun` → `code_amc`. Cacheado em CSV; `--force` rebaixa do geobr.
2. **Agrega** o painel #16 por `(code_amc, ano)`:
   - **Extensivas** (158 colunas: hectares, cabeças, toneladas, R$, população, abate, fogo, contagens do Censo, volumes Trase): **soma** com `min_count=1` (se todos os munis da AMC são NaN no ano, fica NaN, não 0).
   - **Derivadas** (13 razões/densidades: lotação, crédito/ha, pct_*, produtividade, pib_per_capita, densidade, taxa_abate_*): **recalculadas** das extensivas já somadas, com as mesmas fórmulas do #16.
   - **Razões reconstruídas** (5: `participacao_agro_pct`, `censo2017_lotacao_bov_ha`, `censo2017_pct_familiar/adubacao/agrotoxicos`): a razão da AMC = Σnumerador / Σdenominador, reconstruindo o denominador implícito de cada município. Crucial para `participacao_agro_pct`, que é `VA_agro/VA_total×100` (e VA_total **não** está no painel — reconstrói-se `VA_total_i = va_agro_i/(part_i/100)`). Somar ou promediar percentuais ignoraria o peso de cada município.
3. **Valida** e salva relatório de impacto.

### Por que a soma resolve

Antes da emancipação o filho é NaN e o pai carrega o valor do território inteiro → a soma da AMC = valor do pai = total correto. Depois, pai e filho têm valores e a soma continua correta. O agregado de AMC é **contínuo**, sem o salto espúrio.

## Como rodar

```bash
python scripts/construir_amc_goias.py            # usa crosswalk cacheado
python scripts/construir_amc_goias.py --force    # rebaixa a AMC do geobr
python scripts/construir_amc_goias.py --sem-geometria   # pula o GPKG
```

## Schema (painel_amc_goias.parquet)

```
code_amc       int    Código da AMC (Ehrl 2017)
amc_nome_rep   str    Nome do município-membro de maior área LULC (rótulo legível)
amc_n_munis    int    Quantos municípios atuais compõem a AMC (1 a 6)
ano            int    1985–2024
... 176 colunas de dado (mesmos nomes do #16: lulc_*, pec_*, agri_*, perm_*,
    sicor_*, abate_*, fogo_*, censo2017_*, e as derivadas lotacao_*, pct_*, etc.)
```

166 AMCs × 40 anos = **6.640 linhas**. (246 munis → 166 AMCs: 53 grupos pai+filhos, 113 unidades 1:1.)

## Validações realizadas

1. **Invariância do total estadual**: a soma estadual de `pec_bovinos_cab`, `lulc_pastagem_ha` e `agri_soja_ha_plantada` é **idêntica** entre o painel municipal e o de AMC (`max|Δ| = 0,000000`). Agregação conserva massa.
2. **Partição territorialmente constante**: **0 de 166 AMCs** estreiam no SIDRA depois de 1985 — toda AMC existia em 1985, prova de que cada filho foi colapsado com seu pai (sem gap de agrupamento).
3. **Artefato territorial eliminado** — pior queda anual de rebanho **nos grupos pai+filhos**:

   | Ano | Municípios-membro | AMCs agrupadas |
   |---|---|---|
   | 1989 | −73% | −12% |
   | 1993 | −81% | −31% |
   | 1997 | −43% | −9% |
   | 2001 | −43% | −4% |

   Exemplos concretos corrigidos: Cidade de Goiás (−56% em 1989 → AMC +32%, agrupada com Araguapaz/Faina/Santa Fé), Goianira (−64% em 1993 → AMC +2%), Pirenópolis (−37% em 1997 → AMC +15%).

## Verificação independente (`scripts/verificar_amc_goias.py`)

Validação ≠ ausência de erro. Um segundo script testa o resultado contra
verdades-terra **independentes** da lógica do #25 (rode após o pipeline):

1. **Identidade dos singletons** (o teste mais forte): as 113 AMCs de 1 município
   reproduzem o município **exatamente** em 173 colunas (NaN incluso). Se a
   classificação de colunas ou as fórmulas tivessem erro, falharia aqui.
2. **Re-agregação manual**: para AMCs multi-município, soma-se os membros do
   painel bruto célula a célula (sem `groupby`) e bate 100% com o painel AMC.
3. **Recálculo de razões** confere as fórmulas (lotação, crédito/ha, etc.).
4. **NaN preservado** (não virou 0).
5. **Contiguidade espacial** dos grupos (informativo).
6. **≥1 pai por grupo** + **limites físicos** (áreas ≥ 0, pct ∈ [0,100], lotação plausível).

**O que a verificação pegou e foi corrigido** (evidência de que o método funciona):
- `participacao_agro_pct` estava sendo recalculada como `va/PIB` (erro de ~6%);
  o correto é `va_agro/VA_total` — passou a ser reconstruída.
- Razão do Censo com numerador todo-NaN virava 0% (em vez de NaN) por causa do
  `skipna` da soma — corrigido com `min_count=1`.
- Três "falhas" eram falsos-positivos do próprio teste (arredondamento de 4 casas
  em `taxa_abate`; suposição "exatamente 1 pai"; AMC não-contígua por emancipação
  multi-pai) — documentados, não são erros do pipeline.

Resultado atual: **todos os testes passam**.

## Estratégia de dois trilhos (importante)

- **AMC = unidade canônica para análises LONGITUDINAIS** (primeiras diferenças, painel com efeitos fixos, DiD, periodização, "tal área cresceu/encolheu X%").
- **Os 246 municípios atuais (#16) permanecem para análises TRANSVERSAIS** e do período recente (Censo 2017, mapas de 2024), onde a malha já é estável.

Por isso este pipeline **não altera** `painel_unificado.parquet` — gera um painel paralelo.

### Consumidores a jusante (modo `--nivel amc`)

- **#17** (`calcular_taxas_lulc.py`) gera `taxas_lulc_amc.csv` automaticamente quando o crosswalk existe.
- **#22** (`correlacoes_painel.py --nivel amc`) → painel 2FE em AMC. **Re-teste confirma os achados** (mesmos sinais/significância, β mais fortes, R²w maior) — ver [22_correlacoes_painel.md](22_correlacoes_painel.md).
- **#24** (`analise_espacial.py --nivel amc`) → Moran/LISA/spreg em AMC. Estrutura espacial mantida.
- **Não consomem** (nível UF, invariante): #21, #23, #26, #29.

## Limitações

- **Granularidade**: 62 municípios atuais deixam de ser analisáveis isoladamente nas séries longas (ficam fundidos com pai/filhos). Inevitável quando o dado vem de pesquisa — a informação histórica do filho estava no pai.
- **Janela da AMC**: usa-se `1980–2010`. Goiás não criou municípios após ~2001, então a malha de 2010 vale até 2024. Se uma análise precisar incluir eventual desmembramento pós-2010 (inexistente em GO hoje), revisar.
- **Contagens de entidades Trase** (`*_n_exporters`, `*_n_hubs`, `*_n_frigorificos`): somadas — uma entidade atuante em >1 município é contada mais de uma vez (proxy, limite superior). Trase é camada secundária.
- **Resíduo de variação real**: AMCs minúsculas (ex.: Mambaí/Buritinópolis, ~14 mil cabeças) ainda oscilam bastante ano a ano — isso é variação **real** de rebanho, não artefato; a AMC só remove o componente territorial.
