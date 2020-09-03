# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy

from crawlers.imdb_crawler.scrapers.ratings_scraper import RatingsScraper
from crawlers.imdb_crawler.scrapers.tv_series_scraper import TvSeriesScraper
from crawlers.imdb_crawler.scrapers.tv_show_scraper import TvShowScraper


class ImdbSpider(scrapy.Spider):
    name = "imdb_spider"

    tot_items = None
    items = 0

    num_votes = 2500
    release_date = 1989
    min_rating = 0.0

    start_urls = [f"https://www.imdb.com/search/title/?count=100&num_votes={num_votes},&release_date={release_date},"
                  f"&title_type=tv_series&title_type=tv_miniseries&user_rating={min_rating},"]

    def parse(self, response):
        scraper = TvSeriesScraper(response.body)

        items, self.tot_items = scraper.get_all_tv_series_items()
        for item in items:
            url = f"/title/{item['id']}/"
            yield response.follow(url, callback=self.parse_show, meta={"tv_series_item": item})

        next_page = scraper.get_next_page()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_show(self, response):
        scraper = TvShowScraper(response.body)
        tv_series_item = scraper.get_details(item=response.meta["tv_series_item"])

        ratings_page = scraper.get_ratings_page()
        ratings_page = response.urljoin(ratings_page)
        yield response.follow(ratings_page, callback=self.parse_ratings, meta={"tv_series_item": tv_series_item})

    def parse_ratings(self, response):
        scraper = RatingsScraper(response.body)
        tv_series_item = scraper.get_all_ratings(item=response.meta["tv_series_item"])
        yield tv_series_item


