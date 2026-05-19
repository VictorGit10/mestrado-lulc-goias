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
│   ├── js/
│   │   ├── vendor/scrollama.min.js   # 4.7 KB
│   │   └── timeline.js               # logica do scrollytelling
│   └── data/
│       ├── painel_goias.json         # serie anual UF (40 anos × 18 cols)
│       ├── marcos.json               # 8 marcos politicos
│       └── transicoes_resumo.json    # resumo 1985 → 2024 por classe LULC
├── img/mapas/cobertura_YYYY.webp     # 40 mapas coropleticos (2.84 MB total)
└── scripts/
    ├── preparar_dados_timeline.py    # gera os JSONs em assets/data/
    └── otimizar_mapas_webp.py        # PNG → WebP em batch
```

Bundle total: ~3 MB (HTML + CSS + JS + dados + 40 mapas).

## Como gerar / atualizar

A peca consome assets de fora da pasta:

- `data/processed/painel_unificado.parquet` (Pipeline #16)
- `outputs/mapas/cobertura_YYYY.png` (Pipeline #9)

Para regerar tudo:

```powershell
python Visualizacao/scripts/preparar_dados_timeline.py
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

MVP de 5 dias (escopo deliberadamente reduzido). Roadmap em
`C:\Users\amara\.claude\plans\partitioned-stirring-mountain.md`.

## Estrutura narrativa: 3 atos no territorio

A peca conta 1985-2024 em **3 atos** com protagonistas no territorio. Os
**8 marcos politicos** sao pinos na regua superior (nao mais capitulos).

| Ato | Anos | Protagonista |
|---|---|---|
| I. Pastagem como heranca | 1985-2000 | Pastagem extensiva |
| II. Expansao e intensificacao | 2001-2019 | Soja + commodity boom |
| III. Conversao seletiva | 2020-2024 | Frigorificos + reorganizacao |

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
