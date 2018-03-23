from . import app
import os
import random


def get_resources_url_path(title):
    essay_dir = os.path.join(app.static_folder,
                             app.config['ESSAY_RESOURCE_FOLDER'],
                             title)
    if os.path.exists(essay_dir):
        resources = []
        for f in os.listdir(essay_dir):
            f_path = '/'.join([app.static_url_path,
                               app.config['ESSAY_RESOURCE_FOLDER'],
                               title,
                               f])
            f = f + '/' if os.path.isdir(f_path) else f
            resources.append((f, f_path))
        return resources
    else:
        return []


def random_slogan():
    return random.choice([
        'Any Similarity is Misleading',
        'All Models are Wrong, but Some are Useful'
         ])
