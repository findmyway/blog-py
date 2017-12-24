"""Provide usefule functions for create-read-update-delete in redis

Data Structures in Redis:

    prefix:ESSAY:{ESSAY_TITLE}
        type: hash_map
        example: {'body': 'This content',
                  'toc': 'Table of content',
                  'create_time': '2017-12-12',
                  'update_time': '2017-12-12',
                  'tags': 'Tag1,Tag2,...'}

    prefix:TAG_LINKS:{TAG}
        type: sorted_set
        example: {(update_timestamp, ESSAY_TITLE), ...}
    
    prefix:ALL_ESSAYS
        type: sorted_set
        example: {(update_timestamp, ESSAY_TITLE), ...}
"""

import logging
import os
from collections import Counter
from datetime import datetime

import redis

from .parser import parse_html

PREFIX = "juntian.me:"
ALL_ESSAYS_KEY = PREFIX + 'ALL_ESSAYS'

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def essay_key_wrapper(title):
    return PREFIX + 'ESSAY:' + title


def tag_links_key_wrapper(tag):
    return PREFIX + 'TAG_LINKS:' + tag


def get_all_titles():
    return [' '.join(t.decode().split('_'))
            for t in r.zrevrange(ALL_ESSAYS_KEY, 0, -1)]


def get_tags(title):
    tags = r.hmget(essay_key_wrapper(title), 'tags')[0]
    return set(tags.decode().split(',')) if tags else set()


def get_tags_count():
    """TODO: use cache here"""
    c = Counter()
    for title in r.zrevrange(ALL_ESSAYS_KEY, 0, -1):
        c.update(get_tags(title.decode()))
    return c.most_common()


def get_tag_links(tag):
    """search for the tag in all essays
    TODO: Cache or use hash here.
    """
    return [t.decode()
            for t in r.zrevrange(ALL_ESSAYS_KEY, 0, -1)
            if tag in get_tags(t.decode())]


def get_essay(title):
    doc = {k.decode(): v.decode() for k, v in
           r.hgetall(essay_key_wrapper(title)).items()}
    if doc:
        doc['title'] = ' '.join(title.split('_'))
        doc['all_titles'] = get_all_titles()
        doc['all_tags'] = get_tags_count()
        return doc
    else:
        return {}


def remove_essay(title):
    """delete an existing essay"""
    doc = get_essay(title)
    tags = set(doc['tags'].split(',')) if 'tags' in doc else set()

    r.delete(essay_key_wrapper(title))
    r.zrem(ALL_ESSAYS_KEY, title)
    for t in tags:
        r.zrem(tag_links_key_wrapper(t), title)


def update_essay(path):
    """update an existing essay"""
    now = datetime.now()

    title = os.path.basename(os.path.dirname(path))
    old_doc = get_essay(title)

    new_doc = parse_html(path)
    new_doc['update_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    if not old_doc:
        new_doc['create_time'] = now.strftime('%Y-%m-%d %H:%M:%S')

    old_tags = set(old_doc['tags'].split(',')) \
        if old_doc.get('tags') else set()
    new_tags = set(new_doc['tags'].split(',')) \
        if new_doc.get('tags') else set()

    logging.debug('old tags: [%s], new tags: {%s}', old_tags, new_tags)
    if old_tags != new_tags:
        # bind new tag
        for t in new_tags - old_tags:
            r.zadd(tag_links_key_wrapper(t), now.timestamp(), title)
        # del old binded essays
        for t in old_tags - new_tags:
            r.zrem(tag_links_key_wrapper(t), title)
    r.hmset(essay_key_wrapper(title), new_doc)
    r.zadd(ALL_ESSAYS_KEY, now.timestamp(), title)
