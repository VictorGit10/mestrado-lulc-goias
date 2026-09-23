/* Caderno de conceitos — Parte 7: os conceitos do argumento */
(function () {
  "use strict";
  const { h, cor: C, f, fs, est: S } = CX;

  function grangerP(y, x) {
    const Xr = [], Xf = [], yy = [];
    for (let t = 1; t < y.length; t++) { Xr.push([1, y[t - 1]]); Xf.push([1, y[t - 1], x[t - 1]]); yy.push(y[t]); }
    const a = S.ols(Xr, yy), b = S.ols(Xf, yy), d2 = yy.length - 3, F = (a.ssr - b.ssr) / (b.ssr / d2);
    return S.pF(F, 1, d2);
  }

  /* ---------------- 7.1 Motor comum × empurrão ---------------- */
  CX.def("drive", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        let hip = "mare", sem = 3;
        CX.seg(ctl, { opcoes: [["corda", "corda: o Sul empurra o Norte"], ["mare", "maré: força comum"]], val: hip, aoMudar: (k) => { hip = k; des(); } });
        CX.btn(ctl, "sortear outra história", () => { sem++; des(); });
        const alvo = h("div"); c.appendChild(alvo);
        const tab = h("table", { class: "cx-tab" }); c.appendChild(tab);
        function des() {
          const r = CX.rng(sem * 7 + (hip === "corda" ? 1 : 2)), n = 39;
          const F = d3.range(n).map(() => CX.normal(r)); // a maré (choque comum)
          const sul = [], norte = [];
          for (let t = 0; t < n; t++) {
            if (hip === "corda") { sul.push(CX.normal(r)); norte.push((t ? 0.8 * sul[t - 1] : 0) + CX.normal(r) * 0.6); }
            else { sul.push(0.9 * F[t] + CX.normal(r) * 0.5); norte.push(0.5 * F[t] + CX.normal(r) * 0.5); }
          }
          alvo.replaceChildren();
          const series = [{ nome: "Sul", cor: C.Sul, v: sul }, { nome: "Norte", cor: C.Norte, v: norte }];
          if (hip === "mare") series.unshift({ nome: "força comum", cor: C.cinza, v: F, traco: "3 3", larg: 1.4 });
          CX.linhas(alvo, { anos: d3.range(1986, 1986 + n), h: 240, m: { l: 40, r: 100, t: 10 }, yl: "variação anual (padronizada)", series, yf: (v) => f(v, 0) });
          const pSN = grangerP(norte, sul), pNS = grangerP(sul, norte), r0 = S.corr(sul, norte);
          tab.innerHTML = `<tr><th>assinatura</th><th>nesta história</th><th>o empurrão exige</th><th>a força comum exige</th></tr>
            <tr><td>o passado do Sul prevê o Norte (Granger)</td><td>p = ${CX.p(pSN)}</td><td>p pequeno</td><td>p grande</td></tr>
            <tr><td>o passado do Norte prevê o Sul</td><td>p = ${CX.p(pNS)}</td><td>p grande</td><td>p grande</td></tr>
            <tr><td>Sul e Norte variam juntos no mesmo ano</td><td>r = ${f(r0, 2)}</td><td>pouco</td><td>sim, e mais onde a exposição é maior</td></tr>`;
        }
        des();
        CX.frase(c, "Os dois mundos produzem duas metades que \"marcham juntas\" ao longo dos anos. O que os separa é a assinatura temporal: com a corda, o Sul de ontem prevê o Norte de hoje; com a maré, os dois se movem no mesmo ano e nenhum antecipa o outro.");
      },
      async passos(c) {
        const [b, m] = await Promise.all([CX.base(), CX.dado("metodo_centro_massa.json")]);
        const M = b.macro, nomePor = Object.fromEntries(m.amc.map((a) => [a.code, a.nome]));
        const delta = S.diff(M.cambio), mu = S.media(delta), sd = Math.sqrt(delta.reduce((s, v) => s + (v - mu) ** 2, 0) / delta.length);
        const choque = (anoChoque) => { const i = M.anos.indexOf(anoChoque); return { antes: M.cambio[i - 1], depois: M.cambio[i], d: delta[i - 1], z: (delta[i - 1] - mu) / sd, ano: anoChoque }; };
        const ord = [...b.apt].sort((p, q) => p.expo - q.expo);
        const rep = [0.15, 0.5, 0.85].map((qq) => ord[Math.round(qq * (ord.length - 1))]);
        const beta = b.horse.find((k) => k.spec === "S1" && k.exposicao === "exp_apt_edafo").beta;
        const nivel = ["menor aptidão", "aptidão intermediária", "maior aptidão"];
        let anoChoque = 2020, igual = false;
        const escolha = (p, redesenha) => {
          const ctl = CX.ctrl(p);
          CX.seg(ctl, { opcoes: [[2020, "alta de 2019 → 2020"], [2022, "queda de 2021 → 2022"]], val: anoChoque, aoMudar: (k) => { anoChoque = k; redesenha(); } });
        };
        const lugar = (a, i, extra) => `<div class="cx-cartao"><small>AMC ${i + 1} · ${a.reg}</small><b>${nomePor[a.code] || a.code}</b>${extra}</div>`;
        CX.passos(c, [
          {
            tit: "Uma mudança. Três lugares.",
            sub: "O índice do câmbio muda no mesmo ano para todas as 166 AMCs. Primeiro, siga só o sinal comum.",
            marca: "Série real do câmbio (Ipeadata); AMCs reais",
            real: true,
            desenha(p) {
              const alvo = h("div");
              escolha(p, des); p.appendChild(alvo);
              const fr = CX.frase(p);
              function des() {
                const k = choque(anoChoque);
                alvo.innerHTML = `<div class="cx-eq"><div><small>câmbio real efetivo, ${k.ano - 1}</small><strong>${f(k.antes, 1)}</strong></div><span>→</span><div><small>${k.ano}</small><strong>${f(k.depois, 1)}</strong></div><span>=</span><div class="cx-eq-res"><small>mudança</small><strong>${fs(k.d, 1)}</strong></div></div>
                  <p style="text-align:center;margin:.2rem 0;color:var(--color-muted)">↓ &nbsp; ↓ &nbsp; ↓ &nbsp; a mesma mudança chega às três</p>
                  <div class="cx-cartoes3">${rep.map((a, i) => lugar(a, i, "<small>recebe o mesmo câmbio</small>")).join("")}</div>`;
                fr.innerHTML = "<b>Primeira ideia:</b> o câmbio sozinho não explica por que uma AMC responderia diferente de outra no mesmo ano. Ele é igual para todas.";
              }
              des();
            },
          },
          {
            tit: "As condições locais mudam a resposta",
            sub: "Agora olhe para uma diferença entre os lugares: a aptidão agrícola, medida antes e por fora do uso da terra.",
            marca: "As três AMCs e suas aptidões são reais (Embrapa)",
            real: true,
            desenha(p) {
              p.innerHTML = `<div class="cx-cartoes3">${rep.map((a, i) => lugar(a, i, `<div style="font-size:1.1rem;color:${C.acento};letter-spacing:.15em">${"●".repeat(i + 1)}${"○".repeat(2 - i)}</div><small>${nivel[i]}: ${fs(a.expo, 2)} na escala padronizada</small>`)).join("")}</div>`;
              CX.frase(p, "<b>Segunda ideia:</b> a <i>exposição</i> é a característica local que faz o mesmo sinal entrar de modo diferente na comparação. Aqui ela é a aptidão; o verbete 5.3 mostra que ela anda junto com a latitude.");
            },
          },
          {
            tit: "O modelo combina sinal × exposição",
            sub: "Veja só a parcela que o modelo associa a essa interação. Ela não é a mudança total observada do rebanho.",
            marca: "Coeficiente estimado: β = −0,0325 (#52)",
            real: true,
            desenha(p) {
              const ctl = CX.ctrl(p);
              CX.seg(ctl, { opcoes: [[2020, "alta de 2019 → 2020"], [2022, "queda de 2021 → 2022"]], val: anoChoque, aoMudar: (k) => { anoChoque = k; des(); } });
              CX.check(ctl, " e se os três lugares tivessem a mesma exposição?", igual, (v) => { igual = v; des(); });
              const alvo = h("div"); p.appendChild(alvo);
              const fr = CX.frase(p);
              function des() {
                const k = choque(anoChoque);
                const vals = rep.map((a) => beta * k.z * (igual ? rep[1].expo : a.expo));
                alvo.innerHTML = `<div class="cx-eq"><div><small>sinal comum (${k.ano - 1}→${k.ano})</small><strong>${fs(k.z, 2)}</strong></div><span>×</span><div><small>condição local</small><strong>exposição</strong></div><span>×</span><div><small>coeficiente</small><strong>${f(beta, 4)}</strong></div><span>=</span><div class="cx-eq-res"><small>parcela estimada</small><strong>nas barras ↓</strong></div></div><p style="text-align:center;margin:-.3rem 0 .4rem;font-size:.8rem;color:var(--color-muted)">o choque de ${k.ano - 1}→${k.ano} entra na variação do rebanho de ${k.ano}→${k.ano + 1}</p>`;
                const q = CX.quadro(alvo, { w: 480, h: 190, m: { l: 175, r: 56, t: 10, b: 38 } });
                const L = Math.max(0.09, ...vals.map(Math.abs)) * 1.15;
                const x = d3.scaleLinear().domain([-L, L]).range([0, q.iw]), y = d3.scaleBand().domain([0, 1, 2]).range([0, q.ih]).padding(0.3);
                CX.eixos(q, x, null, { xl: "desvios-padrão da variação do rebanho (só a interação)", xf: (v) => f(v, 2), xt: 5 });
                q.g.append("line").attr("class", "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", q.ih);
                vals.forEach((v, i) => {
                  q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(i)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", v < 0 ? C.azul : C.acento).attr("rx", 3);
                  q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(i) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(`${nomePor[rep[i].code] || rep[i].code} (${igual ? "exposição igualada" : nivel[i]})`);
                  q.g.append("text").attr("class", "rot-f").attr("x", v >= 0 ? x(v) + 5 : x(v) - 5).attr("text-anchor", v >= 0 ? "start" : "end").attr("y", y(i) + y.bandwidth() / 2 + 4).text(fs(v, 3));
                });
                fr.innerHTML = igual
                  ? "<b>Com as exposições igualadas</b>, as três parcelas ficam iguais: sem diferença local, a interação não produz contraste nenhum entre as AMCs. O modelo só aprende alguma coisa comparando lugares diferentes diante do mesmo choque."
                  : `<b>O modelo estima parcelas diferentes para o mesmo choque.</b> É isso que a interação compara. Lembre o limite: o p agrupado é 0,026, a permutação circular dá 0,132, e com a latitude na conta o coeficiente da aptidão encolhe 62%. Trate o motor comum como hipótese compatível com os dados, e não como causa demonstrada.`;
              }
              des();
            },
          },
        ]);
      },
      placar(c) {
        const linhas = [
          ["Empurrão", "o passado da lavoura do Sul prevê o pasto do Norte", "0 de 24 combinações com p < 0,05 (Granger, #34)", "não aparece"],
          ["Empurrão", "sob método robusto a séries integradas, alguma direção lidera", "Toda-Yamamoto: p = 0,25 (Sul→Norte) e 0,45 (Norte→Sul)", "sem líder"],
          ["Empurrão", "lavoura nos vizinhos ao sul vem com mais pasto local", "nenhuma das 36 estimativas positiva e significativa; com 8 vizinhos, 12 de 12 negativas (a única com p < 0,05 tem o sinal oposto)", "não aparece"],
          ["Empurrão", "precedência só onde há mecanismo", "nos placebos, o pasto do Norte \"antecede\" até o pasto do próprio Sul", "precedência genérica"],
          ["Motor comum", "a força é externa: o teste inverso dá nulo", "câmbio passa no placebo de exogeneidade (#37)", "aparece"],
          ["Motor comum", "a resposta ao mesmo choque muda com a posição no eixo", "direção prevista; p por permutação de 0,07 a 0,13 (#54)", "direção prevista, sem cruzar 5%"],
          ["Motor comum", "o padrão só aparece onde deveria", "placebos de desfecho (urbano, água) e de tempo vazios; jackknife estável", "específico"],
          ["Motor comum", "a exposição medida é o canal", "com a latitude na conta, a aptidão perde 62% e a significância (#56)", "o canal fica em aberto"],
        ];
        const tab = h("table", { class: "cx-tab" });
        tab.innerHTML = "<tr><th>hipótese</th><th>assinatura exigida</th><th>o que o trabalho encontrou</th><th>leitura</th></tr>" +
          linhas.map((l, i) => `<tr data-i="${i}" style="cursor:pointer"><td style="color:${l[0] === "Empurrão" ? C.acento : C.azul};font-weight:700">${l[0]}</td><td>${l[1]}</td><td>${l[2]}</td><td>${l[3]}</td></tr>`).join("");
        c.appendChild(h("div", { style: { overflowX: "auto" } }, tab));
        const det = CX.frase(c, "Clique numa linha para ver o verbete que explica o teste.");
        const alvo = ["granger", "ty", "iluc", "ty", "granger", "perm", "perm", "horse"];
        tab.querySelectorAll("tr[data-i]").forEach((tr) => tr.addEventListener("click", () => {
          tab.querySelectorAll("tr").forEach((t) => t.classList.remove("on")); tr.classList.add("on");
          const k = alvo[+tr.dataset.i];
          det.innerHTML = `Este teste é explicado no verbete <a href="#${k}">${document.querySelector("#" + k + " .cx-cod").textContent} ${document.querySelector("#" + k + " h3").textContent}</a>.`;
        }));
        CX.frase(c, "Nenhuma assinatura do empurrão aparece; as do motor comum aparecem na direção prevista, sem cruzar o corte de 5%, e sem identificar nem a força nem o canal. É por isso que a frase-síntese diz \"compatível com\".");
      },
    });
  });

  /* ---------------- 7.2 Gradiente ---------------- */
  CX.def("gradiente", async (host) => {
    const [m, b] = await Promise.all([CX.dado("metodo_centro_massa.json"), CX.base()]);
    const aptPor = Object.fromEntries(b.apt.map((a) => [a.code, a]));
    const lat = m.amc.map((a) => aptPor[a.code].lat);
    const nF = 8, ext = d3.extent(lat), passo = (ext[1] - ext[0]) / nF;
    const faixa = lat.map((l) => Math.min(nF - 1, Math.floor((l - ext[0]) / passo)));
    const med = {
      apt: ["aptidão agrícola média (Embrapa)", () => m.amc.map((a) => aptPor[a.code].score), false, (v) => f(v, 2)],
      agric: ["agricultura, % da área", (t) => m.amc.map((a, i) => m.pesos.agricultura[t][i] / (a.area * 100)), true, CX.pct],
      pasto: ["pastagem, % da área", (t) => m.amc.map((a, i) => m.pesos.pastagem[t][i] / (a.area * 100)), true, CX.pct],
      veg: ["vegetação natural, % da área", (t) => m.amc.map((a, i) => m.pesos.veg_natural[t][i] / (a.area * 100)), true, CX.pct],
      boi: ["cabeças por km²", (t) => m.amc.map((a, i) => m.pesos.bovinos[t][i] / a.area), true, (v) => f(v, 0)],
    };
    const ctl = CX.ctrl(host);
    let k = "agric", ano = 2024;
    CX.seg(ctl, { opcoes: Object.entries(med).map(([kk, v]) => [kk, v[0].split(",")[0].replace(" média (Embrapa)", "")]), val: k, aoMudar: (v) => { k = v; des(); } });
    const sA = CX.slider(ctl, { rot: "ano", min: 1985, max: 2024, val: 2024, fmt: String, aoMudar: (v) => { ano = v; des(); } });
    const q = CX.quadro(host, { h: 280, m: { l: 60, r: 20, t: 20, b: 44 } });
    const txt = CX.frase(host);
    function des() {
      const [nome, fn, temporal, fm] = med[k];
      sA.el.style.opacity = temporal ? 1 : 0.35;
      const v = fn(ano - 1985);
      const w = m.amc.map((a) => a.area);
      const barras = d3.range(nF).map((j) => { const ids = faixa.map((x, i) => (x === j ? i : -1)).filter((i) => i >= 0); return { j, n: ids.length, v: d3.sum(ids, (i) => v[i] * w[i]) / d3.sum(ids, (i) => w[i]), l0: ext[0] + j * passo, l1: ext[0] + (j + 1) * passo }; });
      const x = d3.scaleBand().domain(barras.map((b2) => b2.j)).range([0, q.iw]).padding(0.15);
      const y = d3.scaleLinear().domain([k === "apt" ? 3.8 : 0, d3.max(barras, (b2) => b2.v) * 1.12]).range([q.ih, 0]);
      CX.eixos(q, x, y, { xf: (j) => `${f(-barras[j].l0, 1)}°–${f(-barras[j].l1, 1)}°S`, yf: (v) => fm(v), yl: nome + (temporal ? ` (${ano})` : "") });
      q.g.selectAll(".b").remove();
      q.g.append("text").attr("class", "b rot-m").attr("x", 0).attr("y", q.ih + 38).text("← Sul");
      q.g.append("text").attr("class", "b rot-m").attr("x", q.iw).attr("y", q.ih + 38).attr("text-anchor", "end").text("Norte →");
      barras.forEach((b2) => {
        q.g.append("rect").attr("class", "b").attr("x", x(b2.j)).attr("width", x.bandwidth()).attr("y", y(b2.v)).attr("height", q.ih - y(b2.v)).attr("rx", 3)
          .attr("fill", { apt: C.acento, agric: C.agric, pasto: C.pasto, veg: C.veg, boi: "#8a6d1c" }[k])
          .on("mousemove", (ev) => CX.tip.mostra(ev, `faixa ${f(-b2.l0, 1)}°–${f(-b2.l1, 1)}°S<br>${b2.n} AMCs<br>${fm(b2.v)}`)).on("mouseleave", CX.tip.esconde);
        q.g.append("text").attr("class", "b rot").attr("x", x(b2.j) + x.bandwidth() / 2).attr("y", y(b2.v) - 5).attr("text-anchor", "middle").text(fm(b2.v));
      });
      txt.innerHTML = `${nome}, média das AMCs em cada faixa de latitude, ponderada pela área. ` + (k === "apt" ? "A aptidão é estática: mede solo, clima e relevo, não o uso." : `Mova o ano e veja o perfil ${k === "veg" ? "esvaziar primeiro no sul" : "mudar"} ao longo do eixo.`);
    }
    des();
  });

  /* ---------------- 7.3 Teto de oferta ---------------- */
  CX.def("teto", (host) => {
    CX.modos(host, {
      simples(c) {
        const ctl = CX.ctrl(c);
        const sV = CX.slider(ctl, { rot: "vagas no estacionamento do shopping", min: 200, max: 900, passo: 50, val: 400, fmt: String, aoMudar: des });
        const sP = CX.slider(ctl, { rot: "procura no pico do fim da tarde (carros por hora)", min: 80, max: 400, passo: 20, val: 260, fmt: String, aoMudar: des });
        const ctl2 = CX.ctrl(c);
        let viz = false;
        CX.check(ctl2, " abrir o estacionamento do supermercado ao lado (outra fonte de vagas)", false, (v) => { viz = v; des(); });
        const q = CX.quadro(c, { h: 270, m: { l: 50, r: 16, t: 24, b: 40 } });
        const horas = d3.range(10, 23);
        const x = d3.scaleBand().domain(horas).range([0, q.iw]).padding(0.2);
        const g = q.g.append("g");
        const lei = CX.leitura(c);
        const nP = CX.num(lei, "carros querendo entrar às 18h"), nE = CX.num(lei, "carros que conseguiram entrar às 18h", true), nF = CX.num(lei, "fila na rua às 19h"), nZ = CX.num(lei, "atendidos no vizinho no dia");
        const txt = CX.frase(c);
        c.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:none;border:2px dashed #111"></i>carros querendo entrar</span><span><i style="background:${C.acento}"></i>entraram no shopping</span><span><i style="background:${C.pasto}"></i>foram para o vizinho</span><span><i style="background:${C.cinza}"></i>fila na rua</span>` }));
        function des() {
          const V = sV.valor(), pico = sP.valor(), VIZ = viz ? 150 : 0;
          const proc = horas.map((hh) => Math.round(50 + (pico - 50) * Math.exp(-(((hh - 18) / 2.2) ** 2))));
          let occ = 0, fila = 0, occV = 0; const ent = [], sai = [], vz = [], fl = [];
          horas.forEach((hh, k) => {
            const saem = k >= 2 ? ent[k - 2] : 0, saemV = k >= 2 ? vz[k - 2] : 0;
            occ -= saem; occV -= saemV;
            const quer = proc[k] + fila;
            const e = Math.min(quer, V - occ); occ += e;
            const ev = Math.min(quer - e, VIZ - occV); occV += ev;
            fila = quer - e - ev;
            ent.push(e); vz.push(ev); fl.push(fila); sai.push(saem);
          });
          const y = d3.scaleLinear().domain([0, Math.max(420, d3.max(proc) * 1.1, d3.max(fl) * 1.05)]).range([q.ih, 0]);
          CX.eixos(q, x, y, { xl: "hora do dia", yl: "carros por hora", xf: (hh) => hh + "h" });
          g.selectAll("*").remove();
          horas.forEach((hh, k) => {
            g.append("rect").attr("x", x(hh)).attr("width", x.bandwidth()).attr("y", y(ent[k])).attr("height", q.ih - y(ent[k])).attr("fill", C.acento).attr("rx", 2);
            if (vz[k] > 0) g.append("rect").attr("x", x(hh)).attr("width", x.bandwidth()).attr("y", y(ent[k] + vz[k])).attr("height", y(ent[k]) - y(ent[k] + vz[k])).attr("fill", C.pasto);
          });
          g.append("path").attr("fill", "none").attr("stroke", "#111").attr("stroke-width", 2).attr("stroke-dasharray", "5 3").attr("d", d3.line().x((_, k) => x(horas[k]) + x.bandwidth() / 2).y((v) => y(v))(proc));
          g.append("path").attr("fill", "none").attr("stroke", C.cinza).attr("stroke-width", 2.4).attr("d", d3.line().x((_, k) => x(horas[k]) + x.bandwidth() / 2).y((v) => y(v))(fl));
          const k18 = horas.indexOf(18), k19 = horas.indexOf(19);
          nP.set(String(proc[k18])); nE.set(String(ent[k18])); nF.set(String(fl[k19])); nZ.set(viz ? String(d3.sum(vz)) : "—");
          const kMax = ent.indexOf(d3.max(ent));
          txt.innerHTML = ent[k18] < proc[k18]
            ? `Às 18h, ${proc[k18]} carros querem entrar e só ${ent[k18]} conseguem: as vagas acabaram. As entradas caem justo quando a procura está no auge, e a fila cresce na rua. Quem olhasse só as entradas veria "menos interesse".` + (viz ? " Com o vizinho aberto, parte da procura é atendida por outra fonte de vagas, e a fila diminui." : " Abra o estacionamento vizinho e veja parte da procura ir para outra fonte.")
            : `Com ${V} vagas, a procura cabe: as entradas acompanham a procura a tarde inteira, com o pico às ${horas[kMax]}h. Diminua as vagas ou aumente a procura para ver o limite aparecer.`;
        }
        des();
      },

      async dados(c) {
        const D = (await CX.base()).decomp.find((d) => d.regiao === "Sul");
        const dFl = D.fluxo_III / D.fluxo_II - 1;
        const lin = [
          ["câmbio real efetivo (média do ato)", 169.0 / 134.5 - 1, C.azul, "demanda"],
          ["preço recebido pela soja", 186.4 / 104.4 - 1, C.azul, "demanda"],
          ["soja plantada, Goiás (IBGE)", 0.38, C.azul, "demanda"],
          ["Sul: taxa pasto → lavoura ou uso misto", 0.51, C.pasto, "fonte já aberta"],
          ["Sul: acréscimo anual de soja plantada", 2.44, C.pasto, "fonte já aberta"],
          ["Sul: fluxo de conversão do estoque exposto (#39)", dFl, C.veg, "Cerrado novo"],
        ];
        const q = CX.quadro(c, { h: 300, m: { l: 290, r: 70, t: 10, b: 36 } });
        const x = d3.scaleLinear().domain([-0.6, 2.6]).range([0, q.iw]), y = d3.scaleBand().domain(lin.map((l) => l[0])).range([0, q.ih]).padding(0.28);
        CX.eixos(q, x, null, { xf: (v) => CX.pct(v), xl: "variação do Ato II para o Ato III" });
        q.g.append("line").attr("class", "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", q.ih);
        lin.forEach(([n, v, cc]) => {
          q.g.append("rect").attr("x", x(Math.min(0, v))).attr("y", y(n)).attr("width", Math.abs(x(v) - x(0))).attr("height", y.bandwidth()).attr("fill", cc).attr("rx", 3);
          q.g.append("text").attr("class", "rot").attr("x", -8).attr("y", y(n) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(n);
          q.g.append("text").attr("class", "rot-f").attr("x", v >= 0 ? x(v) + 5 : x(0) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text(fs(100 * v, 0) + "%");
        });
        c.appendChild(h("div", { class: "cx-leg", html: `<span><i style="background:${C.azul}"></i>sinais de demanda</span><span><i style="background:${C.pasto}"></i>terra de fonte já aberta</span><span><i style="background:${C.veg}"></i>Cerrado ainda em pé</span>` }));
        const lei = CX.leitura(c);
        CX.num(lei, "estoque exposto que resta no estado (1985 = 100%)").set("≈ 60%");
        CX.num(lei, "do que resta, fora da proteção integral", true).set("97%");
        CX.num(lei, "queda do fluxo no Sul que é \"menos estoque\"").set(CX.pct(D.share_estoque));
        CX.frase(c, "Com os três sinais de demanda subindo, o Sul atendeu a demanda com terra já aberta e reduziu a conversão de Cerrado. O fluxo do #39 (estoque exposto, savana e campo) cai " + CX.pct(-dFl) + "; o texto, medindo a abertura de Cerrado novo, fala em queda pela metade. A terra que resta não está protegida por lei: o teto é físico.");
      },
    });
  });

  /* ---------------- 7.4 Carbono ---------------- */
  CX.def("carbono", async (host) => {
    const K = (await CX.base()).carbono.filter((k) => !k.formacao.startsWith("TOTAL"));
    const dens = K.map((k) => (k.mtco2 / k.mha) * (12 / 44)); // tC/ha, recuperado da tabela
    const area = K.map((k) => k.mha);
    const nomes = ["florestal", "savânica", "campestre", "alagada"];
    const cores = [C.veg, "#7fa65a", "#c2b56b", C.agua];
    const ctl = CX.ctrl(host);
    const sl = K.map((k, i) => CX.slider(ctl, { rot: `perda ${nomes[i]} (Mha)`, min: 0, max: Math.ceil(k.mha * 2 * 10) / 10, passo: 0.01, val: k.mha, fmt: (v) => f(v, 2), aoMudar: (v) => { area[i] = v; des(); } }));
    const ctl2 = CX.ctrl(host);
    let desc = false, mos = false;
    CX.check(ctl2, " descontar o estoque do uso entrante (emissão líquida)", false, (v) => { desc = v; des(); });
    CX.check(ctl2, " tratar o Mosaico como pastagem", false, (v) => { mos = v; des(); });
    CX.btn(ctl2, "voltar aos valores reais", () => { K.forEach((k, i) => { area[i] = k.mha; sl[i].set(k.mha, 1); }); des(); });
    const q = CX.quadro(host, { h: 150, m: { l: 130, r: 80, t: 10, b: 36 } });
    const tab = h("table", { class: "cx-tab" }); host.appendChild(tab);
    const lei = CX.leitura(host);
    const nT = CX.num(lei, "total", true), nR = CX.num(lei, "razão savânica / florestal"), nH = CX.num(lei, "1 ha de floresta vale … ha de savana");
    function des() {
      const mt = area.map((a, i) => a * dens[i] * (44 / 12));
      const tot0 = d3.sum(mt);
      // o desconto real (833/973) é quase uniforme por hectare; a convenção do Mosaico leva a 815
      const fator = desc ? (mos ? 815 / 973.27 : 833 / 973.27) : 1;
      const mtD = mt.map((v) => v * fator);
      const x = d3.scaleLinear().domain([0, 1200]).range([0, q.iw]);
      CX.eixos(q, x, null, { xl: "Mt CO₂e", xt: 6, xf: (v) => f(v, 0) });
      q.g.selectAll(".b").remove();
      let acc = 0;
      mtD.forEach((v, i) => {
        q.g.append("rect").attr("class", "b").attr("x", x(acc) + 1).attr("y", 14).attr("width", Math.max(0, x(v) - x(0) - 2)).attr("height", 60).attr("fill", cores[i])
          .on("mousemove", (ev) => CX.tip.mostra(ev, `${nomes[i]}: ${f(v, 0)} Mt<br>${f(area[i], 2)} Mha × ${f(dens[i], 2)} tC/ha × 44/12`)).on("mouseleave", CX.tip.esconde);
        if (v > 60) q.g.append("text").attr("class", "b rot").attr("x", x(acc + v / 2)).attr("y", 49).attr("text-anchor", "middle").style("fill", "#fff").style("font-weight", 700).text(nomes[i]);
        acc += v;
      });
      q.g.append("text").attr("class", "b rot-f").attr("x", x(acc) + 6).attr("y", 49).text(f(acc, 0) + " Mt");
      q.g.append("text").attr("class", "b rot-m").attr("x", -8).attr("y", 49).attr("text-anchor", "end").text(desc ? "emissão líquida" : "estoque removido");
      tab.innerHTML = "<tr><th>formação</th><th>densidade (tC/ha)</th><th>área perdida (Mha)</th><th>Mt CO₂e</th></tr>" +
        K.map((k, i) => `<tr><td>${k.formacao}</td><td>${f(dens[i], 2)}</td><td>${f(area[i], 2)}</td><td>${f(mtD[i], 1)}</td></tr>`).join("");
      nT.set(f(acc, 0) + " Mt" + (desc ? ` (${fs(100 * (acc / tot0 - 1), 1)}%)` : ""));
      nR.set(f(mtD[1] / mtD[0], 2));
      nH.set(f(dens[0] / dens[1], 2));
    }
    des();
    const qa = CX.quadro(host, { h: 190, m: { l: 90, r: 70, t: 24, b: 34 } });
    const atos = [["Ato I", 48.1], ["Ato II", 9.7], ["Ato III", 11.8]];
    const x = d3.scaleLinear().domain([0, 55]).range([0, qa.iw]), y = d3.scaleBand().domain(atos.map((a) => a[0])).range([0, qa.ih]).padding(0.3);
    CX.eixos(qa, x, y, { xl: "estoque removido por ano (Mt CO₂e/ano)", grade: false });
    qa.g.append("text").attr("class", "rot-f").attr("y", -10).text("o ritmo por ato");
    atos.forEach(([n, v]) => {
      qa.g.append("rect").attr("y", y(n)).attr("height", y.bandwidth()).attr("width", x(v)).attr("fill", C.acento).attr("rx", 3);
      qa.g.append("text").attr("class", "rot-f").attr("x", x(v) + 5).attr("y", y(n) + y.bandwidth() / 2 + 4).text(f(v, 1));
    });
    CX.frase(host, "Com as áreas reais, a savânica responde por mais carbono que a florestal, embora cada hectare dela valha menos: é a área perdida (2,6 vezes maior) que decide. Iguale as áreas nos controles e a ordem se inverte. O desconto do uso entrante é aplicado aqui como fator médio (833/973), porque no trabalho ele é quase uniforme por hectare. No tempo, três quartos do estoque saíram no Ato I; o Sul foi quem removeu cedo.");
  });
})();
