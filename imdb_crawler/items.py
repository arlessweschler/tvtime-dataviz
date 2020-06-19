# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TvSeriesItem(Item):
    id = Field
    name = Field()
    start_year = Field()
    rating = Field()
