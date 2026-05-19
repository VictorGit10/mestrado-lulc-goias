"""visualizar_transicoes.py — Análise e visualizações das matrizes de transição
MapBiomas para Goiás (1985–2024).

Gera:
    1. Heatmaps 6×6 por período
    2. Diagrama de Sankey 1985→2024
    3. Mapas coropléticos: transição dominante, estabilidade, pastagem→agricultura
    4. CSV comparativo com Pipeline #5 (proxy vs pixel-a-pixel)

Como rodar:
    python "Scripts e Catalogo/visualizar_transicoes.py"

Pré-requisitos:
    pip install pandas geopandas geobr matplotlib matplotlib-scalebar plotly kaleido
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import geobr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cartografia import adicionar_norte, adicionar_escala  # noqa: E402

# ===== Configuração =====
CLASSES = {
    1: {"nome": "Vegetação Natural", "ids": [3, 4, 12],                          "cor": "#1B8A2F"},
    2: {"nome": "Pastagem",          "ids": [15],                                 "cor": "#FFD700"},
    3: {"nome": "Agricultura",       "ids": [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62], "cor": "#FF69B4"},
    4: {"nome": "Água",              "ids": [31, 33],                              "cor": "#4169E1"},
    5: {"nome": "Área Urbana",       "ids": [24],                                  "cor": "#A0A0A0"},
    6: {"nome": "Outros",            "ids": [5, 6, 11, 23, 25, 27, 29, 30, 32, 49, 50, 75],  "cor": "#D2B48C"},
}
NOME_CLASSE = {k: v["nome"] for k, v in CLASSES.items()}
COR_CLASSE = {k: v["cor"] for k, v in CLASSES.items()}
ORDEM = list(CLASSES.keys())

PERIODOS_NIVEL1 = [(1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024)]
PERIODOS_LONGOS = [(1985, 2000), (2000, 2010), (2010, 2024), (1985, 2010), (1985, 2024)]
TODOS_PERIODOS = PERIODOS_NIVEL1 + PERIODOS_LONGOS

DPI = 200
ROOT = Path(__file__).resolve().parent.parent
CSV_TRANS = ROOT / "data" / "processed" / "transicoes_mapbiomas_goias.csv"
OUT_DIR = ROOT / "outputs" / "transicoes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(CSV_TRANS, dtype={"cd_mun": "int64"})
    print(f"Dados: {len(df):,} linhas, {df['cd_mun'].nunique()} municípios, "
          f"{df.groupby(['ano_origem','ano_destino']).ngroups} pares de período")
    return df


def carregar_malha() -> "gpd.GeoDataFrame":
    gdf = geobr.read_municipality(code_muni="GO", year=2020)
    gdf["cd_mun"] = gdf["code_muni"].astype("int64")
    gdf = gdf.rename(columns={"name_muni": "nm_mun"})
    return gdf


# ──────────────────────────────────────────────────────────────
# 1. Heatmaps 6×6 por período
# ──────────────────────────────────────────────────────────────
def heatmap_matriz(df: pd.DataFrame, ano_orig: int, ano_dest: int) -> None:
    """Heatmap 6×6 da matriz de transição (em % da linha)."""
    mask = (df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest)
    sub = df[mask]

    # Matriz de áreas
    mat = np.zeros((6, 6))
    for _, row in sub.iterrows():
        i = int(row["classe_orig"]) - 1
        j = int(row["classe_dest"]) - 1
        mat[i, j] = row["area_ha"]

    # Converter para % da linha (destino como % da origem)
    row_sums = mat.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    mat_pct = mat / row_sums * 100

    fig, ax = plt.subplots(figsize=(8, 7))
    nomes = [NOME_CLASSE[i + 1] for i in range(6)]

    # Plotar com anotações
    im = ax.imshow(mat_pct, cmap="YlOrRd", vmin=0, vmax=100)

    for i in range(6):
        for j in range(6):
            val = mat_pct[i, j]
            area = mat[i, j]
            if val >= 1:
                texto = f"{val:.0f}%"
                if area >= 1e6:
                    texto += f"\n{area/1e6:.1f}M"
                elif area >= 1e3:
                    texto += f"\n{area/1e3:.0f}k"
                else:
                    texto += f"\n{area:.0f}"
                cor = "white" if val > 50 else "black"
                ax.text(j, i, texto, ha="center", va="center", fontsize=7,
                        color=cor, fontweight="bold" if i == j else "normal")

    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(nomes, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(nomes, fontsize=9)
    ax.set_xlabel(f"Classe em {ano_dest}")
    ax.set_ylabel(f"Classe em {ano_orig}")
    ax.set_title(f"Matriz de Transição — Goiás {ano_orig}→{ano_dest}", fontsize=13)

    # Diagonal mais escura
    for i in range(6):
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False,
                                     edgecolor="black", linewidth=2))

    plt.colorbar(im, ax=ax, label="% da classe de origem", shrink=0.8)
    plt.tight_layout()

    path = OUT_DIR / f"matriz_transicao_{ano_orig}_{ano_dest}.png"
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {path.name}")


# ──────────────────────────────────────────────────────────────
# 2. Sankey 1985→2024
# ──────────────────────────────────────────────────────────────
def sankey_1985_2024(df: pd.DataFrame) -> None:
    """Diagrama de Sankey para o período 1985→2024."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("  [Sankey] plotly não instalado. Instale: pip install plotly")
        return

    mask = (df["ano_origem"] == 1985) & (df["ano_destino"] == 2024)
    sub = df[mask]

    nomes_1985 = [f"{NOME_CLASSE[i]} (1985)" for i in ORDEM]
    nomes_2024 = [f"{NOME_CLASSE[i]} (2024)" for i in ORDEM]
    labels = nomes_1985 + nomes_2024

    sources, targets, values, colors = [], [], [], []
    for _, row in sub.iterrows():
        src = int(row["classe_orig"]) - 1
        tgt = int(row["classe_dest"]) - 1 + 6
        sources.append(src)
        targets.append(tgt)
        values.append(row["area_ha"])
        colors.append(COR_CLASSE[int(row["classe_orig"])])

    # Converter cores hex para rgba com transparência
    def hex_to_rgba(hex_color, alpha=0.4):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            label=labels,
            color=[COR_CLASSE[i] for i in ORDEM] * 2,
        ),
        link=dict(source=sources, target=targets, value=values,
                   color=[hex_to_rgba(c) for c in colors]),
    ))

    fig.update_layout(
        title_text="Transições de Uso da Terra — Goiás 1985→2024",
        font_size=12, width=900, height=500,
    )

    path_png = OUT_DIR / "sankey_1985_2024.png"
    path_html = OUT_DIR / "sankey_1985_2024.html"
    try:
        fig.write_image(str(path_png), scale=2)
        print(f"  Salvo: {path_png.name}")
    except Exception:
        print("  [Sankey] kaleido não disponível para PNG. Salvando HTML.")
    fig.write_html(str(path_html))
    print(f"  Salvo: {path_html.name}")


