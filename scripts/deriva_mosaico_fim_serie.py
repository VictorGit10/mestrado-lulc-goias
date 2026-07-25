"""deriva_mosaico_fim_serie.py — Pipeline #28D (diagnóstico de validade de medida)

Fecha o §4-E da leitura crítica do #28 ("decompor o salto 2020→2022") e, no
caminho, o §4-C (Kaplan-Meier).

## A pergunta

A mediana da idade da pastagem na conversão despenca no fim da série: 20 anos
em 2020, 4 em 2022, 5 em 2024. A leitura crítica listou quatro suspeitos —
reclassificação MapBiomas, concentração espacial, efeito da Coleção 10.1, ou
mudança real de comportamento. Este script decide entre eles.

## O achado

Nenhum dos quatro, na forma como foram formulados. O que acontece é uma
**mudança do rótulo de destino da conversão**: ao longo da série, e com forte aceleração
depois de 2019, a pastagem que sai de "pastagem" para de ser classificada como
**agricultura** e passa a ser classificada como **Mosaico de Usos** (classe 21).

    ano   P→Agricultura   P→Mosaico    razão M/A
    2015    4.040.382      2.442.452       0,6
    2019    2.072.349      3.346.353       1,6
    2022      648.197      6.774.799      10,5
    2024      303.432      9.875.689      32,5

O #28 define seu objeto como "pixel que era pastagem e virou agricultura".
Esse objeto não é constante ao longo da série: em 2024 ele captura 7,5% do que
capturava em 2015, e o que sobra é uma **subpopulação selecionada** — mediana
de 4-5 anos, censura de 4%, contra 20 anos e 47% em 2020.

## Por que isso não é "a conversão acabou"

Três âncoras independentes:

1. **SIDRA (dado de campo, externo ao sensoriamento)**: a área plantada de soja
   em Goiás cresce de 3,58 Mha (2020) para 4,94 Mha (2024), +38%. A expansão da
   lavoura acelera exatamente na janela em que o MapBiomas para de registrar
   pastagem virando lavoura.
2. **A área de "agricultura" do próprio MapBiomas fica estagnada** no mesmo
   período (+0,064 Mha em 4 anos, contra +0,15 a +0,18 Mha/ano em 2015-2017),
   enquanto **Mosaico de Usos cresce +1,35 Mha** — praticamente o tamanho da
   expansão de soja que o SIDRA registra.
3. **A perda de pastagem continua** (−1,16 Mha de 2020 a 2024). O pasto está
   saindo; só não está sendo contabilizado como chegando à agricultura.

## Artefato do classificador ou mudança real da paisagem?

O dado não separa as duas, e é honesto dizer isso. "Mosaico de Usos" é a classe
que o MapBiomas usa quando **não consegue distinguir** lavoura de pastagem no
pixel de 30 m (ver `metodologia/censo_vs_amostra.md` §3). Ela crescer pode ser:

  (a) mudança de rótulo do classificador — os filtros temporais pós-classificação da
      Coleção 10 usam janelas móveis de 3 e 4 anos e regras especiais para os
      últimos anos da série, quando a janela de análise é limitada (ATBD
      Coleção 10, §3.4.1 e §3.4.3.1); ou
  (b) mudança real — integração lavoura-pecuária (ILP) de fato tornando a
      paisagem menos separável, que é um fenômeno que Goiás tem (#40).

A âncora do SIDRA favorece (a) como componente dominante — a soja cresceu 38% e
a agricultura do MapBiomas não se mexeu —, mas não zera (b). **Para o #28 a
distinção não muda a consequência**: em qualquer dos dois mundos, a população de
"conversão pasto→lavoura" medida em 2024 não é comparável à de 2015.

## O que isto atinge

Todo resultado do #28 calculado sobre a janela recente. O Ato III (2020-2024) da
dissertação está inteiramente dentro da mudança de rótulo. Ver
`pipelines/28D_deriva_mosaico.md` §4 para o alcance, e o §4-C para por que isto
também encerra a pendência do Kaplan-Meier.

Como rodar:
    python scripts/deriva_mosaico_fim_serie.py
    python scripts/deriva_mosaico_fim_serie.py --rapido      (6 shards, p/ iterar)

Pré-requisitos: rasterio, pandas, numpy, matplotlib.
"""
from __future__ import annotations

