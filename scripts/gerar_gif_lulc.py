"""gerar_gif_lulc.py — GIF animado dos 40 mapas LULC (1985–2024).

Consome os PNGs compostos em outputs/mapas_gee/ gerados por
gerar_mapas_lulc_gee_40anos.py.

Pré-requisitos:
    pip install imageio

Uso:
    python "Scripts e Catalogo/gerar_gif_lulc.py"
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import imageio.v2 as imageio

ROOT = Path(__file__).resolve().parent.parent
MAP_DIR = ROOT / "outputs" / "mapas_gee"
ANO_MIN, ANO_MAX = 1985, 2024
DURATION_MS = 500  # tempo por frame (~2 fps)


def main() -> None:
    frames = []
    for ano in range(ANO_MIN, ANO_MAX + 1):
        path = MAP_DIR / f"cobertura_{ano}.png"
        if not path.exists():
            sys.exit(f"Mapa não encontrado: {path}")
        frames.append(imageio.imread(path))
        print(f"  {ano}")

    gif_path = MAP_DIR / f"cobertura_{ANO_MIN}_{ANO_MAX}.gif"
    imageio.mimwrite(gif_path, frames, duration=DURATION_MS, loop=0)
    print(f"GIF salvo: {gif_path} ({gif_path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()