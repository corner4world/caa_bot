#!/usr/bin/env python3
#coding:utf8
import redis
import csv

REDIS_HOST = 'localhost'
REDIS_PASS = '' #如果没密码的话，这里是空字符串
REDIS_PORT = 6379
REDIS_DB = 0
redis_conn = redis.StrictRedis(host=REDIS_HOST, password=REDIS_PASS, port=REDIS_PORT, db=REDIS_DB)

# 循环输入
i = 1
while (i<=999999999):
    
    key_p = input("请输入关键词,exit退出 >>> ")
    
    if (key_p == "exit"):
        break
    
    result = redis_conn.get(key_p)
    if (result):
        str_t = result.decode("utf-8")
        print("找到键>>>",key_p," 键值>>>",str_t)
    else:
        print("未找到>>>",key_p)
        
    
    i += 1
