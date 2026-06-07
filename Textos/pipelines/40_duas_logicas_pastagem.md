# Pipeline #40 — As duas lógicas da pastagem: espacialização + plantio direto

**Script**: `scripts/duas_logicas_pastagem.py`
**Status**: ✅ Concluído (2026-06-07)
**Outputs**: 4 CSVs (`duas_logicas_amc.csv`, `duas_logicas_municipal.csv`, `duas_logicas_cruzamento.csv`, `duas_logicas_robustez.csv`) + 5 PNGs em `outputs/duas_logicas/` (`mapa_logica_dominante_amc`, `pixels_mecanismo`, `gradiente_latitude`, `cruzamento_plantio_direto`, `tipologia_carreira_terra`).
**Depende de**: #28 (idade da pastagem na conversão), #27/Censo 2017 (plantio direto), #25 (AMC + crosswalk).

## Pergunta de pesquisa

O #28 provou que a conversão pasto→agricultura em Goiás é **bimodal** (GMM com ΔBIC
estratosférico): um pico **jovem** (~5a) e um **antigo** (~22a), assinatura de dois
mecanismos coexistentes — **rotação/trampolim premeditado** (pasto é uma fase curta de
um sistema de lavoura) vs. **reserva oportunística** (pasto antigo ativado por
oportunidade exógena). Mas o #28 parou em dois lugares:

1. **Espacialmente** ficou na mesorregião (5 unidades) — não disse *onde*, finamente,
   cada lógica domina.
2. **Estruturalmente** cruzou a idade só com **choques de fluxo** municipais (Δ SICOR,
   Δ VA agro) e achou **nada** (r≈0,03, n.s.), concluindo que "os mecanismos operam
   abaixo da escala municipal".

Este pipeline puxa o fio #2 do backlog: **espacializar** as duas lógicas (AMC e
município) e **cruzá-las com a estrutura do sistema agrícola** — o **plantio direto**
(Censo 2017), proxy de integração lavoura-pecuária (ILP)/rotação. A pergunta-teste era:
a idade-na-conversão é ilegível na escala municipal, ou só faltava cruzar com a variável
certa (estrutura, em vez de fluxo)? **Resposta (após verificação): segue largamente
ilegível** — estrutura e fluxo co-variam igualmente no gradiente Sul→Norte; o que o
pipeline entrega de sólido é a **geografia** das duas lógicas, não um preditor próprio.

## O que é novo vs. #28

| | #28 | #40 |
|---|---|---|
| Unidade espacial | mesorregião (5) | **AMC (166) + município (246)** |
| Classificação por mecanismo | regra por pixel (existe) | **agregada à unidade** (mistura + índice) |
| Cruzamento | fluxo em painel (muni,ano) → nulo | estrutura/fluxo em recorte transversal + **parcial \| latitude** |
| Síntese | — | **tipologia "carreira da terra"** (regra + k-means) |

## Método

Reusa a regra de decisão do #28 (`classificar_mecanismo`): pixel não-censurado é
**Premeditado curto** (veg.nat, ≤8a), **Rotação** (agricultura, ≤8a),
**Oportunístico clássico** (veg.nat, ≥20a) ou **Ambíguo**.

