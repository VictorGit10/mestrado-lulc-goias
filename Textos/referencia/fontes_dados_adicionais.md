# Fontes de dados adicionais

Tabela extraída do `SugestaoClaude.md` original (preservado em [_arquivo/sugestao_claude_inicial.md](../_arquivo/sugestao_claude_inicial.md)).

| Fonte | O que adiciona | Como acessar |
|---|---|---|
| MapBiomas Transições | Matrizes A→B (floresta-1995 → pastagem-2005 → soja-2015) | Asset GEE `mapbiomas_brazil_collection10_1_transition_v1` |
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

## Impacto por eixo

- **Dinâmica de Conversão**: sem matriz de transição, descreve-se estoques mas não trajetórias.
- **Vetores econômicos**: sem SICOR + PAM + frigoríficos, falta o lado causal.
- **Bem-estar**: não foi tocado (IDH-M coletado apenas 1991/2000/2010).