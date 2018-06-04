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

#-----系统必备模块引用-----

#-----通用功能模块引用区-----

from diy.inc_conn import * #自定义数据库功能模块

#-----特定功能模块引用区-----

import config #系统配置参数

#-----全局变量赋初值-----

# 内嵌执行主函数
def run_it(args_p):

    str_xml = ""
    str_add = ""
    kwd = ""
    
    #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
    #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
    rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
    #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
    
    if "kwd" in args_p:
    
        kwd = args_p["kwd"][0]
        kwd = kwd.decode(encoding='utf-8')
        
        arr_1 = kwd.split(" ")

        if (len(arr_1)>1):
        
            kwd = arr_1[-1]

            for i in range(len(arr_1)-1):
                str_add += arr_1[i] + " "
            str_add = str_add.replace(" ","")
    
    if "way" in args_p:
        way_p = args_p["way"][0]
        way_p = way_p.decode(encoding='utf-8')
    else:
        way_p = "default"
    
    # 零输入则返回
    if (kwd == ""):
        return ""
        
    str_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    str_xml += "<root>\n"
    
    if (way_p == "default"):
        #1 问题集匹配查询
        sql = "select keyword from index_question where keyword like '%" + kwd + "%' order by idf desc limit 10"
        res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res > 0):
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            k = 1
            for row in rows:
                if (row[0] != "numb_key_ldae" and row[0] != kwd):
                    str_xml += "<message id=\"" + str(k) + "\">\n"
                    str_xml += "    <text>" + str_add + row[0] + "</text>\n" 
                    str_xml += "</message>\n"
                k += 1
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            str_xml += "</root>\n"
        
            return str_xml
        
        else:
        
            # 答案集匹配查询
            sql = "select keyword from index_answer where keyword like '%" + kwd + "%' order by idf desc limit 10"
            res, rows = rs_basedata_mysql.read_sql(sql)
        
            if (res > 0):
                str_xml += "<message id=\"0\">\n"
                str_xml += "<text>__________</text>\n" 
                str_xml += "</message>\n"
                k = 1
                for row in rows:
                    if (row[0] != "numb_key_ldae" and row[0] != kwd):
                        str_xml += "<message id=\"" + str(k) + "\">\n"
                        str_xml += "    <text>" + str_add  + row[0] + "</text>\n" 
                        str_xml += "</message>\n"
                    k += 1
            
                str_xml += "<message id=\"0\">\n"
                str_xml += "<text>__________</text>\n" 
                str_xml += "</message>\n"
                str_xml += "</root>\n"
        
            else:
        
                str_xml += "<message id=\"" + str(k) + "\">\n"
                str_xml += "<text>n/a</text>\n" 
                str_xml += "</message>\n"
                str_xml += "</root>\n"
                
    # 预测提示
    if (way_p == "devine"):
        #1 问题集匹配查询
        sql = "select keyword from devine_alive where keyword like '%" + kwd + "%' order by power desc limit 10"
        res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res > 0):
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            k = 1
            for row in rows:
                if (row[0] != "numb_key_ldae" and row[0] != kwd):
                    str_xml += "<message id=\"" + str(k) + "\">\n"
                    str_xml += "    <text>" + str_add + row[0] + "</text>\n" 
                    str_xml += "</message>\n"
                k += 1
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            str_xml += "</root>\n"
        
            return str_xml
            
    # 花费提示
    if (way_p == "cost"):
        #1 问题集匹配查询
        sql_1 = "select keyword from devine_cost_ill where keyword like '%" + kwd + "%' "
        sql_2 = "select keyword from devine_cost_drug where keyword like '%" + kwd + "%' "
        sql = sql_1 + " UNION " + sql_2 + " limit 10" 
        res, rows = rs_basedata_mysql.read_sql(sql)
        print (sql) # 调试用
        if (res > 0):
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            k = 1
            for row in rows:
                if (row[0] != "numb_key_ldae" and row[0] != kwd):
                    str_xml += "<message id=\"" + str(k) + "\">\n"
                    str_xml += "    <text>" + str_add + row[0] + "</text>\n" 
                    str_xml += "</message>\n"
                k += 1
            str_xml += "<message id=\"0\">\n"
            str_xml += "<text>__________</text>\n" 
            str_xml += "</message>\n"
            str_xml += "</root>\n"
        
            return str_xml
    
    rs_basedata_mysql.close_cur() #关闭数据游标
    rs_basedata_mysql.close() #关闭数据连接
    
    return str_xml

def main():

    print("") # 因为寄生类模块只允许import调用，为防止代码泄露，只输出空白。
    
if __name__ == '__main__':
    
    main()

    #rs_index.close() #关闭方法主要参数mysql数据库