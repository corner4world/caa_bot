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

#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----

sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
import config #系统配置参数
from diy.inc_hash import hash_make # 基本自定义hash模块
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
from dae.inc_dae import * # 基本自定义hash模块

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

sys.path.append("..")

import config #系统配置参数

# ---本模块内部类或函数定义区
class Result_base(object):
    
    def __init__(self):
        pass
    
    # 正序生成
    def forward_get(self,sgm_list):
    # segm_str_cls = inc_html_re.filter_tags(segm_str)

        list_p = sgm_list.split("\n")
        dic_p = {}
        arr_t =[]
        
        i = 0
        for i in range(len(list_p)-1):
            
            if (list_p[i] in dic_p):
                
                arr_t = dic_p[list_p[i]]
                arr_t.append(i+1)
                
            else:
                
                arr_t =[]
                arr_t.append(i+1)
            
            dic_p[list_p[i]] = arr_t
        
            
        #追加词向量计数总值
        dic_p["numb_key_ldae"] = [i]
        
        return dic_p

# 问答对象
class Qa(Result_base):
    
    # 正排处理
    def forward(self,action_p="",tid_p=0,word_step_p=6,tf_idf_if=0,mem_if=0,t_name_p = "qa"):
        
        txt = ""
        nlp_base = Nlp_base() # 自定义自然语言处理基础模块
        dic_q = {} # 问题字典
        dic_a = {} # 答案字典
        
        # 清晰词队列
        clear_list = ["神医","神药","包治百病","绝对药到病除"]
        ignore_list = ["xa0","http","https"," ","http:","https:","\\xa0"]

        dic_m = {} #虚拟数据库主字典
        
        sql = "select id,question,answer from " + t_name_p + " where v1=0 "
        #sql += " limit 32" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        
        if (res < 1):
            return "问答知识库总表为空或读取错误"
        
        numb_rs_all = res
        count_do = 1
        

        #数据切片的主循环
        for row in rows:
            
            sql = "update " + t_name_p + " set v1=1 where id =" + str(row[0]) #打上处理过的访问标记
            updtae_if = rs_basedata_mysql.write_sql(sql)
            question = row[1]
            answer = row[2]
            
            # 防忽悠词 + 自然标注分段处理
            url_p = config.dic_config["url_api"] + "api?q=" + question + "&action=seg"
            txt = ""
            try:
                txt = inc_crawler_fast.get_html_fast(url_p)
            except:
                pass
                
            #顺排正序处理
            txt = txt[1:]
            txt = txt[:-1]
            txt = txt.replace("\"","")
            txt = txt.replace("\n","")
            list_t = txt.split(",")
            
            smt_list_q = ""
            
            for y in list_t:
                str_s = ""
                try:
                    str_s = y.split(":")[1]
                    str_s = str_s.strip()
                    # print (str_s) #调试用
                except:
                    pass
                if (len(str_s) > 1):
                    if not str_s in clear_list:
                        smt_list_q += str_s + "\n"
            
            #print (smt_list_q) #调试用

            #生成正排
            word_dic = self.forward_get(smt_list_q)
            #print(word_dic) # 调试用

            #回存结果
            sql = "update " + t_name_p + " set seq_q='" + transfer_quotes(str(word_dic)) + "' where id =" + str(row[0])
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            #词向量索引操作
            if (tf_idf_if == 1 and mem_if == 0 ):
                
                table_index = "index_question"
                
                for x in word_dic:
                
                    sql = "select id from " + table_index + " where keyword ='" + x + "'"
                    res,rows = rs_basedata_mysql.read_sql(sql)

                    if (res < 1):
                        if (x == "numb_key_ldae"):
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(word_dic[x][0])+ ",idf=1"
                        else:
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(len(word_dic[x]))+ ",idf=1"
                    else:
                        if (x == "numb_key_ldae"):
                            sql = "update " + table_index + " set tf= tf+" + str(word_dic[x][0])+ ",idf=idf+1 where id=" + str(rows[0][0])
                        else:
                            sql = "update " + table_index + " set tf= tf+" + str(len(word_dic[x]))+ ",idf=idf+1 where id=" + str(rows[0][0])
                            
                    sql_do_if = rs_basedata_mysql.write_sql(sql)
                    #print (sql) #调试用
          
            # 答案的正排处理
                        
            # 防忽悠词 + 自然标注分段处理
            url_p = config.dic_config["url_api"] + "api?q=" + answer + "&action=seg"
        
            try:
                txt = inc_crawler_fast.get_html_fast(url_p)
                dic_q = eval(txt)
            except:
                pass
            
            # 分词队列过滤
            smt_list_a = ""
            str_t = ""
            for x in dic_q:
                str_t = dic_q[x]
                if (len(str_t) > 1):
                    if not str_t in clear_list:
                        smt_list_a += str_t + "\n"

            #生成正排
            word_dic = self.forward_get(smt_list_a)
            #print(word_dic) # 调试用
            
            #回存结果
            sql = "update " + t_name_p + " set seq_a='" + transfer_quotes(str(word_dic)) + "' where id =" + str(row[0])
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            
            # 是否进行tf-idf的计数统计
            
            #词向量索引操作
            if (tf_idf_if == 1 and mem_if == 0 ):
                
                table_index = "index_answer"
                
                for x in word_dic:
                
                    sql = "select id from " + table_index + " where keyword ='" + x + "'"
                    res,rows = rs_basedata_mysql.read_sql(sql)

                    if (res < 1):
                        if (x == "numb_key_ldae"):
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(word_dic[x][0])+ ",idf=1"
                        else:
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(len(word_dic[x]))+ ",idf=1"
                    else:
                        if (x == "numb_key_ldae"):
                            sql = "update " + table_index + " set tf= tf+" + str(word_dic[x][0])+ ",idf=idf+1 where id=" + str(rows[0][0])
                        else:
                            sql = "update " + table_index + " set tf= tf+" + str(len(word_dic[x]))+ ",idf=idf+1 where id=" + str(rows[0][0])
                            
                    sql_do_if = rs_basedata_mysql.write_sql(sql)
                    #print (sql) #调试用
            
                
            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
        
        return txt
        
    # 词向量的分词处理
    def seg_list(self,action_p="",tid_p=0,word_step_p=6,tf_idf_if=0,mem_if=0,t_name_p = "qa"):
        
        txt = ""
        list_q = []
        list_a = []
        segment = Segment() #分词模块实例化
        sql = "select id,question,answer from " + t_name_p + " where v3=0 "
        #sql += " limit 32" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "问答知识库总表为空或读取错误"
        numb_rs_all = res
        count_do = 1
        
        #数据切片的主循环
        for row in rows:
            sql = "update " + t_name_p + " set v3=1,"
            
            list_q = segment.seg_jieba(txt_p=row[1],way_p="")
            str_t = ""
            for x in list_q:
                str_t += x.replace("'","\'") + " "
            if (str_t):
                str_t = str_t[:-1]
            sql += "seg_q='" + str_t + "',"
            list_q = segment.seg_jieba(txt_p=row[2],way_p="")
            str_t = ""
            for x in list_q:
                str_t += x.replace("'","\'") + " "
            str_t = str_t[:-1]
            sql += "seg_a='" + str_t + "',"
            if (str_t):
                sql = sql[:-1]
            sql += " where id=" + str(row[0])
            # print(sql) 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
        return txt
