# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagouWebsiteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company_id = scrapy.Field()
    position_id = scrapy.Field()
    position_name = scrapy.Field()
    position_type = scrapy.Field()
    release_time = scrapy.Field()
    salary = scrapy.Field()
    city = scrapy.Field()
    work_year = scrapy.Field()
    education = scrapy.Field()
    temptation = scrapy.Field()
    company_logo = scrapy.Field()
    company_name = scrapy.Field()
    company_full_name = scrapy.Field()
    company_type = scrapy.Field()
    financing = scrapy.Field()
    company_size = scrapy.Field()
    description = scrapy.Field()
    website_name = scrapy.Field()
    _id = scrapy.Field()
