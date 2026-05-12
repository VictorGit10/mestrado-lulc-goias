# Implementacao: estado atual e plano restante

> Documento de execucao. Para a ideia conceitual, ver `IDEIA.md`.

## 1. Estado atual (2026-05-08)

MVP estrutural e narrativo funcionais. Refatoracao para 5 atos no territorio
+ 8 marcos politicos como pinos concluida em 2026-05-07. Atlas expandido com
4 variaveis (LULC, Fogo, Transicoes, Delta vs. 1985) em 2026-05-08. Sankey
lazy-loaded na Sintese.

### 1.1 O que ja roda

Servir localmente:

```powershell
python -m http.server 8765 --directory Visualizacao
# abrir http://127.0.0.1:8765/
```

Funcionalidades operacionais:

- **Hero** com titulo, lede e CTA de scroll
- **Regua superior fixa** com 8 pinos clicaveis (smooth-scroll para o ano)
- **Cursor da regua** que move conforme o scroll
- **Mapa sticky a esquerda** com cross-fade de 450 ms ao trocar de ano
- **40 steps de scroll** (1 por ano), com:
  - Anos-marco (8): card destacado com tag, titulo, subtitulo, descricao e
    referencias bibliograficas — 1985, 1994, 1996, 2002, 2003, 2012, 2018, 2024
  - Anos comuns (32): tag minimalista com o ano
  - Todos: linha de dados-chave (% LULC, soja em Mt, bovinos, **lotacao bov/ha
    pastagem**, PIB, credito)
- **5 atos no territorio** (heranca / soja-sudoeste / boom-commodity /
  intensificacao / reorganizacao) com cabecalho narrativo antes do primeiro
  ano de cada ato
- **Spark-line sticky inferior** com 3 series (% vegetacao, % pasto, % soja)
  e cursor vertical movel
- **Sintese final** com cards de transicao 1985 → 2024 por classe LULC
  + **Diagrama de Sankey** 1985→2024 (D3, lazy-loaded via IntersectionObserver)
- **Footer** com BibTeX, fontes de dados e nota de metodologia
- **Modo Atlas** com 4 variaveis ativas:
  - LULC (40 mapas coropleticos municipais, pixel-a-pixel GEE)
  - Fogo (40 mapas coropleticos municipais, escala log, YlOrRd)
  - Transicoes (5 mapas de periodo, transicao dominante)
  - Delta vs. 1985 (40 mapas divergentes, Δ% pastagem, RdBu_r)
- **Lightbox** para mapa ampliado com info do ano e link para Narrativa

### 1.2 Como os assets sao gerados

```powershell
# Roda em ~10s, le painel_unificado.parquet + transicoes CSV
# Gera 8 JSONs (3 existentes + 5 novos)
python Visualizacao/scripts/preparar_dados_timeline.py

# Roda em ~2min, gera 40 PNGs + 40 WebPs de fogo
python Visualizacao/scripts/gerar_mapas_fogo_40anos.py

# Roda em ~2min, gera 40 PNGs + 40 WebPs de delta
python Visualizacao/scripts/gerar_mapas_delta_lulc.py

# Roda em ~30s, converte 40 PNGs GEE LULC para WebP
python Visualizacao/scripts/otimizar_mapas_webp.py
```

A peca **nao modifica nada** dos pipelines existentes. So consome:

