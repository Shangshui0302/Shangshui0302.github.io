"""Mount-path regressions, with no third-party test dependencies."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from site_builder.urls import SiteURLs, load_config, normalize_site_url
from site_builder.release import release_origin
from site_builder.assets import bundle_styles
from site_builder.search import write_search_index
from site_builder.feed import render_feed

ROOT = Path(__file__).resolve().parents[1]


class URLTests(unittest.TestCase):
    def test_config_precedence_without_mutating_saved_target(self):
        saved = (ROOT / 'site_config.json').read_text()
        with patch.dict('os.environ', {'SITE_URL': 'https://owner.github.io/offset/'}):
            self.assertEqual(load_config(ROOT)['site_url'], 'https://owner.github.io/offset')
            self.assertEqual(load_config(ROOT, 'https://site.org/')['site_url'], 'https://site.org')
        self.assertEqual((ROOT / 'site_config.json').read_text(), saved)

    def test_mount_and_inverse_are_boundary_aware(self):
        for base in ['', '/offset', '/nested/site']:
            urls = SiteURLs('https://owner.github.io' + base + '/')
            self.assertEqual(urls.base_path, base)
            for route in ['/', '/work/test/', '/assets/site.css', '/index/?q=x#main']:
                mounted = urls.mount(route)
                self.assertEqual(mounted, base + route)
                self.assertEqual(urls.mount(mounted), mounted)
                self.assertEqual(urls.local_path(mounted), route.split('?')[0].lstrip('/'))
            for value in ['#main', 'relative.js', 'https://external.org/', '//cdn.org/a', 'data:image/svg+xml,a']:
                self.assertEqual(urls.mount(value), value)
        urls = SiteURLs('https://owner.github.io/offset')
        self.assertEqual(urls.mount('/offset-other/'), '/offset/offset-other/')
        with self.assertRaises(ValueError):
            urls.local_path('/offset-other/')

    def test_url_validation_allows_release_subpaths(self):
        self.assertEqual(release_origin({'site_url': 'https://owner.github.io/offset/'}), 'https://owner.github.io/offset')
        for value in ['https://site.org/a/../b', 'https://site.org//a', 'https://site.org/a%2fb',
                      'https://site.org/a b', 'https://site.org/offset?x=y', 'https://site.org/#x',
                      'https://user:pass@site.org', 'https://site.org/\\evil']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_site_url(value)

    def test_html_rewrite_preserves_content_and_external_urls(self):
        source = '''<!doctype html><a href="/work/test/?a=1&amp;b=2#main">Work</a>
<script>const example = '<a href="/work/">';</script>
<pre>&lt;a href="/work/"&gt;</pre><!-- <a href="/work/"> -->
<a href="//external.org/">External</a><img src='/assets/a.svg'/>
<form action=/index/ data-search-index="/offset/assets/search.json"></form>'''
        urls = SiteURLs('https://owner.github.io/offset')
        result = urls.html(source)
        self.assertIn('href="/offset/work/test/?a=1&amp;b=2#main"', result)
        self.assertIn('src="/offset/assets/a.svg"', result)
        self.assertIn('action="/offset/index/"', result)
        for line in source.splitlines()[1:3]:
            self.assertIn(line, result)
        self.assertIn('href="//external.org/"', result)
        self.assertNotIn('/offset/offset/', result)
        self.assertEqual(urls.html(result), result)
        self.assertEqual(SiteURLs('https://site.org').html(source), source)

    def test_css_search_and_feed_share_the_mount(self):
        posts = [{'slug': 'test', 'title': 'Test', 'deck': 'Deck', 'category_id': 'systems', 'tags': []}]
        taxonomy = {'categories': {'systems': {'label': 'Systems'}}, 'tags': {}}
        for base in ['', '/offset']:
            site_url = 'https://owner.github.io' + base
            urls = SiteURLs(site_url)
            css = bundle_styles(ROOT, urls)
            self.assertIn(f'url("{base}/assets/fonts/', css)
            with tempfile.TemporaryDirectory() as temp:
                output = Path(temp)
                index = write_search_index(output, [], posts, [], taxonomy, urls)
                data = json.loads((output / urls.local_path(index)).read_text())
                self.assertEqual(data[0]['url'], base + '/writing/test/')
            config = {'site_url': site_url, 'site_name': 'Test', 'wordmark': 'TEST', 'description': 'Test'}
            feed = render_feed(config, posts, taxonomy)
            self.assertEqual(feed.findtext('channel/link'), site_url + '/writing/')
            for field in ['link', 'guid']:
                self.assertEqual(feed.findtext('channel/item/' + field), site_url + '/writing/test/')
