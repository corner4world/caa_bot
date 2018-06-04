#!/usr/bin/env python3
#coding:utf8

#-----系统自带必备模块引用-----

import sys
import time # 时间模块

#-----特定功能模块引用区-----
import redis
import csv

#-----DIY自定义库模块引用-----

sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
import config #系统配置参数
import cgi # CGI模式 取得shell参数用
from diy.inc_hash import hash_make # 基本自定义hash模块

path_dic_local = config.dic_config["path_dic"]
import jieba # 引入结巴分词类库 第三方库
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
#import jieba.posseg as pseg #引入词性标注模式
user_dic_path = path_dic_local + "user_dic_jieba.txt"
jieba.load_userdict(user_dic_path)# 导入专用字典

rs_redis = redis.Redis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])

form = cgi.FieldStorage() #处理提交的参数

if form.getvalue('a'):
    args_list = form["a"].value
else:
    args_list = []

dic_args_cmd = args2dic(args_list)

if ("action" in dic_args_cmd):
    action = dic_args_cmd["action"]
else:
    action = ""

# 分支执行函数
def run_it():

    txt = ""
    #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
    rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
    #rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
    #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
    
    # 导入停用词
    if (action == "kw_stop"):
    
        time_start = datetime.datetime.now()
        
        numb_all = 0
        str_t = ""

        sql = "select keyword from keyword_stop"
        res, rows = rs_way_mysql.read_sql(sql)
        if (res < 1):
            return "数据库为空或数据库读取错误"
        else:
            numb_all = res

        i = 1
        for row in rows:
        
            try:
                str_t = row[0]
                str_t = str_t.strip()
                str_t = "s_" + str_t
                rs_redis.set(str_t,str(i)) # 存入停用词
                print (i,str_t) # 调试用
            except:
                pass
            
            i += 1
            
            
        time_last = str(time_cost(time_start))
        print ("共导入：" + str(i-1) + " 条停用词 一共有 " + str(numb_all) + "条")
        print ("耗时：",time_last," 秒")
        
        
    # 导入命名实体词
    if (action == "kw_ne"):
    
        time_start = datetime.datetime.now()
        
        numb_all = 0
        str_t = ""

        sql = "select keyword from keyword_ne"
        res, rows = rs_way_mysql.read_sql(sql)
        if (res < 1):
            return "数据库为空或数据库读取错误"
        else:
            numb_all = res

        i = 1
        for row in rows:
        
            try:
                str_t = row[0]
                str_t = str_t.strip()
                str_t = "n_" + str_t
                rs_redis.set(str_t,str(i)) # 命名实体
                print (i,str_t) # 调试用
            except:
                pass
            
            i += 1
            
    
            
        time_last = str(time_cost(time_start))
        print ("共导入：" + str(i-1) + " 条命名实体 一共有 " + str(numb_all) + "条")
        print ("耗时：",time_last," 秒")
            
    # rs_redis.set('你你','678') #调试用
    
    # 导入API验证码字典
    if (action == "api_key"):
        if ("numb_key" in args_list):
            numb_key = int(args_list["numb_key"])
        else:
            numb_key = 128
            
        txt = str(numb_key)
    
    #rs_way_mysql.close_cur() #关闭数据游标
    rs_way_mysql.close() #关闭数据连接
    
    return txt


def main():

    #1 过程一

    if args_list:
        print (run_it())

    #2 过程二

    #3 过程三
    
if '__main__' == __name__:
    main()