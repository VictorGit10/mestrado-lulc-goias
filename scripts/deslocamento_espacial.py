"""
Pipeline #34 — Deslocamento Sul→Norte: lead-lag + spillover espacial (Camada 3)
==============================================================================

PERGUNTA QUE RESPONDE
---------------------
As Camadas 1 (#32, centro de massa) e 2 (#33, mecanismo de transições) mostraram
uma COINCIDÊNCIA espacial: a agricultura avança no Sul e o pasto/rebanho no Norte.
A Camada 3 faz o teste FORMAL de deslocamento (iLUC intra-estadual):

  (A) TEMPORAL — a expansão da agricultura no SUL *antecede* o avanço de
      pasto/rebanho no NORTE? (lead-lag: CCF + Granger, com teste reverso)
  (B) ESPACIAL — a agricultura dos VIZINHOS AO SUL prevê o crescimento de
      pasto/rebanho LOCAL? (SLX em painel com efeitos fixos, peso direcional)

DECISÃO DE JANELA (conversado 2026-06-06): TEMPO CONTÍNUO. Roda sobre o painel
anual (AMC, #25), com defasagens — NÃO bina por ato. Os atos entram só como
interação de robustez (o efeito se concentra no período recente?). Isso evita a
circularidade de definir períodos a partir de transições (#29c) e depois usá-los
para analisar transições.

LIMITAÇÃO HONESTA: não promete causalidade dura. Granger é precedência preditiva
(N pequeno → baixo poder); o SLX é associação espacial condicional a FE. Juntos,
são evidência CONSISTENTE com deslocamento, não prova de causa.

ENTRADAS
    data/processed/painel_amc_goias.parquet   (#25, níveis)
    data/processed/taxas_lulc_amc.csv         (#25/#17, deltas)
    data/processed/amc_crosswalk_goias.csv    (#25, cd_mun→code_amc)
    data/processed/mapeamento_mesorregioes.csv(#18, cd_mun→meso)
    data/processed/amc_goias.gpkg             (#25, geometria p/ vizinhança)

SAÍDAS (Parte A; Parte B adicionada em seguida)
    data/processed/deslocamento_series_regionais.csv  (séries Sul/Norte por ano)
    data/processed/deslocamento_leadlag.csv           (CCF + Granger)
    outputs/deslocamento/shares_regionais.png         (shares Sul/Norte no tempo)
    outputs/deslocamento/leadlag_ccf.png              (CCF ΔAgric_Sul × Δ_Norte)

COMO RODAR
    python scripts/deslocamento_espacial.py

Depende de: #25, #17, #18. Reusa convenções de #22 (painel) e #24 (espacial).
Quando foi feito: 2026-06-06. Camada 3 da narrativa de deslocamento Sul→Norte.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "deslocamento"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# Recorte regional para o lead-lag (coerente com #33).
MESO_SUL   = ["Sul Goiano"]
MESO_NORTE = ["Norte Goiano", "Noroeste Goiano"]

MAX_LAG = 5   # defasagens da CCF


# ---------------------------------------------------------------------------
# 1. Recorte regional das AMCs
# ---------------------------------------------------------------------------

def amc_para_meso() -> pd.DataFrame:
    """code_amc → mesorregião modal (entre os municípios-membro) + latitude do
    centroide (EPSG:5880, para o peso direcional da Parte B)."""
    cw   = pd.read_csv(DIR_PROC / "amc_crosswalk_goias.csv")
    meso = pd.read_csv(DIR_PROC / "mapeamento_mesorregioes.csv")[["cd_mun", "nm_meso"]]
    cw = cw.merge(meso, on="cd_mun", how="left")
    modal = (cw.dropna(subset=["nm_meso"])
               .groupby("code_amc")["nm_meso"]
               .agg(lambda s: s.value_counts().idxmax())
               .rename("nm_meso").reset_index())

    import geopandas as gpd
    g = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(5880)
    g["code_amc"] = g["code_amc"].astype(int)
    cent = g.geometry.centroid
    lat = pd.DataFrame({"code_amc": g["code_amc"].to_numpy(),
                        "cx": cent.x.to_numpy(), "cy": cent.y.to_numpy()})
    return modal.merge(lat, on="code_amc", how="left")


# ---------------------------------------------------------------------------
# 2. Séries regionais agregadas (níveis → Mha / milhões de cab.)
# ---------------------------------------------------------------------------

def series_regionais(reg: pd.DataFrame) -> pd.DataFrame:
    """Totais anuais por região (Sul / Norte) das variáveis-chave."""
    painel = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")[
        ["code_amc", "ano", "lulc_agricultura_ha", "lulc_pastagem_ha", "pec_bovinos_cab"]]
    painel = painel.merge(reg[["code_amc", "nm_meso"]], on="code_amc", how="left")

    def regiao(m):
        if m in MESO_SUL:   return "Sul"
        if m in MESO_NORTE: return "Norte"
        return "Centro"
    painel["regiao"] = painel["nm_meso"].map(regiao)

    agg = (painel.groupby(["regiao", "ano"]).agg(
                agric_mha=("lulc_agricultura_ha", lambda s: s.sum() / 1e6),
                pasto_mha=("lulc_pastagem_ha",    lambda s: s.sum() / 1e6),
                bovinos_mcab=("pec_bovinos_cab",  lambda s: s.sum() / 1e6))
           .reset_index())

    # Pivot para série larga: agric_Sul, pasto_Norte, bovinos_Norte, etc.
    wide = agg.pivot(index="ano", columns="regiao")
    wide.columns = [f"{v}_{r}" for v, r in wide.columns]
    wide = wide.reset_index()

    # Shares estaduais (para o gráfico descritivo).
    tot_agric = agg.groupby("ano")["agric_mha"].sum()
    tot_pasto = agg.groupby("ano")["pasto_mha"].sum()
    tot_bov   = agg.groupby("ano")["bovinos_mcab"].sum()
    wide["share_agric_Sul"]   = wide["agric_mha_Sul"]   / wide["ano"].map(tot_agric)
    wide["share_pasto_Norte"] = wide["pasto_mha_Norte"] / wide["ano"].map(tot_pasto)
    wide["share_bovinos_Norte"] = wide["bovinos_mcab_Norte"] / wide["ano"].map(tot_bov)
    return wide


# ---------------------------------------------------------------------------
# 3. Lead-lag: CCF + Granger
# ---------------------------------------------------------------------------

def ccf_defasada(x: np.ndarray, y: np.ndarray, max_lag: int) -> pd.DataFrame:
    """Correlação cruzada corr(x_{t-k}, y_t) para k = -max_lag..+max_lag.
    k>0 = x ANTECEDE y (x lidera)."""
    linhas = []
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            xa, ya = x[:len(x) - k], y[k:]
        else:
            xa, ya = x[-k:], y[:len(y) + k]
        if len(xa) > 3:
            r = np.corrcoef(xa, ya)[0, 1]
            linhas.append({"lag": k, "r": round(float(r), 3), "n": len(xa)})
    return pd.DataFrame(linhas)


def granger(x: pd.Series, y: pd.Series, maxlag: int = 2) -> list[dict]:
    """Testa se x Granger-causa y (x ajuda a prever y além do passado de y).
    Retorna p-valor por lag. N pequeno → interpretar com cautela."""
    from statsmodels.tsa.stattools import grangercausalitytests
    data = np.column_stack([y.to_numpy(), x.to_numpy()])  # ordem: [y, x] testa x→y
    out = []
    try:
        res = grangercausalitytests(data, maxlag=maxlag, verbose=False)
        for lag in range(1, maxlag + 1):
            p = res[lag][0]["ssr_ftest"][1]
            out.append({"lag": lag, "p_valor": round(float(p), 4)})
    except Exception as e:  # noqa: BLE001
        out.append({"lag": -1, "p_valor": np.nan, "erro": str(e)})
    return out


def rodar_leadlag(wide: pd.DataFrame) -> pd.DataFrame:
    """ΔAgric_Sul → ΔPasto_Norte e ΔBovinos_Norte (+ testes reversos)."""
    df = wide.sort_values("ano").copy()
    for c in ["agric_mha_Sul", "pasto_mha_Norte", "bovinos_mcab_Norte"]:
        df[f"d_{c}"] = df[c].diff()
    d = df.dropna(subset=["d_agric_mha_Sul", "d_pasto_mha_Norte", "d_bovinos_mcab_Norte"])

    pares = [
        ("d_agric_mha_Sul", "d_pasto_mha_Norte",     "ΔAgric_Sul → ΔPasto_Norte"),
        ("d_agric_mha_Sul", "d_bovinos_mcab_Norte",  "ΔAgric_Sul → ΔBovinos_Norte"),
        # reversos (placebo direcional)
        ("d_pasto_mha_Norte", "d_agric_mha_Sul",     "ΔPasto_Norte → ΔAgric_Sul (reverso)"),
        ("d_bovinos_mcab_Norte", "d_agric_mha_Sul",  "ΔBovinos_Norte → ΔAgric_Sul (reverso)"),
    ]
    linhas = []
    for xcol, ycol, rotulo in pares:
        ccf = ccf_defasada(d[xcol].to_numpy(), d[ycol].to_numpy(), MAX_LAG)
        melhor = ccf.loc[ccf["r"].abs().idxmax()]
        gr = granger(d[xcol], d[ycol], maxlag=2)
        for g in gr:
            linhas.append({"relacao": rotulo,
                           "ccf_lag_pico": int(melhor["lag"]),
                           "ccf_r_pico": melhor["r"],
                           "granger_lag": g["lag"],
                           "granger_p": g["p_valor"]})
    return pd.DataFrame(linhas), d


# ---------------------------------------------------------------------------
# 4. Figuras
# ---------------------------------------------------------------------------

def fig_shares(wide: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(wide["ano"], wide["share_agric_Sul"] * 100, "-", color="#c2185b", lw=2,
            label="Agricultura no Sul (% do estado)")
    ax.plot(wide["ano"], wide["share_pasto_Norte"] * 100, "-", color="#e8920c", lw=2,
            label="Pastagem no Norte+Noroeste (% do estado)")
    ax.plot(wide["ano"], wide["share_bovinos_Norte"] * 100, "-", color="#7a1f1f", lw=2,
            label="Rebanho no Norte+Noroeste (% do estado)")
    ax.set_xlabel("Ano"); ax.set_ylabel("Participação no total estadual (%)")
    ax.set_title("Concentração regional ao longo do tempo (AMC) — montagem do deslocamento",
                 fontsize=12, loc="left")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.25)
    fig.tight_layout(); fig.savefig(DIR_OUT / "shares_regionais.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'shares_regionais.png').relative_to(ROOT)}")


def fig_ccf(d: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    alvos = [("d_pasto_mha_Norte", "ΔPastagem no Norte", "#e8920c"),
             ("d_bovinos_mcab_Norte", "ΔRebanho no Norte", "#7a1f1f")]
    for ax, (ycol, rot, cor) in zip(axes, alvos):
        ccf = ccf_defasada(d["d_agric_mha_Sul"].to_numpy(), d[ycol].to_numpy(), MAX_LAG)
        cores = ["#2e7d32" if l > 0 else "0.7" for l in ccf["lag"]]
        ax.bar(ccf["lag"], ccf["r"], color=cores)
        ax.axhline(0, color="0.3", lw=0.8); ax.axvline(0, color="0.5", lw=0.8, ls=":")
        ax.set_title(f"ΔAgric_Sul × {rot}", fontsize=11, color=cor)
        ax.set_xlabel("defasagem k  (k>0 ⇒ agricultura do Sul ANTECEDE)")
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylabel("correlação cruzada r")
    fig.suptitle("Lead-lag: a agricultura do Sul antecede pasto/rebanho do Norte? "
                 "(verde = agricultura lidera)", fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(DIR_OUT / "leadlag_ccf.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'leadlag_ccf.png').relative_to(ROOT)}")


def fig_slx(slx: pd.DataFrame) -> None:
    """Coeficiente do termo de VIZINHANÇA (W·Δagric) por modelo, com IC95%. O
    deslocamento previa θ>0 (faixa verde); os dados ficam em ~0 ou negativos."""
    import matplotlib.pyplot as plt
    viz = slx[slx.termo.str.startswith("Wagric")].copy()
    viz["rotulo"] = viz["modelo"].str.replace(r" \(placebo\)", " [placebo]", regex=True)
    viz = viz.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(viz))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axvspan(0, viz["beta"].max() + 0.4, color="#2e7d32", alpha=0.06)
    ax.text(0.55, 1.6, "região prevista\npelo deslocamento (θ>0)", color="#2e7d32",
            fontsize=9, ha="center", style="italic")
    for i, r in viz.iterrows():
        cor = "#c2185b" if r["p"] < 0.05 else "0.5"
        ax.errorbar(r["beta"], i, xerr=1.96 * r["se"], fmt="o", color=cor,
                    capsize=4, ms=7)
        ax.text(r["beta"], i + 0.18, f"β={r['beta']:+.3f} (p={r['p']:g})",
                ha="center", fontsize=8.5, color=cor)
    ax.axvline(0, color="0.3", lw=1)
    ax.set_yticks(y); ax.set_yticklabels(viz["rotulo"], fontsize=9)
    ax.set_xlabel("β do termo de vizinhança W·Δagric (painel 2-way FE, IC95%)")
    ax.set_title("Teste espacial de deslocamento: agricultura dos vizinhos ao sul\n"
                 "prevê crescimento local de pasto/rebanho? (θ>0 = sim)", fontsize=12, loc="left")
    fig.tight_layout(); fig.savefig(DIR_OUT / "slx_coeficientes.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'slx_coeficientes.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 5. Parte B — spillover espacial direcional (SLX em painel FE)
# ---------------------------------------------------------------------------

def construir_pesos_direcionais(reg: pd.DataFrame, k: int = 8) -> dict:
    """Matrizes de vizinhança (166×166), linha-padronizadas, sobre os k vizinhos
    mais próximos: W_sul (só vizinhos ao SUL, cy menor), W_norte (placebo) e
    W_todos (agnóstico). Índice = code_amc ordenado."""
    r = reg.dropna(subset=["cx", "cy"]).sort_values("code_amc").reset_index(drop=True)
    codes = r["code_amc"].to_numpy()
    xy = r[["cx", "cy"]].to_numpy()
    n = len(codes)
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    viz = np.argsort(d, axis=1)[:, :k]   # k vizinhos mais próximos de cada i

    def montar(direcao):
        W = np.zeros((n, n))
        for i in range(n):
            for j in viz[i]:
                if direcao == "sul"   and xy[j, 1] >= xy[i, 1]:  continue
                if direcao == "norte" and xy[j, 1] <= xy[i, 1]:  continue
                W[i, j] = 1.0
            s = W[i].sum()
            if s > 0:
                W[i] /= s
        return W

    return {"codes": codes,
            "sul":   montar("sul"),
            "norte": montar("norte"),
            "todos": montar("todos")}


def spatial_lag(valores: pd.DataFrame, W: np.ndarray, codes: np.ndarray,
                col: str, novo: str) -> pd.DataFrame:
    """Wx por ano: para cada ano, multiplica W pelo vetor de `col` (ordenado por
    codes). Retorna (code_amc, ano, novo)."""
    piv = valores.pivot(index="code_amc", columns="ano", values=col).reindex(codes)
    M = piv.to_numpy(float)
    M = np.nan_to_num(M, nan=0.0)
    WM = W @ M
    out = pd.DataFrame(WM, index=codes, columns=piv.columns)
    return out.reset_index(names="code_amc").melt(
        id_vars="code_amc", var_name="ano", value_name=novo)


def rodar_slx(reg: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    """SLX em painel 2-way FE: Δpasto/Δbovinos local ~ Δagric local + W·Δagric
    (vizinhos). θ>0 em W_sul = agricultura dos vizinhos AO SUL prevê crescimento
    local de pasto/rebanho = assinatura de deslocamento espacial."""
    from linearmodels.panel import PanelOLS

    taxas = pd.read_csv(DIR_PROC / "taxas_lulc_amc.csv")[
        ["code_amc", "ano", "agricultura_delta_mha", "pastagem_delta_mha"]]
    pan = pd.read_parquet(DIR_PROC / "painel_amc_goias.parquet")[
        ["code_amc", "ano", "pec_bovinos_cab"]].sort_values(["code_amc", "ano"])
    pan["bovinos_delta_mcab"] = pan.groupby("code_amc")["pec_bovinos_cab"].diff() / 1e6
    df = taxas.merge(pan[["code_amc", "ano", "bovinos_delta_mcab"]], on=["code_amc", "ano"])

    codes = pesos["codes"]
    for nome, W in [("sul", pesos["sul"]), ("norte", pesos["norte"]), ("todos", pesos["todos"])]:
        wl = spatial_lag(taxas, W, codes, "agricultura_delta_mha", f"Wagric_{nome}")
        df = df.merge(wl, on=["code_amc", "ano"], how="left")

    df = df.dropna(subset=["pastagem_delta_mha", "agricultura_delta_mha",
                           "bovinos_delta_mcab", "Wagric_sul"])
    df = df.set_index(["code_amc", "ano"])

    specs = [
        ("pastagem_delta_mha",  ["agricultura_delta_mha", "Wagric_sul"],   "Δpasto ~ Δagric + Wsul·Δagric"),
        ("pastagem_delta_mha",  ["agricultura_delta_mha", "Wagric_norte"], "Δpasto ~ Δagric + Wnorte·Δagric (placebo)"),
        ("pastagem_delta_mha",  ["agricultura_delta_mha", "Wagric_todos"], "Δpasto ~ Δagric + Wtodos·Δagric"),
        ("bovinos_delta_mcab",  ["agricultura_delta_mha", "Wagric_sul"],   "Δbovinos ~ Δagric + Wsul·Δagric"),
        ("bovinos_delta_mcab",  ["agricultura_delta_mha", "Wagric_norte"], "Δbovinos ~ Δagric + Wnorte·Δagric (placebo)"),
    ]
    linhas = []
    for y, xs, rotulo in specs:
        mod = PanelOLS(df[y], df[xs], entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        for x in xs:
            linhas.append({"modelo": rotulo, "y": y, "termo": x,
                           "beta": round(res.params[x], 5),
                           "se": round(res.std_errors[x], 5),
                           "p": round(res.pvalues[x], 4),
                           "n": int(res.nobs), "r2w": round(res.rsquared_within, 4)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #34 — Camada 3 (lead-lag + spillover)")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #34 — Deslocamento Sul→Norte: lead-lag + spillover (Camada 3)")
    print("Janela: TEMPO CONTÍNUO (painel anual AMC, com defasagens)")
    print("=" * 70)

    reg = amc_para_meso()
    n_sul = (reg.nm_meso.isin(MESO_SUL)).sum()
    n_norte = (reg.nm_meso.isin(MESO_NORTE)).sum()
    print(f"[regiões] {n_sul} AMCs no Sul | {n_norte} no Norte+Noroeste | "
          f"{len(reg)-n_sul-n_norte} no Centro/Leste")

    wide = series_regionais(reg)
    wide.to_csv(DIR_PROC / "deslocamento_series_regionais.csv", index=False, encoding="utf-8")
    print(f"[OK] deslocamento_series_regionais.csv ({len(wide)} anos)")

    leadlag, d = rodar_leadlag(wide)
    leadlag.to_csv(DIR_PROC / "deslocamento_leadlag.csv", index=False, encoding="utf-8")
    print(f"[OK] deslocamento_leadlag.csv ({len(leadlag)} linhas)\n")

    print("[lead-lag] CCF (pico) + Granger (p por lag):")
    for rel, sub in leadlag.groupby("relacao"):
        r = sub.iloc[0]
        ps = ", ".join(f"lag{int(g.granger_lag)} p={g.granger_p}" for _, g in sub.iterrows())
        print(f"  {rel:40s} pico CCF: lag={r.ccf_lag_pico:+d} r={r.ccf_r_pico:+.2f} | Granger: {ps}")

    # ---- Parte B — spillover espacial direcional ----
    print("\n[Parte B] SLX em painel 2-way FE (vizinhos ao sul vs placebo norte):")
    pesos = construir_pesos_direcionais(reg, k=8)
    slx = rodar_slx(reg, pesos)
    slx.to_csv(DIR_PROC / "deslocamento_slx.csv", index=False, encoding="utf-8")
    for modelo, sub in slx.groupby("modelo", sort=False):
        termos = " | ".join(
            f"{r.termo}: β={r.beta:+.4f} (p={r.p})" for _, r in sub.iterrows())
        print(f"  {modelo}\n      {termos}  [n={sub.iloc[0].n}, R²w={sub.iloc[0].r2w}]")
    print(f"\n[OK] deslocamento_slx.csv ({len(slx)} linhas)")

    if not args.sem_figuras:
        print()
        fig_shares(wide)
        fig_ccf(d)
        fig_slx(slx)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #34 (Camada 3). Lead-lag + spillover espacial.")
    print("=" * 70)


if __name__ == "__main__":
    main()
