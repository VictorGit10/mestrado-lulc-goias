# Visualizacao — A Marcha ao Norte (Goias, 1985-2024)

Companion digital interativo da dissertacao (CIAMB-UFG). Scrollytelling em
HTML/CSS/JS puro sobre a dinamica de uso e cobertura da terra em Goias e sua
relacao com fatores socioeconomicos.

> **Estrutura atual (desde 2/ago/2026): quatro pernas de evidencia, pagina
> unica, sem abas.** A re-arquitetura proposta em `docs/PROPOSTA_REFORMULACAO.md`
> **foi executada**: `index.html` e a peca em quatro pernas, alinhada a
> `Textos/indice_logico_pipelines.md`; a versao anterior, por abas e
> atos/movimentos, ficou congelada em `index-original.html` e nao recebe mais
> correcao. O texto de qualificacao (`qualificacao/`) e a fonte canonica dos
> numeros: quando as duas divergirem, quem se ajusta e esta pagina.

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
│   ├── css/                    # reforma.css (peca atual) + styles.css (legado)
│   ├── js/                     # 19 modulos + vendor
│   │   ├── vendor/             # scrollama, d3.v7, d3-sankey
│   │   ├── rail.js             # trilho lateral de navegacao (peca atual)
│   │   ├── reforma-hero.js     # abertura
│   │   ├── reserva-perna2.js   # mapa + histograma da Perna 2
│   │   ├── pipeline-modal.js   # ficha de pipeline em modal
│   │   ├── router.js           # hash routing (legado: index-original.html)
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

Comecou como MVP de 5 dias (escopo deliberadamente reduzido), cresceu para um
companion por atos/movimentos e, em 2/ago/2026, foi **re-arquitetada em quatro
pernas de evidencia** — a proposta de `docs/PROPOSTA_REFORMULACAO.md`, executada.
Pendencias tecnicas em `docs/IMPLEMENTACAO.md`.

## Estrutura da peca (desde ago/2026)

Pagina unica, sem abas, com **trilho lateral** de navegacao (`rail.js`):

- **Parte 1 — o que aconteceu**: os 3 atos no territorio (40 mapas), o saldo
  por classe e os fluxos (Sankey).
- **Parte 2 — as quatro pernas**: o padrao existe (centro de massa e as cinco
  verificacoes); o mecanismo (duas logicas da pastagem, com mapa e histograma
  interativos em `reserva-perna2.js`); o teste do deslocamento causal, que nao
  se confirma, e o drive comum; e o teto de oferta.
- **Parte 3 — o veredito** e o que o trabalho **nao** afirma.
- **Parte 4 — a oficina**: periodizacao, reguas de robustez, vitrine do painel,
  as **31 decisoes (D1–D31)** em cards colapsados, limites e glossario. As
  fichas de pipeline abrem em modal (`pipeline-modal.js`).
- **Para alem da tese**: as leituras que o dado sustenta fora do argumento
  central.

`verificar_reforma.py` (Playwright) confere as invariantes: contagem de cards de
decisao e de autocorrecoes, 166 AMCs no mapa, ancoras sem duplicata nem link
quebrado, ausencia das frases banidas, console limpo e comportamento no celular.
Rodar com o site servido em `127.0.0.1:8765`.

### Legado — `index-original.html`

A versao por **abas** (Narrativa / Metodos, hash routing em `router.js`), com o
argumento em 3 movimentos e as decisoes D1–D26, fica arquivada e **nao recebe
mais correcao**. Os numeros dela sao os de jul/2026; para qualquer conferencia,
usar `index.html` e o texto de qualificacao.

## Estrutura narrativa: 3 atos no territorio

A peca conta 1985-2024 em **3 atos** com protagonistas no territorio. Os
**8 marcos politicos** sao pinos na regua superior (nao mais capitulos).

| Ato | Anos | Protagonista |
|---|---|---|
| I. Pastagem como heranca | 1985-2000 | Pastagem extensiva |
| II. Expansao e intensificacao | 2001-2019 | Soja + commodity boom |
| III. Conversao acelerada (mascarada) | 2020-2024 | Aceleracao que a medida crua esconde (#28D) |

> O texto de qualificacao intitula o terceiro ato "conversao acelerada **sob
> rotulo ambiguo**", formulacao mais contida que o "(mascarada)" do nome curto
> de `config_periodos.py`: o que parou foi a **classe**, e quanto do vao entre
> as duas reguas e reetiquetagem e quanto e uso misto de fato fica declarado
> como pendente. O nome curto permanece porque e a chave que os scripts usam.

### Marcos politicos (pinos da regua — contexto, nao achado)

> Os marcos sao **pinos de contexto**, e nao causas testadas. O unico que chegou
> a entrar num desenho causal foi o **Commodity Boom de 2003**, no DiD — que o
> proprio texto rebaixa por nao existir grupo nao tratado. A **Lei Kandir nunca
> foi marco do DiD** (ver `Textos/pipelines/23_did.md`), e a ela nao se pendura
> conclusao alguma.

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
