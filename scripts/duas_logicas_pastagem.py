"""duas_logicas_pastagem.py — Pipeline #40

As DUAS LÓGICAS da pastagem: espacialização dos mecanismos de conversão
pasto→agricultura (#28) e cruzamento com plantio direto (#27/Censo 2017).

O #28 classificou cada pixel não-censurado em um mecanismo (Premeditado curto /
Rotação / Oportunístico clássico / Ambíguo) e provou a bimodalidade ~5a/~22a por
GMM, mas parou na mesorregião e nunca cruzou com a ESTRUTURA do sistema agrícola.
Este pipeline:

  A. AGREGA a mistura de mecanismos por AMC e por município (janela recente),
     construindo um índice contínuo "jovem↔antigo" e a lógica dominante.
  B. ESPACIALIZA: mapas coropléticos AMC (mesma malha EPSG:5880 do #32-#39) +
     scatter de pixels por mecanismo (textura fina) + gradiente latitudinal.
  C. CRUZA com PLANTIO DIRETO (Censo 2017, % da área dos estabelecimentos) — o
     teste estrutural: o #28 mostrou que a idade NÃO responde a choques de fluxo
     municipais (SICOR / VA agro); responde à estrutura do sistema (no-till = proxy
     de integração lavoura-pecuária / rotação)?
  D. TIPOLOGIA "carreira da terra" — classificação municipal (giro de lavoura /
     trampolim de fronteira / reserva ativada / misto), regra + k-means de robustez.

Saídas:
  data/processed/duas_logicas_amc.csv
  data/processed/duas_logicas_municipal.csv
  data/processed/duas_logicas_cruzamento.csv
  outputs/duas_logicas/*.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from estatistica_ponderada import mediana as _mediana_p, media as _media_p

CSV_IDADE = ROOT / "data" / "processed" / "pastagem_idade_conversao.csv"
CENSO_IDADE = ROOT / "data" / "processed" / "pastagem_idade_censo.parquet"
CSV_CROSSWALK = ROOT / "data" / "processed" / "amc_crosswalk_goias.csv"
CSV_MESO = ROOT / "data" / "processed" / "mapeamento_mesorregioes.csv"
GPKG_AMC = ROOT / "data" / "processed" / "amc_goias.gpkg"
PARQUET_PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
DIR_OUT = ROOT / "outputs" / "duas_logicas"
DIR_OUT.mkdir(parents=True, exist_ok=True)
DIR_PROC = ROOT / "data" / "processed"

# ── Parâmetros ──────────────────────────────────────────────────────────────
# Janela primária: regime moderno (consolidação Ato II tardio + Ato III), censura
# baixa, Censo 2017 no meio. As demais entram como robustez do cruzamento.
JANELA_PRIMARIA = (2010, 2024)
JANELAS_ROBUSTEZ = [(2016, 2024), (2010, 2024), (1986, 2024)]
MIN_PX_MUN = 20   # mínimo de pixels não-censurados p/ entrar no scatter municipal
MIN_PX_AMC = 15   # idem para o mapa AMC

JOVEM_MAX = 8     # idade ≤ 8a  → lógica "jovem" (giro/trampolim)  [regra do #28]
ANTIGO_MIN = 20   # idade ≥ 20a → lógica "antiga" (reserva ativada) [regra do #28]

COR_MEC = {
    "Rotação": "#d95f02",
    "Premeditado curto": "#e7c019",
    "Oportunístico clássico": "#1b6e3d",
    "Mosaico de usos": "#c98a3a",
    "Ambíguo / Outro": "#bdbdbd",
}
COR_TIPO = {
    "Giro de lavoura (ILP/rotação)": "#d95f02",
    "Trampolim de fronteira": "#e7c019",
    "Reserva ativada (oportunístico)": "#1b6e3d",
    "Misto / transição": "#9e9e9e",
}


# ── Carga e classificação ───────────────────────────────────────────────────
def classificar_mecanismo(df: pd.DataFrame) -> pd.DataFrame:
    """Regra de decisão do #28 (analise_reserva_terra.classificar_mecanismo)."""
    df = df.copy()
    df["mecanismo"] = "Ambíguo / Outro"
    nc = ~df["censurado"]
    jovem = df["idade_pastagem_anos"] <= JOVEM_MAX
    antigo = df["idade_pastagem_anos"] >= ANTIGO_MIN
    vn = df["origem_anterior"] == "vegetacao_natural"
    ag = df["origem_anterior"] == "agricultura"
    mo = df["origem_anterior"] == "mosaico"
    df.loc[nc & jovem & vn, "mecanismo"] = "Premeditado curto"
    df.loc[nc & jovem & ag, "mecanismo"] = "Rotação"
    df.loc[nc & antigo & vn, "mecanismo"] = "Oportunístico clássico"
    # Mosaico de Usos (classe 21) tem categoria PRÓPRIA, igual ao #28 §4. Até
    # 21/jul/2026 a classe faltava no GRUPO_MAP da coleta e esses pixels vinham
    # rotulados como censurados — o #40 simplesmente não os via (−31% dos
    # não-censurados). Diluí-los em "Ambíguo" reintroduziria o mesmo apagamento
    # por outro caminho: são ~12% das conversões e a categoria mais próxima do
    # mecanismo de rotação, justamente o que este pipeline tenta espacializar.
    df.loc[nc & mo, "mecanismo"] = "Mosaico de usos"
    df.loc[df["censurado"], "mecanismo"] = "Censurado à esquerda"
    return df


