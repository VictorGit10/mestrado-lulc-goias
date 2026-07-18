"""coleta_firjan_ifdm.py — Coletor do IFDM (Índice FIRJAN de Desenvolvimento Municipal)
======================================================================================

Baixa e processa a **Nova Série Histórica do IFDM (2013–2023)**, nível MUNICIPAL,
para os municípios de Goiás. Reabre o eixo de DESENVOLVIMENTO que estava travado por
falta de dado municipal pós-2010 (o IDH-M municipal do #13 só existe 1991/2000/2010).

Diferença crucial em relação ao IDH-M:
  - o IFDM é ANUAL e alcança o **Ato III** (2020–2023), onde a divergência Sul/Norte
    é mais limpa (#32/#50);
  - é uma **série nova** (revisão metodológica; NÃO é emendável com a antiga 2005–2016),
    mas internamente consistente 2013–2023.

Fonte: FIRJAN — https://www.firjan.com.br/ifdm/downloads/
  Arquivo: "Série Histórica IFDM 2013 a 2023" (XLSX, ~5,8 MB).
  4 abas: IFDM Geral, IFDM Educação, IFDM Saúde, IFDM Emprego&Renda.
  Layout por aba: COD_MUNIC (6 díg.), SIGLA_UF, NOME_MUNIC, e por ano
  ["Ranking Estadual…", "Ranking IFDM YYYY", "IFDM… YYYY"] — só a coluna de valor
  "IFDM… YYYY" nos interessa.

Chave municipal: o COD_MUNIC do FIRJAN é o código IBGE de **6 dígitos** (sem o dígito
verificador). O painel usa o código de **7 dígitos**. A ponte é exata e sem cálculo de
DV: `cd_mun_7dig // 10 == COD_MUNIC_6dig` (o DV é apenas anexado). Fazemos o merge
contra os 246 municípios de Goiás já no painel — o que também serve de filtro e valida
a cobertura.

Saída:
  data/processed/ifdm_goias_municipal.csv
  Schema (longo por ano): cd_mun, nm_mun, ano, ifdm, ifdm_emprego, ifdm_educacao, ifdm_saude

Como rodar:
    py -3.14 scripts/coleta_firjan_ifdm.py            # baixa se preciso + processa
    py -3.14 scripts/coleta_firjan_ifdm.py --force    # reprocessa mesmo com cache
    py -3.14 scripts/coleta_firjan_ifdm.py --offline  # só usa o XLSX local em data/raw/firjan/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import requests

ROOT          = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw" / "firjan"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

URL_IFDM = ("https://firjan.com.br/data/files/09/42/7A/34/0EFA6910734FAA69D8284EA8/"
            "Serie-Historica-IFDM-2013-a-2023.xlsx")
ARQ_XLSX = DIR_RAW / "Serie-Historica-IFDM-2013-a-2023.xlsx"
OUT_CSV  = DIR_PROCESSED / "ifdm_goias_municipal.csv"

# aba -> coluna de saída no schema longo
ABAS = {
    "IFDM Geral":        "ifdm",
    "IFDM Emprego&Renda":"ifdm_emprego",
    "IFDM Educação":     "ifdm_educacao",
    "IFDM Saúde":        "ifdm_saude",
}
COLS_SAIDA = ["cd_mun", "nm_mun", "ano", "ifdm", "ifdm_emprego", "ifdm_educacao", "ifdm_saude"]


def baixar(force: bool = False) -> None:
    if ARQ_XLSX.exists() and not force:
        return
    print(f"[download] {URL_IFDM}")
    r = requests.get(URL_IFDM, timeout=180, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    ARQ_XLSX.write_bytes(r.content)
    print(f"  -> {ARQ_XLSX.relative_to(ROOT)} ({len(r.content):,} bytes)")


def _achar_aba(xl: pd.ExcelFile, alvo: str) -> str:
    """Casa o nome da aba de forma tolerante a acento/encoding."""
    norm = lambda s: re.sub(r"[^a-z]", "", s.lower())
    for sh in xl.sheet_names:
        if norm(sh) == norm(alvo):
            return sh
    raise KeyError(f"aba '{alvo}' não encontrada; abas: {xl.sheet_names}")


def _ler_aba(xl: pd.ExcelFile, aba: str, col_valor: str) -> pd.DataFrame:
    """Aba wide -> longo (cod6, ano, valor). Só as colunas de VALOR 'IFDM… YYYY'."""
    df = xl.parse(aba, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    col_cod = next(c for c in df.columns if re.sub(r"[^A-Z]", "", c.upper()).startswith("CODMUNIC"))
    col_uf  = next(c for c in df.columns if "SIGLA" in c.upper())
    # colunas de valor: começam com 'IFDM', terminam em ano, e NÃO são 'Ranking'
    val_cols = {}
    for c in df.columns:
        if c.upper().startswith("IFDM") and "RANKING" not in c.upper():
            m = re.search(r"(20\d{2})\s*$", c)
            if m:
                val_cols[c] = int(m.group(1))
    if not val_cols:
        raise ValueError(f"nenhuma coluna de valor 'IFDM YYYY' na aba {aba}: {list(df.columns)}")

    go = df[df[col_uf].astype(str).str.strip().str.upper() == "GO"].copy()
    go["cod6"] = pd.to_numeric(go[col_cod], errors="coerce").astype("Int64")
    longo = go.melt(id_vars=["cod6"], value_vars=list(val_cols),
                    var_name="col", value_name=col_valor)
    longo["ano"] = longo["col"].map(val_cols)
    longo[col_valor] = pd.to_numeric(longo[col_valor], errors="coerce")
    return longo[["cod6", "ano", col_valor]]


def processar(force: bool = False, offline: bool = False) -> pd.DataFrame:
    if OUT_CSV.exists() and not force:
        df = pd.read_csv(OUT_CSV)
        print(f"[cache] {OUT_CSV.name} ({len(df):,} linhas)")
        return df

    if not offline:
        baixar(force=force)
    if not ARQ_XLSX.exists():
        sys.exit(f"ERRO: {ARQ_XLSX} não existe. Rode sem --offline para baixar.")

    xl = pd.ExcelFile(ARQ_XLSX)
    partes = []
    for alvo, col_valor in ABAS.items():
        aba = _achar_aba(xl, alvo)
        parte = _ler_aba(xl, aba, col_valor)
        print(f"  [{aba:20s}] {parte['cod6'].nunique()} munis GO × "
              f"{parte['ano'].nunique()} anos -> {col_valor}")
        partes.append(parte.set_index(["cod6", "ano"]))
    wide = pd.concat(partes, axis=1).reset_index()

    # --- ponte 6→7 dígitos via o painel (exato, sem cálculo de DV) ---
    painel_path = DIR_PROCESSED / "painel_unificado.parquet"
    if not painel_path.exists():
        sys.exit("ERRO: painel_unificado.parquet ausente — necessário p/ mapear cd_mun (7 díg.).")
    munis = (pd.read_parquet(painel_path, columns=["cd_mun", "nm_mun"])
             .drop_duplicates("cd_mun"))
    munis["cod6"] = munis["cd_mun"] // 10
    df = munis.merge(wide, on="cod6", how="inner")

    df = df[COLS_SAIDA].sort_values(["cd_mun", "ano"]).reset_index(drop=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # --- validação ---
    n_muni, anos = df["cd_mun"].nunique(), sorted(df["ano"].unique())
    print(f"\n[validação] {n_muni} municípios de Goiás | anos {anos[0]}–{anos[-1]} ({len(anos)})")
    if n_muni != 246:
        print(f"  ⚠ esperado 246 municípios de GO; obtido {n_muni} "
              f"(FIRJAN pode omitir municípios muito novos)")
    for c in ("ifdm", "ifdm_emprego", "ifdm_educacao", "ifdm_saude"):
        s = df[c]
        print(f"  {c:16s} [{s.min():.3f}, {s.max():.3f}] | {s.isna().sum()} NA")
    print(f"  -> {OUT_CSV.relative_to(ROOT)} ({len(df):,} linhas)")
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="reprocessa mesmo com cache")
    ap.add_argument("--offline", action="store_true", help="usa só o XLSX local")
    args = ap.parse_args()

    print("=" * 70)
    print("Coleta IFDM (FIRJAN) — Nova Série Histórica municipal 2013–2023")
    print("=" * 70)
    df = processar(force=args.force, offline=args.offline)
    print(f"\nIFDM Geral médio GO 2013: {df[df.ano==2013]['ifdm'].mean():.3f} | "
          f"2023: {df[df.ano==2023]['ifdm'].mean():.3f}")


if __name__ == "__main__":
    main()
