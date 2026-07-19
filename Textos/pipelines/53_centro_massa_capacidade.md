# Pipeline #53 — Centro de massa da capacidade instalada de armazenagem (CONAB)

**Script**: `scripts/centro_massa_capacidade.py`
**Quando foi feito**: 2026-07-18.
**Depende de**: #32 (`centro_massa.py`, **reuso integral** de `mean_center`/`median_center`/`metros_para_lonlat`), #50 (centroides econômicos de referência), #25 (`amc_crosswalk_goias.csv`, `amc_goias.gpkg`). Não usa GEE.
**Outputs**:
- `data/raw/conab/ArmazensCadastrados.txt` — cadastro nacional de armazéns (cache).
- `data/raw/conab/exportacao_capacidade_estatica.xls` — série histórica UF (cache).
- `data/processed/centro_massa_capacidade.csv` — centroide da capacidade (ponto + AMC) + faixa de estabilidade.
- `data/processed/centro_massa_capacidade_vaos.csv` — vão de latitude vs cada referência.
- `data/processed/centro_massa_capacidade_uf_serie.csv` — série de capacidade de GO 2005+ (UF).
- `outputs/centro_massa/capacidade_vs_fronteira.png` — latitude: capacidade vs séries #32/#50.
- `outputs/centro_massa/capacidade_mapa.png` — mapa: armazéns + centroides de referência.

---

## Pergunta

O **#45** (Trase × LULC) fechou o Eixo A com um veredito claro — a cadeia **exportadora acompanha** a produção, **não a lidera** — mas deixou uma ressalva honesta e registrada: o Trase mede **fluxo exportador**, não **capacidade instalada**. Silos e frigoríficos poderiam estar na **dianteira** da fronteira onde o fluxo não está. O **#50** pôs crédito e valor na régua de latitude do #32 e achou que o dinheiro **consolida o núcleo** (crédito ~75 km ao sul do pasto), não persegue a fronteira. Faltava a mesma pergunta para a **capacidade física de armazenagem**:

> O centro de massa da capacidade estática de armazenagem de Goiás está na **dianteira** da fronteira (norte, junto do pasto/rebanho) ou **consolida** o núcleo produtivo (sul, junto do crédito e da lavoura)?

Se a capacidade se senta no núcleo, a metade "silos" da ressalva do #45 fecha de forma **descritiva e honesta**: *nem a capacidade instalada está na dianteira*.

## Por que um centroide, e não um teste de liderança temporal

A fonte fetchável da CONAB **não permite** testar precedência no tempo — e é importante dizer por quê, porque foi o que reduziu a frente ao seu núcleo viável:

| Arquivo CONAB | O que traz | Município? | Tempo? |
|---|---|---|---|
| `ArmazensCadastrados.txt` (8,2 MB) | Cadastro **atual** de armazéns: `cod_ibge` + capacidade estática/expedição/recepção + lat/lon | **Sim** | **Não** (snapshot, sem coluna de data) |
| `exportacao_capacidade_estatica.xls` (55 KB) | Série histórica **2005+**, colunas `Ano · UF · Quantidade` | **Não** (só UF) | Sim, mas estadual |

A versão **municipal** não tem tempo; a versão **temporal** não tem município. O desenho cross-lagged municipal × ano que o #45 usou exigiria as duas dimensões juntas, e a **única** fonte que as entrega — reconstrução do CNPJ por `data_abertura` (itens 6/7 do backlog) — é "engenharia de dado pesada", **já descartada em 2026-05-15**, e cairia na armadilha **D16/#42** (Granger espúrio em série integrada suave). Logo, a frente foi **convertida** de "teste de precedência (inviável)" para "confirmação espacial descritiva (viável, barata)" — um centroide, no espírito do #50.

> **Correção de um registro do backlog.** A ficha de fontes dizia que o SISDEP tinha "série histórica de capacidade estática **por município**". A inspeção mostrou que a série histórica é **por UF** (2005–2026), e a granularidade municipal existe só no **cadastro atual** (sem data). O registro foi corrigido.

## Abordagem

