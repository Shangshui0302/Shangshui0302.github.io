"""Build only allowlisted, curated content. Never reads a vault or live API."""
from pathlib import Path
from stellar_template import render_stellar
from case_template import render_case
from article_template import render_article
from exhibit_template import kanban_diagram, wallpaper_gallery
from taxonomy_template import validate_taxonomy, taxonomy_links, topic_row, topic_page, article_topics
from html import escape as esc
import json
import re
import shutil
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / 'site_config.json').read_text())
MANIFEST = json.loads((ROOT / 'public-content/manifest.json').read_text())
OUT = ROOT / '.sites-runtime/section-build'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)
site_name, wordmark = CONFIG['site_name'], CONFIG['wordmark']

def read_content(kind):
    items = []
    for slug in MANIFEST[kind]:
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError('Invalid allowlist slug')
        item = json.loads((ROOT / 'public-content' / kind / (slug + '.json')).read_text())
        assert item['slug'] == slug
        items.append(item)
    return items

works = read_content('work')
posts = read_content('writing')
topics = read_content('topics')
taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
validate_taxonomy(taxonomy, posts, topics)
work_by_slug = {p['slug']: p for p in works}
post_by_slug = {p['slug']: p for p in posts}
for p in works:
    assert set(p['related']) <= set(post_by_slug)
for p in posts:
    assert set(p['related_work']) <= set(work_by_slug)

def url(kind, item):
    return f'/{kind}/{item["slug"]}/'

def nav(active):
    entries = ''.join(f'<a href="/{slug}/"'+(' aria-current="page"' if active == slug else '')+f'>{label}</a>' for slug, label in [('work','作品'),('writing','文章'),('topics','专题'),('index','索引')])
    return f'''<a class="skip" href="#main">跳到正文</a><header class="topbar wrap">
    <a class="brand" href="/" aria-label="{esc(site_name)} {esc(wordmark)} 首页"><span class="brand-mark" aria-hidden="true"></span>{esc(wordmark)}<span>{esc(site_name)}</span></a>
    <nav aria-label="主导航">{entries}</nav><div class="nav-actions"><a class="search-link" href="/index/#search"><span class="search-symbol" aria-hidden="true"></span>搜索</a><button class="motion" type="button" aria-pressed="false">减少动效</button></div></header>'''

def footer():
    return f'''<footer class="footer wrap"><div><a class="footer-brand" href="/">{esc(wordmark)} / {esc(site_name)}</a><p class="footer-note">作品与文章，按问题组织。</p></div><div class="footer-links"><a href="{CONFIG['github_url']}" target="_blank" rel="noopener noreferrer">GitHub</a><a href="/feed.xml">RSS</a><a href="/index/">完整索引</a></div><span class="mono">© {CONFIG['year']} {esc(wordmark)}</span></footer>'''

def page(title, body, active='', description='', is_article=False, stellar=False, is_case=False):
    stellar_assets = '<link rel="stylesheet" href="/assets/stellar.css"><script src="/assets/stellar.js" defer></script>' if stellar else ''
    inner_assets = '<link rel="stylesheet" href="/assets/inner.css"><script src="/assets/inner.js" defer></script>' if is_article or is_case else ''
    if stellar or is_case:
        inner_assets += '<link rel="stylesheet" href="/assets/exhibits.css">'
    favicon = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23F1EFE9'/%3E%3Cpath fill='%2317191C' d='M10 10h44v14H10zm0 32h44v12H10z'/%3E%3Cpath fill='%23FF4D2E' d='M10 29h44v8H10z'/%3E%3C/svg%3E"
    return f'''<!doctype html><html class="no-js" lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · {esc(site_name)} / {esc(wordmark)}</title><meta name="description" content="{esc(description or CONFIG['description'])}"><meta name="referrer" content="no-referrer"><link rel="icon" type="image/svg+xml" href="{favicon}"><link rel="stylesheet" href="/assets/section.css"><link rel="stylesheet" href="/assets/topics.css"><link rel="alternate" type="application/rss+xml" title="{esc(site_name)}文章" href="/feed.xml"><script src="/assets/section.js" defer></script>{stellar_assets}{inner_assets}</head><body{' class="orbit-home"' if stellar else (' class="reading-page"' if is_article else (' class="case-page"' if is_case else ''))}>{nav(active)}<main id="main">{body}</main>{footer()}</body></html>'''

