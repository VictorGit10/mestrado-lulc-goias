/* zoom.js — lightbox de graficos. Clique em qualquer figura (.grafico-card ou a
 * figura fixa da marcha) abre a imagem em tela cheia, na resolucao natural.
 * Fecha por clique fora, botao × ou Esc. Sem dependencias.
 */
(function (root) {
  "use strict";

  const doc = root.document;
  const SELETOR = ".grafico-card img, .marcha-figura-frame img";

  let overlay = null;
  let focoAnterior = null;

  function legendaDe(img) {
    const fig = img.closest("figure");
    if (fig) {
      const cap = fig.querySelector("figcaption");
      if (cap && cap.textContent.trim()) return cap.textContent.trim();
    }
    const frame = img.closest(".marcha-figura");
    if (frame) {
      const cap = frame.querySelector(".marcha-figura-caption");
      if (cap && cap.textContent.trim()) return cap.textContent.trim();
    }
    return img.alt || "";
  }

  function fechar() {
    if (!overlay) return;
    overlay.remove();
    overlay = null;
    doc.body.style.overflow = "";
    doc.removeEventListener("keydown", aoTeclar);
    if (focoAnterior && typeof focoAnterior.focus === "function") {
      focoAnterior.focus();
    }
    focoAnterior = null;
  }

  function aoTeclar(ev) {
    if (ev.key === "Escape") {
      ev.preventDefault();
      fechar();
    }
  }

  function abrir(img) {
    if (overlay) fechar();
    focoAnterior = doc.activeElement;

    overlay = doc.createElement("div");
    overlay.className = "zoom-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Gráfico ampliado");

    const figura = doc.createElement("figure");
    figura.className = "zoom-figure";

    const grande = doc.createElement("img");
    grande.src = img.currentSrc || img.src;
    grande.alt = img.alt || "";
    figura.appendChild(grande);

    const legenda = legendaDe(img);
    if (legenda) {
      const cap = doc.createElement("figcaption");
      cap.textContent = legenda;
      figura.appendChild(cap);
    }

    const fecharBtn = doc.createElement("button");
    fecharBtn.type = "button";
    fecharBtn.className = "zoom-close";
    fecharBtn.setAttribute("aria-label", "Fechar");
    fecharBtn.textContent = "×";

    overlay.appendChild(figura);
    overlay.appendChild(fecharBtn);
    doc.body.appendChild(overlay);
    doc.body.style.overflow = "hidden";

    // Qualquer clique no overlay (inclusive na imagem) fecha.
    overlay.addEventListener("click", fechar);
    doc.addEventListener("keydown", aoTeclar);

    requestAnimationFrame(() => overlay && overlay.classList.add("is-open"));
    fecharBtn.focus();
  }

  function aoClicar(ev) {
    if (ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) {
      return;
    }
    const img = ev.target.closest("img");
    if (!img || !img.matches(SELETOR)) return;
    ev.preventDefault();
    abrir(img);
  }

  function init() {
    doc.addEventListener("click", aoClicar);
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
