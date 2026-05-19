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
  const ERA_RANGES = [
    {
      era: "heranca",
      ato: "Ato I",
      start: 1985,
      end: 2000,
      titulo: "Pastagem como herança",
      resumo: "pastagem domina e a soja ainda é pontual"
    },
    {
      era: "expansao",
      ato: "Ato II",
      start: 2001,
      end: 2019,
      titulo: "Expansão e intensificação",
      resumo: "soja avança sobre pastagem; intensificação sem fronteira"
    },
    {
      era: "conversao",
      ato: "Ato III",
      start: 2020,
      end: 2024,
      titulo: "Conversão seletiva",
      resumo: "vegetação se recupera; pastagem perde área"
    }
  ];

  // Estado compartilhado entre funcoes (preenchido em init).
  let porAno = {};
  let marcosLinhaDoTempo = [];
  let marcoPorAno = {};

  // Estado dos 3 acordeoes do card lateral (persiste durante o scroll).
  const acordeaoAberto = { agro: false, pecuaria: false, socio: false };

  // Helpers de cobertura (datasets com gaps): marcar campos com nota inline.
  function valorOuTraco(v, formatador) {
    return v == null ? '<span class="metric-na" title="sem dado neste ano">—</span>' : formatador(v);
  }
  const fmtTon = v => {
    if (v >= 1e6) return fmtNum(v / 1e6, 2) + " Mt";
    if (v >= 1e3) return fmtNum(v / 1e3, 0) + " kt";
    return fmtNum(v, 0) + " t";
  };

  // -------------------- carregamento --------------------
  async function carregarDados() {
    const [painel, marcos] = await Promise.all([
      fetch("assets/data/painel_goias.json").then(r => r.json()),
      fetch("assets/data/marcos.json").then(r => r.json())
    ]);
    return { painel, marcos };
  }

  // -------------------- regua superior --------------------
  function moverCursorRegua(ano) {
    const cursor = document.getElementById("rail-cursor");
    if (cursor) cursor.style.left = yearToPct(ano) + "%";
  }

  function eraDoAno(ano) {
    return ERA_RANGES.find(item => ano >= item.start && ano <= item.end) || null;
  }

  function atualizarResumoRegua(ano) {
    const eraEl = document.getElementById("rail-active-era");
    const labelEl = document.getElementById("rail-active-label");
    const era = eraDoAno(ano);
    const marco = marcoPorAno[ano];

    if (eraEl && era) {
      eraEl.textContent = `${era.ato} · ${era.start}-${era.end} · ${era.titulo}`;
    }
    if (labelEl) {
      labelEl.textContent = marco
        ? `${ano} · ${marco.titulo}`
        : `${ano} · ${era ? era.resumo : "linha do tempo em foco"}`;
    }

    document.querySelectorAll(".rail-era-band").forEach(band => {
      band.classList.toggle("is-active", band.dataset.era === (era ? era.era : ""));
    });
    document.querySelectorAll(".rail-marco-pin").forEach(pin => {
      pin.classList.toggle("is-active", pin.dataset.year === String(ano));
    });
  }

  function anoMaisProximoNaRegua(clientX) {
    const track = document.getElementById("rail-track");
    if (!track) return ANO_MIN;
    const rect = track.getBoundingClientRect();
    if (rect.width <= 0) return ANO_MIN;
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    return Math.round(ANO_MIN + pct * TOTAL_ANOS);
  }

  function configurarRegua(marcos) {
    marcosLinhaDoTempo = (marcos.marcos || []).slice().sort((a, b) => a.ano - b.ano);
    marcoPorAno = Object.fromEntries(marcosLinhaDoTempo.map(item => [item.ano, item]));

    const container = document.getElementById("rail-marcos");
    if (container) {
      container.innerHTML = "";
      marcosLinhaDoTempo.forEach(marco => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "rail-marco-pin";
        btn.dataset.year = String(marco.ano);
        btn.style.left = yearToPct(marco.ano) + "%";
        btn.setAttribute("aria-label", `${marco.ano} · ${marco.titulo}`);
        btn.title = `${marco.ano} · ${marco.titulo}`;
        btn.innerHTML = `<span class="rail-marco-pin-label">${marco.ano} · ${marco.titulo}</span>`;
        btn.addEventListener("click", ev => {
          ev.stopPropagation();
          scrollParaAno(marco.ano, 0.46);
          btn.blur();
        });
        container.appendChild(btn);
      });
    }

    document.querySelectorAll(".rail-era-band").forEach(band => {
      band.addEventListener("click", ev => {
        ev.stopPropagation();
        const startYear = parseInt(band.dataset.startYear, 10);
        const era = ERA_RANGES.find(item => item.era === band.dataset.era);
        const focusYear = era ? Math.round((era.start + era.end) / 2) : startYear;
        if (!isNaN(focusYear)) scrollParaAno(focusYear, 0.48);
      });
    });

    const track = document.getElementById("rail-track");
    if (track) {
      track.addEventListener("click", ev => {
        if (ev.target.closest(".rail-marco-pin") || ev.target.closest(".rail-era-band")) return;
        scrollParaAno(anoMaisProximoNaRegua(ev.clientX), 0.46);
      });
    }

    atualizarResumoRegua(ANO_MIN);
    moverCursorRegua(ANO_MIN);
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
    const marcosPorAnoLocal = Object.fromEntries(marcos.marcos.map(m => [m.ano, m]));

    function metricCard(label, value, deltaHtml, cssClass) {
      return '<div class="metric-card' + (cssClass ? ' metric-card--' + cssClass : '') + '">'
        + '<span class="metric-label">' + label + '</span>'
        + '<span class="metric-value">' + value + '</span>'
        + (deltaHtml ? '<span class="metric-delta">' + deltaHtml + '</span>' : '')
        + '</div>';
    }

    // Cards LULC: tres metricas sempre visiveis, mesma altura entre steps.
    function cardsLULC(dado, prev) {
      return [
        metricCard('Veg. nativa', fmtPct(dado.pct_vegetacao_nativa), formatDelta(dado.pct_vegetacao_nativa, prev ? prev.pct_vegetacao_nativa : null, 'veg'), 'veg'),
        metricCard('Pastagem',    fmtPct(dado.pct_pastagem),         formatDelta(dado.pct_pastagem,         prev ? prev.pct_pastagem         : null, 'pasto'), 'pasto'),
        metricCard('Agricultura', fmtPct(dado.pct_agricultura),      formatDelta(dado.pct_agricultura,      prev ? prev.pct_agricultura      : null, 'soja'), 'agric'),
      ].join('');
    }

    // Tabela compacta dois colunas (rotulo | valor) — usada nos acordeoes.
    function linhaTabela(rotulo, valor, nota) {
      const notaHtml = nota ? `<span class="metric-row-nota">${nota}</span>` : '';
      return `<div class="metric-row"><span class="metric-row-label">${rotulo}</span><span class="metric-row-value">${valor}</span>${notaHtml}</div>`;
    }

    function acordeao(id, titulo, conteudo) {
      const aberto = acordeaoAberto[id] ? ' open' : '';
      return `<details class="metric-details" data-acordeao="${id}"${aberto}>`
        + `<summary>${titulo}</summary>`
        + `<div class="metric-rows">${conteudo}</div>`
        + `</details>`;
    }

    function acordeaoAgricultura(dado) {
      const culturas = [
        ['Soja',     dado.agri_soja_ton],
        ['Milho',    dado.agri_milho_total_ton],
        ['Cana',     dado.agri_cana_ton],
        ['Algodão',  dado.agri_algodao_ton],
        ['Sorgo',    dado.agri_sorgo_ton],
        ['Arroz',    dado.agri_arroz_ton],
        ['Feijão',   dado.agri_feijao_ton],
      ];
      const linhas = culturas
        .map(([nome, v]) => linhaTabela(nome, valorOuTraco(v, fmtTon)))
        .join('');
      return acordeao('agro', 'Produção agrícola (toneladas)', linhas);
    }

    function acordeaoPecuaria(dado) {
      const linhas = [
        linhaTabela('Rebanho bovino', valorOuTraco(dado.pec_bovinos_cab, v => fmtNum(v / 1e6, 2) + ' M cab')),
        linhaTabela('Lotação',        valorOuTraco(dado.lotacao_ua_ha_pasto, v => fmtNum(v, 2) + ' UA/ha')),
        linhaTabela('Leite',          valorOuTraco(dado.agri_leite_mil_litros, v => fmtNum(v / 1e3, 1) + ' Mi L')),
      ].join('');
      return acordeao('pecuaria', 'Pecuária', linhas);
    }

    function acordeaoSocio(dado) {
      const linhas = [
        linhaTabela('PIB (IPEA UF)',     valorOuTraco(dado.pib_uf_real_rs,     fmtBilhao), 'IBGE Contas Reg., 1985+'),
        linhaTabela('PIB (Σ municípios)', valorOuTraco(dado.pib_real_rs,        fmtBilhao), 'SIDRA 5938, 2002+'),
        linhaTabela('VA Agro (IPEA UF)',     valorOuTraco(dado.va_agro_uf_real_rs, fmtBilhao), 'IBGE Contas Reg., 1985+'),
        linhaTabela('VA Agro (Σ municípios)', valorOuTraco(dado.va_agro_real_rs,    fmtBilhao), 'SIDRA 5938, 2002+'),
        linhaTabela('Crédito rural', valorOuTraco(dado.sicor_total_real_rs, fmtBilhao), 'desde 2013'),
        linhaTabela('População',     valorOuTraco(dado.populacao,           v => fmtNum(v / 1e6, 2) + ' Mi'), 'desde 2001'),
      ].join('');
      return acordeao('socio', 'Socioeconômico', linhas);
    }

    document.querySelectorAll(".step[data-year]").forEach(step => {
      const ano = parseInt(step.dataset.year, 10);
      const dado = porAno[ano];
      const prev = porAno[ano - 1];
      const marco = marcosPorAnoLocal[ano];

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
        html += '<div class="metric-grid metric-grid--lulc">' + cardsLULC(dado, prev) + '</div>';
        html += '<div class="metric-acordeoes">'
          + acordeaoAgricultura(dado)
          + acordeaoPecuaria(dado)
          + acordeaoSocio(dado)
          + '</div>';
      }

      step.innerHTML = html;
    });

    // Sincronizar abertura/fechamento entre todos os steps (estado global).
    document.querySelectorAll('details[data-acordeao]').forEach(det => {
      det.addEventListener('toggle', () => {
        const id = det.dataset.acordeao;
        acordeaoAberto[id] = det.open;
        document.querySelectorAll(`details[data-acordeao="${id}"]`).forEach(outro => {
          if (outro !== det && outro.open !== det.open) outro.open = det.open;
        });
      });
    });
  }