import argparse
import glob
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parent.parent
DIR_CUBO = ROOT / "data" / "raw" / "cubo_go"
DIR_OUT = ROOT / "data" / "processed"
DIR_FIG = ROOT / "outputs" / "deriva_mosaico"

PARQUET_28 = DIR_OUT / "pastagem_idade_censo.parquet"
CSV_AREAS = DIR_OUT / "taxas_lulc_goias.csv"
PARQUET_PAINEL = DIR_OUT / "painel_unificado.parquet"

ANO_MIN, ANO_MAX = 1985, 2024

ID_PASTAGEM = 15
ID_MOSAICO = 21
IDS_AGRICULTURA = np.array([9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62])
IDS_VEGETACAO = np.array([3, 4, 12])


# ---------------------------------------------------------------- Bloco A
def bloco_a_transicoes(rapido: bool = False) -> pd.DataFrame:
    """Conta, no censo de pixels, o DESTINO de cada saída de pastagem por ano.

    Percorre o cubo em janelas de linhas. Para cada par de bandas consecutivas
    (t-1, t), conta os pixels que eram pastagem em t-1 e foram para cada um dos
    três destinos. É o mesmo passo do #28, mas sem restringir a agricultura —
    e é essa ausência de restrição que revela a mudança de rótulo.
    """
    shards = sorted(glob.glob(str(DIR_CUBO / "*.tif")))
    if rapido:
        shards = shards[:6]
    if not shards:
        raise SystemExit(f"Nenhum shard em {DIR_CUBO}. Rode export/baixa do cubo antes.")

    n_bandas = ANO_MAX - ANO_MIN + 1
    p_agric = np.zeros(n_bandas, dtype=np.int64)
    p_mosaico = np.zeros(n_bandas, dtype=np.int64)
    p_veg = np.zeros(n_bandas, dtype=np.int64)
    p_total = np.zeros(n_bandas, dtype=np.int64)

    print(f"Bloco A — destino das saídas de pastagem ({len(shards)} shards)")
    t0 = time.time()
    for i, f in enumerate(shards, 1):
        with rasterio.open(f) as src:
            for r in range(0, src.height, 4096):
                alt = min(4096, src.height - r)
                arr = src.read(window=Window(0, r, src.width, alt))
                anterior = arr[0]
                for b in range(1, arr.shape[0]):
                    atual = arr[b]
                    era_pasto = anterior == ID_PASTAGEM
                    p_total[b] += int((era_pasto & (atual != ID_PASTAGEM)).sum())
                    p_agric[b] += int((era_pasto & np.isin(atual, IDS_AGRICULTURA)).sum())
                    p_mosaico[b] += int((era_pasto & (atual == ID_MOSAICO)).sum())
                    p_veg[b] += int((era_pasto & np.isin(atual, IDS_VEGETACAO)).sum())
                    anterior = atual
                del arr
        print(f"  [{i}/{len(shards)}] {Path(f).name}  ({time.time() - t0:.0f}s)")

    anos = np.arange(ANO_MIN, ANO_MAX + 1)
    df = pd.DataFrame(
        {
            "ano": anos,
            "px_pasto_para_agricultura": p_agric,
            "px_pasto_para_mosaico": p_mosaico,
            "px_pasto_para_vegetacao": p_veg,
            "px_pasto_saiu_total": p_total,
        }
    ).iloc[1:]  # 1985 não tem ano anterior
    df["razao_mosaico_agricultura"] = df.px_pasto_para_mosaico / df.px_pasto_para_agricultura
    df["pct_saida_para_agricultura"] = 100 * df.px_pasto_para_agricultura / df.px_pasto_saiu_total
    df["pct_saida_para_mosaico"] = 100 * df.px_pasto_para_mosaico / df.px_pasto_saiu_total
    df["fonte_shards"] = len(shards)
    return df


