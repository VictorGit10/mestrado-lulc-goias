"""centro_massa_capacidade.py — Pipeline #53
Centro de massa da CAPACIDADE INSTALADA de armazenagem (CONAB) — fecha a
ressalva de "capacidade instalada" do #45 no eixo espacial do #50
==============================================================================

PERGUNTA QUE RESPONDE
---------------------
O #45 (Trase × LULC) mostrou que a infra EXPORTADORA acompanha a produção mas
NÃO a lidera. Ficou uma ressalva honesta: o Trase mede FLUXO exportador, não
CAPACIDADE INSTALADA — silos/armazéns poderiam estar na dianteira da fronteira
onde o fluxo não está. O #50 pôs crédito/valor na régua de latitude do #32 e
achou que o dinheiro CONSOLIDA o núcleo (crédito ~75 km ao sul do pasto), não
persegue a fronteira. Falta a MESMA pergunta para a capacidade física de
armazenagem:

    O centro de massa da capacidade estática de armazenagem de Goiás está na
    DIANTEIRA da fronteira (norte, junto do pasto/rebanho) ou CONSOLIDA o núcleo
    produtivo (sul, junto do crédito e da lavoura)?

Se a capacidade se senta no núcleo (sul), a ressalva do #45 fica fechada de
forma descritiva e honesta: "nem a capacidade instalada está na dianteira".

POR QUE ISTO E NÃO UM TESTE DE LIDERANÇA TEMPORAL
------------------------------------------------
A fonte fetchável da CONAB não permite testar precedência no tempo:
  - `ArmazensCadastrados.txt` — cadastro ATUAL de armazéns, com município
    (cod_ibge) + capacidade + lat/lon, mas SEM coluna de data. É um snapshot.
  - `exportacao_capacidade_estatica.xls` — série histórica 2005+, mas por UF
    (Ano, UF, Quantidade), NÃO municipal. Série estadual, N≈22, estoque suave
    ⇒ cairia na armadilha D16/#42 (Granger espúrio em série integrada).
A única fonte com município × ano seria a reconstrução do CNPJ por data_abertura
(itens 6/7 do backlog, "engenharia de dado pesada", já DESCARTADOS). Logo, a
frente é convertida de "teste de precedência (inviável)" para "confirmação
espacial descritiva (viável, barata)" — um centroide, no espírito do #50.

ABORDAGEM
---------
Reusa a máquina do #32 (centro_massa.py): mean_center (Lefever 1926),
median_center (Weiszfeld 1937, robusto), metros_para_lonlat, CRS EPSG:5880.
Como o cadastro traz COORDENADAS DE PONTO (o que o LULC/econômico não tem), o
centroide é calculado de DUAS formas:
  (A) PONTO — pesa cada armazém pela capacidade estática na sua própria lat/lon
      (mais fiel; é a vantagem única deste dado).
  (B) AMC — agrega a capacidade por AMC (crosswalk cod_ibge→code_amc, Ehrl 2017)
      e pesa os centroides das 166 AMCs. É o método IDÊNTICO ao #32/#50 →
      comparação de latitude maçã-com-maçã com pasto/agricultura/crédito.
As duas devem quase coincidir (validação cruzada da agregação).

INCERTEZA: bootstrap dos ARMAZÉNS (reamostra as instalações com reposição,
B=2000) → IC95% da latitude do centroide (ponto) e do vão vs a fronteira.

CAUTELAS (herdadas do #50/#32):
- DESCRITIVO. Sem lead-lag entre latitudes (D16). É POSIÇÃO, não precedência.
- SNAPSHOT: a capacidade é a atual (cadastro CONAB). Comparada contra a posição
  RECENTE (último ano disponível) de cada referência do #32/#50, explicitando-o.
- Variável EXTENSIVA (t de capacidade) — centro de massa interpretável.
- Cadastro = armazéns REGISTRADOS na CONAB (padrão nacional de capacidade
  estática); armazenagem intra-fazenda não cadastrada pode ficar de fora.

ENTRADAS
    https://portaldeinformacoes.conab.gov.br/downloads/arquivos/ArmazensCadastrados.txt
    https://portaldeinformacoes.conab.gov.br/downloads/arquivos/exportacao_capacidade_estatica.xls
    data/processed/amc_crosswalk_goias.csv   (#25 — cod_ibge→code_amc)
    data/processed/amc_goias.gpkg            (#25 — geometria/centroides)
    data/processed/centro_massa_anual.csv           (#32 — pasto/agric/rebanho/veg)
    data/processed/centro_massa_economico_anual.csv (#50 — crédito/VA agro/PIB)

SAÍDAS
    data/raw/conab/ArmazensCadastrados.txt          (cache)
    data/raw/conab/exportacao_capacidade_estatica.xls (cache)
    data/processed/centro_massa_capacidade.csv      (centroide ponto+AMC + vãos)
    data/processed/centro_massa_capacidade_uf_serie.csv (série UF 2005+, contexto)
    outputs/centro_massa/capacidade_vs_fronteira.png (latitude: capacidade vs #32/#50)
    outputs/centro_massa/capacidade_mapa.png         (mapa: armazéns + centroides)

COMO RODAR
    py -3.14 scripts/centro_massa_capacidade.py
    py -3.14 scripts/centro_massa_capacidade.py --force      # re-baixa da CONAB
    py -3.14 scripts/centro_massa_capacidade.py --sem-figuras

Depende de: #32 (centro_massa.py), #50 (centroides de referência), #25 (crosswalk
+ geometria). Quando foi feito: 2026-07-18.
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centro_massa as cm  # noqa: E402  — reuso integral da máquina do #32

ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_RAW       = ROOT / "data" / "raw" / "conab"
DIR_OUT       = ROOT / "outputs" / "centro_massa"
for d in (DIR_RAW, DIR_OUT):
    d.mkdir(parents=True, exist_ok=True)

URL_ARMAZENS = "https://portaldeinformacoes.conab.gov.br/downloads/arquivos/ArmazensCadastrados.txt"
URL_SERIE_UF = "https://portaldeinformacoes.conab.gov.br/downloads/arquivos/exportacao_capacidade_estatica.xls"
ARQ_ARMAZENS = DIR_RAW / "ArmazensCadastrados.txt"
ARQ_SERIE_UF = DIR_RAW / "exportacao_capacidade_estatica.xls"

ARQ_CROSSWALK = DIR_PROCESSED / "amc_crosswalk_goias.csv"
ARQ_CM32      = DIR_PROCESSED / "centro_massa_anual.csv"
ARQ_CM50      = DIR_PROCESSED / "centro_massa_economico_anual.csv"

ARQ_OUT       = DIR_PROCESSED / "centro_massa_capacidade.csv"
ARQ_OUT_UF    = DIR_PROCESSED / "centro_massa_capacidade_uf_serie.csv"

KM_POR_GRAU = 111.0   # Δlat° → km (mesma constante do #50)
BOOT_B      = 2000
BOOT_SEED   = 42
UF_ALVO     = "GO"

# Referências (do #32/#50) para o vão de latitude — rótulo e cor p/ figura.
REFS = {
    "pastagem":    ("Pastagem (área)",       "#e8920c", ARQ_CM32),
    "agricultura": ("Agricultura (área)",    "#c2185b", ARQ_CM32),
    "bovinos":     ("Rebanho bovino",        "#7a1f1f", ARQ_CM32),
    "sicor_total": ("Crédito total (SICOR)", "#00695c", ARQ_CM50),
    "va_agro":     ("VA agropecuário",       "#1565c0", ARQ_CM50),
}


# ---------------------------------------------------------------------------
# 1. Download (cache) + parse
# ---------------------------------------------------------------------------

def baixar(url: str, destino: Path, forcar: bool) -> None:
    if destino.exists() and not forcar:
        print(f"[cache] {destino.relative_to(ROOT)} ({destino.stat().st_size:,} bytes)")
        return
    print(f"[download] {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (dissertacao-ciamb)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = r.read()
    destino.write_bytes(dados)
    print(f"[OK] {destino.relative_to(ROOT)} ({len(dados):,} bytes)")


def _f(s):
    """Parse número BR (vírgula decimal) ou vazio → float/NaN."""
    s = str(s).strip()
    if not s or s.lower() in ("nan", "none"):
        return np.nan
    return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)


def carregar_armazens() -> pd.DataFrame:
    """Armazéns de GO com capacidade estática (t) + cod_ibge + lat/lon."""
    df = pd.read_csv(ARQ_ARMAZENS, sep=";", encoding="latin1", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    df["uf"] = df["uf"].str.upper()
    go = df[df["uf"] == UF_ALVO].copy()

    go["capacidade_t"] = go["qtd_capacidade_estatica(t)"].map(_f)
    go["cod_ibge"] = pd.to_numeric(go["cod_ibge"], errors="coerce").astype("Int64")
    # lat/lon usam ponto decimal; troca vírgula por segurança.
    go["latitude"]  = go["latitude"].str.replace(",", ".", regex=False)
    go["longitude"] = go["longitude"].str.replace(",", ".", regex=False)
    go["latitude"]  = pd.to_numeric(go["latitude"], errors="coerce")
    go["longitude"] = pd.to_numeric(go["longitude"], errors="coerce")

    # Só armazéns com capacidade > 0 (peso).
    go = go[go["capacidade_t"] > 0].copy()
    print(f"[dados] {len(go):,} armazéns em {UF_ALVO} com capacidade > 0 | "
          f"capacidade estática total = {go['capacidade_t'].sum()/1e6:.2f} Mt")
    return go


def carregar_serie_uf() -> pd.DataFrame:
    """Série histórica de capacidade estática por UF (contexto temporal, estadual)."""
    try:
        s = pd.read_excel(ARQ_SERIE_UF, header=0)
    except Exception as e:
        print(f"[aviso] não consegui ler a série UF ({e}); seguindo sem ela.")
        return pd.DataFrame()
    s.columns = ["ano", "uf", "cap_mil_t"]
    s["uf"] = s["uf"].astype(str).str.strip().str.upper()
    s["ano"] = pd.to_numeric(s["ano"], errors="coerce")
    s["cap_mil_t"] = pd.to_numeric(s["cap_mil_t"], errors="coerce")
    return s[s["uf"] == UF_ALVO].dropna(subset=["ano"]).sort_values("ano").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. Centroides
# ---------------------------------------------------------------------------

def lonlat_para_metros(lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(lon,lat) EPSG:4674 → (x,y) EPSG:5880 (inverso do cm.metros_para_lonlat)."""
    import geopandas as gpd
    pts = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=cm.CRS_GEO).to_crs(cm.CRS_METRICO)
    return pts.x.to_numpy(), pts.y.to_numpy()


