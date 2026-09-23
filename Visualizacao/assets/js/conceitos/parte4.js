/* Caderno de conceitos — Parte 4: inferência */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  function barrasH(pai, lin, o = {}) {
    const q = CX.quadro(pai, { w: o.w || 680, h: o.h || 40 + lin.length * 38, m: { l: o.l || 190, r: 70, t: 10, b: 30 } });
    const mx = o.max ?? d3.max(lin, (l) => l[1]) * 1.15;
    const x = d3.scaleLinear().domain([Math.min(0, d3.min(lin, (l) => l[1])), mx]).range([0, q.iw]);
    const y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.3);
    CX.eixos(q, x, null, { xf: o.xf, xl: o.xl, xt: o.xt || (q.iw < 300 ? 4 : 8) });
    lin.forEach(([n, v, cc, rot]) => {
      q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(n)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", cc || C.cinza).attr("rx", 3);
      q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
      q.g.append("text").attr("class", "rot-f").attr("x", x(Math.max(0, v)) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text(rot ?? (o.vf ? o.vf(v) : f(v, 2)));
    });
    return { q, x, y };
  }

  /* ---------------- 4.1 p-valor e poder ---------------- */
  CX.def("pval", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sN = CX.slider(ctl, { rot: "jogadas", min: 1, max: 30, val: 10, fmt: String, aoMudar: () => { if (sK.valor() > sN.valor()) sK.set(sN.valor(), 1); des(); } });
        const sK = CX.slider(ctl, { rot: "caras obtidas", min: 0, max: 30, val: 10, fmt: String, aoMudar: () => { if (sK.valor() > sN.valor()) sK.set(sN.valor(), 1); des(); } });
        const q = CX.quadro(c, { h: 240, m: { l: 44, r: 10, t: 14, b: 34 } });
        const lei = CX.leitura(c);
        const nP = CX.num(lei, "p (chance de ≥ essas caras com moeda honesta)", true);
        const txt = CX.frase(c);
        function des() {
          const n = sN.valor(), k = Math.min(sK.valor(), n);
          const pr = d3.range(n + 1).map((i) => Math.exp(S.lgamma(n + 1) - S.lgamma(i + 1) - S.lgamma(n - i + 1) - n * Math.LN2));
          const x = d3.scaleBand().domain(d3.range(n + 1)).range([0, q.iw]).padding(0.15), y = d3.scaleLinear().domain([0, d3.max(pr) * 1.1]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "número de caras", yl: "probabilidade", yf: (v) => CX.pct(v), xt: Math.min(n + 1, 16) });
          q.g.selectAll("rect.b").data(pr).join("rect").attr("class", "b").attr("x", (_, i) => x(i)).attr("width", x.bandwidth()).attr("y", (p) => y(p)).attr("height", (p) => q.ih - y(p)).attr("fill", (_, i) => (i >= k ? C.acento : "#d9d5ca")).attr("rx", 2);
          const p = S.pBinom(k, n);
          nP.set(CX.p(p));
          txt.innerHTML = `A área terracota é o p: a chance de uma moeda honesta dar ${k} ou mais caras em ${n} jogadas. ` + (n <= 4 ? "Com tão poucas jogadas, nem o resultado mais extremo possível seria raro: o teste não tem como desmascarar a moeda. Isso é poder baixo." : p < 0.05 ? "Resultado raro sob a moeda honesta." : "Resultado compatível com uma moeda honesta, o que não prova que ela seja.");
        }
        des();
      },
      dados(c) {
        const ctl = CX.ctrl(c);
        const sE = CX.slider(ctl, { rot: "tamanho do efeito", min: 0, max: 0.8, passo: 0.05, val: 0.3, fmt: (v) => f(v, 2) });
        CX.btn(ctl, "simular", des, true);
        const q = CX.quadro(c, { h: 280, m: { l: 50, r: 20, t: 14, b: 38 } });
        const x = d3.scaleLinear().domain([10, 80]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 1]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xl: "número de anos na série", yl: "poder (chance de detectar)", yf: (v) => CX.pct(v) });
        q.g.append("line").attr("x1", x(38)).attr("x2", x(38)).attr("y1", 0).attr("y2", q.ih).attr("stroke", C.acento).attr("stroke-dasharray", "4 3");
        q.g.append("text").attr("class", "rot-f").attr("x", x(38) + 4).attr("y", 12).style("fill", C.acento).text("38 anos: o que o trabalho tem");
        const gL = q.g.append("g");
        const lei = CX.leitura(c);
        const nP = CX.num(lei, "poder com 38 anos (simulação desta página)", true);
        function poder(n, b, r, sims) {
          let rej = 0;
          for (let s = 0; s < sims; s++) {
            const xs = d3.range(n + 1).map(() => CX.normal(r)), ys = [];
            for (let t = 1; t <= n; t++) ys.push(b * xs[t - 1] + CX.normal(r));
            const fit = S.ols1(xs.slice(0, n), ys);
            if (S.pT(fit.b / fit.se, n - 2) < 0.05) rej++;
          }
          return rej / sims;
        }
        function des() {
          const r = CX.rng(Math.floor(Math.random() * 1e6)), b = sE.valor();
          const ns = d3.range(10, 81, 5), pw = ns.map((n) => poder(n, b, r, 250));
          gL.selectAll("*").remove();
          gL.append("line").attr("x1", 0).attr("x2", q.iw).attr("y1", y(0.05)).attr("y2", y(0.05)).attr("stroke", "#bbb").attr("stroke-dasharray", "2 3");
          gL.append("text").attr("class", "rot-m").attr("x", q.iw).attr("y", y(0.05) - 4).attr("text-anchor", "end").text("5% = falsos positivos quando não há efeito");
          gL.append("path").attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 2.2).attr("d", d3.line().x((_, i) => x(ns[i])).y((p) => y(p))(pw));
          gL.selectAll("circle").data(pw).join("circle").attr("cx", (_, i) => x(ns[i])).attr("cy", (p) => y(p)).attr("r", 3.5).attr("fill", "#111");
          nP.set(CX.pct(poder(38, b, r, 800)));
        }
        des();
        CX.frase(c, "Simulação didática: uma série antecede a outra com o efeito escolhido (em desvios-padrão), e o teste é repetido 250 vezes por ponto. O trabalho fez a simulação com a especificação real do teste de precedência e chegou a cerca de 93% para um efeito forte e 48% para um moderado. Com efeito moderado, um p grande é \"não sei\".");
      },
    });
  });

  /* ---------------- 4.2 Granger ---------------- */
  function grangerF(y, x, lag = 1) {
    const n = y.length, Xr = [], Xf = [], yy = [];
    for (let t = lag; t < n; t++) { const r = [1], fr = [1]; for (let l = 1; l <= lag; l++) { r.push(y[t - l]); fr.push(y[t - l]); } for (let l = 1; l <= lag; l++) fr.push(x[t - l]); Xr.push(r); Xf.push(fr); yy.push(y[t]); }
    const a = S.ols(Xr, yy), b = S.ols(Xf, yy);
    const d2 = yy.length - Xf[0].length, F = ((a.ssr - b.ssr) / lag) / (b.ssr / d2);
    return { F, p: S.pF(F, lag, d2), ssrR: a.ssr, ssrF: b.ssr, fitR: a.fit, fitF: b.fit };
  }
  CX.def("granger", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        let sem = 5;
        const sA = CX.slider(ctl, { rot: "quanto o latido antecede", min: 0, max: 1, passo: 0.05, val: 0.7, fmt: (v) => f(v, 2), aoMudar: des });
        CX.btn(ctl, "sortear outra semana", () => { sem++; des(); });
        const q = CX.quadro(c, { h: 250, m: { l: 44, r: 118 } });
        const lei = CX.leitura(c);
        const nS1 = CX.num(lei, "erro da previsão só com o dono"), nS2 = CX.num(lei, "erro com o latido de ontem"), nP = CX.num(lei, "p do teste F", true);
        function des() {
          const r = CX.rng(sem), n = 40, a = sA.valor();
          const lat = d3.range(n).map(() => CX.normal(r)), dono = [0];
          for (let t = 1; t < n; t++) dono.push(0.3 * dono[t - 1] + a * lat[t - 1] + CX.normal(r) * 0.7);
          const g = grangerF(dono, lat, 1);
          const x = d3.scaleLinear().domain([0, n - 1]).range([0, q.iw]), y = d3.scaleLinear().domain(d3.extent([...dono, ...lat])).nice().range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "dia", yl: "desvio do horário habitual" });
          q.g.selectAll(".l").remove();
          const rots = [];
          [[lat, C.cinza, "latido", 1.4, "3 3"], [dono, "#111", "chegada do dono", 2], [[null, ...g.fitR], C.azul, "prev. sem latido", 2, "5 3"], [[null, ...g.fitF], C.acento, "prev. com latido", 2]].forEach(([v, cc, nome, lw, tr]) => {
            q.g.append("path").attr("class", "l").attr("fill", "none").attr("stroke", cc).attr("stroke-width", lw).attr("stroke-dasharray", tr || null).attr("d", d3.line().defined((d) => d != null).x((_, i) => x(i)).y((d) => y(d))(v));
            const t = q.g.append("text").attr("class", "l rot").attr("x", q.iw + 4); t.append("tspan").style("fill", cc).text("■ "); t.append("tspan").text(nome);
            rots.push({ sel: t, y: y(v[v.length - 1]) + 4 });
          });
          CX.desempilha(rots, 8, q.ih);
          nS1.set(f(g.ssrR, 1)); nS2.set(f(g.ssrF, 1)); nP.set(CX.p(g.p));
        }
        des();
      },
      async dados(c) {
        const G = (await CX.base()).granger;
        const q = CX.quadro(c, { h: 270, m: { l: 54, r: 120, t: 14 } });
        const x = d3.scaleLinear().domain([1986, 2024]).range([0, q.iw]);
        const y = d3.scaleLinear().domain(d3.extent([...G.norte, ...G.sul])).nice().range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: CX.anoF, yl: "variação anual (mil ha)" });
        q.g.append("line").attr("class", "zero").attr("x1", 0).attr("x2", q.iw).attr("y1", y(0)).attr("y2", y(0));
        const rots = [];
        const ln = (anos, v, cc, lw, tr, nome) => {
          q.g.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", lw).attr("stroke-dasharray", tr || null).attr("d", d3.line().x((_, i) => x(anos[i])).y((d) => y(d))(v));
          const t = q.g.append("text").attr("class", "rot").attr("x", q.iw + 4); t.append("tspan").style("fill", cc).text("■ "); t.append("tspan").text(nome);
          rots.push({ sel: t, y: y(v[v.length - 1]) + 4 });
        };
        ln(G.anos, G.sul, C.agric, 1.3, "3 3", "Δ lavoura Sul");
        ln(G.anos, G.norte, "#111", 2.2, null, "Δ pasto Norte");
        ln(G.anos_fit, G.prev_so_norte, C.azul, 2, "6 3", "prev. só Norte");
        ln(G.anos_fit, G.prev_com_sul, C.acento, 1.6, null, "prev. + Sul");
        CX.desempilha(rots, 8, q.ih);
        const lei = CX.leitura(c);
        CX.num(lei, "soma dos erros², só com o Norte").set(f(G.ssr_so_norte, 1));
        CX.num(lei, "soma dos erros², com o Sul").set(f(G.ssr_com_sul, 1));
        CX.num(lei, "p (defasagem de 1 ano)", true).set(f(G.p, 2));
        CX.frase(c, "As duas previsões do pasto do Norte (tracejada azul e terracota) praticamente se sobrepõem: acrescentar o passado da lavoura do Sul não reduz o erro. Abaixo, as 24 combinações testadas.");
        // placar das 24 células
        const cel = G.celulas;
        const reguas = [...new Set(cel.map((k) => k.regua_rotulo))], cols = [...new Set(cel.map((k) => `${k.janela === "plena" ? "1985–2024" : "1985–2019"} · ${k.desfecho.replace("Δ", "Δ ").replace("_", " ")} · lag ${k.granger_lag}`))];
        const tb = h("table", { class: "cx-tab" });
        tb.innerHTML = `<tr><th>régua da lavoura do Sul</th>${["plena", "truncada 1985–2019"].map((j) => `<th colspan="4">${j === "plena" ? "1985–2024" : "1985–2019"}</th>`).join("")}</tr>
          <tr><th></th>${["plena", "t"].map(() => ["Δ pasto N, 1", "Δ pasto N, 2", "Δ boi N, 1", "Δ boi N, 2"].map((t) => `<th>${t}</th>`).join("")).join("")}</tr>` +
          reguas.map((rg) => `<tr><td>${rg}</td>${cel.filter((k) => k.regua_rotulo === rg).map((k) => `<td style="background:${k.granger_p < 0.05 ? "#f6d5c8" : k.granger_p < 0.1 ? "#fbeede" : "transparent"}">${f(k.granger_p, 2)}</td>`).join("")}</tr>`).join("");
        const wrap = h("div", { style: { overflowX: "auto", marginTop: ".6rem" } }, tb);
        c.appendChild(wrap);
        CX.frase(c, `Placar: <b>0 de 24</b> abaixo de 5% (o menor é ${f(d3.min(cel, (k) => k.granger_p), 3)}, sombreado claro por ficar abaixo de 10%).`);
        return cols;
      },
    });
  });

  /* ---------------- 4.3 Estacionariedade e Toda-Yamamoto ---------------- */
  CX.def("ty", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        let tipo = "passeio";
        CX.seg(ctl, { opcoes: [["passeio", "passeios aleatórios (I(1))"], ["ruido", "ruído estacionário (I(0))"]], val: tipo, aoMudar: (k) => { tipo = k; } });
        CX.btn(ctl, "sortear 200 pares independentes", roda, true);
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "pares com correlação \"significativa\" a 5%", true);
        function roda() {
          const r = CX.rng(Math.floor(Math.random() * 1e6)), n = 40;
          let sig = 0, ex = null;
          for (let s = 0; s < 200; s++) {
            let A = [0], B = [0];
            for (let t = 1; t < n; t++) { const ea = CX.normal(r), eb = CX.normal(r); A.push(tipo === "passeio" ? A[t - 1] + ea : ea); B.push(tipo === "passeio" ? B[t - 1] + eb : eb); }
            const fit = S.ols1(A, B);
            const p = S.pT(fit.b / fit.se, n - 2);
            if (p < 0.05) { sig++; if (!ex) ex = [A, B]; }
            if (!ex && s === 199) ex = [A, B];
          }
          a1.replaceChildren(); a2.replaceChildren();
          const q = CX.quadro(a1, { w: 340, h: 240, m: { l: 36, r: 10, t: 22, b: 26 } });
          const x = d3.scaleLinear().domain([0, n - 1]).range([0, q.iw]), y = d3.scaleLinear().domain(d3.extent([...ex[0], ...ex[1]])).nice().range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "tempo" });
          q.g.append("text").attr("class", "rot-f").attr("y", -8).text("um par \"significativo\"");
          [[ex[0], C.azul], [ex[1], C.acento]].forEach(([v, cc]) => q.g.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2).attr("d", d3.line().x((_, i) => x(i)).y((d) => y(d))(v)));
          barrasH(a2, [["significativos", sig / 200, C.acento], ["esperado sem relação", 0.05, C.cinza]], { w: 340, l: 140, max: 1, vf: (v) => CX.pct(v), xf: (v) => CX.pct(v) });
          nR.set(`${sig} de 200 (${CX.pct(sig / 200)})`);
        }
        roda();
        CX.frase(c, "Nenhum par tem relação: cada série é sorteada por conta própria. Com passeios aleatórios, uma fração enorme passa no teste de correlação comum; com ruído estacionário, perto dos 5% prometidos.");
      },
      async dados(c) {
        const b = await CX.base();
        const R = b.reg;
        const ctl = CX.ctrl(c);
        let d = 0;
        CX.seg(ctl, { opcoes: [[0, "nível"], [1, "1ª diferença"], [2, "2ª diferença"]], val: d, aoMudar: (k) => { d = k; des(); } });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const tab = h("table", { class: "cx-tab" }); c.appendChild(tab);
        const serie = (v, k) => { let s = v; for (let i = 0; i < k; i++) s = S.diff(s); return s; };
        const est = Object.fromEntries(b.estac.map((e) => [e.serie, e]));
        function mini(pai, v, anos, cc, tit, e) {
          const q = CX.quadro(pai, { w: 340, h: 220, m: { l: 44, r: 10, t: 24, b: 26 } });
          const x = d3.scaleLinear().domain(d3.extent(anos)).range([0, q.iw]), y = d3.scaleLinear().domain(d3.extent(v)).nice().range([q.ih, 0]);
          CX.eixos(q, x, y, { xf: CX.anoF, xt: 5, yf: (k) => f(k, 2) });
          q.g.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2).attr("d", d3.line().x((_, i) => x(anos[i])).y((k) => y(k))(v));
          q.g.append("text").attr("class", "rot-f").attr("y", -10).text(tit + (e ? ` · ADF p = ${f(e.adf_p, 3)} · KPSS p = ${f(e.kpss_p, 2)}` : ""));
        }
        function des() {
          a1.replaceChildren(); a2.replaceChildren();
          const pre = ["", "Δ", "ΔΔ"][d], suf = d === 0 ? " (nível)" : "";
          const anos = R.anos.slice(d);
          mini(a1, serie(R.agric_mha_Sul, d), anos, C.agric, pre + "agric. Sul", est[pre + "agric_Sul" + suf]);
          mini(a2, serie(R.pasto_mha_Norte, d), anos, C.pasto, pre + "pasto Norte", est[pre + "pasto_Norte" + suf]);
          tab.innerHTML = `<tr><th>Toda-Yamamoto (d<sub>max</sub> = 2)</th><th>p = 1</th><th>p = 2</th></tr>` +
            ["Sul→Norte", "REVERSO"].map((rel) => `<tr><td>${rel === "REVERSO" ? "Norte → Sul (o inverso)" : "Sul → Norte"}</td>${b.ty.filter((t) => t.relacao === rel).map((t) => `<td>${f(t.ty_p, 3)}</td>`).join("")}</tr>`).join("");
        }
        des();
        CX.frase(c, "ADF: a nula é \"a série vagueia\" (p pequeno = estacionária). KPSS: a nula é \"a série é estacionária\" (p pequeno = vagueia). A agricultura do Sul já é estacionária em nível pelo ADF; o pasto do Norte continua vagueando na 1ª diferença e só estabiliza na 2ª, onde os dois testes concordam: I(2). Com ordens diferentes, o Granger comum fabrica precedência, e o Toda-Yamamoto zera as duas direções (tabela).");
      },
    });
  });

  /* ---------------- 4.4 DiD ---------------- */
  CX.def("did", (host) => {
    const ctl = CX.ctrl(host);
    const sE = CX.slider(ctl, { rot: "efeito verdadeiro", min: 0, max: 30, val: 20, fmt: String, aoMudar: des });
    const sT = CX.slider(ctl, { rot: "tendências antes (A − B por período)", min: -4, max: 4, passo: 0.5, val: 0, fmt: (v) => fs(v, 1), aoMudar: des });
    const sC = CX.slider(ctl, { rot: "política atinge também B", min: 0, max: 1, passo: 0.05, val: 0, fmt: (v) => CX.pct(v), aoMudar: des });
    const q = CX.quadro(host, { h: 280, m: { l: 44, r: 150 } });
    const x = d3.scaleLinear().domain([0, 9]).range([0, q.iw]);
    const lei = CX.leitura(host);
    const nV = CX.num(lei, "efeito verdadeiro em A"), nD = CX.num(lei, "DiD estimado", true), nA = CX.num(lei, "só antes × depois em A");
    const txt = CX.frase(host);
    function des() {
      const E = sE.valor(), dt = sT.valor(), cont = sC.valor();
      const B = d3.range(10).map((t) => 50 + 2 * t + (t >= 5 ? cont * E : 0));
      const A = d3.range(10).map((t) => 60 + (2 + dt) * t + (t >= 5 ? E : 0));
      const Acf = d3.range(10).map((t) => 60 + (2 + dt) * t);
      const y = d3.scaleLinear().domain([40, 130]).range([q.ih, 0]);
      CX.eixos(q, x, y, { xl: "período (a farmácia abre no 5)", yl: "vendas" });
      q.g.selectAll(".l").remove();
      q.g.append("rect").attr("class", "l").attr("x", x(4.5)).attr("width", x(9) - x(4.5)).attr("height", q.ih).attr("fill", "#f3efe3");
      [[A, C.acento, "Rua A (tratada)", 2.4], [Acf, C.acento, "A sem a farmácia", 1.5, "5 4"], [B, C.azul, "Rua B (comparação)", 2.4]].forEach(([v, cc, n, lw, tr]) => {
        q.g.append("path").attr("class", "l").attr("fill", "none").attr("stroke", cc).attr("stroke-width", lw).attr("stroke-dasharray", tr || null).attr("d", d3.line().x((_, i) => x(i)).y((d) => y(d))(v));
        q.g.append("text").attr("class", "l rot").attr("x", q.iw + 4).attr("y", y(v[9]) + 4).style("fill", cc).text(n);
      });
      const m = (v, a, b) => S.media(v.slice(a, b));
      const did = (m(A, 5, 10) - m(A, 0, 5)) - (m(B, 5, 10) - m(B, 0, 5));
      nV.set(f(E, 1)); nD.set(f(did, 1)); nA.set(f(m(A, 5, 10) - m(A, 0, 5), 1));
      txt.innerHTML = dt !== 0 ? "As ruas já andavam em ritmos diferentes antes da farmácia: a diferença de tendência entra no DiD como se fosse efeito. É por isso que o event-study olha os períodos anteriores." : cont > 0 ? "A política também chegou à rua de comparação: o DiD mede só a diferença de intensidade. Com um marco federal, não há rua B intocada — foi o caso do #23." : "Com tendências paralelas e comparação intocada, o DiD recupera o efeito verdadeiro; o antes × depois de A sozinho inclui a tendência que as duas ruas compartilham.";
    }
    des();
  });

  /* ---------------- 4.5 FDR ---------------- */
  CX.def("fdr", (host) => {
    const ctl = CX.ctrl(host);
    let m = 135;
    CX.seg(ctl, { opcoes: [[36, "36 (#21)"], [135, "135 (#37)"], [144, "144 (#38)"], [192, "192 (#52)"]], val: m, aoMudar: (k) => { m = k; des(); } });
    const sK = CX.slider(ctl, { rot: "efeitos verdadeiros na grade", min: 0, max: 20, val: 0, fmt: String, aoMudar: des });
    CX.btn(ctl, "sortear", () => { sem++; des(); });
    let sem = 1;
    const q = CX.quadro(host, { h: 290, m: { l: 50, r: 20, t: 14, b: 38 } });
    const lei = CX.leitura(host);
    const nB = CX.num(lei, "p < 0,05 sem correção"), nS = CX.num(lei, "sobreviventes ao BH", true), nF = CX.num(lei, "falsos entre os p < 0,05");
    const tb = h("table", { class: "cx-tab" });
    tb.innerHTML = `<tr><th>placar do trabalho</th><th>testes na família</th><th>sobreviventes ao FDR</th></tr>
      <tr><td>#21 correlações estaduais</td><td>36</td><td>0</td></tr><tr><td>#37 motor comum (estado)</td><td>≈ 135</td><td>≈ 7 acertos brutos, o que o acaso daria</td></tr>
      <tr><td>#38 grade exploratória por AMC</td><td>144</td><td>0</td></tr><tr><td>#52 aptidão exógena</td><td>192</td><td>2</td></tr>`;
    host.appendChild(tb);
    function des() {
      const r = CX.rng(sem * 31 + m), k = sK.valor();
      const ps = d3.range(m).map((i) => ({ v: i < k ? Math.pow(r(), 6) * 0.02 : r(), real: i < k })).sort((a, b) => a.v - b.v);
      let corte = -1; ps.forEach((p, i) => { if (p.v <= ((i + 1) * 0.05) / m) corte = i; });
      const x = d3.scaleLinear().domain([1, Math.min(m, 40)]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 0.12]).range([q.ih, 0]);
      CX.eixos(q, x, y, { xl: "posição do p-valor, do menor ao maior (primeiros 40)", yl: "p-valor", yf: (v) => f(v, 2) });
      q.g.selectAll(".l").remove();
      q.g.append("line").attr("class", "l").attr("x1", 0).attr("x2", q.iw).attr("y1", y(0.05)).attr("y2", y(0.05)).attr("stroke", "#999").attr("stroke-dasharray", "4 3");
      q.g.append("text").attr("class", "l rot-m").attr("x", q.iw).attr("y", y(0.05) - 4).attr("text-anchor", "end").text("0,05 sem correção");
      q.g.append("line").attr("class", "l").attr("x1", x(1)).attr("x2", x(40)).attr("y1", y(0.05 / m)).attr("y2", y((40 * 0.05) / m)).attr("stroke", C.acento).attr("stroke-width", 2);
      q.g.append("text").attr("class", "l rot").attr("x", x(40)).attr("y", y((40 * 0.05) / m) - 6).attr("text-anchor", "end").style("fill", C.acento).text("linha do BH: k × 0,05 ÷ " + m);
      q.g.selectAll("circle.l").data(ps.slice(0, 40)).join("circle").attr("class", "l").attr("cx", (_, i) => x(i + 1)).attr("cy", (p) => y(Math.min(0.12, p.v))).attr("r", 4.5)
        .attr("fill", (p, i) => (i <= corte ? C.acento : "#fff")).attr("stroke", (p) => (p.real ? C.veg : "#777")).attr("stroke-width", (p) => (p.real ? 2.5 : 1.2));
      const brutos = ps.filter((p) => p.v < 0.05);
      nB.set(String(brutos.length)); nS.set(String(corte + 1)); nF.set(String(brutos.filter((p) => !p.real).length));
    }
    des();
    CX.frase(host, "Contorno verde: efeito verdadeiro; cinza: acaso. Preenchido: sobrevive ao BH. Com zero efeitos verdadeiros e 135 testes, alguns p ficam abaixo de 0,05 por puro acaso, e nenhum sobrevive à linha do BH.");
  });

  /* ---------------- 4.6 Bootstrap ---------------- */
  CX.def("boot", (host) => {
    CX.modos(host, {
      simples(c) {
        const A = [{ n: "A", km: 0, p0: 10, p1: 2 }, { n: "B", km: 100, p0: 10, p1: 10 }, { n: "C", km: 200, p0: 10, p1: 18 }];
        const reps = [];
        const ctl = CX.ctrl(c);
        const r = CX.rng(12);
        CX.btn(ctl, "sortear uma réplica", () => { reps.push(sorteia()); des(); }, true);
        CX.btn(ctl, "sortear mais 500", () => { for (let i = 0; i < 500; i++) reps.push(sorteia()); des(); });
        CX.btn(ctl, "zerar", () => { reps.length = 0; des(); });
        function sorteia() {
          const s = [0, 1, 2].map(() => A[Math.floor(r() * 3)]);
          const c0 = d3.sum(s, (a) => a.km * a.p0) / d3.sum(s, (a) => a.p0), c1 = d3.sum(s, (a) => a.km * a.p1) / d3.sum(s, (a) => a.p1);
          return { s: s.map((a) => a.n).join(", "), d: c1 - c0 };
        }
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nO = CX.num(lei, "ΔNorte original"), nR = CX.num(lei, "réplicas"), nI = CX.num(lei, "faixa de 95% das réplicas", true);
        nO.set("+53 km");
        function des() {
          a1.innerHTML = "<table class='cx-tab'><tr><th>réplica</th><th>papéis sorteados</th><th>ΔNorte</th></tr>" + reps.slice(-8).map((p, i) => `<tr><td>${reps.length - Math.min(8, reps.length) + i + 1}</td><td>${p.s}</td><td>${fs(p.d, 0)} km</td></tr>`).join("") + "</table>";
          a2.replaceChildren();
          const q = CX.quadro(a2, { w: 340, h: 220, m: { l: 30, r: 10, t: 14, b: 34 } });
          const x = d3.scaleLinear().domain([-10, 110]).range([0, q.iw]);
          CX.eixos(q, x, null, { xl: "ΔNorte das réplicas (km)" });
          if (reps.length) {
            const bins = d3.bin().domain(x.domain()).thresholds(24)(reps.map((p) => p.d));
            const y = d3.scaleLinear().domain([0, d3.max(bins, (b) => b.length)]).range([q.ih, 0]);
            q.g.selectAll("rect").data(bins).join("rect").attr("x", (b) => x(b.x0)).attr("width", (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr("y", (b) => y(b.length)).attr("height", (b) => q.ih - y(b.length)).attr("fill", C.pasto);
          }
          q.g.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "3 3");
          nR.set(String(reps.length));
          nI.set(reps.length > 20 ? `[${fs(S.quantil(reps.map((p) => p.d), 0.025), 0)}; ${fs(S.quantil(reps.map((p) => p.d), 0.975), 0)}] km` : "—");
        }
        des();
        CX.frase(c, "Cada réplica sorteia 3 papéis com reposição. Quando a AMC A (que perdeu pasto) ou a C (que ganhou) fica de fora, o deslocamento treme. Réplicas com as três iguais dão zero: são as poucas barras no traço.");
      },
      async dados(c) {
        const m = await CX.dado("metodo_centro_massa.json");
        const ctl = CX.ctrl(c);
        let v = "pastagem", bloco = "166";
        CX.seg(ctl, { opcoes: [["pastagem", "pastagem"], ["bovinos", "rebanho"], ["agricultura", "agricultura"], ["veg_natural", "vegetação"]], val: v, aoMudar: (k) => { v = k; roda(); } });
        const ctl2 = CX.ctrl(c);
        CX.seg(ctl2, { rot: "blocos", opcoes: Object.keys(m.blocos).sort((a, b) => b - a).map((k) => [k, k === "166" ? "166 blocos (AMC a AMC)" : k + " blocos"]), val: bloco, aoMudar: (k) => { bloco = k; roda(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nD = CX.num(lei, "ΔNorte observado"), nI = CX.num(lei, "IC 95% (2.000 réplicas, aqui)", true), nL = CX.num(lei, "largura do intervalo"), nO = CX.num(lei, "IC do #32 (AMC a AMC)");
        const txt = CX.frase(c);
        function roda() {
          const r = CX.rng(42), W0 = m.pesos[v][0], W1 = m.pesos[v][39], ids = m.blocos[bloco], nb = +bloco;
          const membros = d3.range(nb).map((b) => ids.map((x, i) => (x === b ? i : -1)).filter((i) => i >= 0));
          const cy = m.amc.map((a) => a.cy);
          const cent = (W, cnt) => { let s = 0, sw = 0; for (let i = 0; i < W.length; i++) { const w = W[i] * cnt[i]; s += w * cy[i]; sw += w; } return s / sw; };
          const um = new Array(166).fill(1), obs = cent(W1, um) - cent(W0, um);
          const reps = [];
          for (let b = 0; b < 2000; b++) {
            const cnt = new Array(166).fill(0);
            for (let k = 0; k < nb; k++) membros[Math.floor(r() * nb)].forEach((i) => cnt[i]++);
            reps.push(cent(W1, cnt) - cent(W0, cnt));
          }
          const lo = S.quantil(reps, 0.025), hi = S.quantil(reps, 0.975);
          alvo.replaceChildren();
          const q = CX.quadro(alvo, { h: 250, m: { l: 40, r: 16, t: 20, b: 36 } });
          const x = d3.scaleLinear().domain([Math.min(-10, d3.min(reps)), Math.max(20, d3.max(reps))]).nice().range([0, q.iw]);
          const bins = d3.bin().domain(x.domain()).thresholds(50)(reps);
          const y = d3.scaleLinear().domain([0, d3.max(bins, (b) => b.length)]).range([q.ih, 0]);
          CX.eixos(q, x, null, { xl: "ΔNorte 1985→2024 em cada réplica (km)" });
          q.g.append("rect").attr("x", x(lo)).attr("width", x(hi) - x(lo)).attr("y", 0).attr("height", q.ih).attr("fill", C.acento).attr("opacity", 0.08);
          q.g.selectAll("rect.b").data(bins).join("rect").attr("class", "b").attr("x", (b) => x(b.x0)).attr("width", (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr("y", (b) => y(b.length)).attr("height", (b) => q.ih - y(b.length)).attr("fill", (b) => (b.x1 < lo || b.x0 > hi ? "#d9d5ca" : C.acento));
          q.g.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", -6).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-width", 1.5);
          q.g.append("text").attr("class", "rot-f").attr("x", x(0) + 4).attr("y", -8).text("zero");
          nD.set(fs(obs, 1) + " km"); nI.set(`[${fs(lo, 1)}; ${fs(hi, 1)}]`); nL.set(f(hi - lo, 1) + " km");
          const of = m.oficial.boot.find((b) => b.variavel === v && b.janela.startsWith("L"));
          nO.set(of ? `[${fs(of.dN_lo, 1)}; ${fs(of.dN_hi, 1)}]` : "—");
          txt.innerHTML = (lo > 0 ? "A nuvem inteira fica à direita do zero: o deslocamento sobrevive aos buracos e às duplicatas." : "A nuvem cruza o zero: a palavra certa é \"ancorada\", não o número do ponto.") +
            (bloco === "166" ? " Sorteando AMC a AMC, a conta refeita aqui chega a um intervalo muito próximo do #32 (as réplicas sorteadas não são as mesmas)." : ` Sorteando ${bloco} blocos de AMCs vizinhas (k-médias sobre os centroides, como no #55), o intervalo alarga porque vizinhas deixam de contar como independentes.`);
        }
        roda();
      },
    });
  });

  /* ---------------- 4.7 Permutação ---------------- */
  CX.def("perm", (host) => {
    CX.modos(host, {
      simples(c) {
        const A = [12, 15, 14, 18, 16, 17, 13, 19], B = [11, 12, 10, 14, 13, 12, 15, 11];
        const obs = S.media(A) - S.media(B), todos = [...A, ...B];
        const perms = [];
        const r = CX.rng(3);
        const ctl = CX.ctrl(c);
        CX.btn(ctl, "embaralhar 1 vez", () => { perms.push(emb()); des(true); }, true);
        CX.btn(ctl, "embaralhar 1.000", () => { for (let i = 0; i < 1000; i++) perms.push(emb()); des(); });
        let ultimo = null;
        function emb() { const a = [...todos]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } ultimo = a; return S.media(a.slice(0, 8)) - S.media(a.slice(8)); }
        const pontos = h("div"); c.appendChild(pontos);
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nO = CX.num(lei, "diferença observada (A − B)"), nP = CX.num(lei, "p por permutação", true);
        nO.set(f(obs, 2));
        function des(mostra) {
          const lista = ultimo && mostra ? ultimo : todos;
          pontos.innerHTML = `<div class="cx-leg">${mostra && ultimo ? "rótulos embaralhados:" : "rótulos originais:"} ${lista.map((v, i) => `<span style="font-weight:700;color:${i < 8 ? C.acento : C.azul}">${v}</span>`).join(" ")}</div>`;
          alvo.replaceChildren();
          const q = CX.quadro(alvo, { h: 200, m: { l: 30, r: 16, t: 14, b: 34 } });
          const x = d3.scaleLinear().domain([-5, 5]).range([0, q.iw]);
          CX.eixos(q, x, null, { xl: "diferença de médias com rótulos embaralhados" });
          if (perms.length) {
            const bins = d3.bin().domain(x.domain()).thresholds(40)(perms);
            const y = d3.scaleLinear().domain([0, d3.max(bins, (b) => b.length)]).range([q.ih, 0]);
            q.g.selectAll("rect").data(bins).join("rect").attr("x", (b) => x(b.x0)).attr("width", (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr("y", (b) => y(b.length)).attr("height", (b) => q.ih - y(b.length)).attr("fill", C.cinza);
            nP.set(CX.p((perms.filter((p) => p >= obs).length + 1) / (perms.length + 1)));
          }
          q.g.append("line").attr("x1", x(obs)).attr("x2", x(obs)).attr("y1", 0).attr("y2", q.ih).attr("stroke", C.acento).attr("stroke-width", 3);
        }
        des();
      },
      async dados(c) {
        const b = await CX.base();
        const M = b.macro;
        const dz = (() => { const d = S.diff(M.cambio), mu = S.media(d), sd = Math.sqrt(d.reduce((s, v) => s + (v - mu) ** 2, 0) / d.length); return d.map((v) => (v - mu) / sd); })();
        const anos = M.anos.slice(1);
        const ctl = CX.ctrl(c);
        const sG = CX.slider(ctl, { rot: "giro da série (anos)", min: 0, max: dz.length - 1, val: 0, fmt: (v) => (v ? v + " ano" + (v > 1 ? "s" : "") : "original"), aoMudar: des });
        const q = CX.quadro(c, { h: 250, m: { l: 50, r: 16, t: 24, b: 36 } });
        const x = d3.scaleBand().domain(anos).range([0, q.iw]).padding(0.15), y = d3.scaleLinear().domain([-3, 3.2]).range([q.ih, 0]);
        CX.eixos(q, x, y, { yl: "choque cambial atribuído ao ano (desvios-padrão)", xf: (a) => (a % 5 === 0 ? a : ""), grade: true });
        const txt = CX.frase(c);
        const S1 = b.horse.find((k) => k.spec === "S1");
        const lei = CX.leitura(c);
        CX.num(lei, "p com erro-padrão agrupado (#52, S1)").set(f(S1.p_agrupado, 3));
        CX.num(lei, "p pela rotação do shifter (S1)", true).set(f(S1.p_circular, 3));
        CX.num(lei, "menor p possível com 38 giros").set(f(1 / 38, 3));
        function des() {
          const k = sG.valor(), rot = dz.map((_, i) => dz[(i + k) % dz.length]);
          q.g.selectAll("rect.b").data(rot).join("rect").attr("class", "b").attr("x", (_, i) => x(anos[i])).attr("width", x.bandwidth())
            .attr("y", (v) => y(Math.max(0, v))).attr("height", (v) => Math.abs(y(v) - y(0))).attr("fill", (v) => (v > 0 ? C.acento : C.azul)).attr("rx", 2)
            .on("mousemove", (ev, v) => { const i = rot.indexOf(v); CX.tip.mostra(ev, `<b>${anos[i]}</b><br>choque atribuído: ${fs(v, 2)} dp<br>(verdadeiro de ${anos[(i + k) % dz.length]})`); }).on("mouseleave", CX.tip.esconde);
          txt.innerHTML = k === 0
            ? "A série verdadeira: a variação anual do câmbio real, padronizada. Em 1999, a desvalorização aparece como o maior choque positivo. Gire a série: cada giro atribui a cada ano o choque de outro, preservando a forma da série, e o teste recalcula o coeficiente com a série girada."
            : `Giro de ${k} ano(s): o choque de ${anos[k % dz.length]} foi parar em ${anos[0]}. Com a exposição das AMCs intacta, qualquer relação entre choque e resposta que sobreviva aqui é acaso. O p da rotação é a fração dos 38 giros que chegam ao valor observado.`;
        }
        des();
        CX.frase(c, "Para o resultado-manchete do motor comum, a rotação dá p entre 0,07 e 0,13, acima do corte de 5%; o p agrupado (≈ 0,03) era otimista, porque com um só choque nacional as AMCs não são 166 experimentos independentes. O que sustenta o padrão é a especificidade dos placebos.");
      },
    });
  });

  /* ---------------- 4.8 Jackknife ---------------- */
  CX.def("jack", (host) => {
    CX.modos(host, {
      simples(c) {
        const base = [[1, 1.8], [2, 2.5], [3, 2.9], [4, 3.8], [5, 4.1], [6, 4.4], [7, 5.3], [8, 5.6], [9, 6.3], [9.6, 1.2]];
        const fora = new Set();
        const q = CX.quadro(c, { h: 280, m: { l: 40, r: 16, t: 14, b: 30 } });
        const x = d3.scaleLinear().domain([0, 10]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 7]).range([q.ih, 0]);
        CX.eixos(q, x, y);
        const gL = q.g.append("g"), gP = q.g.append("g");
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "β com todos"), nA = CX.num(lei, "β sem os pontos riscados", true);
        const lista = h("div", { class: "cx-leg" }); c.appendChild(lista);
        const todos = S.ols1(base.map((p) => p[0]), base.map((p) => p[1]));
        nB.set(f(todos.b, 2));
        const jk = base.map((_, i) => { const s = base.filter((_, j) => j !== i); return S.ols1(s.map((p) => p[0]), s.map((p) => p[1])).b; });
        lista.innerHTML = "β sem cada ponto: " + jk.map((b, i) => `<span style="${Math.abs(b - todos.b) > 0.2 ? "color:" + C.acento + ";font-weight:700" : ""}">#${i + 1}: ${f(b, 2)}</span>`).join(" · ");
        function des() {
          const s = base.filter((_, i) => !fora.has(i)), fit = S.ols1(s.map((p) => p[0]), s.map((p) => p[1]));
          gL.selectAll("*").remove();
          gL.append("line").attr("x1", x(0)).attr("x2", x(10)).attr("y1", y(todos.a)).attr("y2", y(todos.a + todos.b * 10)).attr("stroke", "#bbb").attr("stroke-dasharray", "4 3");
          gL.append("line").attr("x1", x(0)).attr("x2", x(10)).attr("y1", y(fit.a)).attr("y2", y(fit.a + fit.b * 10)).attr("stroke", "#111").attr("stroke-width", 2.2);
          gP.selectAll("circle").data(base).join("circle").attr("cx", (p) => x(p[0])).attr("cy", (p) => y(p[1])).attr("r", 7).style("cursor", "pointer")
            .attr("fill", (_, i) => (fora.has(i) ? "#fff" : C.acento)).attr("stroke", C.acento).attr("stroke-width", 2)
            .on("click", (_, p) => { const i = base.indexOf(p); fora.has(i) ? fora.delete(i) : fora.add(i); des(); });
          nA.set(f(fit.b, 2));
        }
        des();
        CX.frase(c, "O ponto #10, lá embaixo à direita, puxa a reta sozinho: sem ele, o β muda muito mais do que sem qualquer outro. Clique nos pontos para tirá-los e recolocá-los.");
      },
      async dados(c) {
        const [b, m] = await Promise.all([CX.base(), CX.dado("metodo_centro_massa.json")]);
        const J = b.jackknife;
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const q = CX.quadro(a1, { w: 340, h: 290, m: { l: 50, r: 10, t: 44, b: 34 } });
        const hs = [...new Set(J.map((k) => k.headline))];
        const x = d3.scaleBand().domain(hs).range([0, q.iw]).padding(0.3), y = d3.scaleLinear().domain([-0.05, 0.05]).range([q.ih, 0]);
        CX.eixos(q, null, y, { yl: "β sem cada ano", yf: (v) => f(v, 2) });
        q.g.append("text").attr("class", "rot-f").attr("x", -44).attr("y", -30).text("#54: tirando cada um dos 38 anos");
        q.g.append("line").attr("class", "zero").attr("x1", 0).attr("x2", q.iw).attr("y1", y(0)).attr("y2", y(0));
        const r = CX.rng(1);
        q.g.selectAll("circle").data(J).join("circle").attr("cx", (k) => x(k.headline) + x.bandwidth() / 2 + (r() - 0.5) * x.bandwidth() * 0.8).attr("cy", (k) => y(k.beta)).attr("r", 3.5)
          .attr("fill", (k) => (k.beta > 0 ? C.acento : C.azul)).attr("opacity", 0.75)
          .on("mousemove", (ev, k) => CX.tip.mostra(ev, `sem ${k.ano_removido}<br>β = ${f(k.beta, 4)} · p = ${f(k.p, 3)}`)).on("mouseleave", CX.tip.esconde);
        hs.forEach((hh) => q.g.append("text").attr("class", "rot").attr("x", x(hh) + x.bandwidth() / 2).attr("y", q.ih + 18).attr("text-anchor", "middle").text(hh.replace(/ \(#\d+\)/, "")));
        // centro de massa sem cada AMC
        const W0 = m.pesos.pastagem[0], W1 = m.pesos.pastagem[39];
        const cen = (W, sem) => { let s = 0, sw = 0; m.amc.forEach((a, i) => { if (i === sem) return; s += W[i] * a.cy; sw += W[i]; }); return s / sw; };
        const tudo = cen(W1, -1) - cen(W0, -1);
        const jk = m.amc.map((a, i) => ({ nome: a.nome, d: cen(W1, i) - cen(W0, i) }));
        const q2 = CX.quadro(a2, { w: 340, h: 280, m: { l: 40, r: 10, t: 30, b: 34 } });
        const x2 = d3.scaleLinear().domain(d3.extent(jk, (k) => k.d)).nice().range([0, q2.iw]);
        CX.eixos(q2, x2, null, { xl: "ΔNorte da pastagem sem cada AMC (km)" });
        q2.g.append("text").attr("class", "rot-f").attr("y", -16).text("#32 refeito: tirando cada uma das 166 AMCs");
        q2.g.selectAll("circle").data(jk).join("circle").attr("cx", (k) => x2(k.d)).attr("cy", () => 40 + r() * (q2.ih - 60)).attr("r", 3.5).attr("fill", C.pasto)
          .on("mousemove", (ev, k) => CX.tip.mostra(ev, `sem <b>${k.nome}</b><br>ΔNorte = ${fs(k.d, 1)} km`)).on("mouseleave", CX.tip.esconde);
        q2.g.append("line").attr("x1", x2(tudo)).attr("x2", x2(tudo)).attr("y1", 0).attr("y2", q2.ih).attr("stroke", "#111").attr("stroke-dasharray", "4 3");
        const ext = d3.extent(jk, (k) => k.d), mx = jk.reduce((a, b2) => (Math.abs(b2.d - tudo) > Math.abs(a.d - tudo) ? b2 : a));
        CX.frase(c, `À esquerda, o β do motor comum sem cada ano: nenhum ponto cruza o zero, nas duas versões da exposição (proxy de área e aptidão exógena). À direita, o deslocamento da pastagem recalculado sem cada AMC varia só de ${fs(ext[0], 1)} a ${fs(ext[1], 1)} km (traço: ${fs(tudo, 1)} km com todas); a AMC mais influente é ${mx.nome}.`);
      },
    });
  });

  /* ---------------- 4.9 BIC com n gigante ---------------- */
  CX.def("bic", async (host) => {
    const I = (await CX.base()).idade;
    const ctl = CX.ctrl(host);
    const sN = CX.slider(ctl, { rot: "tamanho da amostra", min: 2, max: 7.3, passo: 0.05, val: 3, fmt: (v) => f(Math.pow(10, v), 0), aoMudar: des });
    const q = CX.quadro(host, { h: 270, m: { l: 70, r: 20, t: 14, b: 40 } });
    const x = d3.scaleLog().domain([100, 2e7]).range([0, q.iw]), y = d3.scaleLog().domain([0.1, 1e8]).range([q.ih, 0]);
    CX.eixos(q, x, y, { xl: "n (escala logarítmica)", yf: (v) => (Math.log10(v) % 2 === 0 ? d3.format("~s")(v) : ""), yl: "unidades de BIC (log)", xf: (v) => (Math.log10(v) % 1 === 0 ? d3.format("~s")(v) : "") });
    const delta = 0.0004, k = 3;
    const ns = d3.range(2, 7.31, 0.05).map((e) => Math.pow(10, e));
    q.g.append("path").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2.4).attr("d", d3.line().x((n) => x(n)).y((n) => y(Math.max(0.1, 2 * n * delta)))(ns));
    q.g.append("path").attr("fill", "none").attr("stroke", C.azul).attr("stroke-width", 2.4).attr("d", d3.line().x((n) => x(n)).y((n) => y(k * Math.log(n)))(ns));
    const tg = q.g.append("text").attr("class", "rot").attr("x", x(4e5)).attr("y", y(2 * 4e5 * delta) - 10).attr("text-anchor", "end");
    tg.append("tspan").text("ganho de ajuste (cresce com n) "); tg.append("tspan").style("fill", C.acento).text("■");
    const tm = q.g.append("text").attr("class", "rot").attr("x", x(3e5)).attr("y", y(k * Math.log(3e5)) + 18);
    tm.append("tspan").style("fill", C.azul).text("■ "); tm.append("tspan").text("multa (cresce com log n)");
    q.g.append("circle").attr("cx", x(I.n_eventos)).attr("cy", y(I.bic1 - I.bic2)).attr("r", 6).attr("fill", "#111");
    q.g.append("text").attr("class", "rot-f").attr("x", x(I.n_eventos) - 8).attr("y", y(I.bic1 - I.bic2) - 10).attr("text-anchor", "end").text(`ΔBIC real do #28: ${f((I.bic1 - I.bic2) / 1e6, 1)} milhões`);
    const mk = q.g.append("line").attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "3 3");
    const lei = CX.leitura(host);
    const nG = CX.num(lei, "ganho de ajuste"), nM = CX.num(lei, "multa"), nD = CX.num(lei, "ΔBIC (ganho − multa)", true);
    function des() {
      const n = Math.pow(10, sN.valor()), g = 2 * n * delta, mu = k * Math.log(n);
      mk.attr("x1", x(n)).attr("x2", x(n));
      nG.set(f(g, 1)); nM.set(f(mu, 1)); nD.set(fs(g - mu, 1) + (g > mu ? " → prefere o modelo maior" : " → prefere o menor"));
    }
    des();
    CX.frase(host, "O afastamento entre os dois modelos é fixo e minúsculo (0,0002 de log-verossimilhança por observação). Com poucas centenas de observações, a multa vence; com milhões, o ganho vence por muito, sem que a diferença entre os modelos tenha mudado. O ponto preto é o ΔBIC real do censo da idade do pasto.");
  });

  /* ---------------- 4.10 Shift-share ---------------- */
  CX.def("ss", (host) => {
    CX.modos(host, {
      simples(c) {
        const cid = [["Cidade 1", 0.4], ["Cidade 2", 0.25], ["Cidade 3", 0.1], ["Cidade 4", 0.05]];
        const ctl = CX.ctrl(c);
        const sC = CX.slider(ctl, { rot: "choque nacional (queda das lojas de rua)", min: 0, max: 50, val: 30, fmt: (v) => v + "%", aoMudar: des });
        const alvo = h("div"); c.appendChild(alvo);
        function des() {
          alvo.replaceChildren();
          barrasH(alvo, cid.map(([n, e]) => [`${n} (exposição ${CX.pct(e)})`, (sC.valor() / 100) * e * 100, C.acento, f((sC.valor() / 100) * e * 100, 1) + "% dos empregos"]), { xl: "dose do choque = choque × exposição", xf: (v) => v + "%", l: 210, max: 22 });
        }
        des();
        CX.frase(c, "O choque é o mesmo para todas; a exposição foi medida antes dele. A dose de cada cidade não depende de nada que ela tenha feito depois.");
      },
      async dados(c) {
        const [b, m] = await Promise.all([CX.base(), CX.dado("metodo_centro_massa.json")]);
        const M = b.macro;
        const d = S.diff(M.cambio), mu = S.media(d), sd = Math.sqrt(d.reduce((s, v) => s + (v - mu) ** 2, 0) / d.length), dz = d.map((v) => (v - mu) / sd);
        const aptPor = Object.fromEntries(b.apt.map((a) => [a.code, a.expo]));
        const expo = m.amc.map((a) => aptPor[a.code]);
        const ctl = CX.ctrl(c);
        const sA = CX.slider(ctl, { rot: "ano do choque", min: 1986, max: 2024, val: 1999, fmt: String, aoMudar: des });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const q = CX.quadro(a1, { w: 340, h: 260, m: { l: 44, r: 10, t: 20, b: 30 } });
        const x = d3.scaleLinear().domain([1985, 2024]).range([0, q.iw]), y = d3.scaleLinear().domain(d3.extent(M.cambio)).nice().range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: CX.anoF, xt: 5, yl: "câmbio real efetivo (índice)" });
        q.g.append("path").attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 2).attr("d", d3.line().x((_, i) => x(M.anos[i])).y((v) => y(v))(M.cambio));
        const mk = q.g.append("circle").attr("r", 5).attr("fill", C.acento);
        const q2 = CX.quadro(a2, { w: 320, h: 340, m: { t: 4, r: 4, b: 4, l: 4 } });
        const mp = CX.mapaAMC(q2.g, m, q2.iw, q2.ih);
        const lei = CX.leitura(c);
        const nC = CX.num(lei, "choque do ano (desvios-padrão)", true), nR = CX.num(lei, "r entre aptidão e latitude (166 AMCs)");
        nR.set(f(S.corr(b.apt.map((a) => a.expo), b.apt.map((a) => a.lat)), 2));
        const txt = CX.frase(c);
        function des() {
          const a = sA.valor(), i = a - 1986, z = dz[i];
          mk.attr("cx", x(a)).attr("cy", y(M.cambio[i + 1]));
          const dose = expo.map((e) => z * e), L = d3.max(dose.map(Math.abs)) || 1;
          const cs = d3.scaleDiverging(d3.interpolateRdBu).domain([L, 0, -L]);
          mp.sel.attr("fill", (_, k) => cs(dose[k])).on("mousemove", (ev, am) => { const k = m.amc.indexOf(am); CX.tip.mostra(ev, `<b>${am.nome}</b><br>exposição (aptidão padronizada): ${fs(expo[k], 2)}<br>dose em ${a}: ${fs(dose[k], 2)}`); }).on("mouseleave", CX.tip.esconde);
          nC.set(fs(z, 2));
          txt.innerHTML = `Em ${a} a variação do câmbio foi de ${fs(z, 2)} desvios-padrão. Vermelho: dose positiva; azul: negativa. Como a exposição varia com a latitude, a dose desenha um gradiente Sul–Norte — e é exatamente por isso que a latitude precisou entrar na mesma conta (verbete 5.3).`;
        }
        des();
      },
    });
  });
})();
