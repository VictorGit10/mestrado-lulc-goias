/* ==========================================================================
   Apresentação — o diorama de encerramento (slide .s-diorama).

   O diorama (diorama-encerramento/cena.html) é uma cena WebGL. Para que ela
   não pese no resto da apresentação, o iframe só existe perto do fim:

     fecho ativo      → carrega depois de 1,5 s (a rolagem já terminou e a
                        montagem, ~0,3 s de thread principal, cai numa pausa
                        de fala, não numa transição)
     diorama ativo    → carrega já, se ainda não carregou, e toca
     qualquer outro   → descarrega (about:blank libera o contexto WebGL)

   Fora do slide ativo a cena não desenha nada: pausar() cancela o
   requestAnimationFrame. A resolução segue a escala real do palco na tela.
   ========================================================================== */
(() => {
  "use strict";
  const slide = document.querySelector(".s-diorama");
  if (!slide) return;
  const quadro = slide.querySelector("iframe.diorama");
  const fecho = slide.previousElementSibling;
  const stage = document.querySelector(".stage");
  const src = "diorama-encerramento/cena.html?v=3&embutido" +
    (document.body.classList.contains("estatico") ? "&estatico" : "");
  let carregado = false, tPre = 0;

  const api = () => { try { return carregado ? quadro.contentWindow.diorama : null; } catch (_) { return null; } };
  function escala() { const a = api(); if (a) a.escala(stage.getBoundingClientRect().width / 1920); }

  function carregar() { if (!carregado) { carregado = true; quadro.src = src; } }
  function descarregar() { if (carregado) { carregado = false; quadro.src = "about:blank"; } }

  function estado() {
    const aqui = slide.classList.contains("ativo");
    const antes = !!fecho && fecho.classList.contains("ativo");
    clearTimeout(tPre);
    if (aqui) carregar();
    else if (antes) { if (!carregado) tPre = setTimeout(carregar, 1500); }
    else descarregar();
    const a = api();
    if (a) { if (aqui) a.tocar(); else a.pausar(); }
  }

  quadro.addEventListener("load", () => { if (api()) { escala(); estado(); } });
  const obs = new MutationObserver(estado);
  obs.observe(slide, { attributes: true, attributeFilter: ["class"] });
  if (fecho) obs.observe(fecho, { attributes: true, attributeFilter: ["class"] });
  addEventListener("resize", escala);
  estado();
})();
