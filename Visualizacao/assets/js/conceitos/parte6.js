/* Caderno de conceitos — Parte 6: literatura */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  function indice(v) { const b = v.find((x) => x != null); return v.map((x) => (x == null ? null : (100 * x) / b)); }

  /* ---------------- 6.1 Renda da terra: cones em 3D ---------------- */
  CX.def("renda", (host) => {
    CX.modos(host, {
      async simples(c) {
        const P = { pL: 10, tL: 6, pG: 5, tG: 1.5, ric: false };
        const ctl = CX.ctrl(c), ctl2 = CX.ctrl(c);
        CX.slider(ctl, { rot: "preço da lavoura", min: 5, max: 16, passo: 0.5, val: P.pL, fmt: (v) => f(v, 1), aoMudar: (v) => { P.pL = v; atualiza(); } });
        CX.slider(ctl, { rot: "frete da lavoura", min: 2, max: 10, passo: 0.5, val: P.tL, fmt: (v) => f(v, 1), aoMudar: (v) => { P.tL = v; atualiza(); } });
        CX.slider(ctl2, { rot: "preço do boi", min: 2, max: 9, passo: 0.5, val: P.pG, fmt: (v) => f(v, 1), aoMudar: (v) => { P.pG = v; atualiza(); } });
        CX.slider(ctl2, { rot: "frete do boi", min: 0.5, max: 4, passo: 0.25, val: P.tG, fmt: (v) => f(v, 2), aoMudar: (v) => { P.tG = v; atualiza(); } });
        const ctl3 = CX.ctrl(c);
        CX.check(ctl3, " qualidade da terra cai para o norte (Ricardo)", false, (v) => { P.ric = v; atualiza(); });
        // renda por hectare a d km do mercado (ao sul) e posição y (0 = sul, 1 = norte)
        const q = (yn) => (P.ric ? 1.25 - 0.5 * yn : 1);
        const RL = (d, yn) => P.pL * q(yn) - 2 - (P.tL * d) / 100;
        const RG = (d, yn) => P.pG * Math.pow(q(yn), 0.4) - 1 - (P.tG * d) / 100;
        const box3 = h("div", { class: "cx-3d" }, h("div", { class: "cx-carregando", text: "carregando a biblioteca 3D…" }));
        c.appendChild(box3);
        const perfil = h("div"); c.appendChild(perfil);
        const lei = CX.leitura(c);
        const nL = CX.num(lei, "anel da lavoura vai até"), nG = CX.num(lei, "anel do gado vai até"), nV = CX.num(lei, "vão entre os anéis (meio a meio)", true);
        let THREE = null, surfL, surfG, chao, ren, cena, cam, grupo, parar;
        const N = 70, L = 500; // grade de N×N sobre um quadrado de 500 km, mercado no meio da borda sul
        try { THREE = await import("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"); }
        catch (e) { box3.replaceChildren(h("div", { class: "cx-erro", text: "A biblioteca 3D não carregou (sem internet?). O perfil abaixo mostra a mesma conta em 2D." })); }
        if (THREE) {
          box3.replaceChildren();
          cena = new THREE.Scene(); cena.background = new THREE.Color(0xf6f5f0);
          cam = new THREE.PerspectiveCamera(40, 1.6, 1, 5000); cam.position.set(420, 380, 520); cam.lookAt(0, 0, -60);
          ren = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true }); ren.setPixelRatio(Math.min(2, devicePixelRatio));
          box3.appendChild(ren.domElement);
          box3.appendChild(h("div", { class: "cx-3d-leg", html: `altura = renda por hectare · <span style="color:${C.agric}">■</span> lavoura <span style="color:${C.pasto}">■</span> gado · chão: uso vencedor · ◆ mercado` }));
          cena.add(new THREE.AmbientLight(0xffffff, 0.8)); const luz = new THREE.DirectionalLight(0xffffff, 0.8); luz.position.set(200, 500, 300); cena.add(luz);
          grupo = new THREE.Group(); cena.add(grupo); grupo.rotation.y = -0.35;
          const mkSurf = (cor, op) => { const g = new THREE.PlaneGeometry(L * 2, L, N - 1, N - 1); g.rotateX(-Math.PI / 2); const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: cor, transparent: true, opacity: op, side: THREE.DoubleSide })); grupo.add(m); return m; };
          surfL = mkSurf(C.agric, 0.75); surfG = mkSurf(C.pasto, 0.75);
          const gc = new THREE.PlaneGeometry(L * 2, L, N - 1, N - 1); gc.rotateX(-Math.PI / 2);
          gc.setAttribute("color", new THREE.BufferAttribute(new Float32Array(gc.attributes.position.count * 3), 3));
          chao = new THREE.Mesh(gc, new THREE.MeshBasicMaterial({ vertexColors: true })); chao.position.y = -0.5; grupo.add(chao);
          const merc = new THREE.Mesh(new THREE.ConeGeometry(10, 30, 4), new THREE.MeshLambertMaterial({ color: 0x8b3a1d })); merc.position.set(0, 15, L / 2); grupo.add(merc);
          const redim = () => { const w = box3.clientWidth, hh = box3.clientHeight; ren.setSize(w, hh, false); cam.aspect = w / hh; cam.updateProjectionMatrix(); };
          redim(); new ResizeObserver(redim).observe(box3);
          let arr = null, rot = -0.35;
          box3.addEventListener("pointerdown", (e) => { arr = [e.clientX, rot]; box3.setPointerCapture(e.pointerId); });
          box3.addEventListener("pointermove", (e) => { if (arr) rot = arr[1] + (e.clientX - arr[0]) * 0.008; });
          box3.addEventListener("pointerup", () => { arr = null; });
          let vis = true; new IntersectionObserver((es) => { vis = es[0].isIntersecting; }).observe(box3);
          parar = CX.loop(() => { if (!vis) return; grupo.rotation.y = rot; ren.render(cena, cam); });
        }
        const escH = 18;
        function atualiza() {
          if (THREE) {
            const pl = surfL.geometry.attributes.position, pg = surfG.geometry.attributes.position, pc = chao.geometry.attributes.position, cc = chao.geometry.attributes.color;
            const col = new THREE.Color();
            for (let i = 0; i < pl.count; i++) {
              const x = pl.getX(i), z = pl.getZ(i); // z: +L/2 é o sul (mercado), −L/2 o norte
              const d = Math.hypot(x, z - L / 2), yn = (L / 2 - z) / L;
              const rl = RL(d, yn), rg = RG(d, yn);
              pl.setY(i, Math.max(0, rl) * escH); pg.setY(i, Math.max(0, rg) * escH);
              col.set(rl > rg && rl > 0 ? C.agric : rg > 0 ? C.pasto : C.veg);
              cc.setXYZ(i, col.r, col.g, col.b);
            }
            pl.needsUpdate = pg.needsUpdate = cc.needsUpdate = true;
            surfL.geometry.computeVertexNormals(); surfG.geometry.computeVertexNormals();
            ren.render(cena, cam); // um quadro já, sem depender da animação
          }
          // perfil ao longo do eixo sul→norte
          perfil.replaceChildren();
          const qq = CX.quadro(perfil, { h: 220, m: { l: 44, r: 90, t: 14, b: 36 } });
          const ds = d3.range(0, 501, 5), x = d3.scaleLinear().domain([0, 500]).range([0, qq.iw]);
          const y = d3.scaleLinear().domain([-2, 14]).range([qq.ih, 0]);
          CX.eixos(qq, x, y, { xl: "distância do mercado, rumo ao norte (km)", yl: "renda por hectare" });
          let fimL = 0, fimG = 0;
          ds.forEach((d) => { const yn = d / 500, rl = RL(d, yn), rg = RG(d, yn); if (rl > rg && rl > 0) fimL = d; if (rg >= rl && rg > 0) fimG = d; });
          [[0, fimL, C.agric], [fimL, fimG, C.pasto], [fimG, 500, C.veg]].forEach(([a, b, cor]) => { if (b > a) qq.g.append("rect").attr("x", x(a)).attr("width", x(b) - x(a)).attr("y", qq.ih - 8).attr("height", 8).attr("fill", cor); });
          qq.g.append("line").attr("class", "zero").attr("x1", 0).attr("x2", qq.iw).attr("y1", y(0)).attr("y2", y(0));
          const rots = [];
          [[RL, C.agric, "lavoura"], [RG, "#9c7a1d", "gado"]].forEach(([fn, cor, n]) => {
            qq.g.append("path").attr("fill", "none").attr("stroke", cor).attr("stroke-width", 2.4).attr("d", d3.line().x((d) => x(d)).y((d) => y(Math.max(-2, fn(d, d / 500))))(ds));
            const t = qq.g.append("text").attr("class", "rot").attr("x", qq.iw + 4); t.append("tspan").style("fill", cor).text("■ "); t.append("tspan").text(n);
            rots.push({ sel: t, y: y(Math.max(-2, fn(500, 1))) + 4 });
          });
          CX.desempilha(rots, 8, qq.ih - 14);
          nL.set(fimL + " km"); nG.set(fimG > fimL ? fimG + " km" : "—"); nV.set(fimG > fimL ? f((fimG + fimL) / 2 - fimL / 2, 0) + " km" : "—");
        }
        atualiza();
        CX.frase(c, "Cada uso tem um cone de renda centrado no mercado: alto e íngreme para a lavoura (produto caro, frete pesado), baixo e largo para o gado. Em cada ponto vence o cone mais alto; onde os dois ficam abaixo de zero, fica a vegetação. Suba o preço da lavoura e o anel dela se alarga sobre o do gado, que se desloca para fora sem que ninguém \"empurre\" nada: é o preço que coordena.");
        return () => parar && parar();
      },
      async dados(c) {
        const m = await CX.dado("metodo_centro_massa.json");
        const cy = (v, t) => { const w = m.pesos[v][t]; let s = 0, sw = 0; m.amc.forEach((a, i) => { s += w[i] * a.cy; sw += w[i]; }); return s / sw; };
        const anos = m.anos, vao = anos.map((_, t) => cy("pastagem", t) - cy("agricultura", t));
        const pas = anos.map((_, t) => cy("pastagem", t) - cy("pastagem", 0)), agr = anos.map((_, t) => cy("agricultura", t) - cy("pastagem", 0)), boi = anos.map((_, t) => cy("bovinos", t) - cy("pastagem", 0));
        const q = CX.linhas(c, { anos, h: 290, m: { l: 50, r: 130, t: 14 }, yf: (v) => f(v, 0), yl: "km ao norte do centro da pastagem de 1985", tf: (v) => f(v, 1) + " km",
          series: [{ nome: "pastagem", cor: C.pasto, v: pas }, { nome: "rebanho", cor: "#8a6d1c", v: boi, traco: "4 3" }, { nome: "agricultura", cor: C.agric, v: agr }], ydom: [-160, 100] });
        const lei = CX.leitura(c);
        CX.num(lei, "vão lavoura → pasto, mínimo").set(f(d3.min(vao), 1) + " km");
        CX.num(lei, "vão, máximo", true).set(f(d3.max(vao), 1) + " km");
        CX.num(lei, "pastagem sobe (1985→2024)").set(fs(pas[39], 1) + " km");
        CX.frase(c, "As três camadas sobem juntas, e a lavoura fica sempre entre 123 e 135 km ao sul do pasto: o arranjo previsto pelos anéis (o uso intensivo mais perto do mercado, ao sul) se translada sem se desfazer. É compatível com renda da terra; não diz se a renda é governada por distância (von Thünen) ou por qualidade (Ricardo).");
        return q;
      },
    });
  });

  /* ---------------- 6.2 Transição florestal ---------------- */
  CX.def("transicao", (host) => {
    CX.modos(host, {
      simples(c) {
        const cob = (t) => 100 - 62 / (1 + Math.exp(-(t - 40) / 7)) + 18 / (1 + Math.exp(-(t - 82) / 5));
        const ctl = CX.ctrl(c);
        let def = "angelsen";
        const sT = CX.slider(ctl, { rot: "tempo", min: 0, max: 100, val: 64, fmt: String, aoMudar: des });
        CX.seg(ctl, { opcoes: [["angelsen", "Angelsen (2007): 4 estágios"], ["rudel", "Rudel et al. (2005): par"]], val: def, aoMudar: (k) => { def = k; des(); } });
        const q = CX.quadro(c, { h: 280, m: { l: 50, r: 16, t: 48 } });
        const x = d3.scaleLinear().domain([0, 100]).range([0, q.iw]), y = d3.scaleLinear().domain([20, 105]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xl: "tempo", yl: "cobertura vegetal (%)" });
        const est = [[0, 28, "1 · cobertura alta, perda lenta"], [28, 52, "2 · perda acelera"], [52, 74, "3 · desacelera e estabiliza"], [74, 100, "4 · recupera"]];
        est.forEach(([a, b, n], i) => {
          q.g.insert("rect", ":first-child").attr("x", x(a)).attr("width", x(b) - x(a)).attr("y", 0).attr("height", q.ih).attr("fill", i % 2 ? "#f3efe3" : "#faf8f2");
          q.g.append("text").attr("class", "rot-m").attr("x", x((a + b) / 2)).attr("y", -30).attr("text-anchor", "middle").text(n);
        });
        q.g.append("path").attr("fill", "none").attr("stroke", C.veg).attr("stroke-width", 2.6).attr("d", d3.line().x((t) => x(t)).y((t) => y(cob(t)))(d3.range(0, 100.5, 0.5)));
        const mk = q.g.append("circle").attr("r", 7).attr("fill", C.acento).attr("stroke", "#fff").attr("stroke-width", 2);
        const txt = CX.frase(c);
        function des() {
          const t = sT.valor(); mk.attr("cx", x(t)).attr("cy", y(cob(t)));
          const e = est.findIndex(([a, b]) => t >= a && t < b) + 1 || 4;
          txt.innerHTML = def === "angelsen"
            ? `Estágio ${e} de 4. ` + (e === 3 ? "A perda desacelera e a cobertura se estabiliza — é onde o Sul goiano está desde 2019. Na formulação de Angelsen, a sequência não avançou até o último estágio." : e === 4 ? "Reflorestamento: a cobertura volta a subir." : "A região ainda perde cobertura.")
            : (e === 4 ? "Queda cessou <b>e</b> recuperação começou: há transição florestal." : e === 3 ? "A queda cessou, mas não há recuperação: pela definição de Rudel et al., a transição florestal <b>não</b> ocorreu. É o caso do Sul goiano." : "A cobertura ainda cai: não há transição.");
        }
        des();
      },
      async dados(c) {
        const V = (await CX.base()).veg_reg;
        const ctl = CX.ctrl(c);
        let rg = "Sul";
        CX.seg(ctl, { opcoes: [["Sul", "perda anual: Sul"], ["Centro", "Centro"], ["Norte", "Norte"]], val: rg, aoMudar: (k) => { rg = k; bar(); } });
        CX.linhas(c, { anos: V.anos, h: 260, m: { l: 44, r: 70, t: 14 }, yl: "vegetação natural (1985 = 100)", yf: (v) => f(v, 0), tf: (v) => f(v, 1), ydom: [55, 102],
          series: ["Sul", "Centro", "Norte"].map((r) => ({ nome: r, cor: C[r], v: indice(V[r]) })) });
        const alvo = h("div"); c.appendChild(alvo);
        function bar() {
          alvo.replaceChildren();
          const d = S.diff(V[rg]).map((v) => -v * 1000), anos = V.anos.slice(1);
          const q = CX.quadro(alvo, { h: 180, m: { l: 50, r: 16, t: 18, b: 30 } });
          const x = d3.scaleBand().domain(anos).range([0, q.iw]).padding(0.15), y = d3.scaleLinear().domain([Math.min(0, d3.min(d)), d3.max(d) * 1.1]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xf: (a) => (a % 5 === 0 ? a : ""), yl: `perda líquida de vegetação, ${rg} (mil ha/ano)`, yf: (v) => f(v, 0) });
          q.g.selectAll("rect").data(d).join("rect").attr("x", (_, i) => x(anos[i])).attr("width", x.bandwidth()).attr("y", (v) => y(Math.max(0, v))).attr("height", (v) => Math.abs(y(v) - y(0))).attr("fill", (_, i) => (anos[i] >= 2019 ? C.acento : "#b9b4a6")).attr("rx", 2)
            .on("mousemove", (ev, v) => CX.tip.mostra(ev, `${anos[d.indexOf(v)]}: ${f(v, 1)} mil ha`)).on("mouseleave", CX.tip.esconde);
        }
        bar();
        const pts = (r) => { const v = indice(V[r]), a = V.anos; return v[a.indexOf(2019)] - v[a.indexOf(2024)]; };
        const perdaSul = S.diff(V.Sul).map((v) => -v * 1000), an = V.anos.slice(1);
        const recup = perdaSul.filter((v, i) => an[i] >= 2019 && v < 0).length;
        CX.frase(c, `Índice por região (as três do trabalho, em AMCs), vegetação natural inteira. O Sul, que abriu primeiro, fica com ${f(indice(V.Sul)[39], 0)}% do que tinha em 1985. De 2019 a 2024 o índice do Sul cai ${f(pts("Sul"), 1)} ponto, contra ${f(pts("Centro"), 1)} no Centro e ${f(pts("Norte"), 1)} no Norte. Em hectares, a perda anual do Sul chega perto de zero em 2018–2019 e volta a ${f(perdaSul[perdaSul.length - 2], 0)}–${f(perdaSul[perdaSul.length - 1], 0)} mil ha nos dois últimos anos; anos com ganho líquido desde 2019: ${recup}. Estabilização por esgotamento, sem a recuperação que a definição de Rudel exige. (O texto mede a mesma estabilização no estoque exposto à conversão, savana e campo: 2 pontos no Sul contra 3,5 e 3,4.)`);
      },
    });
  });

  /* ---------------- 6.3 Deslocamento indireto ---------------- */
  CX.def("iluc", async (host) => {
    const [m, b] = await Promise.all([CX.dado("metodo_centro_massa.json"), CX.base()]);
    const VS = b.vizinhos_sul, reg = b.amc_reg;
    const ctl = CX.ctrl(host);
    let modo = "adj", sel = m.amc.findIndex((a) => (VS[a.code] || []).length >= 3 && reg[m.amc.indexOf(a)] === "Norte");
    if (sel < 0) sel = 0;
    CX.seg(ctl, { opcoes: [["adj", "adjacência (o que o trabalho testa)"], ["dist", "distal, a mais de 300 km (Arima et al.)"]], val: modo, aoMudar: (k) => { modo = k; des(); } });
    const grid = h("div", { class: "cx-grade2" }); host.appendChild(grid);
    const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
    const q = CX.quadro(a1, { w: 340, h: 380, m: { t: 4, r: 4, b: 4, l: 4 } });
    const mp = CX.mapaAMC(q.g, m, q.iw, q.ih);
    const gL = q.g.append("g");
    const info = h("div"); a2.appendChild(info);
    mp.sel.style("cursor", "pointer").on("click", (_, a) => { sel = m.amc.indexOf(a); des(); });
    function des() {
      const a = m.amc[sel];
      const alvo = modo === "adj" ? new Set((VS[a.code] || []).map((cd) => m.amc.findIndex((o) => o.code === cd))) : new Set(m.amc.map((o, i) => (Math.hypot(o.cx - a.cx, o.cy - a.cy) > 300 ? i : -1)).filter((i) => i >= 0));
      mp.sel.attr("fill", (_, i) => (i === sel ? C.acento : alvo.has(i) ? (modo === "adj" ? C.agric : "#e7b9d2") : "#ece9e0"));
      gL.selectAll("*").remove();
      if (modo === "adj") alvo.forEach((i) => { const o = m.amc[i]; gL.append("line").attr("x1", mp.px(o.cx)).attr("y1", mp.py(o.cy)).attr("x2", mp.px(a.cx)).attr("y2", mp.py(a.cy)).attr("stroke", "#111").attr("stroke-width", 1.2); });
      info.innerHTML = `<p class="cx-frase"><b>${a.nome}</b> (${reg[sel]}). ` + (modo === "adj"
        ? `O teste do trabalho pergunta se a lavoura das ${alvo.size} AMC(s) vizinhas ao sul (em rosa) ajuda a explicar a variação do pasto aqui, no ano seguinte, além da lavoura local. É o canal curto, intraestadual.</p>`
        : `Numa matriz distal, esta AMC se ligaria a ${alvo.size} AMCs a mais de 300 km — o tipo de ligação que Arima et al. (2011) modelam na Amazônia, entre a área consolidada e a fronteira florestal. Esse canal não é o testado aqui.</p>`) +
        `<table class="cx-tab"><tr><th>placar do canal de adjacência</th><th></th></tr>
        <tr><td>Granger, lavoura Sul → pasto Norte</td><td>p = 0,97</td></tr>
        <tr><td>Toda-Yamamoto, nas duas direções</td><td>p = 0,25 e 0,45</td></tr>
        <tr><td>termo de vizinhança (12 especificações)</td><td>12 negativos; 1 com p &lt; 0,05, no sentido oposto</td></tr>
        <tr><td>recortes sem a assinatura exigida</td><td>36 de 36</td></tr>
        <tr><td>substituição local (dentro da AMC)</td><td>β ≈ −0,51</td></tr></table>`;
    }
    des();
  });

  /* ---------------- 6.4 Câmbio ---------------- */
  CX.def("cambio", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sP = CX.slider(ctl, { rot: "preço da saca (US$)", min: 10, max: 40, val: 20, fmt: (v) => "US$ " + v, aoMudar: des });
        const sC = CX.slider(ctl, { rot: "câmbio (R$ por US$)", min: 1, max: 6, passo: 0.1, val: 2, fmt: (v) => "R$ " + f(v, 2), aoMudar: des });
        const sK = CX.slider(ctl, { rot: "custo por saca (R$)", min: 10, max: 80, val: 30, fmt: (v) => "R$ " + v, aoMudar: des });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "preço recebido (R$)"), nM = CX.num(lei, "margem por saca", true);
        function des() {
          const rec = sP.valor() * sC.valor(), mg = rec - sK.valor();
          alvo.replaceChildren();
          const q = CX.quadro(alvo, { h: 150, m: { l: 150, r: 70, t: 10, b: 30 } });
          const x = d3.scaleLinear().domain([Math.min(0, mg) - 5, 250]).range([0, q.iw]), y = d3.scaleBand().domain(["recebido", "custo", "margem"]).range([0, q.ih]).padding(0.25);
          CX.eixos(q, x, null, { xf: (v) => "R$ " + v });
          [["recebido", rec, C.azul], ["custo", sK.valor(), C.cinza], ["margem", mg, mg >= 0 ? C.veg : "#9b2c2c"]].forEach(([n, v, cc]) => {
            q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(n)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", cc).attr("rx", 3);
            q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
            q.g.append("text").attr("class", "rot-f").attr("x", x(Math.max(0, v)) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text("R$ " + f(v, 0));
          });
          nR.set("R$ " + f(rec, 2)); nM.set("R$ " + f(mg, 2));
        }
        des();
        CX.frase(c, "Suba o câmbio sem mexer no preço em dólar: a margem cresce, e terra que não compensava plantar passa a compensar. É o mecanismo de Richards (2012) para a expansão da soja após as desvalorizações do fim dos anos 1990.");
      },
      async dados(c) {
        const M = (await CX.base()).macro;
        const media = (v, a, b) => S.media(M.anos.map((ano, i) => (ano >= a && ano <= b ? v[i] : null)).filter((x) => x != null));
        const usdIdx = (() => { const mu = S.media(M.soja_usd); return M.soja_usd.map((v) => (100 * v) / mu); })();
        CX.linhas(c, { anos: M.anos, h: 290, m: { l: 44, r: 150, t: 14 }, yl: "índice (média 1985–2024 = 100)", yf: (v) => f(v, 0), tf: (v) => f(v, 1),
          series: [{ nome: "câmbio real efetivo", cor: C.azul, v: M.cambio }, { nome: "soja em US$", cor: C.cinza, v: usdIdx, traco: "4 3" }, { nome: "preço recebido (soja)", cor: C.acento, v: M.recebido_soja }] });
        const tab = h("table", { class: "cx-tab" });
        tab.innerHTML = `<tr><th>média</th><th>Ato I (1985–2000)</th><th>Ato II (2001–2019)</th><th>Ato III (2020–2024)</th></tr>
          <tr><td>câmbio real efetivo</td><td>${f(media(M.cambio, 1985, 2000), 1)}</td><td>${f(media(M.cambio, 2001, 2019), 1)}</td><td>${f(media(M.cambio, 2020, 2024), 1)}</td></tr>
          <tr><td>preço recebido (soja)</td><td>${f(media(M.recebido_soja, 1985, 2000), 1)}</td><td>${f(media(M.recebido_soja, 2001, 2019), 1)}</td><td>${f(media(M.recebido_soja, 2020, 2024), 1)}</td></tr>`;
        c.appendChild(tab);
        CX.frase(c, "No índice do Ipeadata, alta = real depreciado. O salto de 1999 (fim da banda cambial) é o episódio que Richards (2012) associa à resposta de área da soja. Como o preço recebido é a cotação em dólar vezes o câmbio, as duas linhas não são evidências independentes: o que o preço recebido acrescenta é a cotação em dólar.");
      },
    });
  });

  /* ---------------- 6.5 Intensificação (Cohn) ---------------- */
  CX.def("cohn", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sY = CX.slider(ctl, { rot: "produtividade (× a atual)", min: 1, max: 3, passo: 0.1, val: 2, fmt: (v) => f(v, 1) + "×", aoMudar: des });
        const sE = CX.slider(ctl, { rot: "resposta da demanda ao preço", min: 0, max: 1, passo: 0.05, val: 0.4, fmt: (v) => f(v, 2), aoMudar: des });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nI = CX.num(lei, "terra poupada, conta simples"), nR = CX.num(lei, "terra poupada, com a demanda respondendo", true);
        function des() {
          const y = sY.valor(), e = sE.valor();
          const ingenua = 100 / y, real = 100 * Math.pow(y, e - 1);
          alvo.replaceChildren();
          const q = CX.quadro(alvo, { h: 170, m: { l: 190, r: 70, t: 10, b: 30 } });
          const x = d3.scaleLinear().domain([0, 100]).range([0, q.iw]), yy = d3.scaleBand().domain(["hoje", "conta simples", "com a demanda respondendo"]).range([0, q.ih]).padding(0.25);
          CX.eixos(q, x, null, { xl: "hectares de pasto necessários" });
          [["hoje", 100, C.cinza], ["conta simples", ingenua, C.azul], ["com a demanda respondendo", real, C.acento]].forEach(([n, v, cc]) => {
            q.g.append("rect").attr("y", yy(n)).attr("height", yy.bandwidth()).attr("width", x(v)).attr("fill", cc).attr("rx", 3);
            q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", yy(n) + yy.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
            q.g.append("text").attr("class", "rot-f").attr("x", x(v) + 5).attr("y", yy(n) + yy.bandwidth() / 2 + 4).text(f(v, 0) + " ha");
          });
          nI.set(f(100 - ingenua, 0) + " ha"); nR.set(f(100 - real, 0) + " ha");
        }
        des();
        CX.frase(c, "Produzir o dobro por hectare deveria liberar metade da terra. Mas a carne fica mais barata, a demanda cresce, e parte da terra volta a ser usada: a poupança existe, e é parcial.");
      },
      async dados(c) {
        const R = (await CX.base()).reg;
        const ctl = CX.ctrl(c);
        let rg = "Sul";
        CX.seg(ctl, { opcoes: [["Sul", "Sul"], ["Centro", "Centro"], ["Norte", "Norte"]], val: rg, aoMudar: (k) => { rg = k; des(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const txt = CX.frase(c);
        function des() {
          const p = R["pasto_mha_" + rg], b = R["bovinos_mcab_" + rg], a = R["agric_mha_" + rg], lot = b.map((v, i) => v / p[i]);
          alvo.replaceChildren();
          CX.linhas(alvo, { anos: R.anos, h: 270, m: { l: 44, r: 130, t: 14 }, yl: "índice (1985 = 100)", yf: (v) => f(v, 0), tf: (v) => f(v, 1),
            series: [{ nome: "pastagem", cor: C.pasto, v: indice(p) }, { nome: "rebanho", cor: "#8a6d1c", v: indice(b), traco: "4 3" }, { nome: "lotação (cab/ha)", cor: C.acento, v: indice(lot) }] });
          txt.innerHTML = `${rg}: pastagem de ${f(p[0], 2)} para ${f(p[39], 2)} Mha, rebanho de ${f(b[0], 1)} para ${f(b[39], 1)} milhões de cabeças, lotação de ${f(lot[0], 2)} para ${f(lot[39], 2)} cab/ha; a agricultura foi de ${f(a[0], 2)} para ${f(a[39], 2)} Mha. ` + (rg === "Sul" ? "No Sul o pasto encolhe desde o início dos anos 2000 com o rebanho quase estável: a lotação sobe, e a terra liberada vira lavoura." : "Aqui pasto e rebanho crescem juntos durante boa parte da série: é fronteira, não intensificação.");
        }
        des();
      },
    });
  });

  /* ---------------- 6.6 A fronteira do Cerrado ---------------- */
  CX.def("cerrado", async (host) => {
    const SR = await CX.dado("sankey_regional.json");
    const ctl = CX.ctrl(host);
    let ato = "II";
    CX.seg(ctl, { opcoes: [["I", "Ato I (1985–2000)"], ["II", "Ato II (2001–2019)"], ["III", "Ato III (2020–2024)"]], val: ato, aoMudar: (k) => { ato = k; des(); } });
    const alvo = h("div"); host.appendChild(alvo);
    const txt = CX.frase(host);
    const mesos = ["Sul Goiano", "Leste Goiano", "Centro Goiano", "Noroeste Goiano", "Norte Goiano"];
    const destino = (id) => /^(Agricultura|Mosaico de Usos)_/.test(id);
    const origem = (id) => (id.startsWith("Vegetacao") ? "vegetação natural" : id.startsWith("Pastagem") ? "pastagem" : destino(id) ? null : "outros");
    function des() {
      const lin = mesos.map((ms) => {
        const e = SR.find((s) => s.mesorregiao === ms && s.ato === ato); const tot = { "vegetação natural": 0, pastagem: 0, outros: 0 };
        e.links.forEach((l) => { const o = origem(l.source); if (destino(l.target) && o) tot[o] += l.value; });
        const s = tot["vegetação natural"] + tot.pastagem + tot.outros;
        return { ms, tot, s };
      });
      alvo.replaceChildren();
      const q = CX.quadro(alvo, { h: 250, m: { l: 130, r: 90, t: 16, b: 34 } });
      const x = d3.scaleLinear().domain([0, 1]).range([0, q.iw]), y = d3.scaleBand().domain(mesos).range([0, q.ih]).padding(0.25);
      CX.eixos(q, x, y, { xf: (v) => CX.pct(v), xl: "origem da área que virou agricultura ou mosaico no ato", grade: false });
      lin.forEach((l) => {
        let acc = 0;
        [["pastagem", C.pasto], ["vegetação natural", C.veg], ["outros", C.cinza]].forEach(([k, cc]) => {
          const w = l.s ? l.tot[k] / l.s : 0;
          q.g.append("rect").attr("x", x(acc) + 1).attr("y", y(l.ms)).attr("width", Math.max(0, x(w) - x(0) - 2)).attr("height", y.bandwidth()).attr("fill", cc)
            .on("mousemove", (ev) => CX.tip.mostra(ev, `${l.ms}, Ato ${ato}<br>${k}: ${f(l.tot[k], 2)} Mha (${CX.pct(w)})`)).on("mouseleave", CX.tip.esconde);
          if (w > 0.08) q.g.append("text").attr("class", "rot").attr("x", x(acc + w / 2)).attr("y", y(l.ms) + y.bandwidth() / 2 + 4).attr("text-anchor", "middle").style("fill", "#fff").style("font-weight", 700).text(CX.pct(w));
          acc += w;
        });
        q.g.append("text").attr("class", "rot-m").attr("x", q.iw + 6).attr("y", y(l.ms) + y.bandwidth() / 2 + 4).text(f(l.s, 2) + " Mha");
      });
      const sul = lin[0], norte = lin[4];
      txt.innerHTML = `Mesorregiões de sul a norte. No Ato ${ato}, ${CX.pct(sul.tot.pastagem / sul.s)} da área que virou agricultura ou mosaico no Sul Goiano veio de pastagem; no Norte Goiano, ${CX.pct(norte.tot["vegetação natural"] / norte.s)} veio de vegetação natural. À direita, a área total que entrou. Os fluxos muito pequenos não constam do arquivo e ficam de fora da conta.`;
    }
    des();
    host.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.pasto}"></i>pastagem</span><span><i style="background:${C.veg}"></i>vegetação natural</span><span><i style="background:${C.cinza}"></i>outros</span>` }));
  });

  /* ---------------- 6.7 Martins ---------------- */
  CX.def("martins", async (host) => {
    const b = await CX.base();
    const R = b.reg, V = b.veg_reg;
    const med = {
      area: ["área agropecuária (pasto + agricultura)", (r) => R["pasto_mha_" + r].map((p, i) => p + R["agric_mha_" + r][i])],
      boi: ["rebanho bovino", (r) => R["bovinos_mcab_" + r]],
      agric: ["agricultura", (r) => R["agric_mha_" + r]],
      veg: ["vegetação natural", (r) => V[r]],
    };
    const ctl = CX.ctrl(host);
    let k = "area";
    CX.seg(ctl, { opcoes: Object.entries(med).map(([kk, v]) => [kk, v[0]]), val: k, aoMudar: (v) => { k = v; des(); } });
    const alvo = h("div"); host.appendChild(alvo);
    const txt = CX.frase(host);
    function des() {
      const [nome, fn] = med[k];
      alvo.replaceChildren();
      const sul = fn("Sul"), norte = fn("Norte");
      const abs = k === "agric";
      CX.linhas(alvo, { anos: R.anos, h: 270, m: { l: 50, r: 70, t: 14 }, yl: abs ? "agricultura (Mha)" : `${nome} (1985 = 100)`, yf: (v) => f(v, abs ? 1 : 0), tf: (v) => f(v, abs ? 2 : 0),
        series: [{ nome: "Sul", cor: C.Sul, v: abs ? sul : indice(sul) }, { nome: "Norte", cor: C.Norte, v: abs ? norte : indice(norte) }] });
      const ch = (v) => v[v.length - 1] / v[0] - 1;
      txt.innerHTML = abs
        ? `Agricultura em milhões de hectares (em índice, o Norte explodiria a escala: parte de quase nada). O Sul vai de ${f(sul[0], 2)} para ${f(sul[39], 2)} Mha; o Norte, de ${f(norte[0], 2)} para ${f(norte[39], 2)}.`
        : `${nome}: Sul ${fs(100 * ch(sul), 0)}%, Norte ${fs(100 * ch(norte), 0)}% entre 1985 e 2024 (regiões do trabalho, em AMCs). O #51 mede a expansão de área com outra definição e chega a +93% no Norte e +14% no Sul. O contraste é o que a analogia com Martins nomeia; ela não o explica.`;
    }
    des();
  });
})();
