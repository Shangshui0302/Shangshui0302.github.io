"""Explicit release checks; local preview may still use a loopback origin."""
from ipaddress import ip_address
from urllib.parse import urlsplit
from .urls import normalize_site_url


def release_origin(config):
    value = config.get('site_url')
    if not isinstance(value, str):
        raise ValueError('Release requires a public HTTPS site_url in site_config.json')
    value = normalize_site_url(value)
    url = urlsplit(value)
    host = url.hostname or ''
    if (url.scheme != 'https' or not host or '.' not in host or url.username or url.password
            or url.query or url.fragment or url.port not in (None, 443)
            or host.endswith(('.localhost', '.local', '.test', '.invalid', '.example'))
            or host in ('example.com', 'example.org', 'example.net')):
        raise ValueError('site_url must be a public HTTPS origin without a query or credentials')
    try:
        address = ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError('Release site_url cannot use a private or loopback address')
    return value.rstrip('/')


def check_release_output(output, config):
    release_origin(config)
    allowed = {'en', 'assets', 'work', 'writing', 'journal', 'topics', 'index', 'index.html', 'feed.xml'}
    for path in output.iterdir():
        if path.name not in allowed:
            raise ValueError(f'Unexpected release output: {path.name}')
    for path in output.rglob('*'):
        if path.is_symlink() or any(part.startswith('.') for part in path.relative_to(output).parts):
            raise ValueError(f'Private or linked release output: {path.relative_to(output)}')

