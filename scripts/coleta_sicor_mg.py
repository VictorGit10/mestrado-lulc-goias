"""coleta_sicor_mg.py — Coletor SICOR (BACEN, crédito rural) para Minas Gerais

Adaptado de coleta_sicor.py. Usa cdEstado BACEN=12 e nomeUF='MG'.
Salva CSVs com sufixo _mg em data/processed/.

Diferenças em relação ao GO:
  - cdEstado BACEN: MG=12 (GO=10)
  - nomeUF: 'MG' (GO='GO')
  - 853 municípios (GO=246)
  - Cache em data/raw/sicor_mg/

Uso:
    python coleta_sicor_mg.py
    python coleta_sicor_mg.py --force
    python coleta_sicor_mg.py --so custeio
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Configuração MG
# ---------------------------------------------------------------------------
ROOT            = Path(__file__).resolve().parent.parent
DIR_RAW_SICOR_MG = ROOT / "data" / "raw" / "sicor_mg"
DIR_PROCESSED    = ROOT / "data" / "processed"
for d in (DIR_RAW_SICOR_MG, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/SICOR/versao/v2/odata"
ESTADO_BACEN_MG = "12"   # cdEstado do BACEN para Minas Gerais (não é o IBGE 31)
SIGLA_UF_MG     = "MG"   # nomeUF nos datasets *RegiaoUFProduto

ANO_INI = 2013
ANO_FIM = 2026
TOP_MAX = 50000
TIMEOUT = 240
SUFIXO  = "_mg"


# ---------------------------------------------------------------------------
# Camada HTTP — Olinda OData com %20 manual
# ---------------------------------------------------------------------------

def _build_url(endpoint: str, **odata_params) -> str:
    parts = [f"{k}={quote(str(v), safe='')}" for k, v in odata_params.items()]
    return f"{BASE_URL}/{endpoint}?{'&'.join(parts)}"


def _odata_get(endpoint: str, **odata_params) -> list[dict]:
    odata_params.setdefault("$format", "json")
    url = _build_url(endpoint, **odata_params)
    for tentativa in range(1, 4):
        try:
            r = requests.get(url, timeout=TIMEOUT)
            if r.ok:
                j = r.json()
                return j.get("value", [])
            print(f"      [HTTP {r.status_code}] {r.text[:200]}")
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"      [erro tentativa {tentativa}] {e}")
        if tentativa < 3:
            time.sleep(5 * tentativa)
    raise RuntimeError(f"Falha após 3 tentativas: {url}")


def _baixar_ano(endpoint: str, ano: int, filtro_uf: str,
                force: bool = False) -> list[dict]:
    cache = DIR_RAW_SICOR_MG / f"{endpoint}_{ano}.json"
    if cache.exists() and not force:
        with cache.open(encoding="utf-8") as f:
            return json.load(f)

    # Segmentar por MesEmissao — $skip não funciona na API Olinda do BACEN.
    # Com 853 municípios, cada mês fica bem abaixo de 50k registros.
    print(f"    [GET] {endpoint} ano={ano}", end=" ", flush=True)
    t0 = time.time()

    todos = []
    for mes in range(1, 13):
        filtro = f"AnoEmissao eq '{ano}' and MesEmissao eq '{mes}' and {filtro_uf}"
        page = _odata_get(endpoint,
                          **{"$filter": filtro, "$top": TOP_MAX, "$format": "json"})
        todos.extend(page)

    dt = time.time() - t0
    print(f"→ {len(todos):>6} registros ({dt:.1f}s)")

    with cache.open("w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False)
    return todos


# ---------------------------------------------------------------------------
# Coletores por entidade
# ---------------------------------------------------------------------------

def coletar_custeio_municipal(force: bool = False) -> pd.DataFrame:
    print(f"\n[COLETA] CusteioMunicipioProduto (Minas Gerais, cdEstado=12)")
    filtro_uf = f"cdEstado eq '{ESTADO_BACEN_MG}'"

    dfs = []
    for ano in range(ANO_INI, ANO_FIM + 1):
        registros = _baixar_ano("CusteioMunicipioProduto", ano, filtro_uf, force)
        if registros:
            dfs.append(pd.DataFrame(registros))
            del registros
    df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    if df.empty:
        return df

    df = df.rename(columns={
        "codIbge": "cd_mun",
        "codCadMu": "cd_municipio_bacen",
        "Municipio": "nm_mun",
        "cdEstado": "cd_estado_bacen",
        "AnoEmissao": "ano",
        "MesEmissao": "mes",
        "cdPrograma": "cd_programa",
        "cdSubPrograma": "cd_subprograma",
        "cdFonteRecurso": "cd_fonte_recurso",
        "cdTipoSeguro": "cd_tipo_seguro",
        "Atividade": "atividade",
        "cdModalidade": "cd_modalidade",
        "cdProduto": "cd_produto",
        "nomeProduto": "nm_produto",
        "VlCusteio": "valor",
        "AreaCusteio": "area_ha",
    })
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)
    df["cd_mun"] = pd.to_numeric(df["cd_mun"], errors="coerce").astype("Int64")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["area_ha"] = pd.to_numeric(df["area_ha"], errors="coerce")
    df["nm_produto"] = df["nm_produto"].str.strip('"')

    cols = ["ano", "mes", "cd_mun", "nm_mun", "cd_municipio_bacen", "cd_estado_bacen",
            "cd_programa", "cd_subprograma", "cd_fonte_recurso", "cd_tipo_seguro",
            "atividade", "cd_modalidade", "cd_produto", "nm_produto",
            "valor", "area_ha"]
    df = df[cols].sort_values(["ano", "mes", "cd_mun"]).reset_index(drop=True)

    out = DIR_PROCESSED / f"sicor_custeio_municipal{SUFIXO}.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df):,} linhas, {df['cd_mun'].nunique()} munis")
    return df


def coletar_invest_municipal(force: bool = False) -> pd.DataFrame:
    print(f"\n[COLETA] InvestMunicipioProduto (Minas Gerais, cdEstado=12)")
    filtro_uf = f"cdEstado eq '{ESTADO_BACEN_MG}'"

    dfs = []
    for ano in range(ANO_INI, ANO_FIM + 1):
        registros = _baixar_ano("InvestMunicipioProduto", ano, filtro_uf, force)
        if registros:
            dfs.append(pd.DataFrame(registros))
            del registros
    df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    if df.empty:
        return df

    df = df.rename(columns={
        "cdMunicipio": "cd_municipio_bacen",
        "Municipio": "nm_mun",
        "cdEstado": "cd_estado_bacen",
        "AnoEmissao": "ano",
        "MesEmissao": "mes",
        "cdPrograma": "cd_programa",
        "cdSubPrograma": "cd_subprograma",
        "cdFonteRecurso": "cd_fonte_recurso",
        "cdTipoSeguro": "cd_tipo_seguro",
        "Atividade": "atividade",
        "cdModalidade": "cd_modalidade",
        "cdProduto": "cd_produto",
        "nomeProduto": "nm_produto",
        "VlInvest": "valor",
        "AreaInvest": "area_ha",
    })
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["area_ha"] = pd.to_numeric(df["area_ha"], errors="coerce")
    df["nm_produto"] = df["nm_produto"].str.strip('"')

    cols = ["ano", "mes", "cd_municipio_bacen", "nm_mun", "cd_estado_bacen",
            "cd_programa", "cd_subprograma", "cd_fonte_recurso", "cd_tipo_seguro",
            "atividade", "cd_modalidade", "cd_produto", "nm_produto",
            "valor", "area_ha"]
    df = df[cols].sort_values(["ano", "mes", "cd_municipio_bacen"]).reset_index(drop=True)

    out = DIR_PROCESSED / f"sicor_invest_municipal{SUFIXO}.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df):,} linhas, "
          f"{df['cd_municipio_bacen'].nunique()} munis (BACEN)")
    return df


def coletar_uf(force: bool = False) -> pd.DataFrame:
    print(f"\n[COLETA] Painéis UF (CusteioRegiao + InvestRegiao + ComercRegiao, nomeUF=MG)")
    filtro_uf = f"nomeUF eq '{SIGLA_UF_MG}'"

    blocos = []
    spec = [
        ("CusteioRegiaoUFProduto", "Custeio", "VlCusteio", "QtdCusteio"),
        ("InvestRegiaoUFProduto",  "Investimento", "VlInvest", "QtdInvest"),
        ("ComercRegiaoUFProduto",  "Comercializacao", "VlComerc", "QtdComerc"),
    ]
    for endpoint, finalidade, vl_col, qt_col in spec:
        dfs_uf = []
        for ano in range(ANO_INI, ANO_FIM + 1):
            regs = _baixar_ano(endpoint, ano, filtro_uf, force)
            if regs:
                dfs_uf.append(pd.DataFrame(regs))
                del regs

        if not dfs_uf:
            print(f"  [vazio] {endpoint}")
            continue

        df = pd.concat(dfs_uf, ignore_index=True)
        df = df.rename(columns={
            "AnoEmissao": "ano",
            "MesEmissao": "mes",
            "nomeUF": "sigla_uf",
            "nomeRegiao": "nome_regiao",
            "cdPrograma": "cd_programa",
            "cdSubPrograma": "cd_subprograma",
            "cdFonteRecurso": "cd_fonte_recurso",
            "cdTipoSeguro": "cd_tipo_seguro",
            "nomeProduto": "nm_produto",
            "Atividade": "atividade",
            "cdModalidade": "cd_modalidade",
            vl_col: "valor",
            qt_col: "n_contratos",
        })
        df["finalidade"] = finalidade
        df["ano"] = df["ano"].astype(int)
        df["mes"] = df["mes"].astype(int)
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["n_contratos"] = pd.to_numeric(df["n_contratos"], errors="coerce").astype("Int64")
        df["nm_produto"] = df["nm_produto"].str.strip('"')

        if "AreaCusteio" in df.columns:
            df["area_ha"] = pd.to_numeric(df["AreaCusteio"], errors="coerce")
        elif "AreaInvest" in df.columns:
            df["area_ha"] = pd.to_numeric(df["AreaInvest"], errors="coerce")
        else:
            df["area_ha"] = pd.NA

        cols = ["ano", "mes", "sigla_uf", "nome_regiao", "finalidade",
                "cd_programa", "cd_subprograma", "cd_fonte_recurso", "cd_tipo_seguro",
                "atividade", "cd_modalidade", "nm_produto",
                "valor", "n_contratos", "area_ha"]
        df = df[cols]
        blocos.append(df)
        print(f"  {endpoint}: {len(df):,} linhas")

    if not blocos:
        return pd.DataFrame()

    df_uf = pd.concat(blocos, ignore_index=True)
    df_uf = df_uf.sort_values(["ano", "mes", "finalidade"]).reset_index(drop=True)

    out = DIR_PROCESSED / f"sicor_uf_anual{SUFIXO}.csv"
    df_uf.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df_uf):,} linhas")
    return df_uf


# ---------------------------------------------------------------------------
# Pós-processamento
# ---------------------------------------------------------------------------

def gerar_de_para_municipios(df_custeio: pd.DataFrame) -> pd.DataFrame:
    print("\n[POST] Construindo de-para cdMunicipio BACEN → codIbge (MG)")
    de_para = (df_custeio[["cd_municipio_bacen", "cd_mun", "nm_mun"]]
               .dropna(subset=["cd_municipio_bacen", "cd_mun"])
               .drop_duplicates())

    grupos = de_para.groupby("cd_municipio_bacen")["cd_mun"].nunique()
    ambiguos = grupos[grupos > 1]
    if not ambiguos.empty:
        print(f"  AVISO: {len(ambiguos)} cd_municipio_bacen com múltiplos cd_mun:")
        print(ambiguos.head().to_string())

    out = DIR_PROCESSED / f"sicor_de_para_municipio{SUFIXO}.csv"
    de_para.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(de_para)} entradas")
    return de_para


def consolidar_painel_municipal(df_custeio: pd.DataFrame,
                                 df_invest: pd.DataFrame,
                                 de_para: pd.DataFrame) -> pd.DataFrame:
    print("\n[POST] Consolidando painel municipal MG (Custeio + Investimento)")

    invest = df_invest.merge(
        de_para[["cd_municipio_bacen", "cd_mun"]],
        on="cd_municipio_bacen",
        how="left",
    )
    sem_match = invest["cd_mun"].isna().sum()
    if sem_match:
        print(f"  AVISO: {sem_match:,} linhas de Investimento sem cd_mun IBGE "
              f"({sem_match/len(invest)*100:.1f}%) — descartadas")
        invest = invest.dropna(subset=["cd_mun"])

    df_custeio_p = df_custeio.assign(finalidade="Custeio")
    df_invest_p  = invest.assign(finalidade="Investimento")

    cols = ["ano", "cd_mun", "nm_mun", "finalidade", "cd_programa",
            "cd_subprograma", "cd_fonte_recurso", "atividade", "cd_modalidade",
            "cd_produto", "nm_produto", "valor", "area_ha"]
    cust = df_custeio_p[cols]
    inv  = df_invest_p[cols]

    longo = pd.concat([cust, inv], ignore_index=True)
    longo["cd_mun"] = longo["cd_mun"].astype("Int64")

    painel = (longo
              .groupby(["ano", "cd_mun", "finalidade", "cd_programa",
                        "atividade", "cd_modalidade"], dropna=False)
              .agg(valor=("valor", "sum"),
                   area_ha=("area_ha", "sum"),
                   n_operacoes=("valor", "count"))
              .reset_index())

    nomes = (df_custeio[["cd_mun", "nm_mun"]]
             .dropna()
             .drop_duplicates(subset=["cd_mun"]))
    painel = painel.merge(nomes, on="cd_mun", how="left")

    cols_final = ["ano", "cd_mun", "nm_mun", "finalidade", "cd_programa",
                  "atividade", "cd_modalidade", "valor", "area_ha", "n_operacoes"]
    painel = painel[cols_final].sort_values(
        ["ano", "cd_mun", "finalidade", "cd_programa", "atividade"]
    ).reset_index(drop=True)

    out = DIR_PROCESSED / f"sicor_painel_municipal{SUFIXO}.csv"
    painel.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(painel):,} linhas, "
          f"{painel['cd_mun'].nunique()} munis, "
          f"R$ {painel['valor'].sum()/1e9:.2f} bi (nominal, total MG 2013-2026)")
    return painel


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main(force: bool = False, so: list[str] | None = None) -> None:
    print("=" * 70)
    print("Coletor SICOR (BACEN, Minas Gerais 2013-2026)")
    print("=" * 70)

    rodar = lambda nome: not so or any(s.lower() in nome.lower() for s in so)

    df_cust = pd.DataFrame()
    df_inv  = pd.DataFrame()

    if rodar("custeio_municipal"):
        df_cust = coletar_custeio_municipal(force=force)
    else:
        p = DIR_PROCESSED / f"sicor_custeio_municipal{SUFIXO}.csv"
        if p.exists():
            df_cust = pd.read_csv(p, encoding="utf-8")

    if rodar("invest_municipal"):
        df_inv = coletar_invest_municipal(force=force)
    else:
        p = DIR_PROCESSED / f"sicor_invest_municipal{SUFIXO}.csv"
        if p.exists():
            df_inv = pd.read_csv(p, encoding="utf-8")

    if rodar("uf"):
        coletar_uf(force=force)

    if not df_cust.empty and not df_inv.empty and rodar("painel"):
        de_para = gerar_de_para_municipios(df_cust)
        consolidar_painel_municipal(df_cust, df_inv, de_para)

    print("\n" + "=" * 70)
    print("Coletor SICOR MG concluído.")
    print("=" * 70)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true",
                   help="ignora cache e rebaixa tudo")
    p.add_argument("--so", nargs="+",
                   help="rodar só endpoints com essas substrings (ex: 'custeio uf')")
    args = p.parse_args()
    main(force=args.force, so=args.so)