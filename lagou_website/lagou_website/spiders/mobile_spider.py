# -*- coding: utf-8 -*-
import scrapy
import json
import time
import math
import random
import datetime
from urllib.parse import urljoin
from ..items import LagouWebsiteItem


class MobileSpiderSpider(scrapy.Spider):
    name = "mobile_spider"
    allowed_domains = ["lagou.com"]

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://m.lagou.com/search.html",
        "Cookie": "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1532277865,1533050918,1534843806,1534850292; _ga=GA1.2.1672649481.1493376208; LGUID=20170428184410-9cbe33a6-2bff-11e7-b419-5254005c3644; _ga=GA1.3.1672649481.1493376208; user_trace_token=20180606163053-cfc32e8dacc048c9b79eada9130904a4; LG_LOGIN_USER_ID=32488948392d7a65a18a34fe6ce857fc09fef84210ac7bfd; fromsite=www.baidu.com; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1534865548; LGRID=20180821233232-6bbda512-a557-11e8-ab1f-5254005c3644; index_location_city=%E4%B8%8A%E6%B5%B7; _gid=GA1.2.1905354058.1534843808; JSESSIONID=ABAAABAAAFDABFG0A49BDC4969C47AC3E98FBBB978E8F7F; X_HTTP_TOKEN=1cea93d6affc93a3e413629a8bc6f05d; LGSID=20180821222738-5ab0a231-a54e-11e8-98f6-525400f775ce",
        'Host': 'm.lagou.com'
    }

    search_url = "https://m.lagou.com/search.json"
    base_url = "https://www.lagou.com/"
    detail_url = "https://m.lagou.com/jobs/{}.html"
    gongsi_url = "https://www.lagou.com/gongsi/{}.html"

    custom_settings = {
        "ITEM_PIPELINES": {
           'lagou_website.pipelines.LagouWebsitePipeline': 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 'lagou_website.middlewares.ProxyMiddleWare': 125,
        },
        "DEFAULT_REQUEST_HEADERS": {
           "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br',
           "X-Requested-With": "XMLHttpRequest",
           "Referer": "https://m.lagou.com/",
           "Cookie": "",
           'Host': 'm.lagou.com'
        }
    }

    def start_requests(self):
        city_list = ["北京", "上海", "深圳", "广州", "杭州", "南京", "武汉", "成都"]
        city_list = ['上海']
        position_list = [""]
        # "python", "java", "数据分析", "爬虫", "前端",
        # "php", "c", "c++", "数据挖掘", "机器学习", "自然语言处理"

        for city in city_list:
            for job in position_list:
                formdata = dict(
                    city=city,
                    positionName=job,
                    pageNo="1",
                    pageSize="15"
                )
                print(formdata)
                time.sleep(1)
                yield scrapy.FormRequest(self.search_url, method="GET", formdata=formdata,
                                         callback=self.parse)

    def parse(self, response):
        json_data = json.loads(response.text)
        print(json_data)
        job_data = json_data['content']['data']['page']['result']
        if len(job_data) is 0:
            return None
        job_detail_code_list = json_data['content']['data']['page']['result']
        for _ in job_detail_code_list:
            meta_data = dict(
                position_name=_['positionName'],
                city=_['city'],
                position_id=_['positionId'],
                company_id=_['companyId'],
                release_time=_['createTime'],
                salary=_['salary'],
                company_url=self.gongsi_url.format(_['companyId']),
                company_name=_['companyName'],
                company_full_name=_['companyFullName'],
                company_logo=urljoin(self.base_url, _.get('companyLogo')),
                # proxy="http://118.190.95.43:9001",
                )
            yield scrapy.Request(url=self.detail_url.format(_['positionId']), method="GET", headers=self.headers,
                                 meta=meta_data, callback=self.second_parse)

        base_info = dict(
            totalCount=json_data['content']['data']['page']['totalCount'],
            pageNo=json_data['content']['data']['page']['pageNo'],
            positionName=json_data['content']['data']['custom']['positionName'],
            city=json_data['content']['data']['custom']['city']
        )
        total_page = math.ceil(int(base_info['totalCount'])/15)

        if base_info['pageNo'] < total_page:
            # print(response.request.headers['Cookie'])
            next_num = base_info['pageNo'] + 1
            headers = self.headers
            form_data = dict(
                city=(base_info['city']),
                positionName=base_info['positionName'],
                pageNo=str(next_num),
                pageSize="15"
            )
            print("一共有{}页，正在获取第{}页".format(total_page, next_num))
            yield scrapy.FormRequest(self.search_url, method="GET", headers=headers,
                                     formdata=form_data, callback=self.parse)
            time.sleep(random.uniform(1, 3))

    def second_parse(self, response):
        item = LagouWebsiteItem()
        item['_id'] = response.url.replace("/m.", "/www.")
        item['position_url'] = item['_id']
        item['company_url'] = response.meta['company_url']
        item['website_name'] = "拉勾网"
        item['company_id'] = response.meta['company_id']
        item['position_id'] = response.meta['position_id']
        item['position_name'] = response.xpath(".//*[@class='postitle']/h2/text()").extract_first()
        item['position_type'] = response.xpath(".//*[@class='item jobnature']/span/text()").extract_first()
        item['release_time'] = response.meta['release_time']
        item['salary'] = response.meta['salary']
        item['city'] = response.meta['city']
        item['work_year'] = response.xpath(".//*[@class='item workyear']/span/text()").extract_first()
        item['education'] = response.xpath(".//*[@class='item education']/span/text()").extract_first().strip()
        item['temptation'] = response.xpath(".//*[@class='temptation']/text()").extract_first().strip().split("：")[1]
        item['company_logo'] = response.meta['company_logo']
        item['company_name'] = response.meta['company_name']
        item['company_full_name'] = response.meta['company_full_name']

        company_info_list = response.xpath(".//*[@class='info']/text()").extract_first().split('/')
        item['company_type'] = company_info_list[0].strip().split(',')
        item['financing'] = company_info_list[1].strip()
        item['company_size'] = company_info_list[2].strip()

        description = "\n".join(response.xpath(".//*[@class='content']/p/text()").extract())
        item['description'] = description
        if not item['description'].strip():
            item['description'] = "\n".join(response.xpath(".//*[@class='content']/text()").extract())
        elif not item['description'].strip():
            item['description'] = "\n".join(response.xpath(".//*[@class='content']/span/text()").extract())
        item['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
