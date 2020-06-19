# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy

from imdb_crawler.helpers.printer import red
from imdb_crawler.helpers.scraper import TvSeriesScraper, TvShowScraper
from imdb_crawler.helpers.utility import strip_html_tags
from imdb_crawler.items import TvSeriesItem


class ImdbSpider(scrapy.Spider):
    name = "imdb_spider"

    num_votes = 5000
    release_date = 2000
    min_rating = 8.0

    start_urls = [f"https://www.imdb.com/search/title/?count=100&num_votes={num_votes},&release_date={release_date},"
                  f"&title_type=tv_series&user_rating={min_rating},"]

    def parse(self, response):
        scraper = TvSeriesScraper(response.body)

        infos = scraper.get_all_tv_series()
        for i, info in enumerate(infos):
            tv_series_item = TvSeriesItem()
            tv_series_item["name"] = info[0]
            tv_series_item["start_year"] = info[2]
            tv_series_item["rating"] = info[4]
            yield response.follow(info[1], callback=self.parse_ratings, meta={"tv_series_item": tv_series_item})

        next_page = scraper.get_next_page()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_ratings(self, response):
        tv_series_item = response.meta["tv_series_item"]
        scraper = TvShowScraper(response.body)
        try:
            tv_series_item["length"] = strip_html_tags(scraper.get_length())
        except AttributeError:
            print(red(f"ERROR: {tv_series_item['name']}"))
            tv_series_item["length"] = "None"
        print(tv_series_item)
        yield tv_series_item


