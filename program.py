import os 
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
#解决中文显示问题
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def format_data(path:str, tag:str) -> None:
    '''
    聚合指定tag的小说文本并保存到data中,并生成词云图.
    '''
    result = ''
    for dir_, dir_name, file_names in os.walk(path):

        # 如果是指定tag的文本
        for name in file_names:
            if name[0] == tag[0]:
                with open(path+'/'+name,'r',encoding='utf-8') as f:
                    result = result + f.read()
    with open('data/'+tag+'.txt','w+',encoding='utf-8') as f:
        f.write(result)
    # 中文分词
    temp = jieba.cut(result)
    result = ' '.join([x for x in temp if len(x)>=2])
    # 生成对象
    wc = WordCloud(font_path='msyh.ttf', width=800, height=600, mode='RGBA', background_color='white').generate(result)
    # 显示词云
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    # 保存到文件
    wc.to_file(tag+'.png')




 
if __name__ == '__main__':
    tag_list = ['xuanhuan', 'wuxia', 'dushi',
                'lishi', 'wangyou', 'kehuan', 'nvsheng']
    for tag in tag_list:
        format_data(path = 'data/book_content',tag = tag)