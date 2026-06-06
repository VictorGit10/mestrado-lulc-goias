# Janelas temporais — estratégia de análise multi-resolução

**Decisão D12** (2026-06-06): toda análise **longitudinal** que precise resumir o
tempo em períodos (médias, taxas, transições, deslocamentos "por período") é
rodada em **múltiplas resoluções temporais** e relata a **concordância** entre
elas — em vez de depender de um único recorte. Primeira aplicação: [Pipeline #35](../pipelines/35_robustez_janelas.md)
sobre [#32](../pipelines/32_centro_massa.md) e [#33](../pipelines/33_transicoes_regionais.md).

> **Para que serve este documento**: é um *método reutilizável*. Qualquer análise
> nova "por período" da dissertação deve seguir a receita da seção final.

---

## O problema: onde você corta o tempo muda o que você vê

Resumir 40 anos em "períodos" é inevitável (ninguém narra ano a ano), mas **binar
o tempo é uma escolha** — e escolhas diferentes produzem números diferentes.
Três armadilhas:

1. **Cherry-picking (mesmo sem querer)**: é fácil, inconscientemente, preferir o
   recorte que deixa o achado mais bonito. A banca vai perguntar "e se você
   tivesse cortado em outro ano?".
2. **Durações desiguais**: períodos de tamanhos diferentes não são comparáveis em
   total absoluto (um período curto parece "menor" só por ser curto).
3. **Circularidade**: se você *define* os períodos a partir de uma variável e
   depois "descobre" que os períodos diferem nessa variável, você só encontrou o
   que construiu.

A defesa contra as três é a mesma: **rodar a análise em várias réguas de tempo e
mostrar o que sobrevive.** O que aparece em todas as réguas é robusto; o que só
aparece em uma pode ser artefato do recorte.

---

## As 4 formas (o menu de resoluções)

| Forma | O que é | Para que serve | Força | Fraqueza |
|---|---|---|---|---|
| **1. Completa** | série **contínua** (ano a ano) + **janela única** (1985–2024) | a verdade-terra (trajetória sem binning) + o resumo de uma linha (líquido) | zero escolha de corte; máxima robustez | não mostra estrutura temporal interna |
| **2. Atos** | períodos **data-driven** (quebras estruturais, [#29](../pipelines/29_triangulacao_periodizacao.md)) | o **frame narrativo** — os "regimes" da história | fronteiras justificadas pelos próprios dados | durações desiguais; risco de circularidade; é a régua a ser *testada* |
| **3. Grade fina** | blocos **regulares** de 5 anos (8 blocos: 1985–89 … 2020–24) | **robustez exógena** + localizar fenômenos no tempo | independente das fronteiras dos atos → teste válido | mais ruidosa (menos anos por bloco) |
| **4. Décadas** | blocos **regulares** de 10 anos (4 blocos) | robustez exógena grossa, familiar ao leitor | estável, intuitiva | grossa demais para fenômenos curtos (borra o recente) |

> **Por que "4 formas" e não 5**: a forma 1 (Completa) tem duas faces — contínua e
> janela única — mas é uma só ideia ("sem períodos"). As formas 2–4 são as três
> maneiras de *ter* períodos: uma narrativa (atos) e duas réguas exógenas (fina e
> grossa).

### A intuição de cada uma

- **Contínua** é o chão de fábrica: a trajetória anual, sem nenhuma interpretação imposta. Tudo o mais é um *resumo* dela. Se um achado não está na série contínua, desconfie.
- **Janela única** é o título de jornal: "entre 1985 e 2024, X mudou Y". Depende só dos extremos — é idêntico em qualquer régua de binning.
- **Atos** é o enredo: capítulos com começo, meio e fim *motivados pelos dados*. É onde a narrativa mora — mas é justamente por isso que precisa ser *validada* pelas réguas exógenas.
- **Grade fina e décadas** são as réguas neutras: cortam o tempo sem olhar para a história, então se o achado aparece nelas, ele não é invenção do enredo.

---

## Os 4 princípios de uso

1. **A série contínua é a verdade-terra.** Calcule-a primeiro. Todo período é um resumo dela; um achado que não aparece no contínuo é suspeito de ser artefato de binning.
2. **Anualize sempre que comparar períodos** (taxa por ano = total ÷ nº de anos). Períodos de durações diferentes só são comparáveis em taxa, nunca em total absoluto. *(Ex.: o Ato III tem 5 anos e o Ato I tem 16; comparar Mha totais faria o III parecer ínfimo.)*
3. **A régua de robustez é REGULAR e EXÓGENA, nunca aninhada no período narrativo.** Sub-dividir os atos em blocos *re-importa as fronteiras dos atos* — anula o teste. Uma grade de 5 anos sobre a série inteira é independente das fronteiras: é isso que a torna um teste honesto. *(Bônus: alinhe a grade para que o último bloco coincida com o período recente de interesse — aqui, 2020–24 = Ato III — deixando o recente diretamente comparável.)*
4. **Cuidado com circularidade.** Se os períodos foram definidos a partir da variável X (ex.: os atos vêm em parte de transições, [#29](../pipelines/29_triangulacao_periodizacao.md)), **não** use os atos como única régua para analisar X. Use o tempo **contínuo** (painel/séries com defasagem) ou uma grade exógena. *(Foi por isso que a [Camada 3 / #34](../pipelines/34_deslocamento_espacial.md) rodou em tempo contínuo.)*

---

## Como ler a concordância entre as formas (tabela de decisão)

| Padrão observado | Leitura | O que fazer |
|---|---|---|
| Achado aparece em **todas** as réguas | **robusto** | pode afirmar com segurança |
| Aparece nas finas, **some na grossa** | **sensibilidade de resolução** — o fenômeno é *curto/localizado* no tempo | informativo, não é problema: **localize** o fenômeno (qual janela?) e prefira réguas que o isolem |
| Aparece nos **atos**, mas **não na grade exógena** | pode ser **artefato das fronteiras** escolhidas | **rebaixe** o achado; investigue por que a fronteira importa |
| Não aparece na série **contínua** | provável **artefato de binning** | descarte ou investigue |

*Exemplo real (#35)*: a desaceleração recente da agricultura aparece nos **atos** e na **grade de 5 anos** (que isolam 2020–24), mas **dilui nas décadas** (a década 2015–2024 mistura o boom pré-2020 com o congelamento). Leitura pela tabela: **sensibilidade de resolução** → o congelamento é um fenômeno **pós-2020**, e réguas grossas o borram. Isso *valida* o uso de janelas finas, em vez de invalidar o achado.

---

## Receita para uma análise nova (passo a passo)

Para qualquer métrica "por período" (taxa de conversão, deslocamento, correlação por janela, etc.):

1. **Série contínua primeiro** — calcule a métrica ano a ano (a verdade-terra).
2. **Resumo de uma linha** — a janela única 1985→2024 (o líquido).
3. **Atos (anualizado)** — bine pelos atos para a narrativa; sempre em taxa/ano.
4. **Grades exógenas (anualizadas)** — re-bine em 5 anos e em décadas.
5. **Concordância** — compare as réguas pela tabela de decisão acima; reporte explicitamente **o que sobrevive** (robusto) e **o que é sensível à resolução** (e por quê).

> **Quando NÃO precisa das 4 formas**:
> - **Painel/séries com defasagem** (Granger, lead-lag, efeitos fixos): usam o tempo **contínuo** nativamente — não binam. A régua de período entra, se entrar, só como *interação de robustez*. *(Camada 3 / #34.)*
> - **Análises transversais** (um único ano, ex.: Censo 2017): não têm questão temporal.

---

## Relação com a periodização dos atos

Os **atos** ([#29](../pipelines/29_triangulacao_periodizacao.md), `config_periodos.py`) continuam sendo a **régua narrativa oficial** da dissertação — data-driven e citável. A Decisão D12 **não os substitui**; ela diz **como usá-los com honestidade**: como um dos quatro olhares, validado pelas réguas exógenas, sempre anualizado, e nunca como única régua para analisar aquilo que os definiu.

## Onde já foi aplicado

- **[#35](../pipelines/35_robustez_janelas.md)** — robustez de [#32](../pipelines/32_centro_massa.md) (centro de massa) e [#33](../pipelines/33_transicoes_regionais.md) (transições) sob atos / grade-5a / décadas (**face de fronteira**: onde cortar). Resultado: os achados-manchete são robustos; a única sensibilidade (congelamento recente da agricultura) é de resolução e localiza o fenômeno em pós-2020.
- **[#36](../pipelines/36_robustez_janela_slope.md)** — robustez do slope do [#17](../pipelines/17_taxas_lulc.md) à **largura da janela móvel** (3/5/7/10 anos). É a **face de resolução** da D12 (quão fina é a suavização), distinta da face de fronteira do #35 (*binning* disjunto vs. *smoothing* sobreposto). Resultado: as manchetes de slope sobrevivem à largura; a aceleração (D5) é frágil — só o pico da pastagem de 2004 é uma inflexão robusta às 4 janelas.
- **[#34](../pipelines/34_deslocamento_espacial.md)** — Camada 3 rodou em tempo contínuo (princípio 4, anti-circularidade).

## Ver também

- [areas_minimas_comparaveis.md](areas_minimas_comparaveis.md) — Decisão D11 (unidade **espacial** constante; a D12 é a contraparte **temporal**).
- [espacializacao.md](espacializacao.md) — decisões de malha/CRS.
- `scripts/config_periodos.py` — fonte única dos atos.
