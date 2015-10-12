#coding:utf-8
from optparse import OptionParser
import urllib2
from bs4 import BeautifulSoup
import urllib
import re
import StringIO, gzip
import logging
import threading
import Queue
import datetime
import sqlite3
LEVELS={   #日志级别
        1:'CRITICAL',
        2:'ERROR',
        3:'WARNING',
        4:'INFO',
        5:'DEBUG',#数字越大记录越详细
        }
lock = threading.RLock() #设置线程锁
visit = threading.RLock()
alreadyVisit = []

class MySqlite():
    def __init__(self,path="spider.db"):
        try:
            self.conn = sqlite3.connect(path)
            self.cur = self.conn.cursor()
        except Exception,e:
            return

    def create(self,table):
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS %s(Id INTEGER PRIMARY KEY AUTOINCREMENT,Url TEXT,Data TEXT)"% table)
            self.conn.commit()
        except Exception,e:
            self.conn.rollback()
            return

    def insert(self,table,url,data):
        try:
            self.cur.execute("insert into %s(Url,Data) VALUES ('%s','%s')"%(table,url,data))
            self.conn.commit()
        except Exception,e:
            self.conn.rollback()
            return

    def close(self):
        self.cur.close()
        self.conn.close()


class MyThread(threading.Thread):
    def __init__(self, workQueue, resultQueue,timeout=20, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        #线程在结束前等待任务队列多长时间
        self.timeout = timeout
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.start()

    def run(self):
        while True:
            try:
                #从工作队列中获取一个任务
                callable, args = self.workQueue.get(timeout=self.timeout)
                #我们要执行的任务
                callable(*args)
                #把任务返回的结果放在结果队列中
 #               self.resultQueue.put(res+" | "+self.getName())
            except Queue.Empty: #任务队列空的时候结束此线程
                break
            except Exception,e:
                return -1


class ThreadPool:
    def __init__( self, num_of_threads=10):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.threads = []
        self.__createThreadPool( num_of_threads )

    def __createThreadPool( self, num_of_threads ):
        for i in range( num_of_threads ):
            thread = MyThread( self.workQueue, self.resultQueue )
            self.threads.append(thread)

    def wait_for_complete(self):
        #等待所有线程完成。
        while len(self.threads):
            thread = self.threads.pop()
            #等待线程结束
            if thread.isAlive():#判断线程是否还存活来决定是否调用join
                thread.join()

    def add_job(self, callable, *args):
        self.workQueue.put((callable,args))


class Spider():
    def __init__(self,args,tp,table):
        self.url = args.url
        self.depth = args.depth
        self.keyword = args.keyword
        self.threadpool = tp
        self.dbpath = args.dbpath
        self.table = table
    def check_visit(self,url):
        if url in alreadyVisit:
            return True
        else:
            alreadyVisit.append(url)
            return False

    def crawl(self,url,keyword,depth):
        header={"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50",
                'Accept-Encoding':'gzip, deflate'}
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
                    data = gziper.read()
                    try:
                        content = data.decode('gbk')
                    except UnicodeDecodeError,e:
                        content = data.decode('utf-8', 'ignore')

        except urllib2.HTTPError,e:
            logging.critical("%s"%e)
            return -1

        try:
            proto, rest = urllib.splittype(url)
            domain = urllib.splithost(rest)[0]
            m = re.compile(r'%s' % unicode(keyword, 'utf-8')).findall(content)
            if m:
                logging.info('%s',url)
                lock.acquire()
                db = MySqlite(self.dbpath)
                db.insert(self.table,url,content)
                db.close()
                lock.release()
                #print content
            if depth > 1:
                a = BeautifulSoup(data,"lxml").findAll('a')
                alist = []
                for i in a:
                    try:
                        if i.attrs['href'] and i.attrs['href'][0] != 'j':
                            alist.append(i.attrs['href'])
                            alist = map(lambda i: proto + '://' + domain + i if i[0] == '/'  else i, alist)
                    except Exception,e:
                        continue
                self.analysis(alist,keyword,depth)

            else:
                return True
        except Exception,e:
            logging.critical("%s",e)
            return
    #新创建了一个函数，相当于分发器，因为应用了线程池之后分发任务和处理任务就不能在一起了，所以单独出来
    def analysis(self,alist,keyword,depth):
        for link in alist:
            if self.check_visit(link):
                continue
            else:
                print link
                self.threadpool.add_job(self.crawl,link,keyword,int(depth)-1)



    def start(self):
        if not self.url.startswith('http://'):
            self.url = "http://" + self.url

        self.threadpool.add_job(self.crawl,self.url,self.keyword,self.depth)
        self.threadpool.wait_for_complete()


def useage():
    #如果没有指定log文件，默认为本目录下的spider.txt
    #如果没有指定爬取的层数，默认为2
    #如果没有指定日志级别，默认为DEBUG,也就是最详细
    #线程池默认线程数为10,
    #数据库文件默认为本目录下spider.db
    parser = OptionParser(description = "This is a web spider")
    parser.add_option("-k","--key",dest = "keyword",action = "store",
                      help = "the keyword you want to query")
    parser.add_option("-u","--url",dest = "url", action = "store",
                      help = "the url you want to crawl",metavar = "www.baidu.com")
    parser.add_option("-d","--depth",dest = "depth",action = "store",
                      help = "the depth of the website you want to crawl",default = 2)
    parser.add_option("-f", "--file", dest="logfile", action="store",
                      help="name of the logfile", default='spider.log')
    parser.add_option("-l", "--level", dest="level", action = "store",type="int",
                      help="Log level, default 5(DEBUG)", default=5)
    parser.add_option("-t", "--thread", dest="threads", action="store",type="int",
                      help="thread number,default:10", default=10)
    parser.add_option("-b","--dbfile",dest = "dbpath", action = "store",
                      help = "the name of the database", metavar = "spider.db")
    (options,args) = parser.parse_args()
    return options

def init_log(logfile,level):
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
    if not options.keyword or not options.url:
        print "set url and keyword,use the parameters -u and -k"
        return
    init_log(options.logfile,options.level)
    tp = ThreadPool(options.threads)#利用线程数来初始化线程池

    table = datetime.datetime.now().strftime("%y%m%d%H%M%S")#利用时间来为新建的表来命名
    table = "s"+table#因为sqllite不能使用纯数字命名表名，所以在时间前加上一个's'字符

    #创建此次扫描的表
    tb = MySqlite(options.dbpath)
    tb.create(table)
    tb.close()

    crawler = Spider(options,tp,table)
    crawler.start()


if __name__=='__main__':
    main()