/* reserva-perna2.js — peça-central da Perna 2 (família #28 / #28C).
 *
 * A pergunta que a peça responde: "os dois mecanismos de conversão de pastagem
 * estão em regiões diferentes do estado, ou coexistem em toda parte?"
 *
 * Dois painéis que conversam:
 *   1. MAPA — 166 AMCs pintadas pelo VEREDITO de bimodalidade (não pela idade:
 *      ver a nota histórica abaixo). O mapa é quase todo de uma cor de
 *      propósito — é a forma visual de "a geografia explica quase nada"
 *      (η² da mesorregião sobre a idade = 0,5% sob a régua da união, #28C).
 *      Por cima, o contorno das 5 mesorregiões: é ELE o alvo de clique.
 *   2. HISTOGRAMA da região selecionada, com as duas componentes ajustadas
 *      desenhadas por cima e — a peça do argumento — o melhor ajuste de UMA
 *      população só, tracejado, para o leitor ver onde ele falha.
 *
 * ⚠️ MUDANÇA DE 28/jul/2026 (2ª) — a peça passou a desenhar as DUAS RÉGUAS.
 * Ela mostrava só `pasto→agricultura`, exposta à mudança de rótulo do Mosaico,
 * enquanto a copy ao lado afirmava a conclusão obtida sob a UNIÃO. A revisão do
 * autor pegou a contradição a olho: no que estava desenhado, Norte e Noroeste
 * são visivelmente mais bimodais que Sul e Centro. Medido
 * (`forma_regional_bimodalidade.py`), o olho tinha razão — e a diferença é o
 * artefato: a profundidade do vale no Noroeste cai de 0,415 para 0,058 e a
 * distância entre as formas de Sul e Norte cai de 0,223 para 0,023 quando se
 * fecha o buraco de rotulagem. Desenhar só a exposta contradiz o texto;
 * desenhar só a imune esconde a evidência da auditoria. Desenha as duas, com a
 * imune por padrão, e a troca É o argumento.
 *
 * ⚠️ MUDANÇA DE 28/jul/2026 — o clique saiu dos botões e foi para o mapa.
 * Até aqui a peça tinha um mapa por AMC e, ao lado, uma fileira de 6 pastilhas
 * por mesorregião. Duas malhas sem relação visível: o leitor não tinha como
 * saber que a pastilha "Norte" correspondia àquele pedaço do mapa. Agora o
 * contorno das mesorregiões (`malha_mesorregiao.geojson`) vive sobre as AMCs e
 * recebe o clique — a resolução fina continua desenhada por baixo, que é o que
 * sustenta o "162 de 164 AMCs".
 *
 * ⚠️ MUDANÇA DE 25/jul/2026 — o que este arquivo NÃO faz.
 * A versão anterior pintava as AMCs pela **idade média** da pastagem na
 * conversão e anunciava "gradiente Sul→Norte nítido: jovem no Sul, antigo no
 * Norte". Esse gradiente é **artefato** da mudança de rótulo do Mosaico (#28D /
 * D26): a idade é medida só entre os pixels cujo destino foi rotulado
 * "agricultura", e no fim da série esse rótulo migra para "Mosaico de Usos".
 * Sob `pasto→(agric∪mosaico)` a amplitude Sul→Norte cai de 7a para 2a e a
 * ordenação embaralha — três testes independentes (#28C, #40, #33) chegaram à
 * mesma conclusão. Não repintar idade nesta malha.
 *
 * ⚠️ FORK DELIBERADO de `pastagem-reserva.js` (28/jul/2026). O módulo antigo
 * continua servindo o `index.html` que está no ar — ele tem outra marcação (uma
 * fileira de pastilhas, três cards de coorte) e a reforma mudou o desenho da
 * interação, não só o estilo. Fundir os dois numa versão que detecta marcação
 * daria um módulo com dois comportamentos para conviver poucos dias: pela
 * estratégia de arquivo paralelo do PLANO_DE_CONSTRUCAO, `index.html` fica
 * intocado até a troca. **Na troca, `pastagem-reserva.js` é apagado junto com
 * o `index.html` antigo.**
 *
 * Vanilla + d3 v7 (lazy). Namespace: window.GO40.reservaPerna2.
 */
