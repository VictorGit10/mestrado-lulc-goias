"""centro_massa_economico.py — Pipeline #50
Centro de massa das variáveis ECONÔMICAS e AGROINDUSTRIAIS (extensão do #32)
============================================================================

PERGUNTA QUE RESPONDE
---------------------
O #32/#43/#44 espacializaram o mundo FÍSICO (área LULC) e o rebanho. Falta pôr
na mesma régua de latitude o mundo do DINHEIRO, do VALOR e do PROCESSAMENTO —
as variáveis onde uma DIVERGÊNCIA da fronteira (e não a reconfirmação da marcha)
seria o achado. Três famílias, cada uma com uma pergunta que só o centroide
responde:

1. CRÉDITO RURAL (SICOR, 2013–2024).
   O eixo econômico (#37/#38: drive liderado por câmbio; #22: crédito→pasto)
   sempre foi medido no TEMPO, nunca no ESPAÇO. Pergunta: o dinheiro público
   SEGUE a fronteira ao norte, ou CONSOLIDA o núcleo ao sul? Custeio (capital
   de giro, produção estabelecida) e investimento (capex, abertura) podem
   divergir — investimento mais ao norte = crédito de fronteira.

2. VALOR (VA agropecuário 2002–2021; PIB total 2002–2023).
   Divergência VALOR × ÁREA. Se o centroide do valor fica ao SUL enquanto a
   área (pasto/soja) marcha ao norte, a leitura é "a fronteira exporta hectares
   ao norte, mas o valor se acumula no sul intensificado". É um ângulo espacial
   sobre o fio "crescimento sem desenvolvimento" (descartado por falta de IDH-M
   pós-2010) que NÃO precisa de IDH — usa o que já está no painel.

ABATE BOVINO — TESTADO E DESCARTADO (não é analisável com este dado).
   A hipótese era: o rebanho marchou ao norte, e o PROCESSAMENTO (abate/frigorífico)?
   Mas `abate_bovino_cab`/`_kg` no painel são ESTIMATIVA top-down:
   `abate_muni = (rebanho_muni / rebanho_UF) × abate_UF` (estimativa_abate_municipal.py),
   porque a Pesquisa Trimestral do Abate (SIDRA 1092–1094) só existe no nível UF.
   Verificado: dentro de cada ano, abate/rebanho tem std=0,0000 e corr(abate,rebanho)=1,0000
   → o centroide do abate é IDÊNTICO ao do rebanho POR CONSTRUÇÃO (vão 0,0 km). A
   comparação seria circular. A geografia real de abate exigiria o registro SIF/MAPA
   de estabelecimentos ou a geolocalização de frigoríficos do Trase — coleta à parte,
   fora deste pipeline. Por isso o abate NÃO entra abaixo.

ABORDAGEM
---------
Reusa cm.carregar_dados / cm.mean_center / cm.median_center /
cm.metros_para_lonlat do Pipeline #32 (centro_massa.py). Método, CRS (EPSG:5880)
e malha (166 AMCs) IDÊNTICOS — só muda o conjunto de variáveis. As âncoras de
ÁREA (pasto, agricultura, soja, rebanho) são recomputadas no mesmo passo, para
que as latitudes sejam comparáveis maçã-com-maçã (mesmo método, mesmos anos).

CAUTELAS (herdadas do #44/#32):
- Só variáveis EXTENSIVAS (R$, cabeças, kg) — centro de massa de razão/taxa não
  é interpretável. Todas aqui são extensivas.
- Análise DESCRITIVA. NÃO fazemos lead-lag entre latitudes de centroides:
  séries suaves integradas fabricam precedência espúria (D16, #42).
- JANELAS CURTAS: crédito começa em 2013; valor em 2002. A leitura de "marcha"
  de 40 anos NÃO se aplica a elas — para essas, o que interessa é a POSIÇÃO
  RELATIVA (o vão de latitude vs a fronteira) nos anos em que ambas existem,
  não o deslocamento líquido. O resumo reporta a janela própria de cada uma.
- TABULARES sem MAUP: crédito e abate são estatística municipal (como o rebanho),
  sem raster — herdam o caveat "sem validação pixel" do #43; a ponte de
  credibilidade é a validação soja raster×SIDRA do #44.

ENTRADAS
    data/processed/painel_amc_goias.parquet   (#25)
    data/processed/amc_goias.gpkg             (#25)

SAÍDAS
    data/processed/centro_massa_economico_anual.csv
    outputs/centro_massa/economico_credito.png    (SICOR vs fronteira)
    outputs/centro_massa/economico_valor.png       (VA agro/PIB vs área)

COMO RODAR
    py -3.14 scripts/centro_massa_economico.py
    py -3.14 scripts/centro_massa_economico.py --sem-figuras

Depende de: #32 (centro_massa.py, reuso de máquina) e #25 (painel + geometria).
Quando foi feito: 2026-07-16.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centro_massa as cm  # noqa: E402  — reuso integral da máquina do #32
from config_periodos import ATOS  # noqa: E402

ROOT    = Path(__file__).resolve().parent.parent
DIR_OUT = ROOT / "outputs" / "centro_massa"
DIR_OUT.mkdir(parents=True, exist_ok=True)
ARQ_ANUAL = ROOT / "data" / "processed" / "centro_massa_economico_anual.csv"
ARQ_BOOT  = ROOT / "data" / "processed" / "centro_massa_economico_bootstrap.csv"

# key -> (coluna no painel, rótulo, cor, grupo-de-figura)
VARS = {
    # --- âncoras de ÁREA / rebanho (do #32, p/ contexto de latitude) ---
    "agricultura": ("lulc_agricultura_ha", "Agricultura (área)",     "#c2185b", "valor"),
    "pastagem":    ("lulc_pastagem_ha",    "Pastagem (área)",        "#e8920c", "credito"),
    "soja_raster": ("lulc_soja_ha",        "Soja (área, raster)",    "#6a1b9a", "valor"),
    "bovinos":     ("pec_bovinos_cab",     "Rebanho bovino",         "#7a1f1f", "valor"),
    # --- 1. crédito rural (SICOR) ---
    "sicor_total":   ("sicor_total_real_rs",        "Crédito total (SICOR)", "#00695c", "credito"),
    "sicor_custeio": ("sicor_custeio_real_rs",      "Crédito — custeio",     "#26a69a", "credito"),
    "sicor_invest":  ("sicor_investimento_real_rs", "Crédito — investimento", "#004d40", "credito"),
    # --- 2. valor (VA agro, PIB) ---
    "va_agro": ("va_agro_real_rs", "VA agropecuário", "#1565c0", "valor"),
    "pib":     ("pib_real_rs",     "PIB total",       "#90a4ae", "valor"),
    # (abate bovino testado e descartado — derivado do rebanho por construção; ver docstring)
}

KM_POR_GRAU = 111.0  # aprox. p/ latitude em Goiás (converter Δlat° → km)


def calcular(painel: pd.DataFrame) -> pd.DataFrame:
    """Centro médio + mediano por (variável, ano). Idêntico ao #32/#44."""
    linhas = []
    for chave, (col, rotulo, _cor, _grp) in VARS.items():
        if col not in painel.columns:
            print(f"[aviso] coluna ausente: {col} ({chave}) — pulando")
            continue
        for ano, g in painel.groupby("ano"):
            sub = g[["cx", "cy", col]].dropna()
            sub = sub[sub[col] > 0]
            if len(sub) < 3:
                continue
            x, y, w = sub["cx"].to_numpy(), sub["cy"].to_numpy(), sub[col].to_numpy(float)
            mx, my = cm.mean_center(x, y, w)
            dx, dy = cm.median_center(x, y, w)
            linhas.append({"variavel": chave, "rotulo": rotulo, "ano": int(ano),
                           "x_mean": mx, "y_mean": my, "x_med": dx, "y_med": dy,
                           "n_amc": int(len(sub))})
    df = pd.DataFrame(linhas)
    ll_mean = cm.metros_para_lonlat(df[["x_mean", "y_mean"]].to_numpy())
    ll_med = cm.metros_para_lonlat(df[["x_med", "y_med"]].to_numpy())
    df["lat_mean"], df["lat_med"] = ll_mean[:, 1], ll_med[:, 1]
    df["lon_mean"] = ll_mean[:, 0]
    return df.sort_values(["variavel", "ano"]).reset_index(drop=True)