def carregar(fonte: str = "censo") -> pd.DataFrame:
    """Devolve sempre um DataFrame com coluna `peso`, venha de onde vier.

    `fonte="censo"`   → censo de pixels do #28; peso = n_pixels da célula, e
                        lat/lon = centroide EXATO dos pixels daquela célula
                        (`lat_media`/`lon_media`, ver docstring do
                        processa_cubo_idade). Não é o centroide do município.
    `fonte="amostra"` → amostra legada do #28A; peso = 1, lat/lon do pixel.

    A amostra é lida com as duas correções de 21/jul/2026 aplicadas em memória
    (filtro `cd_mun != 0` do envelope e relabel da classe 21), porque o CSV em
    disco é anterior a elas. Sem isso, `--fonte amostra` mediria os bugs.
    """
    if fonte == "censo":
        if not CENSO_IDADE.exists():
            sys.exit(f"Censo não encontrado: {CENSO_IDADE}\n"
                     f"Rode: python scripts/processa_cubo_idade.py --shards data/raw/cubo_go")
        df = pd.read_parquet(CENSO_IDADE).rename(
            columns={"n_pixels": "peso", "lat_media": "lat", "lon_media": "lon"})
        if "lat" not in df.columns:
            sys.exit("Censo sem lat_media/lon_media — reprocesse o cubo "
                     "(processa_cubo_idade.py foi atualizado para acumulá-los)")
        df["peso"] = df["peso"].astype("float64")
    elif fonte == "amostra":
        df = pd.read_csv(CSV_IDADE, dtype={"cd_mun": "int64"})
        df = df[df["cd_mun"] != 0].copy()
        df.loc[df["classe_antes_id"] == 21, "origem_anterior"] = "mosaico"
        df["peso"] = 1.0
    else:
        sys.exit(f"fonte desconhecida: {fonte!r} (use 'censo' ou 'amostra')")

    df["censurado"] = df["origem_anterior"] == "censurado_esquerda"
    cw = pd.read_csv(CSV_CROSSWALK, dtype={"cd_mun": "int64"})[["cd_mun", "code_amc"]]
    meso = pd.read_csv(CSV_MESO, dtype={"cd_mun": "int64"})[["cd_mun", "nm_meso"]]
    df = df.merge(cw, on="cd_mun", how="left").merge(meso, on="cd_mun", how="left")
    df = classificar_mecanismo(df)
    return df


# ── Agregação da mistura de mecanismos por unidade espacial ─────────────────
def agregar_mix(df: pd.DataFrame, chave: str, janela: tuple[int, int],
                min_px: int) -> pd.DataFrame:
    """Mistura de mecanismos + índice jovem↔antigo por unidade espacial,
    sobre os pixels NÃO-CENSURADOS na janela."""
    a, b = janela
    sub = df[(df["ano_conversao"] >= a) & (df["ano_conversao"] <= b) & (~df["censurado"])]
    linhas = []
    for uni, g in sub.groupby(chave):
        w = g["peso"].to_numpy(float)
        n = float(w.sum())
        if n <= 0:
            continue
        idade = g["idade_pastagem_anos"].to_numpy(float)
        # Toda proporção é massa-de-peso / massa-total. Com peso=1 (amostra)
        # reduz exatamente ao `.mean()` de antes — é o contrato do D24 que
        # permite comparar as duas fontes sem trocar de implementação.
        quota = lambda m: float(w[(g["mecanismo"] == m).to_numpy()].sum() / n)  # noqa: E731
        pct_jovem = float(w[idade <= JOVEM_MAX].sum() / n)
        pct_antigo = float(w[idade >= ANTIGO_MIN].sum() / n)
        mec = {
            "Rotação": quota("Rotação"),
            "Premeditado curto": quota("Premeditado curto"),
            "Oportunístico clássico": quota("Oportunístico clássico"),
        }
        dominante = max(mec, key=mec.get)
        # "misto" quando o líder não destaca (ambíguo é a pluralidade real).
        # REGRA INALTERADA na migração para o censo, de propósito: o mosaico
        # entra no DENOMINADOR (era censurado antes, logo invisível), mas não
        # no teste de dominância. Mudar dado e regra juntos tornaria o diff
        # ininterpretável. Revisar a regra é decisão separada.
        if mec[dominante] < 0.30 or quota("Ambíguo / Outro") > mec[dominante]:
            dominante = "Misto"
        linhas.append({
            chave: uni,
            "n_nc": n,
            "n_celulas": int(len(g)),  # censo: células agregadas; amostra: pixels
            "lat_centroide": float(np.average(g["lat"], weights=w)),  # − = Sul
            "lon_centroide": float(np.average(g["lon"], weights=w)),
            "idade_mediana": _mediana_p(idade, w),
            "idade_media": _media_p(idade, w),
            "pct_jovem": pct_jovem,
            "pct_antigo": pct_antigo,
            "indice_jovem": pct_jovem - pct_antigo,  # ∈ [-1,1]; + = lógica jovem
            "pct_rotacao": mec["Rotação"],
            "pct_premeditado": mec["Premeditado curto"],
            "pct_oportunistico": mec["Oportunístico clássico"],
            "pct_mosaico": quota("Mosaico de usos"),
            "pct_ambiguo": quota("Ambíguo / Outro"),
            "pct_origem_vegnat": float(
                w[(g["origem_anterior"] == "vegetacao_natural").to_numpy()].sum() / n),
            "pct_origem_agric": float(
                w[(g["origem_anterior"] == "agricultura").to_numpy()].sum() / n),
            "mecanismo_dominante": dominante,
        })
    out = pd.DataFrame(linhas)
    out["confiavel"] = out["n_nc"] >= min_px
    return out


