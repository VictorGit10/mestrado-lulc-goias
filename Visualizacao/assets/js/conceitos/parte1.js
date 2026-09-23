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

  /* ---------------- 1.2 Cubo de dados (desenho isométrico, sem biblioteca 3D) ---------------- */
  CX.def("cubo", (host) => {
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
    const px = (i, j) => traj[j * N + i];
    const ctl = CX.ctrl(host);
    let ano = 2024, sel = null, tocando = null;
    const sAno = CX.slider(ctl, { rot: "fatia do ano (topo do cubo)", min: 1985, max: 2024, val: 2024, fmt: String, aoMudar: (v) => { ano = v; atualiza(); } });
    const bPlay = CX.btn(ctl, "▶ passar os anos", () => {
      if (tocando) { tocando(); tocando = null; bPlay.textContent = "▶ passar os anos"; return; }
      let t0 = null; bPlay.textContent = "❚❚ parar";
      tocando = CX.loop((t) => { if (t0 == null) t0 = t; const a = 1985 + Math.floor((t - t0) / 220) % 40; if (a !== ano) sAno.set(a); });
    });
    const topo = h("div", { class: "cx-grade2" });
    host.appendChild(topo);
    const esq = h("div"), dir = h("div");
    topo.append(esq, dir);

    // cubo isométrico: u = coluna (oeste→leste), v = linha contada do norte (0) para o sul (N)
    const qi = CX.quadro(esq, { w: 380, h: 440, m: { t: 4, r: 4, b: 4, l: 4 } });
    const s = 10.5, a = s * Math.cos(Math.PI / 6), b = s * Math.sin(Math.PI / 6), hz = 5.2;
    const ox = qi.iw / 2, oy = 14 + ANOS * hz;
    const P = (u, v, z) => [ox + (u - v) * a, oy + (u + v) * b - z * hz];
    const poli = (pts) => "M" + pts.map((p) => p[0].toFixed(1) + "," + p[1].toFixed(1)).join("L") + "Z";
    const gTopo = qi.g.append("g"), gEsq = qi.g.append("g"), gDir = qi.g.append("g"), gMarca = qi.g.append("g");
    const escurece = (cc, k) => d3.color(cc).darker(k).formatHex();

    // mapa plano (a fatia) + trajetória da coluna escolhida
    const qm = CX.quadro(dir, { w: 330, h: 350, m: { t: 24, r: 4, b: 4, l: 4 } });
    const cs = 322 / N;
    qm.g.append("text").attr("class", "rot-m").attr("y", -8).text("a fatia vista de cima (Norte no alto) · clique numa célula");
    const celas = qm.g.selectAll("rect").data(traj).join("rect")
      .attr("x", (d) => d.i * cs).attr("y", (d) => (N - 1 - d.j) * cs).attr("width", cs - 1).attr("height", cs - 1).style("cursor", "pointer")
      .on("click", (_, d) => { sel = d; atualiza(); });
    const qt = CX.quadro(dir, { w: 330, h: 80, m: { t: 24, r: 4, b: 18, l: 4 } });
    const tt = qt.g.append("text").attr("class", "rot-m").attr("y", -8);
    const gT = qt.g.append("g");
    const lei = CX.leitura(host);
    const nums = { veg: CX.num(lei, "vegetação na fatia"), pasto: CX.num(lei, "pastagem"), agric: CX.num(lei, "lavoura e mosaico") };

    function atualiza() {
      const t = ano - 1985, T = t + 1;
      // topo: a fatia do ano escolhido
      gTopo.selectAll("path").data(traj).join("path")
        .attr("d", (p) => { const u = p.i, v = N - 1 - p.j; return poli([P(u, v, T), P(u + 1, v, T), P(u + 1, v + 1, T), P(u, v + 1, T)]); })
        .attr("fill", (p) => C[p.seq[t]]).attr("stroke", "#fff").attr("stroke-width", 0.4);
      // face da frente à esquerda: a história da linha mais ao sul (v = N)
      const esqD = [], dirD = [];
      for (let u = 0; u < N; u++) for (let k = 0; k <= t; k++) esqD.push({ u, k, cl: px(u, 0).seq[k] });
      for (let v = 0; v < N; v++) for (let k = 0; k <= t; k++) dirD.push({ v, k, cl: px(N - 1, N - 1 - v).seq[k] });
      gEsq.selectAll("path").data(esqD).join("path")
        .attr("d", (d) => poli([P(d.u, N, d.k), P(d.u + 1, N, d.k), P(d.u + 1, N, d.k + 1), P(d.u, N, d.k + 1)]))
        .attr("fill", (d) => escurece(C[d.cl], 0.25)).attr("stroke", "#fff").attr("stroke-width", 0.25);
      gDir.selectAll("path").data(dirD).join("path")
        .attr("d", (d) => poli([P(N, d.v, d.k), P(N, d.v + 1, d.k), P(N, d.v + 1, d.k + 1), P(N, d.v, d.k + 1)]))
        .attr("fill", (d) => escurece(C[d.cl], 0.55)).attr("stroke", "#fff").attr("stroke-width", 0.25);
      gMarca.selectAll("*").remove();
      // régua do tempo na aresta da frente
      const [x0, y0] = P(0, N, 0), [x1, y1] = P(0, N, T);
      gMarca.append("line").attr("x1", x0 - 8).attr("x2", x1 - 8).attr("y1", y0).attr("y2", y1).attr("stroke", "#777");
      gMarca.append("text").attr("class", "rot-m").attr("x", x0 - 12).attr("y", y0 + 4).attr("text-anchor", "end").text("1985");
      gMarca.append("text").attr("class", "rot-f").attr("x", x1 - 12).attr("y", y1 + 4).attr("text-anchor", "end").text(ano);
      // seta do Norte sobre o topo
      const [nx0, ny0] = P(N / 2, N / 2 + 2, T), [nx1, ny1] = P(N / 2, 2, T);
      gMarca.append("line").attr("x1", nx0).attr("y1", ny0).attr("x2", nx1).attr("y2", ny1).attr("stroke", C.acento).attr("stroke-width", 2.5).attr("marker-end", "url(#cx-cubo-seta)");
      gMarca.append("text").attr("class", "rot-f").attr("x", nx1 + 6).attr("y", ny1 - 4).style("fill", C.acento).text("N");
      if (sel) {
        const u = sel.i, v = N - 1 - sel.j;
        gMarca.append("path").attr("d", poli([P(u, v, T), P(u + 1, v, T), P(u + 1, v + 1, T), P(u, v + 1, T)])).attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 2);
      }
      // mapa plano e contagem
      celas.attr("fill", (d) => C[d.seq[t]]).attr("stroke", (d) => (d === sel ? "#111" : "none")).attr("stroke-width", 2);
      const cont = { veg: 0, pasto: 0, agric: 0 };
      traj.forEach((p) => { const k = p.seq[t]; if (k in cont) cont[k]++; else if (k === "mosaico") cont.agric++; });
      Object.entries(nums).forEach(([k, n]) => n.set(CX.pct(cont[k] / (N * N))));
      if (sel) {
        tt.text("a coluna do pixel marcado, de 1985 a 2024");
        gT.selectAll("rect").data(sel.seq).join("rect").attr("x", (_, i) => i * 8.1).attr("width", 7.5).attr("height", 24)
          .attr("fill", (k) => C[k]).attr("opacity", (_, i) => (i <= t ? 1 : 0.25)).attr("stroke", (_, i) => (i === t ? "#111" : "none"));
        gT.selectAll("text").data([1985, 2024]).join("text").attr("class", "rot-m").attr("x", (a2) => (a2 - 1985) * 8.1 + (a2 > 2000 ? 7.5 : 0)).attr("y", 38).attr("text-anchor", (a2) => (a2 > 2000 ? "end" : "start")).text(String);
      }
    }
    qi.svg.append("defs").append("marker").attr("id", "cx-cubo-seta").attr("viewBox", "0 0 10 10").attr("refX", 8).attr("refY", 5).attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto")
      .append("path").attr("d", "M0,0L10,5L0,10z").attr("fill", C.acento);
    sel = traj[3 * N + 4];
    atualiza();
    host.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg}"></i>vegetação</span><span><i style="background:${C.pasto}"></i>pastagem</span><span><i style="background:${C.agric}"></i>lavoura</span><span><i style="background:${C.mosaico}"></i>mosaico</span><span><i style="background:${C.agua}"></i>água</span><span>faces laterais: a mesma legenda, mais escura</span>` }));
    CX.frase(host, "O topo do cubo é uma fatia: o mapa de um ano, que serve para medir estoques. As faces laterais são colunas vistas de lado: a história dos pixels da borda, ano a ano, que serve para medir trajetórias. Recue o ano e veja o cubo baixar; olhe a face da frente e repare que, no sul, o verde vira pasto antes de 1985 e a lavoura chega depois.");
    return () => tocando && tocando();
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
        const ctl = CX.ctrl(c);
        const sA = CX.slider(ctl, { rot: "alunos que passam da manhã para a tarde", min: 0, max: 60, val: 30, fmt: String, aoMudar: des });
        const sB = CX.slider(ctl, { rot: "alunos que passam da tarde para a manhã", min: 0, max: 60, val: 30, fmt: String, aoMudar: des });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nS = CX.num(lei, "mudança na contagem da manhã"), nF = CX.num(lei, "alunos que trocaram de turno", true);
        const txt = CX.frase(c);
        function des() {
          const a = sA.valor(), b = sB.valor();
          const man = 100 - a + b, tar = 100 - b + a;
          a1.innerHTML = `<p class="rot-ctrl" style="margin:0 0 .3rem;text-align:center"><b>A matriz de transição</b> (o filme)</p>
            <table class="cx-matriz"><tr><th></th><th>este ano: manhã</th><th>este ano: tarde</th></tr>
            <tr><th>ano passado: manhã</th><td class="fica">${100 - a}</td><td class="muda">${a}</td></tr>
            <tr><th>ano passado: tarde</th><td class="muda">${b}</td><td class="fica">${100 - b}</td></tr></table>
            <p class="cx-leg" style="justify-content:center">azul: ficou no turno · terracota: trocou de turno</p>`;
          a2.replaceChildren();
          const q = CX.quadro(a2, { w: 330, h: 210, m: { l: 90, r: 50, t: 28, b: 30 } });
          const lin = [["manhã", 100, man], ["tarde", 100, tar]];
          const x = d3.scaleLinear().domain([0, 170]).range([0, q.iw]), y = d3.scaleBand().domain(["manhã", "tarde"]).range([0, q.ih]).padding(0.3);
          CX.eixos(q, x, null, { xl: "alunos", xt: 4 });
          q.g.append("text").attr("class", "rot-f").attr("y", -12).text("A contagem (a fotografia)");
          lin.forEach(([n, antes, agora]) => {
            const yy = y(n), bw = y.bandwidth() / 2 - 1;
            q.g.append("rect").attr("y", yy).attr("height", bw).attr("width", x(antes)).attr("fill", C.cinza).attr("rx", 2);
            q.g.append("rect").attr("y", yy + bw + 2).attr("height", bw).attr("width", x(agora)).attr("fill", C.azul).attr("rx", 2);
            q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", yy + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
            q.g.append("text").attr("class", "rot-m").attr("x", x(antes) + 4).attr("y", yy + bw - 2).text(`${antes} (ano passado)`);
            q.g.append("text").attr("class", "rot-f").attr("x", x(agora) + 4).attr("y", yy + 2 * bw).text(`${agora} (este ano)`);
          });
          nS.set(CX.fs(man - 100, 0)); nF.set(String(a + b));
          txt.innerHTML = a === b
            ? `A contagem não se mexe: manhã e tarde continuam com 100. A matriz, porém, registra ${a + b} trocas. É o caso em que o saldo esconde tudo.`
            : `A contagem da manhã muda ${CX.fs(man - 100, 0)}, que é só o saldo das duas direções. A matriz mostra o movimento inteiro: ${a} num sentido e ${b} no outro, ${a + b} trocas ao todo.`;
        }
        des();
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
          txt.innerHTML = `No Ato ${ato}, ${f(ida.bruto_mha, 2)} Mha passaram de ${nomes[a]} para ${nomes[b]} e ${f(volta.bruto_mha, 2)} Mha fizeram o caminho contrário. Quem olha só o saldo (${f(ida.liquido_mha, 2)} Mha) não vê ${CX.pct(Math.max(0, esc))} do movimento de ida. É a mesma situação da troca de turno, em milhões de hectares.`;
        }
        desenha();
      },
    });
  });

  /* ---------------- 1.5 Censura (as árvores de duas praças) ---------------- */
  CX.def("censura", (host) => {
    const r = CX.rng(21);
    const arv = [];
    // praça antiga: plantada sobretudo nos anos 1960 e 1970; praça nova: criada em 1995
    for (let k = 0; k < 19; k++) arv.push({ reg: "antiga", n: Math.round(Math.min(1986, 1968 + CX.normal(r) * 9)) });
    [1996, 2004, 2013].forEach((n) => arv.push({ reg: "antiga", n })); // as poucas replantadas
    for (let k = 0; k < 22; k++) arv.push({ reg: "nova", n: Math.round(Math.min(2021, 1995 + Math.abs(CX.normal(r)) * 9)) });
    arv.sort((a, b) => (a.reg === b.reg ? a.n - b.n : a.reg === "antiga" ? -1 : 1));
    const nomeP = { antiga: "Praça antiga", nova: "Praça nova" };
    const ctl = CX.ctrl(host);
    const s = CX.slider(ctl, { rot: "o cadastro de plantio começa em", min: 1950, max: 2005, val: 1990, fmt: String, aoMudar: desenha });
    const q = CX.quadro(host, { h: 360, m: { l: 92, r: 16, t: 14, b: 26 } });
    const x = d3.scaleLinear().domain([1940, 2024]).range([0, q.iw]);
    const y = d3.scaleBand().domain(arv.map((_, i) => i)).range([0, q.ih]).padding(0.25);
    CX.eixos(q, x, null, { xf: CX.anoF });
    q.g.append("text").attr("class", "rot-f").attr("x", -88).attr("y", y(5)).text("Praça antiga");
    q.g.append("text").attr("class", "rot-f").attr("x", -88).attr("y", y(27)).text("Praça nova");
    const janela = q.g.append("rect").attr("y", -4).attr("height", q.ih + 4).attr("fill", "#f3efe3");
    const defs = q.svg.append("defs");
    const pat = defs.append("pattern").attr("id", "cx-hach").attr("width", 6).attr("height", 6).attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("rect").attr("width", 6).attr("height", 6).attr("fill", "#eee");
    pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6).attr("stroke", "#aaa").attr("stroke-width", 2);
    const bar = q.g.selectAll("g.p").data(arv).join("g").attr("class", "p");
    const bOculto = bar.append("rect").attr("height", y.bandwidth()).attr("fill", "url(#cx-hach)");
    const bVisto = bar.append("rect").attr("height", y.bandwidth()).attr("rx", 2);
    const inicio = q.g.append("line").attr("y1", -4).attr("y2", q.ih).attr("stroke", C.acento).attr("stroke-width", 2);
    const inicioT = q.g.append("text").attr("class", "rot-f").attr("y", -8).attr("text-anchor", "middle").style("fill", C.acento);
    const tab = h("table", { class: "cx-tab" });
    host.appendChild(tab);
    host.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg}"></i>idade conhecida</span><span><i style="background:${C.cinza}"></i>já existia quando o cadastro começou (censurada)</span><span><i style="background:repeating-linear-gradient(45deg,#eee 0 3px,#aaa 3px 5px)"></i>parte da história que o cadastro não vê</span>` }));
    const txt = CX.frase(host);
    function desenha() {
      const t0 = s.valor();
      janela.attr("x", x(t0)).attr("width", x(2024) - x(t0));
      inicio.attr("x1", x(t0)).attr("x2", x(t0)); inicioT.attr("x", x(t0)).text("início do cadastro");
      bar.attr("transform", (_, i) => `translate(0,${y(i)})`);
      bOculto.attr("x", (d) => x(d.n)).attr("width", (d) => Math.max(0, x(Math.max(d.n, Math.min(t0, 2024))) - x(d.n)));
      bVisto.attr("x", (d) => x(Math.max(d.n, t0))).attr("width", (d) => x(2024) - x(Math.max(d.n, t0)))
        .attr("fill", (d) => (d.n < t0 ? C.cinza : C.veg));
      const linhas = ["antiga", "nova"].map((rg) => {
        const p = arv.filter((d) => d.reg === rg);
        const cens = p.filter((d) => d.n < t0).length;
        return [nomeP[rg], cens / p.length, S.mediana(p.map((d) => 2024 - d.n)), S.mediana(p.map((d) => 2024 - Math.max(d.n, t0))),
          p.some((d) => d.n >= t0) ? S.mediana(p.filter((d) => d.n >= t0).map((d) => 2024 - d.n)) : null];
      });
      tab.innerHTML = `<tr><th>praça</th><th>censuradas</th><th>idade verdadeira (mediana)</th><th>tratando "pelo menos" como exata</th><th>sem as censuradas</th></tr>` +
        linhas.map((l) => `<tr><td>${l[0]}</td><td>${CX.pct(l[1])}</td><td>${l[2]} anos</td><td>${l[3]} anos</td><td>${l[4] == null ? "—" : l[4] + " anos"}</td></tr>`).join("");
      const [ant, nov] = linhas;
      txt.innerHTML = `Com o cadastro começando em ${t0}, ${CX.pct(ant[1])} das árvores da praça antiga ficam censuradas. A idade verdadeira dela tem mediana de ${ant[2]} anos, mas a conta que trata o "pelo menos" como exato dá ${ant[3]}` +
        (ant[4] == null ? ", e sem as censuradas não sobra árvore nenhuma para contar." : `, e a que joga as censuradas fora dá ${ant[4]}.`) +
        ` Na praça nova, quase nada muda. Qualquer comparação entre as duas precisa declarar a censura de cada lado. Recue o início do cadastro e veja a distorção sumir.`;
    }
    desenha();
  });

  /* ---------------- 1.6 Censo, amostra e peso ---------------- */
  CX.def("censo", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sS = CX.slider(ctl, { rot: "clientes no sábado", min: 60, max: 900, passo: 10, val: 600, fmt: String, aoMudar: des });
        const sT = CX.slider(ctl, { rot: "clientes na terça", min: 20, max: 300, passo: 10, val: 60, fmt: String, aoMudar: des });
        const ctl2 = CX.ctrl(c);
        const pond = CX.check(ctl2, " pesar cada dia pelo número de clientes", false, des);
        const q = CX.quadro(c, { h: 230, m: { l: 10, r: 10, t: 14, b: 10 } });
        const lei = CX.leitura(c);
        const nV = CX.num(lei, "nota média verdadeira dos clientes"), nE = CX.num(lei, "estimativa pelas 10 + 10 entrevistas", true), nP = CX.num(lei, "peso da terça na estimativa");
        const txt = CX.frase(c);
        const NS = 6.4, NT = 8.6;
        function des() {
          const cS = sS.valor(), cT = sT.valor();
          const verd = (cS * NS + cT * NT) / (cS + cT);
          const wT = pond.valor() ? cT / (cS + cT) : 0.5;
          const est = NS * (1 - wT) + NT * wT;
          nV.set(f(verd, 2)); nE.set(f(est, 2)); nP.set(CX.pct(wT));
          q.g.selectAll("*").remove();
          [["Sábado", cS, NS, C.acento, 20], ["Terça", cT, NT, C.azul, 130]].forEach(([n, k, nota, cc, y0]) => {
            const cols = 45, pessoas = Math.round(k / 10);
            q.g.append("text").attr("class", "rot-f").attr("x", 0).attr("y", y0 - 6).text(`${n}: ${k} clientes · nota média ${f(nota, 1)}`);
            for (let i = 0; i < pessoas; i++) {
              q.g.append("circle").attr("cx", 8 + (i % cols) * 14.6).attr("cy", y0 + 8 + Math.floor(i / cols) * 14).attr("r", 5.2)
                .attr("fill", i === 0 ? cc : "#fff").attr("stroke", cc);
            }
          });
          q.g.append("text").attr("class", "rot-m").attr("x", 0).attr("y", q.ih - 2).text("cada círculo = 10 clientes · o círculo cheio são os 10 entrevistados do dia");
          txt.innerHTML = pond.valor()
            ? `Com os pesos pelo movimento, a terça vale ${CX.pct(wT)} da conta e a estimativa encosta na nota verdadeira. As 20 entrevistas são as mesmas de antes; mudou só o peso na hora de juntar.`
            : `As mesmas 10 entrevistas por dia dão à terça metade do peso da semana, embora ela tenha ${CX.pct(cT / (cS + cT))} dos clientes. Como a terça é o dia bom, a média sai ${verd < est ? "otimista" : "pessimista"} em ${f(Math.abs(est - verd), 2)} ponto.`;
        }
        des();
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
        CX.frase(c, "A amostra de 2.000 pixels por ano dava a todo ano o mesmo peso, como as 10 entrevistas por dia do restaurante. No censo, 2020 (um ano de conversão intensa, o sábado lotado) pesa quase o dobro, e 2024 menos da metade. Ano a ano, a amostra acertava a mediana; no agregado, o erro era de ponderação.");
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
    const s = CX.slider(ctl, { rot: "latitude", min: 0, max: 80, val: 16, fmt: (v) => v + "° S", aoMudar: des });
    const grid = h("div", { class: "cx-grade2" });
    host.appendChild(grid);
    const esq = h("div"), dir = h("div"); grid.append(esq, dir);
    // d3-geo quer anéis no sentido horário; se a área passar de meia esfera, o anel está invertido
    const poligono = (anel) => { let g = { type: "Polygon", coordinates: [anel] }; if (d3.geoArea(g) > 2 * Math.PI) g = { type: "Polygon", coordinates: [[...anel].reverse()] }; return g; };
    const qg = CX.quadro(esq, { w: 320, h: 320, m: { t: 6, r: 6, b: 6, l: 6 } });
    const proj = d3.geoOrthographic().scale(148).translate([154, 154]).rotate([55, 20]).clipAngle(90);
    const path = d3.geoPath(proj);
    qg.g.append("path").datum({ type: "Sphere" }).attr("d", path).attr("fill", "#eef3f6").attr("stroke", "#9bb");
    qg.g.append("path").datum(d3.geoGraticule().step([10, 10])()).attr("d", path).attr("fill", "none").attr("stroke", "#c5d0d5").attr("stroke-width", 0.7);
    // um "gomo" de 10° de longitude, de polo a polo: largo no equador, fino nas pontas
    const gomo = [];
    for (let la = -89; la <= 89; la += 2) gomo.push([-70, la]);
    for (let la = 89; la >= -89; la -= 2) gomo.push([-60, la]);
    gomo.push(gomo[0]);
    qg.g.append("path").datum(poligono(gomo)).attr("d", path).attr("fill", C.azul).attr("opacity", 0.22).attr("stroke", C.azul).attr("stroke-width", 0.8);
    qg.g.append("path").datum(poligono([[-53.2, -19.5], [-45.9, -19.5], [-45.9, -12.4], [-53.2, -12.4], [-53.2, -19.5]])).attr("d", path).attr("fill", C.pasto).attr("opacity", 0.85);
    const paralelo = qg.g.append("path").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2.2);
    qg.g.append("text").attr("class", "rot-m").attr("x", 4).attr("y", 312).text("azul: um gomo de 10° de longitude");
    // gráfico: km em 1° de longitude e de latitude, por latitude
    const qr = CX.quadro(dir, { w: 340, h: 320, m: { t: 30, r: 16, b: 40, l: 48 } });
    const x = d3.scaleLinear().domain([0, 80]).range([0, qr.iw]), y = d3.scaleLinear().domain([0, 120]).range([qr.ih, 0]);
    CX.eixos(qr, x, y, { xl: "latitude (graus ao sul do equador)", yl: "quilômetros em 1 grau", xf: (v) => v + "°", xt: 8 });
    const kLon = (la) => 111.32 * Math.cos((la * Math.PI) / 180);
    const kLat = (la) => (111132.92 - 559.82 * Math.cos((2 * la * Math.PI) / 180) + 1.175 * Math.cos((4 * la * Math.PI) / 180)) / 1000;
    qr.g.append("rect").attr("x", x(12.4)).attr("width", x(19.5) - x(12.4)).attr("y", 0).attr("height", qr.ih).attr("fill", C.pasto).attr("opacity", 0.18);
    qr.g.append("text").attr("class", "rot-m").attr("x", x(16)).attr("y", qr.ih - 6).attr("text-anchor", "middle").text("Goiás");
    const ls = d3.range(0, 80.5, 0.5);
    qr.g.append("path").attr("fill", "none").attr("stroke", "#777").attr("stroke-width", 2).attr("stroke-dasharray", "5 3").attr("d", d3.line().x((la) => x(la)).y((la) => y(kLat(la)))(ls));
    qr.g.append("path").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2.4).attr("d", d3.line().x((la) => x(la)).y((la) => y(kLon(la)))(ls));
    qr.g.append("text").attr("class", "rot").attr("x", x(80)).attr("y", y(kLat(80)) - 6).attr("text-anchor", "end").text("1° de latitude (a altura do gomo)");
    qr.g.append("text").attr("class", "rot").attr("x", x(80)).attr("y", y(kLon(80)) + 18).attr("text-anchor", "end").style("fill", C.acento).text("1° de longitude (a largura)");
    const mk = qr.g.append("g");
    const lei = CX.leitura(host);
    const nL = CX.num(lei, "1° de longitude nesta latitude", true), nA = CX.num(lei, "1° de latitude"), nE = CX.num(lei, "quanto o grau de longitude é mais curto");
    function des() {
      const la = s.valor(), kl = kLon(la), ka = kLat(la);
      const lin = []; for (let lo = -180; lo <= 180; lo += 2) lin.push([lo, -la]);
      paralelo.datum({ type: "LineString", coordinates: lin }).attr("d", path);
      mk.selectAll("*").remove();
      mk.append("line").attr("x1", x(la)).attr("x2", x(la)).attr("y1", 0).attr("y2", qr.ih).attr("stroke", "#111").attr("stroke-dasharray", "3 3");
      mk.append("circle").attr("cx", x(la)).attr("cy", y(kl)).attr("r", 5).attr("fill", C.acento);
      mk.append("circle").attr("cx", x(la)).attr("cy", y(ka)).attr("r", 4).attr("fill", "#777");
      nL.set(f(kl, 1) + " km"); nA.set(f(ka, 1) + " km"); nE.set(CX.pct(1 - kl / ka, 1));
    }
    des();
    CX.frase(host, "Em Goiás, entre 12,4° e 19,5° de latitude sul, um grau de longitude mede de 108 a 105 km, de 3% a 5% menos que um grau de latitude. Uma média de coordenadas feita em graus mistura as duas réguas; por isso a conta dos centros de massa é feita em metros, na projeção policônica do Brasil (EPSG:5880), e só depois volta a graus para desenhar o mapa.");
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
    const W = 108, H = 36;
    const N = [
      ["fontes", "Fontes públicas", 6, 100, "MapBiomas, IBGE/SIDRA, Ipeadata, BACEN, FIRJAN, Embrapa, INPE, Trase. Nada é recebido pronto de terceiros: tudo é buscado na origem."],
      ["coleta", "Coleta automatizada", 130, 100, "scripts/coleta_*.py (SIDRA, SICOR, drivers macro, IFDM…) e rotinas no Google Earth Engine para os rasters. Buscam a série na origem, com cache local."],
      ["raw", "data/raw (cache)", 254, 40, "Arquivos brutos como vieram da fonte. Fora do controle de versão por tamanho; a data de acesso de cada fonte é a data do arquivo."],
      ["proc", "data/processed", 254, 160, "Tabelas limpas e padronizadas (painel municipal, painel por AMC, séries regionais). Reconstruível a partir do raw, offline."],
      ["rotinas", "58 rotinas (#1…#58)", 378, 100, "scripts/*.py, uma pergunta por rotina, com ficha em Textos/pipelines/ (pergunta, dependências, comando, saídas, limitações). O número nunca é renumerado."],
      ["outputs", "outputs/", 502, 100, "Tabelas e figuras gravadas pelas rotinas. Todo número exibido deve ser rastreável até um desses arquivos."],
      ["viz", "Visualização", 640, 20, "Visualizacao/: o site. Consome um recorte leve, versionado junto com ele."],
      ["ci", "CI: verificar-viz", 640, 88, "A cada envio que toca a visualização: sobe o site num navegador sem interface e falha se um número-âncora sumiu, se o console acusou erro ou se um número derrubado reapareceu.", true],
      ["texto", "Texto (qualificação)", 640, 176, "qualificacao/: abnTeX2. O apêndice de especificações é gerado a partir dos arquivos das rotinas, nenhum coeficiente digitado à mão."],
      ["ver", "verificar.py", 640, 244, "Seis invariantes do texto: ponteiro sem destino, citação sem entrada, obra ausente da lista de leitura, sigla antes de definida, calibragem perdida, decisão citada sem registro.", true],
    ];
    const A = [["fontes", "coleta"], ["coleta", "raw"], ["raw", "proc"], ["proc", "rotinas"], ["rotinas", "outputs"], ["outputs", "viz"], ["outputs", "texto"], ["viz", "ci"], ["texto", "ver"]];
    const q = CX.quadro(host, { w: 760, h: 292, m: { t: 4, r: 4, b: 4, l: 4 } });
    const pos = Object.fromEntries(N.map((n) => [n[0], n]));
    q.svg.append("defs").append("marker").attr("id", "cx-seta").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7).attr("orient", "auto")
      .append("path").attr("d", "M0,0L10,5L0,10z").attr("fill", "#888");
    A.forEach(([a, b]) => {
      const p = pos[a], r = pos[b];
      let x1, y1, x2, y2;
      if (p[2] === r[2]) { x1 = x2 = p[2] + W / 2; y1 = p[3] + H; y2 = r[3]; }          // mesma coluna: desce
      else { x1 = p[2] + W; y1 = p[3] + H / 2; x2 = r[2]; y2 = r[3] + H / 2; }             // coluna seguinte: avança
      q.g.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2 - (p[2] === r[2] ? 0 : 2)).attr("y2", y2 - (p[2] === r[2] ? 2 : 0))
        .attr("stroke", "#aaa").attr("stroke-width", 1.5).attr("marker-end", "url(#cx-seta)");
    });
    const info = CX.frase(host, "Clique numa etapa.");
    const g = q.g.selectAll("g.n").data(N).join("g").attr("class", "n").attr("transform", (n) => `translate(${n[2]},${n[3]})`).style("cursor", "pointer");
    const r = g.append("rect").attr("width", W).attr("height", H).attr("rx", 8).attr("fill", (n) => (n[5] ? "#f6e3da" : "#fff")).attr("stroke", (n) => (n[5] ? C.acento : "#999"));
    g.append("text").attr("class", "rot").attr("x", W / 2).attr("y", 22).attr("text-anchor", "middle").style("font-size", "11px").text((n) => n[1]);
    g.on("click", function (_, n) { r.attr("stroke-width", 1); d3.select(this).select("rect").attr("stroke-width", 3); info.innerHTML = `<b>${n[1]}</b>: ${n[4]}`; });
  });

})();
