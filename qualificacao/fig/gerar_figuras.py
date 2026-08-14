"""Gera as figuras do texto de qualificação na geometria da página.

Cada função ``fig_*`` redesenha uma vista a partir do mesmo CSV/parquet que o
pipeline de origem gravou em ``data/processed`` ou ``outputs`` — nunca a
partir do PNG de tela. Assim o número da figura e o número do texto vêm da
mesma fonte, e a figura pode carregar as ressalvas que o pipeline já declarou
(regra D27: se a peça ressalvou uma série em algum lugar, todas as
representações dela carregam a ressalva).

Uso::

    python qualificacao/fig/gerar_figuras.py            # todas
    python qualificacao/fig/gerar_figuras.py fronteira  # só uma
"""

from __future__ import annotations

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from estilo import (
    CORES,
    CORES_CLASSES,
    DIR_OUT,
    DIR_PROC,
    LARGURA_TEXTO,
    configurar,
    escala,
    norte,
    pronta_para_cartografia,
    salvar,
)


# ==========================================================================
# Insumos derivados que este script cria por conta própria
# ==========================================================================
# `data/` é gitignored e tem buracos: quem clonar o repositório não recebe
# estes dois arquivos. Em vez de falhar com "arquivo não encontrado", o
# script os reconstrói na primeira execução.

def _garantir_geo() -> None:
    """Baixa e cacheia as malhas do IBGE usadas na Figura 1."""
    alvos = {
        "_geo_ufs_brasil.gpkg": lambda g: g.read_state(year=2020),
        "_geo_biomas.gpkg": lambda g: g.read_biomes(year=2019),
        "_geo_meso_goias_2017.gpkg": lambda g: g.read_meso_region(
            code_meso="GO", year=2017),
        "_geo_muni_goias.gpkg": lambda g: g.read_municipality(
            code_muni="GO", year=2020),
    }
    faltando = {n: f for n, f in alvos.items() if not (DIR_PROC / n).exists()}
    if not faltando:
        return

    import warnings

    warnings.filterwarnings("ignore")
    import geobr

    for nome, buscar in faltando.items():
        print(f"    [cache] baixando {nome} do IBGE via geobr...")
        buscar(geobr).to_file(DIR_PROC / nome, driver="GPKG")


def _garantir_banda() -> None:
    """Recalcula a faixa de IC da latitude ano a ano, se ela não existir.

    O `#32` calcula esta faixa em memória e nunca a grava; sem ela a Figura 4
    perde a incerteza. O recálculo é o mesmo bootstrap (B=2000, semente 42) e
    reproduz os ΔNorte já publicados.
    """
    destino = DIR_PROC / "centro_massa_banda_lat.csv"
    if destino.exists():
        return

    print("    [cache] recalculando a faixa de bootstrap da latitude...")
    sys.path.insert(0, str(DIR_PROC.parent.parent / "scripts"))
    import centro_massa as cm

    painel, _ = cm.carregar_dados()
    banda, _ = cm.bootstrap_incerteza(
        painel,
        {k: v[0] for k, v in cm.VARIAVEIS.items()},
        {k: v[1] for k, v in cm.VARIAVEIS.items()},
    )
    banda.to_csv(destino, index=False, encoding="utf-8")


