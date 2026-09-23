/* ==========================================================================
   Apresentação — os momentos didáticos: como cada resultado foi construído.

   Carregado depois de apresentacao-hooks.js e antes de apresentacao.js;
   acrescenta hooks a window.HOOKS. Tudo sai dos dados reais:
     assets/data/metodo_centro_massa.json     (pesos por AMC, centroides, bootstrap
                                               oficial do #32; o mesmo da página
                                               "Por dentro do método")
     assets/data/didatica_apresentacao.json   (Visualizacao/scripts/gerar_dados_didaticos.py:
                                               W_sul e nuvem do θ do #34, séries do
                                               Granger, idade do #28C, aptidão do #52/#56)
   A única exceção é o halter do primeiro passo da balança, que é lúdico.

   Hooks
     balanca     halter → Goiás visto de lado → 1985→2024 → bootstrap
     idade       o histograma do censo e as misturas de 1 e 2 componentes
     empurrao    o que o empurrão deixaria nos dados: esperado, espaço (θ), tempo (Granger)
     ty          reserva: o medidor de p do Granger e do Toda–Yamamoto
     balanco     as quatro classes em Mha, 1985–2024 (o pico da pastagem)
     placar      os dois testes do empurrão em 3 medidas × 2 janelas, no mesmo desenho
     motor       a cadeia choque comum → exposição diferente → resposta prevista
     primdif     reserva: o que a primeira diferença faz com uma série

   O mouse é opcional: nos slides da balança, o apoio pode ser arrastado.
   ========================================================================== */