# ── No-till (Censo 2017) por município e AMC ────────────────────────────────
def carregar_plantio_direto() -> pd.DataFrame:
    p = pd.read_parquet(PARQUET_PAINEL)
    c = p[p["ano"] == 2017].copy()
    cols = ["cd_mun", "censo2017_area_plantio_direto_ha", "censo2017_n_estab_plantio_direto",
            "censo2017_n_estabelecimentos", "censo2017_area_estabelecimentos_ha",
            "censo2017_lotacao_bov_ha", "censo2017_pct_familiar",
            "censo2017_valor_producao_soja_mil_rs", "censo2017_pct_agrotoxicos",
            "censo2017_pct_adubacao"]
    cols = [x for x in cols if x in c.columns]
    c = c[cols].copy()
    c["cd_mun"] = c["cd_mun"].astype("int64")
    area_est = c["censo2017_area_estabelecimentos_ha"].replace(0, np.nan)
    n_est = c["censo2017_n_estabelecimentos"].replace(0, np.nan)
    c["pct_pd_area"] = 100 * c["censo2017_area_plantio_direto_ha"] / area_est
    c["pct_pd_estab"] = 100 * c["censo2017_n_estab_plantio_direto"] / n_est
    c["soja_por_estab"] = c["censo2017_valor_producao_soja_mil_rs"] / n_est
    return c


# ── Tipologia "carreira da terra" (regra) ───────────────────────────────────
def tipologia_carreira(row) -> str:
    """Combina mecanismo dominante + origem para nomear a 'carreira da terra'."""
    if not row["confiavel"]:
        return "n/d (amostra rala)"
    dom = row["mecanismo_dominante"]
    if dom == "Rotação":
        return "Giro de lavoura (ILP/rotação)"
    if dom == "Premeditado curto":
        return "Trampolim de fronteira"
    if dom == "Oportunístico clássico":
        return "Reserva ativada (oportunístico)"
    return "Misto / transição"


# ─────────────────────────────── FIGURAS ────────────────────────────────────
def _carregar_geo_amc():
    g = gpd.read_file(GPKG_AMC)  # EPSG:4674
    g5880 = g.to_crs(5880)
    cent = g5880.geometry.centroid
    cent_geo = gpd.GeoSeries(cent, crs=5880).to_crs(4674)
    g = g.copy()
    g["cx"] = cent_geo.x.values
    g["cy"] = cent_geo.y.values  # latitude aprox (graus)
    g["north_km"] = cent.y.values / 1000.0  # northing 5880 (km), p/ ordenar S→N
    return g


