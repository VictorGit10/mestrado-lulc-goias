# Backlog

Itens pendentes alinhados com o plano-mestre e [fontes_dados_adicionais.md](referencia/fontes_dados_adicionais.md).

## Já feito

- [x] Pipeline #1 — Pastagem × PIB UF (2 PNGs)
- [x] Pipeline #2 — Análise expandida UF (4 PNGs)
- [x] Pipeline #3 — Coleta SIDRA municipal (11 tabelas: PAM 1612 expandida 33 produtos, PAM 1613 expandida 38 produtos, PPM 95, PPM 74 mel/lã)
- [x] Pipeline #4 — MapBiomas municipal Goiás (8.6 MB CSV)
- [x] Pipeline #5 — Análise pastagem ↔ soja municipal (7 CSVs + 5 PNGs)
- [x] Pipeline #6 — Coleta SICOR/BACEN crédito rural 2013–2026 (5 CSVs)
- [x] Pipeline #7 — Censo Agropecuário 2017 (7 tabelas + painel 246×44)
- [x] Pipeline #8 — Crédito rural × LULC (3 CSVs + 7 PNGs)
- [x] Pipeline #9 — 40 mapas coropléticos municipais
- [x] Pipeline #10 — 40 mapas raster MapBiomas via GEE
- [x] Pipeline #11 — GIF animado LULC
- [x] Pipeline #12 — Matrizes de transição pixel-a-pixel via GEE
- [x] Pipeline #13 — IDH-M via IPEA Data API (1991/2000/2010)
- [x] Pipeline #14 — Fogo MapBiomas Collection 4 via GEE (CSV + 5 PNGs)
- [x] Pipeline #15 — Milho 1ª e 2ª safra (SIDRA 839, com análise descritiva)
- [x] Pipeline #16 — Painel unificado (9.840×~200, parquet + CSV) com todas as lavouras, permanentes, mel, lã e ovinos tosquiados
- [x] Pipeline #17 — Taxas de variação LULC (delta, slope 5a, SE Newey-West, aceleração) — UF, municípios, mesorregiões
- [x] Pipeline #18 — Mapeamento de mesorregiões IBGE 2017 (246 munis → 5 mesos)
- [x] Pipeline #19 — Transições brutas ano-a-ano (39 pares via GEE + agregação UF/municipal)
- [x] Pipeline #20 — Figuras de taxas (7 PNGs: slope, mesorregiões, delta, mapas, aceleração)
- [x] Pipeline #21 — Correlações UF Δ-vs-Δ (36 pares, 6 scatter plots)
- [x] Pipeline #22 — Painel municipal 2-way FE (16 modelos, 6 significativos)
- [x] Pipeline #23 — DiD GO vs MT/TO (36 modelos, 9 significativos)
- [x] Fix `agregar_conversoes.py` (2026-05-12) — caches GEE têm IDs agrupados 1–6, não MapBiomas brutos. CSV agora exporta 6×6 = 36 transições por ano-par (era 2×2), 39 pares validados em ±15% de 34 Mha.
- [x] Pipeline #26 — Detecção de quebras estruturais (binary segmentation + Quandt-Andrews) GO+TO (2026-05-13). 15 quebras em 6 séries. **Código Florestal 2012 sem quebra empírica em GO ou TO; Cerrado Manifesto 2018 é cerrado-amplo, não GO-específico; inflexão de veg. natural em GO é 1998 (Lei Kandir), não 1994 (Real).**
- [x] Renomeação "PAC Cerrado" → "Cerrado Manifesto" + rebaixamento dos achados DiD 2012/2018 (2026-05-13) — PAC Cerrado era label de rascunho sem programa real correspondente. Efeitos DiD 2012/2018 não replicam vs TO; texto e dados de choque do `index.html`/`marcos.json` atualizados; figuras DiD regeneradas.
- [x] **PIB e VAB agro UF nativos IPEA (1985-2023)** (2026-05-14) — novo `scripts/coleta_pib_uf_ipea.py` baixa séries `PIBE` e `PIBAGE` do IPEA Data, reescala 2010→dez/2024 via IPCA, gera `data/processed/pib_uf_ipea_goias.csv`. Pipeline #21 (`correlacoes_uf.py`) passa a usar essa série em vez do agregado municipal SIDRA — **N por par com PIB/VA agro sobe de ~21 para ~37**, novo par significativo (Δveg.natural × ΔPIB lag=1: r=+0,32, p=0,046). Site (`painel_goias.json` + acordeão socioeconômico) mostra as duas séries lado a lado. Comparação e quebra metodológica documentadas em `validacao_cruzada.md`.
- [x] **Robustez DiD: event-study + placebo + hierarquia TO** (2026-05-14) — `piecewise_did.py` ganhou `rodar_event_study()` e `rodar_placebo()`. Resultados em `event_study_resultados.csv` (132 linhas) + 12 figuras + `placebo_resultados.csv` (36 placebos). **Achado consolidado**: apenas Veg.natural × 1995 vs TO sobrevive ao conjunto parallel-trends + placebo + DiD sig. Demais efeitos pós-2012/2018 vs MT/combined têm placebos significativos (dinâmica pré-existente, não causal). Veja `23_did.md`.
- [x] **Robustez painel multivariada** (2026-05-14) — `correlacoes_painel.py` ganhou `rodar_painel_multivariado()`. 9 modelos multivariados em `painel_multivariada.csv`. **Achado**: SICOR é canal dominante de retração de pastagem (β=−0,003, p<0,001 com VA agro+Bovinos+Fogo no modelo); VA agro perde sig. Intensificação Δ Agricultura × Δ VA agro sobrevive em todas variantes (com/sem SICOR, ambas janelas). R²w salta de 0,047→0,122 em agricultura. VIFs ≤ 1,55.
- [x] **Pipeline #24 — análise espacial estatística** (2026-05-14) — novo `scripts/analise_espacial.py` com Moran's I global, LISA e regressão espacial (OLS/SAR/SEM via `spreg`). **115 de 140 resíduos (modelo × ano × W) têm I sig** — autocorrelação espacial é estrutural. Pico em 2018 (I=+0,53 para pastagem × bovinos). spreg cross-section 2020 mostra SEM com pequena vantagem sobre OLS (λ=+0,06–0,08). 8 mapas LISA gerados. `requirements.txt` ganha pysal stack.
- [x] **Pipeline #27 — Trase.earth integrado** (2026-05-15) — novo `scripts/coleta_trase.py` lê zips de soja (2004–2022) e bovinos (2011–2023 sem 2018) baixados de `resources.trase.earth/20260511/`, filtra GO, mapeia nomes Trase (caixa-alta sem acentos) para cd_mun IBGE via mapeamento_mesorregioes.csv, agrega por (cd_mun, ano). Saída: `data/processed/painel_trase.csv` (4.109 linhas, 244 munis, 12 colunas — volume/fob/n_exporters/n_hubs/top_exporter para soja e boi). Top munis batem: Rio Verde/Jataí/Cristalina (soja); Vale do Araguaia (boi, com JBS/Minerva/Marfrig nominais). `construir_painel_unificado.py` ganha `load_trase()` e merge em (cd_mun, ano). **Limitação importante**: Trase rastreia só fluxo exportador — produção processada domesticamente não entra. Proxy de exposição a cadeia agroindustrial exportadora, não de capacidade total de abate.
- [x] **Censo Agro 2017 — tabelas 6855 e 6877** (2026-05-15) — `coleta_sidra.py` estendido para coletar tabela 6855 (plantio direto na palha: nº estab + ÁREA) e 6877 (veículos no estabelecimento: caminhões, utilitários, automóveis). `load_censo_2017()` em `construir_painel_unificado.py` integra 5 novas colunas: `censo2017_area_plantio_direto_ha` (Rio Verde 362k ha lidera, top 5 = top 5 soja Trase), `censo2017_n_estab_plantio_direto`, `censo2017_n_estab_com_veiculos`, `censo2017_n_veiculos_total`, `censo2017_n_caminhoes`. Painel agora 9.840 × 179 colunas (era 174 antes da integração Trase+Censo extras).
- [x] **Pipeline #29 — Triangulação para periodização data-driven** (2026-05-19) — 3 métodos independentes (sup-F multivariado, Rodionov STARS, KL/TV de transições) mais verificação de sanidade (#30) e Intensity Analysis (#31). Resultado: **3 períodos data-driven confirmados** — P1: 1985-2000 (Pastagem como herança), P2: 2001-2019 (Expansão e intensificação), P3: 2020-2024 (Conversão seletiva). Fronteira ~2005/2006 não incluída como período: método primário não a detecta, taxa total P2(01-05) vs P2(06-19) não difere significativamente (p=0.060), fronteira sensível ao ponto de corte. Sub-fase 2001-05 documentada como nota metodológica (perda de veg_nat 5x mais intensa, p=0.0008). Documentação em `29_triangulacao_periodizacao.md`. `config_periodos.py` centraliza ATOS (3 períodos) e MARCOS (8, tipologia A/B/C).
- [x] **Pipeline #30 — Verificação de sanidade da periodização** (2026-05-19) — Falso positivo (ruido branco), sensibilidade de parâmetros (9 combinações min_size × F_threshold), consistência univariado vs multivariado, robustez STARS (6 parametrizações). FPR aceitável com F≥4.0; 2001 robusta em 100% das combinações; 1991 instável (desloca com min_size); STARS com α=0.05 detecta 2004/2006, com α=0.01 nada detecta.
- [x] **Pipeline #31 — Intensity Analysis (Aldwaik & Pontius 2012)** (2026-05-19) — Diagnóstico focal P2 vs P3. 3 níveis: intervalo (taxa total), categoria (perda/ganho por classe), transição (fluxos específicos). Kruskal-Wallis 4 períodos: H=22.57, p<0.001. P2 vs P3: taxa total p=0.060 (NS), mas perda de veg_nat p=0.0008 (***). Bootstrap: IC 95% P2-P3 não contém zero. Sem 2004 (outlier): P2 vs P3 p=0.189 (NS). Sensibilidade ao corte: significativo em 2005 (p=0.046), marginal em 2004 (p=0.10), NS em 2006 (p=0.12). `verificacao_intensity.py`: consistência de dados (<1.7%), simulação de poder (n=4: poder=0.63, n=7: poder=0.83), bootstrap de IC.

