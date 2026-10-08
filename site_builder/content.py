"""Load only reviewed JSON records, never private source material."""
import json
import re

def read_content(root, manifest, kind):
    items = []
    for slug in manifest[kind]:
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError('Invalid allowlist slug')
        item = json.loads((root / 'public-content' / kind / (slug + '.json')).read_text())
        assert item['slug'] == slug
        items.append(item)
    return items