// -------------------- spark-line --------------------
  // Tres series com unidades diferentes, cada uma normalizada ao proprio
  // maximo (0 a 1). Tooltip mostra valores absolutos com unidade real.
  // Complementa o mapa: nenhuma das tres aparece nos cards LULC ou na barra.
  const SPARK_SERIES = [
    {
      chave: "soja",
      campo: "agri_soja_ton",
      rotulo: "Produção de soja",
      transformar: v => v == null ? null : v / 1e6,
      formatar: v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Mt"
    },
    {
      chave: "rebanho",
      campo: "pec_bovinos_cab",
      rotulo: "Rebanho bovino",
      transformar: v => v == null ? null : v / 1e6,
      formatar: v => v == null ? "—" : fmtNum(v / 1e6, 1) + " M cab"
    },
    {
      chave: "fogo",
      campo: "fogo_total_ha",
      rotulo: "Área queimada",
      transformar: v => v == null ? null : v / 1e3,
      formatar: v => v == null ? "—" : fmtNum(v / 1e3, 0) + " kha"
    }
  ];

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

    // Maximo independente por serie (normalizacao 0..1 de cada uma).
    const maximos = {};
    SPARK_SERIES.forEach(s => {
      const valores = series.map(r => s.transformar(r[s.campo])).filter(v => v != null);
      maximos[s.chave] = valores.length ? Math.max(...valores) : 1;
    });

    const ysNorm = (chave, valor) => {
      if (valor == null) return null;
      const norm = valor / maximos[chave];
      return padT + innerH - norm * innerH;
    };

    const buildPath = (s) => {
      const pontos = series
        .map(r => ({ ano: r.ano, v: s.transformar(r[s.campo]) }))
        .filter(p => p.v != null);
      return pontos
        .map((p, i) => `${i === 0 ? "M" : "L"} ${xs(p.ano).toFixed(2)} ${ysNorm(s.chave, p.v).toFixed(2)}`)
        .join(" ");
    };

    const baselineY = (padT + innerH).toFixed(1);
    svg.innerHTML = `
      <line x1="${padL}" y1="${baselineY}" x2="${W - padR}" y2="${baselineY}"
            stroke="var(--color-rule)" stroke-width="1"/>
      <path class="spark-path spark-path-soja"    d="${buildPath(SPARK_SERIES[0])}"/>
      <path class="spark-path spark-path-rebanho" d="${buildPath(SPARK_SERIES[1])}"/>
      <path class="spark-path spark-path-fogo"    d="${buildPath(SPARK_SERIES[2])}"/>
      <line id="spark-cursor-line" class="spark-cursor"
            x1="${xs(ANO_MIN)}" y1="${padT}" x2="${xs(ANO_MIN)}" y2="${H - padB}"/>
      <rect id="spark-hit-area" x="0" y="0" width="${W}" height="${H}"
            fill="transparent" style="cursor: crosshair;" />
    `;

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
      // O SVG estica para a largura do container (preserveAspectRatio="none"),
      // entao usamos rect.width (CSS px) em vez de innerW (viewBox).
      const rect = svg.getBoundingClientRect();
      const x = clientX - rect.left;
      const pct = Math.max(0, Math.min(1, x / rect.width));
      return ANO_MIN + Math.round(pct * TOTAL_ANOS);
    }

    hitArea.addEventListener("mousemove", (ev) => {
      const ano = anoFromX(ev.clientX);
      const d = porAno[ano];
      if (!d) return;
      moverCursorSparkline(ano);
      const linhasTooltip = SPARK_SERIES.map(s => {
        const v = s.transformar(d[s.campo]);
        return `${s.rotulo}: ${s.formatar(d[s.campo])}`;
      }).join("<br/>");
      tooltip.innerHTML = `<strong>${ano}</strong><br/>${linhasTooltip}`;
      tooltip.style.opacity = "1";
      const rect = svg.getBoundingClientRect();
      tooltip.style.left = (ev.clientX - rect.left + 10) + "px";
      tooltip.style.top = (ev.clientY - rect.top - 10) + "px";
    });

    hitArea.addEventListener("mouseleave", () => {
      tooltip.style.opacity = "0";
      const currentStep = document.querySelector('.step[data-year].is-active');
      if (currentStep) {
        const ano = parseInt(currentStep.dataset.year, 10);
        moverCursorSparkline(ano);
      }
    });

    hitArea.addEventListener("click", (ev) => {
      const ano = anoFromX(ev.clientX);
      scrollParaAno(ano);
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
    if (ano === ANO_MIN) {
      ancora.textContent = "linha de base";
      return;
    }
    const delta = (chave) => {
      const dpp = (cur[chave] - base[chave]) * 100;
      const sinal = dpp > 0 ? "+" : "−";
      return sinal + Math.abs(dpp).toFixed(1).replace(".", ",") + " pp";
    };
    ancora.textContent = `vs. 1985 — veg ${delta("pct_vegetacao_nativa")} · pasto ${delta("pct_pastagem")}`;
  }

  // -------------------- mapa cross-fade --------------------
  let anoAtual = null;
  let camadaAtual = "cobertura";

  // Periodos do mapa de transicoes (5 imagens disponiveis em img/mapas_transicoes/).
  const PERIODOS_TRANSICAO = [
    { ini: 1985, fim: 1995 },
    { ini: 1995, fim: 2005 },
    { ini: 2005, fim: 2015 },
    { ini: 2015, fim: 2024 },
  ];
  function periodoTransicao(ano) {
    for (const p of PERIODOS_TRANSICAO) {
      if (ano >= p.ini && ano <= p.fim) return p;
    }
    return PERIODOS_TRANSICAO[PERIODOS_TRANSICAO.length - 1];
  }

  function urlDoMapa(camada, ano) {
    switch (camada) {
      case "cobertura":  return `img/mapas_gee/cobertura_${ano}.webp`;
      case "delta":      return `img/mapas_delta/delta_${ano}.webp`;
      case "fogo":       return `img/mapas_fogo/fogo_${ano}.webp`;
      case "transicoes": {
        const p = periodoTransicao(ano);
        return `img/mapas_transicoes/transicao_${p.ini}-${p.fim}.webp`;
      }
      default: return `img/mapas_gee/cobertura_${ano}.webp`;
    }
  }

  function altDoMapa(camada, ano) {
    switch (camada) {
      case "cobertura":  return `Cobertura LULC em Goiás em ${ano}`;
      case "delta":      return `Variação acumulada da cobertura em Goiás (${ano} vs 1985)`;
      case "fogo":       return `Cicatrizes de fogo em Goiás em ${ano}`;
      case "transicoes": {
        const p = periodoTransicao(ano);
        return `Transição dominante em Goiás entre ${p.ini} e ${p.fim}`;
      }
      default: return `Mapa de Goiás em ${ano}`;
    }
  }

  function trocarMapa(ano, forcar) {
    if (!forcar && ano === anoAtual) return;
    anoAtual = ano;
    const img = document.getElementById("mapa");
    const frame = img.closest(".map-frame");
    const yearLabel = document.getElementById("map-year");

    frame.classList.add("is-fading");
    const src = urlDoMapa(camadaAtual, ano);
    const next = new Image();
    next.onload = () => {
      img.src = src;
      img.alt = altDoMapa(camadaAtual, ano);
      yearLabel.textContent = ano;
      requestAnimationFrame(() => frame.classList.remove("is-fading"));
    };
    next.onerror = () => frame.classList.remove("is-fading");
    next.src = src;

    atualizarBarra(ano);
    atualizarAncora(ano);
  }

  // Mapeia data-class da barra empilhada -> CSS suffix do metric-card no step ativo.
  const BAR_TO_CARD_CLASS = {
    veg:    "veg",
    pasto:  "pasto",
    agric:  "agric",
    agua:   null,
    urbano: null,
    outros: null,
  };

  function configurarHighlightBarra() {
    const segmentos = document.querySelectorAll("#composition-bar .bar-segment");
    if (segmentos.length === 0) return;
    const img = document.getElementById("mapa");

    segmentos.forEach(seg => {
      seg.addEventListener("mouseenter", () => {
        const cls = seg.dataset.class;
        // destaca o segmento
        document.querySelectorAll("#composition-bar .bar-segment")
          .forEach(s => s.classList.toggle("bar-segment--dim",
            s.dataset.class !== cls));
        // dessatura levemente o mapa para sinalizar foco
        if (img) img.classList.add("mapa--focused");
        // destaca card correspondente no step ativo
        const cardSuffix = BAR_TO_CARD_CLASS[cls];
        if (cardSuffix) {
          const ativo = document.querySelector(".step[data-year].is-active");
          if (ativo) {
            const card = ativo.querySelector(`.metric-card--${cardSuffix}`);
            if (card) card.classList.add("metric-card--highlight");
          }
        }
      });
      seg.addEventListener("mouseleave", () => {
        document.querySelectorAll("#composition-bar .bar-segment")
          .forEach(s => s.classList.remove("bar-segment--dim"));
        if (img) img.classList.remove("mapa--focused");
        document.querySelectorAll(".metric-card--highlight")
          .forEach(c => c.classList.remove("metric-card--highlight"));
      });
    });
  }

  function configurarToggleCamadas() {
    const botoes = document.querySelectorAll(".map-layer-btn");
    botoes.forEach(btn => {
      btn.addEventListener("click", () => {
        const camada = btn.dataset.layer;
        if (camada === camadaAtual) return;
        camadaAtual = camada;
        botoes.forEach(b => {
          const ativo = b.dataset.layer === camada;
          b.classList.toggle("is-active", ativo);
          b.setAttribute("aria-selected", ativo ? "true" : "false");
        });
        if (anoAtual != null) trocarMapa(anoAtual, true);
      });
    });
  }

  // -------------------- gerar steps anuais --------------------
  function gerarStepsAnuais() {
    const eraRanges = [
      { era: 'heranca',  ato: 'I',   start: 1985, end: 2000 },
      { era: 'expansao', ato: 'II',  start: 2001, end: 2019 },
      { era: 'conversao', ato: 'III', start: 2020, end: 2024 },
    ];
    eraRanges.forEach(({ era, ato, start, end }) => {
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
      // Container do mini-sankey ao final do ato (depois do ultimo ano).
      // SEM data-year para que scrollama nao trate como step de ano.
      const mini = document.createElement('aside');
      mini.className = 'step--mini-sankey';
      mini.dataset.ato = ato;
      mini.innerHTML = `
        <h3 class="mini-sankey-titulo">Para onde foram os hectares — ATO ${ato}</h3>
        <p class="mini-sankey-lede">Transições brutas acumuladas entre ${start} e ${end}, em milhões de hectares (off-diagonal apenas).</p>
        <div class="mini-sankey-svg" data-ato="${ato}" role="img" aria-label="Sankey de transicoes do ATO ${ato}"></div>
        <p class="mini-sankey-fonte">Dados: MapBiomas Coleção 10.1 · agregação pixel-a-pixel via GEE.</p>
      `;
      anchor.insertAdjacentElement('afterend', mini);
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
        offset: 0.5,
        progress: false
      })
      .onStepEnter(({ element }) => {
        const ano = parseInt(element.dataset.year, 10);
        document.querySelectorAll(".step[data-year].is-active").forEach(s => s.classList.remove("is-active"));
        element.classList.add("is-active");
        trocarMapa(ano);
        moverCursorRegua(ano);
        atualizarResumoRegua(ano);
        moverCursorSparkline(ano);
      });

    window.addEventListener("resize", () => scroller.resize());
  }

  // -------------------- navegacao programatica --------------------
  // Debounce evita conflitos entre cliques em sparkline/subrota/hash e o
  // proprio Scrollama. Calcula offset compensando regua + tabs sticky.
  let scrollLock = 0;
  function scrollParaAno(ano, triggerPct) {
    const agora = performance.now();
    if (agora - scrollLock < 400) return;
    scrollLock = agora;
    const alvo = document.querySelector(`.step[data-year="${ano}"]`);
    if (!alvo) return;
    const rect = alvo.getBoundingClientRect();
    const topo = rect.top + window.pageYOffset;
    // O Scrollama dispara pelo viewport inteiro, nao pela "area util"
    // abaixo dos sticky headers. Para os pinos nao cairem no ano anterior
    // ao navegar para frente, o topo do step precisa terminar um pouco
    // acima da linha de ativacao (~50% da viewport total).
    const viewportH = window.innerHeight;
    const pct = triggerPct == null ? 0.46 : triggerPct;
    const destino = topo - viewportH * pct;
    window.scrollTo({ top: destino, behavior: "smooth" });
  }

  // -------------------- subrota (chamado pelo router) --------------------
  function aplicarSubrota(segmentos) {
    // segmentos: [] | [ano]
    if (!segmentos || segmentos.length === 0) return;
    const ano = parseInt(segmentos[0], 10);
    if (isNaN(ano) || ano < ANO_MIN || ano > ANO_MAX) return;
    scrollParaAno(ano);
  }

  // -------------------- bootstrap --------------------
  async function init() {
    try {
      const dados = await carregarDados();
      porAno = Object.fromEntries(dados.painel.serie.map(r => [r.ano, r]));
      configurarRegua(dados.marcos);
      gerarStepsAnuais();
      hidratarSteps(dados.painel, dados.marcos);
      desenharSparkline(dados.painel);
      atualizarBarra(ANO_MIN);
      atualizarAncora(ANO_MIN);
      configurarToggleCamadas();
      configurarHighlightBarra();
      inicializarScrollama();
    } catch (err) {
      console.error("Erro ao inicializar timeline:", err);
      const cont = document.getElementById("inventario-grid");
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
