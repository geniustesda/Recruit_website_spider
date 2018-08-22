# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pc端boss直聘爬虫
"""
import requests
import pymysql
import os, time
from lxml import etree
from hashlib import md5
import logging

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
# obj_list = (job, job_des_url, company_des_url, salary, tags, position, worktime, education, company, industry,
#                       finance, size, hr_name, hr_img, hr_job, release_date)

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


def save_to_mysql(data):
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="", db="boss", charset="utf8")
    cursor = conn.cursor()
    # effect_row = cursor.execute("select * from job_crawl;")
    sql = "insert into " \
          "job_crawl(job, job_des_url, company_des_url, salary, position, worktime, education, company, industry," \
          "finance, size, hr_name, hr_img, hr_job, release_date) " \
          "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        # 执行列表一次性写入
        effect_row = cursor.execute(sql, data)
        print("正在写入 {} 条数据".format(effect_row))
        # 提交数据,关闭游标,关闭数据库连接
        conn.commit()
        print('正在写入数据库...')
        cursor.close()
        conn.close()
    except Exception:
        print("mysql数据库写入错误")


# 获取当前页面response
def get_one_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        return response
    return ("页面未成功获取")


# 解析页面
def parse_page(response):
    if response.status_code == 200:
        html = etree.HTML(response.text)
        job = html.xpath(".//*[@class='job-title']/text()")
        job_des_url = html.xpath(".//*[@class='info-primary']/h3/a/@href")
        company_des_url = html.xpath(".//*[@class='company-text']/h3/a/@href")
        salary = html.xpath(".//*[@class='red']/text()")
        # tags = html.xpath(".//*[@class='job-tags']/span/text()")
        position = html.xpath(".//*[@class='info-primary']/p/text()[1]")
        worktime = html.xpath(".//*[@class='info-primary']/p/text()[2]")
        education = html.xpath(".//*[@class='info-primary']/p/text()[3]")
        company = html.xpath(".//*[@class='company-text']/h3/a/text()")
        industry = html.xpath(".//*[@class='company-text']/p/text()[1]")
        finance = html.xpath(".//*[@class='company-text']/p/text()[2]")
        size = html.xpath(".//*[@class='company-text']/p/text()[3]")
        hr_name = html.xpath(".//*[@class='info-publis']/h3/text()[1]")
        hr_img = html.xpath(".//*[@class='name']/img/@src")
        hr_job = html.xpath(".//*[@class='info-publis']/h3/text()[2]")
        release_date = html.xpath(".//*[@class='info-publis']/p/text()")
        result = zip(job, job_des_url, company_des_url, salary,
                 # " ".join([i for i in tags]),
                 position, worktime, education, company, industry, finance, size, hr_name, hr_img, hr_job, release_date)
        return result
    print("parse_error")


# 将数据保存到text
def save_to_txt(result, city, job, filename):
    if not os.path.exists(city + "/" + job):
        os.makedirs(city + "/" + job)
    file_path = '{0}/{1}/{2}.{3}'.format(city, job, filename, 'txt')
    if not os.path.exists(file_path):
        with open(file_path, "a+")as f:
            print("正在写入到txt文件...")
            f.write("\n". join(result))
    print("text数据已存在: ({})".format(file_path))


from openpyxl import Workbook


# 将数据保存到excel
class SavetoExcel(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["职位名称", "职位详情链接", "公司详情链接", "薪资", "工作地点", "工作年限", "学历",
                        "公司名称", "所在行业", "融资情况", "公司规模", "HR名字", "HR头像", "HR的职位",
                        "发布时间"])

    def process_item(self, item, job):
        self.ws.append(list(item))
        print("正在写入excel")
        self.wb.save("./"+job+".xlsx")
        self.wb.close()


import pandas as pd


# 用pandas保存到excel
def pandas_save_to_excel(data, city, job):
    data_df = pd.DataFrame(data)
    data_df.columns = ["职位名称", "职位详情链接", "公司详情链接", "薪资", "工作地点", "工作年限", "学历",
                        "公司名称", "所在行业", "融资情况", "公司规模", "HR名字", "HR头像", "HR的职位",
                        "发布时间"]
    writer = pd.ExcelWriter(city+"/"+job+".xlsx")
    data_df.to_excel(writer, sheet_name="job_info")
    writer.save()


# 写入日志文件
def log_info(errortype, errormessage):
    logger = logging.getLogger(__name__)  # 实例化一个日志对象，并设置日志名称
    logger.setLevel(level=logging.INFO)  # 设置日志等级
    handler = logging.FileHandler("log_text_error.log")  # 设置日志路径
    handler.setLevel(logging.INFO)  # 设置日志文件模型等级
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')  # 构建日志模型内容
    handler.setFormatter(formatter)  # 保存日志模型内容

    console = logging.StreamHandler()    # 实例化控制台日志
    console.setLevel(logging.INFO)       # 设置控制台日志等级

    logger.addHandler(handler)  # 激活设置,保存日志
    logger.addHandler(console)  # 激活设置,打印日志
    if errortype == "info":
        logger.info("{}".format(errormessage))
    if errortype == "debug":
        logger.debug("{}".format(errormessage))
    if errortype == "warning":
        logger.debug("{}".format(errormessage))


def main():
    job_list = ['python', 'java', 'php', '前端', '数据挖掘', '机器学习']
    city = "上海"
    print('正在爬取{}的工作职位'.format(city))
    for job in job_list:
        city_code = str(CITY_CODES[city])

        if not os.path.exists(city):
            os.mkdir(city)
        for num in range(1, 11):
            # save_excel = SavetoExcel()
            url = 'https://www.zhipin.com/c' + city_code + '/h_' + city_code + '/?query=' + job + '&page=' + str(
                num) + '&ka=page-' + str(num)
            print(url)
            try:
                page = get_one_page(url)
            except Exception:
                error_type = "warning"
                error_message = 'get_url_error: {}'.format(url)
                log_info(error_type, error_message)
                continue

            print("{}工作\n    正在爬取第{}页".format(job, num))
            try:
                result = parse_page(page)
            except Exception:
                error_type = "warning"
                error_message = 'parse_page_error:{}'.format(url)
                log_info(error_type, error_message)
                continue
            # 保存数据
            for _ in result:
                save_to_mysql(_)
                filename = md5(str(_).encode("utf-8")).hexdigest()
            #     save_excel.process_item(item=_, job=job)
            #     pandas_save_to_excel(data=_, city=city, job=job)
                try:
                    save_to_txt(_, city, job, filename)
                except Exception:
                    error_type = "warning"
                    error_message = 'save_to_text_error:{} url:{}'.format(filename, _[1])
                    log_info(error_type, error_message)
                    continue
            time.sleep(5)


if __name__ == '__main__':
    main()

