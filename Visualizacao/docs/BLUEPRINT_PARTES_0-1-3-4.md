# Blueprint das Partes 0, 1, 3 e 4 — a moldura da história

> Prancheta de texto (jul/2026). Complementa
> [`BLUEPRINT_PARTE2.md`](BLUEPRINT_PARTE2.md) (o núcleo das 4 pernas). Aqui está a copy
> da **moldura**: a abertura (0), o scroll dos 40 anos (1), o veredito (3) e a oficina
> (4). Mesmo tom: sóbrio, editorial, voz de descoberta. Números conferidos contra o
> saldo atual do site e a `narrativa_pipelines.md`; reconferir antes de congelar.
>
> Legenda: 🎞️ = peça interativa · 🔗 = pipelines/blocos que alimentam · *(itálico)* =
> nota editorial, não é copy.

---

## PARTE 0 · Abertura (hero) — entrega a tese + planta a virada

*Decisão travada: o hero entrega o destino; o suspense fica no "por quê".*

**Sobrelinha (eyebrow)**
> Dissertação CIAMB-UFG · Goiás · 1985–2024

**Título**
> A marcha ao norte

**Lede**
> Em quarenta anos, toda a fronteira agropecuária de Goiás se moveu para o norte —
> pasto, boi e lavoura, cerca de 70 km cada. A explicação óbvia — a soja do Sul
> empurrando o pasto para longe — é boa demais para ser verdade, e este trabalho mostra
> por quê. Cada pixel desta tela é um quadrado de 30 metros no chão; cruzamos 1,5 bilhão
> deles, ano a ano, para rastrear a cicatriz que os mercados e as leis deixaram no
> território. A história se conta em **três atos** no mapa — e se resolve em **quatro
> perguntas**.

**Chamada (CTA)**
> Comece pelo mapa de 1985 ↓

*Alternativa de título, se "A marcha ao norte" parecer entregar demais cedo:
"O território que se reorganizou" (mais neutro). Recomendo o primeiro — é a imagem que
o leitor levará embora.*

---

## PARTE 1 · Os 40 anos no mapa — o fenômeno

🎞️ **Peça-central: o scroll dos 40 anos** (`timeline.js` + seção `story`), intocado.
🔗 #10 (mapas raster GEE) · #12/#19 (transições, Sankey) · saldo do painel UF.

### 1.1 — Contrato de leitura ("como ler")

*Versão enxuta do bloco atual "Como ler esta linha do tempo". Mantém os três painéis
(atos / referências / navegar), mas com uma frase nova no topo que posiciona o mapa como
o fenômeno — ainda não a tese.*

**Título**
> Como ler os 40 anos

**Lede**
> O que vem a seguir é o **fenômeno bruto**: quatro décadas de uso da terra, ano a ano,
> no mesmo enquadramento. Ainda não é a tese — é o que aconteceu no chão, antes de
> perguntarmos *onde* e *por quê*. A série se organiza em **três atos**, definidos por
> triangulação estatística (não escolhidos a dedo), marcados pelas faixas coloridas da
> régua acima; os **pinos pretos** são referências institucionais que contextualizam as
> inflexões — não são o esqueleto da história.

*(Os três sub-blocos — "Os três atos", "Referências institucionais", "Como navegar" —
seguem como estão hoje. O acordeão "Como os atos foram definidos?" pode encolher: a
versão longa vive na Parte 4, a oficina.)*

### 1.2 — Os três atos (passos do scroll)

*Copy de cada era. Mantém-se descritiva — é o mapa falando, não a tese. Refinada a
partir da atual, sem antecipar a investigação.*

**Ato I · Pastagem como herança · 1985–2000**
> *Tese do ato:* O ponto de partida não é uma paisagem natural — é uma fronteira que já
> se moveu.
> *No mapa:* O dourado que domina o centro-sul é pastagem — herança do POLOCENTRO e do
> PRODECER, que abriram cerca de um terço do estado para a pecuária extensiva na década
> anterior. O verde escuro do norte e do nordeste (Paranã, Vão do Paranã) é o Cerrado
> que sobreviveu. A agricultura ainda é incipiente: manchas de rosa no sudoeste. Sob a
> hiperinflação, nenhum cálculo agrícola de longo prazo fecha.

**Ato II · Expansão e intensificação · 2001–2019**
> *Tese do ato:* A soja abre caminho no sudoeste, e o motor não é uma política agrícola —
> é a moeda estável.
> *No mapa:* O Plano Real (1994) faz o que nenhum programa setorial conseguiu — permite
> calcular o futuro; a Lei Kandir (1996) zera o ICMS sobre a exportação de grãos. O
> sudoeste (Rio Verde, Jataí, Mineiros) se veste de rosa: a lavoura avança sobre o pasto.
> A pecuária segue gigante em área, mas a dinâmica econômica do agronegócio já pertence à
> soja.