- **Bloco A — Agregação.** Mistura de mecanismos por AMC e município sobre os pixels
  **não-censurados** na **janela primária 2010–2024** (regime moderno, censura baixa,
  Censo 2017 no meio). Índice contínuo `indice_jovem = %≤8a − %≥20a ∈ [−1,1]`
  (+ = lógica jovem). Filtro de confiabilidade: **≥20 px/município, ≥15 px/AMC**
  (mitiga o ruído de munis pequenos apontado na crítica do #28). → 88 munis e 82 AMCs
  confiáveis.
- **Bloco B — Espacializar.** Coroplético AMC (malha EPSG:5880 do #32–#39): índice
  contínuo + mecanismo dominante categórico; scatter de pixels por mecanismo (textura
  fina, contorna o filtro de N); gradiente latitudinal (índice e no-till × latitude do
  centroide).
- **Bloco C — Cruzar com plantio direto.** `pct_pd_area = área plantio direto / área dos
  estabelecimentos` (Censo 2017). Pearson + **Spearman** (robusto) da mistura municipal
  contra no-till e outras variáveis **estruturais** do Censo; robustez em **3 janelas**.
  **Verificação crítica (Bloco C2)**: parcial controlando **latitude** (o cruzamento é
  informação própria ou só o gradiente Sul→Norte?) + comparação **justa** com fluxo
  (SICOR/VA agro) no **mesmo recorte transversal** municipal.
- **Bloco D — Tipologia.** Regra (mecanismo líder → "carreira da terra") + **k-means
  (k=4)** sobre features padronizadas como robustez à regra.

## Achados

> ⚠️ **Correção de enquadramento (verificação 2026-06-07).** A primeira leitura deste
> pipeline anunciou "a lógica é estrutural (no-till), não de fluxo". A verificação
> (parcial controlando latitude + comparação justa com fluxo) **não sustenta** esse
> enquadramento: quase tudo é o gradiente Sul→Norte compartilhado. O achado **robusto**
> é a **segregação espacial** das duas lógicas; o cruzamento com no-till é **co-localização
> no gradiente**, não efeito próprio. As seções abaixo já refletem a leitura corrigida.

### 1. O achado ROBUSTO — a geografia da bimodalidade (segregação espacial)

A contribuição sólida do #40 é **espacializar** a bimodalidade do #28: cada AMC/município
recebe sua mistura de mecanismos. O resultado é uma **segregação espacial limpa** —
**Rotação (jovem ≤8a, laranja) domina Sul/Centro; Oportunístico (antigo ≥20a, verde)
concentra-se no Norte** (mapa AMC). É o gradiente de mesorregião do #28 (Sul 9a → Norte
20a) em resolução fina, e alinha-se ao eixo Sul→Norte de #32/#39:

- índice jovem↔antigo × latitude: **r = −0,49** (p<0,001, n=82)
- as duas lógicas são a face *mecanismo-de-conversão* do gradiente de **aptidão + capital**:
  o Sul capitalizado **gira** pasto jovem na rotação (pasto = fase); o Norte de fronteira
  **ativa** pasto antigo (pasto = reserva de terra).

### 2. O cruzamento com plantio direto — co-localização, NÃO efeito próprio

Na bivariada, no-till parece explicar a idade (no-till % área × idade mediana **r=−0,37**,
p<0,001; × índice jovem +0,33; × % oportunístico −0,34). **Mas o no-till também desce ao
Sul** (no-till × latitude r=−0,38) — exatamente como a lógica jovem. Controlando a
latitude (correlação **parcial**), o cruzamento **colapsa**:

| no-till (% área) × | r bruto | r parcial \| lat | **r parcial \| lat+lon** | leitura |
|---|---|---|---|---|
| **idade mediana** | −0,37 | −0,22 (p=0,048) | **−0,15 (p=0,19)** | sobrevive lat no fio; **some em 2D** |
| % oportunístico | −0,34 | −0,20 (p=0,072) | −0,12 (p=0,28) | some |
| índice jovem↔antigo | +0,33 | +0,18 (p=0,104) | +0,11 (p=0,34) | some |
| % rotação | +0,27 | +0,06 (p=0,561) | +0,07 (p=0,53) | **evapora** |

A associação era o **gradiente espacial compartilhado**. Controlando só a latitude resta
um resíduo no fio (idade, −0,22); controlando o **gradiente 2D completo (lat+lon**,
Sudoeste→Nordeste — o núcleo agrícola é sul **e** oeste), **nenhum par sobrevive** (idade
−0,15, NS). **Não há efeito próprio do no-till** sobre a idade-na-conversão além da
aptidão/capital que ele mesmo marca.

### 3. "Estrutura bate fluxo" NÃO se sustenta (comparação justa)

O enquadramento original contrastava o cruzamento (transversal) com o **nulo do #28**
(Δ SICOR/Δ VA agro × idade ≈ 0). **A comparação era injusta**: o nulo do #28 era em
**painel (município, ano)** — que lava o gradiente cross-section —, não transversal. Posto
o **fluxo no mesmo recorte transversal** municipal (× idade mediana, mesma janela):

| Fluxo (mesmo recorte) | r bruto | p | r parcial \| lat | p |
|---|---|---|---|---|
| VA agro (nível médio) | −0,22 | 0,041 | −0,05 | 0,65 |
| SICOR (Δ médio) | +0,27 | 0,010 | **+0,28** | **0,010** |
| SICOR (nível médio) | −0,10 | 0,34 | +0,04 | 0,71 |
| VA agro (Δ médio) | −0,21 | 0,056 | −0,11 | 0,31 |

O fluxo **não é nulo** neste recorte: VA agro (nível) iguala o no-till bruto, e **Δ SICOR
ainda sobrevive ao controle de latitude (parcial +0,28, p=0,010) — mais forte que o resíduo
do no-till**. Logo a dicotomia "estrutura > fluxo" **cai**. A leitura honesta: idade,
no-till, VA agro e SICOR **co-variam no mesmo gradiente**; nenhuma variável transversal
isola um mecanismo causal.

### 4. Tipologia "carreira da terra" (88 municípios confiáveis, 2010–24)

| Tipo | n munis | idade med | no-till med | Leitura |
|---|---|---|---|---|
| **Giro de lavoura (ILP/rotação)** | 45 | 7a | 13,5% | pasto é fase do sistema de lavoura |
| **Misto / transição** | 26 | 12a | 13,1% | sem mecanismo líder claro |
| **Reserva ativada (oportunístico)** | 16 | 18a | 5,9% | pasto antigo convertido tardiamente |
| **Trampolim de fronteira** | 1 | 8a | 25,2% | premeditado curto raramente *domina* |

O **"Trampolim de fronteira"** (premeditado curto, veg.nat→pasto→agric em ≤8a) quase
nunca vence o *argmax* — coerente com o #28 §4, que o mediu em ~4–5% estável. As duas
lógicas que **estruturam a geografia** são **Rotação (jovem)** × **Oportunístico
(antigo)**; o premeditado é uma terceira via fina.

**k-means (k=4) recupera os mesmos polos** (com a ressalva de circularidade logo abaixo):

| cluster | %rotação | %oportun. | idade med | **no-till** | n munis | Leitura |
|---|---|---|---|---|---|---|
| 3 | 0,63 | 0,08 | **6,4a** | **39,5%** | 16 | **ILP intensivo** (polo claro de giro) |
| 0 | 0,54 | 0,15 | 8,0a | 5,8% | 23 | rotação de sequeiro (jovem, pouco no-till) |
| 1 | 0,28 | 0,24 | 11,4a | 17,0% | 25 | misto/transição |
| 2 | 0,24 | **0,43** | **18,4a** | 5,6% | 21 | **reserva ativada** (polo antigo) |

Os dois polos emergem do k-means: cluster 3 (rotação + jovem + no-till 40%) vs. cluster 2
(oportunístico + antigo + no-till 6%). **Ressalva de circularidade**: o no-till **entra
como feature** do k-means, então o "no-till 40%" do cluster 3 é em parte por construção;
e como tudo gradeia ao Sul, os clusters **re-expressam o gradiente** mais do que validam
um efeito do no-till. O cluster 0 ainda é instrutivo — rotação jovem **sem** no-till alto
(rotação de sequeiro): nem toda lógica jovem é ILP capitalizada.

## Conexão com a narrativa

- **Fecha o fio #2** do backlog ("as duas lógicas da pastagem") — entregando a **geografia
  da bimodalidade**, não um driver estrutural.
- **Refina o #28 espacialmente**: leva o gradiente de idade da mesorregião (Sul 9a → Norte
  20a) à resolução AMC/municipal e o nomeia (giro de lavoura × reserva ativada). **Corrige**
  a tentação de dizer que a idade "vira legível pela estrutura" — a verificação mostra que
  estrutura (no-till) e fluxo (VA agro/SICOR) co-variam igualmente no gradiente; a idade
  segue sem um preditor transversal próprio (consistente com o #28 §7: o mecanismo opera
  abaixo da escala municipal/transversal).
