"""Small reusable server-rendered components."""
from html import escape as esc
from .taxonomy import taxonomy_links

def url(kind, item):
    return f'/{kind}/{item["slug"]}/'

def note_row(post, topics, taxonomy):
    memberships = ' '.join(topic['slug'] for topic in topics if post['slug'] in topic['articles'])
    return f'''<article class="writing-row" data-category="{post['category_id']}" data-tags="{' '.join(post['tags'])}" data-topics="{memberships}"><span class="mono">{post['number']}</span><div><h3><a href="{url('writing',post)}">{esc(post['title'])}</a></h3><p>{esc(post['deck'])}</p>{taxonomy_links(post, taxonomy)}</div><time datetime="{post['date']}">{post['date'].replace('-','.')}</time></article>'''
