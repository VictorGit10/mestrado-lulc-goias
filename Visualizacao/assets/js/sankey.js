/* sankey.js — Diagrama de Sankey 1985->2024 para a secao Sintese.
 * Carregamento lazy: so baixa D3 + d3-sankey + sankey_data.json quando
 * a secao #sankey-container entra na viewport (IntersectionObserver).
 */

(function (root) {
  "use strict";

  const G = root.GO40 || {};
  let loaded = false;

  // -------------------- carregar vendors --------------------
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error("Falha ao carregar: " + src));
      document.head.appendChild(s);
    });
  }

  async function loadVendors() {
    if (root.d3 && root.d3.sankey) return; // ja carregado
    await loadScript("assets/js/vendor/d3.v7.min.js?v=2");
    await loadScript("assets/js/vendor/d3-sankey.min.js?v=2");
  }

  // -------------------- renderizar Sankey --------------------
  function renderizar(data) {
    const container = document.getElementById("sankey-container");
    if (!container) return;

    // Limpar placeholder
    container.innerHTML = "";

    const containerWidth = container.clientWidth || 800;
    const width = Math.min(containerWidth, 900);
    const height = 480;

    // Mapear IDs para indices
    const nodeById = {};
    data.nodes.forEach((n, i) => { nodeById[n.id] = i; });

    // Construir links com indices numericos
    const links = data.links.map(l => ({
      source: nodeById[l.source],
      target: nodeById[l.target],
      value: l.value,
      color: l.color
    }));

    const nodes = data.nodes.map(n => ({
      ...n,
      nodeId: nodeById[n.id]
    }));

    // Layout Sankey
    const sankey = d3.sankey()
      .nodeId(d => d.nodeId)
      .nodeWidth(16)
      .nodePadding(12)
      .extent([[1, 5], [width - 1, height - 5]]);

    const graph = sankey({
      nodes: nodes.map(d => ({...d})),
      links: links.map(d => ({...d}))
    });

    // SVG
    const svg = d3.select(container)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("role", "img")
      .attr("aria-label", "Diagrama de Sankey: transicoes de uso da terra 1985-2024")
      .style("max-width", "100%")
      .style("height", "auto");

    // Links
    svg.append("g")
      .attr("fill", "none")
      .selectAll("path")
      .data(graph.links)
      .join("path")
      .attr("d", d3.sankeyLinkHorizontal())
      .attr("stroke", d => d.color || "#999")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", d => Math.max(1, d.width))
      .append("title")
      .text(d => {
        const src = data.nodes[d.source.index];
        const tgt = data.nodes[d.target.index];
        return `${src.label} → ${tgt.label}: ${d.value.toFixed(2)} Mha`;
      });

    // Nodes
    const nodeGroup = svg.append("g")
      .selectAll("g")
      .data(graph.nodes)
      .join("g");

    nodeGroup.append("rect")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => Math.max(1, d.y1 - d.y0))
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => d.color)
      .attr("stroke", "#1a1a1a")
      .attr("stroke-width", 0.5);

    // Labels dos nodes
    nodeGroup.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .attr("fill", "#1a1a1a")
      .attr("font-size", "11px")
      .attr("font-family", "var(--font-sans)")
      .text(d => {
        const nome = d.label
          .replace("Vegetacao Natural", "Veg. natural")
          .replace("Agricultura", "Agricultura")
          .replace("Pastagem", "Pastagem")
          .replace("Area Urbana", "Urbano")
          .replace("Outros", "Outros")
          .replace("Agua", "Agua");
        return nome;
      });

    loaded = true;
  }

  // -------------------- lazy load --------------------
  function initLazyLoad() {
    const container = document.getElementById("sankey-container");
    if (!container) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !loaded) {
          observer.disconnect();
          carregarERenderizar();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(container);
  }

  async function carregarERenderizar() {
    const container = document.getElementById("sankey-container");
    if (!container) return;
    try {
      await loadVendors();
      const resp = await fetch("assets/data/sankey_data.json");
      if (!resp.ok) throw new Error("sankey_data.json: " + resp.status);
      const data = await resp.json();
      renderizar(data);
    } catch (err) {
      console.error("[sankey] Erro:", err);
      if (container) {
        container.innerHTML = `<p style="color:#8b3a1d">Falha ao carregar diagrama: ${err.message}</p>`;
      }
    }
  }

  // -------------------- bootstrap --------------------
  function init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", initLazyLoad);
    } else {
      initLazyLoad();
    }
  }

  root.GO40 = root.GO40 || {};
  root.GO40.sankey = { init, renderizar };

  init();

})(typeof window !== "undefined" ? window : this);