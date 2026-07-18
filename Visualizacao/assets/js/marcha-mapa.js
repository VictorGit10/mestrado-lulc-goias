/* marcha-mapa.js — Pipeline #32, versão interativa da marcha ao norte.
 *
 * Herói do Movimento III: o centro de massa de cada uso da terra (agricultura,
 * pastagem, rebanho, vegetação natural) CAMINHANDO ano a ano, 1985→2024, sobre
 * a malha das AMCs — com uma faixa latitude-tempo sincronizada ao lado, que é a
 * versão viva de `deslocamento_latitude.png`.
 *
 * Progressive enhancement: sem d3/JS (ou em falha de rede) o bloco fica hidden
 * e o scrollytelling de PNGs logo abaixo assume a narrativa. Namespace:
 * window.GO40.marchaMapa. Consome assets/data/marcha_centro_massa.json (#32) e
 * reusa a malha idade_pastagem_amc.geojson como base cartográfica.
 *
 * NOTA cartográfica (honestidade de escala): a marcha líquida é ~80 km num
 * estado de ~700 km. O mapa dá zoom na nuvem de trajetórias (para o movimento
 * ser legível) e compensa com (a) um localizador do recorte sobre Goiás inteiro
 * e (b) uma barra de escala em km. O movimento fino ano-a-ano vive na faixa de
 * latitude; o mapa mostra direção e geografia.
 *
 * Um mapa-base de satélite/terreno (MapLibre GL JS, fork open-source do Mapbox,
 * sem token nem cobrança) daria contexto geográfico e câmera 3D — foi avaliado
 * e DESCARTADO de propósito: quebraria o modelo self-contained/offline desta
 * viz (roda no GitHub Pages, tudo vendorizado) e, com deslocamento tão pequeno
 * numa imagem de satélite bonita, o basemap ofuscaria um sinal pequeno-porém-
 * robusto. Se um dia quiser satélite de fundo, o caminho é MapLibre (não Mapbox)
 * — ver Textos/pipelines/32_centro_massa.md, seção "Visualização interativa".
 */
