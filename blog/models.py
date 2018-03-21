from . import app
import os
import random


def get_resources_url_path(title):
    essay_dir = os.path.join(app.static_folder,
                             app.config['ESSAY_RESOURCE_FOLDER'],
                             title)
    if os.path.exists(essay_dir):
        return [[f, '/'.join([app.static_url_path,
                              app.config['ESSAY_RESOURCE_FOLDER'],
                              title,
                              f])]
                for f in os.listdir(essay_dir)]
    else:
        return []


def random_slogan():
    return random.choice([
        'Any Similarity Is Misleading',
        'All Models Are Wrong But Some Are Useful',
        'A Goal Without A Plan Is Just A Wish',
        'To Think Is To Forget Details, Generalize, Make Abstractions'
    ])
