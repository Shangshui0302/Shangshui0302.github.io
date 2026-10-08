"""README previews first, with source-backed diagrams as a fallback."""
from html import escape as esc
from .exhibits import kanban_diagram, wallpaper_gallery

def project_preview(item):
    preview=item['preview']
    pictures=''.join(f'<a href="{esc(image["source"])}" target="_blank" rel="noopener noreferrer" aria-label="查看 {esc(item["title"])} 的项目原图"><img src="{esc(image["src"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["alt"])}" loading="lazy" decoding="async"></a>' for image in preview['images'])
    return f'<figure class="project-preview"><div class="project-preview-images">{pictures}</div><figcaption><span>{esc(preview["caption"])}</span><a href="{esc(preview["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(preview["source_label"])} ↗</a></figcaption></figure>'

def shell_diagram():
    return '''<div class="system-diagram" role="img" aria-label="结构示意：停止已注册服务，启动目标服务，确认 active 后尝试记录选择。停止确认超时或启动命令失败时尝试默认服务。"><div class="diagram-nodes"><div class="diagram-node"><small>01 / STOP</small><strong>停止旧服务<br>确认非 active</strong></div><div class="diagram-node"><small>02 / START</small><strong>启动目标<br>等待 active</strong></div><div class="diagram-node"><small>03 / RECORD</small><strong>确认状态<br>尝试记录</strong></div></div><div class="diagram-note" aria-hidden="true"></div><p class="diagram-legend">停止确认超时 / 启动命令失败时尝试默认服务；active 等待超时仅报错。</p></div>'''

def theme_diagram():
    return '''<figure class="theme-figure"><div class="figure-heading"><span>色板 / 模板 / 候选窗</span><span>FCITX5 × MATUGEN</span></div><div class="theme-flow"><div class="color-input"><span class="swatch" style="--swatch:#d3bea0">primary</span><span class="swatch" style="--swatch:#221b11">on_primary</span></div><div class="map-line" aria-hidden="true"></div><div class="candidate-example"><span>pian yi</span><div class="candidate-row"><b>1 偏移</b><span>2 便宜</span></div></div></div><figcaption class="figcaption">映射示意，非运行截图。高亮背景与文字成对生成，布局沿用主题结构。</figcaption></figure>'''

def skills_diagram():
    return '''<figure class="skills-figure"><div class="figure-heading"><span>验证层次</span><span>每一步，只证明它自己。</span></div><div class="skills-lines"><div><strong>能求值</strong><span>EVALUATE</span></div><div><strong>能构建</strong><span>BUILD</span></div><div><strong>正在运行</strong><span>VERIFY RUNTIME</span></div></div><figcaption class="figcaption">构建结果与现场结果分开记录；激活需要单独授权。</figcaption></figure>'''

def nix_diagram():
    return '''<div class="system-diagram" role="img" aria-label="锁定输入经过 flake 主机入口，组合系统与用户模块。"><div class="diagram-nodes"><div class="diagram-node"><small>01 / INPUTS</small><strong>锁定输入</strong></div><div class="diagram-node"><small>02 / FLAKE</small><strong>主机入口</strong></div><div class="diagram-node"><small>03 / MODULES</small><strong>系统层 / 用户层</strong></div></div><p class="diagram-legend">配置结构示意；不代表所有模块已现场激活。</p></div>'''

def visual(item):
    if item.get('preview'):return project_preview(item)
    if item['visual']=='kanban':return kanban_diagram()
    if item['visual']=='wallpapers':return wallpaper_gallery(item)
    return {'shell':shell_diagram,'theme':theme_diagram,'skills':skills_diagram,'nix':nix_diagram}[item['visual']]()
