# Malha Fundiária Ambiental (LAPIG) — avaliação para a Perna 4

**Avaliação de dado externo** (2026-07-29). Avalia se a *Malha Fundiária Ambiental*
(LAPIG-UFG, v1.0) ajuda a **Perna 4** (inferência shift-share / mecanismo da "marcha") e
documenta o arquivo baixado. Não é uma decisão numerada (Dxx): é a avaliação de um
dado candidato, com veredito e plano de uso. Relaciona-se com
[aptidão edafoclimática](../../) (camada exógena atual da Perna 4), [D7](../pipelines/28C_bimodalidade_regional.md)
(1ª-diff desarma vazamento), [D26](tratamento_deriva_mosaico.md) (bracket, não correção)
e a **opção A da Perna 4** (19/jul: mecanismo, não o câmbio; teto cambial irrespondível;
não é pendência de completude).

---

## 1. O dado, em uma frase

Camada vetorial nacional, sem sobreposição, que resolve conflitos entre propriedades
privadas (CAR/SIGEF/SNCI), terras indígenas, unidades de conservação e outras classes
fundiárias por priorização AHP, e depois sobrepõe os ativos ambientais (APP e Reserva
Legal). Produto do LAPIG-UFG. Repositório: <https://github.com/lapig-ufg/malha-fundiaria-ambiental>.
Plataforma/download: <https://malhafundiaria.lapig.iesa.ufg.br/map>.

## 2. Composição (fontes e hierarquia)

Quatro grupos de fontes oficiais:

| Grupo | Camadas | Fonte |
|---|---|---|
| Social/proteção | TI, Quilombola, UC, Área militar, Corpo d'água, Área urbana | FUNAI, INCRA, MMA, SFB, ANA, IBGE |
| Reforma agrária | Assentamentos, Gleba pública, FPND | INCRA SNCI/SIGEF, SFB |
| Propriedade privada | Propriedade privada, CAR | INCRA SNCI/SIGEF, SICAR |
| Ativos ambientais | APP, Reserva Legal | FBDS+SICAR, SICAR |

Hierarquia AHP (15 níveis tenure + 1 de ativo ambiental), RC = 4,61% (< 10%): corpo
d'água=1, urbano=2, TI homologada=3, UC proteção integral=4, militar=5, propriedade
SIGEF/SNCI=6, assentamento=7, FPND=8, UC uso sustentável=9, gleba pública=10,
quilombola declarada=11, TI não-homologada=12, quilombola não-declarada=13, CAR sem
sobreposição=14, CAR com sobreposição=15. O ativo ambiental (APP/RL) é a 16ª classe,
sobreposta à tenure.

Pipeline: ingestão em PostgreSQL → pré-processamento (reprojeção para ESRI:102033
Albers equal-area, remoção de duplicados/inativos/"grilagem digital", rasterização
10 m) → hierarquização AHP → reclassificação → análise de sobreposição (mínimo
pixel-a-pixel) → integração ambiental (APP+RL por imóvel). Stack: QGIS 3.44+, GDAL,
DuckDB, Python 3.9+, PostGIS.

## 3. Temporalidade — o ponto que governa tudo

**Snapshot único.** Sem série. E, pela página de métricas do projeto, a malha LAPIG
avaliada é **"April/2026"** (comparada com Cartas da Terra iGPP "February/2026"). Logo:

- A malha é um **ponto-fim datado de 2026** — **posterior à janela inteira de desfecho
  da dissertação (1985–2024)**.
- As fontes (CAR, SIGEF, UC) são os registros "atuais" até início de 2026; o CAR é
  continuamente atualizado e reflete décadas de expansão da frente.
- **Consequência:** a malha é *resultado* do processo que a Perna 4 tenta inferir,
  medido no fim. Não pode ser pré-tratamento, não pode ser instrumento, não pode ser
  exposição exógena — nem mesmo moderador pré-tratamento. Só serve como **descritor
  estrutural do ponto final**.

## 4. Veredito para a Perna 4

