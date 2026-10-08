"""RSS includes only curated articles and their public taxonomy."""
from xml.etree.ElementTree import Element, SubElement, ElementTree
from .templates.components import url

def render_feed(config, posts, taxonomy):
    site_name, wordmark = config["site_name"], config["wordmark"]
    # All feed entries are explicitly allowlisted. Preview uses local URLs until approved publication.
    origin=(config.get('site_url') or 'http://127.0.0.1:4173').rstrip('/')
    rss=Element('rss',{'version':'2.0'});channel=SubElement(rss,'channel')
    for key,value in [('title',f'{site_name} / {wordmark}'),('link',origin+'/writing/'),('description',config['description']),('language','zh-cn')]:SubElement(channel,key).text=value
    for post in posts:
        node=SubElement(channel,'item')
        for key,value in [('title',post['title']),('link',origin+url('writing',post)),('guid',origin+url('writing',post)),('description',post['deck'])]:SubElement(node,key).text=value
        SubElement(node,'category').text=taxonomy['categories'][post['category_id']]['label']
        for tag in post['tags']:SubElement(node,'category').text=taxonomy['tags'][tag]
    return ElementTree(rss)
