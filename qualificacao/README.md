# Qualificação — texto ABNT (abnTeX2)

Documento de qualificação do mestrado (PPGCIAMB/UFG), gerado a partir do
material da visualização (`Visualizacao/index.html`) e de `Textos/`.

## Estrutura

```
main.tex          — preâmbulo, dados da capa, ordem dos capítulos
pre/              — resumo, abstract e lista de abreviaturas e siglas
cap/              — um .tex por capítulo (00 = memorial, 01–06 = texto)
pos/apendices.tex — apêndices (pipelines, decisões D1–D27, glossário)
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
| 7 — teto de oferta | `cap4_fronteira_oferta.pdf` | `fronteira_decomposicao.csv`, `fronteira_regional.csv` (#39) |

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
- `cap/02_referencial.tex` — **Referencial teórico** (6 eixos + síntese com
  quadro de posicionamento). Fonte: `Textos/referencia/referencial_marcha.md`.
  Autores sem vínculo bibliográfico (Boserup, Becker, Meyfroidt, Lefever etc.)
  aguardam conferência antes de entrar no `.bib` (comentados no fim do arquivo).
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

- `cap/06_cronograma.tex` — **PRÓXIMO PASSO** (a preencher com o orientador),
  e `pos/apendices.tex` (A pipelines, B decisões D1–D27, C glossário).

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
