"""
Pipeline #41 — O fogo lidera a marcha ao norte? (fogo como assinatura da fronteira)
==================================================================================

PERGUNTA QUE RESPONDE
---------------------
O Pipeline #14 (fogo) ficou FORA da narrativa Sul→Norte (#32–#40). Este pipeline
o traz para dentro testando o item 4 do backlog: o CENTROIDE do fogo *lidera* o
centroide da conversão veg→pasto na marcha ao norte? O fogo é a assinatura
ANTECIPATÓRIA da fronteira agropecuária?

A intuição (doc do #14): "fogo no Cerrado precede ~70% das conversões". Se for
verdade, a geografia do fogo deve estar À FRENTE (mais ao norte) e/ou ANTES (no
tempo) da geografia da conversão.

A ARMADILHA (que este pipeline navega explicitamente, no espírito das correções
dos #34/#37/#40): fogo em vegetação natural e a conversão veg→pasto são quase o
MESMO evento — queimar o Cerrado é, muitas vezes, o ato de abri-lo para pasto.
Um "fogo lidera por ~1 ano" no centroide seria então em parte DEFINICIONAL, não
uma descoberta. Duas coisas blindam a leitura:
  (i)  o fogo em veg natural é ~5–15× MAIOR que a conversão veg→pasto do mesmo
       ano (validação: 2010 fogo_veg=1,27 Mha vs conv=0,083 Mha) — a maior parte
       do fogo NÃO vira pasto, e tem forte componente CLIMÁTICO (1985/2010 = seca).
       Logo o fogo é um sinal MAIS AMPLO, não o decalque da conversão.
  (ii) o teste local (Bloco 4) usa EFEITO FIXO DE ANO, que absorve o choque
       climático comum, e separa o fogo-que-abre-fronteira (fogo em veg →
       conversão) do fogo-de-manejo (conversão → fogo em pasto), em direções
       opostas e com tipos de fogo distintos.

ABORDAGEM (4 blocos)
--------------------
  Bloco 1 — CENTROIDES anuais (mean + median ponderados, EPSG:5880) de quatro
    fluxos: fogo em veg natural, fogo total, fogo em pasto, e conversão veg→pasto.
    Sobre os centroides das AMCs (#25), reusando a maquinaria do #32 (D11:
    AMC neutraliza emancipação).
  Bloco 2 — DESLOCAMENTO N–S (ΔN km, 1985→2023) de cada centroide + OFFSET
    espacial anual lat(fogo_veg) − lat(conv): o fogo está ao NORTE da conversão?
  Bloco 3 — LEAD-LAG AGREGADO: CCF + Granger nas 1as diferenças das latitudes
    dos centroides (fogo_veg → conv), reusando ccf_defasada/granger do #34.
    k>0 ⇒ o fogo ANTECEDE. Honestidade: lag-0 é parcialmente mecânico.
  Bloco 4 — PAINEL LOCAL de precedência (o teste rigoroso): dentro de cada AMC,
    a conversão veg→pasto responde ao fogo em veg DOS ANOS ANTERIORES?
    distributed-lag em painel 2-way FE (ano FE absorve o clima comum; AMC FE
    absorve a propensão local). + contra-teste do fogo-de-manejo (conversão →
    fogo em PASTO defasado), que deve ir na direção OPOSTA.
  Bloco 5 — ROBUSTEZ da liderança local: re-roda o perfil do Bloco 4 sob 5
    especificações (cluster duplo, log1p, sem anos de seca, só 2001+) e compara
    Σβ passado vs futuro. RESULTADO: a liderança t−1 é FRÁGIL (sig só na base,
    some sob log1p, inverte sem os anos de seca); o ROBUSTO é a co-elevação (t0).
  Bloco 6 — TESTE FOCAL 2001–05: a sub-fase do #29 (perda de veg ~3–5× mais
    intensa) foi um pulso de fogo? Compara fogo×perda×composição por janela.
    RESULTADO: NÃO — perda ~3× mas fogo plano (1,09×); veg→agric dobra (soja
    mecanizada) ⇒ demanda/mecanização, não fogo. Fecha o micro-mistério do #29.

ALINHAMENTO TEMPORAL (decisão D15)
----------------------------------
A conversão é rotulada por ano_origem=t (veg em t, pasto em t+1); o evento de
abertura (fogo) ocorre na estação seca de t. Logo fogo(ano=t) ↔ conv(origem=t)
é o alinhamento CONTEMPORÂNEO (k=0, mecânico/esperado). "Fogo lidera" = fogo(t)
prevê conv(origem=t+1, t+2), i.e. k≥1 sobreviver é o sinal genuíno.

ENTRADAS
    data/processed/fogo_mapbiomas_goias.csv     (#14; 246 munis × 40 anos)
    data/processed/conversao_bruta_municipal.csv(#19; transições, ano_origem)
    data/processed/amc_crosswalk_goias.csv      (#25; cd_mun → code_amc)
    data/processed/amc_goias.gpkg               (#25; geometria → centroides)
    data/processed/centro_massa_anual.csv       (#32; overlay de referência)

SAÍDAS
    data/processed/fogo_fronteira_centroides.csv   (fluxo×ano: x/y/lat mean+med)
    data/processed/fogo_fronteira_deslocamento.csv (ΔN/ΔL km por ato + líquido)
    data/processed/fogo_fronteira_offset.csv       (offset espacial anual fogo−conv)
    data/processed/fogo_fronteira_leadlag.csv      (CCF + Granger agregado)
    data/processed/fogo_fronteira_painel.csv       (distributed-lag FE + manejo)
    data/processed/fogo_fronteira_robustez.csv     (5 specs da liderança local)
    data/processed/fogo_fronteira_pulso2001.csv    (teste focal 2001–05, 4 janelas)
    outputs/fogo_fronteira/latitude_trajetorias.png
    outputs/fogo_fronteira/offset_espacial.png
    outputs/fogo_fronteira/mapa_trajetorias.png
    outputs/fogo_fronteira/leadlag.png
    outputs/fogo_fronteira/robustez_leadlag.png
    outputs/fogo_fronteira/pulso_2001_05.png

COMO RODAR
    python scripts/fogo_lidera_fronteira.py
    python scripts/fogo_lidera_fronteira.py --sem-figuras

Depende de: #14, #19, #25, #32 (reusa funções), #34 (reusa CCF/Granger).
Quando foi feito: 2026-06-07. Item 4 do backlog ("fios em aberto").
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
from config_periodos import ATOS, CORES_ATO                          # noqa: E402
from centro_massa import (mean_center, median_center,                # noqa: E402
                          metros_para_lonlat, CRS_METRICO)
from deslocamento_espacial import ccf_defasada, granger              # noqa: E402

# ---------------------------------------------------------------------------
ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "fogo_fronteira"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_FOGO  = DIR_PROC / "fogo_mapbiomas_goias.csv"
ARQ_CONV  = DIR_PROC / "conversao_bruta_municipal.csv"
ARQ_CW    = DIR_PROC / "amc_crosswalk_goias.csv"
ARQ_GEOM  = DIR_PROC / "amc_goias.gpkg"
ARQ_CM32  = DIR_PROC / "centro_massa_anual.csv"

# Fluxos-alvo: chave -> (rótulo, cor).
FLUXOS = {
    "fogo_veg":   ("Fogo em veg. natural",   "#d84315"),  # laranja-fogo
    "conv_vp":    ("Conversão veg→pasto",     "#6a1b9a"),  # roxo
    "fogo_total": ("Fogo total",              "#ef9a9a"),  # vermelho claro
    "fogo_pasto": ("Fogo em pastagem",        "#8d6e63"),  # marrom
}

MAX_LAG = 5      # defasagens da CCF agregada (anos)
ANO_INI, ANO_FIM = 1985, 2023   # janela comum fogo×conversão (conv termina 2023)


# ---------------------------------------------------------------------------
# 1. Dados: fluxos municipais → AMC + centroides
# ---------------------------------------------------------------------------

def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Painel longo (code_amc, ano, fogo_veg, fogo_total, fogo_pasto, conv_vp)
    com centroides (cx, cy) em EPSG:5880, e a tabela de centroides AMC à parte."""
    import geopandas as gpd

    cw = pd.read_csv(ARQ_CW)[["cd_mun", "code_amc"]]
    cw["code_amc"] = cw["code_amc"].astype(int)

    # --- Fogo: já vem decomposto por classe; agregar muni → AMC ---
    fogo = pd.read_csv(ARQ_FOGO)
    fogo = fogo.merge(cw, on="cd_mun", how="left")
    fogo = (fogo.groupby(["code_amc", "ano"])
                .agg(fogo_veg=("area_queimada_veg_nat_ha", "sum"),
                     fogo_total=("area_queimada_total_ha", "sum"),
                     fogo_pasto=("area_queimada_pastagem_ha", "sum"))
                .reset_index())

    # --- Conversão veg→pasto: filtrar e agregar muni → AMC (rotulada por origem) ---
    conv = pd.read_csv(ARQ_CONV)
    vp = conv[(conv.grupo_orig == "vegetacao_natural") &
              (conv.grupo_dest == "pastagem")].copy()
    vp = vp.rename(columns={"ano_origem": "ano"}).merge(cw, on="cd_mun", how="left")
    vp = (vp.groupby(["code_amc", "ano"])
            .agg(conv_vp=("area_ha", "sum"))
            .reset_index())

    painel = fogo.merge(vp, on=["code_amc", "ano"], how="outer")
    painel = painel[(painel.ano >= ANO_INI) & (painel.ano <= ANO_FIM)]
    for c in ("fogo_veg", "fogo_total", "fogo_pasto", "conv_vp"):
        painel[c] = painel[c].fillna(0.0)

    # --- Centroides das AMC (EPSG:5880) ---
    gdf = gpd.read_file(ARQ_GEOM).to_crs(CRS_METRICO)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    cent = gdf.geometry.centroid
    centroides = pd.DataFrame({"code_amc": gdf["code_amc"].to_numpy(),
                               "cx": cent.x.to_numpy(), "cy": cent.y.to_numpy()})

    faltando = set(painel["code_amc"]) - set(centroides["code_amc"])
    if faltando:
        raise RuntimeError(f"{len(faltando)} AMCs sem centroide: {sorted(faltando)[:8]}")

    painel = painel.merge(centroides, on="code_amc", how="left")
    print(f"[dados] painel {painel.shape[0]:,} linhas | "
          f"{painel['code_amc'].nunique()} AMCs × {painel['ano'].nunique()} anos "
          f"({ANO_INI}–{ANO_FIM}) | centroides EPSG:{CRS_METRICO}")
    return painel, centroides


