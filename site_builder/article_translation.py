"""Lossless article translation slots: markup, code and technical tokens are immutable."""
from dataclasses import dataclass, field
from hashlib import sha256
from html.parser import HTMLParser
from html import unescape
import json
import re

BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'figcaption', 'dt', 'dd'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
HAN = re.compile(r'[\u3400-\u9fff]')

@dataclass
class Node:
    tag: str
    start: int
    inner_start: int
    end: int = 0
    inner_end: int = 0
    protected: bool = False
    children: list = field(default_factory=list)


def extract_segments(body):
    offsets = [0]
    for line in body.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    root = Node('root', 0, 0, len(body), len(body))
    stack = [root]
    class Parser(HTMLParser):
        def position(self):
            line, column = self.getpos()
            return offsets[line - 1] + column
        def handle_starttag(self, tag, attrs):
            start = self.position()
            node = Node(tag, start, start + len(self.get_starttag_text()), protected=stack[-1].protected or tag in ('pre', 'code', 'script', 'style'))
            stack[-1].children.append(node)
            if tag not in VOID:
                stack.append(node)
            else:
                node.end = node.inner_end = node.inner_start
        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag not in VOID:
                node = stack.pop(); node.inner_end = node.end = node.inner_start
        def handle_endtag(self, tag):
            for index in range(len(stack) - 1, 0, -1):
                if stack[index].tag == tag:
                    node = stack[index]; node.inner_end = self.position(); node.end = body.find('>', node.inner_end) + 1
                    del stack[index:]; break
        def handle_data(self, data):
            start = self.position()
            stack[-1].children.append(Node('#text', start, start, start+len(data), start+len(data), stack[-1].protected))
    Parser(convert_charrefs=False).feed(body)
    def has_block(node):
        return any(child.tag in BLOCKS or has_block(child) for child in node.children)
    segments=[]
    def visit(node):
        if node.protected:
            return
        if node.tag in BLOCKS and not has_block(node):
            source = body[node.inner_start:node.inner_end]
            # Chinese comments inside code remain untouched and do not create slots.
            prose = re.sub(r'<(?:pre|code)\b[^>]*>[\s\S]*?</(?:pre|code)>', '', source)
            if HAN.search(re.sub('<[^>]*>', '', prose)):
                segments.append((node.inner_start, node.inner_end, source))
            return
        if node.tag == '#text':
            source = body[node.start:node.end]
            if HAN.search(source):
                segments.append((node.start, node.end, source))
        for child in node.children:
            visit(child)
    visit(root)
    return segments


def source_digest(post):
    return sha256(json.dumps({key:post[key] for key in ('body', 'sections', 'refs')}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def markup_signature(value):
    """Preserve tag order/attributes, code, URLs and placeholder tokens exactly."""
    tags = re.findall(r'<[^>]*>', value)
    codes = re.findall(r'<code\b[^>]*>[\s\S]*?</code>', value)
    return tags, codes


def apply_translation(post, record):
    if record.get('source_sha256') != source_digest(post):
        raise ValueError(f'Stale English translation: {post["slug"]}')
    segments = extract_segments(post['body'])
    translations = record['segments']
    if len(translations) != len(segments):
        raise ValueError(f'Translation slot mismatch: {post["slug"]}')
    body = post['body']
    for i, ((start, end, source), translated) in reversed(list(enumerate(zip(segments, translations)))):
        if not isinstance(translated, str) or not translated.strip():
            raise ValueError(f'Empty translation: {post["slug"]} slot {i}')
        if markup_signature(source) != markup_signature(translated):
            raise ValueError(f'Changed article markup/code: {post["slug"]} slot {i}')
        body = body[:start] + translated + body[end:]
    refs = record['reference_labels']
    if len(refs) != len(post['refs']):
        raise ValueError(f'Reference translation mismatch: {post["slug"]}')
    sections = [(anchor, unescape(label)) for anchor, label in re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', body)]
    if [x[0] for x in sections] != [x[0] for x in post['sections']]:
        raise ValueError(f'Changed article outline: {post["slug"]}')
    return {**post, 'body': body, 'sections': sections, 'refs': [[label, original[1]] for label,original in zip(refs,post['refs'])], 'body_language':'en'}
