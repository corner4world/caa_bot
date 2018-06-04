#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"集体",
}
"初创时间:"2017年3月",
"性质":"对话处理引擎"
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块
import json # json控件
import random # 随机数

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件
from diy.inc_hash import hash_make #MD5函数
sys.path.append("..")
import config #系统配置参数

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区

# 对话的基础类
class Dialog_base(object):
    
    def __init__(self):
    
        pass
    
    # json格式文本从文本里获得结果字典
    def dic_txt_json(self,str_t=""):
    
        dic_t = {}
        
        try:
            dic_t = json.loads(str_t)
        except:
            pass
            
        return dic_t
    
    # json格式文本从文本里获得结果
    def result_txt_json(self,str_t="",name_p="n/a"):
    
        result_p = ""
        dic_t = self.dic_txt_json(str_t=str_t)
            
        if (dic_t):
            if (name_p in dic_t):
                result_p = dic_t[name_p]
                
        return result_p
        
    # 显示内部参数 测试用
    def show_dic_test(self,dic_t={}):
        
        for x in dic_t:
            print ("参数类名：",x,"值：",dic_t[x])

    # 比对词向量的构造
    def vector_cos_word(self,list_v1=[],list_v2=[]):
        
        list_v1_out = []
        list_v2_out = []
        list_b = list_v1 + list_v2
        list_s = sorted(set(list_b),key=list_b.index) # 去重排序
        
        #print(list_s,"\n",list_v1,"\n",list_v2) # 调试用
        
        for x in list_s:
        
            list_v1_out.append(list_v1.count(x))
            list_v2_out.append(list_v2.count(x))
                
        #print(list_s,list_v1_out,list_v2_out) # 调试用
                
        return list_v1_out,list_v2_out
            
    
    # 词向量余弦相似度计算
    def cos_word(self,sim_1=[],sim_2=[]):
    
        sim_value = -1 # 相似度值赋初值 1 完全相似 -1 完全相反
        epsilon = 10e-10
        pow_1 = 0
        pow_2 = 0
        inner_product = 0
        list_em = []  # 标准向量
        import math
        
        sim_1,sim_2 = self.vector_cos_word(list_v1=sim_1,list_v2=sim_2)
        #print(sim_1,sim_2)
        for i in range(len(sim_1)):
            #print(i) # 调试用
            inner_product += sim_1[i] * sim_2[i]
            pow_1 += sim_1[i]**2
            pow_2 += sim_2[i]**2
        #print ("inner_product=",inner_product**2,"pow_1*pow_2=",pow_1*pow_2)
        sim_value = round(inner_product/(math.sqrt(pow_1*pow_2)+epsilon),10) # 保留小数点后10位
        
        return sim_value
        
# 对话的日志类
class Dialog_log(object):
    
    # 获得文件大小，单位是MB
    def get_FileSize_mb(filePath="",code="utf8"):
        
        fsize =0
        try:
            fsize = os.path.getsize(filePath)
            fsize = fsize/float(1024*1024)
            fsize = round(fsize,2)
        except:
            pass
        return fsize

    # 读取历史对话
    def read_chatlist(self,path_p="",numb_chatlist_p=10,action=1):
    
        import linecache 
        dic_t = {}
        numb_lines = 0 # 历史资料行数
        fsize = 0 # 文件大小
        lines_0 = [] # 文件内容分行原始列表
        lines = [] # 文件内容分行最终列表
        # 获得文件大小
        try:
            fsize = os.path.getsize(path_p)
            fsize = fsize/float(1024*1024)
            fsize = round(fsize,2)
        except:
            pass
        #filesize = self.get_FileSize_mb(filePath=path_p,code="utf8")
        print ("对话历史文件大小：",fsize) # 调试用
        
        # 大于某阈值大小 逐行读取
        if (fsize > 128):
        
            with open(path_p, 'r',encoding='utf-8') as f:
                while True:
                    lines_0.append(f.readline())
                    if not line:
                        break
        
        # 默认一次性分行读取
        else:
        
            with open(path_p, 'r',encoding='utf-8') as f:
                lines_0 = f.readlines()
                
        # 倒排读取指定行数的数据
        if (action == 1):
            
            lines=lines_0[::-1] 
            numb_lines = len(lines)
            print ("历史资料行数",numb_lines)
            
            j = 1
            for x in lines:
                if (j > numb_chatlist_p):
                    break
                dic_t[j] = x
                j += 1
            
        return dic_t
            
    # 获得历史对话语料
    def get_chatlist(self,path_p="",numb_chatlist_p=10,dic_user={}):
        
        dic_t = {} # 结果字典
        name_csv_p = "" # 聊天记录文件名
        id = 0
        
        #print ("用户参数字典",dic_user) # 调试用
        if ("session" in dic_user):
            if (dic_user["session"]):
                name_csv_p = "_" + str(dic_user["session"]["id"])
                id = dic_user["session"]["id"]
            else:
                name_csv_p = hash_make(dic_user["remote_ip"] + dic_user["headers"]["User-Agent"])
                
        path_csv = path_p + name_csv_p + ".csv"
        print ("聊天历史文件路径：",path_csv,"文件是否存在：",os.path.exists(path_csv)) # 调试用
        if (os.path.exists(path_csv)):
            #print("读取最近",numb_chatlist_p,"条历史记录")
            dic_t = self.read_chatlist(path_p=path_csv,numb_chatlist_p=numb_chatlist_p,action=1)
        else:
            return dic_t,name_csv_p,id
        
        return dic_t,name_csv_p,id
        
    # 写入历史对话记录
    def save_chat_list(self,path_chat_list_p="",code_p="utf-8",content_p=""):
        
        with open(path_chat_list_p, "a+",encoding=code_p) as f:
            f.write(content_p)
    
    # 写入对话访问日志
    def save_visit_log(self,path_visit_log_p="",code_p="utf-8",content_p=""):
        
        with open(path_visit_log_p, "a+",encoding=code_p) as f:
            f.write(content_p)
            
