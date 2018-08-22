# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymongo


class ZhilianzhaopinPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("job_des.json", "w+", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + ',\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class SaveToRedisPipeline(object):
    def __init__(self):
        pass


class SaveToMongodbPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient()