def centroide_ponto(go: pd.DataFrame) -> dict:
    """Centro médio + mediano ponderado pela capacidade, nas coords dos armazéns."""
    sub = go.dropna(subset=["latitude", "longitude", "capacidade_t"])
    # Descarta coords implausíveis (fora do bbox amplo de GO).
    sub = sub[(sub.latitude.between(-20, -12)) & (sub.longitude.between(-54, -45))]
    x, y = lonlat_para_metros(sub["longitude"].to_numpy(), sub["latitude"].to_numpy())
    w = sub["capacidade_t"].to_numpy(float)
    mx, my = cm.mean_center(x, y, w)
    dx, dy = cm.median_center(x, y, w)
    ll = cm.metros_para_lonlat(np.array([[mx, my], [dx, dy]]))
    return {"metodo": "ponto", "n_unidades": int(len(sub)),
            "peso_total_t": float(w.sum()),
            "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
            "lat_mean": ll[0, 1], "lon_mean": ll[0, 0],
            "lat_med": ll[1, 1], "lon_med": ll[1, 0],
            "_x": x, "_y": y, "_w": w}


def centroide_amc(go: pd.DataFrame, crosswalk: pd.DataFrame,
                  centroides: pd.DataFrame) -> dict:
    """Agrega capacidade por AMC (cod_ibge→code_amc) e pesa os centroides das AMCs
    — método IDÊNTICO ao #32/#50 (comparação de latitude maçã-com-maçã)."""
    cw = crosswalk[["cd_mun", "code_amc"]].drop_duplicates()
    m = go.merge(cw, left_on="cod_ibge", right_on="cd_mun", how="left")
    faltando = m[m["code_amc"].isna()]["cod_ibge"].dropna().unique()
    if len(faltando):
        perdido = go[go["cod_ibge"].isin(faltando)]["capacidade_t"].sum()
        print(f"[aviso] {len(faltando)} cod_ibge sem AMC "
              f"({perdido/1e3:.0f} mil t, {perdido/go['capacidade_t'].sum()*100:.1f}% do total): "
              f"{sorted(int(x) for x in faltando)[:8]}")
    m = m.dropna(subset=["code_amc"])
    m["code_amc"] = m["code_amc"].astype(int)
    cap_amc = m.groupby("code_amc")["capacidade_t"].sum().reset_index()
    cap_amc = cap_amc.merge(centroides, on="code_amc", how="left").dropna(subset=["cx", "cy"])
    x, y, w = cap_amc["cx"].to_numpy(), cap_amc["cy"].to_numpy(), cap_amc["capacidade_t"].to_numpy(float)
    mx, my = cm.mean_center(x, y, w)
    dx, dy = cm.median_center(x, y, w)
    ll = cm.metros_para_lonlat(np.array([[mx, my], [dx, dy]]))
    return {"metodo": "amc", "n_unidades": int(len(cap_amc)),
            "peso_total_t": float(w.sum()),
            "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
            "lat_mean": ll[0, 1], "lon_mean": ll[0, 0],
            "lat_med": ll[1, 1], "lon_med": ll[1, 0]}


