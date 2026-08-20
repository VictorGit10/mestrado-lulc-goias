# Qualificação — texto ABNT (abnTeX2)

Documento de qualificação do mestrado (PPGCIAMB/UFG), gerado a partir do
material da visualização (`Visualizacao/index.html`) e de `Textos/`.

## Estrutura

```
main.tex          — preâmbulo, dados da capa, ordem dos capítulos
pre/              — resumo, abstract e lista de abreviaturas e siglas
cap/              — um .tex por capítulo (00 = memorial, 01–06 = texto)
ref/referencias.bib — bibliografia (ABNT autor-data via abntex2cite [alf])
fig/              — figuras + o gerador que as produz (ver abaixo)
compilar.ps1      — pdflatex → bibtex → pdflatex ×2 → main.pdf
```

## Figuras

```powershell
python fig\gerar_figuras.py            # todas
python fig\gerar_figuras.py sankey     # só uma
```

`fig/estilo.py` fixa a geometria de página e `fig/gerar_figuras.py` traz uma
função por vista. **As figuras não são reaproveitadas de `outputs/`**: são
redesenhadas a partir dos mesmos CSV/parquet que os pipelines gravaram.

A razão é geométrica, não de resolução. As figuras de `outputs/` têm pixels de
sobra (`trajetorias.png` = 1803 px ≈ 380 dpi a 12 cm), mas nascem com `figsize`
de 9×5 a 12×12 polegadas; reduzidas à mancha ABNT de 16 cm (6,3 pol), um rótulo
de 10 pt vira ~5 pt. Aqui a largura já é 16 cm, o corpo é 9 pt e a escala de
inclusão é 1,0. Redesenhar também permite (a) tirar o título embutido, que na
ABNT é a `\caption`, e (b) aplicar ressalvas que o PNG de tela não carrega.

Saída em PDF vetorial, exceto o painel de mapas (raster, PNG a 300 dpi).
Prévias em PNG vão para o scratchpad, fora do repositório.