(function (root) {
  "use strict";

  const COR_BIMODAL = "#8b3a1d";  // terracota — as duas populações coexistem
  const COR_UNIMODAL = "#d4b65a"; // amarelo pastagem — uma população só
  const COR_SEM = "#e6e3dc";      // sem ajuste (n < 100)

  const COR_JOVEM = "#e8920c";    // componente jovem (rotação)
  const COR_ANTIGO = "#2e7d32";   // componente velha (reserva)
  const COR_UMA = "#8b3a1d";      // o ajuste de UMA população — a hipótese nula

  const ESTADO = "Goiás (estado)";

  // `uniao` é o padrão: é a régua imune à reetiquetagem, e é a única sob a qual
  // a afirmação "o desenho é o mesmo nas cinco regiões" se sustenta.
  const REGUA_PADRAO = "uniao";

  let DADOS = null;       // idade_pastagem_bracket.json (as duas réguas)
  let reguaAtiva = REGUA_PADRAO;
  let regiaoAtiva = ESTADO;
  let redesenharMapa = null;   // fechado sobre a seleção; setado em desenharMapa

  function fmtN(v) {
    return (root.GO40 && root.GO40.fmt && root.GO40.fmt.num)
      ? root.GO40.fmt.num(v) : String(v);
  }

  const vg = v => String(v).replace(".", ",");
  const fmtPct = (v, casas) =>
    (v * 100).toFixed(casas == null ? 0 : casas).replace(".", ",") + "%";

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

  function bloco() {
    return (DADOS && DADOS.reguas && DADOS.reguas[reguaAtiva]) || null;
  }

  function celulaAmc(code) {
    const b = bloco();
    return (b && b.amc["AMC " + code]) || null;
  }

  function celulaRegiao(rot) {
    const b = bloco();
    return (b && b.mesorregiao[rot]) || null;
  }

  function corCelula(c) {
    if (!c || c.bimodal == null) return COR_SEM;
    return c.bimodal ? COR_BIMODAL : COR_UNIMODAL;
  }

  function selecionar(rot) {
    if (rot === regiaoAtiva) return;
    regiaoAtiva = rot;
    if (redesenharMapa) redesenharMapa();
    desenharHist();
    const btn = document.getElementById("reserva-reset");
    if (btn) btn.hidden = (regiaoAtiva === ESTADO);
  }

  // ---- 0. Troca de régua (D26) ----
  // Trocar a régua redesenha TUDO: o veredito de cada AMC muda (166/166 sob a
  // união, 162/164 sob a exposta) e a forma do histograma também. É a única
  // interação da peça que altera os dois painéis ao mesmo tempo — de propósito,
  // porque o argumento é justamente que as duas coisas mudam juntas.
  function trocarRegua(nome) {
    if (nome === reguaAtiva || !DADOS.reguas[nome]) return;
    reguaAtiva = nome;
    document.querySelectorAll("[data-regua]").forEach(b => {
      const ativo = b.dataset.regua === nome;
      b.classList.toggle("is-ativo", ativo);
      b.setAttribute("aria-pressed", ativo ? "true" : "false");
    });
    const aviso = document.getElementById("reserva-regua-aviso");
    if (aviso) aviso.hidden = (nome === "uniao");
    if (redesenharVeredito) redesenharVeredito();
    desenharHist();
  }

  let redesenharVeredito = null;   // setado em desenharMapa

  // ---- 1. Mapa: AMCs pelo veredito + mesorregiões como alvo de clique ----
  function desenharMapa(geoAmc, geoMeso) {
    const cont = d3.select("#reserva-mapa");
    cont.selectAll("*").remove();
    const W = 460, H = 420;
    const svg = cont.append("svg")
      .attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("class", "reserva-svg");

    // A projeção é ajustada à malha de AMC e REUSADA no contorno das
    // mesorregiões — ajustar cada uma à sua própria extensão desalinharia as
    // duas camadas (as 2 AMCs sem mesorregião mudam o bounding box).
    const proj = d3.geoMercator().fitSize([W, H - 8], geoAmc);
    const path = d3.geoPath(proj);
    const tip = tooltip();

    const gAmc = svg.append("g").attr("class", "reserva-amcs");
    const amcs = gAmc.selectAll("path")
      .data(geoAmc.features)
      .join("path")
      .attr("d", path)
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.4);

    redesenharVeredito = function () {
      amcs.attr("fill", d => corCelula(celulaAmc(d.properties.code_amc)));
      desenharLegenda(geoAmc);
    };

    // Camada de clique. `fill: transparent` (não `none`) para que o polígono
    // inteiro receba o ponteiro, não só o traço.
    const gMeso = svg.append("g").attr("class", "reserva-mesos");
    const mesos = gMeso.selectAll("path")
      .data(geoMeso.features)
      .join("path")
      .attr("d", path)
      .attr("fill", "transparent")
      .attr("class", "reserva-meso")
      .attr("tabindex", 0)
      .attr("role", "button")
      .attr("aria-label", d => `Ver a distribuição de ${d.properties.mesorregiao}`)
      .on("pointerenter focus", function (ev, d) {
        d3.select(this).classed("is-hover", true);
        const rot = d.properties.mesorregiao;
        const c = celulaRegiao(rot);
        const amcs = geoAmc.features.filter(f => f.properties.mesorregiao === rot);
        const nBi = amcs.filter(f => {
          const cc = celulaAmc(f.properties.code_amc);
          return cc && cc.bimodal;
        }).length;
        tip.hidden = false;
        tip.innerHTML = `<strong>${rot}</strong><br>` +
          (c ? `${fmtN(c.n)} conversões de idade conhecida<br>` : "") +
          `${nBi} de ${amcs.length} AMCs bimodais por dentro<br>` +
          `<em>clique para ver a distribuição</em>`;
      })
      .on("pointermove", ev => {
        tip.style.left = (ev.clientX + 14) + "px";
        tip.style.top = (ev.clientY + 14) + "px";
      })
      .on("pointerleave blur", function () {
        d3.select(this).classed("is-hover", false);
        tip.hidden = true;
      })
      .on("click", (ev, d) => selecionar(d.properties.mesorregiao))
      .on("keydown", (ev, d) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          selecionar(d.properties.mesorregiao);
        }
      });

    // Véu sobre o que NÃO está selecionado. Ausente quando a seleção é o estado
    // inteiro — assim a vista padrão mostra o mapa sem nenhuma interferência, que
    // é justamente onde o "quase tudo da mesma cor" precisa ser lido.
    const gVeu = svg.append("g").attr("class", "reserva-veu")
      .attr("pointer-events", "none");
    gVeu.selectAll("path")
      .data(geoMeso.features)
      .join("path")
      .attr("d", path)
      .attr("fill", "#faf9f6");

    redesenharMapa = function () {
      mesos.classed("is-ativo", d => d.properties.mesorregiao === regiaoAtiva);
      gVeu.selectAll("path")
        .attr("opacity", d => (regiaoAtiva === ESTADO ||
                               d.properties.mesorregiao === regiaoAtiva) ? 0 : 0.62);
    };
    redesenharMapa();
    redesenharVeredito();
  }

  // Conta sobre as feições DESENHADAS, não sobre o JSON: a malha tem 166 AMCs, e
  // sob a régua exposta o censo só ajusta 164 (duas ficam sem eventos
  // suficientes). Contar pelo JSON esconderia justamente as células cinza.
  function contagemAmc(geo) {
    let bimodal = 0, unimodal = 0, sem = 0;
    geo.features.forEach(f => {
      const c = celulaAmc(f.properties.code_amc);
      const b = c && c.bimodal;
      if (b === true) bimodal++; else if (b === false) unimodal++; else sem++;
    });
    return { bimodal, unimodal, sem, total: geo.features.length };
  }

  function itemLegenda(li, cor, txt, tracejado) {
    const chip = li.append("span").attr("class", "reserva-legenda-chip");
    if (tracejado) chip.attr("class", "reserva-legenda-chip reserva-legenda-chip--linha")
      .style("border-color", cor);
    else chip.style("background", cor);
    li.append("span").text(txt);
  }

  function desenharLegenda(geo) {
    const cont = d3.select("#reserva-mapa-legenda");
    cont.selectAll("*").remove();
    const n = contagemAmc(geo);
    const itens = [
      [COR_BIMODAL, `as duas populações convivem ali dentro (${n.bimodal} de ${n.total})`],
    ];
    if (n.unimodal) itens.push([COR_UNIMODAL, `uma população só (${n.unimodal})`]);
    if (n.sem) itens.push([COR_SEM, `poucas conversões para ajustar (${n.sem})`]);

    const lista = cont.append("ul").attr("class", "reserva-legenda-lista");
    itens.forEach(([cor, txt]) => itemLegenda(lista.append("li"), cor, txt, false));
  }

  // ---- 2. Histograma da região selecionada ----
  const norm = (x, mu, sig) =>
    Math.exp(-0.5 * Math.pow((x - mu) / sig, 2)) / (sig * Math.sqrt(2 * Math.PI));

  function linha(x, y, pts) {
    return d3.line().x(d => x(d[0])).y(d => y(d[1])).curve(d3.curveBasis)(pts);
  }

  function desenharHist() {
    const rot = regiaoAtiva;
    const c = celulaRegiao(rot);
    const cont = d3.select("#reserva-hist");
    cont.selectAll("*").remove();
    const titulo = document.getElementById("reserva-hist-titulo");
    if (titulo) {
      titulo.textContent = rot === ESTADO
        ? "Goiás inteiro" : rot.replace(" Goiano", " Goiano");
    }
    if (!c) return;

    const bins = DADOS.meta.bins;
    const larg = bins[1] - bins[0];
    const W = 460, H = 300, M = { t: 14, r: 12, b: 34, l: 46 };
    const svg = cont.append("svg").attr("viewBox", `0 0 ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet").attr("class", "reserva-svg");

    const centros = c.counts.map((_, i) => (bins[i] + bins[i + 1]) / 2);
    const x = d3.scaleLinear().domain([0, 40]).range([M.l, W - M.r]);
    const y = d3.scaleLinear().domain([0, d3.max(c.counts) * 1.12]).range([H - M.b, M.t]);
    const bw = (x(larg) - x(0)) * 0.88;

    svg.append("g").attr("transform", `translate(0,${H - M.b})`)
      .call(d3.axisBottom(x).ticks(8).tickFormat(d => d + "a"))
      .attr("class", "reserva-eixo");
    svg.append("g").attr("transform", `translate(${M.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d3.format("~s")(d).replace("G", "bi")))
      .attr("class", "reserva-eixo");

    svg.append("g").selectAll("rect")
      .data(c.counts).join("rect")
      .attr("x", (d, i) => x(centros[i]) - bw / 2)
      .attr("y", d => y(d))
      .attr("width", bw)
      .attr("height", d => Math.max(0, (H - M.b) - y(d)))
      .attr("fill", "#dedbd2");

    // As curvas ajustadas, em unidade de CONTAGEM: densidade × n × largura do bin
    // — assim elas dividem a mesma escala vertical das barras.
    const g = c.gmm;
    if (g && g.sig_jovem && g.sig_velho) {
      const esc = c.n * larg;
      const xs = d3.range(0, 40.2, 0.4);
      const c1 = xs.map(v => [v, esc * g.w_jovem * norm(v, g.mu_jovem, g.sig_jovem)]);
      const c2 = xs.map(v => [v, esc * g.w_velho * norm(v, g.mu_velho, g.sig_velho)]);
      const uma = xs.map(v => [v, esc * norm(v, g.mu_1c, g.sig_1c)]);

      const area = d3.area().x(d => x(d[0])).y0(y(0)).y1(d => y(d[1]))
        .curve(d3.curveBasis);
      svg.append("path").attr("d", area(c1)).attr("fill", COR_JOVEM).attr("opacity", 0.28);
      svg.append("path").attr("d", area(c2)).attr("fill", COR_ANTIGO).attr("opacity", 0.28);
      svg.append("path").attr("d", linha(x, y, c1)).attr("fill", "none")
        .attr("stroke", COR_JOVEM).attr("stroke-width", 1.6);
      svg.append("path").attr("d", linha(x, y, c2)).attr("fill", "none")
        .attr("stroke", COR_ANTIGO).attr("stroke-width", 1.6);
      svg.append("path").attr("d", linha(x, y, uma)).attr("fill", "none")
        .attr("stroke", COR_UMA).attr("stroke-width", 2)
        .attr("stroke-dasharray", "6 3");

    }

    // A legenda vive em HTML, FORA do SVG. Dentro dela competia com as curvas
    // por espaço e encolhia junto com o viewBox — no celular ficava com ~6 px.
    // Fora, ela usa o mesmo componente da legenda do mapa (chips + texto), então
    // os dois painéis passam a ler igual.
    const leg = d3.select("#reserva-hist-legenda");
    leg.selectAll("*").remove();
    if (g) {
      const lista = leg.append("ul").attr("class", "reserva-legenda-lista");
      itemLegenda(lista.append("li"), COR_JOVEM,
                  `pasto de ciclo curto · ${fmtPct(g.w_jovem)} das conversões`, false);
      itemLegenda(lista.append("li"), COR_ANTIGO,
                  `pasto antigo · ${fmtPct(g.w_velho)}`, false);
      itemLegenda(lista.append("li"), COR_UMA, "o que uma população só produziria", true);
    }

    const nota = document.getElementById("reserva-hist-nota");
    if (nota) {
      const cens = c.n_censurado / (c.n + c.n_censurado);
      // `dip_emp` = profundidade do vale no histograma BRUTO. É o número que
      // responde "esta região parece mais bimodal que a outra?" — a pergunta que
      // a peça convida a fazer e que, sem isto, ficava por conta do olho.
      const dip = g ? g.dip_emp : 0;
      const forma = !g ? ""
        : dip >= 0.05
          ? `Aqui o histograma tem <strong>vale visível</strong> — desce e volta a subir por ` +
            `volta dos ${vg(g.vale_emp_x)} anos (profundidade ${vg(Math.round(dip * 100))}%). `
          : `Aqui não há vale visível: as duas populações se somam num pico e um ombro. `;
      nota.innerHTML = forma +
        (c.bimodal
          ? `O ajuste separa modos em <strong>${vg(g.mu_jovem)}a</strong> e ` +
            `<strong>${vg(g.mu_velho)}a</strong>` +
            (g.bc_sarle ? `, e o coeficiente de Sarle — que não usa ajuste nenhum — dá ` +
                          `<strong>${vg(g.bc_sarle)}</strong>, acima do limiar de 0,555` : "") + ". "
          : "O ajuste não separa duas populações aqui. ") +
        `${fmtN(c.n)} conversões de idade conhecida; outras ${fmtN(c.n_censurado)} ` +
        `(${fmtPct(cens)}) já eram pastagem em 1985, têm a idade truncada e ficam de fora.`;
    }
  }

  // ---- 3. Nota de cobertura (censo municipal) ----
  function preencherCobertura(muni) {
    const el = document.getElementById("reserva-cobertura");
    if (!el || !Array.isArray(muni) || !muni.length) return;
    const min = muni.reduce((m, r) => Math.min(m, r.n_pixels), Infinity);
    el.innerHTML = `O censo cobre <strong>${muni.length} municípios</strong>, e mesmo o menor ` +
      `deles tem <strong>${fmtN(min)}</strong> conversões de idade conhecida — não há aqui ` +
      `nenhum recorte medido no fio do ruído.`;
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
  async function montar(caixa) {
    if (montado) return;
    montado = true;
    try {
      await garantirD3();
      const [geoAmc, geoMeso, bracket, muni] = await Promise.all([
        d3.json("assets/data/malha_amc.geojson"),
        d3.json("assets/data/malha_mesorregiao.geojson"),
        d3.json("assets/data/idade_pastagem_bracket.json"),
        d3.json("assets/data/idade_pastagem_municipal.json")
      ]);
      if (!geoAmc || !geoMeso || !bracket) return;
      DADOS = bracket;
      caixa.hidden = false;          // revela só quando os dados chegam
      const btn = document.getElementById("reserva-reset");
      if (btn) {
        btn.hidden = true;
        btn.addEventListener("click", () => selecionar(ESTADO));
      }
      document.querySelectorAll("[data-regua]").forEach(b => {
        const ativo = b.dataset.regua === reguaAtiva;
        b.classList.toggle("is-ativo", ativo);
        b.setAttribute("aria-pressed", ativo ? "true" : "false");
        b.addEventListener("click", () => trocarRegua(b.dataset.regua));
      });
      desenharMapa(geoAmc, geoMeso);
      desenharHist();
      preencherCobertura(muni);
    } catch (err) {
      montado = false;               // permite nova tentativa
      console.warn("[reserva] falha ao montar", err);
    }
  }

  function init() {
    const caixa = document.getElementById("reserva-interativo");
    if (!caixa) return;
    // Observa o bloco-pai VISÍVEL (#reserva-interativo começa hidden = tamanho 0).
    const alvo = document.getElementById("sec-idade-pastagem") || caixa;
    if (typeof IntersectionObserver === "undefined") { montar(caixa); return; }
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { montar(caixa); obs.disconnect(); }
      });
    }, { rootMargin: "300px 0px" });
    obs.observe(alvo);
  }

  root.GO40 = root.GO40 || {};
  root.GO40.reservaPerna2 = { init };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