def bootstrap_latitude_ponto(c: dict, B: int = BOOT_B, seed: int = BOOT_SEED) -> tuple[float, float]:
    """IC95% da latitude do centroide-ponto por reamostragem dos armazéns.
    Reamostrar N unidades com reposição = contagens ~ Multinomial(N, 1/N)."""
    x, y, w = c["_x"], c["_y"], c["_w"]
    n = len(x)
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(float)  # B×n
    cw = counts * w                                     # peso efetivo por réplica
    den = cw.sum(axis=1)
    my = (cw @ y) / den
    mx = (cw @ x) / den
    lat = cm.metros_para_lonlat(np.column_stack([mx, my]))[:, 1]
    return tuple(np.percentile(lat, [2.5, 97.5]))


# ---------------------------------------------------------------------------
# 3. Referências (último ano) + vãos de latitude
# ---------------------------------------------------------------------------

def refs_latitude() -> pd.DataFrame:
    """Latitude do centro médio de cada referência no seu ÚLTIMO ano disponível."""
    linhas = []
    for chave, (rotulo, cor, arq) in REFS.items():
        if not arq.exists():
            print(f"[aviso] referência ausente: {arq.name} ({chave})")
            continue
        d = pd.read_csv(arq)
        g = d[d["variavel"] == chave]
        if g.empty:
            print(f"[aviso] variável {chave} ausente em {arq.name}")
            continue
        r = g.loc[g["ano"].idxmax()]
        linhas.append({"variavel": chave, "rotulo": rotulo, "cor": cor,
                       "ano": int(r["ano"]), "lat_mean": float(r["lat_mean"]),
                       "x_mean": float(r["x_mean"]), "y_mean": float(r["y_mean"])})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 4. Figuras