# ==========================================================================
# Cap. 4 — Perna 4: o teto de oferta
# ==========================================================================
def fig_fronteira_oferta() -> None:
    """Decomposição do fluxo Ato II->III e o estoque remanescente por região.

    Fontes: ``fronteira_decomposicao.csv`` e ``fronteira_regional.csv`` (#39).

    Cuidado de rótulo: a segunda parcela **não é demanda**. Ela reúne tudo o
    que não é o tamanho do estoque (propensão a converter, atrito de acesso,
    proteção, troca de fonte de terra). Chamá-la de demanda foi o defeito que
    a auditoria de figuras registrou como caso 1 da D27.
    """
    dec = pd.read_csv(DIR_PROC / "fronteira_decomposicao.csv")
    reg = pd.read_csv(DIR_PROC / "fronteira_regional.csv")

    dec = dec[dec.regiao != "Goiás (total)"].set_index("regiao")
    ordem = ["Sul", "Centro", "Norte"]
    dec = dec.loc[ordem]

    traj = reg[reg.agrupamento == "mesorregiao"]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(LARGURA_TEXTO, 2.9), gridspec_kw={"width_ratios": [1, 1.15]}
    )

    # ---- (a) decomposição -------------------------------------------------
    x = np.arange(len(ordem))
    larg = 0.34
    ax1.bar(
        x - larg / 2,
        dec.efeito_estoque * 1000,
        larg,
        color=CORES["veg_natural"],
        label="parcela de estoque",
    )
    ax1.bar(
        x + larg / 2,
        dec.efeito_hazard * 1000,
        larg,
        color="#9e9e9e",
        label="parcela residual",
    )
    ax1.plot(
        x,
        dec.d_fluxo * 1000,
        "D",
        color="black",
        markersize=4,
        linestyle="none",
        label="Δ observado",
    )
    ax1.axhline(0, color="black", lw=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(ordem)
    ax1.set_ylabel("contribuição à Δ do fluxo\n(mil ha/ano), Ato II → III")
    ax1.legend(loc="lower right", handlelength=1.4, borderpad=0.2, labelspacing=0.3)
    ax1.grid(axis="x", visible=False)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    # a advertência que a figura precisa carregar sozinha (D27): o canto
    # superior esquerdo fica vazio porque as barras do Sul são negativas
    ax1.annotate(
        "a parcela residual\nnão é demanda medida",
        xy=(0.02, 0.97),
        xycoords="axes fraction",
        ha="left",
        va="top",
        fontsize=7,
        style="italic",
        color=CORES["neutro"],
    )

    # ---- (b) estoque remanescente ----------------------------------------
    for grupo in ordem:
        s = traj[traj.grupo == grupo].sort_values("ano")
        ax2.plot(
            s.ano,
            s.pct_restante * 100,
            color=CORES[grupo],
            lw=1.3,
            label=grupo,
        )
    ax2.axhline(60, color=CORES["neutro"], lw=0.6, ls=":")
    ax2.annotate(
        "60%",
        xy=(2023.5, 60.6),
        fontsize=7,
        ha="right",
        va="bottom",
        color=CORES["neutro"],
    )
    ax2.set_xlim(1985, 2024)
    ax2.set_ylim(50, 101)
    ax2.set_ylabel("estoque convertível remanescente\n(% do estoque de 1985)")
    ax2.set_xlabel("ano")
    ax2.legend(loc="lower left", handlelength=1.4, borderpad=0.2, labelspacing=0.3)
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    salvar(fig, "cap4_fronteira_oferta")


# ==========================================================================
# Cap. 4 — Perna 3: as doze especificações do teste espacial
# ==========================================================================
def fig_teste_espacial() -> None:
    """As doze estimativas de θ, com IC95%, e a zona que a hipótese exigiria.

    Fonte: ``deslocamento_bracket_slx.csv`` (#49) — termo de vizinhança,
    excluídos os modelos de placebo (vizinhos ao norte).

    A hipótese do empurrão exige θ > 0. A figura mostra que as doze caem do
    lado oposto: o resultado é a **ausência de um sinal exigido**, não um
    p-valor rejeitando tese — por isso a zona exigida é desenhada, e não
    apenas os intervalos.
    """
    d = pd.read_csv(DIR_PROC / "deslocamento_bracket_slx.csv")
    v = d[(d.termo == "vizinhanca") & (~d.modelo.str.contains("placebo"))].copy()

    # o Times não tem o glifo de união; a mathtext (STIX) tem
    v["regua_rot"] = v.regua_rotulo.str.replace("∪", r"$\cup$", regex=False)
    v["desfecho"] = np.where(v.desfecho_imune, "pasto imune", "pasto MapBiomas")
    v["rotulo"] = v.regua_rot + "  ·  " + v.desfecho

    janelas = [("plena", "janela plena, 1985–2024"),
               ("truncada 1985–2019", "janela truncada, 1985–2019")]

    fig, axes = plt.subplots(
        1, 2, figsize=(LARGURA_TEXTO, 2.7), sharey=True, sharex=True
    )

    for ax, (janela, titulo) in zip(axes, janelas):
        s = v[v.janela == janela].sort_values(["regua_rotulo", "desfecho_imune"])
        s = s.reset_index(drop=True)
        y = np.arange(len(s))[::-1]

        # a zona que a hipótese do empurrão exigiria — desenhada porque o
        # resultado é a ausência de um sinal exigido, não um p-valor
        ax.axvspan(0, 0.4, color=CORES["veg_natural"], alpha=0.10, zorder=0)

        ax.hlines(y, s.beta - 1.96 * s.se, s.beta + 1.96 * s.se,
                  color=CORES["agricultura"], lw=1.1)
        ax.plot(s.beta, y, "o", color=CORES["agricultura"], markersize=3.4)

        ax.axvline(0, color="black", lw=0.7)
        ax.set_yticks(y)
        ax.set_yticklabels(s.rotulo, fontsize=7)
        ax.set_xlim(-0.36, 0.36)
        ax.set_xticks([-0.3, -0.15, 0, 0.15, 0.3])
        ax.set_title(titulo, fontsize=8, pad=4)
        ax.grid(axis="y", visible=False)

    axes[0].annotate(
        "θ > 0:\nzona exigida\npela hipótese",
        xy=(0.03, 0.06),
        xycoords="axes fraction",
        fontsize=6.5,
        style="italic",
        color=CORES["veg_natural"],
        va="bottom",
    )

    fig.supxlabel(
        "θ — efeito da lavoura dos vizinhos ao sul sobre o pasto local (IC 95%)",
        fontsize=9,
        y=0.01,
    )
    fig.tight_layout()
    salvar(fig, "cap4_teste_espacial")


# ==========================================================================
# Cap. 4 — Perna 1: a marcha ao norte
# ==========================================================================
# A partir deste ano a lavoura recém-convertida começa a receber o rótulo
# "Mosaico de Usos" e sai do centroide de "Agricultura" (D25/D26). O
# interativo da visualização corta a série aqui (ANO_ROTULO_DERIVA); a
# figura impressa precisa carregar a mesma ressalva — é o caso 2 da D27.
ANO_ROTULO_DERIVA = 2019


def fig_centro_massa() -> None:
    """Centro de massa em movimento (1985→2024) e a latitude ano a ano.

    Fontes: ``centro_massa_anual.csv`` e ``centro_massa_banda_lat.csv``
    (bootstrap de AMCs, B=2000, semente 42 — reproduz o IC da Tabela dos
    deslocamentos), sobre a malha de ``amc_goias.gpkg`` (#32).

    O mapa mostra o estado inteiro de propósito: a marcha líquida é de ~80 km
    num estado de ~700 km, e um zoom na nuvem de trajetórias faria um sinal
    pequeno-porém-robusto parecer maior do que é.
    """
    import geopandas as gpd

    _garantir_banda()
    cen = pd.read_csv(DIR_PROC / "centro_massa_anual.csv")
    banda = pd.read_csv(DIR_PROC / "centro_massa_banda_lat.csv")
    amc = gpd.read_file(DIR_PROC / "amc_goias.gpkg")
    # ver a nota sobre simplificação em fig_localizacao: a 6 cm de largura,
    # 0,008° (~800 m) fica bem abaixo da espessura do traço
    amc["geometry"] = amc.geometry.simplify(0.008, preserve_topology=True)
    # métrico, como na Figura 1 — e o próprio #32 já grava os centroides em
    # EPSG:5880 nas colunas x_mean/y_mean, então o mapa usa a medida original
    # em vez de reconverter para graus
    amc = amc.to_crs(5880)

    camadas = [
        ("pastagem", "Pastagem", CORES["pastagem"]),
        ("bovinos", "Rebanho bovino", CORES["bovinos"]),
        ("agricultura", "Agricultura", CORES["agricultura"]),
        ("veg_natural", "Vegetação natural", CORES["veg_natural"]),
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(LARGURA_TEXTO, 3.3), gridspec_kw={"width_ratios": [1, 1.35]}
    )

    # ---- (a) o mapa -------------------------------------------------------
    amc.boundary.plot(ax=ax1, color="#e8e8e8", linewidth=0.2)
    amc.dissolve().boundary.plot(ax=ax1, color="#666666", linewidth=0.6)

    for chave, rotulo, cor in camadas:
        g = cen[cen.variavel == chave].sort_values("ano")
        ini, fim = g.iloc[0], g.iloc[-1]
        ax1.annotate(
            "",
            xy=(fim.x_mean, fim.y_mean),
            xytext=(ini.x_mean, ini.y_mean),
            arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.0,
                            mutation_scale=7, shrinkA=0, shrinkB=0),
        )
        ax1.plot(ini.x_mean, ini.y_mean, "o", mfc="white", mec=cor,
                 mew=0.9, markersize=3.6, zorder=4)
        ax1.plot(fim.x_mean, fim.y_mean, "o", color=cor,
                 markersize=3.6, zorder=4, label=rotulo)

    ax1.set_aspect("equal")
    ax1.set_axis_off()
    ax1.set_title("(a) posição em 1985 (○) e 2024 (●)", loc="left", fontsize=8)

    # ---- (b) a latitude ano a ano ----------------------------------------
    for ini, fim, nome in [(1985, 2000, "Ato I"), (2001, 2019, "Ato II"),
                           (2020, 2024, "Ato III")]:
        ax2.axvspan(ini - 0.5, fim + 0.5, color="#000000", alpha=0.035, zorder=0)
        ax2.annotate(nome, xy=((ini + fim) / 2, 0.985),
                     xycoords=("data", "axes fraction"),
                     ha="center", va="top", fontsize=6.5, color="#888888")

    for chave, rotulo, cor in camadas:
        g = cen[cen.variavel == chave].sort_values("ano")
        b = banda[banda.variavel == chave].sort_values("ano")
        ax2.fill_between(b.ano, b.lat_lo, b.lat_hi, color=cor, alpha=0.13,
                         lw=0, zorder=1)
        if chave == "agricultura":
            # ressalva D27: a partir de 2019 a série subconta a lavoura nova
            ate = g[g.ano <= ANO_ROTULO_DERIVA]
            dps = g[g.ano >= ANO_ROTULO_DERIVA]
            ax2.plot(ate.ano, ate.lat_mean, "-", color=cor, lw=1.3, zorder=3)
            ax2.plot(dps.ano, dps.lat_mean, ":", color=cor, lw=1.3, zorder=3)
        else:
            ax2.plot(g.ano, g.lat_mean, "-", color=cor, lw=1.3, zorder=3)

    ax2.axvline(ANO_ROTULO_DERIVA, color=CORES["neutro"], lw=0.5, ls="--")
    ax2.annotate(
        "a partir de 2019 a lavoura nova migra\npara o Mosaico e sai desta série\n"
        "(pontilhado; D25/D26)",
        xy=(2018.4, 0.45),
        xycoords=("data", "axes fraction"),
        ha="right",
        va="center",
        fontsize=6.5,
        style="italic",
        color=CORES["neutro"],
    )

    ax2.set_xlim(1985, 2024)
    ax2.set_xlabel("ano")
    ax2.set_ylabel("latitude do centro de massa (°)\nmais alto = mais ao norte")
    ax2.set_title("(b) faixa = IC 95% por bootstrap das AMCs", loc="left", fontsize=8)

    # legenda única para os dois painéis
    handles = [
        plt.Line2D([], [], color=cor, lw=1.6, marker="o", markersize=3.6,
                   label=rotulo)
        for _, rotulo, cor in camadas
    ]
    pronta_para_cartografia(fig, rect=(0, 0.07, 1, 1))
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8,
               handlelength=1.4, columnspacing=1.6, bbox_to_anchor=(0.5, 0.0))
    # escala e norte só depois do layout final — ver a nota em estilo.escala
    escala(ax1, dx=1, total_km=200, loc="lower left", borderpad=0.6)
    norte(ax1, size=0.40, loc="lower right", borderpad=0.3)
    salvar(fig, "cap4_centro_massa")


