# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NaverStockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    end_price = scrapy.Field()
    change = scrapy.Field()
    start_price = scrapy.Field()
    high_price = scrapy.Field()
    low_price = scrapy.Field()
    volume = scrapy.Field()
    pass
