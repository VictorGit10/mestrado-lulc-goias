# Trabalhos paralelos

Material **fora** do foco da dissertação (LULC em Goiás). Mantido aqui para ficar acessível sem
poluir o trabalho principal. Ver `../CLAUDE.md` para a definição de escopo.

## Conteúdo

| Pasta | O que é | Versionado? |
|---|---|---|
| `TrabalhoParalelo/` | Site **publicado**: rebanho bovino BR/MG + Montes Claros (PPM/IBGE). Linkado em `../index.html`. | Sim (git) |
| `Trabalho paralelo/` | Workspace-**fonte**: scripts e dados que geram os PNG/JSON de `TrabalhoParalelo/`. | Não (gitignored) |
| `Minas/` | Site de visualização de **Minas Gerais** (timeline, atlas, séries municipais). | Não |
| `CampoPastoLegal/` | Experiência interativa da viagem de campo "Pasto Legal" (Norte de MG, mai/2026). | Não |

## Dependências fora desta pasta

- **Pipeline de dados de MG**: `../scripts/*_mg.py` (ficaram no `scripts/` principal por
  acoplamento com os coletores de Goiás). Eles geram `../data/processed/*_mg.*`, que o
  `Minas/scripts/preparar_dados_mg.py` consome para montar os JSONs da viz de Minas.
- **Dados compartilhados**: os scripts paralelos leem/gravam em `../data/` e `../outputs/`
  (raiz do repo). Os caminhos foram ajustados após a mudança para `paralelo/`.

## Regenerar

```bash
# Rebanho BR/MG (gera assets de TrabalhoParalelo/)
python "paralelo/Trabalho paralelo/scripts/coleta_ppm_br_bovino.py"
python "paralelo/Trabalho paralelo/scripts/figura_media_mediana_anual.py"
python "paralelo/Trabalho paralelo/scripts/analise_montes_claros.py"

# Viz de Minas (consome data/processed/*_mg.* já gerados por scripts/*_mg.py)
python "paralelo/Minas/scripts/preparar_dados_mg.py"
```