# ──────────────────────────────────────────────────────────────
# 3. Mapa coroplético — transição dominante
# ──────────────────────────────────────────────────────────────
def mapa_transicao_dominante(df: pd.DataFrame, gdf: "gpd.GeoDataFrame",
                              ano_orig: int, ano_dest: int) -> None:
    """Mapa da transição com maior área por município."""
    mask = (df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest)
    sub = df[mask]

    # Excluir diagonal (estabilidade) para mostrar só mudanças
    mudancas = sub[sub["classe_orig"] != sub["classe_dest"]]

    # Transição dominante por município
    idx = mudancas.groupby("cd_mun")["area_ha"].idxmax()
    dom = mudancas.loc[idx, ["cd_mun", "nm_mun", "classe_orig", "classe_dest",
                             "classe_orig_nome", "classe_dest_nome", "area_ha"]]

    # Rótulo da transição
    dom["transicao"] = dom["classe_orig_nome"] + " → " + dom["classe_dest_nome"]

    # Cor: classe de destino
    dom["cor"] = dom["classe_dest"].map(COR_CLASSE)

    # Merge com malha
    gdf_plot = gdf.merge(dom[["cd_mun", "transicao", "area_ha", "cor", "classe_dest"]],
                          on="cd_mun", how="left")

    fig, ax = plt.subplots(figsize=(10, 8))
    gdf_plot = gdf_plot.to_crs(5880)  # área

    # Plotar usando as cores MapBiomas (COR_CLASSE) — bate com a legenda.
    # Municípios sem mudança detectada (NaN em cor) recebem cinza claro.
    cores_munis = gdf_plot["cor"].fillna("#e0e0e0").tolist()
    gdf_plot.plot(ax=ax, color=cores_munis,
                  edgecolor="0.5", linewidth=0.2)

    # Legenda manual com cores das classes
    destinos_unicos = sorted(gdf_plot["classe_dest"].dropna().unique())
    handles = [Patch(facecolor=COR_CLASSE[int(d)], edgecolor="black",
                     label=NOME_CLASSE[int(d)]) for d in destinos_unicos]
    if gdf_plot["cor"].isna().any():
        handles.append(Patch(facecolor="#e0e0e0", edgecolor="black",
                             label="Sem mudança detectada"))
    ax.legend(handles=handles, loc="lower right", fontsize=8,
              title=f"Classe destino dominante\n(maior mudança {ano_orig}→{ano_dest})",
              borderaxespad=-1.2)

    ax.set_title(f"Transição Dominante por Município — Goiás {ano_orig}→{ano_dest}", fontsize=13)
    ax.set_axis_off()
    adicionar_escala(ax, dx=1)
    adicionar_norte(ax)

    plt.savefig(OUT_DIR / f"mapa_transicao_dominante_{ano_orig}_{ano_dest}.png",
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: mapa_transicao_dominante_{ano_orig}_{ano_dest}.png")


# ──────────────────────────────────────────────────────────────
# 4. Mapa de estabilidade
# ──────────────────────────────────────────────────────────────
def mapa_estabilidade(df: pd.DataFrame, gdf: "gpd.GeoDataFrame",
                       ano_orig: int, ano_dest: int) -> None:
    """Fração da área que permaneceu na mesma classe (diagonal / total)."""
    mask = (df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest)
    sub = df[mask]

    # Total por município
    total = sub.groupby("cd_mun")["area_ha"].sum().rename("total_ha")

    # Diagonal (mesma classe origem = destino)
    diagonal = sub[sub["classe_orig"] == sub["classe_dest"]]
    estab = diagonal.groupby("cd_mun")["area_ha"].sum().rename("estavel_ha")

    ratio = (estab / total * 100).fillna(0).reset_index()
    ratio.columns = ["cd_mun", "pct_estavel"]

    gdf_plot = gdf.merge(ratio, on="cd_mun", how="left")

    fig, ax = plt.subplots(figsize=(10, 8))
    gdf_plot = gdf_plot.to_crs(5880)
    gdf_plot.plot(column="pct_estavel", cmap="RdYlGn", legend=True,
                  ax=ax, edgecolor="0.5", linewidth=0.2,
                  legend_kwds={"label": "% estável", "shrink": 0.7})

    ax.set_title(f"Estabilidade do Uso da Terra — Goiás {ano_orig}→{ano_dest}", fontsize=13)
    ax.set_axis_off()
    adicionar_escala(ax, dx=1)
    adicionar_norte(ax)
    plt.savefig(OUT_DIR / f"mapa_estabilidade_{ano_orig}_{ano_dest}.png",
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: mapa_estabilidade_{ano_orig}_{ano_dest}.png")


# ──────────────────────────────────────────────────────────────
# 5. Mapa pastagem → agricultura
# ──────────────────────────────────────────────────────────────────────────────
def mapa_pastagem_agricultura(df: pd.DataFrame, gdf: "gpd.GeoDataFrame",
                               ano_orig: int, ano_dest: int) -> None:
    """Mapa da conversão pastagem → agricultura por município."""
    mask = ((df["ano_origem"] == ano_orig) & (df["ano_destino"] == ano_dest) &
            (df["classe_orig"] == 2) & (df["classe_dest"] == 3))

    conv = df[mask].groupby("cd_mun")["area_ha"].sum().reset_index()
    conv.columns = ["cd_mun", "pasto_para_agri_ha"]

    gdf_plot = gdf.merge(conv, on="cd_mun", how="left")
    gdf_plot["pasto_para_agri_ha"] = gdf_plot["pasto_para_agri_ha"].fillna(0)

    fig, ax = plt.subplots(figsize=(10, 8))
    gdf_plot = gdf_plot.to_crs(5880)
    gdf_plot.plot(column="pasto_para_agri_ha", cmap="OrRd", legend=True,
                  ax=ax, edgecolor="0.5", linewidth=0.2,
                  legend_kwds={"label": "Pasto→Agri (ha)", "shrink": 0.7})

    ax.set_title(f"Conversão Pastagem → Agricultura — Goiás {ano_orig}→{ano_dest}", fontsize=13)
    ax.set_axis_off()
    adicionar_escala(ax, dx=1)
    adicionar_norte(ax)
    plt.savefig(OUT_DIR / f"mapa_pastagem_agricultura_{ano_orig}_{ano_dest}.png",
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: mapa_pastagem_agricultura_{ano_orig}_{ano_dest}.png")


# ──────────────────────────────────────────────────────────────
# 6. CSV comparativo com Pipeline #5
# ──────────────────────────────────────────────────────────────
def comparar_com_pipeline5(df: pd.DataFrame) -> None:
    """Compara métricas do Pipeline #5 (proxy) com matrizes reais."""
    csv_p5 = ROOT / "data" / "processed" / "painel_pastagem_soja_municipal.csv"
    if not csv_p5.exists():
        print("  [comparação] CSV Pipeline #5 não encontrado, pulando.")
        return

    p5 = pd.read_csv(csv_p5, dtype={"cd_mun": "int64"})
    print(f"  Pipeline #5: {len(p5)} linhas")

    # Do Pipeline #12: pastagem → agricultura (proxy para conversão)
    mask = (df["classe_orig"] == 2) & (df["classe_dest"] == 3)
    conv_real = df[mask].groupby(["cd_mun", "ano_origem", "ano_destino"])["area_ha"].sum().reset_index()
    conv_real.columns = ["cd_mun", "ano_origem", "ano_destino", "pasto_agri_ha_real"]

    # Salvar CSV comparativo
    comp = conv_real.merge(p5[["cd_mun", "taxa_conversao", "delta_pastagem_ha", "delta_soja_ha"]],
                            on="cd_mun", how="outer")

    path = ROOT / "data" / "processed" / "comparacao_transicao_vs_proxy.csv"
    comp.to_csv(path, index=False, float_format="%.4f")
    print(f"  Salvo: {path.name}")


# ──────────────────────────────────────────────────────────────
# 7. Evolução temporal — gráfico de linhas das transições principais
# ──────────────────────────────────────────────────────────────
def evolucao_transicoes(df: pd.DataFrame) -> None:
    """Gráfico de linhas mostrando as principais transições ao longo dos 4 períodos Nível 1."""
    transicoes_chave = [
        (1, 2, "Veg. Nat. → Pastagem"),
        (1, 3, "Veg. Nat. → Agricultura"),
        (2, 3, "Pastagem → Agricultura"),
        (2, 1, "Pastagem → Veg. Nat."),
        (3, 1, "Agricultura → Veg. Nat."),
        (3, 2, "Agricultura → Pastagem"),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    for orig, dest, label in transicoes_chave:
        mask = (df["classe_orig"] == orig) & (df["classe_dest"] == dest)
        sub = df[mask].groupby(["ano_origem", "ano_destino"])["area_ha"].sum().reset_index()

        # Criar rótulo de período
        sub["periodo"] = sub["ano_origem"].astype(str) + "→" + sub["ano_destino"].astype(str)

        # Ordenar pelos períodos Nível 1
        periodo_ordem = {f"{a}→{b}": i for i, (a, b) in enumerate(PERIODOS_NIVEL1)}
        sub["ordem"] = sub["periodo"].map(periodo_ordem)
        sub = sub.dropna(subset=["ordem"]).sort_values("ordem")

        cor = COR_CLASSE.get(orig, "#333333")
        estilo = "-" if orig != dest else "--"
        ax.plot(sub["periodo"], sub["area_ha"] / 1e6, marker="o",
                label=label, color=cor, linewidth=2, linestyle=estilo)

    ax.set_xlabel("Período")
    ax.set_ylabel("Área (milhões de ha)")
    ax.set_title("Evolução das Principais Transições — Goiás", fontsize=13)
    ax.legend(loc="upper right", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "evolucao_transicoes.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: evolucao_transicoes.png")


def main() -> None:
    print("Carregando dados de transição...")
    df = carregar_dados()

    print("\n[1/7] Heatmaps 6×6...")
    for ao, ad in PERIODOS_NIVEL1:
        heatmap_matriz(df, ao, ad)

    print("\n[2/7] Sankey 1985→2024...")
    sankey_1985_2024(df)

    print("\n[3/7] Carregando malha municipal...")
    gdf = carregar_malha()

    print("\n[4/7] Mapas de transição dominante...")
    for ao, ad in PERIODOS_NIVEL1:
        mapa_transicao_dominante(df, gdf, ao, ad)
    # Também para os longos mais importantes
    mapa_transicao_dominante(df, gdf, 1985, 2024)

    print("\n[5/7] Mapas de estabilidade...")
    for ao, ad in PERIODOS_NIVEL1:
        mapa_estabilidade(df, gdf, ao, ad)
    mapa_estabilidade(df, gdf, 1985, 2024)

    print("\n[6/7] Mapas pastagem → agricultura...")
    for ao, ad in PERIODOS_NIVEL1:
        mapa_pastagem_agricultura(df, gdf, ao, ad)
    mapa_pastagem_agricultura(df, gdf, 1985, 2024)

    print("\n[7/7] Comparação com Pipeline #5...")
    comparar_com_pipeline5(df)

    print("\n[Extra] Evolução temporal das transições...")
    evolucao_transicoes(df)

    print("\n[Extra] Convertendo PNGs de transição dominante para WebP publicados...")
    exportar_webps_transicoes()

    print(f"\nConcluído. Outputs em: {OUT_DIR}")


def exportar_webps_transicoes() -> None:
    """Converte os 5 PNGs de transição dominante para WebP em Visualizacao/img/."""
    from PIL import Image

    pares = [(1985, 1995), (1995, 2005), (2005, 2015), (2015, 2024), (1985, 2024)]
    dst_dir = ROOT / "Visualizacao" / "img" / "mapas_transicoes"
    dst_dir.mkdir(parents=True, exist_ok=True)

    for ao, ad in pares:
        src = OUT_DIR / f"mapa_transicao_dominante_{ao}_{ad}.png"
        dst = dst_dir / f"transicao_{ao}-{ad}.webp"
        if not src.exists():
            print(f"  AVISO: {src.name} não encontrado, pulando")
            continue
        with Image.open(src) as img:
            img.save(dst, format="WEBP", quality=85, method=6)
        size_in = src.stat().st_size
        size_out = dst.stat().st_size
        ratio = (1 - size_out / size_in) * 100
        print(f"  {dst.name}: {size_in/1024:.0f} KB → {size_out/1024:.0f} KB ({ratio:.0f}% menor)")


if __name__ == "__main__":
    main()