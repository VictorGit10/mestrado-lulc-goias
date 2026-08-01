# Gráficos da dissertação / visualização

Esta pasta guarda figuras de síntese geradas para o site e para a dissertação.
Cada entrada indica o script gerador, os números de destaque e os cuidados de interpretação.

---

## `produtividade_extensao_intensificacao.png`

**Tema:** decomposição do crescimento da soja e da pecuária em **extensão de área** vs. **intensificação** (produtividade / lotação).

**Script:** [`Visualizacao/scripts/gerar_figura_produtividade.py`](../../scripts/gerar_figura_produtividade.py)

### Painéis

- **A) Soja — scatter conectado:** área plantada (eixo x) × produção (eixo y), com os anos conectados por uma linha colorida. Se a produtividade crescesse rápido, a curva se afastaria da reta tracejada (produtividade constante). Ela quase não se afasta.
- **B) Bovinocultura — scatter conectado:** pastagem (eixo x) × rebanho (eixo y). A curva se afasta da reta tracejada para cima: o rebanho cresceu mais que a pastagem.
- **C) Soja — séries indexadas (1988 = 100):** área plantada, produção e produtividade. Área e produção caminham juntas; produtividade mal dobra.
- **D) Bovinocultura — séries indexadas (1985 = 100):** pastagem, rebanho e lotação. Pastagem quase não cresce; rebanho sobe 46%; lotação sobe 34%.

### Números de destaque (Goiás)

| Indicador | Início | Fim | Crescimento |
|-----------|--------|-----|-------------|
| Área plantada de soja (SIDRA/PAM) | 0,75 Mha (1988) | 4,94 Mha (2024) | **6,6×** |
| Produção de soja (SIDRA/PAM) | 1,45 Mt (1988) | 16,97 Mt (2024) | **11,7×** |
| Produtividade da soja | 1,94 t/ha (1988) | 3,43 t/ha (2024) | **1,8×** |
| Área de soja no LULC (MapBiomas) | 0,37 Mha (1985) | 4,50 Mha (2024) | **12,1×** |
| Pastagem (MapBiomas) | 10,98 Mha (1985) | 11,99 Mha (2024) | **1,09×** |
| Rebanho bovino (SIDRA) | 15,91 M cab (1985) | 23,22 M cab (2024) | **1,46×** |
| Lotação bovina (cab/ha de pasto) | 1,45 (1985) | 1,94 (2024) | **1,34×** |

### Interpretação / conexão com as pernas do trabalho

- **Perna 2 (intensificação vs. extensificação):** a soja é o caso-paradigma de **extensão**. Quase todo o aumento da produção veio de mais hectares, não de mais toneladas por hectare. A produtividade realmente subiu, mas pouco: 1,8× em 36 anos.
- **Pecuária é o caso oposto:** a pastagem mal cresceu (+9%), mas o rebanho cresceu 46%. A diferença foi **intensificação** — mais cabeças por hectare de pasto. Isso contrasta com a soja e mostra que os dois setores responderam de formas distintas ao mesmo ambiente macro (crédito, câmbio, tecnologia).
- **Atenção ao denominador da soja:** a frase "área de soja cresceu 12×" costuma usar o **LULC MapBiomas** (`lulc_soja_ha`), enquanto a produção vem do **SIDRA/PAM**. Comparar 12× de LULC com 13× de produção dá uma produtividade *aparente* quase estagnada (~1,08×), mas isso mistura duas fontes. O gráfico usa a área plantada SIDRA como denominador, que é o conceito agronômico correto: aí a produtividade cresce ~1,8×.
- **Não prova iLUC:** a figura mostra que a soja expandiu enquanto a pecuária intensificou. Isso é compatível com a hipótese de que a soja ocupou novas áreas sem necessariamente expulsar o gado (o gado ganhou densidade). Mas "compatível com" ≠ "prova de". O teste formal de iLUC no projeto não encontrou assinatura causal significativa (0/36 canais). Esta figura ilustra o padrão espacial/quantitativo; não deve ser lida como evidência causal de deslocamento.

### Fontes

- Produção e área plantada de soja: SIDRA/PAM (`agri_soja_ton`, `agri_soja_ha_plantada`), reconciliadas no painel AMC.
- Rebanho bovino: SIDRA (`pec_bovinos_cab`).
- Pastagem e soja no LULC: MapBiomas coleção 10 (`lulc_pastagem_ha`, `lulc_soja_ha`).
- Unidade espacial: Áreas Mínimas Comparáveis (AMC, Ehrl 2017) — agregadas ao nível estadual nesta figura.

### Como regenerar

```bash
cd Visualizacao
python scripts/gerar_figura_produtividade.py
```

---

## Outras figuras nesta pasta (não geradas nesta conversa)

- `sintese_pecuaria_intensificacao.png` — síntese relacionada à intensificação da pecuária.
- `sintese_culturas_comparadas.png` — comparação entre culturas.
- `sintese_socioeconomico.png` — indicadores socioeconômicos.
- `mapa_pastagem_agricultura_1985_2024.png` — mapa comparativo de pastagem vs. agricultura.
- `07_evolucao_pastagem_soja_estado.png`, `09_scatter_delta_pastagem_soja.png`, `13_scatter_credito_pastagem.png`, `24_fogo_estado_serie.png` — análises parciais anteriores.
