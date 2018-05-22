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
import math #数学计算库
from collections import Counter # 统计函数

#-----系统外部需安装库模块引用-----

import jieba # 引入结巴分词类库 第三方库
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
#import jieba.posseg as pseg #引入词性标注模式
user_dic_path = config.dic_config["path_jieba_dic"]
jieba.load_userdict(user_dic_path)# 导入专用字典

#-----DIY自定义库模块引用-----

from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
from diy.inc_result import * #自定义特定功能模块
from diy.inc_hash import hash_make #MD5函数
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
import config #系统配置参数

sys.path.append("..")

import inc_dic # 内置数据字典模块

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理
path_main = config.dic_config["path_main"] #主绝对路径
log_if = int(config.dic_config["log_if"]) #主绝对路径
numb_prattle_why = len(inc_dic.dic_prattle_why)
numb_prattle_last = len(inc_dic.dic_prattle_last)
dic_hello = inc_dic.dic_hello
dic_ner_1 = inc_dic.dic_ner_1
dic_ner_2 = inc_dic.dic_ner_2
dic_guide = inc_dic.dic_guide
dic_prattle_last = inc_dic.dic_prattle_last
dic_prattle_why = inc_dic.dic_prattle_why
result_base = Result_base() #特殊功能类实例化
test_if = int(config.dic_config["test_if"]) # 调试模式
dic_cf_root = {1:"cf_cnn_bilstm_field",2:"cf_svm",3:"cf_lr_yesno"} #意图优先字典
dic_cf_child = {0:"cf_lr_yesno",1:"cf_lr_yesno",2:"cf_cnn_bilstm_field",3:"cf_lr_yesno",4:"cf_cnn_bilstm_field",5:"cf_lr_yesno",6:"cf_cnn_bilstm_field"}

# 搜索基类
class Search_base(object):

    def __init__(self):
    
        self.numb_kwd_long = 32 #超长文本阈值
        self.numb_kwd_cut = 6 #自然分词阈值
        self.numb_dot = 20 # 知识点取样阈值
        self.numb_table = 6 # 最大并表阈值
        self.numb_like = 10 # 结果值最大相近阈值
    
    # 文本的重点标注
    def txt_remak(self,txt_p="",color_p="#ff0000",list_p=[()]):
        #for x in list_p:
            #txt_p = txt_p.replace(x[0],"<font style=\"height:32px;font-family: 微软雅黑;color:" + color_p + ";\">" + x[0] + "</font>")
        return txt_p
        
