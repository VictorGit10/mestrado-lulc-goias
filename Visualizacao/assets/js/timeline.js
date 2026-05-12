/* timeline.js — orquestracao do scrollytelling.
 * Carrega dados, hidrata steps, inicializa Scrollama, desenha spark-line
 * e move cursores ao trocar de ano.
 */

(function (root) {
  "use strict";

  const ANO_MIN = 1985;
  const ANO_MAX = 2024;
  const TOTAL_ANOS = ANO_MAX - ANO_MIN;

  const fmtPct = v => (v == null ? "—" : (v * 100).toFixed(1).replace(".", ",") + "%");
  const fmtNum = (v, d = 0) => {
    if (v == null) return "—";
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: d }).format(v);
  };
  const fmtBilhao = v => v == null ? "—" : "R$ " + (v / 1e9).toFixed(1).replace(".", ",") + " bi";
  const fmtMilhao = v => v == null ? "—" : (v / 1e6).toFixed(2).replace(".", ",") + " Mha";
  const fmtPctBar = v => (v * 100).toFixed(1).replace(".", ",") + "%";
  const fmtPp = v => {
    if (v == null) return "";
    const abs = Math.abs(v).toFixed(1).replace(".", ",");
    return `${abs} pp`;
  };

  const yearToPct = ano => ((ano - ANO_MIN) / TOTAL_ANOS) * 100;

  // Estado compartilhado entre funcoes (preenchido em init).
  let porAno = {};

  // -------------------- carregamento --------------------
  async function carregarDados() {
    const [painel, marcos, transicoes] = await Promise.all([
      fetch("assets/data/painel_goias.json").then(r => r.json()),
      fetch("assets/data/marcos.json").then(r => r.json()),
      fetch("assets/data/transicoes_resumo.json").then(r => r.json())
    ]);
    return { painel, marcos, transicoes };
  }

  // -------------------- regua superior --------------------
  function posicionarPinosRegua(marcos) {
    document.querySelectorAll(".rail-pin").forEach(pin => {
      const ano = parseInt(pin.dataset.year, 10);
      pin.style.left = yearToPct(ano) + "%";
      pin.addEventListener("click", () => {
        const alvo = document.querySelector(`.step[data-year="${ano}"]`);
        if (alvo) alvo.scrollIntoView({ behavior: "smooth", block: "center" });
      });
    });
    // tooltip via title
    marcos.marcos.forEach(m => {
      const pin = document.querySelector(`.rail-pin[data-year="${m.ano}"]`);
      if (pin) pin.title = `${m.ano} — ${m.titulo}`;
    });
  }

  function moverCursorRegua(ano) {
    const cursor = document.getElementById("rail-cursor");
    if (cursor) cursor.style.left = yearToPct(ano) + "%";
    document.querySelectorAll(".rail-pin").forEach(pin => {
      pin.classList.toggle("rail-pin--active", parseInt(pin.dataset.year, 10) === ano);
    });
  }

  // -------------------- delta inline --------------------
  // direcao "boa": para 'veg' subir = bom (verde); para 'pasto'/'soja' subir = expansao (terracota).
  function classeDelta(cls, dpp) {
    if (Math.abs(dpp) < 0.05) return "delta--flat";
    const subindo = dpp > 0;
    if (cls === "veg") return subindo ? "delta--up-good" : "delta--down-bad";
    return subindo ? "delta--up-bad" : "delta--down-good";
  }

  function formatDelta(curr, prev, cls) {
    if (curr == null || prev == null) return "";
    const dpp = (curr - prev) * 100;
    const klass = classeDelta(cls, dpp);
    if (klass === "delta--flat") {
      return `<span class="delta delta--flat">~ 0,0 pp</span>`;
    }
    const seta = dpp > 0 ? "▲" : "▼";
    return `<span class="delta ${klass}">${seta} ${fmtPp(dpp)}</span>`;
  }

  // -------------------- hidratacao dos steps --------------------
  function hidratarSteps(painel, marcos) {
    const marcoPorAno = Object.fromEntries(marcos.marcos.map(m => [m.ano, m]));

    function metricCard(label, value, deltaHtml, cssClass) {
      return '<div class="metric-card' + (cssClass ? ' metric-card--' + cssClass : '') + '">'
        + '<span class="metric-label">' + label + '</span>'
        + '<span class="metric-value">' + value + '</span>'
        + (deltaHtml ? '<span class="metric-delta">' + deltaHtml + '</span>' : '')
        + '</div>';
    }

    document.querySelectorAll(".step[data-year]").forEach(step => {
      const ano = parseInt(step.dataset.year, 10);
      const dado = porAno[ano];
      const prev = porAno[ano - 1];
      const marco = marcoPorAno[ano];

      let html = "";
      if (marco) {
        step.classList.add("step--marco");
        html += '<span class="marco-tag">' + ano + ' · ' + marco.categoria.replace(/_/g, " ") + '</span>';
        html += '<h3 class="marco-titulo">' + marco.titulo + '</h3>';
        if (marco.subtitulo) html += '<p class="marco-subtitulo">' + marco.subtitulo + '</p>';
        html += '<p class="marco-descricao">' + marco.descricao + '</p>';
      } else {
        html += '<span class="marco-tag muted-year">' + ano + '</span>';
      }

      if (dado) {
        const primary = [
          metricCard('Veg. nativa', fmtPct(dado.pct_vegetacao_nativa), formatDelta(dado.pct_vegetacao_nativa, (prev ? prev.pct_vegetacao_nativa : null), 'veg'), 'veg'),
          metricCard('Pastagem', fmtPct(dado.pct_pastagem), formatDelta(dado.pct_pastagem, (prev ? prev.pct_pastagem : null), 'pasto'), 'pasto'),
          metricCard('Soja (solo)', fmtPct(dado.pct_soja), formatDelta(dado.pct_soja, (prev ? prev.pct_soja : null), 'soja'), 'soja'),
          metricCard('Rebanho', dado.pec_bovinos_cab != null ? fmtNum(dado.pec_bovinos_cab / 1e6, 1) + ' M cab' : '—', '', 'bovino'),
          metricCard('Lotacao', dado.lotacao_ua_ha_pasto != null ? fmtNum(dado.lotacao_ua_ha_pasto, 2) + ' UA/ha' : '—', '', 'lotacao'),
          metricCard('Soja (prod.)', dado.agri_soja_ton != null ? fmtNum(dado.agri_soja_ton / 1e6, 1) + ' Mt' : '—', '', 'soja'),
        ].join('');

        let secondary = [];
        if (dado.pib_real_rs != null) {
          secondary.push(metricCard('PIB', fmtBilhao(dado.pib_real_rs), '', 'pib'));
        }
        if (dado.va_agro_real_rs != null) {
          secondary.push(metricCard('VA Agro', fmtBilhao(dado.va_agro_real_rs), '', 'va'));
        }
        if (dado.sicor_total_real_rs != null) {
          secondary.push(metricCard('Credito rural', fmtBilhao(dado.sicor_total_real_rs), '', 'credito'));
        }
        if (dado.fogo_total_ha != null) {
          secondary.push(metricCard('Fogo', fmtNum(dado.fogo_total_ha / 1e3, 0) + ' kha' , '', 'fogo'));
        }
        if (dado.agri_leite_mil_litros != null) {
          secondary.push(metricCard('Leite', fmtNum(dado.agri_leite_mil_litros / 1e3, 1) + ' Mi L', '', 'leite'));
        }
        if (dado.populacao != null) {
          secondary.push(metricCard('Populacao', fmtNum(dado.populacao / 1e6, 2) + ' Mi', '', 'pop'));
        }

        html += '<div class="metric-grid">' + primary + '</div>';
        if (secondary.length > 0) {
          html += '<details class="metric-details">'
            + '<summary>+ dados socioeconomicos</summary>'
            + '<div class="metric-grid metric-grid--secondary">' + secondary.join('') + '</div>'
            + '</details>';
        }
      }

      step.innerHTML = html;
    });
  }

