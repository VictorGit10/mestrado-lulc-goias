"""
coleta_trase.py -- Agregacao municipal anual dos datasets Trase.earth para Goias
================================================================================

Le os zips de cadeias produtivas baixados manualmente em data/raw/trase/, filtra
linhas com produto originado em GOIAS, mapeia o nome do municipio Trase (caixa
alta, sem acentos) para cd_mun IBGE via mapeamento_mesorregioes.csv, e agrega
por (cd_mun, ano).

Fontes (Trase.earth, CC BY 4.0):
  - Brazil beef v2.2.2 (2011-2017 + 2019-2023, sem 2018)
    URL: resources.trase.earth/20260511/data/supply-chains/brazil_beef_v2_2_2.zip
  - Brazil soy v2.6.1 composite (2004-2022)
    URL: resources.trase.earth/20260511/data/supply-chains/brazil_soy_v2_6_1_composite.zip
    DOI: 10.48650/DCE3-JJ97

Os zips contem 1 CSV cada. Beef e 1.86 GB descompactado, por isso usamos leitura
em chunks com filtro inline. Soy e 171 MB e cabe em memoria.

Saidas:
  data/processed/painel_trase.csv

Schema:
  cd_mun, ano,
  trase_soja_volume_t, trase_soja_volume_export_t, trase_soja_volume_domestico_t,
  trase_soja_fob_usd, trase_soja_n_exporters,
  trase_soja_n_hubs, trase_soja_n_hubs_export, trase_soja_top_exporter,
  trase_boi_volume_t, trase_boi_volume_export_t, trase_boi_volume_domestico_t,
  trase_boi_fob_usd, trase_boi_n_frigorificos,
  trase_boi_n_hubs, trase_boi_n_hubs_export, trase_boi_top_frigorifico

OBSERVACAO ANALITICA CRITICA -- "Trase = so exportacao" NAO vale para a soja
---------------------------------------------------------------------------
Esta era a premissa original deste script, e ela e FALSA para a soja (corrigido
em 2026-07-17). O dataset *composite* da soja cobre o fluxo TOTAL rastreado e
ETIQUETA o que foi esmagado no Brasil, em vez de omiti-lo. Medido em GO 2004-22:

  exporter == 'PROCESSED DOMESTICALLY'  -> 44,6% do volume (74,2 de 166,4 Mt)
    destino BRAZIL em 100% das linhas, FOB = 0 em 100% das linhas.
  exporter in {'UNKNOWN', 'UNKNOWN CUSTOMER'} -> 1,4% do volume
    exportacao REAL (destinos China/Alemanha/..., portos Santos/Paranagua,
    FOB > 0 sempre) -- so o trader e anonimo. CONTA como export.

Por isso o schema separa explicitamente:
  *_volume_t            = fluxo total rastreado   (export + domestico)
  *_volume_export_t     = so exportacao           <- use este como "infra exportadora"
  *_volume_domestico_t  = so esmagamento no Brasil
  *_fob_usd             = so exportacao POR CONSTRUCAO (as linhas domesticas tem FOB=0)
  *_n_exporters         = so tradings IDENTIFICADAS (exclui os 3 rotulos pseudo)
  *_n_hubs_export       = hubs logisticos nas linhas de exportacao

O BOI (v2.2.2) e export-only de verdade: nao tem bucket domestico, e as colunas
*_volume_domestico_t saem 0 -- o que este script VERIFICA e imprime, em vez de
supor. A simetria e proposital: se uma versao futura da Trase passar a incluir
volume domestico no boi, os numeros aparecem em vez de contaminar em silencio.

Consequencia para quem consome: `trase_soja_volume_t` e `trase_boi_volume_t`
NAO sao comparaveis (total vs export). O par comparavel e *_volume_export_t.
Ver Textos/pipelines/27_coleta_trase.md.

Como rodar:
    python coleta_trase.py            # processa zips e salva painel
    python coleta_trase.py --force    # reprocessa mesmo se saida existe
"""
from __future__ import annotations

