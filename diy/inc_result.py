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

#-----系统外部需安装库模块引用-----

#-----DIY自定义库模块引用-----

sys.path.append("..")
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_hash import hash_make # 基本自定义hash模块
import config # 系统自定义文件

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

# 数据处理基础类
class Result_base(object):
    
    def __init__(self):
        pass
        
    # 自定义查词
    def word_in_dic(self,str_p="",dic_p={},to_do_p="max"):
        
        txt = ""
        if (to_do_p == "max"):
            for x in dic_p:
                if x in str_p:
                    if (len(x) > len(txt)): 
                        txt = x
                        
        if (to_do_p == "all"):
            txt = "-"
            for x in dic_p:
                if x in str_p:
                    txt += x + "-"
        return txt
        
    # 自定义字典切词分词
    def segment_dic_cut(self,txt_p="",dic_p={},action_p="left",step_p=6,end_p=1):
        txt = txt_p
        list_p = []
        
        if (len(txt) <= step_p):
            list_p.append(txt)
            return list_p #小于切词步阈长度直接返回
        
        # 由左到右正向分词
        if (action_p == "left"):
            s=0
            e=step_p
            while (s < len(txt_p)-1-end_p):
                str_t = txt[s:e]
                for i in range(step_p-1):
                    if str_t in dic_p:
                        list_p.append(str_t)
                        s += i + 1
                        break
                    else:
                        str_t = str_t[s:e-i]
                        if (e-i == end_p):
                            list_p.append(str_t)
                            s += end_p
                            break
        
        # 由右到左逆向分词
        if (action_p == "right"):
            s=0
            e=step_p
            while (s > -1*(len(txt_p)-1-end_p)):
                str_t = txt[-1*e:-1*s]
                for i in range(step_p-1):
                    if str_t in dic_p:
                        list_p.append(str_t)
                        s += -1*(i + 1)
                        break
                    else:
                        str_t = str_t[-1*(e-i):s]
                        if (-1*(e-i) == end_p):
                            list_p.append(str_t)
                            s += -1*end_p
                            break
        
        return list_p
        
    # 自然分段
    def np_all(self,txt_p="",ignore_list=[]):
        
        txt_p = txt_p.replace("'","\n")
        txt_p = txt_p.replace("\n","\n")
        txt_p = txt_p.replace("\"","\n")
        txt_p = txt_p.replace(",","\n")
        txt_p = txt_p.replace("（","\n")
        txt_p = txt_p.replace("）","\n")
        txt_p = txt_p.replace("(","\n")
        txt_p = txt_p.replace(")","\n")
        txt_p = txt_p.replace("，","\n")
        txt_p = txt_p.replace("。","\n")
        txt_p = txt_p.replace("；","\n")
        txt_p = txt_p.replace("“","\n")
        txt_p = txt_p.replace("”","\n")
        txt_p = txt_p.replace("（","\n")
        txt_p = txt_p.replace("）","\n")
        txt_p = txt_p.replace("？","\n")
        txt_p = txt_p.replace("：","\n")
        txt_p = txt_p.replace("《","\n")
        txt_p = txt_p.replace("》","\n")
        txt_p = txt_p.replace("『","\n")
        txt_p = txt_p.replace("』","\n")
        txt_p = txt_p.replace("[","\n")
        txt_p = txt_p.replace("]","\n")
        txt_p = txt_p.replace("！","\n")
        txt_p = txt_p.replace("、","\n")
        #txt_p = txt_p.replace(" ","\n")
        txt_p = txt_p.replace("\\","\n")
        txt_p = txt_p.replace("=","\n")
        txt_p = txt_p.replace("×","\n")
        txt_p = txt_p.replace("÷","\n")
        txt_p = txt_p.replace("+","\n")
        txt_p = txt_p.replace("-","\n")
        txt_p = txt_p.replace("≈","\n")
        txt_p = txt_p.replace("【","\n")
        txt_p = txt_p.replace("】","\n")
        txt_p = txt_p.replace("〖","\n")
        txt_p = txt_p.replace("〗","\n")
        txt_p = txt_p.replace("[","\n")
        txt_p = txt_p.replace("]","\n")
        txt_p = txt_p.replace("｛","\n")
        txt_p = txt_p.replace("｝","\n")
        txt_p = txt_p.replace("?","\n")
        txt_p = txt_p.replace("±","\n")
        txt_p = txt_p.replace("/","\n")
        txt_p = txt_p.replace("≌","\n")
        txt_p = txt_p.replace("∽","\n")
        txt_p = txt_p.replace("∪","\n")
        txt_p = txt_p.replace("∩","\n")
        txt_p = txt_p.replace("∈","\n")
        txt_p = txt_p.replace("\r\n", "\n")
        txt_p = txt_p.replace("\n","\n")
        txt_p = txt_p.replace("\r","\n")
        txt_p = txt_p.replace("  ","\n")
        #txt_p = txt_p.replace(".","\n")
        txt_p = txt_p.replace("|","\n")
        txt_p = txt_p.replace("_","\n")
        
        #停用词初滤
        for x in ignore_list:
            txt_p = txt_p.replace(x,"")
        
        return txt_p

    # 简化的自然分句
    def np_some(self,str_p=""):
        str_p = str_p.replace(",","@x@")
        str_p = str_p.replace("，","@x@")
        str_p = str_p.replace(";","@x@")
        str_p = str_p.replace("；","@x@")
        str_p = str_p.replace(":","@x@")
        str_p = str_p.replace("：","@x@")
        str_p = str_p.replace("'","@x@")
        str_p = str_p.replace("\"","@x@")
        str_p = str_p.replace("\\","@x@")
        str_p = str_p.replace("、","@x@")
        str_p = str_p.replace("“","@x@")
        str_p = str_p.replace("”","@x@")
        str_p = str_p.replace("!","@x@")
        str_p = str_p.replace("！","@x@")
        str_p = str_p.replace("?","@x@")
        str_p = str_p.replace("？","@x@")
        str_p = str_p.replace("。","@x@")
        str_p = str_p.replace(" ","@x@")
        return str_p
        
# ---- 模块预留综合处理函数 -----
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