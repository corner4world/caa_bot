# 多轮对话的form码
    form_ask = """

<link rel="shortcut icon" href="./statics/img/logo.ico" />
<script src="./statics/js/jquery-1.8.2.min.js"></script>
<script src="./statics/js/common.js"></script>
<link href="./statics/css/style.css" rel="stylesheet" type="text/css" />
<script language="javascript" src="./statics/search_tag/main_py.js"></script>
<link href="./statics/css/style_sug.css" rel="stylesheet" type="text/css" />
</head>
<center>
<div>
<form name="search_form" onSubmit="return bottomForm(this);" target="_self" method="post" action="./api">
<table>
<tr>
<td>
    <input style="width:202px;height:34px;" id="txtSearch" name="q"  onfocus="if(this.value=='空格键确认输入分隔'){this.value='';}else{this.select();}this.style.color='black';"  value="空格键确认输入分隔" onkeydown="searchSuggest();" size="28" />
&nbsp;&nbsp;&nbsp;&nbsp;
    </td>
<td>
    <input class="sb_qa" name="Input" type="submit" value="" >
</td>
</tr>
</table>
    <div id="search_suggest" style="position:float;left:-50px;top:5px;width:207px;font-size:14px;" >
    </div>

    <input name="action" type="hidden" value="chat">

</form>
</div>
<div>&nbsp;</div>

</center>
<script src="./statics/js/ah.js"></script>

    """
    
    if (answer_p[6] == 0):
        chat_p += "<br>提示：您若还有其它问题,可以继续提问。" + form_ask # 加入尾部提问
    
    chat_foot += """
    <HR style="FILTER: progid:DXImageTransform.Microsoft.Glow(color=#987cb9,strength=10)" width="100%" color=#cccccc SIZE=1>
    """
    
    chat_foot += "<div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">本次对话,共耗时：" + str(answer_p[5]) + " 秒。</div>"
    chat_foot += "<div style=\"font-size:12px;font-family: 微软雅黑;color:#ff0000;\">敬请注意：智能问答不能代替线下执业医生的诊疗，以上结果应仅仅作为建议使用！</div>"
--------------
chat_main+= "<div align=\"left\"  style=\"font-size:20px\">"
    chat_main+= "<div  style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">"
    chat_main+= answer_p[4] + "</div>"
    
chat_head += "<div align=\"left\"  style=\"font-size:20px\">"
        numb_dic_h = len(dic_h)
        j = numb_dic_h
        while (j > 0):
            tup_t = ()
            try:
                tup_t = eval("(" + dic_h[j] + ")")
            except:
                pass
            if (tup_t):
                chat_head += "<div id=\"result\" align=\"left\" style=\"width:550px; border:none; overflow:hidden;\">"
                chat_head += "【" + tup_t[1] + "】" + tup_t[4] + " "  +str(tup_t[5])+ "秒" + "<br>"
                chat_head += tup_t[2] +"<br><br>"
                chat_head += """
    <HR style="FILTER: progid:DXImageTransform.Microsoft.Glow(color=#987cb9,strength=10)" width="100%" color=#cccccc SIZE=1>
    """
                chat_head += "</div>"
            j = j -1
        chat_head += "<div> ----- <a name=\"ah1\">以上为对话的历史记录</a> ----- </div>"
        chat_head += "</div>"
        
+++++++++++++++++++++++++++++++++++++
                values = {
                    "action":model_p,
                    "q":q_p
                    }
                    
+++++++++++++++++++++++++++++++++++++
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
==================
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

#-----系统外部需安装库模块引用-----

import jieba # 引入结巴分词类库 第三方库
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
import jieba.posseg as pseg #引入词性标注模式
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

import dae.inc_dic as inc_dic # 内置数据字典模块
import dae.inc_dae as inc_dae # 数据分析引擎核心库

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

inc_redis = inc_dae.inc_redis # 缓存实例传递

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

# 问答基类
class Qa_base(object):

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
        