import argparse
import io
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

ROOT          = Path(__file__).resolve().parent.parent
DIR_RAW       = ROOT / "data" / "raw" / "trase"
DIR_PROCESSED = ROOT / "data" / "processed"
DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

ZIP_BEEF = DIR_RAW / "brazil_beef_v2_2_2.zip"
ZIP_SOY  = DIR_RAW / "brazil_soy_v2_6_1_composite.zip"
CSV_BEEF = "brazil_beef_v2_2_2.csv"
CSV_SOY  = "brazil_soy_v2_6_1_composite.csv"

MAPEAMENTO_CSV = DIR_PROCESSED / "mapeamento_mesorregioes.csv"
SAIDA          = DIR_PROCESSED / "painel_trase.csv"

# Rotulos do campo `exporter` que nao sao uma trading exportadora identificada.
# Verificado no dado bruto (GO): DOMESTICO tem destino BRAZIL e FOB=0 em 100% das
# linhas; os NAO_IDENTIFICADO tem destino estrangeiro, porto real e FOB>0 -- sao
# exportacao de verdade, so o trader e anonimo (logo entram no volume exportado,
# mas nao podem ser contados como um "player").
EXPORTER_DOMESTICO       = "PROCESSED DOMESTICALLY"
EXPORTER_NAO_IDENTIFICADO = {"UNKNOWN", "UNKNOWN CUSTOMER"}


