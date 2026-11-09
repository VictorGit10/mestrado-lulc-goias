"""centro_massa_robustez_complementar.py -- Pipeline #59: a bateria que faltava ao centro de massa
==============================================================================================

PERGUNTA QUE RESPONDE
---------------------
O centro de massa do #32 já passou por malha (#43), incerteza (D19, #55), janelas (#35),
desagregação (#44) e régua do Mosaico (D26). Em 28/set/2026, ao revisar a família inteira
para levar o centro de massa à dissertação, ficaram cinco perguntas sem teste:

  A. PROJEÇÃO -- o EPSG:5880 é métrico de compromisso, não de área-igual. O resultado muda
     numa projeção de área-igual ou numa média sobre a esfera?
  B. ANOS-EXTREMO -- o ΔNorte compara 1985 com 2024. E se um dos dois for atípico?
  C. RÉGUA AGRÍCOLA INDEPENDENTE -- a lavoura do MapBiomas perde área para o Mosaico no fim da
     série (D25/D26) e a união lavoura+Mosaico vai ao SUL (−60 km). A soja da SIDRA foi a
     âncora até aqui. E a lavoura temporária inteira da PAM?
  D. MALHA DO REBANHO -- o #43 testou a malha só para as classes com raster. O rebanho é
     tabular e nunca foi medido fora da AMC.
  E. COLEÇÃO -- o erro de classificação do MapBiomas não entra no IC do bootstrap. A
     alternativa que existe é refazer o centro, pixel a pixel, em três coleções (9, 10.1 e
     11): se o deslocamento sobrevive a três classificações diferentes do mesmo satélite, ele
     não é artefato de uma delas.

ABORDAGEM
---------
A. Centroides das AMCs em EPSG:5880 (o do #32), em Albers de área-igual para a América do Sul
   (ESRI:102033) e média esférica (vetor 3D unitário ponderado, reconvertido em latitude; km =
   graus × π/180 × 6.371). Mesmos pesos do #32.
B. ΔNorte com 1 ano, média de 3 e média de 5 anos em cada extremo; e a inclinação da reta de
   mínimos quadrados da latitude do centro contra o ano (× 39 anos), com r². Descritivo: a
   série anual é autocorrelacionada e o r² não é teste de significância.
C. Centro das áreas plantadas da PAM/SIDRA agregadas às AMCs: soja; lavoura temporária sem
   milho; lavoura temporária com milho total (o milho de 2ª safra dupla a área onde há
   safrinha -- declarado, não corrigido). Comparado com a agricultura MapBiomas e a união.
D. Centro pelos 246 municípios (malha atual do IBGE, sem AMC) para as quatro camadas do #32.
   Nos anos anteriores às emancipações o município-filho não tem dado e a massa fica no pai:
   é o artefato que a AMC existe para evitar, e é por isso que o teste é informativo.
E. Cubos de pixel do #28 (EPSG:4326, 30 m, recortados por rasterização das AMCs) das Coleções
   9 (1985–2023), 10.1 (1985–2024) e 11 (1985–2025). Por classe e ano soma-se cos(lat) --
   a área do pixel -- e a posição em EPSG:5880 do centro de uma célula de 16×16 pixels
   (~480 m). Mesmas classes do painel:
       pastagem [15]; agricultura [20,39,40,41,46,47,48,62]; vegetação natural [3,4,12];
       Mosaico [21]; silvicultura [9] (guardada à parte: o #43 a soma na agricultura).
   Validação: a Coleção 10.1 tem de reproduzir o #43.

LIMITE DECLARADO
----------------
E mede a sensibilidade à COLEÇÃO, que é a forma de erro de classificação que se consegue
medir sem verdade de campo. Não é propagação de acurácia: as três coleções compartilham
satélite, grande parte do método e parte das amostras. Concordância entre elas é necessária,
não suficiente.

ENTRADAS
    data/processed/painel_amc_goias.parquet, amc_goias.gpkg, centro_massa_anual.csv   (#25, #32)
    data/processed/painel_unificado.parquet, _geo_muni_goias.gpkg                      (#16)
    data/processed/centro_massa_pixel_anual.csv                                        (#43)
    data/raw/cubo_go{,_col9,_col11}/*.tif                                               (#28)

SAÍDAS
    data/processed/centro_massa_robustez_complementar.csv   (teste × variável × régua × janela)
    data/processed/centro_massa_colecoes_pixel.csv          (cache do bloco E, coleção×grupo×ano)
    data/processed/centro_massa_regua_series.csv            (latitude anual por régua, p/ figura)
    outputs/centro_massa/robustez_complementar.png

COMO RODAR
    python scripts/centro_massa_robustez_complementar.py            # E lido do cache se existir
    python scripts/centro_massa_robustez_complementar.py --refazer-pixel   # relê os cubos (~15 min)

Depende de: #32, #43, #16, #25, #28 (cubos).
Quando foi feito: 2026-09-28.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centro_massa as cm                 # noqa: E402
from config_periodos import ATOS          # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_RAW  = ROOT / "data" / "raw"
DIR_OUT  = ROOT / "outputs" / "centro_massa"

ARQ_SAIDA  = DIR_PROC / "centro_massa_robustez_complementar.csv"
ARQ_PIXEL  = DIR_PROC / "centro_massa_colecoes_pixel.csv"
ARQ_SERIES = DIR_PROC / "centro_massa_regua_series.csv"

ANO_INI, ANO_FIM = cm.ANO_INI, cm.ANO_FIM
R_TERRA_KM = 6371.0
CRS_ALBERS = "ESRI:102033"

VARS4 = {"pastagem": "lulc_pastagem_ha", "bovinos": "pec_bovinos_cab",
         "agricultura": "lulc_agricultura_ha", "veg_natural": "veg_natural_ha"}
ROTULO = {"pastagem": "Pastagem", "bovinos": "Rebanho bovino", "agricultura": "Agricultura",
          "veg_natural": "Vegetação natural"}

COLECOES = {"9": "cubo_go_col9", "10.1": "cubo_go", "11": "cubo_go_col11"}
GRUPOS_PX = {1: ("pastagem", [15]), 2: ("agricultura", [20, 39, 40, 41, 46, 47, 48, 62]),
             3: ("veg_natural", [3, 4, 12]), 4: ("mosaico", [21]), 5: ("silvicultura", [9])}
CELULA = 16                     # pixels por lado da célula de agregação (~480 m)

linhas: list[dict] = []         # tabela única de saída


def reg(teste, variavel, regua, janela, a0, a1, dn_km, **extra):
    linhas.append({"teste": teste, "variavel": variavel, "regua": regua, "janela": janela,
                   "ano_ini": a0, "ano_fim": a1, "dN_km": dn_km, **extra})


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def centro_y(y: np.ndarray, w: np.ndarray) -> float:
    ok = np.isfinite(w) & (w > 0)
    return float(np.dot(w[ok], y[ok]) / w[ok].sum())


def lat_esferica_km(lat: np.ndarray, lon: np.ndarray, w: np.ndarray) -> float:
    """Latitude (em km de arco) da média ponderada de vetores unitários 3D."""
    ok = np.isfinite(w) & (w > 0)
    la, lo = np.radians(lat[ok]), np.radians(lon[ok])
    v = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]) @ w[ok]
    return float(np.arctan2(v[2], np.hypot(v[0], v[1])) * R_TERRA_KM)


def serie_centro(p: pd.DataFrame, col: str, ycol: str = "cy") -> pd.Series:
    """Coordenada N do centro médio (km) por ano, regra de peso do #32."""
    out = {}
    for ano, g in p.groupby("ano"):
        w = g[col].to_numpy(float)
        if (np.isfinite(w) & (w > 0)).sum() >= 3:
            out[int(ano)] = centro_y(g[ycol].to_numpy(), w) / 1e3
    return pd.Series(out).sort_index()


