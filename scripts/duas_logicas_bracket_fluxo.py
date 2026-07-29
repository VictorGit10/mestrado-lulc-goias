"""
duas_logicas_bracket_fluxo.py — o fio que ficou aberto no #40: crédito e estrutura
sob a régua da união (fecha a última pendência da D26 no #40)
=================================================================================

O QUE FICOU EM ABERTO
---------------------
A D26 (bracket do Mosaico) foi aplicada ao **gradiente latitudinal** do #40 em
23/jul/2026 (`duas_logicas_bracket_evento.py`) e o derrubou: sob
`pasto→(agric∪mosaico)` o ρ vai a ~zero nas três janelas. Mas o #40 tem um
**segundo** conjunto de resultados que nunca passou pela mesma régua:

  • **estrutura** — plantio direto × idade mediana municipal (veredito: *não
    estabelecido*, p≈0,058 sob controle 2D, 0/8 sobrevivem a FDR-BH);
  • **fluxo** — Δ SICOR × idade mediana municipal (r=+0,22, p=0,0009, **o único
    par do pipeline que sobrevive a FDR-BH**), com o alerta de que o sinal é o
    **oposto** do esperado: mais crédito → pasto convertido mais VELHO.

Os dois medem a idade sobre o mesmo subconjunto selecionado pela mudança de rótulo
que derrubou o gradiente. Enquanto não passarem pela união, o único achado
"robusto" do #40 está apoiado numa régua que já falhou noutro teste do mesmo
pipeline. É o que este script fecha.

MÉTODO — idêntico ao do #40, trocando só a definição de evento
--------------------------------------------------------------
Reusa `duas_logicas_bracket_evento.preparar` (schema do #40) e
`duas_logicas_pastagem.agregar_mix` (mesma regra de agregação, mesmo filtro de
confiabilidade). Para cada régua × janela:

  - r bruto, parcial | latitude, parcial | latitude+longitude (D14: o gradiente
    de aptidão é confundidor de 1ª ordem; e os DOIS lados da comparação
    estrutura×fluxo recebem o MESMO controle, que é o corolário da D14)
  - FDR-BH sobre todos os pares do bloco, por régua e janela

O desfecho é sempre `idade_mediana` municipal, como no #40.

SAÍDA
    data/processed/duas_logicas_bracket_fluxo.csv

COMO RODAR
    python scripts/duas_logicas_bracket_fluxo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duas_logicas_pastagem as duas                      # noqa: E402
from duas_logicas_bracket_evento import preparar          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAINEL = ROOT / "data" / "processed" / "painel_unificado.parquet"
ARQ_OUT = ROOT / "data" / "processed" / "duas_logicas_bracket_fluxo.csv"

REGUAS = {"agric": {"agricultura"}, "uniao": {"agricultura", "mosaico"}}
JANELAS = {"limpa 2010-2019": (2010, 2019), "cheia 2010-2024": (2010, 2024),
           "exposta 2016-2024": (2016, 2024)}
MIN_PX_MUNI = 20          # mesmo filtro do #40


def fluxo_municipal(a: int, b: int) -> pd.DataFrame:
    """Nível médio e Δ médio de SICOR e VA agro na janela — definição do #40."""
    p = pd.read_parquet(PAINEL).sort_values(["cd_mun", "ano"])
    sub = p[(p["ano"] >= a) & (p["ano"] <= b)].copy()
    out = None
    for col in ["sicor_total_real_rs", "va_agro_real_rs"]:
        if col not in sub.columns:
            continue
        sub["_d"] = sub.groupby("cd_mun")[col].diff()
        agg = (sub.groupby("cd_mun")
               .agg(**{f"{col}__nivel": (col, "mean"), f"{col}__dmed": ("_d", "mean")})
               .reset_index())
        agg["cd_mun"] = agg["cd_mun"].astype("int64")
        out = agg if out is None else out.merge(agg, on="cd_mun", how="outer")
    return out


