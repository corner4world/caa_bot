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

class Hot_base(object):

    def __init__(self):
        pass
        
class Hot_main(Hot_base):

    def hot_get(self,page_p=1,test_if=0):
        
        list_t1 = []
        list_t2 = []
        list_t3 = []
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        txt = """
        <style type="text/css">
        A {text-decoration: none;color: #666666; }
        A:hover {text-decoration: underline;color: #2b8bd5;}
        </style> 
        """
        txt += """
                   <script  language="javascript"> 
                   var url_p = window.location.href;
                   var path_p = window.location.pathname;
                   var port_p = window.location.port;
                """
        txt += "url_p = url_p.replace(\"?page=" + str(page_p) +  "\",\"\");"
        txt += """
                   url_p = url_p.replace(path_p,"");
                   url_p = url_p.replace(port_p,"");
                   url_p = url_p + "8001/api?action=show_qa"
                   </script>
        """
        id_t = 0 
        
        page_limit = int(config.dic_config["numb_limit_hot"])
        
        sql = "select question,id,rank from qa order by rank desc "
        sql += "limit " + str(page_limit*(page_p+1))
        
        site_p =  page_limit * (page_p-1)
        #print(page_p,site_p,sql) # 调试用
        res, rows = rs_basedata_mysql.read_sql_page(sql,site_p)
        
        if (res < 1):
            return "<center>所需数据已删除或数据库读取错误</center>"
        #print (rows) # 调试用
        
        # 转化为列表
        i = 0
        for row in rows:
            list_t1.append(rows[i][0])
            i += 1
        # 重复再标注
        i = 0
        for x in list_t1: 
            if not x in list_t2:
                list_t2.append(x)
                list_t3.append(i)
            i += 1
        
        i = 0
        j = 0
        for row in rows:
        
            # 只显示去重选项
            if (not i in list_t3):
                i += 1
                continue
            else:
                j += 1
                i += 1
                
            if (j > page_limit):
                break
            
            id_t = row[1]
            txt += "<div style=\"width:508px;height:50px;align:left;\"><li>" 
            txt += "<script  language=\"javascript\"> "
            txt += "document.write('<a href=\"' + url_p + '&id=" + str(id_t) + "\" target=\"_blank\">" + row[0] + "</a>')" 
            txt += "</script>"
            if(test_if==1):
                txt += " rank:" + str(row[2])
            txt += "</li></div>"
            
        
        #加入翻页
        txt += "<center><div>"
        if (page_p > 1):
            txt += "<a href=\"hot?page=" + str(page_p - 1) + "\" ><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">上一页</font></a> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp"
        if (res > i-1):
            txt += "<a href=\"hot?page=" + str(page_p + 1) + "\" ><font style=\"font-size:13px;font-family: 微软雅黑;\" color=\"#666666\">下一页</font></a>"
        txt += "</div></center>"
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
# 外调模块引擎驱动函数
def run_it(page_p=1,test_if=0):
    txt = ""
    hot_main = Hot_main() # 主对象实例化
    txt = hot_main.hot_get(page_p=page_p,test_if=test_if)
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