"""
coleta_sidra.py — Coletor unificado SIDRA/IBGE para a dissertação CIAMB-UFG
============================================================================

Baixa todas as tabelas SIDRA relevantes do plano-mestre, no nível MUNICIPAL
(246 municípios de Goiás), com cache local em CSV para evitar re-downloads.

Tabelas cobertas:
  - PAM 1612 — Lavouras temporárias (soja, milho, sorgo, cana, etc.)
  - PAM 1613 — Lavouras permanentes (café, citrus, banana)
  - PAM 839  — Milho 1ª e 2ª safras (2003–2024)
  - PPM 3939 — Efetivo de rebanhos (bovinos, suínos, ovinos, caprinos)
  - PPM 74   — Produção de leite
  - PPM 94   — Produção de ovos de galinha
  - 5938     — PIB municipal e Valor Adicionado por setor
  - 6579     — População residente (estimativas anuais)
  - 1737     — IPCA mensal (deflator)

Saída:
  - data/raw/sidra/<nome>.csv     — bruto, schema SIDRA original
  - data/processed/sidra_<nome>.csv — limpo, schema padronizado

Schema padronizado: [cd_mun, nm_mun, ano, variavel_id, variavel, unidade,
                     categoria_id, categoria, valor]

Como rodar:
    python coleta_sidra.py            # baixa o que faltar (usa cache)
    python coleta_sidra.py --force    # ignora cache e rebaixa tudo
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import sidrapy

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
UF_NOME        = "Goiás"
UF_SIGLA       = "GO"
UF_CODIGO_IBGE = "52"
N_MUNICIPIOS_GO = 246

ROOT           = Path(__file__).resolve().parent.parent
DIR_RAW_SIDRA = ROOT / "data" / "raw" / "sidra"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW_SIDRA, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

# "in n3 52" = todos os municípios cuja UF (n3) é 52 (Goiás).
# Sintaxe documentada em https://servicodados.ibge.gov.br/api/docs/agregados.
TERRITORIO_MUNI_GO = "in n3 52"

# Códigos SIDRA — VALIDADOS contra a API de metadados em 2026-04-26
# https://servicodados.ibge.gov.br/api/v3/agregados/<tab>/metadados

# PAM 1612 — Lavouras temporárias (variável 215 omitida: muda de moeda
# entre Cruzeiros/Cruzados/Reais; 112 omitida: derivável de 214/216).
PAM1612_VARIAVEIS = {
    "109": ("Área plantada", "ha"),
    "216": ("Área colhida", "ha"),
    "214": ("Quantidade produzida", "t"),
}
# Classification 81 = Produto das lavouras temporárias
PAM1612_PRODUTOS = {
    "2688": "Abacaxi",
    "40471": "Alfafa fenada",
    "2689": "Algodão herbáceo (em caroço)",
    "2690": "Alho",
    "2691": "Amendoim (em casca)",
    "2692": "Arroz (em casca)",
    "2693": "Aveia (em grão)",
    "2694": "Batata-doce",
    "2695": "Batata-inglesa",
    "2696": "Cana-de-açúcar",
    "40470": "Cana para forragem",
    "2697": "Cebola",
    "2698": "Centeio (em grão)",
    "2699": "Cevada (em grão)",
    "2700": "Ervilha (em grão)",
    "2701": "Fava (em grão)",
    "2702": "Feijão (em grão)",
    "2703": "Fumo (em folha)",
    "109179": "Girassol (em grão)",
    "2704": "Juta (fibra)",
    "2705": "Linho (semente)",
    "2706": "Malva (fibra)",
    "2707": "Mamona (baga)",
    "2708": "Mandioca",
    "2709": "Melancia",
    "2710": "Melão",
    "2711": "Milho (em grão)",
    "2712": "Rami (fibra)",
    "2713": "Soja (em grão)",
    "2714": "Sorgo (em grão)",
    "2715": "Tomate",
    "2716": "Trigo (em grão)",
    "109180": "Triticale (em grão)",
}

# PAM 1613 — Lavouras permanentes (mesmo critério de variáveis)
PAM1613_VARIAVEIS = {
    "2313": ("Área destinada à colheita", "ha"),
    "216":  ("Área colhida", "ha"),
    "214":  ("Quantidade produzida", "t"),
}
# Classification 82 = Produto das lavouras permanentes
PAM1613_PRODUTOS = {
    "2717": "Abacate",
    "2718": "Algodão arbóreo (em caroço)",
    "45981": "Açaí",
    "2719": "Azeitona",
    "2720": "Banana (cacho)",
    "2721": "Borracha (látex coagulado)",
    "40472": "Borracha (látex líquido)",
    "2722": "Cacau (em amêndoa)",
    "2723": "Café (em grão) Total",
    "31619": "Café (em grão) Arábica",
    "31620": "Café (em grão) Canephora",
    "40473": "Caju",
    "2724": "Caqui",
    "2725": "Castanha de caju",
    "2726": "Chá-da-índia (folha verde)",
    "2727": "Coco-da-baía",
    "2728": "Dendê (cacho de coco)",
    "2729": "Erva-mate (folha verde)",
    "2730": "Figo",
    "2731": "Goiaba",
    "2732": "Guaraná (semente)",
    "2733": "Laranja",
    "2734": "Limão",
    "2735": "Maçã",
    "2736": "Mamão",
    "2737": "Manga",
    "2738": "Maracujá",
    "2739": "Marmelo",
    "2740": "Noz (fruto seco)",
    "90001": "Palmito",
    "2741": "Pera",
    "2742": "Pêssego",
    "2743": "Pimenta-do-reino",
    "2744": "Sisal ou agave (fibra)",
    "2745": "Tangerina",
    "2746": "Tungue (fruto seco)",
    "2747": "Urucum (semente)",
    "2748": "Uva",
}

# PPM 3939 — Efetivo de rebanhos. Classification 79 = Tipo de rebanho.
# Foco no que importa para a tese (bovino + alternativas pecuárias).
PPM3939_REBANHOS = {
    "2670":  "Bovino",
    "32794": "Suíno - total",
    "2675":  "Bubalino",
    "2672":  "Equino",
    "2677":  "Ovino",
    "2681":  "Caprino",
    "32796": "Galináceos - total",
}

# PAM 839 — Milho 1ª e 2ª safras (municipal, 2003–2024)
# Classification 81 = Produto das lavouras temporárias
# Categorias validadas via API em 2026-04-30:
#   114253 = Milho (em grão) - 1ª safra
#   114254 = Milho (em grão) - 2ª safra
PAM839_VARIAVEIS = {
    "109": ("Área plantada", "ha"),
    "216": ("Área colhida", "ha"),
    "214": ("Quantidade produzida", "t"),
    "112": ("Rendimento médio", "kg/ha"),
}
PAM839_SAFRAS = {
    "114253": "Milho (em grão) - 1ª safra",
    "114254": "Milho (em grão) - 2ª safra",
}

# PPM 74 — Produção de leite (variável 106 = Quantidade, mil litros)
# PPM 94 — Produção de ovos de galinha (variável 100 = Quantidade, mil dúzias)

# 5938 — PIB municipal (códigos validados em 2026-04-26)
#  37   = PIB a preços correntes
#  498  = VA bruto total
#  543  = Impostos líquidos de subsídios sobre produtos
#  513  = VA Agropecuária
#  517  = VA Indústria
#  6575 = VA Serviços (excl. Adm. Pública)
#  525  = VA Adm. Pública, defesa, educação, saúde e seg. social
TAB_5938_VARIAVEIS = ["37", "498", "543", "513", "517", "6575", "525"]

# 6579 — População residente (estimativas anuais 2001+)
# Variável 9324 = População residente estimada

# ---------------------------------------------------------------------------
# Núcleo: chamada SIDRA com cache em CSV + paginação por janelas de anos
# ---------------------------------------------------------------------------

# Limite oficial da API SIDRA: 50k valores por chamada. Deixamos margem.
SIDRA_LIMITE_VALORES = 50_000
SIDRA_MARGEM = 45_000

def _get_sidra_cached(
    nome: str,
    *,
    force: bool = False,
    sleep: float = 1.5,
    **kwargs,
) -> pd.DataFrame:
    """
    Wrapper de sidrapy.get_table com cache local em CSV.
    `nome` é só rótulo de arquivo. Demais kwargs vão direto pra sidrapy.get_table.
    """
    arquivo = DIR_RAW_SIDRA / f"{nome}.csv"
    if arquivo.exists() and not force:
        df = pd.read_csv(arquivo, dtype=str, keep_default_na=False)
        print(f"  [cache] {nome}.csv ({len(df):,} linhas)")
        return df

    print(f"  [...] baixando {nome} ...")
    t0 = time.time()
    df = sidrapy.get_table(**kwargs)
    dt = time.time() - t0
    df.to_csv(arquivo, index=False)
    print(f"  [OK] {nome}.csv ({len(df):,} linhas, {dt:.1f}s)")
    if sleep > 0:
        time.sleep(sleep)  # cortesia para a API SIDRA
    return df


def _quebrar_periodo(
    ano_ini: int, ano_fim: int, *,
    n_munis: int = N_MUNICIPIOS_GO,
    n_vars: int = 1,
    n_cats: int = 1,
    max_valores: int = SIDRA_MARGEM,
) -> list[str]:
    """
    Retorna lista de strings 'AAAA,AAAA,...' tal que cada chamada SIDRA
    fique sob `max_valores`. Cada string vira o argumento `period`.
    """
    valores_por_ano = n_munis * n_vars * n_cats
    anos_por_janela = max(1, max_valores // valores_por_ano)
    anos = list(range(ano_ini, ano_fim + 1))
    return [
        ",".join(str(a) for a in anos[i:i + anos_por_janela])
        for i in range(0, len(anos), anos_por_janela)
    ]


def _get_sidra_paginated(
    nome_base: str,
    *,
    ano_ini: int,
    ano_fim: int,
    n_vars: int,
    n_cats: int,
    force: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Faz chamadas SIDRA paginadas em janelas de anos (calculadas para
    caber no limite de 50k valores) e concatena. Cada janela é cacheada
    separadamente em data/raw/sidra/<nome_base>_pNN.csv.
    """
    janelas = _quebrar_periodo(ano_ini, ano_fim, n_vars=n_vars, n_cats=n_cats)
    print(f"  janelas: {len(janelas)} chamadas "
          f"({ano_ini}–{ano_fim}, ~{len(janelas[0].split(','))} anos/chamada)")
    dfs = []
    for i, periodo in enumerate(janelas):
        nome_chunk = f"{nome_base}_p{i:02d}"
        df = _get_sidra_cached(
            nome_chunk, force=force, period=periodo, **kwargs,
        )
        # Cabeçalho do SIDRA (linha 0) é repetido em cada chunk; só mantemos um
        if i > 0 and len(df) > 0:
            df = df.iloc[1:]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def _padronizar_municipal(
    df_raw: pd.DataFrame,
    classif_col: Optional[str] = None,
    classif_nome: Optional[str] = None,
    var_col: str = "D3C",
) -> pd.DataFrame:
    """
    Recebe o DataFrame bruto do SIDRA (com primeira linha-cabeçalho repetida) e
    devolve schema canônico [cd_mun, nm_mun, ano, variavel_id, variavel,
    unidade, categoria_id, categoria, valor].

    `classif_col` é o nome da coluna SIDRA com o código da classificação extra
    (ex: "D4C" para PAM/PPM). Se None, deixa categoria_id/nome em branco.

    `var_col` é a coluna SIDRA que contém o id da variável; default "D3C".
    Algumas tabelas (ex: PPM 74 com classificação 80) trocam a ordem de
    dimensões e colocam a variável em D4.
    """
    df = df_raw.iloc[1:].copy()  # remove linha-cabeçalho do SIDRA

    out = pd.DataFrame()
    out["cd_mun"] = pd.to_numeric(df["D1C"], errors="coerce").astype("Int64")
    out["nm_mun"] = (
        df["D1N"]
        .astype(str)
        .str.replace(r"\s*-\s*GO$", "", regex=True)
        .str.strip()
    )
    out["ano"] = pd.to_numeric(df["D2C"], errors="coerce").astype("Int64")
    var_name_col = var_col.replace("C", "N")
    out["variavel_id"] = df[var_col].astype(str)
    out["variavel"] = df[var_name_col].astype(str)
    out["unidade"] = df["MN"].astype(str)
    if classif_col and classif_col in df.columns:
        out["categoria_id"] = df[classif_col].astype(str)
        out["categoria"] = df[classif_col.replace("C", "N")].astype(str)
    else:
        out["categoria_id"] = ""
        out["categoria"] = classif_nome or ""

    # Valor: SIDRA usa ".." (não disponível) e "-" (zero/n.a.). Vira NaN.
    out["valor"] = pd.to_numeric(
        df["V"].replace({"..": pd.NA, "-": pd.NA, "...": pd.NA, "X": pd.NA}),
        errors="coerce",
    )

    out = out.dropna(subset=["cd_mun", "ano"]).reset_index(drop=True)
    out["cd_mun"] = out["cd_mun"].astype(int)
    out["ano"] = out["ano"].astype(int)
    return out


