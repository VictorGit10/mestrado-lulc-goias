# Pipeline #33 — Mecanismo de transições por mesorregião × ato

**Script**: `scripts/transicoes_regionais.py`
**Quando foi feito**: 2026-06-06. Camada 2 da narrativa de deslocamento Sul→Norte.
**Depende de**: #19 (`conversao_bruta_municipal.csv`), #18 (mesorregiões), #28 (idade do pasto). Reusa a maquinaria do #25 (`analise_transicoes.py`).
**Outputs**:
- `data/processed/transicoes_regionais_matrizes.csv` — matriz 6×6 (mesorregião × ato), formato longo.
- `data/processed/transicoes_regionais_fluxos_chave.csv` — fluxos-chave + balanço líquido + idade do pasto, por mesorregião × ato.
- `data/processed/transicoes_regionais_idade.csv` — idade do pasto por mesorregião × ato **com rótulo de identificação** (`exata` / `limite_inferior` / `nao_informativa`), censura % e Kaplan-Meier de sensibilidade.
- `data/processed/transicoes_regionais_dominante.csv` — conversão dominante por mesorregião × ato.
- `outputs/transicoes_regionais/fluxos_chave.png` — barras pasto→agric vs veg→pasto, Sul→Norte, por ato.
- `outputs/transicoes_regionais/dominante_grid.png` — grade mesorregião × ato da conversão dominante.
- `Visualizacao/assets/data/sankey_regional.json` — 15 mini-Sankeys (meso × ato) para o site.

---

## Pergunta de pesquisa

O Pipeline #32 (centro de massa) mostrou **o quê** se moveu: pasto e rebanho marcharam para o norte e a agricultura **desacelerou** no Ato III. Este pipeline responde **por quê** — qual é o **mecanismo** de uso da terra por trás disso.

> A hipótese é um gradiente Sul→Norte: no **Sul**, `pastagem → agricultura` (a lavoura come o pasto e empurra o rebanho para fora); no **Norte/Noroeste**, `vegetação natural → pastagem` (o pasto abre fronteira nova sobre o Cerrado).

---

## A intuição: do "onde" para o "como"

