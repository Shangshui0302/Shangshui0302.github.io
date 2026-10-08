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

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'
manifest = json.loads((ROOT / 'public-content/manifest.json').read_text())
taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
posts = [json.loads((ROOT / 'public-content/writing' / f'{slug}.json').read_text()) for slug in manifest['writing']]
topics = [json.loads((ROOT / 'public-content/topics' / f'{slug}.json').read_text()) for slug in manifest['topics']]


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids, self.links, self.rows, self.h1 = [], [], [], 0
        self.nested_link, self.inside_link = False, False
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a':
            self.nested_link |= self.inside_link
            self.inside_link = True
        if 'writing-row' in attrs.get('class', '').split():
            self.rows.append(attrs)
        for key in ('href', 'src'):
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
        references += 1
        target = (OUT / url.path.lstrip('/') if url.path.startswith('/') else path.parent / url.path).resolve() if url.path else path
        if target.is_dir():
            target /= 'index.html'
        if not target.exists():
            errors.append(f'Missing {value}: {route}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'Missing anchor {value}: {route}')

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
        target = OUT / ref.lstrip('/') if ref.startswith('/') else path.parent / ref
        assert target.resolve().is_file(), f'Missing asset import: {path.name} -> {ref}'
for path in OUT.rglob('index.html'):
    if '/demos/' not in str(path):
        assert re.findall(r'data-nav="([^" ]+)"', path.read_text()) == ['home', 'work', 'writing', 'index']

for post in posts:
    for prefix in ('writing', 'journal'):
        assert OUT.joinpath(prefix, post['slug'], 'index.html').is_file()
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

feed = ElementTree.parse(OUT / 'feed.xml').findall('channel/item')
assert len(feed) == len(posts)
for post, item in zip(posts, feed):
    assert [node.text for node in item.findall('category')] == [taxonomy['categories'][post['category_id']]['label'], *[taxonomy['tags'][tag] for tag in post['tags']]]

for path in OUT.rglob('*'):
    if path.suffix in ('.html', '.css', '.js', '.json', '.xml', '.svg'):
        text = path.read_text()
        # Public source URLs may contain repository paths named home/; inspect local data separately.
        local_text = re.sub(r'https?://[^\s<>"\']+', '', text)
        # Reviewed generic examples retain absolute paths where ~ would change code semantics.
        home_accounts = re.findall(r'(?<![\w.~])/(?:home|Users)/([^/:\s<>&"\']+)', local_text)
        if any(account not in {'user', 'alice', 'bob', 'example', '用户', '$USER'} for account in home_accounts) or re.search(r'MyVault|github_pat_|ghp_[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|\[\[02_Academic', local_text):
            errors.append(f'Private-source pattern: {path.relative_to(OUT)}')
        if Path.home().name not in ('root', 'user') and Path.home().name in text:
            errors.append(f'Local account name: {path.relative_to(OUT)}')

report = {'pages': len(pages), 'local_references': references, 'articles': len(posts), 'topics': len(topics), 'categories': len({post['category_id'] for post in posts}), 'tags': len({tag for post in posts for tag in post['tags']}), 'errors': errors}
print(json.dumps(report, ensure_ascii=False))
assert not errors, '\n'.join(errors)
