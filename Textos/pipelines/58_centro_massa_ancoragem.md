# Pipeline #58 — Quem segura e quem move o centro de massa

**Script**: `scripts/centro_massa_ancoragem.py`
**Quando foi feito**: 2026-09-28. Veio de uma sugestão de Mario Barroso: os revisores de um
manuscrito dele sobre centros de massa de área queimada por bioma pediram métricas de
exclusão (*leave-one-out*) e de alavanca, e ele propôs rodá-las com as zonas de Goiás.
**Depende de**: #32 (centro médio, centroides das AMCs, bootstrap D19), #34 (`amc_para_meso`,
regra canônica de região), #55 (`kmeans_blocos`, bootstrap em blocos), #25 (painel AMC).
**Outputs**:
- `data/processed/centro_massa_ancoragem_anual.csv`: partição × variável × ano × zona (peso,
  LOO, puxão N–S e L–O, influência, *share*).
- `data/processed/centro_massa_ancoragem_resumo.csv`: mediana e IQR entre anos, período
  completo e por Ato.
- `data/processed/centro_massa_decomposicao.csv`: partição × variável × janela × zona (termos
  ENTRE e DENTRO, N e L, extremos e encadeado).
- `data/processed/centro_massa_decomposicao_ic.csv`: IC95% do total, do ENTRE, do DENTRO e da
  fração ENTRE, com k = 166 (i.i.d.), 33 e 12 blocos.
- `outputs/centro_massa/ancoragem_puxao_norte.png`, `ancoragem_decomposicao.png`.

---

## Pergunta de pesquisa

O #32 mede quanto o centro de massa se deslocou. Não diz que parte do estado o segura onde
ele está, nem o que o moveu. A regra de leitura adotada em setembro ("o centro de gravidade
está N km mais ao norte", nunca "a lavoura subiu") se apoiava até aqui numa tabela de
composição por região. Faltava medir quanto do deslocamento é troca de peso entre regiões e
quanto é movimento dentro delas.

## Abordagem

O centro médio se decompõe sem perda por qualquer partição do estado em zonas. Se `A_b` é a
massa da zona *b* (ha ou cabeças), `w_b = A_b / Σ A` o seu peso e `C_b` o centro médio das
AMCs da zona, então `C = Σ w_b · C_b`. O script confere que essa reconstrução reproduz o
centro publicado pelo #32 nas seis variáveis e nos quarenta anos (diferença máxima de
5·10⁻⁹ m).

**1. Ancoragem (métricas do manuscrito).** Por ano e zona:

| Métrica | Definição | O que mede |
|---|---|---|
| LOO | `|C − C^(−b)|`, o centro recomputado sem a zona *b* | quanto o centro muda se a zona sai (km, 2D) |
| Puxão norte | `C_N − C_N^(−b)` | o mesmo, só na direção N–S e com sinal (+ = a zona puxa ao norte) |
| Influência | `w_b · |C_b − C|` | braço de alavanca: massa × distância ao centro |
| *Share* | influência / soma das influências | fatia da alavanca total, soma 1 no ano |

Os resumos entre anos usam mediana e IQR, como no manuscrito.

**As duas métricas do manuscrito são a mesma quantidade.** Como `C − C^(−b) = w_b(C_b − C^(−b))`
e `C_b − C = (1 − w_b)(C_b − C^(−b))`, vale exatamente **`LOO_b = Influência_b / (1 − w_b)`**.
O manuscrito as apresenta como complementares; em rigor são uma medida em duas escalas. O
script verifica a identidade em todas as linhas e reporta as duas por fidelidade ao método.

**2. Decomposição do deslocamento.** Entre dois anos, a identidade simétrica (ponto médio)

```
ΔC = Σ_b (w_b1 − w_b0)·(C̄_b − C̄)   +   Σ_b (w_b0 + w_b1)/2·(C_b1 − C_b0)
          ENTRE zonas (troca de peso)       DENTRO das zonas (movimento interno)

C̄_b = (C_b0 + C_b1)/2      C̄ = (C_0 + C_1)/2   (centro do estado, média dos dois extremos)
```

