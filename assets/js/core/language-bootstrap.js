/* The URL owns the page language. A saved choice only selects the root landing
   page; deep links and browser history always keep their explicit language. */
(() => {
  try {
    const base = document.documentElement.dataset.basePath || '';
    const entry = performance.getEntriesByType('navigation')[0];
    if (location.pathname === `${base}/` && entry?.type !== 'back_forward' &&
        localStorage.getItem('offset-language') === 'en') {
      document.documentElement.dataset.languageRedirect = 'true';
      location.replace(`${base}/en/${location.search}${location.hash}`);
    }
  } catch {
    delete document.documentElement.dataset.languageRedirect;
    /* Explicit links still work with unavailable storage or navigation. */
  }
})();
