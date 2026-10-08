import {reducedMotion} from '../core/motion.js';
import {enterPage} from './page-enter.js';

/* Capture the viewport, not a second DOM tree or a full-length main layer. */
export function createPageTransition() {
  let active, cancelEntrance = () => {};
  const cancel = () => {
    active?.skipTransition();
    active = undefined;
    cancelEntrance();
    cancelEntrance = () => {};
  };
  document.addEventListener('offset:motion-change', () => {
    if (reducedMotion()) cancel();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancel();
  });

  return {
    cancel,
    async run(commit, nextMain) {
      if (reducedMotion() || document.hidden) { commit(); return; }
      if (!document.startViewTransition) {
        commit();
        cancelEntrance = enterPage(nextMain);
        return;
      }
      const transition = document.startViewTransition(commit);
      active = transition;
      // A skipped/unsupported capture still commits the page. Only a failed
      // update callback is a navigation error; never commit the same page twice.
      transition.ready.catch(() => {});
      const release = () => { if (active === transition) active = undefined; };
      transition.finished.then(release, release);
      await transition.updateCallbackDone;
    },
  };
}
