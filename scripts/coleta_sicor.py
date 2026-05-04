"""
Pipeline #6 — Coletor SICOR (BACEN, crédito rural)
====================================================

Baixa operações de crédito rural do SICOR via OData do BACEN, filtradas para
Goiás. Cobre 5 entidades:

    Granularidade municipal:
      - CusteioMunicipioProduto      (tem codIbge nativo)
      - InvestMunicipioProduto       (tem só cdMunicipio do BACEN — de-para via Custeio)

    Granularidade UF agregada:
      - CusteioRegiaoUFProduto
      - InvestRegiaoUFProduto
      - ComercRegiaoUFProduto

Período: 2013 a 2026 (cobertura completa do SICOR; 2026 parcial — registrar
na análise). Não há série pré-2013 nessa API.

Idiossincrasias do Olinda BACEN (descobertas em sondagem 2026-04-27):
  - $filter eq exige %20 entre tokens (NÃO +). requests.get(params=) usa +
    e quebra a API; precisamos montar a URL manualmente com urllib.quote.
  - $skip, $count, $orderby, $apply não funcionam.
  - Apenas $filter eq, AND, $top, $select são confiáveis.
  - cdEstado BACEN para Goiás = '10' (não é o código IBGE 52).
  - nomeUF nos datasets UF é a sigla 'GO' (não 'GOIÁS').

Estratégia de paginação:
  Sem $skip, segmentamos por (AnoEmissao, cdEstado|nomeUF) — uma chamada
  por ano. Volumes em Goiás cabem folgados em $top=50000:
    Custeio municipal: ~14k–20k registros/ano
    Investimento municipal: ~10k–17k registros/ano

Saídas em data/processed/:
  - sicor_custeio_municipal.csv     (1 linha por operação, com cd_mun IBGE)
  - sicor_invest_municipal.csv      (1 linha por operação, com cd_municipio_bacen)
  - sicor_de_para_municipio.csv     (mapping cdMunicipio BACEN ↔ codIbge)
  - sicor_uf_anual.csv              (3 finalidades agregadas UF, longo)
  - sicor_painel_municipal.csv      (Custeio+Invest unificado, ano × município × finalidade)

Cache em data/raw/sicor/<endpoint>_<ano>.json (1 arquivo por chamada).
Re-execuções usam o cache — apague o diretório para forçar redownload.

Uso:
    python coleta_sicor.py                    # baixa só o que faltar
    python coleta_sicor.py --force            # ignora cache
    python coleta_sicor.py --so custeio       # roda só endpoints com 'custeio' no nome
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
# Configuração
# ---------------------------------------------------------------------------
ROOT           = Path(__file__).resolve().parent.parent
DIR_RAW_SICOR = ROOT / "data" / "raw" / "sicor"
DIR_PROCESSED = ROOT / "data" / "processed"
for d in (DIR_RAW_SICOR, DIR_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/SICOR/versao/v2/odata"
ESTADO_BACEN_GO = "10"   # cdEstado do BACEN para Goiás (NÃO é o IBGE 52)
SIGLA_UF_GO     = "GO"   # nomeUF nos datasets *RegiaoUFProduto

ANO_INI = 2013   # primeiro ano disponível no SICOR
ANO_FIM = 2026   # último ano com registros (parcial em curso)
TOP_MAX = 50000  # cabe folgado para qualquer (UF, ano) no SICOR

TIMEOUT = 240    # segundos por request


# ---------------------------------------------------------------------------
# Camada HTTP — Olinda OData com %20 manual
# ---------------------------------------------------------------------------

def _build_url(endpoint: str, **odata_params) -> str:
    """
    Monta URL com parâmetros OData usando %20 entre tokens.
    O Olinda quebra com '+' (form-encoding), exige %20 puro.
    """
    parts = [f"{k}={quote(str(v), safe='')}" for k, v in odata_params.items()]
    return f"{BASE_URL}/{endpoint}?{'&'.join(parts)}"


def _odata_get(endpoint: str, **odata_params) -> list[dict]:
    """
    GET no Olinda com retry simples. Retorna lista de registros.
    """
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
    """
    Baixa todos os registros de um (endpoint, ano) filtrando pela UF.
    Usa cache JSON em data/raw/sicor/<endpoint>_<ano>.json.
    """
    cache = DIR_RAW_SICOR / f"{endpoint}_{ano}.json"
    if cache.exists() and not force:
        with cache.open(encoding="utf-8") as f:
            return json.load(f)

    filtro = f"AnoEmissao eq '{ano}' and {filtro_uf}"
    print(f"    [GET] {endpoint} ano={ano}", end=" ", flush=True)
    t0 = time.time()
    registros = _odata_get(endpoint,
                           **{"$filter": filtro, "$top": TOP_MAX,
                              "$format": "json"})
    dt = time.time() - t0
    print(f"→ {len(registros):>6} registros ({dt:.1f}s)")

    # Sanity: se bater no teto exato, há risco de truncamento
    if len(registros) >= TOP_MAX:
        print(f"      AVISO: resultado bateu em $top={TOP_MAX} — possível truncamento")

    with cache.open("w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False)
    return registros


# ---------------------------------------------------------------------------
# Coletores por entidade
# ---------------------------------------------------------------------------

def coletar_custeio_municipal(force: bool = False) -> pd.DataFrame:
    """
    CusteioMunicipioProduto, filtrado por cdEstado (Goiás = '10').
    Inclui o codIbge nativo — pronto para join com SIDRA/MapBiomas.
    """
    print("\n[COLETA] CusteioMunicipioProduto (Goiás, cdEstado=10)")
    filtro_uf = f"cdEstado eq '{ESTADO_BACEN_GO}'"

    todos = []
    for ano in range(ANO_INI, ANO_FIM + 1):
        todos.extend(_baixar_ano("CusteioMunicipioProduto", ano, filtro_uf, force))

    df = pd.DataFrame(todos)
    if df.empty:
        return df

    # Normalização de tipos e nomes
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
    # Limpa aspas duplas vindas no nome do produto ("MILHO" → MILHO)
    df["nm_produto"] = df["nm_produto"].str.strip('"')

    cols = ["ano", "mes", "cd_mun", "nm_mun", "cd_municipio_bacen", "cd_estado_bacen",
            "cd_programa", "cd_subprograma", "cd_fonte_recurso", "cd_tipo_seguro",
            "atividade", "cd_modalidade", "cd_produto", "nm_produto",
            "valor", "area_ha"]
    df = df[cols].sort_values(["ano", "mes", "cd_mun"]).reset_index(drop=True)

    out = DIR_PROCESSED / "sicor_custeio_municipal.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df):,} linhas, {df['cd_mun'].nunique()} munis")
    return df


def coletar_invest_municipal(force: bool = False) -> pd.DataFrame:
    """
    InvestMunicipioProduto, filtrado por cdEstado (Goiás = '10').
    Tem só cdMunicipio do BACEN — codIbge anexado depois via de-para.
    """
    print("\n[COLETA] InvestMunicipioProduto (Goiás, cdEstado=10)")
    filtro_uf = f"cdEstado eq '{ESTADO_BACEN_GO}'"

    todos = []
    for ano in range(ANO_INI, ANO_FIM + 1):
        todos.extend(_baixar_ano("InvestMunicipioProduto", ano, filtro_uf, force))

    df = pd.DataFrame(todos)
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

    out = DIR_PROCESSED / "sicor_invest_municipal.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df):,} linhas, "
          f"{df['cd_municipio_bacen'].nunique()} munis (BACEN)")
    return df


def coletar_uf(force: bool = False) -> pd.DataFrame:
    """
    Concatena os 3 datasets *RegiaoUFProduto, filtrando por nomeUF='GO'.
    Salva em formato longo com coluna 'finalidade'.
    """
    print(f"\n[COLETA] Painéis UF (CusteioRegiao + InvestRegiao + ComercRegiao, nomeUF=GO)")
    filtro_uf = f"nomeUF eq '{SIGLA_UF_GO}'"

    blocos = []
    spec = [
        ("CusteioRegiaoUFProduto", "Custeio", "VlCusteio", "QtdCusteio"),
        ("InvestRegiaoUFProduto",  "Investimento", "VlInvest", "QtdInvest"),
        ("ComercRegiaoUFProduto",  "Comercializacao", "VlComerc", "QtdComerc"),
    ]
    for endpoint, finalidade, vl_col, qt_col in spec:
        regs = []
        for ano in range(ANO_INI, ANO_FIM + 1):
            regs.extend(_baixar_ano(endpoint, ano, filtro_uf, force))

        if not regs:
            print(f"  [vazio] {endpoint}")
            continue

        df = pd.DataFrame(regs)
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

        # Comercialização não tem AreaXxxx; garantir coluna mesmo que ausente
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

    out = DIR_PROCESSED / "sicor_uf_anual.csv"
    df_uf.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(df_uf):,} linhas")
    return df_uf


# ---------------------------------------------------------------------------
# Pós-processamento
# ---------------------------------------------------------------------------

def gerar_de_para_municipios(df_custeio: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói tabela de-para cdMunicipio BACEN → codIbge a partir do Custeio
    (que tem ambos). Usado para anexar codIbge ao painel de Investimento.

    Sanidade: cada cd_municipio_bacen deve mapear para um único cd_mun IBGE.
    """
    print("\n[POST] Construindo de-para cdMunicipio BACEN → codIbge")
    de_para = (df_custeio[["cd_municipio_bacen", "cd_mun", "nm_mun"]]
               .dropna(subset=["cd_municipio_bacen", "cd_mun"])
               .drop_duplicates())

    # Sanidade: 1 cd_municipio_bacen por cd_mun?
    grupos = de_para.groupby("cd_municipio_bacen")["cd_mun"].nunique()
    ambiguos = grupos[grupos > 1]
    if not ambiguos.empty:
        print(f"  AVISO: {len(ambiguos)} cd_municipio_bacen com múltiplos cd_mun:")
        print(ambiguos.head().to_string())

    out = DIR_PROCESSED / "sicor_de_para_municipio.csv"
    de_para.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(de_para)} entradas")
    return de_para