def fig_mapas_amc(amc_mix: pd.DataFrame) -> None:
    g = _carregar_geo_amc().merge(amc_mix, on="code_amc", how="left")
    conf = g["confiavel"] == True  # noqa: E712

    fig, axes = plt.subplots(1, 2, figsize=(15, 8))

    # (a) Índice jovem↔antigo contínuo — paleta partilhada com (b):
    #     laranja = jovem/rotação (≤8a) · verde = antigo/reserva (≥20a)
    ax = axes[0]
    g.plot(ax=ax, color="#f0f0ec", edgecolor="white", linewidth=0.4)
    cmap_jovem = LinearSegmentedColormap.from_list(
        "jovem_antigo", ["#1b6e3d", "#f0f0ec", "#d95f02"])  # −1 verde → +1 laranja
    norm = TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
    g[conf].plot(ax=ax, column="indice_jovem", cmap=cmap_jovem, norm=norm,
                 edgecolor="white", linewidth=0.4, legend=True,
                 legend_kwds={"label": "Índice jovem↔antigo  (+ jovem / − antigo)",
                              "shrink": 0.6})
    ax.set_title(f"(a) Lógica dominante por idade — AMC ({JANELA_PRIMARIA[0]}–{JANELA_PRIMARIA[1]})\n"
                 "laranja = giro/trampolim (≤8a) · verde = reserva ativada (≥20a)",
                 fontsize=11)
    ax.axis("off")

    # (b) Mecanismo dominante (categórico)
    ax = axes[1]
    g.plot(ax=ax, color="#f0f0ec", edgecolor="white", linewidth=0.4)
    cor_dom = {"Rotação": "#d95f02", "Premeditado curto": "#e7c019",
               "Oportunístico clássico": "#1b6e3d", "Misto": "#9e9e9e"}
    handles = []
    for dom, cor in cor_dom.items():
        sel = g[conf & (g["mecanismo_dominante"] == dom)]
        if not sel.empty:
            sel.plot(ax=ax, color=cor, edgecolor="white", linewidth=0.4)
            handles.append(mpatches.Patch(facecolor=cor, edgecolor="white",
                                          label=f"{dom} (n={len(sel)})"))
    ax.legend(handles=handles, loc="lower left", fontsize=9, title="Mecanismo líder")
    ax.set_title(f"(b) Mecanismo de conversão dominante — AMC ({JANELA_PRIMARIA[0]}–{JANELA_PRIMARIA[1]})",
                 fontsize=11)
    ax.axis("off")

    fig.suptitle("As duas lógicas da pastagem, espacializadas — onde cada mecanismo domina",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "mapa_logica_dominante_amc.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_pixels_mecanismo(df: pd.DataFrame, fonte: str = "censo") -> None:
    """Conversões não-censuradas por mecanismo, no espaço.

    Com `fonte="amostra"` cada ponto é um pixel e a figura tem textura fina.
    Com `fonte="censo"` cada ponto é uma CÉLULA `(ano, muni, idade, classe)`
    posicionada no centroide exato dos seus pixels, com área ∝ nº de pixels.
    A tabela de contingência não guarda a coordenada individual, então a textura
    intramunicipal se perde — é o preço do censo, e está dito no título em vez
    de ser disfarçado com pontos que fingem ser pixels.
    """
    g = _carregar_geo_amc()
    contorno = g.dissolve().boundary
    a, b = JANELA_PRIMARIA
    sub = df[(df["ano_conversao"] >= a) & (df["ano_conversao"] <= b) & (~df["censurado"])]
    sub = sub[sub["mecanismo"] != "Ambíguo / Outro"]

    fig, ax = plt.subplots(figsize=(9, 9))
    contorno.plot(ax=ax, color="#999", linewidth=0.6)
    ordem = ["Oportunístico clássico", "Premeditado curto", "Rotação"]
    for mec in ordem:
        s = sub[sub["mecanismo"] == mec]
        if fonte == "censo":
            # área ∝ peso, normalizada para o maior ponto ficar legível
            tam = 2.0 + 60.0 * (s["peso"] / max(sub["peso"].max(), 1.0)) ** 0.5
            rot = f"{mec} (n={s['peso'].sum():,.0f} px)"
        else:
            tam, rot = 5, f"{mec} (n={len(s):,})"
        ax.scatter(s["lon"], s["lat"], s=tam, alpha=0.45, color=COR_MEC[mec],
                   label=rot, edgecolors="none")
    ax.legend(loc="lower left", fontsize=9, markerscale=2.5, framealpha=0.9)
    sub_t = ("cada ponto = célula do censo (área ∝ nº de pixels)" if fonte == "censo"
             else "cada ponto = pixel amostrado não-censurado")
    ax.set_title(f"Conversão pasto→agricultura por mecanismo ({a}–{b})\n{sub_t}",
                 fontsize=11)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "pixels_mecanismo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_gradiente_latitude(amc_mix: pd.DataFrame, nt: pd.DataFrame,
                           cw: pd.DataFrame) -> None:
    """Índice jovem e no-till vs latitude da AMC."""
    g = _carregar_geo_amc().merge(amc_mix, on="code_amc", how="left")
    # no-till agregado a AMC (soma de áreas)
    p = pd.read_parquet(PARQUET_PAINEL)
    c = p[p["ano"] == 2017][["cd_mun", "censo2017_area_plantio_direto_ha",
                             "censo2017_area_estabelecimentos_ha"]].copy()
    c["cd_mun"] = c["cd_mun"].astype("int64")
    c = c.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
    pd_amc = c.groupby("code_amc").sum(numeric_only=True)
    pd_amc["pct_pd_area"] = (100 * pd_amc["censo2017_area_plantio_direto_ha"]
                             / pd_amc["censo2017_area_estabelecimentos_ha"].replace(0, np.nan))
    g = g.merge(pd_amc[["pct_pd_area"]], on="code_amc", how="left")
    conf = g["confiavel"] == True  # noqa: E712
    gg = g[conf].copy()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, col, lab, cor in [
        (axes[0], "indice_jovem", "Índice jovem↔antigo", "#d95f02"),
        (axes[1], "pct_pd_area", "Plantio direto (% área estab., 2017)", "#1b6e3d"),
    ]:
        m = gg.dropna(subset=[col, "cy"])
        ax.scatter(m["cy"], m[col], s=22, alpha=0.7, color=cor)
        if len(m) > 3:
            r, pval = pearsonr(m["cy"], m[col])
            z = np.polyfit(m["cy"], m[col], 1)
            xs = np.linspace(m["cy"].min(), m["cy"].max(), 50)
            ax.plot(xs, np.polyval(z, xs), color="black", linestyle="--", linewidth=1)
            ax.set_title(f"{lab}\nr = {r:+.2f} (p={pval:.3f}, n={len(m)})", fontsize=10)
        ax.set_xlabel("Latitude do centroide da AMC (graus; ← Sul · Norte →)")
        ax.set_ylabel(lab)
        # latitudes negativas: ordem ascendente já põe o Sul (−19) à esquerda
    fig.suptitle("Gradiente latitudinal — a lógica jovem e o plantio direto descem ao Sul",
                 fontsize=12, y=1.0)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "gradiente_latitude.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def cruzar_plantio_direto(mun_mix: pd.DataFrame, nt: pd.DataFrame) -> pd.DataFrame:
    """Correlações município: mistura de mecanismos × estrutura Censo 2017."""
    m = mun_mix[mun_mix["confiavel"]].merge(nt, on="cd_mun", how="left")
    desfechos = ["idade_mediana", "pct_jovem", "indice_jovem", "pct_rotacao",
                 "pct_oportunistico", "pct_origem_agric"]
    estruturais = {
        "pct_pd_area": "Plantio direto (% área)",
        "pct_pd_estab": "Plantio direto (% estab.)",
        "censo2017_lotacao_bov_ha": "Lotação bovina (cab/ha)",
        "censo2017_pct_familiar": "% agric. familiar",
        "soja_por_estab": "Valor soja / estab.",
        "censo2017_pct_agrotoxicos": "% estab. c/ agrotóxico",
    }
    linhas = []
    for ev, ev_lab in estruturais.items():
        for dz in desfechos:
            sub = m.dropna(subset=[ev, dz])
            if len(sub) < 15:
                continue
            r, p = pearsonr(sub[ev], sub[dz])
            rho, prho = spearmanr(sub[ev], sub[dz])
            linhas.append({
                "estrutural": ev, "estrutural_label": ev_lab, "desfecho": dz,
                "n": len(sub), "pearson_r": r, "pearson_p": p,
                "spearman_rho": rho, "spearman_p": prho,
            })
    return pd.DataFrame(linhas)


