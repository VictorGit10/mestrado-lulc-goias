/* rail.js — navegacao do scroll unico da peca reformulada.
 *
 * Substitui o par router.js + secoes.js, que existia para o site em abas.
 * Tres responsabilidades:
 *
 *  (a) Rail lateral: marca a parte (e a perna) em que o leitor esta, e salta
 *      ao clique. Some no hero, aparece a partir da Parte 1.
 *  (b) Regua dos 40 anos: e' peca da Parte 1. Recolhe quando o leitor sai dos
 *      mapas, para nao competir com o rail lateral no resto do scroll.
 *  (c) Deep-link por hash (#p2-perna3) com offset das barras fixas.
 *
 * A logica de "secao ativa por scroll" e' a mesma de secoes.js (rAF + linha de
 * leitura); o que muda e' o alvo — rail lateral em vez da faixa horizontal.
 */
(function (root) {
  "use strict";

  const doc = root.document;

  // Respiro ao saltar para uma ancora (regua sticky + folga editorial).
  const OFFSET_ANCORA = 110;

  // Linha de leitura, em pixels do topo da viewport. Precisa ficar LOGO ABAIXO
  // do OFFSET_ANCORA: uma secao curta levada ate a ancora tem que conter a
  // linha, senao ela nunca fica ativa e o rail acende a seguinte. Com uma
  // linha proporcional (ex. 35% da altura) as pernas curtas acendiam a vizinha.
  const LINHA_LEITURA = OFFSET_ANCORA + 40;

  // Ordem do scroll. `pai` aninha a perna sob a Parte 2 no rail.
  const SECOES = [
    { id: "parte-1" },
    { id: "parte-2" },
    { id: "p2-perna1", pai: "parte-2" },
    { id: "p2-perna2", pai: "parte-2" },
    { id: "p2-perna3", pai: "parte-2" },
    { id: "p2-perna4", pai: "parte-2" },
    { id: "parte-3" },
    { id: "parte-4" },
  ];

  let alvos = [];            // [{ id, el, pai }] — so' os que existem no DOM
  let itens = {};            // id -> elemento <li> do rail
  let aguardandoFrame = false;
  let ativoAtual = null;

  function comportamentoScroll() {
    return root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto" : "smooth";
  }

  // Executa `cb` uma unica vez, quando a rolagem parar (ou depois do teto).
  function aoAssentar(cb) {
    let debounce = null;
    let feito = false;
    function finalizar() {
      if (feito) return;
      feito = true;
      root.removeEventListener("scroll", agendar);
      if (debounce) root.clearTimeout(debounce);
      root.clearTimeout(teto);
      cb();
    }
    function agendar() {
      if (debounce) root.clearTimeout(debounce);
      debounce = root.setTimeout(finalizar, 140);
    }
    const teto = root.setTimeout(finalizar, 4000);
    root.addEventListener("scroll", agendar, { passive: true });
    agendar();
  }

  /* Salto para uma ancora, com correcao depois que a pagina assenta.
   *
   * Por que a correcao existe: varias pecas da Parte 1 renderizam de forma
   * preguicosa (o Sankey, os mini-Sankeys por ato). Num salto longo — do topo
   * ate a Parte 3 sao ~30 mil px — elas entram na viewport durante a animacao,
   * crescem, e empurram o alvo para baixo. Medido: o clique em "O veredito"
   * parava 405 px acima do lugar certo. Reposiciona-se ate duas vezes; se
   * ainda desviar, o leitor esta perto o bastante e insistir viraria tremor. */
  function rolarAte(el, tentativas) {
    const restantes = typeof tentativas === "number" ? tentativas : 2;
    const topo = el.getBoundingClientRect().top + root.pageYOffset;
    root.scrollTo({ top: Math.max(0, topo - OFFSET_ANCORA), behavior: comportamentoScroll() });
    if (restantes <= 0) return;
    aoAssentar(() => {
      const desvio = el.getBoundingClientRect().top - OFFSET_ANCORA;
      if (Math.abs(desvio) > 6) rolarAte(el, restantes - 1);
    });
  }

  // -------------------- construcao --------------------
  function construir() {
    const nav = doc.getElementById("rail-lateral");
    if (!nav) return false;

    SECOES.forEach(sec => {
      const el = doc.getElementById(sec.id);
      if (!el) return;
      alvos.push({ id: sec.id, el: el, pai: sec.pai || null });
      const item = nav.querySelector('[data-alvo="' + sec.id + '"]');
      if (item) itens[sec.id] = item;
    });

    // Clique nos links do rail: rolagem controlada (nao o salto bruto do
    // browser, que ignora a regua fixa) + hash atualizado sem novo history
    // entry a cada clique de navegacao interna.
    nav.querySelectorAll("a[href^='#']").forEach(link => {
      link.addEventListener("click", ev => {
        const id = link.getAttribute("href").slice(1);
        const el = doc.getElementById(id);
        if (!el) return;
        ev.preventDefault();
        rolarAte(el);
        if (root.history && root.history.replaceState) {
          root.history.replaceState(null, "", "#" + id);
        }
        fecharSeCompacto();
      });
    });

    return alvos.length > 0;
  }

  // -------------------- estado ativo --------------------
  function marcarAtivo(id) {
    if (id === ativoAtual) return;
    ativoAtual = id;
    Object.keys(itens).forEach(k => {
      itens[k].classList.remove("is-active", "is-ancestral");
    });
    if (!id || !itens[id]) return;
    itens[id].classList.add("is-active");
    // Uma perna ativa tambem acende a Parte 2 (o pai), sem roubar o destaque.
    const alvo = alvos.find(a => a.id === id);
    if (alvo && alvo.pai && itens[alvo.pai]) {
      itens[alvo.pai].classList.add("is-ancestral");
    }
  }

  // -------------------- visibilidade das duas barras --------------------
  function atualizarVisibilidade() {
    const hero = doc.getElementById("p0-hero");
    const nav = doc.getElementById("rail-lateral");
    const regua = doc.getElementById("regua-anos");

    // Rail lateral: aparece quando o hero sai de cena.
    if (nav && hero) {
      const heroFora = hero.getBoundingClientRect().bottom < root.innerHeight * 0.4;
      nav.classList.toggle("is-visivel", heroFora);
    }

    // Regua dos 40 anos: e' peca da Parte 1. Fica enquanto os mapas estao em
    // cena (com folga para o bloco "como ler", logo acima).
    if (regua) {
      const mapas = doc.getElementById("p1-mapas");
      const comoLer = doc.querySelector("#parte-1 .como-ler");
      const inicio = comoLer || mapas;
      let dentro = false;
      if (inicio && mapas) {
        const topo = inicio.getBoundingClientRect().top;
        const fim = mapas.getBoundingClientRect().bottom;
        dentro = topo < root.innerHeight * 0.6 && fim > 0;
      }
      regua.classList.toggle("is-recolhida", !dentro);
      doc.body.classList.toggle("regua-visivel", dentro);
    }
  }

  // -------------------- laco de scroll --------------------
  function avaliar() {
    aguardandoFrame = false;
    atualizarVisibilidade();
    if (alvos.length === 0) return;

    const linha = LINHA_LEITURA;

    // Antes da Parte 1 (ainda no hero) nada fica ativo.
    if (alvos[0].el.getBoundingClientRect().top > linha) {
      marcarAtivo(null);
      return;
    }

    // Ativa e' a secao que CONTEM a linha de leitura, nao a ultima que passou
    // por ela. A diferenca importa: blocos curtos e vizinhos (as pernas) fazem
    // o topo do proximo cruzar a linha enquanto o leitor ainda esta no atual —
    // pela regra ingenua, clicar na Perna 3 acendia a Perna 4.
    // A ordem do array resolve o aninhamento: a perna vem depois da Parte 2,
    // entao ganha dela quando as duas contem a linha.
    let ativo = null;
    alvos.forEach(a => {
      const r = a.el.getBoundingClientRect();
      if (r.top <= linha && r.bottom > linha) ativo = a;
    });

    // Fallback para vaos entre secoes (margens, fim da pagina).
    if (!ativo) {
      alvos.forEach(a => {
        if (a.el.getBoundingClientRect().top <= linha) ativo = a;
      });
    }

    marcarAtivo(ativo ? ativo.id : null);
  }

  function agendar() {
    if (aguardandoFrame) return;
    aguardandoFrame = true;
    root.requestAnimationFrame(avaliar);
  }

  // -------------------- modo compacto (mobile) --------------------
  function estaCompacto() {
    return root.matchMedia && root.matchMedia("(max-width: 1180px)").matches;
  }

  function fecharSeCompacto() {
    if (!estaCompacto()) return;
    const nav = doc.getElementById("rail-lateral");
    const btn = doc.getElementById("rail-lateral-toggle");
    if (!nav || !btn) return;
    nav.classList.remove("is-aberto");
    btn.setAttribute("aria-expanded", "false");
  }

  function configurarToggle() {
    const nav = doc.getElementById("rail-lateral");
    const btn = doc.getElementById("rail-lateral-toggle");
    if (!nav || !btn) return;
    btn.addEventListener("click", () => {
      const aberto = nav.classList.toggle("is-aberto");
      btn.setAttribute("aria-expanded", aberto ? "true" : "false");
    });
    doc.addEventListener("keydown", ev => {
      if (ev.key === "Escape") fecharSeCompacto();
    });
  }

  // -------------------- deep-link na carga --------------------
  function aplicarHashInicial() {
    const id = (root.location.hash || "").replace(/^#/, "");
    if (!id) return;
    const el = doc.getElementById(id);
    if (!el) return;
    // Espera o layout assentar (a regua e os steps do timeline entram depois).
    root.setTimeout(() => rolarAte(el), 120);
  }

  // -------------------- bootstrap --------------------
  function init() {
    if (!construir()) return;
    configurarToggle();
    root.addEventListener("scroll", agendar, { passive: true });
    root.addEventListener("resize", agendar);
    avaliar();
    aplicarHashInicial();
  }

  root.GO40 = root.GO40 || {};
  root.GO40.rail = { rolarAte: rolarAte };

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