# ==========================================================================
# Cap. 4 — Perna 2: a idade da pastagem convertida
# ==========================================================================
def fig_idade_pastagem() -> None:
    """A forma da distribuição de idade e o que havia no pixel antes do pasto.

    Fonte: ``pastagem_idade_censo.parquet`` (#28C) — censo de pixels, ponderado
    por ``n_pixels``. Descarta os eventos de idade truncada pelo início da
    série (``censurado_esquerda``), que não têm idade conhecida.

    O painel (a) existe para mostrar que a segunda população **não** se lê por
    inspeção visual: não há dois picos, há um pico jovem e um ombro longo. O
    que a estabelece é o ajuste de uma componente não dar conta da forma.
    """
    import sys as _sys

    _sys.path.insert(0, str(DIR_PROC.parent.parent / "scripts"))
    from estatistica_ponderada import gmm_ponderado

    d = pd.read_parquet(DIR_PROC / "pastagem_idade_censo.parquet")
    nc = d[d.origem_anterior != "censurado_esquerda"]

    idade = nc.groupby("idade_pastagem_anos").n_pixels.sum().sort_index()
    x = idade.index.to_numpy(dtype=float)
    w = idade.to_numpy(dtype=float)
    dens = w / w.sum()

    r1 = gmm_ponderado(x, w, n_comp=1)
    r2 = gmm_ponderado(x, w, n_comp=2)

    grade = np.linspace(0.5, 40, 400)

    def _mistura(res):
        y = np.zeros_like(grade)
        for mu, sig, peso in zip(res["mu"], res["sigma"], res["peso"]):
            y += peso * np.exp(-0.5 * ((grade - mu) / sig) ** 2) / (
                sig * np.sqrt(2 * np.pi)
            )
        return y

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(LARGURA_TEXTO, 2.9))

    # ---- (a) a forma e os dois ajustes -----------------------------------
    # O histograma vem primeiro e em destaque: o que o censo mostra é uma
    # curva decrescente com um ombro, e não dois picos. As componentes
    # aparecem separadas justamente para não sugerir bimodalidade visual.
    mu1, mu2 = float(r2["mu"][0]), float(r2["mu"][1])
    sig1, sig2 = float(r2["sigma"][0]), float(r2["sigma"][1])
    w1, w2 = float(r2["peso"][0]), float(r2["peso"][1])

    def _comp(mu, sig, peso):
        return peso * np.exp(-0.5 * ((grade - mu) / sig) ** 2) / (
            sig * np.sqrt(2 * np.pi)
        )

    ax1.bar(x, dens, width=0.9, color="#dcdcdc", edgecolor="none",
            label="censo de pixels", zorder=1)
    ax1.fill_between(grade, 0, _comp(mu1, sig1, w1), color=CORES["pastagem"],
                     alpha=0.30, lw=0, zorder=2)
    ax1.fill_between(grade, 0, _comp(mu2, sig2, w2), color=CORES["veg_natural"],
                     alpha=0.25, lw=0, zorder=2)
    ax1.plot(grade, _mistura(r1), color=CORES["bovinos"], lw=1.2, ls="--",
             label="se fosse 1 população", zorder=3)
    ax1.plot(grade, _mistura(r2), color="black", lw=1.0,
             label="2 populações somadas", zorder=4)

    ax1.annotate(
        f"pasto jovem\nμ={mu1:.1f}a · σ={sig1:.1f}a\n{w1:.0%} da massa".replace(".", ","),
        xy=(7.0, 0.081), fontsize=6.3, color="#8a5a00", va="top",
    )
    ax1.annotate(
        f"pasto velho\nμ={mu2:.1f}a · σ={sig2:.1f}a\n{w2:.0%} da massa\n"
        f"({sig2 / sig1:.0f}× mais larga:\nvira ombro, não pico)".replace(".", ","),
        xy=(21.5, 0.052), fontsize=6.3, color="#1b5e20", va="top",
    )

    ax1.set_xlim(0, 40)
    ax1.set_ylim(0, 0.099)
    ax1.set_xlabel("idade da pastagem na conversão (anos)")
    ax1.set_ylabel("densidade dos eventos")
    ax1.legend(loc="upper right", handlelength=1.4, borderpad=0.2,
               labelspacing=0.3, fontsize=6.5)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    # ---- (b) o que havia antes do pasto ----------------------------------
    rotulos = {
        "vegetacao_natural": ("Vegetação natural", CORES["veg_natural"]),
        "mosaico": ("Mosaico de Usos", CORES["mosaico"]),
        "agricultura": ("Agricultura", CORES["agricultura"]),
    }
    comp = (
        nc.groupby(["idade_pastagem_anos", "origem_anterior"])
        .n_pixels.sum()
        .unstack(fill_value=0)
    )
    outras = [c for c in comp.columns if c not in rotulos]
    comp["outras"] = comp[outras].sum(axis=1)
    comp = comp.drop(columns=outras)
    share = comp.div(comp.sum(axis=1), axis=0) * 100

    ordem = ["agricultura", "mosaico", "outras", "vegetacao_natural"]
    cores = [rotulos.get(c, ("Outras origens", "#e0e0e0"))[1] for c in ordem]
    ax2.stackplot(share.index, *[share[c] for c in ordem],
                  colors=cores, edgecolor="none", alpha=0.9)

    # mediana da idade dentro de cada origem: é o número que o texto lidera,
    # e ele não depende de ajuste nenhum
    def _mediana(origem):
        g = nc[nc.origem_anterior == origem].groupby(
            "idade_pastagem_anos").n_pixels.sum().sort_index()
        return int(g.index[g.cumsum() >= g.sum() / 2][0])

    med_veg, med_mos = _mediana("vegetacao_natural"), _mediana("mosaico")
    med_lav = _mediana("agricultura")

    # rótulo direto sobre cada faixa: legenda separada não cabe sem cobrir dado
    ax2.annotate(f"antes era VEGETAÇÃO NATURAL\nmediana {med_veg}a",
                 xy=(20, 78), fontsize=6.3, color="white", ha="center",
                 va="center", fontweight="bold")
    ax2.annotate(f"antes era MOSAICO DE USOS\nmediana {med_mos}a",
                 xy=(20, 33), fontsize=6.3, color="white", ha="center",
                 va="center", fontweight="bold")
    ax2.annotate(f"antes era LAVOURA\n(rotação) · mediana {med_lav}a",
                 xy=(3.2, 13), fontsize=6.3, color="white", ha="left",
                 va="center", fontweight="bold")

    ax2.set_xlim(1, 37)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("idade da pastagem na conversão (anos)")
    ax2.set_ylabel("origem anterior do pixel (%)")
    ax2.set_title("(b)", loc="left", fontweight="bold")
    ax2.grid(visible=False)

    fig.tight_layout()
    salvar(fig, "cap4_idade_pastagem")

    print(f"    [confere] 1 comp: mu={r1['mu'][0]:.2f} sig={r1['sigma'][0]:.2f}")
    print(f"    [confere] 2 comp: mu1={mu1:.2f} sig1={sig1:.2f} w1={r2['peso'][0]:.3f} | "
          f"mu2={mu2:.2f} sig2={sig2:.2f} w2={r2['peso'][1]:.3f}")
    print(f"    [confere] n eventos={int(d.n_pixels.sum()):,} | "
          f"nao censurados={int(nc.n_pixels.sum()):,}")