def _partial_corr(x: str, y: str, z: str, d: pd.DataFrame):
    """Correlação parcial de x,y controlando z (Pearson) + p-valor."""
    from scipy.stats import t as tdist
    d = d.dropna(subset=[x, y, z])
    n = len(d)
    if n < 5:
        return np.nan, np.nan, n
    rxy = pearsonr(d[x], d[y])[0]
    rxz = pearsonr(d[x], d[z])[0]
    ryz = pearsonr(d[y], d[z])[0]
    denom = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if denom == 0 or n <= 3:
        return np.nan, np.nan, n
    rp = (rxy - rxz * ryz) / denom
    tval = rp * np.sqrt((n - 3) / max(1 - rp ** 2, 1e-12))
    p = 2 * tdist.sf(abs(tval), n - 3)
    return float(rp), float(p), n


def _partial_corr_multi(x: str, y: str, ctrls: list[str], d: pd.DataFrame):
    """Parcial de x,y controlando MÚLTIPLOS regressores (via resíduos OLS)."""
    from scipy.stats import t as tdist
    d = d.dropna(subset=[x, y] + ctrls)
    n = len(d)
    if n < len(ctrls) + 3:
        return np.nan, np.nan, n
    C = np.column_stack([np.ones(n)] + [d[c].values for c in ctrls])
    rx = d[x].values - C @ np.linalg.lstsq(C, d[x].values, rcond=None)[0]
    ry = d[y].values - C @ np.linalg.lstsq(C, d[y].values, rcond=None)[0]
    r = pearsonr(rx, ry)[0]
    dfree = n - len(ctrls) - 2
    tval = r * np.sqrt(dfree / max(1 - r ** 2, 1e-12))
    p = 2 * tdist.sf(abs(tval), dfree)
    return float(r), float(p), n


def robustez_confounder_fluxo(mun_mix: pd.DataFrame, nt: pd.DataFrame):
    """VERIFICAÇÃO crítica (correção do overclaim):
    (1) PARCIAL controlando latitude (e lat+lon, gradiente 2D Sudoeste→Nordeste)
        — o cruzamento no-till×idade é informação própria ou só o gradiente?
    (2) Comparação JUSTA com FLUXO. O nulo do #28 (Δ SICOR/Δ VA agro ~0) era em
        painel (município,ano); o cruzamento daqui é transversal. Posto o fluxo
        no MESMO recorte transversal municipal, ele ainda é nulo?
    """
    m = mun_mix[mun_mix["confiavel"]].merge(nt, on="cd_mun", how="left")
    lat = "lat_centroide"

    parc = []
    for dz in ["idade_mediana", "indice_jovem", "pct_oportunistico", "pct_rotacao"]:
        sub = m.dropna(subset=["pct_pd_area", dz])
        rb = pearsonr(sub["pct_pd_area"], sub[dz])[0]
        rp, pp, n = _partial_corr("pct_pd_area", dz, lat, m)
        rpll, ppll, _ = _partial_corr_multi("pct_pd_area", dz,
                                            ["lat_centroide", "lon_centroide"], m)
        parc.append({"bloco": "parcial_latitude", "estrutural": "pct_pd_area",
                     "desfecho": dz, "r_bruto": round(rb, 4),
                     "r_parcial_lat": round(rp, 4) if rp == rp else np.nan,
                     "p_parcial": round(pp, 4) if pp == pp else np.nan,
                     "r_parcial_latlon": round(rpll, 4) if rpll == rpll else np.nan,
                     "p_parcial_latlon": round(ppll, 4) if ppll == ppll else np.nan,
                     "n": n})

    a, b = JANELA_PRIMARIA
    p_full = pd.read_parquet(PARQUET_PAINEL).sort_values(["cd_mun", "ano"])
    flux = []
    for col in ["sicor_total_real_rs", "va_agro_real_rs"]:
        if col not in p_full.columns:
            continue
        sub = p_full[(p_full["ano"] >= a) & (p_full["ano"] <= b)].copy()
        sub["d"] = sub.groupby("cd_mun")[col].diff()
        agg = (sub.groupby("cd_mun").agg(nivel=(col, "mean"), dmed=("d", "mean"))
               .reset_index())
        agg["cd_mun"] = agg["cd_mun"].astype("int64")
        mm = m.merge(agg, on="cd_mun", how="left")
        for var, lab in [("nivel", "nível médio"), ("dmed", "Δ médio")]:
            s = mm.dropna(subset=[var, "idade_mediana"])
            if len(s) < 15:
                continue
            r, p = pearsonr(s[var], s["idade_mediana"])
            rp, pp, n = _partial_corr(var, "idade_mediana", lat, s)
            # Controle 2D TAMBÉM para o fluxo. Até 21/jul/2026 o bloco de
            # estrutura levava lat+lon e o de fluxo só lat — e a conclusão
            # ("estrutura > fluxo não se sustenta; o fluxo tem sinal próprio")
            # saía da comparação entre os dois. Controles diferentes nos dois
            # lados favorecem o lado menos controlado por construção.
            rpll, ppll, _ = _partial_corr_multi(var, "idade_mediana",
                                                ["lat_centroide", "lon_centroide"], s)
            flux.append({"bloco": "fluxo_mesmo_recorte",
                         "estrutural": f"{col} ({lab})", "desfecho": "idade_mediana",
                         "r_bruto": round(r, 4), "p_bruto": round(p, 4),
                         "r_parcial_lat": round(rp, 4) if rp == rp else np.nan,
                         "p_parcial": round(pp, 4) if pp == pp else np.nan,
                         "r_parcial_latlon": round(rpll, 4) if rpll == rpll else np.nan,
                         "p_parcial_latlon": round(ppll, 4) if ppll == ppll else np.nan,
                         "n": len(s)})
    return pd.DataFrame(parc), pd.DataFrame(flux)


