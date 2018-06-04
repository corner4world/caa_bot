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
#import jieba.posseg as pseg #引入词性标注模式
user_dic_path = config.dic_config["path_jieba_dic"]
jieba.load_userdict(user_dic_path)# 导入专用字典

        
# 词的基础处理
class User(object):

    # 近义词相关词处理
    def ps_get(self,table_name="personas",numb_len=6,model_p="ne",top_p=3):
        
        txt = ""
        txt_dic = ""
        str_t = ""
        list_t = []
        list_ne = [] #命名实体队列
        sql_add = ""
        ill_is = ""
        ill_where = ""
        ill_what = ""

        table_name_root = "qa"
        
        sql = "select question,id from " + table_name_root + " where v4=0"
        #sql += " limit 10" # 调试用
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res>0):
            numb_all =res
        else:
            return ("近似词库为空或数据库读取错误")

        count_t = 1
        for row in rows:
        
            # 打上访问标记
            sql = "update " + table_name_root + " set v4=1 where id=" + str(row[1])
            #print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            str_t = row[0]
            str_t = str_t.strip()
            sql_add = ""
            ill_is = ""
            ill_where = ""
            ill_what = ""
            
            # 微服务请求疾病实体
            url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + str_t
            dic_t = inc_crawler_fast.dic_get(url_p)
            
            if (dic_t):
                
                #排序
                list_ne = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)#关键词排名
                    
                # 查询疾病实体
                for x in list_ne:
                    sql = "select keyword from keyword_ill_is where keyword='" + x[0] + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                    if (res_t > 0):
                        ill_is = x[0]
                        ill_is = ill_is.strip()
                        sql_add += "ill_is='" + ill_is + "'"
                        break
            
            # 微服务请求 主题词
            model_p = "mk"
            url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + str_t
            dic_t = inc_crawler_fast.dic_get(url_p)
            
            if (dic_t):
                
                #排序
                list_mk = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)#关键词排名
                
                if (ill_is == ""):
                    # 查询疾病实体
                    for x in list_ne:
                        sql = "select keyword from keyword_ill_is where keyword='" + x[0] + "'"
                        res_t, rows_t = rs_way_mysql.read_sql(sql)
                        if (res_t > 0):
                            ill_is = x[0]
                            ill_is = ill_is.strip()
                            sql_add += "ill_is='" + ill_is + "'"
                            break
                            
                # 查询疾病部位
                for x in list_ne:
                    sql = "select keyword from keyword_ill_where where keyword='" + x[0] + "'"
                    res_t, rows_t = rs_way_mysql.read_sql(sql)
                    if (res_t > 0):
                        ill_where = x[0]
                        ill_where = ill_where.strip()
                        if (sql_add != ""):
                            sql_add += ","
                        sql_add += "ill_where='" + ill_where + "'"
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
                        
            # 性别判别
            sex_is = ""
            list_male = ["父亲","爸爸","祖父","爷爷","外公","公公","儿子","孙子","丈夫","老公","汉子","小伙","哥们","外甥","男","man","爹","male"] # 男名词
            list_female = ["母亲","妈妈","祖母","奶奶","外婆","婆婆","女儿","孙女","妻子","老婆","美女","姑娘","闺蜜","姐们","女","娘","woman","female"] # 女名词
            for x in list_male:
                if (x in str_t):
                    sex_is += "男"
            for x in list_female:
                if (x in str_t):
                    sex_is += "女"
                    
            if (sql_add != ""):
                if (sex_is != ""):
                    sql_add += ","
                    sql_add += "sex='" + sex_is +"'"
            
            # 增加到用户画像模型表
            if (sql_add != ""):
                sql = "insert into " + table_name + " set qid=" + str(row[1]) + ", "
                sql += sql_add
                try:
                    print (sql) # 调试用
                except:
                    pass
                insert_if = rs_basedata_mysql.write_sql(sql)
                
            print ("第 " + str(count_t) + " 次操作，完成率：" + str(round(count_t*100/numb_all,2)) + "%")
            count_t += 1
            
        return txt

# 主执行调用入口函数
def run_it(str_t="",id=0,action_p="user_main"):

    txt = ""
    
    if (str_t):
        pass
    else:
        return txt
        
    if (action_p == "ps_get"):
        txt = "hello world!"
        user = User()
        txt = user.ps_get(table_name=str_t)
        return txt
    
    return txt
    
if __name__ == '__main__':
    print ("") # 防止代码泄漏只输出空字符 
    