- `data/processed/painel_unificado.parquet` (Pipeline #16)
- `data/processed/transicoes_mapbiomas_goias.csv` (Pipeline #12)
- `outputs/mapas/cobertura_YYYY.png` (Pipeline #9 → Pipeline #10 converte para WebP)
- `outputs/mapas_fogo/fogo_YYYY.png` (gerar_mapas_fogo_40anos.py)
- `outputs/mapas_delta/delta_YYYY.png` (gerar_mapas_delta_lulc.py)
- `outputs/mapas_transicoes/transicao_PERIODO.png` (gerar_mapas_fogo_40anos.py)

### 1.3 Tamanhos

| Asset | Tamanho |
|---|---|
| index.html | 10 KB |
| styles.css | 12 KB |
| timeline.js | 9 KB |
| atlas.js | 9 KB |
| utils.js | 3 KB |
| router.js | 2 KB |
| sankey.js | 5 KB |
| scrollama.min.js | 5 KB |
| d3.v7.min.js | 273 KB |
| d3-sankey.min.js | 6 KB |
| tabs.css + atlas.css | 6 KB |
| painel_goias.json | 41 KB |
| marcos.json | 6 KB |
| transicoes_resumo.json | 1 KB |
| fogo_goias.json | 8 KB |
| painel_municipal_indice.json | 16 KB |
| sankey_data.json | 5 KB |
| transicoes_matriz.json | 6 KB |
| municipios/*.json (246) | ~2 MB |
| 40 mapas LULC WebP | 2.84 MB |
| 40 mapas Fogo WebP | ~3.4 MB |
| 40 mapas Delta WebP | ~3.2 MB |
| 5 mapas Transicoes WebP | 0.5 MB |
| **Total** | **~12 MB** |

Bundle inicial (sem mapas, sem municipios, D3 lazy): ~150 KB.
Mapas carregam sob demanda via `new Image()` no `trocarMapa`.
D3 + d3-sankey carregam so quando Sankey entra na viewport (IntersectionObserver).
Municipios (246 JSONs) carregam sob demanda no drill-down (Fase D).

### 1.4 Compressao alcancada

```
PNG  → WebP qualidade 85
9.69 MB → 2.84 MB  (70.7% menor)
```

Sem perda visual perceptivel a olho nu nos coropleticos.

## 2. Estrutura de arquivos

```
Visualizacao/
├── index.html                          ✓ entry point
├── README.md                           ✓ instrucoes basicas
├── docs/
│   ├── IDEIA.md                        ✓ documento conceitual
│   └── IMPLEMENTACAO.md                ✓ este documento
├── assets/
│   ├── css/
│   │   ├── styles.css                  ✓ ~600 linhas, CSS Grid + sticky + sankey
│   │   ├── tabs.css                    ✓ tabs Narrativa/Atlas
│   │   └── atlas.css                   ✓ grid responsivo, toolbar, lightbox
│   ├── js/
│   │   ├── vendor/scrollama.min.js     ✓ Scrollama 3.2.0
│   │   ├── vendor/d3.v7.min.js         ✓ D3 v7 (lazy-loaded pelo Sankey)
│   │   ├── vendor/d3-sankey.min.js     ✓ d3-sankey (lazy-loaded)
│   │   ├── utils.js                    ✓ constantes + formatadores (window.GO40)
│   │   ├── timeline.js                 ✓ scrollytelling Narrativa
│   │   ├── atlas.js                    ✓ grid + toolbar + lightbox Atlas
│   │   ├── router.js                   ✓ hash routing Narrativa/Atlas
│   │   └── sankey.js                   ✓ Sankey lazy-loaded na Sintese
│   └── data/
│       ├── painel_goias.json           ✓ 40 anos, 18+ cols
│       ├── marcos.json                 ✓ 8 marcos com refs
│       ├── transicoes_resumo.json      ✓ 7 classes LULC
│       ├── fogo_goias.json             ✓ 40 anos, 6 classes fogo UF
│       ├── painel_municipal_indice.json ✓ 246 municipios (lookup)
│       ├── sankey_data.json            ✓ 12 nodos, 23 links
│       ├── transicoes_matriz.json      ✓ 5 matrizes 6x6 por periodo
│       └── municipios/                  ✓ 246 JSONs individuais
├── img/
│   ├── mapas_gee/                      ✓ 40 LULC (pixel-a-pixel 30m)
│   ├── mapas_fogo/                     ✓ 40 fogo (coropletico log-scale)
│   ├── mapas_delta/                    ✓ 40 delta vs.1985 (diverging)
│   └── mapas_transicoes/               ✓ 5 transicoes por periodo
└── scripts/
    ├── preparar_dados_timeline.py      ✓ agrega painel UF, exporta 8 JSONs
    ├── gerar_mapas_fogo_40anos.py      ✓ 40 coropleticos fogo + WebP
    ├── gerar_mapas_delta_lulc.py       ✓ 40 coropleticos delta + WebP
    └── otimizar_mapas_webp.py          ✓ batch PNG → WebP (LULC GEE)
```

## 3. Decisoes tecnicas tomadas

### 3.1 Stack
- **HTML semantico** + **CSS Grid** + **vanilla JS**: sem framework, sem
  build pipeline. Arquivos servidos exatamente como estao.
- **Scrollama 3.2.0**: 5 KB minificado, IntersectionObserver-based, padrao
  de mercado para scrollytelling.
- **WebP qualidade 85**: balanco entre tamanho e fidelidade visual.

### 3.2 Tipografia
- **Corpo**: Source Serif Pro (fallback Crimson Pro / Georgia / Times)
- **UI**: system-ui (-apple-system / Segoe UI / Inter)
- Fontes carregadas do sistema operacional — **nao** ha dependencia de
  Google Fonts (privacidade + offline)

### 3.3 Paleta
- Background: `#fafaf7` (off-white quente)
- Texto: `#1a1a1a`
- Mutado: `#6b6b6b`
- Acento: `#8b3a1d` (terracota Cerrado, usado para soja, marcos, cursor)
- Verde: `#2d5a3d` (vegetacao nativa)
- Dourado: `#c8a45d` (pastagem)

### 3.4 Series do spark-line
Apenas 3 series para evitar poluicao visual:
- `pct_vegetacao_nativa` (soma de floresta_nativa + formacao_savanica + campo_nativo + campo_alagado)
- `pct_pastagem`
- `pct_soja` (LULC MapBiomas, nao ha. plantada SIDRA)

Series com cobertura parcial (PIB municipal 2002-2023, SICOR 2013+) **nao
entram no spark-line** — so aparecem na linha de dados-chave de cada step.

### 3.5 Trigger Scrollama
- `step: ".step[data-year]"` (apenas os 40 steps anuais; os 5 step--era de
  ato nao disparam — sao apenas separadores narrativos)
- `offset: 0.55` (step ativa quando atinge 55% da viewport)
- Animacao: cross-fade do mapa com classe `.is-fading` (opacidade 0.35 →
  pre-load → 1.0)

### 3.6 Posicionamento dos pinos
Pinos da regua e cursor sao posicionados em **percentual proporcional ao
ano**: `((ano - 1985) / 39) * 100%`. Funciona em qualquer largura sem
recalcular.

### 3.7 Tratamento da classe Mosaico (ID 21)
A classe "Mosaico de Agricultura ou Pastagem" (ID 21 do MapBiomas) é intencionalmente excluída dos mapas GEE (ficando transparente através da função `.selfMask()`). Para manter coerência visual entre os mapas rasterizados e a interface interativa (barras empilhadas e legendas), a classe Mosaico também não possui identidade visual isolada no front-end (`index.html`, `timeline.js`, `atlas.js`). Contudo, sua área continua sendo mensurada e preservada no painel tabular unificado (`painel_unificado.parquet`) para cálculos futuros, sendo englobada na visualização dentro da barra "Outros" para fechamento de 100%.

## 4. O que falta (Dia 4 + Dia 5)

### 4.1 Dia 4 — Conteudo narrativo

**Concluido em 2026-05-07** com a refatoracao de 4 capitulos para 5 atos:

- ✓ **Texto introdutorio dos 5 atos** (~150 palavras cada) escrito
  diretamente em `index.html`:
  - I. Pastagem como heranca cerradeira (1985-1993)
  - II. Estabilizacao e a soja chega ao sudoeste (1994-2002)
  - III. Boom commodity sobre pastagem degradada (2003-2011)
  - IV. Codigo Florestal e a intensificacao onde resiste (2012-2017)
  - V. Reorganizacao: frigorificos, oeste e cerrado nordeste (2018-2024)
- ✓ **Marcos politicos novos** (2003 boom commodity, 2018 reorganizacao)
  adicionados em `marcos.json` com referencias bibliograficas
- ✓ **Variavel nova** `lotacao_bov_ha_pasto` exibida na linha de dados-chave
  de cada ano — evidencia empirica do ato IV ("intensificacao onde resiste":
  lotacao sobe de 1,57 para 1,68 cab/ha entre 2012 e 2017 enquanto a area
  de pastagem cai)

Pendente:

- **Revisao do orientador**: copy dos 5 atos + redacao final dos cards de
  2003 e 2018 + bibliografia dos marcos novos
- **Embed do Sankey** existente (`outputs/transicoes/sankey_*.html`) na
  sintese final
- **Embeds seletivos** de graficos analiticos (`outputs/analises/`) em
  pontos estrategicos (ex: grafico 09 scatter pasto↔soja apos Plano Safra)

### 4.2 Dia 5 — Polish, mobile, deploy

- **Cross-browser**: testar em Chrome, Firefox e Edge no Windows
- **Mobile**: ja ha media query para < 900px que stack vertical e esconde
  spark-line; precisa testar em smartphone real e ajustar
- **Lighthouse**: alvo de Performance >= 80, Accessibility >= 90
- **Deploy**: tres opcoes a discutir:
  1. **Repo GitHub novo** `lulc-goias-timeline` com Pages ativado
  2. **Subpasta no repo atual** + Pages (precisa criar remote, hoje sem)
  3. **ZIP estatico** entregue a banca, sem URL publica
- **Atualizar README.md** com link publico (se aplicavel)

### 4.3 Decisao "expandir ou parar"

Apos Dia 5, avaliar com 2-3 colegas e o orientador:

- A peca contribui para a defesa? (sim/nao)
- Vale expandir para v2 (raster MapBiomas em todos os frames, comparador
  A/B, mobile completo, multilingua)?
- Ou ficar com o MVP como artefato final?

## 5. Verificacao end-to-end

Walkthrough manual minimo (passa nas 10 etapas):

1. `python Visualizacao/scripts/preparar_dados_timeline.py` -> 8 JSONs em
   `Visualizacao/assets/data/` + 246 em `municipios/`
2. `python Visualizacao/scripts/gerar_mapas_fogo_40anos.py` -> 40 WebPs em `img/mapas_fogo/`
3. `python Visualizacao/scripts/gerar_mapas_delta_lulc.py` -> 40 WebPs em `img/mapas_delta/`
4. `python Visualizacao/scripts/otimizar_mapas_webp.py` -> 40 WebPs em `img/mapas_gee/`
5. `python -m http.server 8765 --directory Visualizacao` -> abre na 8765
6. Hero rola, mapa de 1985 entra
7. Scroll lento: cross-fade ano-a-ano funcional, spark-line move
8. Em 1994: pino "Plano Real" expande, card aparece com `.step--marco`
9. Clicar em pino "2002" da regua: smooth-scroll para a era do Plano Safra
10. Tab "Atlas" → clicar "Fogo" → grid de 40 mapas de fogo aparece
11. Tab "Atlas" → clicar "Delta" → grid de 40 mapas divergentes aparece
12. Tab "Atlas" → clicar "Transicoes" → grid de 5 mapas de periodo aparece
13. Scroll ate Sintese → Sankey carrega lazy (verificar DevTools Network)

## 6. Reutilizacao de assets do projeto

Tudo consumido em modo leitura. Nada e modificado fora de `Visualizacao/`.

| Asset | Caminho | Uso atual |
|---|---|---|
| Painel unificado | `data/processed/painel_unificado.parquet` | Fonte de series anuais + municipais |
| Transicoes CSV | `data/processed/transicoes_mapbiomas_goias.csv` | Fonte das matrizes e Sankey |
| Coropleticos PNG | `outputs/mapas/cobertura_*.png` | Convertidos para WebP (LULC) |
| Coropleticos transicao | `outputs/transicoes/mapa_transicao_dominante_*.png` | Convertidos para WebP (Transicoes) |
| Mapas de fogo | Gerados por `gerar_mapas_fogo_40anos.py` | WebP coropleticos log-scale |
| Mapas de delta | Gerados por `gerar_mapas_delta_lulc.py` | WebP coropleticos diverging |

## 7. Pendencias documentadas

- [x] ~~Escrever copy das 4 eras~~ → 5 atos escritos diretamente em
      `index.html` (refatoracao 2026-05-07)
- [x] Adicionar variavel de intensificacao pecuaria (lotacao bov/ha pasto)
- [x] ~~Expandir preparar_dados_timeline.py~~ → 8 JSONs (incluindo fogo,
      municipal, transicoes, sankey) gerados (2026-05-08)
- [x] ~~Gerar mapas de fogo~~ → 40 WebPs em `img/mapas_fogo/` (2026-05-08)
- [x] ~~Gerar mapas delta~~ → 40 WebPs em `img/mapas_delta/` (2026-05-08)
- [x] ~~Converter mapas de transicao~~ → 5 WebPs em `img/mapas_transicoes/` (2026-05-08)
- [x] ~~Habilitar toggles do Atlas~~ → Fogo, Transicoes, Delta ativos (2026-05-08)
- [x] ~~Sankey na Sintese~~ → D3 + d3-sankey lazy-loaded, sankey_data.json (2026-05-08)
- [ ] Validar copy dos 5 atos com orientador
- [ ] Validar bibliografia dos marcos novos (2003 boom commodity / 2018
      Cerrado Manifesto + frigorificos) com orientador
- [ ] Testar em 3 browsers (Chrome, Firefox, Edge)
- [ ] Decidir destino de hospedagem (GH Pages novo / atual / ZIP)
- [ ] Atualizar README com URL publica
- [ ] Decidir se expande para v2 ou congela MVP

### Itens registrados como v2 (fora deste MVP)

- Series por mesorregiao no JSON (sub-regionalidade hoje so na narrativa
  textual dos atos)
- Mini-mapas regionais por ato (sudoeste / oeste / nordeste destacados)
- Variaveis adicionais: produtividade soja (ton/ha), fogo segregado por uso,
  IDH-M e componentes
- Abas/lentes alternativas (lente politica vs lente territorio) — descartado
  para manter narrativa linear unica

---

## 8. Atlas (Modo Exploratorio) — refator 2026-05-08

> Plano completo em `C:\Users\amara\.claude\plans\deep-painting-giraffe.md`.
> Esta secao registra o estado de execucao e os passos restantes.

### 8.1 O que foi entregue (vertical slice)

Modo dual ativado: tab **Narrativa** (scrollytelling original) + tab **Atlas**
(parede explorativa de mapas). Hash routing preserva estado:

```
#narrativa            → modo padrao
#narrativa/2010       → scroll-to ano (delegado ao timeline)
#atlas                → grid LULC default
#atlas/lulc/2010      → lightbox no ano
#atlas/{var}          → variavel (lulc | fogo | transicoes | delta)
```

**Funcional no Atlas**:
- Toolbar com 4 toggles de variavel (LULC, Fogo, Transicoes, Delta — todos ativos)
- Grid responsivo: 8x5 (>=1400px), 5x8 (1100-1400), 4x10 (768-1100), 2x20 (mobile)
- 40 miniaturas LULC com borda colorida por ato + pino-mini nos 8 anos-marco
- 40 miniaturas Fogo (YlOrRd, escala log, breaks Jenks globais)
- 40 miniaturas Delta (RdBu_r, diverging centrado em 0)
- 5 miniaturas Transicoes (por periodo)
- Click → lightbox (mapa ampliado + info do ano + botao "Ver no Narrativa")
- Esc / backdrop / X fecha; deep-link via URL hash
- Sparkline some no Atlas (apenas Narrativa)

**Sankey na Sintese**:
- D3 + d3-sankey lazy-loaded via IntersectionObserver
- 12 nodos (6 classes × 2 anos), 23 links (transicoes 1985→2024)
- Valores em Mha, cores alinhadas com paleta do site

### 8.2 Arquivos novos / modificados nesta rodada

**Criados**:

```
Visualizacao/assets/js/utils.js     formatadores e constantes (window.GO40)
Visualizacao/assets/js/router.js    hash routing entre Narrativa | Atlas
Visualizacao/assets/js/atlas.js     grid, toolbar, lightbox
Visualizacao/assets/css/tabs.css    top tabs sticky abaixo da regua
Visualizacao/assets/css/atlas.css   grid responsivo, toolbar, lightbox
```

**Modificados**:

```
Visualizacao/index.html             tabs + 2 sections data-modo + scripts
Visualizacao/assets/css/styles.css  --tabs-h: 40px, sticky tops recalculados
```

### 8.3 Estrutura final pretendida

```
Visualizacao/
├── index.html
├── assets/
│   ├── css/
│   │   ├── styles.css      (ja existe)
│   │   ├── tabs.css        ✓ criado
│   │   ├── atlas.css       ✓ criado
│   │   └── drilldown.css   ⏳ Fase D
│   ├── js/
│   │   ├── vendor/scrollama.min.js
│   │   ├── vendor/d3.v7.bundle.min.js  ⏳ Fase D + E
│   │   ├── utils.js        ✓ criado
│   │   ├── router.js       ✓ criado
│   │   ├── atlas.js        ✓ criado
│   │   ├── timeline.js     (ja existe; sera ampliado na Fase E)
│   │   ├── drilldown.js    ⏳ Fase D
│   │   └── sankey.js       ✓ criado
│   │   └── sankey.js       ⏳ Fase E
│   └── data/
│       ├── painel_goias.json
│       ├── marcos.json
│       ├── transicoes_resumo.json
│       ├── fogo_goias.json              ✓ gerado (nao consumido por JS — futuro)
│       ├── painel_municipal_indice.json ✓ gerado (nao consumido — Fase D)
│       ├── transicoes_matriz.json       ✓ gerado (nao consumido — Fase D)
│       ├── sankey_data.json             ✓ gerado e consumido por sankey.js
│       ├── municipios/{code}.json       ✓ gerado (nao consumido — Fase D, 246 arquivos)
│       └── geo/goias_municipios.topojson ⏳ Fase A2
├── img/
│   ├── mapas_gee/cobertura_*.webp   ✓ consumido por timeline.js e atlas.js
│   ├── mapas_fogo/fogo_*.webp       ✓ consumido por atlas.js (toggle fogo)
│   ├── mapas_transicoes/transicao_*.webp ✓ consumido por atlas.js (toggle transicoes)
│   └── mapas_delta/delta_*.webp     ✓ consumido por atlas.js (toggle delta)
└── scripts/
    ├── preparar_dados_timeline.py   ✓ gerador dos JSONs (ampliado na Fase A3)
    ├── otimizar_mapas_webp.py       ✓ (ja existe)
    ├── gerar_mapas_fogo_40anos.py   ✓ gerador dos mapas de fogo
    ├── gerar_mapas_delta_lulc.py    ✓ gerador dos mapas delta
    └── exportar_geojson_goias.py    ⏳ Fase A2
```

## 9. Passos restantes — em ordem de execucao

Cada passo entrega valor verificavel. Em paralelo: A pode rodar enquanto B/C/D
ficam em pausa. Recomendado seguir A → D → E → F.

### Fase A — Geracao de assets (Python, ~2-3h)

**A1. Gerar 40 mapas coropleticos de fogo**

```powershell
python Visualizacao/scripts/gerar_mapas_fogo_40anos.py
```

Script ainda nao existe. Precisa:
- Ler `data/processed/painel_fogo_municipal.csv` (ou painel_unificado.parquet com
  colunas `fogo_*`)
- `geobr.read_municipality(code_muni="GO", year=2020)` para malha
- Para cada ano 1985-2024: merge fogo_total_ha, `np.log1p`, choropleth matplotlib
- **Critico**: breaks Jenks GLOBAIS (mesmos para os 40 anos), nao por ano —
  senao miniaturas ficam relativas e perdem comparabilidade
- Cmap `YlOrRd`; municipios sem fogo: `#ececec` (cinza distinto)
- Saida: `Visualizacao/img/mapas_fogo/fogo_{ano}.webp` (~150 KB cada)

✓ Check: abrir `img/mapas_fogo/fogo_2020.webp` no browser, comparar com 1995 — 2020
deve ser visivelmente mais intenso.

**A2. Exportar TopoJSON da malha de Goias**

```powershell
python Visualizacao/scripts/exportar_geojson_goias.py
```

- `geobr.read_municipality(code_muni="GO", year=2020)`
- Simplificar: usar lib `topojson` (Python) com `quantization=1e4` ou
  `mapshaper` CLI (`-simplify 5%`)
- Saida: `Visualizacao/assets/data/geo/goias_municipios.topojson` (~150-200 KB)
- Properties: `code_muni`, `name_muni`, `microregiao`

✓ Check: abrir em https://geojson.io/ e ver 246 poligonos.

**A3. Atualizar `preparar_dados_timeline.py`**

```powershell
python Visualizacao/scripts/preparar_dados_timeline.py
```

Adicionar saidas (modificar script existente):
- `assets/data/fogo_goias.json` — serie UF, 40 anos × 6 classes de fogo
- `assets/data/painel_municipal_indice.json` — lookup leve: code_muni, nome,
  microrregiao, centroide
- `assets/data/municipios/{code}.json` × 246 — serie municipal compacta
- `assets/data/transicoes_matriz.json` — 5 matrizes 6x6 (por periodo)
- `assets/data/sankey_data.json` — nodos + links para d3-sankey 1985→2024

✓ Check: `len(os.listdir("Visualizacao/assets/data/municipios"))` deve ser 246.

**A4. Gerar 40 mapas Δ vs. 1985**

```powershell
python Visualizacao/scripts/gerar_mapas_delta_lulc.py
```

Similar ao A1 mas:
- Variavel: Δ%pastagem (ou Δ%vegetacao_nativa) vs. 1985 por municipio
- Cmap diverging `RdBu_r` centrado em 0; 1985 = mapa todo neutro
- Saida: `Visualizacao/img/mapas_delta/delta_{ano}.webp`

✓ Check: 1985 deve ser quase todo neutro; 2024 deve mostrar contraste forte
verde-vermelho.

**A5. Habilitar toggles no Atlas**

Apos A1 + A4 + A2 prontos, editar `assets/js/utils.js` linha ~50:

```javascript
const VARIAVEIS_ATLAS = [
  { id: "lulc",       ..., prontoMVP: true,  ...},
  { id: "fogo",       ..., prontoMVP: true,  ...},  // mudar de false
  { id: "transicoes", ..., prontoMVP: true,  ...},  // mudar de false
  { id: "delta",      ..., prontoMVP: true,  ...}   // mudar de false
];
```

E remover `disabled` + classe `atlas-var--coming` dos botoes em `index.html`
linhas 282-284. Recarregar — toggles ficam clicaveis.

### Fase D — Drill-down municipal (~5-6h, depende de A2 + A3)

**D1. `assets/js/drilldown.js`** (~250 linhas) — painel lateral municipal:
- Lazy fetch `assets/data/municipios/{code}.json` ao clicar muni
- Renderiza ~10 indicadores (composition bar, sparklines pastagem/soja, fogo,
  lotacao, PIB, SICOR, censo, Δ veg, ranking)
- Cache via `fetch(..., {cache: "force-cache"})`
- Slide-in 380px à direita (mobile: bottom sheet 70vh)
- Hash deep-linkable: `#atlas/lulc/municipio/5208707`

**D2. `assets/css/drilldown.css`** — slide-in animado, mini-charts SVG.

**D3. Vendor: D3 v7 bundle parcial**

Gerar bundle minimal com `d3-selection + d3-scale + d3-geo + d3-sankey + topojson-client`:

```powershell
# Opcao 1: bundle pre-pronto via CDN
curl https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js -o Visualizacao/assets/js/vendor/d3.v7.min.js
curl https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js -o Visualizacao/assets/js/vendor/d3-sankey.min.js
curl https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js -o Visualizacao/assets/js/vendor/topojson-client.min.js
```

D3 completo é ~280 KB; aceitavel se nao quisermos rollup. Alternativa: rollup
local com bundle parcial (~100 KB) — fica como otimizacao opcional.

**D4. Integrar no lightbox do Atlas**

Em `atlas.js`, no `abrirLightbox`, adicionar slot SVG e disparar `GO40.drilldown.render(code_muni)` ao hover/click no muni renderizado.

✓ Check: clicar Goiania (5208707) abre painel <500ms; copiar URL e reabrir
mantem estado.

### Fase E — Ampliacoes narrativas (~3h)

**E1. Sparkline com toggle no Narrativa** (em `timeline.js`):
- Adicionar mini-toolbar sobre sparkline (LULC | Fogo | Credito)
- Cada modo pinta 3 series diferentes (ja documentado no plano)
- Estado preservado ao rolar; cursor segue scroll em todos os modos

**E2. 3 pinos extras na regua** (em `index.html` + `styles.css`):
- 2013 (SICOR sistematico), 2017 (Censo Agropecuario), 2020 (Pandemia)
- Classe `.rail-pin--dado` cinza-azul para distinguir dos politicos terracota

**E3. Sankey lazy na Sintese** (`assets/js/sankey.js`):
- IntersectionObserver na `<section class="sintese">`
- Quando entra na viewport: dynamic import D3 + d3-sankey + fetch sankey_data.json
- Renderiza dentro de `<div id="sankey-container">` (criar no HTML)

✓ Check: DevTools Network — `d3-sankey.min.js` carrega so apos o user rolar
ate a Sintese.

### Fase F — Polish + perf + docs (~2h)

**F1. Lazy-loading do Atlas**:
- Confirmar que `loading="lazy"` esta nos 40 imgs (ja esta no atlas.js linha
  ~70). Adicionar IntersectionObserver para descartar `src` de miniaturas muito
  fora da viewport (poupa GPU em mobile).

**F2. Atualizar este `IMPLEMENTACAO.md`**:
- Marcar passos concluidos
- Mover itens de "passos restantes" para "feito"
- Atualizar tamanho total da pasta

**F3. Cross-browser + mobile**:
- Edge + Firefox + Chrome no Windows
- DevTools responsive: 360px, 768px, 1024px, 1440px, 1920px
- Lighthouse desktop alvo: Performance >= 85, Acessibilidade >= 90

## 10. Como executar agora (estado pos-vertical-slice)

```powershell
# 1. Servir
cd C:\Users\amara\OneDrive\Documentos\Antigravity\Mestrado
.\Visualizacao\servir.bat
# ou
python -m http.server 8765 --directory Visualizacao

# 2. Abrir no browser
start http://127.0.0.1:8765/

# 3. Testar Atlas
#    - clicar tab "Atlas" no topo
#    - clicar miniaturas LULC → lightbox
#    - copiar URL #atlas/lulc/2010, abrir em nova aba: deve abrir direto
#    - voltar tab "Narrativa" → scrollytelling intacto
```

Tasks tracking: as Fases A → F estao como itens TaskCreate. Estado atual:
B1, B2, B3, C1, C2 = completed. A1-A5, D1-D4, E1-E3, F1-F3 = pending (criar
sob demanda quando comecar a fase).