def write(route, content):
    target = OUT / route.strip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

def shell_diagram():
    return '''<div class="system-diagram" role="img" aria-label="结构示意：停止已注册服务，启动目标服务，确认 active 后尝试记录选择。停止确认超时或启动命令失败时尝试默认服务。"><div class="diagram-nodes"><div class="diagram-node"><small>01 / STOP</small><strong>停止旧服务<br>确认非 active</strong></div><div class="diagram-node"><small>02 / START</small><strong>启动目标<br>等待 active</strong></div><div class="diagram-node"><small>03 / RECORD</small><strong>确认状态<br>尝试记录</strong></div></div><div class="diagram-note" aria-hidden="true"></div><p class="diagram-legend">停止确认超时 / 启动命令失败时尝试默认服务；active 等待超时仅报错。</p></div>'''

def theme_diagram():
    return '''<figure class="theme-figure"><div class="figure-heading"><span>色板 / 模板 / 候选窗</span><span>FCITX5 × MATUGEN</span></div><div class="theme-flow"><div class="color-input"><span class="swatch" style="--swatch:#d3bea0">primary</span><span class="swatch" style="--swatch:#221b11">on_primary</span></div><div class="map-line" aria-hidden="true"></div><div class="candidate-example"><span>pian yi</span><div class="candidate-row"><b>1 偏移</b><span>2 便宜</span></div></div></div><figcaption class="figcaption">映射示意，非运行截图。高亮背景与文字成对生成，布局沿用主题结构。</figcaption></figure>'''

def skills_diagram():
    return '''<figure class="skills-figure"><div class="figure-heading"><span>验证层次</span><span>每一步，只证明它自己。</span></div><div class="skills-lines"><div><strong>能求值</strong><span>EVALUATE</span></div><div><strong>能构建</strong><span>BUILD</span></div><div><strong>正在运行</strong><span>VERIFY RUNTIME</span></div></div><figcaption class="figcaption">构建结果与现场结果分开记录；激活需要单独授权。</figcaption></figure>'''

def nix_diagram():
    return '''<div class="system-diagram" role="img" aria-label="锁定输入经过 flake 主机入口，组合系统与用户模块。"><div class="diagram-nodes"><div class="diagram-node"><small>01 / INPUTS</small><strong>锁定输入</strong></div><div class="diagram-node"><small>02 / FLAKE</small><strong>主机入口</strong></div><div class="diagram-node"><small>03 / MODULES</small><strong>系统层 / 用户层</strong></div></div><p class="diagram-legend">配置结构示意；不代表所有模块已现场激活。</p></div>'''

def visual(item):
    if item['visual']=='kanban':return kanban_diagram()
    if item['visual']=='wallpapers':return wallpaper_gallery(item)
    return {'shell':shell_diagram,'theme':theme_diagram,'skills':skills_diagram,'nix':nix_diagram}[item['visual']]()

def note_row(post):
    memberships = ' '.join(topic['slug'] for topic in topics if post['slug'] in topic['articles'])
    return f'''<article class="writing-row" data-category="{post['category_id']}" data-tags="{' '.join(post['tags'])}" data-topics="{memberships}"><span class="mono">{post['number']}</span><div><h3><a href="{url('writing',post)}">{esc(post['title'])}</a></h3><p>{esc(post['deck'])}</p>{taxonomy_links(post, taxonomy)}</div><time datetime="{post['date']}">{post['date'].replace('-','.')}</time></article>'''


stellar_hero = render_stellar(ROOT)
hero = works[0]
features = ''
for item in works[1:3]+works[4:]:
    features += f'''<article class="editorial-project"><div class="project-copy"><span class="mono">{item['number']} / {esc(item['category'])}</span><h3>{esc(item['title'])}</h3><p>{esc(item['summary'])}</p><a class="text-link" href="{url('work',item)}">查看项目</a></div><div class="project-visual cut-reveal">{visual(item)}</div></article>'''