def janelas(anos_ok) -> list[tuple[str, int, int]]:
    a_min, a_max = int(min(anos_ok)), int(max(anos_ok))
    js = [("LÍQUIDO", a_min, a_max)]
    js += [(f"Ato {k}", v["inicio"], v["fim"]) for k, v in ATOS.items()
           if v["inicio"] >= a_min and v["fim"] <= a_max]
    return js


def dN(s: pd.Series, a0: int, a1: int) -> float:
    return float(s.loc[a1] - s.loc[a0])


# ---------------------------------------------------------------------------
# A. Projeção
# ---------------------------------------------------------------------------

def teste_projecao(painel: pd.DataFrame) -> None:
    import geopandas as gpd
    g = gpd.read_file(DIR_PROC / "amc_goias.gpkg")
    g["code_amc"] = g["code_amc"].astype(int)
    alb = g.to_crs(CRS_ALBERS)
    ca = alb.geometry.centroid
    ll = gpd.GeoSeries(ca, crs=CRS_ALBERS).to_crs(4326)
    c = pd.DataFrame({"code_amc": g["code_amc"], "ay": ca.y.to_numpy(),
                      "lat": ll.y.to_numpy(), "lon": ll.x.to_numpy()})
    p = painel.merge(c, on="code_amc")
    print("\n[A] Projeção — ΔNorte (km): EPSG:5880 | Albers área-igual | esfera 3D")
    for v, col in VARS4.items():
        s5880 = serie_centro(p, col, "cy")
        salb = serie_centro(p, col, "ay")
        sesf = pd.Series({int(a): lat_esferica_km(gg.lat.to_numpy(), gg.lon.to_numpy(),
                                                   gg[col].to_numpy(float))
                          for a, gg in p.groupby("ano")})
        for nome, a0, a1 in janelas(s5880.index):
            for regua, s in [("EPSG:5880", s5880), ("Albers (ESRI:102033)", salb), ("esfera 3D", sesf)]:
                reg("A_projecao", v, regua, nome, a0, a1, dN(s, a0, a1))
        r = {rg: next(x["dN_km"] for x in linhas[::-1] if x["teste"] == "A_projecao"
                      and x["variavel"] == v and x["regua"] == rg and x["janela"] == "LÍQUIDO")
             for rg in ["EPSG:5880", "Albers (ESRI:102033)", "esfera 3D"]}
        print(f"  {ROTULO[v]:18s} " + " | ".join(f"{x:+6.1f}" for x in r.values()))


