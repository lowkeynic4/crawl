使用python编写一个网站爬虫程序，支持参数如下：
spider.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number --dbfile  filepath  --key=”HTML5”

参数说明：
> -u 指定爬虫开始地址 
-d 指定爬虫深度  
--thread 指定线程池大小，多线程爬取页面，可选参数，默认10  
--dbfile 存放结果数据到指定的数据库（sqlite）文件中  
--key 页面内的关键词，获取满足该关键词的网页，可选参数，默认为所有页面  
-l 日志记录文件记录详细程度，数字越大记录越详细，可选参数，默认spider.log  
--testself 程序自测，可选参数

功能描述：

* 指定网站爬取指定深度的页面，将包含指定关键词的页面内容存放到sqlite3数据库文件中
* 程序每隔10秒在屏幕上打印进度信息
* 支持线程池机制，并发爬取网页
* 代码需要详尽的注释，自己需要深刻理解该程序所涉及到的各类知识点
* 需要自己实现线程池

> 提示1：使用re  urllib/urllib2  beautifulsoup/lxml2  threading optparse Queue  sqlite3 logger  doctest等模块  
提示2：注意是“线程池”而不仅仅是多线程  
提示3：爬取sina.com.cn两级深度要能正常结束

建议程序可分阶段，逐步完成编写，例如：
> 版本1:Spider1.py -u url -d deep  
版本2：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself  
版本3：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number  
版本4：剩下所有功能

　　我的程序是遵循以上的版本写的，但是其中缺少要求中的两项，一个是自测，一个是每隔10秒打印。因为没有接触过python的正规项目，所以不知道自测怎么写；10秒打印只想到打印出一共扫描了多少网址，这个倒是简单，但是总感觉这样打印和题目中的要求有差别，所以也没写。在此留底，待以后改进。具体内容都在文件注释中。