# 搜索类
class Search(Search_base):
    
    # 字符串统计函数
    def count_str(self,list_p=[],action_p="max",numb_p=1):
        if (action_p == "max"):
            return Counter(list_p).most_common(numb_p)
    
    # 通过微服务获得模型类型
    def get_what_is(self,model_p,q_p=""):
        
        what_is_p = 6
        
        url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + q_p
        #print(url_p) # 调试用
        
        try:
            txt = inc_crawler_fast.get_html_get(url_p)
        except:
            pass

        if (txt):
            try:
                dic_t = eval(txt)
                what_is_p = int(dic_t["classify"])
            except:
                pass
        #print (txt) # 调试用
        return what_is_p
    
    # 提交的分类处理
    def class_is(self,q_p=""):
        
        list_v = [] # 投票候选队列
        list_w = [] # 统计队列
        str_t = ""
        what_is_p = 6
        dic_t = {}
        numb_r = 1
        
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
        
        # 意图融合模型判别
        i = 1
        while (i<4): 
        
            # 初次访问随机处理
            if (i == 1):
                numb_r = random.randint(1,3)
            else:
                if (numb_r == i):
                    continue
                else:
                    numb_r = i
                
            print(i,"随机数: ",numb_r,dic_cf_root[numb_r]) # 调试用
            
            what_is_p = self.get_what_is(model_p=dic_cf_root[numb_r],q_p=q_p)
            print (i," 意图识别：",what_is_p) # 调试用
            print (dic_cf_root[i],dic_cf_child[what_is_p]) # 调试用
            
            if (dic_cf_root[numb_r] == dic_cf_child[what_is_p]):
                break
            else:
                list_v.append(str(what_is_p))
            
            i += 1

        # 如果遍历出现 则投票筛选
        if (i == 4):
            list_w = self.count_str(list_v)
            
            if (list_w):
                what_is_p = int(list_w[0][0])
            else:
                what_is_p = self.get_what_is(model_p=dic_cf_root[0]) # 票数相同 取最大综合准度的意图识别模型
            
        return what_is_p
                

    # 主执行方法
    def do_it(self,q_p="",what_is_p=6,test_if_p=0,txt_end_p="<br>您若还有其它问题,可以继续提问。"):
    
        txt = "" # 返回的结果文本
        txt_t = ""
        if (test_if_p == 1):
            txt += "[初级语义分型：" + str(what_is_p) + "]<br>" # 调试用中间结果文本
        time_start_p = datetime.datetime.now() #内部执行初始时间
        q_p = q_p.strip()
        str_mk = "" # 关键词串
        str_ne = "" # 命名实体临时串
        url_p = "" # API服务请求地址
        arr_t = [] # 临时数组
        dic_t = {} # 临时字典
        dic_m = {} # 关键词字典
        dic_n = {} # 命名实体字典
        dic_r = {} # 结果集字典
        dic_p = {} # 最后的排列字典
        list_mk = [] # 关键词队列
        list_ne = [] # 命名实体队列
        list_find = [] # 待查询队列
        list_find_last = [] #最后的匹配命中队列
        list_t = [] # 临时队列
        str_t = "" # 临时字符串
        str_old = "" # 字符串备份 主要用于比对
        sql = "" # 主查询语句
        sql_head = "" # 主查询头
        sql_data = "" # 主查询表端内容
        sql_where = "" # 主查询条件
        sql_order = "" # 主查询排序
        sql_limit = "" # 主查询限定数量
        x_x = "" # 模糊匹配关键词串
        rank = 0.0 # 排名值
        Sq = 0 # 候选集的标题相似度
        Sa = 0 # 候选集的文本相似度
        vec_t = [] # 临时词向量
        dic_input = {} # 提问的关键词字典
        list_cos_0 = "" # 余弦向量初始值队列串
        list_cos = [] # 余弦词向量队列
        dic_c_t = {} # 余弦值临时字典
        list_a = [] # 余弦a边的向量
        list_b = [] # 余弦b边的向量
        
        
        # 2-1 关键词处理
        
        url_p = config.dic_config["url_api"] + "api?action=mk&q=" + q_p

        try:
            str_mk = inc_crawler_fast.get_html_get(url_p)
        except:
            return "系统内部网络故障，稍候请再试一次。"
            
        if (str_mk):

            try:
                dic_t = eval(str_mk)
            except:
                pass
                
            if (dic_t):
                dic_input = dic_t # 提问的关键词字典
                for y in dic_t:
                    dic_m[y] = float(dic_t[y])
                list_mk = sorted(dic_m.items(), key=lambda d:d[1], reverse = True)#关键词排名
            
        #2-2 命名实体处理
        if (dic_m):
            
            list_t = []
            # 对带分段型标点符号的长文本进行特殊处理
            str_t = result_base.np_some(str_p=q_p) # 自然分句
            arr_t = str_t.split("@x@")
            
            
            # 按自然分句进行命名实体识别
            
            # 只有一个自然句
            if (len(arr_t) == 1):
            
                url_p = config.dic_config["url_api"] + "api?action=ne&q=" + q_p
                str_ne = inc_crawler_fast.get_html_get(url_p)
                if (str_ne):

                    try:
                        dic_t = eval(str_ne)
                    except:
                        pass
                
                if (dic_t):
                    for y in dic_t:
                        dic_n[y] = float(dic_t[y])
                    list_ne = sorted(dic_n.items(), key=lambda d:d[1], reverse = True)#命名实体排名
            
            # 多个自然句
            else:
            
                for x in arr_t:
                
                    dic_t = {}
                    dic_n = {}
                    str_ne = ""
                    
                    url_p = config.dic_config["url_api"] + "api?action=ne&q=" + x
                    str_ne = inc_crawler_fast.get_html_get(url_p)
                    
                    if (str_ne):

                        try:
                            dic_t = eval(str_ne)
                        except:
                            pass
                    
                    if (dic_t):
                        for y in dic_t:
                            dic_n[y] = float(dic_t[y])
                        list_t = sorted(dic_n.items(), key=lambda d:d[1], reverse = True)#命名实体排名
                        k = 0
                        for y in list_t:
                        
                            if (k == 1):
                                break
                            
                            if (list_ne):
                                
                                find_if = 0
                                for z in list_ne:
                                    if (z[0] == y[0]):
                                        if (z[1] < y[1]):
                                            list_ne.remove(z)
                                            list_ne.append(y) #出现重复值,则保留最大的评分值
                                        find_if = 1
                                        k += 1
                                        break
                                        
                                if (find_if == 0):
                                    list_ne.append(y)
                                    k += 1
                            
                            else:
                            
                                list_ne.append(y)
                                k += 1
                
        
        # 3 构造查询队列
        
        numb_find = int(config.dic_config["numb_find"]) # 获得最大匹配关键词数
        j = 1
        for x in list_ne:
            
            if (j > numb_find):
                break
            list_find.append([x[0],"",x[1]])
                
            j += 1
        
        j = j - 1
        
        if (j < numb_find):
            
            for x in list_mk:
            
                if (j == numb_find):
                    break
                    
                if (list_find):
                
                    find_if = 0
                    for z in list_find:
                    
                        if (z[0] == x[0]):
                            if (z[2] < x[1]):
                                z[1] = x[1]
                            find_if = 1
                            j += 1
                            break
                                        
                    if (find_if == 0):
                        list_find.append([x[0],"",x[1]])
                        j += 1
                else:
                
                    list_find.append([x[0],"",x[1]])
                    j += 1
        
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
        
        if (test_if_p == 1):
            txt += "[待选匹配：" + str(list_find) + "]<br>" # 调试用      
        
        if (list_find):
            
            list_find_last = list_find 
            
            sql_limit = " limit " + config.dic_config["numb_limit"] + " "
            
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
                else:
                    del list_find_last[len(list_find_last)-1]
                j -= 1
        
        if (test_if_p == 1):
            txt += "[最终成功匹配：" + str(list_find_last) + "]<br>" # 调试用
        
        if (res_p < 1):
            return ""
            
        #2 构造候选结果集
        
        # 生成比对字典初始的部分
        for x in dic_input:
            if x in list_cos_0:
                pass
            else:
                list_cos_0 += x + "@x@"
        
        i = 1
        for row in rows_p:
        
            rank = 0 # 排名值清空
            sql = "select question,forward_question,answer,forward_answer,keyword_question,keyword_answer,rank,what from qa where id=" + str(row[0])
            res, rows = rs_basedata_mysql.read_sql(sql)
            
            if (res < 0):
                continue
                
            dic_r[row[0]] = [row,rows]
            
        
            #3 结果集处理,定位最佳匹配
            
            # 问题相似度计算
            list_cos = []
            dic_c_t.clear()
            list_a = []
            list_b = []
            Sq = 0
            
            # 基础比对向量重赋值
            
            list_cos = list_cos_0.split("@x@")
            
            # 生成比对字典
            try:
                dic_c_t = eval(rows[0][4])
            except:
                pass
                
            # 生成比对字典b边并a边的部分
            for x in dic_c_t:
                if x in dic_input:
                    pass
                else:
                    list_cos.append(x)
                
            for x in list_cos:
                if x in dic_input:
                    list_a.append(float(dic_input[x]))
                else:
                    list_a.append(0.0)
                if x in dic_c_t:
                    list_b.append(dic_c_t[x])
                else:
                    list_b.append(0.0)
            
            #计算余弦值
            fenzi = 0.0 # 分子值
            fenmu_1 = 0.0 # 分母值
            fenmu_2 = 0.0
            k = 0
            
            for x in list_cos:
                fenzi += list_a[k]*list_b[k]
                fenmu_1 += list_a[k]*list_a[k]
                fenmu_2 += list_b[k]*list_b[k]
                k += 1
            
            fenmu_1 = math.sqrt(fenmu_1)
            fenmu_2 = math.sqrt(fenmu_2)
            if (fenmu_1 + fenmu_2 > 0):
                Sq = fenzi/(fenmu_1 + fenmu_2)
                
            #txt += "标题："  + str(rows[0][0]) + " --- 标题对标题余弦待查队列 " + str(list_cos) + " <br>a边： " + str(list_a) + " <br>b边：" + str(list_b) + " <br>标题对标题余弦值：" + str(Sq) + "<br>" # 测试用
            
            #3 结果集处理,定位最佳匹配
            # 问题相似度计算
            list_cos = []
            dic_c_t.clear()
            list_a = []
            list_b = []
            Sa = 0
            
            # 基础比对向量重赋值
            list_cos = list_cos_0.split("@x@")
            
            # 生成比对字典
            try:
                dic_c_t = eval(rows[0][5])
            except:
                pass
                
            # 生成比对字典b边并a边的部分
            for x in dic_c_t:
                if x in dic_input:
                    pass
                else:
                    list_cos.append(x)
            
            for x in list_cos:
                if x in dic_input:
                    list_a.append(float(dic_input[x]))
                else:
                    list_a.append(0.0)
                if x in dic_c_t:
                    list_b.append(0.5*dic_c_t[x][0] + 0.5*dic_c_t[x][1])
                else:
                    list_b.append(0.0)
            
            #计算余弦值
            fenzi = 0.0 # 分子值
            fenmu_1 = 0.0 # 分母值
            fenmu_2 = 0.0
            k = 0
            for x in list_cos:
                fenzi += list_a[k]*list_b[k]
                fenmu_1 += list_a[k]*list_a[k]
                fenmu_2 += list_b[k]*list_b[k]
                k += 1
            fenmu_1 = math.sqrt(fenmu_1)
            fenmu_2 = math.sqrt(fenmu_2)
            if (fenmu_1 + fenmu_2 > 0):
                Sa = fenzi/(fenmu_1 + fenmu_2)
                
            #txt += " 内容："  + str(rows[0][3]) + "  --- 标题对内容余弦待查队列 " + str(list_cos) + " <br>a边： " + str(list_a) + " <br>b边：" + str(list_b) + " <br>标题对内容余弦值：" + str(Sa) + "<br>" # 测试用
            # 内容质量值
            Pr = 0.0
            
            Wq = 0.2
            Wa = 0.7
            Wp = 0.1
            rank = round(Wq*Sq + Wa*Sa + Wp*Pr,8)
            #txt += "<br>id: " + str(row[0]) + " --- 问题： " + str(rows[0][0]) + " --- 近似语义得分：" + str(rank) + "<br><br>" #调试用
            dic_p[row[0]] = rank
            
            i += 1
        
        list_order = sorted(dic_p.items(), key=lambda d:d[1], reverse = True)#命名实体排名
        #txt += "<br> 推荐排名：" + str(list_order) + "<br><br>" # 调试用
        #4 最后结果校验

        #5 最后结果渲染并输出
        numb_fit = 0
        if (list_order):
            
            txt_a_main = ""
            numb_fit = list_order[0][0]
            try:
                if (test_if_p == 1):
                    txt_a_main += "[最佳匹配的问题：" + dic_r[numb_fit][1][0][0] +" ]"
                    txt_a_main += "[近似语义得分：" + str(list_order[0][1]) + "]"
                txt_a_main += dic_r[numb_fit][1][0][2] + "<br><br>"
            except:
                pass
                    
            if (txt_a_main != ""):
                time_wait = round(time_cost(time_start_p),2)
                if (time_wait > 3.66):
                    txt += "让您久等了，找到以下参考答案:<br><br>" 
                txt += txt_a_main
        
        if (len(dic_r) > 1):

            del list_order[0]
            txt_a_t = ""
            
            if (txt_a_main != ""):
                txt_a_about = "---- 您的问题很有代表性，因此我们特意还向你推荐相关参考答案：---- <br><br>"
            else:
                txt_a_about = "---- 您的的问题暂时没标准答案，我们特意向你推荐相关参考答案：---- <br><br>"
            
            m = 0
            for x in list_order:
                
                try:
                    txt_a_t += "<div>问：" + self.txt_remak(txt_p=dic_r[x[0]][1][0][0],color_p="#ff0000",list_p=list_ne) + "</div><br>"
                    if (test_if_p == 1):
                        txt_a_t += "[近似语义得分：" + str(list_order[m][1]) + "]"
                    txt_a_t += "答：" + self.txt_remak(txt_p=dic_r[x[0]][1][0][2],color_p="#ff0000",list_p=list_ne) + "<br><br>"
                except:
                    pass
                    
                m += 1
                    
            if (txt_a_t != ""):
                txt += txt_a_about + txt_a_t
        if (test_if_p == 1):
            txt += txt_t # 调试用
        txt += txt_end_p
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
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p,test_if_p=test_if)
        return txt
        
    # 2 治疗
    if (what_is_p == 2):
        txt = "治疗"
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p,test_if_p=test_if)
        return txt
        
    # 3 知识
    if (what_is_p == 3):
        txt = "预测"
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p,test_if_p=test_if)
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
        txt = qa.do_it(q_p=q_p,what_is_p=what_is_p,test_if_p=test_if)
        return txt
        
    return txt