# ==========================================================================
# Cap. 4 — o balanço de quarenta anos
# ==========================================================================
def fig_sankey() -> None:
    """Cruzamento pixel a pixel 1985 <-> 2024, sete classes.

    Fonte: ``transicoes_cubo_goias.csv`` (#12B) — a recontagem local sobre o
    cubo do censo, que traz o "Mosaico de Usos" como grupo próprio. O #12
    original tinha seis grupos e cobria 0,0% do Mosaico; usar aquela matriz
    aqui esconderia justamente o fluxo que o capítulo discute.
    """
    from matplotlib.path import Path as MplPath
    from matplotlib.patches import PathPatch

    d = pd.read_csv(DIR_PROC / "transicoes_cubo_goias.csv")
    d = d[(d.ano_origem == 1985) & (d.ano_destino == 2024)]
    m = (
        d.groupby(["classe_orig_nome", "classe_dest_nome"]).area_ha.sum().unstack(
            fill_value=0
        )
        / 1e6
    )

    ordem = ["Vegetação Natural", "Pastagem", "Agricultura", "Mosaico de Usos",
             "Outros", "Água", "Área Urbana"]
    m = m.reindex(index=ordem, columns=ordem, fill_value=0)

    # O agrupamento do cubo põe o campo alagado (classe 11) em "Outros", ao
    # passo que a tabela do balanço o conta como vegetação natural. Nomear a
    # classe localiza a diferença de 0,70 Mha na figura, em vez de deixá-la
    # como discrepância silenciosa entre duas páginas.
    rotulo_bloco = dict.fromkeys(ordem)
    rotulo_bloco.update({k: k for k in ordem})
    rotulo_bloco["Outros"] = "Outros\n(inclui campo alagado)"

    total = m.values.sum()
    vao = total * 0.012          # respiro entre blocos
    limiar = 0.05                # Mha: abaixo disso a fita vira sujeira

    def _posicoes(tots):
        # de baixo para cima, na ordem inversa, para que a leitura no papel
        # comece pela vegetação natural no topo
        alt = total - vao * (len(ordem) - 1)
        y, pos = 0.0, {}
        for nome in reversed(ordem):
            h = tots[nome] / total * alt
            pos[nome] = [y, y + h]
            y += h + vao
        return pos

    esq = _posicoes(m.sum(axis=1))
    dir_ = _posicoes(m.sum(axis=0))
    # as fitas empilham do topo de cada bloco para baixo, na ordem das classes:
    # é o que mantém os laços paralelos em vez de trançados
    alt_esq = {k: v[1] for k, v in esq.items()}
    alt_dir = {k: v[1] for k, v in dir_.items()}

    fig, ax = plt.subplots(figsize=(LARGURA_TEXTO, 3.9))
    x0, x1, larg = 0.0, 1.0, 0.035

    # os fluxos que o capítulo cita nominalmente ganham rótulo sobre a fita
    destaques = {
        ("Vegetação Natural", "Pastagem"),
        ("Pastagem", "Agricultura"),
        ("Vegetação Natural", "Agricultura"),
        ("Vegetação Natural", "Mosaico de Usos"),
    }
    rotulos_fita = []

    fitas = [
        (o, dd, m.loc[o, dd]) for o in ordem for dd in ordem if m.loc[o, dd] >= limiar
    ]
    for o, dd, v in fitas:
        h = v / total * (total - vao * (len(ordem) - 1))
        ya1, ya0 = alt_esq[o], alt_esq[o] - h
        yb1, yb0 = alt_dir[dd], alt_dir[dd] - h
        alt_esq[o] -= h
        alt_dir[dd] -= h

        xm = (x0 + x1) / 2
        verts = [
            (x0 + larg, ya0), (xm, ya0), (xm, yb0), (x1 - larg, yb0),
            (x1 - larg, yb1), (xm, yb1), (xm, ya1), (x0 + larg, ya1),
            (x0 + larg, ya0),
        ]
        codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
                 MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
                 MplPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MplPath(verts, codes),
                               facecolor=CORES_CLASSES[o],
                               alpha=0.32 if o != dd else 0.16,
                               edgecolor="none", zorder=1))
        if (o, dd) in destaques:
            rotulos_fita.append((xm, (ya0 + ya1 + yb0 + yb1) / 4, v))

    # blocos e rótulos
    tot_esq, tot_dir = m.sum(axis=1), m.sum(axis=0)
    for nome in ordem:
        for pos, xb, ha, dx, tots in [
            (esq, x0, "right", -0.015, tot_esq),
            (dir_, x1 - larg, "left", larg + 0.015, tot_dir),
        ]:
            y0, y1 = pos[nome]
            if y1 - y0 <= 0:
                continue
            ax.add_patch(plt.Rectangle((xb, y0), larg, y1 - y0,
                                       facecolor=CORES_CLASSES[nome],
                                       edgecolor="none", zorder=3))
            if (y1 - y0) / total > 0.018:
                ax.text(xb + dx, (y0 + y1) / 2,
                        f"{rotulo_bloco[nome]}\n{tots[nome]:.1f} Mha".replace(
                            ".", ","),
                        ha=ha, va="center", fontsize=6.3, zorder=4)

    for xm, ym, v in rotulos_fita:
        ax.text(xm, ym, f"{v:.2f} Mha".replace(".", ","), ha="center",
                va="center", fontsize=6.3, zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.75))

    ax.annotate("1985", xy=(x0 + larg / 2, total * 1.03), ha="center", fontsize=8,
                fontweight="bold")
    ax.annotate("2024", xy=(x1 - larg / 2, total * 1.03), ha="center", fontsize=8,
                fontweight="bold")

    ax.set_xlim(-0.30, 1.30)
    ax.set_ylim(-total * 0.05, total * 1.08)
    ax.set_axis_off()

    fig.tight_layout()
    salvar(fig, "cap4_sankey")

    for o, dd in [("Vegetação Natural", "Pastagem"), ("Pastagem", "Agricultura"),
                  ("Vegetação Natural", "Agricultura"),
                  ("Vegetação Natural", "Mosaico de Usos")]:
        print(f"    [confere] {o} -> {dd}: {m.loc[o, dd]:.3f} Mha")


