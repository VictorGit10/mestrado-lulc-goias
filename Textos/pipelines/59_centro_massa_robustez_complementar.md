# Pipeline #59 — A bateria que faltava ao centro de massa

**Script**: `scripts/centro_massa_robustez_complementar.py`
**Quando foi feito**: 2026-09-28. Nasceu da revisão da família inteira do centro de massa para
levá-la à dissertação: listados os testes feitos (#32, #43, #35, #44, D19, #55, #58), ficaram
cinco perguntas sem resposta.
**Depende de**: #32 (centro médio, centroides, séries oficiais), #43 (validação do bloco E), #16
(painel municipal), #25 (painel AMC), #28 (cubos de pixel das Coleções 9, 10.1 e 11).
**Outputs**:
- `data/processed/centro_massa_robustez_complementar.csv`: teste × variável × régua × janela, com
  o ΔNorte e as colunas próprias de cada teste (r², km por década, parcelas por cultura).
- `data/processed/centro_massa_colecoes_pixel.csv`: cache do bloco E (coleção × grupo × ano: Σ área,
  posição média em EPSG:5880, nº de pixels).
- `data/processed/centro_massa_regua_series.csv`: posição norte anual de cada régua agrícola.
- `outputs/centro_massa/robustez_complementar.png`.

---

## Pergunta de pesquisa

| Bloco | Pergunta | Por que ainda estava aberta |
|---|---|---|
| A | O resultado depende da projeção? | O EPSG:5880 é métrico de compromisso, não de área-igual. O #43 roda em graus e bate, mas nunca se trocou a projeção mantendo a malha |
| B | Depende dos anos das pontas? | O ΔNorte compara dois anos isolados |
| C | Que lavoura é essa? | A lavoura do MapBiomas perde área para o Mosaico no fim da série (D25/D26), e a união lavoura + Mosaico vai ao **sul** (−60 km). A âncora era só a soja da PAM |
| D | E a malha do rebanho? | O #43 testou a malha só para as classes com raster. O rebanho é tabular |
| E | É artefato de uma classificação? | O IC do bootstrap mede a composição das AMCs, não o erro do MapBiomas |

## Abordagem

**A. Projeção.** Mesmos pesos do #32, centroides das AMCs em três réguas: EPSG:5880 (a do #32),
Albers de área-igual para a América do Sul (ESRI:102033) e média esférica (cada centroide vira
um vetor unitário 3D, a média ponderada é reconvertida em latitude, km = arco × 6.371).

**B. Anos-extremo.** ΔNorte com 1, 3 e 5 anos em cada ponta, e a inclinação da reta de mínimos
quadrados da posição norte contra o ano, × 39. O r² é descritivo: a série é autocorrelacionada.

**C. Réguas agrícolas.** Centro de massa pela agricultura MapBiomas, pela união com o Mosaico e
por três réguas da PAM (IBGE) agregadas às AMCs: soja plantada, temporárias sem milho (24
culturas) e temporárias com o milho total. O milho de 2ª safra repete área já contada na soja:
declarado, não corrigido. Para explicar a divergência, as temporárias são decompostas **por
cultura** com a mesma identidade do #58 (troca de composição entre culturas + deslocamento de
cada cultura).

**D. Malha municipal.** As quatro camadas do #32 pelos 246 municípios da malha atual, sem AMC.
Antes das emancipações o município-filho não tem dado e a massa fica no pai: é o artefato que a
AMC evita, e por isso o teste informa.

**E. Coleções.** Os cubos de pixel do #28 (EPSG:4326, 30 m), recortados por rasterização das
AMCs. Por classe e ano, cada pixel pesa pela sua área (cos da latitude) e fica na posição do
centro de uma célula de 16 × 16 pixels (~480 m), projetada em EPSG:5880. Classes do painel:
pastagem [15]; agricultura [20, 39, 40, 41, 46, 47, 48, 62]; vegetação natural [3, 4, 12];
Mosaico [21]; silvicultura [9] à parte, porque o #43 a soma na agricultura. Comparação em
1985–2023, o último ano presente nas três coleções.

## Validações

| Conferência | Resultado |
|---|---|
| Séries de partida × `centro_massa_anual.csv` (4 camadas × 40 anos) | \|Δ\| < 1 mm |
| Decomposição por cultura: soma das parcelas × ΔNorte direto | fecha em 10⁻⁶ km, em todas as janelas |
| Bloco E, Coleção 10.1 com a agricultura do #43 × `centro_massa_pixel_anual.csv`, ΔNorte 1985–2024 na régua EPSG:5880 | pastagem +78,9 × +78,8; agricultura (com silvicultura) +66,5 × +65,8; vegetação natural +6,6 × +6,5. Diferença de nível em qualquer ano ≤ 0,93 km |

