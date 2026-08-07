/* mini-sankey.js — Mini-diagramas de Sankey ao final de cada ATO (I..III).
 * Reutiliza D3 + d3-sankey carregados pelo sankey.js. Render lazy via
 * IntersectionObserver: dispara quando o container do ato entra na viewport.
 */
(function (root) {
  "use strict";

  const ATOS = ["I", "II", "III"];
  const renderizados = new Set();
  const cache = {};

  let currentMode = root.GO40 && root.GO40.sankeyMode ? root.GO40.sankeyMode : "faded";

  // Os rotulos dos JSONs de ato vem sem acento (gerados por script Python com
  // saida ASCII). Reacentuar na exibicao mantem os ids do dado estaveis.
  const ACENTOS = {
    "Vegetacao Natural": "Vegetação Natural",
    "Area Urbana": "Área Urbana",
    "Agua": "Água"
  };
  function acentuar(texto) {
    if (!texto) return texto;
    const m = /^(.*?)(\s\(\d{4}\))?$/.exec(texto);
    const classe = m[1];
    return (ACENTOS[classe] || classe) + (m[2] || "");
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error("Falha ao carregar: " + src));
      document.head.appendChild(s);
    });
  }

  async function ensureVendors() {
    if (root.d3 && root.d3.sankey) return;
    await loadScript("assets/js/vendor/d3.v7.min.js?v=2");
    await loadScript("assets/js/vendor/d3-sankey.min.js?v=2");
  }

  async function carregarAto(ato) {
    if (cache[ato]) return cache[ato];
    const resp = await fetch(`assets/data/sankey_ato_${ato}.json`);
    if (!resp.ok) throw new Error(`sankey_ato_${ato}.json: ${resp.status}`);
    cache[ato] = await resp.json();
    return cache[ato];
  }

  function renderControls(container) {
    if (!container || !container.parentElement) return;
    let ctrl = container.parentElement.querySelector(".sankey-controls");
    if (!ctrl) {
      ctrl = document.createElement("div");
      ctrl.className = "sankey-controls";
      container.parentElement.insertBefore(ctrl, container);
    }

    ctrl.innerHTML = `
      <span class="sankey-controls-label">Mosaico:</span>
      <div class="sankey-controls-group" role="radiogroup" aria-label="Modo de exibição do Mosaico de Usos">
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'full' ? 'active' : ''}" data-mode="full">Normal</button>
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'faded' ? 'active' : ''}" data-mode="faded">Esmaecer</button>
        <button type="button" class="sankey-ctrl-btn ${currentMode === 'hidden' ? 'active' : ''}" data-mode="hidden">Ocultar</button>
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

    ATOS.forEach(ato => {
      const container = document.querySelector(`.mini-sankey-svg[data-ato="${ato}"]`);
      if (container && cache[ato]) {
        renderizar(container, cache[ato]);
      }
    });

    if (root.GO40.sankey && typeof root.GO40.sankey.setMode === "function") {
      root.GO40.sankey.setMode(mode);
    }
  }

  function renderizar(container, data) {
    renderControls(container);
    container.innerHTML = "";

    const isHidden = currentMode === "hidden";
    const isFaded = currentMode === "faded";
    const ehMosaicoId = id => /Mosaico/.test(id);

    let nodesToUse = data.nodes;
    let linksToUse = data.links;

    if (isHidden) {
      nodesToUse = data.nodes.filter(n => !ehMosaicoId(n.id));
      linksToUse = data.links.filter(l => !ehMosaicoId(l.source) && !ehMosaicoId(l.target));
    }

    const containerWidth = container.clientWidth || 720;
    const width = Math.min(containerWidth, 720);
    const height = 280;

    const nodeById = {};
    nodesToUse.forEach((n, i) => { nodeById[n.id] = i; });

    const links = linksToUse.map(l => ({
      source: nodeById[l.source],
      target: nodeById[l.target],
      value: l.value,
      color: l.color,
    }));

    const nodes = nodesToUse.map(n => ({ ...n, nodeId: nodeById[n.id] }));

    const sankey = d3.sankey()
      .nodeId(d => d.nodeId)
      .nodeWidth(12)
      .nodePadding(8)
      .extent([[1, 5], [width - 1, height - 5]]);

    const graph = sankey({
      nodes: nodes.map(d => ({...d})),
      links: links.map(d => ({...d})),
    });

    const svg = d3.select(container)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .style("max-width", "100%")
      .style("height", "auto");

    // Headers
    svg.append("text")
      .attr("x", 6).attr("y", 14)
      .attr("font-family", "var(--font-sans)")
      .attr("font-size", "10px")
      .attr("fill", "#6b6b6b")
      .text(data.ano_ini);
    svg.append("text")
      .attr("x", width - 6).attr("y", 14)
      .attr("text-anchor", "end")
      .attr("font-family", "var(--font-sans)")
      .attr("font-size", "10px")
      .attr("fill", "#6b6b6b")
      .text(data.ano_fim);

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
      .attr("stroke-opacity", d => isFaded ? (tocaMosaico(d) ? 0.06 : 0.4) : 0.4)
      .attr("stroke-width", d => Math.max(1, d.width))
      .append("title")
      .text(d => {
        const src = graph.nodes[d.source.index];
        const tgt = graph.nodes[d.target.index];
        return `${acentuar(src.label || src.id)} → ${acentuar(tgt.label || tgt.id)}: ${d.value.toFixed(3)} Mha`;
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
      .attr("stroke-width", 0.4);

    nodeGroup.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 4 : d.x0 - 4)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .attr("fill", "#1a1a1a")
      .attr("opacity", d => isFaded && ehMosaicoId(d.id) ? 0.4 : 1)
      .attr("font-size", "9px")
      .attr("font-family", "var(--font-sans)")
      .text(d => {
        const raw = d.label || d.id;
        const label = raw.split(" (")[0];
        const map = {
          "Vegetacao Natural": "Veg.",
          "Area Urbana": "Urb.",
          "Mosaico de Usos": "Mosaico",
          "Agua": "Água"
        };
        return map[label] || label;
      });
  }

  async function renderizarSeNecessario(ato) {
    if (renderizados.has(ato)) return;
    const container = document.querySelector(
      `.mini-sankey-svg[data-ato="${ato}"]`);
    if (!container) return;
    try {
      await ensureVendors();
      const data = await carregarAto(ato);
      renderizar(container, data);
      renderizados.add(ato);
    } catch (err) {
      console.error("[mini-sankey] Erro em ATO " + ato + ":", err);
      container.innerHTML =
        `<p style="color:#8b3a1d;font-size:0.85rem">Falha: ${err.message}</p>`;
    }
  }

  let observer = null;

  function init() {
    const containers = document.querySelectorAll(".mini-sankey-svg[data-ato]");
    if (containers.length === 0) return;

    if (observer) observer.disconnect();
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const ato = entry.target.dataset.ato;
          renderizarSeNecessario(ato);
        }
      });
    }, { rootMargin: "0px 0px 200px 0px", threshold: 0.05 });

    containers.forEach(c => observer.observe(c));
  }

  root.GO40 = root.GO40 || {};
  root.GO40.miniSankey = { init, setMode };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(init, 300));
  } else {
    setTimeout(init, 300);
  }
})(typeof window !== "undefined" ? window : this);
