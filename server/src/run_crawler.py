import subprocess

from scrapy import cmdline
import pathlib
import os


def run_imdb_crawler(local=True):
    path = pathlib.Path(__file__).parent.absolute()
    os.chdir(path)
    print("run crawler")
    command = f"scrapy crawl imdb_spider -s local={int(local)}"

    # cmdline.execute(command.split())
    subprocess.call(command, shell=True)
