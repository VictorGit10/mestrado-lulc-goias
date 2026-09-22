/* ==========================================================================
   Por dentro do método — o centro de massa (metodo-centro-de-massa.html)
   Refaz no navegador a conta do Pipeline #32 com os dados reais exportados por
   scripts/exportar_metodo_centro_massa_viz.py. Nenhum número é digitado aqui:
   tudo sai de D (o JSON) — os oficiais vêm de D.oficial, os refeitos da conta.
   ========================================================================== */
(function () {
  "use strict";

  const $ = (s) => document.querySelector(s);
  const NS = "http://www.w3.org/2000/svg";
  const reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const VARS = ["pastagem", "bovinos", "agricultura", "veg_natural"];
  // cores do site (mesmas de centros_massa_completo.json)
  const COR = { pastagem: "#c79a2e", bovinos: "#8e3b5a", agricultura: "#d96aa3", veg_natural: "#2d5a3d" };
  const NORTE = "#4a7ba6", SUL = "#c97052", ACC = "#8b3a1d", INK = "#1a1a1a", RULE = "#d8d6cf", MUTED = "#6b6b6b";
  const TOPO = 800;                 // y do SVG = TOPO − y (km)
  const sy = (y) => TOPO - y;

  const fmt = (v, d = 1) => Number.isFinite(v) ? v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }) : "—";
  const fmtS = (v, d = 1) => (v > 0 ? "+" : v < 0 ? "−" : "") + fmt(Math.abs(v), d);
  const fmtI = (v) => Math.round(v).toLocaleString("pt-BR");
  const el = (tag, at = {}, pai) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); if (pai) pai.appendChild(e); return e; };
  const mix = (cor, p) => `color-mix(in srgb, ${cor} ${p}%, #f1efe8)`;

  const tip = $("#mt-tip");
  const mostraTip = (ev, html) => { tip.innerHTML = html; tip.classList.add("on"); tip.style.left = Math.min(ev.clientX + 14, innerWidth - 270) + "px"; tip.style.top = ev.clientY + 14 + "px"; };
  const escondeTip = () => tip.classList.remove("on");

  function segmento(sel, cb) {
    const box = $(sel);
    box.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      cb(b.dataset);
    }));
  }

  fetch("assets/data/metodo_centro_massa.json").then((r) => r.json()).then(iniciar).catch((e) => {
    console.error(e);
    document.querySelectorAll(".mt-fig").forEach((f) => { f.insertAdjacentHTML("afterbegin", '<p class="mt-leitura">Os dados desta figura não carregaram. Abra a página por um servidor (servir.py), e não direto do disco.</p>'); });
  });

  function iniciar(D) {
    const AMC = D.amc, N = AMC.length;
    const CX = AMC.map((a) => a.cx), CY = AMC.map((a) => a.cy), AREA = AMC.map((a) => a.area);
    const ANOS = D.anos, iA = (a) => a - 1985;
    const S = { v: "pastagem" };
    const ouvintes = [];
    const aoMudarVar = (fn) => ouvintes.push(fn);
    const nome = (v) => D.vars[v].rotulo, un = (v) => D.vars[v].unidade;
    const pesos = (v, ano) => D.pesos[v][iA(ano)];
    const Y0 = D.origem_m[1] / 1000, X0 = D.origem_m[0] / 1000;

    function latlon(x, y) {
      const u = x / D.latfit.esc, w = y / D.latfit.esc; let la = 0, lo = 0;
      D.latfit.expo.forEach(([i, j], k) => { const t = u ** i * w ** j; la += D.latfit.lat[k] * t; lo += D.latfit.lon[k] * t; });
      return [lo, la];
    }
    const grauMin = (v, h) => { const a = Math.abs(v), g = Math.floor(a); let m = Math.round((a - g) * 60); return m === 60 ? `${g + 1}°00′ ${h}` : `${g}°${String(m).padStart(2, "0")}′ ${h}`; };
    const fLat = (la) => grauMin(la, "S"), fLon = (lo) => grauMin(lo, "O");

    function centro(w, c) {
      let sw = 0, sx = 0, s_y = 0;
      for (let i = 0; i < N; i++) { const wi = c ? c[i] * w[i] : w[i]; if (!(wi > 0)) continue; sw += wi; sx += wi * CX[i]; s_y += wi * CY[i]; }
      return { x: sx / sw, y: s_y / sw, W: sw };
    }
    // Weiszfeld como no #32: parte do centro médio; tol 1e-4 m = 1e-7 km
    function weiszfeld(w) {
      let { x, y } = centro(w); const pts = [[x, y]];
      for (let k = 0; k < 1000; k++) {
        let a = 0, bx = 0, by = 0;
        for (let i = 0; i < N; i++) { if (!(w[i] > 0)) continue; const d = Math.max(Math.hypot(CX[i] - x, CY[i] - y), 1e-12); const q = w[i] / d; a += q; bx += q * CX[i]; by += q * CY[i]; }
        const nx = bx / a, ny = by / a; pts.push([nx, ny]);
        const fim = Math.hypot(nx - x, ny - y) < 1e-7; x = nx; y = ny; if (fim) break;
      }
      return pts;
    }
    function mulberry(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
    const rumo = (dx, dy) => ["norte", "nordeste", "leste", "sudeste", "sul", "sudoeste", "oeste", "noroeste"][Math.round(((Math.atan2(dx, dy) * 180) / Math.PI + 360) % 360 / 45) % 8];

    // ── mapa-base em km ────────────────────────────────────────────────
    const POLY_D = D.poly.map((an) => an.map((r) => "M" + r.map(([x, y]) => `${x},${sy(y)}`).join("L") + "Z").join(""));
    const CONT_D = D.contorno.map((r) => "M" + r.map(([x, y]) => `${x},${sy(y)}`).join("L") + "Z").join("");
    let uid = 0;
    function novoMapa(host, { vb = [-22, -8, 836, 822], rotulo = "Mapa de Goiás com as 166 AMC" } = {}) {
      const id = "mt" + ++uid;
      const svg = el("svg", { viewBox: vb.join(" "), class: "mt-mapa", role: "img", "aria-label": rotulo });
      const clip = el("clipPath", { id: id + "c" }, el("defs", {}, svg));
      el("rect", { x: vb[0], y: vb[1], width: vb[2], height: vb[3] }, clip);
      const gG = el("g", { "clip-path": `url(#${id}c)` }, svg);
      const gP = el("g", {}, svg);
      const polys = POLY_D.map((d) => el("path", { d, class: "amc" }, gP));
      el("path", { d: CONT_D, class: "contorno" }, svg);
      const gO = el("g", {}, svg), gT = el("g", {}, svg);
      const m = { svg, vb, gG, gO, gT, polys, atualiza: [] };
      m.kpx = () => vb[2] / Math.max(svg.clientWidth || 800, 1);
      host.appendChild(svg);
      // graticula com rótulos
      const txt = [];
      for (const g of D.grat) el("path", { d: "M" + g.pts.map(([x, y]) => `${x},${sy(y)}`).join("L"), class: "grat" }, gG);
      for (const g of D.grat) {
        const p = g.tipo === "lat" ? g.pts.find(([x]) => x >= vb[0] + 4) : g.pts.find(([, y]) => sy(y) <= vb[1] + vb[3] - 4);
        if (!p) continue;
        const px = p[0], py = sy(p[1]);
        if (px < vb[0] || px > vb[0] + vb[2] || py < vb[1] || py > vb[1] + vb[3]) continue;
        const t = el("text", { class: "grat-t", x: px + 3, y: py - 3 }, gG); t.textContent = `${Math.abs(g.v)}°${g.tipo === "lat" ? "S" : "O"}`; txt.push(t);
      }
      m.atualiza.push(() => { const k = m.kpx(); txt.forEach((t) => t.setAttribute("font-size", 11 * k)); });
      new ResizeObserver(() => m.atualiza.forEach((f) => f())).observe(svg);
      return m;
    }
    // símbolo ⊕ de centro de gravidade
    function marcaCG(pai, r = 9) {
      const g = el("g", {}, pai);
      el("circle", { r: 1, fill: "#fff", stroke: INK, "stroke-width": 0.16 }, g);
      el("path", { d: "M0,0L1,0A1,1 0 0,0 0,-1Z M0,0L-1,0A1,1 0 0,0 0,1Z", fill: INK }, g);
      g._r = r; return g;
    }
    function poeCG(g, m, x, y, r) { g._x = x; g._y = y; if (r) g._r = r; g.setAttribute("transform", `translate(${x},${sy(y)}) scale(${g._r * m.kpx()})`); }

    // ── barra de variáveis ─────────────────────────────────────────────
    const pills = $("#mt-pills");
    for (const v of VARS) {
      const b = document.createElement("button");
      b.type = "button"; b.className = "mt-pill"; b.style.setProperty("--c", COR[v]);
      b.innerHTML = `<i></i>${nome(v)}`; b.setAttribute("aria-pressed", v === S.v);
      b.addEventListener("click", () => { S.v = v; pills.querySelectorAll("button").forEach((x, k) => x.setAttribute("aria-pressed", VARS[k] === v)); ouvintes.forEach((f) => f()); });
      pills.appendChild(b);
    }

    // ── KPIs (oficiais) ────────────────────────────────────────────────
    (function kpis() {
      $("#mt-kpis").innerHTML = VARS.map((v) => {
        const b = D.oficial.boot.find((r) => r.variavel === v && r.janela === "LÍQUIDO");
        const bl = D.oficial.bloco.filter((r) => r.variavel === v);
        const rob = bl.every((r) => r.exclui_zero), anc = bl.every((r) => !r.exclui_zero);
        return `<div class="kpi-card${anc ? " ancorada" : ""}" style="--c:${COR[v]}">
          <div class="kpi-label">${nome(v)}</div>
          <div class="kpi-value">${anc ? "ancorada" : fmtS(b.dN_km) + " km"}</div>
          <div class="kpi-sub">${anc ? `ΔNorte ${fmtS(b.dN_km)} km, com intervalo de 95% [${fmtS(b.dN_lo)}; ${fmtS(b.dN_hi)}] que inclui o zero` : `ao norte, 1985→2024. Intervalo de 95%: [${fmtS(b.dN_lo)}; ${fmtS(b.dN_hi)}] km`}${rob ? ", robusto em todo tamanho de bloco" : ""}.</div></div>`;
      }).join("");
    })();

    // ═══════════════ Cap. 2 · posições
    (function posicoes() {
      const m = novoMapa($("#c2-mapa"));
      const dots = AMC.map((_, i) => el("circle", { cx: CX[i], cy: sy(CY[i]), fill: INK }, m.gO));
      const guia = el("g", {}, m.gT);
      let sel = AMC.findIndex((a) => a.code === 16039), encolhido = false;
      function mostra(i) {
        sel = i;
        m.polys.forEach((p, k) => { p.style.fill = k === i ? mix(ACC, 28) : ""; });
        guia.innerHTML = "";
        const k = m.kpx(), x = CX[i], y = CY[i];
        const linha = (x1, y1, x2, y2) => el("line", { x1, y1, x2, y2, stroke: ACC, "stroke-dasharray": "4 3", "vector-effect": "non-scaling-stroke" }, guia);
        linha(m.vb[0], sy(y), x, sy(y)); linha(x, sy(y), x, m.vb[1] + m.vb[3]);
        el("circle", { cx: x, cy: sy(y), r: 5 * k, fill: ACC, stroke: "#fff", "stroke-width": 1.5 * k }, guia);
        const t1 = el("text", { x: m.vb[0] + 4 * k, y: sy(y) - 5 * k, "font-size": 12 * k, fill: ACC, "font-weight": 700 }, guia); t1.textContent = `y = ${fmt(y)} km`;
        const t2 = el("text", { x: x + 5 * k, y: m.vb[1] + m.vb[3] - 5 * k, "font-size": 12 * k, fill: ACC, "font-weight": 700 }, guia); t2.textContent = `x = ${fmt(x)} km`;
        const a = AMC[i], [lo, la] = latlon(x, y);
        $("#c2-leitura").innerHTML = `<b>${a.nome}</b> · ${a.nmun === 1 ? "1 município" : `${a.nmun} municípios (${a.munis.join(", ")})`} · ${fmtI(a.area)} km².<br>
          Centroide: <b>x = ${fmt(x, 2)} km</b> e <b>y = ${fmt(y, 2)} km</b> na régua da página, ou (${fmtI(x * 1000 + D.origem_m[0])} m; ${fmtI(y * 1000 + D.origem_m[1])} m) em EPSG:5880, o que corresponde a ${fLat(la)}, ${fLon(lo)}.`;
      }
      m.polys.forEach((p, i) => {
        p.style.cursor = "pointer";
        p.addEventListener("click", () => mostra(i));
        p.addEventListener("mousemove", (ev) => mostraTip(ev, `<b>${AMC[i].nome}</b><br>${AMC[i].nmun} município(s)`));
        p.addEventListener("mouseleave", escondeTip);
      });
      const escala = (s) => m.polys.forEach((p, i) => p.setAttribute("transform", s === 1 ? "" : `translate(${CX[i]},${sy(CY[i])}) scale(${s}) translate(${-CX[i]},${-sy(CY[i])})`));
      $("#c2-encolhe").addEventListener("click", () => {
        const de = encolhido ? 0.03 : 1, ate = encolhido ? 1 : 0.03; encolhido = !encolhido;
        $("#c2-encolhe").textContent = encolhido ? "Devolver os polígonos" : "Encolher as AMC até o centroide";
        if (reduz) return escala(ate);
        const t0 = performance.now();
        (function f(t) { const u = Math.min(1, (t - t0) / 1400), e = u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2; escala(de + (ate - de) * e); if (u < 1) requestAnimationFrame(f); })(t0);
      });
      m.atualiza.push(() => { const k = m.kpx(); dots.forEach((d) => d.setAttribute("r", 2.2 * k)); mostra(sel); });
      m.atualiza.forEach((f) => f());
    })();

    // ═══════════════ Cap. 3 · pesos
    (function pesosCap() {
      const m = novoMapa($("#c3-mapa"));
      const circ = AMC.map((_, i) => el("circle", { cx: CX[i], cy: sy(CY[i]), r: 0, "fill-opacity": 0.55, "stroke-width": 1, "vector-effect": "non-scaling-stroke" }, m.gO));
      const mk = marcaCG(m.gT, 10);
      let ano = 1985, modo = "circ";
      segmento("#c3-ano", (d) => { ano = +d.a; desenha(); });
      segmento("#c3-modo", (d) => { modo = d.m; desenha(); });
      function desenha() {
        const v = S.v, w = pesos(v, ano);
        let wmx = 0, dmx = 0;
        for (const a of [1985, 2024]) pesos(v, a).forEach((x, i) => { wmx = Math.max(wmx, x); dmx = Math.max(dmx, x / AREA[i]); });
        m.polys.forEach((p, i) => { p.style.fill = modo === "dens" ? mix(COR[v], Math.round(100 * Math.sqrt(w[i] / AREA[i] / dmx))) : ""; });
        circ.forEach((c, i) => { c.setAttribute("r", modo === "circ" ? 26 * Math.sqrt(w[i] / wmx) : 0); c.setAttribute("fill", COR[v]); c.setAttribute("stroke", COR[v]); });
        const c = centro(w); poeCG(mk, m, c.x, c.y);
        const ord = w.map((x, i) => [x, i]).sort((a, b) => b[0] - a[0]).slice(0, 8), soma8 = ord.reduce((s, [x]) => s + x, 0);
        $("#c3-top").innerHTML = `<div class="linha cab"><span>As 8 AMC mais pesadas em ${ano}</span><span></span><span class="n">do total</span></div>` +
          ord.map(([x, i]) => `<div class="linha" style="--c:${COR[v]}"><span class="nm">${AMC[i].nome}</span><div class="b" style="width:${(100 * x) / ord[0][0]}%"></div><span class="n">${fmt((100 * x) / c.W)}%</span></div>`).join("");
        $("#c3-leitura").innerHTML = `${nome(v)} em ${ano}: <b>${fmtI(c.W)} ${un(v)}</b> em ${w.filter((x) => x > 0).length} AMC. As oito mais pesadas somam ${fmt((100 * soma8) / c.W)}% do total.`;
      }
      m.polys.forEach((p, i) => {
        const h = (ev) => { const w = pesos(S.v, ano)[i]; mostraTip(ev, `<b>${AMC[i].nome}</b><br>${fmtI(w)} ${un(S.v)}<br>${fmt(w / AREA[i])} por km²`); };
        p.addEventListener("mousemove", h); p.addEventListener("mouseleave", escondeTip);
        circ[i].addEventListener("mousemove", h); circ[i].addEventListener("mouseleave", escondeTip);
      });
      $("#c3-n85").textContent = pesos("agricultura", 1985).filter((x) => x > 0).length;
      m.atualiza.push(desenha); aoMudarVar(desenha); desenha();
    })();

    // ═══════════════ Cap. 4 · o equilíbrio visto de lado
    (function equilibrio() {
      const W = 760, H = 360, BX0 = 50, BX1 = 710, BEAM = 250, BIN = 10;
      const svg = d3.select("#c4-graf").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img")
        .attr("aria-label", "Régua norte–sul com o peso das AMC empilhado por faixa de 10 km, apoiada num triângulo");
      const X = d3.scaleLinear().domain([0, 800]).range([BX0, BX1]);
      const nb = 800 / BIN;
      const gRot = svg.append("g");              // tudo que inclina
      const gFant = gRot.append("g"), gBar = gRot.append("g");
      gRot.append("rect").attr("x", BX0 - 6).attr("width", BX1 - BX0 + 12).attr("y", BEAM).attr("height", 6).attr("rx", 2).attr("fill", "#5c5a54");
      const linhaCM = gRot.append("line").attr("stroke", INK).attr("stroke-dasharray", "3 3");
      const cgG = gRot.append("g");
      cgG.append("circle").attr("r", 9).attr("fill", "#fff").attr("stroke", INK).attr("stroke-width", 1.5);
      cgG.append("path").attr("d", "M0,0L9,0A9,9 0 0,0 0,-9Z M0,0L-9,0A9,9 0 0,0 0,9Z").attr("fill", INK);
      const tCM = gRot.append("text").attr("font-size", 12).attr("font-weight", 700).attr("fill", INK).attr("text-anchor", "middle");
      const apoio = svg.append("g").style("cursor", "ew-resize");
      apoio.append("path").attr("d", "M0,0 L-17,34 L17,34 Z").attr("fill", ACC);
      apoio.append("rect").attr("x", -40).attr("y", 34).attr("width", 80).attr("height", 5).attr("fill", "#b9b6ad");
      svg.append("text").attr("x", BX0).attr("y", H - 8).attr("font-size", 12).attr("font-weight", 700).attr("fill", MUTED).text("← Sul");
      svg.append("text").attr("x", BX1).attr("y", H - 8).attr("font-size", 12).attr("font-weight", 700).attr("fill", MUTED).attr("text-anchor", "end").text("Norte →");
      const eixo = svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${H - 44})`);
      const latTicks = [-19, -18, -17, -16, -15, -14, -13].map((la) => { let lo = 0, hi = 800; for (let k = 0; k < 40; k++) { const md = (lo + hi) / 2; latlon(400, md)[1] < la ? (lo = md) : (hi = md); } return [(lo + hi) / 2, la]; }).filter(([y]) => y > 5 && y < 795);
      latTicks.forEach(([y, la]) => { eixo.append("line").attr("x1", X(y)).attr("x2", X(y)).attr("y1", 0).attr("y2", 5).attr("stroke", RULE); eixo.append("text").attr("x", X(y)).attr("y", 17).attr("text-anchor", "middle").text(`${-la}°S`); });

      const st = { ano: 1985, p: null, ang: 0, alvo: 0 };
      function bins(v, ano) { const b = new Float64Array(nb); pesos(v, ano).forEach((w, i) => { if (w > 0) b[Math.min(nb - 1, Math.floor(CY[i] / BIN))] += w; }); return b; }
      let esc = 1;
      function escala() { const v = S.v; let mx = 0; for (const a of ANOS) mx = Math.max(mx, ...bins(v, a)); esc = 165 / mx; }
      const barras = (g, b, estilo) => g.selectAll("rect").data(Array.from(b)).join("rect")
        .attr("x", (_, k) => X(k * BIN) + 0.6).attr("width", X(BIN) - X(0) - 1.2).attr("y", (d) => BEAM - d * esc).attr("height", (d) => d * esc).call(estilo);
      function desenha() {
        const v = S.v, c = centro(pesos(v, st.ano));
        barras(gBar, bins(v, st.ano), (s) => s.attr("fill", COR[v]).attr("fill-opacity", 0.85).attr("stroke", "none"));
        if (st.ano !== 1985) barras(gFant, bins(v, 1985), (s) => s.attr("fill", "none").attr("stroke", INK).attr("stroke-opacity", 0.45).attr("stroke-width", 0.8));
        else gFant.selectAll("rect").remove();
        linhaCM.attr("x1", X(c.y)).attr("x2", X(c.y)).attr("y1", BEAM).attr("y2", 42);
        cgG.attr("transform", `translate(${X(c.y)},32)`); tCM.attr("x", X(c.y)).attr("y", 16).text("centro de massa");
        st.c = c; st.alvo = Math.max(-11, Math.min(11, 0.13 * (c.y - st.p)));
        leitura(); pedir();
      }
      let ag = false;
      function pedir() { if (!ag) { ag = true; requestAnimationFrame(quadro); } }
      function quadro() {
        ag = false;
        st.ang += (st.alvo - st.ang) * (reduz ? 1 : 0.14);
        const px = X(st.p);
        gRot.attr("transform", `rotate(${st.ang.toFixed(3)} ${px} ${BEAM + 6})`);
        apoio.attr("transform", `translate(${px},${BEAM + 6})`);
        if (Math.abs(st.alvo - st.ang) > 0.01) pedir();
        leitura();
      }
      function leitura() {
        const c = st.c, d = c.y - st.p, eq = Math.abs(d) < 0.5;
        const lp = latlon(c.x, st.p)[1], lc = latlon(c.x, c.y)[1];
        $("#c4-leitura").innerHTML = eq
          ? `<b>Em equilíbrio.</b> O apoio está sob o centro de massa da ${nome(S.v).toLowerCase()} de ${st.ano}, em ${fLat(lc)}. Peso total: ${fmtI(c.W)} ${un(S.v)}.`
          : `Apoio em ${fLat(lp)} e centro de massa de ${st.ano} em ${fLat(lc)}. O centro está <b>${fmt(Math.abs(d))} km ao ${d > 0 ? "norte" : "sul"}</b> do apoio, e a régua pende para o ${d > 0 ? "norte" : "sul"}.`;
      }
      function poeApoio(y) { st.p = Math.max(0, Math.min(800, y)); desenha(); }
      const noSvg = (ev) => { const r = svg.node().getBoundingClientRect(); return X.invert(((ev.clientX - r.left) / r.width) * W); };
      let arr = false;
      svg.on("pointerdown", (ev) => { arr = true; svg.node().setPointerCapture(ev.pointerId); poeApoio(noSvg(ev)); })
        .on("pointermove", (ev) => { if (arr) poeApoio(noSvg(ev)); })
        .on("pointerup pointercancel", () => { arr = false; });
      const ano = $("#c4-ano");
      ano.addEventListener("input", () => { st.ano = +ano.value; $("#c4-ano-v").textContent = st.ano; desenha(); });
      $("#c4-cm").addEventListener("click", () => poeApoio(centro(pesos(S.v, st.ano)).y));
      $("#c4-85").addEventListener("click", () => poeApoio(centro(pesos(S.v, 1985)).y));
      aoMudarVar(() => { escala(); st.p = centro(pesos(S.v, 1985)).y; desenha(); });
      escala(); st.p = centro(pesos(S.v, 1985)).y; st.ang = 0; desenha();
    })();

    // ═══════════════ Cap. 5 · a conta
    (function conta() {
      const m = novoMapa($("#c5-mapa"));
      const linhaY = el("line", { x1: m.vb[0], x2: m.vb[0] + m.vb[2], stroke: ACC, "stroke-width": 1.2, "stroke-dasharray": "6 4", "vector-effect": "non-scaling-stroke" }, m.gO);
      const trilha = el("polyline", { fill: "none", stroke: INK, "stroke-width": 1.2, opacity: 0.55, "vector-effect": "non-scaling-stroke" }, m.gO);
      const mk = marcaCG(m.gT, 10), tb = $("#c5-tb");
      let ano = 1985, ordem = [], k = 0, anim = null, linhas = [], sw = 0, swy = 0, swx = 0;
      segmento("#c5-ano", (d) => { ano = +d.a; monta(); });
      $("#c5-ordem").addEventListener("change", monta);
      function monta() {
        parar();
        const v = S.v, w = pesos(v, ano), o = $("#c5-ordem").value;
        const idx = [...Array(N).keys()].filter((i) => w[i] > 0);
        ordem = o === "sn" ? idx.sort((a, b) => CY[a] - CY[b]) : o === "peso" ? idx.sort((a, b) => w[b] - w[a]) : idx.sort((a, b) => AMC[a].code - AMC[b].code);
        tb.innerHTML = ordem.map((i) => `<tr><td>${AMC[i].nome}</td><td>${fmtI(w[i])}</td><td>${fmt(CY[i], 2)}</td><td>${fmtI(w[i] * CY[i])}</td></tr>`).join("");
        linhas = [...tb.rows]; k = 0; sw = swy = swx = 0;
        document.querySelectorAll(".c5-un").forEach((e) => (e.textContent = un(v)));
        m.polys.forEach((p) => (p.style.fill = ""));
        mk.style.display = linhaY.style.display = "none"; trilha.setAttribute("points", "");
        $("#c5-play").textContent = "Somar"; leitura();
      }
      function leitura() {
        const v = S.v, y = swy / sw, x = swx / sw, fim = k === ordem.length;
        $("#c5-formula").innerHTML = `<i>ȳ</i><sub>${ano}</sub> = <span class="frac"><span>Σ <i>w<sub>i</sub></i>·<i>y<sub>i</sub></i></span><span>Σ <i>w<sub>i</sub></i></span></span> = <span class="frac"><span class="v">${fmtI(swy)}</span><span class="v">${fmtI(sw)}</span></span> = <span class="v">${k ? fmt(y, 3) : "…"}</span> km`;
        if (!k) { $("#c5-leitura").innerHTML = `Nenhuma AMC somada ainda. ${ordem.length} AMC têm ${nome(v).toLowerCase()} em ${ano}.`; }
        else {
          mk.style.display = linhaY.style.display = ""; poeCG(mk, m, x, y);
          linhaY.setAttribute("y1", sy(y)); linhaY.setAttribute("y2", sy(y));
          const ofi = D.oficial.anual[v].y[iA(ano)];
          $("#c5-leitura").innerHTML = fim
            ? `Conta completa com <b>${k} AMC</b>: <i>ȳ</i> = <b>${fmt(y, 3)} km</b> na régua da página, ou <b>${fmt(y + Y0, 3)} km</b> em EPSG:5880, que é ${fLat(latlon(x, y)[1])}. O arquivo do pipeline (<code>centro_massa_anual.csv</code>) traz <b>${fmt(ofi + Y0, 3)} km</b>. A mesma conta feita para <i>x</i> dá <i>x̄</i> = ${fmt(x, 3)} km.`
            : `${k} de ${ordem.length} AMC somadas. A última a entrar foi <b>${AMC[ordem[k - 1]].nome}</b>, e o centro parcial está em <i>y</i> = ${fmt(y, 2)} km.`;
        }
        linhas.forEach((r, j) => (r.className = j < k - 1 ? "feita" : j === k - 1 ? "agora" : ""));
      }
      function passo(rola) {
        const w = pesos(S.v, ano), i = ordem[k]; k++;
        sw += w[i]; swy += w[i] * CY[i]; swx += w[i] * CX[i];
        m.polys[i].style.fill = mix(COR[S.v], 50);
        trilha.setAttribute("points", (trilha.getAttribute("points") || "") + ` ${swx / sw},${sy(swy / sw)}`);
        if (rola) { const r = linhas[k - 1], box = r.closest(".mt-razao"); box.scrollTop = r.offsetTop - box.clientHeight / 2; }
      }
      function parar() { if (anim) cancelAnimationFrame(anim); anim = null; $("#c5-play").textContent = k && k < ordem.length ? "Continuar" : "Somar"; }
      $("#c5-play").addEventListener("click", () => {
        if (anim) return parar();
        if (k >= ordem.length) monta();
        $("#c5-play").textContent = "Pausar";
        let t0 = 0;
        const f = (t) => { if (t - t0 > 55) { t0 = t; passo(true); leitura(); } if (k < ordem.length) anim = requestAnimationFrame(f); else { anim = null; $("#c5-play").textContent = "Somar de novo"; } };
        anim = requestAnimationFrame(f);
      });
      $("#c5-fim").addEventListener("click", () => { parar(); while (k < ordem.length) passo(false); leitura(); $("#c5-play").textContent = "Somar de novo"; });
      m.atualiza.push(() => { if (k) poeCG(mk, m, mk._x, mk._y); });
      aoMudarVar(monta); monta();
    })();

    // ═══════════════ Cap. 6 · no tempo
    (function tempo() {
      const cent = {}; const xs = [], ys = [];
      for (const v of VARS) { cent[v] = ANOS.map((a) => centro(pesos(v, a))); cent[v].forEach((c) => { xs.push(c.x); ys.push(c.y); }); }
      const x0 = Math.min(...xs) - 70, x1 = Math.max(...xs) + 110, y0 = Math.min(...ys) - 40, y1 = Math.max(...ys) + 40;
      const m = novoMapa($("#c6-mapa"), { vb: [x0, sy(y1), x1 - x0, y1 - y0], rotulo: "Trajetória anual dos quatro centros de massa, 1985 a 2024" });
      m.polys.forEach((p) => (p.style.fill = "#fbfaf7"));
      const gL = el("g", {}, m.gO), gM = el("g", {}, m.gT), barra = el("g", {}, m.gT);
      const tr = {};
      for (const v of VARS) tr[v] = {
        lin: el("polyline", { fill: "none", stroke: COR[v], "stroke-linejoin": "round", "vector-effect": "non-scaling-stroke" }, gL),
        ini: el("circle", { fill: "#fff", stroke: COR[v], "stroke-width": 2, "vector-effect": "non-scaling-stroke" }, gL),
        cg: marcaCG(gM, 8), rot: el("text", { fill: COR[v], "font-weight": 700 }, gM),
      };
      let ano = 2024, anim = null;
      const slider = $("#c6-ano");
      slider.addEventListener("input", () => { ano = +slider.value; desenha(); });
      $("#c6-play").addEventListener("click", () => {
        if (anim) { cancelAnimationFrame(anim); anim = null; $("#c6-play").textContent = "Tocar 1985 → 2024"; return; }
        ano = 1985; slider.value = ano; desenha(); $("#c6-play").textContent = "Pausar";
        let t0 = 0;
        const f = (t) => { if (t - t0 > 160) { t0 = t; ano++; slider.value = ano; desenha(); } if (ano < 2024) anim = requestAnimationFrame(f); else { anim = null; $("#c6-play").textContent = "Tocar 1985 → 2024"; } };
        anim = requestAnimationFrame(f);
      });
      $("#c6-leg").innerHTML = VARS.map((v) => `<span style="--c:${COR[v]}"><i></i>${nome(v)}</span>`).join("");
      // série de latitude
      const G = (function () {
        const W = 760, H = 240, mg = { l: 62, r: 16, t: 18, b: 26 };
        const svg = d3.select("#c6-graf").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${H}`).style("border-top", "1px solid #efece4");
        const x = d3.scaleLinear().domain([1985, 2024]).range([mg.l, W - mg.r]);
        const y = d3.scaleLinear().domain([Math.min(...ys) - 6, Math.max(...ys) + 6]).range([H - mg.b, mg.t]);
        D.atos.forEach((a, j) => {
          if (j % 2 === 0) svg.append("rect").attr("class", "mt-ato").attr("x", x(a.ini - 0.5)).attr("width", x(a.fim + 0.5) - x(a.ini - 0.5)).attr("y", mg.t).attr("height", H - mg.t - mg.b);
          svg.append("text").attr("class", "mt-ato-t").attr("x", x((a.ini + a.fim) / 2)).attr("y", mg.t + 12).attr("text-anchor", "middle").text("Ato " + a.id);
        });
        svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${H - mg.b})`).call(d3.axisBottom(x).tickFormat(d3.format("d")).ticks(8));
        svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(${mg.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat((d) => fLat(latlon(400, d)[1])));
        const lin = {};
        for (const v of VARS) lin[v] = svg.append("path").attr("fill", "none").attr("stroke", COR[v]).attr("d", d3.line().x((_, i) => x(ANOS[i])).y((c) => y(c.y))(cent[v]));
        const reg = svg.append("line").attr("stroke", INK).attr("stroke-dasharray", "2 3").attr("y1", mg.t).attr("y2", H - mg.b);
        return { marca(a) { reg.attr("x1", x(a)).attr("x2", x(a)); for (const v of VARS) lin[v].attr("stroke-width", v === S.v ? 2.6 : 1.2).attr("opacity", v === S.v ? 1 : 0.45); } };
      })();
      function desenha() {
        $("#c6-ano-v").textContent = ano;
        const k = m.kpx(), n = iA(ano) + 1;
        for (const v of VARS) {
          const t = tr[v], c = cent[v], on = v === S.v, p = c[n - 1];
          t.lin.setAttribute("points", c.slice(0, n).map((q) => `${q.x},${sy(q.y)}`).join(" "));
          t.lin.setAttribute("stroke-width", on ? 2.6 : 1.3); t.lin.setAttribute("opacity", on ? 1 : 0.5);
          t.ini.setAttribute("cx", c[0].x); t.ini.setAttribute("cy", sy(c[0].y)); t.ini.setAttribute("r", 4 * k);
          poeCG(t.cg, m, p.x, p.y, on ? 9 : 6); t.cg.setAttribute("opacity", on ? 1 : 0.6);
          t.rot.setAttribute("x", p.x + 11 * k); t.rot.setAttribute("y", sy(p.y) + 4 * k); t.rot.setAttribute("font-size", (on ? 13 : 11) * k); t.rot.textContent = nome(v);
        }
        barra.innerHTML = "";
        const bx = x0 + 14 * k, by = m.vb[1] + m.vb[3] - 14 * k;
        el("line", { x1: bx, x2: bx + 20, y1: by, y2: by, stroke: INK, "stroke-width": 2, "vector-effect": "non-scaling-stroke" }, barra);
        const tt = el("text", { x: bx, y: by - 5 * k, "font-size": 11 * k, fill: MUTED }, barra); tt.textContent = "20 km";
        const v = S.v, a = cent[v][0], b = cent[v][iA(ano)];
        $("#c6-leitura").innerHTML = `${nome(v)}, 1985 → ${ano}: o centro andou <b>${fmtS(b.y - a.y)} km</b> na direção norte e <b>${fmtS(b.x - a.x)} km</b> na direção leste.`;
        G.marca(ano);
      }
      function tabela() {
        const v = S.v, boot = D.oficial.boot.filter((r) => r.variavel === v);
        const rot = (r) => (r.ato === "LÍQUIDO" ? "1985–2024 (líquido)" : "Ato " + r.ato.split(" ")[0]);
        const jan = (r) => (r.ato === "LÍQUIDO" ? "LÍQUIDO" : "Ato " + r.ato.split(" ")[0]);
        const linhas = D.oficial.desloc.filter((r) => r.variavel === v).map((r) => {
          const b = boot.find((q) => q.janela === jan(r)), aq = cent[v][iA(r.ano_fim)].y - cent[v][iA(r.ano_ini)].y;
          const ic = b ? `[${fmtS(b.dN_lo)}; ${fmtS(b.dN_hi)}]` : "", zero = b && !b.exclui_zero;
          return `<tr class="${r.ato === "LÍQUIDO" ? "forte" : ""}"><td>${rot(r)}</td><td class="num">${r.ano_ini}–${r.ano_fim}</td><td class="num">${fmtS(r.dnorte_km)}</td><td class="num">${ic}${zero ? " · inclui zero" : ""}</td><td class="num">${fmtS(aq)}</td></tr>`;
        }).join("");
        $("#c6-tab").innerHTML = `<table class="tabela-dados"><thead><tr><th>${nome(v)}</th><th class="num">anos</th><th class="num">ΔNorte do pipeline (km)</th><th class="num">IC 95%</th><th class="num">refeito aqui (km)</th></tr></thead><tbody>${linhas}</tbody></table>
          <p class="tabela-nota">ΔNorte de <code>centro_massa_deslocamento.csv</code> e intervalo de <code>centro_massa_bootstrap.csv</code> (Pipeline #32, sorteio AMC a AMC). A última coluna é a conta desta página.</p>`;
      }
      m.atualiza.push(desenha);
      aoMudarVar(() => { desenha(); tabela(); }); desenha(); tabela();
    })();

    // ═══════════════ Cap. 7 · decomposição
    (function decomp() {
      const sa = $("#c7-a"), sb = $("#c7-b");
      ANOS.forEach((a) => { sa.add(new Option(a, a)); sb.add(new Option(a, a)); }); sa.value = 1985; sb.value = 2024;
      const m = novoMapa($("#c7-mapa"));
      const linha = el("line", { x1: m.vb[0], x2: m.vb[0] + m.vb[2], stroke: INK, "stroke-width": 1.2, "stroke-dasharray": "6 4", "vector-effect": "non-scaling-stroke" }, m.gO);
      const tl = el("text", { "text-anchor": "end", fill: INK, "font-weight": 700 }, m.gO);
      const mk0 = marcaCG(m.gT, 7), mk1 = marcaCG(m.gT, 9);
      let contrib = [];
      function calcula() {
        const v = S.v, a = +sa.value, b = +sb.value, wa = pesos(v, a), wb = pesos(v, b), ca = centro(wa), cb = centro(wb);
        contrib = AMC.map((_, i) => (wb[i] / cb.W - wa[i] / ca.W) * (CY[i] - ca.y));
        const mx = Math.max(...contrib.map(Math.abs)) || 1;
        m.polys.forEach((p, i) => { const c = contrib[i]; p.style.fill = mix(c >= 0 ? NORTE : SUL, Math.round(100 * Math.sqrt(Math.abs(c) / mx))); });
        const k = m.kpx();
        linha.setAttribute("y1", sy(ca.y)); linha.setAttribute("y2", sy(ca.y));
        tl.setAttribute("x", m.vb[0] + m.vb[2] - 8 * k); tl.setAttribute("y", sy(ca.y) - 6 * k); tl.setAttribute("font-size", 12 * k); tl.textContent = `linha do centro de ${a}`;
        poeCG(mk0, m, ca.x, ca.y); mk0.setAttribute("opacity", 0.5); poeCG(mk1, m, cb.x, cb.y);
        const bal = { ng: 0, sp: 0, np: 0, sg: 0 };
        contrib.forEach((c, i) => { const norte = CY[i] > ca.y, ganhou = wb[i] / cb.W > wa[i] / ca.W; bal[norte ? (ganhou ? "ng" : "np") : ganhou ? "sg" : "sp"] += c; });
        const tot = contrib.reduce((s, c) => s + c, 0);
        cascata(bal, tot, a, b);
        const top = contrib.map((c, i) => [c, i]).sort((p, q) => Math.abs(q[0]) - Math.abs(p[0])).slice(0, 8), mt = Math.abs(top[0][0]) || 1;
        $("#c7-top").innerHTML = `<div class="linha cab"><span>As 8 maiores parcelas</span><span></span><span class="n">km</span></div>` +
          top.map(([c, i]) => `<div class="linha" style="--c:${c >= 0 ? NORTE : SUL}"><span class="nm">${AMC[i].nome}</span><div class="b" style="width:${(100 * Math.abs(c)) / mt}%"></div><span class="n">${fmtS(c)}</span></div>`).join("");
        $("#c7-leitura").innerHTML = `As 166 parcelas somam <b>${fmtS(tot, 3)} km</b>. O deslocamento calculado direto, <i>ȳ</i><sub>${b}</sub> − <i>ȳ</i><sub>${a}</sub>, é <b>${fmtS(cb.y - ca.y, 3)} km</b>. No mapa, azul empurra o centro para o norte e laranja para o sul, e a cor mais forte marca a parcela maior.`;
      }
      function cascata(bal, tot, a, b) {
        const itens = [["O norte ganhou participação", bal.ng, NORTE], ["O sul perdeu participação", bal.sp, NORTE], ["O norte perdeu participação", bal.np, SUL], ["O sul ganhou participação", bal.sg, SUL]];
        const W = 760, H = 190, mg = { l: 210, r: 70, t: 12, b: 24 }, rh = (H - mg.t - mg.b) / 5;
        let acc = 0; const seg = itens.map(([n, v, c]) => { const s = { n, v, c, a: acc, b: acc + v }; acc += v; return s; });
        const lo = Math.min(0, ...seg.map((s) => Math.min(s.a, s.b)), tot), hi = Math.max(0, ...seg.map((s) => Math.max(s.a, s.b)), tot);
        const x = d3.scaleLinear().domain([lo - 2, hi + 2]).range([mg.l, W - mg.r]);
        const svg = d3.select("#c7-cascata").html("").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${H}`);
        svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", mg.t).attr("y2", H - mg.b).attr("stroke", "#b9b6ad");
        const lin = (j, x0, x1, cor, rot, val, forte) => {
          const yy = mg.t + j * rh;
          svg.append("rect").attr("x", x(Math.min(x0, x1))).attr("width", Math.max(1, Math.abs(x(x1) - x(x0)))).attr("y", yy + 5).attr("height", rh - 10).attr("fill", cor);
          svg.append("text").attr("x", mg.l - 10).attr("y", yy + rh / 2 + 4).attr("text-anchor", "end").attr("font-size", 13).attr("font-weight", forte ? 700 : 400).attr("fill", INK).text(rot);
          svg.append("text").attr("x", x(Math.max(x0, x1)) + 6).attr("y", yy + rh / 2 + 4).attr("font-size", 12).attr("font-weight", forte ? 700 : 400).attr("fill", forte ? INK : MUTED).text(fmtS(val) + " km");
        };
        seg.forEach((s, j) => lin(j, s.a, s.b, s.c, s.n, s.v, false));
        lin(4, 0, tot, INK, `ΔNorte ${a} → ${b}`, tot, true);
        svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${H - mg.b})`).call(d3.axisBottom(x).ticks(6).tickFormat((d) => fmt(d, 0)));
      }
      m.polys.forEach((p, i) => { p.addEventListener("mousemove", (ev) => mostraTip(ev, `<b>${AMC[i].nome}</b><br>parcela: ${fmtS(contrib[i], 2)} km`)); p.addEventListener("mouseleave", escondeTip); });
      sa.addEventListener("change", calcula); sb.addEventListener("change", calcula);
      m.atualiza.push(calcula); aoMudarVar(calcula); calcula();
    })();

    // ═══════════════ Cap. 8 · mediano
    (function mediano() {
      const box = $("#c8-mapa");
      let m, ano = 1985, passos = [], k = 0, base, anim = null;
      const mult = new Float64Array(N).fill(1);
      const pesosM = () => pesos(S.v, ano).map((w, i) => w * mult[i]);
      let dots, trilha, gTr, mkMean, mkMean0, mkMed, mkMed0;
      function monta() {
        box.innerHTML = ""; mult.fill(1);
        const w = pesos(S.v, ano), c = centro(w), med = weiszfeld(w).at(-1);
        const cx = (c.x + med[0]) / 2, cy = (c.y + med[1]) / 2, R = 200;
        m = novoMapa(box, { vb: [cx - R, sy(cy + R * 0.75), 2 * R, 1.5 * R], rotulo: "Centro médio e centro mediano, com as AMC como círculos proporcionais ao peso" });
        m.polys.forEach((p, i) => { p.style.fill = "#fbfaf7"; p.style.cursor = "pointer"; p.addEventListener("click", () => infla(i)); });
        const gD = el("g", {}, m.gO), gC = el("g", {}, m.gT);
        dots = AMC.map((_, i) => {
          const d = el("circle", { cx: CX[i], cy: sy(CY[i]), fill: COR[S.v], "fill-opacity": 0.45, stroke: COR[S.v], "vector-effect": "non-scaling-stroke" }, gD);
          d.style.cursor = "pointer"; d.addEventListener("click", () => infla(i));
          d.addEventListener("mousemove", (ev) => mostraTip(ev, `<b>${AMC[i].nome}</b><br>${fmtI(pesos(S.v, ano)[i] * mult[i])} ${un(S.v)}${mult[i] > 1 ? " (×10)" : ""}<br>clique para ${mult[i] > 1 ? "voltar ao peso real" : "multiplicar por 10"}`));
          d.addEventListener("mouseleave", escondeTip); return d;
        });
        trilha = el("polyline", { fill: "none", stroke: ACC, "stroke-width": 1.5, "vector-effect": "non-scaling-stroke" }, gC);
        gTr = el("g", {}, gC);
        mkMean0 = marcaCG(gC, 7); mkMean0.setAttribute("opacity", 0.3);
        mkMed0 = el("rect", { fill: "none", stroke: ACC, "stroke-width": 1.5, opacity: 0.45, "vector-effect": "non-scaling-stroke" }, gC);
        mkMean = marcaCG(gC, 10);
        mkMed = el("rect", { fill: ACC, stroke: "#fff", "stroke-width": 1.5, "vector-effect": "non-scaling-stroke" }, gC);
        base = { mean: c, med };
        m.atualiza.push(desenha);
        zera();
      }
      function zera() { passos = weiszfeld(pesosM()); k = 0; desenha(); }
      function infla(i) { mult[i] = mult[i] > 1 ? 1 : 10; zera(); corre(); }
      function losango(r, x, y, s) { r.setAttribute("x", x - s); r.setAttribute("y", sy(y) - s); r.setAttribute("width", 2 * s); r.setAttribute("height", 2 * s); r.setAttribute("transform", `rotate(45 ${x} ${sy(y)})`); }
      function desenha() {
        const kk = m.kpx(), w = pesosM(), mx = Math.max(...pesos(S.v, ano));
        dots.forEach((d, i) => { d.setAttribute("r", Math.max(1.3 * kk, 17 * kk * Math.sqrt(w[i] / mx))); d.setAttribute("stroke-width", mult[i] > 1 ? 2.5 : 0.8); d.setAttribute("stroke", mult[i] > 1 ? INK : COR[S.v]); });
        const vis = passos.slice(0, k + 1);
        trilha.setAttribute("points", vis.map(([x, y]) => `${x},${sy(y)}`).join(" "));
        gTr.innerHTML = ""; vis.forEach(([x, y]) => el("circle", { cx: x, cy: sy(y), r: 1.8 * kk, fill: ACC }, gTr));
        const c = centro(w); poeCG(mkMean, m, c.x, c.y);
        const alterado = mult.some((x) => x > 1);
        mkMean0.style.display = mkMed0.style.display = alterado ? "" : "none";
        poeCG(mkMean0, m, base.mean.x, base.mean.y); losango(mkMed0, base.med[0], base.med[1], 5 * kk);
        const [qx, qy] = passos[k]; losango(mkMed, qx, qy, 6 * kk);
        const fim = k === passos.length - 1;
        const mov = k ? Math.hypot(passos[k][0] - passos[k - 1][0], passos[k][1] - passos[k - 1][1]) : 0;
        const fmov = mov < 0.001 ? "menos de 1 m" : mov < 1 ? fmt(mov * 1000, 0) + " m" : fmt(mov, 1) + " km";
        const dm = Math.hypot(c.x - base.mean.x, c.y - base.mean.y), dd = Math.hypot(passos.at(-1)[0] - base.med[0], passos.at(-1)[1] - base.med[1]);
        $("#c8-leitura").innerHTML = `Passo <b>${k}</b> de ${passos.length - 1}${k ? `, e o último moveu o ponto ${fmov}` : ". O ponto de partida é o próprio centro médio"}.` +
          (fim ? ` Convergiu: o mediano de ${ano} está a <b>${fmt(Math.hypot(qx - c.x, qy - c.y))} km</b> do médio.` : "") +
          (alterado && fim ? `<br>Com o peso inflado, o <b>centro médio andou ${fmt(dm)} km</b> e o <b>mediano andou ${fmt(dd)} km</b>.` : "");
      }
      function corre() {
        if (anim) clearTimeout(anim);
        if (reduz) { k = passos.length - 1; return desenha(); }
        const f = () => { if (k < passos.length - 1) { k++; desenha(); anim = setTimeout(f, 70); } };
        f();
      }
      segmento("#c8-ano", (d) => { ano = +d.a; monta(); });
      $("#c8-passo").addEventListener("click", () => { if (k < passos.length - 1) { k++; desenha(); } });
      $("#c8-tudo").addEventListener("click", corre);
      $("#c8-zera").addEventListener("click", () => { mult.fill(1); zera(); });
      aoMudarVar(monta); monta();
    })();

    // ═══════════════ Cap. 9 · bootstrap
    (function bootstrap() {
      const selK = $("#c9-k"), B = 2000;
      const KS = Object.keys(D.blocos).map(Number).sort((a, b) => b - a);
      KS.forEach((k) => selK.add(new Option(k === 166 ? "AMC a AMC (166 unidades)" : `${k} blocos (~${fmt(166 / k, 1)} AMC cada)`, k)));
      const m = novoMapa($("#c9-mapa"));
      const gRot = el("g", {}, m.gT);
      let K = 166, lab = D.blocos["166"], rng, amostra, ultimo, anim = null;
      const dN = (c) => centro(pesos(S.v, 2024), c).y - centro(pesos(S.v, 1985), c).y;
      function sorteia() {
        const cb = new Float64Array(K); for (let t = 0; t < K; t++) cb[Math.floor(rng() * K)]++;
        const c = new Float64Array(N); for (let i = 0; i < N; i++) c[i] = cb[lab[i]]; return c;
      }
      // partição em blocos: 4 tons neutros, vizinhos com tons diferentes (coloração gulosa)
      function mostraBlocos() {
        gRot.innerHTML = "";
        if (K === 166) { m.polys.forEach((p) => (p.style.fill = "")); return; }
        const tons = ["#ebe8df", "#d6d2c6", "#f6f4ee", "#c4bfb1"], cen = [];
        for (let b = 0; b < K; b++) { let sx = 0, s_y = 0, n = 0; lab.forEach((l, i) => { if (l === b) { sx += CX[i]; s_y += CY[i]; n++; } }); cen.push([sx / n, s_y / n]); }
        const lim = 2.2 * Math.sqrt(340000 / K / Math.PI), cb = new Array(K).fill(-1);
        [...Array(K).keys()].sort((a, b) => cen[a][1] - cen[b][1]).forEach((b) => {
          const us = new Set(); for (let o = 0; o < K; o++) if (cb[o] >= 0 && Math.hypot(cen[o][0] - cen[b][0], cen[o][1] - cen[b][1]) < lim) us.add(cb[o]);
          let c = 0; while (us.has(c) && c < 3) c++; cb[b] = c;
        });
        m.polys.forEach((p, i) => (p.style.fill = tons[cb[lab[i]]]));
      }
      function pinta(c) {
        m.polys.forEach((p, i) => (p.style.fill = c[i] === 0 ? "#ffffff" : mix(COR[S.v], Math.min(90, 24 * c[i] + 10))));
        gRot.innerHTML = ""; const k = m.kpx();
        for (let i = 0; i < N; i++) if (c[i] >= 2) { const t = el("text", { x: CX[i], y: sy(CY[i]) + 4 * k, "text-anchor": "middle", "font-size": 11 * k, "font-weight": 700, fill: INK }, gRot); t.textContent = "×" + c[i]; }
      }
      const ic = () => { const s = [...amostra].sort((a, b) => a - b); return [d3.quantileSorted(s, 0.025), d3.quantileSorted(s, 0.975)]; };
      const H = (function () {
        const W = 760, Hh = 210, mg = { l: 44, r: 16, t: 16, b: 28 };
        const svg = d3.select("#c9-hist").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${Hh}`);
        const gB = svg.append("g"), gE = svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${Hh - mg.b})`), gL = svg.append("g");
        return function () {
          const v = S.v, bl = D.oficial.bloco.filter((r) => r.variavel === v);
          const x = d3.scaleLinear().domain([Math.min(-10, ...bl.map((r) => r.dN_lo)) - 6, Math.max(10, ...bl.map((r) => r.dN_hi)) + 6]).range([mg.l, W - mg.r]);
          const bins = d3.bin().domain(x.domain()).thresholds(x.ticks(60))(amostra);
          const y = d3.scaleLinear().domain([0, Math.max(5, d3.max(bins, (b) => b.length))]).range([Hh - mg.b, mg.t]);
          gB.selectAll("rect").data(bins).join("rect").attr("x", (b) => x(b.x0) + 0.5).attr("width", (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr("y", (b) => y(b.length)).attr("height", (b) => y(0) - y(b.length)).attr("fill", COR[v]).attr("opacity", 0.85);
          gE.call(d3.axisBottom(x).ticks(8).tickFormat((d) => fmt(d, 0) + " km"));
          gL.html("");
          const lin = (val, cor, w, das, txt, yy) => {
            gL.append("line").attr("x1", x(val)).attr("x2", x(val)).attr("y1", mg.t).attr("y2", Hh - mg.b).attr("stroke", cor).attr("stroke-width", w).attr("stroke-dasharray", das);
            if (txt) gL.append("text").attr("x", x(val) + 4).attr("y", yy).attr("fill", cor).attr("font-size", 11).attr("font-weight", 700).text(txt);
          };
          lin(0, "#8a8a82", 1, null, "zero", mg.t + 10);
          const pt = dN(null); lin(pt, INK, 2, null, `ΔNorte = ${fmtS(pt)} km`, mg.t + 24);
          if (ultimo !== null) gL.append("circle").attr("cx", x(ultimo)).attr("cy", Hh - mg.b - 6).attr("r", 5).attr("fill", ACC);
          if (amostra.length >= 40) { const [a, b] = ic(); lin(a, ACC, 1.5, "4 3"); lin(b, ACC, 1.5, "4 3"); gL.append("text").attr("x", (x(a) + x(b)) / 2).attr("y", Hh - mg.b - 16).attr("text-anchor", "middle").attr("fill", ACC).attr("font-size", 11).attr("font-weight", 700).text("95% do meio"); }
        };
      })();
      const selo = (lo, hi) => (lo > 0 || hi < 0 ? '<span class="selo rob">exclui o zero · robusto</span>' : '<span class="selo anc">inclui o zero · ancorada</span>');
      function placar() {
        const v = S.v, of = D.oficial.bloco.find((r) => r.variavel === v && r.k_blocos === K), ofB = D.oficial.boot.find((r) => r.variavel === v && r.janela === "LÍQUIDO");
        const ok = amostra.length >= 40, [a, b] = ok ? ic() : [NaN, NaN];
        $("#c9-ic").innerHTML = `<div><div class="k">Esta página · ${fmtI(amostra.length)} sorteios</div><div class="v">${ok ? `[${fmtS(a)}; ${fmtS(b)}] km` : "sorteie ao menos 40"}</div>${ok ? selo(a, b) : ""}</div>
          <div><div class="k">Pipeline #55 · 2.000 sorteios</div><div class="v">[${fmtS(of.dN_lo)}; ${fmtS(of.dN_hi)}] km</div>${selo(of.dN_lo, of.dN_hi)}
          ${K === 166 ? `<div class="s">O Pipeline #32, com outro sorteio, traz [${fmtS(ofB.dN_lo)}; ${fmtS(ofB.dN_hi)}]. A diferença entre dois sorteios é o ruído do próprio sorteio.</div>` : ""}</div>`;
        $("#c9-leitura").innerHTML = ultimo === null
          ? `Cada sorteio monta um Goiás novo e refaz as contas de 1985 e de 2024. ${K < 166 ? "O mapa mostra a partição em blocos: AMC de mesmo tom vizinhas pertencem ao mesmo bloco e entram ou saem juntas. " : ""}Comece com <b>1 sorteio</b> para ver quais AMC entraram.`
          : `Último sorteio: ΔNorte = <b>${fmtS(ultimo)} km</b>. No mapa, as AMC em branco ficaram de fora, e ×2, ×3 marcam as que entraram repetidas${K < 166 ? ", sempre com o bloco inteiro" : ""}.`;
      }
      function grade() {
        const v = S.v, bl = D.oficial.bloco.filter((r) => r.variavel === v).sort((a, b) => b.k_blocos - a.k_blocos);
        const W = 760, Hh = 170, mg = { l: 150, r: 20, t: 28, b: 26 };
        const x = d3.scaleLinear().domain([Math.min(-10, ...bl.map((r) => r.dN_lo)) - 4, Math.max(10, ...bl.map((r) => r.dN_hi)) + 4]).range([mg.l, W - mg.r]);
        const y = d3.scalePoint().domain(bl.map((r) => r.k_blocos)).range([mg.t + 4, Hh - mg.b - 6]);
        const svg = d3.select("#c9-grade").html("").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${Hh}`);
        svg.append("text").attr("x", 14).attr("y", 17).attr("font-size", 12).attr("font-weight", 700).attr("fill", MUTED).text("Intervalo de 95% do Pipeline #55 em cada tamanho de bloco");
        svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", mg.t - 4).attr("y2", Hh - mg.b).attr("stroke", "#8a8a82").attr("stroke-dasharray", "2 3");
        bl.forEach((r) => {
          const yy = y(r.k_blocos), on = r.k_blocos === K;
          svg.append("line").attr("x1", x(r.dN_lo)).attr("x2", x(r.dN_hi)).attr("y1", yy).attr("y2", yy).attr("stroke", COR[v]).attr("stroke-width", on ? 6 : 3).attr("opacity", on ? 1 : 0.5);
          svg.append("circle").attr("cx", x(r.dN_km)).attr("cy", yy).attr("r", 3.5).attr("fill", INK);
          svg.append("text").attr("x", mg.l - 10).attr("y", yy + 4).attr("text-anchor", "end").attr("font-size", 11.5).attr("font-weight", on ? 700 : 400).attr("fill", on ? INK : MUTED).text(r.k_blocos === 166 ? "1 AMC por bloco" : `~${fmt(r.amc_por_bloco, 1)} AMC por bloco`);
        });
        svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${Hh - mg.b})`).call(d3.axisBottom(x).ticks(7).tickFormat((d) => fmt(d, 0) + " km"));
      }
      function zera() { if (anim) cancelAnimationFrame(anim); anim = null; rng = mulberry(42); amostra = []; ultimo = null; mostraBlocos(); H(); placar(); grade(); }
      function lote(n) { let c = null; for (let j = 0; j < n && amostra.length < B; j++) { c = sorteia(); ultimo = dN(c); amostra.push(ultimo); } if (c) pinta(c); H(); placar(); }
      selK.addEventListener("change", () => { K = +selK.value; lab = D.blocos[String(K)]; zera(); });
      $("#c9-1").addEventListener("click", () => lote(1));
      $("#c9-100").addEventListener("click", () => lote(100));
      $("#c9-tudo").addEventListener("click", () => { if (reduz) return lote(B); const f = () => { lote(50); if (amostra.length < B) anim = requestAnimationFrame(f); else anim = null; }; f(); });
      $("#c9-zera").addEventListener("click", zera);
      aoMudarVar(zera); zera();
    })();

    // ═══════════════ Cap. 10 · pixel
    (function pixel() {
      const vs = ["pastagem", "agricultura", "veg_natural"], ser = {};
      let lo = 0, hi = 0;
      for (const v of vs) {
        const amc = ANOS.map((a) => centro(pesos(v, a)).y), px = D.oficial.pixel[v];
        ser[v] = { amc: amc.map((y) => y - amc[0]), px: px.y.map((y) => y - px.y[0]), anos: px.ano };
        lo = Math.min(lo, ...ser[v].amc, ...ser[v].px); hi = Math.max(hi, ...ser[v].amc, ...ser[v].px);
      }
      const W = 760, Hh = 320, mg = { l: 50, r: 16, t: 18, b: 28 };
      const svg = d3.select("#c10-graf").append("svg").attr("class", "mt-graf").attr("viewBox", `0 0 ${W} ${Hh}`).attr("role", "img").attr("aria-label", "Deslocamento norte acumulado desde 1985, calculado sobre as AMC e pixel a pixel");
      const x = d3.scaleLinear().domain([1985, 2024]).range([mg.l, W - mg.r]), y = d3.scaleLinear().domain([lo - 4, hi + 4]).range([Hh - mg.b, mg.t]);
      D.atos.forEach((a, j) => { if (j % 2 === 0) svg.append("rect").attr("class", "mt-ato").attr("x", x(a.ini - 0.5)).attr("width", x(a.fim + 0.5) - x(a.ini - 0.5)).attr("y", mg.t).attr("height", Hh - mg.t - mg.b); });
      svg.append("line").attr("x1", mg.l).attr("x2", W - mg.r).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", "#b9b6ad");
      svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(0,${Hh - mg.b})`).call(d3.axisBottom(x).tickFormat(d3.format("d")).ticks(8));
      svg.append("g").attr("class", "mt-eixo").attr("transform", `translate(${mg.l},0)`).call(d3.axisLeft(y).ticks(6).tickFormat((d) => fmt(d, 0)));
      svg.append("text").attr("x", mg.l + 8).attr("y", mg.t + 10).attr("font-size", 11).attr("fill", MUTED).text("km ao norte da posição de 1985");
      const L = {};
      for (const v of vs) L[v] = [
        svg.append("path").attr("fill", "none").attr("stroke", COR[v]).attr("stroke-width", 2.2).attr("d", d3.line().x((_, i) => x(ANOS[i])).y((d) => y(d))(ser[v].amc)),
        svg.append("path").attr("fill", "none").attr("stroke", COR[v]).attr("stroke-width", 2.2).attr("stroke-dasharray", "5 4").attr("d", d3.line().x((_, i) => x(ser[v].anos[i])).y((d) => y(d))(ser[v].px)),
      ];
      $("#c10-leg").innerHTML = vs.map((v) => `<span style="--c:${COR[v]}"><i></i>${nome(v)}, sobre as AMC</span><span style="--c:${COR[v]}"><i class="tr"></i>pixel a pixel</span>`).join("");
      $("#c10-tab").innerHTML = `<table class="tabela-dados"><thead><tr><th>1985 → 2024</th><th class="num">ΔNorte sobre as AMC</th><th class="num">ΔNorte pixel a pixel</th><th class="num">diferença</th></tr></thead><tbody>` +
        vs.map((v) => { const a = ser[v].amc.at(-1), p = ser[v].px.at(-1); return `<tr><td>${nome(v)}</td><td class="num">${fmtS(a)} km</td><td class="num">${fmtS(p)} km</td><td class="num">${fmtS(p - a)} km</td></tr>`; }).join("") + "</tbody></table>";
      $("#c10-regua").innerHTML = `As duas colunas estão na mesma régua, a posição norte em EPSG:5880. Em outras partes do site o teste do pixel aparece como pastagem +79,2&nbsp;km e agricultura +66,9&nbsp;km. Esses valores vêm da diferença de latitude convertida a 111&nbsp;km por grau, que é uma régua um pouco diferente. Medido na mesma régua das AMC, o pixel dá ${fmtS(ser.pastagem.px.at(-1))} e ${fmtS(ser.agricultura.px.at(-1))}&nbsp;km. A conclusão é a mesma, e a distância entre as duas medições fica ainda menor.`;
      aoMudarVar(() => { for (const v of vs) L[v].forEach((p) => p.attr("opacity", !vs.includes(S.v) || S.v === v ? 1 : 0.3)); });
    })();

    // ═══════════════ conferência contra o CSV oficial
    (function confere() {
      let pior = 0;
      for (const v of VARS) ANOS.forEach((a, j) => { const c = centro(pesos(v, a)); pior = Math.max(pior, Math.abs(c.y - D.oficial.anual[v].y[j]), Math.abs(c.x - D.oficial.anual[v].x[j])); });
      const t = `${fmt(pior * 1000, 1)} m`;
      $("#mt-confere-topo").textContent = `(maior diferença encontrada: ${t})`;
      $("#mt-confere").innerHTML = `<strong>Conferência.</strong> Nos 160 centros anuais (4 variáveis × 40 anos), a maior diferença entre a conta desta página e <code>centro_massa_anual.csv</code> é de ${t}. Fica abaixo de um metro porque o arquivo de dados grava posições e pesos arredondados (ao metro e a 0,1 ha).`;
    })();
  }
})();
