/* ==========================================================================
   Caderno de conceitos — núcleo
   Registro das peças interativas (CX.def), carga preguiçosa (só monta o que
   entra na tela), controles, gráficos (d3) e a estatística mínima que as peças
   refazem no navegador. Cada peça vive em parte-*.js e chama CX.def(id, fn).
   ========================================================================== */
(function () {
  "use strict";
  const CX = (window.CX = {});
  const registro = {};
  CX.def = (id, fn) => { registro[id] = fn; };

  CX.cor = {
    veg: "#3d7a50", pasto: "#c9a43f", agric: "#d96aa3", mosaico: "#c98a4b", agua: "#4a7ba6",
    acento: "#8b3a1d", cinza: "#9a978e", tinta: "#1a1a1a", suave: "#c97052", azul: "#3b6680",
    Sul: "#8b3a1d", Centro: "#c9a43f", Norte: "#3b6680",
  };

  /* mapa das 166 AMCs: projeta km (y cresce ao norte) numa caixa SVG */
  CX.mapaAMC = function (g, m, w, hh, pad = 6) {
    const xs = m.poly.flatMap((p) => p.flatMap((r) => r.map((c) => c[0])));
    const ys = m.poly.flatMap((p) => p.flatMap((r) => r.map((c) => c[1])));
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const k = Math.min((w - 2 * pad) / (x1 - x0), (hh - 2 * pad) / (y1 - y0));
    const ox = (w - k * (x1 - x0)) / 2, oy = (hh - k * (y1 - y0)) / 2;
    const px = (x) => ox + k * (x - x0), py = (y) => hh - oy - k * (y - y0);
    const d = (poly) => poly.map((r) => "M" + r.map((c) => px(c[0]).toFixed(1) + "," + py(c[1]).toFixed(1)).join("L") + "Z").join("");
    const sel = g.selectAll("path.amc").data(m.amc).join("path").attr("class", "amc")
      .attr("d", (_, i) => d(m.poly[i])).attr("stroke", "#fff").attr("stroke-width", 0.6);
    return { sel, px, py, k };
  };

  const REDUZ = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  CX.reduz = REDUZ;

  /* ---------- dados (cache por arquivo) ---------- */
  const cache = {};
  CX.dado = (nome) =>
    (cache[nome] ||= fetch("assets/data/" + nome).then((r) => {
      if (!r.ok) throw new Error("não foi possível ler " + nome);
      return r.json();
    }));
  CX.base = () => CX.dado("conceitos.json");

  /* ---------- DOM ---------- */
  CX.h = function (tag, props, ...kids) {
    const el = document.createElement(tag);
    if (props) {
      for (const [k, v] of Object.entries(props)) {
        if (v == null || v === false) continue;
        if (k === "class") el.className = v;
        else if (k === "text") el.textContent = v;
        else if (k === "html") el.innerHTML = v;
        else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
        else if (k === "on") for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn);
        else el.setAttribute(k, v === true ? "" : v);
      }
    }
    for (const k of kids.flat()) if (k != null) el.append(k.nodeType ? k : document.createTextNode(k));
    return el;
  };
  const h = CX.h;

  CX.ctrl = (pai) => pai.appendChild(h("div", { class: "cx-ctrl" }));

  let uid = 0;
  CX.slider = function (pai, o) {
    const id = "cxs" + ++uid;
    const fmt = o.fmt || ((v) => String(v));
    const inp = h("input", { type: "range", id, min: o.min, max: o.max, step: o.passo ?? 1, value: o.val });
    const out = h("output", { for: id, text: fmt(+o.val) });
    const box = h("div", { class: "cx-slider" }, h("label", { for: id, text: o.rot }), inp, out);
    pai.appendChild(box);
    inp.addEventListener("input", () => { out.textContent = fmt(+inp.value); o.aoMudar && o.aoMudar(+inp.value); });
    return {
      el: box,
      valor: () => +inp.value,
      set(v, silencioso) { inp.value = v; out.textContent = fmt(+inp.value); if (!silencioso && o.aoMudar) o.aoMudar(+inp.value); },
    };
  };

  CX.seg = function (pai, o) {
    const box = h("div", { class: "cx-seg", role: "group", "aria-label": o.rot || "opções" });
    let val = o.val ?? o.opcoes[0][0];
    const bts = o.opcoes.map(([v, l]) => {
      const b = h("button", { type: "button", "aria-pressed": String(v === val), text: l });
      b.addEventListener("click", () => api.set(v));
      box.appendChild(b);
      return [v, b];
    });
    const api = {
      el: box,
      valor: () => val,
      set(v, silencioso) {
        val = v;
        bts.forEach(([vv, b]) => b.setAttribute("aria-pressed", String(vv === v)));
        if (!silencioso && o.aoMudar) o.aoMudar(v);
      },
    };
    if (o.rot && o.mostraRot) pai.appendChild(h("span", { class: "rot-ctrl", text: o.rot }));
    pai.appendChild(box);
    return api;
  };

  CX.btn = (pai, rot, fn, forte) =>
    pai.appendChild(h("button", { type: "button", class: "cx-btn" + (forte ? " cx-btn--forte" : ""), text: rot, on: { click: fn } }));

  CX.check = function (pai, rot, val, fn) {
    const inp = h("input", { type: "checkbox" });
    inp.checked = !!val;
    inp.addEventListener("change", () => fn(inp.checked));
    pai.appendChild(h("label", { class: "cx-check" }, inp, rot));
    return { valor: () => inp.checked, set(v) { inp.checked = v; fn(v); } };
  };

  CX.leitura = (pai) => pai.appendChild(h("div", { class: "cx-leitura" }));
  CX.num = function (pai, rot, acento) {
    const b = h("b", { text: "—" });
    pai.appendChild(h("div", { class: "cx-num" + (acento ? " cx-num--acento" : "") }, b, h("span", { text: rot })));
    return { set: (v) => { b.textContent = v; } };
  };
  CX.frase = (pai, html) => {
    const el = pai.appendChild(h("div", { class: "cx-frase" }));
    if (html) el.innerHTML = html;
    return el;
  };

  /* Alterna "Exemplo simples" × "Com os seus dados" dentro da mesma peça.
     Cada modo recebe um contêiner limpo e pode devolver uma função de limpeza. */
  CX.modos = function (host, modos, inicial, rot = {}) {
    const topo = host.appendChild(h("div", { class: "cx-modos" }));
    const palco = host.appendChild(h("div"));
    let limpa = null;
    const rotulos = Object.assign({ simples: "Exemplo simples", dados: "Com os seus dados", passos: "Passo a passo com os dados", placar: "O placar do trabalho" }, rot);
    const ops = Object.keys(modos).map((k) => [k, rotulos[k] || k]);
    const ir = async (k) => {
      if (typeof limpa === "function") limpa();
      limpa = null;
      // o contêiner entra na página antes de a peça ser montada: quem mede largura (3D) precisa disso
      const c = h("div");
      palco.replaceChildren(c);
      try {
        limpa = await modos[k](c);
      } catch (e) {
        console.error(e);
        palco.replaceChildren(h("div", { class: "cx-erro", text: "Não foi possível montar esta peça: " + e.message }));
      }
    };
    CX.seg(topo, { opcoes: ops, val: inicial || ops[0][0], aoMudar: ir, rot: "modo do exemplo" });
    ir(inicial || ops[0][0]);
  };

  /* Aula em passos (trazida do laboratório de métodos): uma ideia por vez, com
     "Próximo passo →". Cada passo = {tit, sub, marca, desenha(c)}; "marca" diz se o
     passo usa número inventado ou dado da pesquisa. */
  CX.passos = function (host, passos, o = {}) {
    const box = host.appendChild(h("div", { class: "cx-aula" }));
    const topo = box.appendChild(h("div", { class: "cx-aula-topo" }));
    const rot = topo.appendChild(h("span", { class: "cx-aula-rot" }));
    const dots = topo.appendChild(h("div", { class: "cx-aula-dots", role: "group", "aria-label": "etapas" }));
    const tit = box.appendChild(h("h5", { class: "cx-aula-tit" }));
    const sub = box.appendChild(h("p", { class: "cx-aula-sub" }));
    const palco = box.appendChild(h("div", { class: "cx-aula-palco" }));
    const pe = box.appendChild(h("div", { class: "cx-aula-pe" }));
    const marca = pe.appendChild(h("span", { class: "cx-aula-marca" }));
    const prox = pe.appendChild(h("button", { type: "button", class: "cx-btn cx-btn--forte" }));
    let atual = 0, limpa = null;
    const bts = passos.map((p, i) => {
      const b = h("button", { type: "button", text: String(i + 1), "aria-label": `passo ${i + 1}: ${p.tit}` });
      b.addEventListener("click", () => ir(i));
      dots.appendChild(b);
      return b;
    });
    async function ir(i) {
      if (typeof limpa === "function") limpa();
      limpa = null;
      atual = i;
      const p = passos[i];
      rot.textContent = `Passo ${i + 1} de ${passos.length}`;
      tit.textContent = p.tit;
      sub.innerHTML = p.sub || "";
      marca.textContent = p.marca || "";
      marca.className = "cx-aula-marca" + (p.real ? " cx-aula-marca--real" : "");
      bts.forEach((b, k) => b.setAttribute("aria-pressed", String(k === i)));
      prox.textContent = i < passos.length - 1 ? "Próximo passo →" : "Recomeçar ↺";
      const c = h("div");
      palco.replaceChildren(c);
      try { limpa = await p.desenha(c); }
      catch (e) { console.error(e); palco.replaceChildren(h("div", { class: "cx-erro", text: "Não foi possível montar este passo: " + e.message })); }
    }
    prox.addEventListener("click", () => ir(atual < passos.length - 1 ? atual + 1 : 0));
    ir(o.inicial || 0);
    return { ir };
  };

  /* ---------- números ---------- */
  CX.f = (n, d = 1) =>
    n == null || !isFinite(n) ? "—" : n.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/^-/, "−");
  CX.fs = (n, d = 1) => (n > 0 ? "+" : n < 0 ? "−" : "") + CX.f(Math.abs(n), d);
  CX.pct = (n, d = 0) => CX.f(100 * n, d) + "%";
  CX.p = (p) => (p < 0.001 ? "< 0,001" : CX.f(p, p < 0.01 ? 3 : 2));

  /* ---------- aleatoriedade reprodutível ---------- */
  CX.rng = function (seed) {
    let a = seed >>> 0 || 1;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  CX.normal = (r) => {
    let u = 0, v = 0;
    while (u === 0) u = r();
    while (v === 0) v = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  };

  /* ---------- estatística mínima ---------- */
  const S = (CX.est = {});
  S.media = (a) => a.reduce((s, v) => s + v, 0) / a.length;
  S.dp = (a) => { const m = S.media(a); return Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1)); };
  S.corr = (x, y) => {
    const mx = S.media(x), my = S.media(y);
    let sxy = 0, sxx = 0, syy = 0;
    for (let i = 0; i < x.length; i++) { const a = x[i] - mx, b = y[i] - my; sxy += a * b; sxx += a * a; syy += b * b; }
    return sxy / Math.sqrt(sxx * syy);
  };
  S.diff = (a) => a.slice(1).map((v, i) => v - a[i]);
  S.mediana = (a) => { const s = [...a].sort((p, q) => p - q), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
  S.quantil = (a, q) => { const s = [...a].sort((p, q2) => p - q2); const i = (s.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return s[lo] + (s[hi] - s[lo]) * (i - lo); };
  /* regressão simples y = a + b·x, com erro-padrão clássico */
  S.ols1 = (x, y) => {
    const n = x.length, mx = S.media(x), my = S.media(y);
    let sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; }
    const b = sxy / sxx, a = my - b * mx;
    const res = y.map((v, i) => v - a - b * x[i]);
    const ssr = res.reduce((s, v) => s + v * v, 0), sst = y.reduce((s, v) => s + (v - my) ** 2, 0);
    const se = Math.sqrt(ssr / (n - 2) / sxx);
    return { a, b, r2: 1 - ssr / sst, se, res, sxx, mx, n };
  };
  /* erro-padrão HAC (Newey-West, núcleo de Bartlett) da inclinação */
  S.seHAC = (x, fit, L) => {
    const n = x.length, u = fit.res, xc = x.map((v) => v - fit.mx);
    let s = 0;
    for (let i = 0; i < n; i++) s += (xc[i] * u[i]) ** 2;
    for (let l = 1; l <= L; l++) {
      const w = 1 - l / (L + 1);
      let c = 0;
      for (let t = l; t < n; t++) c += xc[t] * u[t] * xc[t - l] * u[t - l];
      s += 2 * w * c;
    }
    return Math.sqrt(s) / fit.sxx;
  };
  /* regressão múltipla por equações normais; X já traz a coluna de 1 */
  S.ols = (X, y) => {
    const k = X[0].length, n = X.length;
    const A = Array.from({ length: k }, () => new Array(k).fill(0)), bv = new Array(k).fill(0);
    for (let i = 0; i < n; i++) for (let a = 0; a < k; a++) { bv[a] += X[i][a] * y[i]; for (let c = 0; c < k; c++) A[a][c] += X[i][a] * X[i][c]; }
    const inv = S.inv(A);
    const beta = inv.map((row) => row.reduce((s, v, j) => s + v * bv[j], 0));
    const fit = X.map((row) => row.reduce((s, v, j) => s + v * beta[j], 0));
    const res = y.map((v, i) => v - fit[i]);
    const ssr = res.reduce((s, v) => s + v * v, 0);
    return { beta, fit, res, ssr, inv, n, k };
  };
  S.inv = (M) => {
    const n = M.length, A = M.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => +(i === j))]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]];
      const d = A[c][c]; if (Math.abs(d) < 1e-12) throw new Error("matriz singular");
      for (let j = 0; j < 2 * n; j++) A[c][j] /= d;
      for (let r = 0; r < n; r++) if (r !== c) { const f = A[r][c]; for (let j = 0; j < 2 * n; j++) A[r][j] -= f * A[c][j]; }
    }
    return A.map((r) => r.slice(n));
  };
  /* distribuições (aproximações numéricas suficientes para ilustração) */
  S.phi = (z) => 0.5 * (1 + S.erf(z / Math.SQRT2));
  S.erf = (x) => { const s = Math.sign(x); x = Math.abs(x); const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return s * y; };
  S.lgamma = (z) => { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
    let x = z, y = z, t = x + 5.5; t -= (x + 0.5) * Math.log(t); let s = 1.000000000190015; for (const cc of c) s += cc / ++y; return -t + Math.log(2.5066282746310005 * s / x); };
  S.betacf = (a, b, x) => { let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap; if (Math.abs(d) < 1e-30) d = 1e-30; d = 1 / d; let hh = d;
    for (let m = 1; m <= 200; m++) { const m2 = 2 * m; let aa = m * (b - m) * x / ((qam + m2) * (a + m2)); d = 1 + aa * d; if (Math.abs(d) < 1e-30) d = 1e-30; c = 1 + aa / c; if (Math.abs(c) < 1e-30) c = 1e-30; d = 1 / d; hh *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2)); d = 1 + aa * d; if (Math.abs(d) < 1e-30) d = 1e-30; c = 1 + aa / c; if (Math.abs(c) < 1e-30) c = 1e-30; d = 1 / d; const del = d * c; hh *= del; if (Math.abs(del - 1) < 3e-12) break; }
    return hh; };
  S.ibeta = (x, a, b) => { if (x <= 0) return 0; if (x >= 1) return 1;
    const bt = Math.exp(S.lgamma(a + b) - S.lgamma(a) - S.lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * S.betacf(a, b, x) / a : 1 - bt * S.betacf(b, a, 1 - x) / b; };
  S.pT = (t, df) => S.ibeta(df / (df + t * t), df / 2, 0.5); // bicaudal
  S.pF = (F, d1, d2) => (F <= 0 ? 1 : S.ibeta(d2 / (d2 + d1 * F), d2 / 2, d1 / 2));
  S.pBinom = (k, n) => { // P(X >= k) sob moeda honesta
    let s = 0; for (let i = k; i <= n; i++) s += Math.exp(S.lgamma(n + 1) - S.lgamma(i + 1) - S.lgamma(n - i + 1) - n * Math.LN2); return Math.min(1, s); };
  /* binomial com probabilidade q: P(X = k) e P(X >= k) */
  S.binom = (k, n, q) => Math.exp(S.lgamma(n + 1) - S.lgamma(k + 1) - S.lgamma(n - k + 1) + k * Math.log(q) + (n - k) * Math.log(1 - q));
  S.binomCauda = (k, n, q) => { let s = 0; for (let i = Math.max(0, k); i <= n; i++) s += S.binom(i, n, q); return Math.min(1, s); };
  S.gauss = (x, mu, sd) => Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI));

  /* ---------- gráficos (d3) ---------- */
  CX.quadro = function (pai, o = {}) {
    const w = o.w || 680, hh = o.h || 300, m = Object.assign({ t: 26, r: 18, b: 34, l: 50 }, o.m || {});
    // espaço para o rótulo do eixo y, que mora acima do gráfico. Margens pequenas (< 10)
    // pedem desenho sem eixo (mapas, grades): ali a margem é respeitada, senão o desenho
    // escorrega para fora da caixa e cobre o que vem embaixo.
    if (m.t >= 10) m.t = Math.max(m.t, 24);
    if (m.b >= 20 && m.b < 38) m.b = 38; // e para o rótulo do eixo x, abaixo dos números
    const svg = d3.select(pai).append("svg").attr("viewBox", `0 0 ${w} ${hh}`).attr("role", "img");
    if (o.rot) svg.attr("aria-label", o.rot);
    const g = svg.append("g").attr("transform", `translate(${m.l},${m.t})`);
    return { svg, g, w, h: hh, m, iw: w - m.l - m.r, ih: hh - m.t - m.b };
  };
  CX.eixos = function (q, x, y, o = {}) {
    q.g.selectAll(".eixo,.grade,.eixo-rot").remove();
    if (o.grade !== false && y) q.g.insert("g", ":first-child").attr("class", "grade")
      .call(d3.axisLeft(y).ticks(o.yt || 5).tickSize(-q.iw).tickFormat(""));
    if (x) q.g.append("g").attr("class", "eixo").attr("transform", `translate(0,${q.ih})`)
      .call(d3.axisBottom(x).ticks(o.xt || 8).tickFormat(o.xf || null).tickSizeOuter(0));
    if (y) q.g.append("g").attr("class", "eixo").call(d3.axisLeft(y).ticks(o.yt || 5).tickFormat(o.yf || null).tickSizeOuter(0));
    if (o.xl) q.g.append("text").attr("class", "rot-m eixo-rot").attr("x", q.iw).attr("y", q.ih + Math.min(30, q.m.b - 4)).attr("text-anchor", "end").text(o.xl);
    if (o.yl) q.g.append("text").attr("class", "rot-m eixo-rot").attr("x", -q.m.l + 4).attr("y", -12).text(o.yl);
  };

  /* afasta rótulos de fim de linha que colidiriam; itens = [{sel, y}] */
  CX.desempilha = function (itens, lo, hi, gap = 16) {
    const s = itens.filter((i) => isFinite(i.y)).sort((a, b) => a.y - b.y);
    s.forEach((it, k) => { it.y = Math.max(lo, Math.min(hi, it.y)); if (k && it.y - s[k - 1].y < gap) it.y = s[k - 1].y + gap; });
    for (let k = s.length - 1; k >= 0; k--) { if (s[k].y > hi) s[k].y = hi; if (k < s.length - 1 && s[k + 1].y - s[k].y < gap) s[k].y = s[k + 1].y - gap; }
    s.forEach((it) => it.sel.attr("y", it.y));
  };
  CX.anoF = (d) => String(d);
  CX.nf = (d = 1) => (v) => CX.f(v, d);

  /* tooltip único */
  let tipEl = null;
  CX.tip = {
    mostra(ev, html) {
      if (!tipEl) { tipEl = h("div", { class: "cx-tip", role: "tooltip" }); document.body.appendChild(tipEl); }
      tipEl.innerHTML = html;
      const x = ev.clientX, y = ev.clientY, W = window.innerWidth;
      tipEl.style.left = Math.min(W - 270, x + 14) + "px";
      tipEl.style.top = y + 16 + "px";
      tipEl.classList.add("on");
    },
    esconde() { tipEl && tipEl.classList.remove("on"); },
  };

  /* linha com cruz de leitura: séries [{nome, cor, v:[...]}] sobre anos */
  CX.linhas = function (pai, o) {
    const q = CX.quadro(pai, o);
    const x = d3.scaleLinear().domain(d3.extent(o.anos)).range([0, q.iw]);
    const todos = o.series.flatMap((s) => s.v.filter((v) => v != null));
    const ext = o.ydom || [Math.min(0, d3.min(todos)), d3.max(todos) * 1.05];
    const y = d3.scaleLinear().domain(ext).nice().range([q.ih, 0]);
    CX.eixos(q, x, y, { xf: CX.anoF, yf: o.yf, yl: o.yl, xl: o.xl });
    const ln = d3.line().defined((d) => d[1] != null).x((d) => x(d[0])).y((d) => y(d[1]));
    const gS = q.g.append("g");
    const desenha = (series) => {
      gS.selectAll("*").remove();
      const rots = [];
      series.forEach((s) => {
        gS.append("path").attr("d", ln(o.anos.map((a, i) => [a, s.v[i]]))).attr("fill", "none")
          .attr("stroke", s.cor).attr("stroke-width", s.larg || 2).attr("stroke-dasharray", s.traco || null);
        const ult = s.v.length - 1 - [...s.v].reverse().findIndex((v) => v != null);
        if (s.rot !== false) {
          const t = gS.append("text").attr("class", "rot").attr("x", x(o.anos[ult]) + 5);
          t.append("tspan").style("fill", s.cor).text("■ ");
          t.append("tspan").text(s.nome);
          rots.push({ sel: t, y: y(s.v[ult]) + 4 });
        }
      });
      CX.desempilha(rots, 8, q.ih);
    };
    desenha(o.series);
    const cruz = q.g.append("line").attr("y1", 0).attr("y2", q.ih).attr("stroke", "#999").attr("opacity", 0);
    q.g.append("rect").attr("width", q.iw).attr("height", q.ih).attr("fill", "transparent")
      .on("mousemove", (ev) => {
        const [mx] = d3.pointer(ev);
        const a = Math.round(x.invert(mx)), i = o.anos.indexOf(a);
        if (i < 0) return;
        cruz.attr("x1", x(a)).attr("x2", x(a)).attr("opacity", 1);
        CX.tip.mostra(ev, `<b>${a}</b><br>` + (q.series || o.series).map((s) => `${s.nome}: ${s.v[i] == null ? "—" : (o.tf || CX.nf(2))(s.v[i])}`).join("<br>"));
      })
      .on("mouseleave", () => { cruz.attr("opacity", 0); CX.tip.esconde(); });
    q.x = x; q.y = y; q.redesenha = (series) => { q.series = series; desenha(series); };
    return q;
  };

  /* animação que para sozinha quando a peça sai da página */
  CX.loop = function (fn) {
    let vivo = true, id;
    const passo = (t) => { if (!vivo) return; fn(t); id = requestAnimationFrame(passo); };
    id = requestAnimationFrame(passo);
    return () => { vivo = false; cancelAnimationFrame(id); };
  };

  /* ---------- montagem preguiçosa ---------- */
  function monta(fig) {
    if (fig.dataset.montado) return;
    fig.dataset.montado = "1";
    const id = fig.dataset.w;
    const dica = fig.querySelector(".cx-lab-dica");
    const cab = h("div", { class: "cx-lab-cab" }, h("span", { class: "cx-lab-tit", text: fig.dataset.titulo || "Laboratório" }),
      fig.dataset.origem ? h("span", { class: "cx-fonte-tag", text: fig.dataset.origem }) : null);
    const corpo = h("div", { class: "cx-lab-corpo" });
    fig.insertBefore(cab, dica);
    fig.insertBefore(corpo, dica);
    const fn = registro[id];
    if (!fn) { corpo.append(h("div", { class: "cx-erro", text: "Peça não encontrada: " + id })); return; }
    Promise.resolve()
      .then(() => fn(corpo, CX))
      .catch((e) => { console.error(id, e); corpo.append(h("div", { class: "cx-erro", text: "Não foi possível montar esta peça: " + e.message })); });
  }

  function iniciar() {
    const figs = document.querySelectorAll(".cx-lab[data-w]");
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((ents) => ents.forEach((e) => { if (e.isIntersecting) { io.unobserve(e.target); monta(e.target); } }), { rootMargin: "600px 0px" });
      figs.forEach((f) => io.observe(f));
    } else figs.forEach(monta);
    if (location.search.includes("todos")) figs.forEach(monta);

    // sumário: realça o verbete em leitura e mostra o progresso
    const links = new Map();
    document.querySelectorAll(".cx-sumario a[href^='#']").forEach((a) => links.set(a.getAttribute("href").slice(1), a));
    const vs = document.querySelectorAll(".cx-verbete");
    const barra = document.querySelector(".cx-progresso");
    if ("IntersectionObserver" in window) {
      const io2 = new IntersectionObserver((ents) => {
        ents.forEach((e) => {
          if (!e.isIntersecting) return;
          links.forEach((a) => a.classList.remove("cx-atual"));
          const a = links.get(e.target.id);
          if (!a) return;
          a.classList.add("cx-atual");
          // rola só o sumário (quando ele é a coluna fixa), nunca a página
          const sum = a.closest(".cx-sumario");
          if (sum && getComputedStyle(sum).position === "sticky") {
            const top = a.offsetTop - sum.clientHeight / 2;
            sum.scrollTo({ top, behavior: REDUZ ? "auto" : "smooth" });
          }
        });
      }, { rootMargin: "-30% 0px -60% 0px" });
      vs.forEach((v) => io2.observe(v));
    }
    if (barra) window.addEventListener("scroll", () => {
      const t = document.documentElement; barra.style.width = (100 * t.scrollTop / (t.scrollHeight - t.clientHeight)) + "%";
    }, { passive: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
