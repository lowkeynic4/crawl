#coding:utf-8

import urllib2
import bs4
import re
import chardet

def get_films_sorted(url):
    #urllib2.urlopen()函数不支持验证、cookie或者其它HTTP高级功能。要支持这些功能，必须使用build_opener()函数创建自定义Opener对象
    headers = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    opener = urllib2.build_opener()  # create an OpenerDirector object
    opener.addheaders = [headers]    # 设置http头
    content = opener.open(url).read()  #请求url然后获取response回来的内容
    #以上几步和urlopen()函数的功能相同
    encoding = chardet.detect(content)['encoding']  #取得网页编码
    content = content.decode(encoding, 'ignore')    #python内部编码为unicode,此处需要用decode将字符串转换为unicode，ignore为忽略非法字符，还有replace会用？代替非法字符

    soup = bs4.BeautifulSoup(content)
    div_now_playing=soup.find('div', id='nowplaying')   # 返回第一个指定属性的div标签的所有内容
    list_li_films = div_now_playing.findAll('li', class_="list-item")    # 返回一个包含所有li标签,class属性为"list-item"的列表

    films_list = []

    # 遍历每个电影
    for li_film in list_li_films:

        # 字典
        film_dic = {}

        if (li_film.ul.li['class'] == ['poster']):
            # 提取相应信息
            film_dic['film_name'] = li_film.ul.li.img['alt']
            film_dic['film_release'] = li_film['data-release']
            film_dic['film_actors'] = li_film['data-actors']
            film_dic['film_director'] = li_film['data-director']

            # 属性也可以用字典定义
            if li_film.find('span', attrs={'class': 'subject-rate'}):
                # 如果有评分
                film_dic['film_points'] = li_film.find('span', {'class','subject-rate'}).string.strip()
                film_dic['points'] = float(film_dic['film_points'])
            else:
                # 如果没评分
                film_dic['film_points'] = u'暂无评分'
                film_dic['points'] = 0


            # stars为class属性的内容
            stars = li_film.find('li', attrs={'class': 'srating'}).span['class']
            if stars[0] != 'rating-star':
                # 没有评星
                film_dic['film_stars'] = u'评价人数不足'
            else:
                # 有评星
                str_stars=stars[1]  #stars[1] = allstar25
                #将allstar后面的数字转换出来
                match = re.match(r'^(\D+)(\d{2})$', str_stars) #\D非数字 ^以什么开头 \d为数字 {2}为匹配前边两次 $以什么结尾
                #match.groups()为全部上面括号里的内容，一个是allstar,另一个是25,序数从1开始,match.groups(2)就是25
                film_dic['film_stars'] = str(int(match.group(2)) / 10).decode('utf-8') + u'颗星'

        films_list.append(film_dic)
    films_list_sorted = sorted(films_list, key=lambda x:x['points'], reverse = True)
    return films_list_sorted



if __name__=="__main__":
    url="http://movie.douban.com/nowplaying/beijing/"
    for film_dic in get_films_sorted(url):
        print "%-20s"%(film_dic['film_name'])+"%-10s"%str(film_dic['points'])+"%-10s"%(film_dic['film_stars'])