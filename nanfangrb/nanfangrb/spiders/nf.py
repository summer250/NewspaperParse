import re

import pandas as pd
import scrapy
from nanfangrb.items import NanfangrbItem
from scrapy_splash import SplashRequest


class NfSpider(scrapy.Spider):
    name = 'nf'
    allowed_domains = ['epaper.southcn.com']

    # start_urls = ['https://epaper.southcn.com/nfdaily/html/202204/01/node_A01.html']

    def start_requests(self):
        df = pd.date_range('2021-01-01', '2021-12-24')
        df_2022 = pd.date_range('2021-12-25', '2022-04-14')
        all_list = []
        for i in range(len(df)):
            date = str(df[i]).split()[0]
            year = re.findall('\d{4}-\d{2}', date)
            year = ''.join(year)
            day = date.replace(year + '-', '')
            all_list.append(year + '/' + day + '/node_2.htm')
        for i in range(len(df_2022)):
            date = str(df_2022[i]).split()[0]
            year = re.findall('\d{4}-\d{2}', date)
            year = ''.join(year)
            year_2022 = year.replace('-', '')
            day = date.replace(year + '-', '')
            all_list.append(year_2022 + '/' + day + '/node_A01.html')
        for date in all_list:
            url = 'https://epaper.southcn.com/nfdaily/html/' + date
            yield SplashRequest(url=url,
                                callback=self.parse_splash,
                                args={'wait': 4},  # 最大超时时间，单位：秒
                                endpoint='render.html')  # 使用splash服务的固定参数

    def parse_splash(self, response):
        data_list = response.xpath('//*[@class="mCSB_container mCS_touch"]/ul/li/div/a/@href').extract()
        for data_url in data_list:
            data_url = ''.join(data_url)
            https_in = 'https' in data_url
            if https_in is True:
                yield scrapy.Request(url=data_url, callback=self.data2022_parse)
            else:
                page_url = response.url
                date = re.findall('\d{4}-\d{2}/\d{2}/', page_url)
                url = 'https://epaper.southcn.com/nfdaily/html/' + ''.join(date) + data_url
                yield scrapy.Request(url=url, callback=self.data2021_parse)

    def data2021_parse(self, response):
        item = NanfangrbItem()

        item['url'] = response.url
        title = response.xpath('//*[@id="print_area"]/h1/text()').extract_first()
        item['title'] = title
        content = response.xpath('//*[@id="content"]/founder-content/p/text()').extract()
        content = "".join(content).replace('\xa0\xa0\xa0\xa0', '')
        item['content'] = content
        yield item

    def data2022_parse(self, response):
        item = NanfangrbItem()

        item['url'] = response.url
        title = response.xpath('//*[@id="print_area"]/h1/text()').extract_first()
        item['title'] = title

        content = response.xpath('//*[@id="content"]/p/text()').extract()
        content = "".join(content).replace('\xa0\xa0\xa0\xa0', '')
        item['content'] = content
        yield item
