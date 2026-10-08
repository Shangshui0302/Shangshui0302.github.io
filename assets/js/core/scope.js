/* One owner for each mounted page's listeners, observers, frames and timers. */
export function createScope() {
  const controller = new AbortController();
  const cleanups = [];
  const frames = new Set();
  const timers = new Set();
  return {
    get disposed() { return controller.signal.aborted; },
    on(target, event, callback, options = {}) {
      target?.addEventListener(event, callback, { ...options, signal: controller.signal });
    },
    frame(callback) {
      const id = requestAnimationFrame(time => {
        frames.delete(id);
        if (!controller.signal.aborted) callback(time);
      });
      frames.add(id);
      return id;
    },
    timeout(callback, delay) {
      const id = setTimeout(() => {
        timers.delete(id);
        if (!controller.signal.aborted) callback();
      }, delay);
      timers.add(id);
      return id;
    },
    own(cleanup) { cleanups.push(cleanup); },
    dispose() {
      controller.abort();
      frames.forEach(cancelAnimationFrame);
      timers.forEach(clearTimeout);
      cleanups.reverse().forEach(cleanup => cleanup());
    },
  };
}
