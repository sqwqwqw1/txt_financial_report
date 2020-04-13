# -*- coding: utf-8 -*-

import scrapy


class NdbgItem(scrapy.Item):
    _id = scrapy.Field()
    code = scrapy.Field()
    year = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()