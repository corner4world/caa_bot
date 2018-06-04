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
class Clear_base(object):

    def __init__(self):
    
        pass
        
# 常规清理对象
class Clear_txt(Clear_base):

    # 清理html标记码
    def html_mark_clear(self,txt_p):
    
        from bs4 import BeautifulSoup as bs_4
        txt_p = bs_4(txt_p).get_text()
        
        return txt_p
    
    # 全角转半角
    def strQ2B(self,ustring):
    
        rstring = ""
        
        for uchar in ustring:
            inside_code=ord(uchar)
            if inside_code == 12288:                              #全角空格直接转换            
                inside_code = 32 
            elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
                inside_code -= 65248

            rstring += chr(inside_code)
            
        return rstring
    
    # 半角转全角
    def strB2Q(self,ustring):
    
        rstring = ""
        
        for uchar in ustring:
            inside_code=ord(uchar)
            if inside_code == 32:                                 #半角空格直接转化                  
                inside_code = 12288
            elif inside_code >= 32 and inside_code <= 126:        #半角字符（除空格）根据关系转化
                inside_code += 65248

            rstring += chr(inside_code)
            
        return rstring
        
    # 特定半角标点转全角
    def banjiao2quanjiao(self,txt_p="",dic_p={",":"，","?":"？","!":"！"}):
        for x in dic_p:
            txt_p = txt_p.replace(x,dic_p[x])
        return txt_p
    
    # html码形式数据清理为纯文本
    def html_code_clear(self,conn_p="",mark_p="v5",numb_for_p=0,renew_if_p=1):
        
        txt = ""
        time_start = datetime.datetime.now()
        numb_all = 0 # 待处理记录总数
        numb_div = 0 # 每一块处理条数
        txt_q = "" # 问题临时文本变量
        txt_a = "" # 答案临时文本变量
        list_bug = ["。","？","！","；"]
        
        print ("mark_p=",mark_p,"numb_for_p=",numb_for_p,"renew_if_p=",renew_if_p) # 调试用
        
        # 游标清零处理
        if (renew_if_p == 1):
            sql = "update qa set " + mark_p + "=0"
            update_if = conn_p.write_sql(sql) # 游标清零
            print ("游标清零处理结果：",update_if)
            
        # 获得待处理记录总数
        sql = " select count(*) from qa where " + mark_p + "=0"
        res,rows = conn_p.read_sql(sql)
        
        if (res < 1):
            return "待处理记录为空或数据库读取错误"
        else:
            numb_all = rows[0][0]
            print ("待处理数据库记录总数：",numb_all)
            if (numb_all == 0):
                return "全部数据处理完毕或数据库读取错误"
        
        # 考虑内存限制，递归分块处理，分块数即numb_for_p 
        if (numb_for_p > 0):

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
                sql = "select id,question,answer from qa where " + mark_p + "=0 limit " + str(numb_div)
                #print (sql)
                res_t,rows_t = conn_p.read_sql(sql)
                if (res_t < 1):
                    break
                for row in rows_t:
                
                    txt_q = row[1]
                    txt_a = row[2]
                    
                    sql = "update qa set " + mark_p + "=1 where id=" + str(row[0])
                    update_if = conn_p.write_sql(sql)
                    txt_q = self.html_mark_clear(txt_p=txt_q)
                    txt_q = self.banjiao2quanjiao(txt_p=txt_q,dic_p={",":"，","?":"？","!":"！","'":"\'","\"":"\\\""})
                    
                    txt_a = self.html_mark_clear(txt_p=txt_a)
                    txt_a = self.banjiao2quanjiao(txt_p=txt_a,dic_p={",":"，","?":"？","!":"！","'":"\'","\"":"\\\""})
                    # 结尾标点的补丁

                    if (txt_a[-1:] in list_bug):
                        pass
                    else:
                        txt_a += "。"
                        
                    #try:
                        #print ("id：",row[0],"问题：",txt_q,"答案：",txt_a) # 调试用
                    #except:
                        #pass
                        
                    sql = "update qa set question=\"" + txt_q +  "\",answer=\"" + txt_a + "\" where id=" + str(row[0])
                    #print (sql) # 调试用
                    update_if = conn_p.write_sql(sql)
                    if (update_if):
                        k += 1
                        
                    print (m) # 显示操作计数
                    m += 1
                    
                j +=1
            
        txt += "执行完毕，共耗时" +  str(round(time_cost(time_start),2)) + "秒,操作" + str(m) + " 次，成功" + str(k)+ "次。"
        
        return txt
        
