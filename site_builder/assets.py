"""Join local CSS imports at build time; no package manager or runtime bundler."""
from pathlib import Path
import re

IMPORT = re.compile(r'@import\s+url\([\'"]?([^\'"\)]+)[\'"]?\);')
URL = re.compile(r'url\(([\'"]?)([^\'"\)]+)\1\)')


def bundle_styles(root):
    def read(path, parents=()):
        path = path.resolve()
        if path in parents or not path.is_relative_to(root.resolve()):
            raise ValueError(f'Invalid stylesheet import: {path.name}')
        source = path.read_text()
        # Resolve asset URLs before nesting styles from another directory.
        def asset(match):
            value = match[2]
            if value.startswith(('/', 'data:', 'https:')) or value.endswith('.css'):
                return match[0]
            target = (path.parent / value).resolve()
            return f'url("/{target.relative_to(root)}")'
        source = URL.sub(asset, source)
        return IMPORT.sub(lambda m: read(path.parent / m[1], (*parents, path)), source)
    return read(root / 'assets/css/site.css')