**Como instrumento / exposição: NÃO.** E a data 2026 reforça o "não" para além do que
se via antes:

1. **Estático (snapshot).** A Perna 4 precisa de um *shifter* temporal (câmbio) e de
   uma exposição espacial. A aptidão edafoclimática já cumpre o papel de exposição — e
   mesmo assim **bateu no "teto temporal"** (a restrição é temporal, não espacial).
   Adicionar outra camada espacial estática não move essa fronteira; é a mesma parede.
2. **Endógena.** A malha é parcialmente derivada de CAR, e o cadastro CAR
   **co-movimenta com a frente** — é resposta à mesma expansão que a Perna 4 explica.
   Isso é exatamente o vazamento que a **D7 (1ª-diff)** foi montada para desarmar
   (área ~ produção/VA). A aptidão passa no teste de exogeneidade porque é
   geológica/climática e não se move; a malha não passa.
3. **Medida depois do desfecho.** Mesmo que fosse exógena em fonte, é de 2026 —
   posterior a todo o período de conversão que se quer explicar.

Colocar a malha no lugar da aptidão seria **retroceder** em todos os três eixos.

**Como placebo de especificidade: SIM, com caveat.** A Perna 4 já se sustenta no
padrão de especificidade (placebos, leads, jackknife) porque a permutação do shifter
deu p ≈ 0,07–0,13 e o veredito virou "corroborante, não estabelecida". A malha fundiária
é um instrumento barato de **placebo estratificado**: o *beat* do shift-share deveria
concentrar-se em **propriedade privada** (onde a agricultura mecanizada converte) e
**evaporar dentro de TI/UC** (onde a conversão é legalmente bloqueada). Isso não
levanta o p do teste principal; levanta a credibilidade da leitura por eliminação
("teto de oferta = 17% estoque / 83% resíduo"). Mesma lógica do bracket D26 e dos
placebos — agora particionando o espaço por uma fronteira **institucional**.

