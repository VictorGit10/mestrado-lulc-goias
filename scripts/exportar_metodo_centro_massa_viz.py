"""exportar_metodo_centro_massa_viz.py — dados da página "Por dentro do método: o centro de massa"
===================================================================================================

Alimenta Visualizacao/metodo-centro-de-massa.html, a aba que refaz no navegador a conta do
Pipeline #32 (centro_massa.py) passo a passo, para quem lê o site entender o método. Exporta,
dos MESMOS arquivos e com a MESMA álgebra do #32 e do #55 (robustez_bootstrap_bloco.py):

  - os 166 polígonos das AMC (simplificados, só para desenho) e os centroides em EPSG:5880 (km);
  - os pesos w_it das quatro variáveis, 1985–2024 (regra do #32: NaN/<=0 -> fora);
  - as partições em blocos do #55 (mesmo k-means, mesma semente);
  - os resultados oficiais (CSVs do #32/#55/#43) para a página se conferir contra eles;
  - as zonas do #58 (mesma função `zonas_por_amc`), para a página refazer a ancoragem e a
    decomposição por região, e os resultados oficiais do #58 e do #59 (réguas agrícolas,
    coleções MapBiomas, projeção, anos-extremo, malha municipal);
  - um ajuste polinomial EPSG:5880 -> (lon, lat), só para rotular latitude no navegador.

Nenhum número novo: a página refaz a conta e mostra a diferença para o CSV oficial. Antes de
gravar, o script confere que o centro recalculado com os pesos exportados bate com
centro_massa_anual.csv (tolerância de 10 m) e aborta se não bater.

COMO RODAR
    python scripts/exportar_metodo_centro_massa_viz.py
Saída: Visualizacao/assets/data/metodo_centro_massa.json
Depende de: #25 (painel_amc_goias.parquet, amc_goias.gpkg), #32, #43, #55, #58, #59.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "Visualizacao" / "assets" / "data" / "metodo_centro_massa.json"
PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "scripts"))
from config_periodos import ATOS  # noqa: E402
from robustez_bootstrap_bloco import kmeans_blocos, GRADE_K  # noqa: E402

CRS_METRICO, CRS_GEO = 5880, 4674
VARS = {
    "pastagem":    ("lulc_pastagem_ha", "Pastagem", "ha"),
    "bovinos":     ("pec_bovinos_cab", "Rebanho bovino", "cabeças"),
    "agricultura": ("lulc_agricultura_ha", "Agricultura", "ha"),
    "veg_natural": (None, "Vegetação natural", "ha"),
}
COLS_VEG = ["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha", "lulc_campo_nativo_ha"]


def main() -> None:
    painel = pd.read_parquet(PROC / "painel_amc_goias.parquet")
    painel["veg_natural_ha"] = painel[COLS_VEG].sum(axis=1, min_count=1)

    gdf = gpd.read_file(PROC / "amc_goias.gpkg").to_crs(CRS_METRICO)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    gdf = gdf.sort_values("code_amc").reset_index(drop=True)
    cent = gdf.geometry.centroid          # mesma ordem do #32: projeta, depois centroide
    codes = gdf["code_amc"].to_numpy()
    CX, CY = cent.x.to_numpy(), cent.y.to_numpy()

    # Origem local (km) para a página: canto sudoeste da caixa de GO.
    x0, y0 = np.floor(gdf.total_bounds[0] / 1000) * 1000, np.floor(gdf.total_bounds[1] / 1000) * 1000

    def km(v, o):
        return np.round((np.asarray(v) - o) / 1000.0, 3)

    # Polígonos simplificados (só desenho; o centroide vem do polígono inteiro).
    simp = gdf.geometry.simplify(700, preserve_topology=True)
    polys = []
    for geom in simp:
        partes = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        aneis = []
        for pt in partes:
            xs, ys = pt.exterior.coords.xy
            aneis.append([[float(a), float(b)] for a, b in zip(km(xs, x0), km(ys, y0))])
        polys.append(aneis)
    contorno = gdf.geometry.union_all().simplify(900)
    partes = list(contorno.geoms) if contorno.geom_type == "MultiPolygon" else [contorno]
    contorno_km = []
    for pt in partes:
        xs, ys = pt.exterior.coords.xy
        contorno_km.append([[float(a), float(b)] for a, b in zip(km(xs, x0), km(ys, y0))])

    meta = (painel[["code_amc", "amc_nome_rep", "amc_n_munis"]]
            .drop_duplicates("code_amc").set_index("code_amc").reindex(codes))
    # O nome no painel perdeu a acentuação (U+FFFD). Recupera pelo código IBGE:
    # crosswalk (nome quebrado → cd_mun) + IDHM bruto (cd_mun → nome correto).
    cw = pd.read_csv(PROC / "amc_crosswalk_goias.csv")
    bom = (pd.read_csv(ROOT / "data" / "raw" / "idhm" / "ipea_idhm_adh_goias.csv")
             .drop_duplicates("cd_mun").set_index("cd_mun")["nm_mun"])
    cw["nome_bom"] = cw["cd_mun"].map(bom)
    rep = cw.set_index(["code_amc", "nm_mun"])["nome_bom"]
    meta["amc_nome_rep"] = [rep.get((c, n), n) for c, n in zip(meta.index, meta["amc_nome_rep"])]
    munis = cw.groupby("code_amc")["nome_bom"].apply(lambda s: sorted(s.dropna())).reindex(codes)
    assert not any("�" in str(n) for n in meta["amc_nome_rep"]), "nome ainda quebrado"
    area_km2 = (gdf.geometry.area / 1e6).to_numpy()

    anos = list(range(1985, 2025))
    pesos = {}
    for chave, (col, _r, _u) in VARS.items():
        col = col or "veg_natural_ha"
        W = (painel.pivot_table(index="code_amc", columns="ano", values=col, aggfunc="first")
                   .reindex(index=codes, columns=anos).to_numpy())
        W = np.where(np.isfinite(W) & (W > 0), W, 0.0)   # mesma regra do #32: NaN/≤0 → fora
        pesos[chave] = np.round(W.T, 1).tolist()          # [ano][amc]

    # Conferência: o centro com os pesos exportados bate com o CSV oficial do #32?
    of = pd.read_csv(PROC / "centro_massa_anual.csv")
    pior = 0.0
    for chave in VARS:
        W = np.array(pesos[chave])
        my = (W * CY).sum(1) / W.sum(1)
        ref = of[of.variavel == chave].set_index("ano").reindex(anos)["y_mean"].to_numpy()
        pior = max(pior, np.nanmax(np.abs(my - ref)) / 1000)
    print(f"[conferência] maior diferença de ȳ contra centro_massa_anual.csv: {pior*1000:.2f} m")
    assert pior < 0.01, "a exportação não reproduz o #32"

    # Ajuste EPSG:5880 (km locais) -> lon/lat, polinômio de grau 3.
    tr_inv = Transformer.from_crs(CRS_METRICO, CRS_GEO, always_xy=True)
    tr_dir = Transformer.from_crs(CRS_GEO, CRS_METRICO, always_xy=True)
    gx, gy = np.meshgrid(np.linspace(-60, 800, 40), np.linspace(-60, 800, 40))
    lon, lat = tr_inv.transform(gx.ravel() * 1000 + x0, gy.ravel() * 1000 + y0)
    u, v = gx.ravel() / 100, gy.ravel() / 100
    termos = lambda u, v: np.column_stack([u**i * v**j for i in range(4) for j in range(4 - i)])
    A = termos(u, v)
    c_lat = np.linalg.lstsq(A, lat, rcond=None)[0]
    c_lon = np.linalg.lstsq(A, lon, rcond=None)[0]
    err = max(np.abs(A @ c_lat - lat).max(), np.abs(A @ c_lon - lon).max())
    print(f"[latitude] erro máximo do ajuste: {err*111000:.1f} m")
    expo = [[i, j] for i in range(4) for j in range(4 - i)]

    # Graticula (linhas de lat/lon inteiras) em km locais.
    grat = []
    for la in range(-19, -11):
        los = np.linspace(-54, -45, 60)
        X, Y = tr_dir.transform(los, np.full_like(los, la))
        grat.append({"tipo": "lat", "v": la, "pts": np.column_stack([km(X, x0), km(Y, y0)]).tolist()})
    for lo in range(-53, -45):
        las = np.linspace(-20, -12, 60)
        X, Y = tr_dir.transform(np.full_like(las, lo), las)
        grat.append({"tipo": "lon", "v": lo, "pts": np.column_stack([km(X, x0), km(Y, y0)]).tolist()})

    # Blocos do #55 (mesmo k-means, mesma semente, mesma ordem de AMCs do painel).
    ordem_55 = np.sort(painel["code_amc"].unique())
    assert np.array_equal(ordem_55, codes)
    XY = np.column_stack([CX, CY])
    blocos = {int(k): kmeans_blocos(XY, k).tolist() for k in GRADE_K}

    # Zonas do #58, pela MESMA função do pipeline (regra canônica de região, faixas de latitude).
    from centro_massa_ancoragem import zonas_por_amc, ORDEM_ZONAS, ROTULO_PARTICAO  # noqa: E402
    zn = zonas_por_amc().set_index("code_amc").reindex(codes)
    zonas = {}
    for p, ordem in ORDEM_ZONAS.items():
        assert zn[p].isin(ordem).all(), f"zona fora da ordem em {p}"
        zonas[p] = {"rotulo": ROTULO_PARTICAO[p], "ordem": ordem,
                    "lab": [ordem.index(z) for z in zn[p]]}

    # #58 — decomposição (totais por partição × variável × janela) e IC; resumo da ancoragem.
    dec = pd.read_csv(PROC / "centro_massa_decomposicao.csv")
    dec = dec[dec.variavel.isin(VARS)]
    dec_tot = (dec.groupby(["particao", "variavel", "janela", "ano_ini", "ano_fim"])
                  [["entre_N_km", "dentro_N_km"]].sum().reset_index())
    dec_ic = pd.read_csv(PROC / "centro_massa_decomposicao_ic.csv")
    dec_ic = dec_ic[dec_ic.variavel.isin(VARS)][["k_blocos", "particao", "variavel", "janela",
                                                  "total_N_lo", "total_N_hi", "entre_N_lo", "entre_N_hi",
                                                  "dentro_N_lo", "dentro_N_hi", "frac_entre_N_lo",
                                                  "frac_entre_N_hi", "dentro_exclui_zero"]]
    anc = pd.read_csv(PROC / "centro_massa_ancoragem_resumo.csv")
    anc = anc[anc.variavel.isin(VARS) & (anc.janela == "LÍQUIDO")][
        ["particao", "variavel", "zona", "loo_km_mediana", "puxao_norte_ini_km", "puxao_norte_fim_km",
         "influencia_share_mediana"]]

    # #59 — bateria complementar, séries das réguas agrícolas e das coleções (km locais).
    rob = pd.read_csv(PROC / "centro_massa_robustez_complementar.csv")
    regua = pd.read_csv(PROC / "centro_massa_regua_series.csv").set_index("ano")
    colpx = pd.read_csv(PROC / "centro_massa_colecoes_pixel.csv", dtype={"colecao": str})
    for c in ["9", "10.1", "11"]:
        assert c in set(colpx.colecao), f"coleção {c} ausente do cache do #59"
    reguas = {k: {"ano": s.dropna().index.tolist(), "y": np.round(s.dropna().to_numpy() - y0 / 1000, 3).tolist()}
              for k, s in regua.items()}
    colecoes = {f"{c}|{g}": {"ano": d.ano.tolist(), "y": km(d.y_m, y0).tolist()}
                for (c, g), d in colpx.sort_values("ano").groupby(["colecao", "grupo"])}

    # Resultados oficiais, para a página se conferir.
    boot = pd.read_csv(PROC / "centro_massa_bootstrap.csv")
    bloco = pd.read_csv(PROC / "centro_massa_bootstrap_bloco.csv")
    desl = pd.read_csv(PROC / "centro_massa_deslocamento.csv")
    pix = pd.read_csv(PROC / "centro_massa_pixel_anual.csv")
    X, Y = tr_dir.transform(pix["lon_pixel"].to_numpy(), pix["lat_pixel"].to_numpy())
    pix["x"], pix["y"] = km(X, x0), km(Y, y0)
    oficial = {
        "anual": {k: {"x": km(g.sort_values("ano")["x_mean"], x0).tolist(),
                      "y": km(g.sort_values("ano")["y_mean"], y0).tolist(),
                      "xmed": km(g.sort_values("ano")["x_med"], x0).tolist(),
                      "ymed": km(g.sort_values("ano")["y_med"], y0).tolist(),
                      "lat": g.sort_values("ano")["lat_mean"].round(5).tolist()}
                  for k, g in of.groupby("variavel")},
        "boot": boot.round(3).to_dict("records"),
        "bloco": bloco[["variavel", "k_blocos", "amc_por_bloco", "dN_km", "dN_lo", "dN_hi",
                        "exclui_zero", "dL_km", "dL_lo", "dL_hi", "exclui_zero_leste"]].round(3).to_dict("records"),
        "desloc": desl[["variavel", "ato", "ano_ini", "ano_fim", "dnorte_km", "dleste_km"]]
                      .round(3).to_dict("records"),
        "pixel": {k: {"ano": g["ano"].tolist(), "x": g["x"].tolist(), "y": g["y"].tolist()}
                  for k, g in pix.sort_values("ano").groupby("variavel")},
        "dec58": dec_tot.round(4).to_dict("records"),
        "dec58_ic": dec_ic.round(4).to_dict("records"),
        "anc58": anc.round(4).to_dict("records"),
        "rob59": rob.round(4).replace({np.nan: None}).to_dict("records"),
        "reguas59": reguas,
        "colecoes59": colecoes,
    }

    dados = {
        "origem_m": [float(x0), float(y0)],
        "anos": anos,
        "atos": [{"id": k, "ini": v["inicio"], "fim": v["fim"], "titulo": v["titulo"]}
                 for k, v in ATOS.items()],
        "vars": {k: {"rotulo": r, "unidade": u} for k, (_c, r, u) in VARS.items()},
        "amc": [{"code": int(c), "nome": str(meta.loc[c, "amc_nome_rep"]),
                 "nmun": int(meta.loc[c, "amc_n_munis"]), "munis": munis.loc[c],
                 "area": round(float(a), 1),
                 "cx": float(km(x, x0)), "cy": float(km(y, y0))}
                for c, a, x, y in zip(codes, area_km2, CX, CY)],
        "poly": polys,
        "contorno": contorno_km,
        "grat": grat,
        "pesos": pesos,
        "latfit": {"expo": expo, "lat": c_lat.tolist(), "lon": c_lon.tolist(), "esc": 100},
        "blocos": blocos,
        "zonas": zonas,
        "oficial": oficial,
    }
    js = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    SAIDA.write_text(js, encoding="utf-8")
    print(f"[ok] {SAIDA.relative_to(ROOT)}  ({len(js)/1e6:.2f} MB)")

if __name__ == "__main__":
    main()