O centro de massa (#32) é uma fotografia do **resultado** — diz que a massa de pasto subiu. Mas não diz **como**: o pasto "andou"? Não — pixels não se movem. O que acontece é que pasto **some** num lugar (vira lavoura) e **aparece** em outro (vira fronteira sobre o Cerrado). A soma desses dois movimentos opostos **desloca o centro de gravidade**.

Para enxergar isso, decompomos cada hectare que mudou de uso em uma **transição** `origem → destino` e perguntamos, **em cada mesorregião e em cada ato**: quais transições dominam? Se o Sul é feito de `pasto→agric` e o Norte de `veg→pasto`, está explicado o porquê do centroide subir.

> [!NOTE]
> **Unidade espacial = mesorregião (IBGE, 5 em Goiás).** É o recorte natural para um eixo "Sul↔Norte". As mesorregiões são ordenadas por **latitude** (média dos pixels de conversão do #28): Sul (−17,7°) → Centro (−16,0°) → Leste (−15,7°) → Noroeste (−15,2°) → Norte (−14,1°).

---

## Como é calculado

1. **Re-corte das conversões.** `conversao_bruta_municipal.csv` (#19 — 235.948 transições ano-a-ano por município) recebe a mesorregião (#18) e é filtrado por ato.
2. **Matriz 6×6** (`matriz_ato`, reusada do #25) por **mesorregião × ato**: linhas = uso de origem, colunas = destino, células = Mha convertidos. A diagonal é persistência; o que interessa é o **off-diagonal** (conversão).
3. **Fluxos-chave** por mesorregião × ato: `pasto→agric`, `veg→pasto`, `agric→pasto`, `veg→agric`, mais o **balanço líquido** de pastagem e agricultura (ganhos − perdas).
4. **Cruzamento com #28**: idade mediana do pasto **no momento da conversão para agricultura**, por mesorregião — conecta o fluxo `pasto→agric` à idade do pasto consumido.

> [!IMPORTANT]
> **Tudo é reportado em taxa anual (Mha/ano).** Os atos têm durações muito diferentes: I = 15, II = 18, III = 4 **transições ano-a-ano** (= fim − início; em anos-calendário inclusivos seriam 16/19/5). A matriz cobre transições consecutivas, então o divisor da taxa é o nº de **transições** (fim − início), não o de anos-calendário. Comparar o **total** em Mha entre atos enganaria — o Ato III pareceria minúsculo só por ser curto.

---

## Achados consolidados

### 1. O gradiente Sul→Norte é real — mas é de ênfase, não de exclusividade
Em **todos** os atos, `pasto→agric` (a barra magenta da figura A) é mais alto no **Sul** e diminui rumo ao norte; `veg→pasto` (verde) é forte no **Centro/Norte**. Mas atenção: o Sul **também** converteu muito Cerrado em pasto, sobretudo no Ato I (quando ainda era fronteira). A assinatura distintiva do Sul não é "só pasto→agric" — é o **surto** de `pasto→agric` no **Ato II**.

### 2. A transição-mãe de Goiás é `veg→pasto`; `pasto→agric` é o sinal do Sul no boom
A grade de **conversão dominante** (figura B) deixa explícito: na **maioria** das células, a conversão líder é `vegetação→pasto` — o Cerrado virando pastagem é a transformação pervasiva do estado. O `pasto→agric` só **assume a liderança** em **duas células**: **Sul e Centro no Ato II** (2001–2019, o boom de commodities). É ali que a intensificação/substituição supera a expansão de fronteira.

### 3. O deslocamento, medido em hectares líquidos
O **balanço líquido de pastagem** quantifica a mudança da fronteira:

| Mesorregião | Ato I | **Ato II** | Ato III |
| :--- | :---: | :---: | :---: |
| **Sul Goiano** | +0,35 | **−0,57** | −0,02 |
| Centro Goiano | +0,11 | −0,15 | +0,01 |
| Leste Goiano | +0,40 | +0,03 | +0,01 |
| Noroeste Goiano | +0,71 | +0,09 | −0,00 |
| Norte Goiano | +0,42 | +0,13 | +0,01 |

*(Mha; + ganha pasto, − perde.)* No **Ato II**, o **Sul perde pasto líquido (−0,57 Mha)** enquanto ganha agricultura (+0,76 Mha) — lavoura **deslocando** pasto. No mesmo período, **Norte (+0,13) e Noroeste (+0,09) ganham pasto**. Em hectares: **o pasto sai do Sul e reaparece no Norte.** É exatamente o que move o centro de massa para cima (#32).

### 4. O Ato III conecta o mecanismo à "desaceleração" do #32
Em taxa anual, no Ato III (2020–2024):
- **Sul: `pasto→agric` despenca** de 0,066 → 0,008 Mha/ano (−88%) → a lavoura **para** de comer pasto no Sul → **a agricultura desacelera** (#32, achado 3).
- **Norte/Noroeste: `veg→pasto` persiste** em ~0,038 Mha/ano → o pasto **segue** abrindo fronteira → **pasto/rebanho continuam subindo** (#32).

O mecanismo, portanto, **explica** o comportamento do centroide período a período.

> [!CAUTION]
> **A primeira metade deste achado NÃO sobrevive ao bracket (D26) — verificado em
> 25/jul/2026, `scripts/transicoes_regionais_bracket.py`.** O `pasto→agric` é medido pela
> classe de destino "agricultura", que no fim da série passa a receber o rótulo "Mosaico
> de Usos" ([#28D / D25](28D_deriva_mosaico.md)). Este é o caso-livro da D25: *a transição
> de interesse "desaparece" enquanto o fenômeno de campo acelera*.
>
> Todas as linhas são a **variação da taxa anual** entre o Ato II e o Ato III (Mha/ano →
> Mha/ano), não variação de área acumulada:
>
> | régua (Δ da taxa anual, Ato II→III) | Sul | Leste | Centro | Noroeste | Norte |
> |---|---:|---:|---:|---:|---:|
> | `pasto→agric` (o número acima) | **−88,4%** | −88,3% | −85,6% | −66,1% | −89,5% |
> | `pasto→(agric∪mosaico)` | **+51,0%** | +28,6% | +38,7% | +119,5% | +31,9% |
> | ritmo de expansão da soja plantada (SIDRA, imune) | **+244%** | +73% | +583% | +567% | +35% |
>
> O bracket **não cruza zero — ele inverte o sinal, nas 5 mesorregiões**, e a âncora imune
> (SIDRA) fica do lado da régua superior. Pela regra da D26 (robusto ⇔ sobrevive nos dois
> extremos), **a queda de −88% não é um achado sobre o campo**: é a assinatura da mudança de
> rótulo. No Sul, a terra que sai de pasto puro para lavoura-ou-uso-misto **acelerou 51%** no
> Ato III, enquanto a soja plantada do IBGE mais que triplicou de ritmo.
>
> **O que fazer com a frase:** não a use para dizer que "a lavoura parou de comer pasto no
> Sul". A leitura defensável do Ato III é a **pergunta grossa**: a saída de pasto puro
> acelerou em todas as mesorregiões. E a ponte com o #32 muda de perna — a desaceleração do
> centroide agrícola no Ato III é ela própria exposta (ver "Robustez à mudança de rótulo" no
> [#32](32_centro_massa.md)); quem sustenta a leitura de fronteira no Sul é o **`veg→pasto`**
> (imune, próxima nota), não este fluxo.
>
> **A segunda metade (o `veg→pasto` do Norte) é IMUNE e sobrevive** — origem e destino
> ficam fora do Mosaico. Na mesma verificação, o `veg→pasto` cai no Sul (−49,3%) e persiste
> no Norte (−12,8%) e no Centro (+2,8%): o contraste Sul-trava/Norte-avança continua de pé
> **por uma medida que a mudança de rótulo não toca** — que é o que o [#39](39_fronteira_fechando.md)
> precisa e usa.

### 5. A idade do pasto (#28) sela a leitura — mas só no Ato III

> **♻️ Revisado em 21/jul/2026.** A versão anterior desta seção publicava uma
> idade mediana agregada 1986–2024 por mesorregião (**Sul 9 · Leste 12 · Centro
> 15 · Noroeste 20 · Norte 20**). Esse número **foi retirado**: ele não estimava
> nenhuma quantidade bem definida. Detalhe completo na nota de método de
> `scripts/transicoes_regionais.py` e no §7.3 de
> [`censo_vs_amostra.md`](../metodologia/censo_vs_amostra.md).
>
> Em resumo: um pixel é censurado quando sua fase de pastagem alcança 1985, e aí
> a idade gravada é `ano − 1985` — um **limite inferior**, não uma medição. Logo
> a censura mede o **horizonte de observação**, que depende de *quando* a região
> converteu. O Sul converteu cedo e tem **70,9%** de censura; o Norte converteu
> tarde e tem **41,9%**. A censura é maior no Sul, não no Norte. Como 42,6% dos
> censurados do Sul têm limite inferior ≤10 anos (7,9% no Norte) e o Ato I pesa
> 45,3% dos eventos no Sul contra 12,4% no Norte, o agregado era uma média de
> artefato de horizonte com pesos que variam por região.

Com estratificação por ato, a idade só é **identificada no Ato III** (horizonte
35–39 anos, censura inteiramente acima da mediana). Ali a mediana observada é
exata — e o Kaplan-Meier concorda com ela nas cinco mesorregiões, confirmando
que a censura não morde:

| | Sul | Leste | Centro | Norte | Noroeste |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ato III (2020–24)** | **16a** | 16a | 28a | **27a** | **31a** |
| censura | 29,3% | 21,0% | 41,9% | 32,0% | 39,5% |

O gradiente sobrevive onde é mensurável: no **Sul** a lavoura consome pasto
comparativamente **jovem** (16a) — coerente com "pasto-reserva" (#28) — e no
**Noroeste/Norte** o pasto convertido é **antigo** (31a/27a), com a ação
principal em `veg→pasto` (fronteira nova). O **Leste** segue mais jovem que a
posição sugere (Entorno do DF, dinamismo próprio).

**Ato I e Ato II não entram**: 10 das 15 células ficam entre "limite inferior" e
"não informativa" (censura ≥50%). O CSV
`transicoes_regionais_idade.csv` traz as 15 com rótulo de identificação, e a
coluna `idade_pasto_mediana_a` do `fluxos_chave.csv` fica **vazia** onde o
número não é medição — de propósito, para não ser plotado como se fosse.

⚠️ Esta página mede **nível**, não forma: **não cruzar com os números do #28C**,
que roda só sobre não-censurados. Ver
["O que a família da idade estabelece"](28_idade_pastagem.md#o-que-a-família-da-idade-estabelece).

> [!CAUTION]
> **Esta tabela também não sobrevive ao bracket — o gradiente não só encolhe, ele INVERTE
> (25/jul/2026, mesmo script).** A tabela acima conta a idade dos pixels cujo destino foi
> rotulado "agricultura"; no Ato III esse é justamente o subconjunto que a mudança de rótulo
> seleciona. Recomputando sobre `pasto→(agric∪mosaico)`, com a mesma convenção (ato pelo
> `ano_conversao`, censurados a face value — que reproduz a linha acima exatamente):
>
> | régua | Sul | Leste | Centro | Noroeste | Norte |
> |---|---:|---:|---:|---:|---:|
> | `pasto→agric` (a tabela acima) | **16a** | 16a | 28a | 31a | 27a |
> | `pasto→(agric∪mosaico)` | **32a** | 21a | 35a | 31a | **23a** |
>
> Na régua superior o **Sul passa a ser a segunda mais VELHA (32a) e o Norte a segunda mais
> jovem (23a)**: a ordenação "Sul jovem → Norte velho" **se inverte**. A leitura de que "no
> Sul a lavoura consome pasto-reserva jovem" vale só dentro do rótulo "agricultura" — é a
> mesma conclusão a que chegaram o [#40](40_duas_logicas_pastagem.md) (bracket-por-evento) e
> o [#28C](28C_bimodalidade_regional.md) (re-checagem sob a união), por caminhos
> independentes. **Retirar da redação o gradiente latitudinal de idade**; o que sobrevive
> daquela família é a **bimodalidade/coexistência** dos dois mecanismos dentro de cada
> região, modulada pelo tempo. Ver [`tratamento_deriva_mosaico.md`](../metodologia/tratamento_deriva_mosaico.md) §9.

---

## Como ler as figuras

### A. `fluxos_chave.png` — o teste do mecanismo
Barras de `pasto→agric` (magenta) e `veg→pasto` (verde) por mesorregião, ordenadas **Sul→Norte**, em painéis por ato e em **Mha/ano** (comparável entre atos). Procure: o magenta **alto no Sul** e o verde **dominando o Norte**; e, no Ato III, o **magenta sumindo** enquanto o verde persiste ao norte.

![Fluxos-chave por mesorregião e ato](../../outputs/transicoes_regionais/fluxos_chave.png)

### B. `dominante_grid.png` — a geografia da conversão dominante
Grade mesorregião (Norte em cima) × ato. Cada célula traz a conversão líder, sua magnitude e a fração da conversão total, com fundo na cor do uso de **destino**. As **únicas** células rosa (`pasto→agric` dominante) são **Sul e Centro no Ato II** — todo o resto é `veg→pasto`. É a prova visual do achado 2.

![Conversão dominante por mesorregião × ato](../../outputs/transicoes_regionais/dominante_grid.png)

---

## Decisões metodológicas

- **Taxa anual (Mha/ano)** para comparar atos de durações diferentes (ver `[!IMPORTANT]` acima).
- **Classes 6×6 agrupadas** (vegetação natural, pastagem, agricultura, água, área urbana, outros), idênticas ao #25 — herdadas de `analise_transicoes.GRUPOS`.
- **Conversões = fluxo bruto ano-a-ano** (#19, do #12 com `--consecutivos`). Capturam rotação **e** substituição; o balanço líquido separa as duas.
- **Mesorregião por latitude** dos pixels de conversão do #28 (dispensa download do geobr).

---

## Limitações

- **Mesorregião é um recorte grosso.** Cada uma agrega dezenas de municípios com dinâmicas internas distintas; o gradiente é uma média regional, não um destino de cada hectare.
- **Descritivo, não causal.** Mostra a **coincidência espacial** do mecanismo (Sul perde pasto / Norte ganha), não prova que um *causa* o outro. A defasagem e o spillover formal são a **Camada 3** (#22/#24 — `Δagric_sul,t-1 → Δrebanho_norte,t`).
- **Fluxo bruto carrega ruído de classificação.** Transições anuais incluem oscilação de classificação do MapBiomas (*flicker*); o balanço líquido e a agregação por ato amortecem, mas não eliminam.
- **Idade do #28 é só do canal `pasto→agric`.** Mede a idade do pasto que virou lavoura — não descreve o pasto que persiste nem o que veio de `veg→pasto`.
- **A idade só é mensurável no Ato III** (5 de 15 células meso×ato). Nos Atos I e II a censura à esquerda consome a mediana: no Ato I o horizonte é de 1–15 anos com 45–84% de censura, então o número reportado seria o horizonte, não a idade. Isso limita a leitura temporal do canal `pasto→agric`: **não** se pode afirmar, com este dado, que a idade do pasto convertido subiu ou caiu ao longo dos atos — só descrever o corte transversal recente.

---

## Conexão com a narrativa

O #33 fecha a ponte que o #32 abriu:

> **#33 (mecanismo)** — Sul: `pasto→agric` sobre pasto jovem; Norte: `veg→pasto` sobre Cerrado →
> **redistribuição líquida** — o Sul perde pasto, o Norte ganha →
> **#32 (resultado)** — o centro de massa do pasto/rebanho migra para o norte, e a agricultura, ancorada no Sul, desacelera quando para de comer pasto (Ato III).

**Próximo passo — Camada 3** (econômica, #22/#24): testar se a expansão da agricultura no Sul *antecede* (lead-lag) o avanço de pasto/rebanho no Norte, e se há *spillover* espacial dos vizinhos — o teste formal de deslocamento.
