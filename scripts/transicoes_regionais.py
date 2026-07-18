"""
Pipeline #33 — Mecanismo de transições por mesorregião × ato (Camada 2)
======================================================================

PERGUNTA QUE RESPONDE
---------------------
O Pipeline #32 (centro de massa) mostrou O QUÊ se moveu: pasto e rebanho
marcharam para o norte e a agricultura congelou no Ato III. Este pipeline mostra
O MECANISMO — quais transições de uso da terra, em qual mesorregião, produziram
esse movimento. A hipótese é um gradiente Sul→Norte:

  - SUL Goiano:      pastagem → agricultura  (a lavoura come o pasto e
                     empurra o rebanho para fora — pasto-reserva jovem, #28: ~9 anos)
  - NORTE/NOROESTE:  vegetação natural → pastagem  (o pasto abre fronteira nova
                     sobre o Cerrado — pasto sobre veg., #28: pasto antigo ~20 anos)

Se isso se confirmar, é a engrenagem por trás da migração do centroide (#32).

ABORDAGEM
---------
Re-corta as conversões brutas ano-a-ano (`conversao_bruta_municipal.csv`, do
#19/#12) por (mesorregião × ato), reusando a maquinaria do #25
(`analise_transicoes.py`): matriz 6×6, fluxo bruto/líquido, Sankey. Sobre isso:
  1. Matriz 6×6 de transição por mesorregião × ato.
  2. Fluxos-chave por mesorregião × ato: pasto→agric, veg→pasto, agric→pasto,
     veg→agric + balanço líquido de pastagem e agricultura.
  3. Conversão dominante (off-diagonal) por mesorregião × ato.
  4. Cruzamento com #28 (idade mediana do pasto na conversão, por mesorregião) —
     conecta o fluxo pasto→agric à idade do pasto convertido.
  5. Foco no Ato III (2020-24), o recorte mais limpo de deslocamento (#32).

ENTRADAS
    data/processed/conversao_bruta_municipal.csv   (#19, 235.948 linhas)
    data/processed/mapeamento_mesorregioes.csv     (#18)
    data/processed/pastagem_idade_conversao.csv    (#28, idade por mesorregião)

SAÍDAS
    data/processed/transicoes_regionais_matrizes.csv     (meso×ato: 6×6 long)
    data/processed/transicoes_regionais_fluxos_chave.csv (meso×ato: fluxos + idade)
    data/processed/transicoes_regionais_dominante.csv    (meso×ato: top conversão)
    outputs/transicoes_regionais/fluxos_chave.png        (barras Sul→Norte por ato)
    outputs/transicoes_regionais/dominante_grid.png      (grade meso×ato)
    Visualizacao/assets/data/sankey_regional.json        (mini-Sankey por meso×ato)

COMO RODAR
    python scripts/transicoes_regionais.py
    python scripts/transicoes_regionais.py --sem-figuras

Depende de: #19 (conversões), #18 (mesorregiões), #28 (idade). Reusa #25.
Quando foi feito: 2026-06-06. Camada 2 da narrativa de deslocamento Sul→Norte.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS, CORES_ATO  # noqa: E402
from analise_transicoes import (  # noqa: E402  (reusa a maquinaria do #25)
    GRUPOS, GRUPO_LABEL, GRUPO_COR, matriz_ato, fluxo_bruto_liquido, sankey_json,
)

ROOT          = Path(__file__).resolve().parent.parent
DIR_PROC      = ROOT / "data" / "processed"
DIR_OUT       = ROOT / "outputs" / "transicoes_regionais"
DIR_VIZ_DATA  = ROOT / "Visualizacao" / "assets" / "data"
for d in (DIR_OUT,):
    d.mkdir(parents=True, exist_ok=True)

ARQ_CONV  = DIR_PROC / "conversao_bruta_municipal.csv"
ARQ_MESO  = DIR_PROC / "mapeamento_mesorregioes.csv"
ARQ_IDADE = DIR_PROC / "pastagem_idade_conversao.csv"

# Fluxos-chave para o teste de mecanismo (orig, dest, rótulo).
FLUXOS_CHAVE = [
    ("pastagem", "agricultura",          "pasto→agric"),
    ("vegetacao_natural", "pastagem",    "veg→pasto"),
    ("agricultura", "pastagem",          "agric→pasto"),
    ("vegetacao_natural", "agricultura", "veg→agric"),
]

# Ordem de fallback Sul→Norte (caso o cálculo por latitude falhe).
MESO_ORDER_FALLBACK = ["Sul Goiano", "Leste Goiano", "Centro Goiano",
                       "Noroeste Goiano", "Norte Goiano"]


# ---------------------------------------------------------------------------
# 1. Carga e ordenação espacial
# ---------------------------------------------------------------------------

def carregar() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Conversões municipais com mesorregião anexada; idade #28; ordem Sul→Norte."""
    conv = pd.read_csv(ARQ_CONV)
    meso = pd.read_csv(ARQ_MESO)[["cd_mun", "nm_meso"]]
    conv = conv.merge(meso, on="cd_mun", how="left")
    sem_meso = conv["nm_meso"].isna().sum()
    if sem_meso:
        print(f"[carga] {sem_meso} linhas sem mesorregião (descartadas)")
    conv = conv.dropna(subset=["nm_meso"])

    idade = pd.read_csv(ARQ_IDADE).dropna(subset=["mesorregiao"])

    # Ordem Sul→Norte pela latitude média dos pixels de conversão do #28.
    lat = idade.groupby("mesorregiao")["lat"].mean().sort_values()  # menor lat = sul
    ordem = [m for m in lat.index if m in conv["nm_meso"].unique()]
    faltando = [m for m in conv["nm_meso"].unique() if m not in ordem]
    ordem += faltando
    if set(ordem) != set(MESO_ORDER_FALLBACK):
        print(f"[carga] aviso: mesos {sorted(set(ordem))} != esperado")
    print("[carga] ordem Sul→Norte (lat média dos pixels #28):")
    for m in ordem:
        print(f"        {m:18s} lat={lat.get(m, float('nan')):.2f}")
    return conv, idade, ordem


