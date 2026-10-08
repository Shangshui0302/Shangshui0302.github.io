"""Source-backed diagrams and selected images from the public collection."""
from html import escape as esc


def kanban_diagram():
    return '''<figure class="kanban-figure"><div class="kanban-caption"><span>GITHUB KANBAN</span><span>INFORMATION / AT A GLANCE</span></div><div class="kanban-lanes"><div><span>01 / INBOX</span><h3>哪些事找到了我</h3><p>通知与未读状态</p><p>等待审阅的 PR</p></div><div><span>02 / ACTIVITY</span><h3>哪些事正在发生</h3><p>PR · Issues · Actions</p><p>关注动态与发布</p></div><div><span>03 / CONTEXT</span><h3>回到具体的项目</h3><p>贡献日历与仓库</p><p>打开对应 GitHub 页面 ↗</p></div></div><figcaption>信息分组示意，非账户数据或运行截图。通知同步行为由插件设置决定。</figcaption></figure>'''


def wallpaper_gallery(item):
    tiles=[]
    for i,picture in enumerate(item['gallery'],1):
        source=f"{item['repo']}/blob/{item['revision']}/{picture['file']}"
        tiles.append(f'''<figure class="wallpaper-tile"><a href="{esc(source)}" target="_blank" rel="noopener noreferrer" aria-label="查看 {esc(picture['title'])} 的收藏原图"><img src="/assets/wallpapers/{esc(picture['file'])}" width="{picture['width']}" height="{picture['height']}" loading="lazy" decoding="async" alt="{esc(picture['alt'])}"><span aria-hidden="true">↗</span></a><figcaption><span>{i:02d} / {esc(picture['title'])}</span><span>{picture['width']} × {picture['height']}</span></figcaption></figure>''')
    return '<div class="wallpaper-gallery">'+''.join(tiles)+'</div><p class="collection-credit">个人壁纸收藏 · 图像版权归各自权利人。点击图片查看公开仓库中的原图。</p>'
