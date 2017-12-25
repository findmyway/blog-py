from . import app
from flask import render_template, request, redirect, abort
from .syncdb import get_essay, get_all_titles, get_tag_links
from .models import get_resources_url_path, random_slogan
from .backward import OLD_TITLES


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
        return redirect(
            '/essays/' + OLD_TITLES[title] + '?disqus_id=' + title,
            301)
    doc = get_essay(title)
    if not doc:
        abort(404)
    return render_template(
        'essay.html',
        url=request.base_url,
        disqus_id=request.args.get('disqus_id', title),
        doc=doc,
        activate="essays",
        slogan=random_slogan(),
        resources=get_resources_url_path(title))


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
    return ""


@app.route('/rss/')
def old_rss():
    return redirect('/rss', 301)
