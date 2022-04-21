import re

import pandas as pd
import scrapy
from scrapy_redis.spiders import RedisSpider
from xinkuairb.items import XinkuairbItem


class XkSpider(RedisSpider):
    name = 'xk'
    allowed_domains = ['epaper.xkb.com.cn']
    url = 'https://epaper.xkb.com.cn/index.php'
    # start_urls = ['http://epaper.xkb.com.cn/']

    redis_key = 'xk:start_url'

    def make_requests_from_url(self, url):
        return scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        df = pd.date_range('2018-01-01', '2022-04-14')
        for i in range(len(df)):
            date = str(df[i]).split()[0]
            data = {
                'act': 'list',
                'date': date
            }
            yield scrapy.FormRequest(url=self.url, formdata=data, callback=self.module_parse)

    def module_parse(self, response):
        module_list = response.json()
        for module in module_list:
            id = module['id']
            data = {
                'act': 'img',
                'id': id
            }
            headers = {
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
            }
            yield scrapy.FormRequest(url=self.url, formdata=data, headers=headers, callback=self.news_parse)

    def news_parse(self, response):

        plate_link = response.json()['plate_img']
        url_list = re.findall('/view/\d{7}', plate_link)
        for url in url_list:
            data_url = 'https://epaper.xkb.com.cn' + url
            yield scrapy.Request(url=data_url, callback=self.data_parse)

    def data_parse(self, response):
        item = XinkuairbItem()
        item['url'] = response.url
        title = response.xpath('//*[@id="viewleftZdy"]/div[1]/span/text()').extract_first()
        item['title'] = title
        date = response.xpath('//*[@id="viewleftZdy"]/div[1]/text()').extract()
        date = "".join(date).replace(" ", "")
        date = "".join(date.split())
        date = re.findall('\d{4}-\d{2}-\d{2}', date)
        date = "".join(date)
        item['date'] = date
        content = response.xpath('//*[@id="news_content"]/p/text()').extract()
        content = ''.join(content).replace("['", '').replace("']", '')
        item['content'] = content
        yield item