# ---------------------------------------------------------------------------
# B. Anos-extremo e tendência
# ---------------------------------------------------------------------------

def teste_extremos(painel: pd.DataFrame) -> None:
    print("\n[B] Anos-extremo — ΔNorte (km) com 1 / 3 / 5 anos em cada ponta; reta MQO × 39 anos (r²)")
    for v, col in VARS4.items():
        s = serie_centro(painel, col)
        for k in (1, 3, 5):
            d = s.loc[ANO_FIM - k + 1:ANO_FIM].mean() - s.loc[ANO_INI:ANO_INI + k - 1].mean()
            reg("B_extremos", v, f"média de {k} ano(s) nas pontas", "LÍQUIDO", ANO_INI, ANO_FIM, d,
                anos_por_ponta=k)
        b, a = np.polyfit(s.index, s.values, 1)
        r2 = np.corrcoef(s.index, s.values)[0, 1] ** 2
        reg("B_extremos", v, "reta MQO (inclinação × 39)", "LÍQUIDO", ANO_INI, ANO_FIM,
            b * (ANO_FIM - ANO_INI), r2=r2, km_por_decada=b * 10)
        for nome, a0, a1 in janelas(s.index)[1:]:
            ss = s.loc[a0:a1]
            bb = np.polyfit(ss.index, ss.values, 1)[0]
            reg("B_extremos", v, "reta MQO (inclinação × anos)", nome, a0, a1, bb * (a1 - a0),
                km_por_decada=bb * 10)
        vals = [x["dN_km"] for x in linhas if x["teste"] == "B_extremos" and x["variavel"] == v
                and x["janela"] == "LÍQUIDO"]
        print(f"  {ROTULO[v]:18s} " + " | ".join(f"{x:+6.1f}" for x in vals[:3])
              + f" | reta {vals[3]:+6.1f} (r² {r2:.2f}, {b*10:+.1f} km/década)")


# ---------------------------------------------------------------------------
# C. Réguas agrícolas independentes (PAM/SIDRA)
# ---------------------------------------------------------------------------

def teste_reguas_agricolas(painel: pd.DataFrame) -> pd.DataFrame:
    temp = [c for c in painel.columns if c.startswith("agri_") and c.endswith("_ha_plantada")]
    sem_milho = [c for c in temp if "milho" not in c]
    painel = painel.copy()
    # min_count=1: AMC-ano sem nenhuma cultura informada fica NaN (fora), não 0.
    painel["pam_temp_sem_milho"] = painel[sem_milho].sum(axis=1, min_count=1)
    painel["pam_temp_com_milho"] = painel[sem_milho + ["agri_milho_total_ha_plantada"]].sum(axis=1, min_count=1)
    painel["agric_uniao"] = (painel["lulc_agricultura_ha"].fillna(0)
                             + painel["lulc_mosaico_usos_ha"].fillna(0))
    reguas = {
        "MapBiomas agricultura": "lulc_agricultura_ha",
        "MapBiomas agricultura ∪ Mosaico": "agric_uniao",
        "PAM soja plantada": "agri_soja_ha_plantada",
        "PAM temporárias sem milho": "pam_temp_sem_milho",
        "PAM temporárias com milho total": "pam_temp_com_milho",
    }
    series = {}
    print(f"\n[C] Réguas agrícolas — ΔNorte (km); PAM temporárias = {len(sem_milho)} culturas + milho")
    for regua, col in reguas.items():
        s = serie_centro(painel, col)
        series[regua] = s
        for nome, a0, a1 in janelas(s.index):
            reg("C_regua_agricola", "agricultura", regua, nome, a0, a1, dN(s, a0, a1))
        ato = {n: dN(s, a0, a1) for n, a0, a1 in janelas(s.index)}
        print(f"  {regua:34s} {s.index.min()}–{s.index.max()} | "
              + " | ".join(f"{k} {v:+6.1f}" for k, v in ato.items()))
    # Onde fica cada régua em relação ao pasto (o "vão" do #32), em 2024.
    past = serie_centro(painel, "lulc_pastagem_ha")
    for regua, s in series.items():
        reg("C_vao_pasto", "agricultura", regua, "2024", 2024, 2024, float(s.loc[2024] - past.loc[2024]))
    decomposicao_culturas(painel, sem_milho)
    return pd.DataFrame({k: v for k, v in series.items()}).rename_axis("ano")


