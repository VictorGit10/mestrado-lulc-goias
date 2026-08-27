"""exploratorio_col11_verificar.py — EXPLORATÓRIO, fora da dissertação
================================================================================

⚠️  ESCOPO. Exploratório da Coleção 11. Não toca em nada da dissertação.

PARA QUE SERVE
--------------
O esqueleto do dossiê novo (`ESQUELETO_DOSSIE.md`) será redigido por outra IA. Cada número
que ela vai escrever precisa estar rastreado até o CSV que o produziu, senão o texto vira
afirmação sem lastro — que é exatamente o modo de falha que este projeto já catalogou
("régua sem etiqueta", "rótulo de figura envelhece").

Este script re-deriva TODOS os números do esqueleto a partir dos CSVs em
`data/processed/exploratorio_col11/` e compara com o valor escrito. Ele não confia no que
está no texto: recalcula e confronta.

SAÍDA: uma linha por asserção, com OK ou FALHA, e o total no fim. Código de saída != 0 se
qualquer asserção falhar, para servir de portão antes de publicar.

⚠️ O que ele NÃO verifica: se a INTERPRETAÇÃO é justa. Ele confere aritmética e
proveniência, não argumento. Overclaim passa por aqui sem ser detectado.

COMO RODAR
    python scripts/exploratorio_col11_verificar.py

Quando: 2026-08-27.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "processed"
E = D / "exploratorio_col11"

IDS_AGRI = [9, 19, 20, 35, 36, 39, 40, 41, 46, 47, 48, 62]
MOS, PAS, SOJ = 21, 15, 39

_ok, _falhas = 0, []


def check(rotulo: str, obtido, esperado, tol=0.0005, fonte=""):
    global _ok
    try:
        bate = abs(float(obtido) - float(esperado)) <= tol
    except (TypeError, ValueError):
        bate = obtido == esperado
    if bate:
        _ok += 1
        print(f"  OK    {rotulo:<58} = {obtido}   [{fonte}]")
    else:
        _falhas.append(rotulo)
        print(f"  FALHA {rotulo:<58} obtido {obtido} != esperado {esperado}   [{fonte}]")


def grupos_por_ano(f: Path) -> pd.DataFrame:
    d = pd.read_csv(f, encoding="utf-8")
    g = lambda ids: d[d.class_id.isin(ids)].groupby("ano").area_ha.sum() / 1e6
    out = pd.DataFrame({"agricultura": g(IDS_AGRI), "mosaico": g([MOS]),
                        "pastagem": g([PAS]), "soja": g([SOJ])})
    out["uniao"] = out.agricultura + out.mosaico
    return out


def main() -> None:
    print("VERIFICAÇÃO DO ESQUELETO DO DOSSIÊ DA COLEÇÃO 11")
    print("=" * 96)

    # ---------- Cap. 2 — idade ----------
    print("\n[Cap. 2] idade da pastagem ao converter  (col11_cap2_idade.csv)")
    t = pd.read_csv(E / "col11_cap2_idade.csv").set_index("ano")
    f = "col11_cap2_idade.csv"
    for ano, conv, pct, med in [(2019, 1117213, 54.9, 22), (2022, 285236, 18.2, 4),
                                (2024, 157245, 4.0, 5)]:
        check(f"col10.1 {ano} conversões (= dossiê)", t.loc[ano, "conv_c101"], conv, 0.5, f)
        check(f"col10.1 {ano} % desconhecida (= dossiê)", t.loc[ano, "pct_desconh_c101"], pct, 0.05, f)
        check(f"col10.1 {ano} mediana de idade (= dossiê)", t.loc[ano, "idade_med_c101"], med, 0.5, f)
    check("col11 2024 conversões", t.loc[2024, "conv_c11"], 529865, 0.5, f)
    check("col11 2024 mediana de idade", t.loc[2024, "idade_med_c11"], 6, 0.5, f)
    check("col11 2019 mediana de idade", t.loc[2019, "idade_med_c11"], 19, 0.5, f)
    check("razão conversões col11/col10.1 em 2024",
          t.loc[2024, "conv_c11"] / t.loc[2024, "conv_c101"], 3.37, 0.02, f)

    # ---------- Cap. 3 — fluxos ----------
    print("\n[Cap. 3] fluxo pasto->destino  (col11_cap3_fluxos_censo_ibge.csv)")
    c3 = pd.read_csv(E / "col11_cap3_fluxos_censo_ibge.csv").set_index("ano_conversao")
    f = "col11_cap3_fluxos_censo_ibge.csv"
    check("col10.1 2015 -> Agricultura (mil ha)", c3.loc[2015, "agricultura_c101"] / 1e3, 190.1, 0.15, f)
    check("col10.1 2024 -> Agricultura (mil ha)", c3.loc[2024, "agricultura_c101"] / 1e3, 14.2, 0.15, f)
    check("col11  2015 -> Agricultura (mil ha)", c3.loc[2015, "agricultura_c11"] / 1e3, 256.6, 0.15, f)
    check("col11  2024 -> Agricultura (mil ha)", c3.loc[2024, "agricultura_c11"] / 1e3, 47.7, 0.15, f)
    check("col10.1 queda 2015->2024 do fluxo p/ Agricultura (x)",
          c3.loc[2015, "agricultura_c101"] / c3.loc[2024, "agricultura_c101"], 13.4, 0.15, f)
    check("col11 queda 2015->2024 do fluxo p/ Agricultura (x)",
          c3.loc[2015, "agricultura_c11"] / c3.loc[2024, "agricultura_c11"], 5.4, 0.1, f)
    check("col10.1 razão M/A em 2024", c3.loc[2024, "razao_c101"], 37.74, 0.02, f)
    check("col11 razão M/A em 2024", c3.loc[2024, "razao_c11"], 4.89, 0.02, f)

    # ---------- Cap. 4 — estoques ----------
    print("\n[Cap. 4] estoques  (censo_munis_col10_1.csv / censo_munis_col11.csv)")
    a = grupos_por_ano(E / "censo_munis_col10_1.csv")
    b = grupos_por_ano(E / "censo_munis_col11.csv")
    ref = grupos_por_ano(D / "mapbiomas_munis_goias.csv")
    f = "censo_munis_*.csv"
    # A fonte do dossiê reproduz o Cap. 4 EXATAMENTE; o meu censo reproduz dentro de
    # 0,13%, desvio UNIFORME (área total do estado também difere 0,119%) que vem da
    # rasterização da malha, não de classe. As duas coisas são asseridas em separado.
    check("REF Agricultura 2020 = dossiê 5,668", ref.loc[2020, "agricultura"], 5.668, 0.001, "mapbiomas_munis_goias.csv")
    check("REF Agricultura 2024 = dossiê 5,732", ref.loc[2024, "agricultura"], 5.732, 0.001, "mapbiomas_munis_goias.csv")
    check("REF Mosaico 2024 = dossiê 3,586", ref.loc[2024, "mosaico"], 3.586, 0.001, "mapbiomas_munis_goias.csv")
    check("REF Pastagem 2024 = dossiê 11,989", ref.loc[2024, "pastagem"], 11.989, 0.001, "mapbiomas_munis_goias.csv")
    for serie in ("agricultura", "mosaico", "pastagem"):
        dif = 100 * abs(a.loc[2024, serie] - ref.loc[2024, serie]) / ref.loc[2024, serie]
        check(f"meu censo × fonte do dossiê, {serie} 2024: desvio < 0,15%", dif < 0.15, True, 0, f)
    check("desvio da ÁREA TOTAL do estado (%) — mostra que é uniforme",
          100 * abs(a.loc[2024].sum() - ref.loc[2024].sum()) / ref.loc[2024].sum(), 0.119, 0.01, f)
    check("col11 Agricultura Δ2020-24 (Mha)", b.loc[2024, "agricultura"] - b.loc[2020, "agricultura"], 0.144, 0.004, f)
    check("col10.1 Agricultura Δ2020-24 (Mha)", a.loc[2024, "agricultura"] - a.loc[2020, "agricultura"], 0.064, 0.004, f)
    check("col10.1 união Δ2020-24 (Mha)", a.loc[2024, "uniao"] - a.loc[2020, "uniao"], 1.415, 0.006, f)
    check("col11 união Δ2020-24 (Mha)", b.loc[2024, "uniao"] - b.loc[2020, "uniao"], 0.801, 0.006, f)
    soja = pd.read_csv(D / "deriva_mosaico_sidra.csv").set_index("ano").soja_mha
    check("soja IBGE Δ2020-24 (Mha)", soja[2024] - soja[2020], 1.364, 0.002, "deriva_mosaico_sidra.csv")
    check("TETO da D26 na col11 fica ABAIXO do IBGE",
          (b.loc[2024, "uniao"] - b.loc[2020, "uniao"]) < (soja[2024] - soja[2020]), True, 0, f)
    check("TETO da D26 na col10.1 fica ACIMA do IBGE",
          (a.loc[2024, "uniao"] - a.loc[2020, "uniao"]) > (soja[2024] - soja[2020]), True, 0, f)

    # ---------- Cap. 7 — centro de massa ----------
    print("\n[Cap. 7] centro de massa  (col11_cap7_centro_massa_municipal.csv)")
    cm = pd.read_csv(E / "col11_cap7_centro_massa_municipal.csv")
    f = "col11_cap7_centro_massa_municipal.csv"
    g = lambda col, ser: cm[(cm.colecao == col) & (cm.serie == ser)].iloc[0]
    r = g("col10.1", "uniao")
    check("col10.1 união desloc (dossiê +4,1)", r.desloc_km, 4.13, 0.05, f)
    check("col10.1 união IC baixo", r.ic95_lo, 0.52, 0.05, f)
    check("col10.1 união IC alto", r.ic95_hi, 7.29, 0.05, f)
    r = g("col10.1", "agricultura")
    check("col10.1 Agricultura desloc", r.desloc_km, 0.65, 0.05, f)
    check("col10.1 Agricultura: IC INCLUI zero", bool(r.ic95_lo < 0 < r.ic95_hi), True, 0, f)
    r = g("col11", "agricultura")
    check("col11 Agricultura desloc", r.desloc_km, 1.71, 0.05, f)
    check("col11 Agricultura: IC NÃO inclui zero", bool(r.ic95_lo > 0), True, 0, f)
    p101, p11 = g("col10.1", "pastagem"), g("col11", "pastagem")
    check("col10.1 pastagem desloc", p101.desloc_km, 13.02, 0.05, f)
    check("col11 pastagem desloc", p11.desloc_km, 7.28, 0.05, f)
    check("pastagem perde 44% da marcha", 100 * (1 - p11.desloc_km / p101.desloc_km), 44.1, 0.6, f)
    check("ICs da pastagem NÃO se sobrepõem", bool(p11.ic95_hi < p101.ic95_lo), True, 0, f)
    check("col10.1 soja-satélite recua ao sul", bool(g("col10.1", "soja_sat").desloc_km < 0), True, 0, f)
    check("col11 soja-satélite recua ao sul", bool(g("col11", "soja_sat").desloc_km < 0), True, 0, f)
    check("soja-campo IBGE avança ao norte", g("IBGE", "soja_campo").desloc_km, 9.93, 0.05, f)

    # ---------- Sentinel ----------
    print("\n[Teste central] Sentinel-2 como juiz  (col11_sentinel_juiz_2024_escala10m.csv)")
    sj = pd.read_csv(E / "col11_sentinel_juiz_2024_escala10m.csv")
    f = "col11_sentinel_juiz_2024_escala10m.csv"
    ag = sj.assign(w=sj.f_agri * sj.n_10m).groupby("populacao")[["n_10m", "w"]].sum()
    ag["f_agri"] = ag.w / ag.n_10m
    piso, teto = ag.loc["PISO_pasto_nos_dois", "f_agri"], ag.loc["TETO_agri_nos_dois", "f_agri"]
    pos = lambda p: 100 * (ag.loc[p, "f_agri"] - piso) / (teto - piso)
    check("nº de recortes varridos", sj.regiao.nunique(), 6, 0, f)
    check("escala Sentinel (m)", sj.escala_m.unique()[0], 10, 0, f)
    check("piso f_agri (pasto nos dois)", piso, 0.0208, 0.001, f)
    check("teto f_agri (agri nos dois)", teto, 0.7886, 0.001, f)
    check("Mosaico->Pastagem: posição no vão (%)", pos("mos101_para_pasto11"), 4.6, 0.15, f)
    check("Mosaico->Agricultura: posição no vão (%)", pos("mos101_para_agri11"), 46.1, 0.15, f)
    check("Mosaico sobrevivente: posição no vão (%)", pos("mos101_sobrevive"), 23.5, 0.15, f)
    check("separação entre as duas populações (x)",
          pos("mos101_para_agri11") / pos("mos101_para_pasto11"), 10.0, 0.4, f)
    # Mosaico inteiro da 10.1 reconstruído das partes
    partes = ["mos101_para_pasto11", "mos101_sobrevive", "mos101_para_agri11"]
    n = ag.loc[partes, "n_10m"].sum()
    fm = (ag.loc[partes, "f_agri"] * ag.loc[partes, "n_10m"]).sum() / n
    check("Mosaico inteiro reconstruído: f_agri (~0,115 do Cap. 9)", fm, 0.135, 0.004, f)

    # ---------- Borda x calendário ----------
    print("\n[Borda × calendário] 5 coleções  (col11_fluxos_absolutos_scale100m.csv)")
    fa = pd.read_csv(E / "col11_fluxos_absolutos_scale100m.csv", dtype={"colecao": str})
    f = "col11_fluxos_absolutos_scale100m.csv"
    v = lambda c, y: fa[(fa.colecao == c) & (fa.ano == y)].para_agricultura_ha.iloc[0] / 1e3
    check("col6 2019 -> Agricultura (mil ha)", v("6", 2019), 99.3, 0.15, f)
    check("col6 2020 (SUA borda) -> Agricultura", v("6", 2020), 72.9, 0.15, f)
    check("col8 2021 -> Agricultura (tombo)", v("8", 2021), 17.0, 0.15, f)
    check("col8 2022 (SUA borda) SOBE em relação a 2021", bool(v("8", 2022) > v("8", 2021)), True, 0, f)
    check("col9 2021 -> Agricultura (tombo)", v("9", 2021), 14.9, 0.15, f)
    check("col10.1 2021 -> Agricultura (tombo)", v("10.1", 2021), 21.8, 0.15, f)
    check("col11 2021 -> Agricultura (tombo)", v("11", 2021), 34.3, 0.15, f)
    check("todas as coleções que alcançam 2021 despencam nele",
          all(v(c, 2021) < 0.4 * v(c, 2019) for c in ("8", "9", "10.1", "11")), True, 0, f)

    # ---------- Origem da soja nova ----------
    print("\n[Origem da soja nova]  (col11_origem_soja_nova_scale100m.csv)")
    os_ = pd.read_csv(E / "col11_origem_soja_nova_scale100m.csv")
    f = "col11_origem_soja_nova_scale100m.csv"
    tot = os_.col10_1_ha.sum()
    frac = lambda nome: 100 * os_[os_.origem == nome].col10_1_ha.iloc[0] / tot
    check("soja nova vinda de Outras temporárias (%)", frac("Outras temporárias"), 43.3, 0.15, f)
    check("soja nova vinda de Cana (%)", frac("Cana"), 35.1, 0.15, f)
    check("soja nova vinda de PASTAGEM (%)", frac("PASTAGEM"), 11.5, 0.15, f)
    check("soja nova vinda de MOSAICO (%)", frac("MOSAICO"), 8.5, 0.15, f)
    check("soma 'já era lavoura' (temporárias + cana) (%)",
          frac("Outras temporárias") + frac("Cana"), 78.4, 0.3, f)

    # ---------- Classe Soja entre coleções ----------
    print("\n[A col11 não mexe na Soja]  (col11_soja_vs_ibge_scale100m.csv)")
    sv = pd.read_csv(E / "col11_soja_vs_ibge_scale100m.csv").set_index("ano")
    f = "col11_soja_vs_ibge_scale100m.csv"
    dif = 100 * (sv["soja_col11_Mha"] - sv["soja_col10.1_Mha"]).abs() / sv["soja_col10.1_Mha"]
    # ⚠️ Eu havia dito "<=1,3%" olhando só 2024. O máximo real é 1,72%, em 2021.
    check("diferença máxima da classe Soja entre coleções (%)", dif.max(), 1.72, 0.02, f)
    check("diferença MÍNIMA da classe Soja entre coleções (%)", dif.min(), 1.35, 0.02, f)
    check("2014: mapa e IBGE praticamente coincidem (dif %)",
          100 * abs(sv.loc[2014, "soja_col10.1_Mha"] - sv.loc[2014, "soja_IBGE_Mha"]) / sv.loc[2014, "soja_IBGE_Mha"],
          1.5, 0.4, f)
    check("2019: o mapa está ACIMA do IBGE (dif %)",
          100 * (sv.loc[2019, "soja_col10.1_Mha"] - sv.loc[2019, "soja_IBGE_Mha"]) / sv.loc[2019, "soja_IBGE_Mha"],
          26.0, 0.6, f)

    # ---------- Matriz de confusão ----------
    print("\n[Matriz de confusão 2024]  (col11_concordancia_escala100m.csv)")
    cc = pd.read_csv(E / "col11_concordancia_escala100m.csv")
    f = "col11_concordancia_escala100m.csv"
    d24 = cc[cc.ano == 2024]
    check("concordância global (%)",
          100 * d24[d24.de_col10_1 == d24.para_col11].frac_do_total.sum(), 87.86, 0.05, f)
    lin = d24[d24.de_col10_1 == "mosaico"]
    tm = lin.frac_do_total.sum()
    dest = lambda c: 100 * lin[lin.para_col11 == c].frac_do_total.iloc[0] / tm
    check("do Mosaico da 10.1 -> pastagem (%)", dest("pastagem"), 44.7, 0.2, f)
    check("do Mosaico da 10.1 -> permanece (%)", dest("mosaico"), 36.8, 0.2, f)
    check("do Mosaico da 10.1 -> veg. natural (%)", dest("veg_natural"), 13.4, 0.2, f)
    check("do Mosaico da 10.1 -> agricultura (%)", dest("agricultura"), 4.3, 0.2, f)
    latd = lambda c: lin[lin.para_col11 == c].lat_media.iloc[0]
    check("gradiente Sul->Norte: agricultura é a mais ao SUL",
          bool(latd("agricultura") < latd("pastagem") < latd("veg_natural")), True, 0, f)
    check("latitude do destino agricultura", latd("agricultura"), -17.187, 0.005, f)
    check("latitude do destino veg. natural", latd("veg_natural"), -16.165, 0.005, f)

    # ---------- Correlação que NÃO reproduz ----------
    print("\n[Achado: r=0,84 do dossiê NÃO reproduz]")
    mos = pd.read_csv(E / "censo_munis_col10_1.csv")
    mos = mos[mos.class_id == MOS].groupby(["cd_mun", "ano"]).area_ha.sum()
    pam = pd.read_csv(D / "sidra_pam1612_temporarias.csv", encoding="utf-8")
    sc = (pam[(pam.categoria.astype(str).str.contains("Soja"))
              & (pam.variavel.astype(str).str.contains("plantada", case=False))]
          .groupby(["cd_mun", "ano"]).valor.sum())
    x = mos.xs(2024, level=1) - mos.xs(2019, level=1)
    y = sc.xs(2024, level=1) - sc.xs(2019, level=1)
    i = x.index.intersection(y.index)
    r_obt = float(np.corrcoef(x.loc[i], y.loc[i])[0, 1])
    check("r obtido (dossiê afirma 0,84)", r_obt, 0.739, 0.002, "censo + PAM 1612")
    check("r do dossiê NÃO é reproduzido", bool(abs(r_obt - 0.84) > 0.05), True, 0, "—")
    check("magnitude ΔMosaico (dossiê 1,53 Mha)", x.loc[i].sum() / 1e6, 1.523, 0.005, "censo")
    check("magnitude ΔSoja (dossiê 1,54 Mha)", y.loc[i].sum() / 1e6, 1.539, 0.005, "PAM 1612")

    # ---------- números que aparecem SÓ no esqueleto ----------
    print("")
    print("[Esqueleto] hero, Cap. 7 e Cap. 10")
    check("hero: encolhimento do Mosaico 2024 (%)",
          100 * (b.loc[2024, "mosaico"] / a.loc[2024, "mosaico"] - 1), -47.4, 0.3, "censo_munis_*.csv")
    check("hero: Mosaico 2024 col10.1 (Mha)", a.loc[2024, "mosaico"], 3.586, 0.006, "censo")
    check("hero: Mosaico 2024 col11 (Mha)", b.loc[2024, "mosaico"], 1.888, 0.006, "censo")
    cr = lambda c: 100 * (sv.loc[2024, c] / sv.loc[2014, c] - 1)
    check("Cap.7 crescimento 2014->2024 IBGE (%)", cr("soja_IBGE_Mha"), 55.6, 0.3, "col11_soja_vs_ibge")
    check("Cap.7 crescimento 2014->2024 mapa col10.1 (%)", cr("soja_col10.1_Mha"), 51.7, 0.3, "col11_soja_vs_ibge")
    check("Cap.7 captura do crescimento 2019->2024 (%)",
          100 * (sv.loc[2024, "soja_col10.1_Mha"] - sv.loc[2019, "soja_col10.1_Mha"]) /
                (sv.loc[2024, "soja_IBGE_Mha"] - sv.loc[2019, "soja_IBGE_Mha"]), 29.7, 0.4, "col11_soja_vs_ibge")
    print("")
    print("[Cap. 10] largura do vao da regua dupla")
    fa2 = fa.assign(uniao=fa.para_agricultura_ha + fa.para_mosaico_ha)
    def vao(c, y):
        r_ = fa2[(fa2.colecao == c) & (fa2.ano == y)]
        return r_.uniao.iloc[0] / r_.para_agricultura_ha.iloc[0]
    for y_, e101, e11 in [(2015, 1.6, 1.3), (2020, 5.6, 3.0), (2022, 14.5, 5.3), (2024, 33.9, 5.8)]:
        check(f"vao col10.1 em {y_} (x)", vao("10.1", y_), e101, 0.06, "col11_fluxos_absolutos_scale100m.csv")
        check(f"vao col11 em {y_} (x)", vao("11", y_), e11, 0.06, "col11_fluxos_absolutos_scale100m.csv")
    print("")
    print("[Cap. 9] centro de massa por pixel (descarta MAUP)")
    KM = 110.9
    cmp_ = {t: pd.read_csv(E / f"centro_massa_classe_{t}.csv") for t in ("col10_1", "col11")}
    def latg(d, ano, ids):
        x = d[(d.ano == ano) & (d.class_id.isin(ids))]
        return (x.lat * x.n_pixels).sum() / x.n_pixels.sum()
    series = [("agricultura", IDS_AGRI, "agricultura", 0.72, 1.70),
              ("mosaico", [MOS], "mosaico", -12.48, -23.73),
              ("uniao", IDS_AGRI + [MOS], "uniao", 3.95, 3.14),
              ("pastagem", [PAS], "pastagem", 13.07, 7.25),
              ("soja", [SOJ], "soja_sat", -6.59, -6.04)]
    maxdif = 0.0
    for nome, ids, ser, e101, e11 in series:
        for tag, col, esp in (("col10_1", "col10.1", e101), ("col11", "col11", e11)):
            dpix = (latg(cmp_[tag], 2024, ids) - latg(cmp_[tag], 2019, ids)) * KM
            check(f"pixel: {nome} {tag} (km)", dpix, esp, 0.06, f"centro_massa_classe_{tag}.csv")
            dmun = cm[(cm.colecao == col) & (cm.serie == ser)].desloc_km.iloc[0]
            maxdif = max(maxdif, abs(dpix - dmun))
    check("as duas ponderacoes concordam dentro de 0,6 km", maxdif < 0.6, True, 0, "pixel x municipal")
    check("maior discrepancia entre ponderacoes (km)", maxdif, 0.60, 0.06, "-")

    print("\n" + "=" * 96)
    print(f"{_ok} asserções OK, {len(_falhas)} falha(s)")
    if _falhas:
        for x_ in _falhas:
            print(f"   FALHOU: {x_}")
        sys.exit(1)
    print("Todas as asserções do esqueleto conferem com os CSVs.")


if __name__ == "__main__":
    main()
