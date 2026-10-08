export function initSearch(root, scope, {updateUrl}) {
  const form = root.querySelector('#search');
  if (!form) return () => {};
  const input = root.querySelector('#search-input'), kind = root.querySelector('#kind');
  // Normalize full article text once per mount, not on every keystroke.
  const rows = [...root.querySelectorAll('#search-results .result-row')].map(row => ({
    row, kind: row.dataset.kind, text: row.dataset.search.toLocaleLowerCase(),
  }));
  const apply = () => {
    const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach(item => {
      const hidden = kind.value !== 'all' && item.kind !== kind.value || !terms.every(term => item.text.includes(term));
      if (item.row.hidden !== hidden) item.row.hidden = hidden;
      if (!hidden) visible++;
    });
    root.querySelector('.count').textContent = `${visible} 项内容`;
    root.querySelector('#search-empty').hidden = visible > 0;
  };
  const restore = () => {
    const params = new URLSearchParams(location.search);
    input.value = params.get('q') || '';
    kind.value = ['work', 'writing', 'topics'].includes(params.get('kind')) ? params.get('kind') : 'all';
    apply(); root.dispatchEvent(new Event('filters:restore'));
  };
  const filter = () => {
    apply();
    const url = new URL(location.href);
    input.value.trim() ? url.searchParams.set('q', input.value.trim()) : url.searchParams.delete('q');
    kind.value === 'all' ? url.searchParams.delete('kind') : url.searchParams.set('kind', kind.value);
    updateUrl(url, 'replace');
  };
  scope.on(input, 'input', filter);
  scope.on(kind, 'change', filter);
  scope.on(form, 'submit', e => { e.preventDefault(); filter(); });
  scope.on(root.querySelector('.reset-search'), 'click', () => { input.value = ''; kind.value = 'all'; filter(); root.dispatchEvent(new Event('filters:restore')); input.focus(); });
  restore();
  return restore;
}
