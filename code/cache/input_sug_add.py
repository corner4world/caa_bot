#!/usr/bin/env python3
#coding:utf8

import time # 时间模块

#-----特定功能模块引用区-----
import redis
import csv


import jieba # 引入结巴分词类库 第三方库
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
#import jieba.posseg as pseg #引入词性标注模式
user_dic_path = "./data/dic/user_dic_jieba.txt"
jieba.load_userdict(user_dic_path)# 导入专用字典

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
rs_redis = redis.Redis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])
#rs_redis = redis.StrictRedis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])

# 自然语言类
class Nlp(object):

    # 中文分词
    def seg(self,txt_p="",way_p="search"):
        list_p = []

        if (len(txt_p) == 0):
            return list_p
        
        #  搜索引擎模式
        if (way_p == "search"):
            try:
                list_p = jieba.cut_for_search(txt_p)
            except:
                list_p = []
                
        # 默认 精确模式   
        if (way_p == "default"):
            try:
                list_p = jieba.cut(txt_p)
            except:
                list_p = []
                
        # 全模式   
        if (way_p == "default"):
            try:
                list_p = jieba.cut(txt_p,cut_all=True)
            except:
                list_p = []
            
        return list_p


def read_csv_data(csv_file):
    
    with open(csv_file, encoding='utf8') as workfile:
        csv_data=csv.reader(workfile)
        return [(r[0],int(r[1])) for r in csv_data]


def main(numb_all=999999999,csv_file = r'./data/test.csv'):

    time_start = datetime.datetime.now()
      #CSV文件的位置
    data=read_csv_data(csv_file)
    e("69")
    #i = 1
    #for x in data:
        #print (i,x)
        #i += 1
        
    app_t = ()
    str_t = ""
    #numb_all = 999999
    k = 1
    m = 0
    nlp = Nlp() # 自然语言处理实例化
    numb_all = len(data)
    
    for x in data:
        
        numb_t = x[1]
        str_t = x[0]
        str_t = str_t.strip()
        key_t = str_t
        arr_t = nlp.seg(txt_p=str_t) #分词处理
                
        # 构造推荐词索引
        if (arr_t):
            for y in arr_t:
                y = y.strip()
                if (y):
                    #rs_redis.r.sadd("set_name","aa")
                    rs_redis.zadd(y,key_t,numb_t)
                    try:
                        print (y,key_t,numb_t) #调试用
                    except:
                        pass
                    m += 1
                    
        print ("第 " + str(k) + " 次处理,完成度：" + str(round(k*100/numb_all,2)) + "%" )
        time.sleep(3)
        #e("64")
        k += 1
        if (k > numb_all):
            break
            
    time_last = str(time_cost(time_start))
    print ("共导入：" + str(k-1) + " 条原生关键词 生成模糊键：" + str(m) + " 条" )
    print ("耗时：",time_last," 秒")
    
if '__main__' == __name__:
    main()