# Oscilação pasto↔savana e o fluxo reverso pasto→"vegetação natural"

**Data:** 31/jul/2026
**Pipelines relacionados:** #12/#12B (transições), #33 (mecanismo regional), #29c (bracket), #47 (carbono), #32/#44 (centro de massa)
**Script de verificação:** `scripts/checar_transicao_pasto_natural_classe.py`
**Output:** `data/processed/checar_transicao_pasto_natural_classe.csv`

## 1. A pergunta

Nas matrizes de transição agregadas (#12B), o **fluxo reverso** `pastagem → vegetação natural` é grande — o pasto é, entre os usos antrópicos, o que mais "vai para natural". Isso levanta duas perguntas:

1. É **regeneração real** (pasto abandonado voltando a Cerrado) ou **artefato de classificador** (oscilação na fronteira espectralmente ambígua)?
2. O rótulo `vegetação nativa` usado na viz é correto? (Não: o agregado é `vegetação natural` = Formação Florestal(3) + Savânica(4) + Campestre(12).)

Este doc responde à (1) com dados em classe bruta e audita quais conclusões do projeto são afetadas. A (2) foi corrigida na viz (ver §6).

## 2. Hipótese inicial (e correção)

**Hipótese inicial:** o reverso seria majoritariamente `pasto↔campo natural(12)` — o par mais confundido do MapBiomas no Cerrado.

**Resultado:** **refutado.** Em Goiás, `pasto→Campo(12)` é ~0% em todos os pares. O reverso é **`pasto→Savana(4)`** = Cerrado *sensu stricto* (formação arbóreo-arbustiva), com 75–98% do fluxo. A classe confusa com pasto, em Goiás, é a **savana**, não o campo. Mudou a classe, não o mecanismo.

## 3. Evidência (classe bruta, sem colapsar)

O `GRUPO_MAP` (`processa_cubo_idade.py`) colapsa 3+4+12 num único grupo *antes* de contar a transição. O script de verificação lê o cubo cru (`data/raw/cubo_go/`, IDs 0–255) **sem aplicar a LUT** e acumula a matriz 256×256 ponderada por área (correção cos(lat), mesma metodologia do #28), para pares decenais, consecutivos e o par longo 1985→2024.

Decomposição do fluxo reverso `pasto→natural` (ha):

| Par | pasto→Floresta(3) | pasto→Savana(4) | pasto→Campo(12) | savana→pasto (reverso) | razão s→p / p→s |
|---|---|---|---|---|---|
| 1985→1995 | 73.522 (25%) | **218.505 (75%)** | 50 (0%) | 1.840.841 | 8,4× |
| 1995→2005 | 29.089 (7%) | **365.669 (93%)** | 132 (0%) | 1.292.934 | 3,5× |
| 2005→2015 | 36.491 (8%) | **410.521 (92%)** | 190 (0%) | 741.524 | 1,8× |
| 2015→2024 | 27.952 (7%) | **387.220 (93%)** | 192 (0%) | 527.995 | 1,36× |
| 1985→2024 | 184.049 (38%) | 303.134 (62%) | 66 (0%) | 2.889.783 | — |
| 2023→2024 (anual) | 937 (2%) | **50.770 (98%)** | 88 (0%) | 61.792 | **1,22×** |

**Assinatura de oscilação, não regeneração:** a razão `savana→pasto : pasto→savana` colapsa de 8,4× (1985-95) para 1,22× (2023-24 anual). Num único ano há 50.770 ha de pasto→savana **e** 61.792 ha de savana→pasto — fluxo grosso bidirecional quase balanceado. Regeneração real é lenta e unidirecional; oscilação de classificador é bidirecional e balanceada ano a ano. É o que se vê.

**Componente real, minoritário, em floresta(3):** só no par longo 1985→2024 o `pasto→Floresta` sobe para 184.049 ha (38% do reverso) — sinal de regeneração secundária lenta que só se acumula em horizontes longos. Nas janelas decenais/anuais é 2–8%.

## 4. Por que não derruba conclusões-manchete

O artefato infla o **fluxo reverso**. As conclusões do projeto se apoiam no **fluxo direto** (`veg→pasto`, conversão real de Cerrado) e em **saldos líquidos** — ambos robustos à oscilação simétrica (que se cancela no líquido).

| Achado/conclusão | Usa o reverso pasto→natural? | Afetado? |
|---|---|---|
| **#33 mecanismo** (Sul `pasto→agric` / Norte `veg→pasto`) | Não — fluxos-chave são ambos *diretos*; métrica é o líquido `ganhos−perdas` | **Não.** O #33 já caveat o flicker (`33_transicoes_regionais.md:254`) |
| **#29c bracket** ("retração da agricultura é a régua, não o campo") | Não — veredito se apoia em `pasto→agric`; `pasto→veg` só é reportado | **Não** |
| **#12 intensity** ("mudança COMPOSICIONAL, perda de veg_nat") | Não — conclusão é sobre **perda**, não ganho | **Não** |
| **#47 carbono** ("floresta nativa ganha área no Norte, abate emissão savânica") | Usa **saldo líquido de estoque**; bruto é "cota-teto" declarada | **Não** — ver §5 |
| **#32/#44 centro de massa** (natural = teto estável; pasto/rebanho marcham ao norte) | Não — natural é teto; oscilação adiciona ruído, não tendência | **Não** (+10km de viés já triangulado) |

O #33 já documenta o fenômeno: *"Fluxo bruto carrega ruído de classificação. Transições anuais incluem oscilação de classificação do MapBiomas (flicker); o balanço líquido e a agregação por ato amortecem, mas não eliminam."* A defesa (líquido + agregação por ato) é parte do desenho, não um adendo.

## 5. Por que o #47 (o caso mais delicado) aguenta

O #47 é o único lugar onde um *ganho* vira **crédito** (de emissão). Não é derrubado por dois motivos:

1. **É líquido, não bruto.** `perda_estoque()` computa a diferença de estoque entre dois anos; o comentário do script diz "líquido (diferença de estoque); bruto ≥ líquido (o líquido desconta rebrota)". Oscilação simétrica pasto↔savana **se cancela no líquido**. O bruto, que seria inflado, é explicitamente rotulado "cota-teto".
2. **É floresta(3), não savana(4).** A oscilação medida é `pasto↔savana(4)`. O crédito do #47 é ganho de **floresta(3)** — classe que essa oscilação não toca. O sinal `pasto→floresta` no par longo 1985→2024 (184 kha) é consistente com regeneração secundária lenta real, que sustenta o crédito.

## 6. Rótulo `nativa` → `natural` (corrigido na viz, 31/jul/2026)

O agregado é `vegetação natural` (3+4+12), não `nativa`. "Nativa" evoca Cerrado arbóreo (floresta+savana) mas o grupo inclui campo natural(12) — e superdimensiona a leitura de "Cerrado sendo desmatado" quando se fala de "abertura de vegetação nativa".

Corrigido em:
- `Visualizacao/reforma.html` — 7 ocorrências
- `Visualizacao/index.html` — 1 ocorrência
- `Visualizacao/dossie-mosaico.html` — 3 ocorrências

**Mantido** (legítimo):
- `floresta nativa` (classe 3, Formação Florestal, contrastada com savana/campo — uso correto)
- `Cerrado nativo` (referência ao bioma)

**Não tocado:** chaves de coluna de dado `pct_vegetacao_nativa` / `lulc_vegetacao_nativa_ha` em `assets/js/timeline.js` e `inventario.js` — são chaves internas (o display já diz "Vegetação natural"/"Veg. natural"); renomear exigiria tocar produtor + consumidores.

**Resíduo cosmético (não corrigido):** `docs/BLUEPRINT_PARTE2.md` (2) e `scripts/gerar_grafico_duas_populacoes.py:29` (comentário) ainda dizem "vegetação nativa". Não são viz visível.

## 7. Resíduos em aberto

**A. Seta reversa do Sankey (Ato III) inflada.** Não há texto narrando o reverso como regeneração — é só o desenho do diagrama. Mas um leitor pode ler a seta grande `pasto→natural` como "pasto voltando a Cerrado". Vale uma nota/tooltip na viz dizendo que a seta reversa é majoritariamente oscilação de borda pasto↔savana, não recuperação. É cosmético, não é conclusão.

**B. Churn *dentro* do natural (savana↔floresta) NÃO foi medido.** O script mediu `pasto↔{3,4,12}`, não `savana↔floresta`. É um artefato *diferent*e do confirmado, e é o único que poderia, em tese, biasedar o #47: se no Norte o classificador promover savana→floresta assimetricamente, o "ganho líquido de floresta" do #47 seria inflado por misclassificação dentro do grupo natural. Não há dado para descartar isso. Para defender o crédito do #47 com rigor, rodar o mesmo script estendido aos pares `savana↔floresta` (e `savana↔campo`) — checagem análoga, ~6 min. **Pendente.**

## 8. Família de artefatos

Mesma família do `tratamento_deriva_mosaico.md` (D26): ambos são artefatos de **agregação de classe** — o rótulo colapsa classes que o classificador confunde, e o churn entre elas fica invisível (vira "persistência" na diagonal ou infla fluxos reversos). Ali era `pasto↔Mosaico`; aqui é `pasto↔savana`. A lição é a mesma: toda métrica que usa **fluxo bruto** entre classes agregadas carrega flicker; **líquido** e **agregação por ato** são a defesa.