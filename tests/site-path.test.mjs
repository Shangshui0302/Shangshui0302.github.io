import assert from 'node:assert/strict';
import {test} from 'node:test';
import {isSitePage} from '../assets/js/core/site-path.js';

test('router stays inside its deployment prefix on the same origin', () => {
  const origin = 'https://owner.github.io';
  for (const base of ['', '/offset']) {
    for (const route of ['/', '/work/project/', '/writing/article/?q=test#section', '/index/']) {
      assert.equal(isSitePage(new URL(base + route, origin), origin, base), true);
    }
    for (const route of ['/demos/', '/demos/cut/', '/feed.xml', '/assets/site.css']) {
      assert.equal(isSitePage(new URL(base + route, origin), origin, base), false);
    }
    assert.equal(isSitePage(new URL(`https://other.github.io${base}/`), origin, base), false);
  }
  for (const path of ['/', '/other/', '/offset-other/', '/offset', '/offset/../other/']) {
    assert.equal(isSitePage(new URL(path, origin), origin, '/offset'), false);
  }
});
