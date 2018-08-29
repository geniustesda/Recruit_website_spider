# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
移动端boss直聘爬虫
"""
import requests
import time
import os
import hashlib
import urllib
import pandas as pd
from json import loads
from lxml import etree
from urllib.parse import urljoin
"""
基本路由结构如下：https://www.zhipin.com/job_detail/?city=101020100&source=100&query=Android
拆分：https://www.zhipin.com/job_detail/?city= <city_code> &source=10&query= <job_name>
https://www.zhipin.com/mobile/jobs.json?page=2&city=101020100&query=python
"""
CITY_CODES = {
        "上海": 101020100,
        "北京": 101010100,
        "深圳": 101280600,
        "广州": 101280100,
        "杭州": 101210100,
        "天津": 101030100,
        "西安": 101110100,
        "苏州": 101190400,
        "武汉": 101200100,
        "厦门": 101230200,
        "长沙": 101250100,
        "成都": 101270100
        }
JOB_LIST = ["python"]
            # "python", "爬虫", "前端", "机器学习", "数据挖掘", "人工智能", "php", "java"
Ready_todo = "ready_list.txt"
Already_todo = "already_list.txt"
CACHE_DIR = "cache"
Domain = "https://www.zhipin.com/"
HEADERS = {"Host": "www.zhipin.com",
           "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/603.1.30 "
                         "(KHTML, like Gecko) Version/11.1.1 Mobile/14E304 Safari/602.1",
           "Accept": "*/*",
           "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
           "Accept-Encoding": "gzip, deflate, br",
           "X-Requested-With": "XMLHttpRequest",
           "Referer": "",
           "Connection": "keep-alive"
           }
csv_head = ['company_name', 'job_name', 'city', 'work_time',
                            'education', 'salary', 'img_url']


# 定义日志方法
def log(*args, **kwargs):
    formats = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(formats, value)
    with open('log.txt', 'a+', encoding='utf-8') as f:
        print(dt, *args, file=f, **kwargs)


# 获取任意页面的response
def get_one_page(url, city_code, job_name):
    job_name = urllib.parse.quote(job_name)     # 将中文转化成url编码
    HEADERS["Referer"] = "https://www.zhipin.com/job_detail/?city="+city_code+"&source=10&query="+job_name
    response = requests.get(url, headers=HEADERS)
    code = response.apparent_encoding
    print("当前页面的编码为:{}".format(code))
    response.encoding = code
    return response


# 保存页面到本地
def save_page(html_page, page_url):
    if os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    page_name = hashlib.md5(page_url.encode('utf-8')).hexdigest()
    if not os.path.exists(CACHE_DIR+"/"+page_name):
        with open("{}/{}".format(CACHE_DIR, page_name), "w+")as f:
            f.write(html_page)


# 保存为csv格式
def save_to_csv(data):
    df = pd.DataFrame(columns=csv_head)
    pd.DataFrame(data)
    df.to_csv("data.csv")


# 获取所有职位的url，并保存到本地
def get_url_lists(city_code, job_name):
    num = 1
    if not os.path.exists(city+"/"+job):
        os.makedirs(city+"/"+job_name)
    job_name = urllib.parse.quote(job_name)  # 将中文转化成url编码
    while 1:
        index_url = "https://www.zhipin.com/mobile/jobs.json?page="+str(num)+"&city="+city_code+"&query="+job_name
        print("正在获取第{}页...\n{}".format(num, index_url))
        response = get_one_page(index_url, city_code, job_name)
        json_data = loads(response.text)
        html = etree.HTML(json_data['html'])
        job_des_url_lists = html.xpath(".//*[@class='item']/a/@href")
        company_name_list = html.xpath(".//*[@class='name']/text()")
        job_name_list = html.xpath(".//*[@class='title']/h4/text()")
        city_lists = html.xpath(".//*[@class='msg']/em[1]/text()")
        work_time_list = html.xpath(".//*[@class='msg']/em[2]/text()")
        education_list = html.xpath(".//*[@class='msg']/em[3]/text()")
        salary_list = html.xpath(".//*[@class='salary']/text()")
        company_imgurl_list = html.xpath(".//*[@class='item']/a/img/@src")
        result = zip(company_name_list, job_name_list, city_lists, work_time_list,
                     education_list, salary_list, company_imgurl_list)
        for _ in result:
            # save_to_csv(list(_))
            print(str(_)+"\n")
        with open(city+"/"+job+"/"+Ready_todo, "a+")as f:
            for _ in job_des_url_lists:
                f.write(urljoin(Domain, _.strip("\n"))+"\n")
        if json_data['hasMore'] == False:
            break
        num += 1
        time.sleep(1)


# 获取任务列表
def get_task_list(city_lists, job_lists):
    for city in city_lists:
        for job in job_lists:
            with open(city + "/" + job + "/" + Ready_todo)as f1:
                ready_list = f1.readlines()
            with open(city + "/" + job + "/" + Already_todo)as f2:
                already_list = set(f2.readlines())
            for _ in already_list:
                ready_list.remove(_)
                return ready_list


if __name__ == '__main__':
    job_list = JOB_LIST
    city_list = list(CITY_CODES.keys())
    # 获取所有职位详情超链
    for city in city_list:
        for job in job_list:
            city_code = str(CITY_CODES[city])
            try:
                get_url_lists(city_code, job)
            except Exception:
                continue

    # 获取所有详情页面并保存页面源码
    task_list = get_task_list(city_list, job_list)
    for i, j, k in (task_list, city_list, job_list):
        city_code = str(CITY_CODES[j])
        response_data = get_one_page(url=i, city_code=city_code, job_name=k)
        save_page(response_data.text, page_url=i)
