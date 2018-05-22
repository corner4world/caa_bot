#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

#-----系统自带必备模块引用-----

#-----系统外部需安装库模块引用-----

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
import inc_vec # 词向量处理

'''
{
"版权":"LDAE工作室",
"author":{
"1":"一世纪末",
"2":"吉更",
}
"初创时间:"2017年3月",
}
'''

def run_it():

    #w2v = inc_vec.W2v()
    path_model = "./data/w2v/w2v.model"
    result = []
    
    numb_r = 128
    # 循环输入
    i = 1
    while (i<=numb_r):
    
        key_p = input("请输入关键词,exit退出 >>> ")
        #print (inc_vec.run_it(str_t=key_p,path_model_p=path_model))
        result = inc_vec.run_it(str_t=key_p,path_model_p=path_model)
        
        if (result):
            print (result)
        else:
            print("未找到>>>",key_p)
    i += 1
    #path_model"./data/w2v/w2v.model"
    #model=gensim.models.Word2Vec.load(path_model)
    #print(model["癌症"])
    #print (model.most_similar("淋巴瘤"))

if __name__ == '__main__':
    run_it()
    