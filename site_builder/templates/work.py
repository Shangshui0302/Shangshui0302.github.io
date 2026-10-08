"""Portfolio directory and reusable related-project links."""
from html import escape as esc
from .components import url

def render_work_directory(works):
    rows=''
    for item in works:
        state='个人收藏<br>非原创图集' if item.get('kind')=='collection' else '公开仓库<br>已核验'
        label='收藏' if item.get('kind')=='collection' else '源码'
        rows += f'''<article class="work-row"><span class="mono">{item['number']}</span><h2><a href="{url('work',item)}">{esc(item['title'])}</a></h2><p>{esc(item['summary'])}</p><span class="state">{state}</span><a class="source-link" href="{item.get('source_url',item['repo'])}" target="_blank" rel="noopener noreferrer">{label}</a></article>'''
    body=f'''<header class="page-intro wrap"><span class="eyebrow">01 / WORK</span><h1>作品目录。</h1><p>桌面工具、系统配置，以及留在屏幕上的视觉收藏。</p></header><section class="directory wrap" aria-label="全部作品"><div class="directory-head"><span>编号</span><span>项目</span><span>用途</span><span>核验范围</span><span>来源</span></div>{rows}<p class="directory-footnote">“已核验”指公开仓库与相关源码可查阅，不代表本站对项目进行了完整运行测试。收藏条目单独标注，图像不声明为本站原创。</p></section>'''
    return body

def related_work_links(post, work_by_slug):
    if not post['related_work']:
        return ''
    links=''
    for slug in post['related_work']:
        item=work_by_slug[slug]
        links+=f'<a class="related-item" href="{url("work",item)}"><strong>{esc(item["title"])}</strong><p>{esc(item["summary"])}</p></a>'
    return '<section class="related"><h2>从文章到实践</h2>'+links+'</section>'