# ---------------------------------------------------------------------------
# 2. Centroides anuais (mean + median ponderados) por fluxo
# ---------------------------------------------------------------------------

def centroides_anuais(painel: pd.DataFrame) -> pd.DataFrame:
    """Centro médio e mediano por (fluxo, ano), ponderado pela área do fluxo."""
    linhas = []
    for chave, (rotulo, _cor) in FLUXOS.items():
        for ano, g in painel.groupby("ano"):
            sub = g[["cx", "cy", chave]].dropna()
            sub = sub[sub[chave] > 0]
            if len(sub) < 5:
                continue
            x, y = sub["cx"].to_numpy(), sub["cy"].to_numpy()
            w = sub[chave].to_numpy(float)
            mx, my = mean_center(x, y, w)
            dx, dy = median_center(x, y, w)
            linhas.append({"fluxo": chave, "rotulo": rotulo, "ano": int(ano),
                           "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
                           "peso_total_mha": float(w.sum()) / 1e6, "n_amc": int(len(sub))})
    df = pd.DataFrame(linhas)
    ll_mean = metros_para_lonlat(df[["x_mean", "y_mean"]].to_numpy())
    ll_med  = metros_para_lonlat(df[["x_med", "y_med"]].to_numpy())
    df["lon_mean"], df["lat_mean"] = ll_mean[:, 0], ll_mean[:, 1]
    df["lon_med"],  df["lat_med"]  = ll_med[:, 0],  ll_med[:, 1]
    return df.sort_values(["fluxo", "ano"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Deslocamento N–S por ato + offset espacial fogo×conversão
# ---------------------------------------------------------------------------

def deslocamento_e_offset(cent: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(a) ΔN/ΔL (km) do centro médio por ato e líquido; (b) offset anual
    lat(fogo_veg) − lat(conv): o fogo está ao norte da conversão?"""
    linhas = []
    for chave, g in cent.groupby("fluxo"):
        rotulo = g["rotulo"].iloc[0]
        gi = g.set_index("ano")
        def reg(rot, a0, a1):
            if a0 not in gi.index or a1 not in gi.index:
                return
            dn = (gi.loc[a1, "y_mean"] - gi.loc[a0, "y_mean"]) / 1000
            dl = (gi.loc[a1, "x_mean"] - gi.loc[a0, "x_mean"]) / 1000
            azim = np.degrees(np.arctan2(dl, dn)) % 360
            linhas.append({"fluxo": chave, "rotulo": rotulo, "periodo": rot,
                           "ano_ini": a0, "ano_fim": a1, "dnorte_km": dn,
                           "dleste_km": dl, "dtotal_km": float(np.hypot(dn, dl)),
                           "azimute_deg": azim})
        for ato, info in ATOS.items():
            ini = info["inicio"]; fim = min(info["fim"], ANO_FIM)
            reg(f"Ato {ato}", ini, fim)
        reg("LÍQUIDO", ANO_INI, ANO_FIM)
    desloc = pd.DataFrame(linhas)

    # Offset espacial: lat(fogo_veg) − lat(conv) por ano (mean e median).
    piv = cent.pivot_table(index="ano", columns="fluxo",
                           values=["lat_mean", "lat_med"])
    off = pd.DataFrame({"ano": piv.index})
    off["offset_lat_mean_deg"] = (piv[("lat_mean", "fogo_veg")] -
                                  piv[("lat_mean", "conv_vp")]).to_numpy()
    off["offset_lat_med_deg"]  = (piv[("lat_med", "fogo_veg")] -
                                  piv[("lat_med", "conv_vp")]).to_numpy()
    # km aprox.: 1° lat ≈ 110,57 km.
    off["offset_norte_km"] = off["offset_lat_mean_deg"] * 110.57
    return desloc, off.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Lead-lag agregado (CCF + Granger nas 1as diferenças das latitudes)
# ---------------------------------------------------------------------------

def leadlag_agregado(cent: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Δlat(fogo_veg) lidera Δlat(conv)? CCF (k>0 ⇒ fogo antecede) + Granger,
    com teste reverso. Em 1as diferenças (D7) para remover a tendência comum."""
    lat = cent.pivot(index="ano", columns="fluxo", values="lat_mean").sort_index()
    lat = lat[["fogo_veg", "conv_vp", "fogo_total"]].dropna()
    d = lat.diff().dropna()

    pares = [
        ("fogo_veg",   "conv_vp",  "Δlat fogo_veg → Δlat conv (fogo lidera?)"),
        ("fogo_total", "conv_vp",  "Δlat fogo_total → Δlat conv"),
        ("conv_vp",    "fogo_veg", "Δlat conv → Δlat fogo_veg (reverso/placebo)"),
    ]
    linhas = []
    for xc, yc, rot in pares:
        ccf = ccf_defasada(d[xc].to_numpy(), d[yc].to_numpy(), MAX_LAG)
        melhor = ccf.loc[ccf["r"].abs().idxmax()]
        gr = granger(d[xc], d[yc], maxlag=2)
        for g in gr:
            linhas.append({"relacao": rot, "ccf_lag_pico": int(melhor["lag"]),
                           "ccf_r_pico": melhor["r"], "granger_lag": g["lag"],
                           "granger_p": g["p_valor"]})
    return pd.DataFrame(linhas), d


# ---------------------------------------------------------------------------
# 5. Painel local de precedência (distributed-lag em 2-way FE)
# ---------------------------------------------------------------------------

def _zscore(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd > 0 else s * 0.0


def painel_precedencia(painel: pd.DataFrame) -> pd.DataFrame:
    """Dentro de cada AMC, a conversão responde ao fogo em veg DOS ANOS ANTERIORES?
    distributed-lag em painel 2-way FE (entity=AMC, time=ano), SE clusterizado por
    AMC. ano FE absorve o choque climático comum (seca → fogo em todo o estado).
    z-score nas variáveis → β comparáveis entre defasagens.

    Modelos:
      (A) PERFIL combinado: conv_vp(t) ~ fogo_veg em k=−2,−1,0,+1,+2 (passado E futuro
          no MESMO modelo). k>0 (passado) = fogo lidera; k<0 (futuro) = placebo. O
          perfil simétrico distingue liderança genuína (pico no passado, soma
          passado>futuro) de co-elevação de "episódio de fronteira" (perfil chato).
      (B) manejo: fogo_pasto(t) ~ conv_vp em k=0,−1,−2 — conversão precede o fogo de
          MANEJO da pastagem nova (direção oposta, tipo de fogo distinto = contra-prova).
    """
    from linearmodels.panel import PanelOLS

    df = painel[["code_amc", "ano", "fogo_veg", "fogo_pasto", "conv_vp"]].copy()
    df = df.sort_values(["code_amc", "ano"])
    # z-score pooled (β em desvios-padrão, comparável entre lags e modelos).
    for c in ("fogo_veg", "fogo_pasto", "conv_vp"):
        df[f"z_{c}"] = _zscore(df[c])
    # Defasagens (lag = passado, k>0) e avanços (lead = futuro) por AMC.
    g = df.groupby("code_amc")
    for k in (1, 2):
        df[f"z_fogo_veg_lag{k}"]  = g["z_fogo_veg"].shift(k)
        df[f"z_fogo_veg_lead{k}"] = g["z_fogo_veg"].shift(-k)
        df[f"z_conv_vp_lag{k}"]   = g["z_conv_vp"].shift(k)

    def ajustar(y, xs, rotulo):
        sub = df.dropna(subset=[y] + xs).set_index(["code_amc", "ano"])
        mod = PanelOLS(sub[y], sub[xs], entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        out = []
        for x in xs:
            out.append({"modelo": rotulo, "y": y, "termo": x,
                        "beta": round(float(res.params[x]), 4),
                        "se": round(float(res.std_errors[x]), 4),
                        "p": round(float(res.pvalues[x]), 4),
                        "n": int(res.nobs), "r2w": round(float(res.rsquared_within), 4)})
        return out

    linhas = []
    # (A) PERFIL combinado: passado (lidera) vs futuro (placebo) no mesmo modelo.
    linhas += ajustar("z_conv_vp",
                      ["z_fogo_veg_lag2", "z_fogo_veg_lag1", "z_fogo_veg",
                       "z_fogo_veg_lead1", "z_fogo_veg_lead2"],
                      "A) conv ~ fogo_veg(t-2..t+2)  [perfil; passado=lidera, futuro=placebo]")
    # (B) manejo: conversão precede fogo de pastagem (direção oposta, contra-prova).
    linhas += ajustar("z_fogo_pasto",
                      ["z_conv_vp", "z_conv_vp_lag1", "z_conv_vp_lag2"],
                      "B) fogo_pasto ~ conv(0,t-1,t-2)  [manejo: conv lidera]")
    return pd.DataFrame(linhas)


def robustez_leadlag(painel: pd.DataFrame) -> pd.DataFrame:
    """A liderança LOCAL (perfil do modelo A) é FRÁGIL? Re-roda o perfil
    conv(t)~fogo_veg(t−2..t+2) sob 5 especificações e compara a soma dos coefs do
    PASSADO (lidera) vs FUTURO (placebo). Se a assimetria passado>futuro só aparece
    numa especificação, o "fogo lidera" não é robusto — só a co-elevação é.

    Especificações:
      base    — z-score, cluster entidade (= modelo A)
      cl_dupl — z-score, cluster duplo entidade+ano (serial+seccional)
      log1p   — log1p em fogo e conv (doma cauda pesada / zero-inflação do fluxo)
      sem_seca— exclui 1985 e 2010 (anos extremos de fogo climático)
      ato2_3  — só 2001–2023 (fronteira recente, sem o grande pulso veg→pasto inicial)
    """
    from linearmodels.panel import PanelOLS

    base = painel[["code_amc", "ano", "fogo_veg", "conv_vp"]].copy()
    base = base.sort_values(["code_amc", "ano"])

    def montar(d, transf):
        d = d.copy()
        if transf == "log1p":
            d["X"] = np.log1p(d["fogo_veg"]); d["Y"] = np.log1p(d["conv_vp"])
        else:
            d["X"] = _zscore(d["fogo_veg"]); d["Y"] = _zscore(d["conv_vp"])
        g = d.groupby("code_amc")
        for k in (1, 2):
            d[f"X_lag{k}"]  = g["X"].shift(k)
            d[f"X_lead{k}"] = g["X"].shift(-k)
        return d

    specs = [
        ("base",     base,                                  "z",     "entity"),
        ("cl_dupl",  base,                                  "z",     "both"),
        ("log1p",    base,                                  "log1p", "entity"),
        ("sem_seca", base[~base.ano.isin([1985, 2010])],    "z",     "entity"),
        ("ato2_3",   base[base.ano >= 2001],                "z",     "entity"),
    ]
    xs = ["X_lag2", "X_lag1", "X", "X_lead1", "X_lead2"]
    linhas = []
    for nome, dd, transf, clus in specs:
        d = montar(dd, transf).dropna(subset=["Y"] + xs).set_index(["code_amc", "ano"])
        mod = PanelOLS(d["Y"], d[xs], entity_effects=True, time_effects=True)
        if clus == "both":
            res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        else:
            res = mod.fit(cov_type="clustered", cluster_entity=True)
        b, p = res.params, res.pvalues
        soma_pass = float(b["X_lag2"] + b["X_lag1"])
        soma_fut  = float(b["X_lead1"] + b["X_lead2"])
        linhas.append({
            "spec": nome,
            "beta_t-1": round(float(b["X_lag1"]), 4), "p_t-1": round(float(p["X_lag1"]), 4),
            "beta_t0":  round(float(b["X"]), 4),       "p_t0":  round(float(p["X"]), 4),
            "beta_t+1": round(float(b["X_lead1"]), 4), "p_t+1": round(float(p["X_lead1"]), 4),
            "soma_passado": round(soma_pass, 4), "soma_futuro": round(soma_fut, 4),
            "passado_lidera": bool(soma_pass > soma_fut), "n": int(res.nobs)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 5b. Teste focal — o pulso de perda de veg de 2001–05 (#29) foi de FOGO?
# ---------------------------------------------------------------------------

# Janelas para o teste focal (a sub-fase 2001–05 do #29 vs vizinhas).
WINS_PULSO = {"1985-2000": (1985, 2000), "2001-2005": (2001, 2005),
              "2006-2019": (2006, 2019), "2020-2023": (2020, 2023)}


def pulso_2001_05() -> tuple[pd.DataFrame, pd.DataFrame]:
    """O #29 achou uma sub-fase 2001–05 com perda de veg ~5× mais intensa que
    2006–19 (p=0,0008) que não virou período. Foi um pulso de FOGO-de-abertura?

    Compara, por janela: (a) fogo em veg; (b) perda BRUTA veg→não-veg; (c)
    declínio do ESTOQUE de veg; (d) acoplamento espacial fogo×perda (Spearman por
    AMC); (e) composição do destino da perda (veg→pasto vs veg→agric).
    Discriminante = o TEMPO: se o fogo NÃO sobe quando a perda sobe, o pulso não é
    de fogo. O acoplamento espacial alto é a co-localização estrutural (#41), não
    prova de causa.
    """
    from scipy.stats import spearmanr

    cw = pd.read_csv(ARQ_CW)[["cd_mun", "code_amc"]]
    cw["code_amc"] = cw["code_amc"].astype(int)
    fogo = pd.read_csv(ARQ_FOGO).merge(cw, on="cd_mun")
    fa = (fogo.groupby(["code_amc", "ano"])["area_queimada_veg_nat_ha"].sum()
              .reset_index(name="fv"))
    conv = pd.read_csv(ARQ_CONV).merge(cw, on="cd_mun")
    loss = conv[(conv.grupo_orig == "vegetacao_natural") &
                (conv.grupo_dest != "vegetacao_natural")]
    gl = (loss.groupby(["code_amc", "ano_origem"])["area_ha"].sum()
              .reset_index(name="loss").rename(columns={"ano_origem": "ano"}))
    amc = fa.merge(gl, on=["code_amc", "ano"], how="outer").fillna(0.0)

    # Estoque de veg natural (declínio anual) — do painel AMC.
    pan = pd.read_parquet(ARQ_PAINEL := DIR_PROC / "painel_amc_goias.parquet")
    vcols = [c for c in ["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                         "lulc_campo_nativo_ha"] if c in pan.columns]
    est = (pan.groupby("ano")[vcols].sum().sum(axis=1) / 1e6)
    decl = -est.diff()   # +→perdeu estoque (Mha/ano)

    fa_uf   = fogo.groupby("ano")["area_queimada_veg_nat_ha"].sum() / 1e6
    gl_uf   = loss.groupby("ano_origem")["area_ha"].sum() / 1e6
    va_uf   = (conv[(conv.grupo_orig == "vegetacao_natural") &
                    (conv.grupo_dest == "agricultura")]
               .groupby("ano_origem")["area_ha"].sum() / 1e6)

    def wmean(s, lo, hi):
        return float(s[(s.index >= lo) & (s.index <= hi)].mean())

    linhas = []
    for lab, (lo, hi) in WINS_PULSO.items():
        w = amc[(amc.ano >= lo) & (amc.ano <= hi)].groupby("code_amc")[["fv", "loss"]].sum()
        rho, p = spearmanr(w["fv"], w["loss"]) if len(w) > 5 else (np.nan, np.nan)
        gl_w = wmean(gl_uf, lo, hi)
        va_w = wmean(va_uf, lo, hi)
        linhas.append({
            "janela": lab, "ano_ini": lo, "ano_fim": hi,
            "fogo_veg_mha_ano": round(wmean(fa_uf, lo, hi), 3),
            "perda_bruta_mha_ano": round(gl_w, 3),
            "declinio_estoque_mha_ano": round(wmean(decl, lo, hi), 3),
            "veg_agric_mha_ano": round(va_w, 4),
            "share_veg_agric_pct": round(100 * va_w / gl_w, 1) if gl_w else np.nan,
            "spearman_fogo_perda": round(float(rho), 3),
            "spearman_p": round(float(p), 4)})
    tab = pd.DataFrame(linhas)

    # Razões 2001-05 vs 2006-19 (o "5×" do #29) para fogo e para perda/estoque.
    g = tab.set_index("janela")
    razoes = pd.DataFrame([{
        "metrica": m,
        "v_2001_05": g.loc["2001-2005", m],
        "v_2006_19": g.loc["2006-2019", m],
        "razao_01_05_sobre_06_19": round(g.loc["2001-2005", m] / g.loc["2006-2019", m], 2)
            if g.loc["2006-2019", m] else np.nan}
        for m in ["fogo_veg_mha_ano", "perda_bruta_mha_ano",
                  "declinio_estoque_mha_ano"]])

    # Série anual (UF) para a figura.
    anos = range(1990, 2013)
    serie = pd.DataFrame({"ano": list(anos)})
    serie["fogo_veg"] = serie["ano"].map(fa_uf)
    serie["perda_bruta"] = serie["ano"].map(gl_uf)
    serie["declinio_estoque"] = serie["ano"].map(decl)
    return tab, razoes, serie


# ---------------------------------------------------------------------------
# 6. Figuras
# ---------------------------------------------------------------------------

def _bandas_ato(ax):
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, min(info["fim"], ANO_FIM) + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)
        ax.text((info["inicio"] + min(info["fim"], ANO_FIM)) / 2, 0.99,
                f"Ato {ato}", transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=9, color="0.4")


def fig_latitude(cent: pd.DataFrame) -> None:
    """Latitude do centro de massa vs ano — fogo_veg, conv, fogo_total + (overlay)
    estoque de pasto e veg natural do #32 como referência."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    _bandas_ato(ax)
    for chave in ("fogo_veg", "conv_vp", "fogo_total", "fogo_pasto"):
        rotulo, cor = FLUXOS[chave]
        g = cent[cent.fluxo == chave].sort_values("ano")
        lw = 2.4 if chave in ("fogo_veg", "conv_vp") else 1.3
        alpha = 1.0 if chave in ("fogo_veg", "conv_vp") else 0.6
        ax.plot(g["ano"], g["lat_mean"], "-", color=cor, lw=lw, alpha=alpha,
                label=rotulo, zorder=3)
    # Overlay #32 (estoques) se existir.
    if ARQ_CM32.exists():
        cm = pd.read_csv(ARQ_CM32)
        for var, cor, rot in [("pastagem", "#e8920c", "[#32] estoque de pasto"),
                              ("veg_natural", "#2e7d32", "[#32] estoque veg natural")]:
            s = cm[cm.variavel == var].sort_values("ano")
            if not s.empty:
                ax.plot(s["ano"], s["lat_mean"], ":", color=cor, lw=1.4,
                        alpha=0.7, label=rot, zorder=2)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°; mais alto = mais ao norte)")
    ax.set_title("O fogo lidera a marcha ao norte? Centroide dos FLUXOS de fogo e "
                 "conversão veg→pasto\n(Goiás, AMC, 1985–2023; pontilhado = estoques "
                 "do #32 como referência)", fontsize=11.5, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=8.5, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "latitude_trajetorias.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'latitude_trajetorias.png').relative_to(ROOT)}")


def fig_offset(off: pd.DataFrame) -> None:
    """Offset espacial anual lat(fogo_veg) − lat(conv): o fogo está ao norte?"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    _bandas_ato(ax)
    cores = ["#d84315" if v > 0 else "#6a1b9a" for v in off["offset_norte_km"]]
    ax.bar(off["ano"], off["offset_norte_km"], color=cores, alpha=0.85, zorder=3)
    m = off["offset_norte_km"].mean()
    ax.axhline(m, color="0.2", lw=1.4, ls="--",
               label=f"média {m:+.0f} km", zorder=4)
    ax.axhline(0, color="0.3", lw=0.9, zorder=2)
    ax.set_xlabel("Ano")
    ax.set_ylabel("lat(fogo veg) − lat(conversão)  [km; + = fogo ao NORTE]")
    ax.set_title("O fogo em veg natural está espacialmente À FRENTE (ao norte) da "
                 "conversão veg→pasto?\n(laranja = fogo ao norte da conversão; "
                 "roxo = ao sul)", fontsize=11.5, loc="left")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "offset_espacial.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'offset_espacial.png').relative_to(ROOT)}")


def fig_mapa(cent: pd.DataFrame) -> None:
    """Trajetória dos centroides fogo_veg vs conv sobre o contorno de GO (zoom)."""
    import matplotlib.pyplot as plt
    import geopandas as gpd
    amc = gpd.read_file(ARQ_GEOM).to_crs(CRS_METRICO)
    fig, ax = plt.subplots(figsize=(8.5, 9))
    amc.boundary.plot(ax=ax, color="0.88", linewidth=0.35, zorder=1)
    amc.dissolve().boundary.plot(ax=ax, color="0.5", linewidth=1.0, zorder=2)

    anos_marco = sorted({ANO_INI, 2001, 2010, 2020, ANO_FIM})
    for chave in ("fogo_veg", "conv_vp"):
        rotulo, cor = FLUXOS[chave]
        g = cent[cent.fluxo == chave].sort_values("ano")
        ax.plot(g["x_mean"], g["y_mean"], "-", color=cor, lw=1.8, alpha=0.9,
                zorder=4, label=rotulo)
        gi = g.set_index("ano")
        for a in anos_marco:
            if a in gi.index:
                ax.scatter([gi.loc[a, "x_mean"]], [gi.loc[a, "y_mean"]], s=48,
                           color="white", edgecolors=cor, linewidths=1.8, zorder=6)
                ax.annotate(str(a), (gi.loc[a, "x_mean"], gi.loc[a, "y_mean"]),
                            textcoords="offset points", xytext=(6, 4),
                            fontsize=8.5, color=cor, zorder=7)
    # Zoom na bbox das duas trajetórias.
    sub = cent[cent.fluxo.isin(["fogo_veg", "conv_vp"])]
    xs, ys = sub["x_mean"], sub["y_mean"]
    mx = (xs.max() - xs.min()) * 0.35 + 8000
    my = (ys.max() - ys.min()) * 0.35 + 8000
    ax.set_xlim(xs.min() - mx, xs.max() + mx)
    ax.set_ylim(ys.min() - my, ys.max() + my)
    ax.set_title("Trajetória dos centroides 1985→2023 — fogo em veg natural vs "
                 "conversão veg→pasto\n(○ marcos; o fogo fica ao norte?)",
                 fontsize=11.5, loc="left")
    ax.legend(loc="lower left", frameon=True, fontsize=10)
    ax.set_aspect("equal"); ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "mapa_trajetorias.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'mapa_trajetorias.png').relative_to(ROOT)}")


def fig_leadlag(d: pd.DataFrame, painel_res: pd.DataFrame) -> None:
    """Dois painéis: (esq) CCF agregado Δlat fogo_veg × Δlat conv; (dir) coefs do
    distributed-lag local (modelo A: fogo lidera conversão)."""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Esq: CCF agregado.
    ax = axes[0]
    ccf = ccf_defasada(d["fogo_veg"].to_numpy(), d["conv_vp"].to_numpy(), MAX_LAG)
    cores = ["#d84315" if l > 0 else "0.7" for l in ccf["lag"]]
    ax.bar(ccf["lag"], ccf["r"], color=cores)
    ax.axhline(0, color="0.3", lw=0.8); ax.axvline(0, color="0.5", lw=0.8, ls=":")
    ax.set_title("Agregado: Δlat(fogo veg) × Δlat(conversão)", fontsize=11)
    ax.set_xlabel("defasagem k  (k>0 ⇒ fogo ANTECEDE)")
    ax.set_ylabel("correlação cruzada r")
    ax.grid(True, axis="y", alpha=0.25)

    # Dir: perfil distributed-lag local (modelo A: t-2..t+2).
    ax = axes[1]
    a = painel_res[painel_res.modelo.str.startswith("A)")].copy()
    ordem = ["z_fogo_veg_lag2", "z_fogo_veg_lag1", "z_fogo_veg",
             "z_fogo_veg_lead1", "z_fogo_veg_lead2"]
    rotk = {"z_fogo_veg_lag2": "t−2\nlidera", "z_fogo_veg_lag1": "t−1\nlidera",
            "z_fogo_veg": "t\ncontemp.", "z_fogo_veg_lead1": "t+1\nplacebo",
            "z_fogo_veg_lead2": "t+2\nplacebo"}
    a = a.set_index("termo").loc[ordem].reset_index()
    x = np.arange(len(a))
    cores = ["#d84315" if (t.startswith("z_fogo_veg_lag") or t == "z_fogo_veg")
             else "#9e9e9e" for t in a["termo"]]
    cores = [c if p < 0.05 else "0.75" for c, p in zip(cores, a["p"])]
    ax.bar(x, a["beta"], yerr=1.96 * a["se"], color=cores, capsize=4, zorder=3)
    ax.axhline(0, color="0.3", lw=0.9)
    ax.axvspan(-0.5, 1.5, color="#d84315", alpha=0.05, zorder=0)
    ax.text(0.5, ax.get_ylim()[1] * 0.92, "fogo lidera", color="#d84315",
            fontsize=9, ha="center", style="italic")
    for i, r in a.iterrows():
        ax.text(i, r["beta"] + 0.004, f"{r['beta']:+.3f}\np={r['p']:g}",
                ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([rotk[t] for t in a["termo"]], fontsize=9)
    ax.set_title("Local (AMC, 2-way FE): conv(t) ~ fogo em veg(t−2..t+2)\n"
                 "perfil DA SPEC BASE — assimetria passado>futuro é FRÁGIL (ver robustez)",
                 fontsize=10.5)
    ax.set_ylabel("β (z-score, IC95% clusterizado)")
    ax.grid(True, axis="y", alpha=0.25)

    fig.suptitle("O fogo lidera a conversão NO TEMPO? Agregado nulo (esq); local positivo "
                 "mas simétrico/frágil (dir)", fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(DIR_OUT / "leadlag.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'leadlag.png').relative_to(ROOT)}")


def fig_pulso(tab: pd.DataFrame, serie: pd.DataFrame) -> None:
    """Teste focal 2001–05: (esq) série anual fogo_veg vs declínio do estoque de
    veg, normalizadas — o pulso de perda NÃO é um pulso de fogo; (dir) razões
    2001-05/2006-19 (fogo plano × perda 3×) + share veg→agric por janela."""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Esq: séries anuais normalizadas pela média 1990-2000.
    ax = axes[0]
    s = serie.dropna().copy()
    base_f = s.loc[s.ano <= 2000, "fogo_veg"].mean()
    base_l = s.loc[s.ano <= 2000, "declinio_estoque"].mean()
    ax.axvspan(2000.5, 2005.5, color="#6a1b9a", alpha=0.10, zorder=0)
    ax.text(2003, ax.get_ylim()[1], "sub-fase\n2001–05 (#29)", ha="center", va="top",
            fontsize=9, color="#6a1b9a")
    ax.plot(s["ano"], s["declinio_estoque"] / base_l, "-o", color="#6a1b9a", lw=2,
            ms=4, label="declínio do estoque de veg (perda)")
    ax.plot(s["ano"], s["fogo_veg"] / base_f, "-s", color="#d84315", lw=2, ms=4,
            label="fogo em veg natural")
    ax.axhline(1, color="0.5", lw=0.8, ls=":")
    ax.set_xlabel("Ano"); ax.set_ylabel("índice (média 1990–2000 = 1)")
    ax.set_title("O pulso de perda de veg de 2001–05 é um pulso de FOGO?\n"
                 "perda cai ~40% em 2006; fogo NÃO acompanha → desacople temporal",
                 fontsize=10.5, loc="left")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.25)

    # Dir: composição (share veg→agric) por janela.
    ax = axes[1]
    t = tab.copy()
    x = np.arange(len(t))
    ax.bar(x, t["share_veg_agric_pct"], color="#c2185b", alpha=0.85, zorder=3)
    for i, r in t.iterrows():
        ax.text(i, r["share_veg_agric_pct"] + 0.1, f"{r['share_veg_agric_pct']:.1f}%",
                ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(t["janela"], fontsize=9)
    ax.set_ylabel("veg→agricultura (% da perda de veg)")
    ax.set_title("Composição: a fatia de conversão DIRETA veg→agric\n"
                 "dobra em 2001–05 = onset da soja mecanizada (clareira sem fogo)",
                 fontsize=10.5, loc="left")
    ax.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Teste focal — a sub-fase 2001–05 foi demanda/mecanização, não fogo "
                 "(reforça o #41)", fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(DIR_OUT / "pulso_2001_05.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'pulso_2001_05.png').relative_to(ROOT)}")


def fig_robustez(rob: pd.DataFrame) -> None:
    """Soma dos coefs PASSADO (fogo lidera) vs FUTURO (placebo) por especificação.
    Se 'passado>futuro' só vale na base, a liderança local NÃO é robusta."""
    import matplotlib.pyplot as plt
    rotspec = {"base": "base\n(z, ent)", "cl_dupl": "cluster\nduplo",
               "log1p": "log1p\n(doma cauda)", "sem_seca": "sem seca\n1985/2010",
               "ato2_3": "só 2001–23"}
    r = rob.copy()
    x = np.arange(len(r)); w = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(x - w / 2, r["soma_passado"], w, color="#d84315", label="Σ passado (fogo lidera)")
    ax.bar(x + w / 2, r["soma_futuro"], w, color="#9e9e9e", label="Σ futuro (placebo)")
    ax.axhline(0, color="0.3", lw=0.9)
    for i, row in r.reset_index().iterrows():
        lead_ok = (row["p_t-1"] < 0.05) and row["passado_lidera"]
        marca = "lead\nsig" if lead_ok else ("inverte" if not row["passado_lidera"]
                                             else "t−1\nn.s.")
        cor = "#2e7d32" if lead_ok else "#b71c1c"
        ax.text(i, max(row["soma_passado"], row["soma_futuro"]) + 0.012,
                marca, ha="center", va="bottom", fontsize=8.5, color=cor, fontweight="bold")
        ax.text(i, -0.02, f"t−1 p={row['p_t-1']:g}", ha="center", va="top",
                fontsize=7.5, color="0.35")
    ax.set_xticks(x); ax.set_xticklabels([rotspec[s] for s in r["spec"]], fontsize=9)
    ax.set_ylabel("soma dos β do fogo em veg")
    ax.set_title("Robustez da liderança LOCAL: passado (lidera) vs futuro (placebo)\n"
                 "lead t−1 significativo só na base (mesma amostra) — colapsa sob log1p, "
                 "inverte sem os anos de seca ⇒ liderança FRÁGIL; co-elevação é o robusto",
                 fontsize=10.5, loc="left")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "robustez_leadlag.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'robustez_leadlag.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #41 — o fogo lidera a marcha ao norte?")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #41 — O fogo lidera a marcha ao norte? (fogo × conversão veg→pasto)")
    print("=" * 70)

    painel, _ = carregar()
    cent = centroides_anuais(painel)
    cent.to_csv(DIR_PROC / "fogo_fronteira_centroides.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_centroides.csv ({len(cent)} linhas)")

    desloc, off = deslocamento_e_offset(cent)
    desloc.to_csv(DIR_PROC / "fogo_fronteira_deslocamento.csv", index=False, encoding="utf-8")
    off.to_csv(DIR_PROC / "fogo_fronteira_offset.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_deslocamento.csv ({len(desloc)} linhas)")
    print(f"[OK] fogo_fronteira_offset.csv ({len(off)} anos)")

    leadlag, d = leadlag_agregado(cent)
    leadlag.to_csv(DIR_PROC / "fogo_fronteira_leadlag.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_leadlag.csv ({len(leadlag)} linhas)")

    painel_res = painel_precedencia(painel)
    painel_res.to_csv(DIR_PROC / "fogo_fronteira_painel.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_painel.csv ({len(painel_res)} linhas)")

    rob = robustez_leadlag(painel)
    rob.to_csv(DIR_PROC / "fogo_fronteira_robustez.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_robustez.csv ({len(rob)} specs)")

    pulso_tab, pulso_raz, pulso_serie = pulso_2001_05()
    pulso_tab.to_csv(DIR_PROC / "fogo_fronteira_pulso2001.csv", index=False, encoding="utf-8")
    print(f"[OK] fogo_fronteira_pulso2001.csv ({len(pulso_tab)} janelas)")

    # ---- Resumo na tela ----
    print("\n[1] Deslocamento N–S líquido 1985→2023 (km; + = norte):")
    liq = desloc[desloc.periodo == "LÍQUIDO"]
    for _, r in liq.iterrows():
        seta = "↑N" if r["dnorte_km"] > 0 else "↓S"
        print(f"    {r['rotulo']:24s} ΔN={r['dnorte_km']:+7.1f} km {seta} | "
              f"ΔL={r['dleste_km']:+6.1f} km | azimute {r['azimute_deg']:5.1f}°")

    print(f"\n[2] Offset espacial lat(fogo_veg)−lat(conv):  "
          f"média {off['offset_norte_km'].mean():+.1f} km | "
          f"anos fogo-ao-norte: {(off['offset_norte_km'] > 0).sum()}/{len(off)}")

    print("\n[3] Lead-lag AGREGADO (Δlat; k>0 ⇒ fogo antecede):")
    for rel, sub in leadlag.groupby("relacao", sort=False):
        r = sub.iloc[0]
        ps = ", ".join(f"lag{int(g.granger_lag)} p={g.granger_p}" for _, g in sub.iterrows())
        print(f"    {rel:42s} pico CCF lag={r.ccf_lag_pico:+d} r={r.ccf_r_pico:+.2f} | Granger {ps}")

    print("\n[4] Painel LOCAL (AMC, 2-way FE; β z-score, p clusterizado):")
    for modelo, sub in painel_res.groupby("modelo", sort=False):
        print(f"    {modelo}  [n={sub.iloc[0].n}, R²w={sub.iloc[0].r2w}]")
        for _, r in sub.iterrows():
            sig = "*" if r["p"] < 0.05 else " "
            print(f"        {r['termo']:24s} β={r['beta']:+.4f} (p={r['p']:.4f}) {sig}")

    print("\n[5] ROBUSTEZ da liderança local (Σpassado vs Σfuturo; lead = t−1 sig E passado>futuro):")
    for _, r in rob.iterrows():
        lead_ok = (r["p_t-1"] < 0.05) and r["passado_lidera"]
        marca = "← lead sig" if lead_ok else ("✗ INVERTE" if not r["passado_lidera"]
                                              else "(t−1 n.s.)")
        print(f"    {r['spec']:9s} Σpass={r['soma_passado']:+.3f} Σfut={r['soma_futuro']:+.3f} "
              f"| t−1 β={r['beta_t-1']:+.3f} (p={r['p_t-1']:.3f}) {marca}")
    n_dir  = int(rob["passado_lidera"].sum())
    n_lead = int(((rob["p_t-1"] < 0.05) & rob["passado_lidera"]).sum())
    # contemporâneo (t0) sig nas specs de período completo (proxy da co-elevação robusta)
    n_t0   = int((rob["p_t0"] < 0.05).sum())
    print(f"    → direção passado>futuro em {n_dir}/{len(rob)}; lead t−1 SIG em apenas "
          f"{n_lead}/{len(rob)} (mesma amostra); t0 sig em {n_t0}/{len(rob)}.")
    print(f"    VEREDITO: co-elevação fogo↔conversão ROBUSTA; liderança temporal "
          f"{'ROBUSTA' if n_lead >= 4 else 'FRÁGIL (não estabelecida)'}.")

    print("\n[6] Teste focal — a sub-fase 2001–05 (#29) foi um pulso de FOGO?")
    for _, r in pulso_raz.iterrows():
        print(f"    {r['metrica']:26s} 2001-05={r['v_2001_05']:.3f}  2006-19={r['v_2006_19']:.3f}  "
              f"razão={r['razao_01_05_sobre_06_19']:.2f}×")
    g = pulso_tab.set_index("janela")
    print(f"    composição veg→agric: 01-05={g.loc['2001-2005','share_veg_agric_pct']:.1f}% "
          f"vs 06-19={g.loc['2006-2019','share_veg_agric_pct']:.1f}% (onset soja direta)")
    print(f"    acoplamento espacial fogo×perda (Spearman): "
          f"01-05={g.loc['2001-2005','spearman_fogo_perda']:.2f} (co-localização estrutural, todas janelas ~0,85)")
    print("    → perda ~3× mas FOGO PLANO (1,1×) ⇒ pulso é DEMANDA/MECANIZAÇÃO (soja), não fogo.")

    if not args.sem_figuras:
        print()
        fig_latitude(cent)
        fig_offset(off)
        fig_mapa(cent)
        fig_leadlag(d, painel_res)
        fig_robustez(rob)
        fig_pulso(pulso_tab, pulso_serie)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #41. Item 4 do backlog (fogo × fronteira Sul→Norte).")
    print("=" * 70)


if __name__ == "__main__":
    main()
