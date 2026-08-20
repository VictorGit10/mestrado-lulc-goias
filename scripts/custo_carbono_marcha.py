"""custo_carbono_marcha.py — Pipeline #47
Custo de carbono da marcha ao norte (eixo ambiental, ponte do #44/#46)
=====================================================================

PERGUNTA QUE RESPONDE
---------------------
A "marcha ao norte" (#32) é uma reorganização da produção — mas ela tem um
CUSTO ambiental que a dissertação de Ciências Ambientais precisa quantificar:
quanto CARBONO a conversão de vegetação nativa emitiu, e ONDE?

O #44 mostrou que a "muralha norte" da vegetação (+8 km, quase parada no #32)
era miragem de média: a FLORESTA nativa ficou presa (mata de galeria, +9 km),
mas o CAMPO nativo (+35 km) e a savana recuaram forte ao norte. Como as três
formações têm densidades de carbono MUITO diferentes (floresta densa >> savana
>> campo), a pergunta ambiental é dupla:

  (1) Quanto carbono comprometido (committed emissions) saiu do recuo de cada
      formação, 1985→2024?
  (2) Esse custo MARCHA ao norte junto com a fronteira (o centróide da PERDA de
      carbono sobe), ou fica ancorado ao sul?

ABORDAGEM (método de diferença de estoque — IPCC Tier 1, formação-resolvida)
---------------------------------------------------------------------------
Emissão comprometida = Σ_f  Δestoque_f (ha perdidos) × densidade_C_f (Mg C/ha),
por AMC × ano, com f ∈ {floresta nativa, formação savânica, campo nativo}.

- Estoque por formação vem do painel AMC (#25/#44): lulc_floresta_nativa_ha,
  lulc_formacao_savanica_ha, lulc_campo_nativo_ha — 166 AMC × 40 anos.
- Densidades (D18): valores de literatura do Cerrado, biomassa AGB+BGB, em três
  cenários (baixa/central/alta) para SENSIBILIDADE. Solo (SOC) entra como camada
  SEPARADA e opcional (mudança de SOC na conversão é lenta/contestada — não vai
  na manchete). Ver DENSIDADES abaixo e o cabeçalho da tabela.
- Espacialização reusa a máquina do #39/#34: amc_para_meso → região (Sul/Centro/
  Norte), faixa de latitude (4 quantis) e latitude do centróide (EPSG:5880→4674).
- CO2e = C × 44/12.

Três produtos:
  A. Balanço por formação (estado): quanto C cada formação custou; a floresta
     perde pouca ÁREA mas é densa — a savana/campo perdem muita área mas são
     ralas. Quem domina a EMISSÃO?
  B. Espacial: emissão por região × ato; e o CENTRÓIDE da perda de carbono por
     ato (marcha ao norte?), análogo ao #32.
  C. Cross-check com as MATRIZES DE TRANSIÇÃO (#12/#19): o fluxo bruto
     veg→antrópico × densidade média ponderada = cota-teto (bruto) vs o líquido
     (diferença de estoque). Bruto ≥ líquido (o líquido desconta rebrota).

CAUTELAS (herdadas do estilo do projeto)
- Diferença de estoque = emissão LÍQUIDA comprometida (desconta rebrota/regen);
  reporto o bruto (transições) ao lado como cota superior. Não é fluxo medido
  de CO2 (sem torre de fluxo) — é estoque removido × fator, padrão inventário.
- Densidade é Tier 1 (literatura, não medida em campo em GO) → sensibilidade
  baixa/central/alta obrigatória; a MANCHETE é robusta ao cenário se o
  ordenamento (quem domina, para onde marcha) não muda.
- "Comprometida" = o carbono deixa de estar estocado; a emissão real se dá ao
  longo de anos (decomposição/queima). Não modelo a dinâmica temporal da
  liberação — só o estoque comprometido no período.
- Centróide é média (D do #32): reporto mediano ao lado; e só sobre PERDAS
  (AMCs que ganharam formação não emitem — entram no líquido estadual, não no
  centróide da perda).

DUAS RÉGUAS DE DENSIDADE (--regua), acrescentado em 2026-08-20
--------------------------------------------------------------
A conta inteira é área medida × densidade de literatura. A densidade era o único
insumo sem localizador de página, e duas das quatro fontes da D18 nunca foram lidas
(Bustamante e Grace, pagas). A régua `mcti` resolve isso na raiz: usa os estoques do
4º Inventário Nacional (MCTI, 2020), que são oficiais, gratuitos, resolvidos por
fitofisionomia, ESPECÍFICOS PARA GOIÁS e publicados nas mesmas classes do MapBiomas
que este painel usa — nenhum passo de tradução.

O que a troca faz (perda 1985→2024, cenário central):

    régua   floresta  savânica   razão   flo Mt   sav Mt    total   quem domina
    d18       95,00     33,00    2,88      500      458      973    floresta
    mcti      64,72     41,32    1,57      340      573      973    savânica

Duas leituras saem daí, e as duas importam:

1. O TOTAL é o mesmo (973 Mt). Uma fonte oficial independente chega ao mesmo número
   por outro caminho — corroboração externa da magnitude.
2. A COMPOSIÇÃO inverte. "A floresta perde 2,6× menos área e ainda assim emite mais"
   exige razão de densidade > 2,64 (a razão de ÁREA perdida savânica/floresta). A D18
   dá 2,88 — 9% de folga —, e os TRÊS cenários dela mantêm a razão em 2,88-3,00, de
   modo que a sensibilidade publicada testa o NÍVEL e não consegue testar a
   composição. Sob a régua oficial a razão é 1,57 e a manchete cai.

O relatório imprime a razão crítica de propósito: é ela, e não as seis densidades,
que sustenta a afirmação de composição.

DENSIDADES DE CARBONO (D18) — Mg C/ha, biomassa aérea+radicular (AGB+BGB)
------------------------------------------------------------------------
Faixas de literatura do Cerrado. Fontes: Bustamante et al. (2012, Climatic
Change 115:559-577); Grace et al. (2006, J. Biogeography 33:387); Ribeiro &
Walter (2008, fisionomias do Cerrado); IPCC (2006 GL, Tier 1 tropical). O
Cerrado tem enorme biomassa RADICULAR (razão raiz:parte-aérea alta), por isso
savana/campo não são desprezíveis. Valores centrais conservadores.

    formação            baixa  central  alta
    floresta nativa      75      95     120
    formação savânica    25      33      40
    campo nativo          8      13      18

SOC (0-30 cm) opcional: ~40 Mg C/ha nas três; a fração liberada na conversão
para pasto/lavoura é pequena e contestada → camada separada (--com-solo).

ENTRADAS
    data/processed/painel_amc_goias.parquet     (#25/#44 — estoque por formação)
    data/processed/amc_crosswalk_goias.csv + mapeamento_mesorregioes.csv +
        amc_goias.gpkg  (via deslocamento_espacial.amc_para_meso — região+lat)
    data/processed/conversao_bruta_goias.csv    (#12/#19 — cross-check bruto)

SAÍDAS
    data/processed/carbono_por_formacao.csv     (estado × formação × cenário)
    data/processed/carbono_regional_ato.csv     (região × ato × formação)
    data/processed/carbono_por_amc.csv          (AMC × formação: perda + lat/reg)
    data/processed/carbono_centroide_ato.csv    (centróide da perda por ato)
    data/processed/carbono_sensibilidade.csv    (baixa/central/alta — manchetes)
    outputs/custo_carbono/*.png                 (3 figuras)

    Com `--regua mcti` os CSVs saem com sufixo `_mcti`. A régua publicada NÃO é
    sobrescrita de propósito: o texto da qualificação cita os arquivos sem sufixo,
    e trocar a régua do texto é decisão editorial, não efeito colateral de rodar
    o pipeline.

COMO RODAR
    py -3.14 scripts/custo_carbono_marcha.py                      # régua d18 (publicada)
    py -3.14 scripts/custo_carbono_marcha.py --regua mcti         # régua oficial (GO)
    py -3.14 scripts/custo_carbono_marcha.py --com-solo --sem-figuras

Depende de: #44 (formações abertas), #32/#34/#39 (máquina de região/centróide),
#12/#19 (transições). Quando foi feito: 2026-07-16.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deslocamento_espacial import amc_para_meso, MESO_SUL, MESO_NORTE  # noqa: E402
from config_periodos import ATOS  # noqa: E402


def regiao_de_meso(m) -> str:
    """Sul / Norte / Centro a partir da mesorregião (mesma regra do #34/#39)."""
    if m in MESO_SUL:
        return "Sul"
    if m in MESO_NORTE:
        return "Norte"
    return "Centro"

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "custo_carbono"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_PAINEL = DIR_PROC / "painel_amc_goias.parquet"
ARQ_TRANS  = DIR_PROC / "conversao_bruta_goias.csv"

CRS_METRICO, CRS_GEO = 5880, 4674
ANO_INI, ANO_FIM = 1985, 2024
C_PARA_CO2 = 44.0 / 12.0

# Formação -> (coluna no painel, rótulo, cor). A chave é a classe do MapBiomas:
# floresta=3, savanica=4, campo=12 (Formação Campestre), alagado=11 (Campo Alagado
# e Área Pantanoso). O alagado entrou com a régua `mcti`; sob a `d18` ele vale zero,
# que é o que a versão publicada fazia — só que sem dizer.
FORMACOES = {
    "floresta": ("lulc_floresta_nativa_ha",   "Formação florestal (galeria/cerradão)", "#1b5e20"),
    "savanica": ("lulc_formacao_savanica_ha", "Formação savânica (Cerrado s.s.)",      "#66bb6a"),
    "campo":    ("lulc_campo_nativo_ha",      "Formação campestre",                    "#c5e1a5"),
    "alagado":  ("lulc_campo_alagado_ha",     "Campo alagado e área pantanosa",        "#4dd0e1"),
}

# ---------------------------------------------------------------------------
# DUAS RÉGUAS DE DENSIDADE. Ver o cabeçalho para o que a troca muda.
# ---------------------------------------------------------------------------
# `d18` — a régua publicada. Faixas de literatura do Cerrado, biomassa AGB+BGB,
#   com três cenários de sensibilidade. Fontes: Bustamante et al. (2012), Grace
#   et al. (2006), IPCC (2006), Ribeiro & Walter (2008).
#   ⚠️ Bustamante e Grace NÃO foram lidas (pagas); só metadados do Crossref. Os
#   valores não têm localizador de página. É por isso que a régua `mcti` existe.
#
# `mcti` — 4º Inventário Nacional (MCTI, 2020), Relatório de Referência do setor
#   LULUCF, Tabela 24 (p. 121-127) para as fitofisionomias do Cerrado e Tabela 76
#   (p. 246) para as florestais; agregação nas classes do MapBiomas por média
#   ponderada de área conforme a Nota Metodológica do SEEG (Tabela 2, p. 20-32;
#   Tabela 3, p. 33). O estoque de floresta do Cerrado é POR ESTADO: GO = 64,72.
#   Escopo: aéreo + subterrâneo + madeira morta + serapilheira, SEM solo — dois
#   compartimentos a mais que a d18, ainda abaixo do estoque total.
#   Sem cenário: o Inventário publica valor pontual para o Cerrado, e a Tabela 85
#   (p. 269) trata a incerteza de forma QUALITATIVA. Não se inventa faixa aqui;
#   os três cenários repetem o valor central de propósito.
_MCTI = {"floresta": 64.72, "savanica": 41.32, "campo": 24.94, "alagado": 36.21}

DENSIDADES_POR_REGUA = {  # régua: {formação: {cenário: Mg C/ha}}
    "d18": {
        "floresta": {"baixa": 75.0, "central": 95.0, "alta": 120.0},
        "savanica": {"baixa": 25.0, "central": 33.0, "alta": 40.0},
        "campo":    {"baixa": 8.0,  "central": 13.0, "alta": 18.0},
        "alagado":  {"baixa": 0.0,  "central": 0.0,  "alta": 0.0},
    },
    "mcti": {k: {c: v for c in ("baixa", "central", "alta")} for k, v in _MCTI.items()},
}

# Estoque do uso que ENTRA (Cerrado, 4º Inventário via SEEG, Tabela 5 p. 36).
# Não entra na manchete: a conta publicada é de estoque removido, e passar a
# descontar o uso de destino é mudança de método, não de parâmetro. Fica aqui
# para dimensionar o viés, que o relatório imprime.
ESTOQUE_DESTINO_CERRADO = {"pastagem": 7.57, "agricultura_anual": 5.00}

# Régua ativa. `main()` a define; o default preserva o comportamento publicado.
REGUA = "d18"


def DENS(formacao: str, cenario: str = "central") -> float:
    """Densidade da formação sob a régua ativa."""
    return DENSIDADES_POR_REGUA[REGUA][formacao][cenario]


# Compatibilidade: código antigo que lia DENSIDADES[f][c] continua funcionando,
# mas passa a enxergar a régua ativa.
class _DensProxy(dict):
    def __getitem__(self, formacao):
        return DENSIDADES_POR_REGUA[REGUA][formacao]

    def __iter__(self):
        return iter(DENSIDADES_POR_REGUA[REGUA])


DENSIDADES = _DensProxy()
# SOC 0-30 cm (Mg C/ha) e fração liberada na conversão (camada opcional).
SOC_MGC_HA = 40.0
SOC_FRACAO_LIBERADA = 0.25  # conservador; literatura 0-0,4 p/ pasto/lavoura

CORES_REGIAO = {"Sul": "#c2185b", "Centro": "#8d6e63", "Norte": "#2e7d32"}


# ---------------------------------------------------------------------------
# 1. Carga: painel + região + latitude do centróide (reuso #39)
# ---------------------------------------------------------------------------

def carregar() -> pd.DataFrame:
    pan = pd.read_parquet(ARQ_PAINEL)
    pan = pan[pan["ano"].between(ANO_INI, ANO_FIM)].copy()

    reg = amc_para_meso()  # code_amc, nm_meso, cx, cy (EPSG:5880)
    reg["regiao"] = reg["nm_meso"].map(regiao_de_meso)

    import geopandas as gpd
    pts = gpd.GeoSeries(gpd.points_from_xy(reg["cx"], reg["cy"]),
                        crs=CRS_METRICO).to_crs(CRS_GEO)
    reg["lat"] = pts.y.to_numpy()
    reg["faixa_lat"] = pd.qcut(reg["lat"], 4,
                               labels=["F1 (sul)", "F2", "F3", "F4 (norte)"])

    pan = pan.merge(reg[["code_amc", "nm_meso", "regiao", "cx", "cy", "lat", "faixa_lat"]],
                    on="code_amc", how="left")
    print(f"[carga] painel {pan.shape[0]:,} linhas | {pan['code_amc'].nunique()} AMCs × "
          f"{pan['ano'].nunique()} anos | regiões: {reg['regiao'].value_counts().to_dict()}")
    return pan


# ---------------------------------------------------------------------------
# 2. Perda de estoque por AMC × formação (líquida, entre limites de período)
# ---------------------------------------------------------------------------

def perda_estoque(pan: pd.DataFrame, ano_a: int, ano_b: int) -> pd.DataFrame:
    """ha de cada formação perdidos (>0) ou ganhos (<0) por AMC entre ano_a→ano_b."""
    meta = ["code_amc", "regiao", "nm_meso", "cx", "cy", "lat", "faixa_lat"]
    a = pan[pan.ano == ano_a].set_index("code_amc")
    b = pan[pan.ano == ano_b].set_index("code_amc")
    out = pan[pan.ano == ano_b].set_index("code_amc")[meta[1:]].copy()
    for chave, (col, _r, _c) in FORMACOES.items():
        out[f"perda_ha_{chave}"] = (a[col] - b[col]).reindex(out.index)  # >0 = perdeu
    return out.reset_index()


def emissao(perda: pd.DataFrame, cenario: str, com_solo: bool) -> pd.DataFrame:
    """Converte ha perdidos em Mg C comprometido por AMC (cenário de densidade)."""
    df = perda.copy()
    tot = np.zeros(len(df))
    for chave in FORMACOES:
        d = DENSIDADES[chave][cenario]
        c = df[f"perda_ha_{chave}"] * d  # Mg C (líquido; negativo = sequestro)
        if com_solo:
            c = c + df[f"perda_ha_{chave}"] * SOC_MGC_HA * SOC_FRACAO_LIBERADA
        df[f"MgC_{chave}"] = c
        tot = tot + c.fillna(0).to_numpy()
    df["MgC_total"] = tot
    df["MtCO2_total"] = df["MgC_total"] * C_PARA_CO2 / 1e6
    return df


# ---------------------------------------------------------------------------
# 3. Bloco A — balanço estadual por formação (quem domina a emissão)
# ---------------------------------------------------------------------------

def balanco_formacao(perda_total: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for chave, (_col, rot, _c) in FORMACOES.items():
        ha = perda_total[f"perda_ha_{chave}"].sum()
        row = {"formacao": rot, "area_perdida_Mha": ha / 1e6}
        for cen in ("baixa", "central", "alta"):
            row[f"MtC_{cen}"] = ha * DENSIDADES[chave][cen] / 1e6
            row[f"MtCO2_{cen}"] = ha * DENSIDADES[chave][cen] * C_PARA_CO2 / 1e6
        linhas.append(row)
    out = pd.DataFrame(linhas)
    tot = out.select_dtypes("number").sum()
    tot["formacao"] = "TOTAL"
    out = pd.concat([out, pd.DataFrame([tot])], ignore_index=True)
    return out


# ---------------------------------------------------------------------------
# 4. Bloco B — espacial: região × ato + centróide da perda por ato
# ---------------------------------------------------------------------------

def por_regiao_ato(pan: pd.DataFrame, com_solo: bool) -> pd.DataFrame:
    linhas = []
    for ato, info in ATOS.items():
        pr = perda_estoque(pan, info["inicio"], info["fim"])
        em = emissao(pr, "central", com_solo)
        dur = info["fim"] - info["inicio"]
        for reg, g in em.groupby("regiao"):
            for chave, (_c, rot, _cor) in FORMACOES.items():
                mgc = g[f"MgC_{chave}"].sum()
                linhas.append({
                    "ato": ato, "periodo": f"{info['inicio']}-{info['fim']}",
                    "regiao": reg, "formacao": rot,
                    "MtC": mgc / 1e6, "MtCO2": mgc * C_PARA_CO2 / 1e6,
                    "MtCO2_por_ano": mgc * C_PARA_CO2 / 1e6 / dur,
                })
    return pd.DataFrame(linhas)


def centroide_perda(pan: pd.DataFrame, com_solo: bool) -> pd.DataFrame:
    """Centróide (latitude) da PERDA de carbono por ato — a 'marcha' do custo."""
    import geopandas as gpd
    linhas = []
    for ato, info in ATOS.items():
        pr = perda_estoque(pan, info["inicio"], info["fim"])
        em = emissao(pr, "central", com_solo)
        w = em["MgC_total"].clip(lower=0).to_numpy()  # só perdas ponderam
        m = w > 0
        if m.sum() < 3:
            continue
        x, y = em.loc[m, "cx"].to_numpy(), em.loc[m, "cy"].to_numpy()
        ww = w[m]
        xm, ym = np.average(x, weights=ww), np.average(y, weights=ww)
        # mediano ponderado (robusto ao cluster) via Weiszfeld leve
        xd, yd = _weiszfeld(x, y, ww)
        pt = gpd.GeoSeries(gpd.points_from_xy([xm, xd], [ym, yd]),
                           crs=CRS_METRICO).to_crs(CRS_GEO)
        linhas.append({"ato": ato, "periodo": f"{info['inicio']}-{info['fim']}",
                       "lat_mean": pt.y[0], "lat_med": pt.y[1],
                       "MtCO2_perda": ww.sum() * C_PARA_CO2 / 1e6,
                       "n_amc_perda": int(m.sum())})
    return pd.DataFrame(linhas)


def _weiszfeld(x, y, w, iters=64, eps=1e-6):
    cx, cy = np.average(x, weights=w), np.average(y, weights=w)
    for _ in range(iters):
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) + eps
        wd = w / d
        nx, ny = np.sum(wd * x) / np.sum(wd), np.sum(wd * y) / np.sum(wd)
        if abs(nx - cx) < eps and abs(ny - cy) < eps:
            break
        cx, cy = nx, ny
    return cx, cy


# ---------------------------------------------------------------------------
# 5. Bloco C — cross-check com transições brutas (#12/#19)
# ---------------------------------------------------------------------------

def cross_check_transicoes(pan: pd.DataFrame, perda_total: pd.DataFrame) -> dict:
    """Fluxo bruto veg→antrópico × densidade média ponderada (cota-teto bruta)."""
    t = pd.read_csv(ARQ_TRANS)
    antro = ["pastagem", "agricultura", "area_urbana"]
    bruto_mha = t[(t.grupo_orig == "vegetacao_natural") &
                  (t.grupo_dest.isin(antro))].area_mha.sum()
    # densidade média ponderada pela COMPOSIÇÃO da perda líquida por formação
    # Só entram as formações que a régua ativa contabiliza. Sob a d18 o campo
    # alagado tem densidade zero, e deixá-lo no denominador diluiria a média —
    # uma formação fora da conta não deve puxar a densidade média para baixo.
    contadas = [k for k in FORMACOES if DENS(k) > 0]
    ha = {k: max(perda_total[f"perda_ha_{k}"].sum(), 0.0) for k in contadas}
    tot_ha = sum(ha.values()) or 1.0
    dens_pond = sum(DENS(k) * ha[k] for k in contadas) / tot_ha
    bruto_MtCO2 = bruto_mha * 1e6 * dens_pond * C_PARA_CO2 / 1e6
    liq_MtCO2 = emissao(perda_total, "central", False)["MgC_total"].clip(lower=0).sum() \
        * C_PARA_CO2 / 1e6
    return {"bruto_veg_antropico_Mha": bruto_mha, "densidade_ponderada_MgCha": dens_pond,
            "bruto_MtCO2": bruto_MtCO2, "liquido_MtCO2": liq_MtCO2,
            "razao_liq_bruto": liq_MtCO2 / bruto_MtCO2 if bruto_MtCO2 else np.nan}


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def _fundo_atos(ax):
    from config_periodos import CORES_ATO
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, info["fim"] + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)


