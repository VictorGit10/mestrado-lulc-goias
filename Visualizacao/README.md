# Visualizacao — Linha do tempo LULC Goias 1985-2024

Companion digital interativo da dissertacao (CIAMB-UFG). Scrollytelling em
HTML/CSS/JS puro mostrando a relacao entre uso e cobertura da terra em Goias
e marcos institucionais (Plano Real, Lei Kandir, Plano Safra, Codigo Florestal).

## Documentacao

- **`docs/IDEIA.md`** — conceito, tese narrativa, decisoes de design,
  alternativas consideradas, riscos e roadmap.
- **`docs/IMPLEMENTACAO.md`** — estado atual, decisoes tecnicas, estrutura
  de arquivos, pendencias e verificacao end-to-end.

## Estrutura

```
Visualizacao/
├── index.html                  # pagina unica
├── assets/
│   ├── css/styles.css
│   ├── js/                     # 12 modulos + vendor
│   │   ├── vendor/             # scrollama, d3.v7, d3-sankey
│   │   ├── router.js           # hash routing entre as abas
│   │   ├── timeline.js         # scrollytelling dos atos
│   │   ├── marcha.js           # scrollytelling do Movimento III
│   │   ├── marcha-mapa.js      # mapa animado do centro de massa
│   │   ├── sankey.js           # Sankey principal (le sankey_data.json)
│   │   ├── mini-sankey.js      # mini-Sankey por ato (le sankey_ato_*.json)
│   │   ├── matriz.js           # matriz de transicoes
│   │   ├── inventario.js       # vitrine do painel
│   │   ├── pastagem-reserva.js # idade do pasto / reserva de terra
│   │   ├── secoes.js           # navegacao de blocos
│   │   ├── zoom.js             # lightbox das figuras
│   │   └── utils.js
│   └── data/                   # 17 JSONs + 1 geojson + amcs/
│       ├── painel_goias.json         # serie anual UF
│       ├── painel_amc_indice.json + amcs/*.json   # 166 AMCs
│       ├── malha_amc.geojson         # malha das AMCs (coropletico)
│       ├── marcha_centro_massa.json  # #32/#44
│       ├── idade_pastagem_*.json     # 4 arquivos (#28/#28C, censo)
│       ├── sankey_data.json + sankey_ato_{I,II,III}.json + sankey_regional.json
│       ├── transicoes_{matriz,resumo}.json
│       ├── fogo_goias.json           # #14
│       └── marcos.json               # 8 marcos politicos
├── img/                        # 154 figuras em 7 pastas
│   ├── mapas_gee/cobertura_YYYY.webp      # 40 coropleticos anuais (#10)
│   ├── mapas_delta/delta_YYYY.webp        # 40 mapas de variacao
│   ├── mapas_fogo/*.webp                  # 40 mapas de fogo (#14)
│   ├── mapas_transicoes/transicao_*.webp  # 5 recortes de periodo
│   ├── marcha_norte/*.png                 # 17 figuras da marcha (#32-#44)
│   ├── graficos/*                         # 10 graficos de sintese
│   └── correlacoes/*                      # 2
└── scripts/
    ├── preparar_dados_timeline.py    # gera os JSONs em assets/data/
    ├── gerar_graficos_sintese.py
    ├── gerar_mapas_delta_lulc.py
    ├── gerar_mapas_fogo_40anos.py
    └── otimizar_mapas_webp.py        # PNG → WebP em batch
```

Bundle total: ~40 MB (30 MB de imagens + 9,8 MB de dados/assets).

## Como gerar / atualizar

A peca consome assets de fora da pasta:

