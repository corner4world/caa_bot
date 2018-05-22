#!/usr/bin/env python3
#coding:utf8
import redis
import csv

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
rs_redis = redis.Redis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])

list_t = []
numb_r = 999999999 #设置循环极限次数
numb_limit = 10 #列表分页阈值
rank_if = 0

# 查询类
class Redis_fit(object):

    # 输入关键词匹配
    def word_fit(self,key_p="",numb_limit=10,rank_if=0):
        pass
        
# 循环输入
i = 1
while (i<=numb_r):
    
    key_p = input("请输入关键词,exit退出 >>> ")
    
    if (key_p == "exit"):
        break
    if (rank_if == 1):
        result = rs_redis.zrevrange(key_p,0,numb_limit,withscores=True,score_cast_func=int)
    else:
        result = rs_redis.zrevrange(key_p,0,numb_limit,withscores=False,score_cast_func=int)
    if (result):
        for x in result:
            
            if (rank_if == 1):
                str_t = x[0].decode("utf-8")
                print("找到键>>>",key_p," 键值>>>",str_t,"rank值",str(x[1]))
            else:
                str_t = x.decode("utf-8")
                print("找到键>>>",key_p," 键值>>>",str_t)
    else:
        print("未找到>>>",key_p)
        
    
    i += 1

# 函数测试区
redis_fit = Redis_fit() # 匹配对象实例化