def figuras(balanco: pd.DataFrame, reg_ato: pd.DataFrame, cen: pd.DataFrame,
            pan: pd.DataFrame, com_solo: bool, suf: str = ""):
    """Sufixo no nome do arquivo porque a régua entra na figura e um PNG não é
    grepável nem aparece no diff (regra D27): duas réguas, dois arquivos."""
    import matplotlib.pyplot as plt

    # Fig 1 — quem domina a emissão: área perdida vs carbono (barras pareadas)
    b = balanco[balanco.formacao != "TOTAL"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    cores = [FORMACOES[k][2] for k in FORMACOES]
    a1.bar(range(len(b)), b["area_perdida_Mha"], color=cores)
    a1.set_xticks(range(len(b)))
    a1.set_xticklabels([r.split(" (")[0] for r in b.formacao], rotation=15, ha="right")
    a1.set_ylabel("Área nativa perdida 1985→2024 (Mha)")
    a1.set_title("Quem perde ÁREA", loc="left", fontsize=11)
    a2.bar(range(len(b)), b["MtCO2_central"], color=cores,
           yerr=[(b.MtCO2_central - b.MtCO2_baixa).abs(),
                 (b.MtCO2_alta - b.MtCO2_central).abs()], capsize=4)
    a2.set_xticks(range(len(b)))
    a2.set_xticklabels([r.split(" (")[0] for r in b.formacao], rotation=15, ha="right")
    a2.set_ylabel("Emissão comprometida (Mt CO₂e)")
    a2.set_title("Quem domina o CARBONO (barras = cenário baixa–alta)", loc="left", fontsize=11)
    fig.suptitle("Custo de carbono por formação — Goiás 1985→2024"
                 + (" (com solo)" if com_solo else " (só biomassa)"),
                 fontsize=13, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(DIR_OUT / f"carbono_por_formacao{suf}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / f"carbono_por_formacao{suf}.png").relative_to(ROOT)}")

    # Fig 2 — emissão por região × ato (Mt CO2/ano), empilhado por formação
    fig, ax = plt.subplots(figsize=(11, 6))
    piv = (reg_ato.groupby(["ato", "regiao"])["MtCO2_por_ano"].sum()
           .unstack("regiao").reindex(index=list(ATOS.keys())))
    piv = piv[[c for c in ["Sul", "Centro", "Norte"] if c in piv.columns]]
    x = np.arange(len(piv)); wbar = 0.25
    for i, reg in enumerate(piv.columns):
        ax.bar(x + (i - 1) * wbar, piv[reg], wbar, label=reg,
               color=CORES_REGIAO.get(reg, "0.5"))
    ax.set_xticks(x)
    ax.set_xticklabels([f"Ato {a}\n{ATOS[a]['inicio']}-{ATOS[a]['fim']}" for a in piv.index])
    ax.set_ylabel("Emissão comprometida (Mt CO₂e / ano)")
    ax.set_title("Ritmo de emissão por região e ato — o custo migra ao norte?",
                 loc="left", fontsize=12)
    ax.legend(frameon=True)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / f"carbono_regiao_ato{suf}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / f"carbono_regiao_ato{suf}.png").relative_to(ROOT)}")

    # Fig 3 — centróide da perda de carbono por ato (a marcha do custo)
    if not cen.empty:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.plot(cen["ato"], cen["lat_mean"], "o-", color="#5d1451", lw=2.2,
                label="centro médio da perda de C")
        ax.plot(cen["ato"], cen["lat_med"], "s--", color="#b06fa8", lw=1.6,
                label="centro mediano (robusto)")
        for _, r in cen.iterrows():
            ax.annotate(f"{r['MtCO2_perda']:.0f} Mt", (r["ato"], r["lat_mean"]),
                        textcoords="offset points", xytext=(8, 6), fontsize=9)
        ax.set_ylabel("Latitude do centróide (°, ↑ = norte)")
        ax.set_xlabel("Ato")
        ax.set_title("Marcha ao norte do custo de carbono\n"
                     "centróide da PERDA de C por ato", loc="left", fontsize=12)
        ax.legend(frameon=True)
        ax.grid(True, alpha=0.25)
        fig.tight_layout()
        fig.savefig(DIR_OUT / f"carbono_centroide_marcha{suf}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)
        print(f"[fig] {(DIR_OUT / f"carbono_centroide_marcha{suf}.png").relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #47 — custo de carbono da marcha ao norte")
    ap.add_argument("--com-solo", action="store_true",
                    help="inclui SOC (0-30cm) × fração liberada — camada opcional")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--regua", choices=("d18", "mcti"), default="d18",
                    help="régua de densidade (ver cabeçalho). d18 = publicada; "
                         "mcti = 4o Inventario Nacional, especifica p/ Goias")
    ap.add_argument("--sufixo", default="",
                    help="sufixo dos CSVs de saida; evita sobrescrever a regua publicada")
    args = ap.parse_args()

    global REGUA
    REGUA = args.regua
    suf = args.sufixo or ("" if args.regua == "d18" else f"_{args.regua}")

    print("=" * 70)
    print("Pipeline #47 — Custo de carbono da marcha ao norte")
    print("=" * 70)
    if args.com_solo:
        print(f"[modo] biomassa + solo (SOC {SOC_MGC_HA} × {SOC_FRACAO_LIBERADA} liberado)")
    else:
        print("[modo] só biomassa — manchete")

    print(f"[régua] densidades: {args.regua.upper()}  "
          f"({', '.join(f'{k}={DENS(k):.2f}' for k in FORMACOES)})")

    pan = carregar()

    # --- Perda total 1985→2024 e balanço por formação ---
    perda_tot = perda_estoque(pan, ANO_INI, ANO_FIM)
    bal = balanco_formacao(perda_tot)
    bal.to_csv(DIR_PROC / f"carbono_por_formacao{suf}.csv", index=False, encoding="utf-8")
    print("\n[A] Balanço estadual por formação (1985→2024):")
    print("-" * 70)
    for _, r in bal.iterrows():
        if r["formacao"] == "TOTAL":
            print("-" * 70)
        print(f"  {r['formacao']:<38} {r['area_perdida_Mha']:>6.2f} Mha  →  "
              f"{r['MtCO2_central']:>7.1f} Mt CO₂e "
              f"[{r['MtCO2_baixa']:.0f}–{r['MtCO2_alta']:.0f}]")

    # Quem domina
    b = bal[bal.formacao != "TOTAL"].copy()
    dom_area = b.loc[b.area_perdida_Mha.idxmax(), "formacao"].split(" (")[0]
    dom_carb = b.loc[b.MtCO2_central.idxmax(), "formacao"].split(" (")[0]
    tot_co2 = bal.loc[bal.formacao == "TOTAL", "MtCO2_central"].iloc[0]
    print(f"\n  → maior perda de ÁREA: {dom_area};  maior emissão de CARBONO: {dom_carb}")
    print(f"  → TOTAL comprometido (biomassa, central): {tot_co2:.0f} Mt CO₂e "
          f"({tot_co2/(ANO_FIM-ANO_INI):.1f} Mt/ano médio)")

    # --- A razão crítica: o número de que a afirmação de composição depende ---
    # "A floresta perde menos área e ainda assim emite mais" NÃO é uma afirmação
    # sobre seis densidades; é sobre UMA razão. Ela vale se, e só se,
    #     densidade_floresta / densidade_savânica  >  área_savânica / área_floresta.
    # Os três cenários da d18 movem o nível e quase não movem a razão, e por isso
    # não conseguem testar a composição. Este bloco imprime o teste que falta.
    ha_flo = perda_tot["perda_ha_floresta"].sum()
    ha_sav = perda_tot["perda_ha_savanica"].sum()
    r_area = ha_sav / ha_flo
    print(f"\n  → razão crítica: a composição só se sustenta se "
          f"dens(floresta)/dens(savânica) > {r_area:.2f} (= razão de ÁREA perdida)")
    for cenario in ("baixa", "central", "alta"):
        r_dens = DENS("floresta", cenario) / DENS("savanica", cenario)
        veredito = "floresta domina" if r_dens > r_area else "SAVÂNICA domina"
        folga = 100 * (r_dens / r_area - 1)
        print(f"     {cenario:<8} razão {r_dens:5.2f}  ({folga:+5.1f}% de folga)  → {veredito}")
    dens_sav_empate = DENS("floresta") / r_area
    print(f"     empate no central com savânica = {dens_sav_empate:.2f} Mg C/ha "
          f"(hoje {DENS('savanica'):.2f})")

    # --- Sensibilidade (manchetes por cenário) ---
    sens = []
    for cen in ("baixa", "central", "alta"):
        em = emissao(perda_tot, cen, args.com_solo)
        sens.append({"cenario": cen,
                     "MtCO2_total": em["MgC_total"].sum() * C_PARA_CO2 / 1e6,
                     "MtCO2_perda_bruta": em["MgC_total"].clip(lower=0).sum() * C_PARA_CO2 / 1e6})
    sens = pd.DataFrame(sens)
    sens.to_csv(DIR_PROC / f"carbono_sensibilidade{suf}.csv", index=False, encoding="utf-8")

    # --- Bloco B: região × ato + centróide ---
    reg_ato = por_regiao_ato(pan, args.com_solo)
    reg_ato.to_csv(DIR_PROC / f"carbono_regional_ato{suf}.csv", index=False, encoding="utf-8")
    em_tot = emissao(perda_tot, "central", args.com_solo)
    em_tot[["code_amc", "regiao", "nm_meso", "lat", "faixa_lat"]
           + [f"perda_ha_{k}" for k in FORMACOES]
           + [f"MgC_{k}" for k in FORMACOES] + ["MgC_total", "MtCO2_total"]] \
        .to_csv(DIR_PROC / f"carbono_por_amc{suf}.csv", index=False, encoding="utf-8")

    print("\n[B] Emissão por região (total 1985→2024, Mt CO₂e, cenário central):")
    reg_sum = (reg_ato.groupby("regiao")["MtCO2"].sum()
               .reindex(["Sul", "Centro", "Norte"]))
    for reg, v in reg_sum.items():
        print(f"   {reg:<8} {v:>7.1f} Mt CO₂e  ({100*v/reg_sum.sum():>4.1f}%)")

    cen = centroide_perda(pan, args.com_solo)
    cen.to_csv(DIR_PROC / f"carbono_centroide_ato{suf}.csv", index=False, encoding="utf-8")
    if not cen.empty:
        print("\n[B] Centróide da PERDA de carbono por ato (marcha ao norte):")
        for _, r in cen.iterrows():
            print(f"   Ato {r['ato']} ({r['periodo']}): lat {r['lat_mean']:+.2f} "
                  f"(med {r['lat_med']:+.2f}) | {r['MtCO2_perda']:.0f} Mt CO₂e")
        dn = (cen["lat_mean"].iloc[-1] - cen["lat_mean"].iloc[0]) * 111
        print(f"   → deslocamento do custo de C: {dn:+.0f} km "
              f"({'NORTE' if dn > 0 else 'SUL'}) de Ato I a III")

    # --- Bloco C: cross-check bruto vs líquido ---
    cc = cross_check_transicoes(pan, perda_tot)
    print("\n[C] Cross-check com transições brutas (#12/#19):")
    print(f"   fluxo bruto veg→antrópico: {cc['bruto_veg_antropico_Mha']:.2f} Mha "
          f"(soma ano-a-ano; densidade pond. {cc['densidade_ponderada_MgCha']:.0f} Mg C/ha)")
    print(f"   bruto ≈ {cc['bruto_MtCO2']:.0f} Mt CO₂e (cota-teto)  |  "
          f"líquido (estoque) ≈ {cc['liquido_MtCO2']:.0f} Mt CO₂e  |  "
          f"razão líq/bruto = {cc['razao_liq_bruto']:.2f}")

    if not args.sem_figuras:
        print()
        figuras(bal, reg_ato, cen, pan, args.com_solo, suf)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #47 (custo de carbono; eixo ambiental).")
    print("=" * 70)


if __name__ == "__main__":
    main()