# ==========================================================================
# Cap. 4 — os três atos vistos no mapa
# ==========================================================================
def fig_painel_cobertura() -> None:
    """Cobertura da terra em 1985, 1995, 2005, 2015 e 2024, legenda comum.

    Fonte: ``outputs/mapas_gee/_raw_7c/raw_YYYY.png`` (#10, Coleção 10.1) — os
    rasters sem moldura, com as sete classes já pintadas. Cada arquivo traz o
    seu próprio título, rosa dos ventos e legenda na versão decorada; aqui só
    o raster entra, e a legenda é única para os cinco painéis.

    O recorte branco a leste do centro é o Distrito Federal, que não pertence
    a Goiás e por isso não é classificado.
    """
    import geopandas as gpd
    from matplotlib.patches import Patch
    from PIL import Image

    anos = [1985, 1995, 2005, 2015, 2024]
    dir_raw = DIR_OUT / "mapas_gee" / "_raw_7c"

    # O GEE exporta o thumbnail sobre o *bounding box* de Goiás em EPSG:4326,
    # com o mesmo passo em graus nos dois eixos (a razão de pixels, 1,0333,
    # é igual à razão de graus, 1,0335). Isso é plate carrée cru: exibido a
    # 1:1, o estado sai esticado, porque 1° de latitude vale mais quilômetros
    # que 1° de longitude nesta faixa. Ancorando a imagem no *bounding box*
    # métrico (EPSG:5880) obtêm-se o aspecto e o metro-por-pixel corretos,
    # que é como o próprio `gerar_mapas_lulc_gee_40anos.py` calcula a escala.
    _garantir_geo()
    go = gpd.read_file(DIR_PROC / "_geo_ufs_brasil.gpkg")
    bb = go[go.abbrev_state == "GO"].to_crs(5880).total_bounds

    fig, axes = plt.subplots(2, 3, figsize=(LARGURA_TEXTO, 4.35))

    mpp_x = None
    for ax, ano in zip(axes.ravel(), anos):
        im = np.array(Image.open(dir_raw / f"raw_{ano}.png").convert("RGB"))
        # o fundo do raster é preto; no papel ele tem de ser o branco da página
        fundo = (im.sum(axis=2) == 0)
        rgba = np.dstack([im, np.where(fundo, 0, 255).astype(np.uint8)])
        alt, larg = im.shape[:2]
        mpp_x = (bb[2] - bb[0]) / larg
        mpp_y = (bb[3] - bb[1]) / alt
        ax.imshow(rgba, interpolation="antialiased", aspect=mpp_y / mpp_x)
        ax.set_axis_off()
        ax.set_title(str(ano), fontsize=9, pad=2)

    ax_ref = axes.ravel()[len(anos) - 1]

    # a sexta célula recebe a legenda comum
    ax_leg = axes.ravel()[-1]
    ax_leg.set_axis_off()
    ordem = ["Vegetação Natural", "Pastagem", "Agricultura", "Mosaico de Usos",
             "Água", "Área Urbana", "Outros"]
    ax_leg.legend(
        handles=[Patch(facecolor=CORES_CLASSES[c], label=c) for c in ordem],
        loc="center", fontsize=7.5, handlelength=1.1, handleheight=1.0,
        labelspacing=0.55, borderpad=0.6, title="Classe (7 grupos)",
        title_fontsize=8, frameon=False,
    )

    # Escala e orientação valem para os cinco recortes, que compartilham
    # projeção e enquadramento; repeti-las cinco vezes só somaria ruído.
    # Só depois do layout final — ver a nota em estilo.escala.
    pronta_para_cartografia(fig, h_pad=0.6, w_pad=0.2)
    escala(ax_ref, dx=mpp_x, total_km=200, loc="lower left", borderpad=0.0)
    norte(ax_ref, size=0.38, loc="lower right", borderpad=0.0)
    salvar(fig, "cap4_painel_cobertura", raster=True)


