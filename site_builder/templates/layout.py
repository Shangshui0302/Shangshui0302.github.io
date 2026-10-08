"""Persistent site shell; every route shares the same assets and navigation."""
from html import escape as esc


def render_page(config, title, body, active='', description='', is_article=False, stellar=False, is_case=False):
    name, wordmark = config['site_name'], config['wordmark']
    entries = ''.join(
        f'<a href="{href}" data-nav="{slug}"'+(' aria-current="page"' if active == slug else '')+f'>{label}</a>'
        for slug, href, label in [('home', '/', '首页'), ('work', '/work/', '作品'), ('writing', '/writing/', '文章'), ('index', '/index/', '<span class="search-symbol" aria-hidden="true"></span>搜索')])
    body_class = 'orbit-home' if stellar else 'reading-page' if is_article else 'case-page' if is_case else ''
    favicon = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23F1EFE9'/%3E%3Cpath fill='%2317191C' d='M10 10h44v14H10zm0 32h44v12H10z'/%3E%3Cpath fill='%23FF4D2E' d='M10 29h44v8H10z'/%3E%3C/svg%3E"
    return f'''<!doctype html><html class="no-js" lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(name)} / {esc(wordmark)}</title>
<meta name="description" content="{esc(description or config['description'])}"><meta name="referrer" content="no-referrer">
<link rel="icon" type="image/svg+xml" href="{favicon}"><link rel="stylesheet" href="/assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{esc(name)}文章" href="/feed.xml">
<script type="module" src="/assets/js/app.js"></script></head>
<body class="{body_class}" data-section="{active}" data-site-shell>
<a class="skip" href="#main">跳到正文</a>
<header class="topbar wrap"><a class="brand" href="/" aria-label="{esc(name)} {esc(wordmark)} 首页"><span class="brand-mark" aria-hidden="true"></span>{esc(wordmark)}<span>{esc(name)}</span></a>
<nav aria-label="主导航">{entries}</nav><div class="nav-actions"><button class="motion" type="button" aria-pressed="false">减少动效</button></div></header>
<main id="main" tabindex="-1">{body}</main>
<footer class="footer wrap"><div><a class="footer-brand" href="/">{esc(wordmark)} / {esc(name)}</a><p class="footer-note">作品与文章，按问题组织。</p></div><div class="footer-links"><a href="{config['github_url']}" target="_blank" rel="noopener noreferrer">GitHub</a><a href="/feed.xml">RSS</a><a href="/index/">搜索与目录</a></div><span class="mono">© {config['year']} {esc(wordmark)}</span></footer>
<div class="route-status sr-only" role="status" aria-live="polite"></div>
<div class="route-error" role="alert" hidden><p>页面未能加载，请重试。</p><button type="button" data-route-retry>重新加载</button><a data-route-open data-native>直接打开</a><button type="button" data-route-dismiss aria-label="关闭">×</button></div>
</body></html>'''
