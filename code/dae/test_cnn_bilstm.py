#!/usr/bin/env python

# -*- coding: UTF-8 -*-  

'''

{

"版权":"LDAE工作室",

"author":{

"1":"zhui",
"2":"吉更",

}

"初创时间:"2017年3月",

}

'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import cgi # CGI模式 取得shell参数用

#-----系统外部需安装库模块引用-----

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
import inc_cnn_bilstm as cb # cnn_bilstm方法库引用
import diy.inc_nlp as inc_nlp # 自然语言处理模块
#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

def run_it(str_p=""):

    txt = ""
    result = []
    segment = inc_nlp.Segment() #分词类实例化
    numb_r = 999999
    # 循环输入
    i = 1
    while (i<=numb_r):
    
        key_p = input("请输入,exit退出 >>> ")
        
        if (key_p == "exit"):
            break
        
        if (key_p):
            result = int(cb.run_it(str_t=key_p,segment_p=segment))
        else:
            print ("输入不能为空")
            continue
            
        #print ("结果",result) # 调试用
        
        if (result):
            print ("识别结果代码：",result) #调试用
        else:
            print("处理失败>>>",key_p)
    i += 1
    
    return txt

#--------- 内部模块处理<<结束>> ---------#

if __name__ == '__main__':
    
    print (run_it())

    