- **Encaixa no #39/#32/#38**: as duas lógicas são o gradiente **Sul→Norte de aptidão**
  visto pela lente da idade-na-conversão — o Sul gira pasto jovem (a face *mecanismo* da
  intensificação que o #39 viu o Sul adotar ao bater no teto de oferta), o Norte ativa
  pasto antigo. É **descrição coerente do gradiente**, não uma quarta peça causal nova.

## Limitações honestas

1. **Gradiente espacial domina** — o cruzamento é transversal e quase tudo é o gradiente
   Sudoeste→Nordeste de aptidão. Controlando só latitude, no-till × idade ainda fica no fio
   (parcial −0,22, p=0,048); controlando o **gradiente 2D (lat+lon)**, **nenhum par
   sobrevive** (idade −0,15, NS). **Não** se estabelece efeito próprio do no-till.
2. **"Estrutura bate fluxo" refutado** — em recorte transversal comparável, fluxo (VA agro,
   Δ SICOR) correlaciona com a idade tanto quanto/mais que o no-till. O contraste com o nulo
   do #28 era injusto (lá era painel (muni,ano)).
3. **Correlação ecológica** — agregados municipais, não fazenda; Censo 2017 é *snapshot*.
   Mecanismo (rotação vs reserva) é **inferido** por idade+origem; sem CAR/intenção do
   produtor (herança do #28).
4. **Circularidade no k-means** — no-till é feature; clusters re-expressam o gradiente.
5. **Amostra/cobertura** — amostra estratificada do #28 (ruído de classificação pode gerar
   idades curtas artificiais); só 88/246 munis passam o filtro de N; mapa de tipologia pinta
   AMC pelo tipo de maior peso (sem geometria municipal no projeto).

## Decisão metodológica (D14)

**Em cruzamentos transversais de LULC em Goiás, sempre reportar a correlação PARCIAL
controlando o gradiente espacial (latitude e longitude — o eixo de aptidão
Sudoeste→Nordeste) antes de atribuir efeito próprio a qualquer covariável — e comparar
régua com régua (transversal × transversal, painel × painel).** Justificativa empírica
(aprendida aqui): no-till, VA agro e SICOR **co-variam com a idade da pastagem apenas
porque todos gradeiam ao Sudoeste**; a bivariada no-till × idade (r=−0,37) cai a −0,22 ao
controlar latitude e a −0,15 (NS) ao controlar lat+lon, e o "nulo de fluxo" do #28 não vale
como contraste porque era painel (muni,ano), não transversal. Regra reusável: **o gradiente
de aptidão é um confundidor de primeira ordem em todo cross-section estadual** (ecoa #38,
onde γ_t absorvia o choque comum e a identificação vinha da interação, não do nível).

## Como rodar

```bash
python scripts/duas_logicas_pastagem.py
# lê pastagem_idade_conversao.csv (#28) + painel_unificado.parquet (#27/Censo) +
# amc_crosswalk_goias.csv + amc_goias.gpkg; escreve 3 CSVs + 4 PNGs.
```