def decomposicao_culturas(painel: pd.DataFrame, culturas: list[str]) -> None:
    """Por que as temporárias da PAM vão ao sul enquanto a soja vai ao norte?

    Mesma identidade simétrica do #58, com CULTURAS no lugar de zonas:
        ΔC = Σ_c (s_c1 − s_c0)·(C_c0 + C_c1)/2  +  Σ_c (s_c0 + s_c1)/2·(C_c1 − C_c0)
             troca de composição entre culturas   deslocamento de cada cultura
    s_c = fatia da cultura na área plantada; C_c = centro N da cultura.
    """
    for a0, a1 in [(1988, ANO_FIM), (1988, 2000), (2001, ANO_FIM)]:
        rows = []
        for c in culturas:
            est = []
            for a in (a0, a1):
                g = painel[painel.ano == a]
                w = g[c].to_numpy(float)
                ok = np.isfinite(w) & (w > 0)
                A = w[ok].sum()
                est.append((A, np.dot(w[ok], g["cy"].to_numpy()[ok]) / A / 1e3 if A else np.nan))
            rows.append((c, *est[0], *est[1]))
        d = pd.DataFrame(rows, columns=["cultura", "A0", "y0", "A1", "y1"])
        d["s0"], d["s1"] = d.A0 / d.A0.sum(), d.A1 / d.A1.sum()
        d["y0"], d["y1"] = d.y0.fillna(d.y1), d.y1.fillna(d.y0)
        d = d.dropna(subset=["y0"])
        # Parcela por cultura medida em relação ao centro médio dos dois extremos (a soma
        # não depende da referência; a parcela de cada cultura, sim — ver #58, _decompor).
        yref = ((d.s0 * d.y0).sum() + (d.s1 * d.y1).sum()) / 2
        d["composicao"] = (d.s1 - d.s0) * ((d.y0 + d.y1) / 2 - yref)
        d["deslocamento"] = (d.s0 + d.s1) / 2 * (d.y1 - d.y0)
        tot = d.composicao.sum() + d.deslocamento.sum()
        direto = (d.s1 * d.y1).sum() - (d.s0 * d.y0).sum()
        if abs(tot - direto) > 1e-6:
            raise RuntimeError("decomposição por cultura não fecha")
        janela = f"{a0}–{a1}"
        reg("C_culturas", "pam_temporarias", "TOTAL", janela, a0, a1, tot,
            composicao_km=d.composicao.sum(), deslocamento_km=d.deslocamento.sum())
        d["contrib"] = d.composicao + d.deslocamento
        for _, r in d.reindex(d.contrib.abs().sort_values(ascending=False).index).iterrows():
            reg("C_culturas", "pam_temporarias", r.cultura.replace("agri_", "").replace("_ha_plantada", ""),
                janela, a0, a1, r.contrib, composicao_km=r.composicao, deslocamento_km=r.deslocamento,
                fatia_ini=r.s0, fatia_fim=r.s1, area_ini_ha=r.A0, area_fim_ha=r.A1)
        top = d.reindex(d.contrib.abs().sort_values(ascending=False).index).head(5)
        print(f"    temporárias sem milho {janela}: ΔN {tot:+6.1f} = composição {d.composicao.sum():+6.1f}"
              f" + deslocamento {d.deslocamento.sum():+6.1f} | maiores: "
              + ", ".join(f"{r.cultura[5:-12]} {r.contrib:+.1f}" for _, r in top.iterrows()))


