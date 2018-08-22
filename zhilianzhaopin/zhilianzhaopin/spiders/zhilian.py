# -*- coding: utf-8 -*-
import scrapy
from ..items import ZhilianzhaopinItem
from scrapy.loader import ItemLoader
from scrapy import Request
from urllib.parse import urljoin
import re


class ZhilianSpider(scrapy.Spider):
    name = "zhilian"
    allowed_domains = ["sou.zhaopin.com"]
    start_urls = ["http://sou.zhaopin.com"]

    start_url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}'
    headers = {
        "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
    }

    # 爬取的职位和城市
    city_lists = ['上海']
    job_lists = ['python']

    mongourl = 'mongodb://127.0.0.1:27017'
    mongodb = name

    # 重写首页爬取目标
    def start_requests(self):
        base_url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}'
        for c in self.city_lists:
            for j in self.job_lists:
                yield scrapy.Request(base_url.format(c, j))

    # 初步过滤url字符串
    def filter_job_name(self, job):
        regx1 = r""".*<a.*>(<b>.*)</a>.*"""
        regx2 = r""".*<a.*>(.*)</a>.*"""
        print(job)
        if len(re.findall(regx1, job)) == 0:
            return re.match(regx2, job).group(1).strip('()（）\xa0')
        return re.findall(regx1, job)[0].strip('()（）\xa0')

    # 解析首页页面的url
    def parse(self, response):
        item = ZhilianzhaopinItem()
        num = response.xpath(".//*[@class='search_yx_tj']/em/text()")
        print("一共有{}个职位".format(num)[0])
        job1 = response.xpath(".//*[@class='zwmc']/div/a").extract()
        job1 = [self.filter_job_name(_) for _ in job1]
        # 过滤列表中的空字符
        while '' in job1:
            job1.remove('')
        print(job1)
        job_url_suffer = response.xpath(".//*[@class='zwmc']/div/a/@href").extract()
        company = response.xpath(".//*[@class='gsmc']/a/text()").extract()
        salary = response.xpath(".//*[@class='zwyx']/text()").extract()[1:]
        position = response.xpath(".//*[@class='gzdd']/text()").extract()[1:]
        org_item = zip(job1, job_url_suffer, company, salary, position)
        for i in org_item:
            item['job'] = i[0]
            item['job_url'] = i[1]
            item['company'] = i[2]
            item['salary'] = i[3]
            item['position'] = i[4]
            yield item
        # 将工作详情url传给第二个解析器
        for suffer in job_url_suffer:
            yield Request(url=urljoin(self.start_urls[0], suffer), headers=self.headers)
        # 提取下一页，并回传再次获取链接
        next_page = response.xpath(".//*[@class='pagesDown-pos']/a/@href").extract()
        if next_page:
            yield Request(url=urljoin(response.url, next_page[0]), headers=self.headers, callback=self.parse)

    def parse_detail(self, response):
        print("Hello*****************************")