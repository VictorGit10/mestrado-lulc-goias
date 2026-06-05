/* descobertas.js — Sistema de badges, progresso e easter eggs */
(function () {
  'use strict';

  const STORAGE_KEY = 'pl_discoveries';

  const BADGES = [
    {
      id: 'cartografo',
      title: 'Cartógrafo',
      desc: 'Visualizou todas as fazendas no mapa',
      icon: '🗺️',
      condition: () => {
        const seen = state.seenFazendas || new Set();
        return seen.size >= 4;
      }
    },
    {
      id: 'cronista',
      title: 'Cronista',
      desc: 'Leu todos os dias do itinerário',
      icon: '📜',
      condition: () => {
        const seen = state.seenDays || new Set();
        return seen.size >= 4;
      }
    },
    {
      id: 'expedicionario',
      title: 'Expedicionário',
      desc: 'Acompanhou a rota completa',
      icon: '🚗',
      condition: () => state.playedJourney === true
    },
    {
      id: 'colecionador',
      title: 'Colecionador',
      desc: 'Abriu o diário de campo',
      icon: '📓',
      condition: () => state.openedForm === true
    },
    {
      id: 'mestre',
      title: 'Mestre da Expedição',
      desc: 'Completou 100% da jornada',
      icon: '🏆',
      condition: () => {
        const total = BADGES.length - 1; // exclude mestre itself
        let unlocked = 0;
        BADGES.forEach(b => {
          if (b.id !== 'mestre' && state.unlocked.has(b.id)) unlocked++;
        });
        return unlocked >= total;
      }
    }
  ];

  let state = {
    unlocked: new Set(),
    seenFazendas: new Set(),
    seenDays: new Set(),
    playedJourney: false,
    openedForm: false,
    scrollProgress: 0
  };

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data = JSON.parse(raw);
        state.unlocked = new Set(data.unlocked || []);
        state.seenFazendas = new Set(data.seenFazendas || []);
        state.seenDays = new Set(data.seenDays || []);
        state.playedJourney = data.playedJourney || false;
        state.openedForm = data.openedForm || false;
        state.scrollProgress = data.scrollProgress || 0;
      }
    } catch (e) {
      console.warn('Erro ao carregar descobertas:', e);
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        unlocked: Array.from(state.unlocked),
        seenFazendas: Array.from(state.seenFazendas),
        seenDays: Array.from(state.seenDays),
        playedJourney: state.playedJourney,
        openedForm: state.openedForm,
        scrollProgress: state.scrollProgress
      }));
    } catch (e) {
      console.warn('Erro ao salvar descobertas:', e);
    }
  }

  function showToast(badge) {
    const toast = document.getElementById('badge-toast');
    const title = document.getElementById('badge-toast-title');
    const desc = document.getElementById('badge-toast-desc');
    if (!toast || !title || !desc) return;

    title.textContent = 'Selo desbloqueado: ' + badge.title;
    desc.textContent = badge.desc;
    toast.classList.add('is-visible');

    setTimeout(() => {
      toast.classList.remove('is-visible');
    }, 4000);
  }

  function unlock(badgeId) {
    if (state.unlocked.has(badgeId)) return;

    const badge = BADGES.find(b => b.id === badgeId);
    if (!badge) return;

    if (badge.condition && !badge.condition()) return;

    state.unlocked.add(badgeId);
    saveState();
    renderBadges();
    showToast(badge);

    // Check for mestre
    if (badgeId !== 'mestre') {
      setTimeout(() => unlock('mestre'), 500);
    }
  }

  function renderBadges() {
    const container = document.getElementById('discovery-badges');
    const count = document.getElementById('discovery-count');
    if (!container) return;

    container.innerHTML = '';
    BADGES.forEach(badge => {
      const isUnlocked = state.unlocked.has(badge.id);
      const el = document.createElement('div');
      el.className = 'discovery-badge' + (isUnlocked ? ' is-unlocked' : '');
      el.innerHTML = `
        <span class="badge-icon">${isUnlocked ? badge.icon : '🔒'}</span>
        <span>${badge.title}</span>
      `;
      container.appendChild(el);
    });

    if (count) {
      count.textContent = state.unlocked.size;
    }
  }

  // Track fazenda views
  function trackFazenda(fazendaId) {
    state.seenFazendas.add(fazendaId);
    saveState();
    unlock('cartografo');
  }

  // Track day views
  function trackDay(dayIdx) {
    state.seenDays.add(dayIdx);
    saveState();
    unlock('cronista');
  }

  // Track journey play
  function trackJourneyPlay() {
    state.playedJourney = true;
    saveState();
    unlock('expedicionario');
  }

  // Track form open
  function trackFormOpen() {
    state.openedForm = true;
    saveState();
    unlock('colecionador');
  }

  // Toggle panel
  const toggle = document.getElementById('discovery-toggle');
  const badgesPanel = document.getElementById('discovery-badges');
  if (toggle && badgesPanel) {
    toggle.addEventListener('click', () => {
      const isOpen = badgesPanel.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // Hook into existing events
  const originalFlyToFazenda = window.flyToFazenda;
  window.flyToFazenda = function(id) {
    trackFazenda(id);
    if (originalFlyToFazenda) originalFlyToFazenda(id);
  };

  const originalPlayJourney = window.playJourney;
  window.playJourney = function() {
    trackJourneyPlay();
    if (originalPlayJourney) originalPlayJourney();
  };

  // Hook form open
  const fab = document.getElementById('fab-form');
  if (fab) {
    fab.addEventListener('click', trackFormOpen);
  }

  // Scroll progress tracking
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    state.scrollProgress = docHeight > 0 ? (scrollTop / docHeight) : 0;
    saveState();
  }, { passive: true });

  // Init
  loadState();
  renderBadges();

  // Expose API
  window.DiscoverySystem = {
    unlock,
    trackFazenda,
    trackDay,
    trackJourneyPlay,
    trackFormOpen,
    getState: () => ({ ...state, unlocked: Array.from(state.unlocked) })
  };
}());