**Ato III · Conversão seletiva · 2020–2024**
> *Tese do ato:* A inércia de quatro décadas se quebra — o pasto recua e a vegetação
> ensaia um piso.
> *No mapa:* Pela primeira vez o pasto encolhe e a vegetação nativa registra uma
> recuperação sutil. O Cerrado resiste no norte (Vão do Paranã); as lavouras se
> estabilizam no oeste. Com a vegetação natural em 34,9% do estado em 2024, Goiás toca o
> limite do bioma — mas a queda livre de quarenta anos parece, enfim, encontrar um piso.

### 1.3 — O fecho: o saldo e os fluxos

*Fecho da Parte 1. Dá o baseline factual e entrega o bastão à investigação. O Sankey é
mantido (é bonito e carrega os fluxos).*

**Bloco A — O que 40 anos deixaram (saldo)**

*Grid de quatro números-choque, como hoje:*
> **−5,8 Mha** · Vegetação natural perdida — 17,65 → 11,88 Mha (51,9% → 34,9% do estado).
> **×4,8** · Agricultura — 1,17 → 5,58 Mha (a soja sozinha: ×12 em área, ×13 em produção).
> **+1,0 Mha** · Pastagem — saldo enganoso: sobe até ~14,8 Mha em 2003 e recua (U invertido).
> **×1,35** · Lotação bovina — 1,01 → 1,36 UA/ha: o rebanho cresce 46% e a área de pasto, só 9%.

> *Em uma frase:* a vegetação perdeu 5,8 Mha, a agricultura quase quintuplicou e a
> pastagem *parece* estável no saldo — mas saldo líquido esconde o caminho dos hectares.

**Bloco B — Para onde os hectares foram (Sankey)** 🎞️

> O saldo diz *quanto* cada classe ganhou ou perdeu; esconde *de onde para onde*. O
> diagrama cruza o uso de cada pixel em 1985 com o do mesmo pixel em 2024. Três fluxos
> enquadram tudo:
> **4,11 Mha** vegetação → pastagem (o desmatamento histórico, concentrado nos anos
> 1980–90); **2,73 Mha** pastagem → agricultura (a conversão moderna, que expande a
> lavoura sem desmatar direto); **1,29 Mha** vegetação → agricultura direta (menor, mas
> ganha peso no nordeste após 2010).
>
> *Em uma frase:* dois fluxos mandam — vegetação→pasto (o desmatamento antigo) e
> pasto→lavoura (a conversão recente) —, e a pastagem é o elo intermediário de quase
> tudo.

*Bridge para a Parte 2:* o texto encerra aqui e a Parte 2 abre com "A pergunta que o
mapa não respondeu" (ver `BLUEPRINT_PARTE2.md`) — o saldo e os fluxos deram o *quanto* e
o *de onde para onde*; falta o **onde no estado** e o **por quê**. Não repetir a ponte
nos dois lados: ela vive na abertura da Parte 2.

---

## PARTE 3 · O veredito

*Fecho da investigação. Três beats: a tese em uma frase; a assinatura de honestidade; os
limites. É onde a peça cobra o investimento do leitor.*
🔗 `narrativa_pipelines.md` (Encerramento) · `indice_logico_pipelines.md` (Parte 1 e as
7 autocorreções) · `ensaio_a_investigacao.md`.

### 3.1 — A tese, em uma frase (callout central)

*Componente destacado — o clímax textual. Reusa o estilo do `tese-callout` atual.*

> **Goiás viveu uma reorganização espacial da produção agropecuária entre 1985 e 2024** —
> intensificação no Sul, fronteira no Norte —, coordenada por **forças de mercado comuns**
> (câmbio, crédito, preço) sobre um **gradiente estrutural de aptidão**, e limitada por um
> **teto de oferta** de Cerrado convertível que só resta no norte.
>
> Não foi um **deslocamento causal** de uma região sobre a outra — a hipótese óbvia do
> vazamento intra-estadual (iLUC) foi **testada e refutada**. É uma descrição
> empiricamente verificável, não uma metáfora.

### 3.2 — A assinatura do trabalho: uma investigação que se autocorrige

*Painel curto, em destaque — o "por que confiar nisto". NÃO é rodapé.*

**Título**
> Por que confiar nisto: o trabalho foi atrás dos próprios erros

**Corpo**
> A parte mais rara desta investigação não são os achados — são as vezes em que ela se
> corrigiu, sozinha e datada, antes que qualquer banca o fizesse. Sete correções sustentam
> a honestidade da tese:

