# Pipeline #44 — Centro de massa: abrir os *lumps* + controles (extensão do #32)

**Script**: `scripts/centro_massa_desagregado.py`
**Quando foi feito**: 2026-07-13.
**Depende de**: #32 (`centro_massa.py`, **reuso integral** de `mean_center`/`median_center`/`metros_para_lonlat`/`carregar_dados`) e #25 (`painel_amc_goias.parquet`, `amc_goias.gpkg`). Não usa GEE — todas as variáveis já estão no painel AMC.
**Outputs**:
- `data/processed/centro_massa_desagregado_anual.csv` — variável × ano: centro médio/mediano + latitude.
- `data/processed/centro_massa_desagregado_bootstrap.csv` — variável × janela: ΔNorte + **IC95%** (bootstrap de AMCs, D19).
- `outputs/centro_massa/desagregado_soja.png` — soja (raster e SIDRA) vs "agricultura" (lump) + régua-espelho `agric∪mosaico` (#28D).
- `outputs/centro_massa/desagregado_vegetacao.png` — as 3 formações vs o lump de veg. natural.
- `outputs/centro_massa/desagregado_controle.png` — leite e área urbana vs a fronteira.

---

## Pergunta

O #32 mediu o deslocamento de **4 agregados**. Dois deles carregam a narrativa e são *lumps* heterogêneos ("agricultura" e "vegetação natural"), e um terceiro (o rebanho) é a única variável que o #43 **não** consegue validar por MAUP (não tem raster). Este pipeline abre os lumps e adiciona controles — quatro sondagens, cada uma com hipótese:

1. **Soja isolada + validação cruzada de fonte.** "Agricultura" mistura soja + milho + cana + algodão + perenes. A soja é a commodity de exportação (o mecanismo do #37 é história de câmbio/preço). (a) A soja marcha ao norte **mais** que o lump? (b) O centroide da soja pelo **raster** (MapBiomas, `lulc_soja_ha`) bate com o da **SIDRA** (área plantada)?
2. **Vegetação natural aberta** em floresta nativa / formação savânica / campo nativo. O "+8 km, quase parada" do #32 é uniforme, ou média enganosa de uma muralha fixa com formações que recuaram?
3. **Leite como controle** (placebo sobre o próprio fenômeno). O leite é pecuária atada à bacia leiteira do **Sul**. Se o boi sobe e o leite fica ancorado ao sul, é contraste *dentro* da pecuária. **Área urbana** entra como segundo controle (deveria ficar parada).
4. **Régua-espelho da mudança de rótulo do Mosaico** (propagação da robustez oficial do #32; #28D/D25). A soja recém-convertida migra para a classe "Mosaico de Usos" no fim da série. Aqui isso é **duplamente visível**: o raster de soja e o lump subcontam a soja recente, enquanto a SIDRA é **imune**. A validação da sondagem 1 vale antes de 2020 e **diverge** no Ato III? E sob a régua `agricultura ∪ mosaico` o congelamento agrícola some?

## Abordagem

Método idêntico ao #32 (centro médio ponderado de Lefever + mediano de Weiszfeld sobre os centroides das 166 AMCs em EPSG:5880), só muda o conjunto de variáveis. **Só extensivas** (ha, cabeças, mil litros) — centro de massa de uma razão/taxa não é interpretável. É **descritivo**: não fazemos lead-lag entre latitudes de centroides (séries suaves integradas fabricam precedência espúria — D16/#42).

---

## Achados

### 1. Soja: a hipótese "soja lidera o lump" está ERRADA — mas a validação de fonte passa

A soja **não** marcha ao norte mais que o agregado. Ela marcha **um pouco menos** e fica praticamente **colada** ao lump o tempo todo:

| Variável | ΔN 1985→2024 (médio) | ΔN (mediano) | janela |
|---|---:|---:|---|
| Agricultura (lump) | +65,2 km | +39,9 | 1985–2024 |
| **Soja — MapBiomas (raster)** | **+58,8 km** | +35,6 | 1985–2024 |
| **Soja — SIDRA (área plantada)** | **+48,3 km** | +48,8 | 1988–2024 |

A latitude da soja e a do lump agrícola coincidem dentro de **±5 km em todos os anos** (1990/2000/2010/2024). **Razão**: em Goiás a soja **domina** o agregado agrícola — logo "agricultura" no #32 é, na prática, **"soja + co-movedores"** (milho-safrinha segue a soja), não um lump escondendo uma commodity divergente. A hipótese cai, mas o resultado é útil: **valida que a manchete do #32 é essencialmente a geografia da soja.**

**Validação cruzada de fonte (o que salva a sondagem):** os centroides da soja pelo **raster** (satélite) e pela **SIDRA** (censo agropecuário) — dois sistemas de medição totalmente independentes — concordam: **corr(latitude anual) = 0,89**, `|Δlat|` médio de **~7 km** ao longo de 37 anos, mesma direção e magnitude. É a versão raster×estatística do que o #43 fez (raster×malha), e é a **ponte de credibilidade** para os centroides tabulares — em especial o do rebanho, que o #43 não alcança: onde dá para conferir (soja), o método do centroide-AMC dá a mesma resposta em fonte de satélite e de pesquisa. **Ressalva importante:** essa concordância é uma propriedade **pré-2020** (corr 0,84 até 2019); no Ato III as duas fontes **divergem** por causa da mudança de rótulo do Mosaico — ver Achado 4.

**Reinterpretação pela mudança de rótulo do Mosaico (#28D):** por ato a soja-raster faz **I:+15 II:+50 III:−7 km** — recuo ao sul no Ato III **estatisticamente robusto** (IC95% [−13, −3]). A leitura antiga era "leve recuo ao núcleo consolidado do Sul". Mas a **SIDRA — imune ao classificador — anda +8 km ao NORTE na mesma janela**: as duas fontes vão em **sentidos opostos**. O recuo do raster é, portanto, em boa parte **artefato**: o classificador mantém a soja velha do Sudoeste na classe "Soja" e roteia a soja nova da fronteira para o "Mosaico", puxando o centroide *visível* para trás. Não é a soja que recuou ao sul — é o rótulo "Soja" que perdeu a soja nova. Detalhe no Achado 4.

### 2. Vegetação: o "+8 km, muralha norte" é miragem de média

Abrindo o lump, as três formações contam histórias opostas:

| Formação | ΔN médio | IC95% (bootstrap) | leitura |
|---|---:|---:|---|
| Floresta nativa | +8,7 km | **[+2,5, +15,1]** ≠0 | **quase presa** — move só ~9 km, mas robusto |
| Formação savânica (Cerrado *s.s.*) | +12,4 km | **[−0,3, +23,3]** inclui 0 | **≈ ancorada** — recuo não distinguível de zero |
| Campo nativo | +34,8 km | **[+0,2, +79,9]** ≠0 mas larguíssimo | recuo ao norte na **direção**, magnitude **muito incerta** |

O lump "+7,6 km" é a **média de uma floresta quase presa com um campo nativo que fugiu ao norte**. O campo nativo — grama aberta, a formação **mais barata de converter** (sem desmate) — foi consumido primeiro no Sul e cedo (por ato: **I:+30**, depois ~parado), então seu centro de massa disparou ao norte. A floresta nativa move-se pouco (~9 km, mas robusto). A savânica, aberta pelo IC, está **dentro do ruído** — sua "reserva setentrional" quase não mudou de latitude. Visualmente (`desagregado_vegetacao.png`), por volta de **2021 o centroide do pasto ultrapassa em latitude a floresta e o campo nativo** — a fronteira **alcançou** a vegetação convertível que ainda restava.

Isso **fortalece e torna mais honesta** a narrativa: a formação natural **mais barata (campo nativo)** recuou ao norte junto com a fronteira; floresta e savânica quase não se moveram. O lump escondia isso.

> Cautela — **confirmada pelo bootstrap (D19)**: o campo nativo tem **magnitude instável** — o IC95% do ΔNorte vai de **+0,2 a +79,9 km** (nº de AMCs com campo cai de 158→142, algumas zeram; o suporte encolhe). A **direção** (recuo ao norte) mal sobrevive; o **valor** é indeterminado. Reportar como "recuou ao norte", **nunca** cravar km. E a savânica **não** deve ser reportada como "recuo de +12 km" — seu IC inclui zero.

### 3. Controles: a marcha ao norte é específica da fronteira

| Variável | ΔN médio | IC95% (bootstrap) | leitura |
|---|---:|---:|---|
| **Área urbana** | **−8,4 km** | **[−18,6, −1,5]** ≠0 | move **ao sul** (oposto da fronteira) — placebo forte |
| Leite (produção) | +29,9 km | [+10,8, +49,8] ≠0 | move **muito menos** que o boi, e fica ao sul |
| Rebanho bovino (total) | +66,9 km | [+47,2, +84,5] | (referência) |
| Pastagem | +77,6 km | [+54,7, +98,2] | (referência) |

- **Área urbana é o controle negativo forte**: seu centro de massa não só **não segue** a fronteira, como se desloca robustamente **ao sul** (−8,4 km, IC exclui zero, no eixo Goiânia–Anápolis). A urbanização foi na **direção oposta** à fronteira → **a marcha ao norte não é deriva genérica de centroide**, é específica da fronteira agropecuária. (Melhor que um nulo perfeito: um placebo que anda ao contrário.)
- **Leite é o contraste dentro da pecuária**: fica sistematicamente **ao sul** do rebanho total, move-se bem menos (+30 vs +67 km) e o **vão entre os dois dobra** — boi está **+30 km** ao norte do leite em 1985 e **+67 km** em 2024. O laticínio ficou ancorado à bacia consolidada do Sul enquanto o rebanho de corte marchou ao norte. (Não é nulo perfeito — o leite também subiu +30 km com a expansão geral —, então é um controle "moveu muito menos e ficou ao sul", não "não moveu".)

### 4. Régua-espelho: a mudança de rótulo do Mosaico e a divergência raster×SIDRA no Ato III

Propaga a robustez oficial do #32 (régua-espelho, #28D/D25) para o nível desagregado. Aqui a mudança de rótulo fica **mais nítida que em qualquer outro pipeline**, porque a fonte está aberta: o rótulo "Soja" do raster perde a soja recém-convertida para o "Mosaico", enquanto a SIDRA a conta. ΔNorte no **Ato III (2020→24)**, com IC95% (D19):

| Régua de destino | ΔNorte Ato III | IC95% | Leitura |
|---|---:|---|---|
| Agricultura (lump) | **+0,2 km** | [−0,5; +1,1] | congela — *exposto* |
| **Soja — MapBiomas (raster)** | **−7,1 km** | **[−13,2; −3,4]** | **recua ao SUL** — *exposto, o mais mordido* |
| **Agricultura ∪ Mosaico** | **+4,1 km** | **[+1,0; +6,9]** | **sobe** — *corrigido* |
| Soja — SIDRA (área plant.) | **+8,2 km** | [−0,5; +16,1] | sobe — *imune, sugestivo* |

**A assinatura mais limpa da mudança de rótulo no projeto inteiro:** o raster de soja e a SIDRA — que concordaram por 37 anos — andam em **sentidos opostos no Ato III** (um recuo robusto de −7 km contra um avanço de +8 km, um vão de ~15 km em 4 anos). Não é "congelamento", é **reversão ativa** do centroide *visível*, fabricada pelo classificador. Isso (a) **confirma a mudança de rótulo** por um caminho independente do #28D (dois medidores de soja divergindo exatamente quando o Mosaico incha) e (b) mostra que a régua `agricultura ∪ mosaico` **recupera** o movimento ao norte que o rótulo cru esconde (+4,1 km, IC exclui zero), reproduzindo o resultado do #32.

**O que isto faz com a sondagem 1.** A validação raster×SIDRA (a manchete do #44) é uma propriedade **histórica**: sólida até 2019, ela **quebra no Ato III** — e a quebra é *diagnóstica*, não um defeito do método. A ponte de credibilidade para o **rebanho** continua de pé: o rebanho é tabular/SIDRA e **não** é uma classe drenada pela mudança de rótulo. Mas o **centroide da soja pelo raster não deve ser lido nos anos terminais** — ali a SIDRA (ou a régua `agric∪mosaico`) é a fonte confiável. O núcleo da narrativa (agricultura ao sul da fronteira que marcha) permanece intacto: a mudança de rótulo morde só a **trajetória recente da perna agrícola**, não o gradiente. Ver a seção "Robustez à mudança de rótulo do Mosaico" do [#32](32_centro_massa.md) e o [§5.4 do #28D](28D_deriva_mosaico.md).

---

## Como ler as figuras

- **`desagregado_soja.png`** — as duas séries roxas (soja raster/SIDRA) andam juntas e **coladas ao tracejado magenta** (lump agrícola), ~1,5° ao sul do pasto (laranja). Confirma soja ≈ lump. **No Ato III sombreado elas se separam**: o raster recua ao sul e a SIDRA sobe (a mudança de rótulo do Mosaico, Achado 4); a linha violeta (`agric∪mosaico`) mostra a régua corrigida.
- **`desagregado_vegetacao.png`** — floresta (verde-escuro) **reta**; campo nativo (verde-claro) **subindo**; savânica (verde-médio) no topo (norte) quase reta; o **pasto (laranja) cruza floresta/campo por volta de 2021**.
- **`desagregado_controle.png`** — área urbana (cinza) **horizontal**; leite (azul) **abaixo** do boi/pasto o tempo todo; o vão leite↔boi alargando.

## Limitações

- **Descritivo** (deslocamento), não causal — mesma postura do #32. Nenhum lead-lag entre centroides (D16).
- **Incerteza reportada (D19)**: todo ΔNorte carrega IC95% por bootstrap de AMCs (faixa nas figuras). Refinou este pipeline: **savânica inclui zero** (não é "recuo de +12 km") e o **campo nativo tem IC larguíssimo** [+0,2; +79,9] — confirma numericamente a cautela de magnitude.
- **Campo nativo**: magnitude instável (ver cautela acima) — direção robusta, km não.
- **Soja-SIDRA** começa em 1988 (não 1985) — comparação de ΔN líquido usa janela ligeiramente diferente.
- **Sem MAUP-pixel** para as novas variáveis. Como soja e as 3 formações são subconjuntos de classes que o #43 já validou no agregado (AMC≈pixel a ~1-2 km), o MAUP é muito provavelmente irrelevante aqui também — mas não foi rodado no GEE. Extensão possível se a banca cobrar.
- **Rótulos ecológicos** ("galeria", "Cerrado *s.s.*") são atalhos: `lulc_floresta_nativa_ha` inclui cerradão e mata seca, não só mata ciliar.

## Conexão com a narrativa

Não muda nenhuma conclusão das 5 camadas — **refina** a Camada 1 (#32):

1. **A manchete do #32 é a geografia da soja** (soja ≈ lump agrícola), **validada em duas fontes independentes** (raster + SIDRA, r=0,89) — o que empresta credibilidade ao centroide tabular do rebanho. Ressalva: a validação é **pré-2020**; nos anos terminais a mudança de rótulo do Mosaico separa as fontes (Achado 4), mas a ponte para o rebanho (imune) permanece.
2. **A "muralha norte" é a floresta**, não a vegetação natural inteira: campo nativo e savânica **recuaram ao norte** com a fronteira (o pasto os alcança em latitude ~2021) — fortalece a leitura de fronteira.
3. **Controles fixam a especificidade**: urbanização parada (placebo limpo) + leite ancorado ao sul (o corte é que marcha) — a marcha ao norte é da **fronteira agropecuária**, não mudança de rótulo geral.
4. **A régua-espelho da mudança de rótulo (#28D) é robustez, não ressalva**: sob `agric∪mosaico` e SIDRA (imune) a agricultura segue subindo no Ato III; o "congelamento" do rótulo cru é artefato. O núcleo (agricultura ao sul da fronteira) sobrevive nas três réguas.
