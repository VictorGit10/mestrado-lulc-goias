# Pipeline #32 — Centro de massa migratório das AMCs de Goiás

**Script**: `scripts/centro_massa.py`
**Quando foi feito**: 2026-06-06. Camada 1 (*keystone*) da narrativa de deslocamento Sul→Norte.
**Depende de**: Pipeline #25 (`painel_amc_goias.parquet` e `amc_goias.gpkg`).
**Outputs**:
- `data/processed/centro_massa_anual.csv` — variável × ano: centro médio e mediano (em metros EPSG:5880 e em graus).
- `data/processed/centro_massa_elipses.csv` — variável × ato: parâmetros da elipse de desvio-padrão.
- `data/processed/centro_massa_deslocamento.csv` — variável × ato: deslocamento N–S e L–O (km), distância total e azimute.
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

## Como ler as figuras

### A. `overview_posicoes.png` — o panorama (1985 vs. 2024)
Cada variável aparece com a posição do centro de massa em **1985 (círculo vazado)** e **2024 (círculo cheio)**, ligadas por uma seta, sobre a malha das AMCs. É a imagem que resume tudo: a agricultura (magenta) lá embaixo no sul, pasto (laranja) e rebanho (vinho) no centro, vegetação (verde) ao norte — e todas as setas apontando para cima.

![Posições 1985 vs 2024](../../outputs/centro_massa/overview_posicoes.png)

### B. `deslocamento_latitude.png` — a narrativa N–S em uma linha
Latitude do centro de massa **ano a ano**. As bandas de fundo marcam os três atos. É aqui que se enxerga, de relance, o **gradiente estável** (as linhas nunca se cruzam: agricultura sempre embaixo) e a **desaceleração do Ato III** (a linha magenta achata enquanto laranja e vinho seguem subindo). Linha cheia = centro médio; tracejada = mediano (robusto).

![Latitude no tempo](../../outputs/centro_massa/deslocamento_latitude.png)

### C. `trajetorias.png` — o caminho de cada uma, com zoom
Um painel por variável, com **zoom apertado** na trajetória (que tem ~80 km, minúscula perante os ~700 km do estado). Mostra as **setas por ato** e os rótulos de ano. O traçado **mediano (tracejado)** ao lado do **médio (sólido)** revela onde o cluster do Sudoeste "puxa" o médio para longe do ponto robusto.

![Trajetórias com zoom](../../outputs/centro_massa/trajetorias.png)

### D. `elipses_por_ato.png` — a dispersão e a orientação
Um painel por ato, com a elipse 1σ de cada variável em escala estadual. Vê-se a pegada **sulina e a NE** da agricultura, a pegada **ampla e central** de pasto/rebanho, e a **setentrional** da vegetação — e como a elipse da agricultura se abre e gira para NE de Ato I a III (achado 5).

![Elipses por ato](../../outputs/centro_massa/elipses_por_ato.png)

---

## Decisões metodológicas

- **Unidade = AMC (D11).** Território constante 1985–2024 (166 AMCs, Ehrl 2017) elimina o viés de emancipação que criaria saltos espúrios no centroide. Ver [25_amc_goias.md](25_amc_goias.md).
- **CRS = EPSG:5880** (SIRGAS 2000 / Albers Brasil, *equal-area*). Centroides e distâncias são calculados em metros nessa projeção; para os rótulos de latitude/longitude, os pontos são reprojetados de volta para EPSG:4674.
- **Vegetação natural** = floresta nativa + formação savânica + campo nativo (mesma composição de `pct_natural_lulc` no #16/#25).
- **Pesos NaN/≤0 descartados** por variável-ano (uma AMC sem o dado simplesmente não entra naquele ano).

---

## Limitações

- **É descritivo, não causal.** O centro de massa mostra *que* a distribuição se moveu, não *por que* nem *quem converteu quem*. O mecanismo local (Camada 2) e a defasagem econômica/spillover (Camada 3) exigem as próximas análises.
- **Albers preserva área, não distância.** Para o deslocamento N–S de dezenas a centenas de km dentro de GO, o erro de escala é pequeno e aceitável para leitura descritiva — mas as distâncias em km não são geodésicas exatas.
- **Sensibilidade ao cluster.** O centro **médio** é puxado pela concentração de peso (Sudoeste para agricultura; Vale do Araguaia para pecuária). Isso é exatamente o fenômeno que se quer descrever — e por isso o centro **mediano** é reportado ao lado, como contraprova de robustez.
- **Azimutes de movimentos minúsculos são ruído.** Ex.: agricultura no Ato III anda só 0,6 km — seu azimute (292°) não tem significado direcional; o que importa é que ela **parou**.

---

## Conexão com a narrativa e próximos passos

O #32 entrega a **Camada 1** (o panorama). O achado afina o foco das próximas:

1. **Camada 2 — Mecanismo** (transições por mesorregião × ato, #12/#19/#28): testar se o **Sul converte pasto jovem** (reserva de curto prazo — #28 mostra mediana de 9 anos) enquanto o **Norte/Noroeste suprime vegetação ou converte pasto antigo** (mediana de 20 anos). Focar o recorte **2020–2024**, onde o deslocamento é mais limpo.
2. **Camada 3 — Econômica** (lead-lag + spillover espacial no painel AMC, #22/#24): testar se $\Delta\text{agricultura}_{t-1,\,\text{sul}} \rightarrow \Delta\text{rebanho}_{t,\,\text{norte}}$ — a agricultura no sul **antecede** o avanço da pecuária no norte? Há spillover dos vizinhos?