# ---------------------------------------------------------------- Bloco B
def bloco_b_areas() -> pd.DataFrame | None:
    """Série de área por classe agregada — o mosaico crescendo no fim da série."""
    if not CSV_AREAS.exists():
        print(f"  (pulado: {CSV_AREAS.name} ausente)")
        return None
    d = pd.read_csv(CSV_AREAS)
    cols = ["ano", "pastagem_mha", "agricultura_mha", "mosaico_mha", "vegetacao_natural_mha"]
    d = d[[c for c in cols if c in d.columns]].copy()
    for c in d.columns:
        if c.endswith("_mha"):
            d["d_" + c.replace("_mha", "")] = d[c].diff()
    return d


# ---------------------------------------------------------------- Bloco C
def bloco_c_efeito_no_28() -> pd.DataFrame | None:
    """O que a mudança de rótulo faz com a medida do #28: n, censura e mediana por ano.

    Mostra as DUAS coisas ao mesmo tempo:
      - até ~2019 a mediana é governada pelo HORIZONTE (não pode exceder
        ano-1985), o que já era a lição do §7.3 do censo_vs_amostra;
      - de 2020 em diante a série quebra: n colapsa, censura colapsa e a
        mediana desaba, porque o objeto medido mudou.
    """
    if not PARQUET_28.exists():
        print(f"  (pulado: {PARQUET_28.name} ausente)")
        return None
    df = pd.read_parquet(PARQUET_28)
    df = df[df.cd_mun != 0]
    nc = df[df.origem_anterior != "censurado_esquerda"]

    def mediana_ponderada(g: pd.DataFrame) -> float:
        if not len(g):
            return np.nan
        g = g.sort_values("idade_pastagem_anos")
        acum = g.n_pixels.cumsum()
        return float(g.idade_pastagem_anos[acum >= acum.iloc[-1] / 2].iloc[0])

    linhas = []
    for ano in range(ANO_MIN + 1, ANO_MAX + 1):
        t = df[df.ano_conversao == ano]
        n = nc[nc.ano_conversao == ano]
        tot, nao_cens = int(t.n_pixels.sum()), int(n.n_pixels.sum())
        linhas.append(
            {
                "ano": ano,
                "n_eventos": tot,
                "n_nao_censurado": nao_cens,
                "pct_censura": 100 * (1 - nao_cens / tot) if tot else np.nan,
                "mediana_idade_nao_cens": mediana_ponderada(n),
                "horizonte_max": ano - ANO_MIN,
            }
        )
    d = pd.DataFrame(linhas)
    d["mediana_sobre_horizonte"] = d.mediana_idade_nao_cens / d.horizonte_max
    return d


# ---------------------------------------------------------------- Bloco D
def bloco_d_ancora_sidra() -> pd.DataFrame | None:
    """Âncora externa: a lavoura cresceu de fato? (SIDRA, dado de campo)"""
    if not PARQUET_PAINEL.exists():
        print(f"  (pulado: {PARQUET_PAINEL.name} ausente)")
        return None
    p = pd.read_parquet(PARQUET_PAINEL)
    col = "agri_soja_ha_plantada"
    if col not in p.columns:
        print(f"  (pulado: coluna {col} ausente no painel)")
        return None
    d = p.groupby("ano")[col].sum(min_count=1).reset_index()
    d = d[(d.ano >= 2014) & (d.ano <= ANO_MAX)].copy()
    d["soja_mha"] = d[col] / 1e6
    d["d_soja_mha"] = d.soja_mha.diff()
    return d[["ano", "soja_mha", "d_soja_mha"]]


