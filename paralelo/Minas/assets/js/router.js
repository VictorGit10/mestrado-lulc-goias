/* router.js — alternancia entre modo Narrativa e modo Atlas via hash routing.
 * Adaptado para MG. Namespace MG40.
 * Sem camada de fogo.
 */
(function (root) {
  "use strict";

  const VARIAVEIS = ["lulc", "transicoes", "delta"];
  const MODOS = ["narrativa", "atlas"];

  function parseHash() {
    const raw = (root.location.hash || "").replace(/^#/, "");
    if (!raw) return { modo: "narrativa", segmentos: [] };
    const partes = raw.split("/").filter(Boolean);
    const modo = MODOS.includes(partes[0]) ? partes[0] : "narrativa";
    return { modo, segmentos: partes.slice(1) };
  }

  function aplicarRota(rota) {
    const { modo, segmentos } = rota;
    document.querySelectorAll("[data-modo]").forEach(sec => {
      const ativo = sec.dataset.modo === modo;
      sec.hidden = !ativo;
      sec.toggleAttribute("aria-current", ativo);
    });
    document.querySelectorAll(".mode-tab").forEach(tab => {
      const ativo = tab.dataset.modo === modo;
      tab.classList.toggle("mode-tab--active", ativo);
      tab.setAttribute("aria-selected", ativo ? "true" : "false");
    });
    document.body.dataset.modoAtivo = modo;

    const ns = (root.MG40 && root.MG40[modo]) || null;
    if (ns && typeof ns.aplicarSubrota === "function") {
      try { ns.aplicarSubrota(segmentos); }
      catch (e) { console.warn(`[router] erro ao aplicar subrota ${modo}/${segmentos.join("/")}`, e); }
    }
  }

  function ir(modo, ...segmentos) {
    const partes = [modo, ...segmentos.filter(s => s != null && s !== "")];
    root.location.hash = "#" + partes.join("/");
  }

  function init() {
    document.querySelectorAll(".mode-tab").forEach(tab => {
      tab.addEventListener("click", (ev) => {
        ev.preventDefault();
        ir(tab.dataset.modo);
      });
    });

    root.addEventListener("hashchange", () => aplicarRota(parseHash()));
    aplicarRota(parseHash());
  }

  root.MG40 = root.MG40 || {};
  root.MG40.router = { ir, parseHash, aplicarRota, VARIAVEIS };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);