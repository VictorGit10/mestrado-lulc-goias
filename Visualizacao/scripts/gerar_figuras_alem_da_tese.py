"""
Gera as quatro figuras da secao "Para alem da tese" (reforma.html).

Sao achados laterais — reais, testados, e fora do fio condutor das quatro pernas:

  1. oscilacao_pasto_savana.png  — o fluxo reverso pasto->"natural" e' oscilacao
     de classificador na borda pasto<->savana, nao regeneracao. (#12B + doc
     Textos/metodologia/oscilacao_pasto_savana.md)
  2. malha_fundiaria_buckets.png — GO e' 90% privado / 4% protegido; o placebo
     de especificidade da Perna 4 e' fraco por construcao. (malha LAPIG, §10)
  3. amc_emancipacoes.png        — quedas de 50-80% de rebanho nas ondas de
     emancipacao sao perda de territorio, nao dinamica pecuaria. (#25 / D11)
  4. quebras_calendario.png      — as 15 quebras data-driven de GO e TO contra
     os marcos institucionais; o Codigo Florestal nao deixa quebra. (#26 + C2)

Uso:
  cd Visualizacao
  python scripts/gerar_figuras_alem_da_tese.py            # portugues (index.html)
  python scripts/gerar_figuras_alem_da_tese.py --lang en  # ingles (index.en.html)

Saida:
  Visualizacao/img/alem_da_tese/*.png      (pt)
  Visualizacao/img/alem_da_tese/*.en.png   (en)

Em ingles mudam so' os textos e o separador decimal; dados, geometria e cores
sao os mesmos, e a saida em portugues continua byte a byte igual.
"""

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "Visualizacao" / "img" / "alem_da_tese"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta da peca (assets/css/styles.css). As figuras precisam ler como parte da
# pagina, nao como anexo colado: mesmo fundo, mesma familia de cor.
BG = "#fcfcfa"          # fundo do card
FG = "#1a1a1a"
MUTED = "#6b6b6b"
RULE = "#d8d6cf"
ACCENT = "#8b3a1d"      # terracota Cerrado
ACCENT_SOFT = "#c97052"
VEG = "#2d5a3d"         # formacao florestal
SAVANA = "#7d9c55"      # savanica — o meio-termo que o classificador confunde
CAMPO = "#c9d59b"       # campestre
PASTO = "#d4b65a"
AGRIC = "#d96aa3"
AGUA = "#4a7ba6"
CINZA = "#8a8a82"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Inter", "DejaVu Sans"],
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "text.color": FG,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": RULE,
    "axes.linewidth": 0.8,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.labelsize": 9.5,
})


EN = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en"
SUFIXO = ".en.png" if EN else ".png"


def t(pt, en):
    """Texto da figura no idioma da rodada."""
    return en if EN else pt


def vg(x, casas=2):
    """Numero no formato do idioma (virgula decimal em pt-BR, ponto em ingles)."""
    s = f"{x:.{casas}f}"
    return s if EN else s.replace(".", ",")


