"""Converte 40 PNGs pixel-a-pixel GEE (outputs/mapas_gee/) para WebP otimizado.

Saida: Visualizacao/img/mapas_gee/cobertura_YYYY.webp
Reducao tipica: 80-90% (PNGs GEE compostos sao ~2.3 MB; WebP fica ~250-400 KB).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "outputs" / "mapas_gee"
DST = ROOT / "Visualizacao" / "img" / "mapas_gee"

QUALITY = 85
ANO_INICIO = 1985
ANO_FIM = 2024


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    total_in = total_out = 0
    convertidos = 0

    for ano in range(ANO_INICIO, ANO_FIM + 1):
        src = SRC / f"cobertura_{ano}.png"
        dst = DST / f"cobertura_{ano}.webp"
        if not src.exists():
            print(f"AVISO: {src.name} nao encontrado, pulando")
            continue

        size_in = src.stat().st_size
        with Image.open(src) as img:
            img.save(dst, format="WEBP", quality=QUALITY, method=6)
        size_out = dst.stat().st_size

        total_in += size_in
        total_out += size_out
        convertidos += 1
        ratio = (1 - size_out / size_in) * 100
        print(f"  {ano}: {size_in/1024:7.1f} KB -> {size_out/1024:6.1f} KB  ({ratio:5.1f}% menor)")

    if convertidos:
        ratio = (1 - total_out / total_in) * 100
        print(
            f"\n{convertidos} arquivos | {total_in/1024/1024:.2f} MB -> "
            f"{total_out/1024/1024:.2f} MB ({ratio:.1f}% menor)"
        )


if __name__ == "__main__":
    main()
