/* Caderno de conceitos — Parte 3: gramática estatística */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  /* dispersão genérica com reta opcional; pts = [{x,y,cor?,tip?}] */
  function dispersao(pai, pts, o = {}) {
    const q = CX.quadro(pai, { w: o.w || 680, h: o.h || 300, m: o.m || { l: 56, r: 16, t: 14, b: 38 } });
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const qx = o.clip ? [S.quantil(xs, 0.01), S.quantil(xs, 0.99)] : d3.extent(xs);
    const qy = o.clip ? [S.quantil(ys, 0.01), S.quantil(ys, 0.99)] : d3.extent(ys);
    const pad = (a) => { const d = (a[1] - a[0]) * 0.06 || 1; return [a[0] - d, a[1] + d]; };
    const x = d3.scaleLinear().domain(o.xdom || pad(qx)).range([0, q.iw]).nice();
    const y = d3.scaleLinear().domain(o.ydom || pad(qy)).range([q.ih, 0]).nice();
    CX.eixos(q, x, y, { xl: o.xl, yl: o.yl, xf: o.xf, yf: o.yf });
    const dentro = pts.filter((p) => p.x >= x.domain()[0] && p.x <= x.domain()[1] && p.y >= y.domain()[0] && p.y <= y.domain()[1]);
    q.g.append("g").selectAll("circle").data(dentro).join("circle").attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y))
      .attr("r", o.r || 3.5).attr("fill", (p) => p.cor || C.cinza).attr("opacity", o.op ?? 0.8)
      .on("mousemove", (ev, p) => p.tip && CX.tip.mostra(ev, p.tip)).on("mouseleave", CX.tip.esconde);
    if (o.reta) {
      const [a, b] = o.reta, [x0, x1] = x.domain();
      q.g.append("line").attr("x1", x(x0)).attr("x2", x(x1)).attr("y1", y(a + b * x0)).attr("y2", y(a + b * x1)).attr("stroke", o.corReta || C.acento).attr("stroke-width", 2.5);
    }
    q.x = x; q.y = y;
    return q;
  }
  CX.dispersao = dispersao;

  /* ---------------- 3.1 Correlação e confundidor ---------------- */
  CX.def("corr", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(8), dias = d3.range(120).map(() => { const T = Math.max(0, r() * 30 - 4); return { T, s: 15 + 4 * T + CX.normal(r) * 10, a: 3 + 0.25 * T + CX.normal(r) * 1.1 }; });
        const ctl = CX.ctrl(c);
        let filtro = false;
        CX.check(ctl, " olhar só os dias com a mesma chuva (entre 10 e 14 mm)", false, (b) => { filtro = b; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "r (guarda-chuvas × batidas)", true), nN = CX.num(lei, "dias considerados");
        const cs = d3.scaleSequential(d3.interpolateRgb("#e9d9a8", "#2f5f86")).domain([0, 26]);
        function des() {
          const sub = filtro ? dias.filter((d) => d.T >= 10 && d.T <= 14) : dias;
          alvo.replaceChildren();
          dispersao(alvo, sub.map((d) => ({ x: d.s, y: d.a, cor: cs(d.T), tip: `chuva: ${f(d.T, 1)} mm` })), { xl: "guarda-chuvas vendidos no dia", yl: "batidas de carro no dia", h: 260, xdom: [0, 140], ydom: [0, 14] });
          nR.set(f(S.corr(sub.map((d) => d.s), sub.map((d) => d.a)), 2)); nN.set(String(sub.length));
        }
        des();
        c.appendChild(h("div", { class: "cx-leg", html: `<span>cor de cada ponto: a chuva do dia</span><span><i style="background:#e9d9a8"></i>dia seco</span><span><i style="background:#2f5f86"></i>muita chuva</span>` }));
        CX.frase(c, "Com todos os dias juntos, r é alto: dias de guarda-chuva vendido são dias de batida. Olhando só dias com a mesma chuva, o r despenca, porque era a chuva que movia as duas coisas.");
      },
      async dados(c) {
        const g = (await CX.base()).go;
        const ctl = CX.ctrl(c);
        const pares = {
          val: ["agric", "soja_sidra_mt", "agricultura no satélite (Mha)", "soja produzida, IBGE (Mt)", "Duas fontes independentes (um satélite, um levantamento) medindo quase o mesmo fenômeno: r alto é o que se espera, e é validação. O #44 compara a latitude anual do centro da soja nas duas fontes e acha r = 0,89."],
          boi: ["pasto", "bovinos_mi", "pastagem (Mha)", "rebanho bovino (milhões de cabeças)", "Pastagem e rebanho: a correlação em nível mistura relação real (boi precisa de pasto) com tendência comum. O verbete seguinte separa as duas."],
        };
        let k = "val";
        CX.seg(ctl, { opcoes: [["val", "satélite × IBGE (validação)"], ["boi", "pastagem × rebanho"]], val: k, aoMudar: (v) => { k = v; des(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "r em nível", true), nD = CX.num(lei, "r em primeira diferença");
        const txt = CX.frase(c);
        const card = CX.frase(c, "<b>O caso do alarme (Trase, #45):</b> r = 0,986 entre o regressor \"volume de soja\" e a área plantada. Com r assim entre regressor e variável explicada, o β mede quase uma identidade. Trocado pelo volume exportado de verdade, o coeficiente-manchete caiu de +0,335 para +0,037.");
        card.style.borderLeftColor = C.acento;
        const cs = d3.scaleSequential(d3.interpolateViridis).domain([1985, 2024]);
        function des() {
          const [a, b, la, lb, t] = pares[k];
          const pts = g.anos.map((ano, i) => ({ x: g[a][i], y: g[b][i], cor: cs(ano), tip: `<b>${ano}</b><br>${la}: ${f(g[a][i], 2)}<br>${lb}: ${f(g[b][i], 2)}` })).filter((p) => p.y != null);
          alvo.replaceChildren();
          dispersao(alvo, pts, { xl: la, yl: lb, h: 260 });
          nR.set(f(S.corr(pts.map((p) => p.x), pts.map((p) => p.y)), 3));
          nD.set(f(S.corr(S.diff(pts.map((p) => p.x)), S.diff(pts.map((p) => p.y))), 3));
          txt.innerHTML = t + " Cor dos pontos: o ano (roxo = 1985, amarelo = 2024).";
        }
        des();
      },
    });
  });

  /* ---------------- 3.2 Primeira diferença ---------------- */
  CX.def("dif", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        let sem = 1;
        const sT = CX.slider(ctl, { rot: "quanto os dois crescem por ano", min: 0, max: 1, passo: 0.05, val: 0.5, fmt: (v) => f(v, 2), aoMudar: des });
        CX.btn(ctl, "sortear de novo", () => { sem++; des(); });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nN = CX.num(lei, "r em nível", true), nD = CX.num(lei, "r em diferença");
        function des() {
          const r = CX.rng(sem), n = 40, tr = sT.valor();
          let A = [0], B = [0];
          for (let t = 1; t < n; t++) { A.push(A[t - 1] + tr + CX.normal(r) * 0.6); B.push(B[t - 1] + tr + CX.normal(r) * 0.6); }
          a1.replaceChildren(); a2.replaceChildren();
          dispersao(a1, A.map((v, i) => ({ x: v, y: B[i], cor: C.azul, tip: `ano ${2000 + i}` })), { w: 340, h: 260, xl: "preço do cafezinho (índice)", yl: "celulares (índice)" });
          const dA = S.diff(A), dB = S.diff(B);
          dispersao(a2, dA.map((v, i) => ({ x: v, y: dB[i], cor: C.acento, tip: `de ${2000 + i} para ${2001 + i}` })), { w: 340, h: 260, xl: "quanto o café mudou no ano", yl: "quanto os celulares mudaram no ano" });
          nN.set(f(S.corr(A, B), 2)); nD.set(f(S.corr(dA, dB), 2));
        }
        des();
        CX.frase(c, "As duas séries são sorteadas de forma independente: não há relação nenhuma entre elas, só o fato de as duas crescerem com o tempo. Com o crescimento ligado, o r em nível vai para perto de 1; em diferença, fica perto de zero, que é a verdade.");
      },
      async dados(c) {
        const g = (await CX.base()).go;
        const ctl = CX.ctrl(c);
        const pares = { pb: ["pasto", "bovinos_mi", "pastagem (Mha)", "rebanho (mi cab.)"], av: ["agric", "veg", "agricultura (Mha)", "vegetação natural (Mha)"], am: ["agric", "mosaico", "agricultura (Mha)", "mosaico (Mha)"], ps: ["pasto", "soja_sidra_mt", "pastagem (Mha)", "soja produzida (Mt)"] };
        let k = "pb";
        CX.seg(ctl, { opcoes: [["pb", "pastagem × rebanho"], ["av", "agricultura × vegetação"], ["am", "agricultura × mosaico"], ["ps", "pastagem × soja"]], val: k, aoMudar: (v) => { k = v; des(); } });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nN = CX.num(lei, "r em nível", true), nD = CX.num(lei, "r em diferença");
        function des() {
          const [a, b, la, lb] = pares[k];
          const idx = g.anos.map((_, i) => i).filter((i) => g[b][i] != null);
          const A = idx.map((i) => g[a][i]), B = idx.map((i) => g[b][i]), anos = idx.map((i) => g.anos[i]);
          a1.replaceChildren(); a2.replaceChildren();
          dispersao(a1, A.map((v, i) => ({ x: v, y: B[i], cor: C.azul, tip: String(anos[i]) })), { w: 340, h: 260, xl: la, yl: lb });
          const dA = S.diff(A), dB = S.diff(B);
          dispersao(a2, dA.map((v, i) => ({ x: v, y: dB[i], cor: C.acento, tip: `${anos[i + 1]}` })), { w: 340, h: 260, xl: "Δ " + la, yl: "Δ " + lb });
          nN.set(f(S.corr(A, B), 2)); nD.set(f(S.corr(dA, dB), 2));
        }
        des();
        CX.frase(c, "Contas no agregado do estado, 1985–2024. Repare que alguns pares mudam de sinal ou de força ao passar para a diferença: o nível estava contando a tendência de 40 anos; a diferença conta o co-movimento de cada ano.");
      },
    });
  });

  /* ---------------- 3.3 Regressão e β ---------------- */
  CX.def("beta", (host) => {
    CX.modos(host, {
      simples(c) {
        const BASE = [[1, 215], [2, 160], [3, 305], [4, 245], [5, 355], [6, 425], [7, 395], [8, 545]];
        const pts = BASE.map(([x, y]) => ({ x, y }));
        const ctl = CX.ctrl(c);
        let quad = true;
        CX.check(ctl, " mostrar os quadrados dos resíduos", true, (b) => { quad = b; des(); });
        CX.btn(ctl, "acrescentar a casa com piscina aquecida", () => { if (!pts.some((p) => p.piscina)) pts.push({ x: 1.5, y: 640, piscina: true }); des(); });
        CX.btn(ctl, "recomeçar", () => { pts.splice(0, pts.length, ...BASE.map(([x, y]) => ({ x, y }))); des(); });
        const q = CX.quadro(c, { h: 320, m: { l: 56, r: 16, t: 10, b: 30 } });
        const x = d3.scaleLinear().domain([0, 10]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 700]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xl: "horas de ar-condicionado ligado por dia", yl: "conta de luz no mês (R$)" });
        const fundo = q.g.append("rect").attr("width", q.iw).attr("height", q.ih).attr("fill", "transparent").style("cursor", "crosshair");
        fundo.on("click", (ev) => { const [mx, my] = d3.pointer(ev); pts.push({ x: x.invert(mx), y: y.invert(my) }); des(); });
        const gQ = q.g.append("g"), gL = q.g.append("g"), gP = q.g.append("g");
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "β (inclinação)", true), nA = CX.num(lei, "intercepto (conta com o ar desligado)"), nR = CX.num(lei, "R²"), nS = CX.num(lei, "soma dos quadrados");
        function des() {
          const fit = S.ols1(pts.map((p) => p.x), pts.map((p) => p.y));
          gQ.selectAll("*").remove(); gL.selectAll("*").remove();
          if (quad) pts.forEach((p, i) => {
            const e = fit.res[i], ly = fit.a + fit.b * p.x, lado = Math.abs(y(p.y) - y(ly));
            gQ.append("rect").attr("x", x(p.x)).attr("y", Math.min(y(p.y), y(ly))).attr("width", lado).attr("height", lado).attr("fill", e > 0 ? C.azul : C.acento).attr("opacity", 0.24).attr("stroke", e > 0 ? C.azul : C.acento).attr("stroke-opacity", 0.5);
            gQ.append("line").attr("x1", x(p.x)).attr("x2", x(p.x)).attr("y1", y(p.y)).attr("y2", y(ly)).attr("stroke", "#555").attr("stroke-dasharray", "2 2");
          });
          gL.append("line").attr("x1", x(0)).attr("x2", x(10)).attr("y1", y(fit.a)).attr("y2", y(fit.a + fit.b * 10)).attr("stroke", "#111").attr("stroke-width", 2.2);
          gP.selectAll("circle").data(pts).join("circle").attr("r", 5.5).attr("fill", C.acento).attr("stroke", "#fff").attr("stroke-width", 1.5).style("cursor", "grab")
            .attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y))
            .call(d3.drag().on("drag", (ev, p) => { p.x = Math.max(0, Math.min(10, x.invert(ev.x))); p.y = Math.max(0, Math.min(700, y.invert(ev.y))); des(); }));
          nB.set("R$ " + f(fit.b, 0) + " por hora"); nA.set("R$ " + f(fit.a, 0)); nR.set(f(fit.r2, 2)); nS.set(f(fit.res.reduce((s, e) => s + e * e, 0), 0));
          txt.innerHTML = pts.some((p) => p.piscina)
            ? `Uma única casa, a da piscina aquecida, puxou a reta: a inclinação foi a R$ ${f(fit.b, 0)} por hora. Nada mudou nas outras oito casas.`
            : `A reta passa onde a soma das áreas dos quadrados é a menor possível. Cada hora diária de ar-condicionado vem acompanhada, em média, de R$ ${f(fit.b, 0)} a mais na conta.`;
        }
        const txt = CX.frase(c);
        des();
      },
      async dados(c) {
        const F = (await CX.base()).fwl;
        const ctl = CX.ctrl(c);
        let k = "local";
        CX.seg(ctl, { opcoes: [["local", "substituição local (β)"], ["viz", "vizinhos ao sul (θ)"]], val: k, aoMudar: (v) => { k = v; des(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "inclinação refeita aqui", true), nO = CX.num(lei, "valor do pipeline"), nN = CX.num(lei, "observações AMC-ano");
        const txt = CX.frase(c);
        function des() {
          const xs = k === "local" ? F.xl : F.x, ys = k === "local" ? F.yl : F.y;
          let sxy = 0, sxx = 0; xs.forEach((v, i) => { sxy += v * ys[i]; sxx += v * v; });
          const b = sxy / sxx;
          alvo.replaceChildren();
          dispersao(alvo, xs.map((v, i) => ({ x: v, y: ys[i], cor: k === "local" ? C.agric : C.azul })), {
            clip: true, r: 1.8, op: 0.35, reta: [0, b], corReta: "#111", h: 320,
            xl: k === "local" ? "Δ lavoura na própria AMC (ha, após efeitos fixos)" : "Δ lavoura dos vizinhos ao sul (ha, após efeitos fixos)",
            yl: "Δ pastagem na AMC (ha, após efeitos fixos)", xf: (v) => f(v / 1000, 0) + " mil", yf: (v) => f(v / 1000, 0) + " mil",
          });
          nB.set(f(b, 3)); nO.set(f(k === "local" ? F.beta_local : F.theta, 3)); nN.set(f(F.n, 0));
          txt.innerHTML = k === "local"
            ? "Cada ponto é uma AMC num ano, depois de retirados os efeitos fixos de AMC e de ano e o efeito dos vizinhos (é o teorema de Frisch-Waugh-Lovell: a inclinação desta nuvem é o coeficiente da regressão múltipla). Mostram-se 98% centrais; a reta usa todos os pontos."
            : "A mesma nuvem para o termo dos vizinhos ao sul: se a lavoura do Sul empurrasse o pasto para o Norte, a inclinação seria positiva. Ela é negativa aqui. Com a matriz de oito vizinhos, as 12 especificações do teste dão sinal negativo; com quatro ou doze vizinhos, algumas ficam positivas, e nenhuma estimativa positiva é distinguível de zero (verbete 6.3).";
        }
        des();
      },
    });
  });

  /* ---------------- 3.4 R² ---------------- */
  CX.def("r2", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sR = CX.slider(ctl, { rot: "quanto a nota depende de outras coisas", min: 0, max: 2.5, passo: 0.1, val: 1.5, fmt: (v) => "± " + f(v, 1) + " ponto", aoMudar: () => { tres = false; des(); } });
        CX.btn(ctl, "turma de 3 alunos", () => { tres = true; des(); });
        CX.btn(ctl, "sortear outra turma", () => { sem++; tres = false; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "inclinação estimada (verdadeira = 0,3 ponto por hora)", true), nR = CX.num(lei, "R²");
        const txt = CX.frase(c);
        let tres = false;
        function des() {
          const r = CX.rng(sem), n = tres ? 3 : 90;
          const xs = d3.range(n).map((i) => (tres ? [2, 7, 12][i] : r() * 15)), ys = xs.map((x) => Math.max(0, Math.min(10, 3.5 + 0.3 * x + CX.normal(r) * sR.valor())));
          const fit = S.ols1(xs, ys);
          alvo.replaceChildren();
          dispersao(alvo, xs.map((x, i) => ({ x, y: ys[i], cor: C.azul })), { xdom: [0, 15], ydom: [0, 10], reta: [fit.a, fit.b], h: 260, xl: "horas de estudo por semana", yl: "nota na prova", r: tres ? 7 : 3.5 });
          nB.set(f(fit.b, 2)); nR.set(f(fit.r2, 2));
          txt.innerHTML = tres
            ? `Com três alunos, a reta passa perto de todos e o R² vai a ${f(fit.r2, 2)}. Não é sinal de que o estudo explique a nota: com tão poucos pontos, quase qualquer reta fica perto deles.`
            : `A inclinação estimada fica perto da verdadeira (0,3 ponto por hora), mas o R² é ${f(fit.r2, 2)}: a maior parte da variação das notas vem de outras coisas. Aumente essa variação e veja o R² cair enquanto a inclinação continua no lugar.`;
        }
        let sem = 4;
        des();
      },
      async dados(c) {
        const F = (await CX.base()).fwl;
        let sxy = 0, sxx = 0, syy = 0; F.xl.forEach((v, i) => { sxy += v * F.yl[i]; sxx += v * v; syy += F.yl[i] ** 2; });
        const b = sxy / sxx, r2 = (b * b * sxx) / syy;
        // médias por faixa de x (binscatter): mostra a inclinação que a nuvem esconde
        const ord = F.xl.map((v, i) => [v, F.yl[i]]).sort((a, bb) => a[0] - bb[0]);
        const nb = 25, bins = d3.range(nb).map((k) => { const sl = ord.slice(Math.floor((k * ord.length) / nb), Math.floor(((k + 1) * ord.length) / nb)); return { x: S.media(sl.map((p) => p[0])), y: S.media(sl.map((p) => p[1])) }; });
        const q = dispersao(c, bins.map((p) => ({ x: p.x, y: p.y, cor: C.agric, tip: `média de ${Math.round(ord.length / nb)} pontos` })), { r: 6, reta: [0, b], corReta: "#111", h: 280, xl: "Δ lavoura na AMC (ha, após efeitos fixos) — médias por faixa", yl: "Δ pastagem (ha)", xf: (v) => f(v / 1000, 0) + " mil", yf: (v) => f(v / 1000, 0) + " mil" });
        const lei = CX.leitura(c);
        CX.num(lei, "β (substituição local)", true).set(f(b, 3));
        CX.num(lei, "R² dessa nuvem").set(f(r2, 3));
        CX.frase(c, `A nuvem inteira (verbete 3.3) é tão espalhada que o R² fica em ${f(r2, 3)}. Agrupando os ${f(F.n, 0)} pontos em 25 faixas de x e tirando a média de y em cada uma, a inclinação aparece nítida. β nítido e R² baixo convivem: um diz a direção média, o outro quanto da variação total ela acompanha.`);
        return q;
      },
    });
  });

  /* ---------------- 3.5 Efeitos fixos ---------------- */
  function demoFE(c, unid, rotx, roty) {
    const ctl = CX.ctrl(c);
    let fu = false, ft = false;
    CX.check(ctl, " efeito fixo da unidade (tirar a média de cada uma)", false, (b) => { fu = b; des(); });
    CX.check(ctl, " efeito fixo do ano (tirar a média de cada ano)", false, (b) => { ft = b; des(); });
    const q = CX.quadro(c, { h: 320, m: { l: 56, r: 110, t: 14, b: 38 } });
    const lei = CX.leitura(c);
    const nB = CX.num(lei, "inclinação da reta", true), nQ = CX.num(lei, "o que está sendo comparado");
    const T = unid[0].x.length;
    function transf() {
      let P = unid.map((u) => ({ ...u, xs: [...u.x], ys: [...u.y] }));
      if (fu) P.forEach((u) => { const mx = S.media(u.xs), my = S.media(u.ys); u.xs = u.xs.map((v) => v - mx); u.ys = u.ys.map((v) => v - my); });
      if (ft) for (let t = 0; t < T; t++) { const mx = S.media(P.map((u) => u.xs[t])), my = S.media(P.map((u) => u.ys[t])); P.forEach((u) => { u.xs[t] -= mx; u.ys[t] -= my; }); }
      return P;
    }
    const gP = q.g.append("g"), gL = q.g.append("g");
    function des() {
      const P = transf();
      const all = P.flatMap((u) => u.xs.map((x, t) => ({ x, y: u.ys[t], u })));
      const x = d3.scaleLinear().domain(d3.extent(all, (p) => p.x)).nice().range([0, q.iw]);
      const y = d3.scaleLinear().domain(d3.extent(all, (p) => p.y)).nice().range([q.ih, 0]);
      CX.eixos(q, x, y, { xl: rotx + (fu || ft ? " (desvio)" : ""), yl: roty + (fu || ft ? " (desvio)" : "") });
      const dur = CX.reduz ? 0 : 600;
      gP.selectAll("circle").data(all).join("circle").attr("r", 3.4).attr("fill", (p) => p.u.cor).attr("opacity", 0.75)
        .transition().duration(dur).attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y));
      const fit = S.ols1(all.map((p) => p.x), all.map((p) => p.y));
      const [x0, x1] = x.domain();
      gL.selectAll("*").remove();
      gL.append("line").attr("x1", x(x0)).attr("x2", x(x1)).attr("y1", y(fit.a + fit.b * x0)).attr("y2", y(fit.a + fit.b * x1)).attr("stroke", "#111").attr("stroke-width", 2.4);
      const rots = P.map((u) => { const t = gL.append("text").attr("class", "rot").attr("x", q.iw + 6); t.append("tspan").style("fill", u.cor).text("● "); t.append("tspan").text(u.nome); return { sel: t, y: y(S.media(u.ys)) + 4 }; });
      CX.desempilha(rots, 8, q.ih);
      nB.set(fs(fit.b, 2));
      nQ.set(!fu && !ft ? "unidades entre si" : fu && !ft ? "cada unidade consigo mesma" : !fu && ft ? "anos descontados" : "dentro da unidade, sem o ano");
    }
    des();
  }
  CX.def("fe", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(2);
        const pessoas = [["Ana", C.azul], ["Bruno", C.veg], ["Carla", C.pasto], ["Davi", C.acento]].map(([nome, cor], k) => {
          const x = [], y = [];
          const vel = 30 + 15 * k, erro = 12 - 2.6 * k; // quem é mais rápido é mais experiente e erra menos
          for (let t = 0; t < 10; t++) { const dv = (r() - 0.5) * 16; x.push(vel + dv); y.push(erro + 0.28 * dv + t * 0.12 + CX.normal(r) * 0.6); }
          return { nome, cor, x, y };
        });
        demoFE(c, pessoas, "velocidade (palavras por minuto)", "erros por página");
        CX.frase(c, "Miniatura construída de propósito. Entre as pessoas, a reta desce: os mais rápidos são os mais experientes e erram menos. Com o efeito fixo da pessoa, cada uma é comparada consigo mesma, e a reta sobe: nos dias em que alguém digita mais rápido do que costuma, erra mais. O efeito fixo do dia tira a leve piora de todos com o teclado novo.");
      },
      async dados(c) {
        const R = (await CX.base()).reg;
        const un = ["Sul", "Centro", "Norte"].map((r) => ({ nome: r, cor: C[r], x: R["agric_mha_" + r], y: R["pasto_mha_" + r] }));
        demoFE(c, un, "agricultura (Mha)", "pastagem (Mha)");
        CX.frase(c, "Três regiões, 40 anos cada. Sem efeitos fixos, a reta liga as regiões: o Sul tem mais de tudo, e a inclinação é positiva. Com os dois efeitos fixos, sobra o que acontece dentro de cada região depois de descontado o ano, e a inclinação é negativa: é a substituição local. O painel do trabalho faz isso com 166 AMCs.");
      },
    });
  });

  /* ---------------- 3.6 HAC ---------------- */
  CX.def("hac", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sP = CX.slider(ctl, { rot: "memória da série (φ)", min: 0, max: 0.9, passo: 0.05, val: 0.6, fmt: (v) => f(v, 2) });
        CX.btn(ctl, "rodar 400 simulações", roda, true);
        const q = CX.quadro(c, { h: 220, m: { l: 150, r: 60, t: 18, b: 34 } });
        const txt = CX.frase(c, "Cada simulação gera 38 anos de uma série sem tendência nenhuma, com memória φ, e testa a inclinação a 5%. A taxa de rejeição deveria ser 5%.");
        function roda() {
          const r = CX.rng(Math.floor(Math.random() * 1e6)), n = 38, phi = sP.valor(), t = d3.range(n);
          let ri = 0, rh = 0;
          for (let s = 0; s < 400; s++) {
            let e = CX.normal(r) / Math.sqrt(1 - phi * phi); const y = [];
            for (let k = 0; k < n; k++) { if (k) e = phi * e + CX.normal(r); y.push(e); }
            const fit = S.ols1(t, y), crit = 2.03;
            if (Math.abs(fit.b / fit.se) > crit) ri++;
            if (Math.abs(fit.b / S.seHAC(t, fit, 2)) > crit) rh++;
          }
          const lin = [["erro-padrão comum", ri / 400, C.cinza], ["HAC (defasagem 2)", rh / 400, C.acento]];
          const x = d3.scaleLinear().domain([0, Math.max(0.6, d3.max(lin, (l) => l[1]) * 1.1)]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.35);
          CX.eixos(q, x, null, { xf: (v) => CX.pct(v), xl: "fração de testes que acusam tendência (não há nenhuma)" });
          q.g.selectAll(".b").remove();
          q.g.append("line").attr("class", "b").attr("x1", x(0.05)).attr("x2", x(0.05)).attr("y1", -6).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "4 3");
          q.g.append("text").attr("class", "b rot-m").attr("x", x(0.05) + 4).attr("y", -6).text("5% prometidos");
          lin.forEach(([n2, v, cc]) => {
            q.g.append("rect").attr("class", "b").attr("y", y(n2)).attr("height", y.bandwidth()).attr("width", x(v)).attr("fill", cc).attr("rx", 3);
            q.g.append("text").attr("class", "b rot").attr("x", -8).attr("y", y(n2) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n2);
            q.g.append("text").attr("class", "b rot-f").attr("x", x(v) + 6).attr("y", y(n2) + y.bandwidth() / 2 + 4).text(CX.pct(v));
          });
          txt.innerHTML = `Com φ = ${f(phi, 2)}, o erro-padrão comum acusa tendência em ${CX.pct(ri / 400)} das séries, quando deveria acusar em 5%; o HAC, em ${CX.pct(rh / 400)}. ` + (phi < 0.3 ? "Com pouca memória, os dois ficam perto do prometido." : rh / 400 > 0.08 ? "O HAC reduz o engano, mas com memória forte e só 38 anos não chega aos 5%: ele corrige a medida da incerteza, e não cria a informação que falta." : "O HAC traz a taxa para perto do prometido; o erro-padrão comum continua enganando.");
        }
        roda();
      },
      async dados(c) {
        const g = (await CX.base()).go;
        const ctl = CX.ctrl(c);
        let v = "pasto", jan = "tudo";
        CX.seg(ctl, { opcoes: [["pasto", "pastagem"], ["agric", "agricultura"], ["veg", "vegetação natural"]], val: v, aoMudar: (k) => { v = k; des(); } });
        CX.seg(ctl, { opcoes: [["tudo", "1985–2024"], ["II", "Ato II"], ["III", "Ato III"]], val: jan, aoMudar: (k) => { jan = k; des(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const tab = h("table", { class: "cx-tab" }); c.appendChild(tab);
        function des() {
          const [a, b] = { tudo: [1985, 2024], II: [2001, 2019], III: [2020, 2024] }[jan];
          const idx = g.anos.map((_, i) => i).filter((i) => g.anos[i] >= a && g.anos[i] <= b);
          const t = idx.map((i) => g.anos[i]), y = idx.map((i) => g[v][i]);
          const fit = S.ols1(t, y), seH = S.seHAC(t, fit, 2);
          alvo.replaceChildren();
          const q = dispersao(alvo, t.map((x, i) => ({ x, y: y[i], cor: C[v === "agric" ? "agric" : v === "veg" ? "veg" : "pasto"], tip: String(x) })), { reta: [fit.a, fit.b], h: 240, xl: "ano", yl: "Mha", xf: CX.anoF });
          const ic = (se) => `[${fs(fit.b - 2.03 * se, 3)}; ${fs(fit.b + 2.03 * se, 3)}]`;
          tab.innerHTML = `<tr><th>erro-padrão</th><th>inclinação (Mha/ano)</th><th>erro-padrão</th><th>intervalo ≈95%</th></tr>
            <tr><td>comum (anos independentes)</td><td>${fs(fit.b, 3)}</td><td>${f(fit.se, 4)}</td><td>${ic(fit.se)}</td></tr>
            <tr class="on"><td>HAC, Newey-West (defasagem 2)</td><td>${fs(fit.b, 3)}</td><td>${f(seH, 4)}</td><td>${ic(seH)}</td></tr>`;
          return q;
        }
        des();
        CX.frase(c, "A inclinação é a mesma nas duas linhas; muda só a incerteza. Nas séries de uso da terra, cujos resíduos de anos vizinhos se parecem, o HAC costuma ser mais largo. Com os 5 anos do Ato III, nenhum erro-padrão salva a conta: são poucos pontos.");
      },
    });
  });

  /* ---------------- 3.7 I de Moran ---------------- */
  function moranI(z, viz) {
    const n = z.length, m = S.media(z), d = z.map((v) => v - m);
    let num = 0, den = 0;
    for (let i = 0; i < n; i++) { let lag = 0; viz[i].forEach((j) => { lag += d[j]; }); num += d[i] * (lag / viz[i].length); den += d[i] * d[i]; }
    return num / den;
  }
  function permuta(z, viz, n, r) {
    const out = [], a = [...z];
    for (let k = 0; k < n; k++) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } out.push(moranI(a, viz)); }
    return out;
  }
  function histPerm(pai, perms, obs) {
    const q = CX.quadro(pai, { w: 340, h: 210, m: { l: 30, r: 10, t: 32, b: 38 } });
    const x = d3.scaleLinear().domain([Math.min(d3.min(perms), obs, -0.2) - 0.05, Math.max(d3.max(perms), obs) + 0.05]).range([0, q.iw]);
    const bins = d3.bin().domain(x.domain()).thresholds(30)(perms);
    const y = d3.scaleLinear().domain([0, d3.max(bins, (b) => b.length)]).range([q.ih, 0]);
    CX.eixos(q, x, null, { xl: "I de Moran", xf: (v) => f(v, 1) });
    q.g.selectAll("rect").data(bins).join("rect").attr("x", (b) => x(b.x0)).attr("width", (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr("y", (b) => y(b.length)).attr("height", (b) => q.ih - y(b.length)).attr("fill", C.cinza);
    q.g.append("line").attr("x1", x(obs)).attr("x2", x(obs)).attr("y1", -8).attr("y2", q.ih).attr("stroke", C.acento).attr("stroke-width", 3);
    q.g.append("text").attr("class", "rot-f").attr("x", x(obs)).attr("y", -10).attr("text-anchor", x(obs) > q.iw * 0.75 ? "end" : "middle").text("observado");
    q.g.append("text").attr("class", "rot-m").attr("x", 0).attr("y", -6).text("cinza: I em mapas embaralhados");
  }
  CX.def("moran", (host) => {
    CX.modos(host, {
      simples(c) {
        const N = 14, ctl = CX.ctrl(c);
        let sem = 1;
        const sA = CX.slider(ctl, { rot: "o quanto os bairros se parecem por dentro", min: 0, max: 8, val: 3, fmt: (v) => (v ? v + " rodadas de mistura" : "nada (sal e pimenta)"), aoMudar: des });
        CX.btn(ctl, "sortear", () => { sem++; des(); });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const viz = d3.range(N * N).map((k) => { const i = k % N, j = Math.floor(k / N); return [[1, 0], [-1, 0], [0, 1], [0, -1]].map(([di, dj]) => [i + di, j + dj]).filter(([a, b]) => a >= 0 && b >= 0 && a < N && b < N).map(([a, b]) => b * N + a); });
        const lei = CX.leitura(c);
        const nI = CX.num(lei, "I de Moran", true), nP = CX.num(lei, "p (499 embaralhamentos)");
        function des() {
          const r = CX.rng(sem);
          let z = d3.range(N * N).map(() => CX.normal(r));
          for (let it = 0; it < sA.valor(); it++) z = z.map((v, k) => (v + viz[k].reduce((s, j) => s + z[j], 0)) / (1 + viz[k].length));
          const I = moranI(z, viz), perms = permuta(z, viz, 499, CX.rng(99));
          a1.replaceChildren(); a2.replaceChildren();
          const q = CX.quadro(a1, { w: 300, h: 300, m: { t: 4, r: 4, b: 4, l: 4 } });
          const cs = d3.scaleSequential(d3.interpolateRgb("#f4efe3", "#8b3a1d")).domain(d3.extent(z));
          const cz = 292 / N;
          q.g.selectAll("rect").data(z).join("rect").attr("x", (_, k) => (k % N) * cz).attr("y", (_, k) => Math.floor(k / N) * cz).attr("width", cz - 1).attr("height", cz - 1).attr("fill", (v) => cs(v));
          histPerm(a2, perms, I);
          nI.set(f(I, 2)); nP.set(CX.p((perms.filter((p) => p >= I).length + 1) / 500));
          txtM.innerHTML = sA.valor() === 0
            ? "Preços sorteados sem relação com os vizinhos: o I observado cai no meio dos mapas embaralhados, e o p é grande. É o mapa sal e pimenta."
            : `Quarteirões vizinhos com preços parecidos formam manchas: o I (${f(I, 2)}) fica muito à direita de todos os mapas embaralhados. Tratar cada quarteirão como independente seria contar o mesmo bairro várias vezes.`;
        }
        a1.parentNode.after(h("div", { class: "cx-leg", html: `<span>cor: preço do metro quadrado</span><span><i style="background:#f4efe3;border:1px solid #ddd"></i>mais barato</span><span><i style="background:#8b3a1d"></i>mais caro</span>` }));
        const txtM = CX.frase(c);
        des();
      },
      async dados(c) {
        const [m, b] = await Promise.all([CX.dado("metodo_centro_massa.json"), CX.base()]);
        const aptPor = Object.fromEntries(b.apt.map((a) => [a.code, a.score]));
        const n = m.amc.length;
        const viz = m.amc.map((a, i) => m.amc.map((o, j) => [j, Math.hypot(o.cx - a.cx, o.cy - a.cy)]).filter(([j]) => j !== i).sort((p, q) => p[1] - q[1]).slice(0, 6).map((p) => p[0]));
        const vars = {
          dpasto: ["variação da fração de pastagem, 1985→2024", m.amc.map((a, i) => (m.pesos.pastagem[39][i] - m.pesos.pastagem[0][i]) / (a.area * 100))],
          veg: ["fração de vegetação natural em 2024", m.amc.map((a, i) => m.pesos.veg_natural[39][i] / (a.area * 100))],
          apt: ["aptidão agrícola média (Embrapa)", m.amc.map((a) => aptPor[a.code])],
          sorteio: ["valores sorteados ao acaso (controle)", (() => { const r = CX.rng(3); return m.amc.map(() => r()); })()],
        };
        const ctl = CX.ctrl(c);
        let k = "dpasto";
        CX.seg(ctl, { opcoes: Object.entries(vars).map(([kk, v]) => [kk, v[0].split(",")[0].replace("variação da fração de pastagem", "Δ pastagem")]), val: k, aoMudar: (v) => { k = v; des(); } });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nI = CX.num(lei, "I de Moran (6 vizinhos)", true), nP = CX.num(lei, "p (499 embaralhamentos)");
        const txt = CX.frase(c);
        function des() {
          const [nome, z] = vars[k];
          const I = moranI(z, viz), perms = permuta(z, viz, 499, CX.rng(7));
          a1.replaceChildren(); a2.replaceChildren();
          const q = CX.quadro(a1, { w: 320, h: 340, m: { t: 4, r: 4, b: 4, l: 4 } });
          const mp = CX.mapaAMC(q.g, m, q.iw, q.ih);
          const ext = d3.extent(z), dv = ext[0] < 0 && ext[1] > 0;
          const cs = dv ? d3.scaleDiverging(d3.interpolateRdBu).domain([-Math.max(-ext[0], ext[1]), 0, Math.max(-ext[0], ext[1])]) : d3.scaleSequential(d3.interpolateRgb("#f4efe3", "#8b3a1d")).domain(ext);
          mp.sel.attr("fill", (_, i) => (dv ? cs(-z[i]) : cs(z[i]))).on("mousemove", (ev, a) => CX.tip.mostra(ev, `<b>${a.nome}</b><br>${f(z[m.amc.indexOf(a)], 3)}`)).on("mouseleave", CX.tip.esconde);
          histPerm(a2, perms, I);
          const p = (perms.filter((v) => v >= I).length + 1) / 500;
          nI.set(f(I, 2)); nP.set(CX.p(p));
          txt.innerHTML = `${nome}. ` + (k === "sorteio" ? "Com valores sorteados, o I observado cai no meio dos embaralhados: sem padrão espacial, como deve ser." : "O I observado fica muito à direita de todos os mapas embaralhados: vizinhos se parecem. É por isso que o trabalho reamostra em blocos espaciais (verbete 4.6).");
        }
        des();
      },
    });
  });
})();
