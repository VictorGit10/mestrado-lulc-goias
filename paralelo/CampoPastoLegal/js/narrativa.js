/* narrativa.js — Gerenciador central do storytelling: scroll-sync e transições */
(function () {
  'use strict';

  // ===================== Scroll Progress Bar =====================
  const progressBar = document.getElementById('journey-progress-bar');
  function updateProgress() {
    if (!progressBar) return;
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = progress + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });

  // ===================== Transição Poética Visibility =====================
  const transitionSections = document.querySelectorAll('.transition-section');
  const transitionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.transition-number, .transition-number-alt, .transition-text, .transition-text-alt')
          .forEach(el => el.classList.add('is-visible'));
      }
    });
  }, { threshold: 0.3 });
  transitionSections.forEach(section => transitionObserver.observe(section));

  // ===================== Hero Scroll Indicator =====================
  const scrollIndicator = document.getElementById('hero-scroll-indicator');
  if (scrollIndicator) {
    scrollIndicator.addEventListener('click', () => {
      const nextSection = document.getElementById('transicao-1');
      if (nextSection) {
        nextSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  // ===================== Scroll-Sync Mapa + Itinerário =====================
  let diaAtual = 0;
  const dayCards = document.querySelectorAll('.day-card');
  const chapterDots = document.querySelectorAll('.chapter-dot');

  function updateChapterIndicator(idx) {
    chapterDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === idx);
    });
  }

  function flyToChapter(idx) {
    if (typeof flyToFazenda !== 'function') return;
    const progressMap = [0.05, 0.45, 0.55, 0.85];
    const progress = progressMap[idx] || 0;

    // Animate car on map
    if (typeof animateToProgress === 'function') {
      animateToProgress(progress);
    }

    // Highlight fazenda
    const dia = ITINERARIO[idx];
    if (dia && dia.fazendas && dia.fazendas.length > 0) {
      const fazendaId = dia.fazendas[0];
      setTimeout(() => {
        flyToFazenda(fazendaId);
      }, 500);
    }

    // Draw route progress
    if (typeof drawRouteTo === 'function') {
      drawRouteTo(progress);
    }

    // Update active card
    dayCards.forEach((card, i) => {
      card.classList.toggle('is-active', i === idx);
    });

    updateChapterIndicator(idx);
    diaAtual = idx;

    // Unlock badge for viewing itinerary
    if (window.DiscoverySystem) {
      window.DiscoverySystem.unlock('cronista');
    }
  }

  // IntersectionObserver for day cards
  const dayObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const idx = parseInt(entry.target.dataset.day, 10);
        if (!isNaN(idx) && idx !== diaAtual) {
          flyToChapter(idx);
        }
      }
    });
  }, {
    root: null,
    rootMargin: '-40% 0px -40% 0px',
    threshold: 0
  });

  // Observe day cards when they exist
  function observeDayCards() {
    const cards = document.querySelectorAll('.day-card');
    cards.forEach(card => dayObserver.observe(card));
  }

  // Call after jornada.js renders
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(observeDayCards, 500);
    });
  } else {
    setTimeout(observeDayCards, 500);
  }

  // Chapter dot clicks
  chapterDots.forEach(dot => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.dataset.chapter, 10);
      if (!isNaN(idx)) {
        const card = document.querySelector(`.day-card[data-day="${idx}"]`);
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  });

  // Expose flyToChapter globally
  window.flyToChapter = flyToChapter;
}());
