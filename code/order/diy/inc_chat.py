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
import random # 随进函数
import math #数学计算库

#-----系统外部需安装库模块引用-----

import jieba # 引入结巴分词类库 第三方库
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
import jieba.posseg as pseg #引入词性标注模式
user_dic_path = "../data/dic/user_dic_jieba.txt"
jieba.load_userdict(user_dic_path)# 导入专用字典

#-----DIY自定义库模块引用-----

from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
from diy.inc_hash import hash_make #MD5函数
from diy.inc_nlp_way import * #nlp的一些基础方法,快速库,简单字典等
from diy.inc_result import Result_base # 基础NLP型处理类
from diy.inc_dae import * # 数据分析引擎核心库

sys.path.append("..")
rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
import config #系统配置参数


#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

result = Result_base() # 基础处理实例

# ---全局变量处理

numb_prattle_why = len(dic_prattle_why)
numb_prattle_last = len(dic_prattle_last)

# 问答基类
class Qa_base(object):

    def __init__(self):
        self.numb_kwd_long = 32 #超长文本阈值
        self.numb_kwd_cut = 6 #自然分词阈值
        self.numb_dot = 20 # 知识点取样阈值
        self.numb_table = 6 # 最大并表阈值
        self.numb_like = 10 # 结果值最大相近阈值
        sql = "select count(*) from qa"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res > 0):
            self.numb_q_all = rows[0][0]
        else:
            self.numb_q_all = 0.00000001
    
    # 文本的重点标注
    def txt_remak(self,txt_p="",color_p="#ff0000",list_p=[()]):
        for x in list_p:
            txt_p = txt_p.replace(x[0],"<font style=\"height:32px;font-family: 微软雅黑;color:" + color_p + ";\">" + x[0] + "</font>")
        return txt_p
        