*(Lista compacta, uma linha cada — cada item é um "eu achava X; o dado disse Y".)*
> · **A lógica do pasto jovem era do plantio direto?** Não — era confundidor de latitude. *(#40 → D14)*
> · **O fogo lidera a fronteira no tempo?** Não — só na geografia; co-evolui, não antecede. *(#41)*
> · **A bimodalidade é causada pela região?** Não — coexiste dentro de cada região; o tempo pesa mais. *(#28C)*
> · **O Norte antecede o Sul (o dado que invertia a tese)?** Não — regressão espúria; some com o método certo. *(#42 → D16)*
> · **A "muralha norte" é a vegetação inteira?** Não — é só a floresta; o campo nativo recuou. *(#44)*
> · **Calcário e assistência técnica explicam a geografia?** Não — somem sob o gradiente 2D, como o plantio direto. *(#40B)*
> · **A infra de exportação lidera a fronteira?** Não — e o regressor "volume" era produção disfarçada; o achado caiu 9×. *(#45)*
> · *(bônus)* **Faltava barra de erro na marcha?** Sim — agora todo ΔNorte vem com IC95%; a vegetação inclui zero. *(D19)*

> *Em uma frase:* uma tese que perseguiu a hipótese que mais a favorecia e a derrubou é
> mais forte do que uma que só coleciona confirmações.

### 3.3 — O que o trabalho NÃO afirma (os limites honestos)

*Bloco discreto, fechando o veredito com a mesma disciplina das pernas.*

> · Não se afirma que o **iLUC não existe** — apenas que o canal intra-estadual testado
>   não se confirma.
> · O **drive comum** é *corroborante, não estabelecido*: o câmbio é o candidato mais
>   forte, não uma causa provada.
> · O **Ato III** tem só 4–5 anos — a desaceleração é recente, e o tempo dirá.
> · "**Convertível**" e "**protegida**" são proxies com teto declarado (MapBiomas + malha
>   de UCs), não o cadastro pixel a pixel.
> · O recorte por mesorregião é grosso — mas, onde deu para testar na malha fina (AMC), a
>   conclusão sobreviveu.

**Chamada final**
> Como cada número foi apurado — a detecção dos atos, as réguas de robustez, as vinte
> decisões metodológicas, os limites — está na **oficina**, abaixo. ↓

---

## PARTE 4 · A oficina (era a aba Métodos) — moldura

*Deixa de ser aba: vira o fecho do scroll único, apêndice para quem quiser descer à
metodologia. O corpo reusa os blocos M1–M6 atuais, consolidados. Aqui só a copy de
moldura e a nova organização; as exposições de método já existem no site.*

**Abertura da oficina**
> Tudo o que você leu tem uma bancada por trás. Esta seção é para quem quer conferir — não
> é preciso ler para entender a tese, mas é o que permite *confiar* nela.

**Organização proposta (consolida M1–M6):**

1. **Como os três atos foram detectados** — a periodização data-driven (triangulação de
   quatro métodos; a candidata a 4º período rejeitada). *Consolida o M1 atual + o acordeão
   longo que sai da Parte 1.*
2. **As réguas de robustez** — as quatro provas independentes a que cada manchete foi
   submetida: tempo, latitude, integração, espaço (mais a incerteza por bootstrap).
   *Funde M2 (as métricas) + M3 (camadas de evidência) numa peça só, orientada a "como
   sabemos que sobrevive".*
3. **A vitrine do painel** — o inventário de dados (fontes, cobertura, o que entra e o que
   falta). *Mantém o M4 (`inventario.js`).*
4. **As vinte decisões (D1–D20)** — a régua comum de todos os pipelines, em **tabela
   colapsável** de referência. *Recolhe o M5 num único `details`.*
5. **Os limites** — as fragilidades declaradas. *Mantém o M6 — é honestidade, fica
   visível.*

**Fecho da peça (rodapé)**
> *Dissertação CIAMB-UFG · Goiás 1985–2024 · dados MapBiomas Coleção 10.1, IBGE/SIDRA,
> BACEN/SICOR, IPEA, Trase, INPE. Anexo digital de uma dissertação — não a substitui.*

---

## Ordem de leitura final (o scroll inteiro, de cima a baixo)

```
0 · Hero — a marcha + a virada
1 · Os 40 anos no mapa  ── scroll 40 anos → saldo → Sankey
        ↓ "o mapa não respondeu onde nem por quê"
2 · A investigação  ── hipótese tentadora → Perna 1 (trajetórias) → Perna 2 (idade do
        pasto) → Perna 3 (o clímax) → Perna 4 (teto)
        ↓
3 · O veredito  ── a tese em uma frase → a autocorreção como assinatura → os limites
        ↓
4 · A oficina  ── periodização · robustez · painel · decisões · limites
```
