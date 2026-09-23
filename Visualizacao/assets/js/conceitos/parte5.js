/* Caderno de conceitos — Parte 5: réguas de honestidade */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  /* ---------------- 5.1 Bracket e âncora ---------------- */
  CX.def("bracket", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sF = CX.slider(ctl, { rot: "ano em que a regra de atraso muda (5 → 15 min)", min: 2016, max: 2023, val: 2020, fmt: String, aoMudar: des });
        const sQ = CX.slider(ctl, { rot: "atrasos que a regra nova deixa de contar", min: 0, max: 80, passo: 5, val: 60, fmt: (v) => v + "%", aoMudar: des });
        const q = CX.quadro(c, { h: 270, m: { l: 44, r: 190 } });
        const txt = CX.frase(c);
        const anos = d3.range(2015, 2025);
        function des() {
          const verd = anos.map((a, k) => 80 + 3 * k + (k % 3 === 1 ? 2 : k % 3 === 2 ? -1 : 0)); // atrasos de mais de 5 minutos, de verdade
          const A = verd.map((v) => v * 1.0);                                                  // contagem com a regra antiga mantida
          const B = verd.map((v, k) => (anos[k] >= sF.valor() ? v * (1 - sQ.valor() / 100) : v)); // contagem oficial, com a troca de regra
          const cat = verd.map((v, k) => v * 0.97 + (k % 2 ? 1.5 : -1.5));                     // catraca: fonte independente, com o seu próprio ruído
          const x = d3.scaleLinear().domain([2015, 2024]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 120]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "ano", yl: "alunos atrasados por mês", xf: CX.anoF });
          q.g.selectAll(".l").remove();
          q.g.append("path").attr("class", "l").attr("fill", C.acento).attr("opacity", 0.1).attr("d", d3.area().x((_, k) => x(anos[k])).y0((_, k) => y(Math.min(A[k], B[k]))).y1((_, k) => y(Math.max(A[k], B[k])))(anos));
          const rots = [];
          [[A, C.azul, "regra antiga mantida (5 min)"], [B, C.acento, "contagem oficial (regra muda)"], [cat, "#111", "catraca (âncora)", "5 3"]].forEach(([v, cc, n, tr2]) => {
            q.g.append("path").attr("class", "l").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2.2).attr("stroke-dasharray", tr2 || null).attr("d", d3.line().x((_, k) => x(anos[k])).y((d) => y(d))(v));
            const t = q.g.append("text").attr("class", "l rot").attr("x", q.iw + 4).style("fill", cc).text(n);
            rots.push({ sel: t, y: y(v[9]) + 4 });
          });
          CX.desempilha(rots, 8, q.ih, 15);
          const k0 = anos.indexOf(sF.valor()) - 1, dA = A[9] - A[k0], dB = B[9] - B[k0], dC = cat[9] - cat[k0];
          txt.innerHTML = `De ${anos[k0]} a 2024, a regra antiga mantida diz ${fs(dA, 0)} alunos atrasados por mês, a contagem oficial diz ${fs(dB, 0)} e a catraca diz ${fs(dC, 0)}. ` +
            (Math.sign(dA) !== Math.sign(dB) ? "As duas contagens discordam até sobre o sinal: esse \"resultado\" é da regra, e a catraca, que nunca passou por ela, desempata." : "As duas contagens concordam no sinal: essa conclusão não depende da regra, e a catraca confirma.");
        }
        des();
      },
      async dados(c) {
        const b = await CX.base();
        const g = b.go, sd = b.soja_sidra_area;
        const uni = g.agric.map((a, i) => a + g.mosaico[i]);
        const ctl = CX.ctrl(c);
        const sI = CX.slider(ctl, { rot: "janela: de", min: 2014, max: 2023, val: 2019, fmt: String, aoMudar: des });
        const q = CX.quadro(c, { h: 290, m: { l: 44, r: 150, t: 14 } });
        const x = d3.scaleLinear().domain([1985, 2024]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 11]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: CX.anoF, yl: "milhões de hectares" });
        q.g.append("path").attr("fill", C.mosaico).attr("opacity", 0.18).attr("d", d3.area().x((_, i) => x(g.anos[i])).y0((a) => y(a)).y1((_, i) => y(uni[i]))(g.agric));
        const ln = (anos, v, cc, lw, tr, n, dy = 0) => {
          q.g.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", lw).attr("stroke-dasharray", tr || null).attr("d", d3.line().x((_, i) => x(anos[i])).y((d) => y(d))(v));
          q.g.append("text").attr("class", "rot").attr("x", q.iw + 4).attr("y", y(v[v.length - 1]) + 4 + dy).style("fill", cc).text(n);
        };
        ln(g.anos, g.agric, C.agric, 2.2, null, "agricultura (régua crua)");
        ln(g.anos, uni, C.mosaico, 2.2, null, "agricultura ∪ mosaico (teto)");
        ln(sd.anos, sd.mha, "#111", 2.2, "5 3", "soja plantada, IBGE (âncora)");
        const jan = q.g.append("rect").attr("y", 0).attr("height", q.ih).attr("fill", "#111").attr("opacity", 0.05);
        const alvo = h("div"); c.appendChild(alvo);
        function des() {
          const a = sI.valor();
          jan.attr("x", x(a)).attr("width", x(2024) - x(a));
          const cr = (v, anos) => { const i0 = anos.indexOf(a), i1 = anos.indexOf(2024); return v[i1] / v[i0] - 1; };
          alvo.replaceChildren();
          const lin = [["agricultura (crua)", cr(g.agric, g.anos), C.agric], ["agricultura ∪ mosaico", cr(uni, g.anos), C.mosaico], ["soja plantada (IBGE)", cr(sd.mha, sd.anos), "#555"]];
          const qq = CX.quadro(alvo, { h: 150, m: { l: 170, r: 70, t: 20, b: 30 } });
          const xx = d3.scaleLinear().domain([Math.min(0, d3.min(lin, (l) => l[1])) - 0.05, Math.max(0.1, d3.max(lin, (l) => l[1])) + 0.05]).range([0, qq.iw]), yy = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, qq.ih]).padding(0.25);
          CX.eixos(qq, xx, null, { xf: (v) => CX.pct(v) });
          qq.g.append("text").attr("class", "rot-f").attr("y", -8).text(`crescimento de ${a} a 2024`);
          lin.forEach(([n, v, cc]) => {
            qq.g.append("rect").attr("x", xx(Math.min(0, v))).attr("y", yy(n)).attr("width", Math.abs(xx(v) - xx(0))).attr("height", yy.bandwidth()).attr("fill", cc).attr("rx", 3);
            qq.g.append("text").attr("class", "rot").attr("x", -8).attr("y", yy(n) + yy.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
            qq.g.append("text").attr("class", "rot-f").attr("x", xx(Math.max(0, v)) + 5).attr("y", yy(n) + yy.bandwidth() / 2 + 4).text(fs(v * 100, 1) + "%");
          });
        }
        des();
        CX.frase(c, "A faixa ocre é o colchete: entre a agricultura que o classificador rotula e a agricultura somada ao Mosaico. A linha preta vem do IBGE e nunca passou pelo classificador. No fim da série a régua crua quase para, enquanto a soja do IBGE segue subindo: a lavoura nova está caindo no Mosaico.");
      },
    });
  });

  /* ---------------- 5.2 Domínio da variável ---------------- */
  CX.def("dominio", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(9);
        const bons = d3.range(80).map(() => { const t = r() * 20; return { t, min: Math.min(10, Math.max(0, 3.8 + 0.25 * t + CX.normal(r) * 0.9)), fora: false }; });
        const ruins = d3.range(12).map(() => ({ t: -99, min: Math.min(10, Math.max(0, 6.3 + CX.normal(r) * 1.3)), fora: true }));
        const ctl = CX.ctrl(c);
        let inclui = true, z = false;
        CX.check(ctl, " incluir os −99 (\"não informado\")", true, (v) => { inclui = v; des(); });
        CX.check(ctl, " padronizar as horas (z-score)", false, (v) => { z = v; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "inclinação estimada", true), nR = CX.num(lei, "faixa ocupada pelas horas verdadeiras (0 a 20), em z");
        function des() {
          const pts = inclui ? [...bons, ...ruins] : bons;
          const mu = S.media(pts.map((p) => p.t)), sdv = S.dp(pts.map((p) => p.t));
          const tx = (t) => (z ? (t - mu) / sdv : t);
          const fit = S.ols1(pts.map((p) => tx(p.t)), pts.map((p) => p.min));
          alvo.replaceChildren();
          CX.dispersao(alvo, pts.map((p) => ({ x: tx(p.t), y: p.min, cor: p.fora ? "#9b2c2c" : C.azul, tip: p.fora ? "−99: não informado" : `${f(p.t, 1)} horas` })), { reta: [fit.a, fit.b], h: 250, xl: z ? "horas de estudo (z-score)" : "horas de estudo por semana", yl: "nota" });
          nB.set(f(fit.b, 3) + (z ? " ponto por desvio-padrão" : " ponto por hora"));
          const vz = bons.map((p) => (p.t - mu) / sdv);
          nR.set(z ? `${f(d3.min(vz), 2)} a ${f(d3.max(vz), 2)}` : "—");
        }
        des();
        CX.frase(c, "Pontos vermelhos: os −99. Com eles dentro, a inclinação verdadeira (cerca de 0,25 ponto por hora) é achatada por uma nuvem que não pertence à escala. Padronizando, as horas verdadeiras ficam espremidas num canto do eixo, e quem decide a reta são os −99. Tire-os e a inclinação volta.");
      },
      async dados(c) {
        const D = (await CX.base()).deplecao;
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const q = CX.quadro(a1, { w: 340, h: 250, m: { l: 44, r: 10, t: 24, b: 40 } });
        const lab = D.dentro_hist.map((_, i) => f(i * 0.05, 2));
        const x = d3.scaleBand().domain(lab).range([0, q.iw]).padding(0.1), y = d3.scaleLinear().domain([0, d3.max(D.dentro_hist)]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: (v, i) => (i % 5 === 0 ? v : ""), xl: "depleção dentro do domínio (0 a 1)" });
        q.g.append("text").attr("class", "rot-f").attr("y", -10).text(`dentro de 0..1: ${f(D.n - D.fora, 0)} pares`);
        q.g.selectAll("rect").data(D.dentro_hist).join("rect").attr("x", (_, i) => x(lab[i])).attr("width", x.bandwidth()).attr("y", (v) => y(v)).attr("height", (v) => q.ih - y(v)).attr("fill", C.veg);
        const q2 = CX.quadro(a2, { w: 340, h: 250, m: { l: 44, r: 10, t: 24, b: 40 } });
        const bd = D.fora_hist_bordas, lab2 = D.fora_hist.map((_, i) => `${f(bd[i], 1)} a ${f(bd[i + 1], 1)}`);
        const x2 = d3.scaleBand().domain(lab2).range([0, q2.iw]).padding(0.1), y2 = d3.scaleLinear().domain([0, d3.max(D.fora_hist)]).range([q2.ih, 0]);
        CX.eixos(q2, x2, y2, { xf: () => "", xl: `fora do domínio: de ${f(D.min, 1)} a 0` });
        q2.g.append("text").attr("class", "rot-f").attr("y", -10).text(`fora de 0..1: ${f(D.fora, 0)} pares (${CX.pct(D.fora / D.n)})`);
        q2.g.selectAll("rect").data(D.fora_hist).join("rect").attr("x", (_, i) => x2(lab2[i])).attr("width", x2.bandwidth()).attr("y", (v) => y2(v)).attr("height", (v) => q2.ih - y2(v)).attr("fill", "#9b2c2c")
          .on("mousemove", (ev, v) => CX.tip.mostra(ev, `${lab2[D.fora_hist.indexOf(v)]}: ${v} pares`)).on("mouseleave", CX.tip.esconde);
        const lei = CX.leitura(c);
        CX.num(lei, "desvio-padrão com os valores fora do domínio", true).set(f(D.dp, 2));
        CX.num(lei, "faixa 0..1 inteira, medida em z").set(f(1 / D.dp, 2) + " dp");
        CX.num(lei, "menor valor no arquivo").set(f(D.min, 1));
        CX.frase(c, `Uma fração deveria ocupar de 0 a 1. Com ${CX.pct(D.fora / D.n)} dos pares fora disso, o desvio-padrão da coluna vai a ${f(D.dp, 2)}, e depois do z-score todo o domínio legítimo cabe em ${f(1 / D.dp, 2)} desvio-padrão: a regressão passa a ser decidida pelos valores negativos. Eles vêm de AMCs com estoque minúsculo em 1985 que depois "cresceu" pela oscilação pasto ↔ savana (verbete 5.6).`);
      },
    });
  });

  /* ---------------- 5.3 Horse race ---------------- */
  CX.def("horse", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(6);
        const rua = d3.range(70).map(() => { const d = r(); return { d, ipe: Math.max(0, 12 - 9 * d + CX.normal(r) * 1.6), preco: 9000 - 5000 * d + CX.normal(r) * 600 }; });
        const ctl = CX.ctrl(c);
        let fix = false;
        CX.check(ctl, " controlar pela distância ao centro (usar só o que sobra depois dela)", false, (v) => { fix = v; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nB = CX.num(lei, "inclinação preço × ipês (R$ por ipê)", true);
        const txt = CX.frase(c);
        const res = (v) => S.ols1(rua.map((k) => k.d), v).res;
        function des() {
          const xs = fix ? res(rua.map((k) => k.ipe)) : rua.map((k) => k.ipe), ys = fix ? res(rua.map((k) => k.preco)) : rua.map((k) => k.preco);
          const fit = S.ols1(xs, ys);
          const cs = d3.scaleSequential(d3.interpolateRgb("#8b3a1d", "#c9c3b3")).domain([0, 1]);
          alvo.replaceChildren();
          CX.dispersao(alvo, xs.map((x, i) => ({ x, y: ys[i], cor: cs(rua[i].d), tip: `a ${f(rua[i].d * 10, 1)} km do centro` })), { reta: [fit.a, fit.b], h: 250, xl: fix ? "ipês além do esperado pela distância" : "ipês no quarteirão", yl: fix ? "preço além do esperado (R$/m²)" : "preço do m² (R$)", yf: (v) => f(v, 0) });
          nB.set(f(fit.b, 0));
          txt.innerHTML = fix
            ? `Comparando só ruas à mesma distância do centro, os ipês a mais quase não vêm com preço a mais (${f(fit.b, 0)} R$ por ipê). O ipê estava acompanhando o centro.`
            : `Sem controle, cada ipê a mais no quarteirão vem com ${f(fit.b, 0)} reais a mais por metro quadrado. A cor mostra a distância ao centro: ruas centrais (terracota) têm mais ipês e são mais caras.`;
        }
        des();
      },
      async dados(c) {
        const b = await CX.base();
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        CX.dispersao(a1, b.apt.map((a) => ({ x: a.lat, y: a.score, cor: C[a.reg], tip: `AMC ${a.code} (${a.reg})<br>lat ${f(a.lat, 2)} · aptidão ${f(a.score, 2)}` })), { w: 340, h: 280, xl: "latitude (graus; à direita, mais ao norte)", yl: "aptidão agrícola média (Embrapa)", xf: (v) => f(v, 0) });
        a1.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.Sul}"></i>Sul</span><span><i style="background:${C.Centro}"></i>Centro</span><span><i style="background:${C.Norte}"></i>Norte</span> · r = ${f(S.corr(b.apt.map((a) => a.lat), b.apt.map((a) => a.score)), 2)} (escore) · ${f(S.corr(b.apt.map((a) => a.lat), b.apt.map((a) => a.expo)), 2)} (exposição padronizada)` }));
        const H = b.horse;
        const lin = [["S1 aptidão sozinha", H.find((k) => k.spec === "S1")], ["S4 aptidão (com latitude)", H.find((k) => k.spec === "S4" && k.exposicao === "exp_apt_edafo")], ["S2 latitude sozinha", H.find((k) => k.spec === "S2")], ["S4 latitude (com aptidão)", H.find((k) => k.spec === "S4" && k.exposicao === "exp_latitude")]];
        const q = CX.quadro(a2, { w: 340, h: 280, m: { l: 150, r: 20, t: 24, b: 36 } });
        const x = d3.scaleLinear().domain([-0.07, 0.09]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.35);
        CX.eixos(q, x, null, { xf: (v) => f(v, 2), xl: "coeficiente ± 2 erros-padrão", xt: 5 });
        q.g.append("text").attr("class", "rot-f").attr("y", -10).text("#56: a corrida");
        q.g.append("line").attr("class", "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", q.ih);
        lin.forEach(([n, k]) => {
          const yy = y(n) + y.bandwidth() / 2, cc = k.exposicao === "exp_latitude" ? C.azul : C.acento;
          q.g.append("line").attr("x1", x(k.beta - 2 * k.se)).attr("x2", x(k.beta + 2 * k.se)).attr("y1", yy).attr("y2", yy).attr("stroke", cc).attr("stroke-width", 2);
          q.g.append("circle").attr("cx", x(k.beta)).attr("cy", yy).attr("r", 6).attr("fill", cc)
            .on("mousemove", (ev) => CX.tip.mostra(ev, `${n}<br>β = ${f(k.beta, 4)}<br>p agrupado = ${f(k.p_agrupado, 3)}<br>p por rotação = ${f(k.p_circular, 3)}`)).on("mouseleave", CX.tip.esconde);
          q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", yy + 4).attr("text-anchor", "end").text(n);
        });
        const s1 = lin[0][1], s4 = lin[1][1];
        CX.frase(c, `Com a latitude na mesma conta, o coeficiente da aptidão vai de ${f(s1.beta, 3)} para ${f(s4.beta, 3)} (perda de ${CX.pct(1 - s4.beta / s1.beta)}), e o p por rotação de ${f(s1.p_circular, 2)} para ${f(s4.p_circular, 2)}. O da latitude quase não se move. As barras mostram ±2 erros-padrão agrupados, que o verbete 4.7 mostra serem otimistas para este desenho.`);
      },
    });
  });

  /* ---------------- 5.4 MAUP ---------------- */
  CX.def("maup", (host) => {
    CX.modos(host, {
      simples(c) {
        const r = CX.rng(14);
        // duas variáveis com uma componente regional comum e muito ruído local
        const reg = (x, y) => Math.sin(x / 40) + Math.cos(y / 55);
        const pts = d3.range(1600).map(() => { const x = r() * 400, y = r() * 400, g = reg(x, y); return { x, y, a: g + CX.normal(r) * 1.6, b: g + CX.normal(r) * 1.6 }; });
        const ctl = CX.ctrl(c);
        const sC = CX.slider(ctl, { rot: "tamanho do agrupamento", min: 10, max: 200, passo: 10, val: 10, fmt: (v) => (v <= 10 ? "quase uma pessoa por grupo" : `grupos de ~${Math.round((v * v) / 100)} pessoas`), aoMudar: des });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "correlação entre estudo e renda nos grupos", true), nN = CX.num(lei, "grupos");
        function des() {
          const cs = sC.valor(), cel = new Map();
          pts.forEach((p) => { const k = Math.floor(p.x / cs) + "," + Math.floor(p.y / cs); if (!cel.has(k)) cel.set(k, []); cel.get(k).push(p); });
          const agg = [...cel.entries()].map(([k, ps]) => { const [i, j] = k.split(",").map(Number); return { i, j, a: S.media(ps.map((p) => p.a)), b: S.media(ps.map((p) => p.b)), n: ps.length }; });
          a1.replaceChildren(); a2.replaceChildren();
          const q = CX.quadro(a1, { w: 320, h: 320, m: { t: 4, r: 4, b: 4, l: 4 } });
          const k = 312 / 400, col = d3.scaleSequential(d3.interpolateRgb("#f4efe3", "#8b3a1d")).domain(d3.extent(agg, (a) => a.a));
          q.g.selectAll("rect").data(agg).join("rect").attr("x", (a) => a.i * cs * k).attr("y", (a) => a.j * cs * k).attr("width", Math.min(cs, 400 - 0) * k - 1).attr("height", cs * k - 1).attr("fill", (a) => col(a.a));
          CX.dispersao(a2, agg.map((a) => ({ x: a.a, y: a.b, cor: C.azul })), { w: 320, h: 320, xl: "estudo médio do grupo (padronizado)", yl: "renda média do grupo (padronizada)", r: Math.max(2, Math.min(6, cs / 20)) });
          nR.set(f(S.corr(agg.map((a) => a.a), agg.map((a) => a.b)), 2)); nN.set(String(agg.length));
        }
        des();
        CX.frase(c, "As 1.600 pessoas são sempre as mesmas; o mapa à esquerda pinta o estudo médio de cada grupo. Aumentando os grupos, as diferenças individuais se cancelam dentro de cada um e a correlação sobe: a medida mudou por causa da malha, e não das pessoas.");
      },
      dados(c) {
        const lin = [["pastagem · 166 AMCs", 77.6, C.pasto], ["pastagem · pixel a pixel", 79.2, "#8a6d1c"], ["agricultura · 166 AMCs", 65.2, C.agric], ["agricultura · pixel a pixel", 66.9, "#a83c78"]];
        const q = CX.quadro(c, { h: 220, m: { l: 190, r: 70, t: 10, b: 34 } });
        const x = d3.scaleLinear().domain([0, 90]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.3);
        CX.eixos(q, x, null, { xl: "centro de gravidade: km mais ao norte em 2024 que em 1985" });
        lin.forEach(([n, v, cc]) => {
          q.g.append("rect").attr("y", y(n)).attr("height", y.bandwidth()).attr("width", x(v)).attr("fill", cc).attr("rx", 3);
          q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
          q.g.append("text").attr("class", "rot-f").attr("x", x(v) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text("+" + f(v, 1) + " km");
        });
        CX.frase(c, "A malha das AMCs (#32) e o pixel de 30 m sem malha nenhuma (#43) dão a mesma resposta com 1 a 2 km de diferença. Para esta manchete, o achado é da terra.");
      },
    });
  });

  /* ---------------- 5.5 Instrumento × placebo ---------------- */
  CX.def("iv", (host) => {
    const cand = {
      loteria: { nome: "sorteio dos apartamentos", setas: { ZX: true, ZY: false, YZ: false, UZ: false }, tempo: true, txt: "O sorteio muda onde a família mora (relevância), só chega à saúde pelo endereço (exclusão), não depende da saúde nem do cuidado de cada família (exogeneidade) e acontece em rodadas diferentes. É um instrumento." },
      notas: { nome: "fila por ordem de inscrição", setas: { ZX: true, ZY: false, YZ: false, UZ: true }, tempo: true, txt: "A fila também muda o endereço, mas quem se inscreve primeiro tende a ser mais informado e cuidadoso, o mesmo traço que melhora a saúde (o confundidor). Falha a exogeneidade." },
      malha: { nome: "malha fundiária (LAPIG, 2026)", setas: { ZX: true, ZY: false, YZ: true, UZ: true }, tempo: false, txt: "Um só retrato, de 2026: não varia no tempo e sai da conta com o efeito fixo. A proteção responde à própria conversão (seta do desfecho para o candidato) e é posterior a ela. Falha exogeneidade e variação; serve como placebo." },
    };
    const ctl = CX.ctrl(host);
    let k = "malha";
    CX.seg(ctl, { opcoes: Object.entries(cand).map(([kk, v]) => [kk, v.nome]), val: k, aoMudar: (v) => { k = v; des(); } });
    const q = CX.quadro(host, { w: 680, h: 260, m: { t: 10, r: 10, b: 10, l: 10 } });
    const N = { Z: [112, 130, "candidato a instrumento (Z)"], X: [300, 130, "tratamento (X)"], Y: [530, 130, "desfecho (Y)"], U: [415, 30, "confundidor não observado (U)"] };
    const defs = q.svg.append("defs");
    ["#111", "#9b2c2c", "#bbb"].forEach((cc, i) => defs.append("marker").attr("id", "cx-iv" + i).attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7).attr("orient", "auto").append("path").attr("d", "M0,0L10,5L0,10z").attr("fill", cc));
    const gA = q.g.append("g");
    Object.entries(N).forEach(([key, [x, y, n]]) => {
      const lw = key === "U" || key === "Z" ? 100 : 70;
      q.g.append("rect").attr("x", x - lw).attr("y", y - 20).attr("width", 2 * lw).attr("height", 40).attr("rx", 20).attr("fill", key === "U" ? "#f3f1ea" : "#fff").attr("stroke", key === "Z" ? C.acento : "#777").attr("stroke-dasharray", key === "U" ? "4 3" : null).attr("stroke-width", key === "Z" ? 2.5 : 1.2);
      q.g.append("text").attr("class", "rot").attr("x", x).attr("y", y + 4).attr("text-anchor", "middle").style("font-size", "11px").text(n);
    });
    const tab = h("table", { class: "cx-tab" }); host.appendChild(tab);
    const txt = CX.frase(host);
    function seta(a, b, cc, i, curva) {
      const [x1, y1] = N[a], [x2, y2] = N[b];
      const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
      const la = a === "U" || a === "Z" ? 102 : 72, lb = b === "U" || b === "Z" ? 102 : 72;
      const sx = x1 + ux * la, sy = y1 + uy * 22, ex = x2 - ux * lb, ey = y2 - uy * 22;
      const d = curva ? `M${sx},${sy + 18}Q${(sx + ex) / 2},${sy + curva} ${ex},${ey + 18}` : `M${sx},${sy}L${ex},${ey}`;
      gA.append("path").attr("d", d).attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2).attr("marker-end", `url(#cx-iv${i})`);
    }
    function des() {
      const c = cand[k];
      gA.selectAll("*").remove();
      seta("X", "Y", "#111", 0); seta("U", "X", "#bbb", 2); seta("U", "Y", "#bbb", 2);
      if (c.setas.ZX) seta("Z", "X", "#111", 0);
      if (c.setas.UZ) seta("U", "Z", "#9b2c2c", 1);
      if (c.setas.YZ) seta("Y", "Z", "#9b2c2c", 1, 110);
      const cond = [["relevância (Z move X)", c.setas.ZX], ["exclusão (Z só chega a Y por X)", !c.setas.ZY], ["exogeneidade (nem U nem Y movem Z)", !c.setas.UZ && !c.setas.YZ], ["varia no tempo (sobrevive ao efeito fixo)", c.tempo]];
      tab.innerHTML = "<tr><th>condição</th><th>atende?</th></tr>" + cond.map(([n, ok]) => `<tr><td>${n}</td><td style="color:${ok ? C.veg : "#9b2c2c"};font-weight:700">${ok ? "sim" : "não"}</td></tr>`).join("");
      txt.innerHTML = c.txt;
    }
    des();
    CX.frase(host, "Em Goiás a malha mostra 90,6% do território como propriedade privada e só 1,7% sob proteção integral ou terra indígena. Do estoque convertível que resta, 97% (6,35 de 6,56 Mha) está fora da proteção integral.");
  });

  /* ---------------- 5.6 Oscilação do classificador ---------------- */
  CX.def("osc", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sV = CX.slider(ctl, { rot: "conversão verdadeira savana → pasto (% ao ano)", min: 0, max: 5, passo: 0.25, val: 1, fmt: (v) => f(v, 2) + "%", aoMudar: des });
        const sR = CX.slider(ctl, { rot: "pixels de borda que o classificador troca por ano", min: 0, max: 10, passo: 0.5, val: 4, fmt: (v) => f(v, 1) + "%", aoMudar: des });
        const N = 30, q = CX.quadro(c, { w: 680, h: 250, m: { t: 6, r: 6, b: 6, l: 6 } });
        const lei = CX.leitura(c);
        const nI = CX.num(lei, "savana → pasto (bruto)"), nV = CX.num(lei, "pasto → savana (bruto)"), nR = CX.num(lei, "razão ida / volta", true);
        function des() {
          const r = CX.rng(17), verd = [], vis0 = [], vis1 = [];
          for (let k = 0; k < N * N; k++) { const i = k % N; verd.push(i < 15 ? "sav" : "pasto"); }
          // conversão verdadeira num ano
          const v1 = verd.map((v) => (v === "sav" && r() < sV.valor() / 100 * 6 ? "pasto" : v));
          // o classificador troca pixels de borda (colunas 12 a 19) nos dois anos, independentemente
          const juiz = (arr) => arr.map((v, k) => { const i = k % N; return i >= 11 && i <= 18 && r() < sR.valor() / 100 * 3.75 ? (v === "sav" ? "pasto" : "sav") : v; });
          const a0 = juiz(verd), a1 = juiz(v1);
          let ida = 0, volta = 0; a0.forEach((v, k) => { if (v === "sav" && a1[k] === "pasto") ida++; if (v === "pasto" && a1[k] === "sav") volta++; });
          q.g.selectAll("*").remove();
          const cz = 10.5;
          [[a0, 0, "ano 1 (como o classificador viu)"], [a1, 340, "ano 2 (como o classificador viu)"]].forEach(([arr, ox, tit]) => {
            q.g.append("text").attr("class", "rot-m").attr("x", ox).attr("y", 10).text(tit);
            q.g.selectAll(null).data(arr).join("rect").attr("x", (_, k) => ox + (k % N) * cz).attr("y", (_, k) => 16 + Math.floor(k / N) * (cz * 0.72)).attr("width", cz - 1).attr("height", cz * 0.72 - 1).attr("fill", (v) => (v === "sav" ? C.veg : C.pasto));
          });
          nI.set(String(ida)); nV.set(String(volta)); nR.set(volta ? f(ida / volta, 2) + "×" : "∞");
        }
        des();
        c.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg}"></i>savana</span><span><i style="background:${C.pasto}"></i>pastagem</span>` }));
        CX.frase(c, "Com o classificador firme (zero troca na borda), só há ida, e a razão é infinita. Com muita hesitação e pouca conversão verdadeira, os fluxos nos dois sentidos ficam parecidos e a razão cai para perto de 1: é a assinatura do classificador balançando, como o aplicativo que troca cachorro por lobo, e não de vegetação voltando.");
      },
      async dados(c) {
        const O = (await CX.base()).oscilacao;
        const ordem = [[1985, 1995], [1995, 2005], [2005, 2015], [2015, 2024], [1985, 2024], [1995, 1996], [2005, 2006], [2015, 2016], [2023, 2024]];
        const lin = ordem.map(([a, b]) => O.find((o) => o.ini === a && o.fim === b)).filter(Boolean);
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        const rot = (o) => `${o.ini}–${String(o.fim).slice(2)}`;
        const q = CX.quadro(a1, { w: 340, h: 300, m: { l: 70, r: 40, t: 24, b: 34 } });
        const x = d3.scaleLinear().domain([0, 10]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map(rot)).range([0, q.ih]).padding(0.25);
        CX.eixos(q, x, y, { xl: "savana→pasto ÷ pasto→savana", grade: false });
        q.g.append("text").attr("class", "rot-f").attr("y", -10).text("razão entre os dois sentidos");
        q.g.append("line").attr("x1", x(1)).attr("x2", x(1)).attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "3 3");
        lin.forEach((o) => {
          const v = o.sav_pasto / o.pasto_sav;
          q.g.append("rect").attr("y", y(rot(o))).attr("height", y.bandwidth()).attr("width", x(v)).attr("fill", o.fim - o.ini === 1 ? C.acento : C.azul).attr("rx", 3)
            .on("mousemove", (ev) => CX.tip.mostra(ev, `${rot(o)}<br>savana→pasto: ${f(o.sav_pasto, 0)} ha<br>pasto→savana: ${f(o.pasto_sav, 0)} ha`)).on("mouseleave", CX.tip.esconde);
          q.g.append("text").attr("class", "rot-f").attr("x", x(v) + 4).attr("y", y(rot(o)) + y.bandwidth() / 2 + 4).text(f(v, 2) + "×");
        });
        const q2 = CX.quadro(a2, { w: 340, h: 300, m: { l: 70, r: 40, t: 24, b: 34 } });
        const x2 = d3.scaleLinear().domain([0, 1]).range([0, q2.iw]);
        CX.eixos(q2, x2, y, { xf: (v) => CX.pct(v), xl: "composição do fluxo pasto → natural", grade: false });
        q2.g.append("text").attr("class", "rot-f").attr("y", -10).text("para onde vai o reverso");
        lin.forEach((o) => {
          const tot = o.pasto_sav + o.pasto_flo + o.pasto_campo, fs2 = o.pasto_sav / tot, ff = o.pasto_flo / tot;
          q2.g.append("rect").attr("y", y(rot(o))).attr("height", y.bandwidth()).attr("width", x2(fs2)).attr("fill", C.veg).attr("opacity", 0.55);
          q2.g.append("rect").attr("x", x2(fs2)).attr("y", y(rot(o))).attr("height", y.bandwidth()).attr("width", x2(ff)).attr("fill", "#24543a");
          q2.g.append("text").attr("class", "rot").attr("x", q2.iw + 4).attr("y", y(rot(o)) + y.bandwidth() / 2 + 4).text(CX.pct(ff));
        });
        a2.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.veg};opacity:.55"></i>savana</span><span><i style="background:#24543a"></i>floresta (número à direita)</span><span>campo: ≈ 0%</span>` }));
        CX.frase(c, "À esquerda: nas janelas de um ano (terracota), os dois sentidos quase se equilibram; em 1985–95 a ida era 8,4 vezes a volta. À direita: o reverso é quase todo savana, e só no par longo 1985–2024 a floresta chega a 38%, o componente compatível com regeneração real, lenta e de mão única.");
      },
    });
  });
})();