# 数据库清理对象
class Clear_db(Clear_base):

    def __init__(self):
        
        # 主题关键词
        self.keyword_topic = ["癌",
        "瘤",
        "囊肿",
        "淋巴",
        "放疗",
        "化疗",
        "靶向",
        "病理",
        "恶性",
        "良性",
        "病变",
        "占位",
        "白血病",
        ]
        # html特征码
        self.html_code = [["<br/>","\n"],
        ["&quot;",""],
        ["&amp;","&"],
        ["&lt;","<"],
        ["&gt;",">"],
        ["&nbsp;"," "],
        ["&times",""],
        ["&#039;"," "],
        ]
        # 固定搭配标点
        self.punctuation_cut =["。",
        ".",
        "，",
        ",",
        "！",
        "!"
        "；",
        ";",
        "？",
        "?",
        "：",
        ":",
        "、",
        ]
    
    # 问数据库基础清理
    def qa_base(self,table_name_p="qa",conn_p=""):
        
        txt = ""
        sql = ""
        sql_where = ""
        numb_all_1 = 0
        numb_all_2 = 0
            
        # 清理主题不相关
        sql = "select count(*) from " + table_name_p
        res,rows = conn_p.read_sql(sql)
        
        if ( res < 1):
            return table_name_p + "为空或数据库读取错误"
        else:
            numb_all_1 = rows[0][0]
        print ("原始数据记录",numb_all_1) # 调试用
        
        sql = "delete from " + table_name_p + " where question is null"
        print (sql) # 调试用
        del_if = conn_p.write_sql(sql) # 清理数据
        
        sql = "delete from " + table_name_p + " where answer is null"
        print (sql) # 调试用
        del_if = conn_p.write_sql(sql) # 清理数据
        
        sql = "delete from " + table_name_p + " "
        
        for x in self.keyword_topic:
            sql_where += " or question like '%" + x + "%'" 
        if (self.keyword_topic):
            sql_where = sql_where[3:]
        sql_where ="where not (" + sql_where + ")"
        sql += sql_where
        print (sql) # 调试用
        del_if = conn_p.write_sql(sql) # 清理数据
        
        # 删除问题与答案错误
        sql = "delete from " + table_name_p + " where trim(question)=trim(answer)"
        print (sql) # 调试用
        del_if = conn_p.write_sql(sql) # 清理数据
        
        # 删除长度较短但并非简短答案
        #sql = "delete from " + table_name_p + " where LENGTH(answer) < 4"
        #print (sql) # 调试用
        #del_if = conn_p.write_sql(sql) # 清理数据
        
        # 删除特定简短答案
        sql = "delete from " + table_name_p + " where trim(answer) = '你好' or trim(answer) = '您好'"
        print (sql) # 调试用
        del_if = conn_p.write_sql(sql) # 清理数据
        
        sql = "select count(*) from " + table_name_p
        res,rows = conn_p.read_sql(sql)
        
        if ( res < 1):
            pass
        else:
            numb_all_2 = rows[0][0]
        
        print ("删除性清理记录数",numb_all_1-numb_all_2)
        
        for x in self.html_code:
        
            sql ="update " + table_name_p + " set question=replace(question,'" + x[0] + "','" + x[1] + "'), answer=replace(answer,'" + x[0] + "','" + x[1] + "')"
            print (sql) # 调试用
            update_if = conn_p.write_sql(sql) # 清理数据
        
        # 去掉特定前缀
        for x in self.punctuation_cut:
        
            sql ="update " + table_name_p + " set question=substring(question,4) where left(question,3) = '你好" + x + "'"
            print(sql) #调试用
            update_if = conn_p.write_sql(sql) # 清理数据
            sql ="update " + table_name_p + " set question=substring(question,4) where left(question,3) = '您好" + x + "'"
            print(sql) #调试用
            update_if = conn_p.write_sql(sql) # 清理数据
            sql ="update " + table_name_p + " set answer=substring(answer,4) where left(answer,3) = '你好" + x + "'"
            print(sql) #调试用
            update_if = conn_p.write_sql(sql) # 清理数据
            sql ="update " + table_name_p + " set question=substring(answer,4) where left(answer,3) = '您好" + x + "'"
            print(sql) #调试用
            update_if = conn_p.write_sql(sql) # 清理数据
            
        
        # 建立哈希值
        sql = "update " + table_name_p + " set hash=md5(CONCAT(question,answer))"
        print(sql) #调试用
        update_if = conn_p.write_sql(sql) # 清理数据
            
        return txt
    
    # 数据去重
    def nosame(self,t_name_p="temp",row_list_p="*",conn_p="",group_p="hash_main",order_p="id",where_p =""):
        
        txt = ""
        
        print (t_name_p,"去重......\n")
        
        table_name = code_char_rand()#生成随机表名
        
        sql = "CREATE TABLE " + t_name_p + "_" + table_name + " LIKE " + t_name_p
        print(sql) #调试用

        create_table_if = conn_p.write_sql(sql)
            
        sql ="INSERT INTO " + t_name_p + "_" + table_name + "(" + row_list_p + ")"
        #where_p = " where keyword not in (select keyword from keyword_wait)" # 测试用
        sql += " SELECT " + row_list_p + " from " + t_name_p + where_p + " GROUP BY " + group_p + " order by " + order_p 
        print(sql) #调试用
        insert_into_if = conn_p.write_sql(sql)
            
        sql = "drop table " + t_name_p
        print(sql) #调试用
        drop_if = conn_p.write_sql(sql)
            
        sql = "alter table " + t_name_p + "_"  + table_name + " rename " + t_name_p
        print(sql) #调试用
        alter_if = conn_p.write_sql(sql)
        
        return txt
        
    # rank分析后的问答去重处理
    def nosame_after_rank(self,table_name_p="qa",conn_p="",group_p="question,rank"):
        
        numb_fisrt = 0
        numb_last = 0
        
        sql = "select count(*) from " + table_name_p
        res,rows = conn_p.read_sql(sql)
        
        if ( res < 1):
            return table_name_p + "为空或数据库读取错误"
        else:
            numb_first = rows[0][0]
            
        sql = "truncate table temp_id"
        do_if = conn_p.write_sql(sql)
        
        sql = "INSERT temp_id (id) select id from qa group by " + group_p
        insert_if = conn_p.write_sql(sql)
        
        sql = "delete from qa where id not in (select id from temp_id )"
        insert_if = conn_p.write_sql(sql)
        
        sql = "select count(*) from " + table_name_p
        res,rows = conn_p.read_sql(sql)
        
        if ( res < 1):
            pass
        else:
            numb_last = rows[0][0]

        txt = "去重复记录：" + str(numb_first - numb_last)
        
        return txt
    
    # 访问归零
    def v2zero(self,table_name_p="qa",v_list_p=["v1","v2","v3"],conn_p=""):
        
        txt = ""
        sql = "update " + table_name_p + " set "
        for x in v_list_p:
            sql += x + "=0,"
        sql = sql[0:-1]
        print (sql) # 调试用
        update_if = conn_p.write_sql(sql) # 清理数据
        
        return txt
    # 默认综合处理函数
    def run_it(self,action_p="",tid_p=0):
        pass
    
