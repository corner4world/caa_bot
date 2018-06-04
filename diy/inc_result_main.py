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
import math # 引入数学计算模块

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----

sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
import config #系统配置参数
from diy.inc_hash import hash_make # 基本自定义hash模块
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
import dae.inc_dae as inc_dae # 引用所有数据分析模块
import dae.diy.inc_nlp as inc_nlp # 引用所有数据分析模块
import diy.inc_dic as inc_dic # 引用字典模块

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
    
    # 正排生成
    def forward_get(self,list_p=[]):

        dic_p = {}
        i = 1
        for x in list_p:
            if (x in dic_p):
                dic_p[x].append(i)
            else:
                dic_p[x] = [i]
            i +=1

        return dic_p
        

# 问答对象
class Qa(Result_base):

    # 词向量索引总表构造及相关td_idf基础值存储的方法函数
    def vec_make(self,table_name_p="",dic_p={},conn_data=""):
    
        dic_oneword = {} # 单字实义词字典
        dic_unitword = {} # 单字量词字典
        
        
        #导入特殊字典 用于字典容量不大的情况
        
        try:
            dic_oneword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_oneword.txt",split_p="\n")
        except:
            pass
            
        try:
            dic_unitword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_unitword.txt",split_p="\n")
        except:
            pass

        for x in dic_p:
            
            if (len(x.strip()) < 1):
                continue
                
            if (len(x.strip()) == 1):
                # 单个汉字的特殊规则
                if (x.strip() in dic_oneword or x.strip() in dic_unitword):
                    pass
                else:
                    continue
                    
            sql = "update " + table_name_p + " set power=power+1,tf=tf+" + str(len(dic_p[x])) + ",idf=idf+1 "
            sql += "where keyword=\"" + x.strip() + "\""
            #print(sql) # 调试用
            update_if = conn_data.write_sql(sql)
            if (update_if):
                pass
            else:
                sql = "insert " + table_name_p + " set keyword=\"" + x.strip() + "\",power=1,tf=" + str(len(dic_p[x])) + ",idf=1,keyword_hash=\"" + hash_make(x.strip()) + "\""
                insert_if = conn_data.write_sql(sql)
                            
            #print(sql) # 调试用
    
    # 索引生成
    def index_make(self,dic_p={},conn_basedate="",conn_index="",name_p="",dic_oneword={},dic_unitword={},numb_file_all=1,rankway_p=0,pid=0):
        
        do_if = False # 成功执行数
        rank_t = 0 # 每一个词向量元素的排名值
        numb_nij = 0 # 语料词向量元素的总数
        idf_t = 0 # IDF值
        hash_t = "" # 哈希值
        hash_p = "" # 关键词定位哈希值
        sql = ""
        x0 = 0
        x1 = 0
        x2 = 0
        x3 = 0
        
        for x in dic_p:
            numb_nij += len(dic_p[x])
        if (numb_nij < 1):
            return do_if
        
        for x in dic_p:
            
            hash_p = hash_make(x) # 生成词向量元素标定哈希值
            
            if (len(x.strip()) == 1):
                # 单个汉字的特殊规则
                if (x.strip() in dic_oneword or x.strip() in dic_unitword):
                    pass
                else:
                    continue
                    
            # 计算排名值
            # 标准TF_IDF法
            if (rankway_p == 0 and dic_p[x] != []):
            
                sql = "select idf from index_" + name_p + " where keyword='" + x + "'"
                res,rows = conn_basedate.read_sql(sql)
                if (res > 0):
                    idf_t = rows[0][0] 
                    if ((idf_t) < 1):
                        continue
                else:
                    continue
                rank_t = len(dic_p[x])/numb_nij*math.log(numb_file_all/idf_t)
                rank_t = int(numb_file_all*100*rank_t) 
                #print (x,rank_t) # 调试用
                
                # 存入数据页子表
                try:
                
                    sql="create table if not exists z_invert_" + name_p + "_" + hash_p + " like z_invert_" + name_p
                    create_if = conn_index.write_sql(sql)
                    
                    sql = "insert z_invert_" + name_p + "_" + hash_p + " set "
                    sql += " pid='" + str(pid) + "',"
                    
                    if (rank_t != 0):
                        sql += " rank=" + str(rank_t) + ","
                    if (hash_t != ""):
                        sql += " hash='" + hash_t + "',"
                    if (x0 != 0):
                        sql += "x0=" + str(x0) + ","
                    if (x1 != 0):
                        sql += "x1=" + str(x1) + ","
                    if (x2 != 0):
                        sql += "x2=" + str(x2) + ","
                    if (x3 != 0):
                        sql += "x3=" + str(x3) + "，"
                        
                    sql = sql[:-1]
                    insert_if = conn_index.write_sql(sql)
                    #print (sql) #调试用

                except:
                    
                    pass
                
        do_if = True
        return do_if
            
    
    # 知识库问答对词向量的分词处理
    def vector_preprocess(self,tf_idf_if_p=0,t_name_p="qa",conn_data="",mark_p="v5",numb_for_p=0,renew_if_p=1,forward_if_p=0):
        
        txt = "" # 结果文本
        list_q = [] # 问题分词列表
        list_a = [] # 答案分词列表
        list_al = [] # 精选答案分词列表
        time_start = datetime.datetime.now() #启动时间
        numb_all = 0 # 待处理记录总数
        numb_div = 0 # 每一块处理条数
        dic_q = {} # 问题正排字典
        dic_a = {} # 答案正排字典
        dic_al = {} # 精选答案正排字典
        sql_head = "update " + t_name_p + " set " # sql 语句头
        
        print ("mark_p=",mark_p,"numb_for_p=",numb_for_p,"renew_if_p=",renew_if_p,"forward_if_p=",forward_if_p,"tf_idf_if_p=",tf_idf_if_p) # 调试用
        
        # 游标清零处理
        if (renew_if_p == 1):
            sql = "update " + t_name_p + " set " + mark_p + "=0"
            update_if = conn_data.write_sql(sql) # 游标清零
            print ("游标清零处理结果：",update_if)
            sql = "truncate table index_question"
            clear_if = conn_data.write_sql(sql) # 游标清零
            print ("问题词向量索引表清零处理结果：",clear_if)
            sql = "truncate table index_answer"
            clear_if = conn_data.write_sql(sql) # 游标清零
            print ("答案词向量索引表清零处理结果：",clear_if)
            sql = "truncate table index_answer_last"
            clear_if = conn_data.write_sql(sql) # 游标清零
            print ("精选答案词向量索引表清零理结果：",clear_if)
            
        # 获得待处理记录总数
        sql = " select count(*) from " + t_name_p + " where " + mark_p + "=0"
        res,rows = conn_data.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_all = rows[0][0]
            print ("待处理数据库记录总数：",numb_all)
            if (numb_all == 0):
                return "全部数据处理完毕或数据库读取错误"
        
        segment = inc_nlp.Segment() #分词模块实例化
        
        if (numb_all/numb_for_p > 0 and numb_all/numb_for_p <= 1):
            numb_div = 1
            numb_for_p = 1
        else:
            numb_div = int(round(numb_all/numb_for_p))
         
        j = 1
        k = 0
        m = 0
        while (j <= numb_for_p):
            
            print("第 ",j," 次分块处理") #调试用
            sql = "select id,question,answer,answer_last from qa where " + mark_p + "=0 limit " + str(numb_div)
            res_t,rows_t = conn_data.read_sql(sql)
            if (res_t < 1):
                break
            for row in rows_t:
                
                # 不管成功失败都打上访问标记
                sql = "update " + t_name_p + " set " + mark_p + "=1 where id=" + str(row[0])
                update_if = conn_data.write_sql(sql)
                
                # 主处理sql语句
                sql = ""
                list_q = segment.jieba2list(token_p=segment.seg_jieba(txt_p=row[1],way_p=""))
                sql += "segment_question=\"" + str(list_q).replace("\"","\\\"") + "\","
                list_a = segment.jieba2list(token_p=segment.seg_jieba(txt_p=row[2],way_p=""))
                sql += "segment_answer=\"" + str(list_a).replace("\"","\\\"") + "\","
                list_al = segment.jieba2list(token_p=segment.seg_jieba(txt_p=row[3],way_p=""))
                sql += "segment_answer_last=\"" + str(list_al).replace("\"","\\\"") + "\","

                # 正排处理
                if (forward_if_p == 1):
                    dic_q = self.forward_get(list_p=list_q)
                    if (dic_q):
                        sql +="forward_question=\"" + str(dic_q).replace("\"","\\\"") + "\","
                    dic_a = self.forward_get(list_p=list_a)
                    if (dic_a):
                        sql +="forward_answer=\"" + str(dic_a).replace("\"","\\\"") + "\","
                    dic_al = self.forward_get(list_p=list_al)
                    if (dic_al):
                        sql +="forward_answer_last=\"" + str(dic_al).replace("\"","\\\"") + "\","
                sql = sql[:-1]
                sql = sql_head + sql
                sql += " where id=" + str(row[0])
                update_if = conn_data.write_sql(sql)
                if (update_if):
                    k += 1
                
                #print ("问题：",list_q,"答案：",list_a,"精选答案：",list_al) # 调试用
                
                # 词向量索引总表构造及相关td_idf基础值存储
                if (tf_idf_if_p == 1):
                
                    self.vec_make(table_name_p="index_question",dic_p=dic_q,conn_data=conn_data)
                    self.vec_make(table_name_p="index_answer",dic_p=dic_a,conn_data=conn_data)
                    self.vec_make(table_name_p="index_answer_last",dic_p=dic_al,conn_data=conn_data)
                
                m +=1
                print(m) #显示具体计数
                
                #return txt # 只循环一次中断调试用
                
            j += 1
            
        txt += "执行完毕，共耗时" +  str(round(time_cost(time_start),2)) + "秒,操作" + str(m) + " 次，成功" + str(k)+ "次。"
        return txt
        
    # 闲聊模板库词向量元素的预处理
    def vector_preprocess_gossip(self,tf_idf_if_p=0,t_name_p="qa_gossip",conn_data="",mark_p="v5",numb_for_p=0,renew_if_p=1,forward_if_p=0):
        
        txt = "" # 结果文本
        list_q = [] # 问题分词列表
        list_a = [] # 答案分词列表
        list_al = [] # 精选答案分词列表
        time_start = datetime.datetime.now() #启动时间
        numb_all = 0 # 待处理记录总数
        numb_div = 0 # 每一块处理条数
        dic_q = {} # 问题正排字典
        dic_a = {} # 答案正排字典
        sql_head = "update " + t_name_p + " set " # sql 语句头
        
        print ("mark_p=",mark_p,"numb_for_p=",numb_for_p,"renew_if_p=",renew_if_p,"forward_if_p=",forward_if_p,"tf_idf_if_p=",tf_idf_if_p) # 调试用
        
        # 游标清零处理
        if (renew_if_p == 1):
            sql = "update " + t_name_p + " set " + mark_p + "=0"
            update_if = conn_data.write_sql(sql) # 游标清零
            print ("游标清零处理结果：",update_if)
            sql = "truncate table index_question_gossip"
            clear_if = conn_data.write_sql(sql) # 游标清零
            print ("问题词向量索引表清零处理结果：",clear_if)
            sql = "truncate table index_answer_gossip"
            clear_if = conn_data.write_sql(sql) # 游标清零
            print ("答案词向量索引表清零处理结果：",clear_if)

        # 获得待处理记录总数
        sql = " select count(*) from " + t_name_p + " where " + mark_p + "=0"
        res,rows = conn_data.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_all = rows[0][0]
            print ("待处理数据库记录总数：",numb_all)
            if (numb_all == 0):
                return "全部数据处理完毕或数据库读取错误"
        
        segment = inc_nlp.Segment() #分词模块实例化
        
        if (numb_all/numb_for_p > 0 and numb_all/numb_for_p <= 1):
            numb_div = 1
            numb_for_p = 1
        else:
            numb_div = int(round(numb_all/numb_for_p))
         
        j = 1
        k = 0
        m = 0
        while (j <= numb_for_p):
            
            print("第 ",j," 次分块处理") #调试用
            sql = "select id,question,answer,answer_last from " + t_name_p + " where " + mark_p + "=0 limit " + str(numb_div)
            res_t,rows_t = conn_data.read_sql(sql)
            if (res_t < 1):
                break
            for row in rows_t:
                
                # 不管成功失败都打上访问标记
                sql = "update " + t_name_p + " set " + mark_p + "=1 where id=" + str(row[0])
                update_if = conn_data.write_sql(sql)
                
                # 主处理sql语句
                sql = ""
                if (row[1] is None):
                    list_q = []
                else:
                    list_q = segment.jieba2list(token_p=segment.seg_jieba(txt_p=row[1],way_p=""))
                if (list_q):
                    sql += "segment_question=\"" + str(list_q).replace("\"","\\\"") + "\","
                
                if (row[2] is None):
                    list_a = []
                else:
                    list_a = segment.jieba2list(token_p=segment.seg_jieba(txt_p=row[2],way_p=""))
                if (list_a):
                    sql += "segment_answer=\"" + str(list_q).replace("\"","\\\"") + "\","
                    

                # 正排处理
                if (forward_if_p == 1):
                    dic_q = self.forward_get(list_p=list_q)
                    if (dic_q):
                        sql +="forward_question=\"" + str(dic_q).replace("\"","\\\"") + "\","
                    dic_a = self.forward_get(list_p=list_a)
                    if (dic_a):
                        sql +="forward_answer=\"" + str(dic_a).replace("\"","\\\"") + "\","

                sql = sql[:-1]
                sql = sql_head + sql
                sql += " where id=" + str(row[0])
                update_if = conn_data.write_sql(sql)
                if (update_if):
                    k += 1
                
                #print ("问题：",list_q,"答案：",list_a,"精选答案：",list_al) # 调试用
                
                # 词向量索引总表构造及相关td_idf基础值存储
                if (tf_idf_if_p == 1):
                
                    self.vec_make(table_name_p="index_question_gossip",dic_p=dic_q,conn_data=conn_data)
                    self.vec_make(table_name_p="index_answer_gossip",dic_p=dic_a,conn_data=conn_data)
                
                m +=1
                print(m) #显示具体计数
                
                #return txt # 只循环一次中断调试用
                
            j += 1
            
        txt += "执行完毕，共耗时" +  str(round(time_cost(time_start),2)) + "秒,操作" + str(m) + " 次，成功" + str(k)+ "次。"
        return txt
        
    # 闲聊语料库的索引构造
    def qa_gossip_index(self,t_name_p="qa_gossip",conn_basedate="",conn_index="",conn_way="",rankway_p=0,mark_p="v2",numb_for_p=0,renew_if_p=1):
        
        txt = "" # 结果文本
        sql = "" # sql语句
        time_start = datetime.datetime.now() #启动时间
        dic_q = {} # 问题正排字典
        dic_a = {} # 答案正排字典
        rank_t = 0
        # 构造单字校验字典
        dic_oneword = {} # 单字实义词字典
        dic_unitword = {} # 单字量词字典
        numb_file_all = 0 # 语料的总文件数
        
        # 获得语料总文件数
        
        sql = " select count(*) from " + t_name_p 
        res,rows = conn_basedate.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_file_all = rows[0][0]
        
        #导入特殊字典 用于字典容量不大的情况
        
        #try:
            #dic_oneword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_oneword.txt",split_p="\n")
        #except:
            #pass
            
        #try:
            #dic_unitword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_unitword.txt",split_p="\n")
        #except:
            #pass
            
        print ("mark_p=",mark_p,"numb_for_p=",numb_for_p,"renew_if_p=",renew_if_p,"rankway_p=",rankway_p) # 调试用
        
        # 游标清零处理
        if (renew_if_p == 1):
            sql = "update " + t_name_p + " set " + mark_p + "=0"
            update_if = conn_basedate.write_sql(sql) # 游标清零
        

        # 获得待处理记录总数
        sql = " select count(*) from " + t_name_p + " where " + mark_p + "=0"
        res,rows = conn_basedate.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_all = rows[0][0]
            print ("待处理数据库记录总数：",numb_all)
            if (numb_all == 0):
                return "全部数据处理完毕或数据库读取错误"
        
        if (numb_all/numb_for_p > 0 and numb_all/numb_for_p <= 1):
            numb_div = 1
            numb_for_p = 1
        else:
            numb_div = int(round(numb_all/numb_for_p))
         
        j = 1
        m = 0
        while (j <= numb_for_p):
            
            print("第 ",j," 次分块处理") #调试用
            sql = "select id,forward_question,forward_answer from " + t_name_p + " where " + mark_p + "=0 limit " + str(numb_div)
            res_t,rows_t = conn_basedate.read_sql(sql)

            if (res_t < 1):
                break
            for row in rows_t:
                
                # 不管成功失败都打上访问标记
                sql = "update " + t_name_p + " set " + mark_p + "=1 where id=" + str(row[0])
                update_if = conn_basedate.write_sql(sql)
                
                # 引入正排字典
                
                try:
                    dic_q = eval(row[1]) # 问题正排字典
                except:
                    pass
                try:
                    dic_a = eval(row[2]) # 答案正排字典
                except:
                    pass
                
                #print (dic_q,dic_a,dic_al) # 调试用
                # 对问题进行索引

                self.index_make(dic_p=dic_q,conn_basedate=conn_basedate,conn_index=conn_index,name_p="question_gossip",dic_oneword=dic_oneword,dic_unitword=dic_unitword,numb_file_all=numb_file_all,rankway_p=rankway_p,pid=row[0])
                self.index_make(dic_p=dic_q,conn_basedate=conn_basedate,conn_index=conn_index,name_p="answer_gossip",dic_oneword=dic_oneword,dic_unitword=dic_unitword,numb_file_all=numb_file_all,rankway_p=rankway_p,pid=row[0])
                
                m +=1
                print(m) #显示具体计数
                
                #return txt # 只循环一次中断调试用
                
            j += 1
            
        txt += "执行完毕，共耗时" +  str(round(time_cost(time_start),2)) + "秒,操作" + str(m) + " 次"
        return txt
        
    # 知识型主问答库的索引构造
    def qa_index(self,t_name_p="qa",conn_basedate="",conn_index="",conn_way="",rankway_p=0,mark_p="v2",numb_for_p=0,renew_if_p=1):
        
        txt = "" # 结果文本
        sql = "" # sql语句
        time_start = datetime.datetime.now() #启动时间
        dic_q = {} # 问题正排字典
        dic_a = {} # 答案正排字典
        dic_al = {} # 精选答案正排字典
        rank_t = 0
        # 构造单字校验字典
        dic_oneword = {} # 单字实义词字典
        dic_unitword = {} # 单字量词字典
        numb_file_all = 0 # 语料的总文件数
        
        # 获得语料总文件数
        
        sql = " select count(*) from " + t_name_p 
        res,rows = conn_basedate.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_file_all = rows[0][0]
        
        #导入特殊字典 用于字典容量不大的情况
        
        try:
            dic_oneword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_oneword.txt",split_p="\n")
        except:
            pass
            
        try:
            dic_unitword = inc_dic.dic_make_one(path_p=config.dic_config["path_dic"] + "dic_unitword.txt",split_p="\n")
        except:
            pass
            
        print ("mark_p=",mark_p,"numb_for_p=",numb_for_p,"renew_if_p=",renew_if_p,"rankway_p=",rankway_p) # 调试用
        
        # 游标清零处理
        if (renew_if_p == 1):
            sql = "update " + t_name_p + " set " + mark_p + "=0"
            update_if = conn_basedate.write_sql(sql) # 游标清零
        

        # 获得待处理记录总数
        sql = " select count(*) from " + t_name_p + " where " + mark_p + "=0"
        res,rows = conn_basedate.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_all = rows[0][0]
            print ("待处理数据库记录总数：",numb_all)
            if (numb_all == 0):
                return "全部数据处理完毕或数据库读取错误"
        
        if (numb_all/numb_for_p > 0 and numb_all/numb_for_p <= 1):
            numb_div = 1
            numb_for_p = 1
        else:
            numb_div = int(round(numb_all/numb_for_p))
         
        j = 1
        m = 0
        while (j <= numb_for_p):
            
            print("第 ",j," 次分块处理") #调试用
            sql = "select id,forward_question,forward_answer,forward_answer_last from " + t_name_p + " where " + mark_p + "=0 limit " + str(numb_div)
            res_t,rows_t = conn_basedate.read_sql(sql)

            if (res_t < 1):
                break
            for row in rows_t:
                
                # 不管成功失败都打上访问标记
                sql = "update " + t_name_p + " set " + mark_p + "=1 where id=" + str(row[0])
                update_if = conn_basedate.write_sql(sql)
                
                # 引入正排字典
                
                try:
                    dic_q = eval(row[1]) # 问题正排字典
                except:
                    pass
                try:
                    dic_a = eval(row[2]) # 答案正排字典
                except:
                    pass
                try:
                    dic_al = eval(row[3]) # 精选问题答案字典
                except:
                    pass
                
                #print (dic_q,dic_a,dic_al) # 调试用
                # 对问题进行索引

                self.index_make(dic_p=dic_q,conn_basedate=conn_basedate,conn_index=conn_index,name_p="question",dic_oneword=dic_oneword,dic_unitword=dic_unitword,numb_file_all=numb_file_all,rankway_p=rankway_p,pid=row[0])
                self.index_make(dic_p=dic_q,conn_basedate=conn_basedate,conn_index=conn_index,name_p="answer",dic_oneword=dic_oneword,dic_unitword=dic_unitword,numb_file_all=numb_file_all,rankway_p=rankway_p,pid=row[0])
                self.index_make(dic_p=dic_q,conn_basedate=conn_basedate,conn_index=conn_index,name_p="answer_last",dic_oneword=dic_oneword,dic_unitword=dic_unitword,numb_file_all=numb_file_all,rankway_p=rankway_p,pid=row[0])
                
                m +=1
                print(m) #显示具体计数
                
                #return txt # 只循环一次中断调试用
                
            j += 1
            
        txt += "执行完毕，共耗时" +  str(round(time_cost(time_start),2)) + "秒,操作" + str(m) + " 次"
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