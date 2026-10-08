/* Cache only visited static documents; cap memory and let preview edits expire. */
export function createPageCache() {
  const entries = new Map();
  const maxBytes = 800_000, maxPages = 8, lifetime = 60_000;
  let bytes = 0;
  const remove = key => { bytes -= entries.get(key).size; entries.delete(key); };
  const put = (key, html) => {
    if (entries.has(key)) remove(key);
    const size = html.length * 2;
    if (size > maxBytes) return;
    entries.set(key, {html, size, expires: performance.now() + lifetime});
    bytes += size;
    while (entries.size > maxPages || bytes > maxBytes) remove(entries.keys().next().value);
  };
  return {
    put,
    async read(url, signal) {
      const key = url.pathname;
      const item = entries.get(key);
      if (item && item.expires > performance.now()) {
        entries.delete(key); entries.set(key, item);
        return item.html;
      }
      if (item) remove(key);
      const response = await fetch(url, {signal, headers: {Accept: 'text/html'}});
      if (!response.ok || !response.headers.get('content-type')?.includes('text/html')) throw new Error('Invalid page');
      const html = await response.text();
      // Never retain error pages or HTML outside the shared site shell.
      if (!html.includes('data-site-shell')) throw new Error('Missing site shell');
      put(key, html);
      return html;
    },
  };
}
