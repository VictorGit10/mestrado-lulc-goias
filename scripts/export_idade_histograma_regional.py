"""export_idade_histograma_regional.py — export de viz (família #28/#28C)
========================================================================

O QUE FAZ
---------
Pré-computa os histogramas da idade da pastagem na conversão (não-censurada)
POR REGIÃO, para alimentar a peça interativa "re-cablada" da Perna 2 do site
(PROPOSTA_REFORMULACAO §4, Opção A): selecionar uma região redesenha o
histograma, que continua bimodal. O redesenho lê um bin-array pré-computado —
não reamostra os pixels ao vivo.

Não é um pipeline analítico novo (não gera achado): é tooling de export para o
#28/#28C. Por isso NÃO recebe número próprio e reusa as funções do #28
(`carregar`, `ajustar_gmm_unidim`) e o critério de bimodalidade do #28C.

DECISÃO DE GRANULARIDADE — Opção A, e por que ela CADUCOU
----------------------------------------------------------
A escolha original (jul/2026) foi operar nas **5 mesorregiões**, não nas AMCs,
porque a amostra do #28A era rala: só 36 de 158 AMCs tinham n≥100 pixels
não-censurados (mediana 22/AMC), então "selecionar qualquer AMC" mostraria
histograma ralo em 3 de 4 cliques.

**Com o censo (21/jul/2026) essa restrição desapareceu: 164 de 164 AMCs têm
n≥100.** A Opção B (seleção por AMC) passou a ser viável, e a granularidade fina
é justamente o que o #28C precisa para a geografia da bimodalidade. A decisão de
qual malha o site expõe agora é editorial, não técnica — ambos os blocos são
exportados. Deixado como está até haver decisão explícita sobre a peça.

CENSURA
-------
O histograma é sobre pixels NÃO-CENSURADOS (a idade só é válida quando a fase
pastagem não está truncada em 1985). `n_censurado` vem reportado à parte por
célula, para o site poder ser honesto sobre a cobertura.

ENTRADAS
    data/processed/pastagem_idade_censo.parquet      (#28 censo, via carregar("censo"))
    data/processed/amc_crosswalk_goias.csv           (#25, p/ o bloco AMC)

SAÍDA
    Visualizacao/assets/data/idade_pastagem_regional.json

COMO RODAR
    python scripts/export_idade_histograma_regional.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_periodos import ATOS_FLAT as ATOS                        # noqa: E402
from analise_reserva_terra import carregar, ajustar_gmm_unidim       # noqa: E402
from estatistica_ponderada import mediana as mediana_p               # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CW_AMC = ROOT / "data" / "processed" / "amc_crosswalk_goias.csv"
DIR_VIZ = ROOT / "Visualizacao" / "assets" / "data"
SAIDA = DIR_VIZ / "idade_pastagem_regional.json"

# Bins do histograma: 0,2,…,40 anos — mesma convenção do site e do #28C.
BINS = np.arange(0, 41, 2)

# Critério de bimodalidade do #28C (todos precisam valer).
BIC_MIN = 10.0     # ΔBIC = bic_1c - bic_2c
SEP_MIN = 5.0      # separação mínima entre modos (anos)
PESO_MIN = 0.15    # peso mínimo do componente menor
N_GMM_MIN = 100    # abaixo disso o GMM é frágil: emite histograma, marca confiavel=False


def _bloco_celula(idade_nc: np.ndarray, n_censurado: float,
                  peso_nc: np.ndarray | None = None) -> dict:
    """Histograma + (se n≥N_GMM_MIN) ajuste GMM e veredito de bimodalidade para
    uma célula (região × recorte de ato). `idade_nc` = idades NÃO-censuradas.

    `peso_nc` é obrigatório na prática desde que o #28 virou censo: a fonte é uma
    tabela de contingência, então cada linha é uma CÉLULA com `n_pixels`, não uma
    observação. Contar linhas daria n=405.771 em vez de 44,6 milhões, e mediana
    sobre linhas não ponderadas seria simplesmente outra estatística.
    """
    w = np.ones_like(idade_nc, dtype=float) if peso_nc is None else np.asarray(peso_nc, float)
    counts, _ = np.histogram(idade_nc, bins=BINS, weights=w)
    n = int(round(w.sum()))
    celula = {
        "n": n,
        "n_censurado": int(round(n_censurado)),
        "mediana": mediana_p(idade_nc, w) if n else None,
        "counts": [int(round(c)) for c in counts],
        "confiavel": bool(n >= N_GMM_MIN),
        "gmm": None,
        "bimodal": None,
    }
    if n >= N_GMM_MIN:
        g = ajustar_gmm_unidim(idade_nc.astype(float), w)
        delta_bic = g["bic_1c"] - g["bic_2c"]
        sep = abs(g["mu2"] - g["mu1"])
        peso_menor = min(g["w1"], g["w2"])
        celula["gmm"] = {
            "mu_jovem": round(g["mu1"], 1), "w_jovem": round(g["w1"], 3),
            "mu_velho": round(g["mu2"], 1), "w_velho": round(g["w2"], 3),
            "separacao_anos": round(sep, 1), "delta_bic": round(delta_bic, 1),
        }
        celula["bimodal"] = bool(
            (delta_bic > BIC_MIN) and (sep > SEP_MIN) and (peso_menor > PESO_MIN)
        )
    return celula


def _bloco_regiao(sub: pd.DataFrame) -> dict:
    """Para uma região: célula 'todos' + uma por ato (I/II/III). O toggle de ato
    do site lê estas chaves; 'todos' é a vista padrão."""
    recortes = {"todos": sub}
    for ato_id in ATOS:
        recortes[ato_id] = sub[sub["ato"] == ato_id]
    out = {}
    for chave, s in recortes.items():
        nc = s[~s["censurado"]]
        n_cens = s.loc[s["censurado"], "peso"].sum()
        out[chave] = _bloco_celula(nc["idade_pastagem_anos"].to_numpy(float),
                                   n_cens, nc["peso"].to_numpy(float))
    return out


def _malha_block(df: pd.DataFrame, col: str, incluir_estado: bool) -> dict:
    """Monta {ordem, regioes} para uma coluna de recorte (mesorregião ou AMC).
    `ordem` = regiões ordenadas pela mediana da idade não-censurada (jovem→velho),
    que é a ordem natural Sul→Norte da narrativa da Perna 2."""
    regioes: dict[str, dict] = {}

    if incluir_estado:
        regioes["Goiás (estado)"] = _bloco_regiao(df)

    chaves = [c for c in df[col].dropna().unique() if str(c) != "" and str(c) != "0"]
    # Ordena pela mediana não-censurada PONDERADA (jovem→velho).
    nc_all = df[~df["censurado"]]
    medianas = {c: mediana_p(g["idade_pastagem_anos"].to_numpy(float),
                             g["peso"].to_numpy(float))
                for c, g in nc_all.groupby(col, observed=True)}
    chaves = sorted(chaves, key=lambda c: medianas.get(c, np.inf))

    ordem = (["Goiás (estado)"] if incluir_estado else [])
    for c in chaves:
        nome = str(int(c)) if col == "code_amc" else str(c)
        rotulo = f"AMC {nome}" if col == "code_amc" else nome
        regioes[rotulo] = _bloco_regiao(df[df[col] == c])
        ordem.append(rotulo)

    return {"ordem": ordem, "regioes": regioes}


def main() -> None:
    print("Carregando o censo do #28 (pastagem_idade_censo.parquet)...")
    df = carregar("censo")
    df = df[df["ato"].notna()].copy()
    n_nc = df.loc[~df["censurado"], "peso"].sum()
    print(f"  {df['peso'].sum():,.0f} eventos em {len(df):,} células | "
          f"{n_nc:,.0f} não-censurados")

    # --- Bloco mesorregião (o que o site consome na Opção A) ----------------
    df_meso = df[df["mesorregiao"].notna() & (df["mesorregiao"] != "")]
    meso_block = _malha_block(df_meso, "mesorregiao", incluir_estado=True)
    print(f"  mesorregião: {len(meso_block['regioes'])} regiões (+estado)")

    # --- Bloco AMC (registro / eventual Opção B; confiavel por N) ------------
    amc_block = None
    if CW_AMC.exists():
        cw = pd.read_csv(CW_AMC, dtype={"cd_mun": "int64", "code_amc": "int64"})
        df_amc = df.merge(cw[["cd_mun", "code_amc"]], on="cd_mun", how="left")
        df_amc = df_amc[df_amc["code_amc"].notna()].copy()
        df_amc["code_amc"] = df_amc["code_amc"].astype(int)
        amc_block = _malha_block(df_amc, "code_amc", incluir_estado=False)
        n_conf = sum(1 for r in amc_block["regioes"].values()
                     if r["todos"]["confiavel"])
        print(f"  AMC: {len(amc_block['regioes'])} regiões | "
              f"{n_conf} com n≥{N_GMM_MIN} (confiáveis)")
    else:
        print(f"  [aviso] {CW_AMC.name} ausente — bloco AMC não gerado")

    saida = {
        "meta": {
            "fonte": "pastagem_idade_censo.parquet (#28 censo) + config_periodos + amc_crosswalk (#25)",
            "gerado_por": "scripts/export_idade_histograma_regional.py",
            "malha_interativa": "mesorregiao (Opção A)",
            "bins": BINS.astype(int).tolist(),
            "nota_censura": "histograma sobre pixels NÃO-censurados; n_censurado por célula à parte",
            "criterio_bimodal": f"ΔBIC>{BIC_MIN:.0f} & separação>{SEP_MIN:.0f}a & peso_menor>{PESO_MIN} (n≥{N_GMM_MIN})",
            "atos": {k: {"periodo": [v[0], v[1]], "nome": v[2]} for k, v in ATOS.items()},
        },
        "mesorregiao": meso_block,
        "amc": amc_block,
    }

    DIR_VIZ.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] {SAIDA.relative_to(ROOT)}")

    # Resumo legível: mesorregiões, ordem Sul→Norte e veredito bimodal em 'todos'.
    print("\nMesorregiões (ordem jovem→velho, célula 'todos'):")
    for rot in meso_block["ordem"]:
        c = meso_block["regioes"][rot]["todos"]
        bm = "bimodal" if c["bimodal"] else ("unimodal" if c["bimodal"] is not None else "n<min")
        med = f"{c['mediana']:.0f}a" if c["mediana"] is not None else "—"
        print(f"  {rot:<18} n={c['n']:>5}  mediana={med:>4}  {bm}")


if __name__ == "__main__":
    main()
