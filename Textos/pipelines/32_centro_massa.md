# Pipeline #32 — Centro de massa migratório das AMCs de Goiás

**Script**: `scripts/centro_massa.py`
**Quando foi feito**: 2026-06-06. Camada 1 (*keystone*) da narrativa de deslocamento Sul→Norte.
**Depende de**: Pipeline #25 (`painel_amc_goias.parquet` e `amc_goias.gpkg`).
**Outputs**:
- `data/processed/centro_massa_anual.csv` — variável × ano: centro médio e mediano (em metros EPSG:5880 e em graus).
- `data/processed/centro_massa_elipses.csv` — variável × ato: parâmetros da elipse de desvio-padrão.
- `data/processed/centro_massa_deslocamento.csv` — variável × ato: deslocamento N–S e L–O (km), distância total e azimute.
- `data/processed/centro_massa_bootstrap.csv` — variável × janela (LÍQUIDO + atos): ΔNorte pontual + **IC95%** (`dN_lo`/`dN_hi`) e flag `exclui_zero`, por bootstrap de AMCs.
- `data/processed/centro_massa_robustez_deriva.csv` — régua × ano: latitude do centroide agrícola sob 3 réguas de destino + IC95%, para a robustez à mudança de rótulo do Mosaico (#28D).
- `data/processed/centro_massa_robustez_deriva_desloc.csv` — régua × janela: ΔNorte + IC95% das 3 réguas.
- `outputs/centro_massa/robustez_deriva_regua.png` — latitude × ano das 3 réguas + pastagem de referência.
- `outputs/centro_massa/overview_posicoes.png` — mapa estadual, posição 1985 vs. 2024.
- `outputs/centro_massa/trajetorias.png` — zoom pequeno-múltiplo na trajetória anual.
- `outputs/centro_massa/elipses_por_ato.png` — elipses de dispersão por ato.
- `outputs/centro_massa/deslocamento_latitude.png` — latitude do centro × ano.

---

## Pergunta de pesquisa

> O centro de gravidade do **pasto** e do **rebanho bovino** migrou para o norte enquanto o da **agricultura** ficou ancorado no sul?

É a **figura-manchete** da narrativa de deslocamento de fronteira Sul→Norte (efeito indireto de uso da terra, *iLUC*, dentro do próprio estado). Ela coloca, num mesmo arcabouço geográfico, dois mundos que normalmente são analisados em separado: o **físico** (pixels de uso da terra do MapBiomas) e o **econômico** (rebanho bovino da PPM/SIDRA).

---

## A intuição: o que é um "centro de massa" de uso da terra?

Imagine Goiás como uma **bandeja plana**. Em cada Área Mínima Comparável (AMC — ver #25) você empilha fichas em quantidade proporcional ao que aquela região tem da variável de interesse — por exemplo, hectares de pastagem. Onde a bandeja **se equilibraria sobre a ponta de um dedo**? Esse ponto de equilíbrio é o **centro de massa** (ou centro médio ponderado).

A ideia-chave: se a pastagem cresce no **norte** e encolhe no **sul**, o ponto de equilíbrio **desliza para o norte**. Calculando esse ponto **ano a ano**, obtemos uma **trajetória** — um fio que mostra para onde a "massa" de cada uso da terra está se mudando ao longo de 40 anos.

Isso transforma uma pergunta difícil ("onde está concentrada a pastagem, e essa concentração está se movendo?") em **um único ponto por ano**, que cabe num mapa e numa tabela. Fazemos isso para quatro variáveis — **agricultura, pastagem, rebanho bovino e vegetação natural** — e comparamos suas trajetórias.

> [!NOTE]
> **Por que sobre AMCs e não sobre municípios?** Se usássemos os 246 municípios atuais, o desmembramento de um município (emancipação) criaria um **salto espúrio** no centro de massa — um artefato territorial, não um fenômeno real (Decisão D11). As 166 AMCs têm território **constante** de 1985 a 2024, então cada movimento do centroide é movimento de verdade. Ver [25_amc_goias.md](25_amc_goias.md).

---

## Como é calculado

Para cada variável e cada ano de 1985 a 2024, usamos os **centroides das AMCs** ($x_i, y_i$) em projeção métrica (EPSG:5880 Albers, que preserva área) e o **valor da variável** naquela AMC ($w_i$) como peso.

### 1. Centro médio ponderado (*mean center*) — o ponto de equilíbrio
$$\bar{x} = \frac{\sum_i w_i \, x_i}{\sum_i w_i}, \qquad \bar{y} = \frac{\sum_i w_i \, y_i}{\sum_i w_i}$$

É a média das posições, pesada pela quantidade. **Intuição**: a "ficha" de cada AMC puxa o ponto de equilíbrio na sua direção, com força proporcional ao seu peso. Um grande aglomerado (o Sudoeste agrícola, por exemplo) puxa bastante.

### 2. Centro mediano ponderado (*median center*) — o ponto mais central
O ponto $m$ que **minimiza a soma das distâncias ponderadas** a todas as AMCs (centro de mínima distância), resolvido pelo algoritmo iterativo de **Weiszfeld (1937)**:
$$\min_{m} \; \sum_i w_i \, \lVert m - p_i \rVert_2$$

**Intuição**: é o ponto que deixa todo mundo "o mais perto possível". Como usa a distância (e não o quadrado dela), é **robusto** — um único aglomerado pesado o desloca menos que ao centro médio. **Por que reportamos os dois:** se o médio e o mediano contam a *mesma* história, o movimento não é um artefato do peso do cluster do Sudoeste — é um deslocamento genuíno da distribuição.

### 3. Elipse de desvio-padrão (*Standard Deviational Ellipse*, SDE) — a "sombra" da massa
Enquanto o centro diz **onde** está a massa, a elipse (Yuill 1971) diz **quão espalhada** e **em que orientação** ela está. É a pegada de 1 desvio-padrão (1σ) calculada por ato. O ângulo do eixo principal:
$$\theta = \tfrac{1}{2}\,\operatorname{arctan2}\!\left(2\textstyle\sum_i w_i\,dx_i\,dy_i,\; \sum_i w_i\,(dx_i^2 - dy_i^2)\right)$$
com semi-eixos = desvios-padrão ponderados das coordenadas rotacionadas. **Intuição**: uma elipse comprida e fina = massa esticada numa direção; uma elipse mais redonda = massa espalhada por igual.

> [!NOTE]
> **Os "atos" são períodos *data-driven*, não políticos.** Atos I (1985–2000), II (2001–2019) e III (2020–2024) vêm da **triangulação de quebras estruturais** do Pipeline #29 (sup-F multivariado + STARS + KL/TV), centralizada em `config_periodos.py`. Eles descrevem a *dinâmica empírica do uso da terra*, não mandatos de governo.

---

## Resultados

### Deslocamento líquido do centro médio, 1985 → 2024

| Variável | Δ Norte (km) | Δ Leste (km) | Distância total (km) | Azimute |
| :--- | :---: | :---: | :---: | :---: |
| **Pastagem** | **+77,6** | +19,1 | 80,0 | 14° (quase N) |
| **Rebanho bovino** | **+66,9** | +22,6 | 70,6 | 19° (quase N) |
| **Agricultura** | **+65,2** | +49,5 | 81,9 | 37° (NE) |
| **Vegetação natural** | +7,6 | +7,4 | 10,6 | 45° (quase parada) |

*(Azimute: 0° = Norte, 90° = Leste. Decomposição por ato em `centro_massa_deslocamento.csv`.)*

### Achados consolidados

1. **Marcha generalizada ao norte (refina e em parte contraria a hipótese).** A hipótese literal era "agricultura estática × pasto/rebanho subindo". Na verdade, **toda a fronteira agropecuária subiu de latitude** ao longo dos 40 anos — a pastagem liderou (+77,6 km), seguida de rebanho (+66,9 km) e da própria agricultura (+65,2 km). A vegetação natural ficou praticamente **ancorada no norte** (+7,6 km), funcionando como a barreira ecológica contra a qual a fronteira pressiona.

2. **Gradiente latitudinal persistente.** Mesmo todos subindo, a **distância relativa entre eles quase não muda**: o centro da agricultura fica sistematicamente **1,1° a 1,2° (≈120–130 km) ao sul** do de pastagem/rebanho em *todos* os anos. Desenha-se um modelo de cinturões ordenados de sul para norte: **agricultura → pastagem/pecuária → vegetação natural**.

3. **Desaceleração agrícola recente (Ato III) — o sinal mais limpo.** No **Ato III (2020–2024)**, o centro da agricultura **desacelera** (apenas +0,2 km ao norte), enquanto pastagem (+11,0 km) e rebanho (+8,1 km) **seguem subindo**. É a assinatura mais nítida de deslocamento de fronteira *recente*: a agricultura se assentou nas áreas consolidadas do Sul/Sudoeste e a pecuária continua sendo empurrada para o Norte/Noroeste. *(Nota: +0,2 km ainda é crescimento, não estagnação absoluta; "desaceleração" é o termo honesto, não "congelamento".)* **É o recorte que as Camadas 2 e 3 devem investigar.**

4. **Vetores de expansão distintos.** A agricultura avança a **nordeste** (azimute líquido 37°; forte componente leste), enquanto pasto e rebanho sobem quase **a prumo** ao norte (14° e 19°). Ou seja: não é só *quanto* cada um anda, mas em *que direção*.

5. **A pegada (SDE) da agricultura se EXPANDIU — não se contraiu.** Ao longo dos atos, a elipse da agricultura **cresceu nos dois eixos** (eixo maior 160 → 183 km; eixo menor 78 → 107 km), ficou **menos alongada** (razão 2,05 → 1,72) e **girou para NE** (θ 19° → 31°). As elipses de pastagem, rebanho e vegetação ficaram **estáveis** (variação de poucos km). Leitura: a área agrícola **se espalhou e mudou de orientação** à medida que avançou para o Entorno do DF e o Nordeste goiano — **não há sinal de consolidação/encolhimento** da pegada espacial.

> [!WARNING]
> Análises geradas por terceiros afirmaram "contração e alongamento das elipses à medida que as fronteiras se consolidam". Isso **contradiz os dados** (`centro_massa_elipses.csv`): a pegada da agricultura **expandiu** e ficou **mais redonda**. Use o achado 5 acima.

---

## Incerteza: o deslocamento sobrevive ao acaso amostral? (bootstrap)

Um centro médio é uma estatística **pontual** — sem barra de erro não dá para saber se um deslocamento pequeno é real ou ruído. Por isso o pipeline faz um **bootstrap de AMCs**: reamostra as 166 AMCs **com reposição** (B = 2000 vezes), recomputa o centro médio a cada vez, e reporta o **IC95% percentílico** do ΔNorte 1985→2024. Isso testa a robustez à **composição das unidades espaciais** (e se materializa como a **faixa sombreada** na figura de latitude).

| Variável | ΔNorte | IC95% (km) | Veredito |
| :--- | :---: | :---: | :--- |
| **Pastagem** | +77,6 km | **[+54,7, +98,2]** | deslocamento robusto |
| **Rebanho bovino** | +66,9 km | **[+47,2, +84,5]** | deslocamento robusto |
| **Agricultura** | +65,2 km | **[+43,5, +94,6]** | deslocamento robusto |
| **Vegetação natural** | +7,6 km | **[−0,5, +15,6]** | **inclui zero — dentro do ruído** |

**Leitura honesta**: as três manchetes (pasto, rebanho, agricultura marcham ao norte) são **estatisticamente sólidas** — o IC está longe de zero. Mas o "+7,6 km" da vegetação **não é distinguível de "não se moveu"** (o IC contém zero). Isso **reforça** — não enfraquece — a leitura de que a vegetação está **ancorada**; apenas significa que o número +7,6 km **não deve ser lido como deslocamento**, e que qualquer movimento pequeno em nível de ato (ex.: a agricultura no Ato III, +0,2 km) está seguramente dentro do ruído e nunca deve ser interpretado como valor. **Decisão D19** (ver abaixo).

> [!NOTE]
> O bootstrap incide sobre o centro **médio**. O centro **mediano** (Weiszfeld) continua reportado ao lado como robustez a um eixo *diferente* — o peso do cluster, não a amostra de unidades. As duas robustezas são complementares.

---

## Robustez à mudança de rótulo do Mosaico (#28D): a régua-espelho do destino agrícola

**A ameaça.** A [#28D](28D_deriva_mosaico.md) (Decisão D25) mostrou que, no fim da
série MapBiomas, a conversão `pasto→agricultura` migra para a classe **"Mosaico de
Usos" (21)**. O centroide da agricultura pondera pelo **estoque**
`lulc_agricultura_ha`, que subconta a soja recém-convertida — logo o congelamento
da agricultura no Ato III (+0,2 km, acima) pode ser **artefato de rótulo, não de
campo**. Como confiar na figura se o destino da conversão mudou de nome?

**O teste.** Recomputa-se o centroide agrícola sob **três réguas de destino**, com
IC95% por bootstrap (D19). Se a conclusão sobrevive nas três, é robusta à convenção
de classe; onde só sobrevive numa, fica delimitado o que depende do rótulo.

| Régua de destino | O que é | Vulnerabilidade à mudança de rótulo |
|---|---|---|
| **Agricultura** (MapBiomas) | a régua da manchete | **exposta** (o rótulo que esvazia) |
| **Agricultura ∪ Mosaico** | reivindica a massa escondida | teto do viés (reabsorve tudo) |
| **Soja plantada (SIDRA)** | dado de campo do IBGE | **imune** (não passa pelo classificador) |

**Resultado 1 — o gradiente é robusto nas três réguas.** A agricultura fica ao
**sul** da pastagem em toda régua e todo ano: o vão agricultura↔pastagem em 2024 é
−135 km (MapBiomas), −111 km (∪ Mosaico) e −122 km (soja SIDRA). **A manchete —
agricultura ancorada ao sul da fronteira que marcha — não depende da convenção de
Mosaico.**

**Resultado 2 — o "congelamento no Ato III" é, em parte, artefato de rótulo.**
ΔNorte no Ato III (2020→2024), com IC95%:

| Régua | ΔNorte Ato III | IC95% | Veredito D19 |
|---|---|---|---|
| Agricultura (MapBiomas) | **+0,2 km** | [−0,5, +1,1] | inclui 0 — *congelada* |
| Agricultura ∪ Mosaico | **+4,1 km** | [+1,0, +6,9] | **≠0 — sobe** |
| Soja plantada (SIDRA) | **+8,2 km** | [−0,5, +16,1] | inclui 0 — *sugestivo* |

Ao reivindicar o Mosaico, aparece um deslocamento ao norte **estatisticamente
sólido** (+4,1 km, IC exclui zero) exatamente onde a régua crua mostra
congelamento. A soja SIDRA aponta na **mesma direção** e com magnitude maior
(+8,2 km), mas sobre uma janela de só 4 anos o IC **inclui zero** — é
**corroborante, não estabelecido**. Leitura honesta: a agricultura de fato
continuou subindo no Ato III (a mudança de rótulo escondia ~4–8 km desse movimento), mas só a
régua ∪ Mosaico crava o número com IC limpo; **a frase "a agricultura parou depois
de 2020" deve ser abandonada — é assinatura do classificador, não do campo.**

**O que a mudança de rótulo NÃO toca.** A perna que *sobe* da narrativa (pastagem e rebanho)
é imune: o rebanho é SIDRA e o estoque de pastagem quase não é drenado. A mudança de rótulo
morde só a **perna da agricultura**, e só a sua **trajetória recente** — não o
gradiente, que é o coração da manchete. Ver a análise-companheira
`centro_massa_deriva_check.py` (§5.4 do #28D) para a triangulação do viés
(+10 km pontual em 2019→24) e o centroide da massa escondida (+46,5 km ao norte da
agricultura visível).

![Robustez à mudança de rótulo do Mosaico](../../outputs/centro_massa/robustez_deriva_regua.png)

---

## Como ler as figuras

### A. `overview_posicoes.png` — o panorama (1985 vs. 2024)
Cada variável aparece com a posição do centro de massa em **1985 (círculo vazado)** e **2024 (círculo cheio)**, ligadas por uma seta, sobre a malha das AMCs. É a imagem que resume tudo: a agricultura (magenta) lá embaixo no sul, pasto (laranja) e rebanho (vinho) no centro, vegetação (verde) ao norte — e todas as setas apontando para cima.

![Posições 1985 vs 2024](../../outputs/centro_massa/overview_posicoes.png)

### B. `deslocamento_latitude.png` — a narrativa N–S em uma linha
Latitude do centro de massa **ano a ano**. As bandas de fundo marcam os três atos. É aqui que se enxerga, de relance, o **gradiente estável** (as linhas nunca se cruzam: agricultura sempre embaixo) e a **desaceleração do Ato III** (a linha magenta achata enquanto laranja e vinho seguem subindo). Linha cheia = centro médio; tracejada = mediano (robusto); **faixa sombreada = IC95% do centro médio por bootstrap de AMCs** (a incerteza da posição a cada ano). Onde as faixas de duas variáveis não se sobrepõem, a diferença de latitude entre elas é robusta.

![Latitude no tempo](../../outputs/centro_massa/deslocamento_latitude.png)

### C. `trajetorias.png` — o caminho de cada uma, com zoom
Um painel por variável, com **zoom apertado** na trajetória (que tem ~80 km, minúscula perante os ~700 km do estado). Mostra as **setas por ato** e os rótulos de ano. O traçado **mediano (tracejado)** ao lado do **médio (sólido)** revela onde o cluster do Sudoeste "puxa" o médio para longe do ponto robusto.

![Trajetórias com zoom](../../outputs/centro_massa/trajetorias.png)

### D. `elipses_por_ato.png` — a dispersão e a orientação
Um painel por ato, com a elipse 1σ de cada variável em escala estadual. Vê-se a pegada **sulina e a NE** da agricultura, a pegada **ampla e central** de pasto/rebanho, e a **setentrional** da vegetação — e como a elipse da agricultura se abre e gira para NE de Ato I a III (achado 5).

![Elipses por ato](../../outputs/centro_massa/elipses_por_ato.png)

---

## Método é padrão acadêmico?

Sim. "Centro de massa / centro de gravidade ponderado" de uma distribuição ao longo do tempo é técnica estabelecida de estatística espacial: é exatamente o que o **US Census Bureau** publica como *mean center of population* (média das coordenadas ponderada pela população) e o que o toolset *Measuring Geographic Distributions* do **ArcGIS** implementa (mean center + median center + standard deviational ellipse). O trio usado aqui é esse. A implementação foi **auditada e reproduzida de forma independente** (reimplementação do zero a partir do parquet cru bate os ΔNorte ao decimal), e as manchetes passam no bootstrap. As checagens de corretude confirmadas: cálculo em projeção *equal-area* (`.to_crs(5880)` **antes** do `.centroid`), média ponderada `Σwx/Σw`, Weiszfeld com guard da singularidade, e ângulo da elipse = ângulo do eixo principal da matriz de 2º momento (com `max/min` dos semi-eixos, evitando trocar maior por menor).

## Decisões metodológicas

- **Unidade = AMC (D11).** Território constante 1985–2024 (166 AMCs, Ehrl 2017) elimina o viés de emancipação que criaria saltos espúrios no centroide. Ver [25_amc_goias.md](25_amc_goias.md).
- **CRS = EPSG:5880** (SIRGAS 2000 / Albers Brasil, *equal-area*). Centroides e distâncias são calculados em metros nessa projeção; para os rótulos de latitude/longitude, os pontos são reprojetados de volta para EPSG:4674.
- **Vegetação natural** = floresta nativa + formação savânica + campo nativo (mesma composição de `pct_natural_lulc` no #16/#25).
- **Pesos NaN/≤0 descartados** por variável-ano (uma AMC sem o dado simplesmente não entra naquele ano).
- **D19 — quantificação de incerteza por bootstrap.** Todo deslocamento de centroide deve vir com **IC95% por bootstrap de AMCs** (resample com reposição, B=2000); um ΔNorte cujo IC **inclui zero** (vegetação; movimentos de ato pequenos) **não** pode ser reportado como número, só como "≈ ancorado / dentro do ruído". O bootstrap incide sobre o centro médio; o mediano segue como robustez ao cluster. Generaliza para o #44 e #50.

---

## Limitações (e como cada uma é mitigada ou declarada)

- **É descritivo, não causal.** O centro de massa mostra *que* a distribuição se moveu, não *por que* nem *quem converteu quem*. Um único ponto-centro é uma redução drástica: distribuições diferentes podem ter o mesmo centro, e "o centro subiu" **não prova** "a fronteira foi empurrada". Por isso a leitura causal foi deliberadamente **recuada** para "reorganização" (Camadas 2/3, #33/#34), e não se afirma iLUC a partir do centroide.
- **Aproximação do centroide-de-polígono.** Todo o valor de uma AMC é colocado no seu centroide **geométrico** — assume distribuição uniforme intra-AMC. Para as variáveis **com raster** (pasto, agricultura, vegetação) isso foi **testado** (#43, pixel-a-pixel: difere ~1–2 km). Para as variáveis **tabulares (rebanho, e no #50 crédito/VA)** é uma **aproximação não verificada por pixel** — declarada como tal; a ponte de credibilidade é a validação soja raster×SIDRA do #44 (concordam a ~7 km).
- **Convenção da elipse (SDE).** Os semi-eixos são "1 desvio-padrão ponderado" dividindo por Σw, **sem o fator √2** que algumas implementações (ArcGIS/CrimeStat) adotam. Orientação e **comparação relativa** entre atos não mudam; só o **km absoluto** do eixo segue esta convenção — não compare o km absoluto com uma elipse gerada em outro software. A elipse é usada só descritivamente.
- **Suporte variável.** Descartar AMCs com peso ≤0 faz o centroide mover-se quando o *suporte encolhe*, não só quando a massa migra — real para o campo nativo (#44; nº de AMCs cai 158→142), irrelevante para pasto/agricultura (presentes em toda parte).
- **Albers preserva área, não distância.** Para o deslocamento N–S de dezenas a centenas de km dentro de GO, o erro de escala é pequeno e aceitável para leitura descritiva — mas as distâncias em km não são geodésicas exatas.
- **Sensibilidade ao cluster.** O centro **médio** é puxado pela concentração de peso (Sudoeste para agricultura; Vale do Araguaia para pecuária). Isso é exatamente o fenômeno que se quer descrever — e por isso o centro **mediano** é reportado ao lado, como contraprova de robustez.
- **Azimutes e ΔN de movimentos minúsculos são ruído.** Ex.: agricultura no Ato III anda só 0,6 km — seu azimute (292°) não tem significado direcional, e seu ΔN está dentro do IC do bootstrap; o que importa é que ela **parou**.

---

## Conexão com a narrativa e próximos passos

O #32 entrega a **Camada 1** (o panorama). O achado afina o foco das próximas:

1. **Camada 2 — Mecanismo** (transições por mesorregião × ato, #12/#19/#28): testar se o **Sul converte pasto jovem** (reserva de curto prazo — #28 mostra mediana de 9 anos, não-cens.) enquanto o **Norte/Noroeste suprime vegetação ou converte pasto antigo** (mediana de 16 anos, não-cens.). Focar o recorte **2020–2024**, onde o deslocamento é mais limpo.
2. **Camada 3 — Econômica** (lead-lag + spillover espacial no painel AMC, #22/#24): testar se $\Delta\text{agricultura}_{t-1,\,\text{sul}} \rightarrow \Delta\text{rebanho}_{t,\,\text{norte}}$ — a agricultura no sul **antecede** o avanço da pecuária no norte? Há spillover dos vizinhos?

---

## Visualização interativa (Movimento III do site)

Além das quatro figuras estáticas (`outputs/centro_massa/*.png`, servidas no scrollytelling da "marcha ao norte"), o #32 ganhou uma **peça interativa** — o bloco-herói do Movimento III em `Visualizacao/index.html`. Ela anima os quatro centros de massa **caminhando ano a ano** de 1985 a 2024.

**Arquivos**
- `scripts/exportar_marcha_viz.py` — reempacota `data/processed/centro_massa_*.csv` (anual, deslocamento, bootstrap, elipses) num único `Visualizacao/assets/data/marcha_centro_massa.json` (~64 KB). **Não recomputa nada** (sem GEE, sem parquet): é reprodutível a partir dos CSVs versionados. As elipses SDE são amostradas na fronteira em **coordenadas métricas** (EPSG:5880, onde `theta` e os semi-eixos foram calculados) e reprojetadas para lon/lat via geopandas — assim o d3 as desenha na mesma projeção do mapa **sem misturar referenciais de ângulo**.
- `Visualizacao/assets/js/marcha-mapa.js` — o componente (vanilla + d3 v7 já vendorizado; namespace `GO40.marchaMapa`). *Progressive enhancement*: sem JS/d3 o bloco fica `hidden` e o scrollytelling de PNGs assume.
- `Visualizacao/assets/css/marchamap.css` — estilos.

**O que a peça mostra** (dois painéis sincronizados):
- **Mapa animado** — a malha das AMCs ao fundo; os quatro centros com **rastro** que cresce, ponto de partida (1985, vazado) e cabeça (ano corrente); **play/pausa + slider**; toggle da **elipse 1σ do ato**. *Honestidade de escala*: a marcha líquida é ~80 km num estado de ~700 km, então o mapa **dá zoom na nuvem de trajetórias** e compensa com (a) um **localizador** do recorte sobre Goiás inteiro e (b) uma **barra de escala** em km — o leitor nunca confunde o zoom com a escala real.
- **Faixa latitude-tempo** — a versão viva de `deslocamento_latitude.png`: latitude de cada centro ano a ano, bandas dos três atos, e uma **linha-scan** que varre o tempo junto com a animação. É onde o **gradiente persistente** (~1,2°) e a **desaceleração do Ato III** se leem de relance. Arrastar a faixa faz *scrub* do ano (controla os dois painéis).

**Por que d3, e não Mapbox/MapLibre.** A peça é 100% self-contained (roda no GitHub Pages, tudo vendorizado, offline-reprodutível) e são só 4 trajetórias de 40 pontos — d3 sobra. Mapbox foi **descartado**: exige *access token* e chamadas aos servidores da Mapbox (*map loads* cobrados), o que amarraria a dissertação a um serviço pago e quebraria o modelo offline; e, com deslocamento tão pequeno, um basemap de satélite bonito **ofuscaria um sinal pequeno-porém-robusto**.

> **Possibilidade documentada — MapLibre GL JS.** Se algum dia se quiser um **mapa-base real** (satélite/terreno para *grounding* geográfico, câmera 3D/`flyTo`, ou trilhas animadas via deck.gl `TripsLayer`), o caminho correto é o **MapLibre GL JS** — o fork *open-source* do Mapbox GL JS, **sem token e sem cobrança**, que pode inclusive auto-hospedar/embutir um raster estático de satélite de Goiás. Ele entrega a mesma renderização WebGL, vetor-tiles e 3D sem prender a viz a um provedor pago. **Não Mapbox** (token + *map loads* cobrados). Mesmo assim, vale o alerta de "mapa-vaidade": em escala estadual, imagem de satélite tende a afogar uma marcha de ~80 km — por isso o padrão fica em d3, e o MapLibre é *opt-in* só se o objetivo passar a ser contexto geográfico, não a métrica do deslocamento.
