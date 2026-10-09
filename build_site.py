"""Build only allowlisted, curated content. Never reads a vault or live API."""
from site_builder.content import read_content, select_home_content, validate_case_studies
from site_builder.search import write_search_index
from site_builder.i18n import localized_content, translate_html, text_en, canonical_route
from html import escape
from site_builder.release import release_origin
from site_builder.urls import load_config, SiteURLs
import argparse
from site_builder.assets import bundle_styles
from pathlib import Path
from functools import partial
from site_builder.templates.layout import render_page
from site_builder.templates.home import render_home
from site_builder.templates.library import library_pages
from site_builder.templates.search import render_search
from site_builder.templates.case import render_case
from site_builder.templates.article import render_article
from site_builder.templates.visuals import visual
from site_builder.templates.taxonomy import validate_taxonomy, taxonomy_links, article_topics
from site_builder.templates.work import render_work_directory, related_work_links
from site_builder.templates.components import url
import json
import shutil
import re
from hashlib import sha256
from site_builder.feed import render_feed

ROOT = Path(__file__).parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', action='store_true', help='Require a public HTTPS origin before building')
parser.add_argument('--site-url', help='Override the deployment URL (or set SITE_URL)')
args = parser.parse_args()
CONFIG = load_config(ROOT, args.site_url)
urls = SiteURLs(CONFIG['site_url'])
# Version the module graph and stylesheet together so a deploy cannot mix old UI code
# with the new bilingual shell in a visitor’s browser cache.
asset_sources = sorted((ROOT / 'assets/js').rglob('*.js')) + sorted((ROOT / 'assets/css').rglob('*.css'))
CONFIG['asset_version'] = sha256(b''.join(path.read_bytes() for path in asset_sources)).hexdigest()[:16]
if args.release:
    CONFIG['site_url'] = release_origin(CONFIG)
MANIFEST = json.loads((ROOT / 'public-content/manifest.json').read_text())
OUT = ROOT / '.sites-runtime/section-build'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)
works = read_content(ROOT, MANIFEST, 'work')
posts = read_content(ROOT, MANIFEST, 'writing')
topics = read_content(ROOT, MANIFEST, 'topics')
taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
validate_taxonomy(taxonomy, posts, topics)
validate_case_studies(works)
home_config = json.loads((ROOT / 'public-content/home.json').read_text())


def render_locale(language, works, posts, topics, taxonomy):
    validate_taxonomy(taxonomy, posts, topics)
    validate_case_studies(works)
    english = language == 'en'
    config = {**CONFIG, 'language': language}
    if english:
        config['description'] = text_en(CONFIG['description'])
    def page(title, *args, **kwargs):
        return render_page(config, text_en(title) if english else title, *args, **kwargs)
    def write(route, content):
        logical = '/' + route.strip('/') + '/' if route else '/'
        zh, en = urls.mount(logical), urls.mount('/en' + logical)
        origin = CONFIG['site_url'][:-len(urls.base_path)] if urls.base_path else CONFIG['site_url']
        canonical_logical = canonical_route(logical)
        meta_zh, meta_en = urls.mount(canonical_logical), urls.mount('/en' + canonical_logical)
        canonical = meta_en if english else meta_zh
        alternates = f'<link rel="canonical" href="{escape(origin + canonical)}">' + ''.join(
            f'<link rel="alternate" hreflang="{lang}" href="{escape(origin + path)}">'
            for lang, path in [('zh-CN', meta_zh), ('en', meta_en), ('x-default', meta_zh)])
        content = content.replace('</head>', alternates + '</head>', 1)
        content = content.replace('href="LANGUAGE_ZH"', f'href="{zh}"').replace('href="LANGUAGE_EN"', f'href="{en}"')
        if english:
            content = translate_html(content)
        target = OUT / ('en' if english else '') / route.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(urls.html(content))

    home_selection = select_home_content(home_config, works, posts)
    work_by_slug = {item['slug']: item for item in works}
    post_by_slug = {post['slug']: post for post in posts}
    for item in works:
        assert set(item['related']) <= set(post_by_slug)
    for post in posts:
        assert set(post['related_work']) <= set(work_by_slug)
    write('', page('开源作品与技术文章', render_home(ROOT, works, home_selection, topics, taxonomy), 'home', stellar=True))
    write('work', page('作品目录', render_work_directory(works), 'work'))
    related_work = partial(related_work_links, work_by_slug=work_by_slug)
    for item in works:
        body = render_case(item, works, post_by_slug, visual)
        write('work/' + item['slug'], page(item['title'], body, 'work', item['summary'], is_case=True))
    for route, title, body, active, description in library_pages(posts, topics, taxonomy):
        write(route, page(title, body, active, description))
    for post in posts:
        topic_links, continuation = article_topics(post, topics, post_by_slug)
        article = render_article(post, posts, related_work, taxonomy_links(post, taxonomy), topic_links, continuation)
        for prefix in ('writing/', 'journal/'):
            write(prefix + post['slug'], page(post['title'], article, 'writing', post['deck'], True))
    index_url = write_search_index(OUT, works, posts, topics, taxonomy, urls, english=english)
    write('index', page('搜索', render_search(works, posts, topics, taxonomy, index_url), 'index'))
    feed_config = {**config, 'site_url': CONFIG['site_url'] + ('/en' if english else '')}
    render_feed(feed_config, posts, taxonomy).write(OUT / ('en' if english else '') / 'feed.xml', encoding='utf-8', xml_declaration=True)


render_locale('zh-CN', works, posts, topics, taxonomy)
render_locale('en', *localized_content(works, posts, topics, taxonomy, require_complete=args.release))

shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
(OUT/'assets/site.css').write_text(bundle_styles(ROOT, urls))
for script in (OUT / 'assets/js').rglob('*.js'):
    code = script.read_text()
    code = re.sub(r"((?:from\s+|import\s*\()['\"])([^'\"]+\.js)(['\"])",
                  lambda m: m[1] + m[2] + '?v=' + CONFIG['asset_version'] + m[3], code)
    script.write_text(code)
dest=ROOT/'dist'
previous=ROOT/'.sites-runtime/previous-build'
if previous.exists():shutil.rmtree(previous)
if dest.exists():dest.rename(previous)
OUT.rename(dest)
mode = 'release build (not deployed)' if args.release else 'local preview only'
print(f'Rendered {len(works)} projects and {len(posts)} articles with {len(topics)} topics from the explicit allowlist; {mode}.')

