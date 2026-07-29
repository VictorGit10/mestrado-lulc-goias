# Pipeline #27 — Coleta Trase.earth (cadeia produtiva soja + boi)

**Script**: `scripts/coleta_trase.py`
**Quando foi feito**: 2026-05-15 (zips baixados e painel gerado); commitado em 2026-05-16.
**Depende de**: `mapeamento_mesorregioes.csv` (#18, para o de-para nome → `cd_mun`) e os dois zips
Trase **baixados manualmente** em `data/raw/trase/`.
**Consumido por**: #16 (painel unificado, colunas `trase_*`) e **#45** (`analise_trase_lulc.py`, a
análise — o Eixo A).
**Outputs**: `data/processed/painel_trase.csv` (4.109 × 18).

---

## O que faz

Lê os dois datasets de cadeia produtiva da Trase.earth, filtra as linhas com produção originada em
**GOIAS**, mapeia o nome do município Trase (caixa-alta, sem acento) para `cd_mun` do IBGE, e agrega
por `(cd_mun, ano)`.

Para cada município-ano e cada cadeia (soja, boi), produz cinco métricas: **volume** escoado,
**valor FOB**, número de **players** distintos (tradings / frigoríficos), número de **hubs
logísticos** distintos, e o **maior player** por volume.

É um **coletor puro** — não analisa nada. Ficou dormente por dois meses até o #45 ativá-lo.

## Fontes

Trase.earth, licença **CC BY 4.0**. Os zips **não são baixados pelo script** (não há API); o
script falha com instrução explícita se não os encontrar.

| Cadeia | Dataset | Cobertura | Zip | Descompactado |
|---|---|---|---|---|
| Boi | `brazil_beef_v2_2_2` | 2011–2017 + **2019–2023** (sem 2018) | 291 MB | **1,86 GB** |
| Soja | `brazil_soy_v2_6_1_composite` | 2004–2022 | 32 MB | 171 MB |

DOI da soja: `10.48650/DCE3-JJ97`. URLs em `resources.trase.earth/20260511/data/supply-chains/`.

**Decisão de leitura**: o beef é lido em **chunks de 200 mil linhas com filtro inline** por GO — 1,86 GB
não cabe confortavelmente em memória. A soja cabe e é lida de uma vez. É a única razão de os dois
caminhos de código serem diferentes.

## Saída — schema

`data/processed/painel_trase.csv` — **4.109 linhas × 18 colunas** (2 chaves + 16 de dado), 244 municípios, 2004–2023.

`{cadeia}` = `soja` ou `boi`. As colunas são simétricas nas duas cadeias.

| Coluna | Tipo | Nota |
|---|---|---|
| `cd_mun`, `ano` | chave | Padrão do projeto |
| `trase_{cadeia}_volume_t` | numérica | **Fluxo total rastreado** = export + doméstico. ⚠️ **Não é "volume exportado"** — na soja tem r=0,986 com a área plantada, ou seja, é **produção**. Não use como proxy de cadeia exportadora |
| `trase_{cadeia}_volume_export_t` | numérica | ✅ **Só exportação** — este é o proxy de exposição à cadeia exportadora |
| `trase_{cadeia}_volume_domestico_t` | numérica | Só esmagamento/abate no Brasil. **0 em todas as linhas do boi** (verificado, não suposto) |
| `trase_{cadeia}_fob_usd` | numérica | Só exportação **por construção** (as linhas domésticas têm FOB = 0) |
| `trase_soja_n_exporters` / `trase_boi_n_frigorificos` | numérica | Só players **identificados** (exclui os 3 rótulos pseudo) |
| `trase_{cadeia}_n_hubs` | numérica | Hubs logísticos distintos (todas as linhas) |
| `trase_{cadeia}_n_hubs_export` | numérica | Hubs distintos **nas linhas de exportação** |
| `trase_soja_top_exporter` / `trase_boi_top_frigorifico` | categórica | Maior trading **identificada** por volume; `None` se o muni-ano não teve exportador identificado |

