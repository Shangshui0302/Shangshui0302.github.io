"""Render the shared galaxy cover using the existing public project allowlist."""
from html import escape
import json

def render_stellar(root):
    slugs=json.loads((root/'public-content/manifest.json').read_text())['work']
    nodes=[]
    for i,slug in enumerate(slugs):
        item=json.loads((root/'public-content/work'/f'{slug}.json').read_text())
        planet=escape(item.get('planet',slug))
        nodes.append(f'''<a class="orbit-node" href="/work/{escape(slug)}/" data-planet="{i}" aria-label="探索 {escape(item['title'])}"><span class="planet-index">{i+1:02d} / {escape(item['category'])}</span><span class="planet-body"><img src="/assets/planets/{planet}.svg" width="400" height="400" alt=""><span class="planet-reticle" aria-hidden="true"></span></span><span class="planet-name">{escape(item['title'])}<span aria-hidden="true">↗</span></span><span class="planet-summary">{escape(item['summary'])}</span></a>''')
    return (root/'components/stellar.html').read_text().replace('<!-- PROJECT_PLANETS -->',''.join(nodes)).replace('<!-- PROJECT_COUNT -->',str(len(slugs)))
