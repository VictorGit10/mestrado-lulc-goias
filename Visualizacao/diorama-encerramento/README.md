# Diorama de Goiás para o encerramento

## Arquivos

- `cena.html`: **a versão em uso**. Página própria num palco de 1920 × 1080, embutida no
  slide de encerramento de `../apresentacao.html` e também abrível sozinha (toca em loop;
  Espaço pausa). Parâmetros: `?embutido` (espera a apresentação chamar
  `window.diorama.tocar()`), `?estatico` (um quadro só, para captura/PDF).
- `diorama.html`: fragmento original gerado por outra IA (fonte da cena, mantido como
  referência). Editar a `cena.html`, não este.
- `index.html`: pré-visualização do ambiente onde o fragmento foi gerado; não funciona
  fora dele (abre em branco). Não é publicada.

## Como entra na apresentação

`assets/js/apresentacao-diorama.js` controla o iframe do slide `.s-diorama`:

| slide ativo | o que acontece |
|---|---|
| fecho (o anterior) | carrega a cena 1,5 s depois de chegar, pausada |
| encerramento | carrega (se ainda não carregou) e toca |
| qualquer outro | descarrega (`about:blank` libera o contexto WebGL) |

Pausada, a cena não tem `requestAnimationFrame` nenhum. O iframe tem
`pointer-events: none` e `tabindex="-1"`: nunca pega o foco, então as setas continuam
com a apresentação. O "Obrigado." saiu do fecho e ficou só aqui.

## Desempenho (medido numa Intel UHD, 23/set/2026)

- Em 1920 × 1080 a 1 px por px do palco, ~11% dos quadros atrasavam; em 0,85, 2%; em 0,7,
  nenhum. O gargalo é preencher pixels. A cena desce sozinha em degraus
  (1 → 0,85 → 0,7 → sombra em 1024 px) quando mais de 8% dos quadros passam de 25 ms.
- Compilar os shaders no primeiro quadro travava a página por ~1,2 s; agora é
  `renderer.compileAsync` (em paralelo), e a montagem cai no fecho, numa pausa de fala.

## Offline

Tudo é local: `../assets/js/vendor/three.min.js` (Three.js 0.158.0, baixado do jsDelivr
em 23/set/2026) e `d3.v7.min.js`; a fonte é a mesma pilha dos slides, sem Google Fonts. O
jsDelivr só entra como reserva se o arquivo local sumir.

O contorno vem dos dados do projeto. Árvores, relevo, lavouras, gado, construções e nuvens
são paisagem ilustrativa, sem posição nem quantidade medidas; o rodapé do slide diz isso.