home = f'''{stellar_hero}
<section id="featured-project" aria-labelledby="featured-title"><div class="feature-caption wrap"><div><span class="mono">FEATURED PROJECT</span><h2 id="featured-title"><a href="{url('work',hero)}">{esc(hero['title'])}</a></h2></div><p>{esc(hero['summary'])}</p><a class="text-link" href="{url('work',hero)}">查看项目</a></div></section>
<section class="section wrap"><div class="section-label"><h2 class="eyebrow">继续拆开 / 精选作品</h2><span class="mono">以结构呈现选择</span></div>{features}<div class="section-end"><a class="text-link" href="/work/">全部 {len(works)} 个项目</a></div></section>
<section class="section writing-preview wrap"><div class="section-label"><p class="eyebrow">文章 / 整理与推演</p><span class="mono">FIELD NOTES</span></div><h2 class="section-title">把问题拆开，<br>把思路留下。</h2>{''.join(note_row(p) for p in posts[-6:])}<div class="section-end"><a class="text-link" href="/writing/">全部文章</a></div></section>
<section class="index-callout wrap"><h2>按问题，<br>找到下一步。</h2><div><p>{len(works)} 个项目，{len(posts)} 篇文章。<br>从目录进入，不必顺着展陈走。</p><a class="text-link" href="/index/">进入完整索引</a></div></section>'''
write('', page('开源作品与技术文章',home,stellar=True))

rows=''
for item in works:
    state='个人收藏<br>非原创图集' if item.get('kind')=='collection' else '公开仓库<br>已核验'
    label='收藏' if item.get('kind')=='collection' else '源码'
    rows += f'''<article class="work-row"><span class="mono">{item['number']}</span><h2><a href="{url('work',item)}">{esc(item['title'])}</a></h2><p>{esc(item['summary'])}</p><span class="state">{state}</span><a class="source-link" href="{item.get('source_url',item['repo'])}" target="_blank" rel="noopener noreferrer">{label}</a></article>'''
body=f'''<header class="page-intro wrap"><span class="eyebrow">01 / WORK</span><h1>作品目录。</h1><p>桌面工具、系统配置，以及留在屏幕上的视觉收藏。</p></header><section class="directory wrap" aria-label="全部作品"><div class="directory-head"><span>编号</span><span>项目</span><span>用途</span><span>核验范围</span><span>来源</span></div>{rows}<p class="directory-footnote">“已核验”指公开仓库与相关源码可查阅，不代表本站对项目进行了完整运行测试。收藏条目单独标注，图像不声明为本站原创。</p></section>'''
write('work',page('作品目录',body,'work'))

def related_work_links(post):
    if not post['related_work']:
        return ''
    links=''
    for slug in post['related_work']:
        item=work_by_slug[slug]
        links+=f'<a class="related-item" href="{url("work",item)}"><strong>{esc(item["title"])}</strong><p>{esc(item["summary"])}</p></a>'
    return '<section class="related"><h2>从文章到实践</h2>'+links+'</section>'

for item in works:
    body=render_case(item,works,post_by_slug,visual)
    write('work/'+item['slug'],page(item['title'],body,'work',item['summary'],is_case=True))

category_counts = {key:sum(post['category_id'] == key for post in posts) for key in taxonomy['categories']}
tag_counts = {key:sum(key in post['tags'] for post in posts) for key in taxonomy['tags']}

def writing_navigation(current='all'):
    entries = [('all','/writing/','全部文章'),('topics','/topics/','专题阅读'),('tags','/writing/tags/','标签索引')]
    return '<nav class="writing-navigation" aria-label="阅读方式">'+''.join(f'<a href="{href}"'+(' aria-current="page"' if key==current else '')+f'>{label}</a>' for key,href,label in entries)+'</nav>'

def category_navigation(current=None):
    return '<nav class="category-navigation" aria-label="文章分类">'+''.join(f'<a href="/writing/categories/{key}/"'+(' aria-current="page"' if key==current else '')+f'>{esc(value["label"])}<span>{category_counts[key]}</span></a>' for key,value in taxonomy['categories'].items() if category_counts[key])+'</nav>'

