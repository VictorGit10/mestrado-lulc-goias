/* sankey.js — Diagrama de Sankey 1985->2024 para a secao Sintese.
 * Carregamento lazy: so baixa D3 + d3-sankey + sankey_data.json quando
 * a secao #sankey-container entra na viewport (IntersectionObserver).
 */

(function (root) {
  "use strict";

  const G = root.GO40 || {};
  let loaded = false;
  let cachedData = null;

  // Modos do Mosaico: 'full' (exibir normal), 'faded' (esmaecer marcha), 'hidden' (ocultar/filtrar)
  let currentMode = root.GO40 && root.GO40.sankeyMode ? root.GO40.sankeyMode : "faded";

  // Os rotulos de sankey_data.json vem sem acento (gerados por script Python
  // com saida ASCII). Reacentuar aqui, e nao no dado, mantem os ids estaveis.
  const ACENTOS = {
    "Vegetacao Natural": "Vegetação Natural",
    "Area Urbana": "Área Urbana",
    "Agua": "Água"
  };
  function acentuar(texto) {
    if (!texto) return texto;
    // Separa "Classe (ano)" para reacentuar so a classe.
    const m = /^(.*?)(\s\(\d{4}\))?$/.exec(texto);
    const classe = m[1];
    return (ACENTOS[classe] || classe) + (m[2] || "");
  }

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

  // -------------------- controles de interface --------------------
  function renderControls(container) {
    if (!container || !container.parentElement) return;
    let ctrl = container.parentElement.querySelector(".sankey-controls");
    if (!ctrl) {
      ctrl = document.createElement("div");
      ctrl.className = "sankey-controls";
      container.parentElement.insertBefore(ctrl, container);
    }

    ctrl.innerHTML = `
      <span class="sankey-controls-label">Mosaico de Usos:</span>
      <div class="sankey-controls-group" role="radiogroup" aria-label="Modo de exibição do Mosaico de Usos">
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'full' ? 'active' : ''}" data-mode="full">Exibir normal</button>
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'faded' ? 'active' : ''}" data-mode="faded">Esmaecer (Marcha)</button>
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'hidden' ? 'active' : ''}" data-mode="hidden">Ocultar (Filtrar)</button>
      </div>
    `;

    ctrl.querySelectorAll(".sankey-ctrl-btn").forEach(btn => {
      btn.onclick = (e) => {
        const mode = e.currentTarget.dataset.mode;
        if (mode) setMode(mode);
      };
    });
  }

  function setMode(mode) {
    if (currentMode === mode && root.GO40 && root.GO40.sankeyMode === mode) return;
    currentMode = mode;
    root.GO40 = root.GO40 || {};
    root.GO40.sankeyMode = mode;

    if (cachedData) {
      renderizar(cachedData);
    }
    if (root.GO40.miniSankey && typeof root.GO40.miniSankey.setMode === "function") {
      root.GO40.miniSankey.setMode(mode);
    }
  }

  // -------------------- renderizar Sankey --------------------
  function renderizar(data) {
    cachedData = data;
    const container = document.getElementById("sankey-container");
    if (!container) return;

    renderControls(container);

    // Limpar SVG e mensagens anteriores
    container.innerHTML = "";

    const isHidden = currentMode === "hidden";
    const isFaded = currentMode === "faded";
    const ehMosaicoId = id => /Mosaico/.test(id);

    // Filtrar dados caso o mosaico esteja oculto
    let nodesToUse = data.nodes;
    let linksToUse = data.links;

    if (isHidden) {
      nodesToUse = data.nodes.filter(n => !ehMosaicoId(n.id));
      linksToUse = data.links.filter(l => !ehMosaicoId(l.source) && !ehMosaicoId(l.target));
    }

    const containerWidth = container.clientWidth || 800;
    const width = Math.min(containerWidth, 900);
    const height = 480;

    // Mapear IDs para indices
    const nodeById = {};
    nodesToUse.forEach((n, i) => { nodeById[n.id] = i; });

    // Construir links com indices numericos
    const links = linksToUse.map(l => ({
      source: nodeById[l.source],
      target: nodeById[l.target],
      value: l.value,
      color: l.color
    }));

    const nodes = nodesToUse.map(n => ({
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
      .attr("aria-label", "Diagrama de Sankey: transições de uso da terra 1985-2024")
      .style("max-width", "100%")
      .style("height", "auto");

    const tocaMosaico = d => {
      const srcNode = graph.nodes[d.source.index];
      const tgtNode = graph.nodes[d.target.index];
      return (srcNode && ehMosaicoId(srcNode.id)) || (tgtNode && ehMosaicoId(tgtNode.id));
    };

    // Links
    svg.append("g")
      .attr("fill", "none")
      .selectAll("path")
      .data(graph.links)
      .join("path")
      .attr("d", d3.sankeyLinkHorizontal())
      .attr("stroke", d => d.color || "#999")
      .attr("stroke-opacity", d => isFaded ? (tocaMosaico(d) ? 0.06 : 0.5) : 0.4)
      .attr("stroke-width", d => Math.max(1, d.width))
      .append("title")
      .text(d => {
        const src = graph.nodes[d.source.index];
        const tgt = graph.nodes[d.target.index];
        return `${acentuar(src.label || src.id)} → ${acentuar(tgt.label || tgt.id)}: ${d.value.toFixed(2)} Mha`;
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
      .attr("fill-opacity", d => isFaded && ehMosaicoId(d.id) ? 0.18 : 1)
      .attr("stroke", "#1a1a1a")
      .attr("stroke-opacity", d => isFaded && ehMosaicoId(d.id) ? 0.25 : 1)
      .attr("stroke-width", 0.5);

    // Labels dos nodes
    nodeGroup.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .attr("fill", "#1a1a1a")
      .attr("opacity", d => isFaded && ehMosaicoId(d.id) ? 0.4 : 1)
      .attr("font-size", "11px")
      .attr("font-family", "var(--font-sans)")
      .text(d => {
        return (d.label || d.id)
          .replace("Vegetacao Natural", "Veg. natural")
          .replace("Area Urbana", "Urbano")
          .replace("Mosaico de Usos", "Mosaico")
          .replace("Agua", "Água");
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
  root.GO40.sankey = { init, renderizar, setMode };

  init();

})(typeof window !== "undefined" ? window : this);