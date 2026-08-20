"""robustez_bootstrap_bloco.py -- Pipeline #55: o IC do centro de massa sob
   dependência espacial (bootstrap de BLOCOS, não de AMCs isoladas)
====================================================================================

PERGUNTA QUE RESPONDE
---------------------
A decisão D19 põe barra de erro em todo deslocamento do centro de massa (#32), e o
IC vem de um bootstrap que reamostra as 166 AMCs COM REPOSIÇÃO, uma a uma. Isso
supõe que as AMCs são trocáveis e independentes.

O próprio trabalho mostra que não são: o #41 acha I de Moran significativo em 125 dos
140 testes na malha de AMC, e os parâmetros de defasagem/erro espacial ficam entre
+0,35 e +0,56. Sob dependência espacial, o bootstrap i.i.d. tem N EFETIVO menor que
166 -- e o IC sai ESTREITO DEMAIS. A pergunta é direta:

    O veredito da Tabela de centros (3 classes "robustas" + vegetação "ancorada")
    sobrevive quando a reamostragem respeita a vizinhança?

Isso importa porque é a tabela mais visível do trabalho, e porque a vegetação natural
já está no fio da navalha (+7,6 km, IC i.i.d. [-0,5; +15,6] -- inclui zero por pouco).
Se o IC alargar, ela continua "ancorada" (o veredito não muda, e fica MAIS seguro).
Se algum dos três robustos passar a incluir zero, a Perna 1 muda de grau.

ABORDAGEM
---------
Bootstrap de BLOCOS ESPACIAIS. Em vez de sortear AMC a AMC, agrupa-se o estado em k
blocos espacialmente contíguos (k-means sobre os centroides em EPSG:5880) e sorteiam-se
os BLOCOS com reposição. Um bloco entra ou sai inteiro, com todos os seus vizinhos --
que é justamente o que a reamostragem i.i.d. quebra.

O tamanho do bloco é um parâmetro, e não um valor "certo": bloco de 1 AMC = o
bootstrap i.i.d. atual (k=166); bloco grande = mais conservador e menos preciso. Por
isso o pipeline NÃO escolhe um k -- ele varre uma grade de k e reporta o IC como
função do tamanho do bloco. O que se lê é a ESTABILIDADE do veredito ao longo da
grade, no mesmo espírito da régua temporal (D12): concordância entre réguas, não
uma régua eleita.

Vale registrar o que o método NÃO faz: ele corrige a incerteza por composição de
unidades sob vizinhança; não corrige erro do classificador, nem viés de medida, nem
a suposição de distribuição uniforme da classe dentro da AMC (essa é a régua de
escala do #32, que recalcula tudo pixel a pixel e bate em 1-2 km).

ENTRADAS
    data/processed/painel_amc_goias.parquet   (#25)
    data/processed/amc_goias.gpkg             (#25, geometria -> centroides)
    scripts/centro_massa.py                   (#32, importado: carga e reprojeção)

SAÍDAS
    data/processed/centro_massa_bootstrap_bloco.csv   (variável × k: ΔN, IC95%, veredito)
    outputs/centro_massa/bootstrap_bloco.png          (IC × tamanho do bloco)

COMO RODAR
    py -3.14 scripts/robustez_bootstrap_bloco.py
    py -3.14 scripts/robustez_bootstrap_bloco.py --sem-figuras

Depende de: Pipeline #25, #32.
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
import centro_massa as cm  # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "centro_massa"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ARQ_SAIDA = DIR_PROC / "centro_massa_bootstrap_bloco.csv"

# Grade de tamanhos de bloco. k = nº de blocos; 166 = uma AMC por bloco = o
# bootstrap i.i.d. da D19 (serve de linha de base e de teste de sanidade: tem de
# reproduzir o IC publicado).
GRADE_K = [166, 83, 55, 33, 20, 12]

BOOT_B    = 2000        # mesmo B da D19
BOOT_SEED = 20260819

ANO_INI, ANO_FIM = cm.ANO_INI, cm.ANO_FIM


# ---------------------------------------------------------------------------
# 1. Blocos espaciais (k-means sobre os centroides)
# ---------------------------------------------------------------------------
# k-means próprio (166 pontos, 2 dimensões) para não acrescentar dependência de
# sklearn a um pipeline que roda em 3 segundos. Inicialização k-means++ com semente
# fixa; Lloyd até convergir. O objetivo aqui não é a partição ótima, e sim blocos
# espacialmente coerentes e reprodutíveis.

def kmeans_blocos(XY: np.ndarray, k: int, seed: int = 7, iters: int = 200) -> np.ndarray:
    n = len(XY)
    if k >= n:
        return np.arange(n)
    rng = np.random.default_rng(seed)
    # k-means++
    cen = [XY[rng.integers(n)]]
    for _ in range(k - 1):
        d2 = np.min(((XY[:, None, :] - np.array(cen)[None, :, :]) ** 2).sum(-1), axis=1)
        prob = d2 / d2.sum() if d2.sum() > 0 else np.full(n, 1 / n)
        cen.append(XY[rng.choice(n, p=prob)])
    cen = np.array(cen, dtype=float)
    lab = np.zeros(n, dtype=int)
    for _ in range(iters):
        d2 = ((XY[:, None, :] - cen[None, :, :]) ** 2).sum(-1)
        novo = d2.argmin(axis=1)
        if np.array_equal(novo, lab):
            break
        lab = novo
        for j in range(k):
            m = lab == j
            if m.any():
                cen[j] = XY[m].mean(axis=0)
    # recompacta rótulos (blocos vazios somem)
    _, lab = np.unique(lab, return_inverse=True)
    return lab


# ---------------------------------------------------------------------------
# 2. Bootstrap de blocos do ΔNorte
# ---------------------------------------------------------------------------
# Reamostrar BLOCOS com reposição = sortear contagens ~ Multinomial(k, 1/k) sobre os
# blocos e propagá-las às AMCs do bloco. A partir daí a álgebra é a do #32: o centro
# médio de cada réplica é uma razão de dois produtos matriz-vetor.

def boot_bloco(painel: pd.DataFrame, col_por_chave: dict, rotulos: dict,
               labels: np.ndarray, codes: np.ndarray,
               B: int = BOOT_B, seed: int = BOOT_SEED) -> list[dict]:
    geo = painel.groupby("code_amc")[["cx", "cy"]].first().reindex(codes)
    CX, CY = geo["cx"].to_numpy(), geo["cy"].to_numpy()
    anos = np.sort(painel["ano"].unique())
    k = int(labels.max() + 1)

    rng = np.random.default_rng(seed)
    cnt_bloco = rng.multinomial(k, np.full(k, 1.0 / k), size=B).astype(float)  # B×k
    counts = cnt_bloco[:, labels]                                             # B×n

    linhas = []
    for chave, col in col_por_chave.items():
        W = (painel.pivot_table(index="code_amc", columns="ano", values=col, aggfunc="first")
                   .reindex(index=codes, columns=anos).to_numpy())
        W = np.where(np.isfinite(W) & (W > 0), W, 0.0)

        CYW = CY[:, None] * W
        CXW = CX[:, None] * W
        DEN = counts @ W
        with np.errstate(invalid="ignore", divide="ignore"):
            MY = (counts @ CYW) / DEN
            MX = (counts @ CXW) / DEN
            MY_pt = CYW.sum(axis=0) / W.sum(axis=0)
            MX_pt = CXW.sum(axis=0) / W.sum(axis=0)

        idx = {int(a): j for j, a in enumerate(anos)}
        i0, i1 = idx[ANO_INI], idx[ANO_FIM]
        dN_b = (MY[:, i1] - MY[:, i0]) / 1000.0
        dE_b = (MX[:, i1] - MX[:, i0]) / 1000.0
        dN_pt = (MY_pt[i1] - MY_pt[i0]) / 1000.0
        dE_pt = (MX_pt[i1] - MX_pt[i0]) / 1000.0
        lo, hi = np.nanpercentile(dN_b, [2.5, 97.5])
        loE, hiE = np.nanpercentile(dE_b, [2.5, 97.5])
        linhas.append({
            "variavel": chave, "rotulo": rotulos[chave],
            "k_blocos": k, "amc_por_bloco": round(len(codes) / k, 2),
            "dN_km": dN_pt, "dN_lo": lo, "dN_hi": hi,
            "largura_km": hi - lo,
            "exclui_zero": bool(lo > 0 or hi < 0),
            "dL_km": dE_pt, "dL_lo": loE, "dL_hi": hiE,
            "exclui_zero_leste": bool(loE > 0 or hiE < 0),
        })
    return linhas


# ---------------------------------------------------------------------------
# 3. Figura
# ---------------------------------------------------------------------------

def figura(res: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    ordem = ["pastagem", "bovinos", "agricultura", "veg_natural"]
    cores = {k: cm.VARIAVEIS[k][2] for k in ordem}
    ks = sorted(res["k_blocos"].unique(), reverse=True)
    desloc = np.linspace(-0.26, 0.26, len(ordem))

    for j, var in enumerate(ordem):
        sub = res[res["variavel"] == var].set_index("k_blocos").reindex(ks)
        x = np.arange(len(ks)) + desloc[j]
        ax.errorbar(x, sub["dN_km"],
                    yerr=[sub["dN_km"] - sub["dN_lo"], sub["dN_hi"] - sub["dN_km"]],
                    fmt="o", ms=5, capsize=3, lw=1.6, color=cores[var],
                    label=cm.VARIAVEIS[var][1])

    ax.axhline(0, color="0.35", lw=1.0, ls="--")
    ax.set_xticks(np.arange(len(ks)))
    ax.set_xticklabels([f"{k} blocos\n({166/k:.0f} AMC/bloco)" for k in ks], fontsize=8)
    ax.set_ylabel("Deslocamento ao norte, 1985→2024 (km)")
    ax.set_xlabel("Tamanho do bloco espacial da reamostragem")
    ax.set_title("IC95% do deslocamento sob bootstrap de blocos espaciais\n"
                 "(166 blocos = o bootstrap i.i.d. da decisão D19)", fontsize=10)
    ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "bootstrap_bloco.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'bootstrap_bloco.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------

def main(sem_figuras: bool = False) -> None:
    painel, _ = cm.carregar_dados()
    col_por_chave = {k: v[0] for k, v in cm.VARIAVEIS.items()}
    rotulos = {k: v[1] for k, v in cm.VARIAVEIS.items()}

    geo = painel.groupby("code_amc")[["cx", "cy"]].first()
    codes = geo.index.to_numpy()
    XY = geo[["cx", "cy"]].to_numpy()
    print(f"[dados] {len(codes)} AMCs, {painel['ano'].nunique()} anos")

    linhas = []
    for k in GRADE_K:
        lab = kmeans_blocos(XY, k)
        kk = int(lab.max() + 1)
        tam = np.bincount(lab)
        print(f"[blocos] k={kk:3d}  tamanho: min {tam.min()} / mediana {int(np.median(tam))} / max {tam.max()}")
        linhas += boot_bloco(painel, col_por_chave, rotulos, lab, codes)

    res = pd.DataFrame(linhas)
    res.to_csv(ARQ_SAIDA, index=False, encoding="utf-8")
    print(f"\n[saída] {ARQ_SAIDA.relative_to(ROOT)}")

    print("\n" + "=" * 78)
    print("ΔNORTE 1985→2024 — IC95% POR TAMANHO DE BLOCO")
    print("=" * 78)
    for var in ["pastagem", "bovinos", "agricultura", "veg_natural"]:
        sub = res[res["variavel"] == var]
        print(f"\n{cm.VARIAVEIS[var][1]}  (ΔN = {sub['dN_km'].iloc[0]:+.1f} km)")
        for _, r in sub.iterrows():
            marca = "robusto " if r["exclui_zero"] else "ANCORADA"
            print(f"   k={r['k_blocos']:3.0f} ({r['amc_por_bloco']:4.1f} AMC/bloco)  "
                  f"IC95% [{r['dN_lo']:+7.1f}; {r['dN_hi']:+7.1f}]  "
                  f"largura {r['largura_km']:5.1f} km   {marca}")

    print("\n" + "-" * 78)
    print("VEREDITO POR VARIÁVEL (concordância ao longo da grade de blocos)")
    print("-" * 78)
    for var in ["pastagem", "bovinos", "agricultura", "veg_natural"]:
        sub = res[res["variavel"] == var]
        n_ok = int(sub["exclui_zero"].sum())
        print(f"  {cm.VARIAVEIS[var][1]:20s}  exclui zero em {n_ok}/{len(sub)} tamanhos de bloco")

    # Componente leste: a marcha tem duas componentes, e a tabela publicada só
    # reporta a norte. Registrada aqui com a mesma barra de erro.
    print("\n" + "-" * 78)
    print("COMPONENTE LESTE (mesma reamostragem) — bloco mais conservador da grade")
    print("-" * 78)
    kmin = res["k_blocos"].min()
    for _, r in res[res["k_blocos"] == kmin].iterrows():
        marca = "robusto" if r["exclui_zero_leste"] else "inclui zero"
        print(f"  {r['rotulo']:20s}  ΔL = {r['dL_km']:+6.1f} km  "
              f"IC95% [{r['dL_lo']:+7.1f}; {r['dL_hi']:+7.1f}]  {marca}")

    if not sem_figuras:
        figura(res)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sem-figuras", action="store_true")
    main(**vars(ap.parse_args()))
