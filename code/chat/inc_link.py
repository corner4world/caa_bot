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

#-----系统外部需安装库模块引用-----

#-----DIY自定义库模块引用-----

from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
from diy.inc_result import * #自定义特定功能模块
from diy.inc_hash import hash_make #MD5函数
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
import config #系统配置参数

sys.path.append("..")

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

class Link_base(object):

    def __init__(self):
        pass
        
class Link_main(Link_base):

    def link_get(self,page_p=1):
        
        txt = """
        <style type="text/css">
        A {text-decoration: none;color: #666666; }
        A:hover {text-decoration: underline;color: #2b8bd5;}
        </style> 
        """ 
        page_limit = 10
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        #rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        sql = "select seed_type from seed_type where pass_if=1 order by power desc "
        print(sql) # 调试用
        res, rows = rs_way_mysql.read_sql(sql)
        if (res < 1):
            return "<center>所需数据已删除或数据库读取错误</center>"
        #print (rows) # 调试用
        txt += "<div style=\"width:338px;\" position:left;>"
        
        i = 1
        for row in rows:
            if (i > page_limit):
                break
            
            sql = "select seed_name,seed_url from seed "
            sql += "where seed_type='" + row[0] + "' and pass_if =1 "
            sql += "order by rank desc"
            res_t, rows_t = rs_way_mysql.read_sql(sql)
            
            
            if (res_t > 0):
                txt += "<p><font style=\"font-family: 微软雅黑;\">" + row[0] + "</font><br>"
            else:
                continue
            
            for row_t in rows_t:
                txt += " &nbsp&nbsp&nbsp<a href=\"" + str(row_t[1]) + "\" target=\"_blank\"><font style=\"font-family: 微软雅黑;\">" + row_t[0] + "</font></a>\n"
            
            txt += "</p>\n"
            i += 1
            
        txt += "</div>"
        
        rs_way_mysql.close_cur() #关闭数据游标
        rs_way_mysql.close() #关闭数据连接
        
        return txt
        
# 外调模块引擎驱动函数
def run_it(page_p=1):
    txt = ""
    link_main = Link_main() # 主对象实例化
    txt = link_main.link_get(page_p=page_p)
    return txt
    
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