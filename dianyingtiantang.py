#!/usr/bin/python
#coding:utf-8

import urllib2
import bs4
import re
import chardet

def get_films_sorted(url):
    film_list = []
    headers = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    
    # 创建OpenerDirector对象并打开网页
    opener = urllib2.build_opener()
    opener.addheaders = [headers]
    content = opener.open(url).read()
    encoding = chardet.detect(content)['encoding']
    content = content.decode(encoding, 'ignore')

    # 创建网页的BeautifulSoup对象
    soup = bs4.BeautifulSoup(content)
    films_set = soup.findAll('a', class_='ulink')  # list of tags "a" with attribute "class=ulink"

    for film in films_set:
        film_dic = {}
        # 提取地址,并与主域名拼凑
        film_href = "http://www.dytt8.net" + film['href']
        # 打开地址,获取第二页代码
        film_content = urllib2.urlopen(film_href).read()
        encoding = chardet.detect(film_content)['encoding']
        film_content = film_content.decode(encoding, 'ignore')
        # 获取HTML文档的BeautifulSoup对象
        film_soup = bs4.BeautifulSoup(film_content)
        # 提取电影title及下载地址
        title_all = film_soup.findAll('div', class_='title_all')
        film_dic['film_title'] = title_all[-1].h1.font.string
        if film_dic['film_title']:
            film_dic['download_url'] = film_soup.findAll('td', style='WORD-WRAP: break-word')[0].a['href']
            #这获取的和在浏览器中f12看见的代码不一致,浏览器中是经过js处理过的,可以对比一下
            #print film_soup.findAll('td', style='WORD-WRAP: break-word')[0]
            film_list.append(film_dic)
        else:
            break
    return film_list


url = "http://www.dytt8.net/html/gndy/dyzz/index.html"

for film_dic in get_films_sorted(url):
    print film_dic['film_title']
    print film_dic['download_url']