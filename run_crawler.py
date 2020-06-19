from scrapy import cmdline

command = f"scrapy crawl imdb_spider"

cmdline.execute(command.split())
