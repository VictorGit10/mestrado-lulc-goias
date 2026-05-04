"""
coleta_idhm.py — Coletor de IDH-M (Atlas do Desenvolvimento Humano no Brasil)
==============================================================================

Baixa e processa o Índice de Desenvolvimento Humano Municipal (IDH-M) e
sub-índices para os 246 municípios de Goiás, nos anos 1991, 2000, 2010 e 2021.

Fonte: PNUD Brasil / Fundação João Pinheiro / IBGE — Atlas do Desenvolvimento
Humano no Brasil (http://www.atlasbrasil.org.br/)

COMO OBTER OS DADOS (download manual):

  1. Acesse http://www.atlasbrasil.org.br/consulta/planilha
  2. Selecione:
     - Abrangência: Municípios
     - UF: Goiás
     - Anos: 1991, 2000, 2010 (ou 2019 para a atualização 2021)
     - Indicadores: IDH-M, IDH-M Renda, IDH-M Longevidade, IDH-M Educação
  3. Clique em "BAIXAR TABELA"
  4. Salve o CSV como data/raw/idhm/atlas_idhm_goias.csv

  Alternativa (dados 1991–2010):
    - Base dos Dados: https://basedosdados.org/dataset/br-atlas-de-desenvolvimento-humano
    - Baixar a tabela municipio como CSV e colocar em data/raw/idhm/

  Para dados 2021:
    - A atualização 2021 do Atlas Brasil está em
      https://www.ipea.gov.br/atlasbrasil/outras-informacoes/
    - Baixe o arquivo Excel/CSV e coloque em data/raw/idhm/atlas_idhm_2021_goias.xlsx
      (ou .csv)

O script detecta o formato do arquivo e normaliza automaticamente.

Saída:
  data/processed/idhm_goias_municipal.csv

Schema: cd_mun, nm_mun, ano, idhm, idhm_r, idhm_l, idhm_e

Como rodar:
    python coleta_idhm.py            # processa o CSV se existir
    python coleta_idhm.py --force    # reprocessa mesmo se output já existe
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

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


# ---------------------------------------------------------------------------
# Funções de leitura
# ---------------------------------------------------------------------------

def _encontrar_arquivo_raw() -> Path | None:
    """Procura arquivo de dados IDH-M em data/raw/idhm/."""
    padroes = ["atlas_idhm_goias.csv", "atlas_idhm_goias.xlsx",
               "municipio.csv", "*.csv", "*.xlsx"]
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
        # Atlas Brasil exporta CSV com ; e encoding latin-1
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
    # Detectar e renomear colunas de identificação municipal
    rename = {}
    for col in df.columns:
        col_strip = col.strip()
        if col_strip in COLUNAS_MUNI:
            rename[col] = COLUNAS_MUNI[col_strip]
        elif col_strip in COLUNAS_IDHM:
            rename[col] = COLUNAS_IDHM[col_strip]

    df = df.rename(columns=rename)

    # Detectar coluna de ano
    for col in df.columns:
        if col.strip() in COLUNAS_ANO:
            df = df.rename(columns={col: "ano"})
            break

    # Garantir tipos
    if "cd_mun" in df.columns:
        # cd_mun pode ter 6 ou 7 dígitos. Normalizar para 7 (adicionar dígito verificador se 6).
        df["cd_mun"] = pd.to_numeric(df["cd_mun"], errors="coerce").astype("Int64")
        # Se códigos têm 6 dígitos, converter para 7
        mask_6 = df["cd_mun"].astype(str).str.len() == 6
        if mask_6.any():
            # Fórmula do dígito verificador IBGE: soma alternada dos 5 primeiros dígitos
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
        # Talvez o cd_mun esteja como UF + código sem dígito
        # Tentar filtrar por UF=52 (primeiros 2 dígitos)
        raise ValueError(
            "Nenhum município de Goiás encontrado. Códigos presentes: "
            f"{df['cd_mun'].dropna().unique()[:10]}"
        )
    return df_go


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def coletar_idhm(force: bool = False) -> pd.DataFrame:
    """Processa dados IDH-M a partir de arquivo baixado manualmente."""
    output_path = DIR_PROCESSED / "idhm_goias_municipal.csv"
    if output_path.exists() and not force:
        df = pd.read_csv(output_path)
        print(f"[cache] idhm_goias_municipal.csv ({len(df):,} linhas)")
        return df

    arquivo = _encontrar_arquivo_raw()
    if arquivo is None:
        print("=" * 70)
        print("ERRO: Nenhum arquivo de dados encontrado em data/raw/idhm/")
        print()
        print("COMO OBTER OS DADOS:")
        print()
        print("  Opção 1 — Atlas Brasil (todos os anos, formato web):")
        print("    1. Acesse http://www.atlasbrasil.org.br/consulta/planilha")
        print("    2. Selecione: Municípios > Goiás > Anos 1991, 2000, 2010, 2019/2021")
        print("    3. Indicadores: IDH-M, IDH-M Renda, IDH-M Longevidade, IDH-M Educação")
        print("    4. Baixe como CSV e salve em:")
        print(f"       {DIR_RAW_IDHM / 'atlas_idhm_goias.csv'}")
        print()
        print("  Opção 2 — Base dos Dados (1991–2010, formato longo):")
        print("    1. Acesse https://basedosdados.org/dataset/br-atlas-de-desenvolvimento-humano")
        print("    2. Baixe a tabela 'municipio' como CSV")
        print("    3. Salve em:")
        print(f"       {DIR_RAW_IDHM / 'municipio.csv'}")
        print("=" * 70)
        sys.exit(1)

    print(f"\n[IDH-M] Processando {arquivo.name}...")

    # Detectar formato e ler
    if "municipio" in arquivo.name.lower() and "atlas" not in arquivo.name.lower():
        df = _ler_basedosdados(arquivo)
    else:
        df = _ler_atlas_web(arquivo)

    # Normalizar colunas
    df = _normalizar_colunas(df)

    # Filtrar Goiás
    df = _filtrar_goias(df)

    # Selecionar colunas de interesse
    colunas_saida = [c for c in ["cd_mun", "nm_mun", "ano", "idhm", "idhm_r", "idhm_l", "idhm_e"] if c in df.columns]
    df = df[colunas_saida].copy()

    # Ordenar
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
    args = parser.parse_args()

    print("=" * 70)
    print("Coleta IDH-M — Atlas do Desenvolvimento Humano (PNUD)")
    print(f"  raw     -> {DIR_RAW_IDHM}")
    print(f"  limpo   -> {DIR_PROCESSED}")
    print("=" * 70)

    df = coletar_idhm(force=args.force)

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