# ---------------------------------------------------------------------------
# 2. Matrizes 6×6 por (mesorregião × ato)
# ---------------------------------------------------------------------------

def matrizes_regionais(conv: pd.DataFrame, ordem: list[str]) -> dict:
    """{(meso, ato): matriz 6×6 em Mha}. Off-diagonal = conversão; diagonal =
    persistência. Usa matriz_ato (#25) sobre o subconjunto meso×ato."""
    mats = {}
    for meso in ordem:
        for ato, info in ATOS.items():
            ini, fim = info["inicio"], info["fim"]
            sub = conv[(conv.nm_meso == meso) &
                       (conv.ano_origem >= ini) & (conv.ano_destino <= fim)]
            if sub.empty:
                continue
            mats[(meso, ato)] = matriz_ato(sub)
    return mats


def matrizes_para_long(mats: dict) -> pd.DataFrame:
    linhas = []
    for (meso, ato), m in mats.items():
        for orig in GRUPOS:
            for dest in GRUPOS:
                linhas.append({"mesorregiao": meso, "ato": ato,
                               "grupo_orig": orig, "grupo_dest": dest,
                               "area_mha": round(float(m.loc[orig, dest]), 4)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 3. Fluxos-chave + balanço + idade do pasto (#28)
# ---------------------------------------------------------------------------

def idade_mediana_por_meso(idade: pd.DataFrame) -> pd.DataFrame:
    """Idade mediana do pasto na conversão p/ agricultura, por meso (e meso×ato)."""
    geral = idade.groupby("mesorregiao")["idade_pastagem_anos"].median()
    # Por ato (ano_conversao dentro das fronteiras do ato).
    def ato_de(ano):
        for a, info in ATOS.items():
            if info["inicio"] <= ano <= info["fim"]:
                return a
        return None
    idade = idade.copy()
    idade["ato"] = idade["ano_conversao"].map(ato_de)
    por_ato = (idade.dropna(subset=["ato"])
               .groupby(["mesorregiao", "ato"])["idade_pastagem_anos"].median())
    return geral, por_ato


def fluxos_chave(mats: dict, idade_geral, idade_ato) -> pd.DataFrame:
    """Por meso×ato: fluxos-chave + balanço líquido de pasto/agric + idade #28.

    Os atos têm durações MUITO diferentes (I=15a, II=18a, III=4a), então o total
    em Mha não é comparável entre atos. Por isso cada fluxo vem também em TAXA
    ANUAL (Mha/ano = total / nº de anos do ato), que é o que se compara entre atos.
    """
    linhas = []
    for (meso, ato), m in mats.items():
        info = ATOS[ato]
        n_anos = info["fim"] - info["inicio"]
        reg = {"mesorregiao": meso, "ato": ato, "n_anos": n_anos}
        for orig, dest, rot in FLUXOS_CHAVE:
            v = float(m.loc[orig, dest])
            reg[rot] = round(v, 4)
            reg[f"{rot}/ano"] = round(v / n_anos, 5)
        # Balanço líquido (ganhos − perdas), excluindo persistência.
        for g in ("pastagem", "agricultura"):
            ganhos = sum(float(m.loc[o, g]) for o in GRUPOS if o != g)
            perdas = sum(float(m.loc[g, d]) for d in GRUPOS if d != g)
            reg[f"net_{g}"] = round(ganhos - perdas, 4)
            reg[f"net_{g}/ano"] = round((ganhos - perdas) / n_anos, 5)
        reg["conversao_total"] = round(
            float(m.values.sum() - np.trace(m.values)), 4)
        reg["idade_pasto_mediana_a"] = round(float(idade_ato.get((meso, ato), np.nan)), 1)
        linhas.append(reg)
    return pd.DataFrame(linhas)


def dominante(mats: dict) -> pd.DataFrame:
    """Conversão off-diagonal dominante por meso×ato + sua fração da conversão."""
    linhas = []
    for (meso, ato), m in mats.items():
        off = m.copy().astype(float)
        np.fill_diagonal(off.values, 0.0)
        total = off.values.sum()
        if total <= 0:
            continue
        orig = off.values.max(axis=1).argmax()
        o = GRUPOS[orig]
        d = GRUPOS[int(off.loc[o].values.argmax())]
        linhas.append({"mesorregiao": meso, "ato": ato,
                       "grupo_orig": o, "grupo_dest": d,
                       "area_mha": round(float(off.loc[o, d]), 4),
                       "pct_da_conversao": round(float(off.loc[o, d]) / total * 100, 1)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 4. Figuras
# ---------------------------------------------------------------------------

def fig_fluxos_chave(fluxos: pd.DataFrame, ordem: list[str],
                     idade_geral: pd.Series) -> None:
    """Barras agrupadas pasto→agric vs veg→pasto, por mesorregião (Sul→Norte),
    em painéis por ato. Anota a idade mediana do pasto (#28) sob cada meso."""
    import matplotlib.pyplot as plt

    atos = list(ATOS.keys())
    fig, axes = plt.subplots(1, len(atos), figsize=(5.4 * len(atos), 6.2), sharey=True)
    x = np.arange(len(ordem))
    w = 0.38
    cor_pa = GRUPO_COR["agricultura"]      # pasto→agric (pinta como agricultura)
    cor_vp = GRUPO_COR["vegetacao_natural"]  # veg→pasto

    for ax, ato in zip(np.atleast_1d(axes), atos):
        sub = fluxos[fluxos.ato == ato].set_index("mesorregiao").reindex(ordem)
        ax.bar(x - w/2, sub["pasto→agric/ano"], w, color=cor_pa, label="pasto→agric")
        ax.bar(x + w/2, sub["veg→pasto/ano"],  w, color=cor_vp, label="veg→pasto")
        info = ATOS[ato]
        ax.set_title(f"Ato {ato} ({info['inicio']}–{info['fim']}, {info['fim']-info['inicio']}a)"
                     f"\n{info['titulo']}",
                     fontsize=11, color=CORES_ATO.get(ato, "0.2"))
        ax.set_xticks(x)
        rot = [m.replace(" Goiano", "") for m in ordem]
        ax.set_xticklabels(rot, rotation=30, ha="right", fontsize=9)
        ax.grid(True, axis="y", alpha=0.25)
        ax.margins(x=0.02)

    np.atleast_1d(axes)[0].set_ylabel("Conversão (Mha/ano — comparável entre atos)")
    # Eixo-x didático: seta Sul→Norte.
    fig.text(0.5, 0.015, "◄ SUL          mesorregião (ordenada por latitude)          NORTE ►",
             ha="center", fontsize=10, color="0.35")
    handles, labels = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", frameon=True, fontsize=10)
    fig.suptitle("Mecanismo Sul→Norte: pasto→agric (sul) vs veg→pasto (norte), "
                 "por mesorregião e ato", fontsize=13, y=0.99)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(DIR_OUT / "fluxos_chave.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'fluxos_chave.png').relative_to(ROOT)}")


def fig_dominante_grid(dom: pd.DataFrame, ordem: list[str]) -> None:
    """Grade mesorregião (linhas, Norte em cima) × ato (colunas). Cada célula: a
    conversão dominante + magnitude, fundo na cor do grupo de DESTINO."""
    import matplotlib.pyplot as plt

    atos = list(ATOS.keys())
    ordem_norte_cima = list(reversed(ordem))   # norte no topo (estilo mapa)
    fig, ax = plt.subplots(figsize=(2.4 * len(atos) + 2, 1.05 * len(ordem) + 1.5))

    seta = {"pastagem": "→pasto", "agricultura": "→agric",
            "vegetacao_natural": "→veg", "agua": "→água",
            "area_urbana": "→urb", "outros": "→outros"}
    for i, meso in enumerate(ordem_norte_cima):
        for j, ato in enumerate(atos):
            r = dom[(dom.mesorregiao == meso) & (dom.ato == ato)]
            if r.empty:
                continue
            r = r.iloc[0]
            cor = GRUPO_COR.get(r["grupo_dest"], "#cccccc")
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=cor, alpha=0.30,
                                       edgecolor="white", lw=2))
            txt = (f"{GRUPO_LABEL[r['grupo_orig']].split()[0]}{seta[r['grupo_dest']]}\n"
                   f"{r['area_mha']:.2f} Mha\n({r['pct_da_conversao']:.0f}% da conv.)")
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=9)

    ax.set_xlim(0, len(atos)); ax.set_ylim(0, len(ordem))
    ax.set_xticks(np.arange(len(atos)) + 0.5)
    ax.set_xticklabels([f"Ato {a}\n{ATOS[a]['inicio']}–{ATOS[a]['fim']}" for a in atos],
                       fontsize=10)
    ax.set_yticks(np.arange(len(ordem)) + 0.5)
    ax.set_yticklabels([m.replace(" Goiano", "") for m in ordem_norte_cima], fontsize=10)
    # O eixo-y do matplotlib cresce para cima, então i=0 (Norte) cairia na base.
    # Invertê-lo põe Norte no topo (estilo mapa), alinhando com as anotações
    # NORTE/SUL abaixo (que são fixas em transAxes) e com a leitura "marcha ao norte".
    ax.invert_yaxis()
    ax.text(-0.06, 0.98, "NORTE", transform=ax.transAxes, fontsize=9, color="0.4", va="top")
    ax.text(-0.06, 0.02, "SUL", transform=ax.transAxes, fontsize=9, color="0.4", va="bottom")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Conversão dominante por mesorregião × ato\n"
                 "(fundo = cor do uso de destino)", fontsize=12)
    fig.tight_layout()
    fig.savefig(DIR_OUT / "dominante_grid.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / 'dominante_grid.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 5. Sankey por meso×ato (para a Visualizacao)
# ---------------------------------------------------------------------------

def salvar_sankeys(mats: dict) -> None:
    blocos = []
    for (meso, ato), m in mats.items():
        info = ATOS[ato]
        sk = sankey_json(m, ato, info["inicio"], info["fim"],
                         f"{meso} — Ato {ato}")
        sk["mesorregiao"] = meso
        blocos.append(sk)
    out = DIR_VIZ_DATA / "sankey_regional.json"
    if DIR_VIZ_DATA.exists():
        out.write_text(json.dumps(blocos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[viz] {out.relative_to(ROOT)}  ({len(blocos)} mini-Sankeys)")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def resumo_mecanismo(fluxos: pd.DataFrame, ordem: list[str], idade_geral: pd.Series) -> None:
    """Teste explícito: Sul vs Norte/Noroeste em pasto→agric e veg→pasto."""
    sul = ordem[0]
    norte = ordem[-2:]   # as duas mais ao norte
    print("\n[mecanismo] taxa anual (Mha/ano) — pasto→agric (sul) vs veg→pasto (norte):")
    for ato in ATOS:
        f = fluxos[fluxos.ato == ato].set_index("mesorregiao")
        pa_sul = f.loc[sul, "pasto→agric/ano"] if sul in f.index else np.nan
        vp_norte = f.reindex(norte)["veg→pasto/ano"].sum()
        pa_norte = f.reindex(norte)["pasto→agric/ano"].sum()
        print(f"  Ato {ato}: {sul} pasto→agric={pa_sul:.4f} | "
              f"Norte+Noroeste veg→pasto={vp_norte:.4f} vs pasto→agric={pa_norte:.4f}")
    print("\n[mecanismo] idade mediana do pasto na conversão (#28), por meso:")
    for m in ordem:
        print(f"  {m:18s} {idade_geral.get(m, float('nan')):.0f} anos")


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #33 — transições por mesorregião × ato")
    ap.add_argument("--sem-figuras", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #33 — Mecanismo de transições por mesorregião × ato (Camada 2)")
    print("=" * 70)

    conv, idade, ordem = carregar()
    mats = matrizes_regionais(conv, ordem)
    print(f"[matrizes] {len(mats)} combinações meso×ato")

    idade_geral, idade_ato = idade_mediana_por_meso(idade)
    long = matrizes_para_long(mats)
    fluxos = fluxos_chave(mats, idade_geral, idade_ato)
    dom = dominante(mats)

    long.to_csv(DIR_PROC / "transicoes_regionais_matrizes.csv", index=False, encoding="utf-8")
    fluxos.to_csv(DIR_PROC / "transicoes_regionais_fluxos_chave.csv", index=False, encoding="utf-8")
    dom.to_csv(DIR_PROC / "transicoes_regionais_dominante.csv", index=False, encoding="utf-8")
    print(f"\n[OK] transicoes_regionais_matrizes.csv  ({len(long)} linhas)")
    print(f"[OK] transicoes_regionais_fluxos_chave.csv ({len(fluxos)} linhas)")
    print(f"[OK] transicoes_regionais_dominante.csv  ({len(dom)} linhas)")

    resumo_mecanismo(fluxos, ordem, idade_geral)

    if not args.sem_figuras:
        print()
        fig_fluxos_chave(fluxos, ordem, idade_geral)
        fig_dominante_grid(dom, ordem)
        salvar_sankeys(mats)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #33. Camada 2 (mecanismo) da narrativa Sul→Norte.")
    print("=" * 70)


if __name__ == "__main__":
    main()
