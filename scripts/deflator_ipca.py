"""deflator_ipca.py — deflator IPCA compartilhado (Goiás)

Reúne o par `carregar_ipca()` / `deflacionar()` que vivia copiado em três
pipelines de Goiás (#8 `construir_painel_unificado`, #16 `analise_expandida_goias`,
`analise_credito_uso_terra`). As três cópias eram idênticas a menos de quebra de
linha e crase no docstring — a extração é no-op numérico, e `__main__` abaixo
confere isso contra a implementação pré-refactor.

O método está descrito em `Textos/metodologia/deflacao_ipca.md`: índice IPCA
acumulado (SIDRA 1737), dezembro de cada ano como representante do ano, base
`DATA_BASE_DEFLATOR`.

## Armadilha do índice (a razão de este docstring existir)

`deflacionar()` faz um `merge` interno e devolve uma Series com índice 0..N-1,
**não** o índice do DataFrame que você passou. Se `df_nominal` vier de um filtro
sem `reset_index(drop=True)`, seus índices são esparsos (ex.: [11, 12, ...]) e a
atribuição `df["x_real"] = deflacionar(df, "x", ipca)` embaralha valores entre
municípios pelo alinhamento por índice do pandas — silenciosamente. **Sempre
resete o índice antes de chamar.**

## Ano sem dezembro sai NaN, sem avisar

O merge é `how="left"` pelo ano, então um ano nominal que não tenha dezembro na
série IPCA recebe `idx_dez = NaN` e o valor deflacionado sai `NaN` — sem erro,
sem warning. Hoje a série vai até **março/2026**, logo 2026 é o único ano nessa
condição; nenhum pipeline atual é afetado (todos terminam em 2023/2024). Se um
dia a janela chegar ao ano corrente, isso vira bug silencioso.

## O que deliberadamente NÃO está aqui

- **Conversão de unidade.** `construir_painel_unificado` multiplica por 1000
  depois de deflacionar (PIB do SIDRA vem em R$ mil) e `analise_expandida_goias`
  multiplica antes, na carga. A ordem é indiferente porque `deflacionar()` é
  linear, mas o fator é do chamador — ver `auditoria_pib.py`.
- **`deflacionar_pib()`** (`grafico_pastagem_pib_goias.py`) — mesma matemática,
  contrato diferente: devolve DataFrame, hardcoda `pib_nominal_rs`, imprime.
- **`fator_ipca()`** (`coleta_pib_uf_ipea.py`) — outro trabalho: fator escalar
  dez/2010 → dez/2024 para séries que o IPEA já entrega deflacionadas.
- **`baixar_ipca()`** (`analise_expandida_goias.py`) — baixa do SIDRA em vez de
  ler o cache. Aqui só se lê o CSV já materializado.

Autoteste (convenção do `estatistica_ponderada.py`):

    python scripts/deflator_ipca.py
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = ROOT / "data" / "processed"
ARQ_IPCA = DIR_PROCESSED / "sidra_1737_ipca.csv"

# Base de deflação: R$ de dezembro/2024 (fim da série LULC).
DATA_BASE_DEFLATOR = (2024, 12)


def carregar_ipca(verbose: bool = False) -> pd.DataFrame:
    """Série IPCA acumulada (SIDRA 1737) do cache, sem os meses faltantes."""
    df = pd.read_csv(ARQ_IPCA, encoding="utf-8")
    df = df.dropna(subset=["indice_acum"])
    if verbose:
        print(f"[ipca] {len(df)} registros, {df['ano'].min()}-{df['ano'].max()}")
    return df


def deflacionar(df_nominal: pd.DataFrame, col_val: str, df_ipca: pd.DataFrame) -> pd.Series:
    """Deflaciona col_val para R$ de DATA_BASE_DEFLATOR usando dez de cada ano.

    Devolve Series com índice 0..N-1 — resete o índice de `df_nominal` antes de
    atribuir o resultado de volta (ver "Armadilha do índice" no topo do módulo).
    """
    ano_base, mes_base = DATA_BASE_DEFLATOR
    idx_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base),
        "indice_acum",
    ].iloc[0]
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "idx_dez"}
    )
    merged = df_nominal.merge(df_dez, on="ano", how="left")
    return merged[col_val] * (idx_base / merged["idx_dez"])


# ---------------------------------------------------------------------------
# Autoteste: a extração preserva o resultado bit a bit?
# ---------------------------------------------------------------------------

def _deflacionar_pre_refactor(df_nominal, col_val, df_ipca):
    """Cópia literal do corpo que estava nos três scripts, para comparação."""
    ano_base, mes_base = (2024, 12)
    idx_base = df_ipca.loc[
        (df_ipca["ano"] == ano_base) & (df_ipca["mes"] == mes_base), "indice_acum"
    ].iloc[0]
    df_dez = df_ipca[df_ipca["mes"] == 12][["ano", "indice_acum"]].rename(
        columns={"indice_acum": "idx_dez"}
    )
    merged = df_nominal.merge(df_dez, on="ano", how="left")
    return merged[col_val] * (idx_base / merged["idx_dez"])


def testa_equivalencia() -> None:
    """Confere módulo == cópias antigas sobre a série IPCA real."""
    import numpy as np

    ipca = carregar_ipca(verbose=True)

    anos = ipca["ano"].drop_duplicates().sort_values()
    rng = np.random.default_rng(42)
    nominal = pd.DataFrame({
        "ano": anos.values,
        "valor": rng.uniform(1e3, 1e9, size=len(anos)),
    })

    novo = deflacionar(nominal, "valor", ipca)
    velho = _deflacionar_pre_refactor(nominal, "valor", ipca)

    pd.testing.assert_series_equal(novo, velho, check_names=False)
    print(f"[ok] equivalência com a implementação pré-refactor ({len(nominal)} anos)")

    # A base deflaciona para si mesma: o ano-base sai com fator 1.
    ano_base, _ = DATA_BASE_DEFLATOR
    if ano_base in set(nominal["ano"]):
        i = nominal.index[nominal["ano"] == ano_base][0]
        assert np.isclose(novo.iloc[i], nominal["valor"].iloc[i]), "fator do ano-base ≠ 1"
        print(f"[ok] fator do ano-base ({ano_base}) = 1")

    # Linearidade: é o que autoriza o ×1000 do chamador ficar de qualquer lado.
    # equal_nan porque ano sem dezembro sai NaN nos dois lados (ver abaixo).
    dobro = nominal.assign(valor=nominal["valor"] * 1000.0)
    assert np.allclose(deflacionar(dobro, "valor", ipca), novo * 1000.0,
                       equal_nan=True), "não-linear"
    print("[ok] linearidade (×1000 pode vir antes ou depois)")

    # Contrato do NaN: ano sem dezembro na série IPCA não é erro, é NaN.
    com_dez = set(ipca.loc[ipca["mes"] == 12, "ano"])
    sem_dez = sorted(set(nominal["ano"]) - com_dez)
    nan_saida = sorted(nominal.loc[novo.isna(), "ano"])
    assert sem_dez == nan_saida, f"NaN inesperado: {sem_dez} vs {nan_saida}"
    if sem_dez:
        print(f"[ok] anos sem dezembro saem NaN, como documentado: {sem_dez}")
    else:
        print("[ok] todos os anos têm dezembro na série")


if __name__ == "__main__":
    testa_equivalencia()
