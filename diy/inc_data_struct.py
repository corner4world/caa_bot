#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"吉更",
"2":"iron",
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

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

sys.path.append("..")

import config #系统配置参数

# ---本模块内部类或函数定义区

# 基础清理对象
class Struct_base(object):
    def __init__(self):
        pass
        
# 数据库清理对象
class Struct_main(Struct_base):
    
    # 默认综合处理函数
    def run_it(self,action_p="",tid_p=0):
        pass
        
    # 对ID为X的子任务执行结构化数据到知识切片页的清理操作 ID为0则执行全部已经结构化的子任务
    def struct_to_page(self,tid_p=0,res_if=0):
    
        data_name = "ldae_basedata_" + config.dic_config["name_mysql_after"]
        txt = ""
        dic_child = {}
        if (tid_p == 0):
        
            #获得结构化子表名
            sql="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '" + data_name + "' and TABLE_NAME like 'z_struct_%' "
            res_stru, rows_stru = rs_basedata_mysql.read_sql(sql)
            if (res_stru < 1):
                return ("结构化子表不存在或数据库读取错误")
            else:
                for t_name in rows_stru:
                    
                    #建立子表字典
                    name_t = t_name[0].split("_")[2]
                    if (not name_t in dic_child):
                        dic_child[name_t] = "0"
                        
                    #获得结构化表基础字段 不含自增ID
                    sql = "select COLUMN_NAME from INFORMATION_SCHEMA.Columns where table_name='" + t_name[0] + "' and table_schema='" + data_name + "'"
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if (res < 1):
                        print ("结构化子表 " + t_name + " 不存在或结构读取错误")
                    else:
                        row_str = ""
                        str_t = ""
                        for row in rows:
                            str_t = row[0]
                            str_t = str_t.strip()
                            if (str_t != "id" and str_t != ""):
                                row_str += str_t + ","
                        row_str = row_str[0:-1]
                        sql = "INSERT INTO struct(" + row_str + ") SELECT " + row_str + " FROM " + t_name[0]
                        #print (sql) #调试用
                        insert_if = rs_basedata_mysql.write_sql(sql) # 转存至结构化总表 便于集中处理
        
        if (tid_p > 0):
        
            sql = "select seed_name from task where id=" + str(tid_p)
            res, rows = rs_way_mysql.read_sql(sql)
            if (res < 1):
                return "子任务不存在此任务或数据库读取错误"
            else:
                t_name_p ="z_struct_" + hash_make(rows[0][0])
                
             #获得结构化表基础字段 不含自增ID
            sql = "select COLUMN_NAME from INFORMATION_SCHEMA.Columns where table_name='" + t_name_p + "' and table_schema='" + data_name + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res < 1):
                print ("结构化子表 " + t_name_p + " 不存在或结构读取错误")
            else:
                row_str = ""
                str_t = ""
                for row in rows:
                    str_t = row[0]
                    str_t = str_t.strip()
                    if (str_t != "id" and str_t != ""):
                        row_str += str_t + ","
                row_str = row_str[0:-1]
                sql = "INSERT INTO struct(" + row_str + ") SELECT " + row_str + " FROM " + t_name_p
                #print (sql) #调试用
                #insert_if = rs_basedata_mysql.write_sql(sql) # 转存至结构化总表 便于集中处理
            
        #结构化主表去重
        if (tid_p == 0):
            print(self.nosame_stru(row_list_p=row_str))
        if (tid_p > 0):
            print(self.nosame_stru(t_name_p=t_name_p,row_list_p=row_str))

        #装载到主数据切片表
        print (self.page_load())
        
        if (res_if == 1):
            #简单结果处理
            pass
        
        return txt
        
    #结构化表去重
    def nosame_stru(self,t_name_p="struct",row_list_p="*",conn_p=rs_basedata_mysql):
        
        txt = ""
        
        print ("结构化去重......\n")
        
        table_name = code_char_rand()#生成随机表名
        
        sql = "CREATE TABLE stru_" + table_name + " LIKE " + t_name_p
        #print(sql) #调试用

        create_table_if = conn_p.write_sql(sql)
            
        sql ="INSERT INTO stru_" + table_name + "(" + row_list_p + ")"
        sql += "SELECT " + row_list_p + " from " + t_name_p + " GROUP BY url_hash order by id asc"
        #print(sql) #调试用
        insert_into_if = conn_p.write_sql(sql)
            
        sql = "drop table " + t_name_p
        #print(sql) #调试用
        drop_if = conn_p.write_sql(sql)
            
        sql = "alter table stru_" + table_name + " rename " + t_name_p
        #print(sql) #调试用
        alter_if = conn_p.write_sql(sql)
        
        return txt
    
    # 载入到主数据切片表
    def page_load(self,t_name_p="struct"):
        
        txt = ""
        dic_row = {}
        row_str = ""
        data_name = "ldae_basedata_" + config.dic_config["name_mysql_after"]
        sql = "select column_name from INFORMATION_SCHEMA.Columns where table_name='" + t_name_p + "' and table_schema='" + data_name + "'"
        res_stru,rows_stru = rs_basedata_mysql.read_sql(sql)
        if (res_stru < 1):
            return "结构化表 " + t_name_p + "字段为空或数据库读取错误"
        else:
            i = 0
            for row in rows_stru:
                dic_row[row[0]] = i
                i +=1
        sql = "select dim_name_db from struct_dim order by power desc"
        res,rows = rs_way_mysql.read_sql(sql)
        if (res < 1):
            return "结构化维度表为空或读取错误"
        else:
            for row in rows:
                if (row[0] in dic_row):
                    row_str += row[0] + ","
            row_str = row_str[0:-1]
        
        sql_head = "insert into page(content,seed_name,seed_type,url_hash,label,title,digest)"
        sql_data = " select concat_ws(','," + row_str + ") as content ,seed_name,seed_type,url_hash,label,position_title,job_description from " + t_name_p + " "
        sql = sql_head + sql_data
        insert_if = rs_basedata_mysql.write_sql(sql)
        #print (sql) #调试用
        txt += "数据切片总表装载完毕"
        return txt
    
    #职业清理
    def job_clear(self,char_p="utf-8",path_p="../data/clear/job.csv",key_p=""):
        
        not_in_list = " \"'.|·=×§№☆★○●◎◇◆□〓↓↑←→↗↖↘↙※▲▼△■¤⊙【】〖〗［］｛｝▓‖╳⊿◣◢◥@!&^（〔［｛《【〖〈）〕］｝》】〗〉'『'』。？！，；、；…_：-—－—－?'()+-*&^#@!~`{}[]\:;'<>,/＜≈≡≠=≤≥<>≮≯∷±+-×÷/∫∮∝∞∧∨∑∏∪∩∈∵∴⊥‖∠⌒⊙≌∽√︴﹏﹋﹌︵︶︹︺【】〖〗＠﹕﹗/\_<>`,·。≈{}~～()_-『』√$@*&#※卐々∞Ψ∪∩∈∏の℡ぁ§∮〝〞ミ灬ξ№∑⌒ξζω＊????ㄨ≮≯＋－×÷﹢﹣±／＝∫∮∝∞∧∨∑∏∥∠≌∽≦≧≒﹤﹥じ☆↑↓⊙●❤★☆■♀『』Ψ※→№←㊣∑⌒〖〗＠ξζω□∮〓※∴ぷ∏卐【】△√∩¤々♀♂∞①ㄨ≡↘↙┗┛↑↓←→↖↗↙↘㊣◎○●⊕⊙○●△▲☆★◇◆□■▽▼§￥〒￠￡※♀♂“”"
        text = ""
        txt = ""
        t = open(path_p,"r",encoding=char_p)
        text = t.read()
        t.close()

        for x in not_in_list:
            text = text.replace(x,"\n")
        
        
        #关键词校验
        list_p = []
        if (not key_p == ""):
            arr_t = text.split("\n")
            
            for x in arr_t:
                if (key_p in x):
                    if (not x in list_p):
                        list_p.append(x)
        text = ""
        for x in list_p:
            if (x != ""):
                text += x + "\n"
        clear_last = ["高薪","诚聘","急聘","急招","招聘","直招","底薪","诚招","年终奖","双休","五险","一金","聘","x0a"]
        for x in clear_last:
            text = text.replace(x,"")
        
        text = re.sub("\d+[K|k]","",text)
        
        # 回写结果文件
        path_p = "../data/clear/job_result.csv"
        f = open(path_p,'w',encoding=char_p)
        f.write(text)
        f.close()
        
        return txt

def run_it():

    print("") # 调试用

#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    #1 过程一
    run_it()
    #2 过程二
    #3 过程三
    rs_sqlite_file.close()
    rs_way_mysql.close()
    rs_basedata_mysql.close()
    rs_index_mysql.close()
    
if __name__ == '__main__':
    main()
    rs_sqlite_file.close()
    rs_way_mysql.close()
    rs_basedata_mysql.close()
    rs_index_mysql.close()
    
#---------- 主过程<<结束>> -----------#