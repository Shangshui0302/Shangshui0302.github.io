export function initReveals(root, scope) {
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.remove('pending');
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  }), {threshold: .12});
  root.querySelectorAll('.cut-reveal').forEach(node => { node.classList.add('pending'); observer.observe(node); });
  scope.own(() => observer.disconnect());
}