## Em andamento (2026-05-15)

- [x] **Pipeline #28 — Idade da pastagem na conversão para agricultura** (2026-05-15) — Sub-pipelines A (coleta GEE) e B (análise descritiva) concluídos. 78.000 pixels coletados, 241 munis, 1986-2024. Calcula idade da pastagem em Python a partir de bandas `classification_YYYY` amostradas via `stratifiedSample` (não exige asset MapBiomas Pastagem separado). **Achado-chave: período 2018-24 tem distribuição BIMODAL — picos em ~5a e ~35a — assinatura empírica direta da coexistência dos mecanismos premeditado e oportunístico.** Sensibilidade ao corte temporal a verificar (janelas deslizantes). Sul Goiano (37% dos pixels) com mediana 9a domina conversão; Norte/Noroeste mediana 20a. Coorte veg.nat→pastagem→agric (20.5%, n=16.009) mediana 13a com cauda longa; rotação agric→pastagem→agric (12.1%) mediana 5a. Sem correlação com Δ SICOR/Δ VA agro municipais. Outputs: `data/processed/pastagem_idade_conversao.csv`, 6 PNGs em `outputs/idade_pastagem/`, 2 JSONs em `Visualizacao/assets/data/`. **Sub-pipeline C (aba na Visualizacao/) pendente.**

