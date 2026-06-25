/* secoes.js — navegacao pos-mapas e aba Metodos.
 *
 * (a) Regua viva: enquanto o leitor esta na regiao "Depois dos mapas" da
 *     Narrativa, a regua superior troca a linha de anos pelos blocos do
 *     argumento (atos ← | saldo | processos | marcha | tese), com o bloco
 *     ativo destacado e clique-para-saltar.
 * (b) Subrota #metodos/<id>: ao trocar para a aba Metodos com uma ancora
 *     (ex.: #metodos/metodo-evidencia), rola ate o bloco correspondente.
 */
(function (root) {
  "use strict";

  // Compensa regua + tabs sticky + respiro ao rolar para uma ancora.
  const OFFSET_STICKY = 150;

  // Respeita prefers-reduced-motion: rolagem instantanea em vez de suave.
  function comportamentoScroll() {
    return root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto" : "smooth";
  }

  // -------------------- aba Metodos: subrota de ancoras --------------------
  function aplicarSubrotaMetodos(segmentos) {
    if (!segmentos || segmentos.length === 0) {
      root.scrollTo({ top: 0, behavior: comportamentoScroll() });
      return;
    }
    const alvo = document.getElementById(segmentos[0]);
    if (!alvo) return;
    // O painel acabou de ficar visivel; espera 1 frame para o layout assentar.
    requestAnimationFrame(() => {
      const topo = alvo.getBoundingClientRect().top + root.pageYOffset;
      root.scrollTo({ top: Math.max(0, topo - OFFSET_STICKY), behavior: comportamentoScroll() });
    });
  }

  // -------------------- regua viva pos-mapas --------------------
  // Cada secao aponta para um marcador no DOM da Narrativa. O flex controla
  // a largura relativa do segmento na regua.
  const SECOES = [
    { id: "panel-narrativa", rotulo: "Os três atos · 1985–2024 · role para voltar aos mapas",
      curto: "↑ Atos", flex: 0.7, isVoltar: true },
    { id: "mov-saldo", rotulo: "Movimento I · O saldo e os fluxos de 40 anos",
      curto: "Saldo e fluxos", flex: 1.0 },
    { id: "mov-processos", rotulo: "Movimento II · O que os dados revelam — no agregado",
      curto: "Processos", flex: 1.3 },
    { id: "mov-marcha", rotulo: "Movimento III · A marcha ao norte — a tese central",
      curto: "Marcha ao norte", flex: 1.7 },
    { id: "sec-tese", rotulo: "A afirmação central — e a aba Métodos",
      curto: "A tese", flex: 0.8 },
  ];

  let marcadores = [];   // [{ el, secao }] — somente secoes navegaveis (nao isVoltar)
  let botoes = {};       // secao.id -> button
  let modoAtivo = false;
  let aguardandoFrame = false;

  function construir() {
    const cont = document.getElementById("rail-secoes");
    if (!cont) return false;
    cont.innerHTML = "";
    SECOES.forEach(sec => {
      const el = document.getElementById(sec.id);
      if (!el) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "rail-secao" + (sec.isVoltar ? " rail-secao--voltar" : "");
      btn.style.flexGrow = String(sec.flex);
      btn.textContent = sec.curto;
      btn.title = sec.rotulo;
      btn.setAttribute("aria-label", sec.rotulo);
      btn.addEventListener("click", () => {
        if (sec.isVoltar) {
          root.scrollTo({ top: 0, behavior: comportamentoScroll() });
          return;
        }
        const topo = el.getBoundingClientRect().top + root.pageYOffset;
        root.scrollTo({ top: Math.max(0, topo - OFFSET_STICKY), behavior: comportamentoScroll() });
      });
      cont.appendChild(btn);
      botoes[sec.id] = btn;
      if (!sec.isVoltar) marcadores.push({ el, secao: sec });
    });
    return marcadores.length > 0;
  }

  function definirModo(ligado) {
    if (ligado === modoAtivo) return;
    modoAtivo = ligado;
    document.body.classList.toggle("is-pos-mapas", ligado);
    const alternar = (id, esconder) => {
      const el = document.getElementById(id);
      if (el) el.hidden = esconder;
    };
    alternar("rail-secoes", !ligado);
    alternar("rail-context-secoes", !ligado);
    alternar("rail-hint-secoes", !ligado);
    alternar("rail-context-anos", ligado);
    alternar("rail-hint-anos", ligado);
  }

  function avaliar() {
    aguardandoFrame = false;
    // So vale na aba Narrativa.
    const modo = document.body.dataset.modoAtivo || "narrativa";
    if (modo !== "narrativa") { definirModo(false); return; }

    const inicio = document.getElementById("depois-dos-mapas");
    if (!inicio) return;
    const linha = root.innerHeight * 0.5;
    const rect = inicio.getBoundingClientRect();
    const dentro = rect.top < linha && rect.bottom > 0;
    definirModo(dentro);
    if (!dentro) return;

    // Bloco ativo = ultimo marcador cujo topo ja passou da linha de leitura.
    let ativo = marcadores[0];
    marcadores.forEach(m => {
      if (m.el.getBoundingClientRect().top <= linha) ativo = m;
    });
    marcadores.forEach(m => {
      botoes[m.secao.id].classList.toggle("is-active", m === ativo);
    });
    const label = document.getElementById("rail-secao-label");
    if (label && ativo) label.textContent = ativo.secao.rotulo;
  }

  function agendarAvaliacao() {
    if (aguardandoFrame) return;
    aguardandoFrame = true;
    root.requestAnimationFrame(avaliar);
  }

  // Registrado no parse (antes do DOMContentLoaded): o router aplica a rota
  // inicial no seu proprio init e precisa encontrar o handler ja publicado.
  root.GO40 = root.GO40 || {};
  root.GO40.metodos = { aplicarSubrota: aplicarSubrotaMetodos };

  function init() {
    if (!construir()) return;
    root.addEventListener("scroll", agendarAvaliacao, { passive: true });
    root.addEventListener("resize", agendarAvaliacao);
    root.addEventListener("hashchange", agendarAvaliacao);
    agendarAvaliacao();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