def resumo(df: pd.DataFrame) -> pd.DataFrame:
    """ΔN líquido (km) na janela PRÓPRIA de cada variável + latitude nos extremos."""
    out = []
    for chave, (col, rotulo, _c, _g) in VARS.items():
        g = df[df.variavel == chave].set_index("ano")
        if g.empty:
            continue
        a0, a1 = g.index.min(), g.index.max()
        dn = (g.loc[a1, "y_mean"] - g.loc[a0, "y_mean"]) / 1000
        dn_med = (g.loc[a1, "y_med"] - g.loc[a0, "y_med"]) / 1000
        out.append({"variavel": chave, "rotulo": rotulo, "grupo": _g,
                    "ano_ini": int(a0), "ano_fim": int(a1),
                    "lat_ini": g.loc[a0, "lat_mean"], "lat_fim": g.loc[a1, "lat_mean"],
                    "dN_km_mean": dn, "dN_km_med": dn_med})
    return pd.DataFrame(out)


def gap_lat(df: pd.DataFrame, key_a: str, key_b: str) -> tuple[float, list]:
    """Vão de latitude (km) key_a − key_b nos anos em comum (+ = A ao norte de B).
    Retorna (vão médio em km, [(ano, gap_km) em anos-marco])."""
    a = df[df.variavel == key_a].set_index("ano")["lat_mean"]
    b = df[df.variavel == key_b].set_index("ano")["lat_mean"]
    comum = a.index.intersection(b.index)
    if len(comum) == 0:
        return float("nan"), []
    gap_medio = float((a.loc[comum] - b.loc[comum]).mean()) * KM_POR_GRAU
    marcos = [ano for ano in (comum.min(), comum.max()) ]
    detalhe = [(int(ano), float(a.loc[ano] - b.loc[ano]) * KM_POR_GRAU) for ano in marcos]
    return gap_medio, detalhe


