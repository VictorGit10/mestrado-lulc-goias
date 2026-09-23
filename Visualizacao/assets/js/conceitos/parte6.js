/* Caderno de conceitos — Parte 6: literatura */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  function indice(v) { const b = v.find((x) => x != null); return v.map((x) => (x == null ? null : (100 * x) / b)); }

  /* ---------------- 6.1 Renda da terra: perfil de renda e mapa visto de cima ---------------- */
  CX.def("renda", (host) => {
    CX.modos(host, {
      simples(c) {
        const P = { pL: 10, tL: 6, pG: 5, tG: 1.5, ric: false };
        const ctl = CX.ctrl(c), ctl2 = CX.ctrl(c);
        CX.slider(ctl, { rot: "preço da lavoura", min: 5, max: 16, passo: 0.5, val: P.pL, fmt: (v) => f(v, 1), aoMudar: (v) => { P.pL = v; atualiza(); } });
        CX.slider(ctl, { rot: "frete da lavoura (por 100 km)", min: 2, max: 10, passo: 0.5, val: P.tL, fmt: (v) => f(v, 1), aoMudar: (v) => { P.tL = v; atualiza(); } });
        CX.slider(ctl2, { rot: "preço do boi", min: 2, max: 9, passo: 0.5, val: P.pG, fmt: (v) => f(v, 1), aoMudar: (v) => { P.pG = v; atualiza(); } });
        CX.slider(ctl2, { rot: "frete do boi (por 100 km)", min: 0.5, max: 4, passo: 0.25, val: P.tG, fmt: (v) => f(v, 2), aoMudar: (v) => { P.tG = v; atualiza(); } });
        const ctl3 = CX.ctrl(c);
        CX.check(ctl3, " a qualidade da terra piora rumo ao norte (Ricardo)", false, (v) => { P.ric = v; atualiza(); });
        // renda por hectare a d km do mercado; yn = 0 no sul (mercado), 1 no norte
        const qual = (yn) => (P.ric ? 1.25 - 0.5 * yn : 1);
        const RL = (d, yn) => P.pL * qual(yn) - 2 - (P.tL * d) / 100;
        const RG = (d, yn) => P.pG * Math.pow(qual(yn), 0.4) - 1 - (P.tG * d) / 100;
        const vence = (d, yn) => { const rl = RL(d, yn), rg = RG(d, yn); return rl > rg && rl > 0 ? "agric" : rg > 0 ? "pasto" : "veg"; };
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const a1 = h("div"), a2 = h("div"); grid.append(a1, a2);
        // perfil: renda de cada uso ao longo do eixo sul → norte
        const qq = CX.quadro(a1, { w: 340, h: 280, m: { l: 44, r: 16, t: 24, b: 40 } });
        const ds = d3.range(0, 501, 5), x = d3.scaleLinear().domain([0, 500]).range([0, qq.iw]), y = d3.scaleLinear().domain([0, 14]).range([qq.ih, 0]);
        CX.eixos(qq, x, y, { xl: "distância do mercado, rumo ao norte (km)", yl: "quanto cada uso pode pagar por hectare", xt: 5 });
        const gPerf = qq.g.append("g");
        // mapa visto de cima: o mercado no meio da borda sul
        const qm = CX.quadro(a2, { w: 340, h: 280, m: { t: 24, r: 6, b: 6, l: 6 } });
        const NX = 56, NY = 28, cw = qm.iw / NX, chh = (qm.ih - 18) / NY;
        const celas = [];
        for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) celas.push({ i, j, xk: -500 + ((i + 0.5) * 1000) / NX, yk: ((NY - j - 0.5) * 500) / NY });
        const gM = qm.g.append("g");
        const rc = gM.selectAll("rect").data(celas).join("rect").attr("x", (d) => d.i * cw).attr("y", (d) => d.j * chh).attr("width", cw + 0.3).attr("height", chh + 0.3);
        qm.g.append("path").attr("d", `M${qm.iw / 2},${NY * chh - 12}l-8,12h16z`).attr("fill", "#111");
        qm.g.append("text").attr("class", "rot-f").attr("x", qm.iw / 2).attr("y", NY * chh + 14).attr("text-anchor", "middle").text("mercado");
        qm.g.append("text").attr("class", "rot-m").attr("x", qm.iw).attr("y", -8).attr("text-anchor", "end").text("norte ↑");
        qm.g.append("text").attr("class", "rot-m").attr("y", -8).text("visto de cima: quem vence em cada ponto");
        a2.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.agric}"></i>lavoura</span><span><i style="background:${C.pasto}"></i>gado</span><span><i style="background:${C.veg}"></i>vegetação (nenhum uso compensa)</span>` }));
        const lei = CX.leitura(c);
        const nL = CX.num(lei, "o anel da lavoura vai até"), nG = CX.num(lei, "o anel do gado vai até"), nV = CX.num(lei, "vão entre os centros dos anéis", true);
        const txt = CX.frase(c);
        function atualiza() {
          rc.attr("fill", (d) => C[vence(Math.hypot(d.xk, d.yk), d.yk / 500)]);
          gPerf.selectAll("*").remove();
          let fimL = 0, fimG = 0;
          ds.forEach((d) => { const k = vence(d, d / 500); if (k === "agric") fimL = d; if (k === "pasto") fimG = d; });
          [[0, fimL, C.agric], [fimL, fimG, C.pasto], [Math.max(fimL, fimG), 500, C.veg]].forEach(([a, b, cor]) => { if (b > a) gPerf.append("rect").attr("x", x(a)).attr("width", x(b) - x(a)).attr("y", qq.ih + 1).attr("height", 5).attr("fill", cor); });
          [[RL, C.agric, "lavoura"], [RG, "#9c7a1d", "gado"]].forEach(([fn, cor, n]) => {
            gPerf.append("path").attr("fill", "none").attr("stroke", cor).attr("stroke-width", 2.4).attr("d", d3.line().defined((d) => fn(d, d / 500) > 0).x((d) => x(d)).y((d) => y(Math.min(14, fn(d, d / 500))))(ds));
            const d0 = 20;
            gPerf.append("text").attr("class", "rot").attr("x", x(d0) + 4).attr("y", y(Math.min(13.5, fn(d0, d0 / 500))) - 6).style("fill", cor).text(n);
          });
          nL.set(fimL ? fimL + " km" : "—"); nG.set(fimG > fimL ? fimG + " km" : "—"); nV.set(fimG > fimL ? f(fimG / 2, 0) + " km" : "—");
          txt.innerHTML = "Cada linha mostra quanto um uso pode pagar por hectare a cada distância do mercado: a da lavoura começa alta e cai depressa (produto valioso, frete caro); a do gado começa baixa e cai devagar. Em cada ponto fica o uso que pode pagar mais; onde nenhum paga nada, fica a vegetação. Suba o preço da lavoura: o anel dela se alarga e o do gado se desloca para longe, sem que ninguém empurre ninguém." +
            (P.ric ? " Com a qualidade piorando rumo ao norte, os anéis deixam de ser círculos: encolhem para o norte e se esticam para os lados, e a ordenação passa a depender também da terra, e não só da distância." : "");
        }
        atualiza();
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
        <tr><td>termo de vizinhança, 12 recortes com 8 vizinhos</td><td>12 negativos; 1 com p &lt; 0,05, no sentido oposto</td></tr>
        <tr><td>com 4 e 12 vizinhos</td><td>alguns positivos no rebanho, nenhum distinguível de zero</td></tr>
        <tr><td>estimativas positivas e significativas</td><td>0 de 36</td></tr>
        <tr><td>substituição local (dentro da AMC)</td><td>β ≈ −0,51</td></tr></table>`;
    }
    des();
  });

  /* ---------------- 6.4 Câmbio ---------------- */
  CX.def("cambio", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sP = CX.slider(ctl, { rot: "preço da rede lá fora (US$)", min: 10, max: 50, val: 30, fmt: (v) => "US$ " + v, aoMudar: des });
        const sC = CX.slider(ctl, { rot: "câmbio (R$ por US$)", min: 2, max: 6, passo: 0.1, val: 4, fmt: (v) => "R$ " + f(v, 2), aoMudar: des });
        const sK = CX.slider(ctl, { rot: "custo de cada rede (R$)", min: 40, max: 160, val: 100, fmt: (v) => "R$ " + v, aoMudar: des });
        const alvo = h("div"); c.appendChild(alvo);
        const lei = CX.leitura(c);
        const nR = CX.num(lei, "o artesão recebe (R$)"), nM = CX.num(lei, "margem por rede", true);
        function des() {
          const rec = sP.valor() * sC.valor(), mg = rec - sK.valor();
          alvo.replaceChildren();
          const q = CX.quadro(alvo, { h: 150, m: { l: 150, r: 70, t: 10, b: 30 } });
          const x = d3.scaleLinear().domain([Math.min(0, mg) - 5, 300]).range([0, q.iw]), y = d3.scaleBand().domain(["recebido", "custo", "margem"]).range([0, q.ih]).padding(0.25);
          CX.eixos(q, x, null, { xf: (v) => "R$ " + v });
          [["recebido", rec, C.azul], ["custo", sK.valor(), C.cinza], ["margem", mg, mg >= 0 ? C.veg : "#9b2c2c"]].forEach(([n, v, cc]) => {
            q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(n)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", cc).attr("rx", 3);
            q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
            q.g.append("text").attr("class", "rot-f").attr("x", x(Math.max(0, v)) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text("R$ " + f(v, 0));
          });
          nR.set("R$ " + f(rec, 2)); nM.set("R$ " + f(mg, 2));
        }
        des();
        CX.frase(c, "Suba o câmbio sem mexer no preço em dólar: a margem cresce, e produzir mais passa a compensar. Na soja, a conta é a mesma, e terra que não compensava plantar passa a compensar. É o mecanismo de Richards (2012) para a expansão da soja depois das desvalorizações do fim dos anos 1990.");
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
