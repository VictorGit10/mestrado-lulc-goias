# Escopo do repositório

Este repositório contém **um trabalho principal** e **vários trabalhos paralelos**. Por padrão,
toda conversa e tarefa é sobre o **trabalho principal**. Só entre no material paralelo quando o
usuário pedir explicitamente (rebanho bovino, Minas Gerais, Montes Claros, viagem de campo).

## Trabalho principal — dissertação CIAMB-UFG: LULC em Goiás (1985–2024)

Análise de uso e cobertura da terra em **Goiás** e fatores socioeconômicos. É aqui que o trabalho
acontece por padrão.

Pastas/arquivos do principal:
- `Visualizacao/` — site/visualização interativa de Goiás (exceto a variante abaixo).
- `Textos/` — documentação da dissertação (escopo, pipelines, metodologia, outputs).
- `scripts/*.py` — pipelines de Goiás, **exceto os `*_mg.py`** (ver paralelo).
- `data/`, `outputs/`, `notebooks/` — dados, resultados e cadernos (de Goiás).
- `index.html` (raiz), `explicacao_atos.md`, `guia-github-pages-e-commits.md`, `requirements.txt`.

## Trabalhos paralelos — IGNORAR salvo pedido explícito

Não buscar, ler nem editar estes itens durante tarefas de Goiás. Ao trabalhar no principal,
**exclua-os de buscas** (Glob/Grep) e do raciocínio.

- `paralelo/` — guarda-chuva de tudo que é paralelo:
  - `paralelo/TrabalhoParalelo/` — site publicado: rebanho bovino BR/MG + Montes Claros.
  - `paralelo/Trabalho paralelo/` — workspace-fonte (scripts/dados) que gera o site acima
    (gitignored; invisível ao Grep/Glob).
  - `paralelo/Minas/` — site de visualização de Minas Gerais (timeline, atlas, municípios).
  - `paralelo/CampoPastoLegal/` — experiência interativa da viagem de campo (Norte de MG).
- `scripts/*_mg.py` (9 arquivos) — pipeline de dados de **Minas Gerais**. Ficam em `scripts/`
  por acoplamento técnico (ex.: `coleta_sidra_mg.py` importa `coleta_sidra.py` e lê `data/`),
  mas são **paralelos**. O sufixo `_mg` os distingue.
- `Visualizacao/index-Victor-Lapig.html` — variante experimental da viz de Goiás (usa os assets
  de `Visualizacao/`; por isso não foi movida). Não é a viz principal; candidata a remoção se
  obsoleta.

> Há uma análise metodológica em aberto (sugestão de uma professora de Economia) sobre usar
> **Áreas Mínimas Comparáveis (AMC)** do IBGE para séries municipais consistentes — isso é
> relevante tanto para Goiás (principal) quanto para o paralelo de MG. Tratar conforme o
> contexto da conversa.
