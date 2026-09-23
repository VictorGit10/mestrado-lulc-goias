/* Caderno de conceitos — Parte 1: o dado */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  /* ---------------- 1.1 Sensoriamento remoto e classificação ---------------- */
  CX.def("sr", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(11), NX = 18, NY = 10;
        // "verdade" do chão: mata à esquerda, pasto no meio, lavoura à direita, com bordas irregulares
        const px = [];
        for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
          const borda1 = 5 + 1.5 * Math.sin(j * 0.9) + (r() - 0.5) * 1.2;
          const borda2 = 12 + 1.2 * Math.cos(j * 0.7) + (r() - 0.5) * 1.2;
          const verd = i < borda1 ? "veg" : i < borda2 ? "pasto" : "agric";
          const base = { veg: 0.78, pasto: 0.5, agric: 0.24 }[verd];
          // pasto sujo e savana rala se parecem: o ruído do pasto é maior
          const ruido = verd === "pasto" ? 0.11 : 0.08;
          px.push({ i, j, verd, v: Math.max(0.02, Math.min(0.98, base + CX.normal(r) * ruido)) });
        }
        const ctl = CX.ctrl(c);
        const s1 = CX.slider(ctl, { rot: "limiar lavoura | pasto", min: 0.2, max: 0.5, passo: 0.01, val: 0.37, fmt: (v) => f(v, 2), aoMudar: desenha });
        const s2 = CX.slider(ctl, { rot: "limiar pasto | vegetação", min: 0.5, max: 0.8, passo: 0.01, val: 0.64, fmt: (v) => f(v, 2), aoMudar: desenha });
        const s3 = CX.slider(ctl, { rot: "zona de dúvida ±", min: 0, max: 0.1, passo: 0.005, val: 0, fmt: (v) => f(v, 3), aoMudar: desenha });
        const ctl2 = CX.ctrl(c);
        const vv = CX.check(ctl2, " mostrar a verdade do chão (contorno)", false, desenha);
        const q = CX.quadro(c, { w: 680, h: 350, m: { t: 6, r: 6, b: 90, l: 6 } });
        const cel = 680 / NX - 0.5, ch = 230 / NY;
        const gP = q.g.append("g");
        const hx = d3.scaleLinear().domain([0, 1]).range([20, 650]);
        const gH = q.g.append("g").attr("transform", `translate(0,${NY * ch + 18})`);
        const lei = CX.leitura(c);
        const nAc = CX.num(lei, "acertos entre os decididos", true), nDu = CX.num(lei, "pixels em \"não sei\""), nEr = CX.num(lei, "erros");
        function classe(v) {
          const t1 = s1.valor(), t2 = s2.valor(), d = s3.valor();
          if (Math.abs(v - t1) < d || Math.abs(v - t2) < d) return "mosaico";
          return v < t1 ? "agric" : v < t2 ? "pasto" : "veg";
        }
        function desenha() {
          let ac = 0, du = 0, er = 0;
          gP.selectAll("rect").data(px).join("rect")
            .attr("x", (d) => d.i * (680 / NX)).attr("y", (d) => d.j * ch).attr("width", cel).attr("height", ch - 0.5)
            .attr("fill", (d) => { const k = classe(d.v); if (k === "mosaico") du++; else if (k === d.verd) ac++; else er++; return C[k]; })
            .attr("stroke", (d) => (vv.valor() && classe(d.v) !== d.verd ? "#111" : "none")).attr("stroke-width", 1.6)
            .on("mousemove", (ev, d) => CX.tip.mostra(ev, `verdor medido: <b>${f(d.v, 2)}</b><br>verdade: ${nome(d.verd)}<br>classificado: ${nome(classe(d.v))}`))
            .on("mouseleave", CX.tip.esconde);
          nAc.set(CX.pct(ac / Math.max(1, ac + er)));
          nDu.set(String(du));
          nEr.set(String(er));
          // histograma do "verdor" por classe verdadeira, com os limiares
          gH.selectAll("*").remove();
          const bins = d3.bin().domain([0, 1]).thresholds(40);
          ["veg", "pasto", "agric"].forEach((k) => {
            const b = bins(px.filter((p) => p.verd === k).map((p) => p.v));
            gH.append("path").attr("fill", C[k]).attr("opacity", 0.55)
              .attr("d", d3.area().curve(d3.curveStep).x((d) => hx((d.x0 + d.x1) / 2)).y0(50).y1((d) => 50 - d.length * 3.2)(b));
          });
          gH.append("line").attr("x1", hx(0)).attr("x2", hx(1)).attr("y1", 50).attr("y2", 50).attr("stroke", "#bbb");
          [s1.valor(), s2.valor()].forEach((t) => {
            const dd = s3.valor();
            if (dd > 0) gH.append("rect").attr("x", hx(t - dd)).attr("width", hx(t + dd) - hx(t - dd)).attr("y", 0).attr("height", 50).attr("fill", C.mosaico).attr("opacity", 0.25);
            gH.append("line").attr("x1", hx(t)).attr("x2", hx(t)).attr("y1", -4).attr("y2", 54).attr("stroke", "#111").attr("stroke-width", 1.5);
          });
          gH.append("text").attr("class", "rot-m").attr("x", hx(0)).attr("y", 68).text("pouca planta (solo, lavoura na entressafra)");
          gH.append("text").attr("class", "rot-m").attr("x", hx(1)).attr("y", 68).attr("text-anchor", "end").text("muita planta (mata)");
        }
        const nome = (k) => ({ veg: "vegetação", pasto: "pastagem", agric: "lavoura", mosaico: "não sei (mosaico)" }[k]);
        desenha();
        c.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg}"></i>vegetação</span><span><i style="background:${C.pasto}"></i>pastagem</span><span><i style="background:${C.agric}"></i>lavoura</span><span><i style="background:${C.mosaico}"></i>"não sei"</span>` }));
        CX.frase(c, "Repare que os erros se concentram nas bordas e no pasto, cujas medidas se espalham mais. Abrir a zona de dúvida troca erros por \"não sei\": o mapa fica mais honesto e menos completo.");
      },
      async dados(c) {
        const d = (await CX.base()).go;
        const chaves = [["veg", "Vegetação natural"], ["pasto", "Pastagem"], ["mosaico", "Mosaico de Usos"], ["agric", "Agricultura"]];
        const linhas = d.anos.map((a, i) => ({ ano: a, veg: d.veg[i], pasto: d.pasto[i], mosaico: d.mosaico[i], agric: d.agric[i] }));
        const pilha = d3.stack().keys(chaves.map((k) => k[0]))(linhas);
        const q = CX.quadro(c, { h: 320, m: { l: 44, r: 120 } });
        const x = d3.scaleLinear().domain([1985, 2024]).range([0, q.iw]);
        const y = d3.scaleLinear().domain([0, 34]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: CX.anoF, yl: "milhões de hectares" });
        q.g.selectAll("path.cam").data(pilha).join("path").attr("class", "cam").attr("fill", (s) => C[s.key]).attr("stroke", "#fff").attr("stroke-width", 1)
          .attr("d", d3.area().x((p) => x(p.data.ano)).y0((p) => y(p[0])).y1((p) => y(p[1])));
        pilha.forEach((s, k) => { const u = s[s.length - 1]; q.g.append("text").attr("class", "rot").attr("x", q.iw + 6).attr("y", y((u[0] + u[1]) / 2) + 4).text(chaves[k][1]); });
        const cruz = q.g.append("line").attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("opacity", 0);
        q.g.append("rect").attr("width", q.iw).attr("height", q.ih).attr("fill", "transparent")
          .on("mousemove", (ev) => {
            const a = Math.round(x.invert(d3.pointer(ev)[0])), l = linhas[a - 1985]; if (!l) return;
            cruz.attr("x1", x(a)).attr("x2", x(a)).attr("opacity", 0.6);
            CX.tip.mostra(ev, `<b>${a}</b><br>` + chaves.map(([k, n]) => `${n}: ${f(l[k], 2)} Mha`).join("<br>"));
          }).on("mouseleave", () => { cruz.attr("opacity", 0); CX.tip.esconde(); });
        CX.frase(c, `Entre 1985 e 2024 a vegetação natural sai de ${f(d.veg[0], 1)} para ${f(d.veg[39], 1)} Mha e a agricultura de ${f(d.agric[0], 1)} para ${f(d.agric[39], 1)} Mha. A faixa do Mosaico é a "caixa do não sei" do classificador de verdade. Área total fora destes quatro grupos (água, urbano, outros) não aparece.`);
      },
    });
  });

  /* ---------------- 1.2 Cubo de dados (three.js) ---------------- */
  CX.def("cubo", async (host) => {
    const N = 16, ANOS = 40;
    const r = CX.rng(5);
    // trajetória de cada pixel: j=0 é o Sul. O Sul abriu antes e recebe lavoura depois.
    const traj = [];
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const lat = j / (N - 1);
      const agua = (i - 11) ** 2 + (j - 4) ** 2 < 2.2;
      const yP = 1972 + lat * 42 + CX.normal(r) * 7;         // ano em que vira pasto
      const querLav = r() < 0.75 * (1 - lat) ** 1.3;
      const yL = querLav ? Math.max(yP + 4, 1992 + lat * 25 + CX.normal(r) * 6) : 9999;
      const fica = r() < 0.1 + 0.35 * lat;                    // parte da vegetação nunca é convertida
      const seq = [];
      for (let t = 0; t < ANOS; t++) {
        const ano = 1985 + t;
        let k = "veg";
        if (agua) k = "agua";
        else if (!fica && ano >= yP) k = ano >= yL ? (r() < 0.12 && ano > 2016 ? "mosaico" : "agric") : "pasto";
        seq.push(k);
      }
      traj.push({ i, j, seq });
    }
    const topo = h("div", { class: "cx-grade2" });
    host.appendChild(topo);
    const esq = h("div"), dir = h("div");
    topo.append(esq, dir);
    const box3 = h("div", { class: "cx-3d" }, h("div", { class: "cx-carregando", text: "carregando a biblioteca 3D…" }));
    esq.appendChild(box3);
    const ctl = CX.ctrl(host);
    let ano = 2024, sel = null;
    const sAno = CX.slider(ctl, { rot: "fatia do ano", min: 1985, max: 2024, val: 2024, fmt: String, aoMudar: (v) => { ano = v; atualiza(); } });
    const bPlay = CX.btn(ctl, "▶ passar os anos", () => {
      if (tocando) { tocando(); tocando = null; bPlay.textContent = "▶ passar os anos"; return; }
      let t0 = null; bPlay.textContent = "❚❚ parar";
      tocando = CX.loop((t) => { if (t0 == null) t0 = t; const a = 1985 + Math.floor((t - t0) / 180) % 40; if (a !== ano) sAno.set(a); });
    });
    let tocando = null;

    // mapa plano (a fatia) + trajetória da coluna escolhida
    const qm = CX.quadro(dir, { w: 330, h: 330, m: { t: 18, r: 4, b: 4, l: 4 } });
    const cs = 322 / N;
    qm.g.append("text").attr("class", "rot-m").attr("y", -6).text("a fatia vista de cima (Norte no alto)");
    const celas = qm.g.selectAll("rect").data(traj).join("rect")
      .attr("x", (d) => d.i * cs).attr("y", (d) => (N - 1 - d.j) * cs).attr("width", cs - 1).attr("height", cs - 1).style("cursor", "pointer")
      .on("click", (_, d) => { sel = d; atualiza(); });
    const qt = CX.quadro(dir, { w: 330, h: 70, m: { t: 18, r: 4, b: 16, l: 4 } });
    const tt = qt.g.append("text").attr("class", "rot-m").attr("y", -6).text("clique numa célula para ver a coluna dela");
    const gT = qt.g.append("g");
    const lei = CX.leitura(host);
    const nums = { veg: CX.num(lei, "vegetação na fatia"), pasto: CX.num(lei, "pastagem"), agric: CX.num(lei, "lavoura") };

    // three.js
    let THREE = null, inst = null, cena, cam, ren, grupo, destaque, rodar = null;
    try {
      THREE = await import("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js");
    } catch (e) {
      box3.replaceChildren(h("div", { class: "cx-erro", text: "A biblioteca 3D não carregou (sem internet?). O mapa plano ao lado continua funcionando." }));
    }
    if (THREE) {
      box3.replaceChildren();
      cena = new THREE.Scene();
      cena.background = new THREE.Color(0xf6f5f0);
      cam = new THREE.PerspectiveCamera(38, 1.6, 0.1, 200);
      cam.position.set(22, 20, 26); cam.lookAt(0, 4, 0);
      ren = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true }); // permite capturar a imagem (impressão, miniatura)
      ren.setPixelRatio(Math.min(2, window.devicePixelRatio));
      box3.appendChild(ren.domElement);
      box3.appendChild(h("div", { class: "cx-3d-leg", text: "↕ tempo (1985 embaixo, 2024 em cima) · arraste para girar" }));
      cena.add(new THREE.AmbientLight(0xffffff, 0.75));
      const luz = new THREE.DirectionalLight(0xffffff, 0.9); luz.position.set(10, 30, 15); cena.add(luz);
      grupo = new THREE.Group(); cena.add(grupo);
      grupo.rotation.y = -0.5;
      const H = 0.26;
      const geo = new THREE.BoxGeometry(0.94, H * 0.9, 0.94);
      const mat = new THREE.MeshLambertMaterial();
      inst = new THREE.InstancedMesh(geo, mat, N * N * ANOS);
      const m4 = new THREE.Matrix4(), col = new THREE.Color();
      let k = 0;
      traj.forEach((p) => p.seq.forEach((cl, t) => {
        m4.makeTranslation(p.i - N / 2 + 0.5, t * H, -(p.j - N / 2 + 0.5));
        inst.setMatrixAt(k, m4); inst.setColorAt(k, col.set(C[cl])); k++;
      }));
      grupo.add(inst);
      destaque = new THREE.Mesh(new THREE.BoxGeometry(1.08, ANOS * H + 0.3, 1.08),
        new THREE.MeshBasicMaterial({ color: 0x111111, wireframe: true }));
      destaque.visible = false; grupo.add(destaque);
      const seta = new THREE.ArrowHelper(new THREE.Vector3(0, 0, -1), new THREE.Vector3(-N / 2 - 1.5, 0, N / 2), 5, 0x8b3a1d);
      grupo.add(seta);
      grupo.userData.H = H;
      const redim = () => { const w = box3.clientWidth, hh = box3.clientHeight; ren.setSize(w, hh, false); cam.aspect = w / hh; cam.updateProjectionMatrix(); };
      redim();
      new ResizeObserver(redim).observe(box3);
      let arr = null, rotY = -0.5, rotX = 0;
      box3.addEventListener("pointerdown", (e) => { arr = [e.clientX, e.clientY, rotY, rotX]; box3.setPointerCapture(e.pointerId); });
      box3.addEventListener("pointermove", (e) => { if (!arr) return; rotY = arr[2] + (e.clientX - arr[0]) * 0.01; rotX = Math.max(-0.5, Math.min(0.6, arr[3] + (e.clientY - arr[1]) * 0.006)); });
      box3.addEventListener("pointerup", () => { arr = null; });
      // renderiza só enquanto a peça está visível
      let visivel = true;
      new IntersectionObserver((es) => { visivel = es[0].isIntersecting; }).observe(box3);
      rodar = CX.loop(() => { if (!visivel) return; grupo.rotation.y = rotY; grupo.rotation.x = rotX; ren.render(cena, cam); });
    }

    function atualiza() {
      const t = ano - 1985;
      celas.attr("fill", (d) => C[d.seq[t]]).attr("stroke", (d) => (d === sel ? "#111" : "none")).attr("stroke-width", 2);
      const cont = { veg: 0, pasto: 0, agric: 0 };
      traj.forEach((p) => { const k = p.seq[t]; if (k in cont) cont[k]++; else if (k === "mosaico") cont.agric++; });
      Object.entries(nums).forEach(([k, n]) => n.set(CX.pct(cont[k] / (N * N))));
      if (sel) {
        tt.text(`coluna do pixel (${sel.i + 1}, ${sel.j + 1}): 1985 → 2024`);
        gT.selectAll("rect").data(sel.seq).join("rect").attr("x", (_, i) => i * 7.9).attr("width", 7.4).attr("height", 22)
          .attr("fill", (k) => C[k]).attr("opacity", (_, i) => (i <= t ? 1 : 0.25));
        gT.selectAll("text").data([1985, 2024]).join("text").attr("class", "rot-m").attr("x", (a) => (a - 1985) * 7.9).attr("y", 36).attr("text-anchor", (a) => (a > 2000 ? "end" : "start")).text(String);
      }
      if (inst) {
        const m4 = new THREE.Matrix4(), H = grupo.userData.H;
        let k = 0;
        traj.forEach((p) => p.seq.forEach((_, tt2) => {
          const vis = tt2 <= t;
          m4.makeScale(vis ? 1 : 0.0001, vis ? 1 : 0.0001, vis ? 1 : 0.0001);
          m4.setPosition(p.i - N / 2 + 0.5, tt2 * H, -(p.j - N / 2 + 0.5));
          inst.setMatrixAt(k++, m4);
        }));
        inst.instanceMatrix.needsUpdate = true;
        if (sel) { destaque.visible = true; destaque.position.set(sel.i - N / 2 + 0.5, (ANOS * H) / 2 - H / 2, -(sel.j - N / 2 + 0.5)); }
        ren.render(cena, cam); // um quadro já, sem depender da animação (aba oculta, impressão)
      }
    }
    sel = traj[3 * N + 4];
    atualiza();
    host.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg}"></i>vegetação</span><span><i style="background:${C.pasto}"></i>pastagem</span><span><i style="background:${C.agric}"></i>lavoura</span><span><i style="background:${C.mosaico}"></i>mosaico</span><span><i style="background:${C.agua}"></i>água</span><span>seta terracota = Norte</span>` }));
  });

  /* ---------------- 1.3 Onde colocar o Mosaico ---------------- */
  CX.def("mosaico", async (host) => {
    const d = (await CX.base()).go;
    const ctl = CX.ctrl(host);
    const q = CX.quadro(host, { h: 300, m: { l: 44, r: 150 } });
    const x = d3.scaleLinear().domain([1985, 2024]).range([0, q.iw]);
    const y = d3.scaleLinear().domain([0, 0.6]).range([q.ih, 0]);
    CX.eixos(q, x, y, { xf: CX.anoF, yf: (v) => CX.pct(v), yl: "parcela da área classificada nos 4 grupos" });
    const gL = q.g.append("g");
    const lei = CX.leitura(host);
    const nP = CX.num(lei, "pastagem em 2024"), nL = CX.num(lei, "lavoura em 2024"), nD = CX.num(lei, "área que some em 1985", true);
    const txt = CX.frase(host);
    const conv = CX.seg(ctl, {
      opcoes: [["propria", "categoria própria (D22/D26)"], ["lavoura", "somar à lavoura"], ["pasto", "somar ao pasto"], ["esquecer", "esquecer a classe (bug do #12)"]],
      val: "propria", aoMudar: desenha,
    });
    function desenha(v) {
      const ser = d.anos.map((_, i) => {
        let p = d.pasto[i], l = d.agric[i], m = d.mosaico[i], vg = d.veg[i];
        if (v === "lavoura") { l += m; m = 0; } else if (v === "pasto") { p += m; m = 0; }
        const tot = v === "esquecer" ? p + l + vg : p + l + m + vg;
        return { p: p / tot, l: l / tot, m: v === "esquecer" ? null : m / tot, v: vg / tot };
      });
      const series = [["p", "pastagem", C.pasto], ["l", "lavoura", C.agric], ["m", "mosaico", C.mosaico], ["v", "vegetação natural", C.veg]];
      gL.selectAll("*").remove();
      const rots = [];
      series.forEach(([k, n, cc]) => {
        if (ser[0][k] == null || (k === "m" && ser[0][k] === 0)) return;
        gL.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2.2)
          .attr("d", d3.line().x((_, i) => x(d.anos[i])).y((s) => y(s[k]))(ser));
        const t = gL.append("text").attr("class", "rot").attr("x", q.iw + 6);
        t.append("tspan").style("fill", cc).text("■ "); t.append("tspan").text(n);
        rots.push({ sel: t, y: y(ser[39][k]) + 4 });
      });
      CX.desempilha(rots, 8, q.ih);
      nP.set(CX.pct(ser[39].p, 1)); nL.set(CX.pct(ser[39].l, 1));
      const tot0 = d.pasto[0] + d.agric[0] + d.mosaico[0] + d.veg[0];
      nD.set(v === "esquecer" ? CX.pct(d.mosaico[0] / tot0, 1) : "0%");
      txt.innerHTML = {
        propria: "O Mosaico fica como está: a dúvida do classificador tem linha própria e não contamina a lavoura nem o pasto. É a convenção do trabalho.",
        lavoura: "Somar o Mosaico à lavoura dá o <b>teto</b> da lavoura, a régua \"agricultura ∪ mosaico\" da D26. É um limite superior, não uma correção.",
        pasto: "Somar ao pasto é a convenção oposta. No carbono, tratar o Mosaico como pastagem move a emissão líquida de 833 para 815 Mt — diferença de convenção, declarada.",
        esquecer: "Sem a classe 21, parte do estado some do numerador <i>e</i> do denominador. As parcelas sobem sem que nada tenha mudado no chão: foi o defeito do #12 original.",
      }[v];
    }
    desenha("propria");
  });

  /* ---------------- 1.4 Estoque × fluxo ---------------- */
  CX.def("fluxo", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c), ctl2 = CX.ctrl(c);
        const cx = [
          { nome: "Caixa A", t: CX.slider(ctl, { rot: "A torneira", min: 0, max: 10, val: 6, fmt: String }), r: CX.slider(ctl, { rot: "A ralo", min: 0, max: 10, val: 2, fmt: String }), n: 50, hist: [] },
          { nome: "Caixa B", t: CX.slider(ctl2, { rot: "B torneira", min: 0, max: 10, val: 3, fmt: String }), r: CX.slider(ctl2, { rot: "B ralo", min: 0, max: 10, val: 7, fmt: String }), n: 50, hist: [] },
        ];
        CX.btn(ctl2, "recomeçar no mesmo nível", () => cx.forEach((k) => { k.n = 50; k.hist = []; }));
        const q = CX.quadro(c, { h: 250, m: { t: 10, r: 10, b: 24, l: 10 } });
        const gx = [60, 250];
        const gs = cx.map((k, i) => {
          const g = q.g.append("g").attr("transform", `translate(${gx[i]},20)`);
          g.append("rect").attr("width", 110).attr("height", 180).attr("fill", "#fff").attr("stroke", "#555").attr("stroke-width", 2);
          const agua = g.append("rect").attr("x", 2).attr("width", 106).attr("fill", C.agua).attr("opacity", 0.75);
          const jT = g.append("rect").attr("x", 20).attr("y", -20).attr("width", 6).attr("fill", C.agua);
          const jR = g.append("rect").attr("x", 84).attr("y", 180).attr("width", 6).attr("fill", C.agua);
          const txt = g.append("text").attr("class", "rot-f").attr("x", 55).attr("y", 205).attr("text-anchor", "middle");
          return { agua, jT, jR, txt };
        });
        const x = d3.scaleLinear().domain([0, 120]).range([420, 660]), y = d3.scaleLinear().domain([0, 100]).range([200, 20]);
        q.g.append("text").attr("class", "rot-m").attr("x", 420).attr("y", 12).text("nível ao longo do tempo");
        q.g.append("line").attr("x1", 420).attr("x2", 660).attr("y1", 200).attr("y2", 200).attr("stroke", "#bbb");
        const lns = cx.map((_, i) => q.g.append("path").attr("fill", "none").attr("stroke", i ? C.acento : C.azul).attr("stroke-width", 2));
        let tAnt = null;
        return CX.loop((t) => {
          const dt = tAnt == null ? 0 : Math.min(0.05, (t - tAnt) / 1000); tAnt = t;
          cx.forEach((k, i) => {
            const vt = k.t.valor(), vr = k.r.valor();
            k.n = Math.max(0, Math.min(100, k.n + (vt - vr) * dt * 3));
            if (!k.hist.length || t - k.hist[k.hist.length - 1][0] > 200) { k.hist.push([t, k.n]); if (k.hist.length > 120) k.hist.shift(); }
            const g = gs[i];
            g.agua.attr("y", 180 - 1.78 * k.n).attr("height", 1.78 * k.n);
            g.jT.attr("height", vt > 0 ? 20 + 180 - 1.78 * k.n : 0).attr("width", 2 + vt * 0.9);
            g.jR.attr("height", vr > 0 && k.n > 0 ? 14 : 0).attr("width", 2 + vr * 0.9);
            g.txt.text(`${k.nome}: nível ${f(k.n, 0)} · fluxo ${fs(vt - vr, 0)}`);
            lns[i].attr("d", d3.line().x((_, j) => x(j)).y((p) => y(p[1]))(k.hist));
          });
        });
      },
      async dados(c) {
        const fb = (await CX.base()).fluxo_bl;
        const ctl = CX.ctrl(c);
        const nomes = { vegetacao_natural: "vegetação natural", pastagem: "pastagem", agricultura: "agricultura", mosaico: "mosaico" };
        const pares = [["vegetacao_natural", "pastagem"], ["pastagem", "agricultura"], ["pastagem", "mosaico"], ["vegetacao_natural", "mosaico"]];
        const sAto = CX.seg(ctl, { opcoes: [["I", "Ato I (1985–2000)"], ["II", "Ato II (2001–19)"], ["III", "Ato III (2020–24)"]], val: "I", aoMudar: desenha });
        const sPar = CX.seg(ctl, { opcoes: pares.map((p, i) => [i, `${nomes[p[0]]} ↔ ${nomes[p[1]]}`]), val: 0, aoMudar: desenha });
        const q = CX.quadro(c, { h: 220, m: { l: 260, r: 70, t: 10, b: 30 } });
        const txt = CX.frase(c);
        function desenha() {
          const [a, b] = pares[sPar.valor()], ato = sAto.valor();
          const ida = fb.find((r) => r.ato === ato && r.grupo_orig === a && r.grupo_dest === b);
          const volta = fb.find((r) => r.ato === ato && r.grupo_orig === b && r.grupo_dest === a);
          const lin = [
            [`bruto ${nomes[a]} → ${nomes[b]}`, ida.bruto_mha, C.acento],
            [`bruto ${nomes[b]} → ${nomes[a]}`, volta.bruto_mha, C.azul],
            ["saldo líquido", ida.liquido_mha, "#444"],
          ];
          const x = d3.scaleLinear().domain([Math.min(0, d3.min(lin, (l) => l[1])), d3.max(lin, (l) => l[1]) * 1.1]).range([0, q.iw]);
          const y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.3);
          CX.eixos(q, x, null, { xl: "milhões de hectares no ato" });
          q.g.selectAll(".b").remove();
          lin.forEach((l) => {
            q.g.append("rect").attr("class", "b").attr("x", x(Math.min(0, l[1]))).attr("y", y(l[0])).attr("width", Math.abs(x(l[1]) - x(0))).attr("height", y.bandwidth()).attr("fill", l[2]).attr("rx", 3);
            q.g.append("text").attr("class", "b rot").attr("x", -8).attr("y", y(l[0]) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(l[0]);
            q.g.append("text").attr("class", "b rot-f").attr("x", x(Math.max(0, l[1])) + 6).attr("y", y(l[0]) + y.bandwidth() / 2 + 4).text(f(l[1], 2));
          });
          const esc = ida.bruto_mha > 0 ? 1 - ida.liquido_mha / ida.bruto_mha : 0;
          txt.innerHTML = `No Ato ${ato}, ${f(ida.bruto_mha, 2)} Mha passaram de ${nomes[a]} para ${nomes[b]} e ${f(volta.bruto_mha, 2)} Mha fizeram o caminho contrário. Quem olha só o saldo (${f(ida.liquido_mha, 2)} Mha) não vê ${CX.pct(Math.max(0, esc))} do movimento de ida.`;
        }
        desenha();
      },
    });
  });

  /* ---------------- 1.5 Censura ---------------- */
  CX.def("censura", (host) => {
    const r = CX.rng(21);
    const past = [];
    for (let k = 0; k < 22; k++) past.push({ reg: "Sul", n: Math.round(Math.min(2020, 1971 + CX.normal(r) * 11)) });
    for (let k = 0; k < 22; k++) past.push({ reg: "Norte", n: Math.round(Math.min(2021, 1995 + CX.normal(r) * 9)) });
    past.sort((a, b) => (a.reg === b.reg ? a.n - b.n : a.reg < b.reg ? 1 : -1));
    const ctl = CX.ctrl(host);
    const s = CX.slider(ctl, { rot: "a série começa em", min: 1950, max: 2005, val: 1985, fmt: String, aoMudar: desenha });
    const q = CX.quadro(host, { h: 360, m: { l: 52, r: 16, t: 8, b: 26 } });
    const x = d3.scaleLinear().domain([1940, 2024]).range([0, q.iw]);
    const y = d3.scaleBand().domain(past.map((_, i) => i)).range([0, q.ih]).padding(0.25);
    CX.eixos(q, x, null, { xf: CX.anoF });
    q.g.append("text").attr("class", "rot-f").attr("x", -48).attr("y", y(5)).text("Sul");
    q.g.append("text").attr("class", "rot-f").attr("x", -48).attr("y", y(27)).text("Norte");
    const janela = q.g.append("rect").attr("y", -4).attr("height", q.ih + 4).attr("fill", "#f3efe3");
    const bar = q.g.selectAll("g.p").data(past).join("g").attr("class", "p");
    const bOculto = bar.append("rect").attr("height", y.bandwidth()).attr("fill", "url(#cx-hach)");
    const bVisto = bar.append("rect").attr("height", y.bandwidth()).attr("rx", 2);
    const defs = q.svg.append("defs");
    const pat = defs.append("pattern").attr("id", "cx-hach").attr("width", 6).attr("height", 6).attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("rect").attr("width", 6).attr("height", 6).attr("fill", "#eee");
    pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6).attr("stroke", "#aaa").attr("stroke-width", 2);
    const inicio = q.g.append("line").attr("y1", -4).attr("y2", q.ih).attr("stroke", C.acento).attr("stroke-width", 2);
    const inicioT = q.g.append("text").attr("class", "rot-f").attr("y", -8).attr("text-anchor", "middle").style("fill", C.acento);
    const tab = h("table", { class: "cx-tab" });
    host.appendChild(tab);
    function desenha() {
      const t0 = s.valor();
      janela.attr("x", x(t0)).attr("width", x(2024) - x(t0));
      inicio.attr("x1", x(t0)).attr("x2", x(t0)); inicioT.attr("x", x(t0)).text("início da série");
      bar.attr("transform", (_, i) => `translate(0,${y(i)})`);
      bOculto.attr("x", (d) => x(d.n)).attr("width", (d) => Math.max(0, x(Math.max(d.n, Math.min(t0, 2024))) - x(d.n)));
      bVisto.attr("x", (d) => x(Math.max(d.n, t0))).attr("width", (d) => x(2024) - x(Math.max(d.n, t0)))
        .attr("fill", (d) => (d.n < t0 ? C.cinza : C.pasto));
      const linhas = ["Sul", "Norte"].map((rg) => {
        const p = past.filter((d) => d.reg === rg);
        const cens = p.filter((d) => d.n < t0).length;
        return [rg, cens / p.length, S.mediana(p.map((d) => 2024 - d.n)), S.mediana(p.map((d) => 2024 - Math.max(d.n, t0))),
          p.some((d) => d.n >= t0) ? S.mediana(p.filter((d) => d.n >= t0).map((d) => 2024 - d.n)) : null];
      });
      tab.innerHTML = `<tr><th>região</th><th>censuradas</th><th>idade verdadeira (mediana)</th><th>mediana com censuradas</th><th>mediana sem censuradas</th></tr>` +
        linhas.map((l) => `<tr><td>${l[0]}</td><td>${CX.pct(l[1])}</td><td>${l[2]} anos</td><td>${l[3]} anos</td><td>${l[4] == null ? "—" : l[4] + " anos"}</td></tr>`).join("");
    }
    desenha();
    host.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.pasto}"></i>idade observável</span><span><i style="background:${C.cinza}"></i>pastagem já existente no início (censurada)</span><span><i style="background:repeating-linear-gradient(45deg,#eee 0 3px,#aaa 3px 5px)"></i>parte da história que a série não vê</span>` }));
    CX.frase(host, "Com a série começando em 1985, quase todo o Sul fica censurado e sua mediana \"com censuradas\" encolhe muito abaixo da verdadeira. Tirar as censuradas também não resolve: sobram só as pastagens novas. Qualquer comparação Sul × Norte precisa declarar a censura de cada lado.");
  });

  /* ---------------- 1.6 Censo, amostra e peso ---------------- */
  CX.def("censo", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sA = CX.slider(ctl, { rot: "alunos na turma A", min: 10, max: 120, val: 60, fmt: String, aoMudar: des });
        const sB = CX.slider(ctl, { rot: "alunos na turma B", min: 10, max: 120, val: 10, fmt: String, aoMudar: des });
        const ctl2 = CX.ctrl(c);
        const pond = CX.check(ctl2, " pesar cada turma pelo seu tamanho", false, des);
        const q = CX.quadro(c, { h: 220, m: { l: 10, r: 10, t: 14, b: 30 } });
        const lei = CX.leitura(c);
        const nV = CX.num(lei, "média verdadeira da escola"), nE = CX.num(lei, "estimativa pelas 3 + 3 medidas", true), nP = CX.num(lei, "peso da turma B na estimativa");
        function des() {
          const nA = sA.valor(), nB = sB.valor();
          const verd = (nA * 150 + nB * 170) / (nA + nB);
          const wB = pond.valor() ? nB / (nA + nB) : 0.5;
          const est = 150 * (1 - wB) + 170 * wB;
          nV.set(f(verd, 1) + " cm"); nE.set(f(est, 1) + " cm"); nP.set(CX.pct(wB));
          q.g.selectAll("*").remove();
          [["A", nA, 150, C.azul, 20], ["B", nB, 170, C.acento, 350]].forEach(([n, k, alt, cc, x0]) => {
            const cols = 20;
            for (let i = 0; i < k; i++) {
              const sorteado = i < 3;
              q.g.append("circle").attr("cx", x0 + (i % cols) * 15).attr("cy", 20 + Math.floor(i / cols) * 15).attr("r", 5.5)
                .attr("fill", sorteado ? cc : "#fff").attr("stroke", cc);
            }
            q.g.append("text").attr("class", "rot-f").attr("x", x0).attr("y", 8).text(`Turma ${n}: ${k} alunos · média ${alt} cm`);
          });
        }
        des();
        CX.frase(c, "O sorteio é o mesmo nos dois casos: 3 alunos por turma. O que muda a resposta é o peso na hora de juntar. Sem ponderar, uma turma de 10 vale tanto quanto uma de 60.");
      },
      dados(c) {
        const q = CX.quadro(c, { h: 250, m: { l: 50, r: 20, t: 20, b: 34 } });
        const dados = [["2020", 22.2, 43.2], ["2024", 24.5, 11.2]];
        const x0 = d3.scaleBand().domain(dados.map((d) => d[0])).range([0, q.iw]).padding(0.35);
        const x1 = d3.scaleBand().domain(["amostra", "censo"]).range([0, x0.bandwidth()]).padding(0.1);
        const y = d3.scaleLinear().domain([0, 50]).range([q.ih, 0]);
        CX.eixos(q, x0, y, { yf: (v) => v + "%", yl: "peso do ano no agregado da idade do pasto", xt: 2 });
        dados.forEach(([a, am, ce]) => {
          [["amostra", am, C.cinza], ["censo", ce, C.acento]].forEach(([k, v, cc]) => {
            q.g.append("rect").attr("x", x0(a) + x1(k)).attr("y", y(v)).attr("width", x1.bandwidth()).attr("height", q.ih - y(v)).attr("fill", cc).attr("rx", 3);
            q.g.append("text").attr("class", "rot-f").attr("x", x0(a) + x1(k) + x1.bandwidth() / 2).attr("y", y(v) - 5).attr("text-anchor", "middle").text(f(v, 1) + "%");
            q.g.append("text").attr("class", "rot-m").attr("x", x0(a) + x1(k) + x1.bandwidth() / 2).attr("y", q.ih - 6).attr("text-anchor", "middle").style("fill", "#fff").text(k);
          });
        });
        CX.frase(c, "A amostra de 2.000 pixels por ano dava a todo ano o mesmo peso. No censo, 2020 (um ano de conversão intensa) pesa quase o dobro, e 2024 menos da metade. Por ano, a amostra acertava a mediana; no agregado, o erro era de ponderação.");
      },
    });
  });

  /* ---------------- 1.7 AMC ---------------- */
  CX.def("amc", async (host) => {
    const m = await CX.dado("metodo_centro_massa.json");
    const grid = h("div", { class: "cx-grade2" });
    host.appendChild(grid);
    const esq = h("div"), dir = h("div");
    grid.append(esq, dir);
    const q = CX.quadro(esq, { w: 360, h: 400, m: { t: 4, r: 4, b: 4, l: 4 } });
    const cs = d3.scaleSequential(d3.interpolateRgb("#f1e6d9", "#8b3a1d")).domain([1, 6]);
    const mp = CX.mapaAMC(q.g, m, q.iw, q.ih);
    const info = h("div", { class: "cx-frase", html: "Passe o mouse sobre uma AMC." });
    mp.sel.attr("fill", (d) => cs(Math.min(6, d.nmun)))
      .on("mouseenter", function (ev, d) {
        d3.select(this).attr("stroke", "#111").attr("stroke-width", 1.6).raise();
        info.innerHTML = `<b>AMC ${d.nome}</b> · ${d.nmun} município${d.nmun > 1 ? "s" : ""} de hoje: ${d.munis.join(", ")}. Área: ${f(d.area, 0)} km².`;
      })
      .on("mouseleave", function () { d3.select(this).attr("stroke", "#fff").attr("stroke-width", 0.6); });
    esq.appendChild(h("div", { class: "cx-leg", html: `cor: quantos municípios de hoje cada AMC reúne (1 → 6 ou mais) · ${m.amc.filter((a) => a.nmun > 1).length} das 166 AMCs juntam mais de um` }));
    esq.appendChild(info);
    const qd = CX.quadro(dir, { w: 360, h: 300, m: { l: 50, r: 20, t: 30, b: 34 } });
    const ondas = [["1989", 73, 12], ["1993", 81, 31], ["1997", 43, 9], ["2001", 43, 4]];
    const x = d3.scaleLinear().domain([0, 90]).range([0, qd.iw]);
    const y = d3.scaleBand().domain(ondas.map((o) => o[0])).range([0, qd.ih]).padding(0.4);
    CX.eixos(qd, x, y, { xf: (v) => "−" + v + "%", xl: "pior queda de rebanho num único ano", grade: false });
    qd.g.append("text").attr("class", "rot-f").attr("y", -12).text("Ondas de emancipação");
    ondas.forEach(([a, mu, am]) => {
      const yy = y(a) + y.bandwidth() / 2;
      qd.g.append("line").attr("x1", x(am)).attr("x2", x(mu)).attr("y1", yy).attr("y2", yy).attr("stroke", "#bbb").attr("stroke-width", 3);
      qd.g.append("circle").attr("cx", x(mu)).attr("cy", yy).attr("r", 7).attr("fill", C.acento);
      qd.g.append("circle").attr("cx", x(am)).attr("cy", yy).attr("r", 7).attr("fill", C.azul);
      qd.g.append("text").attr("class", "rot").attr("x", x(mu)).attr("y", yy - 11).attr("text-anchor", "middle").text("−" + mu + "%");
      qd.g.append("text").attr("class", "rot").attr("x", x(am)).attr("y", yy - 11).attr("text-anchor", "middle").text("−" + am + "%");
    });
    dir.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.acento}"></i>pior município</span><span><i style="background:${C.azul}"></i>pior AMC</span>` }));
    CX.frase(dir, "Em 1993, Mambaí perde 81% do rebanho num ano: é o rebanho dos distritos emancipados saindo da conta. Somados pai e filhos, a pior queda daquele ano cai para 31%.");
  });

  /* ---------------- 1.8 Projeção ---------------- */
  CX.def("proj", (host) => {
    const ctl = CX.ctrl(host);
    const s = CX.slider(ctl, { rot: "latitude", min: -80, max: 0, val: -16, fmt: (v) => f(Math.abs(v), 0) + "° S", aoMudar: des });
    const grid = h("div", { class: "cx-grade2" });
    host.appendChild(grid);
    const esq = h("div"), dir = h("div"); grid.append(esq, dir);
    const qg = CX.quadro(esq, { w: 320, h: 320, m: { t: 10, r: 10, b: 10, l: 10 } });
    const proj = d3.geoOrthographic().scale(145).translate([150, 150]).rotate([50, 20]);
    const path = d3.geoPath(proj);
    qg.g.append("path").datum({ type: "Sphere" }).attr("d", path).attr("fill", "#eef3f6").attr("stroke", "#9bb");
    qg.g.append("path").datum(d3.geoGraticule().step([10, 10])()).attr("d", path).attr("fill", "none").attr("stroke", "#b9c6cc").attr("stroke-width", 0.7);
    const faixa = qg.g.append("path").attr("fill", C.pasto).attr("opacity", 0.35);
    faixa.datum({ type: "Polygon", coordinates: [[[-53.2, -19.5], [-45.9, -19.5], [-45.9, -12.4], [-53.2, -12.4], [-53.2, -19.5]]] }).attr("d", path);
    const cel = qg.g.append("path").attr("fill", C.acento).attr("opacity", 0.8);
    const qr = CX.quadro(dir, { w: 340, h: 320, m: { t: 30, r: 10, b: 30, l: 10 } });
    const k = 1.9;
    const rLat = qr.g.append("rect").attr("fill", "none").attr("stroke", "#999").attr("stroke-dasharray", "4 3");
    const rLon = qr.g.append("rect").attr("fill", C.acento).attr("opacity", 0.2).attr("stroke", C.acento);
    const t1 = qr.g.append("text").attr("class", "rot-f"), t2 = qr.g.append("text").attr("class", "rot");
    qr.g.append("text").attr("class", "rot-m").attr("y", -12).text("tracejado: 1° × 1° no equador · cheio: na latitude escolhida");
    const lei = CX.leitura(host);
    const nL = CX.num(lei, "1° de longitude", true), nA = CX.num(lei, "1° de latitude"), nE = CX.num(lei, "erro ao tratar grau como igual");
    function des() {
      const lat = s.valor(), klon = 111.32 * Math.cos((lat * Math.PI) / 180), klat = 110.6;
      cel.datum({ type: "Polygon", coordinates: [[[-50, lat], [-40, lat], [-40, Math.min(0, lat + 10)], [-50, Math.min(0, lat + 10)], [-50, lat]]] }).attr("d", path);
      rLat.attr("x", 20).attr("y", 20).attr("width", 111.32 * k).attr("height", klat * k);
      rLon.attr("x", 20).attr("y", 20).attr("width", klon * k).attr("height", klat * k);
      t1.attr("x", 20).attr("y", 20 + klat * k + 20).text(`${f(klon, 1)} km de largura × ${f(klat, 1)} km de altura`);
      t2.attr("x", 20).attr("y", 20 + klat * k + 38).text(lat <= -12.4 && lat >= -19.5 ? "dentro da faixa de latitude de Goiás" : "");
      nL.set(f(klon, 1) + " km"); nA.set(f(klat, 1) + " km"); nE.set(CX.pct(1 - klon / klat, 1));
    }
    des();
    CX.frase(host, "Em Goiás, um grau de longitude é 3% a 5% mais curto que um de latitude. Uma média de coordenadas feita em graus mistura as duas réguas; por isso a conta dos centros de massa é feita em metros, na projeção EPSG:5880.");
  });

  /* ---------------- 1.9 Fontes e janelas ---------------- */
  CX.def("fontes", (host) => {
    const F = [
      ["MapBiomas 10.1", 1985, 2024, "Uso e cobertura da terra, 30 m, anual. Estoques, matrizes de transição, centros de massa, idade da pastagem. A espinha dorsal."],
      ["MapBiomas Fogo", 1985, 2024, "Área queimada. Só como camada descritiva (centro de massa do fogo em vegetação natural)."],
      ["IBGE PAM", 1985, 2024, "Área plantada e colhida, produção e rendimento das lavouras. É a âncora externa da soja (verbete 5.1)."],
      ["IBGE PPM", 1985, 2024, "Efetivo do rebanho bovino, leite. É o peso do centro de massa do rebanho."],
      ["Ipeadata (câmbio, preços)", 1985, 2024, "Câmbio real efetivo e cotações internacionais. O shifter do desenho de interação (verbete 4.10)."],
      ["Contas Regionais (PIB)", 1999, 2021, "PIB municipal e valor adicionado por setor, deflacionados pelo IPCA."],
      ["PRODES/INPE", 2001, 2024, "Aferição externa das séries de supressão de vegetação. Não é insumo."],
      ["Trase (soja)", 2004, 2022, "Cadeia de comercialização por município de origem. 44,6% do volume é esmagamento doméstico."],
      ["Trase (boi)", 2011, 2023, "Exportação de carne bovina por município de origem."],
      ["SICOR/BACEN", 2013, 2024, "Crédito rural por município, finalidade e produto."],
      ["FIRJAN IFDM (revista)", 2013, 2023, "Desenvolvimento municipal. Não emenda com a série anterior (2005–2016)."],
      ["Censo Agro 2017", 2017, 2017, "Plantio direto, calcário, orientação técnica: só um ano, transversal."],
    ];
    let marcados = new Set([0, 9]);
    const q = CX.quadro(host, { h: 44 + F.length * 24, m: { l: 176, r: 16, t: 26, b: 26 } });
    const x = d3.scaleLinear().domain([1985, 2024.9]).range([0, q.iw]);
    const y = d3.scaleBand().domain(F.map((_, i) => i)).range([0, q.ih]).padding(0.28);
    CX.eixos(q, x, null, { xf: CX.anoF });
    const faixa = q.g.append("rect").attr("y", -8).attr("height", q.ih + 8).attr("fill", "#1a1a1a").attr("opacity", 0.08);
    const faixaT = q.g.append("text").attr("class", "rot-f").attr("y", -12);
    const linhas = q.g.selectAll("g.f").data(F).join("g").attr("class", "f").attr("transform", (_, i) => `translate(0,${y(i)})`).style("cursor", "pointer");
    const barras = linhas.append("rect").attr("x", (d) => x(d[1])).attr("width", (d) => Math.max(6, x(d[2] + 0.9) - x(d[1]))).attr("height", y.bandwidth()).attr("rx", 3);
    const rot = linhas.append("text").attr("class", "rot").attr("x", -8).attr("y", y.bandwidth() / 2 + 4).attr("text-anchor", "end").text((d) => d[0]);
    const papel = CX.frase(host);
    linhas.on("click", (_, d) => { const i = F.indexOf(d); marcados.has(i) ? marcados.delete(i) : marcados.add(i); papel.innerHTML = `<b>${d[0]}</b> (${d[1]}${d[2] !== d[1] ? "–" + d[2] : ""}): ${d[3]}`; des(); });
    const lei = CX.leitura(host);
    const nA = CX.num(lei, "anos em comum", true), nI = CX.num(lei, "intervalos anuais (primeiras diferenças)");
    function des() {
      barras.attr("fill", (_, i) => (marcados.has(i) ? C.acento : "#d8d4c8"));
      rot.style("font-weight", (_, i) => (marcados.has(i) ? 700 : 400));
      const sel = F.filter((_, i) => marcados.has(i));
      const a = d3.max(sel, (d) => d[1]), b = d3.min(sel, (d) => d[2]);
      if (!sel.length || a > b) { faixa.attr("width", 0); faixaT.text(sel.length ? "sem ano em comum" : ""); nA.set("0"); nI.set("0"); return; }
      faixa.attr("x", x(a)).attr("width", x(b + 0.9) - x(a));
      faixaT.attr("x", x(a)).text(`janela comum: ${a}${b !== a ? "–" + b : ""}`);
      nA.set(String(b - a + 1)); nI.set(String(Math.max(0, b - a)));
    }
    des();
    papel.innerHTML = "Com MapBiomas e SICOR marcados, a janela comum é 2013–2024. Clique em outras fontes para ver a janela encolher.";
  });

  /* ---------------- 1.10 Deflação ---------------- */
  CX.def("defl", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sI = CX.slider(ctl, { rot: "inflação ao ano", min: 0, max: 15, passo: 0.5, val: 6, fmt: (v) => f(v, 1) + "%", aoMudar: des });
        const sR = CX.slider(ctl, { rot: "ganho real ao ano", min: -3, max: 5, passo: 0.5, val: 1, fmt: (v) => f(v, 1) + "%", aoMudar: des });
        const q = CX.quadro(c, { h: 260, m: { l: 60, r: 110 } });
        const lei = CX.leitura(c);
        const nN = CX.num(lei, "salário nominal no ano 30"), nR = CX.num(lei, "salário em reais do ano 0", true), nP = CX.num(lei, "pães que ele compra");
        function des() {
          const i = sI.valor() / 100, g = sR.valor() / 100;
          const anos = d3.range(0, 31);
          const nom = anos.map((t) => 1000 * Math.pow((1 + i) * (1 + g), t)), real = anos.map((t) => 1000 * Math.pow(1 + g, t));
          const x = d3.scaleLinear().domain([0, 30]).range([0, q.iw]), y = d3.scaleLinear().domain([0, d3.max(nom) * 1.05]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "anos", yf: (v) => "R$ " + f(v, 0), yl: "salário" });
          q.g.selectAll(".l").remove();
          [[nom, C.cinza, "nominal"], [real, C.acento, "real"]].forEach(([v, cc, n]) => {
            q.g.append("path").attr("class", "l").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2.2).attr("d", d3.line().x((_, t) => x(t)).y((p) => y(p))(v));
            q.g.append("text").attr("class", "l rot").attr("x", q.iw + 5).attr("y", y(v[30]) + 4).text(n);
          });
          nN.set("R$ " + f(nom[30], 0)); nR.set("R$ " + f(real[30], 0)); nP.set(f(real[30] / 0.2, 0));
        }
        des();
      },
      async dados(c) {
        const d = (await CX.base()).macro;
        const pts = d.anos.map((a, i) => [a, d.credito_bi[i]]).filter((p) => p[1] != null && p[0] >= 2013);
        const q = CX.quadro(c, { h: 260, m: { l: 50, r: 16, t: 20 } });
        const x = d3.scaleBand().domain(pts.map((p) => p[0])).range([0, q.iw]).padding(0.25);
        const y = d3.scaleLinear().domain([0, 38]).range([q.ih, 0]);
        CX.eixos(q, x, y, { yl: "crédito rural de Goiás, R$ bilhões de dez/2024" });
        q.g.selectAll("rect.b").data(pts).join("rect").attr("class", "b").attr("x", (p) => x(p[0])).attr("width", x.bandwidth())
          .attr("y", (p) => y(p[1])).attr("height", (p) => q.ih - y(p[1])).attr("rx", 3).attr("fill", (p) => (p[0] >= 2020 ? C.acento : C.cinza))
          .on("mousemove", (ev, p) => CX.tip.mostra(ev, `<b>${p[0]}</b><br>R$ ${f(p[1], 1)} bi (dez/2024)`)).on("mouseleave", CX.tip.esconde);
        q.g.selectAll("text.v").data(pts).join("text").attr("class", "v rot-m").attr("x", (p) => x(p[0]) + x.bandwidth() / 2).attr("y", (p) => y(p[1]) - 4).attr("text-anchor", "middle").text((p) => f(p[1], 1));
        CX.frase(c, "Em reais de dezembro de 2024, a média sobe de 14,3 (2013–2019) para 24,1 bilhões (Ato III, em terracota), mas a série dispara em 2021–2022 e desaba em 2023–2024. A média esconde o formato, e é por isso que o trabalho apoia a \"demanda alta\" do Ato III no câmbio, no preço e na soja plantada, não na média do crédito.");
      },
    });
  });

  /* ---------------- 1.11 Rotinas reprodutíveis ---------------- */
  CX.def("pipe", (host) => {
    const N = [
      ["fontes", "Fontes públicas", 20, 60, "MapBiomas, IBGE/SIDRA, Ipeadata, BACEN, FIRJAN, Embrapa, INPE, Trase. Nada é recebido pronto de terceiros: tudo é buscado na origem."],
      ["coleta", "Coleta automatizada", 150, 60, "scripts/coleta_*.py (SIDRA, SICOR, drivers macro, IFDM…) e rotinas no Google Earth Engine para os rasters. Buscam a série na origem, com cache local."],
      ["raw", "data/raw (cache)", 280, 20, "Arquivos brutos como vieram da fonte. Fora do controle de versão por tamanho; a data de acesso de cada fonte é a data do arquivo."],
      ["proc", "data/processed", 280, 100, "Tabelas limpas e padronizadas (painel municipal, painel por AMC, séries regionais). Reconstruível a partir do raw, offline."],
      ["rotinas", "58 rotinas (#1…#58)", 410, 60, "scripts/*.py, uma pergunta por rotina, com ficha em Textos/pipelines/ (pergunta, dependências, comando, saídas, limitações). O número nunca é renumerado."],
      ["outputs", "outputs/", 540, 60, "Tabelas e figuras gravadas pelas rotinas. Todo número exibido deve ser rastreável até um desses arquivos."],
      ["viz", "Visualização", 670, 20, "Visualizacao/: o site. Consome um recorte leve, versionado junto com ele."],
      ["texto", "Texto (qualificação)", 670, 100, "qualificacao/: abnTeX2. O apêndice de especificações é gerado a partir dos arquivos das rotinas, nenhum coeficiente digitado à mão."],
      ["ci", "CI: verificar-viz", 670, 180, "A cada envio que toca a visualização: sobe o site num navegador sem interface e falha se um número-âncora sumiu, se o console acusou erro ou se um número derrubado reapareceu.", true],
      ["ver", "verificar.py", 540, 180, "Seis invariantes do texto: ponteiro sem destino, citação sem entrada, obra ausente da lista de leitura, sigla antes de definida, calibragem perdida, decisão citada sem registro.", true],
    ];
    const A = [["fontes", "coleta"], ["coleta", "raw"], ["raw", "proc"], ["proc", "rotinas"], ["rotinas", "outputs"], ["outputs", "viz"], ["outputs", "texto"], ["viz", "ci"], ["texto", "ver"]];
    const q = CX.quadro(host, { w: 800, h: 240, m: { t: 10, r: 10, b: 10, l: 10 } });
    const pos = Object.fromEntries(N.map((n) => [n[0], n]));
    const defs = q.svg.append("defs");
    defs.append("marker").attr("id", "cx-seta").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7).attr("orient", "auto")
      .append("path").attr("d", "M0,0L10,5L0,10z").attr("fill", "#888");
    A.forEach(([a, b]) => {
      const p = pos[a], r = pos[b];
      q.g.append("line").attr("x1", p[2] + 110).attr("y1", p[3] + 18).attr("x2", r[2] + (r[2] > p[2] ? 0 : 55)).attr("y2", r[3] + (r[3] > p[3] + 40 ? 0 : 18))
        .attr("stroke", "#aaa").attr("stroke-width", 1.5).attr("marker-end", "url(#cx-seta)");
    });
    const info = CX.frase(host, "Clique numa etapa.");
    const g = q.g.selectAll("g.n").data(N).join("g").attr("class", "n").attr("transform", (n) => `translate(${n[2]},${n[3]})`).style("cursor", "pointer");
    const r = g.append("rect").attr("width", 110).attr("height", 36).attr("rx", 8).attr("fill", (n) => (n[5] ? "#f6e3da" : "#fff")).attr("stroke", (n) => (n[5] ? C.acento : "#999"));
    g.append("text").attr("class", "rot").attr("x", 55).attr("y", 22).attr("text-anchor", "middle").style("font-size", "11px").text((n) => n[1]);
    g.on("click", function (_, n) { r.attr("stroke-width", 1); d3.select(this).select("rect").attr("stroke-width", 3); info.innerHTML = `<b>${n[1]}</b>: ${n[4]}`; });
  });
})();
