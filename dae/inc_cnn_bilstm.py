#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import sys
from time import time
import random

#-----系统外部需安装库模块引用-----

import codecs
from collections import Counter
import numpy as np
import tensorflow as tf

#-----DIY自定义库模块引用-----
import cnn_bilstm_load_data
import cnn_bilstm_text_cnn
from diy.inc_sys import * #自定义系统级功能模块
import cnn_bilstm_config as config
import inc_seg # 分词模块

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# 主测试方法
def test_it():

    txt = ""
    t0 = time.time()
    word_weights, char_weights, tag_weights = cnn_bilstm_load_data.load_embedding()
    word_voc, char_voc, tag_voc, label_voc = cnn_bilstm_load_data.load_voc()

    # load data
    sentences_test, chars_test, tags_test, labels_test = cnn_bilstm_load_data.init_data( config.TEST_PATH , word_voc, char_voc, tag_voc, label_voc)
    # init model
    print("测试集长度: ",len(labels_test)) # 调试用

    model = cnn_bilstm_text_cnn.DCModel(
        config.MAX_LEN, 
        word_weights, 
        char_weights, 
        tag_weights, 
        model_path = config.DIR_MODEL,
        label_voc=label_voc
        )

    saver = tf.train.Saver()
    
    flag = 1 # 分支选择参数
    
    if (flag):
        saver.restore(model.sess, config.TRAIN_ALL_MODEL)
    else :
        saver.restore(model.sess, config.DIR_MODEL)
        
    #p_test, r_test, f_test = model.evaluate(sentences_test, chars_test ,tags_test, labels_test)
    #print('\tp_test=%f, r_test=%f, f_test=%f' % (p_test, r_test, f_test))
    
    pre_y,pre_proba = model.predict(sentences_test, chars_test ,tags_test)

    with codecs.open(config.path_main + 'result/predict.csv', 'w', encoding='utf-8') as file_w:
        file_w.write("max_label,label_0,label_1,label_2,label_3,lable_4,label_5,label_6\n")
        
        for num, scores in enumerate(pre_proba):
            file_w.write('%d,%f,%f,%f,%f,%f,%f,%f\n' % (int(model._label_voc_rev[pre_y[num]]), scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6]))

    print('Done in %ds!' % (time.time()-t0))
    
    return txt

# 主调用函数
def run_it(str_t="",action_p=""):
    
    words = [] # 分词结果集 
    #str_t = "非霍奇金淋巴瘤二期已化疗了五次还要化疗吗？" # 测试用
    txt_t = ""
    txt_t += "1," # 临时文本
    
    segment = inc_seg.Segment() # 分词模块实例化
    words = segment.seg_jieba(txt_p=str_t,way_p="pseg")# 获得分词结果
    for w in words:  
        #print (w.word, w.flag) # 调试用
        txt_t += w.word + "/" + w.flag + "|"
    txt_t = txt_t[0:-1]
    
    # 写入待处理文本
    with codecs.open(config.path_main + 'corpus/testing.seg.csv', 'w', encoding='utf-8') as file_w:
        file_w.write(txt_t)

    txt = ""
    
    t0 = time.time()
    
    word_weights, char_weights, tag_weights = cnn_bilstm_load_data.load_embedding()
    word_voc, char_voc, tag_voc, label_voc = cnn_bilstm_load_data.load_voc()

    # load data
    sentences_test, chars_test, tags_test, labels_test = cnn_bilstm_load_data.init_data( config.TEST_PATH , word_voc, char_voc, tag_voc, label_voc)
    # init model
    print("测试集长度: ",len(labels_test)) # 调试用

    model = cnn_bilstm_text_cnn.DCModel(
        config.MAX_LEN, 
        word_weights, 
        char_weights, 
        tag_weights, 
        model_path = config.DIR_MODEL,
        label_voc=label_voc
        )

    saver = tf.train.Saver()
    
    flag = 1 # 分支选择参数
    
    if (flag):
        saver.restore(model.sess, config.TRAIN_ALL_MODEL)
    else:
        saver.restore(model.sess, config.DIR_MODEL)
        
        
    #p_test, r_test, f_test = model.evaluate(sentences_test, chars_test ,tags_test, labels_test)
    #print('\tp_test=%f, r_test=%f, f_test=%f' % (p_test, r_test, f_test))
    
    pre_y,pre_proba = model.predict(sentences_test, chars_test ,tags_test)

    with codecs.open(config.path_main + 'result/predict.csv', 'w', encoding='utf-8') as file_w:
        file_w.write("max_label,label_0,label_1,label_2,label_3,lable_4,label_5,label_6\n")
        
        for num, scores in enumerate(pre_proba):
            file_w.write('%d,%f,%f,%f,%f,%f,%f,%f\n' % (int(model._label_voc_rev[pre_y[num]]), scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6]))
            txt = model._label_voc_rev[pre_y[num]]
    
    print('Done in %ds!' % (time.time()-t0))
    
    return txt
    
if __name__ == '__main__':
    
    print ("")