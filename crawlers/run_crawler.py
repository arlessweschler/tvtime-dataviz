from scrapy import cmdline
import pathlib
import os


def run_crawler():
    path = pathlib.Path(__file__).parent.absolute()
    os.chdir(path)
    command = f"scrapy crawl imdb_spider"

    cmdline.execute(command.split())