# ---------------------------------------------------------------------------
# D. Malha municipal (sem AMC)
# ---------------------------------------------------------------------------

def teste_malha_municipal(painel_amc: pd.DataFrame) -> None:
    import geopandas as gpd
    m = gpd.read_file(DIR_PROC / "_geo_muni_goias.gpkg").to_crs(cm.CRS_METRICO)
    cen = m.geometry.centroid
    geo = pd.DataFrame({"cd_mun": m["code_muni"].astype(int), "cy": cen.y.to_numpy()})
    cols = ["cd_mun", "ano", "lulc_pastagem_ha", "pec_bovinos_cab", "lulc_agricultura_ha"] + cm.COLS_VEG_NATURAL
    p = pd.read_parquet(DIR_PROC / "painel_unificado.parquet", columns=cols)
    p["veg_natural_ha"] = p[cm.COLS_VEG_NATURAL].sum(axis=1, min_count=1)
    p = p.merge(geo, on="cd_mun", how="left")
    if p["cy"].isna().any():
        raise RuntimeError("município sem geometria")
    n85 = p[(p.ano == ANO_INI) & (p.pec_bovinos_cab > 0)].cd_mun.nunique()
    print(f"\n[D] Malha municipal (246 municípios; rebanho informado em {n85} em 1985) — ΔNorte (km): AMC | município")
    for v, col in VARS4.items():
        s_amc = serie_centro(painel_amc, col)
        s_mun = serie_centro(p, col)
        for nome, a0, a1 in janelas(s_amc.index):
            reg("D_malha", v, "AMC (166, #32)", nome, a0, a1, dN(s_amc, a0, a1))
            reg("D_malha", v, "município (246, malha atual)", nome, a0, a1, dN(s_mun, a0, a1))
        print(f"  {ROTULO[v]:18s} {dN(s_amc, ANO_INI, ANO_FIM):+6.1f} | {dN(s_mun, ANO_INI, ANO_FIM):+6.1f}"
              f"   (Ato I: {dN(s_amc, 1985, 2000):+6.1f} | {dN(s_mun, 1985, 2000):+6.1f})")


# ---------------------------------------------------------------------------
# E. Coleções MapBiomas, pixel a pixel
# ---------------------------------------------------------------------------

def _agregar_colecao(pasta: Path, colecao: str, go_4326) -> list[dict]:
    import rasterio
    from rasterio.features import rasterize
    from rasterio.windows import Window
    from pyproj import Transformer

    tr = Transformer.from_crs(4326, cm.CRS_METRICO, always_xy=True)
    lut = np.zeros(256, dtype=np.uint8)
    for gi, (_n, ids) in GRUPOS_PX.items():
        lut[ids] = gi
    G = len(GRUPOS_PX) + 1
    acc = None
    anos = None
    t_ini = time.time()
    tifs = sorted(p for p in pasta.glob("*.tif"))
    for t_i, tif in enumerate(tifs):
        with rasterio.open(tif) as src:
            if anos is None:
                anos = [int(d.split("_")[-1]) for d in src.descriptions]
                acc = np.zeros((len(anos), G, 4))            # Σw, Σw·x, Σw·y, n
            mask = rasterize([(go_4326, 1)], out_shape=(src.height, src.width),
                             transform=src.transform, fill=0, dtype=np.uint8)
            if not mask.any():
                continue
            T = src.transform
            BL = 256                     # linhas por bloco: ~84 MB com 40 bandas (a RAM é curta)
            for top in range(0, src.height, BL):
                h = min(BL, src.height - top)
                mk = mask[top:top + h]
                if not mk.any():
                    continue
                # Só as colunas que tocam Goiás neste bloco.
                cols = np.flatnonzero(mk.any(axis=0))
                c0, c1 = int(cols[0]), int(cols[-1]) + 1
                arr = src.read(window=Window(c0, top, c1 - c0, h))      # (anos, h, w)
                mk = mk[:, c0:c1]
                dentro = np.flatnonzero(mk.ravel())
                comp = arr.reshape(arr.shape[0], -1)[:, dentro]          # (anos, n_dentro) compacto
                del arr
                # Célula de CELULA×CELULA pixels: posição = centro da célula em EPSG:5880.
                rr = np.arange(h) // CELULA
                cc = (c0 + np.arange(c1 - c0)) // CELULA
                cc0 = cc.min()
                ncr, ncc = int(rr.max()) + 1, int(cc.max() - cc0) + 1
                cel = (rr[:, None] * ncc + (cc - cc0)[None, :]).ravel()[dentro]
                lat_row = T.f + (top + np.arange(h) + 0.5) * T.e
                w_d = np.repeat(np.cos(np.radians(lat_row)), c1 - c0)[dentro]   # área ∝ cos(lat)
                clon = T.c + ((cc0 + np.arange(ncc)) * CELULA + CELULA / 2) * T.a
                clat = T.f + (top + np.arange(ncr) * CELULA + CELULA / 2) * T.e
                LON, LAT = np.meshgrid(clon, clat)
                X, Y = tr.transform(LON.ravel(), LAT.ravel())
                ncel = ncr * ncc
                base = cel.astype(np.int64) * G
                for j in range(comp.shape[0]):
                    g = lut[comp[j]]
                    sw = np.bincount(base + g, weights=w_d, minlength=ncel * G).reshape(ncel, G)
                    acc[j, :, 0] += sw.sum(0)
                    acc[j, :, 1] += X @ sw
                    acc[j, :, 2] += Y @ sw
                    acc[j, :, 3] += np.bincount(g, minlength=G)
        print(f"    coleção {colecao}: tile {t_i + 1}/{len(tifs)} ({time.time() - t_ini:.0f} s)", flush=True)
    out = []
    for j, ano in enumerate(anos):
        for gi, (nome, _ids) in GRUPOS_PX.items():
            sw, sx, sy, n = acc[j, gi]
            out.append({"colecao": colecao, "grupo": nome, "ano": ano, "sw": sw,
                        "x_m": sx / sw if sw else np.nan, "y_m": sy / sw if sw else np.nan,
                        "n_px": int(n)})
    return out


