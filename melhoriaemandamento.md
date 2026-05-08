  Contexto
                                                                                                 
     O site de visualização tem dois modos funcionais (Narrativa + Atlas), mas 3 das 4 variáveis 
     do Atlas estão desabilitadas (prontoMVP: false). A Síntese final ainda não tem o diagrama   
     Sankey. O sparkline mostra apenas LULC. Este plano executa as fases A3 → A1+A4 → A5 → E3 em
     sequência lógica, desbloqueando features progressivamente.

     Estado atual dos dados:
     - painel_goias.json — 40 anos × 18 colunas (UF agregada)
     - marcos.json — 8 marcos políticos
     - transicoes_resumo.json — 7 classes, 1985→2024
     - 40 mapas LULC (WebP) em img/mapas_gee/

     Dados disponíveis mas NÃO consumidos pelo site:
     - painel_unificado.parquet — 9.840 × 66 (246 municípios × 40 anos, incluindo fogo_*,        
     sicor_*, pib_*, pec_*, idhm*)
     - fogo_mapbiomas_goias.csv — fogo por município × ano × classe LULC
     - transicoes_mapbiomas_goias.csv — matrizes de transição pixel-a-pixel
     - outputs/transicoes/sankey_1985_2024.html — Sankey Plotly (5 MB, ineficiente para embed)   

     ---
     Fase 1: Expandir preparar_dados_timeline.py (A3)

     Objetivo: Gerar 5 novos JSONs a partir do painel_unificado.parquet e outras fontes.

     Arquivos a modificar:
     - Visualizacao/scripts/preparar_dados_timeline.py

     Novos JSONs a gerar:

     1.1 assets/data/fogo_goias.json

     Série UF agregada, 40 anos × 6 classes de fogo. Schema:
     {
       "unidade": "Goias (UF)",
       "n_anos": 40,
       "classes": ["veg_nat", "pastagem", "agricultura", "mosaico", "outros", "total"],
       "serie": [
         { "ano": 1985, "veg_nat": 2091625.36, "pastagem": ..., "total": ... },
         ...
       ]
     }
     Fonte: agregar painel_unificado.parquet por ano, somando colunas fogo_veg_nat_ha,
     fogo_pastagem_ha, fogo_agricultura_ha, fogo_mosaico_ha, fogo_outros_ha, fogo_total_ha.      

     1.2 assets/data/painel_municipal_indice.json

     Lookup leve: 246 municípios. Schema:
     [
       { "cd_mun": 5200050, "nm_mun": "Abadia de Goias", "microrregiao": "...", "lat": -16.75,   
     "lon": -49.34 },
       ...
     ]
     Fonte: painel_unificado.parquet (colunas cd_mun, nm_mun) + centroides do geobr.

     1.3 assets/data/municipios/{cd_mun}.json × 246

     Série municipal compacta. Cada arquivo:
     {
       "cd_mun": 5208707, "nm_mun": "Goiania",
       "serie": [
         { "ano": 1985, "pct_veg_nat": 0.12, "pct_pastagem": 0.35, ... },
         ...
       ]
     }
     Fonte: painel_unificado.parquet, filtrado por município, ~20 colunas selecionadas (LULC %,  
     fogo, PIB, crédito, lotação).

     1.4 assets/data/transicoes_matriz.json

     5 matrizes 6×6 (por período). Schema:
     {
       "periodos": [
         {
           "rotulo": "1985 → 1995",
           "classes_orig": ["Vegetação Natural", "Pastagem", ...],
           "classes_dest": ["Vegetação Natural", "Pastagem", ...],
           "matriz": [[...6x6...]]
         },
         ...
       ]
     }
     Fonte: agregar transicoes_mapbiomas_goias.csv por período, somando area_ha.

     1.5 assets/data/sankey_data.json

     Nodos + links para D3-sankey. Schema:
     {
       "nodes": [
         { "id": "veg_1985", "label": "Vegetação Natural (1985)", "color": "#2d5a3d" },
         ...12 nodes (6 classes × 2 anos)...
       ],
       "links": [
         { "source": "veg_1985", "target": "veg_2024", "value": 11883358 },
         ...30 links (6×6 - 6 diagonais = 30 fluxos não-triviais + 6 diagonais)...
       ]
     }
     Fonte: agregar transicoes_mapbiomas_goias.csv filtrando ano_origem=1985, ano_destino=2024,  
     somando area_ha por par de classes. Converter para Mha para legibilidade.

     Verificação: Rodar python Visualizacao/scripts/preparar_dados_timeline.py e confirmar que os
      5 novos JSONs foram gerados corretamente no diretório assets/data/.

     ---
     Fase 2: Gerar mapas de fogo (A1) e delta (A4)

     Objetivo: Criar 80 novos WebP (40 de fogo + 40 de delta) para habilitar os toggles do Atlas.

     2.1 Script gerar_mapas_fogo_40anos.py

     Novo arquivo: Visualizacao/scripts/gerar_mapas_fogo_40anos.py

     Estrutura (seguindo o padrão de gerar_mapas_lulc_40anos.py):
     1. Ler painel_unificado.parquet e agregar fogo_total_ha por município × ano
     2. Carregar malha municipal via geobr.read_municipality(code_muni="GO", year=2020)
     3. Calcular breaks Jenks globais (mesmos para os 40 anos) usando jenkspy ou manual
     4. Aplicar np.log1p() para escala log (fogo é altamente enviesado)
     5. Gerar 40 coropléticos municipais: cmap YlOrRd, municípios sem fogo em cinza #ececec      
     6. Salvar em Visualizacao/img/mapas_fogo/fogo_{ano}.png
     7. Converter para WebP com qualidade 85 (reutilizar lógica de otimizar_mapas_webp.py)       

     2.2 Script gerar_mapas_delta_lulc.py

     Novo arquivo: Visualizacao/scripts/gerar_mapas_delta_lulc.py

     Estrutura similar:
     1. Ler painel_unificado.parquet, calcular pct_pastagem_lulc por município × ano
     2. Baseline = 1985: delta_pct = pct_pastagem[ano] - pct_pastagem[1985]
     3. Carregar malha municipal via geobr
     4. Cmap diverging RdBu_r centrado em 0; 1985 = todo neutro
     5. Gerar 40 coropléticos em Visualizacao/img/mapas_delta/delta_{ano}.png
     6. Converter para WebP

     Verificação: Abrir img/mapas_fogo/fogo_2020.webp e img/mapas_delta/delta_2024.webp no       
     browser. Fogo 2020 deve ser visivelmente mais intenso que 1995. Delta 2024 deve mostrar     
     contraste verde-vermelho forte; 1985 deve ser neutro.

     ---
     Fase 3: Habilitar toggles do Atlas (A5)

     Objetivo: Ativar Fogo, Transições e Delta no Atlas após Fases 1 e 2.

     3.1 Editar assets/js/utils.js

     Alterar prontoMVP: false → prontoMVP: true para as 3 variáveis:
     { id: "fogo",       ..., prontoMVP: true,  ... },
     { id: "transicoes", ..., prontoMVP: true,  ... },
     { id: "delta",      ..., prontoMVP: true,  ... },

     3.2 Editar index.html (linhas 282-284)

     Remover disabled e classe atlas-var--coming dos 3 botões. Adicionar data-var="fogo", etc.   

     3.3 Gerar mapas de transição (5 períodos)

     Para o toggle "Transições", são necessários 5 WebPs:
     - img/mapas_transicoes/transicao_1985-1995.webp
     - img/mapas_transicoes/transicao_1995-2005.webp
     - img/mapas_transicoes/transicao_2005-2015.webp
     - img/mapas_transicoes/transicao_2015-2024.webp
     - img/mapas_transicoes/transicao_1985-2024.webp

     Esses já existem como PNGs em outputs/transicoes/mapa_transicao_dominante_*.png. Copiar e   
     converter para WebP.

     Verificação: Recarregar o site, clicar em cada toggle do Atlas e verificar que os mapas     
     aparecem no grid e no lightbox.

     ---
     Fase 4: Sankey na Síntese (E3)

     Objetivo: Adicionar diagrama de Sankey interativo na seção <section class="sintese">.       

     4.1 Adicionar vendors D3 + d3-sankey

     Baixar versões mínimas (partial bundle):
     - d3.v7.min.js (~280 KB) → assets/js/vendor/d3.v7.min.js
     - d3-sankey.min.js (~15 KB) → assets/js/vendor/d3-sankey.min.js

     Se possível, gerar bundle parcial com apenas d3-selection + d3-scale + d3-sankey (~100 KB). 

     4.2 Criar assets/js/sankey.js (~150 linhas)

     - IntersectionObserver lazy-load: só carrega D3 + sankey quando a seção Síntese entra na    
     viewport
     - Fetch sankey_data.json
     - Renderizar diagrama SVG dentro de <div id="sankey-container">
     - Cores dos nodos alinhadas com a paleta do site (var(--color-veg), var(--color-pasto),     
     etc.)
     - Responsivo (redimensiona com window.resize)

     4.3 Editar index.html

     Adicionar dentro de <section class="sintese">:
     <div id="sankey-container" class="sankey-container">
       <p class="resumo-loading">Carregando diagrama…</p>
     </div>

     Adicionar antes de </body>:
     <!-- Sankey (lazy-loaded) -->

     4.4 Adicionar estilos em styles.css

     Estilos para .sankey-container, .sankey-node, .sankey-link, .sankey-tooltip.

     Verificação: Scroll até a seção Síntese. DevTools Network deve mostrar que d3.v7.min.js e   
     sankey_data.json só carregam após a seção ficar visível. O diagrama deve mostrar 6 classes ×
      2 anos com fluxos proporcionais.

     ---
     Fase 5: Documentação

     Objetivo: Atualizar IMPLEMENTACAO.md refletindo o que foi feito e apontando o que falta.    

     5.1 Atualizar seção de estado atual

     - Marcar A1, A3, A4, A5, E3 como concluídos
     - Atualizar lista de arquivos com novos scripts e JSONs
     - Recalcular tamanho total do bundle

     5.5 Atualizar lista de pendências

     Remover itens concluídos. Manter como pendente:
     - ~~Embed do Sankey~~ → CONCLUÍDO
     - A2 (TopoJSON) — pré-requisito para drill-down municipal (Fase D)
     - D1-D4 (drill-down municipal)
     - E1 (sparkline com toggle)
     - E2 (pinos extras na régua)
     - F1-F3 (polish, cross-browser, deploy)

     ---
     Ordem de execução

     ┌───────┬───────────────────────────────────────────┬────────────────┬────────────┐
     │ Passo │                 Descrição                 │  Dependência   │ Tempo est. │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 1     │ Expandir preparar_dados_timeline.py       │ Nenhuma        │ ~1h        │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 2     │ Rodar script e validar JSONs              │ Passo 1        │ ~5min      │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 3     │ Criar gerar_mapas_fogo_40anos.py          │ Passo 2        │ ~1h        │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 4     │ Criar gerar_mapas_delta_lulc.py           │ Passo 2        │ ~1h        │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 5     │ Gerar mapas + WebP                        │ Passos 3, 4    │ ~5min      │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 6     │ Copiar e converter mapas de transição     │ Nenhuma        │ ~5min      │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 7     │ Habilitar toggles (utils.js + index.html) │ Passos 2, 5, 6 │ ~10min     │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 8     │ Baixar vendors D3                         │ Nenhuma        │ ~5min      │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 9     │ Criar sankey.js + editar HTML/CSS         │ Passo 2        │ ~1.5h      │
     ├───────┼───────────────────────────────────────────┼────────────────┼────────────┤
     │ 10    │ Atualizar IMPLEMENTACAO.md                │ Todos          │ ~20min     │
     └───────┴───────────────────────────────────────────┴────────────────┴────────────┘

     Tempo total estimado: ~5h

     ---
     O que fica pendente (não incluído neste plano)

     - A2 (TopoJSON de Goiás) — necessário para drill-down interativo
     - D1-D4 (drill-down municipal) — requer A2 + A3
     - E1 (sparkline com toggle LULC/Fogo/Crédito) — requer fogo_goias.json (disponível após     
     Fase 1)
     - E2 (3 pinos extras na régua: 2013, 2017, 2020)
     - F1-F3 (polish, cross-browser, Lighthouse, deploy)
     - Mapas de transição com TopoJSON interativo (fase futura)

     ---
     Verificação end-to-end

     1. python Visualizacao/scripts/preparar_dados_timeline.py → 8 JSONs em assets/data/
     2. python Visualizacao/scripts/gerar_mapas_fogo_40anos.py → 40 PNGs + 40 WebPs em
     img/mapas_fogo/
     3. python Visualizacao/scripts/gerar_mapas_delta_lulc.py → 40 PNGs + 40 WebPs em
     img/mapas_delta/
     4. Copiar 5 PNGs de outputs/transicoes/ → WebPs em img/mapas_transicoes/
     5. python -m http.server 8765 --directory Visualizacao → abrir browser
     6. Testar: Narrativa scroll, Atlas LULC, Atlas Fogo, Atlas Delta, Atlas Transições, Sankey  
     na Síntese
     7. Validar URL hash: #atlas/fogo/2020, #atlas/delta/2024, #atlas/transicoes/1985-2024