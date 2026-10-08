"""Editorial project cases; all claims come from the curated public records."""
from html import escape as esc

def source_link(url, label):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>'

def shell_lab(study):
    panels=[]
    controls=''.join(f'<label><input type="radio" name="shell-scenario" value="{esc(step["id"], quote=True)}"'+(' checked' if i==0 else '')+f'><span>{esc(step["control_label"])}</span></label>' for i,step in enumerate(study['steps']))
    for i,step in enumerate(study['steps']):
        boxes=''.join(f'<div class="flow-node"><span>{n+1:02d}</span><strong>{esc(text)}</strong></div>' for n,text in enumerate(step['nodes']))
        panels.append(f'<section class="scenario-panel" data-scenario="{esc(step["id"], quote=True)}"'+(' hidden' if i else '')+f'><h3 class="sr-only">{esc(step["title"])}</h3><div class="flow-nodes">{boxes}</div><p>{esc(step["text"])}</p>{source_link(step["source"],"查看这一分支")}</section>')
    return f'<div class="case-lab"><div class="lab-heading"><h2>{esc(study["heading"])}</h2><span>源码流程示意 · 不执行系统命令</span></div><fieldset class="scenario-controls"><legend class="sr-only">选择切换情境</legend>{controls}</fieldset>{"".join(panels)}<p class="lab-footnote">{esc(study["note"])}</p></div>'

def code_excerpt(study):
    snippet=study['snippet']
    return f'''<figure class="case-code"><figcaption><span>src/main.rs · RUST</span>{source_link(snippet['source'],f"L{snippet['startLine']}–L{snippet['endLine']}")}</figcaption><div class="code-wrap"><button class="copy-code" type="button" aria-label="复制源码摘录">复制代码</button><pre tabindex="0"><code>{esc(snippet['code'])}</code></pre></div><p class="code-caption">{esc(snippet['caption'])}</p></figure>'''

def render_case(item, works, posts, visual):
    study=item.get('case_study');headline=esc(item['headline']).replace('\n','<br>')
    collection=item.get('kind')=='collection'
    sections=[('problem','收藏动机'),('structure','编排'),('tradeoff','选择'),('result','收藏记录'),('source','来源')] if collection else [('problem','问题'),('structure','结构'),('tradeoff','取舍'),('result','结果'),('source','源码')]
    toc=''.join(f'<a href="#{key}"><span>0{i}</span>{label}</a>' for i,(key,label) in enumerate(sections,1))
    prose=''
    for n,(key,label) in enumerate(sections[:-1],1):
        extra=code_excerpt(study) if key=='structure' and study else ''
        prose+=f'<section id="{key}" data-reading-section><p class="section-index">0{n} / {key.upper()}</p><h2>{label}<a class="heading-anchor" href="#{key}" aria-label="{label}段落链接">#</a></h2><p>{esc(item[key])}</p>{extra}</section>'
    evidence=''.join(f'<li>{source_link(item["repo"]+"/blob/"+item["revision"]+"/"+path,label)}</li>' for label,path in item['evidence'])
    evidence+=''.join(f'<li>{source_link(url,label)}</li>' for label,url in item.get('references',[]))
    if study:
        evidence+=''.join(f'<li>{source_link(fact["source"],fact["text"])}</li>' for fact in study['key_evidence'])
    source_title='来源与说明' if collection else '源码与证据'
    limitation_title='收藏说明' if collection else '边界与不足'
    revision_note='，本页选图保留仓库中的原始文件。' if collection else '，不代表对所有运行环境的测试结论。'
    prose+=f'<aside class="limitations"><h3>{limitation_title}</h3><p>{esc(item["limitation"])}</p></aside><section id="source" data-reading-section><p class="section-index">05 / SOURCE</p><h2>{source_title}<a class="heading-anchor" href="#source" aria-label="来源段落链接">#</a></h2><p>以上说明对应固定版本 <code>{item["revision"][:10]}</code>{revision_note}</p><ul class="evidence-list">{evidence}</ul></section>'
    if item['related']:
        prose+='<section class="related"><h2>继续拆开相邻的一层</h2>'
        for slug in item['related']:
            post=posts[slug];prose+=f'<a class="related-item" href="/writing/{slug}/"><strong>{esc(post["title"])}</strong><p>{esc(post["deck"])}</p></a>'
        prose+='</section>'
    idx=next(i for i,w in enumerate(works) if w['slug']==item['slug']);nxt=works[(idx+1)%len(works)]
    lab=shell_lab(study) if study else f'<div class="case-lab general-lab"><div class="lab-heading"><h2>拆开这个系统。</h2><span>结构示意 · 依据公开源码与文档</span></div>{visual(item)}</div>'
    if item.get('preview'):
        lab=f'<section class="case-lab preview-lab" aria-label="项目预览">{visual(item)}</section>'+(shell_lab(study) if study else '')
    if collection:
        lab=f'<section class="case-lab collection-lab" id="gallery"><div class="lab-heading"><h2>四帧，几种情绪。</h2><span>SELECTED WALLPAPERS / 个人收藏</span></div>{visual(item)}</section>'
    planet=esc(item.get('planet',item['slug']))
    next_planet=esc(nxt.get('planet',nxt['slug']))
    source_label='打开收藏仓库' if collection else '公开源码'
    explore_label='进入画廊' if collection else '拆开来看'
    explore_anchor='gallery' if collection else 'case-detail'
    medium_label='收藏形式' if collection else '技术构成'
    premise_label='THE COLLECTION' if collection else 'THE QUESTION'
    return f'''<div class="reading-progress" role="progressbar" aria-label="案例阅读进度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></div>
<header class="case-hero"><a class="case-back" href="/#selected-work">← 返回作品星系</a><div class="case-orbital-art" aria-hidden="true"><div class="case-orbital-ring"></div><img src="/assets/planets/{planet}.svg" width="400" height="400" alt=""><span>ORBIT / {item['number']}</span></div><div class="case-hero-copy"><p class="case-kicker">PROJECT {item['number']} / {esc(item['category'])}</p><p class="case-repo-name">{esc(item['title'])}</p><h1 aria-label="{esc(item['title'])}：{esc(item['headline'].replace(chr(10),''))}">{headline}</h1><p class="case-deck">{esc(item['summary'])}</p><div class="case-hero-links"><a href="#{explore_anchor}">{explore_label} <span aria-hidden="true">↓</span></a>{source_link(item.get('source_url',item['repo']),source_label)}</div></div><div class="case-hero-footer"><span>{medium_label} / {esc(item['tech'])}</span><span>FIXED REVISION / {item['revision'][:10]}</span></div></header>
<div id="case-detail" class="case-detail"><div class="case-premise"><span>{premise_label}</span><p>{esc(item['problem'])}</p></div>{lab}<div class="case-layout"><aside class="local-toc"><p class="eyebrow">项目切面 / {item['number']}</p><nav aria-label="项目目录">{toc}</nav><p class="reading-status">阅读进度 <span>0%</span></p><a class="toc-return" href="/#selected-work">返回星系 ↗</a></aside><article class="prose reading-body">{prose}</article></div></div>
<a class="next-orbit" href="/work/{nxt['slug']}/"><div><span>NEXT ORBIT / 下一个作品</span><strong>{esc(nxt['title'])}</strong><p>{esc(nxt['headline'].replace(chr(10),''))}</p></div><img src="/assets/planets/{next_planet}.svg" width="400" height="400" alt=""><b aria-hidden="true">↗</b></a>'''
