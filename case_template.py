"""Editorial project cases; all claims come from the curated public records."""
from html import escape as esc

def source_link(url, label):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>'

def shell_lab(study):
    panels=[]
    labels=['正常交接','停止超时 / 启动失败','等待 active 超时']
    flows=[['停止已注册服务','启动目标服务','确认 active · 尝试记录'],['停止超时 / 启动命令失败','尝试启动默认服务','返回错误 · 恢复未确认'],['启动命令成功','轮询等待 active','超时返回 · 不回退']]
    controls=''.join(f'<label><input type="radio" name="shell-scenario" value="{i}"'+(' checked' if i==0 else '')+f'><span>{label}</span></label>' for i,label in enumerate(labels))
    for i,(step,nodes) in enumerate(zip(study['steps'],flows)):
        boxes=''.join(f'<div class="flow-node"><span>0{n+1}</span><strong>{esc(text)}</strong></div>' for n,text in enumerate(nodes))
        panels.append(f'<section class="scenario-panel" data-scenario="{i}"'+(' hidden' if i else '')+f'><h3 class="sr-only">{labels[i]}</h3><div class="flow-nodes">{boxes}</div><p>{esc(step["text"])}</p>{source_link(step["source"],"查看这一分支")}</section>')
    return f'<div class="case-lab"><div class="lab-heading"><h2>一次切换，三种路径。</h2><span>源码流程示意 · 不执行系统命令</span></div><fieldset class="scenario-controls"><legend class="sr-only">选择切换情境</legend>{controls}</fieldset>{"".join(panels)}<p class="lab-footnote">判断依据是 systemd 是否报告 active；写入选择记录和默认服务恢复都可能失败。</p></div>'

def code_excerpt(study):
    snippet=study['snippet']
    return f'''<figure class="case-code"><figcaption><span>src/main.rs · RUST</span>{source_link(snippet['source'],f"L{snippet['startLine']}–L{snippet['endLine']}")}</figcaption><div class="code-wrap"><button class="copy-code" type="button" aria-label="复制源码摘录">复制代码</button><pre tabindex="0"><code>{esc(snippet['code'])}</code></pre></div><p class="code-caption">{esc(snippet['caption'])}</p></figure>'''

def render_case(item, works, posts, visual):
    study=item.get('case_study');headline=esc(item['headline']).replace('\n','<br>')
    sections=[('problem','问题'),('structure','结构'),('tradeoff','取舍'),('result','结果'),('source','源码')]
    toc=''.join(f'<a href="#{key}"><span>0{i}</span>{label}</a>' for i,(key,label) in enumerate(sections,1))
    prose=''
    for n,(key,label) in enumerate(sections[:-1],1):
        extra=code_excerpt(study) if key=='structure' and study else ''
        prose+=f'<section id="{key}" data-reading-section><p class="section-index">0{n} / {key.upper()}</p><h2>{label}<a class="heading-anchor" href="#{key}" aria-label="{label}段落链接">#</a></h2><p>{esc(item[key])}</p>{extra}</section>'
    evidence=''.join(f'<li>{source_link(item["repo"]+"/blob/"+item["revision"]+"/"+path,label)}</li>' for label,path in item['evidence'])
    if study:
        evidence+=''.join(f'<li>{source_link(fact["source"],fact["text"])}</li>' for fact in study['key_evidence'])
    prose+=f'<aside class="limitations"><h3>边界与不足</h3><p>{esc(item["limitation"])}</p></aside><section id="source" data-reading-section><p class="section-index">05 / SOURCE</p><h2>源码与证据<a class="heading-anchor" href="#source" aria-label="源码段落链接">#</a></h2><p>以上说明对应固定版本 <code>{item["revision"][:10]}</code>，不代表对所有运行环境的测试结论。</p><ul class="evidence-list">{evidence}</ul></section>'
    if item['related']:
        prose+='<section class="related"><h2>继续拆开相邻的一层</h2>'
        for slug in item['related']:
            post=posts[slug];prose+=f'<a class="related-item" href="/writing/{slug}/"><strong>{esc(post["title"])}</strong><p>{esc(post["deck"])}</p></a>'
        prose+='</section>'
    idx=next(i for i,w in enumerate(works) if w['slug']==item['slug']);nxt=works[(idx+1)%len(works)]
    lab=shell_lab(study) if study else f'<div class="case-lab general-lab"><div class="lab-heading"><h2>拆开这个系统。</h2><span>结构示意 · 依据公开源码与文档</span></div>{visual(item)}</div>'
    return f'''<div class="reading-progress" role="progressbar" aria-label="案例阅读进度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></div>
<header class="case-hero"><a class="case-back" href="/#selected-work">← 返回作品星系</a><div class="case-orbital-art" aria-hidden="true"><div class="case-orbital-ring"></div><img src="/assets/planets/{item['slug']}.svg" width="400" height="400" alt=""><span>ORBIT / {item['number']}</span></div><div class="case-hero-copy"><p class="case-kicker">PROJECT {item['number']} / {esc(item['category'])}</p><p class="case-repo-name">{esc(item['title'])}</p><h1 aria-label="{esc(item['title'])}：{esc(item['headline'].replace(chr(10),''))}">{headline}</h1><p class="case-deck">{esc(item['summary'])}</p><div class="case-hero-links"><a href="#case-detail">拆开来看 <span aria-hidden="true">↓</span></a>{source_link(item['repo'],'公开源码')}</div></div><div class="case-hero-footer"><span>技术构成 / {esc(item['tech'])}</span><span>FIXED REVISION / {item['revision'][:10]}</span></div></header>
<div id="case-detail" class="case-detail"><div class="case-premise"><span>THE QUESTION</span><p>{esc(item['problem'])}</p></div>{lab}<div class="case-layout"><aside class="local-toc"><p class="eyebrow">项目切面 / {item['number']}</p><nav aria-label="项目目录">{toc}</nav><p class="reading-status">阅读进度 <span>0%</span></p><a class="toc-return" href="/#selected-work">返回星系 ↗</a></aside><article class="prose reading-body">{prose}</article></div></div>
<a class="next-orbit" href="/work/{nxt['slug']}/"><div><span>NEXT ORBIT / 下一个作品</span><strong>{esc(nxt['title'])}</strong><p>{esc(nxt['headline'].replace(chr(10),''))}</p></div><img src="/assets/planets/{nxt['slug']}.svg" width="400" height="400" alt=""><b aria-hidden="true">↗</b></a>'''
