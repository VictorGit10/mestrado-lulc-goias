"""
Pipeline #39 — A fronteira está fechando? (frontier closure / oferta de Cerrado)
================================================================================

PERGUNTA QUE RESPONDE
---------------------
A desaceleração recente da fronteira agropecuária em Goiás (agricultura quase
parada no Ato III, #32/#33) é o **estoque de Cerrado convertível se esgotando**
— a fronteira *fechando* pelo lado da OFERTA — ou só a DEMANDA esfriando
(drive comum câmbio/crédito/commodities, #37/#38)? O sinal de partida é do #32:
tudo marchou ao norte (+65 a +78 km) MENOS a vegetação natural (+8 km, ancorada),
coerente com uma fronteira que recua ao norte à medida que o estoque ao sul se
exaure. Esta é uma REINTERPRETAÇÃO da desaceleração, não mais um cruzamento.

ABORDAGEM (3 blocos)
--------------------
A. Mapear o estoque convertível restante por região e no tempo (descritivo).
B. Testar se a conversão responde à OFERTA restante, além da demanda:
   - hazard = perda anual / estoque do ano anterior (taxa por unidade de estoque);
   - painel 2-way FE (ano FE absorve o choque comum de demanda → o coeficiente do
     estoque/depleção isola o gradiente de oferta cross-AMC; mesma lógica do #38);
   - resíduo controlado por demanda (drivers macro do #37): o estoque adiciona poder?
C. Decompor a desaceleração Ato II→III em efeito-ESTOQUE (oferta) vs efeito-HAZARD
   (demanda/governança) por região: Δ(fluxo) = h̄·Δestoque + estoquē·Δhazard
   (decomposição exata de um produto pelo ponto médio). Veredito honesto e por região.

⚠ NOME QUE ENGANA: as colunas de regressor `lestoque`, `lestoque2` e `ldeplecao`
  NÃO são logaritmos. O `l` é herança de uma versão anterior; hoje elas recebem
  `estoque_prev`, `estoque_prev**2` e `deplecao_prev` em NÍVEL (ver l. 260-262;
  `np.log` não aparece neste arquivo). Quem consumir o CSV pela coluna `regressor`
  precisa rotular como nível — o apêndice da qualificação rotulou como "log" até
  20/ago/2026, e isso mandaria o leitor reconstruir o modelo transformado.
  Os nomes não foram trocados porque a coluna `regressor` é chave de dado e o
  rótulo vive no consumidor; a etiqueta certa está em qualificacao/apendice/.

⚠ DUAS RÉGUAS DE ERRO-PADRÃO (corrigido em 21/ago/2026)
  O bloco B reporta o p agrupado por entidade E o agrupado por entidade+ano em toda
  linha, e não só na que decide. Antes desta data o ajuste amarrava o agrupamento ao
  efeito fixo de ano, de modo que o B3 — o único sem ano FE — saía com a régua frouxa
  sozinha. Ver `_painel_fe`. O veredito do bloco não muda: o que muda é que os p dos
  sinais de demanda do B3 deixam de cruzar 5%, e eles nunca sustentaram afirmação.

D13 — "TERRA CONVERTÍVEL" (decisão metodológica, proxy com teto declarado)
-------------------------------------------------------------------------
Sem CAR/UC/PRODES integrados (coletas pendentes), reportamos 3 definições lado a lado:
  - ampla     = veg. natural 3-classe (floresta nativa + savana + campo nativo),
                consistente com #32/#25 (centro_massa.COLS_VEG_NATURAL);
  - refinada  = formação savânica + campo nativo (PREFERIDA) — as classes de Cerrado
                que de fato alimentam veg→pasto/agric; exclui floresta nativa (mata
                ciliar/APP, tende a ser protegida). Justificada empiricamente abaixo
                (depleção por classe: savana encolhe, floresta ~estável);
  - refinada_rl = refinada menos um piso de Reserva Legal de 20% da área de
                estabelecimentos (Censo 2017) — sensibilidade "legalmente convertível".
LIMITE HONESTO: é um TETO (inclui RL/APP/UC não-subtraídos). PRODES/TerraClass/CAR
refinariam, mas não são necessários para o teste de primeira ordem.

ENTRADAS
    data/processed/painel_amc_goias.parquet   (#25 — classes LULC por AMC×ano)
    data/processed/drivers_macro_anual.csv    (#37 — demanda: REER/preço/crédito)
    data/processed/amc_crosswalk_goias.csv + mapeamento_mesorregioes.csv + amc_goias.gpkg
        (via deslocamento_espacial.amc_para_meso — região + latitude do centroide)

SAÍDAS
    data/processed/fronteira_estoque_convertivel.csv  (AMC×ano: estoque/depleção, 3 defs)
    data/processed/fronteira_regional.csv             (mesorregião/faixa-lat × ano)
    data/processed/fronteira_teste_supply.csv         (painel FE: oferta × demanda)
    data/processed/fronteira_decomposicao.csv         (região×ato: estoque vs hazard)
    outputs/fronteira_fechando/*.png                  (4 figuras)

COMO RODAR
    python scripts/fronteira_fechando.py
    python scripts/fronteira_fechando.py --sem-figuras

Reusa: config_periodos (ATOS), deslocamento_espacial (amc_para_meso, MESO_SUL/NORTE),
padrão PanelOLS 2FE + cluster de drive_comum_amc/correlacoes_painel (D8).
Depende de: #25 (painel/geometria AMC), #37 (drivers macro).
Quando foi feito: 2026-06-07.
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
from config_periodos import ATOS                                   # noqa: E402
from deslocamento_espacial import amc_para_meso, MESO_SUL, MESO_NORTE  # noqa: E402

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "fronteira_fechando"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_PAINEL  = DIR_PROC / "painel_amc_goias.parquet"
ARQ_DRIVERS = DIR_PROC / "drivers_macro_anual.csv"

CRS_METRICO, CRS_GEO = 5880, 4674
ANO_INI, ANO_FIM, ANO_BASE = 1985, 2024, 1985

# Classes naturais no painel AMC (#25)
CL_FLORESTA = "lulc_floresta_nativa_ha"
CL_SAVANA   = "lulc_formacao_savanica_ha"
CL_CAMPO    = "lulc_campo_nativo_ha"
CL_ALAGADO  = "lulc_campo_alagado_ha"

# D13 — definições de "terra convertível"
DEFINICOES = {
    "ampla":    [CL_FLORESTA, CL_SAVANA, CL_CAMPO],   # 3-classe (consistente com #32)
    "refinada": [CL_SAVANA, CL_CAMPO],                # savana + campo (convertível de fato)
}
DEF_PRIMARIA = "refinada"
RL_FLOOR = 0.20   # piso de Reserva Legal (bioma Cerrado) — cenário de sensibilidade

# Demanda (drivers macro exógenos, #37) usada no resíduo controlado e na leitura por ato
DRIVERS = ["cambio_real_efetivo", "preco_recebido_soja_idx", "credito_rural_go_real"]

CORES_REGIAO = {"Sul": "#c2185b", "Centro": "#8d6e63", "Norte": "#2e7d32"}


def _zscore(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and np.isfinite(sd) else s * 0.0


def regiao_de_meso(m) -> str:
    if m in MESO_SUL:
        return "Sul"
    if m in MESO_NORTE:
        return "Norte"
    return "Centro"


# ---------------------------------------------------------------------------
# 1. Carga: painel AMC + região + latitude do centroide
# ---------------------------------------------------------------------------

def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    pan = pd.read_parquet(ARQ_PAINEL)
    pan = pan[pan["ano"].between(ANO_INI, ANO_FIM)].copy()

    reg = amc_para_meso()                       # code_amc, nm_meso, cx, cy (EPSG:5880)
    reg["regiao"] = reg["nm_meso"].map(regiao_de_meso)

    import geopandas as gpd                      # latitude (graus) para faixas e rótulos
    pts = gpd.GeoSeries(gpd.points_from_xy(reg["cx"], reg["cy"]), crs=CRS_METRICO).to_crs(CRS_GEO)
    reg["lat"] = pts.y.to_numpy()
    # 4 faixas de latitude (Sul→Norte), rótulo pela latitude média
    reg["faixa_lat"] = pd.qcut(reg["lat"], 4, labels=["F1 (sul)", "F2", "F3", "F4 (norte)"])

    pan = pan.merge(reg[["code_amc", "nm_meso", "regiao", "lat", "faixa_lat"]],
                    on="code_amc", how="left")
    print(f"[carga] painel {pan.shape[0]:,} linhas | {pan['code_amc'].nunique()} AMCs × "
          f"{pan['ano'].nunique()} anos | regiões: "
          f"{reg['regiao'].value_counts().to_dict()}")
    return pan, reg


# ---------------------------------------------------------------------------
# 2. Bloco A — estoque convertível por AMC×ano (3 definições D13) + depleção
# ---------------------------------------------------------------------------

def justificar_d13(pan: pd.DataFrame) -> pd.DataFrame:
    """Depleção 1985→2024 por classe natural (justifica excluir floresta nativa)."""
    linhas = []
    for col, rot in [(CL_SAVANA, "Formação savânica"), (CL_FLORESTA, "Floresta nativa"),
                     (CL_CAMPO, "Campo nativo"), (CL_ALAGADO, "Campo alagado (não usado)")]:
        s = pan.groupby("ano")[col].sum() / 1e6
        v0, v1 = s.loc[ANO_INI], s.loc[ANO_FIM]
        linhas.append({"classe": rot, "mha_1985": round(v0, 2), "mha_2024": round(v1, 2),
                       "deplecao_pct": round(100 * (1 - v1 / v0), 1) if v0 else np.nan})
    out = pd.DataFrame(linhas)
    print("\n[D13] depleção por classe natural 1985→2024:")
    for _, r in out.iterrows():
        print(f"   {r['classe']:<28} {r['mha_1985']:>6} → {r['mha_2024']:>6} Mha  "
              f"({r['deplecao_pct']:>5}% perdido)")
    return out


def estoque_convertivel(pan: pd.DataFrame) -> pd.DataFrame:
    cols_meta = ["code_amc", "ano", "regiao", "nm_meso", "lat", "faixa_lat",
                 "lulc_area_total_ha", "censo2017_area_estabelecimentos_ha"]
    df = pan[cols_meta + [CL_FLORESTA, CL_SAVANA, CL_CAMPO, CL_ALAGADO]].copy()

    for nome, cols in DEFINICOES.items():
        df[f"estoque_{nome}_ha"] = df[cols].sum(axis=1, min_count=1)

    # Sensibilidade RL: convertível líquido = max(0, refinada − 20% da área de estab.)
    base_rl = df["censo2017_area_estabelecimentos_ha"].fillna(df["lulc_area_total_ha"])
    df["estoque_refinada_rl_ha"] = np.maximum(0.0, df["estoque_refinada_ha"] - RL_FLOOR * base_rl)

    df = df.sort_values(["code_amc", "ano"]).reset_index(drop=True)

    # Depleção (vs 1985 da AMC) e % da área da AMC, por definição
    base = df[df["ano"] == ANO_BASE].set_index("code_amc")
    for nome in ["ampla", "refinada", "refinada_rl"]:
        col = f"estoque_{nome}_ha"
        b = df["code_amc"].map(base[col])
        df[f"deplecao_{nome}"] = np.where(b > 0, 1 - df[col] / b, np.nan)
        df[f"pct_area_{nome}"] = df[col] / df["lulc_area_total_ha"]

    # Fluxo e hazard (na definição primária) — perda líquida anual de estoque
    df["estoque_prev"] = df.groupby("code_amc")[f"estoque_{DEF_PRIMARIA}_ha"].shift(1)
    df["fluxo_ha"]   = np.maximum(0.0, df["estoque_prev"] - df[f"estoque_{DEF_PRIMARIA}_ha"])
    df["hazard"]     = np.where(df["estoque_prev"] > 0, df["fluxo_ha"] / df["estoque_prev"], np.nan)
    df["deplecao_prev"] = df.groupby("code_amc")[f"deplecao_{DEF_PRIMARIA}"].shift(1)
    return df


def agregar_regional(est: pd.DataFrame) -> pd.DataFrame:
    """Totais por (agrupamento × grupo × ano): estoque, fluxo, hazard, % restante."""
    saidas = []
    for agr_col, agr_nome in [("regiao", "mesorregiao"), ("faixa_lat", "faixa_lat")]:
        g = (est.groupby([agr_col, "ano"], observed=True)
                .agg(estoque_ampla_mha=("estoque_ampla_ha", lambda s: s.sum() / 1e6),
                     estoque_refinada_mha=("estoque_refinada_ha", lambda s: s.sum() / 1e6),
                     estoque_refinada_rl_mha=("estoque_refinada_rl_ha", lambda s: s.sum() / 1e6),
                     fluxo_mha=("fluxo_ha", lambda s: s.sum() / 1e6))
                .reset_index().rename(columns={agr_col: "grupo"}))
        g["grupo"] = g["grupo"].astype(str)   # faixa_lat vem como categórico
        g["agrupamento"] = agr_nome
        # % restante vs 1985 do grupo (definição primária) + hazard agregado
        b = g[g["ano"] == ANO_BASE].set_index("grupo")["estoque_refinada_mha"]
        g["pct_restante"] = g["estoque_refinada_mha"] / g["grupo"].map(b)
        g["estoque_prev_mha"] = g.groupby("grupo")["estoque_refinada_mha"].shift(1)
        g["hazard"] = np.where(g["estoque_prev_mha"] > 0, g["fluxo_mha"] / g["estoque_prev_mha"], np.nan)
        saidas.append(g)
    out = pd.concat(saidas, ignore_index=True)
    return out[["agrupamento", "grupo", "ano", "estoque_ampla_mha", "estoque_refinada_mha",
                "estoque_refinada_rl_mha", "pct_restante", "fluxo_mha", "hazard"]]


# ---------------------------------------------------------------------------
# 3. Bloco B — teste de oferta: hazard + painel 2-way FE
# ---------------------------------------------------------------------------

def _painel_fe(df: pd.DataFrame, y: str, xs: list[str], time_effects: bool = True) -> dict | None:
    """PanelOLS com efeito fixo de entidade (+ tempo), nas DUAS réguas de erro-padrão.

    Absorver o ano e AGRUPAR por ano são escolhas independentes: o cluster duplo
    entidade+ano é computável com ou sem `time_effects`. Ele é a régua que decide,
    aqui como no #39B; o agrupamento só por entidade vem ao lado porque é a régua
    mais frouxa, e mostrar as duas é o que impede a régua de ser trocada em silêncio.

    ⚠ CORREÇÃO DATADA (21/ago/2026). Até aqui as duas escolhas estavam amarradas neste
      ajuste: sem `time_effects`, o B3 recaía no agrupamento por entidade, e o apêndice
      da qualificação publicava isso como imposição do desenho ("sem efeito fixo de ano,
      o B3 não admite o agrupamento por ano"). Não era imposição, era acoplamento de
      código — e caía justamente onde mais custa, porque os regressores de demanda do B3
      são séries nacionais, constantes dentro do ano, para as quais o agrupamento por
      entidade subestima o erro-padrão. Sob a régua que decide, o estoque sobrevive
      (p<0,001, o resultado que a linha sustenta) e os três sinais de demanda deixam de
      cruzar 5% (câmbio 0,003→0,179; preço da soja <0,001→0,150; crédito 0,828→0,950).
      Nenhum deles era lido como significância no texto; a linha do estoque, que era,
      não se move.

    Variáveis padronizadas (z) na chamada → betas comparáveis.
    """
    from linearmodels.panel import PanelOLS
    sub = df[["code_amc", "ano", y, *xs]].dropna().copy()
    if sub["code_amc"].nunique() < 30 or len(sub) < 200:
        return None
    sub = sub.set_index(["code_amc", "ano"])
    try:
        mod = PanelOLS(sub[y], sub[xs], entity_effects=True, time_effects=time_effects,
                       check_rank=False)
        r_ent = mod.fit(cov_type="clustered", cluster_entity=True)
        r_2w  = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    except Exception as e:  # noqa: BLE001
        return {"erro": str(e)[:120]}
    # A de duas dimensões decide; a de entidade só assume se a vcov bidimensional não
    # sair positiva-definida (erro-padrão não finito) — e o rótulo diz quando assumiu.
    if np.all(np.isfinite(r_2w.std_errors.to_numpy())):
        res, cluster = r_2w, "entidade+ano"
    else:
        res, cluster = r_ent, "entidade (fallback)"
    return {"params": res.params, "se": res.std_errors, "t": res.tstats, "p": res.pvalues,
            "p_entidade": r_ent.pvalues, "p_entidade_ano": r_2w.pvalues,
            "n_obs": int(res.nobs), "n_amc": int(sub.index.get_level_values(0).nunique()),
            "r2_within": float(res.rsquared_within), "cluster": cluster}


def teste_supply(est: pd.DataFrame) -> pd.DataFrame:
    """Especificações de oferta (z-score sobre o painel modelado)."""
    df = est.copy()
    df["lestoque"]  = df["estoque_prev"]                      # estoque defasado (nível)
    df["lestoque2"] = df["estoque_prev"] ** 2
    df["ldeplecao"] = df["deplecao_prev"]                    # depleção defasada (0..1)

    # drivers (1as diferenças, z-score sobre os anos) por ano — para o spec controlado
    drv = pd.read_csv(ARQ_DRIVERS).sort_values("ano").set_index("ano")
    dd = pd.DataFrame(index=drv.index)
    for d in DRIVERS:
        dd[f"zd_{d}"] = _zscore(drv[d].diff())
    df = df.merge(dd.reset_index(), on="ano", how="left")

    # z-score das colunas de modelagem (betas legíveis/comparáveis; t/p invariantes)
    for c in ["fluxo_ha", "hazard", "lestoque", "lestoque2", "ldeplecao"]:
        df[c + "_z"] = _zscore(df[c])

    specs = [
        # (rótulo, y, regressores, time_effects, hipótese de leitura)
        ("B1  fluxo ~ estoque_def (disponibilidade)",
         "fluxo_ha_z", ["lestoque_z"], True,
         "β>0: conversão escala com o estoque disponível (canal de disponibilidade)."),
        ("B1q fluxo ~ estoque + estoque² (não-linear)",
         "fluxo_ha_z", ["lestoque_z", "lestoque2_z"], True,
         "Curvatura: conversão satura/derruba quando o estoque rareia."),
        ("B2a hazard ~ estoque_def",
         "hazard_z", ["lestoque_z"], True,
         "β>0: AMCs com mais estoque convertem MAIS por unidade (comportamento de fronteira)."),
        ("B2b hazard ~ esgotamento_def",
         "hazard_z", ["ldeplecao_z"], True,
         "β<0: hazard CAI com o esgotamento = remanescente difícil de converter (atrito de oferta)."),
        ("B3  fluxo ~ estoque + demanda (sem ano FE)",
         "fluxo_ha_z", ["lestoque_z", "zd_cambio_real_efetivo",
                        "zd_preco_recebido_soja_idx", "zd_credito_rural_go_real"], False,
         "Estoque sobrevive ao controle por demanda (#37)? → oferta adiciona poder."),
    ]
    linhas = []
    for rotulo, y, xs, te, hip in specs:
        r = _painel_fe(df, y, xs, time_effects=te)
        if r is None or "erro" in r:
            linhas.append({"spec": rotulo, "erro": (r or {}).get("erro", "amostra insuficiente")})
            continue
        for x in xs:
            # `p` é o da régua que decide (a mesma de `se`/`t`); `p_entidade` e
            # `p_entidade_ano` vão ao lado para que a troca de régua não passe calada.
            linhas.append({"spec": rotulo, "regressor": x,
                           "beta": round(float(r["params"][x]), 4),
                           "se": round(float(r["se"][x]), 4),
                           "t": round(float(r["t"][x]), 2),
                           "p": round(float(r["p"][x]), 4),
                           "p_entidade": round(float(r["p_entidade"][x]), 4),
                           "p_entidade_ano": round(float(r["p_entidade_ano"][x]), 4),
                           "n_obs": r["n_obs"], "n_amc": r["n_amc"],
                           "r2_within": round(r["r2_within"], 4),
                           "cluster": r["cluster"], "hipotese": hip})
    out = pd.DataFrame(linhas)
    print("\n[Bloco B] teste de oferta (painel 2-way FE):")
    for _, r in out.iterrows():
        if "erro" in r and pd.notna(r.get("erro")):
            print(f"   {r['spec']}: {r['erro']}"); continue
        sig = "***" if r["p"] < 0.01 else "**" if r["p"] < 0.05 else "*" if r["p"] < 0.1 else ""
        print(f"   {r['spec'][:36]:<36} {r['regressor']:<26} β={r['beta']:+.3f} "
              f"p={r['p']:.3f}{sig:<3} (ent={r['p_entidade']:.3f} "
              f"ent+ano={r['p_entidade_ano']:.3f}) N={r['n_obs']} AMCs={r['n_amc']}")
    return out


# ---------------------------------------------------------------------------
# 4. Bloco C — decomposição oferta×demanda da desaceleração Ato II→III
# ---------------------------------------------------------------------------

def _stats_regiao_ato(est: pd.DataFrame, regioes: dict[str, list[str]]) -> pd.DataFrame:
    """Fluxo médio anual, estoque médio e hazard por (região × ato)."""
    linhas = []
    for nome, membros in regioes.items():
        sub = est if membros is None else est[est["regiao"].isin(membros)]
        for ato, info in ATOS.items():
            a = sub[sub["ano"].between(info["inicio"], info["fim"])]
            # fluxo médio anual: soma estadual por ano (Mha), média sobre os anos
            fluxo_ano = a.groupby("ano")["fluxo_ha"].sum() / 1e6
            est_ano   = a.groupby("ano")["estoque_prev"].sum() / 1e6
            fbar = float(fluxo_ano.mean()) if len(fluxo_ano) else np.nan
            sbar = float(est_ano.mean()) if len(est_ano) else np.nan
            linhas.append({"regiao": nome, "ato": ato, "periodo": f"{info['inicio']}-{info['fim']}",
                           "fluxo_mha_ano": fbar, "estoque_mha": sbar,
                           "hazard": fbar / sbar if sbar else np.nan})
    return pd.DataFrame(linhas)


def decomposicao(est: pd.DataFrame) -> pd.DataFrame:
    regioes = {"Goiás (total)": None, "Sul": ["Sul"], "Centro": ["Centro"], "Norte": ["Norte"]}
    sa = _stats_regiao_ato(est, regioes)
    piv = sa.pivot(index="regiao", columns="ato")

    linhas = []
    for reg in regioes:
        s2, s3 = piv[("estoque_mha", "II")][reg], piv[("estoque_mha", "III")][reg]
        h2, h3 = piv[("hazard", "II")][reg],     piv[("hazard", "III")][reg]
        f2, f3 = piv[("fluxo_mha_ano", "II")][reg], piv[("fluxo_mha_ano", "III")][reg]
        sbar, hbar = (s2 + s3) / 2, (h2 + h3) / 2
        ef_estoque = hbar * (s3 - s2)        # efeito-OFERTA   (menos terra disponível)
        # RESIDUAL, não "demanda": o hazard capta tudo o que não é o volume do
        # estoque — propensão a converter, atrito de acesso, proteção e troca da
        # fonte de terra. Ver a "Ressalva de rótulo" no §3 do 39_fronteira_fechando.md.
        ef_hazard  = sbar * (h3 - h2)        # efeito-RESIDUAL (a taxa por unidade muda)
        dflow = f3 - f2
        # Shares só quando Δfluxo não é ~ruído; senão os efeitos opostos quase se
        # cancelam e a razão explode → reportar NaN.
        estavel = abs(dflow) >= 0.003
        linhas.append({"regiao": reg,
                       "fluxo_II": round(f2, 4), "fluxo_III": round(f3, 4),
                       "d_fluxo": round(dflow, 4),
                       "hazard_II": round(h2, 4), "hazard_III": round(h3, 4),
                       "estoque_II": round(s2, 3), "estoque_III": round(s3, 3),
                       "efeito_estoque": round(ef_estoque, 4),
                       "efeito_hazard": round(ef_hazard, 4),
                       "share_estoque": round(ef_estoque / dflow, 3) if estavel else np.nan,
                       "share_hazard": round(ef_hazard / dflow, 3) if estavel else np.nan})
    out = pd.DataFrame(linhas)

    # Leitura de demanda (#37): a demanda realmente caiu no Ato III?
    drv = pd.read_csv(ARQ_DRIVERS)
    dr_ato = {}
    for ato, info in ATOS.items():
        a = drv[drv["ano"].between(info["inicio"], info["fim"])]
        dr_ato[ato] = {d: round(float(a[d].mean()), 1) for d in DRIVERS}

    print("\n[Bloco C] decomposição da Δ fluxo de conversão de veg. (Ato II→III) por região:")
    for _, r in out.iterrows():
        nota = " [Δfluxo~0: efeitos opostos se cancelam]" if pd.isna(r["share_estoque"]) else ""
        print(f"   {r['regiao']:<14} Δfluxo={r['d_fluxo']:+.4f} Mha/ano | "
              f"oferta(Δestoque)={r['efeito_estoque']:+.4f} | "
              f"demanda(Δhazard)={r['efeito_hazard']:+.4f}{nota}")
    print("   demanda macro por ato (#37, níveis médios):")
    for d in DRIVERS:
        print(f"     {d:<26} II={dr_ato['II'][d]:>8} → III={dr_ato['III'][d]:>8}")
    return out


# ---------------------------------------------------------------------------
# 5. Figuras
# ---------------------------------------------------------------------------

def _bandas_ato(ax):
    cores = {"I": "#f5efe6", "II": "#eef3ee", "III": "#e7efe9"}
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"], info["fim"], color=cores[ato], alpha=0.5, zorder=0)


def figuras(reg_df: pd.DataFrame, est: pd.DataFrame, dec: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Fig 1 — estoque convertível restante por mesorregião × ano
    meso = reg_df[reg_df["agrupamento"] == "mesorregiao"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _bandas_ato(ax)
    for r in ["Sul", "Centro", "Norte"]:
        s = meso[meso["grupo"] == r].sort_values("ano")
        ax.plot(s["ano"], s["estoque_refinada_mha"], lw=2.2, color=CORES_REGIAO[r], label=r)
    ax.set_xlabel("Ano"); ax.set_ylabel("Cerrado convertível restante (Mha, def. refinada)")
    ax.set_title("Estoque de Cerrado convertível por mesorregião — a fronteira recua ao norte")
    ax.legend(title="Mesorregião"); ax.set_xlim(ANO_INI, ANO_FIM)
    fig.tight_layout(); fig.savefig(DIR_OUT / "estoque_por_regiao.png", dpi=140); plt.close(fig)

    # Fig 2 — % restante por faixa de latitude (Sul→Norte)
    fl = reg_df[reg_df["agrupamento"] == "faixa_lat"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _bandas_ato(ax)
    cmap = plt.cm.viridis(np.linspace(0.1, 0.9, fl["grupo"].nunique()))
    for cor, g in zip(cmap, sorted(fl["grupo"].unique(), key=str)):
        s = fl[fl["grupo"] == g].sort_values("ano")
        ax.plot(s["ano"], s["pct_restante"] * 100, lw=2, color=cor, label=str(g))
    ax.set_xlabel("Ano"); ax.set_ylabel("% do estoque convertível de 1985 ainda restante")
    ax.set_title("Esgotamento do Cerrado convertível por faixa de latitude (Sul→Norte)")
    ax.legend(title="Faixa (latitude)"); ax.set_xlim(ANO_INI, ANO_FIM)
    fig.tight_layout(); fig.savefig(DIR_OUT / "deplecao_latitude.png", dpi=140); plt.close(fig)

    # Fig 3 — hazard vs depleção (binned), pooled AMC×ano
    d = est.dropna(subset=["hazard", "deplecao_prev"]).copy()
    d = d[(d["hazard"] >= 0) & (d["hazard"] <= 1)]
    d["bin"] = pd.cut(d["deplecao_prev"], np.linspace(0, 1, 11))
    gb = d.groupby("bin", observed=True)["hazard"].agg(["mean", "median", "count"]).reset_index()
    gb["centro"] = gb["bin"].apply(lambda b: b.mid)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(d["deplecao_prev"], d["hazard"], s=4, alpha=0.06, color="#777")
    ax.plot(gb["centro"], gb["mean"], "-o", color="#b3261e", lw=2.2, label="hazard médio por bin")
    ax.set_xlabel("Esgotamento acumulado do estoque convertível (0 = intacto, 1 = exaurido)")
    ax.set_ylabel("Hazard anual (perda / estoque do ano anterior)")
    ax.set_title("A conversão trava onde o estoque acabou? (hazard × esgotamento, AMC×ano)")
    ax.set_ylim(0, min(0.2, float(d["hazard"].quantile(0.99)))); ax.legend()
    fig.tight_layout(); fig.savefig(DIR_OUT / "hazard_vs_deplecao.png", dpi=140); plt.close(fig)

    # Fig 4 — decomposição oferta×demanda (Ato II→III) por região
    dd = dec[dec["regiao"] != "Goiás (total)"].copy()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(dd)); w = 0.38
    ax.bar(x - w / 2, dd["efeito_estoque"], w, color="#2e7d32", label="Efeito-OFERTA (Δestoque)")
    ax.bar(x + w / 2, dd["efeito_hazard"], w, color="#8a8a8a",
           label="Efeito-RESIDUAL (Δhazard) — NÃO é demanda medida")
    ax.plot(x, dd["d_fluxo"], "D", color="k", ms=8, label="Δ fluxo observado")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(dd["regiao"])
    ax.set_ylabel("Contribuição à Δ do fluxo de conversão (Mha/ano), Ato II→III")
    ax.set_title("Por que o fluxo mudou? oferta (estoque) vs o resto (hazard)")
    ax.legend()
    fig.tight_layout(); fig.savefig(DIR_OUT / "decomposicao_oferta_demanda.png", dpi=140); plt.close(fig)

    print(f"\n[figuras] 4 PNGs em {DIR_OUT}")


# ---------------------------------------------------------------------------
# 6. Main
# ---------------------------------------------------------------------------

def main(sem_figuras: bool = False) -> None:
    pan, _reg = carregar()
    justificar_d13(pan)

    est = estoque_convertivel(pan)
    reg_df = agregar_regional(est)

    cols_amc = ["code_amc", "ano", "regiao", "nm_meso", "lat",
                "estoque_ampla_ha", "estoque_refinada_ha", "estoque_refinada_rl_ha",
                "deplecao_ampla", "deplecao_refinada", "deplecao_refinada_rl",
                "pct_area_refinada", "estoque_prev", "fluxo_ha", "hazard", "deplecao_prev"]
    est[cols_amc].to_csv(DIR_PROC / "fronteira_estoque_convertivel.csv", index=False)
    reg_df.to_csv(DIR_PROC / "fronteira_regional.csv", index=False)

    supply = teste_supply(est)
    supply.to_csv(DIR_PROC / "fronteira_teste_supply.csv", index=False)

    dec = decomposicao(est)
    dec.to_csv(DIR_PROC / "fronteira_decomposicao.csv", index=False)

    if not sem_figuras:
        figuras(reg_df, est, dec)

    print("\n[ok] Pipeline #39 concluído. CSVs em data/processed/fronteira_*.csv")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline #39 — A fronteira está fechando?")
    p.add_argument("--sem-figuras", action="store_true", help="pula a geração de PNGs")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(sem_figuras=args.sem_figuras)