def agregar_pixels() -> pd.DataFrame:
    import geopandas as gpd
    go = gpd.read_file(DIR_PROC / "amc_goias.gpkg").to_crs(4326).geometry.union_all()
    rows = []
    for col, pasta in COLECOES.items():
        print(f"  [E] lendo cubo da coleção {col} ({pasta})", flush=True)
        rows += _agregar_colecao(DIR_RAW / pasta, col, go)
    df = pd.DataFrame(rows)
    df.to_csv(ARQ_PIXEL, index=False, encoding="utf-8")
    print(f"  [OK] {ARQ_PIXEL.relative_to(ROOT)}")
    return df


def teste_colecoes(refazer: bool) -> pd.DataFrame | None:
    if refazer or not ARQ_PIXEL.exists():
        px = agregar_pixels()
    else:
        px = pd.read_csv(ARQ_PIXEL, dtype={"colecao": str})
        print(f"\n[E] cache {ARQ_PIXEL.relative_to(ROOT)} (use --refazer-pixel para reler os cubos)")

    # Validação: Coleção 10.1 com a definição de agricultura do #43 (inclui silvicultura)
    # tem de reproduzir o #43 na mesma régua (média do pixel reprojetada para EPSG:5880).
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, cm.CRS_METRICO, always_xy=True)
    ref = pd.read_csv(DIR_PROC / "centro_massa_pixel_anual.csv")
    _, ref["y_m"] = tr.transform(ref["lon_pixel"].to_numpy(), ref["lat_pixel"].to_numpy())
    c10 = px[px.colecao.astype(str) == "10.1"].pivot(index="ano", columns="grupo", values=["sw", "y_m"])
    ag43 = ((c10["sw"]["agricultura"] * c10["y_m"]["agricultura"]
             + c10["sw"]["silvicultura"] * c10["y_m"]["silvicultura"])
            / (c10["sw"]["agricultura"] + c10["sw"]["silvicultura"]))
    print("\n[E] Validação — Coleção 10.1 aqui × #43 (ΔNorte 1985→2024, km, régua EPSG:5880)")
    for v, s_aqui in [("pastagem", c10["y_m"]["pastagem"]), ("agricultura", ag43),
                      ("veg_natural", c10["y_m"]["veg_natural"])]:
        r = ref[ref.variavel == v].set_index("ano")["y_m"]
        d_aqui, d_43 = (s_aqui.loc[2024] - s_aqui.loc[1985]) / 1e3, (r.loc[2024] - r.loc[1985]) / 1e3
        nivel = float((s_aqui - r).abs().max() / 1e3)
        print(f"  {ROTULO[v]:18s} aqui {d_aqui:+6.1f} | #43 {d_43:+6.1f} | Δ {d_aqui - d_43:+5.2f} km"
              f" | maior diferença de nível no ano {nivel:.2f} km")
        reg("E_validacao_43", v, "Col. 10.1 aqui − #43", "LÍQUIDO", 1985, 2024, d_aqui - d_43,
            max_dif_nivel_km=nivel)
        if abs(d_aqui - d_43) > 2.0:
            raise RuntimeError(f"coleção 10.1 não reproduz o #43 em {v}")

    print("\n[E] Coleções — ΔNorte (km), pixel a pixel, régua EPSG:5880")
    series = {}
    for grupo in ["pastagem", "agricultura", "veg_natural", "mosaico"]:
        for col in COLECOES:
            s = px[(px.colecao.astype(str) == col) & (px.grupo == grupo)].set_index("ano")["y_m"] / 1e3
            series[(grupo, col)] = s
            a1c = min(ANO_FIM, int(s.index.max()))
            for nome, a0, a1 in janelas(range(ANO_INI, a1c + 1)):
                reg("E_colecao", grupo, f"Coleção {col}", nome, a0, a1, dN(s, a0, a1))
        comum = 2023      # último ano presente nas três
        vals = {col: dN(series[(grupo, col)], ANO_INI, comum) for col in COLECOES}
        for col, v in vals.items():
            reg("E_colecao", grupo, f"Coleção {col}", "1985–2023 (comum)", ANO_INI, comum, v)
        print(f"  {grupo:12s} 1985→2023: " + " | ".join(f"col {k} {v:+6.1f}" for k, v in vals.items()))
    return px