def consolidar_painel_municipal(df_custeio: pd.DataFrame,
                                 df_invest: pd.DataFrame,
                                 de_para: pd.DataFrame) -> pd.DataFrame:
    """
    Une Custeio e Investimento em um único painel municipal anual:
      ano × cd_mun × finalidade × cd_programa × atividade  →  valor + área + n_op

    Resolve o cd_mun do Investimento via de-para.
    """
    print("\n[POST] Consolidando painel municipal (Custeio + Investimento)")

    # Anexar cd_mun do IBGE ao Investimento
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

    # Adicionar coluna 'finalidade' e padronizar
    df_custeio_p = df_custeio.assign(finalidade="Custeio")
    df_invest_p  = invest.assign(finalidade="Investimento")

    cols = ["ano", "cd_mun", "nm_mun", "finalidade", "cd_programa",
            "cd_subprograma", "cd_fonte_recurso", "atividade", "cd_modalidade",
            "cd_produto", "nm_produto", "valor", "area_ha"]
    cust = df_custeio_p[cols]
    inv  = df_invest_p[cols]

    longo = pd.concat([cust, inv], ignore_index=True)
    longo["cd_mun"] = longo["cd_mun"].astype("Int64")

    # Painel agregado: 1 linha por (ano, cd_mun, finalidade, programa, atividade)
    painel = (longo
              .groupby(["ano", "cd_mun", "finalidade", "cd_programa",
                        "atividade", "cd_modalidade"], dropna=False)
              .agg(valor=("valor", "sum"),
                   area_ha=("area_ha", "sum"),
                   n_operacoes=("valor", "count"))
              .reset_index())

    # Anexar nome do município (1 representativo)
    nomes = (df_custeio[["cd_mun", "nm_mun"]]
             .dropna()
             .drop_duplicates(subset=["cd_mun"]))
    painel = painel.merge(nomes, on="cd_mun", how="left")

    # Reordenar colunas
    cols_final = ["ano", "cd_mun", "nm_mun", "finalidade", "cd_programa",
                  "atividade", "cd_modalidade", "valor", "area_ha", "n_operacoes"]
    painel = painel[cols_final].sort_values(
        ["ano", "cd_mun", "finalidade", "cd_programa", "atividade"]
    ).reset_index(drop=True)

    out = DIR_PROCESSED / "sicor_painel_municipal.csv"
    painel.to_csv(out, index=False, encoding="utf-8")
    print(f"  [OK] {out.name} — {len(painel):,} linhas, "
          f"{painel['cd_mun'].nunique()} munis, "
          f"R$ {painel['valor'].sum()/1e9:.2f} bi (nominal, total Goiás 2013-2026)")
    return painel


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main(force: bool = False, so: list[str] | None = None) -> None:
    print("=" * 70)
    print("Pipeline #6 — Coletor SICOR (BACEN, Goiás 2013-2026)")
    print("=" * 70)

    rodar = lambda nome: not so or any(s.lower() in nome.lower() for s in so)

    df_cust = pd.DataFrame()
    df_inv  = pd.DataFrame()

    if rodar("custeio_municipal"):
        df_cust = coletar_custeio_municipal(force=force)
    else:
        # Carrega cache do CSV se existir, para o de-para
        p = DIR_PROCESSED / "sicor_custeio_municipal.csv"
        if p.exists():
            df_cust = pd.read_csv(p, encoding="utf-8")

    if rodar("invest_municipal"):
        df_inv = coletar_invest_municipal(force=force)
    else:
        p = DIR_PROCESSED / "sicor_invest_municipal.csv"
        if p.exists():
            df_inv = pd.read_csv(p, encoding="utf-8")

    if rodar("uf"):
        coletar_uf(force=force)

    # Pós-processamento exige Custeio + Invest carregados
    if not df_cust.empty and not df_inv.empty and rodar("painel"):
        de_para = gerar_de_para_municipios(df_cust)
        consolidar_painel_municipal(df_cust, df_inv, de_para)

    print("\n" + "=" * 70)
    print("Pipeline #6 concluído.")
    print("=" * 70)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true",
                   help="ignora cache e rebaixa tudo")
    p.add_argument("--so", nargs="+",
                   help="rodar só endpoints com essas substrings (ex: 'custeio uf')")
    args = p.parse_args()
    main(force=args.force, so=args.so)