# ---------------------------------------------------------------------------

def fig_latitude(cap_pt: dict, cap_ci: tuple, refs: pd.DataFrame) -> None:
    """Latitude das séries de referência (#32/#50) + faixa horizontal do centroide
    de capacidade (snapshot). Mostra onde a capacidade se senta na régua N–S."""
    import matplotlib.pyplot as plt
    cm32 = pd.read_csv(ARQ_CM32)
    cm50 = pd.read_csv(ARQ_CM50) if ARQ_CM50.exists() else pd.DataFrame()

    fig, ax = plt.subplots(figsize=(11, 6))
    series = [("pastagem", cm32), ("agricultura", cm32), ("bovinos", cm32)]
    if not cm50.empty:
        series += [("sicor_total", cm50), ("va_agro", cm50)]
    for chave, src in series:
        rotulo, cor, _ = REFS[chave]
        g = src[src["variavel"] == chave].sort_values("ano")
        if g.empty:
            continue
        ax.plot(g["ano"], g["lat_mean"], "-", color=cor, lw=2.0, label=rotulo, zorder=3)

    # Centroide de capacidade: faixa horizontal (IC95%) + linha.
    lo, hi = cap_ci
    ax.axhspan(lo, hi, color="#37474f", alpha=0.14, zorder=1)
    ax.axhline(cap_pt["lat_mean"], color="#263238", lw=2.4, ls="-", zorder=4,
               label="Capacidade de armazenagem (CONAB, atual)")
    ax.axhline(cap_pt["lat_med"], color="#263238", lw=1.0, ls="--", alpha=0.6, zorder=4)

    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°, ↑ = mais ao norte)")
    ax.set_title("Onde se senta a capacidade de armazenagem — Goiás\n"
                 "linha escura = centroide da capacidade estática (snapshot CONAB); "
                 "faixa = IC95% (bootstrap de armazéns)", fontsize=12, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=8.5, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "capacidade_vs_fronteira.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'capacidade_vs_fronteira.png').relative_to(ROOT)}")


