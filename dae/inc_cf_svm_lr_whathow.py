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

import time

#-----系统外部需安装库模块引用-----

import numpy as np
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from jieba import analyse

#-----DIY自定义库模块引用-----
import config #系统配置参数

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

def cut_word(sentence, tag = 'tfidf'):
    # 分词 -- 特定条件
    if tag == 'textrank':
        return ' '.join(analyse.textrank(sentence))
    else:
        return ' '.join(analyse.tfidf(sentence))


def cal_tf_idf(article, tag='tf'):
    # 计算 TF 或者 TF-IDF值
    vectorizer = CountVectorizer()
    if tag == 'tf':
    #获取TF矩阵（词频）
        tf_matrix = vectorizer.fit_transform(article).toarray()
        word = vectorizer.get_feature_names()
        tf_matrix = pd.DataFrame(tf_matrix,columns=word)
        return tf_matrix
    else:
        #获取TFIDF矩阵
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(article))
        word = vectorizer.get_feature_names()
        weight = tfidf.toarray()
        tfidf_matrix = pd.DataFrame(weight,columns=word)
        return tfidf_matrix

# 预测
def predict(sentence):

    # 预测模型
    lines = cut_word(sentence, tag = 'tfidf')
    #print (lines) # 调试用
    xx = cal_tf_idf([lines])
    high_words = pickle.load(open(config.dic_config["path_svm"] + 'high_words.pkl', 'rb+'))
    xx = pd.DataFrame(xx,columns=high_words).fillna(0)
    
    clf = 'LR'+'_1'
    model = pickle.load(open(config.dic_config["path_svm"] + '%s'%(clf), 'rb+'))
    pre = model.predict_proba(xx)
    
    return pre.argmax()

# 调用
def run_it(str_p=""):
    #str_p = '孕妇怀孕吃什么水果好？' # 调试用
    return predict(str_p)
    
#--------- 内部模块处理<<结束>> ---------#

if __name__ == '__main__':
    
    print ("")

    





