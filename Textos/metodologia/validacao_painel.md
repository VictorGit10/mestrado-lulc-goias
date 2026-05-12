# Validação do Painel Unificado (Pipeline #16)

Framework para responder à pergunta: *"a soma dos 246 valores municipais do painel reconstrói o agregado de Goiás publicado pelas fontes originais? Onde houver diferença, ela é esperada ou anômala?"*

**Script**: `scripts/validar_painel_unificado.py`
**Notebook**: `notebooks/validacao_painel.ipynb`
**Saídas**: `outputs/diagnosticos/validacao_painel.csv`, `outputs/diagnosticos/validacao_painel_resumo.csv`

## Sim, é legítimo somar

Reconstruir o agregado UF a partir do painel municipal é o teste de consistência padrão para painéis hierárquicos. O framework checa exatamente isso, em quatro camadas independentes (ver `pipelines/16_painel_unificado.md` para o contexto do painel).

## Arquitetura em camadas

1. **Integridade interna** — sem fonte externa: shape exato (9.840 = 246×40), PK `(cd_mun, ano)` única, identidades aritméticas (soja ≤ agricultura), ausência de `±inf` nos derivados.
2. **Gabaritos internos** (`data/processed/*goias*.csv`) — LULC, bovinos, PIB, SICOR e fogo já têm séries UF consolidadas no projeto. O painel soma e bate.
3. **SIDRA UF (N3)** — PAM 1612/839 (soja, cana, feijão, algodão, milho total + safras), PPM 3939 (bovinos, suínos, galináceos) e População 6579 são baixadas via `sidrapy` em nível UF=52 e comparadas. Cache em `data/cache/validacao_uf/`.
4. **Validação cruzada entre fontes** — mesma quantidade por dois caminhos. Implementado para soja MapBiomas (`lulc_soja_ha`) × soja PAM (`agri_soja_ha_plantada`).

## Regras de tolerância e flag

Cada linha `(bloco, variável, ano)` recebe um flag conforme `|diff_rel|` e o ano:

| Padrão | Tolerância | Acima → flag |
|---|---|---|
| LULC (estoque, área) | 0,5 % | `ANOMALA` |
| Bovinos (gabarito interno) | 0,1 % | `ANOMALA` pós-1989; `ESPERADA_TOCANTINS` pré-1989 |
| PAM/PPM vs SIDRA UF | 0,5 % | `ANOMALA` pós-1989; `ESPERADA_TOCANTINS` pré-1989 |
| PIB UF | 1 % | `ANOMALA` (testa o `×1000` de Mil R$ → R$ e a deflação) |
| SICOR UF (deflacionado) | 0,1 % | `ANOMALA` |
| Fogo (gabarito interno) | 2 % | `ANOMALA` |
| População SIDRA UF | 0,1 % | `ANOMALA` exceto 2007/2010 → `ESPERADA_CENSO` |

Flags possíveis:

- **`OK`** — divergência dentro da tolerância.
- **`ESPERADA_TOCANTINS`** — `|diff_rel|` ultrapassa tolerância mas ano < 1989. Causa: SIDRA/IBGE reportam UF=52 com fronteira histórica de GO (incluindo TO até 1988); o painel cobre só os 246 munis de GO atual. Referência: `pipelines/16_painel_unificado.md` §9.
- **`ESPERADA_CENSO`** — população em 2007 (Contagem) e 2010 (Censo): IBGE não publica estimativa intercensitária nesses anos, então o painel tem NaN nos 246 munis. Referência: `pipelines/16_painel_unificado.md`.
- **`CRUZADA_INFORMATIVA`** — comparação entre duas fontes independentes da mesma quantidade. Não é erro nem do painel nem da fonte: razão MapBiomas/PAM varia conforme cobertura raster e taxa de declaração. Referência: `glossario_metricas.md` (raster vs autodeclarado).
- **`CRUZADA_DIVERGENTE`** — cruzada com razão fora de [0,5; 1,5]. Reserva-se para flag visual; não é erro.
- **`SEM_GABARITO`** — variável sem cobertura no agregado externo nesse ano. Ex.: `agri_soja_ha_plantada` em 1985 (SIDRA começou em 1990 para essa categoria UF).
- **`ANOMALA`** — fora da tolerância sem categoria de divergência esperada. **Requer investigação manual.**

## Como rodar

```bash
python scripts/validar_painel_unificado.py
```

Tempo: ~5 min na primeira rodada (downloads SIDRA UF); ~5 s nas seguintes (cache). Exit code 0 se zero `ANOMALA`; 1 caso contrário — pronto para CI.

Para inspeção visual:

```bash
jupyter notebook notebooks/validacao_painel.ipynb
```

## Estado atual da validação (referência)

Última execução em `painel_unificado.parquet` (9.840 × 157):

```
OK                     1699   (95,6 %)
ESPERADA_TOCANTINS       36   (2,0 %)
CRUZADA_INFORMATIVA      25   (1,4 %)
SEM_GABARITO             17   (1,0 %)
ANOMALA                   0
```

Detalhes notáveis:

- Bovinos (`pec_bovinos_cab`) pré-1989: `diff_rel` de −18 a −20 % contra `rebanho_bovino_goias.csv` e contra SIDRA 3939 UF=52. Causa Tocantins; flag automático.
- Soja PAM (`agri_soja_ha_plantada`) em 1988: −3,4 % vs SIDRA UF — ainda na faixa Tocantins (TO instalado em 1989).
- PIB (`pib_real_rs`) em 2002: diff = 6,9 mil R$ em base de 134 bi R$ (`diff_rel` = 5e-8). Pré-2002 o painel não tem PIB → todos os anos viram `SEM_GABARITO`.
- Soja MapBiomas vs PAM: razão cai de 1,43 (2000) para ~1,05 (2024) — convergência conforme PAM melhora cobertura municipal.

## O que ESTA validação NÃO cobre

- **Censo Agro 2017** — replicado como atributo estático no painel; comparação trivial contra o CSV bruto. Fora de escopo (escolha do usuário no plano).
- **IDH-M** — IPEA Data API é a fonte única; sem agregação a validar.
- **Lavouras de pouca expressão** (frutas em PAM 1613, sorgo, trigo, etc.) — incluí-las explodiria o CSV de validação sem ganho informativo. Para auditar uma cultura específica, adicionar entrada em `culturas_1612` na função `validar_agri_pam`.
- **Composição etária bovina** (UA) — o fator `0,7` é constante estado-estacionário; não há gabarito municipal anual.
- **Granularidade municipal** — esta validação opera no agregado UF. Anomalias em municípios individuais (ex.: cd_mun com PIB zerado) ficam a cargo do diagnóstico de cobertura `outputs/diagnosticos/painel_unificado_cobertura.csv`.

## Quando re-rodar

- Sempre que `scripts/construir_painel_unificado.py` for re-executado.
- Quando uma fonte externa atualizar (IBGE publica PIB 2024, BACEN fecha SICOR 2025).
- Antes de submeter texto da dissertação que cita valores agregados — confirma que o gabarito não mudou desde a leitura.

Para forçar refresh dos downloads SIDRA UF: `rm -r data/cache/validacao_uf/`.