# ---------------------------------------------------------------------------
# F. Centro mediano × centro médio (registro; o mediano já é calculado pelo #32)
# ---------------------------------------------------------------------------

def teste_mediano() -> None:
    """O #32 reporta o mediano (Weiszfeld) como robustez ao aglomerado, mas nenhuma ficha
    registrava o ΔNorte dele. Lido de centro_massa_anual.csv, sem recalcular."""
    of = pd.read_csv(DIR_PROC / "centro_massa_anual.csv")
    print("\n[F] Mediano × médio — ΔNorte (km), de centro_massa_anual.csv")
    for v in VARS4:
        g = of[of.variavel == v].set_index("ano")
        for nome, a0, a1 in janelas(g.index):
            reg("F_mediano", v, "centro médio", nome, a0, a1, (g.loc[a1, "y_mean"] - g.loc[a0, "y_mean"]) / 1e3)
            reg("F_mediano", v, "centro mediano (Weiszfeld)", nome, a0, a1,
                (g.loc[a1, "y_med"] - g.loc[a0, "y_med"]) / 1e3)
        m = (g.loc[ANO_FIM, "y_mean"] - g.loc[ANO_INI, "y_mean"]) / 1e3
        d = (g.loc[ANO_FIM, "y_med"] - g.loc[ANO_INI, "y_med"]) / 1e3
        print(f"  {ROTULO[v]:18s} médio {m:+6.1f} | mediano {d:+6.1f}")


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def figura(series_agr: pd.DataFrame, px: pd.DataFrame | None) -> None:
    import matplotlib.pyplot as plt
    res = pd.DataFrame(linhas)
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.8))

    # (1) Réguas agrícolas: km relativos a 1985 (ou 1º ano da régua).
    ax = axs[0]
    estilos = {"MapBiomas agricultura": ("#c2185b", "-"),
               "MapBiomas agricultura ∪ Mosaico": ("#7b1fa2", "--"),
               "PAM soja plantada": ("#1565c0", "-"),
               "PAM temporárias sem milho": ("#00838f", "-"),
               "PAM temporárias com milho total": ("#00838f", ":")}
    for regua, (cor, ls) in estilos.items():
        s = series_agr[regua].dropna()
        s = s - s.iloc[0]
        ax.plot(s.index, s.values, color=cor, ls=ls, lw=2,
                label=f"{regua.replace('MapBiomas ', 'MB ')} ({s.values[-1]:+.0f} km)")
    ax.axhline(0, color="#888", lw=.8)
    ax.set_ylim(top=ax.get_ylim()[1] + 45)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_xlim(ANO_INI - 1, ANO_FIM + 1)
    ax.set_ylabel("Deslocamento N–S desde o 1º ano (km; + = norte)")
    ax.set_title("Réguas da agricultura", fontsize=10.5, loc="left")

    # (2) Coleções: pastagem e agricultura, pixel.
    ax = axs[1]
    if px is not None:
        cores = {"pastagem": "#e8920c", "agricultura": "#c2185b"}
        ls_col = {"9": ":", "10.1": "-", "11": "--"}
        for grupo, cor in cores.items():
            for col, ls in ls_col.items():
                s = px[(px.colecao.astype(str) == col) & (px.grupo == grupo)].set_index("ano")["y_m"] / 1e3
                s = s - s.loc[ANO_INI]
                ax.plot(s.index, s.values, color=cor, ls=ls, lw=1.8)
            ax.annotate(ROTULO[grupo], (ANO_FIM + 1, s.values[-1]), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=8, color="#333")
        for col, ls in ls_col.items():
            ax.plot([], [], color="#555", ls=ls, label=f"Coleção {col}")
        ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.axhline(0, color="#888", lw=.8)
    ax.set_xlim(ANO_INI - 1, ANO_FIM + 12)
    ax.set_title("Três coleções MapBiomas, pixel a pixel", fontsize=10.5, loc="left")

    # (3) Placar: ΔNorte LÍQUIDO de pastagem/rebanho/agricultura por teste.
    ax = axs[2]
    casos = [("A_projecao", "EPSG:5880", "5880 (#32)"), ("A_projecao", "Albers (ESRI:102033)", "Albers"),
             ("A_projecao", "esfera 3D", "Esfera"), ("B_extremos", "média de 3 ano(s) nas pontas", "Pontas 3 anos"),
             ("B_extremos", "reta MQO (inclinação × 39)", "Reta MQO"),
             ("D_malha", "município (246, malha atual)", "Municípios")]
    vv = ["pastagem", "bovinos", "agricultura"]
    mk = {"pastagem": ("#e8920c", "o"), "bovinos": ("#7a1f1f", "s"), "agricultura": ("#c2185b", "^")}
    for i, (t, rg, lab) in enumerate(casos):
        for j, v in enumerate(vv):
            q = res[(res.teste == t) & (res.regua == rg) & (res.variavel == v) & (res.janela == "LÍQUIDO")]
            if len(q):
                cor, m = mk[v]
                ax.scatter(q.dN_km.iloc[0], len(casos) - i + (1 - j) * .18, color=cor, marker=m, s=38,
                           label=ROTULO[v] if i == 0 else None, zorder=3)
    ax.set_yticks(range(len(casos), 0, -1), [c[2] for c in casos], fontsize=8.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("ΔNorte 1985→2024 (km)")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_title("O mesmo número por seis caminhos", fontsize=10.5, loc="left")
    for a in axs:
        a.grid(axis="y" if a is not axs[2] else "x", color="#ddd", lw=.6)
        for s_ in ("top", "right"):
            a.spines[s_].set_visible(False)
    fig.text(.01, .01, "Pipeline #59 · robustez complementar do centro de massa (#32) · "
             "AMC 166 / municípios 246 / cubos de pixel 30 m", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, .03, 1, 1))
    DIR_OUT.mkdir(parents=True, exist_ok=True)
    arq = DIR_OUT / "robustez_complementar.png"
    fig.savefig(arq, dpi=150)
    plt.close(fig)
    print(f"[fig] {arq.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(refazer_pixel: bool = False, sem_figuras: bool = False, sem_pixel: bool = False) -> None:
    print("=" * 78)
    print("Pipeline #59 — Robustez complementar do centro de massa (AMC Goiás, 1985–2024)")
    print("=" * 78)
    painel, _ = cm.carregar_dados()

    # Conferência: a série da régua do #32 aqui é a do CSV oficial.
    of = pd.read_csv(DIR_PROC / "centro_massa_anual.csv")
    for v, col in VARS4.items():
        s = serie_centro(painel, col)
        r = of[of.variavel == v].set_index("ano")["y_mean"] / 1e3
        if (s - r).abs().max() > 1e-6:
            raise RuntimeError(f"{v}: série ≠ centro_massa_anual.csv")
    print("[conferência] as séries de partida são as do #32 (|Δ| < 1 mm)")

    teste_projecao(painel)
    teste_extremos(painel)
    series_agr = teste_reguas_agricolas(painel)
    teste_malha_municipal(painel)
    teste_mediano()
    px = None if sem_pixel else teste_colecoes(refazer_pixel)

    res = pd.DataFrame(linhas)
    res.to_csv(ARQ_SAIDA, index=False, encoding="utf-8")
    series_agr.to_csv(ARQ_SERIES, encoding="utf-8")
    print(f"\n[OK] {ARQ_SAIDA.relative_to(ROOT)} ({len(res)} linhas)")
    print(f"[OK] {ARQ_SERIES.relative_to(ROOT)}")
    if not sem_figuras:
        figura(series_agr, px)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refazer-pixel", action="store_true", help="relê os três cubos (~15 min)")
    ap.add_argument("--sem-pixel", action="store_true", help="pula o bloco E")
    ap.add_argument("--sem-figuras", action="store_true")
    main(**vars(ap.parse_args()))
