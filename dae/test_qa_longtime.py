#!/usr/bin/env python

# -*- coding: UTF-8 -*-  

'''

{

"版权":"LDAE工作室",

"author":{

"1":"出门向右",
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
import inc_qa_longtime as ql # svm_lr方法库引用


#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

def run_it(str_p=""):

    txt = ""
    result = ""
    
    numb_r = 128
    # 循环输入
    i = 1
    while (i<=numb_r):
    
        key_p = input("请输入句子,exit退出 >>> ")
        if (key_p == "exit"):
            break
            
        result = ql.run_it(key_p)
        
        if (result):
            print (result) #调试用
        else:
            print("处理失败>>>",key_p)
    i += 1
    
    return txt

#--------- 内部模块处理<<结束>> ---------#

if __name__ == '__main__':
    
    print (run_it())

    





