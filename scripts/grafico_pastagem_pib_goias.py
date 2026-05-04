"""
Gráfico exploratório: Pastagem em Goiás vs PIB de Goiás (1985–2024)
====================================================================

O que esse script faz, em quatro passos:
  1. Baixa a planilha de estatísticas do MapBiomas Coleção 10.1 (estados/biomas),
     filtra Goiás e a classe Pastagem, e produz uma série anual em hectares.
  2. Baixa o PIB Estadual de Goiás via SIDRA/IBGE (Contas Regionais).
  3. Baixa o IPCA via SIDRA e deflaciona o PIB para reais de dezembro/2024.
  4. Gera dois gráficos: (a) pastagem 1985–2024 sozinha; (b) pastagem + PIB
     real lado a lado no período de overlap.

Como rodar:
    pip install pandas openpyxl matplotlib requests sidrapy
    python grafico_pastagem_pib_goias.py

Saída: dois PNGs em ./outputs/ e dois CSVs em ./data/processed/

Nota de honestidade: o ano-base do deflator é dezembro/2024. Isso significa
que TODOS os valores monetários no gráfico estão em "reais de dez/2024".
Mude DATA_BASE_DEFLATOR se quiser outra referência.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

# Estado-alvo
UF_NOME = "Goiás"
UF_SIGLA = "GO"
UF_CODIGO_IBGE = 52  # código IBGE de Goiás

# Período
ANO_INICIO = 1985
ANO_FIM = 2024

# Classe MapBiomas: 15 = Pastagem
CLASSE_PASTAGEM = 15

# Data-base para deflacionar valores monetários
# Formato: (ano, mês). Dez/2024 é uma escolha defensável e natural quando
# a série mais recente vai até 2024.
DATA_BASE_DEFLATOR = (2024, 12)

# URLs das fontes
# Coleção 10.1 — Biomas, Estados e Municípios — Cobertura (atualizada em 19/02/2026)
# Fonte: https://brasil.mapbiomas.org/estatisticas/
# DOI: https://doi.org/10.58053/MapBiomas/SJZOLT
URL_MAPBIOMAS_COL10_ESTADO = (
    "https://drive.google.com/uc?id=1p0dLrhvKymPhrSithsRBMRgHlFHq0FUf&export=download"
)

# Diretórios de saída
ROOT = Path(__file__).resolve().parent.parent
DIR_RAW = ROOT / "data" / "raw"
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUTPUT = ROOT / "outputs"

for d in (DIR_RAW, DIR_PROCESSED, DIR_OUTPUT):
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. MapBiomas — área de pastagem em Goiás
# ---------------------------------------------------------------------------

def baixar_mapbiomas_estado() -> Path:
    """
    Baixa a planilha de estatísticas do MapBiomas Coleção 10.1 por estado/bioma.
    Cacheia em data/raw/. Se já existir, não baixa de novo.

    O arquivo é hospedado no Google Drive, que pode emitir um redirect com aviso
    de vírus para arquivos grandes. A sessão com cookies lida com isso automaticamente.
    """
    arquivo = DIR_RAW / "mapbiomas_col10_estado.xlsx"
    if arquivo.exists():
        print(f"[OK] MapBiomas já em cache: {arquivo}")
        return arquivo

    print(f"[...] Baixando MapBiomas Coleção 10.1 (estados/biomas/municípios)...")
    session = requests.Session()
    r = session.get(URL_MAPBIOMAS_COL10_ESTADO, timeout=180, stream=True)
    r.raise_for_status()

    # Google Drive pode redirecionar para página de confirmação de vírus;
    # nesse caso o content-type é HTML, não xlsx. Tentamos seguir o link direto.
    content_type = r.headers.get("Content-Type", "")
    if "html" in content_type.lower():
        # Extrair token de confirmação e re-requisitar
        import re
        token_match = re.search(r'confirm=([0-9A-Za-z_\-]+)', r.text)
        if token_match:
            token = token_match.group(1)
            confirm_url = URL_MAPBIOMAS_COL10_ESTADO + f"&confirm={token}"
            r = session.get(confirm_url, timeout=180, stream=True)
            r.raise_for_status()

    arquivo.write_bytes(r.content)
    print(f"[OK] Salvo em {arquivo} ({arquivo.stat().st_size/1e6:.1f} MB)")
    return arquivo


def serie_pastagem_goias(arquivo_xlsx: Path) -> pd.DataFrame:
    """
    Extrai a série anual de pastagem (classe 15) em Goiás.
    
    A planilha do MapBiomas é "wide": cada ano é uma coluna (1985, 1986, ...).
    Ela tem várias abas; a que interessa para nós é a com cobertura por
    estado/bioma. Vamos detectar a aba certa e a coluna de classe certa.
    """
    print(f"[...] Lendo MapBiomas Coleção 10.1 e filtrando {UF_NOME} / classe {CLASSE_PASTAGEM} (Pastagem)...")
    
    # Ler todas as abas e usar a mais provável (a maior, normalmente)
    xls = pd.ExcelFile(arquivo_xlsx)
    print(f"  Abas disponíveis: {xls.sheet_names}")
    
    # A aba principal costuma ser a primeira com dados de cobertura.
    # Se mudar, ajuste o índice abaixo. Aqui usamos heurística: pegar a aba
    # que tem as colunas dos anos como inteiros 1985..2024.
    aba_escolhida = None
    for nome_aba in xls.sheet_names:
        df_teste = pd.read_excel(arquivo_xlsx, sheet_name=nome_aba, nrows=3)
        cols = set(df_teste.columns.astype(str))
        if str(ANO_INICIO) in cols and str(ANO_FIM) in cols:
            aba_escolhida = nome_aba
            break
    if aba_escolhida is None:
        raise ValueError(
            f"Não encontrei aba com colunas de anos {ANO_INICIO}..{ANO_FIM}. "
            f"Inspecione manualmente: {xls.sheet_names}"
        )
    print(f"  Aba escolhida: '{aba_escolhida}'")
    
    df = pd.read_excel(arquivo_xlsx, sheet_name=aba_escolhida)
    # Padronizar nomes de coluna em minúsculas para a busca ficar robusta
    df.columns = [str(c) for c in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}
    
    # Identificar colunas-chave da planilha do MapBiomas.
    # Os nomes podem variar por coleção, mas costumam ser:
    #   - "state", "estado", "uf"  -> UF
    #   - "class", "classe", "level_X" -> classe ou nível
    #   - "feature_id" para o código numérico da classe
    col_estado = next(
        (cols_lower[k] for k in ("state", "estado", "uf") if k in cols_lower),
        None,
    )
    col_classe_id = next(
        (cols_lower[k] for k in ("feature_id", "class_id", "id_class") if k in cols_lower),
        None,
    )
    col_classe_nome = next(
        (cols_lower[k] for k in ("class", "classe", "level_3", "class_level_3") if k in cols_lower),
        None,
    )
    
    if col_estado is None:
        raise ValueError(f"Não achei coluna de estado. Colunas: {list(df.columns)}")
    
    # Filtrar Goiás
    df_go = df[df[col_estado].astype(str).str.strip().str.upper().isin([UF_NOME.upper(), UF_SIGLA])]
    print(f"  Linhas para {UF_NOME}: {len(df_go)}")
    
    # Filtrar classe Pastagem — tentar por ID primeiro, depois por nome
    if col_classe_id is not None:
        df_go_pasto = df_go[df_go[col_classe_id] == CLASSE_PASTAGEM]
    elif col_classe_nome is not None:
        df_go_pasto = df_go[
            df_go[col_classe_nome].astype(str).str.contains("Pastagem|Pasture", case=False, na=False)
        ]
    else:
        raise ValueError("Não achei coluna de classe (id ou nome).")
    
    # A planilha do MapBiomas frequentemente tem múltiplas linhas para a mesma
    # combinação UF×classe (uma por bioma, por exemplo). Somar tudo:
    cols_anos = [c for c in df.columns if c.isdigit() and ANO_INICIO <= int(c) <= ANO_FIM]
    serie = df_go_pasto[cols_anos].sum(axis=0)
    serie.index = serie.index.astype(int)
    serie.name = "area_pastagem_ha"
    
    df_serie = serie.reset_index().rename(columns={"index": "ano"})
    df_serie["uf"] = UF_SIGLA
    print(f"[OK] Serie de pastagem em {UF_NOME}: {len(df_serie)} anos, "
          f"{df_serie['area_pastagem_ha'].iloc[0]/1e6:.2f} Mha -> "
          f"{df_serie['area_pastagem_ha'].iloc[-1]/1e6:.2f} Mha")
    return df_serie


# ---------------------------------------------------------------------------
# 2. PIB de Goiás via SIDRA/IBGE
# ---------------------------------------------------------------------------

def baixar_pib_goias() -> pd.DataFrame:
    """
    Baixa o PIB de Goiás via SIDRA, tabela 5938 (Contas Regionais — PIB municipal).
    Agrega os 246 municípios de GO para obter o estadual.
    
    Disponibilidade: 2002 até o ano mais recente publicado (geralmente t-2).
    Para anos anteriores (1985–2001) seria necessário usar a série retropolada
    do IBGE/IpeaData, que tem metodologia diferente. Não inclui aqui para
    manter a comparação metodologicamente coerente.
    """
    import sidrapy
    
    print(f"[...] Baixando PIB de Goiás via SIDRA (tabela 5938)...")
    
    # Tabela 5938: Produto Interno Bruto a preços correntes
    # Variável 37: PIB a preços correntes (mil R$)
    # Nível territorial 3 = UF (estado direto)
    df = sidrapy.get_table(
        table_code="5938",
        territorial_level="3",
        ibge_territorial_code=str(UF_CODIGO_IBGE),
        period="all",
        variable="37",
    )
    
    # Limpar: SIDRA retorna a primeira linha como cabeçalho repetido
    df = df.iloc[1:].copy()
    df["ano"] = df["D2C"].astype(int)
    df["pib_nominal_mil"] = pd.to_numeric(df["V"], errors="coerce")
    df["pib_nominal_rs"] = df["pib_nominal_mil"] * 1000  # converter para reais
    
    df_pib = df[["ano", "pib_nominal_rs"]].sort_values("ano").reset_index(drop=True)
    print(f"[OK] PIB nominal Goiás: {df_pib['ano'].min()}–{df_pib['ano'].max()} "
          f"({len(df_pib)} anos)")
    return df_pib


# ---------------------------------------------------------------------------
# 3. IPCA — deflator
# ---------------------------------------------------------------------------

def baixar_ipca_acumulado() -> pd.DataFrame:
    """
    Baixa o IPCA mensal e calcula o índice acumulado com base em DATA_BASE_DEFLATOR.
    Resultado: DataFrame com colunas [ano, mes, indice_acum].
    
    O IPCA é um índice mensal de variação. Para deflacionar uma série anual,
    o procedimento mais correto é:
      1. Pegar o IPCA mensal de jan/1985 a dez/2024.
      2. Construir um "número-índice" cumulativo (produto das (1+i_t/100)).
      3. Para cada ano X, usar o índice em dez/X (ou média do ano) como
         representativo do ano.
      4. Fator de deflação = índice_base / índice_ano.
    """
    import sidrapy
    
    print(f"[...] Baixando IPCA via SIDRA (tabela 1737)...")
    
    # Tabela 1737, variável 63: IPCA - Variação mensal (%)
    df = sidrapy.get_table(
        table_code="1737",
        territorial_level="1",
        ibge_territorial_code="all",
        period="all",
        variable="63",
    )
    df = df.iloc[1:].copy()
    
    # D2C tem formato "AAAAMM"
    df["ano"] = df["D2C"].str[:4].astype(int)
    df["mes"] = df["D2C"].str[4:6].astype(int)
    df["var_mensal"] = pd.to_numeric(df["V"], errors="coerce")
    df = df.sort_values(["ano", "mes"]).reset_index(drop=True)
    
    # Construir índice acumulado
    df["fator_mensal"] = 1 + df["var_mensal"] / 100
    df["indice_acum"] = df["fator_mensal"].cumprod()
    
    print(f"[OK] IPCA: {df['ano'].min()}–{df['ano'].max()}, "
          f"{len(df)} observações mensais")
    return df[["ano", "mes", "var_mensal", "indice_acum"]]


def deflacionar_pib(df_pib: pd.DataFrame, df_ipca: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o deflator IPCA ao PIB nominal, gerando PIB real em R$ de DATA_BASE.
    
    Estratégia: para cada ano X, usar o índice acumulado em dez/X como
    representativo. Fator = índice_base / índice_dezX.
    """
    ano_base, mes_base = DATA_BASE_DEFLATOR
    
    # Índice no mês-base
    indice_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base),
        "indice_acum",
    ].iloc[0]
    
    # Índice em dezembro de cada ano
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "indice_dez"}
    )
    
    df_out = df_pib.merge(df_dez, on="ano", how="left")
    df_out["fator_deflator"] = indice_base / df_out["indice_dez"]
    df_out["pib_real_rs"] = df_out["pib_nominal_rs"] * df_out["fator_deflator"]
    
    print(f"[OK] PIB deflacionado para R$ de {mes_base:02d}/{ano_base}")
    return df_out


