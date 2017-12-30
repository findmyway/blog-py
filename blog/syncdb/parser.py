import os
from bs4 import BeautifulSoup

RESOURCE_URL_PREFIX = '/static/essay_resources'
KNOWN_LANGS = ['python', 'julia']


def refactor_code(soup):
    """add "language-" prefix to code attribute
    change
    `<pre class="python">` 
    into 
    `<pre class="language-python">`
    """
    for s in soup.find_all('pre'):
        if s.code and 'class' in s.attrs:
            s['class'] = ['language-' + x
                          if x in KNOWN_LANGS else x
                          for x in s['class']]


def refactor_url(soup, title):
    """add prefix to local resources"""
    # img
    for s in soup.find_all('img'):
        if not s['src'].startswith('http'):
            s['src'] = '/'.join([RESOURCE_URL_PREFIX, title, s['src']])
    # a href
    for s in soup.find_all('a'):
        if not s['href'].startswith('http'):
            s['href'] = '/'.join([RESOURCE_URL_PREFIX, title, s['href']])


def parse_html(filepath):
    """Parse the rendered html and return a map"""
    title = os.path.basename(os.path.dirname(filepath))

    with open(filepath, encoding='utf8') as fp:
        soup = BeautifulSoup(fp)

    toc_elm = soup.find(id="TOC")
    if toc_elm:
        toc = toc_elm.decode()
        toc_elm.decompose()  # remove toc element from body

    tags = soup.head.find('meta', attrs={'name': 'keywords'})
    if tags:
        tags = tags.attrs['content']

    refactor_code(soup)
    refactor_url(soup, title)
    body = soup.body.decode()

    return {'toc': toc, 'tags': tags, 'body': body}
