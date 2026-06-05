/* mapa.js — Leaflet com rota real, animação e estilo limpo (tema claro) */
(function () {
  'use strict';

  const el = document.getElementById('map');
  if (!el) return;

  // ===================== Inicialização do mapa =====================
  const map = L.map('map', {
    zoomControl: false,
    attributionControl: false,
    minZoom: 5,
    maxZoom: 18
  }).setView([-16.5, -44.0], 6);

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // CartoDB Positron — clean, light, elegante
  L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }
  ).addTo(map);

  // ===================== Carregar rota real =====================
  let rotaLayer = null;
  let rotaCoords = [];
  let carMarker = null;
  let animationFrame = null;
  let isPlaying = false;
  let currentIndex = 0;

  fetch('assets/rota_completa.json')
    .then(r => r.json())
    .then(data => {
      const coords = data.routes[0].geometry.coordinates;
      // Simplificar para performance
      rotaCoords = coords.filter((_, i) => i % 8 === 0).map(c => [c[1], c[0]]);

      // Rota principal
      rotaLayer = L.polyline(rotaCoords, {
        color: '#2d6a42',
        weight: 3,
        opacity: 0.7,
        lineCap: 'round',
        lineJoin: 'round',
        dashArray: '8, 4'
      }).addTo(map);

      addCidadeMarkers();
      addFazendaMarkers();
      window._initCarMarker();
      map.fitBounds(rotaLayer.getBounds().pad(0.08), { animate: true, duration: 1.5 });

      window.dispatchEvent(new CustomEvent('mapa:pronto'));
    })
    .catch(err => {
      console.warn('Falha ao carregar rota real, usando fallback:', err);
      rotaCoords = ROTA_COORDS;
      rotaLayer = L.polyline(rotaCoords, {
        color: '#2d6a42', weight: 3, opacity: 0.7, dashArray: '8, 4'
      }).addTo(map);
      addCidadeMarkers();
      addFazendaMarkers();
      window._initCarMarker();
      map.fitBounds(rotaLayer.getBounds().pad(0.08));
      window.dispatchEvent(new CustomEvent('mapa:pronto'));
    });

  // ===================== Marcadores =====================
  function createPinIcon(color, size = 12, label = '') {
    const labelHtml = label
      ? `<span style="
          position:absolute;
          left:50%;transform:translateX(-50%);
          top:${size + 8}px;
          font-size:10px;font-weight:600;
          color:#1a2e1f;
          white-space:nowrap;
          font-family:Inter,system-ui,sans-serif;
          text-shadow: 0 1px 3px rgba(255,255,255,0.9);
        ">${label}</span>`
      : '';
    return L.divIcon({
      className: 'custom-pin',
      html: `<div style="position:relative;">
        <div style="
          width:${size}px;height:${size}px;
          border-radius:50%;
          background:${color};
          border:2.5px solid #fff;
          box-shadow:0 2px 8px rgba(0,0,0,0.25);
        "></div>
        ${labelHtml}
      </div>`,
      iconSize: [size + 5, size + 5],
      iconAnchor: [(size + 5) / 2, (size + 5) / 2]
    });
  }

  function addCidadeMarkers() {
    ROTA_MUNICIPIOS.forEach(m => {
      const isEndpoint = m.tipo === 'partida' || m.tipo === 'chegada';
      const icon = createPinIcon(
        isEndpoint ? '#c5922a' : '#2d6a42',
        isEndpoint ? 14 : 10,
        m.nome
      );
      const marker = L.marker(m.coords, { icon }).addTo(map);
      const tipoLabel = m.tipo === 'partida' ? 'Partida' :
                        m.tipo === 'chegada' ? 'Chegada' : 'Pernoite';
      marker.bindPopup(`
        <h4>${m.nome}</h4>
        <p><strong style="color:#2d6a42;">${tipoLabel}</strong></p>
      `, { offset: [0, -8] });
    });
  }

  function addFazendaMarkers() {
    FAZENDAS.forEach(fz => {
      const icon = createPinIcon(fz.cor, 14);
      const marker = L.marker(fz.coords, { icon }).addTo(map);
      marker.bindPopup(`
        <h4>${fz.nome}</h4>
        <p>${fz.municipio}</p>
        <p style="font-size:0.7rem;opacity:0.6;word-break:break-all;">${fz.codigo_car}</p>
      `, { offset: [0, -10] });
      fz.marker = marker;
    });
  }

  // ===================== Carro animado =====================
  function initCarMarker() {
    if (!rotaCoords.length) return;
    const carIcon = L.divIcon({
      className: 'car-marker',
      html: `<div style="
        width:26px;height:26px;
        background:#2d6a42;
        border-radius:50%;
        border:2.5px solid #fff;
        box-shadow:0 3px 12px rgba(0,0,0,0.3);
        display:grid;place-items:center;
      ">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/>
          <circle cx="7" cy="17" r="2"/>
          <path d="M9 17h6"/>
          <circle cx="17" cy="17" r="2"/>
        </svg>
      </div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });
    carMarker = L.marker(rotaCoords[0], { icon: carIcon, zIndexOffset: 1000 }).addTo(map);
  }

  // ===================== Animação =====================
  function animateCar(targetProgress, duration = 2000) {
    if (!rotaCoords.length || !carMarker) return;
    isPlaying = true;
    const startIndex = currentIndex;
    const targetIndex = Math.floor(targetProgress * (rotaCoords.length - 1));
    const totalSteps = targetIndex - startIndex;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const idx = startIndex + Math.floor(totalSteps * eased);

      if (idx >= 0 && idx < rotaCoords.length) {
        currentIndex = idx;
        carMarker.setLatLng(rotaCoords[idx]);
        if (idx % 20 === 0) {
          map.panTo(rotaCoords[idx], { animate: true, duration: 0.5 });
        }
      }

      if (progress < 1) {
        animationFrame = requestAnimationFrame(step);
      } else {
        isPlaying = false;
        currentIndex = targetIndex;
      }
    }
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(step);
  }

  function playFullJourney() {
    if (!rotaCoords.length || !carMarker) return;
    isPlaying = true;
    currentIndex = 0;
    carMarker.setLatLng(rotaCoords[0]);
    const duration = 8000;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const idx = Math.floor(eased * (rotaCoords.length - 1));

      if (idx >= 0 && idx < rotaCoords.length) {
        currentIndex = idx;
        carMarker.setLatLng(rotaCoords[idx]);
        if (idx % 30 === 0) {
          map.panTo(rotaCoords[idx], { animate: true, duration: 0.6 });
        }
      }

      if (progress < 1) {
        animationFrame = requestAnimationFrame(step);
      } else {
        isPlaying = false;
      }
    }
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(step);
  }

  // ===================== Funções globais =====================
  window.flyToFazenda = function (id) {
    const fz = FAZENDAS.find(f => f.id === id);
    if (!fz || !fz.marker) return;
    map.flyTo(fz.coords, 14, { duration: 1.5 });
    setTimeout(() => fz.marker.openPopup(), 1500);
  };

  window.animateToProgress = function (progress) {
    animateCar(progress);
  };

  window.playJourney = function () {
    playFullJourney();
  };

  window.flyToCoords = function (coords, zoom = 13) {
    map.flyTo(coords, zoom, { duration: 1.5 });
  };

  // ===================== Animação de desenho da rota =====================
  let drawAnimationFrame = null;
  let drawnLayer = null;

  function drawRouteTo(targetProgress) {
    if (!rotaCoords.length || !rotaLayer) return;
    const targetIndex = Math.floor(targetProgress * (rotaCoords.length - 1));
    const segment = rotaCoords.slice(0, targetIndex + 1);

    if (drawnLayer) {
      map.removeLayer(drawnLayer);
    }

    if (segment.length < 2) return;

    drawnLayer = L.polyline(segment, {
      color: '#c5922a',
      weight: 4,
      opacity: 0.9,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(map);
  }

  function animateDrawRoute(targetProgress, duration = 1500) {
    if (!rotaCoords.length) return;
    const startTime = performance.now();
    const targetIndex = Math.floor(targetProgress * (rotaCoords.length - 1));

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentIndex = Math.floor(targetIndex * eased);

      if (currentIndex >= 1) {
        const segment = rotaCoords.slice(0, currentIndex + 1);
        if (drawnLayer) map.removeLayer(drawnLayer);
        drawnLayer = L.polyline(segment, {
          color: '#c5922a',
          weight: 4,
          opacity: 0.9,
          lineCap: 'round',
          lineJoin: 'round'
        }).addTo(map);
      }

      if (progress < 1) {
        drawAnimationFrame = requestAnimationFrame(step);
      }
    }
    cancelAnimationFrame(drawAnimationFrame);
    drawAnimationFrame = requestAnimationFrame(step);
  }

  // ===================== Funções globais expandidas =====================
  window.drawRouteTo = function(progress) {
    animateDrawRoute(progress);
  };

  window.flyToChapter = function(idx) {
    const progressMap = [0.05, 0.45, 0.55, 0.85];
    const progress = progressMap[idx] || 0;
    animateDrawRoute(progress);

    // Highlight fazenda
    const dia = (typeof ITINERARIO !== 'undefined') ? ITINERARIO[idx] : null;
    if (dia && dia.fazendas && dia.fazendas.length > 0) {
      const fazendaId = dia.fazendas[0];
      setTimeout(() => {
        const fz = (typeof FAZENDAS !== 'undefined') ? FAZENDAS.find(f => f.id === fazendaId) : null;
        if (fz) {
          map.flyTo(fz.coords, 13, { duration: 1.5 });
          if (fz.marker) {
            setTimeout(() => fz.marker.openPopup(), 1600);
          }
        }
      }, 800);
    }
  };

  // Easter egg: click on car marker shows fun fact
  // (carMarker is set in initCarMarker, we'll add a click listener there)
  const originalInitCarMarker = initCarMarker;
  window._initCarMarker = function() {
    originalInitCarMarker();
    if (carMarker) {
      carMarker.on('click', () => {
        const popup = L.popup({ offset: [0, -15] })
          .setLatLng(carMarker.getLatLng())
          .setContent('<h4>🚗 Curiosidade</h4><p>1.977 km é o equivalente a ir de Goiânia até Recife! A rota passa por 4 fazendas e 3 cidades do Norte de Minas.</p>')
          .openOn(map);
      });
    }
  };
}());
