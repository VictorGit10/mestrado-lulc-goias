/* itinerario.js — renderiza sidebar, tabs e acordeão */
(function () {
  'use strict';

  // Tabs
  const tabs = document.querySelectorAll('.sidebar-tab');
  const panels = document.querySelectorAll('.sidebar-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach(t => { t.classList.toggle('is-active', t === tab); t.setAttribute('aria-selected', t === tab); });
      panels.forEach(p => {
        const isTarget = p.dataset.panel === target;
        p.classList.toggle('is-active', isTarget);
        p.hidden = !isTarget;
      });
    });
  });

  // Toggle sidebar em mobile
  const btnToggle = document.getElementById('btn-toggle-sidebar');
  const sidebar = document.getElementById('sidebar');
  if (btnToggle && sidebar) {
    btnToggle.addEventListener('click', () => {
      sidebar.classList.toggle('is-hidden');
      const expanded = !sidebar.classList.contains('is-hidden');
      btnToggle.setAttribute('aria-expanded', String(expanded));
    });
  }

  // Renderiza itinerário
  const itContainer = document.getElementById('itinerario-list');
  if (itContainer) {
    ITINERARIO.forEach((dia, idx) => {
      const card = document.createElement('article');
      card.className = 'dia-card' + (idx === 0 ? ' is-open' : '');
      card.innerHTML = `
        <button type="button" class="dia-header" aria-expanded="${idx === 0}">
          <div>
            <h3>${dia.dia}</h3>
            <span class="dia-resumo">${dia.resumo}</span>
          </div>
          <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="dia-body">
          ${dia.atividades.map(a => `
            <div class="atividade">
              <span class="atividade-hora">${a.hora}</span>
              <div class="atividade-texto">
                <h4>${a.local}</h4>
                <p>${a.descricao}</p>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      const header = card.querySelector('.dia-header');
      header.addEventListener('click', () => {
        const open = card.classList.toggle('is-open');
        header.setAttribute('aria-expanded', String(open));
      });

      itContainer.appendChild(card);
    });
  }

  // Renderiza fazendas
  const fzContainer = document.getElementById('fazendas-list');
  if (fzContainer) {
    FAZENDAS.forEach(fz => {
      const card = document.createElement('div');
      card.className = 'fazenda-card';
      card.innerHTML = `
        <h4><span class="pin" style="background:${fz.cor}"></span>${fz.nome}</h4>
        <p class="municipio">${fz.municipio} · IBGE ${fz.cod_ibge}</p>
        <p class="codigo">${fz.codigo_car}</p>
        <button type="button" class="btn-fly" data-fazenda="${fz.id}">Ver no mapa</button>
      `;
      card.querySelector('.btn-fly').addEventListener('click', () => {
        if (typeof flyToFazenda === 'function') flyToFazenda(fz.id);
        // Em mobile, esconder sidebar ao clicar
        if (window.innerWidth <= 860 && sidebar) sidebar.classList.add('is-hidden');
      });
      fzContainer.appendChild(card);
    });
  }

  // Renderiza equipe
  const eqContainer = document.getElementById('equipe-list');
  if (eqContainer) {
    EQUIPE.forEach(p => {
      const li = document.createElement('li');
      li.className = 'equipe-item';
      const iniciais = p.nome.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
      li.innerHTML = `
        <div class="equipe-avatar">${iniciais}</div>
        <div class="equipe-info">
          <strong>${p.nome}</strong>
          <span>${p.papel}</span>
        </div>
      `;
      eqContainer.appendChild(li);
    });
  }
}());
