# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CsdnblogItem(scrapy.Item):
    article_name = scrapy.Field()
    article_url = scrapy.Field()
    pass