| Figura | Arquivo | Fonte de dados |
|---|---|---|
| 1 — área de estudo | `cap3_localizacao.pdf` | malhas IBGE via `geobr`, cache em `data/processed/_geo_*.gpkg` |
| 2 — cobertura em 5 cortes | `cap4_painel_cobertura.png` | `outputs/mapas_gee/_raw_7c/raw_*.png` (#10) |
| 3 — Sankey 1985↔2024 | `cap4_sankey.pdf` | `transicoes_cubo_goias.csv` (#12B) |
| 4 — centro de massa | `cap4_centro_massa.pdf` | `centro_massa_anual.csv` + `centro_massa_banda_lat.csv` (#32) |
| 5 — idade da pastagem | `cap4_idade_pastagem.pdf` | `pastagem_idade_censo.parquet` (#28C) |
| 6 — doze especificações | `cap4_teste_espacial.pdf` | `deslocamento_bracket_slx.csv` (#49) |
| 7 — corrida entre exposições | `cap4_horse_race.pdf` | `drive_horse_race_latitude.csv` (#56) |
| 8 — teto de oferta | `cap4_fronteira_oferta.pdf` | `fronteira_decomposicao.csv`, `fronteira_regional.csv` (#39) |

**Vegetação natural: 16,96 × 17,65 Mha — resolvido por declaração (13/ago).**
Não é divergência de dado: é a mesma medida sob duas convenções de classe. A
Tabela do balanço (painel, #25) conta **campo alagado** como natural; o
agrupamento em sete classes do cubo (#12B) o põe em "Outros". A diferença é
exatamente 0,70 Mha em 1985. Não se regagrupou o cubo de propósito — mover a
classe 11 mexeria nos fluxos-manchete (4,10 / 2,72 / 1,29 Mha), que são
auditados e citados no texto. Em vez disso: (a) a Tabela ganhou **nota de
rodapé** que declara a composição e reconcilia os dois números; (b) o bloco da
Figura 3 passou a se chamar **"Outros (inclui campo alagado)"**, o que localiza
a diferença dentro da própria figura; (c) as legendas de ambas apontam uma para
a outra. A Tabela também ganhou linha de fonte, que não tinha.

### Cartografia (13/ago)

Os três mapas (Figuras 1, 2 e 4) têm **rosa-dos-ventos e régua de escala**.
Ambas vêm de `scripts/_cartografia.py`, o módulo que os mapas de `outputs/` já
usam — a cartografia da dissertação inteira fica igual. `estilo.py` só
redimensiona: aquele módulo foi calibrado para figuras de tela de 10–12
polegadas, e estes painéis têm 2 a 3 (o "N" é recomposto depois porque o módulo
o escala junto com a rosa, e a 0,45 sairia com 5 pt).

**Projeção.** Tudo em **EPSG:5880** (SIRGAS 2000 / Policônica do Brasil), o CRS
métrico que o projeto já adota. Desenhar em graus exigiria corrigir o aspecto
por cos(latitude), o que só vale numa latitude de referência: tolerável em Goiás
(±1,7% entre 12°S e 19°S), ruim no painel do Brasil, que atravessa 40°.

Os rasters do GEE são **plate carrée cru** — a razão de pixels (1,0333) é igual
à razão de graus (1,0335), então exibi-los a 1:1 esticava Goiás. Agora a imagem
é ancorada no *bounding box* métrico do estado, o que dá o aspecto correto
(1,0243) e o metro-por-pixel (387,2 m) que a régua usa.

⚠️ **Armadilha de ordem, encontrada e corrigida.** `adicionar_escala` dimensiona
a barra a partir da largura do eixo **em pixels**, medida na hora da chamada, e
depois a congela em pontos. Chamada antes do `tight_layout()`, a barra sai fora
de escala — aqui deu **−17,5%**, porque o layout alarga o eixo de 726 px para
880 px. Use `pronta_para_cartografia(fig)` (faz `tight_layout` + `draw`) e só
então chame `escala`/`norte`. As quatro réguas foram conferidas depois disso e
medem **0,00% de erro** contra a largura real de Goiás (793 km).

Barras padronizadas em **200 km** nos três mapas de Goiás e **1000 km** no
painel do Brasil. No painel de cobertura, régua e rosa aparecem **uma vez** e
valem para os cinco recortes, que compartilham projeção, escala e orientação;
repeti-las cinco vezes só somaria ruído. A legenda declara isso.

**D27 aplicada.** Duas figuras carregam ressalva na própria imagem, não só na
legenda: a série da agricultura na Figura 4 é **pontilhada a partir de 2019**
(`ANO_ROTULO_DERIVA`), o que fecha o caso 2 de `auditoria_de_figuras.md` §7 —
aberto desde 28/jul porque o PNG plotava a série cheia ao lado de um
interativo que a cortava; e a Figura 7 diz na face que **a parcela residual
não é demanda medida** (caso 1).

**Dado novo persistido.** A faixa de IC da latitude ano a ano era calculada em
memória pelo `#32` e nunca gravada. Agora vive em
`data/processed/centro_massa_banda_lat.csv` (bootstrap B=2000, semente 42);
o recálculo reproduz exatamente os ΔNorte da Tabela dos centros de massa
(65,24 / 77,64 / 66,88 / 7,55 km).

## Como compilar

```powershell
.\compilar.ps1
```

Requer MiKTeX (instalado em ago/2026 via `winget install MiKTeX.MiKTeX`;
binários em `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64` — sessões de
terminal abertas antes da instalação precisam prefixar esse caminho no PATH).
Pacotes faltantes são baixados automaticamente na primeira compilação.

## Estado (13/ago/2026)

**Em prosa (redigidos e revisados em conversa com o autor):**

- `cap/00_apresentacao.tex` — **Memorial** (1ª pessoa, 3 blocos: trajetória /
  percurso do mestrado / método e IA). Fatos da entrevista de 11/ago + Lattes.
  Revisado: nome atual do LAPIG é "Laboratório de Sensoriamento Remoto e
  Geoprocessamento" (o lab foi renomeado); frase final reescrita a pedido
  (brilho contido).
- `cap/01_introducao.tex` — **Introdução** (contexto/problema, pergunta/objeto,
  justificativa, objetivos, organização). Aguardando validação do autor:
  (a) o parágrafo de implicação de política ("conter a lavoura conteria a
  fronteira…"); (b) o parágrafo de produtos do mestrado profissional
  (pipelines + visualização) — alinhar à definição formal do programa se houver.
- `cap/02_referencial.tex` — **Referencial teórico**. **Reescrito em 15/ago/2026**
  e **revarrido em 16/ago** (ver as duas seções abaixo; a segunda varredura achou
  3 defeitos + 1 lacuna que a primeira não olhava). Estrutura atual: 2.1 estatuto +
  como as fontes foram reunidas (declara a **regra da fonte conferida**);
  2.2 tese em quatro cláusulas, com o grau de estabelecimento de cada uma;
  2.3 as sete subseções de fontes conferidas; 2.4 origem dos métodos
  descritivos; 2.5 lista de leitura; 2.6 síntese + quadro.
  Fonte: `Textos/referencia/referencial_marcha.md` + os PDFs de `ref/pdf/`.
- `cap/03_metodologia.tex` — **Metodologia** (12 seções: área de estudo,
  fontes, AMC, painel/D7, periodização, instrumental por frente, réguas de
  robustez, decisões críticas, reprodutibilidade, IA, limitações). Fontes:
  Parte 3 do `guia_de_leitura.md` + `Textos/metodologia/` + docs de pipelines.
  Duas tabelas próprias (mesorregiões; fontes × cobertura × papel) e a
  equação do 2FE. `Ehrl2017` entrou no `.bib` (dados conferidos em
  `metodologia/areas_minimas_comparaveis.md`). Pendências declaradas no
  `\notaguia` do topo: (a) métodos citados por
  epônimo — Newey-West, Quandt-Andrews, Rodionov, Toda-Yamamoto,
  Benjamini-Hochberg, Weiszfeld, Yuill, inferência shift-share — listados no
  fim do `.bib` para conferência; (b) citação formal da Coleção 10.1.
  O **mapa de localização** entrou (Figura 1), com a malha de mesorregiões de
  2017 — a mesma que a análise usa (D6), e não a de 2020.

- `cap/04_resultados.tex` — **Resultados preliminares** (6 seções: três atos +
  balanço de 40 anos; Perna 1 marcha; Perna 2 mecanismo; Perna 3 deslocamento
  e drive comum; Perna 4 teto de oferta; o que não se afirma + 4 resultados
  superados). Fonte: Partes 1–3 do `Visualizacao/index.html` (números já
  auditados contra CSV) + Parte 4 do `guia_de_leitura.md`. 5 tabelas próprias
  (quebras, balanço, centros de massa c/ IC, superados). Calibragem aplicada:
  iLUC nunca "refutado"; drive comum "corroborante, não estabelecido" (p
  0,07–0,13, e os p de 0,026/0,031 explicitamente proibidos); "convertível"
  = exposição, não disponibilidade; Ato III = sinal inicial.
  **Figuras inseridas (13/ago):** os 6 marcadores viraram as Figuras 2–7
  (ver a seção "Figuras" acima).
  ⚠️ O `guia_de_leitura.md` (linha ~1030) ainda tem a frase proibida "iLUC
  testada e **refutada**" — é resíduo pré-28/jul, não seguir; a viz está certa.

  ✅ **Perna 2 recalibrada para o censo completo (13/ago).** Decisão do autor:
  uma régua só, o censo. Três correções, todas com o número recomputado do
  `pastagem_idade_censo.parquet`:
  1. *"μ ≈ 23 anos"* da população velha → **μ ≈ 16** (σ 7,5; 67% da massa).
     O 22–23 vinha das **janelas deslizantes**
     (`idade_pastagem_gmm_sensibilidade.csv`, 2016–24: μ₂=22,5), emparelhado
     com σ₁=1,6 que é do censo — a frase misturava duas réguas.
     ⚠️ **O `guia_de_leitura.md` (l. 1115) NÃO está errado**: ele diz
     "μ₂≈21-23a *em toda janela testada*", com o qualificador. O defeito
     nasceu na transposição para o capítulo, que perdeu o "janela".
     O parágrafo ganhou também o ajuste de 1 componente (μ ≈ 12) explicitado,
     que é o que estabelece a segunda população.
  2. *"Pasto de trinta e três anos quase sempre veio de vegetação natural"* →
     aos 30+ anos a lavoura anterior é **1%**, e o restante divide-se entre
     vegetação natural (46,8%) e **Mosaico (49,8%)**. O trecho passou a
     liderar pelas **medianas por origem** (lavoura 5a × vegetação natural
     13a), que não dependem de ajuste, e a afirmar o **contraste 45% × 1%**
     em vez da atribuição por pixel. Ressalva nova e explícita: metade da
     origem do pasto velho é indeterminada, porque Mosaico é justamente a
     classe em que o classificador não separou usos.
  3. O exemplo de truncamento à esquerda usava "pasto de vinte e dois anos →
     2007"; virou "dezesseis anos → 2001", coerente com o modo do censo.

  A Figura 5(b) passou a estampar as três medianas, para que a figura sustente
  o número que o texto lidera.

- `cap/05_discussao.tex` — **Discussão** (7 seções): (5.1) fronteira, renda
  da terra e a **transição truncada** — o Sul cumpre a primeira metade da
  previsão de Mather/Rudel (estabilização) e não a segunda (não há
  regeneração líquida; o fluxo reverso é oscilação de classificador);
  (5.2) o nulo do iLUC como **previsão do arcabouço** de teleacoplamento, não
  anomalia; (5.3) divisão de trabalho com Richards (a literatura carrega o
  nível, a tese a geografia) + o que levantaria o teto de ~38 realizações;
  (5.4) espelho MATOPIBA — o ganho é metodológico (dois regimes sob a mesma
  régua) e o Sul **não** é "o futuro do MATOPIBA"; (5.5) implicações
  ambientais (exposição, proteção fora do caminho, carbono não proporcional
  à área, IFDM); (5.6) política + a recomendação operacional de monitoramento
  (não usar a classe "Agricultura" isolada em janela que toque 2020–24);
  (5.7) alcance e limites, com **tabela nova** grau de estabelecimento ×
  o que elevaria cada frente.

**Esqueleto anotado (notas cinzas `\notaguia` dizem o que entra e de onde):**

- `cap/06_cronograma.tex` — **PRÓXIMO PASSO** (a preencher com o orientador).

### Reestruturação do cap. 2 (15/ago/2026)

Auditoria fonte a fonte do referencial (texto integral dos 19 PDFs extraído e
grepado) seguida de reescrita **estrutural**, a pedido do autor. O diagnóstico
não foi uma lista de erros: era o capítulo permitir a classe do erro — citação
não conferida reaparecendo como certeza, apesar da instrução repetida.

**A regra, agora declarada no §2.1 e no cabeçalho do `.bib`:** só entra no corpo
do texto a obra cujo **texto integral foi obtido e conferido**. O que o
levantamento apontou e não foi lido vive na lista de leitura do §2.5, não
sustenta afirmação e **não figura nas referências**. Três exceções, nominais:
Richards (lido em *working paper*), Lefever e Yuill (atribuição de método).
O capítulo passou a declarar que a origem das fontes é um **levantamento
bibliográfico primário**, distinto da revisão sistemática do cap. 6.

**Defeitos de conteúdo corrigidos** (todos verificados no PDF, não supostos):

1. **von Thünen não prevê ordenação por aptidão.** O cap. 2 derivava o gradiente
   de aptidão do modelo de localização. Angelsen (2007, p. 5) assume, "como von
   Thünen", a **planície homogênea**; ordenar por qualidade da terra é
   ricardiano, e é o próprio Angelsen quem faz a ponte (p. 6, "no mundo
   ricardiano"). Agravante: a definição usada era tradução do abstract de
   Angelsen creditada a von Thünen (1826), obra não lida. Reescrito para a
   versão estendida, com as duas tradições nomeadas; von Thünen e Ricardo foram
   para o §2.5. O cap. 5 dizia "ricardiana" enquanto o cap. 2 dizia von Thünen —
   alinhados.
2. **"Três fases" da transição florestal não estava em nenhuma das duas fontes.**
   Rudel (2005, p. 23) define pelo par (a queda cessa **e** a recuperação
   começa) e não dá sequência; Mather **não foi lido**. A única sequência
   conferida é a de Angelsen (2007, p. 3), com **quatro** estágios, que separa
   estabilização (3º) de reflorestamento (4º). Fundir os dois fazia a Perna 4
   reportar como falha do arcabouço o que é o 3º estágio. Reescrito; **Mather
   saiu das referências**. Registrado também o horizonte: a estabilização do Sul
   tem **cinco anos** (desde 2019) e nenhuma formulação fixa quanto tempo separa
   um estágio do outro — sequência inacabada e truncada não são separáveis aqui.
3. **Arima (2011) é precedente do canal DISTAL, não da adjacência.** A novidade
   declarada pelos autores é a matriz que liga municípios a centenas de km. O
   texto o apresentava só como "mesmo nível municipal", o que fazia o nulo
   parecer contradição de um achado consolidado. Corrigido no cap. 2 e no cap. 5.
4. **O quadro-síntese afirmava conferência que não houve.** A coluna "Âncoras
   conferidas" e a linha de fonte ("obras conferidas em `ref/pdf/`") incluíam
   Mather, Lefever e Yuill, que **não têm PDF** — e o próprio `.bib` classifica
   as duas últimas como crédito de método, não leitura. Coluna renomeada para
   "Fontes" e nota de fonte reescrita com as exceções.
5. **O quadro não tinha linha para o MATOPIBA**, deixando de fora Carneiro
   Filho, Rausch e Soterroni — três âncoras conferidas e uma subseção inteira.
   Linha 5 acrescentada; e linha 6 para Martins.
6. **Martins estava em dois lugares ao mesmo tempo.** O §2.5 o listava como
   leitura pendente (edição de 1971) enquanto o cap. 5 já citava e usava
   `Martins1996`, que tem PDF conferido. Virou a subseção **2.3.7**; Becker
   segue na lista.
7. **Overclaims no fecho.** "Teto **físico** de oferta" contradizia o cap. 4, que
   registra não ter separado exaustão de restrição legal (RL/APP) — o adjetivo
   caiu. E o fecho enunciava o *drive* comum como resultado; voltou a
   "corroborada e não estabelecida", como no §2.2 e no cap. 5.
8. **A frase da tese se contradizia**: dizia "das três cláusulas" (são quatro) e
   apontava "a segunda" como testada com resultado negativo, quando a segunda
   era justamente a leitura de mercado que a mesma frase dava por não
   estabelecida. Reescrita como lista de quatro cláusulas, cada uma com seu grau.
9. **Cohn: duas previsões anunciadas, uma entregue.** O §2.3.4 dizia que dois
   resultados eram verificáveis aqui, mas a poupança parcial de terra nunca é
   confrontada (grep em caps. 4–5: zero). Passou a declarar que não é testada.
10. **Ponteiro órfão:** o cap. 5 remetia a uma "restrição bibliográfica declarada
    no cap. 2" que não existia mais (o `\notaguia` fora removido). Agora aponta
    para a regra do §2.1.
11. **ABNT:** as duas citações diretas ganharam página (Meyfroidt, p. 20917;
    Carneiro Filho, p. 5), e a de Meyfroidt marca a supressão com `[...]`. Páginas
    também em Angelsen (p. 5 e 6), Rudel (p. 23), Cohn (p. 7238), Rausch (p. 4) e
    Soterroni (p. 2).
12. **Formato da lista de leitura:** o `Decide:` saiu (o autor o considerou
    "confuso e errado"); cada item agora traz **"O que podem oferecer"**,
    formulado como expectativa a verificar. Dez frentes; entraram von
    Thünen/Ricardo, Mather e Ramalho Filho & Beek (1995), este último porque o
    argumento anticircularidade do §2.3.1 depende do que aquele sistema
    classifica. O §2.3.1 deixou de chamar a camada Embrapa de "atributo físico"
    e passou a descrevê-la como classificação de **uso potencial** que não deriva
    do uso observado — que é o que de fato quebra a circularidade.

**Conferência das fontes: nada caiu.** Os números e atribuições corrigidos em
13–14/ago foram reconferidos no texto integral e todos batem — Arima (10%→40%),
Richards (80 mil km²/31%; 63 mil/29%), Cohn ("twice as likely", incl. logística),
Rausch (16–32%), Carneiro Filho (87% / ~70% / 74% / 90% / citação do MATOPIBA),
Soterroni (86%), Meyfroidt (definição de *leakage*), Liu, Lapola, Angelsen,
Rudel. Metadados de Richards, Lefever e Yuill reconferidos no Crossref.

⚠️ **Gotcha novo do BibTeX:** `%` **não** protege um arroba. Comentar uma entrada
inteira com `%` quebra a compilação, e o mesmo vale para o arroba escrito dentro
de uma frase em prosa comentada. A entrada desativada do Mather está guardada no
`.bib` **sem o caractere arroba**.

### Segunda varredura do cap. 2 (16/ago/2026)

A pergunta que a motivou foi direta: *o cap. 2 ficou sem erros?* Não tinha
ficado. A varredura de 15/ago olhava **uma classe** de defeito — atribuição a
fonte — e achou o que procurava; não varreu consistência interna, referências
cruzadas nem cap. 2 × caps. 4–5. Este passe olhou essas.

**O que se reconfirmou.** Texto integral dos 19 PDFs reextraído e cada número
regrepado: Arima (761 municípios, 2003–2008, 10%→40%, *"hundreds of kilometers"*,
*"distal"*), Richards (80.000 km²/31%; 63.000/29%), Cohn (*"twice as likely"*),
Carneiro Filho (87%, ~70%, 74%, 90% e a citação do MATOPIBA **verbatim**),
Rausch (16–32%), Soterroni (86%, 2021–2050), Meyfroidt, Rudel (definição pelo
par, p. 23), Angelsen (quatro estágios p. 3, planície homogênea p. 5). Nenhum
caiu. Os `\ref` para o cap. 5 apontam para as seções certas — conferido por
número de linha, que é o que o compilador **não** verifica (Cohn está em §5.2,
Martins em §5.1). As quatro cláusulas do §2.2 batem uma a uma com o quadro de
grau de estabelecimento do cap. 5.

⚠️ **Paginação de PDF ≠ página impressa.** A citação do MATOPIBA está na página
6 do arquivo, que traz o número impresso **5** — que é o que o `\cite[p.~5]`
declara. Conferir o número impresso, não o índice do extrator.

**Corrigido neste passe (5 itens):**

1. **`\cite[p.~6]{Angelsen2007}` para "mundo ricardiano" estava fora do sentido
   da fonte.** A palavra *Ricardian* aparece **uma única vez** nas 43 páginas, e
   é um parêntese definindo renda como valor **anual** em oposição a VPL
   (*"'Rent' refers to annual values (in the Ricardian world: the maximum annual
   amount a land manager could pay per year…)"*) — forma temporal da renda, não
   ordenação por qualidade da terra. A aspa saiu; a ponte para Ricardo agora se
   apoia só na frase que a sustenta de fato (*"differences in, for example, soil
   quality would affect yield and thereby land rent directly"*, p. 6). Era a
   mesma classe de defeito que a varredura de 15/ago existia para eliminar, e
   **foi introduzida pela correção do defeito #1 dela**.
2. **A contagem que abre o §2.3 não fechava com o próprio capítulo.** Dizia
   "quatro subseções geram previsão… em duas se cumpriu… as três restantes",
   mas o §2.3.6 enuncia previsão ("A previsão que daí se extrai… é a de que o
   contraste apareça dentro de Goiás") e a linha 5 do quadro a reporta cumprida.
   Agora: **cinco** geram previsão (2.3.1–2.3.4 e 2.3.6), **três** cumpridas,
   **duas** não correspondem, **duas** restantes (câmbio = divisão de trabalho;
   Martins = vocabulário). Mesma classe do defeito #8 de 15/ago — a frase-resumo
   não acompanhou a reestruturação.
3. **Liu (2013) não "põe os acoplamentos locais explicitamente de lado".** O
   artigo tem a Tabela 4 (*"Differences between local couplings and
   telecouplings"*) e pede integrar os dois. A conclusão sobrevive — o objeto do
   arcabouço é a distância, logo seu silêncio não prevê ausência de efeito de
   vizinhança — mas a premissa foi reescrita.
4. **Escopo da regra da fonte conferida, que era lacuna.** `Embrapa_Aptidao` era
   citada com `\citeonline` no corpo do §2.3.1 sem texto integral e sem estar
   entre as exceções. O §2.1 passou a declarar que **a regra governa a
   literatura**; fonte de dado é categoria distinta, descrita no cap. 3. E
   registra que o sistema que define as classes daquela camada (Ramalho Filho e
   Beek, 1995) não foi lido e está no §2.5 — o que delimita o alcance do
   argumento anticircularidade. Escopo replicado no cabeçalho do `.bib`.
5. **Resíduo no cap. 5** (l. 109): "o precedente mais próximo, **no mesmo nível
   municipal**, encontrou-o na Amazônia" afirmava para ressalvar na frase
   seguinte — a forma exata que o defeito #3 de 15/ago corrigia. Virou
   "municipal na unidade, porém distal na ligação".

**Compilação:** 76 págs, 0 overfull, 0 indefinida, 0 erro de BibTeX. Verificado
**no texto extraído do PDF** (14/14 asserções: 6 sumiram, 8 entraram, 14/14
obras seguem na bibliografia, Mather segue fora) — log limpo não é verificação
de conteúdo.

⚠️ **O gotcha do arroba mordeu de novo, e no mesmo dia em que foi documentado:**
escrever `@misc` numa frase em prosa comentada do `.bib` quebrou o BibTeX
("I was expecting a `{' or a `('"). O comentário agora escreve "entradas do tipo
misc" e carrega o aviso.

### Terceira varredura do cap. 2 — língua e ABNT (16/ago/2026)

Mesma pergunta do autor, terceira classe. Depois de fonte (15/ago) e consistência
interna (16/ago, acima), este passe olhou **língua, conformidade ABNT e as regras
de voz do projeto**. Achou 5 defeitos e 3 imprecisões, todos corrigidos.

1. **Crase que invertia o sentido**, e justo no parágrafo que enuncia a regra do
   capítulo: *"É preferível **a** alternativa, que seria sustentar o argumento em
   obras conhecidas de segunda mão"* — sem crase, o sujeito é "a alternativa" e a
   frase defende o oposto do capítulo. Virou "**à** alternativa".
2. **Colchetes marcando interpolação inexistente** na citação do Meyfroidt. O
   original diz *"…or through trade in timber or agricultural products"*: o trecho
   entre colchetes era tradução fiel, não acréscimo. Colchetes removidos. (O
   registro de 15/ago dizia que essa citação "marca a supressão com `[...]`" —
   não marcava, e não há supressão.)
3. **Nenhuma citação traduzida declarava "tradução nossa"** — zero ocorrências no
   documento inteiro. As três citações diretas traduzidas do cap. 2 (Angelsen ×2
   na mesma frase, Meyfroidt ×1) ganharam a indicação da NBR 10520. ⚠️ **Os demais
   capítulos não foram varridos para isso.**
4. **Overclaim contradito pelo parágrafo seguinte:** o §2.4 abria com "três
   instrumentos… e **nenhum deles é construção *ad hoc***" e dois parágrafos abaixo
   admitia que para o centro de massa — a métrica-manchete — não se localizou
   precedente. Virou "a origem de **dois** deles está identificada na literatura".
5. **Anglicismo "endereçar"** (cap. 2 e cap. 5) → "enfrentar".
6. **"O remanescente goiano é majoritariamente savânico" era verdade por pouco.**
   Derivando de `carbono_por_formacao.csv` + os percentuais de perda do cap. 4:
   savânica ≈ 6,1 Mha (**54%**), floresta de galeria/cerradão ≈ 4,9 Mha (**43%**),
   campo ≈ 0,4 Mha. Reescrito para dizer a composição — o que **fortalece** o
   limite, porque aquele 43% é fisionomia de Cerrado e não a floresta sobre a qual
   a teoria foi formulada. Mantido qualitativo ("pouco mais da metade") para
   respeitar a convenção de que os caps. 1–2 não carregam número de resultado.
   *(Checagem cruzada: as três áreas de 1985 somam 16,97 Mha e batem com os 16,96
   do censo de sete classes.)*
7. **"Mather (1992), que cunhou o termo"** era fato de segunda mão num capítulo de
   regra estrita. Agora atribuído: *"a quem Angelsen (2007, p. 31) credita a
   introdução do conceito"*.
8. **Caixa do sobrenome composto: testado e mantido como estava.** `(Carneiro
   Filho; COSTA, 2016)` sai em caixa mista porque as chaves duplas bloqueiam o
   `change.case$`. Tirei as chaves para testar: **fica pior** — o BibTeX passa a
   ler "Filho" como sobrenome e **perde o "Carneiro"** (`FILHO, A. C.` na lista,
   "Filho e Costa (2016)" no texto). Revertido, e o `.bib` registra o teste. Das 5
   ocorrências no PDF, as 3 `\citeonline` saem certas e 2 perdem a caixa alta.

**Falso positivo descartado:** o extrator devolve "definemleakagecomo" e
"Épreferívelàalternativa". Não é defeito do PDF — o pypdf perde o espaço na troca
de fonte do `\emph` e em linhas muito justificadas. Conferir sempre com comparação
**insensível a espaço** antes de reportar como erro.

Também medidas as duas citações longas no PDF renderizado: ambas ocupam **2
linhas**, abaixo do limite de 3 da NBR 10520 — corretamente em linha, sem recuo.

⚠️ **O gotcha do comentário mordeu de novo:** pus um `%` explicativo **dentro** da
entrada do Carneiro Filho e o BibTeX quebrou. Comentário só **acima** do arroba.

**Compilação:** 76 págs, 0 overfull, 0 indefinida, 0 erro de BibTeX; 8/8 asserções
conferidas no texto extraído, mais 7/7 de regressão sobre as correções de 15–16/ago.

**Ainda não varrido no cap. 2:** conformidade ABNT de estrutura (numeração,
espaçamento, formato de quadro) e a revisão de língua dos **demais** capítulos —
os itens 3 e 5 provavelmente reaparecem lá.

### Quarta varredura do cap. 2 — o rastro da reestruturação (17/ago/2026)

Mesma pergunta do autor pela quarta vez sobre o cap. 2, e a resposta a ela é o
achado principal: **cinco dos seis defeitos deste passe nasceram da própria
reescrita de 15/ago**, e as duas varreduras de 16/ago olhavam classes que não
cobriam o rastro dela. O 15/ago não foi varredura, foi reestruturação — criou
o §2.5 do zero, reescreveu o quadro, moveu seções. Edição desse tamanho gera
defeito na proporção em que elimina. **Regra nova: depois de reestruturar,
varrer o que a reestruturação deixou para trás, antes de varrer classe nova.**

Escopo declarado deste passe: coerência interna do cap. 2, cap. 2 × caps.
1/4/5, cap. 2 × `.bib`/`LEIAME`, estrutura ABNT. **Não** reconferiu número
contra CSV nem atribuição contra fonte (três passes já fizeram).

**Corrigido (7 itens):**

1. **A cláusula (ii) da tese se contradizia no parágrafo seguinte.** Dizia
   "essa reorganização **não é** um deslocamento causal" e, três linhas abaixo,
   que o resultado "não equivale a demonstrar que o fenômeno não exista" — a
   forma afirmação-forte × lista-de-limites que a regra de 28/jul proíbe. O
   cap. 5 já tinha a formulação certa (linha 3a do quadro de grau). Reescrita
   para "o deslocamento causal…, no canal local e contemporâneo em que pôde ser
   testado, não apresenta a assinatura que exigiria". ⚠️ A 2ª varredura
   registrou que "as cláusulas batem com o quadro do cap. 5" — batiam em
   **conteúdo**, e a comparação não olhou **força da afirmação**.
2. **"A (ii) é a única testada diretamente"** contradizia o §5.3, que reporta
   teste formal com p-valor de permutação para a (iii). Virou "a única
   enunciada como hipótese a rejeitar".
3. **O Quadro 1 inventava duas frentes.** A coluna dizia "Frente" e a legenda
   "por frente da investigação", com linhas "5." e "6." — mas são **quatro**
   frentes (cap. 1 l. 96 e 119, §2.1, e o quadro do cap. 5, que tem 1/2/3a/3b/4).
   Criado pelo reparo #5 de 15/ago. Coluna e legenda viraram "eixo de
   confronto", as duas últimas linhas perderam o número, e o parágrafo de
   abertura declara que são transversais às frentes.
4. **A nota de fonte do quadro afirmava conferência que não houve, de novo.**
   Listava três exceções e incluía `Weiszfeld1937` na afirmação "texto integral
   lido e conferido" — que descreve interlocução teórica, não citação de origem
   de método. Weiszfeld entra em §2.4 pela mesma função de Lefever e Yuill.
   Passou à exceção 2 do §2.1, com o estatuto exato: **das três, só Weiszfeld
   teve o texto integral obtido**. Mesma classe do defeito #4 de 15/ago.
5. **Lista de leitura do `.bib` fora de sincronia com o §2.5**, contra a regra
   do próprio cabeçalho. `Lefever (1926)` estava na lista de pendentes **e** era
   entrada ativa citada no corpo — o defeito do Martins (#6 de 15/ago), na
   mesma estrutura, com outro nome; Meyfroidt e Lambin (2011) faltava no §2.5;
   Noojipady faltava no `.bib`; e o comentário do USDA-ERS ainda dizia "citado
   na seção do câmbio", de onde a reescrita de 15/ago o tinha tirado.
6. **USDA-ERS sem definição na primeira ocorrência**, contra a regra de 13/ago.
   Era a **única** ocorrência da sigla no documento, e a definição se perdeu na
   reescrita do §2.5.
7. **Resíduo no cap. 3** (l. 396), achado pela conferência no PDF: o centro de
   massa era dito "na linhagem de Lefever (1926), e não uma construção *ad
   hoc*", **apontando para a §2.4** — que diz o oposto (Lefever é a elipse; para
   o centro de massa o levantamento não localizou precedente). É o overclaim
   que o item #4 de 16/ago removeu do cap. 2 deixando o gêmeo no cap. 3.

**Falso positivo meu, descartado na fonte:** as duas bases de Richards
("31% da extensão então cultivada" × "29% da área nacional de 2009") parecem
inconsistentes e não são — o original diz *"31 percent of the current extent"*
e *"29 percent of the nation's 2009 total"*. O capítulo reproduz fielmente.

**Não corrigido, decisão do autor com o orientador:** forma ABNT das ~10 obras
do §2.5 e do §2.1 citadas em autor-data sem entrada nas referências (Mather,
von Thünen, Ricardo, Boserup, Strassburg, Seto, Spera, Noojipady, Ramalho Filho
e Beek, Becker). A declaração do §2.1 resolve a epistemologia, não a NBR 10520.
Saídas: mudar a tipografia para não lerem como citação, ou mover o §2.5 para
apêndice.

### Quinta varredura — atribuição contra o PDF, e o §1.3 (18/ago/2026)

Escopo declarado: (a) **refazer do zero** a conferência de toda atribuição e de
todo número do cap. 2 contra o **texto integral** dos PDFs, sem confiar no
registro dos passes anteriores; (b) a regra do §2.1 contra o **resto do
documento**, não só contra o cap. 2; (c) as contagens internas do cap. 2; (d) a
justificativa (§1.3), a pedido do autor. **Não** varri língua/ABNT nem número
de resultado contra CSV.

**A reconferência independente não achou nada.** As 15 obras foram relidas no
PDF e todas as atribuições se sustentam, inclusive as páginas: Angelsen
(p. 5 planície homogênea + citação, p. 6 qualidade do solo, p. 3 os quatro
estágios, p. 31 crédito a Mather), Rudel (p. 23), Cohn (p. 7238), Meyfroidt
(p. 20917), Carneiro Filho (p. 5 — impressa, que é a 6ª do PDF), Rausch (p. 4),
Soterroni (p. 2), mais Arima, Lapola, Liu, Martins, Richards, Lefever, Yuill e
Weiszfeld. A nota de rodapé do Plan B de Richards confere com a entrada do
`.bib` (4 autores, GEC 22(2):454–462).

**Corrigido no cap. 2 (1 item):** o parágrafo de abertura do Quadro 1 dizia
"as **quatro** primeiras linhas correspondem às frentes; as duas últimas são
transversais" — 4+2=6, e o quadro tem **sete** linhas. São as **cinco**
primeiras (a frente 3 vem desdobrada em 3a/3b, como no `quadro:alcance` do
cap. 5). Resíduo do reparo #3 de 17/ago, que tirou a numeração das duas
últimas linhas e não reajustou a contagem — mesma classe de defeito do passe
anterior, uma iteração depois.

**Corrigido no §1.3 (4 itens).** A justificativa afirmava mais do que o
trabalho sustenta, e num caso contra uma fonte conferida:

1. **"O canal intra-estadual raramente é isolado"** — afirmação sobre o estado
   da literatura que o §2.5 declara **desconhecido** ("se existe literatura que
   tenha testado o canal de adjacência em escala subnacional") e que o cap. 6
   põe como frente prioritária. Passou à formulação do §2.3.3: não é examinado
   por nenhuma das fontes conferidas, e verificar se alguém já o isolou é a
   frente prioritária da revisão.
2. **"as séries municipais longas costumam ignorar o problema das fronteiras
   administrativas móveis"** — **contradito por Ehrl (2017)**, que é a fonte da
   própria AMC: *"Numerous other papers have previously worked with differently
   defined AMCs"*; *"Even studies with a horizon of only ten years and more
   **have to rely on** AMCs"*; as AMCs do IPEA (Reis et al., 2011) são o padrão,
   usado por Caselli e Michaels (2013) e Reis (2014). AMC é equipamento padrão
   da economia aplicada brasileira, não um descuido que este trabalho conserta.
   Reescrito para a versão estreita e defensável: o instrumento é consolidado
   (`\cite{Ehrl2017}` entra no cap. 1); o que é menos frequente é empregá-lo no
   ponto em que as duas fontes se cruzam — raster recortado pelo polígono de
   hoje × estatística tabulada pelo município do ano (§3.3).
3. **"o Cerrado remanescente concentra-se no Norte"** — os caps. 4 e 5 dizem
   **44%** do estoque exposto. É a maior parcela entre as três regiões, não a
   maioria; sem o número ao lado, "concentra-se" lê como maioria. Virou "a maior
   parcela do Cerrado ainda exposto à conversão", que também acerta o
   vocabulário (exposição, não remanescente genérico).
4. **"as alavancas eficazes são outras, e agem sobre o estado inteiro"** — o
   §5.6 diz textualmente que "nenhuma estimativa aqui identifica efeito de
   política" e que "o trabalho não diz qual instrumento funciona". Passou à
   forma condicional do cap. 5 (política que só desloca atividade entre regiões
   tende a não reduzir a conversão total, porque o que altera o agregado é o
   retorno de converter) mais o limite explícito.

Menor, no mesmo passe: "a literatura da fronteira do Cerrado **opera**" virou
"opera **sobretudo**" — afirmação universal apoiada em três obras conferidas.

**Pendente, decisão do autor: a regra do §2.1 não cobre dez obras citadas nos
caps. 3 e 4.** A regra é enunciada como "só entra **no corpo do texto**" e o
cap. 5 a estende a si, mas ficam fora das três exceções declaradas: (a)
**Bustamante (2012) e Grace (2006)**, apresentadas em 4.5 como "colhidos da
**literatura** de estoques do Cerrado", e das quais o `LEIAME` registra que só
se conferiu metadado no Crossref; (b) **oito obras de método do cap. 3**
(Newey-West, Andrews, Quandt, Rodionov, Toda-Yamamoto, Benjamini-Hochberg,
Adão, Borusyak), mesma função da exceção 2, que só nomeia Lefever/Yuill/
Weiszfeld. Adão e Borusyak são o caso exposto: a l. 538 lhes atribui uma
**afirmação de conteúdo** ("o erro-padrão agrupado é otimista"), não só a
origem de um procedimento. O `.bib` declara o estatuto num comentário, que a
banca não lê. Conserto barato: generalizar a exceção 2 da lista nominal para a
classe, e dar a Bustamante/Grace o mesmo tratamento que a camada da Embrapa já
tem (fonte de parâmetro, não interlocução).

**Pendente também:** o §2.3.1 manda o leitor ao cap. 3 para a camada de aptidão
— toda a defesa anticircularidade pende dela —, e lá ela só existe como uma
linha do quadro de fontes. Falta dizer o que a camada é, como as classes foram
ordenadas e como ela entra no painel.

**Compilação:** 76 págs, 0 overfull, 0 referência indefinida, 0 erro de BibTeX;
`verificar.py` em 0 erros e os mesmos 12 avisos (caps. 3–4, fora do escopo).

### Reestruturação do cap. 2 — tirar o método de dentro do capítulo (19/ago/2026)

Pedido do autor, e o diagnóstico é dele: o capítulo tinha virado a descrição
das próprias decisões. Enunciava regras de trabalho, explicava como as fontes
foram reunidas, declarava exceções, e só então chegava ao conteúdo. **Nada
disso é conteúdo de referencial teórico.** Frase-tipo que motivou o pedido: *"A
seção seguinte trata desses arcabouços na medida exata em que as fontes
conferidas os sustentam"*.

**Estrutura antes → depois:**

| antes | depois |
|---|---|
| 2.1 O estatuto deste capítulo e como as fontes foram reunidas | *(saiu)* |
| 2.2 A tese e os arcabouços que ela mobiliza (4 cláusulas + graus) | *(virou 1 parágrafo de abertura)* |
| 2.3 As fontes conferidas e o que cada uma sustenta (7 subseções) | 2.1–2.7, **seções planas** |
| 2.4 Origem dos métodos descritivos | 2.8 |
| 2.5 O que o levantamento apontou e ainda não foi lido | 2.10, com abertura de 4 linhas |
| 2.6 Síntese e posicionamento provisório (quadro + "o que há de novo") | 2.9, **só o quadro** |

**As três coisas que saíram, e para onde foram:**

1. **A regra da fonte conferida** (só entra obra lida integralmente) continua
   valendo — deixou de ser *enunciada*. Vive no cabeçalho do `.bib`, que é onde
   se decide se uma entrada nova passa. O §2.10 conserva a única frase que o
   leitor precisa: "nenhuma delas sustenta afirmação deste texto, e por isso não
   figuram na lista de referências".
2. **As exceções acabaram** — e não viraram nota de rodapé. Primeira tentativa
   foi essa, e o autor rejeitou no mesmo dia: *"as coisas que não sabemos ainda
   e não temos certeza, podemos só não colocar no texto… é só não usar ela (não
   precisamos usar e dizer que temos certeza)"*. Resolvidas **na raiz**:
   - **Richards** passou a citar a versão que foi de fato lida — o Plan B
     Research Paper do MSU (Richards sozinho, out/2012, AgEcon Search), agora
     `techreport` no `.bib`, com os metadados tirados da capa do próprio PDF.
     Sai a nota, some a discrepância. Custo: o *working paper* é menos citável
     que o artigo da *Global Environmental Change*; se o PDF pago aparecer pela
     CAPES, a entrada volta a ser a publicada. Concordância ajustada no texto
     ("constituem"→"é", "os autores estimam"→"o autor estima").
   - **Lefever (1926) e Yuill (1971) saíram** do texto e do `.bib`. Só se
     tinham metadados. A elipse de desvio-padrão continua descrita nos caps. 2
     e 3, **sem atribuição de origem** — é instrumento auxiliar, não precisa de
     linhagem. Não foram para a lista de leitura: metadados guardados em
     comentário no `.bib` para recriar as entradas se um dia interessarem.
   - **Weiszfeld nunca foi exceção**: o fac-símile do J-STAGE foi obtido. Segue
     citado, e agora é a única atribuição de método do §2.8.
3. **A última coluna do quadro** era "O que o confronto mostrou" — isto é,
   resultado. Virou "O que prevê ou oferece". O desfecho de cada confronto já
   mora no cap. 5, e estava duplicado. Pelo mesmo motivo saiu o fecho "o que há
   de novo, se a fronteira do Cerrado rumo ao norte já é conhecida?".

**Justificativa residual, segundo passe.** Depois de tirar a seção declaratória
ainda sobrava o hábito dela, espalhado em cláusulas: *"as formulações originais
de von Thünen e de Ricardo não foram consultadas"*, *"a formulação original de
Mather ainda não foi lida"*, *"esse resultado não é confrontado aqui, porque o
desenho não produz…"*, *"o limite da correspondência fica dito"*, *"a escala
precisa ser dita com exatidão"*, *"é essa procedência — e não uma suposta
neutralidade — que quebra a circularidade"*. Todas cortadas. O marcador
"literatura **lida**" / "fontes **lidas**" também saiu de quatro pontos: ele
reintroduzia a regra pela porta dos fundos.

**Terceiro passe — varredura de "leitura de metadados"** (pergunta do autor:
*tirou todas?*). No corpo do texto, sim: zero ocorrência de "metadado",
"conferido/conferida" aplicado a fonte, "texto integral", "não foi lida",
"working paper", "versão publicada". Duas sobras foram achadas e cortadas:
(a) a abertura do §2.10 ainda dizia "obras pertinentes cujo **texto integral**
ainda não foi lido… nenhuma delas sustenta afirmação deste texto, e por isso
não figuram na lista de referências" — virou duas linhas: *"O levantamento
apontou, tema a tema, obras ainda não lidas. Elas estão abaixo, com o que se
espera de cada leitura."*; (b) o `\notaguia` do cap. 3 anunciava que "as
referências de método antes citadas apenas por epônimo foram **conferidas e
vinculadas**" — pendência resolvida, nota obsoleta, removida.

**O que sobrou de propósito**, e não é do mesmo tipo: o `\footnote` do cap. 1
que abre a sigla MATOPIBA, e o "conferido contra uma fonte que não passa pelo
classificador" do cap. 4 — este é sobre **dado** (o bracket da D26), não sobre
literatura.

**Voz.** O texto descrevia o trabalho de fora ("O trabalho recusou ancorar os
períodos…", "Este capítulo apresenta os resultados…"). Corrigido no cap. 2
inteiro e nos pontos que o autor nomeou: abertura do cap. 3, §3.x da
periodização (a frase *"decisão metodológica, não detalhe de exposição"* saiu),
abertura do cap. 4, e sete pontos do cap. 5.

**Coerência dos caps. posteriores** (era a preocupação explícita do autor):

- **Ponteiro morto.** O `\notaguia` do cap. 5 remetia à regra do
  `sec:ref-estatuto`, que deixou de existir. Reescrito.
- **Alegação sem lastro, e duas vezes.** *"É a assinatura que a renda da terra
  prevê"* (§5.1) atribuía a Angelsen mais do que ele diz: o arcabouço prevê a
  **ordenação** dos usos pelo gradiente, não a translação do conjunto com o vão
  preservado. E "camadas que sobem juntas… sem que o vão entre elas se feche"
  não tinha sujeito: **contradiz o cap. 4**, que mostra vegetação natural
  ancorada, leite subindo menos da metade do rebanho (vão 30→68~km) e área
  urbana andando para o **sul** — e fecha com "quem marcha é a pecuária de corte
  na fronteira, e não o mapa inteiro subindo". A frase vale para as **três
  camadas produtivas** (pastagem $+77{,}6$, rebanho $+66{,}9$, agricultura
  $+65{,}2$~km) e para o vão lavoura×pasto de 120–130~km. Reescrita nomeando as
  três e o vão.
- **Fonte não lida sustentando interpretação.** O §5.1 dizia que a leitura
  geopolítica de **Becker** "informa a interpretação do Norte goiano como
  território em disputa". Becker está na lista de leitura. A menção saiu; a
  ressalva que ela carregava (o desenho não observa Estado, projeto ou agente)
  ficou.
- **Parêntese não fechado** no §5.6 ("…e quando (antes de o fluxo chegar…"),
  achado de passagem.
- Cap. 1 dizia "fontes conferidas"; agora "fontes lidas até aqui" (o termo
  técnico saiu junto com a seção que o definia). Cap. 6 idem.

**`verificar.py` recalibrado.** A invariante 3 exigia um `\section` **depois**
do `sec:ref-agenda`; com a lista de leitura fechando o capítulo, o regex passou
a aceitar fim de arquivo. As âncoras de calibragem do cap. 2 (invariante 5)
sobreviveram por construção — as três frases guardadas foram realocadas, não
apagadas: *"não equivale a demonstrar que o fenômeno não exista"* → §2.3,
*"corroborante e não estabelecida"* → §2.5, *"não constitui teste"* → §2.7.

**Compilação:** 74 págs (eram 76), 0 overfull, 0 referência indefinida, 0 erro
de BibTeX; `verificar.py` em **0 erros** e os mesmos 12 avisos de sigla nos
caps. 3–4.

**Segue pendente** (não tocado aqui, herdado da varredura de 18/ago): a camada
de aptidão da Embrapa, de que depende toda a defesa anticircularidade do §2.1,
só existe no cap. 3 como uma linha do quadro de fontes; e Adão/Borusyak
recebem, na l. 538 do cap. 3, uma **afirmação de conteúdo** sem terem sido
lidos.

### Passe de tom nos caps. 3–5 (19/ago/2026)

Pedido do autor depois da leitura de avaliação. **Só forma: nenhum número,
nenhuma afirmação e nenhuma chave de citação mudaram** — conferido por script
que compara os multiconjuntos de tokens numéricos e de chaves `\cite`/`\ref`
dos dois lados de cada edição (`confere_numeros.py`, 0 divergências).

**O diagnóstico.** Duas construções tinham virado o formato-padrão da frase:

| | cap. 2 | cap. 3 | cap. 4 | cap. 5 |
|---|---|---|---|---|
| conector causal soldado (*pois, já que, uma vez que, dado que, de modo que, porque*) | 2 → **2** | 40 → **1** | 49 → **8** | 23 → **6** |
| antítese *"X, e não Y"* / *"não é X, e sim Y"* | 5 → **5** | 27 → **18** | 49 → **30** | 28 → **7** |

O conector causal é o mesmo hábito que estragava o cap. 2, uma escala abaixo:
cada afirmação vinha com uma justificativa soldada. Quase sempre a oração se
sustentava sozinha, com ponto final ou dois-pontos. A antítese é um bom
instrumento de precisão — é dela que vem parte do rigor do texto —, mas a uma
cada 16 linhas o leitor parava de registrá-la. Foram convertidas as em que a
alternativa negada já era óbvia pelo contexto; as que carregam calibragem
(*"mede exposição, e não disponibilidade"*, *"associativa e não causal"*,
*"e não como tendo andado oito quilômetros"*) ficaram todas.

**Casos que estavam dobrados sobre si mesmos** e foram desfeitos:
*"É um preço inevitável quando o dado vem de pesquisa, **porque** a informação
histórica do município-filho não existe separada, **pois** ela estava no pai"*;
*"a proteção não falhou onde tentou, **pois** ela não estava no caminho, e não
está agora, **já que** o Norte concentra 44\%…"*; *"o mecanismo (reorganização
sob força comum, **e não** empurrão entre regiões), **e não** a identidade da
força"*.

**Cuidado tomado para não trocar um tique por outro.** Boa parte dos cortes
virou dois-pontos. Auditado depois: só 6 parágrafos em todo o documento têm 3+
dois-pontos, e 4 deles já eram assim (enumerações). Os 2 criados pelo passe
foram desfeitos à mão.

**Um parágrafo dividido.** A conta de carbono do §4.5 era um bloco único de ~25
linhas com sete orações subordinadas. Virou três parágrafos (a conta e seu
escopo; quem paga; quando se pagou), sem perder uma palavra. Aproveitou-se para
consertar a sintaxe quebrada de *"Depois, quando se pagou --- 80\% do total,
774~Mt, saiu no Ato~I"*.

**Reenquadramento.** As substituições deixaram linhas longas no meio de
parágrafos. Um passe de `textwrap` em 78 colunas reenquadrou 27 parágrafos de
prosa, protegendo (a) comandos LaTeX de argumento único, para que nenhum
`\cite{}` fique partido em duas linhas — isso quebra a invariante 2, que casa
linha a linha, e aconteceu uma vez com `\cite{Adao2019, Borusyak2022}`; e (b) as
cinco frases-âncora da invariante 5, que o `verificar.py` procura no texto cru.

**Compilação:** 74 págs, 0 overfull, 0 referência indefinida; `verificar.py` em
0 erros e os mesmos 12 avisos de sigla.

### Os dois defeitos de conteúdo achados na leitura de avaliação (19/ago/2026)

**1. O `p = 0,060` do §4.1 não era órfão — perdeu o referente.** A frase citava
três p-valores (0,10 / 0,046 / 0,12, a sensibilidade ao ponto de corte) e depois
um quarto, sem origem: *"e não porque um único teste tenha dado p = 0,060"*.

Rastreado até `Textos/pipelines/29_triangulacao_periodizacao.md`: **é outro
teste**. O 0,060 é o Mann-Whitney da **taxa total de mudança entre as sub-fases
2001–05 e 2006–19** (ratio 1,25, n=4, poder 0,63). A transposição fundiu dois
testes distintos num só e deixou o número solto. ⚠️ **Cuidado com a tabela do
`29_...md`**: as linhas dizem "P2 vs P3" mas testam as **sub-fases** — a nota de
rastreabilidade (corrigida em jul/2026) registra que um bug passava `ATOS_FLAT`
à função e ela recomputava Ato II × Ato III. Os rótulos legados ficaram.

O §4.1 passou a dar as **três** razões da não adoção, na ordem em que pesam:
(a) o método primário não detecta a fronteira — o sup-F lê o intervalo como
platô contínuo, e a regra do §3.5 exige convergência; (b) a taxa total não
separa as sub-fases (p = 0,060, poder 0,63 com n = 4); (c) a fronteira é
sensível ao corte (0,046 / 0,10 / 0,12). E ganhou o que faltava: a sub-fase
2001–05 **é real na composição** (veg. natural perdida em ritmo muito mais
alto, p = 0,0008; conversão pasto→agricultura ~4× mais intensa), e está inteira
antes de 2020, fora do alcance da mudança de rótulo.

**2. O θ significativo que o cap. 5 usava e o cap. 4 não reportava.** O §5.2
construía um parágrafo sobre *"a décima segunda é significativa"* — fato que o
cap. 4 nunca dava. Pior: a nota da figura do cap. 4 falava de **outra** célula
significativa (o placebo dos vizinhos ao norte, p = 0,032), o que fazia o
parágrafo do cap. 5 parecer estar descrevendo o placebo.

Fonte auditada (`Visualizacao/index.html`, bloco "0 / 12"): as duas coisas são
verdadeiras e são células diferentes. Entre as doze, **uma** tem p < 0,05
(p = 0,02) — e a viz carrega a ressalva que **sumiu na transposição**: *"o único
p<0,05 está na régua que o classificador contamina — por isso este trabalho não
cita aquele p=0,02 como se carregasse a conclusão"*. Por eliminação entre as
três réguas do §4.3, a contaminada é a da classe ``Agricultura'' estrita (a
união é robusta à reetiquetagem por construção; a soja do IBGE não passa pelo
classificador).

Consertado dos dois lados: o §4.3 passou a reportar "onze das doze não são
significativas; a décima segunda tem p = 0,02, na régua que o rótulo do Mosaico
contamina", e o §5.2 passou a dar **os dois** motivos para não ler aquilo como
achado — a régua contaminada e o placebo direcional que acende ao norte.

**Padrão-raiz, terceira ocorrência:** a transposição da viz para o texto perde a
ressalva datada e mantém o número. Mesma família do 20,5→51,6 Mt/ano (14/ago) e
do EPSG:5880≠Albers.

### Link da visualização e fim dos apêndices (19/ago/2026)

**A visualização entrou no texto.** Caixa de destaque (`\destaque`, definida no
`main.tex` com `fbox`+`minipage`, sem pacote novo) na abertura do memorial,
antes de "Trajetória e formação", com o endereço
`https://victorgit10.github.io/mestrado-lulc-goias/Visualizacao/` — guardado
numa macro única, `\urlviz`, para não haver duas cópias do endereço no
documento. A caixa puxa o gancho da IA (o mesmo instrumento que deu autonomia
para programar construiu a visualização), aponta para a §3.10 e recomenda o
acesso antes dos capítulos de resultados e discussão. O endereço reaparece uma
segunda vez, em nota de rodapé, na §3.10, onde os "produtos de uso direto" são
enunciados.

**Os três apêndices saíram.** A pedido do autor, com a leitura de que
sobrecarregariam uma qualificação. O diagnóstico confirmou: A (índice dos
pipelines) e C (glossário de métricas) eram só `\notaguia`, sem conteúdo, e o
que prometiam já está no repositório e na visualização — que tem "As vinte e
sete decisões" e o "Glossário rápido" navegáveis, e agora está linkada. O B
tinha prosa real, mas suas três subseções (D21–D24, D25–D26, oscilação)
repetiam a §3.9.

**O que não se perdeu** (a parte que não era repetição):

- O **Quadro "Resultados superados"** subiu para o corpo, como **§4.6**, onde
  já era referenciado no fecho do cap. 4. Quadro renumerado de 7 para 5.
- Os números que só existiam no apêndice foram dobrados na §3.9: os 43,7% de
  linhas fora do polígono, a censura de 74,9%→63,7%, as observações de
  11.035→15.933 (+44%) e — o ponto que faltava — que os registros descartados
  **não eram aleatórios** (eram os de origem mista agricultura/pastagem, a
  categoria mais próxima do mecanismo que a análise queria distinguir).
- Na §3.9, também: por que a união não é correção (o que a classe Mosaico
  contém: ILP, mosaico fino demais para 30 m, mosaico antigo e estável) e os
  números da simetria da oscilação (75–98% para savana; razão 8,4×→1,22×).

**Referências cruzadas religadas:** `ap:decisoes`→`sec:met-decisoes` (memorial
e §3.9, esta apontando o registro completo para a visualização),
`ap:glossario`→"cada métrica é definida no ponto em que é empregada",
`ap:pipelines`→"publicada com o repositório", `ap:superados`→`sec:superados`.
`pos/apendices.tex` removido, o `include` retirado do `main.tex`, entrada
tirada do `CORPO` do `verificar.py`. 75 → 71 páginas; `verificar.py` com
0 erros.

**Fio que isto fecha:** a saída "mover o §2.10 para apêndice", registrada em
15/ago como uma das duas para a forma ABNT das obras da lista de leitura,
deixou de existir. Resta a outra (mudar a tipografia para não lerem como
citação).

**Gotcha do ambiente:** duas barras invertidas seguidas, num heredoc de Bash,
chegam ao Python como uma só — as linhas do `tabular` do quadro promovido
vieram com uma barra e o `pdflatex` quebrou com `Misplaced noalign`. Montar a
barra com `chr(92)*2` ou corrigir linha a linha.

### Tirar o andaime: notas, siglas e cronograma (19/ago/2026)

**As cinco notas cinzas saíram.** `notaguia` nos caps. 1, 3, 4, 5 e 6 era
andaime de trabalho ("Primeira redação, a partir da Parte 4 da visualização…")
e saía impresso. A macro continua definida no `main.tex`, sem uso — a
procedência que as notas guardavam já vive aqui neste README. Nenhuma delas
carregava informação que não estivesse registrada em outro lugar; a única com
pendência real era a do cap. 6 (produto técnico), fechada abaixo.

**Os 12 avisos do `verificar.py` foram a zero.** Eram três classes:

- **AMC, EPSG, Mha** — primeira ocorrência fora de tabela sem a expansão ao
  lado. `Áreas Mínimas Comparáveis (AMC)` no §1.2 (a 1ª menção do corpo);
  `14,8 milhões de hectares (Mha)` no §4.1; e a projeção virou "SIRGAS 2000,
  código 5880 do registro geodésico EPSG", que nomeia o registro em vez de só
  exibir o código.
- **Nove siglas "nunca expandidas no corpo"** (SIDRA, PPM, PIB, IPCA, SICOR,
  IPEA, Embrapa, PRODES, INPE): todas estreavam dentro do Quadro 2, e a
  expansão só existia na lista de siglas. O parágrafo que abre o §3.2 foi
  reescrito para amarrar cada sigla à sua expansão na primeira menção. Nota:
  o PDF já expandia IBGE/INPE/IPEA/Embrapa **via citação** (o autor no `.bib`
  é a instituição por extenso), mas o `verificar.py` lê o `.tex` e não vê
  isso — e o leitor também não via o vínculo entre a expansão e a sigla.
- Onde a prosa passou a nomear a instituição, `citeonline` virou `cite`, para
  o nome não sair duas vezes.

**Cronograma refeito (cap. 6).** O orientador liberou o formato ("como
acharmos melhor"). Atividades mais gerais, seis linhas em vez de oito, e a
régua deixou de ser semestral (2026.2/2027.1/2027.2) e passou a mensal:
**set., out., nov., dez.–jan., com a defesa no fim de dezembro de 2026 ou
início de janeiro de 2027**. Fecha também o item que a nota cinza deixava
aberto: os produtos de uso direto (repositório + visualização) já existem, e
o que resta a eles é documentação de uso e versão de depósito — viraram linha
do quadro.

**Defeito da própria classe, pego no passe:** a frase de abertura dizia "três
frentes" e o quadro passou a ter quatro atividades substantivas. Trocada por
enumeração sem contagem. É a `frase-resumo não acompanha reestruturação` de
16/ago, terceira aparição.

**Resolvido no mesmo dia**, ver a seção seguinte: o §2.10 passou a ficha
bibliográfica NBR 6023 fora das Referências.

### O §2.10 em ficha bibliográfica — o meio-termo (19/ago/2026)

**Diagnóstico corrigido.** O registro de 15/ago dizia "~10 obras do §2.1 e do
§2.10 citadas em autor-data sem entrada nas referências". Errado quanto ao
§2.1: o corpo argumentativo já resolvia por nome ("von Thünen" aparece 3× no
§2.2, nunca como `von Thünen (1826)`, com a atribuição recaindo sobre Angelsen,
que foi lido). **Todas** as formas autor-data estavam dentro do §2.10, a seção
cujo título diz que as obras não foram lidas. O que disparava a NBR 10520 era
uma coisa só: o ano entre parênteses depois do nome.

**A saída adotada** (nem A nem B): ficha bibliográfica completa em forma
NBR 6023, **dentro do §2.10, fora das Referências**. Ganha a precisão que B
queria (autor, título, veículo, volume, páginas) sem criar entrada para obra
não lida, e a separação entre as duas listas passa a ser estrutural em vez de
declarada — é o argumento a dar a quem perguntar por que Boserup não está nas
referências.

**`apud` foi considerado e descartado**, e vale registrar por quê: é o
dispositivo da NBR para "conheço por intermédio de", e caberia em von Thünen /
Ricardo / Mather. Fui ver e o corpo **não atribui afirmação específica a
nenhuma delas** — atribui a Angelsen e a Rudel, que as retomam. Não há citação
de segunda mão a formalizar.

**Metadados conferidos no Crossref e em catálogo** (o registro é bibliográfico;
nenhuma obra passou a ser lida): Strassburg GEC 28:84–97; Spera GCB
22(10):3405–3413; Meyfroidt e Lambin ARER 36:343–371; Mather Area 24(4):367–379;
Boserup London: George Allen & Unwin, 1965; von Thünen Hamburg: Perthes, 1826;
Ricardo London: John Murray, 1817.

**Achado: o título de Noojipady estava errado.** A lista trazia "Reduced
deforestation and forest degradation emissions from the Brazilian Cerrado", que
**não corresponde a nenhuma obra do autor** — a varredura do Crossref por autor
em 2016–2018 devolve, do Cerrado, só *Forest carbon emissions from cropland
expansion in the Brazilian Cerrado biome*, ERL 12(2):025004,
doi 10.1088/1748-9326/aa5986. Corrigido no `.bib` e na ficha. O erro estava só
no registro interno: o `.tex` trazia "Noojipady et al. (2017)" sem título, e
por isso nenhuma varredura anterior o pegou. **Lição: obra que entra na lista
sem título não é conferível — o título é o que se checa.**

**Três frentes não têm obra e passaram a dizer isso**: centróides migratórios
(o levantamento não localizou precedente), o estudo do USDA-ERS (título por
identificar) e a produção da UFG (a levantar). Becker segue com edição por
identificar. Antes ficavam implícitas; agora a ausência é explícita.

**Mecânica.** Comando `\ficha` no `main.tex` (`hangindent`, corpo menor). O
rótulo do `item` ficava pendurado no `everypar` da lista e saía na mesma linha
da primeira ficha — `\leavevmode` depois do rótulo nos 6 itens que abrem com
ficha. **`verificar.py`, invariante 3, foi adaptado junto**: `obras_cap` lia
`Nome (ano)` e passou a ler as fichas (ano fecha o registro, autoria é o trecho
até o primeiro ponto). A invariante pegou a mudança de formato sozinha, com 10
erros, antes de eu adaptá-la — que é exatamente para isso que ela existe.
Segue em 10 obras no `.bib` ↔ 10 no §2.10.

**Este item sai da lista de pendências.** A forma ABNT do §2.10 está resolvida.

### Leitura crítica do texto inteiro, e as três análises que ela pediu (19/ago/2026)

Primeira leitura do documento **como banca**, não como autor: escopo declarado
= consistência numérica texto × CSV, lógica das afirmações e forma ABNT.
**Não** reauditou fidelidade das citações aos PDFs (feito em 13/ago) nem
conteúdo de figura. ~60 números conferidos contra `data/processed/`.

**O que se sustentou.** Quase tudo. Batem dígito a dígito: as 12 θ do teste
espacial (todas negativas; a única significativa é a régua "Agricultura",
p=0,0204), o placebo direcional que acende (β=−0,054; p=0,0319), a substituição
local (−0,515 a −1,144), o menor p do teste temporal (0,0782), o shift-share
(β=−0,0325; R²w=0,00116), os quatro desfechos de área nulos, o GMM do censo
(μ₁=3,89/σ 1,60/33%; μ₂=16,31/σ 7,53/67%), o carbono (973 Mt [751–1208]), o
estoque (6,56 Mha; Norte 44%; 97%/94,3%), a decomposição (17%/83%), Moran
(115/140 e 125/140), ρ e λ (0,353–0,558). **A calibragem do texto estava
correta.**

**Cinco erros achados e corrigidos.**

1. **Base do crédito invertida** (§4.4.1). Dizia "14,3→24,1 bilhões (série da
   fonte em reais de 2010, e não na base de dezembro de 2024)". É o contrário:
   14,3→24,1 são `credito_rural_go_real` = **dez/2024**; a série de 2010 dá
   6,5→10,9. A ressalva, escrita para ser cuidadosa, é que criava o erro.
   Aproveitado para acrescentar o que a média do período escondia: o crédito
   **desaba** em 2023–24 (15,8 bi, abaixo da média 2013–19) — dos três sinais
   de demanda do Ato III, dois seguram e um se inverte no fim.
2. **Vão lavoura–pasto** dizia "120 a 130 km em todos os 40 anos". A série dá
   **122,6 a 135,0**; 10 dos 40 anos fora da faixa, inclusive 2024, cujo valor
   (135 km) o próprio texto citava 3 parágrafos adiante. → "entre 123 e 135".
3. **"Atenuam-se em no máximo 12%"** (§3.6.3): o maior recuo em
   `painel_espacial_dinamico.csv` é o M2, **14,6%**. → 15%.
4. **"Cai cerca de seis vezes"** (carbono): 51,59/7,58 = **6,8**. → "quase sete".
5. **Vale do Centro Goiano existe** (`tem_vale_emp=True`, dip 0,084). O texto
   dizia que Sul, Centro e Leste não tinham. → "Sul e Leste", com o Centro
   nomeado como vale raso.

**Três reescritas substantivas.**

- **Ato I não era pausa agrícola.** O texto dizia "a lavoura permanece onde já
  estava". Os dados: agricultura +1,83 Mha no Ato I a **0,122 Mha/ano**, contra
  0,128 no Ato II — ritmo absoluto praticamente igual; soja quase sextuplica
  (0,37→2,13). **Quem quebra em 2001 é a pastagem** (+0,248 → −0,076 Mha/ano).
  O rótulo "Ato II = expansão" sugeria aceleração da lavoura que não houve: o
  que muda em 2001 é a **fonte da terra**. Reescritos os dois atos. Ganho
  colateral: a periodização passa a ter significado mecânico, não descritivo.
- **A marcha tem componente leste** e o texto só reportava a norte. Agricultura
  +49,5 km leste (IC [22,6; 77,1]) contra +65,2 norte = resultante 82 km,
  **azimute 37°**. Pasto (14°) e rebanho (19°) são quase meridionais; a lavoura
  não. Pela D19 era reportável e não estava reportado.
- **B1 é identidade, não resultado** (§4.4.1). `fluxo ≡ taxa × estoque`: o
  β=+2,76 com R²w=0,43 é a definição se reapresentando. O conteúdo empírico
  está todo no **nulo** de B2b (a taxa não cai com a depleção, p=0,48,
  R²within≈0) — e não rejeitar "a taxa varia" ≠ estabelecer "a taxa é
  constante". Reescrito com a régua de nulo que o próprio trabalho exige.

**Três análises novas (#55, #56, #57)** — ver
`Textos/indice_logico_pipelines.md` para o detalhe. Resumo do que mudou aqui:

- **#55 (bootstrap de blocos)**: a Perna 1 **fica mais forte**. Veredito
  invariante em 6/6 tamanhos de bloco.
- **#56 (corrida de cavalos)**: **o achado que dói**. Posta a latitude na mesma
  regressão, a aptidão perde 62% da magnitude e a significância nas duas
  réguas (p_agrup 0,026→0,30; p_circ 0,13→0,47). ⇒ **D28**, novo
  "resultado superado", §3.7 nova, §4.3.2 com subseção própria, §5.3
  recalibrada, quadro de alcance, resumo e abstract ("gradiente de aptidão" →
  "gradiente Sul–Norte"). **O argumento da Perna 3 sobrevive** — o que cai é a
  atribuição a solo/clima.
- **#57 (qualidade do remanescente)**: veredito misto, entra como subseção nova
  em §4.4.2 e reforça §5.5.

**Forma.** `\notafig` criado no `main.tex` (a norma separa Fonte de Nota, e as
legendas carregavam meia dúzia de linhas de método dentro de "Fonte:") e
aplicado às 7 figuras. Tabela 1 (convergência dos métodos) → **Quadro**: era
textual e violava a convenção declarada no próprio preâmbulo. Nota da Tabela 3
passou a declarar **as duas** diferenças de convenção (campo alagado **e
silvicultura**, 5,58 vs 5,73 Mha) — só a primeira estava declarada, e sem a
segunda os fluxos do Sankey não fecham. Quadro novo com as **densidades de
carbono da D18** (75/95/120, 25/33/40, 8/13/18 Mg C/ha): produziam os 973 Mt e
não apareciam no texto.

**Fontes que faltavam no Quadro 2** (metade da Perna 3 e 4 rodava com fonte não
declarada): câmbio real efetivo e preços recebidos (**Ipeadata**, série GAC12,
deflator INPC, ponderação de exportações — o *shifter* central, e não estava em
lugar nenhum do documento), **MapBiomas Fogo Coleção 4**, FIRJAN/IFDM, CONAB,
malhas do geobr incluindo CNUC. Duas entradas novas no `.bib`
(`MapBiomas2025fogo`, `IPEA_Ipeadata`).

**Lista de leitura (§2.10)**: três frentes ganharam nome. **Souza Jr. et al.
(2020)** — a acurácia da própria Coleção, ausente num trabalho cuja limitação
central é comportamento de classificador; **Parente & Ferreira (2018)** —
mapeamento e qualidade de pastagem, a linha do laboratório de origem (com o
conflito de interesse anotado no `.bib`: o orientador é coautor); e a produção
regional sobre Goiás, com as duas perguntas que orientam a busca.

**Cronograma**: depósito e defesa separados pelo **prazo de leitura da banca**
(era a mesma célula), e o **produto do mestrado profissional** nomeado como
requisito formal a alinhar com o programa — pendência que o README registrava
desde 13/ago e o texto não enunciava.

**Contagens atualizadas**: 54 → **57 pipelines**, 27 → **28 decisões**, quatro
→ **cinco** decisões críticas na §3.7, cinco → **seis** réguas, quatro →
**cinco** verificações da marcha, quatro → **cinco** resultados superados.

### Auditoria da própria auditoria (19/ago/2026, mesmo dia)

O autor pediu para revisar tudo o que a leitura crítica havia mudado, e depois
para **tirar do texto o que não devia ter entrado**: a regra que ficou é que o
capítulo de resultados traz o resultado **correto**, e o defeito que o produziu
vive no registro de decisões (§3.7 e o quadro de superados) — nunca os dois
narrados em sequência no corpo.

**Escopo:** 80 asserções numéricas conferidas uma a uma contra os CSV (script no
scratchpad) — **0 falhas**.

**Confirmado.** O estimador da permutação do #56 reproduz o PanelOLS a 3e−17 nas
seis specs; VIF de S4 = **1,24** (a corrida é limpa); `exp_latitude` **não** é a
`exp_fronteira` do #38 renomeada (r=0,58). ⚠️ Precisão que faltava: **p=0,026 é o
piso** do teste (1/38) — para a latitude sozinha, nenhuma das 37 rotações supera
o observado; e o p=0,053 de S4 é decidido por **uma única** rotação.

**Dois erros meus.** (1) O β do #57 que eu citara (+0,011) era o inflado: hazard é
razão, 690 pares têm estoque <100 ha e os extremos são AMCs do **Sul** (região de
aptidão alta) com <1 ha, onde hazard=1,00 por construção. Grade de cortes: o sinal
sobrevive nas 3 regiões e em todos os cortes, a magnitude não. O texto passou a
citar **+0,004 (corte ≥1.000 ha; p<0,01)**. (2) Reconstruí a spec do B2b **por
chute** (`log1p(deplecao_refinada)`) e obtive sinal TROCADO; a spec real é
`deplecao_prev`, sem log. ⚠️ **Não reconstruir spec alheia por nome de coluna.**

**O defeito maior, pré-existente — #39B / D29.** Reproduzida a spec real
(β=−0,0152, r²w=−0,00023, batem à 4ª casa), o nulo do B2b **não sobrevive**:
`deplecao_prev` é documentada como fração 0..1 e vai a **−84,9** em **14%** do
painel (920 de 6.379), de 46 AMCs com estoque de 1985 minúsculo (mediana 544 ha ×
24.031 ha) cujo estoque *cresceu* — oscilação pasto↔savana pelo lado do estoque.
Tratado por qualquer via, **inclusive a que não descarta linha alguma**, β<0 e
significante (−0,07 a −0,31; 5 de 6 réguas). **A taxa CAI com a depleção** = atrito
de oferta, que é a hipótese pré-declarada pelo próprio #39 para β<0. B1 segue
identidade, quadrático segue nulo, e o **B2a já era −0,32 (p=0,002) na versão
publicada** — já contrariava hazard constante.

**Isso conserta um problema que eu mesmo criara.** Minha reescrita anterior punha a
Perna 4 num nulo fraco, depois de eu criticar o pipeline por pô-la numa identidade.
A versão correta não precisa de nenhum dos dois: na depleção **caem as duas
coisas**, estoque e taxa. Casa com o #57 e dá nome a parte do residual do #39.
Bônus: o cap. 5 **já dizia** "taxa de conversão cadente" enquanto o cap. 4 dizia
"a taxa não cai" — contradição interna anterior, resolvida a favor do cap. 5.

**O que foi RETIRADO no passe de enxugamento** (a pedido do autor):

- §4.4.1: os dois parágrafos que narravam o defeito de domínio e a meta-frase
  "essa correção fortalece a frente" → **um** parágrafo com o resultado e a faixa.
- §4.4.3: o parágrafo inteiro do "ritmo de emissão do Ato III não volta a cair
  (9,1 × 7,6)" seguido do seu próprio desmentido pela convenção de denominador
  (7,2 × 7,3). Sai tudo; fica só a composição (62% florestal → 2%), que é robusta.
- §4.4.2: a narração do β inflado do hazard → só o número do corte defensável.
- Quadro das densidades: a ressalva de que as faixas "ainda não foram reconferidas
  contra o texto integral" — viola a **regra da fonte conferida** (resolve-se na
  raiz, nunca com ressalva). A tarefa segue no cronograma, que é o lugar dela.
- §3.6.4: o parágrafo de ressalva sobre ADF/KPSS que terminava em "a conduta
  permanece a mesma" → uma oração dentro da frase que já classificava a série.
- §5.1: o parágrafo sobre circularidade × canal, condensado à metade.
- Meta-frases: "uma auditoria não devolve sempre menos do que encontrou", "o mérito
  de registrar isso é evitar que o trabalho seja citado como…", "corta contra a
  conveniência do argumento", "Guarde-se, porém, o número −0,44", "e o que ela
  desfaz" no título. O `−0,44` aparecia 3× e ficou 1×.
- A componente leste era reportada e qualificada em dois lugares → um.

**Propagado à viz publicada:** quatro trechos ainda afirmavam "a taxa não cai com a
depleção (p=0,48)" — corrigidos (não é enxugamento, é inconsistência real), mais o
card da D29 e os contadores. `verificar_reforma.py` de 28 → 29.

**Figura nova (a 8ª)**: `cap4_horse_race.pdf`, a corrida entre exposições, em
§4.3.2. Entrou porque o resultado do #56 é o achado novo mais consequente e o
cap. 4 já tinha o precedente de gráfico de coeficientes para resultado
negativo (a Figura 6). A leitura pretendida é o **contraste** S1 × S4 — por
isso as seis especificações ficam empilhadas na mesma escala, e não em painéis
—, e o `p` ao lado de cada ponto é o de **permutação circular**, não o agrupado
que desenha a barra; as duas réguas estão declaradas na nota como não
comparáveis. As figuras 7 e 8 trocaram de número.

**Estado ao fim**: `verificar.py` 0 erros / 0 avisos; `compilar.ps1` sem
Overfull e sem referência indefinida; **82 páginas**, 8 figuras;
`verificar_reforma.py` todas passaram. 54→**58 pipelines** (#55, #56, #57, #39B),
27→**29 decisões**.

**Dois avisos que o `verificar.py` pegou na minha própria escrita** (e é para
isso que ele existe): "Mha" usado antes da definição, porque a reescrita do
Ato I passou a citar Mha antes do parágrafo do Ato II que definia a sigla; e
"estoque **disponível**" no parágrafo da identidade, que é exatamente a palavra
proibida pela regra de voz do Cerrado remanescente.

**Dois números meus que a conferência derrubou** (corrigidos antes de fechar):
escrevi que a emissão do Ato III subia 20% e que a conversão migrara para
formações **mais** densas — a segunda metade é falsa, a emissão migra para
savana (62% florestal no Ato I → 2% no Ato III), e o "+20%" depende da
convenção de denominador (intervalos: 7,6→9,1; anos: 7,2→7,3). Reescrito para
o enunciado que sobrevive às duas convenções: a emissão anual **não volta a
cair**. E a perda de vegetação do Ato I é 0,27 Mha/ano (4× os atos seguintes),
não 0,29 (5×), que eu havia obtido por subtração em vez de ler a série.

### `verificar.py` — invariantes (17/ago/2026)

Teste de regressão, **não** auditoria: roda sempre as mesmas cinco checagens e
dá sempre o mesmo resultado. Existe porque "está sem erros?" não tem resposta,
e "alguma invariante quebrou?" tem.

```powershell
python verificar.py       # tudo
python verificar.py 3     # só a invariante 3
```

1. todo `\ref` resolve a um `\label`; 2. toda chave citada existe no `.bib` e
nenhuma entrada fica órfã; 3. lista de leitura do `.bib` == §2.10 (casa por ano
+ sobrenome, robusto a "Meyfroidt, P.; Lambin, E.F." × "Meyfroidt e Lambin");
4. toda sigla é definida na primeira ocorrência; 5. frases proibidas ausentes e
âncoras de calibragem presentes.

⚠️ **O verificador nasceu com três defeitos próprios, todos corrigidos:** o
casador de nomes da 3 não via nome e ano em linhas diferentes; a 4 fazia ruído
com sigla em célula de tabela; e a 5 acusava justamente a frase que **proíbe**
citar os p-valores agrupados, além de não enxergar frase quebrada em duas
linhas (por isso a 5 agora lê texto normalizado e poupa o que está entre
aspas — citação direta reproduz a fonte).

**Estado: 0 erros, 12 avisos.** Os 12 são de caps. 3 e 4, **fora do escopo
varrido**, e são reais: as expansões de SIDRA, PPM, PIB, IPCA, IPEA, INPE,
PRODES, SICOR e Embrapa existem **só** em `pre/siglas.tex` e não aparecem no
corpo; AMC é expandida no cap. 1 sem introduzir a sigla, que estreia nua no
cap. 3; `Mha` e `EPSG` nunca são expandidas. Pendente para a revisão do cap. 3.

**Compilação:** 76 págs, 0 overfull, 0 indefinida, 0 erro de BibTeX; **29/29
asserções conferidas no texto extraído do PDF** (12 entraram, 7 sumiram, 10 de
regressão sobre 15–16/ago). Mather segue fora da lista de referências,
conferido linha a linha — e não pela busca ingênua, que o acha no corpo, onde
ele deve mesmo estar.

### Revisão de consistência (13/ago/2026)

Varredura dos caps. 00–04 contra os CSVs e os docs de `Textos/`. Corrigidos:

1. **Erro aritmético (cap. 3, AMC):** dizia "cerca de 62 municípios deixam de
   ser analisáveis isoladamente" — herdado de
   `metodologia/areas_minimas_comparaveis.md`, que confunde os 62 emancipados
   pós-1985 com o efeito da agregação. Verificado no `amc_crosswalk_goias.csv`:
   são **133 municípios em 53 grupos**, e a malha perde **80 unidades**
   (246 − 166). Uma banca faz essa subtração.
2. **Rótulo errado (cap. 4, Perna 4):** "a soja plantada sobe 244%" —
   contradizia os "+38% no estado" do parágrafo anterior. O 244% é o **ritmo
   de expansão** (Δ da taxa anual entre Atos II e III, `#33`), não o
   crescimento do estoque plantado. Corrigido e a diferença entre as duas
   réguas explicitada. ⚠️ A viz (`index.html`, ~l. 1943 e 1974) tem a mesma
   imprecisão.
3. **Coleção 10 → 10.1** em `pre/resumo`, `pre/abstract` e cap. 1 (o cap. 3 e
   a viz já diziam 10.1).
4. **Moran (cap. 3):** 115/140 é a malha municipal; o painel roda em AMC
   (125/140). Passou a declarar as duas — e a frase fica mais forte.
5. **0,06 × 0,071 Mha/ano** (cap. 4): eram saldo **líquido** e fluxo **bruto**
   de conversão, apresentados como se fossem a mesma medida. Rotulados.
6. **4,10 × 4,11 Mha** (cap. 4): pareciam erro de digitação um do outro. São
   `veg→pastagem` (cruzamento 1985↔2024) e a depleção do estoque convertível
   (10,67 → 6,56 Mha). O segundo passou a dizer de onde vem.
7. **120–130 km × 135 km** (cap. 4): "em todos os quarenta anos … de 120 a
   130 km" contradizia o valor de 2024 duas frases adiante. Virou "cerca de".
8. Mistura da idade da pastagem passou a trazer **μ ≈ 4 e ≈ 23 anos** junto
   dos σ (antes as duas populações só apareciam pelo desvio).

### Siglas (13/ago/2026)

`pre/siglas.tex` — **lista de abreviaturas e siglas** pré-textual (ambiente
`siglas` do abnTeX2, ordem alfabética, entre o abstract e o sumário). Regra
adotada: **toda sigla da lista também é definida na primeira ocorrência no
texto**, e nenhuma sigla entra na lista sem aparecer no corpo (FDR, ILP, VAR e
LULC foram retirados por isso — o texto escreve por extenso).

Definidas na primeira ocorrência neste passe: UFG, PPGCIAMB (o memorial dizia
"CIAMB", que não bate com a capa), IBGE, MATOPIBA e **iLUC** (agora com a
origem inglesa, no cap. 1 — antes a sigla aparecia com o termo em português,
sem dizer de onde vinha), USDA-ERS, MAUP, SIDRA/PAM/PPM/PIB/IPCA, SICOR/BACEN,
IDH-M/IPEA, Trase, Embrapa, PRODES/INPE, EPSG/SIRGAS, STARS, ADF/KPSS, BIC,
SAR/SEM/LISA, APP, CO₂e e IFDM. `MAUP` saiu do quadro do cap. 2 (a sigla
aparecia antes de existir) e passou a ser definida onde o cap. 3 a discute.

⚠️ A expansão do **PRODES** ficou descritiva ("sistema de monitoramento do
desmatamento por satélite do INPE") em vez de tentar o nome oficial, que varia
entre fontes — conferir antes da versão final.

Fora do `qualificacao/`, no mesmo passe: `Textos/guia_de_leitura.md` perdeu as
três ocorrências de "iLUC **refutada**" (frase proibida desde 28/jul) e o
"D1–D20" desatualizado. **Pendente:** `Textos/narrativa_pipelines.md` (l. 62 e
757) ainda diz "as vinte decisões (D1–D20)".

**Decisões de forma já tomadas:**

- Fonte Times (newtx); typewriter da Latin Modern (`\ttdefault{lmtt}` — a tt
  inclinada da txfonts falha no MiKTeX).
- Títulos em fonte 12 (`\ABNTEX*fontsize` = `\normalsize`), hierarquia por
  negrito/caixa alta — o default `\Large` do abnTeX2 destoa do padrão BR.
- Margens ABNT 3-3-2-2: o bloco de texto fica 0,5 cm à direita do centro
  (espaço de encadernação) — é norma, não defeito.
- `\notaguia{}` (não `\nota` — colide com abntex2cite) para orientação de
  trabalho visível no PDF; some conforme o texto definitivo entra.
- Capa: Victor Alves Rodrigues Amaral; orientador Prof. Dr. Laerte Guimarães
  Ferreira Júnior (ordem correta: Guimarães Ferreira).
- Resumo/abstract têm rascunho real (calibrar ao final, quando os capítulos
  fecharem).

**Convenções:**

- Referências `[conferir]` no `.bib`: verificar páginas/DOI antes da versão
  final.
- `main.pdf` não é versionado; PDFs de marco vão em `entregas/`.
- Números citados no texto seguem a disciplina do projeto: rastreáveis a um
  CSV de `outputs/`; capítulos 1–2 mantêm números de enquadramento e deixam
  os resultados quantitativos para o cap. 4.
- Regulamento do PPGCIAMB (Res. CEPEC 1932/2025) não fixa formato — seguimos
  ABNT/estrutura acadêmica convencional (confirmado pelo autor, 11/ago/2026).
