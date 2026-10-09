import {reducedMotion} from '../core/motion.js';

// The sampling map must never turn back on itself. Peak slope is at most
// pi/8; the squared-sine envelope has zero slope at both ends of the bevel.
export function lensOffset(x, y, width, height, cornerRadius = 18) {
  const radius = Math.min(cornerRadius, width / 2, height / 2);
  const band = Math.min(16, radius * .65);
  const amplitude = Math.min(2, band / 8);
  const px = x - width / 2, py = y - height / 2;
  const qx = Math.abs(px) - (width / 2 - radius);
  const qy = Math.abs(py) - (height / 2 - radius);
  const cx = Math.max(qx, 0), cy = Math.max(qy, 0);
  const length = Math.hypot(cx, cy);
  const depth = radius - length - Math.min(Math.max(qx, qy), 0);
  if (depth <= 0 || depth >= band) return [0, 0];
  const bend = amplitude * Math.sin(Math.PI * depth / band) ** 2;
  const nx = length ? cx / length : qx > qy ? 1 : 0;
  const ny = length ? cy / length : qy >= qx ? 1 : 0;
  return [-Math.sign(px) * nx * bend, -Math.sign(py) * ny * bend];
}

const PADDING = 24, DISPLACEMENT_SCALE = 8;
function lensMap(width, height, radius) {
  const canvas = document.createElement('canvas');
  const totalWidth = width + PADDING * 2, totalHeight = height + PADDING * 2;
  const ratio = Math.min(1, 1440 / totalWidth);
  canvas.width = Math.max(1, Math.round(totalWidth * ratio));
  canvas.height = Math.max(1, Math.round(totalHeight * ratio));
  const context = canvas.getContext('2d');
  if (!context) return null;
  const pixels = context.createImageData(canvas.width, canvas.height);
  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      const dx = (x + .5) * totalWidth / canvas.width - PADDING;
      const dy = (y + .5) * totalHeight / canvas.height - PADDING;
      const [ux, uy] = lensOffset(dx, dy, width, height, radius);
      const offset = (y * canvas.width + x) * 4;
      pixels.data[offset] = Math.round(255 * (.5 + ux / DISPLACEMENT_SCALE));
      pixels.data[offset + 1] = Math.round(255 * (.5 + uy / DISPLACEMENT_SCALE));
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
  let definition, filter, mapImage;
  if (chromium) {
    definition = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    definition.classList.add('liquid-glass-defs');
    definition.setAttribute('aria-hidden', 'true');
    definition.innerHTML = '<defs><filter id="offset-liquid-lens" filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB"><feGaussianBlur in="SourceGraphic" stdDeviation="5" edgeMode="duplicate" result="soft"/><feImage result="lens" preserveAspectRatio="none"/><feDisplacementMap in="soft" in2="lens" scale="8" xChannelSelector="R" yChannelSelector="G" result="refracted"/><feColorMatrix in="refracted" type="saturate" values="1.1"/></filter></defs>';
    document.body.append(definition);
    filter = definition.querySelector('filter');
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
        const radius = parseFloat(getComputedStyle(surface).borderTopLeftRadius);
        const map = lensMap(rect.width, rect.height, radius);
        if (map) {
          // The filter and every primitive use the same padded pixel region.
          // Never blend a second, undisplaced backdrop in to hide clipped edges.
          for (const node of [filter, ...filter.children]) {
            node.setAttribute('x', -PADDING); node.setAttribute('y', -PADDING);
            node.setAttribute('width', rect.width + PADDING * 2);
            node.setAttribute('height', rect.height + PADDING * 2);
          }
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
