"""The visual front page, composed from shared content components."""
from html import escape as esc
from .components import url, note_row
from .stellar import render_stellar
from .visuals import visual

def render_home(ROOT, works, posts, topics, taxonomy):
    stellar_hero = render_stellar(ROOT)
    hero = works[0]
    features = ''
    for item in works[1:3]+works[4:]:
        features += f'''<article class="editorial-project"><div class="project-copy"><span class="mono">{item['number']} / {esc(item['category'])}</span><h3>{esc(item['title'])}</h3><p>{esc(item['summary'])}</p><a class="text-link" href="{url('work',item)}">查看项目</a></div><div class="project-visual cut-reveal">{visual(item)}</div></article>'''
    home = f'''{stellar_hero}
    <section id="featured-project" aria-labelledby="featured-title"><div class="feature-caption wrap"><div><span class="mono">FEATURED PROJECT</span><h2 id="featured-title"><a href="{url('work',hero)}">{esc(hero['title'])}</a></h2></div><p>{esc(hero['summary'])}</p><a class="text-link" href="{url('work',hero)}">查看项目</a></div></section>
    <section class="section wrap"><div class="section-label"><h2 class="eyebrow">继续拆开 / 精选作品</h2><span class="mono">以结构呈现选择</span></div>{features}<div class="section-end"><a class="text-link" href="/work/">全部 {len(works)} 个项目</a></div></section>
    <section class="section writing-preview wrap"><div class="section-label"><p class="eyebrow">文章 / 整理与推演</p><span class="mono">FIELD NOTES</span></div><h2 class="section-title">把问题拆开，<br>把思路留下。</h2>{''.join(note_row(p, topics, taxonomy) for p in posts[-6:])}<div class="section-end"><a class="text-link" href="/writing/">全部文章</a></div></section>
    <section class="index-callout wrap"><h2>按问题，<br>找到下一步。</h2><div><a class="text-link" href="/index/">搜索与目录</a></div></section>'''
    return home