# 对话渲染类
class Dialog_show(object):

    # web渲染 
    def web_show(self,q_p="",code_p="",dic_h="",time_zero="",time_cost=0,dialog_is=1,rot_is=6):
        
        chat_head = ""
        chat_foot = ""
        chat_main = ""
        txt = ""
        
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
        
        chat_main += "<div align=\"left\"  style=\"font-size:20px\">"
        chat_main += "<div  style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">"
        chat_main += time_zero + "</div>"
        chat_main += "<div align=\"right\">" + q_p + "&nbsp&nbsp <img src=\""+ config.dic_config["path_main"] +"statics/img/head_pat_1.gif\" border=0 alt=\"患者\" ></div><br><br>"
        chat_main += "<img src=\""+  config.dic_config["path_main"] +"statics/img/head_doc_" + str(rot_is)+ ".gif\" border=0 alt=\"回答\" >&nbsp&nbsp " + code_p + "<br><br>"
        chat_main += "</div>"
        
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
    
        if (dialog_is == 1):
            chat_foot += "<br>提示：您若还有其它问题,可以继续提问。" + form_ask # 加入尾部提问
    
        chat_foot += """
    <HR style="FILTER: progid:DXImageTransform.Microsoft.Glow(color=#987cb9,strength=10)" width="100%" color=#cccccc SIZE=1>
    """
    
        chat_foot += "<div style=\"height:32px;font-family: 微软雅黑;color:#cccccc;\">本次对话,共耗时：" + str(time_cost) + " 秒。</div>"
        chat_foot += "<div style=\"font-size:12px;font-family: 微软雅黑;color:#ff0000;\">敬请注意：智能问答不能代替线下执业医生的诊疗，以上结果应仅仅作为建议使用！</div>"
        
        txt = chat_head + chat_main + chat_foot
        
        return txt

