/* ==========================================================================
   Apresentação da qualificação — motor: o site navegado pelas setas.

   Os slides são uma página longa, um abaixo do outro; avançar rola o palco
   para o slide seguinte, como rolar o index.html. O sumário lateral (o rail
   do site) acompanha a seção; some nos slides "cheios" (título, abertura,
   pergunta, fecho), como some no hero do site.

   Cada <section class="slide"> tem passos. Um elemento com data-step="n"
   aparece a partir do passo n; com data-ate="n", some depois do passo n.
   Um slide com data-hook chama HOOKS[nome].passo(slide, passo, anterior).

   Atributos do slide
     data-secao     problema | metodo | investigacao | veredito | defesa
     data-perna     1–4 (subitem da investigação)
     data-realca    passo a partir do qual as 4 perguntas do sumário acendem
     data-fundo     terracota | escuro (cor da tarja fora do 16:9)
     class="cheia"  sem sumário, largura inteira

   Teclas
     → ↓ PageDown Espaço Enter   avança um passo
     ← ↑ PageUp Backspace         volta um passo
     Shift + ←/→                  pula o slide inteiro
     Home / End                   primeiro / último slide principal
     número + Enter               vai ao slide n
     O ou Esc                     índice (↑↓ e Enter escolhem)
     B ou .                       tela preta
     F                            tela cheia
     no slide-hub (reserva)       letra do cartão abre a página dentro da apresentação;
                                  dentro dela: Esc volta, + e − mudam o tamanho
   ========================================================================== */
