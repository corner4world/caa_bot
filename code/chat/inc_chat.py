#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"集体",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----内部参数引用
import config # 内部主参数

#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块
import random # 随进函数
import math #数学计算库
from collections import Counter # 统计函数
import json
#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----

import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
from diy.inc_hash import hash_make #MD5函数
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
import diy.inc_dic as inc_dic # 内置数据字典模块
import diy.inc_chat_engine as inc_chat_engine # 内置

sys.path.append("..")
import order.inc_order as inc_order # 指令控件库


#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理


# ---全局变量处理
dic_hello = inc_dic.dic_hello # 问候语字典

# ---本模块内部类或函数定义区

        
# 外调模块引擎驱动函数
def run_it(q_p="",dic_user={},code_out=1):

    time_zero = time.strftime('%Y-%m-%d %H:%M:%S')
    time_start = datetime.datetime.now()
    code_p = "" # 返回的反馈编码
    sql = "" #  sql查询主语句
    sql_where = "" # sql的条件查询部分
    
    # 重要参数
    dialog_is = 1 # 对话状态参数 0 结束 1 进行中 2 僵持
    initiative = 0 # 话语主动权 0 用户 1 机器人 2 无归属
    query_is = "" # 反问内容
    order_is = "" # 指令内容
    txt_json = "" # json格式的文本
    rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
    rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
    dic_h = {} # 对话历史记录字典
    name_csv = "" # 对话csv文件名
    user_id = "" # 登录用户的ID
    log_dialog = "" # 对话记录
    answer_p = [0,"","",0,"",0,0] # 对话日志内容队列
    log_visit = [] # 访问日志
    
    # 对话参数主字典初始化 最重要
    dic_m = {
    "question":q_p,
    "order":{"active":0},
    "pretreatment":{},
    "segment":[],
    "mk":{},
    "list_search":[],
    "intent":{"gossip":-1,"emotion":-1,"yesno":-1,"order":-1,"what":-1,"what_is":-1,"why":-1,"how":-1,"do":-1,"field":{}}
    }
    
    dialog = inc_chat_engine.Dialog() # 人性化对话对象实例化
    order_main = inc_order.Order_main() # 主指令对象实例化
    
    # 导入对话记录
    if (config.dic_config["dialog_history_if"] == "1"):
        dic_h,name_csv,user_id = dialog.get_chatlist(path_p=config.dic_config["path_chat_old"],numb_chatlist_p=int(config.dic_config["numb_chatlist"]),dic_user=dic_user)
        answer_p[0] = user_id # 获得用户ID 没有注册或登录id为0
        answer_p[1] = q_p
        answer_p[4] = time_zero
        
    #---- 问答解析开始 ----
    
    #1-数据预处理
    dic_m["pretreatment"] = dialog.pretreatment(q_p=q_p)

    if (dic_m["pretreatment"]):
        for i in range(len(dic_m["pretreatment"])):
            dic_m["segment"].append(dic_m["pretreatment"][str(i+1)]["name"])
    else:
        # 问题没内容做单次对话退出
        pass
    
    #2-意图识别
    
    #2-1 闲聊识别
    dic_m["intent"]["gossip"] = dialog.intent_is(dic_p=dic_m,action_p="gossip")
        #print (txt_json,type(txt_json),dic_m["intent"]["gossip"],type(dic_m["intent"]["gossip"])) # 调试用
    
    #3-对话状态判别
    
    #4-话语权识别
    
    #5-指令判别
    
    #6-执行权限判别
    
    #7-指令执行
   
    
    #8 问答答案生成与渲染
    
    #8-1 答案生成
    
    #8-1-1 闲聊的答案生成
    if (dic_m["intent"]["gossip"] == 1 and dic_m["order"]["active"] == 0):
    
        # 闲聊的补丁校验 敏感词一票否定法
        
        if (dialog.gossip_bug_ner(q_p=q_p,dic_ner_1=inc_dic.dic_ner_1,dic_ner_2=inc_dic.dic_ner_2) is True):
            pass
        else:
            print ("闲聊语句含有敏感词")
            dic_m["intent"]["gossip"] = 0

        # 基本礼貌语优先处理
        if (dic_m["intent"]["gossip"] == 1):
            str_t = dialog.hello_is(dic_p=dic_m["segment"],dic_hello=inc_dic.dic_hello)
            if (str_t != ""):
                code_p = str_t
        
        # 非索引直接匹配
        if (code_p == "" and dic_m["intent"]["gossip"] == 1 and config.dic_config["qa_gossip_index_is"] == "0"):
            code_p = dialog.answer_noindex(dic_m=dic_m,conn_p=rs_basedata_mysql)
            
    #8-1-2 实质性问题的答案生成
    if (dic_m["intent"]["gossip"] == 0 and dic_m["order"]["active"] == 0):
        
        # 非索引直接匹配
        if (code_p == "" and dic_m["intent"]["gossip"] == 0 and config.dic_config["qa_index_similar_is"] == "0"):
            code_p = dialog.answer_noindex(dic_m=dic_m,conn_p=rs_basedata_mysql)
            
        # 索引+相似度 加速匹配
        if (code_p == "" and dic_m["intent"]["gossip"] == 0 and config.dic_config["qa_index_similar_is"] == "1"):
            code_p = dialog.answer_index_similar(dic_m=dic_m,conn_1=rs_basedata_mysql,conn_2=rs_index_mysql,code_out=code_out)
    
    dialog.show_dic_test(dic_t=dic_m) # 调试用 重要
    answer_p[5] = round(time_cost(time_start),2) # 存入分析时间
    
    # 8-1-3 如果匹配不成 进行话语权切换 进行提示性反问
    if (code_p == ""):
        code_p = dialog.answer_nothing_bug(dic_p=inc_dic.dic_prattle_why)

    
    if (code_p != ""):
        answer_p[2] = code_p # 存入答案
        answer_p[3] = initiative # 存入话语权
    
    #8-2 答案的渲染 code_out 0 不渲染 1 web 2 api
    # 回答机器人判别
    if (dic_m["intent"]["gossip"] == 1):
        rot_is = 6
    if (dic_m["intent"]["gossip"] == 0):
        rot_is = 0
    if (code_p != "" and dialog_is == 1):
        # 按web编码进行渲染输出
        if (code_out == 1):
            # 渲染历史记录
            if (config.dic_config["dialog_history_if"] == "1"):
                if (dic_h):
                    code_p = dialog.web_show(q_p=q_p,code_p=code_p,dic_h=dic_h,time_zero=time_zero,time_cost=answer_p[5],dialog_is=dialog_is,rot_is=rot_is)
    
    
    #9-收尾处理
    
    
    #9-1 写入历史对话记录
    
    dialog.save_chat_list(
    path_chat_list_p=config.dic_config["path_chat_old"] + name_csv + ".csv",
    code_p="utf-8",
    content_p=str(answer_p).replace("[","").replace("]","") + "\n"
    )
    
    #9-2 写入对话访问日志
    
    log_visit = answer_p # 格式化访问队列
        
    #9-2-1 获得IP
    log_visit[1] = dic_user["remote_ip"]
    
    #9-2-2 获得User-Agent
    log_visit[2] = dic_user["headers"]["User-Agent"]
    
    #9-2-3 存入访问日志
    dialog.save_visit_log(
    path_visit_log_p="./data/log/visit_log.csv",
    code_p="utf-8",
    content_p=str(log_visit).replace("[","").replace("]","") + "\n"
    )
    
    #9-3 关闭数据库连接
    rs_basedata_mysql.close() #关闭数据连接
    rs_index_mysql.close() #关闭数据连接
    
    return code_p
    
#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    #1 过程一
    print("") # 调试用
    #2 过程二
    #3 过程三
    
if __name__ == '__main__':
    main()
    
#---------- 主过程<<结束>> -----------#