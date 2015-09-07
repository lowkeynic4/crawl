#coding:utf-8
from scrapy.spiders import Spider
from scrapy.selector import Selector
import logging
from w3school.items import W3SchoolItem

class W3schoolSpider(Spider):
    name = "w3school"
    allowed_domains = ["w3school.com.cn"]
    start_urls = [
        "http://www.w3school.com.cn/xpath/index.asp"
    ]
    #许多例子都是用from scrapy import log 但是已经deprecated了，推荐使用build_in logging
    logging.basicConfig(level = logging.DEBUG,
                        format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='w3school.log',
                        filemode='w')

    def parse(self, response):
        sel = Selector(response)
        sites = sel.xpath('//div[@id="course"]/ul[1]/li')
        items = []

        for site in sites:
            item = W3SchoolItem()
            title = site.xpath('a/text()').extract()[0]
            item['title'] = title
            link = site.xpath('a/@href').extract()[0]
            item['link'] = "http://www.w3school.com.cn"+link
            #这是输出文字的两种方法，具体差别暂时还不清楚
            desc = site.xpath('a/@title').extract()
            item['desc'] = [d.encode('utf-8') for d in desc]
            items.append(item)
            logging.info("add one item")
        logging.info("done")
        return items