- `data/processed/painel_unificado.parquet` (Pipeline #16)
- `data/processed/painel_amc_goias.parquet` (Pipeline #25) — abas AMC e marcha
- `outputs/mapas_gee/cobertura_YYYY.png` (Pipeline #10)
- `outputs/centro_massa/*.png` (Pipelines #32/#43/#44) e demais `outputs/`
  citados nas figuras da aba Narrativa

Para regerar tudo:

```powershell
python Visualizacao/scripts/preparar_dados_timeline.py
python Visualizacao/scripts/gerar_graficos_sintese.py
python Visualizacao/scripts/gerar_mapas_delta_lulc.py
python Visualizacao/scripts/gerar_mapas_fogo_40anos.py
python Visualizacao/scripts/otimizar_mapas_webp.py
```

## Como rodar localmente

O site usa `fetch()` para carregar dados, entao **precisa ser servido por HTTP**
(duplo-clique direto no `index.html` nao funciona — `file://` bloqueia `fetch`).
Mesmo comportamento do GitHub Pages.

- **Mais facil (Windows):** duplo-clique em `servir.bat`. Abre o navegador automaticamente.
- **PowerShell:** `.\servir.ps1` dentro da pasta `Visualizacao/`.
- **Manual:** `python -m http.server 8765 --directory Visualizacao` e abrir <http://127.0.0.1:8765/>.

Para parar o servidor: `Ctrl+C` no terminal (ou fechar a janela).

## Stack

- HTML semantico + CSS Grid + vanilla JS
- [Scrollama 3.x](https://github.com/russellsamora/scrollama) para triggers
- WebP qualidade 85 (reducao ~70% sobre PNG)
- Sem build pipeline, sem framework

## Status

Comecou como MVP de 5 dias (escopo deliberadamente reduzido) e cresceu para o
companion completo descrito acima. Proposta de re-arquitetura em **4 pernas de
evidencia** (alinhada a `Textos/indice_logico_pipelines.md`) esta em
`docs/PROPOSTA_REFORMULACAO.md` — **redigida, nao executada**: o site ainda
apresenta a estrutura por atos/movimentos. Pendencias tecnicas em
`docs/IMPLEMENTACAO.md`.

## Abas (jun/2026, revisado jul/2026)

A pagina tem **duas abas** (hash routing em `router.js`):

- **Narrativa** — scrollytelling dos 3 atos (40 mapas) + "Depois dos mapas",
  o argumento em 3 movimentos (saldo/fluxos → processos no agregado → marcha
  ao norte) ate a tese. Cada secao abre com a *pergunta* e fecha com a
  *resposta em uma frase* (`.bloco-pergunta` / `.bloco-resposta`); jargao tem
  tooltip (`.termo`). O **Movimento III e um segundo scrollytelling**
  (`marcha.js` + `.marcha-scrolly`): painel de figura fixo a esquerda troca a
  figura-chave (#32→#33→#42→#37→#39) conforme o leitor avanca pelos passos
  7–11; em telas <1020px degrada para fluxo normal com figuras inline
  (`.figura-chave`). A secao 12 expoe a **autocorrecao** do metodo (#40, #41,
  #28C) em cards visiveis. Depois dos mapas, a regua superior vira uma
  **navegacao de blocos** (`secoes.js` + `#rail-secoes`). Rolagens
  programaticas respeitam `prefers-reduced-motion`.
- **Metodos** — a oficina: periodizacao dos atos, metricas do tempo, tres
  camadas de evidencia, vitrine do painel, **decisoes D1-D26** (agrupadas por
  tema), limitacoes e glossario. Ancoras: `#metodos/<id>` (ex.:
  `#metodos/metodo-evidencia`); de volta, `#narrativa/<id>`.

## Estrutura narrativa: 3 atos no territorio

A peca conta 1985-2024 em **3 atos** com protagonistas no territorio. Os
**8 marcos politicos** sao pinos na regua superior (nao mais capitulos).

| Ato | Anos | Protagonista |
|---|---|---|
| I. Pastagem como heranca | 1985-2000 | Pastagem extensiva |
| II. Expansao e intensificacao | 2001-2019 | Soja + commodity boom |
| III. Conversao acelerada (mascarada) | 2020-2024 | Aceleracao que a medida crua esconde (#28D) |

### Marcos politicos (pinos da regua, validar com orientador)

1. **1985** — Inicio da serie / redemocratizacao (baseline)
2. **1994** — Plano Real
3. **1996** — Lei Kandir (LC 87/1996)
4. **2002** — Sistematizacao do Plano Safra
5. **2003** — Boom commodity / China shock
6. **2012** — Novo Codigo Florestal (Lei 12.651/2012)
7. **2018** — Cerrado Manifesto + reorganizacao frigorifica
8. **2024** — Fim da serie / sintese

Bibliografia inicial em `assets/data/marcos.json`. Os marcos de **2003 e
2018 foram adicionados** com a refatoracao para 3 atos e ainda aguardam
revisao bibliografica do orientador.
