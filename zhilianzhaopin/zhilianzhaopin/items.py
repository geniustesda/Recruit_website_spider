# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhilianzhaopinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job = scrapy.Field()
    job_url = scrapy.Field()
    company = scrapy.Field()
    salary = scrapy.Field()
    position = scrapy.Field()

