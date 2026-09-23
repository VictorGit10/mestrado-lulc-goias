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
      dados(c) {
        const linhas = [
          ["Empurrão", "o passado da lavoura do Sul prevê o pasto do Norte", "0 de 24 combinações com p < 0,05 (Granger, #34)", "não aparece"],
          ["Empurrão", "sob método robusto a séries integradas, alguma direção lidera", "Toda-Yamamoto: p = 0,25 (Sul→Norte) e 0,45 (Norte→Sul)", "sem líder"],
          ["Empurrão", "lavoura nos vizinhos ao sul vem com mais pasto local", "12 de 12 estimativas negativas; a única com p < 0,05 tem o sinal oposto", "sinal oposto"],
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
      CX.eixos(q, x, y, { xf: (j) => `${f(-barras[j].l0, 1)}°–${f(-barras[j].l1, 1)}°S`, yf: fm, yl: nome + (temporal ? ` (${ano})` : "") });
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
        const sD = CX.slider(ctl, { rot: "fregueses por minuto", min: 1, max: 10, val: 7, fmt: String });
        const sO = CX.slider(ctl, { rot: "pães do forno por minuto", min: 1, max: 10, val: 4, fmt: String });
        const ctl2 = CX.ctrl(c);
        let ontem = false;
        CX.check(ctl2, " vender também o pão de ontem (outra fonte)", false, (v) => { ontem = v; });
        CX.btn(ctl2, "recomeçar", () => { fila = 0; hist.length = 0; });
        const q = CX.quadro(c, { h: 230, m: { l: 44, r: 100, t: 14 } });
        const x = d3.scaleLinear().domain([0, 150]).range([0, q.iw]), y = d3.scaleLinear().domain([0, 100]).range([q.ih, 0]);
        CX.eixos(q, x, y, { xl: "tempo", yl: "pessoas na fila" });
        const ln = q.g.append("path").attr("fill", "none").attr("stroke", C.acento).attr("stroke-width", 2.4);
        const lei = CX.leitura(c);
        const nF = CX.num(lei, "fila agora", true), nA = CX.num(lei, "atendidos por minuto");
        let fila = 0, t0 = null; const hist = [];
        return CX.loop((t) => {
          if (t0 == null) t0 = t;
          if (t - t0 < 120) return; t0 = t;
          const at = Math.min(fila + sD.valor(), sO.valor() + (ontem ? 3 : 0));
          fila = Math.max(0, Math.min(100, fila + sD.valor() - at));
          hist.push(fila); if (hist.length > 150) hist.shift();
          ln.attr("d", d3.line().x((_, i) => x(i)).y((v) => y(v))(hist));
          nF.set(String(Math.round(fila))); nA.set(String(at));
        });
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
    const q = CX.quadro(host, { h: 230, m: { l: 130, r: 80, t: 10, b: 36 } });
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
      CX.eixos(q, x, null, { xl: "Mt CO₂e", xt: 6 });
      q.g.selectAll(".b").remove();
      let acc = 0;
      mtD.forEach((v, i) => {
        q.g.append("rect").attr("class", "b").attr("x", x(acc) + 1).attr("y", 40).attr("width", Math.max(0, x(v) - x(0) - 2)).attr("height", 60).attr("fill", cores[i])
          .on("mousemove", (ev) => CX.tip.mostra(ev, `${nomes[i]}: ${f(v, 0)} Mt<br>${f(area[i], 2)} Mha × ${f(dens[i], 2)} tC/ha × 44/12`)).on("mouseleave", CX.tip.esconde);
        if (v > 60) q.g.append("text").attr("class", "b rot").attr("x", x(acc + v / 2)).attr("y", 75).attr("text-anchor", "middle").style("fill", "#fff").style("font-weight", 700).text(nomes[i]);
        acc += v;
      });
      q.g.append("text").attr("class", "b rot-f").attr("x", x(acc) + 6).attr("y", 75).text(f(acc, 0) + " Mt");
      q.g.append("text").attr("class", "b rot-m").attr("x", -8).attr("y", 75).attr("text-anchor", "end").text(desc ? "emissão líquida" : "estoque removido");
      tab.innerHTML = "<tr><th>formação</th><th>densidade (tC/ha)</th><th>área perdida (Mha)</th><th>Mt CO₂e</th></tr>" +
        K.map((k, i) => `<tr><td>${k.formacao}</td><td>${f(dens[i], 2)}</td><td>${f(area[i], 2)}</td><td>${f(mtD[i], 0)}</td></tr>`).join("");
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