def fig_cruzamento(mun_mix: pd.DataFrame, nt: pd.DataFrame) -> None:
    m = mun_mix[mun_mix["confiavel"]].merge(nt, on="cd_mun", how="left")
    pares = [
        ("pct_pd_area", "idade_mediana", "Plantio direto (% área estab.)",
         "Idade mediana da pastagem convertida (a)"),
        ("pct_pd_area", "pct_rotacao", "Plantio direto (% área estab.)",
         "% conversões por rotação (agric≤8a)"),
        ("pct_pd_area", "pct_oportunistico", "Plantio direto (% área estab.)",
         "% conversões oportunísticas (veg.nat≥20a)"),
        ("pct_pd_area", "indice_jovem", "Plantio direto (% área estab.)",
         "Índice jovem↔antigo"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    for ax, (ev, dz, xl, yl) in zip(axes.flat, pares):
        sub = m.dropna(subset=[ev, dz])
        ax.scatter(sub[ev], sub[dz], s=26, alpha=0.6, color="#2d5a3d",
                   edgecolors="white", linewidth=0.4)
        if len(sub) > 3:
            r, p = pearsonr(sub[ev], sub[dz])
            rho, prho = spearmanr(sub[ev], sub[dz])
            rp, pp, _ = _partial_corr(ev, dz, "lat_centroide", m)
            z = np.polyfit(sub[ev], sub[dz], 1)
            xs = np.linspace(sub[ev].min(), sub[ev].max(), 50)
            ax.plot(xs, np.polyval(z, xs), color="#a3387f", linestyle="--", linewidth=1.5)
            ax.set_title(f"bruto r={r:+.2f} (p={p:.3f}) · ρ={rho:+.2f}   |   "
                         f"PARCIAL|lat r={rp:+.2f} (p={pp:.3f})   ·   n={len(sub)}",
                         fontsize=9.5)
        ax.set_xlabel(xl); ax.set_ylabel(yl)
    fig.suptitle("Cruzamento com PLANTIO DIRETO (Censo 2017) — co-localização no gradiente Sul→Norte\n"
                 "r bruto vs. r PARCIAL controlando latitude: quase tudo é o gradiente comum (aptidão+capital)",
                 fontsize=12, y=1.0)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "cruzamento_plantio_direto.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_tipologia(mun_mix: pd.DataFrame, nt: pd.DataFrame, cw: pd.DataFrame) -> None:
    """Mapa municipal da tipologia 'carreira da terra' (dissolve AMC→muni p/ contexto)."""
    # geometria municipal não está no projeto; mapeamos a tipologia ao AMC do muni
    # via maioria ponderada por n_nc dentro de cada AMC (aproximação cartográfica).
    g = _carregar_geo_amc()
    mm = mun_mix[mun_mix["confiavel"]].merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
    mm["tipo"] = mm.apply(tipologia_carreira, axis=1)
    # tipo dominante por AMC (peso n_nc)
    dom = (mm.groupby(["code_amc", "tipo"])["n_nc"].sum()
             .reset_index()
             .sort_values("n_nc", ascending=False)
             .drop_duplicates("code_amc"))
    g = g.merge(dom[["code_amc", "tipo"]], on="code_amc", how="left")

    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    g.plot(ax=ax, color="#f0f0ec", edgecolor="white", linewidth=0.4)
    handles = []
    for tipo, cor in COR_TIPO.items():
        sel = g[g["tipo"] == tipo]
        if not sel.empty:
            sel.plot(ax=ax, color=cor, edgecolor="white", linewidth=0.4)
            handles.append(mpatches.Patch(facecolor=cor, edgecolor="white",
                                          label=f"{tipo} ({len(sel)} AMC)"))
    ax.legend(handles=handles, loc="lower left", fontsize=9,
              title="Carreira da terra dominante")
    ax.set_title("Tipologia 'carreira da terra' — mecanismo líder por AMC\n"
                 f"(municípios confiáveis, {JANELA_PRIMARIA[0]}–{JANELA_PRIMARIA[1]}; "
                 "AMC pintada pelo tipo de maior peso)", fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(DIR_OUT / "tipologia_carreira_terra.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def kmeans_robustez(mun_mix: pd.DataFrame, nt: pd.DataFrame) -> pd.DataFrame:
    """k-means (k=4) sobre features padronizadas — robustez à tipologia de regra."""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return pd.DataFrame()
    feats = ["pct_rotacao", "pct_oportunistico", "pct_premeditado", "idade_mediana"]
    m = mun_mix[mun_mix["confiavel"]].merge(nt[["cd_mun", "pct_pd_area"]], on="cd_mun", how="left")
    m = m.dropna(subset=feats + ["pct_pd_area"]).copy()
    if len(m) < 8:
        return pd.DataFrame()
    X = StandardScaler().fit_transform(m[feats + ["pct_pd_area"]])
    km = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X)
    m["cluster"] = km.labels_
    perfil = m.groupby("cluster")[feats + ["pct_pd_area", "n_nc"]].mean().round(3)
    perfil["n_munis"] = m.groupby("cluster").size()
    return perfil.reset_index()


# ─────────────────────────────── MAIN ───────────────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser(description="Pipeline #40 — as duas lógicas da pastagem")
    p.add_argument("--fonte", choices=["censo", "amostra"], default="censo",
                   help="censo de pixels (padrão) ou amostra legada do #28A")
    args = p.parse_args()
    # A amostra escreve com sufixo para não sobrescrever os CSVs canônicos —
    # assim as duas fontes coexistem e a comparação fica possível.
    suf = "" if args.fonte == "censo" else "_amostra"

    print(f"Fonte: {args.fonte} | lendo + crosswalks...")
    df = carregar(args.fonte)
    cw = pd.read_csv(CSV_CROSSWALK, dtype={"cd_mun": "int64"})
    nt = carregar_plantio_direto()
    print(f"  {len(df):,} linhas | {df['peso'].sum():,.0f} pixels | "
          f"{df['cd_mun'].nunique()} munis | "
          f"no-till 2017 em {nt['pct_pd_area'].notna().sum()} munis")

    # ── A. Agregação ─────────────────────────────────────────────────────────
    print(f"\nAgregando mistura de mecanismos — janela {JANELA_PRIMARIA}...")
    amc_mix = agregar_mix(df, "code_amc", JANELA_PRIMARIA, MIN_PX_AMC)
    mun_mix = agregar_mix(df, "cd_mun", JANELA_PRIMARIA, MIN_PX_MUN)
    mun_mix["tipo_carreira"] = mun_mix.apply(tipologia_carreira, axis=1)
    print(f"  AMC: {amc_mix['confiavel'].sum()}/{len(amc_mix)} confiáveis (≥{MIN_PX_AMC}px)")
    print(f"  Municípios: {mun_mix['confiavel'].sum()}/{len(mun_mix)} confiáveis (≥{MIN_PX_MUN}px)")

    amc_mix.to_csv(DIR_PROC / f"duas_logicas_amc{suf}.csv", index=False, float_format="%.4f")
    mun_mix_out = mun_mix.merge(nt, on="cd_mun", how="left")
    mun_mix_out.to_csv(DIR_PROC / f"duas_logicas_municipal{suf}.csv", index=False, float_format="%.4f")

    # ── B. Mapas ─────────────────────────────────────────────────────────────
    print("\nGerando mapas espaciais...")
    fig_mapas_amc(amc_mix)
    fig_pixels_mecanismo(df, args.fonte)
    fig_gradiente_latitude(amc_mix, nt, cw)

    # ── C. Cruzamento com plantio direto ─────────────────────────────────────
    print("\nCruzando com plantio direto (Censo 2017)...")
    cruz = cruzar_plantio_direto(mun_mix, nt)
    # robustez do par central (no-till × idade) em 3 janelas
    rob = []
    for jan in JANELAS_ROBUSTEZ:
        mm = agregar_mix(df, "cd_mun", jan, MIN_PX_MUN)
        mm = mm[mm["confiavel"]].merge(nt, on="cd_mun", how="left").dropna(
            subset=["pct_pd_area", "idade_mediana"])
        if len(mm) >= 15:
            r, p = pearsonr(mm["pct_pd_area"], mm["idade_mediana"])
            rr, pr = pearsonr(mm["pct_pd_area"], mm["pct_rotacao"])
            rob.append({"janela": f"{jan[0]}-{jan[1]}", "n": len(mm),
                        "r_notill_idade": r, "p_notill_idade": p,
                        "r_notill_rotacao": rr, "p_notill_rotacao": pr})
    cruz.attrs["robustez"] = rob
    cruz.to_csv(DIR_PROC / f"duas_logicas_cruzamento{suf}.csv", index=False, float_format="%.4f")
    fig_cruzamento(mun_mix, nt)

    # ── C2. VERIFICAÇÃO crítica: confundidor latitude + fluxo no mesmo recorte ──
    print("\nVerificando confundidor (latitude) e comparação justa com fluxo...")
    parc, flux = robustez_confounder_fluxo(mun_mix, nt)
    rob_full = pd.concat([parc, flux], ignore_index=True)
    rob_full.to_csv(DIR_PROC / f"duas_logicas_robustez{suf}.csv", index=False)

    # ── D. Tipologia ─────────────────────────────────────────────────────────
    print("\nMontando tipologia 'carreira da terra'...")
    fig_tipologia(mun_mix, nt, cw)
    perfil_km = kmeans_robustez(mun_mix, nt)

    # ── Relatório ────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RESUMO — As duas lógicas da pastagem")
    print("=" * 70)
    conf_mun = mun_mix[mun_mix["confiavel"]]
    print(f"\nTipologia municipal (n={len(conf_mun)} munis confiáveis, {JANELA_PRIMARIA}):")
    for tipo, n in conf_mun["tipo_carreira"].value_counts().items():
        sub = conf_mun[conf_mun["tipo_carreira"] == tipo]
        print(f"  {tipo:38s} {n:3d} munis | idade med {sub['idade_mediana'].median():.0f}a | "
              f"no-till {conf_mun.merge(nt,on='cd_mun').loc[lambda d: d['tipo_carreira']==tipo,'pct_pd_area'].median():.1f}%")

    print("\nCruzamento com plantio direto — pares com |r|>0.2 e p<0.05:")
    sig = cruz[(cruz["pearson_p"] < 0.05) & (cruz["pearson_r"].abs() > 0.2)]
    if sig.empty:
        print("  (nenhum)")
    for _, r in sig.sort_values("pearson_r").iterrows():
        print(f"  {r['estrutural_label']:26s} × {r['desfecho']:18s}  "
              f"r={r['pearson_r']:+.2f} (p={r['pearson_p']:.3f}) ρ={r['spearman_rho']:+.2f}  n={r['n']:.0f}")

    print("\nRobustez no-till × idade mediana (3 janelas):")
    for rr in rob:
        print(f"  {rr['janela']}: r_idade={rr['r_notill_idade']:+.2f} (p={rr['p_notill_idade']:.3f}) | "
              f"r_rotacao={rr['r_notill_rotacao']:+.2f} (p={rr['p_notill_rotacao']:.3f}) | n={rr['n']}")

    if not perfil_km.empty:
        print("\nk-means (k=4) — perfil dos clusters (robustez à regra):")
        print(perfil_km.to_string(index=False))

    print("\n" + "-" * 70)
    print("VERIFICAÇÃO — o cruzamento é informação própria ou só o gradiente?")
    print("-" * 70)
    print("(1) no-till × desfecho, BRUTO vs PARCIAL controlando o gradiente:")
    for _, r in parc.iterrows():
        flag = "" if (r["p_parcial_latlon"] == r["p_parcial_latlon"] and r["p_parcial_latlon"] < 0.05) else "  ← some no 2D"
        print(f"    × {r['desfecho']:18s} bruto {r['r_bruto']:+.2f} → |lat "
              f"{r['r_parcial_lat']:+.2f} (p={r['p_parcial']:.3f}) → |lat+lon "
              f"{r['r_parcial_latlon']:+.2f} (p={r['p_parcial_latlon']:.3f}){flag}")
    print("(2) FLUXO no MESMO recorte transversal e sob o MESMO controle 2D (× idade mediana):")
    for _, r in flux.iterrows():
        f2 = "" if (r["p_parcial_latlon"] == r["p_parcial_latlon"]
                    and r["p_parcial_latlon"] < 0.05) else "  ← some no 2D"
        print(f"    {r['estrutural']:32s} bruto {r['r_bruto']:+.2f} → |lat "
              f"{r['r_parcial_lat']:+.2f} (p={r['p_parcial']:.3f}) → |lat+lon "
              f"{r['r_parcial_latlon']:+.2f} (p={r['p_parcial_latlon']:.3f}) "
              f"n={r['n']}{f2}")
    # O veredito é DERIVADO do que rodou, não escrito à mão. Até 21/jul/2026
    # estas linhas eram texto fixo ("NENHUM par sobrevive", com os números da
    # amostra embutidos) — uma conclusão que a própria execução não podia
    # desmentir. Com o censo os números mudaram e o texto fixo passou a
    # contradizer a tabela impressa logo acima.
    p2 = parc["p_parcial_latlon"]
    n_sobrevive = int((p2 < 0.05).sum())
    n_limiar = int(((p2 >= 0.05) & (p2 < 0.10)).sum())
    idade = parc[parc["desfecho"] == "idade_mediana"]
    tr = idade.iloc[0] if len(idade) else parc.iloc[0]
    print("\nLEITURA (derivada dos números acima):")
    print(f"  n = {int(tr['n']) if 'n' in tr else '?'} municípios | pares testados: {len(parc)}")
    print(f"  × {tr['desfecho']}: bruto {tr['r_bruto']:+.2f} → |lat+lon "
          f"{tr['r_parcial_latlon']:+.2f} (p={tr['p_parcial_latlon']:.3f})")
    if n_sobrevive == 0 and n_limiar == 0:
        print("  Controlando lat+lon, NENHUM par sobrevive nem chega perto do limiar:")
        print("  o no-till co-localiza com a lógica jovem por gradiente espacial")
        print("  compartilhado, sem efeito próprio detectável.")
    elif n_sobrevive == 0:
        print(f"  NENHUM par cruza p<0,05, mas {n_limiar} fica(m) na FAIXA LIMÍTROFE "
              f"(0,05 ≤ p < 0,10).")
        print("  Isso NÃO é o mesmo que um nulo limpo: a associação encolhe muito sob o")
        print("  controle 2D mas não desaparece. Com multiplicidade (vários pares) o")
        print("  veredito segue 'não estabelecido' — porém por falta de evidência")
        print("  conclusiva, não por ausência de sinal. Não escrever 'não há efeito'.")
    else:
        print(f"  {n_sobrevive} par(es) sobrevive(m) a p<0,05 sob controle 2D "
              f"(+{n_limiar} no limiar).")
        print("  Reavaliar a D14: a leitura de 'sem efeito próprio' não se sustenta")
        print("  neste recorte. Corrigir por multiplicidade antes de afirmar efeito.")
    # O fluxo agora passa pelo MESMO controle 2D, então a comparação
    # "estrutura × fluxo" é simétrica e o veredito pode ser derivado.
    pf = flux["p_parcial_latlon"]
    f_sobrev = int((pf < 0.05).sum())
    if f_sobrev:
        quais = ", ".join(flux.loc[pf < 0.05, "estrutural"].tolist())
        print(f"  FLUXO sob o MESMO controle 2D: {f_sobrev} de {len(flux)} sobrevive(m) "
              f"({quais}).")
        print("  A comparação estrutura × fluxo agora é simétrica: o fluxo tem sinal")
        print("  próprio que a estrutura não tem neste recorte transversal.")
    else:
        print(f"  FLUXO sob o MESMO controle 2D: 0 de {len(flux)} sobrevive(m).")
        print("  Sob controle simétrico, NENHUM dos dois lados isola efeito próprio —")
        print("  a assimetria anterior ('fluxo tem sinal, estrutura não') vinha de o")
        print("  fluxo levar só controle 1D. Não repetir aquela leitura.")
    print("  Achado estável nas duas fontes: a SEGREGAÇÃO ESPACIAL das duas lógicas")
    print("  ao longo do gradiente de aptidão.")

    print(f"\n5 PNGs em {DIR_OUT.relative_to(ROOT)} | 4 CSVs em data/processed/")


if __name__ == "__main__":
    main()
