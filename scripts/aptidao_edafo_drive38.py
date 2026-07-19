"""aptidao_edafo_drive38.py -- Protótipo Etapa B (cand. #52): aptidão edafoclimática
   EXÓGENA como 4ª exposição no teste de interação do #38
====================================================================================

PERGUNTA QUE RESPONDE
---------------------
A Etapa A (aptidao_edafo_exposicao.py) construiu `exp_apt_edafo` (aptidão física da
Embrapa, exógena) e mostrou que ela reproduz o gradiente Sul→Norte, correlacionando-se
de forma MODERADA (+0,30) com a exposição atual do #38 (% agri baseline) — logo carrega
informação própria, não é clone. Esta etapa a coloca à prova no desenho do #38:

    O gradiente câmbio × aptidão no rebanho (Achado #1 do #38) sobrevive quando a
    exposição é uma aptidão FÍSICA EXÓGENA, em vez do proxy de área (mecanicamente
    complementar)? E a grade exploratória, com a família honesta (agora 4 exposições
    = 192 testes), devolve algum sobrevivente do FDR?

DESENHO (reuso INTEGRAL do #38 — não altera o #38 publicado)
------------------------------------------------------------
Importa `drive_comum_amc` (#38): mesma interação 2-way FE
    Δy_it = α_i + γ_t + β·(Δdriver_t × exposição_i) + ε_it
mesma clusterização dupla (entidade+ano, fallback entidade), mesmos z-scores, mesmo
FDR-BH. `exp_apt_edafo` entra como 4ª exposição, ADICIONADA às três do #38 (decisão:
adicionar, não substituir — preserva comparabilidade e explicita o contraste).

Confirmatório NOVO (pré-declarado, com direção). Como exp_apt_edafo é ALTA no núcleo
apto (Sul) e r≈−0,69 com a fronteira, o sinal esperado é o ESPELHO do #38 sobre a
fronteira:
  - câmbio × aptidão → REBANHO  : sinal − (depreciação cresce o rebanho MAIS onde a
    aptidão é BAIXA = fronteira; espelho exógeno do +0,028 sobre exp_fronteira do #38).
  - preço soja × aptidão → AGRICULTURA : sinal + (boom converte MAIS onde a aptidão é alta).
  - câmbio × aptidão → PASTAGEM : sinal − (avanço de pasto na fronteira de baixa aptidão).

ENTRADAS
    scripts/drive_comum_amc.py            (#38, importado)
    data/processed/aptidao_edafo_amc.csv  (Etapa A: exp_apt_edafo por AMC)
    + as entradas do #38 (drivers, painel AMC, taxas)

SAÍDAS
    data/processed/drive_amc_apt_confirmatorio.csv
    data/processed/drive_amc_apt_exploratorio.csv
    outputs/aptidao_edafo/interacao_confirmatoria_apt.png

COMO RODAR
    py -3.14 scripts/aptidao_edafo_drive38.py
    py -3.14 scripts/aptidao_edafo_drive38.py --sem-figuras
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
DIR_OUT  = ROOT / "outputs" / "aptidao_edafo"
DIR_OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "scripts"))
import drive_comum_amc as d38   # reuso integral do #38

EXPO_NOVA = "exp_apt_edafo"

# Confirmatório novo (pré-declarado). Espelha os testes do #38 sobre a fronteira,
# com o sinal invertido porque aptidão alta = núcleo (Sul), oposto da fronteira.
CONF_NOVO = [
    ("cambio_real_efetivo",     EXPO_NOVA, "d_bovinos_mcab",        "-",
     "Depreciação cresce o rebanho MAIS onde a aptidão é BAIXA (fronteira) — espelho exógeno do #38."),
    ("preco_recebido_soja_idx", EXPO_NOVA, "agricultura_delta_mha", "+",
     "Boom de preço converte MAIS para agricultura onde a aptidão física é ALTA (núcleo)."),
    ("cambio_real_efetivo",     EXPO_NOVA, "pastagem_delta_mha",    "-",
     "Depreciação expande pasto MAIS na fronteira de BAIXA aptidão (avanço no Norte)."),
]


def carregar_estendido() -> pd.DataFrame:
    """df do #38 (3 exposições + interações) + exp_apt_edafo (Etapa A) e suas interações."""
    df = d38.carregar()   # constrói as 3 exposições, drivers z-score, interações, outcomes z-score
    apt = pd.read_csv(DIR_PROC / "aptidao_edafo_amc.csv")[["code_amc", EXPO_NOVA]]
    apt["code_amc"] = apt["code_amc"].astype(df["code_amc"].dtype)
    df = df.merge(apt, on="code_amc", how="left")
    # interações da nova exposição (todos os drivers, todos os lags)
    for d in d38.DRIVERS:
        for lag in d38.LAGS:
            df[f"ix__{d}__{EXPO_NOVA}__l{lag}"] = df[f"zd_{d}_l{lag}"] * df[EXPO_NOVA]
    return df


