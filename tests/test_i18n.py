import copy
import unittest
from site_builder.i18n import english_route, text_en, translate_html, canonical_route
from site_builder.templates.article import render_article
from site_builder.article_translation import extract_segments, source_digest, apply_translation

class LocalizationTests(unittest.TestCase):
    def test_page_routes_only(self):
        for route in ('/', '/work/project/', '/writing/article/?q=abc#section', '/journal/old/', '/topics/path/', '/index/'):
            self.assertEqual(english_route(route), '/en' + route)
        for route in ('/assets/site.css', '/feed.xml', '/en/work/', '#source', 'https://example.org/', '//example.org/', 'relative/'):
            self.assertEqual(english_route(route), route)

    def test_legacy_canonicals_use_primary_routes(self):
        self.assertEqual(canonical_route('/journal/article/'), '/writing/article/')
        self.assertEqual(canonical_route('/topics/'), '/writing/topics/')
        self.assertEqual(canonical_route('/topics/linux/'), '/writing/topics/linux/')
        self.assertEqual(canonical_route('/work/project/'), '/work/project/')

    def test_html_translation_preserves_code_and_original_content(self):
        html = '<h1>作品目录。</h1><a href="/work/" aria-label="结构段落链接">查看项目</a><pre><code>作品</code></pre><div lang="zh-CN" data-original-content>作品目录。</div><script>"作品"</script>\n'
        result = translate_html(html)
        self.assertIn('<h1>Projects.</h1>', result)
        self.assertIn('href="/en/work/"', result)
        self.assertIn('aria-label="Link to section: Structure"', result)
        self.assertIn('<pre><code>作品</code></pre>', result)
        self.assertIn('data-original-content>作品目录。</div>', result)
        self.assertIn('<script>"作品"</script>', result)
        self.assertTrue(result.endswith('\n'))
        self.assertFalse(result.endswith('\n\n'))
        self.assertEqual(text_en('  '), '  ')
        self.assertEqual(text_en('Podman Machine（macOS/Windows）'), 'Podman Machine(macOS/Windows)')
        self.assertEqual(text_en('ArchWiki：GNOME'), 'ArchWiki: GNOME')
        code_markup = '<pre><code><a href="/writing/example/">源码</a></code></pre>'
        self.assertEqual(translate_html(code_markup), code_markup)

    def test_translated_heading_quotes_are_safe_in_accessible_labels(self):
        post = {'slug':'sample', 'body':'<h2 id="first">Why "switch"?</h2><p>Example.</p>', 'sections':[['first','Why "switch"?']], 'refs':[], 'number':'01', 'category':'SYSTEMS', 'title':'Sample', 'deck':'A sample.', 'date':'2026-10-09', 'body_language':'en'}
        result = translate_html(render_article(post,[post],lambda _:''))
        self.assertIn('aria-label="Link to section: Why &quot;switch&quot;?"', result)

    def test_article_slots_are_lossless_and_fail_closed(self):
        post = {'slug':'sample', 'body':'<h2 id="first">第一节</h2><p>请保留 <code>echo 中文</code> 和 <a href="https://example.org/">来源</a>。</p><pre><code># 中文注释\necho x</code></pre>', 'sections':[['first','第一节']], 'refs':[['来源','https://example.org/']]}
        slots=extract_segments(post['body'])
        self.assertEqual(len(slots),2)
        record={'source_sha256':source_digest(post),'segments':['First section','Keep <code>echo 中文</code> and the <a href="https://example.org/">source</a>.'],'reference_labels':['Source']}
        translated=apply_translation(post,record)
        self.assertIn('<pre><code># 中文注释\necho x</code></pre>',translated['body'])
        self.assertEqual(translated['sections'],[('first','First section')])
        self.assertEqual(translated['refs'],[['Source','https://example.org/']])
        broken=copy.deepcopy(record);broken['segments'][1]=broken['segments'][1].replace('echo 中文','echo English')
        with self.assertRaises(ValueError):apply_translation(post,broken)
        broken=copy.deepcopy(record);broken['segments'].pop()
        with self.assertRaises(ValueError):apply_translation(post,broken)
        broken=copy.deepcopy(record);broken['source_sha256']='stale'
        with self.assertRaises(ValueError):apply_translation(post,broken)

if __name__ == '__main__': unittest.main()
