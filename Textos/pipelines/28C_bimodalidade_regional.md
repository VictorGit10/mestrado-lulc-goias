# Pipeline #28C — A bimodalidade é regionalmente causada? (decomposição within/between)

**Script**: `scripts/bimodalidade_regional.py`
**Status**: ✅ Concluído (2026-06-08)
**Outputs**: 4 CSVs (`idade_bimodalidade_por_grupo.csv`, `idade_bimodalidade_decomposicao.csv` + variantes `_amc`) + 2 PNGs em `outputs/idade_pastagem/` (`bimodalidade_unidade_ato.png`, `bimodalidade_unidade_ato_amc.png`).
**Depende de**: #28A (`pastagem_idade_conversao.csv`) e **reusa o GMM do #28** (`analise_reserva_terra.ajustar_gmm_unidim`); #25 (`amc_crosswalk_goias.csv`) na malha AMC.

## Pergunta de pesquisa

O #28 mostrou que a idade da pastagem na conversão é **bimodal** (picos em ~5 e ~22 anos)
e o #28/#40 mostraram um **gradiente regional** (Sul converte pasto jovem, Norte pasto
antigo). Daí a pergunta de precisão que faltava fechar:

> A bimodalidade é **regionalmente causada**? Ou seja, ela é uma **composição** entre
> regiões internamente unimodais (Sul = só jovem, Norte = só velho), ou uma
> **coexistência** dos dois mecanismos **dentro de cada região**, apenas com peso de
> mistura diferente?

A distinção é decisiva para a redação (ecoa **D14**): "regionalmente causada" exigiria que
cada região fosse internamente unimodal e que a bimodalidade do agregado viesse *só* da
mistura de regiões. Se cada região é, ela mesma, bimodal, então a geografia **modula o
peso** — não **cria** os modos.

**Confundidor explícito: o tempo.** O Ato I converte pasto jovem (mediana 6a) e o Ato II/III
convertem pasto velho (~19a). Logo, parte da "bimodalidade" agregada é **temporal**, não
regional. Por isso a **célula região×ato** é o teste decisivo: dentro de uma única região
*e* um único ato, ainda há dois modos?

## Método

Reusa o `ajustar_gmm_unidim` do #28 (GMM 1c vs 2c, AIC/BIC) — método idêntico ao da manchete
do #28 — e adiciona quatro instrumentos:

- **Decomposição de variância (η²)** da idade não-censurada por **espaço**, **ato** e
  **espaço×ato** — quanto cada eixo "explica" da variância.
- **GMM 1c vs 2c por unidade espacial e por célula espaço×ato** (Ato II e III): cada unidade,
  isoladamente, continua bimodal? Critério de bimodalidade (todos precisam valer): ΔBIC =
  bic₁c − bic₂c > 10, separação entre modos > 5 anos, peso do componente menor > 0,15.
- **Coeficiente de bimodalidade de Sarle (BC)** — corroboração **model-free** do GMM
  (BC > 5/9 ≈ 0,555 sugere bimodalidade).
- **η² da pertinência ao modo "velho"** (responsabilidade posterior de **um GMM global**,
  rótulos consistentes para evitar label-switching) por espaço/ato/célula → isola a parcela
  **between** vs **within** da *separação jovem/velho* especificamente (não só da variância).

### Duas blindagens contra a inflação de nº de grupos (essenciais para a malha AMC)

η² **infla mecanicamente** com mais grupos (166 AMCs "explicam" mais variância que 5
mesorregiões só por terem mais graus de liberdade, mesmo no acaso). Para comparar as malhas
de forma honesta:

- **ω² (omega-quadrado)** — effect-size de variância explicada **corrigido para k grupos**
  (pode ficar negativo se o agrupamento não explica nada além do acaso).
- **Linha-base de permutação** (B=200): embaralha os rótulos espaciais (preserva tamanhos de
  grupo e a distribuição do valor) e recalcula η² → o **η² esperado sob o acaso** para aquele
  número/tamanho de grupos. O sinal real é `η²_obs − η²_acaso` (e um p-valor de permutação).

