"""Build only allowlisted, curated content. Never reads a vault or live API."""
from site_builder.content import read_content, select_home_content, validate_case_studies
from site_builder.search import write_search_index
from site_builder.release import release_origin
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
from site_builder.feed import render_feed

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / 'site_config.json').read_text())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', action='store_true', help='Require a public HTTPS origin before building')
args = parser.parse_args()
if args.release:
    CONFIG['site_url'] = release_origin(CONFIG)
MANIFEST = json.loads((ROOT / 'public-content/manifest.json').read_text())
OUT = ROOT / '.sites-runtime/section-build'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)
page = partial(render_page, CONFIG)

works = read_content(ROOT, MANIFEST, 'work')
posts = read_content(ROOT, MANIFEST, 'writing')
topics = read_content(ROOT, MANIFEST, 'topics')
taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
validate_taxonomy(taxonomy, posts, topics)
validate_case_studies(works)
home_selection = select_home_content(json.loads((ROOT / 'public-content/home.json').read_text()), works, posts)
work_by_slug = {p['slug']: p for p in works}
post_by_slug = {p['slug']: p for p in posts}
for p in works:
    assert set(p['related']) <= set(post_by_slug)
for p in posts:
    assert set(p['related_work']) <= set(work_by_slug)

def write(route, content):
    target = OUT / route.strip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

write('', page('开源作品与技术文章', render_home(ROOT, works, home_selection, topics, taxonomy), 'home', stellar=True))

write('work', page('作品目录', render_work_directory(works), 'work'))
related_work = partial(related_work_links, work_by_slug=work_by_slug)

for item in works:
    body=render_case(item,works,post_by_slug,visual)
    write('work/'+item['slug'],page(item['title'],body,'work',item['summary'],is_case=True))

for route, title, body, active, description in library_pages(posts, topics, taxonomy):
    write(route, page(title, body, active, description))

for post in posts:
    topic_links, continuation = article_topics(post, topics, post_by_slug)
    article=render_article(post,posts,related_work,taxonomy_links(post,taxonomy),topic_links,continuation)
    write('writing/'+post['slug'],page(post['title'],article,'writing',post['deck'],True))
    # Existing preview links remain useful without depending on JavaScript.
    write('journal/'+post['slug'],page(post['title'],article,'writing',post['deck'],True))

index_url = write_search_index(OUT, works, posts, topics, taxonomy)
write('index', page('搜索', render_search(works, posts, topics, taxonomy, index_url), 'index'))

render_feed(CONFIG, posts, taxonomy).write(OUT/'feed.xml', encoding='utf-8', xml_declaration=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
(OUT/'assets/site.css').write_text(bundle_styles(ROOT))
dest=ROOT/'dist'
previous=ROOT/'.sites-runtime/previous-build'
if previous.exists():shutil.rmtree(previous)
if dest.exists():dest.rename(previous)
OUT.rename(dest)
mode = 'release build (not deployed)' if args.release else 'local preview only'
print(f'Rendered {len(works)} projects and {len(posts)} articles with {len(topics)} topics from the explicit allowlist; {mode}.')
