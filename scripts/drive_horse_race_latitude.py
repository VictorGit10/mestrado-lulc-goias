"""drive_horse_race_latitude.py -- Pipeline #56: a aptidão sobrevive ao gradiente?
   (corrida de cavalos entre exposições no desenho shift-share do drive comum)
====================================================================================

PERGUNTA QUE RESPONDE
---------------------
O drive comum (#38/#52/#54) estima  Δy_it = α_i + γ_t + β·(Δcâmbio_t × exposição_i).
Com efeito fixo de ano, o nível do choque some e o que resta identificado é o
GRADIENTE: onde o mesmo choque nacional bate mais forte. A exposição escolhida é a
aptidão edafoclimática da Embrapa, defendida por ser física e exógena ao uso da terra.

Exógena, porém, não é o mesmo que ISOLADA. A aptidão correlaciona-se −0,44 com a
latitude, e a latitude organiza quase tudo em Goiás: infraestrutura, idade da
ocupação, distância aos mercados, especialização produtiva. Se o câmbio interage com
QUALQUER gradiente Sul→Norte, o coeficiente da aptidão acende sem que a aptidão seja
o mecanismo. Os placebos já rodados (#54) são de DESFECHO -- urbano e água -- e não
tocam nessa ameaça: eles mostram que o efeito é específico do rebanho, não que a
aptidão seja a share certa.

    O β da interação câmbio × aptidão sobrevive quando o MESMO choque entra
    interagido, ao mesmo tempo, com outros gradientes espaciais candidatos?

É o teste que a régua de latitude (D14) manda aplicar em todo recorte transversal e
que esta frente ainda não tinha recebido.

DESENHO
-------
Três exposições concorrentes, todas z-score sobre as 166 AMCs:
  (1) exp_apt_edafo  -- aptidão física da Embrapa (a do #52; a defendida).
  (2) exp_latitude   -- latitude do centroide da AMC. É o confundidor puro: mede
      "quão ao norte", sem nenhum conteúdo agronômico.
  (3) exp_acesso     -- distância ao núcleo de lavoura de 1985 (centro de massa da
      agricultura no primeiro ano da série). Proxy grosseira de acesso a mercado e
      infraestrutura, construída de dado ANTERIOR a toda a janela de estimação.
      Entra porque "custo logístico" é a explicação rival mais citada na literatura
      de renda da terra (é a metade von Thünen do arcabouço da §2.2), e ela também
      cresce de sul para norte.

Especificações, todas 2FE (entidade+ano), desfecho Δ rebanho bovino, lag 1 (o do #52):
    S1  aptidão sozinha                 (reproduz o #52 -- teste de sanidade)
    S2  latitude sozinha
    S3  acesso sozinho
    S4  aptidão + latitude              (a corrida que importa)
    S5  aptidão + acesso
    S6  aptidão + latitude + acesso     (todas juntas)

Inferência: o SE agrupado é reconhecidamente otimista neste desenho (Adão et al.,
2019; Borusyak et al., 2022), então cada especificação recebe também a permutação
CIRCULAR do shifter (rotação da série de câmbio, exaustiva sobre as T−1 rotações),
que é a régua conservadora adotada no #54. As duas são reportadas lado a lado, e
NUNCA comparadas entre si como se fossem a mesma medida.

O QUE O TESTE NÃO FAZ
---------------------
Não estabelece a aptidão como mecanismo, mesmo que ela sobreviva. Sobreviver a três
rivais é condição necessária, não suficiente: o gradiente verdadeiro pode ser um
quarto, não medido. E o teto de ~38 realizações do shifter continua de pé -- ele
limita o poder de todas as especificações igualmente.

ENTRADAS
    scripts/drive_comum_amc.py            (#38, importado)
    scripts/defensabilidade_perna4.py     (#54, importado: carga estendida + permutação)
    data/processed/aptidao_edafo_amc.csv  (#52)
    data/processed/fronteira_estoque_convertivel.csv (#39: latitude por AMC)
    data/processed/centro_massa_anual.csv (#32: núcleo de lavoura de 1985)
    data/processed/amc_goias.gpkg         (#25: centroides métricos)

SAÍDAS
    data/processed/drive_horse_race_latitude.csv
    outputs/drive_comum/horse_race_latitude.png

COMO RODAR
    py -3.14 scripts/drive_horse_race_latitude.py
    py -3.14 scripts/drive_horse_race_latitude.py --sem-figuras

Depende de: Pipelines #25, #32, #38, #39, #52, #54.
Quando foi feito: 2026-08-19.
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
import drive_comum_amc as d38            # noqa: E402
import defensabilidade_perna4 as p54     # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "drive_comum"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_SAIDA = DIR_PROC / "drive_horse_race_latitude.csv"

DRIVER   = "cambio_real_efetivo"
DESFECHO = "d_bovinos_mcab"
LAG      = 1

EXPO_APT = "exp_apt_edafo"
EXPO_LAT = "exp_latitude"
EXPO_ACE = "exp_acesso"

ROTULOS = {
    EXPO_APT: "Aptidão edafoclim. (Embrapa)",
    EXPO_LAT: "Latitude (confundidor puro)",
    EXPO_ACE: "Distância ao núcleo de lavoura 1985",
}

ESPECIFICACOES = [
    ("S1", [EXPO_APT], "aptidão sozinha (reproduz o #52)"),
    ("S2", [EXPO_LAT], "latitude sozinha"),
    ("S3", [EXPO_ACE], "acesso sozinho"),
    ("S4", [EXPO_APT, EXPO_LAT], "aptidão + latitude"),
    ("S5", [EXPO_APT, EXPO_ACE], "aptidão + acesso"),
    ("S6", [EXPO_APT, EXPO_LAT, EXPO_ACE], "aptidão + latitude + acesso"),
]


def _z(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


# ---------------------------------------------------------------------------
# 1. Exposições rivais
# ---------------------------------------------------------------------------

def exposicoes_rivais() -> pd.DataFrame:
    """Latitude e distância ao núcleo de lavoura de 1985, por AMC (z-score)."""
    import geopandas as gpd

    g = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(5880)
    cen = g.geometry.centroid
    amc = pd.DataFrame({"code_amc": g["code_amc"].astype("int64"),
                        "cx": cen.x.to_numpy(), "cy": cen.y.to_numpy()})

    # Núcleo de lavoura no PRIMEIRO ano da série (anterior a toda a janela estimada).
    cm = pd.read_csv(DIR_PROC / "centro_massa_anual.csv")
    n0 = cm[(cm["variavel"] == "agricultura") & (cm["ano"] == 1985)].iloc[0]
    amc["dist_nucleo_km"] = np.hypot(amc["cx"] - n0["x_mean"],
                                     amc["cy"] - n0["y_mean"]) / 1000.0

    # Latitude: reusa a coluna já publicada pelo #39 (mesma malha de AMC).
    lat = (pd.read_csv(DIR_PROC / "fronteira_estoque_convertivel.csv",
                       usecols=["code_amc", "lat"])
             .drop_duplicates("code_amc"))
    lat["code_amc"] = lat["code_amc"].astype("int64")
    amc = amc.merge(lat, on="code_amc", how="left")

    amc[EXPO_LAT] = _z(amc["lat"])              # maior = mais ao norte
    amc[EXPO_ACE] = _z(amc["dist_nucleo_km"])   # maior = mais longe do núcleo
    return amc[["code_amc", "lat", "dist_nucleo_km", EXPO_LAT, EXPO_ACE]]


def carregar() -> pd.DataFrame:
    df = p54.carregar_estendido()          # traz exp_apt_edafo + interações do #38/#52
    riv = exposicoes_rivais()
    riv["code_amc"] = riv["code_amc"].astype(df["code_amc"].dtype)
    df = df.merge(riv, on="code_amc", how="left")
    for e in (EXPO_LAT, EXPO_ACE):
        df[f"ix__{DRIVER}__{e}__l{LAG}"] = df[f"zd_{DRIVER}_l{LAG}"] * df[e]
    return df


# ---------------------------------------------------------------------------
# 2. Estimação multivariada 2FE
# ---------------------------------------------------------------------------

def rodar_multi(df: pd.DataFrame, y: str, ixs: list[str]) -> dict:
    from linearmodels.panel import PanelOLS

    sub = df[["code_amc", "ano", y, *ixs]].dropna().set_index(["code_amc", "ano"])
    mod = PanelOLS(sub[y], sub[ixs], entity_effects=True, time_effects=True,
                   check_rank=False)
    res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    if not np.isfinite(res.std_errors).all():
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        cluster = "entidade (fallback)"
    else:
        cluster = "entidade+ano"
    return {"res": res, "cluster": cluster, "n_obs": int(res.nobs),
            "n_amc": int(sub.index.get_level_values(0).nunique()),
            "r2_within": float(res.rsquared_within), "sub": sub}


# ---------------------------------------------------------------------------
# 3. Permutação circular do shifter, versão multivariada
# ---------------------------------------------------------------------------
# Mesma lógica do #54: rotaciona a série anual do câmbio (preserva a autocorrelação),
# recomputa TODAS as interações da especificação e reestima o vetor β within. O p de
# cada exposição é a fração de rotações cujo |β| iguala ou supera o observado.

def permutacao_multi(df: pd.DataFrame, y: str, expos: list[str]) -> dict:
    zcol = f"zd_{DRIVER}_l{LAG}"
    sub = df[["code_amc", "ano", y, zcol, *expos]].dropna().copy()

    ent = pd.factorize(sub["code_amc"])[0]
    tim = pd.factorize(sub["ano"])[0]
    ne, nt = int(ent.max() + 1), int(tim.max() + 1)

    ydd = p54._demean2way(sub[y].to_numpy(), ent, tim, ne, nt)
    E = sub[expos].to_numpy()                       # n×p

    anos_ord = np.sort(sub["ano"].unique())
    y2i = {a: i for i, a in enumerate(anos_ord)}
    obs_yi = sub["ano"].map(y2i).to_numpy()
    s_ord = sub.groupby("ano")[zcol].first().reindex(anos_ord).to_numpy()
    T = len(anos_ord)

    def betas(shifter_ord):
        X = shifter_ord[obs_yi][:, None] * E
        Xdd = np.column_stack([p54._demean2way(X[:, j], ent, tim, ne, nt)
                               for j in range(X.shape[1])])
        return np.linalg.lstsq(Xdd, ydd, rcond=None)[0]

    b_real = betas(s_ord)
    nulos = np.array([betas(np.roll(s_ord, k)) for k in range(1, T)])   # (T−1)×p
    p_circ = [(1 + int(np.sum(np.abs(nulos[:, j]) >= abs(b_real[j])))) / T
              for j in range(len(expos))]
    return {"beta_within": b_real, "p_circular": np.array(p_circ), "T": T}


# ---------------------------------------------------------------------------

def main(sem_figuras: bool = False) -> None:
    df = carregar()

    # Correlação entre as exposições: diz se a corrida é separável ou colinear.
    ex = df.groupby("code_amc")[[EXPO_APT, EXPO_LAT, EXPO_ACE]].first().dropna()
    print("\n" + "=" * 78)
    print("CORRELAÇÃO ENTRE AS EXPOSIÇÕES (166 AMCs)")
    print("=" * 78)
    print(ex.corr().round(3).to_string())

    linhas = []
    print("\n" + "=" * 78)
    print(f"CORRIDA DE CAVALOS — câmbio(t−{LAG}) × exposição → Δ rebanho bovino")
    print("=" * 78)
    for cod, expos, desc in ESPECIFICACOES:
        ixs = [f"ix__{DRIVER}__{e}__l{LAG}" for e in expos]
        out = rodar_multi(df, DESFECHO, ixs)
        perm = permutacao_multi(df, DESFECHO, expos)
        res = out["res"]
        print(f"\n{cod}  {desc}   (n={out['n_obs']}, R²within={out['r2_within']:.4f}, "
              f"cluster={out['cluster']})")
        for j, (e, ix) in enumerate(zip(expos, ixs)):
            b, se, p = float(res.params[ix]), float(res.std_errors[ix]), float(res.pvalues[ix])
            pc = perm["p_circular"][j]
            print(f"    {ROTULOS[e]:36s} β={b:+.4f}  se={se:.4f}  "
                  f"p_agrup={p:.4f}  p_circ={pc:.4f}")
            linhas.append({
                "spec": cod, "descricao": desc, "exposicao": e, "rotulo": ROTULOS[e],
                "n_expos": len(expos), "beta": b, "se": se, "p_agrupado": p,
                "p_circular": float(pc), "n_obs": out["n_obs"], "n_amc": out["n_amc"],
                "r2_within": out["r2_within"], "cluster": out["cluster"],
            })

    res = pd.DataFrame(linhas)
    res.to_csv(ARQ_SAIDA, index=False, encoding="utf-8")
    print(f"\n[saída] {ARQ_SAIDA.relative_to(ROOT)}")

    # Leitura direta: o que acontece com o β da aptidão de S1 para S4/S5/S6.
    apt = res[res["exposicao"] == EXPO_APT].set_index("spec")
    b1 = apt.loc["S1", "beta"]
    print("\n" + "-" * 78)
    print("O QUE ACONTECE COM O β DA APTIDÃO QUANDO OS RIVAIS ENTRAM")
    print("-" * 78)
    for cod in ["S1", "S4", "S5", "S6"]:
        r = apt.loc[cod]
        print(f"  {cod}  β={r['beta']:+.4f}  ({100*(r['beta']-b1)/abs(b1):+6.1f}% vs S1)  "
              f"p_agrup={r['p_agrupado']:.3f}  p_circ={r['p_circular']:.3f}  "
              f"[{r['descricao']}]")

    if not sem_figuras:
        figura(res)


def figura(res: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cores = {EXPO_APT: "#1565c0", EXPO_LAT: "#c2185b", EXPO_ACE: "#e8920c"}
    especs = [c for c, _, _ in ESPECIFICACOES]
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ypos, ticks, labels = 0, [], []
    for cod in especs:
        sub = res[res["spec"] == cod]
        for _, r in sub.iterrows():
            ic = 1.96 * r["se"]
            ax.errorbar(r["beta"], ypos, xerr=ic, fmt="o", ms=6, capsize=3,
                        color=cores[r["exposicao"]], lw=1.8)
            ypos -= 1
        # o grupo ocupou as linhas [ypos+len(sub) .. ypos+1]; o centro delas é
        # ypos + (len+1)/2. Sem o +1 o rótulo fica meio ponto abaixo do grupo.
        ticks.append(ypos + (len(sub) + 1) / 2)
        labels.append(f"{cod}: {sub['descricao'].iloc[0]}")
        ypos -= 0.6

    ax.axvline(0, color="0.35", lw=1.0, ls="--")
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_ylim(ypos + 0.4, 1.6)   # folga acima p/ a legenda não cobrir barra
    ax.set_xlabel("β da interação câmbio(t−1) × exposição  →  Δ rebanho bovino")
    ax.set_title("A aptidão sobrevive quando latitude e acesso disputam o mesmo choque?\n"
                 "(barras = IC95% do SE agrupado, que se sabe otimista)", fontsize=10)
    hs = [plt.Line2D([], [], color=c, marker="o", ls="", label=ROTULOS[e])
          for e, c in cores.items()]
    ax.legend(handles=hs, frameon=False, fontsize=8, loc="upper left",
              bbox_to_anchor=(0.005, 1.0), ncol=3, columnspacing=1.2,
              handletextpad=0.4)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "horse_race_latitude.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'horse_race_latitude.png').relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sem-figuras", action="store_true")
    main(**vars(ap.parse_args()))