# 问答类
class Qa(Qa_base):
    
    # 提交的分类处理
    def class_is(self,q_p=""):
    
        what_is_p = 6
        # 问候形式引导词优先判别
        numb_q = len(q_p)
        if (numb_q < 1):
            what_is_p = -1
            return what_is_p
        else:
            if (numb_q < 7):
                for x in dic_guide:
                    if (x in q_p):
                        what_is_p = 0
                        return what_is_p
                        break
                
        feature_dae = Feature_dae()
        dic_min,dic_max = feature_dae.dic_endline()
        what_is_p = feature_dae.question_cf(q_p=q_p,numb_p=16,id_p=7,dic_min=dic_min,dic_max=dic_max)
        return what_is_p
        
    # 中文分词不标注词性
    def seg_main(self,str_p=""):
        
        smt_list = ""
        
        try:
            str_list = result.nature_paragraph(str_p)
        except: 
            str_list = str_p
            
        list_t = str_list.split("\n") #自然分词后处理的队列
        
        # 分词处理
        for str_t in list_t:
            
            try:
                numb_str = len(str_t)
            except:
                numb_str = 0
            
            # 如果没达到自然分词阈值的上限
            if (numb_str <= self.numb_kwd_cut):
                    
                if (numb_str > 0):
                    if (str_t.strip() != ''):
                        smt_list +=  str_t + "\n" #自然分段处理后 长度小于分词阈值 默认为一个词存入待选队列
                        #smt_list_flag = smt_list_flag + str_t + "/nz~~~~" #自然分词词性默认为其它名词
            else:
                #words = pseg.cut_for_search(str_t)
                words = jieba.cut(str_t)
                for str_y in words:
                    smt_list += str_y + "\n" #利用结巴分词组件进行初步分析处理
                    #smt_list_flag = smt_list_flag + str_y.word + "/" + str_y.flag +"~~~~"
        
        arr_last = smt_list.split("\n")
        return arr_last
        
    # 命名实体识别
    def ner(self,list_p=[]):
        ne = ""
        list_ne = []
        str_t = ""
        dic_t = {}
        
        for x in list_p:

            #1 高级字典匹配
            find_if = 0

            for y in dic_ner_1:
                if (y in x):
                    list_ne.append(x)
                    find_if = 1
                    break
            if (find_if == 1):
                continue
            #2 中级字典匹配
            for y in dic_ner_2:
                if (y in x):
                    list_ne.append(x)
                    find_if = 1
                    break
            if (find_if == 1):
                continue
           
        # 高中级字典匹配失败后，进行初级字典匹配
        if (len(list_ne) < 1):
        
            for x in list_p:
                #3 初级字典匹配 调用数据库
                sql = "select keyword from keyword_ne where keyword like '%" + x + "%'"
                res, rows = rs_way_mysql.read_sql(sql)
                if (res > 0):
                    list_ne.append(x)
                    find_if = 1
                    continue
                else:
                    #右侧缩进一个词再做一次尝试
                    if (len(x) > 1):
                        x = x[0:-1]
                        sql = "select keyword from keyword_ne where keyword like '%" + x + "%'"
                        res, rows = rs_way_mysql.read_sql(sql)
                        if (res > 0):
                            list_ne.append(x)
                            find_if = 1
                            continue
            
            #if (len(list_ne) < 1):
            #调用机器学习命名实体判别引擎
        
        return list_ne
    
    # 主执行方法
    def do_it(self,q_p="",what_is_p=6):
        
        txt = ""
        txt_t = ""
        x_x = ""
        q_p = q_p.strip()
        str_t = ""
        seg_list = []
        ne_list = "" # 命名实体或主题词
        dic_t = {}
        list_t = []
        list_wait = [] # 待加入命名实体队列
        sql = ""
        sql_head = ""
        sql_data = ""
        sql_where = ""
        sql_order = ""
        sql_limit = ""
        str_old = ""
        
        #1全句匹配
        sql = "select answer from qa where hash='" + hash_make(q_p) + "'"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if ( res>0 ):
            txt = rows[0][0]
            return txt
        #2 检索相近集
        #2-1 形成待查队列
        seg_list = self.seg_main(str_p=q_p)
        list_wait = seg_list
        txt_t += str(seg_list) #调试用
        #2-2 命名实体处理
        list_ne = self.ner(list_p=seg_list)
        txt_t += "<br>命名实体：" + str(list_ne) # 调试用
        
        #TF_IDF算法参数处理
        
        numb_q = len(seg_list) #提交块词队列长度即总词数
        
        
        # 已识别命名主体处理
        if (len(list_ne) > 0):
            # TD-IDF法判别唯一命名实体
            # 统计词频
            for x in list_ne:
                if (x in dic_t):
                    dic_t[x] = dic_t[x] + 1
                else:
                    dic_t[x] = 1
                    
            # 获得TF-IDF值
            for x in dic_t:
                
                numb_q_idf = 1
                
                sql = "select idf from index_question where keyword='" + x + "'"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if ( res > 0):
                    numb_q_idf = rows[0][0] + 1
                else:
                    # 长词缩短增加命中率
                    if (len(x) > 4):
                        x_x = x[0:4]
                    sql = "select idf from index_question where keyword like '%" + x_x + "%' order by idf desc"
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if ( res > 0):
                        numb_q_idf = rows[0][0] + 1

                dic_t[x] = (dic_t[x]/numb_q)*math.log(self.numb_q_all/numb_q_idf)
        
            list_t = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)#排名
            #txt_t += "<br>命名主体排序：" + str(list_t) # 调试用
            list_ne = []
            for x in list_t:
                list_ne.append(x)
                # 从待查队列中去掉命名实体
                list_t2 = list_wait
                list_wait = []
                for y in list_t2:
                    if(y != x[0]):
                        list_wait.append(y)
                        
        # 命名主体识别失败
        if (len(list_ne) == 0):
            #启动机器学习泛化命名主体识别引擎
            list_wait =  seg_list
            
        txt_t += "<br>已选命名主体队列：" + str(list_ne)
        #整理候选关键词
        dic_t = {}
        dic_add = {}
        
        for x in list_wait:
            
            #滤掉单字
            if (len(x) < 2):
                continue
                
            #滤掉停用词
            if (x in dic_stop):
                continue
            
            #统计TF
            if (x in dic_t):
                numb_t = dic_t[x]
                dic_t[x] = numb_t + 1
            else:
                dic_t[x] = 1
        
        if (dic_t):
        
            list_del = []
            # 获得TF-IDF值
            
            for x in dic_t:
            
                new_ne = "" #构造新命名主体
                numb_q_idf = 1
                
                sql = "select idf from index_question where keyword='" + x + "'"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if ( res > 0):
                    numb_q_idf = rows[0][0] + 1
                    dic_t[x] = (dic_t[x]/numb_q)*math.log(self.numb_q_all/numb_q_idf)
                else:
                    # 长词缩短增加命中率
                    if (len(x) > 4):
                        x_x = x[0:4]
                    sql = "select idf,keyword from index_question where keyword like '%" + x_x + "%' order by idf desc"
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if ( res > 0):
                        numb_q_idf = rows[0][0] + 1
                        new_ne = rows[0][1]
                
                    if (new_ne == ""):
                        list_del.append(x)
                    else:
                        dic_add[new_ne] = (dic_t[x]/numb_q)*math.log(self.numb_q_all/numb_q_idf)
            
            #删除非主体词
            for y in list_del:
                del dic_t[y]
            
            #增加新元素
            for z in dic_add:
                dic_t[z] = dic_add[z]
            
            list_t = []
            list_t = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)#排名
            #txt_t += "<br>候选命名主体排序：" + str(list_t) # 调试用
            list_wait = []
            for x in list_t:
                if (x[1] != ""):
                    list_wait.append(x)
        
        #2-3 获得命名主体相关结果集
        numb_select = 0
        list_find = []
        #构造查询队列

        for x in list_ne:
            list_find.append([x[0],""])
            numb_select += 1
            if (numb_select >= self.numb_table):
                break
        for x in list_wait:
            try:
                str_t = x[0]
                str_t = str_t.strip
                if (str_t != "numb_key_ldae" and str_t !="" and len(str_t)>1):
                    list_find.append([str_t,""])
                numb_select += 1
            except:
                pass
            if (numb_select >= self.numb_table):
                break

        #获得查询关键词hash值
        for x in list_find:
            sql = "select keyword_hash from index_question where keyword='" + x[0] + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res>0):
                x[1] = rows[0][0]
            else:
                if (len(x[0]) > 4):
                    x_x = x[0][0:4]
                sql = "select keyword_hash from index_question where keyword like '%" + x_x + "%' order by idf desc"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if (res>0):
                    x[1] = rows[0][0]
                
        txt_t += "<br>最后的待查询队列：" + str(list_find)
        
        if (list_find):
            sql_limit = " limit " + str(self.numb_like) + " "
            j = len(list_find)
            
            while (j >= 0):
            
                i = 1
                for x in list_find:
                    
                    if (i > j):
                        #print (str(i)) 调试用
                        break

                    if (i == 1):

                        sql_head = "select "
                        sql_head +="z_question_" + x[1] + ".pid, "
                        sql_head +="z_question_" + x[1] + ".rank, "
                        sql_head +="z_question_" + x[1] + ".x0, "
                        sql_head +="z_question_" + x[1] + ".x1, "
                        sql_head +="z_question_" + x[1] + ".x2, "
                        sql_head +="z_question_" + x[1] + ".x3 "
                        sql_head += "from "
                        sql_data = " z_question_" + x[1]
                        sql_where = ""
                        sql_order = " order by z_question_" + x[1] + ".rank desc "
                        
                    else:
                        
                        sql_data += " inner join z_question_" + x[1] + " on z_question_" + str_old + ".pid = z_question_" + x[1] + ".pid "
                    
                    str_old = x[1]
                    i += 1
                
                sql = sql_head + sql_data + sql_where + sql_order + sql_limit
                #print (sql) #调试用
                res_p, rows_p = rs_index_mysql.read_sql(sql)
                if (res_p > 0):
                    break
                
                j -= 1
        txt_t += "<br>" + sql
        
        # 结果集导入
        if (res_p > 0):
            
            tf = 0
            idf = 0
            dic_t = {}
            k = 1
            list_idf = []
            
            # 主题词IDF计算
            for y in list_find:
                
                numb_q_idf = 0
                str_t = y[0]
                
                sql = "select idf from index_answer where keyword='" + str_t + "'"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if ( res > 0):
                    numb_q_idf = rows[0][0] + 1
                    list_idf.append([y[0],math.log(self.numb_q_all/numb_q_idf)])
                else:
                    # 长词缩短增加命中率
                    if (len(x) > 4):
                        x_x = str_t[0:4]
                    else:
                        x_x = str_t
                    
                    sql = "select idf from index_answer where keyword like '%" + x_x + "%' order by idf desc"
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if ( res > 0):
                        numb_q_idf = rows[0][0] + 1
                        list_idf.append([y[0],math.log(self.numb_q_all/numb_q_idf)])
                        
            # 命中主题词IDF查找结束
            k = 1
            for row in rows_p:
            
                is_if = 0 # 是否标题分类匹配
                rank_t = 0 # 按标题匹配顺序赋予排名初值
                dic_seq ={}
                sql = "select question,answer,seq_a,what from qa where "
                sql += " id=" + str(row[0])
                res, rows = rs_basedata_mysql.read_sql(sql)
                
                if (res > 0):
                    
                    #获得正排字典
                    try:
                        dic_seq = eval(rows[0][2])
                    except:
                        pass
                    
                    # 计算TF-IDF之和作为二次排名的参考
                    for y in list_idf:
                        
                        if y[0] in dic_seq:
                            rank_t += len(dic_seq[y[0]])*y[1]
                            #print (k,y[0],y[1],rank_t) # 调试用
                    
                    if (what_is_p == rows[0][3]):
                        is_if = 1
                        
                    # 重新计算答案匹配度
                    dic_t[k]=[rows[0][0],rows[0][1],rows[0][2],is_if,rank_t]
                    k +=1
                    
                    
            if dic_t:
                pass
            else:
                txt = ""
                return txt
                
        else:
        
            txt = ""
            return txt
            
        #3 结果集处理,定位最佳匹配
        
        list_order = []
        dic_1 = {}
        dic_2 = {}
        list_1 = []
        list_2 = []
        for x in dic_t:
            # 区分分类是否命中
            if (dic_t[x][3]==1):
                dic_1[x] = dic_t[x][4]
            else:
                dic_2[x] = dic_t[x][4]
        
        if (dic_1):
            list_1 = sorted(dic_1.items(), key=lambda d:d[1], reverse = True)#排名
        if (dic_2):
            list_2 = sorted(dic_2.items(), key=lambda d:d[1], reverse = True)#排名
        if (list_1):
            list_order += list_1
        if (list_2):
            list_order += list_2
        
        #4 最后结果校验

        #5 最后结果渲染并输出
        numb_fit = 0
        if (list_order):
            
            
            txt_a_main = ""
            
            try:
                numb_fit = list_order[0][0]
                txt_a_main= dic_t[numb_fit][1] + "<br><br>"
            except:
                pass
                
            if (txt_a_main != ""):
                txt += "让您久等了，找到以下参考答案:<br><br>" + txt_a_main
                
        if (len(dic_t) > 1):

            del list_order[0]
            txt_a_t = ""
            
            if (txt_a_main != ""):
                txt_a_about = "---- 您的问题很有代表性，因此我们特意还向你推荐相关参考答案：---- <br><br>"
            else:
                txt_a_about = "---- 您的的问题暂时没标准答案，我们特意向你推荐相关参考答案：---- <br><br>"

            for x in list_order:
                
                try:
                    txt_a_t += "<div>问：" + self.txt_remak(txt_p=dic_t[x[0]][0],color_p="#ff0000",list_p=list_ne) + "</div><br>"
                    txt_a_t += "答：" + self.txt_remak(txt_p=dic_t[x[0]][1],color_p="#ff0000",list_p=list_ne) + "<br><br>"
                except:
                    pass
                    
            if (txt_a_t != ""):
                txt += txt_a_about + txt_a_t
        
        return txt

