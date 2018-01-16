import argparse
import logging
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .crud import remove_essay, update_essay

ESSAY_FILE_NAME = "main.html"
LOG_FILE = "sync.log"


class BlogEventHandler(FileSystemEventHandler):
    """check file change and write the rendered html into redis"""

    def on_moved(self, event):
        if os.path.basename(event.src_path) == ESSAY_FILE_NAME:
            title = os.path.basename(os.path.dirname(event.src_path))
            try:
                remove_essay(title)
                logging.info('Renaming... Deleted essay %s', event.src_path)
                update_essay(event.dest_path)
                logging.info('Renaming... Create essay %s', event.dest_path)
            except Exception:
                logging.error("Failed to rename from [%s] to [%s]",
                              event.src_path,
                              event.dest_path,
                              exc_info=True)
        else:
            logging.debug("[Moved] From [%s] to [%s]",
                          event.src_path, event.dest_path)

    def on_created(self, event):
        logging.debug('[Created] %s', event.src_path)

    def on_deleted(self, event):
        logging.debug('[Deleted] %s', event.src_path)

    def on_modified(self, event):
        if os.path.basename(event.src_path) == ESSAY_FILE_NAME:
            try:
                update_essay(event.src_path)
                logging.info('Updated essay %s', event.src_path)
            except Exception:
                logging.error("Failed to update %s",
                              event.src_path, exc_info=True)
        else:
            logging.debug('[Updated] %s', event.src_path)


def watch(path):
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='[%(levelname)s][%(asctime)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = BlogEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--update', help='''given a html file path and
        update the renderd result in redis''')
    group.add_argument('-w', '--watch', help='''given a dir and
        watch file changes(update/delete), then update rendered result in redis''')
    group.add_argument('-d', '--delete', help='delete the TITLE in redis')
    args = parser.parse_args()

    if args.watch:
        watch(args.watch)
    elif args.update:
        update_essay(args.update)
    elif args.delete:
        remove_essay(args.delete)
