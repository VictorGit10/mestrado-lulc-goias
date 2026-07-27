# Pipeline #12 — Matrizes de transição pixel-a-pixel via GEE

**Script**: `scripts/transicoes_mapbiomas.py` + `scripts/visualizar_transicoes.py`
**Depende de**: Earth Engine autenticado.
**Outputs**: `data/cache/transicoes/` (9 CSVs) + `outputs/transicoes/` (visualizações).

## O que faz

Calcula matrizes de transição pixel-a-pixel via Google Earth Engine para pares de anos do MapBiomas Coleção 10.1, agregando as 22 classes em 6 grupos. Para cada município de Goiás, cruza o raster do ano-origem com o ano-destino e gera tabela de fluxo (ex: hectares que eram Floresta em 1995 e viraram Pastagem em 2005).

## Pares de anos calculados

`data/cache/transicoes/` contém 9 CSVs (mais pares do que os 5 períodos publicados em `outputs/transicoes/`):
- 1985→1995, 1985→2000, 1985→2010, 1985→2024
- 1995→2005, 2000→2010
- 2005→2015, 2010→2024, 2015→2024

## Visualizações

`scripts/visualizar_transicoes.py` produz:
- Heatmaps origem×destino
- Diagramas Sankey
- Mapas coropléticos das principais conversões

## Como rodar

```bash
python scripts/transicoes_mapbiomas.py
python scripts/visualizar_transicoes.py
```

## Diferença vs Pipeline #5

- Pipeline #5 (proxy) confronta **estoques** anuais — pastagem em t e soja em t+1, sem pareamento espacial.
- Pipeline #12 (este) faz **pareamento pixel-a-pixel real** — cada pixel sabe sua trajetória.

Para a versão final da dissertação, **#12 substitui #5** como fonte primária da matriz de transição. #5 fica como validação cruzada e baseline metodológico.

---

## 🛑 Limitação estrutural: a matriz primária **não enxerga o Mosaico** (registrado em 25/jul/2026)

`transicoes_mapbiomas.py` **exclui a classe 21 (Mosaico de Agricultura ou Pastagem)** do mapa de
6 grupos — os IDs não listados vão para `0` e são mascarados. A justificativa está escrita no
cabeçalho do script:

> `EXCLUÍDO: ID 21 (Mosaico de Agricultura ou Pastagem) — no Cerrado goiano, maioria é pastagem, não agricultura.`

**Essa justificativa não sobrevive ao [#28D](28D_deriva_mosaico.md).** Ela foi escrita quando o
Mosaico era um resíduo estável; a auditoria de julho/2026 mostrou que, no fim da série, ele é
justamente **o destino para onde a conversão migra** (a razão `P→mosaico / P→agric` vai de 0,6 em
2015 para **32,5** em 2024, enquanto o SIDRA registra a soja **+38%**). Ou seja: a classe descartada
por ser "resíduo de pastagem" virou o terminal da rota que mais interessa.

### Consequência

A matriz do #12 — a fonte primária de transições da dissertação, que alimenta [#19](19_conversoes_brutas.md)
e [#33](33_transicoes_regionais.md) — **perde a rota `pastagem → Mosaico → agricultura`**. Onde essa
rota carrega o fluxo, a matriz mostra o pixel simplesmente **saindo da contabilidade**, o que se lê
como "a conversão parou". É exatamente o artefato que a **[D25](../metodologia/tratamento_deriva_mosaico.md)**
descreve, e é a razão pela qual **todo número desta matriz que tenha "agricultura" no destino precisa
ser lido sob o bracket da [D26](../metodologia/tratamento_deriva_mosaico.md)** — nunca na régua crua.

### A validação batimental não protege disso

`validar_batimental()` compara os totais por classe-destino do #12 contra o [#4](04_mapbiomas_municipal.md).
O #4 **carrega** a classe 21 (9.840 linhas: 246 munis × 40 anos), mas a função mapeia os `class_id` do #4
pelo **mesmo** dicionário de 6 grupos e faz `dropna(subset=["classe_agg"])` — descartando a classe 21
**dos dois lados** antes de comparar. A validação é, portanto, **cega por construção** ao Mosaico: ela
confere que os dois pipelines concordam *no subconjunto que ambos enxergam*, e passaria com δ≈0 mesmo
que 100% da conversão recente tivesse migrado para o rótulo excluído. **Um batimento verde aqui não é
evidência de que a rota do Mosaico está coberta.**

### O que seria preciso para fechar

Re-exportar os caches de transição do GEE com a classe 21 como **grupo próprio** (7 grupos, não 6),
propagando a `agregar_conversoes.py` → `analise_transicoes.py` → #19/#33 e aos JSONs do Sankey da
visualização. É **re-execução de GEE + repropagação a jusante**, não um ajuste de leitura — por isso
está registrado aqui como limitação declarada e **não** foi feito nesta passada. Enquanto não for:

- **não** citar a matriz do #12 crua para qualquer afirmação sobre `pasto→agricultura` no Ato III;
- usar o bracket da D26 (`agric` como piso, `agric ∪ mosaico` como teto) e a **âncora SIDRA**;
- tratar `veg→pasto` (que não passa pelo Mosaico) como a transição **imune** do conjunto.

Ver a tabela de alcance auditado em
[`metodologia/tratamento_deriva_mosaico.md`](../metodologia/tratamento_deriva_mosaico.md).
