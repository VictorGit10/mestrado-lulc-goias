# Tratamento da deriva do Mosaico em análises — bracket `[agric, agric∪mosaico]` + âncora SIDRA

**Decisão D26** (2026-07-23). Governa como qualquer análise deve lidar com a deriva do
Mosaico documentada na [#28D / D25](../pipelines/28D_deriva_mosaico.md). Irmã de D25
(diagnóstico da deriva), D24 (contrato de peso) e D19 (incerteza por bootstrap).

---

## 1. O problema, em uma frase

No fim da série MapBiomas (Coleção 10.1, agudo em 2022–2024), a conversão
`pastagem → agricultura` é **reetiquetada** como classe **21 "Mosaico de Usos"**. Em
consequência, o **estoque/fluxo de agricultura subconta** a lavoura recente, e qualquer
medida que dependa da classe "Agricultura" (ou da transição com destino = agricultura)
numa janela que toca 2020–2024 fica distorcida. A soja de campo não parou — a SIDRA
registra **+38% (2020–24)**; foi o *rótulo* que mudou.

## 2. A tentação — e por que `agric∪mosaico` NÃO é uma "correção"

Somar `agricultura + mosaico` parece "desfazer" a reetiquetagem. **Não é uma correção
no sentido de recuperar o valor verdadeiro**, porque tratar a união como "a agricultura
real" assume que **100% do Mosaico é agricultura mal-rotulada**. Isso é falso por três
motivos, cada um demonstrável com os próprios dados:

1. **A classe 21 é genuinamente ambígua, não só artefato.** Ela contém (a) sistemas
   **integrados lavoura-pecuária (ILP) reais**; (b) mosaicos finos demais para separar a
   30 m; (c) a soja nova rerroteada (o que se quer recuperar); e (d) **mosaico antigo e
   estável**. A união joga (a), (b) e (d) dentro de "agricultura" → **superconta**.
2. **A união inflaciona a série inteira, não só a cauda contaminada.** O Mosaico existe
   desde ~2010 e ficou **~flat em 1,9–2,1 Mha até 2019**, saltando **+1,53 Mha em
   2020–24**. Dos **3,59 Mha** de Mosaico em 2024, só ~1,5 é candidato à deriva; os outros
   ~2,0 são mosaico velho que nada tem a ver com o artefato.
3. **Não é demonstrado — é sugestivo.** A base é (a) o balanço de massa (mosaico +1,5 ≈
   soja +1,5), que é **quase tautológico** e **não discrimina artefato × ILP**; e (b) a
   correlação espacial mosaico×soja-SIDRA por AMC (**r = 0,84**), forte mas correlacional.
   O que *demonstraria* — rastreio pixel `pasto→21`, comparação com a Coleção 9 — **não
   foi rodado** (ver [28D §9](../pipelines/28D_deriva_mosaico.md)).

## 3. O enquadramento correto: **bracket**, não correção

| Régua | Papel | Viés |
|---|---|---|
| `agricultura` (só) | **limite INFERIOR** | subconta (a soja rerroteada some) |
| `agricultura ∪ mosaico` | **limite SUPERIOR** | superconta (ILP + mosaico antigo entram) |

A verdade está **dentro do intervalo**. A regra operacional:

> **Reportar o intervalo `[agric, agric∪mosaico]`, nunca um ponto. Uma conclusão só é
> robusta à deriva se sobrevive nos DOIS extremos.** Se ela muda de sinal/significância
> entre um extremo e outro, então depende da convenção de classe — e isso precisa ser
> dito, não escondido.

## 4. A pergunta mais grossa — por que a união ainda é honesta

`agric∪mosaico` **não é uma agricultura mal-medida; é a resposta exata a uma pergunta
diferente e mais grossa**:

- **Pergunta fina** (só `agricultura`): *"quanta terra virou lavoura pura?"* — é a que a
  deriva corrompe.
- **Pergunta grossa** (`agric∪mosaico`): *"quanta terra **saiu de pasto puro para
  lavoura-ou-uso-misto**?"* — **robusta à reetiquetagem por construção**, porque a
  reetiquetagem é *interna* à união (mover um pixel de "Agricultura" para "Mosaico" não
  muda a soma).

As duas perguntas são legítimas. **O erro é passar uma pela outra.** O custo da pergunta
grossa é misturar conversão produtiva (soja) com integração real (ILP) e com perda de
legibilidade do classificador — ela ganha robustez trocando por especificidade.

## 5. A hierarquia: a âncora é a SIDRA, não o bracket

O bracket é uma ferramenta de *contenção do artefato*, não a melhor evidência disponível.
A ordem de preferência:

1. **Fonte imune direta (SIDRA / SICOR / Contas Regionais).** É o **instrumento superior**
   — outra medição, independente do classificador, não um "desfazer" de artefato. Onde ela
   alcança (soja plantada, rebanho, crédito, valor), **é ela que responde**. Ex.: a soja
   SIDRA quebra em 2020 sozinha (delta F=7,8, p=0,008; expansão ×3) — fecha a periodização
   **sem tocar o MapBiomas**.
2. **Bracket `[agric, agric∪mosaico]`.** Para o que a SIDRA não mede diretamente (centroide
   pixel-a-pixel, quantidades de *cobertura*). Contém o tamanho máximo do artefato.
3. **Demonstração.** O rastreio pixel `pasto→21` **com idade já está feito** (cubo
   reprocessado, §9) e estabelece a **co-localização** (mesmos pixels, mesma janela). O que
   **ainda falta** para uma **correção de ponto** — estimar a *fração* do Mosaico que é soja
   rerroteada e somar só essa fração, em vez do bracket grosso — é **discriminar artefato ×
   ILP real**, e isso exige a **Coleção 9** (borda móvel). É a única dívida em aberto.

## 6. Protocolo por tipo de análise

| Tipo de análise | Como tratar a deriva |
|---|---|
| **Quebra / delta** (#29) | Bracket é bom aqui: o Mosaico é ~flat pré-2020, então ele quase só perturba a cauda. Sempre com **SIDRA de âncora independente**. |
| **Nível / ponto** (centroide #32/#44) | Bracket obrigatório; `agric∪mosaico` só como **teto**. Reportar o intervalo, nunca um ponto. |
| **Inferencial** (regressão #49) | Bracketar o regressor/regressando exposto; usar Δ(soja SIDRA) como **âncora imune**. É teste de sensibilidade, não correção. |
| **Transições / mecanismo** (#40, #12/#19) | Truncar em ~2019; para 2020–24, redefinir o evento como `pasto→(agric∪mosaico)` (a pergunta grossa) e marcar como provisório. |
| **Estoque de vegetação nativa** | **Imune** — colunas próprias, não drenadas pelo Mosaico. Nada a fazer. |

## 7. Aplicação a #49 e #40 (plano — **executado**, vereditos no §9)

### #49 — painel espacial dinâmico (inferencial)
Modelos `M1: Δagric ~ ΔVA` (2003–21) e `M3: Δpasto ~ Δagric` (1986–2024) usam
`agricultura_delta`, exposto. `M2: Δpasto ~ ΔSICOR + ΔVA` tem regressores imunes.

- **M1 (intensificação).** Rodar o regressando em **três réguas** — `agric` (inferior),
  `agric∪mosaico` (superior) e **Δ(soja SIDRA)** (âncora imune; a soja domina o lump, #44)
  — mais uma variante com **janela truncada em 2019**. β robusto ⇔ sinal e significância
  sobrevivem nas três + no truncado.
- **M3 (substituição local).** Bracketar o **regressor** `Δagric` (inferior) ↔
  `Δ(agric∪mosaico)` (superior), com **Δ(soja SIDRA)** de âncora; `y = pastagem` é
  largamente real. Comparar janela `1986–2024` × `1986–2019`. **Hipótese direta:** o
  `Δagric` congelado na cauda **atenua** o β (a substituição *parece* mais fraca); as
  réguas imune/superior devem devolver um β mais forte. Reportar o **intervalo de β**.
- **M2.** Regressores imunes, `y` ~real → prioridade baixa; nota de que a cauda do pasto é
  levemente inflada pela reetiquetagem.

### #40 — duas lógicas da pastagem (mecanismo, pixel-level)
Analisa mecanismos de `pasto→agricultura` (janela 2010–2024) sobre a tabela de eventos do
#28 — a SIDRA **não** ancora "mecanismo". Plano:

- **Bracket via evento**: recomputar o mix de mecanismos redefinindo a conversão como
  **`pasto→(agric∪mosaico)`** (a pergunta grossa: "a fase de pasto terminou?") ao lado do
  `pasto→agric` original.
- **Janela**: a análise **pré-2019 é limpa**; a janela `2016–2024` é a mais exposta.
  Reportar o mix terminal como **intervalo** `[pasto→agric, pasto→(agric∪mosaico)]` e
  **provisório**, não como número fechado.
- **Sanity SIDRA**: o total `pasto→(agric∪mosaico)` deve acompanhar a expansão de soja
  SIDRA no agregado (checagem de plausibilidade, não identificação).

## 8. Resumo (o que citar na banca)

- `agric∪mosaico` **não é uma correção** — é o **limite superior** de um intervalo cujo
  limite inferior é `agric` sozinha; a verdade está dentro, e conclusões robustas
  sobrevivem nos dois extremos.
- A união responde honestamente a uma **pergunta mais grossa** ("saiu de pasto puro para
  lavoura-ou-uso-misto"), não à pergunta fina ("virou lavoura pura").
- A **melhor evidência** dos anos terminais é a **SIDRA** (imune), não o bracket.
- A **co-localização** já está demonstrada pixel-a-pixel (cubo reprocessado, §9); o que
  falta para uma correção de *ponto* é **discriminar artefato × ILP** e assim estimar a
  **fração rerroteada** — isso exige a **Coleção 9** (borda móvel, §9 do #28D).

## 9. Alcance auditado — veredito por pipeline (varredura fechada, 23/jul/2026)

O cubo foi reprocessado com destino=Mosaico (`processa_cubo_idade_destinos.py` →
`pastagem_conversao_destinos.parquet`), fechando a demonstração e os brackets-por-evento.
Verdicts consolidados:

| pipeline / medida | canal de exposição | veredito | evidência-chave |
|---|---|---|---|
| **#12/#19/#28** | — (fonte do artefato) | — | reetiquetagem `pasto→agric` → `pasto→Mosaico` |
| **#32** centro de massa | estoque `agricultura` | **exposto, robusto** | bracket + SIDRA; viés +10 km; gradiente e marcha de 40a intactos |
| **#44** desagregado | soja-raster | **exposto, robusto** (+achado) | raster×SIDRA em **sentidos opostos** no Ato III (−7 vs +8 km) |
| **#50** econômico | crédito/valor | **imune** | SICOR/VA/PIB não passam pelo classificador |
| **#29** fronteira 2020 | `Δagricultura` | **real; rótulo invertido** | sup-F **fortalece** sob correção (F 21,5→34,1); soja SIDRA quebra em 2020 sozinha |
| **#29c** KL/TV | matriz de 6 classes | **contaminado** | não rastreia Mosaico → não é corroboração independente |
| **#49 M3** substituição | `Δagric` (regressor) | **exposto, robusto** | β<0 nas 3 réguas; deriva **subestimava** (−0,49→−0,63) |
| **#49 M1** intensificação | `Δagric` (regressando) | **frágil** | bracket cruza zero; âncora SIDRA dá **sinal oposto** |
| **#40** gradiente idade×lat | `pasto→agric` | **REFUTADO** | bracket-por-evento: sob a união ρ≈0 (ns) nas 3 janelas |
| **#28C** gradiente idade×lat | `pasto→agric` | **artefato** | união: amplitude Sul→Norte 7a → 2a |
| **#28C** bimodalidade/coexistência | `pasto→agric` | **robusto** | união: 5/5 regiões, 10/10 células; η²(região) 3,7→0,5% |
| **#39** fronteira fechando | oferta de Cerrado | **imune** | mede veg→pasto, não `pasto→agric` |
| **#48** validação PRODES | veg→antrópico | **imune** | perda de veg estável 2017–24 (a deriva é antrópico→antrópico) |
| **#22 / #24** | `Δagric` | **cobertos pelo #49** | mesmos canais M1/M3; 1ª-diff (D7) desarma o grosso |

**Duas afirmações que a deriva contaminava e foram isoladas:** (1) o *congelamento recente
da agricultura* (na verdade acelera — SIDRA +38%); (2) o *gradiente latitudinal na idade do
pasto* (young-Sul/old-Norte — artefato do rótulo "agricultura", cai no #40 **e** no #28C sob
a união). **O que sobrevive e sai reforçado:** a marcha dos **centroides** (#32/#44), a
**fronteira de 2020** (fonte imune), e a **coexistência bimodal** dos dois mecanismos de
conversão modulada pelo **tempo** (Ato III), não pela latitude. Único item em aberto:
artefato × ILP real (Coleção 9), que **não** é pré-requisito da dissertação.

## Ver também
- [28D — deriva do Mosaico / D25](../pipelines/28D_deriva_mosaico.md) (§4-C sobre a união; §8 demonstração pixel; §9 Coleção 9)
- [#32 — robustez à deriva (bracket no centroide)](../pipelines/32_centro_massa.md)
- [#44 — raster×SIDRA em sentidos opostos no Ato III](../pipelines/44_centro_massa_desagregado.md)
- [#29 — a fronteira de 2020 é real (SIDRA confirma; KL/TV contaminado)](../pipelines/29_triangulacao_periodizacao.md)
- [#49 — M3 robusto, M1 frágil (bracket inferencial)](../pipelines/49_painel_espacial_dinamico.md)
- [#40 — gradiente refutado pelo bracket-por-evento](../pipelines/40_duas_logicas_pastagem.md)
- [#28C — bimodalidade robusta, gradiente artefato](../pipelines/28C_bimodalidade_regional.md)
- Scripts: `centro_massa_deriva_check.py`, `periodizacao_robustez_deriva.py`,
  `painel_espacial_dinamico_deriva.py`, `duas_logicas_deriva_check.py`,
  `processa_cubo_idade_destinos.py`, `duas_logicas_bracket_evento.py`,
  `bimodalidade_regional_uniao.py`; e `robustez_deriva()` em `centro_massa.py` (§6).