fecha sem resíduo. A soma do termo ENTRE não depende da referência C̄, porque os pesos somam
1 nos dois anos (Σ Δw = 0); a parcela de cada zona depende, e a referência é o que dá a ela
leitura: quanto a mudança de fatia daquela zona empurrou o centro. Uma zona sem massa num dos extremos recebe o centro do outro extremo: o seu
DENTRO é zero e ela contribui só pela troca de peso. Há também a versão **encadeada** (soma das
decomposições ano a ano), para saber se a partição depende do caminho.

**3. Partições.** A escala das zonas é parte do resultado, e por isso rodam quatro:

| Partição | Zonas | Papel |
|---|---|---|
| 3 regiões | Sul (Sul Goiano, 58 AMCs) · Centro (Centro + Leste, 78) · Norte (Norte + Noroeste, 30) | a regra canônica do projeto (#34, #39, #57) |
| 5 mesorregiões | as do IBGE | granularidade administrativa |
| 4 faixas de latitude | quartis da latitude do centroide da AMC | partição sem fronteira administrativa |
| 166 AMCs | cada AMC é uma zona | teste de sanidade: DENTRO tem de dar zero |

**4. Incerteza.** Bootstrap de AMCs com B = 2000, i.i.d. (D19) e em blocos espaciais do #55
(k = 33 e 12). Cada AMC leva a sua zona consigo.

## Validações

| Conferência | Resultado |
|---|---|
| Centro reconstruído por zona × centro do #32 (6 variáveis × 40 anos, 3 regiões e 5 meso) | |Δ| máx 5,6·10⁻⁹ m |
| ΔNorte LÍQUIDO da decomposição × `centro_massa_deslocamento.csv` | idêntico nas 4 variáveis do #32 |
| Partição de 166 AMCs | DENTRO = 0 e ENTRE = 100% em todas as janelas |
| Identidade LOO = Influência/(1 − w) | verificada em todas as linhas (tolerância relativa 10⁻⁹) |
| LOO por força bruta (centro sem as AMCs da zona, recalculado direto do painel), 4 casos em partições e anos diferentes | igual até a 4ª casa decimal |
| IC95% do ΔNorte total, k = 166, 33, 12 × `centro_massa_bootstrap_bloco.csv` (#55) | mesmas faixas, a menos da semente (pastagem i.i.d.: [+55,7; +99,3] × [+53,9; +98,6]) |
| *Share* | soma 1,000 em todo ano |
| Encadeada × extremos | ENTRE difere em menos de 3 km em todas as janelas com deslocamento robusto |

## Achados

### Ancoragem: o Sul segura, e o que muda é quanto

3 regiões, 1985–2024, mediana entre anos (IQR entre colchetes):

| Variável | Região | Peso 1985 → 2024 | LOO (km) | Puxão norte 1985 → 2024 (km) | *Share* |
|---|---|---|---|---|---|
| Pastagem | Sul | 50% → 32% | 125 [117–134] | −137 → −100 | 45% |
| | Centro | 28% → 31% | 54 [53–54] | +33 → +16 | 22% |
| | Norte | 21% → 38% | 81 [71–87] | +57 → +91 | 33% |
| Rebanho | Sul | 47% → 32% | 117 [110–127] | −134 → −96 | 45% |
| | Centro | 30% → 33% | 47 [46–49] | +36 → +16 | 21% |
| | Norte | 23% → 34% | 80 [72–82] | +58 → +83 | 34% |
| Agricultura | Sul | 92% → 71% | 241 [221–254] | −171 → −169 | 49% |
| | Centro | 7% → 21% | 51 [42–59] | +13 → +37 | 43% |
| | Norte | 1% → 7% | 7 [7–14] | +2 → +21 | 8% |
| Vegetação natural | Sul | 28% → 26% | 95 [95–97] | −86 → −83 | 43% |
| | Centro | 35% → 36% | 62 [61–64] | +14 → +12 | 24% |
| | Norte | 37% → 38% | 86 [86–86] | +85 → +86 | 32% |

O resultado sobre a **posição** do centro já era esperado: o Sul é a região que mais o
ancora em todas as camadas, porque é a mais pesada e a mais distante do centro. A informação
nova está na **trajetória** do puxão:

- **Pastagem e rebanho**: o puxão do Sul para o sul perde 37–38 km e o do Norte para o norte
  ganha 25–35 km. As duas pontas se movem.
- **Agricultura**: o puxão do Sul fica igual (−171 → −169 km). O peso do Sul cai de 92% para
  71%, mas a distância N–S entre o centro do Sul e o do resto do estado cresce de 185 para
  238 km e compensa a perda. O centro de gravidade fica mais ao norte porque Centro e Norte
  ganham peso, e a lavoura do Sul não perde força de ancoragem.
  Isso confirma com uma métrica a tabela de composição de setembro (a lavoura cresce mais no
  Sul em hectares e muda de fatia).
- **Vegetação natural**: os três puxões ficam parados, o que é coerente com o centro
  ancorado da D19.

### Decomposição: três quartos do deslocamento são troca de peso entre regiões

ΔNorte 1985 → 2024 (km), 3 regiões:

| Variável | Total | ENTRE (troca de peso) | DENTRO (movimento interno) | Fração ENTRE, IC95% i.i.d. | Fração ENTRE, k = 12 |
|---|---|---|---|---|---|
| Pastagem | +77,6 | +62,8 | +14,8 [+5,4; +23,3] | 81% [67; 93] | [56; 99] |
| Rebanho | +66,9 | +50,2 | +16,7 [+9,4; +23,2] | 75% [62; 87] | [49; 89] |
| Agricultura | +65,2 | +48,4 | +16,8 [+5,0; +28,2] | 74% [62; 92] | [52; 102] |
| Soja plantada (SIDRA, 1988–2024) | +48,3 | +37,9 | +10,4 [−3,3; +23,5] | 79% [49; 108] | [41; 115] |

Na escala de três regiões, **entre três quartos e quatro quintos** do deslocamento de pasto,
rebanho e lavoura vêm de as regiões mudarem de peso, e não de a atividade andar ao norte
dentro de cada uma. É a defesa quantitativa da leitura "centro de gravidade N km mais ao
norte": o deslocamento é sobretudo redistribuição entre regiões.

O termo DENTRO **não é zero**. Nas três camadas-manchete ele é positivo, com 15–17 km e IC
i.i.d. que exclui zero: dentro de cada região a massa também se deslocou ao norte. Sob blocos
espaciais grandes (k = 12) o DENTRO da agricultura passa a incluir zero; o do pasto e o do
rebanho, não. As duas coisas acontecem ao mesmo tempo, e a redistribuição é a maior.

A versão encadeada dá o mesmo quadro (pastagem: ENTRE +62,5 encadeado × +62,8 nos extremos):
a divisão não depende do caminho.

**Por região** (parcela de cada uma no ΔNorte, km; troca de peso | movimento dentro):

| Variável | Sul | Centro | Norte |
|---|---|---|---|
| Pastagem | +32,3 \| −0,4 | +1,4 \| +9,0 | +29,1 \| +6,3 |
| Rebanho | +26,8 \| +4,9 | +1,9 \| +5,0 | +21,5 \| +6,8 |
| Agricultura | +8,7 \| +9,2 | +21,1 \| +5,6 | +18,7 \| +2,0 |

No pasto e no rebanho, as duas pontas contribuem quase igual: o Sul pela fatia que perde, o
Norte pela que ganha. Na agricultura, a perda de fatia do Sul contribui só +8,7 km, e o grosso
vem do Centro e do Norte ganhando fatia. É a mesma leitura do puxão do Sul, que na lavoura não
cede.

> **Correção de 28/set/2026 (mesmo dia).** A primeira versão gravava a parcela ENTRE de cada
> zona em coordenadas absolutas (`Δw_b · C̄_b`, com C̄_b na casa dos 8.000 km). A **soma** entre
> zonas não depende da origem, porque Σ Δw = 0, e por isso os totais, as frações e os IC estavam
> certos desde o início. A **parcela de cada zona**, não: sem referência ela não tem leitura. Ela
> passou a ser medida em relação ao centro médio dos dois extremos, `Δw_b · (C̄_b − C̄)`. Só a
> coluna `entre_N_km`/`entre_L_km` por zona de `centro_massa_decomposicao.csv` mudou, e nenhuma
> tabela desta ficha usava a versão anterior. O defeito apareceu quando a mesma conta, feita por
> cultura no #59, devolveu parcelas de ±3.000 km.

**Por Ato** (3 regiões, fração ENTRE): pastagem 82% / 79% / 78% nos Atos I, II e III; rebanho
80% / 67% / 66%; agricultura 66% / 79% nos Atos I e II. No Ato III a agricultura não se
desloca (+0,2 km, IC que inclui zero pela D19) e a fração perde sentido.

### A fração depende da escala das zonas

| Variável | 3 regiões | 4 faixas de latitude | 5 mesorregiões | 166 AMCs |
|---|---|---|---|---|
| Pastagem | 81% | 97% | 89% | 100% |
| Rebanho | 75% | 93% | 82% | 100% |
| Agricultura | 74% | 94% | 73% | 100% |

Não há leitura de "X% do deslocamento é troca de peso" sem a escala ao lado. Com as 166 AMCs
a fração é 100% por construção, porque o centroide de uma AMC não se move. As faixas de
latitude dão frações altas também por construção: numa faixa estreita no sentido N–S, o
centro interno quase não tem para onde se mover ao norte. A leitura correta é a de uma
escala: **quando o estado é visto em 3 a 5 pedaços, a maior parte do deslocamento já aparece
como mudança de peso entre os pedaços.**

### O caso da união lavoura + Mosaico

A régua-teto da D26 se desloca **ao sul** no período completo (−60,5 km, igual ao #32), e 89%
disso é troca de peso: a fatia do Norte na união cai de 25% para 11%. O deslocamento ao sul já
estava no #32; a decomposição acrescenta que ele também é redistribuição entre regiões.

## Sensibilidade

**AMC dividida.** A AMC 16151 (Niquelândia + Mimoso de Goiás) tem um município no Norte Goiano
e outro no Leste Goiano. A regra modal a põe no Centro. Passada ao Norte, a fração ENTRE muda
em até 5,2 pontos (soja SIDRA, 78,6% → 83,8%; nas três manchetes, 1–2 pontos) e nenhum *share*
muda mais de 3,7 pontos.

**Blocos espaciais.** Nas três manchetes, o limite inferior do IC95% da fração ENTRE nunca
fica abaixo de 49% (rebanho com k = 12) em nenhum tamanho de bloco.

## O que este pipeline NÃO diz

- **Não diz por que as regiões trocaram de peso.** É contabilidade do deslocamento, não
  mecanismo. O mecanismo é assunto das Pernas 2 a 4.
- **Pouca alavanca não é pouca importância.** O Centro tem 30–33% do rebanho e um puxão de
  só +16 km em 2024 porque fica perto do centro do estado.
- **"Troca de peso" não quer dizer que nenhum hectare se moveu dentro das regiões.** O DENTRO
  é de 15–17 km e robusto sob i.i.d.
- **A zona não é um bioma.** No manuscrito do Barroso as zonas são unidades naturais; aqui são
  recortes escolhidos. Por isso a ancoragem é reportada em três partições, e a fração ENTRE em
  quatro.
- **Só o centro médio se decompõe.** O centro mediano (Weiszfeld) do #32 não é média ponderada
  de centros de zona e fica fora.

## Fontes

O manuscrito ancora as métricas em Stone (1974), Arlot e Celisse (2010) e, para dados
espaciais, Le Rest et al. (2014), Roberts et al. (2017) e Ploton et al. (2020). Nenhuma dessas
obras foi lida aqui. Ficam como lista de leitura e não entram como referência.

## Como rodar

```
python scripts/centro_massa_ancoragem.py                              # completo (segundos)
python scripts/centro_massa_ancoragem.py --sem-bootstrap --sem-figuras # só CSVs pontuais
```

O script para com erro se qualquer conferência falhar (reconstrução ≠ #32, identidade
LOO × influência, decomposição que não fecha, ΔNorte ≠ #32, DENTRO ≠ 0 com 166 AMCs).