def fig_mapa(go: pd.DataFrame, cap_pt: dict, cap_amc: dict, refs: pd.DataFrame) -> None:
    """Mapa: armazéns (pontos ~capacidade) + centroide de capacidade + centroides
    de referência (pasto/agric/rebanho/crédito, último ano)."""
    import matplotlib.pyplot as plt
    import geopandas as gpd
    amc = gpd.read_file(cm.ARQ_GEOM).to_crs(cm.CRS_METRICO)

    fig, ax = plt.subplots(figsize=(8.5, 9))
    amc.boundary.plot(ax=ax, color="0.85", linewidth=0.4, zorder=1)
    amc.dissolve().boundary.plot(ax=ax, color="0.45", linewidth=1.1, zorder=2)

    sub = go.dropna(subset=["latitude", "longitude", "capacidade_t"])
    sub = sub[(sub.latitude.between(-20, -12)) & (sub.longitude.between(-54, -45))]
    px, py = lonlat_para_metros(sub["longitude"].to_numpy(), sub["latitude"].to_numpy())
    tam = 6 + 60 * (sub["capacidade_t"].to_numpy() / sub["capacidade_t"].max()) ** 0.5
    ax.scatter(px, py, s=tam, color="#90a4ae", alpha=0.45, edgecolors="none",
               zorder=3, label=f"Armazéns CONAB (n={len(sub)})")

    # Centroides de referência (último ano).
    for _, r in refs.iterrows():
        ax.scatter([r["x_mean"]], [r["y_mean"]], s=120, color=r["cor"],
                   edgecolors="white", linewidths=1.3, zorder=5,
                   label=f"{r['rotulo']} ({r['ano']})")

    # Centroide da capacidade (ponto e AMC).
    ax.scatter([cap_pt["x_mean"]], [cap_pt["y_mean"]], s=230, marker="*",
               color="#263238", edgecolors="white", linewidths=1.4, zorder=6,
               label="Capacidade — centroide (ponto)")
    ax.scatter([cap_amc["x_mean"]], [cap_amc["y_mean"]], s=130, marker="P",
               color="#263238", edgecolors="white", linewidths=1.1, zorder=6,
               label="Capacidade — centroide (AMC)")

    ax.set_title("Capacidade de armazenagem vs centroides da fronteira e do crédito — Goiás\n"
                 "★ capacidade (ponto)  ✚ capacidade (AMC)", fontsize=12, loc="left")
    ax.legend(loc="lower left", frameon=True, fontsize=8)
    ax.set_aspect("equal"); ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(DIR_OUT / "capacidade_mapa.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'capacidade_mapa.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #53 — centro de massa da capacidade de armazenagem")
    ap.add_argument("--force", action="store_true", help="re-baixa os arquivos da CONAB")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("Pipeline #53 — Centro de massa da capacidade instalada (CONAB) | eixo #50")
    print("=" * 72)

    baixar(URL_ARMAZENS, ARQ_ARMAZENS, args.force)
    baixar(URL_SERIE_UF, ARQ_SERIE_UF, args.force)

    go = carregar_armazens()
    _, centroides = cm.carregar_dados()
    crosswalk = pd.read_csv(ARQ_CROSSWALK)

    cap_pt  = centroide_ponto(go)
    cap_amc = centroide_amc(go, crosswalk, centroides)
    cap_ci  = bootstrap_latitude_ponto(cap_pt)

    print("\n[centroide da capacidade de armazenagem]")
    print(f"  PONTO  lat {cap_pt['lat_mean']:.3f}° (mediano {cap_pt['lat_med']:.3f}°) | "
          f"IC95% [{cap_ci[0]:.3f}, {cap_ci[1]:.3f}] | n={cap_pt['n_unidades']} armazéns")
    print(f"  AMC    lat {cap_amc['lat_mean']:.3f}° (mediano {cap_amc['lat_med']:.3f}°) | "
          f"n={cap_amc['n_unidades']} AMCs | Δ(ponto−AMC) = "
          f"{(cap_pt['lat_mean']-cap_amc['lat_mean'])*KM_POR_GRAU:+.1f} km")

    refs = refs_latitude()
    print("\n[vão de latitude] capacidade (AMC) − referência (km; + = capacidade ao NORTE):")
    print("-" * 72)
    vaos = []
    for _, r in refs.iterrows():
        vao_amc = (cap_amc["lat_mean"] - r["lat_mean"]) * KM_POR_GRAU
        vao_pt  = (cap_pt["lat_mean"]  - r["lat_mean"]) * KM_POR_GRAU
        pos = "ao NORTE de" if vao_amc > 0 else "ao SUL de"
        print(f"  {r['rotulo']:24s}({r['ano']}) lat {r['lat_mean']:.3f}° | "
              f"AMC {vao_amc:+6.1f} km  ponto {vao_pt:+6.1f} km  → capacidade {pos}")
        vaos.append({"referencia": r["variavel"], "ref_rotulo": r["rotulo"],
                     "ref_ano": r["ano"], "ref_lat": r["lat_mean"],
                     "vao_km_amc": vao_amc, "vao_km_ponto": vao_pt})

    # Série UF (contexto temporal, estadual — NÃO espacializável).
    serie = carregar_serie_uf()
    if not serie.empty:
        a0, a1 = serie.iloc[0], serie.iloc[-1]
        cresc = (a1["cap_mil_t"] / a0["cap_mil_t"] - 1) * 100
        print(f"\n[contexto temporal — série UF, NÃO espacial] capacidade estática de GO: "
              f"{a0['cap_mil_t']/1e3:.1f} Mt ({int(a0['ano'])}) → {a1['cap_mil_t']/1e3:.1f} Mt "
              f"({int(a1['ano'])}) = {cresc:+.0f}%")
        serie.to_csv(ARQ_OUT_UF, index=False, encoding="utf-8")
        print(f"[OK] {ARQ_OUT_UF.relative_to(ROOT)} ({len(serie)} anos)")

    # Persistir centroides + vãos.
    linhas = []
    for c in (cap_pt, cap_amc):
        linhas.append({k: v for k, v in c.items() if not k.startswith("_")})
    df_cent = pd.DataFrame(linhas)
    df_cent["lat_ci_lo"] = np.where(df_cent["metodo"] == "ponto", cap_ci[0], np.nan)
    df_cent["lat_ci_hi"] = np.where(df_cent["metodo"] == "ponto", cap_ci[1], np.nan)
    df_vao = pd.DataFrame(vaos)
    # Salva os dois blocos num CSV só (centroides no topo, vãos abaixo via merge amplo).
    df_cent.to_csv(ARQ_OUT, index=False, encoding="utf-8")
    df_vao.to_csv(ARQ_OUT.with_name("centro_massa_capacidade_vaos.csv"), index=False, encoding="utf-8")
    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)} ({len(df_cent)} centroides)")
    print(f"[OK] {ARQ_OUT.with_name('centro_massa_capacidade_vaos.csv').relative_to(ROOT)} ({len(df_vao)} vãos)")

    if not args.sem_figuras:
        print()
        fig_latitude(cap_pt, cap_ci, refs)
        fig_mapa(go, cap_pt, cap_amc, refs)

    print("\n" + "=" * 72)
    print("CONCLUÍDO — Pipeline #53. Fecha a ressalva de capacidade instalada do #45")
    print("no eixo espacial do #50 (descritivo).")
    print("=" * 72)


if __name__ == "__main__":
    main()