São **16 colunas numéricas** + 2 categóricas. O #45 usa `_volume_export_t` (e `_volume_domestico_t`
como contraste).

> **Invariante checado a cada execução**: `volume_t == volume_export_t + volume_domestico_t` nas duas
> cadeias (assert no `main()`, tolerância de float).

### Cobertura real

| | Células | Municípios | Anos |
|---|---|---|---|
| Soja | 3.264 | 222 | 2004–2022 (todos) |
| Boi | 2.834 | 243 | 2011–2023, **sem 2018** |

Totais na janela: soja **166,4 Mt** rastreados, dos quais **92,2 Mt (55,4%) exportados** —
**US$ 37,9 bi** FOB; boi **3,07 Mt**, **100% exportados** — **US$ 10,4 bi** FOB.

**Dois municípios não têm nenhuma linha Trase**: Teresina de Goiás e Valparaíso de Goiás. É
ausência real na fonte, não falha de mapeamento (ver validação abaixo) — coerente com o perfil dos
dois (Valparaíso é município-dormitório da RIDE-DF).

**O buraco de 2018 no boi é da fonte** (o dataset v2.2.2 não traz o ano), não do script. Qualquer
análise com o boi trabalha com 12 anos não contíguos — o que o #45 declara como limitação de poder.

---

## ⚠️ A pegadinha: "Trase = só exportação" **não vale para a soja**

Esta era a premissa original do script — e ela é **verdadeira para o boi e falsa para a soja**.
Descoberta ao escrever esta doc (jul/2026) e **corrigida no schema**. Medido no zip bruto
(Goiás, 2004–2022):

| Categoria no campo `exporter` | Volume | Fatia | O que é |
|---|---|---|---|
| Tradings identificadas | 89,9 Mt | 54,0% | Exportação ✅ |
| `UNKNOWN` + `UNKNOWN CUSTOMER` | 2,3 Mt | 1,4% | **Exportação real**, trader anônimo ✅ |
| **`PROCESSED DOMESTICALLY`** | **74,2 Mt** | **44,6%** | Esmagamento no Brasil ❌ |

O dataset **composite** da soja cobre o fluxo total rastreado e **etiqueta** o que foi esmagado
internamente, em vez de omiti-lo. A discriminação é inequívoca no dado, e foi verificada linha a
linha:

- `PROCESSED DOMESTICALLY` → `country_of_first_import = BRAZIL` em **100%** das linhas, `fob = 0`
  em **100%** das linhas, `port_of_export` ausente ou literal `PROCESSED DOMESTICALLY`.
- `UNKNOWN` / `UNKNOWN CUSTOMER` → destinos **estrangeiros** reais (China, Alemanha, Irã, Tailândia),
  portos reais (Santos, Paranaguá, Manaus), `fob > 0` em **100%** das linhas. **É exportação** — só
  o trader é anônimo. Por isso entram no volume exportado, mas **não** contam como *player*.

**O que isso causava (e como foi corrigido):**

| Sintoma | Causa | Correção |
|---|---|---|
| `trase_soja_volume_t` misturava 55% export + 45% doméstico — e tinha **r=0,986 com a área plantada**, ou seja, **era produção** | `_agregar_grupo` somava `volume` sobre todas as linhas | Coluna mantida (é um total legítimo), mas **acrescentadas** `_volume_export_t` e `_volume_domestico_t` |
| `fob/volume` da soja **não era preço** (45% do volume com FOB = 0) | universos diferentes no numerador e denominador | Documentado; use `fob_usd / volume_export_t` |
| `n_exporters` contava até **3 pseudo-players** | `nunique()` sobre o campo cru | Só tradings **identificadas** |
| `top_exporter` era `PROCESSED DOMESTICALLY` em **51%** dos muni-anos | idem | Maior trading **identificada**; `None` se não houver |

