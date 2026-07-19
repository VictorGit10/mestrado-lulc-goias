# Pipeline #52 — Aptidão edafoclimática exógena como exposição no #38

**Scripts**: `scripts/aptidao_edafo_exposicao.py` (52A — constrói a exposição + valida o gradiente)
e `scripts/aptidao_edafo_drive38.py` (52B — entra a exposição no teste de interação do #38).
**Quando foi feito**: 2026-07-18. Realiza a frente de expansão "aptidão edafoclimática direta como
exposição no #38" que o backlog vinha listando (ataca o **drive comum** — a metade mais fraca da tese, hoje o *positivo da Perna 3*).
**Depende de**: #38 (`drive_comum_amc.py`, importado integralmente em 52B), #25 (`amc_goias.gpkg`,
geometria das AMCs), #17/AMC (`taxas_lulc_amc.csv`, shares baseline), #39 (`fronteira_estoque_convertivel.csv`,
região + latitude por AMC). Reusa a máquina de overlay vetorial × AMC do #46.
**Outputs**:
- `data/processed/aptidao_edafo_amc.csv` — aptidão por AMC (score, % apto p/ lavoura, exp_apt_edafo, lat, região).
- `data/processed/drive_amc_apt_confirmatorio.csv` — confirmatórias do #38 + as novas (com aptidão exógena).
- `data/processed/drive_amc_apt_exploratorio.csv` — grade completa de 192 (4 exposições) + FDR-BH.
- `outputs/aptidao_edafo/validacao_gradiente.png` — mapa por AMC + aptidão × latitude (52A).
- `outputs/aptidao_edafo/interacao_confirmatoria_apt.png` — forest plot das confirmatórias novas (52B).

---

## Pergunta de pesquisa

O #38 testa "o choque comum (câmbio) bate mais forte onde a **exposição** é maior?". A exposição
que ele usa é **"% de área baseline 1985-89"** — um proxy de aptidão com dois defeitos que o próprio
#38 declarou:

1. **Mecanicamente complementar**: as três exposições são *shares* que somam ~constante, então
   `exp_fronteira ≈ −exp_apt_agri`. O Achado #3 do #38 apontou que isso **infla a "coerência de
   sinais"** — não são três ângulos independentes, é um gradiente visto de ângulos ligados.
2. **Semi-endógena**: um *share* de uso humano em 1985-89 já reflete escolhas (infraestrutura,
   história de ocupação), não só a aptidão física.

A pergunta do #52 é: **e se a exposição for uma aptidão edafoclimática física — exógena e
não-complementar?** Isso não muda o teto de poder do #38 (o driver varia só ~40×), mas melhora a
**identificação**: remove a objeção de complementaridade do achado-manchete.

Em duas etapas: **52A** valida antes de testar (a pergunta mais barata e mais robusta); **52B** entra
a exposição no #38.

---

## O dado

**Embrapa GeoServer WFS** — camada `geonode:aptidao_agr_bra` (*Aptidão Agrícola das Terras do Brasil*,
1:500.000), puxada por WFS GetFeature (GeoJSON) recortada no bbox de GO: **8.284 polígonos**. O campo
`simb_apt` segue o sistema **Ramalho Filho & Beek (1995)** — o **dígito líder** é o grupo de aptidão:

| Grupo | Legenda | Score (7−grupo) |
|---|---|---|
| 1 | boa para lavouras | 6 |
| 2 | regular para lavouras | 5 |
| 3 | restrita para lavouras | 4 |
| 4 | apta só para pastagem plantada | 3 |
| 5 | silvicultura / pastagem natural | 2 |
| 6 | preservação da flora e fauna | 1 |

Maior score = mais apto para lavoura. Dos 8.284 polígonos, **1.848 (22%) não têm grupo** (água,
urbano, corpos sem classe de aptidão) e são **excluídos** da média — não se calcula aptidão média
sobre um rio. Em GO aparecem grupos 1-4 e 6 (grupo 5 ausente).

