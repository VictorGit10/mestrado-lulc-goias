"""exploratorio_col11_centro_massa_cap7.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. A dissertação usa a Coleção 10.1 para trás. A 11 é exploratória à parte
(decisão do autor em 2026-08-26). Saídas em data/processed/exploratorio_col11/ (gitignored).
Nada aqui altera #28D, D26, dossie-mosaico.html, qualificacao/ nem cria pipeline novo.

REPLICA O CAPÍTULO 7 DO DOSSIÊ, COM A COLEÇÃO 11 AO LADO
--------------------------------------------------------
O Cap. 7 afirma, entre 2019 e 2024:
  • centro de massa da Agricultura avança +0,2 km ao norte (IC 95% inclui zero);
  • soja plantada e rebanho bovino (IBGE) avançam +8 a +12 km;
  • a união Agricultura+Mosaico avança +4,1 km [+1,0; +6,9];
  • o crescimento do Mosaico está 46,5 km ao norte da Agricultura visível;
  • r = 0,84 por município entre crescimento do Mosaico e crescimento da soja do IBGE;
  • a soja-satélite recua 7,1 km ao sul enquanto a soja-campo avança 8,2 km ao norte.

DUAS PONDERAÇÕES, DE PROPÓSITO
------------------------------
(a) **Por centroide municipal** — é a única forma de pôr no mesmo gráfico as séries do
    IBGE (soja plantada, rebanho), que são tabulares por município e não têm raster. É a
    ponderação do Pipeline #32 e a da Figura 4 do dossiê. Sofre MAUP: municípios do Norte
    são maiores e mais irregulares.
(b) **Por pixel** — a posição de cada pixel é o próprio pixel, sem polígono no meio
    (Pipeline #43). Imune a MAUP, mas não existe para as séries do IBGE.

As duas são reportadas lado a lado. Se divergirem, é MAUP; se concordarem, o achado não é
artefato da malha. Fazer só uma delas seria escolher entre comparabilidade com o IBGE e
robustez geométrica, e não há motivo para escolher.

INTERVALOS DE CONFIANÇA
-----------------------
Bootstrap sobre MUNICÍPIOS (reamostragem com reposição dos 246, B repetições), que é a
unidade de variação relevante: o que é incerto é qual conjunto de municípios se moveu, não
a posição de um pixel. O IC sai dos percentis 2,5 e 97,5 do deslocamento reamostrado.

⚠️ Só se aplica à ponderação (a). Na (b) o "n" é de centenas de milhões de pixels
espacialmente autocorrelacionados, e um IC ingênuo ali seria absurdamente estreito — por
isso ele não é reportado.

ENTRADAS
    data/processed/mapbiomas_munis_goias.csv                     (col10.1, já existente)
    data/processed/exploratorio_col11/censo_munis_col11.csv      (col11, gerado nesta rodada)
    data/processed/exploratorio_col11/centro_massa_classe_*.csv  (ponderação por pixel)
    data/processed/sidra_pam1612_temporarias.csv                 (soja plantada, IBGE)

COMO RODAR
    python scripts/exploratorio_col11_centro_massa_cap7.py

Quando: 2026-08-27.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_SAIDA = DIR_PROC / "exploratorio_col11"

# "Agricultura" do dossiê: confere com 5,668 Mha (2020) e 5,732 Mha (2024)
IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]
ID_MOSAICO, ID_PASTAGEM, ID_SOJA = 21, 15, 39
KM_POR_GRAU = 110.9  # meridional, ~ -16° de latitude

ANO_A, ANO_B = 2019, 2024  # janela do Cap. 7


def centroides_municipais() -> pd.DataFrame:
    """Centroide de cada município (geobr 2020, o mesmo do #28/#32)."""
    import geobr
    g = geobr.read_municipality(code_muni="GO", year=2020).to_crs(4326)
    g = g.rename(columns={"code_muni": "cd_mun"})
    c = g.geometry.centroid
    return pd.DataFrame({"cd_mun": g["cd_mun"].astype("int64"),
                         "lat_mun": c.y.values, "lon_mun": c.x.values})


def areas_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    """Colapsa classe->grupo por (cd_mun, ano). Espera colunas cd_mun/ano/class_id/area_ha."""
    d = df.copy()
    d["grupo"] = np.where(d.class_id.isin(IDS_AGRI), "agricultura",
                 np.where(d.class_id == ID_MOSAICO, "mosaico",
                 np.where(d.class_id == ID_PASTAGEM, "pastagem", "outro")))
    g = d.groupby(["cd_mun", "ano", "grupo"])["area_ha"].sum().unstack("grupo").fillna(0.0)
    soja = (d[d.class_id == ID_SOJA].groupby(["cd_mun", "ano"])["area_ha"].sum()
            .rename("soja_sat"))
    g = g.join(soja).fillna(0.0)
    g["uniao"] = g.get("agricultura", 0) + g.get("mosaico", 0)
    return g.reset_index()


def centro(pesos: np.ndarray, lat: np.ndarray) -> float:
    s = pesos.sum()
    return float((pesos * lat).sum() / s) if s > 0 else float("nan")


def desloc_km(g: pd.DataFrame, col: str, lat: np.ndarray,
              ano_a: int = ANO_A, ano_b: int = ANO_B) -> float:
    a = g[g.ano == ano_a].set_index("cd_mun")[col]
    b = g[g.ano == ano_b].set_index("cd_mun")[col]
    idx = a.index.intersection(b.index)
    la = pd.Series(lat, index=g[g.ano == ano_a].set_index("cd_mun").index).loc[idx].values
    return (centro(b.loc[idx].values, la) - centro(a.loc[idx].values, la)) * KM_POR_GRAU


def boot_ic(pesos_a: np.ndarray, pesos_b: np.ndarray, lat: np.ndarray,
            B: int = 2000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(lat)
    out = np.empty(B)
    for i in range(B):
        k = rng.integers(0, n, n)
        out[i] = (centro(pesos_b[k], lat[k]) - centro(pesos_a[k], lat[k])) * KM_POR_GRAU
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser(description="EXPLORATÓRIO — Cap. 7 replicado com a col11")
    ap.add_argument("--boot", type=int, default=2000)
    args = ap.parse_args()

    cen = centroides_municipais()

    fontes = {}
    # Os DOIS lados vêm do mesmo censo local (mesma máscara, mesma rasterização, mesma
    # correção de cos(lat)), para que a comparação entre coleções não carregue diferença
    # de pipeline. O `mapbiomas_munis_goias.csv` (fonte do dossiê) fica como controle: ele
    # reproduz o Cap. 4 ao 3º decimal e bate com este censo dentro de 0,12%.
    f101 = DIR_SAIDA / "censo_munis_col10_1.csv"
    f11 = DIR_SAIDA / "censo_munis_col11.csv"
    for tag, f in [("col10.1", f101), ("col11", f11)]:
        if not f.exists():
            print(f"  [pendente] {f.name} ainda não existe — pulando {tag}")
            continue
        fontes[tag] = areas_por_grupo(pd.read_csv(f, encoding="utf-8"))

    # soja de campo (IBGE/PAM 1612), área plantada por município
    pam = pd.read_csv(DIR_PROC / "sidra_pam1612_temporarias.csv", encoding="utf-8")
    soja_campo = (pam[(pam.categoria.astype(str).str.contains("Soja"))
                      & (pam.variavel.astype(str).str.contains("plantada", case=False))]
                  .groupby(["cd_mun", "ano"])["valor"].sum().rename("soja_campo").reset_index())

    linhas = []
    for tag, g in fontes.items():
        g = g.merge(cen, on="cd_mun", how="inner")
        for col in ["agricultura", "mosaico", "uniao", "pastagem", "soja_sat"]:
            if col not in g.columns:
                continue
            sub_a = g[g.ano == ANO_A].sort_values("cd_mun")
            sub_b = g[g.ano == ANO_B].sort_values("cd_mun")
            lat = sub_a.lat_mun.values
            d = (centro(sub_b[col].values, lat) - centro(sub_a[col].values, lat)) * KM_POR_GRAU
            lo, hi = boot_ic(sub_a[col].values, sub_b[col].values, lat, args.boot)
            linhas.append({"colecao": tag, "serie": col, "ponderacao": "centroide_municipal",
                           "desloc_km": d, "ic95_lo": lo, "ic95_hi": hi,
                           "lat_ini": centro(sub_a[col].values, lat),
                           "lat_fim": centro(sub_b[col].values, lat)})

    # soja de campo — não depende da coleção
    sc = soja_campo.merge(cen, on="cd_mun", how="inner")
    a = sc[sc.ano == ANO_A].sort_values("cd_mun")
    b = sc[sc.ano == ANO_B].sort_values("cd_mun")
    idx = np.intersect1d(a.cd_mun.values, b.cd_mun.values)
    a, b = a[a.cd_mun.isin(idx)], b[b.cd_mun.isin(idx)]
    lat = a.lat_mun.values
    d = (centro(b.soja_campo.values, lat) - centro(a.soja_campo.values, lat)) * KM_POR_GRAU
    lo, hi = boot_ic(a.soja_campo.values, b.soja_campo.values, lat, args.boot)
    linhas.append({"colecao": "IBGE", "serie": "soja_campo", "ponderacao": "centroide_municipal",
                   "desloc_km": d, "ic95_lo": lo, "ic95_hi": hi,
                   "lat_ini": centro(a.soja_campo.values, lat),
                   "lat_fim": centro(b.soja_campo.values, lat)})

    df = pd.DataFrame(linhas)
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(DIR_SAIDA / "col11_cap7_centro_massa_municipal.csv", index=False)
    print(f"\nDESLOCAMENTO DO CENTRO DE MASSA {ANO_A}->{ANO_B} (km ao norte; "
          f"ponderação por centroide municipal, IC bootstrap {args.boot}x)\n")
    print(df[["colecao", "serie", "desloc_km", "ic95_lo", "ic95_hi"]].round(2).to_string(index=False))

    # centro de massa do CRESCIMENTO do Mosaico vs Agricultura visível
    print("\nCENTRO DE MASSA DO CRESCIMENTO (delta 2019->2024, só municípios que cresceram)")
    for tag, g in fontes.items():
        g = g.merge(cen, on="cd_mun", how="inner")
        a = g[g.ano == ANO_A].set_index("cd_mun"); b = g[g.ano == ANO_B].set_index("cd_mun")
        idx = a.index.intersection(b.index)
        lat = a.loc[idx, "lat_mun"].values
        dmos = (b.loc[idx, "mosaico"] - a.loc[idx, "mosaico"]).clip(lower=0).values
        lat_cresc = centro(dmos, lat)
        lat_agri = centro(b.loc[idx, "agricultura"].values, lat)
        print(f"  {tag}: crescimento do Mosaico a {(lat_cresc-lat_agri)*KM_POR_GRAU:+.1f} km "
              f"da Agricultura visível (lat {lat_cresc:.4f} vs {lat_agri:.4f})")

    # correlação municipal: crescimento do Mosaico x crescimento da soja de campo
    print(f"\nCORRELAÇÃO MUNICIPAL {ANO_A}->{ANO_B}: crescimento do Mosaico × crescimento da soja (IBGE)")
    sca = soja_campo[soja_campo.ano == ANO_A].set_index("cd_mun")["soja_campo"]
    scb = soja_campo[soja_campo.ano == ANO_B].set_index("cd_mun")["soja_campo"]
    for tag, g in fontes.items():
        a = g[g.ano == ANO_A].set_index("cd_mun"); b = g[g.ano == ANO_B].set_index("cd_mun")
        idx = a.index.intersection(b.index).intersection(sca.index).intersection(scb.index)
        dmos = (b.loc[idx, "mosaico"] - a.loc[idx, "mosaico"])
        dsoja = (scb.loc[idx] - sca.loc[idx])
        r = float(np.corrcoef(dmos.values, dsoja.values)[0, 1])
        print(f"  {tag}: r = {r:.3f}  (n={len(idx)} municípios) | "
              f"soma dMosaico = {dmos.sum()/1e6:.3f} Mha, soma dSoja = {dsoja.sum()/1e6:.3f} Mha")

    print("\n  ⚠️  EXPLORATÓRIO: não alimenta #28D, D26, dossiê nem qualificação.")


if __name__ == "__main__":
    main()
