"""
Análise expandida: Goiás (1985–2024)
=====================================

Usa o arquivo MapBiomas Col. 10.1 já em cache e novos dados do SIDRA para gerar
um painel completo com 4 análises:

  1. Cobertura do solo — 5 classes (pastagem, soja/lavoura, cerrado/savana,
     floresta nativa, área urbana) empilhadas numa área chart.
  2. Rebanho bovino em Goiás (SIDRA PPM — tabela 3939), 1985–2024.
  3. Pastagem × Rebanho: "taxa de lotação implícita" (UA/ha).
  4. PIB agropecuário real vs PIB total real de Goiás (participação %).

Como rodar (dependências já instaladas):
    python analise_expandida_goias.py

Saída: PNGs em ./outputs/  e CSVs em ./data/processed/
"""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
UF_NOME        = "Goiás"
UF_SIGLA       = "GO"
UF_CODIGO_IBGE = 52
ANO_INICIO     = 1985
ANO_FIM        = 2024
DATA_BASE_DEFLATOR = (2024, 12)

ROOT           = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw"
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_OUTPUT    = ROOT / "outputs"
for d in (DIR_RAW, DIR_PROCESSED, DIR_OUTPUT):
    d.mkdir(parents=True, exist_ok=True)

# Classes MapBiomas que queremos extrair
# Ref: https://brasil.mapbiomas.org/legenda-classificacao/
CLASSES = {
    15: ("Pastagem",          "#a07830"),
    39: ("Soja",              "#f5c242"),
    19: ("Lavoura Temporaria","#f0e040"),  # lavouras exceto soja (soma depois)
    41: ("Outra Lavoura Temp","#e8d830"),
    20: ("Cana",              "#e87820"),
    36: ("Lavoura Perene",    "#d46010"),
     4: ("Savana/Cerrado",    "#b8c878"),
     3: ("Floresta Nativa",   "#1e6820"),
    11: ("Campo Alagado",     "#5890d8"),
    12: ("Campo Nativo",      "#c8d890"),
    24: ("Area Urbana",       "#d04820"),
}

# Agrupamentos para o gráfico de área
GRUPOS = {
    "Pastagem":          [15],
    "Agricultura":       [39, 19, 41, 20, 36],
    "Cerrado/Savana":    [4, 12],
    "Floresta Nativa":   [3],
    "Area Urbana":       [24],
}
CORES_GRUPOS = {
    "Pastagem":        "#a07830",
    "Agricultura":     "#f5c242",
    "Cerrado/Savana":  "#78a050",
    "Floresta Nativa": "#1e6820",
    "Area Urbana":     "#d04820",
}

# ---------------------------------------------------------------------------
# 1. Carregar MapBiomas (reutiliza cache)
# ---------------------------------------------------------------------------

def carregar_mapbiomas() -> pd.DataFrame:
    """
    Lê o arquivo xlsx em cache e retorna DataFrame com colunas:
    [ano, classe_id, area_ha] para Goiás.
    """
    arquivo = DIR_RAW / "mapbiomas_col10_estado.xlsx"
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo MapBiomas não encontrado em {arquivo}. "
            "Execute primeiro grafico_pastagem_pib_goias.py para baixar."
        )
    print(f"[OK] Lendo {arquivo.name} do cache...")

    xls = pd.ExcelFile(arquivo)
    aba = next(
        (s for s in xls.sheet_names
         if str(ANO_INICIO) in pd.read_excel(arquivo, sheet_name=s, nrows=2).columns.astype(str)),
        None,
    )
    if aba is None:
        raise ValueError(f"Aba de dados não encontrada. Abas: {xls.sheet_names}")
    print(f"  Aba: '{aba}'")

    df = pd.read_excel(arquivo, sheet_name=aba)
    df.columns = [str(c) for c in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}

    col_estado = next(
        (cols_lower[k] for k in ("state", "estado", "uf") if k in cols_lower), None
    )
    col_classe_id = next(
        (cols_lower[k] for k in ("feature_id", "class_id", "id_class") if k in cols_lower), None
    )
    if col_estado is None or col_classe_id is None:
        raise ValueError(f"Colunas esperadas não encontradas. Disponíveis: {list(df.columns)[:20]}")

    # Filtrar Goiás
    df_go = df[
        df[col_estado].astype(str).str.strip().str.upper().isin([UF_NOME.upper(), UF_SIGLA])
    ].copy()
    print(f"  Linhas Goiás: {len(df_go)}")

    cols_anos = [c for c in df.columns if c.isdigit() and ANO_INICIO <= int(c) <= ANO_FIM]

    # Derreter para formato longo
    df_long = df_go[[col_classe_id] + cols_anos].copy()
    df_long = df_long.rename(columns={col_classe_id: "classe_id"})
    df_long = df_long.melt(id_vars="classe_id", var_name="ano", value_name="area_ha")
    df_long["ano"] = df_long["ano"].astype(int)
    df_long["area_ha"] = pd.to_numeric(df_long["area_ha"], errors="coerce").fillna(0)
    df_long["classe_id"] = pd.to_numeric(df_long["classe_id"], errors="coerce")

    # Somar por classe e ano (múltiplos biomas)
    df_agg = df_long.groupby(["ano", "classe_id"], as_index=False)["area_ha"].sum()
    print(f"  Classes disponíveis: {sorted(df_agg['classe_id'].dropna().unique().tolist())}")
    return df_agg


