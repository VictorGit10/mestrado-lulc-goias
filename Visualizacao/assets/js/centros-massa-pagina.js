/* centros-massa-pagina.js — Módulo interativo do Atlas Completo dos Centros de Massa */

(function (root) {
  "use strict";

  let DADOS = null;
  let GEO = null;
  let anoAtual = 1985;
  let tocando = false;
  let timer = null;
  let activeCategory = "todos";
  let activeVars = new Set(); // conjunto de IDs de variáveis visíveis no mapa

  const W_MAPA = 520, H_MAPA = 480;
  const W_STRIP = 480, H_STRIP = 380;
  const M_STRIP = { t: 20, r: 16, b: 32, l: 42 };

  let proj = null;
  let X = null, Y = null;

  function el(id) { return document.getElementById(id); }

  // --------------------------------------------------------------------------
  // 1. Inicialização & Fetch
  // --------------------------------------------------------------------------
  async function init() {
    try {
      const [dados, geo] = await Promise.all([
        d3.json("assets/data/centros_massa_completo.json"),
        d3.json("assets/data/malha_amc.geojson")
      ]);

      if (!dados || !geo) {
        console.error("[centros-massa] Dados não carregaram adequadamente.");
        return;
      }

      DADOS = dados;
      GEO = geo;

      // Selecionar todas as variáveis inicialmente
      DADOS.variaveis.forEach(v => activeVars.add(v.id));

      montarInterface();
      render();
    } catch (err) {
      console.error("[centros-massa] Erro de inicialização:", err);
    }
  }

  // --------------------------------------------------------------------------
  // 2. Montagem dos Filtros & Controles
  // --------------------------------------------------------------------------
  function montarInterface() {
    renderCategoryPills();
    renderSeriesGrid();
    renderCards();
    ligarEventosControles();
  }

  function renderCategoryPills() {
    const container = el("cm-cat-pills");
    if (!container) return;

    let html = `<button class="cm-cat-pill ${activeCategory === "todos" ? "active" : ""}" data-cat="todos">
      Todos <span class="cm-pill-count">${DADOS.variaveis.length}</span>
    </button>`;

    DADOS.categorias.forEach(cat => {
      const count = DADOS.variaveis.filter(v => v.categoria === cat.id).length;
      html += `<button class="cm-cat-pill ${activeCategory === cat.id ? "active" : ""}" data-cat="${cat.id}">
        ${cat.titulo.split("(")[0]} <span class="cm-pill-count">${count}</span>
      </button>`;
    });

    container.innerHTML = html;

    container.querySelectorAll(".cm-cat-pill").forEach(btn => {
      btn.addEventListener("click", () => {
        const cat = btn.dataset.cat;
        activeCategory = cat;

        // Atualizar conjunto ativo
        activeVars.clear();
        if (cat === "todos") {
          DADOS.variaveis.forEach(v => activeVars.add(v.id));
        } else {
          DADOS.variaveis.filter(v => v.categoria === cat).forEach(v => activeVars.add(v.id));
        }

        renderCategoryPills();
        renderSeriesGrid();
        renderCards();
        render();
      });
    });
  }

  function renderSeriesGrid() {
    const grid = el("cm-series-grid");
    if (!grid) return;

    const list = (activeCategory === "todos")
      ? DADOS.variaveis
      : DADOS.variaveis.filter(v => v.categoria === activeCategory);

    grid.innerHTML = list.map(v => {
      const checked = activeVars.has(v.id) ? "checked" : "";
      const dN = v.liquido.dN != null ? v.liquido.dN : 0;
      const shiftTxt = dN > 0 ? `+${dN} km` : (dN < 0 ? `${dN} km` : `0 km`);
      return `
        <label class="cm-series-item" data-id="${v.id}">
          <input type="checkbox" ${checked} value="${v.id}">
          <span class="cm-swatch" style="background:${v.cor}"></span>
          <span class="cm-series-name">${v.rotulo}</span>
          <span class="cm-series-shift">${shiftTxt}</span>
        </label>
      `;
    }).join("");

    grid.querySelectorAll("input[type='checkbox']").forEach(chk => {
      chk.addEventListener("change", (e) => {
        const id = e.target.value;
        if (e.target.checked) activeVars.add(id);
        else activeVars.delete(id);
        render();
      });
    });
  }

  function ligarEventosControles() {
    const playBtn = el("cm-play-btn");
    if (playBtn) {
      playBtn.addEventListener("click", () => tocando ? parar() : tocar());
    }

    const slider = el("cm-year-slider");
    if (slider) {
      slider.addEventListener("input", (e) => {
        parar();
        anoAtual = +e.target.value;
        render();
      });
    }

    const selectAllBtn = el("cm-btn-select-all");
    if (selectAllBtn) {
      selectAllBtn.addEventListener("click", () => {
        const list = (activeCategory === "todos")
          ? DADOS.variaveis
          : DADOS.variaveis.filter(v => v.categoria === activeCategory);
        list.forEach(v => activeVars.add(v.id));
        renderSeriesGrid();
        render();
      });
    }

    const clearAllBtn = el("cm-btn-clear-all");
    if (clearAllBtn) {
      clearAllBtn.addEventListener("click", () => {
        activeVars.clear();
        renderSeriesGrid();
        render();
      });
    }
  }

  function tocar() {
    if (tocando) return;
    if (anoAtual >= 2024) anoAtual = 1985;
    tocando = true;
    const b = el("cm-play-btn");
    if (b) b.innerHTML = "⏸ Pausar";
    timer = setInterval(() => {
      if (anoAtual >= 2024) { parar(); return; }
      anoAtual += 1;
      render();
    }, 130);
  }

  function parar() {
    tocando = false;
    if (timer) { clearInterval(timer); timer = null; }
    const b = el("cm-play-btn");
    if (b) b.innerHTML = "▶ Reproduzir";
  }

  // --------------------------------------------------------------------------
  // 3. Renderização do Mapa (D3 Mercator)
  // --------------------------------------------------------------------------
  function calcularBBoxAtivas(pad = 0.5) {
    const vars = DADOS.variaveis.filter(v => activeVars.has(v.id));
    if (vars.length === 0) return [[-53.5, -18.5], [-45.5, -12.5]];

    let lon0 = Infinity, lon1 = -Infinity, lat0 = Infinity, lat1 = -Infinity;
    vars.forEach(v => v.pts.forEach(p => {
      lon0 = Math.min(lon0, p.lon); lon1 = Math.max(lon1, p.lon);
      lat0 = Math.min(lat0, p.lat); lat1 = Math.max(lat1, p.lat);
    }));

    const dlon = Math.max(0.4, (lon1 - lon0) * pad);
    const dlat = Math.max(0.4, (lat1 - lat0) * pad);
    return [[lon0 - dlon, lat0 - dlat], [lon1 + dlon, lat1 + dlat]];
  }

  function desenharMapa() {
    const cont = d3.select("#cm-mapa-container");
    cont.selectAll("*").remove();

    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W_MAPA} ${H_MAPA}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    const [sw, ne] = calcularBBoxAtivas(0.5);
    const extent = { type: "MultiPoint", coordinates: [sw, ne] };
    proj = d3.geoMercator().fitExtent([[16, 16], [W_MAPA - 16, H_MAPA - 44]], extent);
    const path = d3.geoPath(proj);

    // clip
    svg.append("clipPath").attr("id", "cm-clip")
      .append("rect").attr("x", 0).attr("y", 0).attr("width", W_MAPA).attr("height", H_MAPA);

    const g = svg.append("g").attr("clip-path", "url(#cm-clip)");

    // Malha municipal AMC
    g.append("g").selectAll("path").data(GEO.features).join("path")
      .attr("d", path)
      .attr("fill", "#f3f1ea")
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 0.5);

    // Trajetórias ativas
    const lineGen = d3.line().curve(d3.curveCatmullRom.alpha(0.5));
    const gVars = g.append("g");

    DADOS.variaveis.filter(v => activeVars.has(v.id)).forEach(v => {
      const gv = gVars.append("g").attr("data-id", v.id);
      const linePts = v.pts.map(p => proj([p.lon, p.lat]));

      // Trilha completa (faint)
      gv.append("path")
        .attr("d", lineGen(linePts))
        .attr("fill", "none")
        .attr("stroke", v.cor)
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "2 3")
        .attr("opacity", 0.35);

      // Trecho percorrido até anoAtual
      const feitos = v.pts.filter(p => p.a <= anoAtual).map(p => proj([p.lon, p.lat]));
      gv.append("path")
        .attr("class", "cm-traj-done")
        .attr("d", feitos.length > 1 ? lineGen(feitos) : null)
        .attr("fill", "none")
        .attr("stroke", v.cor)
        .attr("stroke-width", 2.5)
        .attr("stroke-linecap", "round");

      // Ponto de início (1985)
      const p0 = proj([v.pts[0].lon, v.pts[0].lat]);
      gv.append("circle")
        .attr("cx", p0[0]).attr("cy", p0[1]).attr("r", 3.2)
        .attr("fill", "#ffffff").attr("stroke", v.cor).attr("stroke-width", 1.6);

      // Cabeça (ano atual)
      const pAtual = v.pts.find(pt => pt.a === anoAtual) || v.pts[v.pts.length - 1];
      const hp = proj([pAtual.lon, pAtual.lat]);
      gv.append("circle")
        .attr("class", "cm-head-dot")
        .attr("cx", hp[0]).attr("cy", hp[1]).attr("r", 5.5)
        .attr("fill", v.cor).attr("stroke", "#ffffff").attr("stroke-width", 1.6);
    });

    // Inset e Escala
    desenharLocalizador(svg, sw, ne);
    desenharEscala(svg);
  }

  function desenharLocalizador(svg, sw, ne) {
    const w = 72, h = 84, x0 = W_MAPA - w - 8, y0 = 8;
    const g = svg.append("g").attr("transform", `translate(${x0},${y0})`);
    g.append("rect").attr("width", w).attr("height", h).attr("rx", 3)
      .attr("fill", "#ffffff").attr("stroke", "#e5e3dc").attr("stroke-width", 1);

    const pLoc = d3.geoMercator().fitExtent([[4, 4], [w - 4, h - 4]], GEO);
    g.append("path").attr("d", d3.geoPath(pLoc)(GEO))
      .attr("fill", "#ece9e1").attr("stroke", "#cfccc3").attr("stroke-width", 0.4);

    const tl = pLoc([sw[0], ne[1]]), br = pLoc([ne[0], sw[1]]);
    g.append("rect").attr("x", tl[0]).attr("y", tl[1])
      .attr("width", Math.max(2, br[0] - tl[0]))
      .attr("height", Math.max(2, br[1] - tl[1]))
      .attr("fill", "none").attr("stroke", "#8b3a1d").attr("stroke-width", 1.2);
  }

  function desenharEscala(svg) {
    const cLat = -16.0;
    const km = 50;
    const dLon = km / (111.32 * Math.cos(cLat * Math.PI / 180));
    const cLon = -49.5;
    if (!proj) return;
    const x1 = proj([cLon, cLat])[0], x2 = proj([cLon + dLon, cLat])[0];
    const px = Math.abs(x2 - x1);
    const x0 = W_MAPA - px - 16, y0 = H_MAPA - 14;

    const g = svg.append("g");
    g.append("line").attr("x1", x0).attr("y1", y0).attr("x2", x0 + px).attr("y2", y0)
      .attr("stroke", "#1a1a1a").attr("stroke-width", 1.6);
    g.append("text").attr("x", x0 + px / 2).attr("y", y0 - 4)
      .attr("text-anchor", "middle").style("font-size", "9px").style("font-weight", "600").text("50 km");
  }

  // --------------------------------------------------------------------------
  // 4. Renderização do Gráfico Latitude-Tempo (D3 Strip)
  // --------------------------------------------------------------------------
  function desenharStrip() {
    const cont = d3.select("#cm-strip-container");
    cont.selectAll("*").remove();

    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W_STRIP} ${H_STRIP}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    const activeVarsList = DADOS.variaveis.filter(v => activeVars.has(v.id));

    let lat0 = -18.2, lat1 = -15.0;
    if (activeVarsList.length > 0) {
      lat0 = Infinity; lat1 = -Infinity;
      activeVarsList.forEach(v => v.pts.forEach(p => {
        lat0 = Math.min(lat0, p.lat); lat1 = Math.max(lat1, p.lat);
      }));
      const pad = (lat1 - lat0) * 0.08;
      lat0 -= pad; lat1 += pad;
    }

    X = d3.scaleLinear().domain([1985, 2024]).range([M_STRIP.l, W_STRIP - M_STRIP.r]);
    Y = d3.scaleLinear().domain([lat0, lat1]).range([H_STRIP - M_STRIP.b, M_STRIP.t]);

    // Bandas dos atos
    const gB = svg.append("g");
    (DADOS.atos || []).forEach((a, i) => {
      gB.append("rect")
        .attr("x", X(a.ini)).attr("y", M_STRIP.t)
        .attr("width", X(a.fim) - X(a.ini)).attr("height", (H_STRIP - M_STRIP.b) - M_STRIP.t)
        .attr("fill", i % 2 ? "transparent" : "rgba(0,0,0,0.03)");
      gB.append("text").attr("x", (X(a.ini) + X(a.fim)) / 2).attr("y", M_STRIP.t + 11)
        .attr("text-anchor", "middle").style("font-size", "9px").style("fill", "#5c5c56")
        .text(`Ato ${a.id}`);
    });

    // Eixos
    svg.append("g").attr("transform", `translate(0,${H_STRIP - M_STRIP.b})`)
      .call(d3.axisBottom(X).ticks(7).tickFormat(d3.format("d")))
      .attr("color", "#d8d6cf");

    svg.append("g").attr("transform", `translate(${M_STRIP.l},0)`)
      .call(d3.axisLeft(Y).ticks(6).tickFormat(d => Math.abs(d).toFixed(1) + "°S"))
      .attr("color", "#d8d6cf");

    // Linhas por variável
    const lineGen = d3.line().x(p => X(p.a)).y(p => Y(p.lat));
    activeVarsList.forEach(v => {
      svg.append("path")
        .attr("d", lineGen(v.pts))
        .attr("fill", "none")
        .attr("stroke", v.cor)
        .attr("stroke-width", 2)
        .attr("opacity", 0.9);
    });

    // Scanline & Pontos no ano atual
    const gDin = svg.append("g");
    gDin.append("line")
      .attr("x1", X(anoAtual)).attr("x2", X(anoAtual))
      .attr("y1", M_STRIP.t).attr("y2", H_STRIP - M_STRIP.b)
      .attr("stroke", "#1a1a1a").attr("stroke-width", 1)
      .attr("stroke-dasharray", "3 2").attr("opacity", 0.6);

    activeVarsList.forEach(v => {
      const p = v.pts.find(pt => pt.a === anoAtual) || v.pts[v.pts.length - 1];
      gDin.append("circle")
        .attr("cx", X(p.a)).attr("cy", Y(p.lat)).attr("r", 4)
        .attr("fill", v.cor).attr("stroke", "#ffffff").attr("stroke-width", 1.4);
    });

    // Listener de drag/scrub
    const overlay = svg.append("rect")
      .attr("x", M_STRIP.l).attr("y", M_STRIP.t)
      .attr("width", W_STRIP - M_STRIP.r - M_STRIP.l)
      .attr("height", (H_STRIP - M_STRIP.b) - M_STRIP.t)
      .attr("fill", "transparent").style("cursor", "ew-resize");

    function scrub(ev) {
      const [mx] = d3.pointer(ev, svg.node());
      const ano = Math.round(X.invert(mx));
      anoAtual = Math.max(1985, Math.min(2024, ano));
      render();
    }

    overlay.on("pointerdown", function (ev) {
      parar(); scrub(ev);
      const move = e => scrub(e);
      const up = () => { root.removeEventListener("pointermove", move); root.removeEventListener("pointerup", up); };
      root.addEventListener("pointermove", move); root.addEventListener("pointerup", up);
    });
  }

  // --------------------------------------------------------------------------
  // 5. Renderização dos Cards Analíticos
  // --------------------------------------------------------------------------
  function renderCards() {
    const grid = el("cm-cards-grid");
    if (!grid) return;

    const list = DADOS.variaveis.filter(v => activeVars.has(v.id));

    grid.innerHTML = list.map(v => {
      const dN = v.liquido.dN != null ? v.liquido.dN : 0;
      let tagClass = "robust";
      let tagText = `+${dN} km (Norte)`;

      if (dN < 0) {
        tagClass = "south";
        tagText = `${dN} km (Sul)`;
      } else if (!v.liquido.robusto && dN < 15) {
        tagClass = "anchored";
        tagText = `+${dN} km (≈ Ancorada)`;
      }

      // Tag extra: deslocamento no Ato III para a categoria de validação (soja)
      let atoIII = "";
      if (v.categoria === "validacao" && v.liquido.janelas && v.liquido.janelas["Ato III"] != null) {
        const a3 = v.liquido.janelas["Ato III"];
        const cls = a3 < 0 ? "south" : "robust";
        atoIII = `<span class="cm-card-shift ${cls}" style="margin-left:0.35rem">Ato III: ${a3 > 0 ? "+" : ""}${a3} km</span>`;
      }

      const ano0 = v.pts[0].a;
      const ano1 = v.pts[v.pts.length - 1].a;

      return `
        <div class="cm-card" style="border-left-color: ${v.cor}">
          <div class="cm-card-head">
            <h3 class="cm-card-title">${v.rotulo}</h3>
            <span><span class="cm-card-shift ${tagClass}">${tagText}</span>${atoIII}</span>
          </div>
          <p class="cm-card-insight">${v.insight}</p>
          <div class="cm-card-footer">
            <span>Fonte: <strong>${v.fonte}</strong></span>
            <span>Ano: ${ano0}–${ano1}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  // --------------------------------------------------------------------------
  // 6. Atualização Render Loop
  // --------------------------------------------------------------------------
  function render() {
    const slider = el("cm-year-slider");
    if (slider) slider.value = String(anoAtual);

    const yearDisplay = el("cm-year-display");
    if (yearDisplay) yearDisplay.textContent = anoAtual;

    desenharMapa();
    desenharStrip();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
