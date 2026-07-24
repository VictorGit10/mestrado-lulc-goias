"""borda_movel_colecao9.py — Pipeline #28E: o teste da borda móvel (Coleção 9 × 10.1)
================================================================================

Executa o teste desenhado no §9 de `Textos/pipelines/28D_deriva_mosaico.md`: separa
o **artefato terminal do classificador** da **integração lavoura-pecuária (ILP) real**
como causa da "deriva do mosaico" (a razão pasto→Mosaico / pasto→agricultura explode
nos anos terminais da série MapBiomas — 0,66 em 2015 a 37,7 em 2024 na 10.1).

A hipótese, tornada falseável (§9.1):
  • FENÔMENO REAL (soja/ILP explodindo) está ancorado no CALENDÁRIO — aparece nos
    mesmos anos em qualquer coleção.
  • ARTEFATO TERMINAL está ancorado na BORDA de cada coleção — cada coleção aplica a
    regra de janela truncada aos SEUS próprios últimos anos. A Coleção 9 termina em
    2023; a 10.1 em 2024. Logo o colapso deve ANDAR com a borda.

As duas hipóteses fazem predições OPOSTAS sobre 2023, que é TERMINAL na 9 e INTERIOR
(tem 2024 de futuro) na 10.1. As grades das duas coleções coincidem pixel-a-pixel
(offset inteiro 3253col×9300lin, resíduo <1e-11 px; ambos exportados no MESMO
crsTransform), então dá para cruzar o MESMO pixel entre coleções.

DOIS TESTES
-----------
Parte A — razão M/A por ano-calendário (agregado). Lê os dois parquets de destinos
  (`processa_cubo_idade_destinos.py` rodado nas duas coleções). Predição-artefato:
  razão(2023 | Col9) >> razão(2023 | Col10.1), porque na 9 o ano 2023 é a borda
  (artefato máximo) e na 10.1 ele já ganhou 2024 de contexto (parcialmente "curado").

Parte B — reclassificação pixel-a-pixel (decisivo, SEM confundir com nível). Para um
  ano-alvo Y, dos pixels que a Col9 chama de Mosaico(21), que fração a Col10.1 chama
  de Agricultura? Chame isso R(Y). Feito para Y=2023 (terminal na 9) e anos-controle
  interiores (2010, 2015) em AMBAS. §9.2: comparar NÍVEIS entre coleções confunde
  "ganhou futuro" com "algoritmo melhor"; a razão R(2023)/R(controle) remove o offset
  médio de qualidade. Predição-artefato: R(2023) >> R(controle). Predição-real:
  R(2023) ≈ R(controle) (o Mosaico de 2023 é estável entre coleções).
  Subproduto: o CENTROIDE dos pixels rerroteados (Mosaico na 9 → Agric na 10.1) é a
  "agricultura escondida" — crava a direção do viés no centro de massa (#32/#44).

SAÍDA
    data/processed/borda_movel_razao_ano.csv       (Parte A)
    data/processed/borda_movel_reclassificacao.csv (Parte B: cross-tab + R(Y) + centroide)

COMO RODAR (depois de baixar e reprocessar a Coleção 9)
    python scripts/borda_movel_colecao9.py \
        --shards9 data/raw/cubo_go_col9 --shards10 data/raw/cubo_go \
        --parquet9 data/processed/pastagem_conversao_destinos_col9.parquet \
        --parquet10 data/processed/pastagem_conversao_destinos.parquet

Quando: 2026-07-23. Companheiro do #28D. Fecha o §9 (artefato × ILP real).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window

sys.path.insert(0, str(Path(__file__).resolve().parent))
import processa_cubo_idade as pc  # noqa: E402 — reusa grade/IDs/municípios do #28

ROOT = Path(__file__).resolve().parent.parent
CSV_RAZAO = ROOT / "data" / "processed" / "borda_movel_razao_ano.csv"
CSV_RECLASS = ROOT / "data" / "processed" / "borda_movel_reclassificacao.csv"

ID_MOSAICO = 21
# Categorias compactas para o cross-tab entre coleções
CAT_OUTROS, CAT_PASTO, CAT_AGRI, CAT_MOSAICO = 0, 1, 2, 3
CAT_NOMES = ["outros", "pastagem", "agricultura", "mosaico"]


def lut_categoria() -> np.ndarray:
    """LUT 0..255 → categoria compacta {outros, pastagem, agricultura, mosaico}."""
    lut = np.zeros(256, dtype=np.uint8)
    lut[pc.ID_PASTAGEM] = CAT_PASTO
    for cid in pc.IDS_AGRICULTURA:
        lut[cid] = CAT_AGRI
    lut[ID_MOSAICO] = CAT_MOSAICO
    return lut


# ============================ Parte A: razão por ano ============================

def razao_por_ano(parquet: Path) -> pd.DataFrame:
    df = pd.read_parquet(parquet)
    piv = df.groupby(["ano_conversao", "destino"])["n_pixels"].sum().unstack(fill_value=0)
    for c in ("agricultura", "mosaico"):
        if c not in piv.columns:
            piv[c] = 0
    piv["razao_M_A"] = piv["mosaico"] / piv["agricultura"].replace(0, np.nan)
    return piv[["agricultura", "mosaico", "razao_M_A"]]


def parte_A(parquet9: Path, parquet10: Path) -> pd.DataFrame:
    r9 = razao_por_ano(parquet9).add_suffix("_c9")
    r10 = razao_por_ano(parquet10).add_suffix("_c10")
    out = r10.join(r9, how="outer")  # 10.1 vai a 2024; a 9 a 2023
    out["razao_c9_sobre_c10"] = out["razao_M_A_c9"] / out["razao_M_A_c10"]
    out = out.reset_index().rename(columns={"ano_conversao": "ano"})
    return out


# ==================== Parte B: reclassificação pixel-a-pixel ====================

def _indexar_shards(pasta: Path) -> dict:
    """Mapeia (transform.c, transform.f) → caminho, p/ casar tiles entre coleções."""
    idx = {}
    for t in sorted(pasta.glob("*.tif")):
        with rasterio.open(t) as s:
            chave = (round(s.transform.c, 9), round(s.transform.f, 9), s.width, s.height)
        idx[chave] = t
    return idx


def _processar_tile(t9: Path, t10: Path, gdf_muni, lut, anos, janela,
                    cont, slat, past_antes) -> None:
    """Acumula o cross-tab 4×4 (cat_c9 × cat_c10) de UM tile casado, por ano.
    cont/slat têm shape (len(anos),4,4); past_antes shape (len(anos),)."""
    with rasterio.open(t9) as s9, rasterio.open(t10) as s10:
        if s9.transform != s10.transform or (s9.width, s9.height) != (s10.width, s10.height):
            raise RuntimeError(f"tiles desalinhados: {t9.name} × {t10.name}")
        muni = rasterize(
            ((g, i) for g, i in zip(gdf_muni.geometry, gdf_muni.muni_idx)),
            out_shape=(s9.height, s9.width), transform=s9.transform,
            fill=0, dtype=np.uint16)
        if not muni.any():
            return
        lats_lin = s9.transform.f - (np.arange(s9.height) + 0.5) * pc.PX
        for top in range(0, s9.height, janela):
            for left in range(0, s9.width, janela):
                h = min(janela, s9.height - top)
                w = min(janela, s9.width - left)
                mj = muni[top:top + h, left:left + w] > 0
                if not mj.any():
                    continue
                win = Window(left, top, w, h)
                lat2d = np.broadcast_to(lats_lin[top:top + h, None], (h, w))
                latm = lat2d[mj]
                for ia, a in enumerate(anos):
                    banda = a - pc.ANO_MIN + 1  # 1-based; 1985 é a banda 1 nas duas
                    c9 = lut[s9.read(banda, window=win)][mj]
                    c10 = lut[s10.read(banda, window=win)][mj]
                    chave = c9.astype(np.int64) * 4 + c10.astype(np.int64)
                    cont[ia] += np.bincount(chave, minlength=16).reshape(4, 4)
                    slat[ia] += np.bincount(chave, weights=latm, minlength=16).reshape(4, 4)
                    if a - 1 >= pc.ANO_MIN:
                        rer = (c9 == CAT_MOSAICO) & (c10 == CAT_AGRI)
                        if rer.any():
                            prev10 = lut[s10.read(banda - 1, window=win)][mj][rer]
                            past_antes[ia] += int((prev10 == CAT_PASTO).sum())


def parte_B(shards9: Path, shards10: Path, anos: list[int], janela: int,
            ckpt: Path, max_shards: int) -> tuple:
    """Roda com checkpoint por tile (o ambiente mata tarefas de CPU longa). Retorna
    (cont, slat, past, anos, completo, ndone, ntot)."""
    anos = sorted(anos)
    lut = lut_categoria()
    idx9, idx10 = _indexar_shards(shards9), _indexar_shards(shards10)
    chaves = sorted(set(idx9) & set(idx10))
    if not chaves:
        sys.exit("Nenhum shard casa entre as duas coleções (grades diferentes?).")

    if ckpt.exists():
        z = np.load(ckpt, allow_pickle=True)
        cont = z["cont"].astype(np.int64); slat = z["slat"].astype(np.float64)
        past = z["past"].astype(np.int64); done = set(z["done"].tolist())
        anos_ck = z["anos"].tolist(); z.close()
        if anos_ck != anos:
            sys.exit(f"checkpoint {ckpt.name} é de outros anos {anos_ck}; apague-o.")
        print(f"  checkpoint: {len(done)}/{len(chaves)} tiles já feitos")
    else:
        cont = np.zeros((len(anos), 4, 4), dtype=np.int64)
        slat = np.zeros((len(anos), 4, 4), dtype=np.float64)
        past = np.zeros(len(anos), dtype=np.int64); done = set()

    gdf_muni = pc.carregar_municipios()
    print(f"  {len(chaves)} tiles casados (9∩10.1) de {len(idx9)}/{len(idx10)}")

    pend = [k for k in chaves if idx9[k].name not in done]
    if max_shards:
        pend = pend[:max_shards]
    for k in pend:
        t0 = time.time()
        _processar_tile(idx9[k], idx10[k], gdf_muni, lut, anos, janela, cont, slat, past)
        done.add(idx9[k].name)
        np.savez(ckpt, cont=cont, slat=slat, past=past,
                 done=np.array(sorted(done)), anos=np.array(anos))
        print(f"  [{len(done):02d}/{len(chaves)}] {idx9[k].name} ({time.time()-t0:.0f}s) [ckpt]",
              flush=True)

    return cont, slat, past, anos, len(done) >= len(chaves), len(done), len(chaves)


def finalizar_B(cont, slat, past, anos) -> pd.DataFrame:
    linhas = []
    for ia, a in enumerate(anos):
        C = cont[ia]
        n_mos9 = C[CAT_MOSAICO].sum()             # pixels Mosaico na Col9 (ano a)
        n_mos9_agri10 = C[CAT_MOSAICO, CAT_AGRI]  # → Agricultura na Col10.1 (os rerroteados)
        n_mos9_mos10 = C[CAT_MOSAICO, CAT_MOSAICO]
        n_mos9_past10 = C[CAT_MOSAICO, CAT_PASTO]
        R = n_mos9_agri10 / n_mos9 if n_mos9 else np.nan  # a taxa de "cura" R(Y)
        # centroide (lat média) dos rerroteados = agricultura escondida
        lat_rer = slat[ia][CAT_MOSAICO, CAT_AGRI] / n_mos9_agri10 if n_mos9_agri10 else np.nan
        # baseline: lat média de todo pixel Mosaico da Col9 nesse ano
        lat_mos9 = slat[ia][CAT_MOSAICO].sum() / n_mos9 if n_mos9 else np.nan
        # direção reversa (deve ser pequena se o artefato é unidirecional)
        n_agri9 = C[CAT_AGRI].sum()
        R_rev = C[CAT_AGRI, CAT_MOSAICO] / n_agri9 if n_agri9 else np.nan
        linhas.append({
            "ano": a,
            "mosaico_c9": int(n_mos9),
            "mos9_para_agri10": int(n_mos9_agri10),
            "mos9_para_mos10": int(n_mos9_mos10),
            "mos9_para_past10": int(n_mos9_past10),
            "R_cura_mos9_agri10": R,
            "R_reversa_agri9_mos10": R_rev,
            "frac_rerroteado_era_pasto_ant": (past[ia] / n_mos9_agri10
                                              if n_mos9_agri10 else np.nan),
            "lat_rerroteado": lat_rer,
            "lat_mosaico_c9": lat_mos9,
            "dlat_rer_menos_mos9": lat_rer - lat_mos9 if n_mos9_agri10 else np.nan,
        })
    return pd.DataFrame(linhas)


def main() -> None:
    p = argparse.ArgumentParser(description="Teste da borda móvel (Coleção 9 × 10.1) — §9 do #28D")
    p.add_argument("--shards9", type=Path, default=ROOT / "data/raw/cubo_go_col9")
    p.add_argument("--shards10", type=Path, default=ROOT / "data/raw/cubo_go")
    p.add_argument("--parquet9", type=Path,
                   default=ROOT / "data/processed/pastagem_conversao_destinos_col9.parquet")
    p.add_argument("--parquet10", type=Path,
                   default=ROOT / "data/processed/pastagem_conversao_destinos.parquet")
    p.add_argument("--anos", type=int, nargs="+", default=[2010, 2015, 2019, 2021, 2022, 2023],
                   help="anos-alvo do teste pixel-a-pixel (interiores = controle; 2023 = terminal na 9)")
    p.add_argument("--janela", type=int, default=2048)
    p.add_argument("--max-shards", type=int, default=0,
                   help="máx. tiles por invocação (0=todos); use ~3 p/ caber no orçamento de CPU")
    p.add_argument("--so-A", action="store_true", help="só a Parte A (razão; não precisa dos shards)")
    args = p.parse_args()
    ckpt = CSV_RECLASS.with_suffix(".ckptB.npz")

    print("=" * 74)
    print("PARTE A — razão pasto→Mosaico / pasto→agricultura por ano (9 × 10.1)")
    print("=" * 74)
    if args.parquet9.exists() and args.parquet10.exists():
        A = parte_A(args.parquet9, args.parquet10)
        A.to_csv(CSV_RAZAO, index=False)
        with pd.option_context("display.width", 120, "display.max_columns", 12):
            cols = ["ano", "razao_M_A_c9", "razao_M_A_c10", "razao_c9_sobre_c10"]
            print(A[cols].round(2).to_string(index=False))
        print(f"\n  -> {CSV_RAZAO}")
        print("  Leitura: se razao_c9_sobre_c10 dispara em 2022-2023 (a borda da 9), o")
        print("           colapso ANDA com a borda = artefato terminal.")
    else:
        print(f"  (pulada — falta {args.parquet9.name} ou {args.parquet10.name})")

    if args.so_A:
        return

    print("\n" + "=" * 74)
    print("PARTE B — reclassificação pixel-a-pixel: dos Mosaico da Col9, quantos a")
    print("          Col10.1 vira Agricultura? R(2023 terminal) >> R(controle) = artefato")
    print("=" * 74)
    t0 = time.time()
    cont, slat, past, anos, completo, ndone, ntot = parte_B(
        args.shards9, args.shards10, sorted(args.anos), args.janela, ckpt, args.max_shards)
    if not completo:
        print(f"\nPARCIAL: {ndone}/{ntot} tiles ({time.time()-t0:.0f}s). Reinvoque para continuar.")
        return
    B = finalizar_B(cont, slat, past, anos)
    B.to_csv(CSV_RECLASS, index=False)
    ckpt.unlink(missing_ok=True)
    with pd.option_context("display.width", 140, "display.max_columns", 14):
        mostra = ["ano", "mosaico_c9", "mos9_para_agri10", "R_cura_mos9_agri10",
                  "R_reversa_agri9_mos10", "frac_rerroteado_era_pasto_ant",
                  "lat_rerroteado", "dlat_rer_menos_mos9"]
        print(B[mostra].round(4).to_string(index=False))
    print(f"\n  -> {CSV_RECLASS}  ({time.time() - t0:.0f}s)")
    print("  Leitura: R_cura é a fração de Mosaico(Col9) que vira Agricultura(Col10.1).")
    print("           R(2023)/R(controle) remove o offset de qualidade entre coleções.")
    print("           dlat_rer>0 = agricultura escondida está ao NORTE (viés do #32/#44).")


if __name__ == "__main__":
    main()
