/* A single preference shared by navigation, controls and the stellar scene. */
export const reducedMotion = () => document.documentElement.dataset.reducedMotion === 'true';
export function initMotion() {
  const root = document.documentElement;
  const system = matchMedia('(prefers-reduced-motion: reduce)');
  const button = document.querySelector('.motion');
  let preference;
  try { preference = localStorage.getItem('offset-reduced-motion'); } catch {}
  const apply = () => {
    const reduced = system.matches || preference === 'true';
    root.dataset.reducedMotion = String(reduced);
    root.classList.toggle('motion-ready', !reduced);
    button?.setAttribute('aria-pressed', String(reduced));
    if (button) {
      button.disabled = system.matches;
      button.title = system.matches ? '遵循系统的减少动效设置' : '';
    }
  };
  button?.addEventListener('click', () => {
    preference = String(!reducedMotion());
    try { localStorage.setItem('offset-reduced-motion', preference); } catch {}
    apply();
  });
  system.addEventListener('change', apply);
  root.classList.remove('no-js');
  apply();
}
