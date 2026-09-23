"""Figura da idade da pastagem para a APRESENTAÇÃO (TV), a partir da da qualificação.

Mesma regra de gerar_figura_idade_web.py: a figura mantida é a da qualificação
(`fig_idade_pastagem()` em qualificacao/fig/gerar_figuras.py) e aqui só muda o
suporte. Nenhum número é recalculado. Diferenças para a versão do site:

- só o painel (a), a distribuição com as duas populações (é o que o slide mostra);
- todo texto desenhado é ampliado (TEXTO_X), porque no palco de 1080 px exibido
  numa TV de 80" o rótulo de 8 pt da figura impressa fica com ~13 px: ilegível
  a 4 m.

COMO RODAR
    python Visualizacao/scripts/gerar_figura_idade_apresentacao.py

SAÍDA
    Visualizacao/img/graficos/idade_pastagem_duas_populacoes.apresentacao.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[2]
DIR_QUAL = ROOT / "qualificacao" / "fig"
DESTINO = ROOT / "Visualizacao" / "img" / "graficos" / "idade_pastagem_duas_populacoes.apresentacao.png"
TEXTO_X = 2.2
FIGSIZE_PAR = (19.0, 5.6)   # a função pede 1×2; cada painel fica largo e baixo, como o espaço do slide
DPI = 160


def main() -> None:
    sys.path.insert(0, str(DIR_QUAL))
    import estilo
    import gerar_figuras

    def salvar_no_palco(fig, nome: str, raster: bool = False) -> Path:
        painel_b = fig.axes[1]
        painel_b.remove()
        for t in fig.findobj(Text):
            t.set_fontsize(t.get_fontsize() * TEXTO_X)
        for ax in fig.axes:
            ax.tick_params(width=1.2, length=5)
        fig.savefig(DESTINO, dpi=DPI, facecolor="white", bbox_inches="tight", pad_inches=0.12)
        plt.close(fig)
        return DESTINO

    subplots_original = gerar_figuras.plt.subplots

    def subplots_largo(*args, **kwargs):
        if args[:2] == (1, 2):
            kwargs["figsize"] = FIGSIZE_PAR
        return subplots_original(*args, **kwargs)

    original = gerar_figuras.salvar
    gerar_figuras.salvar = salvar_no_palco
    gerar_figuras.plt.subplots = subplots_largo
    try:
        estilo.configurar()
        gerar_figuras.fig_idade_pastagem()
    finally:
        gerar_figuras.salvar = original
        gerar_figuras.plt.subplots = subplots_original
    print(f"[OK] {DESTINO.relative_to(ROOT)}  ({DESTINO.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
