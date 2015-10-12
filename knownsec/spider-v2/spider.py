#coding:utf-8
from optparse import OptionParser
import urllib2
from bs4 import BeautifulSoup
import urllib
import re
import StringIO, gzip
import logging

LEVELS={   #日志级别
        1:'CRITICAL',
        2:'ERROR',
        3:'WARNING',
        4:'INFO',
        5:'DEBUG',#数字越大记录越详细
        }

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
                if "gzip" in resHeader.get("Content-Encoding"):
                    compressedstream = StringIO.StringIO(content)
                    gziper = gzip.GzipFile(fileobj=compressedstream)
                    data2 = gziper.read()
                    try:
                        content = data2.decode('gbk')
                    except UnicodeDecodeError,e:
                        content = data2.decode('utf-8', 'ignore')

        except urllib2.HTTPError,e:
            logging.critical("%s"%e)
            return -1


        try:
            proto, rest = urllib.splittype(url)
            domain = urllib.splithost(rest)[0]
            m = re.compile(r'%s' % unicode(keyword, 'utf-8')).findall(content)
            if m:
                logging.info('%s',url)
                #print content
            if depth > 1:
                a = BeautifulSoup(data2,"lxml").findAll('a')
                alist = []
                for i in a:
                    try:
                        if i.attrs['href'] and i.attrs['href'][0] != 'j':
                            alist.append(i.attrs['href'])
                            alist = map(lambda i: proto + '://' + domain + i if i[0] == '/' else  i, alist)
                    except Exception,e:
                        continue
                for link in alist:
                    #print link
                    self.crawl(link,keyword,int(depth)-1)
            else:
                return True
        except Exception,e:
            logging.critical("%s",e)
            return


    def start(self):
        if not self.url.startswith('http://'):
            self.url = "http://" + self.url
            self.crawl(self.url,self.keyword,self.depth)


def useage():
    #如果没有指定log文件，默认为本目录下的spider.txt
    #如果没有指定爬取的层数，默认为2
    #如果没有指定日志级别，默认为DEBUG,也就是最详细
    parser = OptionParser(description = "This is a web spider")
    parser.add_option("-k","--key",dest = "keyword",action = "store",
                     help = "the keyword you want to query")
    parser.add_option("-u","--url",dest = "url", action = "store",
                     help = "the url you want to crawl",metavar = "www.baidu.com")
    parser.add_option("-d","--depth",dest = "depth",action = "store",
                     help = "the depth of the website you want to crawl",default = 2)
    parser.add_option("-f", "--file", dest="logfile", action="store",
                     help="name of the logfile", default='spider.log')
    parser.add_option("-l", "--level", dest="level", action = "store",
                     type="int",help="Log level, default 5(DEBUG)", default = 5)


    (options,args) = parser.parse_args()
    return options

def init_log(logfile ,level):
    #输出到日志文件中
    logging.basicConfig(
        #这里说明下为什么要定义一个LEVELS字典:logging模块中默认DEBUG为10，CRITICAL为50，也就是说数字越小越详细
        #但是人们的正常使用习惯是数字越大输出越详细，所以这里需要一个翻转，于是用到了一个字典
                    level    = LEVELS.get(level,"CRITICAL"),
                    format   = 'LINE %(lineno)-4d  %(asctime)s  %(levelname)-8s %(message)s',
                    datefmt  = '%m-%d %H:%M',
                    filename = logfile,
                    filemode = 'a')

    #这里输出到屏幕，输出级别为INFO
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)



def main():
    options = useage()
    if not options.keyword or not options.url :
        print "set url and keyword,use the parameters -u and -k "
        return
    init_log(options.logfile,options.level)
    crawler = Spider(options)
    crawler.start()
    pass



if __name__=='__main__':
    main()