def montar_grupos(df_agg: pd.DataFrame) -> pd.DataFrame:
    """Soma as classes em grupos e retorna DataFrame wide [ano, grupo1, grupo2, ...]."""
    anos = sorted(df_agg["ano"].unique())
    registros = []
    for ano in anos:
        linha = {"ano": ano}
        for grupo, ids in GRUPOS.items():
            total = df_agg.loc[
                (df_agg["ano"] == ano) & (df_agg["classe_id"].isin(ids)),
                "area_ha"
            ].sum()
            linha[grupo] = total / 1e6  # Mha
        registros.append(linha)
    return pd.DataFrame(registros)


# ---------------------------------------------------------------------------
# 2. Rebanho bovino — SIDRA PPM tabela 3939
# ---------------------------------------------------------------------------

def baixar_rebanho_bovino() -> pd.DataFrame:
    """
    Baixa o efetivo de rebanho bovino em Goiás via SIDRA (PPM, tabela 3939).
    Variável 105: Efetivo dos rebanhos (cabeças). Tipo D4C=0 = total.
    Disponibilidade: 1974–ano mais recente.
    """
    import sidrapy

    print("[...] Baixando rebanho bovino (SIDRA tabela 3939)...")
    df = sidrapy.get_table(
        table_code="3939",
        territorial_level="3",
        ibge_territorial_code=str(UF_CODIGO_IBGE),
        period="all",
        variable="105",
        classifications={"79": "2670"},  # classif 79 = tipo rebanho; 2670 = Bovinos
    )
    df = df.iloc[1:].copy()
    df["ano"]     = pd.to_numeric(df["D2C"], errors="coerce")
    df["bovinos"] = pd.to_numeric(df["V"].replace("..", float("nan")), errors="coerce")
    df = df[["ano", "bovinos"]].dropna().sort_values("ano").reset_index(drop=True)
    df["ano"]     = df["ano"].astype(int)
    df["bovinos"] = df["bovinos"].astype(float)
    df = df[(df["ano"] >= ANO_INICIO) & (df["ano"] <= ANO_FIM)]
    print(f"[OK] Rebanho bovino: {df['ano'].min()}–{df['ano'].max()} ({len(df)} anos)")
    return df


# ---------------------------------------------------------------------------
# 3. PIB agropecuário — SIDRA Contas Regionais tabela 5938
#    Variável 513 = VA agropecuária a preços correntes (mil R$)
# ---------------------------------------------------------------------------

def baixar_pib_agro() -> pd.DataFrame:
    """
    Baixa o Valor Adicionado da Agropecuária de Goiás via SIDRA (tabela 5938).
    Variável 513: VA Agropecuária a preços correntes (mil R$).
    """
    import sidrapy

    print("[...] Baixando VA agropecuário (SIDRA tabela 5938, var 513)...")
    df = sidrapy.get_table(
        table_code="5938",
        territorial_level="3",
        ibge_territorial_code=str(UF_CODIGO_IBGE),
        period="all",
        variable="513",
    )
    df = df.iloc[1:].copy()
    df["ano"] = df["D2C"].astype(int)
    df["va_agro_nominal_rs"] = pd.to_numeric(df["V"], errors="coerce") * 1000
    df = df[["ano", "va_agro_nominal_rs"]].sort_values("ano").reset_index(drop=True)
    print(f"[OK] VA agro: {df['ano'].min()}–{df['ano'].max()} ({len(df)} anos)")
    return df