# ---------------------------------------------------------------------------
# 4. Gráficos
# ---------------------------------------------------------------------------

def grafico_pastagem_sozinho(df_pasto: pd.DataFrame, caminho_saida: Path) -> None:
    """Gráfico A: pastagem em Goiás 1985–2024."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_pasto["ano"], df_pasto["area_pastagem_ha"] / 1e6,
            marker="o", markersize=3, linewidth=1.8, color="#7a4f00")
    ax.fill_between(df_pasto["ano"], df_pasto["area_pastagem_ha"] / 1e6,
                    alpha=0.15, color="#7a4f00")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Área de pastagem (milhões de hectares)")
    ax.set_title(f"Pastagem em {UF_NOME} — MapBiomas Coleção 10.1 (1985–2024)")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(ANO_INICIO - 0.5, ANO_FIM + 0.5)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {caminho_saida}")


def grafico_pastagem_pib(df_pasto: pd.DataFrame, df_pib: pd.DataFrame,
                         caminho_saida: Path) -> None:
    """
    Gráfico B: pastagem e PIB em painéis empilhados, no período de overlap.
    Eixo x compartilhado.
    """
    # Período de overlap
    ano_min = max(df_pasto["ano"].min(), df_pib["ano"].min())
    ano_max = min(df_pasto["ano"].max(), df_pib["ano"].max())
    
    pasto = df_pasto[(df_pasto["ano"] >= ano_min) & (df_pasto["ano"] <= ano_max)]
    pib = df_pib[(df_pib["ano"] >= ano_min) & (df_pib["ano"] <= ano_max)]
    
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    
    # Painel superior: pastagem
    ax1 = axes[0]
    ax1.plot(pasto["ano"], pasto["area_pastagem_ha"] / 1e6,
             marker="o", markersize=4, linewidth=2, color="#7a4f00",
             label="Pastagem (MapBiomas Col. 10)")
    ax1.set_ylabel("Pastagem (Mha)", color="#7a4f00")
    ax1.tick_params(axis="y", labelcolor="#7a4f00")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")
    
    # Painel inferior: PIB real
    ax2 = axes[1]
    ano_base, mes_base = DATA_BASE_DEFLATOR
    ax2.plot(pib["ano"], pib["pib_real_rs"] / 1e9,
             marker="s", markersize=4, linewidth=2, color="#1f4e79",
             label=f"PIB real (R$ de {mes_base:02d}/{ano_base})")
    ax2.set_ylabel(f"PIB Goiás (R$ bilhões, base {mes_base:02d}/{ano_base})",
                   color="#1f4e79")
    ax2.tick_params(axis="y", labelcolor="#1f4e79")
    ax2.set_xlabel("Ano")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")
    
    fig.suptitle(f"Pastagem vs PIB real em {UF_NOME} — {ano_min}–{ano_max}",
                 fontsize=13, y=0.995)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {caminho_saida}")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print(f"Pastagem × PIB — {UF_NOME} ({ANO_INICIO}–{ANO_FIM})")
    print("=" * 70)
    
    # 1. MapBiomas
    arquivo_mb = baixar_mapbiomas_estado()
    df_pasto = serie_pastagem_goias(arquivo_mb)
    df_pasto.to_csv(DIR_PROCESSED / "pastagem_goias_anual.csv", index=False)
    
    # 2. PIB
    df_pib_nom = baixar_pib_goias()
    
    # 3. Deflator
    df_ipca = baixar_ipca_acumulado()
    df_pib = deflacionar_pib(df_pib_nom, df_ipca)
    df_pib.to_csv(DIR_PROCESSED / "pib_goias_real.csv", index=False)
    
    # 4. Gráficos
    grafico_pastagem_sozinho(df_pasto, DIR_OUTPUT / "01_pastagem_goias_1985-2024.png")
    grafico_pastagem_pib(df_pasto, df_pib, DIR_OUTPUT / "02_pastagem_pib_goias.png")
    
    print("\nFeito.")


if __name__ == "__main__":
    main()
