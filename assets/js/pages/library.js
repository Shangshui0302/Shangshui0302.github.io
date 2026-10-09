import {t} from '../core/language.js';
/* URL-owned directory state; the router is the only history writer. */
export function initLibrary(root, scope, {updateUrl}) {
  const category = root.querySelector('#article-category');
  const tag = root.querySelector('#article-tag');
  const topic = root.querySelector('#article-topic');
  if (!category || !tag || !topic) return () => {};
  const fields = [['category', category], ['tag', tag], ['topic', topic]];
  const rows = [...root.querySelectorAll('#writing-list .writing-row')];
  const apply = () => {
    let visible = 0;
    rows.forEach(row => {
      row.hidden = category.value !== 'all' && row.dataset.category !== category.value
        || tag.value !== 'all' && !row.dataset.tags.split(' ').includes(tag.value)
        || topic.value !== 'all' && !row.dataset.topics.split(' ').includes(topic.value);
      if (!row.hidden) visible++;
    });
    root.querySelector('#writing-count').textContent = t(`${visible} / ${rows.length} 篇文章`, `${visible} / ${rows.length} articles`);
    root.querySelector('#writing-empty').hidden = visible > 0;
  };
  const restore = () => {
    const params = new URLSearchParams(location.search);
    fields.forEach(([key, select]) => {
      const value = params.get(key) || 'all';
      select.value = [...select.options].some(option => option.value === value) ? value : 'all';
    });
    apply();
    root.dispatchEvent(new Event('filters:restore'));
  };
  const filter = () => {
    apply();
    const url = new URL(location.href);
    fields.forEach(([key, select]) => select.value === 'all' ? url.searchParams.delete(key) : url.searchParams.set(key, select.value));
    updateUrl(url);
  };
  fields.forEach(([, select]) => scope.on(select, 'change', filter));
  const reset = () => {
    fields.forEach(([, select]) => select.value = 'all');
    filter(); root.dispatchEvent(new Event('filters:restore'));
    root.querySelector('#article-category-trigger')?.focus();
  };
  scope.on(root.querySelector('#reset-writing'), 'click', reset);
  scope.on(root.querySelector('#empty-reset-writing'), 'click', reset);
  restore();
  return restore;
}
