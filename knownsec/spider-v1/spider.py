#coding:utf-8
from optparse import OptionParser
import urllib2
from bs4 import BeautifulSoup
import urllib
import re
import StringIO, gzip

class Spider():
    def __init__(self,args):
        self.url = args.url
        self.depth = args.depth
        self.keyword = args.keyword
        self.alreadyVisit = []
    def check_visit(self,url):
        if url in self.alreadyVisit:
            return True
        else:
            return False


    def crawl(self,url,keyword,depth):
        header={"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50",
                'Accept-Encoding':'gzip, deflate'}
        #网页中会有很多重复的链接，如果没有访问过就按正常流程访问并放入已访问列表中，访问过就跳过
        if self.check_visit(url):
            return
        else:
            self.alreadyVisit.append(url)
        try:

            request = urllib2.Request(url = url,headers = header)
            response = urllib2.urlopen(request)
            resHeader = response.info()
            content = response.read()
            if ('Content-Encoding' in resHeader and resHeader['Content-Encoding']) or \
                ('content-encoding' in resHeader and resHeader['content-encoding']):
                #判断是否是gzip压缩，如果是的话就先解压
                if "gzip" in resHeader.get("Content-Encoding"):
                    compressedstream = StringIO.StringIO(content)
                    gziper = gzip.GzipFile(fileobj=compressedstream)
                    data2 = gziper.read()
                    try:
                        #正常情况下都利用gbk进行解码
                        content = data2.decode('gbk')
                    except UnicodeDecodeError,e:
                        #如果出错就利用utf8解码，这里的思路是因为大多数中文网页都使用gbk编码，但是也要考虑例外
                        content = data2.decode('utf-8', 'ignore')

        except urllib2.HTTPError,e:
            return -1


        try:
            proto, rest = urllib.splittype(url)
            domain = urllib.splithost(rest)[0]
            m = re.compile(r'%s' % unicode(keyword, 'utf-8')).findall(content)
            if m:
                #网页中有关键字的匹配
                #print content  #打印网页内容
                pass
            if depth > 1:
                #利用bs4将网页中的所有a标签都获取出来
                a = BeautifulSoup(data2).findAll('a')
                alist = []
                for i in a:
                    try:
                        #a标签中有很多属性，这里只需要href属性，因为只利用它的超链接，但是也需要判断是否这个超链接是以java开头的
                        if i.attrs['href'] and i.attrs['href'][0] != 'j':
                            alist.append(i.attrs['href'])
                            #网站中href中的网址有两种形式，直接给出http://xxxxx/index.html和/index.html,
                            #如果是第一种就直接添加到列表中，
                            #如果是第二种就自己拼凑成第一种的形式
                            alist = map(lambda i: proto + '://' + domain + i if i[0] == '/' else i, alist)
                    except Exception,e:
                        continue
                for link in alist:
                    print link
                    #这里用递归并带入爬取的层数
                    self.crawl(link,keyword,int(depth)-1)
            else:
                return True
        except Exception,e:
            return True


    def start(self):
        if not self.url.startswith('http://'):
            self.url = "http://" + self.url
            self.crawl(self.url,self.keyword,self.depth)


def useage():
    parser = OptionParser(description = "This is a web spider")
    parser.add_option("-k","--key",dest = "keyword",action = "store",
                     help = "the keyword you want to query")
    parser.add_option("-u","--url",dest = "url", action = "store",
                     help = "the url you want to crawl",metavar = "www.baidu.com")
    parser.add_option("-d","--depth",dest = "depth",action = "store",
                     help = "the depth of the website you want to crawl",default = 1)

    (options,args) = parser.parse_args()
    return options



def main():
    options = useage()
    if not options.keyword or not options.url:
        print "set url and keyword,use the parameters -u and -k"
        return
    crawler = Spider(options)
    crawler.start()
    pass



if __name__=='__main__':
    main()