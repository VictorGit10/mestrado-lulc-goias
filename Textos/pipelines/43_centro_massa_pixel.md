# Pipeline #43 — Centro de massa pixel-ponderado (robustez MAUP do #32)

**Script**: `scripts/centro_massa_pixel.py`
**Quando foi feito**: 2026-07-07.
**Depende de**: #32 (`centro_massa_anual.csv`, só para a figura de comparação). Usa o asset MapBiomas Coleção 10.1 direto via GEE — **não** depende do painel AMC (#25).
**Outputs**:
- `data/processed/centro_massa_pixel_anual.csv` — lon/lat/n_pixels do centro de massa por (variável, ano).
- `outputs/centro_massa/comparacao_pixel_amc.png` — latitude × ano, AMC (#32) vs pixel (#43) sobrepostos.
- `data/cache/centro_massa_pixel/{ano}.json` — cache por ano (reduceRegion é caro; script é resumível).

---

## Pergunta

O centro de massa do #32 usa o **centroide do polígono** de cada AMC (166 unidades), ponderado pelo ha/cabeça da variável. Isso assume implicitamente que a variável está distribuída uniformemente dentro da AMC — uma aproximação que pode não ser neutra à direção Sul→Norte medida, já que as AMCs do Norte (fronteira) tendem a ser maiores e mais irregulares que as do Sul (núcleo agrícola consolidado). É **MAUP** (*modifiable areal unit problem*) real, ou irrelevante na prática?

## Abordagem

Para cada ano (1985–2024) e cada classe (veg. natural, pastagem, agricultura), calcula a média de longitude/latitude de **todo pixel** do raster MapBiomas classificado naquele grupo, sobre o contorno de Goiás — **sem nenhuma malha administrativa intermediária**. A posição de cada pixel é o próprio pixel (30×30 m), cada um pesando igual:

$$\overline{\text{lat}} = \text{média}(\text{latitude}_{\text{pixel}} \mid \text{pixel} \in \text{classe})$$

Um `reduceRegion` por ano sobre uma imagem de 6 bandas (lon/lat × 3 classes), cada banda mascarada pela própria classe — o GEE aplica o reducer `mean` **banda a banda**, cada uma só sobre seus pixels não-mascarados (semântica padrão de máscara). A contagem de pixels por classe sai num `reduceRegion` separado (reducer `count`), só para diagnóstico (`n_pixels`).

**Classes** (mesmos IDs do #28/#40/#44 — MapBiomas Coleção 10.1): veg_natural = Floresta(3)+Savânica(4)+Campestre(12); pastagem = Pastagem(15); agricultura = 12 classes de lavoura/silvicultura (9,19,20,35,36,39,40,41,46,47,48,62).

**Rebanho bovino fica de fora**: é estatística tabular por município (PPM/IBGE), sem raster de posição — não há como calcular um centroide-pixel "de verdade" para ele. (A robustez do centroide **tabular** do rebanho vem por outra via: o #44 mostra que, para a soja — que tem raster *e* estatística —, o centroide-AMC concorda entre as duas fontes a ~7 km.)

**Gotcha técnico**: o polígono de GO do `geobr` tem ~103 mil vértices (segue meandros de rio como limite estadual) — estourava o limite de computação interativa do GEE mesmo em `scale=90`/`tileScale=16` (testado). Resolvido simplificando a **1 km de tolerância** (Douglas-Peucker) antes de virar `ee.Geometry` — ~800 vértices, área muda **0,005%**, irrelevante frente aos deslocamentos de dezenas/centenas de km medidos. O `_reduzir_com_retry` sobe `tileScale` (4→8→16) e o timeout se o servidor reclamar de memória (mesmo padrão de robustez do #28).

## Achado

**Concordância quase perfeita.** ΔN líquido 1985→2024, pixel (#43) vs centroide-AMC (#32):

| Variável | AMC (#32) | Pixel (#43) | Diferença |
|---|---:|---:|---:|
| Pastagem | +77,6 km | +79,2 km | +1,6 km |
| Agricultura | +65,2 km | +66,9 km | +1,7 km |
| Vegetação natural | +7,6 km | +6,7 km | −0,9 km |

As três diferenças ficam **abaixo de ~1,7 km** — duas ordens de grandeza menores que os deslocamentos medidos (dezenas a ~80 km). As duas séries anuais de latitude **colam visualmente o tempo todo** (`comparacao_pixel_amc.png`), inclusive nas inflexões do Ato II e na desaceleração do Ato III. **O MAUP não é um problema prático para a Camada 1**: o centroide de polígono AMC (#32) é um proxy adequado do centro de massa real.

## Como ler a figura

### `comparacao_pixel_amc.png`
Latitude do centro de massa × ano, três pares de linhas: **cheia** = centroide sobre os 166 polígonos AMC (#32); **tracejada com marcador** = pixel-a-pixel bruto (#43, este script). Bandas de ato ao fundo. Para cada variável — vegetação natural (verde, no topo/norte, ~plana), pastagem (laranja, subindo de −16,6 a −15,9) e agricultura (magenta, subindo de −17,7 a −17,1) — a linha sólida e a tracejada ficam **praticamente sobrepostas em todos os 40 anos**. É a prova visual de que trocar a malha AMC pelo pixel bruto não move o centroide: a leitura Sul→Norte não é artefato de agregação areal.

![Comparação pixel × AMC](../../outputs/centro_massa/comparacao_pixel_amc.png)

## Decisões metodológicas

- **Polígono de GO (não bbox)** — a bounding-box vazaria pixels de UFs vizinhas para dentro da média de lon/lat. Usa-se o contorno estadual, simplificado a 1 km (ver gotcha).
- **Máscara self-masked por classe** — cada banda lon/lat é mascarada pela própria classe; o `mean` do GEE ignora pixels mascarados, então uma só imagem de 6 bandas resolve as 3 classes num `reduceRegion`.
- **`scale=30`** nativo do MapBiomas (ajustável via `--escala` se o GEE estourar; o erro de posição a 60/90 m é irrelevante frente aos km medidos).
- **Cache por ano** (`{ano}.json`) — o `reduceRegion` é caro; o script é resumível e idempotente (`--force` reprocessa).

## Limitações

- Só cobre as **3 classes com raster** (não o rebanho — permanece limitação de **fonte**, não de método; ver ponte via #44 acima).
- `scale=30` nativo, mas a geometria de GO é simplificada (tolerância 1 km) — irrelevante frente aos deslocamentos medidos.
- É robustez de **medição espacial** (malha), não de causalidade — não toca nas conclusões do #34.

## Conexão com a narrativa

Fecha uma robustez adicional da **Camada 1** (#32), ao lado da robustez de janelas (#35/#36) e da desagregação/controles (#44). Não muda nenhuma conclusão — reforça que a leitura Sul→Norte **não é artefato da malha AMC** (este pipeline) nem das fronteiras de ato (#35) nem da largura de janela (#36). Junto com o #44 (que valida o centroide-AMC contra a SIDRA para a soja), consolida a Camada 1 como descritivamente sólida em três frentes: malha, janela e fonte.
