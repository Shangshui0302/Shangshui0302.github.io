import {t} from '../core/language.js';
import {loadSearchIndex} from '../core/search-index.js';

export function initSearch(root, scope, {updateUrl}) {
  const form = root.querySelector('#search');
  if (!form) return () => {};
  const input = root.querySelector('#search-input'), kind = root.querySelector('#kind');
  const count = root.querySelector('.count'), notice = root.querySelector('#search-notice');
  const retry = root.querySelector('.retry-search'), empty = root.querySelector('#search-empty');
  let index, loading = false, failed = false;
  const rows = [...root.querySelectorAll('#search-results .result-row')].map(row => ({
    row, kind: row.dataset.kind, url: row.getAttribute('href'),
  }));
  const apply = () => {
    if (scope.disposed) return;
    const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const waiting = terms.length > 0 && !index;
    notice.hidden = !waiting;
    notice.querySelector('span').textContent = failed ? t('全文搜索暂时不可用，可继续浏览目录。', 'Full-text search is unavailable. You can still browse the index.') : t('正在准备全文搜索…', 'Preparing full-text search…');
    retry.hidden = !failed;
    if (waiting && !loading && !failed) {
      loading = true;
      loadSearchIndex(form.dataset.searchIndex).then(result => {
        if (rows.some(item => !result.has(item.url))) throw new Error('Incomplete search index');
        index = result;
      }).catch(() => { failed = true; }).finally(() => { loading = false; apply(); });
    }
    let visible = 0;
    rows.forEach(item => {
      const hidden = kind.value !== 'all' && item.kind !== kind.value || !!index && !terms.every(term => index.get(item.url).includes(term));
      if (item.row.hidden !== hidden) item.row.hidden = hidden;
      if (!hidden) visible++;
    });
    count.textContent = waiting
      ? t(`${visible} 项目录内容 · ${failed ? '搜索未完成' : '准备搜索中'}`, `${visible} index entries · ${failed ? 'search unavailable' : 'preparing search'}`)
      : t(`${visible} 项内容`, `${visible} ${visible === 1 ? 'result' : 'results'}`);
    empty.hidden = waiting || visible > 0;
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
  scope.on(retry, 'click', () => { failed = false; apply(); });
  scope.on(root.querySelector('.reset-search'), 'click', () => { input.value = ''; kind.value = 'all'; filter(); root.dispatchEvent(new Event('filters:restore')); input.focus(); });
  restore();
  return restore;
}
