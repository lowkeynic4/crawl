#!/usr/bin/python
#coding:utf-8
import urllib2
import re
import bs4

def getOnePage(url,index=0):
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
def getUrl(childCode):
    try:
        infoList = []
        soup = bs4.BeautifulSoup(childCode)
        table = soup.find('table',attrs={'class':'items table'})
        trs = table.findAll('tr')

        pattern = re.compile(r'<td>.*?</td><td><a href="(.*?)" target="_blank">.*?</a></td>',re.S)
        for tr in trs:
            infoDic = {}
            urls = re.findall(pattern,str(tr))
            for url in urls:
                childUrl ='http://www.sec-wiki.com'+url
                sonCode = getOnePage(childUrl)
                childPattern=re.compile('<strong>(.*?)</strong>.*?<a href="(.*?)">(.*?)</a>',re.S)
                items = re.findall(childPattern,sonCode)
                for item in items:
                    infoDic['time'] = item[0]
                    infoDic['url'] = item[1]
                    infoDic['title'] = item[2]
                    infoList.append(infoDic)
        return infoList
    finally:
        pass


if __name__=="__main__":
    newsPage = "http://www.sec-wiki.com/news/index"
    homeCode = getOnePage(newsPage)
    pattern = re.compile(r'<li class="last"><a href="/news/index\?News_page=(.*?)">',re.S)
    pageSum = re.findall(pattern,homeCode)
    print pageSum
    for i in range(int(pageSum[0])):#从0开始，需要+1
        childCode = getOnePage('http://www.sec-wiki.com/news/index?News_page=',i+1)
        infos = getUrl(childCode)
        for info in infos:
            print info['time']+'%-100s'%(info['title'])+'%-100s'%(info['url'])





