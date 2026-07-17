"""
Pipeline #32 — Centro de massa migratório (mean center) das AMCs de Goiás
=========================================================================

PERGUNTA QUE RESPONDE
---------------------
O centro de gravidade do PASTO e do REBANHO bovino migrou para o norte
enquanto o da AGRICULTURA ficou ancorado no sul? É a figura-manchete da
narrativa de deslocamento de fronteira Sul→Norte (iLUC intra-estadual):
põe LULC (pixels) e economia (rebanho) na mesma latitude, num só mapa.

ABORDAGEM
---------
Para cada variável e cada ano, calcula o CENTRO MÉDIO PONDERADO (mean center,
Lefever 1926) usando os centroides das AMCs como posições e o valor da variável
(ha de pasto/agricultura, cabeças de gado) como peso:

    x̄(t) = Σ_i w_i(t)·x_i / Σ_i w_i(t)   (idem para ȳ)

Acompanha:
  - CENTRO MEDIANO ponderado (center of minimum distance, Weiszfeld 1937),
    robusto ao puxão do cluster agrícola do Sudoeste — ao lado do médio.
  - ELIPSE DE DESVIO-PADRÃO (standard deviational ellipse, Yuill 1971) por ATO:
    resume dispersão e orientação da massa de cada variável em cada período.
  - TABELA DE DESLOCAMENTO N–S (km) por ato + deslocamento líquido 1985→2024.

Por que AMC (Pipeline #25) e não os 246 municípios: a malha AMC é
territorialmente constante 1985–2024, então o centro de massa não sofre o
artefato de emancipação (um filho que se desmembra não cria salto espúrio no
centroide do rebanho — Decisão D11).

CRS: centroides e distâncias em EPSG:5880 (SIRGAS 2000 / Brasil Albers,
EQUAL-AREA). Limitação honesta: Albers preserva área, não distância; para o
deslocamento N–S de algumas dezenas a centenas de km dentro de GO o erro de
escala é pequeno e aceitável para uma leitura descritiva. Latitudes para rótulo
vêm de reprojetar o ponto-centro de volta para EPSG:4674.

LIMITAÇÃO: análise DESCRITIVA. O centroide é sensível ao peso do aglomerado
agrícola do Sudoeste (mas esse é justamente o ponto da narrativa). O mecanismo
(quem→quem por região) é a Camada 2; a defasagem econômica é a Camada 3.

ENTRADAS
    data/processed/painel_amc_goias.parquet   (Pipeline #25)
    data/processed/amc_goias.gpkg             (geometria das AMC, Pipeline #25)

SAÍDAS
    data/processed/centro_massa_anual.csv          (variável×ano: médio + mediano)
    data/processed/centro_massa_elipses.csv        (variável×ato: parâmetros da SDE)
    data/processed/centro_massa_deslocamento.csv   (variável×ato: ΔN/ΔL km, azimute)
    outputs/centro_massa/overview_posicoes.png     (full-GO: posições 1985 vs 2024)
    outputs/centro_massa/trajetorias.png           (small-multiples zoom: trajetória+setas)
    outputs/centro_massa/elipses_por_ato.png       (SDE 1σ por variável, painel por ato)
    outputs/centro_massa/deslocamento_latitude.png (latitude×ano, narrativa N–S)

COMO RODAR
    python scripts/centro_massa.py
    python scripts/centro_massa.py --sem-figuras

Depende de: Pipeline #25 (painel_amc_goias.parquet, amc_goias.gpkg).
Quando foi feito: 2026-06-06.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

# Import tardio de geopandas/matplotlib feito dentro das funções que precisam,
# para o script falhar com mensagem clara se o stack geo não estiver instalado.

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS, CORES_ATO  # noqa: E402

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUT       = ROOT / "outputs" / "centro_massa"
for d in (DIR_PROCESSED, DIR_OUT):
    d.mkdir(parents=True, exist_ok=True)

ARQ_PAINEL = DIR_PROCESSED / "painel_amc_goias.parquet"
ARQ_GEOM   = DIR_PROCESSED / "amc_goias.gpkg"

ARQ_ANUAL        = DIR_PROCESSED / "centro_massa_anual.csv"
ARQ_ELIPSES      = DIR_PROCESSED / "centro_massa_elipses.csv"
ARQ_DESLOCAMENTO = DIR_PROCESSED / "centro_massa_deslocamento.csv"
ARQ_BOOTSTRAP    = DIR_PROCESSED / "centro_massa_bootstrap.csv"

BOOT_B    = 2000   # nº de reamostras do bootstrap (IC do deslocamento/latitude)
BOOT_SEED = 42     # semente p/ reprodutibilidade do bootstrap

CRS_METRICO = 5880   # SIRGAS 2000 / Brasil Polyconic Albers (equal-area, metros)
CRS_GEO     = 4674   # SIRGAS 2000 geográfico (para rótulos de lon/lat)

# Componentes da vegetação natural (consistente com pct_natural_lulc no #25/#16).
COLS_VEG_NATURAL = ["lulc_floresta_nativa_ha", "lulc_formacao_savanica_ha",
                    "lulc_campo_nativo_ha"]

# Variáveis-alvo: chave -> (coluna no painel | None se derivada, rótulo, cor).
VARIAVEIS = {
    "agricultura": ("lulc_agricultura_ha", "Agricultura",     "#c2185b"),  # magenta
    "pastagem":    ("lulc_pastagem_ha",    "Pastagem",        "#e8920c"),  # laranja
    "bovinos":     ("pec_bovinos_cab",     "Rebanho bovino",  "#7a1f1f"),  # vinho
    "veg_natural": (None,                  "Vegetação natural", "#2e7d32"), # verde
}

ANO_INI, ANO_FIM = 1985, 2024


# ---------------------------------------------------------------------------
# 1. Dados: painel + centroides das AMC
# ---------------------------------------------------------------------------

def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Painel AMC (long) + centroides em EPSG:5880 (code_amc, cx, cy)."""
    import geopandas as gpd

    if not ARQ_PAINEL.exists():
        raise FileNotFoundError(f"{ARQ_PAINEL} ausente. Rode construir_amc_goias.py (#25).")
    if not ARQ_GEOM.exists():
        raise FileNotFoundError(f"{ARQ_GEOM} ausente. Rode construir_amc_goias.py (#25).")

    painel = pd.read_parquet(ARQ_PAINEL)

    # Vegetação natural derivada (somável; min_count=1 → all-NaN vira NaN).
    presentes = [c for c in COLS_VEG_NATURAL if c in painel.columns]
    painel["veg_natural_ha"] = painel[presentes].sum(axis=1, min_count=1)
    VARIAVEIS["veg_natural"] = ("veg_natural_ha",) + VARIAVEIS["veg_natural"][1:]

    gdf = gpd.read_file(ARQ_GEOM).to_crs(CRS_METRICO)
    gdf["code_amc"] = gdf["code_amc"].astype(int)
    cent = gdf.geometry.centroid
    centroides = pd.DataFrame({
        "code_amc": gdf["code_amc"].to_numpy(),
        "cx": cent.x.to_numpy(),
        "cy": cent.y.to_numpy(),
    })

    # Cobertura: todo code_amc do painel precisa de centroide.
    faltando = set(painel["code_amc"]) - set(centroides["code_amc"])
    if faltando:
        raise RuntimeError(f"{len(faltando)} AMCs do painel sem centroide: {sorted(faltando)[:10]}")

    painel = painel.merge(centroides, on="code_amc", how="left")
    print(f"[dados] painel AMC {painel.shape[0]:,} linhas | "
          f"{painel['code_amc'].nunique()} AMCs × {painel['ano'].nunique()} anos | "
          f"centroides em EPSG:{CRS_METRICO}")
    return painel, centroides


