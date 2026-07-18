# Pipeline #45 — A infraestrutura exportadora SEGUE ou LIDERA a expansão LULC?

**Script**: `scripts/analise_trase_lulc.py`
**Quando foi feito**: 2026-07-13. **Corrigido em 2026-07-17** (ver "A correção", abaixo). Ativa o **Eixo A** do backlog (as colunas Trase do #27, até aqui sem análise).
**Depende de**: #27 (`painel_trase.csv`, cadeia produtiva Trase.earth), #16 (`painel_unificado.parquet`, LULC/SIDRA/rebanho/abate). Reusa CCF/Granger do #34 e o padrão PanelOLS do #22; aplica D7 (diferenças) e **D16** (cautela com lead-lag de séries integradas).
**Outputs**:
- `data/processed/trase_lulc_leadlag_agregado.csv` — Bloco A: CCF (pico) + Granger (2 direções) + ADF/KPSS por par.
- `data/processed/trase_lulc_painel.csv` — Bloco B: cross-lagged em painel (β padronizado), 3 termos por par.
- `data/processed/trase_lulc_robustez_defasagem.csv` — **Bloco C (novo)**: cada termo defasado significativo reestimado sob winsor/log1p.
- `outputs/trase_lulc/leadlag_agregado.png`, `painel_direcoes.png`.

---

## ⚠️ A correção de 2026-07-17 — o regressor não era o que dizia ser

A primeira versão deste pipeline pareava **`trase_soja_volume_t`** e o chamava de "volume
exportado". Ao documentar o #27, a premissa foi medida no dado bruto e **não se sustentou**:
**44,6% desse volume é `PROCESSED DOMESTICALLY`** (esmagamento no Brasil; destino BRAZIL, FOB = 0).
A variável não era infraestrutura exportadora — era, quase literalmente, **produção**:

> `trase_soja_volume_t` × `agri_soja_ha_plantada` (área plantada SIDRA): **r = 0,986 em nível.**

Ou seja, o dataset *composite* da Trase rastreia toda a soja produzida no município e a reparte por
destino; somar tudo devolve a produção. O achado-manchete da primeira versão — `β = +0,335`,
`r²within = 0,268`, anunciado como o co-movimento "material" — estava, portanto, **regredindo
produção contra área plantada**. Media a consistência interna da Trase, não uma relação econômica
entre cadeia e uso da terra.

**A correção**: o #27 agora separa `trase_soja_volume_export_t` (exportação de fato) de
`trase_soja_volume_domestico_t` (esmagamento interno), e este pipeline usa o **exportado**. Entrou
um par de **contraste** com o doméstico e um **Bloco C** de robustez dos termos defasados.

**O efeito da correção é grande e vale registrar:**

| Par (co-movimento contemporâneo) | β antigo | β corrigido | r²within |
|---|---|---|---|
| Soja × área plantada SIDRA | **+0,335** | **+0,037** | 0,268 → **0,025** |

O β caiu **9×** e o r²within **10×**. O que parecia a evidência mais forte do Eixo A era artefato
da variável. **Nenhuma conclusão da narrativa muda** — o veredito de não-liderança fica *mais*
limpo —, mas a redação não pode mais chamar aquilo de co-movimento material.

> Reprodutibilidade da correção: rodando a especificação **antiga** (`trase_soja_volume_t`) sobre o
> painel novo, o `β = +0,3351` reaparece ao decimal — a queda vem da **troca da variável**, não de
> mudança de método.

---

## Pergunta de pesquisa

O Pipeline #27 integrou a cadeia produtiva da Trase.earth (soja 2004–2022, boi 2011–2023 sem 2018) ao painel — volume/valor escoado, nº de tradings/frigoríficos, nº de hubs logísticos — mas **nunca rodou análise**. A pergunta do Eixo A:

> A presença de infraestrutura exportadora **antecede** a expansão do uso da terra (a infra "puxa" a lavoura/pasto — seria um vetor de fronteira), ou **segue** a expansão (a infra chega onde a produção já se instalou)?

É o complemento do canal de crédito do #22 (SICOR → retração de pastagem): o canal de **infraestrutura agroindustrial exportadora**.

---

## O que faz (dois níveis, com a disciplina do #42/D16)

- **Bloco A — Lead-lag AGREGADO (série estadual GO, anual).** CCF defasada + Granger nas duas direções, em 1as diferenças (D7). **Disciplina D16**: as séries de área/volume são suaves e integradas; o #42 provou que Granger ingênuo em 1ª diferença sobre séries integradas **fabrica precedência espúria**. Por isso o Bloco A é **diagnóstico, não inferência** — reporta ADF/KPSS de cada série e trata T≈12–18 como baixo poder. A inferência fica com o Bloco B.
- **Bloco B — Cross-lagged em PAINEL (municipal, 2-way FE — o cavalo de batalha).** Variáveis **padronizadas (z-score, padrão #38)** para tornar β comparável entre escalas (toneladas × hectares × cabeças). Por par (infra × LULC), três estimativas em painel de efeitos fixos município+ano, SE clusterizado por município:
  - `contemp` — Δlulc ~ Δinfra (co-movimento, direção-neutro);
  - `infra_lidera` — Δlulc ~ Δinfra(t−1) (infra antecede);
  - `lulc_lidera` — Δinfra ~ Δlulc(t−1) (LULC antecede).
  Usa **defasagem distribuída** (sem termo autorregressivo Y(t−1)) para evitar o viés de Nickell de um CLPM com FE — coerente com o SLX do #34.

**Pareamentos**: Trase soja × `lulc_soja_ha` (MapBiomas), `agri_soja_ha_plantada` (SIDRA), `lulc_agricultura_ha`; Trase boi × `lulc_pastagem_ha`, `pec_bovinos_cab`, `abate_bovino_cab`. A soja com fonte **satélite e censo** dá validação cruzada embutida.

---

## Achados — a cadeia exportadora não lidera *nem* co-move materialmente

### 1. Bloco A confirma o alerta da D16 (diagnóstico, não achado)
Todas as séries pareadas são **≥I(2) ou I(1)** (ADF não rejeita raiz unitária no nível). O Granger agregado é **disperso e inconsistente**: picos de CCF espalhados por lags diferentes com troca de sinal, e **nenhum** p<0,05 forma padrão. É exatamente o comportamento que a D16 prevê para séries integradas com T≈13–19. O agregado é **diagnóstico** e não sustenta leitura causal.

### 2. Bloco B — o que sobra depois de usar a variável certa
Contagem sobre os 9 pares (painel FE, β padronizado):

| Termo | Pares com p<0,05 | Leitura |
|---|---|---|
| co-movimento contemporâneo | 5/9 | mas **só 1 é material** — ver abaixo |
| infra lidera (t−1) | 1/9 | **não sobrevive à robustez** (Bloco C) |
| LULC lidera (t−1) | 2/9 | **não sobrevivem à robustez** (Bloco C) |

A contagem engana; o que importa é a **magnitude**. Os cinco contemporâneos significativos:

| Par | β | r²within | Leitura |
|---|---|---|---|
| **Boi: exportado × abate bovino** | **+0,084** | 0,034 | **o único material** — mas *definicional*: a exportação sai do abate, que por sua vez é **modelado do rebanho** (ver limitações) |
| Soja: exportado × área plantada SIDRA | +0,037 | 0,025 | trivial (era +0,335 antes da correção) |
| Boi: exportado × rebanho bovino | −0,029 | 0,015 | trivial; sinal sensato (exportar puxa o rebanho em pé para baixo) |
| Soja: **esmagamento doméstico** × SIDRA | +0,013 | 0,007 | trivial — o contraste **não** resgata o sinal antigo |
| Boi: exportado × pastagem LULC | −0,004 | 0,007 | trivial |

Todos os p<0,05 vêm do **N alto** (2.334–2.900 obs) e do SE minúsculo, não de efeito grande: os
r²within ficam entre **0,007 e 0,034** — o modelo explica de 0,7% a 3,4% da variação interna.

O par de **contraste** responde à pergunta que motivou a correção: o β de +0,335 vinha do componente
doméstico? **Nem isso** — o doméstico sozinho dá apenas +0,013. O sinal antigo era da **soma**, que
é produção (r=0,986 com a área plantada); e os componentes são quase **ortogonais entre si**
(r = 0,150 entre exportado e doméstico), ou seja, o *destino* da soja é informação genuinamente
independente da produção — e nenhum dos dois destinos co-move materialmente com a área.

### 3. Bloco C — nenhuma liderança sobrevive à robustez (novo)
Os 3 termos defasados significativos foram reestimados sob **winsorização (1%/99%)** e **log1p**,
no espírito do #41/D14 — o regressando (Δ volume municipal exportado) é ruidoso, e um p<0,05 com
r²within ≈ 0,005 é candidato natural a artefato de outlier:

| Par [termo] | bruto | winsor | log1p | Veredito |
|---|---|---|---|---|
| Soja: exportado × SIDRA [LULC lidera] | −0,369 **\*** | −0,388 (p=0,08) | −0,029 (p=0,77) | **frágil** — some por completo |
| Soja: exportado × agric. LULC [LULC lidera] | −0,846 **\*** | −0,931 (p=0,22) | −0,778 (p=0,09) | **frágil** |
| Boi: exportado × pastagem [infra lidera] | −0,004 **\*** | −0,001 (p=0,64) | +0,003 (p=0,17) | **frágil** |

> **0 de 3** termos defasados sobrevivem às três especificações. E note que os dois de "LULC lidera"
> tinham sinal **negativo** — "plantar mais soja hoje ⇒ exportar menos amanhã" não é mecanismo
> nenhum, é a assinatura de ruído. Sem o Bloco C, esses dois p<0,01 poderiam ter virado uma
> alegação de liderança reversa.

### 4. Veredito
> Em Goiás, na janela observável, a cadeia **exportadora** **não lidera** a expansão do uso da terra
> em direção nenhuma — nenhum termo defasado sobrevive à robustez — e **também não co-move
> materialmente** com ela: o único co-movimento de peso é `exportação ↔ abate`, que é um elo
> mecânico da própria cadeia, não uma relação com a terra. A infraestrutura exportadora é
> **coincidente e fraca**, não pioneira.
>
> Isso é coerente com o veredito recorrente do projeto — **co-evolução sob forças comuns, sem
> precedência temporal limpa** (#34, #37, #42) — e o **reforça**: a evidência que antes parecia
> "co-movimento material" (β=+0,335) era a variável medindo produção. Terceiro canal a não achar
> líder temporal, agora sem o falso positivo.

---

## Como ler as figuras

### `painel_direcoes.png` — a figura-manchete
Três colunas de coeficientes por par (9 pares): **co-movimento contemporâneo** (verde), **infra lidera t−1** (roxo), **LULC lidera t−1** (rosa). Os pontos cheios (p<0,05) concentram-se na coluna do **contemporâneo**; as colunas de defasagem ficam quase todas em ~0. Mostra visualmente que o sinal é de coincidência, não de liderança. **Leia junto com o Bloco C**: os poucos pontos cheios das colunas defasadas são os três termos que a robustez derruba.

![Direções no painel](../../outputs/trase_lulc/painel_direcoes.png)

### `leadlag_agregado.png` — as séries estaduais
Volume **exportado** (normalizado) × uso da terra (normalizado) para soja e boi. As curvas sobem juntas — co-movimento visível — sem defasagem clara de uma sobre a outra. (Desde a correção de jul/2026 a curva da soja é a de exportação de fato, não a do fluxo total.)

---

## Limitações honestas

- **"Trase = fluxo exportador apenas" vale para o BOI, não para a soja** (#27) — foi o erro
  corrigido em jul/2026. Hoje os pares de soja usam `trase_soja_volume_export_t`; **não** use
  `trase_soja_volume_t` (é produção, r=0,986 com a área plantada).
- O co-movimento `boi × abate` — o único material que resta — é **definicional** por dois motivos:
  (i) a exportação é um recorte do abate; (ii) o próprio `abate_bovino_cab` **não é medido no
  município** — é estimado como `(rebanho_muni/rebanho_UF) × abate_UF` com taxa de abate **constante
  por ano** (`estimativa_abate_municipal.py`), de modo que num painel com FE de ano ele é o **rebanho
  reescalado** (r_within-ano ≈ 1,0). Não é medida independente nem evidência de relação com a terra —
  é o mesmo motivo pelo qual o #50 o descartou como comparação circular.
- **Trase mede FLUXO, não capacidade instalada.** Silos, esmagadoras e frigoríficos com SIF
  exigiriam CONAB SISDEP / SIGSIF-MAPA. Esse ângulo — que poderia dar liderança onde o fluxo não dá
  — segue nas coletas pendentes do backlog. **É a ressalva mais importante deste pipeline**: o nulo
  aqui é sobre *fluxo exportador*, não sobre *infraestrutura física*.
- **Janela curta** (soja 19 anos, boi 12 sem 2018) → baixo poder, sobretudo no agregado (Bloco A). O painel recupera poder pelo N municipal, mas o T ainda é curto para defasagens longas.
- **Precedência preditiva, não causalidade** (D16 aplicada). O agregado é diagnóstico.
- **Efeitos minúsculos.** Mesmo os contemporâneos significativos têm r²within ≤ 0,034. A leitura
  correta é "não há relação de peso", não "há uma relação pequena bem medida".

---

## Conexão com a narrativa

Fecha o **Eixo A** do backlog. Reforça, por um terceiro canal (infraestrutura), o veredito de **co-evolução sem precedência** que a narrativa Sul→Norte já sustentava pelos canais de deslocamento (#34) e de drive macro (#37/#42): nenhum dos vetores testados — nem a agricultura do Sul, nem os drivers de mercado, nem a cadeia exportadora — **lidera temporalmente** a expansão. A dissertação ganha o argumento de que a cadeia exportadora é **coincidente**, não pioneira — ela escoa a produção que a fronteira e o gradiente de aptidão organizam.

E ganha um **caso-modelo de autocorreção** no espírito do #40, do #41 e do #42: o achado mais forte
da primeira versão (`β=+0,335`) caiu quando a **premissa sobre o dado** foi verificada em vez de
herdada — a variável não media o que o rótulo dizia. A lição é irmã da D14 (controle o gradiente
antes de atribuir efeito) e da D16 (diagnostique a integração antes de ler precedência), mas numa
camada anterior: **audite o que a variável contém antes de interpretar o coeficiente.** Aqui, uma
correlação de 0,986 entre o "regressor" e o "regressando" bastava para desconfiar — e ninguém tinha
olhado.
