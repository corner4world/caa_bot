#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{

"版权":"LDAE工作室",

"author":{

"1":"zhui",
"2":"吉更",

}

"初创时间:"2017年3月",

}
"""
import pandas as pd
import numpy as np
import random
import codecs
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
import jieba
jieba.load_userdict(config.dic_config["path_dic"] + "user_dic_jieba.txt")  
import jieba.posseg #需要另外加载一个词性标注模块  
import cnn_bilstm_config as config_cb

import diy.inc_nlp as inc_nlp # 自然语言处理模块

# 词性标注处理
def str2pseg(str_t="",segment_p=""):
    
    txt_t = ""
    list_seg = []
    
    try:
        list_seg = segment_p.seg_pseg(txt_p=str_t)
    except:
        pass
        
    list_t = []
    
    for x in list_seg:
    
        try:
            list_t = eval(x)
        except:
            list_t = []
        if (list_t):
            txt_t += list_t[0] + "/" + list_t[1] + "|"
    txt_t = txt_t[0:-1]
    
    return txt_t
    
def read_lines(path):
    lines = []
    with codecs.open(path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.rstrip()
            if line:
                lines.append(line)
    return lines

def get_sentence(sentence_tag):
    words = []
    for item in sentence_tag.split('|'):
        try:
            index = item.rindex('/')
        except:
            print(1,item)
        try:
            words.append(item[:index])
        except:
            pass
    return ' '.join(words)


def extract_sentece():

    lines = read_lines(config_cb.TRAIN_PATH)
    lines += read_lines(config_cb.TEST_PATH)
    
    with codecs.open(config_cb.SENTENCE_PATH, 'w', encoding='utf-8') as file_w:
    
        for line in lines:
        
            try:
                index = line.index(',')
            except:
                print(line)
                
            word_tag = line[index+1:]
            file_w.write('%s\n' % get_sentence(word_tag))

train = pd.read_csv(config_cb.TRAIN_CSV_PATH,encoding = "utf8")#,index = False , encoding = "utf8")
test = pd.read_csv(config_cb.TEST_CSV_PATH, encoding = "utf8")

index = np.arange(0,train.shape[0])
random.shuffle(index)

segment = inc_nlp.Segment() # 分词对象实例化

train = train.loc[index]
train_data = train.data.tolist()
train_label = train.label.tolist()

f1 = codecs.open(config_cb.TRAIN_PATH,"w",encoding = "utf8")

str_t = ""
for s ,j in enumerate(train_label):
    str_t = str2pseg(str_t=train_data[s],segment_p=segment)
    if (str_t != ""):
        f1.write(str(j) + "," + str_t + "\n")

f1.close()

test_data = test.data.tolist()
test_label = test.label.tolist()

f2 = codecs.open(config_cb.TEST_PATH,"w",encoding = "utf8")

str_t = ""
for s ,j in enumerate(test_label):
    str_t = str2pseg(str_t=test_data[s],segment_p=segment)
    f2.write(str(j) + "," + str_t + "\n")

f2.close()

            

# 生成句向量语料
extract_sentece() 


# 词向量的嵌入处理

import re
all_data = train.data.tolist() + test.data.tolist()
char_sens = []
all_word = []
for line in all_data:
    word_tmp = []
    try:
        tmp_line = re.sub("\s+","", line.strip())
    except:
        temp_line = []
    for w in tmp_line:
        word_tmp.append(w.lower())
    all_word += word_tmp
    char_sens.append(word_tmp)

from gensim.models.word2vec import Word2Vec  
from gensim.models.word2vec import LineSentence
from time import time
t0 = time()
in_path = config_cb.SENTENCE_PATH
model  = Word2Vec(sentences=LineSentence(in_path), sg=1, size=config_cb.W2V_DIM,  window=3,  min_count=3,  negative=3, sample=0.001, hs=1, workers=4)
model.wv.save_word2vec_format(config_cb.EMBEDDING_ROOT + '/word_embedding.txt', binary=False)
model.wv.save_word2vec_format(config_cb.EMBEDDING_ROOT + '/word_embedding.bin', binary=True)

model  = Word2Vec(sentences=char_sens, sg=1, size=config_cb.C2V_DIM,  window=3,  min_count=3,  negative=3, sample=0.001, hs=1, workers=4)
model.wv.save_word2vec_format(config_cb.EMBEDDING_ROOT + '/char_embedding.txt', binary=False)
model.wv.save_word2vec_format(config_cb.EMBEDDING_ROOT + '/char_embedding.bin', binary=True)

print(time()-t0,"s , w2v done!")