# ---------------------------------------------------------------------------
# Coletores específicos por tabela
# ---------------------------------------------------------------------------

def coletar_pam1612(force: bool = False) -> pd.DataFrame:
    """PAM 1612 — Lavouras temporárias por município de Goiás (8 culturas-chave)."""
    print("\n[PAM 1612] Lavouras temporárias")
    variaveis = ",".join(PAM1612_VARIAVEIS.keys())
    produtos = ",".join(PAM1612_PRODUTOS.keys())
    df_raw = _get_sidra_paginated(
        "pam1612_temporarias",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=len(PAM1612_VARIAVEIS), n_cats=len(PAM1612_PRODUTOS),
        table_code="1612",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable=variaveis,
        classifications={"81": produtos},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_pam1612_temporarias.csv", index=False)
    print(f"  -> sidra_pam1612_temporarias.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_pam1613(force: bool = False) -> pd.DataFrame:
    """PAM 1613 — Lavouras permanentes."""
    print("\n[PAM 1613] Lavouras permanentes")
    variaveis = ",".join(PAM1613_VARIAVEIS.keys())
    produtos = ",".join(PAM1613_PRODUTOS.keys())
    df_raw = _get_sidra_paginated(
        "pam1613_permanentes",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=len(PAM1613_VARIAVEIS), n_cats=len(PAM1613_PRODUTOS),
        table_code="1613",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable=variaveis,
        classifications={"82": produtos},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_pam1613_permanentes.csv", index=False)
    print(f"  -> sidra_pam1613_permanentes.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ppm3939(force: bool = False) -> pd.DataFrame:
    """PPM 3939 — Efetivo de rebanhos por município, várias espécies."""
    print("\n[PPM 3939] Efetivo de rebanhos")
    rebanhos = ",".join(PPM3939_REBANHOS.keys())
    df_raw = _get_sidra_paginated(
        "ppm3939_rebanhos",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=1, n_cats=len(PPM3939_REBANHOS),
        table_code="3939",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable="105",
        classifications={"79": rebanhos},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_ppm3939_rebanhos.csv", index=False)
    print(f"  -> sidra_ppm3939_rebanhos.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ppm74_leite(force: bool = False) -> pd.DataFrame:
    """PPM 74 — Produção de leite (mil litros).

    A variável 106 ("Produção de origem animal") só retorna valor quando
    combinada com a classificação 80 (Tipo de produto), categoria 2682 (Leite).
    Sem isso, o endpoint devolve apenas a variável 215 (Valor da produção em
    moedas históricas mistas), que é incomparável ao longo do tempo.
    """
    print("\n[PPM 74] Produção de leite")
    df_raw = _get_sidra_paginated(
        "ppm74_leite",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=2, n_cats=1,
        table_code="74",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        classifications={"80": "2682"},
    )
    df = _padronizar_municipal(df_raw, classif_nome="Leite", var_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_ppm74_leite.csv", index=False)
    print(f"  -> sidra_ppm74_leite.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ppm94_ovos(force: bool = False) -> pd.DataFrame:
    """PPM 94 — Produção de ovos de galinha (mil dúzias)."""
    print("\n[PPM 94] Produção de ovos")
    df_raw = _get_sidra_paginated(
        "ppm94_ovos",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=2, n_cats=1,
        table_code="94",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
    )
    df = _padronizar_municipal(df_raw, classif_nome="Ovos de galinha")
    df.to_csv(DIR_PROCESSED / "sidra_ppm94_ovos.csv", index=False)
    print(f"  -> sidra_ppm94_ovos.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_pib_municipal(force: bool = False) -> pd.DataFrame:
    """5938 — PIB e VA setoriais por município (disponível 2002+)."""
    print("\n[5938] PIB municipal e VA setoriais")
    variaveis = ",".join(TAB_5938_VARIAVEIS)
    df_raw = _get_sidra_paginated(
        "tab5938_pib_municipal",
        force=force,
        ano_ini=2002, ano_fim=2024,
        n_vars=len(TAB_5938_VARIAVEIS), n_cats=1,
        table_code="5938",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable=variaveis,
    )
    df = _padronizar_municipal(df_raw, classif_nome="PIB/VA")
    df.to_csv(DIR_PROCESSED / "sidra_5938_pib_municipal.csv", index=False)
    print(f"  -> sidra_5938_pib_municipal.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_populacao(force: bool = False) -> pd.DataFrame:
    """6579 — Estimativas anuais de população residente (2001+)."""
    print("\n[6579] População residente estimada")
    df_raw = _get_sidra_paginated(
        "tab6579_populacao",
        force=force,
        ano_ini=2001, ano_fim=2024,
        n_vars=1, n_cats=1,
        table_code="6579",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
    )
    df = _padronizar_municipal(df_raw, classif_nome="População residente")
    df.to_csv(DIR_PROCESSED / "sidra_6579_populacao.csv", index=False)
    print(f"  -> sidra_6579_populacao.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ipca(force: bool = False) -> pd.DataFrame:
    """1737 — IPCA mensal Brasil. Único deflator nacional, não é municipal."""
    print("\n[1737] IPCA mensal (Brasil)")
    df_raw = _get_sidra_cached(
        "tab1737_ipca",
        force=force,
        table_code="1737",
        territorial_level="1",
        ibge_territorial_code="all",
        period="all",
        variable="63",
    )
    df = df_raw.iloc[1:].copy()
    df["ano"] = df["D2C"].str[:4].astype(int)
    df["mes"] = df["D2C"].str[4:6].astype(int)
    df["var_mensal_pct"] = pd.to_numeric(df["V"], errors="coerce")
    df = df.sort_values(["ano", "mes"]).reset_index(drop=True)
    df["fator_mensal"] = 1 + df["var_mensal_pct"] / 100
    df["indice_acum"] = df["fator_mensal"].cumprod()
    out = df[["ano", "mes", "var_mensal_pct", "indice_acum"]]
    out.to_csv(DIR_PROCESSED / "sidra_1737_ipca.csv", index=False)
    print(f"  -> sidra_1737_ipca.csv ({len(out):,} linhas, "
          f"{out['ano'].min()}/{out['mes'].min():02d}–{out['ano'].max()}/{out['mes'].max():02d})")
    return out


def coletar_ppm95_ovinos_tosquiados(force: bool = False) -> pd.DataFrame:
    """PPM 95 — Ovinos tosquiados (cabeças)."""
    print("\n[PPM 95] Ovinos tosquiados")
    df_raw = _get_sidra_paginated(
        "ppm95_ovinos_tosquiados",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=1, n_cats=1,
        table_code="95",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable="108",
    )
    df = _padronizar_municipal(df_raw, classif_nome="Ovinos tosquiados")
    df.to_csv(DIR_PROCESSED / "sidra_ppm95_ovinos_tosquiados.csv", index=False)
    print(f"  -> sidra_ppm95_ovinos_tosquiados.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ppm74_mel(force: bool = False) -> pd.DataFrame:
    """PPM 74 — Produção de mel de abelha (quilogramas)."""
    print("\n[PPM 74] Produção de mel de abelha")
    df_raw = _get_sidra_paginated(
        "ppm74_mel",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=2, n_cats=1,
        table_code="74",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        classifications={"80": "2687"},
    )
    df = _padronizar_municipal(df_raw, classif_nome="Mel de abelha", var_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_ppm74_mel.csv", index=False)
    print(f"  -> sidra_ppm74_mel.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_ppm74_la(force: bool = False) -> pd.DataFrame:
    """PPM 74 — Produção de lã (quilogramas)."""
    print("\n[PPM 74] Produção de lã")
    df_raw = _get_sidra_paginated(
        "ppm74_la",
        force=force,
        ano_ini=1974, ano_fim=2024,
        n_vars=2, n_cats=1,
        table_code="74",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        classifications={"80": "2684"},
    )
    df = _padronizar_municipal(df_raw, classif_nome="Lã", var_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_ppm74_la.csv", index=False)
    print(f"  -> sidra_ppm74_la.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def coletar_pam839_safrinha(force: bool = False) -> pd.DataFrame:
    """PAM 839 — Milho 1ª e 2ª safras por município de Goiás (2003–2024)."""
    print("\n[PAM 839] Milho 1ª e 2ª safras")
    variaveis = ",".join(PAM839_VARIAVEIS.keys())
    safras = ",".join(PAM839_SAFRAS.keys())
    df_raw = _get_sidra_paginated(
        "pam839_milho_safras",
        force=force,
        ano_ini=2003, ano_fim=2024,
        n_vars=len(PAM839_VARIAVEIS), n_cats=len(PAM839_SAFRAS),
        table_code="839",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        variable=variaveis,
        classifications={"81": safras},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_pam839_milho_safras.csv", index=False)
    print(f"  -> sidra_pam839_milho_safras.csv ({len(df):,} linhas, "
          f"{df['ano'].min()}–{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

COLETORES = [
    ("PAM 1612 (lavouras temporárias)",   coletar_pam1612),
    ("PAM 1613 (lavouras permanentes)",   coletar_pam1613),
    ("PAM 839 (milho safras)",           coletar_pam839_safrinha),
    ("PPM 3939 (rebanhos)",               coletar_ppm3939),
    ("PPM 74 (leite)",                    coletar_ppm74_leite),
    ("PPM 74 (mel)",                      coletar_ppm74_mel),
    ("PPM 74 (lã)",                       coletar_ppm74_la),
    ("PPM 94 (ovos)",                     coletar_ppm94_ovos),
    ("PPM 95 (ovinos tosquiados)",        coletar_ppm95_ovinos_tosquiados),
    ("Tab 5938 (PIB municipal)",          coletar_pib_municipal),
    ("Tab 6579 (população)",              coletar_populacao),
    ("Tab 1737 (IPCA — deflator)",        coletar_ipca),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true",
        help="Ignora o cache e rebaixa todas as tabelas",
    )
    parser.add_argument(
        "--so", nargs="+", default=None,
        help="Roda só os coletores cujo nome contenha alguma destas substrings "
             "(case-insensitive). Ex: --so 1612 5938",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"Coleta SIDRA — {UF_NOME} ({N_MUNICIPIOS_GO} municípios)")
    print(f"  raw     -> {DIR_RAW_SIDRA}")
    print(f"  limpo   -> {DIR_PROCESSED}")
    print(f"  cache   -> {'OFF (--force)' if args.force else 'ON'}")
    print("=" * 70)

    resumo = []
    for label, fn in COLETORES:
        if args.so and not any(s.lower() in label.lower() for s in args.so):
            continue
        try:
            df = fn(force=args.force)
            resumo.append({
                "tabela": label,
                "linhas": len(df),
                "anos": (
                    f"{df['ano'].min()}–{df['ano'].max()}"
                    if "ano" in df.columns and len(df) else "-"
                ),
                "municipios": df["cd_mun"].nunique() if "cd_mun" in df.columns else "-",
                "status": "OK",
            })
        except Exception as e:
            resumo.append({
                "tabela": label, "linhas": 0, "anos": "-",
                "municipios": "-", "status": f"ERRO: {type(e).__name__}: {e}",
            })
            print(f"  [ERRO] {label}: {e}", file=sys.stderr)

    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(pd.DataFrame(resumo).to_string(index=False))


# ---------------------------------------------------------------------------
# Censo Agro 2017 — tabelas transversais (1 período = 2017)
# ---------------------------------------------------------------------------
# IDs validados contra https://servicodados.ibge.gov.br/api/v3/agregados/<id>/metadados
# em 2026-04-27.
#
# Escopo: subconjunto temático focado nos eixos da dissertação (LULC × estrutura
# produtiva). Cada tabela é coletada com classificações-chave no nível "Total"
# + quebras relevantes (tipologia familiar/não-familiar, tipo de insumo, etc.).
#
# Saída principal: sidra_censo_agro_2017.csv (1 linha/município, colunas wide).

# --- Classificações comuns (presentes em quase todas as tabelas) ---
TIPOLOGIA_TOTAL = "46302"
TIPOLOGIA_FAMILIAR_SIM = "46304"
TIPOLOGIA_FAMILIAR_NAO = "46303"
TIPOLOGIA_TODAS = f"{TIPOLOGIA_TOTAL},{TIPOLOGIA_FAMILIAR_SIM},{TIPOLOGIA_FAMILIAR_NAO}"

ATIVIDADE_TOTAL = "113601"  # Grupos de atividade econômica — Total

# Tabela 6878 — Estrutura fundiária (estab + área)
CENSO_6878_VARIAVEIS = {"183": "n_estabelecimentos", "184": "area_estabelecimentos_ha"}

# Tabela 6884 — Pessoal ocupado
CENSO_6884_VARIAVEIS = {"10099": "n_estab_com_pessoal", "185": "pessoal_ocupado"}

# Tabela 6870 — Tratores
CENSO_6870_VARIAVEIS = {"1918": "n_estab_com_tratores", "1862": "n_tratores"}

# Tabela 6848 — Adubação (classificação 12522 = Uso de adubação)
ADUBACAO_CATEGORIAS = {
    "46545": "total",
    "46546": "fez_adubacao",
    "46547": "adubacao_quimica",
    "46548": "adubacao_organica",
    "46549": "adubacao_quimica_e_organica",
    "46550": "nao_fez_adubacao",
}

# Tabela 6851 — Agrotóxicos (classificação 12521 = Uso de agrotóxicos)
AGROTOXICOS_CATEGORIAS = {
    "46556": "total",
    "111611": "utilizou_agrotoxicos",
    "111612": "nao_utilizou_agrotoxicos",
}

# Tabela 6910 — Bovinos
CENSO_6910_VARIAVEIS = {
    "2326": "n_estab_com_bovinos",
    "2057": "n_cabecas_bovinos",
    "9741": "n_vacas_reprodutoras",
}

# Tabela 6958 — Lavouras temporárias (classificação 226 = Produtos)
LAVOURA_TEMP_PRODUTOS = {
    "4896": "soja",
    "4888": "milho",
    "4857": "cana_acucar",
}
CENSO_6958_VARIAVEIS = {
    "10084": "n_estab_com_lavoura",
    "10089": "area_colhida_ha",
    "10087": "valor_producao_mil_reais",
}


def coletar_censo_6878(force: bool = False) -> pd.DataFrame:
    """6878 — Estrutura fundiária: nº estabelecimentos + área, por tipologia."""
    print("\n[6878] Estrutura fundiária (Censo Agro 2017)")
    df_raw = _get_sidra_cached(
        "censo_6878_estrutura_fundiaria",
        force=force,
        table_code="6878",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="183,184",
        classifications={"829": TIPOLOGIA_TODAS, "12517": ATIVIDADE_TOTAL},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6878_estrutura.csv", index=False)
    print(f"  -> sidra_censo_6878_estrutura.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6884(force: bool = False) -> pd.DataFrame:
    """6884 — Pessoal ocupado, por tipologia."""
    print("\n[6884] Pessoal ocupado (Censo Agro 2017)")
    df_raw = _get_sidra_cached(
        "censo_6884_pessoal_ocupado",
        force=force,
        table_code="6884",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="10099,185",
        classifications={"829": TIPOLOGIA_TODAS, "2": "0", "12517": ATIVIDADE_TOTAL},
    )
    df = _padronizar_municipal(df_raw, classif_col="D4C")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6884_pessoal.csv", index=False)
    print(f"  -> sidra_censo_6884_pessoal.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6870(force: bool = False) -> pd.DataFrame:
    """6870 — Tratores: nº estabelecimentos com tratores + nº tratores."""
    print("\n[6870] Tratores (Censo Agro 2017)")
    df_raw = _get_sidra_cached(
        "censo_6870_tratores",
        force=force,
        table_code="6870",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="1918,1862",
        classifications={"829": TIPOLOGIA_TOTAL, "12605": "113521", "12517": ATIVIDADE_TOTAL},
    )
    df = _padronizar_municipal(df_raw, classif_nome="Tratores")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6870_tratores.csv", index=False)
    print(f"  -> sidra_censo_6870_tratores.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6848(force: bool = False) -> pd.DataFrame:
    """6848 — Adubação: nº estabelecimentos por tipo de adubação."""
    print("\n[6848] Adubação (Censo Agro 2017)")
    adub_ids = ",".join(ADUBACAO_CATEGORIAS.keys())
    df_raw = _get_sidra_cached(
        "censo_6848_adubacao",
        force=force,
        table_code="6848",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="183",
        classifications={"829": TIPOLOGIA_TOTAL, "12522": adub_ids},
    )
    df = _padronizar_municipal(df_raw, classif_col="D5C")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6848_adubacao.csv", index=False)
    print(f"  -> sidra_censo_6848_adubacao.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6851(force: bool = False) -> pd.DataFrame:
    """6851 — Agrotóxicos: nº estabelecimentos por uso."""
    print("\n[6851] Agrotóxicos (Censo Agro 2017)")
    agro_ids = ",".join(AGROTOXICOS_CATEGORIAS.keys())
    df_raw = _get_sidra_cached(
        "censo_6851_agrotoxicos",
        force=force,
        table_code="6851",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="183",
        classifications={"829": TIPOLOGIA_TOTAL, "12521": agro_ids},
    )
    df = _padronizar_municipal(df_raw, classif_col="D5C")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6851_agrotoxicos.csv", index=False)
    print(f"  -> sidra_censo_6851_agrotoxicos.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6910(force: bool = False) -> pd.DataFrame:
    """6910 — Bovinos: nº estabelecimentos + efetivo + vacas reprodutoras."""
    print("\n[6910] Bovinos (Censo Agro 2017)")
    df_raw = _get_sidra_cached(
        "censo_6910_bovinos",
        force=force,
        table_code="6910",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable="2326,2057,9741",
        classifications={"829": TIPOLOGIA_TOTAL, "3244": "0", "12517": ATIVIDADE_TOTAL},
    )
    df = _padronizar_municipal(df_raw, classif_nome="Bovinos")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6910_bovinos.csv", index=False)
    print(f"  -> sidra_censo_6910_bovinos.csv ({len(df):,} linhas)")
    return df


def coletar_censo_6958(force: bool = False) -> pd.DataFrame:
    """6958 — Lavouras temporárias: estabelecimentos + área colhida (soja, milho, cana)."""
    print("\n[6958] Lavouras temporárias - soja, milho, cana (Censo Agro 2017)")
    prod_ids = ",".join(LAVOURA_TEMP_PRODUTOS.keys())
    var_ids = ",".join(CENSO_6958_VARIAVEIS.keys())
    df_raw = _get_sidra_cached(
        "censo_6958_lavouras_temp",
        force=force,
        table_code="6958",
        territorial_level="6",
        ibge_territorial_code=TERRITORIO_MUNI_GO,
        period="2017",
        variable=var_ids,
        classifications={"829": TIPOLOGIA_TOTAL, "226": prod_ids},
    )
    df = _padronizar_municipal(df_raw, classif_col="D5C")
    df.to_csv(DIR_PROCESSED / "sidra_censo_6958_lavouras.csv", index=False)
    print(f"  -> sidra_censo_6958_lavouras.csv ({len(df):,} linhas)")
    return df


# ---------------------------------------------------------------------------
# Montar painel wide do Censo Agro (1 linha/município)
# ---------------------------------------------------------------------------

def montar_painel_censo_agro(force: bool = False) -> pd.DataFrame:
    """
    Coleta as 7 tabelas do Censo Agro e monta um painel wide-format
    (1 linha por município) em sidra_censo_agro_2017.csv.
    """
    # Coletar todas as tabelas
    df_est = coletar_censo_6878(force=force)
    df_pes = coletar_censo_6884(force=force)
    df_tra = coletar_censo_6870(force=force)
    df_adu = coletar_censo_6848(force=force)
    df_agr = coletar_censo_6851(force=force)
    df_bov = coletar_censo_6910(force=force)
    df_lav = coletar_censo_6958(force=force)

    # Começar com a lista de municípios
    munis = (
        df_est[["cd_mun", "nm_mun"]]
        .drop_duplicates()
        .sort_values("cd_mun")
        .reset_index(drop=True)
    )

    def pivot_long(df: pd.DataFrame, prefix: str, cat_map: dict | None = None) -> pd.DataFrame:
        """Pivot long→wide para uma tabela do Censo Agro."""
        rows = []
        for _, row in df.iterrows():
            base = {"cd_mun": row["cd_mun"]}
            var_id = row["variavel_id"]
            cat_id = str(row.get("categoria_id", ""))
            col_name = f"{prefix}_{var_id}"
            if cat_map and cat_id in cat_map:
                col_name = f"{prefix}_{cat_map[cat_id]}"
            elif cat_id and cat_id != "":
                col_name = f"{prefix}_{var_id}_{cat_id}"
            base[col_name] = row["valor"]
            rows.append(base)
        if not rows:
            return pd.DataFrame({"cd_mun": munis["cd_mun"]})
        out = pd.DataFrame(rows)
        # Aggregate duplicates (same cd_mun + col_name → sum, which is correct for totals)
        out = out.groupby("cd_mun").first().reset_index()
        return out

    # Estrutura fundiária — separar por tipologia
    # Tipologia IDs: 46302=Total, 46303=Fam-não, 46304=Fam-sim
    tipologia_map = {"46302": "total", "46303": "fam_nao", "46304": "fam_sim"}
    wide_est_rows = []
    for _, row in df_est.iterrows():
        tip = tipologia_map.get(str(row.get("categoria_id", "")), "total")
        var_key = CENSO_6878_VARIAVEIS.get(str(row["variavel_id"]), str(row["variavel_id"]))
        col_name = f"ca_{var_key}_{tip}"
        wide_est_rows.append({"cd_mun": row["cd_mun"], col_name: row["valor"]})
    wide_est = pd.DataFrame(wide_est_rows).groupby("cd_mun").first().reset_index()

    # Pessoal ocupado — por tipologia
    wide_pes_rows = []
    for _, row in df_pes.iterrows():
        tip = tipologia_map.get(str(row.get("categoria_id", "")), "total")
        var_key = CENSO_6884_VARIAVEIS.get(str(row["variavel_id"]), str(row["variavel_id"]))
        col_name = f"ca_{var_key}_{tip}"
        wide_pes_rows.append({"cd_mun": row["cd_mun"], col_name: row["valor"]})
    wide_pes = pd.DataFrame(wide_pes_rows).groupby("cd_mun").first().reset_index()

    # Tratores
    wide_tra = pivot_long(df_tra, "ca", cat_map=None)
    wide_tra.columns = [
        f"ca_{CENSO_6870_VARIAVEIS.get(c.replace('ca_', ''), c)}"
        if c.replace('ca_', '') in CENSO_6870_VARIAVEIS else c
        for c in wide_tra.columns
    ]

    # Adubação
    wide_adu_rows = []
    for _, row in df_adu.iterrows():
        cat_key = ADUBACAO_CATEGORIAS.get(str(row.get("categoria_id", "")), str(row.get("categoria_id", "")))
        col_name = f"ca_n_estab_adubacao_{cat_key}"
        wide_adu_rows.append({"cd_mun": row["cd_mun"], col_name: row["valor"]})
    wide_adu = pd.DataFrame(wide_adu_rows).groupby("cd_mun").first().reset_index()

    # Agrotóxicos
    wide_agr_rows = []
    for _, row in df_agr.iterrows():
        cat_key = AGROTOXICOS_CATEGORIAS.get(str(row.get("categoria_id", "")), str(row.get("categoria_id", "")))
        col_name = f"ca_n_estab_agrotoxicos_{cat_key}"
        wide_agr_rows.append({"cd_mun": row["cd_mun"], col_name: row["valor"]})
    wide_agr = pd.DataFrame(wide_agr_rows).groupby("cd_mun").first().reset_index()

    # Bovinos
    wide_bov = pivot_long(df_bov, "ca", cat_map=None)
    wide_bov.columns = [
        f"ca_{CENSO_6910_VARIAVEIS.get(c.replace('ca_', ''), c)}"
        if c.replace('ca_', '') in CENSO_6910_VARIAVEIS else c
        for c in wide_bov.columns
    ]

    # Lavouras temporárias
    wide_lav_rows = []
    for _, row in df_lav.iterrows():
        prod_key = LAVOURA_TEMP_PRODUTOS.get(str(row.get("categoria_id", "")), str(row.get("categoria_id", "")))
        var_key = CENSO_6958_VARIAVEIS.get(str(row["variavel_id"]), str(row["variavel_id"]))
        col_name = f"ca_{var_key}_{prod_key}"
        wide_lav_rows.append({"cd_mun": row["cd_mun"], col_name: row["valor"]})
    wide_lav = pd.DataFrame(wide_lav_rows).groupby("cd_mun").first().reset_index()

    # Merge all wide tables
    painel = munis.copy()
    for wide in [wide_est, wide_pes, wide_tra, wide_adu, wide_agr, wide_bov, wide_lav]:
        if "cd_mun" in wide.columns and len(wide.columns) > 1:
            painel = painel.merge(wide, on="cd_mun", how="left")

    # Derivar variáveis úteis
    if "ca_n_estabelecimentos_total" in painel.columns and "ca_area_estabelecimentos_ha_total" in painel.columns:
        painel["ca_area_media_estab_ha"] = (
            painel["ca_area_estabelecimentos_ha_total"] / painel["ca_n_estabelecimentos_total"]
        )
    if "ca_n_estab_adubacao_total" in painel.columns and "ca_n_estab_adubacao_fez_adubacao" in painel.columns:
        painel["ca_pct_adubacao"] = (
            painel["ca_n_estab_adubacao_fez_adubacao"]
            / painel["ca_n_estab_adubacao_total"] * 100
        ).round(2)
    if "ca_n_estab_agrotoxicos_total" in painel.columns and "ca_n_estab_agrotoxicos_utilizou_agrotoxicos" in painel.columns:
        painel["ca_pct_agrotoxicos"] = (
            painel["ca_n_estab_agrotoxicos_utilizou_agrotoxicos"]
            / painel["ca_n_estab_agrotoxicos_total"] * 100
        ).round(2)
    if "ca_n_estab_com_bovinos" in painel.columns and "ca_n_estabelecimentos_total" in painel.columns:
        painel["ca_pct_estab_com_bovinos"] = (
            painel["ca_n_estab_com_bovinos"]
            / painel["ca_n_estabelecimentos_total"] * 100
        ).round(2)
    if "ca_n_cabecas_bovinos" in painel.columns and "ca_area_estabelecimentos_ha_total" in painel.columns:
        painel["ca_lotacao_censo_bov_ha"] = (
            painel["ca_n_cabecas_bovinos"]
            / painel["ca_area_estabelecimentos_ha_total"]
        ).round(4)
    if "ca_n_estab_com_tratores" in painel.columns and "ca_n_estabelecimentos_total" in painel.columns:
        painel["ca_pct_estab_com_tratores"] = (
            painel["ca_n_estab_com_tratores"]
            / painel["ca_n_estabelecimentos_total"] * 100
        ).round(2)
    if "ca_n_estabelecimentos_fam_sim" in painel.columns and "ca_n_estabelecimentos_total" in painel.columns:
        painel["ca_pct_familiar"] = (
            painel["ca_n_estabelecimentos_fam_sim"]
            / painel["ca_n_estabelecimentos_total"] * 100
        ).round(2)

    painel.to_csv(DIR_PROCESSED / "sidra_censo_agro_2017.csv", index=False)
    n_cols = len(painel.columns)
    print(f"\n  -> sidra_censo_agro_2017.csv ({len(painel):,} linhas, {n_cols} colunas)")
    return painel


COLETORES_CENSO_AGRO = [
    ("6878 (estrutura fundiária)",  coletar_censo_6878),
    ("6884 (pessoal ocupado)",      coletar_censo_6884),
    ("6870 (tratores)",             coletar_censo_6870),
    ("6848 (adubação)",            coletar_censo_6848),
    ("6851 (agrotóxicos)",         coletar_censo_6851),
    ("6910 (bovinos)",             coletar_censo_6910),
    ("6958 (lavouras temporárias)", coletar_censo_6958),
]


def main_censo_agro(force: bool = False) -> None:
    """Coleta o Censo Agro 2017 e monta o painel wide."""
    print("=" * 70)
    print("Coleta SIDRA — Censo Agropecuário 2017")
    print(f"  raw     -> {DIR_RAW_SIDRA}")
    print(f"  limpo   -> {DIR_PROCESSED}")
    print(f"  cache   -> {'OFF (--force)' if force else 'ON'}")
    print("=" * 70)

    resumo = []
    for label, fn in COLETORES_CENSO_AGRO:
        try:
            df = fn(force=force)
            resumo.append({"tabela": label, "linhas": len(df), "municipios": df["cd_mun"].nunique(), "status": "OK"})
        except Exception as e:
            resumo.append({"tabela": label, "linhas": 0, "municipios": "-", "status": f"ERRO: {e}"})
            print(f"  [ERRO] {label}: {e}", file=sys.stderr)

    print("\n[Montando painel wide...]")
    painel = montar_painel_censo_agro(force=force)

    print("\n" + "=" * 70)
    print("RESUMO Censo Agro 2017")
    print("=" * 70)
    print(pd.DataFrame(resumo).to_string(index=False))
    print(f"\nPainel consolidado: {len(painel)} municípios × {len(painel.columns)} colunas")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Ignora o cache e rebaixa tudo")
    parser.add_argument("--so", nargs="+", default=None,
                        help="Roda só os coletores cujo nome contenha alguma destas substrings")
    parser.add_argument("--censo-agro", action="store_true",
                        help="Roda só o bloco do Censo Agro 2017")
    args = parser.parse_args()

    if args.censo_agro:
        main_censo_agro(force=args.force)
    else:
        main()
