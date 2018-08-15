import lxml
import requests  # 导入网页请求库
from bs4 import BeautifulSoup  # 导入网页解析库
import pprint  # 使打印出来的列表更方便看
import json  # 用于将列表字典（json格式）转化为相同形式字符串，以便存入文件
import pandas as pd
import time


def start_requests(url):
    print(url)  # 用这条命令知道当前在抓取哪个链接，如果发生错误便于调试
    r = requests.get(url)
    return r.content


def parse(text, k):
    for i in range(0, k):
        soup = BeautifulSoup(text, 'lxml')
        movie_list = soup.find_all('li', class_=' j_thread_list clearfix')
        for movie in movie_list:
            mydict = {}
            mydict['name'] = movie.find('a').text
            mydict['lianjie'] = "http://tieba.baidu.com" + movie.find('a')['href']
            email = movie.find('span', class_='tb_icon_author')['title'].replace('主题作者: ', '')
            mydict['email'] = email if email else None  # 抓取10页就总会遇到这种特殊情况要处理

            mydict['xi'] = movie.find('span').text
            result_list.append(mydict)  # 向全局变量result_list中加入元素
        nextpage = soup.find('a', class_='next pagination-item ')  # 找到“下一页”位置
        if nextpage:  # 找到的就再解析，没找到说明是最后一页，递归函数parse就运行结束
            nexturl = 'http:' + nextpage['href']
            text = start_requests(nexturl)


def write_json(result):
    s = json.dumps(result, indent=4, ensure_ascii=False)
    with open('movies.json', 'w', encoding='utf-8') as f:
        f.write(s)


def main():
    text = start_requests(baseurl)
    k = 5
    parse(text, k)
    write_json(result_list)  # 所有电影都存进去之后一起输出到文件


if __name__ == '__main__':
    baseurl = 'https://tieba.baidu.com/f?kw=%E7%81%AB%E7%84%B0%E4%B9%8B%E7%BA%B9%E7%AB%A0if&ie=utf-8&pn=0'
    result_list = []
    main()



def get_content(url):
    '''
    分析贴吧的网页文件，整理信息，保存在列表变量中
    '''

    # 初始化一个列表来保存所有的帖子信息：
    comments = []
    # 首先，我们把需要爬取信息的网页下载到本地
    html = get_html(url)

    # 我们来做一锅汤
    soup = BeautifulSoup(html, 'lxml')

    # 按照之前的分析，我们找到所有具有‘ j_thread_list clearfix’属性的li标签。返回一个列表类型。
    liTags = soup.find_all('li', attrs={'class': ' j_thread_list clearfix'})

    # 通过循环找到每个帖子里的我们需要的信息：
    for li in liTags:
        # 初始化一个字典来存储文章信息
        comment = {}
        # 这里使用一个try except 防止爬虫找不到信息从而停止运行
        try:
            # 开始筛选信息，并保存到字典中
            comment['title'] = li.find(
                'a', attrs={'class': 'j_th_tit '}).text.strip()
            comment['link'] = "http://tieba.baidu.com/" + \
                              li.find('a', attrs={'class': 'j_th_tit '})['href']
            comment['name'] = li.find(
                'span', attrs={'class': 'tb_icon_author '})['title'].replace('主题作者：'.encode('utf-8'),
                                                                             ''.encode('utf-8'))
            comment['time'] = li.find(
                'span', attrs={'class': 'pull-right is_show_create_time'}).text.strip()
            comment['replyNum'] = li.find(
                'span', attrs={'class': 'threadlist_rep_num center_text'}).text.strip()
            comments.append(comment)
        except:
            print('出了点小问题')

    return comments


def Out2File(dict):
    '''
    将爬取到的文件写入到本地
    保存到当前目录的 TTBT.txt文件中。

    '''
    with open('TTBT.txt', 'a+') as f:
        for comment in dict:
            f.write('标题： {} \t 链接：{} \t 发帖人：{} \t 发帖时间：{} \t 回复数量： {} \n'.format(
                comment['title'], comment['link'], comment['name'], comment['time'], comment['replyNum']))

        print('当前页面爬取完成')


def main(base_url, deep):
    url_list = []
    # 将所有需要爬去的url存入列表
    for i in range(0, deep):
        url_list.append(base_url + '&pn=' + str(50 * i))
    print('所有的网页已经下载到本地！ 开始筛选信息。。。。')

    # 循环写入所有的数据
    for url in url_list:
        content = get_content(url)
        Out2File(content)
    print('所有的信息都已经保存完毕！')
