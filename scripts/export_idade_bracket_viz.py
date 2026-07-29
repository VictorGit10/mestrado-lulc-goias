"""export_idade_bracket_viz.py — export de viz: a idade do pasto NAS DUAS RÉGUAS

POR QUE ESTE ARQUIVO EXISTE (2026-07-28)
----------------------------------------
A peça da Perna 2 desenhava só `pasto→agricultura` — a régua **exposta** à
mudança de rótulo do Mosaico — enquanto a copy ao lado afirmava a conclusão
obtida sob a régua da **união** ("as cinco regiões têm o mesmo desenho"). Uma
revisão do autor pegou a inconsistência a olho: no que está desenhado, Norte e
Noroeste são visivelmente mais bimodais que Sul e Centro. Medido
(`forma_regional_bimodalidade.py`), o olho estava certo:

| medida (célula "todos") | agric | união |
|---|---|---|
| profundidade do vale — Noroeste | **0,415** | 0,058 |
| profundidade do vale — Norte | **0,271** | 0 (sem vale) |
| profundidade do vale — Sul / Leste | 0 | 0 |
| peso da população jovem, amplitude entre regiões | 0,239–0,390 | 0,380–0,435 |
| distância entre formas (TV) Sul × Norte | **0,223** | **0,023** |

Ou seja: a diferença regional de FORMA existe, é grande, e **é o artefato** — ela
some quando se fecha o buraco de rotulagem. A peça, portanto, não pode desenhar
só uma das réguas: desenhar só a exposta contradiz o texto; desenhar só a imune
esconde do leitor a própria evidência da auditoria. Ela desenha **as duas**, com
a imune por padrão.

DUAS RÉGUAS (D26)
  agric  — `pasto→agricultura`; piso, e a régua onde a idade é medida no #28
  uniao  — `pasto→(agricultura ∪ mosaico)`; teto, imune à reetiquetagem por
           construção, porque não depende de o classificador separar as classes

Só a célula "todos" (série inteira) é exportada: o eixo temporal está suspenso
(D25/D26) e a peça não oferece recorte por ato.

ENTRADAS
    data/processed/pastagem_conversao_destinos.parquet   (#28 + destinos, D26)
    data/processed/amc_crosswalk_goias.csv               (#25)
    data/processed/mapeamento_mesorregioes.csv

SAÍDA
    Visualizacao/assets/data/idade_pastagem_bracket.json

COMO RODAR
    python scripts/export_idade_bracket_viz.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analise_reserva_terra import ajustar_gmm_unidim              # noqa: E402
from bimodalidade_regional import bimodality_coef                 # noqa: E402
from estatistica_ponderada import mediana as mediana_p            # noqa: E402
from forma_regional_bimodalidade import antimodo, vale_empirico   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DESTINOS = ROOT / "data" / "processed" / "pastagem_conversao_destinos.parquet"
CW_AMC = ROOT / "data" / "processed" / "amc_crosswalk_goias.csv"
MESO = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
SAIDA = ROOT / "Visualizacao" / "assets" / "data" / "idade_pastagem_bracket.json"

BINS = np.arange(0, 41, 2)          # 2 anos — mesma convenção do site
BINS_FINO = np.arange(0, 41, 1)     # 1 ano — só para detectar o vale empírico
REGUAS = {"agric": ["agricultura"], "uniao": ["agricultura", "mosaico"]}
ESTADO = "Goiás (estado)"

# Critério de bimodalidade do #28C (todos precisam valer).
BIC_MIN, SEP_MIN, PESO_MIN, N_GMM_MIN = 10.0, 5.0, 0.15, 100


def celula(idade: np.ndarray, peso: np.ndarray, n_censurado: float) -> dict:
    counts, _ = np.histogram(idade, bins=BINS, weights=peso)
    n = int(round(float(peso.sum())))
    out = {
        "n": n,
        "n_censurado": int(round(n_censurado)),
        "mediana": mediana_p(idade, peso) if n else None,
        "counts": [int(round(c)) for c in counts],
        "gmm": None,
        "bimodal": None,
    }
    if n < N_GMM_MIN:
        return out

    g = ajustar_gmm_unidim(idade.astype(float), peso)
    sep = abs(g["mu2"] - g["mu1"])
    delta_bic = g["bic_1c"] - g["bic_2c"]
    bc = bimodality_coef(idade.astype(float), peso)
    fino, _ = np.histogram(idade, bins=BINS_FINO, weights=peso)
    ve = vale_empirico(fino / fino.sum())
    am = antimodo(g)
    out["gmm"] = {
        "mu_jovem": round(g["mu1"], 1), "sig_jovem": round(g["sig1"], 2),
        "w_jovem": round(g["w1"], 3),
        "mu_velho": round(g["mu2"], 1), "sig_velho": round(g["sig2"], 2),
        "w_velho": round(g["w2"], 3),
        "mu_1c": round(g["mu_1c"], 1), "sig_1c": round(g["sig_1c"], 2),
        "separacao_anos": round(sep, 1),
        "bc_sarle": round(bc, 3) if bc == bc else None,
        # `dip` = profundidade do vale na mistura ajustada; `dip_emp` = no
        # histograma bruto. É o par que quantifica "parece mais bimodal".
        "dip": round(float(am["dip"]), 3),
        "dip_emp": round(float(ve["dip_emp"]), 3),
        "vale_emp_x": None if ve["vale_emp_x"] != ve["vale_emp_x"] else float(ve["vale_emp_x"]),
    }
    out["bimodal"] = bool(delta_bic > BIC_MIN and sep > SEP_MIN
                          and min(g["w1"], g["w2"]) > PESO_MIN)
    return out


def bloco(df: pd.DataFrame, col: str, rotular, incluir_estado: bool) -> dict:
    nc = df[~df["censurado"]]
    regioes = {}
    if incluir_estado:
        regioes[ESTADO] = celula(nc["idade_pastagem_anos"].to_numpy(float),
                                 nc["peso"].to_numpy(float),
                                 df.loc[df["censurado"], "peso"].sum())
    for chave, g in nc.groupby(col, observed=True):
        if str(chave) in ("", "0", "nan"):
            continue
        cens = df[(df[col] == chave) & df["censurado"]]["peso"].sum()
        regioes[rotular(chave)] = celula(g["idade_pastagem_anos"].to_numpy(float),
                                         g["peso"].to_numpy(float), cens)
    return regioes


def carregar(destinos: list[str]) -> pd.DataFrame:
    df = pd.read_parquet(DESTINOS)
    df = df[df["destino"].isin(destinos)].rename(columns={"n_pixels": "peso"})
    df["peso"] = df["peso"].astype("float64")
    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    meso = pd.read_csv(MESO, dtype={"cd_mun": "int64"})[["cd_mun", "nm_meso"]]
    cw = pd.read_csv(CW_AMC, dtype={"cd_mun": "int64", "code_amc": "int64"})
    df = df.merge(meso, on="cd_mun", how="left").merge(
        cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
    df["mesorregiao"] = df["nm_meso"].fillna("")
    return df


def main() -> None:
    saida = {
        "meta": {
            "fonte": "pastagem_conversao_destinos.parquet (#28 + destinos, D26)",
            "gerado_por": "scripts/export_idade_bracket_viz.py",
            "bins": BINS.astype(int).tolist(),
            "recorte": "série inteira (1986–2024); o eixo temporal está suspenso (D25/D26)",
            "criterio_bimodal": f"ΔBIC>{BIC_MIN:.0f} & separação>{SEP_MIN:.0f}a "
                                f"& peso_menor>{PESO_MIN} (n≥{N_GMM_MIN})",
            "reguas": {
                "agric": "pasto→agricultura — exposta à mudança de rótulo do Mosaico",
                "uniao": "pasto→(agricultura ∪ mosaico) — imune por construção",
            },
        },
        "reguas": {},
    }

    for nome, destinos in REGUAS.items():
        df = carregar(destinos)
        nc = df.loc[~df["censurado"], "peso"].sum()
        print(f"{nome:<6} {df['peso'].sum():,.0f} eventos | {nc:,.0f} não-censurados")
        meso_b = bloco(df[df["mesorregiao"] != ""], "mesorregiao", str, True)
        amc_b = bloco(df[df["code_amc"].notna()], "code_amc",
                      lambda c: f"AMC {int(c)}", False)
        n_bi = sum(1 for c in amc_b.values() if c["bimodal"])
        print(f"       mesorregiões: {len(meso_b) - 1} (+estado) | "
              f"AMCs: {len(amc_b)} ({n_bi} bimodais)")
        saida["reguas"][nome] = {"mesorregiao": meso_b, "amc": amc_b}

    SAIDA.write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
    print(f"\n[OK] {SAIDA.relative_to(ROOT)} — {SAIDA.stat().st_size / 1024:.0f} KB")

    print("\nForma por região (célula 'todos'):")
    print(f"  {'região':<18} {'régua':<7} {'w_jovem':>8} {'vale ajust.':>12} {'vale bruto':>11}")
    for nome in REGUAS:
        for rot, c in saida["reguas"][nome]["mesorregiao"].items():
            if not c["gmm"]:
                continue
            g = c["gmm"]
            print(f"  {rot:<18} {nome:<7} {g['w_jovem']:>8.3f} "
                  f"{g['dip']:>12.3f} {g['dip_emp']:>11.3f}")


if __name__ == "__main__":
    main()
