# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class BossWebsitePipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("127.0.0.1", 27017)
        database = client['Recruitment_website']
        self.collection_job_info = database['boss_zhipin_info']

    def process_item(self, item, spider):
        print("正在保存数据:{}".format(item))
        self.collection_job_info.save(item)
        return item
