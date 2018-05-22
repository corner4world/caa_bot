#!/usr/bin/env python3
#coding:utf8

import time # 时间模块

#-----特定功能模块引用区-----
import cgi # CGI模式 取得shell参数用

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
import inc_result_cache # 缓存数据预处理

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# shell模式下参数处理
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


def run_it(csv_file = r'./data/test.csv'):

    # 建议词处理
    if (action == "sug"):
        print (inc_result_cache.sug_do(csv_file))
    
#---------- 主过程<<开始>> -----------#

def main():

    #1 过程一
    #print (args_list) #调试用
    if args_list:
        print (run_it(csv_file = r'./data/suggest.csv'))

    #2 过程二

    #3 过程三
    
if '__main__' == __name__:
    main()