def directory_page(selected, title, description, category=None, filters=False):
    controls = ''
    if filters:
        categories = ''.join(f'<option value="{key}">{esc(value["label"])}</option>' for key,value in taxonomy['categories'].items() if category_counts[key])
        tags = ''.join(f'<option value="{key}">{esc(label)}</option>' for key,label in taxonomy['tags'].items() if tag_counts[key])
        paths = ''.join(f'<option value="{item["slug"]}">{esc(item["title"])}</option>' for item in topics)
        controls = f'''<div class="writing-filters"><div><label for="article-category">分类</label><select id="article-category"><option value="all">全部分类</option>{categories}</select></div><div><label for="article-tag">标签</label><select id="article-tag"><option value="all">全部标签</option>{tags}</select></div><div><label for="article-topic">专题</label><select id="article-topic"><option value="all">全部专题</option>{paths}</select></div><button type="button" id="reset-writing">清空筛选</button></div>'''
    return f'''<header class="page-intro writing-intro wrap"><span class="eyebrow">02 / WRITING</span><h1>{esc(title)}</h1><p>{esc(description)}</p>{writing_navigation('all' if filters else '')}{category_navigation(category)}</header><section class="directory light-list wrap" aria-label="文章列表">{controls}<div class="writing-list-status"><span id="writing-count" role="status" aria-live="polite">{len(selected)} 篇文章</span><a href="/topics/">按专题顺着读 ↗</a></div><noscript><p class="noscript-note">可通过分类、标签和专题链接浏览文章；组合筛选需要 JavaScript。</p></noscript><div id="writing-list">{''.join(note_row(post) for post in selected)}</div><div id="writing-empty" class="empty-state" hidden><p>没有同时符合这些条件的文章。</p><button type="button" id="empty-reset-writing">清空筛选，查看全部</button></div></section>'''

write('writing',page('文章目录',directory_page(posts,'文章目录。','按领域浏览，用标签找到具体技术，或沿着专题读完一组问题。',filters=True),'writing'))
for key, value in taxonomy['categories'].items():
    selected = [post for post in posts if post['category_id'] == key]
    if selected:
        write('writing/categories/'+key,page(value['label'],directory_page(selected,value['label']+'。',value['description'],category=key),'writing',value['description']))
for key, label in taxonomy['tags'].items():
    selected = [post for post in posts if key in post['tags']]
    if selected:
        write('writing/tags/'+key,page(label+' 标签',directory_page(selected,label,f'与 {label} 相关的文章。每篇保留完整正文、示例和参考资料。'),'writing'))
tag_links = ''.join(f'<a href="/writing/tags/{key}/"><span>{esc(label)}</span><b>{tag_counts[key]:02d}</b></a>' for key,label in taxonomy['tags'].items() if tag_counts[key])
body = f'''<header class="page-intro wrap"><span class="eyebrow">WRITING / TAGS</span><h1>从一个词，继续找。</h1><p>标签连接不同分类中的同一项技术或方法。</p>{writing_navigation('tags')}</header><section class="tag-directory wrap" aria-label="全部标签">{tag_links}</section>'''
write('writing/tags',page('标签索引',body,'writing'))
body = f'''<header class="page-intro topics-intro wrap"><span class="eyebrow">03 / DOSSIERS</span><h1>专题。</h1><p>把相关的问题连起来。每个专题都有入口，也有下一步。</p>{writing_navigation('topics')}<span class="topics-count">{len(topics)} 个专题 / {len(posts)} 篇文章</span></header><section class="topics-directory wrap" aria-label="全部专题">{''.join(topic_row(topic,i,post_by_slug) for i,topic in enumerate(topics,1))}</section>'''
write('topics',page('专题',body,'topics'))
for i, topic in enumerate(topics,1):
    write('topics/'+topic['slug'],page(topic['title'],topic_page(topic,i,post_by_slug,taxonomy),'topics',topic['deck']))

