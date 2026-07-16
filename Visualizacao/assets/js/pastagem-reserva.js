/* pastagem-reserva.js — Sub-pipeline #28-C.
 *
 * Enriquece o bloco §6 ("Pastagem como reserva de terra") com dois elementos
 * interativos (progressive enhancement — sem d3/JS, a figura estática assume):
 *   1. Coroplético das 166 AMCs pela idade média da pastagem na conversão
 *      (idade_pastagem_amc.geojson) — gradiente Sul(jovem)→Norte(antigo), a
 *      geografia da bimodalidade do #40.
 *   2. Histograma por Ato com toggle (idade_pastagem_histograma.json),
 *      destacando visualmente os DOIS picos (bimodalidade) no Ato III.
 *
 * Vanilla + d3 v7 (já carregado). Namespace: window.GO40.reserva.
 */
(function (root) {
  "use strict";

  const COR_JOVEM = "#e8920c";   // laranja — pasto jovem (rotação/ILP), Sul
  const COR_ANTIGO = "#2e7d32";  // verde — pasto antigo (oportunismo), Norte
  const COR_SEM = "#e6e3dc";     // AMC sem pixels de conversão
  const DOM = [6, 22];           // ancorado nos dois modos (~5 × ~22 anos)

  function corIdade(v) {
    if (v == null || isNaN(v)) return COR_SEM;
    return d3.scaleLinear()
      .domain([DOM[0], (DOM[0] + DOM[1]) / 2, DOM[1]])
      .range([COR_JOVEM, "#f0e2a8", COR_ANTIGO])
      .clamp(true)(v);
  }

  function tooltip() {
    let el = document.getElementById("reserva-tooltip");
    if (!el) {
      el = document.createElement("div");
      el.id = "reserva-tooltip";
      el.className = "reserva-tooltip";
      el.hidden = true;
      document.body.appendChild(el);
    }
    return el;
  }

  // ---- 1. Coroplético AMC ----
  function desenharMapa(geo) {
    const cont = d3.select("#reserva-mapa");
    cont.selectAll("*").remove();
    const W = 460, H = 420;
    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("class", "reserva-svg");

    const proj = d3.geoMercator().fitSize([W, H - 8], geo);
    const path = d3.geoPath(proj);
    const tip = tooltip();

    svg.append("g").selectAll("path")
      .data(geo.features)
      .join("path")
      .attr("d", path)
      .attr("fill", d => corIdade(d.properties.idade_amc))
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.4)
      .attr("tabindex", 0)
      .attr("role", "listitem")
      .on("pointerenter focus", function (ev, d) {
        d3.select(this).attr("stroke", "#222").attr("stroke-width", 1.2).raise();
        const p = d.properties;
        const idade = p.idade_amc == null || isNaN(p.idade_amc)
          ? "sem conversão amostrada"
          : `${p.idade_amc.toFixed(1).replace(".", ",")} anos`;
        tip.hidden = false;
        tip.innerHTML = `<strong>AMC ${p.code_amc}</strong>` +
          (p.mesorregiao ? `<br>${p.mesorregiao}` : "") +
          `<br>idade média: ${idade}`;
      })
      .on("pointermove", ev => {
        tip.style.left = (ev.clientX + 14) + "px";
        tip.style.top = (ev.clientY + 14) + "px";
      })
      .on("pointerleave blur", function () {
        d3.select(this).attr("stroke", "#fff").attr("stroke-width", 0.4);
        tip.hidden = true;
      });

    desenharLegenda();
  }

  function desenharLegenda() {
    const cont = d3.select("#reserva-mapa-legenda");
    cont.selectAll("*").remove();
    const W = 260, H = 44;
    const svg = cont.append("svg").attr("viewBox", `0 0 ${W} ${H}`)
      .attr("class", "reserva-legenda-svg");
    const defs = svg.append("defs");
    const grad = defs.append("linearGradient").attr("id", "reserva-grad")
      .attr("x1", "0%").attr("x2", "100%");
    const stops = [[0, COR_JOVEM], [0.5, "#f0e2a8"], [1, COR_ANTIGO]];
    stops.forEach(([o, c]) => grad.append("stop")
      .attr("offset", `${o * 100}%`).attr("stop-color", c));
    svg.append("rect").attr("x", 8).attr("y", 6).attr("width", W - 16)
      .attr("height", 12).attr("rx", 2).attr("fill", "url(#reserva-grad)");
    const labels = [[8, "6 a", "start"], [W / 2, "14 a", "middle"], [W - 8, "22+ a", "end"]];
    labels.forEach(([x, t, anc]) => svg.append("text").attr("x", x).attr("y", 34)
      .attr("text-anchor", anc).attr("class", "reserva-legenda-txt").text(t));
    svg.append("text").attr("x", 8).attr("y", 34).attr("text-anchor", "start")
      .attr("class", "reserva-legenda-cap").attr("dy", 9).text("jovem (Sul)");
    svg.append("text").attr("x", W - 8).attr("y", 34).attr("text-anchor", "end")
      .attr("class", "reserva-legenda-cap").attr("dy", 9).text("antigo (Norte)");
  }

  // ---- 2. Histograma por Ato ----
  let HIST = [];
  let atoAtivo = 2; // começa no Ato III (onde a bimodalidade é visível)

  function desenharToggle() {
    const cont = d3.select("#reserva-ato-toggle");
    cont.selectAll("*").remove();
    HIST.forEach((h, i) => {
      cont.append("button")
        .attr("type", "button")
        .attr("role", "tab")
        .attr("aria-selected", i === atoAtivo ? "true" : "false")
        .attr("class", "reserva-tab" + (i === atoAtivo ? " reserva-tab--ativo" : ""))
        .style("--ato-cor", (root.GO40.ATOS[i] || {}).cor || "#666")
        .html(`Ato ${h.ato} <span>${h.periodo[0]}–${h.periodo[1]}</span>`)
        .on("click", () => { atoAtivo = i; desenharToggle(); desenharHist(); });
    });
  }

  function picosBimodais(h) {
    // Detecta os dois maiores picos separados por ao menos 6 bins (12 anos).
    const c = h.counts;
    const idx = c.map((v, i) => [i, v]).filter(d => d[1] > 0)
      .sort((a, b) => b[1] - a[1]);
    if (idx.length === 0) return new Set();
    const p1 = idx[0][0];
    const p2 = (idx.find(d => Math.abs(d[0] - p1) >= 6) || [])[0];
    const s = new Set([p1]);
    if (p2 != null) s.add(p2);
    return s;
  }

  function desenharHist() {
    const h = HIST[atoAtivo];
    const cont = d3.select("#reserva-hist");
    cont.selectAll("*").remove();
    const W = 460, H = 300, M = { t: 12, r: 12, b: 34, l: 40 };
    const svg = cont.append("svg").attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet").attr("class", "reserva-svg");

    const centros = h.bins.slice(0, h.counts.length).map((b, i) =>
      (b + (h.bins[i + 1] ?? b + 2)) / 2);
    const x = d3.scaleLinear().domain([0, 40]).range([M.l, W - M.r]);
    const y = d3.scaleLinear().domain([0, d3.max(h.counts) * 1.08]).range([H - M.b, M.t]);
    const bw = (x(2) - x(0)) * 0.86;
    const picos = h.ato === "III" ? picosBimodais(h) : new Set();

    // eixos
    svg.append("g").attr("transform", `translate(0,${H - M.b})`)
      .call(d3.axisBottom(x).ticks(8).tickFormat(d => d + "a"))
      .attr("class", "reserva-eixo");
    svg.append("g").attr("transform", `translate(${M.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d3.format("~s")(d)))
      .attr("class", "reserva-eixo");

    // barras
    svg.append("g").selectAll("rect")
      .data(h.counts).join("rect")
      .attr("x", (d, i) => x(centros[i]) - bw / 2)
      .attr("y", d => y(d))
      .attr("width", bw)
      .attr("height", d => (H - M.b) - y(d))
      .attr("fill", (d, i) => corIdade(centros[i]))  // mesma linguagem de cor do mapa
      .attr("opacity", (d, i) => picos.size && !picos.has(i) ? 0.4 : 0.95)
      .attr("stroke", (d, i) => picos.has(i) ? "#222" : "none")
      .attr("stroke-width", 0.6);

    // mediana
    svg.append("line")
      .attr("x1", x(h.mediana)).attr("x2", x(h.mediana))
      .attr("y1", M.t).attr("y2", H - M.b)
      .attr("stroke", "#222").attr("stroke-dasharray", "4 3").attr("stroke-width", 1.2);
    svg.append("text").attr("x", x(h.mediana) + 4).attr("y", M.t + 10)
      .attr("class", "reserva-hist-med")
      .text(`mediana ${h.mediana.toString().replace(".", ",")} a`);

    // anotação bimodal (Ato III)
    if (picos.size >= 2) {
      svg.append("text").attr("x", W - M.r).attr("y", H - M.b - 6)
        .attr("text-anchor", "end").attr("class", "reserva-hist-nota-svg")
        .text("dois picos = dois mecanismos");
    }

    const nota = document.getElementById("reserva-hist-nota");
    if (nota) {
      const n = root.GO40.fmt.num(h.n);
      nota.innerHTML = h.ato === "III"
        ? `<strong>Ato III (${h.periodo[0]}–${h.periodo[1]})</strong>: a distribuição é ` +
          `<strong>bimodal</strong> — um pico de pasto jovem (~5 a) e outro de pasto ` +
          `antigo (~35 a, destacado). ${n} amostras.`
        : `Ato ${h.ato} (${h.periodo[0]}–${h.periodo[1]}): mediana ` +
          `${h.mediana.toString().replace(".", ",")} anos. ${n} amostras.`;
    }
  }

  // d3 é carregado lazy (mesmo vendor do sankey.js) — não é global no load.
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src; s.onload = resolve;
      s.onerror = () => reject(new Error("Falha ao carregar: " + src));
      document.head.appendChild(s);
    });
  }

  async function garantirD3() {
    if (root.d3 && root.d3.geoPath) return;
    await loadScript("assets/js/vendor/d3.v7.min.js?v=2");
  }

  let montado = false;
  async function montar(bloco) {
    if (montado) return;
    montado = true;
    try {
      await garantirD3();
      const [geo, hist] = await Promise.all([
        d3.json("assets/data/idade_pastagem_amc.geojson"),
        d3.json("assets/data/idade_pastagem_histograma.json")
      ]);
      if (!geo || !hist) return;
      HIST = hist;
      bloco.hidden = false;          // revela só quando os dados chegam
      desenharMapa(geo);
      desenharToggle();
      desenharHist();
    } catch (err) {
      montado = false;               // permite nova tentativa
      console.warn("[reserva] falha ao montar", err);
    }
  }

  function init() {
    const bloco = document.getElementById("reserva-interativo");
    if (!bloco) return;
    // Observa o bloco-pai VISÍVEL (#reserva-interativo começa hidden = tamanho 0).
    const alvo = document.getElementById("sec-idade-pastagem") || bloco;
    if (typeof IntersectionObserver === "undefined") { montar(bloco); return; }
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { montar(bloco); obs.disconnect(); }
      });
    }, { rootMargin: "300px 0px" });
    obs.observe(alvo);
  }

  root.GO40 = root.GO40 || {};
  root.GO40.reserva = { init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
