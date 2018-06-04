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
import pymysql
#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----
sys.path.append("..")
import config #系统配置参数
import csv #CSV组件
import diy.inc_sys as inc_sys #自定义基础组件

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区

#继承字符扩展对象
class Csv_base(inc_sys.String_what):


    # CSV 文件读取
    def read_csv_file(self,file_path='../data/test/one.csv'):
        list = []
        #打开文件，用with打开可以不用去特意关闭file了，python3不支持file()打开文件，只能用open()
        with open(file_path,"r",encoding="utf-8") as csvfile:
            #读取csv文件，返回的是迭代类型
            read = csv.reader(csvfile)
            for item in read:
                list.append(item)
        return list

    # CSV 文件读取
    def read_csv_file_line(self,file_path='../data/test/one.csv',line=0):
        #打开文件，用with打开可以不用去特意关闭file了，python3不支持file()打开文件，只能用open()
        csv_list = []
        with open(file_path,"r",encoding="utf-8") as csvfile:
            #读取csv文件，返回的是迭代类型
            read = csv.reader(csvfile)
            for i,rows in enumerate(read):
                
                if (i > line):
                    break
                else:
                    csv_list.append(rows)
                    
        return csv_list

    # 创建表
    # 前提条件 文件第一行必须为标题行
    # 如果头不是标题行在做其他处理
    def create_table(self,data_stru_p,table_name,mysql_conn):
        
        data_title = data_stru_p[0]
        data_row = data_stru_p[1]

        sql = 'create table if not exists '+table_name +"("
        for i in range(len(data_title)):
            
            sql += data_title[i] 
            
            for j in range(len(data_row)):
                str_t = data_row[j]
                if self.is_num_by_except(str_t):
                
                    if isinstance(str_t, float):
                        type_is = "float"
                    else:
                        type_is = "bigint"
                        
                    sql += " " + type_is + ","
                    
                    break
                    
                else:
                    
                    type_is = "text"    
                    sql += " " + type_is + ","
                    
                    break
                    
        sql = sql[0:len(sql)-1]
        sql += ")"
        print (sql) #调试用
        mysql_conn.write_sql(sql=sql)


    # 数据录入
    def load_data_from_csv_into_mysql(self,table_name,mysql_conn,file_path ='../data/test/one.csv',t="','",e="'\"'",l="'\\r\\n'"):
        sql = "LOAD DATA INFILE '" + file_path + "'"
        sql += " INTO TABLE " + table_name 
        sql += " character set utf8 " 
        sql += " FIELDS TERMINATED BY " + t
        sql += " OPTIONALLY ENCLOSED BY " + e + " escaped by " + e
        sql += " LINES TERMINATED BY " + l 
        sql += " IGNORE 1 LINES"
        try:
            print (sql) #调试用
            mysql_conn.write_sql(sql=sql)
            return True
        except:
            return False
            
    # 数据录入
    def load_data_from_mysql_into_csv(self,sql_p,mysql_conn,file_path ='../data/test/one.csv',t="','",e="'\"'",l="'\\r\\n'"):
        
        sql = sql_p
        sql += " into outfile '" + file_path + "'"
        sql += " character set utf8 "
        sql += " FIELDS TERMINATED BY " + t
        sql += " OPTIONALLY ENCLOSED BY " + e + " escaped by " + e
        sql += " LINES TERMINATED BY " + l 
        try:
            print (sql) #调试用
            mysql_conn.write_sql(sql=sql)
            return True
        except:
            return False



#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    print ("") #调试用
    
if __name__ == '__main__':
    
    main()
    
#---------- 主过程<<结束>> -----------#