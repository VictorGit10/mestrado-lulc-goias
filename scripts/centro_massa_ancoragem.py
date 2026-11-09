"""centro_massa_ancoragem.py -- Pipeline #58: quem segura e quem move o centro de massa
====================================================================================

PERGUNTA QUE RESPONDE
---------------------
O #32 mede QUANTO o centro de massa se deslocou (pasto +78 km, rebanho +67, lavoura +65).
Não diz QUEM o segura onde está nem O QUE o moveu. Duas perguntas, duas ferramentas:

  (1) ANCORAGEM -- que zona do estado segura a posição do centro em cada ano?
      Métricas de exclusão (leave-one-out) e de alavanca, na forma usada por Barroso et
      al. (manuscrito em revisão, centros de massa de área queimada por bioma), trocando
      "bioma" por zona de Goiás. Sugestão do próprio Barroso ao autor (set/2026).

  (2) DECOMPOSIÇÃO DO DESLOCAMENTO -- o ΔNorte veio de as zonas TROCAREM DE PESO entre
      si, ou de a atividade andar ao norte DENTRO de cada zona? É a pergunta que a regra
      de leitura do centro de massa ("centro de gravidade N km mais ao norte", nunca "a
      lavoura subiu") pedia e que até aqui só tinha a tabela de composição por região.

ABORDAGEM
---------
O centro médio do #32 se decompõe sem perda por qualquer partição do estado em zonas:

    C(t) = Σ_b w_b(t)·C_b(t),   w_b = A_b / Σ_j A_j,   C_b = centro médio das AMCs da zona b

(A_b = massa da zona: ha, cabeças). O script CONFERE que essa reconstrução bate com o
centro publicado pelo #32 (tolerância 1 m).

(1) Ancoragem, por ano t e zona b:
    C^(−b)   = centro recomputado sem a zona b (pesos renormalizados)
    LOO_b    = |C − C^(−b)|                       (km, 2D; métrica do manuscrito)
    puxao_N  = C_N − C_N^(−b)                     (km; + = a zona puxa o centro ao norte)
    Infl_b   = w_b·|C_b − C|                      (braço de alavanca: massa × distância)
    Share_b  = Infl_b / Σ_k Infl_k

    ⚠ As duas métricas NÃO são independentes. Por álgebra, C − C^(−b) = w_b·(C_b − C^(−b))
    e C_b − C = (1 − w_b)·(C_b − C^(−b)), logo  LOO_b = Infl_b / (1 − w_b)  exatamente.
    O manuscrito as chama de "complementares"; aqui são a mesma quantidade em duas
    escalas. O script verifica a identidade e reporta as duas só por fidelidade ao método.

(2) Decomposição simétrica (ponto médio) do deslocamento entre a0 e a1, por zona:

    ΔC = Σ_b (w_b1 − w_b0)·(C̄_b − C̄)   +   Σ_b (w_b0 + w_b1)/2 · (C_b1 − C_b0)
         └────── ENTRE zonas ──────┘       └────────── DENTRO das zonas ──────────┘
    C̄_b = (C_b0 + C_b1)/2;  C̄ = centro do estado, média dos dois extremos.

    É uma identidade exata (sem resíduo). A SOMA do termo ENTRE não depende de C̄ porque
    Σ_b (w_b1 − w_b0) = 0; a parcela de cada zona depende, e C̄ é o que lhe dá leitura
    (corrigido em 28/set/2026: a primeira versão gravava a parcela em coordenada absoluta). Zona sem massa num dos extremos (C_b
    indefinido) recebe o C_b do outro extremo: seu DENTRO é zero e o que ela contribui
    vai inteiro para ENTRE (ela "entra" ou "sai" do estado).

    Versão ENCADEADA: soma das decomposições ano a ano dentro da janela. Endpoint e
    encadeada dão o mesmo total; a partição entre/dentro pode diferir se o caminho for
    sinuoso -- a diferença é reportada.

LIMITE DECLARADO -- a partição
------------------------------
A fração ENTRE depende da partição por construção: com 1 zona ela é 0%; com as 166 AMCs
como zonas ela é 100% (o centroide de uma AMC não se move). O número "X% do deslocamento
vem da troca de peso" só tem sentido COM a escala das zonas ao lado. Por isso o script
roda quatro partições -- 3 regiões (a canônica do projeto), 5 mesorregiões, 4 faixas de
latitude (quartis, sem fronteira administrativa) e as 166 AMCs (teste de sanidade: ENTRE
tem de dar 100%) -- e a leitura é a de uma ESCALA: quanto do deslocamento já aparece
quando o estado é visto em 3–5 pedaços.

O mesmo vale para a ancoragem: a zona é um recorte escolhido, não uma unidade natural
como o bioma do manuscrito. E pouca alavanca não é pouca massa: uma zona pesada que
fica sobre o centro do estado tem Share ≈ 0.

Uma AMC (16151: Niquelândia + Mimoso de Goiás) tem municípios em duas mesorregiões
(Norte e Leste Goiano, 1 a 1). A regra canônica (`amc_para_meso`, modal) a põe no Leste,
logo no Centro. O script mede o efeito de passá-la ao Norte.

Só o centro MÉDIO se decompõe. O centro mediano (Weiszfeld) do #32 não é uma média
ponderada de centros de zona e fica fora deste pipeline.

INCERTEZA
---------
IC95% da decomposição por bootstrap de AMCs com as regras do projeto: i.i.d. (D19, uma
AMC por bloco) e em blocos espaciais (#55, k-means; k = 33 e 12). A AMC leva a sua zona
consigo. Réplica em que uma zona some nos dois extremos entra com as zonas restantes.

ENTRADAS
    data/processed/painel_amc_goias.parquet, amc_goias.gpkg   (#25, via centro_massa.py)
    data/processed/amc_crosswalk_goias.csv, mapeamento_mesorregioes.csv
    data/processed/centro_massa_anual.csv, centro_massa_robustez_deriva.csv   (#32, conferência)

SAÍDAS
    data/processed/centro_massa_ancoragem_anual.csv    (partição × variável × ano × zona)
    data/processed/centro_massa_ancoragem_resumo.csv   (mediana e IQR por janela)
    data/processed/centro_massa_decomposicao.csv       (partição × variável × janela × zona)
    data/processed/centro_massa_decomposicao_ic.csv    (IC95% do total/entre/dentro, por k)
    outputs/centro_massa/ancoragem_puxao_norte.png
    outputs/centro_massa/ancoragem_decomposicao.png

COMO RODAR
    python scripts/centro_massa_ancoragem.py
    python scripts/centro_massa_ancoragem.py --sem-figuras --sem-bootstrap

Depende de: #32 (centro_massa.py), #34 (amc_para_meso), #55 (kmeans_blocos).
Quando foi feito: 2026-09-28.
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
import centro_massa as cm                                             # noqa: E402
from config_periodos import ATOS                                      # noqa: E402
from deslocamento_espacial import amc_para_meso, MESO_SUL, MESO_NORTE  # noqa: E402
from robustez_bootstrap_bloco import kmeans_blocos                    # noqa: E402

ROOT     = Path(__file__).resolve().parent.parent
DIR_PROC = ROOT / "data" / "processed"
DIR_OUT  = ROOT / "outputs" / "centro_massa"

ARQ_ANUAL  = DIR_PROC / "centro_massa_ancoragem_anual.csv"
ARQ_RESUMO = DIR_PROC / "centro_massa_ancoragem_resumo.csv"
ARQ_DECOMP = DIR_PROC / "centro_massa_decomposicao.csv"
ARQ_DEC_IC = DIR_PROC / "centro_massa_decomposicao_ic.csv"

ANO_INI, ANO_FIM = cm.ANO_INI, cm.ANO_FIM
AMC_DIVIDIDA = 16151          # Niquelândia (Norte Goiano) + Mimoso de Goiás (Leste Goiano)

BOOT_B    = cm.BOOT_B         # 2000, o mesmo da D19 e do #55
BOOT_SEED = 20260928
GRADE_K   = [166, 33, 12]     # 166 = i.i.d. (D19); 33 e 12 = blocos do #55

ORDEM_ZONAS = {
    "regiao3":   ["Sul", "Centro", "Norte"],
    "meso5":     ["Sul Goiano", "Leste Goiano", "Centro Goiano", "Noroeste Goiano", "Norte Goiano"],
    "faixa_lat4": ["F1 (sul)", "F2", "F3", "F4 (norte)"],
}
ROTULO_PARTICAO = {"regiao3": "3 regiões", "meso5": "5 mesorregiões",
                   "faixa_lat4": "4 faixas de latitude", "amc166": "166 AMCs"}
CORES_ZONA = {"Sul": "#c2185b", "Centro": "#e8920c", "Norte": "#2e7d32"}   # as do #57


# ---------------------------------------------------------------------------
# 1. Dados: painel do #32 + zonas por AMC
# ---------------------------------------------------------------------------

def regiao_de_meso(m: str) -> str:
    """Regra canônica do projeto (#34/#39/#57)."""
    if m in MESO_SUL:
        return "Sul"
    if m in MESO_NORTE:
        return "Norte"
    return "Centro"


def zonas_por_amc() -> pd.DataFrame:
    """code_amc → zona em cada partição. Usada também pelo exportador da página do método,
    para que a página refaça a conta com exatamente as mesmas zonas."""
    reg = amc_para_meso()
    reg["regiao3"] = reg["nm_meso"].map(regiao_de_meso)
    reg["meso5"] = reg["nm_meso"]
    lat = cm.metros_para_lonlat(reg[["cx", "cy"]].to_numpy())[:, 1]
    reg["faixa_lat4"] = pd.qcut(lat, 4, labels=ORDEM_ZONAS["faixa_lat4"]).astype(str)
    reg["amc166"] = reg["code_amc"].astype(str)
    # Sensibilidade: a AMC dividida vai ao Norte.
    reg["regiao3_alt"] = reg["regiao3"]
    reg.loc[reg["code_amc"] == AMC_DIVIDIDA, "regiao3_alt"] = "Norte"
    return reg


def carregar() -> tuple[pd.DataFrame, dict]:
    painel, _ = cm.carregar_dados()
    # Mesma construção do #32 (centro_massa.main): NaN do Mosaico/agric. vira 0.
    painel["agric_mais_mosaico_ha"] = (painel["lulc_agricultura_ha"].fillna(0)
                                       + painel["lulc_mosaico_usos_ha"].fillna(0))

    reg = zonas_por_amc()

    faltando = set(painel["code_amc"]) - set(reg["code_amc"])
    if faltando:
        raise RuntimeError(f"AMCs sem zona: {sorted(faltando)[:10]}")
    painel = painel.merge(reg[["code_amc", "regiao3", "regiao3_alt", "meso5",
                               "faixa_lat4", "amc166"]], on="code_amc", how="left")
    print(f"[zonas] regiao3: {reg['regiao3'].value_counts().to_dict()} | "
          f"AMC {AMC_DIVIDIDA} → {reg.loc[reg.code_amc == AMC_DIVIDIDA, 'nm_meso'].iloc[0]}")

    variaveis = {k: (v[0], v[1]) for k, v in cm.VARIAVEIS.items()}
    variaveis["agric_uniao_mosaico"] = ("agric_mais_mosaico_ha", "Agricultura ∪ Mosaico")
    variaveis["soja_sidra"] = ("agri_soja_ha_plantada", "Soja plantada (SIDRA)")
    return painel, variaveis


def massas_por_zona(painel: pd.DataFrame, col: str, particao: str) -> pd.DataFrame:
    """(ano, zona) → A, SX, SY. Mesma regra de peso do #32: NaN/≤0 descartados."""
    d = painel[["ano", particao, "cx", "cy", col]].copy()
    w = d[col].to_numpy(float)
    w = np.where(np.isfinite(w) & (w > 0), w, 0.0)
    d["A"], d["SX"], d["SY"] = w, w * d["cx"], w * d["cy"]
    g = d.groupby(["ano", particao])[["A", "SX", "SY"]].sum().reset_index()
    return g.rename(columns={particao: "zona"})


# ---------------------------------------------------------------------------
# 2. Conferência com o #32
# ---------------------------------------------------------------------------

def conferir_com_32(painel: pd.DataFrame, variaveis: dict) -> None:
    ref = pd.read_csv(DIR_PROC / "centro_massa_anual.csv")
    ref_r = pd.read_csv(DIR_PROC / "centro_massa_robustez_deriva.csv").rename(columns={"regua": "variavel"})
    ref = pd.concat([ref[["variavel", "ano", "x_mean", "y_mean"]],
                     ref_r[["variavel", "ano", "x_mean", "y_mean"]]])
    ref = ref.drop_duplicates(["variavel", "ano"])   # "agricultura" está nos dois arquivos
    pior = 0.0
    for chave, (col, _rot) in variaveis.items():
        r = ref[ref.variavel == chave].set_index("ano")
        if r.empty:
            raise RuntimeError(f"{chave}: sem referência no #32")
        for particao in ["regiao3", "meso5"]:
            m = massas_por_zona(painel, col, particao).groupby("ano")[["A", "SX", "SY"]].sum()
            m = m[m["A"] > 0]
            comuns = m.index.intersection(r.index)
            dx = (m.loc[comuns, "SX"] / m.loc[comuns, "A"] - r.loc[comuns, "x_mean"]).abs().max()
            dy = (m.loc[comuns, "SY"] / m.loc[comuns, "A"] - r.loc[comuns, "y_mean"]).abs().max()
            if len(comuns) != len(r) or max(dx, dy) > 1.0:
                raise RuntimeError(f"{chave}/{particao}: reconstrução ≠ #32 "
                                   f"(anos {len(comuns)}/{len(r)}, |Δ|máx {max(dx, dy):.3f} m)")
            pior = max(pior, dx, dy)
    print(f"[conferência] centro reconstruído por zona = centro do #32 em todas as "
          f"{len(variaveis)} variáveis e anos (|Δ| máx {pior:.2e} m)")


# ---------------------------------------------------------------------------
# 3. Ancoragem: LOO e alavanca
# ---------------------------------------------------------------------------

def ancoragem(painel: pd.DataFrame, variaveis: dict, particoes: list[str]) -> pd.DataFrame:
    linhas = []
    for particao in particoes:
        for chave, (col, rot) in variaveis.items():
            m = massas_por_zona(painel, col, particao)
            for ano, g in m.groupby("ano"):
                g = g[g["A"] > 0]
                if len(g) < 2:
                    continue
                A, SX, SY = g["A"].to_numpy(), g["SX"].to_numpy(), g["SY"].to_numpy()
                At, X, Y = A.sum(), SX.sum() / A.sum(), SY.sum() / A.sum()
                w = A / At
                Cbx, Cby = SX / A, SY / A
                Xo, Yo = (SX.sum() - SX) / (At - A), (SY.sum() - SY) / (At - A)
                loo = np.hypot(X - Xo, Y - Yo)
                infl = w * np.hypot(Cbx - X, Cby - Y)
                # Identidade LOO = Infl/(1−w): verificada, não suposta.
                if not np.allclose(loo * (1 - w), infl, rtol=1e-9, atol=1e-6):
                    raise RuntimeError(f"identidade LOO×Infl falhou: {particao}/{chave}/{ano}")
                for i, z in enumerate(g["zona"]):
                    linhas.append({"particao": particao, "variavel": chave, "rotulo": rot,
                                   "ano": int(ano), "zona": z, "peso": w[i],
                                   "dist_ao_centro_km": np.hypot(Cbx[i] - X, Cby[i] - Y) / 1e3,
                                   "zona_N_menos_centro_km": (Cby[i] - Y) / 1e3,
                                   "loo_km": loo[i] / 1e3,
                                   "puxao_norte_km": (Y - Yo[i]) / 1e3,
                                   "puxao_leste_km": (X - Xo[i]) / 1e3,
                                   "influencia_km": infl[i] / 1e3,
                                   "influencia_share": infl[i] / infl.sum()})
    return pd.DataFrame(linhas)


def janelas() -> list[tuple[str, int, int]]:
    js = [("LÍQUIDO", ANO_INI, ANO_FIM)]
    js += [(f"Ato {a}", i["inicio"], i["fim"]) for a, i in ATOS.items()]
    return js


def resumo_ancoragem(anc: pd.DataFrame) -> pd.DataFrame:
    """Mediana e IQR entre anos (como no manuscrito), período completo e por Ato."""
    linhas = []
    for nome, a0, a1 in janelas():
        sub = anc[anc["ano"].between(a0, a1)]
        for (p, v, z), g in sub.groupby(["particao", "variavel", "zona"]):
            reg = {"particao": p, "variavel": v, "zona": z, "janela": nome, "n_anos": len(g)}
            for c in ["peso", "loo_km", "puxao_norte_km", "influencia_share"]:
                q1, q2, q3 = g[c].quantile([.25, .5, .75])
                reg.update({f"{c}_mediana": q2, f"{c}_q1": q1, f"{c}_q3": q3})
            ini, fim = g.loc[g.ano.idxmin()], g.loc[g.ano.idxmax()]
            reg.update({"ano_ini": int(ini.ano), "ano_fim": int(fim.ano),
                        "peso_ini": ini.peso, "peso_fim": fim.peso,
                        "puxao_norte_ini_km": ini.puxao_norte_km,
                        "puxao_norte_fim_km": fim.puxao_norte_km})
            linhas.append(reg)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 4. Decomposição ENTRE × DENTRO
# ---------------------------------------------------------------------------

def _decompor(w0, w1, x0, x1, y0, y1):
    """Arrays por zona (NaN = zona sem massa naquele extremo). Retorna dict de arrays
    por zona: entre/dentro em N e L (metros)."""
    x0, x1 = np.where(np.isnan(x0), x1, x0), np.where(np.isnan(x1), x0, x1)
    y0, y1 = np.where(np.isnan(y0), y1, y0), np.where(np.isnan(y1), y0, y1)
    ok = ~(np.isnan(x0) | np.isnan(x1))          # zona vazia nos dois extremos: fora
    w0, w1 = np.where(ok, w0, 0.0), np.where(ok, w1, 0.0)
    x0, x1, y0, y1 = [np.where(ok, a, 0.0) for a in (x0, x1, y0, y1)]
    # Referência = centro médio dos dois extremos. A SOMA do termo ENTRE não depende dela
    # (Σ Δw = 0), mas a parcela de CADA zona depende: em coordenadas absolutas (~8.000 km)
    # ela não tem leitura. Medida em relação ao centro, a parcela da zona diz quanto a
    # troca de peso dela puxou o centro — e é essa que vai para o CSV.
    xr = ((w0 * x0).sum(axis=-1, keepdims=True) + (w1 * x1).sum(axis=-1, keepdims=True)) / 2
    yr = ((w0 * y0).sum(axis=-1, keepdims=True) + (w1 * y1).sum(axis=-1, keepdims=True)) / 2
    return {"entre_N": (w1 - w0) * ((y0 + y1) / 2 - yr), "dentro_N": (w0 + w1) / 2 * (y1 - y0),
            "entre_L": (w1 - w0) * ((x0 + x1) / 2 - xr), "dentro_L": (w0 + w1) / 2 * (x1 - x0)}


def _estado_ano(m: pd.DataFrame, ano: int, zonas: list) -> tuple:
    g = m[m["ano"] == ano].set_index("zona").reindex(zonas)
    A = g["A"].fillna(0).to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(A > 0, g["SX"].to_numpy() / A, np.nan)
        y = np.where(A > 0, g["SY"].to_numpy() / A, np.nan)
    return A / A.sum(), x, y


def decomposicao(painel: pd.DataFrame, variaveis: dict, particoes: list[str]) -> pd.DataFrame:
    linhas = []
    for particao in particoes:
        for chave, (col, rot) in variaveis.items():
            m = massas_por_zona(painel, col, particao)
            anos_ok = sorted(m.groupby("ano")["A"].sum().pipe(lambda s: s[s > 0]).index)
            zonas = sorted(m["zona"].unique())
            for nome, a0, a1 in janelas():
                a0e, a1e = max(a0, anos_ok[0]), min(a1, anos_ok[-1])
                if a0e >= a1e or (nome != "LÍQUIDO" and (a0e != a0 or a1e != a1)):
                    continue                    # ato sem os dois extremos (soja SIDRA, Ato I)
                w0, x0, y0 = _estado_ano(m, a0e, zonas)
                w1, x1, y1 = _estado_ano(m, a1e, zonas)
                d = _decompor(w0, w1, x0, x1, y0, y1)
                # Encadeada: soma das decomposições ano a ano.
                enc_e, enc_d = np.zeros(len(zonas)), np.zeros(len(zonas))
                for t in range(a0e, a1e):
                    wa, xa, ya = _estado_ano(m, t, zonas)
                    wb, xb, yb = _estado_ano(m, t + 1, zonas)
                    dd = _decompor(wa, wb, xa, xb, ya, yb)
                    enc_e += dd["entre_N"]
                    enc_d += dd["dentro_N"]
                # Total direto (centro médio nos extremos) — tem de fechar com a soma.
                tot_N = (np.nansum(w1 * np.nan_to_num(y1)) - np.nansum(w0 * np.nan_to_num(y0)))
                soma = d["entre_N"].sum() + d["dentro_N"].sum()
                if abs(soma - tot_N) > 1e-3 or abs(enc_e.sum() + enc_d.sum() - tot_N) > 1e-3:
                    raise RuntimeError(f"decomposição não fecha: {particao}/{chave}/{nome}")
                for i, z in enumerate(zonas):
                    linhas.append({"particao": particao, "variavel": chave, "rotulo": rot,
                                   "janela": nome, "ano_ini": a0e, "ano_fim": a1e, "zona": z,
                                   "peso_ini": w0[i], "peso_fim": w1[i],
                                   "entre_N_km": d["entre_N"][i] / 1e3,
                                   "dentro_N_km": d["dentro_N"][i] / 1e3,
                                   "entre_L_km": d["entre_L"][i] / 1e3,
                                   "dentro_L_km": d["dentro_L"][i] / 1e3,
                                   "entre_N_encadeado_km": enc_e[i] / 1e3,
                                   "dentro_N_encadeado_km": enc_d[i] / 1e3})
    return pd.DataFrame(linhas)


def totais_decomp(dec: pd.DataFrame) -> pd.DataFrame:
    t = (dec.groupby(["particao", "variavel", "rotulo", "janela", "ano_ini", "ano_fim"], sort=False)
            [["entre_N_km", "dentro_N_km", "entre_L_km", "dentro_L_km",
              "entre_N_encadeado_km", "dentro_N_encadeado_km"]].sum().reset_index())
    t["total_N_km"] = t["entre_N_km"] + t["dentro_N_km"]
    t["total_L_km"] = t["entre_L_km"] + t["dentro_L_km"]
    t["frac_entre_N"] = t["entre_N_km"] / t["total_N_km"]
    t["frac_entre_N_encadeado"] = t["entre_N_encadeado_km"] / t["total_N_km"]
    return t


def conferir_totais(tot: pd.DataFrame) -> None:
    """ΔNorte total = o do #32; com 166 AMCs como zonas, DENTRO = 0 por construção."""
    ref = pd.read_csv(DIR_PROC / "centro_massa_deslocamento.csv")
    ref = ref[ref.ato == "LÍQUIDO"].set_index("variavel")["dnorte_km"]
    liq = tot[(tot.janela == "LÍQUIDO") & (tot.particao == "regiao3")].set_index("variavel")
    for v in ref.index:
        if abs(liq.loc[v, "total_N_km"] - ref[v]) > 1e-3:
            raise RuntimeError(f"ΔNorte de {v} ≠ #32 ({liq.loc[v, 'total_N_km']:.3f} × {ref[v]:.3f})")
    amc = tot[tot.particao == "amc166"]
    if not np.allclose(amc["dentro_N_km"], 0, atol=1e-9):
        raise RuntimeError("com 166 AMCs como zonas o termo DENTRO deveria ser zero")
    print(f"[conferência] ΔNorte LÍQUIDO = #32 nas {len(ref)} variáveis; "
          f"partição de 166 AMCs dá DENTRO = 0 (ENTRE = 100%), como exige a construção")


# ---------------------------------------------------------------------------
# 5. Incerteza: bootstrap i.i.d. (D19) e em blocos (#55)
# ---------------------------------------------------------------------------

def bootstrap_decomp(painel: pd.DataFrame, variaveis: dict, particoes: list[str]) -> pd.DataFrame:
    geo = painel.groupby("code_amc")[["cx", "cy"] + particoes].first()
    codes = geo.index.to_numpy()
    CX, CY = geo["cx"].to_numpy(), geo["cy"].to_numpy()
    XY = geo[["cx", "cy"]].to_numpy()
    anos = np.sort(painel["ano"].unique())
    idx = {int(a): j for j, a in enumerate(anos)}
    rng = np.random.default_rng(BOOT_SEED)

    linhas = []
    for k in GRADE_K:
        lab = kmeans_blocos(XY, k)
        kk = int(lab.max() + 1)
        cnt = rng.multinomial(kk, np.full(kk, 1.0 / kk), size=BOOT_B).astype(float)[:, lab]  # B×n
        for particao in particoes:
            zonas = sorted(geo[particao].unique())
            M = np.stack([(geo[particao] == z).to_numpy(float) for z in zonas], axis=1)     # n×Z
            for chave, (col, rot) in variaveis.items():
                W = (painel.pivot_table(index="code_amc", columns="ano", values=col, aggfunc="first")
                           .reindex(index=codes, columns=anos).to_numpy())
                W = np.where(np.isfinite(W) & (W > 0), W, 0.0)
                anos_ok = anos[W.sum(axis=0) > 0]
                for nome, a0, a1 in janelas():
                    a0e, a1e = max(a0, int(anos_ok[0])), min(a1, int(anos_ok[-1]))
                    if a0e >= a1e or (nome != "LÍQUIDO" and (a0e != a0 or a1e != a1)):
                        continue
                    est = []
                    for a in (a0e, a1e):
                        w = W[:, idx[a]]
                        A = cnt @ (w[:, None] * M)                        # B×Z
                        SX = cnt @ ((w * CX)[:, None] * M)
                        SY = cnt @ ((w * CY)[:, None] * M)
                        with np.errstate(invalid="ignore", divide="ignore"):
                            est.append((A / A.sum(axis=1, keepdims=True),
                                        np.where(A > 0, SX / A, np.nan),
                                        np.where(A > 0, SY / A, np.nan)))
                    (w0, x0, y0), (w1, x1, y1) = est
                    d = _decompor(w0, w1, x0, x1, y0, y1)
                    e = d["entre_N"].sum(axis=1) / 1e3
                    dn = d["dentro_N"].sum(axis=1) / 1e3
                    t = e + dn
                    with np.errstate(invalid="ignore", divide="ignore"):
                        f = e / t
                    reg = {"k_blocos": kk, "particao": particao, "variavel": chave,
                           "janela": nome, "ano_ini": a0e, "ano_fim": a1e}
                    for nomev, arr in [("total_N", t), ("entre_N", e), ("dentro_N", dn),
                                       ("frac_entre_N", f)]:
                        lo, hi = np.nanpercentile(arr, [2.5, 97.5])
                        reg[f"{nomev}_lo"], reg[f"{nomev}_hi"] = lo, hi
                    reg["total_exclui_zero"] = bool(reg["total_N_lo"] > 0 or reg["total_N_hi"] < 0)
                    reg["dentro_exclui_zero"] = bool(reg["dentro_N_lo"] > 0 or reg["dentro_N_hi"] < 0)
                    linhas.append(reg)
        print(f"[bootstrap] k={kk:3d} blocos concluído")
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 6. Sensibilidade à AMC dividida
# ---------------------------------------------------------------------------

def sensibilidade_amc_dividida(painel, variaveis, tot, res) -> pd.DataFrame:
    alt_tot = totais_decomp(decomposicao(painel, variaveis, ["regiao3_alt"]))
    alt_res = resumo_ancoragem(ancoragem(painel, variaveis, ["regiao3_alt"]))
    base = tot[(tot.particao == "regiao3") & (tot.janela == "LÍQUIDO")].set_index("variavel")
    alt = alt_tot[alt_tot.janela == "LÍQUIDO"].set_index("variavel")
    rb = res[(res.particao == "regiao3") & (res.janela == "LÍQUIDO")].set_index(["variavel", "zona"])
    ra = alt_res[alt_res.janela == "LÍQUIDO"].set_index(["variavel", "zona"])
    linhas = []
    print(f"\n[sensibilidade] AMC {AMC_DIVIDIDA} no Centro (canônico) × no Norte:")
    for v in base.index:
        dsh = (ra["influencia_share_mediana"] - rb["influencia_share_mediana"]).loc[v].abs().max()
        linhas.append({"variavel": v, "entre_N_base": base.loc[v, "entre_N_km"],
                       "entre_N_alt": alt.loc[v, "entre_N_km"],
                       "frac_entre_base": base.loc[v, "frac_entre_N"],
                       "frac_entre_alt": alt.loc[v, "frac_entre_N"],
                       "max_dif_share_pp": dsh * 100})
        print(f"  {v:20s} fração ENTRE {base.loc[v, 'frac_entre_N']*100:5.1f}% → "
              f"{alt.loc[v, 'frac_entre_N']*100:5.1f}% | maior Δ de share {dsh*100:4.1f} p.p.")
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 7. Figuras
# ---------------------------------------------------------------------------

VARS_FIG = ["pastagem", "bovinos", "agricultura", "veg_natural"]


def fig_puxao(anc: pd.DataFrame, variaveis: dict) -> None:
    import matplotlib.pyplot as plt
    sub = anc[anc.particao == "regiao3"]
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True, sharey=True)
    for ax, v in zip(axs.ravel(), VARS_FIG):
        for info in ATOS.values():
            ax.axvspan(info["inicio"] - .5, info["fim"] + .5, color="#000", alpha=.035 if
                       list(ATOS.values()).index(info) % 2 == 0 else 0, lw=0)
        ax.axhline(0, color="#888", lw=.8)
        g = sub[sub.variavel == v]
        for z in ORDEM_ZONAS["regiao3"]:
            s = g[g.zona == z].sort_values("ano")
            if s.empty:
                continue
            ax.plot(s.ano, s.puxao_norte_km, color=CORES_ZONA[z], lw=2)
            ax.annotate(z, (s.ano.iloc[-1], s.puxao_norte_km.iloc[-1]), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=9, color="#333")
        ax.set_title(variaveis[v][1], fontsize=11, loc="left")
        ax.grid(axis="y", color="#ddd", lw=.6)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    for ax in axs[:, 0]:
        ax.set_ylabel("Puxão sobre o centro (km; + = ao norte)")
    axs[0, 0].set_xlim(ANO_INI - 1, ANO_FIM + 6)
    fig.suptitle("Quanto cada região desloca o centro de massa de Goiás (centro com a região − centro sem ela)",
                 fontsize=11.5, x=.01, ha="left")
    fig.text(.01, .005, "Pipeline #58 · 3 regiões (Sul Goiano | Centro + Leste | Norte + Noroeste) · "
             "166 AMCs, EPSG:5880 · faixas cinza = Atos I e III", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, .02, 1, .96))
    arq = DIR_OUT / "ancoragem_puxao_norte.png"
    fig.savefig(arq, dpi=150)
    plt.close(fig)
    print(f"[fig] {arq.relative_to(ROOT)}")


