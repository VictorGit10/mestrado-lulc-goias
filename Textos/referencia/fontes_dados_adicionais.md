# Fontes de dados adicionais

Tabela extraída do `SugestaoClaude.md` original (preservado em [_arquivo/sugestao_claude_inicial.md](../_arquivo/sugestao_claude_inicial.md)).

| Fonte | O que adiciona | Como acessar |
|---|---|---|
| MapBiomas Transições | Matrizes A→B (floresta-1995 → pastagem-2005 → soja-2015) | Asset GEE `mapbiomas_brazil_collection10_1_transition_v1` |
| MapBiomas — idade da pastagem (calculada) | Anos consecutivos imediatamente anteriores em que cada pixel foi pastagem (classe 15). **Não há asset separado** — calcula-se do asset LULC Coleção 10.1 já em uso, percorrendo as bandas `classification_YYYY` com a lógica do MapBiomas platform-analysis (`analysis_1_age.js`). Pipeline #28 (`coleta_idade_pastagem.py`). | Mesmo asset LULC Coleção 10.1 |
| MapBiomas Fogo | Cicatriz anual. Fogo precede ~70% das conversões no Cerrado | `mapbiomas-public/assets/brazil/fire/collection4` |
| PRODES Cerrado (INPE) | Desmatamento anual com regra "primeira supressão" | `terrabrasilis.dpi.inpe.br` |
| TerraClass Cerrado (INPE/Embrapa) | Distingue pastagem íntegra vs. degradada (categórico) | `terraclass.gov.br` |
| PAM (IBGE) | Tabelas 1612/1613 — área plantada por cultura municipal | `sidrapy` tabelas 1612, 1613, 5457 |
| PPM expandida | Tabela 74 (leite), 94 (ovos), 3939 (efetivo) | `sidrapy` |
| Censo Agropecuário 2006 e 2017 | Estrutura fundiária, mecanização, mão-de-obra | `sidrapy` tabelas 6710–6900 |
| SICOR (BACEN OData) | Crédito rural municipalizado por modalidade e finalidade | `olinda.bcb.gov.br/.../SICOR/v2/odata/` |
| SIGSIF (MAPA) | Frigoríficos federais com endereço | `sigsif.agricultura.gov.br` |
| Agrodefesa-GO | Frigoríficos SIE (estaduais) | `goias.gov.br/agrodefesa` |
| CONAB SISDEP | Silos e armazéns por município, capacidade estática | `sisdep.conab.gov.br` |
| DNIT/SNV | Malha rodoviária pavimentada | `gov.br/dnit` |
| PNUD Atlas Brasil | IDH-M 1991, 2000, 2010, 2021 | `atlasbrasil.org.br` |
| Censos demográficos | População rural/urbana 1991–2022 | `sidrapy` tabelas 200, 6579 |
| CAR/SICAR | Limites prediais + reserva legal declarada | `sicar.gov.br` |
| ANA / OttoBacias | Recorte hidrográfico alternativo ao municipal | `metadados.snirh.gov.br` |
| Xavier/ERA5 | Precipitação mensal gradeada | Xavier (UFES) ou GEE ECMWF/ERA5 |
| Embrapa AgroSatélite / IBGE LSPA | Safrinha (2ª safra) | LSPA via SIDRA tabela 1618 |
| Trase.earth — Brazil beef | Volume/FOB de bovinos exportados por município de origem + frigorífico exportador + logistics hub. 2011–2017 + 2019–2023. CC BY 4.0. | URL direta: `resources.trase.earth/20260511/data/supply-chains/brazil_beef_v2_2_2.zip` (~277 MB, descomprime para 1.86 GB CSV). Já baixado em `data/raw/trase/brazil_beef/`. |
| Trase.earth — Brazil soy | Volume/FOB de soja exportada por município de origem + exporter (Bunge/ADM/Cargill/LDC) + logistics hub. 2004–2022. CC BY 4.0. DOI 10.48650/DCE3-JJ97. | URL direta: `resources.trase.earth/20260511/data/supply-chains/brazil_soy_v2_6_1_composite.zip` (~30 MB). Já baixado em `data/raw/trase/brazil_soy/`. |
| CNPJ Receita Federal | Cadastro nacional de estabelecimentos com `data_abertura`, `data_situacao_cadastral`, CNAE primário. Permite reconstruir contagem anual de frigoríficos/silos por município. | `dadosabertos.rfb.gov.br/CNPJ/` — snapshots mensais ~5 GB cada. CNAEs relevantes: 1011-2 (abate bovinos), 1012-1 (aves/suínos), 1013-9 (carnes preparadas), 5211-7 (armazéns). |

## Censo Agropecuário 2017 — tabelas adicionais

Já coletadas (Pipeline #7): 6878 estrutura fundiária, 6884 pessoal, 6870 tratores, 6848 adubação, 6851 agrotóxicos, 6910 bovinos, 6958 lavouras temporárias. Tabelas SIDRA adicionais ainda não tocadas e relevantes:

| Tabela | Conteúdo | Por que importa |
|---|---|---|
| 6855 | Sistema de preparo do solo (variáveis 2016 nº estabelecimentos com plantio direto na palha, 2018 área com plantio direto) | Proxy direta de modernização agrícola. Conecta com achado consolidado "intensificação produtiva" (Δ Agric × Δ VA agro). |
| 6877 | Veículos no estabelecimento (caminhões, utilitários, automóveis) | Proxy de capacidade logística on-farm. Complementa infraestrutura externa (rodovias, frigoríficos). |
| 6850 | Uso de calcário/corretivos | Insumo crítico para correção do solo cerrado em conversão para agricultura. |
| 6779/6780 | Orientação técnica recebida (governo, cooperativa, ATER privada) | Canal de transferência tecnológica que medeia adoção de práticas que afetam LULC. |
| 6770/6771/6773 | Variantes de estrutura fundiária com cruzamentos por condição legal, CNPJ, residência do produtor | Pode revelar segmentos não capturados pela tabela base 6878. |

## Impacto por eixo

- **Dinâmica de Conversão**: sem matriz de transição, descreve-se estoques mas não trajetórias.
- **Vetores econômicos**: sem SICOR + PAM + frigoríficos, falta o lado causal.
- **Bem-estar**: não foi tocado (IDH-M coletado apenas 1991/2000/2010).