(function (root) {
  "use strict";

  // Hex literais da paleta (styles.css): var(--...) num ATRIBUTO de apresentação
  // SVG não resolve confiavelmente em todo navegador (Firefox), então fixamos aqui.
  const COR_FG = "#1a1a1a";       // --color-fg
  const COR_RULE = "#d8d6cf";     // --color-rule
  const COR_ACCENT = "#8b3a1d";   // --color-accent

  let DADOS = null;
  let GEO = null;
  let proj = null;
  let path = null;
  let X = null, Y = null;      // escalas da faixa latitude-tempo
  let anoAtual = 1985;
  let tocando = false;
  let timer = null;
  let mostrarElipse = false;

  const W_MAPA = 520, H_MAPA = 480;
  const M_STRIP = { t: 14, r: 14, b: 30, l: 40 };
  const W_STRIP = 460, H_STRIP = 360;

  // ---- utilidades ----
  function el(id) { return document.getElementById(id); }

  function anoParaAto(ano) {
    return (DADOS.atos || []).find(a => ano >= a.ini && ano <= a.fim) || null;
  }

  function fmtLat(v) {
    // -17.09 -> "17,09° S"
    return Math.abs(v).toFixed(2).replace(".", ",") + "° S";
  }

  // ==========================================================================
  // 1. Mapa animado
  // ==========================================================================
  function bboxTrajetorias(pad) {
    let lon0 = Infinity, lon1 = -Infinity, lat0 = Infinity, lat1 = -Infinity;
    DADOS.variaveis.forEach(v => v.pts.forEach(p => {
      lon0 = Math.min(lon0, p.lon); lon1 = Math.max(lon1, p.lon);
      lat0 = Math.min(lat0, p.lat); lat1 = Math.max(lat1, p.lat);
    }));
    const dlon = (lon1 - lon0) * pad, dlat = (lat1 - lat0) * pad;
    return [[lon0 - dlon, lat0 - dlat], [lon1 + dlon, lat1 + dlat]];
  }

  function desenharMapa() {
    const cont = d3.select("#marchamap-mapa");
    cont.selectAll("*").remove();
    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W_MAPA} ${H_MAPA}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("class", "marchamap-svg");

    // Projeção: zoom na nuvem de trajetórias (60% de folga em torno da bbox).
    const [sw, ne] = bboxTrajetorias(0.6);
    // GeoJSON multipoint dos 2 cantos = extensão a enquadrar (evita geoBounds,
    // que lê o winding do polígono ao contrário e devolve bounds ~globais).
    const extent = { type: "MultiPoint", coordinates: [sw, ne] };
    proj = d3.geoMercator().fitExtent([[16, 16], [W_MAPA - 16, H_MAPA - 44]], extent);
    path = d3.geoPath(proj);

    // clip ao frame (o mapa dá zoom; recorta a malha que sai da moldura)
    svg.append("clipPath").attr("id", "marchamap-clip")
      .append("rect").attr("x", 0).attr("y", 0).attr("width", W_MAPA).attr("height", H_MAPA);
    const g = svg.append("g").attr("clip-path", "url(#marchamap-clip)");

    // malha AMC (contexto)
    g.append("g").selectAll("path").data(GEO.features).join("path")
      .attr("d", path).attr("fill", "#f3f1ea").attr("stroke", "#ffffff")
      .attr("stroke-width", 0.5);

    // trajetórias completas (contexto faint) + camadas por variável
    const gVar = g.append("g").attr("class", "marchamap-vars");
    DADOS.variaveis.forEach(v => {
      const linePts = v.pts.map(p => proj([p.lon, p.lat]));
      const lineGen = d3.line().curve(d3.curveCatmullRom.alpha(0.5));

      const gv = gVar.append("g").attr("data-var", v.id);
      // trajetória completa, tênue (mostra o caminho inteiro de saída)
      gv.append("path").attr("class", "marchamap-traj-full")
        .attr("d", lineGen(linePts))
        .attr("fill", "none").attr("stroke", v.cor)
        .attr("stroke-width", 1).attr("stroke-dasharray", "2 3")
        .attr("opacity", 0.28);
      // trecho percorrido (colorido, cresce com o ano)
      gv.append("path").attr("class", "marchamap-traj-done")
        .attr("fill", "none").attr("stroke", v.cor)
        .attr("stroke-width", 2.4).attr("stroke-linecap", "round")
        .attr("opacity", 0.9);
      // elipse do ato (opcional)
      gv.append("path").attr("class", "marchamap-elipse")
        .attr("fill", v.cor).attr("fill-opacity", 0.07)
        .attr("stroke", v.cor).attr("stroke-width", 1)
        .attr("stroke-dasharray", "3 2").attr("opacity", 0).style("display", "none");
      // ponto de partida (1985, vazado)
      const p0 = proj([v.pts[0].lon, v.pts[0].lat]);
      gv.append("circle").attr("class", "marchamap-start")
        .attr("cx", p0[0]).attr("cy", p0[1]).attr("r", 3.2)
        .attr("fill", "#fff").attr("stroke", v.cor).attr("stroke-width", 1.6);
      // cabeça (posição do ano atual)
      gv.append("circle").attr("class", "marchamap-head")
        .attr("r", 5.5).attr("fill", v.cor)
        .attr("stroke", "#fff").attr("stroke-width", 1.6);
    });

    desenharLocalizador(svg, sw, ne);
    desenharSetaNorte(svg);
    desenharEscala(svg);
  }

  // localizador: Goiás inteiro + retângulo do recorte ampliado
  function desenharLocalizador(svg, sw, ne) {
    const w = 78, h = 92, x0 = W_MAPA - w - 8, y0 = 8;
    const g = svg.append("g").attr("transform", `translate(${x0},${y0})`)
      .attr("class", "marchamap-loc");
    g.append("rect").attr("width", w).attr("height", h).attr("rx", 3)
      .attr("fill", "#fff").attr("stroke", COR_RULE).attr("stroke-width", 1);
    const pLoc = d3.geoMercator().fitExtent([[5, 5], [w - 5, h - 5]], GEO);
    const pathLoc = d3.geoPath(pLoc);
    g.append("path").attr("d", pathLoc(GEO))
      .attr("fill", "#ece9e1").attr("stroke", "#cfccc3").attr("stroke-width", 0.4);
    // retângulo do recorte (canto NO e SE do bbox, projetados direto)
    const tl = pLoc([sw[0], ne[1]]), br = pLoc([ne[0], sw[1]]);
    g.append("rect").attr("x", tl[0]).attr("y", tl[1])
      .attr("width", br[0] - tl[0]).attr("height", br[1] - tl[1])
      .attr("fill", "none").attr("stroke", COR_ACCENT).attr("stroke-width", 1.2);
  }

  function desenharSetaNorte(svg) {
    const g = svg.append("g").attr("transform", `translate(20,${H_MAPA - 58})`)
      .attr("class", "marchamap-norte");
    g.append("line").attr("x1", 0).attr("y1", 16).attr("x2", 0).attr("y2", -2)
      .attr("stroke", COR_FG).attr("stroke-width", 1.4);
    g.append("path").attr("d", "M0,-8 L4,2 L0,-1 L-4,2 Z").attr("fill", COR_FG);
    g.append("text").attr("x", 0).attr("y", 30).attr("text-anchor", "middle")
      .attr("class", "marchamap-norte-txt").text("N");
  }

  function desenharEscala(svg) {
    // 50 km a partir do centro do frame, medidos na longitude local
    const cLat = (proj.invert([W_MAPA / 2, H_MAPA / 2]) || [0, -16])[1];
    const km = 50;
    const dLon = km / (111.32 * Math.cos(cLat * Math.PI / 180));
    const cLon = proj.invert([W_MAPA / 2, H_MAPA / 2])[0];
    const x1 = proj([cLon, cLat])[0], x2 = proj([cLon + dLon, cLat])[0];
    const px = Math.abs(x2 - x1);
    const x0 = W_MAPA - px - 16, y0 = H_MAPA - 16;
    const g = svg.append("g").attr("class", "marchamap-escala");
    g.append("line").attr("x1", x0).attr("y1", y0).attr("x2", x0 + px).attr("y2", y0)
      .attr("stroke", COR_FG).attr("stroke-width", 1.6);
    [[x0, y0], [x0 + px, y0]].forEach(([x, y]) => g.append("line")
      .attr("x1", x).attr("y1", y - 3).attr("x2", x).attr("y2", y + 3)
      .attr("stroke", COR_FG).attr("stroke-width", 1.6));
    g.append("text").attr("x", x0 + px / 2).attr("y", y0 - 5).attr("text-anchor", "middle")
      .attr("class", "marchamap-escala-txt").text("50 km");
  }

  function pontoInterp(v, ano) {
    // posição no ano (com a mesma curva do traçado, via ponto anual exato)
    const p = v.pts.find(pt => pt.a === ano) || v.pts[v.pts.length - 1];
    return proj([p.lon, p.lat]);
  }

  function atualizarMapa() {
    if (!proj) return;
    const svg = d3.select("#marchamap-mapa svg");
    const lineGen = d3.line().curve(d3.curveCatmullRom.alpha(0.5));
    DADOS.variaveis.forEach(v => {
      const gv = svg.select(`g[data-var="${v.id}"]`);
      const feitos = v.pts.filter(p => p.a <= anoAtual).map(p => proj([p.lon, p.lat]));
      gv.select(".marchamap-traj-done").attr("d", feitos.length > 1 ? lineGen(feitos) : null);
      const hp = pontoInterp(v, anoAtual);
      gv.select(".marchamap-head").attr("cx", hp[0]).attr("cy", hp[1]);
    });
    atualizarElipses(svg);
  }

  function atualizarElipses(svg) {
    const ato = anoParaAto(anoAtual);
    DADOS.variaveis.forEach(v => {
      const gv = svg.select(`g[data-var="${v.id}"]`);
      const sel = gv.select(".marchamap-elipse");
      if (!mostrarElipse || !ato) { sel.attr("opacity", 0).style("display", "none"); return; }
      const e = (DADOS.elipses || []).find(x => x.id === v.id && x.ato === ato.id);
      if (!e) { sel.attr("opacity", 0).style("display", "none"); return; }
      const d = "M" + e.ring.map(pt => proj(pt).join(",")).join("L") + "Z";
      sel.attr("d", d).style("display", null).attr("opacity", 0.85);
    });
  }

  // ==========================================================================
  // 2. Faixa latitude-tempo (deslocamento_latitude.png viva)
  // ==========================================================================
  function desenharStrip() {
    const cont = d3.select("#marchamap-strip");
    cont.selectAll("*").remove();
    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W_STRIP} ${H_STRIP}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("class", "marchamap-svg");

    let lat0 = Infinity, lat1 = -Infinity;
    DADOS.variaveis.forEach(v => v.pts.forEach(p => {
      lat0 = Math.min(lat0, p.lat); lat1 = Math.max(lat1, p.lat);
    }));
    const pad = (lat1 - lat0) * 0.08;
    X = d3.scaleLinear().domain([DADOS.anos[0], DADOS.anos[DADOS.anos.length - 1]])
      .range([M_STRIP.l, W_STRIP - M_STRIP.r]);
    Y = d3.scaleLinear().domain([lat0 - pad, lat1 + pad])
      .range([H_STRIP - M_STRIP.b, M_STRIP.t]);

    // bandas dos atos
    const gB = svg.append("g");
    (DADOS.atos || []).forEach((a, i) => {
      gB.append("rect")
        .attr("x", X(a.ini)).attr("y", M_STRIP.t)
        .attr("width", X(a.fim) - X(a.ini)).attr("height", (H_STRIP - M_STRIP.b) - M_STRIP.t)
        .attr("fill", i % 2 ? "#00000000" : "#0000000a");
      gB.append("text").attr("x", (X(a.ini) + X(a.fim)) / 2).attr("y", M_STRIP.t + 11)
        .attr("text-anchor", "middle").attr("class", "marchamap-ato-txt")
        .text("Ato " + a.id);
    });

    // eixos
    svg.append("g").attr("transform", `translate(0,${H_STRIP - M_STRIP.b})`)
      .call(d3.axisBottom(X).ticks(6).tickFormat(d3.format("d")))
      .attr("class", "marchamap-eixo");
    svg.append("g").attr("transform", `translate(${M_STRIP.l},0)`)
      .call(d3.axisLeft(Y).ticks(5).tickFormat(d => Math.abs(d).toFixed(1).replace(".", ",")))
      .attr("class", "marchamap-eixo");
    svg.append("text").attr("x", M_STRIP.l - 30).attr("y", M_STRIP.t - 2)
      .attr("class", "marchamap-eixo-cap").text("°S ↑ norte");

    // linhas de latitude por variável
    const lineGen = d3.line().x(p => X(p.a)).y(p => Y(p.lat));
    DADOS.variaveis.forEach(v => {
      svg.append("path").attr("d", lineGen(v.pts))
        .attr("fill", "none").attr("stroke", v.cor).attr("stroke-width", 2)
        .attr("opacity", 0.9);
    });

    // grupo dinâmico: scan line + marcadores do ano
    const gDin = svg.append("g").attr("class", "marchamap-din");
    gDin.append("line").attr("class", "marchamap-scan")
      .attr("y1", M_STRIP.t).attr("y2", H_STRIP - M_STRIP.b)
      .attr("stroke", COR_FG).attr("stroke-width", 1)
      .attr("stroke-dasharray", "3 2").attr("opacity", 0.55);
    DADOS.variaveis.forEach(v => {
      gDin.append("circle").attr("data-var", v.id).attr("r", 4)
        .attr("fill", v.cor).attr("stroke", "#fff").attr("stroke-width", 1.4);
    });

    // scrub: clicar/arrastar na faixa muda o ano
    const overlay = svg.append("rect")
      .attr("x", M_STRIP.l).attr("y", M_STRIP.t)
      .attr("width", W_STRIP - M_STRIP.r - M_STRIP.l)
      .attr("height", (H_STRIP - M_STRIP.b) - M_STRIP.t)
      .attr("fill", "transparent").style("cursor", "ew-resize");
    function scrub(ev) {
      const [mx] = d3.pointer(ev, svg.node());
      const ano = Math.round(X.invert(mx));
      irParaAno(Math.max(DADOS.anos[0], Math.min(DADOS.anos[DADOS.anos.length - 1], ano)));
    }
    overlay.on("pointerdown", function (ev) {
      parar(); scrub(ev);
      const move = e => scrub(e);
      const up = () => { root.removeEventListener("pointermove", move); root.removeEventListener("pointerup", up); };
      root.addEventListener("pointermove", move); root.addEventListener("pointerup", up);
    });
  }

  function atualizarStrip() {
    const svg = d3.select("#marchamap-strip svg");
    if (svg.empty()) return;
    svg.select(".marchamap-scan").attr("x1", X(anoAtual)).attr("x2", X(anoAtual));
    DADOS.variaveis.forEach(v => {
      const p = v.pts.find(pt => pt.a === anoAtual) || v.pts[v.pts.length - 1];
      svg.select(`.marchamap-din circle[data-var="${v.id}"]`)
        .attr("cx", X(p.a)).attr("cy", Y(p.lat));
    });
  }

  // ==========================================================================
  // 3. Controles e sincronização
  // ==========================================================================
  function atualizarLegendaNota() {
    const ato = anoParaAto(anoAtual);
    el("marchamap-ano").textContent = anoAtual;
    const slider = el("marchamap-slider");
    if (slider) slider.value = String(anoAtual);
    // nota: gradiente atual (agric ao sul de pasto) — lê direto dos pontos
    const byId = {};
    DADOS.variaveis.forEach(v => {
      const p = v.pts.find(pt => pt.a === anoAtual);
      if (p) byId[v.id] = p.lat;
    });
    const nota = el("marchamap-nota");
    if (nota && byId.agricultura != null && byId.pastagem != null) {
      const gap = Math.abs(byId.pastagem - byId.agricultura) * 111.0; // km aprox
      nota.innerHTML =
        `<strong>${anoAtual}</strong>` + (ato ? ` · Ato ${ato.id} (${ato.titulo})` : "") +
        ` — a agricultura está <strong>~${Math.round(gap)} km ao sul</strong> ` +
        `de pasto/rebanho. Arraste a faixa ou o controle para percorrer os 40 anos.`;
    }
  }

  function render() {
    atualizarMapa();
    atualizarStrip();
    atualizarLegendaNota();
  }

  function irParaAno(ano) {
    anoAtual = ano;
    render();
  }

  function tocar() {
    if (tocando) return;
    if (anoAtual >= DADOS.anos[DADOS.anos.length - 1]) anoAtual = DADOS.anos[0];
    tocando = true;
    el("marchamap-play").textContent = "⏸ Pausar";
    el("marchamap-play").setAttribute("aria-pressed", "true");
    timer = setInterval(() => {
      if (anoAtual >= DADOS.anos[DADOS.anos.length - 1]) { parar(); return; }
      anoAtual += 1;
      render();
    }, 130);
  }

  function parar() {
    tocando = false;
    if (timer) { clearInterval(timer); timer = null; }
    const b = el("marchamap-play");
    if (b) { b.textContent = "▶ Reproduzir"; b.setAttribute("aria-pressed", "false"); }
  }

  function desenharLegenda() {
    const cont = d3.select("#marchamap-legenda");
    cont.selectAll("*").remove();
    DADOS.variaveis.slice().reverse().forEach(v => {
      const item = cont.append("span").attr("class", "marchamap-leg-item");
      item.append("span").attr("class", "marchamap-leg-swatch")
        .style("background", v.cor);
      const dN = v.liquido.dN;
      const rob = v.liquido.robusto === false;
      item.append("span").html(
        `${v.rotulo} <b>${dN >= 0 ? "+" : ""}${String(dN).replace(".", ",")} km</b>` +
        (rob ? " <em>(≈ ancorada)</em>" : ""));
    });
  }

  function ligarControles() {
    const play = el("marchamap-play");
    if (play) play.addEventListener("click", () => tocando ? parar() : tocar());
    const slider = el("marchamap-slider");
    if (slider) {
      slider.min = String(DADOS.anos[0]);
      slider.max = String(DADOS.anos[DADOS.anos.length - 1]);
      slider.value = String(anoAtual);
      slider.addEventListener("input", e => { parar(); irParaAno(+e.target.value); });
    }
    const chk = el("marchamap-elipse");
    if (chk) chk.addEventListener("change", e => {
      mostrarElipse = e.target.checked;
      atualizarElipses(d3.select("#marchamap-mapa svg"));
    });
  }

  // ==========================================================================
  // 4. Boot (lazy: d3 + JSON só quando o bloco entra em cena)
  // ==========================================================================
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
      const [dados, geo] = await Promise.all([
        d3.json("assets/data/marcha_centro_massa.json"),
        d3.json("assets/data/idade_pastagem_amc.geojson"),
      ]);
      if (!dados || !geo) return;
      DADOS = dados; GEO = geo;
      anoAtual = DADOS.anos[0];
      bloco.hidden = false;
      desenharMapa();
      desenharStrip();
      desenharLegenda();
      ligarControles();
      render();
    } catch (err) {
      montado = false;
      console.warn("[marcha-mapa] falha ao montar", err);
    }
  }

  function init() {
    const bloco = el("marcha-mapa-bloco");
    if (!bloco) return;
    if (typeof IntersectionObserver === "undefined") { montar(bloco); return; }
    // Observa uma âncora VISÍVEL (o bloco começa hidden = display:none = área 0,
    // que nunca "intersecta"). O divisor do Movimento III fica logo acima.
    const alvo = el("mov-marcha") || bloco.parentElement || bloco;
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { montar(bloco); obs.disconnect(); } });
    }, { rootMargin: "400px 0px" });
    obs.observe(alvo);
    // pausa a animação ao sair da viewport (cortesia de bateria/CPU)
    const obsVis = new IntersectionObserver(entries => {
      entries.forEach(e => { if (!e.isIntersecting) parar(); });
    }, { threshold: 0 });
    obsVis.observe(bloco);
  }

  root.GO40 = root.GO40 || {};
  root.GO40.marchaMapa = { init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