def limpar(ax, esquerda=True, baixo=True):
    """Tira as bordas que nao carregam informacao."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(esquerda)
    ax.spines["bottom"].set_visible(baixo)


def titulo(ax, texto, sub=None):
    ax.set_title(texto, loc="left", fontsize=11.5, fontweight="600",
                 color=FG, pad=22 if sub else 8)
    if sub:
        ax.text(0, 1.028, sub, transform=ax.transAxes, fontsize=9,
                color=MUTED, va="bottom", ha="left")


def rodape(fig, texto):
    fig.text(0.008, 0.012, texto, fontsize=7.6, color=MUTED, ha="left", va="bottom")


# ======================================================================
# 1. Oscilacao pasto <-> savana
# ======================================================================
def fig_oscilacao():
    src = REPO_ROOT / "data" / "processed" / "checar_transicao_pasto_natural_classe.csv"
    d = pd.read_csv(src)

    def fluxo(o, dst, co, cd):
        m = d[(d.ano_origem == o) & (d.ano_destino == dst)
              & (d.classe_orig == co) & (d.classe_dest == cd)]
        return float(m.area_ha.iloc[0]) if len(m) else 0.0

    janelas = [  # (origem, destino, rotulo, e' janela decenal?)
        (1985, 1995, "1985–95", True),
        (1995, 2005, "1995–2005", True),
        (2005, 2015, "2005–15", True),
        (2015, 2024, "2015–24", True),
        (2023, 2024, t("2023–24\num ano", "2023–24\none year"), False),
        (1985, 2024, t("1985–2024\n40 anos", "1985–2024\n40 years"), False),
    ]

    linhas = []
    for o, dst, rot, dec in janelas:
        f = fluxo(o, dst, 15, 3)    # pasto -> floresta
        s = fluxo(o, dst, 15, 4)    # pasto -> savana
        c = fluxo(o, dst, 15, 12)   # pasto -> campo natural
        sp = fluxo(o, dst, 4, 15)   # savana -> pasto (o sentido dominante)
        linhas.append(dict(rot=rot, dec=dec, flor=f, sav=s, campo=c, tot=f + s + c,
                           sav_pasto=sp, pasto_sav=s, razao=sp / s if s else np.nan))
    L = pd.DataFrame(linhas)

    fig, (axA, axB) = plt.subplots(
        1, 2, figsize=(11.4, 5.1), gridspec_kw={"width_ratios": [1.38, 1]})
    fig.subplots_adjust(left=0.105, right=0.985, top=0.775, bottom=0.215, wspace=0.30)

    # ---- A: composicao do fluxo reverso -----------------------------------
    y = np.arange(len(L))[::-1]
    frac = L[["flor", "sav", "campo"]].div(L.tot, axis=0) * 100

    axA.barh(y, frac.flor, color=VEG, height=0.62, label=t("Floresta (3)", "Forest (3)"))
    axA.barh(y, frac.sav, left=frac.flor, color=SAVANA, height=0.62, label=t("Savana (4)", "Savanna (4)"))
    axA.barh(y, frac.campo, left=frac.flor + frac.sav, color=CAMPO, height=0.62,
             label=t("Campo natural (12)", "Natural grassland (12)"))

    for i, yy in enumerate(y):
        pf, ps = frac.flor.iloc[i], frac.sav.iloc[i]
        if ps > 12:
            axA.text(pf + ps / 2, yy, f"{ps:.0f}%", ha="center", va="center",
                     fontsize=9.2, color="white", fontweight="600")
        if pf > 12:
            axA.text(pf / 2, yy, f"{pf:.0f}%", ha="center", va="center",
                     fontsize=9.2, color="white", fontweight="600")

    # As duas ultimas linhas nao sao janelas decenais: separa para nao serem
    # lidas como continuacao da serie.
    axA.axhline(1.5, color=RULE, lw=0.9, ls=(0, (3, 3)), xmin=0.0, xmax=0.73)

    axA.set_yticks(y, L.rot, fontsize=8.8)
    axA.set_xlim(0, 138)
    axA.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
    limpar(axA, esquerda=False)
    axA.tick_params(axis="y", length=0)
    axA.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    axA.set_axisbelow(True)
    titulo(axA, t("Para onde vai o pasto que “volta a ser natural”",
                 "Where the pasture that “turns natural again” goes"),
           sub=t("composição do fluxo reverso pastagem → vegetação natural",
                 "composition of the reverse flow pasture → natural vegetation"))

    # A hipotese inicial era campo natural. Ela nao aparece — e a ausencia e' o
    # achado, entao precisa de seta: o leitor nao ve sozinho o que nao esta la.
    axA.annotate(t("campo natural:\n0% em todas\nas janelas\n— era a\nhipótese inicial",
                   "natural grassland:\n0% in every\nwindow\n— it was the\ninitial hypothesis"),
                 xy=(101.5, y[2]), xytext=(108, y[2] - 0.6),
                 fontsize=8.4, color=ACCENT, ha="left", va="center", linespacing=1.5,
                 arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.0,
                                 connectionstyle="arc3,rad=0.2"))

    axA.legend(loc="upper left", bbox_to_anchor=(0.0, -0.135), ncol=3,
               frameon=False, fontsize=8.6, handlelength=1.1, columnspacing=1.5)

    # ---- B: a razao que colapsa -------------------------------------------
    dec = L[L.dec].reset_index(drop=True)
    x = np.arange(len(dec))
    axB.plot(x, dec.razao, color=ACCENT, lw=2.0, marker="o", ms=7,
             mfc=BG, mew=2.0, zorder=4)
    for xi, r in zip(x, dec.razao):
        axB.annotate(vg(r, 1) + "×", (xi, r), textcoords="offset points",
                     xytext=(0, 12), ha="center", fontsize=9.2,
                     color=ACCENT, fontweight="600")

    anual = L[L.rot.str.startswith("2023")].iloc[0]
    xa = len(dec) + 0.4
    axB.plot([xa], [anual.razao], marker="D", ms=8, color=ACCENT_SOFT, zorder=5)
    axB.annotate(vg(anual.razao) + "×", (xa, anual.razao), textcoords="offset points",
                 xytext=(13, 1), ha="left", va="center", fontsize=9.2,
                 color=ACCENT_SOFT, fontweight="600")

    axB.axhline(1.0, color=MUTED, lw=1.0, ls=(0, (4, 3)))
    axB.text(-0.35, 1.22, t("mão dupla equilibrada", "balanced two-way flow"), fontsize=8.2, color=MUTED,
             ha="left", va="bottom")

    axB.set_xticks(list(x) + [xa], list(dec.rot) + [t("2023–24\num ano", "2023–24\none year")], fontsize=8.6)
    axB.set_xlim(-0.45, xa + 0.5)
    axB.set_ylim(0, 10.4)
    axB.set_ylabel(t("savana→pasto ÷ pasto→savana", "savanna→pasture ÷ pasture→savanna"))
    limpar(axB)
    axB.grid(axis="y", color=RULE, lw=0.6, alpha=0.7)
    axB.set_axisbelow(True)
    titulo(axB, t("O mesmo par vai e volta, cada vez mais parelho",
                 "Back and forth, ever more evenly"),
           sub=t("quanto o sentido dominante supera o reverso",
                 "how much the dominant direction exceeds the reverse"))

    nota_anual = (
        f"in one year: {anual.pasto_sav/1000:,.0f} thousand ha pasture→savanna\n"
        f"and {anual.sav_pasto/1000:,.0f} thousand ha savanna→pasture" if EN else
        f"num único ano: {anual.pasto_sav/1000:,.0f} mil ha de pasto→savana\n"
        f"e {anual.sav_pasto/1000:,.0f} mil ha de savana→pasto".replace(",", "."))
    axB.annotate(nota_anual,
                 xy=(xa - 0.06, anual.razao + 0.35), xytext=(xa + 0.12, 5.1),
                 fontsize=8.2, color=MUTED, ha="right", va="center", linespacing=1.5,
                 arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9,
                                 connectionstyle="arc3,rad=-0.25"))

    rodape(fig, t("MapBiomas col. 10.1, cubo de Goiás em classe bruta (sem colapsar 3/4/12), "
                  "área corrigida por cos(lat) · script checar_transicao_pasto_natural_classe.py",
                  "MapBiomas col. 10.1, Goiás cube in raw classes (3/4/12 not collapsed), "
                  "area corrected by cos(lat) · script checar_transicao_pasto_natural_classe.py"))

    out = OUT_DIR / f"oscilacao_pasto_savana{SUFIXO}"
    fig.savefig(out, dpi=190, facecolor=BG)
    plt.close(fig)
    print(f"[1] {out.name}")
    print("    razões: " + " · ".join(
        f"{r.rot.splitlines()[0]} {r.razao:.2f}" for r in L.itertuples()
        if not np.isnan(r.razao)))
    print(f"    campo natural, máximo em qualquer janela: "
          f"{(L.campo / L.tot * 100).max():.3f}%")


# ======================================================================
# 2. Malha fundiaria — 90% privado, 2% de placebo limpo
# ======================================================================
def fig_malha():
    src = REPO_ROOT / "outputs" / "diag_malha_fundiaria_por_classe.csv"
    d = pd.read_csv(src).set_index("cls_malha")["area_Mha"]

    # "Ativo Ambiental" (APP/RL) e' overlay sobre a tenure, nao classe de tenure:
    # somar tudo dupla-conta 7,30 Mha. O territorio efetivo e' 32,30 Mha.
    privado = d[["SIGEF/SNCI", "CAR sem sobreposição", "CAR com sobreposição"]].sum()
    assent = d["Assentamentos"]
    outros = d[["Massa dagua", "Malha Urbana", "Área Militar",
                "Gleba Pública", "Floresta Publica Não Destinada"]].sum()
    # Ordenado para deixar adjacentes, a' direita, as duas classes que de fato
    # vedam a conversao (UC de protecao integral e TI homologada).
    prot_itens = [
        (t("UC de uso sustentável", "Sustainable-use PA"), d["Unidade Conservação de Uso Sustentável"], CINZA),
        (t("Terra quilombola", "Quilombola land"), d["Terra Quilombola Declarado"]
         + d["Terra Quilombola Não Declarado"], SAVANA),
        (t("UC de proteção integral", "Strict-protection PA"), d["Unidade de Conservação de Proteção Integral"], VEG),
        (t("Terra indígena", "Indigenous land"), d["Terra Indigena Homologada"]
         + d["Terra Indigena Não Homologada"], ACCENT),
    ]
    protegido = sum(v for _, v, _ in prot_itens)
    veda = prot_itens[2][1] + prot_itens[3][1]
    total = privado + assent + protegido + outros

    fig = plt.figure(figsize=(11.4, 4.7))
    axT = fig.add_axes([0.048, 0.640, 0.925, 0.145])
    axZ = fig.add_axes([0.048, 0.285, 0.925, 0.145])

    # ---- barra da tenure ---------------------------------------------------
    segs = [
        (t("Propriedade privada (SIGEF/SNCI + CAR)", "Private property (SIGEF/SNCI + CAR)"), privado, ACCENT_SOFT),
        (t("Assentamentos", "Settlements"), assent, PASTO),
        (t("Protegido", "Protected"), protegido, VEG),
        (t("Água, urbano, militar, gleba pública", "Water, urban, military, public land"), outros, AGUA),
    ]
    esq = 0.0
    x_prot = (0.0, 0.0)
    for rot, val, cor in segs:
        pct = val / total * 100
        axT.barh([0], [pct], left=esq, color=cor, height=0.8,
                 edgecolor=BG, linewidth=1.2)
        if pct > 20:
            axT.text(esq + pct / 2, 0, f"{rot}\n{vg(val)} Mha · {vg(pct, 1)}%",
                     ha="center", va="center", fontsize=9.6, color="white",
                     fontweight="600", linespacing=1.5)
        if rot == t("Protegido", "Protected"):
            x_prot = (esq, esq + pct)
        esq += pct

    axT.set_xlim(0, 100)
    axT.set_ylim(-0.55, 0.55)
    axT.axis("off")
    axT.text(0, 1.75, t("Quem é dono de Goiás", "Who owns Goiás"), transform=axT.transAxes,
             fontsize=11.5, fontweight="600", color=FG, va="bottom")
    axT.text(0, 1.20, t(f"território efetivo = {vg(total)} Mha  ·  APP e Reserva Legal "
                        f"({vg(d['Ativo Ambiental'])} Mha) são sobreposição, não classe",
                        f"effective territory = {vg(total)} Mha  ·  APP and Legal Reserve "
                        f"({vg(d['Ativo Ambiental'])} Mha) are an overlay, not a class"),
             transform=axT.transAxes, fontsize=9, color=MUTED, va="bottom")

    # Os tres buckets pequenos nao cabem dentro da barra: viram uma linha de
    # chips logo abaixo, na ordem em que aparecem nela.
    chip_x = 0.0
    for rot, val, cor in segs[1:]:
        axT.add_patch(plt.Rectangle((chip_x, -1.12), 1.05, 0.20, color=cor,
                                    clip_on=False))
        txt = f"{rot} — {vg(val)} Mha · {vg(val / total * 100, 1)}%"
        axT.text(chip_x + 1.7, -1.02, txt, fontsize=8.8, color=MUTED,
                 va="center", ha="left")
        chip_x += 1.9 + len(txt) * 0.63

    # ---- zoom no protegido -------------------------------------------------
    esqz = 0.0
    x_veda = None
    for rot, val, cor in prot_itens:
        largura = val / protegido * 100
        axZ.barh([0], [largura], left=esqz, color=cor, height=0.8,
                 edgecolor=BG, linewidth=1.2)
        rotulo = f"{rot}\n{vg(val)} Mha · {vg(val / total * 100, 1)}%" + t(" do estado", " of the state")
        if largura > 16:
            axZ.text(esqz + largura / 2, 0, rotulo, ha="center", va="center",
                     fontsize=8.9, color="white", fontweight="600", linespacing=1.5)
        else:
            # Fatia colada na borda direita: alinha o texto pela direita, senao
            # ele sai da figura.
            centro = esqz + largura / 2
            perto_da_borda = centro > 92
            axZ.annotate(rotulo, xy=(centro, -0.42),
                         xytext=(100 if perto_da_borda else centro, -1.35),
                         fontsize=8.4, color=cor,
                         ha="right" if perto_da_borda else "center", va="top",
                         fontweight="600", linespacing=1.5,
                         arrowprops=dict(arrowstyle="-", color=cor, lw=0.9))
        if rot == prot_itens[2][0]:
            x_veda = esqz
        esqz += largura

    # O que a lei de fato veda converter e' so' PI + TI — as duas ultimas.
    axZ.plot([x_veda, 100], [0.62, 0.62], color=ACCENT, lw=1.1, clip_on=False)
    for xx in (x_veda, 100):
        axZ.plot([xx, xx], [0.52, 0.62], color=ACCENT, lw=1.1, clip_on=False)
    axZ.text((x_veda + 100) / 2, 0.74,
             t(f"o que veda converter: {vg(veda)} Mha = {vg(veda / total * 100, 1)}% do estado",
               f"what forbids conversion: {vg(veda)} Mha = {vg(veda / total * 100, 1)}% of the state"),
             ha="center", va="bottom", fontsize=8.8, color=ACCENT, fontweight="600")

    axZ.set_xlim(0, 100)
    axZ.set_ylim(-0.55, 0.55)
    axZ.axis("off")
    axZ.text(0, 1.52, t(f"os {vg(protegido / total * 100, 1)}% protegidos, abertos",
                       f"the {vg(protegido / total * 100, 1)}% protected, opened up"),
             transform=axZ.transAxes, fontsize=9.8, fontweight="600",
             color=FG, va="bottom")

    # Cunha de zoom: idioma padrao de "barra da barra", mais legivel que duas
    # linhas soltas de conexao.
    fig.add_artist(Polygon(
        [[axT.transData.transform((x_prot[0], -0.55))[0] / fig.bbox.width, 0.640],
         [axT.transData.transform((x_prot[1], -0.55))[0] / fig.bbox.width, 0.640],
         [0.973, 0.430], [0.048, 0.430]],
        closed=True, transform=fig.transFigure, facecolor=VEG, alpha=0.09,
        edgecolor="none", zorder=0))

    rodape(fig, t("Malha Fundiária Ambiental LAPIG-UFG v1.0 (snapshot abr/2026), recorte de Goiás, "
                  "área em ESRI:102033 · outputs/diag_malha_fundiaria_por_classe.csv",
                  "LAPIG-UFG Environmental Land Tenure Layer v1.0 (Apr/2026 snapshot), Goiás clip, "
                  "area in ESRI:102033 · outputs/diag_malha_fundiaria_por_classe.csv"))

    out = OUT_DIR / f"malha_fundiaria_buckets{SUFIXO}"
    fig.savefig(out, dpi=190, facecolor=BG)
    plt.close(fig)
    print(f"[2] {out.name}")
    print(f"    privado {privado:.2f} ({privado/total*100:.1f}%) · "
          f"protegido {protegido:.2f} ({protegido/total*100:.1f}%) · "
          f"veda converter {veda:.3f} ({veda/total*100:.1f}%) · "
          f"TI {(prot_itens[3][1]*1000):.0f} mil ha · total {total:.2f} Mha")


# ======================================================================
# 3. AMC — o "colapso" que era perda de territorio
# ======================================================================
def fig_amc():
    src = REPO_ROOT / "outputs" / "diagnosticos" / "amc_impacto_goias.csv"
    d = pd.read_csv(src).sort_values("ano")

    # Quantos municipios foram emancipados em cada onda (#16 / doc AMC).
    n_emancipados = {1989: 27, 1993: 21, 1997: 10, 2001: 4}
    # Nome do municipio da pior queda, onde o doc registra o caso nominal
    # (Textos/metodologia/areas_minimas_comparaveis.md).
    exemplo = {1989: "Formoso", 1993: "Mambaí"}

    fig, ax = plt.subplots(figsize=(11.4, 4.6))
    fig.subplots_adjust(left=0.075, right=0.845, top=0.775, bottom=0.245)

    y = np.arange(len(d))[::-1]
    mun = d.pior_queda_municipio_membro_pct.values
    amc = d.pior_queda_amc_grupo_pct.values

    for yy, m, a in zip(y, mun, amc):
        ax.plot([m, a], [yy, yy], color=RULE, lw=3.4, solid_capstyle="round", zorder=1)
    ax.scatter(mun, y, s=115, color=ACCENT, zorder=3,
               label=t("município, como o IBGE tabula", "municipality, as IBGE tabulates it"))
    ax.scatter(amc, y, s=115, color=VEG, zorder=3,
               label=t("AMC — o município somado aos que dele saíram",
                     "AMC — the municipality plus those split off from it"))

    for yy, m, a, ano in zip(y, mun, amc, d.ano):
        nome = exemplo.get(int(ano))
        rot = f"{m:.0f}%".replace("-", "−")
        ax.annotate(f"{nome}  {rot}" if nome else rot, (m, yy),
                    textcoords="offset points", xytext=(-11, 0), ha="right",
                    va="center", fontsize=9.4, color=ACCENT, fontweight="600")
        ax.annotate(f"{a:.0f}%".replace("-", "−"), (a, yy),
                    textcoords="offset points", xytext=(11, 0), ha="left",
                    va="center", fontsize=9.4, color=VEG, fontweight="600")

    ax.set_yticks(y, [str(int(a)) for a in d.ano], fontsize=10.5)
    ax.set_xlim(-102, 6)
    ax.set_xticks([-80, -60, -40, -20, 0], ["−80%", "−60%", "−40%", "−20%", "0"])
    ax.axvline(0, color=RULE, lw=1.0)
    limpar(ax, esquerda=False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel(t("pior queda de rebanho bovino registrada no ano da onda",
                   "worst cattle-herd drop recorded in the year of the wave"))
    titulo(ax, t("O ano em que um município perde 81% do rebanho sem perder uma vaca",
                 "The year a municipality loses 81% of its herd without losing a cow"),
           sub=t("ondas de emancipação em Goiás: a mesma queda, medida de dois jeitos",
                 "waves of municipal splits in Goiás: the same drop, measured two ways"))

    for yy, ano in zip(y, d.ano):
        ax.text(1.015, yy, f"{n_emancipados[int(ano)]} " + t("municípios\nemancipados", "new\nmunicipalities"),
                transform=ax.get_yaxis_transform(), fontsize=8.6, color=MUTED,
                va="center", ha="left", linespacing=1.5)

    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.215), ncol=2, frameon=False,
              fontsize=9, handletextpad=0.4, columnspacing=2.2)

    rodape(fig, t("SIDRA/PPM (rebanho bovino municipal) × agregação AMC de Ehrl (2017) para Goiás "
                  "· outputs/diagnosticos/amc_impacto_goias.csv",
                  "SIDRA/PPM (municipal cattle herd) × AMC aggregation of Ehrl (2017) for Goiás "
                  "· outputs/diagnosticos/amc_impacto_goias.csv"))

    out = OUT_DIR / f"amc_emancipacoes{SUFIXO}"
    fig.savefig(out, dpi=190, facecolor=BG)
    plt.close(fig)
    print(f"[3] {out.name}")
    print("    " + " · ".join(
        f"{int(r.ano)}: mun {r.pior_queda_municipio_membro_pct:.1f}% / "
        f"amc {r.pior_queda_amc_grupo_pct:.1f}%" for r in d.itertuples()))


# ======================================================================
# 4. O calendario que os dados escreveram sozinhos
# ======================================================================
def fig_quebras():
    src = REPO_ROOT / "outputs" / "correlacoes" / "quebras_resultados.csv"
    d = pd.read_csv(src)

    # (ano, rotulo, fileira) — fileira alterna para marcos vizinhos nao colidirem.
    marcos = [
        (1994, "Plano Real", 0),
        (1996, "Lei Kandir", 1),
        (2002, "Plano Safra", 0),
        (2003, t("Boom das commodities", "Commodity boom"), 1),
        (2012, t("Código Florestal", "Forest Code"), 0),
        (2018, "Cerrado Manifesto", 0),
    ]
    fileira_y = {0: 1.62, 1: 1.90}
    cor_classe = {"vegetacao_natural": VEG, "pastagem": PASTO, "agricultura": AGRIC}
    lane = {"Goiás": 1.0, "Tocantins": 0.0}

    fig, ax = plt.subplots(figsize=(11.4, 4.8))
    fig.subplots_adjust(left=0.055, right=0.985, top=0.845, bottom=0.230)

    for ano, rot, fil in marcos:
        destaque = ano == 2012
        yl = fileira_y[fil]
        ax.vlines(ano, -0.62, yl - 0.08, color=ACCENT if destaque else RULE,
                  lw=1.4 if destaque else 1.0,
                  ls=(0, (4, 3)) if destaque else (0, (2, 4)), zorder=1)
        ax.text(ano, yl, rot, ha="center", va="center", fontsize=8.6,
                color=ACCENT if destaque else MUTED,
                fontweight="600" if destaque else "normal")

    for uf, yy in lane.items():
        ax.axhline(yy, color=RULE, lw=0.9, zorder=1)
        ax.text(1985.0, yy + 0.13, uf, fontsize=10.5, fontweight="600",
                color=FG, va="bottom", ha="left")

    # Jitter vertical por classe: quebras do mesmo ano na mesma UF nao se cobrem.
    desl = {"vegetacao_natural": 0.0, "pastagem": -0.16, "agricultura": 0.16}
    for r in d.itertuples():
        yy = lane[r.uf] + desl[r.classe_lulc]
        orfa = not r.coincide_marco
        ax.scatter([r.ano_quebra], [yy], s=44 + 2.6 * min(r.f_stat, 90),
                   color="none" if orfa else cor_classe[r.classe_lulc],
                   edgecolor=cor_classe[r.classe_lulc],
                   linewidth=1.8 if orfa else 0.0, zorder=4)
        if orfa:
            # A pastagem ja' ocupa a faixa de baixo do lane; as outras classes
            # levam o rotulo para cima para nao encostar no vizinho.
            desloc = (0, -20) if r.classe_lulc == "pastagem" else (0, 15)
            ax.annotate(str(r.ano_quebra), (r.ano_quebra, yy),
                        textcoords="offset points", xytext=desloc, ha="center",
                        fontsize=8, color=MUTED, fontweight="600")

    ax.set_xlim(1984.4, 2025.6)
    ax.set_ylim(-0.62, 2.06)
    ax.set_yticks([])
    ax.set_xticks(range(1985, 2025, 5))
    limpar(ax, esquerda=False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(t("ano da quebra estrutural detectada", "year of the detected structural break"))
    titulo(ax, t("Onde as séries quebram — e onde a lei mais esperada não deixa marca",
                 "Where the series break — and where the most expected law leaves no mark"),
           sub=t("15 quebras achadas sem olhar para nenhum marco; Tocantins entra como controle",
                 "15 breaks found without looking at any milestone; Tocantins enters as a control"))

    ax.text(2012, 0.5, t("nenhuma quebra em\nnenhuma das seis séries", "no break in\nany of the six series"),
            ha="center", va="center", fontsize=8.6, color=ACCENT,
            fontweight="600", linespacing=1.5, zorder=5,
            bbox=dict(boxstyle="round,pad=0.45", fc=BG, ec=ACCENT, lw=0.9))

    legenda = [
        Line2D([], [], marker="o", ls="", ms=8, mfc=VEG, mec=VEG, label=t("vegetação natural", "natural vegetation")),
        Line2D([], [], marker="o", ls="", ms=8, mfc=PASTO, mec=PASTO, label=t("pastagem", "pasture")),
        Line2D([], [], marker="o", ls="", ms=8, mfc=AGRIC, mec=AGRIC, label=t("agricultura", "cropland")),
        Line2D([], [], marker="o", ls="", ms=8, mfc="none", mec=MUTED, mew=1.8,
               label=t("órfã: sem marco a ±2 anos", "orphan: no milestone within ±2 years")),
        Line2D([], [], marker="o", ls="", ms=11, mfc=CINZA, mec=CINZA, alpha=0.5,
               label=t("área do ponto = força da quebra (F)", "dot area = break strength (F)")),
    ]
    ax.legend(handles=legenda, loc="upper left", bbox_to_anchor=(0.0, -0.175),
              ncol=5, frameon=False, fontsize=8.6, handletextpad=0.35,
              columnspacing=1.5)

    rodape(fig, t("MapBiomas col. 10.1 (Δ anual por classe, GO e TO) · sup-F de Quandt-Andrews com "
                  "segmentação binária, F > 5,0 · outputs/correlacoes/quebras_resultados.csv",
                  "MapBiomas col. 10.1 (annual Δ by class, GO and TO) · Quandt-Andrews sup-F with "
                  "binary segmentation, F > 5.0 · outputs/correlacoes/quebras_resultados.csv"))

    out = OUT_DIR / f"quebras_calendario{SUFIXO}"
    fig.savefig(out, dpi=190, facecolor=BG)
    plt.close(fig)
    orfas = d[~d.coincide_marco]
    print(f"[4] {out.name}")
    print(f"    {len(d)} quebras · {len(orfas)} órfãs em {sorted(orfas.ano_quebra.unique())}")
    print(f"    quebras a ±2 anos de 2012: {((d.ano_quebra - 2012).abs() <= 2).sum()}")


def main():
    fig_oscilacao()
    fig_malha()
    fig_amc()
    fig_quebras()
    print(f"\nSaída em {OUT_DIR}")


if __name__ == "__main__":
    main()
