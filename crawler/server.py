'''
分布式爬虫服务端.

'''

import pandas
from filter_callback import url_filter
from redis_ms import Master
import os

from spider import Crawler

ip = '106.14.19.204'
port = 6379
password = 'antony'
mission_queue = 'mission'
data_queue = 'result'


def get_book_list(n:int)->None:
    '''
    获取不同种类小说的书名、简介以及url并保存至csv文件中. 
    n: 每种类型爬取的数量
    '''
    bqg_spider = Crawler()
    # 爬取玄幻，武侠，都市，历史，网游，科幻，女生共六种类型的小说
    tag_list = ['xuanhuan', 'wuxia', 'dushi',
                'lishi', 'wangyou', 'kehuan', 'nvsheng']
    for i in range(len(tag_list)):
        # 每种类型爬取n页数据
        for j in range(1, n+1):
            bqg_spider.add_url(url='https://www.bige7.com/json?sortid=' +
                            str(i+1)+'&page='+str(j), tag=tag_list[i], func=url_filter)
    bqg_spider.run()
    data = bqg_spider.get_data()
    for tag,book_list in data.items():
        file_name = tag+'.csv'
        name_list = []
        intro_list = []
        url_list = []
        for book in book_list:
            name_list.append(book['book_name'])
            intro_list.append(book['introduction'])
            url_list.append('https://www.bige7.com'+book['url'])
        temp_data = pandas.DataFrame({'name':name_list,'introduction':intro_list,'url':url_list})
        temp_data.to_csv('../data/book_list/'+file_name,index=False)    

if __name__ == '__main__':
    # 创建存储文件夹
    if not os.path.exists('../data/book_content'):
            os.makedirs('../data/book_content')
    if not os.path.exists('../data/book_list'):
            os.makedirs('../data/book_list')
    # 初始化Master端
    master = Master(ip=ip, port=port,password=password,
                    mission_queue=mission_queue, result_queue=data_queue)
    master.clear()
    # 任务字典列表
    book_tag_list =['xuanhuan', 'wuxia', 'dushi',
                'lishi', 'wangyou', 'kehuan', 'nvsheng']
    mission_dict = {}
    for index in book_tag_list:
        book_list = pandas.read_csv('../data/book_list/'+index+'.csv')
        names = book_list['name']
        urls = book_list['url']
        # 每种爬10本书
        for j in range(0,10):
            # 每本书爬100章
            mission_dict[index+names[j]] = [urls[j]+str(i)+'.html' for i in range(1,100)]
    print(mission_dict)
    # 总任务数量
    mission_total = 0
    # 计算总任务数量
    for tag, url_list in mission_dict.items():
        for i in url_list:
            # 将任务添加至队列
            master.add_mission(tag+'|'+i)
            print('任务添加: ' + tag)
            mission_total +=1
    # 任务布置完毕
    master.add_mission('END')
    while True:
        content = master.get_data()
        if content != None:
            if content  == 'END':
                print('任务全部完成.')
                break
            else:
                print(content)
                name = content.split('|')[0]
                data = content.split('|')[1]
                with open('../data/book_content/'+name+'.txt','a+',encoding='utf-8') as f:
                    f.write(data)
                print('数据接收: '+name)

            
    # 关闭
    master.close()