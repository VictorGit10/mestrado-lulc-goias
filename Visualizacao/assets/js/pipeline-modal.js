/* ============================================================================
 * pipeline-modal.js — abre pipelines (#NN) e scripts (*.py) num modal inline.
 *
 * O leitor da oficina encontra referências como "#32" e "<code>centro_massa.py</code>"
 * que só nomeiam o método. Aqui elas viram clicáveis: o conteúdo real do doc de
 * pipeline (Textos/pipelines/) ou do script (scripts/) é buscado no raw do GitHub,
 * renderizado (markdown via marked.js; Python como bloco de código) e mostrado por
 * cima da página — sem sair do texto. Cada modal traz ainda um link "ver no GitHub"
 * para a fonte renderizada pelo próprio GitHub.
 *
 * Escopo: só liga elementos já presentes no DOM (autoc-refs, <strong>#NN</strong> das
 * tabelas de método, <code>*.py</code>). Ação por delegação de evento (um listener).
 * ========================================================================== */

(function () {
  "use strict";

  // ---- Fontes (repo público VictorGit10/mestrado-lulc-goias, branch master) -------
  const RAW = "https://raw.githubusercontent.com/VictorGit10/mestrado-lulc-goias/master";
  const GH  = "https://github.com/VictorGit10/mestrado-lulc-goias/blob/master";

  // ---- Mapa: token do pipeline -> nome do arquivo em Textos/pipelines/ ------------
  // Construído a partir do inventário real da pasta. Tokens sem arquivo dedicado
  // (ex.: 22B, 14B) apontam ao doc da família mais próxima, já verificado.
  const PIPE_MAP = {
    "10": "10_mapas_gee.md", "11": "11_gif_lulc.md", "12": "12_transicoes.md",
    "13": "13_idhm.md", "14": "14_fogo.md", "14B": "14_fogo.md",
    "15": "15_safrinha.md", "16": "16_painel_unificado.md", "17": "17_taxas_lulc.md",
    "18": "18_mesorregioes.md", "19": "19_conversoes_brutas.md",
    "20": "20_figuras_taxas.md", "21": "21_correlacoes_uf.md",
    "22": "22_correlacoes_painel.md", "22B": "22_correlacoes_painel.md",
    "23": "23_did.md", "24": "24_analise_espacial.md", "25": "25_amc_goias.md",
    "26": "26_deteccao_quebras.md", "27": "27_coleta_trase.md",
    "28": "28_idade_pastagem.md", "28C": "28C_bimodalidade_regional.md",
    "28D": "28D_deriva_mosaico.md", "29": "29_triangulacao_periodizacao.md",
    "32": "32_centro_massa.md", "33": "33_transicoes_regionais.md",
    "34": "34_deslocamento_espacial.md", "35": "35_robustez_janelas.md",
    "36": "36_robustez_janela_slope.md", "37": "37_drive_comum.md",
    "38": "38_drive_comum_amc.md", "39": "39_fronteira_fechando.md",
    "40": "40_duas_logicas_pastagem.md", "40B": "40B_calcario_orientacao.md",
    "41": "41_fogo_fronteira.md", "42": "42_granger_reverso_norte_sul.md",
    "43": "43_centro_massa_pixel.md", "44": "44_centro_massa_desagregado.md",
    "45": "45_trase_lulc.md", "46": "46_fronteira_protecao.md",
    "47": "47_custo_carbono_marcha.md", "48": "48_validacao_prodes.md",
    "49": "49_painel_espacial_dinamico.md", "50": "50_centro_massa_economico.md",
    "51": "51_crescimento_sem_desenvolvimento.md", "52": "52_aptidao_edafoclimatica.md",
    "53": "53_centro_massa_capacidade.md", "54": "54_defensabilidade_perna4.md"
  };

  // Regex de um token de pipeline: #NN ou #NNB (ex.: #32, #28D, #40B).
  const RE_PIPE = /#(\d+[A-Z]?)/g;
  // Um nome de script isolado em <code>: começa com letra/_, termina em .py.
  const RE_SCRIPT = /^[A-Za-z_][A-Za-z0-9_]*\.py$/;

  const cache = Object.create(null);

  // ---- Montagem do modal (uma vez) ------------------------------------------------
  function montarModal() {
    if (document.getElementById("pl-modal")) return;
    const el = document.createElement("div");
    el.id = "pl-modal";
    el.className = "pl-modal";
    el.hidden = true;
    el.innerHTML = `
      <div class="pl-modal__overlay" data-pl-close></div>
      <div class="pl-modal__panel" role="dialog" aria-modal="true" aria-labelledby="pl-modal-titulo">
        <header class="pl-modal__cabecalho">
          <span id="pl-modal-titulo" class="pl-modal__titulo"></span>
          <a class="pl-modal__github" target="_blank" rel="noopener">ver no GitHub &#8599;</a>
          <button class="pl-modal__fechar" type="button" data-pl-close aria-label="Fechar">&times;</button>
        </header>
        <div class="pl-modal__corpo" id="pl-modal-corpo"></div>
      </div>`;
    document.body.appendChild(el);
  }

  function fechar() {
    const m = document.getElementById("pl-modal");
    if (!m || m.hidden) return;
    m.hidden = true;
    document.body.classList.remove("pl-lock");
    if (ultimoFoco) { try { ultimoFoco.focus(); } catch (e) {} }
    ultimoFoco = null;
  }

  let ultimoFoco = null;

  async function abrir(tipo, chave) {
    montarModal();
    const m = document.getElementById("pl-modal");
    const corpo = document.getElementById("pl-modal-corpo");
    const titulo = document.getElementById("pl-modal-titulo");
    const ghLink = m.querySelector(".pl-modal__github");

    const arquivo = (tipo === "pipe") ? PIPE_MAP[chave] : chave;
    const caminho  = (tipo === "pipe") ? "Textos/pipelines/" + arquivo : "scripts/" + arquivo;
    const url = RAW + "/" + caminho;
    ghLink.href = GH + "/" + caminho;

    titulo.textContent = (tipo === "pipe") ? ("Pipeline #" + chave) : arquivo;
    corpo.innerHTML = '<p class="pl-modal__carregando">Carregando…</p>';
    ultimoFoco = document.activeElement;
    m.hidden = false;
    document.body.classList.add("pl-lock");
    m.querySelector(".pl-modal__fechar").focus();

    try {
      let txt = cache[url];
      if (txt === undefined) {
        const r = await fetch(url);
        if (!r.ok) throw new Error("HTTP " + r.status);
        txt = await r.text();
        cache[url] = txt;
      }
      if (tipo === "script") {
        const pre = document.createElement("pre");
        pre.className = "pl-src";
        const code = document.createElement("code");
        code.textContent = txt;
        pre.appendChild(code);
        corpo.innerHTML = "";
        corpo.appendChild(pre);
      } else {
        corpo.innerHTML = window.marked ? window.marked.parse(txt) : "<pre>" + escHtml(txt) + "</pre>";
      }
    } catch (err) {
      corpo.innerHTML =
        '<p class="pl-modal__erro">Não foi possível buscar o arquivo (' +
        escHtml(String(err.message)) + ').</p>' +
        '<p><a class="pl-modal__github" href="' + escHtml(ghLink.href) +
        '" target="_blank" rel="noopener">Abrir no GitHub &#8599;</a></p>';
    }
  }

  function escHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }

  // ---- Ligação dos alvos no DOM ----------------------------------------------------
  function ligar() {
    // (1) autoc-refs inline: envolver cada #NN num <a data-pipe> (só se houver mapa).
    // O href aponta ao blob do GitHub (doc renderado) — funciona sem JS e não vira
    // âncora interna falsa; com JS, o clique é interceptado e abre o modal.
    document.querySelectorAll("em.autoc-ref").forEach((em) => {
      em.innerHTML = em.innerHTML.replace(RE_PIPE, (todo, token) => {
        if (!PIPE_MAP[token]) return todo;
        const href = GH + "/Textos/pipelines/" + PIPE_MAP[token];
        return '<a class="pl-link" href="' + href + '" target="_blank" rel="noopener" data-pipe="' + token + '">' + todo + "</a>";
      });
    });

    // (2) coluna "Pipeline" das tabelas de método: <strong>#NN</strong> clicável.
    document.querySelectorAll(".camadas-tabela strong").forEach((st) => {
      const t = st.textContent.trim();
      const m = t.match(/^#(\d+[A-Z]?)$/);
      if (m && PIPE_MAP[m[1]]) {
        st.classList.add("pl-link");
        st.dataset.pipe = m[1];
        st.setAttribute("role", "link");
        st.tabIndex = 0;
        st.title = "Abrir o pipeline #" + m[1];
      }
    });

    // (3) <code> com nome de script: clicável, mantém o estilo <code>.
    document.querySelectorAll("code").forEach((c) => {
      const t = c.textContent.trim();
      if (RE_SCRIPT.test(t)) {
        c.classList.add("pl-link", "pl-link--script");
        c.dataset.script = t;
        c.setAttribute("role", "link");
        c.tabIndex = 0;
        c.title = "Abrir o script " + t;
      }
    });

    // Delegação: um único listener trata cliques e teclado.
    document.addEventListener("click", (e) => {
      const alvo = e.target.closest("[data-pipe],[data-script]");
      if (alvo) {
        e.preventDefault();
        if (alvo.dataset.pipe) abrir("pipe", alvo.dataset.pipe);
        else if (alvo.dataset.script) abrir("script", alvo.dataset.script);
      } else if (e.target.closest("[data-pl-close]")) {
        fechar();
      }
    });

    document.addEventListener("keydown", (e) => {
      const m = document.getElementById("pl-modal");
      if (!m || m.hidden) return;
      if (e.key === "Escape") { e.preventDefault(); fechar(); }
      if ((e.key === "Enter" || e.key === " ") && e.target.closest && e.target.closest("[data-pipe],[data-script]")) {
        e.preventDefault();
        const alvo = e.target.closest("[data-pipe],[data-script]");
        if (alvo.dataset.pipe) abrir("pipe", alvo.dataset.pipe);
        else if (alvo.dataset.script) abrir("script", alvo.dataset.script);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ligar);
  } else {
    ligar();
  }
})();