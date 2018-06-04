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

# ---系统参变量处理
import config #导入系统配置参数模块

# ---全局变量处理


#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块
import csv # CSV模块
import json # json处理模块

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----

import inc_vec # 词向量处理
sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
from diy.inc_hash import hash_make # 基本自定义hash模块
from diy.inc_result import * #自定义特定功能模块
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
import cache.inc_redis as inc_redis # redis 缓存
import diy.inc_nlp as inc_nlp # 自然语言处理模块
import diy.inc_ml as inc_ml # 机器学习模块

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

        
#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

# 数据分析引擎主类
class Dae_main(object):
    
    # 默认的分词方法
    def segment_default(self,segment_p):
        
        dic_t = {}
        list_s = []
        list_t = []
        
        list_s = segment_p.seg_main() #分词处理
        
        # json化处理
        i = 1
        for x in list_s:
            if (x != ""):
                dic_t[i] ={"name":x}
                i += 1
                
        return dic_t
        
    # 带词性标注的分词方法
    def segment_pseg(self,segment_p):
    
        dic_t = {}
        list_s = []
        list_t = []
        list_s = segment_p.seg_pseg() #分词处理
        
        i = 1
        for x in list_s:
        
            if (x):
            
                list_t = []
                try:
                    list_t = eval(x)
                except:
                    pass
                if (list_t and len(list_t) == 2):
                    dic_t[i]={"name":list_t[0],"pseg":list_t[1]}

                i += 1
        
        return dic_t