def main(sem_figuras: bool = False) -> None:
    print("=" * 78)
    print("Etapa B — aptidão edafoclimática EXÓGENA como 4ª exposição no #38")
    print("=" * 78)

    df = carregar_estendido()
    n_apt = df[EXPO_NOVA].notna().sum()
    print(f"[carga] {len(df):,} obs | exp_apt_edafo presente em {n_apt:,} linhas "
          f"({df['code_amc'].nunique()} AMCs)\n")

    # registra a nova exposição no #38 (rótulo p/ tabelas) e estende o confirmatório
    d38.EXPOSICOES[EXPO_NOVA] = ("(exógena)", "Aptidão edafoclim. (exógena)")
    conf_orig_len = len(d38.CONFIRMATORIO)
    d38.CONFIRMATORIO.extend(CONF_NOVO)

    # ── Confirmatório (reusa a lógica exata do #38; original + novo) ──
    conf = d38.confirmatorio(df)
    conf.to_csv(DIR_PROC / "drive_amc_apt_confirmatorio.csv", index=False, encoding="utf-8")
    conf_novo = conf[conf["exposicao"] == EXPO_NOVA]
    conf_velho = conf[conf["exposicao"] != EXPO_NOVA]

    print("[reprodução] confirmatórias ORIGINAIS do #38 (inalteradas — sanity):")
    if not conf_velho.empty:
        best = conf_velho.loc[conf_velho.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()]
        for _, r in best.iterrows():
            flag = " ✔" if r["confirma"] else ""
            print(f"  {r['driver_rotulo']:20s} × {r['exposicao_rotulo']:30s} → {r['desfecho_rotulo']:16s} "
                  f"lag{int(r['lag'])}: β={r['beta']:+.4f} p={r['p']:.3f}{flag}")

    print("\n[NOVO] confirmatórias com aptidão edafoclimática EXÓGENA:")
    if not conf_novo.empty:
        best = conf_novo.loc[conf_novo.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()]
        for _, r in best.iterrows():
            flag = "  ✔ CONFIRMA" if r["confirma"] else ("  (p<.05 sinal inesperado)" if r["p"] < 0.05 else "")
            print(f"  {r['driver_rotulo']:20s} → {r['desfecho_rotulo']:16s} "
                  f"lag{int(r['lag'])}: β={r['beta']:+.4f} p={r['p']:.3f} "
                  f"(esp.{r['sinal_esperado']}, N={r['n_obs']:,}){flag}")

    # ── Comparação direta: rebanho, proxy de área (fronteira) vs aptidão exógena ──
    print("\n[contraste] câmbio × EXPOSIÇÃO → Δ Rebanho (proxy de área vs aptidão exógena):")
    for e, rot in [("exp_fronteira", "Fronteira (% veg, proxy)"),
                   (EXPO_NOVA,       "Aptidão física (exógena)")]:
        sub = conf[(conf["driver"] == "cambio_real_efetivo") & (conf["exposicao"] == e)
                   & (conf["desfecho"] == "d_bovinos_mcab")]
        if not sub.empty:
            r = sub.loc[sub["p"].idxmin()]
            print(f"  {rot:28s}: β={r['beta']:+.4f} p={r['p']:.3f} (lag {int(r['lag'])})")

    # ── Exploratório: grade completa com 4 exposições (família honesta) + FDR-BH ──
    expl = d38.exploratorio(df)
    expl.to_csv(DIR_PROC / "drive_amc_apt_exploratorio.csv", index=False, encoding="utf-8")
    print(f"\n[exploratório] grade completa: {len(expl)} interações "
          f"(4 drivers × 4 exposições × 4 desfechos × 3 lags):")
    sig = expl[expl["sig_fdr"]].sort_values("p")
    if len(sig):
        for _, r in sig.iterrows():
            print(f"  ✚ {d38.DRIVERS[r['driver']]:18s} × {d38.EXPOSICOES[r['exposicao']][1]:28s} → "
                  f"{d38.OUTCOMES[r['desfecho']]:16s} lag{int(r['lag'])}: "
                  f"β={r['beta']:+.4f} p={r['p']:.4f} p_fdr={r['p_fdr']:.4f}")
    else:
        print("  Nenhuma sobrevive ao FDR-BH.")
    n_bruto = int((expl["p"] < 0.05).sum())
    n_novo_bruto = int(((expl["p"] < 0.05) & (expl["exposicao"] == EXPO_NOVA)).sum())
    print(f"  ({n_bruto} de {len(expl)} com p<0,05 brutos; {n_novo_bruto} deles na nova exposição; "
          f"{int(expl['sig_fdr'].sum())} sobrevivem ao FDR)")

    # figura: forest plot das confirmatórias novas
    if not sem_figuras and not conf_novo.empty:
        _fig_conf(conf_novo)

    # restaura o estado do módulo #38 (higiene — evita efeito colateral se reimportado)
    del d38.CONFIRMATORIO[conf_orig_len:]
    d38.EXPOSICOES.pop(EXPO_NOVA, None)

    print("\n" + "=" * 78)
    print("CONCLUÍDO — Etapa B.")
    print("=" * 78)


