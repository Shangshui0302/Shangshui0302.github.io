"""Build-time localization. Original article HTML and stable route IDs are preserved."""
from copy import deepcopy
from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from .article_translation import apply_translation
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STRINGS = json.loads((ROOT / 'public-content/translations/en/ui.json').read_text())


def text_en(value):
    stripped = value.strip()
    if not stripped:
        return value
    result = STRINGS.get(stripped)
    if stripped == '1 篇文章':
        result = '1 article'
    if result is None and stripped.endswith('段落链接'):
        result = 'Link to section: ' + text_en(stripped[:-4])
    if result is None:
        patterns = [
            (r'(\d+) 篇文章', r'\1 articles'),
            (r'(\d+) 项内容', r'\1 items'),
            (r'全部 (\d+) 个项目', r'All \1 projects'),
            (r'(\d+) 个专题 / (\d+) 篇文章', r'\1 reading paths / \2 articles'),
            (r'READING PATH / (\d+) 篇', r'READING PATH / \1 ARTICLES'),
            (r'DOSSIER (\d+) / (\d+) 篇文章', r'DOSSIER \1 / \2 ARTICLES'),
            (r'专题 / (\d+) 篇', r'Reading path / \1 articles'),
            (r'约 (\d+) 分钟阅读', r'About \1 min read'),
            (r'整理于 (.+)', r'Edited \1'),
            (r'与 (.+) 相关的文章。', r'Articles about \1.'),
            (r'(.+) 标签', r'\1 tag'),
            (r'项目切面 / (.+)', r'PROJECT ANATOMY / \1'),
            (r'技术构成 / (.+)', r'Built with / \1'),
            (r'收藏形式 / (.+)', r'Format / \1'),
            (r'探索 (.+)', r'Explore \1'),
            (r'查看 (.+) 的项目原图', r'View the original project image for \1'),
            (r'查看 (.+) 的收藏原图', r'View the original collection image: \1'),
            (r'(.+)段落链接', r'Link to section: \1'),
        ]
        for pattern, replacement in patterns:
            if re.fullmatch(pattern, stripped):
                result = re.sub(pattern, replacement, stripped)
                break
    if result is None:
        result = stripped
    # Already-English source fragments still use Chinese punctuation in places.
    # Normalize prose punctuation only; code and original-language regions are skipped.
    if not re.search(r'[\u3400-\u9fff]', result):
        result = result.translate(str.maketrans({'，': ', ', '。': '.', '：': ': ', '；': '; ',
                                               '！': '!', '？': '?', '（': '(', '）': ')',
                                               '【': '[', '】': ']'}))
    return value[:len(value) - len(value.lstrip())] + result + value[len(value.rstrip()):]


def english_route(value):
    """Localize page routes only; never rewrite assets, sources, fragments or RSS."""
    if value.startswith('//') or not value.startswith('/'):
        return value
    path = value.split('?', 1)[0].split('#', 1)[0]
    if path == '/' or re.match(r'^/(?:work|writing|journal|topics|index)(?:/|$)', path):
        return '/en' + value
    return value


def canonical_route(value):
    """Legacy preview URLs stay navigable but point search engines to the primary route."""
    if value.startswith('/journal/'):
        return '/writing/' + value[len('/journal/'):]
    if value == '/topics/' or value.startswith('/topics/'):
        return '/writing/topics/' + value[len('/topics/'):]
    return value


def localized_content(works, posts, topics, taxonomy, require_complete=False):
    sources = json.loads((ROOT / 'public-content/translations/en/sources.json').read_text())
    def digest(value):
        return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    for kind, items in [('work', works), ('writing', posts), ('topics', topics)]:
        assert set(sources[kind]) == {item['slug'] for item in items}, f'English source coverage mismatch: {kind}'
        for item in items:
            value = {key: item[key] for key in ('title', 'deck', 'category')} if kind == 'writing' else item
            if sources[kind][item['slug']] != digest(value):
                raise ValueError(f'Stale English {kind} metadata: {item["slug"]}')
    if sources['taxonomy'] != digest(taxonomy):
        raise ValueError('Stale English taxonomy metadata')
    project_data = json.loads((ROOT / 'public-content/translations/en/work.json').read_text())
    catalog = json.loads((ROOT / 'public-content/translations/en/catalog.json').read_text())
    assert set(project_data) == {item['slug'] for item in works}, 'English project coverage mismatch'
    assert set(catalog['writing']) == {item['slug'] for item in posts}, 'English article metadata coverage mismatch'
    assert set(catalog['topics']) == {item['slug'] for item in topics}, 'English topic coverage mismatch'
    en_posts = []
    for post in posts:
        path = ROOT / 'public-content/translations/en/articles' / (post['slug'] + '.json')
        if path.exists():
            translated = apply_translation(post, json.loads(path.read_text()))
        elif require_complete:
            raise ValueError(f'Missing full English translation: {post["slug"]}')
        else:
            translated = {**deepcopy(post), 'body_language': 'zh-CN'}
        en_posts.append({**translated, **catalog['writing'][post['slug']]})
    return ([project_data[item['slug']] for item in works], en_posts,
            [catalog['topics'][item['slug']] for item in topics], catalog['taxonomy'])


def translate_html(source):
    """Translate text/labels and route attributes without touching code or original prose.

    Source-position edits preserve markup and entities exactly outside changed text.
    A protected lang region declares original Chinese copy honestly on English pages.
    """
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    edits, stack = [], []
    attribute = re.compile(r'''(\s([\w-]+)\s*=\s*)(?:"([^"]*)"|'([^']*)'|([^\s>]+))''')
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    class Translator(HTMLParser):
        def position(self):
            line, column = self.getpos()
            return offsets[line - 1] + column

        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            protected = (stack[-1][1] if stack else False) or 'data-original-content' in values or tag in ('script', 'style', 'code', 'pre')
            if tag not in void:
                stack.append((tag, protected))
            original = self.get_starttag_text()
            in_code = any(name in ('script', 'style', 'code', 'pre') for name, _ in stack)
            def replace(match):
                name = match[2]
                raw = next(value for value in match.groups()[2:] if value is not None)
                value = unescape(raw)
                changed = value
                if name in ('href', 'action') and not in_code and 'data-language' not in values and tag not in ('link',):
                    changed = english_route(value)
                elif name in ('aria-label', 'title', 'placeholder', 'alt') and not protected:
                    changed = text_en(value)
                return match[0] if changed == value else match[1] + '"' + escape(changed, quote=True) + '"'
            changed = attribute.sub(replace, original)
            if changed != original:
                start = self.position()
                edits.append((start, start + len(original), changed))

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag not in void:
                self.handle_endtag(tag)

        def handle_endtag(self, tag):
            for index in range(len(stack) - 1, -1, -1):
                if stack[index][0] == tag:
                    del stack[index:]
                    break

        def handle_data(self, data):
            if stack and stack[-1][1]:
                return
            changed = text_en(unescape(data))
            if changed != unescape(data):
                start = self.position()
                edits.append((start, start + len(data), escape(changed, quote=False)))

    parser = Translator(convert_charrefs=False)
    parser.feed(source)
    parser.close()
    for start, end, changed in reversed(edits):
        source = source[:start] + changed + source[end:]
    return source
