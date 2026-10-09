"""Shared build/check URL configuration, without changing the saved deployment target."""
from html import escape, unescape
from html.parser import HTMLParser
import json
import os
import re
from urllib.parse import urlsplit


def normalize_site_url(value):
    if not isinstance(value, str) or not value:
        raise ValueError('site_url must be an absolute HTTP(S) URL')
    parsed = urlsplit(value)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or re.search(r'[\s\\]', value)):
        raise ValueError('site_url must be an HTTP(S) URL without credentials, query or fragment')
    # A conservative, unambiguous mount path works on Pages and custom domains.
    path = parsed.path.rstrip('/')
    if path and (not re.fullmatch(r'(?:/[A-Za-z0-9._~-]+)+', path)
                 or any(part in ('.', '..') for part in path.split('/'))):
        raise ValueError('site_url contains an invalid mount path')
    parsed.port  # Validate malformed port numbers before any files are written.
    return parsed._replace(path=path).geturl()


def load_config(root, site_url=None):
    config = json.loads((root / 'site_config.json').read_text())
    config['site_url'] = normalize_site_url(
        site_url if site_url is not None else os.environ.get('SITE_URL', config.get('site_url') or 'http://127.0.0.1:4173'))
    return config


class SiteURLs:
    def __init__(self, site_url):
        self.site_url = normalize_site_url(site_url)
        self.base_path = urlsplit(self.site_url).path

    def mount(self, value):
        """Mount root-local URLs exactly once; preserve external/relative URLs."""
        if not self.base_path or not value.startswith('/') or value.startswith('//'):
            return value
        path = urlsplit(value).path
        if path == self.base_path or path.startswith(self.base_path + '/'):
            return value
        return self.base_path + value

    def local_path(self, value):
        """Map a mounted URL path back to dist; reject links outside the mount."""
        path = urlsplit(value).path
        if not path.startswith('/') or path.startswith('//'):
            raise ValueError(f'Expected an absolute local path: {value}')
        if self.base_path:
            if path == self.base_path:
                return ''
            if not path.startswith(self.base_path + '/'):
                raise ValueError(f'URL escapes site mount: {value}')
            path = path[len(self.base_path):]
        return path.lstrip('/')

    def html(self, source):
        """Rewrite only actual URL attributes, preserving scripts, prose and markup.

        Templates and curated body HTML use logical root-local routes. Parsing tag
        positions avoids changing escaped code examples or JavaScript strings.
        """
        if not self.base_path:
            return source
        urls = self
        offsets = [0]
        for line in source.splitlines(keepends=True):
            offsets.append(offsets[-1] + len(line))
        edits = []
        attribute = re.compile(r'''(\s(?:href|src|action|poster|data-search-index)\s*=\s*)(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', re.I)

        class Rewriter(HTMLParser):
            def handle_starttag(self, tag, attrs):
                original = self.get_starttag_text()
                def replace(match):
                    raw = next(value for value in match.groups()[1:] if value is not None)
                    value = unescape(raw)
                    mounted = urls.mount(value)
                    return match[0] if mounted == value else match[1] + '"' + escape(mounted, quote=True) + '"'
                changed = attribute.sub(replace, original)
                if changed != original:
                    line, column = self.getpos()
                    start = offsets[line - 1] + column
                    edits.append((start, start + len(original), changed))
            handle_startendtag = handle_starttag

        parser = Rewriter(convert_charrefs=False)
        parser.feed(source)
        parser.close()
        for start, end, changed in reversed(edits):
            source = source[:start] + changed + source[end:]
        return source
