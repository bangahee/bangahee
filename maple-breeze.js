/* Textured maple leaves on a click-through layer above the entire page. */
(() => {
  'use strict';
  const canvas = document.getElementById('maple-layer');
  const button = document.getElementById('breeze-toggle');
  const label = document.getElementById('breeze-label');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const atlas = new Image();
  const leaves = [];
  const sprites = [];
  const random = (min, max) => min + Math.random() * (max - min);
  let width = 0, height = 0, frameId = null, previousTime = 0, time = 0;
  let ready = false;
  let override = null;
  try { override = localStorage.getItem('garden-maple-motion'); } catch (_) { /* Storage is optional. */ }
  let enabled = override === null ? !reducedMotion.matches : override === 'on';

  function newLeaf(scattered = false) {
    return {
      x: random(-90, width + 90),
      y: scattered ? random(-height * .15, height) : random(-130, -50),
      size: random(23, width < 600 ? 43 : 59),
      speed: random(26, 66),
      drift: random(9, 27),
      phase: random(0, Math.PI * 2),
      rotation: random(0, Math.PI * 2),
      spin: random(-.65, .65),
      flutter: random(.55, 1.1),
      sprite: Math.floor(random(0, sprites.length)),
      opacity: random(.78, .98),
    };
  }

  function resize() {
    const oldWidth = width, oldHeight = height;
    width = window.innerWidth;
    height = window.innerHeight;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (!ready) return;
    const count = Math.max(16, Math.min(48, Math.round(width * height / 27000)));
    if (oldWidth && oldHeight) {
      for (const leaf of leaves) {
        leaf.x *= width / oldWidth;
        leaf.y *= height / oldHeight;
      }
    }
    leaves.splice(count);
    while (leaves.length < count) leaves.push(newLeaf(true));
  }

  function paint(now) {
    frameId = null;
    if (!enabled || document.hidden || !ready) return;
    const dt = previousTime ? Math.min((now - previousTime) / 1000, .05) : 0;
    previousTime = now;
    time += dt;
    ctx.clearRect(0, 0, width, height);
    const wind = 13 + Math.sin(time * .24) * 13 + Math.sin(time * .67) * 6;
    for (let i = 0; i < leaves.length; i++) {
      let leaf = leaves[i];
      leaf.y += leaf.speed * dt;
      leaf.x += (wind + leaf.drift + Math.sin(time * .75 + leaf.phase) * 17) * dt;
      leaf.rotation += leaf.spin * dt;
      if (leaf.y > height + 100) leaves[i] = leaf = newLeaf();
      if (leaf.x > width + 100) leaf.x = -95;
      if (leaf.x < -100) leaf.x = width + 95;
      const flip = Math.cos(time * leaf.flutter + leaf.phase);
      // Preserve a short edge-on moment as a leaf turns through the breeze.
      const squash = Math.sign(flip || 1) * Math.max(.12, Math.abs(flip));
      const sway = Math.sin(time * 1.1 + leaf.phase) * 8;
      ctx.save();
      ctx.translate(leaf.x + sway, leaf.y);
      ctx.rotate(leaf.rotation + Math.sin(time * .6 + leaf.phase) * .22);
      ctx.scale(squash, 1);
      ctx.globalAlpha = leaf.opacity;
      ctx.drawImage(sprites[leaf.sprite], -leaf.size / 2, -leaf.size / 2, leaf.size, leaf.size);
      ctx.restore();
    }
    frameId = window.requestAnimationFrame(paint);
  }

  function sync() {
    if (frameId !== null) cancelAnimationFrame(frameId);
    frameId = null;
    previousTime = 0;
    button.setAttribute('aria-pressed', String(enabled));
    label.textContent = enabled ? 'Pause leaves' : 'Let leaves fall';
    if (!enabled) ctx.clearRect(0, 0, width, height);
    if (enabled && ready && !document.hidden) frameId = requestAnimationFrame(paint);
  }

  atlas.onload = () => {
    const sw = atlas.naturalWidth / 3, sh = atlas.naturalHeight / 2;
    for (let row = 0; row < 2; row++) {
      for (let col = 0; col < 3; col++) {
        const tile = document.createElement('canvas');
        tile.width = tile.height = 160;
        tile.getContext('2d').drawImage(atlas, col * sw, row * sh, sw, sh, 0, 0, 160, 160);
        sprites.push(tile);
      }
    }
    ready = true;
    resize();
    button.hidden = false;
    sync();
  };
  atlas.onerror = () => { canvas.hidden = true; };
  button.addEventListener('click', () => {
    enabled = !enabled;
    override = enabled ? 'on' : 'off';
    try { localStorage.setItem('garden-maple-motion', override); } catch (_) { /* No persistent storage required. */ }
    sync();
  });
  reducedMotion.addEventListener('change', () => {
    if (override === null) { enabled = !reducedMotion.matches; sync(); }
  });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('resize', resize, { passive: true });
  resize();
  atlas.src = new URL('maple/leaves-atlas.png', document.baseURI).href;
})();
