import re

import pandas as pd
import scrapy
from guangmingrb.items import GuangmingrbItem
from scrapy_redis.spiders import RedisSpider


class GmSpider(RedisSpider):
    name = 'gm'
    allowed_domains = ['epaper.gmw.cn']
    # start_urls = ['https://epaper.gmw.cn/gmrb/html/2022-04/17/nbs.D110000gmrb_01.htm']

    redis_key = 'gm:start_url'

    def make_requests_from_url(self, url):
        return scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        df = pd.date_range('2018-01-01', '2022-04-14')
        for i in range(len(df)):
            date = str(df[i]).split()[0]
            year = re.findall('\d{4}-\d{2}', date)
            year = ''.join(year)
            day = date.replace(year + '-', '')
            url = f'https://epaper.gmw.cn/gmrb/html/{year}/{day}/nbs.D110000gmrb_01.htm'
            yield scrapy.Request(url=url, callback=self.page_parse)

    def page_parse(self, response):
        page_list = response.xpath('//*[@id="pageLink"]/@href').extract()
        for page in page_list:
            now_url = response.url
            now_url_list = re.findall('https://epaper.gmw.cn/gmrb/html/\d{4}-\d{2}/\d{2}/', now_url)
            page_str = ''.join(now_url_list)
            url = page_str + page
            yield scrapy.Request(url=url, callback=self.content_parse)

    def content_parse(self, response):
        content_list = response.xpath('//*[@id="titleList"]/ul/li/a/@href').extract()
        for content in content_list:
            now_url = response.url
            now_url_list = re.findall('https://epaper.gmw.cn/gmrb/html/\d{4}-\d{2}/\d{2}/', now_url)
            page_str = ''.join(now_url_list)
            url = page_str + content
            yield scrapy.Request(url=url, callback=self.data_parse)

    def data_parse(self, response):
        item = GuangmingrbItem()
        item['url'] = response.url

        title = response.xpath('//*[@class="text_c"]/h1/text()').extract_first()
        item['title'] = title

        content = response.xpath('//*[@id="articleContent"]/p/text()').extract()
        content = "".join(content).replace('\u2003\u2003', '').replace('\u3000\u3000', '').replace('\xa0', '')
        item['content'] = content
        yield item