# ==========================================================================
# Cap. 3 — a área de estudo
# ==========================================================================
def fig_localizacao() -> None:
    """Goiás no Brasil e no Cerrado (a); mesorregiões e malha municipal (b).

    Fontes: malhas do IBGE via ``geobr`` — estados e municípios de 2020,
    mesorregiões de 2020, biomas de 2019 — em cache local
    (``data/processed/_geo_*.gpkg``).

    As mesorregiões são preenchidas segundo a **ordenação por latitude média
    dos pixels de conversão**, que é o eixo analítico do trabalho: é essa
    ordem, e não a nomenclatura, que organiza o Sul--Norte.
    """
    import geopandas as gpd
    from matplotlib.patches import Patch

    # As malhas do IBGE vêm com detalhe de escala cadastral. Impressas a 6-8 cm
    # de largura, um vértice a cada ~30 m não é visível e só engorda o PDF (10 MB
    # antes desta simplificação). As tolerâncias abaixo ficam bem abaixo de
    # 1 mm no papel: ~0,01° ≈ 1 km em Goiás, ~0,05° ≈ 5 km na escala do Brasil.
    _garantir_geo()

    def _simplificar(gdf, tol):
        gdf = gdf.copy()
        gdf["geometry"] = gdf.geometry.simplify(tol, preserve_topology=True)
        return gdf

    ufs = _simplificar(gpd.read_file(DIR_PROC / "_geo_ufs_brasil.gpkg"), 0.05)
    biomas = _simplificar(gpd.read_file(DIR_PROC / "_geo_biomas.gpkg"), 0.05)
    # malha de mesorregiões de 2017 — a mesma que a análise usa (decisão D6),
    # e não a de 2020, para que o mapa e o painel falem da mesma divisão
    meso = _simplificar(gpd.read_file(DIR_PROC / "_geo_meso_goias_2017.gpkg"), 0.008)
    mun = _simplificar(gpd.read_file(DIR_PROC / "_geo_muni_goias.gpkg"), 0.008)

    # Tudo em EPSG:5880 (SIRGAS 2000 / Policônica do Brasil), o CRS métrico que o
    # projeto já usa. Desenhar em graus exigiria corrigir o aspecto por
    # cos(latitude), o que só vale numa latitude de referência — aceitável em
    # Goiás (erro de ±1,7% entre 12°S e 19°S), mas ruim no painel do Brasil,
    # que atravessa 40° de latitude. Em CRS métrico a régua vale em toda parte
    # e `dx=1` na escala é exato.
    ufs, biomas = ufs.to_crs(5880), biomas.to_crs(5880)
    meso, mun = meso.to_crs(5880), mun.to_crs(5880)

    cerrado = biomas[biomas.name_biome == "Cerrado"]
    goias = ufs[ufs.abbrev_state == "GO"]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(LARGURA_TEXTO, 3.4), gridspec_kw={"width_ratios": [1, 1.2]}
    )

    # ---- (a) Goiás no Brasil e no Cerrado --------------------------------
    ufs.plot(ax=ax1, facecolor="#f5f5f5", edgecolor="white", linewidth=0.4)
    cerrado.plot(ax=ax1, facecolor=CORES["veg_natural"], alpha=0.22,
                 edgecolor=CORES["veg_natural"], linewidth=0.4)
    goias.plot(ax=ax1, facecolor=CORES["agricultura"], alpha=0.75,
               edgecolor="black", linewidth=0.5)
    ufs.dissolve().boundary.plot(ax=ax1, color="#777777", linewidth=0.4)

    # Recorta as ilhas oceânicas, que a esta escala são sujeira solta no mar e
    # esticam o enquadramento: em EPSG:5880 o extremo LESTE CONTINENTAL (Ponta
    # do Seixas, PB) está em x ≈ 7.121 km, enquanto Fernando de Noronha (PE)
    # vai a 7.396 e Trindade (ES) a 7.614.
    cont = ufs.total_bounds
    ax1.set_xlim(cont[0] - 8e4, 7.20e6)
    ax1.set_ylim(cont[1] - 8e4, cont[3] + 8e4)
    ax1.set_aspect("equal")
    ax1.set_axis_off()
    ax1.legend(
        handles=[
            Patch(facecolor=CORES["agricultura"], alpha=0.75, label="Goiás"),
            Patch(facecolor=CORES["veg_natural"], alpha=0.22, label="bioma Cerrado"),
        ],
        loc="lower left", fontsize=7, handlelength=1.1, borderpad=0.3,
        labelspacing=0.35,
    )
    ax1.set_title("(a) Goiás no Brasil e no bioma Cerrado", loc="left",
                  fontsize=8)

    # ---- (b) mesorregiões e malha municipal ------------------------------
    # ordenadas pela latitude média dos pixels de conversão (Tabela das
    # mesorregiões): é a ordem que define o eixo Sul-Norte da análise
    ordem_lat = ["Sul Goiano", "Centro Goiano", "Leste Goiano",
                 "Noroeste Goiano", "Norte Goiano"]
    rampa = plt.get_cmap("YlGnBu")
    cor_meso = {nome: rampa(0.20 + 0.62 * i / (len(ordem_lat) - 1))
                for i, nome in enumerate(ordem_lat)}

    for nome in ordem_lat:
        meso[meso.name_meso == nome].plot(
            ax=ax2, facecolor=cor_meso[nome], edgecolor="none")
    mun.boundary.plot(ax=ax2, color="white", linewidth=0.25)
    meso.boundary.plot(ax=ax2, color="#333333", linewidth=0.5)

    for nome in ordem_lat:
        g = meso[meso.name_meso == nome]
        p = g.representative_point().iloc[0]
        ax2.annotate(nome.replace(" Goiano", ""), xy=(p.x, p.y), ha="center",
                     va="center", fontsize=7, fontweight="bold", color="#222222",
                     bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                               edgecolor="none", alpha=0.7))

    ax2.set_aspect("equal")
    ax2.set_axis_off()
    ax2.set_title("(b) mesorregiões (IBGE) e os 246 municípios",
                  loc="left", fontsize=8)

    # escala e norte só depois do layout final — ver a nota em estilo.escala
    pronta_para_cartografia(fig)
    escala(ax1, dx=1, total_km=1000, loc="lower right", borderpad=0.0)
    norte(ax1, size=0.42, loc="upper right", borderpad=0.0)
    escala(ax2, dx=1, total_km=200, loc="lower left", borderpad=0.0)
    norte(ax2, size=0.42, loc="lower right", borderpad=0.0)
    salvar(fig, "cap3_localizacao")


# ==========================================================================
FIGURAS = {
    "centro": fig_centro_massa,
    "cobertura": fig_painel_cobertura,
    "localizacao": fig_localizacao,
    "espacial": fig_teste_espacial,
    "fronteira": fig_fronteira_oferta,
    "idade": fig_idade_pastagem,
    "sankey": fig_sankey,
}


def main() -> None:
    configurar()
    alvos = sys.argv[1:] or list(FIGURAS)
    for nome in alvos:
        if nome not in FIGURAS:
            print(f"figura desconhecida: {nome} (opções: {', '.join(FIGURAS)})")
            continue
        print(f"[{nome}]")
        FIGURAS[nome]()


if __name__ == "__main__":
    main()