def _fig_conf(conf_novo: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    best = conf_novo.loc[conf_novo.groupby(["driver", "exposicao", "desfecho"])["p"].idxmin()].reset_index(drop=True)
    best = best.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 0.95 * len(best) + 2))
    for i, r in best.iterrows():
        cor = "#1b7837" if r["confirma"] else ("#762a83" if r["p"] < 0.05 else "#999999")
        ax.errorbar(r["beta"], i, xerr=[[r["beta"] - r["ci_lo"]], [r["ci_hi"] - r["beta"]]],
                    fmt="o", color=cor, capsize=4, lw=2, ms=8)
        rot = (f"{r['driver_rotulo']} × Aptidão exógena\n→ {r['desfecho_rotulo']} "
               f"(lag {int(r['lag'])}; esperado {r['sinal_esperado']})")
        ax.annotate(rot, (r["ci_lo"], i), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=8)
        ax.annotate(f"p={r['p']:.3f}", (r["ci_hi"], i), xytext=(8, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8, color=cor)
    ax.axvline(0, color="0.4", lw=1, ls="--")
    ax.set_yticks([])
    ax.set_xlabel("β padronizado (DP do desfecho por +1 DP driver × +1 DP aptidão)")
    ax.set_title("Etapa B — interações confirmatórias com aptidão edafoclimática EXÓGENA (#38)\n"
                 "verde = confirma direção e p<0,05; roxo = p<0,05 sinal inesperado; cinza = NS",
                 fontsize=11, fontweight="bold")
    ax.margins(x=0.35)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "interacao_confirmatoria_apt.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[fig] {(DIR_OUT / 'interacao_confirmatoria_apt.png').relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Etapa B — aptidão edafoclimática no #38")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()
    try:
        main(sem_figuras=args.sem_figuras)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        raise
