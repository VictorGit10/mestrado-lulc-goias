/* ==========================================================================
   Apresentação — comportamentos por slide (mapa animado, dominó, centros de
   massa). Carregado ANTES de apresentacao.js, que chama init() e passo().
   Dados: os mesmos JSON do site (assets/data), nenhum número digitado aqui.
   ========================================================================== */
window.HOOKS = (() => {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const fmt1 = v => v.toFixed(1).replace(".", ",");
  const json = u => fetch(u).then(r => r.json());
  const el = (tag, attrs = {}, pai) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (pai) pai.appendChild(e);
    return e;
  };

  // projeção equiretangular com correção de cos(lat) — suficiente para um estado
  function projecao(geo, larg, alt, margem = 20) {
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    const anda = c => typeof c[0] === "number"
      ? (x0 = Math.min(x0, c[0]), x1 = Math.max(x1, c[0]), y0 = Math.min(y0, c[1]), y1 = Math.max(y1, c[1]))
      : c.forEach(anda);
    geo.features.forEach(f => anda(f.geometry.coordinates));
    const k0 = Math.cos(((y0 + y1) / 2) * Math.PI / 180);
    const k = Math.min((larg - 2 * margem) / ((x1 - x0) * k0), (alt - 2 * margem) / (y1 - y0));
    const ox = (larg - (x1 - x0) * k0 * k) / 2, oy = (alt - (y1 - y0) * k) / 2;
    const p = (lon, lat) => [ox + (lon - x0) * k0 * k, oy + (y1 - lat) * k];
    p.kLat = k;
    return p;
  }
  function caminho(geo, p) {
    const anel = r => r.map((c, i) => (i ? "L" : "M") + p(c[0], c[1]).map(v => v.toFixed(1)).join(",")).join("") + "Z";
    return geo.features.map(f => {
      const g = f.geometry;
      const polis = g.type === "Polygon" ? [g.coordinates] : g.coordinates;
      return polis.map(pl => pl.map(anel).join("")).join("");
    });
  }
  let geoMeso;
  const pegaGeo = () => geoMeso || (geoMeso = json("assets/data/malha_mesorregiao.geojson"));

  // ------------------------------------------------------------------------
  // 0a. Goiás desenhado: a marca d'água do hero do site (reforma-hero.js),
  //     as mesorregiões traçadas do Sul para o Norte, em laço.
  // ------------------------------------------------------------------------
  const goias = {
    async init() {
      const alvos = document.querySelectorAll("svg.goias-traco");
      if (!alvos.length) return;
      const geo = await pegaGeo();
      alvos.forEach(svg => {
        const L = 700, A = 820;
        svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
        svg.setAttribute("aria-hidden", "true");
        const p = projecao(geo, L, A, 12);
        const ds = caminho(geo, p);
        // centro vertical de cada mesorregião, para a ordem Sul → Norte
        const cy = geo.features.map(f => {
          let s = 0, n = 0;
          const anda = c => typeof c[0] === "number" ? (s += p(c[0], c[1])[1], n++) : c.forEach(anda);
          anda(f.geometry.coordinates);
          return s / n;
        });
        const ordem = ds.map((d, k) => k).sort((a, b) => cy[b] - cy[a]);
        const gb = el("g", {}, svg), ga = el("g", {}, svg);
        ordem.forEach(k => el("path", { d: ds[k], class: "base" }, gb));
        ordem.forEach((k, j) => {
          const path = el("path", { d: ds[k], class: "anim" }, ga);
          path.style.setProperty("--len", path.getTotalLength().toFixed(0));
          path.style.animationDelay = `${(j * 0.6).toFixed(1)}s`;
        });
      });
    },
  };

  // ------------------------------------------------------------------------
  // 0b. Régua dos 40 anos: a do topo do site (atos em faixas, marcos em pinos)
  // ------------------------------------------------------------------------
  const pct = a => ((a - 1985) / 39) * 100;
  const regua = {
    marcos: [],
    async init() {
      const alvos = document.querySelectorAll(".regua");
      if (!alvos.length) return;
      this.marcos = (await json("assets/data/marcos.json")).marcos.slice().sort((a, b) => a.ano - b.ano);
      alvos.forEach(r => {
        const trilho = r.querySelector(".regua-trilho");
        if (r.hasAttribute("data-marcos")) {
          this.marcos.forEach(m => {
            const i = document.createElement("i");
            i.className = "pino"; i.dataset.ano = m.ano; i.style.left = pct(m.ano) + "%";
            trilho.appendChild(i);
          });
        }
      });
    },
    // posiciona o cursor e acende o ato; devolve o marco do ano, se houver
    ano(r, a) {
      const cur = r.querySelector(".regua-cursor");
      if (cur) { cur.style.left = pct(a) + "%"; cur.dataset.ano = a; }
      const ato = ATOS.find(t => a >= t.ini && a <= t.fim);
      r.querySelectorAll(".banda").forEach((b, k) => b.classList.toggle("ativa", ATOS[k] === ato));
      r.querySelectorAll(".pino").forEach(pn => pn.classList.toggle("aceso", +pn.dataset.ano === a));
      const m = this.marcos.find(x => x.ano === a);
      const era = r.querySelector(".regua-era"), rot = r.querySelector(".regua-rot");
      if (era) era.textContent = `${ato.rot} · ${ato.ini}–${ato.fim} · ${ato.nome}`;
      if (rot) rot.textContent = m ? `${a} · ${m.titulo}` : `${a}`;
    },
  };

  // ------------------------------------------------------------------------
  // 1. Abertura: o mapa anual 1985→2024, ato a ato
  // ------------------------------------------------------------------------
  const ATOS = [
    { ini: 1985, fim: 2000, rot: "Ato I", nome: "Pastagem como herança" },
    { ini: 2001, fim: 2019, rot: "Ato II", nome: "Expansão e intensificação" },
    { ini: 2020, fim: 2024, rot: "Ato III", nome: "Conversão acelerada sob rótulo ambíguo" },
  ];
  const ALVO_ABERTURA = [1985, 2000, 2019, 2024, 2024];
  const abertura = {
    imgs: {}, painel: {}, ano: 1985, timer: null,
    async init() {
      const s = document.querySelector('[data-hook="abertura"]');
      if (!s) return;
      this.s = s;
      this.cv = s.querySelector("canvas");
      this.cv.width = 1353; this.cv.height = 1280;
      this.ctx = this.cv.getContext("2d");
      const p = await json("assets/data/painel_goias.json");
      p.serie.forEach(r => { this.painel[r.ano] = r; });
      const carrega = a => new Promise(res => {
        const im = new Image();
        im.onload = () => { this.imgs[a] = im; if (a === this.ano) this.desenha(a); res(); };
        im.onerror = res;
        im.src = `img/mapas_gee/cobertura_${a}.webp`;
      });
      await carrega(1985);
      for (let a = 1986; a <= 2024; a++) carrega(a);   // o resto em segundo plano
    },
    desenha(a) {
      this.ano = a;
      const im = this.imgs[a];
      if (im) { this.ctx.clearRect(0, 0, 1353, 1280); this.ctx.drawImage(im, 0, 65, 1353, 1280, 0, 0, 1353, 1280);
        // a rosa dos ventos do PNG disputa espaço com o ano: fica só em branco (área fora do estado)
        this.ctx.fillStyle = "#fff"; this.ctx.fillRect(40, 10, 225, 250); }
      this.s.querySelector(".ano").textContent = a;
      const r = this.s.querySelector(".regua");
      if (r) regua.ano(r, a);
      const ato = ATOS.find(t => a >= t.ini && a <= t.fim);
      this.s.querySelector(".ato-rot").innerHTML = `<b>${ato.rot} · ${ato.ini}–${ato.fim}</b>${ato.nome}`;
      const v = this.painel[a];
      if (v) {
        this.s.querySelector('[data-c="veg"]').textContent = fmt1(v.pct_vegetacao_nativa * 100) + "%";
        this.s.querySelector('[data-c="pasto"]').textContent = fmt1(v.pct_pastagem * 100) + "%";
        this.s.querySelector('[data-c="agric"]').textContent = fmt1(v.pct_agricultura * 100) + "%";
        this.s.querySelector('[data-c="mosaico"]').textContent = fmt1(v.pct_mosaico * 100) + "%";
      }
    },
    passo(s, p, ant, instantaneo) {
      clearInterval(this.timer);
      const alvo = ALVO_ABERTURA[p];
      if (instantaneo || ant === null || p < ant) { this.desenha(alvo); return; }
      let a = this.ano;
      this.timer = setInterval(() => {
        if (a >= alvo) { clearInterval(this.timer); return; }
        a++; this.desenha(a);
      }, 150);
    },
  };

  // ------------------------------------------------------------------------
  // 2. A leitura óbvia: o dominó desenhado sobre o contorno do estado
  // ------------------------------------------------------------------------
  const domino = {
    // As duas pontas da hipótese são dados (ganho de lavoura e de pasto por AMC,
    // 1985–2019); o elo entre elas é a hipótese e fica tracejado, com "?".
    async init() {
      const s = document.querySelector('[data-hook="domino"]');
      if (!s) return;
      const [geoAmc, geo, dados] = await Promise.all([
        json("assets/data/malha_amc.geojson"), pegaGeo(), json("assets/data/domino_amc.json"),
      ]);
      const porAmc = Object.fromEntries(dados.amc.map(r => [r.amc, r]));
      const svg = s.querySelector("svg.mapa-domino");
      this.svg = svg;
      const L = 760, A = 880;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const p = projecao(geoAmc, L, A, 24);
      const ds = caminho(geoAmc, p);
      // centro aproximado de cada AMC (média dos vértices projetados)
      const cen = geoAmc.features.map(f => {
        let sx = 0, sy = 0, n = 0;
        const anda = c => typeof c[0] === "number" ? (([sx, sy] = [sx + p(c[0], c[1])[0], sy + p(c[0], c[1])[1]]), n++) : c.forEach(anda);
        anda(f.geometry.coordinates);
        return [sx / n, sy / n];
      });
      const ys = cen.map(c => c[1]), y0 = Math.min(...ys), y1 = Math.max(...ys);
      const onda = y => ((y1 - y) / (y1 - y0) * 1.1).toFixed(2) + "s";   // o Sul acende primeiro
      const esc = (v, teto) => v > 0 ? Math.min(1, v / teto) ** 0.85 : 0;

      const gBase = el("g", { class: "dom-base" }, svg);
      const gAg = el("g", { class: "dom-agric" }, svg);
      const gPa = el("g", { class: "dom-pasto" }, svg);
      geoAmc.features.forEach((f, k) => {
        const r = porAmc[f.properties.code_amc] || { d_agric: 0, d_pasto: 0 };
        el("path", { d: ds[k] }, gBase);
        const a = el("path", { d: ds[k] }, gAg);
        a.style.setProperty("--v", (0.06 + 0.94 * esc(r.d_agric, 0.3)).toFixed(3));
        a.style.setProperty("--d", onda(cen[k][1]));
        const b = el("path", { d: ds[k] }, gPa);
        b.style.setProperty("--v", esc(r.d_pasto, 0.25).toFixed(3));
        b.style.setProperty("--d", onda(cen[k][1]));
      });
      const pm = projecao(geo, L, A, 24);
      caminho(geo, pm).forEach(d => el("path", { d, class: "dom-meso" }, svg));

      // o elo hipotético: um feixe que sai do núcleo de lavoura do Sul e se abre
      // para as AMC de maior ganho de pasto no Norte; o "?" fica no meio dele
      const meio = (y0 + y1) / 2;
      const idx = geoAmc.features.map((f, k) => ({ k, r: porAmc[f.properties.code_amc] || {} }));
      const nucleo = idx.filter(u => cen[u.k][1] > meio + 80).sort((u, v) => v.r.d_agric - u.r.d_agric).slice(0, 10);
      const o = [0, 1].map(e => nucleo.reduce((t, u) => t + cen[u.k][e], 0) / nucleo.length);
      const dest = [];
      idx.filter(u => cen[u.k][1] < meio - 120).sort((u, v) => v.r.d_pasto - u.r.d_pasto).forEach(u => {
        const c = cen[u.k];
        if (dest.length < 4 && dest.every(d => Math.hypot(d[0] - c[0], d[1] - c[1]) > 110)) dest.push(c);
      });
      dest.sort((a, b) => a[0] - b[0]);
      const gFio = el("g", { class: "dom-fios", "data-step": 2 }, svg);
      const mk = el("marker", { id: "ponta-fio", viewBox: "0 0 10 10", refX: 6, refY: 5, markerWidth: 4.5, markerHeight: 4.5, orient: "auto" }, el("defs", {}, svg));
      el("path", { d: "M0,1 L9,5 L0,9 Z", fill: "#8b3a1d" }, mk);
      let meioFeixe = null;
      dest.forEach((t, i) => {
        const c = [(o[0] + t[0]) / 2 + 40, (o[1] + t[1]) / 2 + 30];
        el("path", { d: `M${o[0].toFixed(1)},${o[1].toFixed(1)} Q${c[0].toFixed(1)},${c[1].toFixed(1)} ${t[0].toFixed(1)},${t[1].toFixed(1)}`,
          class: "dom-fio", "marker-end": "url(#ponta-fio)", style: `animation-delay:${(-i * 0.4).toFixed(2)}s` }, gFio);
        if (i === Math.floor(dest.length / 2)) meioFeixe = [.25 * o[0] + .5 * c[0] + .25 * t[0], .25 * o[1] + .5 * c[1] + .25 * t[1]];
      });
      el("circle", { cx: o[0], cy: o[1], r: 11, class: "dom-nucleo" }, gFio);
      const et = el("g", { class: "dom-interroga" }, gFio);
      el("circle", { cx: meioFeixe[0], cy: meioFeixe[1], r: 40 }, et);
      el("text", { x: meioFeixe[0], y: meioFeixe[1] + 20, "text-anchor": "middle" }, et).textContent = "?";
      const rotS = el("text", { x: L / 2 - 20, y: y1 + 58, class: "dom-regiao", "text-anchor": "middle" }, svg);
      rotS.textContent = "SUL";
      const rotN = el("text", { x: L / 2 + 40, y: 30, class: "dom-regiao", "text-anchor": "middle" }, svg);
      rotN.textContent = "NORTE";
    },
    passo(s, p) {
      if (!this.svg) return;
      this.svg.classList.toggle("f-agric", p >= 1);
      this.svg.classList.toggle("f-pasto", p >= 3);
    },
  };

  // ------------------------------------------------------------------------
  // 3. Perna 1: os centros de massa caminhando (mapa + latitude)
  // ------------------------------------------------------------------------
  const ORDEM_CM = ["pastagem", "bovinos", "agricultura", "veg_natural"];
  const marcha = {
    ano: 1985, timer: null,
    async init() {
      const s = document.querySelector('[data-hook="marcha"]');
      if (!s) return;
      this.s = s;
      const [geo, cm] = await Promise.all([pegaGeo(), json("assets/data/marcha_centro_massa.json")]);
      this.vars = ORDEM_CM.map(id => cm.variaveis.find(v => v.id === id));

      // mapa
      const svg = s.querySelector("svg.mapa-cm");
      const L = 760, A = 860;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const p = projecao(geo, L, A, 16);
      caminho(geo, p).forEach(d => el("path", { d, class: "geo-contorno" }, svg));
      // escala de 100 km (1° de latitude ≈ 111 km)
      const esc = p.kLat * 100 / 111;
      // (no canto de baixo à direita, junto do mapa, com as pontas marcadas: lê-se como escala)
      const ex1 = L - 30, ex0 = ex1 - esc, ey = A - 46;
      el("path", { d: `M${ex0},${ey - 9} V${ey} H${ex1} V${ey - 9}`, stroke: "#1a1a1a", "stroke-width": 3, fill: "none" }, svg);
      el("text", { x: (ex0 + ex1) / 2, y: ey - 16, class: "lat-rot", "text-anchor": "middle" }, svg).textContent = "escala: 100 km";
      this.mapa = this.vars.map(v => {
        const pts = v.pts.map(q => p(q.lon, q.lat));
        const ini = pts[0];
        el("circle", { cx: ini[0], cy: ini[1], r: 9, class: "cm-inicio", stroke: v.cor }, svg);
        const trilha = el("path", { class: "cm-trilha", stroke: v.cor }, svg);
        const ponto = el("circle", { r: 15, class: "cm-ponto", fill: v.cor }, svg);
        return { pts, trilha, ponto };
      });
      // o vão lavoura × pasto em 2024, desenhado no mapa
      const pa = this.mapa[0].pts[39], ag = this.mapa[2].pts[39];
      const gv = el("g", { class: "cm-vao", "data-step": 3 }, svg);
      el("line", { x1: ag[0] + 30, y1: ag[1], x2: ag[0] + 30, y2: pa[1] }, gv);
      el("text", { x: ag[0] + 44, y: (ag[1] + pa[1]) / 2 + 8 }, gv).textContent = "~123–135 km";

      // latitude × tempo
      const gl = s.querySelector("svg.graf-lat");
      const GL = 980, GA = 520, m = { l: 110, r: 170, t: 20, b: 60 };
      gl.setAttribute("viewBox", `0 0 ${GL} ${GA}`);
      const la0 = -17.9, la1 = -15.3;
      const x = a => m.l + (a - 1985) / 39 * (GL - m.l - m.r);
      const y = la => m.t + (la1 - la) / (la1 - la0) * (GA - m.t - m.b);
      const eixo = el("g", { class: "lat-eixo" }, gl);
      [-17.5, -17, -16.5, -16, -15.5].forEach(v => {
        el("line", { x1: m.l, x2: GL - m.r, y1: y(v), y2: y(v) }, eixo);
        el("text", { x: m.l - 14, y: y(v) + 8, "text-anchor": "end" }, eixo).textContent = `${fmt1(-v)}° S`;
      });
      [1985, 2000, 2019, 2024].forEach(a => {
        el("text", { x: x(a), y: GA - 18, "text-anchor": "middle" }, eixo).textContent = a;
      });
      this.lat = this.vars.map(v => {
        const linha = el("path", { class: "lat-linha", stroke: v.cor }, gl);
        const rot = el("text", { class: "lat-rot", fill: v.cor, "font-weight": 700 }, gl);
        rot.textContent = v.id === "bovinos" ? "Rebanho" : v.id === "veg_natural" ? "Veg. natural" : v.rotulo;
        return { linha, rot, xy: v.pts.map(q => [x(q.a), y(q.lat)]) };
      });
      this.anoTxt = el("text", { x: GL - m.r, y: GA - m.b - 16, class: "lat-ano", "text-anchor": "end" }, gl);
      this.desenha(1985);
    },
    desenha(a) {
      this.ano = a;
      const n = a - 1985;
      this.mapa.forEach(v => {
        const seg = v.pts.slice(0, n + 1);
        v.trilha.setAttribute("d", seg.map((q, i) => (i ? "L" : "M") + q[0].toFixed(1) + "," + q[1].toFixed(1)).join(""));
        v.ponto.setAttribute("cx", seg[n][0]); v.ponto.setAttribute("cy", seg[n][1]);
      });
      this.lat.forEach(v => {
        const seg = v.xy.slice(0, n + 1);
        v.linha.setAttribute("d", seg.map((q, i) => (i ? "L" : "M") + q[0].toFixed(1) + "," + q[1].toFixed(1)).join(""));
        v.rot.setAttribute("x", seg[n][0] + 14); v.rot.setAttribute("y", seg[n][1] + 8);
      });
      // rótulos finais se sobrepõem (pasto × rebanho): afasta um pouco
      const [rp, rb] = [this.lat[0].rot, this.lat[1].rot];
      const yp = +rp.getAttribute("y"), yb = +rb.getAttribute("y");
      if (Math.abs(yp - yb) < 26) { rp.setAttribute("y", Math.min(yp, yb) - 6); rb.setAttribute("y", Math.max(yp, yb) + 20); }
      this.anoTxt.textContent = a;
    },
    passo(s, p, ant, instantaneo) {
      clearInterval(this.timer);
      const alvo = p === 0 ? 1985 : 2024;
      if (instantaneo || ant === null || p < ant || p > 1) { this.desenha(alvo); return; }
      let a = this.ano;
      this.timer = setInterval(() => {
        if (a >= alvo) { clearInterval(this.timer); return; }
        a++; this.desenha(a);
      }, 110);
    },
  };

  return { goias, regua, abertura, domino, marcha };
})();
