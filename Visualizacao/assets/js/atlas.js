/* atlas.js — Modo Atlas: parede de 40 mapas com toggle de variavel.
 * Estrutura:
 *   - renderiza grid de miniaturas
 *   - bind toolbar (LULC | Fogo | Transicoes | Delta)
 *   - click em miniatura abre lightbox (placeholder por ora)
 *   - shift+click adiciona ao modo Comparar (fase 2)
 *   - registra GO40.atlas.aplicarSubrota para o router
 *
 * MVP: so LULC esta ativo. Outras variaveis ficam disabled ate Fase A.
 */

(function (root) {
  "use strict";

  const G = root.GO40 || {};
  const { ANO_MIN, ANO_MAX, ANOS_MARCO, VARIAVEIS_ATLAS, eraDoAno } = G;

  let varAtual = "lulc";
  let lightboxAberto = null;

  // Periodos das transicoes (Pipeline #12) — usado quando varAtual === 'transicoes'.
  const PERIODOS_TRANSICAO = [
    { id: "1985-1995", rotulo: "1985 → 1995" },
    { id: "1995-2005", rotulo: "1995 → 2005" },
    { id: "2005-2015", rotulo: "2005 → 2015" },
    { id: "2015-2024", rotulo: "2015 → 2024" },
    { id: "1985-2024", rotulo: "1985 → 2024 (total)" }
  ];

  function pathMapa(variavel, chave) {
    const meta = VARIAVEIS_ATLAS.find(v => v.id === variavel);
    if (!meta) return null;
    return `${meta.pasta}/${meta.prefixo}${chave}.${meta.ext}`;
  }

  function rotuloDescritivo(variavel) {
    const map = {
      lulc: "Uso e cobertura da terra · pixel-a-pixel 30m · MapBiomas Coleção 10.1",
      fogo: "Área queimada por município · escala log · MapBiomas Coleção 4",
      transicoes: "Transições pixel-a-pixel · pares de anos · 6 classes",
      delta: "Δ %pastagem vs. 1985 · diverging · valores positivos = expansão"
    };
    return map[variavel] || "";
  }

  // -------------------- render do grid --------------------
  function renderGrid(variavel) {
    const grid = document.getElementById("atlas-grid");
    if (!grid) return;
    varAtual = variavel;
    const meta = VARIAVEIS_ATLAS.find(v => v.id === variavel);
    if (!meta) return;

    grid.dataset.variavel = variavel;
    grid.dataset.coluna = (variavel === "transicoes") ? "5" : "8";

    const itens = [];

    if (variavel === "transicoes") {
      // 5 cards de periodos.
      PERIODOS_TRANSICAO.forEach(p => {
        const era = eraDoAno(parseInt(p.id.split("-")[0], 10));
        itens.push(`
          <button class="atlas-cell atlas-cell--periodo" data-chave="${p.id}" data-era="${era ? era.id : ""}" title="${p.rotulo}">
            <span class="atlas-cell-img-wrap">
              <img loading="lazy" decoding="async" src="${pathMapa(variavel, p.id)}" alt="Mapa de transição ${p.rotulo}"
                   onerror="this.classList.add('img-fail')">
            </span>
            <span class="atlas-cell-ano">${p.rotulo}</span>
          </button>
        `);
      });
    } else {
      // 40 mapas anuais (1985..2024).
      for (let ano = ANO_MIN; ano <= ANO_MAX; ano++) {
        const era = eraDoAno(ano);
        const isMarco = ANOS_MARCO.has(ano);
        itens.push(`
          <button class="atlas-cell ${isMarco ? "atlas-cell--marco" : ""}" data-chave="${ano}" data-era="${era ? era.id : ""}" title="${ano}">
            <span class="atlas-cell-img-wrap">
              <img loading="lazy" decoding="async" src="${pathMapa(variavel, ano)}" alt="Mapa ${meta.rotulo} ${ano}"
                   onerror="this.classList.add('img-fail')">
            </span>
            <span class="atlas-cell-ano">${ano}${isMarco ? "<span class=\"atlas-cell-pino\" aria-hidden=\"true\"></span>" : ""}</span>
          </button>
        `);
      }
    }

    grid.innerHTML = itens.join("");

    // Bind clicks.
    grid.querySelectorAll(".atlas-cell").forEach(cell => {
      cell.addEventListener("click", onCellClick);
    });

    // Atualiza label informativa.
    const label = document.getElementById("atlas-var-label");
    if (label) label.textContent = rotuloDescritivo(variavel);

    // Atualiza legenda
    renderLegenda(variavel);
  }

  // -------------------- legenda --------------------
  function renderLegenda(variavel) {
    const cont = document.getElementById("atlas-legend");
    if (!cont) return;
    if (variavel === "lulc") {
      cont.innerHTML = `
        <span class="atlas-leg-titulo">Classes LULC</span>
        <span class="legend-swatch legend-swatch--veg">Vegetação natural</span>
        <span class="legend-swatch legend-swatch--pasto">Pastagem</span>
        <span class="legend-swatch legend-swatch--agric">Agricultura</span>
        <span class="legend-swatch legend-swatch--mosaico">Mosaico</span>
        <span class="legend-swatch legend-swatch--agua">Água</span>
        <span class="legend-swatch legend-swatch--urbano">Urbano</span>
        <span class="legend-swatch legend-swatch--outros">Outros</span>
      `;
    } else if (variavel === "fogo") {
      cont.innerHTML = `<span class="atlas-leg-titulo">Área queimada (escala log)</span>
        <span class="atlas-leg-grad atlas-leg-grad--fogo"></span>
        <span class="atlas-leg-min">menor</span><span class="atlas-leg-max">maior</span>`;
    } else if (variavel === "delta") {
      cont.innerHTML = `<span class="atlas-leg-titulo">Δ %pastagem vs. 1985</span>
        <span class="atlas-leg-grad atlas-leg-grad--delta"></span>
        <span class="atlas-leg-min">retração (verde)</span><span class="atlas-leg-max">expansão (vermelho)</span>`;
    } else {
      cont.innerHTML = `<span class="atlas-leg-titulo">Transição dominante por município no período</span>`;
    }
  }

  // -------------------- click handlers --------------------
  function onCellClick(ev) {
    ev.preventDefault();
    const cell = ev.currentTarget;
    const chave = cell.dataset.chave;
    if (ev.shiftKey) {
      // Modo Comparar — placeholder fase 2.
      console.info("[atlas] shift+click (Comparar): pendente fase 2", chave);
      return;
    }
    if (ev.ctrlKey || ev.metaKey) {
      // Vai para narrativa naquele ano (so faz sentido em variaveis anuais).
      if (G.router && /^\d{4}$/.test(chave)) {
        G.router.ir("narrativa", chave);
      }
      return;
    }
    abrirLightbox(varAtual, chave);
  }

  // -------------------- lightbox --------------------
  function abrirLightbox(variavel, chave) {
    fecharLightbox();
    const meta = VARIAVEIS_ATLAS.find(v => v.id === variavel);
    const src = pathMapa(variavel, chave);
    const ehAno = /^\d{4}$/.test(chave);
    const eraNum = ehAno ? eraDoAno(parseInt(chave, 10)) : null;
    const isMarco = ehAno && ANOS_MARCO.has(parseInt(chave, 10));

    const overlay = document.createElement("div");
    overlay.className = "atlas-lightbox";
    overlay.innerHTML = `
      <div class="atlas-lightbox-backdrop"></div>
      <div class="atlas-lightbox-frame" role="dialog" aria-modal="true" aria-label="Mapa ampliado ${chave}">
        <button class="atlas-lightbox-close" aria-label="Fechar">×</button>
        <div class="atlas-lightbox-img">
          <img src="${src}" alt="Mapa ampliado ${meta.rotulo} ${chave}">
        </div>
        <div class="atlas-lightbox-info">
          <div class="atlas-lightbox-titulo">
            <span class="atlas-lightbox-chave">${chave}${isMarco ? " ·" : ""}</span>
            ${isMarco ? `<span class="atlas-lightbox-marco">marco político</span>` : ""}
          </div>
          ${eraNum ? `<div class="atlas-lightbox-era" style="border-left-color:${eraNum.cor}"><strong>${eraNum.titulo}</strong></div>` : ""}
          <div class="atlas-lightbox-fonte">${rotuloDescritivo(variavel)}</div>
          <div class="atlas-lightbox-acoes">
            ${ehAno ? `<button class="atlas-lightbox-btn" data-acao="narrativa">Ver no modo Narrativa →</button>` : ""}
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    lightboxAberto = overlay;

    overlay.querySelector(".atlas-lightbox-backdrop").addEventListener("click", fecharLightbox);
    overlay.querySelector(".atlas-lightbox-close").addEventListener("click", fecharLightbox);
    document.addEventListener("keydown", onKeyLightbox);

    overlay.querySelectorAll("[data-acao]").forEach(btn => {
      btn.addEventListener("click", () => {
        const acao = btn.dataset.acao;
        if (acao === "narrativa" && G.router) G.router.ir("narrativa", chave);
      });
    });

    // Sync URL hash sem disparar reload da rota.
    if (G.router) {
      const h = `#atlas/${variavel}/${chave}`;
      if (root.location.hash !== h) {
        history.replaceState(null, "", h);
      }
    }
  }

  function fecharLightbox() {
    if (lightboxAberto) {
      lightboxAberto.remove();
      lightboxAberto = null;
      document.removeEventListener("keydown", onKeyLightbox);
      // Limpa segmento da URL preservando variavel.
      if (G.router && root.location.hash.match(/#atlas\/\w+\/\S+/)) {
        history.replaceState(null, "", `#atlas/${varAtual}`);
      }
    }
  }

  function onKeyLightbox(ev) {
    if (ev.key === "Escape") fecharLightbox();
  }

  // -------------------- toolbar --------------------
  function bindToolbar() {
    document.querySelectorAll(".atlas-var").forEach(btn => {
      btn.addEventListener("click", () => {
        if (btn.disabled) return;
        const v = btn.dataset.var;
        if (v === varAtual) return;
        document.querySelectorAll(".atlas-var").forEach(b => {
          b.classList.toggle("atlas-var--active", b === btn);
          b.setAttribute("aria-checked", b === btn ? "true" : "false");
        });
        renderGrid(v);
        if (G.router) {
          const h = `#atlas/${v}`;
          if (root.location.hash !== h) history.replaceState(null, "", h);
        }
      });
    });
  }

  // -------------------- subrota (chamado pelo router) --------------------
  function aplicarSubrota(segmentos) {
    // segmentos: [] | [var] | [var, ano] | [var, 'municipio', code] | ['comparar', ...]
    if (!segmentos || segmentos.length === 0) {
      // mantem variavel atual
      return;
    }
    const v = segmentos[0];
    const variaveisValidas = VARIAVEIS_ATLAS.filter(x => x.prontoMVP).map(x => x.id);
    if (variaveisValidas.includes(v) && v !== varAtual) {
      // simula click no toggle
      const btn = document.querySelector(`.atlas-var[data-var="${v}"]`);
      if (btn && !btn.disabled) btn.click();
    }
    if (segmentos.length >= 2) {
      const sub = segmentos[1];
      if (/^\d{4}$/.test(sub) || /^\d{4}-\d{4}$/.test(sub)) {
        abrirLightbox(varAtual, sub);
      } else {
        // 'municipio' ou 'comparar' — fase 2/3
        console.info("[atlas] subrota pendente:", sub);
      }
    }
  }

  // -------------------- bootstrap --------------------
  function init() {
    bindToolbar();
    renderGrid(varAtual);
    root.GO40 = root.GO40 || {};
    root.GO40.atlas = { aplicarSubrota, renderGrid, abrirLightbox };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(typeof window !== "undefined" ? window : this);