(() => {
  "use strict";
  const HOOKS = window.HOOKS || (window.HOOKS = {});
  const NS = "http://www.w3.org/2000/svg";
  const ESTATICO = /estatico/.test(location.search);
  const el = (tag, attrs = {}, pai) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (pai) pai.appendChild(e);
    return e;
  };
  const txt = (pai, x, y, s, attrs = {}) => { const t = el("text", { x, y, ...attrs }, pai); t.textContent = s; return t; };
  const json = u => fetch(u).then(r => { if (!r.ok) throw new Error(`${u}: HTTP ${r.status}`); return r.json(); });
  // número à brasileira: milhar com ponto, decimal com vírgula, sinal de menos tipográfico
  const fmt = (v, c = 1) => {
    const neg = v < 0, [i, d] = Math.abs(v).toFixed(c).split(".");
    return (neg ? "−" : "") + i.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  };
  const fmtS = (v, c = 1) => (v > 0 ? "+" : "") + fmt(v, c);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const eio = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const eout = t => 1 - Math.pow(1 - t, 3);
  const mulberry = a => () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const caminhoPts = pts => pts.map((q, i) => (i ? "L" : "M") + q[0].toFixed(1) + "," + q[1].toFixed(1)).join("");

  // um "gerador" por hook: cada passo novo invalida as animações do anterior
  function animador() {
    let gen = 0;
    return {
      novo: () => ++gen,
      vivo: g => g === gen,
      tween(g, ms, fn, ease = eio) {
        if (ESTATICO || ms <= 0) { fn(1); return Promise.resolve(true); }
        return new Promise(res => {
          const t0 = performance.now();
          const f = now => {
            if (g !== gen) return res(false);
            const t = Math.min(1, (now - t0) / ms);
            fn(ease(t));
            if (t < 1) requestAnimationFrame(f); else res(true);
          };
          requestAnimationFrame(f);
        });
      },
      espera: (g, ms) => (ESTATICO ? Promise.resolve(g === gen) : new Promise(res => setTimeout(() => res(g === gen), ms))),
    };
  }

  let pMetodo, pDid;
  const metodo = () => pMetodo || (pMetodo = json("assets/data/metodo_centro_massa.json"));
  const didatica = () => pDid || (pDid = json("assets/data/didatica_apresentacao.json"));

  // centro de massa norte–sul (km, EPSG:5880) de um vetor de pesos
  const centroY = (w, Y, c) => { let a = 0, b = 0; for (let i = 0; i < w.length; i++) { const k = c ? c[i] * w[i] : w[i]; a += k * Y[i]; b += k; } return a / b; };

  // ========================================================================
  // 0. O BALANÇO DE QUARENTA ANOS: as quatro classes em milhões de hectares,
  //    na mesma escala (painel_goias.json, o mesmo do site). Uma classe por
  //    passo; o passo 3 destaca o pico de 2003 (o saldo esconde um U invertido).
  // ========================================================================
  const balanco = {
    async init() {
      const s = document.querySelector('[data-hook="balanco"]');
      if (!s) return;
      const serie = (await json("assets/data/painel_goias.json")).serie;
      const svg = s.querySelector("svg.graf-balanco");
      const L = 1696, A = 620, m = { l: 90, r: 360, t: 50, b: 56 };
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      this.svg = svg;
      const anos = serie.map(r => r.ano);
      const mha = k => serie.map(r => r[k] * r.lulc_area_total_ha / 1e6);
      const X = a => m.l + (a - 1985) / 39 * (L - m.l - m.r), Y = v => A - m.b - v / 18 * (A - m.t - m.b);
      // os três atos, ao fundo
      const ga = el("g", { class: "gb-ato" }, svg);
      [["ATO I", 1985, 2000.5, "var(--ato1)"], ["ATO II", 2000.5, 2019.5, "var(--ato2)"], ["ATO III", 2019.5, 2024, "var(--ato3)"]].forEach(([n, a, b, c]) => {
        el("rect", { x: X(a), width: X(b) - X(a), y: m.t, height: A - m.t - m.b, fill: c }, ga);
        txt(ga, (X(a) + X(b)) / 2, m.t - 16, n, { "text-anchor": "middle", fill: c });
      });
      const ge = el("g", { class: "gb-eixo" }, svg);
      [0, 5, 10, 15].forEach(v => { el("line", { x1: m.l, x2: L - m.r, y1: Y(v), y2: Y(v) }, ge); txt(ge, m.l - 14, Y(v) + 8, v, { "text-anchor": "end" }); });
      [1985, 1995, 2005, 2015, 2024].forEach(a => txt(ge, X(a), A - m.b + 34, a, { "text-anchor": "middle" }));
      txt(ge, m.l - 14, m.t - 16, "Mha", { "text-anchor": "end", class: "gb-tit" });
      const C = [
        { k: "pct_vegetacao_nativa", nome: "Vegetação natural", cor: "#2d5a3d", g: "veg" },
        { k: "pct_agricultura", nome: "Agricultura", cor: "#d96aa3", g: "agric" },
        { k: "pct_mosaico", nome: "Mosaico de usos", cor: "#c98a4b", g: "agric", fraca: true },
        { k: "pct_pastagem", nome: "Pastagem", cor: "#c79a2e", g: "pasto" },
      ];
      // rótulos na ponta direita, afastados para não se sobreporem
      const rots = C.map(c => { const v = mha(c.k); return { c, v, y: Y(v[v.length - 1]) }; }).sort((a, b) => a.y - b.y);
      for (let i = 1; i < rots.length; i++) if (rots[i].y - rots[i - 1].y < 64) rots[i].y = rots[i - 1].y + 64;
      this.grupos = {};
      rots.forEach(({ c, v, y }) => {
        const g = this.grupos[c.g] || (this.grupos[c.g] = el("g", { class: `gb-s ${c.g}` }, svg));
        const p = el("path", { d: caminhoPts(anos.map((a, i) => [X(a), Y(v[i])])), class: "gb-linha" + (c.fraca ? " fraca" : ""), stroke: c.cor }, g);
        p.style.setProperty("--len", p.getTotalLength().toFixed(0));
        const yv = Y(v[v.length - 1]);
        if (Math.abs(y - yv) > 4) el("path", { d: `M${X(2024) + 8},${yv} L${X(2024) + 22},${y - 8}`, stroke: c.cor, "stroke-width": 2, fill: "none" }, g);
        const t = txt(g, X(2024) + 28, y - 6, c.nome, { class: "gb-rot", fill: c.cor });
        void t;
        txt(g, X(2024) + 28, y + 24, `${fmt(v[0])} → ${fmt(v[v.length - 1])} Mha`, { class: "gb-rot-v", fill: "var(--fg)" });
      });
      // o pico da pastagem
      const vp = mha("pct_pastagem"), iP = vp.indexOf(Math.max(...vp));
      const gpk = el("g", { class: "gb-pico" }, this.grupos.pasto);
      el("line", { x1: X(anos[iP]), x2: X(anos[iP]), y1: Y(vp[iP]), y2: A - m.b, stroke: "#c79a2e" }, gpk);
      el("circle", { cx: X(anos[iP]), cy: Y(vp[iP]), r: 11, fill: "#c79a2e" }, gpk);
      txt(gpk, X(anos[iP]), Y(vp[iP]) - 28, `pico: ${fmt(vp[iP])} Mha em ${anos[iP]}`, { "text-anchor": "middle", fill: "#8a6a1c" });
      this.pico = gpk;
    },
    // uma classe por passo: vegetação → agricultura e mosaico → pastagem → o pico
    // (as outras esmaecem) → a resposta, com as quatro de volta em contraste pleno
    passo(s, p, ant) {
      if (!this.svg) return;
      const G = this.grupos;
      clearTimeout(this.tVeg);
      const aplica = () => {
        G.veg.classList.add("on");
        G.agric.classList.toggle("on", p >= 1);
        G.pasto.classList.toggle("on", p >= 2);
        this.pico.classList.toggle("on", p >= 3);
        this.svg.classList.toggle("f-pico", p === 3);
      };
      if (ant === null && !ESTATICO) {
        Object.values(G).forEach(g => g.classList.remove("on")); void this.svg.getBoundingClientRect();
        // chegando de outro slide, as linhas esperam a rolagem do palco terminar
        this.tVeg = setTimeout(aplica, 850);
      } else aplica();
    },
  };

  // ========================================================================
  // 1. A BALANÇA
  // ========================================================================
  const COR = { pastagem: "#c79a2e", veg_natural: "#2d5a3d" };
  const ROT = { pastagem: "Pastagem", veg_natural: "Vegetação natural" };
  const balanca = {
    async init() {
      const s = document.querySelector('[data-hook="balanca"]');
      if (!s) return;
      const D = await metodo();
      this.s = s; this.D = D; this.an = animador();
      const svg = s.querySelector("svg.palco-bal");
      const L = 1512, A = 660;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      this.svg = svg;
      const N = D.amc.length, CX = D.amc.map(a => a.cx), CY = D.amc.map(a => a.cy);
      this.N = N; this.CX = CX; this.CY = CY;
      const cyMin = Math.min(...CY), cyMax = Math.max(...CY), cxMin = Math.min(...CX), cxMax = Math.max(...CX);
      this.cym = (cyMin + cyMax) / 2; this.cxm = (cxMin + cxMax) / 2;

      // a régua: km norte–sul (EPSG:5880) → x do palco
      const kmLo = Math.floor(cyMin / 10) * 10 - 10, kmHi = Math.ceil(cyMax / 10) * 10 + 10;
      this.kmLo = kmLo; this.kmHi = kmHi;
      this.beamY = 392; this.x0 = 120; this.s1 = (1390 - 120) / (kmHi - kmLo);
      this.bx = km => this.x0 + (km - kmLo) * this.s1;
      this.kmU = u => kmLo + (u / 120) * (kmHi - kmLo);       // escala do halter: 0–120 "cm" na mesma régua
      this.s0 = 0.78; this.mapC = [430, 318];

      // pesos por faixa de 10 km, para cada variável e ano
      this.bins = []; for (let k = kmLo; k < kmHi; k += 10) this.bins.push(k);
      const binDe = D.amc.map(a => Math.floor((a.cy - kmLo) / 10));
      // c (opcional) = quantas vezes cada AMC entrou no sorteio
      this.porFaixa = (v, ano, c) => {
        const w = D.pesos[v][ano - 1985], f = new Float64Array(this.bins.length);
        for (let i = 0; i < N; i++) f[binDe[i]] += c ? c[i] * w[i] : w[i];
        return f;
      };
      this.maxFaixa = {};
      for (const v of ["pastagem", "veg_natural"]) {
        let m = 0; for (let a = 1985; a <= 2024; a++) m = Math.max(m, ...this.porFaixa(v, a));
        this.maxFaixa[v] = m;
      }
      this.cm = (v, ano, c) => centroY(D.pesos[v][ano - 1985], CY, c);

      // bootstrap AMC a AMC (o do #32): 2.000 sorteios com reposição, semente fixa
      // (as contagens de cada sorteio ficam guardadas: a cena mostra o Goiás sorteado)
      const B = 2000, rng = mulberry(42);
      this.boot = { pastagem: [], veg_natural: [] };
      this.cont = [];
      for (let b = 0; b < B; b++) {
        const c = new Uint8Array(N); for (let t = 0; t < N; t++) c[Math.floor(rng() * N)]++;
        this.cont.push(c);
        for (const v of ["pastagem", "veg_natural"]) this.boot[v].push(this.cm(v, 2024, c) - this.cm(v, 1985, c));
      }
      this.oficial = {};
      for (const v of ["pastagem", "veg_natural"]) {
        const o = D.oficial.boot.find(r => r.variavel === v && r.janela === "LÍQUIDO");
        this.oficial[v] = o;
        const aqui = this.cm(v, 2024) - this.cm(v, 1985);
        if (Math.abs(aqui - o.dN_km) > 0.05) console.warn(`balança: ΔNorte de ${v} = ${aqui.toFixed(2)} ≠ oficial ${o.dN_km}`);
      }

      this.monta(svg, L, A);
      this.st = this.estado(0);
      this.ang = this.alvoAng();
      this.render();
      this.loop();
      this.arrasto();
    },

    monta(svg, L, A) {
      const D = this.D, by = this.beamY;
      const defs = el("defs", {}, svg);
      const grad = (id, stops, attrs = {}) => {
        const g = el(attrs.r ? "radialGradient" : "linearGradient", { id, ...attrs }, defs);
        stops.forEach(([o, c]) => el("stop", { offset: o, "stop-color": c }, g));
      };
      grad("bal-aco", [[0, "#f4f4f2"], [0.35, "#b9bab6"], [0.6, "#7d7f7b"], [1, "#4a4c49"]], { x1: 0, y1: 0, x2: 0, y2: 1 });
      grad("bal-anilha", [[0, "#565a5b"], [0.15, "#25292a"], [0.56, "#171b1c"], [0.84, "#343839"], [1, "#686c6b"]], { x1: 0, y1: 0, x2: 1, y2: 0 });
      grad("bal-madeira", [[0, "#e9dcc3"], [0.5, "#d2bf9b"], [1, "#a78f69"]], { x1: 0, y1: 0, x2: 0, y2: 1 });
      grad("bal-apoio", [[0, "#b04b27"], [1, "#6e2c15"]], { x1: 0, y1: 0, x2: 1, y2: 1 });
      const fl = el("filter", { id: "bal-sombra", x: "-20%", y: "-20%", width: "140%", height: "160%" }, defs);
      el("feDropShadow", { dx: 0, dy: 6, stdDeviation: 7, "flood-color": "#000", "flood-opacity": 0.16 }, fl);

      // chão e réguas
      this.gCena = el("g", {}, svg);
      svg = this.gCena;
      this.gChao = el("g", { class: "bal-chao" }, svg);
      el("line", { x1: 90, x2: 1420, y1: by + 64, y2: by + 64 }, this.gChao);
      this.gReguaU = el("g", { class: "bal-regua" }, svg);
      for (let u = 0; u <= 120; u += 20) {
        const x = this.bx(this.kmU(u));
        el("line", { x1: x, x2: x, y1: by + 74, y2: by + 84 }, this.gReguaU);
        txt(this.gReguaU, x, by + 112, u, { "text-anchor": "middle" });
      }
      txt(this.gReguaU, this.bx(this.kmU(120)) + 26, by + 112, "cm", { "text-anchor": "start" });
      this.gReguaKm = el("g", { class: "bal-regua" }, svg);
      txt(this.gReguaKm, this.bx(this.kmLo), by + 114, "← SUL", { "text-anchor": "start", class: "bal-dir" });
      txt(this.gReguaKm, this.bx(this.kmHi), by + 114, "NORTE →", { "text-anchor": "end", class: "bal-dir" });

      // o mapa (polígonos das AMC) e a rosa dos ventos
      this.gMapa = el("g", { class: "bal-mapa" }, svg);
      const w85 = D.pesos.pastagem[0];
      const dens = D.amc.map((a, i) => w85[i] / (a.area * 100));   // fração da AMC em pasto
      this.polys = D.poly.map((pl, i) => {
        const aneis = typeof pl[0][0] === "number" ? [pl] : pl;
        const d = aneis.map(r => caminhoPts(r.map(q => [q[0], -q[1]])) + "Z").join("");
        return el("path", { d, style: `fill-opacity:${(0.12 + 0.7 * clamp(dens[i], 0, 1)).toFixed(3)}` }, this.gMapa);
      });
      this.gRosa = el("g", { class: "bal-rosa" }, svg);
      el("circle", { r: 34 }, this.gRosa);
      el("path", { d: "M0,-30 L9,4 L0,-3 L-9,4 Z" }, this.gRosa);
      this.rosaN = txt(this.gRosa, 0, -44, "N", { "text-anchor": "middle" });

      // a haste (gira em torno do apoio): barras, régua de madeira, halter
      this.gHaste = el("g", {}, svg);
      this.gBarras = el("g", { class: "bal-barras" }, this.gHaste);
      this.gFantasma = el("g", { class: "bal-fantasma" }, this.gHaste);
      this.barras = this.bins.map(k => el("rect", { x: this.bx(k) + 0.8, width: 10 * this.s1 - 1.6, y: by - 8, height: 0 }, this.gBarras));
      this.fantasmas = this.bins.map(k => el("rect", { x: this.bx(k) + 0.8, width: 10 * this.s1 - 1.6, y: by - 8, height: 0 }, this.gFantasma));
      this.tabua = el("rect", { x: this.bx(this.kmLo) - 6, width: (this.kmHi - this.kmLo) * this.s1 + 12, y: by - 8, height: 16, rx: 3, fill: "url(#bal-madeira)", filter: "url(#bal-sombra)" }, this.gHaste);
      this.gHalter = el("g", { filter: "url(#bal-sombra)" }, this.gHaste);
      el("rect", { x: this.bx(this.kmU(4)), width: this.bx(this.kmU(116)) - this.bx(this.kmU(4)), y: by - 8, height: 16, rx: 8, fill: "url(#bal-aco)" }, this.gHalter);
      const anilhas = (u, n) => {
        const xc = this.bx(this.kmU(u)), esp = 34, tot = n * esp + (n - 1) * 4;
        for (let j = 0; j < n; j++) {
          const x = xc - tot / 2 + j * (esp + 4);
          el("rect", { x, width: esp, y: by - 96, height: 192, rx: 10, fill: "url(#bal-anilha)", stroke: "#171a1a", "stroke-width": 1.5 }, this.gHalter);
          el("rect", { x: x + 5, width: 3, y: by - 78, height: 156, rx: 1.5, fill: "#aeb3b0", opacity: .28 }, this.gHalter);
          el("ellipse", { cx: x + esp - 4, cy: by, rx: 7, ry: 91, fill: "#3d4242", stroke: "#737a78", "stroke-width": 1.2 }, this.gHalter);
          el("ellipse", { cx: x + esp - 4, cy: by, rx: 2.4, ry: 14, fill: "#8a918e", opacity: .75 }, this.gHalter);
        }
        el("rect", { x: xc - tot / 2 - 16, width: 12, y: by - 22, height: 44, rx: 3, fill: "url(#bal-aco)" }, this.gHalter);
        el("rect", { x: xc + tot / 2 + 4, width: 12, y: by - 22, height: 44, rx: 3, fill: "url(#bal-aco)" }, this.gHalter);
        txt(this.gHalter, xc, by - 116, `${n} kg`, { "text-anchor": "middle", class: "bal-kg" });
      };
      anilhas(20, 3); anilhas(100, 1);

      // apoio (arrastável), apoio-fantasma e rótulo do deslocamento
      this.gGhost = el("g", { class: "bal-ghost" }, svg);
      el("path", { d: "M0,8 L-30,64 L30,64 Z" }, this.gGhost);
      this.ghostRot = txt(this.gGhost, 0, 150, "1985", { "text-anchor": "middle" });
      this.gDesl = el("g", { class: "bal-desl" }, svg);
      this.deslLinha = el("path", {}, this.gDesl);
      this.deslTxt = txt(this.gDesl, 0, 0, "", { "text-anchor": "middle" });
      this.gJit = el("g", { class: "bal-jit" }, svg);
      this.gApoio = el("g", { class: "bal-apoio" }, svg);
      el("ellipse", { cx: 0, cy: 66, rx: 48, ry: 7, class: "bal-sombra" }, this.gApoio);
      el("path", { d: "M0,8 L-32,64 L32,64 Z", fill: "url(#bal-apoio)" }, this.gApoio);
      el("rect", { x: -44, y: 62, width: 88, height: 9, rx: 4.5, fill: "#74321d" }, this.gApoio);
      el("circle", { cx: 0, cy: 8, r: 7, fill: "#d18a66", stroke: "#74321d", "stroke-width": 2 }, this.gApoio);
      this.apoioRot = txt(this.gApoio, 0, 150, "", { "text-anchor": "middle", class: "bal-apoio-rot" });

      // círculos das AMC (espaço de tela)
      this.gCirc = el("g", { class: "bal-circ" }, svg);
      const wmax = Math.max(...w85);
      this.circs = D.amc.map((a, i) => el("circle", { r: 0, "data-r": (3 + 19 * Math.sqrt(w85[i] / wmax)).toFixed(1) }, this.gCirc));
      this.queda = D.amc.map(() => Math.random() * 0.35);

      // ano e variável
      this.anoTxt = txt(this.svg, 0, 92, "", { class: "bal-ano" });

      // o bootstrap em dois painéis: à esquerda, a própria balança refeita com o
      // Goiás de UM sorteio (a cena encolhe para lá); à direita, a pilha de todos
      // os sorteios, um tijolo por sorteio, com a faixa de 95% oficial no fim.
      svg = this.svg;
      this.cenaBoot = { k: 0.5, tx: 350 - 0.5 * this.bx(this.cym), ty: 360 - 0.5 * by };
      this.gBoot = el("g", { class: "bal-boot" }, svg);
      txt(this.gBoot, 20, 96, "UM SORTEIO", { class: "bal-boot-tit" });
      this.bootSub = txt(this.gBoot, 20, 134, "", { class: "bal-boot-sub" });
      this.bootDelta = txt(this.gBoot, 350, 520, "", { class: "bal-boot-delta", "text-anchor": "middle" });
      el("line", { x1: 730, x2: 730, y1: 70, y2: 600, class: "bal-boot-div" }, this.gBoot);
      const bx0 = 790, bx1 = 1300, d0 = -25, d1 = 115;
      this.bootX = v => bx0 + (v - d0) / (d1 - d0) * (bx1 - bx0);
      this.bootBins = []; for (let v = d0; v < d1; v += 2) this.bootBins.push(v);
      this.linhasBoot = {};
      this.escBoot = {};
      [["pastagem", 318], ["veg_natural", 540]].forEach(([v, y0]) => {
        const cont = new Array(this.bootBins.length).fill(0);
        this.boot[v].forEach(d => { const j = Math.floor((d + 25) / 2); if (j >= 0 && j < cont.length) cont[j]++; });
        this.escBoot[v] = 138 / Math.max(...cont);
        const g = el("g", { class: "bal-boot-linha" }, this.gBoot);
        const o = this.oficial[v];
        const faixa = el("rect", { x: this.bootX(o.dN_lo), width: this.bootX(o.dN_hi) - this.bootX(o.dN_lo), y: y0 - 142, height: 146, class: "bal-ic", fill: COR[v] }, g);
        txt(g, bx0, y0 - 150, ROT[v], { class: "bal-boot-rot", fill: COR[v] });
        const hs = this.bootBins.map(b => el("rect", { x: this.bootX(b) + 0.5, width: this.bootX(b + 2) - this.bootX(b) - 1, y: y0, height: 0, fill: COR[v] }, g));
        el("line", { x1: bx0, x2: bx1, y1: y0, y2: y0, class: "bal-boot-base" }, g);
        const lado = el("g", { class: "bal-boot-ic" }, g);
        txt(lado, bx1 + 22, y0 - 96, "95% dos sorteios", { class: "bal-ic-rot" });
        txt(lado, bx1 + 22, y0 - 64, `${fmt(o.dN_lo)} a ${fmt(o.dN_hi)} km`, {});
        txt(lado, bx1 + 22, y0 - 26, o.exclui_zero ? "longe do zero" : "inclui o zero", { class: o.exclui_zero ? "bal-selo" : "bal-selo anc" });
        this.linhasBoot[v] = { g, hs, y0, faixa, lado };
      });
      const eixo = el("g", { class: "bal-boot-eixo" }, this.gBoot);
      Object.values(this.linhasBoot).forEach(L => el("line", { x1: this.bootX(0), x2: this.bootX(0), y1: L.y0 - 138, y2: L.y0 + 8, class: "bal-zero" }, L.g));
      [0, 25, 50, 75, 100].forEach(v => txt(eixo, this.bootX(v), 584, v === 0 ? "0 km" : `+${v}`, { "text-anchor": "middle" }));
      txt(this.gBoot, bx0, 96, "TODOS OS SORTEIOS", { class: "bal-boot-tit" });
      txt(this.gBoot, bx0, 128, "deslocamento ao norte em cada um, 1985 → 2024", { class: "bal-boot-sub" });
      this.contador = txt(this.gBoot, 1500, 96, "", { class: "bal-cont", "text-anchor": "end" });
      this.tijolo = el("rect", { width: this.bootX(2) - this.bootX(0) - 1, height: 16, rx: 2, class: "bal-tijolo" }, this.gBoot);
    },

    // o estado final de cada passo
    estado(p) {
      const cp85 = this.cm("pastagem", 1985), cp24 = this.cm("pastagem", 2024);
      const base = { halter: 1, haste: 1, mapa: 0, rot: 0, queda: 0, barras: 0, ano: 1985, v: "pastagem",
        apoio: this.kmU(60), ghost: null, regua: "u", boot: { pastagem: 0, veg_natural: 0 }, bootVis: 0,
        c: null, cA: null, mix: 1, sorteio: 0, tijolo: null };
      const E = [
        {},
        { apoio: this.kmU(40) },
        { halter: 0, haste: 0, mapa: 1, apoio: this.kmU(40) },
        { halter: 0, mapa: 0, rot: 1, queda: 1, barras: 1, apoio: cp85, regua: "km" },
        { halter: 0, rot: 1, queda: 1, barras: 1, apoio: cp85, regua: "km", ano: 2024, ghost85: true },
        { halter: 0, rot: 1, queda: 1, barras: 1, apoio: cp24, regua: "km", ano: 2024, ghost: cp85, ghost85: true },
        { halter: 0, rot: 1, queda: 1, barras: 1, apoio: cp24, regua: "km", ano: 2024, ghost: cp85, ghost85: true, bootVis: 1, boot: { pastagem: 2000, veg_natural: 0 } },
        { halter: 0, rot: 1, queda: 1, barras: 1, v: "veg_natural", apoio: this.cm("veg_natural", 2024), regua: "km", ano: 2024,
          ghost: this.cm("veg_natural", 1985), ghost85: true, bootVis: 1, boot: { pastagem: 2000, veg_natural: 2000 } },
      ];
      return { ...base, ...E[Math.min(p, E.length - 1)], boot: { ...base.boot, ...(E[p] || {}).boot } };
    },

    // transformação do mapa: 0 = mapa de pé; 0,45 = girado; 1 = girado, esticado e achatado sobre a régua
    xf(t) {
      const a = clamp(t / 0.45, 0, 1), b = clamp((t - 0.45) / 0.55, 0, 1);
      const ea = eio(a), eb = eio(b);
      const th = 90 * ea, s = this.s0;
      const ax = lerp(1, this.s1 / this.s0, eb), ay = lerp(1, 0.42, eb);
      const Tx = lerp(this.mapC[0], lerp(this.mapC[0] + 240, this.bx(this.cym), eb), ea);
      const Ty = lerp(this.mapC[1], lerp(this.mapC[1], this.beamY - 150, eb), ea);
      return { th, s, ax, ay, Tx, Ty };
    },
    ponto(f, cx, cy) {
      const vx = (cx - this.cxm) * f.s, vy = -(cy - this.cym) * f.s;
      const r = f.th * Math.PI / 180, c = Math.cos(r), sn = Math.sin(r);
      return [f.Tx + f.ax * (vx * c - vy * sn), f.Ty + f.ay * (vx * sn + vy * c)];
    },

    massas() {
      const st = this.st;
      if (st.halter > 0.5) return [[this.kmU(20), 3], [this.kmU(100), 1]];
      if (st.barras < 0.02) return [];
      const f = this.faixaAtual || this.porFaixa(st.v, st.ano);
      return this.bins.map((k, j) => [k + 5, f[j]]);
    },
    alvoAng() {
      const m = this.massas(); if (!m.length) return 0;
      let a = 0, b = 0; m.forEach(([y, w]) => { a += w * y; b += w; });
      const d = a / b - this.st.apoio;                     // km entre o centro e o apoio
      return 7 * Math.tanh(d / 55);
    },
    loop() {
      const f = now => {
        if (this.s.classList.contains("ativo") || ESTATICO) {
          // ao chegar no slide, o halter fica parado um instante e só então tomba
          const alvo = !ESTATICO && now < (this.segura || 0) ? 0 : this.alvoAng();
          this.ang = ESTATICO ? alvo : this.ang + (alvo - this.ang) * 0.075;
          const x = this.bx(this.st.apoio);
          this.gHaste.setAttribute("transform", `rotate(${this.ang.toFixed(3)} ${x.toFixed(1)} ${this.beamY})`);
        }
        if (!ESTATICO) requestAnimationFrame(f);
      };
      requestAnimationFrame(f);
    },

    render() {
      const st = this.st, by = this.beamY;
      const bv = st.bootVis;
      this.s.classList.toggle("bootstrap", bv > 0.5);
      // no bootstrap a cena encolhe para o painel da esquerda e continua viva
      const cb = this.cenaBoot, k = lerp(1, cb.k, bv);
      this.gCena.setAttribute("transform", `translate(${(cb.tx * bv).toFixed(1)},${(cb.ty * bv).toFixed(1)}) scale(${k.toFixed(4)})`);
      // halter × régua de madeira
      this.gHalter.style.opacity = st.halter;
      this.tabua.style.opacity = (1 - st.halter) * st.haste;
      this.gHaste.style.opacity = Math.max(st.halter, st.haste);
      this.gReguaU.style.opacity = st.halter * st.haste;
      this.gReguaKm.style.opacity = st.regua === "km" ? st.haste : 0;
      this.gChao.style.opacity = st.haste;
      this.gApoio.style.opacity = st.haste;
      this.gApoio.setAttribute("transform", `translate(${this.bx(st.apoio).toFixed(1)},${by})`);
      this.apoioRot.textContent = st.regua === "km" && st.ghost !== null ? String(st.ano) : "";

      // mapa e círculos
      const f = this.xf(st.rot);
      this.gMapa.setAttribute("transform", `translate(${f.Tx.toFixed(1)},${f.Ty.toFixed(1)}) scale(${f.ax.toFixed(4)},${f.ay.toFixed(4)}) rotate(${f.th.toFixed(2)}) scale(${f.s}) translate(${-this.cxm},${this.cym})`);
      const visMapa = Math.max(st.mapa, st.rot > 0 ? 1 - clamp((st.queda - 0.05) / 0.4, 0, 1) : 0);
      this.gMapa.style.opacity = visMapa;
      this.gMapa.style.display = visMapa < 0.01 ? "none" : "";
      const rp = this.ponto(f, this.cxm + 360, this.cym + 300);
      this.gRosa.setAttribute("transform", `translate(${(rp[0] + (st.rot > 0 ? 0 : 60)).toFixed(1)},${rp[1].toFixed(1)}) rotate(${f.th.toFixed(1)})`);
      this.rosaN.setAttribute("transform", `rotate(${(-f.th).toFixed(1)} 0 -44)`);
      this.gRosa.style.opacity = visMapa;
      const visC = st.rot > 0 ? 1 - clamp((st.barras - 0.4) / 0.6, 0, 1) : st.mapa;
      this.gCirc.style.opacity = visC;
      this.gCirc.style.display = visC < 0.01 ? "none" : "";
      if (visC > 0.01) {
        this.circs.forEach((c, i) => {
          let [x, y] = this.ponto(f, this.CX[i], this.CY[i]);
          const r0 = +c.dataset.r;
          if (st.queda > 0) {
            const q = eout(clamp((st.queda - this.queda[i]) / 0.65, 0, 1));
            y = lerp(y, by - 8 - r0 * 0.6, q);
          }
          c.setAttribute("cx", x.toFixed(1)); c.setAttribute("cy", y.toFixed(1));
          c.setAttribute("r", r0 * (st.rot > 0 ? lerp(1, 0.6, clamp(st.queda, 0, 1)) : 1));
        });
      }

      // barras da régua (do Goiás sorteado, no bootstrap) e a sombra de 1985
      const ano = Math.round(st.ano);
      let fx = this.porFaixa(st.v, ano, st.c);
      if (st.mix < 1 && st.cA !== undefined) {
        const fa = this.porFaixa(st.v, ano, st.cA);
        fx = fx.map((v, j) => lerp(fa[j], v, st.mix));
      }
      this.faixaAtual = st.barras > 0.02 ? fx : null;
      const H = 236 * (1 - 0.3 * bv) / this.maxFaixa[st.v];
      this.barras.forEach((r, j) => { const h = fx[j] * H * st.barras; r.setAttribute("y", by - 8 - h); r.setAttribute("height", Math.max(0, h)); });
      this.gBarras.style.fill = COR[st.v];
      const f85 = this.porFaixa(st.v, 1985, st.c);
      this.fantasmas.forEach((r, j) => { const h = f85[j] * H; r.setAttribute("y", by - 8 - h); r.setAttribute("height", h); });
      this.gFantasma.style.opacity = st.ghost85 && st.ano > 1985 ? 1 : 0;

      // apoio-fantasma e rótulo
      const temG = st.ghost !== null && st.haste > 0;
      this.gGhost.style.opacity = temG ? 1 : 0;
      this.gDesl.style.opacity = temG && bv < 0.5 ? 1 : 0;
      if (temG) {
        const xg = this.bx(st.ghost), xa = this.bx(st.apoio);
        this.gGhost.setAttribute("transform", `translate(${xg.toFixed(1)},${by})`);
        const yy = by + 92;
        this.deslLinha.setAttribute("d", `M${xg},${yy} L${xa},${yy} M${xa - 8},${yy - 7} L${xa},${yy} L${xa - 8},${yy + 7}`);
        const d = st.apoio - st.ghost;
        this.deslTxt.setAttribute("x", ((xg + xa) / 2).toFixed(1));
        this.deslTxt.setAttribute("y", yy - 12);
        this.deslTxt.textContent = Math.abs(d) > 1 ? `${fmtS(d)} km` : "";
        this.ghostRot.textContent = "1985";
        const rot = Math.abs(xa - xg) > 70 && bv < 0.5 ? 1 : 0;
        this.ghostRot.style.opacity = rot;
        this.apoioRot.style.opacity = rot;
      }

      // ano
      this.anoTxt.textContent = st.regua === "km" && st.haste > 0 ? `${ROT[st.v]} · ${ano}` : "";
      this.anoTxt.style.fill = COR[st.v];
      this.anoTxt.style.opacity = 1 - bv;

      // bootstrap
      this.gBoot.style.opacity = bv;
      this.gBoot.style.display = bv < 0.01 ? "none" : "";
      for (const v of ["pastagem", "veg_natural"]) {
        const n = Math.round(st.boot[v]), L = this.linhasBoot[v], cont = new Array(this.bootBins.length).fill(0);
        for (let b = 0; b < n; b++) { const j = Math.floor((this.boot[v][b] + 25) / 2); if (j >= 0 && j < cont.length) cont[j]++; }
        // escala viva: nos primeiros sorteios cada um é um tijolo de 16 px; a pilha encolhe à medida que cresce
        L.esc = Math.min(16, 138 / Math.max(1, ...cont));
        L.hs.forEach((r, j) => { const h = cont[j] * L.esc; r.setAttribute("y", L.y0 - h); r.setAttribute("height", h); });
        L.g.style.opacity = v === "pastagem" || n > 0 || st.v === v ? 1 : 0;
        const pronto = n >= 2000;
        L.faixa.style.opacity = pronto ? 0.16 : 0;
        L.lado.style.opacity = pronto ? 1 : 0;
        L.cont = cont;
      }
      const nAtual = st.v === "veg_natural" ? st.boot.veg_natural : st.boot.pastagem;
      this.contador.textContent = nAtual > 0 ? `${fmt(Math.round(nAtual), 0)} de 2.000` : "";
      // o painel da esquerda: qual Goiás está na balança agora
      const dReal = this.cm(st.v, 2024) - this.cm(st.v, 1985);
      if (st.c) {
        let fora = 0, rep = 0; st.c.forEach(n => { if (n === 0) fora++; else if (n > 1) rep++; });
        this.bootSub.textContent = `${ROT[st.v]} · sorteio ${fmt(st.sorteio, 0)}: ${fora} AMC de fora, ${rep} repetidas`;
        this.bootDelta.textContent = `${fmtS(st.apoio - st.ghost)} km neste sorteio`;
      } else {
        this.bootSub.textContent = `${ROT[st.v]} · o mapa real, sem sorteio`;
        this.bootDelta.textContent = `${fmtS(dReal)} km no mapa real`;
      }
      this.bootDelta.style.fill = COR[st.v];
      // o tijolo que sai da balança e cai na pilha
      if (st.tijolo) {
        const t = st.tijolo, x = lerp(t.x0, t.x1, t.u), y = lerp(t.y0, t.y1, t.u) - 120 * Math.sin(Math.PI * t.u);
        this.tijolo.setAttribute("x", x.toFixed(1)); this.tijolo.setAttribute("y", y.toFixed(1));
        this.tijolo.style.fill = COR[st.v];
        this.tijolo.style.opacity = 1;
      } else this.tijolo.style.opacity = 0;

      if (ESTATICO) {   // sem animação (captura/PDF): a inclinação vai direto ao equilíbrio do estado
        this.ang = this.alvoAng();
        this.gHaste.setAttribute("transform", `rotate(${this.ang.toFixed(3)} ${this.bx(st.apoio).toFixed(1)} ${by})`);
      }
    },

    // um sorteio na balança: a cena passa para o Goiás sorteado e o tijolo cai na pilha
    async sorteio(g, T, v, b, lento) {
      const an = this.an, st = this.st, c = this.cont[b];
      const a0 = st.apoio, g0 = st.ghost, a1 = this.cm(v, 2024, c), g1 = this.cm(v, 1985, c);
      st.cA = st.c; st.c = c; st.sorteio = b + 1; st.mix = 0;
      if (!(await T(lento ? 700 : 0, t => { st.mix = t; st.apoio = lerp(a0, a1, t); st.ghost = lerp(g0, g1, t); }))) return false;
      st.mix = 1; st.cA = null;
      if (lento) {
        const L = this.linhasBoot[v], d = this.boot[v][b], j = Math.floor((d + 25) / 2);
        const cs = this.cenaBoot, xm = cs.tx + cs.k * this.bx((a1 + g1) / 2), ym = cs.ty + cs.k * (this.beamY + 60);
        const x1 = this.bootX(this.bootBins[j]) + 0.5, y1 = L.y0 - ((L.cont[j] || 0) + 1) * L.esc;
        st.tijolo = { x0: xm, y0: ym, x1, y1, u: 0 };
        if (!(await T(650, t => { st.tijolo.u = t; }, x => x))) return false;
        st.tijolo = null;
      }
      st.boot[v] = b + 1;
      this.render();
      return lento ? an.espera(g, 450) : true;
    },

    async passo(s, p, ant, inst) {
      if (!this.st) return;
      const an = this.an, g = an.novo();
      if (inst || ant === null || p < ant) {
        this.st = this.estado(p); this.render();
        if (ant === null && p === 0 && !ESTATICO) { this.ang = 0; this.segura = performance.now() + 1100; }
        return;
      }
      const de = this.st, para = this.estado(p);
      const T = (ms, fn, ease) => an.tween(g, ms, t => { fn(t); this.render(); }, ease);
      if (p === 1) {
        await T(1600, t => { this.st.apoio = lerp(de.apoio, para.apoio, t); });
      } else if (p === 2) {
        await T(700, t => { this.st.halter = 1 - t; this.st.haste = 1 - t; });
        await T(900, t => { this.st.mapa = t; });
        this.st = para; this.render();
      } else if (p === 3) {
        this.st = { ...this.estado(2), apoio: para.apoio, regua: "km" };
        await an.espera(g, 150);
        await T(2600, t => { this.st.rot = t; }, x => x);
        await T(1200, t => { this.st.queda = t; this.st.haste = t; }, x => x);
        await T(900, t => { this.st.barras = t; });
        this.st = para; this.render();
      } else if (p === 4) {
        this.st.ghost85 = true;
        await T(4200, t => { this.st.ano = lerp(1985, 2024, t); }, x => x);
        this.st = para; this.render();
      } else if (p === 5) {
        this.st.ghost = de.apoio;
        await T(1800, t => { this.st.apoio = lerp(de.apoio, para.apoio, t); });
        this.st = para; this.render();
      } else if (p === 6 || p === 7) {
        const v = p === 6 ? "pastagem" : "veg_natural", st = this.st;
        if (p === 6) {
          if (!(await T(1000, t => { st.bootVis = t; }))) return;
        } else {
          // a balança troca de variável: a vegetação natural, no mapa real
          if (!(await T(500, t => { st.barras = 1 - t; }))) return;
          Object.assign(st, { v, c: null, apoio: this.cm(v, 2024), ghost: this.cm(v, 1985) });
          if (!(await T(600, t => { st.barras = t; }))) return;
          if (!(await an.espera(g, 900))) return;
        }
        // os primeiros sorteios devagar, um a um; depois o resto, cada vez mais rápido
        const lentos = p === 6 ? 5 : 3;
        for (let b = 0; b < lentos; b++) if (!(await this.sorteio(g, T, v, b, true))) return;
        let feito = lentos;
        const ok = await T(3200, t => {
          const alvo = Math.round(lerp(lentos, 2000, t));
          while (feito < alvo) { st.boot[v] = ++feito; }
          const c = this.cont[feito - 1];
          Object.assign(st, { c, sorteio: feito, apoio: this.cm(v, 2024, c), ghost: this.cm(v, 1985, c) });
        }, t => t * t);
        if (!ok) return;
        await an.espera(g, 300);
        this.st = para; this.render();
      }
    },

    // mouse opcional: arrastar o apoio ao longo da régua
    arrasto() {
      const alvo = this.gApoio;
      alvo.style.cursor = "grab";
      const pt = e => { const m = this.svg.getScreenCTM().inverse(); return new DOMPoint(e.clientX, e.clientY).matrixTransform(m); };
      let ativo = false;
      alvo.addEventListener("pointerdown", e => { if (this.st.haste < 0.5) return; ativo = true; alvo.setPointerCapture(e.pointerId); alvo.style.cursor = "grabbing"; e.preventDefault(); });
      alvo.addEventListener("pointermove", e => {
        if (!ativo) return;
        const km = this.kmLo + (pt(e).x - this.x0) / this.s1;
        this.st.apoio = clamp(km, this.kmLo + 5, this.kmHi - 5);
        this.render();
      });
      const solta = () => { ativo = false; alvo.style.cursor = "grab"; };
      alvo.addEventListener("pointerup", solta);
      alvo.addEventListener("pointercancel", solta);
    },
  };
  HOOKS.balanca = balanca;

  // ========================================================================
  // 2. A IDADE DO PASTO: a forma do censo e as misturas de 1 e 2 componentes
  // ========================================================================
  const idade = {
    async init() {
      const s = document.querySelector('[data-hook="idade"]');
      if (!s) return;
      const I = (await didatica()).idade;
      const svg = s.querySelector("svg.graf-idade");
      const L = 940, A = 560, m = { l: 96, r: 24, t: 40, b: 78 };
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      this.svg = svg;
      const x = v => m.l + v / 40 * (L - m.l - m.r), y = v => A - m.b - v / 0.099 * (A - m.t - m.b);
      const eixo = el("g", { class: "gi-eixo" }, svg);
      [0, 0.02, 0.04, 0.06, 0.08].forEach(v => {
        el("line", { x1: m.l, x2: L - m.r, y1: y(v), y2: y(v) }, eixo);
        txt(eixo, m.l - 14, y(v) + 8, `${fmt(v * 100, 0)}%`, { "text-anchor": "end" });
      });
      [0, 5, 10, 15, 20, 25, 30, 35, 40].forEach(v => txt(eixo, x(v), A - m.b + 34, v, { "text-anchor": "middle" }));
      txt(eixo, (m.l + L - m.r) / 2, A - 8, "idade do pasto quando virou lavoura (anos)", { "text-anchor": "middle", class: "gi-tit" });
      txt(eixo, m.l, 20, "% das conversões com idade conhecida", { class: "gi-tit" });
      const gb = el("g", { class: "gi-barras" }, svg);
      I.x.forEach((a, k) => {
        const r = el("rect", { x: x(a - 0.45), width: x(0.9) - x(0), y: y(I.dens[k]), height: y(0) - y(I.dens[k]) }, gb);
        r.style.transitionDelay = `${(k * 0.018).toFixed(3)}s`;
      });
      const grade = []; for (let a = 0.5; a <= 40; a += 0.1) grade.push(a);
      const gauss = (c, a) => c.peso * Math.exp(-0.5 * ((a - c.mu) / c.sigma) ** 2) / (c.sigma * Math.sqrt(2 * Math.PI));
      const linha = f => caminhoPts(grade.map(a => [x(a), y(f(a))]));
      const area = c => linha(a => gauss(c, a)) + `L${x(40)},${y(0)}L${x(0.5)},${y(0)}Z`;
      const [c1, c2] = I.dois, u = I.um[0];
      el("path", { d: area(c1), class: "gi-comp gi-jovem" }, svg);
      el("path", { d: area(c2), class: "gi-comp gi-velho" }, svg);
      const l1 = el("path", { d: linha(a => gauss(u, a)), class: "gi-um" }, svg);
      const l2 = el("path", { d: linha(a => gauss(c1, a) + gauss(c2, a)), class: "gi-soma" }, svg);
      [l1, l2].forEach(p => p.style.setProperty("--len", p.getTotalLength().toFixed(0)));
      const r1 = el("g", { class: "gi-rot gi-rot-um" }, svg);
      txt(r1, x(19), y(0.058), "se fosse um tipo só", {});
      txt(r1, x(19), y(0.058) + 30, "a curva não alcança o pico", { class: "gi-sub" });
      const rj = el("g", { class: "gi-rot gi-rot-jovem" }, svg);
      txt(rj, x(6.4), y(0.088), `pasto jovem · ~${fmt(c1.mu, 0)} anos`, {});
      txt(rj, x(6.4), y(0.088) + 30, `${fmt(c1.peso * 100, 0)}% das conversões`, { class: "gi-sub" });
      const rv = el("g", { class: "gi-rot gi-rot-velho" }, svg);
      txt(rv, x(21), y(0.036), `pasto velho · ~${fmt(c2.mu, 0)} anos`, {});
      txt(rv, x(21), y(0.036) + 30, `${fmt(c2.peso * 100, 0)}% das conversões`, { class: "gi-sub" });
    },
    passo(s, p, ant) {
      if (!this.svg) return;
      if (ant === null) { this.svg.classList.remove("f0"); void this.svg.getBoundingClientRect(); }
      requestAnimationFrame(() => this.svg.classList.add("f0"));
      this.svg.classList.toggle("f1", p >= 1);
      this.svg.classList.toggle("f2", p >= 2);
      this.svg.classList.toggle("f3", p >= 3);
    },
  };

  // ========================================================================
  // 3. O EMPURRÃO: o que ele deixaria nos dados, em três momentos
  //    (0) o esperado, com Acreúna e os vizinhos ao sul · (1) no espaço: a nuvem
  //    cuja inclinação é o θ · (2) no tempo: as duas previsões do Granger
  // ========================================================================
  const empurrao = {
    async init() {
      const s = document.querySelector('[data-hook="empurrao"]');
      if (!s) return;
      const [D, DD] = await Promise.all([metodo(), didatica()]);
      this.s = s; this.E = DD.empurrao; this.an = animador();
      this.montaMapa(s.querySelector("svg.mapa-emp"), D, this.E);
      this.montaNuvem(s.querySelector(".g-nuvem"));
      this.montaSerie(s.querySelector(".g-serie"));
      this.st = this.estado(0);
      this.render();
    },

    montaMapa(svg, D, E) {
      const L = 620, A = 720, mg = 18;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const CX = D.amc.map(a => a.cx), CY = D.amc.map(a => a.cy);
      const x0 = Math.min(...CX) - 30, x1 = Math.max(...CX) + 30, y0 = Math.min(...CY) - 30, y1 = Math.max(...CY) + 30;
      const k = Math.min((L - 2 * mg) / (x1 - x0), (A - 2 * mg) / (y1 - y0));
      const ox = (L - (x1 - x0) * k) / 2, oy = (A - (y1 - y0) * k) / 2;
      const P = (cx, cy) => [ox + (cx - x0) * k, oy + (y1 - cy) * k];
      const reg = Object.fromEntries(E.mapa.map(r => [r.code, r]));
      const g = el("g", { class: "emp-amc" }, svg);
      this.polys = {};
      D.amc.forEach((a, i) => {
        const pl = D.poly[i], aneis = typeof pl[0][0] === "number" ? [pl] : pl;
        const d = aneis.map(r => caminhoPts(r.map(q => P(q[0], q[1]))) + "Z").join("");
        this.polys[a.code] = el("path", { d, class: `r-${reg[a.code].reg}` }, g);
      });
      const gr = el("g", { class: "emp-regioes" }, svg);
      txt(gr, 200, A - 40, "SUL", { class: "emp-regiao sul", "text-anchor": "middle" });
      txt(gr, 330, 60, "NORTE e NOROESTE", { class: "emp-regiao norte", "text-anchor": "middle" });

      // a AMC do exemplo, os 8 vizinhos mais próximos e os que ficam ao sul (a W_sul do #34)
      const ex = E.exemplo, iEx = D.amc.findIndex(a => a.code === ex.code), cE = P(CX[iEx], CY[iEx]);
      const dist = D.amc.map((a, j) => [j, j === iEx ? Infinity : Math.hypot(CX[j] - CX[iEx], CY[j] - CY[iEx])]).sort((a, b) => a[1] - b[1]).slice(0, 8);
      const sul = new Set(reg[ex.code].sul);
      let bx0 = 1e9, by0 = 1e9, bx1 = -1e9, by1 = -1e9;
      [iEx, ...dist.map(d => d[0])].forEach(j => {
        const b = this.polys[D.amc[j].code].getBBox();
        bx0 = Math.min(bx0, b.x); by0 = Math.min(by0, b.y); bx1 = Math.max(bx1, b.x + b.width); by1 = Math.max(by1, b.y + b.height);
      });
      let w = (bx1 - bx0) * 1.2, h = (by1 - by0) * 1.3;
      if (w / h > L / A) h = w * A / L; else w = h * L / A;
      this.vbFull = [0, 0, L, A];
      this.vbZoom = [(bx0 + bx1) / 2 - w / 2, (by0 + by1) / 2 - h / 2 - h * 0.04, w, h];
      const z = L / w;
      const defs = el("defs", {}, svg);
      const mk = el("marker", { id: "emp-ponta", viewBox: "0 0 10 10", refX: 7, refY: 5, markerWidth: 4, markerHeight: 4, orient: "auto" }, defs);
      el("path", { d: "M0,1 L9,5 L0,9 Z", fill: "#8b3a1d" }, mk);
      const gv = el("g", { class: "emp-viz" }, svg);
      const nomes = el("g", { class: "emp-nomes", style: `font-size:${(19 / z).toFixed(2)}px; stroke-width:${(5 / z).toFixed(2)}px` }, gv);
      dist.forEach(([j]) => {
        const code = D.amc[j].code, c = P(CX[j], CY[j]);
        this.polys[code].classList.add(sul.has(code) ? "viz-sul" : "viz-norte");
        if (sul.has(code)) {
          const dx = cE[0] - c[0], dy = cE[1] - c[1], n = Math.hypot(dx, dy);
          el("path", { d: `M${c[0] + dx / n * 8 / z},${c[1] + dy / n * 8 / z} L${cE[0] - dx / n * 18 / z},${cE[1] - dy / n * 18 / z}`, class: "emp-seta zoom", "marker-end": "url(#emp-ponta)", style: `stroke-width:${(4 / z).toFixed(2)}` }, gv);
          if (D.amc[j].nome === "Rio Verde") txt(nomes, c[0], c[1] + 30 / z, "Rio Verde", { "text-anchor": "middle" });
        }
        el("circle", { cx: c[0], cy: c[1], r: 6 / z, class: sul.has(code) ? "emp-pt sul" : "emp-pt norte", style: `stroke-width:${(2.5 / z).toFixed(2)}` }, gv);
      });
      this.polys[ex.code].classList.add("exemplo");
      el("circle", { cx: cE[0], cy: cE[1], r: 10 / z, class: "emp-pt ex", style: `stroke-width:${(2.5 / z).toFixed(2)}` }, gv);
      const rot = el("g", { class: "emp-rot-ex", style: `font-size:${(30 / z).toFixed(2)}px; stroke-width:${(6 / z).toFixed(2)}px` }, gv);
      txt(rot, cE[0], cE[1] - 54 / z, "pasto aqui?", { "text-anchor": "middle", class: "emp-rot-sub" });
      txt(rot, cE[0], cE[1] - 20 / z, D.amc[iEx].nome, { "text-anchor": "middle" });
      this.svgMapa = svg;

      // o tempo: o Sul agregado antes do Norte agregado?
      const gt = el("g", { class: "emp-tempo" }, svg);
      const cent = r => {
        const ids = D.amc.map((a, j) => j).filter(j => reg[D.amc[j].code].reg === r);
        return P(ids.reduce((t, j) => t + CX[j], 0) / ids.length, ids.reduce((t, j) => t + CY[j], 0) / ids.length);
      };
      const cs = cent("Sul"), cn = cent("Norte");
      el("path", { d: `M${cs[0] + 40},${cs[1] - 50} C${cs[0] + 260},${cs[1] - 120} ${cn[0] + 200},${cn[1] + 190} ${cn[0] + 30},${cn[1] + 60}`, class: "emp-seta tempo", "marker-end": "url(#emp-ponta)" }, gt);
      const et = el("g", { class: "emp-antes" }, gt);
      const mx = (cs[0] + cn[0]) / 2 + 190, my = (cs[1] + cn[1]) / 2 - 10;
      el("rect", { x: mx - 66, y: my - 32, width: 132, height: 50, rx: 25 }, et);
      txt(et, mx, my + 2, "antes?", { "text-anchor": "middle" });
    },

    // ---- a nuvem: 6.474 pares AMC-ano, a reta que o empurrão exigiria e a estimada (θ)
    montaNuvem(box) {
      const L = 1008, A = 470, m = { l: 118, r: 40, t: 20, b: 78 };
      const cv = box.querySelector("canvas"), svg = box.querySelector("svg");
      cv.width = L * 2; cv.height = A * 2;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const F = this.E.fwl;
      const pct = (arr, q) => { const s = [...arr].sort((a, b) => a - b); return s[Math.floor(q * (s.length - 1))]; };
      const ax = Math.max(Math.abs(pct(F.x, 0.015)), Math.abs(pct(F.x, 0.985))), ay = Math.max(Math.abs(pct(F.y, 0.015)), Math.abs(pct(F.y, 0.985)));
      const X = v => m.l + (v + ax) / (2 * ax) * (L - m.l - m.r), Y = v => A - m.b - (v + ay) / (2 * ay) * (A - m.t - m.b);
      const eixo = el("g", { class: "ge-eixo" }, svg);
      el("rect", { x: m.l, y: m.t, width: L - m.l - m.r, height: A - m.t - m.b, class: "ge-moldura" }, eixo);
      el("line", { x1: m.l, x2: L - m.r, y1: Y(0), y2: Y(0), class: "ge-zero" }, eixo);
      el("line", { x1: X(0), x2: X(0), y1: m.t, y2: A - m.b, class: "ge-zero" }, eixo);
      const passo = v => { const e = Math.pow(10, Math.floor(Math.log10(v))); return [1, 2, 5, 10].map(q => q * e).find(q => v / q <= 3); };
      const tx = passo(ax), ty = passo(ay);
      for (let v = -Math.floor(ax / tx) * tx; v <= ax + 1e-9; v += tx) txt(eixo, X(v), A - m.b + 32, fmtS(v, 0), { "text-anchor": "middle" });
      for (let v = -Math.floor(ay / ty) * ty; v <= ay + 1e-9; v += ty) txt(eixo, m.l - 12, Y(v) + 7, fmtS(v, 0), { "text-anchor": "end" });
      txt(eixo, (m.l + L - m.r) / 2, A - 12, "lavoura nova nos vizinhos ao sul, além do habitual (ha)", { "text-anchor": "middle", class: "ge-tit" });
      txt(eixo, 0, 0, "pasto novo aqui, além do habitual (ha)", { "text-anchor": "middle", class: "ge-tit", transform: `translate(30,${(m.t + A - m.b) / 2}) rotate(-90)` });
      this.lHip = el("line", { class: "ge-hip" }, svg);
      this.lReal = el("line", { class: "ge-real" }, svg);
      this.lRot = txt(svg, X(ax * 0.92), 0, "", { class: "ge-real-rot", "text-anchor": "end" });
      this.nuv = { L, A, m, X, Y, ax, ay, ctx: cv.getContext("2d") };
    },
    renderNuvem() {
      const st = this.st, F = this.E.fwl, { L, A, m, X, Y, ax, ay, ctx } = this.nuv;
      ctx.setTransform(2, 0, 0, 2, 0, 0);
      ctx.clearRect(0, 0, L, A);
      const n = Math.round(F.x.length * st.pts);
      ctx.save(); ctx.beginPath(); ctx.rect(m.l, m.t, L - m.l - m.r, A - m.t - m.b); ctx.clip();
      ctx.fillStyle = "rgba(70,62,52,0.16)";
      for (let i = 0; i < n; i++) { ctx.beginPath(); ctx.arc(X(F.x[i]), Y(F.y[i]), 2.3, 0, 6.2832); ctx.fill(); }
      ctx.restore();
      const reta = (ln, slope, vis) => {
        const xa = -ax * 0.94, xb = ax * 0.94;
        ln.setAttribute("x1", X(xa)); ln.setAttribute("y1", Y(clamp(slope * xa, -ay, ay)));
        ln.setAttribute("x2", X(xb)); ln.setAttribute("y2", Y(clamp(slope * xb, -ay, ay)));
        ln.style.opacity = vis;
      };
      const sHip = 0.6 * ay / ax, sl = lerp(sHip, F.theta, st.ang);
      reta(this.lHip, sHip, st.hip);
      reta(this.lReal, sl, st.real);
      this.lRot.setAttribute("y", Y(sl * ax * 0.92) + 48);
      this.lRot.textContent = st.ang > 0.98 ? `θ = ${fmt(F.theta, 3)}` : "";
    },

    // ---- as séries regionais e as duas previsões do Granger
    montaSerie(box) {
      const L = 1008, A = 470, m = { l: 96, r: 30, t: 20, b: 58 };
      const svg = box.querySelector("svg");
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const G = this.E.granger, anos = G.anos;
      const lo = Math.min(0, ...G.sul, ...G.norte) - 10, hi = Math.max(...G.sul, ...G.norte) + 10;
      const X = a => m.l + (a - anos[0]) / (anos[anos.length - 1] - anos[0]) * (L - m.l - m.r), Y = v => A - m.b - (v - lo) / (hi - lo) * (A - m.t - m.b);
      const eixo = el("g", { class: "ge-eixo" }, svg);
      [-50, 0, 50, 100, 150, 200].filter(v => v >= lo && v <= hi).forEach(v => {
        el("line", { x1: m.l, x2: L - m.r, y1: Y(v), y2: Y(v), class: v === 0 ? "ge-zero" : "ge-grade" }, eixo);
        txt(eixo, m.l - 12, Y(v) + 7, fmt(v, 0), { "text-anchor": "end" });
      });
      [1990, 2000, 2010, 2020].forEach(a => txt(eixo, X(a), A - m.b + 34, a, { "text-anchor": "middle" }));
      txt(eixo, 0, 0, "mil ha a mais por ano", { "text-anchor": "middle", class: "ge-tit", transform: `translate(28,${(m.t + A - m.b) / 2}) rotate(-90)` });
      const linha = (xs, vals, cls) => {
        const p = el("path", { d: caminhoPts(vals.map((v, i) => [X(xs[i]), Y(v)])), class: cls }, svg);
        p.style.setProperty("--len", p.getTotalLength().toFixed(0));
        return p;
      };
      this.serie = [linha(anos, G.sul, "ge-sul"), linha(anos, G.norte, "ge-norte")];
      this.prev = [linha(G.anos_fit, G.prev_so_norte, "ge-prev a"), linha(G.anos_fit, G.prev_com_sul, "ge-prev b")];
      this.svgSerie = svg;
    },
    renderSerie() {
      const st = this.st, cut = (p, t) => { const L = +p.style.getPropertyValue("--len"); p.style.strokeDasharray = `${L} ${L}`; p.style.strokeDashoffset = (L * (1 - t)).toFixed(1); };
      this.serie.forEach(p => cut(p, st.serie));
      this.prev.forEach(p => { p.style.opacity = st.prev; });   // tracejadas: entram por opacidade
    },

    render() { this.renderNuvem(); this.renderSerie(); },

    estado(p) {
      const E = [
        {},
        { pts: 1, hip: 1, real: 1, ang: 1 },
        { pts: 1, hip: 1, real: 1, ang: 1, serie: 1, prev: 1 },
      ];
      return { pts: 0, hip: 0, real: 0, ang: 0, serie: 0, prev: 0, ...E[Math.min(p, 2)] };
    },
    vb(v) { this.svgMapa.setAttribute("viewBox", v.map(n => n.toFixed(2)).join(" ")); this.vbAtual = v; },
    async passo(s, p, ant, inst) {
      if (!this.st) return;
      const vbAlvo = p <= 1 ? this.vbZoom : this.vbFull;
      if (inst || ant === null || !this.vbAtual || ESTATICO) this.vb(vbAlvo);
      else if (vbAlvo !== this.vbAtual) {
        const de = this.vbAtual, gz = (this.gZoom = (this.gZoom || 0) + 1), t0 = performance.now();
        const f = now => { if (this.gZoom !== gz) return; const t = eio(Math.min(1, (now - t0) / 1400)); this.vb(de.map((v, k) => lerp(v, vbAlvo[k], t))); if (t < 1) requestAnimationFrame(f); };
        requestAnimationFrame(f);
      }
      this.svgMapa.classList.toggle("f-viz", p <= 1);
      this.svgMapa.classList.toggle("f-dim", p === 1);
      this.svgMapa.classList.toggle("f-regioes", p >= 2);
      this.svgMapa.classList.toggle("f-tempo", p >= 2);
      const g = this.an.novo();
      const para = this.estado(p);
      if (inst || ant === null || p < ant) { this.st = para; this.render(); return; }
      const T = (ms, fn, ease) => this.an.tween(g, ms, t => { fn(t); this.render(); }, ease);
      if (p === 1) {
        this.st = this.estado(0);
        if (!(await this.an.espera(g, 450))) return;
        await T(1500, t => { this.st.pts = t; }, x => x);
        await T(600, t => { this.st.hip = t; });
        if (!(await this.an.espera(g, 700))) return;
        this.st.real = 1;
        await T(1800, t => { this.st.ang = t; });
      } else if (p === 2) {
        if (!(await this.an.espera(g, 600))) return;
        await T(2400, t => { this.st.serie = t; }, x => x);
        if (!(await this.an.espera(g, 400))) return;
        await T(2000, t => { this.st.prev = t; }, x => x);
      }
      if (this.an.vivo(g)) { this.st = para; this.render(); }
    },
  };

  // ========================================================================
  // 3b. RESERVA — o medidor de p do Granger e do Toda–Yamamoto (#42)
  // ========================================================================
  const ty = {
    async init() {
      const s = document.querySelector('[data-hook="ty"]');
      if (!s) return;
      const G = (await didatica()).empurrao.granger;
      const svg = s.querySelector("svg.medidor-p");
      const L = 1500, A = 150, x0 = 40, x1 = 1460;
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const X = p => x0 + p * (x1 - x0);
      el("rect", { x: X(0), y: 44, width: X(0.05) - X(0), height: 40, class: "mp-sig" }, svg);
      el("line", { x1: x0, x2: x1, y1: 84, y2: 84, class: "mp-eixo" }, svg);
      [0, 0.25, 0.5, 0.75, 1].forEach(p => txt(svg, X(p), 116, fmt(p, 2).replace(/,00$/, ""), { "text-anchor": "middle", class: "mp-tick" }));
      txt(svg, x0, 146, "p < 0,05: aqui acenderia", { class: "mp-sig-rot" });
      txt(svg, x1, 146, "p, defasagem de 1 ano", { "text-anchor": "end", class: "mp-tick" });
      const t1 = G.ty.filter(r => r.lag === 1), pSN = t1.find(r => r.dir === "Sul→Norte").p, pNS = t1.find(r => r.dir === "REVERSO").p;
      const marca = (p, rot, cls, anc) => { const g = el("g", { class: `mp-marca ${cls}` }, svg); el("circle", { cx: X(p), cy: 70, r: 12 }, g); txt(g, X(p) + (anc === "start" ? -12 : anc === "end" ? 12 : 0), 36, rot, { "text-anchor": anc }); };
      marca(G.p, `Granger Sul→Norte · ${fmt(G.p, 2)}`, "gr", "end");
      marca(pSN, `Toda–Yamamoto Sul→Norte · ${fmt(pSN, 2)}`, "ty", "end");
      marca(pNS, `Toda–Yamamoto Norte→Sul · ${fmt(pNS, 2)}`, "ty2", "start");
    },
  };

  // ========================================================================
  // 4. O PLACAR: os dois testes do empurrão, repetidos em 3 medidas × 2 janelas,
  //    no mesmo desenho. No espaço, 12 inclinações (as do site, auditadas);
  //    no tempo, os 24 p-valores do Granger (didatica_apresentacao.json).
  //    A zona sombreada é onde o empurrão apareceria; o ponto rosa é o exemplo
  //    do slide anterior (θ = −0,157; p = 0,97).
  // ========================================================================
  const placar = {
    async init() {
      const s = document.querySelector('[data-hook="placar"]');
      if (!s) return;
      const E = (await didatica()).empurrao;
      const LINHAS = [["sat", "Agricultura", "satélite"], ["uni", "Agricultura + Mosaico", "satélite"], ["soja", "Soja plantada", "IBGE"]];
      const th = s.querySelector("svg.pl-theta");
      const V = JSON.parse(th.dataset.valores);
      this.painel(th, {
        lo: -0.2, hi: 0.1, zona: [0, 0.1], zero: true, linhas: LINHAS, vals: V, ex: ["sat", E.fwl.theta],
        ticks: [-0.2, -0.1, 0, 0.1], fmtT: v => (v === 0 ? "0" : fmtS(v, 1)),
        zonaRot: "zona do empurrão (θ > 0)", tit: "inclinação: lavoura dos vizinhos ao sul → pasto da AMC",
      });
      const P = { sat: [], uni: [], soja: [] };
      E.granger.celulas.forEach(c => P[/Mosaico/.test(c.regua_rotulo) ? "uni" : /Soja/.test(c.regua_rotulo) ? "soja" : "sat"].push(c.granger_p));
      this.painel(s.querySelector("svg.pl-p"), {
        lo: 0, hi: 1, zona: [0, 0.05], zero: false, linhas: LINHAS, vals: P, ex: ["sat", E.granger.p],
        ticks: [0, 0.25, 0.5, 0.75, 1], fmtT: v => fmt(v, 2).replace(/,00$/, ""),
        zonaRot: "zona do empurrão (p < 0,05)", tit: "p do teste: a lavoura do Sul antecede o pasto do Norte?",
      });
    },
    painel(svg, o) {
      const L = 800, A = 320, x0 = 290, x1 = 780, base = 244, ys = [74, 134, 194];
      svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
      const X = v => x0 + (v - o.lo) / (o.hi - o.lo) * (x1 - x0);
      el("rect", { x: X(o.zona[0]), width: X(o.zona[1]) - X(o.zona[0]), y: 36, height: base - 36, class: "pl-zona" }, svg);
      txt(svg, X(o.zona[0]) + 8, 24, o.zonaRot, { class: "pl-zona-rot", "text-anchor": o.zona[0] > o.lo ? "start" : "start" });
      ys.forEach(y => el("line", { x1: x0, x2: x1, y1: y, y2: y, class: "pl-grade" }, svg));
      if (o.zero) el("line", { x1: X(0), x2: X(0), y1: 36, y2: base, class: "pl-linha-zero" }, svg);
      el("line", { x1: x0, x2: x1, y1: base, y2: base, class: "pl-grade" }, svg);
      o.ticks.forEach(t => txt(svg, X(t), base + 30, o.fmtT(t), { class: "pl-esc" }));
      txt(svg, (x0 + x1) / 2, base + 64, o.tit, { class: "pl-esc" });
      const gp = el("g", { class: "pl-pts" }, svg);
      let atraso = 0, exFeito = false;
      o.linhas.forEach(([k, nome, fonte], r) => {
        const t = txt(svg, x0 - 18, ys[r] - 2, nome, { class: "pl-rot" });
        txt(svg, x0 - 18, ys[r] + 22, fonte, { class: "pl-rot pl-fonte" + (fonte === "IBGE" ? " ibge" : "") });
        void t;
        // pontos próximos se empilham para cima e para baixo, sem se esconder
        const vals = [...o.vals[k]].sort((a, b) => a - b), usados = [];
        vals.forEach(v => {
          let n = 0; const niveis = [0, -1, 1, -2, 2];
          while (usados.some(u => u.n === niveis[n] && Math.abs(X(u.v) - X(v)) < 15)) n++;
          usados.push({ v, n: niveis[n] });
          const ex = !exFeito && k === o.ex[0] && Math.abs(v - o.ex[1]) < 0.0015;
          if (ex) exFeito = true;
          const c = el("circle", { cx: X(v), cy: ys[r] + niveis[n] * 13, r: ex ? 10 : 8, class: "pl-ponto" + (k === "soja" ? " soja" : "") + (ex ? " ex" : "") }, gp);
          c.style.transitionDelay = `${(0.15 + atraso++ * 0.05).toFixed(2)}s`;
          if (ex) txt(svg, X(v), ys[r] - 26, "o do slide anterior", { class: "pl-ex-rot", "text-anchor": X(v) > x1 - 90 ? "end" : "middle" });
        });
      });
    },
    passo() {},
  };

  // ========================================================================
  // 5. O MOTOR COMUM como cadeia: (1) o choque comum, o câmbio real;
  //    (2) a exposição diferente, a aptidão por AMC; (3) o teste da resposta,
  //    o p de permutação da interação, contra a zona de 5%.
  // ========================================================================
  const motor = {
    async init() {
      const s = document.querySelector('[data-hook="motor"]');
      if (!s) return;
      const [D, DD] = await Promise.all([metodo(), didatica()]);
      const M = DD.motor;
      this.s = s;
      // (1) câmbio real, 1985–2024
      {
        const svg = s.querySelector("svg.mo-cambio"), L = 520, A = 250, m = { l: 14, r: 14, t: 34, b: 40 };
        svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
        const lo = Math.min(...M.cambio), hi = Math.max(...M.cambio);
        const X = a => m.l + (a - 1985) / 39 * (L - m.l - m.r), Y = v => A - m.b - (v - lo) / (hi - lo) * (A - m.t - m.b);
        const ge = el("g", { class: "mo-eixo" }, svg);
        el("line", { x1: m.l, x2: L - m.r, y1: A - m.b + 8, y2: A - m.b + 8 }, ge);
        [1985, 2000, 2024].forEach(a => txt(ge, X(a), A - 6, a, { "text-anchor": a === 1985 ? "start" : a === 2024 ? "end" : "middle" }));
        txt(ge, m.l, 18, "↑ real mais desvalorizado", {});
        const pl = el("path", { d: caminhoPts(M.anos.map((a, i) => [X(a), Y(M.cambio[i])])), class: "mo-linha" }, svg);
        pl.style.setProperty("--len", pl.getTotalLength().toFixed(0));
        this.linhaCambio = pl;
      }
      // (2) aptidão agrícola por AMC (Embrapa): mais escuro = mais apta
      {
        const svg = s.querySelector("svg.mo-mapa"), L = 520, A = 250;
        svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
        const CX = D.amc.map(a => a.cx), CY = D.amc.map(a => a.cy);
        const x0 = Math.min(...CX) - 25, x1 = Math.max(...CX) + 25, y0 = Math.min(...CY) - 25, y1 = Math.max(...CY) + 25;
        const k = Math.min(300 / (x1 - x0), (A - 6) / (y1 - y0));
        const ox = 20 + (300 - (x1 - x0) * k) / 2, oy = 3 + (A - 6 - (y1 - y0) * k) / 2;
        const P = (cx, cy) => [ox + (cx - x0) * k, oy + (y1 - cy) * k];
        const apt = Object.fromEntries(M.amc.map(r => [r.code, r.apt]));
        const aL = Math.min(...M.amc.map(r => r.apt)), aH = Math.max(...M.amc.map(r => r.apt));
        const cor = e => { const a = [246, 226, 236], b = [150, 40, 100]; return `rgb(${a.map((v, j) => Math.round(lerp(v, b[j], e))).join(",")})`; };
        const gm = el("g", { class: "mo-amc" }, svg);
        D.amc.forEach((a, i) => {
          const pl = D.poly[i], aneis = typeof pl[0][0] === "number" ? [pl] : pl;
          const d = aneis.map(r => caminhoPts(r.map(q => P(q[0], q[1]))) + "Z").join("");
          el("path", { d }, gm).style.fill = cor(clamp((apt[a.code] - aL) / (aH - aL), 0, 1));
        });
        // legenda em rampa
        const defs = el("defs", {}, svg), lg = el("linearGradient", { id: "mo-rampa", x1: 0, y1: 1, x2: 0, y2: 0 }, defs);
        [0, 0.5, 1].forEach(e => el("stop", { offset: e, "stop-color": cor(e) }, lg));
        el("rect", { x: 360, y: 40, width: 22, height: 170, fill: "url(#mo-rampa)", rx: 3 }, svg);
        txt(svg, 394, 56, "mais apta", { class: "mo-rot" });
        txt(svg, 394, 208, "menos apta", { class: "mo-rot" });
        txt(svg, 20, 18, "N ↑", { class: "mo-rot" });
      }
      // (3) o p da interação câmbio × aptidão, contra a zona de 5%
      {
        const svg = s.querySelector("svg.mo-p"), L = 520, A = 96, x0 = 10, x1 = 510;
        svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
        const X = p => x0 + p * (x1 - x0);
        el("rect", { x: X(0), y: 26, width: X(0.05) - X(0), height: 34, class: "pl-zona" }, svg);
        txt(svg, X(0), 18, "p < 0,05", { class: "pl-zona-rot" });
        el("line", { x1: x0, x2: x1, y1: 60, y2: 60, class: "pl-grade" }, svg);
        el("rect", { x: X(0.07), y: 34, width: X(0.13) - X(0.07), height: 18, rx: 9, fill: "var(--accent)" }, svg);
        txt(svg, X(0.13) + 12, 50, "0,07 a 0,13", { class: "mo-rot", "font-weight": 700 });
        [0, 0.25, 0.5, 0.75, 1].forEach(p => txt(svg, X(p), 86, fmt(p, 2).replace(/,00$/, ""), { class: "pl-esc", "text-anchor": p === 0 ? "start" : p === 1 ? "end" : "middle" }));
      }
    },
    passo(s, p) {
      if (this.linhaCambio) this.linhaCambio.classList.toggle("on", p >= 1);
    },
  };

  // ========================================================================
  // 6. RESERVA — a primeira diferença numa AMC real (Rio Verde)
  // ========================================================================
  const primdif = {
    async init() {
      const s = document.querySelector('[data-hook="primdif"]');
      if (!s) return;
      const D = await metodo();
      const i = D.amc.findIndex(a => a.nome === "Rio Verde");
      const serie = D.pesos.agricultura.map(w => w[i] / 1000), anos = D.anos;
      const dif = serie.slice(1).map((v, k) => v - serie[k]);
      const desenha = (svg, vals, xs, tit, cls, barras) => {
        const L = 700, A = 400, m = { l: 90, r: 20, t: 56, b: 50 };
        svg.setAttribute("viewBox", `0 0 ${L} ${A}`);
        const lo = Math.min(0, ...vals), hi = Math.max(...vals);
        const X = a => m.l + (a - 1985) / 39 * (L - m.l - m.r), Y = v => A - m.b - (v - lo) / (hi - lo) * (A - m.t - m.b);
        txt(svg, m.l, 30, tit, { class: "pd-tit" });
        const passoY = hi > 200 ? 100 : 20;
        for (let v = Math.ceil(lo / passoY) * passoY; v <= hi; v += passoY) {
          el("line", { x1: m.l, x2: L - m.r, y1: Y(v), y2: Y(v), class: v === 0 ? "pd-zero" : "pd-grade" }, svg);
          txt(svg, m.l - 10, Y(v) + 7, fmt(v, 0), { "text-anchor": "end", class: "pd-tick" });
        }
        [1985, 2000, 2024].forEach(a => txt(svg, X(a), A - 14, a, { "text-anchor": "middle", class: "pd-tick" }));
        if (barras) vals.forEach((v, k) => el("rect", { x: X(xs[k]) - 5, width: 10, y: Math.min(Y(v), Y(0)), height: Math.abs(Y(v) - Y(0)), class: cls }, svg));
        else el("path", { d: caminhoPts(vals.map((v, k) => [X(xs[k]), Y(v)])), class: cls }, svg);
      };
      desenha(s.querySelector("svg.pd-nivel"), serie, anos, "Quanto havia · mil ha de lavoura", "pd-linha", false);
      desenha(s.querySelector("svg.pd-dif"), dif, anos.slice(1), "Quanto mudou em cada ano · mil ha", "pd-barra", true);
    },
  };

  Object.assign(HOOKS, { balanco, idade, empurrao, ty, placar, motor, primdif });
})();
