import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {languageURL, initLanguage} from '../assets/js/core/language.js';

const origin = 'https://owner.github.io';
test('language links retain route, filters and anchors at both deployment mounts', () => {
  for (const base of ['', '/offset']) {
    for (const route of ['/', '/writing/article/', '/journal/article/', '/writing/topics/linux/', '/index/']) {
      const value = `${origin}${base}${route}?q=services&tag=nix#example`;
      const english = languageURL(value, 'en', base);
      assert.equal(english.pathname, `${base}/en${route}`);
      assert.equal(english.search, '?q=services&tag=nix');
      assert.equal(english.hash, '#example');
      assert.equal(languageURL(english.href, 'en', base).href, english.href);
      assert.equal(languageURL(english.href, 'zh-CN', base).href, value);
    }
  }
  assert.equal(languageURL(`${origin}/another/`, 'en', '/offset').pathname, '/another/');
});

test('language preference selects the landing page without overriding deep links or history', () => {
  const source = readFileSync(new URL('../assets/js/core/language-bootstrap.js', import.meta.url), 'utf8');
  const run = (pathname, preference='en', type='navigate', throws=false) => {
    const redirects=[];
    vm.runInNewContext(source, {
      document: {documentElement: {dataset: {basePath:'/offset'}}},
      performance: {getEntriesByType: () => [{type}]},
      localStorage: {getItem: () => {if(throws) throw new Error('Unavailable'); return preference;}},
      location: {pathname, search:'?q=git', hash:'#selected-work', replace: value => redirects.push(value)},
    });
    return redirects;
  };
  assert.deepEqual(run('/offset/'), ['/offset/en/?q=git#selected-work']);
  for (const pathname of ['/offset/en/', '/offset/writing/article/', '/']) assert.deepEqual(run(pathname), []);
  assert.deepEqual(run('/offset/', 'zh-CN'), []);
  assert.deepEqual(run('/offset/', 'en', 'back_forward'), []);
  assert.deepEqual(run('/offset/', 'en', 'navigate', true), []);
});

test('language picker updates with routed history and survives blocked storage', () => {
  const globalBefore = Object.fromEntries(['document','location','localStorage','addEventListener'].map(k => [k,globalThis[k]]));
  try {
    const handlers={}, clicks={}, saved=[];
    const links = ['zh-CN','en'].map(language=>({dataset:{language},addEventListener:(name,fn)=>clicks[language]=fn}));
    globalThis.document={documentElement:{lang:'zh-CN',dataset:{basePath:''}},querySelectorAll:()=>links};
    globalThis.location={href:`${origin}/writing/?tag=nix#main`};
    globalThis.localStorage={setItem:(key,value)=>saved.push([key,value])};
    globalThis.addEventListener=(name,handler)=>handlers[name]=handler;
    initLanguage();
    assert.equal(links[1].href,`${origin}/en/writing/?tag=nix#main`);
    let prevented=false;
    clicks['zh-CN']({button:0,preventDefault:()=>prevented=true});
    assert.equal(prevented,true);
    assert.deepEqual(saved,[['offset-language','zh-CN']]);
    clicks.en({button:0,ctrlKey:true});
    assert.equal(saved.length,1);
    location.href=`${origin}/work/shell-switcher/#source`;
    handlers['offset:url-change']();
    assert.equal(links[1].href,`${origin}/en/work/shell-switcher/#source`);
    globalThis.localStorage={setItem:()=>{throw new Error('Unavailable')}};
    assert.doesNotThrow(()=>clicks.en({button:0}));
  } finally {
    for(const [key,value] of Object.entries(globalBefore)) value===undefined ? delete globalThis[key] : globalThis[key]=value;
  }
});
