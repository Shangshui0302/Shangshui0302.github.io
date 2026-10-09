import {reducedMotion} from '../core/motion.js';

// A normal map for a rounded lens: the flat centre does not shift, while its
// bevel bends the actual backdrop inward. Generated only when the size changes.
function lensMap(width, height) {
  const canvas = document.createElement('canvas');
  const ratio = Math.min(1, 1440 / width);
  canvas.width = Math.max(1, Math.round(width * ratio));
  canvas.height = Math.max(1, Math.round(height * ratio));
  const context = canvas.getContext('2d');
  if (!context) return null;
  const pixels = context.createImageData(canvas.width, canvas.height);
  const radius = Math.min(24, height / 2);
  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      const px = (x + .5) / ratio - width / 2;
      const py = (y + .5) / ratio - height / 2;
      const qx = Math.abs(px) - (width / 2 - radius);
      const qy = Math.abs(py) - (height / 2 - radius);
      const cx = Math.max(qx, 0), cy = Math.max(qy, 0);
      const length = Math.hypot(cx, cy);
      const depth = radius - length - Math.min(Math.max(qx, qy), 0);
      const bend = depth > 0 && depth < 22 ? Math.sin(depth / 22 * Math.PI) * .46 : 0;
      const nx = length ? cx / length : qx > qy ? 1 : 0;
      const ny = length ? cy / length : qy >= qx ? 1 : 0;
      const offset = (y * canvas.width + x) * 4;
      pixels.data[offset] = Math.round(128 - Math.sign(px) * nx * bend * 127);
      pixels.data[offset + 1] = Math.round(128 - Math.sign(py) * ny * bend * 127);
      pixels.data[offset + 2] = 128;
      pixels.data[offset + 3] = 255;
    }
  }
  context.putImageData(pixels, 0, 0);
  return canvas.toDataURL();
}

export function initLiquidGlass() {
  const header = document.querySelector('.topbar');
  if (!header || !(CSS.supports('backdrop-filter', 'blur(1px)') || CSS.supports('-webkit-backdrop-filter', 'blur(1px)'))) return;
  const surface = document.createElement('span');
  surface.className = 'liquid-glass';
  surface.setAttribute('aria-hidden', 'true');
  header.prepend(surface);
  header.dataset.glassReady = '';

  // URL backdrop filters need pixel verification, not only CSS.supports().
  // Chromium is the validated path. Other engines retain the working blur.
  const chromium = navigator.userAgentData?.brands?.some(item => /Chromium/.test(item.brand))
    || /Chrome\//.test(navigator.userAgent) && !/EdgiOS|CriOS/.test(navigator.userAgent);
  let definition, mapImage;
  if (chromium) {
    definition = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    definition.classList.add('liquid-glass-defs');
    definition.setAttribute('aria-hidden', 'true');
    definition.innerHTML = '<defs><filter id="offset-liquid-lens" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feGaussianBlur in="SourceGraphic" stdDeviation="6" result="soft"/><feImage result="lens" width="100%" height="100%" preserveAspectRatio="none"/><feDisplacementMap in="soft" in2="lens" scale="72" xChannelSelector="R" yChannelSelector="G" result="refracted"/><feComposite in="refracted" in2="soft" operator="over"/><feColorMatrix type="saturate" values="1.35"/></filter></defs>';
    document.body.append(definition);
    mapImage = definition.querySelector('feImage');
  }

  let size = '', frame = 0, resize = true, pointer = null;
  const finePointer = matchMedia('(any-pointer:fine)');
  function paint() {
    frame = 0;
    if (reducedMotion() || document.hidden) return;
    const rect = surface.getBoundingClientRect();
    const scene = document.querySelector('.galaxy-experience');
    const onDark = Boolean(scene && scene.getBoundingClientRect().bottom > rect.bottom);
    if (header.dataset.glassOnDark !== String(onDark)) header.dataset.glassOnDark = String(onDark);
    if (resize && mapImage && rect.width && rect.height) {
      resize = false;
      const nextSize = `${Math.round(rect.width)}:${Math.round(rect.height)}`;
      if (nextSize !== size) {
        const map = lensMap(rect.width, rect.height);
        if (map) {
          mapImage.setAttribute('href', map);
          surface.style.setProperty('--liquid-refraction', 'url("#offset-liquid-lens")');
          size = nextSize;
        }
      }
    }
    if (pointer) {
      surface.style.setProperty('--glass-x', `${Math.max(0, Math.min(100, (pointer.x - rect.left) / rect.width * 100)).toFixed(1)}%`);
      surface.style.setProperty('--glass-y', `${Math.max(0, Math.min(100, (pointer.y - rect.top) / rect.height * 100)).toFixed(1)}%`);
      pointer = null;
    }
  }
  function schedule() {
    if (!frame && !reducedMotion() && !document.hidden) frame = requestAnimationFrame(paint);
  }
  function resetPointer() {
    pointer = null;
    surface.style.removeProperty('--glass-x');
    surface.style.removeProperty('--glass-y');
  }
  header.addEventListener('pointermove', event => {
    if (!finePointer.matches || reducedMotion() || event.pointerType === 'touch') return;
    pointer = {x:event.clientX, y:event.clientY};
    schedule();
  }, {passive:true});
  header.addEventListener('pointerleave', resetPointer);
  const observer = new ResizeObserver(() => { resize = true; schedule(); });
  observer.observe(header);
  const routeObserver = new MutationObserver(schedule);
  routeObserver.observe(document.body, {attributes:true, attributeFilter:['class']});
  addEventListener('scroll', schedule, {passive:true});
  document.addEventListener('offset:motion-change', () => {
    cancelAnimationFrame(frame); frame = 0; resetPointer(); resize = true; schedule();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(frame); frame = 0; resetPointer(); }
    else schedule();
  });
  // Persistent shell: a single event-driven instance, with no idle render loop.
  schedule();
}
