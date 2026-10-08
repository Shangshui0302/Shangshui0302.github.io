"""A versioned full-text index, loaded independently of the directory HTML."""
from hashlib import sha256
from html import unescape
import json
import re
from .templates.components import url


def write_search_index(output, works, posts, topics, taxonomy):
    records = []
    for kind, items in [('work', works), ('writing', posts), ('topics', topics)]:
        for item in items:
            text = ' '.join(str(item.get(key, '')) for key in (
                'title', 'summary', 'deck', 'description', 'category', 'tech',
                'problem', 'structure', 'tradeoff', 'result', 'body'))
            text = unescape(re.sub('<[^>]+>', ' ', text))
            if kind == 'writing':
                text += ' ' + taxonomy['categories'][item['category_id']]['label']
                text += ' ' + ' '.join(taxonomy['tags'][tag] for tag in item['tags'])
            records.append({'url': url('writing/topics' if kind == 'topics' else kind, item),
                            'text': re.sub(r'\s+', ' ', text).strip()})
    payload = json.dumps(records, ensure_ascii=False, separators=(',', ':'))
    path = 'assets/search-' + sha256(payload.encode()).hexdigest()[:16] + '.json'
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    (output / path).write_text(payload)
    return '/' + path