(() => {
  "use strict";
  const W = 1920, H = 1080;
  const stage = document.querySelector(".stage");
  const pagina = stage.querySelector(".pagina");
  const slides = [...pagina.querySelectorAll(".slide")];
  const nPrincipais = slides.filter(s => !s.classList.contains("reserva")).length;
  const HOOKS = window.HOOKS || {};
  if (/estatico/.test(location.search)) document.body.classList.add("estatico");

  slides.forEach((s, k) => { s.style.top = `${k * H}px`; });

  // --- escala do palco -------------------------------------------------------
  function ajustar() {
    const s = Math.min(innerWidth / W, innerHeight / H);
    stage.style.transform = `translate(-50%, -50%) scale(${s})`;
  }
  addEventListener("resize", ajustar);
  ajustar();

  function passosDe(slide) {
    let m = +slide.dataset.passos || 0;
    slide.querySelectorAll("[data-step]").forEach(e => { m = Math.max(m, +e.dataset.step); });
    slide.querySelectorAll("[data-ate]").forEach(e => { m = Math.max(m, +e.dataset.ate + 1); });
    return m;
  }

  // --- sumário lateral (o rail do site) -------------------------------------
  const SECOES = [
    { id: "problema", n: "1", nome: "O problema" },
    { id: "metodo", n: "2", nome: "Dados e método" },
    { id: "investigacao", n: "3", nome: "A investigação",
      sub: ["O padrão existe?", "Qual é o mecanismo?", "O Sul empurrou o Norte?", "Por que desacelerou?"] },
    { id: "veredito", n: "4", nome: "O veredito" },
    { id: "defesa", n: "5", nome: "Até a defesa" },
    { id: "reserva", n: "R", nome: "Reserva" },
  ];
  const sumario = document.createElement("nav");
  sumario.className = "sumario";
  sumario.setAttribute("aria-label", "Sumário da apresentação");
  sumario.innerHTML = `<p class="marca">Qualificação<b>A marcha ao norte</b></p><ol>${
    SECOES.map(s => `<li class="item${s.id === "reserva" ? " reserva" : ""}" data-secao="${s.id}">
      <span><span class="n">${s.n}</span>${s.nome}</span>
      ${s.sub ? `<ol class="sub">${s.sub.map((t, k) => `<li data-perna="${k + 1}">${t}</li>`).join("")}</ol>` : ""}
    </li>`).join("")
  }</ol><div class="pe"><div class="contagem"></div><div class="barra-prog"><i></i></div></div>`;
  const pagNum = document.createElement("div");
  pagNum.className = "pagina-num";
  stage.append(sumario, pagNum);
  const itens = [...sumario.querySelectorAll(".item")];
  const subs = [...sumario.querySelectorAll(".sub li")];
  const ordemSecao = id => SECOES.findIndex(s => s.id === id);

  function atualizarSumario(slide, p) {
    const cheia = slide.classList.contains("cheia");
    const reserva = slide.classList.contains("reserva");
    sumario.classList.toggle("visivel", !cheia);
    sumario.classList.toggle("em-reserva", reserva);
    const secao = reserva ? "reserva" : slide.dataset.secao;
    const iSec = ordemSecao(secao);
    const perna = +slide.dataset.perna || 0;
    itens.forEach(li => li.classList.toggle("agora", li.dataset.secao === secao));
    const iInv = ordemSecao("investigacao");
    subs.forEach(li => {
      const k = +li.dataset.perna;
      li.classList.toggle("agora", k === perna);
      li.classList.toggle("feito", (perna && k < perna) || (!reserva && iSec > iInv));
    });
    const realca = slide.dataset.realca;
    sumario.classList.toggle("realce", realca !== undefined && p >= +realca);
    const i = slides.indexOf(slide);
    sumario.querySelector(".contagem").textContent = reserva ? `Reserva ${i - nPrincipais + 1}` : `${i + 1} / ${nPrincipais}`;
    sumario.querySelector(".barra-prog i").style.width = reserva ? "100%" : `${((i + 1) / nPrincipais) * 100}%`;
    pagNum.textContent = i > 0 ? (reserva ? `R${i - nPrincipais + 1}` : `${i + 1} / ${nPrincipais}`) : "";
  }

  // --- navegação -------------------------------------------------------------
  let atual = -1, passo = 0;

  function aplicarPassos(slide, p) {
    slide.querySelectorAll("[data-step]").forEach(e => e.classList.toggle("on", p >= +e.dataset.step));
    slide.querySelectorAll("[data-ate]").forEach(e => e.classList.toggle("fora", p > +e.dataset.ate));
  }

  function ir(i, p, instantaneo) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    const slide = slides[i];
    p = Math.max(0, Math.min(passosDe(slide), p));
    const anteriorSlide = atual, anteriorPasso = passo;
    if (i !== atual) {
      // vizinho: rola como o site; longe (índice, número): salta
      const salto = instantaneo || atual < 0 || Math.abs(i - atual) > 1;
      pagina.classList.toggle("salto", salto);
      pagina.style.transform = `translateY(${-i * H}px)`;
      if (salto) requestAnimationFrame(() => requestAnimationFrame(() => pagina.classList.remove("salto")));
      slides.forEach((s, k) => s.classList.toggle("ativo", k === i));
      document.body.classList.toggle("fundo-terracota", slide.dataset.fundo === "terracota");
      document.body.classList.toggle("fundo-escuro", slide.dataset.fundo === "escuro");
    }
    atual = i; passo = p;
    aplicarPassos(slide, p);
    const h = HOOKS[slide.dataset.hook];
    if (h && h.passo) {
      const mesmo = anteriorSlide === i;
      // um gráfico que falhe não pode travar a navegação
      try { h.passo(slide, p, mesmo ? anteriorPasso : null, instantaneo || !mesmo || Math.abs(p - anteriorPasso) !== 1); }
      catch (e) { console.error(slide.dataset.hook, e); }
    }
    atualizarSumario(slide, p);
    history.replaceState(null, "", `${location.search}#${i + 1}.${p}`);
  }

  function avancar() {
    if (passo < passosDe(slides[atual])) ir(atual, passo + 1);
    else if (atual < slides.length - 1) ir(atual + 1, 0);
  }
  function voltar() {
    if (passo > 0) ir(atual, passo - 1);
    else if (atual > 0) ir(atual - 1, passosDe(slides[atual - 1]));
  }

  // --- índice ---------------------------------------------------------------
  const indice = document.createElement("div");
  indice.className = "indice";
  const lista = document.createElement("ol");
  slides.forEach((s, k) => {
    const li = document.createElement("li");
    const res = s.classList.contains("reserva");
    li.innerHTML = `<span class="n">${res ? "R" + (k - nPrincipais + 1) : k + 1}</span>${s.dataset.titulo || "—"}`;
    if (res) li.classList.add("res");
    li.addEventListener("click", () => { fecharIndice(); ir(k, 0); });
    lista.appendChild(li);
  });
  indice.innerHTML = `<h2>Índice · principal (${nPrincipais}) e reserva (${slides.length - nPrincipais})</h2>`;
  indice.appendChild(lista);
  indice.insertAdjacentHTML("beforeend", `<div class="ajuda">
    <kbd>→</kbd> <kbd>Espaço</kbd> <kbd>PageDown</kbd> avança &nbsp;·&nbsp; <kbd>←</kbd> <kbd>PageUp</kbd> volta &nbsp;·&nbsp;
    <kbd>Shift</kbd>+<kbd>→</kbd> pula o slide &nbsp;·&nbsp; número + <kbd>Enter</kbd> vai ao slide &nbsp;·&nbsp;
    <kbd>O</kbd> índice &nbsp;·&nbsp; <kbd>B</kbd> tela preta &nbsp;·&nbsp; <kbd>F</kbd> tela cheia</div>`);
  const preto = document.createElement("div"); preto.className = "preto";
  const buffer = document.createElement("div"); buffer.className = "buffer";
  document.body.append(indice, preto, buffer);
  let sel = 0;
  function marcarSel() { [...lista.children].forEach((li, k) => li.classList.toggle("sel", k === sel)); lista.children[sel].scrollIntoView({ block: "nearest" }); }
  function abrirIndice() { sel = atual; indice.classList.add("on"); document.body.classList.add("cursor"); marcarSel(); }
  function fecharIndice() { indice.classList.remove("on"); document.body.classList.remove("cursor"); }

  // --- janela: o site aberto dentro da apresentação (slide de reserva) -------
  // Fica fora do palco escalado e ocupa a tela toda; o iframe é ampliado por
  // `zoom` para a TV. Mesma origem (o site está na mesma pasta), então o
  // teclado de dentro da página também fecha a janela com Esc.
  const janela = document.createElement("div");
  janela.className = "janela";
  janela.innerHTML = `<div class="janela-barra"><b></b><span class="janela-url"></span>
    <span class="janela-ajuda">Esc volta à apresentação · + − tamanho</span><button type="button">Voltar</button></div>
    <div class="janela-corpo"><iframe title="Página do trabalho"></iframe></div>`;
  document.body.appendChild(janela);
  const quadro = janela.querySelector("iframe");
  let zoom = 1.35;
  function aplicarZoom() {
    quadro.style.transform = `scale(${zoom})`;
    quadro.style.width = `${100 / zoom}%`;
    quadro.style.height = `${100 / zoom}%`;
  }
  function teclaJanela(e) {
    if (e.key === "Escape") { fecharJanela(); e.preventDefault(); }
    else if (e.key === "+" || e.key === "=") { zoom = Math.min(2.2, zoom + 0.1); aplicarZoom(); e.preventDefault(); }
    else if (e.key === "-") { zoom = Math.max(0.8, zoom - 0.1); aplicarZoom(); e.preventDefault(); }
  }
  quadro.addEventListener("load", () => {
    try {
      const w = quadro.contentWindow;
      w.addEventListener("keydown", teclaJanela);
      w.focus();
      // o site monta mapas e gráficos depois do load e a página cresce: a
      // âncora do link se perde. Rola até ela de novo quando o layout assenta.
      const id = decodeURIComponent(w.location.hash.slice(1));
      if (id) [300, 1200, 2500].forEach(ms => setTimeout(() => {
        const alvo = w.document.getElementById(id);
        if (alvo && janela.classList.contains("on")) w.scrollTo({ top: alvo.getBoundingClientRect().top + w.scrollY - 24, behavior: "instant" });
      }, ms));
    } catch (_) { /* outra origem */ }
  });
  function abrirJanela(a) {
    janela.querySelector("b").textContent = a.querySelector("b").textContent;
    janela.querySelector(".janela-url").textContent = a.getAttribute("href");
    aplicarZoom();
    quadro.src = a.getAttribute("href");
    janela.classList.add("on");
    document.body.classList.add("cursor");
  }
  function fecharJanela() {
    janela.classList.remove("on");
    quadro.src = "about:blank";
    window.focus();
  }
  janela.querySelector("button").addEventListener("click", fecharJanela);
  document.querySelectorAll(".hub").forEach(a => a.addEventListener("click", e => { e.preventDefault(); abrirJanela(a); }));

  // --- teclado --------------------------------------------------------------
  let digitos = "", tDig;
  addEventListener("keydown", e => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const k = e.key;
    if (janela.classList.contains("on")) { teclaJanela(e); return; }
    if (preto.classList.contains("on")) { preto.classList.remove("on"); e.preventDefault(); return; }
    // no slide-hub: a letra do cartão abre a página; Enter abre o cartão em foco (Tab navega)
    if (slides[atual] && slides[atual].classList.contains("s-hub")) {
      const alvo = k.length === 1 && slides[atual].querySelector(`.hub[data-tecla="${CSS.escape(k.toUpperCase())}"]`);
      if (alvo) { abrirJanela(alvo); e.preventDefault(); return; }
      if (k === "Enter" && document.activeElement && document.activeElement.classList.contains("hub")) {
        abrirJanela(document.activeElement); e.preventDefault(); return;
      }
    }
    if (indice.classList.contains("on")) {
      if (k === "ArrowDown" || k === "ArrowRight") sel = Math.min(slides.length - 1, sel + 1);
      else if (k === "ArrowUp" || k === "ArrowLeft") sel = Math.max(0, sel - 1);
      else if (k === "Enter") { fecharIndice(); ir(sel, 0); }
      else if (k === "Escape" || k === "o" || k === "O") fecharIndice();
      marcarSel(); e.preventDefault(); return;
    }
    if (/^[0-9]$/.test(k)) {
      digitos += k; buffer.textContent = "→ " + digitos; buffer.classList.add("on");
      clearTimeout(tDig); tDig = setTimeout(() => { digitos = ""; buffer.classList.remove("on"); }, 2500);
      return;
    }
    if (k === "Enter" && digitos) {
      ir(+digitos - 1, 0); digitos = ""; buffer.classList.remove("on"); e.preventDefault(); return;
    }
    switch (k) {
      case "ArrowRight": case "ArrowDown": case "PageDown": case " ": case "Enter":
        if (e.shiftKey && (k === "ArrowRight" || k === "ArrowDown")) ir(atual + 1, 0); else avancar();
        break;
      case "ArrowLeft": case "ArrowUp": case "PageUp": case "Backspace":
        if (e.shiftKey && (k === "ArrowLeft" || k === "ArrowUp")) ir(atual - 1, 0); else voltar();
        break;
      case "Home": ir(0, 0); break;
      case "End": ir(nPrincipais - 1, 0); break;
      case "o": case "O": case "Escape": abrirIndice(); break;
      case "b": case "B": case ".": preto.classList.add("on"); break;
      case "f": case "F":
        if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen().catch(() => {});
        break;
      default: return;
    }
    e.preventDefault();
  });
  // a roda do mouse e o trackpad não rolam o palco por engano
  addEventListener("wheel", e => e.preventDefault(), { passive: false });
  // o cursor some sozinho; reaparece quando o mouse se mexe
  let tCur;
  addEventListener("mousemove", () => { document.body.classList.add("cursor"); clearTimeout(tCur); tCur = setTimeout(() => { if (!indice.classList.contains("on")) document.body.classList.remove("cursor"); }, 1800); });

  // --- início ---------------------------------------------------------------
  Promise.all(Object.values(HOOKS).map(h => h.init ? Promise.resolve().then(() => h.init()).catch(e => console.error(e)) : null)).finally(() => {
    const m = location.hash.match(/^#(\d+)(?:\.(\d+))?/);
    ir(m ? +m[1] - 1 : 0, m && m[2] ? +m[2] : 0, true);
  });
  addEventListener("hashchange", () => {
    const m = location.hash.match(/^#(\d+)(?:\.(\d+))?/);
    if (m) ir(+m[1] - 1, m[2] ? +m[2] : 0, true);
  });
})();