def normaliza_nome(s: str) -> str:
    """CAIXA-ALTA sem acentos, sem espacos duplos. Match Trase x IBGE."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.upper().split())


def carregar_mapeamento() -> pd.DataFrame:
    """cd_mun -> nm_norm para join com Trase."""
    mp = pd.read_csv(MAPEAMENTO_CSV, encoding="utf-8")
    mp["nm_norm"] = mp["nm_mun"].map(normaliza_nome)
    return mp[["cd_mun", "nm_mun", "nm_norm"]]


def _agregar_grupo(g: pd.DataFrame, prefix: str, col_exporter: str) -> pd.Series:
    """Agrega um (cd_mun, ano) em uma linha de metricas.

    Separa exportacao de esmagamento domestico (ver docstring do modulo). O
    `top_exporter` e a maior trading IDENTIFICADA -- se o muni-ano so teve volume
    domestico ou anonimo, sai None (honesto: nao houve exportador identificado),
    e nao 'PROCESSED DOMESTICALLY' como na versao anterior.
    """
    eh_domestico = g[col_exporter] == EXPORTER_DOMESTICO
    g_exp = g[~eh_domestico]                # exportacao (inclui trader anonimo)
    g_dom = g[eh_domestico]                 # esmagamento no Brasil
    # so tradings identificadas contam como "player"
    ident = g_exp[~g_exp[col_exporter].isin(EXPORTER_NAO_IDENTIFICADO)]
    top = ident.groupby(col_exporter)["volume"].sum().sort_values(ascending=False)
    return pd.Series({
        f"{prefix}_volume_t": float(g["volume"].sum()),
        f"{prefix}_volume_export_t": float(g_exp["volume"].sum()),
        f"{prefix}_volume_domestico_t": float(g_dom["volume"].sum()),
        f"{prefix}_fob_usd": float(g["fob"].sum()),
        f"{prefix}_n_exporters": int(ident[col_exporter].nunique()),
        f"{prefix}_n_hubs": int(g["logistics_hub"].nunique()),
        f"{prefix}_n_hubs_export": int(g_exp["logistics_hub"].nunique()),
        f"{prefix}_top_exporter": (top.index[0] if len(top) else None),
    })


def _auditar_cadeia(df: pd.DataFrame, nome: str, col_exporter: str) -> None:
    """Imprime a composicao export x domestico da cadeia -- VERIFICA em vez de supor."""
    tot = df["volume"].sum()
    if tot <= 0:
        return
    dom = df.loc[df[col_exporter] == EXPORTER_DOMESTICO, "volume"].sum()
    anon = df.loc[df[col_exporter].isin(EXPORTER_NAO_IDENTIFICADO), "volume"].sum()
    fob_dom = df.loc[df[col_exporter] == EXPORTER_DOMESTICO, "fob"].sum()
    print(f"  [auditoria {nome}] volume total {tot/1e6:.2f} Mt")
    print(f"    exportado           : {(tot-dom)/1e6:6.2f} Mt ({100*(tot-dom)/tot:5.1f}%)")
    print(f"      dos quais anonimos: {anon/1e6:6.2f} Mt ({100*anon/tot:5.1f}%) -- export real, trader UNKNOWN")
    print(f"    esmagado no Brasil  : {dom/1e6:6.2f} Mt ({100*dom/tot:5.1f}%) -- FOB somado = {fob_dom:.0f}")
    if dom == 0:
        print(f"    -> {nome} e export-only (nenhuma linha '{EXPORTER_DOMESTICO}') [confirmado]")


def processar_soja(mapeamento: pd.DataFrame) -> pd.DataFrame:
    """Le zip soja, filtra GO, agrega por (cd_mun, ano)."""
    print(f"[soja] lendo {ZIP_SOY.name}...")
    with zipfile.ZipFile(ZIP_SOY) as zf:
        with zf.open(CSV_SOY) as f:
            df = pd.read_csv(f, usecols=[
                "year", "state", "municipality_of_production",
                "logistics_hub", "exporter", "volume", "fob",
            ])
    print(f"  total: {len(df):,} linhas")
    df = df[df["state"] == "GOIAS"].copy()
    print(f"  GO:    {len(df):,} linhas")

    df["nm_norm"] = df["municipality_of_production"].map(normaliza_nome)
    df = df.merge(mapeamento[["cd_mun", "nm_norm"]], on="nm_norm", how="left")

    nao_mapeados = df[df["cd_mun"].isna()]["nm_norm"].value_counts()
    if len(nao_mapeados):
        print(f"  munis Trase nao mapeados ({len(nao_mapeados)}):")
        for nm, n in nao_mapeados.head(10).items():
            print(f"    - {nm}: {n} linhas")

    df = df.dropna(subset=["cd_mun"])
    df["cd_mun"] = df["cd_mun"].astype(int)
    df = df.rename(columns={"year": "ano"})

    _auditar_cadeia(df, "soja", "exporter")

    agg = (
        df.groupby(["cd_mun", "ano"], group_keys=False)
        .apply(lambda g: _agregar_grupo(g, "trase_soja", "exporter"), include_groups=False)
        .reset_index()
    )
    print(f"  agregado: {agg.shape[0]:,} (cd_mun, ano), munis distintos: {agg['cd_mun'].nunique()}")
    print(f"  cobertura anos: {agg['ano'].min()}-{agg['ano'].max()}")
    return agg


def processar_boi(mapeamento: pd.DataFrame) -> pd.DataFrame:
    """Le zip beef em chunks (1.86 GB descomprimido), filtra GO, agrega."""
    print(f"[boi] lendo {ZIP_BEEF.name} em chunks...")
    cols = [
        "year", "state_of_production", "municipality_of_production",
        "logistics_hub", "exporter", "volume", "fob",
    ]
    chunks_go = []
    total = 0
    with zipfile.ZipFile(ZIP_BEEF) as zf:
        with zf.open(CSV_BEEF) as f:
            for ck in pd.read_csv(f, chunksize=200_000, usecols=cols):
                total += len(ck)
                go = ck[ck["state_of_production"] == "GOIAS"]
                if len(go):
                    chunks_go.append(go)
    df = pd.concat(chunks_go, ignore_index=True)
    print(f"  total: {total:,} linhas, GO: {len(df):,} linhas")

    df["nm_norm"] = df["municipality_of_production"].map(normaliza_nome)
    df = df.merge(mapeamento[["cd_mun", "nm_norm"]], on="nm_norm", how="left")

    nao_mapeados = df[df["cd_mun"].isna()]["nm_norm"].value_counts()
    if len(nao_mapeados):
        print(f"  munis Trase nao mapeados ({len(nao_mapeados)}):")
        for nm, n in nao_mapeados.head(10).items():
            print(f"    - {nm}: {n} linhas")

    df = df.dropna(subset=["cd_mun"])
    df["cd_mun"] = df["cd_mun"].astype(int)
    df = df.rename(columns={"year": "ano"})

    _auditar_cadeia(df, "boi", "exporter")

    agg = (
        df.groupby(["cd_mun", "ano"], group_keys=False)
        .apply(lambda g: _agregar_grupo(g, "trase_boi", "exporter"), include_groups=False)
        .reset_index()
    )
    agg = agg.rename(columns={
        "trase_boi_n_exporters": "trase_boi_n_frigorificos",
        "trase_boi_top_exporter": "trase_boi_top_frigorifico",
    })
    print(f"  agregado: {agg.shape[0]:,} (cd_mun, ano), munis distintos: {agg['cd_mun'].nunique()}")
    print(f"  cobertura anos: {sorted(agg['ano'].unique())}")
    return agg


def main(force: bool = False) -> Path:
    if SAIDA.exists() and not force:
        print(f"[ok] {SAIDA.name} ja existe (use --force para reprocessar).")
        return SAIDA

    if not ZIP_SOY.exists() or not ZIP_BEEF.exists():
        raise FileNotFoundError(
            f"Zips Trase nao encontrados em {DIR_RAW}.\n"
            f"Baixe manualmente de:\n"
            f"  https://resources.trase.earth/20260511/data/supply-chains/brazil_beef_v2_2_2.zip\n"
            f"  https://resources.trase.earth/20260511/data/supply-chains/brazil_soy_v2_6_1_composite.zip"
        )

    mapeamento = carregar_mapeamento()
    print(f"[map] {len(mapeamento)} municipios IBGE GO carregados")

    soja = processar_soja(mapeamento)
    boi  = processar_boi(mapeamento)

    painel = soja.merge(boi, on=["cd_mun", "ano"], how="outer").sort_values(["cd_mun", "ano"])

    cols_principais = ["cd_mun", "ano"]
    cols_soja = [c for c in painel.columns if c.startswith("trase_soja")]
    cols_boi  = [c for c in painel.columns if c.startswith("trase_boi")]
    painel = painel[cols_principais + cols_soja + cols_boi].reset_index(drop=True)

    # Consistencia: total == export + domestico, cadeia a cadeia (tolerancia de float)
    for p in ("trase_soja", "trase_boi"):
        soma = painel[f"{p}_volume_export_t"].fillna(0) + painel[f"{p}_volume_domestico_t"].fillna(0)
        resid = (painel[f"{p}_volume_t"].fillna(0) - soma).abs().max()
        assert resid < 1e-6, f"{p}: volume_t != export + domestico (residuo max {resid})"
    print("\n[check] volume_t == volume_export_t + volume_domestico_t nas duas cadeias [OK]")

    painel.to_csv(SAIDA, index=False, encoding="utf-8")
    print(f"\n[ok] {SAIDA.name}")
    print(f"  shape: {painel.shape}")
    print(f"  munis: {painel['cd_mun'].nunique()}, anos: {painel['ano'].min()}-{painel['ano'].max()}")
    for p, rot in (("trase_soja", "soja"), ("trase_boi", "boi ")):
        v, e = painel[f"{p}_volume_t"].sum(), painel[f"{p}_volume_export_t"].sum()
        pct = 100 * e / v if v else float("nan")
        print(f"  cobertura {rot}: {painel[f'{p}_volume_t'].notna().sum():,} celulas | "
              f"{v/1e6:6.2f} Mt total, dos quais {pct:.1f}% exportado")
    return SAIDA


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--force", action="store_true", help="Reprocessa mesmo se saida existe")
    args = p.parse_args()
    main(force=args.force)
