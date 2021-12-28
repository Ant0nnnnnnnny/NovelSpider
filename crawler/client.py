'''
分布式爬虫客户端.
'''

from filter_callback import chapter_filter
from redis_ms import Slave
from spider import Crawler

ip = '106.14.19.204'
port = 6379
password = 'antony'
mission_queue = 'mission'
data_queue = 'result'



if __name__ == '__main__':

    # 初始化Slave端
    slave = Slave(ip=ip, port=port,password=password,
                  mission_queue=mission_queue, result_queue=data_queue)
    chapter_spider = Crawler()
    while True:
        misson = slave.get_mission()
        if misson == 'END' or misson == None:
            print('处理数据上传完毕.')
            slave.sub_data('END')
            break
        print('任务接收: '+misson)
        tag = misson.split('|')[0]
        url = misson.split('|')[1]
        data = chapter_spider.run_once(url,tag,chapter_filter)
        for tag,content in data.items():
            slave.sub_data(tag+'|'+''.join(content))
        print('任务已完成: '+misson)