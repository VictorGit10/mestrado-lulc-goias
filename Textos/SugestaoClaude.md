🗂️ Mais fontes de dados para enriquecer a tese

  Camadas que faltam e mudariam a história

  ┌────────────────────────┬────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┐    
  │         Fonte          │                                 O que adiciona                                 │                         Como acessar                          │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ MapBiomas Transições   │ Matrizes A→B (ex: floresta-1995 → pastagem-2005 → soja-2015). É o coração do   │ Asset GEE mapbiomas_brazil_collection10_1_transition_v1 ou    │    
  │                        │ eixo "vetor de ocupação" do seu brainstorm.                                    │ tabela pré-computada                                          │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ MapBiomas Fogo         │ Cicatriz anual. Fogo precede ~70% das conversões no Cerrado — explica como a   │ mapbiomas-public/assets/brazil/fire/collection4               │    
  │                        │ pastagem aparece.                                                              │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ PRODES Cerrado (INPE)  │ Desmatamento anual com regra "primeira supressão". Resolução temporal melhor   │ terrabrasilis.dpi.inpe.br                                     │    
  │                        │ que MapBiomas para quando desmatou.                                            │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ TerraClass Cerrado     │ Distingue pastagem "íntegra" vs. degradada — sem entrar em "qualidade/vigor"   │ terraclass.gov.br                                             │    
  │ (INPE/Embrapa)         │ no sentido espectral, só uma flag categórica.                                  │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ PAM (IBGE)             │ Tabelas 1612/1613 — produção e área plantada por cultura municipal. Sem isso,  │ sidrapy tabelas 1612, 1613, 5457                              │    
  │                        │ "agricultura" no MapBiomas é só pixel — não tem soja, milho, sorgo.            │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ PPM expandida          │ Tabela 74 (leite), 94 (ovos), 3939 (efetivo). Fluxo de produto, não só         │ sidrapy                                                       │    
  │                        │ rebanho.                                                                       │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ Censo Agropecuário     │ Estrutura fundiária: nº imóveis por estrato de área, mecanização, mão-de-obra. │ sidrapy tabelas 6710–6900                                     │    
  │ 2006 e 2017            │  Recortes que PPM/PAM não dão.                                                 │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ SICOR (BACEN OData)    │ Crédito rural municipalizado por modalidade (custeio/investimento) e           │ olinda.bcb.gov.br/.../SICOR/v2/odata/                         │    
  │                        │ finalidade (formação de pasto, máquinas). Direto do brainstorm.                │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ SIGSIF (MAPA)          │ Frigoríficos federais com endereço. Pontos para geocoding + análise de         │ sigsif.agricultura.gov.br                                     │    
  │                        │ proximidade.                                                                   │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ Agrodefesa-GO          │ Frigoríficos SIE (estaduais), abatedouros menores. Complementa SIGSIF.         │ goias.gov.br/agrodefesa                                       │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ CONAB SISDEP           │ Silos e armazéns por município, capacidade estática. Mostra onde a logística   │ sisdep.conab.gov.br                                           │    
  │                        │ travou.                                                                        │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ DNIT/SNV               │ Malha rodoviária pavimentada. Acessibilidade → expansão da fronteira.          │ gov.br/dnit                                                   │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ PNUD Atlas Brasil      │ IDH-M 1991, 2000, 2010, 2021. Bem-estar humano vs. expansão pastoril.          │ atlasbrasil.org.br                                            │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ Censos demográficos    │ População rural/urbana 1991–2022. Esvaziamento rural correlaciona com pastagem │ sidrapy tabelas 200, 6579                                     │    
  │                        │  extensiva.                                                                    │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ CAR/SICAR              │ Limites prediais + reserva legal declarada. Dá granularidade abaixo do         │ sicar.gov.br (download por UF)                                │    
  │                        │ município.                                                                     │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ ANA / OttoBacias       │ Recorte hidrográfico — alternativa ao recorte municipal para análise           │ metadados.snirh.gov.br                                        │    
  │                        │ ambiental.                                                                     │                                                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ Xavier/ERA5            │ Precipitação mensal grade. Controle climático para regressões.                 │ Xavier (UFES) ou GEE ECMWF/ERA5                               │    
  ├────────────────────────┼────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤    
  │ Embrapa AgroSatélite / │ Safrinha (2ª safra) — chave da intensificação agrícola, MapBiomas mistura num  │ LSPA via SIDRA tabela 1618                                    │    
  │  IBGE LSPA             │ só pixel.                                                                      │                                                               │    
  └────────────────────────┴────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────┘    

  Onde isso muda a tese

  - Hoje seu eixo "Dinâmica de Conversão" tem só estoques anuais por classe. Sem matriz de transição, você descreve, mas não rastreia trajetórias.
  - "Vetores econômicos" hoje tem PIB e rebanho. Sem SICOR + PAM + frigoríficos, você não tem o lado da causa: crédito, infraestrutura, viabilidade.
  - "Bem-estar" não foi tocado.

  ---
  🤝 Onde eu posso contribuir concretamente

  Posso construir cada um desses módulos como scripts independentes plugando no que já existe:

  1. pipeline_municipal.py — baixa MapBiomas munis (xlsx separado), normaliza para malha IBGE 2020 via geobr, resolve desmembramentos (Goiás teve ~14 entre 1989 e 1995). Saída: 
  GeoDataFrame [cd_mun, ano, classe, area_ha, geometry].
  2. transicoes_mapbiomas.py — extrai matriz A→B via GEE Python API ou tabela pré-computada. Pares-chave: 1985→2000, 2000→2010, 2010→2024.
  3. coleta_sidra.py — wrapper único para PAM, PPM, Censo Agro com retry, cache e padronização de schema.
  4. coleta_sicor.py — cliente OData paginado. Já cuido de paginação $skip/$top, retry, deflação automática.
  5. geocode_frigorificos.py — parser do CSV SIGSIF + tabela Agrodefesa, geocoding (Nominatim/IBGE), saída como pontos. Calcula vizinho-mais-próximo por município.
  6. indicadores_compostos.py — taxa de conversão floresta→pasto (ha/ano por município), tempo médio entre desmate e cultivo, persistência de pastagem.
  7. analise_estatistica.py — correlação, Moran's I global e local, regressão espacial (pysal/spreg).
  8. dashboard_streamlit.py — opcional, mas eu monto se for útil para a banca.

  Recomendaria fazer nessa ordem (1 → 2 → 3 desbloqueia o resto).

  ---
  🗺️ Espacialização e mapas — perguntas para você decidir antes de eu codar

  Sobre a unidade espacial

  1. Malha de referência: IBGE 2020 (250 mil), 2022 ou 2024? Goiás tem 246 munis hoje, mas em 1985 tinha ~199 — vai harmonizar para qual ano? Recomendação: usar 2020 e agregar  
  séries anteriores via pai-filho de desmembramento (geobr tem read_municipality_seat).
  2. Bacia ou município? Para a análise ambiental, OttoBacias nível 4 ou 5 fragmentam menos a paisagem. Para socioeconômica, município é obrigatório (é onde IBGE/BACEN
  publicam).
  3. Mistura? Posso gerar duas malhas: municipal para correlações com SIDRA/SICOR, e bacia para análise de transição/desmatamento. Junção via área proporcional.

  Sobre projeção e CRS

  4. CRS para análise de área: Goiás cobre tanto UTM 22S quanto 23S. Para cálculos de área honestos use Albers Cônica de Áreas Iguais (Brasil) — EPSG:5880 ou customizada        
  +proj=aea +lat_1=-2 +lat_2=-22 +lat_0=-12 +lon_0=-54. Para mapas finais que não distorçam: SIRGAS 2000 lat/long (EPSG:4674) com equalearth.
  5. Web Mercator (3857) NÃO, exceto se for embed em Folium/Leaflet — distorce área em 30% nessa latitude.

  Sobre os tipos de mapa

  6. Snapshots vs. animação: anos-chave (1985, 1995, 2005, 2015, 2024) num painel de 5 mapas, ou GIF anual? Painel é melhor para PDF de tese; GIF para apresentação oral/digital.  7. Coropleto absoluto vs. relativo: pastagem em ha mostra "onde tem", em % da área municipal mostra "onde domina". Os dois contam histórias diferentes — vale gerar ambos.     
  8. Bivariados: matrizes 3×3 cor (Joshua Stevens) cruzando pastagem × crédito, ou desmatamento × frigoríficos. Visualmente densos, mas didáticos.
  9. Hotspot (LISA / Getis-Ord): clusters HH/LL de variação de pastagem. Identifica fronteiras ativas vs. estabilizadas.
  10. Mapa de fluxo: setas A→B sobre matriz de transição (origem-destino dentro de Goiás).

  Sobre a estética e legibilidade

  11. Classes: quantis (5 classes) ou Jenks natural breaks? Jenks para distribuições enviesadas como pastagem; quantis para comparação entre mapas.
  12. Paleta: divergente (RdYlBu) para variações, sequencial (YlOrBr) para estoques. Daltonismo: ColorBrewer já cobre.
  13. Camadas-base: relevo sombreado SRTM ou contorno limpo? Município com >2.000 unidades vai poluir; Goiás com 246 cabe bem.
  14. Mapas temáticos múltiplos no mesmo layout (small multiples): 4 décadas em 4 painéis com legenda compartilhada — padrão-ouro para tese.

  Sobre infraestrutura técnica

  15. GeoPackage ou Shapefile? GPKG. Sempre. Shapefile trunca nomes de coluna em 10 chars e perde Unicode.
  16. PostGIS local? Útil se passar de 5GB de raster ou se quiser SQL espacial. Para uma dissertação solo, geopandas+gpkg basta.
  17. GEE: account próprio ou via assets públicos pré-computados? Pré-computados são mais rápidos para iterar; GEE direto é necessário só para transições customizadas e
  fogo×LULC.
  18. Saída final em QGIS? Brainstorm já diz que sim. Fluxo natural: Python gera os GPKG/CSV/PNG; QGIS faz o layout final cartográfico (escala, norte, créditos, grid).

  ---
  Quer que eu comece por algum bloco específico? Sugiro municipalização primeiro — é pré-requisito para tudo que envolve mapas. Depois matriz de transição, que é o coração do   
  que sua tese se propõe a explicar.