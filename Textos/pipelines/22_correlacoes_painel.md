# Pipeline #22 — Correlações painel municipal (2-way FE)

**Script**: `scripts/correlacoes_painel.py`
**Status**: ✅ executado
**Depende de**: #17 (`taxas_lulc_municipal.csv`), #16 (`painel_unificado.parquet`)

## O que faz

Regressão em painel com efeitos fixos de entidade (município) e tempo (ano) para associar mudanças LULC a mudanças socioeconômicas no nível municipal.

**Decisão D8**: `PanelOLS` com `entity_effects + time_effects`, SE clusterizado por município.

**Especificação**: Δlulc_it = α_i + γ_t + β·Δx_it + ε_it

## Janelas

| Janela | Obs típico | Variáveis disponíveis |
|--------|-----------|----------------------|
| 2013–2021 (plena) | ~1.956–2.214 | LULC + pecuária + PIB + SICOR |
| 2002–2023 (estendida) | ~2.444–5.412 | LULC + pecuária + PIB (sem SICOR) |

## Pares testados

| Y (Δ LULC) | X (Δ socioeconômico) | Rótulo |
|------------|---------------------|--------|
| Δ Pastagem | Δ SICOR crédito rural | Crédito rural × pastagem |
| Δ Pastagem | Δ Bovinos | Rebanho × pastagem |
| Δ Pastagem | Δ VA agropecuária | VA agro × pastagem |
| Δ Veg. natural | Δ Fogo veg. nativa | Fogo × vegetação natural |
| Δ Veg. natural | Δ PIB real | PIB × vegetação natural |
| Δ Agricultura | Δ Produção soja | Soja × agricultura |
| Δ Agricultura | Δ SICOR crédito rural | Crédito rural × agricultura |
| Δ Agricultura | Δ VA agropecuária | VA agro × agricultura |

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `outputs/correlacoes/painel_2fe.csv` | Tabela com 16 modelos: β, SE, p, R² within, n_obs |
| `outputs/correlacoes/painel_residuos.csv` | Resíduos para futura análise espacial (Moran's I) |

## Resultados principais

6 de 16 modelos significativos a 5%:

| Y | X | Janela | β | p | R² within | Interpretação |
|---|---|--------|---|---|-----------|---------------|
| Δ Pastagem | Δ SICOR | 2013–2021 | −0,0034 | 0,0000 | 0,049 | Crédito rural associado a retração de pastagem (possível transição para agricultura) |
| Δ Pastagem | Δ SICOR | 2002–2023 | −0,0029 | 0,0000 | 0,030 | Robusto na janela estendida |
| Δ Pastagem | Δ Bovinos | 2002–2023 | ≈0 | 0,0042 | 0,021 | Significativo mas efeito praticamente nulo |
| Δ Pastagem | Δ VA agro | 2013–2021 | −0,0015 | 0,0334 | 0,022 | Crescimento do VA agro associado a retração de pastagem |
| Δ Agricultura | Δ VA agro | 2013–2021 | −0,0035 | 0,0000 | 0,105 | VA cresce sem expansão de área → intensificação |
| Δ Agricultura | Δ VA agro | 2002–2023 | −0,0040 | 0,0000 | 0,047 | Robusto na janela estendida |

**Conclusão**: o sinal negativo Δ Agricultura × Δ VA agro é o achado mais robusto — sugere que o crescimento do valor adicionado agropecuário em Goiás se dá por intensificação (produtividade), não por expansão de área. Os R² within baixos (0–10%) são esperados para modelos bivariados com alta heterogeneidade municipal.

## Robustez — especificação multivariada (2026-05-14)

Para responder à crítica de R² within baixo no univariado, rodamos três modelos multivariados com covariáveis simultâneas (mesma especificação 2FE, cluster por município):

| Y (ΔLULC) | Covariáveis simultâneas | R²w uni (máx) | R²w mv | N |
|---|---|---|---|---|
| Δ Pastagem | Δ SICOR, Δ Bovinos, Δ VA agro, Δ Fogo | 0,049 | 0,072 | 1.956 |
| Δ Veg. natural | Δ Fogo veg.nat., Δ SICOR, Δ VA agro | 0,002 | 0,005 | 1.956 |
| Δ Agricultura | Δ Soja ton, Δ SICOR, Δ VA agro, Δ Bovinos | 0,105 | 0,122 | 1.550 |

Variante sem SICOR (janela estendida 2002–2023, mais N):

| Y | Covariáveis sem SICOR | R²w mv | N |
|---|---|---|---|
| Δ Pastagem | Δ Bovinos, Δ VA agro, Δ Fogo | 0,014 | 4.674 |
| Δ Agricultura | Δ Soja, Δ VA agro, Δ Bovinos | 0,061 | 3.339 |

### β multivariados significativos (p<0,05)

- **Δ Pastagem ~ Δ SICOR**: β=−0,0030, p<0,001 (com VA agro+Bovinos+Fogo no modelo) — **SICOR é o canal dominante de retração de pastagem** — **na janela plena com SICOR (2013–2021), ~8 anos, não nos 40**; VA agro perde significância (p=0,15) quando se controla por SICOR.
- **Δ Agricultura ~ Δ VA agro**: β=−0,0035, p<0,001 (com SICOR, com Soja, com Bovinos); β=−0,0029, p=0,012 sem SICOR (N=3.339) — **achado de intensificação sobrevive a todos os controles**.

### VIFs

Todos ≤ 1,55. Sem multicolinearidade preocupante.

### Implicação

- O R² within do multivariado é 1,5× a 2,4× o do univariado em pastagem e agricultura. Substancial, mas ainda modesto — confirma que **dinâmica intra-municipal** captura a maior parte da variação de Δlulc, com socioeconômicos explicando ~10–15% adicional.
- A **decomposição do canal** muda interpretação: para pastagem, SICOR (não VA agro) é o **canal associado mais forte** — o preditor mais robusto da retração; VA agro perde significância quando se controla por SICOR. Para agricultura, VA agro mantém a posição central — **a intensificação é o resultado consistente da dissertação**. *(Leitura **associativa**, não causal: um painel 2FE com cluster identifica associação condicional, não efeito causal — o crédito pode **responder** ao plano de conversão tanto quanto antecedê-lo. "Canal mais forte" = preditor mais robusto, não "vetor causal".)*

## Robustez — Áreas Mínimas Comparáveis (D11, 2026-06-04)

25% dos 246 municípios surgiram após 1985 (emancipações 1989/1993/1997/2001), o
que injeta saltos territoriais espúrios na variação intra-município — exatamente
a variação que o 2FE usa. Re-rodamos o painel inteiro sobre as **166 AMC**
(Pipeline #25, território constante): `--nivel amc`.

**As conclusões são robustas.** Todos os achados significativos mantêm sinal e
significância; os β ficam sistematicamente um pouco **mais fortes** e o R² within
**maior** — coerente com a remoção do ruído territorial que atenuava as
estimativas municipais.

| Y ~ X | Janela | β municipal | β AMC | R²w mun → AMC |
|---|---|---|---|---|
| Δ Pastagem ~ Δ SICOR | 2013–2021 | −0,0034* | −0,0045* | 0,049 → 0,070 |
| Δ Pastagem ~ Δ SICOR | 2002–2023 | −0,0029* | −0,0040* | 0,030 → 0,045 |
| Δ Pastagem ~ Δ VA agro | 2013–2021 | −0,0015* | −0,0018* | 0,022 → 0,031 |
| Δ Agricultura ~ Δ VA agro | 2013–2021 | −0,0035* | −0,0040* | 0,105 → 0,137 |
| Δ Agricultura ~ Δ VA agro | 2002–2023 | −0,0040* | −0,0047* | 0,047 → 0,068 |

\* p < 0,05. R²w médio dos 16 modelos: 0,021 (municipal) → 0,028 (AMC).

- **Trocas de sinal: 2** — ambas em `Δ Agricultura ~ Δ SICOR`, β≈0 e **não-significativo** nos dois níveis (ruído, sem achado).
- **Trocas de significância: 1** — `Δ Agricultura ~ Δ Soja [2013–2021]` passa de p=0,112 (n.s.) para p=0,044 (sig.), na direção esperada com dados mais limpos.

**Implicação para a redação**: a AMC é a unidade defensável para os resultados
longitudinais (responde à crítica de comparabilidade), e o re-teste **confirma**
que os achados-chave — crédito associado a retração de pastagem e VA agro a intensificação da
agricultura — não eram artefatos da malha municipal.

Saídas AMC: `painel_2fe_amc.csv`, `painel_residuos_amc.csv`,
`painel_multivariada_amc.csv`, e a comparação lado a lado em
`outputs/correlacoes/comparacao_municipal_vs_amc.csv`.

---

## ✅ Ambiguidade do achado-manchete: intensificação × composição — RESOLVIDA (#22B, 27/jul/2026)

> **Levantada em 25/jul, fechada em 27/jul** por [`intensificacao_vs_composicao.py`](../../scripts/intensificacao_vs_composicao.py).
> **Veredito: a leitura (A), intensificação *within*, se sustenta.** O β<0 **não** é artefato de
> composição entre municípios. O texto abaixo preserva o enunciado do problema (que continua
> correto como raciocínio) e o resultado vem na sequência.

O β<0 de `Δ Agricultura ~ Δ VA agro` é robusto (sobrevive a AMC, a multivariado, a VIF e ao termo
espacial do [#49](49_painel_espacial_dinamico.md)) — mas **"robusto" não é "interpretado"**. Duas
histórias substantivamente diferentes produzem exatamente o mesmo sinal negativo, e este pipeline
**não as separa**:

| Leitura | Mecanismo | O que estaria acontecendo |
|---|---|---|
| **(A) Intensificação *within*** | Dentro de um mesmo município, o valor sobe sem que a área cresça | Ganho de produtividade — a leitura que o doc vinha adotando |
| **(B) Composição entre unidades** | A expansão de área acontece **onde a produtividade é baixa**, e o crescimento de valor acontece **onde a área já está travada** | Nenhum município intensificou; a correlação negativa é o retrato de **dois grupos de municípios diferentes** |

**Por que o 2FE não decide sozinho.** O efeito fixo de unidade remove o *nível* de cada município
e o de ano remove o choque comum — mas o β continua sendo uma **média das relações Δárea↔ΔVA dentro
de cada unidade**, ponderada por quem varia mais. Se as unidades de fronteira contribuem
Δárea grande com ΔVA pequeno, e as do núcleo contribuem Δárea≈0 com ΔVA grande, o β agregado é
negativo **sem que nenhuma unidade tenha intensificado**. É a leitura (B), e ela é **coerente com
o resto da dissertação** — é literalmente o "dois Goiáses" ([#32](32_centro_massa.md)/[#33](33_transicoes_regionais.md))
e o vão valor↔área do [#50](50_centro_massa_economico.md).

**Cuidado para não confundir com o R²-within.** A discussão de R² acima (a dinâmica intra-municipal
capta a maior parte da variação de Δlulc) é sobre **decomposição de variância** — quanto do
movimento mora dentro das unidades. Não responde a esta pergunta, que é sobre **de onde vem o sinal
do β**. São coisas distintas e a primeira não licencia a segunda.

### O teste (#22B) — e por que o desenho decisivo não é a subamostra

Duas estratégias, `scripts/intensificacao_vs_composicao.py`, com **regra de decisão
pré-declarada** (D14 — com muitos cortes possíveis, escolher o corte depois de ver o resultado
é garimpo):

- **Subamostras** (o que esta seção propunha): rodar o mesmo modelo dentro de grupos homogêneos —
  região do [#39](39_fronteira_fechando.md) (Sul/Centro/Norte) e tercis do **share agrícola
  baseline** (lido no ano *anterior* à janela, para que o grupo não seja função do desfecho).
- **FE de grupo × ano** — o **decisivo**. Troca γ_t por **γ_gt**: remove a média de *cada grupo em
  cada ano*, que é exatamente o canal por onde (B) opera. Sobra só a variação de um município
  contra os do **seu próprio grupo** naquele ano. Se o β sobrevive a isso, ele é within-grupo.

> **Por que γ_gt e não só o FE de entidade.** O FE de entidade já remove a composição *estática*
> (níveis médios de cada município). O que ele **não** remove é a composição *dinâmica*: se a
> fronteira responde ao choque do ano com área e o núcleo responde com valor, os desvios em torno
> da média anual são positivos em área num grupo e em valor no outro, e a covariância pooled sai
> negativa sem que ninguém tenha intensificado. É esse canal que o γ_gt fecha.

### Resultado: o β não se move

| Especificação | β (2013–21) | β (2002–23) | β AMC (2002–23) |
|---|---|---|---|
| **Pooled** (o #22 como estava) | −0,00349 *** | −0,00405 *** | −0,00466 *** |
| **+ γ_gt por região** | −0,00324 *** (+7,2%) | −0,00387 *** (+4,4%) | −0,00454 *** (+2,4%) |
| **+ γ_gt por tercil de share** | −0,00325 *** (+7,0%) | −0,00348 *** (+14,1%) | −0,00422 *** (+9,5%) |

*(\*\*\* p<0,001; o % é a variação em relação ao pooled. `outputs/correlacoes/intensificacao_composicao{,_amc}.csv`.)*

**O β sobrevive ao teste decisivo em todas as janelas e nas duas malhas**, movendo-se entre
+2,4% e +14,1% — e mantendo p<0,001. Sob a hipótese (B), ele deveria **ir a zero**. Não vai.

Nas subamostras, **os 24 β estimados (2 malhas × 2 janelas × 3 regiões e 3 tercis) são todos
negativos**, sem uma única inversão de sinal. No AMC 2002–23 — a malha recomendada para o
longitudinal (D11) — os **6/6** são também significativos, o que dispara o veredito (A) pela
regra estrita. Os poucos não-significativos estão nos grupos pequenos (Norte, n≈450) e são
perda de poder, não sinal ausente.

**Controle interno: o teste tem poder para rejeitar.** O par `Δ Pastagem ~ Δ VA agro`
(substituição local, M3 do #49) **não** passa: já é fraco no pooled (β=−0,0015, p=0,033 na janela
plena; **ns** na estendida) e perde significância sob γ_gt (p=0,087). Um desenho que aprovasse
tudo não diria nada; este separa.

> **Defeito da regra pré-declarada, encontrado ao rodar e registrado em vez de corrigido em
> silêncio.** A regra exigia `p<0,05` sob γ_gt — o que confunde **o efeito colapsar** (evidência
> de (B)) com **o teste perder poder** (γ_gt queima muitos graus de liberdade). O critério que
> interpreta é a **magnitude**; o p é o que primeiro se degrada. O script reporta as duas leituras
> lado a lado, com a de magnitude marcada como **pós-hoc**. Por isso o par da pastagem acima é
> lido como *fraco/inconclusivo*, e não como prova de composição: o β dele também não colapsa.

### ⚠️ O #22B NÃO revoga a ressalva de medida (D26 / #49)

São **duas ressalvas independentes** sobre o mesmo β, e fechar uma não fecha a outra:

| Pergunta | Quem responde | Estado |
|---|---|---|
| **De onde vem o sinal** — within-município ou composição entre municípios? | **#22B** (esta seção) | ✅ **within** |
| **Qual variável** — o β depende de medir "agricultura ampla" (MapBiomas) ou soja (SIDRA)? | **[#49](49_painel_espacial_dinamico.md)** + [D26](../metodologia/tratamento_deriva_mosaico.md) | ⚠️ **aberta** — a âncora imune dá **sinal oposto** |

O #49 mostrou que a **soja do SIDRA expande** onde o VA agro cresce (extensificação), enquanto a
**agricultura ampla do MapBiomas encolhe** (intensificação) — e que isso **não** é principalmente
a mudança de rótulo (o β sobrevive à truncagem). É **dependência de medida**: os dois fenômenos
coexistem, e o β herda o sinal da variável escolhida.

O #22B testou a estrutura do sinal **dentro da medida MapBiomas**. Ele diz que, medida assim, a
relação é within-unidade e não artefato de agregação. Ele **não** diz que "agricultura ampla" é a
medida certa. Quem escrever a partir daqui precisa carregar as duas coisas: *o sinal é
within-município* **e** *ele é específico à medida de área agrícola ampla*.

### Como escrever agora

Pode-se afirmar **intensificação** — com dois qualificadores, não um. Primeiro, no sentido estrito
de *"o valor cresce sem que a área acompanhe, dentro do mesmo município e comparado aos seus pares
regionais no mesmo ano"* (#22B). Segundo, *na medida de área agrícola ampla — a soja isolada
extensifica* (#49). A formulação neutra (*"onde o VA agro cresce, a área agrícola não acompanha"*)
continua correta e é a mais segura para a manchete; o que mudou é que **não é mais preciso
hedge-ar contra a leitura (B)** — mas continua sendo preciso reportar as duas medidas.

O que ainda **não** se pode afirmar: que a intensificação seja ganho de **produtividade** medido.
O desenho mostra que o sinal é within-unidade, não de onde vem o ganho — separar produtividade de
travamento de fronteira exigiria produtividade medida (rendimento por hectare), não este painel.
E nada aqui muda o estatuto causal: continua sendo FE + associação (D14).

**Uma observação registrada, não interpretada.** O β é sistematicamente **mais forte no tercil de
baixo share agrícola** (AMC 2013–21: T1 = −0,0224 × T3 = −0,0031, ~7×) e a interação
`Δx × share_base` é positiva e significativa no AMC (p=0,008). Lido cru, isso diria que a
"intensificação" é mais intensa na fronteira. **Não reportar assim**: β está em Mha por R$ bi e
municípios de baixo share têm base pequena nos dois lados da razão, então o gradiente pode ser
efeito de escala. Fica como fio, não como achado.

## Como rodar

```bash
pip install linearmodels
python scripts/correlacoes_painel.py                # municipal (246) — default
python scripts/correlacoes_painel.py --nivel amc    # AMC (166) — longitudinal (D11)
```

Requer `linearmodels`. O modo `amc` depende de `painel_amc_goias.parquet` (#25) e
`taxas_lulc_amc.csv` (#17).