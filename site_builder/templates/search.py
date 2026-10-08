"""One searchable index for every public content type."""
from html import escape as esc
from .components import url

def render_search(works, posts, topics, taxonomy, index_url):
    results=[]
    for kind, items in [('work',works),('writing',posts),('topics',topics)]:
        for item in items:
            title=item['title'];summary=item.get('summary',item.get('deck',''))
            category_label = taxonomy['categories'][item['category_id']]['label'] if kind == 'writing' else item.get('category','专题 / '+str(len(item.get('articles',[])))+' 篇')
            kind_label = {"work":"作品", "writing":"文章", "topics":"专题"}[kind]
            results.append(f'<a class="result-row" href="{url('writing/topics' if kind == 'topics' else kind,item)}" data-kind="{kind}"><span class="kind">{kind_label}</span><div><h2>{esc(title)}</h2><p>{esc(summary)}</p></div><span class="mono">{esc(category_label)}</span></a>')
    body=f'''<header class="page-intro wrap"><span class="eyebrow">03 / SEARCH</span><h1>搜索。</h1><p>作品、文章与专题，在这里找到。</p><form class="search-form" id="search" data-search-index="{esc(index_url, quote=True)}" action="/index/" method="get" role="search"><label class="sr-only" for="search-input">搜索作品、文章与专题</label><input id="search-input" name="q" type="search" placeholder="例如：服务、权限、Git" autocomplete="off"><button type="submit">搜索</button></form></header><section class="directory wrap"><div class="listing-controls"><label for="kind">类型</label><select id="kind"><option value="all">全部内容</option><option value="work">作品</option><option value="writing">文章</option><option value="topics">专题</option></select><span class="count" role="status" aria-live="polite">{len(works)+len(posts)+len(topics)} 项内容</span></div><noscript><p class="noscript-note">当前显示完整目录。搜索与筛选需要 JavaScript，所有作品、文章与专题链接仍可直接打开。</p></noscript><p id="search-notice" role="status" hidden><span></span> <button class="retry-search text-link" type="button" hidden>重试搜索</button></p><div id="search-results">{''.join(results)}</div><div id="search-empty" class="empty-state" hidden><p>没有找到匹配内容。</p><button class="reset-search" type="button">清空搜索，查看全部</button></div></section>'''
    return body
