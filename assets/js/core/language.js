/* Small runtime messages only; page copy is translated at build time. */
export const isEnglish = () => document.documentElement.lang === 'en';
export const t = (zh, en) => isEnglish() ? en : zh;

export function languageURL(value, language, basePath = '') {
  const url = new URL(value);
  if (basePath && !url.pathname.startsWith(`${basePath}/`)) return url;
  let route = url.pathname.slice(basePath.length);
  if (route === '/en' || route.startsWith('/en/')) route = route.slice(3) || '/';
  url.pathname = basePath + (language === 'en' ? '/en' : '') + route;
  return url;
}

export function initLanguage() {
  const links = [...document.querySelectorAll('[data-language]')];
  const base = document.documentElement.dataset.basePath || '';
  const sync = () => links.forEach(link => {
    link.href = languageURL(location.href, link.dataset.language, base).href;
  });
  links.forEach(link => link.addEventListener('click', event => {
    // Modified clicks keep the preference in this tab unchanged.
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    try { localStorage.setItem('offset-language', link.dataset.language); } catch {}
    if (link.dataset.language === document.documentElement.lang) event.preventDefault();
  }));
  addEventListener('offset:url-change', sync);
  addEventListener('pageshow', sync);
  sync();
}
