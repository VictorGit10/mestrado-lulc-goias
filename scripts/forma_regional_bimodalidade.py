"""forma_regional_bimodalidade.py — a FORMA da distribuição difere entre regiões?

PERGUNTA (28/jul/2026, levantada na revisão da Perna 2 do site)
--------------------------------------------------------------
A copy da Perna 2 afirma que, ao percorrer as cinco mesorregiões, "o desenho não
muda". Olhando os histogramas, Norte e Noroeste **parecem** mais nitidamente
bimodais que Sul e Centro — há um vale visível neles e não nos outros. A
afirmação da tela está errada, ou o olho está sendo enganado?

A distinção que este script existe para fazer:

  1. **COEXISTÊNCIA** — as duas populações estão presentes na região?
     (é o que o #28C mede: 5/5 regiões, 162/164 AMCs)
  2. **FORMA** — a mistura das duas produz um vale VISÍVEL na densidade?
     (nunca foi medido; é o que o olho lê como "mais bimodal")

São coisas diferentes e podem divergir: uma mistura com w₁=0,36 e modos a 11,5a
de distância pode não ter vale nenhum, enquanto w₁=0,24 com modos a 15,1a tem.
Coexistência é sobre a existência dos dois componentes; forma é sobre a
geometria da soma.

MÉTODO
------
Para cada mesorregião, sob DUAS réguas (D26):
  - `agric`  — o subconjunto `pasto→agricultura` (a régua exposta à mudança de
    rótulo do Mosaico, e a única que a peça do site desenha hoje)
  - `uniao`  — `pasto→(agricultura ∪ mosaico)`, imune à reetiquetagem por
    construção

mede-se:
  - GMM 2c ponderado (mesmo `ajustar_gmm_unidim` do #28) → μ, σ, w, separação
  - BC de Sarle (model-free)
  - **antimodo da mistura ajustada**: existe mínimo local entre os dois modos?
    Profundidade relativa `dip = 1 − f(vale)/f(pico menor)` ∈ [0,1]. dip=0
    significa "sem vale nenhum" (ombro puro); dip alto = vale fundo.
  - **vale empírico**: o histograma bruto (bins de 1a) desce e volta a subir?
    Medido sobre a curva suavizada por média móvel de 3 bins, para não contar
    ruído de bin como vale.
  - **distância entre formas**: distância de variação total (TV) entre os
    histogramas normalizados de cada par de regiões — quanto da massa teria de
    ser movida para uma virar a outra. É a medida honesta de "o desenho muda?",
    e não depende de ajuste nenhum.

Sob censo, p-valor e ΔBIC medem n, não evidência (D23) — por isso o veredito
sai de TAMANHO de efeito (dip, TV) e de ESTABILIDADE entre as duas réguas.

SAÍDA
    data/processed/forma_regional_bimodalidade.csv
    data/processed/forma_regional_tv.csv

COMO RODAR
    python scripts/forma_regional_bimodalidade.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analise_reserva_terra import carregar, ajustar_gmm_unidim   # noqa: E402
from bimodalidade_regional import bimodality_coef                # noqa: E402
from estatistica_ponderada import mediana as mediana_p           # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DESTINOS = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"
MESO_IN = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
OUT = ROOT / "data" / "processed"

BINS = np.arange(0, 41, 1)
CENTROS = BINS[:-1] + 0.5
ORDEM_SUL_NORTE = ["Sul Goiano", "Centro Goiano", "Leste Goiano",
                   "Noroeste Goiano", "Norte Goiano"]


def normal(x, mu, sig):
    return np.exp(-0.5 * ((x - mu) / sig) ** 2) / (sig * np.sqrt(2 * np.pi))


def antimodo(g: dict) -> dict:
    """Existe vale entre os dois modos da mistura ajustada? Qual a profundidade?

    Varre a densidade da mistura entre μ₁ e μ₂. Se ela é monotônica no
    intervalo, não há vale — a segunda população aparece como OMBRO. Se há
    mínimo interior, a profundidade relativa é 1 − f(vale)/f(pico menor): 0 =
    sem vale, 1 = os dois picos totalmente separados.
    """
    x = np.linspace(g["mu1"], g["mu2"], 2000)
    f = g["w1"] * normal(x, g["mu1"], g["sig1"]) + g["w2"] * normal(x, g["mu2"], g["sig2"])
    i = int(np.argmin(f))
    if i == 0 or i == len(x) - 1:            # mínimo na borda = sem vale interior
        return {"tem_vale": False, "vale_x": np.nan, "dip": 0.0}
    pico_menor = min(f[0], f[-1])
    return {"tem_vale": True, "vale_x": float(x[i]),
            "dip": float(1 - f[i] / pico_menor)}


PROEMINENCIA_MIN = 0.02   # 2% — abaixo disso é ondulação de bin, não vale


def vale_empirico(dens: np.ndarray) -> dict:
    """O histograma BRUTO desce e volta a subir? (sem ajustar nada)

    Procura um **segundo pico local** depois do pico jovem e mede a profundidade
    do vale que o separa dele. Não serve pegar o mínimo global do trecho: numa
    distribuição com cauda longa ele cai sempre na ponta direita e o teste nunca
    dispara — foi o defeito da primeira versão deste código.

    Suaviza com média móvel de 3 bins (um bin ruidoso não pode fundar um vale) e
    exige proeminência relativa mínima, senão qualquer ondulação de 0,1 pp
    contaria como bimodalidade visível.
    """
    vazio = {"tem_vale_emp": False, "vale_emp_x": np.nan,
             "pico2_emp_x": np.nan, "dip_emp": 0.0}
    s = np.convolve(dens, np.ones(3) / 3, mode="same")
    pico = int(np.argmax(s))
    if len(s) - pico < 4:
        return vazio

    # Máximos locais estritos à direita do pico jovem.
    cand = [j for j in range(pico + 2, len(s) - 1)
            if s[j] > s[j - 1] and s[j] >= s[j + 1]]
    melhor = vazio
    for j in cand:
        i = pico + int(np.argmin(s[pico:j]))
        if i <= pico or s[j] <= s[i]:
            continue
        dip = float(1 - s[i] / s[j])
        if dip > melhor["dip_emp"]:
            melhor = {"tem_vale_emp": dip >= PROEMINENCIA_MIN,
                      "vale_emp_x": float(CENTROS[i]),
                      "pico2_emp_x": float(CENTROS[j]),
                      "dip_emp": dip}
    return melhor if melhor["dip_emp"] >= PROEMINENCIA_MIN else vazio


def celula(idade: np.ndarray, peso: np.ndarray) -> dict:
    n = float(peso.sum())
    c, _ = np.histogram(idade, bins=BINS, weights=peso)
    dens = c / c.sum()
    g = ajustar_gmm_unidim(idade, peso)
    sep = abs(g["mu2"] - g["mu1"])
    out = {
        "n": int(round(n)),
        "mediana": mediana_p(idade, peso),
        "mu1": round(g["mu1"], 2), "sig1": round(g["sig1"], 2), "w1": round(g["w1"], 3),
        "mu2": round(g["mu2"], 2), "sig2": round(g["sig2"], 2), "w2": round(g["w2"], 3),
        "separacao": round(sep, 2),
        "bc_sarle": round(bimodality_coef(idade, peso), 3),
        "bimodal_28c": bool((g["bic_1c"] - g["bic_2c"] > 10) and sep > 5
                            and min(g["w1"], g["w2"]) > 0.15),
    }
    out.update({k: (round(v, 3) if isinstance(v, float) else v)
                for k, v in antimodo(g).items()})
    out.update({k: (round(v, 3) if isinstance(v, float) else v)
                for k, v in vale_empirico(dens).items()})
    out["_dens"] = dens
    return out


def tabela(df: pd.DataFrame, rotulo: str) -> pd.DataFrame:
    nc = df[~df["censurado"]]
    linhas, densidades = [], {}
    for reg in ["Goiás (estado)"] + ORDEM_SUL_NORTE:
        sub = nc if reg.startswith("Goiás") else nc[nc["mesorregiao"] == reg]
        if sub.empty:
            continue
        c = celula(sub["idade_pastagem_anos"].to_numpy(float),
                   sub["peso"].to_numpy(float))
        densidades[reg] = c.pop("_dens")
        linhas.append({"regua": rotulo, "regiao": reg, **c})
    return pd.DataFrame(linhas), densidades


def distancias_tv(dens: dict, rotulo: str) -> pd.DataFrame:
    """Distância de variação total entre os histogramas de cada par de regiões.

    TV = ½·Σ|p−q| ∈ [0,1]: a fração da massa que teria de mudar de lugar para
    uma distribuição virar a outra. Não depende de ajuste, de n, nem de
    p-valor — é a resposta direta a "o desenho muda entre regiões?".
    """
    regs = [r for r in ORDEM_SUL_NORTE if r in dens]
    linhas = []
    for i, a in enumerate(regs):
        for b in regs[i + 1:]:
            linhas.append({"regua": rotulo, "a": a, "b": b,
                           "tv": round(float(0.5 * np.abs(dens[a] - dens[b]).sum()), 3)})
    return pd.DataFrame(linhas)


def carregar_uniao() -> pd.DataFrame:
    """Mesmo formato de `carregar('censo')`, mas com os dois destinos somados."""
    df = pd.read_parquet(DESTINOS).rename(columns={"n_pixels": "peso"})
    meso = pd.read_csv(MESO_IN, dtype={"cd_mun": "int64"})
    df = df.merge(meso[["cd_mun", "nm_meso"]], on="cd_mun", how="left")
    df["mesorregiao"] = df["nm_meso"].fillna("")
    df["peso"] = df["peso"].astype("float64")
    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    return df


def main() -> None:
    print("Régua 1 — pasto→agricultura (a que o site desenha hoje)")
    agric = carregar("censo")
    t1, d1 = tabela(agric, "agric")

    print("Régua 2 — pasto→(agricultura ∪ mosaico), imune à mudança de rótulo")
    uniao = carregar_uniao()
    t2, d2 = tabela(uniao, "uniao")

    tab = pd.concat([t1, t2], ignore_index=True)
    tv = pd.concat([distancias_tv(d1, "agric"), distancias_tv(d2, "uniao")],
                   ignore_index=True)

    tab.to_csv(OUT / "forma_regional_bimodalidade.csv", index=False, encoding="utf-8")
    tv.to_csv(OUT / "forma_regional_tv.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 200, "display.max_columns", 40)
    for regua in ["agric", "uniao"]:
        print(f"\n{'=' * 100}\nRÉGUA: {regua}\n{'=' * 100}")
        sub = tab[tab["regua"] == regua]
        print(sub[["regiao", "n", "mediana", "mu1", "sig1", "w1", "mu2", "sig2", "w2",
                   "separacao", "bc_sarle", "bimodal_28c",
                   "tem_vale", "dip", "tem_vale_emp", "vale_emp_x", "pico2_emp_x", "dip_emp"]].to_string(index=False))
        print("\n  Distância entre formas (TV — fração da massa que teria de mudar de lugar):")
        s = tv[tv["regua"] == regua].sort_values("tv", ascending=False)
        for _, r in s.iterrows():
            print(f"    {r['a']:<16} × {r['b']:<16} {r['tv']:.3f}")

    print("\n[OK] data/processed/forma_regional_bimodalidade.csv + _tv.csv")


if __name__ == "__main__":
    main()
