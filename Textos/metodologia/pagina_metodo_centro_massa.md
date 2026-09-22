# "Por dentro do método": a página do centro de massa

**Página:** `Visualizacao/metodo-centro-de-massa.html`
**Criada em:** 21–22/set/2026
**Pipelines explicados:** #32 (centro de massa), #55 (bootstrap de blocos), #43 (teste pixel a pixel)

## Para que serve

As fichas de pipeline e o caderno de preparação para a qualificação explicam o centro de massa em texto, mas ler a explicação não é o mesmo que ver a conta acontecer. Esta página refaz a conta do #32 **no navegador**, com os dados reais, e deixa o leitor mexer em cada passo. Pode ser usada para estudar o método e também como material público do site.

Ela é a primeira de uma série, **"Por dentro do método"**, com uma página por método, cada uma no mesmo molde (ver a última seção).

## Regra de origem dos números

Nenhum número da página é digitado à mão. Eles vêm de duas fontes:

- **Refeitos.** A página refaz o centro médio, o mediano (Weiszfeld), a decomposição, o bootstrap e o deslocamento pixel a pixel na mesma régua, a partir dos pesos e posições do JSON.
- **Oficiais.** O que vem de CSV de pipeline é lido de `D.oficial` e rotulado com o nome do arquivo: `centro_massa_anual.csv`, `centro_massa_deslocamento.csv`, `centro_massa_bootstrap.csv`, `centro_massa_bootstrap_bloco.csv` e `centro_massa_pixel_anual.csv`.

Onde as duas coisas aparecem juntas (a tabela por ato, o IC do bootstrap), elas ficam lado a lado.

**Conferência dupla:**
1. `scripts/exportar_metodo_centro_massa_viz.py` recalcula o centro com os pesos que vai exportar e **aborta** se a diferença para `centro_massa_anual.csv` passar de 10 m. Na geração de 22/set, a diferença foi de 0,05 m.
2. Ao abrir, a página refaz os 160 centros (4 variáveis × 40 anos) e mostra no topo e no rodapé a maior diferença contra o CSV. Dá 0,6 m, que é o arredondamento com que o JSON grava as posições (ao metro) e os pesos (a 0,1 ha).

## Fluxo de dados

```
data/processed/painel_amc_goias.parquet  ┐
data/processed/amc_goias.gpkg            │  (#25)
data/processed/centro_massa_*.csv        ├─► scripts/exportar_metodo_centro_massa_viz.py
data/processed/amc_crosswalk_goias.csv   │        │ confere contra o #32 e aborta se divergir
data/raw/idhm/ipea_idhm_adh_goias.csv    ┘        ▼
                              Visualizacao/assets/data/metodo_centro_massa.json (~0,5 MB)
                                                   │ fetch
                              Visualizacao/assets/js/metodo-centro-massa.js  (d3 v7 do vendor)
                              Visualizacao/assets/css/metodo.css
                              Visualizacao/metodo-centro-de-massa.html
```

O que o JSON leva:
- os polígonos das 166 AMC em km locais (simplificados a 700 m, só para desenho);
- os centroides, calculados sobre o polígono inteiro em EPSG:5880, **depois** da projeção, como no #32;
- os pesos `[ano][amc]` das quatro variáveis, com a regra do #32 (NaN ou ≤0 vira 0);
- as partições em blocos do #55, importadas de `robustez_bootstrap_bloco.kmeans_blocos` com a mesma semente e a mesma grade `GRADE_K`;
- um polinômio de grau 3 que converte EPSG:5880 em lon/lat, com erro máximo de 14 m, usado só para rotular latitude;
- a graticula e os resultados oficiais.

**Regenerar:** `python scripts/exportar_metodo_centro_massa_viz.py`. É preciso rodar de novo sempre que o painel AMC ou algum dos CSVs do #32/#43/#55 mudar.

**Gotcha dos nomes:** `amc_nome_rep` no parquet perdeu a acentuação (U+FFFD, "Goi�nia"). O exportador recupera o nome pelo código IBGE (crosswalk → `cd_mun` → nome do IDHM bruto) e aborta se ainda sobrar algum caractere quebrado. O defeito continua no parquet do #25 e não foi corrigido lá.

## Os 11 capítulos

| # | Capítulo | O que a figura faz | Álgebra de origem |
|---|---|---|---|
| 1 | A pergunta | fórmula e intuição | #32 |
| 2 | Cada AMC vira um ponto | mapa. Clicar mostra o centroide (km locais, metros EPSG:5880, lat/lon). Um botão encolhe os polígonos até o centroide | #32 `carregar_dados` |
| 3 | Cada ponto recebe um peso | círculos ou densidade, 1985/2024. Mostra as 8 AMC mais pesadas | painel #25 |
| 4 | O equilíbrio visto de lado | régua norte–sul com o peso somado em faixas de 10 km e um apoio arrastável. A régua inclina conforme ȳ − p | #32 (componente N) |
| 5 | A conta, linha por linha | tabela com 166 linhas de w·y. As AMC entram uma a uma e o centro parcial caminha no mapa. Três ordens, mesmo ponto final. Compara com o CSV | #32 `mean_center` |
| 6 | Quarenta contas | trajetórias ampliadas, série de latitude com os atos, tabela por ato (pipeline × refeito) | #32 `tabela_deslocamento` |
| 7 | De onde vêm os km | decomposição ΔN = Σ(s_fim − s_ini)(y − ȳ_ini): mapa divergente, cascata em 4 grupos e as 8 maiores parcelas | identidade contábil (nova, só leitura) |
| 8 | Centro mediano | Weiszfeld passo a passo. Clicar numa AMC multiplica o peso por 10 | #32 `median_center` |
| 9 | Quanto é ruído | bootstrap ao vivo (mulberry32, semente 42) com o mapa das cópias, histograma, o IC ao vivo ao lado do #55, seletor de blocos e a grade de IC do #55 | #32 `bootstrap_incerteza`, #55 |
| 10 | Sem malha nenhuma | série AMC × pixel desde 1985 e tabela na mesma régua | #43 |
| 11 | O que o método não diz | veredito e limites | — |

