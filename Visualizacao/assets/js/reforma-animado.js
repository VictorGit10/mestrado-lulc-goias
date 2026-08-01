/* reforma-animado.js — Controlador do Laboratório de Animações Numeradas.
 *
 * Observação de arquitetura: as animações de revelação por scroll (#2 Entrada
 * Suave e #6 Título Revelado) vivem em reforma-hero.js, que é compartilhado por
 * reforma.html e reforma-animado.html e dispara de forma síncrona. Este arquivo
 * NÃO duplica esses observadores — cuida apenas das animações exclusivas do
 * laboratório: #1 (count-up), #4 (shimmer/revelação de imagens) e #5 (barras).
 */
(function (root) {
  "use strict";

  // -------------------------------------------------------------------------
  // [ANIMAÇÃO #1] — CONTADOR NUMÉRICO PROGRESSIVO (COUNT-UP)
  // -------------------------------------------------------------------------
  function initCountUp() {
    const els = document.querySelectorAll(".count-up-val");
    if (!els.length) return;
    // Sem IntersectionObserver: deixa o valor estático do HTML (fallback correto).
    if (!("IntersectionObserver" in root)) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        if (el.dataset.counted === "true") return;
        el.dataset.counted = "true";
        observer.unobserve(el);

        const target = parseInt(el.dataset.targetValue, 10);
        const prefix = el.dataset.prefix || "";
        const suffix = el.dataset.suffix || "";
        const duration = parseInt(el.dataset.duration || "1400", 10);

        // Começa em 0 só no instante em que a animação efetivamente dispara,
        // para evitar um flash "valor final → 0 → valor final" antes do scroll.
        el.textContent = `${prefix}${(0).toLocaleString("pt-BR")}${suffix}`;

        let startTimestamp = null;
        const step = (timestamp) => {
          if (!startTimestamp) startTimestamp = timestamp;
          const progress = Math.min((timestamp - startTimestamp) / duration, 1);
          // ease-out suave para os números grandes não "travarem" no fim
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = Math.floor(eased * target);
          el.textContent = `${prefix}${current.toLocaleString("pt-BR")}${suffix}`;
          if (progress < 1) {
            window.requestAnimationFrame(step);
          } else {
            el.textContent = `${prefix}${target.toLocaleString("pt-BR")}${suffix}`;
          }
        };
        window.requestAnimationFrame(step);
      });
    }, { threshold: 0.2 });

    els.forEach(el => observer.observe(el));
  }

  // -------------------------------------------------------------------------
  // [ANIMAÇÃO #4] — SHIMMER & REVELAÇÃO DE IMAGENS DE MAPAS/FIGURES
  // -------------------------------------------------------------------------
  // Alvos:
  //   • .map-image-container (marcados à mão no HTML, com sweep completo)
  //   • .grafico-card img   (figures estáticos — revelação segura por scale/brightness)
  // Não toca no #mapa (sticky scrollama) para não interferir na sincronização.
  function initMapShimmer() {
    const manualContainers = Array.from(document.querySelectorAll(".map-image-container"));
    const figureImgs = Array.from(document.querySelectorAll(".grafico-card img"));

    figureImgs.forEach(img => img.classList.add("map-image-animated"));

    if (!("IntersectionObserver" in root)) {
      figureImgs.forEach(img => img.classList.add("is-loaded-map"));
      manualContainers.forEach(c => {
        const sweep = c.querySelector(".map-shimmer-sweep");
        if (sweep) sweep.classList.add("is-sweeping");
      });
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const container = entry.target;
        const img = container.querySelector("img");
        const sweep = container.querySelector(".map-shimmer-sweep");
        if (img) img.classList.add("is-loaded-map");
        if (sweep && !sweep.classList.contains("is-sweeping")) sweep.classList.add("is-sweeping");
        observer.unobserve(container);
      });
    }, { threshold: 0.15 });

    manualContainers.forEach(el => observer.observe(el));

    // Observa cada figure uma única vez (o container é o próprio .grafico-card).
    const seen = new Set();
    figureImgs.forEach(img => {
      const container = img.closest(".map-image-container") || img.parentElement;
      if (container && !seen.has(container)) {
        seen.add(container);
        observer.observe(container);
      }
    });
  }

  // -------------------------------------------------------------------------
  // [ANIMAÇÃO #5] — BARRAS DE DADOS ANIMADAS
  // -------------------------------------------------------------------------
  // Alvos:
  //   • .data-bar-animated (largura-alvo vem de data-target-width; CSS já parte de 0)
  //   • .churn-bar         (largura-alvo vem da custom property --w; JS parte de 0,
  //                         preservando o fallback sem-JS que usa width: var(--w))
  function initDataBars() {
    const bars = document.querySelectorAll(".data-bar-animated, .churn-bar");
    if (!bars.length) return;

    bars.forEach(bar => {
      if (bar.classList.contains("churn-bar")) {
        const w = (getComputedStyle(bar).getPropertyValue("--w") || "").trim() || "100%";
        bar.dataset.targetWidth = w;
        bar.style.width = "0%";
        bar.style.transition = "width 1.1s cubic-bezier(0.16, 1, 0.3, 1)";
      } else if (!bar.dataset.targetWidth) {
        bar.dataset.targetWidth = "100%";
      }
    });

    if (!("IntersectionObserver" in root)) {
      bars.forEach(bar => { bar.style.width = bar.dataset.targetWidth; });
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const bar = entry.target;
        bar.style.width = bar.dataset.targetWidth;
        observer.unobserve(bar);
      });
    }, { threshold: 0.3 });

    bars.forEach(el => observer.observe(el));
  }

  // Initializer global
  function initLabAnimations() {
    initCountUp();
    initMapShimmer();
    initDataBars();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLabAnimations);
  } else {
    initLabAnimations();
  }
})(typeof window !== "undefined" ? window : this);