# 分支选择执行
def to_do(what_is_p=0,q_p=""):
    txt = ""
    qa = Qa()
    #print (what_is_p) # 调试用
    # 0 引导词
    if (what_is_p == 0):
        txt = ""
        if q_p in dic_hello:
            txt = dic_hello[q_p]
        return txt
        
    # 1 诊断
    if (what_is_p == 1):
        txt = "诊断"
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p)
        return txt
        
    # 2 治疗
    if (what_is_p == 2):
        txt = "治疗"
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p)
        return txt
        
    # 3 知识
    if (what_is_p == 3):
        txt = "预测"
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p)
        return txt
        
    # 4 预测生存期
    if (what_is_p == 4):
        txt = "预测生存期"
        return txt
        
    # 5 费用
    if (what_is_p == 5):
        txt = "费用"
        return txt
        
    # 6 其它
    if (what_is_p == 6):
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p)
        return txt
        
    return txt

# ---本模块内部类或函数定义区
def run_it(q_p,log_if=1):

    #---- 问答解析开始 ----
    
    # 重要变量赋初值
    time_start = datetime.datetime.now()
    answer = ""
    time_zero = time.strftime('%Y-%m-%d %H:%M:%S')
    chat_p = "<div align=\"left\">"
    chat_p += "<div  style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">"
    chat_p += time_zero + "</div>"
    chat_p += "<div align=\"right\">" + q_p + "&nbsp&nbsp <img src=\"/statics/img/head_pat_1.gif\" border=0 alt=\"患者\" ></div><br><br>"
    what_is = 6
    
    #1 提交性质判别
    if (q_p in dic_hello):
        what_is = 0
    else:
        qa = Qa()
        #命名实体识别
        try:
            what_is = qa.class_is(q_p) # 提交分类判别
        except:
            pass
            
    #2 根据提交性质选择分支执行
    answer = to_do(what_is_p=what_is,q_p=q_p)
    #3 结果校验
    #4 最后一次匹配提交
    
    if (answer == ""):
        try:
            answer = dic_prattle_why[random.randint(1,numb_prattle_why)]
        except:
            answer = "......"
            
    #if (answer == ""):
        #answer = dic_prattle_last[random.randint(1,numb_prattle)]
    #5 最后的结果渲染
    if (what_is == 0):
        chat_p += "<img src=\"/statics/img/head_doc_0.gif\" border=0 alt=\"引导\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 1):
        chat_p += "<img src=\"/statics/img/head_doc_1.gif\" border=0 alt=\"诊断\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 2):
        chat_p += "<img src=\"/statics/img/head_doc_2.gif\" border=0 alt=\"治疗\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 3):
        chat_p += "<img src=\"/statics/img/head_doc_3.gif\" border=0 alt=\"知识\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 4):
        chat_p += "<img src=\"/statics/img/head_doc_4.gif\" border=0 alt=\"预测\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 5):
        chat_p += "<img src=\"/statics/img/head_doc_5.gif\" border=0 alt=\"费用\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 6):
        chat_p += "<img src=\"/statics/img/head_doc_6.gif\" border=0 alt=\"其它\" >&nbsp&nbsp " + answer + "<br><br>"
    
    chat_p += "</div>"
    chat_p += """
    <HR style="FILTER: progid:DXImageTransform.Microsoft.Glow(color=#987cb9,strength=10)" width="100%" color=#cccccc SIZE=1>
    """
    
    #6 收尾处理，返回结果
    
    
    time_last = str(time_cost(time_start))
    chat_p += "<div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">本次对话,共耗时：" + time_last + " 秒。</div>"
    
    # 日志处理
    if (log_if == 1):
        try:
            f = open('../data/log/chat_log.txt','a')
            f.write('\n\n')
            f.write(time_zero)
            f.write("@~@" + q_p)
            f.write("@~@" + answer)
            f.write("@~@" + time_last)
            f.close()
        except:
            pass
            
    return chat_p
    

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