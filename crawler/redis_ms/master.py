import redis
class Master:
    '''
    基于Master-Slave模型的分布式爬虫. 
    -------------------------------
    使用redis.
    ---------
    Master: 负责派发任务,接收Slave处理过的数据,调度队列.

    Slave: 负责从队列中接收任务,并将处理之后的数据上交给Master.
    '''

    __ip = '127.0.0.1'
    __port = '6379'
    __password = None
    __client = None
    __mission_queue = None
    __result_queue = None
    def __init__(self,mission_queue:str,result_queue:str, ip:str, port = 6379,password = None) -> None:
        '''
        初始化Master. 连接至redis.
        mission_queue: 任务队列名称.
        result_queue: 数据队列名称.
        '''
        self.__ip = ip
        self.__port = port
        self.__password = password
        self.__mission_queue = mission_queue
        self.__result_queue = result_queue
        if self.__password is None:
            self.__client = redis.StrictRedis(host = self.__ip,port= self.__port,)
        else:
            self.__client = redis.StrictRedis(host = self.__ip,port= self.__port,password=self.__password)
        
    def add_mission(self,content:str)->int:
        '''
        向任务队列中添加任务, 返回队列id.
        '''
        return self.__client.lpush(self.__mission_queue,content)
    
    def get_data(self)->str:
        '''
        从数据队列中获取Slave处理完毕的数据.
        '''
        result = self.__client.rpop(self.__result_queue).decode(encoding='UTF-8')
        
        return result

    def close(self)->None:
        '''
        关闭连接.
        '''
        self.__client.close()