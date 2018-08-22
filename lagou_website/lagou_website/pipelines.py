# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime


class LagouWebsitePipeline(object):
    create_time = datetime.datetime.now().strftime("%Y%m%d")

    def __init__(self):
        client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.collections = client["Recruitment_website"]["lagou_job_info_"+str(self.create_time)]

    def process_item(self, item, spider):
        self.collections.save(item)
        return item