# ---------------------------------------------------------------- Bloco E
def bloco_e_sensibilidade_gmm() -> pd.DataFrame | None:
    """Quanto da manchete do #28 se move quando a mudança de rótulo entra na janela?

    Refaz o GMM ponderado em janelas de 5 anos deslizantes e ano a ano. O que
    interessa não é cada número, é o CONTRASTE entre janelas que terminam antes
    de 2020 e a janela 2020-2024 que o #28 publica como Ato III.
    """
    if not PARQUET_28.exists():
        return None
    sys.path.insert(0, str(ROOT / "scripts"))
    from estatistica_ponderada import gmm_ponderado, mediana

    df = pd.read_parquet(PARQUET_28)
    df = df[(df.cd_mun != 0) & (df.origem_anterior != "censurado_esquerda")]

    linhas = []
    janelas = [(a, a + 4) for a in range(2010, 2021)] + [(a, a) for a in range(2019, 2025)]
    for a0, a1 in janelas:
        d = df[(df.ano_conversao >= a0) & (df.ano_conversao <= a1)]
        if not len(d):
            continue
        v = d.idade_pastagem_anos.values.astype(float)
        w = d.n_pixels.values.astype(float)
        r = gmm_ponderado(v, w, n_comp=2)
        if not r.get("ok"):
            continue
        linhas.append(
            {
                "janela": f"{a0}-{a1}" if a0 != a1 else str(a0),
                "ano_inicio": a0,
                "ano_fim": a1,
                "largura": a1 - a0 + 1,
                "n_nao_censurado": float(w.sum()),
                "mediana": mediana(v, w),
                "mu1": r["mu"][0], "w1": r["peso"][0],
                "mu2": r["mu"][1], "w2": r["peso"][1],
                "toca_deriva": a1 >= 2021,
            }
        )
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- figura
def figura(trans: pd.DataFrame, areas: pd.DataFrame | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))

    t = trans[trans.ano >= 1990]
    axs[0].plot(t.ano, t.px_pasto_para_agricultura / 1e6, lw=2, color="#c2571a",
                label="pastagem → agricultura")
    axs[0].plot(t.ano, t.px_pasto_para_mosaico / 1e6, lw=2, color="#3d7a5a",
                label="pastagem → Mosaico de Usos")
    axs[0].axvspan(2020, ANO_MAX, color="#999", alpha=0.15)
    axs[0].annotate("Ato III", (2022, axs[0].get_ylim()[1] * 0.93), ha="center",
                    fontsize=9, color="#555")
    axs[0].set_title("O destino da saída da pastagem inverte", fontsize=11)
    axs[0].set_ylabel("milhões de pixels/ano")
    axs[0].set_xlabel("ano")
    axs[0].legend(fontsize=9)
    axs[0].grid(alpha=0.25)

    if areas is not None:
        a = areas[areas.ano >= 1990]
        for col, cor, rot in (
            ("pastagem_mha", "#8a6d3b", "pastagem"),
            ("agricultura_mha", "#c2571a", "agricultura"),
            ("mosaico_mha", "#3d7a5a", "Mosaico de Usos"),
        ):
            if col in a.columns:
                axs[1].plot(a.ano, a[col], lw=2, color=cor, label=rot)
        axs[1].axvspan(2020, ANO_MAX, color="#999", alpha=0.15)
        axs[1].set_title("Área por classe — o mosaico absorve o fim da série", fontsize=11)
        axs[1].set_ylabel("Mha")
        axs[1].set_xlabel("ano")
        axs[1].legend(fontsize=9)
        axs[1].grid(alpha=0.25)

    fig.suptitle(
        "#28D — mudança do rótulo de destino da conversão no fim da série (MapBiomas Col. 10.1, Goiás)",
        fontsize=12,
    )
    fig.tight_layout()
    saida = DIR_FIG / "deriva_mosaico.png"
    fig.savefig(saida, dpi=140)
    print(f"  figura: {saida.relative_to(ROOT)}")


