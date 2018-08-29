# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BossWebsiteItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    website_name = scrapy.Field()
    position_url = scrapy.Field()
    company_url = scrapy.Field()
    company_id = scrapy.Field()
    position_id = scrapy.Field()
    position_name = scrapy.Field()
    position_type = scrapy.Field()
    work_address = scrapy.Field()
    release_time = scrapy.Field()
    salary = scrapy.Field()
    city = scrapy.Field()
    work_year = scrapy.Field()
    education = scrapy.Field()
    temptation = scrapy.Field()
    hr_name = scrapy.Field()
    hr_head = scrapy.Field()
    hr_position = scrapy.Field()
    company_logo = scrapy.Field()
    company_name = scrapy.Field()
    company_full_name = scrapy.Field()
    company_size = scrapy.Field()
    business_info = scrapy.Field()
    update_time = scrapy.Field()
    description = scrapy.Field()