A barra de variável no topo (pastagem, rebanho, agricultura, vegetação natural) reprograma todas as figuras de uma vez.

### A decomposição (capítulo 7) não é resultado novo

A página diz isso explicitamente. É a mesma conta do #32 reescrita: como Σ Δs = 0, subtrair ȳ_ini de cada y não altera a soma. A página verifica que as 166 parcelas somam o ΔN direto até o metro. Os números servem para **ler** o deslocamento, e nenhum deles entrou no texto da dissertação:

| variável | norte ganhou | sul perdeu | norte perdeu | sul ganhou | ΔN |
|---|---|---|---|---|---|
| pastagem | +55,0 | +26,4 | −2,3 | −1,4 | +77,6 |
| rebanho | +43,5 | +28,0 | −3,3 | −1,3 | +66,9 |
| agricultura | +60,4 | +9,2 | −1,5 | −2,8 | +65,2 |

Se algum dia for para o texto, entra como pipeline próprio, com ficha.

## Decisões de desenho

- **A placa 3D foi descartada.** O primeiro protótipo (three.js, "A balança de Goiás", fora do site) punha o estado numa placa apoiada num lápis. Vista de cima, a inclinação quase não aparece, e foi esse o comentário do autor. O substituto é a **régua vista de lado** do capítulo 4, que mostra só a componente norte. É exatamente o número reportado, e a inclinação fica visível.
- **O estilo do site, e não um estilo próprio:** coluna de 900 px, `styles.css`, capítulos com título em terracota e as caixas `pista` / `veredito-box` / `nao-mostra` do `dossie-mosaico.html`, com as cores das séries de `centros_massa_completo.json`. Sem tema escuro, como o resto do site.
- **O sorteio ao vivo não substitui o oficial.** O bootstrap da página usa outro gerador (mulberry32), então o IC ao vivo difere do #55 na casa das unidades de km. A página mostra os dois e diz que a diferença é ruído do próprio sorteio.
- **Animação só quando algo muda.** Os laços de `requestAnimationFrame` param quando a figura converge, e `prefers-reduced-motion` desliga as animações.

## Achado de passagem: a régua do teste do pixel

O `index.html` e o caderno (`p3a_matematica.tex`, caixa "Pixel contra AMC") citam o pixel como **pastagem +79,2 km e agricultura +66,9 km** contra +77,6 e +65,2 na AMC. Só que as duas medições estão em réguas diferentes:
- o #43 imprime Δlat × 111 km/grau (`centro_massa_pixel.py`, `dlat * 111.0`);
- o #32 mede Δy em metros EPSG:5880.

Na **mesma régua** (a média do pixel reprojetada para EPSG:5880):

| | AMC | pixel (5880) | diferença | como citado hoje |
|---|---|---|---|---|
| pastagem | +77,6 | +78,8 | +1,2 | +79,2 (+1,6) |
| agricultura | +65,2 | +65,8 | +0,5 | +66,9 (+1,7) |
| vegetação natural | +7,6 | +6,5 | −1,0 | — |

A conclusão não muda, e a distância entre as duas medições **diminui**. A página nova usa a mesma régua e explica a diferença numa nota (capítulo 10). O `index.html` e o caderno **ainda não foram alinhados**. A decisão fica com o autor. É o mesmo padrão de "régua sem etiqueta" que já apareceu na revisão de 14/ago.

## Pendências

- [ ] Link para a página no `index.html` (proposta: um card em "Bastidores", ao lado do Atlas e do Caso do Mosaico). Por enquanto a página não aparece em nenhum link da página principal.
- [ ] Versão em inglês (`metodo-centro-de-massa.en.html`), como as outras páginas à parte.
- [ ] Alinhar a régua do pixel no `index.html` e no caderno (ver acima).
- [ ] Nenhuma verificação visual por captura de tela foi possível na sessão de criação, porque o painel do navegador não renderizava. A verificação foi funcional, por script: todos os capítulos, console limpo e 375 px sem rolagem lateral.

## Como fazer a próxima página da série

1. Um exportador `scripts/exportar_metodo_<nome>_viz.py` que leia os mesmos arquivos do pipeline, confira contra o CSV oficial e **aborte se divergir**.
2. `Visualizacao/metodo-<nome>.html`, que reaproveita `assets/css/metodo.css` (barra, KPIs, roteiro, capítulos, `.mt-fig`, `.mt-ctl`, `.formula`, as caixas).
3. `Visualizacao/assets/js/metodo-<nome>.js`, com a mesma regra: número oficial vem de `D.oficial` e é rotulado com o arquivo; número refeito é recalculado no navegador.
4. Cada capítulo com uma caixa "o que não diz". Os candidatos, pelo caderno, são o shift-share com inferência por permutação (#54), Granger/Toda-Yamamoto e a mistura de gaussianas (#28).
