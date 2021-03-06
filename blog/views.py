from . import app
from flask import render_template, request, redirect, abort
from datetime import datetime
from rfeed import *
from .syncdb import get_essay, get_all_titles, get_tag_links
from .models import get_resources_url_path, random_slogan
from .backward import OLD_TITLES


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def home():
    titles = get_all_titles()
    if not titles:
        app.logger.error("NO ESSAYS EXISTS!")
        abort(404)
    doc = get_essay(titles[0])
    return render_template(
        'essay.html',
        url=request.base_url,
        doc=doc,
        page_title="Tian Jun",
        activate="essays",
        resources=get_resources_url_path(titles[0]))


@app.route('/essays/<title>')
def gen_essay(title):
    if title in OLD_TITLES:
        return redirect('/essays/' + OLD_TITLES[title], 301)
    doc = get_essay(title)
    if not doc:
        abort(404)
    return render_template(
        'essay.html',
        url=request.base_url,
        doc=doc,
        activate="essays",
        slogan=random_slogan(),
        resources=get_resources_url_path(title))


@app.route('/essays/<title>/')
def old_gen_essay(title):
    return redirect('/essays/' + title, 301)


@app.route('/search')
def search():
    tag = request.args.get('tag', '')
    links = get_tag_links(tag)
    return render_template('search.html', tag=tag, links=links)


@app.route('/about')
def about():
    return render_template('about.html', activate="about")


@app.route('/about/')
def old_about():
    return redirect('/about', 301)


@app.route('/rss')
def rss():
    items = []
    for title in get_all_titles()[:5]:
        doc = get_essay(title)
        items.append(Item(
            title=doc['title'],
            link="https://tianjun.me/essays/" + title,
            description=doc['body'],
            author="Jun Tian",
            guid=Guid(title),
            pubDate=datetime.strptime(doc['update_time'], '%Y-%m-%d %H:%M:%S')))
    feed = Feed(
        title="Tian Jun",
        link="https://tianjun.me/rss",
        description="All about Tian Jun",
        language="en-US",
        lastBuildDate=datetime.now(),
        items=items)
    return feed.rss()


@app.route('/rss/')
def old_rss():
    return redirect('/rss', 301)
