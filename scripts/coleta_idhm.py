"""
coleta_idhm.py — Coletor de IDH-M (Atlas do Desenvolvimento Humano no Brasil)
==============================================================================

Baixa e processa o Índice de Desenvolvimento Humano Municipal (IDH-M) e
sub-índices para os 246 municípios de Goiás.

Fonte primária: IPEA Data API (séries ADH_IDHM, ADH_IDHM_E, ADH_IDHM_L,
ADH_IDHM_R). Cobre os anos do Censo Demográfico: 1991, 2000, 2010.

  API endpoint: http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='<SERIE>')

Fonte secundária (fallback manual): PNUD Brasil / Fundação João Pinheiro / IBGE
— Atlas do Desenvolvimento Humano no Brasil.
  Necessária para o ano 2021 (PNAD Contínua), não disponível na IPEA API
  no nível municipal.

COMO OBTER OS DADOS DE 2021 (download manual):

  1. Acesse http://www.atlasbrasil.org.br/ranking
  2. Selecione: Municípios > Ano 2021
  3. Clique em "BAIXAR TABELA"
  4. Salve o CSV como data/raw/idhm/atlas_idhm_2021_goias.csv
     ou o XLSX como data/raw/idhm/atlas_idhm_2021_goias.xlsx

  Alternativa (todos os anos Censo):
    1. Acesse http://www.atlasbrasil.org.br/consulta/planilha
    2. Selecione: Municípios > Goiás > Anos 1991, 2000, 2010, 2021
    3. Indicadores: IDH-M, IDH-M Renda, IDH-M Longevidade, IDH-M Educação
    4. Baixe como CSV e salve em data/raw/idhm/atlas_idhm_goias.csv

  Alternativa Base dos Dados (1991–2010):
    1. Acesse https://basedosdados.org/dataset/br-atlas-de-desenvolvimento-humano
    2. Baixe a tabela municipio como CSV e coloque em data/raw/idhm/

Saída:
  data/processed/idhm_goias_municipal.csv

Schema: cd_mun, nm_mun, ano, idhm, idhm_r, idhm_l, idhm_e

  idhm   — IDH-M geral
  idhm_r — IDH-M Renda
  idhm_l — IDH-M Longevidade
  idhm_e — IDH-M Educação

Como rodar:
    python coleta_idhm.py            # busca IPEA API + processa arquivos locais
    python coleta_idhm.py --force    # reprocessa mesmo se output já existe
    python coleta_idhm.py --offline  # só processa arquivos locais, sem API
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
ROOT           = Path(__file__).resolve().parent.parent
DIR_RAW_IDHM  = ROOT / "data" / "raw" / "idhm"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW_IDHM, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

N_MUNICIPIOS_GO = 246
CODIGO_UF_GO = 52  # Prefixo IBGE para Goiás

# IPEA Data API — séries ADH (Atlas do Desenvolvimento Humano - Censo)
IPEA_SERIES = {
    "ADH_IDHM":   "idhm",
    "ADH_IDHM_E": "idhm_e",
    "ADH_IDHM_L": "idhm_l",
    "ADH_IDHM_R": "idhm_r",
}
IPEA_API_BASE = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{code}')"

# Colunas de interesse (nomes variam por fonte)
COLUNAS_IDHM = {
    # Atlas Brasil (download web)
    "IDHM":           "idhm",
    "IDHM_R":         "idhm_r",
    "IDHM_L":         "idhm_l",
    "IDHM_E":         "idhm_e",
    # Base dos Dados (lowercase, prefixo)
    "idhm":           "idhm",
    "idhm_renda":     "idhm_r",
    "idhm_longevidade":"idhm_l",
    "idhm_educacao":  "idhm_e",
    # Alternativas comuns
    "IDH Municipal":  "idhm",
    "IDHM Renda":     "idhm_r",
    "IDHM Longevidade":"idhm_l",
    "IDHM Educação":  "idhm_e",
}

# Identificadores municipais (nomes variam por fonte)
COLUNAS_MUNI = {
    "CodMun":      "cd_mun",
    "Codmun":      "cd_mun",
    "codmun6":     "cd_mun",
    "cod_municipio":"cd_mun",
    "Código do Município":"cd_mun",
    "id_municipio":"cd_mun",
    "Município":  "nm_mun",
    "Nome do Município":"nm_mun",
    "nome_municipio":"nm_mun",
    "NM_MUNICIPIO":"nm_mun",
}

COLUNAS_ANO = {"Ano", "ano", "ANO"}

COLUNAS_SAIDA = ["cd_mun", "nm_mun", "ano", "idhm", "idhm_r", "idhm_l", "idhm_e"]


# ---------------------------------------------------------------------------
# Fonte 1: IPEA Data API
# ---------------------------------------------------------------------------

def _baixar_ipea() -> pd.DataFrame:
    """Baixa dados IDH-M do IPEA Data API para municípios de Goiás.

    Retorna DataFrame longo com colunas: cd_mun, ano, col_name (idhm/idhm_e/idhm_l/idhm_r), valor.
    """
    all_data = []
    for sercodigo, col_name in IPEA_SERIES.items():
        url = IPEA_API_BASE.format(code=sercodigo)
        print(f"  IPEA API: {sercodigo} -> {col_name}...")
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"    ERRO: {e}")
            continue

        values = r.json().get("value", [])
        goias = [
            v for v in values
            if str(v.get("TERCODIGO", "")).startswith("52")
            and v.get("NIVNOME", "") == "Municípios"
        ]
        print(f"    {len(goias)} registros de Goiás")

        for v in goias:
            all_data.append({
                "cd_mun": int(v["TERCODIGO"]),
                "ano": int(v["VALDATA"][:4]),
                "col_name": col_name,
                "valor": v["VALVALOR"],
            })

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    pivot = df.pivot_table(
        index=["cd_mun", "ano"], columns="col_name", values="valor", aggfunc="first"
    ).reset_index()
    pivot.columns.name = None
    return pivot


# ---------------------------------------------------------------------------
# Fonte 2: arquivos locais (fallback manual)
# ---------------------------------------------------------------------------

def _encontrar_arquivo_raw() -> Path | None:
    """Procura arquivo de dados IDH-M em data/raw/idhm/."""
    padroes = [
        "atlas_idhm_goias.csv", "atlas_idhm_goias.xlsx",
        "atlas_idhm_2021_goias.csv", "atlas_idhm_2021_goias.xlsx",
        "municipio.csv", "*.csv", "*.xlsx",
    ]
    for padrao in padroes:
        arquivos = list(DIR_RAW_IDHM.glob(padrao))
        if arquivos:
            return arquivos[0]
    return None


def _ler_atlas_web(caminho: Path) -> pd.DataFrame:
    """Lê CSV/Excel do download manual do Atlas Brasil."""
    if caminho.suffix == ".xlsx":
        df = pd.read_excel(caminho)
    else:
        try:
            df = pd.read_csv(caminho, sep=";", encoding="latin-1", thousands=".", decimal=",")
        except UnicodeDecodeError:
            df = pd.read_csv(caminho, sep=";", encoding="utf-8", thousands=".", decimal=",")

    print(f"  Colunas do arquivo: {list(df.columns[:15])}...")
    print(f"  Shape: {df.shape}")
    return df


def _ler_basedosdados(caminho: Path) -> pd.DataFrame:
    """Lê CSV do Base dos Dados (formato padrão)."""
    try:
        df = pd.read_csv(caminho)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding="utf-8")

    print(f"  Colunas do arquivo: {list(df.columns[:15])}...")
    print(f"  Shape: {df.shape}")
    return df


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nomes de colunas para o schema canônico."""
    rename = {}
    for col in df.columns:
        col_strip = col.strip()
        if col_strip in COLUNAS_MUNI:
            rename[col] = COLUNAS_MUNI[col_strip]
        elif col_strip in COLUNAS_IDHM:
            rename[col] = COLUNAS_IDHM[col_strip]

    df = df.rename(columns=rename)

    for col in df.columns:
        if col.strip() in COLUNAS_ANO:
            df = df.rename(columns={col: "ano"})
            break

    if "cd_mun" in df.columns:
        df["cd_mun"] = pd.to_numeric(df["cd_mun"], errors="coerce").astype("Int64")
        mask_6 = df["cd_mun"].astype(str).str.len() == 6
        if mask_6.any():
            def _dv_7dig(cd6: int) -> int:
                s = str(cd6)
                resto = sum(int(s[i]) * (7 - i) for i in range(6)) % 10
                dv = 0 if resto == 0 else 10 - resto
                return cd6 * 10 + dv
            df.loc[mask_6, "cd_mun"] = df.loc[mask_6, "cd_mun"].apply(_dv_7dig)

    if "ano" in df.columns:
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")

    for col_idhm in ["idhm", "idhm_r", "idhm_l", "idhm_e"]:
        if col_idhm in df.columns:
            df[col_idhm] = pd.to_numeric(df[col_idhm], errors="coerce")

    return df