Rodado em **duas malhas**: mesorregião (`--malha meso`, 5 unidades, D6) e AMC
(`--malha amc`, 158 com conversão, via crosswalk do #25). 11.035 pixels não-censurados.

## Achados

### 1. Cada unidade espacial é bimodal POR DENTRO

Não há nenhuma região/AMC unimodal que a mistura "junte":

| Malha | Unidades internamente bimodais (n≥100) | Células espaço×ato bimodais | BC de Sarle |
|---|---|---|---|
| **Mesorregião (5)** | **5/5** | **10/10** | 0,60–0,70 (todas > 0,555) |
| **AMC (158)** | **34/36** | 14/20 | maioria > 0,555 |

As 5 mesorregiões têm ΔBIC de 274 a 3.906; mesmo isolando o tempo (célula região×ato), os
dois modos (~5a e ~20a) aparecem em **todos** os painéis. Na malha AMC, 34 das 36 AMCs com
n≥100 seguem bimodais — as 2 exceções são as **pontas do gradiente** (AMCs quase puro-jovem
ou puro-velho), exatamente o que "gradiente contínuo no peso" prevê.

### 2. A geografia explica MUITO POUCO da separação jovem/velho

Decomposição da pertinência ao modo "velho" (η² / ω² / líquido de acaso):

| Eixo | Mesorregião (5) | AMC (158) |
|---|---|---|
| **Espacial** η² | 2,5% | 8,7% |
| **Espacial** ω² (corrigido) | 2,4% | 7,4% |
| **Espacial** líquido de acaso (perm.) | 2,4% (acaso ~0%) | **7,3%** (acaso 1,4%, p=0,005) |
| **Ato (tempo)** η² | **20,2%** | **20,2%** |
| **DENTRO das células** espaço×ato (1−ω²) | **77%** | **73%** |

(Para a variância da *idade* bruta: espacial η² = 4,0% (meso) / 12,1% (AMC); within-célula
≈ 81% / 74%.)

### 3. O recorte fino capta MAIS — mas pouco, e ainda minoria

Indo da mesorregião para a AMC, a parcela espacial sobe de **2,5% → 7,3%** (líquido de
acaso), ~3×. E a permutação prova que esse ganho é **real, não inflação mecânica**: com 158
grupos o acaso entregaria só 1,4%, e o observado (8,7%) tem **p=0,005**. Ou seja, a
mesorregião era um pouco grossa — geografia fina captura sinal genuíno que ela escondia.

**Mas a conclusão não muda**: mesmo no recorte fino, (a) o espaço explica ~7% da separação
jovem/velho, **menos que o tempo (20%)**; (b) **73%** mora *dentro* das células; e (c)
**34/36** AMCs grandes seguem bimodais por dentro.

### Veredito

> A bimodalidade **NÃO é regionalmente causada**, nem na mesorregião nem na AMC. Os dois
> mecanismos **coexistem em praticamente toda unidade**; a geografia **modula o peso** da
> mistura ao longo de um gradiente Sul→Norte — um pouco mais nitidamente em resolução fina —
> mas **não cria os modos**. O que mais desloca o peso é o **tempo** (o pulso jovem recente
> do Ato III, coerente com o *onset* da soja direta do #41), não a latitude.

## Conexão com a narrativa

- **Fecha a pergunta de precisão deixada por #28/#40.** O #40 entregou a *geografia* das duas
  lógicas (Rotação no Sul × Oportunístico no Norte); o #28C mede **quanto** dessa geografia é
  composição (between) vs coexistência (within) — e responde: coexistência domina (~73–77%).
- **Reforça e quantifica a D14.** O #40 mostrou que a latitude é confundidor de 1ª ordem em
  cross-section; o #28C mostra que, mesmo *sendo* o eixo organizador do peso, a geografia
  explica só ~2–7% da separação jovem/velho. A frase correta passa a ser **"gradiente
  regional no peso da mistura"**, nunca "bimodalidade causada pela região".
- **Responde a uma limitação do Encerramento** ("o recorte mesorregional (5 unidades) é
  grosso"): replicado na malha AMC, com ω² + permutação contra a inflação — a conclusão é
  robusta às duas malhas.

## Limitações honestas

1. **Observacional.** η²(espacial) baixo prova que a geografia não **gera** os modos; não
   prova que "região não importa para nada" — ela move o peso, e esse gradiente é real
   (líquido de acaso, p=0,005 na AMC).
2. **"Espacial" é um proxy de um pacote** (aptidão de solo, chuva, preço da terra,
   infraestrutura, distância a esmagadoras) — a decomposição diz *quanto* o espaço capta, não
   *qual* fator dentro dele.
3. **Censura à esquerda** herdada do #28 (idades truncadas quando o pasto já existia em 1985);
   por isso só os **não-censurados** entram (11.035 px). A bimodalidade é do regime recente.
4. **GMM e BC concordam, mas n pequeno** em algumas células AMC×ato (por isso o filtro n≥100
   para o GMM por unidade; células abaixo disso não são classificadas).

## Como rodar

```bash
python scripts/bimodalidade_regional.py                 # malha mesorregião (5)
python scripts/bimodalidade_regional.py --malha amc     # malha AMC (158)
# lê pastagem_idade_conversao.csv (#28A); na malha AMC também amc_crosswalk_goias.csv (#25).
# escreve idade_bimodalidade_{por_grupo,decomposicao}[_amc].csv + 1 PNG por malha.
```