def metros_para_lonlat(xy: np.ndarray) -> np.ndarray:
    """Converte pontos (N,2) de EPSG:5880 para (lon, lat) em EPSG:4674."""
    import geopandas as gpd
    pts = gpd.GeoSeries(gpd.points_from_xy(xy[:, 0], xy[:, 1]), crs=CRS_METRICO).to_crs(CRS_GEO)
    return np.column_stack([pts.x.to_numpy(), pts.y.to_numpy()])


# ---------------------------------------------------------------------------
# 2. Centros: médio (mean) e mediano (Weiszfeld)
# ---------------------------------------------------------------------------

def mean_center(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """Centro médio ponderado (Lefever 1926)."""
    sw = w.sum()
    return (np.dot(w, x) / sw, np.dot(w, y) / sw)


def median_center(x: np.ndarray, y: np.ndarray, w: np.ndarray,
                  tol: float = 1e-4, max_iter: int = 1000) -> tuple[float, float]:
    """Centro mediano ponderado = ponto que minimiza Σ w_i·||m − p_i|| (center of
    minimum distance). Resolvido por Weiszfeld (1937). Robusto a aglomerados
    extremos (ex.: cluster agrícola do Sudoeste) por usar distância, não quadrado
    da distância. Inicia no centro médio."""
    mx, my = mean_center(x, y, w)
    for _ in range(max_iter):
        d = np.hypot(x - mx, y - my)
        d = np.where(d < 1e-9, 1e-9, d)   # evita divisão por zero se cair sobre um ponto
        ww = w / d
        nx, ny = np.dot(ww, x) / ww.sum(), np.dot(ww, y) / ww.sum()
        if np.hypot(nx - mx, ny - my) < tol:
            return (nx, ny)
        mx, my = nx, ny
    return (mx, my)


def calcular_centros_anuais(painel: pd.DataFrame) -> pd.DataFrame:
    """Centro médio e mediano por (variável, ano). Pesos NaN/≤0 são descartados."""
    linhas = []
    for chave, (col, rotulo, _cor) in VARIAVEIS.items():
        for ano, g in painel.groupby("ano"):
            sub = g[["cx", "cy", col]].dropna()
            sub = sub[sub[col] > 0]
            if len(sub) < 3:
                continue
            x, y, w = sub["cx"].to_numpy(), sub["cy"].to_numpy(), sub[col].to_numpy(float)
            mx, my = mean_center(x, y, w)
            dx, dy = median_center(x, y, w)
            linhas.append({"variavel": chave, "rotulo": rotulo, "ano": int(ano),
                           "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
                           "peso_total": float(w.sum()), "n_amc": int(len(sub))})
    df = pd.DataFrame(linhas)

    # Anexar lon/lat (graus) dos dois centros, reprojetando de uma vez.
    ll_mean = metros_para_lonlat(df[["x_mean", "y_mean"]].to_numpy())
    ll_med  = metros_para_lonlat(df[["x_med", "y_med"]].to_numpy())
    df["lon_mean"], df["lat_mean"] = ll_mean[:, 0], ll_mean[:, 1]
    df["lon_med"],  df["lat_med"]  = ll_med[:, 0],  ll_med[:, 1]
    return df.sort_values(["variavel", "ano"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2b. Incerteza por BOOTSTRAP de AMCs (IC do deslocamento e banda de latitude)
# ---------------------------------------------------------------------------
# POR QUÊ: o centro médio é uma estatística PONTUAL; sem barra de erro não dá
# para saber se um deslocamento pequeno (ex.: vegetação +8 km, ou o +0,2 km da
# agricultura no Ato III) é distinguível de "não se moveu". O bootstrap reamostra
# as 166 AMCs COM REPOSIÇÃO (B vezes) e recomputa o centro médio a cada vez; o
# IC95% percentílico do deslocamento diz se ele sobrevive à composição de unidades.
#
# VETORIZAÇÃO: reamostrar AMCs com reposição equivale a sortear um vetor de
# CONTAGENS ~ Multinomial(n, 1/n). O peso efetivo de cada AMC vira count·valor, e
#     ȳ_b(t) = Σ_i count_i·w_i(t)·y_i / Σ_i count_i·w_i(t).
# Empilhando as B contagens numa matriz C (B×n), tudo vira 2 produtos de matriz
# por variável (C@(y·W) e C@W), sem laço sobre B. Só o centro MÉDIO recebe IC
# (o mediano/Weiszfeld segue reportado como robustez ao cluster, não à amostra).

def bootstrap_incerteza(painel: pd.DataFrame, col_por_chave: dict,
                        rotulos: dict | None = None,
                        B: int = BOOT_B, seed: int = BOOT_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    """IC do centro médio por bootstrap de AMCs (resample c/ reposição).

    col_por_chave: {chave -> coluna do painel}. rotulos: {chave -> rótulo} (opc.).
    Retorna (banda, desloc):
      banda  — (variavel, ano, lat_lo, lat_hi): faixa IC95% da latitude p/ figura.
      desloc — (variavel, janela, dN_km, dN_lo, dN_hi, exclui_zero): IC95% do ΔNorte
               (LÍQUIDO 1º→último ano disponível + cada ato com ambos os extremos).
    """
    rotulos = rotulos or {k: k for k in col_por_chave}
    geo = painel.groupby("code_amc")[["cx", "cy"]].first()
    codes = geo.index.to_numpy()
    n = len(codes)
    CX, CY = geo["cx"].to_numpy(), geo["cy"].to_numpy()
    anos = np.sort(painel["ano"].unique())

    rng = np.random.default_rng(seed)
    counts = rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(float)  # B×n

    banda_rows, desloc_rows = [], []
    for chave, col in col_por_chave.items():
        rot = rotulos.get(chave, chave)
        wpiv = (painel.pivot_table(index="code_amc", columns="ano", values=col,
                                   aggfunc="first")
                      .reindex(index=codes, columns=anos))
        W = wpiv.to_numpy()
        W = np.where(np.isfinite(W) & (W > 0), W, 0.0)   # n×A ; NaN/≤0 → peso 0

        CYW, CXW = CY[:, None] * W, CX[:, None] * W
        DEN = counts @ W                                  # B×A
        with np.errstate(invalid="ignore", divide="ignore"):
            MY = (counts @ CYW) / DEN                      # B×A (metros, norte)
            MX = (counts @ CXW) / DEN
        # Ponto (sem bootstrap) = pesos reais (contagem unitária).
        wsum = W.sum(axis=0)
        with np.errstate(invalid="ignore", divide="ignore"):
            MY_pt = CYW.sum(axis=0) / wsum                 # A (metros)

        # Latitude de cada (b, ano) numa reprojeção só.
        pts = np.column_stack([MX.ravel(), MY.ravel()])
        finito = np.isfinite(pts).all(axis=1)
        lat = np.full(pts.shape[0], np.nan)
        if finito.any():
            lat[finito] = metros_para_lonlat(pts[finito])[:, 1]
        LAT = lat.reshape(B, len(anos))                    # B×A

        anos_ok = anos[wsum > 0]
        for j, ano in enumerate(anos):
            if wsum[j] <= 0:
                continue
            lo, hi = np.nanpercentile(LAT[:, j], [2.5, 97.5])
            banda_rows.append({"variavel": chave, "rotulo": rot, "ano": int(ano),
                               "lat_lo": lo, "lat_hi": hi})

        # Deslocamento ΔNorte (km) com IC — LÍQUIDO + cada ato disponível.
        idx = {int(a): k for k, a in enumerate(anos)}
        janelas = []
        if len(anos_ok):
            janelas.append(("LÍQUIDO", int(anos_ok.min()), int(anos_ok.max())))
        for ato, info in ATOS.items():
            ini, fim = info["inicio"], info["fim"]
            if ini in anos_ok and fim in anos_ok:
                janelas.append((f"Ato {ato}", ini, fim))
        for nome, a0, a1 in janelas:
            i0, i1 = idx[a0], idx[a1]
            dN_b = (MY[:, i1] - MY[:, i0]) / 1000.0
            dN_pt = (MY_pt[i1] - MY_pt[i0]) / 1000.0
            lo, hi = np.nanpercentile(dN_b, [2.5, 97.5])
            desloc_rows.append({"variavel": chave, "rotulo": rot, "janela": nome,
                                "ano_ini": a0, "ano_fim": a1,
                                "dN_km": dN_pt, "dN_lo": lo, "dN_hi": hi,
                                "exclui_zero": bool(lo > 0 or hi < 0)})

    return pd.DataFrame(banda_rows), pd.DataFrame(desloc_rows)


# ---------------------------------------------------------------------------
# 3. Elipse de desvio-padrão (SDE) por ato
# ---------------------------------------------------------------------------

def sde_ponderada(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> dict:
    """Elipse de desvio-padrão ponderada (Yuill 1971), 1σ.

    Orientação θ do eixo principal (a partir do eixo x, anti-horário):
        θ = ½·atan2(2·Σw·dx·dy, Σw·(dx²−dy²))
    Semi-eixos (desvio-padrão ponderado das coords rotacionadas):
        σ_u = sqrt(Σw·u² / Σw),  u = dx·cosθ + dy·sinθ   (eixo a θ)
        σ_v = sqrt(Σw·v² / Σw),  v = −dx·sinθ + dy·cosθ   (eixo a θ+90°)
    """
    sw = w.sum()
    cx, cy = np.dot(w, x) / sw, np.dot(w, y) / sw
    dx, dy = x - cx, y - cy
    A = np.dot(w, dx * dx - dy * dy)
    B = np.dot(w, dx * dy)
    theta = 0.5 * np.arctan2(2 * B, A)
    u = dx * np.cos(theta) + dy * np.sin(theta)
    v = -dx * np.sin(theta) + dy * np.cos(theta)
    sigma_u = np.sqrt(np.dot(w, u * u) / sw)
    sigma_v = np.sqrt(np.dot(w, v * v) / sw)
    return {"cx": cx, "cy": cy, "sigma_u": sigma_u, "sigma_v": sigma_v,
            "theta": theta}


def calcular_elipses(painel: pd.DataFrame) -> pd.DataFrame:
    """SDE por (variável, ato). Peso de cada AMC = MÉDIA da variável sobre os anos
    do ato (distribuição espacial típica do período)."""
    linhas = []
    for chave, (col, rotulo, _cor) in VARIAVEIS.items():
        for ato, info in ATOS.items():
            ini, fim = info["inicio"], info["fim"]
            g = painel[(painel.ano >= ini) & (painel.ano <= fim)]
            peso = (g.groupby("code_amc")
                      .agg(cx=("cx", "first"), cy=("cy", "first"), w=(col, "mean"))
                      .dropna())
            peso = peso[peso["w"] > 0]
            if len(peso) < 5:
                continue
            e = sde_ponderada(peso["cx"].to_numpy(), peso["cy"].to_numpy(),
                              peso["w"].to_numpy(float))
            linhas.append({
                "variavel": chave, "rotulo": rotulo, "ato": ato,
                "ato_titulo": info["titulo"], "ano_ini": ini, "ano_fim": fim,
                "cx": e["cx"], "cy": e["cy"],
                "sigma_maior_km": max(e["sigma_u"], e["sigma_v"]) / 1000,
                "sigma_menor_km": min(e["sigma_u"], e["sigma_v"]) / 1000,
                "theta_deg": np.degrees(e["theta"]),
                "_sigma_u": e["sigma_u"], "_sigma_v": e["sigma_v"], "_theta": e["theta"],
                "n_amc": int(len(peso))})
    df = pd.DataFrame(linhas)
    ll = metros_para_lonlat(df[["cx", "cy"]].to_numpy())
    df["lon"], df["lat"] = ll[:, 0], ll[:, 1]
    return df


# ---------------------------------------------------------------------------
# 4. Tabela de deslocamento N–S
# ---------------------------------------------------------------------------

def tabela_deslocamento(centros: pd.DataFrame) -> pd.DataFrame:
    """ΔNorte/ΔLeste (km), distância total e azimute do centro MÉDIO, por ato
    (do primeiro ao último ano do ato) + deslocamento líquido 1985→2024."""
    linhas = []

    def reg(chave, rotulo, rotulo_ato, a0, a1, p0, p1):
        dnorth = (p1[1] - p0[1]) / 1000          # Δy → km (norte+)
        deast  = (p1[0] - p0[0]) / 1000          # Δx → km (leste+)
        dtot   = np.hypot(dnorth, deast)
        azim   = (np.degrees(np.arctan2(deast, dnorth))) % 360   # 0=N, 90=L
        linhas.append({"variavel": chave, "rotulo": rotulo, "ato": rotulo_ato,
                       "ano_ini": a0, "ano_fim": a1,
                       "dnorte_km": dnorth, "dleste_km": deast,
                       "dtotal_km": dtot, "azimute_deg": azim})

    for chave, g in centros.groupby("variavel"):
        rotulo = g["rotulo"].iloc[0]
        g = g.set_index("ano")
        for ato, info in ATOS.items():
            ini, fim = info["inicio"], info["fim"]
            if ini in g.index and fim in g.index:
                p0 = (g.loc[ini, "x_mean"], g.loc[ini, "y_mean"])
                p1 = (g.loc[fim, "x_mean"], g.loc[fim, "y_mean"])
                reg(chave, rotulo, f"{ato} ({info['titulo']})", ini, fim, p0, p1)
        # Líquido 1985→2024
        if ANO_INI in g.index and ANO_FIM in g.index:
            p0 = (g.loc[ANO_INI, "x_mean"], g.loc[ANO_INI, "y_mean"])
            p1 = (g.loc[ANO_FIM, "x_mean"], g.loc[ANO_FIM, "y_mean"])
            reg(chave, rotulo, "LÍQUIDO", ANO_INI, ANO_FIM, p0, p1)

    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 5. Figuras
# ---------------------------------------------------------------------------

def _carregar_amc_metrico():
    import geopandas as gpd
    g = gpd.read_file(ARQ_GEOM).to_crs(CRS_METRICO)
    g["code_amc"] = g["code_amc"].astype(int)
    return g


def fig_overview(centros: pd.DataFrame) -> None:
    """Mapa full-GO: posição do centro de massa em 1985 (vazado) e 2024 (cheio)
    de cada variável, com seta ligando — a manchete 'mesma latitude'."""
    import matplotlib.pyplot as plt

    amc = _carregar_amc_metrico()
    fig, ax = plt.subplots(figsize=(8.5, 9))
    amc.boundary.plot(ax=ax, color="0.82", linewidth=0.4, zorder=1)
    amc.dissolve().boundary.plot(ax=ax, color="0.45", linewidth=1.1, zorder=2)

    for chave, (col, rotulo, cor) in VARIAVEIS.items():
        g = centros[centros.variavel == chave].set_index("ano")
        if ANO_INI not in g.index or ANO_FIM not in g.index:
            continue
        x0, y0 = g.loc[ANO_INI, "x_mean"], g.loc[ANO_INI, "y_mean"]
        x1, y1 = g.loc[ANO_FIM, "x_mean"], g.loc[ANO_FIM, "y_mean"]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=cor, lw=2.2,
                                    shrinkA=0, shrinkB=0), zorder=4)
        ax.scatter([x0], [y0], s=70, facecolors="white", edgecolors=cor,
                   linewidths=2.0, zorder=5)
        ax.scatter([x1], [y1], s=110, color=cor, edgecolors="white",
                   linewidths=1.2, zorder=6, label=f"{rotulo}")

    ax.set_title("Centro de massa 1985 → 2024 — Goiás (AMC)\n"
                 "○ 1985   ● 2024   (seta = trajetória do centroide ponderado)",
                 fontsize=12, loc="left")
    ax.legend(loc="lower left", frameon=True, fontsize=9, title="2024")
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "overview_posicoes.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'overview_posicoes.png').relative_to(ROOT)}")


def fig_trajetorias(centros: pd.DataFrame) -> None:
    """Small-multiples (uma por variável) com zoom APERTADO na trajetória do
    centroide: linha anual do centro médio + setas por ato + centro mediano
    (tracejado) + rótulos de ano. (As elipses ficam em figura própria, em escala
    estadual — aqui a trajetória é ~80 km e seria esmagada pela elipse de ~200 km.)
    """
    import matplotlib.pyplot as plt

    amc = _carregar_amc_metrico()
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    anos_marco = sorted({ANO_INI} | {info["fim"] for info in ATOS.values()})

    for ax, (chave, (col, rotulo, cor)) in zip(axes.ravel(), VARIAVEIS.items()):
        g = centros[centros.variavel == chave].sort_values("ano")
        if g.empty:
            ax.set_axis_off(); continue

        amc.boundary.plot(ax=ax, color="0.90", linewidth=0.3, zorder=1)

        # Trajetória anual (médio sólido) + mediano (tracejado).
        ax.plot(g["x_mean"], g["y_mean"], "-", color=cor, lw=1.6, alpha=0.95, zorder=4)
        ax.plot(g["x_med"], g["y_med"], "--", color=cor, lw=1.0, alpha=0.5, zorder=3)

        # Setas por ato (centro médio do 1º→último ano do ato).
        gi = g.set_index("ano")
        for ato, info in ATOS.items():
            ini, fim = info["inicio"], info["fim"]
            if ini in gi.index and fim in gi.index:
                ax.annotate("", xy=(gi.loc[fim, "x_mean"], gi.loc[fim, "y_mean"]),
                            xytext=(gi.loc[ini, "x_mean"], gi.loc[ini, "y_mean"]),
                            arrowprops=dict(arrowstyle="-|>",
                                            color=CORES_ATO.get(ato, cor), lw=2.6,
                                            shrinkA=0, shrinkB=0), zorder=5)

        # Marcos: 1985, fronteiras de ato e 2024.
        for a in anos_marco:
            if a in gi.index:
                ax.scatter([gi.loc[a, "x_mean"]], [gi.loc[a, "y_mean"]],
                           s=46, color="white", edgecolors=cor, linewidths=1.7, zorder=6)
                ax.annotate(str(a), (gi.loc[a, "x_mean"], gi.loc[a, "y_mean"]),
                            textcoords="offset points", xytext=(6, 4), fontsize=8.5,
                            color="0.25", zorder=7)

        # Zoom apertado: bbox da trajetória (médio+mediano) + margem.
        xs = np.concatenate([g["x_mean"], g["x_med"]])
        ys = np.concatenate([g["y_mean"], g["y_med"]])
        span = max(xs.max() - xs.min(), ys.max() - ys.min())
        mx = (span - (xs.max() - xs.min())) / 2 + span * 0.22 + 3000
        my = (span - (ys.max() - ys.min())) / 2 + span * 0.22 + 3000
        ax.set_xlim(xs.min() - mx, xs.max() + mx)
        ax.set_ylim(ys.min() - my, ys.max() + my)

        # Deslocamento N–S líquido no título.
        if ANO_INI in gi.index and ANO_FIM in gi.index:
            dn = (gi.loc[ANO_FIM, "y_mean"] - gi.loc[ANO_INI, "y_mean"]) / 1000
            dl = (gi.loc[ANO_FIM, "x_mean"] - gi.loc[ANO_INI, "x_mean"]) / 1000
            sub = f"  ΔN {dn:+.0f} km · ΔL {dl:+.0f} km"
        else:
            sub = ""
        ax.set_title(f"{rotulo}{sub}", fontsize=11.5, loc="left", color=cor)
        ax.set_aspect("equal"); ax.set_axis_off()

    fig.suptitle("Trajetória do centro de massa, 1985→2024 (AMC, EPSG:5880) — zoom; "
                 "— médio, -- mediano; setas por ato", fontsize=12.5, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(DIR_OUT / "trajetorias.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'trajetorias.png').relative_to(ROOT)}")


def fig_elipses_por_ato(elipses: pd.DataFrame) -> None:
    """Elipses de desvio-padrão (1σ) em escala estadual, um painel por ato. Mostra
    a 'pegada' espacial e a orientação da massa de cada variável e como ela sobe
    para o norte ao longo dos atos. Contornos coloridos por variável + centro."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse

    amc = _carregar_amc_metrico()
    contorno = amc.dissolve()
    atos = list(ATOS.keys())
    fig, axes = plt.subplots(1, len(atos), figsize=(5.2 * len(atos), 6.2))

    for ax, ato in zip(np.atleast_1d(axes), atos):
        amc.boundary.plot(ax=ax, color="0.90", linewidth=0.25, zorder=1)
        contorno.boundary.plot(ax=ax, color="0.55", linewidth=0.9, zorder=2)
        sub = elipses[elipses.ato == ato]
        for _, r in sub.iterrows():
            cor = VARIAVEIS[r["variavel"]][2]
            ax.add_patch(Ellipse((r["cx"], r["cy"]),
                                 width=2 * r["_sigma_u"], height=2 * r["_sigma_v"],
                                 angle=np.degrees(r["_theta"]),
                                 facecolor="none", edgecolor=cor, lw=1.8, zorder=4,
                                 label=r["rotulo"]))
            ax.scatter([r["cx"]], [r["cy"]], s=34, color=cor,
                       edgecolors="white", linewidths=0.8, zorder=5)
        info = ATOS[ato]
        ax.set_title(f"Ato {ato} ({info['inicio']}–{info['fim']})\n{info['titulo']}",
                     fontsize=11, color=CORES_ATO.get(ato, "0.2"))
        ax.set_aspect("equal"); ax.set_axis_off()

    handles, labels = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=True, fontsize=10)
    fig.suptitle("Elipse de desvio-padrão (1σ) da massa por variável e ato — "
                 "Goiás (AMC)", fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(DIR_OUT / "elipses_por_ato.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'elipses_por_ato.png').relative_to(ROOT)}")


def fig_latitude(centros: pd.DataFrame, banda: pd.DataFrame | None = None) -> None:
    """Latitude (°) do centro médio vs ano — a narrativa N–S em uma figura.
    Bandas de ato ao fundo; mediano em tracejado fino; faixa sombreada = IC95%
    do centro médio por bootstrap de AMCs (se `banda` fornecida)."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 6))

    # Bandas de ato.
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, info["fim"] + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)
        ax.text((info["inicio"] + info["fim"]) / 2, 0.99, f"Ato {ato}",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=9, color="0.4")

    for chave, (col, rotulo, cor) in VARIAVEIS.items():
        g = centros[centros.variavel == chave].sort_values("ano")
        if g.empty:
            continue
        if banda is not None:
            b = banda[banda.variavel == chave].sort_values("ano")
            if not b.empty:
                ax.fill_between(b["ano"], b["lat_lo"], b["lat_hi"],
                                color=cor, alpha=0.13, lw=0, zorder=1)
        ax.plot(g["ano"], g["lat_mean"], "-", color=cor, lw=2.0, label=rotulo, zorder=3)
        ax.plot(g["ano"], g["lat_med"], "--", color=cor, lw=0.9, alpha=0.5, zorder=2)

    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°, mais alto = mais ao norte)")
    subt = ("linha cheia = centro médio; tracejado = centro mediano (robusto); "
            "faixa = IC95% bootstrap" if banda is not None
            else "linha cheia = centro médio; tracejado = centro mediano (robusto)")
    ax.set_title("Deslocamento norte–sul do centro de massa — Goiás 1985–2024 (AMC)\n"
                 + subt, fontsize=12, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=9, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "deslocamento_latitude.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'deslocamento_latitude.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #32 — centro de massa migratório")
    ap.add_argument("--sem-figuras", action="store_true", help="só CSVs, sem PNGs")
    ap.add_argument("--sem-bootstrap", action="store_true",
                    help="pula o IC por bootstrap (mais rápido)")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #32 — Centro de massa migratório (AMC Goiás, 1985–2024)")
    print("=" * 70)

    painel, _ = carregar_dados()

    centros = calcular_centros_anuais(painel)
    elipses = calcular_elipses(painel)
    desloc  = tabela_deslocamento(centros)

    # Salvar CSVs (descartando colunas auxiliares com prefixo _ das elipses).
    centros.to_csv(ARQ_ANUAL, index=False, encoding="utf-8")
    elipses.drop(columns=[c for c in elipses.columns if c.startswith("_")]) \
           .to_csv(ARQ_ELIPSES, index=False, encoding="utf-8")
    desloc.to_csv(ARQ_DESLOCAMENTO, index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_ANUAL.relative_to(ROOT)}  ({len(centros)} linhas)")
    print(f"[OK] {ARQ_ELIPSES.relative_to(ROOT)}  ({len(elipses)} linhas)")
    print(f"[OK] {ARQ_DESLOCAMENTO.relative_to(ROOT)}  ({len(desloc)} linhas)")

    # Resumo na tela: deslocamento N–S líquido por variável.
    print("\n[resumo] Deslocamento N–S líquido 1985→2024 (km; + = norte):")
    liq = desloc[desloc.ato == "LÍQUIDO"].set_index("rotulo")
    for rotulo, r in liq.iterrows():
        seta = "↑N" if r["dnorte_km"] > 0 else "↓S"
        print(f"  {rotulo:18s} ΔN = {r['dnorte_km']:+7.1f} km {seta} | "
              f"ΔL = {r['dleste_km']:+6.1f} km | total {r['dtotal_km']:5.1f} km "
              f"| azimute {r['azimute_deg']:5.1f}°")

    # Incerteza por bootstrap de AMCs (IC95% do ΔNorte + banda de latitude).
    banda = None
    if not args.sem_bootstrap:
        col_por_chave = {k: v[0] for k, v in VARIAVEIS.items()}
        rotulos = {k: v[1] for k, v in VARIAVEIS.items()}
        banda, desloc_ic = bootstrap_incerteza(painel, col_por_chave, rotulos)
        desloc_ic.to_csv(ARQ_BOOTSTRAP, index=False, encoding="utf-8")
        print(f"[OK] {ARQ_BOOTSTRAP.relative_to(ROOT)}  ({len(desloc_ic)} linhas)")
        print(f"\n[incerteza] IC95% do ΔNorte por bootstrap de AMCs "
              f"(B={BOOT_B}); LÍQUIDO 1985→2024:")
        liq_ic = desloc_ic[desloc_ic.janela == "LÍQUIDO"]
        for _, r in liq_ic.iterrows():
            marca = "≠0 robusto" if r["exclui_zero"] else "INCLUI 0 (dentro do ruído)"
            print(f"  {r['rotulo']:18s} ΔN {r['dN_km']:+6.1f} km "
                  f"| IC95% [{r['dN_lo']:+6.1f}, {r['dN_hi']:+6.1f}] | {marca}")

    if not args.sem_figuras:
        print()
        fig_overview(centros)
        fig_trajetorias(centros)
        fig_elipses_por_ato(elipses)
        fig_latitude(centros, banda)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #32. Camada 1 (keystone) da narrativa Sul→Norte.")
    print("=" * 70)


if __name__ == "__main__":
    main()