## Achados

### A. Projeção: diferença de até 2 km

| ΔNorte 1985 → 2024 (km) | EPSG:5880 | Albers | Esfera |
|---|---|---|---|
| Pastagem | +77,6 | +79,7 | +78,2 |
| Rebanho | +66,9 | +68,4 | +67,5 |
| Agricultura | +65,2 | +65,7 | +66,3 |
| Vegetação natural | +7,6 | +7,5 | +7,7 |

A projeção de compromisso não fabrica o resultado. A maior diferença é de 2,1 km (pastagem, Albers).

### B. Anos-extremo: a série é quase uma reta

| ΔNorte (km) | 1 ano | média de 3 | média de 5 | reta, 40 anos | r² | km por década |
|---|---|---|---|---|---|---|
| Pastagem | +77,6 | +72,0 | +65,8 | +71,1 | 0,98 | +18,2 |
| Rebanho | +66,9 | +61,4 | +58,1 | +62,8 | 0,97 | +16,1 |
| Agricultura | +65,2 | +64,1 | +61,2 | +66,8 | 0,98 | +17,1 |
| Vegetação natural | +7,6 | +6,3 | +5,1 | +2,9 | 0,09 | +0,7 |

As médias das pontas encolhem o número porque encurtam o intervalo (com 5 anos por ponta, os
centros estão em 1987 e 2022, 35 anos de distância e não 39), e não porque os anos-extremo sejam
atípicos. A reta, que usa os 40 anos, fica entre 63 e 71 km nas três camadas, com r² de 0,97–0,98.
A vegetação natural não tem tendência (r² 0,09), o que é coerente com "ancorada".

### C. Que lavoura? O resultado se divide

| Régua | Período | ΔNorte | Ato I | Ato II | Ato III |
|---|---|---|---|---|---|
| MapBiomas agricultura | 1985–2024 | **+65,2** | +29,6 | +34,2 | +0,2 |
| MapBiomas agricultura ∪ Mosaico | 1985–2024 | **−60,5** | −58,4 | −5,2 | +4,1 |
| PAM soja plantada | 1988–2024 | **+48,3** | — | +51,9 | +8,2 |
| PAM temporárias sem milho | 1988–2024 | **−46,0** | — | +27,7 | +7,3 |
| PAM temporárias com milho total | 1988–2024 | **−45,5** | — | +12,7 | +6,6 |

A lavoura comercial (as classes de lavoura do MapBiomas e a soja da PAM, fonte independente do
satélite) tem o centro de gravidade ao norte. O conjunto das lavouras temporárias e a união com o
Mosaico o têm ao **sul**. No Ato II as quatro réguas sem o Mosaico vão ao norte (a união fica
em −5,2 km), e no Ato III as cinco vão ao norte.

A decomposição por cultura explica a divisão (temporárias sem milho, parcelas em km):

| Janela | ΔNorte | troca de composição | deslocamento de cada cultura | maiores parcelas |
|---|---|---|---|---|
| 1988–2024 | −46,0 | −80,5 | +34,6 | arroz −37,0; soja +14,7; cana −12,4; feijão −10,7 |
| 1988–2000 | −81,5 | −55,4 | −26,1 | arroz −39,3; soja −21,9; feijão −11,3 |
| 2001–2024 | +35,7 | −12,3 | +48,0 | soja +44,2; cana −6,2; arroz −5,7 |

Em 1988 o **arroz** tinha 689 mil ha plantados em Goiás, quase a área da soja (748 mil), e o
centro dele ficava 77 km ao norte do centro das temporárias. Em 2024 tinha 28 mil ha. O feijão
fez o mesmo em escala menor. A cana, ao sul do centro, cresceu de 104 mil para 1,03 milhão de ha.
**O deslocamento ao sul das temporárias é, quase inteiro, o desaparecimento do arroz do norte
entre 1988 e 2000.** A leitura mais provável é a do arroz de sequeiro plantado na abertura de
áreas, antes do pasto, mas isso é interpretação: os dados mostram o tamanho, a posição e o
desaparecimento, não a razão, e não há fonte lida no projeto sobre isso. A união com o Mosaico
vai ao sul quase toda no Ato I (−58,4 de −60,5 km), o mesmo período. Que o Mosaico do norte de
1985 guardasse essa agricultura não foi testado.

**Consequência para o texto.** "O centro de gravidade da agricultura está 65 km mais ao norte"
vale para a lavoura **comercial**, e a soja da PAM a confirma de fora do satélite (+48 km). Não
vale para "toda a lavoura". A dissertação precisa dizer qual das duas mede. Para a pastagem e o
rebanho essa ambiguidade não existe.

