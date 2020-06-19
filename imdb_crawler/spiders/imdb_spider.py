# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from imdb_crawler.helpers.scraper import TvSeriesScraper, TvShowScraper


class ImdbSpider(scrapy.Spider):
    name = "imdb_spider"

    num_votes = 5000
    release_date = 2000
    min_rating = 8.0

    start_urls = [f"https://www.imdb.com/search/title/?count=100&num_votes={num_votes},&release_date={release_date},&title_type=tv_series&user_rating={min_rating},"]

    def parse(self, response):
        scraper = TvSeriesScraper(response.body)

        infos = scraper.get_all_tv_series()
        for i, info in enumerate(infos):
            print(f"{i} - {info}")
            yield response.follow(info[1], callback=self.parse_ratings)

        next_page = scraper.get_next_page()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_ratings(self, response):
        scraper = TvShowScraper(response.body)
        print(scraper.get_length())


