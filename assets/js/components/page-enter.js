import {reducedMotion} from '../core/motion.js';

/* Animate bounded, visible headings/controls instead of rasterizing a long main. */
export function enterPage(root) {
  if (reducedMotion()) return () => {};
  const animations = [];
  const candidates = root.querySelectorAll('.page-intro, .topic-hero-copy, .article-cover-copy, .case-hero-copy, .galaxy-center, .writing-filters');
  for (const node of candidates) {
    const rect = node.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top >= innerHeight || rect.height > innerHeight) continue;
    animations.push(node.animate(
      [{opacity: .65, transform: 'translateY(7px)'}, {opacity: 1, transform: 'none'}],
      {duration: 200, easing: 'cubic-bezier(.16,1,.3,1)'}));
  }
  return () => animations.forEach(animation => animation.cancel());
}
