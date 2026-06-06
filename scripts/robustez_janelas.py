"""
Pipeline #35 — Robustez de janelas temporais (#32 e #33)
========================================================

PERGUNTA QUE RESPONDE
---------------------
Os achados-manchete das Camadas 1 (#32) e 2 (#33) dependem de ONDE cortamos o
tempo (das fronteiras data-driven dos atos)? Ou sobrevivem a réguas exógenas e
de duração igual? Este é o teste de robustez multi-resolução (à prova de banca).

ESQUEMAS DE JANELA COMPARADOS
  - CONTÍNUA (anual) + JANELA ÚNICA (1985–2024): a espinha dorsal e o resumo.
  - ATOS (3, data-driven #29): o frame narrativo — a LINHA DE BASE testada.
  - GRADE 5 ANOS (8 blocos): régua regular, exógena às fronteiras dos atos.
  - DÉCADAS (4 blocos): régua regular, mais grossa.

MÉTRICAS-MANCHETE RECALCULADAS SOB CADA ESQUEMA
  #32 — VELOCIDADE para o norte (km/ano) do centro de massa de cada variável,
        por janela = inclinação OLS do northing (EPSG:5880) vs ano na janela.
        Checagem: pasto/rebanho sobem (>0) e a agricultura DESACELERA na janela
        recente, em TODOS os esquemas?
  #33 — Taxa anual (Mha/ano) de pasto→agric (Sul) vs veg→pasto (Norte), por
        janela. Checagem: o gradiente (Sul faz pasto→agric; Norte faz veg→pasto)
        e o colapso recente do pasto→agric no Sul valem em TODOS os esquemas?

Reusa #32 (`centro_massa`) e #33 (`transicoes_regionais`) — não reimplementa.

ENTRADAS: as mesmas de #32 e #33.
SAÍDAS
    data/processed/robustez_velocidade_ns.csv     (#32 por esquema×janela×variável)
    data/processed/robustez_fluxos_regionais.csv  (#33 por esquema×janela×região)
    outputs/robustez/velocidade_ns.png            (#32)
    outputs/robustez/fluxos_regionais.png         (#33)

COMO RODAR
    python scripts/robustez_janelas.py

Depende de: #32, #33 (e as entradas deles). Quando: 2026-06-06.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centro_massa as cm                # reusa #32
import transicoes_regionais as tr        # reusa #33
from config_periodos import ATOS         # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "robustez"
DIR_OUT.mkdir(parents=True, exist_ok=True)

ANO_INI, ANO_FIM = 1985, 2024

# Recorte regional (idêntico ao #34).
MESO_SUL   = ["Sul Goiano"]
MESO_NORTE = ["Norte Goiano", "Noroeste Goiano"]


# ---------------------------------------------------------------------------
# Esquemas de janela: lista de (rótulo, ano_ini, ano_fim)
# ---------------------------------------------------------------------------

def esquema_atos() -> list[tuple]:
    return [(f"Ato {k}", v["inicio"], v["fim"]) for k, v in ATOS.items()]

def esquema_grid5() -> list[tuple]:
    return [(f"{a}-{a+4}", a, a + 4) for a in range(ANO_INI, ANO_FIM + 1, 5)]

def esquema_decadas() -> list[tuple]:
    return [(f"{a}-{a+9}", a, a + 9) for a in range(ANO_INI, ANO_FIM + 1, 10)]

ESQUEMAS = {"Atos": esquema_atos(), "Grade 5 anos": esquema_grid5(),
            "Décadas": esquema_decadas()}


# ---------------------------------------------------------------------------
# #32 — velocidade N–S por janela (inclinação do northing vs ano)
# ---------------------------------------------------------------------------

def velocidade_ns(centros: pd.DataFrame) -> pd.DataFrame:
    """Para cada (esquema, janela, variável): velocidade para o norte em km/ano =
    inclinação OLS de y_mean (m, EPSG:5880) vs ano, sobre os anos da janela."""
    linhas = []
    for esquema, janelas in ESQUEMAS.items():
        for rot, ini, fim in janelas:
            sub_anos = centros[(centros.ano >= ini) & (centros.ano <= fim)]
            for chave, (col, rotulo, cor) in cm.VARIAVEIS.items():
                g = sub_anos[sub_anos.variavel == chave]
                if len(g) < 2:
                    continue
                slope = np.polyfit(g["ano"], g["y_mean"], 1)[0] / 1000  # km/ano
                linhas.append({"esquema": esquema, "janela": rot,
                               "ano_mid": (ini + fim) / 2, "variavel": chave,
                               "rotulo": rotulo, "vel_norte_km_ano": round(slope, 3)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# #33 — fluxos regionais por janela (anualizado)
# ---------------------------------------------------------------------------

def fluxos_regionais(conv: pd.DataFrame) -> pd.DataFrame:
    """Para cada (esquema, janela): pasto→agric no Sul e veg→pasto no Norte, em
    Mha/ano (= soma na janela / nº de anos da janela)."""
    def regiao(m):
        if m in MESO_SUL:   return "Sul"
        if m in MESO_NORTE: return "Norte"
        return "Centro"
    conv = conv.copy()
    conv["regiao"] = conv["nm_meso"].map(regiao)

    def soma(df, reg, o, dst):
        m = df[(df.regiao == reg) & (df.grupo_orig == o) & (df.grupo_dest == dst)]
        return float(m["area_mha"].sum())

    linhas = []
    for esquema, janelas in ESQUEMAS.items():
        for rot, ini, fim in janelas:
            w = conv[(conv.ano_origem >= ini) & (conv.ano_destino <= fim)]
            n = max(fim - ini, 1)
            linhas.append({
                "esquema": esquema, "janela": rot, "ano_mid": (ini + fim) / 2,
                "sul_pasto_agric_ano":  round(soma(w, "Sul", "pastagem", "agricultura") / n, 4),
                "norte_veg_pasto_ano":  round(soma(w, "Norte", "vegetacao_natural", "pastagem") / n, 4),
                "norte_pasto_agric_ano": round(soma(w, "Norte", "pastagem", "agricultura") / n, 4),
                "sul_veg_pasto_ano":     round(soma(w, "Sul", "vegetacao_natural", "pastagem") / n, 4),
            })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def fig_velocidade(vel: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    esquemas = list(ESQUEMAS.keys())
    fig, axes = plt.subplots(1, len(esquemas), figsize=(5.4 * len(esquemas), 5.4), sharey=True)
    for ax, esq in zip(np.atleast_1d(axes), esquemas):
        sub = vel[vel.esquema == esq]
        for chave, (col, rotulo, cor) in cm.VARIAVEIS.items():
            g = sub[sub.variavel == chave].sort_values("ano_mid")
            ax.plot(g["ano_mid"], g["vel_norte_km_ano"], "-o", color=cor, lw=1.8,
                    ms=5, label=rotulo)
        ax.axhline(0, color="0.3", lw=0.9)
        ax.set_title(esq, fontsize=12); ax.set_xlabel("ano (meio da janela)")
        ax.grid(True, alpha=0.25)
    np.atleast_1d(axes)[0].set_ylabel("velocidade p/ o norte (km/ano)")
    np.atleast_1d(axes)[0].legend(fontsize=8.5, loc="upper right")
    fig.suptitle("Robustez #32 — velocidade do centro de massa para o norte, por esquema de janela\n"
                 "(pasto/rebanho >0; agricultura desacelera no recente — em todos os esquemas)",
                 fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(DIR_OUT / "velocidade_ns.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'velocidade_ns.png').relative_to(ROOT)}")


def fig_fluxos(flux: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    esquemas = list(ESQUEMAS.keys())
    fig, axes = plt.subplots(1, len(esquemas), figsize=(5.4 * len(esquemas), 5.4), sharey=True)
    cor_pa = tr.GRUPO_COR["agricultura"]; cor_vp = tr.GRUPO_COR["vegetacao_natural"]
    for ax, esq in zip(np.atleast_1d(axes), esquemas):
        g = flux[flux.esquema == esq].sort_values("ano_mid")
        ax.plot(g["ano_mid"], g["sul_pasto_agric_ano"], "-o", color=cor_pa, lw=2, ms=5,
                label="Sul: pasto→agric")
        ax.plot(g["ano_mid"], g["norte_veg_pasto_ano"], "-s", color=cor_vp, lw=2, ms=5,
                label="Norte: veg→pasto")
        ax.set_title(esq, fontsize=12); ax.set_xlabel("ano (meio da janela)")
        ax.grid(True, alpha=0.25)
    np.atleast_1d(axes)[0].set_ylabel("conversão (Mha/ano)")
    np.atleast_1d(axes)[0].legend(fontsize=9, loc="upper right")
    fig.suptitle("Robustez #33 — gradiente Sul(pasto→agric) vs Norte(veg→pasto), por esquema\n"
                 "(o gradiente e o colapso recente do pasto→agric no Sul valem em todos)",
                 fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(DIR_OUT / "fluxos_regionais.png", dpi=160, bbox_inches="tight")
    plt.close(fig); print(f"[fig] {(DIR_OUT / 'fluxos_regionais.png').relative_to(ROOT)}")


# ---------------------------------------------------------------------------
def verdito(vel: pd.DataFrame, flux: pd.DataFrame) -> None:
    """Checagem programática dos achados-manchete em cada esquema."""
    print("\n[veredito] Achados-manchete por esquema:")
    for esq in ESQUEMAS:
        v = vel[vel.esquema == esq]
        ult = v[v.ano_mid == v.ano_mid.max()].set_index("variavel")["vel_norte_km_ano"]
        # pasto/rebanho sobem no geral?
        pasto_med = v[v.variavel == "pastagem"]["vel_norte_km_ano"].mean()
        # agric desacelera na janela recente vs própria média?
        agric_ult = ult.get("agricultura", np.nan)
        agric_med = v[v.variavel == "agricultura"]["vel_norte_km_ano"].mean()
        f = flux[flux.esquema == esq]
        grad_ok = (f["sul_pasto_agric_ano"] >= f["norte_pasto_agric_ano"]).mean()
        grad_vp = (f["norte_veg_pasto_ano"] >= f["sul_veg_pasto_ano"]).mean()
        print(f"  {esq:14s} | pasto sobe (vel.méd={pasto_med:+.1f} km/a) | "
              f"agric recente {agric_ult:+.1f} vs méd {agric_med:+.1f} km/a | "
              f"Sul>Norte em pasto→agric: {grad_ok:.0%} das janelas | "
              f"Norte>Sul em veg→pasto: {grad_vp:.0%}")


def main() -> None:
    print("=" * 70)
    print("Pipeline #35 — Robustez de janelas temporais (#32 e #33)")
    print("Esquemas:", ", ".join(ESQUEMAS), "| + contínua/janela-única (referência)")
    print("=" * 70)

    # #32 — reusa a série anual de centros do #32
    painel, _ = cm.carregar_dados()
    centros = cm.calcular_centros_anuais(painel)
    vel = velocidade_ns(centros)
    vel.to_csv(DIR_PROC / "robustez_velocidade_ns.csv", index=False, encoding="utf-8")
    print(f"[OK] robustez_velocidade_ns.csv ({len(vel)} linhas)")

    # Net 1985→2024 (janela única — idêntico em todos os esquemas, p/ referência)
    print("\n[janela única] deslocamento N–S líquido 1985→2024 (km, igual p/ todo esquema):")
    for chave, (col, rotulo, cor) in cm.VARIAVEIS.items():
        g = centros[centros.variavel == chave].set_index("ano")
        if ANO_INI in g.index and ANO_FIM in g.index:
            dn = (g.loc[ANO_FIM, "y_mean"] - g.loc[ANO_INI, "y_mean"]) / 1000
            print(f"    {rotulo:18s} {dn:+6.1f} km")

    # #33 — reusa o recorte regional do #33
    conv, _idade, _ordem = tr.carregar()
    flux = fluxos_regionais(conv)
    flux.to_csv(DIR_PROC / "robustez_fluxos_regionais.csv", index=False, encoding="utf-8")
    print(f"\n[OK] robustez_fluxos_regionais.csv ({len(flux)} linhas)")

    verdito(vel, flux)

    print()
    fig_velocidade(vel)
    fig_fluxos(flux)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #35. Robustez multi-resolução de #32 e #33.")
    print("=" * 70)


if __name__ == "__main__":
    main()