for post in posts:
    topic_links, continuation = article_topics(post, topics, post_by_slug)
    article=render_article(post,posts,related_work_links,taxonomy_links(post,taxonomy),topic_links,continuation)
    write('writing/'+post['slug'],page(post['title'],article,'writing',post['deck'],True))
    # Existing preview links remain useful without depending on JavaScript.
    write('journal/'+post['slug'],page(post['title'],article,'writing',post['deck'],True))

results=[]
for kind, items in [('work',works),('writing',posts),('topics',topics)]:
    for item in items:
        title=item['title'];summary=item.get('summary',item.get('deck',''))
        searchable=' '.join(str(item.get(k,'')) for k in ['title','summary','deck','description','category','tech','problem','structure','tradeoff','result','body'])
        searchable=re.sub('<[^>]+>',' ',searchable)
        if kind == 'writing':
            searchable += ' ' + taxonomy['categories'][item['category_id']]['label'] + ' ' + ' '.join(taxonomy['tags'][tag] for tag in item['tags'])
        category_label = taxonomy['categories'][item['category_id']]['label'] if kind == 'writing' else item.get('category','专题 / '+str(len(item.get('articles',[])))+' 篇')
        kind_label = {"work":"作品", "writing":"文章", "topics":"专题"}[kind]
        results.append(f'<a class="result-row" href="{url(kind,item)}" data-kind="{kind}" data-search="{esc(searchable,quote=True)}"><span class="kind">{kind_label}</span><div><h2>{esc(title)}</h2><p>{esc(summary)}</p></div><span class="mono">{esc(category_label)}</span></a>')
body=f'''<header class="page-intro wrap"><span class="eyebrow">04 / INDEX</span><h1>完整索引。</h1><p>作品、文章与专题放在同一个目录。搜索标题、标签或正文中的关键词。</p><form class="search-form" id="search" action="/index/" method="get" role="search"><label class="sr-only" for="search-input">搜索作品、文章与专题</label><input id="search-input" name="q" type="search" placeholder="例如：服务、权限、Git" autocomplete="off"><button type="submit">搜索</button></form></header><section class="directory wrap"><div class="listing-controls"><label for="kind">类型</label><select id="kind"><option value="all">全部内容</option><option value="work">作品</option><option value="writing">文章</option><option value="topics">专题</option></select><span class="count" role="status" aria-live="polite">{len(works)+len(posts)+len(topics)} 项内容</span></div><noscript><p class="noscript-note">当前显示完整目录。搜索与筛选需要 JavaScript，所有作品、文章与专题链接仍可直接打开。</p></noscript><div id="search-results">{''.join(results)}</div><div id="search-empty" class="empty-state" hidden><p>没有找到匹配内容。</p><button class="reset-search" type="button">清空搜索，查看全部</button></div></section>'''
write('index',page('完整索引',body,'index'))

# All feed entries are explicitly allowlisted. Preview uses local URLs until approved publication.
origin=CONFIG.get('site_url') or 'http://127.0.0.1:4173'
rss=Element('rss',{'version':'2.0'});channel=SubElement(rss,'channel')
for key,value in [('title',f'{site_name} / {wordmark}'),('link',origin+'/writing/'),('description',CONFIG['description']),('language','zh-cn')]:SubElement(channel,key).text=value
for post in posts:
    node=SubElement(channel,'item')
    for key,value in [('title',post['title']),('link',origin+url('writing',post)),('guid',origin+url('writing',post)),('description',post['deck'])]:SubElement(node,key).text=value
    SubElement(node,'category').text=taxonomy['categories'][post['category_id']]['label']
    for tag in post['tags']:SubElement(node,'category').text=taxonomy['tags'][tag]
ElementTree(rss).write(OUT/'feed.xml',encoding='utf-8',xml_declaration=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
dest=ROOT/'dist'
previous=ROOT/'.sites-runtime/previous-build'
if previous.exists():shutil.rmtree(previous)
if dest.exists():dest.rename(previous)
OUT.rename(dest)
print(f'Rendered {len(works)} projects and {len(posts)} articles with {len(topics)} topics from the explicit allowlist; local preview only.')
