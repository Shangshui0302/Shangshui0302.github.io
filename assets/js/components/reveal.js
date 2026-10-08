export function initReveals(root, scope) {
  if (!('IntersectionObserver' in window)) return;
  // The collapsed clip exposes only 10% of the element. A 12% threshold
  // cannot be reached until it opens, so reveal on first intersection.
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.remove('pending');
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  }), {threshold: 0});
  root.querySelectorAll('.cut-reveal').forEach(node => { node.classList.add('pending'); observer.observe(node); });
  scope.own(() => observer.disconnect());
}