**O caveat novo (reverse-causalidade):** a designação de UC durante a janela é ela
mesma endógena ao período (uma UC criada em 2010 contém pixels que eram "convertíveis"
antes de 2010). Logo, "dentro de UC hoje" é um placebo contaminado. Só as classes
**pré-existentes/exógenas** (TI homologada, corpo d'água, malha urbana, militar)
escapam desse problema.

### 4.1 Estratificação recomendada do placebo

| Papel | Classes (hierarquia) | Risco de endogeneidade |
|---|---|---|
| **Placebo limpo** (efeito deve evapora) | Corpo d'água (1), Urbano (2), TI homologada (3), Militar (5) | Baixo — pré-existentes/físicos |
| Placebo frágil | UC proteção integral (4), UC uso sustentável (9), TI não-homologada (12) | Médio — designação é parcialmente outcome do período |
| **Bucket ativo** (efeito deve concentra) | SIGEF/SNCI (6), CAR ss/cs (14/15), Assentamento (7) | Alto (esperado — é onde a frente age) |

Leitura honesta a reportar: *"a conversão 1985–2024 ocorreu quase toda sobre o que hoje
é propriedade privada registrada, e é nula sobre TI homologada e corpos d'água; a
evidência é descritiva de especificidade, não causal sobre a malha."*

## 5. Caveat estrutural: Goiás tem pouca área protegida

Contagem de polígonos por classe (do arquivo baixado, §7) mostra que o estoque
protegido de GO é **pequeno**: TI Homologada = **4** polígonos, UC Proteção Integral
= 26, UC Uso Sustentável = 88. Goiás não é Amazônia — a maior parte do território é
propriedade privada (CAR + SIGEF/SNCI). Consequência: o placebo "a conversão evitou
área protegida" é **fraco em GO por construção** (não havia muito a evitar), não por
falha do dado. Rebaixa a expectativa: o placebo confirma "a conversão se concentrou
no privado" (bucket ativo gigantesco), mas tem **pouco poder de discriminação no
bucket protegido**. Dizer isso explicitamente na escrita.

## 6. O que pedir (se for requisitar mais)

Pedido mínimo (núcleo do placebo + reserva conversível):

1. **Recorte de GO do vetor hard-class** em **GeoParquet**, com `cls_malha`, `cod_malha`,
   `fonte`, `GEOCODIGO`. (GeoParquet não trunca nomes de campo como o `.shp`.)
2. **APP e RL por imóvel** — como camadas separadas ou fração de área por `cod_malha`.
   Permite computar "privado − APP∪RL" = reserva **legalmente** conversível (residual
   2026).
3. **(stretch, alto valor) `data_cadastro` do CAR por imóvel**, se retido. É a **única**
   âncora temporal do snapshot. Com ela, data-se a formalização fundiária de cada
   parcela e testa-se *conversão em terra não-registrada que se formaliza depois*
   (grilagem) vs. *conversão em terra já registrada* — um check de mecanismo que a
   Perna 4 consegue usar. Se existir, muda o jogo; se não, o endpoint-snapshot
   permanece.

Projeção: entregar em SIRGAS 2000 ou ESRI:102033; reprojeta-se para 5880 (ambos
equal-area, somas de área seguras). **Não pedir o raster 10 m** — o vetor basta.

**Não pedir:** série histórica da reserva conversível (já existe = estoque LULC de
MapBiomas 1985–2024); o raster nacional 10 m (overkill).

### 6.1 O que a série temporal da "reserva conversível" já é (não está no dado LAPIG)

A série temporal da reserva conversível **já existe no cubo** de MapBiomas: é o
estoque não-florestal/não-protegido (pastagem, mosaico, veg nativa fora de UC) ano a
ano, 1985–2024. O dado LAPIG **não** dá isso — é snapshot 2026. O que o LAPIG agrega de
único é a **fronteira legal/institucional no ponto-fim**: qual pixel é privado vs.
TI/UC, e dentro do privado quanto é APP∪RL. Ou seja, ele define a reserva
**legalmente** conversível (residual 2026), não o estoque histórico.

## 7. Arquivo baixado — inspeção

- **Arquivo:** `brasil_malhafundiaria_ambiental_10m_v3b_GO.parquet` (Downloads locais,
  2,0 GB).
- **Formato:** **GeoParquet vetorial** (não raster; o "10m" no nome é a resolução do
  pipeline que gerou os polígonos, não o formato). GeoParquet v1.1.0, geometria WKB.
- **Cobertura:** Goiás completo — 246 municípios (GEOCODIGO), 4.273.501 polígonos,
  46 row groups.
- **Projeção:** ESRI:102033 (Albers equal-area) — bbox em metros [684394, 1363939,
  1462493, 2243607], dentro da extensão BR do repo. **Atenção:** o CRS **não veio nos
  metadados** GeoParquet (há `bbox` e `encoding`, mas sem campo `crs`). Pior: o GeoParquet
  v1.1 *defaulta* para `OGC:CRS84` (WGS84, graus) quando `crs` está ausente, então
  `gpd.read_parquet` devolve `gdf.crs = OGC:CRS84` (não `None`) — o cheque `if gdf.crs is
  None` **não dispara** e o aviso "Geometry is in a geographic CRS" aparece ao calcular
  área. As coordenadas, porém, estão em metros Albers, então `.area` dá m² corretos; o
  rótulo é que mente. **Fix:** `gdf.set_crs("ESRI:102033", inplace=True, allow_override=True)`.
- **Geometria:** `MultiPolygon Z` (3D). O Z é descartável — `force_2d()` se alguma
  operação reclamar.

### 7.1 Schema

```
fonte      string     # CAR/SIGEF/SNCI/app/rl/...
cod_malha  string     # código do imóvel — chave para agregar APP/RL
cls_malha  string     # classe fundiária (rótulo, ver §7.2)
geo_id     string
GEOCODIGO  string     # código IBGE do município (7 dígitos)
geometry   binary     # WKB MultiPolygon Z
```

### 7.2 Classes e contagens (no arquivo GO)

| cls_malha | n polígonos | papel (§4.1) |
|---|---:|---|
| **Ativo Ambiental** (APP/RL) | 4.023.848 | não-tenure — passivo ambiental |
| SIGEF/SNCI | 125.115 | privado |
| CAR sem sobreposição | 85.393 | privado |
| CAR com sobreposição | 35.096 | privado |
| Malha Urbana | 3.011 | exógeno |
| Assentamentos | 400 | ativo |
| Gleba Pública | 212 | outro |
| Massa d'água | 298 | exógeno |
| UC Uso Sustentável | 88 | placebo frágil |
| UC Proteção Integral | 26 | placebo frágil |
| Terra Indígena Homologada | **4** | placebo limpo |
| TI Não Homologada | 1 | placebo frágil |
| Quilombola Declarado | 3 | — |
| Quilombola Não Declarado | 1 | — |
| Área Militar | 2 | exógeno |
| Floresta Pública Não Destinada | 3 | — |

**Surpresa positiva:** "Ativo Ambiental" (fonte `app`/`rl`) = **APP e Reserva Legal**,
94% das linhas. O download **já inclui o passivo ambiental** — a reserva conversível
(privado − APP∪RL) é computável com este único arquivo, sem pedido extra (melhor que o
caveat do §6).

> Mojibake: "sobreposi??o", "N?o" em console Windows é **cosmético** (cp1252 não
> renderiza UTF-8). As strings no Parquet são UTF-8 corretas; o geopandas lê certo.

## 8. Como carregar (stack verificado: Py 3.14, pyarrow 24, geopandas 1.1.3, shapely 2.1.2)

```python
import geopandas as gpd

path = r"C:\Users\amara\Downloads\brasil_malhafundiaria_ambiental_10m_v3b_GO.parquet"
gdf = gpd.read_parquet(
    path, columns=["cls_malha", "cod_malha", "fonte", "GEOCODIGO", "geometry"]
)
if gdf.crs is None:                       # CRS não veio nos metadados
    gdf.set_crs("ESRI:102033", inplace=True)
gdf = gdf.to_crs(5880)                     # -> Brazil Polyconic (stack do projeto)

tenure = gdf[gdf.cls_malha != "Ativo Ambiental"]   # ~250k polys — leve, é a partição
ativos = gdf[gdf.cls_malha == "Ativo Ambiental"]   # 4M — APP/RL; carregar só p/ reserva
```

Carregar por colunas e separar tenure de Ativo Ambiental no filtro: a partição do
placebo roda só com os ~250k de tenure (leve). Os 4M de APP/RL só se puxam na hora de
computar a reserva conversível.

`duckdb` não está instalado no ambiente, mas **não é necessário** — o caminho pyarrow
cobre leitura e escrita.

## 9. Plano de uso (se for adiante)

1. Carregar como em §8; recortar em GO (já é GO; confirmar sem buraco por município).
2. Rasterizar `cls_malha` para a grade do cubo MapBiomas (30 m, EPSG:5880), regra =
   classe dominante por pixel. Atribuir a cada pixel do cubo uma `cls_malha` (ou
   máscara binária `protegido = TI homologada ∪ UC proteção integral ∪ corpo d'água`).
3. No shift-share da Perna 4, particionar o *beat* por `protegido` vs. `privado`.
   Reportar a fração do efeito em cada partição **+** o caveat reverse-causal nas UC.
4. (Opcional) computar a reserva conversível residual (privado − APP∪RL) e checar
   correlação espacial com a direção da "marcha" (Norte) — **descritivo, não causal**:
   "a reserva residual está no Norte" é consistente com a marcha, mas é leitura
   post-hoc (o Sul pode ter exaurido a sua).
5. **Não entrar como regressor** em nenhuma especificação — só como partição de amostra.

## 10. Breakdown de área por `cls_malha` — RODADO (29/jul/2026)

Script: `scripts/diag_malha_fundiaria.py`. Saídas: `outputs/diag_malha_fundiaria_por_classe.csv`
e `_por_fonte.csv`. Área em ESRI:102033 (Albers equal-area, m²→ha). **Atenção ao
double-counting:** "Ativo Ambiental" (APP/RL) é um *overlay* sobreposto à tenure (§2),
não uma classe tenure — somar tudo dá 39,60 Mha, mas o **território efetivo (tenure) =
32,30 Mha** (= 39,60 − 7,30 de APP/RL). Sanity: GO ≈ 34 Mha; 32,3 é ~5% sob (efeito de
borda água/urbano + contorno do recorte). 246 municípios, sem buraco.

| Bucket | área (Mha) | % da tenure | papel |
|---|---:|---:|---|
| **Privado bruto** (SIGEF/SNCI + CAR ss + CAR cs) | 29,27 | 90,6% | onde a frente age |
| **Protegido** (TI + UC PI + UC US + quilombo) | 1,28 | 4,0% | placebo (frágil p/ UC) |
| — do qual **Placebo limpo** (TI homol. + água + urbano + militar) | 0,69 | 2,1% | exógeno, reverse-causal-safe |
| — do qual **Placebo frágil** (UC + TI não-homol. + quilombo) | 1,25 | 3,9% | designação parcialmente outcome |
| **APP/RL** (overlay, passivo ambiental) | 7,30 | — (overlay) | RL 5,32 + APP 1,98 |
| Assentamentos | 1,01 | 3,1% | bucket ativo |
| Gleba pública + FPND | 0,08 | 0,2% | outro |
| **Território efetivo (tenure)** | **32,30** | 100% | — |

**Leitura que quantifica o caveat §5:** Goiás é **90% privado, 4% protegido**. A TI
homologada somada é **33 mil ha** (0,03 Mha) — minúscula. Consequência para o placebo
de especificidade: o bucket "protegido" onde o *beat* deveria evaporar é **4% do
território**, e o subset honesto (exógeno, reverse-causal-safe) é **2%**. Ou seja, o
placebo confirma "a conversão se concentrou no privado" — mas isso é **quase
tautológico** quando 90% já é privado. O poder de discriminação do placebo é baixo **por
construção**, não por falha do dado. Dizer isso explicitamente.

**Reserva conversível (privado − APP∪RL):** ≈ 29,27 − 7,30 ≈ **21,97 Mha** (aproximado —
o overlay exato depende de quanto APP/RL cai dentro do privado vs. dentro de UC/assent.;
cálculo exato pende de `erase` espacial, §10-pendente abaixo). Já é consistente com a
"marcha": a reserva residual está no eixo Norte, mas é leitura post-hoc (o Sul pode ter
exaurido a sua).

### 10.1 Pendências remanescentes (NÃO rodadas)

- **Overlay espacial APP/RL × tenure** (`erase` ou `union`): quantificar quanto do
  7,30 Mha de APP/RL cai *dentro* do privado vs. dentro de UC/assentamento, para virar o
  "privado bruto" em "privado líquido conversível" exato. Caro (4M polys de APP/RL);
  só vale se a reserva conversível virar figura.
- Verificar se os polígonos "Ativo Ambiental" carregam o `cod_malha` do imóvel-pai
  (habilitaria agregação APP/RL por propriedade via group-by, mais barato que erase
  espacial).
- Confirmar a janela temporal exata do snapshot (a página de métricas diz "April/2026"
  para a malha LAPIG; confirmar com a equipe se refere à data de corte das fontes).

## 11. Estado

Avaliação concluída; **breakdown de área rodado (§10, 29/jul/2026)**. **Sem mudança no
veredito da Perna 4** (opção A, 19/jul) — este dado não resolve pendência de
completude; é apenas robustez voluntária (placebo de especificidade por fronteira
institucional). O §10 **reforça** o caveat §5 com números: GO é 90% privado / 4%
protegido (placebo limpo = 2% da tenure), então o placebo é de baixo poder por
construção. Uso condicionado a decidir se esse placebo de baixo poder vale o esforço do
overlay espacial (§10.1) e da rasterização para a grade do cubo.