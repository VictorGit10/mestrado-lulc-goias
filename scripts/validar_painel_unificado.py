"""
Validação do Painel Unificado (Pipeline #16)
============================================

Pergunta central: a soma dos 246 valores municipais do painel reconstrói o
agregado de Goiás publicado pelas fontes originais (IBGE/SIDRA, MapBiomas,
BACEN)? Onde houver diferença, ela é esperada (recorte territorial, mudança
de unidade, decisão metodológica) ou anômala (erro real a investigar)?

Estratégia em 4 camadas:
    Camada 1 — Integridade interna do painel (shape, PK, cobertura, identidades).
    Camada 2 — Agregação municipal → UF contra gabaritos internos
               (data/processed/*goias*.csv) quando existem.
    Camada 3 — Agregação municipal → UF contra fonte original (SIDRA N3,
               SICOR UF) quando o gabarito interno não cobre a variável.
    Camada 4 — Validação cruzada entre fontes (MapBiomas × PAM para soja).

Saídas:
    outputs/diagnosticos/validacao_painel.csv          — linha por (bloco, variável, ano)
    outputs/diagnosticos/validacao_painel_resumo.csv   — pivot bloco × ano de % anômalas
    stdout                                              — resumo por flag + top 20 anomalias

Como rodar:
    python scripts/validar_painel_unificado.py

Exit code:
    0 se zero ANOMALA; >0 se houver pelo menos uma. Pronto para CI/Make.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT          = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_CACHE_UF  = ROOT / "data" / "cache" / "validacao_uf"
DIR_DIAG      = ROOT / "outputs" / "diagnosticos"
for d in (DIR_CACHE_UF, DIR_DIAG):
    d.mkdir(parents=True, exist_ok=True)

ANO_INI, ANO_FIM = 1985, 2024
CD_UF_GO = "52"

# Tolerâncias (fração absoluta de diff_rel). Acima disso → ANOMALA.
TOL_LULC      = 0.005   # 0,5 %
TOL_BOVINOS   = 0.001   # 0,1 %
TOL_PAM_PPM   = 0.005   # 0,5 %
TOL_PIB       = 0.010   # 1 %
TOL_SICOR     = 0.001   # 0,1 %
TOL_FOGO      = 0.020   # 2 %  (mesmo gabarito interno; tolerância folgada cobre arredondamento)
TOL_POP       = 0.001   # 0,1 %

# Referências documentais (para o campo `referencia_doc` no CSV)
DOC_TOCANTINS = "Textos/pipelines/16_painel_unificado.md §9 (pre-1989 GO inclui TO)"
DOC_PIB_X1000 = "Textos/pipelines/16_painel_unificado.md §3 (SIDRA 5938 Mil R$ → ×1000)"
DOC_CENSO_POP = "Textos/pipelines/16_painel_unificado.md (pop 2007/2010 NaN — IBGE não publica)"
DOC_LEITE     = "Textos/pipelines/16_painel_unificado.md §5 (PPM 74 classif 80 = leite)"
DOC_MOSAICO   = "Textos/metodologia/glossario_metricas.md (MapBiomas raster vs PAM autodeclarado)"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _diff_rel(painel: float, gabarito: float) -> float:
    """Diferença relativa (painel − gabarito) / gabarito. NaN se gabarito ≤ 0 ou NaN."""
    if gabarito is None or pd.isna(gabarito) or gabarito == 0:
        return np.nan
    return (painel - gabarito) / gabarito


def _registro(
    bloco: str, variavel: str, ano: int,
    soma_painel: float, gabarito: float,
    tolerancia: float,
    *,
    fonte_gabarito: str,
    pre1989_esperado: bool = False,
    doc_pre1989: str = DOC_TOCANTINS,
    flag_forcada: Optional[tuple[str, str]] = None,
) -> dict:
    """Constrói uma linha do CSV de validação com flag classificado."""
    dabs = soma_painel - gabarito if pd.notna(gabarito) and pd.notna(soma_painel) else np.nan
    drel = _diff_rel(soma_painel, gabarito)

    if flag_forcada is not None:
        flag, ref = flag_forcada
    elif pd.isna(drel):
        flag, ref = "SEM_GABARITO", ""
    elif pre1989_esperado and ano < 1989 and abs(drel) > tolerancia:
        flag, ref = "ESPERADA_TOCANTINS", doc_pre1989
    elif abs(drel) <= tolerancia:
        flag, ref = "OK", ""
    else:
        flag, ref = "ANOMALA", ""

    return {
        "bloco": bloco,
        "variavel": variavel,
        "ano": int(ano),
        "soma_painel": soma_painel,
        "gabarito": gabarito,
        "fonte_gabarito": fonte_gabarito,
        "diff_abs": dabs,
        "diff_rel": drel,
        "tolerancia": tolerancia,
        "flag": flag,
        "referencia_doc": ref,
    }


def _sidra_uf_cached(nome: str, **kwargs) -> pd.DataFrame:
    """Baixa série SIDRA para UF=52 (GO) com cache em data/cache/validacao_uf/<nome>.csv.

    `kwargs` vai direto para `sidrapy.get_table`. O cache não invalida — quem
    quiser refrescar deve apagar o CSV.
    """
    cache = DIR_CACHE_UF / f"{nome}.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype=str, keep_default_na=False)
    import sidrapy  # importado tarde para o script rodar offline quando o cache existe
    print(f"  [SIDRA UF] baixando {nome} ...", end=" ", flush=True)
    t0 = time.time()
    df = sidrapy.get_table(**kwargs)
    df.to_csv(cache, index=False)
    print(f"OK ({len(df):,} linhas, {time.time()-t0:.1f}s)")
    time.sleep(1.5)
    return df


def _parse_sidra_uf(df_raw: pd.DataFrame, valor_col: str = "V") -> pd.DataFrame:
    """Parser mínimo para SIDRA UF: descarta cabeçalho, extrai ano e valor."""
    df = df_raw.iloc[1:].copy()
    df["ano"] = pd.to_numeric(df["D2C"], errors="coerce").astype("Int64")
    df["valor"] = pd.to_numeric(df[valor_col].replace({"...": np.nan, "-": np.nan, "..": np.nan, "X": np.nan}), errors="coerce")
    return df.dropna(subset=["ano"])


# ---------------------------------------------------------------------------
# Camada 1 — Integridade interna
# ---------------------------------------------------------------------------

def validar_integridade(painel: pd.DataFrame) -> list[dict]:
    """Asserções estruturais. Retorna registros com flag OK/ANOMALA."""
    out = []
    # Shape exato
    n_lin = len(painel)
    out.append(_registro(
        "integridade", "n_linhas", 0, n_lin, 9840, 0,
        fonte_gabarito="246 munis × 40 anos",
        flag_forcada=("OK" if n_lin == 9840 else "ANOMALA", ""),
    ))
    # PK única
    n_dup = painel.duplicated(subset=["cd_mun", "ano"]).sum()
    out.append(_registro(
        "integridade", "duplicatas_pk", 0, n_dup, 0, 0,
        fonte_gabarito="PK (cd_mun, ano)",
        flag_forcada=("OK" if n_dup == 0 else "ANOMALA", ""),
    ))
    # Identidades aritméticas: lulc_agricultura_ha ≥ lulc_soja_ha (linha a linha onde ambos não-NaN)
    sub = painel.dropna(subset=["lulc_agricultura_ha", "lulc_soja_ha"])
    n_viol = (sub["lulc_soja_ha"] > sub["lulc_agricultura_ha"] + 1e-3).sum()
    out.append(_registro(
        "integridade", "soja<=agricultura", 0, n_viol, 0, 0,
        fonte_gabarito="lulc_soja_ha ≤ lulc_agricultura_ha",
        flag_forcada=("OK" if n_viol == 0 else "ANOMALA", ""),
    ))
    # Métricas derivadas sem Inf
    n_inf = np.isinf(painel.select_dtypes(include=[float])).sum().sum()
    out.append(_registro(
        "integridade", "valores_inf", 0, n_inf, 0, 0,
        fonte_gabarito="np.inf → NaN nos derivados",
        flag_forcada=("OK" if n_inf == 0 else "ANOMALA", ""),
    ))
    return out


# ---------------------------------------------------------------------------
# Camada 2 — Gabaritos internos (data/processed/*goias*.csv)
# ---------------------------------------------------------------------------

def validar_lulc(painel: pd.DataFrame) -> list[dict]:
    """LULC contra cobertura_goias_grupos.csv (em Mha) e pastagem_goias_anual.csv (ha).

    Gabarito vem do MESMO raw MapBiomas que alimenta o painel; o batimento deve
    ser exato em todos os anos. ATENÇÃO: o gabarito usa GRUPOS de classes (ver
    `analise_expandida_goias.py` linhas 64–70) que NÃO coincidem 1-para-1 com
    as colunas wide do painel. Daí o mapa abaixo somar várias colunas painel
    para reconstruir cada grupo do gabarito.

    Agricultura é PULADA aqui — gabarito usa class_ids [39, 19, 41, 20, 36]
    (Col antiga) e painel `lulc_agricultura_ha` usa [20, 39, 40, 41, 46, 47,
    48, 62] (Col 10.1, mais subclasses). Comparação direta produziria
    divergência definicional, não erro. A validação correta de
    `lulc_agricultura_ha` está em `validar_lulc_reagregacao` (Camada 1).
    """
    out = []
    cob = pd.read_csv(DIR_PROCESSED / "cobertura_goias_grupos.csv")
    past = pd.read_csv(DIR_PROCESSED / "pastagem_goias_anual.csv")

    # Cada chave do gabarito → lista de colunas do painel que somadas o
    # reconstroem. Ver GRUPOS em analise_expandida_goias.py.
    mapa_grupos = {
        "Pastagem":         ["lulc_pastagem_ha"],
        "Cerrado/Savana":   ["lulc_formacao_savanica_ha", "lulc_campo_nativo_ha"],
        "Floresta Nativa":  ["lulc_floresta_nativa_ha"],
        "Area Urbana":      ["lulc_area_urbana_ha"],
    }
    for ano in range(ANO_INI, ANO_FIM + 1):
        sub_p = painel[painel["ano"] == ano]
        for grupo_cob, cols_painel in mapa_grupos.items():
            if grupo_cob not in cob.columns:
                continue
            gab_mha = cob.loc[cob["ano"] == ano, grupo_cob]
            if gab_mha.empty:
                continue
            gab_ha = float(gab_mha.iloc[0]) * 1e6  # Mha → ha
            soma = sum(sub_p[c].sum(skipna=True) for c in cols_painel)
            out.append(_registro(
                "lulc", grupo_cob, ano, soma, gab_ha, TOL_LULC,
                fonte_gabarito="cobertura_goias_grupos.csv (MapBiomas)",
            ))

    # Pastagem em ha (gabarito redundante mas independente — sanity extra)
    for ano in range(ANO_INI, ANO_FIM + 1):
        gab = past.loc[past["ano"] == ano, "area_pastagem_ha"]
        if gab.empty:
            continue
        soma = painel.loc[painel["ano"] == ano, "lulc_pastagem_ha"].sum(skipna=True)
        out.append(_registro(
            "lulc", "pastagem_ha_independente", ano, soma, float(gab.iloc[0]), TOL_LULC,
            fonte_gabarito="pastagem_goias_anual.csv",
        ))
    return out


def validar_lulc_reagregacao(painel: pd.DataFrame) -> list[dict]:
    """Recalcula cada coluna LULC do painel diretamente do raw MapBiomas e
    compara — valida que `load_lulc` no Pipeline #16 não perdeu/duplicou
    classes. Espera-se 0% em todos os anos; qualquer divergência é ANOMALA.

    Replica o dicionário GRUPOS_LULC de `construir_painel_unificado.py`. Se
    aquele dicionário mudar e este não, esta validação acusa.
    """
    GRUPOS_LULC = {
        "lulc_floresta_nativa_ha":     [3],
        "lulc_formacao_savanica_ha":   [4],
        "lulc_silvicultura_ha":        [9],
        "lulc_campo_alagado_ha":       [11],
        "lulc_campo_nativo_ha":        [12],
        "lulc_pastagem_ha":            [15],
        "lulc_mosaico_usos_ha":        [21],
        "lulc_area_urbana_ha":         [24],
        "lulc_outras_nao_vegetadas_ha":[25, 29],
        "lulc_mineracao_ha":           [30],
        "lulc_aquicultura_ha":         [31],
        "lulc_corpo_dagua_ha":         [33],
        "lulc_soja_ha":                [39],
        "lulc_agricultura_ha":         [20, 39, 40, 41, 46, 47, 48, 62],
    }
    out = []
    raw = pd.read_csv(DIR_PROCESSED / "mapbiomas_munis_goias.csv")
    for ano in range(ANO_INI, ANO_FIM + 1):
        sub_r = raw[raw["ano"] == ano]
        sub_p = painel[painel["ano"] == ano]
        if sub_r.empty:
            continue
        for col, class_ids in GRUPOS_LULC.items():
            gab = sub_r[sub_r["class_id"].isin(class_ids)]["area_ha"].sum()
            soma = sub_p[col].sum(skipna=True)
            out.append(_registro(
                "lulc_reagreg", col, ano, soma, gab, TOL_LULC,
                fonte_gabarito="mapbiomas_munis_goias.csv (re-agregação)",
            ))
        # Area total = soma de todas as classes presentes
        gab_total = sub_r["area_ha"].sum()
        out.append(_registro(
            "lulc_reagreg", "lulc_area_total_ha", ano,
            sub_p["lulc_area_total_ha"].sum(skipna=True), gab_total, TOL_LULC,
            fonte_gabarito="mapbiomas_munis_goias.csv (todas as classes)",
        ))
    return out


def validar_bovinos_gabarito_interno(painel: pd.DataFrame) -> list[dict]:
    """Bovinos painel × rebanho_bovino_goias.csv.

    Gabarito interno foi gerado em algum momento por agregação SIDRA UF (e por
    isso reflete a definição histórica de Goiás, incluindo Tocantins pré-1989).
    Pré-1989: ESPERADA_TOCANTINS. Pós-1989: batimento exato.
    """
    out = []
    g = pd.read_csv(DIR_PROCESSED / "rebanho_bovino_goias.csv")
    for ano in range(ANO_INI, ANO_FIM + 1):
        gab = g.loc[g["ano"] == ano, "bovinos"]
        if gab.empty:
            continue
        soma = painel.loc[painel["ano"] == ano, "pec_bovinos_cab"].sum(skipna=True)
        out.append(_registro(
            "pec_gabarito", "bovinos_cab", ano, soma, float(gab.iloc[0]), TOL_BOVINOS,
            fonte_gabarito="rebanho_bovino_goias.csv",
            pre1989_esperado=True,
        ))
    return out


def validar_sicor(painel: pd.DataFrame) -> list[dict]:
    """SICOR painel × sicor_uf_anual.csv (somente Custeio + Investimento, nominais).

    O painel armazena valores reais (deflacionados). Para bater contra o UF
    nominal, deflacionamos o UF também usando o mesmo IPCA e base que o painel.
    """
    out = []
    uf = pd.read_csv(DIR_PROCESSED / "sicor_uf_anual.csv")
    # Soma anual UF Custeio + Investimento (Comercialização não está no painel)
    uf_an = (
        uf[uf["finalidade"].isin(["Custeio", "Investimento"])]
        .groupby(["ano", "finalidade"], as_index=False)["valor"].sum()
        .pivot(index="ano", columns="finalidade", values="valor")
        .reset_index()
    )

    # Deflator dez/2024 — replicar exatamente a lógica do painel
    ipca = pd.read_csv(DIR_PROCESSED / "sidra_1737_ipca.csv").dropna(subset=["indice_acum"])
    idx_base = ipca.loc[(ipca["ano"] == 2024) & (ipca["mes"] == 12), "indice_acum"].iloc[0]
    idx_dez = ipca[ipca["mes"] == 12][["ano", "indice_acum"]].rename(columns={"indice_acum": "idx_dez"})
    uf_an = uf_an.merge(idx_dez, on="ano", how="left")
    uf_an["custeio_real"] = uf_an["Custeio"] * (idx_base / uf_an["idx_dez"])
    uf_an["invest_real"]  = uf_an["Investimento"] * (idx_base / uf_an["idx_dez"])

    for _, row in uf_an.iterrows():
        ano = int(row["ano"])
        if ano > ANO_FIM:
            continue
        sub = painel[painel["ano"] == ano]
        out.append(_registro(
            "sicor", "custeio_real_rs", ano,
            sub["sicor_custeio_real_rs"].sum(), float(row["custeio_real"]),
            TOL_SICOR, fonte_gabarito="sicor_uf_anual.csv (deflacionado)",
        ))
        out.append(_registro(
            "sicor", "investimento_real_rs", ano,
            sub["sicor_investimento_real_rs"].sum(), float(row["invest_real"]),
            TOL_SICOR, fonte_gabarito="sicor_uf_anual.csv (deflacionado)",
        ))
        out.append(_registro(
            "sicor", "total_real_rs", ano,
            sub["sicor_total_real_rs"].sum(),
            float(row["custeio_real"] + row["invest_real"]),
            TOL_SICOR, fonte_gabarito="sicor_uf_anual.csv (deflacionado)",
        ))
    return out


def validar_fogo(painel: pd.DataFrame) -> list[dict]:
    """Fogo painel × fogo_mapbiomas_goias.csv (mesma fonte municipal → 0% esperado)."""
    out = []
    path = DIR_PROCESSED / "fogo_mapbiomas_goias.csv"
    if not path.exists():
        return out
    g = pd.read_csv(path)
    mapa = {
        "area_queimada_total_ha":       "fogo_total_ha",
        "area_queimada_veg_nat_ha":     "fogo_veg_nat_ha",
        "area_queimada_pastagem_ha":    "fogo_pastagem_ha",
        "area_queimada_agricultura_ha": "fogo_agricultura_ha",
        "area_queimada_mosaico_ha":     "fogo_mosaico_ha",
    }
    for ano in sorted(g["ano"].unique()):
        if not (ANO_INI <= ano <= ANO_FIM):
            continue
        sub_p = painel[painel["ano"] == ano]
        sub_g = g[g["ano"] == ano]
        for col_g, col_p in mapa.items():
            if col_g not in sub_g.columns or col_p not in sub_p.columns:
                continue
            out.append(_registro(
                "fogo", col_p, int(ano),
                sub_p[col_p].sum(skipna=True),
                float(sub_g[col_g].sum(skipna=True)),
                TOL_FOGO,
                fonte_gabarito="fogo_mapbiomas_goias.csv",
            ))
    return out


# ---------------------------------------------------------------------------
# Camada 3 — SIDRA UF (N3, GO)
# ---------------------------------------------------------------------------

def _serie_pam_uf(table_code: str, var_id: str, cat_id: int,
                  classif: str, ano_ini: int, ano_fim: int,
                  nome_cache: str) -> pd.DataFrame:
    """Baixa série anual UF de uma cultura PAM (área plantada ou produção)."""
    df_raw = _sidra_uf_cached(
        nome_cache,
        table_code=table_code,
        territorial_level="3",
        ibge_territorial_code=CD_UF_GO,
        period=f"{ano_ini}-{ano_fim}",
        variable=var_id,
        classifications={classif: str(cat_id)},
    )
    return _parse_sidra_uf(df_raw)


def validar_agri_pam(painel: pd.DataFrame) -> list[dict]:
    """PAM 1612/839 painel × SIDRA UF. Culturas-chave: soja, milho1, milho2, cana, feijão, algodão.

    Pré-1989: ESPERADA_TOCANTINS (SIDRA UF=52 historicamente inclui TO).
    """
    out = []
    culturas_1612 = {
        "soja":    (2713, "agri_soja"),
        "cana":    (2696, "agri_cana"),
        "feijao":  (2702, "agri_feijao"),
        "algodao": (2689, "agri_algodao"),
        "milho_total": (2711, "agri_milho_total"),
    }
    for nome, (cat, prefixo) in culturas_1612.items():
        # Área plantada (var 109) → ha
        try:
            df_area = _serie_pam_uf("1612", "109", cat, "81",
                                    1985, ANO_FIM, f"pam1612_uf_{nome}_area")
        except Exception as e:
            print(f"  [WARN] PAM 1612 UF {nome} área falhou: {e}")
            continue
        col_p = f"{prefixo}_ha_plantada"
        for _, row in df_area.iterrows():
            ano = int(row["ano"])
            soma = painel.loc[painel["ano"] == ano, col_p].sum(skipna=True)
            out.append(_registro(
                "agri", f"{nome}_ha_plantada", ano, soma, row["valor"],
                TOL_PAM_PPM,
                fonte_gabarito=f"SIDRA 1612 N3 var 109 cat {cat}",
                pre1989_esperado=True,
            ))
        # Quantidade produzida (var 214) → ton
        try:
            df_ton = _serie_pam_uf("1612", "214", cat, "81",
                                   1985, ANO_FIM, f"pam1612_uf_{nome}_ton")
        except Exception as e:
            print(f"  [WARN] PAM 1612 UF {nome} ton falhou: {e}")
            continue
        col_t = f"{prefixo}_ton"
        for _, row in df_ton.iterrows():
            ano = int(row["ano"])
            soma = painel.loc[painel["ano"] == ano, col_t].sum(skipna=True)
            out.append(_registro(
                "agri", f"{nome}_ton", ano, soma, row["valor"],
                TOL_PAM_PPM,
                fonte_gabarito=f"SIDRA 1612 N3 var 214 cat {cat}",
                pre1989_esperado=True,
            ))

    # PAM 839 — milho 1ª e 2ª safra (2003+)
    milho_839 = {"milho1": 114253, "milho2": 114254}
    for nome, cat in milho_839.items():
        try:
            df_area = _serie_pam_uf("839", "109", cat, "81",
                                    2003, ANO_FIM, f"pam839_uf_{nome}_area")
            df_ton = _serie_pam_uf("839", "214", cat, "81",
                                   2003, ANO_FIM, f"pam839_uf_{nome}_ton")
        except Exception as e:
            print(f"  [WARN] PAM 839 UF {nome} falhou: {e}")
            continue
        for _, row in df_area.iterrows():
            ano = int(row["ano"])
            soma = painel.loc[painel["ano"] == ano, f"agri_{nome}_ha_plantada"].sum(skipna=True)
            out.append(_registro(
                "agri", f"{nome}_ha_plantada", ano, soma, row["valor"],
                TOL_PAM_PPM, fonte_gabarito=f"SIDRA 839 N3 cat {cat}",
            ))
        for _, row in df_ton.iterrows():
            ano = int(row["ano"])
            soma = painel.loc[painel["ano"] == ano, f"agri_{nome}_ton"].sum(skipna=True)
            out.append(_registro(
                "agri", f"{nome}_ton", ano, soma, row["valor"],
                TOL_PAM_PPM, fonte_gabarito=f"SIDRA 839 N3 cat {cat}",
            ))
    return out


def validar_ppm_uf(painel: pd.DataFrame) -> list[dict]:
    """PPM 3939 painel × SIDRA UF para bovinos, suínos, galináceos.

    Pré-1989: ESPERADA_TOCANTINS.
    """
    out = []
    rebanhos = {
        "bovinos":    (2670, "pec_bovinos_cab"),
        "suinos":     (32794, "pec_suinos_cab"),
        "galinaceos": (32796, "pec_galinaceos_cab"),
    }
    for nome, (cat, col_p) in rebanhos.items():
        try:
            df_raw = _sidra_uf_cached(
                f"ppm3939_uf_{nome}",
                table_code="3939",
                territorial_level="3",
                ibge_territorial_code=CD_UF_GO,
                period=f"1985-{ANO_FIM}",
                variable="105",
                classifications={"79": str(cat)},
            )
            df = _parse_sidra_uf(df_raw)
        except Exception as e:
            print(f"  [WARN] PPM 3939 UF {nome} falhou: {e}")
            continue
        for _, row in df.iterrows():
            ano = int(row["ano"])
            soma = painel.loc[painel["ano"] == ano, col_p].sum(skipna=True)
            out.append(_registro(
                "pec_uf", f"{nome}_cab", ano, soma, row["valor"], TOL_PAM_PPM,
                fonte_gabarito=f"SIDRA 3939 N3 cat {cat}",
                pre1989_esperado=True,
            ))
    return out


def validar_pib(painel: pd.DataFrame) -> list[dict]:
    """PIB painel × pib_goias_real.csv (gabarito UF deflacionado).

    Testa o ×1000 e a deflação. Gabarito está em R$ deflacionados dez/2024.
    PIB municipal só existe 2002+.
    """
    out = []
    g = pd.read_csv(DIR_PROCESSED / "pib_goias_real.csv")
    g_agro = pd.read_csv(DIR_PROCESSED / "pib_agro_goias.csv")
    for _, row in g.iterrows():
        ano = int(row["ano"])
        if not (ANO_INI <= ano <= ANO_FIM):
            continue
        soma = painel.loc[painel["ano"] == ano, "pib_real_rs"].sum(skipna=True)
        out.append(_registro(
            "pib", "pib_real_rs", ano, soma, float(row["pib_real_rs"]), TOL_PIB,
            fonte_gabarito="pib_goias_real.csv",
        ))
    for _, row in g_agro.iterrows():
        ano = int(row["ano"])
        if not (ANO_INI <= ano <= ANO_FIM):
            continue
        soma = painel.loc[painel["ano"] == ano, "va_agro_real_rs"].sum(skipna=True)
        out.append(_registro(
            "pib", "va_agro_real_rs", ano, soma, float(row["va_agro_real_rs"]),
            TOL_PIB, fonte_gabarito="pib_agro_goias.csv",
        ))
    return out


def validar_populacao(painel: pd.DataFrame) -> list[dict]:
    """População painel × SIDRA 6579 N3 UF.

    Anos 2007 e 2010 são marcados como ESPERADA_CENSO (IBGE não publica
    estimativa nesses anos — usa Contagem 2007 e Censo 2010 respectivamente,
    com defasagem de publicação na série municipal).
    """
    out = []
    try:
        df_raw = _sidra_uf_cached(
            "pop6579_uf",
            table_code="6579",
            territorial_level="3",
            ibge_territorial_code=CD_UF_GO,
            period=f"2001-{ANO_FIM}",
            variable="9324",
        )
        df = _parse_sidra_uf(df_raw)
    except Exception as e:
        print(f"  [WARN] População UF falhou: {e}")
        return out
    for _, row in df.iterrows():
        ano = int(row["ano"])
        soma = painel.loc[painel["ano"] == ano, "populacao"].sum(skipna=True)
        n_nan = painel.loc[painel["ano"] == ano, "populacao"].isna().sum()
        if ano in (2007, 2010) and n_nan == 246:
            out.append(_registro(
                "populacao", "habitantes", ano, soma, row["valor"], TOL_POP,
                fonte_gabarito="SIDRA 6579 N3 var 9324",
                flag_forcada=("ESPERADA_CENSO", DOC_CENSO_POP),
            ))
        else:
            out.append(_registro(
                "populacao", "habitantes", ano, soma, row["valor"], TOL_POP,
                fonte_gabarito="SIDRA 6579 N3 var 9324",
            ))
    return out


# ---------------------------------------------------------------------------
# Camada 4 — Validações cruzadas
# ---------------------------------------------------------------------------

def validar_cruzada_soja(painel: pd.DataFrame) -> list[dict]:
    """Soja MapBiomas (lulc_soja_ha) × Soja PAM (agri_soja_ha_plantada).

    São fontes independentes para a mesma quantidade. Diferenças sistemáticas
    são esperadas (raster vs autodeclarado; MapBiomas inclui soja após colheita
    aparente em mosaicos). Reporta como CRUZADA_INFORMATIVA (sem flag de erro).
    """
    out = []
    for ano in range(2000, ANO_FIM + 1):
        sub = painel[painel["ano"] == ano]
        mapb = sub["lulc_soja_ha"].sum(skipna=True)
        pam = sub["agri_soja_ha_plantada"].sum(skipna=True)
        if pam <= 0:
            continue
        razao = mapb / pam
        # Tolerância folgada (50 %); fora disso flag como CRUZADA_DIVERGENTE.
        flag = ("CRUZADA_INFORMATIVA", DOC_MOSAICO) if 0.5 <= razao <= 1.5 else ("CRUZADA_DIVERGENTE", DOC_MOSAICO)
        out.append({
            "bloco": "cruzada",
            "variavel": "soja_mapbiomas_vs_pam",
            "ano": ano,
            "soma_painel": mapb,
            "gabarito": pam,
            "fonte_gabarito": "agri_soja_ha_plantada (PAM 1612)",
            "diff_abs": mapb - pam,
            "diff_rel": (mapb - pam) / pam,
            "tolerancia": 0.5,
            "flag": flag[0],
            "referencia_doc": flag[1],
        })
    return out


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 72)
    print("Validação do Painel Unificado — Pipeline #16")
    print("=" * 72)

    painel = pd.read_parquet(DIR_PROCESSED / "painel_unificado.parquet")
    print(f"[load] painel_unificado.parquet — {painel.shape[0]:,} × {painel.shape[1]}")

    blocos = []
    print("\n[1/8] Integridade interna")
    blocos += validar_integridade(painel)
    print("[2/8] LULC vs gabaritos internos (MapBiomas)")
    blocos += validar_lulc(painel)
    print("[2b]  LULC re-agregação direta do raw MapBiomas")
    blocos += validar_lulc_reagregacao(painel)
    print("[3/8] Bovinos vs rebanho_bovino_goias.csv")
    blocos += validar_bovinos_gabarito_interno(painel)
    print("[4/8] SICOR vs sicor_uf_anual.csv (deflacionado)")
    blocos += validar_sicor(painel)
    print("[5/8] Fogo vs fogo_mapbiomas_goias.csv")
    blocos += validar_fogo(painel)
    print("[6/8] PAM (soja, milho, cana, feijão, algodão) vs SIDRA UF")
    blocos += validar_agri_pam(painel)
    print("[7/8] PPM (bovinos, suínos, galináceos) vs SIDRA UF")
    blocos += validar_ppm_uf(painel)
    print("[7b]   PIB vs pib_goias_real.csv / pib_agro_goias.csv")
    blocos += validar_pib(painel)
    print("[7c]   População vs SIDRA UF")
    blocos += validar_populacao(painel)
    print("[8/8] Cruzada MapBiomas × PAM (soja)")
    blocos += validar_cruzada_soja(painel)

    df = pd.DataFrame(blocos)
    out_path = DIR_DIAG / "validacao_painel.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\n[OUT] {out_path.relative_to(ROOT)} — {len(df):,} linhas")

    # Resumo bloco × flag
    print("\n[RESUMO] Contagem por flag:")
    print(df["flag"].value_counts().to_string())

    print("\n[RESUMO] Cobertura por bloco:")
    pivot = df.pivot_table(
        index="bloco", columns="flag", values="variavel",
        aggfunc="count", fill_value=0,
    )
    print(pivot.to_string())

    # Resumo pivot bloco × ano
    df_alvo = df[df["bloco"] != "integridade"]
    resumo = df_alvo.groupby(["bloco", "ano"]).agg(
        n_total=("flag", "count"),
        n_anomala=("flag", lambda s: (s == "ANOMALA").sum()),
        n_esperada=("flag", lambda s: s.str.startswith("ESPERADA_").sum()),
        n_ok=("flag", lambda s: (s == "OK").sum()),
    ).reset_index()
    resumo["pct_anomala"] = resumo["n_anomala"] / resumo["n_total"] * 100
    resumo_path = DIR_DIAG / "validacao_painel_resumo.csv"
    resumo.to_csv(resumo_path, index=False, encoding="utf-8")
    print(f"\n[OUT] {resumo_path.relative_to(ROOT)} — {len(resumo):,} linhas")

    # Top 20 anomalias (ordenadas por |diff_rel| descendente)
    anomalias = df[df["flag"] == "ANOMALA"].copy()
    if len(anomalias):
        anomalias["abs_diff_rel"] = anomalias["diff_rel"].abs()
        top = anomalias.sort_values("abs_diff_rel", ascending=False).head(20)
        print(f"\n[ANOMALIAS] {len(anomalias)} total — top 20:")
        cols_show = ["bloco", "variavel", "ano", "soma_painel", "gabarito", "diff_rel", "fonte_gabarito"]
        print(top[cols_show].to_string(index=False))
    else:
        print("\n[ANOMALIAS] Nenhuma — todas as divergências são esperadas, OK, ou sem gabarito.")

    return 0 if len(anomalias) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