# 数据库renew对象
class Renew_db(Clear_base):
    
    # 重建词向量元素并去重
    def index_main_renew(self,conn_p="",clear_if=1):
        txt = ""
        if (clear_if == 1):
            sql = "truncate table index_main"
            sql_if = conn_p.write_sql(sql)
            print ("表清空：",sql_if) # 调试用
            
         # 插入问题词向量元素
        sql = "INSERT into index_main (keyword,keyword_hash,idf,tf,power,where_get) "
        sql += " select keyword,keyword_hash,idf,tf,power,where_get from index_question"
        insert_if = conn_p.write_sql(sql)
        print ("插入问题词向量元素：",insert_if) # 调试用
         
         # 插入答案词向量元素
        sql = "INSERT into index_main (keyword,keyword_hash,idf,tf,power,where_get) "
        sql += " select keyword,keyword_hash,idf,tf,power,where_get from index_answer"
        insert_if = conn_p.write_sql(sql)
        print ("插入答案词向量元素：",insert_if) # 调试用
         
         # 统计最终条目数
        sql = "select count(*) from index_main"
        res,rows = conn_p.read_sql(sql)
        
        if ( res < 1):
            return "index_main表为空或数据库读取错误"
        else:
            txt = "词向量元素汇总数为：" + str(rows[0][0])
         
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
    
if __name__ == '__main__':
    main()
    
#---------- 主过程<<结束>> -----------#