#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"一世纪末",
"2":"吉更",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys
import csv
import datetime # 日期模块

#-----系统外部需安装库模块引用-----
import jieba

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
from diy.inc_conn import * #自定义数据库功能模块
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件

# ---全局变量处理
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
import jieba.posseg as pseg #引入词性标注模式
user_dic_path = config.dic_config["path_jieba_dic"]
jieba.load_userdict(user_dic_path)# 导入专用字典

        
# 词的基础处理
class Kg(object):

    # 近义词相关词处理
    def kg_get(self,table_name="personas",str_t="",model_p="ne"):
        
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

        if (str_t):
        
            sql_add = ""
            ill_is = ""
            ill_where = ""
            ill_what = ""
            
            # 微服务请求疾病实体
            url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + str_t
            dic_ne = inc_crawler_fast.dic_get(url_p)
            
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
            
            # 微服务请求 主题词
            model_p = "mk"
            url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + str_t
            dic_mk = inc_crawler_fast.dic_get(url_p)
            
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
        
        return txt

# 主执行调用入口函数
def run_it(q_p="",action_p="kg_get"):

    txt = ""
    
    if (q_p):
        pass
    else:
        return txt
        
    if (action_p == "kg_get"):
        
        txt = "hello world!"
        kg = Kg()
        txt = kg.kg_get(str_t=q_p)
        
        return txt
    
    return txt
    
if __name__ == '__main__':

    numb_r = 99999
    # 循环输入
    i = 1
    while (i<=numb_r):
    
        key_p = input("请输入句子,exit退出 >>> ")
        if (key_p == "exit"):
            break
            
        result = run_it(key_p) #测试输入
        
        if (result):
            print (result) #调试用
        else:
            print("处理失败>>>",key_p)
    i += 1
    
    
    print ("") # 防止代码泄漏只输出空字符 
    