/* marcha.js — scrollytelling da marcha ao norte (Movimento III).
 *
 * Espelha a mecanica dos mapas: um painel de figura fixo (sticky) a esquerda
 * troca a figura-chave conforme o leitor avanca pelos passos 7-11 do
 * argumento. Cada passo declara sua figura via data-figura / data-figcap.
 * Sem JS (ou em telas estreitas), as figuras inline .figura-chave assumem.
 */
(function (root) {
  "use strict";

  function init() {
    const cont = document.getElementById("marcha-scrolly");
    if (!cont || typeof scrollama === "undefined") return;

    const steps = Array.from(
      cont.querySelectorAll(".marcha-steps > .como-bloco[data-figura]")
    );
    const img = document.getElementById("marcha-figura-img");
    const cap = document.getElementById("marcha-figura-caption");
    const frame = cont.querySelector(".marcha-figura-frame");
    if (steps.length === 0 || !img || !cap || !frame) return;

    // So a partir daqui o CSS pode esconder as figuras inline e aplicar
    // o esmaecimento dos passos inativos.
    cont.classList.add("js-ativo");

    let atual = null;
    function trocar(step) {
      if (step === atual) return;
      atual = step;
      steps.forEach(s => s.classList.toggle("is-active", s === step));

      const src = step.dataset.figura;
      const legenda = step.dataset.figcap || "";
      if (img.getAttribute("src") === src) {
        cap.textContent = legenda;
        return;
      }
      frame.classList.add("is-fading");
      const proxima = new Image();
      proxima.onload = () => {
        img.src = src;
        img.alt = legenda;
        cap.textContent = legenda;
        requestAnimationFrame(() => frame.classList.remove("is-fading"));
      };
      proxima.onerror = () => frame.classList.remove("is-fading");
      proxima.src = src;
    }

    const scroller = scrollama();
    scroller
      .setup({ step: steps, offset: 0.55, progress: false })
      .onStepEnter(({ element }) => trocar(element));

    trocar(steps[0]);

    root.addEventListener("resize", () => scroller.resize());
    // Ao voltar da aba Metodos, o painel reaparece e as medidas mudam.
    root.addEventListener("hashchange", () => setTimeout(() => scroller.resize(), 60));

    // Pre-carrega as demais figuras quando o navegador estiver ocioso.
    const prefetch = () => steps.forEach(s => { (new Image()).src = s.dataset.figura; });
    if ("requestIdleCallback" in root) root.requestIdleCallback(prefetch, { timeout: 4000 });
    else setTimeout(prefetch, 2500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
