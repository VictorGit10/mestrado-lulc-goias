# Backlog

> **Modo atual: EXPLORAÇÃO, não redação.** A fase agora é gerar análises, pensá-las e
> **descobrir as histórias dos 40 anos de dados**. A redação é adiada **por opção** — virá
> quando o autor decidir parar e escrever (e será barata, porque tudo está documentado em
> `Textos/` de forma completa e didática). **Como ler este arquivo**: "Já feito" é o *mapa
> do território já explorado* (inventário, não checklist de conclusão); **"Fios em aberto"
> logo abaixo é onde a ação está**. As frentes mais antigas falam em "sprint / prioritário
> / redação" — descontar esse enquadramento de conclusão ao ler.

Itens alinhados com o plano-mestre e [fontes_dados_adicionais.md](referencia/fontes_dados_adicionais.md).

## Fios em aberto — perguntas a puxar (exploração)

As histórias mais ricas ainda não contadas, em ordem de **riqueza × viabilidade com o dado
que já existe**. Nenhuma exige redação; todas são investigação.

1. ~~**Caracterizar o "drive comum"**~~ — ✅ **FEITO (2026-06-06, [#37](pipelines/37_drive_comum.md))**.
   Resultado: câmbio-competitividade (REER) e crédito rural **antecedem** as inflexões do LULC
   (exogeneidade confirmada); o **preço** de commodity **co-move contemporâneo, não lidera**. A órfã
   1991 = colapso de crédito do Plano Collor. Detalhe completo em "Já feito".
2. **As duas lógicas da pastagem** — a bimodalidade do [#28](pipelines/28_idade_pastagem.md)
   (picos ~5a e ~35a em 2018–24) é uma manchete enterrada: pasto-trampolim **planejado** de
   5 anos vs. conversão **oportunista** de pasto degradado de 35 anos. **Espacializar** onde
   cada lógica domina e cruzar com plantio direto (#27/Censo). Tipologia de "carreira da terra".
3. **A fronteira está fechando?** — no [#32](pipelines/32_centro_massa.md) tudo marchou ao
   norte (+65 a +78 km) menos a vegetação (+8 km, parada). Testar se a desaceleração recente
   da agricultura é **oferta de Cerrado convertível se esgotando** (supply-side / *frontier
   closure*), não só demanda. Mapear terra convertível restante por região no tempo.
   Reinterpretação, não só mais um cruzamento — pode ser a história mais surpreendente.
4. **Fogo como assinatura antecipatória da fronteira** — o [#14](pipelines/14_fogo.md) está
   fora da narrativa Sul→Norte. Lead-lag do centroide do fogo vs. centroide da conversão
   veg→pasto: o fogo lidera a marcha ao norte? Barato (dado pronto).
5. **O Granger reverso Norte→Sul** — o #34 achou precedência reversa (ΔPasto_Norte →
   ΔAgric_Sul, **p=0,0007**) e descartou por N pequeno. Se real, **inverte a leitura**. Cutucar.
6. **Crescimento sem desenvolvimento?** — IDH-M ([#13](pipelines/13_idhm.md); 2021 é coleta
   trivial pendente). O boom agrícola chegou às pessoas? Sul (intensificação) vs. Norte
   (fronteira) no desenvolvimento humano — espelho socioeconômico dos "dois Goiáses".

- **Bônus / micro-mistério**: o [#29](pipelines/29_triangulacao_periodizacao.md) viu uma
  sub-fase **2001–05** com perda de veg natural **5× mais intensa** (p=0,0008) que não virou
  período. O que houve nessa janela curta (onset do boom da soja, pré-Moratória, pré-Código)?

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
- [x] **Pipeline #32 — Centro de massa migratório (keystone, Camada 1 da narrativa Sul→Norte)** (2026-06-06) — `scripts/centro_massa.py`: *mean center* anual ponderado + *median center* (Weiszfeld 1937, robusto) + elipse de desvio-padrão (Yuill 1971) por ato, sobre os centroides das 166 AMCs (#25) em EPSG:5880. Variáveis: pastagem, agricultura, rebanho bovino, vegetação natural. **Achado — refina e em parte CONTRARIA a hipótese-mãe**: não é "agricultura estática × rebanho subindo". **Toda a fronteira agropecuária marchou para o norte** 1985→2024 (pastagem ΔN +78 km, rebanho +67 km, agricultura +65 km; veg. natural quase parada, +8 km). O que **sustenta** a narrativa: (a) **gradiente latitudinal persistente** — a agricultura fica ~1,1–1,2° (≈120–130 km) AO SUL de pasto/rebanho em todos os anos, com a veg. natural como fronteira norte; (b) a **pastagem lidera** o avanço ao norte; (c) a agricultura expande-se a NORDESTE (azimute 37°, ΔL +50 km) enquanto pasto/rebanho sobem quase a prumo (azimute 14°/19°, ΔL +19/+23 km); (d) **só no Ato III (2020-24) a agricultura desacelera** (ΔN +0,2 km) enquanto pasto (+11 km) e rebanho (+8 km) seguem subindo — o sinal mais limpo de deslocamento, e é o período atual. AMC neutraliza o artefato de emancipação no rebanho (D11). Saídas: `data/processed/centro_massa_anual.csv` (160 linhas), `centro_massa_elipses.csv` (12), `centro_massa_deslocamento.csv` (16) + 4 PNGs em `outputs/centro_massa/` (overview, trajetórias-zoom, elipses-por-ato, latitude×ano). **Camada 1 ✓; Camadas 2 (mecanismo por mesorregião) e 3 (lead-lag/spillover) pendentes.**
- [x] **Pipeline #33 — Mecanismo de transições por mesorregião × ato (Camada 2 da narrativa Sul→Norte)** (2026-06-06) — `scripts/transicoes_regionais.py`: re-corta as conversões brutas (#19) por (mesorregião × ato), reusando a maquinaria do #25 (`analise_transicoes.py`). Matriz 6×6, fluxos-chave em **taxa anual** (Mha/ano — atos têm durações diferentes: 15/18/4 anos), balanço líquido e cruzamento com a idade do pasto (#28). **Mecanismo confirmado, mas como gradiente RELATIVO, não exclusivo**: (a) a transição-mãe de GO é `veg→pasto` (dominante na maioria das células); `pasto→agric` só **lidera** em **Sul+Centro no Ato II** (o boom); (b) o **deslocamento aparece no balanço líquido**: no Ato II o **Sul perde pasto líquido (−0,57 Mha)** e ganha agricultura (+0,76) enquanto **Norte (+0,13)/Noroeste (+0,09) ganham pasto** — pasto sai do Sul, reaparece no Norte; (c) no **Ato III** `pasto→agric` do Sul despenca (0,066→0,008 Mha/ano, −88% → agricultura desacelera, #32) enquanto `veg→pasto` do Norte persiste (~0,038 → pasto/rebanho seguem subindo, #32); (d) idade do pasto na conversão: Sul **9a** (reserva jovem) → Norte **20a** (fronteira). **Cadeia fechada**: mecanismo → redistribuição líquida → centroide do #32. Saídas: 3 CSVs (`transicoes_regionais_*`), 2 PNGs (`outputs/transicoes_regionais/`), `sankey_regional.json` (15 mini-Sankeys). **Camada 2 ✓; Camada 3 (econômica, lead-lag/spillover) pendente.**
- [x] **Pipeline #34 — Deslocamento Sul→Norte: lead-lag + spillover espacial (Camada 3, teste FORMAL)** (2026-06-06) — `scripts/deslocamento_espacial.py`, no **tempo contínuo** (painel anual AMC, sem binar por ato — decisão para evitar circularidade com #29). (A) lead-lag regional ΔAgric_Sul → ΔPasto/ΔRebanho_Norte (CCF + Granger, com reverso); (B) spillover espacial direcional via **SLX em painel 2-way FE** com peso de vizinhos ao sul (placebo = vizinhos ao norte). **RESULTADO DE NÃO-CONFIRMAÇÃO** (importante p/ não superestimar iLUC na redação): o padrão Sul→Norte é **real como reorganização** (shares: agricultura no Sul 92%→71%, pasto/rebanho no Norte 21%→37%/34%), mas **os testes formais não sustentam deslocamento causal**: (1) **sem precedência temporal** — Granger ΔAgric_Sul→ΔPasto_Norte **p=0,97 (nulo)**; co-movimento contemporâneo forte; se algo, precedência é reversa (Norte→Sul p=0,0007); (2) **sem spillover direcional** — agricultura dos vizinhos ao sul → pasto local **β=−0,16 (p=0,02, negativo)**, oposto do θ>0 previsto; placebos nulos; (3) **substituição local forte** (Δagric→Δpasto β=−0,52, p<0,001 = intensificação, confere #22). **Leitura defensável**: co-evolução sob drive comum (boom/crédito) + gradiente de aptidão (lavoura no Sul, fronteira no Norte) — **descrever como "reorganização espacial", não iLUC causal**. Saídas: 3 CSVs (`deslocamento_*`), 3 PNGs (`outputs/deslocamento/`). Doc `pipelines/34_deslocamento_espacial.md`. **Camada 3 ✓ — narrativa Sul→Norte fechada nas 3 camadas (#32/#33/#34).**
- [x] **Pipeline #35 — Robustez de janelas temporais (#32 e #33)** (2026-06-06) — `scripts/robustez_janelas.py`: recalcula as métricas-manchete sob **3 réguas** (atos data-driven, grade regular de 5 anos = 8 blocos exógenos, décadas) + referência contínua/janela-única. Motivado pela discussão metodológica sobre os atos. Decisão: **grade regular exógena**, não blocos aninhados nos atos (atos não são múltiplos de 5 e aninhar re-importaria a fronteira). **Achados robustos**: pasto marcha ao norte (~+2 km/ano) em todos os esquemas; gradiente Sul(pasto→agric)>Norte em **100% das janelas** em todos; Norte(veg→pasto)>Sul em 100/88/75% (atos/5a/décadas, coerente com "relativo não exclusivo" do #33). **Única sensibilidade**: a desaceleração recente da agricultura é nítida nos atos/grade-5 (isolam 2020-24) e diluída nas décadas — confirma que a desaceleração é **pós-2020** e endossa janelas finas. Deslocamento líquido idêntico em todo esquema (depende só dos extremos). Saídas: 2 CSVs (`robustez_*`), 2 PNGs (`outputs/robustez/`). Doc `pipelines/35_robustez_janelas.md`.
- [x] **Pipeline #36 — Robustez do slope à janela móvel** (2026-06-06) — `scripts/robustez_janela_slope.py`: recalcula manchetes de slope do #17 sob 4 larguras (3/5/7/10a) × 2 métodos (trailing, centrada). **Face de resolução** da D12. Desaceleração da vegetação e freada recente da agricultura robustas em todas as janelas; pico da pastagem estável em ~2002-03 na centrada (o "2004" do trailing é viés de atraso); aceleração frágil (só pasto 2004 sobrevive). Saídas: 3 CSVs (`robustez_janela_slope*.csv`), 2 PNGs (`outputs/robustez/`). Doc `pipelines/36_robustez_janela_slope.md`.
- [x] **Pipeline #37 — Caracterizar o "drive comum" (testa a ponta solta do #34)** (2026-06-06) — `scripts/coleta_drivers_macro.py` (#37A) + `scripts/drive_comum.py` (#37B). O #34 fechou a narrativa Sul→Norte num nulo causal e atribuiu o co-movimento a um "drive comum" **inferido, não testado**; o #37 o **materializa e testa**. Coleta drivers macro **exógenos** 1985–2024 (tudo IPEA Data OData4, reprodutível): preços internacionais soja/boi/milho (IMF IFS), **câmbio real efetivo** REER (`GAC12_TCERXTINPC12`, índice INPC-exp, 1980–2024 — contorna a troca de moedas pré-1994), câmbio nominal `BM_ERV`, **crédito rural de GO** `CREATE` (R$ 2010, 1969+ — faz a **ponte** com o SICOR 2013+). Constrói o **"preço recebido"** = preço internacional × câmbio (índice real). Análise UF/anual em 1as diferenças (D7), reusando `ccf_defasada`/`granger` (#34) e `pearson_with_hac` (#21). **Achados**: (a) **exogeneidade confirmada** — em nenhum par a taxa LULC Granger-causa o preço internacional (placebos reversos nulos); (b) **câmbio-competitividade e crédito ANTECEDEM** o LULC — câmbio→pastagem (Granger p=0,046, lag 2) e câmbio→**rebanho Norte** (r=+0,36, p=0,027, lag 1 — a ponte com o Sul→Norte), crédito GO→agricultura (p=0,037, lag 2) e →vegetação (p=0,024, lag 2); (c) **preço de commodity NÃO lidera** (Granger p=0,24–0,81) — transmissão **contemporânea**; (d) **alinhamento com as quebras do #26**: 2001/2020 (pastagem) precedidas por surtos de preço+câmbio (+24%/+64% em 2001; +47%/+51% em 2020), e a **órfã 1991 = colapso de crédito do Plano Collor** (crédito −56%); (e) decomposição **padronizada** NÃO sustenta que um canal domine — na pastagem o **preço** pesa o dobro do câmbio (−0,043 vs −0,022), nenhum significativo (N≈38); o câmbio carrega **precedência** (Granger/ponte), não amplitude. **Leitura**: o drive comum tem **alguma** materialidade — opera por **câmbio** (e crédito como contexto endógeno), com o preço co-movendo sem liderar —, não por empurrão inter-regional. **Começa a fechar** a peça do #34. Atualiza o item 5 de `tese_central_rascunho.md` de "evidência indireta, a completar" para "**parcialmente** testado". Saídas: `drivers_macro_anual.csv` + 4 CSVs `drive_comum_*` + 3 PNGs (`outputs/drive_comum/`). Doc `pipelines/37_drive_comum.md`. **Limite honesto**: precedência preditiva (Granger), não causalidade; crédito é parcialmente endógeno; **multiplicidade não corrigida** (~7 hits em ~135 testes ≈ acaso; nada sobrevive a Bonferroni/FDR — o peso do câmbio vem de reaparecer em duas margens, não do p isolado). O teste com mais poder fica para o #38.
- [x] **Pipeline #38 — O "drive comum" no painel AMC (driver × exposição)** (2026-06-06) — `scripts/drive_comum_amc.py`. Muda a unidade de análise do #37 (UF/anual, N≈38) para o **painel AMC** (166 AMCs × 40 anos ≈ 6.640 obs) e, com isso, a **estratégia de identificação**: como o driver é nacional (mesmo número p/ todas as AMCs num ano), testa-se não "o driver mexe o LULC?" mas **"o choque comum bate mais forte onde a exposição é maior?"** — interação **driver × exposição baseline (1985–89)** em **2-way FE** (γ_t absorve o choque comum, a interação isola o gradiente). z-score em tudo (β comparável); clusterização dupla entidade+ano (fallback entidade em 3/144 células não-PSD). Disciplina de multiplicidade do #37: **conjunto confirmatório teórico** (4 hipóteses × lags 0/1) + **grade exploratória FDR-BH** (4 drivers × 3 exposições × 4 desfechos × **lags 0/1/2** = 144). **Achado (sóbrio)**: o único elemento com standing é a confirmatória **câmbio × fronteira → REBANHO** (β=+0,028, p=0,031, lag 1) — sob depreciação o rebanho cresce mais na fronteira (Norte) e menos no núcleo agrícola (Sul), coerente com #32/#33. **MAS**: (i) é 1 de 8 testes confirmatórios; (ii) a grade completa (com lag 2) **não devolve nenhum** sobrevivente do FDR — o "1 que sobrevivia" na grade de 96 era artefato do tamanho da família (p_fdr 0,042→0,063 ao incluir lag 2); (iii) a "coerência de sinais" na coluna do rebanho é **mecânica** (exposições complementares + `preço recebido` contém o câmbio), não replicação independente; (iv) R²-within ~0,001. A **área** LULC **não** responde diferencialmente (nulo robusto até o lag 2). Saídas: 2 CSVs (`drive_amc_confirmatorio.csv`, `drive_amc_exploratorio.csv`) + 2 PNGs (`outputs/drive_comum_amc/`). Doc `pipelines/38_drive_comum_amc.md`. **Veredito**: gradiente câmbio × aptidão na pecuária de fronteira é **indício sugestivo, NÃO achado estabelecido** — avança (não fecha) a Camada 5. Próximo passo p/ "estabelecer": aptidão edafoclimática como exposição + instrumento p/ o câmbio.

## Em andamento (2026-05-15)

- [x] **Pipeline #28 — Idade da pastagem na conversão para agricultura** (2026-05-15) — Sub-pipelines A (coleta GEE) e B (análise descritiva) concluídos. 78.000 pixels coletados, 241 munis, 1986-2024. Calcula idade da pastagem em Python a partir de bandas `classification_YYYY` amostradas via `stratifiedSample` (não exige asset MapBiomas Pastagem separado). **Achado-chave: período 2018-24 tem distribuição BIMODAL — picos em ~5a e ~35a — assinatura empírica direta da coexistência dos mecanismos premeditado e oportunístico.** Sensibilidade ao corte temporal a verificar (janelas deslizantes). Sul Goiano (37% dos pixels) com mediana 9a domina conversão; Norte/Noroeste mediana 20a. Coorte veg.nat→pastagem→agric (20.5%, n=16.009) mediana 13a com cauda longa; rotação agric→pastagem→agric (12.1%) mediana 5a. Sem correlação com Δ SICOR/Δ VA agro municipais. Outputs: `data/processed/pastagem_idade_conversao.csv`, 6 PNGs em `outputs/idade_pastagem/`, 2 JSONs em `Visualizacao/assets/data/`. **Sub-pipeline C (aba na Visualizacao/) pendente.**

## Em andamento (sequência A→B→C, 2026-05-12)

- [x] **Frente A** — Fix conversao_bruta_*.csv (concluído)
- [x] **Frente B** — `scripts/analise_transicoes.py` (matrizes 6×6 por ATO, decomposição de origem, fluxo bruto vs líquido, 3 JSONs Sankey, top por mesorregião) — concluído; todos os outputs gerados e JSONs integrados na Visualização. **Nota de numeração**: esta maquinaria foi rascunhada como "#25", mas o número **#25 foi reatribuído ao AMC** (`construir_amc_goias.py`); `analise_transicoes.py` não tem número próprio e virou a **base do #33** (Camada 2). Conflito de rótulo resolvido.
- [x] **Frente C** — Refinar primeira aba do `Visualizacao/index.html`:
  - C1: cards diversificados de produção (mini-grid 4 culturas por ATO, explora painel ampliado)
  - ~~C2: toggle de camadas no sticky-map (Cobertura | Δ | Fogo | Transições)~~ ✅ concluído (4 toggles ativos, mapas gerados)
  - C3: pull-quotes nos marcos 1994/1996/2003/2012/2018
  - ~~C4: mini-sankey ao fim de cada ato (consome JSONs da Frente B)~~ ✅ concluído (2026-06-06, containers HTML + JS + CSS integrados)
  - C5: highlight barra empilhada ↔ pixels do mapa
- [ ] **Sub-pipeline #28-C — Aba "Pastagem como reserva de terra" no `Visualizacao/index.html`** (criada 2026-05-15). JSONs prontos em `Visualizacao/assets/data/idade_pastagem_municipal.json` (~41 KB, idade mediana/média/n por município) e `idade_pastagem_histograma.json` (~3 KB, histograma por ATO com bins/counts/mediana). Componentes propostos:
  - **Mapa coroplético municipal** de idade mediana na conversão, com classes em quantis (jovem/médio/antigo) e toggle por ATO.
  - **Histograma interativo** por ATO com slider temporal, **destacando visualmente o achado bimodal no período 2018-24** — picos em ~5a (premeditado) e ~35a (oportunístico). Sensibilidade ao corte temporal a verificar (P#28, seção 2F).
  - **Pull-quote narrativo** com a hipótese e leitura empírica.
  - **Cards de coortes** comparando `veg.nat → pastagem → agric` (n=16.009, mediana 13a) vs rotação `agric → pastagem → agric` (n=9.419, mediana 5a).
  - Padrão alinhado com `timeline.js` / `inventario.js` / `atlas.js`. Conexão com a tese: refina a leitura do Δ Pastagem × Δ SICOR β=−0,003 (Pipeline #22) ao distinguir se SICOR opera sobre pastagem nova ou antiga.

## Frentes técnicas em aberto — opções, sem ordem de prioridade (2026-05-15)

### Eixo A — Análise Trase × LULC (Granger + cross-lagged)

Pipeline #27 deixou 8 colunas Trase no painel sem análise rodada.

- **Pergunta**: "infra exportadora segue ou lidera expansão LULC?"
- **Abordagem**: Granger pairwise em painel + cross-lagged (Y[t] ~ Y[t-1] + X[t-1] e modelo reverso). Padrão dos Pipelines #21-23.
- **Limitação**: janela curta (Trase soja 2004-22, boi 2011-23 sem 2018) — talvez agregar a mesorregião para ganhar poder.
- **Esforço**: 1-2 dias.
- **Valor**: conecta infra agroindustrial à dinâmica LULC; complementa modelo multivariado do Pipeline #22.

### Eixo B — Iniciar redação da dissertação

> **ADIADO POR OPÇÃO** (jun/2026) — a fase atual é EXPLORAÇÃO, não escrita. Esta frente
> fica registrada como opção futura; **não** é prioridade agora e **não** deve ser sugerida
> proativamente. A doc completa em `Textos/` é o que torna a escrita barata quando o momento
> chegar (ver banner no topo e "Fios em aberto").

- **Estado**: zero capítulos. Só metadados, pipelines documentados, decisões metodológicas D1-D9, validação cruzada.
- **Estrutura típica CIAMB**: Introdução → Referencial → Métodos → Resultados → Discussão → Conclusões → Referências.
- **Estratégia**: começar por Métodos (~70% pronto em `Textos/metodologia/`), depois Resultados (consolida narrativa do site em prosa), por último Introdução + Referencial (exigem revisão bibliográfica externa).
- **Esforço**: trabalho contínuo de semanas, não cabe em sprint.
- **Valor**: sem texto não há defesa.

### Eixo C — Painel espacial dinâmico + validação de quebras data-driven

- **C1**: Pipeline #24 hoje é cross-section 2020. Estender com `spreg.Panel_FE_Lag` em todas as janelas. Resolve fragilidade de autocorrelação espacial estrutural não modelada no painel #22. Esforço 2-3 dias.
- **C2**: Validar via literatura as quebras 1991 (Plano Collor?), 1999 (câmbio flutuante?), 2006 (Moratória Soja Amazônia?) detectadas pelo Pipeline #26 sem marco teórico atribuído. Trabalho de leitura + redação curta, não código. Esforço 1-2 dias.

## Eixo prioritário — Narrativa de deslocamento Sul→Norte (2026-06-06)

**Hipótese-mãe**: a pressão da agricultura no Sul Goiano empurra pasto **e** rebanho bovino para o Norte/Noroeste (deslocamento de fronteira / iLUC intra-estadual).

**Decisão de sequência**: a narrativa é entregue em **Sprint 1** com dados/máquina que já existem (baixo risco, vira capítulo de Resultados). A máquina pesada de pixel fica para **Sprint 2**, opcional, escopada *depois* que a Sprint 1 disser quais regiões/transições merecem aprofundamento. **3 das 4 pernas já existem** — #12/#19 (transições), #28 (idade: Sul 9a vs Norte/Noroeste 20a), #16/#25 (painel rebanho); o **centro de massa é a peça que falta e que amarra as outras três**. Pesar a Sprint 2 contra o Eixo B (começar a redação): não iniciá-la antes de a Sprint 1 fechar.

### Sprint 1 — núcleo fácil + defensável (sobre o painel AMC #25, EPSG:5880)

**Camada 1 — Pipeline #32: Centro de massa migratório** *(keystone — ✅ FEITO 2026-06-06; detalhe completo em "Já feito")*
- **Pergunta**: o centro de gravidade do pasto e do rebanho migrou para o norte enquanto o da agricultura ficou ancorado no sul?
- **Abordagem**: centro médio ponderado anual (*mean center*) de `lulc_pastagem_ha`, `pec_bovinos_cab`, `lulc_agricultura_ha`, ponderado pelos centroides das AMCs (`amc_goias.gpkg`); elipse de desvio-padrão por ato; centro mediano (robusto) ao lado do médio. Saída: mapa de trajetória com setas + elipses + tabela de deslocamento N–S (km) por ato.
- **Limitação**: descritivo; centroide sensível ao cluster agrícola do sudoeste (mas é o ponto). AMC evita o artefato de emancipação no rebanho (D11).
- **Esforço**: ~1 dia. **Valor**: a figura-manchete que põe LULC e economia na mesma latitude; ativa #12/#28/#16.
- **Resultado (2026-06-06)**: hipótese **refinada** — a fronteira inteira sobe ao norte (pastagem lidera, +78 km), não só pasto/rebanho. Mas o **gradiente latitudinal** se mantém (agricultura ~1,1° ao sul de pasto/rebanho o tempo todo) e a agricultura **só desacelera no Ato III** (2020-24) enquanto o rebanho segue subindo — esse é o deslocamento limpo, e é recente. 4 figuras + 3 CSVs. **Implicação para as Camadas 2/3**: focar o mecanismo no recorte 2020-24 e no contraste Sudoeste (agricultura travada) × Norte/Noroeste (pasto/rebanho avançando).

**Camada 2 — Mecanismo: transições por mesorregião × ato** *(Pipeline #33 — ✅ FEITO 2026-06-06; detalhe completo em "Já feito")*
- **Pergunta**: o mecanismo é "sul: pasto→agric; norte: veg→pasto"?
- **Abordagem**: re-cortar matrizes 6×6 e fluxo bruto/líquido (#12/#19/`analise_transicoes.py`) por mesorregião × ato; mini-Sankey por região; cruzar com #28 (Sul 9a = pasto-reserva jovem; Norte 20a = fronteira aberta de veg).
- **Esforço**: 1–2 dias (máquina pronta). **Valor**: dá o mecanismo causal-narrativo por trás do centro de massa.
- **Resultado (2026-06-06)**: hipótese confirmada como **gradiente relativo** — `veg→pasto` é a transição-mãe pervasiva; `pasto→agric` só lidera no **Sul+Centro × Ato II**. O **deslocamento** aparece no balanço líquido (Ato II: Sul −0,57 Mha de pasto, Norte/Noroeste +0,13/+0,09). No **Ato III** o `pasto→agric` do Sul despenca (−88%, agricultura desacelera) e o `veg→pasto` do Norte persiste — fecha a cadeia com o #32. Idade #28: Sul 9a → Norte 20a. Doc: `pipelines/33_transicoes_regionais.md`.

**Camada 3 — Conversa econômica: lead-lag + spillover espacial** *(Pipeline #34 — ✅ FEITO 2026-06-06; detalhe em "Já feito")*
- **Resultado (2026-06-06)**: **NÃO-CONFIRMAÇÃO** do deslocamento causal. Sem precedência temporal (Granger p=0,97) e sem spillover espacial direcional (θ=−0,16, oposto do previsto). O padrão Sul→Norte é reorganização sob drive comum + gradiente de aptidão, não iLUC causal. Tempo contínuo (não atos). **Redigir como "reorganização espacial", não deslocamento causal.**
- **Pergunta**: a expansão da agricultura no sul *antecede* o avanço de pasto/rebanho no norte? Há spillover dos vizinhos?
- **Abordagem**: (a) shares regionais no tempo; (b) lead-lag/distributed-lag no painel AMC (padrão #21–23: Δagric_sul → Δrebanho_norte defasado); (c) regressão espacial (#24/`spreg`): *spatial lag* da agricultura dos vizinhos sobre pasto/rebanho local = teste formal de deslocamento.
- **Limitação**: não promete causalidade dura — descritivo + defasagem + spillover.
- **Esforço**: 2–3 dias. **Valor**: fecha o "fazer os pixels conversarem com a economia"; reusa #22/#24.

### Sprint 2 — Pipeline #33 (proposto): trajetórias e sobrevivência de pixel *(opcional, escopar após Sprint 1)*

Generaliza o motor do #28 (amostragem + stack 40 bandas + run-length local) de UMA transição (pasto→agric) para TODOS os estados.
- **Produtos**: (a) trajetórias multi-passo encadeadas (*sequence analysis*/optimal matching) → tipologia de "carreiras" da terra; (b) sobrevivência generalizada (Kaplan-Meier por estado × ato × região, tratando censura); (c) **mapa de churn** (nº de transições por pixel, censo em *tiles*) = instabilidade/fronteira; (d) Sankey de 3+ camadas ligado por trajetória; testa *path dependence* (passar por pasto predispõe à agricultura?).
- **Decisões a logar**: D-flicker (duração mínima / moda temporal); D-censura (esquerda = estoque pré-1985 inmensurável; direita = KM); validar idade contra produto MapBiomas Pastagem/LAPIG e avaliar adotar a camada de **vigor/degradação** (não replicável via coverage).
- **Amostra vs censo**: prototipar na amostra (distribuições/sobrevivência); rodar o mesmo kernel no censo em tiles só para os mapas (~2–4 GB em disco, processamento de laptop). Limite honesto: anual, 30 m, erro de classificação — captura o que o dado enxerga.
- **Esforço**: 1–2 semanas. **Risco**: médio (flicker/censura afetam resultados). **Valor**: a história rica dos pixels; pesar contra o Eixo B.

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