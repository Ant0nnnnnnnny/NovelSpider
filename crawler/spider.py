import time
import requests
class Crawler:
    '''
    Crawler类
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    获取指定网页中的内容
    '''

    # 请求头，基本的防止反爬
    __headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

    # 索引URL字典
    __url_index_dict = {}
    # 结果URL字典
    __result_dict = {}
    # 指定特殊headers
    __headers_dict = {}
    # 回调函数字典
    __func_dict = {}

    def __init__(self) -> None:
        pass

    def add_url(self, url: str, tag: str, func, headers=None) -> None:
        '''
        添加URL到索引URL字典中, 并指定tag和回调函数func(), 并支持指定特殊headers. 允许不同url共用同一tag.
        其中, 回调函数func接收一个Response对象作为参数, 并返回一个列表, 列表中为url内符合要求的集合.

        >>> def filter(r: Resonse) -> list:
              url_list = []
        >>>   ...
        >>>   return url_list
        >>> url_crawler = UrlCrawler()
        >>> url_crawler.add_url('https://tieba.baidu.com/f?ie=utf-8&kw=','baidu',filter)
        '''

        # 判断tag是否已经存在
        if tag in self.__url_index_dict:
            self.__url_index_dict[tag].append(url)
        else:
            self.__url_index_dict[tag] = [url]
        # 如果要求使用指定headers
        if headers is not None:
            self.__headers_dict[tag] = headers
        # 添加回调函数
        self.__func_dict[tag] = func

    def __crawler(self, tag, url_list, headers, timeout, callback):
        for url in url_list:
            r = None
            print('Downloading: ' + url)
            try:
                r = requests.get(
                    url=url, headers=headers, timeout=timeout)
                r.raise_for_status()
                print('Download successfully.')
            except:
                print('Error in :' + url)

            result = callback(r)
            self.__result_dict[tag] = self.__result_dict[tag] + result if tag in self.__result_dict else result
    def run(self, time_out=3) -> None:
        '''
        启动爬虫.
        '''
        for key, value in self.__url_index_dict.items():
            time_before = time.time()
            self.__crawler(tag=key,
                           url_list=value, headers=self.__headers_dict[key] if key in self.__headers_dict else self.__headers, timeout=time_out,callback= self.__func_dict[key])
            time_after = time.time()
            print('-----'+str(key)+': '+ str(time_after-time_before)+' s.')
    def run_once(self,url,tag,callback,headers = None,timeout = 3):
        '''
        一次性爬取读入.
        '''
   
        r = None
        print('Downloading: ' + url)
        try:
            r = requests.get(
                url=url, headers=headers if headers != None else self.__headers, timeout=timeout)
            r.raise_for_status()

            print('Download successfully.')

        except:
            print('Error in :' + url)

        result = callback(r)
        return {tag:result}

    def clear(self):
        self.__result_dict = {}
        
    def get_data(self):
        return self.__result_dict