# ---本模块内部类或函数定义区

# 外调模块引擎驱动函数
def run_it(q_p,remote_ip_p="0.0.0.0",user_host_p="0:0"):
    
    #---- 问答解析开始 ----
    
    # 重要变量赋初值
    time_start = datetime.datetime.now()
    result = ""
    time_zero = time.strftime('%Y-%m-%d %H:%M:%S')
    
    #1 搜索实例化
    search = Search()
 
    #2 根据提交性质选择分支执行
    result = search.do_it(q_p=q_p)
    #3 结果校验
    #4 最后一次匹配提交
    #5 最后的结果渲染

    
    #6 收尾处理，返回结果
    
    
    time_last = str(round(time_cost(time_start),2))
    result += "<div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">本次对话,共耗时：" + time_last + " 秒。</div>"
    print(log_if) # 调试用
    
    # 日志处理
    if (log_if == 1):
    
        default_l = "n/a"
        sql = "insert log_chat set "
        sql += "input='" + q_p + "',"
        sql += "output='" + answer[0:128] + "',"
        sql += "time_zero='" + time_zero + "',"
        sql += "time_last='" + time_last + "',"
        sql += "user='" + default_l + "',"
        sql += "ip='" + remote_ip_p + "',"
        sql += "port='" + user_host_p.split(":")[1] + "',"
        sql += "action='chat'"
        
        insert_if = rs_way_mysql.write_sql(sql)
    
    return result
    
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