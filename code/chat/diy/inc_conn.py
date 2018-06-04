#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"腾辉",
"2":"吉更"
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys
import os
#-----系统外部需安装库模块引用-----
import sqlite3
import pymysql
#-----DIY自定义库模块引用-----
sys.path.append("..")
import config #系统配置参数
#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区
# sqlite3数据库对象
class Conn_sqlite3():

    def __init__(self,path_data,memory_if=0,cached_statements=100,timeout=5):
        
        # 如果数据库路径为空，则赋值为默认路径
        if (path_data == ""):
            self.path_data =  config.path_main + "data\\sqlite\\main_sqlite.db"
        else:
            self.path_data = path_data
            
        try:
        
            if (memory_if == 0):
                self.conn = sqlite3.connect(self.path_data,cached_statements,timeout)
                
                #print("sqllite文件型调用:[{}]".format(self.path_data)) # 调试用
            else:
                self.conn = sqlite3.connect(':memory:')
                
                #print("sqlite内存型调用:[:memory:]") # 调试用
        
        except Exception as e:
        
            print('事务处理失败', e)

    # 全表读数据方法
    def read_sql(self, sql):
        res = 0
        data = ()
        self.cur = self.conn.cursor()
        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
            res = len(data)
        except:
            pass
        self.cur.close()
        return res, data
        
    # 数据写操作方法
    def write_sql(self, sql, *args):
        res = 0
        self.cur = self.conn.cursor()
        try:
        
            self.cur.execute(sql, *args)
            res = self.cur.rowcount
            
        except:
        
            res = -1
        self.cur.close()
        return res
        
        
    #利用脚本批量操作的方法
    def script(self,script_p):
        
        result = 1
        self.cur = self.conn.cursor()
        try:
            self.cur.executescript(script_p)
        except:
            result =0
        self.cur.close()
        return result
    
    # 传递连接对象
    def get_conn(self):
        return self.conn
        
    # 关闭游标
    def close_cur(self):
        self.cur.close()
    
    # 关闭连接对象
    def close(self):
        self.conn.commit()
        self.conn.close()

# mysql数据库对象
class Conn_mysql():

    def __init__(self, host='localhost', user='root', passwd='', db='', port=3306):
        try:
            self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset="utf8")
        except Exception as e:
            print('事务处理失败', e)
    
    # 全表读数据方法
    def read_sql(self, sql):
        res = 0
        data = ()
        self.cur = self.conn.cursor()
        try:
            res = self.cur.execute(sql)
            data = self.cur.fetchall()
        except:
            pass
        self.cur.close()
        return res, data
        
    # 分页读数据方法
    def read_sql_page(self, sql, values_p):
        res = 0
        data = ()
        self.cur = self.conn.cursor()
        try:
            res = self.cur.execute(sql)
            if (values_p < res):
                self.cur.scroll(values_p,'relative')
            data = self.cur.fetchall()
        except:
            pass
        self.cur.close()
        return res, data
    
    # 数据写操作方法
    def write_sql(self, sql, *args):
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(sql, *args)
            self.conn.commit()
            self.cur.close()
            return True
        except:
            return False
            pass
        
    # 传递连接对象
    def get_conn(self):
        return self.conn
    
    # 关闭游标
    def close_cur(self):
        self.cur.close()
    
    # 关闭连接对象
    def close(self):
        self.conn.commit()
        self.conn.close()
        
#--------- 内部模块处理<<结束>> ---------#

# 默认数据库全连通示意

#rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
#rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
#rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
#rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例


#---------- 主过程<<开始>> -----------#
def main():

    print ("")  # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()
#---------- 主过程<<结束>> -----------#