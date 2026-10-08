"""One article center with list, topic and tag views."""
from html import escape as esc
from .components import note_row
from .taxonomy import topic_row, topic_page

def library_pages(posts, topics, taxonomy):
    post_by_slug = {post["slug"]: post for post in posts}
    category_counts = {key:sum(post['category_id'] == key for post in posts) for key in taxonomy['categories']}
    tag_counts = {key:sum(key in post['tags'] for post in posts) for key in taxonomy['tags']}

    def writing_navigation(current='all'):
        entries = [('all','/writing/','全部文章'),('topics','/writing/topics/','专题'),('tags','/writing/tags/','标签')]
        return '<nav class="writing-navigation" aria-label="阅读方式">'+''.join(f'<a href="{href}"'+(' aria-current="page"' if key==current else '')+f'>{label}</a>' for key,href,label in entries)+'</nav>'

    def category_navigation(current=None):
        return '<nav class="category-navigation" aria-label="文章分类">'+''.join(f'<a href="/writing/categories/{key}/"'+(' aria-current="page"' if key==current else '')+f'>{esc(value["label"])}<span>{category_counts[key]}</span></a>' for key,value in taxonomy['categories'].items() if category_counts[key])+'</nav>'

    def directory_page(selected, title, description, category=None, filters=False, current='all'):
        controls = ''
        if filters:
            categories = ''.join(f'<option value="{key}">{esc(value["label"])}</option>' for key,value in taxonomy['categories'].items() if category_counts[key])
            tags = ''.join(f'<option value="{key}">{esc(label)}</option>' for key,label in taxonomy['tags'].items() if tag_counts[key])
            paths = ''.join(f'<option value="{item["slug"]}">{esc(item["title"])}</option>' for item in topics)
            controls = f'''<div class="writing-filters"><div><label for="article-category">分类</label><select id="article-category"><option value="all">全部分类</option>{categories}</select></div><div><label for="article-tag">标签</label><select id="article-tag"><option value="all">全部标签</option>{tags}</select></div><div><label for="article-topic">专题</label><select id="article-topic"><option value="all">全部专题</option>{paths}</select></div><button type="button" id="reset-writing">清空筛选</button></div>'''
        return f'''<header class="page-intro writing-intro wrap"><span class="eyebrow">02 / WRITING</span><h1>{esc(title)}</h1><p>{esc(description)}</p>{writing_navigation(current)}{category_navigation(category)}</header><section class="directory light-list wrap" aria-label="文章列表">{controls}<div class="writing-list-status"><span id="writing-count" role="status" aria-live="polite">{len(selected)} 篇文章</span><a href="/writing/topics/">按专题阅读</a></div><noscript><p class="noscript-note">可通过分类、标签和专题链接浏览文章；组合筛选需要 JavaScript。</p></noscript><div id="writing-list">{''.join(note_row(post, topics, taxonomy) for post in selected)}</div><div id="writing-empty" class="empty-state" hidden><p>没有同时符合这些条件的文章。</p><button type="button" id="empty-reset-writing">清空筛选，查看全部</button></div></section>'''

    yield 'writing', '文章', directory_page(posts,'文章。','从一篇笔记，读到一组问题。',filters=True), 'writing', ''
    for key, value in taxonomy['categories'].items():
        selected = [post for post in posts if post['category_id'] == key]
        if selected:
            yield 'writing/categories/'+key, value['label'], directory_page(selected,value['label']+'。',value['description'],category=key), 'writing', value['description']
    for key, label in taxonomy['tags'].items():
        selected = [post for post in posts if key in post['tags']]
        if selected:
            yield 'writing/tags/'+key, label+' 标签', directory_page(selected,label,f'与 {label} 相关的文章。', current='tags'), 'writing', ''
    tag_links = ''.join(f'<a href="/writing/tags/{key}/"><span>{esc(label)}</span><b>{tag_counts[key]:02d}</b></a>' for key,label in taxonomy['tags'].items() if tag_counts[key])
    body = f'''<header class="page-intro wrap"><span class="eyebrow">02 / WRITING</span><h1>文章。</h1><p>标签连接不同分类中的同一项技术或方法。</p>{writing_navigation('tags')}</header><section class="tag-directory wrap" aria-label="全部标签">{tag_links}</section>'''
    yield 'writing/tags', '文章 · 标签', body, 'writing', ''
    body = f'''<header class="page-intro topics-intro wrap"><span class="eyebrow">02 / WRITING</span><h1>文章。</h1><p>沿着一组问题，读完一个专题。</p>{writing_navigation('topics')}<span class="topics-count">{len(topics)} 个专题 / {len(posts)} 篇文章</span></header><section class="topics-directory wrap" aria-label="全部专题">{''.join(topic_row(topic,i,post_by_slug) for i,topic in enumerate(topics,1))}</section>'''
    yield 'writing/topics', '文章 · 专题', body, 'writing', ''
    # Retain old preview links without adding a second navigation entry.
    yield 'topics', '文章 · 专题', body, 'writing', ''
    for i, topic in enumerate(topics,1):
        body = topic_page(topic,i,post_by_slug,taxonomy)
        yield 'writing/topics/'+topic['slug'], topic['title'], body, 'writing', topic['deck']
        yield 'topics/'+topic['slug'], topic['title'], body, 'writing', topic['deck']