## Em andamento (sequência A→B→C, 2026-05-12)

- [x] **Frente A** — Fix conversao_bruta_*.csv (concluído)
- [ ] **Frente B** — Pipeline #25: `scripts/analise_transicoes.py` (matrizes 6×6 por ATO, decomposição de origem, fluxo bruto vs líquido, 3 JSONs Sankey, top por mesorregião)
- [ ] **Frente C** — Refinar primeira aba do `Visualizacao/index.html`:
  - C1: cards diversificados de produção (mini-grid 4 culturas por ATO, explora painel ampliado)
  - C2: toggle de camadas no sticky-map (Cobertura | Δ | Fogo | Transições)
  - C3: pull-quotes nos marcos 1994/1996/2003/2012/2018
  - C4: mini-sankey ao fim de cada ato (consome JSONs da Frente B)
  - C5: highlight barra empilhada ↔ pixels do mapa
- [ ] **Sub-pipeline #28-C — Aba "Pastagem como reserva de terra" no `Visualizacao/index.html`** (criada 2026-05-15). JSONs prontos em `Visualizacao/assets/data/idade_pastagem_municipal.json` (~41 KB, idade mediana/média/n por município) e `idade_pastagem_histograma.json` (~3 KB, histograma por ATO com bins/counts/mediana). Componentes propostos:
  - **Mapa coroplético municipal** de idade mediana na conversão, com classes em quantis (jovem/médio/antigo) e toggle por ATO.
  - **Histograma interativo** por ATO com slider temporal, **destacando visualmente o achado bimodal no período 2018-24** — picos em ~5a (premeditado) e ~35a (oportunístico). Sensibilidade ao corte temporal a verificar (P#28, seção 2F).
  - **Pull-quote narrativo** com a hipótese e leitura empírica.
  - **Cards de coortes** comparando `veg.nat → pastagem → agric` (n=16.009, mediana 13a) vs rotação `agric → pastagem → agric` (n=9.419, mediana 5a).
  - Padrão alinhado com `timeline.js` / `inventario.js` / `atlas.js`. Conexão com a tese: refina a leitura do Δ Pastagem × Δ SICOR β=−0,003 (Pipeline #22) ao distinguir se SICOR opera sobre pastagem nova ou antiga.

## Eixos prioritários — próxima sprint (2026-05-15)

### Eixo A — Análise Trase × LULC (Granger + cross-lagged)

Pipeline #27 deixou 8 colunas Trase no painel sem análise rodada.

- **Pergunta**: "infra exportadora segue ou lidera expansão LULC?"
- **Abordagem**: Granger pairwise em painel + cross-lagged (Y[t] ~ Y[t-1] + X[t-1] e modelo reverso). Padrão dos Pipelines #21-23.
- **Limitação**: janela curta (Trase soja 2004-22, boi 2011-23 sem 2018) — talvez agregar a mesorregião para ganhar poder.
- **Esforço**: 1-2 dias.
- **Valor**: conecta infra agroindustrial à dinâmica LULC; complementa modelo multivariado do Pipeline #22.

### Eixo B — Iniciar redação da dissertação

- **Estado**: zero capítulos. Só metadados, pipelines documentados, decisões metodológicas D1-D9, validação cruzada.
- **Estrutura típica CIAMB**: Introdução → Referencial → Métodos → Resultados → Discussão → Conclusões → Referências.
- **Estratégia**: começar por Métodos (~70% pronto em `Textos/metodologia/`), depois Resultados (consolida narrativa do site em prosa), por último Introdução + Referencial (exigem revisão bibliográfica externa).
- **Esforço**: trabalho contínuo de semanas, não cabe em sprint.
- **Valor**: sem texto não há defesa.

### Eixo C — Painel espacial dinâmico + validação de quebras data-driven

- **C1**: Pipeline #24 hoje é cross-section 2020. Estender com `spreg.Panel_FE_Lag` em todas as janelas. Resolve fragilidade de autocorrelação espacial estrutural não modelada no painel #22. Esforço 2-3 dias.
- **C2**: Validar via literatura as quebras 1991 (Plano Collor?), 1999 (câmbio flutuante?), 2006 (Moratória Soja Amazônia?) detectadas pelo Pipeline #26 sem marco teórico atribuído. Trabalho de leitura + redação curta, não código. Esforço 1-2 dias.

## Coletas pendentes

| # | Coleta | Esforço | Valor | Risco | Tier |
|---|--------|---------|-------|-------|------|
| 1 | Censo Agro 6850 (calcário) | 30 min | Insumo de correção de solo, proxy intensificação | Nenhum | **trivial** |
| 2 | Censo Agro 6779/6780 (orientação técnica) | 30 min cada | Proxy capacitação/extensão rural | Nenhum | **trivial** |
| 3 | IDH-M 2021 (Atlas Brasil PNUD, manual) | 1-2 h | Fecha série decenal 1991/2000/2010/2021 | Baixo | **trivial** |
| 4 | CONAB SISDEP (armazéns 2006+) | 3-5 dias | Capacidade armazenagem, proxy logística pós-colheita | Médio | |
| 5 | DNIT/SNV (rodovias 2013+) | ~1 semana | Distância à BR pavimentada + densidade rodoviária | Médio (pré-2013 só gROADS/OSM) | |
| 6 | CNPJ Receita Federal (1985-2024) | 1-2 semanas | Capacidade industrial doméstica anual, complementa Trase | Alto (não diferencia SIF/SIE/SIM, big files) | **descartado 2026-05-15** |
| 7 | SIGSIF/MAPA (frigoríficos federais hist.) | dias-meses | Flag tem_sif por município | Alto (LAI pode demorar) | **descartado 2026-05-15** |
| 8 | PRODES Cerrado (INPE) | 1-2 dias | Desmatamento oficial INPE, comparação cruzada com MapBiomas | Baixo | |
| 9 | TerraClass Cerrado | 3-5 dias | Distingue pastagem íntegra vs degradada | Médio | |
| 10 | CAR/SICAR | 3-5 dias | Limites prediais + Reserva Legal declarada | Baixo-médio | |
| 11 | Precipitação (Xavier/ERA5) | 3-7 dias | Controle climático para regressões | Médio (NetCDF) | |

Itens 1-3 (~3-4 h totais) são triviais e fecham lacunas menores. Itens 5 e 6 foram descartados em 2026-05-15 por esforço desproporcional ao valor residual para a dissertação; item 7 (SIGSIF) descartado pela incerteza do acesso via LAI.

## Decisões de espacialização pendentes

- Malha de referência: **IBGE 2020** (recomendado, default).
- CRS para cálculo de área: **EPSG:5880 SIRGAS Albers** (Brasil).
- Pacote de malha: `geobr`.
- Mapas finais: pipeline gera GPKG/CSV, QGIS faz layout cartográfico.