Em 2024, as cinco réguas ficam de 111 a 135 km ao sul do centro da pastagem (linhas
`C_vao_pasto` do CSV). O gradiente lavoura ao sul, pasto ao norte, do #32, não depende da régua.

### D. Malha municipal: diferença de até 1,1 km

| ΔNorte 1985 → 2024 (km) | 166 AMCs | 246 municípios | Ato I, AMC \| municípios |
|---|---|---|---|
| Pastagem | +77,6 | +77,9 | +37,8 \| +37,8 |
| Rebanho | +66,9 | +68,0 | +26,9 \| +27,6 |
| Agricultura | +65,2 | +64,9 | +29,6 \| +29,2 |
| Vegetação natural | +7,6 | +7,5 | +10,8 \| +10,9 |

O rebanho, que nunca tinha sido medido fora da AMC, fica a 1,1 km. Em 1985 só 184 dos 246
municípios informam rebanho, e mesmo assim o artefato das emancipações não chega a 1 km no Ato I.

### E. Coleções MapBiomas: o deslocamento sobrevive às três classificações

| ΔNorte 1985 → 2023 (km), pixel a pixel | Coleção 9 | Coleção 10.1 | Coleção 11 |
|---|---|---|---|
| Pastagem | +76,5 | +75,9 | +69,0 |
| Agricultura | +65,7 | +65,8 | +65,9 |
| Vegetação natural | +5,4 | +6,7 | +5,2 |
| Mosaico de Usos | −67,1 | −73,2 | −43,4 |

A agricultura é praticamente a mesma nas três coleções (diferença de 0,2 km). A pastagem fica
entre +69 e +77 km: a Coleção 11 dá 7 km a menos, dentro do IC95% i.i.d. da D19 ([+54,7; +98,2]).
A vegetação natural fica perto de zero nas três. O Mosaico vai ao sul nas três, com a maior
diferença entre coleções (−43 a −73 km), coerente com a Coleção 11 ter reclassificado cerca de
metade do Mosaico de Goiás (exploratório da Coleção 11, fora da dissertação).

**Leitura:** o deslocamento das camadas-manchete não é artefato de uma classificação. É
condição necessária, não suficiente (ver "O que este pipeline NÃO diz").

Tempo: ~7 min por coleção (16 tiles de 8.192², 40 bandas), lidos em blocos de 256 linhas com os
pixels de Goiás compactados uma vez por bloco. A primeira versão, com blocos de 1.024 linhas,
estourava a RAM livre da máquina e levaria ~4 h.

### F. Centro mediano × centro médio: a direção se mantém, a magnitude não

| ΔNorte 1985 → 2024 (km) | médio | mediano (Weiszfeld) |
|---|---|---|
| Pastagem | +77,6 | +101,1 |
| Rebanho | +66,9 | +81,1 |
| Agricultura | +65,2 | +39,9 |
| Vegetação natural | +7,6 | +11,1 |

Lido de `centro_massa_anual.csv`, sem recalcular: o #32 sempre calculou o mediano, mas nenhuma
ficha registrava o deslocamento dele. A ficha do #32 dizia que os dois "contam a mesma história".
Na **direção**, contam. Na **magnitude**, não: na agricultura o mediano se desloca 40 km e o médio
65 km. O mediano fica dentro do aglomerado do Sudoeste e é menos sensível ao crescimento de massa
distante ao norte, que é justamente o que o médio registra. **Consequência para o texto:** o
número em quilômetros é sempre o do centro médio, e se diz qual centro é.

## O que este pipeline NÃO diz

- **O bloco E não mede acurácia.** As três coleções compartilham satélite, boa parte do método e
  parte das amostras, e podem errar juntas. A concordância é condição necessária, não suficiente.
- **O bloco C não diz por que o arroz sumiu.** Mede tamanho, posição e desaparecimento.
- **O r² do bloco B não é teste.** A série anual é autocorrelacionada.
- **O rebanho continua sem teste pixel a pixel.** O bloco D troca a malha, não elimina a malha.

## Como rodar

```
python scripts/centro_massa_robustez_complementar.py                 # E lido do cache
python scripts/centro_massa_robustez_complementar.py --refazer-pixel # relê os 3 cubos (~20 min)
python scripts/centro_massa_robustez_complementar.py --sem-pixel     # só A–D (segundos)
```

O script aborta se as séries de partida divergirem do #32, se a decomposição por cultura não
fechar ou se a Coleção 10.1 do bloco E não reproduzir o #43 (tolerância de 2 km no ΔNorte).
