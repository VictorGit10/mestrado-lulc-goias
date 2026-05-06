# Pipeline #3 — Coleta SIDRA municipal

**Script**: `scripts/coleta_sidra.py`
**Quando foi feito**: 2026-04-26.
**Depende de**: nenhum.
**Outputs**: 8 CSVs em `data/processed/sidra_*.csv`. Ver [tabelas_processadas.md](../outputs/tabelas_processadas.md).

## O que faz

Baixa **8 tabelas SIDRA no nível municipal** (246 munis de Goiás) usando paginação automática para respeitar o limite de 50.000 valores/chamada da API SIDRA.

## Tabelas cobertas

| Tabela | Variáveis | Categorias | Anos | Linhas |
|---|---|---|---|---:|
| **PAM 1612** — Lavouras temporárias | 109 área plantada, 216 área colhida, 214 quantidade produzida | 8 culturas (algodão, arroz, cana, feijão, mamona, milho, soja, sorgo) | 1974–2024 | 301k |
| **PAM 1613** — Lavouras permanentes | 2313 área destinada, 216 área colhida, 214 quantidade | 8 culturas (banana, café, coco, goiaba, laranja, limão, manga, tangerina) | 1974–2024 | 297k |
| **PPM 3939** — Efetivo rebanhos | 105 efetivo (cabeças) | 7 espécies (bovino, suíno, bubalino, equino, ovino, caprino, galináceos) | 1974–2024 | 88k |
| **PPM 74** — Produção de leite | quantidade (mil L), valor (mil R$) | – | 1974–2024 | 25k |
| **PPM 94** — Produção de ovos | quantidade (mil dúzias), valor | – | 1974–2024 | 13k |
| **5938** — PIB municipal | 37 PIB, 498 VA total, 543 impostos, 513 VA agro, 517 VA indústria, 6575 VA serviços, 525 VA adm. pública | – | 2002–2023 | 38k |
| **6579** — População residente | 9324 estimativas anuais | – | 2001–2024 | 5k |
| **1737** — IPCA mensal Brasil | 63 variação mensal | – | 1979–2026 | 556 |

## Schema padronizado

(todos os 8 CSVs em `data/processed/sidra_*.csv`):

```
cd_mun         int     Código IBGE 7 dígitos do município
nm_mun         str     Nome do município (sem o sufixo " - GO")
ano            int     Ano de referência
variavel_id    int     Código IBGE da variável (ex: 109 = área plantada)
variavel       str     Nome da variável
unidade        str     Unidade de medida (Hectares, Toneladas, Cabeças, etc.)
categoria_id   int     Código da classificação (ex: 2713 = Soja). Vazio quando não aplicável.
categoria      str     Nome da classificação (ex: "Soja (em grão)")
valor          float   Valor numérico. NaN para "..", "-" ou ausente no SIDRA.
```

## Decisões metodológicas

1. **Variável 215 (valor da produção PAM) omitida**. Razão: a unidade de moeda muda no tempo — Cruzeiros (1974–85), Cruzados (1986–88), Cruzados Novos (1989), Cruzeiros Reais (1993), Reais (1994+). Não dá pra deflacionar via IPCA puro. Se precisar do valor real, dá pra reconstruir a partir de Quantidade × Preço médio anual (PAM tabela auxiliar) em uma fase posterior.

2. **Variável 112 (rendimento médio) omitida**. Razão: redundante — é exatamente Quantidade Produzida (214) ÷ Área Colhida (216). Posso calcular no momento da análise sem perda.

3. **PAM 1613 tem 243 municípios, não 246**. Razão: 3 munis de Goiás nunca tiveram registro de lavoura permanente em nenhum ano da série. Goiás é dominado por temporárias.

4. **PIB municipal vai só até 2023**, não 2024. Razão: o IBGE publica Contas Regionais com defasagem de 2 anos.

5. **Códigos validados contra metadados da API** em 2026-04-26. Os primeiros chutes estavam errados: Soja é 2713 (não 2737); Bovino é 2670 (correto); mas Suíno é 32794 (não 2675 — esse é Bubalino). Sempre conferir via `https://servicodados.ibge.gov.br/api/v3/agregados/<tab>/metadados`.

## Como rodar

```bash
python coleta_sidra.py                  # baixa só o que faltar (usa cache CSV)
python coleta_sidra.py --force          # ignora cache e rebaixa tudo
python coleta_sidra.py --so 1612 5938   # roda só tabelas que casem com essas substrings
```

**Tempo de execução**: ~10 min na primeira execução (38 chunks × ~25s cada). Re-execuções são instantâneas (cache CSV).

## Arquitetura interna

```
_get_sidra_cached(nome, **kwargs)             # 1 chamada SIDRA + cache CSV
        ↓
_quebrar_periodo(ano_ini, ano_fim, ...)       # calcula janelas para caber em 50k valores
        ↓
_get_sidra_paginated(...)                     # várias chamadas, concatena, deduplica header
        ↓
coletar_<tabela>()                            # 1 função por tabela, padroniza schema
        ↓
_padronizar_municipal(df_raw, classif_col)    # bruto → schema canônico
        ↓
data/processed/sidra_<nome>.csv
```