# ---------------------------------------------------------------------------
# Figuras (mesmo estilo do #44: bandas de ato, latitude × ano)
# ---------------------------------------------------------------------------

def _fundo_atos(ax):
    from config_periodos import CORES_ATO
    for ato, info in ATOS.items():
        ax.axvspan(info["inicio"] - 0.5, info["fim"] + 0.5,
                   color=CORES_ATO.get(ato, "0.5"), alpha=0.06, zorder=0)
        ax.text((info["inicio"] + info["fim"]) / 2, 0.99, f"Ato {ato}",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=8.5, color="0.45")


def fig_grupo(df: pd.DataFrame, titulo: str, arquivo: str,
              chaves: list[str], tracejadas: tuple[str, ...] = (),
              banda: pd.DataFrame | None = None) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 6))
    _fundo_atos(ax)
    for chave in chaves:
        col, rotulo, cor, _g = VARS[chave]
        g = df[df.variavel == chave].sort_values("ano")
        if g.empty:
            continue
        # Faixa IC95% (bootstrap) só das variáveis-alvo (não das âncoras tracejadas).
        if banda is not None and chave not in tracejadas:
            b = banda[banda.variavel == chave].sort_values("ano")
            if not b.empty:
                ax.fill_between(b["ano"], b["lat_lo"], b["lat_hi"],
                                color=cor, alpha=0.13, lw=0, zorder=1)
        estilo = "--" if chave in tracejadas else "-"
        lw = 1.4 if chave in tracejadas else 2.1
        ax.plot(g["ano"], g["lat_mean"], estilo, color=cor, lw=lw,
                label=rotulo, zorder=3)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Latitude do centro de massa (°, ↑ = mais ao norte)")
    ax.set_title(titulo, fontsize=12, loc="left")
    ax.legend(loc="best", frameon=True, fontsize=8.5, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(DIR_OUT / arquivo, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {(DIR_OUT / arquivo).relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline #50 — centro de massa econômico/agroindustrial")
    ap.add_argument("--sem-figuras", action="store_true")
    ap.add_argument("--sem-bootstrap", action="store_true", help="pula o IC por bootstrap")
    args = ap.parse_args()

    print("=" * 70)
    print("Pipeline #50 — Centro de massa: crédito, valor e abate (extensão #32)")
    print("=" * 70)

    painel, _ = cm.carregar_dados()  # reuso: cx/cy idênticos ao #32
    df = calcular(painel)
    df.to_csv(ARQ_ANUAL, index=False, encoding="utf-8")
    print(f"[OK] {ARQ_ANUAL.relative_to(ROOT)} ({len(df)} linhas)\n")

    res = resumo(df)
    print("[resumo] Deslocamento N–S líquido na janela PRÓPRIA (km; + = norte):")
    print("-" * 70)
    for _, r in res.sort_values("dN_km_mean").iterrows():
        seta = "↑N" if r["dN_km_mean"] > 0 else "↓S"
        print(f"  {r['rotulo']:26s} ΔN {r['dN_km_mean']:+6.1f} km {seta} "
              f"(med {r['dN_km_med']:+6.1f}) | lat {r['lat_ini']:.2f}→{r['lat_fim']:.2f} "
              f"| {r['ano_ini']}–{r['ano_fim']}")

    # --- 1. CRÉDITO: segue a fronteira ou consolida o núcleo? --------------
    print("\n[1. CRÉDITO vs fronteira] vão de latitude (km; + = crédito ao NORTE do pasto):")
    for chave in ("sicor_total", "sicor_custeio", "sicor_invest"):
        gm, det = gap_lat(df, chave, "pastagem")
        marca = "  ".join(f"{ano}:{g:+.0f}" for ano, g in det)
        print(f"  {VARS[chave][1]:24s} vs Pastagem: médio {gm:+6.1f} km | {marca}")
    gm_ci, _ = gap_lat(df, "sicor_custeio", "sicor_invest")
    print(f"  → investimento − custeio: {-gm_ci:+.1f} km "
          f"({'investimento mais ao NORTE' if -gm_ci > 0 else 'custeio mais ao NORTE'})")

    # --- 2. VALOR vs ÁREA: onde está o valor vs onde está a terra? ---------
    print("\n[2. VALOR vs área] vão de latitude (km; + = valor ao NORTE da área):")
    for chave_val in ("va_agro", "pib"):
        for chave_area in ("agricultura", "pastagem"):
            gm, det = gap_lat(df, chave_val, chave_area)
            marca = "  ".join(f"{ano}:{g:+.0f}" for ano, g in det)
            print(f"  {VARS[chave_val][1]:18s} vs {VARS[chave_area][1]:18s}: "
                  f"médio {gm:+6.1f} km | {marca}")

    # --- Incerteza por bootstrap de AMCs (IC95% do ΔNorte + banda de latitude) ---
    banda = None
    if not args.sem_bootstrap:
        col_por_chave = {k: v[0] for k, v in VARS.items()}
        rotulos = {k: v[1] for k, v in VARS.items()}
        banda, desloc_ic = cm.bootstrap_incerteza(painel, col_por_chave, rotulos)
        desloc_ic.to_csv(ARQ_BOOT, index=False, encoding="utf-8")
        print(f"\n[incerteza] IC95% do ΔNorte por bootstrap de AMCs (B={cm.BOOT_B}); "
              f"LÍQUIDO na janela própria:")
        liq_ic = desloc_ic[desloc_ic.janela == "LÍQUIDO"]
        for chave in ("sicor_total", "sicor_custeio", "sicor_invest", "va_agro", "pib"):
            r = liq_ic[liq_ic.variavel == chave]
            if r.empty:
                continue
            r = r.iloc[0]
            marca = "≠0 robusto" if r["exclui_zero"] else "INCLUI 0 (dentro do ruído)"
            print(f"  {r['rotulo']:24s} ΔN {r['dN_km']:+6.1f} km "
                  f"| IC95% [{r['dN_lo']:+6.1f}, {r['dN_hi']:+6.1f}] "
                  f"| {int(r['ano_ini'])}–{int(r['ano_fim'])} | {marca}")
        print(f"[OK] {ARQ_BOOT.relative_to(ROOT)} ({len(desloc_ic)} linhas)")

    if not args.sem_figuras:
        print()
        fig_grupo(df,
                  "Crédito rural (SICOR) vs a fronteira — centro de massa, Goiás 2013–2024\n"
                  "o dinheiro público segue o pasto ao norte, ou consolida o núcleo ao sul?",
                  "economico_credito.png",
                  ["pastagem", "agricultura", "sicor_total", "sicor_custeio", "sicor_invest"],
                  tracejadas=("pastagem", "agricultura"), banda=banda)
        fig_grupo(df,
                  "Valor (VA agro, PIB) vs área — centro de massa, Goiás\n"
                  "se o valor fica ao SUL da área, a fronteira exporta hectares e o valor fica no núcleo",
                  "economico_valor.png",
                  ["pastagem", "agricultura", "soja_raster", "bovinos", "va_agro", "pib"],
                  tracejadas=("pastagem", "agricultura", "soja_raster", "bovinos"), banda=banda)

    print("\n" + "=" * 70)
    print("CONCLUÍDO — Pipeline #50 (extensão econômica/agroindustrial do #32).")
    print("=" * 70)


if __name__ == "__main__":
    main()
