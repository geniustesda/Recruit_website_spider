# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class LagouWebsitePipeline(object):

    def __init__(self):
        client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.collections = client["Recruitment_website"]["lagou_job_info"]

    def process_item(self, item, spider):
        self.collections.save(item)
        return item
