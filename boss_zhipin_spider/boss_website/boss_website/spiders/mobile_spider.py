# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
from lxml import etree
from urllib.parse import urljoin
from ..items import BossWebsiteItem

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


class MobileSpiderSpider(scrapy.Spider):
    name = 'mobile_spider'
    allowed_domains = ['m.zhipin.com']
    start_urls = ['http://m.zhipin.com/']

    base_url = "https://m.zhipin.com/"
    post_url = "https://m.zhipin.com/mobile/jobs.json"

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/51.0.2704.104 Mobile/13F69 Safari/601.1.46",
            # "Cookie": "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1534918003,1534918286,1535029673,1535509963; __a=74802520.1503583734.1534918003.1535509963.341.28.11.63; t=mPJJdxHvahxprgfs; wt=mPJJdxHvahxprgfs; JSESSIONID=""; __c=1535509963; __g=-; __l=l=%2Fwww.zhipin.com%2Fc101280600%2F&r=http%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DZIJF50xTasDZH1FJC1EIWD5AivNRb0zttamdTGY2UdWQyVUPutv1I-nr4uJTQX49%26wd%3D%26eqid%3D8acb9b3700003c86000000045b8605c5; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1535510047",
            # "Referer": "https://m.zhipin.com/c101020100/",
            "Host": "m.zhipin.com",
        },
        "ITEM_PIPELINES": {
            "boss_website.pipelines.BossWebsitePipeline": 300,
        }
    }

    def start_requests(self):
        city = "上海"
        post_data = {
            "city": str(CITY_CODES['{}'.format(city)]),
            "query": "python",
            "page": "1",
        }
        yield scrapy.FormRequest(url=self.post_url, method="GET", formdata=post_data, meta=post_data)

    def parse(self, response):
        post_data = {
            "city": response.meta['city'],
            "query": response.meta['query'],
            "page": str(int(response.meta['page']) + 1),
        }
        json_data = json.loads(response.text)
        if json_data.get('html'):
            response = etree.HTML(json_data['html'])
            detail_url = response.xpath(".//*[@class='item']/a/@href")
            for _ in detail_url:
                print(_)
                yield scrapy.Request(url=urljoin(self.base_url, _), method="GET", callback=self.second_parse)
        else:
            """设置代理ip请求"""
            post_data['proxy'] = "http://183.62.196.10:3128"
            post_data['page'] = '1'
            yield scrapy.FormRequest(url=self.post_url, method="GET", formdata=post_data,
                                     callback=self.parse, meta=post_data)
            print(json.loads(response.text))

        # 判断下一页
        if json_data.get('hasMore'):
            yield scrapy.FormRequest(url=self.post_url, method="GET", formdata=post_data,
                                     callback=self.parse, meta=post_data)

    def second_parse(self, response):
        item = BossWebsiteItem()
        item['_id'] = response.url
        item['website_name'] = "boss直聘"
        item['position_url'] = response.url
        item['company_url'] = urljoin(self.base_url, response.xpath(".//*[@class='view-business']/@href").extract_first())
        item['company_id'] = ""
        item['position_id'] = ""
        item['position_name'] = response.xpath(".//*[@class='job-banner']/div[2]/text()").extract_first()
        item['position_type'] = response.xpath(".//*[@class='job-tags']/span/text()").extract()[1:]
        item['work_address'] = response.xpath(".//*[@class='location-address']/text()").extract_first()
        item['release_time'] = response.xpath(".//*[@class='job-tags']/span/text()").extract_first()
        item['salary'] = response.xpath(".//*[@class='job-banner']/div[2]/span/text()").extract_first()

        item['city'] = response.xpath(".//*[@class='job-banner']/p/text()").extract_first()
        item['work_year'] = response.xpath(".//*[@class='job-banner']/p/text()").extract()[1]
        item['education'] = response.xpath(".//*[@class='job-banner']/p/text()").extract()[2]

        item['temptation'] = ""
        item['hr_name'] = response.xpath(".//*[@class='info-primary']/div/text()").extract_first()
        item['hr_head'] = urljoin(self.base_url, response.xpath(".//*[@class='job-author']/div/img/@src").extract_first())
        item['hr_position'] = response.xpath(".//*[@class='gray']/text()").extract()[1]
        item['company_logo'] = response.xpath(".//*[@class='job-company']/div/img/@src").extract_first()
        item['company_name'] = response.xpath(".//*[@class='gray']/text()").extract_first()
        item['company_full_name'] = response.xpath(".//*[@class='business-info']/h4/text()").extract_first()
        item['company_size'] = response.xpath(".//*[@class='job-company']/div[2]/p[2]/text()").extract()[-1:][0]
        item['business_info'] = item['company_url']
        item['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['description'] = "\n".join(_.strip() for _ in response.xpath(".//*[@class='text']/text()").extract())
        yield item
