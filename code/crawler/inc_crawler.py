#!/usr/bin/env python
# -*- coding: UTF-8 -*- 

'''
{
"版权":"LDAE工作室",
"author":{
"1":"腾辉",
"2":"吉更",
"3":"iron",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

import cgi # 声明IIS调用方式
import sys
import requests #互联网功能模块
import urllib.request #互联网功能模块2
import chardet #编码识别模块
import http.cookiejar as cookielib #cookie处理模块
import os
import csv # 文件操作
import time # 定时模块
import threading # 线程模块
import re #正则处理
import requests

#-----系统外部需安装库模块引用-----
from lxml import etree # 解析网页源码模块
from lxml import html as lxml_html # 解析网页源码模块
from bs4 import BeautifulSoup as bs_4 
import functools
import chardet
from selenium import webdriver # 浏览器引擎webdriver模块

#-----DIY自定义库模块引用-----
sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_conn import * #自定义数据库功能模块
import config #系统配置参数
from diy.inc_hash import hash_make # 基本自定义hash模块
from diy.inc_nlp import Content_main # 正文识别

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

# 基础爬虫对象
class Crawler_base(object):

    def __init__(self, headers="", timeout=10, cookies_file='cookies',driver_type="PhantomJs", page_load_timeout=12):
        # session设置
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename=cookies_file)
        if (headers == ""):
            headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/56.0.2924.87 Safari/537.36")}
        self.headers = headers
        self.timeout = timeout
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            pass
        
        # webdriver设定, 浏览器超时设定
        self.page_load_timeout = page_load_timeout
        self.driver = self.get_driver(driver_type) #获取源码se的方法需要 必要时激活
        self.driver.set_page_load_timeout(self.page_load_timeout) #获取源码se的方法需要 必要时激活

    # 获取浏览器引擎, 此处动态添加浏览器引擎设定, 默认为PhantomJs
    @staticmethod
    def get_driver(driver_type="PhantomJs"):
        """
        获取浏览器引擎
        :param driver_type: 浏览器引擎类型
        :return:
        """
        if driver_type == "PhantomJs":
            return webdriver.PhantomJS("../library/plug/phantomjs")
        elif driver_type == "Chrome":
            return webdriver.Chrome("../library/plug/chromedriver")
        elif driver_type == "Ie":
            return webdriver.Ie("../library/plug/IEDriverServer")

        raise Exception("未有的浏览器引擎")

    # 重新设置浏览器driver
    def reset_driver(self, type_):
        """
        重新设置浏览器引擎
        :param type_: 页码加载超时时间
        :return:
        """
        self.driver.close()
        self.driver = self.__get_driver(type_)

    # 更新会话
    def reset_session(self):
        """重新设置会话"""
        self.session = requests.Session()
    
    # 获取网页源码 重要
    def get_html(self,url_p,chartset_p='utf-8',type_p ='rg',has_p='',headers_p={},timeout_p=28,count_p=0):
        
        txt = "nothing" # 返回的文本赋初值
        
        count_p +=1 #多步循环阈值计数
        print ("time_run:",count_p) #调试用
        if (count_p > 6):
            return txt
        
        #---基础参数设定---
        #设定默认浏览器头
        if (not headers_p):
            headers_p = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/56.0.2924.87 Safari/537.36")}
        txt = "nothing" # 返回的文本赋初值
        work_list = "rg-rp-ss-ul-df-se-" #原始递归工作队列 按好用的概率排列
        what_list = work_list.replace(has_p,"") #进行中的待选队列
        
        #全部遍历过后，无结果则退出
        if (what_list == ""):
            return txt
            
        if (type_p in what_list):
            pass
        else:
            type_p = what_list.split("-")[0] #取得待选队列第一个
            
        print (type_p,what_list,headers_p) # 调试用
            
        #全部遍历过后，无结果则退出
        if (type == ""):
            return txt
        
        # get的方法
        if (type_p == 'rg'):
            
            try:
                html = requests.get(url=url_p,timeout=timeout_p, headers=headers_p)
                txt = str(html.text.encode(html.encoding), encoding=chartset_p)
                html.close()
            except:
                pass
        
        # post的方法
        if (type_p == 'rp'):
        
            try:
                html = requests.post(url=url_p, timeout=timeout_p, headers=headers_p)
                txt = str(html.text.encode(html.encoding), encoding=chartset_p)
                html.close()
            except:
                pass
        
        # session的方法
        if (type_p == 'ss'):
        
            try:
                res_addr = self.session.get(url_p, timeout=timeout_p, headers=headers_p)
                res_addr.encoding = chardet.detect(res_addr.content)["encoding"]
                txt = bs_4(res_addr.text, "lxml")
            except:
                pass
        
        # urllib的方法
        if (type_p == 'ul'):
        
            try:
                html = urllib.request.urlopen(url = url_p)  
                txt = html.read().decode(chartset_p,"ignore")
                html.close()
            except:
                pass
        
        # Selenium的方法 待完善
        if (type_p == 'se'):
        
            try:
                self.driver.get(url_p)
                js = "var q=document.body.scrollTop=100000"
                self.driver.execute_script(js)
                self.driver.implicitly_wait(30) # 据说此方法是智能等待，看效果还不错，数据加载完就返回了 30 代表等待秒
                txt = self.driver.page_source
            except:
                pass
                
        # login的方法 待完善
        if (type_p == 'lg'):
        
            try:
                pass
            except:
                pass
        
        # 最后默认的方法
        if (type_p == 'df'):
            
            try:
                html = requests.get(url=url_p, timeout=timeout_p,headers=headers_p)
                txt = html.text
                html.close()
            except:
                txt = "nothing"
                pass

        #失败后的递归校验
        if (txt == "nothing"):
            if (has_p == ""):
                has_p = type_p + "-"
            else:
                has_p += type_p + "-"
            #递归调用
            
            time.sleep(10)
            return self.get_html(url_p,chartset_p,type_p,has_p,headers_p,timeout_p,count_p=count_p)
            
        else:
            return txt
        # 返回值
        return txt

    # 读取网站域名
    def get_url_root(self,url):
        http = ''
        https= ''
        url_root = ''
        if 'http://' in url  or 'http:/' in url :
            http = 'http://'
            url = url.replace('http://','').replace('http:/','').strip()
        elif 'https://' in url  or 'https:/' in url :
            https = 'https://'
            url = url.replace('https://', '').replace('httpss:/', '').strip()
        else:
            pass
        url_root = url.split('/')[0]
        return url_root
        
    # 从文本中提取网页编码方式
    def pick_charset(self,html):

        charset = None
        m = re.compile('<meta .*(http-equiv="?Content-Type"?.*)?charset="?([a-zA-Z0-9_-]+)"?', re.I).search(html)
        if m and m.lastindex == 2:
            charset = m.group(2).lower()
        return charset
        
    # 松散html的初步清理
    def html_clear(self,code_p=""):
        code_p = code_p.replace(" ","@~@~@~@~@")
        code_p = "".join(code_p.split())
        code_p = code_p.replace("@~@~@~@~@"," ")
        return code_p
 
    #方法库的代码生成
    def code_make(self,seed_name_p,conn_way=""):

        sql_code = "select keep_if,code,code_view,secret_if,id from code where bag_name ='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql_code)
        if (res < 1):
            print (sql_code)
            print ("固定方法库 " + seed_name_p + "不存在或读取失败")
            e("中断行号：271")
        else:
            keep_if = rows[0][0]
            code = rows[0][1]
            code_view = rows[0][2]
            secret_if = rows[0][3]
            cid = rows[0][4]
            
        # 地址表检查
        code_name = "z_code_" + str(cid) + ".py" #源码文件的默认名
        
        # 临时生成方法库文件
        
        if (code_view == "根目录执行" or code_view == "根目录寄生" ):
            path_code = "z_code_" + str(cid) + ".py"
            code_name = "z_code_" + str(cid) + ".py"
            
        if (code_view == "子目录调用"):
            path_code = "diy\\z_code_" + str(cid) + ".py"
            code_name = "diy.z_code_" + str(cid) + ".py"
            
        if (secret_if == "yes"):
            code = secret_ldae(text_p=code_txt,secret_if=dic_p["secret_if"],key_p=config.dic_config["secret_key"],salt_p=config.dic_config["secret_salt"])
        
        if (path_code != ""):
            
            if os.path.exists(path_code):
                pass
            else:
                f = open(path_code, 'w', encoding="utf-8")
                f.write(code.replace("\\n","\n"))
                f.close()
                time.sleep(1)
        
        return keep_if,code_name,path_code
    
    #调试或临时性生成永久化中间结果
    def file_temp(self,code_p='',path_p = "../data/temp.html",char_p="utf-8"):
        try:
            f = open(path_p,'w',encoding=char_p)
            f.write(gbk_bug(str(code_p)))
            f.close()
        except:
            pass
        return True
        
# 地址爬虫类
class Crawler_addr(Crawler_base):


    def run_do(self,seed_name_p,numb_rs_p=0,nosame_if_p=0,shell_if_p=1,sleep_p=0,conn_way=""):
        
        self.sleep_p = sleep_p #设置喘气间隔参数
        
        # 固定方法库调用
        
        keep_if,code_name,path_code = self.code_make(seed_name_p=seed_name_p + "_0")

        #引用方法
        
        run_model =__import__(code_name.replace(".py",""))
        self.dic_addr_chk = run_model.dic_addr_chk
        #print (self.dic_addr_chk) #调试用
        # 引用完毕后删除源文件
        if (keep_if == 0):
            os.remove(path_code)
        
        # 网址参数调用
        sql = "select "
        sql += "rule_addr,"
        sql += "runs_addr,"
        sql += "nosame_addr,"
        sql += "tree_height,"
        sql += "eff_addr"
        sql += " from rule_crawler" 
        sql += " where seed_name='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)

        if (res == 1):
            self.rule_addr = rows[0][0] # 地址运行参数
            self.runs_addr = rows[0][1] # 地址阶段执行参考次数
            self.nosame_addr = rows[0][2] # 地址去重阈值
            self.tree_height_max = rows[0][3] # 地址树的最大参考深度
            self.eff_addr = rows[0][4] # 地址最低效率阈值
        else:
            print("爬虫任务不存在")
            return "子任务参数不存在"

        self.dic_addr = {} #定义参数字典
        #print (self.rule_addr) #调试用
        if (self.rule_addr != ""):
            try:
                self.dic_addr = eval(self.rule_addr)
            except:
                
                self.rule_addr = r'{"domain":[".www."],"power":[".html",".shtml","/\d/"],"order":["tree_height asc","power asc"],"login":["no"],"where":[""]}'
                sql = "select seed_url from seed where seed_name ='" + seed_name_p + "'"
                res, rows = conn_way.read_sql(sql)
                if (res > 0):
                    self.rule_addr = self.rule_addr.replace(r':[".www."],',":[\"" + self.domain_main_get(rows[0][0],head_p="http://") +"\"],")
                    self.dic_addr = eval(self.rule_addr)
        
        txt = "" #中间结果字符串
        self.seed_name = seed_name_p
        self.shell_if = shell_if_p
        self.time_start = datetime.datetime.now() #赋值初始时间
        self.dic_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        self.tree_hight = 0
        self.addr_run = 1
        
        #取得种子网址
        sql = "select seed_url,seed_type from seed where seed_name='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)
        
        if (res == 1):

            self.seed_url = rows[0][0]
            self.seed_type = rows[0][1]

        else:

            time.sleep(10)
            return "种子不存在或者有重复项，请重新配置参数并启动任务。"
        
        # 取得子任务信息
        sql = "select "
        sql += "id,"
        sql += "title,"
        sql += "model_run,"
        sql += "pram_run,"
        sql += "skip_to,"
        sql += "step_if,"
        sql += "pass_if,"
        sql += "login_if,"
        sql += "admin_list,"
        sql += "run_time_step,"
        sql += "run_time_all,"
        sql += "step_if "
        sql += "from task "
        sql += "where seed_name ='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)
        
        if (res > 0):
        
            self.id = rows[0][0] # ID值
            self.title = rows[0][1] #标题值
            self.model_run = rows[0][2] #运行模块
            self.pram_run = rows[0][3] # 运行参数
            self.skip_to = rows[0][4] #结束后跳转地址
            self.step_if = rows[0][5] #是否为单步执行
            self.pass_if = rows[0][6] #是否标记为可执行
            self.login_if = rows[0][7] #受否需要先登录再爬取
            self.admin_list = rows[0][8] #管理权限队列
            self.run_time_step = rows[0][9] #管理权限队列
            self.run_time_all = rows[0][10] #管理权限队列
            self.step_if = rows[0][11] #管理权限队列
        
        else:
            
            return "子任务不存在"

        self.seed_hash = hash_make(seed_name_p)
        
        #[1] 地址爬虫调用
        self.url_table = "z_url_" + self.seed_hash

        #校验子任务的数据源子表
        try:
            sql="create table if not exists " + self.url_table + " like url"
            create_if = conn_data.write_sql(sql)
        except:
            pass
        # 强制去重
        if (nosame_if_p == 1 ):
            self.addr_nosame_do(self="",url_table_p=self.url_table,conn_index=conn_data)
            return "强制去重完成"
            

        #----- 地址爬虫递归大循环开始 -----
        self.numb_addr_get = 0
        self.numb_addr_nosame = 0
        self.numb_addr_eff = 0
        self.count_addr = 1
        
        self.rows = ()#赋值空元组
        
        #种子调用处理控制
        if (numb_rs_p == 0):
            self.crawler_addr_robot(thread_if_p=0,rows_p=self.rows)
        if (numb_rs_p == -1):
            sql = "select id" 
            sql += ",url_main"
            sql += ",root_id"
            sql += ",tree_height"
            sql += " from " + self.url_table
            sql += " where v1=0"
            sql += " order by rand()"
            res, self.rows = conn_data.read_sql(sql)
            self.crawler_addr_robot(thread_if_p=0,rows_p=self.rows)
        if (numb_rs_p > 0):
            sql = "select id" 
            sql += ",url_main"
            sql += ",root_id"
            sql += ",tree_height"
            sql += " from " + self.url_table
            sql += " where v1=0"
            sql += " order by rand()"
            sql += " limit " + str(numb_rs_p)
            res, self.rows = conn_data.read_sql(sql)
            self.crawler_addr_robot(thread_if_p=0,rows_p=self.rows)

    # 地址爬虫工作机器人
    def crawler_addr_robot(self,thread_if_p=0,rows_p=(),t_p=0):

        #单线程模式
        if (thread_if_p ==0):
        
            self.time_start_addr = datetime.datetime.now()
            
            sql_addr = "select id" 
            sql_addr += ",url_main"
            sql_addr += ",root_id"
            sql_addr += ",tree_height"
            sql_addr += " from " + self.url_table
            
            sql_addr += " where v1=0"
            
            # 添加上查询限定条件
            if ("where" in self.dic_addr):
                if (self.dic_addr["where"]):
                    for x in self.dic_addr["where"]:
                        if (x != ""):
                            sql_addr += " and " + x

            sql_addr += " order by "
                
            if ("order" in self.dic_addr):
                for x in self.dic_addr["order"]:
                    sql_addr += x + ","
                sql_addr = sql_addr[:-1]
                    
            sql_addr += " limit 1"
            
            while (self.count_addr < self.runs_addr):
        
                self.time_start_temp = datetime.datetime.now()
                #print (sql) #调试用
                res, rows = conn_data.read_sql(sql_addr)

                if (res < 1):
                    self.id = 0
                    self.root_id = 0
                    self.tree_height = 0
                else:
                    self.id = rows[0][0]
                    self.seed_url = rows[0][1]
                    self.tree_height = rows[0][2]
                    self.root_id = self.id
                try:
                    msg_0 = "种子网址ID：" + str(self.id) + " 网址：" + self.seed_url + ""
                    print (msg_0)
                except:
                    msg_0 = ""
                    pass
                
                # 本次调用的种子地址打上已访问标记
                if (self.addr_run == 1 and self.id !=0 ):
                    sql = "update " + self.url_table + " set v1=1 where id = " + str(self.id)
                    update_if = conn_data.write_sql(sql)

                # 非标准地址种子的校验补丁
                if (".jpg" in self.seed_url or ".gif" in self.seed_url or ".css" in self.seed_url or ".png" in self.seed_url or ".pdf" in self.seed_url or ".js" in self.seed_url):
                    continue
                    
                    
                # 地址方法字典查找
                addr_list = []
                for key in self.dic_addr_chk:
                    if (key in self.seed_url):
                        addr_list = self.dic_addr_chk[key]
                        break
                
                #self.html = self.get_html(url_p = self.seed_url) #测试用
                
                if addr_list:
                    self.html = self.get_html(url_p=self.seed_url,chartset_p=addr_list[0],type_p=addr_list[1])
                else:
                    self.html = self.get_html(url_p = self.seed_url)
                
                # ----查看基本源码用----
                
                
                self.a_url_origin = []
                all_a_text = []

                if (isinstance(self.html,bs_4)):
                    
                    for tag in self.html.select("a"):
                        
                        self.a_url_origin.append(tag.get('href'))
                        arr_t = []
                        str_t = ""
                        
                        try:
                            
                            arr_t.append(tag.get('href'))
                            str_t = str(tag)
                            str_t = str_t.split("</a>")[0]
                            str_t = str_t.split(">")[1]
                            arr_t.append(str_t)
                            all_a_text.append(arr_t)
                            
                        except:
                            pass
                else:
                    
                    self.html = str(self.html)
                    self.html = self.html_clear(code_p=self.html)
                
                #self.file_temp(code_p=self.html) #调试用
                
                # 获得<a>链接型网址
                
                #判别是否是选择性深度优先
                if ("deep_if" in self.dic_addr):
                    deep_if = self.dic_addr["deep_if"]
                else:
                    deep_if = ["no"]

                if ("deep" in self.dic_addr):
                    deep = self.dic_addr["deep"]
                else:
                    deep = ["@@@"]

                # yes进行选择性深度处理

                if (deep_if[0] == "yes"):
                        
                        if (all_a_text):
                            pass
                        else:
                            #self.file_temp(code_p=self.html) #调试用
                            all_a_text = self.get_a_text(self.html)
                            #self.file_temp(code_p=str(all_a_text),path_p = "../data/a.txt") #调试用
                        print ("深度待选网址数：" + str(len(all_a_text)))
                     
                        self.a_url_origin = [""]

                        if (all_a_text):
                            
                            for x in all_a_text:
                            
                                for y in deep:

                                    if ( re.findall(y.split("@@@")[-1],x[-1].strip()) and re.findall(y.split("@@@")[0],x[0].strip())):
                                        self.a_url_origin.append(x[0].strip())
                                        break
                else:
                    
                    # 广度用先BS 然后LXML 最后re的方法
                    if (self.a_url_origin):
                        pass
                    else:
                        try:
                            self.a_url_origin = self.get_url_list_xpath(html=self.html)
                        except:
                            self.a_url_origin = self.get_url_list(html=self.html)
                
                #self.file_temp(code_p=str(self.a_url_origin),path_p = "../data/temp.txt") #调试用
                
                # 网址集清理：
    
                # --- 去除噪点去重复/
                self.a_url_last = self.addr_clear(all_a_url_p = self.a_url_origin)
                print ("去噪后获得：" + str(len(self.a_url_last)) + " 个地址 ")
                
                # --- 补全完整路径/
                self.a_url_last = self.addr_whole(all_a_url = self.a_url_last,url_root = self.seed_url)
                print ("补全后获得：" + str(len(self.a_url_last)) + " 个地址 ")

                # --- 网址特征词清理
                if ("domain" in self.dic_addr):
                    self.a_url_last = self.addr_clear_url(all_a_url_p=self.a_url_last,list_url_p=self.dic_addr["domain"])
                print ("预处理后获得：" + str(len(self.a_url_last)) + " 个地址 ")

                self.numb_addr_get += len(self.a_url_last) #累计获得地址数
                self.numb_addr_nosame += len(self.a_url_last) #累计获得去重数
                self.numb_addr_eff = self.numb_addr_get/self.count_addr
                self.numb_addr_eff = round(self.numb_addr_eff,8)
        
                # --- 权重处理
                if ("power" in self.dic_addr):
                    self.a_url_last = self.addr_power(all_a_url = self.a_url_last,list_p = self.dic_addr["power"])
                else:
                    self.a_url_last = self.addr_power(all_a_url = self.a_url_last,list_p = [""])
                
                if (self.id == 0):
    
                    sql = "insert " + self.url_table + " set "
                    sql += "url_main='" + transfer_quotes(self.seed_url) + "'"
                    sql += ",url_hash ='" + hash_make(transfer_quotes(self.seed_url)) + "'"
                    sql += ",seed_hash='" + self.seed_hash + "'"
                    sql += ",root_id=1"
                    sql += ",seed_type='" + self.seed_type + "'"
                    sql += ",power=0"
                    sql += ",tree_height=" + str(self.tree_height + 1)

                    insert_if = conn_data.write_sql(sql) # 写入待采集网址
                    
                else:
                    
                    for x in self.a_url_last:
                        
                        #网址最后一次校验
                        if (not "://" in x[0]):
                            continue
                            
                        sql = "insert " + self.url_table + " set "
                        sql += "url_main='" + transfer_quotes(x[0]) + "'"
                        sql += ",url_hash ='" + hash_make(transfer_quotes(x[0])) + "'"
                        sql += ",seed_hash='" + self.seed_hash + "'"
                        sql += ",root_id=" + str(self.root_id)
                        sql += ",seed_type='" + self.seed_type + "'"
                        sql += ",power=" + str(x[1]) 
                        sql += ",tree_height=" + str(self.tree_height + 1)
                        
                        insert_if = conn_data.write_sql(sql) # 写入待采集网址
                        
                msg_1 = "第" + str(self.count_addr) + "次处理处理耗时：" +  str(time_cost(self.time_start_temp)) + "秒 累计耗时：" + str(time_cost(self.time_start_addr)) + "秒"
                msg_2 = "累计获得地址数：" + str(self.numb_addr_get) + " 爬虫树深度：" + str(self.tree_height) + " 效率：" + str(self.numb_addr_eff)
                print (msg_1)
                print (msg_2)
                print ("\n")
                # 启用喘气模式
    
                if (self.sleep_p > 0):
                    print ("将要延时 " + str(self.sleep_p)+ " 秒")
                    time.sleep(self.sleep_p)

                #shell模式写入工作日志
                if (self.shell_if == 0):
                    sql_log = "update task set runs_numb=runs_numb+1,run_time_now=run_time_now+1"
                    sql_log += " where seed_name='" + self.seed_name + "'"
                    update_if = conn_way.write_sql(sql_log) # 写入待采集网址
                    log_file = "\"runs\":\"" + str(self.count_addr) + "\"\n" 
                    log_file += ",\"msg_0\":\"" + msg_0 + "\"\n"
                    log_file += ",\"msg_1\":\"" + msg_1 + "\"\n"
                    log_file += ",\"msg_2\":\"" + msg_2 + "\"\n"
                    log_file += ",\"time_last\":\"" + str(datetime.datetime.now()) + "\"\n"
                    log_file = "{\n" + log_file + "}\n"
                    self.file_temp(code_p=log_file,path_p="../data/log/" + self.seed_name + ".txt",char_p="GBK") #写入日志
                    
                # return sql #调试用 一步一执行
                
                # ----任务中断操作----
                # 去重处理
                if (self.numb_addr_nosame >= self.nosame_addr):
            
                    #去重操作
                    print ("地址去重数量阈值成立")
                    self.addr_nosame_do(self="",url_table_p=self.url_table,conn_index=conn_data)
                    time.sleep(10)
                    self.numb_addr_nosame = 0
        
                # 判别爬虫数深度
                if (self.tree_height > self.tree_height_max):
            
                    #去重操作
                    print ("地址去重深度阈值成立")
                    self.addr_nosame_do(self="",url_table_p=self.url_table,conn_index=conn_data)
                    time.sleep(10)
                    break
            
                # 判别爬虫效率值
                if (self.numb_addr_eff < self.eff_addr and self.numb_addr_nosame > self.nosame_addr):
            
                    #去重操作
                    print ("地址去重效率阈值成立")
                    self.addr_nosame_do(self="",url_table_p=self.url_table,conn_index=conn_data)
                    time.sleep(10)
                    break
                #break #调试用
                self.count_addr += 1
                
        # 返回执行情况
        return ("ok")
                
    # 获得域名主成分
    def domain_main_get(self,url_p="",head_p=""):
        
        url_p =url_p.replace(head_p,"")
        arr_t = url_p.split("/")
        url_p = arr_t[0]
        print (url_p)
        return url_p
    
    # 获取html原码的地址列表信息1
    def get_url_list(self, html=''):
        
        all_a_url = re.findall("href=[\"'](.*?)[\"']", html)
        return all_a_url

    
    # 获取html原码的地址列表信息2
    def get_url_list_xpath(self,html=''):
        # print(html)
        # 取得列表块
        doc = etree.HTML(html)
        # 网页上所有a标签的href地址
        all_a_url = doc.xpath('//a/@href')
        #all_img_url = doc.xpath('//img/@src')[0]

        # 地址
        return all_a_url
        
    # 获取超链接_文本对内容
    def get_a_text(self,html=""):
        a_text_p =()
        try:
            a_text_p = re.findall("href=[\"'](.*?)[\"'](.*?)>(.*?)</a>", html)
        except:
            pass
        return a_text_p
        
        
    # 去除噪点
    def addr_clear(self, all_a_url_p):
        list_url = []
        for url in all_a_url_p:
            # 先去除 噪点
            try:
                if  ("javascript" not in url and url.replace('#','') != ""):
                    # 去除重复
                    if url not in list_url:
                        list_url.append(url.strip())
            except:
                pass
        return list_url
        
    #截取相对路径
    def current_url_get(self,url_p=""):
        
        url_t = ""
        if ("://" in url_p):
            url_t = url_p.split('://')[0]
            url_p = url_p.replace(url_t + "://","")
            
            #如果存在二级及以上的虚拟目录
            if ("/" in url_p):
                url_p = url_p.replace('/' + url_p.split('/')[-1], '/')
        
        else:
            return url_t
            
        return url_p

    # 计算完整的路径
    def addr_reckon(self,url,url_root):
        first_charate = url[0:1]
        second_charate = url[1:2]
        current_url = ""
        #print(first_charate)
        if first_charate == '/':
            # 根路径拼接
            url_root_temp = self.get_url_root(url=url_root)
            url = url_root_temp + url
            if second_charate == '/':
                url =  url
        elif  first_charate == '.':
            if second_charate == '/':
                # 当前路径下拼接
                url =  current_url + url[1:]
            elif second_charate == '.':
                # 递归上层路径
                url = url[3:]
                #print(url)
                current_url = self.current_url_get(url_p=url_root)
                #print(url_root)
                url = self.addr_reckon(url=url,url_root=current_url)
        elif '//' in url:
            url = '//'+url.split('//')[1]
        elif ':' in url:
            url = '//'+url.split(':')[1]
        elif url[0:1] in ['?','~','+']:
            url = url
        if (url[0:5] == "http:" and url[0:7] != "http://"):
            url = url[0:5] + "//" + url[6:len(url)]
        return url

    # 简单验证地址的正确性
    def addr_validate(self,url=''):
        url_head = url.split(':')[0]
        if url_head not in ['http','https','ftp']:
            if url[0:2] == '//':
                return True
            return False
        else:
            return True

    # 补全完整路径/
    def addr_whole(self, all_a_url,url_root,url_key=""):
    
        url_temp = []
        current_url = self.current_url_get(url_p=url_root)
        
        for url in all_a_url:
        
            if ("http://"  in url) or ("https://" in url):
                pass
            else:
                # 计算完整路径
                url = self.addr_reckon(url,url_root=current_url)
                
            # 简单验证地址的正确性
            if self.addr_validate(url=url):
                url_temp.append(url.strip())
                
        all_a_url = url_temp
        
        return all_a_url
        
    # 网址特征词清理
    def addr_clear_url(self,all_a_url_p,list_url_p):
        
        list_p = []
        
        for url in all_a_url_p:
            for x in list_url_p:
                if (x in url and x!= ""):
                    list_p.append(url.strip())
                    continue

        return list_p
        
    # 权重
    def addr_power(self, all_a_url,list_p=[".html",".htm",".shtml",""]):
        
        list_url = []
        
        
        for url in all_a_url:
            arr_t = []
            power_p = 0
            
            for i in range(len(list_p)-1):

                if re.match(list_p[i],url): 
                    
                    power_p += 4
                
                power_p += url.count(".")*16
                power_p += url.count("/")*8
                power_p += url.count("?")*4
                power_p += url.count("&")
                power_p += url.count("=")
                power_p += url.count("-")
                power_p += url.count("#")
                    
            arr_t.append(url.strip())
            arr_t.append(power_p)
            list_url.append(arr_t)

        return list_url
        
    # 地址去重 需数据库支持
    @staticmethod
    def addr_nosame_do(self,url_table_p,conn_index=""):
        
        print ("地址去重......\n")
        table_name = code_char_rand()#生成随机表名
        sql = "CREATE TABLE url_" + table_name + " LIKE url"
        create_table_if = conn_index.write_sql(sql)
            
        sql ="INSERT INTO url_" + table_name + "(url_main,url_hash,root_id,tree_height,seed_hash,seed_type,remarks,power,ipc,v1,v2,v3)"
        sql += "SELECT url_main,url_hash,root_id,tree_height,seed_hash,seed_type,remarks,power,ipc,v1,v2,v3 from " + url_table_p + " GROUP BY url_hash order by id asc"
        insert_into_if = conn_index.write_sql(sql)
            
        sql = "drop table " + url_table_p
        drop_if = conn_index.write_sql(sql)
            
        sql = "alter table url_" + table_name + " rename " + url_table_p
        alter_if = conn_index.write_sql(sql)
        
        
# 数据页爬虫类
class Crawler_page(Crawler_base):

    def error_web_list_fun(self):
        #封装查错数据
        self.error_web_list =["404"
        ,"400"
        ,"401"
        ,"403"
        ,"405"
        ,"406"
        ,"407"
        ,"414"
        ,"500"
        ,"501"
        ,"502"
        ,"访问出错"
        ,"页面出错"
        ,"页面不存在"
        ,"不是网站最新内容"
        ,"请登录或注册"
        ,"文章不存在"
        ,"秒后将跳转"
        ,"浏览器版本过低"
        ,"InternalServerError"]
    
    # 出错粗略检查
    def error_chk(self,str_p=""):
    
        str_t = str_p.replace(" ","")
        str_t = str_t.strip('\n')
        error_web_list = self.error_web_list_fun()
        for x in error_web_list:
            
            if (re.search(r'\D' + x + '\D', str_p)):
            
                return x
                
            if (re.search(x + '\D', str_p)):
            
                return x

            if x.isalpha():

                if (str_t.find(x) != -1 ):
                        
                    return x
                        
        return "noerror"
        
    def run_do(self,seed_name_p,numb_burst_p=0,nosame_if_p=0,shell_if_p=1,sleep_p=0,conn_way=""):

        txt = "" #中间结果字符串
        self.count_page = 0 #执行计数 
        self.shell_if = shell_if_p # 是否是命令行模式 输入参数转内部变量
        self.dic_dim = {}
        self.sleep_p = sleep_p
        
        sql = "select dim_name,dim_name_db from struct_dim order by id"
        res_dim, rows_dim = conn_way.read_sql(sql)
        
        if (res_dim > 0):
            for row in rows_dim:
                self.dic_dim[row[0]] = row[1]
        
        # <地址>固定方法库调用
        keep_if,code_name,path_code = self.code_make(seed_name_p=seed_name_p + "_0")
        #引用方法
        run_model =__import__(code_name.replace(".py",""))
        self.dic_addr_chk = run_model.dic_addr_chk
        #print (self.dic_addr_chk) #调试用

        # <结构化>固定方法库调用
        keep_if,code_name,path_code = self.code_make(seed_name_p=seed_name_p + "_1")
        #引用方法
        self.run_model =__import__(code_name.replace(".py",""))
        
        # 引用完毕后删除源文件
        if (keep_if == 0):
            os.remove(path_code)
        
        # 网址参数调用
        sql = "select rule_page,runs_page,nosame_page from rule_crawler where seed_name='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)

        if (res == 1):
            self.rule_page = rows[0][0] # 地址运行参数
            self.runs_page = rows[0][1] # 地址阶段执行参考次数
            self.seed_name = seed_name_p
            self.nosame_page = rows[0][2] # 地址去重阈值
        else:
            return "子任务参数不存在"
            
        self.dic_page = {} #定义参数字典
        #print (self.rule_addr) #调试用
        if (self.rule_page != ""):
            try:
                self.dic_page = eval(self.rule_page)
            except:
                self.rule_page = r'{"order":["power desc"]}'
                self.dic_page = eval(self.rule_page)

        
        self.time_start = datetime.datetime.now() #赋值初始时间

        
        #取得种子网址
        sql = "select seed_url,seed_type from seed where seed_name='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)
        
        if (res == 1):

            self.seed_url = rows[0][0]
            self.seed_type = rows[0][1]
            
        else:

            time.sleep(10)
            return "种子不存在或者有重复项，将重新启动任务。"
            
        # 取得子任务信息
        sql = "select "
        sql += "id,"
        sql += "title,"
        sql += "model_run,"
        sql += "pram_run,"
        sql += "skip_to,"
        sql += "step_if,"
        sql += "pass_if,"
        sql += "login_if,"
        sql += "admin_list "
        sql += "from task "
        sql += "where seed_name ='" + seed_name_p + "'"
        res, rows = conn_way.read_sql(sql)

        if (res > 0):
        
            self.id = rows[0][0] # ID值
            self.title = rows[0][1] #标题值
            self.model_run = rows[0][2] #运行模块
            self.pram_run = rows[0][3] # 运行参数
            self.skip_to = rows[0][4] #结束后跳转地址
            self.step_if = rows[0][5] #是否为单步执行
            self.pass_if = rows[0][6] #是否标记为可执行
            self.login_if = rows[0][7] #受否需要先登录再爬取
            self.admin_list = rows[0][8] #管理权限队列
        
        else:
            
            return "子任务不存在"
            
        self.seed_hash = hash_make(seed_name_p)

        # 地址表名
        self.url_table = "z_url_" + self.seed_hash
        # 数据页表名
        self.page_table = "z_page_" + self.seed_hash
        
            
        #校验子任务的数据页子表
        sql="create table if not exists " + self.page_table + " like page"
        create_if = conn_data.write_sql(sql)
        
        # 简单结构化处理
        if ("struct_if" in self.dic_page):
            self.struct_if = self.dic_page["struct_if"]
        else:
            self.struct_if = ["no"]
        
        #校验子任务的数据页子表
        if (self.struct_if[0] == "yes"):
        
            self.table_name_struct = "z_struct_" + hash_make(self.seed_name)
            sql="create table if not exists " + self.table_name_struct + " like struct"
            create_if = conn_data.write_sql(sql)
            
        # 强制去重
        if (nosame_if_p == 1 ):
            self.page_nosame_do(self="",url_table_p=self.page_table,conn_index=conn_data)
            return "强制去重完成"

        #----- 数据页爬虫递归大循环开始 -----
        self.numb_page_get = 0
        self.numb_page_nosame = 0
        self.count_page = 1
        
        rows = ()#赋值空元组

        
        # 0是单步任务 小于12800是切片处理 大于12800是分页处理 
        if (numb_burst_p ==0):
            
            while (self.count_page <= self.runs_page):
        
                self.time_start_temp = datetime.datetime.now()
        
                sql = "select id" 
                sql += ",url_main"
                sql += " from " + self.url_table
                sql += " where v2=0"

                # 数据库where条件优化采集策略
                if ("where" in self.dic_page):

                    for x in self.dic_page["where"]:
                        if (x != ""):
                            sql += " and " + x + " "

                
                # 数据库排序法优化采集策略
                if ("order" in self.dic_page):
                    sql += " order by "
                    for x in self.dic_page["order"]:
                        sql += x + ","
                    sql = sql[:-1]
                    
                sql += " limit 1"

                res, rows = conn_data.read_sql(sql)
                if res < 1:
                    return "数据源读取错误或在限制阈值内已完成任务"
                print(self.crawler_page_robot(rows_p=rows)) #调用数据页处理机器人
                
                self.count_page += 1
                

        if (numb_burst_p > 0 and numb_burst_p <12800):
            
            #现有数据切片
            sql = "select count(*)" 
            sql += " from " + self.url_table 
            sql += " where v2=0"
            res, rows = conn_data.read_sql(sql)
            numb_rs = rows[0][0]
            
            numb_page_every = int(round(numb_rs / numb_burst_p))

            if (numb_rs % numb_burst_p  == 0):
                numb_page = numb_burst_p
            else:
                numb_page = numb_burst_p + 1
                    
            self.time_start_temp = datetime.datetime.now()
        
            sql = "select id" 
            sql += ",url_main"
            sql += " from " + self.url_table
            sql += " where v2=0"
            
            # 数据库where条件优化采集策略
            if ("where" in self.dic_page):
                if (self.dic_page["where"][0] != ""):
                    sql += " and "
                    for x in self.dic_page["where"]:
                        sql += x + ","
                    sql = sql[:-1]
                
            # 数据库排序法优化采集策略
            if ("order" in self.dic_page):
                if (self.dic_page["order"][0] != ""):
                    sql += " order by "
                    for x in self.dic_page["order"]:
                        sql += x + ","
                    sql = sql[:-1]
                    
            #print (sql) #调试用
            res, rows = conn_data.read_sql(sql)
            if res < 1:
                    return "数据源读取错误或在限制阈值内已完成任务"
            for i in range(numb_page):
                print(self.crawler_page_robot(rows_p=rows[numb_page_every*i:numb_page_every*(i+1)])) #调用数据页处理机器人
                self.count_page =1
                
        if (numb_burst_p >=12800):
            
            i = 1
            while ( i < numb_burst_p):
            
                self.time_start_temp = datetime.datetime.now()
        
                sql = "select id" 
                sql += ",url_main"
                sql += " from " + self.url_table
                sql += " where v2=0"
                
                # 数据库where条件优化采集策略
                if ("where" in self.dic_page):

                    if (self.dic_page["where"][0] != ""):
                        sql += " and "
                        for x in self.dic_page["where"]:
                            sql += x + ","
                        sql = sql[:-1]
                
                # 数据库排序法优化采集策略
                if ("order" in self.dic_page):
                
                    if (self.dic_page["order"][0] != ""):
                        sql += " order by "
                        for x in self.dic_page["order"]:
                            sql += x + ","
                        sql = sql[:-1]
                    
                sql += " limit " + str(numb_burst_p)
                #print (sql) #调试用

                res, rows = conn_data.read_sql(sql)
                if res < 1:
                    return "数据源读取错误或在限制阈值内已完成任务"
                print(self.crawler_page_robot(rows_p=rows)) #调用数据页处理机器人
                i += 1
                self.count_page = i

        #self.page_nosame_do(self="",url_table_p=self.page_table,conn_index=conn_data) # 多线程执行完去重退出
    
    # 数据页爬虫工作机器人
    def crawler_page_robot(self,rows_p=(),conn_way=""):
        
        html_p = "" #网页原码字符串
        chart_is = "utf-8" # 指定默认字符编码
        #rows_p = ((4, 'http://www.autohome.com.cn/news/201706/903385.html#pvareaid=2023114'),) #调试用
        time_start_page = datetime.datetime.now()
        txt = ""
        id_p = 0
        url_page = ""
        
        for row in rows_p:
        
            id_p = row[0]
            url_page = row[1]
            
            # 本次调用的种子地址打上已访问标记
            sql = "update " + self.url_table + " set v2=1 where id = " + str(id_p)
            update_if = conn_data.write_sql(sql)
            
            ## 地址方法字典查找
            addr_list = []
            for key in self.dic_addr_chk:
                if (key in url_page):
                    addr_list = self.dic_addr_chk[key]
                    break
                    
            # 获得源码
            if addr_list:
                try:
                    html_p = self.get_html(url_p = url_page,chartset_p=addr_list[0],type_p=addr_list[1])
                    chart_is = addr_list[0] #获得已知网页编码
                except:
                    pass
            else:
                try:
                    html_p = self.get_html(url_p = url_page)
                    chart_is = self.pick_charset(html_p) #赋值默认编码
                except:
                    pass
                    
            # 开启喘气模式
            if (self.sleep_p > 0):
                print ("将延时" + str(self.sleep_p) +" 秒")
                time.sleep(self.sleep_p)

            # self.file_temp(code_p=html_p,char_p=chart_is) # 调试用

            len_html = len(html_p)
            
            # 源码初级校验
            if (len_html < 16):
                break
                return "源码长度[" + str(len_html) + "]过短，按异常情况不予以处理！\n"
                
            
            if (self.struct_if[0] == "yes" and addr_list):
                dic_res ={}
                try:
                    dic_res = self.run_model.run_it(html_p=html_p,to_do="lx",url="")
                except:
                    pass
                if (dic_res and self.dic_dim):
                    try:
                        print ("结构化结果：" + str(dic_res))# 
                    except:
                        pass
                    
                    sql = "insert " + self.table_name_struct + " set "
                    sql += "seed_name='" + self.seed_name + "'"
                    sql += ",seed_type='" + self.seed_type + "'"
                    sql += ",url_hash ='" + hash_make(url_page) + "'"
                    #print (sql)
                    insert_if = conn_data.write_sql(sql) # 建立初始记录
                    sql = "select last_insert_id()"
                    res_id, rows_id = conn_data.read_sql(sql)
                    if (res_id > 0):
                        sid = rows_id[0][0]
                        print ("新增结构化数据记录号:" + str(sid))
                        sql_head_stru = "update " + self.table_name_struct + " set "
                        sql_where_stru = " where id=" + str(sid)
                        for x in dic_res:
                            if (x in self.dic_dim):
                                str_t = str(dic_res[x])
                                str_t = str_t.replace("\\t","")
                                str_t = str_t.replace("\\n","")
                                str_t = str_t.replace("\\r","")
                                str_t = str_t.replace("\xa0","")
                                str_t = gbk_bug(str_t)
                                str_t = transfer_quotes(str_t)
                                sql_data_stru = self.dic_dim[x] + "='" + str_t +"'"
                                #print (sql_head_stru + sql_data_stru + sql_where_stru) #调试用
                                update_if = conn_data.write_sql(sql_head_stru + sql_data_stru + sql_where_stru)
                        
            # 源码的初级结构化处理加次级简单校验
            soup = bs_4(html_p)
            title_p = "nothing"
            try:
                title_p = str(soup.find("title"))
                title_p = re.sub(r'<.title>',"",title_p)
                title_p = re.sub(r'<title.*>',"",title_p)
            except:
                pass
                
            #错误页检查
            if ("word_chk_if" in self.dic_page):
                if (self.dic_page["word_chk_if"] == "yes"):
                    error_if = self.error_chk(str_p=title_p)
                    if (error_if != "noerror"):
                        return "包含<" + error_if + ">，将不予以处理！"
                        
            soup = bs_4(html_p, "html.parser")  # 创建BeautifulSoup对象
            body_p = str(soup.body) # 获取body部分
            
            label_p = "nothing"
            try:
                label_p = str(soup.find(attrs={"name":"keywords"})['content'])
            except:
                pass

            soup_body = bs_4(body_p)
            [script.extract() for script in soup_body.findAll('script')]
            [style.extract() for style in soup_body.findAll('style')]
            content_p = soup_body.prettify()
            content_p = soup_body.get_text()
            content_main = Content_main()
            content_p = str(content_p)
            #content_p = content_main.extract(content_p) # 正文自然语言规则决策树识别
            digest_p = content_main.extract(content_p) # 正文自然语言规则决策树识别
            #digest_p = digest_p[0:256] # 临时摘要处理
            
            #错误页检查
            if ("word_chk_if" in self.dic_page):
                if (self.dic_page["word_chk_if"] == "yes"):
                    error_if = self.error_chk(str_p=title_p)
                    if (error_if != "noerror"):
                        return "包含<" + error_if + ">，将不予以处理！"
            
            # 运行信息展示
            msg_0 = "地址id：[" + str(id_p) + "] 地址：" + url_page
            print(msg_0)
            msg_1 = "源码长度：" + str(len_html)
            print (msg_1)
            try:
                print ("标题：" + title_p[0:128])
            except:
                pass
            try:
                print ("临时摘要:" + digest_p[0:128])
            except:
                pass
            
            # 存入数据页子表
            
            sql = "insert " + self.page_table + " set "
            sql += "seed_name='" + self.seed_name + "'"
            sql += ",seed_type='" + self.seed_type + "'"
            sql += ",url_main='" + url_page + "'"
            sql += ",url_hash ='" + hash_make(url_page) + "'"
            sql += ",title='" + transfer_quotes(title_p) + "'"
            sql += ",title_hash ='" + hash_make(title_p) + "'"
            sql += ",content='" + transfer_quotes(content_p) + "'"
            sql += ",label='" + transfer_quotes(label_p) + "'"
            sql += ",label_hash ='" + hash_make(label_p) + "'"
            sql += ",digest='" + transfer_quotes(digest_p) + "'"
            sql += ",digest_hash ='" + hash_make(digest_p) + "'"

            insert_if = conn_data.write_sql(sql) # 写入数据也主库
            
            # 写入数据页原码
            
            # ---若临时文件夹不存在，则创建一个
            path_page = "../data/page/" + hash_make(self.seed_name) + "/"
            if not os.path.exists(path_page):
                os.makedirs(path_page)
            self.file_temp(code_p=html_p,path_p=path_page + hash_make(url_page) + ".html",char_p=chart_is)

            msg_2 = "本次调用总计耗时：" + str(time_cost(time_start_page)) + "秒\n"
            txt += msg_2

            #shell模式写入工作日志
            if (self.shell_if == 0):
                sql_log = "update task set runs_numb=runs_numb+1,run_time_now=run_time_now+1"
                sql_log += " where seed_name='" + self.seed_name + "'"
                update_if = conn_way.write_sql(sql_log) # 写入待处理数据页信息
                log_file = "\"runs\":\"" + str(self.count_page) + "\"\n" 
                log_file += ",\"msg_0\":\"计数:[" + str(self.count_page) + "] " + msg_0 + "\"\n"
                #log_file += ",\"msg_1\":\"" + msg_1 + "\"\n"
                #log_file += ",\"msg_2\":\"" + msg_2 + "\"\n"
                log_file += ",\"time_last\":\"" + str(datetime.datetime.now()) + "\"\n"
                log_file = "{\n" + log_file + "}\n"
                self.file_temp(code_p=log_file,path_p="../data/log/" + self.seed_name + ".txt",char_p="GBK") #写入日志
        
        print ("\n") #换行
        return txt
        
   #网页去重
    @staticmethod
    def page_nosame_do(self,url_table_p,conn_index=""):
    
        print ("数据页去重......\n")
        
        table_name = code_char_rand()#生成随机表名
        
        sql = "CREATE TABLE page_" + table_name + " LIKE page"
        #print(sql) #调试用
        create_table_if = conn_index.write_sql(sql)
            
        sql ="INSERT INTO page_" + table_name + "(seed_name,seed_type,url_main,url_hash,title,title_hash,content,smt,seq,simi,hot,label,label_hash,digest,digest_hash,time_reg,time_edit,power,score,opinion,rd,v1,v2,v3,v4,v5)"
        sql += "SELECT seed_name,seed_type,url_main,url_hash,title,title_hash,content,smt,seq,simi,hot,label,label_hash,digest,digest_hash,time_reg,time_edit,power,score,opinion,rd,v1,v2,v3,v4,v5 from " + url_table_p + " GROUP BY digest_hash order by id asc"
        #print(sql) #调试用
        insert_into_if = conn_index.write_sql(sql)
            
        sql = "drop table " + url_table_p
        #print(sql) #调试用
        drop_if = conn_index.write_sql(sql)
            
        sql = "alter table page_" + table_name + " rename " + url_table_p
        #print(sql) #调试用
        alter_if = conn_index.write_sql(sql)
        
        
# 结构化爬虫类
class Crawler_stru(Crawler_base):

    def run_do(self,seed_name_p,numb_rs_p=0,nosame_if_p=0,shell_if_p=0,sleep_p=0):
        
        self.sleep_p = sleep_p #设置喘气间隔参数
        txt = "" #中间结果字符串
        self.count_page = 0 #执行计数 
        self.shell_if = shell_if_p # 是否是命令行模式 输入参数转内部变量
        self.dic_dim = {}
        self.seed_name = seed_name_p
        self.stru_md5 = hash_make(seed_name_p)
        self.table_name = "z_page_" + self.stru_md5
        
        self.table_name_struct = "z_struct_" + hash_make(self.seed_name)
        sql="create table if not exists " + self.table_name_struct + " like struct"
        create_if = conn_data.write_sql(sql)
        
        sql = "select dim_name,dim_name_db from struct_dim order by id"
        res_dim, rows_dim = conn_way.read_sql(sql)
        
        if (res_dim > 0):
            for row in rows_dim:
                self.dic_dim[row[0]] = row[1]
        # <地址>固定方法库调用
        keep_if,code_name,path_code = self.code_make(seed_name_p=seed_name_p + "_0")
        #引用方法
        run_model =__import__(code_name.replace(".py",""))
        self.dic_addr_chk = run_model.dic_addr_chk
        #print (self.dic_addr_chk) #调试用

        # <结构化>固定方法库调用
        keep_if,code_name,path_code = self.code_make(seed_name_p=seed_name_p + "_1")
        #引用方法
        self.run_model =__import__(code_name.replace(".py",""))
        
        # 引用完毕后删除源文件
        if (keep_if == 0):
            os.remove(path_code)
        #根据numb_rs值将数据页分块导入
        sql = "select url_main,url_hash,seed_type from " + self.table_name + " where v1=0"
        if (numb_rs_p > 0):
            sql += " limit " + str(numb_rs_p)
        res, rows = conn_data.read_sql(sql)
        if res < 1:
            return "数据源读取错误或在限制阈值内已完成任务"
        else:
            print(self.crawler_stru_robot(rows_p=rows))
        #执行处理循环体
        #收尾处理
        
        return txt
        
    # 数据页爬虫工作机器人
    def crawler_stru_robot(self,rows_p):
        txt = ""
        addr_list = []
        path_page = ""
        html_code =""
        msg_0 = ""
        self.count_stru = 0
        
        for row in rows_p:
            sql = "update " + self.table_name + " set v1=1 where url_hash= '" + row[1] + "'"
            update_if = conn_data.write_sql(sql)

            ## 地址方法字典查找
            for key in self.dic_addr_chk:
                if (key in row[0]):
                    addr_list = self.dic_addr_chk[key]
                    break

            # 获得源码
            path_page ="../data/page/" + self.stru_md5 + "/" + row[1] + ".html"
            
            if os.path.exists(path_page):
                if (addr_list):
                    with open(path_page, encoding=addr_list[0]) as f:
                        html_code = f.read()
            
            #self.file_temp(code_p=html_code,char_p=addr_list[0]) # 调试用
            
            if (html_code == ""):

                #重新获得源码
                if addr_list:
                    try:
                        html_p = self.get_html(url_p = row[0],chartset_p=addr_list[0],type_p=addr_list[1])
                    except:
                        pass
                else:
                    try:
                        html_p = self.get_html(url_p = row[0])
                    except:
                        pass
                time.sleep(10) # 强制喘气10秒
                
            dic_res = {}
            
            html_code = self.html_clear(code_p=html_code) #html清理
            #self.file_temp(code_p=html_code,char_p=addr_list[0]) # 调试用
            try:
                dic_res = self.run_model.run_it(html_p=html_code,to_do="lx",url="")
            except:
                pass
            
            if (not dic_res):
                print (row[0] + "任务失败")
                continue
            
            if (dic_res and self.dic_dim):
                
                try:
                    print ("结构化结果：" + str(dic_res))# 
                except:
                    pass
                    
                sql = "insert " + self.table_name_struct + " set "
                sql += "seed_name='" + self.seed_name + "'"
                sql += ",seed_type='" + row[2] + "'"
                sql += ",url_hash ='" + hash_make(row[0]) + "'"
                #print (sql)
                insert_if = conn_data.write_sql(sql) # 建立初始记录
                sql = "select last_insert_id()"
                res_id, rows_id = conn_data.read_sql(sql)
                if (res_id > 0):
                    sid = rows_id[0][0]
                    msg_0 ="新增结构化数据记录号:" + str(sid)
                    txt += msg_0
                    sql_head_stru = "update " + self.table_name_struct + " set "
                    sql_where_stru = " where id=" + str(sid)
                    for x in dic_res:
                        if (x in self.dic_dim):
                            str_t = str(dic_res[x])
                            str_t = str_t.replace("\\t","")
                            str_t = str_t.replace("\\n","")
                            str_t = str_t.replace("\\r","")
                            str_t = str_t.replace("\\xa0","")
                            str_t = gbk_bug(str_t)
                            str_t = transfer_quotes(str_t)
                            sql_data_stru = self.dic_dim[x] + "=CONCAT('" + str_t + "'," + self.dic_dim[x] + ") "
                            sql_bug_null = sql_head_stru + " " + self.dic_dim[x] + "='' where isnull(" + self.dic_dim[x] + ") and id=" + str(sid)
                            #print (sql_bug_null) # 调试用
                            update_if = conn_data.write_sql(sql_bug_null)
                            #print (sql_head_stru + sql_data_stru + sql_where_stru) #调试用
                            update_if = conn_data.write_sql(sql_head_stru + sql_data_stru + sql_where_stru)

            #shell模式写入工作日志
            if (self.shell_if == 0):
                sql_log = "update task set runs_numb=runs_numb+1,run_time_now=run_time_now+1"
                sql_log += " where seed_name='" + self.seed_name + "'"
                update_if = conn_way.write_sql(sql_log) # 写入待处理数据页信息
                log_file = "\"runs\":\"" + str(self.count_stru) + "\"\n" 
                log_file += ",\"msg_0\":\"计数:[" + str(self.count_stru) + "] " + msg_0 + "\"\n"
                log_file += ",\"time_last\":\"" + str(datetime.datetime.now()) + "\"\n"
                log_file = "{\n" + log_file + "}\n"
                self.file_temp(code_p=log_file,path_p="../data/log/" + self.seed_name + ".txt",char_p="GBK") #写入日志
            
            self.count_stru += 1 #执行计数器自增1
        
        # 启用喘气模式
        if (self.sleep_p > 0):
            print ("将要延时 " + str(self.sleep_p)+ " 秒")
            time.sleep(self.sleep_p)
        
        # 返回执行情况
        return txt
    
    # 以下为备份解决方案
    # 结构化解析页面总的方法
    def stru_dim_get(self, html_p,way_p="lx"):
        """
        单分支输出 lx和bs是并行同等效力的方法 re的方法作为最后的后备方法
        rule_p 抽取规则,way_p校验方法 都有内部方法库取得 
        """
        list_p = []

        if (html_p):
        
            if (way_p == "lx"):
                lisp_p = self.res_chk(self.stru_lxml(html_p,a[1])) # 用lxml方法处理后并校验
                # 处理失败 用下一个方法
                if (not lisp_p):
                    lisp_p = self.res_chk(self.stru_re(html_p,a[1])) # 用正则的方法处理后并校验
                return list_p
            if (way_p == "bs"):
                lisp_p = self.res_chk(self.stru_bs(html_p,a[1])) # 用lxml方法处理后并校验
                # 处理失败 用下一个方法
                if (not lisp_p):
                    lisp_p = self.res_chk(self.stru_re(html_p,a[1])) # 用正则的方法处理后并校验
                return list_p
            if (way_p == "re"):
                lisp_p = self.res_chk(self.stru_re(html_p,a[1])) # 用lxml方法处理后并校验
                # 处理失败 用下一个方法
                return list_p
                
        return list_p
        
    # 结构化xml的方法
    def stru_lxml(self, html_p, rule_p):
        print ("lxml")
        list_p = []
        return list_p
        
    # 结构化BeautifulSoup的方法
    def stru_bs(self, html_p, rule_p):
        print ("bs")
        print(type(rule_p))  # 调试语句

        rule_p = eval(rule_p)
        # 解析
        soup = bs_4(html_p, "lxml")

        list_p = []
        for task_id, rule_list in rule_p.items():
            # 特征, 查询规则, 方法
            for feat, rule, func, num in rule_list:
                value_list = soup.select(rule)

                list_p.append({feat: value_list})

        return list_p

    # 结构化正则的方法
    def stru_re(self, html_p, rule_p):
        print ("re")
        list_p = []
        print(type(rule_p))  # 调试语句

        rule_p = eval(rule_p)
        
        # 方法1
        for task_id, rule_list in rule_p.items():
            # 特征, 查询规则, 方法
            for feat, rule, func, num in rule_list:
                value_list = [match.group("content") for match in list(re.finditer(rule, html_p))]  # 直接获取(?P<content>)的标签
                list_p.append({feat: value_list})

        # 方法2
        if (not list_p):
            for task_id, rule_list in rule_p.items():
            # 特征, 查询规则, 方法
                for feat, rule, func, num in rule_list:
                # 抽取
                    value_list_ = [match_string for match_string in list(re.findall(rule, html_p))]

                # 过滤
                    value_list = [re.sub(rule, "", value) for value in value_list_]
                    list_p.append({feat: value_list})

        return list_p
        
    # 结构化结果校验
    def res_chk(self, list_p,way_p):
        print ("res_chk")
        #校验只输出合理的结果集
        return list_p

# 索引爬虫类
class Crawler_index(Crawler_base):

    def run_do(self,seed_name_p="",numb_rs_p=0,nosame_if_p=0,shell_if_p=0,conn_data="",conn_index=""):
    
        import math # 引入数学计算模块
        txt = ""
        t_name_p = "page"
        dic_p = {}
        
        if (seed_name_p != ""):
            t_name_p = "z_page_" + hash_make(seed_name_p)
        sql = "select url_hash,seq,hot,power,score,opinion,id from " + t_name_p + " where v2=0"
        #sql += " limit 1" #调试用
        # 任务处理条件限定
        if (numb_rs_p > 0):
            sql += " limit " + str(numb_rs_p)
        print (sql) # 调试用
        res,rows = conn_data.read_sql(sql)
        
        if (res < 1):
            return "知识切片总表为空或读取错误"
            
        numb_rs_all = res
        count_do = 1

        #数据切片的主循环
        for row in rows:
            
            hash = row[0]
            numb_list = 0
            rank = 0.0
            numb_key_all = 1
            pid = row[6]
            
            sql = "update " + t_name_p + " set v2=1 where url_hash ='" + hash + "'" #打上处理过的访问标记
            updtae_if = conn_data.write_sql(sql)
            
            try:
                dic_p = eval(row[1])
            except:
                continue
            
            print (row[2],row[3],row[4],row[5]) #调试用
            
            if (not row[2] is None):
                x0 = row[2]
            else:
                x0 = 0
                
            if (not row[3] is None):
                x1 = row[3]
            else:
                x1 = 0
                
            if (not row[4] is None):
                x2 = row[4]
            else:
                x2 = 0
            
            # 情感处理
            if (not row[5] is None):
            
                # 负面
                if (row[5] == "neg"):
                    x3 = -1
                # 中性
                if (row[5] == "neu"):
                    x3 = 0
                # 正面
                if (row[5] == "pos"):
                    x3 = 0
            else:
            
                x3 = 0
                
            print (x0,x1,x2,x3) #调试用
            
            if ("numb_key_ldae" in dic_p):
                numb_list = dic_p["numb_key_ldae"][0]
                del dic_p["numb_key_ldae"]
            
            sql = "select idf from index_main where keyword ='numb_key_ldae'"
            res_t,rows_t = conn_data.read_sql(sql)
            if (res_t < 1):
                return "主索引表为空或读取失败"
            else:
                numb_key_all = rows_t[0][0]
            
            # 操作主循环
            for x in dic_p:
                rank = 0
                #取得IDF数字
                sql = "select idf from index_main where keyword ='" + x + "'"
                res_t,rows_t = conn_data.read_sql(sql)
                if (res_t < 1):
                    numb_idf = 1
                else:
                    numb_idf = rows_t[0][0]
                #print ("tf:" + str(len(dic_p[x])/numb_list) + " idf频数:" + str(numb_idf) + " idf:" + str(math.log(numb_key_all/numb_idf))) #调试用 
                #rank值计算
                #诚意系数 1 长正文的数据页优先 2 标题优先 3 最先提及的优先 
                for y in dic_p[x]:
                    rank += numb_list/y # 诚意系数
                try:
                    rank = rank*len(dic_p[x])/numb_list*math.log(numb_key_all/numb_idf)
                except:
                    pass
                rank = int(rank*923337203) # 整数化 便于快速排名
                #print (x + " 排名值：" + str(rank))
                # 存入数据页子表
                try:
                    sql="create table if not exists z_invert_" + hash_make(x) + " like z_invert"
                    create_if = conn_index.write_sql(sql)
                    sql = "insert z_invert_" + hash_make(x)+ " set "
                    sql += " pid='" + str(pid) + "',"
                    sql += " hash='" + hash + "',"
                    sql += "rank=" + str(rank) + ","
                    sql += "x0=" + str(x0) + ","
                    sql += "x1=" + str(x1) + ","
                    sql += "x2=" + str(x2) + ","
                    sql += "x3=" + str(x3) + " "
                    insert_if = conn_index.write_sql(sql)
                    #print (sql) #调试用
                except:
                    pass


            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
            
        return txt
        
# 问答索引爬虫类
class Crawler_qa(Crawler_base):

    def run_do(self,seed_name_p="",numb_rs_p=0,nosame_if_p=0,shell_if_p=0,hot_if_p=1,conn_index="",conn_data=""):
        
        import math # 引入数学计算模块
        
        # 进行热点处理
        dic_kw_q= {} # 问题关键词热度字典
        dic_kw_a= {} # 答案关键热度字典 
        data_name_p = config.dic_config["name_mysql_after"] # 数据库后缀参数
        rank_p = 0
        div_v_q = {}
        dic_v_a = {}
        
        if (hot_if_p == 1):
            import diy.inc_result_main as inc_result_main
            hot = inc_result_main.Hot() # 热点对象实例化
            # 构造热点关键词字典
            sql = "select keyword,power from ldae_way_" + data_name_p + ".keyword_hot_q"
            res_t,rows_t = conn_index.read_sql(sql)
            if (res_t > 0):
                for y in rows_t:
                    dic_kw_q[y[0]] = y[1]
                
            sql = "select keyword,power from ldae_way_" + data_name_p + ".keyword_hot_a"
            res_t,rows_t = conn_index.read_sql(sql)
            if (res_t > 0):
                for y in rows_t:
                    dic_kw_a[y[0]] = y[1]
                    
            #print (dic_kw_q,dic_kw_a) # 调试用
        
        txt = ""
        t_name_p = "qa"
        dic_p = {}
        dic_v_q = {} # 问题的词向量字典
        div_v_a = {} # 答案的词向量字典
        numb_key_all = 0
        site_max = 0.0 # 位置最大值
        what = 0
        
        # 获得问答对总数
        sql = "select count(*) from qa"
        res_t,rows_t = conn_data.read_sql(sql)
            
        if (res_t < 1):
            return "主索引表为空或读取失败"
        else:
            numb_file_all = rows_t[0][0]
        
        if (seed_name_p != ""):
            t_name_p = "z_qa_" + hash_make(seed_name_p)
        
        sql = "select hash,seq_q,seq_a,id,what from " + t_name_p + " where v2=0 order by rank desc "
        
        # 任务处理条件限定
        if (numb_rs_p > 0):
            sql += " limit " + str(numb_rs_p)
            
        #sql += " limit 1" #调试用
        res,rows = conn_data.read_sql(sql)
        print (sql) # 调试用

        if (res < 1):
            return "知识切片总表为空或读取错误"
            
        numb_rs_all = res
        count_do = 1

        #数据切片的主循环
        for row in rows:
            
            hash = row[0]
            numb_list = 0
            rank = 0.0
            numb_key_all = 1
            pid = row[3]
            what = row[4]
            dic_t_1 = {} # 问题的词向量字典
            dic_t_2 = {} # 答案的词向量字典
            rank_p = 0
            
            try:
                dic_t_1 = eval(row[1])
                dic_t_2 = eval(row[2])
            except:
                dic_t_1 = {}
                dic_t_2 = {}
            
            sql = "update " + t_name_p + " set v2=1"
            if (hot_if_p == 1):
                # 计算热点得分
                
                if (dic_t_1):
                    # print (dic_t_1)
                    rank_p = hot.hot_rank_c(dic_t_1,dic_kw_p=dic_kw_q)
                if (dic_t_2):
                    # print (dic_t_2)
                    rank_p += hot.hot_rank_c(dic_t_2,dic_kw_p=dic_kw_a)
                if (rank_p > 0):
                    sql += ",rank=" + str(rank_p)
                    print ("热点值:",rank_p) # 调试用
                    
            sql += " where id=" + str(pid) + " " #打上处理过的访问标记
            updtae_if = conn_data.write_sql(sql)
            
            # 问题的索引处理
            
            table_index = "index_question" #索引表
            table_child = "z_question_" #子表前缀
            
            try:
                dic_p= eval(row[1])
            except:
                continue
            
            # 排名参数赋初值
            
            x0 = 0.0
            x1 = 0.0
            x2 = 0.0
            x3 = 0.0
            
            if ("numb_key_ldae" in dic_p):
                del dic_p["numb_key_ldae"]
            
            # 获得正排的总词长
            numb_tf_all = 0
            for x in dic_p:
                numb_tf_all += len(dic_p[x])
            
            # 操作主循环
            for x in dic_p:
            
                rank = 0
                #取得IDF数字
                sql = "select idf from " + table_index + " where keyword ='" + x + "'"
                res_t,rows_t = conn_data.read_sql(sql)
                if (res_t < 1):
                    numb_idf = 1
                else:
                    numb_idf = rows_t[0][0] + 1
                #print ("tf:" + str(len(dic_p[x])/numb_list) + " idf频数:" + str(numb_idf) + " idf:" + str(math.log(numb_key_all/numb_idf))) #调试用 
                #rank值计算
                rank = len(dic_p[x])/numb_tf_all*math.log(numb_file_all/numb_idf)
                
                # 问题词向量处理
                dic_v_q[x] = round(rank,8)
                
                rank = int(rank*92333720) # 整数化 便于快速排名
                #引入说明文校正 标题型 总分总型结构
                svg_y = int(numb_tf_all/2)+1 #中位欧式距离原点
                x0 = 0.0 
                for y in dic_p[x]:
                    x0 += round(abs(svg_y-y)/svg_y,8)
                
                    
                #print (x + " 排名值：" + str(rank))
                
                # 存入索引子表
                try:
                    sql="create table if not exists " + table_child  + hash_make(x) + " like z_invert"
                    create_if = conn_index.write_sql(sql)
                    sql = "insert " + table_child + hash_make(x)+ " set "
                    sql += " pid='" + str(pid) + "',"
                    sql += " hash='" + hash + "',"
                    sql += "rank=" + str(rank) + ","
                    sql += "x0=" + str(x0) + ","
                    sql += "x1=" + str(x1) + ","
                    sql += "x2=" + str(x2) + ","
                    sql += "x3=" + str(x3) + ","
                    sql += "what=" + str(what) + " "
                    insert_if = conn_index.write_sql(sql)
                    #print (sql) #调试用
                except:
                    pass
                
                
            # 答案的索引处理
            
            table_index = "index_answer" #索引表
            table_child = "z_answer_" #子表前缀
            
            try:
                dic_p= eval(row[2])
            except:
                continue

            # 排名参数赋初值
            
            x0 = 0.0
            x1 = 0.0
            x2 = 0.0
            x3 = 0.0
            
            if ("numb_key_ldae" in dic_p):
                del dic_p["numb_key_ldae"]
                
            # 获得正排的总词长
            numb_tf_all = 0
            for x in dic_p:
                numb_tf_all += len(dic_p[x])
            
            # 操作主循环
            for x in dic_p:
            
                rank = 0
                #取得IDF数字
                sql = "select idf from " + table_index + " where keyword ='" + x + "'"
                res_t,rows_t = conn_data.read_sql(sql)
                if (res_t < 1):
                    numb_idf = 1
                else:
                    numb_idf = rows_t[0][0] + 1
                #print ("tf:" + str(len(dic_p[x])/numb_list) + " idf频数:" + str(numb_idf) + " idf:" + str(math.log(numb_key_all/numb_idf))) #调试用 
                #rank值计算
                rank = len(dic_p[x])/numb_tf_all*math.log(numb_file_all/numb_idf)
                
                # 答案词向量处理
                dic_v_a[x] = [round(rank,8),0.0]
                
                rank = int(rank*92333720) # 整数化 便于快速排名
                #引入说明文校正 标题型 总分总型结构
                svg_y = int(numb_tf_all/2)+1 #中位欧式距离原点
                x0 = 0.0 
                for y in dic_p[x]:
                    x0 += round(abs(svg_y-y)/svg_y,8)
                
                dic_v_a[x][1] = x0 #文本向量补充位置权重
                
                # 存入索引子表
                try:
                    sql="create table if not exists " + table_child + hash_make(x) + " like z_invert"
                    create_if = conn_index.write_sql(sql)
                    sql = "insert " + table_child + hash_make(x)+ " set "
                    sql += " pid='" + str(pid) + "',"
                    sql += " hash='" + hash + "',"
                    sql += "rank=" + str(rank) + ","
                    sql += "x0=" + str(x0) + ","
                    sql += "x1=" + str(x1) + ","
                    sql += "x2=" + str(x2) + ","
                    sql += "x3=" + str(x3) + ","
                    sql += "what=" + str(what) + " "
                    insert_if = conn_index.write_sql(sql)
                    #print (sql) #调试用
                except:
                    pass

            # 文本向量存入主表
            sql = "update " + t_name_p + " set vec_q_mk='" + str(dic_v_q).replace("'","\"") + "',vec_a_mk='" + str(dic_v_a).replace("'","\"") + "' where id=" + str(pid) + " " #打上处理过的访问标记
            updtae_if = conn_data.write_sql(sql)

            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_rs_all) + "%")
            count_do += 1
            
        return txt
        
        
# 内部爬虫基础类
class crawler_inside_base(object):
    
    def args_get_json(self,args={}):
    
        path_last = ""
        
        #print ("参数字典",args) # 调试用
        # 参数处理
        if ("file_name" in args):
            file_name_p = args["file_name"]
        else:
            file_name_p = ""
        if ("path" in args):
            path_p = args["path"].replace("@",":")
        else:
            path_p = ""
        if ("database" in args):
            database_p = args["database"]
        else:
            database_p = ""
        if ("table" in args):
            table_p = args["table"]
        else:
            table_p = "test"
            
        if ("row2row" in args):
            row2row = args["row2row"]
        else:
            row2row = ""
            
        if ("sql_add" in args):
            sql_add = args["sql_add"]
        else:
            sql_add = ""
            
        path_last = path_p + file_name_p
        
        return path_last,file_name_p,path_p,database_p,table_p,sql_add,row2row
        
# 内部数据转mysql
class File2mysql(crawler_inside_base):
    
    def json2mysql_baidu(self,args={}):
        
        self.time_start = datetime.datetime.now()
        result = ""
        jsonobj = {}
        list_t = []
        sql = ""
        sql_head = "insert into "
        sql_mid = ""
        sql_foot = ""
        list_c = []
        dic_c = {}
        list_s = []
        # 参数处理
        path_last,file_name_p,path_p,database_p,table_p,sql_add,row2row = self.args_get_json(args)
        
        if (table_p !=""):
            sql_head += table_p + " set "
        else:
            result = "数据库表名不能为空！"
            return result
            
        if (row2row != ""):
            row2row = row2row.replace("@~@","\":\"")
            row2row = row2row.replace("@!@","\",\"")
            row2row = "{\"" + row2row + "\"}"
            try:
                dic_c = eval(row2row)
            except:
                pass
                
        if (sql_add != ""):
            sql_add = sql_add.replace("@~@","=") + ", "
            sql_head += sql_add
                
        #数据库链接对象
        
        if (database_p != ""):
            
            rs_do_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"],database_p, int(config.dic_config["port_mysql"]))
            sql = "select COLUMN_NAME from INFORMATION_SCHEMA.Columns where table_name='" + table_p + "' and table_schema='" + database_p + "'"
            res_c, rows_c = rs_do_mysql.read_sql(sql)
            if (res_c < 1):
                result = "数据库名或表名错误！"
                rs_do_mysql.close_cur() #关闭数据游标
                rs_do_mysql.close() #关闭数据连接
                return result
            else:
                for row in rows_c:
                    list_c.append(row[0])
        else:
            result = "数据库名不能为空！"
            return result
            
        # 引用相关模块
        import linecache
        import json
        
        #读
        lines = linecache.getlines(path_last)
        i = 0
        j = 0
        for line in lines:
            
            jsonobj = {}
            try:
                jsonobj = json.loads(line)
                
            except:
                pass
                
            sql_mid = ""
            list_s = []
            
            list_t = []
            
            for x in jsonobj:
            
                #print (x," == ",jsonobj[x],"\n\n\n\n\n") # 调试用
                
                if (x=="documents"):
                
                    list_t = jsonobj[x]

                else:

                    if (x in list_c):
                    
                        # 评估分的补丁
                        if (x == "match_scores"):
                        
                            if (not jsonobj[x]):
                                sql_mid += x + "=0.0,"
                            else:
                                sql_mid += x + "=" + str(jsonobj[x]).replace("[","").replace("]","").replace("\"","\\\"") +","
                        else:
                        
                            sql_mid += x + "=\"" + str(jsonobj[x]).replace("\"","\\\"") +"\","
                            
                    else:
                    
                        if (x == "answers"):
                        
                            list_s = jsonobj[x]
                            
                        else:
                        
                            if (x in dic_c):
                        
                                # 防止重复添加字段
                                if (not dic_c[x] in sql_mid):
                                    sql_mid += dic_c[x] + "=\"" + str(jsonobj[x]).replace("\"","\\\"") + "\","
                    
                
            #print ("sql_mid == ",sql_mid) # 调试用
            #print (type(list_s),list_s) # 调试用
            #print (type(list_t),list_t) # 调试用

            if (list_t):
                
                k = 0
                for y in list_t:
                    
                    sql = sql_head + sql_mid
                    
                    for z in y:
                    
                        if (z == "is_selected"):
                            
                            if (y[z] == True):
                                #print (y[z],k) # 调试用
                                if (k <= len(list_s)-1):
                                    # print (k,"候选答案",list_s[k]) # 调试用
                                    sql += "answer_last=\"['" + str(list_s[k]).replace("\"","\\\"") + "']\","
                                    k += 1

                            
                        if z in dic_c:
                            # 防止重复添加字段
                            if (not dic_c[z] in sql):
                                sql += dic_c[z] + "=\"" + str(y[z]).replace("\"","\\\"") + "\","
                        else:
                            if z in list_c:
                                # 防止重复添加字段
                                if (not z in sql):
                                    sql += z + "=\"" + str(y[z]).replace("\"","\\\"") + "\","
                        #print (z) # 调试用
                        
                    sql = sql[:-1]

                    j += 1
                    print(j)
                    #print (sql) # 调试用
                    insert_if = False 
                    insert_if = rs_do_mysql.write_sql(sql)
                    if (insert_if is True):
                        i += 1
                    else:
                        # 写入错误日志
                        if (config.dic_config["log_if"] == "1"):
                            try:
                                with open("..\\data\\err\\log_json2mysql_err.txt", 'a+') as f:
                                    f.write(sql + '\n')
                            except:
                                pass
                                
            
        if (i > 0):
            result += "共执行" + str(j) + "次操作! 成功" + str(i) + "次！耗时" + str(time_cost(self.time_start))+ "秒！"
            
        rs_do_mysql.close_cur() #关闭数据游标
        rs_do_mysql.close() #关闭数据连接
        
        return result
        
#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():
    print("") # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()

#---------- 主过程<<结束>> -----------##