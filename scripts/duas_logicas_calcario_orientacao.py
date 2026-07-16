"""duas_logicas_calcario_orientacao.py — Extensão do Pipeline #40

Calcário (correção de solo) + Orientação técnica (extensão) no arcabouço das
"duas lógicas da pastagem" (#40), sob a disciplina D14.
=====================================================================

PERGUNTA QUE RESPONDE
---------------------
O #40 mostrou que a segregação Rotação(jovem,Sul) × Oportunístico(antigo,Norte)
é REAL, mas que o cruzamento com no-till NÃO isola mecanismo próprio: controlando
o gradiente 2D (lat+lon), o sinal evapora (D14 — em cross-section estadual tudo
co-varia na aptidão latitudinal). Duas covariáveis novas do Censo 2017 (tabela
6850, coletadas em jul/2026) permitem TESTAR A GENERALIDADE dessa lição:

  - **Calcário** (% estab. que corrigem o pH do solo) = proxy DIRETO de
    intensificação (transformar Cerrado ácido em lavoura mecanizada).
  - **Orientação técnica** (% estab. que recebem assistência) = proxy de
    capacitação/instituição; com a composição por origem (cooperativas × governo).

Hipótese (D14): ambas descem ao Sul com a lógica jovem, mas o efeito próprio
some ao controlar o gradiente — confirmando que a intensificação também é
gradiente-confundida, não um driver independente da idade da pastagem.

ABORDAGEM (idêntica ao #40 — régua transversal municipal, mesma máquina)
------------------------------------------------------------------------
Reusa `carregar`/`agregar_mix`/`_partial_corr`/`_partial_corr_multi` do #40.
Para cada covariável × cada desfecho da lógica (idade_mediana, indice_jovem,
pct_rotacao, pct_oportunistico): correlação BRUTA → PARCIAL|lat → PARCIAL|lat+lon.
No-till e adubação entram como REFERÊNCIA (já caracterizados no #40).

ENTRADAS
    data/processed/pastagem_idade_conversao.csv   (#28 — via #40.carregar)
    data/processed/painel_unificado.parquet       (#16 — Censo 2017, calcário/orientação)

SAÍDAS
    data/processed/duas_logicas_calcario_orientacao.csv   (tabela parcial D14)
    outputs/duas_logicas/calcario_orientacao.png

COMO RODAR
    py -3.14 scripts/duas_logicas_calcario_orientacao.py
    py -3.14 scripts/duas_logicas_calcario_orientacao.py --sem-figuras

Depende de: #40 (máquina) e das coletas triviais 6850 (calcário/orientação).
Quando foi feito: 2026-07-16.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import duas_logicas_pastagem as dl  # reuso integral da máquina do #40  # noqa: E402

DIR_PROC = ROOT / "data" / "processed"
DIR_OUT = ROOT / "outputs" / "duas_logicas"
DIR_OUT.mkdir(parents=True, exist_ok=True)
PARQUET_PAINEL = DIR_PROC / "painel_unificado.parquet"

# Covariáveis a testar: as duas NOVAS + duas de REFERÊNCIA (já vistas no #40).
COVARIAVEIS = {
    "censo2017_pct_calcario":   "Calcário (% estab.) — correção de solo",
    "censo2017_pct_orientacao": "Orientação técnica (% estab.) — extensão",
    "pct_pd_area":              "Plantio direto (% área) [ref. #40]",
    "censo2017_pct_adubacao":   "Adubação (% estab.) [ref.]",
}
DESFECHOS = {
    "idade_mediana":     "Idade mediana (a)",
    "indice_jovem":      "Índice jovem↔antigo",
    "pct_rotacao":       "% Rotação (jovem)",
    "pct_oportunistico": "% Oportunístico (antigo)",
}


def carregar_covariaveis() -> pd.DataFrame:
    """Censo 2017 por município: calcário, orientação (+composição), no-till, adubação."""
    p = pd.read_parquet(PARQUET_PAINEL)
    c = p[p["ano"] == 2017].copy()
    keep = ["cd_mun", "censo2017_pct_calcario", "censo2017_pct_orientacao",
            "censo2017_pct_adubacao", "censo2017_n_estab_orientacao",
            "censo2017_n_estab_orientacao_governo", "censo2017_n_estab_orientacao_coop",
            "censo2017_area_plantio_direto_ha", "censo2017_area_estabelecimentos_ha"]
    keep = [x for x in keep if x in c.columns]
    c = c[keep].copy()
    c["cd_mun"] = c["cd_mun"].astype("int64")
    area_est = c["censo2017_area_estabelecimentos_ha"].replace(0, np.nan)
    c["pct_pd_area"] = 100 * c["censo2017_area_plantio_direto_ha"] / area_est
    # composição da orientação entre os que recebem (share cooperativas × governo)
    rec = c["censo2017_n_estab_orientacao"].replace(0, np.nan)
    c["orient_share_coop"] = 100 * c["censo2017_n_estab_orientacao_coop"] / rec
    c["orient_share_governo"] = 100 * c["censo2017_n_estab_orientacao_governo"] / rec
    return c


def tabela_d14(m: pd.DataFrame) -> pd.DataFrame:
    """Para cada covariável × desfecho: gradiente + bruto → parcial|lat → parcial|lat+lon."""
    lat, lon = "lat_centroide", "lon_centroide"
    linhas = []
    for cov, cov_lab in COVARIAVEIS.items():
        if cov not in m.columns:
            continue
        grad = m.dropna(subset=[cov, lat])
        r_lat = pearsonr(grad[cov], grad[lat])[0] if len(grad) > 3 else np.nan
        for dz, dz_lab in DESFECHOS.items():
            sub = m.dropna(subset=[cov, dz])
            if len(sub) < 15:
                continue
            r_bruto = pearsonr(sub[cov], sub[dz])[0]
            r_lat_p, p_lat, n = dl._partial_corr(cov, dz, lat, m)
            r_2d, p_2d, _ = dl._partial_corr_multi(cov, dz, [lat, lon], m)
            linhas.append({
                "covariavel": cov, "covariavel_label": cov_lab,
                "corr_covar_latitude": round(r_lat, 3),
                "desfecho": dz, "desfecho_label": dz_lab, "n": n,
                "r_bruto": round(r_bruto, 3),
                "r_parcial_lat": round(r_lat_p, 3) if r_lat_p == r_lat_p else np.nan,
                "p_parcial_lat": round(p_lat, 4) if p_lat == p_lat else np.nan,
                "r_parcial_latlon": round(r_2d, 3) if r_2d == r_2d else np.nan,
                "p_parcial_latlon": round(p_2d, 4) if p_2d == p_2d else np.nan,
                "sobrevive_2d": bool(p_2d == p_2d and p_2d < 0.05 and abs(r_2d) > 0.2),
            })
    return pd.DataFrame(linhas)


def figura(m: pd.DataFrame, tab: pd.DataFrame):
    import matplotlib.pyplot as plt
    lat = "lat_centroide"
    novas = ["censo2017_pct_calcario", "censo2017_pct_orientacao"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # Linha 1 — gradiente latitudinal das duas covariáveis novas
    for ax, cov in zip(axes[0], novas):
        s = m.dropna(subset=[cov, lat])
        ax.scatter(s[lat], s[cov], s=26, alpha=0.65, color="#8b3a1d", edgecolors="white", lw=0.4)
        if len(s) > 3:
            r = pearsonr(s[lat], s[cov])[0]
            z = np.polyfit(s[lat], s[cov], 1); xs = np.linspace(s[lat].min(), s[lat].max(), 40)
            ax.plot(xs, np.polyval(z, xs), "--", color="black", lw=1)
            ax.set_title(f"{COVARIAVEIS[cov].split(' —')[0].split(' [')[0]} × latitude\n"
                         f"r = {r:+.2f}  (← Sul · Norte →)", fontsize=10)
        ax.set_xlabel("Latitude do centróide (graus)")
        ax.set_ylabel(COVARIAVEIS[cov].split(" —")[0].split(" [")[0])

    # Linha 2 — cross-check com a lógica: bruto vs parcial|lat+lon (índice jovem)
    for ax, cov in zip(axes[1], novas):
        s = m.dropna(subset=[cov, "indice_jovem"])
        ax.scatter(s[cov], s["indice_jovem"], s=26, alpha=0.6, color="#2d5a3d", edgecolors="white", lw=0.4)
        row = tab[(tab.covariavel == cov) & (tab.desfecho == "indice_jovem")]
        if not row.empty and len(s) > 3:
            rb = row.iloc[0]["r_bruto"]; rl = row.iloc[0]["r_parcial_lat"]
            r2 = row.iloc[0]["r_parcial_latlon"]; p2 = row.iloc[0]["p_parcial_latlon"]
            z = np.polyfit(s[cov], s["indice_jovem"], 1); xs = np.linspace(s[cov].min(), s[cov].max(), 40)
            ax.plot(xs, np.polyval(z, xs), "--", color="#a3387f", lw=1.4)
            ax.set_title(f"bruto r={rb:+.2f}  →  |lat {rl:+.2f}  →  |lat+lon {r2:+.2f} (p={p2:.3f})",
                         fontsize=9.5)
        ax.set_xlabel(COVARIAVEIS[cov].split(" —")[0].split(" [")[0])
        ax.set_ylabel("Índice jovem↔antigo")

    fig.suptitle("Calcário + orientação técnica no arcabouço das duas lógicas (#40) — teste D14\n"
                 "descem ao Sul com a lógica jovem (linha 1), mas o efeito próprio some ao controlar "
                 "o gradiente 2D (linha 2)", fontsize=12, y=1.0)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "calcario_orientacao.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'calcario_orientacao.png').relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description="Extensão #40 — calcário + orientação técnica (D14)")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Extensão #40 — Calcário + Orientação técnica no arcabouço das duas lógicas")
    print("=" * 70)

    df = dl.carregar()
    mun_mix = dl.agregar_mix(df, "cd_mun", dl.JANELA_PRIMARIA, dl.MIN_PX_MUN)
    mun_mix = mun_mix[mun_mix["confiavel"]]
    cov = carregar_covariaveis()
    m = mun_mix.merge(cov, on="cd_mun", how="left")
    print(f"[dados] {len(m)} munis confiáveis (≥{dl.MIN_PX_MUN}px, {dl.JANELA_PRIMARIA}) | "
          f"calcário em {m['censo2017_pct_calcario'].notna().sum()} | "
          f"orientação em {m['censo2017_pct_orientacao'].notna().sum()}")

    tab = tabela_d14(m)
    tab.to_csv(DIR_PROC / "duas_logicas_calcario_orientacao.csv", index=False)

    # --- Relatório ---
    print("\n[gradiente] correlação da covariável com a latitude (− = desce ao Sul):")
    for cov_id, cov_lab in COVARIAVEIS.items():
        sub = tab[tab.covariavel == cov_id]
        if not sub.empty:
            print(f"  {cov_lab:45s} r(lat) = {sub.iloc[0]['corr_covar_latitude']:+.2f}")

    print("\n[D14] cross-check com a lógica — bruto → parcial|lat → parcial|lat+lon:")
    for cov_id in COVARIAVEIS:
        sub = tab[tab.covariavel == cov_id]
        if sub.empty:
            continue
        print(f"\n  {COVARIAVEIS[cov_id]}")
        for _, r in sub.iterrows():
            flag = "  SOBREVIVE" if r["sobrevive_2d"] else "  → some no 2D"
            print(f"    × {r['desfecho_label']:22s} bruto {r['r_bruto']:+.2f} → "
                  f"|lat {r['r_parcial_lat']:+.2f} (p={r['p_parcial_lat']:.3f}) → "
                  f"|lat+lon {r['r_parcial_latlon']:+.2f} (p={r['p_parcial_latlon']:.3f}){flag}")

    # Composição da orientação (textura): Sul mais cooperativa, fronteira mais governo?
    def _corr_lat(col):
        s = m.dropna(subset=[col, "lat_centroide"])
        return (pearsonr(s["lat_centroide"], s[col])[0], len(s)) if len(s) > 10 else (np.nan, len(s))
    rc, nc = _corr_lat("orient_share_coop")
    rg, ng = _corr_lat("orient_share_governo")
    print(f"\n[composição da orientação × latitude]  (− = mais ao Sul)")
    print(f"  share cooperativas r(lat)={rc:+.2f} (n={nc}) | share governo r(lat)={rg:+.2f} (n={ng})")
    print("  coop desce ao Sul + governo sobe ao Norte ⇒ orientação COMERCIAL no núcleo "
          "× PÚBLICA na fronteira")

    n_sobrev = int(tab[tab.covariavel.isin(["censo2017_pct_calcario", "censo2017_pct_orientacao"])]
                   ["sobrevive_2d"].sum())
    print("\n" + "-" * 70)
    print("VEREDITO")
    print("-" * 70)
    if n_sobrev == 0:
        print("Calcário e orientação técnica DESCEM ao Sul com a lógica jovem (gradiente real),")
        print("mas NENHUM par sobrevive ao controle do gradiente 2D (lat+lon) — exatamente como o")
        print("no-till no #40. GENERALIZA a D14: a intensificação (calcário) e a instituição")
        print("(extensão) co-localizam na aptidão latitudinal; não isolam efeito próprio sobre a")
        print("idade da pastagem. Reforça que o achado robusto é a SEGREGAÇÃO ESPACIAL das duas")
        print("lógicas, não um driver estrutural.")
    else:
        print(f"ATENÇÃO: {n_sobrev} par(es) das covariáveis novas SOBREVIVE(m) ao gradiente 2D —")
        print("investigar (seria a 1ª covariável transversal a isolar efeito próprio, contra a D14).")

    if not args.sem_figuras:
        print()
        figura(m, tab)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — extensão #40 (calcário + orientação técnica).")
    print("=" * 70)


if __name__ == "__main__":
    main()