# 对话主类
class Dialog (Dialog_base,Dialog_log, Dialog_show):
    
    # 问题预处理
    def pretreatment(self,q_p="",action_p="seg"):
        
        str_t = ""
        dic_p = {}
        url_p = config.dic_config["url_api"] + "api"
        values = {
                "action":action_p,
                "q":q_p
                    }
        try:
            dic_p = json.loads(inc_crawler_fast.get_html_post(url_p,values))
        except:
            pass
            
        return dic_p
        
    # 意图识别
    def intent_is(self,dic_p={},action_p="gossip"):
    
        result_p = ""
        
        if (action_p == "gossip"):
            url_p = config.dic_config["url_api"] + "api"
            values = {
                "action":"cf_lr_gossip",
                "q":dic_p["segment"]
                    }
            #print (url_p,values) #调试用
            try:
                txt_json = inc_crawler_fast.get_html_post(url_p,values)
            except:
                pass
            if (txt_json != ""):
                result_p = self.result_txt_json(str_t=txt_json,name_p="classify")
                
            return result_p
            
        return result_p
        
    # 话语权状态识别
    def initiative_is(self,dic_p={}):
        result_p = ""
        return result_p
        
    # 反问识别
    def query_is(self,dic_p={}):
        result_p = ""
        return result_p
        
    # 指令识别
    def order_is(self,dic_p={}):
        result_p = ""
        return result_p
        
    # 指令安全权限识别
    def order_power_is(self,dic_p={}):
        result_p = ""
        return result_p
        
    # 所有意图模式匹配失败的补丁
    def answer_nothing_bug(self,dic_p={}):
        
        result_p = ""
        
        if (dic_p):
            result_p = dic_p[random.randrange(1,len(dic_p))]
            
        return result_p
        
    # 通过命名实体字典 打闲聊意图识别错误的补丁
    def gossip_bug_ner(self,q_p="",dic_ner_1={},dic_ner_2={}):
        
        gossip_if = True
        
        for x in dic_ner_1:
            if (x.strip() in q_p):
                gossip_if = False
                return gossip_if
                
        for x in dic_ner_2:
            if (x.strip() in q_p):
                gossip_if = False
                return gossip_if
                
        return gossip_if
        
    # 简单问候语识别
    def hello_is(self,dic_p={},dic_hello={}):
        
        txt = ""
        
        for x in dic_p:
            if (x in dic_hello):
                txt = dic_hello[x]
                break
                
        return txt
        
    # 闲聊非索引SQL直接匹配
    def answer_noindex(self,dic_m={},conn_p=""):
    
        code_p = ""
        sql_head = ""
        sql_where = ""
        sql_foot = ""
        sql = ""
        url_p = config.dic_config["url_api"] + "api"
        values = {
                "action":"pseg",
                "q":dic_m["question"]
                    }
        txt_json = ""
        try:
            txt_json = inc_crawler_fast.get_html_post(url_p,values)
        except:
            pass
        if (txt_json != ""):
            dic_m["pseg"] = self.dic_txt_json(str_t=txt_json)
        #print ("词性标注",dic_m["pseg"]) #调试用
        
        # 按词性 进行简单礼貌语判别
        if (dic_m["pseg"]):
            i = 1
            for x in dic_m["pseg"]:
                print (dic_m["pseg"][str(i)]) # 调试用
                if (dic_m["pseg"][str(i)]["pseg"] == "a" or dic_m["pseg"][str(i)]["pseg"] == "v" or dic_m["pseg"][str(i)]["pseg"] == "l" or dic_m["pseg"][str(i)]["pseg"] == "i" or "n" in dic_m["pseg"][str(i)]["pseg"]):
                    dic_m["list_search"].append(dic_m["pseg"][str(i)]["name"])
                i +=1
            print ("待查询队列",dic_m["list_search"])
            
        if (dic_m["list_search"]):
            
            # 闲聊语料判别
            if (dic_m["intent"]["gossip"] == 1):
                table_name_p = "qa_gossip"
                
            # 实质性问题知识库判别
            if (dic_m["intent"]["gossip"] == 0):
                table_name_p = "qa"
                
            row_name_p = "question"
            sql_head = "select question,answer from " + table_name_p + " "
            sql_foot = " order by LENGTH(question),LENGTH(answer),rand() limit 1"
            
            for x in dic_m["list_search"]:
                sql_where += " " + row_name_p + " like '%" + x + "%' and"
            if (sql_where != ""):
                sql_where = sql_where[:-3]
                sql_where += " and answer is not null"
                sql_where = "where " + sql_where
                sql = sql_head + sql_where + sql_foot
            res_p,rows_p = conn_p.read_sql(sql)
            
            # 闲聊问答语料表的问题部分能满足匹配条件
            if (res_p > 0):
            
                code_p = rows_p[0][1]
            
            else:
                # 匹配闲聊问答语料表的答案部分
                row_name_p = "answer"
                sql_where = ""
                for x in dic_m["list_search"]:
                    sql_where += " " + row_name_p + " like '%" + x + "%' and"
                if (sql_where != ""):
                    sql_where = sql_where[:-3]
                    sql_where += " and answer is not null"
                    sql_where = "where " + sql_where
                    sql = sql_head + sql_where + sql_foot
                    res_p,rows_p = conn_p.read_sql(sql)
                    if (res_p > 0):
                        code_p = rows_p[0][1]
                    else:
                        # 未成功 改为宽松 匹配
                        sql_where = ""
                        for x in dic_m["list_search"]:
                            sql_where += " " + row_name_p + " like '%" + x + "%' or"
                        if (sql_where != ""):
                            sql_where = sql_where[:-3]
                        sql_where += " and answer is not null"
                        sql_where = "where " + sql_where
                        sql = sql_head + sql_where + sql_foot
                        res_p,rows_p = conn_p.read_sql(sql)
                        if (res_p > 0):
                            code_p = rows_p[0][1]
        #print("最后匹配的问题",rows_p[0][0],"最后生效的匹配查询",sql) # 调试用
        return code_p
        
    # -------- 关键词索引 + 语义相似 为核心的匹配算法方法函数
    def answer_index_similar(self,dic_m={},conn_1="",conn_2="",code_out=1,order_is="rank,x0,x1,x2,x3"):
        pass
    
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