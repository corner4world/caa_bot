#!/usr/bin/env python3
#coding:utf8
import redis
import csv

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
rs_redis = redis.Redis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])

# 主运行

# 停用词查询
def kw_stop(key_p=""):
    str_t = ""
    result = rs_redis.get("s_" + key_p)
    if (result):
        str_t = result.decode("utf-8")
    return str_t
    
# 命名实体词查询
def kw_ne(key_p=""):
    str_t = ""
    result = rs_redis.get("n_" + key_p)
    if (result):
        str_t = result.decode("utf-8")
    return str_t

def main():

    #1 过程一
    #2 过程二
    #3 过程三
    print("")
    
if __name__ == '__main__':
    main()