def fdr_bh(ps: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg: devolve o vetor booleano de rejeições ao nível q."""
    ps = np.asarray(ps, float)
    ok = ~np.isnan(ps)
    rej = np.zeros(len(ps), bool)
    idx = np.where(ok)[0]
    if not len(idx):
        return rej
    ordem = idx[np.argsort(ps[idx])]
    m = len(ordem)
    limiar = q * (np.arange(1, m + 1) / m)
    passou = ps[ordem] <= limiar
    if passou.any():
        corte = np.max(np.where(passou)[0])
        rej[ordem[:corte + 1]] = True
    return rej


def bloco(regua: str, janela_nome: str, jan: tuple[int, int],
          nt: pd.DataFrame) -> pd.DataFrame:
    a, b = jan
    df = preparar(REGUAS[regua])
    mix = duas.agregar_mix(df, "cd_mun", jan, MIN_PX_MUNI)
    mix = mix[mix["confiavel"]].copy()
    mix["cd_mun"] = mix["cd_mun"].astype("int64")
    m = mix.merge(nt, on="cd_mun", how="left").merge(
        fluxo_municipal(a, b), on="cd_mun", how="left")

    pares = [("pct_pd_area", "estrutura · plantio direto (% área estab.)"),
             ("sicor_total_real_rs__dmed", "fluxo · Δ SICOR"),
             ("sicor_total_real_rs__nivel", "fluxo · SICOR (nível)"),
             ("va_agro_real_rs__dmed", "fluxo · Δ VA agro"),
             ("va_agro_real_rs__nivel", "fluxo · VA agro (nível)")]

    linhas = []
    for col, rot in pares:
        if col not in m.columns:
            continue
        s = m.dropna(subset=[col, "idade_mediana", "lat_centroide", "lon_centroide"])
        if len(s) < 20:
            continue
        rb, pb = pearsonr(s[col], s["idade_mediana"])
        rl, pl, _ = duas._partial_corr(col, "idade_mediana", "lat_centroide", s)
        r2, p2, n = duas._partial_corr_multi(
            col, "idade_mediana", ["lat_centroide", "lon_centroide"], s)
        linhas.append({
            "regua": regua, "janela": janela_nome, "variavel": rot, "n": n,
            "r_bruto": round(rb, 4), "p_bruto": round(pb, 5),
            "r_parcial_lat": round(rl, 4), "p_parcial_lat": round(pl, 5),
            "r_parcial_latlon": round(r2, 4), "p_parcial_latlon": round(p2, 5),
        })
    t = pd.DataFrame(linhas)
    if not t.empty:
        t["sobrevive_fdr"] = fdr_bh(t["p_parcial_latlon"].to_numpy())
    return t


def main() -> None:
    nt = duas.carregar_plantio_direto()
    partes = []
    for regua in REGUAS:
        for nome, jan in JANELAS.items():
            print(f"  {regua:<6} · {nome} ...")
            partes.append(bloco(regua, nome, jan, nt))
    tab = pd.concat(partes, ignore_index=True)
    tab.to_csv(ARQ_OUT, index=False, encoding="utf-8")

    pd.set_option("display.width", 200, "display.max_columns", 30)
    for nome in JANELAS:
        print(f"\n{'=' * 108}\nJANELA: {nome}\n{'=' * 108}")
        s = tab[tab["janela"] == nome]
        print(s[["regua", "variavel", "n", "r_bruto", "r_parcial_lat",
                 "r_parcial_latlon", "p_parcial_latlon", "sobrevive_fdr"]]
              .to_string(index=False))

    print(f"\n[OK] {ARQ_OUT.relative_to(ROOT)}")

    # Leitura direta do que estava em aberto.
    print("\n--- O par que o #40 dava como robusto (Δ SICOR × idade) ---")
    s = tab[tab["variavel"].str.contains("SICOR") & tab["variavel"].str.contains("Δ")]
    for _, r in s.iterrows():
        marca = "sobrevive FDR" if r["sobrevive_fdr"] else "NÃO sobrevive FDR"
        print(f"  {r['regua']:<6} {r['janela']:<18} n={r['n']:<4} "
              f"r|lat+lon = {r['r_parcial_latlon']:+.3f}  p={r['p_parcial_latlon']:.4f}  {marca}")


if __name__ == "__main__":
    main()
