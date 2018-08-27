# -*- coding:utf-8 -*-
from scrapy.cmdline import execute
import time
import datetime
import pymongo
import os


def data_backup():
    create_time = datetime.datetime.now().strftime("%Y%m%d")
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    documents = client['Recruitment_website']['lagou_job_info']
    all_data = documents.find()
    for _ in all_data:
        client['Recruitment_website']['lagou_job_info'+'_'+create_time].save(_)


def auto_run_crawl():
    while 1:
        now_time1 = datetime.datetime.now()
        # if now_time.hour == 1:
        #     os.system("scrapy3 crawl mobile_spider")
        os.system("scrapy3 crawl mobile_spider")
        data_backup()
        now_time2 = datetime.datetime.now()
        used_time = (now_time2 - now_time1).seconds
        time.sleep(60*60*1-used_time)


if __name__ == '__main__':
    auto_run_crawl()
    # os.system("scrapy3 crawl mobile_spider")
    # data_backup()
