# Plano-mestre original

Conversão para MD do `ResumoDoBrainStorm.ini` (preservado integralmente em [_arquivo/resumo_brainstorm_original.ini](../_arquivo/resumo_brainstorm_original.ini)).

---

## 1. Escopo Analítico e Eixos de Pesquisa

A análise exploratória estrutura-se no cruzamento de dados geoespaciais e tabulares para o período de 1985 a 2024, utilizando o estado de Goiás como unidade de estudo e seus 246 municípios como unidade de análise espacial.

**Eixos de investigação**:

1. **Dinâmica de Conversão (Uso e Cobertura)**: Mapeamento temporal da expansão da pastagem, sua consolidação e posterior substituição por agricultura (ex: soja e cana) ou regeneração de vegetação nativa.

2. **Transição e Vetores**: Quantificação da pastagem como estágio intermediário de ocupação do solo (matrizes de transição de desmatamento → pastagem → lavoura).

3. **Variáveis Econômicas e de Infraestrutura**: Correlação das mudanças espaciais com a evolução do PIB agropecuário, acesso a crédito rural, produção pecuária (lotação animal, produção de leite/carne) e a instalação de infraestrutura agroindustrial (frigoríficos, estradas e silos).

## 2. Fontes de Dados e Acessos

### Uso e Cobertura da Terra (LULC)

- **MapBiomas (Coleção 10.1)**: Dados anuais de 1985 a 2024 (resolução 30m).
  - Classes prioritárias: 15 (Pastagem), 3, 4, 11, 12 (Vegetação Nativa), 18, 20, 39, 41 (Agricultura).
  - Acesso recomendado: Google Earth Engine (GEE).
  - Asset de Cobertura: `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`
  - Transições: Assets de transição do MapBiomas para pares de anos específicos.

### Dados Socioeconômicos (IBGE)

- Acesso: API SIDRA ou biblioteca Python `sidrapy`.
- PPM: Tabela 3939 (Efetivo de rebanhos) e Tabelas 74/94 (Produção pecuária/leite).
- PAM: Tabelas 1612 (Lavouras temporárias) e 1613 (Lavouras permanentes).
- PIB Municipal: Tabela 5938.
- Demografia e Censo Agropecuário: Tabelas 200/6579 (População) e 6778 (Censo Agro).

### Crédito Rural

- **SICOR (Banco Central)**: Dados municipalizados sobre custeio e investimento.
  - API OData: `https://olinda.bcb.gov.br/olinda/servico/SICOR/versao/v2/odata/`
  - Microdados: `https://www.bcb.gov.br/estabilidadefinanceira/micrrural`

### Infraestrutura e Parque Agroindustrial

- Frigoríficos SIF (Federal): Cadastro SIGSIF/MAPA.
- Frigoríficos SIE (Estadual Goiás): Agrodefesa-GO.
- Malha Viária e Hidrovias: SNV/DNIT.
- Armazéns e Silos: CONAB.

### Indicadores de Bem-estar

- IDH Municipal: Atlas do Desenvolvimento Humano (PNUD).

## 3. Metodologia de Tratamento e Espacialização

- **Malha base**: IBGE de referência (ex: 2020) via `geobr`. Ajuste de desmembramentos municipais.
- **Processamento LULC**: tabulação cruzada no GEE (`reduceRegions` com `frequencyHistogram`).
- **Matrizes de Transição**: cruzamento de rasters de diferentes anos no GEE.
- **Integração tabular**: junção via código IBGE de 7 dígitos.
- **Deflação Econômica**: IPCA, mês/ano base para comparabilidade temporal.
- **Geocodificação de Infraestrutura**: endereços → coordenadas → métricas espaciais.

## 4. Stack Tecnológico

| Tecnologia | Papel |
|---|---|
| Google Earth Engine (Python API) | Processamento LULC em nuvem |
| Python Geoespacial | Pipelines e análises (geopandas, pandas, rasterio, matplotlib, seaborn) |
| APIs e Conectores Python | Coleta automatizada (sidrapy, OData BACEN) |
| QGIS | Inspeção visual e layouts cartográficos finais |