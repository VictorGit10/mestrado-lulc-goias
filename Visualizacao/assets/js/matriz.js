/* matriz.js — Matriz de transição com toggle %/Mha e seletor de período.
 * Renderiza a tabela dinamicamente a partir de transicoes_matriz.json.
 * Default: modo %, período 1985→2024.
 * Lazy-load: só faz fetch quando o <details> é aberto pela primeira vez.
 *
 * A ordem e a quantidade de classes vêm do JSON (`periodo.classes`), nunca de
 * uma constante local: o #12B levou a matriz de 6 para 7 grupos (o Mosaico de
 * Usos passou a existir) e uma iteração fixa em 6 esconderia a linha e a coluna
 * novas sem erro nenhum — justamente onde mora o achado.
 */
(function (root) {
  "use strict";

  var G = root.GO40 || {};
  var data = null;
  var modoAtual = "pct";      // "pct" | "mha"
  var periodoIdx = 4;         // índice do período (4 = 1985→2024, o último)

  // Rótulo curto por nome de classe do JSON. Classe ausente daqui cai no próprio
  // nome do JSON — aparece feia, mas aparece.
  var ROTULO_CURTO = {
    "Vegetacao Natural": "Veg. natural",
    "Pastagem": "Pastagem",
    "Agricultura": "Agricultura",
    "Agua": "Água",
    "Area Urbana": "Urbano",
    "Outros": "Outros",
    "Mosaico de Usos": "Mosaico"
  };

  function rotulo(nomeClasse) {
    return ROTULO_CURTO[nomeClasse] || nomeClasse;
  }

  // ---------- formatação ----------

  function fmtPct(v) {
    if (v < 0.1 && v > 0) return "< 0,1%";
    if (v === 0) return "0%";
    return v.toFixed(1).replace(".", ",") + "%";
  }

  function fmtMha(v) {
    var mha = v / 1e6;
    if (mha === 0) return "0";
    if (mha < 0.005) return "< 0,01";
    return mha.toFixed(2).replace(".", ",");
  }

  // ---------- renderização ----------

  function renderizar() {
    if (!data) return;
    var p = data.periodos[periodoIdx];
    var matriz = modoAtual === "pct" ? p.matriz_pct : p.matriz;
    var fmt = modoAtual === "pct" ? fmtPct : fmtMha;
    var isPct = modoAtual === "pct";
    var classes = p.classes;
    var n = classes.length;

    // Container da tabela
    var container = document.getElementById("matriz-container");
    if (!container) return;

    // Construir <table>
    var html = '<div style="overflow-x: auto;">';
    html += '<table class="camadas-tabela" style="margin: 0;">';

    // Cabeçalho
    html += "<thead><tr>";
    html += "<th>Origem ↓ / Destino →</th>";
    for (var j = 0; j < n; j++) {
      html += '<th style="text-align:right;">' + rotulo(classes[j]) + "</th>";
    }
    html += "</tr></thead>";

    // Corpo
    html += "<tbody>";
    for (var i = 0; i < n; i++) {
      html += "<tr>";
      html += "<td>" + rotulo(classes[i]) + "</td>";
      for (var j = 0; j < n; j++) {
        var v = matriz[i][j];
        var isDiag = i === j;
        var isDestaque = isPct
          ? (v > 5 && !isDiag)   // off-diagonal > 5%
          : (v > 5e5 && !isDiag); // off-diagonal > 0,5 Mha
        var cls = (isDiag ? " matriz-diagonal" : "") + (isDestaque ? " matriz-destaque" : "");
        html += '<td style="text-align:right; font-variant-numeric: tabular-nums;" class="' + cls.trim() + '">';
        html += fmt(v);
        html += "</td>";
      }
      html += "</tr>";
    }
    html += "</tbody></table></div>";

    container.innerHTML = html;

    // Caption
    var caption = document.getElementById("matriz-caption");
    if (caption) {
      if (isPct) {
        caption.textContent =
          "Cada linha soma 100%. A diagonal mostra a porcentagem que permaneceu na mesma classe; " +
          "as células fora da diagonal mostram para onde a área foi convertida. O Mosaico de Usos " +
          "(lavoura ou pasto, que o classificador não separa) entra como classe própria. " +
          "Fonte: MapBiomas Coleção 10.1 (Pipeline #12B).";
      } else {
        caption.textContent =
          "Valores em milhões de hectares (Mha). Na diagonal, os pixels que permaneceram na mesma " +
          "classe; fora dela, as transições. O Mosaico de Usos (lavoura ou pasto, que o classificador " +
          "não separa) entra como classe própria. " +
          "Fonte: MapBiomas Coleção 10.1 (Pipeline #12B).";
      }
    }

    // Atualizar botões de toggle
    var btns = document.querySelectorAll(".matriz-toggle-btn");
    for (var k = 0; k < btns.length; k++) {
      btns[k].classList.toggle("active", btns[k].dataset.modo === modoAtual);
    }

    // Atualizar botões de período
    var pBtns = document.querySelectorAll(".matriz-periodo-btn");
    for (var k = 0; k < pBtns.length; k++) {
      pBtns[k].classList.toggle("active", parseInt(pBtns[k].dataset.idx) === periodoIdx);
    }
  }

  // ---------- toggle e período ----------

  function alternarModo(novoModo) {
    if (novoModo === modoAtual) return;
    modoAtual = novoModo;
    renderizar();
  }

  function trocarPeriodo(idx) {
    if (idx === periodoIdx) return;
    periodoIdx = idx;
    renderizar();
  }

  // ---------- inicialização ----------

  function carregarErenderizar() {
    if (data) {
      renderizar();
      return;
    }
    var basePath = document.querySelector('script[src*="matriz.js"]');
    var baseUrl = basePath ? basePath.src.replace(/matriz\.js.*$/, "") : "assets/data/";
    var url = baseUrl + "transicoes_matriz.json";
    // Corrigir: usar caminho relativo à raiz do site
    url = "assets/data/transicoes_matriz.json";

    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (json) {
        data = json;
        renderizar();
      })
      .catch(function (err) {
        console.error("[matriz] Erro ao carregar dados:", err);
      });
  }

  function criarBotoes() {
    // Toggle % / Mha
    var toggleContainer = document.getElementById("matriz-toggle");
    if (!toggleContainer) return;
    toggleContainer.innerHTML =
      '<button class="matriz-toggle-btn active" data-modo="pct">%</button>' +
      '<button class="matriz-toggle-btn" data-modo="mha">Mha</button>';
    toggleContainer.addEventListener("click", function (e) {
      if (e.target.classList.contains("matriz-toggle-btn")) {
        alternarModo(e.target.dataset.modo);
      }
    });

    // Períodos
    if (!data) return;
    var periodosContainer = document.getElementById("matriz-periodos");
    if (!periodosContainer) return;
    var html = "";
    for (var i = 0; i < data.periodos.length; i++) {
      var p = data.periodos[i];
      var active = i === periodoIdx ? " active" : "";
      html += '<button class="matriz-periodo-btn' + active + '" data-idx="' + i + '">' +
              p.rotulo + "</button>";
    }
    periodosContainer.innerHTML = html;
    periodosContainer.addEventListener("click", function (e) {
      if (e.target.classList.contains("matriz-periodo-btn")) {
        trocarPeriodo(parseInt(e.target.dataset.idx));
      }
    });
  }

  function init() {
    var details = document.getElementById("matriz-details");
    if (!details) return;

    // Lazy-load: só carrega dados quando o details é aberto
    var carregado = false;
    details.addEventListener("toggle", function () {
      if (details.open && !carregado) {
        carregado = true;
        carregarErenderizar();
        criarBotoes();
      }
    });

    // Se já está aberto na carga da página
    if (details.open) {
      carregado = true;
      carregarErenderizar();
      criarBotoes();
    }
  }

  G.matriz = { init: init, renderizar: renderizar };
  root.GO40 = G;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);