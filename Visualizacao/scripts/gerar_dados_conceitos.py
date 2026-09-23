"""Gera assets/data/conceitos.json — o recorte leve que a página conceitos.html consome.

Só lê: arquivos de data/processed (saídas dos pipelines) e dois JSONs que a própria
visualização já publica (metodo_centro_massa.json, didatica_apresentacao.json).
Nenhum número é digitado aqui; a página faz as contas didáticas no navegador a partir
deste recorte.

    python Visualizacao/scripts/gerar_dados_conceitos.py
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data" / "processed"
VIZ = ROOT / "Visualizacao" / "assets" / "data"


def r(x, n=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), n)


def col(df, c, n=4):
    return [r(v, n) for v in df[c]]


out = {"_fonte": "gerado por Visualizacao/scripts/gerar_dados_conceitos.py — não editar à mão"}

# --- Série estadual por grupo (Mha), régua crua do MapBiomas 10.1 ------------------
a = pd.read_csv(P / "deriva_mosaico_areas.csv").sort_values("ano")
painel = json.loads((VIZ / "painel_goias.json").read_text(encoding="utf-8"))["serie"]
bov = {row["ano"]: row["pec_bovinos_cab"] for row in painel}
soja_t = {row["ano"]: row["agri_soja_ton"] for row in painel}
out["go"] = {
    "anos": a.ano.astype(int).tolist(),
    "pasto": col(a, "pastagem_mha"),
    "agric": col(a, "agricultura_mha"),
    "mosaico": col(a, "mosaico_mha"),
    "veg": col(a, "vegetacao_natural_mha"),
    "bovinos_mi": [r(bov[y] / 1e6, 3) for y in a.ano],
    "soja_sidra_mt": [r((soja_t[y] or np.nan) / 1e6, 3) for y in a.ano],
}
s = pd.read_csv(P / "deriva_mosaico_sidra.csv")
out["soja_sidra_area"] = {"anos": s.ano.astype(int).tolist(), "mha": col(s, "soja_mha")}

# --- Séries regionais (Perna 3) -----------------------------------------------------
g = pd.read_csv(P / "deslocamento_series_regionais.csv").sort_values("ano")
out["reg"] = {"anos": g.ano.astype(int).tolist()}
for c in g.columns:
    if c != "ano":
        out["reg"][c] = col(g, c, 5)

# Vegetação natural por região, a partir dos pesos por AMC já publicados
m = json.loads((VIZ / "metodo_centro_massa.json").read_text(encoding="utf-8"))
apt = pd.read_csv(P / "aptidao_edafo_amc.csv")
reg_por_code = dict(zip(apt.code_amc, apt.regiao))
codes = [x["code"] for x in m["amc"]]
veg = np.array(m["pesos"]["veg_natural"])  # anos × amc
out["veg_reg"] = {"anos": m["anos"]}
for rg in ["Sul", "Centro", "Norte"]:
    idx = [i for i, c in enumerate(codes) if reg_por_code.get(c) == rg]
    out["veg_reg"][rg] = [r(v / 1e6, 4) for v in veg[:, idx].sum(axis=1)]
out["amc_reg"] = [reg_por_code.get(c) for c in codes]

# --- Estacionariedade e Toda-Yamamoto (#42) -----------------------------------------
e = pd.read_csv(P / "granger_reverso_estacionaria.csv")
out["estac"] = [
    {"serie": x.serie, "adf_p": r(x.adf_p), "kpss_p": r(x.kpss_p)}
    for x in e[e.bloco == "estacionariedade"].itertuples()
]
out["ty"] = [
    {"relacao": x.relacao, "p": int(x.p), "ty_p": r(x.ty_p)}
    for x in e[e.bloco == "toda_yamamoto"].itertuples()
]
did = json.loads((VIZ / "didatica_apresentacao.json").read_text(encoding="utf-8"))
out["granger"] = did["empurrao"]["granger"]

# --- Macro: câmbio, preço, crédito ------------------------------------------------------
d = pd.read_csv(P / "drivers_macro_anual.csv").sort_values("ano")
out["macro"] = {
    "anos": d.ano.astype(int).tolist(),
    "cambio": col(d, "cambio_real_efetivo", 2),
    "soja_usd": col(d, "preco_soja_usd", 1),
    "recebido_soja": col(d, "preco_recebido_soja_idx", 2),
    "credito_bi": [r(v / 1e9, 2) for v in d.credito_rural_go_real],
}

# --- Decomposição estoque × taxa (#39) ---------------------------------------------------
f = pd.read_csv(P / "fronteira_decomposicao.csv")
out["decomp"] = json.loads(f.to_json(orient="records", force_ascii=False))

# --- Domínio da depleção (#39B / D29) ----------------------------------------------------
fe = pd.read_csv(P / "fronteira_estoque_convertivel.csv")
x = fe.deplecao_prev.dropna()
out["deplecao"] = {
    "n": int(len(x)),
    "fora": int(((x < 0) | (x > 1)).sum()),
    "min": r(x.min(), 2),
    "max": r(x.max(), 2),
    "dentro_hist": np.histogram(x[(x >= 0) & (x <= 1)], bins=20, range=(0, 1))[0].tolist(),
    "fora_hist_bordas": [-90, -50, -20, -10, -5, -2, -1, -0.5, 0],
    "fora_hist": np.histogram(x[x < 0], bins=[-90, -50, -20, -10, -5, -2, -1, -0.5, 0])[0].tolist(),
    "media": r(x.mean(), 4),
    "dp": r(x.std(), 4),
}

# --- Aptidão, latitude e horse race (#52/#56) -------------------------------------------
out["apt"] = [
    {"code": int(x.code_amc), "score": r(x.apt_score_mean, 3), "expo": r(x.exp_apt_edafo, 4),
     "lat": r(x.lat, 4), "reg": x.regiao}
    for x in apt.itertuples()
]
h = pd.read_csv(P / "drive_horse_race_latitude.csv")
out["horse"] = json.loads(h[["spec", "descricao", "exposicao", "rotulo", "beta", "se",
                             "p_agrupado", "p_circular"]].to_json(orient="records", force_ascii=False))
j = pd.read_csv(P / "perna4_jackknife.csv")
out["jackknife"] = json.loads(j.to_json(orient="records", force_ascii=False))

# --- Carbono (#47 / D30) -------------------------------------------------------------------
c = pd.read_csv(P / "carbono_por_formacao_mcti.csv")
out["carbono"] = [{"formacao": x.formacao, "mha": r(x.area_perdida_Mha), "mtco2": r(x.MtCO2_central, 1)}
                  for x in c.itertuples()]

# --- Idade da pastagem: estatísticas e bimodalidade (#28) --------------------------------
ist = pd.read_csv(P / "idade_pastagem_estatisticas.csv")
out["idade_stats"] = json.loads(ist.to_json(orient="records", force_ascii=False))
out["idade"] = did["idade"]
out["idade_hist"] = json.loads((VIZ / "idade_pastagem_histograma.json").read_text(encoding="utf-8"))

# --- Oscilação pasto ↔ savana (classe bruta) -------------------------------------------
ch = pd.read_csv(P / "checar_transicao_pasto_natural_classe.csv")
osc = []
for (o, dd), sub in ch.groupby(["ano_origem", "ano_destino"]):
    get = lambda a_, b_: float(sub[(sub.classe_orig == a_) & (sub.classe_dest == b_)].area_ha.sum())
    osc.append({"ini": int(o), "fim": int(dd),
                "sav_pasto": r(get(4, 15), 0), "pasto_sav": r(get(15, 4), 0),
                "pasto_flo": r(get(15, 3), 0), "pasto_campo": r(get(15, 12), 0)})
out["oscilacao"] = osc

# --- Fluxo bruto × líquido por ato -------------------------------------------------------
fb = pd.read_csv(P / "fluxo_bruto_liquido.csv")
out["fluxo_bl"] = json.loads(fb.to_json(orient="records", force_ascii=False))

# --- Empurrão: FWL (substituição local e vizinhança) -------------------------------------
fw = did["empurrao"]["fwl"]
# nuvem inteira: as caudas pesam na inclinação, e uma subamostra não reproduz θ nem β
out["fwl"] = {k: fw[k] for k in ("theta", "beta_local", "n", "n_amc", "n_ano", "x", "y", "xl", "yl")}
out["vizinhos_sul"] = {str(x["code"]): x["sul"] for x in did["empurrao"]["mapa"]}

dest = VIZ / "conceitos.json"
dest.write_text(json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")
print(f"OK: {dest.relative_to(ROOT)} — {dest.stat().st_size // 1024} KB")
