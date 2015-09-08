#coding:utf-8
from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor as sle
from cnblogs.items import *
class CnblogsSpider(CrawlSpider):
    #定义爬虫的名称
    name = "cnblogs"
    #定义允许抓取的域名,如果不是在此列表的域名则放弃抓取
    allowed_domains = ["cnblogs.com"]
    #定义抓取的入口urls
    start_urls = ["http://www.cnblogs.com/rwxwsblog/default.html?page=1"]
    # 定义爬取URL的规则，并指定回调函数为parse_item
    rules = [
        #此处要注意?号的转换，复制过来需要对?号进行转换。
        Rule(sle(allow=("/rwxwsblog/default.html\?page=\d{1,}")),
			 follow=True,
			 callback='parse_item')
    ]

    #定义回调函数
    def parse_item(self, response):
        items = []
        sel = Selector(response)
        #base_url = get_base_url(response)#获取当页来自哪个url
        #print base_url
        #div.day=div的class属性是day,然后空格表示下级在找div的class为postTitle的所有元素
        postTitle = sel.css('div.day div.postTitle')
        postCon = sel.css('div.postCon div.c_b_p_desc')
        for index in range(len(postTitle)):
            item = CnblogsItem()
            item['title'] = postTitle[index].css("a").xpath('text()').extract()[0]
            item['link'] = postTitle[index].css('a').xpath('@href').extract()[0]
            item['desc'] = postCon[index].xpath('text()').extract()[0]
            items.append(item)
        return items