# Auditoria de rótulos de figura — o rótulo é uma afirmação, e ele envelhece

**Decisão D27** (2026-07-28). Governa toda figura **importada de um script** para uma peça de
comunicação (site, dissertação, apresentação). Nasceu de um defeito real encontrado na revisão da
Perna 4 da viz ([#39](../pipelines/39_fronteira_fechando.md); registro em
`Visualizacao/docs/PLANO_DE_CONSTRUCAO.md` §18).

É uma decisão **de processo**, não de análise: não muda nenhum número. Muda o que precisa ser
conferido antes de um número aparecer para alguém.

---

## 1. O problema, em uma frase

Uma figura exportada por um pipeline é uma **citação congelada de uma versão anterior da
análise**. Quando uma auditoria muda a conclusão do pipeline, a prosa é corrigida — é texto, está
no diff, alguém relê. O PNG não: ele só muda se alguém **rodar o script de novo**, e ninguém
lembra de rodar o script por causa de uma frase que mudou.

O resultado é uma peça que **afirma uma coisa no texto e a coisa oposta na figura ao lado**.

## 2. O caso que gerou a regra

A Perna 4 da viz respondia "por que a fronteira desacelerou no Sul?" com a manchete **"não foi a
demanda que acabou — foi a oferta de terra"**. Ao lado, a figura
`outputs/fronteira_fechando/decomposicao_oferta_demanda.png`, importada do #39, com duas barras
rotuladas **"Efeito-OFERTA"** e **"Efeito-DEMANDA"**. No Sul, a barra da *demanda* é a grande:
−0,0047 de −0,0056, ou **83% da freada**.

Ou seja: a página dizia "não foi a demanda" exibindo uma figura em que a demanda explica quase
tudo.

O agravante é o que torna isto uma regra e não um descuido isolado: **o próprio #39 já havia
retratado aquele rótulo.** O §3 do pipeline tem uma seção chamada "Ressalva de rótulo" dizendo,
com todas as letras, que a coluna se chama *efeito-residual* justamente porque **não** é demanda
medida — o hazard capta propensão a converter, atrito de acesso, proteção e troca da fonte de
terra, tudo junto. A prancheta foi corrigida. A figura ficou com o rótulo antigo, e foi a figura
que chegou ao leitor.

Corrigido em três lugares: a figura saiu da página (substituída por SVG inline, com o resíduo em
**cinza** — cinza é a cor do que não foi identificado); o rótulo foi consertado **na origem**, em
`scripts/fronteira_fechando.py`; e o "17% estoque / 83% resíduo" virou fragilidade declarada em
`p4-limites`.

## 3. Por que isto não é acidente — três propriedades do arquivo importado

1. **O rótulo está dentro do binário.** Não é grepável. A varredura de frases banidas do site
   (§7 do plano de construção) passa **em verde** numa página que exibe uma frase banida — porque
   a frase está em pixels, não em texto.
2. **Não aparece na revisão de código.** O `git diff` de um PNG é `Binary files differ`. Nenhuma
   leitura de diff, humana ou automática, vê o que mudou ou o que deixou de mudar.
3. **Só se atualiza por efeito colateral.** A figura muda quando alguém roda o script inteiro —
   e uma auditoria tipicamente corrige a *interpretação* sem tocar no cálculo, logo sem motivo
   aparente para re-rodar.

**Corolário desagradável:** prancheta e figura divergem exatamente **nos pontos onde o trabalho
mais avançou**. Quanto mais auditado o achado, maior a chance de a figura estar velha. As figuras
mais perigosas são as dos pipelines mais trabalhados.

## 4. A regra

Antes de publicar, **toda figura importada de um script** responde:

> **O rótulo — título, eixo, legenda, nome de série — ainda diz o que o pipeline conclui *hoje*,
> ou diz o que ele concluía *antes da última auditoria*?**

Três desfechos aceitáveis, nesta ordem de preferência:

1. **Re-rodar** o script depois de consertar o rótulo na origem (foi o que se fez com o #39 —
   conserta a figura e todas as futuras).
2. **Substituir por figura autorada na peça** (SVG inline), quando a peça precisa de um recorte
   ou de uma ênfase que o pipeline não tem por que produzir.
3. **Manter com ressalva explícita na legenda**, quando a figura está certa mas incompleta.

Desfecho inaceitável: **manter sem revisar**, que é o estado padrão de qualquer figura que
ninguém olhou.

**Regra companheira — a ressalva acompanha a série.** Se a peça acrescentou uma ressalva a uma
série (tracejado, corte de ano, nota), **toda representação daquela série na mesma peça carrega a
ressalva** — inclusive a que veio pronta do pipeline. Foi por violar esta regra que nasceu o caso
2 do §7.

## 5. As três classes de risco

Nem toda figura corre o mesmo risco. O que separa as classes é **onde o rótulo mora** e **quem o
relê**.

| Classe | O que é | Onde mora o rótulo | Revisável no diff? | Risco |
|---|---|---|---|---|
| **A** | Raster importado de script (`.png`/`.webp` de `outputs/`) | dentro do binário | não | **alto** |
| **B** | Figura montada em JS a partir de JSON exportado | rótulo no `.js` (grepável); **categorização** no script de export | parcial | **médio** |
| **C** | SVG inline autorado na própria peça | no mesmo arquivo da prosa | sim | **baixo** |

A classe **B** tem uma armadilha própria, já paga uma vez: o rótulo está visível no JS, mas o
**agrupamento de categorias** está no script que gera o JSON. Foi assim que a classe 21 do
MapBiomas ("Mosaico de Usos") sumiu de um dicionário de grupos e virou censura silenciosa
([bug da classe 21](censo_vs_amostra.md)). Rótulo certo, conteúdo errado.

A migração A → C não é estética: é a decisão de **trazer o rótulo para dentro do diff**. É por
isso que a reforma da viz vem trocando PNG por SVG inline a cada perna revisada.

## 6. Inventário — o que está exposto hoje (28/jul/2026)

### 6.1 `Visualizacao/reforma.html` — 12 figuras

| Figura | Onde | Classe | Origem | Estado |
|---|---|---|---|---|
| mapa GEE, 4 camadas (cobertura/delta/fogo/transições) | Parte 1 | B | export GEE via `timeline.js` | **não auditado** — o ponto é a legenda de classes |
| `marchamap-mapa` | Perna 1 | B | #32/#44 | ✅ revisado na revisão da Perna 1 |
| `marchamap-strip` | Perna 1 | B | #32 | ✅ carrega o corte `ANO_ROTULO_DERIVA = 2019` |
| **`deslocamento_latitude.png`** | Perna 1, l. 553 | **A** | #32 (`centro_massa.py`) | ⚠️ **ABERTO — ver §7** |
| `cinco-medidas` (SVG) | Perna 1 | C | autorado | ✅ |
| `sintese_idade_duas_populacoes.png` | Perna 2, l. 782 | **A** | `Visualizacao/scripts/gerar_grafico_duas_populacoes.py` | ✅ autorado em 28/jul já sob esta regra; títulos descritivos |
| `reserva-painel` ×2 | Perna 2 | B | #28C | ✅ revisados na Perna 2 |
| `assinatura` (SVG) | Perna 3 | C | autorado | ✅ |
| `esquema-espuria` ×2 (SVG) | Perna 3 | C | autorado | ✅ |
| `simetria` (SVG) | Perna 3 | C | autorado | ✅ |
| `decomp` (SVG) | Perna 4 | C | autorado | ✅ substituiu a figura do caso 1 |
| `estoquefig` (SVG) | Perna 4 | C | autorado | ✅ |

**Partes 3 (veredito) e 4 (oficina) não têm figura nenhuma** — `grep "<figure\|<canvas"` retorna
zero depois da linha 1777. (Isto corrige a suspeita inicial de que sobrariam figuras na oficina:
não sobram; o que sobra é a Perna 1.)

Saldo da reforma: **2 figuras de classe A** (uma verificada, uma aberta) contra **8 de classe C**.

### 6.2 `Visualizacao/index.html` — o site **publicado**: 25 figuras, todas classe A

Nenhuma delas passou por esta regra. Inclui `decomposicao_oferta_demanda.png` — ou seja, **o site
no ar neste momento exibe a figura do caso 1**, com o rótulo "Efeito-DEMANDA" que o #39 já
retratou.

Isto não pede uma força-tarefa: pede **a troca**. A reforma remove 23 das 25 por construção
(as figuras não foram migradas, foram substituídas por peças autoradas ou cortadas). Auditar o
`index.html` figura a figura seria trabalho jogado fora — o alvo da auditoria é o
`reforma.html`, e a exposição atual termina no dia da troca.

### 6.3 `outputs/` — 434 PNGs

Este é o número que assusta e **não é o alvo**. A esmagadora maioria é figura de trabalho: serve
para o autor olhar e decidir, não afirma nada a ninguém. Daí o princípio de escopo:

> **Audita-se por exposição, não por inventário.** Uma figura entra na fila da D27 quando é
> **publicada** — site, texto da dissertação, apresentação, parecer. Enquanto vive só em
> `outputs/`, um rótulo velho é um lembrete desatualizado, não uma afirmação falsa.

434 figuras é trabalho inviável e desnecessário. As ~25 que um leitor vê é trabalho de um dia.

## 7. Os casos vivos

**Caso 1 — `decomposicao_oferta_demanda.png` (#39). FECHADO.** Descrito no §2. Rótulo consertado
na origem, figura fora da peça, número que ela escondia (17/83) declarado como fragilidade.

**Caso 2 — `deslocamento_latitude.png` (#32). ABERTO.** Encontrado ao levantar este inventário,
e é a mesma falha em outra roupa. Na Perna 1, a revisão do autor concluiu que a série da
agricultura precisa de ressalva a partir de **2019** por causa da deriva do Mosaico
([D25/D26](tratamento_deriva_mosaico.md)) — e o interativo passou a marcar isso
(`ANO_ROTULO_DERIVA` em `marcha-mapa.js`, com nota em texto). O PNG que fica **imediatamente
abaixo, na mesma tela**, plota a *mesma série* em linha cheia, período inteiro, legenda
"Agricultura", sem ressalva alguma.

Nenhum rótulo está errado aqui — os títulos do `fig_latitude` são descritivos. O que falha é a
**regra companheira do §4**: a peça acrescentou uma ressalva à série e uma das duas
representações não a recebeu. O leitor vê a linha ressalvada e, dois centímetros abaixo, a mesma
linha sem ressalva.

**E o rastro é mais fundo do que a tela.** A seção "Como ler as figuras" do próprio
[#32](../pipelines/32_centro_massa.md) descreve esta figura dizendo que nela se enxerga "a
desaceleração do Ato III (a linha magenta achata)" — que é **precisamente o efeito que a deriva
do rótulo produz por artefato**, e o mesmo documento, algumas seções acima, tem a régua-espelho
que mede o viés. Ou seja: o defeito não nasceu na visualização, nasceu na leitura da figura
dentro do pipeline, e a peça herdou. Ressalva adicionada ao #32 em 28/jul; a figura continua
pendente.

Isso acrescenta um alvo ao protocolo do §8: **a seção "como ler esta figura" do pipeline é
rótulo também** — é onde a interpretação mora quando não cabe no eixo, e envelhece igual.

Três saídas possíveis, a decidir: (a) propagar o corte para o `fig_latitude` e re-rodar; (b)
trocar o PNG pela figura de robustez que o próprio #32 já produz
(`outputs/centro_massa/robustez_deriva_regua.png`, feita para exatamente esta pergunta); (c)
remover o PNG, já que o interativo acima cobre a mesma informação — foi o desfecho na Perna 3
com o `veredito.png`.

## 8. O protocolo da revisão pesada

Fica registrado para quando for a hora — **não é pré-requisito da troca**, com a exceção do §9.
A ordem importa: cada passo só faz sentido se o anterior passou.

1. **Congelar a lista de exposição.** `grep` de `<img>`, `<figure>`, `<canvas>` e dos caminhos de
   imagem montados em JS, na peça publicada. Hoje: 12 no `reforma.html`.
2. **Classificar** cada uma em A/B/C (§5). Só A e B seguem.
3. **Para cada A e B, abrir o script que a gera** e ler **só os rótulos**: título, eixos, legenda,
   nomes de série, anotações. Comparar com a seção de conclusão do `.md` do pipeline — não com a
   memória do que o pipeline fazia.
3b. **Ler também a seção "como ler esta figura" do `.md` do pipeline**, que é rótulo estendido:
   é onde a interpretação mora quando não cabe no eixo, e envelhece igual. Foi lá que o caso 2 do
   §7 estava desde antes de chegar ao site.
4. **Para cada B, abrir também o script de export do JSON** e conferir o *agrupamento de
   categorias*, não só os rótulos (a armadilha do §5).
5. **Conferir a legenda da peça contra a figura**, não contra o texto: legenda que descreve uma
   figura que mudou é o mesmo defeito com outro dono.
6. **Rodar a régua companheira**: para cada série que a peça ressalvou em algum lugar, verificar
   que **todas** as suas representações carregam a ressalva.
7. **Registrar o veredito por figura** numa tabela como a do §6.1 — inclusive os ✅, porque o
   valor da tabela é dizer *o que já foi olhado*.

**Varredura irmã, que não é esta e não deve ser confundida com ela: número na tela × CSV.** A
revisão da Perna 4 fez isso *ad hoc* e achou três erros (janela `+93%/+14%` que era 2013→2021 e
não 2013–2023; "97% desprotegido" quando a régua melhor do #46 dá 94,3%; carbono sem a
cronologia que a perna precisava). São defeitos de **transcrição**, não de rótulo, e pedem outro
método: abrir o CSV e conferir o número, um a um. Vale programar, e vale programar **separado** —
misturar as duas varreduras faz as duas ficarem pela metade.

## 9. O que entra na troca e o que não entra

- **Entra (bloqueia):** fechar o **caso 2** do §7, porque é uma contradição visível na mesma
  tela, numa perna já lida pelo autor.
- **Entra (bloqueia):** conferir a **legenda de classes do mapa da Parte 1** (linha 1 do §6.1),
  única figura de classe B ainda não auditada — e a classe do bug conhecido é justamente uma
  categoria de legenda.
- **Não entra:** auditar o `index.html` (§6.2) — a troca o aposenta.
- **Não entra:** auditar `outputs/` (§6.3) — audita-se por exposição.
- **Não entra:** a varredura número × CSV do §8 — é outro método, outro dia.

## 10. O que esta regra não cobre

A D27 verifica se **o rótulo está de acordo com o pipeline**. Ela **não** verifica se o pipeline
está certo. Uma figura pode passar na D27 com nota máxima e estar errada, porque o cálculo por
trás dela está errado — é o que a auditoria de pipelines faz, e é outro trabalho.

Também não cobre **ausência**: a figura que deveria existir e não existe (o beat que faltava na
Perna 4 — `pasto→(agric∪mosaico)` +51% contra `veg→pasto` −49% — estava nos dados desde a
auditoria da D26 e nunca tinha chegado à tela). Nenhuma varredura acha o que não está lá; isso
só a leitura de cima a baixo acha, que é o que a Fase D é.

---

## Ver também

- `Visualizacao/docs/PLANO_DE_CONSTRUCAO.md` §18 — o registro da revisão da Perna 4.
- [tratamento_deriva_mosaico.md](tratamento_deriva_mosaico.md) — D25/D26, origem da ressalva do
  caso 2.
- [censo_vs_amostra.md](censo_vs_amostra.md) — o bug da classe 21, a armadilha da classe B.
- [#39](../pipelines/39_fronteira_fechando.md) §3 "Ressalva de rótulo" — o texto que estava certo
  enquanto a figura estava errada.