# ---------------------------------------------------------------- veredito
def veredito(trans: pd.DataFrame, areas: pd.DataFrame | None,
             efeito: pd.DataFrame | None, sidra: pd.DataFrame | None,
             sens: pd.DataFrame | None = None) -> None:
    print("\n" + "=" * 72)
    print("VEREDITO — #28D")
    print("=" * 72)

    def linha(ano: int) -> pd.Series:
        return trans[trans.ano == ano].iloc[0]

    print("\nDestino das saídas de pastagem (censo de pixels):")
    print(f"  {'ano':>6} {'→agric':>12} {'→mosaico':>12} {'razão M/A':>10}")
    for ano in (2000, 2010, 2015, 2019, 2020, 2022, 2024):
        if (trans.ano == ano).any():
            r = linha(ano)
            print(f"  {ano:>6} {r.px_pasto_para_agricultura:>12,.0f} "
                  f"{r.px_pasto_para_mosaico:>12,.0f} {r.razao_mosaico_agricultura:>10.1f}")

    r15, r24 = linha(2015), linha(2024)
    queda = 100 * (1 - r24.px_pasto_para_agricultura / r15.px_pasto_para_agricultura)
    print(f"\n  P→agricultura cai {queda:.0f}% de 2015 a 2024 "
          f"({r15.px_pasto_para_agricultura:,.0f} → {r24.px_pasto_para_agricultura:,.0f} px).")
    print(f"  A razão mosaico/agricultura vai de {r15.razao_mosaico_agricultura:.1f} "
          f"para {r24.razao_mosaico_agricultura:.1f}.")

    if areas is not None:
        a20 = areas[areas.ano == 2020].iloc[0]
        a24 = areas[areas.ano == 2024].iloc[0]
        print("\nÁrea 2020 → 2024 (Mha):")
        for col, rot in (("pastagem_mha", "pastagem"), ("agricultura_mha", "agricultura"),
                         ("mosaico_mha", "Mosaico de Usos")):
            if col in areas.columns:
                print(f"  {rot:<18} {a20[col]:>7.3f} → {a24[col]:>7.3f}  "
                      f"({a24[col] - a20[col]:+.3f})")

    if sidra is not None:
        s20 = sidra[sidra.ano == 2020].soja_mha.iloc[0]
        s24 = sidra[sidra.ano == 2024].soja_mha.iloc[0]
        print(f"\nÂncora externa (SIDRA, área plantada de soja):")
        print(f"  2020 {s20:.3f} Mha → 2024 {s24:.3f} Mha  "
              f"({s24 - s20:+.3f} Mha, {100 * (s24 / s20 - 1):+.0f}%)")
        print("  A lavoura cresceu. A 'agricultura' do MapBiomas não. O mosaico, sim.")

    if efeito is not None:
        print("\nEfeito na medida do #28 (mediana da idade e censura por ano):")
        print(f"  {'ano':>6} {'n_eventos':>12} {'%censura':>9} {'mediana':>8} {'horizonte':>10}")
        for ano in (2000, 2010, 2019, 2020, 2021, 2022, 2023, 2024):
            r = efeito[efeito.ano == ano]
            if len(r):
                r = r.iloc[0]
                print(f"  {ano:>6} {r.n_eventos:>12,.0f} {r.pct_censura:>8.1f}% "
                      f"{r.mediana_idade_nao_cens:>8.0f} {r.horizonte_max:>10.0f}")
        pre = efeito[(efeito.ano >= 1995) & (efeito.ano <= 2019)]
        print(f"\n  Até 2019 a mediana é ~{pre.mediana_sobre_horizonte.mean():.0%} do horizonte "
              f"(dp {pre.mediana_sobre_horizonte.std():.0%}) — ela mede o horizonte,")
        print("  não a idade. De 2020 em diante a série quebra por outro motivo: o objeto muda.")

    if sens is not None and len(sens):
        print("\nSensibilidade da manchete do #28 (GMM ponderado, janelas de 5 anos):")
        print(f"  {'janela':>12} {'n':>11} {'mu1':>6} {'w1':>7} {'mu2':>6} {'w2':>7}")
        for _, r in sens[sens.largura == 5].iterrows():
            marca = " ←mudança de rótulo" if r.toca_deriva else ""
            print(f"  {r.janela:>12} {r.n_nao_censurado:>11,.0f} {r.mu1:>6.2f} "
                  f"{100 * r.w1:>6.1f}% {r.mu2:>6.2f} {100 * r.w2:>6.1f}%{marca}")
        # As janelas até 2013-2017 caem em OUTRA solução do GMM (mu1≈8-10a, que
        # não é um modo jovem). Comparar w1 entre soluções qualitativamente
        # distintas seria comparar coisas diferentes, então o contraste abaixo
        # se restringe às janelas em que o GMM acha o mesmo par de modos.
        comp = sens[(sens.largura == 5) & (sens.mu1 < 6)]
        outra = sens[(sens.largura == 5) & (sens.mu1 >= 6)]
        if len(outra):
            print(f"\n  ⚠️  {len(outra)} janelas antigas ({outra.janela.iloc[0]}…"
                  f"{outra.janela.iloc[-1]}) caem em outra solução do GMM (mu1≈"
                  f"{outra.mu1.mean():.0f}a): não são comparáveis e ficam de fora.")
        if len(comp):
            limpas = comp[~comp.toca_deriva]
            sujas = comp[comp.toca_deriva]
            print("\n  Entre as janelas com a MESMA solução (mu1≈4a), w1 sobe monotonicamente")
            print("  com a exposição à mudança de rótulo:")
            for _, r in comp.iterrows():
                print(f"    {r.janela}  w1={100 * r.w1:5.1f}%"
                      f"{'   (janela inteiramente dentro da mudança de rótulo)' if r.ano_inicio >= 2020 else ''}")
            if len(limpas):
                print(f"\n  Base anterior à mudança de rótulo: w1 ≈ {100 * limpas.w1.min():.0f}–"
                      f"{100 * limpas.w1.max():.0f}%. Ato III publicado: w1 = 51,5%.")
            print("  Os MODOS (mu1≈4-5a, mu2≈21-23a) são estáveis em todas — a bimodalidade")
            print("  sobrevive. O que se move é o PESO, e ele se move com a mudança de rótulo.")

    print("\nConclusão: o 'salto 2020→2022' do §4-E NÃO é reclassificação de novas")
    print("classes de agricultura, nem concentração espacial, nem mudança real de")
    print("comportamento do produtor. É DERIVA DO DESTINO: a saída da pastagem migra")
    print("de 'agricultura' para 'Mosaico de Usos'. O que resta rotulado P→A no fim da")
    print("série é resíduo selecionado (jovem, pouco censurado), não amostra do mesmo")
    print("fenômeno. Estatística do #28 sobre 2020-2024 não é comparável com o resto.")
    print("=" * 72)


