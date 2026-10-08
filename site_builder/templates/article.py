"""Paper field notes with a shared reading surface and explicit source links."""
from html import escape as esc, unescape
from math import ceil
import re


def render_article(post, posts, related_work, taxonomy_html='', topic_links='', continuation=''):
    body = post['body']
    if re.search(r'<script|\son\w+\s*=', body, re.I):
        raise ValueError('Executable content is not allowed')
    plain = unescape(re.sub(r'<[^>]+>', '', body))
    minutes = max(1, ceil(len(re.sub(r'\s+', '', plain)) / 350))
    toc = ''.join(f'<a href="#{anchor}"><span>{i:02d}</span>{esc(label)}</a>'
                  for i, (anchor, label) in enumerate(post['sections'], 1))
    body = re.sub(r'<h2 id="([^"]+)">([^<]+)</h2>',
                  lambda m: f'<h2 id="{m[1]}" data-reading-section>{m[2]}<a class="heading-anchor" href="#{m[1]}" aria-label="{m[2]}段落链接">#</a></h2>', body)
    body = re.sub(r'<pre><code>([\s\S]*?)</code></pre>',
                  lambda m: f'<div class="code-wrap"><span class="code-label" aria-hidden="true">EXCERPT</span><button class="copy-code" type="button" aria-label="复制代码">复制代码</button><pre tabindex="0"><code>{m[1]}</code></pre></div>', body)
    refs = ''.join(f'<li><a href="{esc(ref, quote=True)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a></li>' for label, ref in post['refs'])
    body += f'<section class="references" id="references"><h2>参考与延伸</h2><ol>{refs}</ol><p>根据技术笔记重新整理，示例使用通用名称。</p></section>' + continuation + related_work(post)
    next_post = posts[(posts.index(post) + 1) % len(posts)]
    return f'''<div class="reading-progress" role="progressbar" aria-label="文章阅读进度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></div>
    <header class="article-heading" id="article-start">
      <div class="article-masthead"><a class="back-link" href="/writing/">← 文章目录</a><span>OFFSET / FIELD NOTES</span><span>NO. {post['number']}</span></div>
      <div class="article-cover-copy"><div class="article-meta"><span>{esc(post['category'])}</span><span>技术笔记整理</span></div>
      <h1>{esc(post['title'])}</h1><p class="deck">{esc(post['deck'])}</p>{taxonomy_html}{topic_links}</div>
      <div class="article-folio" aria-hidden="true"><span>{post['number']}</span><i></i><b>READ / THINK / REBUILD</b></div>
      <div class="article-cover-footer"><time datetime="{post['date']}">整理于 {post['date'].replace('-', '.')}</time><span>约 {minutes} 分钟阅读</span><a href="#{post['sections'][0][0]}">开始阅读 <span aria-hidden="true">↓</span></a></div>
    </header>
    <div class="article-layout"><aside class="article-toc"><details open><summary>阅读路径 / CONTENTS</summary><nav aria-label="文章目录">{toc}</nav></details><p class="reading-status">阅读进度 <span>0%</span></p><a class="toc-return" href="#article-start">返回页首 ↑</a></aside><article class="prose reading-body">{body}</article></div>
    <a class="next-note" href="/writing/{next_post['slug']}/"><div><span>CONTINUE READING / 下一篇</span><strong>{esc(next_post['title'])}</strong><p>{esc(next_post['deck'])}</p></div><span class="next-note-number" aria-hidden="true">{next_post['number']}</span><b aria-hidden="true">↗</b></a>'''
