# Pipeline #55 — A barra de erro do centro de massa sob dependência espacial

**Script**: `scripts/robustez_bootstrap_bloco.py`
**Quando foi feito**: 2026-08-19. Nasceu durante a redação da qualificação, na primeira leitura do texto inteiro *como banca*.
**Depende de**: #32 (centro de massa e o bootstrap da D19), #25 (painel e geometria das AMCs), #49 (o diagnóstico espacial que motiva a pergunta).
**Outputs**:
- `data/processed/centro_massa_bootstrap_bloco.csv` — variável × tamanho de bloco: ΔN, IC95%, veredito, e o mesmo para a componente leste.
- `outputs/centro_massa/` — figura da grade de tamanhos.

---

## Pergunta de pesquisa

A **D19** põe barra de erro em todo deslocamento de centro de massa, e o intervalo vem de
um *bootstrap* que reamostra as 166 AMCs **uma a uma, com reposição**. Isso supõe que as
AMCs são trocáveis e independentes.

O próprio trabalho mostra que não são. O I de Moran dos resíduos é significativo em **125
dos 140 testes** na malha de AMC, e os parâmetros de defasagem e de erro espacial ficam
entre +0,35 e +0,56. Sob dependência espacial o número efetivo de unidades independentes
é menor que 166, e o intervalo sai **estreito demais**. A pergunta é direta: *o veredito
da tabela de centros sobrevive quando a reamostragem respeita a vizinhança?*

Importa porque essa é a tabela mais visível do trabalho, e porque a vegetação natural já
está no fio da navalha (+7,6 km, IC i.i.d. [−0,5; +15,6] — inclui zero por pouco).

## Abordagem

*Bootstrap* de **blocos espaciais**: em vez de sortear AMC a AMC, o estado é particionado
em blocos compactos (k-médias sobre os centroides em EPSG:5880, que os torna compactos sem
impor contiguidade) e sorteiam-se os **blocos inteiros**, com todos os seus vizinhos juntos.

O tamanho do bloco **não é um valor a descobrir**, e sim um parâmetro que se varre: um
bloco de uma AMC reproduz o *bootstrap* original, e blocos grandes dão intervalos mais
conservadores e menos precisos. Reporta-se, como nas demais réguas do projeto, a
**concordância do veredito ao longo da grade**, e não um tamanho eleito.

## Achados

Varrido o bloco de **1 a 14 AMCs** (seis partições: k = 166, 83, 55, 33, 20, 12):

| Variável | ΔN (km) | veredito i.i.d. | veredito em blocos |
|---|---|---|---|
| Pastagem | +77,6 | exclui zero | **exclui zero nas 6** |
| Rebanho bovino | +66,9 | exclui zero | **exclui zero nas 6** |
| Agricultura | +65,2 | exclui zero | **exclui zero nas 6** |
| Vegetação natural | +7,6 | inclui zero | **inclui zero nas 6** |

O intervalo **alarga como esperado** — no caso da pastagem, de **45 para 80 km** de
largura entre o bloco de 1 AMC e o de 14 —, e **o veredito não muda em nenhum tamanho**.

O único ponto em que a régua importa é a **componente leste da agricultura**, que passa a
incluir zero quando os blocos chegam a **oito AMCs**. É a única afirmação da Perna 1 cuja
força depende de tratar as unidades como independentes, e por isso ela é reportada com
essa ressalva.

## Veredito

**A Perna 1 fica mais forte.** O achado que a banca previsivelmente atacaria — "o seu IC
supõe independência que o seu próprio diagnóstico espacial nega" — foi testado e não
derruba nada: a leitura da tabela de centros não depende de tratar as AMCs como
independentes. A vegetação natural continua **ancorada**, e o veredito é invariante em
6 de 6 tamanhos de bloco.

Este pipeline não gera decisão nova: ele **defende a D19** contra a objeção que ela mesma
convida.
