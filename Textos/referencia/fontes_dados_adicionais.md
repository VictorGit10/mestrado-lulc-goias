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
| **CONAB — capacidade de armazenagem** (Pipeline #53) | **Dois arquivos fetcháveis** por download direto (`portaldeinformacoes.conab.gov.br/downloads/arquivos/`): **(a)** `ArmazensCadastrados.txt` (~8 MB, `;`/latin1) = cadastro **atual** de armazéns com `cod_ibge` + capacidade estática/expedição/recepção + **lat/lon** — snapshot municipal, **sem coluna de data**; **(b)** `exportacao_capacidade_estatica.xls` (BIFF, precisa `xlrd`) = série histórica **por UF** (`Ano·UF·Quantidade`, 2005+), **não municipal**. ⚠️ Correção: não há série de capacidade **municipal** por ano (a "por município" só existe no snapshot). GO = 1.135 armazéns / 18,5 Mt. Vira o centroide do #53. | `portaldeinformacoes.conab.gov.br/download-arquivos.html` |
| **Embrapa — Aptidão Agrícola das Terras** (Pipeline #52) | Camada nacional (1:500.000) de aptidão edafoclimática, sistema Ramalho Filho & Beek (1995), campo ordinal `simb_apt` (grupo 1 boa→6 preservação). Usada como exposição **exógena** e não-complementar no drive comum do #38 (substitui o proxy de área). Alternativa estadual mais fina (MacroZAEE-GO, 1:250k) **não é fetchável** deste ambiente (cert TLS quebrado do SIEG) — fica como pendência de refino. | WFS: `geoinfo.dados.embrapa.br/geoserver/ows`, camada `geonode:aptidao_agr_bra`. Coletor: `scripts/aptidao_edafo_exposicao.py` → `data/processed/aptidao_edafo_amc.csv`. |
| DNIT/SNV | Malha rodoviária pavimentada | `gov.br/dnit` |
| PNUD Atlas Brasil | IDH-M 1991, 2000, 2010, 2021 | `atlasbrasil.org.br` |
| **FIRJAN IFDM** (Pipeline #51) | Índice de Desenvolvimento Municipal, **Nova Série Histórica municipal 2013–2023** (anual; 4 dimensões: Geral/Emprego&Renda/Educação/Saúde). **Alcança o Ato III** — reabre o eixo de desenvolvimento que o IDH-M (só 1991/2000/2010) não cobre. Série nova ≠ emendável com a antiga 2005–16. | XLSX direto: `firjan.com.br/data/files/09/42/7A/34/0EFA6910734FAA69D8284EA8/Serie-Historica-IFDM-2013-a-2023.xlsx`. Coletor: `scripts/coleta_firjan_ifdm.py` → `data/processed/ifdm_goias_municipal.csv`. Chave `COD_MUNIC` (6 díg.) → `cd_mun` via `//10`. |
| Censos demográficos | População rural/urbana 1991–2022 | `sidrapy` tabelas 200, 6579 |
| CAR/SICAR | Limites prediais + reserva legal declarada | `sicar.gov.br` |
| ANA / OttoBacias | Recorte hidrográfico alternativo ao municipal | `metadados.snirh.gov.br` |
| Xavier/ERA5 | Precipitação mensal gradeada | Xavier (UFES) ou GEE ECMWF/ERA5 |
| Embrapa AgroSatélite / IBGE LSPA | Safrinha (2ª safra) | LSPA via SIDRA tabela 1618 |
| Trase.earth — Brazil beef | Volume/FOB de bovinos exportados por município de origem + frigorífico exportador + logistics hub. 2011–2017 + 2019–2023. CC BY 4.0. | URL direta: `resources.trase.earth/20260511/data/supply-chains/brazil_beef_v2_2_2.zip` (~277 MB, descomprime para 1.86 GB CSV). Já baixado em `data/raw/trase/brazil_beef/`. |
| Trase.earth — Brazil soy | Volume/FOB de soja exportada por município de origem + exporter (Bunge/ADM/Cargill/LDC) + logistics hub. 2004–2022. CC BY 4.0. DOI 10.48650/DCE3-JJ97. | URL direta: `resources.trase.earth/20260511/data/supply-chains/brazil_soy_v2_6_1_composite.zip` (~30 MB). Já baixado em `data/raw/trase/brazil_soy/`. |
| CNPJ Receita Federal | Cadastro nacional de estabelecimentos com `data_abertura`, `data_situacao_cadastral`, CNAE primário. Permite reconstruir contagem anual de frigoríficos/silos por município. | `dadosabertos.rfb.gov.br/CNPJ/` — snapshots mensais ~5 GB cada. CNAEs relevantes: 1011-2 (abate bovinos), 1012-1 (aves/suínos), 1013-9 (carnes preparadas), 5211-7 (armazéns). |
| **IPEA Data — drivers macro (Pipeline #37)** | Séries macroeconômicas exógenas para o "drive comum": preços internacionais de commodity (USD), câmbio real efetivo, câmbio nominal, crédito rural estadual. Já coletadas em `data/processed/drivers_macro_anual.csv`. | API OData4 `www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='<code>')`. Códigos: `IFS12_SOJAGP12` / `IFS12_BEEFB12` / `IFS12_MAIZE12` (preços IMF IFS, mensais); `GAC12_TCERXTINPC12` (REER INPC-exportações, 1980–2024); `BM_ERV` (câmbio nominal anual); `CREATE` (fluxo de crédito rural por UF, R$ 2010 — filtrar TERCODIGO=52 p/ Goiás). |

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