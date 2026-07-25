/* pastagem-reserva.js — Sub-pipeline #28-C.
 *
 * Enriquece o bloco §6 ("Pastagem como reserva de terra") com dois elementos
 * interativos (progressive enhancement — sem d3/JS, a figura estática assume):
 *   1. Mapa das AMCs pela COEXISTÊNCIA dos dois mecanismos (bimodalidade da
 *      idade na conversão) — 162 de 164 AMCs são bimodais por dentro. O mapa é
 *      quase uniforme de propósito: é a forma visual de "a geografia explica
 *      quase nada" (η² da mesorregião = 0,5% sob a união).
 *   2. Histograma por REGIÃO com toggle (mesorregiões + estado), mostrando que
 *      os dois picos aparecem dentro de cada recorte.
 *
 * ⚠️ MUDANÇA DE 25/jul/2026 — o que este arquivo NÃO faz mais.
 * A versão anterior pintava as AMCs pela **idade média** da pastagem na
 * conversão e anunciava "gradiente Sul→Norte nítido: jovem no Sul, antigo no
 * Norte". Esse gradiente é **artefato** da mudança de rótulo do Mosaico (#28D /
 * D26): a idade é medida só entre os pixels cujo destino foi rotulado
 * "agricultura", e no fim da série esse rótulo migra para "Mosaico de Usos".
 * Sob `pasto→(agric∪mosaico)` a amplitude Sul→Norte cai de 7a para 2a e a
 * ordenação embaralha — três testes independentes (#28C, #40, #33) chegaram à
 * mesma conclusão. Pior: os valores desenhados vinham da **amostra** de 43.951
 * px (arquivo órfão), sob uma seção que anuncia o censo de 44,6 milhões.
 * Agora a geometria vem de `malha_amc.geojson` (gerado por
 * `scripts/export_malha_amc_viz.py`, só identidade) e todos os números vêm do
 * censo, em tempo de execução.
 *
 * Vanilla + d3 v7 (já carregado). Namespace: window.GO40.reserva.
 */
