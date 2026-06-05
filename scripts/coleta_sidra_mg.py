"""coleta_sidra_mg.py — Coleta dados SIDRA/IBGE para Minas Gerais (UF=31, 853 municípios)

Importa o módulo coleta_sidra.py e sobrescreve constantes/funções para MG.
Escreve CSVs com sufixo _mg em data/processed/.

Problemas corrigidos em relação à versão anterior:
  - Parâmetros default (N_MUNICIPIOS_GO, TERRITORIO_MUNI_GO) eram capturados
    na definição da função, então monkey-patch não funcionava.
  - _padronizar_municipal removia " - GO" em vez de " - MG".
  - Renome de arquivos colidia com _mg já existentes.
  - PAM 1612/1613 excedem 50k valores para 853 municípios; agora paginam por produto.
  - Encoding Unicode no Windows.

Uso:
    python coleta_sidra_mg.py            # baixa o que faltar
    python coleta_sidra_mg.py --force    # rebaixa tudo
    python coleta_sidra_mg.py --so 1612  # só PAM 1612
    python coleta_sidra_mg.py --abate    # só abate (UF)
    python coleta_sidra_mg.py --censo-agro  # só Censo Agro 2017
"""
from __future__ import annotations

import argparse
import math
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd
import sidrapy

# ─── Constantes MG ───────────────────────────────────────────────────────────
UF_NOME_MG        = "Minas Gerais"
UF_SIGLA_MG        = "MG"
UF_CODIGO_IBGE_MG  = "31"
N_MUNICIPIOS_MG    = 853
TERRITORIO_MUNI_MG = "in n3 31"

ROOT               = Path(__file__).resolve().parent.parent
DIR_RAW_SIDRA_MG   = ROOT / "data" / "raw" / "sidra_mg"
DIR_PROCESSED       = ROOT / "data" / "processed"
SUFIXO              = "_mg"

DIR_RAW_SIDRA_MG.mkdir(parents=True, exist_ok=True)
DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

# ─── Importar módulo original ────────────────────────────────────────────────
ORIGINAL = Path(__file__).resolve().parent / "coleta_sidra.py"

import importlib.util
_spec = importlib.util.spec_from_file_location("coleta_sidra", str(ORIGINAL))
coleta = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coleta)

# ─── Monkey-patch constantes do módulo ───────────────────────────────────────
# Estes são lookup em __dict__ do módulo, então funcionam quando
# referenciados dentro de funções via LOAD_GLOBAL.
coleta.UF_NOME           = UF_NOME_MG
coleta.UF_SIGLA          = UF_SIGLA_MG
coleta.UF_CODIGO_IBGE    = UF_CODIGO_IBGE_MG
coleta.N_MUNICIPIOS_GO   = N_MUNICIPIOS_MG
coleta.TERRITORIO_MUNI_GO = TERRITORIO_MUNI_MG
coleta.DIR_RAW_SIDRA     = DIR_RAW_SIDRA_MG
coleta.DIR_PROCESSED      = DIR_PROCESSED

