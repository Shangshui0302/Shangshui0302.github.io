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


def select_home_content(config, works, posts):
    """Editorial placement is explicit and independent of the publication allowlist."""
    def select(slugs, items, label):
        available = {item['slug']: item for item in items}
        if not isinstance(slugs, list) or not slugs or any(not isinstance(slug, str) for slug in slugs):
            raise ValueError(f'Invalid homepage {label}')
        if len(set(slugs)) != len(slugs) or not set(slugs) <= available.keys():
            raise ValueError(f'Duplicate or unknown homepage {label}')
        return [available[slug] for slug in slugs]

    hero, *features = select([config['featured_work'], *config['work']], works, 'work')
    return hero, features, select(config['writing'], posts, 'writing')


def validate_case_studies(works):
    for work in works:
        study = work.get('case_study')
        if not study:
            continue
        for key in ('heading', 'note'):
            if not isinstance(study.get(key), str) or not study[key].strip():
                raise ValueError(f'Missing case {key}: {work["slug"]}')
        steps = study.get('steps')
        if not isinstance(steps, list) or not steps:
            raise ValueError(f'Missing case scenarios: {work["slug"]}')
        ids = set()
        for step in steps:
            key = step.get('id', '')
            if not re.fullmatch(r'[a-z0-9-]+', key) or key in ids:
                raise ValueError(f'Invalid case scenario id: {work["slug"]}')
            ids.add(key)
            for field in ('title', 'control_label', 'text', 'source'):
                if not isinstance(step.get(field), str) or not step[field].strip():
                    raise ValueError(f'Missing scenario {field}: {key}')
            nodes = step.get('nodes')
            if not isinstance(nodes, list) or not nodes or any(not isinstance(node, str) or not node.strip() for node in nodes):
                raise ValueError(f'Invalid scenario nodes: {key}')