(function (root) {
  "use strict";

  const COR_BIMODAL = "#8b3a1d";  // terracota — os dois mecanismos coexistem
  const COR_UNIMODAL = "#d4b65a"; // amarelo pastagem — um modo só
  const COR_SEM = "#e6e3dc";      // sem ajuste (n < 100)

  // Cores dos dois modos no histograma (mantidas do desenho anterior: a
  // linguagem "jovem × antigo" continua válida DENTRO de cada distribuição —
  // o que caiu foi lê-la no mapa, entre regiões).
  const COR_JOVEM = "#e8920c";
  const COR_ANTIGO = "#2e7d32";
  const CORTE_MODO = 12;          // anos: fronteira visual entre os dois modos

  let REG = null;   // idade_pastagem_regional.json (censo)

  function fmtN(v) {
    return (root.GO40 && root.GO40.fmt && root.GO40.fmt.num)
      ? root.GO40.fmt.num(v) : String(v);
  }

  function fmtPct(v, casas) {
    return (v * 100).toFixed(casas == null ? 0 : casas).replace(".", ",") + "%";
  }

  function tooltip() {
    let el = document.getElementById("reserva-tooltip");
    if (!el) {
      el = document.createElement("div");
      el.id = "reserva-tooltip";
      el.className = "reserva-tooltip";
      el.hidden = true;
      document.body.appendChild(el);
    }
    return el;
  }

  // ---- 1. Mapa da coexistência (AMC) ----
  function celulaAmc(code) {
    const r = REG && REG.amc && REG.amc.regioes["AMC " + code];
    return r ? r.todos : null;
  }

  function corCelula(c) {
    if (!c || c.bimodal == null) return COR_SEM;
    return c.bimodal ? COR_BIMODAL : COR_UNIMODAL;
  }

  function desenharMapa(geo) {
    const cont = d3.select("#reserva-mapa");
    cont.selectAll("*").remove();
    const W = 460, H = 420;
    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("class", "reserva-svg");

    const proj = d3.geoMercator().fitSize([W, H - 8], geo);
    const path = d3.geoPath(proj);
    const tip = tooltip();

    svg.append("g").selectAll("path")
      .data(geo.features)
      .join("path")
      .attr("d", path)
      .attr("fill", d => corCelula(celulaAmc(d.properties.code_amc)))
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.4)
      .attr("tabindex", 0)
      .attr("role", "listitem")
      .on("pointerenter focus", function (ev, d) {
        d3.select(this).attr("stroke", "#222").attr("stroke-width", 1.2).raise();
        const p = d.properties;
        const c = celulaAmc(p.code_amc);
        let corpo;
        if (!c || c.bimodal == null) {
          corpo = "sem ajuste (poucos eventos de idade conhecida)";
        } else if (c.bimodal) {
          corpo = `<strong>bimodal</strong> — modos em ${c.gmm.mu_jovem.toString().replace(".", ",")}a ` +
            `(${fmtPct(c.gmm.w_jovem)}) e ${c.gmm.mu_velho.toString().replace(".", ",")}a ` +
            `(${fmtPct(c.gmm.w_velho)})<br>${fmtN(c.n)} eventos de idade conhecida`;
        } else {
          corpo = `<strong>unimodal</strong><br>${fmtN(c.n)} eventos de idade conhecida`;
        }
        tip.hidden = false;
        tip.innerHTML = `<strong>AMC ${p.code_amc}</strong>` +
          (p.mesorregiao ? `<br>${p.mesorregiao}` : "") + `<br>${corpo}`;
      })
      .on("pointermove", ev => {
        tip.style.left = (ev.clientX + 14) + "px";
        tip.style.top = (ev.clientY + 14) + "px";
      })
      .on("pointerleave blur", function () {
        d3.select(this).attr("stroke", "#fff").attr("stroke-width", 0.4);
        tip.hidden = true;
      });

    desenharLegenda(geo);
  }

  // Conta sobre as feições DESENHADAS, não sobre o JSON: a malha tem 166 AMCs e o
  // censo ajusta 164 (duas ficam sem eventos suficientes). Contar pelo JSON
  // esconderia justamente as células cinza do mapa.
  function contagemAmc(geo) {
    let bimodal = 0, unimodal = 0, sem = 0;
    geo.features.forEach(f => {
      const c = celulaAmc(f.properties.code_amc);
      const b = c && c.bimodal;
      if (b === true) bimodal++; else if (b === false) unimodal++; else sem++;
    });
    return { bimodal, unimodal, sem, total: geo.features.length };
  }

  function desenharLegenda(geo) {
    const cont = d3.select("#reserva-mapa-legenda");
    cont.selectAll("*").remove();
    const n = contagemAmc(geo);
    const itens = [
      [COR_BIMODAL, `bimodal — os dois mecanismos (${n.bimodal})`],
      [COR_UNIMODAL, `um modo só (${n.unimodal})`]
    ];
    if (n.sem) itens.push([COR_SEM, `poucos eventos para ajustar (${n.sem})`]);

    const lista = cont.append("ul").attr("class", "reserva-legenda-lista");
    itens.forEach(([cor, txt]) => {
      const li = lista.append("li");
      li.append("span").attr("class", "reserva-legenda-chip").style("background", cor);
      li.append("span").text(txt);
    });
  }

  // ---- 2. Histograma por região ----
  let ORDEM = [];        // rótulos das regiões, na ordem do toggle
  let regiaoAtiva = 0;   // começa em "Goiás (estado)"

  function ordemRegioes() {
    const meso = (REG && REG.mesorregiao) || { ordem: [] };
    // A `ordem` do JSON vem classificada pela mediana da idade (jovem→velho) —
    // exatamente a leitura que a auditoria de 25/jul refutou. Aqui o estado vem
    // primeiro e as mesorregiões em ordem alfabética, para que a sequência dos
    // botões não sugira um gradiente.
    const estado = meso.ordem.filter(r => r.indexOf("Goiás") === 0);
    const resto = meso.ordem.filter(r => r.indexOf("Goiás") !== 0)
      .sort((a, b) => a.localeCompare(b, "pt-BR"));
    return estado.concat(resto);
  }

  function celulaRegiao(rot) {
    const r = REG.mesorregiao.regioes[rot];
    return r ? r.todos : null;
  }

  function desenharToggle() {
    const cont = d3.select("#reserva-regiao-toggle");
    cont.selectAll("*").remove();
    ORDEM.forEach((rot, i) => {
      cont.append("button")
        .attr("type", "button")
        .attr("role", "tab")
        .attr("aria-selected", i === regiaoAtiva ? "true" : "false")
        .attr("class", "reserva-tab" + (i === regiaoAtiva ? " reserva-tab--ativo" : ""))
        .text(rot.replace(" Goiano", "").replace("Goiás (estado)", "Goiás"))
        .on("click", () => { regiaoAtiva = i; desenharToggle(); desenharHist(); });
    });
  }

  function desenharHist() {
    const rot = ORDEM[regiaoAtiva];
    const c = celulaRegiao(rot);
    const cont = d3.select("#reserva-hist");
    cont.selectAll("*").remove();
    if (!c) return;

    const bins = REG.meta.bins;
    const W = 460, H = 300, M = { t: 12, r: 12, b: 34, l: 44 };
    const svg = cont.append("svg").attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet").attr("class", "reserva-svg");

    const centros = c.counts.map((_, i) => (bins[i] + bins[i + 1]) / 2);
    const x = d3.scaleLinear().domain([0, 40]).range([M.l, W - M.r]);
    const y = d3.scaleLinear().domain([0, d3.max(c.counts) * 1.08]).range([H - M.b, M.t]);
    const bw = (x(2) - x(0)) * 0.86;

    svg.append("g").attr("transform", `translate(0,${H - M.b})`)
      .call(d3.axisBottom(x).ticks(8).tickFormat(d => d + "a"))
      .attr("class", "reserva-eixo");
    svg.append("g").attr("transform", `translate(${M.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d3.format("~s")(d)))
      .attr("class", "reserva-eixo");

    svg.append("g").selectAll("rect")
      .data(c.counts).join("rect")
      .attr("x", (d, i) => x(centros[i]) - bw / 2)
      .attr("y", d => y(d))
      .attr("width", bw)
      .attr("height", d => (H - M.b) - y(d))
      .attr("fill", (d, i) => centros[i] < CORTE_MODO ? COR_JOVEM : COR_ANTIGO)
      .attr("opacity", 0.9);

    if (c.mediana != null) {
      svg.append("line")
        .attr("x1", x(c.mediana)).attr("x2", x(c.mediana))
        .attr("y1", M.t).attr("y2", H - M.b)
        .attr("stroke", "#222").attr("stroke-dasharray", "4 3").attr("stroke-width", 1.2);
      svg.append("text").attr("x", x(c.mediana) + 4).attr("y", M.t + 10)
        .attr("class", "reserva-hist-med")
        .text(`mediana ${c.mediana.toString().replace(".", ",")} a`);
    }

    if (c.bimodal) {
      svg.append("text").attr("x", W - M.r).attr("y", M.t + 10)
        .attr("text-anchor", "end").attr("class", "reserva-hist-nota-svg")
        .text("dois modos = dois mecanismos");
    }

    const nota = document.getElementById("reserva-hist-nota");
    if (nota) {
      const cens = c.n_censurado / (c.n + c.n_censurado);
      const veredito = c.bimodal
        ? `<strong>bimodal</strong> (modos em ${c.gmm.mu_jovem.toString().replace(".", ",")}a e ` +
          `${c.gmm.mu_velho.toString().replace(".", ",")}a, ΔBIC ${fmtN(Math.round(c.gmm.delta_bic))})`
        : "<strong>unimodal</strong>";
      nota.innerHTML = `<strong>${rot}</strong>, série inteira (1986–2024): ${veredito}. ` +
        `${fmtN(c.n)} eventos de idade conhecida; outros ${fmtN(c.n_censurado)} (${fmtPct(cens)}) ` +
        `já eram pastagem em 1985 e ficam de fora. Os modos aqui são mais baixos que os dos cards ` +
        `abaixo porque a série inteira mistura horizontes — um pixel convertido em 1995 não podia ` +
        `ter mais de 10 anos. <em>Não compare a mediana entre regiões</em>: ela é medida só dentro ` +
        `do rótulo "agricultura", e é exatamente essa comparação que a auditoria de jul/2026 derrubou.`;
    }
  }

  // ---- 3. Cards do GMM (janela 2016–2024, censo) ----
  const JANELA_CARDS = "2016–2024";

  function preencherCards(gmm) {
    if (!Array.isArray(gmm)) return;
    const j = gmm.find(g => g.janela === JANELA_CARDS);
    if (!j) return;
    const um = (v, casas) => v.toFixed(casas).replace(".", ",");
    const alvos = [
      ["reserva-card-jovem", j.mu1, j.sig1, j.w1],
      ["reserva-card-antigo", j.mu2, j.sig2, j.w2]
    ];
    alvos.forEach(([id, mu, sig, w]) => {
      const el = document.getElementById(id);
      if (!el) return;
      const valor = el.querySelector("[data-campo='valor']");
      const peso = el.querySelectorAll("[data-campo='peso']");
      const sigma = el.querySelectorAll("[data-campo='sigma']");
      if (valor) valor.textContent = `μ ≈ ${um(mu, 1)} a (${fmtPct(w, 1)})`;
      peso.forEach(n => { n.textContent = fmtPct(w, 1); });
      sigma.forEach(n => { n.textContent = um(sig, 1); });
    });
    const n = document.getElementById("reserva-cards-n");
    if (n) n.textContent = fmtN(j.n_nao_censurado);
  }

  // ---- 4. Nota de cobertura (censo municipal) ----
  function preencherCobertura(muni) {
    const el = document.getElementById("reserva-cobertura");
    if (!el || !Array.isArray(muni) || !muni.length) return;
    const min = muni.reduce((m, r) => Math.min(m, r.n_pixels), Infinity);
    el.innerHTML = `Cobertura do censo: <strong>${muni.length} municípios</strong>, e o menor ` +
      `deles tem <strong>${fmtN(min)}</strong> eventos de idade conhecida. Na amostra anterior, ` +
      `44% dos municípios tinham menos de 20 — a mediana municipal era ruído.`;
  }

  // d3 é carregado lazy (mesmo vendor do sankey.js) — não é global no load.
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src; s.onload = resolve;
      s.onerror = () => reject(new Error("Falha ao carregar: " + src));
      document.head.appendChild(s);
    });
  }

  async function garantirD3() {
    if (root.d3 && root.d3.geoPath) return;
    await loadScript("assets/js/vendor/d3.v7.min.js?v=2");
  }

  let montado = false;
  async function montar(bloco) {
    if (montado) return;
    montado = true;
    try {
      await garantirD3();
      const [geo, regional, gmm, muni] = await Promise.all([
        d3.json("assets/data/malha_amc.geojson"),
        d3.json("assets/data/idade_pastagem_regional.json"),
        d3.json("assets/data/idade_pastagem_gmm.json"),
        d3.json("assets/data/idade_pastagem_municipal.json")
      ]);
      if (!geo || !regional) return;
      REG = regional;
      ORDEM = ordemRegioes();
      bloco.hidden = false;          // revela só quando os dados chegam
      desenharMapa(geo);
      desenharToggle();
      desenharHist();
      preencherCards(gmm);
      preencherCobertura(muni);
    } catch (err) {
      montado = false;               // permite nova tentativa
      console.warn("[reserva] falha ao montar", err);
    }
  }

  function init() {
    const bloco = document.getElementById("reserva-interativo");
    if (!bloco) return;
    // Observa o bloco-pai VISÍVEL (#reserva-interativo começa hidden = tamanho 0).
    const alvo = document.getElementById("sec-idade-pastagem") || bloco;
    if (typeof IntersectionObserver === "undefined") { montar(bloco); return; }
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { montar(bloco); obs.disconnect(); }
      });
    }, { rootMargin: "300px 0px" });
    obs.observe(alvo);
  }

  root.GO40 = root.GO40 || {};
  root.GO40.reserva = { init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
