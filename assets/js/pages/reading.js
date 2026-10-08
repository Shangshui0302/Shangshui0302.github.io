/* Scroll work is limited to real reading pages, with geometry reads before writes. */
export function initReading(root, scope) {
  const progress = root.querySelector('.reading-progress');
  const body = root.querySelector('.reading-body');
  const links = [...root.querySelectorAll('.local-toc nav a,.article-toc nav a')];
  if (!progress && !body && !links.length) return;
  const topbar = document.querySelector('.topbar');
  const statuses = [...root.querySelectorAll('.reading-status span')];
  const targets = links.map(link => ({link, target: document.getElementById(decodeURIComponent(link.hash.slice(1)))})).filter(item => item.target);
  let pending = false, previous = -1, previousHeader = 0, previousLink;
  function update() {
    pending = false;
    const header = topbar?.getBoundingClientRect().height || 76;
    const rect = body?.getBoundingClientRect();
    const value = rect ? Math.round(Math.max(0, Math.min(1, (header + 30 - rect.top) / Math.max(1, rect.height - innerHeight + header + 30))) * 100) : 0;
    let current = targets[0]?.link;
    for (const item of targets) if (item.target.getBoundingClientRect().top < header + 85) current = item.link;
    if (header !== previousHeader) {
      previousHeader = header;
      document.documentElement.style.setProperty('--topbar-height', `${header}px`);
    }
    if (progress && value !== previous) {
      previous = value;
      progress.style.setProperty('--read-progress', `${value}%`);
      progress.setAttribute('aria-valuenow', String(value));
      statuses.forEach(node => { node.textContent = `${value}%`; });
    }
    if (current !== previousLink) {
      previousLink?.removeAttribute('aria-current');
      current?.setAttribute('aria-current', 'location');
      previousLink = current;
    }
  }
  const schedule = () => { if (!pending) { pending = true; scope.frame(update); } };
  scope.on(window, 'scroll', schedule, {passive: true});
  scope.on(window, 'resize', schedule);
  scope.on(window, 'pageshow', schedule);
  document.fonts?.ready.then(() => { if (!scope.disposed) schedule(); });
  root.querySelectorAll('.scenario-controls input').forEach(input => scope.on(input, 'change', () => {
    if (!input.checked) return;
    root.querySelectorAll('.scenario-panel').forEach(panel => { panel.hidden = panel.dataset.scenario !== input.value; });
    schedule();
  }));
  update();
}
