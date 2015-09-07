#!/usr/bin/python
#coding:utf-8
import urllib2
import re
import bs4
import  threading

import sys


from time import sleep
mylock = threading.RLock()
reload(sys)
sys.setdefaultencoding( "utf-8" )
trpattern = re.compile(r'<td>.*?</td><td><a href="(.*?)" target="_blank">.*?</a></td><td>',re.S)
childPattern=re.compile('<strong>(.*?)</strong>.*?<a href="(.*?)">(.*?)</a>',re.S)

def getOnePage(url,index):
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        if index==0:
            pass
        else:
            url = url+str(index)
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        pageCode = response.read().decode('utf-8')
        return pageCode
    except urllib2.URLError,e:
        if hasattr(e,"reason"):
            print u"错误",e.reason
            return None
def getUrl(index):
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        childCode = getOnePage('http://www.sec-wiki.com/news/index?News_page=',index+1)
        infoList = []
        soup = bs4.BeautifulSoup(childCode)
        table = soup.find('table',attrs={'class':'items table'})
        trs = table.findAll('tr')


        for tr in trs:
            infoDic = {}
            urls = re.findall(trpattern,str(tr))
            for url in urls:
                childUrl ='http://www.sec-wiki.com'+url
                request = urllib2.Request(childUrl,headers = headers)
                response = urllib2.urlopen(request)
                pageCode = response.read().decode('utf-8')
                items = re.findall(childPattern,pageCode)
                for item in items:
                 #   print item[0]+'%-100s'%(item[1])+'%-100s'%(item[2])
                    mylock.acquire()
                    fp = open('test.txt','a')
                    fp.writelines('%s %-100s %-100s\n'%(str(item[0]),str(item[1]),str(item[2])))
                    fp.close()
                    mylock.release()
                    print u'我写完了'
    finally:
        pass

if __name__=="__main__":
    threads = []
    newsPage = "http://www.sec-wiki.com/news/index"
    homeCode = getOnePage(newsPage,0)
    pattern = re.compile(r'<li class="last"><a href="/news/index\?News_page=(.*?)">',re.S)
    pageSum = re.findall(pattern,homeCode)
    num = int(pageSum[0])
    #num = 3
    print pageSum
    for i in range(num):#从0开始，需要+1
        t = threading.Thread(target=getUrl,args=(i,))
        threads.append(t)
    for thread in threads:
        thread.start()
        sleep(1)
        thread.join()










