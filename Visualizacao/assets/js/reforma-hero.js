/* reforma-hero.js — Marca d'água cartográfica animada para o Hero do reforma.html.
 * Carrega a malha de mesorregiões (malha_mesorregiao.geojson) via D3 e traça
 * as linhas do mapa de Goiás em sequência contínua do Sul para o Norte.
 */
(function (root) {
  "use strict";

  async function loadD3() {
    if (root.d3) return root.d3;
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = "assets/js/vendor/d3.v7.min.js?v=2";
      s.onload = () => resolve(root.d3);
      s.onerror = () => reject(new Error("Falha ao carregar D3.js"));
      document.head.appendChild(s);
    });
  }

  async function initHeroWatermark() {
    const heroSection = document.getElementById("p0-hero");
    if (!heroSection) return;

    // Criar container SVG da marca d'água
    let svgEl = heroSection.querySelector(".hero-bg-watermark-continuous");
    if (!svgEl) {
      svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svgEl.setAttribute("class", "hero-bg-watermark-continuous");
      svgEl.setAttribute("viewBox", "0 0 320 380");
      svgEl.setAttribute("aria-hidden", "true");
      heroSection.insertBefore(svgEl, heroSection.firstChild);
    }

    try {
      const d3 = await loadD3();
      const resp = await fetch("assets/data/malha_mesorregiao.geojson");
      if (!resp.ok) return;
      const geojson = await resp.json();

      const svg = d3.select(svgEl);
      svg.selectAll("*").remove();

      const projection = d3.geoMercator().fitExtent([[15, 15], [300, 365]], geojson);
      const pathGen = d3.geoPath().projection(projection);

      // Ordenar mesorregiões do Sul para o Norte (Sul -> Centro/Leste -> Noroeste -> Norte)
      const sortedFeatures = geojson.features.slice().sort((a, b) => {
        const centA = pathGen.centroid(a);
        const centB = pathGen.centroid(b);
        return centB[1] - centA[1]; // Maior Y (Sul) vem primeiro
      });

      // Linhas base fixas (suaves)
      const gBase = svg.append("g").attr("class", "map-base-group");
      gBase.selectAll("path")
        .data(sortedFeatures)
        .enter()
        .append("path")
        .attr("class", "base-map-line")
        .attr("d", pathGen);

      // Linhas animadas que se formam do Sul para o Norte em loop
      const gAnim = svg.append("g").attr("class", "map-anim-group");

      sortedFeatures.forEach((feat, index) => {
        const pathNode = gAnim.append("path")
          .datum(feat)
          .attr("class", "animated-drawing-line")
          .attr("d", pathGen)
          .node();

        if (pathNode) {
          const length = pathNode.getTotalLength();
          pathNode.style.strokeDasharray = `${length} ${length}`;
          pathNode.style.strokeDashoffset = length;
          pathNode.style.setProperty("--path-len", `${length}px`);

          // Escalonar inicio do desenho por região (Sul primeiro, Norte por último)
          const staggerDelay = index * 0.6;
          pathNode.style.animationDelay = `${staggerDelay}s`;
        }
      });

    } catch (err) {
      console.warn("[reforma-hero] Aviso:", err.message);
    }
  }

  function initScrollObservers() {
    // Sem IntersectionObserver: revela tudo imediatamente (fallback robusto).
    if (!("IntersectionObserver" in root)) {
      document.querySelectorAll(".scroll-reveal").forEach(el => el.classList.add("is-visible"));
      document.querySelectorAll(".parte-titulo").forEach(el => el.classList.add("is-revealed"));
      return;
    }

    // Animação #2: Entrada Suave nos blocos ao rolar
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".scroll-reveal").forEach(el => revealObserver.observe(el));

    // Animação #6: Revelação Editorial de Títulos (.parte-titulo)
    // Observa .parte-titulo (não .title-reveal-animated) para cobrir todos os
    // títulos, inclusive os que só têm .parte-titulo — ex. a Parte 4.
    const titleObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          titleObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    document.querySelectorAll(".parte-titulo").forEach(el => titleObserver.observe(el));
  }

  // Revelação síncrona na carga (independente do watermark, que é assíncrono):
  // garante que títulos e blocos apareçam na hora certa mesmo se D3/geojson
  // falharem ou demorarem. Roda em ambas as páginas que incluem este script.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      initScrollObservers();
      initHeroWatermark();
    });
  } else {
    initScrollObservers();
    initHeroWatermark();
  }
})(typeof window !== "undefined" ? window : this);
