/* timeline.js — orquestracao do scrollytelling.
 * Carrega dados, hidrata steps, inicializa Scrollama
 * e move cursores ao trocar de ano.
 */

(function (root) {
  "use strict";


  // i18n: em paginas que nao carregam i18n.js (ex.: index-original.html), T/TF
  // caem para a identidade e o texto original em portugues e' preservado.
  var _I18N = root.GO40I18N || null;
  var T  = _I18N ? _I18N.T  : function (s) { return s; };
  var TF = _I18N ? _I18N.TF : function (s) {
    var a = Array.prototype.slice.call(arguments, 1), o = String(s);
    for (var i = 0; i < a.length; i++) o = o.split("{" + i + "}").join(String(a[i]));
    return o;
  };
  const ANO_MIN = 1985;
  const ANO_MAX = 2024;
  const TOTAL_ANOS = ANO_MAX - ANO_MIN;

  // Formatacao numerica segue o idioma da pagina (ver i18n.js).
  const I18N = root.GO40I18N || { lang: "pt", T: s => s, num: { decimal: ",", locale: "pt-BR", bilhao: " bi" } };
  const dec = s => I18N.num.decimal === "," ? s.replace(".", ",") : s;

  const fmtPct = v => (v == null ? "—" : dec((v * 100).toFixed(1)) + "%");
  const fmtNum = (v, d = 0) => {
    if (v == null) return "—";
    return new Intl.NumberFormat(I18N.num.locale, { maximumFractionDigits: d }).format(v);
  };
  const fmtBilhao = v => v == null ? "—" : "R$ " + dec((v / 1e9).toFixed(1)) + I18N.num.bilhao;
  const fmtMilhao = v => v == null ? "—" : dec((v / 1e6).toFixed(2)) + " Mha";
  const fmtPctBar = v => dec((v * 100).toFixed(1)) + "%";
  const fmtPp = v => {
    if (v == null) return "";
    const abs = dec(Math.abs(v).toFixed(1));
    return `${abs} pp`;
  };

  const yearToPct = ano => ((ano - ANO_MIN) / TOTAL_ANOS) * 100;
  const ERA_RANGES = [
    {
      era: "heranca",
      ato: T("Ato I"),
      start: 1985,
      end: 2000,
      titulo: T("Pastagem como herança"),
      resumo: T("pastagem domina e a soja ainda é pontual")
    },
    {
      era: "expansao",
      ato: T("Ato II"),
      start: 2001,
      end: 2019,
      titulo: T("Expansão e intensificação"),
      resumo: T("soja avança sobre pastagem; intensificação sem fronteira")
    },
    {
      era: "conversao",
      ato: T("Ato III"),
      start: 2020,
      end: 2024,
      titulo: T("Conversão acelerada (mascarada)"),
      resumo: T("a pastagem cede três vezes mais rápido; a conversão acelera — e a medida crua esconde")
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
    return v == null ? '<span class="metric-na" title="' + T("sem dado neste ano") + '">—</span>' : formatador(v);
  }
  const fmtTon = v => {
    if (v >= 1e6) return fmtNum(v / 1e6, 2) + T(" Mt");
    if (v >= 1e3) return fmtNum(v / 1e3, 0) + " kt";
    return fmtNum(v, 0) + " t";
  };

  // -------------------- carregamento --------------------
  async function carregarDados() {
    const [painel, marcos] = await Promise.all([
      fetch("assets/data/painel_goias.json").then(r => r.json()),
      fetch(I18N.lang === "en" ? "assets/data/marcos.en.json" : "assets/data/marcos.json").then(r => r.json())
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
  // ▲ verde, ▼ terracota — consistência visual por direção.
  function classeDelta(cls, dpp) {
    if (Math.abs(dpp) < 0.05) return "delta--flat";
    return dpp > 0 ? "delta--up" : "delta--down";
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
  // As chaves de categoria sao slugs ASCII no JSON; trocar "_" por espaco
  // deixava "regulacao ambiental" e "credito publico" na tela.
  const ROTULO_CATEGORIA = {
    contexto: T("contexto"),
    macroeconomia: T("macroeconomia"),
    "tributação": T("tributação"),
    credito_publico: T("crédito público"),
    regulacao_ambiental: T("regulação ambiental"),
    mercado: T("mercado")
  };

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
        metricCard(T('Veg. natural'), fmtPct(dado.pct_vegetacao_nativa), formatDelta(dado.pct_vegetacao_nativa, prev ? prev.pct_vegetacao_nativa : null, 'veg'), 'veg'),
        metricCard(T('Pastagem'),    fmtPct(dado.pct_pastagem),         formatDelta(dado.pct_pastagem,         prev ? prev.pct_pastagem         : null, 'pasto'), 'pasto'),
        metricCard(T('Agricultura'), fmtPct(dado.pct_agricultura),      formatDelta(dado.pct_agricultura,      prev ? prev.pct_agricultura      : null, 'soja'), 'agric'),
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
        [T('Soja'),     dado.agri_soja_ton],
        [T('Milho'),    dado.agri_milho_total_ton],
        [T('Cana'),     dado.agri_cana_ton],
        [T('Algodão'),  dado.agri_algodao_ton],
        [T('Sorgo'),    dado.agri_sorgo_ton],
        [T('Arroz'),    dado.agri_arroz_ton],
        [T('Feijão'),   dado.agri_feijao_ton],
      ];
      const linhas = culturas
        .map(([nome, v]) => linhaTabela(nome, valorOuTraco(v, fmtTon)))
        .join('');
      return acordeao('agro', T('Produção agrícola (toneladas)'), linhas);
    }

    function acordeaoPecuaria(dado) {
      const linhas = [
        linhaTabela(T('Rebanho bovino'), valorOuTraco(dado.pec_bovinos_cab, v => fmtNum(v / 1e6, 2) + T(' M cab'))),
        linhaTabela(T('Lotação'),        valorOuTraco(dado.lotacao_bov_ha_pasto, v => fmtNum(v, 2) + T(' cab/ha'))),
        linhaTabela(T('Leite'),          valorOuTraco(dado.agri_leite_mil_litros, v => fmtNum(v / 1e3, 1) + T(' Mi L'))),
      ].join('');
      return acordeao('pecuaria', T('Pecuária'), linhas);
    }

    function acordeaoSocio(dado) {
      const linhas = [
        linhaTabela(T('PIB (IPEA UF)'),     valorOuTraco(dado.pib_uf_real_rs,     fmtBilhao), T('IBGE Contas Reg., 1985+')),
        linhaTabela(T('PIB (Σ municípios)'), valorOuTraco(dado.pib_real_rs,        fmtBilhao), T('SIDRA 5938, 2002+')),
        linhaTabela(T('VA Agro (IPEA UF)'),     valorOuTraco(dado.va_agro_uf_real_rs, fmtBilhao), T('IBGE Contas Reg., 1985+')),
        linhaTabela(T('VA Agro (Σ municípios)'), valorOuTraco(dado.va_agro_real_rs,    fmtBilhao), T('SIDRA 5938, 2002+')),
        linhaTabela(T('Crédito rural'), valorOuTraco(dado.sicor_total_real_rs, fmtBilhao), T('desde 2013')),
        linhaTabela(T('População'),     valorOuTraco(dado.populacao,           v => fmtNum(v / 1e6, 2) + T(' Mi')), T('desde 2001')),
      ].join('');
      return acordeao('socio', T('Socioeconômico'), linhas);
    }

    document.querySelectorAll(".step[data-year]").forEach(step => {
      const ano = parseInt(step.dataset.year, 10);
      const dado = porAno[ano];
      const prev = porAno[ano - 1];
      const marco = marcosPorAnoLocal[ano];

      let html = "";
      if (marco) {
        step.classList.add("step--marco");
        const rotuloCat = ROTULO_CATEGORIA[marco.categoria] || marco.categoria.replace(/_/g, " ");
        html += '<span class="marco-tag">' + ano + ' · ' + rotuloCat + '</span>';
        html += '<h3 class="marco-titulo">' + marco.titulo + '</h3>';
        if (marco.subtitulo) html += '<p class="marco-subtitulo">' + marco.subtitulo + '</p>';
        html += '<p class="marco-descricao">' + marco.descricao + '</p>';
        // Selo curto e sempre igual: o card justapoe marco e serie, mas nao
        // testa um contra o outro. Identico em todos, vira rotulo e nao prosa.
        // Fica de fora dos marcos de "contexto" (1985 e 2024), que sao as
        // pontas da serie e nao tem nada a testar.
        if (marco.categoria !== "contexto") {
          html += '<p class="marco-ressalva">' + T("Contexto: os números abaixo acompanham o marco, não o testam.") + '</p>';
        }
      } else {
        html += '<span class="marco-tag muted-year">' + ano + '</span>';
      }

      if (dado) {
        html += '<div class="metric-grid metric-grid--lulc">' + cardsLULC(dado, prev) + '</div>';
        // A seta em pp e ano-a-ano; o caption do mapa mostra o acumulado desde
        // 1985. Sem esta linha os dois "pp" da tela ficam sem base declarada.
        if (prev) html += '<p class="metric-grid-base">' + TF("▲▼ em pp vs. {0}", ano - 1) + '</p>';
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

  // -------------------- barra empilhada --------------------
  // 7 segmentos: veg natural, pastagem, agricultura (inclui soja no MapBiomas),
  // mosaico agric./pastagem, água, área urbana, outros (silvicultura +
  // mineração + não-mapeados).
  //
  // O Mosaico ganhou faixa própria em jul/2026. Antes ele caía dentro de
  // "Outros" — uma escolha neutra quando a classe era pequena, que virou omissão
  // quando ela passou a absorver a conversão do fim da série (D25): em 2024 são
  // 10,5% do estado, contra 1,0% de tudo o mais somado. O mapa raster continua
  // sem pintá-la (`selfMask()` no GEE), e a legenda declara isso.
  function atualizarBarra(ano) {
    const dado = porAno[ano];
    if (!dado) return;
    const veg = dado.pct_vegetacao_nativa || 0;
    const pasto = dado.pct_pastagem || 0;
    const agric = dado.pct_agricultura || 0;
    const mosaico = dado.pct_mosaico || 0;
    const agua = dado.pct_agua || 0;
    const urbano = dado.pct_area_urbana || 0;
    const outros = Math.max(0, 1 - veg - pasto - agric - mosaico - agua - urbano);

    const map = { veg, pasto, agric, mosaico, agua, urbano, outros };
    const nomes = {
      veg: T("Vegetação natural"),
      pasto: T("Pastagem"),
      agric: T("Agricultura"),
      mosaico: T("Mosaico de usos"),
      agua: T("Água"),
      urbano: T("Área urbana"),
      outros: T("Outros")
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
  // O caption e os cards laterais mostram os dois "pp" da tela e precisam dizer
  // qual e qual: aqui e o ACUMULADO desde 1985; la e a variacao ano a ano.
  function atualizarAncora(ano) {
    const ancora = document.getElementById("map-anchor");
    if (!ancora) return;
    if (camadaAtual === "transicoes") {
      ancora.textContent = T("destino dominante no período");
      return;
    }
    const cur = porAno[ano];
    const base = porAno[ANO_MIN];
    if (!cur || !base) {
      ancora.textContent = "";
      return;
    }
    if (ano === ANO_MIN) {
      ancora.textContent = T("linha de base");
      return;
    }
    const delta = (chave) => {
      const dpp = (cur[chave] - base[chave]) * 100;
      const sinal = dpp > 0 ? "+" : "−";
      return sinal + fmtPp(dpp);
    };
    ancora.textContent = TF("acumulado desde 1985: veg {0} · pasto {1}", delta("pct_vegetacao_nativa"), delta("pct_pastagem"));
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

  // Os mapas trazem título e legenda desenhados na imagem: a variante inglesa
  // tem o seu par *.en.webp, gerado pelos mesmos scripts com --lang en.
  const SUFIXO_MAPA = I18N.lang === "en" ? ".en" : "";

  function urlDoMapa(camada, ano) {
    if (camada === "transicoes") {
      const p = periodoTransicao(ano);
      return `img/mapas_transicoes/transicao_${p.ini}-${p.fim}${SUFIXO_MAPA}.webp`;
    }
    return `img/mapas_gee/cobertura_${ano}${SUFIXO_MAPA}.webp`;
  }

  function altDoMapa(camada, ano) {
    if (camada === "transicoes") {
      const p = periodoTransicao(ano);
      return TF("Transição dominante por município em Goiás entre {0} e {1}", p.ini, p.fim);
    }
    return TF("Cobertura e uso da terra em Goiás em {0}", ano);
  }

  // Cada camada tem unidade espacial e fonte proprias. Antes de ago/2026 a
  // legenda e o caption ficavam parados em "pixel-a-pixel (30 m)" enquanto a
  // imagem trocava — inclusive para coropleticos. Agora trocam juntos.
  const FONTE_CAMADA = {
    cobertura:
      T('Fonte: MapBiomas Coleção 10.1 &middot; pixel-a-pixel (30&nbsp;m) &middot; ' +
        'o mapa é reduzido para caber na tela, então classes fragmentadas encolhem ' +
        'no desenho: a medida está na barra acima'),
    transicoes:
      T('Fonte: MapBiomas Coleção 10.1 &middot; agregado <strong>por município</strong>, ' +
        'não por pixel &middot; a partir de 2015 o destino dominante na maior parte do estado ' +
        'é o <em>Mosaico de usos</em>, o que é mudança de rótulo tanto quanto de uso ' +
        '(<a href="dossie-mosaico.html">a investigação</a>)')
  };

  function rotuloDoAno(camada, ano) {
    if (camada === "transicoes") {
      const p = periodoTransicao(ano);
      return `${p.ini}–${p.fim}`;
    }
    return String(ano);
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
      yearLabel.textContent = rotuloDoAno(camadaAtual, ano);
      requestAnimationFrame(() => frame.classList.remove("is-fading"));
    };
    next.onerror = () => frame.classList.remove("is-fading");
    next.src = src;

    atualizarBarra(ano);
    atualizarAncora(ano);
  }

  // Legenda, barra de composicao e fonte pertencem a camada, nao ao ano.
  function aplicarCamada(camada) {
    const legCob = document.getElementById("map-legend-cobertura");
    const legTr = document.getElementById("map-legend-transicoes");
    const barra = document.getElementById("composition-bar");
    const fonte = document.getElementById("map-source");
    const ehTransicoes = camada === "transicoes";

    if (legCob) legCob.hidden = ehTransicoes;
    if (legTr) legTr.hidden = !ehTransicoes;
    // A barra mede a composicao de UM ano; no mapa de periodo ela nao se aplica.
    if (barra) barra.hidden = ehTransicoes;
    if (fonte) fonte.innerHTML = FONTE_CAMADA[camada] || FONTE_CAMADA.cobertura;
  }

  // Mapeia data-class da barra empilhada -> CSS suffix do metric-card no step ativo.
  const BAR_TO_CARD_CLASS = {
    veg:     "veg",
    pasto:   "pasto",
    agric:   "agric",
    mosaico: null,   // não tem metric-card próprio nos steps
    agua:    null,
    urbano:  null,
    outros:  null,
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
        aplicarCamada(camada);
        if (anoAtual != null) trocarMapa(anoAtual, true);
      });
    });
  }

  // -------------------- gerar steps anuais --------------------
  function gerarStepsAnuais() {
    const eraRanges = [
      { era: 'heranca',  ato: 'I',   start: 1985, end: 2000,
        lede: T('Para onde foram os hectares entre 1985 e 2000: cruzamento pixel-a-pixel das transições deste período.') },
      { era: 'expansao', ato: 'II',  start: 2001, end: 2019,
        lede: T('Para onde foram os hectares entre 2001 e 2019: o período da grande expansão agrícola sobre a pastagem.') },
      { era: 'conversao', ato: 'III', start: 2020, end: 2024,
        lede: T('Para onde foram os hectares entre 2020 e 2024: a conversão acelera sobre a pastagem — e o mapa, sozinho, diz o contrário.') },
    ];
    eraRanges.forEach(({ era, ato, start, end, lede }) => {
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
        <p class="mini-sankey-titulo">${TF("Fluxos do Ato {0}", ato)}</p>
        <p class="mini-sankey-lede">${lede}</p>
        <div class="mini-sankey-svg" data-ato="${ato}" role="img" aria-label="${TF("Sankey de transições do Ato {0}", ato)}"></div>
        <p class="mini-sankey-fonte">${T("Fonte: MapBiomas Col. 10.1 · Pipeline #25")}</p>
      `;
      anchor.insertAdjacentElement('afterend', mini);
    });

    // Os containers do mini-sankey so existem agora (gerados acima). Dispara a
    // inicializacao do observer apos a geracao, evitando a corrida com o
    // self-init por timeout de mini-sankey.js (que roda antes do fetch acabar).
    if (root.GO40 && root.GO40.miniSankey) root.GO40.miniSankey.init();
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
      });

    window.addEventListener("resize", () => scroller.resize());
  }

  // -------------------- navegacao programatica --------------------
  // Debounce evita conflitos entre cliques na regua/subrota/hash e o
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
    window.scrollTo({ top: destino, behavior: comportamentoScroll() });
  }

  // Respeita prefers-reduced-motion: rolagem instantanea em vez de suave.
  function comportamentoScroll() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto" : "smooth";
  }

  // -------------------- subrota (chamado pelo router) --------------------
  function aplicarSubrota(segmentos) {
    // segmentos: [] | [ano] | [id-de-ancora]
    if (!segmentos || segmentos.length === 0) return;
    const ano = parseInt(segmentos[0], 10);
    if (!isNaN(ano) && ano >= ANO_MIN && ano <= ANO_MAX) {
      scrollParaAno(ano);
      return;
    }
    // Ancora nao-numerica (secoes pos-mapas, ex.: #narrativa/sec-tese).
    const alvo = document.getElementById(segmentos[0]);
    if (alvo) {
      requestAnimationFrame(() => {
        const topo = alvo.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({ top: Math.max(0, topo - 150), behavior: comportamentoScroll() });
      });
    }
  }

  // -------------------- bootstrap --------------------
  async function init() {
    try {
      const dados = await carregarDados();
      porAno = Object.fromEntries(dados.painel.serie.map(r => [r.ano, r]));
      configurarRegua(dados.marcos);
      gerarStepsAnuais();
      hidratarSteps(dados.painel, dados.marcos);
      atualizarBarra(ANO_MIN);
      atualizarAncora(ANO_MIN);
      aplicarCamada(camadaAtual);
      configurarToggleCamadas();
      configurarHighlightBarra();
      inicializarScrollama();
    } catch (err) {
      console.error("Erro ao inicializar timeline:", err);
      const cont = document.getElementById("inventario-grid");
      if (cont) {
        cont.innerHTML =
          `<p class="resumo-loading" style="color:#8b3a1d">` +
          TF("Falha ao carregar dados: {0}. ", err.message) +
          T("Se voce abriu via duplo-clique, use o servir.bat ou servir.ps1.") + `</p>`;
      }
    }
    root.GO40 = root.GO40 || {};
    root.GO40.narrativa = { aplicarSubrota };
    // O router aplica a rota inicial antes deste init assincrono terminar;
    // reaplica a subrota da carga (deep-link p/ ano ou ancora pos-mapas).
    if (root.GO40.router) {
      const rota = root.GO40.router.parseHash();
      if (rota.modo === "narrativa" && rota.segmentos.length > 0) {
        aplicarSubrota(rota.segmentos);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