> **Por que a Embrapa, e não o MacroZAEE-GO.** O MacroZAEE estadual (1:250k, fonte oficial de Goiás)
> seria mais fino, mas **não é fetchável** deste ambiente: não está publicado nos GeoServers estaduais
> alcançáveis (o SIGA/meioambiente só traz zoneamentos de UC e solos IBGE), e o portal do SIEG tem
> certificado TLS quebrado (`no-sni.goias.gov.br`) + derruba conexões automáticas. Exigiria download
> manual no navegador + remapeamento da legenda própria do MacroZAEE. **Fica como pendência** (ver
> abaixo); a pipeline aceita a troca da camada-fonte com mudança mínima.

---

## Método

**52A — exposição + validação** (`aptidao_edafo_exposicao.py`):
1. WFS paginado (chunks de 2.000) → cache `data/raw/aptidao/aptidao_agr_bra_go.gpkg`.
2. `simb_apt` → grupo (1..6) → score (7−grupo). Fallback: dígito da legenda.
3. **Overlay com as 166 AMCs em EPSG:5880** (equal-area, reusa a máquina do #46). Aptidão da AMC =
   média do score **ponderada por área** dos polígonos que a cobrem. Variante de robustez guardada:
   `pct_apt_lavoura` = % da AMC com grupo ≤ 3.
4. **z-score** sobre as 166 AMCs → `exp_apt_edafo` (pronta para o #38).
5. **Validação**: correlaciona `exp_apt_edafo` com a latitude do centróide, com a exposição atual do
   #38 (% agri baseline) e com a fronteira (% veg baseline). Pearson + Spearman (ordinal).

**52B — a exposição no #38** (`aptidao_edafo_drive38.py`): importa `drive_comum_amc` (#38) e reusa
**integralmente** seu desenho — interação 2-way FE `Δy = α_i + γ_t + β·(Δdriver × exposição)`,
clusterização dupla (entidade+ano, fallback entidade), mesmos z-scores, mesmo FDR-BH. `exp_apt_edafo`
entra como **4ª exposição, adicionada** às três do #38 (decisão: **adicionar, não substituir** —
preserva a comparabilidade com o #38 publicado e explicita o contraste "exógena vs. proxy de área").
Confirmatório novo, pré-declarado com direção (espelho exógeno dos testes do #38 sobre a fronteira —
o sinal inverte porque aptidão alta = núcleo Sul, oposto da fronteira).

---

## Achados

### 52A — a aptidão exógena REPRODUZ o gradiente Sul→Norte

A premissa que sustenta toda a narrativa ("o Sul é apto, o Norte é fronteira") era **assumida** —
provada só por *shares* de uso da terra. Agora é **medida** com um dado físico independente do LULC:

| Correlação (n=166 AMCs) | Pearson | Spearman | Esperado |
|---|---|---|---|
| aptidão × latitude | **−0,44** (p<0,0001) | −0,40 | − (apto no Sul) ✓ |
| aptidão × exp. atual do #38 (% agri baseline) | +0,30 (p=0,0001) | +0,42 | + ✓ |
| aptidão × fronteira (% veg baseline) | **−0,69** (p<0,0001) | −0,69 | − ✓ |

Média por região, **monotônica**: **Sul 4,69 > Centro 4,47 > Norte 4,17**.

Dois pontos, e o segundo é o que importa para a identificação:
- A aptidão física correlaciona **forte** com a fronteira (−0,69): a marcha ao norte avança, de fato,
  sobre terra de aptidão inferior.
- A correlação com a exposição *atual* do #38 é só **moderada (+0,30)**. Isso é **bom**: `exp_apt_edafo`
  aponta na mesma direção mas **não é clone** do "% agri baseline" — carrega informação exógena própria.
  É exatamente o ganho de identificação buscado (quebra a complementaridade mecânica).

### 52B — o achado-manchete do #38 reaparece com a exposição exógena, e um pouco mais firme

Reprodução do #38 inalterada (sanity ✓). O único elemento com standing do #38 reaparece como
**espelho exógeno**:

| Câmbio × exposição → Δ Rebanho (lag 1) | β | p |
|---|---|---|
| Fronteira (% veg — proxy de área, #38) | +0,0285 | 0,031 |
| **Aptidão física (exógena — #52)** | **−0,0325** | **0,026** |

Mesma história, dois ângulos: sob depreciação cambial, o rebanho cresce **mais onde a aptidão é baixa**
(a fronteira Norte) e **menos no núcleo apto** (Sul). Os sinais são opostos só porque aptidão alta =
núcleo e fronteira alta = Norte. **O ganho**: a versão exógena **não sofre** da complementaridade
mecânica — o headline deixa de depender de um *share* que empresta o resultado de si mesmo. Os nulos de
área continuam nulos (câmbio × aptidão → pastagem p=0,83; preço soja × aptidão → agricultura p=0,60).

### 52B — a grade exploratória passou de 0 para 2 sobreviventes do FDR — mas isso corta nos dois sentidos

Na família honesta de **192 testes** (4 exposições × 4 drivers × 4 desfechos × 3 lags), sobrevivem ao
FDR-BH:
- `crédito × aptidão exógena → Δ veg` (lag 0; p=0,0003; p_fdr=0,042) — **novo**;
- `câmbio × aptidão agrícola → Δ rebanho` (lag 0; p=0,0004; p_fdr=0,042).

**Ressalva de honestidade (a mesma do Achado #2 do #38, agora cortando a favor)**: o segundo é
**exatamente** o *cell* que o #38 documentou como frágil — sobrevivia na grade de 96, morria na de 144
(p_fdr 0,042→0,063). Ele ressuscita aqui porque a nova exposição adiciona um segundo *p* minúsculo que
se **reforça** com ele no passo do Benjamini-Hochberg. Ou seja, é a mesma **sensibilidade ao tamanho da
família** que o #38 alertou — não uma replicação independente que "fecha" a questão. A evidência
exploratória firmou de 0→2, com o mesmo mecanismo de fragilidade.

**Camada mais profunda — a costura com o #54.** Há uma razão *além* do tamanho de família para
desconfiar do sobrevivente do **câmbio**: seu `p=0,0004` é um erro-padrão **clusterizado**, e o #54
mostrou que, para um shift-share de shifter único nacional (o câmbio), esse SE é **otimista**. Sob a
inferência correta — permutação do shifter — o p do `câmbio × aptidão → rebanho` sobe para
**≈0,07–0,13**, e um p desse tamanho **não sobreviveria** ao FDR. Isto é, o próprio insumo do
Benjamini-Hochberg está subestimado: o sobrevivente do câmbio é ainda mais frágil do que "sensibilidade
ao tamanho da família" já sugeria — ele é **duplamente frágil** (tamanho de família *e* SE otimista). O
sobrevivente do **crédito** (`crédito × aptidão → Δ veg`), ao contrário, **não** sofre disso: o crédito
(SICOR) varia por AMC×ano — não é um shifter único —, então seu p não é otimista no sentido AKM/BHJ e a
permutação do #54 não o toca. Dos dois sobreviventes, é o do crédito que tem standing exploratório; o do
câmbio deve ser lido como artefato de multiplicidade sobre um insumo já otimista. Ver
[`54_defensabilidade_perna4.md`](54_defensabilidade_perna4.md).

---

## Veredito

> **Atualização de inferência (#54, 2026-07-18).** O `p=0,026` reportado abaixo é o **erro-padrão
> clusterizado** (entidade+ano). O #54 mostrou que, para um shift-share de **um único shifter
> nacional** (o câmbio), esse SE é **otimista** (resultado AKM 2019): a inferência correta —
> **permutação do shifter** — dá **p≈0,07 (naive) a 0,13 (rotação circular), não significante a
> 5%**. Leia o `p=0,026` deste doc como o número clusterizado do desenho original, **não** como a
> significância defensável do achado. O ganho de **identificação** do #52 (abaixo) permanece
> válido; o que muda é que a **significância** cai para "corroborante, não estabelecido". Ver
> [`54_defensabilidade_perna4.md`](54_defensabilidade_perna4.md).

O drive comum (o positivo da Perna 3) vai, **na identificação**, de **"sugestiva"** para **"sugestiva mais firme / mais defensável"** — não "estabelecida" (e a **significância** é calibrada para baixo pelo #54; ver caixa acima).
O que mudou de fato:
- O achado-manchete (câmbio × aptidão → rebanho de fronteira) fica **livre da objeção de
  complementaridade**: confirma-se com uma exposição exógena, não-complementar (β=−0,033, p=0,026).
- A premissa "Sul apto / Norte fronteira" **deixa de ser assumida e vira medida** (52A).
- A grade exploratória firmou de 0→2 sobreviventes do FDR — mas via a mesma fragilidade de tamanho de
  família que o #38 flagou, então **beira** um FDR-survivor sem cruzar para "estabelecido".

O **teto de poder temporal** do #38 (o driver varia só ~40×) segue intacto — uma exposição exógena
limpa a **identificação**, não fabrica **poder**. Um IV para o câmbio seria o próximo passo para sair
de "sugestivo firme" para "estabelecido".

## Limitações

- **Mapa nacional 1:500k**, mais grosso que um ZAEE estadual. O MacroZAEE-GO refinaria (ver pendência).
- **Codificação ordinal**: o score usa o dígito-grupo do `simb_apt` (colapsa os níveis de manejo a/b/c).
  A variante `pct_apt_lavoura` (grupos 1-3) fica guardada para robustez.
- **Aptidão time-invariant** (um snapshot) — adequado como exposição baseline, coerente com o desenho do #38.
- **Herda os limites do #38**: identifica gradiente (não nível); 3 fallbacks de vcov não-PSD (mesmo
  comportamento conhecido); crédito parcialmente endógeno.
- **Descritivo em 52A**: a validação não testa a interação (isso é 52B) nem resolve o teto temporal.

## Pendência registrada — MacroZAEE-GO (IMB/SIEG)

Refinar a exposição com o **"Mapa de Aptidão Agrícola das Terras" do MacroZAEE-GO** (estadual, 1:250k,
fonte oficial de Goiás — mais defensável para a banca). **Bloqueio**: não é fetchável deste ambiente
(cert TLS quebrado + hosts do SIEG derrubam conexão automática). **Caminho**: download manual no portal
IMB/SIEG (`goias.gov.br/imb/download-de-arquivos-sig-shapefile/` → "SIG do MacroZAEE"), arquivo em
`data/raw/aptidao/`, e remapear a legenda própria do MacroZAEE (não é Ramalho Filho & Beek). A pipeline
52A isola a fonte em `baixar_aptidao()`/`preparar_aptidao()` — troca de baixo custo. **Ganho esperado:
defensabilidade da versão escrita, não novo resultado** (52B já mostrou que o achado se sustenta e o
gargalo que resta é temporal, que um mapa mais fino não move).

## Como rodar

```bash
py -3.14 scripts/aptidao_edafo_exposicao.py           # 52A: exposição + validação
py -3.14 scripts/aptidao_edafo_exposicao.py --force   # re-baixa o WFS
py -3.14 scripts/aptidao_edafo_drive38.py             # 52B: a exposição no #38
```

52A cacheia o WFS em `data/raw/aptidao/`. 52B importa o #38 e o restaura ao fim (sem efeito colateral).

---

## Conexão com a narrativa

| Camada | Pipeline | Pergunta | Resposta |
|---|---|---|---|
| 4/5 | #37 | Qual é o drive comum? | Assinatura cambial fraca (UF/anual, N≈38). |
| 5 | #38 | O drive opera sobre o gradiente de aptidão (proxy de área)? | Indício sugestivo; nada sobrevive ao FDR (144). |
| **5** | **#52** | **E com aptidão edafoclimática EXÓGENA?** | **A premissa do gradiente vira medida (52A); o achado do rebanho confirma-se sem a complementaridade (β=−0,033, p=0,026) e beira o FDR (52B). Mais firme e mais defensável — não estabelecido; teto temporal intacto.** |

O #52 **fortalece a identificação** do drive comum (o positivo da Perna 3, a metade mais fraca) sem quebrar seu teto de poder: troca um
proxy de área mecanicamente complementar por uma aptidão física exógena, e o achado-manchete
sobrevive — mais defensável. Não fecha o drive comum; a leva de "sugestiva" a "sugestiva mais firme".