O **boi não tem o problema**: nenhuma linha `PROCESSED DOMESTICALLY` (o script **verifica e
imprime**, em vez de supor), 125 frigoríficos reais, forte concentração — **JBS 48,6% + Minerva
28,6% + Marfrig 8,2% = 85,4%** do volume goiano. As colunas `_volume_domestico_t` do boi saem 0. A
simetria é proposital: se uma versão futura da Trase passar a incluir volume doméstico no boi, os
números aparecem em vez de contaminar em silêncio.

> **Consequência para o #45 — corrigida em 2026-07-17.** O #45 pareava `trase_soja_volume_t` e o
> chamava de "volume exportado"; seu achado mais forte era `β = +0,335` (soja-SIDRA), anunciado como
> co-movimento material. Com `_volume_export_t`, o **β cai 9× para +0,037** e o r²within cai de
> 0,268 para 0,025 — o sinal antigo era a variável medindo produção. O veredito do #45 (a infra não
> lidera) **sobrevive e fica mais limpo**. Ver [`45_trase_lulc.md`](45_trase_lulc.md).

---

## Validações realizadas

**De-para de municípios: perfeito nas duas cadeias.** A normalização (`normaliza_nome`: NFKD →
ASCII → caixa-alta → colapso de espaços) resolve 100% dos nomes:

| Cadeia | Linhas GO | Não mapeadas | Volume perdido |
|---|---|---|---|
| Soja | 44.929 | **0** (0,000%) | **0,000%** |
| Boi | 601.215 | **0** (0,000%) | **0,000%** |

Nenhum município Trase ficou órfão — o `dropna(subset=["cd_mun"])` do script não descarta nada em
Goiás. O script imprime os não-mapeados quando existem; aqui a lista sai vazia.

**Idempotência**: `main()` sai cedo se `painel_trase.csv` existe; `--force` reprocessa.

## Como rodar

```bash
# Pré-requisito: baixar manualmente os dois zips para data/raw/trase/
#   https://resources.trase.earth/20260511/data/supply-chains/brazil_beef_v2_2_2.zip
#   https://resources.trase.earth/20260511/data/supply-chains/brazil_soy_v2_6_1_composite.zip

py -3.14 scripts/coleta_trase.py            # ~2-3 min (o beef domina o tempo)
py -3.14 scripts/coleta_trase.py --force    # reprocessa mesmo se a saída existe
```

## Limitações honestas

- **Proxy de exposição, não de capacidade.** Mesmo no boi (que é export-only de verdade), a Trase
  mede **fluxo**, não ativos físicos instalados. Silos, esmagadoras e frigoríficos com SIF exigiriam
  CONAB SISDEP / SIGSIF-MAPA — coletas listadas no backlog.
- **Janela curta e desalinhada.** Soja 19 anos, boi 12 (sem 2018), contra os 40 anos do LULC. Toda
  análise com Trase vive numa fatia recente da série.
- **A assimetria soja × boi era conceitual, não só de cobertura** (ver a pegadinha acima). Está
  resolvida no schema: o par comparável entre as cadeias é **`_volume_export_t`**. Comparar
  `trase_soja_volume_t` com `trase_boi_volume_t` continua sendo erro (total × exportação).
- **`top_exporter` / `top_frigorifico` são categóricas** e não entram em nenhuma regressão — ficam
  como cor descritiva (quem domina onde).

## Conexão com a narrativa

Pertence à **Fase 1** (fundação de dados) e é o insumo do **Eixo A**. Ficou dormente de maio a
julho/2026 — coletado sem uso — até o **#45** perguntar se a infraestrutura exportadora *antecede*
ou *segue* a expansão do uso da terra. Resposta: **co-move contemporaneamente, não lidera** — o
terceiro canal (depois de #34 e #37/#42) a confirmar co-evolução sem precedência temporal.

Ver o [índice lógico](../indice_logico_pipelines.md) para o papel deste pipeline (coletor) e
[`45_trase_lulc.md`](45_trase_lulc.md) para a análise.
