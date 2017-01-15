# -*- coding:utf-8 -*-

from selenium import webdriver
import time
import pymysql
import sys
import importlib
importlib.reload(sys)
# sys.setdefaultencoding('utf8')

def createTable():
    # connect to database
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='my_database', charset='utf8')
    # setup cursor
    cursor = db.cursor()
    cursor.execute("drop table if exists info")
    cursor.execute("create table info(source text, href text, title text, brief text, im text, type text)")
    db.close()

def export(source, href, title, brief, im, type):
    # connect to database
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1111', db='my_database', charset='utf8')
    # setup cursor
    cursor = db.cursor()
    # insert to table
    try:
        cursor.execute("INSERT INTO info VALUES (%s,%s,%s,%s,%s,%s)", (source, href, title, brief, im, type))
        db.commit()
    except:
        db.rollback()
    db.close()

# 定义记录结构体
class score:
        def __init__(self):
            self.source = ''   # 记录来源
            self.title  = ''   # 记录标题
            self.href   = ''   # 记录超链接
            self.brief  = ''   # 记录摘要
            self.im     = ''   # 记录图片
            self.like   = 0    # 记录点赞量
            self.read   = 0    # 记录阅读量

# 阅读量排序并存入数据库
def bubbleSort(url_news_list, numberOfNote):
    for j in range(numberOfNote - 1, 0, -1):
        for i in range(j):
            if url_news_list[i].read < url_news_list[i+1].read:
                url_news_list[i], url_news_list[i+1] = url_news_list[i+1], url_news_list[i]
    return url_news_list



def spider_url_content(url,url_news_list, counter, step):
    try:
        browser = webdriver.PhantomJS()  # 打开 PhantomJS 浏览器
        browser.set_page_load_timeout(200)   # 防止页面加载个没完

        # 浏览器打开爬取页面
        browser.get(url)

        p_source = browser.find_elements_by_id("nickname_p")   # 获取类型以及文章来源
        print(p_source[0].text)

        time.sleep(1)
        xpath_title = "//div[@class='p_1']/p/a"  # 获取文章标题
        p_title = browser.find_elements_by_xpath(xpath_title)

        xpath_href = "//div[@class='p_1']/p/a"  # 获取文章原文链接
        # href = (browser.find_elements_by_xpath(xpath_title)).get_attribute("href")
        p_href = browser.find_elements_by_xpath(xpath_href)

        # 获取文章摘要内容

        xpath_brief = "//div[@class='wz']/p/a"
        p_brief = (browser.find_elements_by_xpath(xpath_brief))

        # 获取文章图片链接
        xpath_img = "//div[@class='tp']/a/img"
        p_im = browser.find_elements_by_xpath(xpath_img)

        # 获取阅读量和点赞数
        xpath_read = "//div[@class='m_p']/span[@class='orange']"

        for i in range(step):
            try:
                url_news_list[counter+i].source = p_source[0].text

                url_news_list[counter+i].title = p_title[i].text
                print("title: " + url_news_list[counter+i].title)

                url_news_list[counter+i].href = p_href[i].get_attribute("href")
                print("href: " + url_news_list[counter+i].href)

                url_news_list[counter+i].brief = p_brief[i].text
                print("brief: " + url_news_list[counter+i].brief)

                url_news_list[counter+i].im = p_im[i].get_attribute("src")
                print("image: " + url_news_list[counter+i].im)

                url_news_list[counter+i].read = int(browser.find_elements_by_xpath(xpath_read)[2*i].text)
                url_news_list[counter+i].like = int(browser.find_elements_by_xpath(xpath_read)[2*i+1].text)
                print("read: " + str(url_news_list[counter+i].read), "like: " + str(url_news_list[counter+i].like) + " \n" )

            except Exception as ex:
                print("error msg: " + str(ex))
                continue


            # time.sleep(1)

        browser.quit()                      # 关闭浏览器
    except Exception as ex:
        print("error msg: " + str(ex))

if __name__ == '__main__':

    # 自主添加公众号类型以及url即可
    
    url_notification = ["http://www.gsdata.cn/index.php/rank/single/xxxxxx"]

    url_news = ["http://www.gsdata.cn/index.php/rank/single/xxxxxx"]

    url_association = ["http://www.gsdata.cn/index.php/rank/single/xxxxxx"]

    url_class = ["http://www.gsdata.cn/index.php/rank/single/xxxxxx"]
  

    # 创建一个表
    createTable()
    # 文章分类
    type = ["重大通知", "时讯新闻", "社团风采", "班级媒体"]

    # 定义一个计数器
    counter = 0
    # 所要抓取的每个公众号中文章数
    step = 3
    # 每一类公众号所需文章数
    finalAmount = 5
    # 初始化表单

    # 重大通知类的表单,长度为公众号数目*每个公众号中的文章数
    url_notification_list = [score() for i in range(step*len(url_notification))]
    url_news_list = [score() for i in range(step*len(url_news))]
    url_association_list = [score() for i in range(step*len(url_association))]
    url_class_list = [score() for i in range(step*len(url_class))]

    for url in url_notification:
        spider_url_content(url, url_notification_list, counter, step)
        # 每次抓取公众号中的step篇文章，
        counter += step
    # 根据阅读量排序
    temp = bubbleSort(url_notification_list, len(url_notification_list))
    # 只将阅读量前3的文章导入数据库
    for k in range(finalAmount):
        export(temp[k].source, temp[k].href, temp[k].title, temp[k].brief, temp[k].im, type[0])  # 导出到数据库
        print('重大通知 good successful save!')

    # 重新初始化变量
    counter = 0
    k = 0

    for url in url_news:
        spider_url_content(url, url_news_list, counter, step)
        # 每次抓取公众号中的step篇文章，
        counter += step
    # 根据阅读量排序
    temp = bubbleSort(url_news_list, len(url_news_list))
    # 只将阅读量前3的文章导入数据库
    for k in range(finalAmount):
        export(temp[k].source, temp[k].href, temp[k].title, temp[k].brief, temp[k].im, type[1])  # 导出到数据库
        print('时讯新闻 good successful save!')

    # 重新初始化变量
    counter = 0
    k = 0

    for url in url_association:
        spider_url_content(url, url_association_list, counter, step)
        # 每次抓取公众号中的step篇文章，
        counter += step
    # 根据阅读量排序
    temp = bubbleSort(url_association_list, len(url_association_list))
    # 只将阅读量前3的文章导入数据库
    for k in range(finalAmount):
        export(temp[k].source, temp[k].href, temp[k].title, temp[k].brief, temp[k].im, type[2])  # 导出到数据库
        print('社团风采 good successful save!')

    # 重新初始化变量
    counter = 0
    k = 0

    for url in url_class:
        spider_url_content(url, url_class_list, counter, step)
        # 每次抓取公众号中的step篇文章，
        counter += step
    # 根据阅读量排序
    temp = bubbleSort(url_class_list, len(url_class_list))
    # 只将阅读量前3的文章导入数据库
    for k in range(finalAmount):
        export(temp[k].source, temp[k].href, temp[k].title, temp[k].brief, temp[k].im, type[3])  # 导出到数据库
        print('班级媒体 good successful save!')