def _filtrar_goias(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra apenas municípios de Goiás (códigos começando com 52)."""
    if "cd_mun" not in df.columns:
        raise ValueError(
            "Coluna 'cd_mun' não encontrada. Colunas disponíveis: "
            f"{list(df.columns)}. Verifique o formato do arquivo de entrada."
        )
    df_go = df[df["cd_mun"].astype(str).str.startswith("52")].copy()
    print(f"  Municípios de Goiás encontrados: {df_go['cd_mun'].nunique()}")
    if df_go["cd_mun"].nunique() == 0:
        raise ValueError(
            "Nenhum município de Goiás encontrado. Códigos presentes: "
            f"{df['cd_mun'].dropna().unique()[:10]}"
        )
    return df_go


def _processar_arquivo_local() -> pd.DataFrame | None:
    """Lê, normaliza e filtra arquivo local de IDH-M."""
    arquivo = _encontrar_arquivo_raw()
    if arquivo is None:
        return None

    print(f"\n[IDH-M] Processando arquivo local: {arquivo.name}...")

    if "municipio" in arquivo.name.lower() and "atlas" not in arquivo.name.lower():
        df = _ler_basedosdados(arquivo)
    else:
        df = _ler_atlas_web(arquivo)

    df = _normalizar_colunas(df)
    df = _filtrar_goias(df)
    return df


# ---------------------------------------------------------------------------
# Merge IPEA API + arquivos locais
# ---------------------------------------------------------------------------

def _mesclar_fontes(df_ipea: pd.DataFrame, df_local: pd.DataFrame | None) -> pd.DataFrame:
    """Mescla dados da IPEA API com arquivos locais (anos adicionais como 2021).

    IPEA API tem prioridade para anos sobrepostos.
    """
    frames = []

    if not df_ipea.empty:
        frames.append(df_ipea)
        anos_ipea = sorted(df_ipea["ano"].unique())
        print(f"  IPEA API: anos {anos_ipea}, {df_ipea['cd_mun'].nunique()} municípios")

    if df_local is not None and not df_local.empty:
        # Adicionar apenas anos que a IPEA não cobre
        anos_ipea_set = set(df_ipea["ano"].unique()) if not df_ipea.empty else set()
        df_local_extra = df_local[~df_local["ano"].isin(anos_ipea_set)]
        if not df_local_extra.empty:
            frames.append(df_local_extra)
            anos_local = sorted(df_local_extra["ano"].unique())
            print(f"  Arquivo local (anos adicionais): {anos_local}, {df_local_extra['cd_mun'].nunique()} municípios")

    if not frames:
        return pd.DataFrame(columns=COLUNAS_SAIDA)

    df = pd.concat(frames, ignore_index=True)
    # Remover duplicatas (IPEA tem prioridade por vir primeiro na concat)
    df = df.drop_duplicates(subset=["cd_mun", "ano"], keep="first")

    return df


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def coletar_idhm(force: bool = False, offline: bool = False) -> pd.DataFrame:
    """Coleta dados IDH-M: IPEA API (primária) + arquivos locais (fallback/2021)."""
    output_path = DIR_PROCESSED / "idhm_goias_municipal.csv"
    if output_path.exists() and not force:
        df = pd.read_csv(output_path)
        print(f"[cache] idhm_goias_municipal.csv ({len(df):,} linhas)")
        return df

    # --- Fonte 1: IPEA Data API ---
    df_ipea = pd.DataFrame()
    if not offline:
        print("\n[IDH-M] Consultando IPEA Data API...")
        try:
            df_ipea = _baixar_ipea()
        except Exception as e:
            print(f"  IPEA API falhou: {e}")
            print("  Continuando com arquivos locais...")
    else:
        print("\n[IDH-M] Modo offline — pulando IPEA API")

    # --- Fonte 2: arquivos locais ---
    df_local = None
    print("\n[IDH-M] Verificando arquivos locais em data/raw/idhm/...")
    try:
        df_local = _processar_arquivo_local()
    except Exception as e:
        print(f"  Arquivo local falhou: {e}")

    if df_local is None and df_ipea.empty:
        print("=" * 70)
        print("ERRO: Nenhuma fonte de dados disponível.")
        print()
        print("  IPEA API: indisponível ou sem dados municipais de Goiás")
        print("  Arquivo local: nenhum encontrado em data/raw/idhm/")
        print()
        print("COMO OBTER OS DADOS:")
        print()
        print("  Opção 1 — IPEA Data API (automático):")
        print("    Rode sem --offline. Requer conexão com internet.")
        print()
        print("  Opção 2 — Atlas Brasil (todos os anos, formato web):")
        print("    1. Acesse http://www.atlasbrasil.org.br/consulta/planilha")
        print("    2. Selecione: Municípios > Goiás > Anos 1991, 2000, 2010, 2021")
        print("    3. Indicadores: IDH-M, IDH-M Renda, IDH-M Longevidade, IDH-M Educação")
        print("    4. Baixe como CSV e salve em:")
        print(f"       {DIR_RAW_IDHM / 'atlas_idhm_goias.csv'}")
        print()
        print("  Opção 3 — Base dos Dados (1991–2010, formato longo):")
        print("    1. Acesse https://basedosdados.org/dataset/br-atlas-de-desenvolvimento-humano")
        print("    2. Baixe a tabela 'municipio' como CSV")
        print("    3. Salve em:")
        print(f"       {DIR_RAW_IDHM / 'municipio.csv'}")
        print("=" * 70)
        sys.exit(1)

    # --- Mesclar fontes ---
    print("\n[IDH-M] Mesclando fontes...")
    df = _mesclar_fontes(df_ipea, df_local)

    if df.empty:
        print("ERRO: Mescla resultou em DataFrame vazio.")
        sys.exit(1)

    # Adicionar nomes dos municípios do painel unificado
    painel_path = DIR_PROCESSED / "painel_unificado.parquet"
    if painel_path.exists():
        munis = pd.read_parquet(painel_path, columns=["cd_mun", "nm_mun"]).drop_duplicates()
        df = df.merge(munis, on="cd_mun", how="left")
    elif "nm_mun" not in df.columns:
        df["nm_mun"] = pd.NA

    # Selecionar e ordenar colunas
    cols = [c for c in COLUNAS_SAIDA if c in df.columns]
    df = df[cols].copy()
    df = df.sort_values(["cd_mun", "ano"]).reset_index(drop=True)

    # Validação
    n_munis = df["cd_mun"].nunique()
    anos_presentes = sorted(df["ano"].dropna().unique())
    print(f"  Municípios únicos: {n_munis}")
    print(f"  Anos presentes: {anos_presentes}")

    for col in ["idhm", "idhm_r", "idhm_l", "idhm_e"]:
        if col in df.columns:
            val_min, val_max = df[col].min(), df[col].max()
            n_missing = df[col].isna().sum()
            print(f"  {col}: [{val_min:.3f}, {val_max:.3f}], {n_missing} missing")

    # Salvar
    df.to_csv(output_path, index=False)
    print(f"\n  -> idhm_goias_municipal.csv ({len(df):,} linhas)")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo se output já existe")
    parser.add_argument("--offline", action="store_true",
                        help="Só processa arquivos locais, sem IPEA API")
    args = parser.parse_args()

    print("=" * 70)
    print("Coleta IDH-M — Atlas do Desenvolvimento Humano")
    print(f"  IPEA API -> http://www.ipeadata.gov.br/api/odata4/")
    print(f"  raw      -> {DIR_RAW_IDHM}")
    print(f"  limpo    -> {DIR_PROCESSED}")
    print("=" * 70)

    df = coletar_idhm(force=args.force, offline=args.offline)

    print("\n" + "=" * 70)
    print("RESUMO IDH-M")
    print("=" * 70)
    print(f"  Municípios: {df['cd_mun'].nunique()}")
    print(f"  Anos: {sorted(df['ano'].dropna().unique())}")
    print(f"  Linhas: {len(df)}")
    if "idhm" in df.columns:
        print(f"  IDH-M médio GO: {df['idhm'].mean():.3f}")


if __name__ == "__main__":
    main()