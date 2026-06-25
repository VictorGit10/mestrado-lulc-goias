/* router.js — alternancia entre modo Narrativa e modo Metodos via hash routing.
 * Esquema URL:
 *   #narrativa            → padrao
 *   #narrativa/2010       → scroll-to ano (delegado ao timeline.js)
 *   #narrativa/sec-tese   → scroll-to ancora pos-mapas (delegado ao timeline.js)
 *   #metodos              → aba Metodos
 *   #metodos/{id-secao}   → scroll-to secao da oficina (delegado ao secoes.js)
 *
 * Decoupling: este modulo so muda visibilidade das secoes e atualiza tabs.
 * Os modos publicam handlers em window.GO40.narrativa.* e window.GO40.metodos.*
 * para receber sub-rotas (ano, ancora, etc).
 */

(function (root) {
  "use strict";

  const MODOS = ["narrativa", "metodos"];

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

    // Delegar sub-rota para o modo ativo.
    const ns = (root.GO40 && root.GO40[modo]) || null;
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
    // Click handlers nas tabs.
    document.querySelectorAll(".mode-tab").forEach(tab => {
      tab.addEventListener("click", (ev) => {
        ev.preventDefault();
        ir(tab.dataset.modo);
      });
    });

    root.addEventListener("hashchange", () => aplicarRota(parseHash()));
    aplicarRota(parseHash());
  }

  root.GO40 = root.GO40 || {};
  root.GO40.router = { ir, parseHash, aplicarRota };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
