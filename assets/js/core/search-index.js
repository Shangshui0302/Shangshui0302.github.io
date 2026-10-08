/* Share one version across page mounts; failed loads can be retried. */
let currentUrl, pending;
export function loadSearchIndex(url) {
  if (currentUrl !== url || !pending) {
    currentUrl = url;
    const request = fetch(url, {headers: {Accept: 'application/json'}})
      .then(response => {
        if (!response.ok) throw new Error('Search index unavailable');
        return response.json();
      }).then(records => {
        if (!Array.isArray(records) || records.some(item => typeof item.url !== 'string' || typeof item.text !== 'string')) {
          throw new Error('Invalid search index');
        }
        return new Map(records.map(item => [item.url, item.text.toLocaleLowerCase()]));
      });
    pending = request;
    request.catch(() => { if (pending === request) pending = null; });
  }
  return pending;
}
