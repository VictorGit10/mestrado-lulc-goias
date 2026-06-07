# Pipelines — índice

Pipelines **#1–#38** documentados aqui — **37 com doc dedicado**; o **#27** (Trase) ainda está sem doc próprio, e o **#30** e o **#31** vivem dentro do [#29](29_triangulacao_periodizacao.md). Cada arquivo descreve **processo** (o que faz, como rodar, decisões metodológicas, validações, limitações). Para descrição dos **produtos** (PNGs, CSVs com interpretação para redação), ver [outputs/](../outputs/).

## Tabela resumo

| # | Arquivo | Script | Foco | Período | Nível | Status |
|---|---|---|---|---|---|---|
| 1 | [01_pastagem_pib.md](01_pastagem_pib.md) | `grafico_pastagem_pib_goias.py` | Pastagem × PIB UF | 1985–2024 | Estado (GO) | ✅ |
| 2 | [02_analise_expandida.md](02_analise_expandida.md) | `analise_expandida_goias.py` | Cobertura, rebanho, lotação, PIB agro | 1985–2024 | Estado (GO) | ✅ |
| 3 | [03_coleta_sidra.md](03_coleta_sidra.md) | `coleta_sidra.py` | 8 tabelas SIDRA municipais | Variável | Municipal | ✅ |
| 4 | [04_mapbiomas_municipal.md](04_mapbiomas_municipal.md) | `pipeline_municipal.py` | MapBiomas Col 10.1 municipal | 1985–2024 | Municipal | ✅ |
| 5 | [05_pastagem_soja.md](05_pastagem_soja.md) | `analise_pastagem_soja.py` | Transição pastagem ↔ soja (proxy) | 1985–2024 | Municipal | ✅ |
| 6 | [06_sicor.md](06_sicor.md) | `coleta_sicor.py` | Crédito rural SICOR/BACEN | 2013–2026 | Municipal | ✅ |
| 7 | [07_censo_agro.md](07_censo_agro.md) | `coleta_sidra.py --censo-agro` | Censo Agro 2017 (7 tabelas) | 2017 | Municipal | ✅ |
| 8 | [08_credito_lulc.md](08_credito_lulc.md) | `analise_credito_uso_terra.py` | Crédito × uso da terra | 2013–2023 | Municipal | ✅ |
| 9 | [09_mapas_coropleticos.md](09_mapas_coropleticos.md) | `gerar_mapas_lulc_40anos.py` | 40 mapas coropléticos | 1985–2024 | Municipal | ✅ |
| 10 | [10_mapas_gee.md](10_mapas_gee.md) | `gerar_mapas_lulc_gee_40anos.py` | 40 mapas raster GEE 30m | 1985–2024 | Estado (raster) | ✅ |
| 11 | [11_gif_lulc.md](11_gif_lulc.md) | `gerar_gif_lulc.py` | GIF animado 40 anos | 1985–2024 | Estado | ✅ |
| 12 | [12_transicoes.md](12_transicoes.md) | `transicoes_mapbiomas.py` | Matrizes pixel-a-pixel via GEE | 1985–2024 | Municipal | ✅ |
| 13 | [13_idhm.md](13_idhm.md) | `coleta_idhm.py` | IDH-M (IPEA API) | 1991/2000/2010 | Municipal | ✅ (pós-2010 inexistente) |
| 14 | [14_fogo.md](14_fogo.md) | `fogo_mapbiomas.py` | Área queimada × LULC via GEE | 1985–2024 | Municipal | ✅ |
| 15 | [15_safrinha.md](15_safrinha.md) | `coleta_sidra.py --so 839` | Milho 1ª/2ª safra | 2003–2024 | Municipal | ✅ (sem análise gráfica) |
| 16 | [16_painel_unificado.md](16_painel_unificado.md) | `construir_painel_unificado.py` | Painel wide 9.840 × 66 | 1985–2024 | Municipal | ✅ |
| 17 | [17_taxas_lulc.md](17_taxas_lulc.md) | `calcular_taxas_lulc.py` | Taxas de variação LULC (slope, delta, aceleração) | 1985–2024 | UF, muni, meso | ✅ |
| 18 | [18_mesorregioes.md](18_mesorregioes.md) | `mapeamento_mesorregioes.py` | Mapeamento cd_mun → mesorregião IBGE 2017 | — | Municipal | ✅ |
| 19 | [19_conversoes_brutas.md](19_conversoes_brutas.md) | `agregar_conversoes.py` | Transições brutas ano-a-ano (A→B) | 1985–2024 | UF, muni | ✅ |
| 20 | [20_figuras_taxas.md](20_figuras_taxas.md) | `figuras_taxas.py` | 7 figuras de taxas (slope, delta, aceleração, mapas) | 1985–2024 | UF, muni, meso | ✅ |
| 21 | [21_correlacoes_uf.md](21_correlacoes_uf.md) | `correlacoes_uf.py` | Correlações LULC × socioeconômicas UF (Δ-vs-Δ, HAC) | 1985–2024 | UF | ✅ |
| 22 | [22_correlacoes_painel.md](22_correlacoes_painel.md) | `correlacoes_painel.py` | Painel municipal 2-way FE (entity + time) | 2002–2023 | Municipal | ✅ |
| 23 | [23_did.md](23_did.md) | `piecewise_did.py` | DiD piecewise GO vs MT/TO + event-study + placebo | 1985–2024 | UF | ✅ |
| 24 | [24_analise_espacial.md](24_analise_espacial.md) | `analise_espacial.py` | Moran's I, LISA, regressão espacial (OLS/SAR/SEM) | 2013–2021 | Municipal | ✅ |
| 25 | [25_amc_goias.md](25_amc_goias.md) | `construir_amc_goias.py` | Áreas Mínimas Comparáveis (Ehrl 2017) — painel 6.640 × 180 para análise longitudinal | 1985–2024 | AMC (166) | ✅ |
| 26 | [26_deteccao_quebras.md](26_deteccao_quebras.md) | `deteccao_quebras.py` | Detecção de quebras estruturais (sup-F + binary segmentation) GO+TO | 1985–2024 | UF | ✅ |
| 28 | [28_idade_pastagem.md](28_idade_pastagem.md) | `coleta_idade_pastagem.py` + `analise_reserva_terra.py` | Idade da pastagem na conversão para agricultura (hipótese "reserva de terra") | 1986–2024 | Pixel amostrado (78k) + municipal | ✅ |
| 29 | [29_triangulacao_periodizacao.md](29_triangulacao_periodizacao.md) | `periodizacao_multivariada.py` + `periodizacao_stars.py` + `periodizacao_transicoes.py` | Triangulação para periodização data-driven (sup-F multivariado + STARS + KL/TV) | 1985–2024 | UF (GO) | ✅ |
| 30 | (em #29) | `verificacao_periodizacao.py` | Verificação de sanidade (FPR, sensibilidade, consistência) | 1985–2024 | UF (GO) | ✅ |
| 31 | (em #29) | `intensity_analysis.py` + `verificacao_intensity.py` | Intensity Analysis (Aldwaik & Pontius 2012) + diagnóstico P2 vs P3 | 1985–2024 | UF (GO) | ✅ |
| 32 | [32_centro_massa.md](32_centro_massa.md) | `centro_massa.py` | Centro de massa migratório das AMCs (Camada 1 Sul→Norte) | 1985–2024 | AMC (166) | ✅ |
| 33 | [33_transicoes_regionais.md](33_transicoes_regionais.md) | `transicoes_regionais.py` | Mecanismo de transições por mesorregião × ato (Camada 2 Sul→Norte) | 1985–2024 | Mesorregião (5) | ✅ |
| 34 | [34_deslocamento_espacial.md](34_deslocamento_espacial.md) | `deslocamento_espacial.py` | Lead-lag + spillover espacial (Camada 3 Sul→Norte) — teste formal de deslocamento | 1985–2024 | AMC (166) | ✅ |
| 35 | [35_robustez_janelas.md](35_robustez_janelas.md) | `robustez_janelas.py` | Robustez multi-resolução de #32/#33 (atos vs grade 5a vs décadas) | 1985–2024 | AMC + meso | ✅ |
| 36 | [36_robustez_janela_slope.md](36_robustez_janela_slope.md) | `robustez_janela_slope.py` | Robustez do slope do #17 à largura da janela móvel (3/5/7/10 anos) | 1985–2024 | UF (GO) | ✅ |
| 37 | [37_drive_comum.md](37_drive_comum.md) | `coleta_drivers_macro.py` + `drive_comum.py` | Drivers macro (preço recebido, câmbio real, crédito) × inflexões do LULC — testa o "drive comum" do #34 | 1985–2024 | UF (GO) | ✅ |
| 38 | [38_drive_comum_amc.md](38_drive_comum_amc.md) | `drive_comum_amc.py` | Drive comum no painel AMC: interação **driver × exposição** (2FE) — testa o gradiente de aptidão (indício sugestivo, não confirmado sob FDR) | 1985–2024 | AMC (166) | ✅ |

## Como os pipelines se cruzam

- **#1 e #2** foram feitos antes do plano-mestre amadurecer; produzem só análises **descritivas no nível UF**, úteis como "primeira foto" da tese e como baseline de validação batimental.
- **#3, #4, #6, #7** são o **fundamento real da dissertação**: dados municipais brutos prontos para correlações, mapas e regressão espacial.
- **#5 consome #3 e #4** para produzir a primeira camada analítica municipal — métricas de transição pastagem↔soja por município e período, com validação cruzada entre as duas fontes (MapBiomas vs SIDRA).
- **#8 consome #3, #4, #5, #6** para cruzar crédito × LULC.
- **#9 e #10** consomem #4 para mapas; #10 também usa GEE direto.
- **#11** consome PNGs do #10.
- **#12** é independente (puro GEE) e **substitui o #5 como fonte de matriz de transição** real (pixel-a-pixel).
- **#13, #14, #15** alimentam slots do painel unificado (#16).
- **#16** consolida #3, #4, #6, #7, #13, #15 num painel pronto para análise espacial estatística.
- **#25** consome #16 e a concordância AMC do `geobr` (Ehrl 2017). Agrega o painel municipal em 166 Áreas Mínimas Comparáveis de território constante — unidade canônica para as análises **longitudinais** (corrige o viés de 25% de munis criados após 1985). Ver D11 em [metodologia/areas_minimas_comparaveis.md](../metodologia/areas_minimas_comparaveis.md).
- **#32** consome #25 (painel AMC e geometrias GPKG) para calcular o centro de massa migratório (médio e mediano) e elipses de dispersão por ato, consolidando a Camada 1 da narrativa de deslocamento Sul→Norte.
- **#33** consome #19 (conversões brutas), #18 (mesorregiões) e #28 (idade do pasto), reusando a maquinaria do #25 (`analise_transicoes.py`). Re-corta as transições 6×6 por mesorregião × ato e quantifica o **mecanismo** Sul→Norte (Sul: pasto→agric; Norte: veg→pasto) — Camada 2, que explica o movimento do centroide do #32.
- **#34** consome #25 (painel AMC + geometria), #17 (deltas) e #18 (mesorregiões), reusando convenções de #22 (painel FE) e #24 (pesos espaciais). Faz o **teste formal de deslocamento** (Camada 3): lead-lag temporal (Granger/CCF) + spillover espacial direcional (SLX em painel FE). **Resultado de não-confirmação**: o padrão Sul→Norte é reorganização espacial sob drive comum, **não** deslocamento causal (sem precedência temporal nem spillover direcional). Tempo contínuo (não bina por ato).
- **#35** reusa #32 e #33 e recalcula as métricas-manchete (velocidade N–S; gradiente de fluxos) sob **três réguas de tempo** (atos, grade de 5 anos, décadas) + referência contínua/janela-única. **Os achados são robustos**: pasto sempre marcha ao norte e o gradiente Sul(pasto→agric)/Norte(veg→pasto) vale em ~todas as janelas; a desaceleração recente da agricultura é nítida só em réguas que isolam 2020–24 (confirma que é fenômeno pós-2020).
- **#36** reusa #17 e recalcula as manchetes de **slope** sob **quatro larguras de janela móvel** (3/5/7/10 anos) — é a **face de resolução** da D12 (largura da suavização), complementar à **face de fronteira** do #35 (onde cortar). **Robustos**: a desaceleração da vegetação e a freada recente da agricultura valem em toda janela; o pico da pastagem é robusto a menos do atraso esperado do trailing — **confirmado pela versão centrada** (`rolling_slope_hac_centr`), que fixa o cruzamento de zero em ~2002–03 independente da largura. Sensibilidades informativas: a cronologia interna da expansão agrícola (multi-pico) e a aceleração (frágil — só o pico de pastagem 2004 sobrevive às 4 janelas, confirmando a D5 do #17).
- **#17** consome #4 (dados brutos MapBiomas municipal) e #18 (mesorregiões). Produz métricas de variação LULC para #20 e para as correlações da Etapa 2.
- **#18** é independente (geobr). Alimenta #17 e #20 com o mapeamento cd_mun → mesorregião.
- **#19** consome #12 com flag `--consecutivos` (39 pares ano-a-ano). Produz conversão bruta A→B para análise de fluxo.
- **#20** consome #17 (taxas) e #18 (geometrias) para figuras.
- **#21** consome #17 (taxas UF) e #16 (painel socioeconômico) para correlações UF in primeiras diferenças (D7).
- **#22** consome #17 (taxas municipais) e #16 (painel socioeconômico) para painel 2-way FE (D8). Resíduos alimentam análise espacial (Moran's I).
- **#23** consome #17 (taxas GO) + séries MT/TO baixadas via GEE. DiD piecewise (D9).
- **#29** consome #17 (taxas GO) e #19 (transições). Triangulação de 3 métodos para estabelecer fronteiras data-driven dos atos. Define `config_periodos.py` (ATOS, MARCOS) que #20, #23, #26, #28, #31 importam.
- **#30** (verificação de sanidade) consome #29a diretamente. Testa FPR, sensibilidade de parâmetros, consistência univariado vs multivariado, robustez STARS.
- **#31** consome #19 (transições) e #17 (taxas). Intensity Analysis (Aldwaik & Pontius 2012) para testar se P2 e P3 diferem em taxa de mudança. Diagnóstico complementar para fronteira 2005/2006.
- **#37** coleta drivers macro **exógenos** novos (IPEA Data: preços internacionais IMF IFS, câmbio real efetivo REER, crédito rural longo CREATE-GO) e cruza com #17 (deltas LULC), #26 (quebras) e #34 (séries regionais). Reusa `ccf_defasada`/`granger` do #34 e `pearson_with_hac` do #21. **Testa o "drive comum"** que o #34 deixou inferido — mas na série **UF/anual (N≈38)**: os hits não sobrevivem a multiplicidade e só o **câmbio** tem estrutura (aparece em duas margens). Camada 4 da narrativa Sul→Norte; deixa o teste com poder para o #38.
- **#38** consome #37A (drivers macro), #25 (painel AMC, rebanho) e `taxas_lulc_amc`, reusando o padrão **PanelOLS 2-way FE** do #22. **Muda a unidade de análise** do #37 (UF/anual, N≈38) para o **painel AMC** (~6.600 obs) e testa o **gradiente de aptidão** via interação **driver × exposição baseline**: o γ_t absorve o choque comum, a interação identifica o gradiente. Clusterização dupla (entidade+ano) + **conjunto confirmatório teórico** + **grade exploratória FDR** (lição de multiplicidade do #37). **Achado (sóbrio)**: a hipótese confirmatória câmbio × fronteira → **REBANHO** confirma a direção (p=0,031), mas a grade exploratória completa (lags 0/1/2, 144 testes) **não devolve nenhum** sobrevivente do FDR — o gradiente no rebanho é **sugestivo, não estabelecido**; a área LULC **não** responde (nulo robusto). Avança (não fecha) a Camada 5.

## Convenções

- **Cache CSV** em todos os coletores — re-execuções são instantâneas; `--force` rebaixa.
- **Schema padronizado** quando possível: chave municipal `cd_mun` (IBGE 7 dígitos) + `nm_mun` + `ano`.
- **Idempotência**: rodar o mesmo pipeline duas vezes produz output idêntico.
- **Deflação para R$ dez/2024** via IPCA — ver [metodologia/deflacao_ipca.md](../metodologia/deflacao_ipca.md).