# 数据页
class Page(Result_base):
    
    # 正排处理
    def forward(self,action_p="",tid_p=0,word_step_p=6,tf_idf_if=0,mem_if=0,t_name_p = "page"):
    
        # 清洗词队列
        clear_list = ["神医","神药","包治百病","绝对药到病除"]
        
        sql = "select id,title,content from " + t_name_p + " where v1=0"
        #sql += " limit 3" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        
        if (res < 1):
            return "问答知识库总表为空或读取错误"
        
        numb_rs_all = res
        count_do = 1
        

        #数据切片的主循环
        for row in rows:
            #print (row) #调试用
            
            sql = "update " + t_name_p + " set v1=1 where id =" + str(row[0]) #打上处理过的访问标记
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            str_t = row[1] + " " + row[2]
            
            url_p = config.dic_config["url_api"] + "api?q=" + str_t + "&action=seg"
            list_t = []
            
            txt = ""
            try:
                txt = inc_crawler_fast.get_html_fast(url_p)
            except:
                pass
                
            #顺排正序处理
            txt = txt[1:]
            txt = txt[:-1]
            txt = txt.replace("\"","")
            txt = txt.replace("\n","")
            list_t = txt.split(",")
            
            smt_list_q = ""
            
            for y in list_t:
                str_s = ""
                try:
                    str_s = y.split(":")[1]
                    str_s = str_s.strip()
                    # print (str_s) #调试用
                except:
                    pass
                if (len(str_s) > 1):
                    if not str_s in clear_list:
                        smt_list_q += str_s + "\n"
            
            #print (smt_list_q) #调试用

            #生成正排
            word_dic = self.forward_get(smt_list_q)
            #print(word_dic) # 调试用

            #回存结果
            sql = "update " + t_name_p + " set seq='" + transfer_quotes(str(word_dic)) + "' where id =" + str(row[0])
            updtae_if = rs_basedata_mysql.write_sql(sql)
                
            #词向量索引操作
            if (tf_idf_if == 1 and mem_if == 0 ):
                
                table_index = "index_main"
                
                for x in word_dic:
                
                    sql = "select id from " + table_index + " where keyword ='" + x + "'"
                    res,rows = rs_basedata_mysql.read_sql(sql)

                    if (res < 1):
                        if (x == "numb_key_ldae"):
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(word_dic[x][0])+ ",idf=1"
                        else:
                            sql = "insert " + table_index + " set keyword='" + x + "',keyword_hash='" + hash_make(x) + "',tf=" + str(len(word_dic[x]))+ ",idf=1"
                    else:
                        if (x == "numb_key_ldae"):
                            sql = "update " + table_index + " set tf= tf+" + str(word_dic[x][0])+ ",idf=idf+1 where id=" + str(rows[0][0])
                        else:
                            sql = "update " + table_index + " set tf= tf+" + str(len(word_dic[x]))+ ",idf=idf+1 where id=" + str(rows[0][0])
                            
                    sql_do_if = rs_basedata_mysql.write_sql(sql)
                    #print (sql) #调试用
            
                
            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            
            count_do += 1
        
        
    
