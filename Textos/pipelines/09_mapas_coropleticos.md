# Pipeline #9 — 40 mapas coropléticos municipais

**Script**: `scripts/gerar_mapas_lulc_40anos.py`
**Quando foi feito**: 2026-04-27.
**Depende de**: Pipeline #4.
**Outputs**: 40 PNGs em `outputs/mapas/cobertura_{1985..2024}.png`. Ver [mapas_lulc.md](../outputs/mapas_lulc.md).

## O que faz

Lê `mapbiomas_munis_goias.csv` (Pipeline #4), agrega as 22 classes MapBiomas em **8 grupos temáticos**, calcula a **classe dominante por município/ano** (maior área em ha) e renderiza 40 PNGs coropléticos — um por ano de 1985 a 2024.

## 8 classes agregadas

(mapeamento explícito no topo do script):

| Classe | IDs MapBiomas | Cor |
|---|---|---|
| Floresta | 3 | `#006400` verde escuro |
| Cerrado | 4 | `#32CD32` verde médio |
| Campo natural | 12 | `#90EE90` verde claro |
| Pastagem | 15 | `#FFD700` amarelo |
| Soja | 39 | `#FF69B4` rosa |
| Lavouras+Cana | 20, 40, 41, 46, 47, 48, 62 | `#800080` roxo |
| Área urbana | 24 | `#A0A0A0` cinza |
| Água | 33 | `#4169E1` azul |

Demais IDs do CSV (`0, 9, 11, 21, 25, 29, 30, 31`) são **descartados** antes do cálculo da classe dominante — foco da dissertação é pastagem×soja×água×urbano.

## Layout cada PNG

- Coroplético municipal (246 polígonos), 1 cor por município
- Bordas municipais OFF por padrão (variável `SHOW_BORDERS = False` no topo)
- Título "Cobertura e Uso da Terra — Goiás {ANO}"
- Legenda com 8 entradas (canto inferior direito)
- Barra de escala em km (canto inferior esquerdo)
- DPI 200, ~10×8 polegadas

## Como rodar

```bash
python "scripts/gerar_mapas_lulc_40anos.py"
```

(após Pipeline #4).

**Pré-requisitos**: `pip install pandas geopandas geobr matplotlib matplotlib-scalebar` (ver [referencia/ambiente_python.md](../referencia/ambiente_python.md) sobre gotchas Py 3.14).

## Saída

40 PNGs em `outputs/mapas/cobertura_{ANO}.png` (~250 KB cada, ~10 MB total).

## Limitações

(importante registrar para o texto da dissertação):

- **Resolução visual = 246 polígonos**. Cada município vira UMA cor. Município com 51% pastagem e 49% soja "vira" amarelo total — perde-se toda a heterogeneidade interna.
- **Não é raster**. A representação mata o detalhe que aparece na plataforma MapBiomas (manchas finas de cana, núcleos urbanos, hidrografia, mosaicos).
- **Útil para**: visão geral rápida, slide de apresentação, narrativa "qual classe domina cada município". **Não substitui** o Pipeline #10 (raster 30m via GEE) para figuras finais da dissertação.