def baixar_pib_total() -> pd.DataFrame:
    """PIB total nominal de Goiás (variável 37)."""
    import sidrapy

    print("[...] Baixando PIB total (SIDRA tabela 5938, var 37)...")
    df = sidrapy.get_table(
        table_code="5938",
        territorial_level="3",
        ibge_territorial_code=str(UF_CODIGO_IBGE),
        period="all",
        variable="37",
    )
    df = df.iloc[1:].copy()
    df["ano"] = df["D2C"].astype(int)
    df["pib_nominal_rs"] = pd.to_numeric(df["V"], errors="coerce") * 1000
    df = df[["ano", "pib_nominal_rs"]].sort_values("ano").reset_index(drop=True)
    return df


def baixar_ipca() -> pd.DataFrame:
    import sidrapy

    print("[...] Baixando IPCA (tabela 1737)...")
    df = sidrapy.get_table(
        table_code="1737",
        territorial_level="1",
        ibge_territorial_code="all",
        period="all",
        variable="63",
    )
    df = df.iloc[1:].copy()
    df["ano"] = df["D2C"].str[:4].astype(int)
    df["mes"] = df["D2C"].str[4:6].astype(int)
    df["var_mensal"] = pd.to_numeric(df["V"], errors="coerce")
    df = df.sort_values(["ano", "mes"]).reset_index(drop=True)
    df["indice_acum"] = (1 + df["var_mensal"] / 100).cumprod()
    return df[["ano", "mes", "indice_acum"]]


def deflacionar(df_nominal: pd.DataFrame, col_val: str, df_ipca: pd.DataFrame) -> pd.Series:
    """Deflaciona `col_val` para R$ de DATA_BASE_DEFLATOR usando dez de cada ano."""
    ano_base, mes_base = DATA_BASE_DEFLATOR
    idx_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base), "indice_acum"
    ].iloc[0]
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "idx_dez"}
    )
    merged = df_nominal.merge(df_dez, on="ano", how="left")
    return merged[col_val] * (idx_base / merged["idx_dez"])


# ---------------------------------------------------------------------------
# 4. Gráficos
# ---------------------------------------------------------------------------

def _salvar(fig, nome):
    fig.savefig(DIR_OUTPUT / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] outputs/{nome}")


