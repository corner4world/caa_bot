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

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----
from diy.inc_hash import hash_make #MD5函数

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区

# 对话基础引擎类
class Engine_base(object):

    def __init__(self,*args):
        pass
    
    # 用户ID检查
    def id_check(self):
        pass
    
# 对话主引擎类
class Engine_main(Engine_base):

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