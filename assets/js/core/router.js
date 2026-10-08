import { reducedMotion } from './motion.js';
import {createPageCache} from './page-cache.js';
import {enterPage} from '../components/page-enter.js';

/* Progressive navigation: static documents remain independently readable. */
export function createRouter(mountPage) {
  let current = new URL(location.href), page, request, sequence = 0, cancelEntrance = () => {};
  let scrollTimer = 0, navigating = false, failedURL;
  const root = document.documentElement;
  const notice = document.querySelector('.route-status');
  const error = document.querySelector('.route-error');
  history.scrollRestoration = 'manual';
  const cache = createPageCache();
  cache.put(current.pathname, document.documentElement.outerHTML);

  const remember = () => {
    if (location.href === current.href) history.replaceState({...history.state, offset: {x: scrollX, y: scrollY}}, '', current);
  };
  const writeURL = (url, mode) => {
    if (mode !== 'none' && url.href !== location.href) {
      history[mode === 'replace' ? 'replaceState' : 'pushState']({offset: {x: scrollX, y: scrollY}}, '', url);
    }
    current = new URL(url);
  };
  const focus = element => {
    if (!element) return;
    if (!element.matches('a,button,input,select,textarea,[tabindex]')) element.setAttribute('tabindex', '-1');
    element.focus({preventScroll: true});
  };
  const targetFor = hash => {
    try { return document.getElementById(decodeURIComponent(hash.slice(1))); } catch { return null; }
  };
  const position = (url, saved, changedPage) => {
    if (saved) window.scrollTo({left: saved.x, top: saved.y, behavior: 'instant'});
    else if (url.hash && targetFor(url.hash)) {
      const target = targetFor(url.hash);
      target.scrollIntoView({behavior: changedPage || reducedMotion() ? 'instant' : 'smooth'});
      focus(target);
    } else window.scrollTo({top: 0, left: 0, behavior: 'instant'});
    if (changedPage && !url.hash) focus(document.querySelector('#main h1') || document.querySelector('#main'));
  };
  const updateUrl = (value, mode = 'push') => {
    remember();
    writeURL(new URL(value, location.href), mode);
    remember();
  };

  async function navigate(value, {mode = 'push', saved} = {}) {
    const url = new URL(value, location.href);
    if (url.origin !== location.origin) return;
    const id = ++sequence;
    request?.abort();
    cancelEntrance();
    request = new AbortController();
    if (mode !== 'none') remember();
    error.hidden = true;
    if (url.pathname === current.pathname) {
      writeURL(url, mode);
      page.restore?.();
      position(url, saved, false);
      navigating = false;
      root.classList.remove('route-loading');
      return;
    }
    navigating = true;
    root.classList.add('route-loading');
    notice.textContent = '正在加载';
    try {
      const html = await cache.read(url, request.signal);
      if (id !== sequence) return;
      const incoming = new DOMParser().parseFromString(html, 'text/html');
      const nextMain = incoming.querySelector('#main');
      if (!nextMain || !incoming.querySelector('[data-site-shell]')) throw new Error('Missing site shell');
      if (id !== sequence) return;
      const commit = () => {
        if (id !== sequence) return;
        page.dispose();
        document.querySelector('#main').replaceWith(nextMain);
        document.title = incoming.title;
        document.querySelector('meta[name="description"]').content = incoming.querySelector('meta[name="description"]').content;
        document.body.className = incoming.body.className;
        document.body.dataset.section = incoming.body.dataset.section;
        document.querySelectorAll('[data-nav]').forEach(link => {
          if (link.dataset.nav === incoming.body.dataset.section) link.setAttribute('aria-current', 'page');
          else link.removeAttribute('aria-current');
        });
        writeURL(url, mode);
        page = mountPage(nextMain, {navigate, updateUrl});
        position(url, saved, true);
      };
      commit();
      cancelEntrance = enterPage(nextMain);
      if (id === sequence) { notice.textContent = document.title; remember(); }
    } catch (failure) {
      if (id !== sequence || failure.name === 'AbortError') return;
      failedURL = url.href;
      if (mode === 'none') history.replaceState({offset: {x: scrollX, y: scrollY}}, '', current);
      error.querySelector('[data-route-open]').href = url.href;
      error.hidden = false;
      notice.textContent = '';
    } finally {
      if (id === sequence) { navigating = false; root.classList.remove('route-loading'); }
    }
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.hasAttribute('download') || link.hasAttribute('data-native') || link.target && link.target !== '_self') return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !url.pathname.endsWith('/') || url.pathname.startsWith('/demos/')) return;
    event.preventDefault();
    navigate(url);
  });
  addEventListener('popstate', event => navigate(location.href, {mode: 'none', saved: event.state?.offset}));
  addEventListener('scroll', () => {
    clearTimeout(scrollTimer);
    if (!navigating) scrollTimer = setTimeout(remember, 100);
  }, {passive: true});
  addEventListener('pagehide', remember);
  error.querySelector('[data-route-retry]').addEventListener('click', () => navigate(failedURL));
  error.querySelector('[data-route-dismiss]').addEventListener('click', () => { error.hidden = true; });
  page = mountPage(document.querySelector('#main'), {navigate, updateUrl});
  // Reload keeps the browser's initial position; subsequent moves are owned here.
  remember();
  return {navigate, updateUrl};
}
