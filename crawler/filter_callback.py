'''
Filter Callback.
----------------

该文件提供了爬虫所需要的回调函数.
'''

from lxml import etree
import re
import requests
import json


def url_filter(r: requests.Response) -> list:
    '''
    小说基本信息以及url爬取回调函数.
    '''
    raw_data = json.loads(r.text)
    data = [{'book_name': x['articlename'], 'introduction':x['intro'],
             'url':x['url_list']} for x in raw_data]
    return data


def chapter_filter(r:requests.Response)->list:
    '''
    小说每章信息的爬取回调函数.
    '''
    html_dom =  etree.HTML(r.text)
    result = html_dom.xpath('//div[@id = "chaptercontent"]/text()')
    result = re.sub('\s','',''.join(result))
    return [result]

