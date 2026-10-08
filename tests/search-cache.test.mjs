import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {test} from 'node:test';
import {loadSearchIndex} from '../assets/js/core/search-index.js';
import {createPageCache} from '../assets/js/core/page-cache.js';

test('full text loads once across concurrent and later mounts; failures retry', async t => {
  let requests = 0;
  t.mock.method(globalThis, 'fetch', async () => {
    requests++;
    return {ok: requests !== 2, json: async () => [{url: '/writing/test/', text: 'FULL text && 正文'}]};
  });
  const [first, concurrent] = await Promise.all([loadSearchIndex('/index-a.json'), loadSearchIndex('/index-a.json')]);
  assert.equal(first, concurrent);
  assert.equal(await loadSearchIndex('/index-a.json'), first);
  assert.equal(requests, 1);
  assert.equal(first.get('/writing/test/'), 'full text && 正文');
  await assert.rejects(loadSearchIndex('/index-b.json'));
  assert.equal((await loadSearchIndex('/index-b.json')).size, 1);
  assert.equal(requests, 3);
});

test('built search directory fits and hits the page cache', async t => {
  const html = await readFile(new URL('../dist/index/index.html', import.meta.url), 'utf8');
  let requests = 0;
  t.mock.method(globalThis, 'fetch', async () => {
    requests++;
    return {ok: true, headers: {get: () => 'text/html'}, text: async () => html};
  });
  const cache = createPageCache(), url = new URL('https://offset-site.org/index/');
  const signal = new AbortController().signal;
  assert.equal(await cache.read(url, signal), html);
  assert.equal(await cache.read(url, signal), html);
  assert.equal(requests, 1);
});
