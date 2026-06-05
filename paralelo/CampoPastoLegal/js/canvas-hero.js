/* canvas-hero.js — Efeito de partículas orgânicas no hero */
(function () {
  'use strict';

  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let animationId = null;
  let isVisible = true;
  let mouseX = 0;
  let mouseY = 0;
  let isHovering = false;

  const config = {
    particleCount: 40,
    colors: ['rgba(45, 106, 66, 0.4)', 'rgba(197, 146, 42, 0.3)', 'rgba(255, 255, 255, 0.5)'],
    minSize: 1,
    maxSize: 4,
    speed: 0.3,
    mouseRepelRadius: 150,
    mouseRepelStrength: 0.5
  };

  function resize() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = hero.offsetWidth * dpr;
    canvas.height = hero.offsetHeight * dpr;
    canvas.style.width = hero.offsetWidth + 'px';
    canvas.style.height = hero.offsetHeight + 'px';
    ctx.scale(dpr, dpr);
  }

  function createParticle() {
    const hero = document.getElementById('hero');
    if (!hero) return null;
    return {
      x: Math.random() * hero.offsetWidth,
      y: Math.random() * hero.offsetHeight,
      size: config.minSize + Math.random() * (config.maxSize - config.minSize),
      color: config.colors[Math.floor(Math.random() * config.colors.length)],
      vx: (Math.random() - 0.5) * config.speed,
      vy: (Math.random() - 0.5) * config.speed - 0.1,
      opacity: 0.2 + Math.random() * 0.5,
      opacitySpeed: 0.005 + Math.random() * 0.01,
      opacityDirection: Math.random() > 0.5 ? 1 : -1
    };
  }

  function initParticles() {
    particles = [];
    for (let i = 0; i < config.particleCount; i++) {
      const p = createParticle();
      if (p) particles.push(p);
    }
  }

  function updateParticles() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    const w = hero.offsetWidth;
    const h = hero.offsetHeight;

    particles.forEach(p => {
      // Mouse repulsion
      if (isHovering) {
        const dx = p.x - mouseX;
        const dy = p.y - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < config.mouseRepelRadius && dist > 0) {
          const force = (config.mouseRepelRadius - dist) / config.mouseRepelRadius;
          p.vx += (dx / dist) * force * config.mouseRepelStrength;
          p.vy += (dy / dist) * force * config.mouseRepelStrength;
        }
      }

      p.x += p.vx;
      p.y += p.vy;

      // Friction
      p.vx *= 0.99;
      p.vy *= 0.99;

      // Opacity oscillation
      p.opacity += p.opacitySpeed * p.opacityDirection;
      if (p.opacity > 0.7 || p.opacity < 0.1) {
        p.opacityDirection *= -1;
      }

      // Wrap around
      if (p.x < -10) p.x = w + 10;
      if (p.x > w + 10) p.x = -10;
      if (p.y < -10) p.y = h + 10;
      if (p.y > h + 10) p.y = -10;
    });
  }

  function drawParticles() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    ctx.clearRect(0, 0, hero.offsetWidth, hero.offsetHeight);

    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color.replace(/[\d.]+\)$/, p.opacity + ')');
      ctx.fill();
    });
  }

  function animate() {
    if (!isVisible) {
      animationId = requestAnimationFrame(animate);
      return;
    }
    updateParticles();
    drawParticles();
    animationId = requestAnimationFrame(animate);
  }

  // Intersection Observer for performance
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      isVisible = entry.isIntersecting;
    });
  }, { threshold: 0 });
  observer.observe(canvas);

  // Mouse interaction
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
    isHovering = true;
  });
  canvas.addEventListener('mouseleave', () => {
    isHovering = false;
  });

  // Visibility change
  document.addEventListener('visibilitychange', () => {
    isVisible = !document.hidden && canvas.getBoundingClientRect().top < window.innerHeight;
  });

  // Init
  resize();
  initParticles();
  animate();

  window.addEventListener('resize', () => {
    resize();
    initParticles();
  });
}());
