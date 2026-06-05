/* jornada.js — renderiza itinerário, fazendas, equipe e controla a navegação */
(function () {
  'use strict';

  let diaAtual = 0;

  // ===================== Renderizar Itinerário =====================
  const container = document.getElementById('itinerary-container');
  if (container) {
    ITINERARIO.forEach((dia, idx) => {
      const card = document.createElement('div');
      card.className = 'day-card fade-in' + (idx === 0 ? ' is-active is-open' : '');
      card.dataset.day = idx;

      // Stats HTML
      const statsHtml = (dia.stats || []).map(s => `
        <div class="day-stat">
          <span class="day-stat-value">${s.valor}</span>
          <span class="day-stat-label">${s.label}</span>
        </div>
      `).join('');

      // Activities HTML
      const activitiesHtml = dia.atividades.map(a => `
        <div class="activity">
          <span class="activity-time">${a.hora}</span>
          <div class="activity-content">
            <h4>${a.local}</h4>
            <p>${a.descricao}</p>
          </div>
        </div>
      `).join('');

      // Fazendas chips HTML
      const fazendasHtml = (dia.fazendas || []).map(fzId => {
        const fz = FAZENDAS.find(f => f.id === fzId);
        if (!fz) return '';
        return `
          <button type="button" class="fazenda-chip" data-fazenda="${fz.id}">
            <span class="fazenda-chip-dot" style="background:${fz.cor}"></span>
            ${fz.nome}
          </button>
        `;
      }).join('');

      card.innerHTML = `
        <div class="day-card-header">
          <div class="day-badge">${idx + 1}</div>
          <div class="day-info">
            <span class="day-date">${dia.dia}</span>
            <h3 class="day-title">${dia.resumo}</h3>
          </div>
          <svg class="day-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
        <div class="day-body">
          <div class="day-body-inner">
            <div class="day-stats">${statsHtml}</div>
            <div class="activities">${activitiesHtml}</div>
            ${fazendasHtml ? '<div class="day-fazendas">' + fazendasHtml + '</div>' : ''}
          </div>
        </div>
      `;

      // Click header to expand/collapse
      const header = card.querySelector('.day-card-header');
      header.addEventListener('click', () => {
        // Close others
        document.querySelectorAll('.day-card.is-open').forEach(c => {
          if (c !== card) c.classList.remove('is-open');
        });
        // Toggle this
        card.classList.toggle('is-open');
        // Activate
        selectDay(idx);

        // Track discovery
        if (window.DiscoverySystem) {
          window.DiscoverySystem.trackDay(idx);
        }
      });

      // Fazenda chip clicks
      card.querySelectorAll('.fazenda-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          if (typeof flyToFazenda === 'function') {
            flyToFazenda(chip.dataset.fazenda);
          }
        });
      });

      container.appendChild(card);
    });
  }

  // ===================== Renderizar Fazendas =====================
  const fazendasGrid = document.getElementById('fazendas-grid');
  if (fazendasGrid) {
    FAZENDAS.forEach(fz => {
      const card = document.createElement('div');
      card.className = 'fazenda-card fade-in';
      card.innerHTML = `
        <div class="fazenda-header">
          <span class="fazenda-pin" style="background:${fz.cor}"></span>
          <span class="fazenda-name">${fz.nome}</span>
        </div>
        <p class="fazenda-location">${fz.municipio} · IBGE ${fz.cod_ibge}</p>
        <p class="fazenda-car">${fz.codigo_car}</p>
        <button type="button" class="btn-map" data-fazenda="${fz.id}">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          Ver no mapa
        </button>
      `;
      card.querySelector('.btn-map').addEventListener('click', () => {
        if (typeof flyToFazenda === 'function') flyToFazenda(fz.id);
        // Scroll to map
        document.getElementById('itinerario')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      fazendasGrid.appendChild(card);
    });
  }

  // ===================== Renderizar Equipe =====================
  const teamGrid = document.getElementById('team-grid');
  if (teamGrid) {
    EQUIPE.forEach(p => {
      const card = document.createElement('div');
      card.className = 'team-card fade-in';
      const iniciais = p.nome.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
      card.innerHTML = `
        <div class="team-avatar">${iniciais}</div>
        <div>
          <div class="team-name">${p.nome}</div>
          <div class="team-role">${p.papel}</div>
        </div>
      `;
      teamGrid.appendChild(card);
    });
  }

  // ===================== Seleção de dia =====================
  function selectDay(idx, animate = true) {
    diaAtual = idx;

    // Update active states
    document.querySelectorAll('.day-card').forEach((card, i) => {
      card.classList.toggle('is-active', i === idx);
    });

    // Animate map
    if (animate && typeof animateToProgress === 'function') {
      const progressMap = [0.05, 0.45, 0.55, 0.85];
      animateToProgress(progressMap[idx] || 0);
    }
  }

  // ===================== Controles =====================
  const btnPrev = document.getElementById('btn-prev');
  const btnPlay = document.getElementById('btn-play');
  const btnNext = document.getElementById('btn-next');

  if (btnPrev) btnPrev.addEventListener('click', () => {
    if (diaAtual > 0) {
      const newIdx = diaAtual - 1;
      openDay(newIdx);
      selectDay(newIdx);
    }
  });
  if (btnNext) btnNext.addEventListener('click', () => {
    if (diaAtual < ITINERARIO.length - 1) {
      const newIdx = diaAtual + 1;
      openDay(newIdx);
      selectDay(newIdx);
    }
  });
  if (btnPlay) btnPlay.addEventListener('click', () => {
    if (typeof playJourney === 'function') playJourney();
  });

  function openDay(idx) {
    document.querySelectorAll('.day-card').forEach((card, i) => {
      card.classList.toggle('is-open', i === idx);
    });
    // Scroll the day card into view
    const target = document.querySelector(`.day-card[data-day="${idx}"]`);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  // ===================== Header nav highlight =====================
  const navLinks = document.querySelectorAll('.header-nav a');
  const sections = ['itinerario', 'fazendas', 'equipe'];

  function updateNav() {
    const scrollY = window.scrollY + 100;
    let current = '';
    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el && el.offsetTop <= scrollY) current = id;
    });
    navLinks.forEach(link => {
      link.classList.toggle('is-active', link.getAttribute('href') === '#' + current);
    });
  }
  window.addEventListener('scroll', updateNav, { passive: true });

  // ===================== 3D Card Hover Effect =====================
  function init3DCardEffect() {
    const cards = document.querySelectorAll('.fazenda-card, .team-card');
    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;
        card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }

  // Apply after DOM renders
  setTimeout(init3DCardEffect, 600);

  // ===================== Init =====================
  window.addEventListener('mapa:pronto', () => {
    selectDay(0, false);
  });
}());