def fig_decomposicao(tot: pd.DataFrame, ic: pd.DataFrame | None, variaveis: dict) -> None:
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})
    liq = tot[(tot.janela == "LÍQUIDO") & (tot.particao == "regiao3")].set_index("variavel")
    comps = [("total_N", "Deslocamento total", "#333333"),
             ("entre_N", "Troca de peso entre regiões", "#1565c0"),
             ("dentro_N", "Movimento dentro das regiões", "#90a4ae")]
    ys = np.arange(len(VARS_FIG))[::-1]
    for j, (c, lab, cor) in enumerate(comps):
        off = (1 - j) * .22
        val = liq.loc[VARS_FIG, f"{c}_km"].to_numpy()
        a1.scatter(val, ys + off, color=cor, s=46, zorder=3, label=lab)
        if ic is not None:
            r = ic[(ic.k_blocos == 166) & (ic.particao == "regiao3") & (ic.janela == "LÍQUIDO")] \
                .set_index("variavel").loc[VARS_FIG]
            a1.hlines(ys + off, r[f"{c}_lo"], r[f"{c}_hi"], color=cor, lw=1.6, zorder=2)
    a1.axvline(0, color="#888", lw=.8)
    a1.set_yticks(ys, [variaveis[v][1] for v in VARS_FIG])
    a1.set_xlabel("ΔNorte 1985→2024 (km)")
    a1.set_title("Decomposição do deslocamento (3 regiões, IC95% i.i.d.)", fontsize=10.5, loc="left")
    a1.legend(frameon=False, fontsize=8.5, loc="lower right")

    parts = ["regiao3", "faixa_lat4", "meso5", "amc166"]
    liq_all = tot[(tot.janela == "LÍQUIDO")]
    # Pontos soltos (sem linha): as partições não formam uma escala ordenada.
    # Cor do #32 + forma do marcador (vinho × magenta são próximos: a forma desambigua).
    estilo = {"pastagem": ("#e8920c", "o"), "bovinos": ("#7a1f1f", "s"), "agricultura": ("#c2185b", "^")}
    for i, v in enumerate(VARS_FIG[:3]):
        f = [liq_all[(liq_all.particao == p) & (liq_all.variavel == v)]["frac_entre_N"].iloc[0] * 100
             for p in parts]
        cor, mk = estilo[v]
        a2.scatter(np.arange(len(parts)) + (i - 1) * .16, f, color=cor, marker=mk, s=44,
                   zorder=3, label=variaveis[v][1])
    a2.legend(frameon=False, fontsize=8.5, loc="lower right")
    a2.set_xticks(range(len(parts)), [ROTULO_PARTICAO[p].replace(" de ", "\nde ") for p in parts],
                  fontsize=8.5)
    a2.set_xlim(-.5, len(parts) - .5)
    a2.set_ylim(0, 105)
    a2.set_ylabel("% do ΔNorte que é troca de peso")
    a2.set_title("A fração depende da escala das zonas", fontsize=10.5, loc="left")
    for ax in (a1, a2):
        ax.grid(axis="x" if ax is a1 else "y", color="#ddd", lw=.6)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    fig.text(.01, .01, "Pipeline #58 · decomposição simétrica (ponto médio), identidade exata · "
             "com 166 AMCs a fração é 100% por construção", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, .03, 1, 1))
    arq = DIR_OUT / "ancoragem_decomposicao.png"
    fig.savefig(arq, dpi=150)
    plt.close(fig)
    print(f"[fig] {arq.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------

def main(sem_figuras: bool = False, sem_bootstrap: bool = False) -> None:
    print("=" * 78)
    print("Pipeline #58 — Ancoragem e decomposição do centro de massa (AMC Goiás, 1985–2024)")
    print("=" * 78)
    painel, variaveis = carregar()
    conferir_com_32(painel, variaveis)

    part_anc = ["regiao3", "meso5", "faixa_lat4"]
    anc = ancoragem(painel, variaveis, part_anc)
    res = resumo_ancoragem(anc)
    dec = decomposicao(painel, variaveis, part_anc + ["amc166"])
    tot = totais_decomp(dec)
    conferir_totais(tot)
    print("[conferência] identidade LOO = Influência/(1 − peso) verificada em todas as linhas")

    anc.to_csv(ARQ_ANUAL, index=False, encoding="utf-8")
    res.to_csv(ARQ_RESUMO, index=False, encoding="utf-8")
    dec[dec.particao != "amc166"].to_csv(ARQ_DECOMP, index=False, encoding="utf-8")
    for a in (ARQ_ANUAL, ARQ_RESUMO, ARQ_DECOMP):
        print(f"[OK] {a.relative_to(ROOT)}")

    # --- Resumo na tela ---
    r = res[(res.particao == "regiao3") & (res.janela == "LÍQUIDO")]
    print("\nANCORAGEM — 3 regiões, 1985–2024 (mediana [IQR] entre anos)")
    for v in ["pastagem", "bovinos", "agricultura", "veg_natural", "agric_uniao_mosaico", "soja_sidra"]:
        print(f"  {variaveis[v][1]}")
        for z in ORDEM_ZONAS["regiao3"]:
            q = r[(r.variavel == v) & (r.zona == z)]
            if q.empty:
                continue
            q = q.iloc[0]
            print(f"    {z:7s} peso {q.peso_ini*100:3.0f}%→{q.peso_fim*100:3.0f}% | "
                  f"LOO {q.loo_km_mediana:6.1f} [{q.loo_km_q1:5.1f}–{q.loo_km_q3:5.1f}] km | "
                  f"puxão N {q.puxao_norte_ini_km:+7.1f}→{q.puxao_norte_fim_km:+7.1f} km | "
                  f"share {q.influencia_share_mediana*100:3.0f}%")

    print("\nDECOMPOSIÇÃO DO ΔNORTE (km) — ENTRE (troca de peso) + DENTRO; fração ENTRE por partição")
    for nome, _a0, _a1 in janelas():
        print(f"  [{nome}]")
        for v in ["pastagem", "bovinos", "agricultura", "veg_natural", "agric_uniao_mosaico", "soja_sidra"]:
            s = tot[(tot.variavel == v) & (tot.janela == nome)].set_index("particao")
            if "regiao3" not in s.index:
                continue
            b = s.loc["regiao3"]
            fr = " ".join(f"{p[:6]} {s.loc[p, 'frac_entre_N']*100:5.0f}%" for p in part_anc if p in s.index)
            print(f"    {variaveis[v][1]:24s} total {b.total_N_km:+7.1f} = entre {b.entre_N_km:+7.1f}"
                  f" + dentro {b.dentro_N_km:+6.1f} (encad. entre {b.entre_N_encadeado_km:+7.1f}) | {fr}")

    sens = sensibilidade_amc_dividida(painel, variaveis, tot, res)

    ic = None
    if not sem_bootstrap:
        ic = bootstrap_decomp(painel, variaveis, part_anc)
        ic = ic.merge(tot[["particao", "variavel", "janela", "total_N_km", "entre_N_km",
                           "dentro_N_km", "frac_entre_N"]], on=["particao", "variavel", "janela"])
        ic.to_csv(ARQ_DEC_IC, index=False, encoding="utf-8")
        print(f"[OK] {ARQ_DEC_IC.relative_to(ROOT)}")
        print("\nIC95% da fração ENTRE e do termo DENTRO (3 regiões, LÍQUIDO), por tamanho de bloco")
        q = ic[(ic.particao == "regiao3") & (ic.janela == "LÍQUIDO")]
        for v in ["pastagem", "bovinos", "agricultura", "veg_natural", "agric_uniao_mosaico", "soja_sidra"]:
            for _, x in q[q.variavel == v].iterrows():
                print(f"  {variaveis[v][1]:24s} k={x.k_blocos:3d} | total [{x.total_N_lo:+6.1f}; "
                      f"{x.total_N_hi:+6.1f}] | dentro [{x.dentro_N_lo:+6.1f}; {x.dentro_N_hi:+6.1f}]"
                      f"{'' if x.dentro_exclui_zero else ' inclui 0'} | fração entre "
                      f"[{x.frac_entre_N_lo*100:4.0f}%; {x.frac_entre_N_hi*100:4.0f}%]")

    if not sem_figuras:
        DIR_OUT.mkdir(parents=True, exist_ok=True)
        fig_puxao(anc, variaveis)
        fig_decomposicao(tot, ic, variaveis)
    return anc, res, tot, ic, sens


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sem-figuras", action="store_true", help="só CSVs")
    ap.add_argument("--sem-bootstrap", action="store_true", help="pula o IC (mais rápido)")
    main(**vars(ap.parse_args()))
