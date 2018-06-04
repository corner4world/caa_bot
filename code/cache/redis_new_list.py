#!/usr/bin/env python3
#coding:utf8

import time # 时间模块

#-----特定功能模块引用区-----
import redis
import csv

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 

rs_redis = redis.StrictRedis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])


def read_csv_data(csv_file):
    
    with open(csv_file, encoding='utf8') as workfile:
        csv_data=csv.reader(workfile)
        return [(r[0]) for r in csv_data]


def main(numb_all=999999999):

    time_start = datetime.datetime.now()
    csv_file = r'test.csv'  #CSV文件的位置
    data=read_csv_data(csv_file)

    app_t = ()
    str_t = ""
    #numb_all = 999999
    k = 1
    m = 0
    
    for x in data:
        
        str_t = x.strip()
        arr_t = []
        
        for j in range(len(str_t)+1):
            if (not str_t[:j] in arr_t):
                arr_t.append(str_t[:j])
                m += 1
            
        str_t = str_t[:-1] #向左缩一个字符
        
        for j in range(len(str_t)):
            if (not str_t[j:] in arr_t):
                arr_t.append(str_t[j:])
                m += 1
            
        if (arr_t):
            for y in arr_t:
                rs_redis.setnx(y,str_t)
                #print (y,str_t) #调试用

        k += 1
        if (k > numb_all):
            break
    time_last = str(time_cost(time_start))
    print ("共导入：" + str(k-1) + " 条原生关键词 生成模糊键：" + str(m) + " 条" )
    print ("耗时：",time_last," 秒")
    
if '__main__' == __name__:
    main()