# Pipeline #2 — Análise Expandida Goiás (cobertura, rebanho, lotação, PIB agro)

**Script**: `scripts/analise_expandida_goias.py`
**Quando foi feito**: Segundo script, expansão do #1.
**Depende de**: Pipeline #1 (lê `pastagem_goias_anual.csv`).
**Outputs**: ver [graficos_descritivos.md](../outputs/graficos_descritivos.md) (PNGs 03–06) e [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## O que faz

1. Reusa o xlsx do MapBiomas (cache).
2. Agrupa as classes do MapBiomas em 5 grupos: Pastagem (15), Agricultura (39, 19, 41, 20, 36), Cerrado/Savana (4, 12), Floresta Nativa (3), Área Urbana (24).
3. Baixa **rebanho bovino** via PPM 3939, variável 105, classification 79 (Tipo de rebanho) → categoria 2670 (Bovino), **nível UF**.
4. Baixa **VA agropecuário** (5938 var 513) e **PIB total** (5938 var 37), **nível UF**, deflaciona via IPCA.
5. Calcula **lotação implícita** = bovinos / área de pastagem.
6. Gera 4 PNGs: cobertura empilhada, rebanho, painel lotação (3 gráficos), PIB agro vs total.

## Como rodar

```bash
python analise_expandida_goias.py
```

(depois de já ter rodado o Pipeline #1, pois ele lê `pastagem_goias_anual.csv`).

## Saída

- 4 PNGs em `outputs/` (`03_*.png` a `06_*.png`)
- 4 CSVs em `data/processed/`

## Limitações

- Mesmo problema do #1: tudo nível UF.
- Lotação implícita = "boi por hectare de pastagem MapBiomas" — mistura precisão de dois sistemas independentes (raster vs. censo PPM). É uma boa aproximação mas não substitui Censo Agro.