Reusa a máquina do #32/#50 (mean center de Lefever 1926 + median center de Weiszfeld 1937, EPSG:5880). Como o cadastro traz **coordenadas de ponto** — o que o LULC e o econômico **não** têm —, o centroide é calculado de **duas** formas:

- **(A) Ponto** — pesa cada armazém pela capacidade estática na sua **própria lat/lon**. É a versão mais fiel; a vantagem única deste dado.
- **(B) AMC** — agrega a capacidade por AMC (`cod_ibge → code_amc`, crosswalk Ehrl 2017) e pesa os centroides das 166 AMCs. É o método **idêntico** ao #32/#50 → comparação de latitude **maçã-com-maçã** com pasto/agricultura/crédito.

As duas quase coincidem (validação cruzada da agregação). **Estabilidade** (não incerteza amostral — ver Limitações): bootstrap dos **armazéns** (reamostra as instalações com reposição, B=2000) → **faixa de estabilidade de 95%** da latitude do centroide-ponto à composição do cadastro.

**Cautelas** (herdadas do #50/#32): descritivo (sem lead-lag entre latitudes, D16); a capacidade é a **atual** (snapshot), comparada contra a posição **recente** de cada referência do #32/#50; variável extensiva (t de capacidade); cadastro = armazéns **registrados** na CONAB (padrão nacional de capacidade estática; armazenagem intra-fazenda não cadastrada pode ficar de fora).

---

## Achado — a capacidade de armazenagem é a camada **mais ao sul de todas**

Goiás tem **1.135 armazéns** cadastrados com **18,54 Mt** de capacidade estática. O centroide dessa capacidade senta-se em **lat −17,24°** — e as duas formas de calcular **coincidem** (ponto −17,240° vs AMC −17,238°; Δ = 0,3 km), validando a agregação por AMC.

Comparado com a posição **recente** de cada referência (vão = capacidade − referência; negativo = capacidade **ao sul**):

| Referência (último ano) | Latitude | Vão vs capacidade | Leitura |
|---|---:|---:|---|
| Pastagem (2024) | −15,87° | **−151,7 km** | capacidade **muito ao sul** da fronteira de pasto |
| Rebanho bovino (2024) | −15,91° | **−146,9 km** | idem, do rebanho |
| **Crédito total — SICOR (2024)** | −16,49° | **−83,0 km** | capacidade **ainda mais ao sul que o crédito** |
| VA agropecuário (2021) | −16,86° | −42,1 km | ao sul do valor |
| **Agricultura — área (2024)** | −17,09° | **−16,4 km** | praticamente **em cima do núcleo de lavoura** |

A leitura é limpa e forte: a capacidade instalada é a **mais core-anchored** de todas as camadas já medidas. Ela senta-se **~150 km ao sul** da fronteira de pasto/rebanho, **~83 km ao sul até do crédito** (que o #50 já achara consolidador), e praticamente **coincide com o centroide da agricultura** (só −16 km, um pouco mais ao sul ainda). O centro **mediano** (robusto) é ainda mais austral (−17,48°), reforçando: a massa de capacidade mora no **sudoeste**, o cinturão de grãos (Rio Verde / Jataí / Cristalina) — exatamente onde a soja/milho se instalou, longe da ponta da fronteira. A faixa de estabilidade de 95% do centroide (bootstrap de composição dos armazéns) é apertada — **[−17,32°, −17,15°]** — e fica **inteiramente ao sul** de tudo exceto a agricultura.

**Fecha a metade "silos" da ressalva do #45**: a capacidade física de armazenagem **não está na dianteira e não lidera** a fronteira — ela consolida o núcleo, **mais fundo até que o crédito**. É o terceiro objeto (depois do crédito no #50 e do fluxo exportador no #45) a mostrar que a infraestrutura da cadeia **acompanha/consolida**, não puxa.

### Contexto temporal (série UF, **não** espacial)

A série histórica da CONAB mostra a capacidade de GO crescendo **+66%** — de **11,2 Mt (2005)** para **18,5 Mt (2026)**. Mas é **estadual**: diz *quanto*, não *onde* — não se pode espacializar o crescimento nem testar se a capacidade nova foi para a fronteira. Fica como contexto (a capacidade acompanhou o boom de produção), não como evidência espacial.

---

## Por que a leitura é sensata (e o que ela **não** fecha)

A capacidade da CONAB é predominantemente **armazenagem de grãos** (silos/graneleiros de soja e milho) — por isso rastreia o **núcleo de lavoura** (sudoeste), não o rebanho. Isso fecha a metade **"silos"** da ressalva do #45 de forma direta. A metade **"frigoríficos"** (abate bovino) **continua aberta**: exigiria o registro **SIF/MAPA** (SIGSIF) ou a geolocalização de frigoríficos do Trase — o **SIGSIF foi descartado** (item 7 das coletas pendentes, acesso via LAI incerto) e o abate modelado do rebanho é circular (ver #50). Então o #53 diz: *a capacidade de armazenagem de grãos não lidera*; **não** diz nada sobre a geografia do abate — que segue sendo um negativo metodológico honesto herdado do #50.

## Conexão com a narrativa

**Não muda nenhuma conclusão** — fecha uma ressalva registrada e adiciona um ponto à leitura espacial-econômica da Camada 1 / Perna 3:

- **Perna 3 (não é deslocamento causal)**: o #45 mostrou que o fluxo exportador acompanha, não lidera. O #53 estende: **nem a capacidade instalada** de armazenagem lidera — ela é a camada mais ancorada ao núcleo de todas. Reforça "co-evolução sem líder" pelo lado da infraestrutura física.
- **Família do centro de massa (#32/#44/#50)**: mais um centroide, e o mais austral já medido. Onde o crédito consolida a massa (~75 km ao sul do pasto, #50), a **capacidade física consolida ainda mais fundo** (~150 km ao sul, colada à lavoura).

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| Eixo A | #45 | A cadeia exportadora lidera a expansão? | Não — acompanha (co-move contemporâneo, sem precedência). |
| 1 / econ. | #50 | O crédito segue a fronteira ou consolida o núcleo? | Consolida (~75 km ao sul do pasto). |
| **1 / econ.** | **#53** | **E a capacidade física de armazenagem?** | **Consolida mais fundo ainda (~150 km ao sul do pasto, ~83 km ao sul do crédito, colada à lavoura). Fecha a metade "silos" da ressalva do #45.** |

## Limitações

- **Descritivo** (posição), não causal — sem lead-lag entre latitudes (D16). É **snapshot**, comparado contra posições recentes.
- **Só armazenagem de grãos**: fecha a metade "silos" da ressalva do #45; a metade "frigoríficos/abate" continua sem dado acessível (SIGSIF descartado).
- **Cadastro CONAB** = armazéns registrados; capacidade intra-fazenda não cadastrada pode ficar de fora (subestima o interior, mas não há razão para viés N–S sistemático).
- **Série histórica é estadual** (UF), não municipal — só dá contexto de magnitude, não de geografia.
- **O bootstrap mede estabilidade, não erro amostral**: o `ArmazensCadastrados.txt` é um **censo** (todos os armazéns registrados), não uma amostra. Reamostrar as instalações quantifica a **sensibilidade do centroide a quais instalações compõem o cadastro** — não incerteza amostral no sentido estatístico estrito. A faixa de 95% é defensável como medida de **estabilidade** (o centroide não depende de um punhado de silos), mas **não** é um erro-padrão de amostragem, e não deve ser lida como tal.
- Herda o caveat "sem MAUP/validação pixel" das camadas tabulares (a concordância ponto↔AMC a 0,3 km mitiga o MAUP aqui).

## Como rodar

```bash
py -3.14 scripts/centro_massa_capacidade.py            # baixa (cacheia) + centroide + figuras
py -3.14 scripts/centro_massa_capacidade.py --force    # re-baixa da CONAB
py -3.14 scripts/centro_massa_capacidade.py --sem-figuras
```

Requer `xlrd` (para o `.xls` binário da CONAB) além do stack geo padrão. Cacheia os dois arquivos da CONAB em `data/raw/conab/`.
