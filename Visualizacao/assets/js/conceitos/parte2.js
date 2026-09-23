/* Caderno de conceitos — Parte 2: descrever */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  /* ---------------- 2.1 Centro de massa ---------------- */
  CX.def("cm", (host) => {
    CX.modos(host, {
      simples(c) {
        const grupos = [{ nome: "na frente", fil: 2, n: 10, cor: C.azul }, { nome: "no meio", fil: 5, n: 0, cor: C.pasto }, { nome: "no fundo", fil: 8, n: 10, cor: C.acento }];
        const ctl = CX.ctrl(c);
        const sl = grupos.map((g) => CX.slider(ctl, { rot: `passageiros ${g.nome} (fileira ${g.fil})`, min: 0, max: 30, val: g.n, fmt: String, aoMudar: (v) => { g.n = v; des(); } }));
        const ctl2 = CX.ctrl(c);
        const poe = (a, b, cc) => { [a, b, cc].forEach((v, i) => { grupos[i].n = v; sl[i].set(v, true); }); des(); };
        CX.btn(ctl2, "situação inicial: 10 na frente, 10 no fundo", () => poe(10, 0, 10));
        CX.btn(ctl2, "entram mais 10 pelo fundo", () => poe(grupos[0].n, grupos[1].n, Math.min(30, grupos[2].n + 10)));
        const q = CX.quadro(c, { h: 250, m: { l: 20, r: 20, t: 12, b: 40 } });
        const x = d3.scaleLinear().domain([0.5, 10.5]).range([0, q.iw]);
        const yB = 150; // linha do assoalho
        // o ônibus: carroceria, bancos e a porta
        q.g.append("rect").attr("x", x(0.5) - 6).attr("y", 8).attr("width", x(10.5) - x(0.5) + 12).attr("height", yB - 2).attr("rx", 16).attr("fill", "#f7f5ef").attr("stroke", "#bbb");
        d3.range(1, 11).forEach((k) => {
          q.g.append("rect").attr("x", x(k) - 14).attr("y", yB - 18).attr("width", 28).attr("height", 12).attr("rx", 3).attr("fill", "#e4dfd2");
          q.g.append("text").attr("class", "rot-m").attr("x", x(k)).attr("y", yB + 20).attr("text-anchor", "middle").text(k);
        });
        q.g.append("text").attr("class", "rot-m").attr("x", x(0.5)).attr("y", yB + 36).text("← frente do ônibus");
        q.g.append("text").attr("class", "rot-m").attr("x", x(10.5)).attr("y", yB + 36).attr("text-anchor", "end").text("fundo →");
        q.g.append("text").attr("class", "rot-m").attr("x", x(5.5)).attr("y", yB + 36).attr("text-anchor", "middle").text("fileira");
        const gP = q.g.append("g"), gM = q.g.append("g");
        const lei = CX.leitura(c);
        const nC = CX.num(lei, "fileira do passageiro médio", true), nF = CX.num(lei, "a conta");
        const txt = CX.frase(c);
        function des() {
          const M = d3.sum(grupos, (g) => g.n), cm = M ? d3.sum(grupos, (g) => g.n * g.fil) / M : null;
          gP.selectAll("*").remove();
          grupos.forEach((g) => {
            for (let i = 0; i < g.n; i++) {
              const col = i % 5, lin = Math.floor(i / 5);
              gP.append("circle").attr("cx", x(g.fil) - 22 + col * 11).attr("cy", yB - 28 - lin * 11).attr("r", 4.3).attr("fill", g.cor);
            }
          });
          gM.selectAll("*").remove();
          if (cm != null) {
            gM.append("path").attr("d", `M${x(cm)},${yB + 2}l-9,14h18z`).attr("fill", "#111");
            gM.append("line").attr("x1", x(cm)).attr("x2", x(cm)).attr("y1", 16).attr("y2", yB).attr("stroke", "#111").attr("stroke-dasharray", "3 3");
            gM.append("text").attr("class", "rot-f").attr("x", x(cm) + 6).attr("y", 26).text("passageiro médio: " + f(cm, 1));
          }
          nC.set(cm == null ? "—" : f(cm, 1));
          const partes = grupos.filter((g) => g.n).map((g) => `${g.n}·${g.fil}`);
          nF.set(M ? `(${partes.join(" + ")}) ÷ ${M}` : "—");
          txt.innerHTML = cm == null ? "Sem passageiros, não há centro." :
            `Ninguém trocou de banco para o ponto se mover: basta mudar quantos estão em cada lugar. Com ${M} passageiros, o passageiro médio está na fileira ${f(cm, 1)}. Repare que não existe necessariamente alguém sentado nessa fileira; o centro é uma conta, não uma pessoa.`;
        }
        des();
      },

      async dados(c) {
        const [m, base] = await Promise.all([CX.dado("metodo_centro_massa.json"), CX.base()]);
        const reg = base.amc_reg;
        const ctl = CX.ctrl(c);
        let v = "pastagem", ano = 2024, med = false;
        const sv = CX.seg(ctl, { opcoes: [["pastagem", "pastagem"], ["bovinos", "rebanho"], ["agricultura", "agricultura"], ["veg_natural", "vegetação natural"]], val: v, aoMudar: (k) => { v = k; des(); } });
        const sa = CX.slider(ctl, { rot: "ano", min: 1985, max: 2024, val: 2024, fmt: String, aoMudar: (a) => { ano = a; des(); } });
        const ctl2 = CX.ctrl(c);
        CX.check(ctl2, " mostrar também o centro mediano (Weiszfeld)", false, (b) => { med = b; des(); });
        let parar = null;
        const bp = CX.btn(ctl2, "▶ animar 1985→2024", () => {
          if (parar) { parar(); parar = null; bp.textContent = "▶ animar 1985→2024"; return; }
          bp.textContent = "❚❚ parar"; let t0 = null;
          parar = CX.loop((t) => { if (t0 == null) t0 = t; const a = 1985 + Math.floor((t - t0) / 160) % 40; if (a !== ano) sa.set(a); });
        });
        const grid = h("div", { class: "cx-grade2" }); c.appendChild(grid);
        const esq = h("div"), dir = h("div"); grid.append(esq, dir);
        const q = CX.quadro(esq, { w: 360, h: 400, m: { t: 4, r: 4, b: 4, l: 4 } });
        const mp = CX.mapaAMC(q.g, m, q.iw, q.ih);
        const gT = q.g.append("g");
        const qb = CX.quadro(dir, { w: 360, h: 200, m: { l: 60, r: 40, t: 24, b: 24 } });
        const qd = CX.quadro(dir, { w: 360, h: 190, m: { l: 44, r: 16, t: 20, b: 26 } });
        const lei = CX.leitura(c);
        const nD = CX.num(lei, "centro mais ao norte que em 1985", true), nO = CX.num(lei, "valor do pipeline #32 (1985→2024)"), nV = CX.num(lei, "IC95% do bootstrap");
        const i0 = 0;
        function centro(t) {
          const w = m.pesos[v][t]; let sw = 0, sx = 0, sy = 0;
          m.amc.forEach((a, i) => { sw += w[i]; sx += w[i] * a.cx; sy += w[i] * a.cy; });
          return [sx / sw, sy / sw];
        }
        function mediano(t) {
          const w = m.pesos[v][t]; let [x, y] = centro(t);
          for (let it = 0; it < 60; it++) {
            let nx = 0, ny = 0, d = 0;
            m.amc.forEach((a, i) => { const dist = Math.hypot(a.cx - x, a.cy - y) || 1e-6; nx += (w[i] * a.cx) / dist; ny += (w[i] * a.cy) / dist; d += w[i] / dist; });
            x = nx / d; y = ny / d;
          }
          return [x, y];
        }
        function des() {
          const t = ano - 1985, w = m.pesos[v][t];
          const dens = m.amc.map((a, i) => w[i] / a.area);
          const cs = d3.scaleSequential(d3.interpolateRgb("#f6f1e6", { pastagem: "#8a6d1c", bovinos: "#6b4f16", agricultura: "#a83c78", veg_natural: "#24543a" }[v])).domain([0, d3.quantile([...dens].sort(d3.ascending), 0.95)]);
          mp.sel.attr("fill", (_, i) => cs(dens[i]))
            .on("mousemove", (ev, a) => { const i = m.amc.indexOf(a); CX.tip.mostra(ev, `<b>${a.nome}</b> (${reg[i]})<br>${f(w[i], 0)} ${m.vars[v].unidade} em ${ano}`); })
            .on("mouseleave", CX.tip.esconde);
          const cam = d3.range(0, t + 1).map(centro);
          gT.selectAll("*").remove();
          gT.append("path").attr("d", d3.line().x((p) => mp.px(p[0])).y((p) => mp.py(p[1]))(cam)).attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 1.5);
          const p0 = cam[0], pt = cam[cam.length - 1];
          gT.append("circle").attr("cx", mp.px(p0[0])).attr("cy", mp.py(p0[1])).attr("r", 4).attr("fill", "#fff").attr("stroke", "#111");
          gT.append("circle").attr("cx", mp.px(pt[0])).attr("cy", mp.py(pt[1])).attr("r", 6).attr("fill", C.acento).attr("stroke", "#fff").attr("stroke-width", 2);
          if (med) { const pm = mediano(t); gT.append("rect").attr("x", mp.px(pm[0]) - 5).attr("y", mp.py(pm[1]) - 5).attr("width", 10).attr("height", 10).attr("fill", C.azul).attr("stroke", "#fff"); }
          gT.append("text").attr("class", "rot-m").attr("x", 6).attr("y", 14).text("○ 1985   ● " + ano + (med ? "   ■ mediano" : ""));
          // fatia por região
          const tot = d3.sum(w), fat = ["Sul", "Centro", "Norte"].map((r) => [r, d3.sum(w.filter((_, i) => reg[i] === r)) / tot]);
          const fat0 = ["Sul", "Centro", "Norte"].map((r) => d3.sum(m.pesos[v][0].filter((_, i) => reg[i] === r)) / d3.sum(m.pesos[v][0]));
          const xb = d3.scaleLinear().domain([0, 0.8]).range([0, qb.iw]), yb = d3.scaleBand().domain(["Sul", "Centro", "Norte"]).range([0, qb.ih]).padding(0.3);
          CX.eixos(qb, xb, yb, { xf: (x) => CX.pct(x), grade: false, xt: 4 });
          qb.g.selectAll(".b").remove();
          qb.g.append("text").attr("class", "b rot-f").attr("y", -10).text(`fatia de cada região no total, ${ano} (traço: 1985)`);
          fat.forEach(([r, s], k) => {
            qb.g.append("rect").attr("class", "b").attr("y", yb(r)).attr("height", yb.bandwidth()).attr("width", xb(s)).attr("fill", C[r]).attr("rx", 3);
            qb.g.append("line").attr("class", "b").attr("x1", xb(fat0[k])).attr("x2", xb(fat0[k])).attr("y1", yb(r) - 3).attr("y2", yb(r) + yb.bandwidth() + 3).attr("stroke", "#111").attr("stroke-width", 2);
            qb.g.append("text").attr("class", "b rot").attr("x", xb(s) + 5).attr("y", yb(r) + yb.bandwidth() / 2 + 4).text(CX.pct(s));
          });
          // deslocamento ao norte ao longo do tempo
          const serie = d3.range(0, 40).map((k) => centro(k)[1] - p0[1]);
          const xd = d3.scaleLinear().domain([1985, 2024]).range([0, qd.iw]), yd = d3.scaleLinear().domain([Math.min(-10, d3.min(serie)), Math.max(90, d3.max(serie))]).range([qd.ih, 0]);
          CX.eixos(qd, xd, yd, { xf: CX.anoF, yl: "km ao norte de 1985", xt: 5, yt: 4 });
          qd.g.selectAll(".l").remove();
          qd.g.append("line").attr("class", "l zero").attr("x1", 0).attr("x2", qd.iw).attr("y1", yd(0)).attr("y2", yd(0));
          qd.g.append("path").attr("class", "l").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2).attr("d", d3.line().x((_, k) => xd(1985 + k)).y((d) => yd(d))(serie));
          qd.g.append("circle").attr("class", "l").attr("cx", xd(ano)).attr("cy", yd(serie[t])).attr("r", 4).attr("fill", C.acento);
          nD.set(fs(pt[1] - p0[1], 1) + " km");
          const of = m.oficial.boot.find((b) => b.variavel === v && b.janela.startsWith("L"));
          nO.set(of ? fs(of.dN_km, 1) + " km" : "—");
          nV.set(of ? `[${f(of.dN_lo, 1)}; ${f(of.dN_hi, 1)}]` : "—");
        }
        des();
        CX.frase(c, "Compare as barras de 1985 (traço) e do ano escolhido: é a mudança de fatia que desloca o ponto. Para a agricultura, o Sul cresce em hectares e mesmo assim o centro sobe, porque a fatia do Sul no total cai. A conta refeita aqui usa os mesmos pesos e centroides do #32 e bate com o valor oficial.");
        return () => parar && parar();
      },
    });
  });

  /* ---------------- 2.2 Mistura de gaussianas ---------------- */
  CX.def("gmm", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sW = CX.slider(ctl, { rot: "fatia de crianças no parquinho", min: 0, max: 1, passo: 0.05, val: 0.45, fmt: (v) => CX.pct(v), aoMudar: des });
        const sM = CX.slider(ctl, { rot: "idade média dos adultos", min: 22, max: 65, passo: 1, val: 40, fmt: (v) => v + " anos", aoMudar: des });
        const q = CX.quadro(c, { h: 260, m: { l: 40, r: 16 } });
        const x = d3.scaleLinear().domain([0, 80]).range([0, q.iw]);
        const lei = CX.leitura(c);
        const nM = CX.num(lei, "idade média de todos", true), nD = CX.num(lei, "pessoas a ±2 anos da média");
        const txt = CX.frase(c);
        const MU1 = 6, SD1 = 1.8, SD2 = 10;
        function des() {
          const w = sW.valor(), mu2 = sM.valor();
          const xs = d3.range(0, 80.01, 0.25);
          const d1 = xs.map((t) => w * S.gauss(t, MU1, SD1)), d2 = xs.map((t) => (1 - w) * S.gauss(t, mu2, SD2));
          const tot = xs.map((_, i) => d1[i] + d2[i]);
          const y = d3.scaleLinear().domain([0, d3.max(tot) * 1.1]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "idade (anos)", yf: () => "" });
          q.g.selectAll(".c").remove();
          const ar = d3.area().x((_, i) => x(xs[i])).y0(q.ih);
          q.g.append("path").attr("class", "c").attr("fill", "#e9e4d6").attr("d", ar.y1((d) => y(d))(tot));
          [[d1, C.azul], [d2, C.acento]].forEach(([d, cc]) => q.g.append("path").attr("class", "c").attr("fill", "none").attr("stroke", cc).attr("stroke-width", 2).attr("d", d3.line().x((_, i) => x(xs[i])).y((v) => y(v))(d)));
          const media = w * MU1 + (1 - w) * mu2;
          q.g.append("line").attr("class", "c").attr("x1", x(media)).attr("x2", x(media)).attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "4 3");
          q.g.append("text").attr("class", "c rot-f").attr("x", x(media) + 4).attr("y", 12).text("média = " + f(media, 1) + " anos");
          nM.set(f(media, 1) + " anos");
          const dm = (t) => w * S.gauss(t, MU1, SD1) + (1 - w) * S.gauss(t, mu2, SD2);
          let p = 0; for (let t = media - 2; t < media + 2; t += 0.01) p += dm(t) * 0.01;
          nD.set(CX.pct(p));
          txt.innerHTML = w > 0.05 && w < 0.95
            ? `Só ${CX.pct(p)} das pessoas no parquinho têm idade a até dois anos da média de ${f(media, 0)}. A média é uma conta correta, mas não descreve ninguém; as duas curvas, cada uma com seu centro (${MU1} e ${mu2} anos), descrevem.`
            : "Com quase só crianças, ou quase só adultos, sobra um monte só, e aí a média volta a descrever bem o grupo.";
        }
        des();
        c.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.azul}"></i>crianças (média de 6 anos)</span><span><i style="background:${C.acento}"></i>adultos</span><span><i style="background:#e9e4d6"></i>o que o histograma mostra (a soma)</span>` }));
      },

      async dados(c) {
        const b = await CX.base();
        const I = b.idade;
        const ctl = CX.ctrl(c);
        let modo = "dois", ato = "todos";
        CX.seg(ctl, { opcoes: [["nada", "só a curva"], ["um", "1 componente"], ["dois", "2 componentes"]], val: modo, aoMudar: (k) => { modo = k; des(); } });
        CX.seg(ctl, { opcoes: [["todos", "censo inteiro"], ["I", "Ato I"], ["II", "Ato II"], ["III", "Ato III"]], val: ato, aoMudar: (k) => { ato = k; des(); } });
        const q = CX.quadro(c, { h: 280, m: { l: 44, r: 16 } });
        const txt = CX.frase(c);
        function des() {
          q.g.selectAll("*").remove();
          if (ato === "todos") {
            const x = d3.scaleLinear().domain([0, 39]).range([0, q.iw]);
            const y = d3.scaleLinear().domain([0, 0.1]).range([q.ih, 0]);
            CX.eixos(q, x, y, { xl: "idade do pasto na conversão (anos)", yl: "densidade", yf: (v) => f(v, 2) });
            q.g.selectAll("rect.b").data(I.x).join("rect").attr("class", "b").attr("x", (a) => x(a - 0.45)).attr("width", x(0.9) - x(0)).attr("y", (_, i) => y(I.dens[i])).attr("height", (_, i) => q.ih - y(I.dens[i])).attr("fill", "#dcd6c6")
              .on("mousemove", (ev, a) => CX.tip.mostra(ev, `idade ${a} anos<br>densidade ${f(I.dens[I.x.indexOf(a)], 3)}`)).on("mouseleave", CX.tip.esconde);
            const xs = d3.range(0.5, 38.5, 0.2);
            const ln = (fn, cc, larg, tr) => q.g.append("path").attr("fill", "none").attr("stroke", cc).attr("stroke-width", larg).attr("stroke-dasharray", tr || null).attr("d", d3.line().x((t) => x(t)).y((t) => y(fn(t)))(xs));
            if (modo === "um") { const g1 = I.um[0]; ln((t) => S.gauss(t, g1.mu, g1.sigma), "#111", 2.2); }
            if (modo === "dois") {
              const [a, bb] = I.dois;
              ln((t) => a.peso * S.gauss(t, a.mu, a.sigma), C.azul, 2, "5 3");
              ln((t) => bb.peso * S.gauss(t, bb.mu, bb.sigma), C.acento, 2, "5 3");
              ln((t) => a.peso * S.gauss(t, a.mu, a.sigma) + bb.peso * S.gauss(t, bb.mu, bb.sigma), "#111", 2.2);
            }
            const [a, bb] = I.dois, u = I.um[0];
            txt.innerHTML = modo === "um"
              ? `Uma curva só (μ = ${f(u.mu, 1)}, σ = ${f(u.sigma, 1)}) passa por cima do pico jovem e por baixo do vale: não descreve nem a rotação nem a conversão de pasto velho.`
              : modo === "dois"
                ? `Duas curvas: jovem (μ = ${f(a.mu, 1)}, σ = ${f(a.sigma, 1)}, peso ${CX.pct(a.peso)}) e velha (μ = ${f(bb.mu, 1)}, σ = ${f(bb.sigma, 1)}, peso ${CX.pct(bb.peso)}), sobre ${f(I.n_eventos / 1e6, 1)} milhões de eventos não censurados. O BIC cai de ${f(I.bic1 / 1e6, 1)} para ${f(I.bic2 / 1e6, 1)} milhões — uma diferença que mede sobretudo o tamanho de n (verbete 4.9).`
                : "A curva real: idade do pasto, em anos, no momento da conversão. O primeiro pico, estreito, fica em 2 a 4 anos; depois vem uma encosta longa.";
          } else {
            const hst = b.idade_hist.find((k) => k.ato === ato);
            const x = d3.scaleLinear().domain([0, 40]).range([0, q.iw]);
            const tot = d3.sum(hst.counts);
            const y = d3.scaleLinear().domain([0, d3.max(hst.counts) / tot * 1.1]).range([q.ih, 0]);
            CX.eixos(q, x, y, { xl: "idade na conversão (anos, faixas de 2)", yf: (v) => CX.pct(v), yl: "fração dos eventos" });
            q.g.selectAll("rect.b").data(hst.counts).join("rect").attr("class", "b").attr("x", (_, i) => x(hst.bins[i]) + 1).attr("width", x(2) - x(0) - 2)
              .attr("y", (v) => y(v / tot)).attr("height", (v) => q.ih - y(v / tot)).attr("fill", C.pasto).attr("rx", 2);
            txt.innerHTML = `Ato ${ato} (${hst.periodo[0]}–${hst.periodo[1]}): ${f(hst.n / 1e6, 1)} milhões de eventos, mediana de ${f(hst.mediana, 0)} anos. Aqui entram também os censurados, cuja idade é um limite inferior (verbete 1.5); a idade máxima possível cresce com o ato, porque a série começa em 1985.`;
          }
        }
        des();
      },
    });
  });

  /* ---------------- 2.3 Hazard e decomposição (aula em passos, do laboratório de métodos) ---------------- */
  CX.def("hazard", (host) => {
    const eq = (itens) => `<div class="cx-eq">${itens.map((it) => (typeof it === "string" ? `<span>${it}</span>` : `<div class="${it.res ? "cx-eq-res" : ""}"><small>${it.rot}</small><strong class="${it.mudou ? "mudou" : ""}">${it.val}</strong></div>`)).join("")}</div>`;
    const pote = (total, saem) => `<div class="cx-cem">${d3.range(100).map((i) => `<i class="${i >= total ? "vazio" : i < saem ? "sai" : ""}"></i>`).join("")}</div>`;
    CX.passos(host, [
      {
        tit: "Uma conta com 100 balas",
        sub: "Num dia, as pessoas pegam 10% das balas que encontram no pote. Quantas saem?",
        marca: "Exemplo inventado, só para aprender a conta",
        desenha(c) {
          c.innerHTML = eq([{ rot: "estoque", val: "100 balas" }, "×", { rot: "taxa do dia", val: "10%" }, "=", { rot: "fluxo do dia", val: "10 balas", res: true }]) +
            pote(100, 10) + `<div class="cx-cem-leg"><span>em terracota, as 10 balas que saem</span><span>90 ficam no pote</span></div>`;
          CX.frase(c, "<b>Primeira ideia:</b> fluxo = estoque × taxa. A taxa (o <i>hazard</i>) é a fração do estoque que sai naquele dia, e não um número fixo de balas.");
        },
      },
      {
        tit: "Mude uma peça de cada vez",
        sub: "Parta das mesmas 100 balas e 10%. Há mais de um jeito de chegar a um fluxo menor.",
        marca: "Ainda é um exemplo inventado",
        desenha(c) {
          const ctl = CX.ctrl(c);
          const alvo = h("div"); c.appendChild(alvo);
          const fr = CX.frase(c);
          const mostra = (k) => {
            const E = k === "taxa" ? 100 : 50, T = k === "estoque" ? 10 : 5, F = (E * T) / 100;
            alvo.innerHTML = `<p class="rot-ctrl" style="text-align:center;margin:.2rem 0">antes</p>` +
              eq([{ rot: "estoque", val: "100" }, "×", { rot: "taxa", val: "10%" }, "=", { rot: "fluxo", val: "10", res: true }]) +
              `<p class="rot-ctrl" style="text-align:center;margin:.2rem 0">depois</p>` +
              eq([{ rot: "estoque", val: String(E), mudou: E < 100 }, "×", { rot: "taxa", val: T + "%", mudou: T < 10 }, "=", { rot: "fluxo", val: f(F, F % 1 ? 1 : 0), res: true }]) + pote(E, Math.round(F));
            fr.innerHTML = k === "ambos"
              ? "<b>As duas peças diminuíram e se multiplicam:</b> metade do estoque vezes metade da taxa dá um quarto do fluxo inicial."
              : `<b>O fluxo caiu de 10 para 5.</b> ${k === "estoque" ? "A taxa não mudou; só havia menos balas." : "O pote continua cheio; as pessoas é que passaram a pegar menos."} Olhando só o fluxo, as duas situações são idênticas.`;
          };
          CX.seg(ctl, { opcoes: [["estoque", "metade das balas"], ["taxa", "metade da taxa"], ["ambos", "as duas coisas"]], val: "estoque", aoMudar: mostra });
          mostra("estoque");
        },
      },
      {
        tit: "O mesmo pote ao longo dos dias",
        sub: "Com a taxa constante, o fluxo cai todo dia sozinho. Escolha um dia em que o hábito muda e compare.",
        marca: "Exemplo inventado",
        desenha(c) {
          const ctl = CX.ctrl(c);
          const sH = CX.slider(ctl, { rot: "taxa no início", min: 2, max: 20, val: 10, fmt: (v) => v + "% ao dia", aoMudar: des });
          const sA = CX.slider(ctl, { rot: "dia em que o bilhete aparece", min: 2, max: 25, val: 16, fmt: (v) => "dia " + v, aoMudar: des });
          const sN = CX.slider(ctl, { rot: "taxa depois do bilhete", min: 0, max: 20, val: 5, fmt: (v) => v + "% ao dia", aoMudar: des });
          const q = CX.quadro(c, { h: 270, m: { l: 44, r: 50 } });
          const x = d3.scaleLinear().domain([1, 25]).range([0, q.iw]);
          const txt = CX.frase(c);
          function des() {
            let estq = 100; const lin = [];
            for (let t = 1; t <= 25; t++) { const hz = (t < sA.valor() ? sH.valor() : sN.valor()) / 100; const fl = estq * hz; lin.push({ t, estq, fl, hz }); estq -= fl; }
            const y = d3.scaleLinear().domain([0, 100]).range([q.ih, 0]), yF = d3.scaleLinear().domain([0, Math.max(10, d3.max(lin, (l) => l.fl) * 1.2)]).range([q.ih, 0]);
            CX.eixos(q, x, y, { xl: "dia", yl: "balas no pote (barras) · balas pegas no dia (linha, eixo à direita)" });
            q.g.selectAll(".d").remove();
            q.g.append("g").attr("class", "d eixo").attr("transform", `translate(${q.iw},0)`).call(d3.axisRight(yF).ticks(4));
            q.g.selectAll("rect.d").data(lin).join("rect").attr("class", "d").attr("x", (l) => x(l.t) - 7).attr("width", 14).attr("y", (l) => y(l.estq)).attr("height", (l) => q.ih - y(l.estq)).attr("fill", C.veg).attr("opacity", 0.35);
            q.g.append("path").attr("class", "d").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2.4).attr("d", d3.line().x((l) => x(l.t)).y((l) => yF(l.fl))(lin));
            q.g.append("line").attr("class", "d").attr("x1", x(sA.valor()) - 9).attr("x2", x(sA.valor()) - 9).attr("y1", 0).attr("y2", q.ih).attr("stroke", "#111").attr("stroke-dasharray", "4 3");
            const d = sA.valor(), antes = lin[d - 2], depois = lin[d - 1];
            txt.innerHTML = `Do dia 1 ao dia ${d - 1}, as balas pegas caem de ${f(lin[0].fl, 1)} para ${f(antes.fl, 1)} sem que o hábito mude (${sH.valor()}% ao dia): é só o pote esvaziando. No dia ${d}, o bilhete muda a taxa para ${sN.valor()}% e o fluxo vai a ${f(depois.fl, 1)}. A linha do fluxo, sozinha, não separa os dois motivos; a conta estoque × taxa separa.`;
          }
          des();
        },
      },
      {
        tit: "O que aconteceu em Goiás",
        sub: "Agora com os dados: médias anuais do Ato II (2001–2019) e do Ato III (2020–2024). Escolha a região.",
        marca: "Dados reais da pesquisa (#39): estoque = savana + campo",
        real: true,
        async desenha(c) {
          const D = (await CX.base()).decomp;
          const ctl = CX.ctrl(c);
          const ordem = ["Sul", "Centro", "Norte", "Goiás (total)"];
          const alvo = h("div"); c.appendChild(alvo);
          const qd = h("div"); c.appendChild(qd);
          const txt = CX.frase(c);
          function des(rg) {
            const d = D.find((k) => k.regiao === rg);
            const cart = (rot, a, b, un) => `<div class="cx-cartao"><small>${rot}</small><b>${a} → ${b}</b><small>${un}</small></div>`;
            alvo.innerHTML = `<div class="cx-cartoes3">${cart("estoque de savana e campo", f(d.estoque_II, 2), f(d.estoque_III, 2), "milhões de hectares")}${cart("taxa anual de conversão", f(d.hazard_II * 100, 2) + "%", f(d.hazard_III * 100, 2) + "%", "do estoque, por ano")}${cart("fluxo anual", f(d.fluxo_II * 1000, 1), f(d.fluxo_III * 1000, 1), "mil hectares por ano")}</div>`;
            qd.replaceChildren();
            const q = CX.quadro(qd, { h: 200, m: { l: 170, r: 70, t: 24, b: 34 } });
            const lin = [["mudança do fluxo", d.d_fluxo * 1000, "#444"], ["parcela do estoque", d.efeito_estoque * 1000, C.veg], ["parcela da taxa", d.efeito_hazard * 1000, C.acento]];
            const ext = d3.max(lin, (l) => Math.abs(l[1])) * 1.15;
            const x = d3.scaleLinear().domain([-ext, ext]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.3);
            CX.eixos(q, x, null, { xl: "mil hectares por ano (Ato III − Ato II)", xf: (v) => f(v, 1) });
            q.g.append("text").attr("class", "rot-f").attr("y", -10).text("a decomposição");
            q.g.append("line").attr("class", "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", q.ih);
            lin.forEach(([n, v, cc]) => {
              q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(n)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", cc).attr("rx", 3);
              q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
              q.g.append("text").attr("class", "rot-f").attr("x", v >= 0 ? x(v) + 5 : x(v) - 5).attr("text-anchor", v >= 0 ? "start" : "end").attr("y", y(n) + y.bandwidth() / 2 + 4).text(fs(v, 2));
            });
            txt.innerHTML = rg === "Sul"
              ? `<b>No Sul</b>, o estoque diminuiu e a taxa também. Da queda do fluxo, cerca de ${CX.pct(d.share_estoque)} acompanha o estoque menor e ${CX.pct(d.share_hazard)} a taxa menor. A conta passo a passo está logo abaixo da peça.`
              : `<b>${rg === "Goiás (total)" ? "No estado" : "No " + rg}</b>, o estoque diminuiu, mas a taxa cresceu mais, e o fluxo aumentou. As duas parcelas têm sinais opostos; por isso aqui não faz sentido dizer "quantos por cento" de cada uma.`;
          }
          CX.seg(ctl, { opcoes: ordem.map((r) => [r, r]), val: "Sul", aoMudar: des });
          des("Sul");
        },
      },
    ]);
  });

  /* ---------------- 2.4 Réguas de tempo ---------------- */
  CX.def("reguas", (host) => {
    CX.modos(host, {
      simples(c) {
        const MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
        const r = CX.rng(4);
        // dois anos de vendas mensais de uma sorveteria: pico em janeiro, vale em julho
        const vendas = d3.range(24).map((m) => 40 + 70 * Math.pow(0.5 + 0.5 * Math.cos((2 * Math.PI * m) / 12), 2) + (r() - 0.5) * 8);
        const ctl = CX.ctrl(c);
        let ini = 0;
        CX.seg(ctl, { opcoes: [[0, "trimestres do calendário (jan–mar…)"], [11, "trimestres das estações (dez–fev…)"], [1, "começando em fevereiro (fev–abr…)"]], val: ini, aoMudar: (k) => { ini = k; des(); } });
        const q = CX.quadro(c, { h: 270, m: { l: 44, r: 16, t: 20 } });
        const x = d3.scaleBand().domain(d3.range(24)).range([0, q.iw]).padding(0.15);
        const y = d3.scaleLinear().domain([0, 125]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xf: (m) => (m % 3 === 0 ? MES[m % 12] + (m % 12 === 0 ? (m < 12 ? " (ano 1)" : " (ano 2)") : "") : ""), yl: "sorvetes vendidos por dia, média do mês" });
        q.g.selectAll("rect.m").data(vendas).join("rect").attr("class", "m").attr("x", (_, m) => x(m)).attr("width", x.bandwidth()).attr("y", (v) => y(v)).attr("height", (v) => q.ih - y(v)).attr("fill", "#dcd6c6").attr("rx", 2);
        const gT = q.g.append("g");
        const lei = CX.leitura(c);
        const nM = CX.num(lei, "melhor trimestre (média)", true), nP = CX.num(lei, "pior trimestre (média)"), nR = CX.num(lei, "razão melhor ÷ pior");
        const txt = CX.frase(c);
        function des() {
          gT.selectAll("*").remove();
          const tri = [];
          for (let a = ini; a + 3 <= 24; a += 3) tri.push({ a, b: a + 3, m: S.media(vendas.slice(a, a + 3)) });
          const best = tri.reduce((p, q2) => (q2.m > p.m ? q2 : p)), worst = tri.reduce((p, q2) => (q2.m < p.m ? q2 : p));
          tri.forEach((t) => {
            const x0 = x(t.a), x1 = x(t.b - 1) + x.bandwidth();
            gT.append("line").attr("x1", x0).attr("x2", x1).attr("y1", y(t.m)).attr("y2", y(t.m)).attr("stroke", t === best ? C.acento : "#555").attr("stroke-width", t === best ? 3.5 : 2);
            gT.append("line").attr("x1", x0 - 1).attr("x2", x0 - 1).attr("y1", 0).attr("y2", q.ih).attr("stroke", "#bbb").attr("stroke-dasharray", "3 3");
            gT.append("text").attr("class", t === best ? "rot-f" : "rot-m").attr("x", (x0 + x1) / 2).attr("y", y(t.m) - 6).attr("text-anchor", "middle").text(f(t.m, 0));
          });
          nM.set(`${MES[best.a % 12]}–${MES[(best.b - 1) % 12]}: ${f(best.m, 0)}`);
          nP.set(`${MES[worst.a % 12]}–${MES[(worst.b - 1) % 12]}: ${f(worst.m, 0)}`);
          nR.set(f(best.m / worst.m, 2) + "×");
          txt.innerHTML = ini === 11
            ? "Com o verão inteiro num trimestre só, ele se destaca: é o recorte que mostra o pico com mais nitidez. Nada nas vendas mudou; mudou só onde cada trimestre começa."
            : ini === 0
              ? "No calendário, dezembro fica num trimestre e janeiro e fevereiro no outro. O verão se divide, e o melhor trimestre parece menos excepcional do que é."
              : "Começando em fevereiro, o recorte parte o verão de outro jeito. A pergunta honesta não é qual recorte está certo, e sim se a conclusão sobrevive a todos eles.";
        }
        des();
      },

      async dados(c) {
        const g = (await CX.base()).go;
        const ctl = CX.ctrl(c);
        let v = "pasto", r = "atos";
        CX.seg(ctl, { opcoes: [["pasto", "pastagem"], ["agric", "agricultura"], ["mosaico", "mosaico"], ["veg", "vegetação natural"]], val: v, aoMudar: (k) => { v = k; des(); } });
        CX.seg(ctl, { opcoes: [["completa", "série completa"], ["atos", "atos"], ["grade", "grade de 5 anos"], ["decadas", "décadas"]], val: r, aoMudar: (k) => { r = k; des(); } });
        const q = CX.quadro(c, { h: 280, m: { l: 50, r: 16, t: 20 } });
        const x = d3.scaleLinear().domain([1985, 2024]).range([0, q.iw]);
        const txt = CX.frase(c);
        const reg = {
          completa: [[1985, 2024]], atos: [[1985, 2000], [2000, 2019], [2019, 2024]],
          grade: [[1985, 1990], [1990, 1995], [1995, 2000], [2000, 2005], [2005, 2010], [2010, 2015], [2015, 2020], [2020, 2024]],
          decadas: [[1985, 1990], [1990, 2000], [2000, 2010], [2010, 2020], [2020, 2024]],
        };
        function des() {
          const ser = g[v], dlt = S.diff(ser);
          const y = d3.scaleLinear().domain([Math.min(-0.8, d3.min(dlt)), Math.max(0.8, d3.max(dlt))]).nice().range([q.ih, 0]);
          CX.eixos(q, x, y, { xf: CX.anoF, yl: "variação anual (Mha/ano)", yf: (k) => f(k, 1) });
          q.g.selectAll(".d").remove();
          q.g.append("line").attr("class", "d zero").attr("x1", 0).attr("x2", q.iw).attr("y1", y(0)).attr("y2", y(0));
          q.g.selectAll("circle.d").data(dlt).join("circle").attr("class", "d").attr("cx", (_, i) => x(1986 + i)).attr("cy", (d) => y(d)).attr("r", 3).attr("fill", C.cinza);
          const res = reg[r].map(([a, b]) => { const vals = dlt.slice(a - 1985, b - 1985); return [a, b, S.media(vals)]; });
          res.forEach(([a, b, mm]) => {
            q.g.append("rect").attr("class", "d").attr("x", x(a + 0.5)).attr("width", x(b + 0.5) - x(a + 0.5) - 2).attr("y", y(Math.max(0, mm))).attr("height", Math.abs(y(mm) - y(0))).attr("fill", mm >= 0 ? C.acento : C.azul).attr("opacity", 0.35);
            q.g.append("line").attr("class", "d").attr("x1", x(a + 0.5)).attr("x2", x(b + 0.5) - 2).attr("y1", y(mm)).attr("y2", y(mm)).attr("stroke", mm >= 0 ? C.acento : C.azul).attr("stroke-width", 2.5);
            q.g.append("text").attr("class", "d rot-f").attr("x", (x(a + 0.5) + x(b + 0.5)) / 2).attr("y", y(mm) + (mm >= 0 ? -6 : 16)).attr("text-anchor", "middle").style("font-size", "11px").text(fs(mm, 2));
          });
          txt.innerHTML = `Pontos: a variação de cada ano. Faixas: a média anual dentro de cada janela da régua "${{ completa: "série completa", atos: "atos", grade: "grade de 5 anos", decadas: "décadas" }[r]}". Troque de régua e confira se o sinal de cada período se mantém: é esse o teste do #35.`;
        }
        des();
      },
    });
  });

  /* ---------------- 2.5 Quebra estrutural ---------------- */
  function varredura(y, minT) {
    const n = y.length, m = S.media(y), ss0 = y.reduce((s, v) => s + (v - m) ** 2, 0);
    const out = [];
    for (let k = minT; k <= n - minT; k++) {
      const a = y.slice(0, k), b = y.slice(k), ma = S.media(a), mb = S.media(b);
      const ss1 = a.reduce((s, v) => s + (v - ma) ** 2, 0) + b.reduce((s, v) => s + (v - mb) ** 2, 0);
      out.push({ k, F: (ss0 - ss1) / (ss1 / (n - 2)), ma, mb });
    }
    return out;
  }
  function desenhaQuebra(c, anos, y, o) {
    c.replaceChildren();
    const rotT = o.rotT || String;
    const q1 = CX.quadro(c, { h: 200, m: { l: 50, r: 16, t: 14, b: 26 } });
    const x = d3.scaleLinear().domain([anos[0], anos[anos.length - 1]]).range([0, q1.iw]);
    const yy = d3.scaleLinear().domain(d3.extent(y)).nice().range([q1.ih, 0]);
    CX.eixos(q1, x, yy, { xf: o.xf || CX.anoF, yl: o.yl, yf: o.yf, xl: o.xl });
    q1.g.selectAll("circle").data(y).join("circle").attr("cx", (_, i) => x(anos[i])).attr("cy", (v) => yy(v)).attr("r", 3.2).attr("fill", C.cinza);
    const sc = varredura(y, o.minT || 5), best = sc.reduce((a, b) => (b.F > a.F ? b : a));
    q1.g.append("line").attr("x1", 0).attr("x2", x(anos[best.k] - 0.5)).attr("y1", yy(best.ma)).attr("y2", yy(best.ma)).attr("stroke", C.acento).attr("stroke-width", 2.5);
    q1.g.append("line").attr("x1", x(anos[best.k] - 0.5)).attr("x2", q1.iw).attr("y1", yy(best.mb)).attr("y2", yy(best.mb)).attr("stroke", C.acento).attr("stroke-width", 2.5);
    const q2 = CX.quadro(c, { h: 170, m: { l: 50, r: 16, t: 14, b: 26 } });
    const yF = d3.scaleLinear().domain([0, Math.max(12, best.F * 1.15)]).range([q2.ih, 0]);
    CX.eixos(q2, x, yF, { xf: o.xf || CX.anoF, yl: "estatística F se a quebra fosse aqui", yt: 4 });
    q2.g.append("path").attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 2).attr("d", d3.line().x((s) => x(anos[s.k])).y((s) => yF(s.F))(sc));
    q2.g.append("circle").attr("cx", x(anos[best.k])).attr("cy", yF(best.F)).attr("r", 5).attr("fill", C.acento);
    q2.g.append("text").attr("class", "rot-f").attr("x", x(anos[best.k]) + 8).attr("y", yF(best.F) + 4).text(`pico: ${rotT(anos[best.k])} (F = ${f(best.F, 1)})`);
    (o.marcas || []).forEach(([a, t]) => {
      q2.g.append("line").attr("x1", x(a)).attr("x2", x(a)).attr("y1", 0).attr("y2", q2.ih).attr("stroke", C.azul).attr("stroke-dasharray", "4 3");
      q2.g.append("text").attr("class", "rot-m").attr("x", x(a) + 3).attr("y", q2.ih - 5).style("fill", C.azul).text(t);
    });
    return best;
  }
  CX.def("quebra", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        let semente = 3;
        const sQ = CX.slider(ctl, { rot: "dia em que o viaduto abriu", min: 8, max: 52, val: 34, fmt: (v) => "dia " + v, aoMudar: des });
        const sT = CX.slider(ctl, { rot: "quanto o viaduto encurta", min: 0, max: 10, passo: 0.5, val: 6, fmt: (v) => f(v, 1) + " min", aoMudar: des });
        const sR = CX.slider(ctl, { rot: "variação do trânsito de um dia para outro", min: 0.5, max: 8, passo: 0.5, val: 3, fmt: (v) => "± " + f(v, 1) + " min", aoMudar: des });
        const ctl2 = CX.ctrl(c);
        CX.btn(ctl2, "sortear outros dias", () => { semente++; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const txt = CX.frase(c);
        const dias = d3.range(1, 61);
        function des() {
          const r = CX.rng(semente);
          const y = dias.map((d) => 40 - (d >= sQ.valor() ? sT.valor() : 0) + CX.normal(r) * sR.valor());
          const b = desenhaQuebra(alvo, dias, y, { yl: "minutos de casa ao trabalho", yf: (v) => f(v, 0), xf: (d) => "dia " + d, rotT: (d) => "dia " + d, marcas: sT.valor() > 0 ? [[sQ.valor(), "viaduto"]] : [] });
          txt.innerHTML = sT.valor() === 0
            ? `Sem viaduto nenhum, a curva ainda tem um pico (F = ${f(b.F, 1)}): a varredura sempre acha um "melhor" dia. Por isso se compara o pico com o que dias sem mudança produzem. No detector do trabalho, esse falso alarme acontece em 11% das séries de puro ruído.`
            : `O pico caiu no dia ${dias[b.k]}; o viaduto abriu no dia ${sQ.valor()}. Aumente a variação do trânsito ou diminua o ganho do viaduto e veja o pico se perder no meio do ruído.`;
        }
        des();
      },
      async dados(c) {
        const g = (await CX.base()).go;
        const ctl = CX.ctrl(c);
        let v = "pasto";
        CX.seg(ctl, { opcoes: [["pasto", "Δ pastagem"], ["veg", "Δ vegetação natural"], ["agric", "Δ agricultura"], ["uniao", "Δ agricultura ∪ mosaico"]], val: v, aoMudar: (k) => { v = k; des(); } });
        const alvo = h("div"); c.appendChild(alvo);
        const txt = CX.frase(c);
        function des() {
          const ser = v === "uniao" ? g.agric.map((a, i) => a + g.mosaico[i]) : g[v];
          const y = S.diff(ser), anos = g.anos.slice(1);
          const b = desenhaQuebra(alvo, anos, y, { yl: "variação anual (Mha)", yf: (k) => f(k, 1), marcas: [[2001, "2001 (#29)"], [2020, "2020 (#29)"]] });
          txt.innerHTML = `Varredura de uma quebra de média, uma série por vez: pico em ${anos[b.k]} (F = ${f(b.F, 1)}). O trabalho usa o sup-F <i>multivariado</i> (as três séries juntas) com segmentação binária, que acha 2001 (F = 62,2) e depois 2020 (F = 21,5); os valores de F aqui não são comparáveis aos dele. Veja que a série da união agricultura ∪ mosaico deixa a quebra de 2020 mais nítida; no trabalho, F sobe de 21,5 para 34,1 sob essa correção.`;
        }
        des();
      },
    });
  });

})();