# 主运行
def run_it(**args):
    
    #time_start_p = datetime.datetime.now() #内部执行初始时间
    
    #获得可变参数
    if "q_p" in args:
        q_p = args["q_p"]
    else:
        q_p = ""
    # get方式的关键词处理
    kw = q_p
    kw = kw.replace("&","")
    kw = kw.replace("?","")
        
    if "action_p" in args:
        action_p = args["action_p"]
    else:
        action_p = "" 
    
    if "threshold" in args:
        threshold = args["threshold"]
    else:
        threshold = 0
        
    if "numb_sm" in args:
        numb_sm = args["numb_sm"]
    else:
        numb_sm = 6
        
    if "answer_p" in args:
        answer_p = args["answer_p"]
    else:
        answer_p = ""
        
    if "page_p" in args:
        page_p = args["page_p"]
    else:
        page_p = 1
        
    if "id_p" in args:
        id_p = args["id_p"]
    else:
        id_p = 0
        
    txt = ''
    result = ""
    path_dae = config.dic_config["path_dae"]
    
    # 词向量相关参数
    numb_q_all = int(config.dic_config["numb_q_all"])
    
    # 定义标点符号字典
    dic_punctuation={
    "!":1,
    ":":2,
    ";":3,
    "'":4,
    "?":5,
    "！":6,
    "：":7,
    "；":8,
    "“":9,
    "”":10,
    "、":11,
    "，":12,
    "。":13,
    "？":14,
    }
    
    #--------------内部函数定语区 快速调用 复用-------------
    # json文本转字典变量
    def json_dic_get(txt_dic=""):
        
        dic_p={}
        
        try:
            dic_p = eval(txt_dic)
        except:
            pass
            
        return dic_p
        
    # tf_idf计算函数
    def tf_idf_get(q_p="",dic_t={}):
    
        import diy.inc_dic as inc_dic # 引用字典模块
        import math # 引用数学模块
        str_t = "" # 临时字符串
        numb_tf = 0 # 提交语料的词向量元素数
        dic_nosame = {} # 词向量元素去重表 用于统计词频
        value_tf_idf = 0 # 词向量元素的td_idf值
        
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        
        if "name_vec" in args:
            name_vec = args["name_vec"]
        else:
            name_vec="question"
        
        if (name_vec == "question"):
        
            sql = "select count(*) from qa"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                numb_idf_all = rows[0][0]
            else:
                numb_idf_all = 0.00000001
        
        if (dic_t):
        
            dic_oneword = inc_dic.dic_make_one_cache(path_p=config.dic_config["path_dic"] + "dic_oneword.txt")
            dic_unitword = inc_dic.dic_make_one_cache(path_p=config.dic_config["path_dic"] + "dic_unitword.txt")
            #print (dic_oneword,dic_unitword) # 调试用
            
            numb_tf = len(dic_t)
            
            for x in dic_t:
            
                str_t = dic_t[x]["name"].strip()
                
                if (str_t in dic_nosame):
                    dic_nosame[str_t] = dic_nosame[str_t] + 1
                else:
                    dic_nosame[str_t] = 1
                    
                dic_t[x]["tf_idf"] = -999999 # tf_id值初始化
        
            for x in dic_t:
            
                str_t = dic_t[x]["name"].strip()
                
                if (len(str_t) == 1):
                # 单个汉字的特殊规则
                    if (str_t in dic_oneword or str_t in dic_unitword):
                        pass
                    else:
                        continue
                    
                sql = "select idf from index_" + name_vec + " where keyword='" + str_t + "'"
                res_t, rows_t = rs_basedata_mysql.read_sql(sql)
                
                if (res_t > 0):
                    
                    if (rows_t[0][0] > 0 and str_t in dic_nosame):
                    
                        value_tf_idf = dic_nosame[str_t]/numb_tf*math.log(numb_idf_all/rows_t[0][0])
                        dic_t[x]["tf_idf"] = value_tf_idf
                
        rs_basedata_mysql.close() #关闭数据连接
        
        return dic_t
        
    # 实体识别函数
    def get_ne(q_p="",dic_t={}):
        
        if (dic_t):
        
            rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
            
            for x in dic_t:
            
                dic_t[x]["ne"] = 0 # 命名实体标签赋初值
                
                if (dic_t[x]["pseg"] == "n"):
                    str_t = dic_t[x]["name"].strip()
                    sql = "select keyword from keyword_ne where keyword='" + str_t + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                
                    if (res_t > 0):
                        dic_t[x]["ne"] = 1
                    else:
                        sql = "select keyword from keyword_ne where keyword like '%" + str_t + "' or keyword like  '" + str_t + "%'"
                        res_t, rows_t = rs_way_mysql.read_sql(sql)
                        
                        if (res_t > 0):
                            dic_t[x]["ne"] = 1

            rs_way_mysql.close() #关闭数据连接
            
        return dic_t
        
    # 主题词识别
    def get_mk(q_p="",dic_t={}):
    
        list_order = []
        dic_order = {}
        dic_t = tf_idf_get(q_p=q_p,dic_t=dic_t) # tf_idf标注字典
        dic_t = get_ne(q_p=q_p,dic_t=dic_t) # 命名实体标注字典
        
        if (dic_t):
                
            # 生成排序字典
            for x in dic_t:
                dic_order[dic_t[x]["name"]] = [dic_t[x]["ne"],dic_t[x]["tf_idf"],dic_t[x]["pseg"]]
            list_order = sorted(dic_order.items(), key=lambda d:d[1], reverse = True) # 参数由大到小排序
            if (list_order):
                dic_t = {}
                i = 1
                for x in list_order:
                    dic_t[i]={"name":x[0],"ne":x[1][0],"tf_idf":x[1][1],"pseg":x[1][2]}
                    i += 1
            
        return dic_t
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        if "table_td" in args:
            table_td = args["table_td"]
        else:
            table_td="index_main"

        list_s = []
        dic_t = {}
        td = 0
        dic_p = {}
        list_last = []
        mk_is = 0 # 主题词判别变量
        list_x = []
        
        dae_base = inc_ml.Dae_base()
        segment = inc_nlp.Segment(txt_p=q_p,threshold_p=threshold,way_p="precise") #分词模块实例化
        list_s = segment.seg_pseg() #含词性标注分词处理
        newword_power_is = int(config.dic_config["newword_power_is"]) #新词识别的词频阈值
        numn_word_self = len(list_s)
        #return (inc_redis.kw_stop("高兴")) # 调试用 测试停用词查找缓存是否生效
        
        # 判别主题词主循环开始
        for x in list_s:
        
            list_x = []
            try:
                list_x = eval(x)
            except:
                pass
        
            mk_if = 0
            
            #print (x,list_x,type(x)) # 调试用
            
            if (list_x):
            
                print ("词名：",list_x[0],"词性：",list_x[1]) # 调试用
                #print ("停用词属性：",inc_redis.kw_stop(list_x[0])) # 调试用
                
                # 如果是名词类型
                if ("n" in list_x[1]):
                    if (inc_redis.kw_stop(list_x[0]) == ""):
                        mk_if = 1
                
                # 如果是数词类型
                if (list_x[1] == "m"):
                    if (inc_redis.kw_stop(list_x[0]) == ""):
                        mk_if = 1
                
                # 如果是动词类型
                if (list_x[1] == "v"):
                    mk_if = 1
                
                # 如果是未知待识别类型
                if (list_x[1] == "x"):
                    
                    # 如果词性未知 先校验是否是成词
                    sql = " select idf from " + table_td + " where keyword='" + list_x[0] + "'"
                    #print (sql) # 调试用
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if (res > 0):
                        mk_if = 1
                        
                    if (len(list_x[0]) <= 16):
                    
                        if (list_x[0] in dic_punctuation):
                            
                            pass
                            
                        else:
                        
                            id = 0
                            sql = "select id,power from word_x where word ='" + list_x[0] + "'"
                            #print (sql) # 调试用
                            res, rows = rs_way_mysql.read_sql(sql)
                            if (res > 0):
                        
                                if (rows[0][1] >= newword_power_is):
                                    mk_if = 1 # 确认可以作为主题词
                                    
                                id = rows[0][0]
                                sql = "update word_x set power = power + 1 where id=" + str(id)
                                #print (sql) # 调试用
                                update_if = rs_way_mysql.write_sql(sql)
                                
                                
                            
                            else:
                        
                                sql = "insert into word_x set word='" +  list_x[0] + "',power=1 "
                                #print (sql) # 调试用
                                insert_if = rs_way_mysql.write_sql(sql)
                
            if (mk_if == 1):
            
                if list_x[0] in dic_t:
                
                    dic_t[list_x[0]][0] = dic_t[list_x[0]][1] + 1
                
                else:
                
                    dic_t[list_x[0]] = [-999999.0,1,0,list_x[1]]

                    sql = " select idf from " + table_td + " where keyword='" + list_x[0] + "'"
                    #print (sql) # 调试用
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if (res > 0):
                        dic_t[list_x[0]][2] = rows[0][0]
                   
        for x in dic_t:
            if (dic_t[x][2] > 0):
                dic_t[x][0] = round(dae_base.tf_idf(nump_tf_p=dic_t[x][1],numb_div_p=numn_word_self,numb_all_p=numb_q_all,numb_idf_p=dic_t[x][2]),10)
                   
        if (dic_t):
            txt = str(dic_t)

        rs_way_mysql.close() #关闭数据连接
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
    
    # 获得原始知识图谱
    def get_kg():
    
        txt = ""
        txt_dic = ""
        w_t = ""
        s_t = ""
        list_t = []
        list_ne = [] #命名实体队列
        sql_add = ""
        ill_is = ""
        ill_where = ""
        ill_what = ""
        dic_ne = {}
        dic_mk = {}
        str_t = q_p
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        if (str_t):
        
            sql_add = ""
            ill_is = ""
            ill_where = ""
            ill_what = ""
            
            # 疾病实体
            dic_ne = json_dic_get(get_ne())

            if (dic_ne):
                
                #排序
                list_ne = sorted(dic_ne.items(), key=lambda d:d[1], reverse = True)#关键词排名
                    
                # 查询疾病实体
                for x in list_ne:
                    sql = "select keyword from keyword_ill_is where keyword='" + x[0] + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                    if (res_t > 0):
                        ill_is = x[0]
                        ill_is = ill_is.strip()
                        break
            
            # 获得主题词
            
            dic_mk = json_dic_get(get_mk())
            
            if (dic_mk):
                
                #排序
                list_mk = sorted(dic_mk.items(), key=lambda d:d[1], reverse = True)#关键词排名
                
                if (ill_is == ""):
                    # 查询疾病实体
                    for x in list_ne:
                        sql = "select keyword from keyword_ill_is where keyword='" + x[0] + "'"
                        res_t, rows_t = rs_way_mysql.read_sql(sql)
                        if (res_t > 0):
                            ill_is = x[0]
                            ill_is = ill_is.strip()
                            break
                            
                # 查询疾病部位
                for x in list_ne:
                    sql = "select keyword from keyword_ill_where where keyword='" + x[0] + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                    if (res_t > 0):
                        ill_where = x[0]
                        ill_where = ill_where.strip()
                        break
                        
                # 查询疾病症状
                for x in list_ne:
                    sql = "select keyword from keyword_ill_what where keyword='" + x[0] + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                    if (res_t > 0):
                        ill_what = x[0]
                        ill_what = ill_what.strip()
                        if (sql_add != ""):
                            sql_add += ","
                        sql_add += "ill_what='" + ill_what + "'"
                        break
        
        # 构造诊断知识图谱
        if (ill_is != "" and ill_what != ""):
            txt = ill_is + "|的病症是|" + ill_what + ","
        if (ill_is != "" and ill_where != ""):
            txt = ill_is + "|的部位是|" + ill_where + ","
        
        # 构造医疗子知识图谱
        # 常见副词
        list_c = ["可能","会","需","要","经","能"]
        list_s = [] #自然分词序列
        dic_v = {}
        words = pseg.cut(str_t)
        
        for w in words:
            
            w_t = ""
            list_s.append(w.word)
            #print (w.word,w.flag) # 调试用
            if (w.flag == "v"):
                w_t = w.word
                w_t = w_t.strip()
                #print (w_t) # 调试用
                # 动词被常见副词修饰
                if (w_t[0:1] in list_c):
                
                    sql = "select title from relation where title like '%" + w_t[1:] + "%' "
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    
                    if (res > 0):
                        if (w_t in dic_v):
                            pass
                        else:
                            dic_v[w_t] = rows[0][0]
                            
                else:
                
                    sql = "select title from relation where title like '%" + w_t + "%' "
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if (res > 0):
                        if (w_t in dic_v):
                            pass
                        else:
                            dic_v[w_t] = rows[0][0]
                            
                print (sql) # 调试用
        #print ("医疗实体",dic_ne) # 调试用
        #print ("主题词",dic_mk) # 调试用
        #print ("分词队列：",list_s) # 调试用
        #print ("动词字典：",dic_v) # 调试用
        # 动词在关系集合命中 则顺序检索
        if (dic_v):
            for y in dic_v:
            
                p = list_s.index(y)
                #print (y,p) # 调试用

                if (p > -1):
                    s_t = ""
                    # 向前搜索实体词
                    j = p - 1
                    while ( j > -1):
                        
                        if (list_s[j] in dic_ne):
                            s_t = list_s[j]
                            break
                        j -= 1
                        
                    if (s_t != ""):
                        s_t += "|" + y
                        
                    # 向后搜索实体词
                    j = p + 1
                    while (j < len(list_s)):
                        if (list_s[j] in dic_ne):
                            if (s_t != ""):
                                s_t += "|" + list_s[j] 
                            else:
                                s_t += y + "|" + list_s[j] 
                            break
                        j += 1
                        
                if (s_t != ""):
                    txt += s_t + ","
                    continue
                    
                # 没命中则搜索主题词字典
                
                if (p > -1):
                    s_t = ""
                    # 向前搜索实体词
                    j = p - 1
                    while ( j > -1):
                        
                        if (list_s[j] in dic_mk):
                            s_t = list_s[j]
                            break
                        j -= 1
                        
                    if (s_t != ""):
                        s_t += "|" + y
                        
                    # 向后搜索实体词
                    j = p + 1
                    while (j < len(list_s)):
                        if (list_s[j] in dic_mk):
                            if (s_t != ""):
                                s_t += "|" + list_s[j] 
                            else:
                                s_t += y + "|" + list_s[j] 
                            break
                        j += 1
                        
                if (s_t != ""):
                    txt += s_t + ","
                    
                    
        if (txt != ""):
            txt = txt[0:-1]
        txt = "{\"kg\":\"" + txt + "\"}"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        rs_way_mysql.close_cur() #关闭数据游标
        rs_way_mysql.close() #关闭数据连接
        
        return txt
    
    # 文本着重标记
    def remark_txt(txt_p,list_remark_p=[],color_p="#D50000"):
        for x in list_remark_p:
            txt_p = txt_p.replace(x,"<font color=\"" + color_p + "\">" + x + "</font>")
        return txt_p
    
    # 词向量元素标注字典分词字段获得
    def dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="default"):
        
        dic_t = {}
        #分词模块实例化 
        segment = inc_nlp.Segment(txt_p=q_p,threshold_p=threshold,way_p="precise")
        dae_main = Dae_main() # 主数据引擎实例化
        if (action_p == "default"):
            dic_t = dae_main.segment_default(segment_p=segment)
        if (action_p == "pseg"):
            dic_t = dae_main.segment_pseg(segment_p=segment)
            
        return dic_t
        
    # ------------- 内嵌函数定义结束 ---------------

    
    # 标准分词处理
    if (action_p == "seg"):
        
        dic_t = dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="default")
        
        return dic_t
        
    # 标准分词词性标注处理
    if (action_p == "pseg"):
        
        dic_t = dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="pseg")
        
        return dic_t
    
    # Td_idf的处理
    if (action_p == "tf_idf"):
    
        dic_t = dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="pseg")
        dic_t = tf_idf_get(q_p=q_p,dic_t=dic_t)
        
        return dic_t
        
    # 命名实体的识别
    if (action_p == "ne"):
    
        dic_t = dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="pseg")
        dic_t = get_ne(q_p=q_p,dic_t=dic_t)
        
        return dic_t

    # 主题词的识别
    if (action_p == "mk"):
        
        dic_t = dic_vec_segment(q_p=q_p,threshold_p=threshold,way_p="precise",action_p="pseg")
        dic_t = get_mk(q_p=q_p,dic_t=dic_t)
        
        return dic_t
        
    # 相似词识别
    if (action_p == "sm"):
        
        dic_t = {}
        
        #待识别词校验
        if (len(q_p) < 1):
            return "待分析词不能为空！"
        if (len(q_p) > numb_sm):
            return "待分析词长度不能超过" + str(numb_sm) + "！"
            
        path_model = "./data/w2v/w2v.model"
        
        result = inc_vec.run_it(str_t=q_p,action_p="similar",path_model_p=path_model) # 获得相似词队列
        
        if (result):
            
            i = 1
            for x in result:
                dic_t[i] = {"name":x[0],"sm":x[1]}
                i += 1
                
        return dic_t
    
    # SVM意图识别
    if (action_p == "cf_svm_whathow"):
        import inc_cf_svm_lr_whathow as sl # svm_lr方法库引用
        rate_t = int(sl.run_it(q_p))
        dic_t = {"classify":rate_t}
        return dic_t
        
    # Cnn+Bilstm_领域知识_意图识别
    if (action_p == "cf_cnn_bilstm"):
        print("740",q_p)
        import inc_cnn_bilstm as cb # cnn_bilstm方法库引用
        rate_t = int(cb.run_it(str_t=q_p))
        dic_t = {"classify":rate_t}
        return dic_t
        
    # 长时语义匹配
    if (action_p == "match_longtime"):
        import inc_qa_longtime as ql # svm_lr方法库引用
        txt = ql.run_it(q_p)
        return txt
    
    def classify_lr(q_p="",name_model = "x",which=2,dim_f=8):
        
        # 主类实例化
        feature_base = inc_ml.Feature_base() # 特征基础类实例化
        feature_dae = inc_ml.Feature_dae() # 特征分析引擎实例化
        # 主要变量
       
        txt = ""
        row = () # 待处理元组
        rows_max = () # 最大值元组
        rows_min = () # 最小值元组
        rows_avg = () # 均值元组
        rows_std = () # 标准差元组
        dic_f = {} # 特征字典
        dic_d = {} # 归一化后的特征字典
        list_t = [] # 临时列表
        list_w = [] # 临时列表
        str_t = "" # 临时字符串
        str_t2 = "" # 临时字符串
        dic_t = {} # 训练字典
        list_test = [] # 测试队列
        rate_max = 0.0 # 最高查准率
        rate_t = -1 # 意图分类值
        step_last = 1 # 最佳迭代次数

        path_dae = config.dic_config["path_lr"] # 中间数据文件夹
        print ("中间文件路径",path_dae) # 测试用
        
        # 导入极值元组集
        
        if (which == 1):
            with open(config.dic_config["path_f"] + "feature_max_" + name_model + ".txt", 'r') as f:
                str_t = f.read()
                rows_max = eval(str_t)
            with open(config.dic_config["path_f"] + "feature_min_" + name_model + ".txt", 'r') as f:
                str_t = f.read()
                rows_min = eval(str_t)
        
        if (which == 2):
            with open(config.dic_config["path_f"] + "feature_avg_" + name_model + ".txt", 'r') as f:
                str_t = f.read()
                rows_avg = eval(str_t)
            with open(config.dic_config["path_f"] + "feature_std_" + name_model + ".txt", 'r') as f:
                str_t = f.read()
                rows_std = eval(str_t)
        dic_f = feature_base.value_get(str_t=q_p,dim_p=dim_f)
        #try:
            #dic_f = feature_base.value_get(str_t=q_p,dim_p=dim_f) # 注：此函数dim_p 为特征个数
        #except:
            #pass
        
        #print ("特征字典：",dic_f) # 测试用
        
        if (len(dic_f) == dim_f):
            j = 0
            for j in range(dim_f):
                str_t2 = "f" + str(j+1) 
                if (str_t2 in dic_f):
                    list_t.append(dic_f[str_t2])
                    
        row = tuple(list_t)
        print ("数据元组",row) # 测试用
        
        if which == 1:
            try:
                dic_d = feature_base.dim_get_max_min(row_p=row,which_p=which,rows_max=rows_max,rows_min=rows_min,numb_dim=dim_f)
            except:
                pass
        
        if which == 2:
            try:
                dic_d = feature_base.dim_get_stand(row_p=row,which_p=which,rows_avg=rows_avg,rows_std=rows_std,numb_dim=dim_f)
            except:
                pass
                
        #print ("归一化字典",dic_d) # 调试用
        
        # 生成归一化序列
        if (len(dic_d) == dim_f):
            j = 0
            for j in range(dim_f):
                str_t2 = "f" + str(j+1) 
                if (str_t2 in dic_d):
                    list_w.append(dic_d[str_t2])
            
        #return q_p + str(dic_f) + str(row) + str(dic_d) + str(list_w) # 调试用
        print ("归一化序列：",list_w)
        rate_t = feature_dae.what_class_lr(list_last=list_w,path_dae_p=path_dae,dim_p=2,test_p=0,name_model_p=name_model)
        dic_t = {"classify":rate_t}
        
        return dic_t
        
    # LR是否型意图识别
    if (action_p == "cf_lr_yesno"):
        dic_t = {}
        dic_t = classify_lr(q_p=q_p,name_model = "yesno",which=2,dim_f=8)
        return dic_t
        
    # LR闲聊型意图识别
    if (action_p == "cf_lr_gossip"):
        dic_t = {}
        dic_t = classify_lr(q_p=q_p,name_model = "gossip",which=2,dim_f=8)
        return dic_t
        
    
    # 知识库搜索
    if (action_p == "search"):
        
        import inc_dic # 内置数据字典模块
        import math
        # ---全局变量处理
        time_start_p = datetime.datetime.now() #内部执行初始时间
        path_main = config.dic_config["path_main"] #主绝对路径
        log_if = int(config.dic_config["log_if"]) #主绝对路径
        numb_page = int(config.dic_config["max_per_page"]) # 分页基数
        numb_prattle_why = len(inc_dic.dic_prattle_why)
        numb_prattle_last = len(inc_dic.dic_prattle_last)
        dic_hello = inc_dic.dic_hello
        dic_ner_1 = inc_dic.dic_ner_1
        dic_ner_2 = inc_dic.dic_ner_2
        dic_guide = inc_dic.dic_guide
        dic_prattle_last = inc_dic.dic_prattle_last
        dic_prattle_why = inc_dic.dic_prattle_why
        result_base = Result_base() #特殊功能类实例化
        test_if_p = int(config.dic_config["test_if"]) # 调试模式
        dic_cf_root = {1:"cf_cnn_bilstm_field",2:"cf_svm_whathow",3:"cf_lr_yesno"} #意图优先字典
        dic_cf_child = {0:"cf_lr_yesno",1:"cf_lr_yesno",2:"cf_cnn_bilstm_field",3:"cf_lr_yesno",4:"cf_cnn_bilstm_field",5:"cf_lr_yesno",6:"cf_cnn_bilstm_field"}
        txt_end_p = ""
        txt = "" # 返回的结果文本
        txt_t = ""

        time_start_p = datetime.datetime.now() #内部执行初始时间
        q_p = q_p.strip()
        str_mk = "" # 关键词串
        str_ne = "" # 命名实体临时串
        url_p = "" # API服务请求地址
        arr_t = [] # 临时数组
        dic_t = {} # 临时字典
        dic_m = {} # 关键词字典
        dic_n = {} # 命名实体字典
        dic_r = {} # 结果集字典
        dic_p = {} # 最后的排列字典
        list_mk = [] # 关键词队列
        list_ne = [] # 命名实体队列
        list_find = [] # 待查询队列
        list_find_last = [] #最后的匹配命中队列
        list_t = [] # 临时队列
        str_t = "" # 临时字符串
        str_old = "" # 字符串备份 主要用于比对
        sql = "" # 主查询语句
        sql_head = "" # 主查询头
        sql_data = "" # 主查询表端内容
        sql_where = "" # 主查询条件
        sql_order = "" # 主查询排序
        sql_limit = "" # 主查询限定数量
        x_x = "" # 模糊匹配关键词串
        rank = 0.0 # 排名值
        Sq = 0 # 候选集的标题相似度
        Sa = 0 # 候选集的文本相似度
        vec_t = [] # 临时词向量
        dic_input = {} # 提问的关键词字典
        list_cos_0 = "" # 余弦向量初始值队列串
        list_cos = [] # 余弦词向量队列
        dic_c_t = {} # 余弦值临时字典
        list_a = [] # 余弦a边的向量
        list_b = [] # 余弦b边的向量
        res_p = 0 # 可查询记录数
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        # 2-1 关键词处理
        
        dic_t = json_dic_get(get_mk(q_p))

        if (dic_t):
                
            dic_input = dic_t # 提问的关键词字典
            for y in dic_t:
                dic_m[y] = dic_t[y][0]
            list_mk = sorted(dic_m.items(), key=lambda d:d[1], reverse = True)#关键词排名
            
        #2-2 命名实体处理
        if (dic_m):
            
            list_t = []
            # 对带分段型标点符号的长文本进行特殊处理
            str_t = result_base.np_some(str_p=q_p) # 自然分句
            arr_t = str_t.split("@x@")
            
            
            # 按自然分句进行命名实体识别
            
            # 只有一个自然句
            if (len(arr_t) == 1):
            
                dic_t = json_dic_get(get_ne())
                
                if (dic_t):
                    for y in dic_t:
                        dic_n[y] = float(dic_t[y])
                    list_ne = sorted(dic_n.items(), key=lambda d:d[1], reverse = True)#命名实体排名
            
            # 多个自然句
            else:
            
                for x in arr_t:
                
                    dic_t = {}
                    dic_n = {}
                    str_ne = ""
                    q_p = x
                    dic_t = json_dic_get(get_ne())
                    
                    if (dic_t):
                        for y in dic_t:
                            dic_n[y] = float(dic_t[y])
                        list_t = sorted(dic_n.items(), key=lambda d:d[1], reverse = True)#命名实体排名
                        k = 0
                        for y in list_t:
                        
                            if (k == 1):
                                break
                            
                            if (list_ne):
                                
                                find_if = 0
                                for z in list_ne:
                                    if (z[0] == y[0]):
                                        if (z[1] < y[1]):
                                            list_ne.remove(z)
                                            list_ne.append(y) #出现重复值,则保留最大的评分值
                                        find_if = 1
                                        k += 1
                                        break
                                        
                                if (find_if == 0):
                                    list_ne.append(y)
                                    k += 1
                            
                            else:
                            
                                list_ne.append(y)
                                k += 1
                
        
        # 3 构造查询队列
        
        numb_find = int(config.dic_config["numb_find"]) # 获得最大匹配关键词数
        j = 1
        for x in list_ne:
            
            if (j > numb_find):
                break
            list_find.append([x[0],"",x[1]])
                
            j += 1
        
        j = j - 1
        
        if (j < numb_find):
            
            for x in list_mk:
            
                if (j == numb_find):
                    break
                    
                if (list_find):
                
                    find_if = 0
                    for z in list_find:
                    
                        if (z[0] == x[0]):
                            if (z[2] < x[1]):
                                z[1] = x[1]
                            find_if = 1
                            j += 1
                            break
                                        
                    if (find_if == 0):
                        list_find.append([x[0],"",x[1]])
                        j += 1
                else:
                
                    list_find.append([x[0],"",x[1]])
                    j += 1
        
        #获得查询关键词hash值
        for x in list_find:
            sql = "select keyword_hash from index_question where keyword='" + x[0] + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res>0):
                x[1] = rows[0][0]
            else:
                if (len(x[0]) > 4):
                    x_x = x[0][0:4]
                sql = "select keyword_hash from index_question where keyword like '%" + x_x + "%' order by idf desc"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if (res>0):
                    x[1] = rows[0][0]
        
        if (test_if_p == 1):
            txt += " 待选匹配：" + str(list_find) + " <br>" # 调试用      
        
        if (list_find):
            
            list_find_last = list_find 
            
            #sql_limit = " limit " + config.dic_config["numb_limit"] + " " #信息检索默认是分页的 故不加限定数量
            
            j = len(list_find)
            
            while (j >= 0):
            
                i = 1
                for x in list_find:
                    
                    if (i > j):
                        #print (str(i)) 调试用
                        break

                    if (i == 1):

                        sql_head = "select "
                        sql_head +="z_question_" + x[1] + ".pid, "
                        sql_head +="z_question_" + x[1] + ".rank, "
                        sql_head +="z_question_" + x[1] + ".x0, "
                        sql_head +="z_question_" + x[1] + ".x1, "
                        sql_head +="z_question_" + x[1] + ".x2, "
                        sql_head +="z_question_" + x[1] + ".x3 "
                        sql_head += "from "
                        sql_data = " z_question_" + x[1]
                        sql_where = ""
                        sql_order = " order by z_question_" + x[1] + ".rank desc "
                        
                    else:
                        
                        sql_data += " inner join z_question_" + x[1] + " on z_question_" + str_old + ".pid = z_question_" + x[1] + ".pid "
                    
                    str_old = x[1]
                    i += 1
                
                sql = sql_head + sql_data + sql_where + sql_order + sql_limit
                #print (sql) #调试用
                #dic_config["max_per_page"]
                site_p =  numb_page * (page_p-1)
                res_p, rows_p = rs_index_mysql.read_sql_page(sql,site_p)
                #res_p, rows_p = rs_index_mysql.read_sql(sql)

                if (res_p > 0):
                    break
                else:
                    del list_find_last[len(list_find_last)-1]
                j -= 1
        
        if (test_if_p == 1):
            txt += " 最终成功匹配：" + str(list_find_last) + " <br>" # 调试用
        
        if (res_p < 1):
            return ""
            
        #2 构造候选结果集
        
        # 生成比对字典初始的部分
        for x in dic_input:
            if x in list_cos_0:
                pass
            else:
                list_cos_0 += x + "@x@"
        
        i = 1
        for row in rows_p:
        
            rank = 0 # 排名值清空
            sql = "select question,forward_question,answer,forward_answer,keyword_question,keyword_answer,rank,what,id from qa where id=" + str(row[0])
            res, rows = rs_basedata_mysql.read_sql(sql)
            
            if (res < 0):
                continue
                
            dic_r[row[0]] = [row,rows]
            
        
            #3 结果集处理,定位最佳匹配
            
            # 问题相似度计算
            list_cos = []
            dic_c_t.clear()
            list_a = []
            list_b = []
            Sq = 0
            
            # 基础比对向量重赋值
            
            list_cos = list_cos_0.split("@x@")
            
            # 生成比对字典
            try:
                dic_c_t = eval(rows[0][4])
            except:
                pass
                
            # 生成比对字典b边并a边的部分
            for x in dic_c_t:
                if x in dic_input:
                    pass
                else:
                    list_cos.append(x)
                
            for x in list_cos:
                if x in dic_input:
                    list_a.append(dic_input[x][0])
                else:
                    list_a.append(0.0)
                if x in dic_c_t:
                    list_b.append(dic_c_t[x])
                else:
                    list_b.append(0.0)
            
            #计算余弦值
            fenzi = 0.0 # 分子值
            fenmu_1 = 0.0 # 分母值
            fenmu_2 = 0.0
            k = 0
            
            for x in list_cos:
                fenzi += list_a[k]*list_b[k]
                fenmu_1 += list_a[k]*list_a[k]
                fenmu_2 += list_b[k]*list_b[k]
                k += 1
            
            fenmu_1 = math.sqrt(fenmu_1)
            fenmu_2 = math.sqrt(fenmu_2)
            if (fenmu_1 + fenmu_2 > 0):
                Sq = fenzi/(fenmu_1 + fenmu_2)
                
            #txt += "标题："  + str(rows[0][0]) + " --- 标题对标题余弦待查队列 " + str(list_cos) + " <br>a边： " + str(list_a) + " <br>b边：" + str(list_b) + " <br>标题对标题余弦值：" + str(Sq) + "<br>" # 测试用
            
            #3 结果集处理,定位最佳匹配
            # 问题相似度计算
            list_cos = []
            dic_c_t.clear()
            list_a = []
            list_b = []
            Sa = 0
            
            # 基础比对向量重赋值
            list_cos = list_cos_0.split("@x@")
            
            # 生成比对字典
            try:
                dic_c_t = eval(rows[0][5])
            except:
                pass
                
            # 生成比对字典b边并a边的部分
            for x in dic_c_t:
                if x in dic_input:
                    pass
                else:
                    list_cos.append(x)
            
            for x in list_cos:
                if x in dic_input:
                    list_a.append(dic_input[x][0])
                else:
                    list_a.append(0.0)
                if x in dic_c_t:
                    list_b.append(0.5*dic_c_t[x][0] + 0.5*dic_c_t[x][1])
                else:
                    list_b.append(0.0)
            
            #计算余弦值
            fenzi = 0.0 # 分子值
            fenmu_1 = 0.0 # 分母值
            fenmu_2 = 0.0
            k = 0
            for x in list_cos:
                fenzi += list_a[k]*list_b[k]
                fenmu_1 += list_a[k]*list_a[k]
                fenmu_2 += list_b[k]*list_b[k]
                k += 1
            fenmu_1 = math.sqrt(fenmu_1)
            fenmu_2 = math.sqrt(fenmu_2)
            if (fenmu_1 + fenmu_2 > 0):
                Sa = fenzi/(fenmu_1 + fenmu_2)
                
            #txt += " 内容："  + str(rows[0][3]) + "  --- 标题对内容余弦待查队列 " + str(list_cos) + " <br>a边： " + str(list_a) + " <br>b边：" + str(list_b) + " <br>标题对内容余弦值：" + str(Sa) + "<br>" # 测试用
            # 内容质量值
            Pr = 0.0
            
            Wq = 0.5
            Wa = 0.4
            Wp = 0.1
            rank = round(Wq*Sq + Wa*Sa + Wp*Pr,8)
            #txt += "<br>id: " + str(row[0]) + " --- 问题： " + str(rows[0][0]) + " --- 近似语义得分：" + str(rank) + "<br><br>" #调试用
            dic_p[row[0]] = rank
            
            if (i >= int(config.dic_config["max_per_page"])):
                break
            i += 1
        
        list_order = sorted(dic_p.items(), key=lambda d:d[1], reverse = True)#命名实体排名
        #txt += "<br> 推荐排名：" + str(list_order) + "<br><br>" # 调试用
        #4 最后结果校验
        #5 最后结果渲染并输出

        txt_a_t = "" # 搜索内容初始化
        txt += """
        <style>
        A {text-decoration: none; }
        A:hover {text-decoration: underline;}
        </style>
        """
        txt += "<center>"
        txt += "<div style=\"width:558px;align:left;\">"
        
        if (list_order):
            
            m = 0
            title_t = ""
            content_t = ""
            rank_t = 0
            id_t = 0
            
            # 构造着重显示关键词队列
            list_remark = []
            for y in list_find_last:
                list_remark.append(y[0])
                
            for x in list_order:
                
                try:
                    title_t = dic_r[x[0]][1][0][0]
                    content_t = dic_r[x[0]][1][0][2]
                    rank_t = dic_r[x[0]][1][0][6]
                    id_t = dic_r[x[0]][1][0][8]
                except:
                    continue
                
                # 关键词的着重处理
                title_t = remark_txt(title_t,list_remark_p=list_remark,color_p="#D50000")
                content_t = remark_txt(content_t,list_remark_p=list_remark,color_p="#D50000")
                
                # 搜索的上栏
                if (len(title_t) >64):
                    txt_a_t += "<div align=\"left\"><a href=\"./api?action=show_qa&id=" + str(id_t) + "\" target=\"_blank\"><font style=\"font-size:15px;font-family: 微软雅黑;font-weight:bold\" color=\"#0570B4\">" + title_t[0:32] + "...</font></a><div>"
                else:
                    txt_a_t += "<div align=\"left\"><a href=\"./api?action=show_qa&id=" + str(id_t) + "\" target=\"_blank\"><font style=\"font-size:15px;font-family: 微软雅黑;font-weight:bold\" color=\"#0570B4\">" + title_t + "</font></a><div>"
                
                # 搜索的中栏
                if (len(content_t) >256):
                    txt_a_t += "<div align=\"left\"><br><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">" + content_t[0:256] + "...</font></div>"
                else:
                    txt_a_t += "<div align=\"left\"><br><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">" + content_t + "</font></div>"
                    
                # 搜索的下栏
                txt_a_t += "<div align=\"left\">"
                txt_a_t += "<font style=\"font-size:12px;font-family: 微软雅黑;\" color=\"#cccccc\">热点值:</font>"
                txt_a_t += "<font style=\"font-size:12px;font-family: 微软雅黑;\" color=\"#D50000\">" + str(rank_t) + "</font>"
                if (len(content_t) >256):
                    txt_a_t += " - <a href=\"./api?action=show_kg&id=" + str(id_t) + "\" target=\"_blank\"><font style=\"font-size:12px;font-family: 微软雅黑;\" color=\"#00343f\">查看全文</font><a>"
                txt_a_t += "<br><br></div>"
                
                m += 1
                    
            if (txt_a_t != ""):
                txt += txt_a_t
                
        if (test_if_p == 1):
            txt += txt_t # 调试用
        
        txt += "</div>"
        txt += "</center>"
        
        
        txt_end_p += "<center><div style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">"
        
        #加入翻页
        if (page_p > 1):
            txt_end_p += "<a href=\"./api?action=search&page=" + str(page_p - 1) + "&q=" + kw + "\" ><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">上一页</font></a> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp"
        if (res_p > i-1):
            txt_end_p += "<a href=\"./api?action=search&page=" + str(page_p + 1) + "&q=" + kw + "\" ><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">下一页</font></a>"
            
        #耗时计算
        time_last_p = str(round(time_cost(time_start_p),2))
        txt_end_p += "<br><br><div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\"><br>本次对话,共耗时：" + time_last_p + " 秒。</div>"
            
        txt_end_p += "</div></center>"
        txt += txt_end_p
        
        return txt
    
    # 知识图谱识别
    if (action_p == "kg"):
        return get_kg()
        
    # 获得建议词
    def get_sug(q_p="",numb_limit=5,out_put="json",table_1='index_question',table_2='index_answer',table_3='qa'):
    
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        txt = ""
        str_add = ""
        
        arr_1 = q_p.split(" ")

        if (len(arr_1)>1):
        
            q_p = arr_1[-1]

            for i in range(len(arr_1)-1):
                str_add += arr_1[i] + " "
            str_add = str_add.replace(" ","")
        
        #1 问题集匹配查询
        sql = "select keyword from " + table_1 + " where keyword like '%" + q_p + "%' and keyword !='" + q_p + "' order by idf desc limit " + str(numb_limit)
        res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res > 0):
        
            k = 1
            for row in rows:
                if (row[0] != "numb_key_ldae"):
                    if (out_put == "json"):
                        txt += str(k) + ":"
                    if (out_put == "app"):
                        txt += "{\"name\":"
                    txt += "\"" + str_add + str(row[0]) + "\""
                    if (out_put == "json"):
                        txt += ","
                    if (out_put == "app"):
                        txt += "},"
                k += 1
                
            if (txt):
                txt = txt[0:-1]
        
        else:
        
            # 答案集匹配查询
            sql = "select keyword from " + table_2 + " where keyword like '%" + q_p + "%' and keyword !='" + q_p + "' order by idf desc limit " + str(numb_limit)
            res, rows = rs_basedata_mysql.read_sql(sql)
        
            if (res > 0):
            
                k = 1
                for row in rows:
                    if (row[0] != "numb_key_ldae"):
                        if (out_put == "json"):
                            txt += str(k) + ":"
                        if (out_put == "app"):
                            txt += "{\"name\":"
                        txt += "\"" + str_add + str(row[0]) + "\""
                        if (out_put == "json"):
                            txt += ","
                        if (out_put == "app"):
                            txt += "},"
                    k += 1
                    
                if (txt):
                    txt = txt[0:-1]
        
            else:
        
                txt = ""
        
        if (out_put == "json"):
            txt = "{" + txt + "}"
        
        if (out_put == "app"):
            txt = "[" + txt + "]"
        
        return txt
        
    # 输入建议_默认
    if (action_p == "sug"):
        return get_sug(q_p)
        
    # 输入建议_默认
    if (action_p == "sug_app"):
        return get_sug(q_p,out_put="app")
        
    # 展示知识图谱
    if (action_p == "show_kg"):
    
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        txt = ""
        
        sql = "select question,answer from qa where id=" + str(id_p)
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "<center>所需数据已删除或数据库读取错误</center>" 
        
        txt += "<center>"
        txt += "<div style=\"width:502px;align:left;\">"
        txt += "<div><h4>"
        txt += rows[0][0]
        txt += "<h4></div>"
        txt += "<div><p align=\"left\">"
        txt += rows[0][1]
        txt += "</p></div>"
        txt += "</div>"
        txt += "<div><font style=\"font-size:11px;font-family: 微软雅黑;\" color=\"#cccccc\">特别声明：以上文本，仅供参考，不应作为诊断和诉讼的依据，请谨慎使用！</font></div>"
        txt += "</center>"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
    # 展示问答对原始语料
    if (action_p == "show_qa"):
    
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        txt = ""
        sql = "select question,answer from qa where id=" + str(id_p)
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "<center>所需数据已删除或数据库读取错误</center>" 
        
        txt += "<center>"
        txt += "<div style=\"width:502px;align:left;\">"
        txt += "<div><h4>"
        txt += rows[0][0]
        txt += "<h4></div>"
        txt += "<div><p align=\"left\">"
        txt += rows[0][1]
        txt += "</p></div>"
        txt += "</div>"
        txt += "<div><font style=\"font-size:11px;font-family: 微软雅黑;\" color=\"#cccccc\">特别声明：以上文本，仅供参考，不应作为诊断和诉讼的依据，请谨慎使用！</font></div>"
        txt += "</center>"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
    # 生存预测
    if (action_p == "alive"):
    
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
    
        txt = ""
        txt += "<center>"
        
        sql = "select keyword,early,mid,later,I,II,III,IV,V from devine_alive where keyword = '" + q_p + "' order by power desc limit 5"
        res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res < 1):
        
            sql = "select keyword,early,mid,later,I,II,III,IV,V from devine_alive where keyword like '%" + q_p + "%' order by power desc limit 5"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res < 1):
                return "<br><br><br>资料不足，无法预测。请更换关键词，或过段时间再试！</center>"
            else:
                txt += "<br><br><br><div>没有直接匹配结果，找到 <<" + q_p + ">> 相关病症的生存预测期:</div>"
                for row in rows:
                    txt += "<br><br><br><div><<" + row[0] + ">>的生存预测期:</div>"
                    txt += "<div><br></div>"
                    txt += "<div>早期:" + str(row[1]) + "个月</div>"
                    txt += "<div>中期:" + str(row[2]) + "个月</div>"
                    txt += "<div>晚期:" + str(row[3]) + "个月</div>"
                    txt += "<div>一(I)期:" + str(row[4]) + "个月</div>"
                    txt += "<div>二(II)期:" + str(row[5]) + "个月</div>"
                    txt += "<div>三(III)期:" + str(row[6]) + "个月</div>"
                    txt += "<div>四(IV)期:" + str(row[7]) + "个月</div>"
                    txt += "<div>五(V)期:" + str(row[8]) + "个月</div>"
                    
        else:
            
            txt += "<br><br><br><div><<" + q_p + ">>的生存预测期:</div>"
            txt += "<div><br></div>"
            txt += "<div>早期:" + str(rows[0][1]) + "个月</div>"
            txt += "<div>中期:" + str(rows[0][2]) + "个月</div>"
            txt += "<div>晚期:" + str(rows[0][3]) + "个月</div>"
            txt += "<div>一(I)期:" + str(rows[0][4]) + "个月</div>"
            txt += "<div>二(II)期:" + str(rows[0][5]) + "个月</div>"
            txt += "<div>三(III)期:" + str(rows[0][6]) + "个月</div>"
            txt += "<div>四(IV)期:" + str(rows[0][7]) + "个月</div>"
            txt += "<div>五(V)期:" + str(rows[0][8]) + "个月</div>"
        txt += "<div><br><br><font style=\"font-size:11px;font-family: 微软雅黑;\" color=\"#cccccc\">特别声明：以上预测结果，仅供参考，不应作为诊断和诉讼的依据，请谨慎使用！</font></div>"
        txt += "</center>"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
    # 费用估算
    if (action_p == "cost"):
        
        txt = ""
        txt += "<center>"
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        sql_1 = "select keyword,cost,norms from devine_cost_ill where keyword = '" + q_p + "' "
        sql_2 = "select keyword,cost,norms from devine_cost_drug where keyword = '" + q_p + "' "
        sql = sql_1 + " UNION " + sql_2 + " limit 10"
        res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res < 1):
        
            sql_1 = "select keyword,cost,norms from devine_cost_ill where keyword like '%" + q_p + "%' "
            sql_2 = "select keyword,cost,norms from devine_cost_drug where keyword like '%" + q_p + "%' "
            sql = sql_1 + " UNION " + sql_2 + " limit 10"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res < 1):
                return "<br><br><br>资料不足，无法预测。请更换关键词，或过段时间再试！</center>"
            else:
            
                txt += "<br><br><br><div>没有直接匹配结果，找到 <<" + q_p + ">> 相似项目的费用估算:</div>"
                for row in rows:
                    txt += "<br><br><br><div><<" + row[0] + ">>的费用估算:</div>"
                    txt += "<div><br></div>"
                    if (row[2] != "n/a"):
                        txt += "<div>参数:" + str(row[2]) + "</div>"
                    txt += "<div>大致花费是: <font style=\"font-size:33px;font-family:arial;\" color=\"#ff0000\">￥ " + str(row[1]) + "</font> 元</div>"
        else:
        
            txt += "<br><br><br><div><<" + q_p + ">>的费用估算:</div>"
            txt += "<div><br></div>"
            if (rows[0][2] != "n/a"):
                txt += "<div>参数:" + str(rows[0][2]) + "</div>"
            txt += "<div>大致花费是: <font style=\"font-size:33px;font-family:arial;\" color=\"#ff0000\">￥ " + str(rows[0][1]) + "</font> 元</div>"
            
        txt += "<div><br><br><font style=\"font-size:11px;font-family: 微软雅黑;\" color=\"#cccccc\">特别声明：以上估算结果，仅供参考，不应作为诊断和诉讼的依据，请谨慎使用！</font></div>"
        txt += "</center>"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
    #主题词字典
    def dic_kw_get(q_p=""):
    
        dic_key = {}
        try:
            dic_key = eval(get_mk(q_p=q_p)) # 问题主题词字典
        except:
            pass
            
        return dic_key
        
    # 主题词队列
    def list_kw_get(dic_key={}):
    
        list_key_order = []

        if (dic_key):
            list_key_order = sorted(dic_key.items(), key=lambda d:d[1], reverse = True)
        #print("问题主题词字典",dic_key,"问题主题词队列",list_key_order) #调试用
        
        return list_key_order
        
    # 句子单独计算TF_IDF值
    def tf_idf_sen(conn_p="",table_p="index_main",word_p="",list_p=[]):
        
        numb_tf_idf = 0
        numb_tf = list_p.count(word_p)
        numb_tf_all = len(list_p)
        idf = 1
        idf_all = int(config.dic_config["numb_q_all"])
        dae_base = inc_ml.Dae_base() # 示例化基础算法类
        
        # 或缺实时IDF分母值
        sql = "select idf from " + table_p + " where keyword = '" + word_p + "'"
        res, rows = conn_p.read_sql(sql)
        if (res > 0):
            idf += rows[0][0]
            
        numb_tf_idf = dae_base.tf_idf(nump_tf_p=numb_tf,numb_div_p=numb_tf_all,numb_all_p=idf_all,numb_idf_p=idf)
        
        return numb_tf_idf,numb_tf,idf
    
    # 短文本相似主函数
    def similar_shorttxt(content_p="",key_p="",action_p="cos"):
        
        import diy.inc_nlp as inc_nlp # 自然语言处理模块
        value_s = 0.0 # 相似度值 
        similar = inc_nlp.Similar() # 相似度类的实例化
        segment = inc_nlp.Segment()  # 分词对象实例化
        list_1 = [] # 原文本比对分词数组
        list_2 = [] # 对比文本比对分词数组
        
        for x in segment.seg_jieba(key_p):
            list_1.append(x)
        
        for y in segment.seg_jieba(content_p):
            list_2.append(y)
        
        # 相似度计算处理
        # 余弦相似度
        if (action_p == "cos"):
            value_s = similar.cos_word(sim_1=list_1,sim_2=list_2)
        
        return value_s
        
    # 短文本相似度
    if (action_p == "similar_shorttxt"):
    
        dic_t = {} # 结果字典
        dic_t["value_similar"] = similar_shorttxt(content_p=answer_p,key_p=q_p,action_p="cos")
        
        return dic_t
    
    # 用相似度法抽取答案主函数
    def extract_answer_similar(content_p="",key_p=""):
    
        import diy.inc_nlp as inc_nlp # 自然语言处理模块
        
        txt = "" # 最后返回的文本型json编码
        dic_sen_main = {} # 主句分段字典
        list_t = [] # 临时队列
        dic_q_kw = {} # 问题（摘要）字典
        dic_t_kw ={} # 临时摘要字典
        dic_sm ={} # 相似度字典
        dic_sen_all={} # 句子字典含段落号
        sm_t = 0.0 #相似度值
        list_order = [] # 最后的抽取排名
        list_last = [] # 最后的结果队列
        segment = inc_nlp.Segment()  # 分词对象实例化
        numb_tf = 0 # 主句中的tf分子
        step_is = "abstract" #语义相似度匹配方法标定 默认是摘要法
        list_cos = []
        cos_t = 0.0 # 临时余弦值 
        
        similar = inc_nlp.Similar() # 相似度类的实例化
        
        extract_txt = inc_nlp.Extract_txt() # 实例文本化抽取类
        dic_sen_main = extract_txt.sentence_div_main_get(content_p=content_p) #构造分句字典
        
        # 相似度计算处理
        
        # 默认进行摘要法
        if (step_is == "abstract"):
        
            dic_q_kw = dic_kw_get(q_p=q_p) # 构造问题主题词摘要
            
            if (not dic_q_kw):
            
                step_is = "entity" # 主题摘要为空 进行下一步实体匹配
            
            else:
            
                # 构造问题分词队列
                for m in dic_q_kw:
                    list_cos.append(m)
            
                k = 1
                for x in dic_sen_main:
                    m = 1
                    for y in dic_sen_main[x]:
            
                        if (y.strip() != ""):
                            list_t = []
                    
                        # 转格式存入列表
                            for w in segment.seg_jieba(y):
                                list_t.append(w)
                            
                            # 计算传统余弦相似度
                            cos_t = similar.cos_word(sim_1=list_cos,sim_2=list_t)
                            #print (k," 传统余弦相似度：",cos_t) # 调试用
                            #print ("段落编号:",x,"主句编号：",k,"主句内容：",y) #调试用
                    
                            for z in dic_q_kw:
                    
                                if (z in list_t):
                        
                                    numb_tf = round(list_t.count(z)/len(list_t),10) 
                            
                                    #print ("段落编号:",x,"主句编号：",k,"命中的主题词：",z,"主句中的rank值",numb_tf) #调试用

                                    if k in dic_sm:
                                        dic_sm[k] = dic_sm[k] + numb_tf
                                    else:
                                        dic_sm[k] = numb_tf
                                
                        m += 1
                        dic_sen_all[k] = [y,"[" + str(k)+ ","+str(x)+ "," + str(m) + "]",cos_t]
                        k += 1
                #print("句子字典：",dic_sen_all) # 调试用
                if (dic_sm):
                    list_order = sorted(dic_sm.items(), key=lambda d:d[1], reverse = True)
                else:
                    # 主题词法完全不匹配 进行实体法匹配 
                    step_is = "entity"
        
        # 实体匹配法
        if (step_is == "entity"):
        
            try:
                dic_t_kw = eval(get_ne(q_p=q_p))
            except:
                pass

            if (not dic_t_kw):
            
                step_is = "virtual" # 主题摘要为空 进行下一步虚拟答案匹配
                
            else:
                
                list_cos = []
                # 构造问题分词队列
                for m in dic_q_kw:
                    list_cos.append(m)
                    
                # 构造tf_idf字典
                rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
                
                for x in dic_t_kw:
                    
                    for w in segment.seg_jieba(q_p):
                        list_t.append(w)
                    # 计算传统余弦相似度
                    cos_t = similar.cos_word(sim_1=list_cos,sim_2=list_t)
                            
                    numb_tf_idf,numb_tf,idf=tf_idf_sen(conn_p=rs_basedata_mysql,table_p="index_main",word_p=x,list_p=list_t)
                    dic_q_kw[x]=[numb_tf_idf,numb_tf,idf,"n"]
                    #print (dic_q_kw)
                
                rs_basedata_mysql.close()
                
                k = 1
                for x in dic_sen_main:
                    m = 1
                    for y in dic_sen_main[x]:
            
                        if (y.strip() != ""):
                            list_t = []
                    
                        # 转格式存入列表
                            for w in segment.seg_jieba(y):
                                list_t.append(w)
                    
                            #print ("段落编号:",x,"主句编号：",k,"主句内容：",y) #调试用
                        
                    
                            for z in dic_q_kw:
                    
                                if (z in list_t):
                        
                                    numb_tf = round(list_t.count(z)/len(list_t),10) 
                            
                                    #print ("段落编号:",x,"主句编号：",k,"命中的主题词：",z,"主句中的rank值",numb_tf) #调试用

                                    if k in dic_sm:
                                        dic_sm[k] = dic_sm[k] + numb_tf
                                    else:
                                        dic_sm[k] = numb_tf
                        m += 1
                        dic_sen_all[k] = [y,"[" + str(k)+ ","+str(x)+ "," + str(m) + "]",cos_t]
                        k += 1
                #print("句子字典：",dic_sen_all) # 调试用
                if (dic_sm):
                    list_order = sorted(dic_sm.items(), key=lambda d:d[1], reverse = True)
                else:
                    # 主题词法完全不匹配 进行实体法匹配 
                    step_is = "virtual"
            
        # 构造json码
        print ("最终生效步骤：",step_is)
        dic_last = {}
        j = 1
        for x in list_order:
            dic_last[j] = [dic_sen_all[x[0]][0],x[1],dic_sen_all[x[0]][1],dic_sen_all[x[0]][2]]
            j += 1
        
        return dic_last
        
    # 相似度法抽取答案
    if (action_p == "answer_extract_similar"):
        txt = extract_answer_similar(content_p=answer_p,key_p=q_p)
    
    # 整体返回文本型结果
    return txt

def main():

    #1 过程一
    #2 过程二
    #3 过程三
    print("")
    
if __name__ == '__main__':
    main()

    
#---------- 主过程<<结束>> -----------#