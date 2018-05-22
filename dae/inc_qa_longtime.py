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

from tqdm import tqdm
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from jieba import analyse

#-----DIY自定义库模块引用-----
import config #系统配置参数

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# ---全局变量处理
tag = 'tfidf'

# ---基本方法函数

def cut_word(sentence):
    # 分词 -- 特定条件
    if tag == 'textrank':
        return ' '.join(analyse.textrank(sentence))
    else:
        return ' '.join(analyse.tfidf(sentence))


def cal_tf_idf(data_list, tag):
    # 计算 TF 或者 TF-IDF值
    vectorizer = CountVectorizer()
    if tag == 'tf':
        #获取TF矩阵（词频）
        tf_matrix = vectorizer.fit_transform(data_list).toarray()
        word = vectorizer.get_feature_names()
        tf_matrix = pd.DataFrame(tf_matrix,columns=word)
    else:
        #获取TFIDF矩阵
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(data_list))
        word = vectorizer.get_feature_names()
        weight = tfidf.toarray()
        tf_matrix = pd.DataFrame(weight,columns=word)
    idx_set = set(tf_matrix.columns)
    tf_matrix = tf_matrix[list(idx_set)]
    return tf_matrix


def cal_cosVector(x,y):
    # 计算两个向量的余弦
    if len(x)!=len(y):
        return 0.2
    result1=0.0
    result2=0.0
    result3=0.0
    for i in range(len(x)):
        result1+=x[i]*y[i]   #sum(X*Y)
        result2+=x[i]**2     #sum(X*X)
        result3+=y[i]**2     #sum(Y*Y)
    return result1/((result2*result3)**0.5)

def cal_Euclidean(p, q):
    #计算欧几里德距离,并将其标准化
    same = 0
    for i in p:
        if i in q:
            same +=1
    e = sum([(p[i] - q[i])**2 for i in range(same)])
    return 1/(1+e**.5)


def cal_way1(input_sen, df):
    # 集合法
    input_sen = cut_word(input_sen)
    a1 = input_sen.split(' ')
    
    result = {}
    for j in tqdm(df.index):
        try:
            a2 = df['cut_question'][j].split(' ')
        except:
            a2 = ['']
        cv = len(set(a1) & set(a2))/(len(a1)+len(a2))*2
        result[df['ID00'][j]] = cv
    result = sorted(result.items(), key=lambda f:f[1], reverse=True)[:5]
    return result

def cal_way2(input_sen, df, tag1, tag2):
    # 距离法
    input_sen = cut_word(input_sen)
    a1 = input_sen.split(' ')
    
    result = {}
    for j in tqdm(df.index):
        try:
            a2 = df['cut_question'][j].split(' ')
        except:
            a2 = ['']
        if len(set(a1) & set(a2)) == 0:
            cv = -1
        else:
            try:
                dta_list = [input_sen, df['cut_question'][j]]
                x = cal_tf_idf(dta_list, tag1)
            except:
                dta_list = [input_sen, '']
                x = cal_tf_idf(dta_list, tag1)
            if tag2 == 'Euclidean':
                try:
                    cv = float(cal_Euclidean(x.iloc[0].values, x.iloc[1].values))
                except:
                    cv = -1
            else:
                try:
                    cv = float(cal_cosVector(x.iloc[0].values, x.iloc[1].values))
                except:
                    cv = -1
        result[df['ID00'][j]] = cv
    result = sorted(result.items(), key=lambda f:f[1], reverse=True)[:3]
    return result


def recommend_question(input_sen, df_department, way):
    if way=='way1':
        rs = cal_way1(input_sen, df_department)
    elif way=='way2':
        rs = cal_way2(input_sen, df_department, 'tf', 'cosVector')
    return rs

# 主执行过程
def run_it(input_sen=""):

    dic_t = {} # 临时倒排字典
    db_department = pd.read_csv(config.dic_config["path_bi"] + 'cache/train_cutword.csv',encoding='utf8') # 加载到内存
    
    t0 = time.time() # 初始时刻
    
    # 提取匹配的问题
    #input_sen = '卵巢交界性粘液性囊腺瘤（肠型），伴上皮内' # 调试用
    rs = recommend_question(input_sen, db_department, 'way1')
    
    # 提取推荐结果
    result = {}
    for offset,i in enumerate(rs):
        iid = i[0]
        try:
            recom = db_department[db_department['ID00']==iid]
            question, answer = recom['question'].values[0], recom['answer'].values[0]
            if str(question)!='nan':
                result[offset] = [i[1], question, answer]
        except:
            pass
    i = 0
    for x in result:
        dic_t["[\"" + result[x][1] + "\",\"" + result[x][2] + "\"]"] = round(result[x][0],8)
        i += 1
        
    #print (dic_t) # 调试用
    #print (result)# 调试用
    
    print('Done in %.1fs!' % (time.time()-t0))
    
    return str(dic_t)
        
#--------- 内部模块处理<<结束>> ---------#

if __name__=='__main__':
    
    #print (run_it()) # 调试用
    print ("")








