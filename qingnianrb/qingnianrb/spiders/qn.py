import re

import pandas as pd
import scrapy
from qingnianrb.items import QingnianrbItem
from scrapy_redis.spiders import RedisSpider


class QnSpider(RedisSpider):
    name = 'qn'
    allowed_domains = ['why.com.cn']

    redis_key = 'qn:start_url'

    def make_requests_from_url(self, url):
        return scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        df = pd.date_range('2018-01-01', '2022-04-14')
        for i in range(len(df)):
            date = str(df[i]).split()[0]
            year = re.findall('\d{4}-\d{2}', date)
            year = ''.join(year)
            day = date.replace(year + '-', '')
            url = f'http://www.why.com.cn/epaper/webpc/qnb/html/{year}/{day}/node_1.html'
            yield scrapy.Request(url=url, callback=self.page_parse)

    def page_parse(self, response):
        page_list = response.xpath('//*[@id="pageLink"]/@href').extract()
        tmp = list(set(page_list))
        for page in tmp:
            now_url = response.url
            now_url_list = re.findall('http://www.why.com.cn/epaper/webpc/qnb/html/\d{4}-\d{2}/\d{2}/', now_url)
            page_str = ''.join(now_url_list)
            url = page_str + page
            yield scrapy.Request(url=url, callback=self.content_parse)

    def content_parse(self, response):
        content_list = response.xpath('//*[@id="artPList1"]/li/a/@href').extract()
        tmp = list(set(content_list))
        for content in tmp:
            now_url = response.url
            now_url_list = re.findall('http://www.why.com.cn/epaper/webpc/qnb/html/\d{4}-\d{2}/\d{2}/', now_url)
            page_str = ''.join(now_url_list)
            url = page_str + content
            yield scrapy.Request(url=url, callback=self.data_parse)

    def data_parse(self, response):
        item = QingnianrbItem()

        item['url'] = response.url
        title = response.xpath('//*[@class="title1"]/text()').extract_first()
        title = ''.join(title).replace('\u3000', '')
        item['title'] = title
        content = response.xpath('//*[@class="content_tt"]/p/text()').extract()
        content = ''.join(content).replace('\u3000', '').replace('\xa0', '')
        item['content'] = content
        yield item
