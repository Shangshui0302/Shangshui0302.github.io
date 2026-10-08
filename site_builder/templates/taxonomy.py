"""Validated category/tag metadata and editorial reading paths for the static site."""
from html import escape as esc
import re


def validate_taxonomy(taxonomy, posts, topics):
    categories, tags = taxonomy['categories'], taxonomy['tags']
    for slug in [*categories, *tags]:
        if not re.fullmatch(r'[a-z0-9-]+', slug) or slug == 'all':
            raise ValueError(f'Invalid taxonomy slug: {slug}')
    post_ids = {post['slug'] for post in posts}
    if len(post_ids) != len(posts):
        raise ValueError('Duplicate article slug')
    if len({topic['slug'] for topic in topics}) != len(topics):
        raise ValueError('Duplicate topic slug')
    for post in posts:
        if post['category_id'] not in categories:
            raise ValueError(f'Unknown category: {post["slug"]}')
        if not post['tags'] or len(post['tags']) != len(set(post['tags'])) or not set(post['tags']) <= tags.keys():
            raise ValueError(f'Invalid tags: {post["slug"]}')
    for topic in topics:
        selected = topic['articles']
        if len(selected) < 2 or len(selected) != len(set(selected)) or not set(selected) <= post_ids:
            raise ValueError(f'Invalid reading path: {topic["slug"]}')
        if len(topic['reading_guide']) != len(selected):
            raise ValueError(f'Reading guide must match articles: {topic["slug"]}')


def taxonomy_links(post, taxonomy):
    category = post['category_id']
    links = f'<a class="category-link" href="/writing/categories/{category}/">{esc(taxonomy["categories"][category]["label"])}</a>'
    links += ''.join(f'<a href="/writing/tags/{tag}/" class="tag-link">{esc(taxonomy["tags"][tag])}</a>' for tag in post['tags'])
    return f'<div class="note-taxonomy" aria-label="文章分类与标签">{links}</div>'


def topic_row(topic, index, posts):
    chapters = ''.join(f'<li><a href="/writing/{slug}/">{esc(posts[slug]["title"])}</a></li>' for slug in topic['articles'])
    return f'''<article class="topic-row">
      <div class="topic-number" aria-hidden="true">{index:02d}<i></i></div>
      <div class="topic-row-copy"><span class="eyebrow">READING PATH / {len(topic['articles'])} 篇</span>
        <h2><a href="/writing/topics/{topic['slug']}/">{esc(topic['title'])}</a></h2><p>{esc(topic['deck'])}</p>
        <a class="text-link" href="/writing/topics/{topic['slug']}/">进入专题</a></div>
      <ol class="topic-chapters" aria-label="专题文章">{chapters}</ol>
    </article>'''


def topic_page(topic, index, posts, taxonomy):
    chapters = ''
    for i, (slug, guide) in enumerate(zip(topic['articles'], topic['reading_guide']), 1):
        post = posts[slug]
        chapters += f'''<li class="path-chapter"><span class="path-step">{i:02d}</span><div>
          <p class="path-guide">{esc(guide)}</p><h2><a href="/writing/{slug}/">{esc(post['title'])}</a></h2>
          <p>{esc(post['deck'])}</p>{taxonomy_links(post, taxonomy)}
          <a class="text-link" href="/writing/{slug}/">阅读文章</a></div></li>'''
    return f'''<header class="topic-hero wrap"><div class="topic-hero-copy"><a class="back-link" href="/writing/topics/">← 全部专题</a>
      <p class="eyebrow">DOSSIER {index:02d} / {len(topic['articles'])} 篇文章</p><h1>{esc(topic['title'])}</h1>
      <p class="topic-deck">{esc(topic['deck'])}</p><a class="text-link" href="/writing/{topic['articles'][0]}/">从第一篇开始</a></div>
      <div class="topic-cover-art" aria-hidden="true"><span>{index:02d}</span><i></i><i></i><i></i><b>FOLLOW THE THREAD</b></div></header>
      <section class="topic-introduction wrap"><h2>沿着问题，继续读。</h2><p>{esc(topic['description'])}</p></section>
      <section class="topic-reading wrap" aria-label="专题阅读顺序"><ol>{chapters}</ol></section>
      <div class="topic-exit wrap"><a href="/writing/topics/">← 浏览其他专题</a><a href="/writing/">查看全部文章 ↗</a></div>'''


def article_topics(post, topics, posts):
    memberships = [topic for topic in topics if post['slug'] in topic['articles']]
    if not memberships:
        return '', ''
    teaser = '<div class="article-topic-links"><span>所在专题</span>' + ''.join(
        f'<a href="/writing/topics/{topic["slug"]}/">{esc(topic["title"])} ↗</a>' for topic in memberships) + '</div>'
    continuation = '<section class="series-reading"><h2>沿专题继续阅读</h2>'
    for topic in memberships:
        chapters = ''
        for i, slug in enumerate(topic['articles'], 1):
            current = ' aria-current="page"' if slug == post['slug'] else ''
            chapters += f'<li><a href="/writing/{slug}/"{current}><span>{i:02d}</span>{esc(posts[slug]["title"])}</a></li>'
        continuation += f'<h3><a href="/writing/topics/{topic["slug"]}/">{esc(topic["title"])}</a></h3><ol>{chapters}</ol>'
    return teaser, continuation + '</section>'
