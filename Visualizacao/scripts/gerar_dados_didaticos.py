"""Dados dos momentos didáticos da apresentação (balança, empurrão, idade, motor).

Nenhum resultado é recalculado por um caminho novo: o script importa a mesma
maquinaria dos pipelines (#34 e o bracket da D26, #28C, #52/#56) e, antes de
gravar, CONFERE cada número contra o CSV oficial. Se algum não bater, para.

O que sai (Visualizacao/assets/data/didatica_apresentacao.json)

  empurrao.mapa     região e vizinhos ao sul de cada AMC (a W_sul do #34, k=8)
  empurrao.exemplo  uma AMC escolhida pelos dados para mostrar a pergunta
  empurrao.fwl      a nuvem AMC-ano do θ: Δpasto e W_sul·Δagric depois de
                    retirar o efeito de cada AMC, de cada ano e da lavoura
                    local (Frisch–Waugh–Lovell). A inclinação da nuvem É o θ
                    publicado (−0,157, régua crua, janela plena)
  empurrao.granger  as séries regionais em 1ª diferença e as duas previsões do
                    teste (só o passado do Norte × + o passado do Sul, lag 1)
  idade             histograma do censo de idades e os ajustes de 1 e 2
                    componentes (mesma rotina do texto: gmm_ponderado)
  motor             câmbio real, aptidão por AMC e latitude (#52/#56)

COMO RODAR
    python Visualizacao/scripts/gerar_dados_didaticos.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DIR_PROC = ROOT / "data" / "processed"
DESTINO = ROOT / "Visualizacao" / "assets" / "data" / "didatica_apresentacao.json"
sys.path.insert(0, str(ROOT / "scripts"))

from deslocamento_espacial import amc_para_meso, construir_pesos_direcionais, spatial_lag, MESO_SUL, MESO_NORTE  # noqa: E402
from deslocamento_bracket import taxas_reguas, series_regionais_reguas  # noqa: E402


EXEMPLO = 16041   # AMC de Acreúna


def confere(nome: str, calculado: float, oficial: float, tol: float = 5e-4) -> None:
    ok = abs(calculado - oficial) <= tol
    print(f"  {'OK ' if ok else 'ERRO'} {nome}: calculado {calculado:.5f} · oficial {oficial:.5f}")
    if not ok:
        raise SystemExit(f"{nome} não bate com o CSV oficial — nada foi gravado.")


def r(v, c=5):
    return None if v is None or not np.isfinite(v) else round(float(v), c)


# ---------------------------------------------------------------------------
def empurrao() -> dict:
    print("[empurrão] W_sul, nuvem do θ e Granger")
    reg = amc_para_meso()
    pesos = construir_pesos_direcionais(reg, k=8)
    codes = pesos["codes"]
    Ws = pesos["sul"]
    reg = reg.set_index("code_amc").loc[codes].reset_index()

    def regiao(m):
        return "Sul" if m in MESO_SUL else "Norte" if m in MESO_NORTE else "Centro"

    mapa = [{"code": int(c), "reg": regiao(m), "sul": [int(codes[j]) for j in np.nonzero(Ws[i])[0]]}
            for i, (c, m) in enumerate(zip(codes, reg["nm_meso"]))]

    # ---- a nuvem do θ (régua crua, janela plena), por Frisch–Waugh–Lovell
    t = taxas_reguas()
    t["x_local"] = t["agric"]
    wl = spatial_lag(t[["code_amc", "ano", "x_local"]].dropna(), Ws, codes, "x_local", "Wx_sul")
    wn = spatial_lag(t[["code_amc", "ano", "x_local"]].dropna(), pesos["norte"], codes, "x_local", "Wx_norte")
    d = (t.merge(wl, on=["code_amc", "ano"]).merge(wn, on=["code_amc", "ano"])
          .dropna(subset=["pastagem_delta_mha", "x_local", "bovinos_delta_mcab", "Wx_sul", "Wx_norte"]))
    n_amc, n_ano = d.code_amc.nunique(), d.ano.nunique()
    assert len(d) == n_amc * n_ano, "painel desbalanceado: a dupla demediação não seria exata"

    def dm(col):   # retira a média de cada AMC e de cada ano (efeitos fixos nos dois sentidos)
        s = d[col]
        return s - d.groupby("code_amc")[col].transform("mean") - d.groupby("ano")[col].transform("mean") + s.mean()

    y, xl, wx = dm("pastagem_delta_mha"), dm("x_local"), dm("Wx_sul")

    def resid(a, b):
        return a - (a @ b) / (b @ b) * b

    ry, rw = resid(y, xl), resid(wx, xl)
    theta = float((ry @ rw) / (rw @ rw))
    ry2, rl = resid(y, wx), resid(xl, wx)
    beta_local = float((ry2 @ rl) / (rl @ rl))
    slx = pd.read_csv(DIR_PROC / "deslocamento_bracket_slx.csv")
    of = slx[(slx.janela == "plena") & (slx.regua == "agric") & (slx.modelo == "Δpasto ~ Δx + Wsul·Δx")]
    confere("θ (vizinhos ao sul → pasto local)", theta, float(of[of.termo == "vizinhanca"].beta.iloc[0]))
    confere("β local (lavoura local → pasto local)", beta_local, float(of[of.termo == "local"].beta.iloc[0]))

    fwl = {"x": [r(v * 1e6, 1) for v in rw], "y": [r(v * 1e6, 1) for v in ry],
           "theta": r(theta), "beta_local": r(beta_local), "n": int(len(d)), "n_amc": int(n_amc), "n_ano": int(n_ano),
           "xl": [r(v * 1e6, 1) for v in rl], "yl": [r(v * 1e6, 1) for v in ry2]}

    # ---- a AMC do exemplo: Acreúna (com Turvelândia). Os vizinhos ao sul incluem Rio Verde
    # e Santa Helena, o núcleo da soja: é onde um empurrão teria de aparecer. Longe do DF
    # (o exemplo anterior, Luziânia, confundia: o DF é um buraco no mapa ao lado dela).
    tot = d.groupby("code_amc").agg(wx=("Wx_sul", "sum"), past=("pastagem_delta_mha", "sum"),
                                    agl=("x_local", "sum")).reset_index()
    tot = tot.merge(pd.DataFrame({"code_amc": codes, "nviz": (Ws > 0).sum(1), "reg": [m["reg"] for m in mapa]}))
    ex = tot[tot.code_amc == EXEMPLO].iloc[0]
    exemplo = {"code": int(ex.code_amc), "d_agric_viz_ha": r(ex.wx * 1e6, 0), "d_pasto_local_ha": r(ex.past * 1e6, 0),
               "d_agric_local_ha": r(ex.agl * 1e6, 0), "nviz_sul": int(ex.nviz)}
    print(f"  exemplo: AMC {exemplo['code']} · {exemplo['nviz_sul']} vizinhos ao sul")

    # ---- Granger: séries regionais (régua crua, plena), lag 1
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import grangercausalitytests
    wide = series_regionais_reguas(reg.reset_index()[["code_amc", "nm_meso"]]).sort_values("ano")
    s = pd.DataFrame({"ano": wide["ano"], "a": wide["agric_Sul"].diff(), "p": wide["pasto_mha_Norte"].diff()}).dropna()
    s["a1"], s["p1"] = s["a"].shift(1), s["p"].shift(1)
    q = s.dropna()
    rest = sm.OLS(q["p"], sm.add_constant(q[["p1"]])).fit()
    irr = sm.OLS(q["p"], sm.add_constant(q[["p1", "a1"]])).fit()
    g = grangercausalitytests(np.column_stack([s["p"], s["a"]]), maxlag=1, verbose=False)
    p_gr = float(g[1][0]["ssr_ftest"][1])
    ll = pd.read_csv(DIR_PROC / "deslocamento_bracket_leadlag.csv")
    ofg = ll[(ll.janela == "plena") & (ll.regua == "agric") & (ll.desfecho == "ΔPasto_Norte") & (ll.granger_lag == 1)]
    confere("Granger ΔAgric_Sul → ΔPasto_Norte, lag 1 (p)", p_gr, float(ofg.granger_p.iloc[0]))
    ty = pd.read_csv(DIR_PROC / "granger_reverso_estacionaria.csv")
    ty = ty[ty.bloco == "toda_yamamoto"]

    granger = {
        "anos": [int(a) for a in s["ano"]],
        "sul": [r(v * 1e3, 1) for v in s["a"]],            # mil ha por ano
        "norte": [r(v * 1e3, 1) for v in s["p"]],
        "anos_fit": [int(a) for a in q["ano"]],
        "prev_so_norte": [r(v * 1e3, 1) for v in rest.fittedvalues],
        "prev_com_sul": [r(v * 1e3, 1) for v in irr.fittedvalues],
        "ssr_so_norte": r(rest.ssr * 1e6, 1), "ssr_com_sul": r(irr.ssr * 1e6, 1),
        "p": r(p_gr, 4), "n": int(len(q)),
        "celulas": ll[["janela", "regua_rotulo", "desfecho", "granger_lag", "granger_p"]].to_dict("records"),
        "ty": [{"dir": x.relacao, "lag": int(x.p), "p": r(x.ty_p, 4)} for x in ty.itertuples()],
    }
    return {"mapa": mapa, "exemplo": exemplo, "fwl": fwl, "granger": granger}


# ---------------------------------------------------------------------------
def idade() -> dict:
    print("[idade] histograma do censo e ajustes de 1 e 2 componentes")
    from estatistica_ponderada import gmm_ponderado
    dd = pd.read_parquet(DIR_PROC / "pastagem_idade_censo.parquet")
    nc = dd[dd.origem_anterior != "censurado_esquerda"]
    ida = nc.groupby("idade_pastagem_anos").n_pixels.sum().sort_index()
    x, w = ida.index.to_numpy(float), ida.to_numpy(float)
    r1, r2 = gmm_ponderado(x, w, n_comp=1), gmm_ponderado(x, w, n_comp=2)
    print(f"  2 componentes: μ = {r2['mu'][0]:.1f} e {r2['mu'][1]:.1f} anos · pesos {r2['peso'][0]:.0%} e {r2['peso'][1]:.0%}")
    comp = lambda res: [{"mu": r(m, 4), "sigma": r(s_, 4), "peso": r(p_, 4)} for m, s_, p_ in zip(res["mu"], res["sigma"], res["peso"])]
    return {"x": [int(v) for v in x], "dens": [r(v, 6) for v in w / w.sum()], "n_eventos": int(w.sum()),
            "um": comp(r1), "dois": comp(r2), "bic1": r(r1["bic"], 1), "bic2": r(r2["bic"], 1)}


# ---------------------------------------------------------------------------
def motor() -> dict:
    print("[motor] câmbio real, aptidão e latitude")
    dr = pd.read_csv(DIR_PROC / "drivers_macro_anual.csv")
    ap = pd.read_csv(DIR_PROC / "aptidao_edafo_amc.csv")
    rr = float(np.corrcoef(ap.exp_apt_edafo, ap.lat)[0, 1])
    confere("corr(aptidão, latitude) do #52", rr, -0.44, tol=0.006)
    hr = pd.read_csv(DIR_PROC / "drive_horse_race_latitude.csv")
    b1 = float(hr[(hr.spec == "S1")].beta.iloc[0])
    b4 = float(hr[(hr.spec == "S4") & (hr.exposicao == "exp_apt_edafo")].beta.iloc[0])
    perda = 1 - b4 / b1
    confere("perda da aptidão com a latitude (D28)", perda, 0.62, tol=0.006)
    return {"anos": [int(a) for a in dr.ano], "cambio": [r(v, 2) for v in dr.cambio_real_efetivo],
            "amc": [{"code": int(a.code_amc), "apt": r(a.exp_apt_edafo, 4), "lat": r(a.lat, 4)} for a in ap.itertuples()],
            "r_apt_lat": r(rr, 3), "beta_s1": r(b1, 4), "beta_s4": r(b4, 4), "perda": r(perda, 3)}


def main() -> None:
    out = {"_fonte": "gerado por Visualizacao/scripts/gerar_dados_didaticos.py — não editar à mão",
           "empurrao": empurrao(), "idade": idade(), "motor": motor()}
    DESTINO.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"[OK] {DESTINO.relative_to(ROOT)} ({DESTINO.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
