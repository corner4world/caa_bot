#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"腾辉",
"2":"吉更"
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys
import os
import time # 时间模块

#-----特定功能模块引用区-----
import csv
import cgi # CGI模式 取得shell参数用

#-----系统外部需安装库模块引用-----
import redis
#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块 
from diy.inc_nlp import * #自定义自然语言处理功能模块 
rs_redis = redis.Redis(host=config.dic_config["redis_host"], password=config.dic_config["redis_pass"], port=config.dic_config["redis_port"], db=config.dic_config["redis_db"])

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区

def read_csv_data(csv_file):
    
    with open(csv_file, encoding='utf8') as workfile:
        csv_data=csv.reader(workfile)
        return [(r[0],int(r[1])) for r in csv_data]

# 建议词数据处理
def sug_do(csv_file = r'./data/test.csv'):

    txt = ""

    time_start = datetime.datetime.now()
    
    #获取原始数据集
    data=read_csv_data(csv_file)

    #i = 1
    #for x in data:
        #print (i,x)
        #i += 1
        
    app_t = ()
    str_t = ""
    #numb_all = 999999
    k = 1
    m = 0
    nlp = Nlp() # 自然语言处理实例化
    numb_all = len(data)
    
    for x in data:
        
        numb_t = x[1]
        str_t = x[0]
        str_t = str_t.strip()
        key_t = str_t
        arr_t = nlp.seg(txt_p=str_t) #分词处理
        
        # 构造推荐词索引
        if (arr_t):
            for y in arr_t:
                y = y.strip()
                if (y):
                    #rs_redis.r.sadd("set_name","aa")
                    rs_redis.zadd(y,key_t,numb_t)
                    try:
                        print (y,key_t,numb_t) #调试用
                    except:
                        pass
                    m += 1
                    
        print ("第 " + str(k) + " 次处理,完成度：" + str(round(k*100/numb_all,2)) + "%" )
        time.sleep(3)
        #e("64")
        k += 1
            
    time_last = str(time_cost(time_start))
    print ("共导入：" + str(k-1) + " 条原生关键词 生成模糊键：" + str(m) + " 条" )
    print ("耗时：",time_last," 秒")
    
    return txt


#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#
def main():

    print ("")  # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()
#---------- 主过程<<结束>> -----------#