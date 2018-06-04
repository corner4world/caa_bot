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
from __future__ import print_function

#-----系统自带必备模块引用-----

import time

#-----系统外部需安装库模块引用-----

import time

import numpy as np
import pandas as pd

import pickle
import re
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from jieba import analyse
from sklearn.svm import SVC
from sklearn.cross_validation import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier

'''
import sys
reload(sys)
sys.setdefaultencoding("utf8")
'''

#-----DIY自定义库模块引用-----
import config #系统配置参数

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

def read_lines(path):

    all_lines = {}
    with open(path, 'r', encoding='utf-8') as file:
        temp_lines = file.readlines()
        for line in temp_lines:
            line = line.strip()
           #line = re.sub('\ufeff','',line)
            if line:
                all_lines[line] = 1
    return all_lines
    
#def write_lines(path, lines):
#    with open(path, 'a+', encoding='utf-8') as file:
#        for line in lines:
#            file.write(line+'\n')
#    file.close()

def cut_word(sentence, tag = 'tfidf'):
    # 分词 -- 特定条件
    if tag == 'textrank':
        return ' '.join([i for i in analyse.textrank(sentence) if i not in stopwords])
    else:
        return ' '.join([i for i in analyse.tfidf(sentence) if i not in stopwords])


def cal_tf_idf(article, tag):
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

def stat_word_freq(dta, num=2):
    # 分词词频统计
    all_words_dict = {}
    for i in dta.index:
        raw = [i for i in dta['cut_question'][i].split(' ') if i!='']
        for word in raw:
            if word in all_words_dict.keys():
                all_words_dict[word] += 1
            else:
                all_words_dict[word] = 1
    all_words_tuple_list = sorted(all_words_dict.items(), key=lambda f:f[1], reverse=True)
    # 内建函数sorted参数需为list
    high_word = []
    for words in all_words_tuple_list:
        if words[1] >= num:
            high_word.append(words[0])
    return high_word

if __name__ == '__main__':
    
    t0 = time.time()
    
    # train deal
    stopwords = read_lines(config.dic_config["path_svm"] + 'stopwords.txt')
    train = pd.read_csv(config.dic_config["path_svm"] + '0_训练集.csv',encoding='utf8')
    train['cut_question'] = train['question'].apply(lambda x:cut_word(x))
    
    dftr_list = list(train['cut_question'].values)
    high_word = stat_word_freq(train, num=2)
    pickle.dump(high_word, open(config.dic_config["path_svm"] + 'high_words.pkl', 'wb+'))
    
    df_matrix_train = cal_tf_idf(dftr_list, tag='tf') #选择TF特征
    df_matrix_train['label'] = train['what']
    df_matrix_train['hash'] = train['hash']
    df_matrix_train = pd.DataFrame(df_matrix_train,columns=['hash','label']+high_word).fillna(0)
    df_matrix_train = df_matrix_train[df_matrix_train['label']<7]
    # test deal
    test = pd.read_csv(config.dic_config["path_svm"] + '1_测试集.csv',encoding='utf8')
    test['cut_question'] = test['question'].apply(lambda x:cut_word(x))
    dfte_list = list(test['cut_question'].values)
    df_matrix_test = cal_tf_idf(dfte_list, tag='tf') #选择TF特征
    df_matrix_test['label'] = test['what']
    df_matrix_test['question'] = test['question']
    df_matrix_test['hash'] = test['HASH']
    df_matrix_test = pd.DataFrame(df_matrix_test,columns=['hash','question','label']+high_word).fillna(0)
    
    train_X = df_matrix_train.drop(['hash', 'label'], axis = 1)
    train_Y = df_matrix_train['label']
    test_X = df_matrix_test[train_X.columns]
    
    print (df_matrix_train['label'].value_counts())
    print ("The load data over!\n")
    
    clfs = {
#       "AdaBoost" : AdaBoostClassifier(n_estimators=800, learning_rate=0.05),
       "LR" : LogisticRegression(penalty='l2', max_iter = 600, n_jobs=-1),
       "SVM" : SVC(C=30, max_iter=600, probability=True, decision_function_shape='ovo')
        }
    kf = KFold(len(train_Y), n_folds = 5, shuffle=True, random_state=201705)
    j = 0
    for idd in clfs:
        print (u"开始训练模型>>> %s"%(idd))
        clf = clfs[idd]
        
        pre_test = []
        for i, (train_index, test_index) in enumerate(kf):
            x_train = train_X.iloc[train_index]
            x_test = train_X.iloc[test_index]
            y_train = train_Y.iloc[train_index]
            y_test = train_Y.iloc[test_index]
            
            clf.fit(x_train, y_train)
            pickle.dump(clf, open(config.dic_config["path_svm"] + '%s_%s'%(idd,i+1), 'wb+'))
            pre = clf.predict_proba(test_X)
            pre_labels = []
            for p in pre:
                pre_labels.append(p.argmax())
            pre_test.append(pre_labels)
        pre_test = pd.DataFrame(pre_test).T
        pre_test['sen_prob'] = pre_test.mode(axis=1)[0]
        df_submit = pd.DataFrame(data = {'hash': df_matrix_test['hash'],
                                         'label': df_matrix_test['label'],
                                         'question':df_matrix_test['question'],
                                         'probability':pre_test['sen_prob']
                                        })
        df_submit.to_excel(config.dic_config["path_svm"] + 'test-forecast/test_predict_result_%s.xlsx'%(idd), index=False, encoding='GBK')
        print ('Done in %.1fs!\n' % (time.time()-t0))
        
    
















