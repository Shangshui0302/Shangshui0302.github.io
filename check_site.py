"""Validate generated navigation, content relationships and public-output boundaries.

Run after build_site.py (and optionally build_demos.py). Uses only the standard library.
"""
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
import json
import re
import argparse
from hashlib import sha256
from site_builder.release import check_release_output
from site_builder.urls import load_config, SiteURLs
from site_builder.article_translation import apply_translation
from site_builder.i18n import canonical_route

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', action='store_true', help='Reject preview origins and non-release output')
parser.add_argument('--site-url', help='Use the same deployment URL as the build (or SITE_URL)')
args = parser.parse_args()
config = load_config(ROOT, args.site_url)
urls = SiteURLs(config['site_url'])
if args.release:
    check_release_output(OUT, config)
manifest = json.loads((ROOT / 'public-content/manifest.json').read_text())
taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
posts = [json.loads((ROOT / 'public-content/writing' / f'{slug}.json').read_text()) for slug in manifest['writing']]
topics = [json.loads((ROOT / 'public-content/topics' / f'{slug}.json').read_text()) for slug in manifest['topics']]


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids, self.links, self.rows, self.h1 = [], [], [], 0
        self.nested_link, self.inside_link = False, False
        self.language = None
        self.language_links, self.alternates = {}, {}
        self.canonical = None
        self.content_hash = None
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-content-hash' in attrs:
            self.content_hash = attrs['data-content-hash']
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag == 'a' and 'data-language' in attrs:
            self.language_links[attrs['data-language']] = attrs.get('href')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')
        if tag == 'link' and attrs.get('rel') == 'alternate' and 'hreflang' in attrs:
            self.alternates[attrs['hreflang']] = attrs.get('href')
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a':
            self.nested_link |= self.inside_link
            self.inside_link = True
        if 'writing-row' in attrs.get('class', '').split():
            self.rows.append(attrs)
        for key in ('href', 'src', 'action', 'poster', 'data-search-index'):
            if key in attrs:
                self.links.append((tag, key, attrs[key], attrs))

    def handle_endtag(self, tag):
        if tag == 'a':
            self.inside_link = False


