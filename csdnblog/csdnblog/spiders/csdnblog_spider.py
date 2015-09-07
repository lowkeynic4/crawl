#coding:utf-8
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from csdnblog.items import CsdnblogItem

class CSDNBlogSpider(Spider):
    name = "csdnblog"
    download_delay = 1#减慢爬取速度 为1s
    allowed_domains = ["blog.csdn.net"]
    #第一篇文章地址
    start_urls = ["http://blog.csdn.net/u012150179/article/details/11749017"]

    def parse(self, response):
        sel = Selector(response)
        item = CsdnblogItem()

        article_url = str(response.url)#本篇文章的url
        article_name = sel.xpath('//div[@id="article_details"]/div/h1/span/a/text()').extract()[0]
        item['article_name'] = article_name
        item['article_url'] = article_url.encode('utf-8')
        yield item

        #获得下一篇文章的url
        url = sel.xpath('//li[@class="next_article"]/a/@href').extract()[0]
        urls = "http://blog.csdn.net" + url
        yield Request(urls, callback=self.parse)