// -------------------- spark-line --------------------
  function desenharSparkline(painel) {
    const svg = document.getElementById("sparkline-svg");
    const W = 1000;
    const H = 80;
    const padL = 8;
    const padR = 8;
    const padT = 6;
    const padB = 6;
    const innerW = W - padL - padR;
    const innerH = H - padT - padB;
    const xs = ano => padL + ((ano - ANO_MIN) / TOTAL_ANOS) * innerW;

    const series = painel.serie;
    const valores = ["pct_vegetacao_nativa", "pct_pastagem", "pct_soja"]
      .flatMap(k => series.map(s => s[k]).filter(v => v != null));
    const yMax = Math.max(...valores) * 1.05;
    const ys = v => padT + innerH - (v / yMax) * innerH;

    const buildPath = (key) =>
      series
        .filter(s => s[key] != null)
        .map((s, i) => `${i === 0 ? "M" : "L"} ${xs(s.ano).toFixed(2)} ${ys(s[key]).toFixed(2)}`)
        .join(" ");

    svg.innerHTML = `
      <line x1="${padL}" y1="${ys(0).toFixed(1)}" x2="${W - padR}" y2="${ys(0).toFixed(1)}"
            stroke="var(--color-rule)" stroke-width="1"/>
      <path class="spark-path spark-path-veg"   d="${buildPath("pct_vegetacao_nativa")}"/>
      <path class="spark-path spark-path-pasto" d="${buildPath("pct_pastagem")}"/>
      <path class="spark-path spark-path-soja"  d="${buildPath("pct_soja")}"/>
      <line id="spark-cursor-line" class="spark-cursor"
            x1="${xs(ANO_MIN)}" y1="${padT}" x2="${xs(ANO_MIN)}" y2="${H - padB}"/>
      <rect id="spark-hit-area" x="0" y="0" width="${W}" height="${H}"
            fill="transparent" style="cursor: crosshair;" />
    `;

    // Tooltip element
    let tooltip = document.getElementById("sparkline-tooltip");
    if (!tooltip) {
      tooltip = document.createElement("div");
      tooltip.id = "sparkline-tooltip";
      tooltip.className = "sparkline-tooltip";
      document.querySelector(".sparkline-inner").appendChild(tooltip);
    }

    const hitArea = document.getElementById("spark-hit-area");
    if (!hitArea) return;

    function anoFromX(clientX) {
      const rect = svg.getBoundingClientRect();
      const x = clientX - rect.left;
      const pct = Math.max(0, Math.min(1, (x - padL) / innerW));
      return ANO_MIN + Math.round(pct * TOTAL_ANOS);
    }

    hitArea.addEventListener("mousemove", (ev) => {
      const ano = anoFromX(ev.clientX);
      const d = porAno[ano];
      if (!d) return;
      moverCursorSparkline(ano);
      tooltip.innerHTML = `
        <strong>${ano}</strong><br/>
        Veg: ${fmtPct(d.pct_vegetacao_nativa)}<br/>
        Pasto: ${fmtPct(d.pct_pastagem)}<br/>
        Soja: ${fmtPct(d.pct_soja)}
      `;
      tooltip.style.opacity = "1";
      const rect = svg.getBoundingClientRect();
      tooltip.style.left = (ev.clientX - rect.left + 10) + "px";
      tooltip.style.top = (ev.clientY - rect.top - 10) + "px";
    });

    hitArea.addEventListener("mouseleave", () => {
      tooltip.style.opacity = "0";
      // Restore cursor to current scroll year
      const currentStep = document.querySelector('.step[data-year].is-active');
      if (currentStep) {
        const ano = parseInt(currentStep.dataset.year, 10);
        moverCursorSparkline(ano);
      }
    });

    hitArea.addEventListener("click", (ev) => {
      const ano = anoFromX(ev.clientX);
      const alvo = document.querySelector(`.step[data-year="${ano}"]`);
      if (alvo) alvo.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

function moverCursorSparkline(ano) {
    const line = document.getElementById("spark-cursor-line");
    if (!line) return;
    const W = 1000;
    const x = 8 + ((ano - ANO_MIN) / TOTAL_ANOS) * (W - 16);
    line.setAttribute("x1", x.toFixed(2));
    line.setAttribute("x2", x.toFixed(2));
    const yearLabel = document.getElementById("sparkline-year");
    if (yearLabel) yearLabel.textContent = ano;
  }

  // -------------------- barra empilhada --------------------
  // 7 segmentos espelhando as classes do mapa: veg natural, pastagem,
  // agricultura (inclui soja no MapBiomas), mosaico agric./pastagem,
  // água, área urbana, outros (silvicultura + mineração + não-mapeados).
  function atualizarBarra(ano) {
    const dado = porAno[ano];
    if (!dado) return;
    const veg = dado.pct_vegetacao_nativa || 0;
    const pasto = dado.pct_pastagem || 0;
    const agric = dado.pct_agricultura || 0;
    const agua = dado.pct_agua || 0;
    const urbano = dado.pct_area_urbana || 0;
    const outros = Math.max(0, 1 - veg - pasto - agric - agua - urbano);

    const map = { veg, pasto, agric, agua, urbano, outros };
    const nomes = {
      veg: "Vegetação natural",
      pasto: "Pastagem",
      agric: "Agricultura",
      agua: "Água",
      urbano: "Área urbana",
      outros: "Outros"
    };
    document.querySelectorAll("#composition-bar .bar-segment").forEach(seg => {
      const k = seg.dataset.class;
      const v = map[k] != null ? map[k] : 0;
      seg.style.width = (v * 100).toFixed(2) + "%";
      seg.title = `${nomes[k]}: ${fmtPctBar(v)}`;
    });

    // Atualizar tooltip
    const tooltip = document.getElementById("bar-tooltip");
    if (tooltip) {
      const parts = Object.entries(map)
        .filter(([, v]) => v > 0.005)
        .map(([k, v]) => `${nomes[k]} ${fmtPctBar(v)}`)
        .join(" · ");
      tooltip.textContent = parts;
    }
  }

  // -------------------- ancora vs. 1985 no caption --------------------
  function atualizarAncora(ano) {
    const ancora = document.getElementById("map-anchor");
    if (!ancora) return;
    const cur = porAno[ano];
    const base = porAno[ANO_MIN];
    if (!cur || !base) {
      ancora.textContent = "";
      return;
    }
    const series = [
      { rotulo: "veg. nativa", chave: "pct_vegetacao_nativa" },
      { rotulo: "pastagem",    chave: "pct_pastagem" }
    ];
    if (ano === ANO_MIN) {
      const partes = series.map(s => `${s.rotulo} ${fmtPct(cur[s.chave])}`);
      ancora.textContent = partes.join(" · ") + " (baseline)";
      return;
    }
    const partes = series.map(s => {
      const dpp = (cur[s.chave] - base[s.chave]) * 100;
      const sinal = dpp > 0 ? "+" : "−";
      const abs = Math.abs(dpp).toFixed(1).replace(".", ",");
      return `${s.rotulo} ${fmtPct(cur[s.chave])} (${sinal}${abs} pp)`;
    });
    ancora.textContent = partes.join(" · ") + " vs. 1985";
  }

  // -------------------- mapa cross-fade --------------------
  let anoAtual = null;
  function trocarMapa(ano) {
    if (ano === anoAtual) return;
    anoAtual = ano;
    const img = document.getElementById("mapa");
    const frame = img.closest(".map-frame");
    const yearLabel = document.getElementById("map-year");

    frame.classList.add("is-fading");
    const src = `img/mapas_gee/cobertura_${ano}.webp`;
    const next = new Image();
    next.onload = () => {
      img.src = src;
      img.alt = `Mapa pixel-a-pixel do uso e cobertura da terra em Goiás em ${ano}`;
      yearLabel.textContent = ano;
      requestAnimationFrame(() => frame.classList.remove("is-fading"));
    };
    next.onerror = () => frame.classList.remove("is-fading");
    next.src = src;

    atualizarBarra(ano);
    atualizarAncora(ano);
  }

  // -------------------- sintese (cards de transicao) --------------------
  function renderizarSintese(transicoes) {
    const cont = document.getElementById("resumo-transicoes");
    if (!cont) return;
    cont.remove();

    const html = transicoes.classes.map(c => {
      const dir = c.delta_ha < 0 ? "neg" : "pos";
      const sinal = c.delta_ha >= 0 ? "+" : "";
      const pct = c.delta_pct == null ? "—" : `${sinal}${fmtNum(c.delta_pct, 1)}%`;
      return `
        <div class="resumo-card">
          <div class="resumo-card-nome">${c.nome}</div>
          <div class="resumo-card-valor resumo-card-valor--${dir}">${pct}</div>
          <div class="resumo-card-detalhe">${fmtMilhao(c.ha_inicio)} → ${fmtMilhao(c.ha_fim)}</div>
        </div>
      `;
    }).join("");

    document.querySelector(".sintese h2").insertAdjacentHTML(
      "afterend",
      `<div class="resumo-transicoes" id="resumo-transicoes">${html}</div>`
    );
  }

  // -------------------- gerar steps anuais --------------------
  function gerarStepsAnuais() {
    const eraRanges = [
      { era: 'heranca',        start: 1985, end: 1993 },
      { era: 'soja-sudoeste',  start: 1994, end: 2002 },
      { era: 'boom-commodity', start: 2003, end: 2011 },
      { era: 'intensificacao', start: 2012, end: 2017 },
      { era: 'reorganizacao',  start: 2018, end: 2024 },
    ];
    eraRanges.forEach(({ era, start, end }) => {
      const eraCard = document.querySelector(`.step--era[data-era="${era}"]`);
      if (!eraCard) return;
      let anchor = eraCard;
      for (let year = start; year <= end; year++) {
        const art = document.createElement('article');
        art.className = 'step';
        art.dataset.year = String(year);
        anchor.insertAdjacentElement('afterend', art);
        anchor = art;
      }
    });
  }

  // -------------------- scrollama --------------------
  function inicializarScrollama() {
    if (typeof scrollama === "undefined") {
      console.warn("Scrollama nao carregado");
      return;
    }
    const scroller = scrollama();
    scroller
      .setup({
        step: ".step[data-year]",
        offset: 0.55,
        progress: false
      })
      .onStepEnter(({ element }) => {
        const ano = parseInt(element.dataset.year, 10);
        document.querySelectorAll(".step[data-year].is-active").forEach(s => s.classList.remove("is-active"));
        element.classList.add("is-active");
        trocarMapa(ano);
        moverCursorRegua(ano);
        moverCursorSparkline(ano);
      });

    window.addEventListener("resize", () => scroller.resize());
  }

  // -------------------- subrota (chamado pelo router) --------------------
  function aplicarSubrota(segmentos) {
    // segmentos: [] | [ano]
    if (!segmentos || segmentos.length === 0) return;
    const ano = parseInt(segmentos[0], 10);
    if (isNaN(ano) || ano < ANO_MIN || ano > ANO_MAX) return;
    const alvo = document.querySelector(`.step[data-year="${ano}"]`);
    if (alvo) alvo.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // -------------------- bootstrap --------------------
  async function init() {
    try {
      const dados = await carregarDados();
      porAno = Object.fromEntries(dados.painel.serie.map(r => [r.ano, r]));
      posicionarPinosRegua(dados.marcos);
      gerarStepsAnuais();
      hidratarSteps(dados.painel, dados.marcos);
      desenharSparkline(dados.painel);
      atualizarBarra(ANO_MIN);
      atualizarAncora(ANO_MIN);
      renderizarSintese(dados.transicoes);
      inicializarScrollama();
    } catch (err) {
      console.error("Erro ao inicializar timeline:", err);
      const cont = document.getElementById("resumo-transicoes");
      if (cont) {
        cont.innerHTML =
          `<p class="resumo-loading" style="color:#8b3a1d">` +
          `Falha ao carregar dados: ${err.message}. ` +
          `Se voce abriu via duplo-clique, use o servir.bat ou servir.ps1.</p>`;
      }
    }
    root.GO40 = root.GO40 || {};
    root.GO40.narrativa = { aplicarSubrota };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