# 词向量
class Vec():

    # 获得前后相关词
    def get_ba_list(self,str_p="",dic_stop={},step_p = 3):
        
        arr_t = []
        try:
            arr_t = str_p.split(" ")
        except:
            pass
        numb_arr = len(arr_t)
            
        str_t = ""
        list_t = []
        list_p = [] #最后的待处理列表
            
        # 待处理队列预处理 去掉单字 和 停用词字典
        for x in arr_t:
                
            str_t = x
            str_t = str_t.strip()
            
            if (len(str_t) > 1):
                if (str_t in dic_stop):
                    pass
                else:
                    #print (str_t) # 调试用
                    list_t.append(str_t)
                        
        #print (list_t) # 调试用
        numb_arr = len(list_t)
        j = 0
        while (j < numb_arr):
        
            list_b = ["","",""] # 前关联词列表 维度3
            list_a = ["","",""] # 后关联词列别 维度3
                    
            #print(j,list_t[j]) # 调试用
            if (j == 0):
                list_a = list_t[j+1:j+step_p+1]
                #print ("后置 - ",list_a)
            if (j == numb_arr-1):
                list_b = list_t[j-step_p-1:j-1]
                #print ("前置 - ",list_b) # 调试用
            if (j > 0 and j < numb_arr-1):
                for i in range(step_p+1):
                    if (list_t[j-i:j]):
                        list_b = list_t[j-i:j]
                #print ("前置 - ",list_b) # 调试用
                if (list_t[j+1:j+step_p+1]):
                    list_a = list_t[j+1:j+step_p+1]
                    #print ("后置 - ",list_a) # 调试用
                
            list_p.append([list_t[j],list_b,list_a]) #增值到中间值列表
                
            j += 1
            
        return list_p

    # 词向量基础数据处理
    def vec_basedata(self,action_p="",tid_p=0,word_step_p=6,tf_idf_if=0,mem_if=0,t_name_p = "qa"):
        
        txt = ""
        arr_t = [] # 临时数组
        str_t = "" # 临时字符串
        path_p = "" # 文件路径
        dic_stop = {} # 停用词字典
        numb_arr = 0 # 待处理列表长度
        list_t = [] # 临时队列
        list_sql = [] # sql操作临时列表
        hash_t = "" #临时哈希值
        
        sql = "select id,seg_q,seg_a from " + t_name_p + " where v4=0 "
        #sql += " limit 8" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "问答知识库总表为空或读取错误"
        numb_rs_all = res
        count_do = 1
        
        #读取停用词字典
        select = "select keyword,power from keyword_stop order by keyword"
        res_w,rows_w = rs_way_mysql.read_sql(sql)
        if (res_w < 1):
            return "停用词字典为空或读取错误"
        for row in rows_w:
            dic_stop[row[0]] = row[1]
            
        # 建立词向量专用数据库连接
        rs_vec_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_vec_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        #数据切片的主循环
        for row in rows:
            
            # 问题的处理
            list_sql = self.get_ba_list(str_p=row[1],dic_stop=dic_stop,step_p=3)
            #print (row[1],list_sql) # 调试用
            for x in list_sql:
                hash_t = hash_make(x[0])
                sql = "select id from index_vec_q where keyword='" + x[0] + "'"
                res_t,rows_t = rs_basedata_mysql.read_sql(sql)
                if (res_t < 1):
                    sql = "insert index_vec_q set keyword='" + x[0] + "',keyword_hash='" + hash_t + "',tf=tf+1" #打上处理过的访问标记
                    insert_if = rs_basedata_mysql.write_sql(sql)
                else:
                    sql = "update index_vec_q set tf=tf+1 where id=" + str(rows_t[0][0])
                    updtae_if = rs_basedata_mysql.write_sql(sql)
                    
                # 写入待统计索引
                table_child = "z_relate_q_" + hash_t
                sql="create table if not exists " + table_child  + " like z_relate"
                create_if = rs_vec_mysql.write_sql(sql)
                
                sql = "insert " + table_child + " set "
                
                j = 1
                for y in x[1]:
                    if (y != ""):
                        sql += "b" + str(j) + "='" + y + "',"
                    j += 1
                
                j = 1
                for y in x[2]:
                    if (y != ""):
                        sql += "a" + str(j) + "='" + y + "',"
                    j += 1
                    
                sql = sql[0:-1]
                #print (sql) #调试用
                insert_if = rs_vec_mysql.write_sql(sql)
            
            # 答案的处理
            list_sql = self.get_ba_list(str_p=row[2],dic_stop=dic_stop,step_p=3)
            #print (row[2],list_sql) # 调试用
            for x in list_sql:
                hash_t = hash_make(x[0])
                sql = "select id from index_vec_a where keyword='" + x[0] + "'"
                res_t,rows_t = rs_basedata_mysql.read_sql(sql)
                if (res_t < 1):
                    sql = "insert index_vec_a set keyword='" + x[0] + "',keyword_hash='" + hash_t + "',tf=tf+1" #打上处理过的访问标记
                    insert_if = rs_basedata_mysql.write_sql(sql)
                else:
                    sql = "update index_vec_a set tf=tf+1 where id=" + str(rows_t[0][0])
                    updtae_if = rs_basedata_mysql.write_sql(sql)
                
                # 写入待统计索引
                table_child = "z_relate_a_" + hash_t
                sql="create table if not exists " + table_child  + " like z_relate"
                create_if = rs_vec_mysql.write_sql(sql)
                
                sql = "insert " + table_child + " set "
                
                j = 1
                for y in x[1]:
                    if (y != ""):
                        sql += "b" + str(j) + "='" + y + "',"
                    j += 1
                
                j = 1
                for y in x[2]:
                    if (y != ""):
                        sql += "a" + str(j) + "='" + y + "',"
                    j += 1
                    
                sql = sql[0:-1]
                #print (sql) #调试用
                insert_if = rs_vec_mysql.write_sql(sql)
                
            sql = "update " + t_name_p + " set v4=1 where id=" + str(row[0]) + " " #打上处理过的访问标记
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
        
        return txt
    
    # 相关词统计
    def vec_relate(self,action_p="",tid_p=0,word_step_p=6,tf_idf_if=0,mem_if=0,t_name_p = "index_vec_q"):
        txt = ""
        hash_t = ""
        sql = "select keyword_hash from " + t_name_p + " where v1=0 order by tf desc"
        #sql += " limit 1" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "问题主索引表为空或读取失败"
        else:
            numb_rs_all = res
            
        # 建立词向量专用数据库连接
        rs_vec_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_vec_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
            
        count_do = 1

        for row in rows:
            
            hash_t = row[0]
            dic_t = {}
            
            # 统计问题
            for i in range(3):
                column_t = "b" + str(i+1)
                sql = "select " + column_t + ",count(" + column_t + ") as pm "
                sql += " from z_relate_q_" + hash_t 
                sql += " where not " + column_t + " = 'n/a' "
                sql += " group by " + column_t 
                sql += " order by pm desc"
                sql += " limit 1"
                res_t,rows_t = rs_vec_mysql.read_sql(sql)
                if (res_t > 0):
                    dic_t[column_t] = rows_t[0][0]
                    
            # 统计答案
            for i in range(3):
                column_t = "a" + str(i+1)
                sql = "select " + column_t + ",count(" + column_t + ") as pm "
                sql += " from z_relate_q_" + hash_t 
                sql += " where not " + column_t + " = 'n/a' "
                sql += " group by " + column_t 
                sql += " order by pm desc"
                sql += " limit 1"
                res_t,rows_t = rs_vec_mysql.read_sql(sql)
                if (res_t > 0):
                    dic_t[column_t] = rows_t[0][0]
            
            sql_value = ""
            for x in dic_t:
                sql_value += x + "='" + dic_t[x] + "',"
            
            sql = "update index_question set " + sql_value + "v1=1 where keyword_hash='" + hash_t + "'"
            #print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            sql = "update " + t_name_p + " set " + sql_value + "v1=1 where keyword_hash='" + hash_t + "'"
            #print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)

            print ("第" + str(count_do) + "次问题处理操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
        
        count_do = 0
        t_name_p = "index_vec_a"
        sql = "select keyword_hash from " + t_name_p + " where v1=0 order by tf desc"
        #sql += " limit 1" #调试用
        res,rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "答案主索引表为空或读取失败"
        else:
            numb_rs_all = res
        
        for row in rows:
            
            hash_t = row[0]
            dic_t = {}
            
            # 统计问题
            for i in range(3):
                column_t = "b" + str(i+1)
                sql = "select " + column_t + ",count(" + column_t + ") as pm "
                sql += " from z_relate_a_" + hash_t 
                sql += " where not " + column_t + " = 'n/a' "
                sql += " group by " + column_t 
                sql += " order by pm desc"
                sql += " limit 1"
                res_t,rows_t = rs_vec_mysql.read_sql(sql)
                if (res_t > 0):
                    dic_t[column_t] = rows_t[0][0]
            
            # 统计答案
            for i in range(3):
                column_t = "a" + str(i+1)
                sql = "select " + column_t + ",count(" + column_t + ") as pm "
                sql += " from z_relate_a_" + hash_t 
                sql += " where not " + column_t + " = 'n/a' "
                sql += " group by " + column_t 
                sql += " order by pm desc"
                sql += " limit 1"
                res_t,rows_t = rs_vec_mysql.read_sql(sql)
                if (res_t > 0):
                    dic_t[column_t] = rows_t[0][0]
            
            sql_value = ""
            for x in dic_t:
                sql_value += x + "='" + dic_t[x] + "',"

            sql = "update index_answer set " + sql_value + "v1=1 where keyword_hash='" + hash_t + "'"
            #print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            sql = "update " + t_name_p + " set " + sql_value + "v1=1 where keyword_hash='" + hash_t + "'"
            #print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            print ("第" + str(count_do) + "次答案处理操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
            
        return txt

# 用户画像类
class User():
    
    def q2u(self,numb_p=6):
    
        txt = ""
        dic_t = {}
        dic_r = {} # 排序字典
        numb_work_all = 0
        numb_rs_all = 0
        numb_word_all = 0
        numb_td_idf = 0 # TF-IDF值
        rank_t = 0 # 最后的排名值
        list_t = [] # 排名队列
        sql_last = "" # 最后的更新语句
        sql_head = ""
        sql_where = ""
        
        import math #数学计算库
        
        # 数据源装载
        sql = "select count(*) from qa"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "记录总数为空或数据库读取错误"
        else:
            numb_rs_all = rows[0][0] # 获得文档总数
            if (numb_rs_all < 1):
                return "记录总数为空或数据库读取错误"
                
        sql = "select hash,seq_q from qa where v3=0"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "已全部处理完毕或数据库读取错误"
        else:
            numb_work_all = res
            
        # 主循环开始
        count_do = 1
        for row in rows:
        
            dic_r = {}
            sql = "update qa set v3=1 where hash='" + row[0] + "'"
            update_if = rs_basedata_mysql.write_sql(sql) # 打上访问标记
            
            # 获得正序字典
            try:
                dic_t = eval(row[1])
            except:
                continue
                
            if (dic_t):
                
                numb_word_all = len(dic_t)
                
                for x in dic_t:
                    
                    # 构造排序字典
                    sql = "select idf from index_question where keyword='" + x + "'"
                    res_t, rows_t = rs_basedata_mysql.read_sql(sql)
                    if (res_t > 0 and x != 'numb_key_ldae'):
                        numb_td_idf = round(len(dic_t[x])/numb_word_all * math.log(numb_rs_all/(rows_t[0][0]+1)),8)
                        rank_t = numb_td_idf # 暂时不做任何修订
                        #print (x,dic_t[x],numb_td_idf,rank_t) # 调试用
                        if (x in dic_r):
                            pass
                        else:
                            dic_r[x] = rank_t
                    
                #print (dic_r) # 调试用
                list_t = sorted(dic_r.items(), key=lambda d:d[1], reverse = True)#排名
                #print (list_t) # 调试用
                
                # 检索用户模型是否存在
                sql_last = ""
                sql = "select id from user_main where hash='" + row[0] + "' limit 1"
                res_u, rows_u = rs_basedata_mysql.read_sql(sql)
                if (res_u > 0):
                    sql_head = "update user_main set "
                    sql_where = " where id=" + str(rows_u[0][0]) + " "
                else:
                    sql_head = "insert user_main set "
                    sql_last = "hash='" + row[0] + "',"
                    sql_where = " "
                
                i = 1 
                for y in list_t:
                    print (y[0],y[1])
                    sql_last += "m" + str(i)+ "='" + y[0] + "',a" + str(i) + "=" + str(y[1]) + "," 
                    if (i  >= numb_p):
                        break
                    else:
                        i += 1
                
                # 数据存入用户画像模型表
                sql_last = sql_head + sql_last + sql_where
                
                if (sql_last):
                    sql_last = sql_last[:-1]
                
                print (sql_last) # 调试用
                sql_do = rs_basedata_mysql.write_sql(sql_last)
                
            #e("stop_1") #调试用

            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_work_all) + "%")
            count_do += 1
            
        return txt
        
        
# ---- 模块预留综合处理函数 -----
def run_it():

    print("") # 调试用

#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    #1 过程一
    run_it()
    #2 过程二
    #3 过程三

    
if __name__ == '__main__':
    main()

    
#---------- 主过程<<结束>> -----------#