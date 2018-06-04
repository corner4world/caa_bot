#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
搜索功能模块
'''

# --- 模块载入
import sys
import os
import re
import chardet
from enum import Enum, unique
import random
import datetime
import math # 引入数学计算模块

sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块
from diy.inc_conn import * #自定义数据库功能模块 已内置引用config模块 无需重复引用

rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
#rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
# --- 核心类

# 基础搜索对象
class Search_base(object):

    def __init__(self):
        self.in_list=['顾问','咨询','主管','经理','医生','老师','主任','工程师','助理','客服','总监','专员','热线','人员','分析师','文员','负责人','督导','代表','跟单','护士','店员','校长','研发','接听','董事','文案','销售','研究员','接待','教师','方面','服务','技术员','运营','售前','招生','组长','岗位','总裁','编辑','员工','合伙人','咨询官','会计','秘书','审计','部长','统计师','红娘','讲师','工单','导员','策划师','文案','培训生','官员','建岗','干部','公司','翻译','律师','复核','专家','设计','管理','陪训师','实习生','经纪人','教务','医师','分析员','培训生','讲解','导师','业务','夜班','中医','总监']
        self.place_foot_list = ['丘','东','中','义','乐','乡','亚','京','亭','什','仁','余','作','依','元','充','克','关','兴','冈','凉','凌','则','化','北','区','华','南','博','卫','原','县','口','古','台','吉','同','名','图','圈','地','圳','坊','坝','城','埠','堰','壁','夏','头','威','子','孜','宁','安','宏','定','宾','密','封','尔','尾','山','岗','岛','岩','岭','峡','峰','川','州','左','市','布','平','庄','庆','底','店','康','建','德','徽','志','忠','感','拉','掖','斯','新','方','施','旗','昌','明','春','曲','松','林','架','树','桃','桥','梁','楞','水','汉','江','池','汾','沂','沙','沧','河','治','泉','波','泰','泽','洛','津','洱','洲','浮','海','清','渠','港','湖','湾','源','溪','滨','潭','澳','照','熟','特','犁','理','田','界','番','疆','盟','眉','石','穴','纳','肃','肥','色','节','芜','芝','花','苏','茅','莞','营','萨','藏','西','贡','边','辽','达','迁','迈','远','连','通','郸','都','里','银','锡','锦','镇','门','阳','阴','陵','雄','靖','顺','饶','马','高','鸡','齐']
        self.numb_kwd_long = 32 #超长文本阈值
        self.numb_kwd_cut = 8 #自然分词阈值
        self.numb_dot = 20 # 知识点取样阈值
        self.numb_table = 6 # 最大并表阈值
        self.judger = SalaryJudger()
    
    # 列表去重
    def list_nosame(self,list_p=[]):
        list_t = []
        for x in list_p:
            if (not x in list_t):
                    list_t.append(x)
        return list_t
        
    # 短查询词是什么
    def kwd_what_is_short(self,list_p,in_list_p=[],place_foot_list=[]):
        
        dic_k = {}
        
        if (not in_list_p):
            in_list_p = self.in_list
        if (not place_foot_list):
            place_foot_list = self.place_foot_list
        
        # --- 判别循环开始
        
        for y in list_p:
        
            #单个字支持的补丁
            if (len(y) == 1):
                if y.isdigit():
                    pass
                else:
                    sql = "select job from page where job like '%" + y + "%' order by power desc limit 1"
                    res, rows = rs_basedata_mysql.read_sql(sql)
                    if (res > 0):
                        dic_k[rows[0][0]] = "job"
                        return dic_k
        
            skip_if = False
            str_t = str(y)
            numb_t = len(str_t)
            if (str_t == ""):
                continue
            
            # 职业校验
            for x in in_list_p:
                if (x in str_t):
                    
                    if (not str_t in dic_k):
                        dic_k[str_t] = "job"
                        skip_if = True
                        break
                        
            if (skip_if):
                continue
            
            # 地点校验
            for x in place_foot_list:
                
                if (x in str_t[-1]):
                    if (not str_t in dic_k):
                        dic_k[str_t] = "place"
                        skip_if = True
                        break
            
            if (skip_if):
                continue
                
            # 薪酬校验
            str_t = self.cn2dig(str_t)
            str_t = str_t.replace("K","000")
            str_t = str_t.replace("k","000")
            try:
                str_t = self.judger.salary_judge(str_t)
                
            except:
                str_t = False
                
            if (str_t):

                if isinstance(str_t,int):
                    tuple_t = (str_t,str_t)
                    if (not tuple_t in dic_k):
                        dic_k[tuple_t] = "pay"
                else:
                    if (not str_t in dic_k):
                        dic_k[str_t] = "pay"
            
        # --- 判别循环结束
        
        return dic_k
    
    # 自然分割
    def cut_nature(self,str_t,ignore_list=[]):
        
        #str_t = str_t.replace(".","~@~")
        #str_t = str_t.replace("-","~@~")
        #str_t = str_t.replace("/","~@~")
        str_t = str_t.replace(" ","~@~")
        str_t = str_t.replace("'","~@~")
        str_t = str_t.replace("\n","~@~")
        str_t = str_t.replace("\"","~@~")
        str_t = str_t.replace(",","~@~")
        str_t = str_t.replace("（","~@~")
        str_t = str_t.replace("）","~@~")
        str_t = str_t.replace("(","~@~")
        str_t = str_t.replace(")","~@~")
        str_t = str_t.replace("，","~@~")
        str_t = str_t.replace("。","~@~")
        str_t = str_t.replace("；","~@~")
        str_t = str_t.replace("“","~@~")
        str_t = str_t.replace("”","~@~")
        str_t = str_t.replace("（","~@~")
        str_t = str_t.replace("）","~@~")
        str_t = str_t.replace("？","~@~")
        str_t = str_t.replace("：","~@~")
        str_t = str_t.replace("《","~@~")
        str_t = str_t.replace("》","~@~")
        str_t = str_t.replace("『","~@~")
        str_t = str_t.replace("』","~@~")
        str_t = str_t.replace("[","~@~")
        str_t = str_t.replace("]","~@~")
        str_t = str_t.replace("！","~@~")
        str_t = str_t.replace("、","~@~")
        str_t = str_t.replace(" ","~@~")
        str_t = str_t.replace("\\","~@~")
        str_t = str_t.replace("=","~@~")
        str_t = str_t.replace("×","~@~")
        str_t = str_t.replace("÷","~@~")
        str_t = str_t.replace("+","~@~")
        str_t = str_t.replace("≈","~@~")
        str_t = str_t.replace("【","~@~")
        str_t = str_t.replace("】","~@~")
        str_t = str_t.replace("〖","~@~")
        str_t = str_t.replace("〗","~@~")
        str_t = str_t.replace("[","~@~")
        str_t = str_t.replace("]","~@~")
        str_t = str_t.replace("｛","~@~")
        str_t = str_t.replace("｝","~@~")
        str_t = str_t.replace("?","~@~")
        str_t = str_t.replace("±","~@~")
        str_t = str_t.replace("≌","~@~")
        str_t = str_t.replace("∽","~@~")
        str_t = str_t.replace("∪","~@~")
        str_t = str_t.replace("∩","~@~")
        str_t = str_t.replace("∈","~@~")
        str_t = str_t.replace("\r\n", "~@~")
        str_t = str_t.replace("\n","~@~")
        str_t = str_t.replace("\r","~@~")
        str_t = str_t.replace("  ","~@~")
        str_t = str_t.replace("|","~@~")
        str_t = str_t.replace("_","~@~")
        #停用词初滤
        for x in ignore_list:
            str_t = str_t.replace(x,"")
        
        list_last = str_t.split("~@~")
        return list_last
    # 中文数字转阿拉伯数字
    def cn2dig(self,str_t):
        dic_numb = {
        u'〇' : "0",
        u'一' : "1",
        u'二' : "2",
        u'三' : "3",
        u'四' : "4",
        u'五' : "5",
        u'六' : "6",
        u'七' : "7",
        u'八' : "8",
        u'九' : "9",
        u'零' : "0",
        u'壹' : "1",
        u'贰' : "2",
        u'叁' : "3",
        u'肆' : "4",
        u'伍' : "5",
        u'陆' : "6",
        u'柒' : "7",
        u'捌' : "8",
        u'玖' : "9",
        u'貮' : "2",
        u'两' : "2",
        u'十' : "0",
        u'拾' : "0",
        u'百' : "00",
        u'佰' : "00",
        u'千' : "000",
        u'仟' : "000",
        u'万' : "0000",
        u'萬' : "0000",
        u'亿' : "00000000",
        u'億' : "00000000",
        u'兆' : "000000000000",
        }
        
        for x in dic_numb:
            str_t = str_t.replace(x,dic_numb[x])
        
        return str_t
    
    
    # 查询的结果渲染
    def show_fit(self,rows_p=(),action_p="fit"):

        txt = ""
        dic_c = {}
        numb_max = 0
        job_last = ""
        if (not rows_p):
            return txt,job_last
        
        #1 --- 精确查找结果渲染开始 ---
        if (action_p == "fit"):
            
            for row in rows_p:
                #print (row) # 调试用
                if row[1] in dic_c:
                    dic_c[row[1]][0] += 1
                    dic_c[row[1]][1].append(row[0])
                    dic_c[row[1]][2] += row[2]
                    dic_c[row[1]][3] += row[3]
                    dic_c[row[1]][4].append(row[4])
                else:
                    dic_c[row[1]] = [1,[row[0]],row[2],row[3],[row[4]]]
                
            numb_t = len(rows_p)
            numb_d = len(dic_c)
        
            # 回归聚类 
            for x in dic_c:
                if (dic_c[x][0] > numb_max):
                    numb_max = dic_c[x][0]
                    job_last = x
                
            # 最终渲染
            name_job_last = job_last
            
            pay1_last = int(dic_c[job_last][2]/numb_max/100)*100
            pay2_last = int(dic_c[job_last][3]/numb_max/100)*100
            
            #薪酬缺失的补丁
            if ( pay1_last == 0 and pay2_last > 0):
                pay1_last = int(pay2_last*0.6785/100)*100
            if ( pay2_last == 0 and pay1_last > 0):
                pay2_last = int(pay1_last*0.6785/100)*100
            
            txt += "为您找到最佳匹配职位：【 <font style=\"font-size:28px;color: #3D7DC7;\">" + name_job_last + "</font> 】<br><br>"
            txt += "参考薪酬：<font color=\"#f54916\">￥</font><font style=\"font-size:55px;color: #f54916;font-family:\"Arial Black\", Gadget, sans-serif;\">" + str(pay1_last) + "-" + str(pay2_last) + "</font> 元/月  <br><br>"
        
            dic_p = {}
            for y in dic_c[job_last][4]:
                if (not y in dic_p):
                    dic_p[y.replace("-","")] = y
            if(dic_p):
                txt += "参考工作地点："
                str_t = ""
                for z in dic_p:
                    str_t += z + " - "
                txt += str_t[0:-2]
                
        # ---精确查找渲染结束---
        
        #2 --- 模糊查找结果渲染开始 ---
        
        if (action_p == "like"):
            
            for row in rows_p:
                #print (row) # 调试用
                if row[2] in dic_c:
                    dic_c[row[2]][0] += 1
                    dic_c[row[2]][1].append(row[2])
                    dic_c[row[2]][2] += row[3]
                    dic_c[row[2]][3] += row[4]
                    dic_c[row[2]][4].append(row[5])
                else:
                    dic_c[row[2]] = [1,[row[0]],row[2],row[3],[row[4]]]
                
            numb_t = len(rows_p)
            numb_d = len(dic_c)
        
            # 回归聚类 
            for x in dic_c:
                if (dic_c[x][0] > numb_max):
                    numb_max = dic_c[x][0]
                    job_last = x
            sql = "select job from result_job where id=" + str(job_last)
            print (sql) #调试用
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                name_job_last = rows[0][0]
            else:
                name_job_last = "综合模型"
            # 最终渲染
            pay1_last = int(dic_c[job_last][2]/numb_max/100)*100
            pay2_last = int(dic_c[job_last][3]/numb_max/100)*100
            
            #薪酬缺失的补丁
            if ( pay1_last == 0 and pay2_last > 0):
                pay1_last = int(pay2_last*0.6785/100)*100
            if ( pay2_last == 0 and pay1_last > 0):
                pay2_last = int(pay1_last*0.6785/100)*100
            
            txt += "为您找到最佳匹配职位：【 <font style=\"font-size:28px;color: #3D7DC7;\">" + name_job_last + "</font> 】<br><br>"
            txt += "参考薪酬：<font color=\"#f54916\">￥</font><font style=\"font-size:55px;color: #f54916;font-family:\"Arial Black\", Gadget, sans-serif;\">" + str(pay1_last) + "-" + str(pay2_last) + "</font> 元/月  <br><br>"
            
            sql = "select place from result_place where "
            dic_p = {}
            for y in dic_c[job_last][4]:
                sql += " id=" + str(y) + " or"
            sql = sql[0:-2]
            print (sql) #调试用
            res, rows = rs_basedata_mysql.read_sql(sql)
            
            if(res >0):
                
                txt += "参考工作地点："
                str_t = ""
                for row in rows:
                    str_t += row[0] + " - "
                txt += str_t[0:-2]
                
        # ---模糊查找渲染结束---
        
        #print (dic_c) # 调试用
        return txt,name_job_last
        
    # 数据库列表转字符串
    def db_list_to_str(self,str_t=""):
        txt = ""
        str_t = str_t.strip()
        try:
            list_t = eval(str_t)
        except:
            pass
        if (list_t):
            for x in list_t:
                if (x != ""):
                    txt += x + " "
        return txt
    
    # 具体知识点渲染
    def show_dot(self,dot_p=""):
        
        txt = ""
        str_t = ""
        list_t = []
        
        if (dot_p == ""):
            txt += "知识点名称不能为空！"
        #读取数据
        sql = "select url_hash,url_main,title from page where job = '" + dot_p + "'"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
        
            sql = "select url_hash,url_main,title from page where url_hash = '" + dot_p + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res < 1):
                txt = "知识点不存在或数据库传输错误！"
                return txt
        
        url_hash = rows[0][0]
        url_main = rows[0][1]
        title = rows[0][2]
        
        sql_head = "select "
        sql_head += "information_sources," #0 数据源值
        sql_head += "where_work," #1 地点
        sql_head += "work_experience," #2工作经验
        sql_head += "education_minimum," #3 最低学历
        sql_head += "company_scale," #4 公司规模
        sql_head += "company_nature," #5 公司属性
        sql_head += "date_release,"  #6 发布时间
        sql_head += "job_description," #7 职位描述
        sql_head += "position_title," #8 职位
        sql_head += "label, " #9 待遇标签
        sql_head += "job_month_pay, " #10 月薪
        sql_head += "work_nature, " #11 工作性质
        sql_head += "recruiters_numb, " #12 招聘人数
        sql_head += "company, " #13 参考用人单位
        sql_head += "company_introduction " #14 参考公司介绍
        sql_data = " from struct "
        sql_where = " where url_hash ='" + url_hash + "'"
        sql = sql_head + sql_data + sql_where
        
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            txt = "知识点结构化信息不存在或数据库传输错误！"
            return txt
            
        txt += """
        <div align=\"left\">
        <div class="fixed-inner-box">
            <div class="inner-left fl">
            <br><br><br>
                <div><b>参考职位名：</b>
        """
        
        txt += title.replace("[","").replace("]","").replace("'","") #参考职位名
        
        txt += """
            </div>
                <div style="width:683px;" class="welfare-tab-box"><b>待遇标签：</b>
            """
        
        # 待遇标签处理
        if (rows[0][9]):
            txt += self.db_list_to_str(str_t=rows[0][9])
        
        txt += """
            
            <div class="inner-right fr">
                
                <button style="display:none;" class="now-apply" onclick="zlzp.searchjob.ajaxApplyBrig3('1');dyweTrackEvent('bjobsdetail14gb','directapply_top_right');" id="applyVacButton2" title="申请职位"></button>
                
            </div>
        </div>
    </div>
    <div>
        <div class="terminalpage-left">
            <ul class="terminal-ul clearfix">
            """
        if (rows[0][10]):
            str_t = self.db_list_to_str(str_t=rows[0][10])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考月薪：</strong></span>" + str_t + "</li>"
        if (rows[0][1]):
            str_t = self.db_list_to_str(str_t=rows[0][1])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考地点：</strong></span>" + str_t + "</li>"
        if (rows[0][6]):
            str_t = self.db_list_to_str(str_t=rows[0][6])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>发布日期：</strong></span>" + str_t + "</li>"
        if (rows[0][11]):
            str_t = self.db_list_to_str(str_t=rows[0][11])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考工作性质：</strong></span>" + str_t + "</li>"
        if (rows[0][2]):
            str_t = self.db_list_to_str(str_t=rows[0][2])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考工作经验：</strong></span>" + str_t + "</li>"
        if (rows[0][3]):
            str_t = self.db_list_to_str(str_t=rows[0][3])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考最低学历：</strong></span>" + str_t + "</li>"
        if (rows[0][12]):
            str_t = self.db_list_to_str(str_t=rows[0][12])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考招聘人数：</strong></span>" + str_t + "</li>"
        if (rows[0][8]):
            str_t = self.db_list_to_str(str_t=rows[0][8])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<li><span><strong>参考职位性质：</strong></span>" + str_t + "</li>"
        txt += """
            </ul>
            <div class="terminalpage-main clearfix">
            <div class="tab-cont-box">
            <div class="tab-inner-cont">
            """
        if (rows[0][7]):
            str_t = self.db_list_to_str(str_t=rows[0][7])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<p><strong>参考资料：</strong></p><p align=\"left\">" + str_t + "</p>"

        txt += """
                    </div>
                </div>
            </div>
        <div >
            <div >
                """
        if (rows[0][13]):
            str_t = self.db_list_to_str(str_t=rows[0][13])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<p><strong>参考用人单位：</strong>" + str_t + "</p> "
        if (rows[0][4]):
            str_t = self.db_list_to_str(str_t=rows[0][4])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<p><strong>参考公司规模：</strong>" + str_t + "</p> "
        if (rows[0][5]):
            str_t = self.db_list_to_str(str_t=rows[0][5])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<p><strong>参考公司属性：</strong>" + str_t + "</p> "
        if (rows[0][14]):
            str_t = self.db_list_to_str(str_t=rows[0][14])
            str_t = str_t.strip()
            str_t = str_t.replace("\\x0a","")
            txt += "<p><strong>参考公司介绍：</strong></p><p align=\"left\">" + str_t + "</p> "
        txt +="<p></p><p><strong>参考网址：</strong><a href=\"" + url_main + "\" target=\"_blank\"><u>" + url_main + "</u></a></p>"
        txt += """
                        </strong>
                    </li>
                </ul>
            </div>
        </div>
    </div>
        """
        return txt
        
    # 知识点分页搜索渲染
    def show_page(self,sql_last_p="",page_p=1):
        
        time_start = datetime.datetime.now() #初始时刻
        txt = ""
        list_t = []
        str_t = ""
        sql_last_p = secret_ldae(sql_last_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="no")
        sql = sql_last_p.split("limit")[0]
        res = 0
        numb_all = 0 #所有记录数
        numb_visit = 0 #已经访问数
        kwd_p = ""

        
        if (page_p == 1):
        
            str_t = sql.split(" from ")[1][0:2]
            str_t = str_t.strip()
            # 直接查找
            if (str_t == "pa"):
                res, rows = rs_basedata_mysql.read_sql(sql)
            # 索引查找
            if (str_t == "z"):
                res, rows = rs_index_mysql.read_sql(sql)
            if (res < 1):
                txt += "知识库无记录或数据读取失败..."
                return txt
            else:
                numb_all = res
            sql_last_p = sql + " limit " + str(numb_all)
            
        if page_p > 1:
            numb_all = sql_last_p.split("limit")[1]
            numb_all = numb_all.strip()
            numb_all = int(numb_all)
        
        sql_last_p = sql_last_p = secret_ldae(sql_last_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
        

        sql += " limit "+ str(int(config.dic_config["max_per_page"])*(page_p-1)) + "," + config.dic_config["max_per_page"]
        
            
        # 正式分页查找
        str_t = sql.split(" from ")[1][0:2]
        str_t = str_t.strip()
        # 直接查找
        if (str_t == "pa"):
            res, rows = rs_basedata_mysql.read_sql(sql)
        # 索引查找
        if (str_t == "z"):
            res, rows = rs_index_mysql.read_sql(sql)
            
        
        if (res < 1):
            txt += "知识库无记录或数据读取失败..."
            return txt
        
        # 记录提示渲染
        numb_visit = int(config.dic_config["max_per_page"])*(page_p-1)
        txt += "<br><br>"
        txt += "<div width=\"528\" align=\"left\"><font color=\"#8e8e8e\">有 " + str(numb_all-numb_visit) + " 条记录可查看 第 " + str(page_p) + " 页</font></div>"
        txt += "<div><br></div>"
        print (sql) # 调试用
        for row in rows:
        
            sql = "select title,content,url_main,pay1,pay2,place,url_hash,tf_idf,job from page where id=" + str(row[0])
            res_t, rows_t = rs_basedata_mysql.read_sql(sql)
            if (res_t > 0):
            
                job_p = rows_t[0][6]
                job_p = job_p.strip()
                job_p = secret_ldae(job_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
                
                txt += "<div width=\"558\" align=\"left\"><h3>"
                
                txt += "<a href=\"search?job=" + job_p + "&action=show_dot\" target=\"_blank\">"
                txt += "<font style=\"font-size:15px;font-weight:bold\" color=\"#0570B4\">" + rows_t[0][0][2:-2] + "</font></a>&nbsp;&nbsp;&nbsp;"
                
                kwd_p = rows_t[0][0][2:-2] + " " + str(rows_t[0][3]) + " - " + str(rows_t[0][4])
                
                # 职位 + 薪酬 组合相关搜索
                kwd_p = rows_t[0][8] + " " + str(rows_t[0][3]) + " - " + str(rows_t[0][4])
                kwd_p = secret_ldae(kwd_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
                txt += "<a href=\"search?job=" + kwd_p + "&action=default\" target=\"_blank\">"
                txt += "<font style=\"font-size:17px;font-weight:bold\" color=\"#F54916\">" + str(rows_t[0][3]) + " - "
                txt += str(rows_t[0][4]) + "</font></a>&nbsp;&nbsp;&nbsp;"
                
                # 职位 + 地点 组合相关搜索
                kwd_p = rows_t[0][8] + " " + rows_t[0][5].replace("-","")
                kwd_p = secret_ldae(kwd_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
                txt += "<a href=\"search?job=" + kwd_p + "&action=default\" target=\"_blank\">"
                txt += "<font style=\"font-size:12px;font-weight:bold\" color=\"#E7CB82\">" + rows_t[0][5] + "</font></a>&nbsp;&nbsp;&nbsp;"
                txt += "</h3></div>"
            
            #摘要内容的处理
            str_t = rows_t[0][1]
            str_t = str_t.replace("["," ").replace("]"," ").replace("'","").replace(","," ").replace("\\xa0","")
            try:
                list_t = eval(rows_t[0][7])
            except:
                pass

            if (list_t):
            
                list_mark = []
                numb_stop = random.randint(3,int(len(list_t)/2))
                str_t = str_t[0:256]
                
                i = 1
                for x in list_t:
                    
                    str_t = str_t.replace(x[0],"<font color=\"#cc0000\">" + x[0] + "</font>")
                    i += 1
                    if (i > numb_stop):
                        break
                
            else:
                str_t = str_t[0:256]
            txt += "<div width=\"528\" height=\"235\" align=\"left\"><font style=\"font-size:12px;\" color=\"#666666\">" + str_t + "......</font></div>"
            txt += "<div width=\"528\" height=\"35\" align=\"left\"><a href=\"" + rows_t[0][2] + "\" target=\"_blank\"><font style=\"font-size:12px;\" color=\"#81c382\">" + rows_t[0][2] + "</font></a>"
            txt += " - <a href=\"statics\\dot_html\\" + rows_t[0][6] + ".html\" target=\"_blank\"><font style=\"font-size:12px;\" color=\"#4783C9\">快照</font></a>"
            
            txt += " - <a href=\"/search?url_hash=" + rows_t[0][6] + "&action=divine\" target=\"_blank\"><font style=\"font-size:12px;\" color=\"#6BC9EF\">预测</font></a>"
            txt += " - <a href=\"/search?url_hash=" + rows_t[0][6] + "&action=knowledge\" target=\"_blank\"><font style=\"font-size:12px;\" color=\"#D36FB7\">知识</font></a> -"
            txt += "</div>"
            
            txt += "<div><br></div>"
        
        txt += "<div width=\"528\" height=\"235\" align=\"center\"><font color=\"#cccccc\">本次执行耗时：" + str(time_cost(time_start)) + " 秒</font></div>"
        txt += "<div width=\"528\" height=\"235\" align=\"center\"><br>"
        
        
        if (page_p > 1):
            txt += "<a href=\"search?sql_last=" + sql_last_p + "&action=show_page&page=" + str(page_p - 1)+ "\">上一页</a>&nbsp;&nbsp;&nbsp;&nbsp;"
        if (numb_all > numb_visit and numb_all > int(config.dic_config["max_per_page"])):
            txt += "<a href=\"search?sql_last=" + sql_last_p + "&action=show_page&page=" + str(page_p + 1)+ "\">下一页</a>"
        
        txt +="</div>"
        return txt
    
    # 更多链接
    def link_more(self,dic_p={}):
        
        # get方式的加解密处理
        job_p = dic_p["job"]
        job_p = secret_ldae(job_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
        sql_last_p = dic_p["sql_last"]
        sql_last_p = secret_ldae(sql_last_p,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="yes")
        
        txt = ""
        txt += "<ul id=\"nav\">" 
        txt += "<li class=\"menu\">"
        txt += "<div class=\"title\" align =\"right\"><font color=\"#cccccc\">更多功能</font>&nbsp;&nbsp;&nbsp;&nbsp;</div>"
        txt += "<dl class=\"submenu\">"
        txt += "<dd>"
        txt += "<a href=\"search?job=" + job_p + "&action=show_dot\" target=\"_blank\">参考职位</a>&nbsp;&nbsp;&nbsp;&nbsp;<br>"
        txt += "<a href=\"search?job=" + job_p + "&action=divine\">薪酬预测</a>&nbsp;&nbsp;&nbsp;&nbsp;<br>"
        txt += "<a href=\"search?job=" + job_p + "&action=knowledge\">相关知识</a>&nbsp;&nbsp;&nbsp;&nbsp;<br>" 
        txt += "<a href=\"search?sql_last=" + sql_last_p + "&action=show_page\">相关职位</a>&nbsp;&nbsp;&nbsp;&nbsp;<br>"
        txt += "<a href=\"search?job=" + job_p + "&action=vip\">VIP功能</a>&nbsp;&nbsp;&nbsp;&nbsp;<br>"
        txt += "</dd>"
        txt += "</dl>"
        txt += "</li>"
        
        return txt
        
    # 短词的索引查询
    def kwd_index_what_short(self,list_p,seg_p):
        
        list_w = []
        if (not list_p):
            return list_w
            
        for str_t in list_p:
            
            sql = "select keyword_hash,idf from index_main where keyword='" +  str_t + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            
            if (res > 0):
                list_w.append([rows[0][0],rows[0][1],1])
            else:
                    
                arr_t = seg_p.cut(str_t) #分词

                if (arr_t):
                
                    for y in arr_t:
                        
                        sql = "select keyword_hash,idf from index_main where keyword='" + y + "'"
                        res, rows = rs_basedata_mysql.read_sql(sql)
                        if (res > 0 and len(y) > 1):
                            list_w.append([rows[0][0],rows[0][1],1])
                            print ("索引精确匹配关键词：",y,rows[0][0],rows[0][1]) #调试用
                        else:
                            sql = "select keyword_hash,idf from index_main where keyword like '%" + y + "%' order by idf desc limit 1"
                            res, rows = rs_basedata_mysql.read_sql(sql)
                            if (res > 0 and len(y) > 1):
                                list_w.append([rows[0][0],rows[0][1],1])
                                print ("索引模糊匹配关键词：",y,rows[0][0],rows[0][1]) #调试用
                                
        #print ("待选词队列",list_w) #调试用
        return list_w #函数结束
        
    # 精确查询
    def find_fit(self,dic_p,numb_dot=0):
        if (numb_dot == 0):
            numb_dot = self.numb_dot
        txt = ""
        dic_f = {}
        res = 0
        sql_last = ""
        
        sql_head = "select id,job,pay1,pay2,place from page "
        sql_where = ""
        sql_order = " order by power desc "
        sql_limit = " limit " + str(numb_dot)
        
        for x in dic_p:
            if (dic_p[x] == "job"):
                sql_where += " job ='" + x + "' and "
            if (dic_p[x] == "place"):
                sql_where += " place like '-" + x + "-' and "
            if (dic_p[x] == "pay"):
                if (x[1] > x[0]):
                    sql_where += " ( pay1='" + str(x[0]) + "' and pay2 ='" + str(x[1]) + "') and "
                else:
                    sql_where += " ( pay1='" + str(x[0]) + "' or pay2 ='" + str(x[1]) + "') and "
        
        if (sql_where != ""):
            sql_where = " where " + sql_where
            sql_where = sql_where[0:-4]
            
            sql = sql_head + sql_where + sql_order + sql_limit
            res, rows = rs_basedata_mysql.read_sql(sql)
        
        # 直接精确查询无效转直接模糊查询
        if (res < 1 ):
            
            sql_where = ""
            
            for x in dic_p:
                if (dic_p[x] == "job"):
                    sql_where += " job like'%" + x + "%' and "
                if (dic_p[x] == "place"):
                    sql_where += " place like '%" + x + "%' and "
                if (dic_p[x] == "pay"):
                    x1 = str(int(x[0]*0.762))
                    x2 = str(int(x[0]*1.238))
                    x3 = str(int(x[1]*0.762))
                    x4 = str(int(x[1]*1.238))
                    if (x[1] > x[0]): 
                        sql_where += " ( ( pay1 > " + x1 + " and pay1 < " + x2 + ") and ( pay2 > " + x3 + " and pay2 < "  + x4 + ") ) and "
                    else:
                        sql_where += " ( pay1 > " + str(x1) + " and pay1 < " + str(x2) + ") or (pay2 > " + str(x3) + " and pay2 < "  + str(x4) + ") ) and "
        
            if (sql_where != ""):
                sql_where = " where " + sql_where
                sql_where = sql_where[0:-4]
                
                sql = sql_head + sql_where + sql_order + " limit " + str(numb_dot)
                res, rows = rs_basedata_mysql.read_sql(sql)
        #print (sql) # 调试用
        if (res > 0):
            sql_last = sql
        
        #print (sql_last) # 调试用
        return rows,sql_last
        
    #模糊查询
    def find_like(self,list_p,numb_kwd_cut=0,numb_table=0,numb_dot=0,page_p=0):
        
        if (numb_kwd_cut == 0):
            numb_kwd_cut = self.numb_kwd_cut
        if (numb_table == 0):
            numb_table = self.numb_table
        if (numb_dot == 0):
            numb_dot = self.numb_dot
            
        txt = ""
        dic_f = {}
        res = 0
        rows_p = ()
        sql_last = ""
        dic_w = {}
        dic_w_t = {} #分词临时数组
        list_w = []
        list_t = []
        sql = ""
        sql_head = ""
        sql_data = ""
        sql_where = ""
        sql_order = ""
        sql_limit = ""
        
        # 模糊搜索比较消耗资源，只有调用是才载入第三方分词库
        import jieba # 引入结巴分词类库 第三方库
        jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
        #import jieba.posseg as pseg #引入词性标注模式
        user_dic_path = "../data/dic/user_dic_jieba.txt"
        jieba.load_userdict(user_dic_path)# 导入专用字典
        
        # 基础分词处理
        
        
        if (list_p):
        
            for x in list_p:
            
                #print (x,len(x)) # 调试用
                if (len(x) <= numb_kwd_cut):
                    
                    if (not x in dic_w):
                        dic_w[x] = [x]
                else:
                    
                    try:
                        list_t = jieba.cut(x)
                        
                        #去除单个字
                        list_t_2 = []
                        for z in list_t:
                            if (len(z) > 1):
                                list_t_2.append(z)
                        list_t = list_t_2
                        
                    except:
                        list_t = []
                        
                    if (list_t):
                        
                        #只有一个待选查询关键
                        if (len(list_t) == 1):
                            dic_w[x] = [x]
                        
                        if (len(list_t) > 1):
                          
                            dic_w[x] = list_t
        if (dic_w):
        
            dic_w_t = {}
            i = 0
            
            for x in dic_w:
                    
                print ("待查字典行号" + str(i),x,dic_w[x]) # 调试用
                list_t = self.kwd_index_what_short(dic_w[x],seg_p=jieba) # 短词模糊查询
                list_w += list_t

                #待选关键词去重与统计处理
                if (list_t):
                    if (not list_t[0][0] in dic_w_t):
                        if (len(list_t[0][0]) > 0):
                            dic_w_t[x] = list_t
                    else:
                        dic_w_t[x][2] = dic_w_t[x][2] + 1
                
                i += 1

        print ("最后的待查关键词字典：",dic_w_t)
        print ("最后的待查关键词哈希队列值：",list_w)
        
        sql_limit = " limit 1" # 并表查询取rank最高值
        
        numb_w = len(list_w) #待查队列长度
        numb_d = len(dic_w_t) #待查字典长度
        
        # ---tf_idf判别，排名
        # 在并表最大阈值内
        dic_t = {} #临时数组
        list_last = [] #最后的待查队列
        if (numb_w == 1):
            list_last.append(list_w[0][0])
        if (numb_w > 1):
            import math #数学计算库
            sql = "select count(*) from page"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                numb_idf_all = rows[0][0]
            else:
                numb_idf_all = 0
            #print("IDF总数",numb_idf_all) #调试用
            for x in list_w:
                if not x[0] in dic_t:
                    numb_tf_idf = x[2]/numb_w*math.log(numb_idf_all/x[1]) #待查关键词队列的tf-idf计算
                    dic_t[x[0]] = numb_tf_idf
            print ("待查临时字典",dic_t) #调试用
            
            #待查临时字典排序生成最终队列
            list_t = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)
            if (list_t):
                for x in list_t:
                    if not x[0] in list_last:
                        list_last.append(x[0])
        numb_last = len(list_last)
        print ("最后的并表查询队列：",list_last,numb_last) # 调试用
        #return rows_p,sql_last
        # 如果候选查询词队列小于等于并表阈值 直接并表查
        if (list_last):
            
            if (numb_last <= numb_table):
                j = numb_last
            else:
                j = numb_table
            
            while (j > 0):

                i = 1
                for x in list_last:
                    
                    if (i > j):
                        break

                    if (i == 1):

                        sql_head = "select "
                        sql_head +="z_invert_" + x + ".pid, "
                        sql_head +="z_invert_" + x + ".rank, "
                        sql_head +="z_invert_" + x + ".x0, "
                        sql_head +="z_invert_" + x + ".x1, "
                        sql_head +="z_invert_" + x + ".x2, "
                        sql_head +="z_invert_" + x + ".x3 "
                        sql_head += "from "
                        sql_data = " z_invert_" + x
                        sql_where = ""
                        sql_order = " order by z_invert_" + x + ".rank desc "
                        
                    else:
                        
                        sql_data += " inner join z_invert_" + x + " on z_invert_" + str_old + ".pid = z_invert_" + x + ".pid "
                    
                    str_old = x
                    i += 1
                
                sql = sql_head + sql_data + sql_where + sql_order + sql_limit
                print (sql) # 调试用
                res_p, rows_p = rs_index_mysql.read_sql(sql)
                if (res_p > 0):
                    break
                    
                j -= 1

        sql_last = sql
        print ("最后递归后的查询",sql_last) # 调试用

        return rows_p,sql_last

    # 查询主函数 重要
    def find_it(self,kwd_p,page_p):
        
        txt = ""
        pid = 0
        #txt = kwd_p + str(page_p) #调试用
        dic_k = {}
        dic_f = {}
        numb_kwd = len(kwd_p)
        rows_p = ()
        sql_last = ""
        job_last = ""
        list_p = []

        # --- 提交文本处理
        
        # 正常文本串的处理
        if (numb_kwd <= self.numb_kwd_long):
        
            list_p = self.cut_nature(kwd_p)
            dic_k = self.kwd_what_is_short(list_p=list_p)
            
            if (dic_k):
            
                print ("职业，薪酬，地点预查成功...")
                rows_p,sql_last = self.find_fit(dic_k) # 精确查找
                
                if (not rows_p):
                
                    print ("精确查找未成功...进入模糊查找") #调试用
                    rows_p,sql_last = self.find_like(list_p=list_p) # 模糊查找
                    if (rows_p):
                        print ("模糊查找成功...") #调试用
                        txt,job_last = self.show_fit(rows_p=rows_p,action_p="like")
                else:
                
                    print ("精确查找成功...") #调试用
                    txt,job_last = self.show_fit(rows_p=rows_p)
            
            if (not dic_k):
                print ("职业，薪酬，地点预查未成功...进入模糊查找")
                rows_p,sql_last = self.find_like(list_p=list_p) # 模糊查找
                if (rows_p):
                        print ("模糊查找成功...") #调试用
                        txt,job_last = self.show_fit(rows_p=rows_p,action_p="like")
                
        # 超长文本串的处理
        if (numb_kwd > self.numb_kwd_long and numb_kwd < 512):
            
            dic_l = {}
            dic_x = {}
            list_t = ""
            dic_w_t = {}
            dic_c = {}
            dic_t = {} #临时数组
            dic_a ={} #全局待选数组
            list_last = [] #最后的待查队列
            list_w = []
            numb_c = 0
            numb_d = 1
            numb_t = 0
            numb_kwd_cut = self.numb_kwd_cut
            numb_table = self.numb_table
            numb_dot = self.numb_dot
            
            import jieba # 引入结巴分词类库 第三方库
            jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
            #import jieba.posseg as pseg #引入词性标注模式
            user_dic_path = "../data/dic/user_dic_jieba.txt"
            jieba.load_userdict(user_dic_path)# 导入专用字典
            
            import math #数学计算库
            
            sql = "select count(*) from page"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                numb_idf_all = rows[0][0]
            else:
                numb_idf_all = 0
            
            list_p = self.cut_nature(kwd_p)
            
            if (not list):
                return txt,job_last,sql_last
            #整理待查长文本
            i = 0
            for x in list_p:
                if (len(x)>0 and (not "xa0" in x)):
                    dic_l[i] = x.strip()
                i += 1
            
            #自然段落最优解
            
            #求得自然分段的配额
            numb_p = len(dic_l)
            if (numb_p <= numb_table):
                numb_p = int(self.numb_table/numb_p + 0.5)
            if (numb_p > self.numb_table):
                numb_p = 1
            print ("自然分段的配额：",numb_p)
            
            
            for x in dic_l:
            
                dic_c = {}
                print (x,dic_l[x])
                str_t = dic_l[x]
                str_t = str_t.strip()
                dic_x[x] = [str_t[0:32]]
                list_w = self.kwd_index_what_short(dic_x[x],seg_p=jieba)

                if (list_w):
                    dic_w_t = {}
                    for x in list_w:
                        if (not x[0] in dic_w_t):
                            dic_w_t[x[0]] = x
                        else:
                            dic_w_t[x[0]] = [x[0],x[1],x[2]+1]
                
                numb_d = len(dic_w_t)
                
                for x in dic_w_t:
                    
                    numb_c = int(dic_w_t[x][2])/numb_d*math.log(numb_idf_all/int(dic_w_t[x][1]))
                    dic_c[x] = numb_c
                    
                list_t = sorted(dic_c.items(), key=lambda d:d[1], reverse = True)
                numb_t = len(list_t) #局部最优排序后待选关键词数
                if (numb_t > numb_p):
                    numb_t = numb_p
                i = 1
                for x in list_t:
                    if (not x[0] in dic_a):
                        dic_a[x[0]] = x[1]
                    i += 1
                    if (i > numb_t):
                        break
                        
            # 获得全局最优关键词排列
            list_t = sorted(dic_a.items(), key=lambda d:d[1], reverse = True)
            numb_t = len(list_t)
            if (numb_t > self.numb_table):
                numb_t = self.numb_table
        
            i = 1
            for x in list_t:
                list_last.append(x[0])
                i += 1
                if (i > numb_t):
                    break
                    
            print ("最后的待查关键词队列：",list_last) # 调试用
            
            # 并表查询
            numb_last = len(list_last)
            sql_limit = " limit 1"
            
            if (list_last):
            
                if (numb_last <= numb_table):
                    j = numb_last
                else:
                    j = numb_table
            
                while (j > 0):

                    i = 1
                    for x in list_last:
                    
                        if (i > j):
                            break

                        if (i == 1):

                            sql_head = "select "
                            sql_head +="z_invert_" + x + ".pid, "
                            sql_head +="z_invert_" + x + ".rank, "
                            sql_head +="z_invert_" + x + ".x0, "
                            sql_head +="z_invert_" + x + ".x1, "
                            sql_head +="z_invert_" + x + ".x2, "
                            sql_head +="z_invert_" + x + ".x3 "
                            sql_head += "from "
                            sql_data = " z_invert_" + x
                            sql_where = ""
                            sql_order = " order by z_invert_" + x + ".rank desc "
                        
                        else:
                        
                            sql_data += " inner join z_invert_" + x + " on z_invert_" + x + ".pid = z_invert_" + x + ".pid "
                    
                        i += 1
                
                    sql = sql_head + sql_data + sql_where + sql_order + sql_limit
                    print (sql) # 调试用
                    res_p, rows_p = rs_index_mysql.read_sql(sql)
                    if (res_p > 0):
                        break
                    
                    j -= 1

            sql_last = sql
            print ("最后递归后的查询",sql_last) # 调试用
            if (rows_p):
                print ("长字符串模糊查找成功...") #调试用
                txt,job_last = self.show_fit(rows_p=rows_p,action_p="like")
        
        return txt,job_last,sql_last
        

# 默认搜索类
class Search_default(Search_base):

    def run_do(self,kwd_p,page_p):
    
        time_start = datetime.datetime.now()
        txt = ""
        job_last = ""
        sql_last = ""
        dic_p = {}
        
        txt,job_last,sql_last = self.find_it(kwd_p=kwd_p,page_p=page_p)
        
        if (txt != ""):
            dic_p["job"] = job_last
            dic_p["sql_last"] = sql_last
            txt += self.link_more(dic_p=dic_p)
        else:
            txt += "<br><br><br>没有匹配项目，请修改或更换关键词！"
            
        txt += "<br><br><br><br><font color=\"#cccccc\">本次执行耗时：" + str(time_cost(time_start)) + " 秒</font>"
        return txt,job_last,sql_last
        
# 预测搜索类
class Search_divine(Search_base):

    def run_do(self,kwd_p,page_p,url_hash_p=""):
    
        time_start = datetime.datetime.now()
        txt = ""
        job_last = ""
        sql_last = ""
        t_name_p = "struct"
        pay1 = 0
        pay2 = 0
        type_p= "CA"
        dic_p = {}
        
        if (url_hash_p == ""):
        
            txt,job_last,sql_last = self.find_it(kwd_p=kwd_p,page_p=page_p)
        
            if (txt == ""):
                txt += "<br><br><br>没有匹配项目，请修改或更换关键词！"
                return txt
        
            # 获得url_hash
            sql = "select url_hash from page where job='" + job_last + "' order by power desc limit 1"
            res, rows = rs_basedata_mysql.read_sql(sql)
            print (job_last)
            if (res < 1):

                sql = "select url_hash from page where job like '%" + job_last + "%' order by power desc limit 1"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if (res < 1):
                    txt += "没有匹配项目，请修改或更换关键词！"
                    return txt
                
            url_hash = rows[0][0]
        
        if (url_hash_p != ""):
            url_hash = url_hash_p
            
        #读取数据
        sql_head = "select "
        sql_head += "url_hash," #0 点位hash值
        sql_head += "where_work," #1 地点
        sql_head += "work_experience," #2工作经验
        sql_head += "education_minimum," #3 最低学历
        sql_head += "company_scale," #4 公司规模
        sql_head += "company_nature," #5 公司属性
        sql_head += "date_release,"  #6 发布时间
        sql_head += "job_description," #7 职位描述
        sql_head += "position_title" #8 职位
        
        sql_from = " from " + t_name_p
        
        sql_where = " where url_hash ='" + url_hash + "'"
        
        sql = sql_head + sql_from + sql_where

        res,rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "不存在补缺的知识点或数据库读取错误"
        
        sys.path.append("../ml/")
        import divine # 薪酬预测模块
        
        for row in rows:
        
            list_p = []
            hash = row[0]
            list_t =""
            
            for i in range(1,len(row)):
                
                if (row[i] is not None):
                    str_t = str(row[i])
                    str_t = str_t.strip()
                    str_t = str_t.replace("[","").replace("]","").replace("'","")
                    if (i==6):
                        str_t = "2017/6/26"
                    #print(i,len(str_t),str_t) #调试用
                    list_t += str_t + "~@~"
                    #list_p = list_p.append(str_t)
                else:
                    list_t += "-1" + "~@~"
                    #list_p = list_p.append("-1")
            list_t = list_t[0:-3]
            list_p = list_t.split("~@~")
            
            #print (len(list_p)) #调试用
            #for i in range(len(list_p)):
                #print (i,list_p[i])
            try:
                pay1,pay2 = divine.run_it(catelog=type_p, test=list_p) #提交预测引擎获得结果
            except:
                pass
        #print ("预测值",pay1,pay2) #调试用
        #渲染输出结果
        if (pay1 > 0 and pay2 > 0):
            txt_head = "机器学习预测结果为："
            txt_head += "<font color=\"#207439\">￥</font><font style=\"font-size:65px;color: #207439;font-family:\"Arial Black\", Gadget, sans-serif;\">" + str(pay1) + "-" + str(pay2) + "</font> 元/月  <br><br>"
            if (kwd_p !=""):
                txt_head += "<br> <font color=\"#cccccc\">----以下为根据历史综合统计分析提供的对照结果----</font><br><br>"
                txt = txt_head + txt
                dic_p["job"] = job_last
                dic_p["sql_last"] = sql_last
                txt += self.link_more(dic_p=dic_p)
            if (kwd_p ==""):
                sql = "select pay1,pay2 from page where url_hash='" + url_hash + "'"
                res,rows = rs_basedata_mysql.read_sql(sql)
                if (res > 0):
                    txt_head += "<br> <font color=\"#cccccc\">----以下为根据历史综合统计分析提供的对照结果----</font><br><br>"
                    txt_head += str(rows[0][0]) + " - " + str(rows[0][1])
                    txt += txt_head
            txt += "<br><br><br><br><font color=\"#cccccc\">本次执行耗时：" + str(time_cost(time_start)) + " 秒</font>"
        else:
            txt = "缺少关键资料,请更换关键词重新预测！"
        return txt
        
# 知识搜索类
class Search_knowledge(Search_base):

    def run_do(self,kwd_p,page_p,url_hash_p=""):
    
        import jieba # 引入结巴分词类库 第三方库
        jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
        #import jieba.posseg as pseg #引入词性标注模式
        user_dic_path = "../data/dic/user_dic_jieba.txt"
        #jieba.load_userdict(user_dic_path)# 导入专用字典
    
        time_start = datetime.datetime.now()
        txt = ""
        job_last = ""
        sql_last = ""
        t_name_p = "struct"
        list_w = []
        dic_dot = {"job":(),"pay":(),"place":(),"remark":()}
        dic_p = {} #临时字典
        numb_max = 0
        zero_is = ""
        dic_p = {}
        
        if (url_hash_p == ""):
        
            txt,job_last,sql_last = self.find_it(kwd_p=kwd_p,page_p=page_p)

            if (txt == ""):
                txt += "<br><br><br>没有匹配项目，请修改或更换关键词！"
                return txt
            else:
                txt = ""
            
            # 获得url_hash
            sql = "select url_hash,job,pay1,pay2,place,seq from page where job='" + job_last + "' order by power desc limit 1"
            res, rows = rs_basedata_mysql.read_sql(sql)
        
        else:
        
            # 获得url_hash
            sql = "select url_hash,job,pay1,pay2,place,seq from page where url_hash='" + url_hash_p + "' order by power desc limit 1"
            res, rows = rs_basedata_mysql.read_sql(sql)
            
        if (res < 1):
            
            if (url_hash_p == ""):
                sql = "select url_hash,job,pay1,pay2,place,seq from page where job like '%" + job_last + "%' order by power desc limit 1"
                res, rows = rs_basedata_mysql.read_sql(sql)
                if (res < 1):
                    txt += "没有匹配项目，请修改或更换关键词！"
                    return txt
            else:
                txt += "没有匹配项目，请修改或更换关键词！"
                return txt
                
        url_hash = rows[0][0]
        job = rows[0][1]
        pay1 = rows[0][2]
        pay2 = rows[0][3]
        place = rows[0][4]
        dic_dot["zero"] = job
        try:
            dic_p = eval(rows[0][5])
        except:
            pass
            
        # 构造职位知识点相关链

        list_w = jieba.cut(job)
        for x in list_w:
            #简化TF-IDF算法
            sql = "select tf/idf as rank from index_main where keyword ='" + x + "'"
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                #print(x,rows[0][0])#调试用
                if (rows[0][0] > numb_max):
                    numb_max = rows[0][0]
                    zero_is = x
        print ("职位核心词：" + zero_is)
        if (zero_is != ""):
            sql = "select job,power from page where job like '%" + zero_is+ "%' group by job order by power desc limit " + str(random.randint(8,12))
            #sql = "select keyword,tf/idf as rank from index_main where keyword like '%" + zero_is+ "%' order by rank limit " + str(random.randint(8,12))
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                dic_dot["job"] = rows
        
        # 构造薪酬知识点相关链
        sql = "select pay1,pay2 from page where job like '%" + zero_is+ "%' group by job order by power,abs((pay2-pay1)-" + str(pay2-pay1) + ") limit " + str(random.randint(8,12))
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res > 0):
            dic_dot["pay"] = rows
            
        # 构造地点知识点相关链
        if (zero_is != ""):
            sql = "select place,power from page where job like '%" + zero_is+ "%' group by place order by power desc limit " + str(random.randint(8,12))
            res, rows = rs_basedata_mysql.read_sql(sql)
            if (res > 0):
                dic_dot["place"] = rows
                
        
        #构造remark
        
        sql = "select tf_idf from page where url_hash='" + url_hash + "' limit 1"
        res, rows = rs_basedata_mysql.read_sql(sql)
        numb_r = random.randint(8,12)
        list_remark = []
        if (res > 0):
            try:
                list_r = eval(rows[0][0])
            except:
                list_r =[]
            if (list_r):
                i = 1
                for x in list_r:
                    list_remark.append(x)
                    i += 1
                    if (i > numb_r):
                        break
        
        dic_dot["remark"] = list_remark
        
        #f = open("../data/test_" + str(random.randint(1,99999)) + ".txt",'w',encoding="utf-8")
        #f.write(str(dic_dot))
        #f.close()
        #print (dic_dot) #调试用
        
        #渲染JS统计图表
        import echarts_do
        txt += echarts_do.k_map_1(obj=dic_dot,job_is=kwd_p)
        dic_p["job"] = job_last
        dic_p["sql_last"] = sql_last
        txt += self.link_more(dic_p=dic_p)
        txt += "<br><br><br><br><font color=\"#cccccc\">本次执行耗时：" + str(time_cost(time_start)) + " 秒</font>"
        return txt
        
# vip搜索类
class Search_vip(Search_base):

    def run_do(self,kwd_p,page_p):
    
        time_start = datetime.datetime.now()
        txt = ""
        job_last = ""
        sql_last = ""
        group_is = ""
        dic_p = {}
        
        txt,job_last,sql_last = self.find_it(kwd_p=kwd_p,page_p=page_p)
        dic_p["job"] = job_last
        dic_p["sql_last"] = sql_last

        if (txt == ""):
            txt += "<br><br><br>没有匹配项目，请修改或更换关键词！"
            return txt
        sql = "select group_is from result_job where job ='" + job_last + "'"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            txt += "<br>没有对应的聚类，请联系总管理员！"
            return txt
        else:
            group_is = rows[0][0]
            txt = "[\'vip\',"
        
        txt += "【"  + group_is + "类】可视化图表(VIP专用) "
        #渲染JS统计图表
        import echarts_do
        txt += echarts_do.vip(group_is_p=group_is)
        
        txt += self.link_more(dic_p=dic_p)
        txt += "<br><br><br><br><font color=\"#cccccc\">本次执行耗时：" + str(time_cost(time_start)) + " 秒</font>"
        return txt
        
# 薪酬处理类
class SalaryJudger(object):
    """
    薪酬转化
    """
    @unique
    class DateTypeScale(Enum):
        """时间薪酬类型比例"""
        Hour = 30 * 8
        Day = 30
        Month = 1
        Year = 1 / 12

    @unique
    class SalaryTypeScale(Enum):
        """薪酬进制比例"""
        Yuan = 1
        Qian = 1000
        Wang = 10000

    @unique
    class SalaryRange(Enum):
        """纯数字薪酬范围"""
        Day = 500
        Month = 300000
        Year = 99999999

    # 中文对应数字比
    DIC_NUMB = {
        '〇': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '零': 0,
        '壹': 1,
        '贰': 2,
        '叁': 3,
        '肆': 4,
        '伍': 5,
        '陆': 6,
        '柒': 7,
        '捌': 8,
        '玖': 9,
        '貮': 1,
        '两': 2,
        '十': 10,
        '拾': 10,
        '百': 100,
        '佰': 100,
        '千': 1000,
        '仟': 1000,
        '万': 10000,
        '萬': 10000,
        '亿': 100000000,
        '億': 100000000,
        '兆': 1000000000000,
        'k': 1000,
        'K': 1000,
        'Ｋ': 1000,
        'ｋ': 1000
    }
    ALL_MATCH = dict({str(x): x for x in range(1, 10)}, **DIC_NUMB)

    # 数字匹配规则
    NUMB_MATCH_PATTERN = "[" + "".join(DIC_NUMB.keys()) + "]"

    # 薪酬类型判别
    UNIT_MATCH_PATTERN = "([元千仟kKＫｋ万萬])[/／每]([月年日天]|小时)"

    # 浮点数｜正整数匹配，非标准匹配中文混合匹配
    FLOAT_MATCH_PATTERN = '[\d\.]+'
    NONSTANDAED_MATCH_PATTERN = "{}{}".format("".join(DIC_NUMB.keys()), "\d")
    NONSTANDAED_NUM_MATCH_PATTERN = "[一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]"
    CN_NUM_MATCH_PATTERN = "[一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两万千仟萬kKＫｋ]"

    # 省略匹配
    OMIT_QIAN_MATCH_PATTERN = "\s*({})[千仟kKＫｋ]({})[^一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]+".\
        format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)
    OMIT_WANG_MATCH_PATTERN = "\s*({})[萬万]({})[^一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]*".\
        format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)

    OMIT_MATCH_PATTERN = "({})([千仟萬万])({})"\
        .format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)

    FLOAT_MATCH_PATTERN_2 = "([\d.]+)([万千仟萬kKＫｋ])"

    def __init__(self):

        # 薪酬类型/ 进制匹配
        self.SALARY_TYPE_MATCH = {
            "年": self.DateTypeScale.Year,
            "年薪": self.DateTypeScale.Year,
            "月薪": self.DateTypeScale.Month,
            "月": self.DateTypeScale.Month,
            "日": self.DateTypeScale.Day,
            "天": self.DateTypeScale.Day,
            "日薪": self.DateTypeScale.Day,
            "每小时": self.DateTypeScale.Hour,
            "小时": self.DateTypeScale.Hour,
            "时": self.DateTypeScale.Hour,
            "时薪": self.DateTypeScale.Hour
        }
        self.RADIX_TYPE_MATCH = {
            "元": self.SalaryTypeScale.Yuan,
            "千": self.SalaryTypeScale.Qian,
            "仟": self.SalaryTypeScale.Qian,
            "k": self.SalaryTypeScale.Qian,
            "K": self.SalaryTypeScale.Qian,
            "Ｋ": self.SalaryTypeScale.Qian,
            "ｋ": self.SalaryTypeScale.Qian,
            "万": self.SalaryTypeScale.Wang,
            "萬": self.SalaryTypeScale.Wang
        }

        # 薪酬类型判别式, 进制判别式
        self.SALARY_TYPE_MATCH_PATTERN = "|".join(self.SALARY_TYPE_MATCH.keys())
        self.RADIX_TYPE_MATCH_PATTERN = "|".join(self.RADIX_TYPE_MATCH.keys())

    def salary_judge(self, salary_string):
        """
        判定上下限的薪酬函数
        :param salary_string: 薪酬字符串
        :return:
        """
        # 面议判别
        if re.search("面议", salary_string):
            return 0, 0

        # 薪酬类型，　进制类型
        salary_type, radix_type = None, None

        # 薪酬类型判别
        # 薪酬单位判别, 仅含薪酬类型判别
        unit_match = re.search(self.UNIT_MATCH_PATTERN, salary_string)
        salary_type_match = re.search(self.SALARY_TYPE_MATCH_PATTERN, salary_string)

        if unit_match:
            radix_type, salary_type = self.RADIX_TYPE_MATCH[unit_match.group(1)], \
                                      self.SALARY_TYPE_MATCH[unit_match.group(2)]
        elif salary_type_match:
            salary_type = self.SALARY_TYPE_MATCH[salary_type_match.group()]

        # 薪酬范围数字的提取
        if unit_match:
            temp_string = re.sub(self.UNIT_MATCH_PATTERN, "", salary_string)
            nums_list = self.__get_nums_from_string(temp_string)
        else:
            nums_list = self.__get_nums_from_string(salary_string)

        if len(nums_list) == 1:
            num1 = num2 = nums_list[0]
        elif len(nums_list) >= 2:
            num1, num2, *_ = nums_list

        # 薪酬类型确认
        if not salary_type:
            if num2 < self.SalaryRange.Day.value:
                salary_type = self.DateTypeScale.Day
            elif num2 < self.SalaryRange.Month.value:
                salary_type = self.DateTypeScale.Month
            elif num2 < self.SalaryRange.Year.value:
                salary_type = self.DateTypeScale.Year

        if not radix_type:
            radix_type = self.SalaryTypeScale.Yuan

        # 薪酬上下限确定
        if re.search("以上|上", salary_string):
            return self.salary_range_judge(salary_lower_limit=num1, date_type=salary_type,
                                           salary_type_scale=radix_type)
        elif re.search("以下|下", salary_string):
            return self.salary_range_judge(salary_upper_limit=num1, date_type=salary_type,
                                           salary_type_scale=radix_type)

        return self.salary_range_judge(num1, num2, date_type=salary_type, salary_type_scale=radix_type)

    def salary_range_judge(self, salary_lower_limit=None, salary_upper_limit=None, date_type=DateTypeScale.Month,
                           salary_type_scale=SalaryTypeScale.Yuan):
        """
        薪酬范围的判别
        :param date_type: 时间类型
        :param salary_type_scale: 薪酬类型
        :param salary_lower_limit: 薪酬下限
        :param salary_upper_limit: 薪酬上限
        :return: 月薪的上下限范围元组对
        """
        if not all([salary_lower_limit, salary_upper_limit]):

            if salary_lower_limit is not None:
                return int(float(salary_lower_limit) * date_type.value * salary_type_scale.value), 99999999

            elif salary_upper_limit is not None:
                return 0, int(float(salary_upper_limit) * date_type.value * salary_type_scale.value)
        else:

            s1 = int(float(salary_lower_limit) * date_type.value * salary_type_scale.value)
            s2 = int(float(salary_upper_limit) * date_type.value * salary_type_scale.value)
            return (s1, s2) if s1 < s2 else (s2, s1)

    def __cn2dig(self, string_):
        """
        中文数字转阿拉伯
        :param string_:
        :return:
        """
        if len(string_) == 3:
            # 省略匹配，　例如一千五，　一万五
            omit_match = re.search(self.OMIT_MATCH_PATTERN, string_)

            # 省略形式的千进制匹配
            if omit_match:
                return (self.ALL_MATCH[omit_match.group(1)] + self.ALL_MATCH[omit_match.group(3)]*0.1) \
                       * self.ALL_MATCH[omit_match.group(2)]

        # 千进制数
        thousand_num_list = re.split("万|萬", string_)
        if string_.endswith("万") or string_.endswith("萬"):
            return self.__turn_thousand_nonstandard_string(string_.strip("万")) * 10000

        # 获取一万以下的数
        t1 = list(reversed(thousand_num_list))[0]
        num = self.__turn_thousand_nonstandard_string(t1)

        # 获取一万以上的数
        if len(thousand_num_list) > 1:
            t2 = thousand_num_list[0]
            num += self.__turn_thousand_nonstandard_string(t2) * 10000
        return num

    def __str2dig(self, string_):
        """
        字符串的浮点数或正整数转化成数字
        :param string_:　
        :return:
        """
        return float(string_)

    def __get_nums_from_string(self, salary_string):
        """
        从字符串中获取薪酬数字
        :param salary_string: 薪酬字符串
        :return:
        """

        # 浮点数千万匹配
        float_match = re.search(self.FLOAT_MATCH_PATTERN_2, salary_string)
        if float_match:
            return [float(match.group(1))*self.ALL_MATCH[match.group(2)] for match in
                    re.finditer(self.FLOAT_MATCH_PATTERN_2, salary_string)]

        # 匹配字符串是否含有非标准字符
        cn_match = re.search(self.CN_NUM_MATCH_PATTERN, salary_string)
        if cn_match:
            nums_match = re.findall("[{}]+".format(self.NONSTANDAED_MATCH_PATTERN), salary_string)
            nums_list = [self.__cn2dig(num) for num in nums_match]
        else:
            nums_result = re.findall(self.FLOAT_MATCH_PATTERN, salary_string)
            nums_list = [self.__str2dig(num) for num in nums_result]

        return nums_list

    def __turn_thousand_nonstandard_string(self, string_):
        """
        将千进制非标准数字字符串转化成数字
        :param string_: 中文字符串
        :return:
        """
        if len(string_) == 1:
            return self.ALL_MATCH[string_]

        # 十 十三 十五 匹配匹配
        shi_match_ = re.match("[拾十]({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN), string_)
        if shi_match_:
            return 10 + self.ALL_MATCH[shi_match_.group(1)]

        num = 0
        qian_match = re.search("({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[千仟kKＫｋ]"), string_)
        bai_match = re.search("({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[百佰]"), string_)
        shi_match = re.search("({})({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[拾十]",
                                                    self.NONSTANDAED_NUM_MATCH_PATTERN), string_)
        single_match = re.search("{}({})".format("[拾十零]", self.NONSTANDAED_NUM_MATCH_PATTERN), string_)

        # 转化进制
        if qian_match:
            num += self.ALL_MATCH[qian_match.group(1)] * 1000
        if bai_match:
            num += self.ALL_MATCH[bai_match.group(1)] * 100
        if shi_match:
            num += self.ALL_MATCH[shi_match.group(1)] * 10
        if single_match:
            num += self.ALL_MATCH[single_match.group(1)]

        return num



def main():
    print("") # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()
    rs_sqlite_file.close()
    #rs_way_mysql.close()
    rs_basedata_mysql.close()
    rs_index_mysql.close()