pages = {path.resolve(): Page(path.read_text()) for path in OUT.rglob('*.html')}
assert pages, 'Build the site before checking it'
errors, references = [], 0
for path, page in pages.items():
    route = str(path.relative_to(OUT))
    if not route.startswith('demos/'):
        english = route.startswith('en/')
        logical = route[3:] if english else route
        logical = '/' + logical.removesuffix('index.html')
        zh, en = urls.mount(logical), urls.mount('/en' + logical)
        origin = config['site_url'][:-len(urls.base_path)] if urls.base_path else config['site_url']
        assert page.language == ('en' if english else 'zh-CN'), f'Wrong document language: {route}'
        assert page.language_links == {'zh-CN': zh, 'en': en}, f'Wrong language counterparts: {route}'
        canonical_logical = canonical_route(logical)
        meta_zh, meta_en = urls.mount(canonical_logical), urls.mount('/en' + canonical_logical)
        assert page.canonical == origin + (meta_en if english else meta_zh), f'Wrong canonical: {route}'
        assert page.alternates == {'zh-CN': origin + meta_zh, 'en': origin + meta_en, 'x-default': origin + meta_zh}, f'Wrong language alternates: {route}'
    if len(page.ids) != len(set(page.ids)):
        errors.append(f'Duplicate id: {route}')
    if page.nested_link:
        errors.append(f'Nested link: {route}')
    if not route.startswith('demos/') and page.h1 != 1:
        errors.append(f'Expected one h1: {route}')
    for tag, key, value, attrs in page.links:
        url = urlsplit(value)
        if url.scheme or url.netloc:
            if url.scheme in ('http', 'https') and (key == 'src' or tag == 'link' and attrs.get('rel') == 'stylesheet'):
                errors.append(f'Remote asset: {route}')
            if url.scheme in ('javascript', 'file'):
                errors.append(f'Unsafe link scheme: {route}')
            continue
        if route.startswith('en/') and tag in ('a', 'form') and key in ('href', 'action') and url.path.startswith('/') and attrs.get('data-language') != 'zh-CN':
            local_route = '/' + urls.local_path(url.path)
            if local_route == '/' or re.match(r'^/(?:work|writing|journal|topics|index)(?:/|$)', local_route):
                errors.append(f'English link leaves its locale: {value}: {route}')
        references += 1
        target = (OUT / urls.local_path(url.path) if url.path.startswith('/') else path.parent / url.path).resolve() if url.path else path
        if target.is_dir():
            target /= 'index.html'
        if not target.exists():
            errors.append(f'Missing {value}: {route}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'Missing anchor {value}: {route}')

# Every Chinese document has a separately addressable English counterpart.
for path in list(pages):
    route = path.relative_to(OUT)
    if route.parts[0] not in ('en', 'demos'):
        assert (OUT / 'en' / route).resolve() in pages, f'Missing English route: {route}'

for topic in topics:
    assert OUT.joinpath('writing/topics', topic['slug'], 'index.html').is_file()

# Refactors must keep native module imports and bundled stylesheet assets resolvable.
for path in (OUT / 'assets').rglob('*'):
    if path.suffix == '.js':
        refs = re.findall(r"(?:from\s+|import\s*\()['\"]([^'\"]+)", path.read_text())
    elif path.suffix == '.css':
        refs = [match[1] for match in re.findall(r"url\((['\"]?)([^'\"\)]+)\1\)", path.read_text())]
    else:
        continue
    for ref in refs:
        if urlsplit(ref).scheme:
            continue
        target = OUT / urls.local_path(ref) if ref.startswith('/') else path.parent / urlsplit(ref).path
        assert target.resolve().is_file(), f'Missing asset import: {path.name} -> {ref}'
for path in OUT.rglob('index.html'):
    if '/demos/' not in str(path):
        assert re.findall(r'data-nav="([^" ]+)"', path.read_text()) == ['home', 'work', 'writing', 'index']

for post in posts:
    for prefix in ('writing', 'journal'):
        assert OUT.joinpath(prefix, post['slug'], 'index.html').is_file()
        assert pages[OUT.joinpath(prefix, post['slug'], 'index.html').resolve()].content_hash == sha256(post['body'].encode()).hexdigest(), f'Stale Chinese article output: {post["slug"]}'
    headings = [(anchor, unescape(label)) for anchor, label in re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', post['body'])]
    assert headings == [tuple(pair) for pair in post['sections']], f'Article outline mismatch: {post["slug"]}'

for key in taxonomy['categories']:
    expected = sum(post['category_id'] == key for post in posts)
    if expected:
        page = pages[(OUT / 'writing/categories' / key / 'index.html').resolve()]
        assert len(page.rows) == expected and all(row['data-category'] == key for row in page.rows)
for key in taxonomy['tags']:
    expected = sum(key in post['tags'] for post in posts)
    if expected:
        page = pages[(OUT / 'writing/tags' / key / 'index.html').resolve()]
        assert len(page.rows) == expected and all(key in row['data-tags'].split() for row in page.rows)
directory = pages[(OUT / 'writing/index.html').resolve()]
assert len(directory.rows) == len(posts)
for post, row in zip(posts, directory.rows):
    assert set(row['data-topics'].split()) == {topic['slug'] for topic in topics if post['slug'] in topic['articles']}

feed_root = ElementTree.parse(OUT / 'feed.xml')
origin = (config.get('site_url') or 'http://127.0.0.1:4173').rstrip('/')
assert feed_root.findtext('channel/link') == origin + '/writing/', 'RSS channel origin mismatch'
feed = feed_root.findall('channel/item')
assert len(feed) == len(posts)
for post, item in zip(posts, feed):
    for field in ('link', 'guid'):
        assert item.findtext(field) == f'{origin}/writing/{post["slug"]}/', f'RSS {field} mismatch: {post["slug"]}'
    assert [node.text for node in item.findall('category')] == [taxonomy['categories'][post['category_id']]['label'], *[taxonomy['tags'][tag] for tag in post['tags']]]

# English subscribers receive translated titles, summaries, taxonomy and stable /en/ links.
en_feed_root = ElementTree.parse(OUT / 'en/feed.xml')
assert en_feed_root.findtext('channel/language') == 'en'
assert en_feed_root.findtext('channel/link') == origin + '/en/writing/'
en_feed = en_feed_root.findall('channel/item')
assert len(en_feed) == len(posts)
en_catalog = json.loads((ROOT / 'public-content/translations/en/catalog.json').read_text())
for post, item in zip(posts, en_feed):
    for field in ('link', 'guid'):
        assert item.findtext(field) == f'{origin}/en/writing/{post["slug"]}/', f'English RSS {field} mismatch'
    assert item.findtext('title') == en_catalog['writing'][post['slug']]['title']
    assert item.findtext('description') == en_catalog['writing'][post['slug']]['deck']
    assert [node.text for node in item.findall('category')] == [en_catalog['taxonomy']['categories'][post['category_id']]['label'], *[en_catalog['taxonomy']['tags'][tag] for tag in post['tags']]]

# The directory shell stays small enough for the application's page cache.
search_html = (OUT / 'index/index.html').read_text()
assert len(search_html.encode('utf-16-le')) <= 800_000, 'Search HTML exceeds the page cache budget'
assert 'data-search=' not in search_html, 'Full-text data must stay outside the page HTML'
index_path = re.search(r'data-search-index="([^"]+)"', search_html)[1]
records = json.loads((OUT / urls.local_path(index_path)).read_text())
expected_urls = {f'/work/{slug}/' for slug in manifest['work']} | {f'/writing/{slug}/' for slug in manifest['writing']} | {f'/writing/topics/{slug}/' for slug in manifest['topics']}
expected_urls = {urls.mount(value) for value in expected_urls}
assert len(records) == len(expected_urls) and {record['url'] for record in records} == expected_urls, 'Search index coverage mismatch'
assert all(isinstance(record['text'], str) and record['text'] for record in records)

en_search_html = (OUT / 'en/index/index.html').read_text()
assert len(en_search_html.encode('utf-16-le')) <= 800_000, 'English search HTML exceeds cache budget'
en_index_path = re.search(r'data-search-index="([^"]+)"', en_search_html)[1]
en_records = json.loads((OUT / urls.local_path(en_index_path)).read_text())
en_expected = {urls.mount('/en/' + urls.local_path(value)) for value in expected_urls}
assert len(en_records) == len(en_expected) and {record['url'] for record in en_records} == en_expected, 'English search coverage mismatch'
assert en_index_path != index_path, 'Language search indexes must be independently versioned'

translated_count = 0
for post in posts:
    translation_path = ROOT / 'public-content/translations/en/articles' / (post['slug'] + '.json')
    if translation_path.exists():
        translated = apply_translation(post, json.loads(translation_path.read_text()))
        assert re.findall(r'<pre>[\s\S]*?</pre>', translated['body']) == re.findall(r'<pre>[\s\S]*?</pre>', post['body']), f'Changed code blocks: {post["slug"]}'
        assert re.findall(r'<code\b[^>]*>[\s\S]*?</code>', translated['body']) == re.findall(r'<code\b[^>]*>[\s\S]*?</code>', post['body']), f'Changed inline code: {post["slug"]}'
        assert re.findall(r'(?:href|src)="[^"]*"', translated['body']) == re.findall(r'(?:href|src)="[^"]*"', post['body']), f'Changed content links: {post["slug"]}'
        for prefix in ('writing', 'journal'):
            rendered = pages[OUT.joinpath('en', prefix, post['slug'], 'index.html').resolve()]
            assert rendered.content_hash == sha256(translated['body'].encode()).hexdigest(), f'Stale English article output: {post["slug"]}'
            rendered_html = OUT.joinpath('en', prefix, post['slug'], 'index.html').read_text()
            assert re.findall(r'<code\b[^>]*>[\s\S]*?</code>', rendered_html) == re.findall(r'<code\b[^>]*>[\s\S]*?</code>', post['body']), f'Changed rendered code: {post["slug"]}'
        translated_count += 1
if args.release:
    assert translated_count == len(posts), 'Release requires every English article body'


def json_text(value):
    """Inspect decoded strings so JSON quote escapes cannot become path characters."""
    if isinstance(value, dict):
        return '\n'.join(json_text(item) for pair in value.items() for item in pair)
    if isinstance(value, list):
        return '\n'.join(json_text(item) for item in value)
    return value if isinstance(value, str) else ''


for path in OUT.rglob('*'):
    if path.suffix in ('.html', '.css', '.js', '.json', '.xml', '.svg'):
        text = path.read_text()
        if path.suffix == '.json':
            text = json_text(json.loads(text))
        # Public source URLs may contain repository paths named home/; inspect local data separately.
        local_text = re.sub(r'https?://[^\s<>"\']+', '', text)
        # Reviewed generic examples retain absolute paths where ~ would change code semantics.
        home_accounts = re.findall(r'(?<![\w.~])/(?:home|Users)/([^/:\s<>&"\']+)', local_text)
        if any(account not in {'user', 'alice', 'bob', 'example', '用户', '$USER'} for account in home_accounts) or re.search(r'MyVault|github_pat_|ghp_[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|\[\[02_Academic', local_text):
            errors.append(f'Private-source pattern: {path.relative_to(OUT)}')
        # Match a real home path, not words such as ssh-agent on an 'agent' runner.
        if Path.home().name not in ('root', 'user') and str(Path.home()) + '/' in local_text:
            errors.append(f'Local account name: {path.relative_to(OUT)}')

report = {'pages': len(pages), 'local_references': references, 'articles': len(posts), 'translated_articles': translated_count, 'topics': len(topics), 'categories': len({post['category_id'] for post in posts}), 'tags': len({tag for post in posts for tag in post['tags']}), 'errors': errors}
print(json.dumps(report, ensure_ascii=False))
assert not errors, '\n'.join(errors)