def grafico_cobertura(df_grupos: pd.DataFrame) -> None:
    """Área chart empilhada das classes de cobertura."""
    grupos_order = list(GRUPOS.keys())
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.stackplot(
        df_grupos["ano"],
        [df_grupos[g] for g in grupos_order],
        labels=grupos_order,
        colors=[CORES_GRUPOS[g] for g in grupos_order],
        alpha=0.85,
    )
    ax.set_xlabel("Ano")
    ax.set_ylabel("Area (milhoes de hectares)")
    ax.set_title(f"Cobertura do solo em {UF_NOME} — MapBiomas Col. 10.1 (1985–2024)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2, axis="y")
    ax.set_xlim(ANO_INICIO, ANO_FIM)
    fig.tight_layout()
    _salvar(fig, "03_cobertura_goias_1985-2024.png")
    df_grupos.to_csv(DIR_PROCESSED / "cobertura_goias_grupos.csv", index=False)


def grafico_rebanho(df_rebanho: pd.DataFrame) -> None:
    """Rebanho bovino em Goiás."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_rebanho["ano"], df_rebanho["bovinos"] / 1e6,
            marker="o", markersize=3, linewidth=1.8, color="#8b2500")
    ax.fill_between(df_rebanho["ano"], df_rebanho["bovinos"] / 1e6, alpha=0.15, color="#8b2500")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Rebanho bovino (milhoes de cabecas)")
    ax.set_title(f"Rebanho bovino em {UF_NOME} — IBGE PPM (1985–2024)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _salvar(fig, "04_rebanho_bovino_goias.png")
    df_rebanho.to_csv(DIR_PROCESSED / "rebanho_bovino_goias.csv", index=False)


def grafico_lotacao(df_pasto: pd.DataFrame, df_rebanho: pd.DataFrame) -> None:
    """Taxa de lotacao implícita (bovinos/hectare de pastagem)."""
    merged = df_pasto.merge(df_rebanho, on="ano", how="inner")
    merged["area_ha"] = merged["area_pastagem_ha"]
    merged["lotacao"] = merged["bovinos"] / merged["area_ha"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

    ax1 = axes[0]
    ax1.plot(merged["ano"], merged["area_ha"] / 1e6, color="#a07830", lw=2, marker="o", ms=3)
    ax1.set_ylabel("Pastagem (Mha)")
    ax1.set_title(f"Pastagem, Rebanho e Lotacao em {UF_NOME}")
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.plot(merged["ano"], merged["bovinos"] / 1e6, color="#8b2500", lw=2, marker="s", ms=3)
    ax2.set_ylabel("Rebanho (Mi cabecas)")
    ax2.grid(True, alpha=0.3)

    ax3 = axes[2]
    ax3.plot(merged["ano"], merged["lotacao"], color="#2060a0", lw=2, marker="^", ms=4)
    ax3.axhline(1.0, color="gray", linestyle="--", lw=1, label="1 boi/ha")
    ax3.set_ylabel("Lotacao (bois/ha)")
    ax3.set_xlabel("Ano")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    fig.tight_layout()
    _salvar(fig, "05_lotacao_implícita_goias.png")
    merged[["ano", "area_ha", "bovinos", "lotacao"]].to_csv(
        DIR_PROCESSED / "lotacao_implicita_goias.csv", index=False
    )


def grafico_pib_agro(df_agro_real: pd.DataFrame, df_total_real: pd.DataFrame) -> None:
    """PIB agro real e participacao % no PIB total."""
    merged = df_agro_real.merge(df_total_real, on="ano", how="inner")
    merged["participacao_pct"] = merged["va_agro_real_rs"] / merged["pib_real_rs"] * 100

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    ax1 = axes[0]
    ax1.bar(merged["ano"], merged["va_agro_real_rs"] / 1e9,
            color="#2e7d32", alpha=0.8, label="VA Agropecuário real")
    ax1.plot(merged["ano"], merged["pib_real_rs"] / 1e9,
             color="#1a237e", lw=2, marker="s", ms=3, label="PIB total real")
    ax1.set_ylabel("R$ bilhoes (base 12/2024)")
    ax1.set_title(f"VA Agropecuario vs PIB total real em {UF_NOME}")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, axis="y")

    ax2 = axes[1]
    ax2.plot(merged["ano"], merged["participacao_pct"],
             color="#e65100", lw=2, marker="o", ms=4)
    ax2.fill_between(merged["ano"], merged["participacao_pct"], alpha=0.2, color="#e65100")
    ax2.set_ylabel("Participacao agro no PIB (%)")
    ax2.set_xlabel("Ano")
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))

    fig.tight_layout()
    _salvar(fig, "06_pib_agro_goias.png")
    merged.to_csv(DIR_PROCESSED / "pib_agro_goias.csv", index=False)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print(f"Analise expandida — {UF_NOME} ({ANO_INICIO}–{ANO_FIM})")
    print("=" * 70)

    # 1. Cobertura do solo (MapBiomas — cache)
    df_agg = carregar_mapbiomas()
    df_grupos = montar_grupos(df_agg)
    grafico_cobertura(df_grupos)

    # 2. Rebanho bovino (SIDRA PPM)
    df_rebanho = baixar_rebanho_bovino()
    grafico_rebanho(df_rebanho)

    # 3. Lotação (pastagem × rebanho)
    df_pasto = pd.read_csv(DIR_PROCESSED / "pastagem_goias_anual.csv")
    grafico_lotacao(df_pasto, df_rebanho)

    # 4. PIB agropecuário (SIDRA Contas Regionais)
    df_ipca = baixar_ipca()
    df_agro_nom = baixar_pib_agro()
    df_total_nom = baixar_pib_total()
    df_agro_nom["va_agro_real_rs"] = deflacionar(df_agro_nom, "va_agro_nominal_rs", df_ipca)
    df_total_nom["pib_real_rs"]    = deflacionar(df_total_nom, "pib_nominal_rs", df_ipca)
    grafico_pib_agro(df_agro_nom, df_total_nom)

    print("\nFeito! Graficos em outputs/, CSVs em data/processed/")


if __name__ == "__main__":
    main()