# ─── Substituir _padronizar_municipal para strip " - MG" ──────────────────────
def _padronizar_municipal_mg(
    df_raw: pd.DataFrame,
    classif_col: str | None = None,
    classif_nome: str | None = None,
    var_col: str = "D3C",
) -> pd.DataFrame:
    """Igual ao original, mas remove sufixo ' - MG' dos nomes de município."""
    df = df_raw.iloc[1:].copy()
    out = pd.DataFrame()
    out["cd_mun"] = pd.to_numeric(df["D1C"], errors="coerce").astype("Int64")
    out["nm_mun"] = (
        df["D1N"]
        .astype(str)
        .str.replace(r"\s*-\s*MG$", "", regex=True)
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

    out["valor"] = pd.to_numeric(
        df["V"].replace({"..": pd.NA, "-": pd.NA, "...": pd.NA, "X": pd.NA}),
        errors="coerce",
    )
    out = out.dropna(subset=["cd_mun", "ano"]).reset_index(drop=True)
    out["cd_mun"] = out["cd_mun"].astype(int)
    out["ano"] = out["ano"].astype(int)
    return out

coleta._padronizar_municipal = _padronizar_municipal_mg

# ─── Substituir _quebrar_periodo com default correto (853 munis) ─────────────
_original_quebrar = coleta._quebrar_periodo

def _quebrar_periodo_mg(
    ano_ini, ano_fim, *,
    n_munis=N_MUNICIPIOS_MG,
    n_vars=1,
    n_cats=1,
    max_valores=coleta.SIDRA_MARGEM,
):
    return _original_quebrar(
        ano_ini, ano_fim,
        n_munis=n_munis, n_vars=n_vars, n_cats=n_cats, max_valores=max_valores,
    )

coleta._quebrar_periodo = _quebrar_periodo_mg

# ─── Substituir _padronizar_estadual_trimestral para MG ──────────────────────
def _padronizar_estadual_trimestral_mg(
    df_raw: pd.DataFrame,
    especie: str,
) -> pd.DataFrame:
    """Igual ao original, mas rótulo usa MG em vez de GO."""
    df = df_raw.iloc[1:].copy()
    out = pd.DataFrame()
    out["uf_cod"] = pd.to_numeric(df["D1C"], errors="coerce").astype("Int64")
    out["uf_nome"] = df["D1N"].astype(str).str.strip()
    out["ano_trimestre"] = df["D2C"].astype(str)
    out["ano"] = out["ano_trimestre"].str[:4].astype(int)
    out["trimestre"] = out["ano_trimestre"].str[4:6].astype(int)
    out["variavel_id"] = df["D3C"].astype(str)
    out["variavel"] = df["D3N"].astype(str)
    out["unidade"] = df["MN"].astype(str)
    out["especie"] = especie
    out["valor"] = pd.to_numeric(
        df["V"].replace({"..": pd.NA, "-": pd.NA, "...": pd.NA, "X": pd.NA}),
        errors="coerce",
    )
    out = out.dropna(subset=["uf_cod", "ano"]).reset_index(drop=True)
    out["uf_cod"] = out["uf_cod"].astype(int)
    out["ano"] = out["ano"].astype(int)
    out["trimestre"] = out["trimestre"].astype(int)
    return out

coleta._padronizar_estadual_trimestral = _padronizar_estadual_trimestral_mg

# ─── Coletores PAM customizados (paginação por produto) ───────────────────────
# Com 853 municípios, PAM 1612 (3 vars × 28 produtos) e PAM 1613 (3 vars × 32
# produtos) excedem o limite de 50k valores mesmo para 1 ano. Solução: paginar
# por produto, fazendo chamadas separadas para cada lote de ~15 produtos.

SIDRA_LIMITE = 50_000
SIDRA_MARGEM_PAM = 42_000  # margem de segurança


def _coletar_pam_por_lote(
    table_code: str,
    nome_base: str,
    *,
    ano_ini: int,
    ano_fim: int,
    variaveis: dict[str, tuple[str, str]],
    produtos: dict[str, str],
    classif_id: str,
    force: bool = False,
) -> pd.DataFrame:
    """Coleta tabela PAM paginando por lote de produtos (para MG com 853 munis)."""
    n_vars = len(variaveis)
    n_munis = N_MUNICIPIOS_MG
    vars_str = ",".join(variaveis.keys())

    # Calcular quantos produtos cabem por chamada
    valores_por_produto_ano = n_vars * n_munis
    produtos_por_lote = max(1, SIDRA_MARGEM_PAM // (valores_por_produto_ano * (ano_fim - ano_ini + 1)))
    # Se não couber nem 1 produto para o período inteiro, paginar por ano tb
    if produtos_por_lote < 1:
        produtos_por_lote = max(1, SIDRA_MARGEM_PAM // valores_por_produto_ano)

    # Dividir produtos em lotes
    prod_items = list(produtos.items())
    lotes = [prod_items[i:i + produtos_por_lote] for i in range(0, len(prod_items), produtos_por_lote)]

    print(f"  PAM {table_code}: {len(produtos)} produtos em {len(lotes)} lote(s) "
          f"(~{produtos_por_lote} produtos/lote, {n_munis} munis)")

    dfs = []
    for i, lote in enumerate(lotes):
        lote_dict = dict(lote)
        lote_str = ",".join(lote_dict.keys())
        lote_n_cats = len(lote_dict)

        # Paginar por anos se necessário
        anos_por_janela = max(1, SIDRA_MARGEM_PAM // (n_vars * lote_n_cats * n_munis))
        anos = list(range(ano_ini, ano_fim + 1))
        janelas = [
            ",".join(str(a) for a in anos[j:j + anos_por_janela])
            for j in range(0, len(anos), anos_por_janela)
        ]
        print(f"  Lote {i+1}/{len(lotes)}: {len(lote_dict)} produtos, "
              f"{len(janelas)} janela(s) de anos")

        for ji, periodo in enumerate(janelas):
            nome_chunk = f"{nome_base}_l{i:02d}_p{ji:02d}"
            try:
                df_raw = coleta._get_sidra_paginated(
                    nome_chunk,
                    force=force,
                    ano_ini=ano_ini, ano_fim=ano_fim,
                    n_vars=n_vars, n_cats=lote_n_cats,
                    table_code=table_code,
                    territorial_level="6",
                    ibge_territorial_code=TERRITORIO_MUNI_MG,
                    variable=vars_str,
                    classifications={classif_id: lote_str},
                    period=periodo,
                )
            except Exception as e:
                # Se o _get_sidra_paginated não aceitar period, tentar sem
                print(f"    [AVISO] Tentando sem period explícito: {e}")
                try:
                    df_chunk = coleta._get_sidra_cached(
                        nome_chunk,
                        force=force,
                        table_code=table_code,
                        territorial_level="6",
                        ibge_territorial_code=TERRITORIO_MUNI_MG,
                        variable=vars_str,
                        classifications={classif_id: lote_str},
                        period=periodo,
                    )
                    # Remove linha de cabeçalho duplicada
                    if ji > 0 and len(df_chunk) > 0:
                        df_chunk = df_chunk.iloc[1:]
                    dfs.append(df_chunk)
                    continue
                except Exception as e2:
                    print(f"    [ERRO] Lote {i+1}, janela {ji+1}: {e2}")
                    continue

            dfs.append(df_raw)

    if not dfs:
        print(f"  [ERRO] Nenhum dado coletado para PAM {table_code}")
        return pd.DataFrame()

    df_raw_all = pd.concat(dfs, ignore_index=True)
    df = _padronizar_municipal_mg(df_raw_all, classif_col="D4C")
    return df


# Substituir os coletores PAM no módulo original
def _coletar_pam1612_mg(force: bool = False) -> pd.DataFrame:
    """PAM 1612 — Lavouras temporárias por município de MG (com paginação por produto)."""
    print("\n[PAM 1612] Lavouras temporárias (MG, paginado por produto)")
    df = _coletar_pam_por_lote(
        "1612", "pam1612_temporarias_mg",
        ano_ini=1974, ano_fim=2024,
        variaveis=coleta.PAM1612_VARIAVEIS,
        produtos=coleta.PAM1612_PRODUTOS,
        classif_id="81",
        force=force,
    )
    if df.empty:
        return df
    out = DIR_PROCESSED / f"sidra_pam1612_temporarias{SUFIXO}.csv"
    df.to_csv(out, index=False)
    print(f"  -> {out.name} ({len(df):,} linhas, "
          f"{df['ano'].min()}-{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


def _coletar_pam1613_mg(force: bool = False) -> pd.DataFrame:
    """PAM 1613 — Lavouras permanentes por município de MG (com paginação por produto)."""
    print("\n[PAM 1613] Lavouras permanentes (MG, paginado por produto)")
    df = _coletar_pam_por_lote(
        "1613", "pam1613_permanentes_mg",
        ano_ini=1974, ano_fim=2024,
        variaveis=coleta.PAM1613_VARIAVEIS,
        produtos=coleta.PAM1613_PRODUTOS,
        classif_id="82",
        force=force,
    )
    if df.empty:
        return df
    out = DIR_PROCESSED / f"sidra_pam1613_permanentes{SUFIXO}.csv"
    df.to_csv(out, index=False)
    print(f"  -> {out.name} ({len(df):,} linhas, "
          f"{df['ano'].min()}-{df['ano'].max()}, {df['cd_mun'].nunique()} munis)")
    return df


# PAM 839 (milho safras) também pode precisar de paginação por produto
# 4 vars × 2 categorias × 853 munis = 6.824/ano → cabe sem paginação especial

# ─── Mapeamento: nome original → nome _mg ────────────────────────────────────
# Coletores municipais escrevem em DIR_PROCESSED / nome_original.csv
# Depois renomeamos para nome_mg.csv

# Tabelas que usam os coletores originais (monkey-patched) e precisam de renomeio
MUNICIPAIS_RENOMEIO = [
    # PAM 1612/1613: salvam diretamente com _mg, NÃO renomear
    ("sidra_pam839_milho_safras",      "PAM 839 (milho safras)"),
    ("sidra_ppm3939_rebanhos",         "PPM 3939 (rebanhos)"),
    ("sidra_ppm74_leite",              "PPM 74 (leite)"),
    ("sidra_ppm74_mel",                "PPM 74 (mel)"),
    ("sidra_ppm74_la",                 "PPM 74 (lã)"),
    ("sidra_ppm94_ovos",               "PPM 94 (ovos)"),
    ("sidra_ppm95_ovinos_tosquiados",  "PPM 95 (ovinos tosquiados)"),
    ("sidra_5938_pib_municipal",       "Tab 5938 (PIB municipal)"),
    ("sidra_6579_populacao",           "Tab 6579 (população)"),
    ("sidra_1737_ipca",                "Tab 1737 (IPCA — deflator)"),
]

# Coletores que usam funções originais (PAM 1612/1613 usam coletores customizados)
COLETORES_ORIGINAIS = [
    ("PAM 839 (milho safras)",           coleta.coletar_pam839_safrinha),
    ("PPM 3939 (rebanhos)",              coleta.coletar_ppm3939),
    ("PPM 74 (leite)",                   coleta.coletar_ppm74_leite),
    ("PPM 74 (mel)",                     coleta.coletar_ppm74_mel),
    ("PPM 74 (lã)",                      coleta.coletar_ppm74_la),
    ("PPM 94 (ovos)",                    coleta.coletar_ppm94_ovos),
    ("PPM 95 (ovinos tosquiados)",       coleta.coletar_ppm95_ovinos_tosquiados),
    ("Tab 5938 (PIB municipal)",         coleta.coletar_pib_municipal),
    ("Tab 6579 (população)",             coleta.coletar_populacao),
    ("Tab 1737 (IPCA — deflator)",        coleta.coletar_ipca),
]

# Coletores PAM customizados (paginam por produto)
COLETORES_PAM = [
    ("PAM 1612 (lavouras temporárias)",   _coletar_pam1612_mg),
    ("PAM 1613 (lavouras permanentes)",   _coletar_pam1613_mg),
]

ABATE_ORIGINAIS = [
    ("sidra_abate1092_bovinos_go", "ABATE 1092 (bovinos — MG UF)"),
    ("sidra_abate1093_suinos_go",  "ABATE 1093 (suínos — MG UF)"),
    ("sidra_abate1094_frangos_go", "ABATE 1094 (frangos — MG UF)"),
]

CENSO_AGRO_INDIVIDUAIS = [
    ("sidra_censo_6878_estrutura_fundiaria", "6878 (estrutura fundiária)"),
    ("sidra_censo_6884_pessoal_ocupado",     "6884 (pessoal ocupado)"),
    ("sidra_censo_6870_tratores",             "6870 (tratores)"),
    ("sidra_censo_6848_adubacao",             "6848 (adubação)"),
    ("sidra_censo_6851_agrotoxicos",          "6851 (agrotóxicos)"),
    ("sidra_censo_6910_bovinos",              "6910 (bovinos)"),
    ("sidra_censo_6958_lavouras_temp",        "6958 (lavouras temporárias)"),
    ("sidra_censo_6855_plantio_direto",       "6855 (plantio direto)"),
    ("sidra_censo_6877_veiculos",              "6877 (veículos)"),
]


def _mover_para_mg(nome_original: str) -> Path | None:
    """Move DIR_PROCESSED/nome_original.csv → DIR_PROCESSED/nome_original_mg.csv.
    Retorna o Path do arquivo _mg ou None se o original não existir."""
    orig = DIR_PROCESSED / f"{nome_original}.csv"
    dest = DIR_PROCESSED / f"{nome_original}{SUFIXO}.csv"
    if not orig.exists():
        return None
    if dest.exists():
        dest.unlink()
    orig.rename(dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Ignora cache e rebaixa todas as tabelas")
    parser.add_argument("--so", nargs="+", default=None,
                        help="Roda só coletores cujo nome contenha estas substrings")
    parser.add_argument("--abate", action="store_true",
                        help="Roda só o bloco de abate (tabelas 1092/1093/1094, nível UF)")
    parser.add_argument("--censo-agro", action="store_true",
                        help="Roda só o Censo Agro 2017")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Coleta SIDRA — Minas Gerais (853 municípios, UF=31)")
    print(f"  raw     -> {DIR_RAW_SIDRA_MG}")
    print(f"  limpo   -> {DIR_PROCESSED}")
    print(f"  cache   -> {'OFF (--force)' if args.force else 'ON'}")
    print("=" * 70)

    # ─── Coleção municipal ────────────────────────────────────────────────────
    if not args.abate and not args.censo_agro:
        resumo = []

        # PAM customizados (com paginação por produto)
        for label, fn in COLETORES_PAM:
            if args.so and not any(s.lower() in label.lower() for s in args.so):
                continue
            try:
                print(f"\n--- {label} ---")
                df = fn(force=args.force)
                resumo.append({"tabela": label, "linhas": len(df), "status": "OK"})
            except Exception as e:
                print(f"  [ERRO] {label}: {e}")
                resumo.append({"tabela": label, "linhas": 0, "status": f"ERRO: {e}"})

        # Coletores originais (monkey-patched para MG)
        for label, fn in COLETORES_ORIGINAIS:
            if args.so and not any(s.lower() in label.lower() for s in args.so):
                continue
            try:
                print(f"\n--- {label} ---")
                df = fn(force=args.force)
                resumo.append({"tabela": label, "linhas": len(df), "status": "OK"})
            except Exception as e:
                print(f"  [ERRO] {label}: {e}")
                resumo.append({"tabela": label, "linhas": 0, "status": f"ERRO: {e}"})

        # Renomear arquivos de saída: adicionar sufixo _mg
        # (PAM 1612/1613 já salvam com _mg, não renomear)
        print("\n--- Renomeando arquivos municipais para _mg ---")
        renomeados = 0
        for nome_original, label in MUNICIPAIS_RENOMEIO:
            dest = _mover_para_mg(nome_original)
            if dest:
                print(f"  {nome_original}.csv -> {dest.name}")
                renomeados += 1
            else:
                print(f"  [AVISO] {nome_original}.csv não encontrado")
        print(f"  {renomeados} arquivos municipais renomeados")

        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO SIDRA MUNICIPAL — Minas Gerais")
        print("=" * 70)
        for r in resumo:
            status = r["status"]
            print(f"  {r['tabela']:40s}  {r['linhas']:>6,} linhas  {status}")
        print("=" * 70)

    # ─── Coleção abate (UF) ──────────────────────────────────────────────────
    if args.abate or (not args.censo_agro):
        # Abate: coletar e renomear
        if args.abate:
            print("\n" + "=" * 70)
            print(f"Coleta ABATE — Minas Gerais (UF={UF_CODIGO_IBGE_MG})")
            print("=" * 70)

        abate_resumo = []
        for label, fn in coleta.COLETORES_ABATE:
            try:
                df = fn(force=args.force)
                abate_resumo.append({"tabela": label, "linhas": len(df), "status": "OK"})
            except Exception as e:
                abate_resumo.append({"tabela": label, "linhas": 0, "status": f"ERRO: {e}"})
                print(f"  [ERRO] {label}: {e}")

        # Agregar abate em anual
        print("\n[ABATE] Agregando trimestres → anual...")
        anual = coleta.agregar_abate_anual(force=args.force)

        # Renomear arquivos de abate
        print("\n--- Renomeando arquivos de abate para _mg ---")
        for nome_original, label in ABATE_ORIGINAIS:
            dest = _mover_para_mg(nome_original)
            if dest:
                print(f"  {nome_original}.csv -> {dest.name}")

        # Renomear painel anual de abate
        abate_anual_orig = DIR_PROCESSED / "sidra_abate_goias_anual.csv"
        abate_anual_dest = DIR_PROCESSED / f"sidra_abate_mg_anual{SUFIXO}.csv"
        if abate_anual_orig.exists():
            if abate_anual_dest.exists():
                abate_anual_dest.unlink()
            abate_anual_orig.rename(abate_anual_dest)
            print(f"  sidra_abate_goias_anual.csv -> {abate_anual_dest.name}")

        if args.abate and abate_resumo:
            print("\n" + "=" * 70)
            print("RESUMO ABATE — Minas Gerais")
            print("=" * 70)
            for r in abate_resumo:
                print(f"  {r['tabela']:40s}  {r['linhas']:>6,} linhas  {r['status']}")

    # ─── Coleção Censo Agro 2017 ──────────────────────────────────────────────
    if args.censo_agro:
        print("\n" + "=" * 70)
        print("Coleta CENSO AGRO 2017 — Minas Gerais")
        print("=" * 70)

        censo_resumo = []
        for label, fn in coleta.COLETORES_CENSO_AGRO:
            try:
                df = fn(force=args.force)
                censo_resumo.append({
                    "tabela": label, "linhas": len(df),
                    "municipios": df["cd_mun"].nunique() if "cd_mun" in df.columns else "-",
                    "status": "OK",
                })
            except Exception as e:
                censo_resumo.append({
                    "tabela": label, "linhas": 0, "municipios": "-",
                    "status": f"ERRO: {e}",
                })
                print(f"  [ERRO] {label}: {e}")

        # Montar painel wide
        print("\n[Montando painel wide do Censo Agro...]")
        painel = coleta.montar_painel_censo_agro(force=args.force)

        # Renomear arquivos individuais do Censo Agro
        print("\n--- Renomeando arquivos do Censo Agro para _mg ---")
        for nome_original, label in CENSO_AGRO_INDIVIDUAIS:
            dest = _mover_para_mg(nome_original)
            if dest:
                print(f"  {nome_original}.csv -> {dest.name}")

        # Renomear painel consolidado
        censo_painel_orig = DIR_PROCESSED / "sidra_censo_agro_2017.csv"
        censo_painel_dest = DIR_PROCESSED / f"sidra_censo_agro_2017{SUFIXO}.csv"
        if censo_painel_orig.exists():
            if censo_painel_dest.exists():
                censo_painel_dest.unlink()
            censo_painel_orig.rename(censo_painel_dest)
            print(f"  sidra_censo_agro_2017.csv -> {censo_painel_dest.name}")

        print("\n" + "=" * 70)
        print("RESUMO CENSO AGRO 2017 — Minas Gerais")
        print("=" * 70)
        for r in censo_resumo:
            print(f"  {r['tabela']:40s}  {r['linhas']:>6,}  {r['status']}")

    # ─── Validação: verificar cd_mun prefixos ─────────────────────────────────
    print("\n--- Validação: prefixos cd_mun ---")
    mg_files = list(DIR_PROCESSED.glob("sidra_*_mg.csv"))
    for f in sorted(mg_files):
        try:
            df = pd.read_csv(f, nrows=3)
            if "cd_mun" in df.columns:
                prefixes = df["cd_mun"].astype(str).str[:2].unique()
                status = "OK" if "31" in prefixes else "ERRO (prefixo != 31)"
                print(f"  {f.name}: prefixos={prefixes} -> {status}")
            elif "uf_cod" in df.columns:
                prefixes = df["uf_cod"].astype(str).str[:2].unique()
                print(f"  {f.name}: uf_cod prefixes={prefixes}")
            else:
                print(f"  {f.name}: (sem cd_mun/uf_cod)")
        except Exception as e:
            print(f"  {f.name}: ERRO ao ler - {e}")


if __name__ == "__main__":
    main()