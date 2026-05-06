# Decisões metodológicas — SICOR/BACEN

Restrições de escopo aceitas para a coleta de crédito rural via SICOR. Tudo aqui é **escolha consciente**, não omissão acidental — caso a análise futura mostre que algum item é necessário, basta voltar e estender o coletor.

Pipeline relacionado: [#6](../pipelines/06_sicor.md).

## Sondagem da API (registrada para evitar retrabalho)

**Data**: 2026-04-27.

- **API**: `https://olinda.bcb.gov.br/olinda/servico/SICOR/versao/v2/odata/`
- **Datasets úteis**:
  - `CusteioMunicipioProduto`, `InvestMunicipioProduto` — granularidade município. Investimento traz só `cdMunicipio` BACEN, não `codIbge`.
  - `CusteioRegiaoUFProduto`, `InvestRegiaoUFProduto`, `ComercRegiaoUFProduto` — agregado UF.
- **Idiossincrasias do Olinda**:
  - `$filter eq` funciona **somente com `%20`** entre tokens (não `+`).
  - `$skip`, `$count`, `$orderby`, `$apply` retornam erro ou são ignorados.
  - `$top` aceita até pelo menos 100.000.
- **Códigos confirmados**:
  - `cdEstado` BACEN para Goiás = `'10'`.
  - `nomeUF` nos datasets agregados = sigla `'GO'` (não 'GOIÁS').
- **Range disponível em TODOS os datasets**: `AnoEmissao` de **2013 a 2026** (operações registradas inclusive com vencimento futuro). **Não há série pré-2013** nesta API — nem município, nem UF.

## Escopo decidido

- **Painel municipal**: período **2013 a 2026** (cobertura efetiva do SICOR; 2026 será parcial — sinalizado na análise).
- **Painel UF agregado**: mesmo período **2013 a 2026** (a ideia inicial de cobrir 2003+ foi **abandonada** ao constatar que o OData só inicia em 2013).
- **Recorte de operações**: **todas as finalidades** (Custeio + Investimento + Comercialização). Industrialização não tem entidade própria no OData — fica fora.
- **Granularidade salva**:
  - Municipal: `(ano, cd_mun_IBGE, finalidade, programa, subprograma, fonte_recurso, atividade, modalidade, produto)` → valor contratado (R$), área (ha) quando aplicável.
  - UF: `(ano, sigla_uf, finalidade, programa, …)` → valor + nº de contratos (`QtdCusteio`/`QtdInvest`/`QtdComerc`).

## O que estamos abrindo mão

| Item | Razão |
|---|---|
| **Crédito rural antes de 2013** (qualquer granularidade) | API OData só consolida pós-2013. Anuários do Crédito Rural (BACEN/MCR) anteriores publicam agregados Brasil/região em PDFs sem padrão. Cobrir o buraco exigiria scraping específico — custo alto, payoff baixo (o ciclo recente de soja em GO se acelerou justamente após 2013). |
| **Microdados operação-a-operação** (`bcb.gov.br/.../micrrural`) | Agregado por município/finalidade/programa basta para correlação com LULC. Microdados servem para análise de tomador (perfil de produtor), fora do escopo. |
| **Industrialização** (4ª finalidade do MCR) | OData do SICOR não expõe entidade dedicada para isso, e o volume é marginal no estado. |
| **Subsídio implícito** (custo de equalização Tesouro-BACEN) | Publicado só em nível Brasil — não dá para municipalizar. |
| **Deflação na coleta** | Salvamos valores nominais; deflação para R$ dez/2024 aplicada no momento da análise (usando IPCA já em `sidra_1737_ipca.csv`). Mantém o coletor desacoplado da escolha de deflator. Ver [deflacao_ipca.md](deflacao_ipca.md). |
| **Resolução temporal mensal** | SICOR traz `MesEmissao`, mas para correlação com LULC anual o mês é granular demais. Salvamos mês no painel mas trabalhamos com soma anual no painel agregado. |

## Estratégia de paginação

(consequência das limitações do Olinda):

Como `$skip`/`$count` não funcionam, a coleta é segmentada por (`AnoEmissao`, `cdEstado`/`nomeUF`) — uma chamada por ano. Volumes Goiás por ano: ~15–20k registros em Custeio, ~10–17k em Investimento — bem dentro do `$top=50000`.