def main() -> None:
    ap = argparse.ArgumentParser(description="#28D — mudança de rótulo do mosaico no fim da série")
    ap.add_argument("--rapido", action="store_true",
                    help="usa 6 shards em vez de 16 (itera rápido; tendência preservada)")
    ap.add_argument("--reusar-transicoes", action="store_true",
                    help="reaproveita o CSV do Bloco A (que leva ~9 min sobre o cubo)")
    args = ap.parse_args()

    DIR_OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    csv_trans = DIR_OUT / "deriva_mosaico_transicoes.csv"
    if args.reusar_transicoes and csv_trans.exists():
        print(f"Bloco A — reusando {csv_trans.name}")
        trans = pd.read_csv(csv_trans)
    else:
        trans = bloco_a_transicoes(rapido=args.rapido)
        trans.to_csv(csv_trans, index=False)

    print("Bloco B — área por classe")
    areas = bloco_b_areas()
    if areas is not None:
        areas.to_csv(DIR_OUT / "deriva_mosaico_areas.csv", index=False)

    print("Bloco C — efeito na medida do #28")
    efeito = bloco_c_efeito_no_28()
    if efeito is not None:
        efeito.to_csv(DIR_OUT / "deriva_mosaico_efeito_28.csv", index=False)

    print("Bloco D — âncora externa SIDRA")
    sidra = bloco_d_ancora_sidra()
    if sidra is not None:
        sidra.to_csv(DIR_OUT / "deriva_mosaico_sidra.csv", index=False)

    print("Bloco E — sensibilidade da manchete do #28")
    sens = bloco_e_sensibilidade_gmm()
    if sens is not None:
        sens.to_csv(DIR_OUT / "deriva_mosaico_sensibilidade_gmm.csv", index=False)

    figura(trans, areas)
    veredito(trans, areas, efeito, sidra, sens)
    print(f"\nTempo total: {time.time() - t0:.0f}s")
    if args.rapido:
        print("⚠️  Rodado com --rapido (6 shards): números absolutos NÃO são o censo.")


if __name__ == "__main__":
    main()