# 问答类
class Qa(Qa_base):
    
    # 提交的分类处理
    def class_is(self,q_p=""):
        
        str_t = ""
        what_is_p = 6
        dic_t = {}
        
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
        
        url_p = config.dic_config["url_api"] + "api?action=cf&q=" + q_p
        
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
            
        return what_is_p
                

    # 主执行方法
    def do_it(self,q_p="",what_is_p=6,test_if_p=0):
        
        txt = "" # 返回的结果文本
        txt_t = "初级语义分型：" + str(what_is_p) # 调试用中间结果文本
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
        mci = 0 # 候选集的标题相似度
        nui = 0 # 候选集的文本相似度
        vec_t = [] # 临时词向量
        dic_input = {} # 提问的关键词字典
        list_cos = [] # 余弦词向量队列
        
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
        
        txt_t += "  待选匹配：" + str(list_find) # 调试用      
        
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
                
        txt_t += "   最终成功匹配：" + str(list_find_last) # 调试用
        
        if (res_p < 1):
            return ""
            
        #2 构造候选结果集
        
        i = 1
        for row in rows_p:
            rank = 0 # 排名值清空
            sql = "select question,forward_question,answer,forward_answer,keyword_question,keyword_answer,rank,what from qa where id=" + str(row[0])
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                dic_r[row[0]] = [row,rows]
                dic_p[row[0]] = round(1/i,8)
            i += 1
        
        #3 结果集处理,定位最佳匹配
        list_cos = list_mk
        txt += " 余弦待查队列 " + str(list_cos) + " - 待叠加队列 " + str(rows[0][4]) # 测试用
        
        mci = 0
        nui = 0
        
        list_order = sorted(dic_p.items(), key=lambda d:d[1], reverse = True)#命名实体排名
        
        
        #4 最后结果校验

        #5 最后结果渲染并输出
        numb_fit = 0
        if (list_order):
            
            txt_a_main = ""
            numb_fit = list_order[0][0]
            try:
                txt_a_main= dic_r[numb_fit][1][0][2] + "<br><br>"
                txt_t += "  最佳匹配的问题：" + dic_r[numb_fit][1][0][0]
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

            for x in list_order:
                
                try:
                    txt_a_t += "<div>问：" + self.txt_remak(txt_p=dic_r[x[0]][1][0][0],color_p="#ff0000",list_p=list_ne) + "</div><br>"
                    txt_a_t += "答：" + self.txt_remak(txt_p=dic_r[x[0]][1][0][2],color_p="#ff0000",list_p=list_ne) + "<br><br>"
                except:
                    pass
                    
            if (txt_a_t != ""):
                txt += txt_a_about + txt_a_t
        if (test_if_p == 1):
            txt += txt_t # 调试用
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
    answer = ""
    time_zero = time.strftime('%Y-%m-%d %H:%M:%S')
    
    chat_head = "<div align=\"left\"  style=\"font-size:20px\">"
    chat_head += "<div  style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">"
    chat_head += time_zero + "</div>"
    chat_head += "<div align=\"right\">" + q_p + "&nbsp&nbsp <img src=\""+  path_main +"statics/img/head_pat_1.gif\" border=0 alt=\"患者\" ></div><br><br>"
    
    what_is = 6 # 默认问题的初级语义分类
    
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
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_0.gif\" border=0 alt=\"引导\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 1):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_1.gif\" border=0 alt=\"诊断\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 2):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_2.gif\" border=0 alt=\"治疗\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 3):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_3.gif\" border=0 alt=\"知识\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 4):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_4.gif\" border=0 alt=\"预测\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 5):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_5.gif\" border=0 alt=\"费用\" >&nbsp&nbsp " + answer + "<br><br>"
    if (what_is == 6):
        chat_head += "<img src=\""+  path_main +"statics/img/head_doc_6.gif\" border=0 alt=\"其它\" >&nbsp&nbsp " + answer + "<br><br>"
    
    chat_head += "</div>"
    chat_head += """
    <HR style="FILTER: progid:DXImageTransform.Microsoft.Glow(color=#987cb9,strength=10)" width="100%" color=#cccccc SIZE=1>
    """
    
    #6 收尾处理，返回结果
    
    
    time_last = str(round(time_cost(time_start),2))
    chat_head += "<div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">本次对话,共耗时：" + time_last + " 秒。</div>"
    print(log_if)
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
    
    return chat_head
    
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